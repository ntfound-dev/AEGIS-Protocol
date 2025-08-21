# File: services/backend-ai-agents/agents/oracle_agent.py

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import requests # Library untuk membuat permintaan HTTP ke API eksternal
import os

# Model ini HARUS SAMA PERSIS dengan yang ada di validator_agent.py
class RawEarthquakeData(Model):
    source: str
    magnitude: float
    location: str
    lat: float
    lon: float
    timestamp: int

# Alamat agent validator yang akan menerima data dari oracle ini
# Pastikan alamat ini sesuai dengan log dari validator_agent Anda
VALIDATOR_AGENT_ADDRESS = "agent1q22w4s4tc2hdt8tzn0skpv2cffmue5j85ktt3m4q06f723say726vzp0d4n"

# API_KEY = os.getenv("EARTHQUAKE_API_KEY") # Contoh jika butuh API Key
API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"

oracle_agent = Agent(
    name="oracle_agent_usgs",
    port=8001, # Port ini hanya untuk internal, tidak perlu di-ekspos kecuali ada alasan khusus
    seed="oracle_agent_usgs_secret_seed_phrase_12345",
    endpoint=["http://oracle-agent:8001/submit"],
)

fund_agent_if_low(str(oracle_agent.wallet.address()))

# Fungsi ini akan berjalan secara otomatis setiap 5 menit (300 detik)
@oracle_agent.on_interval(period=300.0)
async def fetch_earthquake_data(ctx: Context):
    ctx.logger.info("Oracle is fetching new data from USGS API...")
    try:
        # 1. Mengambil data dari API eksternal
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status() # Akan error jika status code bukan 2xx
        
        data = response.json()
        latest_earthquake = data['features'][0] # Ambil gempa terbaru

        props = latest_earthquake['properties']
        coords = latest_earthquake['geometry']['coordinates']

        # 2. Memformat data ke dalam Model yang disepakati
        earthquake_model = RawEarthquakeData(
            source="USGS_API_Oracle",
            magnitude=props.get('mag', 0),
            location=props.get('place', 'Unknown'),
            lat=coords[1],
            lon=coords[0],
            timestamp=props.get('time', 0) // 1000 # Konversi dari milidetik ke detik
        )

        ctx.logger.info(f"Found new event: {earthquake_model.magnitude} magnitude earthquake at {earthquake_model.location}")

        # 3. Mengirim data ke validator_agent
        await ctx.send(VALIDATOR_AGENT_ADDRESS, earthquake_model)
        ctx.logger.info("Data successfully sent to validator agent.")

    except requests.RequestException as e:
        ctx.logger.error(f"Error fetching data from API: {e}")
    except Exception as e:
        ctx.logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    oracle_agent.run()