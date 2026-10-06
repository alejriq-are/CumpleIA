"""Creación concurrente M3 con contexto RAT, PostgreSQL y RLS reales."""

import asyncio
import uuid

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import delete, select, text, update

from app.db.models import (
    LegalAssessment,
    LegalAssessmentSeries,
    Treatment,
    TreatmentDataCategory,
    TreatmentDataSubject,
    TreatmentPurpose,
)
from app.schemas.licitud import LegalAssessmentDraftCreate, LegalAssessmentDraftUpdate
from app.services import licitud


@pytest.fixture
def complete_payload():
    ids = [
        "consentimiento_libre",
        "consentimiento_informado",
        "consentimiento_especifico_finalidad",
        "consentimiento_previo",
        "voluntad_inequivoca",
        "accion_afirmativa_clara",
        "revocacion_posible",
        "revocacion_medio_equivalente",
        "revocacion_expedita",
        "revocacion_fidedigna",
        "revocacion_gratuita",
        "revocacion_disponible_permanentemente",
        "responsable_puede_acreditar",
    ]
    return {
        "given_by": "titular",
        "grant_method": "electronico",
        "answers": [{"question_id": q, "answer": "si"} for q in ids]
        + [{"question_id": "contexto_contrato_servicio", "answer": "no"}],
    }


@pytest_asyncio.fixture
async def rat_m3(_session_factory, org_a_id, negative_controls):
    treatment_id, purpose_id = uuid.uuid4(), uuid.uuid4()
    async with _session_factory() as db:
        db.add(
            Treatment(
                id=treatment_id,
                organization_id=org_a_id,
                name="API M3",
                organization_role="responsable",
                retention_rule="5 años",
                has_automated_decisions=False,
            )
        )
        await db.flush()
        common = {"treatment_id": treatment_id, "organization_id": org_a_id}
        db.add_all(
            [
                TreatmentPurpose(
                    **common, id=purpose_id, purpose="Gestión de clientes"
                ),
                TreatmentDataCategory(
                    **common,
                    category_code="id",
                    category_name="Identidad",
                    is_sensitive=False,
                ),
                TreatmentDataSubject(
                    **common,
                    category_code="clientes",
                    category_name="Clientes",
                    includes_children=False,
                    includes_adolescents=False,
                    is_vulnerable_group=False,
                ),
            ]
        )
        await db.commit()
    yield treatment_id, {
        **negative_controls,
        "purpose_id": str(purpose_id),
        "scope": {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]},
        "legal_basis": "consentimiento_art12",
        "justification": "Finalidad documentada",
    }
    async with _session_factory() as db:
        await db.execute(
            delete(LegalAssessment).where(LegalAssessment.treatment_id == treatment_id)
        )
        await db.execute(
            delete(LegalAssessmentSeries).where(
                LegalAssessmentSeries.treatment_id == treatment_id
            )
        )
        await db.execute(delete(Treatment).where(Treatment.id == treatment_id))
        await db.commit()


