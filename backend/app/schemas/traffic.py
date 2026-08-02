from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class Road(StrEnum):
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"


class VehicleClass(StrEnum):
    CAR = "car"
    BUS = "bus"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"


class BoundingBox(BaseModel):
    x1: float = Field(ge=0, le=1)
    y1: float = Field(ge=0, le=1)
    x2: float = Field(ge=0, le=1)
    y2: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_corners(self) -> "BoundingBox":
        if self.x1 >= self.x2 or self.y1 >= self.y2:
            raise ValueError("Bounding-box end coordinates must be greater than start coordinates")
        return self


class VehicleObservation(BaseModel):
    tracking_id: str = Field(min_length=1, max_length=64)
    vehicle_class: VehicleClass
    confidence: float = Field(ge=0, le=1)
    bbox: BoundingBox
    waiting_seconds: float = Field(default=0, ge=0, le=3600)


class TrafficFrameRequest(BaseModel):
    observations: list[VehicleObservation] = Field(default_factory=list, max_length=500)


class RoadMetrics(BaseModel):
    road: Road
    vehicle_count: int = Field(ge=0)
    queue_length_meters: float = Field(ge=0)
    average_wait_seconds: float = Field(ge=0)
    density_score: float = Field(ge=0)
    congestion: str
    recommended_green_seconds: int


class TrafficDecision(BaseModel):
    road: Road
    vehicles: int
    density: str
    score: float
    green_time: int
    confidence: int
    reason: str


class TrafficProcessingResult(BaseModel):
    roads: dict[str, RoadMetrics]
    decision: TrafficDecision
    observations: list[VehicleObservation]
