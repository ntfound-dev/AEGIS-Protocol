import os
import json
import asyncio
from typing import Any, Dict
import aiofiles # type: ignore

from uagents import Agent, Context, Model # type: ignore
from uagents.setup import fund_agent_if_low # type: ignore

# Pustaka untuk interaksi dengan Internet Computer
from ic.agent import Agent as ICAgent # type: ignore
from ic.client import Client # type: ignore
from ic.identity import Identity # type: ignore
from ic import candid # type: ignore

# --- KONFIGURASI ---
ACTION_AGENT_SEED = os.getenv("ACTION_AGENT_SEED", "action_agent_secret_seed_phrase_placeholder")
ICP_URL = os.getenv("ICP_URL", "http://127.0.0.1:4943")
IDENTITY_PEM_PATH = "/app/identity.pem"
CANISTER_IDS_PATH = "/app/dfx-local/canister_ids.json"
EVENT_FACTORY_CANISTER_NAME = "event_factory"

# --- MODEL DATA ---
class ValidatedEvent(Model):
    event_type: str
    severity: str
    details_json: str
    confidence_score: float

# --- INISIALISASI AGENT ---
action_agent = Agent(
    name="action_agent_bridge",
    port=8003,
    seed=ACTION_AGENT_SEED,
    endpoint=[f"http://action-agent:8003/submit"],
)

fund_agent_if_low(str(action_agent.wallet.address()))
# REVISI: Mengembalikan ke ._logger untuk memperbaiki AttributeError
action_agent._logger.info(f"Action Agent berjalan dengan alamat: {action_agent.address}")

# REVISI: Menambahkan type hint untuk kejelasan
ic_state: Dict[str, Any] = {"agent": None, "factory_canister_id": None, "is_ready": False}

# --- FUNGSI INTERAKSI DENGAN BLOCKCHAIN (IC) ---

async def initialize_ic_agent(ctx: Context):
    """Fungsi startup untuk menginisialisasi koneksi ke IC."""
    ctx.logger.info("Memulai inisialisasi koneksi ke Internet Computer...")

    try:
        for _ in range(10):
            if os.path.isfile(CANISTER_IDS_PATH):
                break
            ctx.logger.info(f"Menunggu file canister ID di: {CANISTER_IDS_PATH}...")
            await asyncio.sleep(2)

        if not os.path.isfile(CANISTER_IDS_PATH):
            ctx.logger.critical(f"FATAL: File Canister ID tidak ditemukan: {CANISTER_IDS_PATH}")
            return

        async with aiofiles.open(CANISTER_IDS_PATH, "r") as f:
            canister_ids_json = await f.read()
        
        canister_ids = json.loads(canister_ids_json)
        canister_id = canister_ids.get(EVENT_FACTORY_CANISTER_NAME, {}).get("local")

        if not canister_id:
            ctx.logger.critical(f"FATAL: Canister '{EVENT_FACTORY_CANISTER_NAME}' tidak ditemukan di {CANISTER_IDS_PATH}")
            return
        ic_state["factory_canister_id"] = canister_id
    except Exception as e:
        ctx.logger.critical(f"FATAL: Gagal membaca file Canister ID. Error: {e}")
        return

    try:
        if not os.path.isfile(IDENTITY_PEM_PATH):
            ctx.logger.critical(f"FATAL: File identitas tidak ditemukan di {IDENTITY_PEM_PATH}.")
            return
            
        async with aiofiles.open(IDENTITY_PEM_PATH, "rb") as f:
            pem_content = await f.read()
        
        # REVISI: Menambahkan # type: ignore untuk mengatasi Pylance false positive
        identity = Identity.from_pem(pem_content) # type: ignore
    except Exception as e:
        ctx.logger.critical(f"FATAL: Gagal membaca atau mem-parsing identity.pem. Error: {e}")
        return

    client = Client(url=ICP_URL)
    ic_state["agent"] = ICAgent(identity=identity, client=client)
    ic_state["is_ready"] = True
    ctx.logger.info(f"SUKSES: Koneksi ke IC berhasil. Siap mengirim pesan ke canister '{ic_state['factory_canister_id']}'.")

async def call_icp_declare_event(ctx: Context, event: ValidatedEvent):
    """Memanggil fungsi 'declare_event' di canister IC."""
    if not ic_state["is_ready"]:
        ctx.logger.error("Koneksi ke IC belum siap. Panggilan ke canister dibatalkan.")
        return None
    
    try:
        ctx.logger.info(f"Mempersiapkan panggilan 'declare_event' ke canister {ic_state['factory_canister_id']}...")
        
        arg_payload = {
            "event_type": event.event_type,
            "severity": event.severity,
            "details_json": event.details_json,
        }
        
        encoded_arg = await asyncio.to_thread(candid.encode, [arg_payload])

        response = await asyncio.to_thread(
            ic_state["agent"].update_raw,
            ic_state["factory_canister_id"],
            "declare_event",
            encoded_arg
        )
        
        result = await asyncio.to_thread(candid.decode, response)
        ctx.logger.info(f"SUKSES: Panggilan canister berhasil. Hasil: {result}")
        return result
    except Exception as e:
        ctx.logger.error(f"FATAL: Terjadi error saat memanggil canister: {e}", exc_info=True)
        return None

# --- EVENT HANDLERS ---

# Daftarkan handler startup — kompatibel jika framework menyimpan hooks sebagai callable atau list
try:
    if callable(getattr(action_agent, "_on_startup", None)):
        action_agent._on_startup(initialize_ic_agent)  # type: ignore
        action_agent._logger.info("initialize_ic_agent didaftarkan via callable _on_startup().")
    else:
        hooks = getattr(action_agent, "_on_startup", None)
        if isinstance(hooks, list):
            hooks.append(initialize_ic_agent)
            action_agent._logger.info("initialize_ic_agent ditambahkan ke list _on_startup hooks.")
        else:
            action_agent._logger.warning("_on_startup tidak callable atau list; melewatkan pendaftaran otomatis.")
except Exception as e:
    action_agent._logger.error(f"Gagal mendaftar initialize_ic_agent: {e}", exc_info=True)

@action_agent.on_message(model=ValidatedEvent) # type: ignore
async def handle_validated_event(ctx: Context, sender: str, msg: ValidatedEvent):
    ctx.logger.info(f"Menerima event tervalidasi dari {sender}. Menjembatani ke IC...")
    await call_icp_declare_event(ctx, msg)

if __name__ == "__main__":
    action_agent.run()
