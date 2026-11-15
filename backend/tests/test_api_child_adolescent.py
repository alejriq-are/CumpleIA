"""CRUD ficticio bajo permisos/RLS, con gates conservadores."""

import asyncio
from copy import deepcopy
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text, update

from app.db.models import (
    Membership,
    Subscription,
    SubscriptionStatus,
    TreatmentDataSubject,
    TreatmentPurpose,
    UserRole,
)
from app.schemas.child_adolescent_api import LegalAssessmentChildDraftUpdateV1
from app.services import licitud
from app.services.child_adolescent_binding import (
    evaluate_child_adolescent_association_v1,
)
from tests import test_api_licitud as api
from tests import test_eipd_policy_shared_lock as locks
from tests import test_rls_isolation_licitud as rls

rat_m3 = api.rat_m3
complete_payload = api.complete_payload
explicit_review_policy = api.explicit_review_policy
pytestmark = pytest.mark.asyncio(loop_scope="session")
DOCUMENT = {
    "declared_groups": ["ninos_ninas"],
    "notes": "PRUEBA: documento ficticio",
}


@pytest.fixture
async def saved(client_a, rat_m3, org_a_id):
    tid, payload = rat_m3
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        response = await client.post(
            f"/licitud/treatments/{tid}/assessments",
            json={**payload, "child_adolescent_assessment": DOCUMENT},
        )
        assert response.status_code == 201, response.text
    return tid, response.json(), client_a, org_a_id


async def test_create_get_binding_uses_server_identity(saved, _session_factory):
    tid, out, app, org = saved
    bound = out["child_adolescent_assessment"]
    assert bound["assessment"]["notes"].startswith("PRUEBA")
    context = {
        "organization_id": org,
        "treatment_id": tid,
        "assessment_id": out["id"],
        "rat_context_snapshot": out["rat_context_snapshot"],
        "legal_basis": out["legal_basis"],
        "consent_assessment": out["consent_assessment"],
        "sensitive_consent_assessment": out["sensitive_consent_assessment"],
        "special_conditions_document": {
            k: v for k, v in out["special_conditions"].items() if k != "context_binding"
        },
        "sensitive_representation_assessment": out[
            "sensitive_representation_assessment"
        ],
    }
    assert evaluate_child_adolescent_association_v1(bound, context).result == "vigente"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        result = await client.get(f"/licitud/treatments/{tid}/assessments/{out['id']}")
        assert (
            result.status_code == 200
            and result.json()["child_adolescent_assessment"] == bound
        )
    async with _session_factory() as db:
        assert (
            await db.scalar(
                text(
                    "SELECT child_adolescent_assessment FROM legal_assessments WHERE id=:id"
                ),
                {"id": UUID(out["id"])},
            )
            == bound
        )


async def test_patch_omission_stale_reaporte_and_null(saved, _session_factory):
    tid, out, app, org = saved
    original = deepcopy(out["child_adolescent_assessment"])
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        changed = await client.patch(
            url,
            json={
                "consent_assessment": {
                    "given_by": "mandatario",
                    "notes": "PRUEBA: cambio de contexto",
                }
            },
        )
        assert changed.status_code == 200, changed.text
        assert changed.json()["child_adolescent_assessment"] == original
        current = changed.json()
        context = {
            "organization_id": org,
            "treatment_id": tid,
            "assessment_id": out["id"],
            "rat_context_snapshot": current["rat_context_snapshot"],
            "legal_basis": current["legal_basis"],
            "consent_assessment": current["consent_assessment"],
            "sensitive_consent_assessment": current["sensitive_consent_assessment"],
            "special_conditions_document": {
                k: v
                for k, v in current["special_conditions"].items()
                if k != "context_binding"
            },
            "sensitive_representation_assessment": current[
                "sensitive_representation_assessment"
            ],
        }
        assert evaluate_child_adolescent_association_v1(original, context).issues == (
            "asociacion_contexto_obsoleta",
        )

        fresh = await client.patch(url, json={"child_adolescent_assessment": DOCUMENT})
        assert fresh.status_code == 200, fresh.text
        assert (
            fresh.json()["child_adolescent_assessment"]["context_binding"][
                "context_hash"
            ]
            != original["context_binding"]["context_hash"]
        )
        removed = await client.patch(url, json={"child_adolescent_assessment": None})
        assert (
            removed.status_code == 200
            and removed.json()["child_adolescent_assessment"] is None
        )
        # Un documento retirado no prepara por si solo el consentimiento incompleto.
        assert (await client.post(url + "/confirm")).status_code != 200
    async with _session_factory() as db:
        assert await db.scalar(
            text(
                "SELECT child_adolescent_assessment IS NULL FROM legal_assessments WHERE id=:id"
            ),
            {"id": UUID(out["id"])},
        )


