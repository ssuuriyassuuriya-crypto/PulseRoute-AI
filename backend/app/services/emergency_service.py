from uuid import uuid4

from app.schemas.emergency import EmergencySnapshot, MissionData, MissionStatus, Priority, StartMissionRequest
from app.services.green_corridor_service import GreenCorridorService
from app.services.map_service import MapService
from app.services.simulation_service import GpsSimulationService
from app.state.manager import StateManager


class MissionStateError(Exception):
    """Raised for invalid mission lifecycle actions."""


class EmergencyService:
    def __init__(self, state: StateManager, gps: GpsSimulationService, corridor: GreenCorridorService, map_service: MapService) -> None:
        self._state = state
        self._gps = gps
        self._corridor = corridor
        self._map = map_service

    def start(self, driver: str, request: StartMissionRequest) -> EmergencySnapshot:
        if self._state.get("mission").get("status") == MissionStatus.ACTIVE.value:
            raise MissionStateError("An emergency mission is already active")
        gps = self._gps.begin()
        mission = MissionData(
            mission_id=f"EMS-{uuid4().hex[:8].upper()}",
            driver=driver,
            hospital=request.hospital,
            status=MissionStatus.ACTIVE,
            priority=Priority.NORMAL,
            distance_meters=gps.distance_meters,
            eta_seconds=gps.eta_seconds,
        )
        self._state.update("mission", mission.model_dump())
        corridor = self._corridor.update(gps, self._map.route)
        self._state.add_log(f"Emergency mission {mission.mission_id} started by {driver}", level="WARNING")
        return EmergencySnapshot(mission=mission, gps=gps, corridor=corridor)

    def tick(self) -> EmergencySnapshot | None:
        gps = self._gps.tick()
        if gps is None:
            return None
        mission = MissionData.model_validate(self._state.get("mission"))
        corridor = self._corridor.update(gps, self._map.route)
        if gps.route_index == len(self._map.route) - 1:
            mission.status = MissionStatus.HOSPITAL
            mission.distance_meters = 0
            mission.eta_seconds = 0
            self._state.update("mission", mission.model_dump())
            self._corridor.release()
            self._state.add_log(f"Mission {mission.mission_id} reached {mission.hospital}", level="WARNING")
        else:
            mission.distance_meters = gps.distance_meters
            mission.eta_seconds = gps.eta_seconds
            self._state.update("mission", mission.model_dump())
        return EmergencySnapshot(mission=mission, gps=gps, corridor=corridor)

    def stop(self) -> EmergencySnapshot:
        mission = MissionData.model_validate(self._state.get("mission"))
        if mission.status != MissionStatus.ACTIVE:
            raise MissionStateError("No active emergency mission to stop")
        mission.status = MissionStatus.COMPLETED
        self._state.update("mission", mission.model_dump())
        self._corridor.release()
        self._state.add_log(f"Mission {mission.mission_id} completed")
        return self.snapshot()

    def request_priority(self) -> EmergencySnapshot:
        mission = MissionData.model_validate(self._state.get("mission"))
        if mission.status != MissionStatus.ACTIVE:
            raise MissionStateError("High priority can only be requested for an active mission")
        mission.priority = Priority.HIGH
        self._state.update("mission", mission.model_dump())
        self._state.add_log(f"Mission {mission.mission_id} escalated to high priority", level="WARNING")
        return self.snapshot()

    def snapshot(self) -> EmergencySnapshot:
        mission = self._state.get("mission")
        raw_gps = self._state.get("gps")
        corridor = self._state.get("green_corridor").get("junctions", [])
        return EmergencySnapshot(
            mission=MissionData.model_validate(mission) if mission.get("status") != MissionStatus.IDLE.value else None,
            gps=raw_gps or None,
            corridor=corridor,
        )

    def reset(self) -> EmergencySnapshot:
        """Return the simulator to its idle state for a repeatable demo run."""
        if self._state.get("green_corridor").get("active_junction"):
            self._corridor.release()
        self._state.update("mission", {"status": MissionStatus.IDLE.value})
        self._state.update("gps", {})
        self._state.add_log("Emergency simulation reset")
        return self.snapshot()
