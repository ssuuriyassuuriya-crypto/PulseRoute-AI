from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.traffic import Road


class MissionStatus(StrEnum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    HOSPITAL = "HOSPITAL"
    COMPLETED = "COMPLETED"


class Priority(StrEnum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class StartMissionRequest(BaseModel):
    hospital: str = Field(default="PulseCare General Hospital", min_length=2, max_length=120)


class MissionData(BaseModel):
    mission_id: str
    driver: str
    hospital: str
    status: MissionStatus
    priority: Priority
    distance_meters: float = Field(ge=0)
    eta_seconds: int = Field(ge=0)


class GpsData(BaseModel):
    latitude: float
    longitude: float
    speed_kph: float
    distance_meters: float = Field(ge=0)
    eta_seconds: int = Field(ge=0)
    current_junction: str
    upcoming_junction: str | None = None
    route_index: int = Field(ge=0)


class CorridorJunction(BaseModel):
    junction: str
    road: Road
    status: str


class EmergencySnapshot(BaseModel):
    mission: MissionData | None = None
    gps: GpsData | None = None
    corridor: list[CorridorJunction] = Field(default_factory=list)
