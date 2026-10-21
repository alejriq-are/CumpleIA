"""Versioned internal qualitative methodology; never a legal approval."""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Text = Annotated[str, Field(max_length=5000)]
Identifier = Annotated[
    str, Field(min_length=1, max_length=100, pattern=r"^\S(?:.*\S)?$")
]
Rank = Annotated[int, Field(strict=True, ge=1, le=4)]


class Closed(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Rating(Closed):
    probability: Rank | None = None
    impact: Rank | None = None
    rationale: Text = ""


class RiskRating(Closed):
    risk_id: Identifier
    harm: Text = ""
    frequency_context: Text = ""
    inherent: Rating = Field(default_factory=Rating)
    projected: Rating = Field(default_factory=Rating)
    residual: Rating = Field(default_factory=Rating)
    action: Text = ""
    owner_reference: Text = ""
    review_on: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class ControlRating(Closed):
    measure_id: Identifier
    dimension: Literal["probabilidad", "impacto", "ambos"] | None = None
    effectiveness: Literal["no_evaluada", "insuficiente", "parcial", "suficiente"] = (
        "no_evaluada"
    )
    status: Literal["propuesta", "en_implementacion", "verificada"] = "propuesta"
    rationale: Text = ""
    evidence_references: list[Identifier] = Field(default_factory=list, max_length=50)


class RiskMethodology(Closed):
    methodology: Literal["CUMPLEIA-CUALITATIVA-1"] = "CUMPLEIA-CUALITATIVA-1"
    horizon: Text = "12 meses"
    risks: list[RiskRating] = Field(default_factory=list, max_length=100)
    controls: list[ControlRating] = Field(default_factory=list, max_length=100)


class RiskSave(Closed):
    data_kind: Literal["ficticios"]
    request_id: UUID
    expected_revision: int = Field(default=0, ge=0)
    document_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    analysis: RiskMethodology


class AnnexSave(Closed):
    data_kind: Literal["ficticios"]
    request_id: UUID
    reference: str = Field(pattern=r"^SIMULADA-[A-Za-z0-9_-]{1,90}$")
    filename: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=2000)
    section: Literal[
        "alcance", "base", "necesidad", "riesgos", "medidas", "fuentes", "seguimiento"
    ]
    risk_ids: list[Identifier] = Field(default_factory=list, max_length=100)
    measure_ids: list[Identifier] = Field(default_factory=list, max_length=100)
    content_base64: str = Field(min_length=4, max_length=2796204)
