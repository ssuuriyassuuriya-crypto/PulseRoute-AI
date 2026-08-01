"""
PulseRoute AI - Analytics Schemas
"""
from pydantic import BaseModel
from typing import Dict, List

class JunctionAnalytics(BaseModel):
    junction_id: str
    junction_name: str
    total_vehicles: int
    lane_counts: Dict[str, int]
    congestion_level: str
    queue_length_meters: float
    wait_time_index: float
    selected_green_lane: str
    allocated_green_seconds: int
    confidence_score: float
    reasoning: str