@pytest.mark.parametrize(
    "existing_series,release",
    [
        (False, "commit"),
        (False, "rollback"),
        (True, "commit"),
        (True, "rollback"),
        (True, "confirm_commit"),
    ],
)
async def test_creacion_concurrente_serie_y_versiones(
    rat_m3,
    complete_payload,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    existing_series,
    release,
):
    treatment_id, data = rat_m3
    payload = LegalAssessmentDraftCreate.model_validate(
        {**data, "consent_assessment": complete_payload}
    )

    async def authenticate(db):
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
            {"sub": str(auth_a_id)},
        )
        await db.execute(text("SET LOCAL statement_timeout = '5000ms'"))

    if existing_series:
        async with _app_session_factory() as setup:
            await authenticate(setup)
            initial = await licitud.create_legal_assessment_draft_v1(
                setup, org_a_id, treatment_id, profile_a_id, payload
            )
            await licitud.confirm_legal_assessment_v1(
                setup, org_a_id, treatment_id, initial.id, profile_a_id
            )
            await setup.commit()

    contender = None
    try:
        async with _app_session_factory() as first, _app_session_factory() as second:
            await authenticate(first)
            await authenticate(second)
            second_pid = (
                await second.execute(text("SELECT pg_backend_pid()"))
            ).scalar_one()
            # Una serie ya presente en el identity map no debe conservar un
            # contador anterior a la transacción que acaba de liberar el lock.
            cached = None
            if existing_series:
                cached = (
                    await second.execute(
                        select(LegalAssessmentSeries).where(
                            LegalAssessmentSeries.treatment_id == treatment_id
                        )
                    )
                ).scalar_one()
                assert cached.next_version == 2
            created = await licitud.create_legal_assessment_draft_v1(
                first, org_a_id, treatment_id, profile_a_id, payload
            )
            if release == "confirm_commit":
                await licitud.confirm_legal_assessment_v1(
                    first, org_a_id, treatment_id, created.id, profile_a_id
                )

            async def second_create():
                try:
                    draft = await licitud.create_legal_assessment_draft_v1(
                        second, org_a_id, treatment_id, profile_a_id, payload
                    )
                    result = (201, draft.version)
                    await second.commit()
                    return result
                except HTTPException as exc:
                    await second.rollback()
                    return (exc.status_code, None)

            contender = asyncio.create_task(second_create())

            async def wait_for_lock():
                while True:
                    blockers = (
                        await first.execute(
                            text("SELECT pg_blocking_pids(:pid)"), {"pid": second_pid}
                        )
                    ).scalar_one()
                    if blockers:
                        return
                    if contender.done():
                        await contender
                        raise AssertionError("La segunda creación no esperó el bloqueo")
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(wait_for_lock(), timeout=3)
            if release == "rollback":
                await first.rollback()
            else:
                await first.commit()
            expected_version = 2 if existing_series else 1
            expected = (
                (201, 3)
                if release == "confirm_commit"
                else (201, expected_version) if release == "rollback" else (409, None)
            )
            assert await asyncio.wait_for(contender, timeout=3) == expected
            if cached is not None and release == "confirm_commit":
                assert cached.next_version == 4

        async with _app_session_factory() as check:
            await authenticate(check)
            series = (
                (
                    await check.execute(
                        select(LegalAssessmentSeries).where(
                            LegalAssessmentSeries.treatment_id == treatment_id
                        )
                    )
                )
                .scalars()
                .all()
            )
            assessments = (
                (
                    await check.execute(
                        select(LegalAssessment)
                        .where(LegalAssessment.treatment_id == treatment_id)
                        .order_by(LegalAssessment.version)
                    )
                )
                .scalars()
                .all()
            )
            assert len(series) == 1
            assert sum(row.status == "borrador" for row in assessments) == 1
            expected_versions = (
                [1, 2, 3]
                if release == "confirm_commit"
                else [1, 2] if existing_series else [1]
            )
            assert [row.version for row in assessments] == expected_versions
            assert series[0].next_version == expected_versions[-1] + 1
            assert sum(row.status == "confirmado" for row in assessments) == (
                1 if existing_series else 0
            )
            await check.rollback()
    finally:
        if contender is not None and not contender.done():
            contender.cancel()
            await asyncio.gather(contender, return_exceptions=True)


