from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app


def admin_token(client: TestClient) -> str:
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    return response.json()["data"]["access_token"]


def test_timeline_report_and_dashboard_socket() -> None:
    with TestClient(app) as client:
        token = admin_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        timeline = client.get("/api/timeline", headers=headers)
        report = client.get("/api/reports", headers=headers)
        assert timeline.status_code == 200
        assert report.status_code == 200
        assert "delay_saved_seconds" in report.json()["data"]

        with client.websocket_connect(f"/ws/dashboard?token={token}") as socket:
            snapshot = socket.receive_json()
            assert "signals" in snapshot
            assert "mission" in snapshot


def test_dashboard_socket_rejects_ambulance_driver() -> None:
    with TestClient(app) as client:
        response = client.post("/api/auth/login", json={"username": "driver", "password": "driver123"})
        token = response.json()["data"]["access_token"]
        try:
            with client.websocket_connect(f"/ws/dashboard?token={token}"):
                pass
        except WebSocketDisconnect as exc:
            assert exc.code == 1008
        else:
            raise AssertionError("Driver dashboard websocket connection should be rejected")
