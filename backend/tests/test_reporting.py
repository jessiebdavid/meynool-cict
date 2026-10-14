"""Focused tests for the database-check reporting helpers in conftest.py.

They verify that report selection uses the explicit ``db_integration`` marker
(a filename must not count), that the module under report really carries the
marker, and that the verdict line distinguishes every database-verification
state. No live PostgreSQL is required.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import conftest


def _report(keywords, when="call"):
    """Minimal stand-in for a pytest TestReport (only fields conftest uses)."""
    return SimpleNamespace(nodeid="whatever/the/file_is_named.py::test_x", keywords=keywords, when=when)


def test_selection_uses_marker_not_filename():
    marked = _report({conftest.DB_MARKER: object()})
    filename_only = _report({"test_migrations.py": True, "test_migrations.py::test_x": True})
    unmarked = _report({"test_reporting.py": True})
    assert conftest._is_db_report(marked)
    # A matching filename/nodeid alone must NOT be counted anymore.
    assert not conftest._is_db_report(filename_only)
    assert not conftest._is_db_report(unmarked)


def test_db_reports_filters_by_outcome_and_marker():
    stats = {
        "passed": [
            _report({conftest.DB_MARKER: object()}),
            _report({}),  # unmarked pass must not count
        ],
        "failed": [_report({})],  # unmarked failure must not count
    }
    assert len(conftest._db_reports(stats, "passed")) == 1
    assert len(conftest._db_reports(stats, "failed")) == 0


def test_database_test_module_carries_reporting_marker():
    """Guard against the marker (and with it the summary) silently vanishing."""
    import test_migrations

    marks = test_migrations.pytestmark
    if not isinstance(marks, list):
        marks = [marks]
    assert any(m.name == conftest.DB_MARKER for m in marks), (
        f"test_migrations.pytestmark must include {conftest.DB_MARKER!r}, got {marks!r}"
    )


@pytest.mark.parametrize(
    "counts, expected",
    [
        ((0, 0, 0, 0), None),
        ((0, 0, 0, 20), "INCOMPLETE"),
        ((20, 0, 0, 0), "COMPLETE"),
        ((18, 0, 0, 2), "PARTIAL"),
        ((19, 1, 0, 0), "FAILED"),
        ((19, 0, 1, 0), "FAILED"),
    ],
    ids=["none", "all-skipped", "complete", "partial", "failed", "error"],
)
def test_verdict_distinguishes_verification_state(counts, expected):
    verdict = conftest._verdict(*counts)
    if expected is None:
        assert verdict is None
    else:
        assert verdict is not None
        assert expected in verdict
        if expected == "INCOMPLETE":
            assert "NOT successful database validation" in verdict
