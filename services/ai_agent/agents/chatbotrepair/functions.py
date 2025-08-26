# === Standard library imports ===
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import math

# === Third-party imports ===
import requests

# === Models / Data containers ===
from uagents import Model


class EarthquakeRequest(Model):
    """Request model for earthquake lookups.

    Fields:
    - location: free-text location string (city, region, or country).
    - radius_km: search radius in kilometers (default 200).
    - days: time window in days (default 7).

    This model is consumed by the structured-output workflow in the agent.
    """
    location: str
    radius_km: Optional[int] = 200
    days: Optional[int] = 7


class EarthquakeResponse(Model):
    """Simple response model containing a textual `earthquakes` field.

    The field is a human-readable multi-line summary produced by `get_earthquakes`.
    """
    earthquakes: str


# === Helper functions ===

def haversine_km(lat1, lon1, lat2, lon2):
    """Return the great-circle distance between two points using the Haversine formula.

    Inputs are lat/lon in decimal degrees. Returns kilometers as float.

    NOTE: This is a synchronous, pure function with no side effects.
    """
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def parse_iso_time(s: str):
    """Try several ISO / timestamp formats and return a `datetime` or `None`.

    - Accepts: ISO 8601 with milliseconds, without milliseconds, a space-separated format,
      or a millisecond UNIX timestamp (int or numeric-string).
    - Returns None if parsing fails.
    """
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    try:
        # Some providers return epoch milliseconds as an integer/string
        return datetime.utcfromtimestamp(int(s) / 1000.0)
    except Exception:
        return None


