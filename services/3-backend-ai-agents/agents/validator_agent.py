# File: services/backend-ai-agents/agents/validator_agent.py
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import json

class WebTriggerRequest(Model):
    source: str; magnitude: float; location: str; lat: float; lon: float; timestamp: int

class WebTriggerResponse(Model):
    status: str; message: str

class RawEarthquakeData(Model):
    source: str; magnitude: float; location: str; lat: float; lon: float; timestamp: int

class ValidatedEvent(Model):
    event_type: str; severity: str; details_json: str; confidence_score: float

# Pastikan alamat ini sesuai dengan log dari action_agent Anda
ACTION_SWARM_ADDRESS = "agent1qwzkf66hexgnx2e4qvyehqner79cm2sxreacrqeh47daglpqw4tygrjwynq"

validator_agent = Agent(
    name="validator_agent_alpha",
    port=8002,
    seed="validator_agent_alpha_secret_seed_phrase_67890",
    endpoint=["http://validator-agent:8002/submit"],
)
fund_agent_if_low(str(validator_agent.wallet.address()))

def perform_ai_validation(data: RawEarthquakeData) -> ValidatedEvent:
    severity = "Critical" if data.magnitude >= 7.5 else "High" if data.magnitude >= 6.5 else "Low"
    details = {
        "location": data.location, "magnitude": data.magnitude, "lat": data.lat, "lon": data.lon,
        "potential_tsunami": "High" if data.magnitude >= 7.5 else "Low"
    }
    return ValidatedEvent(
        event_type="Earthquake", severity=severity,
        details_json=json.dumps(details), confidence_score=0.95
    )

@validator_agent.on_rest_post("/verify_disaster", WebTriggerRequest, WebTriggerResponse)
async def handle_web_request(ctx: Context, request: WebTriggerRequest):
    try:
        ctx.logger.info(f"Received web trigger: {request.location}")
        earthquake_data = RawEarthquakeData(
            source=request.source, magnitude=request.magnitude, location=request.location,
            lat=request.lat, lon=request.lon, timestamp=request.timestamp
        )
        validated_event = perform_ai_validation(earthquake_data)
        
        # --- PERBAIKAN PENTING: MENAMBAHKAN LOGIKA RETRY ---
        for attempt in range(5):
            try:
                ctx.logger.info(f"Attempt {attempt + 1}: Sending to Action Agent...")
                await ctx.send(ACTION_SWARM_ADDRESS, validated_event)
                ctx.logger.info("Successfully sent message to Action Agent!")
                return WebTriggerResponse(status="success", message="Signal processed and forwarded to action agent!")
            except Exception as e:
                ctx.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in 2s...")
                await ctx.sleep(2.0)
        
        ctx.logger.error("Failed to send message after 5 attempts.")
        return WebTriggerResponse(status="error", message="Critical error: Could not contact action agent.")

    except Exception as e:
        ctx.logger.error(f"Error in web request handler: {e}")
        return WebTriggerResponse(status="error", message=str(e))

if __name__ == "__main__":
    validator_agent.run()