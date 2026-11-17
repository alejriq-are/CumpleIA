"""Fictitious assessment support; raw annex bytes never rendered inline."""

import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_active_subscription, require_permission
from app.db.models import Profile
from app.db.session import get_db
from app.schemas.assessment_support import AnnexSave, RiskSave
from app.schemas.navigation_applicability import ApplicabilitySave
from app.services import assessment_support as service
from app.services import navigation_applicability as applicability_service
from app.services.authorization import Permission

router = APIRouter(
    prefix="/licitud/treatments/{treatment_id}/assessments/{assessment_id}",
    tags=["licitud"],
    dependencies=[Depends(require_active_subscription)],
)


@router.get("/support")
async def support(
    treatment_id: UUID,
    assessment_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.snapshot(db, x_organization_id, treatment_id, assessment_id)


@router.post("/risk-evaluations", status_code=201)
async def save_risks(
    treatment_id: UUID,
    assessment_id: UUID,
    payload: RiskSave,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    return await service.save_risks(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )


@router.post("/annexes", status_code=201)
async def save_annex(
    treatment_id: UUID,
    assessment_id: UUID,
    request: Request,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > 3000000:
            raise HTTPException(413, detail="Archivo demasiado grande")
    try:
        payload = AnnexSave.model_validate(json.loads(data))
    except (ValidationError, ValueError, UnicodeError):
        raise HTTPException(
            422, detail="Datos de anexo invalidos; solo prueba ficticia PDF/TXT"
        ) from None
    return await service.save_annex(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )


@router.get("/annexes/{annex_id}/content")
async def download(
    treatment_id: UUID,
    assessment_id: UUID,
    annex_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    row = await service.download_annex(
        db, x_organization_id, treatment_id, assessment_id, annex_id
    )
    return Response(
        content=row.content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="anexo-{row.id}.bin"',
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-store",
            "Content-Security-Policy": "sandbox",
        },
    )


@router.get("/applicability")
async def applicability(
    treatment_id: UUID,
    assessment_id: UUID,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
):
    return await applicability_service.snapshot(
        db, x_organization_id, treatment_id, assessment_id
    )


@router.post("/applicability", status_code=201)
async def save_applicability(
    treatment_id: UUID,
    assessment_id: UUID,
    payload: ApplicabilitySave,
    x_organization_id: Annotated[UUID, Header()],
    profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
):
    return await applicability_service.save(
        db, x_organization_id, treatment_id, assessment_id, profile.id, payload
    )
