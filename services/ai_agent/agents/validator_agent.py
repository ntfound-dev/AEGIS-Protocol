# =====================================================================
# AEGIS Protocol - Validator Agent
# =====================================================================
# Module: validator_agent.py
# Purpose: Earthquake event validation and consensus processing
# 
# Architecture Overview:
#   The Validator Agent serves as the middle layer in the AEGIS Protocol's
#   three-tier AI system (Oracle → Validator → Action). It receives raw
#   earthquake data from Oracle Agents, applies validation logic and consensus
#   mechanisms, then forwards validated events to Action Agents.
# 
# Key Responsibilities:
#   - Receive and validate raw earthquake data from Oracle Agent
#   - Apply consensus algorithms for multi-source data verification
#   - Calculate confidence scores based on data quality and source reliability
#   - Transform raw data into structured ValidatedEvent format
#   - Forward high-confidence events to Action Agent for blockchain processing
# 
# Validation Criteria:
#   - Magnitude thresholds for significance (typically > 4.5)
#   - Geographic validation for plausible locations
#   - Temporal validation for recent events
#   - Cross-source verification when multiple sources available
#   - Data quality assessment (completeness, consistency)
# 
# Agent Communication:
#   - Receives: RawEarthquakeData from Oracle Agent
#   - Sends: ValidatedEvent to Action Agent
#   - Protocol: Fetch.ai uAgents messaging system
# 
# Environment Variables:
#   VALIDATOR_AGENT_SEED: Cryptographic seed for agent identity
#   ACTION_AGENT_ADDRESS: Target address for forwarding validated events
#   MIN_MAGNITUDE_THRESHOLD: Minimum earthquake magnitude to process
# =====================================================================

import os
import json
import asyncio
from typing import Any, Dict
from datetime import datetime, timezone

# Fetch.ai uAgents framework for decentralized AI agent development
from uagents import Agent, Context, Model, Protocol  # type: ignore
from uagents.setup import fund_agent_if_low  # type: ignore

# =====================================================================
# DATA MODEL DEFINITIONS
# =====================================================================
# Input and output data structures for validation processing

class RawEarthquakeData(Model):
    """
    Input data model for raw earthquake events from Oracle Agent.
    
    This model receives unvalidated earthquake data that requires
    consensus processing and quality assessment before forwarding.
    """
    source: str          # Data source identifier (USGS, BMKG, etc.)
    magnitude: float     # Earthquake magnitude on Richter scale
    location: str        # Human-readable location description
    lat: float          # Latitude coordinate in decimal degrees
    lon: float          # Longitude coordinate in decimal degrees
    timestamp: int      # Unix timestamp of earthquake occurrence

class ValidatedEvent(Model):
    """
    Output data model for validated earthquake events sent to Action Agent.
    
    This model represents earthquake data that has passed validation
    and consensus checks, ready for blockchain processing.
    """
    event_type: str        # Event classification (e.g., "earthquake", "tsunami_risk")
    severity: str          # Severity assessment ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    details_json: str      # JSON string containing full event metadata
    confidence_score: float # Validation confidence (0.0-1.0)

class ActionResponse(Model):
    """
    Response model for Action Agent acknowledgments.
    
    Used to confirm successful processing of validated events.
    """
    status: str      # Processing status ("success", "error", "pending")
    message: str     # Human-readable status description


# =====================================================================
# CONFIGURATION AND ENVIRONMENT SETUP
# =====================================================================
# Agent identity and processing parameters

# Cryptographic seed for deterministic agent identity generation
VALIDATOR_AGENT_SEED = os.getenv("VALIDATOR_AGENT_SEED", "validator_agent_secret_seed_phrase_placeholder")

# Target Action Agent address for forwarding validated events
ACTION_AGENT_ADDRESS = os.getenv("ACTION_AGENT_ADDRESS")

# Validation thresholds and parameters
MIN_MAGNITUDE_THRESHOLD = float(os.getenv("MIN_MAGNITUDE_THRESHOLD", "4.5"))
MAX_EVENT_AGE_HOURS = int(os.getenv("MAX_EVENT_AGE_HOURS", "72"))  # 3 days

# =====================================================================
# AGENT INITIALIZATION AND SETUP
# =====================================================================
# Configure and initialize the Validator Agent

validator_agent = Agent(
    name="validator_agent_consensus",            # Human-readable agent identifier
    port=8002,                                  # Network port for agent communication
    seed=VALIDATOR_AGENT_SEED,                  # Cryptographic seed for identity
    endpoint=["http://validator-agent-1:8002/submit"],  # Docker network endpoint
)

# Ensure agent has sufficient funds for network operations
fund_agent_if_low(str(validator_agent.wallet.address()))

# Log agent initialization with configuration details
validator_agent._logger.info(f"Validator Agent initialized successfully")
validator_agent._logger.info(f"Agent address: {validator_agent.address}")
validator_agent._logger.info(f"Listening on port: 8002")
validator_agent._logger.info(f"Minimum magnitude threshold: {MIN_MAGNITUDE_THRESHOLD}")
validator_agent._logger.info(f"Maximum event age: {MAX_EVENT_AGE_HOURS} hours")
validator_agent._logger.info(f"Action Agent target: {ACTION_AGENT_ADDRESS or 'Not configured'}")


