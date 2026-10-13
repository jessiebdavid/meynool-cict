# API_CONTRACT.md
## Meynool — Tamil Literary Knowledge and Scientific Evidence Intelligence Platform — REST API Contract v1.0

**Status:** Finalized contract baseline for implementation  
**API framework:** Python + FastAPI + Pydantic  
**Base path:** `/api/v1`  
**Canonical database:** Local PostgreSQL + pgvector  
**API owner:** Project owner has final approval over contract changes  
**Authentication policy:** Admin-created accounts only; public registration is disabled  
**Content type:** `application/json`, except documented file-transfer routes  
**Time format:** ISO 8601 UTC timestamps  
**Identifiers:** UUID strings

This contract is the source of truth for frontend/backend integration. Implement routes and schemas as written, or raise a written change request before changing names, response shapes, authorization, or semantics. `openapi.yaml` is a companion draft; the authoritative OpenAPI document must ultimately be generated from or validated against the FastAPI implementation.

---

## 1. Contract-wide rules

### 1.1 API conventions
- Prefix every route with `/api/v1`.
- Use Pydantic request and response models; do not return raw ORM objects.
- UUIDs are JSON strings. Timestamps are UTC ISO 8601 strings, such as `2026-10-13T12:00:00Z`.
- List endpoints use `limit` (default `20`, range `1–100`) and `offset` (default `0`, minimum `0`) unless the route defines cursor pagination.
- List response shape: `{"items": [], "limit": 20, "offset": 0, "total": null}`. `total` is an integer when computed, otherwise `null`; never invent totals.
- Use `201 Created` for synchronous creation, `202 Accepted` for queued work, and `204 No Content` for successful deletion/logout with no body.
- Long-running analysis, ingestion, chunking, embedding and reindex jobs return a resource ID and status URL. The client polls the status endpoint; do not hold a request open while the entire job runs.
- Return only data the caller is authorized to see. Never expose password hashes, raw session tokens, API keys, local filesystem secrets, stack traces or internal configuration.
- The frontend calls FastAPI only. It must not connect directly to PostgreSQL or Ollama.
- No API response may fabricate source text, scientific references, evidence, historical procedures, instruments, counts or evaluation metrics to fill missing data.
- External providers can be unavailable. Return a clear provider status and preserve valid partial results instead of pretending the request succeeded completely.
- Use request IDs for traceability. Include a request ID in error responses and logs.

### 1.2 Standard error envelope

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "request_id": "a-valid-request-id"
  }
}
```

Standard codes: `VALIDATION_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `RATE_LIMITED`, `DEPENDENCY_UNAVAILABLE`, `MODEL_UNAVAILABLE`, `PROVIDER_UNAVAILABLE`, `LICENCE_RESTRICTED`, `JOB_FAILED`, `INTERNAL_ERROR`.

Use standard HTTP statuses: `200`, `201`, `202`, `204`, `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500`, `503`. Do not expose stack traces in `500` responses.

### 1.3 Authorization roles
- **Unauthenticated:** `GET /health`, `POST /auth/login`.
- **Admin:** create/disable accounts; start imports/reindex jobs; view administration and audit information.
- **Researcher:** search, retrieve sources, create analyses, manage own bookmarks/annotations, view research records allowed by project policy.
- **Reviewer:** perform reviews and read the material needed for review. A user can have only one primary role in v1; do not infer admin privileges from reviewer status.
- Account creation is admin-only. There is no public `POST /auth/register` endpoint.
- All authorization checks are enforced by FastAPI, not merely hidden in the UI.

### 1.4 Scientific integrity requirements
- Preserve original source passages separately from translations and interpretations.
- Each evidence item must retain its source identifier/URL and locator where available.
- Empty evidence lists are valid.
- Evidence relationships distinguish `supports`, `contradicts`, `qualifies`, and `contextualizes`.
- A retrieval rank or model confidence score is not scientific confidence.
- A model-generated claim remains `unverified` until assessed under the review process.
- Do not report a “hallucination percentage” unless computed from a documented, human-reviewed evaluation set with a stated denominator, rubric, and adjudication method.
- Hypotheses are clearly labelled as hypotheses, not discoveries.
- Historical procedures/instruments are documentary records only, not validated clinical guidance or step-by-step surgical instructions.

---

## 2. Authentication and accounts

### `POST /auth/login`
Authenticates an active account.

Request:
```json
{
  "username_or_email": "researcher",
  "password": "user-supplied-secret"
}
```