@pytest.mark.parametrize(
    "action,expected",
    [
        ("confirm_commit", 409),
        ("confirm_rollback", 200),
        ("document_update", 409),
        ("rat_update", 409),
    ],
)
@pytest.mark.parametrize(
    "changed_document", ["sensitive_consent_assessment", "geolocation_assessment"]
)
async def test_confirmation_concurrent_real_rat_joint(
    rat_m3,
    complete_payload,
    complete_geolocation,
    geolocation_controls,
    _session_factory,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    action,
    expected,
    changed_document,
):
    from copy import deepcopy

    treatment_id, data = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    controls = deepcopy(geolocation_controls)
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(answer="si", rationale="Declaración expresa", **scope)
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "legal_reference": "art16",
            "documentary_analysis": "Declaración expresa",
            "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
            **scope,
        }
    )
    sensitive = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Categoría sensible",
        "processing_operations": "Operaciones",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Declaración expresa",
        "technology_equivalence_analysis": "Equivalencia",
        "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
    }
    for field in [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ]:
        sensitive[field] = {"answer": "si", "rationale": "Comprobación documentada"}
    payload = LegalAssessmentDraftCreate.model_validate(
        {
            **data,
            **controls,
            "consent_assessment": complete_payload,
            "sensitive_consent_assessment": sensitive,
            "geolocation_assessment": complete_geolocation,
        }
    )

    async def authenticate(db):
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
            {"sub": str(auth_a_id)},
        )
        await db.execute(text("SET LOCAL statement_timeout = '5000ms'"))

    async with _app_session_factory() as setup:
        await authenticate(setup)
        previous = await licitud.create_legal_assessment_draft_v1(
            setup, org_a_id, treatment_id, profile_a_id, payload
        )
        await licitud.confirm_legal_assessment_v1(
            setup, org_a_id, treatment_id, previous.id, profile_a_id
        )
        await setup.commit()
        previous_id = previous.id
        previous_snapshot = deepcopy(previous.rat_context_snapshot)
        previous_hash = previous.rat_context_hash
        previous_confirmed_at = previous.confirmed_at
    async with _app_session_factory() as setup:
        await authenticate(setup)
        draft = await licitud.create_legal_assessment_draft_v1(
            setup, org_a_id, treatment_id, profile_a_id, payload
        )
        await setup.commit()
        draft_id, series_id = draft.id, draft.series_id

    contender = None
    try:
        async with _app_session_factory() as first, _app_session_factory() as second:
            await authenticate(first)
            await authenticate(second)
            # Prime identity map with the original draft; confirmation must refresh it.
            cached = (
                await second.execute(
                    select(LegalAssessment).where(LegalAssessment.id == draft_id)
                )
            ).scalar_one()
            assert cached.status == "borrador"
            second_pid = (
                await second.execute(text("SELECT pg_backend_pid()"))
            ).scalar_one()
            if action == "document_update":
                document = deepcopy(getattr(draft, changed_document))
                response = (
                    "proof_available"
                    if changed_document == "sensitive_consent_assessment"
                    else "information_clear"
                )
                document[response]["answer"] = "pendiente"
                await licitud.update_legal_assessment_draft_v1(
                    first,
                    org_a_id,
                    treatment_id,
                    draft_id,
                    profile_a_id,
                    LegalAssessmentDraftUpdate.model_validate(
                        {changed_document: document}
                    ),
                )
            elif action == "rat_update":
                await first.execute(
                    select(LegalAssessmentSeries)
                    .where(LegalAssessmentSeries.id == series_id)
                    .with_for_update()
                )
                await first.execute(
                    update(TreatmentDataCategory)
                    .where(TreatmentDataCategory.treatment_id == treatment_id)
                    .values(is_sensitive=False)
                )
            else:
                await licitud.confirm_legal_assessment_v1(
                    first, org_a_id, treatment_id, draft_id, profile_a_id
                )

            async def second_confirm():
                try:
                    await licitud.confirm_legal_assessment_v1(
                        second, org_a_id, treatment_id, draft_id, profile_a_id
                    )
                    await second.commit()
                    return 200
                except HTTPException as exc:
                    await second.rollback()
                    return exc.status_code

            contender = asyncio.create_task(second_confirm())

            async def observe_lock():
                while True:
                    blockers = (
                        await first.execute(
                            text("SELECT pg_blocking_pids(:pid)"), {"pid": second_pid}
                        )
                    ).scalar_one()
                    if blockers:
                        return
                    if contender.done():
                        raise AssertionError(
                            "La segunda confirmación no esperó el bloqueo"
                        )
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(observe_lock(), timeout=3)
            assert not contender.done()
            if action == "confirm_rollback":
                await first.rollback()
            else:
                await first.commit()
            assert await asyncio.wait_for(contender, timeout=3) == expected
        async with _app_session_factory() as check:
            await authenticate(check)
            rows = (
                (
                    await check.execute(
                        select(LegalAssessment).where(
                            LegalAssessment.treatment_id == treatment_id
                        )
                    )
                )
                .scalars()
                .all()
            )
            by_id = {row.id: row for row in rows}
            assert sum(row.status == "confirmado" for row in rows) == 1
            old, current = by_id[previous_id], by_id[draft_id]
            assert (
                old.rat_context_snapshot == previous_snapshot
                and old.rat_context_hash == previous_hash
            )
            assert old.confirmed_at == previous_confirmed_at
            if action in ("document_update", "rat_update"):
                assert current.status == "borrador" and old.status == "confirmado"
                assert old.replaced_at is None and old.replaced_by_assessment_id is None
            else:
                assert current.status == "confirmado" and old.status == "reemplazado"
                assert old.replaced_by_assessment_id == draft_id
            if action == "rat_update":
                category = (
                    await check.execute(
                        select(TreatmentDataCategory).where(
                            TreatmentDataCategory.treatment_id == treatment_id
                        )
                    )
                ).scalar_one()
                assert not category.is_sensitive
                assert current.rat_context_snapshot["data_categories"][0][
                    "is_sensitive"
                ]
            if action == "document_update":
                response = (
                    "proof_available"
                    if changed_document == "sensitive_consent_assessment"
                    else "information_clear"
                )
                assert (
                    getattr(current, changed_document)[response]["answer"]
                    == "pendiente"
                )
    finally:
        if contender is not None and not contender.done():
            contender.cancel()
            await asyncio.gather(contender, return_exceptions=True)


