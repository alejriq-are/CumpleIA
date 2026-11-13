"""Frontera protegida preparada por HTTP, sin habilitar decisiones positivas."""

from copy import deepcopy

import pytest
import pytest_asyncio
from sqlalchemy import update

from app.db.models import TreatmentDataCategory
from tests import test_api_eipd_resolution as api_fixtures
from tests import test_services_eipd_resolution as resolution_fixtures
from tests.test_api_eipd_resolution_reviews import events, review

rat_m3 = api_fixtures.rat_m3
resolution_rat = api_fixtures.resolution_rat
complete_resolution = resolution_fixtures.complete_resolution


@pytest_asyncio.fixture
async def prepared_protected_assessment(
    client_a,
    resolution_rat,
    org_a_id,
    _session_factory,
    sensitive_exception_context,
    biometric_exception_context,
    complete_contract,
    complete_resolution,
    biometric,
):
    tid, payload = resolution_rat
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == tid)
            .values(is_sensitive=True)
        )
        await db.commit()
    data = deepcopy(payload)
    data.update(
        legal_basis="contrato_precontractual_art13c",
        contract_assessment=deepcopy(complete_contract),
    )
    if biometric:
        bio, _, special, sensitive = deepcopy(biometric_exception_context)
        bio["context"]["purpose_description"] = "Gestión de clientes"
        data["biometric_rights_exception_assessment"] = bio
    else:
        sensitive, _, special = deepcopy(sensitive_exception_context)
    sensitive["context"]["purpose_description"] = "Gestión de clientes"
    special.pop("context_binding")
    data.update(
        special_conditions=special, sensitive_rights_exception_assessment=sensitive
    )
    for answer in data["eipd_screening"]["answers"]:
        if answer["question_id"] == "datos_protegidos_excepcion_consentimiento":
            answer.update(answer="si", rationale="Excepcion documentada")
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(f"/licitud/treatments/{tid}/assessments", json=data)
        assert created.status_code == 201, created.text
        detail = f"/licitud/treatments/{tid}/assessments/{created.json()['id']}"
        snapshot = created.json()["rat_context_snapshot"]
        document = deepcopy(complete_resolution[0])
        document["purpose_description"] = snapshot["purpose"]
        document["scope"] = {
            "data_category_codes": [
                c["category_code"] for c in snapshot["data_categories"]
            ],
            "data_subject_codes": [
                c["category_code"] for c in snapshot["data_subjects"]
            ],
        }
        # Referencias sinteticas de test: nunca acreditan verificacion global.
        document["official_sources"]["sources"][0][
            "source_reference"
        ] = "TEST: fuente documental aportada por tenant"
        patched = await client.patch(
            detail, json={"eipd_resolution_assessment": document}
        )
        assert patched.status_code == 200, patched.text
        original = patched.json()
        return tid, detail, original


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("prior_negative", [False, True])
async def test_prepared_protected_http_retains_global_barriers_and_dependencies(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    org_b_id,
    _session_factory,
    biometric,
    prior_negative,
):
    tid, detail, original = prepared_protected_assessment
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        if prior_negative:
            negative = await client.post(
                detail + "/eipd-resolution/reviews", json=review("no_continuar")
            )
            assert negative.status_code == 201, negative.text
        before_events = [e.id for e in await events(_session_factory, original["id"])]
        readiness_response = await client.get(detail + "/readiness")
        assert readiness_response.status_code == 200, readiness_response.text
        readiness = readiness_response.json()
        controls = readiness["eipd_controls"]
        assert controls["preparation_result"] == "preparado", controls[
            "preparation_issues"
        ]
        assert controls["preparation_issues"] == []
        assert controls["ordinary"]["result"] == "completo"
        assert controls["resolution"]["result"] == "completo"
        assert controls["resolution"]["context_current"] is True
        assert controls["detection_v2"]["result"] == "requiere_eipd"
        assert controls["detection_v2"]["frontier"]["route"] == (
            "sensible_biometrica_derechos" if biometric else "sensible_derechos"
        )
        assert controls["detection_v2"]["frontier"]["screening"] == readiness["eipd"]
        assert readiness["eipd"]["result"] == "pendiente_revision"
        assert {i["code"] for i in controls["review_blockers"]} == {
            "fuentes_oficiales_no_verificadas",
            "gate_eipd_no_habilitado",
        }
        assert not any(i["stage"] == "review" for i in controls["review_blockers"])
        expected_review_code = (
            "decision_no_continuar" if prior_negative else "revision_ausente"
        )
        assert expected_review_code in {
            i["code"] for i in controls["confirmation_blockers"]
        }
        for suffix, request in [
            ("/eipd-resolution/reviews", review("continuar")),
            ("/confirm", None),
        ]:
            response = (
                await client.post(detail + suffix, json=request)
                if request
                else await client.post(detail + suffix)
            )
            assert response.status_code == 409, response.text
            assert response.json()["detail"]["eipd_controls"] == controls
        assert (await client.get(detail)).json() == original
        assert (await client.get(detail + "/readiness")).json() == readiness
        assert [
            e.id for e in await events(_session_factory, original["id"])
        ] == before_events
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        # Una dependencia retirada invalida preparacion y asociacion del expediente.
        changed = await client.patch(
            detail, json={"sensitive_rights_exception_assessment": {}}
        )
        assert changed.status_code == 200, changed.text
        after = (await client.get(detail + "/readiness")).json()["eipd_controls"]
        assert after["preparation_result"] != "preparado"
        assert any(i["stage"] == "frontier" for i in after["preparation_issues"])
        assert after["resolution"]["context_current"] is False
        if prior_negative:
            assert after["review_state"]["review_status"] == "obsoleta"
        for suffix, request in [
            ("/eipd-resolution/reviews", review("continuar")),
            ("/confirm", None),
        ]:
            response = (
                await client.post(detail + suffix, json=request)
                if request
                else await client.post(detail + suffix)
            )
            assert response.status_code in (400, 409), response.text
        assert (await client.get(detail)).json() == changed.json()
        assert [
            e.id for e in await events(_session_factory, original["id"])
        ] == before_events


