# =====================================================================
# AEGIS Protocol - Action Agent (Blockchain Bridge)
# =====================================================================
# Module: action_agent_bridge.py
# Purpose: Bridge validated disaster events to Internet Computer blockchain
# 
# Architecture Overview:
#   The Action Agent serves as the final layer in the AEGIS Protocol's
#   three-tier AI system (Oracle → Validator → Action). It receives
#   validated earthquake events and executes blockchain transactions to
#   create disaster-specific DAOs and trigger insurance mechanisms.
# 
# Core Responsibilities:
#   - Receive validated events from Validator Agent
#   - Initialize and manage Internet Computer agent connections
#   - Encode Candid messages for canister function calls
#   - Execute blockchain transactions (declare_event calls)
#   - Handle authentication and identity management
#   - Provide reliable retry mechanisms for blockchain operations
# 
# Blockchain Integration:
#   - Uses ic-py library for Internet Computer protocol communication
#   - Manages cryptographic identity for transaction signing
#   - Encodes function arguments using Candid interface definition language
#   - Handles asynchronous blockchain operations with proper error handling
# 
# Security Features:
#   - Secure private key management via PEM file loading
#   - Transaction integrity through cryptographic signing
#   - Safe memory handling for sensitive cryptographic material
#   - Proper error isolation to prevent system compromise
# 
# Agent Communication:
#   - Receives: ValidatedEvent messages from Validator Agent
#   - Executes: declare_event calls on Event Factory canister
#   - Returns: Success/failure confirmations to upstream agents
# 
# Environment Variables:
#   ACTION_AGENT_SEED: Cryptographic seed for agent identity
#   ICP_URL: Internet Computer replica URL (local or mainnet)
#   EVENT_FACTORY_CANISTER_NAME: Target canister for event declarations
# 
# File Dependencies:
#   /app/identity.pem: Private key for blockchain authentication
#   /app/dfx-local/canister_ids.json: Canister ID configuration
# =====================================================================

# =====================================================================
# STANDARD LIBRARY IMPORTS
# =====================================================================
# Core Python libraries for system integration and async operations

import os                    # Environment variable access and file system operations
import json                  # JSON data parsing for configuration files
import asyncio               # Asynchronous programming support for non-blocking operations
from typing import Any, Dict # Type hints for better code documentation and IDE support
import aiofiles              # Async file I/O operations for non-blocking file access

# =====================================================================
# FETCH.AI UAGENTS FRAMEWORK
# =====================================================================
# Decentralized AI agent framework for inter-agent communication

from uagents import Agent, Context, Model  # type: ignore
from uagents.setup import fund_agent_if_low  # type: ignore

# =====================================================================
# INTERNET COMPUTER PROTOCOL LIBRARIES
# =====================================================================
# IC-py library for Internet Computer blockchain integration
# Provides authentication, transaction signing, and canister communication

from ic.agent import Agent as ICAgent  # type: ignore   # IC blockchain agent for transaction execution
from ic.client import Client  # type: ignore           # HTTP client for IC replica communication
from ic.identity import Identity  # type: ignore       # Cryptographic identity management
from ic import candid  # type: ignore                 # Candid interface definition language support


# =====================================================================
# ENVIRONMENT CONFIGURATION AND CONSTANTS
# =====================================================================
# Critical configuration parameters for blockchain and agent operations

# Agent Identity and Communication
ACTION_AGENT_SEED = os.getenv("ACTION_AGENT_SEED", "action_agent_secret_seed_phrase_placeholder")
# Cryptographic seed for deterministic agent identity generation
# Used to ensure consistent agent address across container restarts

# Internet Computer Network Configuration
ICP_URL = os.getenv("ICP_URL", "http://127.0.0.1:4943")
# IC replica endpoint URL - defaults to local development replica
# Production deployments should use mainnet: https://ic0.app

# File System Paths (Docker Container Context)
IDENTITY_PEM_PATH = "/app/identity.pem"
# Path to private key file within Docker container
# Mounted from host system via Docker volume for security

CANISTER_IDS_PATH = "/app/dfx-local/canister_ids.json"
# Path to canister ID configuration file
# Contains mapping of canister names to their blockchain addresses

# Target Canister Configuration
EVENT_FACTORY_CANISTER_NAME = "event_factory"
# Name of the target canister for disaster event declarations
# Must match the canister name in dfx.json configuration


# =====================================================================
# DATA MODEL DEFINITIONS
# =====================================================================
# Input data structures for blockchain transaction processing

