"""Escritura documental V2 sin revision ni confirmacion habilitadas."""

from copy import deepcopy
from uuid import UUID

import pytest
from sqlalchemy import select, text

from app.db.models import EipdResolutionReview, TreatmentDataSource
from app.services.eipd_resolution_binding_v2 import (
    EipdResolutionContextV2,
    eipd_resolution_context_is_current_v2,
)
from tests import test_api_eipd_resolution as api
from tests import test_services_research as research_cases
from tests.eipd_selected_policy_fixtures import (
    explicit_review_policy as explicit_review_policy,
)

rat_m3 = api.rat_m3
resolution_rat = api.resolution_rat
context = research_cases.context


def response_context(value):
    return {
        k: value[k]
        for k in EipdResolutionContextV2.model_fields
        if k != "context_schema_version"
    }


@pytest.fixture
def resolution_document():
    return {"document_reference": "TEST: EIPD149", "report_reference": "TEST: informe"}


@pytest.mark.parametrize("operation", ["create", "patch"])
async def test_final_context_omission_reaporte_withdrawal_and_readonly(
    client_a,
    resolution_rat,
    org_a_id,
    org_b_id,
    context,
    _session_factory,
    operation,
    resolution_document,
):
    treatment, payload = resolution_rat
    document, _, lia = context
    async with _session_factory() as db:
        db.add(
            TreatmentDataSource(
                organization_id=org_a_id,
                treatment_id=treatment,
                source_type="titular",
                is_public_source=False,
            )
        )
        await db.commit()
    async with api.client_for(client_a, org_a_id) as client:
        collection = f"/licitud/treatments/{treatment}/assessments"
        material = dict(
            research_assessment=document,
            legal_basis="interes_legitimo_art13d",
            lia_assessment=lia,
            eipd_resolution_assessment=resolution_document,
        )
        created = await client.post(
            collection,
            json={**payload, **material} if operation == "create" else payload,
        )
        assert created.status_code == 201, created.text
        url = collection + "/" + created.json()["id"]
        current = created.json()
        if operation == "patch":
            patched = await client.patch(url, json=material)
            assert patched.status_code == 200, patched.text
            current = patched.json()
        bound = current["eipd_resolution_assessment"]
        assert bound["context_binding"]["binding_version"] == 2
        assert eipd_resolution_context_is_current_v2(bound, response_context(current))
        ready = await client.get(url + "/readiness")
        assert ready.status_code == 200, ready.text
        data = ready.json()
        assert data["eipd_controls"] is None and data["eipd_controls_v2"] is None
        assert data["eipd_controls_v3"]["resolution"]["binding_version"] == 2
        assert data["eipd_controls_v3"]["resolution"]["context_current"]
        assert not data["eipd_controls_v3"]["can_confirm"]
        assert (await client.get(url)).json() == current
        for decision in ("continuar", "requiere_cambios", "no_continuar"):
            rejected = await client.post(
                url + "/eipd-resolution/reviews",
                json={
                    "decision": decision,
                    "rationale": "TEST: revision",
                    "review_reference": "TEST: REV149",
                },
            )
            assert rejected.status_code == 409, rejected.text
            assert (
                rejected.json()["detail"]["code"]
                == "resolucion_eipd_v2_revision_pendiente"
            )
        assert (await client.post(url + "/confirm")).status_code == 409
        assert (
            await client.patch(
                url,
                json={"eipd_resolution_assessment": resolution_document},
                headers={"X-Organization-Id": str(org_b_id)},
            )
        ).status_code == 403
        assert (
            await client.post(
                collection,
                json={**payload, **material},
                headers={"X-Organization-Id": str(org_b_id)},
            )
        ).status_code == 403
        document = deepcopy(document)
        document["public_interest_analysis"] += " cambiado"
        changed = await client.patch(url, json={"research_assessment": document})
        assert changed.status_code == 200, changed.text
        assert changed.json()["eipd_resolution_assessment"] == bound
        stale = (await client.get(url + "/readiness")).json()["eipd_controls_v3"]
        assert not stale["resolution"]["context_current"]
        refreshed = await client.patch(
            url, json={"eipd_resolution_assessment": resolution_document}
        )
        assert refreshed.status_code == 200, refreshed.text
        new = refreshed.json()
        assert eipd_resolution_context_is_current_v2(
            new["eipd_resolution_assessment"], response_context(new)
        )
        withdrawn = await client.patch(
            url, json={"research_assessment": None, "special_conditions": None}
        )
        assert withdrawn.status_code == 200
        assert (
            withdrawn.json()["eipd_resolution_assessment"]
            == new["eipd_resolution_assessment"]
        )
        again = await client.patch(
            url, json={"eipd_resolution_assessment": resolution_document}
        )
        assert again.status_code == 200
        assert (
            again.json()["eipd_resolution_assessment"]["context_binding"][
                "binding_version"
            ]
            == 2
        )
        assert (await client.get(url + "/readiness")).json()[
            "eipd_controls_v3"
        ] is not None
        cleared = await client.patch(url, json={"eipd_resolution_assessment": None})
        assert (
            cleared.status_code == 200
            and cleared.json()["eipd_resolution_assessment"] is None
        )
        async with _session_factory() as db:
            assert not (
                await db.scalars(
                    select(EipdResolutionReview).where(
                        EipdResolutionReview.assessment_id == UUID(current["id"])
                    )
                )
            ).all()


