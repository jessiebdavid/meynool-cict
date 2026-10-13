from fastapi import FastAPI, HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:local_dev_change_me@127.0.0.1:5432/meynool"
    # Bound the readiness probe so an unreachable database fails fast instead of
    # hanging the worker. Seconds; overridable via DATABASE_CONNECT_TIMEOUT.
    database_connect_timeout: int = 5
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()
app = FastAPI(
    title="Meynool Research Platform API",
    version="0.1.0",
    description=(
        "Starter API for a source-grounded Tamil literature and scientific evidence platform. "
        "Only implemented endpoints are advertised here; the full contract is in ../API_CONTRACT.md."
    ),
)


@app.get("/api/v1/health", tags=["Health"])
def health() -> dict[str, str]:
    """Process health only; does not imply database or AI features are ready."""
    return {"status": "ok", "service": "meynool-api", "stage": "starter"}


@app.get("/api/v1/ready", tags=["Health"])
def readiness() -> dict[str, str]:
    """Check whether the configured PostgreSQL database is reachable."""
    try:
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": settings.database_connect_timeout},
        )
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
    except (SQLAlchemyError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Database is not ready; check DATABASE_URL and PostgreSQL.") from exc
    return {"status": "ready", "database": "reachable", "schema": "not_verified"}
