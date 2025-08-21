# File: services/3-backend-ai-agents/agents/oracle_agent.py
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import json
import time

class RawEarthquakeData(Model):
    source: str
    magnitude: float
    location: str
    lat: float
    lon: float
    timestamp: int

class WebTriggerRequest(Model):
    source: str
    magnitude: float
    location: str
    lat: float
    lon: float
    timestamp: int

class WebTriggerResponse(Model):
    status: str
    message: str

VALIDATOR_SWARM_ADDRESS = "agent1qwzkf66hexgnx2e4qvyehqner79cm2sxreacrqeh47daglpqw4tygrjwynq"

oracle_agent = Agent(
    name="oracle_agent_beta",
    port=8001,
    seed="oracle_agent_beta_secret_seed_phrase_45678",
    endpoint=["http://oracle-agent:8001/submit"],
)

fund_agent_if_low(str(oracle_agent.wallet.address()))

def validate_earthquake_data(data: dict) -> bool:
    """Validasi data gempa bumi"""
    required_fields = ["source", "magnitude", "location", "lat", "lon", "timestamp"]
    
    for field in required_fields:
        if field not in data:
            return False
    
    # Validasi magnitude
    if not isinstance(data["magnitude"], (int, float)) or data["magnitude"] <= 0:
        return False
    
    # Validasi koordinat
    if not isinstance(data["lat"], (int, float)) or not isinstance(data["lon"], (int, float)):
        return False
    
    return True

@oracle_agent.on_message(model=RawEarthquakeData)
async def handle_agent_message(ctx: Context, sender: str, msg: RawEarthquakeData):
    ctx.logger.info(f"Received agent message from {sender}: {msg.location}")
    ctx.logger.info(f"Forwarding to Validator Agent...")
    await ctx.send(VALIDATOR_SWARM_ADDRESS, msg)

@oracle_agent.on_rest_post("/process_earthquake", WebTriggerRequest, WebTriggerResponse)
async def handle_web_request(ctx: Context, request: WebTriggerRequest):
    try:
        ctx.logger.info(f"Received web trigger with data: {request}")
        
        # Validasi data
        data_dict = {
            "source": request.source,
            "magnitude": request.magnitude,
            "location": request.location,
            "lat": request.lat,
            "lon": request.lon,
            "timestamp": request.timestamp
        }
        
        if not validate_earthquake_data(data_dict):
            return WebTriggerResponse(
                status="error",
                message="Invalid earthquake data format"
            )
        
        # Konversi ke RawEarthquakeData
        earthquake_data = RawEarthquakeData(**data_dict)
        
        # Kirim ke Validator Agent
        ctx.logger.info(f"Forwarding earthquake data to Validator Agent...")
        await ctx.send(VALIDATOR_SWARM_ADDRESS, earthquake_data)
        
        return WebTriggerResponse(
            status="success",
            message="Earthquake data received and forwarded to Validator Agent"
        )
        
    except Exception as e:
        ctx.logger.error(f"Error processing earthquake data: {e}")
        return WebTriggerResponse(
            status="error",
            message=f"Internal server error: {str(e)}"
        )

@oracle_agent.on_rest_get("/health")
async def health_check(ctx: Context):
    return {
        "status": "healthy",
        "agent": "oracle_agent_beta",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    print("🚀 Starting Oracle Agent on port 8001...")
    oracle_agent.run()