@pytest.mark.parametrize(
    "field", ["context_binding", "context_hash", "created_by", "can_confirm"]
)
async def test_injection_rejected_without_changing_document(saved, field):
    tid, out, app, org = saved
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        rejected = await client.patch(
            url, json={"child_adolescent_assessment": {field: "PRUEBA"}}
        )
        assert rejected.status_code == 422
        assert (await client.get(url)).json()["child_adolescent_assessment"] == out[
            "child_adolescent_assessment"
        ]


async def test_confirmation_readiness_and_review_fail_closed(saved):
    tid, out, app, org = saved
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        for suffix, code in [
            ("/confirm", "infancia_confirmacion_bloqueada"),
            (
                "/eipd-resolution/reviews/v2",
                "resolucion_eipd_infancia_asociacion_pendiente",
            ),
        ]:
            kwargs = (
                {
                    "json": {
                        "decision": "requiere_cambios",
                        "rationale": "PRUEBA",
                        "review_reference": "PRUEBA",
                    }
                }
                if "reviews" in suffix
                else {}
            )
            result = await client.post(url + suffix, **kwargs)
            assert result.status_code == 409, result.text
            assert result.json()["detail"]["code"] == code
        result = await client.get(url + "/readiness")
        assert result.status_code == 200, result.text
        body = result.json()
        assert body["child_adolescent_context_coverage"] == "pendiente"
        assert body["child_adolescent"]["association_status"] == "vigente"
        assert not body["child_adolescent"]["can_confirm"]
        assert not body["child_adolescent"]["authorizes_action"]
        assert any(
            item["code"] == "infancia_confirmacion_bloqueada"
            for item in body["confirmation_blockers"]
        )
        assert (await client.get(url)).json()["status"] == "borrador"


async def test_other_tenant_and_wrong_parent_cannot_read_material(
    saved, client_b, org_b_id
):
    tid, out, app, org = saved
    async with AsyncClient(
        transport=ASGITransport(app=client_b),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_b_id)},
    ) as client:
        url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
        assert (await client.get(url)).status_code == 404
        assert (
            await client.patch(url, json={"child_adolescent_assessment": None})
        ).status_code == 404


async def test_wrong_parent_cannot_read_material(saved):
    tid, out, app, org = saved
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        assert (
            await client.get(f"/licitud/treatments/{uuid4()}/assessments/{out['id']}")
        ).status_code == 404


async def test_existing_confirmed_history_cannot_receive_material(
    client_a, rat_m3, complete_payload, org_a_id
):
    tid, payload = rat_m3
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(
            f"/licitud/treatments/{tid}/assessments",
            json={**payload, "consent_assessment": complete_payload},
        )
        assert created.status_code == 201, created.text
        url = f"/licitud/treatments/{tid}/assessments/{created.json()['id']}"
        assert (await client.post(url + "/confirm")).status_code == 200
        old = (await client.get(url)).json()
        assert (
            await client.patch(url, json={"child_adolescent_assessment": DOCUMENT})
        ).status_code == 409
        assert (await client.get(url)).json() == old


async def test_unknown_root_fields_do_not_apply_partial_change(saved):
    tid, out, app, org = saved
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        before = (await client.get(url)).json()
        response = await client.patch(
            url,
            json={
                "justification": "PRUEBA: cambio no autorizado",
                "created_by": str(uuid4()),
            },
        )
        assert response.status_code == 422
        assert (await client.get(url)).json() == before


async def test_readiness_reports_stale_context_and_removal(saved):
    tid, out, app, org = saved
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        assert (
            await client.patch(
                url,
                json={
                    "consent_assessment": {
                        "given_by": "mandatario",
                        "notes": "PRUEBA: cambio",
                    }
                },
            )
        ).status_code == 200
        response = await client.get(url + "/readiness")
        assert response.status_code == 200, response.text
        diagnosis = response.json()["child_adolescent"]
        assert diagnosis["result"] == "requiere_revision"
        assert any(
            issue["code"] == "asociacion_contexto_obsoleta"
            for issue in diagnosis["issues"]
        )
        assert (
            await client.patch(url, json={"child_adolescent_assessment": None})
        ).status_code == 200
        response = await client.get(url + "/readiness")
        assert response.status_code == 200
        # Fixture RAT ordinario no sensible: no inferir infancia sensible por given_by solo.
        assert response.json()["child_adolescent"] is None
        assert response.json()["child_adolescent_context_coverage"] == "no_aplica"


