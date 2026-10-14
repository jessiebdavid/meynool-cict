"""Authentication routes — API_CONTRACT.md section 2.

- POST /api/v1/auth/login  — 200 {user}, 401 invalid credentials, 403 inactive account
- POST /api/v1/auth/logout — 204, revokes the current session, 401 without one
- GET  /api/v1/auth/me     — 200 public user representation, 401 otherwise

Session handling follows section 2 literally: opaque random token, only its
SHA-256 hash stored, HttpOnly + SameSite=strict cookie, never returned in
JSON. CSRF for cookie auth is handled by the Origin check middleware in
main.py plus SameSite=strict.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import text

from app.config import settings
from app.db import get_db
from app.schemas import LoginRequest, LoginResponse, UserPublic
from app.security import (
    SESSION_COOKIE,
    create_session,
    get_current_user,
    hash_password,
    require_session_token,
    revoke_session,
    verify_password,
)

router = APIRouter(prefix="/api/v1", tags=["Auth"])

_COOKIE_KWARGS = {
    "httponly": True,
    "samesite": "strict",
    # Local-first: Secure would block the cookie over plain-http development.
    "secure": settings.app_env == "production",
}

# Equalizes timing for unknown usernames (built lazily: PBKDF2 is expensive).
_DUMMY_HASH: str | None = None


def _dummy_hash() -> str:
    global _DUMMY_HASH
    if _DUMMY_HASH is None:
        _DUMMY_HASH = hash_password("timing-equalizer-not-a-real-password")
    return _DUMMY_HASH


def _find_user(conn, username_or_email: str):
    """Deterministic lookup: exact username first (ci), then email (ci)."""
    row = conn.execute(
        text(
            "SELECT id, username, email, display_name, password_hash, "
            "role::text AS role, status::text AS status "
            "FROM users WHERE lower(username) = lower(:u)"
        ),
        {"u": username_or_email},
    ).mappings().first()
    if row is not None:
        return row
    return conn.execute(
        text(
            "SELECT id, username, email, display_name, password_hash, "
            "role::text AS role, status::text AS status "
            "FROM users WHERE lower(email) = lower(:u)"
        ),
        {"u": username_or_email},
    ).mappings().first()


def _public_user(row) -> dict:
    # Only these fields; password_hash/session material never leaves this module.
    return {
        "id": str(row["id"]),
        "username": row["username"],
        "email": row["email"],
        "display_name": row["display_name"],
        "role": row["role"],
        "status": row["status"],
    }


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, conn=Depends(get_db)) -> dict:
    row = _find_user(conn, payload.username_or_email)
    # Always verify a hash so unknown-user and wrong-password cost the same.
    password_ok = verify_password(
        payload.password, row["password_hash"] if row is not None else _dummy_hash()
    )
    if row is None or not password_ok:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Contract: 401 invalid credentials; 403 disabled/pending accounts.
    if row["status"] != "active":
        raise HTTPException(status_code=403, detail="Account is not active")
    token = create_session(conn, str(row["id"]))
    conn.execute(
        text("UPDATE users SET last_login_at = now() WHERE id = :id"),
        {"id": str(row["id"])},
    )
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=settings.session_ttl_days * 86400,
        **_COOKIE_KWARGS,
    )
    return {"user": _public_user(row)}


@router.post("/auth/logout", status_code=204)
def logout(
    response: Response,
    token: str = Depends(require_session_token),
    conn=Depends(get_db),
) -> None:
    revoke_session(conn, token)
    response.delete_cookie(key=SESSION_COOKIE, **_COOKIE_KWARGS)


@router.get("/auth/me", response_model=UserPublic)
def me(user: dict = Depends(get_current_user)) -> dict:
    return {field: user[field] for field in UserPublic.model_fields}
