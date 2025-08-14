# File: services/3-backend-ai-agents/agents/oracle_agent.py
import requests
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

class RawEarthquakeData(Model):
    source: str
    magnitude: float
    location: str
    lat: float
    lon: float
    timestamp: int

VALIDATOR_NETWORK_ADDRESS = "agent1q2gwxq52k8wecuvj3sksv9sszefaqpmq42u0mf6z0q5z4e0a9z0wz9z0q"

oracle_agent = Agent(
    name="oracle_agent_usgs",
    port=8001,
    seed="oracle_agent_usgs_secret_seed_phrase_12345"
)

fund_agent_if_low(str(oracle_agent.wallet.address()))

def fetch_latest_earthquake():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['features']:
            latest_quake = data['features'][0]
            properties = latest_quake['properties']
            
            if properties['mag'] >= 6.0:
                return RawEarthquakeData(
                    source="USGS",
                    magnitude=properties['mag'],
                    location=properties['place'],
                    lat=latest_quake['geometry']['coordinates'][1],
                    lon=latest_quake['geometry']['coordinates'][0],
                    timestamp=int(properties['time'] / 1000)
                )
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    return None

@oracle_agent.on_interval(period=60.0)
async def monitor_usgs(ctx: Context):
    ctx.logger.info("Checking for significant earthquakes...")
    quake_data = fetch_latest_earthquake()
    
    if quake_data:
        ctx.logger.info(f"!!! SIGNIFICANT EVENT DETECTED: {quake_data.magnitude} mag at {quake_data.location} !!!")
        await ctx.send(VALIDATOR_NETWORK_ADDRESS, quake_data)

if __name__ == "__main__":
    oracle_agent.run()