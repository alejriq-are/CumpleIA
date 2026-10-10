"""Identidad de material revisado; contrato interno, no entrada HTTP."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EipdReviewContextMetadataV1(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    metadata_schema_version: Literal[1]
    resolution_binding_version: Literal[1, 2]
    context_schema_version: Literal[1, 2]
    research_coverage: Literal["no_cubierta", "contexto_v2"]
    document_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    research_material_hash: str | None = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator(
        "metadata_schema_version",
        "resolution_binding_version",
        "context_schema_version",
        mode="before",
    )
    @classmethod
    def strict_version(cls, value):
        if type(value) is not int:
            raise ValueError("Version exige entero estricto")
        return value

    @model_validator(mode="after")
    def coherent_coverage(self):
        if self.resolution_binding_version != self.context_schema_version:
            raise ValueError("Versiones de resolucion/contexto discordantes")
        expected = "contexto_v2" if self.context_schema_version == 2 else "no_cubierta"
        if self.research_coverage != expected:
            raise ValueError("Cobertura incompatible con la version")
        if self.context_schema_version == 1 and self.research_material_hash is not None:
            raise ValueError("Contexto V1 no acredita material research")
        return self