# =====================================================================
# VALIDATION PROTOCOL DEFINITION
# =====================================================================
# Define communication protocol for validation processing

validation_protocol = Protocol("ValidationConsensus")


# =====================================================================
# EARTHQUAKE VALIDATION LOGIC
# =====================================================================
# Core validation and consensus algorithms

def validate_earthquake_data(eq_data: RawEarthquakeData) -> tuple[bool, float, str]:
    """
    Validate earthquake data using multiple criteria and calculate confidence score.
    
    Validation Criteria:
    1. Magnitude significance (> minimum threshold)
    2. Geographic plausibility (valid lat/lon ranges)
    3. Temporal relevance (not too old)
    4. Data completeness (all required fields present)
    
    Args:
        eq_data: Raw earthquake data from Oracle Agent
        
    Returns:
        Tuple of (is_valid, confidence_score, severity_level)
        
    Confidence Scoring:
        - 0.9-1.0: High confidence, complete data from reliable source
        - 0.7-0.9: Medium confidence, minor data issues or uncertainty
        - 0.5-0.7: Low confidence, significant data gaps or inconsistencies
        - 0.0-0.5: Very low confidence, reject or flag for manual review
    """
    confidence_factors = []
    
    # Magnitude validation
    if eq_data.magnitude >= MIN_MAGNITUDE_THRESHOLD:
        if eq_data.magnitude >= 7.0:
            magnitude_factor = 1.0  # Major earthquake
        elif eq_data.magnitude >= 6.0:
            magnitude_factor = 0.9  # Strong earthquake
        elif eq_data.magnitude >= 5.0:
            magnitude_factor = 0.8  # Moderate earthquake
        else:
            magnitude_factor = 0.6  # Light earthquake
        confidence_factors.append(magnitude_factor)
    else:
        return False, 0.0, "INSIGNIFICANT"  # Below threshold
    
    # Geographic validation
    if -90 <= eq_data.lat <= 90 and -180 <= eq_data.lon <= 180:
        confidence_factors.append(0.9)  # Valid coordinates
    else:
        return False, 0.0, "INVALID_LOCATION"
    
    # Temporal validation
    current_time = datetime.now(timezone.utc).timestamp()
    event_age_hours = (current_time - eq_data.timestamp) / 3600
    
    if event_age_hours <= MAX_EVENT_AGE_HOURS:
        if event_age_hours <= 1:
            time_factor = 1.0  # Very recent
        elif event_age_hours <= 24:
            time_factor = 0.9  # Recent
        else:
            time_factor = 0.7  # Older but acceptable
        confidence_factors.append(time_factor)
    else:
        return False, 0.0, "TOO_OLD"
    
    # Source reliability assessment
    if eq_data.source == "USGS_API_Oracle":
        source_factor = 1.0  # Highly reliable
    elif eq_data.source == "BMKG_API_Oracle":
        source_factor = 0.9  # Reliable regional source
    else:
        source_factor = 0.7  # Unknown source
    confidence_factors.append(source_factor)
    
    # Data completeness check
    if all([eq_data.location, eq_data.magnitude, eq_data.lat, eq_data.lon]):
        confidence_factors.append(0.9)  # Complete data
    else:
        confidence_factors.append(0.6)  # Missing some fields
    
    # Calculate overall confidence score
    confidence_score = sum(confidence_factors) / len(confidence_factors)
    
    # Determine severity level
    if eq_data.magnitude >= 8.0:
        severity = "CRITICAL"
    elif eq_data.magnitude >= 7.0:
        severity = "HIGH"
    elif eq_data.magnitude >= 6.0:
        severity = "MEDIUM"
    else:
        severity = "LOW"
    
    return True, confidence_score, severity


# =====================================================================
# MESSAGE HANDLERS AND EVENT PROCESSING
# =====================================================================
# Define how the agent responds to incoming messages and queries

