"""
PulseRoute AI - Green Corridor Preemption Controller
"""
import math
from backend.state.state_manager import state_manager, STATE_GREEN_CORRIDOR_ACTIVE

def haversine_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class GreenCorridorService:
    def check_and_apply_preemption(self):
        snapshot = state_manager.get_full_snapshot()
        sys_state = snapshot["system_state"]
        gps = snapshot["ambulance_gps"]
        
        if not gps["is_active"]:
            return
            
        amb_lat = gps["latitude"]
        amb_lng = gps["longitude"]
        
        junctions = snapshot["junctions"]
        
        # Determine upcoming junction based on proximity
        for j_id, j_data in junctions.items():
            j_lat = j_data["lat"]
            j_lng = j_data["lng"]
            dist_km = haversine_distance_km(amb_lat, amb_lng, j_lat, j_lng)
            
            # Preemption zone: lock green if within 1.5 km and approaching
            if dist_km <= 1.5 and dist_km > 0.05:
                if not j_data["is_locked"]:
                    # Determine corridor lane (e.g. SOUTH or EAST towards hospital)
                    corridor_lane = "SOUTH" if j_id == "J1_BEGUMPET" else ("EAST" if j_id == "J2_PANJAGUTTA" else "NORTH")
                    state_manager.update_signal_phase(j_id, corridor_lane, 90, True)
                    state_manager.set_system_state(
                        STATE_GREEN_CORRIDOR_ACTIVE,
                        f"Green Corridor lock activated at {j_data['name']} for approaching ambulance ({dist_km:.2f} km away)"
                    )
            elif dist_km <= 0.05:
                # Ambulance passing junction - release lock
                if j_data["is_locked"]:
                    state_manager.update_signal_phase(j_id, j_data["active_green"], 15, False)
                    state_manager.add_timeline_event(
                        "CORRIDOR_RELEASE",
                        f"Ambulance cleared {j_data['name']}. Green corridor lock released."
                    )

green_corridor_service = GreenCorridorService()
