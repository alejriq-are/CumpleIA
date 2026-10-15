"""Sucesores de infancia; solo datos declarados ficticios y decisiones negativas."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from app.schemas.licitud import EipdResolutionAssessmentV1, EipdResolutionReviewIn
from app.services.eipd_child import EipdChildContextV4


class GlobalPolicyIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_version: StrictInt = Field(ge=1, le=1)
    policy_reference: str = Field(min_length=1)
    policy_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class ChildNegativePolicyV1(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    policy_schema_version: StrictInt = Field(default=1, ge=1, le=1)
    policy_reference: Literal["m3-t1-infancia-pruebas-negativas-v1"] = (
        "m3-t1-infancia-pruebas-negativas-v1"
    )
    sources_status: Literal["pendiente"] = "pendiente"
    acceptance_status: Literal["pendiente"] = "pendiente"
    activation: Literal["deshabilitada"] = "deshabilitada"
    allowed_decisions: tuple[Literal["requiere_cambios"], Literal["no_continuar"]] = (
        "requiere_cambios",
        "no_continuar",
    )
    global_policy_identity: GlobalPolicyIdentity


class ChildResolutionCreateV4(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data_kind: Literal["ficticios"]
    document: EipdResolutionAssessmentV1


class ChildReviewCreateV4(EipdResolutionReviewIn):
    decision: Literal["requiere_cambios", "no_continuar"]
    data_kind: Literal["ficticios"]


class ChildReviewMetadataV3(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    metadata_schema_version: StrictInt = Field(default=3, ge=3, le=3)
    resolution_binding_version: StrictInt = Field(default=4, ge=4, le=4)
    context_schema_version: StrictInt = Field(default=4, ge=4, le=4)
    child_coverage: Literal["contexto_v4"] = "contexto_v4"
    document_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    child_material_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class ChildResolutionOutV4(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    version: StrictInt = Field(ge=1)
    resolution_binding_version: Literal[4] = 4
    stored_coverage: Literal["contexto_v4"] = "contexto_v4"
    data_kind: Literal["ficticios"]
    document: EipdResolutionAssessmentV1
    context_snapshot: EipdChildContextV4
    document_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    child_material_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    created_by: UUID
    created_at: datetime
    authorizes_action: Literal[False] = False
    can_confirm: Literal[False] = False


class ChildReviewOutV4(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    response_schema_version: Literal[4] = 4
    id: UUID
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    resolution_id: UUID
    decision: Literal["requiere_cambios", "no_continuar"]
    data_kind: Literal["ficticios"]
    rationale: str
    review_reference: str
    document_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    child_material_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_snapshot: ChildNegativePolicyV1
    policy_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    review_context_metadata: ChildReviewMetadataV3
    created_by: UUID
    created_at: datetime
    authorizes_action: Literal[False] = False
    can_confirm: Literal[False] = False


class ChildPolicyOutV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy: ChildNegativePolicyV1
    policy_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    authorizes_action: Literal[False] = False
    can_confirm: Literal[False] = False
