"""Diagnostico por decision, sin autoridad ni solicitudes humanas sinteticas."""

import pytest
from pydantic import ValidationError
from sqlalchemy import event

from app.main import app
from app.schemas.licitud import EipdReviewPrerequisitesByDecisionV3Out
from tests import test_api_eipd_negative_review_v2 as cases

rat_m3 = cases.rat_m3
resolution_rat = cases.resolution_rat


@pytest.mark.parametrize("mode", ["current", "stale", "missing", "legacy"])
async def test_readonly_decision_diagnostics(
    client_a, resolution_rat, org_a_id, org_b_id, _session_factory, _app_engine, mode
):
    async with cases.api.client_for(client_a, org_a_id) as client:
        # This module intentionally has no selected-policy fixture: documentary
        # prerequisites may be met while actual action remains unavailable.
        if mode == "legacy":
            tid, payload = resolution_rat
            response = await client.post(
                f"/licitud/treatments/{tid}/assessments",
                json={
                    **payload,
                    "eipd_resolution_assessment": {
                        "document_reference": "TEST: legacy157"
                    },
                },
            )
            assert response.status_code == 201
            original = response.json()
            url = f"/licitud/treatments/{tid}/assessments/{original['id']}"
            assert (
                await client.patch(
                    url, json={"research_assessment": {"purpose_type": "cientifico"}}
                )
            ).status_code == 200
        else:
            url, original = await cases.create(client, resolution_rat)
            if mode == "stale":
                assert (
                    await client.patch(
                        url,
                        json={"research_assessment": {"purpose_type": "estadistico"}},
                    )
                ).status_code == 200
            elif mode == "missing":
                assert (
                    await client.patch(url, json={"eipd_resolution_assessment": None})
                ).status_code == 200
        before = (await client.get(url)).json()
        statements = []

        def record(_conn, _cursor, statement, _params, _ctx, _many):
            statements.append(statement)

        event.listen(_app_engine.sync_engine, "before_cursor_execute", record)
        try:
            response = await client.get(url + "/readiness")
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", record)
        assert response.status_code == 200, response.text
        data = response.json()["eipd_controls_v3"]
        diagnostic = data["review_prerequisites_v3"]
        assert diagnostic["evaluation_scope"] == "requisitos_documentales"
        assert diagnostic["evaluation_version"] == 3
        assert not diagnostic["authorizes_action"] and not diagnostic["can_confirm"]
        assert not data["can_confirm"] and data["policy"]["policy_hash"] is None
        assert data["latest_review_context_metadata"] is None
        for decision in ("requiere_cambios", "no_continuar"):
            result = diagnostic[decision]
            assert result["prerequisites_met"] == (mode == "current")
            assert (result["context_metadata"] is not None) == (mode == "current")
        assert diagnostic["requiere_cambios"] == diagnostic["no_continuar"]
        positive = diagnostic["continuar"]
        assert not positive["prerequisites_met"]
        codes = {i["code"] for i in positive["issues"]}
        assert "investigacion_confirmacion_bloqueada" in codes
        assert "politica_no_disponible" in codes and "revision_ausente" not in codes
        assert not any(
            s.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
            for s in statements
        )
        assert (
            sum(
                "eipd_resolution_reviews" in s
                and s.lstrip().upper().startswith("SELECT")
                for s in statements
            )
            == 1
        )
        assert (await client.get(url)).json() == before
        assert not await cases.rows(_session_factory, original["id"])
        assert (
            await client.get(
                url + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        assert (
            await client.get(url + "/readiness?authorizes_action=true")
        ).json() == response.json()
        assert EipdReviewPrerequisitesByDecisionV3Out.model_validate(diagnostic)
        for change in (
            {"authorizes_action": True},
            {"can_confirm": True},
            {"evaluation_version": 2},
            {"approved": True},
        ):
            with pytest.raises(ValidationError):
                EipdReviewPrerequisitesByDecisionV3Out.model_validate(
                    dict(diagnostic, **change)
                )


async def test_closed_openapi_output_only():
    schemas = app.openapi()["components"]["schemas"]
    for name in (
        "EipdReviewPrerequisitesByDecisionV3Out",
        "EipdReviewDecisionPrerequisitesV3Out",
    ):
        assert schemas[name]["additionalProperties"] is False
    assert (
        "review_prerequisites_v3"
        in schemas["EipdControlCompositionV3Out"]["properties"]
    )
    assert (
        "review_prerequisites_v3" not in schemas["EipdResolutionReviewIn"]["properties"]
    )
