"""
PulseRoute AI - Signal Timing & State Constants
"""
from backend.constants.congestion import LEVEL_LOW, LEVEL_MEDIUM, LEVEL_HIGH

GREEN_DURATION_LOW = 20    # seconds
GREEN_DURATION_MEDIUM = 35 # seconds
GREEN_DURATION_HIGH = 50   # seconds
YELLOW_DURATION = 5        # seconds

SIGNAL_GREEN = "GREEN"
SIGNAL_YELLOW = "YELLOW"
SIGNAL_RED = "RED"

GREEN_CORRIDOR_LOCK_DURATION = 60 # Default max duration for emergency override

def get_green_duration(congestion_level: str) -> int:
    if congestion_level == LEVEL_LOW:
        return GREEN_DURATION_LOW
    elif congestion_level == LEVEL_MEDIUM:
        return GREEN_DURATION_MEDIUM
    else:
        return GREEN_DURATION_HIGH
