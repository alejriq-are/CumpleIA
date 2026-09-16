"""API del Módulo 2 — Registro de Actividades de Tratamiento (RAT).

Todo el módulo exige suscripción activa/grace mediante
`require_active_subscription`. Los permisos funcionales siguen el modelo
general del producto:

- lectura: view_content
- escritura: edit_content

El organization_id siempre proviene de X-Organization-Id y se vuelve a
aplicar explícitamente en el service layer, además de RLS.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_active_subscription, require_permission
from app.db.models import Profile
from app.db.session import get_db
from app.schemas.rat import (
    InternationalTransferCreate,
    InternationalTransferOut,
    InternationalTransferUpdate,
    SystemCreate,
    SystemOut,
    SystemUpdate,
    TreatmentCreate,
    TreatmentDataCategoriesReplace,
    TreatmentDataCategoryOut,
    TreatmentDataSourceOut,
    TreatmentDataSourcesReplace,
    TreatmentDataSubjectOut,
    TreatmentDataSubjectsReplace,
    TreatmentDetailOut,
    TreatmentPurposeOut,
    TreatmentPurposesReplace,
    TreatmentSummaryOut,
    TreatmentSystemsReplace,
    TreatmentUpdate,
    TreatmentVendorOut,
    TreatmentVendorsReplace,
    VendorCreate,
    VendorOut,
    VendorUpdate,
)
from app.services import rat as rat_service
from app.services.authorization import Permission

router = APIRouter(
    prefix="/rat",
    tags=["rat"],
    dependencies=[Depends(require_active_subscription)],
)


# ── Helpers de salida ─────────────────────────────────────────────────────────


async def _construir_detalle(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> TreatmentDetailOut:
    treatment = await rat_service.obtener_tratamiento(
        db,
        organization_id,
        treatment_id,
    )

    purposes = await rat_service.listar_finalidades(db, organization_id, treatment_id)
    categories = await rat_service.listar_categorias_datos(
        db, organization_id, treatment_id
    )
    subjects = await rat_service.listar_titulares_datos(
        db, organization_id, treatment_id
    )
    sources = await rat_service.listar_fuentes_datos(db, organization_id, treatment_id)
    systems = await rat_service.listar_sistemas_tratamiento(
        db, organization_id, treatment_id
    )
    vendors = await rat_service.listar_vendors_tratamiento(
        db, organization_id, treatment_id
    )
    transfers = await rat_service.listar_transferencias(
        db, organization_id, treatment_id
    )

    return TreatmentDetailOut(
        id=treatment.id,
        name=treatment.name,
        description=treatment.description,
        organization_role=treatment.organization_role,
        business_area=treatment.business_area,
        status=treatment.status,
        systems_declaration=treatment.systems_declaration,
        vendors_declaration=treatment.vendors_declaration,
        international_transfers_declaration=(
            treatment.international_transfers_declaration
        ),
        start_date=treatment.start_date,
        last_reviewed_at=treatment.last_reviewed_at,
        next_review_at=treatment.next_review_at,
        created_at=treatment.created_at,
        updated_at=treatment.updated_at,
        data_flow_description=treatment.data_flow_description,
        retention_rule=treatment.retention_rule,
        deletion_method=treatment.deletion_method,
        has_automated_decisions=treatment.has_automated_decisions,
        automated_decision_description=treatment.automated_decision_description,
        purposes=[TreatmentPurposeOut.model_validate(item) for item in purposes],
        data_categories=[
            TreatmentDataCategoryOut.model_validate(item) for item in categories
        ],
        data_subjects=[
            TreatmentDataSubjectOut.model_validate(item) for item in subjects
        ],
        data_sources=[TreatmentDataSourceOut.model_validate(item) for item in sources],
        systems=[SystemOut.model_validate(item) for item in systems],
        vendors=[TreatmentVendorOut.model_validate(item) for item in vendors],
        international_transfers=[
            InternationalTransferOut.model_validate(item) for item in transfers
        ],
    )


# ── Treatments ────────────────────────────────────────────────────────────────


@router.get("/treatments", response_model=list[TreatmentSummaryOut])
async def listar_tratamientos(
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
) -> list[TreatmentSummaryOut]:
    del current_profile

    rows = await rat_service.listar_tratamientos(db, x_organization_id)
    return [TreatmentSummaryOut.model_validate(row) for row in rows]


@router.post(
    "/treatments",
    response_model=TreatmentDetailOut,
    status_code=status.HTTP_201_CREATED,
)
async def crear_tratamiento(
    payload: TreatmentCreate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> TreatmentDetailOut:
    treatment = await rat_service.crear_tratamiento(
        db,
        x_organization_id,
        current_profile.id,
        payload,
    )

    return await _construir_detalle(
        db,
        x_organization_id,
        treatment.id,
    )


@router.get(
    "/treatments/{treatment_id}",
    response_model=TreatmentDetailOut,
)
async def obtener_tratamiento(
    treatment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
) -> TreatmentDetailOut:
    del current_profile

    return await _construir_detalle(
        db,
        x_organization_id,
        treatment_id,
    )


@router.patch(
    "/treatments/{treatment_id}",
    response_model=TreatmentDetailOut,
)
async def actualizar_tratamiento(
    treatment_id: uuid.UUID,
    payload: TreatmentUpdate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> TreatmentDetailOut:
    await rat_service.actualizar_tratamiento(
        db,
        x_organization_id,
        treatment_id,
        current_profile.id,
        payload,
    )

    return await _construir_detalle(
        db,
        x_organization_id,
        treatment_id,
    )


@router.delete(
    "/treatments/{treatment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def eliminar_tratamiento(
    treatment_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> Response:
    del current_profile

    await rat_service.eliminar_tratamiento(
        db,
        x_organization_id,
        treatment_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Componentes normalizados ─────────────────────────────────────────────────


@router.put(
    "/treatments/{treatment_id}/purposes",
    response_model=list[TreatmentPurposeOut],
)
async def reemplazar_finalidades(
    treatment_id: uuid.UUID,
    payload: TreatmentPurposesReplace,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> list[TreatmentPurposeOut]:
    rows = await rat_service.reemplazar_finalidades(
        db,
        x_organization_id,
        treatment_id,
        current_profile.id,
        payload.items,
    )
    return [TreatmentPurposeOut.model_validate(row) for row in rows]


@router.put(
    "/treatments/{treatment_id}/data-categories",
    response_model=list[TreatmentDataCategoryOut],
)
async def reemplazar_categorias_datos(
    treatment_id: uuid.UUID,
    payload: TreatmentDataCategoriesReplace,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> list[TreatmentDataCategoryOut]:
    rows = await rat_service.reemplazar_categorias_datos(
        db,
        x_organization_id,
        treatment_id,
        current_profile.id,
        payload.items,
    )
    return [TreatmentDataCategoryOut.model_validate(row) for row in rows]


@router.put(
    "/treatments/{treatment_id}/data-subjects",
    response_model=list[TreatmentDataSubjectOut],
)
async def reemplazar_titulares_datos(
    treatment_id: uuid.UUID,
    payload: TreatmentDataSubjectsReplace,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> list[TreatmentDataSubjectOut]:
    rows = await rat_service.reemplazar_titulares_datos(
        db,
        x_organization_id,
        treatment_id,
        current_profile.id,
        payload.items,
    )
    return [TreatmentDataSubjectOut.model_validate(row) for row in rows]


@router.put(
    "/treatments/{treatment_id}/data-sources",
    response_model=list[TreatmentDataSourceOut],
)
async def reemplazar_fuentes_datos(
    treatment_id: uuid.UUID,
    payload: TreatmentDataSourcesReplace,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> list[TreatmentDataSourceOut]:
    rows = await rat_service.reemplazar_fuentes_datos(
        db,
        x_organization_id,
        treatment_id,
        current_profile.id,
        payload.items,
    )
    return [TreatmentDataSourceOut.model_validate(row) for row in rows]


@router.put(
    "/treatments/{treatment_id}/systems",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reemplazar_sistemas_tratamiento(
    treatment_id: uuid.UUID,
    payload: TreatmentSystemsReplace,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> Response:
    await rat_service.reemplazar_sistemas_tratamiento(
        db,
        x_organization_id,
        treatment_id,
        current_profile.id,
        payload.system_ids,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/treatments/{treatment_id}/vendors",
    response_model=list[TreatmentVendorOut],
)
async def reemplazar_vendors_tratamiento(
    treatment_id: uuid.UUID,
    payload: TreatmentVendorsReplace,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> list[TreatmentVendorOut]:
    rows = await rat_service.reemplazar_vendors_tratamiento(
        db,
        x_organization_id,
        treatment_id,
        current_profile.id,
        payload.items,
    )
    return [TreatmentVendorOut.model_validate(row) for row in rows]


# ── Systems ──────────────────────────────────────────────────────────────────


@router.get("/systems", response_model=list[SystemOut])
async def listar_sistemas(
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
) -> list[SystemOut]:
    del current_profile

    rows = await rat_service.listar_sistemas(db, x_organization_id)
    return [SystemOut.model_validate(row) for row in rows]


@router.post(
    "/systems",
    response_model=SystemOut,
    status_code=status.HTTP_201_CREATED,
)
async def crear_sistema(
    payload: SystemCreate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> SystemOut:
    row = await rat_service.crear_sistema(
        db,
        x_organization_id,
        current_profile.id,
        payload,
    )
    return SystemOut.model_validate(row)


@router.patch("/systems/{system_id}", response_model=SystemOut)
async def actualizar_sistema(
    system_id: uuid.UUID,
    payload: SystemUpdate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> SystemOut:
    row = await rat_service.actualizar_sistema(
        db,
        x_organization_id,
        system_id,
        current_profile.id,
        payload,
    )
    return SystemOut.model_validate(row)


@router.delete(
    "/systems/{system_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def eliminar_sistema(
    system_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> Response:
    del current_profile

    await rat_service.eliminar_sistema(
        db,
        x_organization_id,
        system_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Vendors ──────────────────────────────────────────────────────────────────


@router.get("/vendors", response_model=list[VendorOut])
async def listar_vendors(
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.view_content)),
    db: AsyncSession = Depends(get_db),
) -> list[VendorOut]:
    del current_profile

    rows = await rat_service.listar_vendors(db, x_organization_id)
    return [VendorOut.model_validate(row) for row in rows]


@router.post(
    "/vendors",
    response_model=VendorOut,
    status_code=status.HTTP_201_CREATED,
)
async def crear_vendor(
    payload: VendorCreate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> VendorOut:
    row = await rat_service.crear_vendor(
        db,
        x_organization_id,
        current_profile.id,
        payload,
    )
    return VendorOut.model_validate(row)


@router.patch("/vendors/{vendor_id}", response_model=VendorOut)
async def actualizar_vendor(
    vendor_id: uuid.UUID,
    payload: VendorUpdate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> VendorOut:
    row = await rat_service.actualizar_vendor(
        db,
        x_organization_id,
        vendor_id,
        current_profile.id,
        payload,
    )
    return VendorOut.model_validate(row)


@router.delete(
    "/vendors/{vendor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def eliminar_vendor(
    vendor_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> Response:
    del current_profile

    await rat_service.eliminar_vendor(
        db,
        x_organization_id,
        vendor_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Transferencias internacionales ────────────────────────────────────────────


@router.post(
    "/treatments/{treatment_id}/international-transfers",
    response_model=InternationalTransferOut,
    status_code=status.HTTP_201_CREATED,
)
async def crear_transferencia(
    treatment_id: uuid.UUID,
    payload: InternationalTransferCreate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> InternationalTransferOut:
    row = await rat_service.crear_transferencia(
        db,
        x_organization_id,
        treatment_id,
        current_profile.id,
        payload,
    )
    return InternationalTransferOut.model_validate(row)


@router.patch(
    "/international-transfers/{transfer_id}",
    response_model=InternationalTransferOut,
)
async def actualizar_transferencia(
    transfer_id: uuid.UUID,
    payload: InternationalTransferUpdate,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> InternationalTransferOut:
    row = await rat_service.actualizar_transferencia(
        db,
        x_organization_id,
        transfer_id,
        current_profile.id,
        payload,
    )
    return InternationalTransferOut.model_validate(row)


@router.delete(
    "/international-transfers/{transfer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def eliminar_transferencia(
    transfer_id: uuid.UUID,
    x_organization_id: Annotated[uuid.UUID, Header()],
    current_profile: Profile = Depends(require_permission(Permission.edit_content)),
    db: AsyncSession = Depends(get_db),
) -> Response:
    del current_profile

    await rat_service.eliminar_transferencia(
        db,
        x_organization_id,
        transfer_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