async def test_legacy_resolution_is_not_upgraded_by_omission(
    client_a,
    resolution_rat,
    org_a_id,
    context,
    resolution_document,
):
    treatment, payload = resolution_rat
    document, _, lia = context
    async with api.client_for(client_a, org_a_id) as client:
        created = await client.post(
            f"/licitud/treatments/{treatment}/assessments",
            json={**payload, "eipd_resolution_assessment": resolution_document},
        )
        assert created.status_code == 201
        original = created.json()
        bound = original["eipd_resolution_assessment"]
        assert bound["context_binding"]["binding_version"] == 1
        url = f"/licitud/treatments/{treatment}/assessments/{original['id']}"
        changed = await client.patch(
            url,
            json={
                "research_assessment": document,
                "legal_basis": "interes_legitimo_art13d",
                "lia_assessment": lia,
            },
        )
        assert changed.status_code == 200
        assert changed.json()["eipd_resolution_assessment"] == bound
        ready = await client.get(url + "/readiness")
        assert ready.status_code == 200, ready.text
        assert "asociacion_investigacion_no_cubierta" in {
            i["code"] for i in ready.json()["eipd_controls_v3"]["resolution"]["issues"]
        }
        rebound = await client.patch(
            url, json={"eipd_resolution_assessment": resolution_document}
        )
        assert rebound.status_code == 200
        assert (
            rebound.json()["eipd_resolution_assessment"]["context_binding"][
                "binding_version"
            ]
            == 2
        )


async def test_client_binding_is_rejected(
    client_a, resolution_rat, org_a_id, resolution_document
):
    treatment, payload = resolution_rat
    injected = dict(
        resolution_document,
        context_binding={"binding_version": 2, "context_hash": "a" * 64},
    )
    async with api.client_for(client_a, org_a_id) as client:
        collection = f"/licitud/treatments/{treatment}/assessments"
        assert (
            await client.post(
                collection, json={**payload, "eipd_resolution_assessment": injected}
            )
        ).status_code == 422
        created = await client.post(collection, json=payload)
        assert created.status_code == 201
        assert (
            await client.patch(
                collection + "/" + created.json()["id"],
                json={"eipd_resolution_assessment": injected},
            )
        ).status_code == 422


async def test_declared_research_without_document_uses_v2(
    client_a,
    resolution_rat,
    org_a_id,
    negative_controls,
    resolution_document,
):
    treatment, payload = resolution_rat
    special = deepcopy(negative_controls["special_conditions"])
    for declaration in special["declarations"]:
        if (
            declaration["question_id"]
            == "fines_historicos_estadisticos_cientificos_investigacion"
        ):
            declaration["answer"] = "si"
    async with api.client_for(client_a, org_a_id) as client:
        created = await client.post(
            f"/licitud/treatments/{treatment}/assessments",
            json={
                **payload,
                "special_conditions": special,
                "eipd_resolution_assessment": resolution_document,
            },
        )
        assert created.status_code == 201, created.text
        original = created.json()
        assert original["research_assessment"] is None
        assert (
            original["eipd_resolution_assessment"]["context_binding"]["binding_version"]
            == 2
        )
        url = f"/licitud/treatments/{treatment}/assessments/{original['id']}"
        ready = await client.get(url + "/readiness")
        assert ready.status_code == 200, ready.text
        controls = ready.json()["eipd_controls_v3"]
        assert controls is not None and not controls["can_confirm"]
        assert "expediente_ausente" in {
            i["code"] for i in controls["preparation_issues"]
        }
        assert (await client.get(url)).json() == original


async def test_confirmed_v2_cannot_be_patched(
    client_a,
    resolution_rat,
    org_a_id,
    _session_factory,
    resolution_document,
):
    treatment, payload = resolution_rat
    async with api.client_for(client_a, org_a_id) as client:
        created = await client.post(
            f"/licitud/treatments/{treatment}/assessments",
            json={
                **payload,
                "research_assessment": {"purpose_type": "cientifico"},
                "eipd_resolution_assessment": resolution_document,
            },
        )
        assert created.status_code == 201
        original = created.json()
        async with _session_factory() as db:
            await db.execute(
                text(
                    "UPDATE legal_assessments SET status='confirmado', confirmed_at=now(), confirmed_by=created_by WHERE id=:id"
                ),
                {"id": UUID(original["id"])},
            )
            await db.commit()
        url = f"/licitud/treatments/{treatment}/assessments/{original['id']}"
        for value in (None, resolution_document):
            assert (
                await client.patch(url, json={"eipd_resolution_assessment": value})
            ).status_code == 409
        after = (await client.get(url)).json()
        assert (
            after["eipd_resolution_assessment"]
            == original["eipd_resolution_assessment"]
        )
        assert after["status"] == "confirmado"
