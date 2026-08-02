from math import ceil
from time import time

from app.constants.signals import DEFAULT_GREEN_SECONDS, YELLOW_SECONDS
from app.schemas.signals import ManualOverrideRequest, SignalMode, SignalPhase, SignalSnapshot
from app.schemas.traffic import Road
from app.state.manager import StateManager


class SignalStateError(Exception):
    """Raised when an invalid signal transition is requested."""


class AdaptiveSignalService:
    """Coordinates adaptive signal phases while preserving safe yellow transitions."""

    def __init__(self, state: StateManager) -> None:
        self._state = state

    def initialize(self) -> SignalSnapshot:
        existing = self._state.get("signals")
        if existing:
            return SignalSnapshot.model_validate(existing)
        return self._start_green(self._recommended_road(), SignalMode.ADAPTIVE, self._recommended_duration())

    def tick(self) -> SignalSnapshot:
        snapshot = self.initialize()
        if snapshot.mode == SignalMode.EMERGENCY:
            return self._refresh_remaining(snapshot)

        expires_at = self._state.get("signals")["expires_at"]
        if expires_at > time():
            return self._refresh_remaining(snapshot)
        if snapshot.phase == SignalPhase.GREEN:
            return self._start_yellow(snapshot.current_green, snapshot.mode)
        return self._start_green(self._recommended_road(), SignalMode.ADAPTIVE, self._recommended_duration())

    def manual_override(self, request: ManualOverrideRequest) -> SignalSnapshot:
        snapshot = self.initialize()
        if snapshot.mode == SignalMode.EMERGENCY:
            raise SignalStateError("Manual override is unavailable while an emergency corridor is locked")
        result = self._start_green(request.road, SignalMode.MANUAL, request.duration_seconds)
        self._state.add_log(f"Manual signal override: {request.road.value} green for {request.duration_seconds} seconds")
        return result

    def reset_adaptive_mode(self) -> SignalSnapshot:
        snapshot = self._start_green(self._recommended_road(), SignalMode.ADAPTIVE, self._recommended_duration())
        self._state.add_log("Signal scheduler reset to adaptive mode")
        return snapshot

    def lock_for_emergency(self, road: Road, duration_seconds: int = 30) -> SignalSnapshot:
        """Extension point consumed by the green-corridor module."""
        snapshot = self._start_green(road, SignalMode.EMERGENCY, duration_seconds)
        self._state.add_log(f"Emergency signal lock enabled for {road.value}", level="WARNING")
        return snapshot

    def release_emergency_lock(self) -> SignalSnapshot:
        snapshot = self._state.get("signals")
        if snapshot.get("mode") != SignalMode.EMERGENCY.value:
            raise SignalStateError("No emergency signal lock is active")
        return self.reset_adaptive_mode()

    def _start_green(self, road: Road, mode: SignalMode, duration_seconds: int) -> SignalSnapshot:
        payload = self._payload(road, mode, SignalPhase.GREEN, duration_seconds)
        self._state.update("signals", payload)
        return SignalSnapshot.model_validate(payload)

    def _start_yellow(self, road: Road, prior_mode: SignalMode) -> SignalSnapshot:
        payload = self._payload(road, prior_mode, SignalPhase.YELLOW, YELLOW_SECONDS)
        self._state.update("signals", payload)
        self._state.add_log(f"{road.value} signal transitioned to yellow")
        return SignalSnapshot.model_validate(payload)

    def _refresh_remaining(self, snapshot: SignalSnapshot) -> SignalSnapshot:
        raw = self._state.get("signals")
        remaining = max(0, ceil(raw["expires_at"] - time()))
        if remaining == snapshot.remaining_seconds:
            return snapshot
        raw["remaining_seconds"] = remaining
        self._state.update("signals", raw)
        return SignalSnapshot.model_validate(raw)

    def _payload(self, road: Road, mode: SignalMode, phase: SignalPhase, duration_seconds: int) -> dict[str, object]:
        lights = {candidate.value: "RED" for candidate in Road}
        lights[road.value] = phase.value
        return {
            "mode": mode.value,
            "phase": phase.value,
            "current_green": road.value,
            "remaining_seconds": duration_seconds,
            "lights": lights,
            "emergency_lock": mode == SignalMode.EMERGENCY,
            "expires_at": time() + duration_seconds,
        }

    def _recommended_road(self) -> Road:
        decision = self._state.get("ai_decision")
        return Road(decision["road"]) if decision else Road.NORTH

    def _recommended_duration(self) -> int:
        decision = self._state.get("ai_decision")
        return int(decision["green_time"]) if decision else DEFAULT_GREEN_SECONDS