Response `200`:
```json
{
  "user": {
    "id": "uuid",
    "username": "researcher",
    "email": "researcher@example.local",
    "display_name": "Researcher",
    "role": "researcher",
    "status": "active"
  }
}
```

For the browser application, use a secure `HttpOnly`, `SameSite` cookie and CSRF protection when cookie-based authentication is used. Store only a hash of opaque session tokens in the database. Never return the session token in JSON. If the implementation uses a different mechanism, document expiry, refresh, revocation and storage before implementation and obtain owner approval.

Errors: `401` for invalid credentials; `403` for disabled/pending accounts.

### `POST /auth/logout`
Authenticated. Revokes the current session. Response `204`.

### `GET /auth/me`
Authenticated. Returns the current public user representation. Response `200`.

### `POST /admin/users`
Admin-only. Creates an account.

Request:
```json
{
  "username": "researcher",
  "email": "researcher@example.local",
  "display_name": "Researcher",
  "role": "researcher",
  "temporary_password": "one-time-secret"
}
```

Response `201` returns public user fields and `must_reset_password: true`; never returns password material. The temporary password should be delivered through a controlled local workflow, not written to application logs. Store only a strong password hash.

Allowed roles: `admin`, `researcher`, `reviewer`. The first admin is bootstrapped through a documented local CLI command, not through a public endpoint.

### `GET /admin/users`
Admin-only. Paginated user list. Do not include password hashes or session tokens.

### `PATCH /admin/users/{user_id}`
Admin-only. Updates permitted account fields such as `role`, `status`, `display_name`, and `must_reset_password`. Account disabling revokes active sessions. Do not allow changing the last active admin into a disabled/non-admin account without an explicit safeguard.

---

## 3. Health and runtime status

### `GET /health`
Returns core API health and dependency status. This endpoint may be unauthenticated but must not disclose secrets or detailed internal network configuration.

Response `200`:
```json
{
  "status": "ok",
  "database": "ok",
  "ollama": "unknown",
  "embedding_model": "not_configured",
  "scientific_providers": {
    "pubmed": "unknown",
    "europe_pmc": "unknown"
  },
  "version": "0.1.0",
  "checked_at": "2026-10-13T12:00:00Z"
}
```

Status values must be measured or clearly defined as last-known. If the database is unavailable, return `503`. An optional external scientific provider being offline does not by itself make the core API unhealthy.

### `GET /admin/runtime`
Admin-only. Returns non-secret runtime configuration relevant to operations: selected model names/versions, embedding profile status and dimension, and provider availability. Never return credentials, environment variable values containing secrets, or filesystem secret paths.

---

## 4. Literary source catalogue

### `GET /sources`
List works. Query parameters: `q`, `tradition_or_collection`, `language_code`, `source_status`, `limit`, `offset`, `sort`.

Response `200`:
```json
{
  "items": [
    {
      "id": "uuid",
      "canonical_title": "Stored title",
      "title_ta": null,
      "title_en": null,
      "attributed_author": "Attribution as recorded",
      "attribution_confidence": "traditional",
      "genre": null,
      "tradition_or_collection": null,
      "source_status": "verified"
    }
  ],
  "limit": 20,
  "offset": 0,
  "total": null
}
```
The example is illustrative only. Do not seed this example as a real source.

### `POST /sources`
Admin or authorized curator. Creates source metadata. Response `201` with source representation.

### `GET /sources/{source_id}`
Returns source metadata and edition summaries. `404` if absent.

### `PATCH /sources/{source_id}`
Admin/authorized curator. Updates source metadata. Changes to attribution confidence/status must be auditable.

### `GET /editions`
Filters: `source_id`, `language_code`, `edition_type`, `rights_status`, `limit`, `offset`.

### `POST /sources/{source_id}/editions`
Admin/authorized curator. Adds a documented edition. Response `201`.

### `GET /editions/{edition_id}`
Returns edition metadata, provenance, identifiers, source URL, repository and rights status/notes.

### `GET /passages`
Filters: `q`, `source_id`, `edition_id`, `status`, `language_code`, `limit`, `offset`. `q` searches stored text only; results must not silently include generated interpretations as source text.

### `POST /editions/{edition_id}/passages`
Admin/authorized curator. Adds a passage with `locator`, `original_text`, language, transcription method and optional confidence. Response `201`.

