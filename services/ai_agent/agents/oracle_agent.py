# =====================================================================
# AEGIS Protocol - Oracle Agent
# =====================================================================
# Module: oracle_agent.py
# Purpose: Multi-source disaster data monitoring and validation
# 
# Architecture Overview:
#   The Oracle Agent serves as the primary data collection layer in the
#   AEGIS Protocol's three-tier AI system (Oracle → Validator → Action).
#   It continuously monitors real-world disaster data sources and forwards
#   validated events to the Validator Agent for consensus processing.
# 
# Data Sources:
#   - USGS: United States Geological Survey earthquake data
#   - BMKG: Indonesian Meteorology, Climatology, and Geophysics Agency
#   - Extensible architecture for additional disaster data sources
# 
# Key Features:
#   - Real-time monitoring with configurable polling intervals
#   - Multi-source data aggregation and normalization
#   - Duplicate event detection to prevent processing redundancy
#   - Fault-tolerant error handling for network and API issues
#   - Standardized data models for downstream processing
# 
# Agent Communication:
#   - Receives: Periodic timer triggers (internal)
#   - Sends: RawEarthquakeData messages to Validator Agent
#   - Protocol: Fetch.ai uAgents messaging system
# 
# Data Flow:
#   1. Periodic polling of external APIs (USGS, BMKG)
#   2. Parse and normalize data into standard format
#   3. Filter out duplicate events using unique identifiers
#   4. Forward new events to Validator Agent for consensus
# 
# Environment Variables:
#   ORACLE_AGENT_SEED: Cryptographic seed for agent identity
#   VALIDATOR_AGENT_ADDRESS: Target address for forwarding data
#   FETCH_INTERVAL_SECONDS: Polling frequency (default: 300s)
# =====================================================================

import os
import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
import httpx

# Fetch.ai uAgents framework for decentralized AI agent development
from uagents import Agent, Context, Model # type: ignore
from uagents.setup import fund_agent_if_low # type: ignore

# =====================================================================
# CONFIGURATION AND ENVIRONMENT SETUP
# =====================================================================
# Agent identity and communication configuration

# Cryptographic seed for deterministic agent identity generation
# Used to ensure consistent agent address across restarts
ORACLE_SEED = os.getenv("ORACLE_AGENT_SEED", "oracle_agent_secret_seed_phrase_placeholder")

# Target validator agent address for data forwarding
# Must be set for the Oracle Agent to function properly
VALIDATOR_AGENT_ADDRESS = os.getenv("VALIDATOR_AGENT_ADDRESS")

# External API endpoints for disaster data collection
# USGS: Provides earthquake data for magnitude 4.5+ events in last 24 hours
# Format: GeoJSON with standardized earthquake properties
USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"

# BMKG: Indonesian agency providing regional earthquake data
# Format: JSON with localized earthquake information
BMKG_API_URL = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"

# Polling interval configuration (seconds)
# Default: 5 minutes (300 seconds) to balance timeliness with API rate limits
FETCH_INTERVAL_SECONDS = float(os.getenv("FETCH_INTERVAL_SECONDS", 300.0))

# =====================================================================
# DATA MODEL DEFINITIONS
# =====================================================================
# Standardized data structures for earthquake event representation

class RawEarthquakeData(Model):
    """
    Standardized earthquake event data model for inter-agent communication.
    
    This model normalizes earthquake data from multiple sources (USGS, BMKG)
    into a consistent format that can be processed by downstream agents.
    
    Attributes:
        source (str): Data source identifier (e.g., "USGS_API_Oracle", "BMKG_API_Oracle")
        magnitude (float): Earthquake magnitude on Richter scale
        location (str): Human-readable location description
        lat (float): Latitude coordinate in decimal degrees
        lon (float): Longitude coordinate in decimal degrees
        timestamp (int): Unix timestamp of earthquake occurrence
    
    Design Notes:
        - Uses Unix timestamps for timezone-independent time representation
        - Magnitude field accommodates both integer and decimal values
        - Location field preserves original source descriptions for context
        - Coordinates use standard WGS84 datum for global compatibility
    """
    source: str
    magnitude: float
    location: str
    lat: float
    lon: float
    timestamp: int

