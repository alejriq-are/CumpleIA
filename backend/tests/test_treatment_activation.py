"""M2-T3.0: declaraciones y transiciones del RAT."""

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.db.models import Treatment
from app.schemas.rat import (
    TreatmentCreate,
    TreatmentDataCategoryIn,
    TreatmentDataSourceIn,
    TreatmentDataSubjectIn,
    TreatmentPurposeIn,
    TreatmentUpdate,
)
from app.services import rat as rat_service


@pytest.mark.asyncio
async def test_activation_requires_all_fields_and_revalidates_archived(
    _session_factory, org_a_id, profile_a_id, _seed_test_data
):
    async with _session_factory() as db:
        treatment = await rat_service.crear_tratamiento(
            db, org_a_id, profile_a_id, TreatmentCreate(name="Clientes")
        )
        treatment_id = treatment.id
        await db.commit()

    try:
        async with _session_factory() as db:
            with pytest.raises(HTTPException) as exc:
                await rat_service.actualizar_tratamiento(
                    db,
                    org_a_id,
                    treatment_id,
                    profile_a_id,
                    TreatmentUpdate(status="activo"),
                )
            assert exc.value.status_code == 400
            for field in (
                "organization_role",
                "retention_rule",
                "purposes",
                "data_categories",
                "data_subjects",
                "data_sources",
                "systems_declaration",
                "vendors_declaration",
                "international_transfers_declaration",
            ):
                assert field in exc.value.detail
            await db.rollback()

        async with _session_factory() as db:
            await rat_service.reemplazar_finalidades(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                [TreatmentPurposeIn(purpose="Prestar servicio")],
            )
            await rat_service.reemplazar_categorias_datos(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                [
                    TreatmentDataCategoryIn(
                        category_code="contacto", category_name="Contacto"
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
                        category_code="cliente", category_name="Cliente"
                    )
                ],
            )
            await rat_service.reemplazar_fuentes_datos(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                [TreatmentDataSourceIn(source_type="titular")],
            )
            active = await rat_service.actualizar_tratamiento(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                TreatmentUpdate(
                    status="activo",
                    organization_role="responsable",
                    retention_rule="Cinco años",
                    systems_declaration="no",
                    vendors_declaration="si",
                    international_transfers_declaration="no",
                ),
            )
            assert active.status == "activo"
            assert active.vendors_declaration == "si"
            await db.commit()

        async with _session_factory() as db:
            row = await rat_service.actualizar_tratamiento(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                TreatmentUpdate(status="archivado"),
            )
            assert row.status == "archivado"
            row = await rat_service.actualizar_tratamiento(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                TreatmentUpdate(status="activo"),
            )
            assert row.status == "activo"
            await db.commit()

        async with _session_factory() as db:
            for status in ("borrador", "archivado"):
                row = await rat_service.actualizar_tratamiento(
                    db,
                    org_a_id,
                    treatment_id,
                    profile_a_id,
                    TreatmentUpdate(status=status),
                )
                assert row.status == status
            await db.commit()
            with pytest.raises(HTTPException) as exc:
                await rat_service.actualizar_tratamiento(
                    db,
                    org_a_id,
                    treatment_id,
                    profile_a_id,
                    TreatmentUpdate(status="borrador"),
                )
            assert exc.value.status_code == 400
            await db.rollback()

        async with _session_factory() as db:
            with pytest.raises(HTTPException) as exc:
                await rat_service.actualizar_tratamiento(
                    db,
                    org_a_id,
                    treatment_id,
                    profile_a_id,
                    TreatmentUpdate(status="activo", retention_rule="   "),
                )
            assert "retention_rule" in exc.value.detail
            await db.rollback()

        async with _session_factory() as db:
            row = await rat_service.actualizar_tratamiento(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                TreatmentUpdate(status="activo"),
            )
            assert row.status == "activo"
            await db.commit()
    finally:
        async with _session_factory() as db:
            await db.execute(delete(Treatment).where(Treatment.id == treatment_id))
            await db.commit()


@pytest.mark.asyncio
async def test_activation_rejects_pending_declaration(
    _session_factory, org_a_id, profile_a_id, _seed_test_data
):
    async with _session_factory() as db:
        treatment = await rat_service.crear_tratamiento(
            db,
            org_a_id,
            profile_a_id,
            TreatmentCreate(name="Clientes con declaración pendiente"),
        )
        treatment_id = treatment.id
        await db.commit()

    try:
        async with _session_factory() as db:
            await rat_service.reemplazar_finalidades(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                [TreatmentPurposeIn(purpose="Prestar servicio")],
            )
            await rat_service.reemplazar_categorias_datos(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                [
                    TreatmentDataCategoryIn(
                        category_code="contacto",
                        category_name="Contacto",
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
                        category_code="cliente",
                        category_name="Cliente",
                    )
                ],
            )
            await rat_service.reemplazar_fuentes_datos(
                db,
                org_a_id,
                treatment_id,
                profile_a_id,
                [TreatmentDataSourceIn(source_type="titular")],
            )

            with pytest.raises(HTTPException) as exc:
                await rat_service.actualizar_tratamiento(
                    db,
                    org_a_id,
                    treatment_id,
                    profile_a_id,
                    TreatmentUpdate(
                        status="activo",
                        organization_role="responsable",
                        retention_rule="Cinco años",
                        systems_declaration="no",
                        vendors_declaration="pendiente",
                        international_transfers_declaration="no",
                    ),
                )

            assert exc.value.status_code == 400
            assert "vendors_declaration" in exc.value.detail
            await db.rollback()

        async with _session_factory() as db:
            row = await rat_service.obtener_tratamiento(
                db,
                org_a_id,
                treatment_id,
            )
            assert row.status == "borrador"

    finally:
        async with _session_factory() as db:
            await db.execute(delete(Treatment).where(Treatment.id == treatment_id))
            await db.commit()


@pytest.mark.asyncio
async def test_http_activation_rejects_incomplete_and_returns_declarations(
    client_a, org_a_id
):
    headers = {"X-Organization-Id": str(org_a_id)}
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        created = await client.post(
            "/rat/treatments",
            headers=headers,
            json={"name": "HTTP activation", "systems_declaration": "no"},
        )
        assert created.status_code == 201
        treatment_id = created.json()["id"]
        try:
            assert created.json()["systems_declaration"] == "no"
            assert created.json()["vendors_declaration"] is None
            response = await client.patch(
                f"/rat/treatments/{treatment_id}",
                headers=headers,
                json={"status": "activo"},
            )
            assert response.status_code == 400
            assert "data_sources" in response.json()["detail"]
            assert "vendors_declaration" in response.json()["detail"]
            invalid = await client.patch(
                f"/rat/treatments/{treatment_id}",
                headers=headers,
                json={"vendors_declaration": "tal vez"},
            )
            assert invalid.status_code == 422
            listed = await client.get("/rat/treatments", headers=headers)
            assert listed.status_code == 200
            assert (
                next(x for x in listed.json() if x["id"] == treatment_id)[
                    "systems_declaration"
                ]
                == "no"
            )
        finally:
            await client.delete(f"/rat/treatments/{treatment_id}", headers=headers)
