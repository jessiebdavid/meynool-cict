"""Contract checks for the standard error envelope and request IDs.

API_CONTRACT.md section 1.1 requires a request ID in error responses;
section 1.2 defines {"error": {"code", "message", "request_id"}}.
"""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

import app.main as main
from app.main import app

client = TestClient(app)


def test_unknown_route_returns_contract_error_envelope():
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "NOT_FOUND"
    assert isinstance(error["message"], str) and error["message"]
    assert error["request_id"]
    assert response.headers["X-Request-ID"] == error["request_id"]


def test_inbound_request_id_is_propagated():
    response = client.get("/api/v1/health", headers={"X-Request-ID": "req-abc-123"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-abc-123"


def test_ready_503_uses_dependency_unavailable_envelope(monkeypatch):
    def unreachable_engine(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("refused"))

    monkeypatch.setattr(main, "create_engine", unreachable_engine)
    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "DEPENDENCY_UNAVAILABLE"
    assert error["request_id"]
    assert "Traceback" not in error["message"]


def test_success_response_carries_request_id_header():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")
