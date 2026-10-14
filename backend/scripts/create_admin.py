"""Bootstrap a local administrator account from the command line.

Required by API_CONTRACT.md section 2 ("The first admin is bootstrapped
through a documented local CLI command, not through a public endpoint") and
DATABASE_SCHEMA.md section 6 step 2. There is deliberately no registration
endpoint; this script is the secure local creation path.

Usage (from backend/, after `alembic upgrade head`):

    python scripts/create_admin.py --username alice \\
        --email alice@local.test --display-name "Alice"

The password is read from an interactive prompt, or from the
MEYNOOL_ADMIN_PASSWORD environment variable when no TTY is available. It is
never accepted as a command-line argument (argv is visible to other local
processes) and is never logged or echoed.

Exit codes: 0 created, 1 rejected (validation/duplicate), 2 password missing.
"""
from __future__ import annotations

import argparse
import getpass
import os
import sys

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db import engine
from app.security import hash_password

PASSWORD_ENV_VAR = "MEYNOOL_ADMIN_PASSWORD"


def _read_password() -> str | None:
    if sys.stdin.isatty():
        first = getpass.getpass("Password for the new administrator: ")
        second = getpass.getpass("Repeat password: ")
        if first != second:
            print("Passwords do not match.", file=sys.stderr)
            return None
        return first or None
    value = os.environ.get(PASSWORD_ENV_VAR)
    if not value:
        print(
            f"No TTY: set {PASSWORD_ENV_VAR} to supply the password "
            "(never pass passwords as command-line arguments).",
            file=sys.stderr,
        )
        return None
    return value


def _validate(username: str, email: str, display_name: str) -> list[str]:
    errors = []
    if not 3 <= len(username) <= 80:
        errors.append("username must be 3-80 characters (users table check)")
    if "@" not in email or len(email) > 254:
        errors.append("email must be a plausible address up to 254 characters")
    if not 1 <= len(display_name) <= 160:
        errors.append("display_name must be 1-160 characters (users table check)")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument(
        "--role",
        choices=("admin",),
        default="admin",
        help="Bootstrap creates administrators only; other roles are created by admins via POST /admin/users.",
    )
    args = parser.parse_args()

    problems = _validate(args.username, args.email, args.display_name)
    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        return 1

    password = _read_password()
    if not password:
        return 2

    try:
        with engine.begin() as conn:
            existing_admin = conn.execute(
                text(
                    "SELECT count(*) FROM users "
                    "WHERE role = 'admin' AND status = 'active'"
                )
            ).scalar()
            user_id = conn.execute(
                text(
                    "INSERT INTO users (username, email, display_name, password_hash, "
                    "role, status, must_reset_password) "
                    "VALUES (:u, :e, :d, :h, 'admin', 'active', false) RETURNING id"
                ),
                {
                    "u": args.username,
                    "e": args.email,
                    "d": args.display_name,
                    "h": hash_password(password),
                },
            ).scalar_one()
    except IntegrityError:
        print(
            "error: username or email already exists (unique constraint)",
            file=sys.stderr,
        )
        return 1
    finally:
        engine.dispose()

    first = "First administrator" if existing_admin == 0 else "Administrator"
    print(f"{first} created: {args.username} ({user_id}) role=admin status=active")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
