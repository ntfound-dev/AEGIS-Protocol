import os
import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
import httpx

from uagents import Agent, Context, Model # type: ignore
from uagents.setup import fund_agent_if_low # type: ignore

# --- CONFIGURATION ---
ORACLE_SEED = os.getenv("ORACLE_AGENT_SEED", "oracle_agent_secret_seed_phrase_placeholder")
VALIDATOR_AGENT_ADDRESS = os.getenv("VALIDATOR_AGENT_ADDRESS")
USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
BMKG_API_URL = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
FETCH_INTERVAL_SECONDS = float(os.getenv("FETCH_INTERVAL_SECONDS", 300.0))

# --- DATA MODEL ---
class RawEarthquakeData(Model):
    source: str
    magnitude: float
    location: str
    lat: float
    lon: float
    timestamp: int

# --- AGENT INITIALIZATION ---
oracle_agent = Agent(
    name="oracle_agent_multi_source",
    port=8001,
    seed=ORACLE_SEED,
    endpoint=["http://oracle-agent-1:8001/submit"],
)
fund_agent_if_low(str(oracle_agent.wallet.address()))
oracle_agent._logger.info(f"Oracle Agent running with address: {oracle_agent.address}")

# PERBAIKAN: Menambahkan set untuk melacak event yang sudah pernah dikirim
SEEN_EVENT_IDS: Set[str] = set()

# --- DATA PARSING FUNCTIONS ---
def _parse_usgs_data(feature: Dict[str, Any]) -> Optional[RawEarthquakeData]:
    try:
        props: Dict[str, Any] = feature['properties']
        coords: List[float] = feature['geometry']['coordinates']
        if props.get('mag') is None or props.get('time') is None:
            return None
        return RawEarthquakeData(
            source="USGS_API_Oracle",
            magnitude=float(props['mag']),
            location=str(props.get('place', 'Unknown Location')),
            lat=float(coords[1]),
            lon=float(coords[0]),
            timestamp=int(props['time'] // 1000)
        )
    except (KeyError, TypeError, IndexError) as e:
        oracle_agent._logger.warning(f"Failed to parse USGS data item: {e}")
        return None

def _parse_bmkg_data(gempa: Dict[str, Any]) -> Optional[RawEarthquakeData]:
    try:
        coords_str: str = gempa.get('Coordinates', '0,0')
        lat_str, lon_str = coords_str.split(',')
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        
        dt_text: Optional[str] = gempa.get('DateTime')
        if not dt_text:
            return None
        dt_object = datetime.fromisoformat(dt_text.replace('Z', '+00:00'))

        return RawEarthquakeData(
            source="BMKG_API_Oracle",
            magnitude=float(gempa.get('Magnitude', 0)),
            location=str(gempa.get('Wilayah', 'Unknown Location')),
            lat=lat,
            lon=lon,
            timestamp=int(dt_object.timestamp())
        )
    except Exception as e:
        oracle_agent._logger.warning(f"Failed to parse BMKG data item: {e}")
        return None

# --- DATA FETCHING FUNCTIONS ---
ParserFunc = Callable[[Dict[str, Any]], Optional[RawEarthquakeData]]

async def _fetch_from_source(ctx: Context, client: httpx.AsyncClient, url: str, parser: ParserFunc, source_name: str) -> List[RawEarthquakeData]:
    ctx.logger.info(f"Fetching data from {source_name} API...")
    try:
        response = await client.get(url, timeout=20.0)
        response.raise_for_status()
        json_data = response.json()

        all_parsed_data: List[RawEarthquakeData] = []
        if source_name == "USGS":
            features: List[Dict[str, Any]] = json_data.get('features', [])
            for feature in features:
                parsed = parser(feature)
                if parsed:
                    all_parsed_data.append(parsed)
        elif source_name == "BMKG":
            gempa_info: Optional[Dict[str, Any]] = json_data.get('Infogempa', {}).get('gempa')
            if gempa_info:
                parsed = parser(gempa_info)
                if parsed:
                    all_parsed_data.append(parsed)
        
        return all_parsed_data
    except Exception as e:
        ctx.logger.error(f"Error while processing data from {source_name}: {e}")
        return []

@oracle_agent.on_interval(period=FETCH_INTERVAL_SECONDS) # type: ignore
async def fetch_and_send_data(ctx: Context):
    """Periodic function to fetch data from all sources and send them."""
    if not VALIDATOR_AGENT_ADDRESS:
        ctx.logger.warning("Validator Agent address not set. Skipping data fetch.")
        return

    ctx.logger.info("Oracle interval triggered. Fetching data from all sources...")
    async with httpx.AsyncClient() as client:
        tasks = [
            _fetch_from_source(ctx, client, USGS_API_URL, _parse_usgs_data, "USGS"),
            _fetch_from_source(ctx, client, BMKG_API_URL, _parse_bmkg_data, "BMKG")
        ]
        results: List[List[RawEarthquakeData]] = await asyncio.gather(*tasks)

    all_earthquakes: List[RawEarthquakeData] = [item for sublist in results for item in sublist]

    if not all_earthquakes:
        ctx.logger.info("No new valid earthquake data found.")
        return

    new_earthquakes_to_send = []
    for eq_data in all_earthquakes:
        # Membuat ID unik untuk setiap event gempa
        event_id = f"{eq_data.source}-{eq_data.timestamp}-{eq_data.magnitude:.2f}"
        if event_id not in SEEN_EVENT_IDS:
            new_earthquakes_to_send.append(eq_data)
            SEEN_EVENT_IDS.add(event_id)

    if not new_earthquakes_to_send:
        ctx.logger.info("Data found, but all events have been sent previously.")
        return
        
    ctx.logger.info(f"Found {len(new_earthquakes_to_send)} new unique events. Sending to validator...")
    for eq_data in new_earthquakes_to_send:
        try:
            await ctx.send(VALIDATOR_AGENT_ADDRESS, eq_data)
            ctx.logger.info(f"Data from {eq_data.source} for '{eq_data.location}' successfully sent.")
        except Exception as e:
            ctx.logger.error(f"Failed to send data to validator: {e}")

if __name__ == "__main__":
    oracle_agent.run()