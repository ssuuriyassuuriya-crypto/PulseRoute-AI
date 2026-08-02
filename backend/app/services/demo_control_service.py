from app.schemas.emergency import StartMissionRequest
from app.schemas.traffic import TrafficFrameRequest
from app.services.emergency_service import EmergencyService, MissionStateError
from app.services.signal_service import AdaptiveSignalService
from app.services.traffic_service import TrafficService
from app.state.manager import StateManager


class DemoControlService:
    """Coordinates safe, repeatable demo actions across domain services."""

    def __init__(self, state: StateManager, traffic: TrafficService, signals: AdaptiveSignalService, emergency: EmergencyService) -> None:
        self._state = state
        self._traffic = traffic
        self._signals = signals
        self._emergency = emergency

    def play_traffic(self) -> dict[str, object]:
        return self._traffic.generate_demo_frame().model_dump()

    def trigger_emergency(self) -> dict[str, object]:
        return self._emergency.start("demo-controller", StartMissionRequest()).model_dump()

    def stop_emergency(self) -> dict[str, object]:
        try:
            return self._emergency.stop().model_dump()
        except MissionStateError:
            return self._emergency.reset().model_dump()

    def reset_simulation(self) -> dict[str, object]:
        self._emergency.reset()
        self._traffic.process_frame(TrafficFrameRequest())
        signals = self._signals.reset_adaptive_mode().model_dump()
        self._state.add_log("Full demo simulation reset")
        return {"signals": signals, "mission": self._state.get("mission"), "gps": self._state.get("gps")}

    def clear_logs(self) -> None:
        self._state.clear_logs()
