import os
import json
import time
import asyncio
import re
from uagents import Agent, Context, Protocol, Model
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement, ChatMessage, TextContent, chat_protocol_spec,
    StartSessionContent, EndSessionContent
)
from functions import get_earthquakes, EarthquakeRequest
from datetime import datetime
from uuid import uuid4
from typing import Any, Dict

# === MODEL DATA (including merged validator models) ===
# These Model classes are small typed containers used by the uagents framework.
# Keep their definitions close to the top so they're easy to find when reviewing the module.
class StructuredOutputPrompt(Model): prompt: str; output_schema: Dict[str, Any]
class StructuredOutputResponse(Model): output: Dict[str, Any]
class ChatRequest(Model): message: str
class ChatResponse(Model): reply: str
class RawEarthquakeData(Model): source: str; magnitude: float; location: str; lat: float; lon: float; timestamp: int
class ValidatedEvent(Model): event_type: str; severity: str; details_json: str; confidence_score: float

# === CONFIGURATION ===
# Use environment variables for runtime configuration. Keep defaults sensible for local testing.
AI_AGENT_ADDRESS = os.getenv("AI_AGENT_ADDRESS", "agent1qtlpfshtlcxekgrfcpmv7m9zpajuwu7d5jfyachvpa4u3dkt6k0uwwp2lct")
VALIDATOR_AGENT_SEED = os.getenv("VALIDATOR_AGENT_SEED", "validator_agent_secret_seed_phrase_placeholder")
ACTION_AGENT_ADDRESS = os.getenv("ACTION_AGENT_ADDRESS")

# === AGENT INITIALIZATION ===
# The Agent instance provides the runtime for registering protocols and handlers.
agent = Agent(
    name="chatbot_validator_merged_agent",
    port=8004,
    seed=VALIDATOR_AGENT_SEED,
    endpoint=["http://validator-agent:8004/submit"]
)

# === CORE LOGIC FUNCTIONS ===
def perform_ai_validation(data: RawEarthquakeData) -> ValidatedEvent:
    """
    Determine severity and potential tsunami risk from raw earthquake data.

    - Inputs: RawEarthquakeData (source, magnitude, location, lat, lon, timestamp)
    - Returns: ValidatedEvent with a JSON-encoded `details_json` and a confidence score.

    NOTES / ASSUMPTIONS:
    - The function uses simple magnitude thresholds to decide severity.
    - This function intentionally returns a fixed confidence_score (0.95) as a placeholder.
    - Do NOT change logic here unless validation policy changes.
    """
    if data.magnitude >= 7.5: severity, potential_tsunami = "Critical", "High"
    elif data.magnitude >= 6.5: severity, potential_tsunami = "High", "Low"
    else: severity, potential_tsunami = "Medium", "Very Low"
    details: Dict[str, Any] = {
        "location": data.location, "magnitude": data.magnitude, "latitude": data.lat, 
        "longitude": data.lon, "potential_tsunami": potential_tsunami, "source": data.source,
    }
    return ValidatedEvent(event_type="Earthquake", severity=severity, details_json=json.dumps(details), confidence_score=0.95)


async def send_to_action_agent(ctx: Context, event: ValidatedEvent) -> bool:
    """Send validated event to a separate Action Agent.

    - Retries up to 3 times on failure with a small backoff.
    - Logs success / failure to the provided Context logger.

    Returns True on success, False on final failure.
    """
    if not ACTION_AGENT_ADDRESS:
        ctx.logger.error("Action Agent address not set. Message cannot be sent.")
        return False
    for attempt in range(3):
        try:
            await ctx.send(ACTION_AGENT_ADDRESS, event)
            ctx.logger.info(f"Validated event '{event.severity}' for '{json.loads(event.details_json)['location']}' sent to Action Agent!")
            return True
        except Exception as e:
            # WHY: retries help with transient network or peer issues.
            ctx.logger.warning(f"Attempt {attempt + 1} to send to Action Agent failed: {e}. Retrying...")
            await asyncio.sleep(2.0)
    ctx.logger.error("Failed to send message to Action Agent after multiple attempts.")
    return False


# === PROTOCOLS ===
# Keep protocol instances separate and clearly named for discoverability.
chat_proto = Protocol(spec=chat_protocol_spec)
struct_output_client_proto = Protocol(name="StructuredOutputClientProtocol", version="0.1.0")
http_protocol = Protocol("ChatbotHTTP")

# === MESSAGE HANDLERS ===
@agent.on_message(model=RawEarthquakeData)
async def handle_oracle_message(ctx: Context, sender: str, msg: RawEarthquakeData):
    """Handle raw earthquake data coming from oracles / data sources.

    - Validates with perform_ai_validation and forwards to Action Agent.
    - Keeps logic minimal: log, validate, forward.
    """
    ctx.logger.info(f"Received data from oracle {sender}: Location '{msg.location}', Mag {msg.magnitude}")
    validated_event = perform_ai_validation(msg)
    await send_to_action_agent(ctx, validated_event)


