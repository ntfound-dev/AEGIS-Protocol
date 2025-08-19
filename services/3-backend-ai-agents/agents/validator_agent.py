# File: services/3-backend-ai-agents/agents/validator_agent.py
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import json

# --- MODEL BARU UNTUK PERMINTAAN WEB ---
# Model ini mendefinisikan "amplop" untuk data yang datang dari Dasbor Demo
class WebTriggerRequest(Model):
    source: str
    magnitude: float
    location: str
    lat: float
    lon: float
    timestamp: int

# Model ini mendefinisikan "amplop balasan" yang akan dikirim kembali ke Dasbor Demo
class WebTriggerResponse(Model):
    status: str
    message: str

# (Model lain tidak berubah)
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

ACTION_SWARM_ADDRESS = "agent1qwzkf66hexgnx2e4qvyehqner79cm2sxreacrqeh47daglpqw4tygrjwynq"

validator_agent = Agent(
    name="validator_agent_alpha",
    port=8002,
    seed="validator_agent_alpha_secret_seed_phrase_67890", 
    # --- PERBAIKAN: Gunakan nama layanan Docker ---
    endpoint=["http://validator-agent:8002/submit"],
)

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

# Handler ini untuk komunikasi antar-agen (dari oracle_agent)
@validator_agent.on_message(model=RawEarthquakeData)
async def handle_agent_message(ctx: Context, sender: str, msg: RawEarthquakeData):
    ctx.logger.info(f"Received agent message from {sender}: {msg.location}")
    validated_event = perform_ai_validation(msg)
    ctx.logger.info(f"Validation complete. Broadcasting to Action Agent...")
    await ctx.send(ACTION_SWARM_ADDRESS, validated_event)

# --- FUNGSI BARU DENGAN DECORATOR YANG BENAR ---
# Ini adalah "pintu" baru kita untuk Dasbor Demo
@validator_agent.on_rest_post("/verify_disaster", WebTriggerRequest, WebTriggerResponse)
async def handle_web_request(ctx: Context, request: WebTriggerRequest):
    try:
        ctx.logger.info(f"Received web trigger with data: {request}")
        
        # Mengubah data dari model WebTriggerRequest menjadi RawEarthquakeData
        earthquake_data = RawEarthquakeData(
            source=request.source,
            magnitude=request.magnitude,
            location=request.location,
            lat=request.lat,
            lon=request.lon,
            timestamp=request.timestamp
        )

        # Panggil logika validasi yang sudah ada
        validated_event = perform_ai_validation(earthquake_data)
        ctx.logger.info(f"Validation complete. Broadcasting to Action Agent...")

        # Kirim hasilnya ke Action Agent
        await ctx.send(ACTION_SWARM_ADDRESS, validated_event)

        # Kirim balasan sukses ke halaman web
        return WebTriggerResponse(status="success", message="Signal received and processed!")

    except Exception as e:
        ctx.logger.error(f"Error processing web request: {e}")
        return WebTriggerResponse(status="error", message=str(e))


if __name__ == "__main__":
    validator_agent.run()