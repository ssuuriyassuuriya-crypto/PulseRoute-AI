"""
PulseRoute AI - Reports Schemas
"""
from pydantic import BaseModel
from typing import List

class SessionReport(BaseModel):
    session_id: str
    timestamp: str
    total_vehicles_processed: int
    avg_wait_time_reduction_pct: float
    total_emergency_corridors_opened: int
    ambulance_delay_saved_minutes: float
    junction_efficiency_score: float
