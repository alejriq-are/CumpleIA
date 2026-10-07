"""Fixtures compartidas para los tests de CumpleIA.

Estrategia de BD: los fixtures crean datos reales en la DB (commit),
los tests corren contra esos datos y el teardown los elimina.
El engine usa la misma DATABASE_URL del .env (requiere Docker Postgres activo).
"""

import os

# SUPABASE_URL es obligatorio para arrancar la app (config.py). Se define un valor
# de test ANTES de importar app.main; en CI/producción la env var real tiene
# prioridad y no es sobreescrita por setdefault.
os.environ.setdefault("SUPABASE_URL", "https://test-project.supabase.co")

import uuid  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from fastapi import Depends  # noqa: E402
from sqlalchemy import delete, select, text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.deps import get_current_profile  # noqa: E402
from app.db.models import (  # noqa: E402
    EipdResolutionReview,
    Membership,
    Organization,
    Profile,
    Subscription,
    SubscriptionCommitmentType,
    SubscriptionStatus,
    UserRole,
)
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

settings = get_settings()

# Variables de secretos que config.py exige en producción. En un entorno real
# (contenedor de dev o CI con dummies) están presentes en os.environ, y
# pydantic-settings las lee aunque se pase _env_file=None. Si no se neutralizan,
# el test que garantiza el arranque seguro en producción pasaría por omisión.
_SENSITIVE_ENV_VARS = (
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_ANON_KEY",
    "SECRET_KEY",
)


@pytest.fixture(autouse=True)
def _hermetic_settings(monkeypatch):
    """Aísla cada test de los secretos presentes en el entorno real.

    Borra las variables sensibles antes de cada test e invalida la caché de
    `get_settings()` para que cualquier reconstrucción de `Settings` vea el
    entorno neutralizado. `monkeypatch` restaura las variables al finalizar.

    Un test que necesite esos secretos presentes (p. ej. el caso inverso de
    producción) los define con `monkeypatch.setenv` dentro de su cuerpo: como
    corre después de este fixture, prevalece.
    """
    for var in _SENSITIVE_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


# IDs fijos: facilitan debugging y evitan colisiones entre ejecuciones
_ORG_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000001")
_ORG_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000001")
_PROFILE_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000002")
_PROFILE_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000002")
_AUTH_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000003")
_AUTH_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000003")


# ── Engine de test (NullPool: sin caché de conexiones, evita cross-loop reuse) ──

# Dos engines separados y con roles distintos, a propósito:
# - `_engine`/`_session_factory` (settings.database_url, rol admin): SOLO para
#   fixtures de setup/teardown/aserciones directas (sembrar orgs de test,
#   verificar filas). BYPASSRLS — nunca debe ser el que sirve una request HTTP
#   de los tests, porque eso escondería un bug real de RLS (pasó en Fase 0:
#   ver Claude_22_julio_2026/estado-23jul2026.md).
# - `_app_engine`/`_app_session_factory` (settings.app_database_url, `app_user`
#   real, sin BYPASSRLS): el que deben usar los overrides de get_db que sirven
#   una request de test, para que RLS esté realmente activo — igual que en
#   producción (ver app/db/session.py).


@pytest.fixture(scope="session")
def _engine():
    engine = create_async_engine(settings.database_url, echo=False, poolclass=NullPool)
    yield engine


@pytest.fixture(scope="session")
def _session_factory(_engine):
    return async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def _app_engine():
    engine = create_async_engine(
        settings.app_database_url, echo=False, poolclass=NullPool
    )
    yield engine


@pytest.fixture(scope="session")
def _app_session_factory(_app_engine):
    return async_sessionmaker(_app_engine, class_=AsyncSession, expire_on_commit=False)


