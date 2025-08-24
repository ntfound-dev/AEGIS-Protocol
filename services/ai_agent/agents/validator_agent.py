import os
import json
import time
import asyncio
from typing import Any, Dict

from uagents import Agent, Context, Model, Protocol # type: ignore
from uagents.setup import fund_agent_if_low # type: ignore

# --- DATA MODEL ---
class WebTriggerRequest(Model):
    source: str; magnitude: float; location: str; lat: float; lon: float; timestamp: int
class WebTriggerResponse(Model):
    status: str; message: str
class RawEarthquakeData(Model):
    source: str; magnitude: float; location: str; lat: float; lon: float; timestamp: int
class ValidatedEvent(Model):
    event_type: str; severity: str; details_json: str; confidence_score: float
class ChatRequest(Model):
    message: str
class ChatResponse(Model):
    reply: str

# --- CONFIGURATION ---
ACTION_AGENT_ADDRESS = os.getenv("ACTION_AGENT_ADDRESS")
VALIDATOR_AGENT_SEED = os.getenv("VALIDATOR_AGENT_SEED", "validator_agent_secret_seed_phrase_placeholder")

# --- AGENT INITIALIZATION ---
validator_agent = Agent(
    name="validator_agent_alpha",
    port=8002,
    seed=VALIDATOR_AGENT_SEED,
    endpoint=[f"http://validator-agent:8002/submit"],
)
fund_agent_if_low(str(validator_agent.wallet.address()))
# REVISION: Return to ._logger to fix AttributeError
validator_agent._logger.info(f"Validator Agent running with address: {validator_agent.address}")

# --- PROTOCOL FOR EXTERNAL INTERACTION ---
validator_protocol = Protocol("ValidatorAPI")

# --- CORE LOGIC FUNCTIONS ---
def perform_ai_validation(data: RawEarthquakeData) -> ValidatedEvent:
    """Simple validation logic based on magnitude."""
    if data.magnitude >= 7.5:
        severity = "Critical"
        potential_tsunami = "High"
    elif data.magnitude >= 6.5:
        severity = "High"
        potential_tsunami = "Low"
    else:
        severity = "Medium"
        potential_tsunami = "Very Low"
    
    details: Dict[str, Any] = {
        "location": data.location,
        "magnitude": data.magnitude,
        "latitude": data.lat,
        "longitude": data.lon,
        "potential_tsunami": potential_tsunami,
        "source": data.source,
    }
    return ValidatedEvent(
        event_type="Earthquake",
        severity=severity,
        details_json=json.dumps(details),
        confidence_score=0.95
    )

async def send_to_action_agent(ctx: Context, event: ValidatedEvent) -> bool:
    """Send event to action agent with retry mechanism."""
    if not ACTION_AGENT_ADDRESS:
        ctx.logger.error("Action Agent address not set. Message cannot be sent.")
        return False
    
    for attempt in range(3):
        try:
            ctx.logger.info(f"Attempt {attempt + 1}: Sending validated event to Action Agent...")
            await ctx.send(ACTION_AGENT_ADDRESS, event)
            ctx.logger.info("Message successfully sent to Action Agent!")
            return True
        except Exception as e:
            ctx.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in 2 seconds...")
            await asyncio.sleep(2.0)
            
    ctx.logger.error("Failed to send message to Action Agent after multiple attempts.")
    return False

# --- EVENT HANDLERS ---
@validator_agent.on_message(model=RawEarthquakeData) # type: ignore
async def handle_oracle_message(ctx: Context, sender: str, msg: RawEarthquakeData):
    ctx.logger.info(f"Receiving data from oracle {sender}: Location '{msg.location}'")
    validated_event = perform_ai_validation(msg)
    await send_to_action_agent(ctx, validated_event)

@validator_protocol.on_query(model=WebTriggerRequest, replies=WebTriggerResponse) # type: ignore
async def handle_legacy_signal(ctx: Context, sender: str, request: WebTriggerRequest):
    ctx.logger.info(f"Receiving LEGACY web trigger from {sender}: {request.location}")
    earthquake_data = RawEarthquakeData(**request.dict())
    validated_event = perform_ai_validation(earthquake_data)
    success = await send_to_action_agent(ctx, validated_event)
    
    if success:
        await ctx.send(sender, WebTriggerResponse(status="success", message="Signal processed and forwarded!"))
    else:
        await ctx.send(sender, WebTriggerResponse(status="error", message="Cannot contact action agent."))

@validator_protocol.on_query(model=ChatRequest, replies=ChatResponse) # type: ignore
async def handle_chat_request(ctx: Context, sender: str, request: ChatRequest):
    ctx.logger.info(f"Receiving chat message from {sender}: '{request.message}'")
    user_message = request.message.lower().strip()
    reply_text = f"I received your message: '{request.message}'. However, I'm not yet programmed to understand it."

    if "send signal" in user_message and "earthquake" in user_message and "magnitude" in user_message:
        try:
            parts = user_message.split()
            loc_index = parts.index("earthquake") + 1
            mag_index = parts.index("magnitude") + 1
            
            location = parts[loc_index].title()
            magnitude = float(parts[mag_index].replace(',', '.'))
            
            earthquake_data = RawEarthquakeData(
                source="Manual Chat Input",
                magnitude=magnitude,
                location=location,
                lat=0.0, lon=0.0,
                timestamp=int(time.time())
            )
            validated_event = perform_ai_validation(earthquake_data)
            success = await send_to_action_agent(ctx, validated_event)
            
            if success:
                reply_text = f"Emergency signal for {location} has been validated and forwarded."
            else:
                reply_text = "Emergency signal detected, but I failed to contact Action Agent."
        except (ValueError, IndexError):
            reply_text = "Signal format not recognized. Try: 'send signal earthquake [location] magnitude [number]'"
            
    elif "status" in user_message or "proposal" in user_message:
        reply_text = "Function to check DAO status directly from chat is under development."
    elif "hello" in user_message or "hi" in user_message:
        reply_text = "Hello! I'm Aegis Validator Agent. I'm ready to receive and validate data."
        
    await ctx.send(sender, ChatResponse(reply=reply_text))

validator_agent.include(validator_protocol)

if __name__ == "__main__":
    validator_agent.run()
