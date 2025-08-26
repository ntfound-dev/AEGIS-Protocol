# ==============================================================
# Module: action_agent_bridge.py
# Description:
#   Action Agent acts as a bridge between validated events (from Validator Agent)
#   and the Internet Computer (IC) canister system. It listens for incoming
#   validated events, initializes the IC agent connection, and forwards events
#   to the target canister using candid encoding.
# ==============================================================

import os
import json
import asyncio
from typing import Any, Dict
import aiofiles  # type: ignore

from uagents import Agent, Context, Model  # type: ignore
from uagents.setup import fund_agent_if_low  # type: ignore

from ic.agent import Agent as ICAgent  # type: ignore
from ic.client import Client  # type: ignore
from ic.identity import Identity  # type: ignore
from ic import candid  # type: ignore


# ==============================================================
# Environment & Constants
# ==============================================================

ACTION_AGENT_SEED = os.getenv("ACTION_AGENT_SEED", "action_agent_secret_seed_phrase_placeholder")
ICP_URL = os.getenv("ICP_URL", "http://127.0.0.1:4943")
IDENTITY_PEM_PATH = "/app/identity.pem"
CANISTER_IDS_PATH = "/app/dfx-local/canister_ids.json"
EVENT_FACTORY_CANISTER_NAME = "event_factory"


# ==============================================================
# Data Models
# ==============================================================

class ValidatedEvent(Model):
    """
    Schema for validated events received from Validator Agent.

    Attributes:
        event_type (str): Type/category of the event.
        severity (str): Severity level of the event (e.g., LOW, HIGH).
        details_json (str): JSON string containing event metadata.
        confidence_score (float): Confidence score assigned by Validator Agent.
    """
    event_type: str
    severity: str
    details_json: str
    confidence_score: float


# ==============================================================
# Agent Initialization
# ==============================================================

action_agent = Agent(
    name="action_agent_bridge",
    port=8003,
    seed=ACTION_AGENT_SEED,
    endpoint=[f"http://action-agent:8003/submit"],
)

# Fund agent wallet if needed
fund_agent_if_low(str(action_agent.wallet.address()))
action_agent._logger.info(f"Action Agent running with address: {action_agent.address}")

# Shared IC state (mutable global)
ic_state: Dict[str, Any] = {
    "agent": None,
    "factory_canister_id": None,
    "is_ready": False,
}


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
