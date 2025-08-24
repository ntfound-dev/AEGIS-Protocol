# functions.py
from uagents import Model
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import math

class EarthquakeRequest(Model):
    location: str
    radius_km: Optional[int] = 200
    days: Optional[int] = 7

class EarthquakeResponse(Model):
    earthquakes: str

# helper: haversine distance (km)
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def parse_iso_time(s: str):
    # try several ISO formats
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    # fallback: attempt epoch millis
    try:
        return datetime.utcfromtimestamp(int(s) / 1000.0)
    except Exception:
        return None

def query_usgs(lat: float, lon: float, radius_km: int, days: int, limit: int = 50) -> List[Dict[str, Any]]:
    endtime = datetime.utcnow()
    starttime = endtime - timedelta(days=max(1, int(days)))
    usgs_params = {
        "format": "geojson",
        "starttime": starttime.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": endtime.strftime("%Y-%m-%dT%H:%M:%S"),
        "latitude": lat,
        "longitude": lon,
        "maxradiuskm": radius_km,
        "orderby": "time",
        "limit": limit,
    }
    r = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query", params=usgs_params, timeout=30)
    r.raise_for_status()
    data = r.json()
    out = []
    for feat in data.get("features", []):
        prop = feat.get("properties", {}) or {}
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates") or [None, None, None]
        event = {
            "source": "USGS",
            "mag": prop.get("mag"),
            "place": prop.get("place"),
            "time": parse_iso_time(prop.get("time")) or (datetime.utcfromtimestamp(int(prop.get("time",0))/1000.0) if prop.get("time") else None),
            "depth_km": coords[2] if len(coords) > 2 else None,
            "lat": coords[1] if len(coords) > 1 else None,
            "lon": coords[0] if len(coords) > 0 else None,
            "id": feat.get("id"),
        }
        out.append(event)
    return out