### `GET /passages/{passage_id}`
Response `200`:
```json
{
  "id": "uuid",
  "source_edition_id": "uuid",
  "passage_code": null,
  "sequence_number": 1,
  "locator": "edition-specific locator",
  "original_text": "Exact stored source text",
  "normalized_text": null,
  "language_code": "ta",
  "transcription_method": "unknown",
  "transcription_confidence": null,
  "status": "draft",
  "text_checksum": null,
  "created_at": "2026-10-13T12:00:00Z"
}
```

### `GET /passages/{passage_id}/interpretations`
Returns translations, glosses, contextual notes, scholarly interpretations and model-generated interpretations as separate typed records. Always label type, language, author/model, review status and source reference when available.

### `POST /passages/{passage_id}/interpretations`
Authorized researcher/curator. Creates a translation or interpretation record. Model-generated content must include model identity/version and be marked unreviewed by default.

### `GET /passages/{passage_id}/revisions`
Returns transcription revision history. Original source text must never be silently overwritten.

---

## 5. Scientific literature

### `GET /science/search`
Searches configured scientific providers, such as PubMed and Europe PMC. Query parameters: `q` (required), `provider` (`pubmed`, `europe_pmc`, `all`; default `all`), `year_from`, `year_to`, `limit`, `offset`.

Response `200`:
```json
{
  "query": "scientific query",
  "items": [
    {
      "id": "local-uuid-or-null-for-provider-only-result",
      "title": "Actual provider-returned title",
      "doi": null,
      "pmid": null,
      "pmcid": null,
      "europe_pmc_id": null,
      "year": null,
      "journal_or_repository": null,
      "canonical_url": "actual provider URL",
      "metadata_source": "europe_pmc",
      "metadata_retrieved_at": "2026-10-13T12:00:00Z",
      "local_record": false
    }
  ],
  "limit": 20,
  "offset": 0,
  "total": null,
  "provider_status": {
    "pubmed": "ok",
    "europe_pmc": "ok"
  }
}
```
Examples are illustrative; runtime values must come from actual provider results. If a provider's total is unknown, return `null`.

### `GET /science/publications`
Searches the locally stored publication catalogue. Filters: `q`, `year_from`, `year_to`, `metadata_source`, `limit`, `offset`.

### `GET /science/publications/{publication_id}`
Returns stored metadata, permitted abstract if available, authors, identifiers, canonical URL, licence/storage status and retrieval timestamps.

### `POST /science/ingestion-jobs`
Admin-only unless the owner explicitly approves a different policy. Starts provider search/metadata ingestion or permitted-text ingestion.

Request:
```json
{
  "source_system": "europe_pmc",
  "job_type": "publication_metadata_sync",
  "query": "user's search terms",
  "limit": 20
}
```

Response `202`:
```json
{
  "job_id": "uuid",
  "status": "queued",
  "status_url": "/api/v1/ingestion/jobs/uuid"
}
```

Store metadata and identifiers by default. Store abstracts/full text only when the source terms, licence, API policy and applicable law permit it. The job must record the storage basis; a returned link alone is not permission to copy the content. Never bypass paywalls or access controls.

---

## 6. Ingestion jobs

### `GET /ingestion/jobs`
Admin-only. Filters: `status`, `source_system`, `job_type`, `limit`, `offset`.

### `GET /ingestion/jobs/{job_id}`
Returns status, counters, timestamps and a safe error summary.

Response:
```json
{
  "id": "uuid",
  "status": "running",
  "source_system": "europe_pmc",
  "job_type": "publication_metadata_sync",
  "records_seen": 20,
  "records_created": 8,
  "records_updated": 2,
  "records_skipped": 10,
  "error_count": 0,
  "started_at": "2026-10-13T12:00:00Z",
  "completed_at": null,
  "error_summary": null
}
```

### `POST /admin/embedding-jobs`
Admin-only. Starts chunking/embedding/reindex work for a chosen approved embedding profile. The profile must have a verified model identity and vector dimension. Response `202` with job ID. Reject incompatible dimensions with `409` or `422`; never silently mix embedding spaces.

### `GET /admin/embedding-profiles`
Admin-only. Lists approved profiles, model/version/digest, dimensions, language coverage, evaluation summary and active status. Do not claim a model supports Tamil well without evaluation.

---

## 7. Hybrid retrieval

### `POST /retrieval/search`
Authenticated. Searches literary passages and/or permitted scientific content using lexical search and optional vector search.

