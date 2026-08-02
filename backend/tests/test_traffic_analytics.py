from app.schemas.traffic import BoundingBox, Road, TrafficFrameRequest, VehicleClass, VehicleObservation
from app.services.ai_decision_service import AIDecisionService
from app.services.traffic_service import RegionMapper, TrafficService
from app.state.manager import StateManager
from fastapi.testclient import TestClient

from app.main import app


def observation(identifier: str, x1: float, y1: float, x2: float, y2: float, wait: float = 0) -> VehicleObservation:
    return VehicleObservation(
        tracking_id=identifier,
        vehicle_class=VehicleClass.CAR,
        confidence=0.9,
        bbox=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
        waiting_seconds=wait,
    )


def test_region_mapping_assigns_a_single_cardinal_road() -> None:
    assert RegionMapper.map_observation(observation("north", 0.45, 0.05, 0.55, 0.15)) == Road.NORTH
    assert RegionMapper.map_observation(observation("south", 0.45, 0.85, 0.55, 0.95)) == Road.SOUTH
    assert RegionMapper.map_observation(observation("west", 0.05, 0.45, 0.15, 0.55)) == Road.WEST
    assert RegionMapper.map_observation(observation("east", 0.85, 0.45, 0.95, 0.55)) == Road.EAST


def test_analytics_prioritizes_highest_road_pressure() -> None:
    service = TrafficService(StateManager(), AIDecisionService())
    observations = [observation(f"e-{index}", 0.8, 0.45, 0.9, 0.55, wait=20) for index in range(36)]
    observations.extend([observation("north", 0.45, 0.05, 0.55, 0.15)])
    result = service.process_frame(TrafficFrameRequest(observations=observations))

    assert result.roads["East"].congestion == "HIGH"
    assert result.roads["East"].recommended_green_seconds == 50
    assert result.decision.road == Road.EAST
    assert "highest congestion score" in result.decision.reason


def test_traffic_endpoint_requires_admin_and_updates_analytics() -> None:
    payload = {
        "observations": [
            {"tracking_id": "e-1", "vehicle_class": "car", "confidence": 0.9,
             "bbox": {"x1": 0.8, "y1": 0.45, "x2": 0.9, "y2": 0.55}}
        ]
    }
    with TestClient(app) as client:
        driver_login = client.post("/api/auth/login", json={"username": "driver", "password": "driver123"})
        driver_token = driver_login.json()["data"]["access_token"]
        assert client.post("/api/traffic/observations", json=payload, headers={"Authorization": f"Bearer {driver_token}"}).status_code == 403

        admin_login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        admin_token = admin_login.json()["data"]["access_token"]
        submitted = client.post("/api/traffic/observations", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert submitted.status_code == 200
        analytics = client.get("/api/analytics", headers={"Authorization": f"Bearer {admin_token}"})

    assert analytics.status_code == 200
    assert analytics.json()["data"]["decision"]["road"] == "East"


def test_demo_traffic_creates_high_east_congestion() -> None:
    result = TrafficService(StateManager(), AIDecisionService()).generate_demo_frame()
    assert len(result.observations) == 69
    assert result.roads["East"].congestion == "HIGH"
    assert result.decision.road == Road.EAST
