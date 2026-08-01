"""
PulseRoute AI - FastAPI Main Application & Unified WebSocket Server
"""
import asyncio
import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import auth, traffic, analytics, emergency
from backend.state.state_manager import state_manager
from backend.services.orchestration_service import orchestration_service
from backend.services.simulation_service import simulation_service
from backend.services.green_corridor_service import green_corridor_service
from backend.services.yolo_service import yolo_service
from backend.config.config import MEDIA_DIR
from backend.utils.video_generator import generate_demo_video

app = FastAPI(title="PulseRoute AI System (v3.0)", version="3.0.0")

# CORS middleware for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media directory for video playback
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Include Routers
app.include_router(auth.router)
app.include_router(traffic.router)
app.include_router(analytics.router)
app.include_router(emergency.router)

# Connection Manager for /ws/dashboard WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial full state snapshot
        await websocket.send_text(json.dumps({
            "type": "INITIAL_STATE",
            "data": state_manager.get_full_snapshot()
        }))
        
        while True:
            # Keep socket alive and receive incoming client commands if any
            data = await websocket.receive_text()
            # Can process client commands (e.g. ping)
            await websocket.send_text(json.dumps({"type": "PONG"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# Background Loop Task for Real-time Simulation & Broadcasts
async def background_system_loop():
    while True:
        try:
            # 1. Update vehicle detections & counts
            for j_id in list(state_manager.junctions_data.keys()):
                detection = yolo_service.process_frame_simulation(j_id)
                state_manager.update_junction_counts(j_id, detection["counts"])
                
            # 2. Step GPS simulation if active
            simulation_service.step()
            
            # 3. Check Green Corridor preemption
            green_corridor_service.check_and_apply_preemption()
            
            # 4. Step Orchestration tick
            orchestration_service.tick()
            
            # 5. Broadcast live state update to all WebSocket subscribers
            snapshot = state_manager.get_full_snapshot()
            await manager.broadcast({
                "type": "LATEST_UPDATE",
                "timestamp": asyncio.get_event_loop().time(),
                "data": snapshot
            })
        except Exception as e:
            print(f"Loop error: {e}")
            
        await asyncio.sleep(1.0) # Tick every 1 second

@app.on_event("startup")
async def startup_event():
    # Ensure demo video exists
    generate_demo_video()
    # Launch background loop
    asyncio.create_task(background_system_loop())

@app.get("/")
def read_root():
    return {
        "system": "PulseRoute AI System (v3.0)",
        "status": "OPERATIONAL",
        "state": state_manager.get_system_state()
    }
