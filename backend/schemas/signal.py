"""
PulseRoute AI - Signal Schemas
"""
from pydantic import BaseModel
from typing import Dict

class SignalState(BaseModel):
    junction_id: str
    active_green_lane: str
    lane_signals: Dict[str, str] # e.g. {"NORTH": "GREEN", "SOUTH": "RED", ...}
    remaining_seconds: int
    is_emergency_locked: bool = False
    locked_lane: str = ""
