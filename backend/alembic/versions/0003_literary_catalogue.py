"""literary source catalogue tables (DATABASE_SCHEMA.md section 3.2,
section 6 step 0003)

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-14

Creates literary_sources, source_editions, passages, passage_revisions and
interpretations with their table-level integrity constraints, including the
two partial unique indexes on passages required verbatim by section 3.2.

The section 4 search/performance indexes for these tables (GIN full-text,
author, year, status lookups) belong to 0013_search_and_performance_indexes
per section 6 and are intentionally not created here.

Reversible: downgrade() drops exactly the tables created by this revision,
children first, and never touches 0001's extensions/enums or 0002's
account tables. Source provenance columns (provenance_notes, source_url,
archive_or_repository, source_reference, identifiers) are preserved as
documented; no data is written by this migration.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum types created by 0001; referenced here without re-creation.
_SOURCE_STATUS = postgresql.ENUM(
    "draft", "verified", "disputed", "withdrawn", name="source_status", create_type=False
)
_PASSAGE_STATUS = postgresql.ENUM(
    "draft", "reviewed", "verified", "disputed", name="passage_status", create_type=False
)


def upgrade() -> None:
    op.create_table(
        "literary_sources",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("canonical_title", sa.Text(), nullable=False),
        sa.Column("title_ta", sa.Text(), nullable=True),
        sa.Column("title_en", sa.Text(), nullable=True),
        sa.Column("attributed_author", sa.Text(), nullable=True),
        sa.Column("attribution_confidence", sa.Text(), nullable=False, server_default=sa.text("'unknown'")),
        sa.Column("genre", sa.Text(), nullable=True),
        sa.Column("tradition_or_collection", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_status", _SOURCE_STATUS, nullable=False, server_default=sa.text("'draft'")),
        sa.Column("provenance_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id", name="pk_literary_sources"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL", name="fk_sources_created_by"),
        sa.CheckConstraint(
            "attribution_confidence IN ('unknown','traditional','probable','disputed','established')",
            name="ck_sources_attribution_confidence",
        ),
    )

    op.create_table(
        "source_editions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("edition_title", sa.Text(), nullable=False),
        sa.Column("editor_or_publisher", sa.Text(), nullable=True),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("publication_year_end", sa.Integer(), nullable=True),
        sa.Column("edition_type", sa.Text(), nullable=False),
        sa.Column("language_code", sa.Text(), nullable=False, server_default=sa.text("'ta'")),
        sa.Column("identifier", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("archive_or_repository", sa.Text(), nullable=True),
        sa.Column("rights_status", sa.Text(), nullable=False, server_default=sa.text("'unknown'")),
        sa.Column("rights_notes", sa.Text(), nullable=True),
        sa.Column("content_checksum", sa.Text(), nullable=True),
        sa.Column("edition_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id", name="pk_source_editions"),
        sa.ForeignKeyConstraint(
            ["source_id"], ["literary_sources.id"], ondelete="RESTRICT", name="fk_editions_source"
        ),
        sa.CheckConstraint(
            "edition_type IN ('manuscript','critical_edition','printed_edition','digital_transcription','translation','other')",
            name="ck_editions_type",
        ),
        sa.CheckConstraint(
            "rights_status IN ('public_domain','licensed','permission_required','restricted','unknown')",
            name="ck_editions_rights_status",
        ),
        sa.CheckConstraint(
            "publication_year IS NULL OR publication_year BETWEEN 1 AND 3000",
            name="ck_editions_publication_year",
        ),
        sa.CheckConstraint(
            "publication_year_end IS NULL OR publication_year IS NULL OR publication_year_end >= publication_year",
            name="ck_editions_publication_year_range",
        ),
    )

    op.create_table(
        "passages",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("source_edition_id", sa.Uuid(), nullable=False),
        sa.Column("passage_code", sa.Text(), nullable=True),
        sa.Column("sequence_number", sa.Integer(), nullable=True),
        sa.Column("locator", sa.Text(), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=True),
        sa.Column("language_code", sa.Text(), nullable=False, server_default=sa.text("'ta'")),
        sa.Column("transcription_method", sa.Text(), nullable=False, server_default=sa.text("'unknown'")),
        sa.Column("transcription_confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("status", _PASSAGE_STATUS, nullable=False, server_default=sa.text("'draft'")),
        sa.Column("text_checksum", sa.Text(), nullable=True),
        sa.Column("editorial_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id", name="pk_passages"),
        sa.ForeignKeyConstraint(
            ["source_edition_id"], ["source_editions.id"], ondelete="RESTRICT", name="fk_passages_edition"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL", name="fk_passages_created_by"),
        sa.CheckConstraint(
            "transcription_method IN ('manual','ocr','published_transcription','mixed','unknown')",
            name="ck_passages_transcription_method",
        ),
        sa.CheckConstraint("length(original_text) > 0", name="ck_passages_original_text_nonempty"),
        sa.CheckConstraint(
            "transcription_confidence IS NULL OR transcription_confidence BETWEEN 0 AND 1",
            name="ck_passages_transcription_confidence",
        ),
    )
    # Section 3.2: partial unique indexes (NOT plain constraints).
    op.create_index(
        "ux_passages_edition_passage_code",
        "passages",
        ["source_edition_id", "passage_code"],
        unique=True,
        postgresql_where=sa.text("passage_code IS NOT NULL"),
    )
    op.create_index(
        "ux_passages_edition_sequence",
        "passages",
        ["source_edition_id", "sequence_number"],
        unique=True,
        postgresql_where=sa.text("sequence_number IS NOT NULL"),
    )

    op.create_table(
        "passage_revisions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("passage_id", sa.Uuid(), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("original_text_snapshot", sa.Text(), nullable=False),
        sa.Column("normalized_text_snapshot", sa.Text(), nullable=True),
        sa.Column("change_reason", sa.Text(), nullable=False),
        sa.Column("changed_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id", name="pk_passage_revisions"),
        sa.ForeignKeyConstraint(
            ["passage_id"], ["passages.id"], ondelete="RESTRICT", name="fk_revisions_passage"
        ),
        sa.ForeignKeyConstraint(
            ["changed_by"], ["users.id"], ondelete="SET NULL", name="fk_revisions_changed_by"
        ),
        sa.UniqueConstraint("passage_id", "revision_number", name="uq_revisions_passage_number"),
        sa.CheckConstraint("revision_number > 0", name="ck_revisions_number_positive"),
        sa.CheckConstraint("length(change_reason) > 0", name="ck_revisions_change_reason_nonempty"),
    )

    op.create_table(
        "interpretations",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("passage_id", sa.Uuid(), nullable=False),
        sa.Column("interpretation_type", sa.Text(), nullable=False),
        sa.Column("language_code", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("author_or_model", sa.Text(), nullable=True),
        sa.Column("model_version", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'unreviewed'")),
        sa.Column("source_reference", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id", name="pk_interpretations"),
        sa.ForeignKeyConstraint(
            ["passage_id"], ["passages.id"], ondelete="RESTRICT", name="fk_interpretations_passage"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], ondelete="SET NULL", name="fk_interpretations_created_by"
        ),
        sa.CheckConstraint(
            "interpretation_type IN ('translation','literal_gloss','commentary','historical_context','scholarly_interpretation','model_generated')",
            name="ck_interpretations_type",
        ),
        sa.CheckConstraint(
            "status IN ('unreviewed','reviewed','accepted','rejected','disputed')",
            name="ck_interpretations_status",
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="ck_interpretations_confidence",
        ),
        sa.CheckConstraint("length(body) > 0", name="ck_interpretations_body_nonempty"),
    )


def downgrade() -> None:
    # Children first; only objects created by this revision.
    op.drop_table("interpretations")
    op.drop_table("passage_revisions")
    op.drop_table("passages")  # drops ux_passages_edition_* partial indexes
    op.drop_table("source_editions")
    op.drop_table("literary_sources")
