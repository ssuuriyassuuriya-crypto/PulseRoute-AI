from datetime import UTC, datetime

from app.state.manager import StateManager


class ReportService:
    """Builds reproducible dashboard reports exclusively from central state."""

    def __init__(self, state: StateManager) -> None:
        self._state = state

    def generate(self) -> dict[str, object]:
        snapshot = self._state.snapshot()
        roads = snapshot["analytics"].get("roads", {})
        total_vehicles = sum(item["vehicle_count"] for item in roads.values())
        total_wait = sum(item["average_wait_seconds"] * item["vehicle_count"] for item in roads.values())
        average_wait = round(total_wait / total_vehicles, 2) if total_vehicles else 0.0
        current_signal = snapshot["signals"]
        logs = snapshot["logs"]
        mission = snapshot["mission"]
        report = {
            "generated_at": datetime.now(UTC).isoformat(),
            "vehicles_processed": snapshot["metrics"].get("total_vehicles", 0),
            "average_wait_seconds": average_wait,
            "signal_utilization": "EMERGENCY" if current_signal.get("emergency_lock") else current_signal.get("mode", "ADAPTIVE"),
            "delay_saved_seconds": round(total_vehicles * average_wait * 0.18, 1),
            "green_corridor_activations": sum("Green corridor activated" in item["event"] for item in logs),
            "mission_status": mission.get("status", "IDLE"),
            "mission_eta_seconds": mission.get("eta_seconds", 0),
        }
        self._state.update("reports", report)
        return report
