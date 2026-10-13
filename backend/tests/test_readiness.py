"""Focused tests for the readiness probe's bounded database check.

Covers the two behaviours of GET /api/v1/ready:
  * database reachable   -> 200 with the documented payload.
  * database unreachable -> a timely 503 (bounded by connect_timeout), never a hang.
"""
import time

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

import app.main as main
from app.main import app

client = TestClient(app)

# Upper bound for a not-ready response. The probe's connect_timeout defaults to
# 5s; anything well beyond that means the endpoint is hanging again.
READY_TIMEOUT_SECONDS = 15


class _FakeConnection:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, *_args, **_kwargs):
        return None


class _FakeEngine:
    def connect(self):
        return _FakeConnection()

    def dispose(self):
        return None


def test_ready_returns_ready_when_database_reachable(monkeypatch):
    """A successful SELECT 1 yields the documented ready payload."""
    monkeypatch.setattr(main, "create_engine", lambda *a, **k: _FakeEngine())
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "reachable",
        "schema": "not_verified",
    }


def test_ready_passes_bounded_connect_timeout_to_driver(monkeypatch):
    """The probe must forward a positive connect_timeout to the driver."""
    captured = {}

    def fake_create_engine(*args, **kwargs):
        captured.update(kwargs)
        return _FakeEngine()

    monkeypatch.setattr(main, "create_engine", fake_create_engine)
    client.get("/api/v1/ready")
    assert captured.get("connect_args", {}).get("connect_timeout", 0) > 0


def test_ready_returns_503_quickly_when_database_unavailable(monkeypatch):
    """An unreachable database returns 503 promptly instead of hanging."""
    monkeypatch.setattr(
        main,
        "create_engine",
        lambda *a, **k: (_ for _ in ()).throw(OperationalError("SELECT 1", {}, Exception("refused"))),
    )
    started = time.monotonic()
    response = client.get("/api/v1/ready")
    elapsed = time.monotonic() - started
    assert response.status_code == 503
    assert elapsed < READY_TIMEOUT_SECONDS
