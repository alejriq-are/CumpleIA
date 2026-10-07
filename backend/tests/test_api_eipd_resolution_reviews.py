"""Accion de revision humana autenticada, sin desbloquear confirmacion."""

from copy import deepcopy
from uuid import uuid4

import pytest
from sqlalchemy import select, update

from app.db.models import (
    EipdResolutionReview,
    Membership,
    Subscription,
    SubscriptionStatus,
    UserRole,
)
from app.services.eipd_resolution import build_eipd_resolution_document_hash_v1
from tests import test_api_eipd_resolution as fixtures
from tests.eipd_selected_policy_fixtures import (
    explicit_review_policy as explicit_review_policy,
)

rat_m3 = fixtures.rat_m3
resolution_rat = fixtures.resolution_rat
complete_payload = fixtures.complete_payload


def review(decision="requiere_cambios"):
    return {
        "decision": decision,
        "rationale": "Revision humana fundada",
        "review_reference": "REV1",
    }


async def setup(client, resolution_rat, document=True):
    tid, payload = resolution_rat
    data = deepcopy(payload)
    if document:
        data["eipd_resolution_assessment"] = {"document_reference": "EIPD1"}
    response = await client.post(f"/licitud/treatments/{tid}/assessments", json=data)
    assert response.status_code == 201, response.text
    detail = f"/licitud/treatments/{tid}/assessments/{response.json()['id']}"
    return detail, response.json()


async def events(factory, assessment_id):
    from uuid import UUID

    async with factory() as db:
        return list(
            (
                await db.scalars(
                    select(EipdResolutionReview).where(
                        EipdResolutionReview.assessment_id == UUID(assessment_id)
                    )
                )
            ).all()
        )


