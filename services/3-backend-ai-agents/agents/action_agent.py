# File: services/3-backend-ai-agents/agents/action_agent.py

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from ic.agent import Agent as ICAgent
from ic.client import Client
from ic.identity import Identity
from ic.candid import encode, decode
import os
import json
import time

class ValidatedEvent(Model):
    event_type: str
    severity: str
    details_json: str
    confidence_score: float

# Alamat ini menunjuk ke dfx yang berjalan di WSL, bukan di container lain.
ICP_URL = "http://host.docker.internal:4943"

IDENTITY_PEM_PATH = "/app/identity.pem"

# Path ini sesuai dengan volume mount: ../../.dfx/local:/app/dfx-local
CANISTER_IDS_PATH = "/app/dfx-local/canister_ids.json"


def get_canister_id(name: str) -> str:
    timeout = 40  # Waktu tunggu sedikit lebih lama untuk keamanan
    start_time = time.time()
    while not os.path.exists(CANISTER_IDS_PATH):
        if time.time() - start_time > timeout:
            print(f"FATAL: Timed out. File {CANISTER_IDS_PATH} tidak ditemukan.")
            print("Pastikan volume di docker-compose.yml sudah benar dan 'dfx deploy' sudah dijalankan di WSL.")
            return None
        print(f"Menunggu file canister ID di: {CANISTER_IDS_PATH}...")
        time.sleep(2)
    
    print(f"File {CANISTER_IDS_PATH} ditemukan. Membaca canister ID...")
    with open(CANISTER_IDS_PATH, "r") as f:
        data = json.load(f)
    
    canister_info = data.get(name)
    if not canister_info or not canister_info.get("local"):
        print(f"FATAL: Canister dengan nama '{name}' tidak ditemukan di dalam {CANISTER_IDS_PATH}")
        return None
        
    return canister_info.get("local")


action_agent = Agent(
    name="action_agent_bridge",
    port=8003,
    seed="action_agent_bridge_secret_seed_phrase_11223",
    endpoint=["http://action-agent:8003/submit"],
)

fund_agent_if_low(str(action_agent.wallet.address()))

def call_icp_declare_event(event: ValidatedEvent):
    event_factory_canister_id = get_canister_id("event_factory")
    if not event_factory_canister_id:
        print("Gagal mendapatkan canister ID, proses dibatalkan.")
        return None

    try:
        print(f"Mempersiapkan pemanggilan ke canister {event_factory_canister_id} di {ICP_URL}...")
        identity = Identity.from_pem(open(IDENTITY_PEM_PATH, "r").read())
        client = Client(url=ICP_URL)
        ic_agent = ICAgent(identity=identity, client=client)
        
        arg = [{
            "event_type": event.event_type,
            "severity": event.severity,
            "details_json": event.details_json,
        }]
        
        print("Memanggil metode 'declare_event'...")
        response = ic_agent.update_raw(
            canister_id=event_factory_canister_id,
            method_name="declare_event",
            arg=encode(arg)
        )
        
        result = decode(response)
        print(f"SUKSES: Panggilan ke canister berhasil. Hasil: {result}")
        return result
        
    except Exception as e:
        print(f"FATAL: Terjadi error saat memanggil canister ICP: {e}")
        return None

@action_agent.on_message(model=ValidatedEvent)
async def handle_validated_event(ctx: Context, sender: str, msg: ValidatedEvent):
    ctx.logger.info(f"Menerima event yang sudah divalidasi dari {sender.split('/')[-1]}.")
    ctx.logger.info(f"Detail: {msg.details_json}")
    
    call_icp_declare_event(msg)

if __name__ == "__main__":
    if not os.path.exists(IDENTITY_PEM_PATH):
        print(f"FATAL: File identitas tidak ditemukan di {IDENTITY_PEM_PATH}. Periksa volume di docker-compose.yml.")
    else:
        action_agent.run()