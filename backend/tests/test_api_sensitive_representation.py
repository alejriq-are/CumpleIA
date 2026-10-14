"""CRUD ficticio bajo permisos/RLS, con gates conservadores."""

from copy import deepcopy
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text, update

from app.db.models import TreatmentDataCategory
from app.services.sensitive_representation_binding import (
    evaluate_sensitive_representation_association_v1,
)
from tests import test_api_licitud as api

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


async def test_representation_marks_all_v3_review_decisions_pending(saved):
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
        controls = result.json()["eipd_controls_v3"]
        assert controls is not None
        for name in ("continuar", "requiere_cambios", "no_continuar"):
            decision = controls["review_prerequisites_v3"][name]
            assert decision["prerequisites_met"] is False
            assert decision["context_metadata"] is None
            assert any(
                issue["code"] == "resolucion_eipd_representacion_asociacion_pendiente"
                for issue in decision["issues"]
            )
        assert (
            await client.post(
                url + "/eipd-resolution/reviews/v2",
                json={
                    "decision": "requiere_cambios",
                    "rationale": "PRUEBA",
                    "review_reference": "PRUEBA",
                },
            )
        ).status_code == 409


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
