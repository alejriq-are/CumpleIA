"""Tests funcionales del service layer del Módulo 2 — RAT."""

import pytest
from fastapi import HTTPException
from sqlalchemy import delete, select

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
    TreatmentCreate,
    TreatmentDataCategoryIn,
    TreatmentDataSourceIn,
    TreatmentDataSubjectIn,
    TreatmentPurposeIn,
    TreatmentUpdate,
    TreatmentVendorIn,
    VendorCreate,
)
from app.services import rat as rat_service


@pytest.mark.asyncio
async def test_crear_listar_obtener_y_actualizar_tratamiento(
    _session_factory, org_a_id, profile_a_id, _seed_test_data
):
    async with _session_factory() as db:
        treatment = await rat_service.crear_tratamiento(
            db,
            org_a_id,
            profile_a_id,
            TreatmentCreate(
                name="Gestión de clientes",
                organization_role="responsable",
                business_area="Comercial",
            ),
        )
        await db.commit()

        treatment_id = treatment.id

    async with _session_factory() as db:
        listado = await rat_service.listar_tratamientos(db, org_a_id)
        assert any(t.id == treatment_id for t in listado)

        obtenido = await rat_service.obtener_tratamiento(db, org_a_id, treatment_id)
        assert obtenido.name == "Gestión de clientes"

        actualizado = await rat_service.actualizar_tratamiento(
            db,
            org_a_id,
            treatment_id,
            profile_a_id,
            TreatmentUpdate(
                name="Gestión comercial de clientes",
                status="activo",
            ),
        )
        await db.commit()

        assert actualizado.name == "Gestión comercial de clientes"
        assert actualizado.status == "activo"

    async with _session_factory() as db:
        await db.execute(delete(Treatment).where(Treatment.id == treatment_id))
        await db.commit()


@pytest.mark.asyncio
async def test_eliminar_tratamiento(
    _session_factory, org_a_id, profile_a_id, _seed_test_data
):
    async with _session_factory() as db:
        treatment = await rat_service.crear_tratamiento(
            db,
            org_a_id,
            profile_a_id,
            TreatmentCreate(name="Tratamiento a eliminar"),
        )
        await db.commit()
        treatment_id = treatment.id

    async with _session_factory() as db:
        await rat_service.eliminar_tratamiento(db, org_a_id, treatment_id)
        await db.commit()

    async with _session_factory() as db:
        result = await db.execute(select(Treatment).where(Treatment.id == treatment_id))
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_reemplazar_componentes_normalizados(
    _session_factory, org_a_id, profile_a_id, _seed_test_data
):
    async with _session_factory() as db:
        treatment = await rat_service.crear_tratamiento(
            db,
            org_a_id,
            profile_a_id,
            TreatmentCreate(name="Tratamiento normalizado"),
        )
        await db.flush()
        treatment_id = treatment.id

        await rat_service.reemplazar_finalidades(
            db,
            org_a_id,
            treatment_id,
            profile_a_id,
            [
                TreatmentPurposeIn(
                    purpose="Prestar el servicio",
                    is_primary=True,
                    sort_order=0,
                ),
                TreatmentPurposeIn(
                    purpose="Facturación",
                    is_primary=False,
                    sort_order=1,
                ),
            ],
        )

        await rat_service.reemplazar_categorias_datos(
            db,
            org_a_id,
            treatment_id,
            profile_a_id,
            [
                TreatmentDataCategoryIn(
                    category_code="identificacion",
                    category_name="Datos de identificación",
                )
            ],
        )

        await rat_service.reemplazar_titulares_datos(
            db,
            org_a_id,
            treatment_id,
            profile_a_id,
            [
                TreatmentDataSubjectIn(
                    category_code="clientes",
                    category_name="Clientes",
                )
            ],
        )

        await rat_service.reemplazar_fuentes_datos(
            db,
            org_a_id,
            treatment_id,
            profile_a_id,
            [
                TreatmentDataSourceIn(
                    source_type="titular",
                    description="Formulario web",
                )
            ],
        )

        await db.commit()

    async with _session_factory() as db:
        purposes = (
            (
                await db.execute(
                    select(TreatmentPurpose).where(
                        TreatmentPurpose.treatment_id == treatment_id
                    )
                )
            )
            .scalars()
            .all()
        )
        categories = (
            (
                await db.execute(
                    select(TreatmentDataCategory).where(
                        TreatmentDataCategory.treatment_id == treatment_id
                    )
                )
            )
            .scalars()
            .all()
        )
        subjects = (
            (
                await db.execute(
                    select(TreatmentDataSubject).where(
                        TreatmentDataSubject.treatment_id == treatment_id
                    )
                )
            )
            .scalars()
            .all()
        )
        sources = (
            (
                await db.execute(
                    select(TreatmentDataSource).where(
                        TreatmentDataSource.treatment_id == treatment_id
                    )
                )
            )
            .scalars()
            .all()
        )

        assert len(purposes) == 2
        assert sum(1 for p in purposes if p.is_primary) == 1
        assert len(categories) == 1
        assert len(subjects) == 1
        assert len(sources) == 1

        await db.execute(delete(Treatment).where(Treatment.id == treatment_id))
        await db.commit()


