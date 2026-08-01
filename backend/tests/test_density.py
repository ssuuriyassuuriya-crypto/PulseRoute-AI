"""
PulseRoute AI - Unit Tests for Congestion & Signal Duration
"""
from backend.constants.congestion import get_congestion_level, LEVEL_LOW, LEVEL_MEDIUM, LEVEL_HIGH
from backend.constants.signals import get_green_duration, GREEN_DURATION_LOW, GREEN_DURATION_MEDIUM, GREEN_DURATION_HIGH
from backend.services.analytics_service import analytics_service

def test_congestion_levels():
    assert get_congestion_level(10) == LEVEL_LOW
    assert get_congestion_level(25) == LEVEL_MEDIUM
    assert get_congestion_level(45) == LEVEL_HIGH

def test_green_durations():
    assert get_green_duration(LEVEL_LOW) == GREEN_DURATION_LOW
    assert get_green_duration(LEVEL_MEDIUM) == GREEN_DURATION_MEDIUM
    assert get_green_duration(LEVEL_HIGH) == GREEN_DURATION_HIGH

def test_analytics_calculation():
    counts = {"NORTH": 10, "SOUTH": 5, "EAST": 30, "WEST": 12}
    res = analytics_service.compute_junction_analytics("J1_BEGUMPET", "Begumpet Junction", counts)
    assert res["selected_green_lane"] == "EAST"
    assert res["congestion_level"] == LEVEL_HIGH
    assert res["allocated_green_seconds"] == GREEN_DURATION_HIGH
    assert res["total_vehicles"] == 57
