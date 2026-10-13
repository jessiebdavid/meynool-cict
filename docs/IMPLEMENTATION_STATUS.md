# Implementation Status

Status is intentionally conservative. A file existing in the repository does not mean the feature is complete.

| Area | Current status | Next action |
|---|---|---|
| Meynool brand and project docs | Present | Validate Tamil spelling/connotations and check trademark/domain availability separately |
| Frontend shell | Starter implemented | Build real screens and connect to implemented API endpoints |
| FastAPI app | Starter implemented | Implement approved API contract incrementally |
| PostgreSQL container | Compose configuration present | Start locally and implement versioned migrations |
| Canonical schema | Specification present | Convert spec into tested migrations; resolve vector dimension after model benchmark |
| Tamil literary ingestion | Not implemented | Select source editions and record rights/provenance |
| PubMed / Europe PMC integration | Not implemented | Implement provider clients and tests |
| Embeddings / hybrid retrieval | Not implemented | Benchmark local embedding models; choose dimension and ranking strategy |
| Ollama model integration | Not implemented | Select and evaluate a locally available model; never assume a model is installed |
| 1D–4D analysis | Design specified, not implemented | Implement structured outputs with citations and uncertainty fields |
| Claim/evidence audit | Design specified, not implemented | Implement claim-level evidence links and reviewer workflow |
| Hallucination evaluation | Not implemented | Create a human-reviewed benchmark and scoring protocol before reporting percentages |
| Authentication and researcher workspace | Specified, not implemented | Implement admin-created accounts, secure sessions and access checks |

## Non-negotiable reporting rule

Do not report made-up counts, accuracy, hallucination percentages, ingestion totals, or system readiness. The UI should display “Not measured yet” or “Not connected” until real measurements exist.
