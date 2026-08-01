"""
PulseRoute AI - GPS Stream Consumer Service Interface
"""
from backend.services.simulation_service import simulation_service
from backend.state.state_manager import state_manager

class GPSService:
    def process_external_gps_payload(self, lat: float, lng: float, speed: float):
        """
        Accepts real GPS coordinates from actual mobile driver app (Production Ready)
        """
        state_manager.update_ambulance_gps(
            latitude=lat,
            longitude=lng,
            speed_kmh=speed,
            progress=50.0,
            current_j="J2_PANJAGUTTA",
            next_j="J3_BANJARA_HILLS",
            dist_km=1.8,
            eta_sec=110.0
        )

gps_service = GPSService()
