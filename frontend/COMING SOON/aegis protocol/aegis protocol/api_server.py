# api_server.py
# FastAPI server untuk menghubungkan UI dengan Aegis Protocol

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

# Import Aegis components
from orchestrator import AegisOrchestrator
from asi_integration import ASIIntegrationLayer
from simulator import DisasterSimulator
from enhanced_main import EnhancedAegisSystem
from oracle_network import DecentralizedOracleNetwork
from parametric_vault import ParametricInsuranceVault
from performance_monitor import PerformanceMonitor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aegis.api")

# Pydantic models for API
class SimulationRequest(BaseModel):
    scenario: str

class InitializeRequest(BaseModel):
    asi_endpoint: Optional[str] = "https://asi-one.api"
    api_key: Optional[str] = "demo_key"

class EventUpdate(BaseModel):
    type: str
    data: Dict

# Global system instance
aegis_system: Optional[EnhancedAegisSystem] = None
connected_websockets: List[WebSocket] = []

# FastAPI app
app = FastAPI(
    title="🛡️ Aegis Protocol API", 
    description="AI-Powered Disaster Response System API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (your HTML dashboard)
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint - serves dashboard"""
    # In production, you'd serve the HTML file here
    return {"message": "Aegis Protocol API", "status": "online", "docs": "/docs"}

@app.get("/api/status")
async def get_status():
    """Get system status"""
    global aegis_system
    
    if not aegis_system:
        return {
            "status": "not_initialized",
            "system_status": "offline",
            "active_events": 0,
            "vault_balance": 10000000,
            "don_monitoring": False,
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Get status from orchestrator
        orchestrator_status = aegis_system.orchestrator.get_system_status()
        
        # Get DON status
        don_status = aegis_system.don.get_monitoring_status()
        
        # Get vault status
        vault_status = aegis_system.vault.get_vault_status()
        
        # Get performance stats
        perf_stats = aegis_system.performance_monitor.get_system_performance_stats()
        
        return {
            "status": "operational",
            "system_status": orchestrator_status.get("system_status", "unknown"),
            "active_events": orchestrator_status.get("active_events", 0),
            "vault_balance": vault_status.get("balance", 0),
            "don_monitoring": don_status.get("monitoring_active", False),
            "don_sources": don_status.get("active_sources", 0),
            "performance_stats": perf_stats,
            "uptime": orchestrator_status.get("uptime", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Status error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/initialize")
async def initialize_system(request: InitializeRequest):
    """Initialize Enhanced Aegis System"""
    global aegis_system
    
    try:
        logger.info("🚀 Initializing Enhanced Aegis System via API...")
        
        # Create enhanced system
        aegis_system = EnhancedAegisSystem()
        
        # Initialize with ASI connection
        await aegis_system.initialize_system()
        
        # Broadcast to WebSocket clients
        await broadcast_update({
            "type": "system_initialized",
            "message": "Enhanced Aegis System initialized successfully",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info("✅ System initialized successfully")
        
        return {
            "success": True,
            "message": "System initialized successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        await broadcast_update({
            "type": "error",
            "message": f"Initialization failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/don/start")
async def start_don():
    """Start DON monitoring"""
    global aegis_system
    
    if not aegis_system:
        raise HTTPException(status_code=400, detail="System not initialized")
    
    try:
        logger.info("📡 Starting DON monitoring...")
        
        # Start DON monitoring
        await aegis_system.don.start_monitoring()
        
        # Broadcast to WebSocket clients
        await broadcast_update({
            "type": "don_started",
            "message": "DON monitoring started",
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": "DON monitoring started",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"DON start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/don/stop")
async def stop_don():
    """Stop DON monitoring"""
    global aegis_system
    
    if not aegis_system:
        raise HTTPException(status_code=400, detail="System not initialized")
    
    try:
        await aegis_system.don.stop_monitoring()
        
        await broadcast_update({
            "type": "don_stopped",
            "message": "DON monitoring stopped",
            "timestamp": datetime.now().isoformat()
        })
        
        return {"success": True, "message": "DON monitoring stopped"}
        
    except Exception as e:
        logger.error(f"DON stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulate")
async def run_simulation(request: SimulationRequest):
    """Run disaster simulation"""
    global aegis_system
    
    if not aegis_system:
        raise HTTPException(status_code=400, detail="System not initialized")
    
    try:
        logger.info(f"🎯 Running simulation: {request.scenario}")
        
        # Start performance tracking
        start_time = time.time()
        
        # Run simulation using simulator
        result = await aegis_system.simulator.run_simulation(request.scenario)
        
        processing_time = time.time() - start_time
        
        # Broadcast real-time updates
        await broadcast_update({
            "type": "event_detected",
            "event_id": result.get("event_id"),
            "title": request.scenario.replace("_", " "),
            "disaster_type": aegis_system.simulator._get_disaster_type_from_scenario(request.scenario),
            "details": f"Simulation started - processing through AI pipeline",
            "timestamp": datetime.now().isoformat()
        })
        
        # Simulate pipeline updates
        pipeline_updates = [
            {"status": "parsing_complete", "delay": 0.5},
            {"status": "validation_started", "delay": 1.0},
            {"status": "consensus_reached", "delay": 1.5},
            {"status": "dao_created", "delay": 0.5},
            {"status": "notifications_sent", "delay": 0.3}
        ]
        
        for update in pipeline_updates:
            await asyncio.sleep(update["delay"])
            await broadcast_update({
                "type": "pipeline_update",
                "event_id": result.get("event_id"),
                "status": update["status"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Final result
        await broadcast_update({
            "type": "simulation_complete", 
            "event_id": result.get("event_id"),
            "scenario": request.scenario,
            "processing_time": processing_time,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "event_id": result.get("event_id"),
            "scenario": request.scenario,
            "processing_time_seconds": processing_time,
            "pipeline_status": result.get("pipeline_status"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        await broadcast_update({
            "type": "error",
            "message": f"Simulation failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stop")
async def stop_system():
    """Stop the entire system"""
    global aegis_system
    
    try:
        if aegis_system:
            await aegis_system.don.stop_monitoring()
            aegis_system = None
        
        await broadcast_update({
            "type": "system_stopped",
            "message": "Aegis system stopped gracefully",
            "timestamp": datetime.now().isoformat()
        })
        
        return {"success": True, "message": "System stopped gracefully"}
        
    except Exception as e:
        logger.error(f"System stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events")
async def get_events():
    """Get active events"""
    global aegis_system
    
    if not aegis_system:
        return {"events": []}
    
    try:
        # Get events from orchestrator
        events = []
        for event_id, event in aegis_system.orchestrator.active_events.items():
            pipeline_status = aegis_system.orchestrator.event_pipeline.get(event_id, "unknown")
            
            events.append({
                "event_id": event_id,
                "disaster_type": event.disaster_type.value,
                "location": event.location,
                "severity": event.severity.value,
                "confidence": event.confidence_score,
                "status": pipeline_status,
                "timestamp": event.timestamp.isoformat()
            })
        
        return {"events": events}
        
    except Exception as e:
        logger.error(f"Get events failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_performance_metrics():
    """Get performance metrics"""
    global aegis_system
    
    if not aegis_system:
        return {"metrics": {}}
    
    try:
        stats = aegis_system.performance_monitor.get_system_performance_stats()
        return {"metrics": stats}
        
    except Exception as e:
        logger.error(f"Get metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    try:
        # Send initial status
        status = await get_status()
        await websocket.send_json({
            "type": "status_update",
            "data": status
        })
        
        # Keep connection alive
        while True:
            # Send periodic heartbeat
            await asyncio.sleep(30)
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
        connected_websockets.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

async def broadcast_update(data: Dict):
    """Broadcast update to all connected WebSocket clients"""
    if not connected_websockets:
        return
    
    message = {
        "type": "update",
        "data": data
    }
    
    # Send to all connected clients
    disconnected = []
    for websocket in connected_websockets:
        try:
            await websocket.send_json(message)
        except:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        connected_websockets.remove(ws)

# Background task untuk DON monitoring updates
async def don_monitoring_task():
    """Background task untuk DON monitoring updates"""
    while True:
        await asyncio.sleep(10)  # Check every 10 seconds
        
        if aegis_system and aegis_system.don.monitoring_active:
            try:
                status = aegis_system.don.get_monitoring_status()
                await broadcast_update({
                    "type": "don_status",
                    "data": status,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"DON monitoring task error: {e}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info("🚀 Starting Aegis Protocol API Server")
    
    # Start background monitoring task
    asyncio.create_task(don_monitoring_task())
    
    logger.info("✅ API Server ready")
    logger.info("📊 Dashboard: http://localhost:8080")
    logger.info("📚 API Docs: http://localhost:8080/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks"""
    global aegis_system
    
    logger.info("🛑 Shutting down Aegis Protocol API Server")
    
    if aegis_system:
        try:
            await aegis_system.don.stop_monitoring()
        except:
            pass
    
    # Close all WebSocket connections
    for websocket in connected_websockets:
        try:
            await websocket.close()
        except:
            pass
    
    logger.info("✅ Shutdown complete")

if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
    