"""Control global EIPD: publicaciones y selecciones solo deshabilitadas."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.eipd_admin import get_eipd_admin_db
from app.services.eipd_policy import EipdGatePolicyV1, Text
from app.services.eipd_policy_audit import (
    EipdPolicyPublicationV1,
    EipdPolicySelectionPlanV1,
    EipdPolicySelectionRequestV1,
)
from app.services.eipd_policy_store import (
    publish_eipd_policy_v1,
    select_eipd_policy_v1,
)

router = APIRouter(prefix="/admin/eipd", tags=["Administracion EIPD"])
AdminDb = Annotated[AsyncSession, Depends(get_eipd_admin_db)]


class PublicationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy: EipdGatePolicyV1
    rationale: Text
    evidence_reference: Text


class SelectionRequest(EipdPolicySelectionRequestV1):
    rationale: Text
    evidence_reference: Text


@router.post("/publications", status_code=201, response_model=EipdPolicyPublicationV1)
async def publish(request: PublicationRequest, db: AdminDb):
    try:
        return await publish_eipd_policy_v1(
            db,
            request.policy,
            rationale=request.rationale,
            evidence_reference=request.evidence_reference,
        )
    except ValueError:
        raise HTTPException(409, "Publicacion EIPD no admitida") from None
    except IntegrityError as exc:
        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise HTTPException(409, "Referencia EIPD ya registrada") from None
        raise


@router.post("/selections", status_code=201, response_model=EipdPolicySelectionPlanV1)
async def select_policy(request: SelectionRequest, db: AdminDb):
    try:
        return await select_eipd_policy_v1(
            db,
            EipdPolicySelectionRequestV1(
                expected_revision=request.expected_revision,
                publication_id=request.publication_id,
            ),
            rationale=request.rationale,
            evidence_reference=request.evidence_reference,
        )
    except ValueError:
        raise HTTPException(
            409, "Seleccion EIPD no admitida o revision obsoleta"
        ) from None
