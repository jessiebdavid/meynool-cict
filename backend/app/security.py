"""Password hashing, opaque session tokens and auth dependencies.

Implements API_CONTRACT.md sections 1.3/2 minimally:
- PBKDF2-SHA256 password hashes (stdlib, no new dependency).
- Opaque session tokens; only their SHA-256 hash is stored (schema 3.1).
- Cookie name `session`, HttpOnly + SameSite=strict, set by the login route.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy import text

from app.config import settings
from app.db import get_db

PBKDF2_ITERATIONS = 600_000
SESSION_COOKIE = "session"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode(),
        base64.urlsafe_b64encode(digest).decode(),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = stored.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64)
        expected = base64.urlsafe_b64decode(digest_b64)
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, int(iterations)
        )
        return hmac.compare_digest(candidate, expected)
    except (ValueError, TypeError):
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(conn, user_id: str) -> str:
    """Create an auth_sessions row; returns the raw token (never stored)."""
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=settings.session_ttl_days)
    conn.execute(
        text(
            "INSERT INTO auth_sessions (id, user_id, token_hash, expires_at) "
            "VALUES (gen_random_uuid(), :uid, :th, :exp)"
        ),
        {"uid": uuid.UUID(user_id), "th": _token_hash(token), "exp": expires},
    )
    return token


def revoke_session(conn, token: str) -> None:
    conn.execute(
        text(
            "UPDATE auth_sessions SET revoked_at = now() "
            "WHERE token_hash = :th AND revoked_at IS NULL"
        ),
        {"th": _token_hash(token)},
    )


_USER_COLUMNS = (
    "u.id, u.username, u.email, u.display_name, "
    "u.role::text AS role, u.status::text AS status, u.must_reset_password"
)


def require_session_token(request: Request) -> str:
    """Raw session cookie or 401 — runs before any database connection.

    Solved ahead of get_db in get_current_user's signature so an
    unauthenticated request gets the contract 401 envelope even when the
    database is unreachable.
    """
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    return token


def get_current_user(
    token: str = Depends(require_session_token), conn=Depends(get_db)
) -> dict:
    """Authenticated, active user or 401 in the contract error envelope."""
    row = conn.execute(
        text(
            f"SELECT {_USER_COLUMNS} FROM auth_sessions s "
            "JOIN users u ON u.id = s.user_id "
            "WHERE s.token_hash = :th AND s.revoked_at IS NULL "
            "AND s.expires_at > now() AND u.status = 'active'"
        ),
        {"th": _token_hash(token)},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    user = dict(row)
    user["id"] = str(user["id"])  # UUID -> JSON string (contract 1.1)
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


def require_researcher(user: dict = Depends(get_current_user)) -> dict:
    """Contract section 4: researcher or curator (admin) may create interpretations."""
    if user["role"] not in ("admin", "researcher"):
        raise HTTPException(status_code=403, detail="Researcher privileges required")
    return user