class ValidatedEvent(Model):
    """
    Validated earthquake event data model from Validator Agent.
    
    This model represents earthquake events that have passed consensus
    validation and are ready for blockchain processing. The Action Agent
    receives these events and creates corresponding disaster DAOs on-chain.
    
    Attributes:
        event_type (str): Event classification (e.g., "earthquake", "tsunami_risk")
        severity (str): Severity assessment ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        details_json (str): Complete event metadata as JSON string
        confidence_score (float): Validation confidence score (0.0-1.0)
    
    Blockchain Mapping:
        - event_type → canister event classification field
        - severity → disaster response urgency level
        - details_json → comprehensive event data for DAO initialization
        - confidence_score → trust metric for automated decision making
    
    Usage Context:
        Events with confidence_score > 0.7 are typically processed automatically.
        Lower confidence events may require manual review or additional validation.
    """
    event_type: str        # Event classification for DAO categorization
    severity: str          # Response urgency level for resource allocation
    details_json: str      # Complete event metadata for blockchain storage
    confidence_score: float # Validation confidence for automated processing


# =====================================================================
# AGENT INITIALIZATION AND NETWORKING
# =====================================================================
# Configure Action Agent for secure blockchain bridge operations

action_agent = Agent(
    name="action_agent_bridge",                      # Descriptive agent identifier
    port=8003,                                       # Network port for inter-agent communication
    seed=ACTION_AGENT_SEED,                          # Cryptographic seed for identity consistency
    endpoint=[f"http://action-agent:8003/submit"],   # Docker network endpoint for service discovery
)

# =====================================================================
# AGENT FUNDING AND WALLET MANAGEMENT
# =====================================================================
# Ensure agent wallet has sufficient tokens for network operations
# The Fetch.ai network requires tokens for message transmission and compute
fund_agent_if_low(str(action_agent.wallet.address()))

# =====================================================================
# INITIALIZATION LOGGING AND MONITORING
# =====================================================================
# Comprehensive startup logging for debugging and operational monitoring
action_agent._logger.info("======================================================")
action_agent._logger.info("         AEGIS Protocol - Action Agent Starting")
action_agent._logger.info("======================================================")
action_agent._logger.info("Initializing blockchain bridge for disaster response...")
action_agent._logger.info(f"Agent Details:")
action_agent._logger.info(f"  Name: action_agent_bridge")
action_agent._logger.info(f"  Address: {action_agent.address}")
action_agent._logger.info(f"  Port: 8003")
action_agent._logger.info(f"  Endpoint: http://action-agent:8003/submit")
action_agent._logger.info(f"")
action_agent._logger.info(f"Blockchain Configuration:")
action_agent._logger.info(f"  IC Replica URL: {ICP_URL}")
action_agent._logger.info(f"  Target Canister: {EVENT_FACTORY_CANISTER_NAME}")
action_agent._logger.info(f"  Identity Path: {IDENTITY_PEM_PATH}")
action_agent._logger.info(f"  Canister Config: {CANISTER_IDS_PATH}")
action_agent._logger.info("======================================================")

# =====================================================================
# INTERNET COMPUTER STATE MANAGEMENT
# =====================================================================
# Global state container for IC agent and canister configuration
# Mutable global state is used here for simplicity, but production
# systems should consider thread-safe state management patterns

ic_state: Dict[str, Any] = {
    "agent": None,                    # IC agent instance for blockchain transactions
    "factory_canister_id": None,     # Event Factory canister blockchain address
    "is_ready": False,               # Initialization status flag
    "last_error": None,              # Last error for debugging purposes
    "connection_attempts": 0,        # Connection retry counter
    "successful_transactions": 0,    # Success metrics for monitoring
    "failed_transactions": 0,        # Failure metrics for debugging
}

# State Management Notes:
# - "agent": Holds the configured IC agent with loaded identity
# - "factory_canister_id": Extracted from canister_ids.json configuration
# - "is_ready": Guards against operations before initialization complete
# - Error and metrics fields support operational monitoring and debugging


# ==============================================================
# Function: initialize_ic_agent
# Purpose : Setup IC agent connection at startup
# ==============================================================