def query_bmkg(days: int = 7) -> List[Dict[str, Any]]:
    """
    BMKG offers JSON files like autogempa.json and gempaterkini.json.
    We'll fetch autogempa (latest single event) and gempaterkini (recent list),
    then filter by time window (days).
    """
    base = "https://data.bmkg.go.id/gempabumi"
    results = []
    try:
        # latest single event (autogempa.json)
        r1 = requests.get(f"{base}/autogempa.json", timeout=20)
        r1.raise_for_status()
        j1 = r1.json()
        # structure may vary; try common keys
        # Example keys: 'Infogempa' or direct 'gempa' -> handle both
        cand = []
        if isinstance(j1, dict):
            if "Infogempa" in j1:
                cand = [j1["Infogempa"]]
            elif "gempa" in j1:
                cand = [j1["gempa"]]
            else:
                # fallback: take whole dict as single event
                cand = [j1]
        for it in cand:
            # BMKG autogempa keys: 'DateTime' (UTC), 'Magnitude', 'Coordinates', 'Depth', 'Wilayah'
            dt = it.get("DateTime") or it.get("Date") or it.get("Tanggal") or it.get("DateTimeUTC")
            mag = it.get("Magnitude") or it.get("Magnitudo") or it.get("MagnitudeValue")
            coords = it.get("Coordinates") or it.get("coordinates") or it.get("point") or ""
            # attempt parse coordinates: BMKG often uses "lat lon" or "(-6.123,106.8)"
            lat = None; lon = None
            if coords:
                # try common formats
                if isinstance(coords, str):
                    s = coords.replace("(", "").replace(")", "").replace(",", " ").strip()
                    parts = s.split()
                    if len(parts) >= 2:
                        try:
                            lat = float(parts[0]); lon = float(parts[1])
                        except:
                            lat = lon = None
                elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
                    lat = float(coords[0]); lon = float(coords[1])
            depth = it.get("Depth") or it.get("Kedalaman")
            place = it.get("Wilayah") or it.get("Region") or it.get("RegionName") or it.get("Place")
            results.append({
                "source": "BMKG",
                "mag": float(mag) if mag not in (None, "") else None,
                "place": place,
                "time": parse_iso_time(dt) if dt else None,
                "depth_km": float(depth) if depth not in (None, "") else None,
                "lat": lat,
                "lon": lon,
                "id": it.get("Shakemap") or it.get("Tanggal") or None
            })
    except Exception:
        # ignore BMKG autogempa failure; continue to gempaterkini
        pass

    # gempaterkini.json -> list of recent events (15)
    try:
        r2 = requests.get(f"{base}/gempaterkini.json", timeout=20)
        r2.raise_for_status()
        j2 = r2.json()
        # j2 may contain 'Gempaterkini' or 'gempaterkini' array
        arr = []
        if isinstance(j2, dict):
            # try a few likely keys
            for key in ("Gempaterkini", "gempaterkini", "Data", "gempas"):
                if key in j2 and isinstance(j2[key], list):
                    arr = j2[key]
                    break
            # fallback: find any list within dict
            if not arr:
                for v in j2.values():
                    if isinstance(v, list):
                        arr = v
                        break
        elif isinstance(j2, list):
            arr = j2

        for it in arr:
            # typical BMKG item keys: 'Tanggal', 'Mag', 'Coordinates', 'Wilayah', 'Kedalaman'
            dt = it.get("DateTime") or it.get("Tanggal") or it.get("DateTimeUTC") or it.get("Date")
            mag = it.get("Magnitude") or it.get("Mag") or it.get("Magnitudo")
            coords = it.get("Coordinates") or it.get("coordinates") or it.get("coordinate") or it.get("point")
            lat = lon = None
            if coords:
                if isinstance(coords, str):
                    s = coords.replace("(", "").replace(")", "").replace(",", " ").strip()
                    parts = s.split()
                    if len(parts) >= 2:
                        try:
                            lat = float(parts[0]); lon = float(parts[1])
                        except:
                            lat = lon = None
                elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
                    lat = float(coords[0]); lon = float(coords[1])
            depth = it.get("Depth") or it.get("Kedalaman")
            place = it.get("Wilayah") or it.get("Region") or it.get("Place") or it.get("Wilayah")
            results.append({
                "source": "BMKG",
                "mag": float(mag) if mag not in (None, "") else None,
                "place": place,
                "time": parse_iso_time(dt) if dt else None,
                "depth_km": float(depth) if depth not in (None, "") else None,
                "lat": lat,
                "lon": lon,
                "id": it.get("Id") or it.get("Tanggal") or None
            })
    except Exception:
        pass

    # Filter by days window
    cutoff = datetime.utcnow() - timedelta(days=max(1, int(days)))
    filtered = [e for e in results if (e.get("time") is None or e.get("time") >= cutoff)]
    return filtered

def merge_events(usgs_list: List[Dict[str,Any]], bmkg_list: List[Dict[str,Any]], center_lat: float, center_lon: float, radius_km: int) -> List[Dict[str,Any]]:
    """
    Merge lists, dedupe by proximity+time+mag.
    Keep events within radius_km of center if lat/lon provided.
    """
    all_events = []
    # include BMKG first for priority
    for e in bmkg_list + usgs_list:
        # skip events without coords if center provided
        if e.get("lat") is not None and e.get("lon") is not None:
            dist = haversine_km(center_lat, center_lon, e["lat"], e["lon"])
            if dist > radius_km + 1:  # small tolerance
                continue
            e["_dist_km"] = round(dist, 2)
        else:
            e["_dist_km"] = None
        all_events.append(e)

    # dedupe: same time (within 30s) and mag (within 0.2) and location (within 10 km)
    deduped = []
    for e in all_events:
        matched = False
        for d in deduped:
            t1 = e.get("time"); t2 = d.get("time")
            if t1 and t2:
                dt = abs((t1 - t2).total_seconds())
            else:
                dt = None
            mag1 = e.get("mag"); mag2 = d.get("mag")
            mag_diff = abs(mag1 - mag2) if (mag1 is not None and mag2 is not None) else None
            if e.get("lat") is not None and d.get("lat") is not None:
                loc_dist = haversine_km(e["lat"], e["lon"], d["lat"], d["lon"])
            else:
                loc_dist = None
            cond_time = (dt is not None and dt <= 30)
            cond_mag = (mag_diff is not None and mag_diff <= 0.2)
            cond_loc = (loc_dist is not None and loc_dist <= 10)
            # if two of three match, consider duplicate
            score = sum([bool(cond_time), bool(cond_mag), bool(cond_loc)])
            if score >= 2:
                # merge: prefer BMKG fields if one is from BMKG
                if d.get("source") == "BMKG":
                    # keep d
                    pass
                elif e.get("source") == "BMKG":
                    # replace d with e (BMKG preferred)
                    deduped.remove(d)
                    deduped.append(e)
                matched = True
                break
        if not matched:
            deduped.append(e)
    # sort by time desc (newest first)
    deduped.sort(key=lambda x: x.get("time") or datetime.min, reverse=True)
    return deduped

