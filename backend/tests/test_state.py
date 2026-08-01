"""
PulseRoute AI - Unit Tests for State Manager Transitions
"""
from backend.state.state_manager import (
    state_manager,
    STATE_NORMAL,
    STATE_EMERGENCY_REQUESTED,
    STATE_MISSION_ACTIVE,
    STATE_GREEN_CORRIDOR_ACTIVE,
    STATE_HOSPITAL_REACHED,
    STATE_ADAPTIVE_SCHEDULING_RESTORED
)

def test_state_transitions():
    state_manager.set_system_state(STATE_NORMAL, "Initial test state")
    assert state_manager.get_system_state() == STATE_NORMAL
    
    state_manager.set_system_state(STATE_EMERGENCY_REQUESTED, "Emergency dispatch")
    assert state_manager.get_system_state() == STATE_EMERGENCY_REQUESTED
    
    state_manager.set_system_state(STATE_MISSION_ACTIVE, "GPS connected")
    assert state_manager.get_system_state() == STATE_MISSION_ACTIVE
    
    state_manager.set_system_state(STATE_GREEN_CORRIDOR_ACTIVE, "Preemption active")
    assert state_manager.get_system_state() == STATE_GREEN_CORRIDOR_ACTIVE
    
    state_manager.set_system_state(STATE_HOSPITAL_REACHED, "Arrived at destination")
    assert state_manager.get_system_state() == STATE_HOSPITAL_REACHED
    
    state_manager.set_system_state(STATE_ADAPTIVE_SCHEDULING_RESTORED, "Normal mode restored")
    assert state_manager.get_system_state() == STATE_ADAPTIVE_SCHEDULING_RESTORED
