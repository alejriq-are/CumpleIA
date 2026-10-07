from copy import deepcopy
from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy import select, update

from app.db.models import EipdResolutionReview, Treatment, TreatmentPurpose
from app.services.eipd_resolution import (
    bind_eipd_resolution_v1,
    build_eipd_resolution_document_hash_v1,
    derive_eipd_resolution_review_state_v1,
)
from tests import test_api_eipd_resolution as api_fixtures
from tests import test_services_eipd_resolution as service_fixtures
from tests.eipd_selected_policy_fixtures import (
    explicit_review_policy as explicit_review_policy,
)

rat_m3 = api_fixtures.rat_m3
resolution_rat = api_fixtures.resolution_rat
complete_payload = api_fixtures.complete_payload
complete_resolution = service_fixtures.complete_resolution


def review_payload(document, decision="continuar"):
    return dict(
        id=str(UUID(int=1)),
        organization_id=str(UUID(int=2)),
        assessment_id=str(UUID(int=3)),
        created_by=str(UUID(int=4)),
        decision=decision,
        rationale="Revision fundada",
        review_reference="REV1",
        document_hash=build_eipd_resolution_document_hash_v1(document),
        context_hash=document.context_binding.context_hash,
        created_at="2026-10-06T00:00:00Z",
    )


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
def test_review_current_does_not_approve(complete_resolution, decision):
    doc, ctx = complete_resolution
    bound = bind_eipd_resolution_v1(doc, ctx)
    review = review_payload(bound, decision)
    original = deepcopy((bound.model_dump(mode="json"), ctx, review))
    state = derive_eipd_resolution_review_state_v1(bound, ctx, review)
    assert state.review_status == "vigente" and state.latest_review.decision == decision
    assert (bound.model_dump(mode="json"), ctx, review) == original


@pytest.mark.parametrize(
    "mode",
    [
        "no_document",
        "no_context",
        "document_changed",
        "context_changed",
        "hash_mismatch",
        "unbound",
    ],
)
def test_review_stale_retains_latest(complete_resolution, mode):
    doc, ctx = complete_resolution
    bound = bind_eipd_resolution_v1(doc, ctx)
    review = review_payload(bound)
    if mode == "no_document":
        bound = None
    elif mode == "no_context":
        ctx = None
    elif mode == "document_changed":
        bound.notes = "Modificado"
    elif mode == "context_changed":
        ctx["consent_assessment"] = {}
    elif mode == "hash_mismatch":
        review["context_hash"] = "a" * 64
    else:
        bound.context_binding = None
    state = derive_eipd_resolution_review_state_v1(bound, ctx, review)
    assert state.review_status == "obsoleta"
    assert state.latest_review.id == UUID(int=1)


def test_no_review_does_not_create_event(complete_resolution):
    doc, ctx = complete_resolution
    state = derive_eipd_resolution_review_state_v1(
        bind_eipd_resolution_v1(doc, ctx), ctx, None
    )
    assert state.review_status == "sin_revision" and state.latest_review is None


def api_document(template, response):
    doc = deepcopy(template)
    doc["purpose_description"] = response["rat_context_snapshot"]["purpose"]
    doc["scope"] = {
        "data_category_codes": [
            c["category_code"]
            for c in response["rat_context_snapshot"]["data_categories"]
        ],
        "data_subject_codes": [
            c["category_code"]
            for c in response["rat_context_snapshot"]["data_subjects"]
        ],
    }
    doc["completed_on"] = "1900-01-01"
    doc["official_sources"]["checked_on"] = "1900-01-01"
    return doc


async def seed_review(
    factory, data, org, actor, decision="continuar", event_id=None, timestamp=None
):
    doc = data["eipd_resolution_assessment"]
    async with factory() as db:
        values = dict(
            organization_id=org,
            assessment_id=UUID(data["id"]),
            created_by=actor,
            decision=decision,
            rationale="Fixture de revision",
            review_reference="REV1",
            document_hash=build_eipd_resolution_document_hash_v1(doc),
            context_hash=doc["context_binding"]["context_hash"],
        )
        if event_id:
            values["id"] = event_id
        if timestamp:
            values["created_at"] = timestamp
        event = EipdResolutionReview(**values)
        db.add(event)
        await db.commit()
        return str(event.id)


async def test_readiness_prepared_review_separate_no_writes(
    client_a,
    resolution_rat,
    complete_payload,
    complete_resolution,
    org_a_id,
    profile_a_id,
    _session_factory,
):
    tid, payload = resolution_rat
    url = f"/licitud/treatments/{tid}/assessments"
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert created.status_code == 201
        detail = url + "/" + created.json()["id"]
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["eipd_resolution"] is None
        assert ready["eipd_resolution_review"] == {
            "review_status": "sin_revision",
            "latest_review": None,
        }
        doc = api_document(complete_resolution[0], created.json())
        saved = await client.patch(detail, json={"eipd_resolution_assessment": doc})
        assert saved.status_code == 200
        before = saved.json()
        ready = (await client.get(detail + "/readiness")).json()
        assert (
            ready["eipd_resolution"]["result"] == "completo"
            and ready["eipd_resolution"]["context_current"]
        )
        assert ready["eipd_resolution_review"]["review_status"] == "sin_revision"
        for decision in ["continuar", "requiere_cambios", "no_continuar"]:
            event_id = await seed_review(
                _session_factory, before, org_a_id, profile_a_id, decision
            )
            current = (await client.get(detail + "/readiness")).json()
            assert current["eipd_resolution_review"]["review_status"] == "vigente"
            assert (
                current["eipd_resolution_review"]["latest_review"]["decision"]
                == decision
            )
            assert current["eipd_resolution_review"]["latest_review"]["id"] == event_id
            rejected = await client.post(detail + "/confirm")
            assert rejected.status_code == 409
            assert (
                rejected.json()["detail"]["confirmation_blockers"]
                == current["confirmation_blockers"]
            )
            assert (await client.get(detail)).json() == before
        changed = await client.patch(
            detail, json={"eipd_resolution_assessment": {**doc, "notes": "Cambio"}}
        )
        assert changed.status_code == 200
        current = (await client.get(detail + "/readiness")).json()
        assert current["eipd_resolution"]["result"] == "completo"
        assert current["eipd_resolution_review"]["review_status"] == "obsoleta"
        removed = await client.patch(detail, json={"eipd_resolution_assessment": None})
        assert removed.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["eipd_resolution"] is None
        assert ready["eipd_resolution_review"]["review_status"] == "obsoleta"
        assert (
            ready["eipd_resolution_review"]["latest_review"]["decision"]
            == "no_continuar"
        )
        async with _session_factory() as db:
            assert (
                len(
                    (
                        await db.scalars(
                            select(EipdResolutionReview).where(
                                EipdResolutionReview.assessment_id == UUID(before["id"])
                            )
                        )
                    ).all()
                )
                == 3
            )
        assert (await client.get(detail)).json() == removed.json()


