from app.schemas.emergency import MissionStatus, StartMissionRequest
from app.schemas.traffic import Road
from app.services.emergency_service import EmergencyService
from app.services.green_corridor_service import GreenCorridorService
from app.services.map_service import MapService
from app.services.signal_service import AdaptiveSignalService
from app.services.simulation_service import GpsSimulationService
from app.state.manager import StateManager
from pathlib import Path


def build_service() -> tuple[EmergencyService, StateManager]:
    state = StateManager()
    signals = AdaptiveSignalService(state)
    mapping = MapService(Path(__file__).resolve().parents[1] / "routes_data" / "hospital_route.json")
    gps = GpsSimulationService(state, mapping)
    corridor = GreenCorridorService(state, signals)
    return EmergencyService(state, gps, corridor, mapping), state


def test_mission_starts_gps_and_green_corridor() -> None:
    service, state = build_service()
    snapshot = service.start("driver", StartMissionRequest())

    assert snapshot.mission is not None
    assert snapshot.mission.status == MissionStatus.ACTIVE
    assert snapshot.gps is not None
    assert snapshot.corridor[0].status == "GREEN"
    assert state.get("signals")["mode"] == "EMERGENCY"
    assert state.get("signals")["current_green"] == Road.NORTH.value


def test_mission_arrival_restores_adaptive_signals() -> None:
    service, state = build_service()
    service.start("driver", StartMissionRequest())
    for _ in range(4):
        snapshot = service.tick()

    assert snapshot is not None
    assert snapshot.mission is not None
    assert snapshot.mission.status == MissionStatus.HOSPITAL
    assert state.get("signals")["mode"] == "ADAPTIVE"