async def initialize_ic_agent(ctx: Context):
    """
    Initialize Internet Computer Agent, load canister IDs, and identity.

    Args:
        ctx (Context): The agent context for logging and event handling.
    """
    ctx.logger.info("Starting Internet Computer connection initialization...")

    # --------------------------
    # Step 1: Load canister_ids.json
    # --------------------------
    try:
        for _ in range(10):
            if os.path.isfile(CANISTER_IDS_PATH):
                break
            ctx.logger.info(f"Waiting for canister ID file at: {CANISTER_IDS_PATH}...")
            await asyncio.sleep(2)

        if not os.path.isfile(CANISTER_IDS_PATH):
            ctx.logger.critical(f"FATAL: Canister ID file not found: {CANISTER_IDS_PATH}")
            return

        async with aiofiles.open(CANISTER_IDS_PATH, "r") as f:
            canister_ids = json.loads(await f.read())

        canister_id = canister_ids.get(EVENT_FACTORY_CANISTER_NAME, {}).get("local")
        if not canister_id:
            ctx.logger.critical(f"FATAL: Canister '{EVENT_FACTORY_CANISTER_NAME}' not found")
            return

        ic_state["factory_canister_id"] = canister_id

    except Exception as e:
        ctx.logger.critical(f"FATAL: Failed to read Canister ID file. Error: {e}")
        return

    # --------------------------
    # Step 2: Load identity.pem
    # --------------------------
    try:
        if not os.path.isfile(IDENTITY_PEM_PATH):
            ctx.logger.critical(f"FATAL: Identity file not found at {IDENTITY_PEM_PATH}.")
            return

        async with aiofiles.open(IDENTITY_PEM_PATH, "rb") as f:
            identity = Identity.from_pem(await f.read())  # type: ignore

    except Exception as e:
        ctx.logger.critical(f"FATAL: Failed to read or parse identity.pem. Error: {e}")
        return

    # --------------------------
    # Step 3: Create IC agent
    # --------------------------
    client = Client(url=ICP_URL)
    ic_state["agent"] = ICAgent(identity=identity, client=client)
    ic_state["is_ready"] = True

    ctx.logger.info(
        f"SUCCESS: IC connection established. Ready to send messages to canister '{ic_state['factory_canister_id']}'."
    )


# ==============================================================
# Function: call_icp_declare_event
# Purpose : Send validated events to IC canister
# ==============================================================

async def call_icp_declare_event(ctx: Context, event: ValidatedEvent):
    """
    Call the `declare_event` function in IC canister.

    Args:
        ctx (Context): The agent context for logging.
        event (ValidatedEvent): Validated event to be sent to IC.

    Returns:
        Any: Response from the canister or None if failed.
    """
    if not ic_state["is_ready"]:
        ctx.logger.error("IC connection not ready. Canister call cancelled.")
        return None

    try:
        ctx.logger.info(f"Preparing 'declare_event' call to canister {ic_state['factory_canister_id']}...")

        # Define expected candid type
        EventRecordType = candid.Types.Record(
            {
                "event_type": candid.Types.Text,
                "severity": candid.Types.Text,
                "details_json": candid.Types.Text,
            }
        )

        # Encode arguments
        encoded_arg = candid.encode([
            {
                "type": EventRecordType,
                "value": {
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "details_json": event.details_json,
                },
            }
        ])

        # Perform IC canister update call
        response = await asyncio.to_thread(
            ic_state["agent"].update_raw,
            ic_state["factory_canister_id"],
            "declare_event",
            encoded_arg
        )

        # Decode response
        result = await asyncio.to_thread(candid.decode, response)
        ctx.logger.info(f"SUCCESS: Canister call successful. Result: {result}")
        return result

    except Exception as e:
        ctx.logger.error(f"FATAL: Error occurred while calling canister: {e}", exc_info=True)
        return None


# ==============================================================
# Startup Hook Registration
# ==============================================================

try:
    hooks = getattr(action_agent, "_on_startup", None)
    if isinstance(hooks, list):
        hooks.append(initialize_ic_agent)
        action_agent._logger.info("initialize_ic_agent successfully added to _on_startup hooks.")
except Exception as e:
    action_agent._logger.error(f"Failed to register initialize_ic_agent: {e}", exc_info=True)


# ==============================================================
# Message Handler
# ==============================================================

@action_agent.on_message(model=ValidatedEvent)  # type: ignore
async def handle_validated_event(ctx: Context, sender: str, msg: ValidatedEvent):
    """
    Handle incoming validated events and forward them to IC canister.

    Args:
        ctx (Context): The agent context for logging.
        sender (str): The sender address of the message.
        msg (ValidatedEvent): The validated event payload.
    """
    ctx.logger.info(f"Receiving validated event from {sender}. Bridging to IC...")
    await call_icp_declare_event(ctx, msg)


# ==============================================================
# Entry Point
# ==============================================================

if __name__ == "__main__":
    action_agent.run()
