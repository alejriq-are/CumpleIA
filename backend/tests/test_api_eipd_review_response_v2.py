"""Respuesta versionada con identidad persistida y frontera de tenant."""

from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import event, text, update

from app.db.models import (
    EipdResolutionReview,
    Membership,
    Subscription,
    SubscriptionStatus,
    UserRole,
)
from app.main import app
from app.schemas.licitud import EipdResolutionReviewOutV2
from tests import test_api_eipd_negative_review_v2 as cases

explicit_review_policy = cases.explicit_review_policy
rat_m3 = cases.rat_m3
resolution_rat = cases.resolution_rat


@pytest.mark.parametrize("decision", ["requiere_cambios", "no_continuar"])
async def test_versioned_write_and_read_identical_persisted_metadata(
    client_a,
    resolution_rat,
    org_a_id,
    org_b_id,
    _session_factory,
    _app_engine,
    decision,
):
    async with cases.api.client_for(client_a, org_a_id) as client:
        url, original = await cases.create(client, resolution_rat)
        reviews = url + "/eipd-resolution/reviews"
        response = await client.post(reviews + "/v2", json=cases.request(decision))
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["response_schema_version"] == 2
        assert body["review_context_metadata"]["resolution_binding_version"] == 2
        assert body["review_context_metadata"]["context_hash"] == body["context_hash"]
        assert body["policy_hash"] is not None
        event_url = reviews + "/" + body["id"] + "/v2"
        statements = []

        def record(_conn, _cursor, statement, _params, _ctx, _many):
            statements.append(statement)

        event.listen(_app_engine.sync_engine, "before_cursor_execute", record)
        try:
            read = await client.get(event_url)
        finally:
            event.remove(_app_engine.sync_engine, "before_cursor_execute", record)
        assert read.status_code == 200 and read.json() == body
        assert not any(
            s.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
            for s in statements
        )
        assert (
            await client.get(event_url, headers={"X-Organization-Id": str(org_b_id)})
        ).status_code == 403
        assert (
            await client.get(reviews + "/" + str(uuid4()) + "/v2")
        ).status_code == 404
        assert (
            await client.patch(
                url, json={"research_assessment": {"purpose_type": "estadistico"}}
            )
        ).status_code == 200
        assert (await client.get(event_url)).json() == body
        ready = (await client.get(url + "/readiness")).json()["eipd_controls_v3"]
        assert (
            ready["review_context_metadata_status"] == "obsoleta"
            and not ready["can_confirm"]
        )
        assert (
            await client.post(reviews + "/v2", json=cases.request("continuar"))
        ).status_code == 409
        assert len(await cases.rows(_session_factory, original["id"])) == 1
        for change in (
            {"response_schema_version": 99},
            {"approved": True},
            {"policy_hash": None},
            {"context_hash": "a" * 64},
        ):
            with pytest.raises(ValidationError):
                EipdResolutionReviewOutV2.model_validate(dict(body, **change))


async def test_historical_route_unchanged_and_metadata_not_inferred(
    client_a, resolution_rat, org_a_id
):
    async with cases.api.client_for(client_a, org_a_id) as client:
        tid, payload = resolution_rat
        response = await client.post(
            f"/licitud/treatments/{tid}/assessments",
            json={
                **payload,
                "eipd_resolution_assessment": {"document_reference": "TEST: V1-158"},
            },
        )
        assert response.status_code == 201
        original = response.json()
        reviews = f"/licitud/treatments/{tid}/assessments/{original['id']}/eipd-resolution/reviews"
        written = await client.post(reviews, json=cases.request())
        assert written.status_code == 201, written.text
        historical = written.json()
        assert (
            "response_schema_version" not in historical
            and "review_context_metadata" not in historical
        )
        read = await client.get(reviews + "/" + historical["id"] + "/v2")
        assert read.status_code == 200, read.text
        body = read.json()
        assert (
            body["review_context_metadata"] is None
            and body["response_schema_version"] == 2
        )
        assert all(body[k] == v for k, v in historical.items())
        assert body["policy_hash"] is not None


