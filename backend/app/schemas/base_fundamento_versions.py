"""Registration always refers to previously saved material."""

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.eipd_document_versions import EipdReviewAuthority, EipdVersionRegister


class BaseFundamentoVersionRegister(EipdVersionRegister):
    annex_ids: list[UUID] = Field(default_factory=list, max_length=50)


class BaseFundamentoReviewAuthority(EipdReviewAuthority):
    """Faculty scoped to Base y fundamento, independent of EIPD."""


class RequirementResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    criterion_id: str = Field(min_length=1, max_length=100)
    field: str = Field(min_length=1, max_length=300)
    code: str = Field(min_length=1, max_length=100)
    resolution: Literal["no_aplica", "respaldo_equivalente"]
    justification: str = Field(min_length=1, max_length=4000)
    reference: str | None = Field(default=None, min_length=1, max_length=1000)

    @model_validator(mode="after")
    def equivalent_requires_reference(self):
        if self.resolution == "respaldo_equivalente" and self.reference is None:
            raise ValueError("Indica dónde consultar el respaldo equivalente")
        return self


class FollowupObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    description: str = Field(min_length=1, max_length=4000)
    responsible: str = Field(min_length=1, max_length=300)
    due_on: date


class BaseFundamentoReviewRegister(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    request_id: UUID
    data_kind: Literal["ficticios"]
    authority_id: UUID
    expected_previous_id: UUID | None
    outcome: Literal["favorable", "requiere_cambios", "desfavorable"]
    reason: str = Field(min_length=1, max_length=4000)
    reference: str = Field(min_length=1, max_length=1000)
    resolutions: list[RequirementResolution] = Field(
        default_factory=list, max_length=250
    )
    observations: list[FollowupObservation] = Field(default_factory=list, max_length=50)
