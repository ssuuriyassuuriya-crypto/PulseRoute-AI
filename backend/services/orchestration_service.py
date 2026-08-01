"""
PulseRoute AI - Adaptive Signal Orchestration Service
"""
from backend.state.state_manager import state_manager, STATE_NORMAL, STATE_GREEN_CORRIDOR_ACTIVE
from backend.services.analytics_service import analytics_service
from backend.constants.signals import SIGNAL_GREEN, SIGNAL_YELLOW, SIGNAL_RED

class OrchestrationService:
    def tick(self):
        """
        Executes standard adaptive signal timing loop updates unless junction is locked by Emergency Green Corridor.
        """
        snapshot = state_manager.get_full_snapshot()
        sys_state = snapshot["system_state"]
        junctions = snapshot["junctions"]
        
        for j_id, j_data in junctions.items():
            if j_data.get("is_locked", False):
                # Signal is locked by Green Corridor override
                continue
                
            rem = j_data["remaining_seconds"] - 1
            if rem <= 0:
                # Cycle complete, compute next green lane based on live counts
                analytics = analytics_service.compute_junction_analytics(j_id, j_data["name"], j_data["counts"])
                next_green = analytics["selected_green_lane"]
                duration = analytics["allocated_green_seconds"]
                state_manager.update_signal_phase(j_id, next_green, duration, False)
                state_manager.add_timeline_event(
                    "SIGNAL_SWITCH",
                    f"{j_data['name']}: Adaptive green phase set to {next_green} for {duration}s"
                )
            else:
                state_manager.update_signal_phase(j_id, j_data["active_green"], rem, False)

orchestration_service = OrchestrationService()
