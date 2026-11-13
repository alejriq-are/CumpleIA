import asyncio
import uuid
from copy import deepcopy
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy import delete, select, text

from app.db.models import LegalAssessment, LegalAssessmentSeries, Treatment
from app.schemas.licitud import (
    LegalAssessmentDraftCreate,
    LegalAssessmentDraftUpdate,
    RatCanonicalContextV1,
    RatContextSnapshotV1,
)
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


@pytest.fixture
def confirmation(monkeypatch, complete_payload, negative_controls):
    org, treatment, actor, series_id = (uuid.uuid4() for _ in range(4))
    data = {
        "purpose": "Clientes",
        "organization_role": "responsable",
        "data_categories": [
            {"category_code": "id", "category_name": "Identidad", "is_sensitive": False}
        ],
        "data_subjects": [
            {
                "category_code": "clientes",
                "category_name": "Clientes",
                "includes_children": False,
                "includes_adolescents": False,
                "is_vulnerable_group": False,
            }
        ],
        "data_sources": [],
        "retention": {"retention_rule": "5 años"},
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
    canonical = RatCanonicalContextV1.model_validate(data)
    snapshot_data = deepcopy(data)
    snapshot_data["data_categories"][0]["notes"] = None
    snapshot_data["data_subjects"][0]["notes"] = None
    snapshot_data["retention"]["deletion_method"] = None
    snapshot = RatContextSnapshotV1.model_validate(snapshot_data)
    bundle = licitud.RatContextBundleV1(canonical, snapshot)
    draft = LegalAssessment(
        id=uuid.uuid4(),
        series_id=series_id,
        organization_id=org,
        treatment_id=treatment,
        version=2,
        status="borrador",
        legal_basis="consentimiento_art12",
        justification="Finalidad documentada",
        consent_assessment=complete_payload,
        schema_version=1,
        rat_context_schema_version=1,
        purpose_snapshot="Clientes",
        rat_context_hash=licitud.build_rat_context_hash_v1(canonical),
        rat_context_snapshot=snapshot.model_dump(mode="json"),
    )
    from app.services.eipd import bind_eipd_screening_v2
    from app.services.special_conditions import bind_special_conditions_v1

    draft.special_conditions = bind_special_conditions_v1(
        negative_controls["special_conditions"],
        snapshot,
        draft.legal_basis,
        draft.consent_assessment,
        None,
    ).model_dump(mode="json")
    draft.eipd_screening = bind_eipd_screening_v2(
        negative_controls["eipd_screening"], snapshot, None, draft.special_conditions
    ).model_dump(mode="json")
    series = LegalAssessmentSeries(
        id=series_id,
        organization_id=org,
        treatment_id=treatment,
        purpose_key=licitud.build_purpose_key_v1("Clientes"),
        next_version=3,
    )
    previous = LegalAssessment(
        id=uuid.uuid4(),
        series_id=series_id,
        organization_id=org,
        treatment_id=treatment,
        status="confirmado",
        confirmed_at=datetime.now(UTC),
        confirmed_by=actor,
    )
    db = AsyncMock()
    results = []
    for value in (draft, series, draft, previous):
        result = MagicMock()
        result.scalar_one_or_none.return_value = value
        results.append(result)
    db.execute.side_effect = results
    builder = AsyncMock(return_value=bundle)
    monkeypatch.setattr(licitud, "build_rat_context_bundle_from_m2_v1", builder)
    return db, org, treatment, actor, draft, series, previous, bundle, results, builder


async def run_confirm(state):
    db, org, treatment, actor, draft, *_ = state
    return await licitud.confirm_legal_assessment_v1(
        db, org, treatment, draft.id, actor
    )


async def test_confirm_reemplaza_en_orden_sin_commit(confirmation):
    db, org, treatment, actor, draft, series, previous, bundle, _, builder = (
        confirmation
    )
    original_snapshot = deepcopy(draft.rat_context_snapshot)
    observed = []

    async def flush():
        observed.append((previous.status, draft.status))

    db.flush.side_effect = flush
    result = await run_confirm(confirmation)
    assert result is draft
    assert observed == [("reemplazado", "borrador"), ("reemplazado", "confirmado")]
    assert previous.replaced_by_assessment_id == draft.id
    assert previous.confirmed_by == actor
    assert draft.confirmed_by == actor
    assert previous.replaced_at == draft.confirmed_at
    assert draft.rat_context_snapshot == original_snapshot
    assert series.next_version == 3
    db.commit.assert_not_awaited()
    db.rollback.assert_not_awaited()
    args = builder.call_args
    assert args.args[:3] == (db, org, treatment)
    queries = [str(call.args[0]) for call in db.execute.call_args_list]
    assert "FOR UPDATE" in queries[1]
    assert all("organization_id" in q and "treatment_id" in q for q in queries)
    assert (
        db.execute.call_args_list[2]
        .args[0]
        .get_execution_options()["populate_existing"]
    )


async def test_confirm_sin_anterior(confirmation):
    confirmation[8][-1].scalar_one_or_none.return_value = None
    await run_confirm(confirmation)
    assert confirmation[0].flush.await_count == 1


@pytest.mark.parametrize(
    "field,value,code",
    [
        ("legal_basis", None, 409),
        ("justification", "  ", 400),
        ("schema_version", 2, 409),
        ("rat_context_schema_version", 2, 409),
        ("consent_assessment", None, 400),
        ("consent_assessment", {"schema_version": 2}, 400),
        ("rat_context_hash", "desactualizado", 409),
        ("rat_context_snapshot", {}, 400),
        ("special_conditions", {}, 400),
    ],
)
async def test_confirm_rechaza_sin_mutaciones(confirmation, field, value, code):
    draft, previous = confirmation[4], confirmation[6]
    setattr(draft, field, value)
    with pytest.raises(HTTPException) as exc:
        await run_confirm(confirmation)
    assert exc.value.status_code == code
    assert draft.status == "borrador"
    assert draft.confirmed_at is None
    assert previous.status == "confirmado"
    confirmation[0].flush.assert_not_awaited()


@pytest.mark.parametrize(
    "answer,result", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
async def test_confirm_devuelve_motivos(confirmation, answer, result):
    confirmation[4].consent_assessment["answers"][0]["answer"] = answer
    with pytest.raises(HTTPException) as exc:
        await run_confirm(confirmation)
    assert exc.value.detail["result"] == result
    assert exc.value.detail["issues"][0]["question_id"] == "consentimiento_libre"
    confirmation[9].assert_not_awaited()
    confirmation[0].flush.assert_not_awaited()


async def test_confirm_relee_estado_y_payload_tras_lock(confirmation):
    refreshed = deepcopy(confirmation[4])
    refreshed.status = "confirmado"
    confirmation[8][2].scalar_one_or_none.return_value = refreshed
    with pytest.raises(HTTPException) as exc:
        await run_confirm(confirmation)
    assert exc.value.status_code == 409
    confirmation[9].assert_not_awaited()


@pytest.mark.parametrize("index", [0, 1, 2])
async def test_confirm_inexistente_no_escribe(confirmation, index):
    confirmation[8][index].scalar_one_or_none.return_value = None
    with pytest.raises(HTTPException) as exc:
        await run_confirm(confirmation)
    assert exc.value.status_code == 404
    confirmation[0].flush.assert_not_awaited()


@pytest.mark.parametrize(
    "field",
    [
        "has_sensitive_data",
        "includes_children",
        "includes_adolescents",
        "has_vulnerable_groups",
    ],
)
async def test_confirm_regimen_especial_bloqueado(confirmation, field):
    bundle = confirmation[7]
    setattr(bundle.canonical.special_regimes, field, True)
    setattr(bundle.snapshot.special_regimes, field, True)
    confirmation[4].rat_context_hash = licitud.build_rat_context_hash_v1(
        bundle.canonical
    )
    with pytest.raises(HTTPException) as exc:
        await run_confirm(confirmation)
    assert exc.value.status_code == 409
    confirmation[0].flush.assert_not_awaited()


async def test_confirm_error_flush_se_propaga_sin_commit(confirmation):
    confirmation[0].flush.side_effect = RuntimeError("flush falló")
    with pytest.raises(RuntimeError, match="flush falló"):
        await run_confirm(confirmation)
    confirmation[0].commit.assert_not_awaited()
    confirmation[0].rollback.assert_not_awaited()


def test_consentimiento_borrador_serializa_fecha_y_null(complete_payload):
    complete_payload["evidence"] = [
        {"evidence_type": "registro", "obtained_on": "2026-10-05"}
    ]
    create = LegalAssessmentDraftCreate.model_validate(
        {
            "purpose_id": str(uuid.uuid4()),
            "scope": {},
            "consent_assessment": complete_payload,
        }
    )
    assert (
        create.consent_assessment.model_dump(mode="json")["evidence"][0]["obtained_on"]
        == "2026-10-05"
    )
    update = LegalAssessmentDraftUpdate.model_validate({"consent_assessment": None})
    assert update.model_dump(exclude_unset=True) == {"consent_assessment": None}
    assert (
        LegalAssessmentDraftUpdate.model_validate({}).model_dump(exclude_unset=True)
        == {}
    )


@pytest.mark.parametrize(
    "basis",
    [
        "consentimiento_art12",
        "interes_legitimo_art13d",
        "contrato_precontractual_art13c",
        "obligacion_legal_art13b",
        "defensa_derechos_art13e",
        "obligaciones_economicas_art13a",
    ],
)
@pytest.mark.parametrize("with_geolocation", [False, True, "sensitive", "health"])
async def test_confirm_postgres_reemplazo_y_rollback_real(
    confirmation,
    basis,
    with_geolocation,
    complete_payload,
    complete_geolocation,
    geolocation_controls,
    complete_lia_context,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
    negative_controls,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    monkeypatch,
):
    """RLS e índices reales; el constructor RAT está simulado en este test."""
    if basis == "interes_legitimo_art13d":
        confirmation = configure_lia_confirmation(
            confirmation, complete_lia_context, negative_controls
        )
    if basis == "contrato_precontractual_art13c":
        confirmation = configure_contract_confirmation(
            confirmation, complete_contract, negative_controls
        )
    if basis == "obligacion_legal_art13b":
        confirmation = configure_legal_confirmation(
            confirmation, complete_legal_obligation, negative_controls
        )
    if basis == "defensa_derechos_art13e":
        confirmation = configure_rights_confirmation(
            confirmation, complete_rights_defense, negative_controls
        )
    if basis == "obligaciones_economicas_art13a":
        confirmation = configure_economic_confirmation(
            confirmation, complete_economic_obligations, negative_controls
        )
    if with_geolocation == "health":
        confirmation = configure_health_confirmation(
            confirmation, complete_payload, negative_controls
        )
    elif with_geolocation == "sensitive":
        confirmation = configure_sensitive_confirmation(
            confirmation, complete_payload, negative_controls
        )
    elif with_geolocation:
        confirmation = configure_geolocation_confirmation(
            confirmation, complete_geolocation, geolocation_controls
        )
    draft, series, previous = confirmation[4:7]
    treatment_id, draft_id, previous_id = draft.treatment_id, draft.id, previous.id
    series.purpose_text = "Clientes"
    for row in (series, draft, previous):
        row.organization_id = org_a_id
        row.created_by = profile_a_id
        row.updated_by = profile_a_id
    previous.version = 1
    previous.schema_version = 1
    previous.rat_context_schema_version = 1
    previous.purpose_snapshot = draft.purpose_snapshot
    previous.rat_context_hash = draft.rat_context_hash
    previous.rat_context_snapshot = deepcopy(draft.rat_context_snapshot)
    previous.confirmed_by = profile_a_id
    async with _app_session_factory() as db:
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
            {"sub": str(auth_a_id)},
        )
        db.add(
            Treatment(
                id=treatment_id,
                organization_id=org_a_id,
                name="Test confirmación",
                organization_role="responsable",
            )
        )
        await db.flush()
        db.add(series)
        await db.flush()
        db.add_all([draft, previous])
        await db.flush()
        original_flush = db.flush
        calls = 0

        async def fail_second_flush(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("fallo tras reemplazo")
            return await original_flush(*args, **kwargs)

        with pytest.raises(RuntimeError, match="fallo tras reemplazo"):
            async with db.begin_nested():
                monkeypatch.setattr(db, "flush", fail_second_flush)
                await licitud.confirm_legal_assessment_v1(
                    db, org_a_id, treatment_id, draft_id, profile_a_id
                )
        monkeypatch.setattr(db, "flush", original_flush)
        rows = (
            (
                await db.execute(
                    select(LegalAssessment)
                    .where(LegalAssessment.treatment_id == treatment_id)
                    .execution_options(populate_existing=True)
                )
            )
            .scalars()
            .all()
        )
        by_id = {row.id: row for row in rows}
        assert by_id[draft_id].status == "borrador"
        assert by_id[previous_id].status == "confirmado"
        assert by_id[previous_id].replaced_at is None
        await licitud.confirm_legal_assessment_v1(
            db, org_a_id, treatment_id, draft_id, profile_a_id
        )
        assert by_id[draft_id].status == "confirmado"
        assert by_id[previous_id].status == "reemplazado"
        assert by_id[previous_id].replaced_by_assessment_id == draft_id
        # Test dentro de una transacción de app_user; no conserva filas de prueba.
        await db.rollback()


async def test_update_guarda_consentimiento_json_y_preserva_omision(confirmation):
    db, org, treatment, actor, draft, *_ = confirmation
    draft.consent_assessment["evidence"] = [
        {"evidence_type": "registro", "obtained_on": "2026-10-05"}
    ]
    update = LegalAssessmentDraftUpdate.model_validate(
        {"consent_assessment": draft.consent_assessment}
    )
    await licitud.update_legal_assessment_draft_v1(
        db, org, treatment, draft.id, actor, update
    )
    assert draft.consent_assessment["evidence"][0]["obtained_on"] == "2026-10-05"
    assert draft.status == "borrador"
    db.flush.assert_awaited_once()


async def test_create_guarda_consentimiento_json(confirmation, monkeypatch):
    db, org, treatment, actor, draft, series, _, bundle, *_ = confirmation
    draft.consent_assessment["evidence"] = [
        {"evidence_type": "registro", "obtained_on": "2026-10-05"}
    ]
    payload = LegalAssessmentDraftCreate.model_validate(
        {
            "purpose_id": str(uuid.uuid4()),
            "scope": {
                "data_category_codes": ["id"],
                "data_subject_codes": ["clientes"],
            },
            "legal_basis": "consentimiento_art12",
            "consent_assessment": draft.consent_assessment,
        }
    )
    monkeypatch.setattr(
        licitud,
        "resolve_purpose_by_id_from_m2_v1",
        AsyncMock(return_value=MagicMock(purpose="Clientes")),
    )
    monkeypatch.setattr(
        licitud, "_get_or_create_series_for_update_v1", AsyncMock(return_value=series)
    )
    empty = MagicMock()
    empty.scalar_one_or_none.return_value = None
    db.execute.side_effect = None
    db.execute.return_value = empty
    db.add = MagicMock()
    created = await licitud.create_legal_assessment_draft_v1(
        db, org, treatment, actor, payload
    )
    assert created.consent_assessment["evidence"][0]["obtained_on"] == "2026-10-05"
    assert created.status == "borrador"
    db.add.assert_called_once_with(created)


@pytest.mark.parametrize(
    "first_action,expected_second",
    [
        ("confirm_commit", 409),
        ("confirm_rollback", 200),
        ("update_commit", 400),
    ],
)
@pytest.mark.parametrize(
    "basis",
    [
        "consentimiento_art12",
        "interes_legitimo_art13d",
        "contrato_precontractual_art13c",
        "obligacion_legal_art13b",
        "defensa_derechos_art13e",
        "obligaciones_economicas_art13a",
    ],
)
@pytest.mark.parametrize("with_geolocation", [False, True, "sensitive", "health"])
async def test_concurrencia_real_revalida_tras_bloqueo(
    confirmation,
    basis,
    with_geolocation,
    complete_payload,
    complete_geolocation,
    geolocation_controls,
    complete_lia_context,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
    negative_controls,
    _app_session_factory,
    org_a_id,
    profile_a_id,
    auth_a_id,
    first_action,
    expected_second,
):
    """Dos conexiones PostgreSQL; RAT simulado, filas y locks reales."""
    if with_geolocation and first_action == "update_commit":
        expected_second = 409
    if basis == "interes_legitimo_art13d":
        confirmation = configure_lia_confirmation(
            confirmation, complete_lia_context, negative_controls
        )
    if basis == "contrato_precontractual_art13c":
        confirmation = configure_contract_confirmation(
            confirmation, complete_contract, negative_controls
        )
    if basis == "obligacion_legal_art13b":
        confirmation = configure_legal_confirmation(
            confirmation, complete_legal_obligation, negative_controls
        )
    if basis == "defensa_derechos_art13e":
        confirmation = configure_rights_confirmation(
            confirmation, complete_rights_defense, negative_controls
        )
    if basis == "obligaciones_economicas_art13a":
        confirmation = configure_economic_confirmation(
            confirmation, complete_economic_obligations, negative_controls
        )
    if with_geolocation == "health":
        confirmation = configure_health_confirmation(
            confirmation, complete_payload, negative_controls
        )
    elif with_geolocation == "sensitive":
        confirmation = configure_sensitive_confirmation(
            confirmation, complete_payload, negative_controls
        )
    elif with_geolocation:
        confirmation = configure_geolocation_confirmation(
            confirmation, complete_geolocation, geolocation_controls
        )
    draft, series, previous = confirmation[4:7]
    treatment_id, draft_id, previous_id = draft.treatment_id, draft.id, previous.id
    series.purpose_text = "Clientes"
    for row in (series, draft, previous):
        row.organization_id = org_a_id
        row.created_by = profile_a_id
        row.updated_by = profile_a_id
    previous.version = 1
    previous.schema_version = 1
    previous.rat_context_schema_version = 1
    previous.purpose_snapshot = draft.purpose_snapshot
    previous.rat_context_hash = draft.rat_context_hash
    previous.rat_context_snapshot = deepcopy(draft.rat_context_snapshot)
    previous.confirmed_by = profile_a_id

    async def authenticate(db):
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
            {"sub": str(auth_a_id)},
        )
        await db.execute(text("SET LOCAL statement_timeout = '5000ms'"))

    # Las dos sesiones deben ver las mismas filas comprometidas.
    async with _app_session_factory() as setup:
        await authenticate(setup)
        setup.add(
            Treatment(
                id=treatment_id,
                organization_id=org_a_id,
                name="Test concurrencia M3",
                organization_role="responsable",
            )
        )
        await setup.flush()
        setup.add(series)
        await setup.flush()
        setup.add_all([draft, previous])
        await setup.commit()

    contender = None
    try:
        async with _app_session_factory() as first, _app_session_factory() as second:
            await authenticate(first)
            await authenticate(second)
            second_pid = (
                await second.execute(text("SELECT pg_backend_pid()"))
            ).scalar_one()
            if first_action == "update_commit":
                if with_geolocation == "health":
                    changed = deepcopy(draft.health_assessment)
                    changed["sanitary_purpose_covered"]["answer"] = "pendiente"
                    changes = {"health_assessment": changed}
                elif with_geolocation == "sensitive":
                    changed = deepcopy(draft.sensitive_consent_assessment)
                    changed["proof_available"]["answer"] = "pendiente"
                    changes = {"sensitive_consent_assessment": changed}
                elif with_geolocation:
                    changed = deepcopy(draft.geolocation_assessment)
                    changed["information_clear"]["answer"] = "pendiente"
                    changes = {"geolocation_assessment": changed}
                elif basis == "obligaciones_economicas_art13a":
                    changed = deepcopy(draft.economic_obligations_assessment)
                    changed["title_iii_reviewed"]["answer"] = "pendiente"
                    changes = {"economic_obligations_assessment": changed}
                elif basis == "defensa_derechos_art13e":
                    changed = deepcopy(draft.rights_defense_assessment)
                    changed["necessary_for_route"]["answer"] = "pendiente"
                    changes = {"rights_defense_assessment": changed}
                elif basis == "obligacion_legal_art13b":
                    changed = deepcopy(draft.legal_obligation_assessment)
                    changed["normative_basis_reviewed"]["answer"] = "pendiente"
                    changes = {"legal_obligation_assessment": changed}
                elif basis == "contrato_precontractual_art13c":
                    changed = deepcopy(draft.contract_assessment)
                    changed["necessary_for_route"]["answer"] = "pendiente"
                    changes = {"contract_assessment": changed}
                elif basis == "interes_legitimo_art13d":
                    changed = deepcopy(draft.lia_assessment)
                    changed["necessity"]["linked_to_interest"]["answer"] = "pendiente"
                    changes = {"lia_assessment": changed}
                else:
                    changed = deepcopy(draft.consent_assessment)
                    changed["answers"][0]["answer"] = "pendiente"
                    changes = {"consent_assessment": changed}
                await licitud.update_legal_assessment_draft_v1(
                    first,
                    org_a_id,
                    treatment_id,
                    draft_id,
                    profile_a_id,
                    LegalAssessmentDraftUpdate.model_validate(changes),
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

            # Verificar la espera mediante PostgreSQL, no mediante una demora asumida.
            async def wait_for_database_lock():
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

            await asyncio.wait_for(wait_for_database_lock(), timeout=3)
            assert not contender.done()
            if first_action == "confirm_rollback":
                await first.rollback()
            else:
                await first.commit()
            assert await asyncio.wait_for(contender, timeout=3) == expected_second

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
            if first_action == "update_commit":
                assert by_id[draft_id].status == "borrador"
                assert by_id[previous_id].status == "confirmado"
                assert by_id[previous_id].replaced_at is None
            else:
                assert by_id[draft_id].status == "confirmado"
                assert by_id[previous_id].status == "reemplazado"
                assert by_id[previous_id].replaced_by_assessment_id == draft_id
            await check.rollback()
    finally:
        if contender is not None and not contender.done():
            contender.cancel()
            await asyncio.gather(contender, return_exceptions=True)
        async with _app_session_factory() as cleanup:
            await authenticate(cleanup)
            await cleanup.execute(
                delete(LegalAssessment).where(
                    LegalAssessment.treatment_id == treatment_id
                )
            )
            await cleanup.execute(
                delete(LegalAssessmentSeries).where(
                    LegalAssessmentSeries.treatment_id == treatment_id
                )
            )
            await cleanup.execute(delete(Treatment).where(Treatment.id == treatment_id))
            await cleanup.commit()


async def test_confirm_rechaza_screening_contrato_invalido(confirmation):
    draft = confirmation[4]
    draft.eipd_screening = {"schema_version": 1, "answers": []}
    with pytest.raises(HTTPException) as exc:
        await run_confirm(confirmation)
    assert exc.value.status_code == 400
    assert draft.status == "borrador"
    confirmation[0].flush.assert_not_awaited()


@pytest.mark.parametrize("missing", ["special_conditions", "eipd_screening", "both"])
async def test_confirm_exige_controles_ausentes_sin_reemplazar(confirmation, missing):
    draft, previous = confirmation[4], confirmation[6]
    for field in ("special_conditions", "eipd_screening"):
        if missing in (field, "both"):
            setattr(draft, field, None)
    with pytest.raises(HTTPException) as exc:
        await run_confirm(confirmation)
    # Quitar especiales deja también obsoleta la asociación EIPD existente.
    assert exc.value.status_code == (409 if missing == "special_conditions" else 400)
    assert exc.value.detail["confirmation_blockers"]
    assert draft.status == "borrador" and previous.status == "confirmado"
    confirmation[0].flush.assert_not_awaited()


@pytest.mark.parametrize(
    "change", ["factual", "positive_eipd", "partial_special", "v1"]
)
async def test_confirm_rechazos_transversales_con_motivos(confirmation, change):
    from app.services.eipd import bind_eipd_screening_v1, bind_eipd_screening_v2

    draft, bundle = confirmation[4], confirmation[7]
    if change == "factual":
        bundle.snapshot.retention.deletion_method = "Cambio factual"
    elif change == "positive_eipd":
        data = {k: v for k, v in draft.eipd_screening.items() if k != "context_binding"}
        data["answers"][1]["answer"] = "si"
        draft.eipd_screening = bind_eipd_screening_v2(
            data, bundle.snapshot, None, draft.special_conditions
        ).model_dump(mode="json")
    elif change == "partial_special":
        draft.special_conditions["declarations"].pop()
        data = {k: v for k, v in draft.eipd_screening.items() if k != "context_binding"}
        draft.eipd_screening = bind_eipd_screening_v2(
            data, bundle.snapshot, None, draft.special_conditions
        ).model_dump(mode="json")
    elif change == "v1":
        data = {k: v for k, v in draft.eipd_screening.items() if k != "context_binding"}
        draft.eipd_screening = bind_eipd_screening_v1(
            data, bundle.snapshot, None
        ).model_dump(mode="json")
    with pytest.raises(HTTPException) as exc:
        await run_confirm(confirmation)
    assert exc.value.status_code == (400 if change == "partial_special" else 409)
    assert exc.value.detail["code"] == "controles_transversales_no_preparados"
    assert confirmation[6].status == "confirmado"
    confirmation[0].flush.assert_not_awaited()


@pytest.mark.parametrize("field", ["special_conditions", "eipd_screening"])
async def test_confirm_relee_controles_despues_del_lock(confirmation, field):
    refreshed = deepcopy(confirmation[4])
    setattr(refreshed, field, None)
    confirmation[8][2].scalar_one_or_none.return_value = refreshed
    with pytest.raises(HTTPException) as exc:
        await run_confirm(confirmation)
    assert exc.value.detail["code"] == "controles_transversales_no_preparados"
    assert field in {b["field"] for b in exc.value.detail["confirmation_blockers"]}
    confirmation[0].flush.assert_not_awaited()
    assert confirmation[6].status == "confirmado"


def configure_lia_confirmation(state, complete_lia_context, negative_controls):
    from app.services.eipd import bind_eipd_screening_v2
    from app.services.special_conditions import bind_special_conditions_v1

    lia, rat = deepcopy(complete_lia_context)
    rat["purpose"] = lia["purpose_and_interest"]["purpose_description"] = "Clientes"
    bundle = state[7]
    snapshot = RatContextSnapshotV1.model_validate(rat)
    canonical = RatCanonicalContextV1.model_validate(rat)
    # Bundle is frozen: update the builder's result instead.
    bundle = licitud.RatContextBundleV1(canonical, snapshot)
    state[9].return_value = bundle
    draft = state[4]
    draft.legal_basis = "interes_legitimo_art13d"
    draft.consent_assessment = None
    draft.lia_assessment = lia
    draft.rat_context_snapshot = snapshot.model_dump(mode="json")
    draft.rat_context_hash = licitud.build_rat_context_hash_v1(canonical)
    draft.special_conditions = bind_special_conditions_v1(
        negative_controls["special_conditions"], snapshot, draft.legal_basis, None, lia
    ).model_dump(mode="json")
    draft.eipd_screening = bind_eipd_screening_v2(
        negative_controls["eipd_screening"], snapshot, lia, draft.special_conditions
    ).model_dump(mode="json")
    return (*state[:7], bundle, *state[8:])


@pytest.fixture
def lia_confirmation(confirmation, complete_lia_context, negative_controls):
    return configure_lia_confirmation(
        confirmation, complete_lia_context, negative_controls
    )


async def test_confirm_lia_completa_sin_consentimiento(lia_confirmation):
    result = await run_confirm(lia_confirmation)
    assert result.status == "confirmado"
    assert lia_confirmation[6].status == "reemplazado"
    assert result.consent_assessment is None
    lia_confirmation[0].commit.assert_not_awaited()


@pytest.mark.parametrize(
    "change,code",
    [
        ("ausente", 400),
        ("decision_aislada", 400),
        ("desfavorable", 409),
        ("finalidad", 409),
        ("medida", 400),
        ("lia_cambiada", 409),
    ],
)
async def test_confirm_lia_rechaza_y_conserva_anterior(lia_confirmation, change, code):
    draft = lia_confirmation[4]
    if change == "ausente":
        draft.lia_assessment = None
    elif change == "decision_aislada":
        draft.lia_assessment = {"conclusion": {"decision": "puede_basarse"}}
    elif change == "desfavorable":
        draft.lia_assessment["conclusion"]["decision"] = "no_puede_basarse"
    elif change == "finalidad":
        draft.lia_assessment["purpose_and_interest"][
            "purpose_description"
        ] = "Otra finalidad"
    elif change == "medida":
        draft.lia_assessment["impact"]["loss_of_control"]["answer"] = "si"
    elif change == "lia_cambiada":
        draft.lia_assessment["conclusion"]["balancing_summary"] = "Nueva ponderación"
    with pytest.raises(HTTPException) as exc:
        await run_confirm(lia_confirmation)
    assert exc.value.status_code == code
    assert draft.status == "borrador" and lia_confirmation[6].status == "confirmado"
    lia_confirmation[0].flush.assert_not_awaited()


def configure_contract_confirmation(state, complete_contract, negative_controls):
    from app.services.eipd import bind_eipd_screening_v3
    from app.services.special_conditions import bind_special_conditions_v2

    contract = deepcopy(complete_contract)
    contract["purpose_description"] = state[7].snapshot.purpose
    draft = state[4]
    draft.legal_basis = "contrato_precontractual_art13c"
    draft.consent_assessment = draft.lia_assessment = None
    draft.contract_assessment = contract
    draft.special_conditions = bind_special_conditions_v2(
        negative_controls["special_conditions"],
        state[7].snapshot,
        draft.legal_basis,
        None,
        None,
        contract,
    ).model_dump(mode="json")
    draft.eipd_screening = bind_eipd_screening_v3(
        negative_controls["eipd_screening"],
        state[7].snapshot,
        None,
        draft.special_conditions,
        contract,
    ).model_dump(mode="json")
    return state


@pytest.fixture
def contract_confirmation(confirmation, complete_contract, negative_controls):
    return configure_contract_confirmation(
        confirmation, complete_contract, negative_controls
    )


@pytest.mark.parametrize(
    "route", ["celebracion_contrato", "ejecucion_contrato", "medidas_precontractuales"]
)
async def test_confirm_contrato_completo(
    contract_confirmation, negative_controls, route
):
    state = contract_confirmation
    contract = deepcopy(state[4].contract_assessment)
    contract["route"] = route
    if route == "medidas_precontractuales":
        contract.pop("contractual_reference")
        contract.update(
            precontractual_measures="Preparar oferta",
            requested_by_holder={"answer": "si", "rationale": "Solicitadas"},
            request_reference="Solicitud",
        )
    configure_contract_confirmation(state, contract, negative_controls)
    original = deepcopy(state[4].contract_assessment)
    assert (await run_confirm(state)).status == "confirmado"
    assert state[4].contract_assessment == original
    assert state[6].status == "reemplazado"
    assert state[4].consent_assessment is None and state[4].lia_assessment is None
    state[0].commit.assert_not_awaited()


@pytest.mark.parametrize(
    "change,code",
    [
        ("absent", 400),
        ("partial", 400),
        ("negative", 409),
        ("purpose", 409),
        ("stale", 409),
        ("special", 409),
        ("eipd", 409),
    ],
)
async def test_confirm_contrato_rechaza_sin_reemplazar(
    contract_confirmation, change, code
):
    from app.services.eipd import bind_eipd_screening_v3

    state = contract_confirmation
    draft = state[4]
    if change == "absent":
        draft.contract_assessment = None
    elif change == "partial":
        draft.contract_assessment = {"route": "ejecucion_contrato"}
    elif change == "negative":
        draft.contract_assessment["necessary_for_route"]["answer"] = "no"
    elif change == "purpose":
        draft.contract_assessment["purpose_description"] = "Otra finalidad"
    elif change == "stale":
        draft.contract_assessment["necessity_analysis"] = "Nuevo análisis"
    elif change == "special":
        state[7].snapshot.special_regimes.has_sensitive_data = True
    elif change == "eipd":
        data = {k: v for k, v in draft.eipd_screening.items() if k != "context_binding"}
        data["answers"][1]["answer"] = "si"
        draft.eipd_screening = bind_eipd_screening_v3(
            data,
            state[7].snapshot,
            None,
            draft.special_conditions,
            draft.contract_assessment,
        ).model_dump(mode="json")
    with pytest.raises(HTTPException) as exc:
        await run_confirm(state)
    assert exc.value.status_code == code
    assert draft.status == "borrador" and state[6].status == "confirmado"
    state[0].flush.assert_not_awaited()


def configure_legal_confirmation(state, complete_legal_obligation, negative_controls):
    from app.services.eipd import bind_eipd_screening_v4
    from app.services.special_conditions import bind_special_conditions_v3

    legal = deepcopy(complete_legal_obligation)
    legal["purpose_description"] = state[7].snapshot.purpose
    draft = state[4]
    draft.legal_basis = "obligacion_legal_art13b"
    draft.consent_assessment = draft.lia_assessment = draft.contract_assessment = None
    draft.legal_obligation_assessment = legal
    draft.special_conditions = bind_special_conditions_v3(
        negative_controls["special_conditions"],
        state[7].snapshot,
        draft.legal_basis,
        None,
        None,
        None,
        legal,
    ).model_dump(mode="json")
    draft.eipd_screening = bind_eipd_screening_v4(
        negative_controls["eipd_screening"],
        state[7].snapshot,
        None,
        draft.special_conditions,
        None,
        legal,
    ).model_dump(mode="json")
    return state


@pytest.fixture
def legal_confirmation(confirmation, complete_legal_obligation, negative_controls):
    return configure_legal_confirmation(
        confirmation, complete_legal_obligation, negative_controls
    )


@pytest.mark.parametrize(
    "route", ["cumplimiento_obligacion_legal", "tratamiento_dispuesto_por_ley"]
)
async def test_confirm_obligacion_legal_completa(
    legal_confirmation, negative_controls, route
):
    state = legal_confirmation
    legal = deepcopy(state[4].legal_obligation_assessment)
    legal["route"] = route
    if route == "tratamiento_dispuesto_por_ley":
        legal["processing_required_by_law"] = legal.pop(
            "obligation_applies_to_controller"
        )
    configure_legal_confirmation(state, legal, negative_controls)
    before = deepcopy(state[4].legal_obligation_assessment)
    assert (await run_confirm(state)).status == "confirmado"
    assert state[6].status == "reemplazado"
    assert state[4].legal_obligation_assessment == before
    assert state[4].consent_assessment is None
    state[0].commit.assert_not_awaited()


@pytest.mark.parametrize(
    "change,code",
    [
        ("absent", 400),
        ("partial", 400),
        ("negative", 409),
        ("purpose", 409),
        ("stale", 409),
        ("reference", 400),
        ("special", 409),
        ("eipd", 409),
    ],
)
async def test_confirm_legal_rechazos_sin_reemplazo(legal_confirmation, change, code):
    from app.services.eipd import bind_eipd_screening_v4

    state = legal_confirmation
    draft = state[4]
    if change == "absent":
        draft.legal_obligation_assessment = None
    elif change == "partial":
        draft.legal_obligation_assessment = {"route": "cumplimiento_obligacion_legal"}
    elif change == "negative":
        draft.legal_obligation_assessment["normative_basis_in_force"]["answer"] = "no"
    elif change == "purpose":
        draft.legal_obligation_assessment["purpose_description"] = "Otra finalidad"
    elif change == "stale":
        draft.legal_obligation_assessment["necessity_analysis"] = "Nuevo análisis"
    elif change == "reference":
        draft.legal_obligation_assessment["normative_references"][0]["provision"] = " "
    elif change == "special":
        state[7].snapshot.special_regimes.has_sensitive_data = True
    elif change == "eipd":
        data = {k: v for k, v in draft.eipd_screening.items() if k != "context_binding"}
        data["answers"][1]["answer"] = "si"
        draft.eipd_screening = bind_eipd_screening_v4(
            data,
            state[7].snapshot,
            None,
            draft.special_conditions,
            None,
            draft.legal_obligation_assessment,
        ).model_dump(mode="json")
    with pytest.raises(HTTPException) as exc:
        await run_confirm(state)
    assert exc.value.status_code == code
    assert draft.status == "borrador" and state[6].status == "confirmado"
    state[0].flush.assert_not_awaited()


def configure_rights_confirmation(state, complete_rights_defense, negative_controls):
    from app.services.eipd import bind_eipd_screening_v5
    from app.services.special_conditions import bind_special_conditions_v4

    legal = deepcopy(complete_rights_defense)
    legal["purpose_description"] = state[7].snapshot.purpose
    draft = state[4]
    draft.legal_basis = "defensa_derechos_art13e"
    draft.consent_assessment = draft.lia_assessment = draft.contract_assessment = None
    draft.legal_obligation_assessment = None
    draft.rights_defense_assessment = legal
    draft.special_conditions = bind_special_conditions_v4(
        negative_controls["special_conditions"],
        state[7].snapshot,
        draft.legal_basis,
        None,
        None,
        None,
        None,
        legal,
    ).model_dump(mode="json")
    draft.eipd_screening = bind_eipd_screening_v5(
        negative_controls["eipd_screening"],
        state[7].snapshot,
        None,
        draft.special_conditions,
        None,
        None,
        legal,
    ).model_dump(mode="json")
    return state


@pytest.fixture
def rights_confirmation(confirmation, complete_rights_defense, negative_controls):
    return configure_rights_confirmation(
        confirmation, complete_rights_defense, negative_controls
    )


@pytest.mark.parametrize(
    "route", ["formulacion_derecho", "ejercicio_derecho", "defensa_derecho"]
)
@pytest.mark.parametrize("forum", ["tribunal_justicia", "organo_publico"])
async def test_confirm_derechos_completos(
    rights_confirmation, negative_controls, route, forum
):
    state = rights_confirmation
    data = deepcopy(state[4].rights_defense_assessment)
    data.update(route=route, forum_type=forum)
    configure_rights_confirmation(state, data, negative_controls)
    before = deepcopy(state[4].rights_defense_assessment)
    assert (await run_confirm(state)).status == "confirmado"
    assert state[6].status == "reemplazado"
    assert state[4].rights_defense_assessment == before
    state[0].commit.assert_not_awaited()


@pytest.mark.parametrize(
    "change,code",
    [
        ("absent", 400),
        ("partial", 400),
        ("negative", 409),
        ("purpose", 409),
        ("stale", 409),
        ("evidence", 400),
        ("special", 409),
        ("eipd", 409),
    ],
)
async def test_confirm_derechos_rechazo_sin_reemplazo(
    rights_confirmation, change, code
):
    from app.services.eipd import bind_eipd_screening_v5

    state = rights_confirmation
    draft = state[4]
    if change == "absent":
        draft.rights_defense_assessment = None
    elif change == "partial":
        draft.rights_defense_assessment = {"route": "defensa_derecho"}
    elif change == "negative":
        draft.rights_defense_assessment["necessary_for_route"]["answer"] = "no"
    elif change == "purpose":
        draft.rights_defense_assessment["purpose_description"] = "Otra finalidad"
    elif change == "stale":
        draft.rights_defense_assessment["necessity_analysis"] = "Nuevo análisis"
    elif change == "evidence":
        draft.rights_defense_assessment["evidence"][0]["reference"] = " "
    elif change == "special":
        state[7].snapshot.special_regimes.has_sensitive_data = True
    elif change == "eipd":
        data = {k: v for k, v in draft.eipd_screening.items() if k != "context_binding"}
        data["answers"][1]["answer"] = "si"
        draft.eipd_screening = bind_eipd_screening_v5(
            data,
            state[7].snapshot,
            None,
            draft.special_conditions,
            None,
            None,
            draft.rights_defense_assessment,
        ).model_dump(mode="json")
    with pytest.raises(HTTPException) as exc:
        await run_confirm(state)
    assert exc.value.status_code == code
    assert draft.status == "borrador" and state[6].status == "confirmado"
    state[0].flush.assert_not_awaited()


def configure_economic_confirmation(
    state, complete_economic_obligations, negative_controls
):
    from app.services.eipd import bind_eipd_screening_v6
    from app.services.special_conditions import bind_special_conditions_v5

    legal = deepcopy(complete_economic_obligations)
    legal["purpose_description"] = state[7].snapshot.purpose
    draft = state[4]
    draft.legal_basis = "obligaciones_economicas_art13a"
    draft.consent_assessment = draft.lia_assessment = draft.contract_assessment = None
    draft.legal_obligation_assessment = None
    draft.rights_defense_assessment = None
    draft.economic_obligations_assessment = legal
    draft.special_conditions = bind_special_conditions_v5(
        negative_controls["special_conditions"],
        state[7].snapshot,
        draft.legal_basis,
        None,
        None,
        None,
        None,
        None,
        legal,
    ).model_dump(mode="json")
    draft.eipd_screening = bind_eipd_screening_v6(
        negative_controls["eipd_screening"],
        state[7].snapshot,
        None,
        draft.special_conditions,
        None,
        None,
        None,
        legal,
    ).model_dump(mode="json")
    return state


@pytest.fixture
def economic_confirmation(
    confirmation, complete_economic_obligations, negative_controls
):
    return configure_economic_confirmation(
        confirmation, complete_economic_obligations, negative_controls
    )


@pytest.mark.parametrize("route", ["sin_comunicacion", "con_comunicacion"])
@pytest.mark.parametrize("kind", ["economica", "financiera", "bancaria", "comercial"])
async def test_confirm_economico_completo(
    economic_confirmation, negative_controls, route, kind
):
    state = economic_confirmation
    data = deepcopy(state[4].economic_obligations_assessment)
    data.update(route=route, obligation_type=kind)
    if route == "sin_comunicacion":
        data["operations_include_communication"]["answer"] = "no"
        for field in (
            "communication_scope",
            "communication_eligibility_analysis",
            "communication_restrictions_analysis",
            "payment_and_extinction_controls",
            "communication_permitted",
            "excluded_data_screened",
            "communication_limits_respected",
        ):
            data.pop(field)
    configure_economic_confirmation(state, data, negative_controls)
    before = deepcopy(state[4].economic_obligations_assessment)
    assert (await run_confirm(state)).status == "confirmado"
    assert state[6].status == "reemplazado"
    assert state[4].economic_obligations_assessment == before
    state[0].commit.assert_not_awaited()


@pytest.mark.parametrize(
    "change,code",
    [
        ("absent", 400),
        ("partial", 400),
        ("negative", 409),
        ("purpose", 409),
        ("stale", 409),
        ("reference", 400),
        ("special", 409),
        ("eipd", 409),
        ("factual", 409),
    ],
)
async def test_confirm_economico_rechazo_sin_reemplazo(
    economic_confirmation, change, code
):
    from app.services.eipd import bind_eipd_screening_v6

    state = economic_confirmation
    draft = state[4]
    data = draft.economic_obligations_assessment
    if change == "absent":
        draft.economic_obligations_assessment = None
    elif change == "partial":
        draft.economic_obligations_assessment = {"route": "con_comunicacion"}
    elif change == "negative":
        data["title_iii_reviewed"]["answer"] = "no"
    elif change == "purpose":
        data["purpose_description"] = "Otra finalidad"
    elif change == "stale":
        data["title_iii_analysis"] = "Análisis cambiado"
    elif change == "reference":
        data["normative_references"][0]["provision"] = " "
    elif change == "special":
        state[7].snapshot.special_regimes.has_sensitive_data = True
    elif change == "factual":
        data["operations_include_communication"]["answer"] = "no"
    elif change == "eipd":
        screening = {
            k: v for k, v in draft.eipd_screening.items() if k != "context_binding"
        }
        screening["answers"][1]["answer"] = "si"
        draft.eipd_screening = bind_eipd_screening_v6(
            screening,
            state[7].snapshot,
            None,
            draft.special_conditions,
            None,
            None,
            None,
            data,
        ).model_dump(mode="json")
    with pytest.raises(HTTPException) as exc:
        await run_confirm(state)
    assert exc.value.status_code == code
    assert draft.status == "borrador" and state[6].status == "confirmado"
    state[0].flush.assert_not_awaited()


def configure_geolocation_confirmation(
    state, complete_geolocation, geolocation_controls
):
    from app.services.eipd import bind_eipd_screening_v7
    from app.services.special_conditions import bind_special_conditions_v6

    draft = state[4]
    geo = deepcopy(complete_geolocation)
    geo["purpose_description"] = state[7].snapshot.purpose
    draft.geolocation_assessment = geo
    draft.special_conditions = bind_special_conditions_v6(
        geolocation_controls["special_conditions"],
        state[7].snapshot,
        draft.legal_basis,
        draft.consent_assessment,
        draft.lia_assessment,
        draft.contract_assessment,
        draft.legal_obligation_assessment,
        draft.rights_defense_assessment,
        draft.economic_obligations_assessment,
        geo,
    ).model_dump(mode="json")
    draft.eipd_screening = bind_eipd_screening_v7(
        geolocation_controls["eipd_screening"],
        state[7].snapshot,
        draft.lia_assessment,
        draft.special_conditions,
        draft.contract_assessment,
        draft.legal_obligation_assessment,
        draft.rights_defense_assessment,
        draft.economic_obligations_assessment,
        geo,
    ).model_dump(mode="json")
    return state


def configure_sensitive_confirmation(state, complete_payload, negative_controls):
    from app.services.eipd import bind_eipd_screening_v8
    from app.services.special_conditions import bind_special_conditions_v7

    draft = state[4]
    bundle = state[7]
    for context in (bundle.snapshot, bundle.canonical):
        context.data_categories[0].is_sensitive = True
        context.special_regimes.has_sensitive_data = True
    draft.rat_context_hash = licitud.build_rat_context_hash_v1(bundle.canonical)
    draft.rat_context_snapshot = bundle.snapshot.model_dump(mode="json")
    if draft.lia_assessment is not None:
        draft.lia_assessment["nature_and_scope"][
            "special_rules_description"
        ] = "Consentimiento sensible documentado"
    draft.consent_assessment = deepcopy(complete_payload)
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    controls = deepcopy(negative_controls)
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(
                answer="si", rationale="Consentimiento documentado", **scope
            )
    controls["special_conditions"]["conditions"] = [
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
    ]
    document = {
        "purpose_description": bundle.snapshot.purpose,
        "sensitive_data_description": "Datos sensibles",
        "processing_operations": "Operaciones",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Declaración expresa",
        "technology_equivalence_analysis": "Equivalencia documentada",
        "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
    }
    for field in [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ]:
        document[field] = {"answer": "si", "rationale": "Comprobación documentada"}
    draft.sensitive_consent_assessment = document
    draft.special_conditions = bind_special_conditions_v7(
        controls["special_conditions"],
        bundle.snapshot,
        draft.legal_basis,
        draft.consent_assessment,
        draft.lia_assessment,
        draft.contract_assessment,
        draft.legal_obligation_assessment,
        draft.rights_defense_assessment,
        draft.economic_obligations_assessment,
        None,
        document,
    ).model_dump(mode="json")
    draft.eipd_screening = bind_eipd_screening_v8(
        controls["eipd_screening"],
        bundle.snapshot,
        draft.lia_assessment,
        draft.special_conditions,
        draft.contract_assessment,
        draft.legal_obligation_assessment,
        draft.rights_defense_assessment,
        draft.economic_obligations_assessment,
        None,
        document,
    ).model_dump(mode="json")
    return state


def configure_health_confirmation(state, complete_payload, negative_controls):
    from app.services.eipd import bind_eipd_screening_v9
    from app.services.special_conditions import bind_special_conditions_v8

    state = configure_sensitive_confirmation(state, complete_payload, negative_controls)
    draft = state[4]
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    conditions = {
        k: deepcopy(v)
        for k, v in draft.special_conditions.items()
        if k != "context_binding"
    }
    for declaration in conditions["declarations"]:
        if declaration["question_id"] == "salud_perfil_biologico":
            declaration.update(answer="si", rationale="Salud documentada", **scope)
    conditions["conditions"].append(
        {
            "regime_id": "salud_perfil_biologico_art16bis",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "Referencia sanitaria",
            "documentary_analysis": "Aplicabilidad",
            "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
            **scope,
        }
    )
    health = {
        "purpose_description": state[7].snapshot.purpose,
        "health_data_description": "Datos de salud",
        "processing_operations": "Operaciones",
        "scope": scope,
        "route": "consentimiento_expreso",
        "sanitary_law_references": [
            {
                "norm_name": "Norma por revisar",
                "provision": "Artículo por identificar",
                "official_source_url": "https://example.test/norma",
                "applicability_analysis": "Aplicabilidad",
            }
        ],
        "sanitary_purpose_analysis": "Finalidad documentada",
        "sanitary_purpose_covered": {"answer": "si", "rationale": "Cobertura"},
        "collection_contexts": ["otro"],
        "collection_context_analysis": "Contexto documentado",
        "includes_data_cession": {"answer": "no", "rationale": "Sin cesión"},
        "includes_identifiable_biological_samples": {
            "answer": "no",
            "rationale": "Sin muestras",
        },
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
    }
    draft.health_assessment = health
    draft.special_conditions = bind_special_conditions_v8(
        conditions,
        state[7].snapshot,
        draft.legal_basis,
        draft.consent_assessment,
        draft.lia_assessment,
        draft.contract_assessment,
        draft.legal_obligation_assessment,
        draft.rights_defense_assessment,
        draft.economic_obligations_assessment,
        None,
        draft.sensitive_consent_assessment,
        health,
    ).model_dump(mode="json")
    draft.eipd_screening = bind_eipd_screening_v9(
        negative_controls["eipd_screening"],
        state[7].snapshot,
        draft.lia_assessment,
        draft.special_conditions,
        draft.contract_assessment,
        draft.legal_obligation_assessment,
        draft.rights_defense_assessment,
        draft.economic_obligations_assessment,
        None,
        draft.sensitive_consent_assessment,
        health,
    ).model_dump(mode="json")
    return state
