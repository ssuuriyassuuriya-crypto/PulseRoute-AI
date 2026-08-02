from fastapi.testclient import TestClient

from app.main import app


def test_admin_can_login_and_read_identity() -> None:
    with TestClient(app) as client:
        response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["user"]["role"] == "ADMIN"

        token = body["data"]["access_token"]
        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["data"]["username"] == "admin"


def test_invalid_credentials_are_rejected() -> None:
    with TestClient(app) as client:
        response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong-password"})
    assert response.status_code == 401


def test_health_exposes_service_snapshot() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "healthy"


def test_frontend_cors_preflight_is_allowed() -> None:
    with TestClient(app) as client:
        response = client.options(
            "/api/auth/login",
            headers={"Origin": "http://127.0.0.1:5173", "Access-Control-Request-Method": "POST"},
        )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
