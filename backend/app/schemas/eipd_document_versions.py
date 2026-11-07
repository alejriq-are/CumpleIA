"""Registration accepts concurrency tokens, never client-supplied document content."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EipdVersionRegister(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    request_id: UUID
    data_kind: Literal["ficticios"]
    expected_source_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_latest_version: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=4000)


class EipdReviewRegister(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    request_id: UUID
    data_kind: Literal["ficticios"]
    authority_id: UUID
    expected_previous_id: UUID | None
    outcome: Literal["favorable", "requiere_cambios", "no_continuar"]
    reason: str = Field(min_length=1, max_length=4000)
    reference: str = Field(min_length=1, max_length=1000)


class EipdReviewAuthority(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    subject_id: UUID
    action: Literal["grant", "revoke"]
    expected_sequence: int = Field(ge=0)
    expires_at: datetime | None = None
    reason: str = Field(min_length=1, max_length=4000)
    reference: str = Field(min_length=1, max_length=1000)


class EipdDecisionAuthority(EipdReviewAuthority):
    compatibility_reason: str | None = Field(
        default=None, min_length=1, max_length=4000
    )


class EipdDecisionRegister(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    request_id: UUID
    data_kind: Literal["ficticios"]
    expected_authority_id: UUID
    expected_review_id: UUID | None
    expected_decision_id: UUID | None
    outcome: Literal["acepta", "requiere_cambios", "rechaza"]
    reason: str = Field(min_length=1, max_length=4000)
    reference: str = Field(min_length=1, max_length=1000)
