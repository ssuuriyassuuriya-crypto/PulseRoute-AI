"""
PulseRoute AI - Congestion Level Constants
"""

# Congestion Thresholds (Vehicle Counts per junction/lane)
CONGESTION_LOW_MAX = 15
CONGESTION_MEDIUM_MAX = 35

LEVEL_LOW = "LOW"
LEVEL_MEDIUM = "MEDIUM"
LEVEL_HIGH = "HIGH"

def get_congestion_level(vehicle_count: int) -> str:
    if vehicle_count <= CONGESTION_LOW_MAX:
        return LEVEL_LOW
    elif vehicle_count <= CONGESTION_MEDIUM_MAX:
        return LEVEL_MEDIUM
    else:
        return LEVEL_HIGH