# ── Datos de test (session-scoped: se crean una vez y se limpian al final) ────


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _seed_test_data(_session_factory):
    """Crea orgs, perfiles y membresías de test. Se limpia al final de la sesión."""
    async with _session_factory() as session:
        # Limpiar datos previos en orden FK-seguro (sin ORM cascade)
        # Historial protegido: limpieza administrativa explicita solo para tenants de test.
        await session.execute(
            text(
                "DELETE FROM eipd_confirmation_evidence WHERE organization_id IN (:a,:b)"
            ),
            {"a": _ORG_A_ID, "b": _ORG_B_ID},
        )
        await session.execute(
            text(
                "DELETE FROM eipd_policy_selector WHERE publication_id IN (SELECT id FROM eipd_policy_publications WHERE created_by IN (:a,:b) AND policy_reference LIKE 'TEST:%')"
            ),
            {"a": _PROFILE_A_ID, "b": _PROFILE_B_ID},
        )
        await session.execute(
            text(
                "DELETE FROM eipd_policy_selections WHERE publication_id IN (SELECT id FROM eipd_policy_publications WHERE created_by IN (:a,:b) AND policy_reference LIKE 'TEST:%')"
            ),
            {"a": _PROFILE_A_ID, "b": _PROFILE_B_ID},
        )
        await session.execute(
            text(
                "DELETE FROM eipd_policy_publications WHERE created_by IN (:a,:b) AND policy_reference LIKE 'TEST:%'"
            ),
            {"a": _PROFILE_A_ID, "b": _PROFILE_B_ID},
        )
        await session.execute(
            delete(EipdResolutionReview).where(
                EipdResolutionReview.organization_id.in_([_ORG_A_ID, _ORG_B_ID])
            )
        )
        await session.execute(
            delete(Subscription).where(
                Subscription.organization_id.in_([_ORG_A_ID, _ORG_B_ID])
            )
        )
        await session.execute(
            delete(Membership).where(
                Membership.organization_id.in_([_ORG_A_ID, _ORG_B_ID])
            )
        )
        await session.execute(
            delete(Organization).where(Organization.id.in_([_ORG_A_ID, _ORG_B_ID]))
        )
        await session.execute(
            delete(Profile).where(Profile.id.in_([_PROFILE_A_ID, _PROFILE_B_ID]))
        )
        await session.commit()

        # Crear perfiles (sin FK a organizations)
        profile_a = Profile(
            id=_PROFILE_A_ID,
            auth_user_id=_AUTH_A_ID,
            email="usuario_a@test.cl",
            full_name="Usuario A",
        )
        profile_b = Profile(
            id=_PROFILE_B_ID,
            auth_user_id=_AUTH_B_ID,
            email="usuario_b@test.cl",
            full_name="Usuario B",
        )
        session.add(profile_a)
        session.add(profile_b)
        await session.flush()

        # Crear organizaciones
        org_a = Organization(id=_ORG_A_ID, name="Organización A (test)", plan="free")
        org_b = Organization(id=_ORG_B_ID, name="Organización B (test)", plan="free")
        session.add(org_a)
        session.add(org_b)
        await session.flush()

        # Membresías: A → org_a, B → org_b (cada uno solo tiene acceso a la suya)
        session.add(
            Membership(
                organization_id=_ORG_A_ID, profile_id=_PROFILE_A_ID, role=UserRole.owner
            )
        )
        session.add(
            Membership(
                organization_id=_ORG_B_ID, profile_id=_PROFILE_B_ID, role=UserRole.owner
            )
        )

        # Toda organización real tiene exactamente una Subscription desde que
        # se crea (ver docs/adr/0001-modelo-organizaciones-roles-suscripcion.md
        # y app/api/organizations.py) — sin esto, org_a/org_b no serían
        # representativas de una organización real para los tests que ejercen
        # get_subscription_status o la RLS de `subscriptions`.
        session.add(
            Subscription(
                organization_id=_ORG_A_ID,
                commitment_type=SubscriptionCommitmentType.monthly,
                status=SubscriptionStatus.active,
                created_by=_PROFILE_A_ID,
            )
        )
        session.add(
            Subscription(
                organization_id=_ORG_B_ID,
                commitment_type=SubscriptionCommitmentType.monthly,
                status=SubscriptionStatus.active,
                created_by=_PROFILE_B_ID,
            )
        )
        await session.commit()

    yield  # tests corren aquí

    # Teardown: eliminar en orden FK-seguro via DELETE bulk (sin ORM cascade)
    async with _session_factory() as session:
        # Historial protegido: limpieza administrativa explicita solo para tenants de test.
        await session.execute(
            text(
                "DELETE FROM eipd_confirmation_evidence WHERE organization_id IN (:a,:b)"
            ),
            {"a": _ORG_A_ID, "b": _ORG_B_ID},
        )
        await session.execute(
            text(
                "DELETE FROM eipd_policy_selector WHERE publication_id IN (SELECT id FROM eipd_policy_publications WHERE created_by IN (:a,:b) AND policy_reference LIKE 'TEST:%')"
            ),
            {"a": _PROFILE_A_ID, "b": _PROFILE_B_ID},
        )
        await session.execute(
            text(
                "DELETE FROM eipd_policy_selections WHERE publication_id IN (SELECT id FROM eipd_policy_publications WHERE created_by IN (:a,:b) AND policy_reference LIKE 'TEST:%')"
            ),
            {"a": _PROFILE_A_ID, "b": _PROFILE_B_ID},
        )
        await session.execute(
            text(
                "DELETE FROM eipd_policy_publications WHERE created_by IN (:a,:b) AND policy_reference LIKE 'TEST:%'"
            ),
            {"a": _PROFILE_A_ID, "b": _PROFILE_B_ID},
        )
        await session.execute(
            delete(EipdResolutionReview).where(
                EipdResolutionReview.organization_id.in_([_ORG_A_ID, _ORG_B_ID])
            )
        )
        await session.execute(
            delete(Subscription).where(
                Subscription.organization_id.in_([_ORG_A_ID, _ORG_B_ID])
            )
        )
        await session.execute(
            delete(Membership).where(
                Membership.organization_id.in_([_ORG_A_ID, _ORG_B_ID])
            )
        )
        await session.execute(
            delete(Organization).where(Organization.id.in_([_ORG_A_ID, _ORG_B_ID]))
        )
        await session.execute(
            delete(Profile).where(Profile.id.in_([_PROFILE_A_ID, _PROFILE_B_ID]))
        )
        await session.commit()


