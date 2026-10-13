# API specification reconciliation — Phase 2

**Scope:** Reconcile the OpenAPI companion document against `API_CONTRACT.md`, which remains the canonical contract. This phase changes API documentation and validation tests only; it does not implement the runtime endpoints.

## Operation coverage

- Canonical contract operations: **62**.
- Original OpenAPI operations: **22**.
- Exact method/path matches before changes: **21**.
- Contract operations absent by exact method/path before changes: **41** — this includes the one ingestion route mismatch, so the breakdown is **40 missing operations + 1 route mismatch**.
- Non-contract operation removed: `POST /ingestion/jobs`.
- OpenAPI operations after reconciliation: **62**, with exact method/path coverage against the contract.

## Operation-by-operation comparison

| Method | Canonical path | Initial draft status | Reconciled status |
|---|---|---|---|
| `POST` | `/auth/login` | Present | Aligned: exact method/path present |
| `POST` | `/auth/logout` | Present | Aligned: exact method/path present |
| `GET` | `/auth/me` | Present | Aligned: exact method/path present |
| `POST` | `/admin/users` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/admin/users` | Missing from draft | Aligned: exact method/path present |
| `PATCH` | `/admin/users/{user_id}` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/health` | Present | Aligned: exact method/path present |
| `GET` | `/admin/runtime` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/sources` | Present | Aligned: exact method/path present |
| `POST` | `/sources` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/sources/{source_id}` | Present | Aligned: exact method/path present |
| `PATCH` | `/sources/{source_id}` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/editions` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/sources/{source_id}/editions` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/editions/{edition_id}` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/passages` | Present | Aligned: exact method/path present |
| `POST` | `/editions/{edition_id}/passages` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/passages/{passage_id}` | Present | Aligned: exact method/path present |
| `GET` | `/passages/{passage_id}/interpretations` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/passages/{passage_id}/interpretations` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/passages/{passage_id}/revisions` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/science/search` | Present | Aligned: exact method/path present |
| `GET` | `/science/publications` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/science/publications/{publication_id}` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/science/ingestion-jobs` | Route mismatch: draft had POST /ingestion/jobs | Aligned: exact method/path present |
| `GET` | `/ingestion/jobs` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/ingestion/jobs/{job_id}` | Present | Aligned: exact method/path present |
| `POST` | `/admin/embedding-jobs` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/admin/embedding-profiles` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/retrieval/search` | Present | Aligned: exact method/path present |
| `POST` | `/analysis` | Present | Aligned: exact method/path present |
| `GET` | `/analysis/{analysis_id}` | Present | Aligned: exact method/path present |
| `GET` | `/analysis` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/analysis/{analysis_id}/claims` | Present | Aligned: exact method/path present |
| `GET` | `/analysis/{analysis_id}/hypotheses` | Present | Aligned: exact method/path present |
| `GET` | `/claims/{claim_id}` | Present | Aligned: exact method/path present |
| `GET` | `/claims/{claim_id}/evidence` | Present | Aligned: exact method/path present |
| `POST` | `/claims/{claim_id}/evidence` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/evidence/{evidence_item_id}` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/evidence` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/evidence/{evidence_item_id}/verify` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/hypotheses/{hypothesis_id}` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/hypotheses/{hypothesis_id}/evidence` | Missing from draft | Aligned: exact method/path present |
| `PATCH` | `/hypotheses/{hypothesis_id}` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/procedures` | Present | Aligned: exact method/path present |
| `GET` | `/procedures/{procedure_id}` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/instruments` | Present | Aligned: exact method/path present |
| `GET` | `/instruments/{instrument_id}` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/procedures/{procedure_id}/instruments` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/reviews` | Present | Aligned: exact method/path present |
| `GET` | `/reviews` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/reviews/{review_id}` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/bookmarks` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/bookmarks` | Missing from draft | Aligned: exact method/path present |
| `DELETE` | `/bookmarks/{bookmark_id}` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/annotations` | Missing from draft | Aligned: exact method/path present |
| `POST` | `/annotations` | Missing from draft | Aligned: exact method/path present |
| `PATCH` | `/annotations/{annotation_id}` | Missing from draft | Aligned: exact method/path present |
| `DELETE` | `/annotations/{annotation_id}` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/dashboard/metrics` | Present | Aligned: exact method/path present |
| `GET` | `/admin/ingestion-jobs` | Missing from draft | Aligned: exact method/path present |
| `GET` | `/admin/audit-logs` | Missing from draft | Aligned: exact method/path present |

## Reported discrepancies corrected in OpenAPI

1. **Operation coverage:** all 62 method/path operations from the contract are now represented; no extra method/path operation remains.
2. **Login request:** `LoginRequest` requires `username_or_email` and `password`; the obsolete `email`-only request definition was removed.
3. **Ingestion route:** ingestion creation is `POST /science/ingestion-jobs`; `GET /ingestion/jobs` and `GET /ingestion/jobs/{job_id}` remain the status/list routes.
4. **Roles:** the public `User` role enum includes `admin`, `researcher`, and `reviewer`.
5. **Health response:** required `embedding_model` and `checked_at` fields are represented, and `503` is documented for database unavailability.

Additional contract-derived alignment included source and passage field names, source/passages query filters, ingestion request vocabulary (`source_system`), the retrieval ranking options (`rrf`, `lexical`, `vector`), the `max_hypotheses` limit of 10, evidence relationship values, review request fields/decisions, pagination envelopes, authentication metadata, and unique `operationId` values.

## Validation added

`backend/tests/test_api_contract.py` checks:

- exact operation-set equality between the Markdown contract and OpenAPI;
- present and unique `operationId` values;
- resolution of local `#/components/...` references;
- login request field names;
- ingestion path alignment;
- reviewer role and required health fields;
- absence of a public registration endpoint/schema;
- review/evidence enum alignment; and
- the analysis hypothesis limit.

## Contract details intentionally not invented

The canonical contract does not define complete field-level request/response schemas for every operation. For those routes, the OpenAPI document uses explicitly described generic object schemas or documents the operation without fabricating field names. These schemas should be refined only after the owner approves the exact fields or the canonical contract is expanded.

The contract itself contains at least one issue to resolve separately: the `GET /passages/{passage_id}` example repeats the `passage_code` JSON key. This Phase 2 change does **not** modify the canonical contract or choose which duplicate occurrence to keep. The `API_CONTRACT.md` remains unchanged.

## Scope and limitations

- This phase does **not** add runtime FastAPI endpoints. The backend still implements only the starter health/readiness routes.
- It does not verify live PostgreSQL, Docker, or frontend integration.
- The OpenAPI file was parsed as YAML and its local component references were checked. A dedicated OpenAPI-specification validator is not installed in the current environment, so full formal OpenAPI schema validation remains unverified.
- No database schema or frontend files were changed.

## Suggested commit message

`docs(api): reconcile OpenAPI with canonical contract`
