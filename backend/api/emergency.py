"""
PulseRoute AI - Emergency Dispatch & Green Corridor API Endpoints
"""
from fastapi import APIRouter
from backend.schemas.mission import StartMissionRequest
from backend.services.emergency_service import emergency_service
from backend.services.simulation_service import simulation_service
from backend.state.state_manager import state_manager

router = APIRouter(prefix="/api/emergency", tags=["Emergency"])

@router.post("/start")
def start_emergency(req: StartMissionRequest):
    mission = emergency_service.start_emergency_mission(
        driver_id=req.driver_id,
        vehicle_plate=req.vehicle_plate,
        start_j=req.start_junction_id,
        dest_j=req.destination_junction_id
    )
    simulation_service.start_simulation()
    return mission

@router.post("/stop")
def stop_emergency():
    simulation_service.stop_simulation()
    emergency_service.stop_emergency_mission("Manually ended by driver/admin")
    return {"message": "Emergency mission ended successfully"}

@router.get("/status")
def get_emergency_status():
    snapshot = state_manager.get_full_snapshot()
    return {
        "system_state": snapshot["system_state"],
        "mission": snapshot["active_mission"],
        "ambulance_gps": snapshot["ambulance_gps"]
    }