@pytest.mark.parametrize("biometric", [False, True])
@pytest.mark.parametrize("operation", ["review", "confirm"])
@pytest.mark.parametrize("commit_change", [False, True])
async def test_protected_preparation_reread_after_dependency_lock(
    client_a,
    prepared_protected_assessment,
    org_a_id,
    profile_a_id,
    auth_a_id,
    _app_session_factory,
    _session_factory,
    biometric,
    operation,
    commit_change,
):
    import asyncio
    from uuid import UUID

    from fastapi import HTTPException
    from sqlalchemy import select, text

    from app.db.models import LegalAssessment, LegalAssessmentSeries
    from app.schemas.licitud import EipdResolutionReviewIn, LegalAssessmentDraftUpdate
    from app.services.licitud import (
        confirm_legal_assessment_v1,
        record_eipd_resolution_review_v1,
        update_legal_assessment_draft_v1,
    )

    tid, detail, original = prepared_protected_assessment
    aid = UUID(original["id"])
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        negative = await client.post(
            detail + "/eipd-resolution/reviews", json=review("no_continuar")
        )
        assert negative.status_code == 201, negative.text
        event_ids = [e.id for e in await events(_session_factory, original["id"])]
        before = (await client.get(detail + "/readiness")).json()["eipd_controls"]
        assert before["preparation_result"] == "preparado"
        assert before["review_state"]["review_status"] == "vigente"
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
            # Carga previa intencional: populate_existing debe refrescar tras espera.
            await waiter.scalar(
                select(LegalAssessment).where(LegalAssessment.id == aid)
            )
            pid = await waiter.scalar(text("SELECT pg_backend_pid()"))
            await update_legal_assessment_draft_v1(
                holder,
                org_a_id,
                tid,
                aid,
                profile_a_id,
                LegalAssessmentDraftUpdate(sensitive_rights_exception_assessment={}),
            )
            if operation == "review":
                call = record_eipd_resolution_review_v1(
                    waiter,
                    org_a_id,
                    tid,
                    aid,
                    profile_a_id,
                    EipdResolutionReviewIn(**review("continuar")),
                )
            else:
                call = confirm_legal_assessment_v1(
                    waiter, org_a_id, tid, aid, profile_a_id
                )
            task = asyncio.create_task(call)
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
                if commit_change:
                    assert controls["preparation_result"] != "preparado"
                    assert any(
                        i["stage"] == "frontier" for i in controls["preparation_issues"]
                    )
                    assert controls["resolution"]["context_current"] is False
                    assert controls["review_state"]["review_status"] == "obsoleta"
                else:
                    assert controls == before
                assert {
                    "fuentes_oficiales_no_verificadas",
                    "gate_eipd_no_habilitado",
                } <= {i["code"] for i in controls["review_blockers"]}
                assert (
                    controls["review_state"]["latest_review"]["id"]
                    == negative.json()["id"]
                )
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
        after = (await client.get(detail)).json()
        assert after["status"] == "borrador"
        assert (
            after["eipd_resolution_assessment"]
            == original["eipd_resolution_assessment"]
        )
        if commit_change:
            assert after["sensitive_rights_exception_assessment"] == (
                LegalAssessmentDraftUpdate(
                    sensitive_rights_exception_assessment={}
                ).model_dump(mode="json")["sensitive_rights_exception_assessment"]
            )
        else:
            assert after == original
        assert [
            e.id for e in await events(_session_factory, original["id"])
        ] == event_ids