# ── Perfiles expuestos a los tests ────────────────────────────────────────────


@pytest.fixture(scope="session")
def profile_a_id() -> uuid.UUID:
    return _PROFILE_A_ID


@pytest.fixture(scope="session")
def profile_b_id() -> uuid.UUID:
    return _PROFILE_B_ID


@pytest.fixture(scope="session")
def org_a_id() -> uuid.UUID:
    return _ORG_A_ID


@pytest.fixture(scope="session")
def org_b_id() -> uuid.UUID:
    return _ORG_B_ID


@pytest.fixture(scope="session")
def auth_a_id() -> uuid.UUID:
    """auth_user_id (el 'sub' del JWT) del perfil A, para firmar tokens de test."""
    return _AUTH_A_ID


@pytest.fixture(scope="session")
def auth_b_id() -> uuid.UUID:
    """auth_user_id (el 'sub' del JWT) del perfil B, para firmar tokens de test."""
    return _AUTH_B_ID


# ── Cliente HTTP con JWT override ─────────────────────────────────────────────


def _make_rls_db_override(auth_user_id: uuid.UUID, session_factory):
    """Override de get_db que corre contra `app_user` con RLS realmente activo.

    Puebla `request.jwt.claim.sub` al abrir la sesión — lo que en producción
    hace `get_current_profile()` real (ver app/core/deps.py) sobre la MISMA
    sesión que después sirve el resto del request. Acá hace falta hacerlo en
    el override de get_db porque get_current_profile también está overrideado
    (para no validar un JWT real en cada test) y por lo tanto nunca ejecuta
    ese set_config por su cuenta. Sin esto, auth.uid() quedaría NULL y RLS
    bloquearía todo (o, peor, pasaría inadvertido si el rol tuviera BYPASSRLS).
    """

    async def _override():
        async with session_factory() as session:
            await session.execute(
                text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
                {"sub": str(auth_user_id)},
            )
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return _override


