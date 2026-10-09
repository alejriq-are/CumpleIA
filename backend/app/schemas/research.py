"""Contrato nuevo independiente; no modifica snapshots/hashes historicos M3."""

from typing import Literal

from pydantic import ConfigDict, Field

from app.schemas.licitud import (
    ContractEvidenceV1,
    ContractResponseV1,
    LegalAssessmentScopeIn,
)


class ResearchAssessmentV1(LegalAssessmentScopeIn):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    schema_version: Literal[1] = 1
    purpose_type: (
        Literal["historico", "estadistico", "cientifico", "estudio_investigacion"]
        | None
    ) = None
    purpose_description: str | None = None
    public_interest_analysis: str | None = None
    exclusive_use: ContractResponseV1 | None = None
    exclusivity_controls_analysis: str | None = None
    quality_measures_analysis: str | None = None
    security_measures_analysis: str | None = None
    measures_implemented: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    publication_planned: ContractResponseV1 | None = None
    anonymization_method: str | None = None
    anonymization_analysis: str | None = None
    anonymization_evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    retention_analysis: str | None = None
