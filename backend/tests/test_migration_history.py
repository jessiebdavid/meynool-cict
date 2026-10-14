"""Script-level migration chain checks (no database connection required).

Sprint requirement: migration 0001 and its history must be preserved. These
tests read Alembic's script directory to pin the lineage explicitly, so a
rebase that silently re-parents or rewrites 0001 fails here without needing
a live database.
"""
from __future__ import annotations

from pathlib import Path

from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _script_directory() -> ScriptDirectory:
    cfg = AlembicConfig(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return ScriptDirectory.from_config(cfg)


def test_migration_chain_preserves_0001_history():
    script = _script_directory()
    revisions = {rev.revision: rev for rev in script.walk_revisions()}

    assert set(revisions) == {"0001", "0002", "0003"}, (
        f"unexpected revision set: {sorted(revisions)}"
    )
    # Lineage per DATABASE_SCHEMA.md section 6: 0001 <- 0002 <- 0003.
    assert revisions["0001"].down_revision is None, "0001 must remain the root"
    assert revisions["0002"].down_revision == "0001"
    assert revisions["0003"].down_revision == "0002"
    assert script.get_current_head() == "0003"


def test_migration_filenames_match_documented_names():
    versions_dir = BACKEND_DIR / "alembic" / "versions"
    names = sorted(p.name for p in versions_dir.glob("*.py"))
    assert names == [
        "0001_extensions_and_types.py",
        "0002_users_and_auth_sessions.py",
        "0003_literary_catalogue.py",
    ], f"unexpected migration files: {names}"
