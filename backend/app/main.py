import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.exceptions import HTTPException as StarletteHTTPException
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

# --- Contract-wide request ID and error envelope (API_CONTRACT.md 1.1/1.2) ---
_ERROR_CODES = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    503: "DEPENDENCY_UNAVAILABLE",
}


def _request_id(request: Request) -> str:
    return (
        getattr(request.state, "request_id", None)
        or request.headers.get("X-Request-ID")
        or uuid.uuid4().hex
    )


def _error_response(
    status_code: int, code: str, message: str, request: Request
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": _request_id(request),
            }
        },
    )


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    incoming = request.headers.get("X-Request-ID")
    request.state.request_id = (
        incoming if incoming and len(incoming) <= 128 else uuid.uuid4().hex
    )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


# Register for both classes: endpoints raise fastapi.HTTPException, while the
# router raises starlette.HTTPException for unmatched routes (404/405).
@app.exception_handler(StarletteHTTPException)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = _ERROR_CODES.get(
        exc.status_code,
        "INTERNAL_ERROR" if exc.status_code >= 500 else "VALIDATION_ERROR",
    )
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": _request_id(request),
            }
        },
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _error_response(422, "VALIDATION_ERROR", "Request validation failed", request)


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
