import os
import json
import time
import asyncio
from typing import Any, Dict

from uagents import Agent, Context, Model, Protocol # type: ignore
from uagents.setup import fund_agent_if_low # type: ignore

# --- MODEL DATA ---
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

# --- KONFIGURASI ---
ACTION_AGENT_ADDRESS = os.getenv("ACTION_AGENT_ADDRESS")
VALIDATOR_AGENT_SEED = os.getenv("VALIDATOR_AGENT_SEED", "validator_agent_secret_seed_phrase_placeholder")

# --- INISIALISASI AGENT ---
validator_agent = Agent(
    name="validator_agent_alpha",
    port=8002,
    seed=VALIDATOR_AGENT_SEED,
    endpoint=[f"http://validator-agent:8002/submit"],
)
fund_agent_if_low(str(validator_agent.wallet.address()))
# REVISI: Mengembalikan ke ._logger untuk memperbaiki AttributeError
validator_agent._logger.info(f"Validator Agent berjalan dengan alamat: {validator_agent.address}")

# --- PROTOKOL UNTUK INTERAKSI EKSTERNAL ---
validator_protocol = Protocol("ValidatorAPI")

# --- FUNGSI LOGIKA INTI ---
def perform_ai_validation(data: RawEarthquakeData) -> ValidatedEvent:
    """Logika validasi sederhana berdasarkan magnitudo."""
    if data.magnitude >= 7.5:
        severity = "Kritis"
        potential_tsunami = "Tinggi"
    elif data.magnitude >= 6.5:
        severity = "Tinggi"
        potential_tsunami = "Rendah"
    else:
        severity = "Sedang"
        potential_tsunami = "Sangat Rendah"
    
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
    """Mengirim event ke action agent dengan mekanisme retry."""
    if not ACTION_AGENT_ADDRESS:
        ctx.logger.error("Alamat Action Agent belum diatur. Pesan tidak dapat dikirim.")
        return False
    
    for attempt in range(3):
        try:
            ctx.logger.info(f"Percobaan {attempt + 1}: Mengirim event tervalidasi ke Action Agent...")
            await ctx.send(ACTION_AGENT_ADDRESS, event)
            ctx.logger.info("Pesan berhasil dikirim ke Action Agent!")
            return True
        except Exception as e:
            ctx.logger.warning(f"Percobaan {attempt + 1} gagal: {e}. Mencoba lagi dalam 2 detik...")
            await asyncio.sleep(2.0)
            
    ctx.logger.error("Gagal mengirim pesan ke Action Agent setelah beberapa kali percobaan.")
    return False

# --- EVENT HANDLERS ---
@validator_agent.on_message(model=RawEarthquakeData) # type: ignore
async def handle_oracle_message(ctx: Context, sender: str, msg: RawEarthquakeData):
    ctx.logger.info(f"Menerima data dari oracle {sender}: Lokasi '{msg.location}'")
    validated_event = perform_ai_validation(msg)
    await send_to_action_agent(ctx, validated_event)

@validator_protocol.on_query(model=WebTriggerRequest, replies=WebTriggerResponse) # type: ignore
async def handle_legacy_signal(ctx: Context, sender: str, request: WebTriggerRequest):
    ctx.logger.info(f"Menerima pemicu web LEGACY dari {sender}: {request.location}")
    earthquake_data = RawEarthquakeData(**request.dict())
    validated_event = perform_ai_validation(earthquake_data)
    success = await send_to_action_agent(ctx, validated_event)
    
    if success:
        await ctx.send(sender, WebTriggerResponse(status="sukses", message="Sinyal diproses dan diteruskan!"))
    else:
        await ctx.send(sender, WebTriggerResponse(status="error", message="Tidak dapat menghubungi action agent."))

@validator_protocol.on_query(model=ChatRequest, replies=ChatResponse) # type: ignore
async def handle_chat_request(ctx: Context, sender: str, request: ChatRequest):
    ctx.logger.info(f"Menerima pesan chat dari {sender}: '{request.message}'")
    user_message = request.message.lower().strip()
    reply_text = f"Saya menerima pesan Anda: '{request.message}'. Namun, saya belum diprogram untuk memahaminya."

    if "kirim sinyal" in user_message and "gempa" in user_message and "magnitudo" in user_message:
        try:
            parts = user_message.split()
            loc_index = parts.index("gempa") + 1
            mag_index = parts.index("magnitudo") + 1
            
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
                reply_text = f"Sinyal darurat untuk {location} telah divalidasi dan diteruskan."
            else:
                reply_text = "Sinyal darurat terdeteksi, tetapi saya gagal menghubungi Action Agent."
        except (ValueError, IndexError):
            reply_text = "Format sinyal tidak dikenali. Coba: 'kirim sinyal gempa [lokasi] magnitudo [angka]'"
            
    elif "status" in user_message or "proposal" in user_message:
        reply_text = "Fungsi untuk memeriksa status DAO langsung dari chat sedang dalam pengembangan."
    elif "halo" in user_message or "hai" in user_message:
        reply_text = "Halo! Saya Aegis Validator Agent. Saya siap menerima dan memvalidasi data."
        
    await ctx.send(sender, ChatResponse(reply=reply_text))

validator_agent.include(validator_protocol)

if __name__ == "__main__":
    validator_agent.run()
