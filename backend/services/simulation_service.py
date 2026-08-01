"""
PulseRoute AI - GPS Route Simulation Service
"""
import json
import os
import time
from backend.config.config import ROUTES_DIR
from backend.state.state_manager import state_manager

class SimulationService:
    def __init__(self):
        self.waypoints = []
        self.current_step = 0
        self.is_running = False
        self.load_route()

    def load_route(self):
        route_path = os.path.join(ROUTES_DIR, "city_route.json")
        if os.path.exists(route_path):
            with open(route_path, "r") as f:
                data = json.load(f)
                self.waypoints = data.get("waypoints", [])

    def start_simulation(self):
        self.current_step = 0
        self.is_running = True
        state_manager.ambulance_gps["is_active"] = True

    def stop_simulation(self):
        self.is_running = False
        state_manager.ambulance_gps["is_active"] = False

    def step(self):
        if not self.is_running or not self.waypoints:
            return
            
        total_steps = len(self.waypoints) - 1
        if self.current_step >= total_steps:
            # Reached hospital
            self.stop_simulation()
            from backend.services.emergency_service import emergency_service
            emergency_service.stop_emergency_mission("Arrived at Banjara Hills Hospital")
            return
            
        p1 = self.waypoints[self.current_step]
        p2 = self.waypoints[min(self.current_step + 1, total_steps)]
        
        # Interpolate location
        lat = p1["lat"] + (p2["lat"] - p1["lat"]) * 0.5
        lng = p1["lng"] + (p2["lng"] - p1["lng"]) * 0.5
        
        progress = round(((self.current_step + 1) / float(total_steps + 1)) * 100, 1)
        speed = 65.0
        dist_km = round((1.0 - (progress / 100.0)) * 5.4, 2)
        eta_sec = round((dist_km / speed) * 3600, 1)
        
        curr_j = p1.get("junction_id") or "J1_BEGUMPET"
        next_j = p2.get("junction_id") or "J2_PANJAGUTTA"
        
        state_manager.update_ambulance_gps(
            latitude=lat,
            longitude=lng,
            speed_kmh=speed,
            progress=progress,
            current_j=curr_j,
            next_j=next_j,
            dist_km=dist_km,
            eta_sec=eta_sec
        )
        
        self.current_step += 1

simulation_service = SimulationService()
