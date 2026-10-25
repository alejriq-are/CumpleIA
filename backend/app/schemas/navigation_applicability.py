"""Manual documentary determination, independent of legal screening and activation."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Determination(BaseModel):
    model_config = ConfigDict(extra="forbid")
    state: Literal[
        "pendiente", "corresponde", "no_corresponde", "informacion_insuficiente"
    ] = "pendiente"
    reason: str = Field(default="", max_length=5000)

    @model_validator(mode="after")
    def reason_required(self):
        if self.state != "pendiente" and not self.reason.strip():
            raise ValueError("Toda determinación exige fundamento")
        return self


class ApplicabilitySave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data_kind: Literal["ficticios"]
    request_id: UUID
    expected_revision: int = Field(ge=0)
    context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    eipd: Determination
    infancia: Determination