def get_earthquakes(location: str, radius_km: int = 200, days: int = 7) -> Dict[str, Any]:
    """
    Return recent earthquakes near a location string using BMKG (if Indonesia) + USGS.
    """
    if not location or not location.strip():
        raise ValueError("location is required")

    # Geocode (Open-Meteo)
    geo_params = {"name": location, "count": 1, "language": "en", "format": "json"}
    gr = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params=geo_params,
        timeout=30,
    )
    gr.raise_for_status()
    g = gr.json()
    if not g.get("results"):
        raise RuntimeError(f"No geocoding match for: {location}")

    r0 = g["results"][0]
    latitude = r0["latitude"]
    longitude = r0["longitude"]
    country = (r0.get("country") or "").strip()
    display = ", ".join([v for v in [r0.get("name"), r0.get("admin1"), r0.get("country")] if v])

    # Detect Indonesia either by country field or bounding box
    is_indonesia = False
    if country.lower() == "indonesia" or "indonesia" in display.lower():
        is_indonesia = True
    # rough bounding box of Indonesia
    if not is_indonesia:
        if -11.0 <= latitude <= 6.5 and 94.5 <= longitude <= 141.0:
            is_indonesia = True

    usgs_events = []
    bmkg_events = []

    # Query USGS always (global)
    try:
        usgs_events = query_usgs(latitude, longitude, radius_km, days, limit=100)
    except Exception:
        usgs_events = []

    # If Indonesia -> query BMKG and merge
    if is_indonesia:
        try:
            bmkg_events = query_bmkg(days=days)
        except Exception:
            bmkg_events = []

    merged = merge_events(usgs_events, bmkg_events, latitude, longitude, radius_km)

    if not merged:
        return {"earthquakes": f"No earthquakes found within {radius_km} km of {display} in the past {days} day(s)."}

    # Format up to 12 items
    max_items = 12
    lines = [f"Earthquakes within {radius_km} km of {display} (last {days} day(s)):"]
    for i, e in enumerate(merged[:max_items]):
        t = e.get("time")
        time_str = t.strftime("%Y-%m-%d %H:%M UTC") if t else "unknown time"
        mag = e.get("mag")
        mag_str = f"M {mag:.1f}" if mag is not None else "M ?"
        depth = e.get("depth_km")
        depth_str = f"{depth} km depth" if depth is not None else ""
        place = e.get("place") or ""
        src = e.get("source") or "?"
        dist = f"{e['_dist_km']} km" if e.get("_dist_km") is not None else ""
        lines.append(f"{i+1}. {mag_str} — {place} ({time_str}) {depth_str} {dist} [{src}]".strip())
    if len(merged) > max_items:
        lines.append(f"...and {len(merged) - max_items} more events (showing {max_items}).")

    return {"earthquakes": "\n".join(lines)}
