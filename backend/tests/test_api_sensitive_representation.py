"""CRUD ficticio bajo permisos/RLS, con gates conservadores."""

import asyncio
from copy import deepcopy
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text, update

from app.db.models import TreatmentDataCategory, TreatmentPurpose
from app.schemas.licitud import LegalAssessmentRepresentationDraftUpdateV1
from app.services import licitud
from app.services.sensitive_representation_binding import (
    evaluate_sensitive_representation_association_v1,
)
from tests import test_api_licitud as api
from tests import test_eipd_policy_shared_lock as locks
from tests import test_rls_isolation_licitud as rls

rat_m3 = api.rat_m3
complete_payload = api.complete_payload
explicit_review_policy = api.explicit_review_policy
pytestmark = pytest.mark.asyncio(loop_scope="session")
DOCUMENT = {
    "representation_kind": "mandatario",
    "authority_document_reference": "PRUEBA: documento ficticio",
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
            json={**payload, "sensitive_representation_assessment": DOCUMENT},
        )
        assert response.status_code == 201, response.text
    return tid, response.json(), client_a, org_a_id


async def test_create_get_binding_uses_server_identity(saved, _session_factory):
    tid, out, app, org = saved
    bound = out["sensitive_representation_assessment"]
    assert bound["assessment"]["authority_document_reference"].startswith("PRUEBA")
    context = {
        "organization_id": org,
        "treatment_id": tid,
        "assessment_id": out["id"],
        "rat_context_snapshot": out["rat_context_snapshot"],
        "legal_basis": out["legal_basis"],
        "consent_assessment": out["consent_assessment"],
        "sensitive_consent_assessment": out["sensitive_consent_assessment"],
    }
    assert (
        evaluate_sensitive_representation_association_v1(bound, context).result
        == "vigente"
    )
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        result = await client.get(f"/licitud/treatments/{tid}/assessments/{out['id']}")
        assert (
            result.status_code == 200
            and result.json()["sensitive_representation_assessment"] == bound
        )
    async with _session_factory() as db:
        assert (
            await db.scalar(
                text(
                    "SELECT sensitive_representation_assessment FROM legal_assessments WHERE id=:id"
                ),
                {"id": UUID(out["id"])},
            )
            == bound
        )


