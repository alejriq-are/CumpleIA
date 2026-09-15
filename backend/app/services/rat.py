"""Servicio del Módulo 2 — Registro de Actividades de Tratamiento (RAT).

Toda operación queda acotada explícitamente por organization_id, además de
las políticas RLS y las FK tenant-aware introducidas en M2-T1.

El servicio no hace commit: app/db/session.py confirma o revierte la
transacción al finalizar cada request.
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    InternationalTransfer,
    System,
    Treatment,
    TreatmentDataCategory,
    TreatmentDataSource,
    TreatmentDataSubject,
    TreatmentPurpose,
    TreatmentSystem,
    TreatmentVendor,
    Vendor,
)
from app.schemas.rat import (
    InternationalTransferCreate,
    InternationalTransferUpdate,
    SystemCreate,
    SystemUpdate,
    TreatmentCreate,
    TreatmentDataCategoryIn,
    TreatmentDataSourceIn,
    TreatmentDataSubjectIn,
    TreatmentPurposeIn,
    TreatmentUpdate,
    TreatmentVendorIn,
    VendorCreate,
    VendorUpdate,
)


def _not_found(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


# ── Treatments ────────────────────────────────────────────────────────────────


async def listar_tratamientos(
    db: AsyncSession,
    organization_id: uuid.UUID,
) -> list[Treatment]:
    result = await db.execute(
        select(Treatment)
        .where(Treatment.organization_id == organization_id)
        .order_by(Treatment.name, Treatment.id)
    )
    return list(result.scalars().all())


async def obtener_tratamiento(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> Treatment:
    result = await db.execute(
        select(Treatment).where(
            Treatment.id == treatment_id,
            Treatment.organization_id == organization_id,
        )
    )
    treatment = result.scalar_one_or_none()

    if treatment is None:
        raise _not_found("Actividad de tratamiento no encontrada")

    return treatment


async def crear_tratamiento(
    db: AsyncSession,
    organization_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: TreatmentCreate,
) -> Treatment:
    treatment = Treatment(
        organization_id=organization_id,
        created_by=profile_id,
        updated_by=profile_id,
        **payload.model_dump(),
    )
    db.add(treatment)
    await db.flush()
    return treatment


async def actualizar_tratamiento(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: TreatmentUpdate,
) -> Treatment:
    treatment = await obtener_tratamiento(db, organization_id, treatment_id)
    changes = payload.model_dump(exclude_unset=True)

    if "name" in changes and changes["name"] is None:
        raise _bad_request("name no puede ser null")

    for field, value in changes.items():
        setattr(treatment, field, value)

    treatment.updated_by = profile_id
    await db.flush()
    return treatment


async def eliminar_tratamiento(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> None:
    treatment = await obtener_tratamiento(db, organization_id, treatment_id)
    await db.delete(treatment)
    await db.flush()


# ── Finalidades ───────────────────────────────────────────────────────────────


async def listar_finalidades(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> list[TreatmentPurpose]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    result = await db.execute(
        select(TreatmentPurpose)
        .where(
            TreatmentPurpose.organization_id == organization_id,
            TreatmentPurpose.treatment_id == treatment_id,
        )
        .order_by(TreatmentPurpose.sort_order, TreatmentPurpose.id)
    )
    return list(result.scalars().all())


async def reemplazar_finalidades(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    profile_id: uuid.UUID,
    items: list[TreatmentPurposeIn],
) -> list[TreatmentPurpose]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    purposes = [item.purpose for item in items]
    if len(purposes) != len(set(purposes)):
        raise _bad_request("No se permiten finalidades duplicadas")

    if sum(1 for item in items if item.is_primary) > 1:
        raise _bad_request("Solo puede existir una finalidad principal")

    await db.execute(
        delete(TreatmentPurpose).where(
            TreatmentPurpose.organization_id == organization_id,
            TreatmentPurpose.treatment_id == treatment_id,
        )
    )

    rows = [
        TreatmentPurpose(
            organization_id=organization_id,
            treatment_id=treatment_id,
            created_by=profile_id,
            updated_by=profile_id,
            **item.model_dump(),
        )
        for item in items
    ]
    db.add_all(rows)
    await db.flush()
    return rows


# ── Categorías de datos ──────────────────────────────────────────────────────


async def listar_categorias_datos(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> list[TreatmentDataCategory]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    result = await db.execute(
        select(TreatmentDataCategory)
        .where(
            TreatmentDataCategory.organization_id == organization_id,
            TreatmentDataCategory.treatment_id == treatment_id,
        )
        .order_by(TreatmentDataCategory.category_name, TreatmentDataCategory.id)
    )
    return list(result.scalars().all())


async def reemplazar_categorias_datos(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    profile_id: uuid.UUID,
    items: list[TreatmentDataCategoryIn],
) -> list[TreatmentDataCategory]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    codes = [item.category_code for item in items]
    if len(codes) != len(set(codes)):
        raise _bad_request("No se permiten category_code duplicados")

    await db.execute(
        delete(TreatmentDataCategory).where(
            TreatmentDataCategory.organization_id == organization_id,
            TreatmentDataCategory.treatment_id == treatment_id,
        )
    )

    rows = [
        TreatmentDataCategory(
            organization_id=organization_id,
            treatment_id=treatment_id,
            created_by=profile_id,
            updated_by=profile_id,
            **item.model_dump(),
        )
        for item in items
    ]
    db.add_all(rows)
    await db.flush()
    return rows


# ── Titulares de datos ───────────────────────────────────────────────────────


async def listar_titulares_datos(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> list[TreatmentDataSubject]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    result = await db.execute(
        select(TreatmentDataSubject)
        .where(
            TreatmentDataSubject.organization_id == organization_id,
            TreatmentDataSubject.treatment_id == treatment_id,
        )
        .order_by(TreatmentDataSubject.category_name, TreatmentDataSubject.id)
    )
    return list(result.scalars().all())


async def reemplazar_titulares_datos(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    profile_id: uuid.UUID,
    items: list[TreatmentDataSubjectIn],
) -> list[TreatmentDataSubject]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    codes = [item.category_code for item in items]
    if len(codes) != len(set(codes)):
        raise _bad_request("No se permiten category_code duplicados")

    await db.execute(
        delete(TreatmentDataSubject).where(
            TreatmentDataSubject.organization_id == organization_id,
            TreatmentDataSubject.treatment_id == treatment_id,
        )
    )

    rows = [
        TreatmentDataSubject(
            organization_id=organization_id,
            treatment_id=treatment_id,
            created_by=profile_id,
            updated_by=profile_id,
            **item.model_dump(),
        )
        for item in items
    ]
    db.add_all(rows)
    await db.flush()
    return rows


# ── Fuentes de datos ─────────────────────────────────────────────────────────


async def listar_fuentes_datos(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> list[TreatmentDataSource]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    result = await db.execute(
        select(TreatmentDataSource)
        .where(
            TreatmentDataSource.organization_id == organization_id,
            TreatmentDataSource.treatment_id == treatment_id,
        )
        .order_by(TreatmentDataSource.created_at, TreatmentDataSource.id)
    )
    return list(result.scalars().all())


async def reemplazar_fuentes_datos(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    profile_id: uuid.UUID,
    items: list[TreatmentDataSourceIn],
) -> list[TreatmentDataSource]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    await db.execute(
        delete(TreatmentDataSource).where(
            TreatmentDataSource.organization_id == organization_id,
            TreatmentDataSource.treatment_id == treatment_id,
        )
    )

    rows = [
        TreatmentDataSource(
            organization_id=organization_id,
            treatment_id=treatment_id,
            created_by=profile_id,
            updated_by=profile_id,
            **item.model_dump(),
        )
        for item in items
    ]
    db.add_all(rows)
    await db.flush()
    return rows


# ── Systems ──────────────────────────────────────────────────────────────────


async def listar_sistemas(
    db: AsyncSession,
    organization_id: uuid.UUID,
) -> list[System]:
    result = await db.execute(
        select(System)
        .where(System.organization_id == organization_id)
        .order_by(System.name, System.id)
    )
    return list(result.scalars().all())


async def obtener_sistema(
    db: AsyncSession,
    organization_id: uuid.UUID,
    system_id: uuid.UUID,
) -> System:
    result = await db.execute(
        select(System).where(
            System.id == system_id,
            System.organization_id == organization_id,
        )
    )
    system = result.scalar_one_or_none()

    if system is None:
        raise _not_found("Sistema no encontrado")

    return system


async def crear_sistema(
    db: AsyncSession,
    organization_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: SystemCreate,
) -> System:
    system = System(
        organization_id=organization_id,
        created_by=profile_id,
        updated_by=profile_id,
        **payload.model_dump(),
    )
    db.add(system)
    await db.flush()
    return system


async def actualizar_sistema(
    db: AsyncSession,
    organization_id: uuid.UUID,
    system_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: SystemUpdate,
) -> System:
    system = await obtener_sistema(db, organization_id, system_id)
    changes = payload.model_dump(exclude_unset=True)

    if "name" in changes and changes["name"] is None:
        raise _bad_request("name no puede ser null")

    for field, value in changes.items():
        setattr(system, field, value)

    system.updated_by = profile_id
    await db.flush()
    return system


async def eliminar_sistema(
    db: AsyncSession,
    organization_id: uuid.UUID,
    system_id: uuid.UUID,
) -> None:
    system = await obtener_sistema(db, organization_id, system_id)
    await db.delete(system)
    await db.flush()


async def reemplazar_sistemas_tratamiento(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    profile_id: uuid.UUID,
    system_ids: list[uuid.UUID],
) -> list[TreatmentSystem]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    if len(system_ids) != len(set(system_ids)):
        raise _bad_request("No se permiten system_id duplicados")

    if system_ids:
        encontrados = set(
            (
                await db.execute(
                    select(System.id).where(
                        System.organization_id == organization_id,
                        System.id.in_(system_ids),
                    )
                )
            )
            .scalars()
            .all()
        )

        faltantes = set(system_ids) - encontrados
        if faltantes:
            raise _bad_request("Uno o más sistemas no pertenecen a la organización")

    await db.execute(
        delete(TreatmentSystem).where(
            TreatmentSystem.organization_id == organization_id,
            TreatmentSystem.treatment_id == treatment_id,
        )
    )

    rows = [
        TreatmentSystem(
            organization_id=organization_id,
            treatment_id=treatment_id,
            system_id=system_id,
            created_by=profile_id,
            updated_by=profile_id,
        )
        for system_id in system_ids
    ]
    db.add_all(rows)
    await db.flush()
    return rows


# ── Vendors ──────────────────────────────────────────────────────────────────


async def listar_vendors(
    db: AsyncSession,
    organization_id: uuid.UUID,
) -> list[Vendor]:
    result = await db.execute(
        select(Vendor)
        .where(Vendor.organization_id == organization_id)
        .order_by(Vendor.name, Vendor.id)
    )
    return list(result.scalars().all())


async def obtener_vendor(
    db: AsyncSession,
    organization_id: uuid.UUID,
    vendor_id: uuid.UUID,
) -> Vendor:
    result = await db.execute(
        select(Vendor).where(
            Vendor.id == vendor_id,
            Vendor.organization_id == organization_id,
        )
    )
    vendor = result.scalar_one_or_none()

    if vendor is None:
        raise _not_found("Proveedor no encontrado")

    return vendor


async def crear_vendor(
    db: AsyncSession,
    organization_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: VendorCreate,
) -> Vendor:
    vendor = Vendor(
        organization_id=organization_id,
        created_by=profile_id,
        updated_by=profile_id,
        **payload.model_dump(),
    )
    db.add(vendor)
    await db.flush()
    return vendor


async def actualizar_vendor(
    db: AsyncSession,
    organization_id: uuid.UUID,
    vendor_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: VendorUpdate,
) -> Vendor:
    vendor = await obtener_vendor(db, organization_id, vendor_id)
    changes = payload.model_dump(exclude_unset=True)

    if "name" in changes and changes["name"] is None:
        raise _bad_request("name no puede ser null")

    for field, value in changes.items():
        setattr(vendor, field, value)

    vendor.updated_by = profile_id
    await db.flush()
    return vendor


async def eliminar_vendor(
    db: AsyncSession,
    organization_id: uuid.UUID,
    vendor_id: uuid.UUID,
) -> None:
    vendor = await obtener_vendor(db, organization_id, vendor_id)
    await db.delete(vendor)
    await db.flush()


async def reemplazar_vendors_tratamiento(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    profile_id: uuid.UUID,
    items: list[TreatmentVendorIn],
) -> list[TreatmentVendor]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    keys = [(item.vendor_id, item.relationship_type) for item in items]
    if len(keys) != len(set(keys)):
        raise _bad_request("No se permiten relaciones vendor/tipo duplicadas")

    vendor_ids = {item.vendor_id for item in items}

    if vendor_ids:
        encontrados = set(
            (
                await db.execute(
                    select(Vendor.id).where(
                        Vendor.organization_id == organization_id,
                        Vendor.id.in_(vendor_ids),
                    )
                )
            )
            .scalars()
            .all()
        )

        if vendor_ids - encontrados:
            raise _bad_request("Uno o más proveedores no pertenecen a la organización")

    await db.execute(
        delete(TreatmentVendor).where(
            TreatmentVendor.organization_id == organization_id,
            TreatmentVendor.treatment_id == treatment_id,
        )
    )

    rows = [
        TreatmentVendor(
            organization_id=organization_id,
            treatment_id=treatment_id,
            created_by=profile_id,
            updated_by=profile_id,
            **item.model_dump(),
        )
        for item in items
    ]
    db.add_all(rows)
    await db.flush()
    return rows


# ── Transferencias internacionales ────────────────────────────────────────────


async def listar_transferencias(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> list[InternationalTransfer]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    result = await db.execute(
        select(InternationalTransfer)
        .where(
            InternationalTransfer.organization_id == organization_id,
            InternationalTransfer.treatment_id == treatment_id,
        )
        .order_by(
            InternationalTransfer.destination_country,
            InternationalTransfer.id,
        )
    )
    return list(result.scalars().all())


async def obtener_transferencia(
    db: AsyncSession,
    organization_id: uuid.UUID,
    transfer_id: uuid.UUID,
) -> InternationalTransfer:
    result = await db.execute(
        select(InternationalTransfer).where(
            InternationalTransfer.id == transfer_id,
            InternationalTransfer.organization_id == organization_id,
        )
    )
    transfer = result.scalar_one_or_none()

    if transfer is None:
        raise _not_found("Transferencia internacional no encontrada")

    return transfer


async def crear_transferencia(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: InternationalTransferCreate,
) -> InternationalTransfer:
    await obtener_tratamiento(db, organization_id, treatment_id)

    if payload.vendor_id is not None:
        await obtener_vendor(db, organization_id, payload.vendor_id)

    transfer = InternationalTransfer(
        organization_id=organization_id,
        treatment_id=treatment_id,
        created_by=profile_id,
        updated_by=profile_id,
        **payload.model_dump(),
    )
    db.add(transfer)
    await db.flush()
    return transfer


async def actualizar_transferencia(
    db: AsyncSession,
    organization_id: uuid.UUID,
    transfer_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: InternationalTransferUpdate,
) -> InternationalTransfer:
    transfer = await obtener_transferencia(
        db,
        organization_id,
        transfer_id,
    )
    changes = payload.model_dump(exclude_unset=True)

    if "destination_country" in changes and changes["destination_country"] is None:
        raise _bad_request("destination_country no puede ser null")

    vendor_id = changes.get("vendor_id", transfer.vendor_id)
    recipient_name = changes.get("recipient_name", transfer.recipient_name)

    if vendor_id is None and not recipient_name:
        raise _bad_request(
            "Debe indicar vendor_id o recipient_name para la transferencia"
        )

    if vendor_id is not None:
        await obtener_vendor(db, organization_id, vendor_id)

    for field, value in changes.items():
        setattr(transfer, field, value)

    transfer.updated_by = profile_id
    await db.flush()
    return transfer


async def eliminar_transferencia(
    db: AsyncSession,
    organization_id: uuid.UUID,
    transfer_id: uuid.UUID,
) -> None:
    transfer = await obtener_transferencia(
        db,
        organization_id,
        transfer_id,
    )
    await db.delete(transfer)
    await db.flush()


# ── Lectura agregada de relaciones RAT ───────────────────────────────────────


async def listar_sistemas_tratamiento(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> list[System]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    result = await db.execute(
        select(System)
        .join(TreatmentSystem, TreatmentSystem.system_id == System.id)
        .where(
            TreatmentSystem.organization_id == organization_id,
            TreatmentSystem.treatment_id == treatment_id,
            System.organization_id == organization_id,
        )
        .order_by(System.name, System.id)
    )
    return list(result.scalars().all())


async def listar_vendors_tratamiento(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
) -> list[TreatmentVendor]:
    await obtener_tratamiento(db, organization_id, treatment_id)

    result = await db.execute(
        select(TreatmentVendor)
        .where(
            TreatmentVendor.organization_id == organization_id,
            TreatmentVendor.treatment_id == treatment_id,
        )
        .order_by(
            TreatmentVendor.vendor_id,
            TreatmentVendor.relationship_type,
            TreatmentVendor.id,
        )
    )
    return list(result.scalars().all())