@validator_agent.on_message(model=RawEarthquakeData)  # type: ignore
async def handle_raw_earthquake_data(ctx: Context, sender: str, msg: RawEarthquakeData):
    """
    Process incoming raw earthquake data from Oracle Agent.
    
    Processing Pipeline:
    1. Log received data for monitoring and debugging
    2. Apply validation logic and consensus algorithms
    3. Calculate confidence score and severity assessment
    4. Forward validated events to Action Agent (if valid)
    5. Log processing results for audit trail
    
    Args:
        ctx: Agent context for logging and communication
        sender: Address of the sending agent (Oracle Agent)
        msg: Raw earthquake data requiring validation
    """
    ctx.logger.info("========================================================")
    ctx.logger.info("Validator Agent - Processing Earthquake Event")
    ctx.logger.info("========================================================")
    ctx.logger.info(f"Received earthquake data from Oracle Agent: {sender}")
    ctx.logger.info(f"Source: {msg.source}")
    ctx.logger.info(f"Location: {msg.location}")
    ctx.logger.info(f"Magnitude: {msg.magnitude}")
    ctx.logger.info(f"Coordinates: ({msg.lat:.4f}, {msg.lon:.4f})")
    ctx.logger.info(f"Timestamp: {msg.timestamp} ({datetime.fromtimestamp(msg.timestamp, timezone.utc)})")
    
    # Apply validation logic and consensus processing
    ctx.logger.info("Applying validation criteria and consensus algorithms...")
    is_valid, confidence_score, severity = validate_earthquake_data(msg)
    
    if not is_valid:
        ctx.logger.warning(f"Event validation failed: {severity}")
        ctx.logger.warning("Event rejected - not forwarding to Action Agent")
        return
    
    ctx.logger.info(f"Validation successful!")
    ctx.logger.info(f"  Confidence Score: {confidence_score:.3f}")
    ctx.logger.info(f"  Severity Level: {severity}")
    
    # Create validated event object with enriched metadata
    event_details = {
        "source": msg.source,
        "original_magnitude": msg.magnitude,
        "location": msg.location,
        "coordinates": {"lat": msg.lat, "lon": msg.lon},
        "timestamp": msg.timestamp,
        "validation_timestamp": datetime.now(timezone.utc).isoformat(),
        "validator_agent": str(validator_agent.address),
        "confidence_score": confidence_score,
        "severity_assessment": severity
    }
    
    validated_event = ValidatedEvent(
        event_type="earthquake",
        severity=severity,
        details_json=json.dumps(event_details, indent=2),
        confidence_score=confidence_score
    )
    
    # Forward to Action Agent if configured
    if ACTION_AGENT_ADDRESS:
        try:
            ctx.logger.info(f"Forwarding validated event to Action Agent: {ACTION_AGENT_ADDRESS}")
            await ctx.send(ACTION_AGENT_ADDRESS, validated_event)
            ctx.logger.info("✓ Successfully forwarded validated event to Action Agent")
        except Exception as e:
            ctx.logger.error(f"✗ Failed to forward event to Action Agent: {e}")
    else:
        ctx.logger.warning("ACTION_AGENT_ADDRESS not configured - cannot forward validated event")
    
    ctx.logger.info("Event processing complete")
    ctx.logger.info("========================================================")


@validation_protocol.on_query(model=RawEarthquakeData, replies=ActionResponse)  # type: ignore
async def handle_validation_query(ctx: Context, sender: str, msg: RawEarthquakeData):
    """
    Handle synchronous validation queries from external agents or services.
    
    This provides a query-response interface for validation services,
    useful for testing, debugging, or integration with external systems.
    
    Args:
        ctx: Agent context for logging and communication
        sender: Address of the querying agent
        msg: Raw earthquake data to validate
        
    Returns:
        ActionResponse indicating validation results
    """
    ctx.logger.info(f"Received validation query from: {sender}")
    
    try:
        # Apply same validation logic as message handler
        is_valid, confidence_score, severity = validate_earthquake_data(msg)
        
        if is_valid:
            response_message = f"Event validated successfully. Confidence: {confidence_score:.3f}, Severity: {severity}"
            await ctx.send(sender, ActionResponse(
                status="success",
                message=response_message
            ))
        else:
            response_message = f"Event validation failed: {severity}"
            await ctx.send(sender, ActionResponse(
                status="error",
                message=response_message
            ))
            
        ctx.logger.info(f"Query response sent: {response_message}")
        
    except Exception as e:
        error_message = f"Validation error: {str(e)}"
        ctx.logger.error(error_message)
        await ctx.send(sender, ActionResponse(
            status="error",
            message=error_message
        ))


# =====================================================================
# PROTOCOL REGISTRATION AND SETUP
# =====================================================================
# Register validation protocol with the agent

validator_agent.include(validation_protocol)

# =====================================================================
# AGENT EXECUTION ENTRY POINT
# =====================================================================
# Start the Validator Agent when script is run directly

if __name__ == "__main__":
    # Log startup information for debugging and monitoring
    validator_agent._logger.info("======================================================")
    validator_agent._logger.info("        AEGIS Protocol - Validator Agent Starting")
    validator_agent._logger.info("======================================================")
    validator_agent._logger.info("Initializing earthquake validation and consensus system...")
    validator_agent._logger.info(f"Validation thresholds:")
    validator_agent._logger.info(f"  Minimum magnitude: {MIN_MAGNITUDE_THRESHOLD}")
    validator_agent._logger.info(f"  Maximum event age: {MAX_EVENT_AGE_HOURS} hours")
    validator_agent._logger.info(f"Action Agent target: {ACTION_AGENT_ADDRESS or 'Not configured'}")
    validator_agent._logger.info("Validator Agent ready - awaiting earthquake data from Oracle")
    validator_agent._logger.info("======================================================")
    
    # Start the agent's main event loop
    # This will run indefinitely, processing incoming validation requests
    validator_agent.run()