# =====================================================================
# AGENT INITIALIZATION AND SETUP
# =====================================================================
# Configure and initialize the Oracle Agent with networking and identity

oracle_agent = Agent(
    name="oracle_agent_multi_source",           # Human-readable agent identifier
    port=8001,                                  # Network port for agent communication
    seed=ORACLE_SEED,                           # Cryptographic seed for identity
    endpoint=["http://oracle-agent-1:8001/submit"],  # Docker network endpoint
)

# Ensure agent has sufficient funds for network operations
# The Fetch.ai network requires tokens for message transmission
fund_agent_if_low(str(oracle_agent.wallet.address()))

# Log agent initialization with address for debugging and monitoring
oracle_agent._logger.info(f"Oracle Agent initialized successfully")
oracle_agent._logger.info(f"Agent address: {oracle_agent.address}")
oracle_agent._logger.info(f"Listening on port: 8001")
oracle_agent._logger.info(f"Monitoring sources: USGS, BMKG")
oracle_agent._logger.info(f"Polling interval: {FETCH_INTERVAL_SECONDS} seconds")

# =====================================================================
# EVENT DEDUPLICATION SYSTEM
# =====================================================================
# Global state management for preventing duplicate event processing

# Set to track previously processed events and prevent duplicates
# Events are identified by unique combination of source, timestamp, and magnitude
# This prevents redundant processing when APIs return overlapping data
SEEN_EVENT_IDS: Set[str] = set()

# Note: In production, this should be persisted to disk or database
# to maintain state across agent restarts. Current implementation
# loses state on restart but is sufficient for development/testing.

# =====================================================================
# DATA PARSING AND NORMALIZATION FUNCTIONS
# =====================================================================
# Source-specific parsers for converting API responses to standard format

