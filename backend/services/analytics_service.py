"""
PulseRoute AI - Road Analytics & Explainable AI Service
"""
from typing import Dict, Any
from backend.constants.congestion import get_congestion_level, LEVEL_LOW, LEVEL_MEDIUM, LEVEL_HIGH
from backend.constants.signals import get_green_duration

class AnalyticsService:
    def compute_junction_analytics(self, junction_id: str, junction_name: str, lane_counts: Dict[str, int]) -> Dict[str, Any]:
        total_vehicles = sum(lane_counts.values())
        congestion_level = get_congestion_level(total_vehicles)
        
        # Determine lane with highest vehicle count
        max_lane = max(lane_counts, key=lane_counts.get) if lane_counts else "NORTH"
        max_count = lane_counts.get(max_lane, 0)
        
        allocated_green = get_green_duration(congestion_level)
        
        # Calculate queue length (approx 6 meters per vehicle) and wait index
        queue_length = round(max_count * 5.8, 1)
        wait_index = round((total_vehicles / 40.0) * 1.8, 2)
        confidence = round(88.0 + (min(total_vehicles, 50) / 50.0) * 11.5, 1)
        
        reasoning = (
            f"Phase assigned to {max_lane} Lane based on highest density ({max_count} vehicles, "
            f"{congestion_level} congestion). Allocated {allocated_green}s green cycle with {confidence}% AI confidence."
        )
        
        return {
            "junction_id": junction_id,
            "junction_name": junction_name,
            "total_vehicles": total_vehicles,
            "lane_counts": lane_counts,
            "congestion_level": congestion_level,
            "queue_length_meters": queue_length,
            "wait_time_index": wait_index,
            "selected_green_lane": max_lane,
            "allocated_green_seconds": allocated_green,
            "confidence_score": confidence,
            "reasoning": reasoning
        }

analytics_service = AnalyticsService()
