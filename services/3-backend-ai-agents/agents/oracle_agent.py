# File: services/3-backend-ai-agents/agents/action_agent.py
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from ic.agent import Agent as ICAgent
from ic.client import Client
from ic.identity import Identity
from ic.candid import encode, decode
import os
import json
import time # Import library 'time' untuk menunggu

class ValidatedEvent(Model):
    event_type: str
    severity: str
    details_json: str
    confidence_score: float

ICP_URL = os.getenv("ICP_URL", "http://dfx-replica:4943")
IDENTITY_PEM_PATH = "/app/identity.pem"
CANISTER_IDS_PATH = "/app/canister_ids.json"

# --- PERBAIKAN UTAMA: Fungsi ini sekarang lebih sabar ---
def get_canister_id(name: str) -> str:
    # Coba selama 30 detik untuk menunggu file dibuat
    timeout = 30 
    start_time = time.time()
    while not os.path.exists(CANISTER_IDS_PATH) or os.path.isdir(CANISTER_IDS_PATH):
        if time.time() - start_time > timeout:
            print(f"Error: Timed out waiting for {CANISTER_IDS_PATH} to be created.")
            return None
        print(f"Waiting for {CANISTER_IDS_PATH} to be created...")
        time.sleep(2) # Tunggu 2 detik sebelum mencoba lagi
    
    with open(CANISTER_IDS_PATH, "r") as f:
        data = json.load(f)
    
    canister_info = data.get(name)
    if not canister_info:
        print(f"Error: Canister '{name}' not found in canister_ids.json")
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
        return None

    try:
        identity = Identity.from_pem(open(IDENTITY_PEM_PATH, "r").read())
        client = Client(url=ICP_URL)
        ic_agent = ICAgent(identity=identity, client=client)
        
        arg = [{
            "event_type": event.event_type,
            "severity": event.severity,
            "details_json": event.details_json,
        }]
        
        encoded_arg = encode(arg)

        print(f"Calling 'declare_event' on canister {event_factory_canister_id}...")
        
        response = ic_agent.update_raw(
            canister_id=event_factory_canister_id,
            method_name="declare_event",
            arg=encoded_arg
        )
        
        result = decode(response)
        print(f"Successfully created Event DAO. Canister ID: {result[0]['Ok']}")
        return result
        
    except Exception as e:
        print(f"Error calling ICP canister: {e}")
        return None

@action_agent.on_message(model=ValidatedEvent)
async def handle_validated_event(ctx: Context, sender: str, msg: ValidatedEvent):
    ctx.logger.info(f"Consensus reached! Received validated event from {sender}.")
    ctx.logger.info(f"Details: {msg.details_json}")
    
    call_icp_declare_event(msg)

if __name__ == "__main__":
    if not os.path.exists(IDENTITY_PEM_PATH):
        print(f"Error: Identity file not found at {IDENTITY_PEM_PATH}")
    else:
        action_agent.run()