from time import time

import pytest

from app.schemas.signals import ManualOverrideRequest, SignalMode, SignalPhase
from app.schemas.traffic import Road
from app.services.signal_service import AdaptiveSignalService, SignalStateError
from app.state.manager import StateManager


def test_signal_scheduler_uses_ai_decision_and_transitions_through_yellow() -> None:
    state = StateManager()
    state.update("ai_decision", {"road": "East", "green_time": 50})
    service = AdaptiveSignalService(state)
    initialized = service.initialize()
    assert initialized.current_green == Road.EAST
    assert initialized.phase == SignalPhase.GREEN
    assert initialized.remaining_seconds == 50

    raw = state.get("signals")
    raw["expires_at"] = time() - 1
    state.update("signals", raw)
    yellow = service.tick()
    assert yellow.phase == SignalPhase.YELLOW
    assert yellow.lights["East"] == "YELLOW"


def test_manual_override_and_emergency_lock_rules() -> None:
    service = AdaptiveSignalService(StateManager())
    manual = service.manual_override(ManualOverrideRequest(road=Road.WEST, duration_seconds=30))
    assert manual.mode == SignalMode.MANUAL
    assert manual.lights["West"] == "GREEN"

    emergency = service.lock_for_emergency(Road.NORTH)
    assert emergency.emergency_lock is True
    with pytest.raises(SignalStateError):
        service.manual_override(ManualOverrideRequest(road=Road.SOUTH, duration_seconds=30))
