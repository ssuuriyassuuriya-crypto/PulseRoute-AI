from app.main import app
from fastapi.testclient import TestClient


def test_admin_demo_controls_are_repeatable() -> None:
    with TestClient(app) as client:
        login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
        traffic = client.post("/api/demo/play-traffic", headers=headers)
        emergency = client.post("/api/demo/trigger-emergency", headers=headers)
        reset = client.post("/api/demo/reset-simulation", headers=headers)

    assert traffic.status_code == 200
    assert emergency.status_code == 200
    assert reset.status_code == 200
    assert reset.json()["data"]["mission"]["status"] == "IDLE"