@pytest.mark.parametrize(
    "action,expected",
    [
        ("confirm_commit", 409),
        ("confirm_rollback", 200),
        ("document_update", 409),
        ("rat_update", 409),
    ],
)
@pytest.mark.parametrize(
    "changed_document",
    ["sensitive_consent_assessment", "geolocation_assessment", "health_assessment"],
)
async def test_health_confirmation_concurrent_real_rat_joint(
    rat_m3,
    complete_payload,
    complete_geolocation,
    geolocation_controls,
    _session_factory,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    action,
    expected,
    changed_document,
):
    from copy import deepcopy

    treatment_id, data = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    controls = deepcopy(geolocation_controls)
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(answer="si", rationale="Declaración expresa", **scope)
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "legal_reference": "art16",
            "documentary_analysis": "Declaración expresa",
            "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
            **scope,
        }
    )
    sensitive = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Categoría sensible",
        "processing_operations": "Operaciones",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Declaración expresa",
        "technology_equivalence_analysis": "Equivalencia",
        "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
    }
    for field in [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ]:
        sensitive[field] = {"answer": "si", "rationale": "Comprobación documentada"}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "salud_perfil_biologico":
            declaration.update(
                answer="si", rationale="Finalidad sanitaria documentada", **scope
            )
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "salud_perfil_biologico_art16bis",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "art16bis",
            "documentary_analysis": "Finalidad sanitaria documentada",
            "evidence": [
                {"evidence_type": "declaracion", "reference": "Registro sanitario"}
            ],
            **scope,
        }
    )
    health = {
        "purpose_description": "Gestión de clientes",
        "health_data_description": "Datos de salud",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "route": "consentimiento_expreso",
        "sanitary_law_references": [
            {
                "norm_name": "Norma por revisar",
                "provision": "Artículo por identificar",
                "official_source_url": "https://example.test/norma",
                "applicability_analysis": "Aplicabilidad documentada",
            }
        ],
        "sanitary_purpose_analysis": "Finalidad documentada",
        "sanitary_purpose_covered": {
            "answer": "si",
            "rationale": "Cobertura documentada",
        },
        "collection_contexts": ["otro"],
        "collection_context_analysis": "Contexto de recolección documentado",
        "includes_data_cession": {"answer": "no", "rationale": "Sin cesión"},
        "includes_identifiable_biological_samples": {
            "answer": "no",
            "rationale": "Sin muestras",
        },
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
    }
    payload = LegalAssessmentDraftCreate.model_validate(
        {
            **data,
            **controls,
            "consent_assessment": complete_payload,
            "sensitive_consent_assessment": sensitive,
            "geolocation_assessment": complete_geolocation,
            "health_assessment": health,
        }
    )

    async def authenticate(db):
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
            {"sub": str(auth_a_id)},
        )
        await db.execute(text("SET LOCAL statement_timeout = '5000ms'"))

    async with _app_session_factory() as setup:
        await authenticate(setup)
        previous = await licitud.create_legal_assessment_draft_v1(
            setup, org_a_id, treatment_id, profile_a_id, payload
        )
        await licitud.confirm_legal_assessment_v1(
            setup, org_a_id, treatment_id, previous.id, profile_a_id
        )
        await setup.commit()
        previous_id = previous.id
        previous_snapshot = deepcopy(previous.rat_context_snapshot)
        previous_hash = previous.rat_context_hash
        previous_confirmed_at = previous.confirmed_at
    async with _app_session_factory() as setup:
        await authenticate(setup)
        draft = await licitud.create_legal_assessment_draft_v1(
            setup, org_a_id, treatment_id, profile_a_id, payload
        )
        await setup.commit()
        draft_id, series_id = draft.id, draft.series_id

    contender = None
    try:
        async with _app_session_factory() as first, _app_session_factory() as second:
            await authenticate(first)
            await authenticate(second)
            # Prime identity map with the original draft; confirmation must refresh it.
            cached = (
                await second.execute(
                    select(LegalAssessment).where(LegalAssessment.id == draft_id)
                )
            ).scalar_one()
            assert cached.status == "borrador"
            second_pid = (
                await second.execute(text("SELECT pg_backend_pid()"))
            ).scalar_one()
            if action == "document_update":
                document = deepcopy(getattr(draft, changed_document))
                response = (
                    "proof_available"
                    if changed_document == "sensitive_consent_assessment"
                    else (
                        "information_clear"
                        if changed_document == "geolocation_assessment"
                        else "sanitary_purpose_covered"
                    )
                )
                document[response]["answer"] = "pendiente"
                await licitud.update_legal_assessment_draft_v1(
                    first,
                    org_a_id,
                    treatment_id,
                    draft_id,
                    profile_a_id,
                    LegalAssessmentDraftUpdate.model_validate(
                        {changed_document: document}
                    ),
                )
            elif action == "rat_update":
                await first.execute(
                    select(LegalAssessmentSeries)
                    .where(LegalAssessmentSeries.id == series_id)
                    .with_for_update()
                )
                await first.execute(
                    update(TreatmentDataCategory)
                    .where(TreatmentDataCategory.treatment_id == treatment_id)
                    .values(is_sensitive=False)
                )
            else:
                await licitud.confirm_legal_assessment_v1(
                    first, org_a_id, treatment_id, draft_id, profile_a_id
                )

            async def second_confirm():
                try:
                    await licitud.confirm_legal_assessment_v1(
                        second, org_a_id, treatment_id, draft_id, profile_a_id
                    )
                    await second.commit()
                    return 200
                except HTTPException as exc:
                    await second.rollback()
                    return exc.status_code

            contender = asyncio.create_task(second_confirm())

            async def observe_lock():
                while True:
                    blockers = (
                        await first.execute(
                            text("SELECT pg_blocking_pids(:pid)"), {"pid": second_pid}
                        )
                    ).scalar_one()
                    if blockers:
                        return
                    if contender.done():
                        raise AssertionError(
                            "La segunda confirmación no esperó el bloqueo"
                        )
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(observe_lock(), timeout=3)
            assert not contender.done()
            if action == "confirm_rollback":
                await first.rollback()
            else:
                await first.commit()
            assert await asyncio.wait_for(contender, timeout=3) == expected
        async with _app_session_factory() as check:
            await authenticate(check)
            rows = (
                (
                    await check.execute(
                        select(LegalAssessment).where(
                            LegalAssessment.treatment_id == treatment_id
                        )
                    )
                )
                .scalars()
                .all()
            )
            by_id = {row.id: row for row in rows}
            assert sum(row.status == "confirmado" for row in rows) == 1
            old, current = by_id[previous_id], by_id[draft_id]
            assert (
                old.rat_context_snapshot == previous_snapshot
                and old.rat_context_hash == previous_hash
            )
            assert old.confirmed_at == previous_confirmed_at
            if action in ("document_update", "rat_update"):
                assert current.status == "borrador" and old.status == "confirmado"
                assert old.replaced_at is None and old.replaced_by_assessment_id is None
            else:
                assert current.status == "confirmado" and old.status == "reemplazado"
                assert old.replaced_by_assessment_id == draft_id
            if action == "rat_update":
                category = (
                    await check.execute(
                        select(TreatmentDataCategory).where(
                            TreatmentDataCategory.treatment_id == treatment_id
                        )
                    )
                ).scalar_one()
                assert not category.is_sensitive
                assert current.rat_context_snapshot["data_categories"][0][
                    "is_sensitive"
                ]
            if action == "document_update":
                response = (
                    "proof_available"
                    if changed_document == "sensitive_consent_assessment"
                    else (
                        "information_clear"
                        if changed_document == "geolocation_assessment"
                        else "sanitary_purpose_covered"
                    )
                )
                assert (
                    getattr(current, changed_document)[response]["answer"]
                    == "pendiente"
                )
    finally:
        if contender is not None and not contender.done():
            contender.cancel()
            await asyncio.gather(contender, return_exceptions=True)


