from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_reports_only_process_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "meynool-api",
        "stage": "starter",
    }
