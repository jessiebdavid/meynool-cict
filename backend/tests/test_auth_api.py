"""Contract tests for the authentication routes (API_CONTRACT.md section 2).

Tests marked ``db_integration`` insert throwaway accounts into the live
database and are skipped honestly when PostgreSQL is unreachable; the
unmarked tests must pass with no database at all (the session-cookie check
is designed to run before any connection is attempted).
"""
from __future__ import annotations

import hashlib
import uuid

import pytest
from sqlalchemy import text


# --------------------------------------------------------------------------
# No database required: unauthenticated envelope behavior
# --------------------------------------------------------------------------


def test_me_without_session_cookie_returns_401_envelope(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    error = response.json()["error"]
    assert error["code"] == "UNAUTHORIZED"
    assert error["request_id"]
    assert response.headers["X-Request-ID"] == error["request_id"]


def test_logout_without_session_cookie_returns_401_envelope(client):
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


# --------------------------------------------------------------------------
# Live database: login / me / logout lifecycle
# --------------------------------------------------------------------------


@pytest.mark.db_integration
def test_login_returns_public_user_and_sets_hardened_cookie(
    client, seed_user, db_engine, test_password
):
    username = seed_user("t_login_ok")
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": test_password},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    user = body["user"]
    assert user["username"] == username
    assert user["role"] == "researcher"
    assert user["status"] == "active"
    # Contract 1.1: never expose password material or session tokens.
    assert "password_hash" not in response.text
    assert test_password not in response.text
    assert set(user) == {"id", "username", "email", "display_name", "role", "status"}

    # HttpOnly + SameSite=strict cookie carrying the opaque token.
    assert client.cookies.get("session")
    set_cookies = [
        (k.lower(), v) for k, v in response.headers.multi_items() if k.lower() == "set-cookie"
    ]
    cookie_header = " ".join(v for _, v in set_cookies).lower()
    assert "httponly" in cookie_header
    assert "samesite=strict" in cookie_header

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == username
    # Session token never appears in JSON.
    assert client.cookies.get("session") not in me.text


@pytest.mark.db_integration
def test_logout_revokes_session_and_clears_cookie(client, seed_user, test_password):
    username = seed_user("t_logout")
    client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": test_password},
    )
    assert client.get("/api/v1/auth/me").status_code == 200

    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    assert response.content == b""

    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.cookies.get("session") is None


@pytest.mark.db_integration
@pytest.mark.parametrize(
    "username_or_email,password,expected_status,expected_code",
    [
        ("t_wrong_pass_user", "definitely-not-the-password", 401, "UNAUTHORIZED"),
        ("t_no_such_user_at_all", "whatever-it-is", 401, "UNAUTHORIZED"),
    ],
)
def test_login_with_bad_credentials_returns_401(
    client, seed_user, username_or_email, password, expected_status, expected_code
):
    if username_or_email == "t_wrong_pass_user":
        seed_user(username_or_email)
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username_or_email, "password": password},
    )
    assert response.status_code == expected_status
    assert response.json()["error"]["code"] == expected_code
    assert client.cookies.get("session") is None


@pytest.mark.db_integration
@pytest.mark.parametrize("status", ["disabled", "pending"])
def test_login_to_inactive_account_returns_403(client, seed_user, status, test_password):
    username = seed_user(f"t_inactive_{status}", status=status)
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": test_password},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
    assert client.cookies.get("session") is None


@pytest.mark.db_integration
def test_login_accepts_email_and_is_case_insensitive(client, seed_user, test_password):
    username = seed_user("t_MixedCase")
    by_email = client.post(
        "/api/v1/auth/login",
        json={
            "username_or_email": f"{username.upper()}@EXAMPLE.TEST",
            "password": test_password,
        },
    )
    assert by_email.status_code == 200
    client.post("/api/v1/auth/logout")
    by_username = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username.upper(), "password": test_password},
    )
    assert by_username.status_code == 200


@pytest.mark.db_integration
def test_login_with_malformed_payload_returns_422_envelope(client, db_engine):
    # db_engine is the skip gate: body validation happens after the DB
    # dependency runs, so this check is only meaningful with PostgreSQL up.
    response = client.post("/api/v1/auth/login", json={"username_only": "x"})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["request_id"]


@pytest.mark.db_integration
def test_expired_session_is_rejected(client, seed_user, db_engine):
    username = seed_user("t_expired")
    token = "expired-token-" + uuid.uuid4().hex
    _insert_session(
        db_engine,
        username,
        token,
        # CHECK (expires_at > created_at): a plausible old session that has since expired.
        created_at="now() - interval '3 days'",
        expires_at="now() - interval '1 day'",
    )
    response = client.get(
        "/api/v1/auth/me", headers={"Cookie": f"session={token}"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.db_integration
def test_revoked_session_is_rejected(client, seed_user, db_engine):
    username = seed_user("t_revoked")
    token = "revoked-token-" + uuid.uuid4().hex
    _insert_session(
        db_engine,
        username,
        token,
        revoked_at="now()",
    )
    response = client.get(
        "/api/v1/auth/me", headers={"Cookie": f"session={token}"}
    )
    assert response.status_code == 401


@pytest.mark.db_integration
def test_disabled_account_session_is_rejected(client, seed_user, db_engine, test_password):
    """Acceptance section E / schema section 7 test 13: disabled users cannot authenticate."""
    username = seed_user("t_disabled_after_login")
    login = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": test_password},
    )
    assert login.status_code == 200
    with db_engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET status = 'disabled' WHERE username = :u"),
            {"u": username},
        )
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def _insert_session(
    engine,
    username: str,
    raw_token: str,
    *,
    expires_at: str = "now() + interval '1 day'",
    created_at: str = "now()",
    revoked_at: str | None = None,
) -> None:
    """Insert an auth_sessions row for a raw token (only its hash is stored).

    The SQL fragments are literals from this test file, never user input.
    """
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    with engine.begin() as conn:
        user_id = conn.execute(
            text("SELECT id FROM users WHERE username = :u"), {"u": username}
        ).scalar_one()
        conn.execute(
            text(
                "INSERT INTO auth_sessions (id, user_id, token_hash, created_at, "
                "expires_at, revoked_at) VALUES (gen_random_uuid(), :uid, :th, "
                f"{created_at}, {expires_at}, {revoked_at or 'NULL'})"
            ),
            {"uid": user_id, "th": token_hash},
        )
