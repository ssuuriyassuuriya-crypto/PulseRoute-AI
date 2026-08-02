from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.traffic import Road


class SignalPhase(StrEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"


class SignalMode(StrEnum):
    ADAPTIVE = "ADAPTIVE"
    MANUAL = "MANUAL"
    EMERGENCY = "EMERGENCY"


class ManualOverrideRequest(BaseModel):
    road: Road
    duration_seconds: int = Field(default=30, ge=10, le=120)


class SignalSnapshot(BaseModel):
    mode: SignalMode
    phase: SignalPhase
    current_green: Road
    remaining_seconds: int = Field(ge=0)
    lights: dict[str, str]
    emergency_lock: bool = False
