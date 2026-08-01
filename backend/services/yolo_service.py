"""
PulseRoute AI - YOLO Analytics & ByteTrack Vehicle Tracking Service
"""
import random
from typing import Dict, List, Any
from backend.schemas.vehicle import VehicleDetection, LaneCount

class YoloService:
    def __init__(self):
        self.model_loaded = False
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")
            self.model_loaded = True
        except Exception:
            self.model_loaded = False

    def process_frame_simulation(self, junction_id: str) -> Dict[str, Any]:
        """
        Simulates frame analysis and ByteTrack unique vehicle tracking mapping to 4 regions (NORTH, SOUTH, EAST, WEST).
        """
        # Base realistic counts with minor random fluctuation for live demo
        base_counts = {
            "J1_BEGUMPET": {"NORTH": 14, "SOUTH": 9, "EAST": 24, "WEST": 16},
            "J2_PANJAGUTTA": {"NORTH": 19, "SOUTH": 28, "EAST": 15, "WEST": 11},
            "J3_BANJARA_HILLS": {"NORTH": 6, "SOUTH": 12, "EAST": 9, "WEST": 7}
        }
        
        target = base_counts.get(junction_id, {"NORTH": 10, "SOUTH": 10, "EAST": 10, "WEST": 10})
        
        # Add live fluctuation
        counts = {
            lane: max(0, val + random.randint(-2, 3))
            for lane, val in target.items()
        }
        
        detections = []
        track_id = 101
        for region, count in counts.items():
            for _ in range(min(count, 5)):
                detections.append({
                    "id": track_id,
                    "class_name": random.choice(["car", "car", "bus", "truck", "motorcycle"]),
                    "confidence": round(random.uniform(0.82, 0.98), 2),
                    "region": region
                })
                track_id += 1

        total = sum(counts.values())
        return {
            "junction_id": junction_id,
            "counts": counts,
            "total_vehicles": total,
            "detections": detections
        }

yolo_service = YoloService()
