from collections.abc import Mapping
from copy import deepcopy
from datetime import UTC, datetime
from threading import RLock
from typing import Any


class StateManager:
    """Thread-safe, in-memory single source of truth for live system state."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._state: dict[str, Any] = {
            "roads": {},
            "signals": {},
            "analytics": {},
            "ai_decision": None,
            "mission": {"status": "IDLE"},
            "gps": {},
            "video": {"status": "IDLE"},
            "green_corridor": {"active_junction": None, "junctions": []},
            "metrics": {},
            "system_health": {
                "backend": "healthy",
                "analytics": "pending",
                "gps": "pending",
                "vision": "pending",
                "websocket": "pending",
            },
            "logs": [],
        }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self._state)

    def get(self, key: str) -> Any:
        with self._lock:
            return deepcopy(self._state[key])

    def update(self, key: str, value: Any) -> None:
        with self._lock:
            self._state[key] = deepcopy(value)

    def merge(self, key: str, values: Mapping[str, Any]) -> None:
        with self._lock:
            if not isinstance(self._state.get(key), dict):
                raise ValueError(f"State key '{key}' is not a mapping")
            self._state[key].update(deepcopy(dict(values)))

    def add_log(self, event: str, level: str = "INFO") -> dict[str, str]:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            "level": level,
        }
        with self._lock:
            self._state["logs"].append(entry)
            self._state["logs"] = self._state["logs"][-250:]
        return entry

    def clear_logs(self) -> None:
        with self._lock:
            self._state["logs"] = []
