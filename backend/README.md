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
