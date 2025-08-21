# File: services/3-backend-ai-agents/agents/action_agent.py
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import json
import time
import os

class ValidatedEvent(Model):
    event_type: str
    severity: str
    details_json: str
    confidence_score: float

# Optional ICP integration - only if files exist
ICP_URL = os.getenv("ICP_URL", "http://dfx-replica:4943")
IDENTITY_PEM_PATH = "/app/identity.pem"
CANISTER_IDS_PATH = "/app/canister_ids.json"

def wait_for_canister_deployment(timeout_seconds: int = 300) -> bool:
    """Wait for canister deployment to complete with proper timeout"""
    print(f"Waiting for canister deployment (timeout: {timeout_seconds}s)...")
    
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        # Check if canister_ids.json exists and is not a directory
        if os.path.exists(CANISTER_IDS_PATH) and not os.path.isdir(CANISTER_IDS_PATH):
            try:
                # Verify the file is valid JSON and contains expected structure
                with open(CANISTER_IDS_PATH, "r") as f:
                    data = json.load(f)
                
                # Check if it contains at least one canister with local deployment
                for canister_name, canister_info in data.items():
                    if isinstance(canister_info, dict) and "local" in canister_info:
                        print(f"✅ Canister deployment detected! Found {canister_name}")
                        return True
                        
                print("📄 canister_ids.json exists but no local deployments found yet...")
                        
            except (json.JSONDecodeError, Exception) as e:
                print(f"📄 canister_ids.json exists but invalid: {e}")
        
        print(f"⏳ Waiting for canister deployment... ({int(time.time() - start_time)}s/{timeout_seconds}s)")
        time.sleep(5)  # Check every 5 seconds
    
    print("❌ Timeout waiting for canister deployment!")
    return False

def get_canister_id(name: str) -> str:
    """Get canister ID if available"""
    if not os.path.exists(CANISTER_IDS_PATH):
        print(f"Warning: {CANISTER_IDS_PATH} not found. ICP integration disabled.")
        return None
    
    try:
        with open(CANISTER_IDS_PATH, "r") as f:
            data = json.load(f)
        
        canister_info = data.get(name)
        if not canister_info:
            print(f"Warning: Canister '{name}' not found in canister_ids.json")
            return None
            
        return canister_info.get("local")
    except Exception as e:
        print(f"Warning: Error reading canister IDs: {e}")
        return None

def call_icp_declare_event(event: ValidatedEvent):
    """Call ICP blockchain if available"""
    event_factory_canister_id = get_canister_id("event_factory")
    if not event_factory_canister_id:
        print("ICP integration not available - skipping blockchain call")
        return None

    try:
        # Only import ICP modules if needed
        from ic.agent import Agent as ICAgent
        from ic.client import Client
        from ic.identity import Identity
        from ic.candid import encode, decode
        
        if not os.path.exists(IDENTITY_PEM_PATH):
            print(f"Warning: Identity file not found at {IDENTITY_PEM_PATH}")
            return None
            
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
        
    except ImportError:
        print("ICP modules not available - skipping blockchain call")
        return None
    except Exception as e:
        print(f"Error calling ICP canister: {e}")
        return None

action_agent = Agent(
    name="action_agent_bridge",
    port=8003,
    seed="action_agent_bridge_secret_seed_phrase_11223",
    endpoint=["http://action-agent:8003/submit"],
)

fund_agent_if_low(str(action_agent.wallet.address()))

@action_agent.on_message(model=ValidatedEvent)
async def handle_validated_event(ctx: Context, sender: str, msg: ValidatedEvent):
    ctx.logger.info(f"Consensus reached! Received validated event from {sender}.")
    ctx.logger.info(f"Event Type: {msg.event_type}")
    ctx.logger.info(f"Severity: {msg.severity}")
    ctx.logger.info(f"Details: {msg.details_json}")
    ctx.logger.info(f"Confidence: {msg.confidence_score}")
    
    # Try to call ICP blockchain
    result = call_icp_declare_event(msg)
    
    if result:
        ctx.logger.info("✅ Successfully processed event and saved to blockchain")
    else:
        ctx.logger.info("✅ Successfully processed event (blockchain integration not available)")

@action_agent.on_rest_get("/health")
async def health_check(ctx: Context):
    return {
        "status": "healthy",
        "agent": "action_agent_bridge",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    print("🚀 Starting Action Agent on port 8003...")
    
    # Wait for canister deployment before starting the agent
    if not wait_for_canister_deployment():
        print("⚠️  Starting agent without canister deployment - ICP integration will be disabled")
    
    action_agent.run()