"""Explicit review of an existing assessment's RAT scope; no legal decision."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.licitud import LegalAssessmentScopeIn


class ScopePreview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scope: LegalAssessmentScopeIn


class ScopeApply(ScopePreview):
    data_kind: Literal["ficticios"]
    request_id: UUID
    review_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    reason: str = Field(min_length=1, max_length=5000)

    @field_validator("reason")
    @classmethod
    def reason_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Explica el motivo del cambio de alcance")
        return value.strip()