def _parse_usgs_data(feature: Dict[str, Any]) -> Optional[RawEarthquakeData]:
    """
    Parse USGS GeoJSON earthquake feature into standardized format.
    
    USGS API Structure:
        - features[].properties: Event metadata (magnitude, time, place)
        - features[].geometry.coordinates: [longitude, latitude, depth]
    
    Args:
        feature: Individual earthquake feature from USGS GeoJSON response
        
    Returns:
        RawEarthquakeData object or None if parsing fails
        
    Error Handling:
        - Gracefully handles missing or malformed data fields
        - Logs warnings for debugging without stopping processing
        - Returns None for invalid data to maintain processing flow
    """
    try:
        # Extract event properties and coordinates with safety checks
        props: Dict[str, Any] = feature['properties']
        coords: List[float] = feature['geometry']['coordinates']
        
        # Validate required fields are present and non-null
        if props.get('mag') is None or props.get('time') is None:
            return None
            
        # Create standardized earthquake data object
        return RawEarthquakeData(
            source="USGS_API_Oracle",                           # Source identifier
            magnitude=float(props['mag']),                      # Magnitude on Richter scale
            location=str(props.get('place', 'Unknown Location')), # Human-readable location
            lat=float(coords[1]),                               # Latitude (second coordinate)
            lon=float(coords[0]),                               # Longitude (first coordinate)
            timestamp=int(props['time'] // 1000)                # Convert milliseconds to seconds
        )
    except (KeyError, TypeError, IndexError) as e:
        # Log parsing errors for debugging without halting processing
        oracle_agent._logger.warning(f"Failed to parse USGS data item: {e}")
        return None

def _parse_bmkg_data(gempa: Dict[str, Any]) -> Optional[RawEarthquakeData]:
    """
    Parse BMKG JSON earthquake data into standardized format.
    
    BMKG API Structure:
        - Infogempa.gempa: Single earthquake object with Indonesian formatting
        - Coordinates: "latitude,longitude" string format
        - DateTime: ISO 8601 string with 'Z' suffix
        - Magnitude: String or numeric magnitude value
        - Wilayah: Indonesian region/location description
    
    Args:
        gempa: Earthquake data object from BMKG JSON response
        
    Returns:
        RawEarthquakeData object or None if parsing fails
        
    Regional Context:
        - BMKG provides Indonesia-specific earthquake monitoring
        - Coordinates use comma-separated latitude,longitude format
        - Location names are in Indonesian language
        - Time format includes timezone information
    """
    try:
        # Parse coordinate string format: "latitude,longitude"
        coords_str: str = gempa.get('Coordinates', '0,0')
        lat_str, lon_str = coords_str.split(',')
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        
        # Parse ISO 8601 datetime string with timezone handling
        dt_text: Optional[str] = gempa.get('DateTime')
        if not dt_text:
            return None
        # Convert 'Z' suffix to proper timezone format for Python parsing
        dt_object = datetime.fromisoformat(dt_text.replace('Z', '+00:00'))

        # Create standardized earthquake data object
        return RawEarthquakeData(
            source="BMKG_API_Oracle",                          # Indonesian source identifier
            magnitude=float(gempa.get('Magnitude', 0)),        # Magnitude conversion to float
            location=str(gempa.get('Wilayah', 'Unknown Location')), # Indonesian location name
            lat=lat,                                           # Parsed latitude
            lon=lon,                                           # Parsed longitude
            timestamp=int(dt_object.timestamp())               # Unix timestamp conversion
        )
    except Exception as e:
        # Broad exception handling for various parsing failures
        oracle_agent._logger.warning(f"Failed to parse BMKG data item: {e}")
        return None

# =====================================================================
# DATA FETCHING AND PROCESSING FUNCTIONS
# =====================================================================
# HTTP client management and source-specific data retrieval

# Type alias for parser function signature
# Enables flexible parser assignment for different data sources
ParserFunc = Callable[[Dict[str, Any]], Optional[RawEarthquakeData]]

async def _fetch_from_source(
    ctx: Context, 
    client: httpx.AsyncClient, 
    url: str, 
    parser: ParserFunc, 
    source_name: str
) -> List[RawEarthquakeData]:
    """
    Fetch and parse earthquake data from a specific API source.
    
    This function handles the complete data retrieval pipeline:
    1. HTTP request with timeout and error handling
    2. JSON response parsing and validation
    3. Source-specific data extraction logic
    4. Data normalization using provided parser function
    
    Args:
        ctx: Agent context for logging and state management
        client: Async HTTP client for making API requests
        url: API endpoint URL to fetch data from
        parser: Source-specific parsing function
        source_name: Human-readable source identifier for logging
        
    Returns:
        List of parsed earthquake data objects
        
    Error Handling:
        - Network timeouts and connection failures
        - HTTP error status codes (4xx, 5xx)
        - JSON parsing and structure validation
        - Individual item parsing failures
        
    Performance Considerations:
        - 20-second timeout to prevent hanging requests
        - Async processing for non-blocking operation
        - Minimal memory footprint with streaming processing
    """
    ctx.logger.info(f"Fetching earthquake data from {source_name} API...")
    ctx.logger.debug(f"API URL: {url}")
    
    try:
        # Make HTTP request with timeout protection
        response = await client.get(url, timeout=20.0)
        response.raise_for_status()  # Raise exception for HTTP error status
        json_data = response.json()
        
        ctx.logger.debug(f"Received response from {source_name}, processing data...")
        all_parsed_data: List[RawEarthquakeData] = []
        
        # Source-specific data extraction logic
        if source_name == "USGS":
            # USGS provides array of earthquake features in GeoJSON format
            features: List[Dict[str, Any]] = json_data.get('features', [])
            ctx.logger.debug(f"Processing {len(features)} USGS earthquake features")
            
            for feature in features:
                parsed = parser(feature)
                if parsed:
                    all_parsed_data.append(parsed)
                    
        elif source_name == "BMKG":
            # BMKG provides single earthquake object in nested structure
            gempa_info: Optional[Dict[str, Any]] = json_data.get('Infogempa', {}).get('gempa')
            if gempa_info:
                ctx.logger.debug("Processing BMKG earthquake data")
                parsed = parser(gempa_info)
                if parsed:
                    all_parsed_data.append(parsed)
            else:
                ctx.logger.debug("No earthquake data found in BMKG response")
        
        ctx.logger.info(f"Successfully processed {len(all_parsed_data)} events from {source_name}")
        return all_parsed_data
        
    except Exception as e:
        # Comprehensive error logging for debugging and monitoring
        ctx.logger.error(f"Error fetching/processing data from {source_name}: {e}")
        ctx.logger.debug(f"Error type: {type(e).__name__}")
        return []  # Return empty list to maintain processing flow

# =====================================================================
# MAIN PERIODIC PROCESSING FUNCTION
# =====================================================================
# Core agent behavior: periodic monitoring and event forwarding

@oracle_agent.on_interval(period=FETCH_INTERVAL_SECONDS) # type: ignore
async def fetch_and_send_data(ctx: Context):
    """
    Main periodic function that orchestrates disaster data collection and forwarding.
    
    This function implements the core Oracle Agent behavior:
    1. Validates configuration and connectivity
    2. Fetches data from all configured sources concurrently
    3. Normalizes and deduplicates earthquake events
    4. Forwards new events to Validator Agent for consensus
    
    Execution Flow:
        - Triggered every FETCH_INTERVAL_SECONDS (default: 300s)
        - Runs asynchronously to prevent blocking agent operations
        - Handles failures gracefully to maintain continuous monitoring
        - Logs detailed information for debugging and monitoring
    
    Data Processing Pipeline:
        1. Configuration validation (validator address check)
        2. Concurrent API calls to all data sources (USGS, BMKG)
        3. Data aggregation and flattening
        4. Duplicate detection using unique event identifiers
        5. Message transmission to downstream validator
    
    Error Handling:
        - Graceful degradation on source failures
        - Continues processing if some sources are unavailable
        - Logs errors without stopping periodic execution
        - Maintains agent health for long-term operation
    
    Performance Optimizations:
        - Concurrent API calls using asyncio.gather()
        - Efficient duplicate detection with set operations
        - Minimal memory footprint with generator patterns
    """
    # ================================================================
    # Configuration and Connectivity Validation
    # ================================================================
    if not VALIDATOR_AGENT_ADDRESS:
        ctx.logger.warning("Validator Agent address not configured - skipping data fetch")
        ctx.logger.warning("Set VALIDATOR_AGENT_ADDRESS environment variable to enable forwarding")
        return

    ctx.logger.info("========================================================")
    ctx.logger.info("Oracle Agent - Periodic Data Collection Cycle Started")
    ctx.logger.info("========================================================")
    ctx.logger.info(f"Fetching from {len(['USGS', 'BMKG'])} configured sources...")
    ctx.logger.debug(f"Validator target: {VALIDATOR_AGENT_ADDRESS}")
    ctx.logger.debug(f"Polling interval: {FETCH_INTERVAL_SECONDS} seconds")
    # ================================================================
    # Concurrent Data Retrieval from Multiple Sources
    # ================================================================
    # Use async HTTP client for efficient concurrent requests
    async with httpx.AsyncClient() as client:
        # Define data source tasks for concurrent execution
        # Each task fetches and parses data from a specific API endpoint
        tasks = [
            _fetch_from_source(ctx, client, USGS_API_URL, _parse_usgs_data, "USGS"),
            _fetch_from_source(ctx, client, BMKG_API_URL, _parse_bmkg_data, "BMKG")
            # Additional sources can be added here for expanded monitoring
        ]
        
        ctx.logger.debug(f"Executing {len(tasks)} concurrent API requests...")
        # Execute all API calls concurrently for optimal performance
        results: List[List[RawEarthquakeData]] = await asyncio.gather(*tasks)
        
    # Flatten results from all sources into single list
    # This aggregates earthquake events from USGS, BMKG, and any future sources
    all_earthquakes: List[RawEarthquakeData] = [item for sublist in results for item in sublist]
    
    ctx.logger.info(f"Data collection complete - found {len(all_earthquakes)} total events")
    for i, result_list in enumerate(results):
        source_name = ["USGS", "BMKG"][i]
        ctx.logger.debug(f"  {source_name}: {len(result_list)} events")

    # ================================================================
    # Early Exit Conditions
    # ================================================================
    if not all_earthquakes:
        ctx.logger.info("No earthquake data found from any source")
        ctx.logger.debug("This could indicate: API downtime, no recent events, or network issues")
        return

    # ================================================================
    # Event Deduplication and Filtering
    # ================================================================
    # Generate unique identifiers for each earthquake event
    # Format: "source-timestamp-magnitude" ensures uniqueness across sources
    new_earthquakes_to_send = []
    
    ctx.logger.debug("Performing duplicate detection and filtering...")
    for eq_data in all_earthquakes:
        # Create composite unique identifier from event characteristics
        event_id = f"{eq_data.source}-{eq_data.timestamp}-{eq_data.magnitude:.2f}"
        
        # Check if this event has been processed previously
        if event_id not in SEEN_EVENT_IDS:
            new_earthquakes_to_send.append(eq_data)
            SEEN_EVENT_IDS.add(event_id)  # Mark as processed
            ctx.logger.debug(f"New event detected: {event_id}")
        else:
            ctx.logger.debug(f"Duplicate event filtered: {event_id}")
    
    ctx.logger.info(f"Deduplication complete - {len(new_earthquakes_to_send)} new unique events")
    ctx.logger.debug(f"Total events seen: {len(SEEN_EVENT_IDS)} (cumulative)")

    # ================================================================
    # Final Validation and Early Exit
    # ================================================================
    if not new_earthquakes_to_send:
        ctx.logger.info("All detected events were duplicates - no forwarding needed")
        ctx.logger.debug("This indicates system is working correctly and avoiding duplicate processing")
        return
        
    # ================================================================
    # Event Forwarding to Validator Agent
    # ================================================================
    ctx.logger.info(f"Forwarding {len(new_earthquakes_to_send)} new events to Validator Agent...")
    ctx.logger.debug(f"Target validator: {VALIDATOR_AGENT_ADDRESS}")
    
    # Send each earthquake event as separate message for granular processing
    success_count = 0
    failure_count = 0
    
    for eq_data in new_earthquakes_to_send:
        try:
            # Forward earthquake data to validator for consensus processing
            await ctx.send(VALIDATOR_AGENT_ADDRESS, eq_data)
            
            # Log successful transmission with event details
            ctx.logger.info(f"✓ Sent: {eq_data.source} | {eq_data.location} | M{eq_data.magnitude}")
            ctx.logger.debug(f"  Coordinates: ({eq_data.lat:.4f}, {eq_data.lon:.4f})")
            ctx.logger.debug(f"  Timestamp: {eq_data.timestamp} ({datetime.fromtimestamp(eq_data.timestamp)})")
            
            success_count += 1
            
        except Exception as e:
            # Log transmission failures without stopping processing
            ctx.logger.error(f"✗ Failed to send {eq_data.source} event: {e}")
            ctx.logger.debug(f"  Event details: {eq_data.location}, M{eq_data.magnitude}")
            failure_count += 1
    
    # ================================================================
    # Cycle Completion and Statistics
    # ================================================================
    ctx.logger.info("========================================================")
    ctx.logger.info("Oracle Agent - Data Collection Cycle Complete")
    ctx.logger.info("========================================================")
    ctx.logger.info(f"Transmission Summary:")
    ctx.logger.info(f"  ✓ Successful: {success_count} events")
    if failure_count > 0:
        ctx.logger.warning(f"  ✗ Failed: {failure_count} events")
    ctx.logger.info(f"Next collection cycle in {FETCH_INTERVAL_SECONDS} seconds")
    ctx.logger.debug(f"Agent health: Normal, continuing monitoring...")

# =====================================================================
# AGENT EXECUTION ENTRY POINT
# =====================================================================
# Start the Oracle Agent when script is run directly

if __name__ == "__main__":
    # Log startup information for debugging and monitoring
    oracle_agent._logger.info("======================================================")
    oracle_agent._logger.info("         AEGIS Protocol - Oracle Agent Starting")
    oracle_agent._logger.info("======================================================")
    oracle_agent._logger.info("Initializing disaster monitoring system...")
    oracle_agent._logger.info(f"Monitoring sources: USGS (Global), BMKG (Indonesia)")
    oracle_agent._logger.info(f"Polling frequency: {FETCH_INTERVAL_SECONDS} seconds")
    oracle_agent._logger.info(f"Target validator: {VALIDATOR_AGENT_ADDRESS or 'Not configured'}")
    oracle_agent._logger.info("Oracle Agent ready - beginning continuous monitoring")
    oracle_agent._logger.info("======================================================")
    
    # Start the agent's main event loop
    # This will run indefinitely, executing periodic data collection
    oracle_agent.run()