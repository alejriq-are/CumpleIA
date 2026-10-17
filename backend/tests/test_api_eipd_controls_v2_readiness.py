"""Readiness v2 con politica de servidor deshabilitada; ninguna accion habilitada."""

from dataclasses import asdict
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import event

from app.db.models import EipdResolutionReview
from app.schemas.licitud import EipdControlCompositionV2Out
from app.services.eipd_controls import compose_eipd_controls_v2
from app.services.eipd_policy import (
    build_eipd_review_policy_metadata_v1,
    resolve_eipd_gate_policy_v1,
)
from app.services.eipd_resolution import build_eipd_resolution_document_hash_v1
from tests import test_api_eipd_prepared_frontier as protected_fixtures
from tests import test_api_eipd_resolution as api_fixtures
from tests import test_services_eipd_controls as control_fixtures
from tests.eipd_selected_policy_fixtures import (
    explicit_review_policy as explicit_review_policy,
)
from tests.test_api_eipd_resolution_reviews import events, review

rat_m3 = api_fixtures.rat_m3
resolution_rat = api_fixtures.resolution_rat
complete_resolution = protected_fixtures.complete_resolution
prepared_protected_assessment = protected_fixtures.prepared_protected_assessment
frontier_context = control_fixtures.frontier_context
prepared_controls = control_fixtures.prepared_controls


def test_resolver_is_fresh_disabled_and_ignores_environment(monkeypatch):
    monkeypatch.setenv("EIPD_GATE_ENABLED", "true")
    monkeypatch.setenv("EIPD_POLICY_HASH", "a" * 64)
    first = resolve_eipd_gate_policy_v1()
    before = first.model_dump(mode="json")
    assert first.activation == "deshabilitada"
    assert first.sources_status == first.acceptance_status == "pendiente"
    assert first.source_records == ()
    first.activation = "habilitada"
    assert resolve_eipd_gate_policy_v1().model_dump(mode="json") == before


@pytest.mark.parametrize(
    "mode",
    [
        "valid",
        "version",
        "bool",
        "extra",
        "nested_version",
        "identity_partial",
        "activation",
    ],
)
def test_v2_output_contract_closed_and_versioned(prepared_controls, mode):
    from datetime import date

    result = compose_eipd_controls_v2(
        dict(
            assessment=prepared_controls,
            policy=resolve_eipd_gate_policy_v1(),
            latest_review_policy=None,
        ),
        evaluated_on=date(2026, 10, 7),
    )
    data = dict(asdict(result), evaluation_version=2, latest_review_policy=None)
    data["detection_v2"]["evaluation_version"] = 2
    if mode == "version":
        data["evaluation_version"] = 1
    elif mode == "bool":
        data["policy"]["policy_version"] = True
    elif mode == "extra":
        data["policy"]["approved"] = True
    elif mode == "nested_version":
        data["detection_v2"]["evaluation_version"] = 1
    elif mode == "identity_partial":
        data["policy"]["policy_hash"] = None
    elif mode == "activation":
        data["policy"]["activation"] = "habilitada"
    if mode == "valid":
        assert EipdControlCompositionV2Out.model_validate(data).evaluation_version == 2
    else:
        with pytest.raises(ValidationError):
            EipdControlCompositionV2Out.model_validate(data)


@pytest.mark.parametrize("biometric", [False, True])
async def test_prepared_v2_readonly_disabled_single_history_query(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    org_b_id,
    _session_factory,
    _app_engine,
    biometric,
):
    _, detail, original = prepared_protected_assessment
    queries = []

    def record(_conn, _cursor, statement, _parameters, _context, _many):
        if (
            "eipd_resolution_reviews" in statement
            and statement.lstrip().upper().startswith("SELECT")
        ):
            queries.append(statement)

    async with api_fixtures.client_for(client_a, org_a_id) as client:
        event.listen(_app_engine.sync_engine, "before_cursor_execute", record)
        try:
            response = await client.get(detail + "/readiness")
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", record)
        assert response.status_code == 200, response.text
        assert len(queries) == 1
        before = response.json()
        controls = before["eipd_controls_v2"]
        assert controls["evaluation_version"] == 2
        assert controls["preparation_result"] == "preparado"
        assert (
            controls["preparation_issues"]
            == before["eipd_controls"]["preparation_issues"]
        )
        assert controls["detection_v2"] == before["eipd_v2"]
        assert controls["review_state"] == before["eipd_resolution_review"]
        assert controls["review_policy_status"] == "sin_revision"
        assert controls["latest_review_policy"] is None
        assert controls["policy"]["activation"] == "deshabilitada"
        assert {i["code"] for i in controls["review_blockers"]} == {
            "fuentes_oficiales_no_verificadas",
            "frontera_revision_no_validada",
            "gate_eipd_no_habilitado",
        }
        assert before["confirmation_blockers"]
        assert (
            await client.get(
                detail + "/readiness?activation=habilitada&policy_hash=fake"
            )
        ).json() == before
        for suffix, request in [
            ("/eipd-resolution/reviews", review("continuar")),
            ("/confirm", None),
        ]:
            result = (
                await client.post(detail + suffix, json=request)
                if request
                else await client.post(detail + suffix)
            )
            assert result.status_code == 409
            assert result.json()["detail"]["eipd_controls"] == before["eipd_controls"]
        assert (await client.get(detail)).json() == original
        assert not await events(_session_factory, original["id"])
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403


