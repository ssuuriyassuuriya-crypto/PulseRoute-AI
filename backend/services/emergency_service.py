"""
PulseRoute AI - Emergency Dispatch Service
"""
import time
from backend.state.state_manager import (
    state_manager,
    STATE_EMERGENCY_REQUESTED,
    STATE_MISSION_ACTIVE,
    STATE_GREEN_CORRIDOR_ACTIVE,
    STATE_HOSPITAL_REACHED,
    STATE_ADAPTIVE_SCHEDULING_RESTORED
)

class EmergencyService:
    def start_emergency_mission(self, driver_id: str, vehicle_plate: str, start_j: str, dest_j: str) -> dict:
        mission_id = f"EMS-{int(time.time())}"
        mission_data = {
            "mission_id": mission_id,
            "driver_id": driver_id,
            "vehicle_plate": vehicle_plate,
            "start_junction_id": start_j,
            "destination_junction_id": dest_j,
            "status": STATE_EMERGENCY_REQUESTED,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with state_manager.state_lock:
            state_manager.active_mission = mission_data
            
        state_manager.set_system_state(
            STATE_EMERGENCY_REQUESTED,
            f"Ambulance {vehicle_plate} requested green corridor route from {start_j} to {dest_j}"
        )
        
        # Trigger mission activation
        time.sleep(0.1)
        state_manager.set_system_state(STATE_MISSION_ACTIVE, "GPS tracker connected. Ambulance en-route.")
        
        return mission_data

    def stop_emergency_mission(self, reason: str = "Mission completed"):
        with state_manager.state_lock:
            state_manager.active_mission = None
            state_manager.ambulance_gps["is_active"] = False
            
            # Unlock all junctions
            for j_id in state_manager.junctions_data:
                state_manager.junctions_data[j_id]["is_locked"] = False
                
        state_manager.set_system_state(
            STATE_HOSPITAL_REACHED,
            f"Handoff completed ({reason}). Override locks released."
        )
        time.sleep(0.1)
        state_manager.set_system_state(
            STATE_ADAPTIVE_SCHEDULING_RESTORED,
            "Reverting junctions back to adaptive density scheduling (NORMAL)"
        )

emergency_service = EmergencyService()
