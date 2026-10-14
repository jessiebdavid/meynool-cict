"""users + auth_sessions tables and account indexes
(DATABASE_SCHEMA.md section 3.1, section 4 "Accounts and sessions",
section 6 step 0002)

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-14

No credentials are seeded here: section 6 step 2 requires the first
administrator to be bootstrapped through a secure local CLI command
(backend/scripts/create_admin.py), never through a migration or a public
endpoint.

Reversible: downgrade() drops exactly the tables and indexes this revision
created, in FK-safe order, and never touches 0001's extensions or enum
types (the columns below reuse the account_role/account_status types
created by 0001 via create_type=False).
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("username", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM("admin", "researcher", "reviewer", name="account_role", create_type=False),
            nullable=False,
            server_default=sa.text("'researcher'"),
        ),
        sa.Column(
            "status",
            postgresql.ENUM("active", "disabled", "pending", name="account_status", create_type=False),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("must_reset_password", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL", name="fk_users_created_by"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint("length(username) BETWEEN 3 AND 80", name="ck_users_username_length"),
        sa.CheckConstraint("length(display_name) BETWEEN 1 AND 160", name="ck_users_display_name_length"),
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_hash", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_auth_sessions"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name="fk_auth_sessions_user"),
        sa.UniqueConstraint("token_hash", name="uq_auth_sessions_token_hash"),
        sa.CheckConstraint("expires_at > created_at", name="ck_auth_sessions_expiry"),
    )

    # Account indexes (section 4, "Accounts and sessions"). The lower()
    # unique indexes are expression indexes; section 6 step 2 assigns them
    # to this migration.
    op.execute("CREATE UNIQUE INDEX ux_users_username_ci ON users (lower(username))")
    op.execute("CREATE UNIQUE INDEX ux_users_email_ci ON users (lower(email))")
    op.create_index("ix_users_role_status", "users", ["role", "status"])
    op.create_index("ix_sessions_user_expiry", "auth_sessions", ["user_id", "expires_at"])
    op.create_index(
        "ix_sessions_expiry_active",
        "auth_sessions",
        ["expires_at"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_sessions_expiry_active", table_name="auth_sessions")
    op.drop_index("ix_sessions_user_expiry", table_name="auth_sessions")
    op.drop_index("ix_users_role_status", table_name="users")
    op.drop_index("ux_users_email_ci", table_name="users")
    op.drop_index("ux_users_username_ci", table_name="users")
    # Children before parents; only objects created by this revision.
    op.drop_table("auth_sessions")
    op.drop_table("users")