def _make_profile_override_from_db(auth_user_id: uuid.UUID):
    """Override de get_current_profile que reutiliza la sesión de get_db.

    Depende de `get_db` (no abre una sesión propia) para que la lectura del
    perfil ocurra en la misma sesión donde ya corrió el set_config de
    `_make_rls_db_override` — si abriera una sesión aparte, sería una conexión
    distinta sin auth.uid() poblado y perfectamente podría devolver 0 filas
    bajo RLS.
    """

    async def _override(db: AsyncSession = Depends(get_db)) -> Profile:
        result = await db.execute(
            select(Profile).where(Profile.auth_user_id == auth_user_id)
        )
        return result.scalar_one()

    return _override


def _make_db_override(session_factory):
    """Override de get_db que usa el engine NullPool de test (rol admin, sin RLS).

    Solo para fixtures de setup/teardown que necesitan escribir sin pasar por
    políticas de organización (p. ej. sembrar datos). Refleja el `get_db` real
    (commit al terminar, rollback ante excepción): sin el commit, las
    escrituras del request se revertirían al cerrar la sesión y no serían
    visibles para requests posteriores ni para las aserciones.
    """

    async def _override():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return _override


@pytest.fixture
def client_a(_app_session_factory, auth_a_id, _seed_test_data):
    """AsyncClient autenticado como usuario A, contra `app_user` con RLS activo."""
    app.dependency_overrides[get_current_profile] = _make_profile_override_from_db(
        auth_a_id
    )
    app.dependency_overrides[get_db] = _make_rls_db_override(
        auth_a_id, _app_session_factory
    )
    yield app
    app.dependency_overrides.pop(get_current_profile, None)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client_b(_app_session_factory, auth_b_id, _seed_test_data):
    """AsyncClient autenticado como usuario B, contra `app_user` con RLS activo."""
    app.dependency_overrides[get_current_profile] = _make_profile_override_from_db(
        auth_b_id
    )
    app.dependency_overrides[get_db] = _make_rls_db_override(
        auth_b_id, _app_session_factory
    )
    yield app
    app.dependency_overrides.pop(get_current_profile, None)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def app_db_only(_app_session_factory, _seed_test_data):
    """App con SOLO get_db overrideado, contra `app_user` con RLS activo.

    A diferencia de client_a/client_b, NO sobreescribe get_current_profile: la
    validación real del JWT (ES256 + JWKS) se ejecuta, y el propio
    get_current_profile real hace su set_config sobre esta misma sesión — no
    hace falta el override especial de get_db con set_config incluido.
    """
    app.dependency_overrides[get_db] = _make_db_override(_app_session_factory)
    yield app
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def negative_controls():
    """Declaraciones negativas explícitas para escenarios ordinarios M3."""
    from typing import get_args

    from app.schemas.licitud import EipdQuestionIdV1, SpecialQuestionIdV1

    return {
        "special_conditions": {
            "declarations": [
                {
                    "question_id": q,
                    "answer": "no",
                    "rationale": "Alcance ordinario revisado",
                }
                for q in get_args(SpecialQuestionIdV1)
            ]
        },
        "eipd_screening": {
            "answers": [
                {"question_id": q, "answer": "no", "rationale": "Supuesto revisado"}
                for q in get_args(EipdQuestionIdV1)
            ]
        },
    }


