"""Pydantic request/response models for auth and the source catalogue.

Field names and enums follow API_CONTRACT.md section 2/4 and
DATABASE_SCHEMA.md sections 3.1/3.2. No field names are invented.
"""
from __future__ import annotations

from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

# --- Enums (DATABASE_SCHEMA.md section 2) ---
AttributionConfidence = Literal[
    "unknown", "traditional", "probable", "disputed", "established"
]
SourceStatus = Literal["draft", "verified", "disputed", "withdrawn"]
PassageStatus = Literal["draft", "reviewed", "verified", "disputed"]
EditionType = Literal[
    "manuscript",
    "critical_edition",
    "printed_edition",
    "digital_transcription",
    "translation",
    "other",
]
RightsStatus = Literal[
    "public_domain", "licensed", "permission_required", "restricted", "unknown"
]
TranscriptionMethod = Literal[
    "manual", "ocr", "published_transcription", "mixed", "unknown"
]
InterpretationType = Literal[
    "translation",
    "literal_gloss",
    "commentary",
    "historical_context",
    "scholarly_interpretation",
    "model_generated",
]
InterpretationStatus = Literal[
    "unreviewed", "reviewed", "accepted", "rejected", "disputed"
]
Role = Literal["admin", "researcher", "reviewer"]
AccountStatus = Literal["active", "disabled", "pending"]

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Contract list envelope: total is null unless actually computed."""

    items: list[T]
    limit: int
    offset: int
    total: int | None = None


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- Auth (API_CONTRACT.md section 2) ---
class LoginRequest(Strict):
    username_or_email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=512)


class UserPublic(BaseModel):
    id: str
    username: str
    email: str
    display_name: str
    role: Role
    status: AccountStatus


class LoginResponse(BaseModel):
    user: UserPublic


# --- Sources (API_CONTRACT.md section 4) ---
class SourceCreate(Strict):
    canonical_title: str = Field(min_length=1, max_length=500)
    title_ta: str | None = None
    title_en: str | None = None
    attributed_author: str | None = None
    attribution_confidence: AttributionConfidence = "unknown"
    genre: str | None = None
    tradition_or_collection: str | None = None
    summary: str | None = None
    source_status: SourceStatus = "draft"
    provenance_notes: str | None = None


class SourceUpdate(Strict):
    canonical_title: str | None = Field(default=None, min_length=1, max_length=500)
    title_ta: str | None = None
    title_en: str | None = None
    attributed_author: str | None = None
    attribution_confidence: AttributionConfidence | None = None
    genre: str | None = None
    tradition_or_collection: str | None = None
    summary: str | None = None
    source_status: SourceStatus | None = None
    provenance_notes: str | None = None


class SourceOut(BaseModel):
    id: str
    canonical_title: str
    title_ta: str | None
    title_en: str | None
    attributed_author: str | None
    attribution_confidence: str
    genre: str | None
    tradition_or_collection: str | None
    source_status: str


class EditionSummary(BaseModel):
    id: str
    edition_title: str
    edition_type: str
    language_code: str
    publication_year: int | None
    rights_status: str


class SourceDetailOut(SourceOut):
    summary: str | None
    provenance_notes: str | None
    created_at: datetime
    updated_at: datetime
    editions: list[EditionSummary]


# --- Editions ---
class EditionCreate(Strict):
    edition_title: str = Field(min_length=1, max_length=500)
    editor_or_publisher: str | None = None
    publication_year: int | None = Field(default=None, ge=1, le=3000)
    publication_year_end: int | None = Field(default=None, ge=1, le=3000)
    edition_type: EditionType
    language_code: str = Field(default="ta", min_length=2, max_length=16)
    identifier: str | None = None
    source_url: str | None = None
    archive_or_repository: str | None = None
    rights_status: RightsStatus = "unknown"
    rights_notes: str | None = None
    edition_notes: str | None = None

    @model_validator(mode="after")
    def _year_range(self):
        if (
            self.publication_year is not None
            and self.publication_year_end is not None
            and self.publication_year_end < self.publication_year
        ):
            raise ValueError("publication_year_end must be >= publication_year")
        return self


class EditionOut(BaseModel):
    id: str
    source_id: str
    edition_title: str
    editor_or_publisher: str | None
    publication_year: int | None
    publication_year_end: int | None
    edition_type: str
    language_code: str
    identifier: str | None
    source_url: str | None
    archive_or_repository: str | None
    rights_status: str
    rights_notes: str | None
    edition_notes: str | None
    created_at: datetime
    updated_at: datetime


# --- Passages ---
class PassageCreate(Strict):
    locator: str = Field(min_length=1, max_length=500)
    original_text: str = Field(min_length=1)
    normalized_text: str | None = None
    passage_code: str | None = Field(default=None, max_length=200)
    sequence_number: int | None = Field(default=None, ge=1)
    language_code: str = Field(default="ta", min_length=2, max_length=16)
    transcription_method: TranscriptionMethod = "unknown"
    transcription_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    editorial_notes: str | None = None


class PassageOut(BaseModel):
    id: str
    source_edition_id: str
    passage_code: str | None
    sequence_number: int | None
    locator: str
    original_text: str
    normalized_text: str | None
    language_code: str
    transcription_method: str
    transcription_confidence: float | None
    status: str
    text_checksum: str | None
    created_at: datetime


# --- Interpretations and revisions ---
class InterpretationCreate(Strict):
    interpretation_type: InterpretationType
    language_code: str = Field(min_length=2, max_length=16)
    body: str = Field(min_length=1)
    author_or_model: str | None = None
    model_version: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    source_reference: str | None = None

    @model_validator(mode="after")
    def _model_identity_required(self):
        # Contract section 4: model-generated content must include model identity.
        if self.interpretation_type == "model_generated" and not (
            self.author_or_model and self.model_version
        ):
            raise ValueError(
                "model_generated interpretations require author_or_model and model_version"
            )
        return self


class InterpretationOut(BaseModel):
    id: str
    passage_id: str
    interpretation_type: str
    language_code: str
    body: str
    author_or_model: str | None
    model_version: str | None
    confidence: float | None
    status: str
    source_reference: str | None
    created_at: datetime


class RevisionOut(BaseModel):
    id: str
    passage_id: str
    revision_number: int
    original_text_snapshot: str
    normalized_text_snapshot: str | None
    change_reason: str
    changed_by: str | None
    created_at: datetime
