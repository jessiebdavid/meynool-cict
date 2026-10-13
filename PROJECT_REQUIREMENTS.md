# Meynool — Tamil Literary Knowledge and Scientific Evidence Intelligence Platform

## Project Requirements — Build Baseline

**Document status:** Approved working baseline for initial implementation; changes to scope, safety rules, schema or API require project-owner approval.\
**Project owner:** User / project owner\
**Deployment target:** Local-first development on a local machine\
**Primary database:** PostgreSQL + pgvector\
**Backend:** Python + FastAPI\
**Frontend:** React + Vite + TypeScript\
**Local LLM runtime:** Ollama\
**Authentication:** Local researcher accounts with login

------------------------------------------------------------------------

## 1. Purpose

Build a biology- and health-sciences research platform that investigates
authentic, traceable Tamil literary sources and carefully evaluates
possible relationships to modern biological and biomedical knowledge.
The system should support source discovery, contextual interpretation,
scientific-literature retrieval, claim-level evidence review, historical
procedure and instrument documentation, and research-hypothesis
generation.

The platform is a research-assistance system, not a clinical
decision-support system. It must not recommend patient-specific
treatment, diagnose people, or present unvalidated historical practices
as safe medical procedures.

## 2. Scope

### 2.1 Source collections

The platform may include: - Works and passages attributed to Bogar, with
attribution and edition provenance recorded. - Vallalar-related
material, including Thiruvarutpa, with source and edition provenance
recorded. - Relevant Puranic narratives only when the specific text,
edition, passage, and provenance can be identified. - Other Tamil
sources only when explicitly approved by the project owner.

Do not assume that every attribution is historically certain. Store
attribution as a claim with a stated source and confidence/verification
status, not as an unquestioned fact.

### 2.2 Scientific scope

Focus on biology and health sciences, including relevant domains such as
anatomy, physiology, microbiology, botany, pharmacology, surgery
history, medical instruments, materials, and biomedical research.
Inclusion of a domain does not imply that a literary passage is
scientifically equivalent to modern knowledge.

### 2.3 Required capabilities

1.  Search and browse literary sources and passages.
2.  Preserve original Tamil text, edition information, passage location,
    provenance, and permitted translations.
3.  Search scientific literature through authorized APIs such as PubMed
    and Europe PMC.
4.  Store scientific metadata and permitted abstracts/full text with
    licensing/provenance information.
5.  Retrieve relevant material using lexical and vector search,
    optionally combined through Reciprocal Rank Fusion (RRF).
6.  Generate structured 1D--4D analyses.
7.  Extract atomic claims from generated analyses and link claims to
    evidence.
8.  Identify supporting, contradicting, qualifying, irrelevant, and
    insufficient evidence.
9.  Generate clearly labelled research hypotheses with rationale,
    testability, limitations, and possible validation methods.
10. Document historical procedures and instruments only to the level
    supported by traceable sources.
11. Track source ingestion, review state, analysis status, failures, and
    audit events.
12. Provide researcher login, bookmarks, annotations, reviews, and
    exports where authorized.
13. Report measured evaluation metrics without inventing performance
    values.

## 3. Mandatory 1D--4D framework

The dimensions are a project-specific analysis framework, not
established scientific dimensions.

-   **1D --- Literal source:** original passage, exact locator,
    translation if available, textual uncertainties, and source
    fidelity.
-   **2D --- Context and interpretation:** surrounding context,
    terminology, genre, historical/cultural context, scholarly
    interpretations, and explicit separation of model-generated
    interpretation.
-   **3D --- Biological relationships and evidence:** candidate
    biological concepts, relevant scientific literature, claim-level
    evidence, conflicts, limitations, and distinctions between analogy
    and scientific equivalence.
-   **4D --- Historical chronology and research development:** dated
    source/edition information when known, historical context, timeline
    of relevant scientific research, and clearly marked unknown or
    uncertain dates.

The UI and API must use these meanings consistently. The system must not
invent dates to fill timeline views.

## 4. Scientific integrity and evidence policy

Every output must distinguish: - Directly documented source text. -
Scholarly or contextual interpretation. - Thematic/metaphorical
analogy. - Modern scientific finding supported by a traceable source. -
Partially supported claim. - Untested hypothesis. - Contradicted
claim. - Unsupported or unverifiable claim.

Rules: 1. Never fabricate quotations, titles, author attributions,
identifiers, DOI/PMID values, URLs, page references, procedures,
instruments, manufacturing methods, or experimental results. 2. An AI
interpretation must never be stored or displayed as original historical
text. 3. Each evidence link must identify the target claim and
relationship: supports, contradicts, qualifies, mentions, or is
irrelevant. 4. A retrieved paper is not automatically evidence for a
claim. Relevance and support must be assessed separately. 5. If evidence
is missing or ambiguous, abstain or mark the claim unverified. 6. Do not
claim a hypothesis is novel solely because retrieval did not find an
earlier paper. 7. Do not present generated hypotheses as discoveries,
established facts, or validated interventions. 8. Historical medical
descriptions must not be converted into actionable surgical instructions
or claims of safety without appropriate evidence and expert review. 9.
Keep human verification distinct from automated checks. 10. Store source
URLs, stable identifiers, exact locators, retrieval timestamps, and
license/usage notes where applicable.

