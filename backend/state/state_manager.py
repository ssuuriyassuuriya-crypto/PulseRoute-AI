"""
PulseRoute AI - Thread-Safe Global State Manager Singleton
"""
import threading
import time
from typing import Dict, Any, List

STATE_NORMAL = "NORMAL"
STATE_EMERGENCY_REQUESTED = "EMERGENCY_REQUESTED"
STATE_MISSION_ACTIVE = "MISSION_ACTIVE"
STATE_GREEN_CORRIDOR_ACTIVE = "GREEN_CORRIDOR_ACTIVE"
STATE_HOSPITAL_REACHED = "HOSPITAL_REACHED"
STATE_ADAPTIVE_SCHEDULING_RESTORED = "ADAPTIVE_SCHEDULING_RESTORED"

class StateManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                cls._instance._init_state()
            return cls._instance

    def _init_state(self):
        self.state_lock = threading.RLock()
        self.system_state = STATE_NORMAL
        
        # Vehicle detection counts per lane for 3 junctions
        self.junctions_data = {
            "J1_BEGUMPET": {
                "name": "Begumpet Junction",
                "counts": {"NORTH": 12, "SOUTH": 8, "EAST": 22, "WEST": 15},
                "active_green": "EAST",
                "remaining_seconds": 25,
                "is_locked": False,
                "lat": 17.4447,
                "lng": 78.4664
            },
            "J2_PANJAGUTTA": {
                "name": "Panjagutta Circle",
                "counts": {"NORTH": 18, "SOUTH": 25, "EAST": 14, "WEST": 9},
                "active_green": "SOUTH",
                "remaining_seconds": 30,
                "is_locked": False,
                "lat": 17.4256,
                "lng": 78.4513
            },
            "J3_BANJARA_HILLS": {
                "name": "Banjara Hills Hospital Gate",
                "counts": {"NORTH": 5, "SOUTH": 10, "EAST": 8, "WEST": 6},
                "active_green": "NORTH",
                "remaining_seconds": 20,
                "is_locked": False,
                "lat": 17.4156,
                "lng": 78.4412
            }
        }
        
        # Active Mission & Ambulance state
        self.active_mission = None
        self.ambulance_gps = {
            "is_active": False,
            "latitude": 17.4447,
            "longitude": 78.4664,
            "speed_kmh": 0.0,
            "heading": 145.0,
            "current_junction_id": "J1_BEGUMPET",
            "next_junction_id": "J2_PANJAGUTTA",
            "distance_to_next_km": 2.1,
            "eta_seconds": 160.0,
            "progress_percentage": 0.0
        }
        
        self.timeline_events: List[Dict[str, Any]] = []
        self.add_timeline_event("SYSTEM", "PulseRoute AI State Manager Initialized (NORMAL)")

    def get_system_state(self) -> str:
        with self.state_lock:
            return self.system_state

    def set_system_state(self, new_state: str, details: str = ""):
        with self.state_lock:
            old_state = self.system_state
            self.system_state = new_state
            msg = f"State transition: {old_state} ➔ {new_state}"
            if details:
                msg += f" ({details})"
            self.add_timeline_event("STATE_CHANGE", msg)

    def add_timeline_event(self, category: str, message: str):
        with self.state_lock:
            event = {
                "timestamp": time.strftime("%H:%M:%S"),
                "category": category,
                "message": message
            }
            self.timeline_events.append(event)
            if len(self.timeline_events) > 100:
                self.timeline_events.pop(0)

    def update_junction_counts(self, junction_id: str, counts: Dict[str, int]):
        with self.state_lock:
            if junction_id in self.junctions_data:
                self.junctions_data[junction_id]["counts"] = counts

    def update_signal_phase(self, junction_id: str, green_lane: str, seconds: int, is_locked: bool = False):
        with self.state_lock:
            if junction_id in self.junctions_data:
                j = self.junctions_data[junction_id]
                j["active_green"] = green_lane
                j["remaining_seconds"] = seconds
                j["is_locked"] = is_locked

    def update_ambulance_gps(self, latitude: float, longitude: float, speed_kmh: float, progress: float, current_j: str, next_j: str, dist_km: float, eta_sec: float):
        with self.state_lock:
            self.ambulance_gps.update({
                "latitude": latitude,
                "longitude": longitude,
                "speed_kmh": speed_kmh,
                "progress_percentage": progress,
                "current_junction_id": current_j,
                "next_junction_id": next_j,
                "distance_to_next_km": dist_km,
                "eta_seconds": eta_sec
            })

    def get_full_snapshot(self) -> Dict[str, Any]:
        with self.state_lock:
            return {
                "system_state": self.system_state,
                "junctions": self.junctions_data,
                "active_mission": self.active_mission,
                "ambulance_gps": self.ambulance_gps,
                "timeline_events": self.timeline_events[-20:]
            }

state_manager = StateManager()
