"""Registration accepts concurrency tokens, never client-supplied document content."""

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
