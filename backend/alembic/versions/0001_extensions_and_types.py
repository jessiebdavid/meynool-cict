"""extensions + enumerated types (DATABASE_SCHEMA.md section 2 and 6, step 0001)

Revision ID: 0001
Revises:
Create Date: 2026-10-13

Installs the required PostgreSQL extensions (pgcrypto, vector) and creates the
controlled-vocabulary enum types. No application tables yet; those follow in
0002+ per the documented migration order.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Controlled vocabularies, exactly as defined in DATABASE_SCHEMA.md section 2.
_ENUMS: dict[str, tuple[str, ...]] = {
    "account_role": ("admin", "researcher", "reviewer"),
    "account_status": ("active", "disabled", "pending"),
    "source_status": ("draft", "verified", "disputed", "withdrawn"),
    "passage_status": ("draft", "reviewed", "verified", "disputed"),
    "evidence_relation": ("supports", "contradicts", "qualifies", "contextualizes"),
    "review_decision": ("approve", "revise", "reject", "needs_expert"),
    "ingestion_status": ("queued", "running", "succeeded", "partial", "failed", "cancelled"),
    "hypothesis_status": ("proposed", "under_review", "supported", "contradicted", "inconclusive", "withdrawn"),
}


def upgrade() -> None:
    # Extensions first (schema section 2: "Apply before table creation").
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    for name, values in _ENUMS.items():
        sa.Enum(*values, name=name).create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    # Drop enum types (reverse of creation). Extensions are left installed:
    # dropping shared extensions can fail if anything else depends on them,
    # and pgcrypto/vector are harmless to retain.
    for name in _ENUMS:
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
