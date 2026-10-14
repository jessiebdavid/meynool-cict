"""Reporting for the Meynool live-database integration tests.

Tests carrying the ``db_integration`` pytest marker (registered in
pytest.ini, applied via ``pytestmark`` in tests/test_migrations.py) can only
run when PostgreSQL is reachable; when it is not, they are skipped. This
conftest makes the final pytest summary explicitly separate passed / failed /
skipped database checks so that skipped checks are never mistaken for
successful database validation.

Report selection uses the explicit marker, never a filename or nodeid, so
renaming or moving the database test module cannot silently disable the
report.
"""
from __future__ import annotations

import uuid

import pytest

DB_MARKER = "db_integration"

# Throwaway credential for tests-created accounts only. The accounts are
# deleted in fixture teardown and never exist outside a test run.
TEST_PASSWORD = "test-only-Password-2026!"


@pytest.fixture
def test_password() -> str:
    """The throwaway credential matching the accounts created by seed_user."""
    return TEST_PASSWORD


@pytest.fixture(scope="session")
def db_engine():
    """Engine to the live PostgreSQL database.

    Skips the dependent test (rather than failing) when PostgreSQL is
    unreachable, matching the honest reporting rules of this suite. The
    first connectivity result is cached so a dead database skips fast.
    """
    from sqlalchemy import create_engine, text

    from app.main import settings

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": settings.database_connect_timeout},
    )
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # any connection failure means "no DB here"
        pytest.skip(f"database not reachable, skipping: {type(exc).__name__}")
    yield engine
    engine.dispose()


@pytest.fixture
def client():
    """Fresh TestClient per test (no cookie leakage between tests)."""
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


@pytest.fixture
def seed_user(db_engine):
    """Factory for throwaway accounts; all created users are removed on teardown.

    Accounts are inserted directly (never through an API endpoint, because
    registration is deliberately not part of the contract).
    """
    from sqlalchemy import text

    from app.security import hash_password

    created: list[str] = []

    def _seed(
        username: str | None = None,
        *,
        password: str = TEST_PASSWORD,
        role: str = "researcher",
        status: str = "active",
    ) -> str:
        name = username or f"t_{uuid.uuid4().hex[:16]}"
        with db_engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO users (username, email, display_name, password_hash, "
                    "role, status, must_reset_password) "
                    "VALUES (:u, :e, :d, :h, :r, :s, false)"
                ),
                {
                    "u": name,
                    "e": f"{name}@example.test",
                    "d": "Test Account",
                    "h": hash_password(password),
                    "r": role,
                    "s": status,
                },
            )
        created.append(name)
        return name

    yield _seed

    if created:
        with db_engine.begin() as conn:  # auth_sessions removed by ON DELETE CASCADE
            for name in created:
                conn.execute(
                    text("DELETE FROM users WHERE username = :u"), {"u": name}
                )


def _is_db_report(report) -> bool:
    """True only for reports of items carrying the db_integration marker."""
    return DB_MARKER in getattr(report, "keywords", {})


def _db_reports(stats, outcome: str):
    return [report for report in stats.get(outcome, []) if _is_db_report(report)]


def _verdict(passed: int, failed: int, errors: int, skipped: int) -> str | None:
    """The single summary line describing live-database verification state.

    Returns None when no database check was collected at all. Pure function
    so tests/test_reporting.py can cover every state without PostgreSQL.
    """
    if not (passed or failed or errors or skipped):
        return None
    if skipped and not passed and not failed and not errors:
        return (
            "LIVE DATABASE VERIFICATION INCOMPLETE: PostgreSQL was unreachable, so "
            f"{skipped} database check(s) were SKIPPED. Skipped checks are "
            "NOT successful database validation."
        )
    if skipped:
        return (
            f"PARTIAL LIVE DATABASE VERIFICATION: {skipped} check(s) skipped; "
            "see skip reasons above."
        )
    if failed or errors:
        return (
            "LIVE DATABASE VERIFICATION FAILED: see the failing database "
            "check(s) above."
        )
    return (
        "LIVE DATABASE VERIFICATION COMPLETE: every database check ran against "
        "PostgreSQL."
    )


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    stats = terminalreporter.stats
    passed = [r for r in _db_reports(stats, "passed") if r.when == "call"]
    failed = _db_reports(stats, "failed")
    errors = _db_reports(stats, "error")
    skipped = _db_reports(stats, "skipped")
    if not (passed or failed or errors or skipped):
        return

    terminalreporter.write_sep(
        "=", f"database integration checks ({DB_MARKER} marker)"
    )
    terminalreporter.write_line(
        f"passed={len(passed)}  failed={len(failed)}  "
        f"errors={len(errors)}  skipped={len(skipped)}"
    )
    verdict = _verdict(len(passed), len(failed), len(errors), len(skipped))
    if verdict is not None:
        terminalreporter.write_line(verdict)
