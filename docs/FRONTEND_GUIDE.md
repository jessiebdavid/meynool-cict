# Frontend Guide

The starter UI uses React + Vite + TypeScript. The initial dashboard is deliberately an empty-state shell; it does not contain fabricated literary sources, papers, claims, or evaluation metrics.

## Suggested screen order

1. **Overview:** connection status, recent work when real data exists, and clear empty states.
2. **Literary library:** source, edition, language, attribution status, passage locator and provenance.
3. **Scientific literature:** PubMed/Europe PMC identifiers, title, authors, date, abstract availability and source link.
4. **Analysis workspace:** 1D literal source, 2D context, 3D scientific relationships/evidence, 4D chronology.
5. **Claims and evidence:** claim text, relationship, source, citation, reviewer status, contradiction and uncertainty.
6. **Hypothesis review:** rationale, evidence basis, alternative explanations, testability and limitations.
7. **Historical procedures/instruments:** source-supported documentary records with prominent non-clinical framing.
8. **Research workspace:** bookmarks, annotations, reviews and exports with authorization.

## API integration rules

- Use `VITE_API_BASE_URL`; default is `http://127.0.0.1:8000/api/v1`.
- The browser talks to FastAPI only, never directly to PostgreSQL or Ollama.
- Keep API calls in a small service layer rather than scattering `fetch` calls through components.
- Treat API data as untrusted; render source text safely and do not interpret HTML from source records.
- Display source status, evidence relation, uncertainty and provenance as separate fields.
- Never use a model's confidence score as proof that a claim is true.
