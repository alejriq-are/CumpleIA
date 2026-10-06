"""API documental EIPD con RAT real, PostgreSQL y runtime app_user."""

import uuid
from copy import deepcopy

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select, update

from app.db.models import (
    EipdResolutionReview,
    LegalAssessment,
    Membership,
    Subscription,
    SubscriptionStatus,
    Treatment,
    TreatmentDataSource,
    UserRole,
)
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    build_eipd_resolution_document_hash_v1,
    eipd_resolution_context_is_current_v1,
)
from tests import test_api_licitud as api_fixtures

rat_m3 = api_fixtures.rat_m3
complete_payload = api_fixtures.complete_payload


@pytest_asyncio.fixture
async def resolution_rat(rat_m3, _session_factory):
    yield rat_m3
    async with _session_factory() as db:
        await db.execute(
            delete(EipdResolutionReview).where(
                EipdResolutionReview.assessment_id.in_(
                    select(LegalAssessment.id).where(
                        LegalAssessment.treatment_id == rat_m3[0]
                    )
                )
            )
        )
        await db.commit()


def context_from_response(data):
    return {f: data[f] for f in EipdResolutionContextV1.model_fields}


def client_for(app, org):
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Organization-Id": str(org)},
    )


async def test_document_create_patch_null_history_and_readonly(
    client_a, resolution_rat, org_a_id, org_b_id, profile_a_id, _session_factory
):
    tid, payload = resolution_rat
    url = f"/licitud/treatments/{tid}/assessments"
    async with client_for(client_a, org_a_id) as client:
        created = await client.post(
            url,
            json={
                **payload,
                "eipd_resolution_assessment": {
                    "document_reference": "EIPD1",
                    "report_reference": "Informe externo",
                    "notes": "Inicial",
                },
            },
        )
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        doc = original["eipd_resolution_assessment"]
        assert eipd_resolution_context_is_current_v1(
            doc, context_from_response(original)
        )
        async with _session_factory() as db:
            event = EipdResolutionReview(
                organization_id=org_a_id,
                assessment_id=uuid.UUID(original["id"]),
                created_by=profile_a_id,
                decision="requiere_cambios",
                rationale="Fixture de revision pendiente",
                review_reference="REV1",
                document_hash=build_eipd_resolution_document_hash_v1(doc),
                context_hash=doc["context_binding"]["context_hash"],
            )
            db.add(event)
            await db.commit()
            event_id = event.id
            event_snapshot = (
                event.decision,
                event.document_hash,
                event.context_hash,
                event.created_at,
            )
        assert (await client.get(detail)).json() == original
        await client.get(detail + "/readiness")
        assert (await client.get(detail)).json() == original
        preserved = await client.patch(
            detail, json={"justification": "Actualizacion ordinaria"}
        )
        assert preserved.status_code == 200
        assert preserved.json()["eipd_resolution_assessment"] == doc
        replaced = await client.patch(
            detail, json={"eipd_resolution_assessment": {"notes": "Sustituido"}}
        )
        assert replaced.status_code == 200, replaced.text
        new_doc = replaced.json()["eipd_resolution_assessment"]
        assert (
            new_doc["report_reference"] is None
            and new_doc["document_reference"] is None
        )
        assert new_doc["notes"] == "Sustituido"
        assert build_eipd_resolution_document_hash_v1(new_doc) != event_snapshot[1]
        assert (await client.patch(detail, json={})).json()[
            "eipd_resolution_assessment"
        ] == new_doc
        removed = await client.patch(detail, json={"eipd_resolution_assessment": None})
        assert (
            removed.status_code == 200
            and removed.json()["eipd_resolution_assessment"] is None
        )
        async with _session_factory() as db:
            current = await db.get(EipdResolutionReview, event_id)
            assert (
                current.decision,
                current.document_hash,
                current.context_hash,
                current.created_at,
            ) == event_snapshot
            events = await db.scalars(
                select(EipdResolutionReview).where(
                    EipdResolutionReview.assessment_id == uuid.UUID(original["id"])
                )
            )
            assert len(events.all()) == 1
            assessment = await db.get(LegalAssessment, uuid.UUID(original["id"]))
            assert assessment.eipd_resolution_assessment is None
        wrong_headers = {"X-Organization-Id": str(org_b_id)}
        assert (await client.get(detail, headers=wrong_headers)).status_code == 403
        assert (
            await client.patch(
                detail, headers=wrong_headers, json={"eipd_resolution_assessment": {}}
            )
        ).status_code == 403
        assert (await client.get(detail)).json() == removed.json()


DOC_FIELDS = [
    f
    for f in EipdResolutionContextV1.model_fields
    if f not in ("rat_context_snapshot", "legal_basis")
]


