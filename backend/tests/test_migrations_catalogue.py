"""Schema-shape checks for migrations 0002 and 0003 against live PostgreSQL.

Every check is read-only against the information catalog, plus one
constraint-behavior probe that creates and removes its own fixture rows.
Skipped (not passed) when PostgreSQL is unreachable — see conftest.py.
"""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

pytestmark = pytest.mark.db_integration

# Exact column sets from DATABASE_SCHEMA.md section 3.1.
USERS_COLUMNS = {
    "id", "username", "email", "display_name", "password_hash", "role", "status",
    "must_reset_password", "last_login_at", "created_by", "created_at", "updated_at",
    "disabled_at",
}
AUTH_SESSIONS_COLUMNS = {
    "id", "user_id", "token_hash", "created_at", "expires_at", "revoked_at",
    "last_seen_at", "ip_hash", "user_agent",
}

# Exact column sets from DATABASE_SCHEMA.md section 3.2.
LITERARY_SOURCES_COLUMNS = {
    "id", "canonical_title", "title_ta", "title_en", "attributed_author",
    "attribution_confidence", "genre", "tradition_or_collection", "summary",
    "source_status", "provenance_notes", "created_by", "created_at", "updated_at",
}
SOURCE_EDITIONS_COLUMNS = {
    "id", "source_id", "edition_title", "editor_or_publisher", "publication_year",
    "publication_year_end", "edition_type", "language_code", "identifier", "source_url",
    "archive_or_repository", "rights_status", "rights_notes", "content_checksum",
    "edition_notes", "created_at", "updated_at",
}
PASSAGES_COLUMNS = {
    "id", "source_edition_id", "passage_code", "sequence_number", "locator",
    "original_text", "normalized_text", "language_code", "transcription_method",
    "transcription_confidence", "status", "text_checksum", "editorial_notes",
    "created_by", "created_at", "updated_at",
}
PASSAGE_REVISIONS_COLUMNS = {
    "id", "passage_id", "revision_number", "original_text_snapshot",
    "normalized_text_snapshot", "change_reason", "changed_by", "created_at",
}
INTERPRETATIONS_COLUMNS = {
    "id", "passage_id", "interpretation_type", "language_code", "body",
    "author_or_model", "model_version", "confidence", "status", "source_reference",
    "created_by", "created_at", "updated_at",
}


def _columns_of(engine, table: str) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = :t"
            ),
            {"t": table},
        ).scalars().all()
    return set(rows)


@pytest.mark.parametrize(
    "table,expected",
    [
        ("users", USERS_COLUMNS),
        ("auth_sessions", AUTH_SESSIONS_COLUMNS),
        ("literary_sources", LITERARY_SOURCES_COLUMNS),
        ("source_editions", SOURCE_EDITIONS_COLUMNS),
        ("passages", PASSAGES_COLUMNS),
        ("passage_revisions", PASSAGE_REVISIONS_COLUMNS),
        ("interpretations", INTERPRETATIONS_COLUMNS),
    ],
)
def test_table_columns_match_spec(db_engine, table, expected):
    actual = _columns_of(db_engine, table)
    assert actual == expected, (
        f"{table}: missing {sorted(expected - actual)}; "
        f"unexpected {sorted(actual - expected)}"
    )


def test_required_columns_are_not_nullable(db_engine):
    """NOT NULL guarantees from sections 3.1/3.2 on the critical columns."""
    checks = [
        ("users", "username"), ("users", "email"), ("users", "password_hash"),
        ("auth_sessions", "token_hash"), ("auth_sessions", "expires_at"),
        ("literary_sources", "canonical_title"), ("source_editions", "edition_title"),
        ("passages", "locator"), ("passages", "original_text"),
        ("passage_revisions", "original_text_snapshot"),
        ("passage_revisions", "change_reason"),
        ("interpretations", "body"), ("interpretations", "language_code"),
    ]
    with db_engine.connect() as conn:
        for table, column in checks:
            is_nullable = conn.execute(
                text(
                    "SELECT is_nullable FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name=:t AND column_name=:c"
                ),
                {"t": table, "c": column},
            ).scalar()
            assert is_nullable == "NO", f"{table}.{column} must be NOT NULL"


