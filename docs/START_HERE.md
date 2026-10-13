# Start Here — Meynool

## Before coding

- [ ] Share this ZIP with the backend teammate.
- [ ] Both contributors install the requirements listed in the root README.
- [ ] Create one shared Git repository from this folder; agree on a branch/PR workflow.
- [ ] Treat `DATABASE_SCHEMA.md` and `API_CONTRACT.md` as the integration baselines.
- [ ] Keep the embedding model and vector dimension undecided until local tests establish a suitable model and dimension.
- [ ] Agree which source editions and licensed source files can legally be ingested.

## First tasks for the project owner

1. Run the frontend and backend starter locally.
2. Sketch and implement the source-search, source-detail, 1D–4D analysis, evidence review, and hypothesis-review screens.
3. Keep empty states honest; do not present invented source records or metrics as real.
4. Write acceptance examples for one known passage and a small, human-reviewed scientific evidence set.
5. Integrate only against agreed API request/response contracts.

## First tasks for the backend teammate

1. Implement migration tooling and a clean-database migration workflow.
2. Implement schema migrations from `DATABASE_SCHEMA.md`, documenting any constraints that cannot be enforced directly in SQL.
3. Implement API endpoints incrementally, starting with health, authentication, source catalogue, and ingestion jobs.
4. Add source provenance and permitted-content/licensing checks before ingestion.
5. Add scientific search through approved providers, then chunking, embeddings and hybrid retrieval.
6. Add tests and report completed endpoints, commands, known gaps and test results.

## Definition of an acceptable first milestone

- Frontend and API run locally.
- PostgreSQL starts locally.
- A migration creates the approved schema from an empty database.
- One explicitly licensed/approved Tamil source can be ingested with edition and passage provenance.
- One scientific record can be retrieved with a stable identifier and source link.
- Every displayed claim/evidence link is traceable; unavailable evidence is shown as unavailable, not invented.