async def test_patch_omission_stale_reaporte_and_null(saved, _session_factory):
    tid, out, app, org = saved
    original = deepcopy(out["sensitive_representation_assessment"])
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
        assert changed.json()["sensitive_representation_assessment"] == original
        current = changed.json()
        context = {
            "organization_id": org,
            "treatment_id": tid,
            "assessment_id": out["id"],
            "rat_context_snapshot": current["rat_context_snapshot"],
            "legal_basis": current["legal_basis"],
            "consent_assessment": current["consent_assessment"],
            "sensitive_consent_assessment": current["sensitive_consent_assessment"],
        }
        assert evaluate_sensitive_representation_association_v1(
            original, context
        ).issues == ("asociacion_contexto_obsoleta",)

        fresh = await client.patch(
            url, json={"sensitive_representation_assessment": DOCUMENT}
        )
        assert fresh.status_code == 200, fresh.text
        assert (
            fresh.json()["sensitive_representation_assessment"]["context_binding"][
                "context_hash"
            ]
            != original["context_binding"]["context_hash"]
        )
        removed = await client.patch(
            url, json={"sensitive_representation_assessment": None}
        )
        assert (
            removed.status_code == 200
            and removed.json()["sensitive_representation_assessment"] is None
        )
        # Un documento retirado no prepara por si solo el consentimiento incompleto.
        assert (await client.post(url + "/confirm")).status_code != 200
    async with _session_factory() as db:
        assert await db.scalar(
            text(
                "SELECT sensitive_representation_assessment IS NULL FROM legal_assessments WHERE id=:id"
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
            url, json={"sensitive_representation_assessment": {field: "PRUEBA"}}
        )
        assert rejected.status_code == 422
        assert (await client.get(url)).json()[
            "sensitive_representation_assessment"
        ] == out["sensitive_representation_assessment"]


async def test_confirmation_readiness_and_review_fail_closed(saved):
    tid, out, app, org = saved
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        for suffix, code in [
            ("/confirm", "representacion_confirmacion_bloqueada"),
            (
                "/eipd-resolution/reviews/v2",
                "resolucion_eipd_representacion_asociacion_pendiente",
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
        assert body["representation_context_coverage"] == "pendiente"
        assert body["sensitive_representation"]["result"] == "incompleto"
        assert not body["sensitive_representation"]["can_confirm"]
        assert not body["sensitive_representation"]["authorizes_action"]
        assert any(
            item["code"] == "representacion_confirmacion_bloqueada"
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
            await client.patch(url, json={"sensitive_representation_assessment": None})
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
            await client.patch(
                url, json={"sensitive_representation_assessment": DOCUMENT}
            )
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
        diagnosis = response.json()["sensitive_representation"]
        assert diagnosis["result"] == "requiere_revision"
        assert any(
            issue["code"] == "asociacion_contexto_obsoleta"
            for issue in diagnosis["issues"]
        )
        assert (
            await client.patch(url, json={"sensitive_representation_assessment": None})
        ).status_code == 200
        response = await client.get(url + "/readiness")
        assert response.status_code == 200
        # Fixture RAT ordinario no sensible: no inferir representacion sensible por given_by solo.
        assert response.json()["sensitive_representation"] is None
        assert response.json()["representation_context_coverage"] == "no_aplica"


@pytest.mark.parametrize("review_version", ["", "/v2"])
@pytest.mark.parametrize(
    "decision_name", ["continuar", "requiere_cambios", "no_continuar"]
)
async def test_representation_marks_all_v4_review_decisions_pending(
    saved, _session_factory, review_version, decision_name
):
    tid, out, app, org = saved
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        result = await client.patch(url, json={"research_assessment": {}})
        assert result.status_code == 200, result.text
        result = await client.get(url + "/readiness")
        assert result.status_code == 200, result.text
        assert result.json()["eipd_controls_v3"] is None
        controls = result.json()["eipd_controls_v4"]
        assert controls is not None
        for name in ("continuar", "requiere_cambios", "no_continuar"):
            decision = controls["review_prerequisites_v4"][name]
            assert decision["prerequisites_met"] is False
            assert decision["context_metadata"] is None
            assert any(
                issue["code"] == "politica_representacion_no_implementada"
                for issue in decision["issues"]
            )
        before = (await client.get(url)).json()
        response = await client.post(
            url + f"/eipd-resolution/reviews{review_version}",
            json={
                "decision": decision_name,
                "rationale": "PRUEBA: decision ficticia sin autorizacion",
                "review_reference": "PRUEBA-BARRERA-V4",
            },
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == (
            "resolucion_eipd_representacion_asociacion_pendiente"
        )
        assert (await client.get(url)).json() == before
    async with _session_factory() as db:
        count = await db.scalar(
            text(
                "SELECT count(*) FROM eipd_resolution_reviews WHERE assessment_id=:id"
            ),
            {"id": UUID(out["id"])},
        )
        assert count == 0


@pytest.mark.parametrize("given_by", ["representante_legal", "mandatario"])
@pytest.mark.parametrize("sensitive_before_create", [True, False])
async def test_missing_document_uses_current_sensitive_rat(
    client_a, rat_m3, org_a_id, _session_factory, given_by, sensitive_before_create
):
    tid, payload = rat_m3

    async def mark_sensitive():
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentDataCategory)
                .where(TreatmentDataCategory.treatment_id == tid)
                .values(is_sensitive=True)
            )
            await db.commit()

    if sensitive_before_create:
        await mark_sensitive()
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(
            f"/licitud/treatments/{tid}/assessments",
            json={**payload, "consent_assessment": {"given_by": given_by}},
        )
        assert created.status_code == 201, created.text
        url = f"/licitud/treatments/{tid}/assessments/{created.json()['id']}"
        before = (await client.get(url)).json()
        if not sensitive_before_create:
            await mark_sensitive()
        response = await client.get(url + "/readiness")
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["representation_context_coverage"] == "pendiente"
        diagnostic = body["sensitive_representation"]
        assert diagnostic["result"] == "incompleto"
        assert diagnostic["can_confirm"] is False
        assert diagnostic["authorizes_action"] is False
        assert any(
            issue["code"] == "representacion_documento_ausente"
            for issue in diagnostic["issues"]
        )
        assert any(
            issue["code"] == "representacion_confirmacion_bloqueada"
            for issue in body["confirmation_blockers"]
        )
        if not sensitive_before_create:
            assert any(
                issue["code"] == "contexto_rat_desactualizado"
                for issue in body["confirmation_blockers"]
            )
        # Consultar no reconstruye ni escribe el expediente persistido.
        assert (await client.get(url)).json() == before
        assert (await client.post(url + "/confirm")).status_code != 200


@pytest.mark.parametrize("given_by", ["representante_legal", "mandatario"])
@pytest.mark.parametrize("with_document", [True, False])
async def test_missing_current_rat_does_not_report_representation_not_applicable(
    client_a, rat_m3, org_a_id, _session_factory, given_by, with_document
):
    tid, payload = rat_m3
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        material = (
            {"sensitive_representation_assessment": DOCUMENT} if with_document else {}
        )
        created = await client.post(
            f"/licitud/treatments/{tid}/assessments",
            json={**payload, **material, "consent_assessment": {"given_by": given_by}},
        )
        assert created.status_code == 201, created.text
        url = f"/licitud/treatments/{tid}/assessments/{created.json()['id']}"
        original = (await client.get(url)).json()
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentPurpose)
                .where(TreatmentPurpose.treatment_id == tid)
                .values(purpose="PRUEBA: finalidad cambiada")
            )
            await db.commit()
        response = await client.get(url + "/readiness")
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["rat_context_current"] is None
        assert body["representation_context_coverage"] == "pendiente"
        diagnostic = body["sensitive_representation"]
        assert diagnostic["result"] == "requiere_revision"
        assert diagnostic["can_confirm"] is False
        assert diagnostic["authorizes_action"] is False
        assert {issue["code"] for issue in diagnostic["issues"]} == {
            "representacion_contexto_actual_no_disponible"
        }
        assert (await client.get(url)).json() == original
        assert (await client.post(url + "/confirm")).status_code != 200


@pytest.mark.parametrize(
    "scope_case", ["compatible", "rat_incompatible", "sensitive_incompatible"]
)
async def test_complete_document_does_not_authorize_actions(
    client_a, rat_m3, org_a_id, _session_factory, scope_case
):
    tid, payload = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == tid)
            .values(is_sensitive=True)
        )
        await db.commit()
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    document = {
        field: "PRUEBA: declaracion ficticia sin verificar facultades"
        for field in (
            "representative_reference",
            "represented_subjects_reference",
            "authority_document_reference",
            "authority_document_version",
            "authority_basis_description",
            "express_authority_analysis",
            "scope_match_analysis",
            "validity_analysis",
            "limitations",
            "revocation_information",
        )
    }
    document.update(
        representation_kind="mandatario",
        scope=deepcopy(scope),
        evidence=[{"evidence_type": "PRUEBA", "reference": "PRUEBA: evidencia"}],
    )
    sensitive_scope = deepcopy(scope)
    if scope_case == "rat_incompatible":
        document["scope"]["data_category_codes"] = ["otra_categoria_ficticia"]
    elif scope_case == "sensitive_incompatible":
        sensitive_scope["data_subject_codes"] = ["otros_titulares_ficticios"]
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(
            f"/licitud/treatments/{tid}/assessments",
            json={
                **payload,
                "consent_assessment": {"given_by": "mandatario"},
                "sensitive_consent_assessment": {"scope": sensitive_scope},
                "sensitive_representation_assessment": document,
            },
        )
        assert created.status_code == 201, created.text
        url = f"/licitud/treatments/{tid}/assessments/{created.json()['id']}"
        original = (await client.get(url)).json()
        readiness = await client.get(url + "/readiness")
        assert readiness.status_code == 200, readiness.text
        body = readiness.json()
        diagnosis = body["sensitive_representation"]
        assert body["representation_context_coverage"] == "pendiente"
        assert diagnosis["can_confirm"] is False
        assert diagnosis["authorizes_action"] is False
        if scope_case == "compatible":
            assert diagnosis["result"] == "completo"
            assert diagnosis["issues"] == []
        else:
            assert diagnosis["result"] == "requiere_revision"
            code = (
                "representacion_alcance_rat_incompatible"
                if scope_case == "rat_incompatible"
                else "representacion_alcance_sensible_incompatible"
            )
            assert any(issue["code"] == code for issue in diagnosis["issues"])
        confirmed = await client.post(url + "/confirm")
        assert confirmed.status_code == 409, confirmed.text
        assert (
            confirmed.json()["detail"]["code"]
            == "representacion_confirmacion_bloqueada"
        )
        reviewed = await client.post(
            url + "/eipd-resolution/reviews/v2",
            json={
                "decision": "requiere_cambios",
                "rationale": "PRUEBA",
                "review_reference": "PRUEBA",
            },
        )
        assert reviewed.status_code == 409, reviewed.text
        assert (
            reviewed.json()["detail"]["code"]
            == "resolucion_eipd_representacion_asociacion_pendiente"
        )
        assert (await client.get(url)).json() == original