def test_account_indexes_exist(db_engine):
    """Section 4 account/session indexes, assigned to 0002 by section 6 step 2."""
    with db_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT indexname, indexdef FROM pg_indexes "
                "WHERE schemaname = 'public' AND tablename IN ('users','auth_sessions')"
            )
        ).all()
    definitions = dict(rows)
    expected = {
        "ux_users_username_ci": "lower(username)",
        "ux_users_email_ci": "lower(email)",
        "ix_users_role_status": "(role, status)",
        "ix_sessions_user_expiry": "(user_id, expires_at)",
        "ix_sessions_expiry_active": "revoked_at IS NULL",
    }
    for name, fragment in expected.items():
        assert name in definitions, f"missing index {name}"
        assert fragment in definitions[name], (
            f"{name}: definition {definitions[name]!r} lacks {fragment!r}"
        )


def test_passage_partial_unique_indexes(db_engine):
    """Section 3.2 requires partial unique indexes, not plain constraints."""
    with db_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT i.indexname, i.indexdef, ix.indisunique "
                "FROM pg_indexes i JOIN pg_index ix ON ix.indexrelid = "
                "to_regclass('public.' || i.indexname) "
                "WHERE i.schemaname = 'public' AND i.tablename = 'passages'"
            )
        ).all()
    by_name = {name: (definition, is_unique) for name, definition, is_unique in rows}

    code_idx = by_name.get("ux_passages_edition_passage_code")
    assert code_idx is not None, "missing ux_passages_edition_passage_code"
    assert code_idx[1] is True
    assert "WHERE (passage_code IS NOT NULL)" in code_idx[0]

    seq_idx = by_name.get("ux_passages_edition_sequence")
    assert seq_idx is not None, "missing ux_passages_edition_sequence"
    assert seq_idx[1] is True
    assert "WHERE (sequence_number IS NOT NULL)" in seq_idx[0]


def test_revision_number_unique_per_passage(db_engine):
    with db_engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT conname FROM pg_constraint "
                "WHERE conrelid = 'public.passage_revisions'::regclass "
                "AND contype = 'u' AND conname = 'uq_revisions_passage_number'"
            )
        ).scalar()
    assert row == "uq_revisions_passage_number"


def test_delete_of_edition_referenced_by_passage_is_restricted(db_engine):
    """Section 7 test 15 / acceptance A: FK RESTRICT protects provenance chains.

    Creates its own fixture rows and removes them afterwards.
    """
    marker = uuid.uuid4().hex
    with db_engine.begin() as conn:
        source_id = conn.execute(
            text(
                "INSERT INTO literary_sources (canonical_title, source_status) "
                "VALUES (:t, 'draft') RETURNING id"
            ),
            {"t": f"ZZTEST fk {marker}"},
        ).scalar_one()
        edition_id = conn.execute(
            text(
                "INSERT INTO source_editions (source_id, edition_title, edition_type) "
                "VALUES (:s, 'FK fixture edition', 'other') RETURNING id"
            ),
            {"s": source_id},
        ).scalar_one()
        conn.execute(
            text(
                "INSERT INTO passages (source_edition_id, locator, original_text) "
                "VALUES (:e, 'p.1', :txt)"
            ),
            {"e": edition_id, "txt": f"fixture text {marker}"},
        )
    try:
        # pytest.raises sits OUTSIDE the transaction so the failed DELETE
        # rolls back cleanly (an aborted transaction must never be committed).
        with pytest.raises(IntegrityError):
            with db_engine.begin() as conn:
                conn.execute(
                    text("DELETE FROM source_editions WHERE id = :e"),
                    {"e": edition_id},
                )
        with pytest.raises(IntegrityError):
            with db_engine.begin() as conn:
                conn.execute(
                    text("DELETE FROM literary_sources WHERE id = :s"),
                    {"s": source_id},
                )
    finally:
        with db_engine.begin() as conn:
            conn.execute(
                text("DELETE FROM passages WHERE source_edition_id = :e"),
                {"e": edition_id},
            )
            conn.execute(
                text("DELETE FROM source_editions WHERE id = :e"),
                {"e": edition_id},
            )
            conn.execute(
                text("DELETE FROM literary_sources WHERE id = :s"),
                {"s": source_id},
            )