@pytest.fixture
def complete_lia_context():
    rat = {
        "purpose": "Gestión de clientes",
        "organization_role": "responsable",
        "data_categories": [
            {
                "category_code": "id",
                "category_name": "Identidad",
                "is_sensitive": False,
                "notes": None,
            }
        ],
        "data_subjects": [
            {
                "category_code": "clientes",
                "category_name": "Clientes",
                "includes_children": False,
                "includes_adolescents": False,
                "is_vulnerable_group": False,
                "notes": None,
            }
        ],
        "data_sources": [
            {"source_type": "titular", "description": None, "is_public_source": False}
        ],
        "retention": {"retention_rule": "5 años", "deletion_method": None},
        "automated_decisions": {"has_automated_decisions": False, "description": None},
        "systems": [],
        "third_parties": [],
        "international_transfers": [],
        "special_regimes": {
            "has_sensitive_data": False,
            "includes_children": False,
            "includes_adolescents": False,
            "has_vulnerable_groups": False,
        },
    }
    lia = {
        "purpose_and_interest": {
            "purpose_description": " Gestión DE clientes ",
            "legitimate_interest": "Interés documentado",
            "interest_holder": "responsable",
            "controller_benefit": "Beneficio",
            "interest_importance": "Importancia",
            "consequences_without_processing": "Consecuencias",
        },
        "necessity": {
            "contributes_to_purpose": {"answer": "si"},
            "linked_to_interest": {"answer": "si"},
            "achievable_without_personal_data": {"answer": "no"},
            "less_intrusive_alternative": {"answer": "no"},
            "fewer_data_possible": {"answer": "no"},
            "categories_necessary_and_relevant": {"answer": "si"},
            "necessity_analysis": "Necesidad",
            "proportionality_analysis": "Proporcionalidad",
            "alternatives_analysis": "Alternativas",
            "minimization_analysis": "Minimización",
        },
        "nature_and_scope": {"exclusively_professional_context": {"answer": "no"}},
        "reasonable_expectations": {
            "prior_relationship": {"answer": "no"},
            "significant_change_of_use": {"answer": "no"},
            "informed_at_direct_collection": {"answer": "si"},
            "foreseeable_purpose_and_method": {"answer": "si"},
            "innovative_processing": {"answer": "no"},
            "expectations_analysis": "Expectativas",
        },
        "impact": {
            "negative_effects": "Sin efectos adicionales identificados",
            "severity": "baja",
            "likelihood": "baja",
            "loss_of_control": {"answer": "no"},
            "intrusion_analysis": "Intrusión",
            "reasonable_opposition_likelihood": {"answer": "no"},
            "rights_and_freedoms_analysis": "Derechos",
            "transparently_explainable": {"answer": "si"},
            "relevant_unmitigated_impacts": {"answer": "no"},
            "impact_analysis": "Impacto",
        },
        "safeguards": {"safeguards_analysis": "No se proponen medidas adicionales"},
        "transparency_and_opposition": {
            "information_method": "Aviso",
            "interest_communication": "Explicación",
            "opposition_channel": "Portal",
            "opposition_procedure": "Procedimiento",
            "responsible_area": "Área",
        },
        "conclusion": {
            "balancing_summary": "Ponderación",
            "identified_interest": "Interés",
            "necessity_and_proportionality_result": "Resultado",
            "main_impacts": "Impactos",
            "relevant_safeguards": "Salvaguardas",
            "rights_protection_reasoning": "Razonamiento",
            "decision": "puede_basarse",
        },
    }
    return lia, rat


@pytest.fixture
def complete_contract():
    return {
        "route": "ejecucion_contrato",
        "purpose_description": "Gestión de clientes",
        "relationship_description": "Titular y responsable son partes",
        "contractual_reference": "Contrato de servicio",
        "contractual_object": "Prestación del servicio",
        "processing_operations": "Registro de identidad para el servicio",
        "necessity_analysis": "Necesidad documentada",
        "data_minimization_analysis": "Solo datos necesarios",
        "holder_is_party": {"answer": "si", "rationale": "Relación documentada"},
        "necessary_for_route": {"answer": "si", "rationale": "Operación necesaria"},
        "purpose_within_route": {"answer": "si", "rationale": "Objeto contractual"},
        "evidence": [{"evidence_type": "contrato", "reference": "Documento interno"}],
    }