Request:
```json
{
  "query": "research question",
  "source_ids": [],
  "include_literary_passages": true,
  "include_scientific_publications": true,
  "top_k": 10,
  "ranking_method": "rrf"
}
```

Validation:
- `query` must be non-empty and within the configured maximum length.
- `top_k` range is `1–50`.
- `ranking_method` is `rrf`, `lexical`, or `vector`.
- Vector retrieval requires an active compatible embedding profile; if unavailable, return lexical results with a clear warning rather than inventing vector scores.

Response `200`:
```json
{
  "query": "research question",
  "ranking_method": "rrf",
  "embedding_profile_id": null,
  "warnings": [],
  "results": [
    {
      "result_type": "literary_passage",
      "source_id": "uuid",
      "edition_id": "uuid",
      "passage_id": "uuid",
      "publication_id": null,
      "title": "Stored source title",
      "excerpt": "Excerpt from a stored, permitted record",
      "source_url": null,
      "source_locator": "stored locator",
      "lexical_rank": 1,
      "dense_rank": null,
      "rrf_score": 0.0164
    }
  ]
}
```
Every value must derive from real retrieval. If a retrieval channel did not return an item, its rank is `null`. Document the RRF constant and exact calculation in implementation configuration. A ranking score is not evidence strength or truth probability. Mark excerpts and rights restrictions correctly.

---

## 8. 1D–4D analysis

### `POST /analysis`
Authenticated researcher. Queues a research analysis.

Request:
```json
{
  "query": "Analyze this passage in relation to biological literature",
  "passage_ids": ["uuid"],
  "dimensions": ["1D", "2D", "3D", "4D"],
  "include_scientific_evidence": true,
  "generate_hypotheses": true,
  "max_hypotheses": 5
}
```

Validation:
- `dimensions` must contain one or more of `1D`, `2D`, `3D`, `4D`.
- `max_hypotheses` range `0–10`.
- Referenced passage IDs must exist and be accessible.
- Analysis must distinguish source-grounded content from model-generated interpretation.
- If no relevant source/evidence is found, return that limitation explicitly.

Response `202`:
```json
{
  "analysis_id": "uuid",
  "status": "queued",
  "status_url": "/api/v1/analysis/uuid"
}
```

### `GET /analysis/{analysis_id}`
Returns analysis run status, available results, claims/hypotheses IDs, limitations and model/retrieval metadata. Queued/running responses may include progress information; failed runs return a safe error code.

Response when completed:
```json
{
  "id": "uuid",
  "status": "succeeded",
  "query_text": "Analyze this passage",
  "dimensions": {
    "1D": {
      "result_text": "Source text and fidelity notes",
      "structured_result": {},
      "limitations": null
    },
    "2D": {
      "result_text": "Context and interpretation",
      "structured_result": {},
      "limitations": null
    },
    "3D": {
      "result_text": "Biological concepts and evidence assessment",
      "structured_result": {},
      "limitations": "No direct scientific equivalence established"
    },
    "4D": {
      "result_text": "Chronology and date uncertainties",
      "structured_result": {},
      "limitations": null
    }
  },
  "claim_ids": [],
  "hypothesis_ids": [],
  "model": {
    "provider": "ollama",
    "name": "configured-model",
    "version_or_digest": null
  },
  "prompt_version": "v1",
  "created_at": "2026-10-13T12:00:00Z",
  "completed_at": "2026-10-13T12:00:30Z"
}
```

The database may store one result for each requested dimension plus `overall`. Return only results actually generated. Do not fabricate a missing dimension result to complete the object.

### `GET /analysis`
Authenticated. Lists the caller's analyses; admins may query all analyses if policy permits. Filters: `status`, `created_after`, `created_before`, `limit`, `offset`.

### `GET /analysis/{analysis_id}/claims`
Returns claims created by the analysis, with status and linked evidence count/summaries.

### `GET /analysis/{analysis_id}/hypotheses`
Returns generated hypotheses, rationale, status, limitations and linked evidence.

---

## 9. Claims and evidence

### `GET /claims/{claim_id}`
Returns claim text, type, origin, dimension, status, confidence if present, uncertainty notes, analysis ID and linked source/evidence counts.

### `GET /claims/{claim_id}/evidence`
Returns evidence items and relationship records: `supports`, `contradicts`, `qualifies`, `contextualizes`; includes source IDs/identifiers, locator, URL, verification status, review status and excerpt only where storage is permitted.