async def test_versioned_openapi_keeps_historical_response_contract():
    schema = app.openapi()
    schemas = schema["components"]["schemas"]
    assert schemas["EipdResolutionReviewOutV2"]["additionalProperties"] is False
    assert (
        "review_context_metadata" not in schemas["EipdResolutionReviewIn"]["properties"]
    )
    paths = schema["paths"]
    path = "/licitud/treatments/{treatment_id}/assessments/{assessment_id}/eipd-resolution/reviews"
    assert paths[path]["post"]["responses"]["201"]["content"]["application/json"][
        "schema"
    ]["$ref"].endswith("/EipdResolutionReviewOut")
    assert paths[path + "/v2"]["post"]["responses"]["201"]["content"][
        "application/json"
    ]["schema"]["$ref"].endswith("/EipdResolutionReviewOutV2")


async def test_old_event_identity_is_not_inferred_and_confirmed_parent_is_readable(
    client_a, resolution_rat, org_a_id, profile_a_id, _session_factory
):
    async with cases.api.client_for(client_a, org_a_id) as client:
        url, original = await cases.create(client, resolution_rat)
        reviews = url + "/eipd-resolution/reviews"
        written = await client.post(reviews + "/v2", json=cases.request())
        assert written.status_code == 201
        current = written.json()
        async with _session_factory() as db:
            historical = EipdResolutionReview(
                organization_id=org_a_id,
                assessment_id=UUID(original["id"]),
                created_by=profile_a_id,
                decision="no_continuar",
                rationale="TEST: historia sin identidad",
                review_reference="TEST: anterior158",
                document_hash=current["document_hash"],
                context_hash=current["context_hash"],
            )
            db.add(historical)
            await db.flush()
            rid = str(historical.id)
            # Confirmed-state fixture exclusively in isolated DB, never action bypass.
            await db.execute(
                text(
                    "UPDATE legal_assessments SET status='confirmado', confirmed_at=now(), confirmed_by=created_by WHERE id=:id"
                ),
                {"id": UUID(original["id"])},
            )
            await db.commit()
        read = await client.get(reviews + "/" + rid + "/v2")
        assert read.status_code == 200, read.text
        body = read.json()
        assert body["review_context_metadata"] is None
        assert (
            body["policy_version"] is None
            and body["policy_hash"] is None
            and body["policy_reference"] is None
        )
        assert (
            await client.get(reviews + "/" + current["id"] + "/v2")
        ).json() == current
        assert (
            await client.get(
                reviews.replace(original["id"], str(uuid4())) + "/" + rid + "/v2"
            )
        ).status_code == 404


async def test_versioned_permissions_and_subscription(
    client_a, resolution_rat, org_a_id, profile_a_id, _session_factory
):
    async with cases.api.client_for(client_a, org_a_id) as client:
        url, original = await cases.create(client, resolution_rat)
        reviews = url + "/eipd-resolution/reviews"
        response = await client.post(reviews + "/v2", json=cases.request())
        assert response.status_code == 201
        event_url = reviews + "/" + response.json()["id"] + "/v2"
        where = (Membership.organization_id == org_a_id) & (
            Membership.profile_id == profile_a_id
        )
        async with _session_factory() as db:
            await db.execute(
                update(Membership).where(where).values(role=UserRole.viewer)
            )
            await db.commit()
        try:
            assert (await client.get(event_url)).status_code == 200
            assert (
                await client.post(reviews + "/v2", json=cases.request())
            ).status_code == 403
        finally:
            async with _session_factory() as db:
                await db.execute(
                    update(Membership).where(where).values(role=UserRole.owner)
                )
                await db.commit()
        async with _session_factory() as db:
            await db.execute(
                update(Subscription)
                .where(Subscription.organization_id == org_a_id)
                .values(status=SubscriptionStatus.suspended)
            )
            await db.commit()
        try:
            assert (await client.get(event_url)).status_code == 402
            assert (
                await client.post(reviews + "/v2", json=cases.request())
            ).status_code == 402
        finally:
            async with _session_factory() as db:
                await db.execute(
                    update(Subscription)
                    .where(Subscription.organization_id == org_a_id)
                    .values(status=SubscriptionStatus.active)
                )
                await db.commit()
        assert len(await cases.rows(_session_factory, original["id"])) == 1
