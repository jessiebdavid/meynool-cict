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

DB_MARKER = "db_integration"


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