@pytest.mark.parametrize("holder_action", ["representation", "confirmation"])
@pytest.mark.parametrize("commit_holder", [True, False])
async def test_representation_and_confirmation_serialize(
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
                "sensitive_representation_assessment": None,
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
            LegalAssessmentRepresentationDraftUpdateV1(
                sensitive_representation_assessment=DOCUMENT
            ),
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
                    assert (
                        exc.value.detail["code"]
                        == "representacion_confirmacion_bloqueada"
                    )
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
                    "SELECT status::text, sensitive_representation_assessment IS NOT NULL AS has_material "
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


async def test_resolution_v3_roundtrip_reaporte_withdrawal_and_actions(
    saved, _session_factory
):
    tid, out, app, org = saved
    url = f"/licitud/treatments/{tid}/assessments/{out['id']}"
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    ) as client:
        response = await client.patch(url, json={"eipd_resolution_assessment": {}})
        assert response.status_code == 200, response.text
        original = response.json()
        resolution = original["eipd_resolution_assessment"]
        assert resolution["context_binding"]["binding_version"] == 3
        assert (await client.get(url)).json() == original
        ready = await client.get(url + "/readiness")
        assert ready.status_code == 200, ready.text
        control = ready.json()["eipd_controls_v4"]
        assert control["resolution"]["binding_version"] == 3
        assert control["resolution"]["context_current"] is True
        assert control["context_metadata"]["metadata_schema_version"] == 2
        assert not control["can_confirm"] and not control["authorizes_action"]
        assert (await client.get(url)).json() == original
        changed = await client.patch(
            url,
            json={
                "sensitive_representation_assessment": {
                    **DOCUMENT,
                    "notes": "PRUEBA: nuevo documento",
                }
            },
        )
        assert changed.status_code == 200
        assert changed.json()["eipd_resolution_assessment"] == resolution
        stale = (await client.get(url + "/readiness")).json()["eipd_controls_v4"]
        assert stale["resolution"]["context_current"] is False
        assert stale["context_metadata"] is None
        fresh = await client.patch(url, json={"eipd_resolution_assessment": {}})
        assert fresh.status_code == 200, fresh.text
        new_resolution = fresh.json()["eipd_resolution_assessment"]
        assert (
            new_resolution["context_binding"]["context_hash"]
            != resolution["context_binding"]["context_hash"]
        )
        assert new_resolution["context_binding"]["binding_version"] == 3
        removed = await client.patch(
            url, json={"sensitive_representation_assessment": None}
        )
        assert removed.status_code == 200
        assert removed.json()["eipd_resolution_assessment"] == new_resolution
        reissued = await client.patch(url, json={"eipd_resolution_assessment": {}})
        assert reissued.status_code == 200, reissued.text
        assert (
            reissued.json()["eipd_resolution_assessment"]["context_binding"][
                "binding_version"
            ]
            == 3
        )
        before_actions = (await client.get(url)).json()
        confirmed = await client.post(url + "/confirm")
        assert confirmed.status_code == 409, confirmed.text
        assert (
            confirmed.json()["detail"]["code"]
            == "representacion_confirmacion_bloqueada"
        )
        review = await client.post(
            url + "/eipd-resolution/reviews/v2",
            json={
                "decision": "requiere_cambios",
                "rationale": "PRUEBA",
                "review_reference": "PRUEBA",
            },
        )
        assert review.status_code == 409, review.text
        assert (
            review.json()["detail"]["code"]
            == "resolucion_eipd_representacion_asociacion_pendiente"
        )
        final_ready = await client.get(url + "/readiness")
        assert final_ready.status_code == 200, final_ready.text
        assert any(
            i["code"] == "representacion_confirmacion_bloqueada"
            for i in final_ready.json()["confirmation_blockers"]
        )
        assert (await client.get(url)).json() == before_actions
    async with _session_factory() as db:
        assert (
            await db.scalar(
                text(
                    "SELECT count(*) FROM eipd_resolution_reviews WHERE assessment_id=:id"
                ),
                {"id": UUID(out["id"])},
            )
            == 0
        )


async def test_create_with_representation_and_resolution_binds_final_context(
    client_a, rat_m3, org_a_id
):
    tid, payload = rat_m3
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        response = await client.post(
            f"/licitud/treatments/{tid}/assessments",
            json={
                **payload,
                "sensitive_representation_assessment": DOCUMENT,
                "eipd_resolution_assessment": {},
            },
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert (
            body["eipd_resolution_assessment"]["context_binding"]["binding_version"]
            == 3
        )
        ready = await client.get(
            f"/licitud/treatments/{tid}/assessments/{body['id']}/readiness"
        )
        assert ready.status_code == 200, ready.text
        assert ready.json()["eipd_controls_v4"]["resolution"]["context_current"] is True