@pytest.mark.parametrize(
    "action,expected",
    [
        ("confirm_commit", 409),
        ("confirm_rollback", 200),
        ("document_update", 409),
        ("rat_update", 409),
    ],
)
@pytest.mark.parametrize(
    "changed_document",
    [
        "sensitive_consent_assessment",
        "geolocation_assessment",
        "health_assessment",
        "biometric_assessment",
    ],
)
async def test_biometric_confirmation_concurrent_real_rat_joint(
    rat_m3,
    complete_payload,
    complete_geolocation,
    geolocation_controls,
    _session_factory,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    action,
    expected,
    changed_document,
):
    from copy import deepcopy

    treatment_id, data = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    controls = deepcopy(geolocation_controls)
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(answer="si", rationale="Declaración expresa", **scope)
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "legal_reference": "art16",
            "documentary_analysis": "Declaración expresa",
            "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
            **scope,
        }
    )
    sensitive = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Categoría sensible",
        "processing_operations": "Operaciones",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Declaración expresa",
        "technology_equivalence_analysis": "Equivalencia",
        "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
    }
    for field in [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ]:
        sensitive[field] = {"answer": "si", "rationale": "Comprobación documentada"}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "salud_perfil_biologico":
            declaration.update(
                answer="si", rationale="Finalidad sanitaria documentada", **scope
            )
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "salud_perfil_biologico_art16bis",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "art16bis",
            "documentary_analysis": "Finalidad sanitaria documentada",
            "evidence": [
                {"evidence_type": "declaracion", "reference": "Registro sanitario"}
            ],
            **scope,
        }
    )
    health = {
        "purpose_description": "Gestión de clientes",
        "health_data_description": "Datos de salud",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "route": "consentimiento_expreso",
        "sanitary_law_references": [
            {
                "norm_name": "Norma por revisar",
                "provision": "Artículo por identificar",
                "official_source_url": "https://example.test/norma",
                "applicability_analysis": "Aplicabilidad documentada",
            }
        ],
        "sanitary_purpose_analysis": "Finalidad documentada",
        "sanitary_purpose_covered": {
            "answer": "si",
            "rationale": "Cobertura documentada",
        },
        "collection_contexts": ["otro"],
        "collection_context_analysis": "Contexto de recolección documentado",
        "includes_data_cession": {"answer": "no", "rationale": "Sin cesión"},
        "includes_identifiable_biological_samples": {
            "answer": "no",
            "rationale": "Sin muestras",
        },
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
    }
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "biometricos_identificacion_unica":
            declaration.update(
                answer="si", rationale="Identificación biométrica", **scope
            )
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "biometricos_art16ter",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "art16ter",
            "documentary_analysis": "Información documentada",
            "evidence": [{"evidence_type": "aviso", "reference": "Aviso"}],
            **scope,
        }
    )
    system = {
        field: "Descripción documentada"
        for field in [
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
    }
    for field in [
        "system_identification_disclosed",
        "purpose_disclosed",
        "use_period_disclosed",
        "rights_exercise_disclosed",
    ]:
        system[field] = {"answer": "si", "rationale": "Información proporcionada"}
    system["evidence"] = [{"evidence_type": "aviso", "reference": "Aviso"}]
    biometric = {
        "purpose_description": "Gestión de clientes",
        "biometric_data_description": "Categoría biométrica",
        "processing_operations": "Identificación",
        "scope": scope,
        "route": "consentimiento_expreso",
        "unique_identification_analysis": "Identificación única documentada",
        "unique_identification_confirmed": {
            "answer": "si",
            "rationale": "Identificación",
        },
        "systems_coverage_analysis": "Sistema documentado",
        "all_systems_documented": {
            "answer": "si",
            "rationale": "Cobertura documentada",
        },
        "systems": [system],
        "evidence": [{"evidence_type": "aviso", "reference": "Aviso"}],
    }
    payload = LegalAssessmentDraftCreate.model_validate(
        {
            **data,
            **controls,
            "consent_assessment": complete_payload,
            "sensitive_consent_assessment": sensitive,
            "geolocation_assessment": complete_geolocation,
            "health_assessment": health,
            "biometric_assessment": biometric,
        }
    )

    async def authenticate(db):
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
            {"sub": str(auth_a_id)},
        )
        await db.execute(text("SET LOCAL statement_timeout = '5000ms'"))

    async with _app_session_factory() as setup:
        await authenticate(setup)
        previous = await licitud.create_legal_assessment_draft_v1(
            setup, org_a_id, treatment_id, profile_a_id, payload
        )
        await licitud.confirm_legal_assessment_v1(
            setup, org_a_id, treatment_id, previous.id, profile_a_id
        )
        await setup.commit()
        previous_id = previous.id
        previous_snapshot = deepcopy(previous.rat_context_snapshot)
        previous_hash = previous.rat_context_hash
        previous_confirmed_at = previous.confirmed_at
        historical_documents = {
            name: deepcopy(getattr(previous, name))
            for name in (
                "consent_assessment",
                "sensitive_consent_assessment",
                "geolocation_assessment",
                "health_assessment",
                "biometric_assessment",
                "special_conditions",
                "eipd_screening",
            )
        }
    async with _app_session_factory() as setup:
        await authenticate(setup)
        draft = await licitud.create_legal_assessment_draft_v1(
            setup, org_a_id, treatment_id, profile_a_id, payload
        )
        await setup.commit()
        draft_id, series_id = draft.id, draft.series_id

    contender = None
    try:
        async with _app_session_factory() as first, _app_session_factory() as second:
            await authenticate(first)
            await authenticate(second)
            # Prime identity map with the original draft; confirmation must refresh it.
            cached = (
                await second.execute(
                    select(LegalAssessment).where(LegalAssessment.id == draft_id)
                )
            ).scalar_one()
            assert cached.status == "borrador"
            second_pid = (
                await second.execute(text("SELECT pg_backend_pid()"))
            ).scalar_one()
            if action == "document_update":
                document = deepcopy(getattr(draft, changed_document))
                response = (
                    "proof_available"
                    if changed_document == "sensitive_consent_assessment"
                    else (
                        "information_clear"
                        if changed_document == "geolocation_assessment"
                        else "sanitary_purpose_covered"
                    )
                )
                if changed_document == "biometric_assessment":
                    document["systems"][0]["purpose_disclosed"]["answer"] = "pendiente"
                else:
                    document[response]["answer"] = "pendiente"
                await licitud.update_legal_assessment_draft_v1(
                    first,
                    org_a_id,
                    treatment_id,
                    draft_id,
                    profile_a_id,
                    LegalAssessmentDraftUpdate.model_validate(
                        {changed_document: document}
                    ),
                )
            elif action == "rat_update":
                await first.execute(
                    select(LegalAssessmentSeries)
                    .where(LegalAssessmentSeries.id == series_id)
                    .with_for_update()
                )
                await first.execute(
                    update(TreatmentDataCategory)
                    .where(TreatmentDataCategory.treatment_id == treatment_id)
                    .values(is_sensitive=False)
                )
            else:
                await licitud.confirm_legal_assessment_v1(
                    first, org_a_id, treatment_id, draft_id, profile_a_id
                )

            async def second_confirm():
                try:
                    await licitud.confirm_legal_assessment_v1(
                        second, org_a_id, treatment_id, draft_id, profile_a_id
                    )
                    await second.commit()
                    return 200
                except HTTPException as exc:
                    await second.rollback()
                    return exc.status_code

            contender = asyncio.create_task(second_confirm())

            async def observe_lock():
                while True:
                    blockers = (
                        await first.execute(
                            text("SELECT pg_blocking_pids(:pid)"), {"pid": second_pid}
                        )
                    ).scalar_one()
                    if blockers:
                        return
                    if contender.done():
                        raise AssertionError(
                            "La segunda confirmación no esperó el bloqueo"
                        )
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(observe_lock(), timeout=3)
            assert not contender.done()
            if action == "confirm_rollback":
                await first.rollback()
            else:
                await first.commit()
            assert await asyncio.wait_for(contender, timeout=3) == expected
        async with _app_session_factory() as check:
            await authenticate(check)
            rows = (
                (
                    await check.execute(
                        select(LegalAssessment).where(
                            LegalAssessment.treatment_id == treatment_id
                        )
                    )
                )
                .scalars()
                .all()
            )
            by_id = {row.id: row for row in rows}
            assert sum(row.status == "confirmado" for row in rows) == 1
            old, current = by_id[previous_id], by_id[draft_id]
            assert (
                old.rat_context_snapshot == previous_snapshot
                and old.rat_context_hash == previous_hash
            )
            assert old.confirmed_at == previous_confirmed_at
            assert {
                name: getattr(old, name) for name in historical_documents
            } == historical_documents
            if action in ("document_update", "rat_update"):
                assert current.status == "borrador" and old.status == "confirmado"
                assert old.replaced_at is None and old.replaced_by_assessment_id is None
            else:
                assert current.status == "confirmado" and old.status == "reemplazado"
                assert old.replaced_by_assessment_id == draft_id
            if action == "rat_update":
                category = (
                    await check.execute(
                        select(TreatmentDataCategory).where(
                            TreatmentDataCategory.treatment_id == treatment_id
                        )
                    )
                ).scalar_one()
                assert not category.is_sensitive
                assert current.rat_context_snapshot["data_categories"][0][
                    "is_sensitive"
                ]
            if action == "document_update":
                response = (
                    "proof_available"
                    if changed_document == "sensitive_consent_assessment"
                    else (
                        "information_clear"
                        if changed_document == "geolocation_assessment"
                        else "sanitary_purpose_covered"
                    )
                )
                assert (
                    getattr(current, changed_document)["systems"][0][
                        "purpose_disclosed"
                    ]["answer"]
                    if changed_document == "biometric_assessment"
                    else getattr(current, changed_document)[response]["answer"]
                ) == "pendiente"
    finally:
        if contender is not None and not contender.done():
            contender.cancel()
            await asyncio.gather(contender, return_exceptions=True)
