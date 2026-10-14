"""Application settings, shared by the API, Alembic and CLI helpers.

DATABASE_URL comes from the environment / repository-root ../.env; when
absent, the built-in local default matches .env.example.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:local_dev_change_me@127.0.0.1:5432/meynool"
    # Bound the readiness probe so an unreachable database fails fast instead of
    # hanging the worker. Seconds; overridable via DATABASE_CONNECT_TIMEOUT.
    database_connect_timeout: int = 5
    # Opaque session lifetime for cookie auth (API_CONTRACT.md section 2).
    session_ttl_days: int = 7
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()
