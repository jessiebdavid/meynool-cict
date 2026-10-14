"""Shared database engine and request-scoped connection dependency."""
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": settings.database_connect_timeout},
)


def get_db() -> Iterator:
    """Yield a connection; commit on success, roll back on error."""
    with engine.connect() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