@pytest.mark.parametrize(
    "mutation", ["consent", "special", "screening", "rat", "rat_unavailable"]
)
async def test_readiness_uses_current_context_not_stored(
    client_a,
    resolution_rat,
    complete_payload,
    complete_resolution,
    org_a_id,
    profile_a_id,
    _session_factory,
    mutation,
):
    tid, payload = resolution_rat
    url = f"/licitud/treatments/{tid}/assessments"
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        detail = url + "/" + created.json()["id"]
        doc = api_document(complete_resolution[0], created.json())
        saved = await client.patch(detail, json={"eipd_resolution_assessment": doc})
        assert saved.status_code == 200
        event_id = await seed_review(
            _session_factory, saved.json(), org_a_id, profile_a_id
        )
        before = saved.json()
        if mutation in ("rat", "rat_unavailable"):
            async with _session_factory() as db:
                stmt = (
                    update(Treatment)
                    .where(Treatment.id == tid)
                    .values(retention_rule="10 años")
                    if mutation == "rat"
                    else update(TreatmentPurpose)
                    .where(TreatmentPurpose.treatment_id == tid)
                    .values(purpose="Otra finalidad")
                )
                await db.execute(stmt)
                await db.commit()
        else:
            field = {
                "consent": "consent_assessment",
                "special": "special_conditions",
                "screening": "eipd_screening",
            }[mutation]
            changed_doc = deepcopy(
                payload[field] if field in payload else complete_payload
            )
            changed_doc["notes"] = "Cambio de contexto"
            saved = await client.patch(detail, json={field: changed_doc})
            assert saved.status_code == 200
            before = saved.json()
        ready_response = await client.get(detail + "/readiness")
        assert ready_response.status_code == 200, ready_response.text
        ready = ready_response.json()
        assert not ready["eipd_resolution"]["context_current"]
        assert ready["eipd_resolution_review"]["review_status"] == "obsoleta"
        assert ready["eipd_resolution_review"]["latest_review"]["id"] == event_id
        assert (await client.get(detail)).json() == before
        if mutation != "rat_unavailable":
            rebound = await client.patch(
                detail, json={"eipd_resolution_assessment": doc}
            )
            assert rebound.status_code == 200
            ready = (await client.get(detail + "/readiness")).json()
            assert ready["eipd_resolution"]["context_current"]
            assert ready["eipd_resolution_review"]["review_status"] == "obsoleta"


async def test_latest_event_tie_order_does_not_select_old_continue(
    client_a,
    resolution_rat,
    complete_resolution,
    org_a_id,
    profile_a_id,
    _session_factory,
):
    tid, payload = resolution_rat
    url = f"/licitud/treatments/{tid}/assessments"
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(url, json=payload)
        detail = url + "/" + created.json()["id"]
        doc = api_document(complete_resolution[0], created.json())
        saved = await client.patch(detail, json={"eipd_resolution_assessment": doc})
        timestamp = datetime(2026, 10, 6, tzinfo=UTC)
        await seed_review(
            _session_factory,
            saved.json(),
            org_a_id,
            profile_a_id,
            "requiere_cambios",
            UUID(int=12),
            timestamp,
        )
        await seed_review(
            _session_factory,
            saved.json(),
            org_a_id,
            profile_a_id,
            "continuar",
            UUID(int=11),
            timestamp,
        )
        ready = (await client.get(detail + "/readiness")).json()
        assert (
            ready["eipd_resolution_review"]["latest_review"]["decision"]
            == "requiere_cambios"
        )
        assert ready["eipd_resolution_review"]["latest_review"]["id"] == str(
            UUID(int=12)
        )


async def test_positive_screening_without_resolution_exposes_missing_document(
    client_a, resolution_rat, org_a_id, org_b_id
):
    tid, payload = resolution_rat
    payload = deepcopy(payload)
    payload["eipd_screening"]["answers"][0]["answer"] = "si"
    url = f"/licitud/treatments/{tid}/assessments"
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201
        detail = url + "/" + created.json()["id"]
        response = await client.get(detail + "/readiness")
        assert response.status_code == 200
        ready = response.json()
        assert ready["eipd_resolution"]["result"] == "incompleto"
        assert any(
            i["code"] == "expediente_ausente"
            for i in ready["eipd_resolution"]["issues"]
        )
        assert ready["eipd"]["result"] != "sin_supuestos_declarados"
        assert ready["eipd_resolution_review"]["review_status"] == "sin_revision"
        assert (await client.get(detail)).json() == created.json()
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
