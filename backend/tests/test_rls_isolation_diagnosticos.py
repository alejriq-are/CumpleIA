"""RLS a nivel de base de datos para las tablas del Módulo 1 (Autodiagnóstico).

Paso 5 del prompt de docs/Modulo1/PROMPT_modulo1_cuestionario.md: confirmar que
las tablas tenant-scoped del cuestionario (`diagnostics`/`diagnostic_answers`
en el esquema real — el prompt las menciona como `autodiagnosticos`/
`autodiagnostico_respuestas`, ver comentario de la migración 0002) siguen
aislando por organización como en Fase 0. Extendido en Fase 1/Módulo 1/Tarea 1
(Paso 1.3) para cubrir también `findings` (el modelo "Brecha" del plan).

Mismo patrón que test_rls_isolation.py: habla directo con Postgres usando el
rol restringido `app_user` (APP_DATABASE_URL, sin BYPASSRLS), sin pasar por
FastAPI. Las políticas (`tenant_isolation_select`/`tenant_isolation_modify`)
ya existen desde la migración 0001 — este archivo es el que faltaba para
probarlas contra estas tablas específicas, no solo dejarlas cubiertas
"por generalización" del bucle que las crea.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import delete, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.models import (
    ConfigVersion,
    Diagnostic,
    DiagnosticAnswer,
    Finding,
    ReferenceDocument,
)

settings = get_settings()


@pytest_asyncio.fixture(loop_scope="function")
async def app_role_session():
    """Ver docstring equivalente en test_rls_isolation.py."""
    engine = create_async_engine(settings.app_database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
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
async def diagnostico_org_a(_session_factory, org_a_id, profile_a_id, _seed_test_data):
    """Crea un Diagnostic de la organización A con el rol admin (sin RLS) —
    igual que el resto de los fixtures de datos de test— y lo limpia al final.

    `config_version_id` es FK obligatoria; usa la versión activa sembrada por
    scripts/seed_modulo1_cuestionario.py (config global, no tenant-scoped).
    """
    async with _session_factory() as session:
        version_id = await session.scalar(
            select(ConfigVersion.id).where(ConfigVersion.activa.is_(True))
        )
        assert version_id is not None, (
            "No hay config_versiones activa — corre "
            "scripts/seed_modulo1_cuestionario.py antes de este test."
        )
        diagnostic_id = uuid.uuid4()
        session.add(
            Diagnostic(
                id=diagnostic_id,
                organization_id=org_a_id,
                config_version_id=version_id,
                created_by=profile_a_id,
            )
        )
        await session.commit()

    yield diagnostic_id

    async with _session_factory() as session:
        await session.execute(
            delete(DiagnosticAnswer).where(
                DiagnosticAnswer.diagnostic_id == diagnostic_id
            )
        )
        await session.execute(delete(Diagnostic).where(Diagnostic.id == diagnostic_id))
        await session.commit()


# ── diagnostics ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_rls_permite_lectura_directa_de_diagnostics_propios(
    app_role_session, auth_a_id, org_a_id, diagnostico_org_a
):
    """Usuario A, consultando directo con SQL, ve el diagnóstico de su org."""
    await _set_auth_user(app_role_session, auth_a_id)
    result = await app_role_session.execute(
        text("SELECT id FROM diagnostics WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )
    assert result.first() is not None


@pytest.mark.asyncio
async def test_rls_bloquea_lectura_directa_de_diagnostics_ajenos(
    app_role_session, auth_b_id, org_a_id, diagnostico_org_a
):
    """Aunque el SQL no filtre por organization_id del lado de la app, RLS
    igual excluye el diagnóstico de la organización A para el usuario B."""
    await _set_auth_user(app_role_session, auth_b_id)
    result = await app_role_session.execute(
        text("SELECT id FROM diagnostics WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )
    assert result.first() is None


# ── diagnostic_answers ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_rls_bloquea_insert_de_respuesta_en_organizacion_ajena(
    app_role_session, auth_b_id, org_a_id, diagnostico_org_a
):
    """Usuario B no puede insertar una respuesta bajo la organización A, aunque
    conozca el diagnostic_id y el pregunta_id (ambos son datos públicos del
    catálogo salvo el diagnóstico en sí)."""
    await _set_auth_user(app_role_session, auth_b_id)

    with pytest.raises(DBAPIError, match="row-level security"):
        await app_role_session.execute(
            text(
                "INSERT INTO diagnostic_answers "
                "(organization_id, diagnostic_id, pregunta_id, answer) "
                "VALUES (:org_id, :diagnostic_id, :pregunta_id, 'Sí')"
            ),
            {
                "org_id": str(org_a_id),
                "diagnostic_id": str(diagnostico_org_a),
                "pregunta_id": "S1Q1",
            },
        )


@pytest.mark.asyncio
async def test_rls_permite_insert_de_respuesta_propia(
    app_role_session, auth_a_id, org_a_id, diagnostico_org_a
):
    """Usuario A sí puede insertar y luego leer una respuesta bajo su propia
    organización."""
    await _set_auth_user(app_role_session, auth_a_id)

    await app_role_session.execute(
        text(
            "INSERT INTO diagnostic_answers "
            "(organization_id, diagnostic_id, pregunta_id, answer) "
            "VALUES (:org_id, :diagnostic_id, :pregunta_id, 'Sí')"
        ),
        {
            "org_id": str(org_a_id),
            "diagnostic_id": str(diagnostico_org_a),
            "pregunta_id": "S1Q1",
        },
    )
    await app_role_session.commit()

    # set_config(..., is_local=true) se descarta al hacer commit — repoblarlo.
    await _set_auth_user(app_role_session, auth_a_id)
    result = await app_role_session.execute(
        text("SELECT answer FROM diagnostic_answers WHERE diagnostic_id = :id"),
        {"id": str(diagnostico_org_a)},
    )
    row = result.first()
    assert row is not None
    assert row[0] == "Sí"


# ── findings (Brecha) ─────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def hallazgo_org_a(_session_factory, org_a_id, diagnostico_org_a):
    """Crea un Finding ("Brecha") de la organización A con el rol admin (sin
    RLS), colgado del diagnóstico de `diagnostico_org_a`, y lo limpia al final.
    """
    async with _session_factory() as session:
        finding_id = uuid.uuid4()
        session.add(
            Finding(
                id=finding_id,
                organization_id=org_a_id,
                diagnostic_id=diagnostico_org_a,
                description="Falta designar responsable de protección de datos.",
                risk="alto",
            )
        )
        await session.commit()

    yield finding_id

    async with _session_factory() as session:
        await session.execute(delete(Finding).where(Finding.id == finding_id))
        await session.commit()


@pytest.mark.asyncio
async def test_rls_permite_lectura_directa_de_findings_propios(
    app_role_session, auth_a_id, org_a_id, hallazgo_org_a
):
    """Usuario A, consultando directo con SQL, ve el hallazgo de su org."""
    await _set_auth_user(app_role_session, auth_a_id)
    result = await app_role_session.execute(
        text("SELECT id FROM findings WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )
    assert result.first() is not None


@pytest.mark.asyncio
async def test_rls_bloquea_lectura_directa_de_findings_ajenos(
    app_role_session, auth_b_id, org_a_id, hallazgo_org_a
):
    """El usuario B no ve el hallazgo de la organización A, aunque el SQL no
    filtre por organization_id del lado de la app."""
    await _set_auth_user(app_role_session, auth_b_id)
    result = await app_role_session.execute(
        text("SELECT id FROM findings WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )
    assert result.first() is None


@pytest.mark.asyncio
async def test_rls_bloquea_insert_de_finding_en_organizacion_ajena(
    app_role_session, auth_b_id, org_a_id
):
    """Usuario B no puede crear un hallazgo bajo la organización A."""
    await _set_auth_user(app_role_session, auth_b_id)

    with pytest.raises(DBAPIError, match="row-level security"):
        await app_role_session.execute(
            text(
                "INSERT INTO findings (organization_id, description, risk) "
                "VALUES (:org_id, 'Hallazgo ajeno', 'alto')"
            ),
            {"org_id": str(org_a_id)},
        )


# ── reference_documents (Tarea 3, ADR 0002 capa 3) ────────────────────────────


@pytest_asyncio.fixture
async def documento_referencia_org_a(_session_factory, org_a_id):
    """Crea un ReferenceDocument de la organización A con el rol admin (sin
    RLS), y lo limpia al final — mismo patrón que hallazgo_org_a."""
    async with _session_factory() as session:
        documento_id = uuid.uuid4()
        session.add(
            ReferenceDocument(
                id=documento_id,
                organization_id=org_a_id,
                tipo="politica_interna_gobernanza",
                titulo="Política interna de gobernanza de datos",
                url="https://ejemplo.cl/politica-gobernanza.pdf",
            )
        )
        await session.commit()

    yield documento_id

    async with _session_factory() as session:
        await session.execute(
            delete(ReferenceDocument).where(ReferenceDocument.id == documento_id)
        )
        await session.commit()


@pytest.mark.asyncio
async def test_rls_permite_lectura_directa_de_reference_documents_propios(
    app_role_session, auth_a_id, org_a_id, documento_referencia_org_a
):
    """Usuario A, consultando directo con SQL, ve su propio documento de
    referencia."""
    await _set_auth_user(app_role_session, auth_a_id)
    result = await app_role_session.execute(
        text("SELECT id FROM reference_documents WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )
    assert result.first() is not None


@pytest.mark.asyncio
async def test_rls_bloquea_lectura_directa_de_reference_documents_ajenos(
    app_role_session, auth_b_id, org_a_id, documento_referencia_org_a
):
    """El usuario B no ve el documento de referencia de la organización A."""
    await _set_auth_user(app_role_session, auth_b_id)
    result = await app_role_session.execute(
        text("SELECT id FROM reference_documents WHERE organization_id = :org_id"),
        {"org_id": str(org_a_id)},
    )
    assert result.first() is None


@pytest.mark.asyncio
async def test_rls_bloquea_insert_de_reference_document_en_organizacion_ajena(
    app_role_session, auth_b_id, org_a_id
):
    """Usuario B no puede vincular un documento de referencia bajo la
    organización A."""
    await _set_auth_user(app_role_session, auth_b_id)

    with pytest.raises(DBAPIError, match="row-level security"):
        await app_role_session.execute(
            text(
                "INSERT INTO reference_documents "
                "(organization_id, tipo, titulo, url) "
                "VALUES (:org_id, 'politica_interna_gobernanza', "
                "'Documento ajeno', 'https://ejemplo.cl/ajeno.pdf')"
            ),
            {"org_id": str(org_a_id)},
        )