def query_usgs(lat: float, lon: float, radius_km: int, days: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Query the USGS earthquake API around a lat/lon.

    - Builds a time-window [now - days, now] and requests geojson results.
    - Returns a list of normalized event dicts with keys: source, mag, place, time, depth_km, lat, lon, id.
    - Raises for HTTP errors via requests.raise_for_status().
    """
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
            # Some USGS feeds provide time as epoch ms in 'time' property
            "time": parse_iso_time(prop.get("time")) or (datetime.utcfromtimestamp(int(prop.get("time",0))/1000.0) if prop.get("time") else None),
            "depth_km": coords[2] if len(coords) > 2 else None,
            "lat": coords[1] if len(coords) > 1 else None,
            "lon": coords[0] if len(coords) > 0 else None,
            "id": feat.get("id"),
        }
        out.append(event)
    return out


def query_bmkg(days: int = 7) -> List[Dict[str, Any]]:
    """Query BMKG public JSON endpoints and normalize results.

    BMKG returns different JSON shapes depending on endpoint/version. This function tries
    multiple endpoints and attempts to normalize fields like Magnitude, DateTime, Coordinates, and place names.

    - Returns events that are not older than `days`.
    - Silently ignores exceptions and returns what it managed to parse.
    """
    base = "https://data.bmkg.go.id/gempabumi"
    results = []
    try:
        r1 = requests.get(f"{base}/autogempa.json", timeout=20)
        r1.raise_for_status()
        j1 = r1.json()
        cand = []
        if isinstance(j1, dict):
            if "Infogempa" in j1:
                cand = [j1["Infogempa"]]
            elif "gempa" in j1:
                cand = [j1["gempa"]]
            else:
                cand = [j1]
        for it in cand:
            dt = it.get("DateTime") or it.get("Date") or it.get("Tanggal") or it.get("DateTimeUTC")
            mag = it.get("Magnitude") or it.get("Magnitudo") or it.get("MagnitudeValue")
            coords = it.get("Coordinates") or it.get("coordinates") or it.get("point") or ""
            lat = None
            lon = None
            if coords:
                if isinstance(coords, str):
                    s = coords.replace("(", "").replace(")", "").replace(",", " ").strip()
                    parts = s.split()
                    if len(parts) >= 2:
                        try:
                            lat = float(parts[0])
                            lon = float(parts[1])
                        except:
                            lat = lon = None
                elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
                    lat = float(coords[0])
                    lon = float(coords[1])
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
                "id": it.get("Shakemap") or it.get("Tanggal") or None,
            })
    except Exception:
        pass
    try:
        r2 = requests.get(f"{base}/gempaterkini.json", timeout=20)
        r2.raise_for_status()
        j2 = r2.json()
        arr = []
        if isinstance(j2, dict):
            for key in ("Gempaterkini", "gempaterkini", "Data", "gempas"):
                if key in j2 and isinstance(j2[key], list):
                    arr = j2[key]
                    break
            if not arr:
                for v in j2.values():
                    if isinstance(v, list):
                        arr = v
                        break
        elif isinstance(j2, list):
            arr = j2
        for it in arr:
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
                            lat = float(parts[0])
                            lon = float(parts[1])
                        except:
                            lat = lon = None
                elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
                    lat = float(coords[0])
                    lon = float(coords[1])
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
                "id": it.get("Id") or it.get("Tanggal") or None,
            })
    except Exception:
        pass
    cutoff = datetime.utcnow() - timedelta(days=max(1, int(days)))
    # Keep only recent events according to cutoff. Events with unknown time are retained.
    filtered = [e for e in results if (e.get("time") is None or e.get("time") >= cutoff)]
    return filtered


def merge_events(usgs_list: List[Dict[str, Any]], bmkg_list: List[Dict[str, Any]], center_lat: float, center_lon: float, radius_km: int) -> List[Dict[str, Any]]:
    """Merge and deduplicate events from USGS and BMKG.

    Strategy:
    - Compute distance from center for each event (if lat/lon available).
    - Discard events outside radius_km + 1km buffer.
    - Deduplicate by comparing (time difference <= 30s, magnitude difference <= 0.2, location distance <= 10km).
      If two events match, prefer BMKG entries when available.
    - Sort by time descending (newest first).
    """
    all_events = []
    for e in bmkg_list + usgs_list:
        if e.get("lat") is not None and e.get("lon") is not None:
            dist = haversine_km(center_lat, center_lon, e["lat"], e["lon"])
            if dist > radius_km + 1:
                continue
            e["_dist_km"] = round(dist, 2)
        else:
            e["_dist_km"] = None
        all_events.append(e)
    deduped = []
    for e in all_events:
        matched = False
        for d in deduped:
            t1 = e.get("time")
            t2 = d.get("time")
            dt = abs((t1 - t2).total_seconds()) if t1 and t2 else None
            mag1 = e.get("mag")
            mag2 = d.get("mag")
            mag_diff = abs(mag1 - mag2) if (mag1 is not None and mag2 is not None) else None
            loc_dist = haversine_km(e["lat"], e["lon"], d["lat"], d["lon"]) if e.get("lat") is not None and d.get("lat") is not None else None
            cond_time = (dt is not None and dt <= 30)
            cond_mag = (mag_diff is not None and mag_diff <= 0.2)
            cond_loc = (loc_dist is not None and loc_dist <= 10)
            score = sum([bool(cond_time), bool(cond_mag), bool(cond_loc)])
            if score >= 2:
                # Prefer BMKG if present. Keep deduped list stable.
                if d.get("source") == "BMKG":
                    pass
                elif e.get("source") == "BMKG":
                    deduped.remove(d)
                    deduped.append(e)
                matched = True
                break
        if not matched:
            deduped.append(e)
    deduped.sort(key=lambda x: x.get("time") or datetime.min, reverse=True)
    return deduped


def get_earthquakes(location: str, radius_km: int = 200, days: int = 7) -> Dict[str, Any]:
    """Main entry point used by the agent to fetch and format earthquake information.

    Steps:
    1. Validate `location` argument.
    2. Resolve `location` to lat/lon using Open-Meteo geocoding API.
    3. Query USGS and optionally BMKG (if location is in Indonesia).
    4. Merge/deduplicate, format up to `max_items` and return a dict with `earthquakes` string.

    Returns:
    - {"earthquakes": <string>} where the string is a human-readable summary.

    Errors:
    - Raises RuntimeError if geocoding fails. Other network errors are propagated from requests unless caught where used.
    """
    if not location or not location.strip():
        raise ValueError("location is required")
    geo_params = {"name": location, "count": 1, "language": "en", "format": "json"}
    gr = requests.get("https://geocoding-api.open-meteo.com/v1/search", params=geo_params, timeout=30)
    gr.raise_for_status()
    g = gr.json()
    if not g.get("results"):
        raise RuntimeError(f"No geocoding match for: {location}")
    r0 = g["results"][0]
    latitude = r0["latitude"]
    longitude = r0["longitude"]
    country = (r0.get("country") or "").strip()
    display = ", ".join([v for v in [r0.get("name"), r0.get("admin1"), r0.get("country")] if v])
    # Heuristic: treat many locations in the Indonesian bounding box as Indonesia when geocoding country is missing.
    is_indonesia = False
    if country.lower() == "indonesia" or "indonesia" in display.lower():
        is_indonesia = True
    if not is_indonesia:
        if -11.0 <= latitude <= 6.5 and 94.5 <= longitude <= 141.0:
            is_indonesia = True
    usgs_events = []
    bmkg_events = []
    try:
        usgs_events = query_usgs(latitude, longitude, radius_km, days, limit=100)
    except Exception:
        usgs_events = []
    if is_indonesia:
        try:
            bmkg_events = query_bmkg(days=days)
        except Exception:
            bmkg_events = []
    merged = merge_events(usgs_events, bmkg_events, latitude, longitude, radius_km)
    if not merged:
        return {"earthquakes": f"No earthquakes found within {radius_km} km of {display} in the past {days} day(s)."}
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