async def insert_historical_positive(
    session_factory, org, actor, original, metadata, decision="continuar"
):
    # Fixture de historia: no se registra continuar por accion de producto.
    async with session_factory() as db:
        document = original["eipd_resolution_assessment"]
        row = EipdResolutionReview(
            organization_id=org,
            assessment_id=UUID(original["id"]),
            created_by=actor,
            decision=decision,
            rationale="TEST: registro historico",
            review_reference="TEST: REV85",
            document_hash=build_eipd_resolution_document_hash_v1(document),
            context_hash=document["context_binding"]["context_hash"],
            **metadata,
        )
        db.add(row)
        await db.commit()
        return str(row.id)


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("mode", ["legacy", "current", "old_policy"])
async def test_persisted_identity_is_separate_and_cannot_activate(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    profile_a_id,
    _session_factory,
    biometric,
    mode,
):
    _, detail, original = prepared_protected_assessment
    metadata = (
        {}
        if mode == "legacy"
        else build_eipd_review_policy_metadata_v1(resolve_eipd_gate_policy_v1())
    )
    if mode == "old_policy":
        metadata["policy_reference"] = "TEST: politica anterior"
    rid = await insert_historical_positive(
        _session_factory, org_a_id, profile_a_id, original, metadata
    )
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        before = (await client.get(detail + "/readiness")).json()
        controls = before["eipd_controls_v2"]
        assert controls["review_state"]["latest_review"]["id"] == rid
        assert controls["review_state"]["review_status"] == "vigente"
        assert (
            controls["review_policy_status"]
            == {
                "legacy": "sin_identidad",
                "current": "vigente",
                "old_policy": "obsoleta",
            }[mode]
        )
        if mode == "legacy":
            assert controls["latest_review_policy"] is None
        else:
            assert controls["latest_review_policy"]["review_id"] == rid
            assert (
                controls["latest_review_policy"]["policy_hash"]
                == metadata["policy_hash"]
            )
        assert controls["review_blockers"] and controls["confirmation_blockers"]
        assert controls["policy"]["activation"] == "deshabilitada"
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (
            await client.post(
                detail + "/eipd-resolution/reviews", json=review("continuar")
            )
        ).status_code == 409
        assert (await client.get(detail)).json() == original
        assert len(await events(_session_factory, original["id"])) == 1
        cleared = await client.patch(detail, json={"eipd_resolution_assessment": None})
        assert cleared.status_code == 200
        after = (await client.get(detail + "/readiness")).json()["eipd_controls_v2"]
        assert after["review_state"]["review_status"] == "obsoleta"
        assert after["review_policy_status"] == controls["review_policy_status"]
        assert after["latest_review_policy"] == controls["latest_review_policy"]
        assert after["preparation_result"] != "preparado"
        assert len(await events(_session_factory, original["id"])) == 1


@pytest.mark.parametrize("biometric", [False, True])
async def test_last_negative_legacy_does_not_fall_back_to_older_policy(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    profile_a_id,
    _session_factory,
    biometric,
):
    _, detail, original = prepared_protected_assessment
    await insert_historical_positive(
        _session_factory,
        org_a_id,
        profile_a_id,
        original,
        build_eipd_review_policy_metadata_v1(resolve_eipd_gate_policy_v1()),
    )
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        negative_id = await insert_historical_positive(
            _session_factory,
            org_a_id,
            profile_a_id,
            original,
            {},
            decision="no_continuar",
        )
        controls = (await client.get(detail + "/readiness")).json()["eipd_controls_v2"]
        assert controls["review_state"]["latest_review"]["id"] == negative_id
        assert controls["latest_review_policy"] is None
        assert controls["review_policy_status"] == "sin_identidad"
        assert "decision_no_continuar" in {
            i["code"] for i in controls["confirmation_blockers"]
        }
        assert len(await events(_session_factory, original["id"])) == 2


async def test_ordinary_without_eipd_keeps_both_compositions_null(
    client_a, resolution_rat, org_a_id
):
    tid, payload = resolution_rat
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(
            f"/licitud/treatments/{tid}/assessments", json=payload
        )
        assert created.status_code == 201
        data = (
            await client.get(
                f"/licitud/treatments/{tid}/assessments/{created.json()['id']}/readiness"
            )
        ).json()
        assert data["eipd_controls"] is None and data["eipd_controls_v2"] is None
