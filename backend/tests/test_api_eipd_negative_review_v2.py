"""Negativas V2 via HTTP real, base aislada y sin activar EIPD."""

from uuid import UUID

import pytest
from fastapi import HTTPException
from sqlalchemy import select, text

from app.db.models import EipdResolutionReview
from app.services import licitud as service
from app.services.eipd_review_metadata import read_eipd_review_context_metadata_v1
from tests import test_api_eipd_resolution as api
from tests.eipd_selected_policy_fixtures import (
    explicit_review_policy as explicit_review_policy,
)

rat_m3 = api.rat_m3
resolution_rat = api.resolution_rat


async def create(client, resolution_rat):
    tid, payload = resolution_rat
    response = await client.post(
        f"/licitud/treatments/{tid}/assessments",
        json={
            **payload,
            "research_assessment": {"purpose_type": "cientifico"},
            "eipd_resolution_assessment": {"document_reference": "TEST: EIPD154"},
        },
    )
    assert response.status_code == 201, response.text
    value = response.json()
    return f"/licitud/treatments/{tid}/assessments/{value['id']}", value


def request(decision="requiere_cambios"):
    return dict(
        decision=decision,
        rationale="TEST: revision fundada",
        review_reference="TEST: REV154",
    )


async def rows(factory, aid):
    async with factory() as db:
        return list(
            (
                await db.scalars(
                    select(EipdResolutionReview).where(
                        EipdResolutionReview.assessment_id == UUID(aid)
                    )
                )
            ).all()
        )


@pytest.mark.parametrize("decision", ["requiere_cambios", "no_continuar"])
@pytest.mark.parametrize("research_present", [True, False])
async def test_negative_persists_metadata_and_keeps_barriers(
    client_a,
    resolution_rat,
    org_a_id,
    org_b_id,
    profile_a_id,
    _session_factory,
    decision,
    research_present,
):
    async with api.client_for(client_a, org_a_id) as client:
        url, original = await create(client, resolution_rat)
        if not research_present:
            patched = await client.patch(
                url,
                json={
                    "research_assessment": None,
                    "eipd_resolution_assessment": {
                        "document_reference": "TEST: EIPD154"
                    },
                },
            )
            assert patched.status_code == 200, patched.text
            original = patched.json()
        denied = await client.post(
            url + "/eipd-resolution/reviews",
            json=request(decision),
            headers={"X-Organization-Id": str(org_b_id)},
        )
        assert denied.status_code == 403
        assert (
            await client.post(
                url + "/eipd-resolution/reviews",
                json={**request(decision), "review_context_metadata": {}},
            )
        ).status_code == 422
        for _ in range(2):
            response = await client.post(
                url + "/eipd-resolution/reviews", json=request(decision)
            )
            assert response.status_code == 201, response.text
            assert response.json()["created_by"] == str(profile_a_id)
        events = await rows(_session_factory, original["id"])
        assert len(events) == 2 and len({e.id for e in events}) == 2
        for event in events:
            metadata = read_eipd_review_context_metadata_v1(event)
            assert metadata.resolution_binding_version == 2
            assert metadata.research_coverage == "contexto_v2"
            assert (metadata.research_material_hash is not None) == research_present
            assert event.policy_hash is not None
        ready = (await client.get(url + "/readiness")).json()["eipd_controls_v3"]
        assert ready["review_context_metadata_status"] == "vigente"
        assert ready["review_state"]["latest_review"]["decision"] == decision
        assert not ready["can_confirm"]
        assert "decision_no_continuar" in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert (await client.post(url + "/confirm")).status_code in (400, 409)
        assert (
            await client.post(
                url + "/eipd-resolution/reviews", json=request("continuar")
            )
        ).status_code == 409
        assert (await client.get(url)).json() == original
        assert len(await rows(_session_factory, original["id"])) == 2


@pytest.mark.parametrize("change", ["research", "status", "rat"])
async def test_rejected_material_has_no_event(
    client_a, resolution_rat, org_a_id, _session_factory, change
):
    async with api.client_for(client_a, org_a_id) as client:
        url, original = await create(client, resolution_rat)
        if change == "research":
            assert (
                await client.patch(
                    url, json={"research_assessment": {"purpose_type": "estadistico"}}
                )
            ).status_code == 200
        else:
            async with _session_factory() as db:
                if change == "status":
                    await db.execute(
                        text(
                            "UPDATE legal_assessments SET status='confirmado', confirmed_at=now(), confirmed_by=created_by WHERE id=:id"
                        ),
                        {"id": UUID(original["id"])},
                    )
                else:
                    await db.execute(
                        text(
                            "UPDATE legal_assessments SET rat_context_hash=:hash WHERE id=:id"
                        ),
                        {"hash": "a" * 64, "id": UUID(original["id"])},
                    )
                await db.commit()
        before = (await client.get(url)).json()
        response = await client.post(url + "/eipd-resolution/reviews", json=request())
        assert response.status_code == 409, response.text
        if change != "status":
            detail = response.json()["detail"]
            assert detail["evaluation_version"] == 3
            assert (
                "asociacion_obsoleta"
                if change == "research"
                else "contexto_rat_desactualizado"
            ) in {i["code"] for i in detail["issues_v3"]}
        assert not await rows(_session_factory, original["id"])
        assert (await client.get(url)).json() == before


async def test_flush_then_failure_rolls_back_event_and_metadata(
    client_a, resolution_rat, org_a_id, _session_factory, monkeypatch
):
    async with api.client_for(client_a, org_a_id) as client:
        url, original = await create(client, resolution_rat)
        real = service.record_eipd_resolution_review_v1

        async def fail_after_flush(*args, **kwargs):
            await real(*args, **kwargs)
            raise HTTPException(status_code=409, detail="TEST: fallo despues de flush")

        monkeypatch.setattr(
            service, "record_eipd_resolution_review_v1", fail_after_flush
        )
        response = await client.post(url + "/eipd-resolution/reviews", json=request())
        assert response.status_code == 409
        assert not await rows(_session_factory, original["id"])
        assert (await client.get(url)).json() == original
