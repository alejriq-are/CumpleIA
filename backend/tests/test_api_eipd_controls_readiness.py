from dataclasses import asdict

import pytest
from pydantic import ValidationError
from sqlalchemy import select, update

from app.db.models import EipdResolutionReview, TreatmentPurpose
from app.schemas.licitud import EipdControlCompositionOut
from app.services.eipd_controls import compose_eipd_controls_v1
from tests import test_api_eipd_resolution as api_fixtures
from tests import test_services_eipd_controls as control_fixtures

rat_m3 = api_fixtures.rat_m3
resolution_rat = api_fixtures.resolution_rat
complete_payload = api_fixtures.complete_payload
frontier_context = control_fixtures.frontier_context
complete_resolution = control_fixtures.complete_resolution
prepared_controls = control_fixtures.prepared_controls


@pytest.mark.parametrize(
    "mode",
    [
        "valid",
        "version",
        "detection_version",
        "approved",
        "stage",
        "ordinary",
        "nested_flag",
    ],
)
def test_contract_closed_versioned_and_no_authorization(prepared_controls, mode):
    result = compose_eipd_controls_v1(
        prepared_controls, evaluated_on=control_fixtures.TODAY
    )
    data = asdict(result) | {"evaluation_version": 1}
    data["detection_v2"]["evaluation_version"] = 2
    if mode == "version":
        data["evaluation_version"] = 2
    elif mode == "detection_version":
        data["detection_v2"]["evaluation_version"] = 1
    elif mode == "approved":
        data["can_confirm"] = True
    elif mode == "stage":
        data["review_blockers"][0]["stage"] = "unknown"
    elif mode == "ordinary":
        data["ordinary"]["legal_basis"] = "unknown"
    elif mode == "nested_flag":
        data["review_blockers"][0]["approved"] = True
    if mode == "valid":
        out = EipdControlCompositionOut.model_validate(data)
        assert out.preparation_result == "preparado"
        assert out.review_blockers and out.confirmation_blockers
    else:
        with pytest.raises(ValidationError):
            EipdControlCompositionOut.model_validate(data)


async def history(factory, tid):
    from app.db.models import LegalAssessment

    async with factory() as db:
        return list(
            (
                await db.scalars(
                    select(EipdResolutionReview).where(
                        EipdResolutionReview.assessment_id.in_(
                            select(LegalAssessment.id).where(
                                LegalAssessment.treatment_id == tid
                            )
                        )
                    )
                )
            ).all()
        )


async def test_composition_without_review_does_not_invent_event_or_mutate(
    client_a, resolution_rat, org_a_id, org_b_id, _session_factory
):
    tid, payload = resolution_rat
    data = dict(payload, eipd_resolution_assessment={"document_reference": "EIPD1"})
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(f"/licitud/treatments/{tid}/assessments", json=data)
        assert created.status_code == 201
        original = created.json()
        detail = f"/licitud/treatments/{tid}/assessments/{original['id']}"
        readiness = (await client.get(detail + "/readiness")).json()
        controls = readiness["eipd_controls"]
        assert controls["evaluation_version"] == 1
        assert controls["detection_v2"] == readiness["eipd_v2"]
        assert controls["resolution"] == readiness["eipd_resolution"]
        assert controls["review_state"] == readiness["eipd_resolution_review"]
        assert controls["review_state"]["review_status"] == "sin_revision"
        assert "review" not in {b["stage"] for b in controls["review_blockers"]}
        assert "revision_ausente" in {
            b["code"] for b in controls["confirmation_blockers"]
        }
        assert {"fuentes_oficiales_no_verificadas", "gate_eipd_no_habilitado"} <= {
            b["code"] for b in controls["review_blockers"]
        }
        assert "resolucion_eipd_no_validada" in {
            b["code"] for b in readiness["confirmation_blockers"]
        }
        assert (await client.get(detail)).json() == original
        assert (await client.get(detail + "/readiness")).json() == readiness
        assert not await history(_session_factory, tid)
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        assert not await history(_session_factory, tid)


async def test_latest_negative_review_stale_after_clear_and_unavailable_rat(
    client_a, resolution_rat, org_a_id, _session_factory
):
    tid, payload = resolution_rat
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(
            f"/licitud/treatments/{tid}/assessments",
            json=dict(
                payload, eipd_resolution_assessment={"document_reference": "EIPD1"}
            ),
        )
        assert created.status_code == 201
        detail = f"/licitud/treatments/{tid}/assessments/{created.json()['id']}"
        events = []
        for decision in ("requiere_cambios", "no_continuar"):
            event = await client.post(
                detail + "/eipd-resolution/reviews",
                json={
                    "decision": decision,
                    "rationale": "Revision humana",
                    "review_reference": "REV1",
                },
            )
            assert event.status_code == 201
            events.append(event.json())
        readiness = (await client.get(detail + "/readiness")).json()
        controls = readiness["eipd_controls"]
        assert controls["review_state"]["latest_review"] == events[-1]
        assert controls["review_state"]["review_status"] == "vigente"
        assert "decision_no_continuar" in {
            b["code"] for b in controls["confirmation_blockers"]
        }
        patched = await client.patch(detail, json={"eipd_resolution_assessment": None})
        assert patched.status_code == 200
        original = patched.json()
        controls = (await client.get(detail + "/readiness")).json()["eipd_controls"]
        assert controls["review_state"]["review_status"] == "obsoleta"
        assert controls["review_state"]["latest_review"] == events[-1]
        assert "expediente_ausente" in {
            b["code"] for b in controls["preparation_issues"]
        }
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentPurpose)
                .where(TreatmentPurpose.treatment_id == tid)
                .values(purpose="Finalidad cambiada")
            )
            await db.commit()
        controls = (await client.get(detail + "/readiness")).json()["eipd_controls"]
        assert controls["detection_v2"]["context_current"] is False
        assert "contexto_rat_no_disponible" in {
            b["code"] for b in controls["review_blockers"]
        }
        assert (await client.get(detail)).json() == original
        assert len(await history(_session_factory, tid)) == 2


async def test_ordinary_without_eipd_keeps_composition_null(
    client_a, resolution_rat, org_a_id
):
    tid, payload = resolution_rat
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(
            f"/licitud/treatments/{tid}/assessments", json=payload
        )
        assert created.status_code == 201
        detail = f"/licitud/treatments/{tid}/assessments/{created.json()['id']}"
        readiness = (await client.get(detail + "/readiness")).json()
        assert readiness["eipd_controls"] is None
        assert readiness["eipd_v2"]["result"] == "sin_supuestos_declarados"
