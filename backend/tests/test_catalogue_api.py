"""Contract tests for the source catalogue routes (API_CONTRACT.md section 4).

Unmarked tests need no database: every catalogue route answers 401 with the
contract envelope before any connection is attempted. Tests marked
``db_integration`` run the full catalogue workflow against live PostgreSQL
and are skipped honestly when it is unreachable.
"""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

API = "/api/v1"

# All 13 catalogue operations from API_CONTRACT.md section 4, as (method, path template).
READ_ROUTES = [
    ("GET", "/sources"),
    ("GET", "/sources/{uuid}"),
    ("GET", "/editions"),
    ("GET", "/editions/{uuid}"),
    ("GET", "/passages"),
    ("GET", "/passages/{uuid}"),
    ("GET", "/passages/{uuid}/interpretations"),
    ("GET", "/passages/{uuid}/revisions"),
]
WRITE_ROUTES = [
    ("POST", "/sources", {"canonical_title": "Unauthenticated attempt"}),
    ("PATCH", "/sources/{uuid}", {"canonical_title": "Unauthenticated attempt"}),
    (
        "POST",
        "/sources/{uuid}/editions",
        {"edition_title": "Unauthenticated attempt", "edition_type": "printed_edition"},
    ),
    (
        "POST",
        "/editions/{uuid}/passages",
        {
            "locator": "p.1",
            "original_text": "Unauthenticated attempt",
            "language_code": "ta",
            "transcription_method": "manual",
        },
    ),
    (
        "POST",
        "/passages/{uuid}/interpretations",
        {
            "interpretation_type": "translation",
            "language_code": "en",
            "body": "Unauthenticated attempt",
        },
    ),
]


def _path(template: str) -> str:
    return API + template.format(uuid=uuid.uuid4())


# --------------------------------------------------------------------------
# No database required: unauthenticated behavior of every route
# --------------------------------------------------------------------------


@pytest.mark.parametrize("method,path_template", READ_ROUTES)
def test_read_routes_require_authentication(client, method, path_template):
    response = client.request(method, _path(path_template))
    assert response.status_code == 401, response.text
    error = response.json()["error"]
    assert error["code"] == "UNAUTHORIZED"
    assert error["request_id"]
    assert response.headers["X-Request-ID"] == error["request_id"]


@pytest.mark.parametrize("method,path_template,body", WRITE_ROUTES)
def test_write_routes_require_authentication(client, method, path_template, body):
    response = client.request(method, _path(path_template), json=body)
    assert response.status_code == 401, response.text
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


# --------------------------------------------------------------------------
# Live database: full catalogue workflow
# --------------------------------------------------------------------------


@pytest.fixture
def researcher_session(client, seed_user, test_password):
    """Logged-in client for a throwaway researcher account."""
    username = seed_user(role="researcher")
    response = client.post(
        f"{API}/auth/login",
        json={"username_or_email": username, "password": test_password},
    )
    assert response.status_code == 200, response.text
    return client


@pytest.fixture
def cleanup_rows(db_engine):
    """Collects (table, id) pairs to delete after a test, in insert order."""
    rows: list[tuple[str, str]] = []
    yield rows
    if rows:
        with db_engine.begin() as conn:
            for table, row_id in reversed(rows):
                conn.execute(
                    text(f"DELETE FROM {table} WHERE id = :id"), {"id": row_id}
                )


