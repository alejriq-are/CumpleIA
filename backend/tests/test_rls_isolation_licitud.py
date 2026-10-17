"""Persistencia, RLS e integridad multi-tenant del Módulo 3 — Bases de Licitud.

Valida cuatro capas de persistencia:

1. RLS real usando `app_user` sin BYPASSRLS.
2. Integridad referencial tenant-aware mediante FK compuestas.
3. Restricciones de ciclo de vida y versionado.
4. Persistencia válida de series y evaluaciones de bases de licitud.

No prueba API, servicios ni frontend: M3-T1 cubre únicamente persistencia.
"""

import uuid

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import delete, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.models import LegalAssessment, LegalAssessmentSeries, Treatment
from app.services.licitud import confirm_legal_assessment_v1

settings = get_settings()


@pytest_asyncio.fixture(loop_scope="function")
async def app_role_session():
    """Sesión directa como app_user, con RLS realmente activo."""
    engine = create_async_engine(
        settings.app_database_url,
        poolclass=NullPool,
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await engine.dispose()


async def _set_auth_user(session, auth_user_id) -> None:
    await session.execute(
        text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
        {"sub": str(auth_user_id)},
    )


@pytest_asyncio.fixture
async def licitud_base_data(
    _session_factory,
    org_a_id,
    org_b_id,
    profile_a_id,
    profile_b_id,
    _seed_test_data,
):
    """Crea treatments y persistencia M3 base en dos organizaciones."""
    treatment_a_id = uuid.uuid4()
    treatment_b_id = uuid.uuid4()
    series_a_id = uuid.uuid4()
    series_b_id = uuid.uuid4()
    assessment_a_id = uuid.uuid4()
    assessment_b_id = uuid.uuid4()

    async with _session_factory() as session:
        session.add_all(
            [
                Treatment(
                    id=treatment_a_id,
                    organization_id=org_a_id,
                    name="Gestión clientes Org A",
                    organization_role="responsable",
                ),
                Treatment(
                    id=treatment_b_id,
                    organization_id=org_b_id,
                    name="Gestión clientes Org B",
                    organization_role="responsable",
                ),
            ]
        )
        await session.flush()

        session.add_all(
            [
                LegalAssessmentSeries(
                    id=series_a_id,
                    organization_id=org_a_id,
                    treatment_id=treatment_a_id,
                    purpose_key="gestion_clientes",
                    purpose_text="Gestionar relación con clientes",
                    created_by=profile_a_id,
                    updated_by=profile_a_id,
                ),
                LegalAssessmentSeries(
                    id=series_b_id,
                    organization_id=org_b_id,
                    treatment_id=treatment_b_id,
                    purpose_key="gestion_clientes",
                    purpose_text="Gestionar relación con clientes",
                    created_by=profile_b_id,
                    updated_by=profile_b_id,
                ),
            ]
        )
        await session.flush()

        session.add_all(
            [
                LegalAssessment(
                    id=assessment_a_id,
                    organization_id=org_a_id,
                    series_id=series_a_id,
                    treatment_id=treatment_a_id,
                    version=1,
                    status="borrador",
                    legal_basis="contrato_precontractual_art13c",
                    justification="Necesario para gestionar la relación contractual.",
                    purpose_snapshot="Gestionar relación con clientes",
                    rat_context_hash="hash-org-a-v1",
                    rat_context_snapshot={"treatment_id": str(treatment_a_id)},
                    schema_version=1,
                    rat_context_schema_version=1,
                    created_by=profile_a_id,
                    updated_by=profile_a_id,
                ),
                LegalAssessment(
                    id=assessment_b_id,
                    organization_id=org_b_id,
                    series_id=series_b_id,
                    treatment_id=treatment_b_id,
                    version=1,
                    status="borrador",
                    legal_basis="contrato_precontractual_art13c",
                    justification="Necesario para gestionar la relación contractual.",
                    purpose_snapshot="Gestionar relación con clientes",
                    rat_context_hash="hash-org-b-v1",
                    rat_context_snapshot={"treatment_id": str(treatment_b_id)},
                    schema_version=1,
                    rat_context_schema_version=1,
                    created_by=profile_b_id,
                    updated_by=profile_b_id,
                ),
            ]
        )
        await session.commit()

    yield {
        "treatment_a": treatment_a_id,
        "treatment_b": treatment_b_id,
        "series_a": series_a_id,
        "series_b": series_b_id,
        "assessment_a": assessment_a_id,
        "assessment_b": assessment_b_id,
    }

    # Limpieza explícita en orden FK-seguro.
    async with _session_factory() as session:
        await session.execute(
            delete(LegalAssessment).where(
                LegalAssessment.id.in_([assessment_a_id, assessment_b_id])
            )
        )
        await session.execute(
            delete(LegalAssessmentSeries).where(
                LegalAssessmentSeries.id.in_([series_a_id, series_b_id])
            )
        )
        await session.execute(
            delete(Treatment).where(Treatment.id.in_([treatment_a_id, treatment_b_id]))
        )
        await session.commit()


# ── RLS ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_rls_licitud_permite_lectura_de_series_propias(
    app_role_session,
    auth_a_id,
    org_a_id,
    licitud_base_data,
):
    await _set_auth_user(app_role_session, auth_a_id)

    result = await app_role_session.execute(
        text(
            "SELECT id FROM legal_assessment_series " "WHERE organization_id = :org_id"
        ),
        {"org_id": str(org_a_id)},
    )

    ids = {row[0] for row in result}
    assert licitud_base_data["series_a"] in ids