## 5. Retrieval and model approach

-   Use PostgreSQL as the single canonical database.
-   Use pgvector for embeddings and PostgreSQL full-text search for
    lexical retrieval.
-   Hybrid retrieval may combine ranked results with RRF. The algorithm
    and configuration must be documented and tested.
-   Use Ollama to serve a locally installed model. The exact model is a
    deployment configuration decision, subject to hardware, language
    support, and evaluation.
-   Use retrieval-augmented generation (RAG) initially. RAG is not model
    training.
-   Do not fine-tune until a defined evaluation demonstrates a need and
    the owner approves a dataset, licensing review, and training plan.
-   Treat retrieved text as untrusted data. It must not override system
    instructions or authorize tools/actions.
-   Store model name, model version, prompt version, retrieval
    configuration, and timestamps for each analysis run.

## 6. Local-first behavior

Core app, PostgreSQL, and Ollama run locally. Internet connectivity may
be used to query scientific literature APIs. The UI must clearly show
when external services are unavailable and must not label stale local
records as live results.

Required configuration belongs in environment variables. Never commit
actual credentials. Provide `.env.example` with placeholders only.
Document backup/restore and local setup. No cloud-hosted database or
model is required for the core deployment.

## 7. Authentication and authorization

-   Local researcher accounts with secure password hashing; never store
    plaintext passwords.
-   Use secure session or token handling appropriate to the local
    deployment.
-   Protect write operations and administrative/ingestion routes.
-   Enforce authorization on the backend, not only in the UI.
-   Avoid exposing the app or database to the public network by default.
-   Keep secrets and sensitive authentication material out of logs.
-   Record relevant administrative and review actions in an audit trail.
-   Define roles minimally for MVP: `researcher` and `admin/reviewer`.
    Owner-specific administration can be configured without hard-coding
    personal identities.

## 8. Initial architecture

-   Frontend: React + Vite + TypeScript.
-   Backend: FastAPI + Pydantic.
-   Database: local PostgreSQL with pgvector.
-   LLM: Ollama local HTTP service, accessed only by backend.
-   Migrations: Alembic (recommended) or one explicitly selected
    migration tool.
-   API docs: FastAPI-generated OpenAPI.
-   Tests: unit, API integration, database migration, retrieval, and
    end-to-end workflow tests.

No frontend component may connect directly to PostgreSQL or Ollama. The
frontend communicates with the backend API only.

## 9. Initial acceptance workflow

A first end-to-end slice must: 1. Ingest a verified literary source
edition and passage. 2. Preserve the original text and provenance. 3.
Retrieve the passage by exact identifier and by search. 4. Retrieve at
least one real scientific record when the query and provider permit it,
or clearly report no results/service unavailability. 5. Run a
local-model analysis using retrieved context. 6. Return structured
1D--4D results. 7. Extract claims and connect any evidence to stored
evidence records. 8. Label hypotheses as untested and list limitations.
9. Render the actual API response in the frontend. 10. Pass tests for
missing evidence, fabricated/invalid citations, provider failure, model
failure, and malformed input.

## 10. Evaluation

Establish a curated, manually reviewed evaluation set before reporting
numeric metrics. Track at minimum: - Retrieval relevance (e.g.,
Precision@k or Recall@k when labels exist). - Source fidelity. -
Citation identifier/URL validity. - Citation-to-claim support
correctness. - Claim evidence coverage. - Unsupported-claim rate on the
evaluation set. - Abstention behavior when evidence is insufficient. -
Hypothesis testability and reviewer assessment.

Always report metric definition, numerator, denominator, sample size,
evaluation-set version, and date. Do not conflate unverified claims with
confirmed hallucinations. Do not display a hallucination percentage
until the measurement protocol is defined and run.

## 11. Out of scope for the initial MVP

-   Patient-specific diagnosis or treatment.
-   Claims that a historical method is clinically safe/effective without
    appropriate evidence.
-   Automatic clinical or surgical instructions.
-   Fine-tuning as a default requirement.
-   Unapproved cloud deployment.
-   Unlicensed bulk ingestion or indiscriminate web scraping.
-   Claims of novelty, scientific validation, or historical certainty
    without supporting evidence.

## 12. Owner decision and change control

The project owner has final authority over scope, architecture, schema,
API contracts, model selection, evaluation, integration, and release.
Contributors must report technical blockers and propose solutions before
changing an approved contract.

Every change affecting schema, APIs, dependencies, data semantics, or
scope must include: - Reason for change. - Affected components. -
Migration/compatibility plan. - Tests. - Owner approval before merge.

## 13. Definition of done

A feature is complete only when it: - Meets its acceptance criteria. -
Uses real contract-compliant API data. - Preserves provenance and
evidence links. - Handles errors and missing evidence. - Has tests and
documentation. - Works from the documented local setup. - Does not
introduce unapproved architecture or scope changes.
