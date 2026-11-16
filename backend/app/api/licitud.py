"""API M3 inicial: borradores y confirmación de consentimiento ordinario."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_active_subscription, require_permission
from app.db.models import Profile
from app.db.session import get_db
from app.schemas.child_adolescent_api import (
    LegalAssessmentChildDraftCreateV1 as LegalAssessmentDraftCreate,
)
from app.schemas.child_adolescent_api import (
    LegalAssessmentChildDraftUpdateV1 as LegalAssessmentDraftUpdate,
)
from app.schemas.child_adolescent_api import (
    LegalAssessmentChildOutV1 as LegalAssessmentOut,
)
from app.schemas.child_adolescent_api import (
    LegalAssessmentChildReadinessOutV1 as LegalAssessmentReadinessOut,
)
from app.schemas.eipd_child_persistence import (
    ChildPolicyOutV1,
    ChildResolutionCreateV4,
    ChildResolutionOutV4,
    ChildReviewCreateV4,
    ChildReviewOutV4,
)
from app.schemas.licitud import (
    EipdNegativeResolutionReviewInV3,
    EipdResolutionReviewIn,
    EipdResolutionReviewOut,
    EipdResolutionReviewOutV2,
    EipdResolutionReviewOutV3,
)
from app.services import eipd_child_persistence as child_service
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


@router.post(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-resolution/reviews/v3",
    response_model=EipdResolutionReviewOutV3,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_revision_negativa_eipd_v3(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    payload: EipdNegativeResolutionReviewInV3,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    event = await service.record_eipd_negative_review_v3(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )
    return service.serialize_eipd_resolution_review_v3(event)


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


@router.get(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-resolution/reviews/{review_id}/v3",
    response_model=EipdResolutionReviewOutV3,
)
async def leer_revision_eipd_salida_v3(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    review_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    _profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_eipd_resolution_review_v3(
        db, x_organization_id, treatment_id, assessment_id, review_id
    )


@router.post(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-child/v4/resolutions",
    response_model=ChildResolutionOutV4,
    status_code=201,
)
async def crear_resolucion_infancia(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    payload: ChildResolutionCreateV4,
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    return await child_service.create_resolution(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )


@router.get(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-child/v4/resolutions",
    response_model=list[ChildResolutionOutV4],
)
async def listar_resoluciones_infancia(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await child_service.list_resolutions(
        db, x_organization_id, treatment_id, assessment_id
    )


@router.get(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-child/v4/resolutions/{resolution_id}",
    response_model=ChildResolutionOutV4,
)
async def obtener_resolucion_infancia(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    resolution_id: uuid.UUID,
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return child_service.resolution_out(
        await child_service.get_resolution(
            db, x_organization_id, treatment_id, assessment_id, resolution_id
        )
    )


@router.post(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-child/v4/resolutions/{resolution_id}/reviews",
    response_model=ChildReviewOutV4,
    status_code=201,
)
async def crear_revision_infancia(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    resolution_id: uuid.UUID,
    payload: ChildReviewCreateV4,
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    return await child_service.create_review(
        db,
        x_organization_id,
        treatment_id,
        assessment_id,
        resolution_id,
        profile.id,
        payload,
    )


@router.get(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-child/v4/resolutions/{resolution_id}/reviews",
    response_model=list[ChildReviewOutV4],
)
async def listar_revisiones_infancia(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    resolution_id: uuid.UUID,
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await child_service.list_reviews(
        db, x_organization_id, treatment_id, assessment_id, resolution_id
    )


@router.get(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-child/v4/resolutions/{resolution_id}/reviews/{review_id}",
    response_model=ChildReviewOutV4,
)
async def obtener_revision_infancia(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    resolution_id: uuid.UUID,
    review_id: uuid.UUID,
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await child_service.get_review(
        db, x_organization_id, treatment_id, assessment_id, resolution_id, review_id
    )


@router.get(
    "/treatments/{treatment_id}/assessments/{assessment_id}/eipd-child/v4/policy",
    response_model=ChildPolicyOutV1,
)
async def politica_infancia(
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    await service.get_legal_assessment_v1(
        db, x_organization_id, treatment_id, assessment_id
    )
    return await child_service.selected_policy(db)