def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    """Create a ChatMessage containing a single text content item.

    - If `end_session` is True, append an EndSessionContent marker.
    - This helper centralizes message construction for consistency.
    """
    content = [TextContent(type="text", text=text)]
    if end_session: content.append(EndSessionContent(type="end-session"))
    return ChatMessage(timestamp=datetime.utcnow(), msg_id=uuid4(), content=content)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Chat protocol handler: receives ChatMessage, forwards structured prompt to AI agent.

    Behavior summary:
    - Save session <-> sender mapping in ctx.storage (used later to reply to the user).
    - Acknowledge the incoming message back to the sender.
    - For TextContent items: forward an EarthquakeRequest schema prompt to AI_AGENT_ADDRESS.

    IMPORTANT: This handler intentionally keeps logic simple and delegates complex parsing
    to the structured-output client (StructuredOutputResponse handler).
    """
    ctx.logger.info(f"Got a message from {sender}: {msg.content}")
    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id))
    for item in msg.content:
        if isinstance(item, StartSessionContent): continue
        elif isinstance(item, TextContent):
            # WHY: store sender again to ensure storage is populated for downstream handlers.
            ctx.storage.set(str(ctx.session), sender)
            await ctx.send(AI_AGENT_ADDRESS, StructuredOutputPrompt(prompt=item.text, output_schema=EarthquakeRequest.schema()))
        else: ctx.logger.info(f"Got unexpected content from {sender}")

# FINAL FIX: Re-added missing handler for ChatAcknowledgement
@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Log acknowledgements from peers. Keeps the system observable for deliverability.

    NOTE: No action is triggered on ack, but this handler prevents unhandled-message warnings.
    """
    ctx.logger.info(f"Got an acknowledgement from {sender} for message {msg.acknowledged_msg_id}")


@struct_output_client_proto.on_message(StructuredOutputResponse)
async def handle_structured_output_response(ctx: Context, sender: str, msg: StructuredOutputResponse):
    """Handle structured output returned by the AI model and reply to original session sender.

    Steps:
    1. Retrieve the session sender from storage.
    2. Validate the structured output (basic checks).
    3. Call get_earthquakes in a thread to avoid blocking the event loop.
    4. Send a ChatMessage back to the original sender containing the reply.

    Error handling:
    - If anything goes wrong, log and inform the user with a polite message.
    """
    session_sender = ctx.storage.get(str(ctx.session))
    if session_sender is None: return
    try:
        output = msg.output if isinstance(msg.output, dict) else {}
        location = output.get("location")
        if not location or "<UNKNOWN>" in str(output): raise ValueError("Location not found or unknown")
        radius_km = output.get("radius_km") or output.get("radius") or 200
        days = output.get("days") or 7
        # WHY: use asyncio.to_thread because get_earthquakes is synchronous and may be blocking.
        result = await asyncio.to_thread(get_earthquakes, location, int(radius_km), int(days))
    except Exception as err:
        ctx.logger.error(f"Error handling structured output: {err}")
        await ctx.send(session_sender, create_text_chat("Sorry, I couldn't process your request. Please try again later."))
        return
    reply = result.get("earthquakes") or f"No earthquake data for {location}."
    await ctx.send(session_sender, create_text_chat(reply))


@http_protocol.on_query(model=ChatRequest, replies=ChatResponse)
async def handle_http_chat(ctx: Context, sender: str, msg: ChatRequest):
    """Handle HTTP-based chat queries (lightweight frontend / webhook style).

    - Performs keyword detection for earthquake-related queries and extracts location.
    - Calls the same get_earthquakes helper and returns ChatResponse objects.
    """
    user_message = msg.message.lower().strip()
    if any(keyword in user_message for keyword in ["earthquake", "gempa", "quake", "seismic"]):
        # Patterns to help extract a location phrase from a user message in English / Indonesian.
        location_patterns = [
            r"earthquake(?:\s+(?:in|at|near))?\s+([a-zA-Z\s,]+?)(?:\s+magnitude|\s+mag|$)",
            r"gempa(?:\s+(?:di|pada))?\s+([a-zA-Z\s,]+?)(?:\s+magnitudo|\s+magnitude|$)",
            r"([a-zA-Z\s,]+?)(?:\s+earthquake|\s+gempa)"
        ]
        # Default to Indonesia if no explicit location is found.
        location = "Indonesia"
        for pattern in location_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match: location = match.group(1).strip(); break
        try:
            result = await asyncio.to_thread(get_earthquakes, location, 200, 7)
            reply = result.get("earthquakes", f"No data for {location}.")
            if "No earthquakes found" in reply: reply = f"🟢 Good news! No significant earthquakes found near {location} recently."
            elif "earthquakes" in reply.lower(): reply = f"🚨 {reply}"
            await ctx.send(sender, ChatResponse(reply=reply))
        except Exception:
            await ctx.send(sender, ChatResponse(reply=f"Sorry, I couldn't get earthquake data for {location}."))
    else:
        await ctx.send(sender, ChatResponse(reply="Hello! I'm the Aegis Assistant. I can get earthquake info. Try 'earthquake in Balikpapan'."))


# === AGENT REGISTRATION & RUN ===
# Include protocols in the agent's manifest — publish_manifest=True makes the agent's interface discoverable.
agent.include(chat_proto, publish_manifest=True)
agent.include(struct_output_client_proto, publish_manifest=True)
agent.include(http_protocol, publish_manifest=True)

if __name__ == "__main__":
    # Entrypoint for running the agent as a standalone process.
    agent.run()