@pytest.fixture
def complete_legal_obligation():
    return {
        "route": "cumplimiento_obligacion_legal",
        "purpose_description": "Gestión de clientes",
        "normative_requirement_description": "Obligación concreta documentada",
        "processing_operations": "Operaciones documentadas",
        "applicability_analysis": "Aplicabilidad documentada",
        "necessity_analysis": "Necesidad documentada",
        "data_minimization_analysis": "Datos pertinentes",
        "normative_references": [
            {
                "norm_name": "Norma de prueba",
                "provision": "Disposición de prueba",
                "official_source_url": "https://www.bcn.cl/leychile/",
                "version_reference": "Versión analizada",
                "relevance_analysis": "Relación documentada",
            }
        ],
        "normative_basis_reviewed": {
            "answer": "si",
            "rationale": "Revisión documentada",
        },
        "normative_basis_in_force": {"answer": "si", "rationale": "Vigencia declarada"},
        "processing_within_legal_scope": {
            "answer": "si",
            "rationale": "Alcance analizado",
        },
        "obligation_applies_to_controller": {
            "answer": "si",
            "rationale": "Obligación aplicable",
        },
        "evidence": [{"evidence_type": "referencia", "reference": "Registro revisión"}],
    }


@pytest.fixture
def complete_rights_defense():
    return {
        "route": "defensa_derecho",
        "purpose_description": "Gestión de clientes",
        "right_description": "Derecho documentado",
        "right_basis_reference": "Fundamento documental",
        "right_holder": "responsable",
        "holder_connection_analysis": "Conexión documentada",
        "forum_type": "tribunal_justicia",
        "forum_description": "Foro documentado",
        "proceeding_stage": "en_curso",
        "proceeding_reference": "Referencia expediente",
        "processing_operations": "Operaciones documentadas",
        "necessity_analysis": "Necesidad documentada",
        "data_minimization_analysis": "Datos pertinentes",
        "related_to_right": {"answer": "si", "rationale": "Relación analizada"},
        "necessary_for_route": {"answer": "si", "rationale": "Necesidad analizada"},
        "within_forum_scope": {"answer": "si", "rationale": "Alcance analizado"},
        "evidence": [
            {"evidence_type": "registro", "reference": "Referencia documental"}
        ],
    }


@pytest.fixture
def complete_economic_obligations(complete_legal_obligation):
    data = {
        "route": "con_comunicacion",
        "obligation_type": "comercial",
        "normative_references": complete_legal_obligation["normative_references"],
        "evidence": complete_legal_obligation["evidence"],
    }
    for field in (
        "purpose_description",
        "obligation_description",
        "obligation_reference",
        "holder_connection_analysis",
        "processing_operations",
        "applicability_analysis",
        "data_minimization_analysis",
        "title_iii_analysis",
        "retention_and_deletion_analysis",
        "accuracy_and_update_analysis",
        "communication_scope",
        "communication_eligibility_analysis",
        "communication_restrictions_analysis",
        "payment_and_extinction_controls",
    ):
        data[field] = "Análisis documentado"
    data["purpose_description"] = "Gestión de clientes"
    for field in (
        "operations_include_communication",
        "related_to_obligation",
        "title_iii_reviewed",
        "processing_within_title_iii",
        "retention_and_deletion_compatible",
        "accuracy_controls_documented",
        "communication_permitted",
        "excluded_data_screened",
        "communication_limits_respected",
    ):
        data[field] = {"answer": "si", "rationale": "Revisión documentada"}
    return data


