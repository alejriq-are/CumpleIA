"""RLS a nivel de base de datos para las tablas del Módulo 1 (Autodiagnóstico).

Paso 5 del prompt de docs/Modulo1/PROMPT_modulo1_cuestionario.md: confirmar que
las tablas tenant-scoped del cuestionario (`diagnostics`/`diagnostic_answers`
en el esquema real — el prompt las menciona como `autodiagnosticos`/
`autodiagnostico_respuestas`, ver comentario de la migración 0002) siguen
aislando por organización como en Fase 0.

Mismo patrón que test_rls_isolation.py: habla directo con Postgres usando el
rol restringido `app_user` (APP_DATABASE_URL, sin BYPASSRLS), sin pasar por
FastAPI. Las políticas (`tenant_isolation_select`/`tenant_isolation_modify`)
ya existen desde la migración 0001 — este archivo es el que faltaba para
probarlas contra estas dos tablas específicas, no solo dejarlas cubiertas
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
from app.db.models import ConfigVersion, Diagnostic, DiagnosticAnswer

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
