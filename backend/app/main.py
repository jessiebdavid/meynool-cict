import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import InterfaceError, OperationalError, SQLAlchemyError

from app.config import settings
from app.routes_auth import router as auth_router
from app.routes_catalogue import router as catalogue_router

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


_UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


@app.middleware("http")
async def csrf_origin_check(request: Request, call_next):
    """Minimal CSRF control for cookie auth (API_CONTRACT.md section 2).

    SameSite=strict cookies are the primary defense; this additionally
    rejects mutating browser requests whose Origin is not this host.
    """
    origin = request.headers.get("Origin")
    if request.method in _UNSAFE_METHODS and origin:
        expected = f"{request.url.scheme}://{request.url.netloc}"
        if origin.rstrip("/") != expected:
            return _error_response(
                403, "FORBIDDEN", "Cross-origin request rejected", request
            )
    return await call_next(request)


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


@app.exception_handler(OperationalError)
@app.exception_handler(InterfaceError)
async def database_unavailable_handler(
    request: Request, exc: OperationalError | InterfaceError
):
    """API_CONTRACT.md 1.2: dependency failures use the envelope, never a
    stack trace — an unreachable database is 503 DEPENDENCY_UNAVAILABLE."""
    return _error_response(
        503,
        "DEPENDENCY_UNAVAILABLE",
        "A required dependency is not available; check /api/v1/ready",
        request,
    )


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    """Other database errors still return the contract envelope (1.2)."""
    return _error_response(
        500, "INTERNAL_ERROR", "Request failed", request
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


app.include_router(auth_router)
app.include_router(catalogue_router)
