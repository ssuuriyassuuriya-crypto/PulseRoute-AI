"""
PulseRoute AI - Mission Schemas
"""
from pydantic import BaseModel
from typing import Optional

class StartMissionRequest(BaseModel):
    driver_id: str = "driver"
    vehicle_plate: str = "TS-09-EMS-108"
    start_junction_id: str = "J1_BEGUMPET"
    destination_junction_id: str = "J3_BANJARA_HILLS"

class MissionResponse(BaseModel):
    mission_id: str
    status: str # EMERGENCY_REQUESTED, MISSION_ACTIVE, GREEN_CORRIDOR_ACTIVE, HOSPITAL_REACHED
    start_time: str
    driver_id: str
    vehicle_plate: str
