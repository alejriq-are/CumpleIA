"""Registered Base y fundamento versions, separate from the mutable draft."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_active_subscription, require_permission
from app.db.models import Profile
from app.db.session import get_db
from app.schemas.base_fundamento_versions import (
    BaseFundamentoReviewAuthority,
    BaseFundamentoReviewRegister,
    BaseFundamentoVersionRegister,
)
from app.services import base_fundamento_reviews as reviews_service
from app.services import base_fundamento_versions as service
from app.services.authorization import Permission

router = APIRouter(
    prefix="/licitud/treatments/{treatment_id}/assessments/{assessment_id}/base-fundamento-versions/v1",
    tags=["licitud"],
    dependencies=[Depends(require_active_subscription)],
)


@router.get("/preview")
async def preview(
    treatment_id: UUID,
    assessment_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
    annex_ids: Annotated[list[UUID] | None, Query(max_length=50)] = None,
):
    return await service.preview(
        db, x_organization_id, treatment_id, assessment_id, annex_ids or []
    )


@router.post("", status_code=201)
async def register(
    treatment_id: UUID,
    assessment_id: UUID,
    payload: BaseFundamentoVersionRegister,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.register_document)),
    db: AsyncSession = Depends(get_db),
):
    return await service.register(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )


@router.get("")
async def history(
    treatment_id: UUID,
    assessment_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    rows = await service.history(db, x_organization_id, treatment_id, assessment_id)
    return [
        dict(
            id=str(r.id),
            version=r.version,
            created_at=r.created_at.isoformat(),
            reason=r.reason,
            bundle_hash=r.bundle_hash,
        )
        for r in rows
    ]


@router.get("/requests/{request_id}")
async def lookup(
    treatment_id: UUID,
    assessment_id: UUID,
    request_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.lookup(
        db, x_organization_id, treatment_id, assessment_id, request_id, profile.id
    )


@router.get("/{version_id}")
async def detail(
    treatment_id: UUID,
    assessment_id: UUID,
    version_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    rows = await service.history(db, x_organization_id, treatment_id, assessment_id)
    row = next((r for r in rows if r.id == version_id), None)
    if row is None:
        raise HTTPException(404, detail="Versión documental no encontrada")
    return service.output(row)


@router.get("/review-authorities/history")
async def review_authorities(
    treatment_id: UUID,
    assessment_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await reviews_service.authorities(
        db, x_organization_id, treatment_id, assessment_id
    )


@router.post("/review-authorities", status_code=201)
async def designate_reviewer(
    treatment_id: UUID,
    assessment_id: UUID,
    payload: BaseFundamentoReviewAuthority,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.manage_members)),
    db: AsyncSession = Depends(get_db),
):
    return await reviews_service.designate(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )


@router.get("/{version_id}/reviews")
async def reviews(
    treatment_id: UUID,
    assessment_id: UUID,
    version_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await reviews_service.history(
        db, x_organization_id, treatment_id, assessment_id, version_id
    )


@router.get("/{version_id}/review-state")
async def review_state(
    treatment_id: UUID,
    assessment_id: UUID,
    version_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await reviews_service.state(
        db, x_organization_id, treatment_id, assessment_id, version_id, profile.id
    )


@router.post("/{version_id}/reviews", status_code=201)
async def record_review(
    treatment_id: UUID,
    assessment_id: UUID,
    version_id: UUID,
    payload: BaseFundamentoReviewRegister,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await reviews_service.record(
        db,
        x_organization_id,
        treatment_id,
        assessment_id,
        version_id,
        profile.id,
        payload,
    )


@router.get("/{version_id}/review-requests/{request_id}")
async def review_request(
    treatment_id: UUID,
    assessment_id: UUID,
    version_id: UUID,
    request_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await reviews_service.lookup(
        db,
        x_organization_id,
        treatment_id,
        assessment_id,
        version_id,
        profile.id,
        request_id,
    )
