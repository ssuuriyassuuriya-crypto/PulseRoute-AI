"""
PulseRoute AI - Timeline Audit Trace Service
"""
from backend.state.state_manager import state_manager

class TimelineService:
    def get_timeline_trace(self):
        snapshot = state_manager.get_full_snapshot()
        return snapshot["timeline_events"]

timeline_service = TimelineService()
