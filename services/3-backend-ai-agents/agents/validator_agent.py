from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import json

# ======================================================
# BAGIAN 1: Definisi Model Data
# ======================================================
class WebTriggerRequest(Model):
    source: str; magnitude: float; location: str; lat: float; lon: float; timestamp: int

class WebTriggerResponse(Model):
    status: str; message: str

class RawEarthquakeData(Model):
    source: str; magnitude: float; location: str; lat: float; lon: float; timestamp: int

class ValidatedEvent(Model):
    event_type: str; severity: str; details_json: str; confidence_score: float

# Model baru untuk Chat Protocol
class ChatRequest(Model):
    message: str

class ChatResponse(Model):
    reply: str

# ======================================================
# BAGIAN 2: Konfigurasi Agen
# ======================================================
ACTION_SWARM_ADDRESS = "agent1qwzkf66hexgnx2e4qvyehqner79cm2sxreacrqeh47daglpqw4tygrjwynq"

validator_agent = Agent(
    name="validator_agent_alpha", 
    port=8002, 
    seed="validator_agent_alpha_secret_seed_phrase_67890",
    # Endpoint menggunakan localhost agar bisa diakses dari browser di host machine
    # (dengan asumsi port 8002 di-mapping di docker-compose)
    endpoint=["http://localhost:8002/submit"], 
)
fund_agent_if_low(str(validator_agent.wallet.address()))

# ======================================================
# BAGIAN 3: Logika Inti & Fungsi Helper
# ======================================================
def perform_ai_validation(data: RawEarthquakeData) -> ValidatedEvent:
    """Fungsi ini menerapkan logika bisnis untuk memvalidasi dan mengklasifikasi data."""
    severity = "Critical" if data.magnitude >= 7.5 else "High" if data.magnitude >= 6.5 else "Low"
    details = {
        "location": data.location, "magnitude": data.magnitude, "lat": data.lat, "lon": data.lon,
        "potential_tsunami": "High" if data.magnitude >= 7.5 else "Low"
    }
    return ValidatedEvent(
        event_type="Earthquake", 
        severity=severity,
        details_json=json.dumps(details), 
        confidence_score=0.95
    )

async def send_to_action_agent(ctx: Context, event: ValidatedEvent) -> bool:
    """Fungsi ini mengirim event yang sudah divalidasi ke Action Agent dengan mekanisme retry."""
    for attempt in range(3): # Coba 3 kali
        try:
            ctx.logger.info(f"Attempt {attempt + 1}: Sending validated event to Action Agent...")
            await ctx.send(ACTION_SWARM_ADDRESS, event)
            ctx.logger.info("Message sent successfully to Action Agent!")
            return True
        except Exception as e:
            ctx.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in 2s...")
            await ctx.sleep(2.0)
    ctx.logger.error("Failed to send message after multiple attempts.")
    return False

# ======================================================
# BAGIAN 4: Message & Endpoint Handlers
# ======================================================
@validator_agent.on_message(model=RawEarthquakeData)
async def handle_oracle_message(ctx: Context, sender: str, msg: RawEarthquakeData):
    """Menerima data dari Oracle Agent."""
    ctx.logger.info(f"Received data from oracle {sender.split('/')[-1]}: {msg.location}")
    validated_event = perform_ai_validation(msg)
    await send_to_action_agent(ctx, validated_event)

@validator_agent.on_rest_post("/verify_disaster", WebTriggerRequest, WebTriggerResponse)
async def handle_legacy_signal(ctx: Context, request: WebTriggerRequest):
    """Menerima sinyal darurat dari frontend model lama (jika masih ada)."""
    ctx.logger.info(f"Received LEGACY web trigger: {request.location}")
    earthquake_data = RawEarthquakeData(source=request.source, magnitude=request.magnitude, location=request.location, lat=request.lat, lon=request.lon, timestamp=request.timestamp)
    validated_event = perform_ai_validation(earthquake_data)
    
    success = await send_to_action_agent(ctx, validated_event)
    if success:
        return WebTriggerResponse(status="success", message="Signal processed and forwarded!")
    else:
        return WebTriggerResponse(status="error", message="Could not contact action agent.")

@validator_agent.on_rest_post("/chat", ChatRequest, ChatResponse)
async def handle_chat_request(ctx: Context, request: ChatRequest):
    """Endpoint utama untuk ChatProtocol dari frontend baru."""
    ctx.logger.info(f"Received chat message: '{request.message}'")
    user_message = request.message.lower()
    reply_text = f"Saya menerima pesan Anda: '{request.message}'. Namun, saya belum diprogram untuk memahaminya."

    # Logika Natural Language Processing (NLP) sederhana
    if "kirim sinyal" in user_message:
        try:
            # Contoh parsing sederhana: "kirim sinyal gempa haiti magnitudo 7.8"
            parts = user_message.split()
            location = parts[3]
            magnitude = float(parts[5])
            
            # Buat data dummy untuk info lain
            earthquake_data = RawEarthquakeData(
                source="Manual Chat Input", magnitude=magnitude, location=location.title(),
                lat=18.4, lon=-72.4, timestamp=int(time.time())
            )
            validated_event = perform_ai_validation(earthquake_data)
            success = await send_to_action_agent(ctx, validated_event)
            if success:
                reply_text = f"Sinyal darurat untuk {location.title()} telah divalidasi dan diteruskan ke blockchain untuk dieksekusi."
            else:
                reply_text = "Sinyal darurat terdeteksi, tetapi saya gagal menghubungi Action Agent."
        except (IndexError, ValueError):
            reply_text = "Format sinyal tidak dikenali. Coba: 'kirim sinyal gempa [lokasi] magnitudo [angka]'"

    elif "status" in user_message or "proposal" in user_message:
        reply_text = "Fungsi untuk memeriksa status DAO langsung dari chat sedang dalam pengembangan. Silakan gunakan tombol 'Lihat Proposal DAO' untuk saat ini."
    
    elif "halo" in user_message or "hai" in user_message:
        reply_text = "Halo! Saya Aegis Agent. Apa yang bisa saya bantu?"

    return ChatResponse(reply=reply_text)

# ======================================================
# BAGIAN 5: Menjalankan Agen
# ======================================================
if __name__ == "__main__":
    validator_agent.run()