@pytest.mark.db_integration
def test_full_catalogue_workflow(
    researcher_session, db_engine, cleanup_rows
):
    client = researcher_session
    marker = uuid.uuid4().hex  # isolates every list assertion from other data
    title = f"ZZTEST source {marker}"
    source_text = f"உவமை உரை {marker}"  # Tamil round-trip (schema section 7 test 17)

    # --- create source (POST /sources) -----------------------------------
    created = client.post(
        f"{API}/sources",
        json={
            "canonical_title": title,
            "title_ta": "சோதனை",
            "title_en": "A test work",
            "attributed_author": "Traditional attribution",
            "attribution_confidence": "traditional",
            "genre": "poetry",
            "tradition_or_collection": "Sangam",
            "summary": "Fixture summary",
            "provenance_notes": "Fixture provenance",
        },
    )
    assert created.status_code == 201, created.text
    source = created.json()
    source_id = source["id"]
    cleanup_rows.append(("literary_sources", source_id))
    assert source["canonical_title"] == title
    assert source["attribution_confidence"] == "traditional"
    assert source["source_status"] == "draft"  # documented default
    assert set(source) == {
        "id", "canonical_title", "title_ta", "title_en", "attributed_author",
        "attribution_confidence", "genre", "tradition_or_collection", "source_status",
    }

    # --- list with q filter (GET /sources) --------------------------------
    listed = client.get(f"{API}/sources", params={"q": title})
    assert listed.status_code == 200
    body = listed.json()
    assert body["limit"] == 20 and body["offset"] == 0
    assert body["total"] == 1
    assert [item["id"] for item in body["items"]] == [source_id]

    # --- filters, sort and pagination -------------------------------------
    filtered = client.get(
        f"{API}/sources",
        params={"q": title, "source_status": "verified"},
    )
    assert filtered.status_code == 200 and filtered.json()["total"] == 0
    filtered = client.get(
        f"{API}/sources",
        params={"q": title, "source_status": "draft"},
    )
    assert filtered.json()["total"] == 1

    by_tradition = client.get(
        f"{API}/sources", params={"tradition_or_collection": "Sangam"}
    )
    assert by_tradition.status_code == 200
    assert any(item["id"] == source_id for item in by_tradition.json()["items"])

    sorted_ok = client.get(f"{API}/sources", params={"sort": "-created_at"})
    assert sorted_ok.status_code == 200
    bad_sort = client.get(f"{API}/sources", params={"sort": "bogus_field"})
    assert bad_sort.status_code == 422
    assert bad_sort.json()["error"]["code"] == "VALIDATION_ERROR"

    bad_status = client.get(f"{API}/sources", params={"source_status": "not_a_status"})
    assert bad_status.status_code == 422

    assert client.get(f"{API}/sources", params={"limit": 0}).status_code == 422
    assert client.get(f"{API}/sources", params={"limit": 101}).status_code == 422
    assert client.get(f"{API}/sources", params={"offset": -1}).status_code == 422
    limited = client.get(f"{API}/sources", params={"q": title, "limit": 1})
    assert len(limited.json()["items"]) == 1

    # --- source detail with edition summaries (GET /sources/{id}) ---------
    detail = client.get(f"{API}/sources/{source_id}")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["provenance_notes"] == "Fixture provenance"
    assert detail_body["editions"] == []
    assert "created_at" in detail_body and "updated_at" in detail_body

    # --- patch source (PATCH /sources/{id}) -------------------------------
    empty_patch = client.patch(f"{API}/sources/{source_id}", json={})
    assert empty_patch.status_code == 422  # openapi minProperties: 1

    patched = client.patch(
        f"{API}/sources/{source_id}",
        json={"attribution_confidence": "disputed", "source_status": "verified"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["attribution_confidence"] == "disputed"
    assert patched.json()["source_status"] == "verified"
    assert patched.json()["canonical_title"] == title  # untouched fields remain

    # --- create + list + get edition --------------------------------------
    edition_resp = client.post(
        f"{API}/sources/{source_id}/editions",
        json={
            "edition_title": "Test edition",
            "editor_or_publisher": "Test editor",
            "publication_year": 1923,
            "publication_year_end": 1925,
            "edition_type": "printed_edition",
            "language_code": "ta",
            "identifier": f"ISBN-TEST-{marker}",
            "source_url": "https://example.test/edition",
            "archive_or_repository": "Test archive",
            "rights_status": "public_domain",
            "rights_notes": "Fixture rights",
            "edition_notes": "Fixture note",
        },
    )
    assert edition_resp.status_code == 201, edition_resp.text
    edition = edition_resp.json()
    edition_id = edition["id"]
    cleanup_rows.append(("source_editions", edition_id))
    assert edition["source_id"] == source_id
    assert edition["publication_year_end"] == 1925
    assert edition["rights_status"] == "public_domain"

    editions_list = client.get(f"{API}/editions", params={"source_id": source_id})
    assert editions_list.status_code == 200
    assert editions_list.json()["total"] == 1
    by_type = client.get(f"{API}/editions", params={"edition_type": "manuscript"})
    assert by_type.status_code == 200 and by_type.json()["total"] == 0
    assert client.get(
        f"{API}/editions", params={"edition_type": "not_a_type"}
    ).status_code == 422

    edition_detail = client.get(f"{API}/editions/{edition_id}")
    assert edition_detail.status_code == 200
    edition_detail_body = edition_detail.json()
    assert edition_detail_body["identifier"] == f"ISBN-TEST-{marker}"
    assert edition_detail_body["source_url"] == "https://example.test/edition"
    assert edition_detail_body["archive_or_repository"] == "Test archive"
    assert edition_detail_body["rights_notes"] == "Fixture rights"

    # source detail now summarizes the edition
    detail_after = client.get(f"{API}/sources/{source_id}").json()
    assert [e["id"] for e in detail_after["editions"]] == [edition_id]
    assert detail_after["editions"][0]["edition_type"] == "printed_edition"

    # --- create passages ----------------------------------------------------
    passage_resp = client.post(
        f"{API}/editions/{edition_id}/passages",
        json={
            "locator": "p. 1, line 1",
            "original_text": source_text,
            "sequence_number": 1,
            "language_code": "ta",
            "transcription_method": "manual",
            "transcription_confidence": 0.9,
            "editorial_notes": "Fixture note",
        },
    )
    assert passage_resp.status_code == 201, passage_resp.text
    passage = passage_resp.json()
    passage_id = passage["id"]
    cleanup_rows.append(("passages", passage_id))
    assert passage["status"] == "draft"  # documented default
    assert passage["text_checksum"] is None  # no checksum algorithm is specified
    assert passage["original_text"] == source_text  # Tamil without corruption

    duplicate = client.post(
        f"{API}/editions/{edition_id}/passages",
        json={
            "locator": "p. 2",
            "original_text": "Another line",
            "sequence_number": 1,  # partial unique index of section 3.2
            "language_code": "ta",
            "transcription_method": "manual",
        },
    )
    assert duplicate.status_code == 409, duplicate.text
    assert duplicate.json()["error"]["code"] == "CONFLICT"

    passage_search = client.get(f"{API}/passages", params={"q": marker})
    assert passage_search.status_code == 200
    assert passage_search.json()["total"] == 1
    assert passage_search.json()["items"][0]["id"] == passage_id

    by_edition = client.get(f"{API}/passages", params={"edition_id": edition_id})
    assert by_edition.json()["total"] == 1
    by_source = client.get(f"{API}/passages", params={"source_id": source_id})
    assert by_source.json()["total"] == 1
    by_status = client.get(
        f"{API}/passages", params={"source_id": source_id, "status": "verified"}
    )
    assert by_status.json()["total"] == 0
    assert client.get(
        f"{API}/passages", params={"status": "not_a_status"}
    ).status_code == 422

    passage_detail = client.get(f"{API}/passages/{passage_id}")
    assert passage_detail.status_code == 200
    assert passage_detail.json()["locator"] == "p. 1, line 1"
    assert passage_detail.json()["transcription_confidence"] == pytest.approx(0.9)

    # --- interpretations ----------------------------------------------------
    invalid_model = client.post(
        f"{API}/passages/{passage_id}/interpretations",
        json={
            "interpretation_type": "model_generated",
            "language_code": "en",
            "body": "Model output without identity",
        },
    )
    assert invalid_model.status_code == 422  # identity required by section 4

    interp_resp = client.post(
        f"{API}/passages/{passage_id}/interpretations",
        json={
            "interpretation_type": "model_generated",
            "language_code": "en",
            "body": "Model-produced rendering",
            "author_or_model": "test-model",
            "model_version": "0.0-test",
            "confidence": 0.5,
            "source_reference": "edition locator p. 1",
        },
    )
    assert interp_resp.status_code == 201, interp_resp.text
    interp = interp_resp.json()
    cleanup_rows.append(("interpretations", interp["id"]))
    assert interp["status"] == "unreviewed"  # unreviewed by default
    assert interp["source_reference"] == "edition locator p. 1"
    assert interp["passage_id"] == passage_id

    interps = client.get(f"{API}/passages/{passage_id}/interpretations")
    assert interps.status_code == 200
    assert interps.json()["total"] == 1
    assert interps.json()["items"][0]["interpretation_type"] == "model_generated"

    # --- revisions: never fabricated, currently written by a future fix flow
    revisions = client.get(f"{API}/passages/{passage_id}/revisions")
    assert revisions.status_code == 200
    assert revisions.json()["items"] == []
    assert revisions.json()["total"] == 0

    # --- 404s ---------------------------------------------------------------
    missing = uuid.uuid4()
    assert client.get(f"{API}/sources/{missing}").status_code == 404
    assert client.get(f"{API}/editions/{missing}").status_code == 404
    assert client.get(f"{API}/passages/{missing}").status_code == 404
    assert (
        client.get(f"{API}/passages/{missing}/interpretations").status_code == 404
    )
    assert client.get(f"{API}/passages/{missing}/revisions").status_code == 404
    assert (
        client.post(
            f"{API}/sources/{missing}/editions",
            json={"edition_title": "x", "edition_type": "other"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"{API}/editions/{missing}/passages",
            json={
                "locator": "p.1",
                "original_text": "x",
                "language_code": "ta",
                "transcription_method": "manual",
            },
        ).status_code
        == 404
    )

    # 404 responses also use the contract envelope
    not_found = client.get(f"{API}/sources/{missing}")
    error = not_found.json()["error"]
    assert error["code"] == "NOT_FOUND" and error["request_id"]

    # Path params are typed uuid (openapi); malformed id -> validation error.
    # Only observable with a session: authentication precedes path validation.
    malformed = client.get(f"{API}/sources/not-a-uuid")
    assert malformed.status_code == 422
    assert malformed.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.db_integration
def test_reviewer_can_read_but_not_write(
    db_engine, seed_user, test_password, client, cleanup_rows
):
    reviewer = seed_user(role="reviewer")
    login = client.post(
        f"{API}/auth/login",
        json={"username_or_email": reviewer, "password": test_password},
    )
    assert login.status_code == 200

    read = client.get(f"{API}/sources")
    assert read.status_code == 200

    write = client.post(
        f"{API}/sources", json={"canonical_title": "Reviewer attempt"}
    )
    assert write.status_code == 403
    assert write.json()["error"]["code"] == "FORBIDDEN"

    patch = client.patch(f"{API}/sources/{uuid.uuid4()}", json={"genre": "x"})
    assert patch.status_code == 403  # authorization precedes existence lookup


@pytest.mark.db_integration
def test_admin_can_write_catalogue(
    db_engine, seed_user, test_password, client, cleanup_rows
):
    admin = seed_user(role="admin")
    login = client.post(
        f"{API}/auth/login",
        json={"username_or_email": admin, "password": test_password},
    )
    assert login.status_code == 200
    created = client.post(
        f"{API}/sources", json={"canonical_title": f"ZZTEST admin {uuid.uuid4().hex}"}
    )
    assert created.status_code == 201, created.text
    cleanup_rows.append(("literary_sources", created.json()["id"]))