@pytest.mark.parametrize("field", DOC_FIELDS)
async def test_patch_document_does_not_auto_rebind_resolution(
    client_a, resolution_rat, org_a_id, field
):
    tid, payload = resolution_rat
    url = f"/licitud/treatments/{tid}/assessments"
    async with client_for(client_a, org_a_id) as client:
        created = await client.post(
            url, json={**payload, "eipd_resolution_assessment": {}}
        )
        assert created.status_code == 201
        original = created.json()
        detail = url + "/" + original["id"]
        old_doc = original["eipd_resolution_assessment"]
        patch = (
            {"notes": "Cambio"}
            if field != "lia_assessment"
            else {"necessity": {"necessity_analysis": "Cambio"}}
        )
        changed = await client.patch(detail, json={field: patch})
        assert changed.status_code == 200, changed.text
        data = changed.json()
        assert data["eipd_resolution_assessment"] == old_doc
        assert not eipd_resolution_context_is_current_v1(
            old_doc, context_from_response(data)
        )
        assert (await client.get(detail)).json() == data
        rebound = await client.patch(detail, json={"eipd_resolution_assessment": {}})
        assert rebound.status_code == 200
        assert eipd_resolution_context_is_current_v1(
            rebound.json()["eipd_resolution_assessment"],
            context_from_response(rebound.json()),
        )
        # Reaportar no genera revision ni aprueba el documento.
        ready = (await client.get(detail + "/readiness")).json()
        assert "resolucion_eipd_no_validada" in {
            b["code"] for b in ready["confirmation_blockers"]
        }
        removed = await client.patch(detail, json={field: None})
        assert removed.status_code == 200
        assert not eipd_resolution_context_is_current_v1(
            removed.json()["eipd_resolution_assessment"],
            context_from_response(removed.json()),
        )


async def test_final_order_and_real_rat_change(
    client_a, resolution_rat, org_a_id, _session_factory
):
    tid, payload = resolution_rat
    url = f"/licitud/treatments/{tid}/assessments"
    async with client_for(client_a, org_a_id) as client:
        created = await client.post(url, json=payload)
        assert (
            created.status_code == 201
            and created.json()["eipd_resolution_assessment"] is None
        )
        detail = url + "/" + created.json()["id"]
        patch = {
            "consent_assessment": {"notes": "Nuevo documento"},
            "legal_basis": "defensa_derechos_art13e",
            "special_conditions": payload["special_conditions"],
            "eipd_screening": payload["eipd_screening"],
            "eipd_resolution_assessment": {"notes": "Version nueva"},
        }
        saved = await client.patch(detail, json=patch)
        assert saved.status_code == 200, saved.text
        data = saved.json()
        assert eipd_resolution_context_is_current_v1(
            data["eipd_resolution_assessment"], context_from_response(data)
        )
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == tid)
                .values(retention_rule="10 años")
            )
            await db.commit()
        assert (await client.get(detail)).json() == data
        ready = (await client.get(detail + "/readiness")).json()
        assert not ready["rat_context_current"]
        assert (await client.get(detail)).json() == data
        refresh = await client.patch(detail, json={})
        assert refresh.status_code == 200
        assert (
            refresh.json()["eipd_resolution_assessment"]
            == data["eipd_resolution_assessment"]
        )
        assert not eipd_resolution_context_is_current_v1(
            data["eipd_resolution_assessment"], context_from_response(refresh.json())
        )
        refreshed = await client.patch(detail, json={"eipd_resolution_assessment": {}})
        assert refreshed.status_code == 200
        assert eipd_resolution_context_is_current_v1(
            refreshed.json()["eipd_resolution_assessment"],
            context_from_response(refreshed.json()),
        )


@pytest.mark.parametrize("method", ["create", "patch"])
async def test_api_rejects_server_fields_and_invalid_contract(
    client_a, resolution_rat, org_a_id, method
):
    tid, payload = resolution_rat
    url = f"/licitud/treatments/{tid}/assessments"
    async with client_for(client_a, org_a_id) as client:
        before = None
        if method == "patch":
            created = await client.post(url, json=payload)
            assert created.status_code == 201
            before = created.json()
            detail = url + "/" + before["id"]
        invalid = [
            {f: None}
            for f in [
                "context_binding",
                "context_hash",
                "created_by",
                "decision",
                "review_status",
                "approved",
            ]
        ] + [
            {"schema_version": 2},
            {"risks": None},
            {"completed_on": "invalid"},
            {"agency_consultation": {"status": "aprobada"}},
            {"performed_before_processing": {"answer": "no_aplica"}},
        ]
        for doc in invalid:
            response = (
                await client.post(
                    url, json={**payload, "eipd_resolution_assessment": doc}
                )
                if method == "create"
                else await client.patch(
                    detail,
                    json={
                        "justification": "No debe persistir",
                        "eipd_resolution_assessment": doc,
                    },
                )
            )
            assert response.status_code == 422, response.text
            if before:
                assert (await client.get(detail)).json() == before


