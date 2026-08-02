from app.schemas.traffic import RoadMetrics, TrafficDecision


class AIDecisionService:
    """Selects the highest-pressure road and emits an auditable explanation."""

    def decide(self, metrics: dict[str, RoadMetrics]) -> TrafficDecision:
        selected = max(
            metrics.values(),
            key=lambda item: (item.density_score, item.vehicle_count, item.road.value),
        )
        confidence = min(98, max(55, round(55 + selected.density_score)))
        return TrafficDecision(
            road=selected.road,
            vehicles=selected.vehicle_count,
            density=selected.congestion,
            score=selected.density_score,
            green_time=selected.recommended_green_seconds,
            confidence=confidence,
            reason=(
                f"{selected.road.value} has the highest congestion score "
                f"({selected.density_score}) with {selected.vehicle_count} tracked vehicles."
            ),
        )
