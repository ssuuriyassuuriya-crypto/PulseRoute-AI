from app.schemas.emergency import GpsData, MissionStatus
from app.services.map_service import MapService
from app.state.manager import StateManager


class GpsSimulationService:
    SPEED_KPH = 42.0

    def __init__(self, state: StateManager, map_service: MapService) -> None:
        self._state = state
        self._map = map_service

    def begin(self) -> GpsData:
        return self._write_position(0)

    def tick(self) -> GpsData | None:
        mission = self._state.get("mission")
        if mission.get("status") != MissionStatus.ACTIVE.value:
            return None
        gps = self._state.get("gps")
        next_index = min(gps["route_index"] + 1, len(self._map.route) - 1)
        return self._write_position(next_index)

    def _write_position(self, index: int) -> GpsData:
        point = self._map.route[index]
        upcoming = self._map.route[index + 1].junction if index < len(self._map.route) - 1 else None
        distance = round(self._map.remaining_distance(index), 1)
        eta_seconds = round(distance / (self.SPEED_KPH / 3.6))
        data = GpsData(
            latitude=point.latitude,
            longitude=point.longitude,
            speed_kph=self.SPEED_KPH,
            distance_meters=distance,
            eta_seconds=eta_seconds,
            current_junction=point.junction,
            upcoming_junction=upcoming,
            route_index=index,
        )
        self._state.update("gps", data.model_dump())
        return data