### `POST /claims/{claim_id}/evidence`
Authorized researcher/reviewer. Links an existing evidence item to a claim.

Request:
```json
{
  "evidence_item_id": "uuid",
  "relation": "supports",
  "rationale": "Why this source supports or qualifies the specific claim",
  "strength": "unassessed"
}
```

The API must not create a new evidence item from an unverified citation string without validating its provenance.

### `GET /evidence/{evidence_item_id}`
Returns the evidence record and provenance, verification status, source identifiers and permitted excerpt.

### `POST /evidence`
Authorized researcher/curator. Creates an evidence record from a real source identifier, passage, publication or explicitly documented other evidence. `evidence_type=no_evidence_found` is allowed to record a search outcome but must include the search scope and timestamp in its summary/metadata.

### `POST /evidence/{evidence_item_id}/verify`
Reviewer/admin. Updates verification status after checking the linked record. Include who checked it and when. `expert_reviewed` must only be set by an authorized reviewer after actual review.

---

## 10. Hypotheses

### `GET /hypotheses/{hypothesis_id}`
Returns hypothesis text, rationale, testability/novelty notes, status, limitations and evidence links.

### `POST /hypotheses/{hypothesis_id}/evidence`
Authorized researcher/reviewer. Adds a supporting, contradicting, qualifying or contextualizing evidence relationship.

### `PATCH /hypotheses/{hypothesis_id}`
Reviewer/admin. Updates review status and notes. Valid statuses: `proposed`, `under_review`, `supported`, `contradicted`, `inconclusive`, `withdrawn`. “Supported” is not equivalent to independently replicated scientific discovery.

---

## 11. Historical procedures and instruments

### `GET /procedures`
Filters: `q`, `source_status`, `modern_clinical_status`, `limit`, `offset`.

### `GET /procedures/{procedure_id}`
Returns documentary description, source/evidence links, source status and explicit safety/limitations note. Do not return step-by-step actionable surgical instructions.

### `GET /instruments`
Filters: `q`, `equivalence_status`, `limit`, `offset`.

### `GET /instruments/{instrument_id}`
Returns historical name/description, possible modern-equivalent claim and equivalence status. Do not present analogy as proof of equivalence.

### `GET /procedures/{procedure_id}/instruments`
Returns linked instruments and the evidence/provenance for each relationship.

These are research-documentation routes, not clinical decision-support endpoints.

---

## 12. Reviews and researcher workspace

### `POST /reviews`
Reviewer/admin only. Creates an append-only review for exactly one supported target.

Request:
```json
{
  "target_type": "claim",
  "target_id": "uuid",
  "decision": "needs_expert",
  "review_notes": "The evidence does not establish the claim."
}
```

Allowed `target_type`: `passage`, `interpretation`, `claim`, `evidence_item`, `hypothesis`, `historical_procedure`, `instrument`. Allowed decisions: `approve`, `revise`, `reject`, `needs_expert`. Validate that the target exists and that the reviewer can access it. A review decision must not silently erase prior review history.

### `GET /reviews`
Reviewer/admin. Filters: `target_type`, `target_id`, `reviewer_id`, `decision`, `limit`, `offset`. Researchers can view reviews only where project permissions allow.

### `GET /reviews/{review_id}`
Returns the review record.

### `GET /bookmarks`
Authenticated. Returns the caller's bookmarks. Filters: `target_type`, `limit`, `offset`.

### `POST /bookmarks`
Authenticated. Creates a bookmark after validating target existence and access.

Request:
```json
{
  "target_type": "passage",
  "target_id": "uuid",
  "label": "Review later"
}
```

Response `201`. Duplicate bookmarks for the same user/target return `409` or an explicitly documented idempotent `200` behavior; use one consistent policy.

### `DELETE /bookmarks/{bookmark_id}`
Authenticated. Deletes only the caller's bookmark. Response `204`.

### `GET /annotations`
Authenticated. Returns caller's annotations; project-visible annotations may be returned only if authorized. Filters: `passage_id`, `analysis_run_id`, `claim_id`, `visibility`, `limit`, `offset`.

### `POST /annotations`
Authenticated. Exactly one of `passage_id`, `analysis_run_id`, or `claim_id` is required.

Request:
```json
{
  "passage_id": "uuid",
  "analysis_run_id": null,
  "claim_id": null,
  "body": "Research note",
  "anchor_start": null,
  "anchor_end": null,
  "visibility": "private"
}
```

