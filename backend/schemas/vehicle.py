"""
PulseRoute AI - Vehicle & Region Schemas
"""
from pydantic import BaseModel
from typing import List, Dict

class VehicleDetection(BaseModel):
    id: int
    class_name: str # car, bus, truck, motorcycle, ambulance
    confidence: float
    bbox: List[float] # [x1, y1, x2, y2]
    region: str # NORTH, SOUTH, EAST, WEST

class LaneCount(BaseModel):
    NORTH: int = 0
    SOUTH: int = 0
    EAST: int = 0
    WEST: int = 0
