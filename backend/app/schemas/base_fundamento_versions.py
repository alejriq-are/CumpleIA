"""Registration always refers to previously saved material."""

from uuid import UUID

from pydantic import Field

from app.schemas.eipd_document_versions import EipdVersionRegister


class BaseFundamentoVersionRegister(EipdVersionRegister):
    annex_ids: list[UUID] = Field(default_factory=list, max_length=50)