@pytest.mark.parametrize("holder_action", ["representation", "confirmation"])
@pytest.mark.parametrize("commit_holder", [True, False])
async def test_child_and_confirmation_serialize(
    saved,
    rat_m3,
    complete_payload,
    _app_session_factory,
    _session_factory,
    profile_a_id,
    auth_a_id,
    holder_action,
    commit_holder,
):
    tid, out, app, org = saved
    aid = UUID(out["id"])
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        prepared = await client.patch(
            f"/licitud/treatments/{tid}/assessments/{aid}",
            json={
                "child_adolescent_assessment": None,
                "consent_assessment": complete_payload,
                "special_conditions": rat_m3[1]["special_conditions"],
                "eipd_screening": rat_m3[1]["eipd_screening"],
            },
        )
        assert prepared.status_code == 200, prepared.text

    async def act(db, action):
        if action == "confirmation":
            return await licitud.confirm_legal_assessment_v1(
                db, org, tid, aid, profile_a_id
            )
        return await licitud.update_legal_assessment_draft_v1(
            db,
            org,
            tid,
            aid,
            profile_a_id,
            LegalAssessmentChildDraftUpdateV1(child_adolescent_assessment=DOCUMENT),
        )

    waiting_action = (
        "confirmation" if holder_action == "representation" else "representation"
    )
    async with _app_session_factory() as holder, _app_session_factory() as waiter:
        await rls._set_auth_user(holder, auth_a_id)
        await rls._set_auth_user(waiter, auth_a_id)
        await act(holder, holder_action)
        pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
        task = asyncio.create_task(act(waiter, waiting_action))
        try:
            await locks.blocked(holder, pid)
            assert not task.done()
            if commit_holder:
                await holder.commit()
                with pytest.raises(HTTPException) as exc:
                    await asyncio.wait_for(task, 5)
                assert exc.value.status_code == 409
                if waiting_action == "confirmation":
                    assert exc.value.detail["code"] == "infancia_confirmacion_bloqueada"
                await waiter.rollback()
                final_action = holder_action
            else:
                await holder.rollback()
                await asyncio.wait_for(task, 5)
                await waiter.commit()
                final_action = waiting_action
        finally:
            await locks.stop(task)
            await holder.rollback()
            await waiter.rollback()
    async with _session_factory() as db:
        row = (
            await db.execute(
                text(
                    "SELECT status::text, child_adolescent_assessment IS NOT NULL AS has_material "
                    "FROM legal_assessments WHERE id=:id"
                ),
                {"id": aid},
            )
        ).one()
        assert tuple(row) == (
            ("borrador", True)
            if final_action == "representation"
            else ("confirmado", False)
        )


async def test_unavailable_rat_does_not_report_old_context_current(
    saved, _session_factory
):
    tid, out, app, org = saved
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentPurpose)
            .where(TreatmentPurpose.treatment_id == tid)
            .values(purpose="PRUEBA: finalidad cambiada")
        )
        await db.commit()
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        before = (await client.get(url)).json()
        response = await client.get(url + "/readiness")
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["rat_context_current"] is None
        assert body["child_adolescent"]["association_status"] == "requiere_revision"
        assert {i["code"] for i in body["child_adolescent"]["issues"]} == {
            "infancia_contexto_actual_no_disponible"
        }
        assert (await client.get(url)).json() == before


@pytest.mark.parametrize("flag", ["includes_children", "includes_adolescents"])
async def test_withdrawal_does_not_remove_rat_gate(saved, _session_factory, flag):
    tid, out, app, org = saved
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataSubject)
            .where(TreatmentDataSubject.treatment_id == tid)
            .values(**{flag: True})
        )
        await db.commit()
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        removed = await client.patch(url, json={"child_adolescent_assessment": None})
        assert removed.status_code == 200, removed.text
        ready = await client.get(url + "/readiness")
        assert ready.status_code == 200, ready.text
        body = ready.json()
        assert body["child_adolescent_context_coverage"] == "pendiente"
        assert body["child_adolescent"]["association_status"] == "requiere_revision"
        assert (await client.post(url + "/confirm")).json()["detail"][
            "code"
        ] == "infancia_confirmacion_bloqueada"


