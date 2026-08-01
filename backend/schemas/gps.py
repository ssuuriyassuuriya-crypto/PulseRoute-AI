"""
PulseRoute AI - GPS Schemas
"""
from pydantic import BaseModel
from typing import Optional

class GPSPoint(BaseModel):
    latitude: float
    longitude: float
    speed_kmh: float = 45.0
    heading: float = 0.0

class AmbulanceStatus(BaseModel):
    is_active: bool
    current_location: Optional[GPSPoint] = None
    destination_name: str = "Banjara Hills Hospital"
    current_junction_id: Optional[str] = None
    next_junction_id: Optional[str] = None
    distance_to_next_km: float = 0.0
    eta_seconds: float = 0.0
    progress_percentage: float = 0.0
