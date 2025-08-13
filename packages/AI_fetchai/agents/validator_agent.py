# agents/validator_agent.py
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import json

class RawEarthquakeData(Model):
    source: str
    magnitude: float
    location: str
    lat: float
    lon: float
    timestamp: int

class ValidatedEvent(Model):
    event_type: str
    severity: str
    details_json: str
    confidence_score: float

ACTION_SWARM_ADDRESS = "agent1qwecgrj5g3k9qg5g3k9qg5g3k9qg5g3k9qg5g3k9qg5g3k9qg5g3k9qg"

validator_agent = Agent(
    name="validator_agent_alpha",
    port=8002,
    seed="validator_agent_alpha_secret_seed_phrase_67890"
)

# --- PERBAIKAN ---
# Menghapus baris yang salah dan memperbaiki panggilan fungsi
fund_agent_if_low(str(validator_agent.wallet.address()))

def perform_ai_validation(data: RawEarthquakeData) -> ValidatedEvent:
    severity = "Low"
    if data.magnitude >= 7.5:
        severity = "Critical"
    elif data.magnitude >= 6.5:
        severity = "High"
    
    details = {
        "location": data.location,
        "magnitude": data.magnitude,
        "lat": data.lat,
        "lon": data.lon,
        "potential_tsunami": "High" if data.magnitude >= 7.5 else "Low"
    }
    
    return ValidatedEvent(
        event_type="Earthquake",
        severity=severity,
        details_json=json.dumps(details),
        confidence_score=0.95,
    )

@validator_agent.on_message(model=RawEarthquakeData)
async def handle_raw_data(ctx: Context, sender: str, msg: RawEarthquakeData):
    ctx.logger.info(f"Received raw data from {sender}: {msg.location}")
    
    validated_event = perform_ai_validation(msg)
    
    ctx.logger.info(f"Validation complete. Broadcasting consensus call...")
    
    await ctx.send(ACTION_SWARM_ADDRESS, validated_event)

if __name__ == "__main__":
    validator_agent.run()
