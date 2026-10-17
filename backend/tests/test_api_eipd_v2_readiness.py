from copy import deepcopy
from dataclasses import asdict

import pytest
from pydantic import ValidationError
from sqlalchemy import update

from app.db.models import Treatment, TreatmentDataCategory, TreatmentPurpose
from app.schemas.licitud import EipdReadinessV2Out
from app.services.eipd_screening_v2 import evaluate_eipd_screening_v2
from tests import test_api_eipd_resolution as api_fixtures
from tests import test_services_eipd_frontier as frontier_fixtures
from tests.eipd_selected_policy_fixtures import (
    explicit_review_policy as explicit_review_policy,
)

rat_m3 = api_fixtures.rat_m3
resolution_rat = api_fixtures.resolution_rat
complete_payload = api_fixtures.complete_payload
frontier_context = frontier_fixtures.frontier_context


@pytest.mark.parametrize("mode", ["valid", "version", "extra", "route", "approval"])
def test_output_contract_closed_and_versioned(frontier_context, mode):
    result = evaluate_eipd_screening_v2(frontier_context)
    data = asdict(result) | {"evaluation_version": 2}
    if mode == "version":
        data["evaluation_version"] = 1
    elif mode == "extra":
        data["approved"] = True
    elif mode == "route":
        data["frontier"]["route"] = "unsupported"
    elif mode == "approval":
        data["frontier"]["can_confirm"] = True
    if mode == "valid":
        assert EipdReadinessV2Out.model_validate(data).result == "requiere_eipd"
    else:
        with pytest.raises(ValidationError):
            EipdReadinessV2Out.model_validate(data)


@pytest.mark.parametrize("biometric", [False, True])
async def test_http_prepared_v2_keeps_v1_and_blockers(
    client_a,
    resolution_rat,
    org_a_id,
    _session_factory,
    sensitive_exception_context,
    biometric_exception_context,
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
        original = created.json()
        detail = f"/licitud/treatments/{tid}/assessments/{original['id']}"
        response = await client.get(detail + "/readiness")
        assert response.status_code == 200, response.text
        readiness = response.json()
        v2 = readiness["eipd_v2"]
        assert v2["evaluation_version"] == 2 and v2["result"] == "requiere_eipd"
        assert v2["frontier"]["result"] == "preparado", v2["frontier"]["issues"]
        assert v2["frontier"]["route"] == (
            "sensible_biometrica_derechos" if biometric else "sensible_derechos"
        )
        assert v2["frontier"]["screening"] == readiness["eipd"]
        assert readiness["eipd"]["result"] == "pendiente_revision"
        assert any(i["code"] == "supuesto_declarado" for i in v2["issues"])
        assert any(i["code"] == "excepcion_especial_preparada" for i in v2["issues"])
        assert any(
            b["code"] == "screening_eipd_no_preparado"
            for b in readiness["confirmation_blockers"]
        )
        assert (await client.post(detail + "/confirm")).status_code in (400, 409)
        assert (await client.get(detail)).json() == original
        assert (await client.get(detail + "/readiness")).json() == readiness
        patched = await client.patch(
            detail, json={"sensitive_rights_exception_assessment": {}}
        )
        assert patched.status_code == 200
        before = patched.json()
        incomplete = (await client.get(detail + "/readiness")).json()
        assert incomplete["eipd_v2"]["frontier"]["result"] != "preparado"
        assert incomplete["eipd_v2"]["issues"] == incomplete["eipd"]["issues"]
        assert (await client.get(detail)).json() == before


async def test_ordinary_and_unavailable_current_context(
    client_a, resolution_rat, org_a_id, org_b_id, _session_factory
):
    tid, payload = resolution_rat
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(
            f"/licitud/treatments/{tid}/assessments", json=payload
        )
        assert created.status_code == 201
        original = created.json()
        detail = f"/licitud/treatments/{tid}/assessments/{original['id']}"
        readiness = (await client.get(detail + "/readiness")).json()
        assert readiness["eipd_v2"]["result"] == "sin_supuestos_declarados"
        assert readiness["eipd_v2"]["frontier"]["result"] != "preparado"
        assert readiness["eipd_v2"]["frontier"]["screening"] == readiness["eipd"]
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == tid)
                .values(retention_rule="Nuevo plazo")
            )
            await db.commit()
        stale = (await client.get(detail + "/readiness")).json()
        assert (
            not stale["rat_context_current"] and not stale["eipd_v2"]["context_current"]
        )
        assert (await client.get(detail)).json() == original


async def test_current_rat_unavailable_does_not_use_stored_snapshot(
    client_a, resolution_rat, org_a_id, _session_factory
):
    tid, payload = resolution_rat
    async with api_fixtures.client_for(client_a, org_a_id) as client:
        created = await client.post(
            f"/licitud/treatments/{tid}/assessments", json=payload
        )
        assert created.status_code == 201
        original = created.json()
        detail = f"/licitud/treatments/{tid}/assessments/{original['id']}"
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentPurpose)
                .where(TreatmentPurpose.treatment_id == tid)
                .values(purpose="Finalidad cambiada")
            )
            await db.commit()
        response = await client.get(detail + "/readiness")
        assert response.status_code == 200, response.text
        readiness = response.json()
        v2 = readiness["eipd_v2"]
        assert v2["result"] == "pendiente_revision" and not v2["context_current"]
        assert v2["frontier"]["result"] == "incompleto"
        assert v2["frontier"]["screening"] is None
        assert any(
            i["code"] == "contexto_rat_no_disponible" for i in v2["frontier"]["issues"]
        )
        assert any(
            b["code"] == "contexto_rat_no_disponible"
            for b in readiness["confirmation_blockers"]
        )
        assert (await client.get(detail)).json() == original