@pytest.mark.parametrize("restriction", ["viewer", "suspended"])
async def test_write_permissions_enforced_without_partial_changes(
    saved, _session_factory, profile_a_id, restriction
):
    tid, out, app, org = saved
    async with _session_factory() as db:
        if restriction == "viewer":
            await db.execute(
                update(Membership)
                .where(
                    Membership.organization_id == org,
                    Membership.profile_id == profile_a_id,
                )
                .values(role=UserRole.viewer)
            )
        else:
            await db.execute(
                update(Subscription)
                .where(Subscription.organization_id == org)
                .values(status=SubscriptionStatus.suspended)
            )
        await db.commit()
    try:
        url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"X-Organization-Id": str(org)},
        ) as client:
            response = await client.patch(
                url, json={"child_adolescent_assessment": None}
            )
            assert response.status_code == (
                403 if restriction == "viewer" else 402
            ), response.text
        async with _session_factory() as db:
            assert (
                await db.scalar(
                    text(
                        "SELECT child_adolescent_assessment FROM legal_assessments WHERE id=:id"
                    ),
                    {"id": UUID(out["id"])},
                )
                == out["child_adolescent_assessment"]
            )
    finally:
        async with _session_factory() as db:
            await db.execute(
                update(Membership)
                .where(
                    Membership.organization_id == org,
                    Membership.profile_id == profile_a_id,
                )
                .values(role=UserRole.owner)
            )
            await db.execute(
                update(Subscription)
                .where(Subscription.organization_id == org)
                .values(status=SubscriptionStatus.active)
            )
            await db.commit()


async def test_binding_failure_rolls_back_all_patch_fields(saved, monkeypatch):
    tid, out, app, org = saved
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"

    def fail(*args, **kwargs):
        raise HTTPException(400, "PRUEBA: bind rechazado")

    monkeypatch.setattr(licitud, "bind_child_adolescent_v1", fail)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        response = await client.patch(
            url,
            json={
                "justification": "PRUEBA: no persistir",
                "child_adolescent_assessment": DOCUMENT,
            },
        )
        assert response.status_code == 400
        assert (await client.get(url)).json() == out


async def test_create_failure_after_child_binding_rolls_back_entire_transaction(
    client_a, rat_m3, org_a_id, _session_factory, monkeypatch
):
    tid, payload = rat_m3

    def fail(*args, **kwargs):
        raise HTTPException(400, "PRUEBA: screening rechazado despues de infancia")

    monkeypatch.setattr(licitud, "bind_eipd_screening_v12", fail)
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        result = await client.post(
            f"/licitud/treatments/{tid}/assessments",
            json={**payload, "child_adolescent_assessment": DOCUMENT},
        )
        assert result.status_code == 400, result.text
    async with _session_factory() as db:
        for table in ("legal_assessments", "legal_assessment_series"):
            assert (
                await db.scalar(
                    text(f"SELECT count(*) FROM {table} WHERE treatment_id=:id"),
                    {"id": tid},
                )
                == 0
            )


async def test_reaporte_binds_final_related_fields_in_same_patch(saved, rat_m3):
    tid, out, app, org = saved
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        response = await client.patch(
            url,
            json={
                "consent_assessment": {
                    "given_by": "mandatario",
                    "notes": "PRUEBA: contexto final",
                },
                "sensitive_representation_assessment": {
                    "representation_kind": "mandatario",
                    "authority_document_reference": "PRUEBA: referencia ficticia",
                },
                "special_conditions": rat_m3[1]["special_conditions"],
                "child_adolescent_assessment": DOCUMENT,
            },
        )
        assert response.status_code == 200, response.text
        current = response.json()
        context = {
            "organization_id": org,
            "treatment_id": tid,
            "assessment_id": current["id"],
            "rat_context_snapshot": current["rat_context_snapshot"],
            "legal_basis": current["legal_basis"],
            "consent_assessment": current["consent_assessment"],
            "sensitive_consent_assessment": current["sensitive_consent_assessment"],
            "special_conditions_document": {
                k: v
                for k, v in current["special_conditions"].items()
                if k != "context_binding"
            },
            "sensitive_representation_assessment": current[
                "sensitive_representation_assessment"
            ],
        }
        assert (
            evaluate_child_adolescent_association_v1(
                current["child_adolescent_assessment"], context
            ).result
            == "vigente"
        )
        assert (await client.get(url)).json() == current
