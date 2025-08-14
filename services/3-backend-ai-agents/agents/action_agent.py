# File: services/3-backend-ai-agents/agents/action_agent.py
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from ic.agent import Agent as ICAgent
from ic.client import Client
from ic.identity import Identity
from ic.candid import encode, decode
import os
from dotenv import load_dotenv

class ValidatedEvent(Model):
    event_type: str
    severity: str
    details_json: str
    confidence_score: float

load_dotenv()

ICP_URL = os.getenv("ICP_URL", "http://127.0.0.1:4943")
EVENT_FACTORY_CANISTER_ID = os.getenv("EVENT_FACTORY_CANISTER_ID")
IDENTITY_PEM_PATH = "./identity.pem"

action_agent = Agent(
    name="action_agent_bridge",
    port=8003,
    seed="action_agent_bridge_secret_seed_phrase_11223"
)

fund_agent_if_low(str(action_agent.wallet.address()))

def call_icp_declare_event(event: ValidatedEvent):
    if not EVENT_FACTORY_CANISTER_ID:
        print("Error: EVENT_FACTORY_CANISTER_ID is not set in .env file.")
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

        print(f"Calling 'declare_event' on canister {EVENT_FACTORY_CANISTER_ID}...")
        
        response = ic_agent.update_raw(
            canister_id=EVENT_FACTORY_CANISTER_ID,
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
        print("Please run 'scripts/generate-keys.sh' first.")
    else:
        action_agent.run()