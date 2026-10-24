"""Registro negativo V3 ficticio, aislamiento y locks reales sin activar EIPD."""

import asyncio
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, text

from app.db.models import EipdResolutionReview
from app.schemas.licitud import (
    EipdNegativeResolutionReviewInV3,
    LegalAssessmentRepresentationDraftUpdateV1,
)
from app.services import licitud
from tests import test_api_sensitive_representation as cases

explicit_review_policy = cases.explicit_review_policy
rat_m3 = cases.rat_m3
saved = cases.saved
pytestmark = pytest.mark.asyncio(loop_scope="session")


def payload(decision="requiere_cambios"):
    return dict(
        decision=decision,
        rationale="PRUEBA: material ficticio incompleto",
        review_reference="PRUEBA-NEGATIVA-V3",
    )


def client(state):
    return AsyncClient(
        transport=ASGITransport(app=state[2]),
        base_url="http://test",
        headers={"X-Organization-Id": str(state[3])},
    )


def url(state):
    return f"/licitud/treatments/{state[0]}/assessments/{state[1]['id']}"


@pytest.fixture
async def prepared(saved, _session_factory):
    async with client(saved) as http:
        response = await http.patch(url(saved), json={"eipd_resolution_assessment": {}})
        assert response.status_code == 200, response.text
    try:
        yield saved
    finally:
        async with _session_factory() as db:
            await db.execute(
                delete(EipdResolutionReview).where(
                    EipdResolutionReview.assessment_id == UUID(saved[1]["id"])
                )
            )
            await db.commit()


@pytest.mark.parametrize("decision", ["requiere_cambios", "no_continuar"])
async def test_negative_v3_records_server_identity_without_confirmation(
    prepared, decision
):
    async with client(prepared) as http:
        before = (await http.get(url(prepared))).json()
        response = await http.post(
            url(prepared) + "/eipd-resolution/reviews/v3", json=payload(decision)
        )
        assert response.status_code == 201, response.text
        event = response.json()
        assert event["decision"] == decision
        assert event["response_schema_version"] == 3
        assert event["organization_id"] == str(prepared[3])
        assert event["review_context_metadata"]["metadata_schema_version"] == 2
        assert (
            event["context_hash"]
            == before["eipd_resolution_assessment"]["context_binding"]["context_hash"]
        )
        assert (
            await http.get(url(prepared) + f"/eipd-resolution/reviews/{event['id']}/v3")
        ).json() == event
        assert (await http.get(url(prepared))).json() == before
        ready = await http.get(url(prepared) + "/readiness")
        assert ready.status_code == 200, ready.text
        assert ready.json()["eipd_controls_v4"]["can_confirm"] is False
        assert (await http.post(url(prepared) + "/confirm")).status_code == 409


@pytest.mark.parametrize(
    "case", ["positive", "injected", "foreign", "missing_parent", "stale"]
)
async def test_invalid_or_unauthorized_negative_never_records(
    prepared, _session_factory, case
):
    async with client(prepared) as http:
        body = payload()
        headers = {}
        endpoint = url(prepared)
        expected = 422
        if case == "positive":
            body["decision"] = "continuar"
        elif case == "injected":
            body["document_hash"] = "a" * 64
        elif case == "foreign":
            headers = {"X-Organization-Id": str(uuid4())}
            expected = 403
        elif case == "missing_parent":
            endpoint = endpoint.replace(prepared[1]["id"], str(uuid4()))
            expected = 404
        else:
            changed = await http.patch(
                endpoint,
                json={
                    "sensitive_representation_assessment": {
                        **cases.DOCUMENT,
                        "notes": "PRUEBA: cambio",
                    }
                },
            )
            assert changed.status_code == 200, changed.text
            expected = 409
        response = await http.post(
            endpoint + "/eipd-resolution/reviews/v3", json=body, headers=headers
        )
        assert response.status_code == expected, response.text
    async with _session_factory() as db:
        assert not (
            await db.execute(
                text("SELECT id FROM eipd_resolution_reviews WHERE assessment_id=:id"),
                {"id": UUID(prepared[1]["id"])},
            )
        ).all()