@pytest.mark.asyncio
async def test_relacion_system_same_tenant_y_rechazo_cross_tenant(
    _session_factory,
    org_a_id,
    org_b_id,
    profile_a_id,
    _seed_test_data,
):
    async with _session_factory() as db:
        treatment = await rat_service.crear_tratamiento(
            db,
            org_a_id,
            profile_a_id,
            TreatmentCreate(name="Tratamiento sistemas"),
        )
        system_a = await rat_service.crear_sistema(
            db,
            org_a_id,
            profile_a_id,
            SystemCreate(name="CRM A"),
        )
        system_b = await rat_service.crear_sistema(
            db,
            org_b_id,
            profile_a_id,
            SystemCreate(name="CRM B"),
        )
        await db.flush()

        treatment_id = treatment.id
        system_a_id = system_a.id
        system_b_id = system_b.id

        rows = await rat_service.reemplazar_sistemas_tratamiento(
            db,
            org_a_id,
            treatment_id,
            profile_a_id,
            [system_a_id],
        )
        assert len(rows) == 1

        with pytest.raises(HTTPException) as exc:
            await rat_service.reemplazar_sistemas_tratamiento(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                [system_b_id],
            )
        assert exc.value.status_code == 400

        await db.rollback()

    async with _session_factory() as db:
        await db.execute(
            delete(TreatmentSystem).where(TreatmentSystem.treatment_id == treatment_id)
        )
        await db.execute(
            delete(System).where(System.id.in_([system_a_id, system_b_id]))
        )
        await db.execute(delete(Treatment).where(Treatment.id == treatment_id))
        await db.commit()


@pytest.mark.asyncio
async def test_relacion_vendor_y_transferencia_internacional(
    _session_factory,
    org_a_id,
    org_b_id,
    profile_a_id,
    _seed_test_data,
):
    async with _session_factory() as db:
        treatment = await rat_service.crear_tratamiento(
            db,
            org_a_id,
            profile_a_id,
            TreatmentCreate(name="Tratamiento proveedores"),
        )
        vendor_a = await rat_service.crear_vendor(
            db,
            org_a_id,
            profile_a_id,
            VendorCreate(name="Proveedor A", country="Chile"),
        )
        vendor_b = await rat_service.crear_vendor(
            db,
            org_b_id,
            profile_a_id,
            VendorCreate(name="Proveedor B", country="Estados Unidos"),
        )
        await db.flush()

        treatment_id = treatment.id
        vendor_a_id = vendor_a.id
        vendor_b_id = vendor_b.id

        relaciones = await rat_service.reemplazar_vendors_tratamiento(
            db,
            org_a_id,
            treatment_id,
            profile_a_id,
            [
                TreatmentVendorIn(
                    vendor_id=vendor_a_id,
                    relationship_type="encargado",
                    purpose="Hosting",
                    has_data_access=True,
                )
            ],
        )
        assert len(relaciones) == 1

        transfer = await rat_service.crear_transferencia(
            db,
            org_a_id,
            treatment_id,
            profile_a_id,
            InternationalTransferCreate(
                vendor_id=vendor_a_id,
                destination_country="Estados Unidos",
                adequacy_status="pendiente",
            ),
        )
        await db.flush()
        transfer_id = transfer.id

        actualizado = await rat_service.actualizar_transferencia(
            db,
            org_a_id,
            transfer_id,
            profile_a_id,
            InternationalTransferUpdate(
                adequacy_status="no_determinado",
                mechanism="Cláusulas contractuales",
            ),
        )

        assert actualizado.adequacy_status == "no_determinado"
        assert actualizado.mechanism == "Cláusulas contractuales"

        with pytest.raises(HTTPException) as exc:
            await rat_service.crear_transferencia(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                InternationalTransferCreate(
                    vendor_id=vendor_b_id,
                    destination_country="Estados Unidos",
                ),
            )
        assert exc.value.status_code == 404

        await db.commit()

    async with _session_factory() as db:
        await db.execute(
            delete(InternationalTransfer).where(InternationalTransfer.id == transfer_id)
        )
        await db.execute(
            delete(TreatmentVendor).where(TreatmentVendor.treatment_id == treatment_id)
        )
        await db.execute(
            delete(Vendor).where(Vendor.id.in_([vendor_a_id, vendor_b_id]))
        )
        await db.execute(delete(Treatment).where(Treatment.id == treatment_id))
        await db.commit()