@pytest.fixture
def complete_geolocation():
    data = {
        "purpose_description": "Gestión de clientes",
        "scope": {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]},
        "notice_provided_on": "2026-10-06",
        "value_added_third_party_transfer": {
            "answer": "si",
            "rationale": "Servicio documentado",
        },
        "evidence": [{"evidence_type": "aviso", "reference": "Registro aviso"}],
    }
    for field in (
        "geolocation_data_description",
        "processing_operations",
        "duration_description",
        "notice_reference",
        "notice_version_reference",
        "notice_delivery_mechanism",
        "notice_content_analysis",
        "third_party_disclosure_description",
        "value_added_service_description",
        "third_party_recipient_description",
    ):
        data[field] = "Descripción documentada"
    for field in (
        "information_clear",
        "information_sufficient",
        "information_timely",
        "data_types_disclosed",
        "purpose_disclosed",
        "duration_disclosed",
        "third_party_information_disclosed",
    ):
        data[field] = {"answer": "si", "rationale": "Revisión documentada"}
    return data


@pytest.fixture
def geolocation_controls(negative_controls):
    from copy import deepcopy

    controls = deepcopy(negative_controls)
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "geolocalizacion":
            declaration.update(
                answer="si",
                rationale="Datos documentados",
                data_category_codes=["id"],
                data_subject_codes=["clientes"],
            )
    controls["special_conditions"]["conditions"] = [
        {
            "regime_id": "geolocalizacion_art16sexies",
            "authorization_route": "regla_especifica",
            "data_category_codes": ["id"],
            "data_subject_codes": ["clientes"],
            "legal_reference": "art16sexies",
            "documentary_analysis": "Aviso documentado",
            "evidence": [{"evidence_type": "aviso", "reference": "Registro aviso"}],
        }
    ]
    return controls


@pytest.fixture
def geolocation_context(
    complete_geolocation, complete_lia_context, geolocation_controls
):
    from app.services.special_conditions import bind_special_conditions_v6

    rat = complete_lia_context[1]
    special = bind_special_conditions_v6(
        geolocation_controls["special_conditions"],
        rat,
        "consentimiento_art12",
        None,
        None,
        None,
        None,
        None,
        None,
        complete_geolocation,
    ).model_dump(mode="json")
    return complete_geolocation, rat, special


@pytest.fixture
def sensitive_exception_context(complete_lia_context, negative_controls):
    from copy import deepcopy

    from app.services.special_conditions import bind_special_conditions_v10

    CONTEXT_TEXTS = [
        "context_reference",
        "purpose_description",
        "right_description",
        "right_basis_reference",
        "holder_connection_analysis",
        "forum_description",
        "proceeding_reference",
        "processing_operations",
        "necessity_analysis",
        "data_minimization_analysis",
        "safeguards_analysis",
    ]
    RESPONSES = [
        "related_to_right",
        "necessary_for_route",
        "within_forum_scope",
        "principles_addressed",
    ]
    rat = deepcopy(complete_lia_context[1])
    rat["data_categories"][0]["is_sensitive"] = True
    rat["special_regimes"]["has_sensitive_data"] = True
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    context = {name: "Analisis documental" for name in CONTEXT_TEXTS}
    context.update(
        context_reference="Caso documental",
        purpose_description=rat["purpose"],
        route="defensa_derecho",
        right_holder="responsable",
        forum_type="organo_administrativo",
        proceeding_stage="en_curso",
        right_basis_reference="Contrato documentado",
        evidence=[{"evidence_type": "caso", "reference": "Registro del caso"}],
    )
    for name in RESPONSES:
        context[name.split(".")[-1]] = {
            "answer": "si",
            "rationale": "Comprobacion documentada",
        }
    document = {
        "exception_basis": "defensa_derechos_art16d",
        "context": context,
        "sensitive_data_description": "Categoria sensible",
        "scope": deepcopy(scope),
        "exception_application_analysis": "Necesidad especifica para el derecho",
        "exception_conditions_met": {
            "answer": "si",
            "rationale": "Aplicacion documentada",
        },
        "evidence": [{"evidence_type": "analisis", "reference": "Registro propio"}],
    }
    draft = deepcopy(negative_controls["special_conditions"])
    next(
        d for d in draft["declarations"] if d["question_id"] == "datos_sensibles"
    ).update(answer="si", rationale="Alcance sensible", **scope)
    draft["conditions"] = [
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "excepcion_legal",
            "sensitive_condition_id": "defensa_derechos_art16d",
            "uses_consent_assessment": False,
            "legal_reference": "art16(d)",
            "documentary_analysis": "Supuesto documentado",
            "evidence": [
                {"evidence_type": "analisis", "reference": "Registro de condicion"}
            ],
            **scope,
        }
    ]
    special = bind_special_conditions_v10(
        draft, rat, "contrato_precontractual_art13c", *([None] * 10), document, None
    ).model_dump(mode="json")
    return document, rat, special


