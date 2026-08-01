"""
PulseRoute AI - Unit Tests for Green Corridor Preemption Logic
"""
from backend.services.green_corridor_service import haversine_distance_km

def test_haversine_distance():
    # Begumpet to Panjagutta distance (approx 2.5 - 2.8 km)
    dist = haversine_distance_km(17.4447, 78.4664, 17.4256, 78.4513)
    assert 2.0 < dist < 3.5
