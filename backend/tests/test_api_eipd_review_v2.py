"""Revision autenticada v2 con politica de servidor deshabilitada."""

import pytest
from sqlalchemy import event

from app.services.eipd_policy import (
    build_eipd_review_policy_metadata_v1,
    resolve_eipd_gate_policy_v1,
)
from tests import test_api_eipd_prepared_frontier as protected
from tests import test_api_eipd_resolution as fixtures
from tests.test_api_eipd_resolution_reviews import events, review, setup

rat_m3 = fixtures.rat_m3
resolution_rat = fixtures.resolution_rat
complete_resolution = protected.complete_resolution
prepared_protected_assessment = protected.prepared_protected_assessment


@pytest.mark.parametrize("decision", ["requiere_cambios", "no_continuar"])
async def test_partial_negative_records_server_policy(
    client_a, resolution_rat, org_a_id, profile_a_id, _session_factory, decision
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(client, resolution_rat)
        response = await client.post(
            detail + "/eipd-resolution/reviews", json=review(decision)
        )
        assert response.status_code == 201, response.text
        assert (await client.get(detail)).json() == original
        rows = await events(_session_factory, original["id"])
        assert len(rows) == 1
        row = rows[0]
        assert row.created_by == profile_a_id
        assert row.decision == decision
        expected = build_eipd_review_policy_metadata_v1(resolve_eipd_gate_policy_v1())
        assert {name: getattr(row, name) for name in expected} == expected
        controls = (await client.get(detail + "/readiness")).json()["eipd_controls_v2"]
        assert controls["latest_review_policy"] == dict(expected, review_id=str(row.id))
        assert controls["review_policy_status"] == "vigente"
        assert controls["policy"]["activation"] == "deshabilitada"
        assert "decision_no_continuar" in {
            i["code"] for i in controls["confirmation_blockers"]
        }


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("prior_negative", [False, True])
async def test_prepared_positive_v2_matches_readiness_and_preserves_history(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    _session_factory,
    _app_engine,
    biometric,
    prior_negative,
):
    _, detail, original = prepared_protected_assessment
    async with fixtures.client_for(client_a, org_a_id) as client:
        if prior_negative:
            assert (
                await client.post(
                    detail + "/eipd-resolution/reviews", json=review("no_continuar")
                )
            ).status_code == 201
        expected = (await client.get(detail + "/readiness")).json()
        before = [row.id for row in await events(_session_factory, original["id"])]
        queries = []

        def record(_conn, _cursor, statement, _parameters, _context, _many):
            if (
                "eipd_resolution_reviews" in statement
                and statement.lstrip().upper().startswith("SELECT")
            ):
                queries.append(statement)

        event.listen(_app_engine.sync_engine, "before_cursor_execute", record)
        try:
            response = await client.post(
                detail + "/eipd-resolution/reviews?activation=habilitada",
                json=review("continuar"),
            )
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", record)
        assert response.status_code == 409, response.text
        result = response.json()["detail"]
        assert result["evaluation_version"] == 2
        assert result["eipd_controls"] == expected["eipd_controls"]
        assert result["eipd_controls_v2"] == expected["eipd_controls_v2"]
        assert result["issues_v2"] == expected["eipd_controls_v2"]["review_blockers"]
        assert not any(i["stage"] == "review" for i in result["issues_v2"])
        assert len(queries) == 1
        assert (await client.get(detail)).json() == original
        assert [
            row.id for row in await events(_session_factory, original["id"])
        ] == before


@pytest.mark.parametrize(
    "field,value",
    [
        ("policy_version", 1),
        ("policy_hash", "a" * 64),
        ("policy_reference", "fake"),
        ("policy", {"activation": "habilitada"}),
    ],
)
async def test_client_cannot_supply_policy(
    client_a, resolution_rat, org_a_id, _session_factory, field, value
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(client, resolution_rat)
        response = await client.post(
            detail + "/eipd-resolution/reviews", json=dict(review(), **{field: value})
        )
        assert response.status_code == 422
        assert not await events(_session_factory, original["id"])
        assert (await client.get(detail)).json() == original