@pytest.mark.parametrize("change", ["stale", "rebind", "withdraw"])
@pytest.mark.parametrize("commit_change", [True, False])
async def test_waiting_v3_reloads_material_after_commit_or_rollback(
    prepared,
    _app_session_factory,
    _session_factory,
    auth_a_id,
    profile_a_id,
    change,
    commit_change,
):
    tid, original, _, org = prepared
    aid = UUID(original["id"])
    async with _app_session_factory() as holder, _app_session_factory() as waiter:
        await cases.rls._set_auth_user(holder, auth_a_id)
        await cases.rls._set_auth_user(waiter, auth_a_id)
        changes = {
            "sensitive_representation_assessment": {
                **cases.DOCUMENT,
                "notes": "PRUEBA: concurrencia",
            }
        }
        if change == "rebind":
            changes["eipd_resolution_assessment"] = {}
        elif change == "withdraw":
            changes = {"eipd_resolution_assessment": None}
        updated = await licitud.update_legal_assessment_draft_v1(
            holder,
            org,
            tid,
            aid,
            profile_a_id,
            LegalAssessmentRepresentationDraftUpdateV1.model_validate(changes),
        )
        expected = updated.eipd_resolution_assessment
        pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(
            licitud.record_eipd_negative_review_v3(
                waiter,
                org,
                tid,
                aid,
                profile_a_id,
                EipdNegativeResolutionReviewInV3.model_validate(payload()),
            )
        )
        try:
            await cases.locks.blocked(holder, pid)
            assert not task.done()
            if commit_change:
                await holder.commit()
            else:
                await holder.rollback()
            if commit_change and change != "rebind":
                with pytest.raises(HTTPException) as exc:
                    await asyncio.wait_for(task, 5)
                assert exc.value.status_code == 409
            else:
                event = await asyncio.wait_for(task, 5)
                assert event.review_context_metadata["resolution_binding_version"] == 3
                if commit_change:
                    assert (
                        event.context_hash
                        == expected["context_binding"]["context_hash"]
                    )
                # Transaction rollback must remove a newly flushed event.
                await waiter.rollback()
        finally:
            await cases.locks.stop(task)
            await holder.rollback()
            await waiter.rollback()
    async with _session_factory() as db:
        assert not (
            await db.execute(
                text("SELECT id FROM eipd_resolution_reviews WHERE assessment_id=:id"),
                {"id": aid},
            )
        ).all()


@pytest.mark.parametrize("restriction", ["viewer", "subscription"])
async def test_negative_v3_requires_edit_permission_and_active_subscription(
    prepared, _session_factory, profile_a_id, restriction
):
    async with _session_factory() as db:
        if restriction == "viewer":
            previous = await db.scalar(
                text(
                    "SELECT role::text FROM memberships WHERE organization_id=:org AND profile_id=:actor"
                ),
                {"org": prepared[3], "actor": profile_a_id},
            )
            await db.execute(
                text(
                    "UPDATE memberships SET role='viewer' WHERE organization_id=:org AND profile_id=:actor"
                ),
                {"org": prepared[3], "actor": profile_a_id},
            )
        else:
            previous = await db.scalar(
                text(
                    "SELECT status::text FROM subscriptions WHERE organization_id=:org"
                ),
                {"org": prepared[3]},
            )
            await db.execute(
                text(
                    "UPDATE subscriptions SET status='suspended' WHERE organization_id=:org"
                ),
                {"org": prepared[3]},
            )
        await db.commit()
    try:
        async with client(prepared) as http:
            response = await http.post(
                url(prepared) + "/eipd-resolution/reviews/v3", json=payload()
            )
            assert response.status_code == (
                403 if restriction == "viewer" else 402
            ), response.text
    finally:
        async with _session_factory() as db:
            if restriction == "viewer":
                await db.execute(
                    text(
                        "UPDATE memberships SET role=:previous WHERE organization_id=:org AND profile_id=:actor"
                    ),
                    {"previous": previous, "org": prepared[3], "actor": profile_a_id},
                )
            else:
                await db.execute(
                    text(
                        "UPDATE subscriptions SET status=:previous WHERE organization_id=:org"
                    ),
                    {"previous": previous, "org": prepared[3]},
                )
            await db.commit()


async def test_child_document_does_not_rewrite_or_promote_historical_review(
    prepared, explicit_review_policy, _session_factory
):
    async with client(prepared) as http:
        response = await http.post(
            url(prepared) + "/eipd-resolution/reviews/v3", json=payload()
        )
        assert response.status_code == 201, response.text
        event = response.json()
        read_url = url(prepared) + f"/eipd-resolution/reviews/{event['id']}/v3"
        historical = await http.get(read_url)
        assert historical.status_code == 200, historical.text
        changed = await http.patch(
            url(prepared),
            json={
                "child_adolescent_assessment": {
                    "declared_groups": ["ninos_ninas"],
                    "notes": "PRUEBA: infancia ficticia",
                }
            },
        )
        assert changed.status_code == 200, changed.text
        readiness = await http.get(url(prepared) + "/readiness")
        assert readiness.status_code == 200, readiness.text
        body = readiness.json()
        assert body["child_adolescent_context_coverage"] == "pendiente"
        assert body["eipd_resolution_review"]["review_status"] == "obsoleta"
        assert all(
            body[field] is None
            for field in (
                "eipd_controls",
                "eipd_controls_v2",
                "eipd_controls_v3",
                "eipd_controls_v4",
            )
        )
        assert (await http.get(read_url)).json() == historical.json()
        rejected = await http.post(
            url(prepared) + "/eipd-resolution/reviews/v3", json=payload()
        )
        assert rejected.status_code == 409
        assert (
            rejected.json()["detail"]["code"]
            == "resolucion_eipd_infancia_asociacion_pendiente"
        )
    async with _session_factory() as db:
        assert (
            await db.scalar(
                text(
                    "SELECT count(*) FROM eipd_resolution_reviews WHERE assessment_id=:id"
                ),
                {"id": UUID(prepared[1]["id"])},
            )
            == 1
        )