@pytest.mark.parametrize(
    "basis",
    [
        "consentimiento_art12",
        "interes_legitimo_art13d",
        "contrato_precontractual_art13c",
        "obligacion_legal_art13b",
        "defensa_derechos_art13e",
        "obligaciones_economicas_art13a",
    ],
)
async def test_resolution_keeps_confirmation_blocked_six_bases(
    client_a,
    resolution_rat,
    org_a_id,
    complete_payload,
    complete_lia_context,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
    _session_factory,
    basis,
):
    tid, payload = resolution_rat
    if basis == "interes_legitimo_art13d":
        async with _session_factory() as db:
            db.add(
                TreatmentDataSource(
                    organization_id=org_a_id,
                    treatment_id=tid,
                    source_type="titular",
                    is_public_source=False,
                )
            )
            await db.commit()
    docs = {
        "consentimiento_art12": ("consent_assessment", complete_payload),
        "interes_legitimo_art13d": ("lia_assessment", complete_lia_context[0]),
        "contrato_precontractual_art13c": ("contract_assessment", complete_contract),
        "obligacion_legal_art13b": (
            "legal_obligation_assessment",
            complete_legal_obligation,
        ),
        "defensa_derechos_art13e": (
            "rights_defense_assessment",
            complete_rights_defense,
        ),
        "obligaciones_economicas_art13a": (
            "economic_obligations_assessment",
            complete_economic_obligations,
        ),
    }
    field, document = docs[basis]
    payload = {**deepcopy(payload), "legal_basis": basis, field: document}
    url = f"/licitud/treatments/{tid}/assessments"
    async with client_for(client_a, org_a_id) as client:
        first = await client.post(url, json=payload)
        assert first.status_code == 201
        first_url = url + "/" + first.json()["id"]
        assert (await client.post(first_url + "/confirm")).status_code == 200
        confirmed = (await client.get(first_url)).json()
        created = await client.post(
            url, json={**payload, "eipd_resolution_assessment": {}}
        )
        assert created.status_code == 201
        draft = created.json()
        detail = url + "/" + draft["id"]
        ready = (await client.get(detail + "/readiness")).json()
        assert {b["code"] for b in ready["confirmation_blockers"]} == {
            "resolucion_eipd_no_validada"
        }
        failed = await client.post(detail + "/confirm")
        assert failed.status_code == 409, failed.text
        assert (
            failed.json()["detail"]["confirmation_blockers"]
            == ready["confirmation_blockers"]
        )
        assert (await client.get(first_url)).json() == confirmed
        assert (await client.get(detail)).json() == draft
        cleared = await client.patch(detail, json={"eipd_resolution_assessment": None})
        assert cleared.status_code == 200
        assert (await client.post(detail + "/confirm")).status_code == 200
        for target in [detail, first_url]:
            assert (
                await client.patch(target, json={"eipd_resolution_assessment": {}})
            ).status_code == 409


async def test_document_respects_edit_permission_and_subscription(
    client_a, resolution_rat, org_a_id, profile_a_id, _session_factory
):
    tid, payload = resolution_rat
    url = f"/licitud/treatments/{tid}/assessments"
    membership = (Membership.organization_id == org_a_id) & (
        Membership.profile_id == profile_a_id
    )
    async with client_for(client_a, org_a_id) as client:
        created = await client.post(
            url, json={**payload, "eipd_resolution_assessment": {}}
        )
        assert created.status_code == 201
        before = created.json()
        detail = url + "/" + before["id"]
        async with _session_factory() as db:
            await db.execute(
                update(Membership).where(membership).values(role=UserRole.viewer)
            )
            await db.commit()
        try:
            assert (await client.get(detail)).json() == before
            assert (
                await client.patch(detail, json={"eipd_resolution_assessment": None})
            ).status_code == 403
            assert (
                await client.post(
                    url, json={**payload, "eipd_resolution_assessment": {}}
                )
            ).status_code == 403
        finally:
            async with _session_factory() as db:
                await db.execute(
                    update(Membership).where(membership).values(role=UserRole.owner)
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
            assert (
                await client.patch(detail, json={"eipd_resolution_assessment": None})
            ).status_code == 402
            assert (await client.get(detail)).status_code == 402
        finally:
            async with _session_factory() as db:
                await db.execute(
                    update(Subscription)
                    .where(Subscription.organization_id == org_a_id)
                    .values(status=SubscriptionStatus.active)
                )
                await db.commit()
        assert (await client.get(detail)).json() == before
