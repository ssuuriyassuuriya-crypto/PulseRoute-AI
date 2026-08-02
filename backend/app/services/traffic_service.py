from collections import defaultdict
from itertools import cycle

from app.constants.traffic import (
    AVERAGE_VEHICLE_LENGTH_METERS,
    GREEN_SECONDS_BY_CONGESTION,
    LOW_CONGESTION_MAX_VEHICLES,
    MEDIUM_CONGESTION_MAX_VEHICLES,
)
from app.schemas.traffic import BoundingBox, Road, RoadMetrics, TrafficFrameRequest, TrafficProcessingResult, VehicleClass, VehicleObservation
from app.services.ai_decision_service import AIDecisionService
from app.state.manager import StateManager


class RegionMapper:
    """Assigns a normalized bounding-box center to exactly one approach road."""

    @staticmethod
    def map_observation(observation: VehicleObservation) -> Road:
        center_x = (observation.bbox.x1 + observation.bbox.x2) / 2
        center_y = (observation.bbox.y1 + observation.bbox.y2) / 2
        horizontal_offset = center_x - 0.5
        vertical_offset = center_y - 0.5
        if abs(horizontal_offset) >= abs(vertical_offset):
            return Road.EAST if horizontal_offset >= 0 else Road.WEST
        return Road.SOUTH if vertical_offset >= 0 else Road.NORTH


class TrafficService:
    def __init__(self, state: StateManager, decision_service: AIDecisionService) -> None:
        self._state = state
        self._decision_service = decision_service

    def process_frame(self, frame: TrafficFrameRequest) -> TrafficProcessingResult:
        road_observations: dict[Road, list[VehicleObservation]] = defaultdict(list)
        for observation in frame.observations:
            road_observations[RegionMapper.map_observation(observation)].append(observation)

        metrics: dict[str, RoadMetrics] = {}
        road_state: dict[str, dict[str, object]] = {}
        for road in Road:
            observations = road_observations[road]
            vehicle_count = len(observations)
            average_wait = round(
                sum(item.waiting_seconds for item in observations) / vehicle_count, 2
            ) if vehicle_count else 0.0
            queue_length = round(vehicle_count * AVERAGE_VEHICLE_LENGTH_METERS, 2)
            congestion = self._congestion_for(vehicle_count)
            density_score = round(vehicle_count + (queue_length * 0.25) + (average_wait * 0.2), 2)
            metric = RoadMetrics(
                road=road,
                vehicle_count=vehicle_count,
                queue_length_meters=queue_length,
                average_wait_seconds=average_wait,
                density_score=density_score,
                congestion=congestion,
                recommended_green_seconds=GREEN_SECONDS_BY_CONGESTION[congestion],
            )
            metrics[road.value] = metric
            road_state[road.value] = {
                "vehicles": [
                    {
                        "id": item.tracking_id,
                        "class": item.vehicle_class.value,
                        "confidence": item.confidence,
                        "waiting_seconds": item.waiting_seconds,
                    }
                    for item in observations
                ],
                "metrics": metric.model_dump(),
            }

        decision = self._decision_service.decide(metrics)
        self._state.update("roads", road_state)
        self._state.update("traffic_frame", {"observations": [item.model_dump() for item in frame.observations]})
        self._state.update("analytics", {"roads": {key: value.model_dump() for key, value in metrics.items()}})
        self._state.update("metrics", {"total_vehicles": len(frame.observations)})
        self._state.update("ai_decision", decision.model_dump())
        self._state.add_log(f"Traffic analytics updated: {len(frame.observations)} tracked vehicles processed")
        return TrafficProcessingResult(roads=metrics, decision=decision, observations=frame.observations)

    def generate_demo_frame(self) -> TrafficProcessingResult:
        """Produce a repeatable, high-congestion frame for an offline demo."""
        observations: list[VehicleObservation] = []
        classes = cycle(VehicleClass)
        for road, count, wait_seconds in ((Road.EAST, 38, 24), (Road.NORTH, 17, 12), (Road.WEST, 9, 5), (Road.SOUTH, 5, 2)):
            for index in range(count):
                bbox = self._demo_box(road, index)
                observations.append(VehicleObservation(
                    tracking_id=f"demo-{road.value.lower()}-{index + 1}",
                    vehicle_class=next(classes),
                    confidence=round(0.78 + ((index % 18) / 100), 2),
                    bbox=bbox,
                    waiting_seconds=wait_seconds,
                ))
        self._state.add_log("Demo traffic frame generated")
        return self.process_frame(TrafficFrameRequest(observations=observations))

    @staticmethod
    def _demo_box(road: Road, index: int) -> BoundingBox:
        lane_offset = (index % 10) * 0.035
        if road == Road.EAST:
            return BoundingBox(x1=0.78, y1=0.30 + lane_offset, x2=0.88, y2=0.34 + lane_offset)
        if road == Road.WEST:
            return BoundingBox(x1=0.12, y1=0.30 + lane_offset, x2=0.22, y2=0.34 + lane_offset)
        if road == Road.NORTH:
            return BoundingBox(x1=0.30 + lane_offset, y1=0.08, x2=0.34 + lane_offset, y2=0.18)
        return BoundingBox(x1=0.30 + lane_offset, y1=0.82, x2=0.34 + lane_offset, y2=0.92)

    @staticmethod
    def _congestion_for(vehicle_count: int) -> str:
        if vehicle_count <= LOW_CONGESTION_MAX_VEHICLES:
            return "LOW"
        if vehicle_count <= MEDIUM_CONGESTION_MAX_VEHICLES:
            return "MEDIUM"
        return "HIGH"