Response `201`. Validate that the anchor is within the stored text when offsets are supplied.

### `PATCH /annotations/{annotation_id}`
Authenticated. Only the owner may edit their annotation unless an admin moderation policy explicitly applies.

### `DELETE /annotations/{annotation_id}`
Authenticated. Only the owner or authorized admin may delete. Response `204`.

---

## 13. Dashboard and evaluation metrics

### `GET /dashboard/metrics`
Authenticated; admin-only for system-wide counts if required by project privacy policy. Returns actual database counts and evaluation metrics with definitions, timestamp, and evaluation-set metadata.

Response shape:
```json
{
  "generated_at": "2026-10-13T12:00:00Z",
  "counts": {
    "literary_sources": 0,
    "passages": 0,
    "scientific_publications": 0,
    "analysis_runs": 0,
    "claims": 0,
    "evidence_items": 0,
    "hypotheses": 0
  },
  "evaluation": {
    "unsupported_claim_rate": null,
    "citation_validity_rate": null,
    "retrieval_recall_at_k": null,
    "evaluation_set_id": null,
    "evaluated_at": null,
    "status": "not_available"
  }
}
```

Zero counts are valid only when measured from the database. Unrun metrics must be `null` with status `not_available`; never use mock numbers in the live dashboard. `unsupported_claim_rate` must be calculated using a defined human-reviewed evaluation set and adjudication rubric. Do not label every unsupported claim as a hallucination without the agreed operational definition.

---

## 14. Audit and administrative endpoints

### `GET /admin/ingestion-jobs`
Admin-only; equivalent to the ingestion job list with operational filters.

### `GET /admin/audit-logs`
Admin-only. Paginated audit entries with filters for actor, action, entity and date range. Do not permit normal application users to update/delete audit rows.

Administrative endpoints must not expose secrets in configuration, provider tokens, raw authentication tokens or personal data not needed for the task.

---

## 15. Suggested implementation order

1. Implement Pydantic base schemas, error envelope, request IDs and pagination.
2. Implement authentication/session middleware and admin-created account workflow.
3. Implement health check and database connectivity.
4. Implement source/edition/passage read APIs and curator write APIs.
5. Implement scientific provider search and metadata ingestion jobs, with licence-aware storage.
6. Implement lexical retrieval; add vector retrieval only after the approved embedding migration is ready.
7. Implement analysis job lifecycle and separate 1D–4D results.
8. Implement claims/evidence/hypothesis endpoints and provenance checks.
9. Implement procedures/instruments, reviews, bookmarks and annotations.
10. Implement measured dashboard metrics and admin audit views.
11. Generate FastAPI OpenAPI, compare it to this contract, run acceptance tests, then integrate frontend.

---

## 16. Contract acceptance checklist

- [ ] No public registration route exists; only an admin can create accounts.
- [ ] Login, logout, disabled accounts, session expiry and revocation are tested.
- [ ] All protected routes enforce roles server-side.
- [ ] All list routes use consistent pagination and stable response envelopes.
- [ ] Source passages always identify their edition and locator.
- [ ] Original text, translation, interpretation and generated content are separately typed.
- [ ] Scientific text is stored only when permitted, and storage basis is traceable.
- [ ] Provider-only search results are not falsely represented as locally stored records.
- [ ] Ingestion/analysis/embedding operations use queued jobs and status endpoints.
- [ ] Retrieval scores are never presented as scientific confidence.
- [ ] Claims can retain contradictory as well as supporting evidence.
- [ ] Hypotheses are explicitly labelled and cannot default to discoveries.
- [ ] Workspace endpoints validate polymorphic targets and user ownership.
- [ ] Dashboard counts and metrics are measured; unavailable metrics are null.
- [ ] API responses never expose passwords, hashes, tokens, stack traces or secrets.
- [ ] Generated OpenAPI matches the implemented routes and Pydantic schemas.
- [ ] Frontend calls FastAPI only and does not access PostgreSQL/Ollama directly.

---

## 17. Change control

The project owner has final approval. Before changing a route, field name, enum, response shape, authorization rule, evidence semantic, or status meaning, the implementer must provide:
1. the reason and user-visible impact;
2. the schema/API/OpenAPI changes;
3. any database migration and rollback plan;
4. tests demonstrating compatibility; and
5. a request for owner approval.

Breaking changes require a deliberate API versioning decision. Do not create a second competing API contract.
