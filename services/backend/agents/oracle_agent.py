import os
import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import httpx

from uagents import Agent, Context, Model # type: ignore
from uagents.setup import fund_agent_if_low # type: ignore

# --- KONFIGURASI ---
ORACLE_SEED = os.getenv("ORACLE_AGENT_SEED", "oracle_agent_secret_seed_phrase_placeholder")
VALIDATOR_AGENT_ADDRESS = os.getenv("VALIDATOR_AGENT_ADDRESS")
USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
BMKG_API_URL = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
FETCH_INTERVAL_SECONDS = float(os.getenv("FETCH_INTERVAL_SECONDS", 300.0))

# --- MODEL DATA ---
class RawEarthquakeData(Model):
    source: str
    magnitude: float
    location: str
    lat: float
    lon: float
    timestamp: int

# --- INISIALISASI AGENT ---
oracle_agent = Agent(
    name="oracle_agent_multi_source",
    port=8001,
    seed=ORACLE_SEED,
    endpoint=["http://oracle-agent:8001/submit"],
)
fund_agent_if_low(str(oracle_agent.wallet.address()))
# REVISI: Mengembalikan ke ._logger untuk memperbaiki AttributeError
oracle_agent._logger.info(f"Oracle Agent berjalan dengan alamat: {oracle_agent.address}")

# --- FUNGSI PARSING DATA ---
def _parse_usgs_data(feature: Dict[str, Any]) -> Optional[RawEarthquakeData]:
    """Mem-parsing satu data gempa dari format USGS."""
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
        oracle_agent._logger.warning(f"Gagal mem-parsing item data USGS: {e}")
        return None

def _parse_bmkg_data(gempa: Dict[str, Any]) -> Optional[RawEarthquakeData]:
    """Mem-parsing data gempa dari format BMKG."""
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
        oracle_agent._logger.warning(f"Gagal mem-parsing item data BMKG: {e}")
        return None

# --- FUNGSI PENGAMBILAN DATA ---
ParserFunc = Callable[[Dict[str, Any]], Optional[RawEarthquakeData]]

async def _fetch_from_source(ctx: Context, client: httpx.AsyncClient, url: str, parser: ParserFunc, source_name: str) -> List[RawEarthquakeData]:
    """Mengambil dan mem-parsing data dari satu sumber API."""
    ctx.logger.info(f"Mengambil data dari API {source_name}...")
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
        ctx.logger.error(f"Error saat memproses data dari {source_name}: {e}")
        return []

@oracle_agent.on_interval(period=FETCH_INTERVAL_SECONDS) # type: ignore
async def fetch_and_send_data(ctx: Context):
    """Fungsi periodik untuk mengambil data dari semua sumber dan mengirimkannya."""
    if not VALIDATOR_AGENT_ADDRESS:
        ctx.logger.warning("Alamat Validator Agent belum diatur. Melewatkan pengambilan data.")
        return

    ctx.logger.info("Interval Oracle terpicu. Mengambil data dari semua sumber...")
    async with httpx.AsyncClient() as client:
        tasks = [
            _fetch_from_source(ctx, client, USGS_API_URL, _parse_usgs_data, "USGS"),
            _fetch_from_source(ctx, client, BMKG_API_URL, _parse_bmkg_data, "BMKG")
        ]
        results: List[List[RawEarthquakeData]] = await asyncio.gather(*tasks)

    all_earthquakes: List[RawEarthquakeData] = [item for sublist in results for item in sublist]

    if not all_earthquakes:
        ctx.logger.info("Tidak ada data gempa baru yang valid ditemukan.")
        return

    ctx.logger.info(f"Menemukan {len(all_earthquakes)} event baru. Mengirim ke validator...")
    for eq_data in all_earthquakes:
        try:
            await ctx.send(VALIDATOR_AGENT_ADDRESS, eq_data)
            ctx.logger.info(f"Data dari {eq_data.source} untuk '{eq_data.location}' berhasil dikirim.")
        except Exception as e:
            ctx.logger.error(f"Gagal mengirim data ke validator: {e}")

if __name__ == "__main__":
    oracle_agent.run()
