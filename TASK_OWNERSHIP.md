# Task Ownership and Integration Rules

**Project owner:** User\
**Decision authority:** The project owner has final authority over
scope, architecture, database schema, API contracts, model/runtime
selection, evaluation, integration and release.

## Owner responsibilities

-   Approve project requirements, database schema and API contract.
-   Own AI orchestration, 1D--4D analysis, claim/evidence auditing,
    hypothesis evaluation and frontend.
-   Define acceptance tests and approve releases.
-   Review proposed architectural changes.

## Backend contributor responsibilities

-   Implement approved database migrations and indexes.
-   Implement source ingestion, provenance and scientific provider
    integration.
-   Implement passage chunking, embedding/indexing and hybrid retrieval.
-   Implement RRF ranking and retrieval endpoints.
-   Implement ingestion job tracking, health checks, documentation and
    tests.
-   Report blockers early and propose solutions before changing approved
    interfaces.

## Shared working rules

1.  One repository and one canonical PostgreSQL database.
2.  One migration history; never manually change shared schemas without
    a migration.
3.  No independent competing app, backend or schema.
4.  Every API endpoint must match the approved contract.
5.  Mock data is temporary and must match the contract.
6.  No secrets in source control or logs.
7.  Changes to schema, routes, dependencies, data semantics or scope
    require owner approval.
8.  Each change includes tests and documentation.
9.  Use small, reviewable pull requests/commits and integrate
    incrementally.
10. Preserve source provenance and evidence auditability.

## Required handoff from backend contributor

-   Migrations and clean-database setup instructions.
-   API implementation matching OpenAPI.
-   Tests and results.
-   Example requests/responses.
-   Ingestion/retrieval documentation.
-   Known limitations and unresolved blockers.
