"""Contract/OpenAPI consistency checks for the Meynool starter.

Run from backend/: python -m pytest -q
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "API_CONTRACT.md"
OPENAPI_PATH = ROOT / "openapi.yaml"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def load_contract_operations() -> set[tuple[str, str]]:
    operations: set[tuple[str, str]] = set()
    for line in CONTRACT_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^### `(GET|POST|PUT|PATCH|DELETE) (.+)`$", line)
        if match:
            operations.add((match.group(1).lower(), "/" + match.group(2).lstrip("/")))
    return operations


def load_openapi() -> dict[str, Any]:
    return yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))


def load_openapi_operations(spec: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (method, path)
        for path, path_item in spec["paths"].items()
        for method in path_item
        if method in HTTP_METHODS
    }


def test_openapi_operations_match_contract_exactly() -> None:
    contract_operations = load_contract_operations()
    spec = load_openapi()
    openapi_operations = load_openapi_operations(spec)

    assert contract_operations, "No endpoint headings were found in API_CONTRACT.md"
    assert openapi_operations == contract_operations, (
        f"Missing from OpenAPI: {sorted(contract_operations - openapi_operations)}; "
        f"not in contract: {sorted(openapi_operations - contract_operations)}"
    )


def test_operation_ids_are_present_and_unique() -> None:
    spec = load_openapi()
    operation_ids = []
    for path, path_item in spec["paths"].items():
        for method, operation in path_item.items():
            if method in HTTP_METHODS:
                assert operation.get("operationId"), f"Missing operationId: {method.upper()} {path}"
                operation_ids.append(operation["operationId"])
    assert len(operation_ids) == len(set(operation_ids)), "OpenAPI operationId values must be unique"


def test_all_local_component_references_resolve() -> None:
    spec = load_openapi()
    missing: list[str] = []

    def walk(value: Any, location: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "$ref" and isinstance(child, str) and child.startswith("#/components/"):
                    current: Any = spec
                    try:
                        for part in child[2:].split("/"):
                            current = current[part]
                    except (KeyError, TypeError):
                        missing.append(f"{location}: {child}")
                else:
                    walk(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{location}[{index}]")

    walk(spec)
    assert not missing, "Unresolved component references: " + "; ".join(missing)


def test_login_schema_matches_canonical_contract() -> None:
    spec = load_openapi()
    login = spec["components"]["schemas"]["LoginRequest"]
    assert set(login["required"]) == {"username_or_email", "password"}
    assert "username_or_email" in login["properties"]
    assert "email" not in login["properties"]


def test_ingestion_route_matches_canonical_contract() -> None:
    spec = load_openapi()
    assert "post" in spec["paths"]["/science/ingestion-jobs"]
    assert "post" not in spec["paths"].get("/ingestion/jobs", {})
    assert "get" in spec["paths"]["/ingestion/jobs"]


def test_role_and_health_schemas_match_contract() -> None:
    spec = load_openapi()
    schemas = spec["components"]["schemas"]
    assert set(schemas["User"]["properties"]["role"]["enum"]) == {"admin", "researcher", "reviewer"}
    health = schemas["HealthResponse"]
    assert {"embedding_model", "checked_at"}.issubset(set(health["required"]))
    assert "503" in spec["paths"]["/health"]["get"]["responses"]


def test_contract_does_not_expose_public_registration() -> None:
    spec = load_openapi()
    assert not any(path.endswith("/register") for path in spec["paths"])
    assert "RegisterRequest" not in spec["components"]["schemas"]


def test_review_and_evidence_vocabularies_match_contract() -> None:
    schemas = load_openapi()["components"]["schemas"]
    review = schemas["ReviewRequest"]
    assert set(review["required"]) == {"target_type", "target_id", "decision"}
    assert set(review["properties"]["decision"]["enum"]) == {"approve", "revise", "reject", "needs_expert"}
    relation = schemas["ClaimEvidence"]["properties"]["relationship"]["enum"]
    assert set(relation) == {"supports", "contradicts", "qualifies", "contextualizes"}


def test_analysis_hypothesis_limit_matches_contract() -> None:
    schemas = load_openapi()["components"]["schemas"]
    assert schemas["AnalysisRequest"]["properties"]["max_hypotheses"]["maximum"] == 10


def test_only_health_and_login_are_public() -> None:
    spec = load_openapi()
    public_operations = {
        (method, path)
        for path, path_item in spec["paths"].items()
        for method, operation in path_item.items()
        if method in HTTP_METHODS and not operation.get("security")
    }
    assert public_operations == {("get", "/health"), ("post", "/auth/login")}


def test_list_routes_document_contract_pagination() -> None:
    spec = load_openapi()
    list_operations = [
        ("get", "/sources"),
        ("get", "/editions"),
        ("get", "/passages"),
        ("get", "/passages/{passage_id}/interpretations"),
        ("get", "/passages/{passage_id}/revisions"),
        ("get", "/science/publications"),
        ("get", "/ingestion/jobs"),
        ("get", "/analysis"),
        ("get", "/analysis/{analysis_id}/claims"),
        ("get", "/analysis/{analysis_id}/hypotheses"),
        ("get", "/claims/{claim_id}/evidence"),
        ("get", "/procedures"),
        ("get", "/instruments"),
        ("get", "/procedures/{procedure_id}/instruments"),
        ("get", "/reviews"),
        ("get", "/bookmarks"),
        ("get", "/annotations"),
        ("get", "/admin/users"),
        ("get", "/admin/embedding-profiles"),
        ("get", "/admin/ingestion-jobs"),
        ("get", "/admin/audit-logs"),
    ]
    for method, path in list_operations:
        parameters = spec["paths"][path][method].get("parameters", [])
        names = {
            parameter.get("name")
            for parameter in parameters
            if isinstance(parameter, dict) and parameter.get("in") == "query"
        }
        refs = {parameter.get("$ref") for parameter in parameters if isinstance(parameter, dict)}
        assert ("limit" in names or "#/components/parameters/Limit" in refs), f"Missing limit on {path}"
        assert ("offset" in names or "#/components/parameters/Offset" in refs), f"Missing offset on {path}"
