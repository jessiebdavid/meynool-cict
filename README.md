# Meynool — Project Starter & Team Handoff

**Brand:** மெய்நூல் · **Meynool**  
**Formal descriptor:** Tamil Literary Knowledge and Scientific Evidence Intelligence Platform  
**Tagline:** From Ancient Texts to Evidence-Based Discovery.

Meynool is a local-first research platform for preserving traceable Tamil literary sources and examining possible relationships to modern science. It must distinguish what a text says, what scholars interpret, what modern research supports, and what remains a hypothesis.

## What is in this ZIP?

This is a **starter repository**, not a finished AI product. It includes:

- `frontend/`: React + Vite + TypeScript UI starter with an honest empty research dashboard and API health indicator.
- `backend/`: FastAPI starter with health/readiness endpoints and an initial test.
- `docker-compose.yml`: local PostgreSQL with pgvector image.
- `.env.example`: configuration template with placeholders only.
- `PROJECT_REQUIREMENTS.md`: product requirements and safety/evidence rules.
- `DATABASE_SCHEMA.md`: canonical database design baseline. **Do not execute `vector(N)` placeholders literally.**
- `API_CONTRACT.md`: REST API integration baseline.
- `openapi.yaml`: companion draft; validate against the actual FastAPI app before release.
- `TASK_OWNERSHIP.md`: task split and change-control rules.
- `ACCEPTANCE_TESTS.md`: initial acceptance criteria.
- `docs/`: setup, status, and collaboration notes.

## Recommended work split

**Project owner:** UI/UX, 1D–4D analysis design, AI orchestration, evidence/hypothesis review flows, integration and acceptance.  
**Backend teammate:** PostgreSQL migrations, source/provenance ingestion, PubMed/Europe PMC integration, chunking/embeddings, hybrid retrieval, ingestion jobs, API routes and backend tests.

Both people work in this same repository and follow the shared contracts. Propose changes before altering the schema or API contract.

## Quick start

### 1. Requirements

- Python 3.11 or newer
- Node.js 20 or newer and npm
- Docker Desktop (recommended for PostgreSQL + pgvector)
- Git (recommended)

### 2. Configure environment

Copy `.env.example` to `.env` and change the placeholder values for your machine. Do not commit `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

### 3. Start PostgreSQL

```bash
docker compose up -d db
```

The database container starts with an empty database. The full schema migrations still need to be implemented by the backend contributor.

### 4. Start the backend

Windows PowerShell:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

macOS/Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for the starter API docs. The starter health endpoint does not claim that database ingestion or AI features are implemented.

### 5. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL Vite prints, usually `http://127.0.0.1:4319`.

### 6. Run backend tests

From `backend/` with its virtual environment activated:

```bash
pytest
```

## Important project rules

1. RAG/retrieval comes before any decision to fine-tune a model.
2. Never invent Tamil quotations, source attributions, publication identifiers, evidence, dates, instruments, procedures or performance metrics.
3. Keep original text, translation, scholarly interpretation, AI-generated analysis and modern scientific findings distinct.
4. Treat historical surgical procedures and instruments as documentary research—not clinical instructions.
5. Hallucination percentages require a human-reviewed test set, defined denominator and documented scoring method.
6. The 1D–4D labels are Meynool's analysis framework, not literal physical dimensions.
7. Store only scientific content permitted by the source's license and provider terms.
8. Do not put passwords, API keys or session secrets in source control.

See `docs/START_HERE.md` for the first-day checklist and `docs/IMPLEMENTATION_STATUS.md` for what is and is not implemented.
