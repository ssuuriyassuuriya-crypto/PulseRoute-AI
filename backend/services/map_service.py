"""
PulseRoute AI - OpenStreetMap Coordinates & Junction Bounds Utility Service
"""
import os
import json
from backend.config.config import ROUTES_DIR

class MapService:
    def get_route_geometry(self, route_name: str = "city"):
        file_path = os.path.join(ROUTES_DIR, f"{route_name}_route.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return {"waypoints": []}

map_service = MapService()