@pytest.fixture
def biometric_exception_context(sensitive_exception_context):
    from copy import deepcopy

    from app.services.special_conditions import bind_special_conditions_v10

    OWN_TEXTS = [
        "biometric_data_description",
        "unique_identification_analysis",
        "exception_application_analysis",
        "sensitive_context_connection_analysis",
        "systems_coverage_analysis",
    ]
    SYSTEM_TEXTS = [
        "system_reference",
        "system_name",
        "system_description",
        "specific_purpose",
        "purpose_alignment_analysis",
        "use_period_description",
        "retention_alignment_analysis",
        "rights_exercise_description",
        "rights_contact_channel",
        "information_reference",
    ]
    sensitive, rat, special = sensitive_exception_context
    scope = deepcopy(sensitive["scope"])
    document = {field: "Analisis biometrico documental" for field in OWN_TEXTS}
    context = deepcopy(sensitive["context"])
    context["processing_operations"] = "Identificacion unica para el caso"
    system = {field: "Informacion documentada" for field in SYSTEM_TEXTS}
    system["system_reference"] = "Sistema 1"
    system["specific_purpose"] = "Identificacion unica necesaria para el derecho"
    system["evidence"] = [{"evidence_type": "aviso", "reference": "Aviso de sistema"}]
    for name in (
        "system_identification_disclosed",
        "purpose_disclosed",
        "use_period_disclosed",
        "rights_exercise_disclosed",
    ):
        system[name] = {"answer": "si", "rationale": "Informacion documentada"}
    document.update(
        exception_basis="defensa_derechos_art16bis_d",
        context=context,
        scope=scope,
        systems=[system],
        evidence=[{"evidence_type": "analisis", "reference": "Referencia propia"}],
    )
    for name in (
        "exception_conditions_met",
        "unique_identification_confirmed",
        "all_systems_documented",
    ):
        document[name] = {"answer": "si", "rationale": "Comprobacion documentada"}
    draft = deepcopy(special)
    draft.pop("context_binding")
    next(
        d
        for d in draft["declarations"]
        if d["question_id"] == "biometricos_identificacion_unica"
    ).update(answer="si", rationale="Identificacion unica", **scope)
    draft["conditions"].append(
        {
            "regime_id": "biometricos_art16ter",
            "authorization_route": "excepcion_legal",
            "uses_consent_assessment": False,
            "legal_reference": "art16ter/art16bis(d)",
            "documentary_analysis": "Remision especifica documentada",
            "evidence": [
                {"evidence_type": "analisis", "reference": "Referencia de condicion"}
            ],
            **scope,
        }
    )
    special = bind_special_conditions_v10(
        draft,
        rat,
        "contrato_precontractual_art13c",
        *([None] * 10),
        sensitive,
        document,
    ).model_dump(mode="json")
    return document, rat, special, sensitive
