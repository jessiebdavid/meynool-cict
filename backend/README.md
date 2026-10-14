# Meynool API Starter

Implemented so far: `/api/v1/health`, `/api/v1/ready`, the authentication
routes of `API_CONTRACT.md` section 2 (`POST /auth/login`,
`POST /auth/logout`, `GET /auth/me`) and the full literary source catalogue
of section 4 (sources, editions, passages, interpretations, revisions — 13
operations). Everything else in `../API_CONTRACT.md` remains a specification,
not an existing endpoint.

Run from this directory after activating a virtual environment and installing `requirements.txt`:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Run tests:

```bash
pytest
```

The `.env` file is read from the repository root when running from `backend/`. Do not commit secrets. Readiness checks connectivity only; it does not verify that migrations or all required tables exist.

## Database configuration

The API and Alembic share one source of truth for the database URL:
`app.main.Settings` reads `DATABASE_URL` from the repository-root `.env`
(`env_file="../.env"`), and `alembic/env.py` imports that same `Settings`.
`alembic.ini` intentionally contains no URL or credentials, so
`alembic upgrade head` always targets the same database as the running API.

Local setup (from the repository root):

```bash
cp .env.example .env   # .env is gitignored; never commit it
# edit DATABASE_URL in .env if your PostgreSQL differs from the template default
```

If `.env` is absent, both the API and Alembic fall back to the built-in local
default URL in `app/config.py` (`127.0.0.1:5432/meynool`). `DATABASE_URL` may
contain a password, so it belongs only in `.env`, never in source control.
Optional: `DATABASE_CONNECT_TIMEOUT` (seconds, default `5`) bounds the
readiness probe's connection attempt.

## Migrations

```bash
alembic upgrade head      # 0001 -> 0002 (users/sessions) -> 0003 (catalogue)
alembic downgrade 0001    # reversible: drops only what 0002/0003 created
```

Index creation for catalog tables is intentionally deferred to migration
`0013_search_and_performance_indexes` (see `../DATABASE_SCHEMA.md` section 6);
`0002` includes the account/session indexes that section 6 step 2 assigns to it.

## Bootstrap the first administrator

There is no registration endpoint by contract. Create the first local admin
with the documented CLI command (from `backend/`, after `alembic upgrade head`):

```bash
python scripts/create_admin.py --username alice \
    --email alice@local.test --display-name "Alice"
```

The script prompts for the password on a TTY (or reads the
`MEYNOOL_ADMIN_PASSWORD` environment variable when run non-interactively);
passwords are never accepted as arguments and never logged. It stores only a
PBKDF2-SHA256 hash and creates the account as `role=admin, status=active`.
