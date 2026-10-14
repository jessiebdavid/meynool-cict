# Meynool API Starter

Only `/api/v1/health` and `/api/v1/ready` are implemented at this stage. The full routes in `../API_CONTRACT.md` are specifications, not existing endpoints.

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
default URL in `app/main.py` (`127.0.0.1:5432/meynool`). `DATABASE_URL` may
contain a password, so it belongs only in `.env`, never in source control.
Optional: `DATABASE_CONNECT_TIMEOUT` (seconds, default `5`) bounds the
readiness probe's connection attempt.