@pytest.mark.asyncio
async def test_rls_licitud_bloquea_lectura_de_series_ajenas(
    app_role_session,
    auth_b_id,
    org_a_id,
    licitud_base_data,
):
    await _set_auth_user(app_role_session, auth_b_id)

    result = await app_role_session.execute(
        text(
            "SELECT id FROM legal_assessment_series " "WHERE organization_id = :org_id"
        ),
        {"org_id": str(org_a_id)},
    )

    assert result.first() is None


@pytest.mark.asyncio
async def test_rls_licitud_bloquea_lectura_de_evaluaciones_ajenas(
    app_role_session,
    auth_b_id,
    org_a_id,
    licitud_base_data,
):
    await _set_auth_user(app_role_session, auth_b_id)

    result = await app_role_session.execute(
        text("SELECT id FROM legal_assessments " "WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )

    assert result.first() is None


@pytest.mark.asyncio
async def test_rls_licitud_bloquea_insert_de_serie_en_org_ajena(
    app_role_session,
    auth_b_id,
    org_a_id,
    licitud_base_data,
):
    await _set_auth_user(app_role_session, auth_b_id)

    with pytest.raises(DBAPIError, match="row-level security"):
        await app_role_session.execute(
            text(
                """
                INSERT INTO legal_assessment_series
                    (
                        organization_id,
                        treatment_id,
                        purpose_key,
                        purpose_text
                    )
                VALUES
                    (
                        :org_id,
                        :treatment_id,
                        :purpose_key,
                        :purpose_text
                    )
                """
            ),
            {
                "org_id": str(org_a_id),
                "treatment_id": str(licitud_base_data["treatment_a"]),
                "purpose_key": "insercion_no_autorizada",
                "purpose_text": "Finalidad no autorizada",
            },
        )


# ── Integridad cross-tenant ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fk_compuesta_bloquea_serie_con_treatment_cross_tenant(
    _session_factory,
    org_a_id,
    licitud_base_data,
):
    async with _session_factory() as session:
        session.add(
            LegalAssessmentSeries(
                organization_id=org_a_id,
                treatment_id=licitud_base_data["treatment_b"],
                purpose_key="cross_tenant",
                purpose_text="Serie inválida",
            )
        )

        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()


@pytest.mark.asyncio
async def test_fk_compuesta_bloquea_assessment_con_serie_cross_tenant(
    _session_factory,
    org_a_id,
    licitud_base_data,
):
    async with _session_factory() as session:
        session.add(
            LegalAssessment(
                organization_id=org_a_id,
                series_id=licitud_base_data["series_b"],
                treatment_id=licitud_base_data["treatment_a"],
                version=2,
                status="borrador",
                purpose_snapshot="Evaluación inválida",
                rat_context_hash="cross-tenant",
                rat_context_snapshot={},
            )
        )

        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()


# ── Restricciones de dominio / ciclo de vida ─────────────────────────────────


@pytest.mark.asyncio
async def test_licitud_bloquea_base_legal_invalida(
    _session_factory,
    org_a_id,
    licitud_base_data,
):
    async with _session_factory() as session:
        series = LegalAssessmentSeries(
            organization_id=org_a_id,
            treatment_id=licitud_base_data["treatment_a"],
            purpose_key="base_legal_invalida",
            purpose_text="Serie aislada para validar base legal",
        )
        session.add(series)
        await session.flush()

        session.add(
            LegalAssessment(
                organization_id=org_a_id,
                series_id=series.id,
                treatment_id=licitud_base_data["treatment_a"],
                version=1,
                status="borrador",
                legal_basis="base_inexistente",
                purpose_snapshot="Gestionar relación con clientes",
                rat_context_hash="hash-invalid-basis",
                rat_context_snapshot={},
            )
        )

        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()


@pytest.mark.asyncio
async def test_licitud_bloquea_confirmado_sin_confirmacion(
    _session_factory,
    org_a_id,
    licitud_base_data,
):
    async with _session_factory() as session:
        session.add(
            LegalAssessment(
                organization_id=org_a_id,
                series_id=licitud_base_data["series_a"],
                treatment_id=licitud_base_data["treatment_a"],
                version=2,
                status="confirmado",
                legal_basis="interes_legitimo_art13d",
                purpose_snapshot="Gestionar relación con clientes",
                rat_context_hash="hash-confirmado-invalido",
                rat_context_snapshot={},
            )
        )

        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()


@pytest.mark.asyncio
async def test_licitud_bloquea_segundo_borrador_en_misma_serie(
    _session_factory,
    org_a_id,
    licitud_base_data,
):
    async with _session_factory() as session:
        session.add(
            LegalAssessment(
                organization_id=org_a_id,
                series_id=licitud_base_data["series_a"],
                treatment_id=licitud_base_data["treatment_a"],
                version=2,
                status="borrador",
                legal_basis="interes_legitimo_art13d",
                purpose_snapshot="Gestionar relación con clientes",
                rat_context_hash="hash-second-draft",
                rat_context_snapshot={},
            )
        )

        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()


# ── Persistencia válida ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_licitud_persistencia_valida_mismo_tenant(
    _session_factory,
    org_a_id,
    licitud_base_data,
):
    async with _session_factory() as session:
        series = await session.scalar(
            select(LegalAssessmentSeries).where(
                LegalAssessmentSeries.id == licitud_base_data["series_a"],
                LegalAssessmentSeries.organization_id == org_a_id,
            )
        )
        assessment = await session.scalar(
            select(LegalAssessment).where(
                LegalAssessment.id == licitud_base_data["assessment_a"],
                LegalAssessment.organization_id == org_a_id,
            )
        )

        assert series is not None
        assert series.treatment_id == licitud_base_data["treatment_a"]
        assert series.next_version == 1

        assert assessment is not None
        assert assessment.series_id == licitud_base_data["series_a"]
        assert assessment.treatment_id == licitud_base_data["treatment_a"]
        assert assessment.version == 1
        assert assessment.status == "borrador"
        assert assessment.legal_basis == "contrato_precontractual_art13c"
        assert assessment.schema_version == 1
        assert assessment.rat_context_schema_version == 1


@pytest.mark.parametrize("requested_tenant", ["a", "b"])
async def test_confirmacion_no_accede_a_evaluacion_otro_tenant(
    app_role_session,
    licitud_base_data,
    auth_a_id,
    org_a_id,
    org_b_id,
    profile_a_id,
    requested_tenant,
):
    await _set_auth_user(app_role_session, auth_a_id)
    with pytest.raises(HTTPException) as exc:
        await confirm_legal_assessment_v1(
            app_role_session,
            org_a_id if requested_tenant == "a" else org_b_id,
            licitud_base_data["treatment_b"],
            licitud_base_data["assessment_b"],
            profile_a_id,
        )
    assert exc.value.status_code == 404
