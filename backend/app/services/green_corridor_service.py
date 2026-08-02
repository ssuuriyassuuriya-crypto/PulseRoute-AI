from app.schemas.emergency import CorridorJunction, GpsData
from app.services.signal_service import AdaptiveSignalService
from app.state.manager import StateManager


class GreenCorridorService:
    """Locks the next route junction green and releases it when the mission ends."""

    def __init__(self, state: StateManager, signals: AdaptiveSignalService) -> None:
        self._state = state
        self._signals = signals

    def update(self, gps: GpsData, route: list[object]) -> list[CorridorJunction]:
        corridor = [
            CorridorJunction(
                junction=point.junction,
                road=point.road,
                status="PASSED" if index < gps.route_index else "GREEN" if index == gps.route_index else "WAITING",
            )
            for index, point in enumerate(route)
        ]
        active = corridor[gps.route_index]
        current = self._state.get("green_corridor")
        if current.get("active_junction") != active.junction:
            self._signals.lock_for_emergency(active.road)
            self._state.add_log(f"Green corridor activated at {active.junction}", level="WARNING")
        self._state.update("green_corridor", {
            "active_junction": active.junction,
            "junctions": [item.model_dump() for item in corridor],
        })
        return corridor

    def release(self) -> None:
        current = self._state.get("green_corridor")
        if current.get("active_junction"):
            self._signals.release_emergency_lock()
            self._state.add_log("Green corridor released; adaptive signal mode restored")
        self._state.update("green_corridor", {"active_junction": None, "junctions": []})
