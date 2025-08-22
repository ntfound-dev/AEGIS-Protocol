from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import requests

class RawEarthquakeData(Model):
    source: str; magnitude: float; location: str; lat: float; lon: float; timestamp: int

VALIDATOR_AGENT_ADDRESS = "agent1q22w4s4tc2hdt8tzn0skpv2cffmue5j85ktt3m4q06f723say726vzp0d4n"
API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"

oracle_agent = Agent(
    name="oracle_agent_usgs", port=8001, seed="oracle_agent_usgs_secret_seed_phrase_12345",
    endpoint=["http://localhost:8001/submit"],
)
fund_agent_if_low(str(oracle_agent.wallet.address()))

@oracle_agent.on_interval(period=300.0)
async def fetch_earthquake_data(ctx: Context):
    ctx.logger.info("Oracle is fetching new data from USGS API...")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        latest_earthquake = response.json()['features'][0]
        props = latest_earthquake['properties']
        coords = latest_earthquake['geometry']['coordinates']
        earthquake_model = RawEarthquakeData(
            source="USGS_API_Oracle", magnitude=props.get('mag', 0), location=props.get('place', 'Unknown'),
            lat=coords[1], lon=coords[0], timestamp=props.get('time', 0) // 1000
        )
        ctx.logger.info(f"Found new event: {earthquake_model.magnitude} mag at {earthquake_model.location}")
        await ctx.send(VALIDATOR_AGENT_ADDRESS, earthquake_model)
        ctx.logger.info("Data successfully sent to validator agent.")
    except Exception as e:
        ctx.logger.error(f"Error fetching or sending data: {e}")

if __name__ == "__main__":
    oracle_agent.run()