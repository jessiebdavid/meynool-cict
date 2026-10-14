"""Focused checks for migrations against a live database.

These tests SKIP (not pass) when no PostgreSQL is reachable, so a missing
database is reported honestly rather than fabricating a green result.
tests/conftest.py prints a database-check summary (passed / failed / skipped)
and states explicitly when live database verification is incomplete.
"""
from __future__ import annotations

import pytest
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DataError

from app.main import settings

# Marks every test in this module for the database summary in conftest.py.
# Selection is by this explicit marker, never by filename, so renaming this
# file cannot silently disable the report.
pytestmark = pytest.mark.db_integration

# The eight controlled vocabularies created by 0001 (DATABASE_SCHEMA.md section 2).
EXPECTED_ENUMS = {
    "account_role",
    "account_status",
    "source_status",
    "passage_status",
    "evidence_relation",
    "review_decision",
    "ingestion_status",
    "hypothesis_status",
}

# Exact accepted labels per enum, from DATABASE_SCHEMA.md section 2. Compared
# against pg_enum to detect drift that migration 0001's checkfirst=True would
# silently skip: checkfirst only verifies a type with that *name* exists, never
# that its labels are correct.
EXPECTED_ENUM_VALUES: dict[str, set[str]] = {
    "account_role": {"admin", "researcher", "reviewer"},
    "account_status": {"active", "disabled", "pending"},
    "source_status": {"draft", "verified", "disputed", "withdrawn"},
    "passage_status": {"draft", "reviewed", "verified", "disputed"},
    "evidence_relation": {"supports", "contradicts", "qualifies", "contextualizes"},
    "review_decision": {"approve", "revise", "reject", "needs_expert"},
    "ingestion_status": {"queued", "running", "succeeded", "partial", "failed", "cancelled"},
    "hypothesis_status": {"proposed", "under_review", "supported", "contradicted", "inconclusive", "withdrawn"},
}

_ENGINE = None
_REACHABLE: bool | None = None


def _engine():
    """One pooled engine per test run (avoids leaking a connection per test)."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": settings.database_connect_timeout},
        )
    return _ENGINE


def _require_db():
    """Return the engine, or skip the test if the database is unreachable.

    The first connectivity failure is cached so that a suite against a dead
    database skips fast instead of paying connect_timeout for every test.
    """
    global _REACHABLE
    if _REACHABLE is False:
        pytest.skip(
            "database not reachable (seen earlier in this run); skipping migration checks"
        )
    try:
        engine = _engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # any connection failure means "no DB here"
        _REACHABLE = False
        pytest.skip(
            f"database not reachable, skipping migration checks: {type(exc).__name__}"
        )
    _REACHABLE = True
    return engine


def test_required_extensions_are_installed():
    engine = _require_db()
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname IN ('pgcrypto','vector')")
        ).scalars().all()
    assert set(rows) == {"pgcrypto", "vector"}, f"expected pgcrypto+vector, got {rows}"


def test_all_controlled_vocab_enums_exist():
    engine = _require_db()
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT typname FROM pg_type WHERE typtype='e'")).scalars().all()
    assert set(rows) == EXPECTED_ENUMS, (
        f"missing {EXPECTED_ENUMS - set(rows)}; extra {set(rows) - EXPECTED_ENUMS}"
    )


def _script_directory() -> ScriptDirectory:
    """Alembic script directory resolved from this backend's alembic.ini."""
    from pathlib import Path

    backend_dir = Path(__file__).resolve().parents[1]
    cfg = AlembicConfig(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    return ScriptDirectory.from_config(cfg)


def test_alembic_version_is_at_head():
    """The live database must sit at the script's current head (0001 -> ... -> 0003)."""
    head = _script_directory().get_current_head()
    engine = _require_db()
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert version == head, f"expected alembic at {head}, got {version!r}"


def test_enum_labels_match_spec():
    """Enum labels actually stored in PostgreSQL must equal the documented spec.

    This is the drift check migration 0001 cannot perform: its
    checkfirst=True skips creation whenever a type with the same name already
    exists, even if that type's labels are wrong, missing or extra.
    """
    engine = _require_db()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT t.typname, e.enumlabel "
                "FROM pg_type AS t JOIN pg_enum AS e ON e.enumtypid = t.oid"
            )
        ).all()
    actual: dict[str, set[str]] = {}
    for typname, label in rows:
        actual.setdefault(typname, set()).add(label)
    assert set(actual) == EXPECTED_ENUMS, (
        f"missing enums {sorted(EXPECTED_ENUMS - set(actual))}; "
        f"unexpected enums {sorted(set(actual) - EXPECTED_ENUMS)}"
    )
    for name in sorted(EXPECTED_ENUMS):
        assert actual[name] == EXPECTED_ENUM_VALUES[name], (
            f"enum {name} drifted: missing labels "
            f"{sorted(EXPECTED_ENUM_VALUES[name] - actual[name])}; extra labels "
            f"{sorted(actual[name] - EXPECTED_ENUM_VALUES[name])}"
        )


@pytest.mark.parametrize("enum_name", sorted(EXPECTED_ENUMS))
def test_enum_accepts_documented_value(enum_name):
    """A documented label must cast successfully."""
    valid = sorted(EXPECTED_ENUM_VALUES[enum_name])[0]
    engine = _require_db()
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT '{valid}'::{enum_name}")).scalar()
    assert result == valid


@pytest.mark.parametrize("enum_name", sorted(EXPECTED_ENUMS))
def test_enum_rejects_undocumented_value(enum_name):
    """An undocumented label must fail with the enum's own invalid-input error.

    The assertion is deliberately narrow: PostgreSQL rejects the cast with
    SQLSTATE 22P02 (invalid_text_representation), which psycopg surfaces as
    InvalidTextRepresentation and SQLAlchemy wraps as DataError. A connection
    failure (OperationalError / InterfaceError) or any unrelated database
    error raises a different class and cannot satisfy pytest.raises(DataError);
    the sqlstate check rejects a misclassified DataError as well.
    """
    engine = _require_db()
    with engine.connect() as conn:
        with pytest.raises(DataError) as excinfo:
            conn.execute(text(f"SELECT 'not_a_documented_member'::{enum_name}"))
        sqlstate = getattr(excinfo.value.orig, "sqlstate", None)
        assert sqlstate == "22P02", (
            f"expected SQLSTATE 22P02 (invalid enum input) for {enum_name}, "
            f"got {sqlstate!r} from {excinfo.value.orig!r}"
        )
