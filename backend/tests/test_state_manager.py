from app.state.manager import StateManager


def test_state_snapshot_is_isolated_and_logs_are_recorded() -> None:
    state = StateManager()
    state.merge("metrics", {"vehicles_processed": 12})
    snapshot = state.snapshot()
    snapshot["metrics"]["vehicles_processed"] = 99
    state.add_log("Traffic service initialized")

    assert state.get("metrics")["vehicles_processed"] == 12
    assert state.get("logs")[0]["event"] == "Traffic service initialized"
