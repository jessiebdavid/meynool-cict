"""Literary source catalogue routes — API_CONTRACT.md section 4.

All 12 catalogue operations, validated against API_CONTRACT.md section 4,
openapi.yaml and DATABASE_SCHEMA.md sections 3.2/4:

    GET    /api/v1/sources
    POST   /api/v1/sources
    GET    /api/v1/sources/{source_id}
    PATCH  /api/v1/sources/{source_id}
    GET    /api/v1/editions
    POST   /api/v1/sources/{source_id}/editions
    GET    /api/v1/editions/{edition_id}
    GET    /api/v1/passages
    POST   /api/v1/editions/{edition_id}/passages
    GET    /api/v1/passages/{passage_id}
    GET    /api/v1/passages/{passage_id}/interpretations
    POST   /api/v1/passages/{passage_id}/interpretations
    GET    /api/v1/passages/{passage_id}/revisions

Authorization (openapi x-required-roles): reads need an authenticated
account (researcher/reviewer; admin included); writes need "admin or
authorized curator", interpreted as role in {admin, researcher} — v1 has
no separate curator role (see report note).

Provenance rules honored here: q on /passages searches stored source text
only (never interpretations); original_text is never updated by any route;
source_reference/identifiers/source_url/notes are stored and returned;
model-generated interpretations require model identity and stay unreviewed.
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.schemas import (
    EditionCreate,
    EditionOut,
    EditionType,
    InterpretationCreate,
    InterpretationOut,
    Page,
    PassageCreate,
    PassageOut,
    PassageStatus,
    RightsStatus,
    RevisionOut,
    SourceCreate,
    SourceDetailOut,
    SourceOut,
    SourceStatus,
    SourceUpdate,
)
from app.security import get_current_user, require_researcher

router = APIRouter(prefix="/api/v1", tags=["Sources"])

_SOURCE_COLUMNS = (
    "s.id, s.canonical_title, s.title_ta, s.title_en, s.attributed_author, "
    "s.attribution_confidence, s.genre, s.tradition_or_collection, "
    "s.source_status::text AS source_status"
)
# Unprefixed variant for INSERT/UPDATE ... RETURNING (no table alias there).
_SOURCE_RETURNING = (
    "id, canonical_title, title_ta, title_en, attributed_author, "
    "attribution_confidence, genre, tradition_or_collection, "
    "source_status::text AS source_status"
)
_EDITION_COLUMNS = (
    "e.id, e.source_id, e.edition_title, e.editor_or_publisher, e.publication_year, "
    "e.publication_year_end, e.edition_type, e.language_code, e.identifier, e.source_url, "
    "e.archive_or_repository, e.rights_status, e.rights_notes, e.edition_notes, "
    "e.created_at, e.updated_at"
)
_PASSAGE_COLUMNS = (
    "p.id, p.source_edition_id, p.passage_code, p.sequence_number, p.locator, "
    "p.original_text, p.normalized_text, p.language_code, p.transcription_method, "
    "p.transcription_confidence, p.status::text AS status, p.text_checksum, p.created_at"
)
_INTERPRETATION_COLUMNS = (
    "i.id, i.passage_id, i.interpretation_type, i.language_code, i.body, "
    "i.author_or_model, i.model_version, i.confidence, i.status, i.source_reference, "
    "i.created_at"
)
_REVISION_COLUMNS = (
    "r.id, r.passage_id, r.revision_number, r.original_text_snapshot, "
    "r.normalized_text_snapshot, r.change_reason, r.changed_by, r.created_at"
)

# GET /sources `sort`: the contract names the parameter but not its values.
# Only these explicit values are honored; anything else is a 422 rather than
# a silently ignored order. Deterministic id tie-break keeps pagination stable.
_SOURCE_SORTS = {
    "canonical_title": "s.canonical_title ASC, s.id ASC",
    "-canonical_title": "s.canonical_title DESC, s.id ASC",
    "created_at": "s.created_at ASC, s.id ASC",
    "-created_at": "s.created_at DESC, s.id ASC",
}
_DEFAULT_SOURCE_SORT = "canonical_title"


def _serialize(row) -> dict:
    """Row -> JSON-safe dict: UUIDs to strings, Decimals to floats (contract 1.1)."""
    data = dict(row)
    for key, value in data.items():
        if isinstance(value, uuid.UUID):
            data[key] = str(value)
        elif isinstance(value, Decimal):
            data[key] = float(value)
    return data


def _like(term: str) -> str:
    """Substring pattern for ILIKE with escaped wildcards (literal search)."""
    escaped = (
        term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    )
    return f"%{escaped}%"


def _page(items, limit: int, offset: int, total: int) -> dict:
    return {"items": items, "limit": limit, "offset": offset, "total": total}


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=404, detail=detail)


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------


@router.get("/sources", response_model=Page[SourceOut])
def list_sources(
    q: str | None = Query(None, max_length=500),
    tradition_or_collection: str | None = Query(None, max_length=500),
    language_code: str | None = Query(None, min_length=2, max_length=16),
    source_status: SourceStatus | None = None,
    sort: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
) -> dict:
    order = _SOURCE_SORTS.get(sort or _DEFAULT_SOURCE_SORT)
    if order is None:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported sort value: {sort!r}; "
            f"expected one of {sorted(_SOURCE_SORTS)}",
        )
    where = ["1=1"]
    params: dict = {}
    if q:
        where.append(
            "(s.canonical_title ILIKE :q OR s.title_ta ILIKE :q "
            "OR s.title_en ILIKE :q OR s.attributed_author ILIKE :q)"
        )
        params["q"] = _like(q)
    if tradition_or_collection:
        where.append("s.tradition_or_collection = :toc")
        params["toc"] = tradition_or_collection
    if language_code:
        # Sources have no language column; language lives on editions (3.2).
        where.append(
            "EXISTS (SELECT 1 FROM source_editions e "
            "WHERE e.source_id = s.id AND e.language_code = :lc)"
        )
        params["lc"] = language_code
    if source_status:
        where.append("s.source_status = :ss")
        params["ss"] = source_status
    where_sql = " AND ".join(where)
    total = conn.execute(
        text(f"SELECT count(*) FROM literary_sources s WHERE {where_sql}"), params
    ).scalar()
    rows = conn.execute(
        text(
            f"SELECT {_SOURCE_COLUMNS} FROM literary_sources s WHERE {where_sql} "
            f"ORDER BY {order} LIMIT :limit OFFSET :offset"
        ),
        {**params, "limit": limit, "offset": offset},
    ).mappings().all()
    return _page([_serialize(r) for r in rows], limit, offset, total)


@router.post("/sources", response_model=SourceOut, status_code=201)
def create_source(
    payload: SourceCreate,
    user: dict = Depends(require_researcher),
    conn=Depends(get_db),
) -> dict:
    params = payload.model_dump()
    params["created_by"] = user["id"]
    row = conn.execute(
        text(
            "INSERT INTO literary_sources ("
            "canonical_title, title_ta, title_en, attributed_author, "
            "attribution_confidence, genre, tradition_or_collection, summary, "
            "source_status, provenance_notes, created_by"
            ") VALUES ("
            ":canonical_title, :title_ta, :title_en, :attributed_author, "
            ":attribution_confidence, :genre, :tradition_or_collection, :summary, "
            ":source_status, :provenance_notes, :created_by"
            f") RETURNING {_SOURCE_RETURNING}"
        ),
        params,
    ).mappings().one()
    return _serialize(row)


@router.get("/sources/{source_id}", response_model=SourceDetailOut)
def get_source(
    source_id: UUID,
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
) -> dict:
    row = conn.execute(
        text(
            "SELECT s.id, s.canonical_title, s.title_ta, s.title_en, s.attributed_author, "
            "s.attribution_confidence, s.genre, s.tradition_or_collection, "
            "s.source_status::text AS source_status, s.summary, s.provenance_notes, "
            "s.created_at, s.updated_at "
            "FROM literary_sources s WHERE s.id = :id"
        ),
        {"id": str(source_id)},
    ).mappings().first()
    if row is None:
        raise _not_found("Source not found")
    editions = conn.execute(
        text(
            "SELECT id, edition_title, edition_type, language_code, publication_year, "
            "rights_status FROM source_editions WHERE source_id = :id "
            "ORDER BY publication_year ASC NULLS LAST, created_at ASC, id ASC"
        ),
        {"id": str(source_id)},
    ).mappings().all()
    detail = _serialize(row)
    detail["editions"] = [_serialize(e) for e in editions]
    return detail


@router.patch("/sources/{source_id}", response_model=SourceOut)
def update_source(
    source_id: UUID,
    payload: SourceUpdate,
    user: dict = Depends(require_researcher),
    conn=Depends(get_db),
) -> dict:
    provided = payload.model_fields_set
    if not provided:  # openapi SourcePatchRequest minProperties: 1
        raise HTTPException(status_code=422, detail="At least one field must be provided")
    # Field names come from our own model definition, never from raw input keys.
    assignments = ", ".join(f"{field} = :{field}" for field in sorted(provided))
    params = {field: getattr(payload, field) for field in provided}
    params["id"] = str(source_id)
    row = conn.execute(
        text(
            f"UPDATE literary_sources SET {assignments}, updated_at = now() "
            f"WHERE id = :id RETURNING {_SOURCE_RETURNING}"
        ),
        params,
    ).mappings().first()
    if row is None:
        raise _not_found("Source not found")
    # Attribution confidence/status changes are recorded by whoever approves
    # the audit_logs migration (0012); no audit table exists before then.
    return _serialize(row)


# --------------------------------------------------------------------------
# Editions
# --------------------------------------------------------------------------


@router.get("/editions", response_model=Page[EditionOut])
def list_editions(
    source_id: UUID | None = None,
    language_code: str | None = Query(None, min_length=2, max_length=16),
    edition_type: EditionType | None = None,
    rights_status: RightsStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
) -> dict:
    where = ["1=1"]
    params: dict = {}
    if source_id:
        where.append("e.source_id = :sid")
        params["sid"] = str(source_id)
    if language_code:
        where.append("e.language_code = :lc")
        params["lc"] = language_code
    if edition_type:
        where.append("e.edition_type = :et")
        params["et"] = edition_type
    if rights_status:
        where.append("e.rights_status = :rs")
        params["rs"] = rights_status
    where_sql = " AND ".join(where)
    total = conn.execute(
        text(f"SELECT count(*) FROM source_editions e WHERE {where_sql}"), params
    ).scalar()
    rows = conn.execute(
        text(
            f"SELECT {_EDITION_COLUMNS} FROM source_editions e WHERE {where_sql} "
            "ORDER BY e.created_at ASC, e.id ASC LIMIT :limit OFFSET :offset"
        ),
        {**params, "limit": limit, "offset": offset},
    ).mappings().all()
    return _page([_serialize(r) for r in rows], limit, offset, total)


@router.post("/sources/{source_id}/editions", response_model=EditionOut, status_code=201)
def create_edition(
    source_id: UUID,
    payload: EditionCreate,
    user: dict = Depends(require_researcher),
    conn=Depends(get_db),
) -> dict:
    exists = conn.execute(
        text("SELECT 1 FROM literary_sources WHERE id = :id"), {"id": str(source_id)}
    ).scalar()
    if exists is None:
        raise _not_found("Source not found")
    params = payload.model_dump()
    params["source_id"] = str(source_id)
    row = conn.execute(
        text(
            "INSERT INTO source_editions ("
            "source_id, edition_title, editor_or_publisher, publication_year, "
            "publication_year_end, edition_type, language_code, identifier, source_url, "
            "archive_or_repository, rights_status, rights_notes, edition_notes"
            ") VALUES ("
            ":source_id, :edition_title, :editor_or_publisher, :publication_year, "
            ":publication_year_end, :edition_type, :language_code, :identifier, :source_url, "
            ":archive_or_repository, :rights_status, :rights_notes, :edition_notes"
            ") RETURNING id, source_id, edition_title, editor_or_publisher, "
            "publication_year, publication_year_end, edition_type, language_code, "
            "identifier, source_url, archive_or_repository, rights_status, rights_notes, "
            "edition_notes, created_at, updated_at"
        ),
        params,
    ).mappings().one()
    return _serialize(row)


@router.get("/editions/{edition_id}", response_model=EditionOut)
def get_edition(
    edition_id: UUID,
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
) -> dict:
    row = conn.execute(
        text(f"SELECT {_EDITION_COLUMNS} FROM source_editions e WHERE e.id = :id"),
        {"id": str(edition_id)},
    ).mappings().first()
    if row is None:
        raise _not_found("Edition not found")
    return _serialize(row)


# --------------------------------------------------------------------------
# Passages
# --------------------------------------------------------------------------


@router.get("/passages", response_model=Page[PassageOut])
def list_passages(
    q: str | None = Query(None, max_length=500),
    source_id: UUID | None = None,
    edition_id: UUID | None = None,
    status: PassageStatus | None = None,
    language_code: str | None = Query(None, min_length=2, max_length=16),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
) -> dict:
    where = ["1=1"]
    params: dict = {}
    if q:
        # Stored source text only: never matches interpretations (section 4).
        where.append("(p.original_text ILIKE :q OR p.normalized_text ILIKE :q)")
        params["q"] = _like(q)
    if source_id:
        where.append(
            "EXISTS (SELECT 1 FROM source_editions e "
            "WHERE e.id = p.source_edition_id AND e.source_id = :sid)"
        )
        params["sid"] = str(source_id)
    if edition_id:
        where.append("p.source_edition_id = :eid")
        params["eid"] = str(edition_id)
    if status:
        where.append("p.status = :st")
        params["st"] = status
    if language_code:
        where.append("p.language_code = :lc")
        params["lc"] = language_code
    where_sql = " AND ".join(where)
    total = conn.execute(
        text(f"SELECT count(*) FROM passages p WHERE {where_sql}"), params
    ).scalar()
    rows = conn.execute(
        text(
            f"SELECT {_PASSAGE_COLUMNS} FROM passages p WHERE {where_sql} "
            "ORDER BY p.created_at ASC, p.id ASC LIMIT :limit OFFSET :offset"
        ),
        {**params, "limit": limit, "offset": offset},
    ).mappings().all()
    return _page([_serialize(r) for r in rows], limit, offset, total)


@router.post("/editions/{edition_id}/passages", response_model=PassageOut, status_code=201)
def create_passage(
    edition_id: UUID,
    payload: PassageCreate,
    user: dict = Depends(require_researcher),
    conn=Depends(get_db),
) -> dict:
    exists = conn.execute(
        text("SELECT 1 FROM source_editions WHERE id = :id"), {"id": str(edition_id)}
    ).scalar()
    if exists is None:
        raise _not_found("Edition not found")
    params = payload.model_dump()
    params["source_edition_id"] = str(edition_id)
    params["created_by"] = user["id"]
    try:
        row = conn.execute(
            text(
                "INSERT INTO passages ("
                "source_edition_id, passage_code, sequence_number, locator, original_text, "
                "normalized_text, language_code, transcription_method, "
                "transcription_confidence, editorial_notes, created_by"
                ") VALUES ("
                ":source_edition_id, :passage_code, :sequence_number, :locator, :original_text, "
                ":normalized_text, :language_code, :transcription_method, "
                ":transcription_confidence, :editorial_notes, :created_by"
                ") RETURNING id, source_edition_id, passage_code, sequence_number, locator, "
                "original_text, normalized_text, language_code, transcription_method, "
                "transcription_confidence, status::text AS status, text_checksum, created_at"
            ),
            params,
        ).mappings().one()
    except IntegrityError:
        # Partial unique indexes of section 3.2 (passage_code/sequence per edition).
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="A passage with this passage_code or sequence_number "
            "already exists in this edition",
        ) from None
    return _serialize(row)


@router.get("/passages/{passage_id}", response_model=PassageOut)
def get_passage(
    passage_id: UUID,
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
) -> dict:
    row = conn.execute(
        text(f"SELECT {_PASSAGE_COLUMNS} FROM passages p WHERE p.id = :id"),
        {"id": str(passage_id)},
    ).mappings().first()
    if row is None:
        raise _not_found("Passage not found")
    return _serialize(row)


# --------------------------------------------------------------------------
# Interpretations and revisions
# --------------------------------------------------------------------------


def _require_passage(conn, passage_id: UUID) -> None:
    exists = conn.execute(
        text("SELECT 1 FROM passages WHERE id = :id"), {"id": str(passage_id)}
    ).scalar()
    if exists is None:
        raise _not_found("Passage not found")


@router.get(
    "/passages/{passage_id}/interpretations", response_model=Page[InterpretationOut]
)
def list_interpretations(
    passage_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
) -> dict:
    _require_passage(conn, passage_id)
    params = {"pid": str(passage_id)}
    total = conn.execute(
        text("SELECT count(*) FROM interpretations WHERE passage_id = :pid"), params
    ).scalar()
    rows = conn.execute(
        text(
            f"SELECT {_INTERPRETATION_COLUMNS} FROM interpretations i "
            "WHERE i.passage_id = :pid ORDER BY i.created_at ASC, i.id ASC "
            "LIMIT :limit OFFSET :offset"
        ),
        {**params, "limit": limit, "offset": offset},
    ).mappings().all()
    return _page([_serialize(r) for r in rows], limit, offset, total)


@router.post(
    "/passages/{passage_id}/interpretations",
    response_model=InterpretationOut,
    status_code=201,
)
def create_interpretation(
    passage_id: UUID,
    payload: InterpretationCreate,
    user: dict = Depends(require_researcher),
    conn=Depends(get_db),
) -> dict:
    _require_passage(conn, passage_id)
    params = payload.model_dump()
    params["passage_id"] = str(passage_id)
    params["created_by"] = user["id"]
    # status is omitted deliberately: the DB default 'unreviewed' applies, so
    # model-generated content is unreviewed by default (section 4).
    row = conn.execute(
        text(
            "INSERT INTO interpretations ("
            "passage_id, interpretation_type, language_code, body, author_or_model, "
            "model_version, confidence, source_reference, created_by"
            ") VALUES ("
            ":passage_id, :interpretation_type, :language_code, :body, :author_or_model, "
            ":model_version, :confidence, :source_reference, :created_by"
            ") RETURNING id, passage_id, interpretation_type, language_code, body, "
            "author_or_model, model_version, confidence, status, source_reference, created_at"
        ),
        params,
    ).mappings().one()
    return _serialize(row)


@router.get("/passages/{passage_id}/revisions", response_model=Page[RevisionOut])
def list_revisions(
    passage_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    conn=Depends(get_db),
) -> dict:
    _require_passage(conn, passage_id)
    params = {"pid": str(passage_id)}
    total = conn.execute(
        text("SELECT count(*) FROM passage_revisions WHERE passage_id = :pid"), params
    ).scalar()
    rows = conn.execute(
        text(
            f"SELECT {_REVISION_COLUMNS} FROM passage_revisions r "
            "WHERE r.passage_id = :pid ORDER BY r.revision_number DESC "
            "LIMIT :limit OFFSET :offset"
        ),
        {**params, "limit": limit, "offset": offset},
    ).mappings().all()
    return _page([_serialize(r) for r in rows], limit, offset, total)