async def test_append_only_review_server_fields_and_readonly(
    client_a, resolution_rat, org_a_id, profile_a_id, _session_factory
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(client, resolution_rat)
        url = detail + "/eipd-resolution/reviews"
        records = []
        for decision in ("requiere_cambios", "no_continuar"):
            response = await client.post(url, json=review(decision))
            assert response.status_code == 201, response.text
            event = response.json()
            assert event["created_by"] == str(profile_a_id)
            assert event["organization_id"] == str(org_a_id)
            assert event["assessment_id"] == original["id"]
            assert event["document_hash"] == build_eipd_resolution_document_hash_v1(
                original["eipd_resolution_assessment"]
            )
            assert (
                event["context_hash"]
                == original["eipd_resolution_assessment"]["context_binding"][
                    "context_hash"
                ]
            )
            assert event["created_at"] and event["id"]
            records.append(event)
        assert records[0]["id"] != records[1]["id"]
        assert (await client.get(detail)).json() == original
        state = (await client.get(detail + "/readiness")).json()[
            "eipd_resolution_review"
        ]
        assert state["review_status"] == "vigente"
        assert state["latest_review"] == records[-1]
        assert (await client.post(detail + "/confirm")).status_code in (400, 409)
        assert len(await events(_session_factory, original["id"])) == 2
        changed = await client.patch(
            detail, json={"eipd_resolution_assessment": {"document_reference": "EIPD2"}}
        )
        assert changed.status_code == 200
        state = (await client.get(detail + "/readiness")).json()[
            "eipd_resolution_review"
        ]
        assert state["review_status"] == "obsoleta"
        assert (await client.post(url, json=review("no_continuar"))).status_code == 201
        assert len(await events(_session_factory, original["id"])) == 3


@pytest.mark.parametrize("mode", ["missing", "obsolete", "continuar"])
async def test_rejection_has_no_write(
    client_a, resolution_rat, org_a_id, _session_factory, mode
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(
            client, resolution_rat, document=mode != "missing"
        )
        if mode == "obsolete":
            response = await client.patch(detail, json={"consent_assessment": {}})
            assert response.status_code == 200
            original = response.json()
        response = await client.post(
            detail + "/eipd-resolution/reviews",
            json=review("continuar" if mode == "continuar" else "no_continuar"),
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "revision_eipd_no_preparada"
        if mode == "continuar":
            codes = {i["code"] for i in response.json()["detail"]["issues"]}
            assert {
                "frontera_revision_no_validada",
                "fuentes_oficiales_no_verificadas",
            } <= codes
        assert (await client.get(detail)).json() == original
        assert not await events(_session_factory, original["id"])


@pytest.mark.parametrize(
    "field",
    [
        "created_by",
        "created_at",
        "context_hash",
        "document_hash",
        "organization_id",
        "assessment_id",
        "sources_verified",
    ],
)
async def test_metadata_forgery_rejected(
    client_a, resolution_rat, org_a_id, _session_factory, field
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(client, resolution_rat)
        response = await client.post(
            detail + "/eipd-resolution/reviews", json=review() | {field: "forged"}
        )
        assert response.status_code == 422
        assert not await events(_session_factory, original["id"])


async def test_auth_and_lookup_boundaries(
    client_a, resolution_rat, org_a_id, org_b_id, profile_a_id, _session_factory
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(client, resolution_rat)
        url = detail + "/eipd-resolution/reviews"
        assert (
            await client.post(
                url, json=review(), headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        assert (
            await client.post(url.replace(original["id"], str(uuid4())), json=review())
        ).status_code == 404
        where = (Membership.organization_id == org_a_id) & (
            Membership.profile_id == profile_a_id
        )
        async with _session_factory() as db:
            await db.execute(
                update(Membership).where(where).values(role=UserRole.viewer)
            )
            await db.commit()
        try:
            assert (await client.post(url, json=review())).status_code == 403
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
            assert (await client.post(url, json=review())).status_code == 402
        finally:
            async with _session_factory() as db:
                await db.execute(
                    update(Subscription)
                    .where(Subscription.organization_id == org_a_id)
                    .values(status=SubscriptionStatus.active)
                )
                await db.commit()
        assert not await events(_session_factory, original["id"])


async def test_confirmed_and_replaced_reject_review(
    client_a, resolution_rat, complete_payload, org_a_id, _session_factory
):
    tid, payload = resolution_rat
    async with fixtures.client_for(client_a, org_a_id) as client:
        data = dict(payload, consent_assessment=complete_payload)
        first = await client.post(f"/licitud/treatments/{tid}/assessments", json=data)
        assert first.status_code == 201
        detail = f"/licitud/treatments/{tid}/assessments/{first.json()['id']}"
        confirmed = await client.post(detail + "/confirm")
        assert confirmed.status_code == 200, confirmed.text
        assert (
            await client.post(detail + "/eipd-resolution/reviews", json=review())
        ).status_code == 409
        second = await client.post(f"/licitud/treatments/{tid}/assessments", json=data)
        assert second.status_code == 201
        second_url = f"/licitud/treatments/{tid}/assessments/{second.json()['id']}"
        assert (await client.post(second_url + "/confirm")).status_code == 200
        before = (await client.get(detail)).json()
        assert before["status"] == "reemplazado"
        assert (
            await client.post(detail + "/eipd-resolution/reviews", json=review())
        ).status_code == 409
        assert (await client.get(detail)).json() == before
        assert not await events(_session_factory, first.json()["id"])


@pytest.mark.parametrize("commit_change", [True, False])
@pytest.mark.parametrize("positive", [False, True])
async def test_rereads_document_after_series_lock(
    client_a,
    resolution_rat,
    org_a_id,
    profile_a_id,
    auth_a_id,
    _app_session_factory,
    _session_factory,
    commit_change,
    positive,
):
    import asyncio
    from uuid import UUID

    from fastapi import HTTPException
    from sqlalchemy import text

    from app.db.models import LegalAssessment, LegalAssessmentSeries
    from app.schemas.licitud import EipdResolutionReviewIn
    from app.services.licitud import record_eipd_resolution_review_v1

    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(client, resolution_rat)
    assessment_id = UUID(original["id"])
    tid = resolution_rat[0]
    async with _app_session_factory() as holder, _app_session_factory() as waiter:
        for session in (holder, waiter):
            await session.execute(
                text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
                {"sub": str(auth_a_id)},
            )
        row = await holder.scalar(
            select(LegalAssessment).where(LegalAssessment.id == assessment_id)
        )
        await holder.execute(
            select(LegalAssessmentSeries)
            .where(LegalAssessmentSeries.id == row.series_id)
            .with_for_update()
        )
        # Carga previa deliberada: debe refrescarse tras esperar.
        await waiter.scalar(
            select(LegalAssessment).where(LegalAssessment.id == assessment_id)
        )
        row.eipd_resolution_assessment = None
        await holder.flush()
        task = asyncio.create_task(
            record_eipd_resolution_review_v1(
                waiter,
                org_a_id,
                tid,
                assessment_id,
                profile_a_id,
                EipdResolutionReviewIn(
                    **review("continuar" if positive else "requiere_cambios")
                ),
            )
        )
        try:
            await asyncio.sleep(0.1)
            assert not task.done()
            if commit_change:
                await holder.commit()
            else:
                await holder.rollback()
            if commit_change or positive:
                with pytest.raises(HTTPException) as exc:
                    await asyncio.wait_for(task, timeout=5)
                assert exc.value.status_code == 409
                if positive:
                    controls = exc.value.detail["eipd_controls"]
                    assert controls["resolution"]["result"] == "incompleto"
                    codes = {
                        i["code"]
                        for i in controls["preparation_issues"]
                        if i["stage"] == "resolution"
                    }
                    assert ("expediente_ausente" in codes) == commit_change
                    assert controls["review_state"]["latest_review"] is None
                await waiter.rollback()
            else:
                event = await asyncio.wait_for(task, timeout=5)
                assert event.document_hash == build_eipd_resolution_document_hash_v1(
                    original["eipd_resolution_assessment"]
                )
                await waiter.commit()
        finally:
            await holder.rollback()
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await waiter.rollback()
    assert len(await events(_session_factory, original["id"])) == (
        0 if commit_change or positive else 1
    )


@pytest.mark.parametrize("operation", ["review", "confirm"])
@pytest.mark.parametrize("prior_negative", [False, True])
async def test_locked_composition_matches_readiness_and_rejection_preserves_state(
    client_a,
    resolution_rat,
    org_a_id,
    _session_factory,
    operation,
    prior_negative,
    complete_payload,
):
    async with fixtures.client_for(client_a, org_a_id) as client:
        detail, original = await setup(client, resolution_rat)
        updated = await client.patch(
            detail,
            json={
                "consent_assessment": complete_payload,
                "eipd_resolution_assessment": {"document_reference": "EIPD1"},
            },
        )
        assert updated.status_code == 200, updated.text
        original = updated.json()
        if prior_negative:
            assert (
                await client.post(
                    detail + "/eipd-resolution/reviews", json=review("no_continuar")
                )
            ).status_code == 201
        history_before = await events(_session_factory, original["id"])
        expected = (await client.get(detail + "/readiness")).json()["eipd_controls"]
        if operation == "review":
            response = await client.post(
                detail + "/eipd-resolution/reviews", json=review("continuar")
            )
            code = "revision_eipd_no_preparada"
        else:
            response = await client.post(detail + "/confirm")
            code = "controles_transversales_no_preparados"
        assert response.status_code == 409, response.text
        rejected = response.json()["detail"]
        assert rejected["code"] == code
        assert rejected["eipd_controls"] == expected
        assert {"fuentes_oficiales_no_verificadas", "gate_eipd_no_habilitado"} <= {
            i["code"] for i in expected["review_blockers"]
        }
        assert not any(i["stage"] == "review" for i in expected["review_blockers"])
        assert (await client.get(detail)).json() == original
        assert [e.id for e in await events(_session_factory, original["id"])] == [
            e.id for e in history_before
        ]


@pytest.mark.parametrize("commit_change", [False, True])
async def test_confirmation_rereads_document_and_latest_review_under_real_lock(
    client_a,
    resolution_rat,
    org_a_id,
    profile_a_id,
    auth_a_id,
    complete_payload,
    _app_session_factory,
    _session_factory,
    commit_change,
):
    import asyncio
    from uuid import UUID

    from fastapi import HTTPException
    from sqlalchemy import text

    from app.db.models import LegalAssessment, LegalAssessmentSeries
    from app.schemas.licitud import EipdResolutionReviewIn
    from app.services.licitud import (
        confirm_legal_assessment_v1,
        record_eipd_resolution_review_v1,
    )

    tid, payload = resolution_rat
    payload = dict(payload, consent_assessment=complete_payload)
    async with fixtures.client_for(client_a, org_a_id) as client:
        url = f"/licitud/treatments/{tid}/assessments"
        first = await client.post(url, json=payload)
        assert first.status_code == 201, first.text
        first_detail = url + "/" + first.json()["id"]
        assert (await client.post(first_detail + "/confirm")).status_code == 200
        confirmed = (await client.get(first_detail)).json()
        second = await client.post(
            url,
            json=dict(
                payload, eipd_resolution_assessment={"document_reference": "EIPD78"}
            ),
        )
        assert second.status_code == 201, second.text
        original = second.json()
        aid = UUID(original["id"])
        detail = url + "/" + original["id"]
        before = (await client.get(detail + "/readiness")).json()["eipd_controls"]
        async with _app_session_factory() as holder, _app_session_factory() as waiter:
            for session in (holder, waiter):
                await session.execute(
                    text("SELECT set_config('request.jwt.claim.sub', :sub, true)"),
                    {"sub": str(auth_a_id)},
                )
            row = await holder.scalar(
                select(LegalAssessment).where(LegalAssessment.id == aid)
            )
            await holder.execute(
                select(LegalAssessmentSeries)
                .where(LegalAssessmentSeries.id == row.series_id)
                .with_for_update()
            )
            await waiter.scalar(
                select(LegalAssessment).where(LegalAssessment.id == aid)
            )
            pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
            document = deepcopy(row.eipd_resolution_assessment)
            document["document_reference"] = "EIPD78 cambiado bajo lock"
            row.eipd_resolution_assessment = document
            await holder.flush()
            await record_eipd_resolution_review_v1(
                holder,
                org_a_id,
                tid,
                aid,
                profile_a_id,
                EipdResolutionReviewIn(**review("no_continuar")),
            )
            task = asyncio.create_task(
                confirm_legal_assessment_v1(waiter, org_a_id, tid, aid, profile_a_id)
            )
            try:

                async def wait_for_lock():
                    while True:
                        if await holder.scalar(
                            text("SELECT pg_blocking_pids(:pid)"), {"pid": pid}
                        ):
                            return
                        await asyncio.sleep(0.02)

                await asyncio.wait_for(wait_for_lock(), timeout=5)
                assert not task.done()
                if commit_change:
                    await holder.commit()
                else:
                    await holder.rollback()
                with pytest.raises(HTTPException) as exc:
                    await asyncio.wait_for(task, timeout=5)
                assert exc.value.status_code == 409
                controls = exc.value.detail["eipd_controls"]
                assert (
                    controls["review_state"]["latest_review"] is not None
                ) == commit_change
                if commit_change:
                    assert controls["review_state"]["review_status"] == "vigente"
                    assert (
                        controls["review_state"]["latest_review"]["decision"]
                        == "no_continuar"
                    )
                    assert "decision_no_continuar" in {
                        i["code"] for i in controls["confirmation_blockers"]
                    }
                else:
                    assert controls == before
                await waiter.rollback()
            finally:
                await holder.rollback()
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                await waiter.rollback()
        assert (await client.get(detail + "/readiness")).json()[
            "eipd_controls"
        ] == controls
        assert (await client.get(first_detail)).json() == confirmed
        after = (await client.get(detail)).json()
        assert after["status"] == "borrador"
        assert after["eipd_resolution_assessment"]["document_reference"] == (
            document["document_reference"] if commit_change else "EIPD78"
        )
        assert len(await events(_session_factory, original["id"])) == (
            1 if commit_change else 0
        )
