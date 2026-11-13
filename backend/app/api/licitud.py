"""API M3 inicial: borradores y confirmación de consentimiento ordinario."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_active_subscription, require_permission
from app.db.models import Profile
from app.db.session import get_db
from app.schemas.licitud import (
    EipdResolutionReviewIn,
    EipdResolutionReviewOut,
    EipdResolutionReviewOutV2,
    LegalAssessmentDraftCreate,
    LegalAssessmentDraftUpdate,
    LegalAssessmentOut,
    LegalAssessmentReadinessOut,
)
from app.services import licitud as service
from app.services.authorization import Permission

router = APIRouter(
    prefix="/licitud",
    tags=["licitud"],
    dependencies=[Depends(require_active_subscription)],
)


@router.post(
    "/treatments/{treatment_id}/assessments",
    response_model=LegalAssessmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def crear_borrador(
    treatment_id: uuid.UUID,
    payload: LegalAssessmentDraftCreate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_legal_assessment_draft_v1(
        db, x_organization_id, treatment_id, profile.id, payload
    )


@router.get(
    "/treatments/{treatment_id}/assessments/{assessment_id}",
    response_model=LegalAssessmentOut,
)
async def obtener_evaluacion(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_legal_assessment_v1(
        db, x_organization_id, treatment_id, assessment_id
    )


@router.patch(
    "/treatments/{treatment_id}/assessments/{assessment_id}",
    response_model=LegalAssessmentOut,
)
async def actualizar_borrador(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    payload: LegalAssessmentDraftUpdate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_legal_assessment_draft_v1(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )


@router.post(
    "/treatments/{treatment_id}/assessments/{assessment_id}/confirm",
    response_model=LegalAssessmentOut,
)
async def confirmar_evaluacion(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.confirm_legal_assessment_v1(
        db, x_organization_id, treatment_id, assessment_id, profile.id
    )


@router.get(
    "/treatments/{treatment_id}/assessments/{assessment_id}/readiness",
    response_model=LegalAssessmentReadinessOut,
)
async def obtener_preparacion(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_legal_assessment_readiness_v1(
        db, x_organization_id, treatment_id, assessment_id
    )


@router.post(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-resolution/reviews",
    response_model=EipdResolutionReviewOut,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_revision_eipd(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    payload: EipdResolutionReviewIn,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.record_eipd_resolution_review_v1(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )


@router.post(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-resolution/reviews/v2",
    response_model=EipdResolutionReviewOutV2,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_revision_eipd_salida_v2(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    payload: EipdResolutionReviewIn,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    event = await service.record_eipd_resolution_review_v1(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )
    return service.serialize_eipd_resolution_review_v2(event)


@router.get(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-resolution/reviews/{review_id}/v2",
    response_model=EipdResolutionReviewOutV2,
)
async def leer_revision_eipd_salida_v2(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    review_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    _profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_eipd_resolution_review_v2(
        db, x_organization_id, treatment_id, assessment_id, review_id
    )
