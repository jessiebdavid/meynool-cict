# Acceptance Tests --- Initial MVP

**Status:** Proposed; owner approval required. Numerical thresholds
should be set after a baseline evaluation.

## A. Database and provenance

-   [ ] All migrations apply to a clean local PostgreSQL + pgvector
    database.
-   [ ] Rollback/restore procedure is documented where supported.
-   [ ] Every passage references an edition; every edition references a
    literary source.
-   [ ] Original source text remains unchanged when translations or
    interpretations are added.
-   [ ] Stable scientific provider identifiers are deduplicated.
-   [ ] Ingestion reruns do not create duplicate records when provider
    IDs/content hashes match.
-   [ ] Foreign-key constraints prevent orphan claims/evidence and
    invalid review targets.

## B. API contracts

-   [ ] Every endpoint matches the approved OpenAPI schema.
-   [ ] Invalid payloads return a consistent validation error.
-   [ ] Missing records return 404.
-   [ ] Unauthenticated requests to protected routes return 401.
-   [ ] Unauthorized role actions return 403.
-   [ ] Pagination limits are enforced.
-   [ ] Secrets, password hashes and stack traces never appear in
    responses.
-   [ ] Long-running operations return job/resource IDs and accurate
    status.

## C. Retrieval

-   [ ] Search results point to actual stored passages/publications.
-   [ ] Every excerpt and locator matches its source record.
-   [ ] Lexical and vector ranks are recorded correctly when available.
-   [ ] RRF scores match the documented calculation.
-   [ ] Empty result sets are handled without fabricated records.
-   [ ] Embedding model and dimension mismatches fail safely.
-   [ ] External provider timeout/rate limit is reported clearly.

## D. Scientific evidence and analysis

-   [ ] Every claim has a stable ID and analysis reference.
-   [ ] Every linked evidence item has a valid source record or a
    documented external source reference.
-   [ ] Evidence relationship is explicitly recorded.
-   [ ] Unsupported or ambiguous claims remain unverified/untested
    rather than being promoted to facts.
-   [ ] A generated interpretation is not stored as original source
    text.
-   [ ] Hypotheses are labelled as hypotheses and include limitations.
-   [ ] Historical procedure/instrument records cite their source
    passage and evidence status.
-   [ ] Model/provider failure produces a safe failed status, not a
    fabricated completed analysis.

## E. Authentication and security

-   [ ] Passwords are hashed using a suitable password-hashing library.
-   [ ] Login/logout and protected route behavior are tested.
-   [ ] Role checks occur on the backend.
-   [ ] Secrets are held in environment configuration and excluded from
    version control.
-   [ ] Logs do not contain passwords, session tokens or API keys.
-   [ ] The database is not exposed to the public network by default.

## F. Evaluation protocol

Before displaying quality percentages, record: - Evaluation-set version
and sample size. - Gold/reference labels and review process. - Metric
definition and denominator. - Date, model version, prompt version and
retrieval configuration. - Separate results for source fidelity,
retrieval relevance, citation validity, citation support correctness,
unsupported claims and abstention.

Do not report a hallucination percentage without a defined, reproducible
evaluation set and protocol.
