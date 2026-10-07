"""Decision de confirmacion v2 con servidor deshabilitado e historia vigente."""

import pytest
from sqlalchemy import event

from app.services.eipd_policy import (
    build_eipd_review_policy_metadata_v1,
    resolve_eipd_gate_policy_v1,
)
from tests import test_api_eipd_prepared_frontier as protected
from tests import test_api_eipd_resolution as fixtures
from tests.test_api_eipd_controls_v2_readiness import insert_historical_positive
from tests.test_api_eipd_resolution_reviews import events, review, setup

rat_m3 = fixtures.rat_m3
resolution_rat = fixtures.resolution_rat
complete_payload = fixtures.complete_payload
complete_resolution = protected.complete_resolution
prepared_protected_assessment = protected.prepared_protected_assessment


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize(
    "history",
    ["absent", "legacy_positive", "current_positive", "old_positive", "negative"],
)
async def test_confirm_v2_readiness_identity_and_preservation(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    profile_a_id,
    _session_factory,
    _app_engine,
    biometric,
    history,
):
    _, detail, original = prepared_protected_assessment
    if history.endswith("positive"):
        metadata = build_eipd_review_policy_metadata_v1(resolve_eipd_gate_policy_v1())
        if history == "legacy_positive":
            metadata = {}
        elif history == "old_positive":
            metadata["policy_hash"] = "a" * 64
        await insert_historical_positive(
            _session_factory, org_a_id, profile_a_id, original, metadata
        )
    async with fixtures.client_for(client_a, org_a_id) as client:
        if history == "negative":
            response = await client.post(
                detail + "/eipd-resolution/reviews", json=review("no_continuar")
            )
            assert response.status_code == 201
        before = (await client.get(detail + "/readiness")).json()
        rows_before = [row.id for row in await events(_session_factory, original["id"])]
        queries = []

        def record(_conn, _cursor, statement, _parameters, _context, _many):
            if (
                "eipd_resolution_reviews" in statement
                and statement.lstrip().upper().startswith("SELECT")
            ):
                queries.append(statement)

        event.listen(_app_engine.sync_engine, "before_cursor_execute", record)
        try:
            response = await client.post(detail + "/confirm?activation=habilitada")
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", record)
        assert response.status_code == 409, response.text
        result = response.json()["detail"]
        assert result["evaluation_version"] == 2
        assert result["eipd_controls"] == before["eipd_controls"]
        assert result["eipd_controls_v2"] == before["eipd_controls_v2"]
        assert len(queries) == 1
        v2 = result["eipd_controls_v2"]
        assert v2["preparation_result"] == "preparado"
        assert v2["policy"]["activation"] == "deshabilitada"
        assert "gate_eipd_no_habilitado" in {
            i["code"] for i in v2["confirmation_blockers"]
        }
        expected = {
            "absent": "sin_revision",
            "legacy_positive": "sin_identidad",
            "current_positive": "vigente",
            "old_positive": "obsoleta",
            "negative": "vigente",
        }
        assert v2["review_policy_status"] == expected[history]
        assert (await client.get(detail)).json() == original
        assert [
            row.id for row in await events(_session_factory, original["id"])
        ] == rows_before


async def test_ordinary_history_without_document_does_not_expand_gate_scope(
    client_a,
    resolution_rat,
    org_a_id,
    _session_factory,
    complete_payload,
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        tid, payload = resolution_rat
        detail, original = await setup(
            client, (tid, dict(payload, consent_assessment=complete_payload))
        )
        assert (
            await client.post(detail + "/eipd-resolution/reviews", json=review())
        ).status_code == 201
        cleared = await client.patch(detail, json={"eipd_resolution_assessment": None})
        assert cleared.status_code == 200
        expected = (await client.get(detail + "/readiness")).json()["eipd_controls_v2"]
        response = await client.post(detail + "/confirm")
        assert response.status_code == 200, response.text
        assert expected["review_state"]["review_status"] == "obsoleta"
        assert (await client.get(detail)).json()["status"] == "confirmado"
        assert len(await events(_session_factory, original["id"])) == 1
