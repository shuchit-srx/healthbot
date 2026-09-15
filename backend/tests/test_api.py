from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "HealthBot"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "HealthBot"
    assert data["version"] == "1.0.0"


def test_not_found_endpoint():
    response = client.get("/does-not-exist")

    assert response.status_code == 404