"""Flujo HTTP M3 contra PostgreSQL/app_user con RLS y contexto RAT real."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select, update

from app.db.models import (
    LegalAssessment,
    LegalAssessmentSeries,
    Membership,
    Subscription,
    SubscriptionStatus,
    Treatment,
    TreatmentDataCategory,
    TreatmentDataSubject,
    TreatmentPurpose,
    UserRole,
)
from app.services.eipd import build_eipd_context_binding_hash_v12
from tests.eipd_selected_policy_fixtures import (
    explicit_review_policy as explicit_review_policy,
)


@pytest.fixture
def complete_payload():
    ids = [
        "consentimiento_libre",
        "consentimiento_informado",
        "consentimiento_especifico_finalidad",
        "consentimiento_previo",
        "voluntad_inequivoca",
        "accion_afirmativa_clara",
        "revocacion_posible",
        "revocacion_medio_equivalente",
        "revocacion_expedita",
        "revocacion_fidedigna",
        "revocacion_gratuita",
        "revocacion_disponible_permanentemente",
        "responsable_puede_acreditar",
    ]
    return {
        "given_by": "titular",
        "grant_method": "electronico",
        "answers": [{"question_id": q, "answer": "si"} for q in ids]
        + [{"question_id": "contexto_contrato_servicio", "answer": "no"}],
    }


@pytest_asyncio.fixture
async def rat_m3(_session_factory, org_a_id, negative_controls):
    treatment_id, purpose_id = uuid.uuid4(), uuid.uuid4()
    async with _session_factory() as db:
        db.add(
            Treatment(
                id=treatment_id,
                organization_id=org_a_id,
                name="API M3",
                organization_role="responsable",
                retention_rule="5 años",
                has_automated_decisions=False,
            )
        )
        await db.flush()
        common = {"treatment_id": treatment_id, "organization_id": org_a_id}
        db.add_all(
            [
                TreatmentPurpose(
                    **common, id=purpose_id, purpose="Gestión de clientes"
                ),
                TreatmentDataCategory(
                    **common,
                    category_code="id",
                    category_name="Identidad",
                    is_sensitive=False,
                ),
                TreatmentDataSubject(
                    **common,
                    category_code="clientes",
                    category_name="Clientes",
                    includes_children=False,
                    includes_adolescents=False,
                    is_vulnerable_group=False,
                ),
            ]
        )
        await db.commit()
    yield treatment_id, {
        **negative_controls,
        "purpose_id": str(purpose_id),
        "scope": {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]},
        "legal_basis": "consentimiento_art12",
        "justification": "Finalidad documentada",
    }
    async with _session_factory() as db:
        await db.execute(
            delete(LegalAssessment).where(LegalAssessment.treatment_id == treatment_id)
        )
        await db.execute(
            delete(LegalAssessmentSeries).where(
                LegalAssessmentSeries.treatment_id == treatment_id
            )
        )
        await db.execute(delete(Treatment).where(Treatment.id == treatment_id))
        await db.commit()


async def test_api_flujo_completo_y_reemplazo(
    client_a, rat_m3, complete_payload, org_a_id, profile_a_id
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    headers = {"X-Organization-Id": str(org_a_id)}
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test", headers=headers
    ) as client:
        first = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        approved = await client.post(first_url + "/confirm")
        assert approved.status_code == 200, approved.text
        assert approved.json()["status"] == "confirmado"
        assert approved.json()["confirmed_by"] == str(profile_a_id)
        assert approved.json()["confirmed_at"]
        second = await client.post(url, json=payload)
        assert second.status_code == 201, second.text
        assert second.json()["version"] == 2
        second_url = url + "/" + second.json()["id"]
        failed = await client.post(second_url + "/confirm")
        assert failed.status_code == 400
        assert failed.json()["detail"]["result"] == "incompleto"
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        complete_payload["evidence"] = [
            {"evidence_type": "registro", "obtained_on": "2026-10-05"}
        ]
        saved = await client.patch(
            second_url,
            json={
                "consent_assessment": complete_payload,
                "special_conditions": payload["special_conditions"],
                "eipd_screening": payload["eipd_screening"],
            },
        )
        assert saved.status_code == 200, saved.text
        assert (
            saved.json()["consent_assessment"]["evidence"][0]["obtained_on"]
            == "2026-10-05"
        )
        assert (await client.post(second_url + "/confirm")).status_code == 200
        historical = (await client.get(first_url)).json()
        assert historical["status"] == "reemplazado"
        assert historical["replaced_by_assessment_id"] == second.json()["id"]
        assert (await client.get(second_url)).json()["status"] == "confirmado"
        assert (
            await client.patch(second_url, json={"justification": "Cambio"})
        ).status_code == 409
        assert (await client.post(second_url + "/confirm")).status_code == 409


async def test_api_rechaza_contexto_rat_cambiado(
    client_a, rat_m3, complete_payload, org_a_id, _session_factory
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    headers = {"X-Organization-Id": str(org_a_id)}
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test", headers=headers
    ) as client:
        created = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert created.status_code == 201
        detail_url = url + "/" + created.json()["id"]
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == treatment_id)
                .values(retention_rule="10 años")
            )
            await db.commit()
        assert (await client.post(detail_url + "/confirm")).status_code == 409
        assert (await client.get(detail_url)).json()["status"] == "borrador"
        assert (await client.patch(detail_url, json={})).status_code == 200
        assert (await client.post(detail_url + "/confirm")).status_code == 409
        assert (
            await client.patch(
                detail_url,
                json={
                    "special_conditions": payload["special_conditions"],
                    "eipd_screening": payload["eipd_screening"],
                },
            )
        ).status_code == 200
        assert (await client.post(detail_url + "/confirm")).status_code == 200


async def test_api_tenant_y_estructura(client_a, rat_m3, org_a_id, org_b_id):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    headers = {"X-Organization-Id": str(org_a_id)}
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test"
    ) as client:
        assert (
            await client.post(
                url, json=payload, headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        assert (
            await client.post(
                url,
                json={**payload, "consent_assessment": {"schema_version": 2}},
                headers=headers,
            )
        ).status_code == 422
        assert (await client.post(url, json=payload)).status_code == 422
        created = await client.post(url, json=payload, headers=headers)
        assert created.status_code == 201
        wrong_url = (
            f"/licitud/treatments/{uuid.uuid4()}/assessments/{created.json()['id']}"
        )
        assert (await client.get(wrong_url, headers=headers)).status_code == 404
        assert (
            await client.post(wrong_url + "/confirm", headers=headers)
        ).status_code == 404


@pytest.mark.parametrize("role", [UserRole.viewer, UserRole.editor])
async def test_api_permisos_lectura_edicion_y_confirmacion(
    client_a, rat_m3, org_a_id, profile_a_id, _session_factory, role
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    headers = {"X-Organization-Id": str(org_a_id)}
    async with AsyncClient(
        transport=ASGITransport(app=client_a), base_url="http://test", headers=headers
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201
        detail_url = url + "/" + created.json()["id"]
        condition = (Membership.organization_id == org_a_id) & (
            Membership.profile_id == profile_a_id
        )
        async with _session_factory() as db:
            original = (
                await db.execute(select(Membership.role).where(condition))
            ).scalar_one()
            await db.execute(update(Membership).where(condition).values(role=role))
            await db.commit()
        try:
            assert (await client.get(detail_url)).status_code == 200
            assert (await client.get(detail_url + "/readiness")).status_code == 200
            assert (await client.post(url, json=payload)).status_code == (
                403 if role == UserRole.viewer else 409
            )
            assert (await client.patch(detail_url, json={})).status_code == (
                403 if role == UserRole.viewer else 200
            )
            assert (await client.post(detail_url + "/confirm")).status_code == (
                403 if role == UserRole.viewer else 400
            )
        finally:
            async with _session_factory() as db:
                await db.execute(
                    update(Membership).where(condition).values(role=original)
                )
                await db.commit()


async def test_api_suscripcion_suspendida_bloquea_y_grace_permite(
    client_a, rat_m3, org_a_id, _session_factory
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    headers = {"X-Organization-Id": str(org_a_id)}
    async with _session_factory() as db:
        original = (
            await db.execute(
                select(Subscription.status).where(
                    Subscription.organization_id == org_a_id
                )
            )
        ).scalar_one()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=client_a),
            base_url="http://test",
            headers=headers,
        ) as client:
            for subscription_status, expected in [
                (SubscriptionStatus.suspended, 402),
                (SubscriptionStatus.grace, 201),
            ]:
                async with _session_factory() as db:
                    await db.execute(
                        update(Subscription)
                        .where(Subscription.organization_id == org_a_id)
                        .values(status=subscription_status)
                    )
                    await db.commit()
                response = await client.post(url, json=payload)
                assert response.status_code == expected, response.text
    finally:
        async with _session_factory() as db:
            await db.execute(
                update(Subscription)
                .where(Subscription.organization_id == org_a_id)
                .values(status=original)
            )
            await db.commit()


async def test_api_lia_borrador_persistencia_y_confirmacion_bloqueada(
    client_a, rat_m3, org_a_id
):
    treatment_id, payload = rat_m3
    payload["legal_basis"] = "interes_legitimo_art13d"
    payload["lia_assessment"] = {
        "purpose_and_interest": {"legitimate_interest": " Gestión de clientes "}
    }
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail_url = url + "/" + created.json()["id"]
        assert (await client.get(detail_url)).json()["lia_assessment"][
            "purpose_and_interest"
        ]["legitimate_interest"] == " Gestión de clientes "
        updated = await client.patch(
            detail_url,
            json={"lia_assessment": {"conclusion": {"decision": "puede_basarse"}}},
        )
        assert updated.status_code == 200, updated.text
        assert (
            updated.json()["lia_assessment"]["purpose_and_interest"][
                "legitimate_interest"
            ]
            is None
        )
        assert (
            await client.patch(detail_url, json={"justification": "Revisión"})
        ).json()["lia_assessment"]["conclusion"]["decision"] == "puede_basarse"
        assert (await client.post(detail_url + "/confirm")).status_code == 400
        assert (await client.get(detail_url)).json()["status"] == "borrador"
        invalid = await client.patch(
            detail_url,
            json={"lia_assessment": {"conclusion": {"decision": "aprobado"}}},
        )
        assert invalid.status_code == 422
        assert (
            await client.patch(detail_url, json={"lia_assessment": None})
        ).status_code == 200
        assert (await client.get(detail_url)).json()["lia_assessment"] is None


async def test_api_screening_binding_revalidacion_y_null(
    client_a, rat_m3, org_a_id, org_b_id, _session_factory
):
    treatment_id, payload = rat_m3
    payload["eipd_screening"] = {
        "answers": [
            {"question_id": "tratamiento_masivo_o_gran_escala", "answer": "pendiente"}
        ]
    }
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail_url = url + "/" + created.json()["id"]
        original = created.json()
        binding = original["eipd_screening"]["context_binding"]["hash"]
        assert binding == build_eipd_context_binding_hash_v12(
            original["rat_context_snapshot"],
            None,
            original["special_conditions"],
            original["contract_assessment"],
            original["legal_obligation_assessment"],
            original["rights_defense_assessment"],
            None,
            None,
            None,
            None,
            None,
            legal_basis=original["legal_basis"],
        )
        assert (
            await client.get(detail_url, headers={"X-Organization-Id": str(org_b_id)})
        ).status_code == 403
        spoofed = await client.patch(
            detail_url, json={"eipd_screening": {"context_binding": {"hash": "a" * 64}}}
        )
        assert spoofed.status_code == 422
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == treatment_id)
                .values(deletion_method="Borrado revisado")
            )
            await db.commit()
        updated = await client.patch(detail_url, json={})
        assert updated.status_code == 200, updated.text
        changed = updated.json()
        assert changed["rat_context_hash"] == original["rat_context_hash"]
        assert changed["eipd_screening"]["context_binding"]["hash"] == binding
        assert (
            build_eipd_context_binding_hash_v12(
                changed["rat_context_snapshot"],
                None,
                changed["special_conditions"],
                changed["contract_assessment"],
                changed["legal_obligation_assessment"],
                changed["rights_defense_assessment"],
                None,
                None,
                None,
                None,
                None,
                legal_basis=changed["legal_basis"],
            )
            != binding
        )
        combined = await client.patch(
            detail_url,
            json={
                "lia_assessment": {"conclusion": {"balancing_summary": "Revisión"}},
                "eipd_screening": {},
            },
        )
        assert combined.status_code == 200, combined.text
        final = combined.json()
        assert final["eipd_screening"]["context_binding"][
            "hash"
        ] == build_eipd_context_binding_hash_v12(
            final["rat_context_snapshot"],
            final["lia_assessment"],
            final["special_conditions"],
            final["contract_assessment"],
            final["legal_obligation_assessment"],
            final["rights_defense_assessment"],
            None,
            None,
            None,
            None,
            None,
            legal_basis=final["legal_basis"],
        )
        assert (await client.get(detail_url)).json()["eipd_screening"] == final[
            "eipd_screening"
        ]
        assert (
            await client.patch(detail_url, json={"eipd_screening": None})
        ).status_code == 200
        assert (await client.get(detail_url)).json()["eipd_screening"] is None


async def test_api_preparacion_consentimiento_lectura_sin_escrituras(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    complete_payload,
    _session_factory,
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201
        detail_url = url + "/" + created.json()["id"]
        prep = await client.get(detail_url + "/readiness")
        assert prep.status_code == 200, prep.text
        data = prep.json()
        assert data["consent"]["result"] == "incompleto"
        assert data["lia"] is None
        assert data["eipd"]["result"] == "sin_supuestos_declarados"
        assert data["rat_context_current"] is True
        assert "consentimiento_no_preparado" in [
            b["code"] for b in data["confirmation_blockers"]
        ]
        assert data["pending_controls"]
        assert (
            await client.get(
                detail_url + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        wrong = f"/licitud/treatments/{uuid.uuid4()}/assessments/{created.json()['id']}/readiness"
        assert (await client.get(wrong)).status_code == 404
        await client.patch(
            detail_url,
            json={
                "consent_assessment": complete_payload,
                "special_conditions": payload["special_conditions"],
                "eipd_screening": payload["eipd_screening"],
            },
        )
        async with _session_factory() as db:
            before = (
                await db.execute(
                    select(LegalAssessment.updated_at).where(
                        LegalAssessment.id == uuid.UUID(created.json()["id"])
                    )
                )
            ).scalar_one()
        original = (await client.get(detail_url)).json()
        complete = (await client.get(detail_url + "/readiness")).json()
        assert complete["consent"]["result"] == "completo"
        assert complete["confirmation_blockers"] == []
        assert complete["pending_controls"]  # No certifica cobertura transversal.
        assert (await client.get(detail_url)).json() == original
        async with _session_factory() as db:
            after = (
                await db.execute(
                    select(LegalAssessment.updated_at).where(
                        LegalAssessment.id == uuid.UUID(created.json()["id"])
                    )
                )
            ).scalar_one()
        assert before == after
        assert (await client.post(detail_url + "/confirm")).status_code == 200
        history = (await client.get(detail_url + "/readiness")).json()
        assert "evaluacion_no_editable" in [
            b["code"] for b in history["confirmation_blockers"]
        ]


async def test_api_preparacion_lia_eipd_actual_y_desactualizado(
    client_a, rat_m3, org_a_id, _session_factory
):
    treatment_id, payload = rat_m3
    payload["legal_basis"] = "interes_legitimo_art13d"
    payload["lia_assessment"] = {"impact": {"severity": "alta"}}
    ids = [
        "evaluacion_sistematica_automatizada_efectos_significativos",
        "tratamiento_masivo_o_gran_escala",
        "monitoreo_sistematico_zona_publica",
        "datos_protegidos_excepcion_consentimiento",
        "probable_alto_riesgo_contextual",
    ]
    screening = {
        "answers": [
            {"question_id": q, "answer": "no", "rationale": "Fundamento"} for q in ids
        ]
    }
    payload["eipd_screening"] = screening
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail_url = url + "/" + created.json()["id"]
        result = await client.get(detail_url + "/readiness")
        assert result.status_code == 200, result.text
        data = result.json()
        assert data["consent"] is None
        assert data["lia"]["result"] == "incompleto"
        assert data["eipd"]["result"] == "sin_supuestos_declarados"
        assert data["eipd"]["observations"][0]["code"] == "valoracion_lia_alta"
        assert {
            "lia_no_preparada",
        } <= {b["code"] for b in data["confirmation_blockers"]}
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == treatment_id)
                .values(deletion_method="Nueva regla")
            )
            await db.commit()
        changed = (await client.get(detail_url + "/readiness")).json()
        assert changed["rat_context_current"] is True
        assert changed["eipd"]["context_current"] is False
        assert changed["eipd"]["result"] == "pendiente_revision"
        assert changed["eipd"]["issues"][0]["code"] == "contexto_desactualizado"
        # La lectura no guarda el contexto nuevo ni reasocia el screening.
        assert (await client.get(detail_url)).json()[
            "rat_context_snapshot"
        ] == created.json()["rat_context_snapshot"]
        screening["answers"][1]["answer"] = "si"
        assert (
            await client.patch(detail_url, json={"eipd_screening": screening})
        ).status_code == 200
        positive = (await client.get(detail_url + "/readiness")).json()
        assert positive["eipd"]["result"] == "requiere_eipd"
        assert positive["eipd"]["issues"][0]["code"] == "supuesto_declarado"
        assert (await client.post(detail_url + "/confirm")).status_code == 400


async def test_api_preparacion_contexto_inaccesible_y_semantico_cambiado(
    client_a, rat_m3, org_a_id, _session_factory
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        detail_url = url + "/" + created.json()["id"]
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == treatment_id)
                .values(retention_rule="Nueva conservación")
            )
            await db.commit()
        current = (await client.get(detail_url + "/readiness")).json()
        assert current["rat_context_current"] is False
        assert "contexto_rat_desactualizado" in [
            b["code"] for b in current["confirmation_blockers"]
        ]
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentPurpose)
                .where(TreatmentPurpose.id == uuid.UUID(payload["purpose_id"]))
                .values(purpose="Finalidad distinta")
            )
            await db.commit()
        result = await client.get(detail_url + "/readiness")
        assert result.status_code == 200, result.text
        unavailable = result.json()
        assert unavailable["rat_context_current"] is None
        assert "contexto_rat_no_disponible" in [
            b["code"] for b in unavailable["confirmation_blockers"]
        ]
        assert unavailable["eipd"]["result"] == "pendiente_revision"


async def test_api_condiciones_especiales_guardado_asociacion_y_borrado(
    client_a, rat_m3, org_a_id, complete_payload
):
    treatment_id, payload = rat_m3
    payload["legal_basis"] = "consentimiento_art12"
    payload["justification"] = "Evaluación de condiciones especiales"
    payload["consent_assessment"] = complete_payload
    payload["special_conditions"] = {
        "declarations": [{"question_id": "datos_sensibles", "answer": "pendiente"}]
    }
    payload["eipd_screening"] = {}
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        assert original["special_conditions"]["context_binding"]["schema_version"] == 11
        assert original["eipd_screening"]["context_binding"]["schema_version"] == 12
        assert original["eipd_screening"]["context_binding"][
            "hash"
        ] == build_eipd_context_binding_hash_v12(
            original["rat_context_snapshot"],
            original["lia_assessment"],
            original["special_conditions"],
            original["contract_assessment"],
            original["legal_obligation_assessment"],
            original["rights_defense_assessment"],
            None,
            None,
            None,
            None,
            None,
            legal_basis=original["legal_basis"],
        )
        assert (await client.post(detail + "/confirm")).status_code == 400
        bad = await client.patch(
            detail,
            json={
                "special_conditions": {
                    "declarations": [
                        {
                            "question_id": "datos_sensibles",
                            "answer": "no",
                            "data_category_codes": ["fuera_del_rat"],
                        }
                    ]
                }
            },
        )
        assert bad.status_code == 400
        assert (await client.get(detail)).json()["special_conditions"] == original[
            "special_conditions"
        ]
        changed = await client.patch(
            detail, json={"special_conditions": {"notes": "Revisión"}}
        )
        assert changed.status_code == 200, changed.text
        assert changed.json()["eipd_screening"] == original["eipd_screening"]
        readiness = await client.get(detail + "/readiness")
        assert readiness.status_code == 200, readiness.text
        assert readiness.json()["eipd"]["context_current"] is False
        assert readiness.json()["special"]["result"] == "incompleto"
        assert readiness.json()["special"]["context_current"] is True
        assert "pregunta_omitida" in [
            i["code"] for i in readiness.json()["special"]["issues"]
        ]
        deleted = await client.patch(detail, json={"special_conditions": None})
        assert deleted.status_code == 200, deleted.text
        assert (await client.get(detail)).json()["special_conditions"] is None


async def test_api_contraste_eipd_especial_sin_mutaciones(client_a, rat_m3, org_a_id):
    treatment_id, payload = rat_m3
    payload["special_conditions"] = {
        "conditions": [
            {"regime_id": "sensibles_art16", "authorization_route": "excepcion_legal"}
        ]
    }
    payload["eipd_screening"] = {
        "answers": [
            {
                "question_id": "datos_protegidos_excepcion_consentimiento",
                "answer": "no",
                "rationale": "Revisado",
            }
        ]
    }
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        response = await client.get(detail + "/readiness")
        assert response.status_code == 200, response.text
        eipd = response.json()["eipd"]
        assert eipd["context_current"] and eipd["result"] == "pendiente_revision"
        assert {
            "excepcion_especial_no_validada",
            "excepcion_consentimiento_discordante",
        }.issubset({i["code"] for i in eipd["issues"]})
        assert (await client.get(detail)).json() == before


async def test_api_motivos_transversales_compartidos_y_rollback(
    client_a, rat_m3, complete_payload, org_a_id
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        previous = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert previous.status_code == 201
        previous_url = url + "/" + previous.json()["id"]
        assert (await client.post(previous_url + "/confirm")).status_code == 200
        payload.update(
            consent_assessment=complete_payload,
            special_conditions=None,
            eipd_screening=None,
        )
        created = await client.post(url, json=payload)
        assert created.status_code == 201
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        prep = (await client.get(detail + "/readiness")).json()
        failed = await client.post(detail + "/confirm")
        assert failed.status_code == 400, failed.text
        assert (
            failed.json()["detail"]["confirmation_blockers"]
            == prep["confirmation_blockers"]
        )
        for control in ("special", "eipd"):
            assert failed.json()["detail"][control] == prep[control]
        assert (await client.get(detail)).json() == before
        assert (await client.get(previous_url)).json()["status"] == "confirmado"


async def test_api_lia_confirmacion_reemplazo_y_motivos(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    complete_lia_context,
    negative_controls,
    _session_factory,
):
    from app.db.models import TreatmentDataSource

    treatment_id, payload = rat_m3
    async with _session_factory() as db:
        db.add(
            TreatmentDataSource(
                organization_id=org_a_id,
                treatment_id=treatment_id,
                source_type="titular",
                is_public_source=False,
            )
        )
        await db.commit()
    lia, _ = complete_lia_context
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        assert (await client.post(first_url + "/confirm")).status_code == 200
        second = await client.post(
            url,
            json={
                **payload,
                "legal_basis": "interes_legitimo_art13d",
                "lia_assessment": {"conclusion": {"decision": "puede_basarse"}},
            },
        )
        assert second.status_code == 201, second.text
        second_url = url + "/" + second.json()["id"]
        prep = (await client.get(second_url + "/readiness")).json()
        assert "base_no_implementada" not in {
            b["code"] for b in prep["confirmation_blockers"]
        }
        rejected = await client.post(second_url + "/confirm")
        assert rejected.status_code == 400, rejected.text
        assert rejected.json()["detail"]["code"] == "lia_no_preparada"
        for field in ("result", "issues", "applicability"):
            assert rejected.json()["detail"][field] == prep["lia"][field]
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        saved = await client.patch(
            second_url, json={"lia_assessment": lia, **negative_controls}
        )
        assert saved.status_code == 200, saved.text
        ready = (await client.get(second_url + "/readiness")).json()
        assert ready["lia"]["result"] == "completo", ready
        assert ready["consent"] is None and not ready["confirmation_blockers"]
        positive = negative_controls["eipd_screening"]
        positive["answers"][1]["answer"] = "si"
        assert (
            await client.patch(second_url, json={"eipd_screening": positive})
        ).status_code == 200
        assert (await client.post(second_url + "/confirm")).status_code == 409
        positive["answers"][1]["answer"] = "no"
        assert (
            await client.patch(second_url, json={"eipd_screening": positive})
        ).status_code == 200
        approved = await client.post(second_url + "/confirm")
        assert approved.status_code == 200, approved.text
        assert approved.json()["consent_assessment"] is None
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        third = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert third.status_code == 201, third.text
        third_url = url + "/" + third.json()["id"]
        assert (await client.post(third_url + "/confirm")).status_code == 200
        assert (await client.get(second_url)).json()["status"] == "reemplazado"
        assert (await client.post(second_url + "/confirm")).status_code == 409


async def test_api_contrato_persistencia_asociaciones_y_historicos(
    client_a, rat_m3, org_a_id, org_b_id, _session_factory, negative_controls
):
    from app.services.eipd import bind_eipd_screening_v2
    from app.services.special_conditions import bind_special_conditions_v1

    treatment_id, payload = rat_m3
    payload.update(
        legal_basis="contrato_precontractual_art13c",
        contract_assessment={
            "route": "medidas_precontractuales",
            "evidence": [{"evidence_type": "solicitud", "obtained_on": "2026-10-05"}],
        },
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        assert (
            original["contract_assessment"]["evidence"][0]["obtained_on"]
            == "2026-10-05"
        )
        assert (await client.post(detail + "/confirm")).status_code == 400
        assert (
            await client.get(detail, headers={"X-Organization-Id": str(org_b_id)})
        ).status_code == 403
        for invalid in (
            {"route": "otra"},
            {"schema_version": 2},
            {"approved": True},
            {"holder_is_party": {"answer": "no_aplica"}},
            {"evidence": [{"evidence_type": "contrato", "obtained_on": "invalid"}]},
        ):
            assert (
                await client.patch(detail, json={"contract_assessment": invalid})
            ).status_code == 422
        assert (await client.get(detail)).json() == original
        assert (
            await client.patch(detail, json={"justification": "Revisión documental"})
        ).status_code == 200
        assert (await client.get(detail)).json()["contract_assessment"] == original[
            "contract_assessment"
        ]
        # Changing only the contract keeps both associations and makes them stale.
        changed = await client.patch(
            detail, json={"contract_assessment": {"notes": "Nueva revisión"}}
        )
        assert changed.status_code == 200, changed.text
        assert changed.json()["special_conditions"] == original["special_conditions"]
        assert changed.json()["eipd_screening"] == original["eipd_screening"]
        prep = (await client.get(detail + "/readiness")).json()
        assert (
            not prep["special"]["context_current"]
            and not prep["eipd"]["context_current"]
        )
        final = await client.patch(
            detail,
            json={
                "contract_assessment": payload["contract_assessment"],
                **negative_controls,
            },
        )
        assert final.status_code == 200, final.text
        assert (await client.get(detail + "/readiness")).json()["special"][
            "context_current"
        ]
        # Simulate stored pre-contract associations, then verify no silent rewrite.
        old_special = bind_special_conditions_v1(
            negative_controls["special_conditions"],
            original["rat_context_snapshot"],
            original["legal_basis"],
            None,
            None,
        ).model_dump(mode="json")
        old_eipd = bind_eipd_screening_v2(
            negative_controls["eipd_screening"],
            original["rat_context_snapshot"],
            None,
            old_special,
        ).model_dump(mode="json")
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == uuid.UUID(original["id"]))
                .values(special_conditions=old_special, eipd_screening=old_eipd)
            )
            await db.commit()
        prep = (await client.get(detail + "/readiness")).json()
        for control in ("special", "eipd"):
            assert "asociacion_contractual_no_cubierta" in {
                i["code"] for i in prep[control]["issues"]
            }
        historical = (await client.get(detail)).json()
        assert (
            historical["special_conditions"] == old_special
            and historical["eipd_screening"] == old_eipd
        )
        from sqlalchemy.exc import IntegrityError

        async with _session_factory() as db:
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        update(LegalAssessment)
                        .where(LegalAssessment.id == uuid.UUID(original["id"]))
                        .values(contract_assessment=[])
                    )
            await db.rollback()
        assert (
            await client.patch(
                detail,
                headers={"X-Organization-Id": str(org_b_id)},
                json={"contract_assessment": {}},
            )
        ).status_code == 403
        deleted = await client.patch(detail, json={"contract_assessment": None})
        assert deleted.status_code == 200, deleted.text
        assert (await client.get(detail)).json()["contract_assessment"] is None
        async with _session_factory() as db:
            assert (
                await db.execute(
                    select(LegalAssessment.id).where(
                        LegalAssessment.id == uuid.UUID(original["id"]),
                        LegalAssessment.contract_assessment.is_(None),
                    )
                )
            ).scalar_one()


async def test_api_preparacion_contractual_completa_y_contexto_actual(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    complete_contract,
    negative_controls,
    _session_factory,
):
    treatment_id, payload = rat_m3
    payload.update(legal_basis="contrato_precontractual_art13c", contract_assessment={})
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        initial = (await client.get(detail + "/readiness")).json()
        assert initial["contract"]["result"] == "incompleto"
        assert "contrato_no_preparado" in {
            b["code"] for b in initial["confirmation_blockers"]
        }
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        saved = await client.patch(
            detail, json={"contract_assessment": complete_contract, **negative_controls}
        )
        assert saved.status_code == 200, saved.text
        before = (await client.get(detail)).json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["contract"]["result"] == "completo"
        assert ready["confirmation_blockers"] == []
        assert (await client.get(detail)).json() == before
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == treatment_id)
                .values(organization_role="encargado")
            )
            await db.commit()
        current = (await client.get(detail + "/readiness")).json()
        assert current["contract"]["result"] == "requiere_revision"
        assert "rol_no_admitido" in {i["code"] for i in current["contract"]["issues"]}
        assert (
            not current["special"]["context_current"]
            and not current["eipd"]["context_current"]
        )
        assert (await client.get(detail)).json() == before


async def test_api_confirmacion_contractual_motivos_reemplazo_y_precontrato(
    client_a, rat_m3, org_a_id, complete_contract, complete_payload, negative_controls
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        assert (await client.post(first_url + "/confirm")).status_code == 200
        second = await client.post(
            url,
            json={
                **payload,
                "legal_basis": "contrato_precontractual_art13c",
                "contract_assessment": {},
            },
        )
        assert second.status_code == 201
        detail = url + "/" + second.json()["id"]
        before = (await client.get(detail)).json()
        prep = (await client.get(detail + "/readiness")).json()
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 400
        assert rejected.json()["detail"]["code"] == "contrato_no_preparado"
        for field in ("result", "issues", "applicability"):
            assert rejected.json()["detail"][field] == prep["contract"][field]
        assert (await client.get(detail)).json() == before
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        complete_contract.update(
            route="medidas_precontractuales",
            precontractual_measures="Preparar oferta",
            requested_by_holder={"answer": "si", "rationale": "Solicitud documentada"},
            request_reference="Referencia solicitud",
        )
        complete_contract.pop("contractual_reference")
        saved = await client.patch(
            detail, json={"contract_assessment": complete_contract, **negative_controls}
        )
        assert saved.status_code == 200, saved.text
        before = saved.json()
        assert (await client.get(detail + "/readiness")).json()[
            "confirmation_blockers"
        ] == []
        approved = await client.post(detail + "/confirm")
        assert approved.status_code == 200, approved.text
        assert approved.json()["contract_assessment"] == before["contract_assessment"]
        assert (
            approved.json()["consent_assessment"] is None
            and approved.json()["lia_assessment"] is None
        )
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        third = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert third.status_code == 201
        assert (
            await client.post(url + "/" + third.json()["id"] + "/confirm")
        ).status_code == 200
        assert (await client.get(detail)).json()["status"] == "reemplazado"
        assert (
            await client.patch(detail, json={"contract_assessment": None})
        ).status_code == 409


async def test_api_obligacion_legal_persistencia_y_compatibilidad(
    client_a, rat_m3, org_a_id, org_b_id, negative_controls, _session_factory
):
    from sqlalchemy.exc import IntegrityError

    from app.services.eipd import (
        bind_eipd_screening_v3,
        build_eipd_context_binding_hash_v12,
    )
    from app.services.special_conditions import bind_special_conditions_v2

    treatment_id, payload = rat_m3
    legal = {
        "route": "cumplimiento_obligacion_legal",
        "normative_references": [
            {
                "norm_name": "Norma",
                "official_source_url": "https://www.bcn.cl/leychile/",
            }
        ],
        "evidence": [{"evidence_type": "referencia", "obtained_on": "2026-10-05"}],
    }
    payload.update(
        legal_basis="obligacion_legal_art13b", legal_obligation_assessment=legal
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        assert (
            original["legal_obligation_assessment"]["evidence"][0]["obtained_on"]
            == "2026-10-05"
        )
        assert original["special_conditions"]["context_binding"]["schema_version"] == 11
        assert original["eipd_screening"]["context_binding"]["schema_version"] == 12
        assert original["eipd_screening"]["context_binding"][
            "hash"
        ] == build_eipd_context_binding_hash_v12(
            original["rat_context_snapshot"],
            None,
            original["special_conditions"],
            None,
            original["legal_obligation_assessment"],
            original["rights_defense_assessment"],
            None,
            None,
            None,
            None,
            None,
            legal_basis=original["legal_basis"],
        )
        assert (await client.post(detail + "/confirm")).status_code == 400
        for invalid in (
            {"route": "otra"},
            {"schema_version": 2},
            {"approved": True},
            {"normative_references": [{"official_source_url": "file:///local"}]},
            {"normative_basis_reviewed": {"answer": "no_aplica"}},
        ):
            assert (
                await client.patch(
                    detail, json={"legal_obligation_assessment": invalid}
                )
            ).status_code == 422
        assert (await client.get(detail)).json() == original
        assert (
            await client.patch(
                detail,
                headers={"X-Organization-Id": str(org_b_id)},
                json={"legal_obligation_assessment": {}},
            )
        ).status_code == 403
        changed = await client.patch(
            detail, json={"legal_obligation_assessment": {"notes": "Cambio normativo"}}
        )
        assert changed.status_code == 200
        assert changed.json()["special_conditions"] == original["special_conditions"]
        assert changed.json()["eipd_screening"] == original["eipd_screening"]
        prep = (await client.get(detail + "/readiness")).json()
        assert (
            not prep["special"]["context_current"]
            and not prep["eipd"]["context_current"]
        )
        updated = await client.patch(
            detail,
            json={
                "legal_obligation_assessment": legal,
                "contract_assessment": {"notes": "Documento residual"},
                **negative_controls,
            },
        )
        assert updated.status_code == 200, updated.text
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["special"]["context_current"] and prep["eipd"]["context_current"]
        old_special = bind_special_conditions_v2(
            negative_controls["special_conditions"],
            original["rat_context_snapshot"],
            original["legal_basis"],
            None,
            None,
            updated.json()["contract_assessment"],
        ).model_dump(mode="json")
        old_eipd = bind_eipd_screening_v3(
            negative_controls["eipd_screening"],
            original["rat_context_snapshot"],
            None,
            old_special,
            updated.json()["contract_assessment"],
        ).model_dump(mode="json")
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == uuid.UUID(original["id"]))
                .values(special_conditions=old_special, eipd_screening=old_eipd)
            )
            await db.commit()
        prep = (await client.get(detail + "/readiness")).json()
        for control in ("special", "eipd"):
            assert "asociacion_obligacion_legal_no_cubierta" in {
                i["code"] for i in prep[control]["issues"]
            }
        assert (await client.get(detail)).json()["eipd_screening"] == old_eipd
        async with _session_factory() as db:
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        update(LegalAssessment)
                        .where(LegalAssessment.id == uuid.UUID(original["id"]))
                        .values(legal_obligation_assessment=[])
                    )
            await db.rollback()
        deleted = await client.patch(detail, json={"legal_obligation_assessment": None})
        assert deleted.status_code == 200
        final = (await client.get(detail)).json()
        assert final["legal_obligation_assessment"] is None
        assert (
            final["eipd_screening"] == old_eipd
            and final["special_conditions"] == old_special
        )
        assert (await client.get(detail + "/readiness")).json()["eipd"][
            "context_current"
        ]
        async with _session_factory() as db:
            assert (
                await db.execute(
                    select(LegalAssessment.id).where(
                        LegalAssessment.id == uuid.UUID(original["id"]),
                        LegalAssessment.legal_obligation_assessment.is_(None),
                    )
                )
            ).scalar_one()


async def test_api_preparacion_normativa_sin_confirmacion_y_contexto_actual(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    complete_legal_obligation,
    negative_controls,
    _session_factory,
):
    treatment_id, payload = rat_m3
    payload.update(
        legal_basis="obligacion_legal_art13b", legal_obligation_assessment={}
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["legal_obligation"]["result"] == "incompleto"
        assert "obligacion_legal_no_preparada" in {
            b["code"] for b in prep["confirmation_blockers"]
        }
        saved = await client.patch(
            detail,
            json={
                "legal_obligation_assessment": complete_legal_obligation,
                **negative_controls,
            },
        )
        assert saved.status_code == 200, saved.text
        before = saved.json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["legal_obligation"]["result"] == "completo"
        assert {b["code"] for b in ready["confirmation_blockers"]} == set()
        assert (
            ready["consent"] is None
            and ready["lia"] is None
            and ready["contract"] is None
        )
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        assert (await client.get(detail)).json() == before
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == treatment_id)
                .values(organization_role="encargado")
            )
            await db.commit()
        current = (await client.get(detail + "/readiness")).json()
        assert current["legal_obligation"]["result"] == "requiere_revision"
        assert "rol_no_admitido" in {
            i["code"] for i in current["legal_obligation"]["issues"]
        }
        assert (
            not current["special"]["context_current"]
            and not current["eipd"]["context_current"]
        )
        assert (await client.get(detail)).json() == before


@pytest.mark.parametrize(
    "route", ["cumplimiento_obligacion_legal", "tratamiento_dispuesto_por_ley"]
)
async def test_api_confirmacion_normativa_motivos_y_reemplazo(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    complete_legal_obligation,
    negative_controls,
    route,
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert first.status_code == 201
        first_url = url + "/" + first.json()["id"]
        assert (await client.post(first_url + "/confirm")).status_code == 200
        second = await client.post(
            url,
            json={
                **payload,
                "legal_basis": "obligacion_legal_art13b",
                "legal_obligation_assessment": {},
            },
        )
        assert second.status_code == 201
        detail = url + "/" + second.json()["id"]
        before = (await client.get(detail)).json()
        prep = (await client.get(detail + "/readiness")).json()
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 400
        assert rejected.json()["detail"]["code"] == "obligacion_legal_no_preparada"
        for field in ("result", "issues", "applicability"):
            assert rejected.json()["detail"][field] == prep["legal_obligation"][field]
        assert (await client.get(detail)).json() == before
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        legal = complete_legal_obligation
        legal["route"] = route
        if route == "tratamiento_dispuesto_por_ley":
            legal["processing_required_by_law"] = legal.pop(
                "obligation_applies_to_controller"
            )
        legal["normative_basis_in_force"]["answer"] = "no"
        assert (
            await client.patch(
                detail, json={"legal_obligation_assessment": legal, **negative_controls}
            )
        ).status_code == 200
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        legal["normative_basis_in_force"]["answer"] = "si"
        saved = await client.patch(
            detail, json={"legal_obligation_assessment": legal, **negative_controls}
        )
        assert saved.status_code == 200, saved.text
        assert (await client.get(detail + "/readiness")).json()[
            "confirmation_blockers"
        ] == []
        approved = await client.post(detail + "/confirm")
        assert approved.status_code == 200, approved.text
        assert (
            approved.json()["legal_obligation_assessment"]
            == saved.json()["legal_obligation_assessment"]
        )
        assert all(
            approved.json()[field] is None
            for field in ("consent_assessment", "lia_assessment", "contract_assessment")
        )
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        third = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert third.status_code == 201
        assert (
            await client.post(url + "/" + third.json()["id"] + "/confirm")
        ).status_code == 200
        assert (await client.get(detail)).json()["status"] == "reemplazado"
        assert (
            await client.patch(detail, json={"legal_obligation_assessment": None})
        ).status_code == 409


async def test_api_derechos_persistencia_compatibilidad_y_sql_null(
    client_a, rat_m3, org_a_id, org_b_id, negative_controls, _session_factory
):
    from sqlalchemy.exc import IntegrityError

    from app.services.eipd import bind_eipd_screening_v4
    from app.services.special_conditions import bind_special_conditions_v3

    treatment_id, payload = rat_m3
    rights = {
        "route": "formulacion_derecho",
        "forum_type": "organo_publico",
        "proceeding_stage": "preparacion",
        "evidence": [{"evidence_type": "registro", "obtained_on": "2026-10-06"}],
    }
    payload.update(
        legal_basis="defensa_derechos_art13e", rights_defense_assessment=rights
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        assert (
            original["rights_defense_assessment"]["evidence"][0]["obtained_on"]
            == "2026-10-06"
        )
        assert original["special_conditions"]["context_binding"]["schema_version"] == 11
        assert original["eipd_screening"]["context_binding"]["schema_version"] == 12
        assert (await client.post(detail + "/confirm")).status_code == 400
        for invalid in (
            {"route": "otra"},
            {"schema_version": 2},
            {"approved": True},
            {"forum_type": "privado"},
            {"proceeding_stage": "otra"},
            {"related_to_right": {"answer": "no_aplica"}},
            {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
        ):
            assert (
                await client.patch(detail, json={"rights_defense_assessment": invalid})
            ).status_code == 422
        assert (await client.get(detail)).json() == original
        assert (
            await client.patch(
                detail,
                headers={"X-Organization-Id": str(org_b_id)},
                json={"rights_defense_assessment": {}},
            )
        ).status_code == 403
        assert (
            await client.patch(detail, json={"justification": "Revisión"})
        ).status_code == 200
        assert (await client.get(detail)).json()[
            "rights_defense_assessment"
        ] == original["rights_defense_assessment"]
        changed = await client.patch(
            detail, json={"rights_defense_assessment": {"notes": "Cambio documental"}}
        )
        assert changed.status_code == 200
        assert (
            changed.json()["special_conditions"] == original["special_conditions"]
            and changed.json()["eipd_screening"] == original["eipd_screening"]
        )
        prep = (await client.get(detail + "/readiness")).json()
        assert (
            not prep["special"]["context_current"]
            and not prep["eipd"]["context_current"]
        )
        saved = await client.patch(
            detail, json={"rights_defense_assessment": rights, **negative_controls}
        )
        assert saved.status_code == 200
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["special"]["context_current"] and prep["eipd"]["context_current"]
        old_special = bind_special_conditions_v3(
            negative_controls["special_conditions"],
            original["rat_context_snapshot"],
            original["legal_basis"],
            None,
            None,
            None,
            None,
        ).model_dump(mode="json")
        old_eipd = bind_eipd_screening_v4(
            negative_controls["eipd_screening"],
            original["rat_context_snapshot"],
            None,
            old_special,
            None,
            None,
        ).model_dump(mode="json")
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == uuid.UUID(original["id"]))
                .values(special_conditions=old_special, eipd_screening=old_eipd)
            )
            await db.commit()
        prep = (await client.get(detail + "/readiness")).json()
        for control in ("special", "eipd"):
            assert "asociacion_derechos_no_cubierta" in {
                i["code"] for i in prep[control]["issues"]
            }
        assert (await client.get(detail)).json()["eipd_screening"] == old_eipd
        async with _session_factory() as db:
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        update(LegalAssessment)
                        .where(LegalAssessment.id == uuid.UUID(original["id"]))
                        .values(rights_defense_assessment=[])
                    )
            await db.rollback()
        deleted = await client.patch(detail, json={"rights_defense_assessment": None})
        assert deleted.status_code == 200
        final = (await client.get(detail)).json()
        assert final["rights_defense_assessment"] is None
        assert (
            final["special_conditions"] == old_special
            and final["eipd_screening"] == old_eipd
        )
        assert (await client.get(detail + "/readiness")).json()["eipd"][
            "context_current"
        ]
        async with _session_factory() as db:
            assert (
                await db.execute(
                    select(LegalAssessment.id).where(
                        LegalAssessment.id == uuid.UUID(original["id"]),
                        LegalAssessment.rights_defense_assessment.is_(None),
                    )
                )
            ).scalar_one()


async def test_api_preparacion_derechos_y_contexto_actual(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    complete_rights_defense,
    negative_controls,
    _session_factory,
):
    treatment_id, payload = rat_m3
    payload.update(legal_basis="defensa_derechos_art13e", rights_defense_assessment={})
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201
        detail = url + "/" + created.json()["id"]
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["rights_defense"]["result"] == "incompleto"
        assert "defensa_derechos_no_preparada" in {
            b["code"] for b in prep["confirmation_blockers"]
        }
        saved = await client.patch(
            detail,
            json={
                "rights_defense_assessment": complete_rights_defense,
                **negative_controls,
            },
        )
        assert saved.status_code == 200, saved.text
        before = saved.json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["rights_defense"]["result"] == "completo"
        assert ready["confirmation_blockers"] == []
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        assert (await client.get(detail)).json() == before
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == treatment_id)
                .values(organization_role="encargado")
            )
            await db.commit()
        current = (await client.get(detail + "/readiness")).json()
        assert current["rights_defense"]["result"] == "requiere_revision"
        assert "rol_no_admitido" in {
            i["code"] for i in current["rights_defense"]["issues"]
        }
        assert (
            not current["special"]["context_current"]
            and not current["eipd"]["context_current"]
        )
        assert (await client.get(detail)).json() == before


@pytest.mark.parametrize(
    "route", ["formulacion_derecho", "ejercicio_derecho", "defensa_derecho"]
)
@pytest.mark.parametrize("forum", ["tribunal_justicia", "organo_publico"])
async def test_api_confirmacion_derechos_motivos_y_reemplazo(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    complete_rights_defense,
    negative_controls,
    route,
    forum,
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert first.status_code == 201
        first_url = url + "/" + first.json()["id"]
        assert (await client.post(first_url + "/confirm")).status_code == 200
        second = await client.post(
            url,
            json={
                **payload,
                "legal_basis": "defensa_derechos_art13e",
                "rights_defense_assessment": {},
            },
        )
        assert second.status_code == 201
        detail = url + "/" + second.json()["id"]
        before = (await client.get(detail)).json()
        prep = (await client.get(detail + "/readiness")).json()
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 400
        assert rejected.json()["detail"]["code"] == "defensa_derechos_no_preparada"
        for field in ("result", "issues", "applicability"):
            assert rejected.json()["detail"][field] == prep["rights_defense"][field]
        assert (await client.get(detail)).json() == before
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        legal = complete_rights_defense
        legal["route"] = route
        legal["forum_type"] = forum
        legal["necessary_for_route"]["answer"] = "no"
        assert (
            await client.patch(
                detail, json={"rights_defense_assessment": legal, **negative_controls}
            )
        ).status_code == 200
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        legal["necessary_for_route"]["answer"] = "si"
        saved = await client.patch(
            detail, json={"rights_defense_assessment": legal, **negative_controls}
        )
        assert saved.status_code == 200, saved.text
        assert (await client.get(detail + "/readiness")).json()[
            "confirmation_blockers"
        ] == []
        approved = await client.post(detail + "/confirm")
        assert approved.status_code == 200, approved.text
        assert (
            approved.json()["rights_defense_assessment"]
            == saved.json()["rights_defense_assessment"]
        )
        assert all(
            approved.json()[field] is None
            for field in ("consent_assessment", "lia_assessment", "contract_assessment")
        )
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        third = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert third.status_code == 201
        assert (
            await client.post(url + "/" + third.json()["id"] + "/confirm")
        ).status_code == 200
        assert (await client.get(detail)).json()["status"] == "reemplazado"
        assert (
            await client.patch(detail, json={"rights_defense_assessment": None})
        ).status_code == 409


@pytest.mark.parametrize(
    "special_version,eipd_version", [(1, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
)
async def test_api_economico_persistencia_compatibilidad_y_sql_null(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    negative_controls,
    _session_factory,
    special_version,
    eipd_version,
):
    from sqlalchemy.exc import IntegrityError

    from app.services import eipd as eipd_service
    from app.services import special_conditions as special_service

    treatment_id, payload = rat_m3
    rights = {
        "route": "con_comunicacion",
        "obligation_type": "comercial",
        "evidence": [{"evidence_type": "registro", "obtained_on": "2026-10-06"}],
    }
    payload.update(
        legal_basis="obligaciones_economicas_art13a",
        economic_obligations_assessment=rights,
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        assert (
            original["economic_obligations_assessment"]["evidence"][0]["obtained_on"]
            == "2026-10-06"
        )
        assert original["special_conditions"]["context_binding"]["schema_version"] == 11
        assert original["eipd_screening"]["context_binding"]["schema_version"] == 12
        assert (await client.post(detail + "/confirm")).status_code == 400
        for invalid in (
            {"route": "otra"},
            {"schema_version": 2},
            {"approved": True},
            {"obligation_type": "otra"},
            {"operations_include_communication": {"answer": "otra"}},
            {"related_to_obligation": {"answer": "no_aplica"}},
            {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
        ):
            assert (
                await client.patch(
                    detail, json={"economic_obligations_assessment": invalid}
                )
            ).status_code == 422
        assert (await client.get(detail)).json() == original
        assert (
            await client.patch(
                detail,
                headers={"X-Organization-Id": str(org_b_id)},
                json={"economic_obligations_assessment": {}},
            )
        ).status_code == 403
        assert (
            await client.patch(detail, json={"justification": "Revisión"})
        ).status_code == 200
        assert (await client.get(detail)).json()[
            "economic_obligations_assessment"
        ] == original["economic_obligations_assessment"]
        changed = await client.patch(
            detail,
            json={"economic_obligations_assessment": {"notes": "Cambio documental"}},
        )
        assert changed.status_code == 200
        assert (
            changed.json()["special_conditions"] == original["special_conditions"]
            and changed.json()["eipd_screening"] == original["eipd_screening"]
        )
        prep = (await client.get(detail + "/readiness")).json()
        assert (
            not prep["special"]["context_current"]
            and not prep["eipd"]["context_current"]
        )
        saved = await client.patch(
            detail,
            json={"economic_obligations_assessment": rights, **negative_controls},
        )
        assert saved.status_code == 200
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["special"]["context_current"] and prep["eipd"]["context_current"]
        special_args = [
            negative_controls["special_conditions"],
            original["rat_context_snapshot"],
            original["legal_basis"],
            None,
            None,
        ]
        special_args += [None] * (special_version - 1)
        old_special = getattr(
            special_service, f"bind_special_conditions_v{special_version}"
        )(*special_args).model_dump(mode="json")
        eipd_args = [
            negative_controls["eipd_screening"],
            original["rat_context_snapshot"],
            None,
        ]
        if eipd_version >= 2:
            eipd_args.append(old_special)
        eipd_args += [None] * max(0, eipd_version - 2)
        old_eipd = getattr(eipd_service, f"bind_eipd_screening_v{eipd_version}")(
            *eipd_args
        ).model_dump(mode="json")
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == uuid.UUID(original["id"]))
                .values(special_conditions=old_special, eipd_screening=old_eipd)
            )
            await db.commit()
        prep = (await client.get(detail + "/readiness")).json()
        for control in ("special", "eipd"):
            assert "asociacion_economica_no_cubierta" in {
                i["code"] for i in prep[control]["issues"]
            }
        assert (await client.get(detail)).json()["eipd_screening"] == old_eipd
        async with _session_factory() as db:
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        update(LegalAssessment)
                        .where(LegalAssessment.id == uuid.UUID(original["id"]))
                        .values(economic_obligations_assessment=[])
                    )
            await db.rollback()
        deleted = await client.patch(
            detail, json={"economic_obligations_assessment": None}
        )
        assert deleted.status_code == 200
        final = (await client.get(detail)).json()
        assert final["economic_obligations_assessment"] is None
        assert (
            final["special_conditions"] == old_special
            and final["eipd_screening"] == old_eipd
        )
        after = (await client.get(detail + "/readiness")).json()
        assert after["special"]["context_current"]
        assert after["eipd"]["context_current"] == (eipd_version != 1)
        assert all(
            "asociacion_economica_no_cubierta"
            not in {i["code"] for i in after[c]["issues"]}
            for c in ("special", "eipd")
        )
        async with _session_factory() as db:
            assert (
                await db.execute(
                    select(LegalAssessment.id).where(
                        LegalAssessment.id == uuid.UUID(original["id"]),
                        LegalAssessment.economic_obligations_assessment.is_(None),
                    )
                )
            ).scalar_one()


async def test_api_preparacion_economica_y_contexto_actual(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    complete_economic_obligations,
    negative_controls,
    _session_factory,
):
    treatment_id, payload = rat_m3
    payload.update(
        legal_basis="obligaciones_economicas_art13a", economic_obligations_assessment={}
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201
        detail = url + "/" + created.json()["id"]
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["economic_obligations"]["result"] == "incompleto"
        assert "obligaciones_economicas_no_preparadas" in {
            b["code"] for b in prep["confirmation_blockers"]
        }
        saved = await client.patch(
            detail,
            json={
                "economic_obligations_assessment": complete_economic_obligations,
                **negative_controls,
            },
        )
        assert saved.status_code == 200, saved.text
        before = saved.json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["economic_obligations"]["result"] == "completo"
        assert ready["confirmation_blockers"] == []
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        assert (await client.get(detail)).json() == before
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == treatment_id)
                .values(organization_role="encargado")
            )
            await db.commit()
        current = (await client.get(detail + "/readiness")).json()
        assert current["economic_obligations"]["result"] == "requiere_revision"
        assert "rol_no_admitido" in {
            i["code"] for i in current["economic_obligations"]["issues"]
        }
        assert (
            not current["special"]["context_current"]
            and not current["eipd"]["context_current"]
        )
        assert (await client.get(detail)).json() == before


@pytest.mark.parametrize("route", ["sin_comunicacion", "con_comunicacion"])
@pytest.mark.parametrize("kind", ["economica", "financiera", "bancaria", "comercial"])
async def test_api_confirmacion_economica_motivos_y_reemplazo(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    complete_economic_obligations,
    negative_controls,
    route,
    kind,
):
    treatment_id, payload = rat_m3
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert first.status_code == 201
        first_url = url + "/" + first.json()["id"]
        assert (await client.post(first_url + "/confirm")).status_code == 200
        second = await client.post(
            url,
            json={
                **payload,
                "legal_basis": "obligaciones_economicas_art13a",
                "economic_obligations_assessment": {},
            },
        )
        assert second.status_code == 201
        detail = url + "/" + second.json()["id"]
        before = (await client.get(detail)).json()
        prep = (await client.get(detail + "/readiness")).json()
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 400
        assert (
            rejected.json()["detail"]["code"] == "obligaciones_economicas_no_preparadas"
        )
        for field in ("result", "issues", "applicability"):
            assert (
                rejected.json()["detail"][field] == prep["economic_obligations"][field]
            )
        assert (await client.get(detail)).json() == before
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        legal = complete_economic_obligations
        legal["route"] = route
        legal["obligation_type"] = kind
        if route == "sin_comunicacion":
            legal["operations_include_communication"]["answer"] = "no"
            for field in (
                "communication_scope",
                "communication_eligibility_analysis",
                "communication_restrictions_analysis",
                "payment_and_extinction_controls",
                "communication_permitted",
                "excluded_data_screened",
                "communication_limits_respected",
            ):
                legal.pop(field)
        legal["title_iii_reviewed"]["answer"] = "no"
        assert (
            await client.patch(
                detail,
                json={"economic_obligations_assessment": legal, **negative_controls},
            )
        ).status_code == 200
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        legal["title_iii_reviewed"]["answer"] = "si"
        saved = await client.patch(
            detail, json={"economic_obligations_assessment": legal, **negative_controls}
        )
        assert saved.status_code == 200, saved.text
        assert (await client.get(detail + "/readiness")).json()[
            "confirmation_blockers"
        ] == []
        approved = await client.post(detail + "/confirm")
        assert approved.status_code == 200, approved.text
        assert (
            approved.json()["economic_obligations_assessment"]
            == saved.json()["economic_obligations_assessment"]
        )
        assert all(
            approved.json()[field] is None
            for field in ("consent_assessment", "lia_assessment", "contract_assessment")
        )
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        third = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert third.status_code == 201
        assert (
            await client.post(url + "/" + third.json()["id"] + "/confirm")
        ).status_code == 200
        assert (await client.get(detail)).json()["status"] == "reemplazado"
        assert (
            await client.patch(detail, json={"economic_obligations_assessment": None})
        ).status_code == 409


@pytest.mark.parametrize(
    "special_version,eipd_version", [(1, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
)
async def test_api_geolocalizacion_persistencia_compatibilidad_y_sql_null(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    negative_controls,
    _session_factory,
    complete_payload,
    special_version,
    eipd_version,
):
    from sqlalchemy.exc import IntegrityError

    from app.services import eipd as eipd_service
    from app.services import special_conditions as special_service

    treatment_id, payload = rat_m3
    rights = {
        "notice_reference": "Aviso de prueba",
        "notice_provided_on": "2026-10-06",
        "scope": {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]},
        "evidence": [{"evidence_type": "registro", "obtained_on": "2026-10-06"}],
    }
    payload.update(geolocation_assessment=rights, consent_assessment=complete_payload)
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        assert (
            original["geolocation_assessment"]["evidence"][0]["obtained_on"]
            == "2026-10-06"
        )
        assert original["special_conditions"]["context_binding"]["schema_version"] == 11
        assert original["eipd_screening"]["context_binding"]["schema_version"] == 12
        assert (await client.post(detail + "/confirm")).status_code == 409
        for invalid in (
            {"schema_version": 2},
            {"approved": True},
            {"notice_provided_on": "invalid"},
            {"information_clear": {"answer": "no_aplica"}},
            {"scope": {"unknown": True}},
            {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
        ):
            assert (
                await client.patch(detail, json={"geolocation_assessment": invalid})
            ).status_code == 422
        assert (await client.get(detail)).json() == original
        assert (
            await client.patch(
                detail,
                headers={"X-Organization-Id": str(org_b_id)},
                json={"geolocation_assessment": {}},
            )
        ).status_code == 403
        assert (
            await client.patch(detail, json={"justification": "Revisión"})
        ).status_code == 200
        assert (await client.get(detail)).json()["geolocation_assessment"] == original[
            "geolocation_assessment"
        ]
        changed = await client.patch(
            detail,
            json={"geolocation_assessment": {"notes": "Cambio documental"}},
        )
        assert changed.status_code == 200
        assert (
            changed.json()["special_conditions"] == original["special_conditions"]
            and changed.json()["eipd_screening"] == original["eipd_screening"]
        )
        prep = (await client.get(detail + "/readiness")).json()
        assert (
            not prep["special"]["context_current"]
            and not prep["eipd"]["context_current"]
        )
        saved = await client.patch(
            detail,
            json={"geolocation_assessment": rights, **negative_controls},
        )
        assert saved.status_code == 200
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["special"]["context_current"] and prep["eipd"]["context_current"]
        assert "expediente_geolocalizacion_residual" in {
            i["code"] for i in prep["special"]["issues"]
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        special_args = [
            negative_controls["special_conditions"],
            original["rat_context_snapshot"],
            original["legal_basis"],
            original["consent_assessment"],
            None,
        ]
        special_args += [None] * (special_version - 1)
        old_special = getattr(
            special_service, f"bind_special_conditions_v{special_version}"
        )(*special_args).model_dump(mode="json")
        eipd_args = [
            negative_controls["eipd_screening"],
            original["rat_context_snapshot"],
            None,
        ]
        if eipd_version >= 2:
            eipd_args.append(old_special)
        eipd_args += [None] * max(0, eipd_version - 2)
        old_eipd = getattr(eipd_service, f"bind_eipd_screening_v{eipd_version}")(
            *eipd_args
        ).model_dump(mode="json")
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == uuid.UUID(original["id"]))
                .values(special_conditions=old_special, eipd_screening=old_eipd)
            )
            await db.commit()
        prep = (await client.get(detail + "/readiness")).json()
        for control in ("special", "eipd"):
            assert "asociacion_geolocalizacion_no_cubierta" in {
                i["code"] for i in prep[control]["issues"]
            }
        assert (await client.get(detail)).json()["eipd_screening"] == old_eipd
        async with _session_factory() as db:
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        update(LegalAssessment)
                        .where(LegalAssessment.id == uuid.UUID(original["id"]))
                        .values(geolocation_assessment=[])
                    )
            await db.rollback()
        deleted = await client.patch(detail, json={"geolocation_assessment": None})
        assert deleted.status_code == 200
        final = (await client.get(detail)).json()
        assert final["geolocation_assessment"] is None
        assert (
            final["special_conditions"] == old_special
            and final["eipd_screening"] == old_eipd
        )
        after = (await client.get(detail + "/readiness")).json()
        assert after["special"]["context_current"]
        assert after["eipd"]["context_current"] == (eipd_version != 1)
        assert all(
            "asociacion_geolocalizacion_no_cubierta"
            not in {i["code"] for i in after[c]["issues"]}
            for c in ("special", "eipd")
        )
        async with _session_factory() as db:
            assert (
                await db.execute(
                    select(LegalAssessment.id).where(
                        LegalAssessment.id == uuid.UUID(original["id"]),
                        LegalAssessment.geolocation_assessment.is_(None),
                    )
                )
            ).scalar_one()


async def test_api_geolocalizacion_declarada_sigue_bloqueada(
    client_a, rat_m3, org_a_id, complete_payload
):
    treatment_id, payload = rat_m3
    declarations = payload["special_conditions"]["declarations"]
    for declaration in declarations:
        if declaration["question_id"] == "geolocalizacion":
            declaration.update(
                answer="si",
                rationale="Geolocalización documentada",
                data_category_codes=["id"],
                data_subject_codes=["clientes"],
            )
    payload["special_conditions"]["conditions"] = [
        {
            "regime_id": "geolocalizacion_art16sexies",
            "authorization_route": "regla_especifica",
            "data_category_codes": ["id"],
            "data_subject_codes": ["clientes"],
            "legal_reference": "art16sexies",
            "documentary_analysis": "Aviso documentado",
            "evidence": [{"evidence_type": "aviso", "reference": "Aviso de prueba"}],
        }
    ]
    payload.update(
        consent_assessment=complete_payload,
        geolocation_assessment={
            "notice_reference": "Aviso de prueba",
            "scope": {
                "data_category_codes": ["id"],
                "data_subject_codes": ["clientes"],
            },
        },
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        ready = (await client.get(detail + "/readiness")).json()
        assert "geolocalizacion_art16sexies" in ready["special"]["detected_regimes"]
        assert ready["geolocation"]["result"] == "incompleto"
        assert "validador_no_implementado" not in {
            i["code"] for i in ready["special"]["issues"]
        }
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == before


@pytest.mark.parametrize("transfer", ["si", "no"])
async def test_api_preparacion_geolocalizacion_y_contexto_actual(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    complete_payload,
    complete_geolocation,
    geolocation_controls,
    _session_factory,
    transfer,
):
    treatment_id, payload = rat_m3
    payload.update(
        consent_assessment=complete_payload,
        geolocation_assessment={},
        **geolocation_controls,
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["geolocation"]["result"] == "incompleto"
        assert "geolocalizacion_no_preparada" in {
            b["code"] for b in prep["confirmation_blockers"]
        }
        geo = complete_geolocation
        geo["value_added_third_party_transfer"]["answer"] = transfer
        if transfer == "no":
            geo.pop("value_added_service_description")
            geo.pop("third_party_recipient_description")
        saved = await client.patch(
            detail, json={"geolocation_assessment": geo, **geolocation_controls}
        )
        assert saved.status_code == 200, saved.text
        before = saved.json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["geolocation"]["result"] == "completo"
        assert "geolocalizacion_no_preparada" not in {
            b["code"] for b in ready["confirmation_blockers"]
        }
        assert ready["confirmation_blockers"] == []
        assert ready["special"]["result"] == "regimenes_preparados"
        assert ready["eipd"]["result"] == "sin_supuestos_declarados"
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        assert (await client.get(detail)).json() == before
        async with _session_factory() as db:
            await db.execute(
                update(Treatment)
                .where(Treatment.id == treatment_id)
                .values(organization_role="encargado")
            )
            await db.commit()
        current = (await client.get(detail + "/readiness")).json()
        assert current["geolocation"]["result"] == "requiere_revision"
        assert "rol_no_admitido" in {
            i["code"] for i in current["geolocation"]["issues"]
        }
        assert (
            not current["special"]["context_current"]
            and not current["eipd"]["context_current"]
        )
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
async def test_api_geolocalizacion_confirmacion_seis_bases(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    complete_lia_context,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
    complete_geolocation,
    geolocation_controls,
    _session_factory,
    basis,
):
    from copy import deepcopy

    from app.db.models import TreatmentDataSource

    treatment_id, payload = rat_m3
    if basis == "interes_legitimo_art13d":
        async with _session_factory() as db:
            db.add(
                TreatmentDataSource(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
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
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        assert (await client.post(first_url + "/confirm")).status_code == 200
        field, document = docs[basis]
        created = await client.post(
            url,
            json={
                **payload,
                **geolocation_controls,
                "legal_basis": basis,
                field: document,
                "geolocation_assessment": complete_geolocation,
            },
        )
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = created.json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["confirmation_blockers"] == [], ready
        assert ready["special"]["result"] == "regimenes_preparados"
        assert "validacion_otros_regimenes_especiales" in ready["pending_controls"]
        geo = deepcopy(complete_geolocation)
        geo["information_clear"]["answer"] = "no"
        assert (
            await client.patch(
                detail, json={"geolocation_assessment": geo, **geolocation_controls}
            )
        ).status_code == 200
        prep = (await client.get(detail + "/readiness")).json()
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409, rejected.text
        for control in ("special", "eipd"):
            assert rejected.json()["detail"][control] == prep[control]
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        positive = deepcopy(geolocation_controls)
        positive["eipd_screening"]["answers"][1]["answer"] = "si"
        assert (
            await client.patch(
                detail,
                json={"geolocation_assessment": complete_geolocation, **positive},
            )
        ).status_code == 200
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(first_url)).json()["status"] == "confirmado"
        saved = await client.patch(
            detail,
            json={
                "geolocation_assessment": complete_geolocation,
                **geolocation_controls,
            },
        )
        assert saved.status_code == 200, saved.text
        approved = await client.post(detail + "/confirm")
        assert approved.status_code == 200, approved.text
        assert (
            approved.json()["geolocation_assessment"]
            == before["geolocation_assessment"]
        )
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        assert (
            await client.patch(detail, json={"geolocation_assessment": None})
        ).status_code == 409
        third = await client.post(
            url, json={**payload, "consent_assessment": complete_payload}
        )
        assert third.status_code == 201
        assert (
            await client.post(url + "/" + third.json()["id"] + "/confirm")
        ).status_code == 200
        assert (await client.get(detail)).json()["status"] == "reemplazado"


@pytest.mark.parametrize(
    "special_version,eipd_version",
    [(1, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)],
)
async def test_api_consentimiento_sensible_persistencia_compatibilidad_y_sql_null(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    negative_controls,
    _session_factory,
    complete_payload,
    special_version,
    eipd_version,
):
    from sqlalchemy.exc import IntegrityError

    from app.services import eipd as eipd_service
    from app.services import special_conditions as special_service

    treatment_id, payload = rat_m3
    rights = {
        "declaration_reference": "Aviso de prueba",
        "declaration_obtained_on": "2026-10-06",
        "scope": {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]},
        "evidence": [{"evidence_type": "registro", "obtained_on": "2026-10-06"}],
    }
    payload.update(
        sensitive_consent_assessment=rights, consent_assessment=complete_payload
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        assert (
            original["sensitive_consent_assessment"]["evidence"][0]["obtained_on"]
            == "2026-10-06"
        )
        assert original["special_conditions"]["context_binding"]["schema_version"] == 11
        assert original["eipd_screening"]["context_binding"]["schema_version"] == 12
        assert (await client.post(detail + "/confirm")).status_code == 409
        for invalid in (
            {"schema_version": 2},
            {"approved": True},
            {"declaration_obtained_on": "invalid"},
            {"express_declaration_documented": {"answer": "no_aplica"}},
            {"scope": {"unknown": True}},
            {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
        ):
            assert (
                await client.patch(
                    detail, json={"sensitive_consent_assessment": invalid}
                )
            ).status_code == 422
        assert (await client.get(detail)).json() == original
        assert (
            await client.patch(
                detail,
                headers={"X-Organization-Id": str(org_b_id)},
                json={"sensitive_consent_assessment": {}},
            )
        ).status_code == 403
        assert (
            await client.patch(detail, json={"justification": "Revisión"})
        ).status_code == 200
        assert (await client.get(detail)).json()[
            "sensitive_consent_assessment"
        ] == original["sensitive_consent_assessment"]
        changed = await client.patch(
            detail,
            json={"sensitive_consent_assessment": {"notes": "Cambio documental"}},
        )
        assert changed.status_code == 200
        assert (
            changed.json()["special_conditions"] == original["special_conditions"]
            and changed.json()["eipd_screening"] == original["eipd_screening"]
        )
        prep = (await client.get(detail + "/readiness")).json()
        assert (
            not prep["special"]["context_current"]
            and not prep["eipd"]["context_current"]
        )
        saved = await client.patch(
            detail,
            json={"sensitive_consent_assessment": rights, **negative_controls},
        )
        assert saved.status_code == 200
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["special"]["context_current"] and prep["eipd"]["context_current"]
        assert "expediente_consentimiento_sensible_residual" in {
            i["code"] for i in prep["special"]["issues"]
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        special_args = [
            negative_controls["special_conditions"],
            original["rat_context_snapshot"],
            original["legal_basis"],
            original["consent_assessment"],
            None,
        ]
        special_args += [None] * (special_version - 1)
        old_special = getattr(
            special_service, f"bind_special_conditions_v{special_version}"
        )(*special_args).model_dump(mode="json")
        eipd_args = [
            negative_controls["eipd_screening"],
            original["rat_context_snapshot"],
            None,
        ]
        if eipd_version >= 2:
            eipd_args.append(old_special)
        eipd_args += [None] * max(0, eipd_version - 2)
        old_eipd = getattr(eipd_service, f"bind_eipd_screening_v{eipd_version}")(
            *eipd_args
        ).model_dump(mode="json")
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == uuid.UUID(original["id"]))
                .values(special_conditions=old_special, eipd_screening=old_eipd)
            )
            await db.commit()
        prep = (await client.get(detail + "/readiness")).json()
        for control in ("special", "eipd"):
            assert "asociacion_consentimiento_sensible_no_cubierta" in {
                i["code"] for i in prep[control]["issues"]
            }
        assert (await client.get(detail)).json()["eipd_screening"] == old_eipd
        async with _session_factory() as db:
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        update(LegalAssessment)
                        .where(LegalAssessment.id == uuid.UUID(original["id"]))
                        .values(sensitive_consent_assessment=[])
                    )
            await db.rollback()
        deleted = await client.patch(
            detail, json={"sensitive_consent_assessment": None}
        )
        assert deleted.status_code == 200
        final = (await client.get(detail)).json()
        assert final["sensitive_consent_assessment"] is None
        assert (
            final["special_conditions"] == old_special
            and final["eipd_screening"] == old_eipd
        )
        after = (await client.get(detail + "/readiness")).json()
        assert after["special"]["context_current"]
        assert after["eipd"]["context_current"] == (eipd_version != 1)
        assert all(
            "asociacion_consentimiento_sensible_no_cubierta"
            not in {i["code"] for i in after[c]["issues"]}
            for c in ("special", "eipd")
        )
        async with _session_factory() as db:
            assert (
                await db.execute(
                    select(LegalAssessment.id).where(
                        LegalAssessment.id == uuid.UUID(original["id"]),
                        LegalAssessment.sensitive_consent_assessment.is_(None),
                    )
                )
            ).scalar_one()


async def test_api_consentimiento_sensible_declarado_sigue_bloqueada(
    client_a, rat_m3, org_a_id, complete_payload
):
    treatment_id, payload = rat_m3
    declarations = payload["special_conditions"]["declarations"]
    for declaration in declarations:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(
                answer="si",
                rationale="Geolocalización documentada",
                data_category_codes=["id"],
                data_subject_codes=["clientes"],
            )
    payload["special_conditions"]["conditions"] = [
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "data_category_codes": ["id"],
            "data_subject_codes": ["clientes"],
            "legal_reference": "art16sexies",
            "documentary_analysis": "Aviso documentado",
            "evidence": [{"evidence_type": "aviso", "reference": "Aviso de prueba"}],
        }
    ]
    payload.update(
        consent_assessment=complete_payload,
        sensitive_consent_assessment={
            "declaration_reference": "Aviso de prueba",
            "scope": {
                "data_category_codes": ["id"],
                "data_subject_codes": ["clientes"],
            },
        },
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        ready = (await client.get(detail + "/readiness")).json()
        assert "sensibles_art16" in ready["special"]["detected_regimes"]
        assert "validador_no_implementado" not in {
            i["code"] for i in ready["special"]["issues"]
        }
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == before


@pytest.mark.parametrize(
    "method,grant",
    [
        ("escrito", "escrito"),
        ("verbal", "verbal"),
        ("tecnologico_equivalente", "electronico"),
    ],
)
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
async def test_api_sensitive_confirmation_six_bases(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    _session_factory,
    method,
    grant,
    basis,
    complete_lia_context,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
):
    treatment_id, payload = rat_m3
    from copy import deepcopy

    ordinary_controls = deepcopy(
        {k: payload[k] for k in ("special_conditions", "eipd_screening")}
    )
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    if basis == "interes_legitimo_art13d":
        from app.db.models import TreatmentDataSource

        async with _session_factory() as db:
            db.add(
                TreatmentDataSource(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    source_type="titular",
                    is_public_source=False,
                )
            )
            await db.commit()
    complete_lia_context[0]["nature_and_scope"][
        "special_rules_description"
    ] = "Consentimiento expreso sensible documentado"
    docs = {
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
    payload["legal_basis"] = basis
    if basis in docs:
        field, ordinary_document = docs[basis]
        payload[field] = ordinary_document
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in payload["special_conditions"]["declarations"]:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(answer="si", rationale="Declaración expresa", **scope)
    payload["special_conditions"]["conditions"] = [
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "legal_reference": "art16",
            "documentary_analysis": "Declaración expresa",
            "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
            **scope,
        }
    ]
    document = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Categoría sensible",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "expression_method": method,
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Consentimiento expreso documentado",
        "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
    }
    for field in [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ]:
        document[field] = {"answer": "si", "rationale": "Comprobación documentada"}
    if method == "tecnologico_equivalente":
        document["technology_equivalence_analysis"] = "Equivalencia documentada"
    complete_payload["grant_method"] = grant
    payload.update(
        sensitive_consent_assessment=document, consent_assessment=complete_payload
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        response = await client.get(detail + "/readiness")
        assert response.status_code == 200, response.text
        ready = response.json()
        assert ready["sensitive_consent"]["result"] == "completo"
        assert ready["sensitive_consent"]["issues"] == []
        assert "consentimiento_sensible_no_preparado" not in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert "validador_no_implementado" not in {
            i["code"] for i in ready["special"]["issues"]
        }
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        assert ready["confirmation_blockers"] == [], ready
        assert (await client.get(detail)).json() == before
        document["proof_available"]["answer"] = "pendiente"
        changed = await client.patch(
            detail, json={"sensitive_consent_assessment": document}
        )
        assert changed.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["sensitive_consent"]["result"] == "incompleto"
        assert "consentimiento_sensible_no_preparado" in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert (
            not ready["special"]["context_current"]
            and not ready["eipd"]["context_current"]
        )
        deleted = await client.patch(
            detail, json={"sensitive_consent_assessment": None}
        )
        assert deleted.status_code == 200
        assert (await client.get(detail + "/readiness")).json()["sensitive_consent"][
            "result"
        ] == "incompleto"

        restored = await client.patch(
            detail,
            json={
                "sensitive_consent_assessment": before["sensitive_consent_assessment"],
                "special_conditions": payload["special_conditions"],
                "eipd_screening": payload["eipd_screening"],
            },
        )
        assert restored.status_code == 200, restored.text
        positive = __import__("copy").deepcopy(payload["eipd_screening"])
        positive["answers"][1]["answer"] = "si"
        assert (
            await client.patch(detail, json={"eipd_screening": positive})
        ).status_code == 200
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json()["status"] == "borrador"
        assert (
            await client.patch(
                detail, json={"eipd_screening": payload["eipd_screening"]}
            )
        ).status_code == 200
        approved = await client.post(detail + "/confirm")
        assert approved.status_code == 200, approved.text
        assert approved.json()["status"] == "confirmado"
        assert (
            await client.patch(detail, json={"sensitive_consent_assessment": None})
        ).status_code == 409
        next_payload = {
            **payload,
            "sensitive_consent_assessment": before["sensitive_consent_assessment"],
        }
        second = await client.post(url, json=next_payload)
        assert second.status_code == 201, second.text
        second_url = url + "/" + second.json()["id"]
        assert (await client.post(second_url + "/confirm")).status_code == 200
        assert (await client.get(detail)).json()["status"] == "reemplazado"

        incomplete = {
            **next_payload,
            "sensitive_consent_assessment": {"notes": "Pendiente"},
        }
        third = await client.post(url, json=incomplete)
        assert third.status_code == 201
        third_url = url + "/" + third.json()["id"]
        rejected = await client.post(third_url + "/confirm")
        assert rejected.status_code in (400, 409)
        assert (await client.get(second_url)).json()["status"] == "confirmado"
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentDataCategory)
                .where(TreatmentDataCategory.treatment_id == treatment_id)
                .values(is_sensitive=False)
            )
            await db.commit()
        ordinary = {
            "purpose_id": payload["purpose_id"],
            "scope": scope,
            "legal_basis": "consentimiento_art12",
            "justification": "Alcance ordinario",
            "consent_assessment": complete_payload,
            **ordinary_controls,
        }
        fourth = await client.patch(
            third_url,
            json={
                **{k: v for k, v in ordinary.items() if k != "purpose_id"},
                "sensitive_consent_assessment": None,
            },
        )
        assert fourth.status_code == 200, fourth.text
        fourth_url = url + "/" + fourth.json()["id"]
        ready = (await client.get(fourth_url + "/readiness")).json()
        assert ready["sensitive_consent"] is None
        assert (await client.post(fourth_url + "/confirm")).status_code == 200
        assert (await client.get(second_url)).json()["status"] == "reemplazado"


@pytest.mark.parametrize(
    "document_field,response_field",
    [
        ("sensitive_consent_assessment", "proof_available"),
        ("geolocation_assessment", "information_clear"),
    ],
)
@pytest.mark.parametrize("answer", ["no", "pendiente"])
async def test_api_sensitive_geolocation_joint_confirmation(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    complete_geolocation,
    geolocation_controls,
    _session_factory,
    document_field,
    response_field,
    answer,
):
    from copy import deepcopy

    treatment_id, payload = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    controls = deepcopy(geolocation_controls)
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(answer="si", rationale="Declaración expresa", **scope)
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "legal_reference": "art16",
            "documentary_analysis": "Declaración expresa",
            "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
            **scope,
        }
    )
    sensitive = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Categoría sensible",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Consentimiento expreso documentado",
        "technology_equivalence_analysis": "Equivalencia documentada",
        "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
    }
    for field in [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ]:
        sensitive[field] = {"answer": "si", "rationale": "Comprobación documentada"}
    payload = {
        **payload,
        **controls,
        "consent_assessment": complete_payload,
        "sensitive_consent_assessment": sensitive,
        "geolocation_assessment": complete_geolocation,
    }
    expected_regimes = ["geolocalizacion_art16sexies", "sensibles_art16"]
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(url, json=payload)
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        readiness = (await client.get(first_url + "/readiness")).json()
        assert readiness["special"]["detected_regimes"] == expected_regimes
        assert readiness["special"]["result"] == "regimenes_preparados"
        assert (
            readiness["sensitive_consent"]["result"]
            == readiness["geolocation"]["result"]
            == "completo"
        )
        assert readiness["confirmation_blockers"] == []
        approved = await client.post(first_url + "/confirm")
        assert approved.status_code == 200, approved.text
        confirmed = (await client.get(first_url)).json()
        assert confirmed["status"] == "confirmado"
        second = await client.post(url, json=payload)
        assert second.status_code == 201, second.text
        second_url = url + "/" + second.json()["id"]
        original = second.json()
        changed = deepcopy(payload[document_field])
        changed[response_field]["answer"] = answer
        patched = await client.patch(second_url, json={document_field: changed})
        assert patched.status_code == 200, patched.text
        readiness = (await client.get(second_url + "/readiness")).json()
        assert (
            not readiness["special"]["context_current"]
            and not readiness["eipd"]["context_current"]
        )
        assert patched.json()["special_conditions"] == original["special_conditions"]
        assert patched.json()["eipd_screening"] == original["eipd_screening"]
        # Rebinding removes staleness but must not approve a negative/pending document.
        patched = await client.patch(
            second_url, json={document_field: changed, **controls}
        )
        assert patched.status_code == 200, patched.text
        before = (await client.get(second_url)).json()
        readiness = (await client.get(second_url + "/readiness")).json()
        failed_section = (
            "sensitive_consent"
            if document_field == "sensitive_consent_assessment"
            else "geolocation"
        )
        other_section = (
            "geolocation"
            if failed_section == "sensitive_consent"
            else "sensitive_consent"
        )
        assert readiness[failed_section]["result"] == (
            "incompleto" if answer == "pendiente" else "requiere_revision"
        )
        assert readiness[other_section]["result"] == "completo"
        assert readiness["special"]["detected_regimes"] == expected_regimes
        assert (
            readiness["special"]["context_current"]
            and readiness["eipd"]["context_current"]
        )
        rejection = await client.post(second_url + "/confirm")
        assert rejection.status_code == 409, rejection.text
        for section in ("special", "eipd"):
            assert rejection.json()["detail"][section] == readiness[section]
        assert (await client.get(second_url)).json() == before
        assert (await client.get(first_url)).json() == confirmed
        restored = await client.patch(
            second_url, json={document_field: payload[document_field], **controls}
        )
        assert restored.status_code == 200, restored.text
        # A positive EIPD answer still blocks even though both special documents are ready.
        positive = deepcopy(controls["eipd_screening"])
        positive["answers"][1]["answer"] = "si"
        assert (
            await client.patch(second_url, json={"eipd_screening": positive})
        ).status_code == 200
        readiness = (await client.get(second_url + "/readiness")).json()
        assert readiness["special"]["result"] == "regimenes_preparados"
        assert (await client.post(second_url + "/confirm")).status_code == 409
        assert (await client.get(first_url)).json() == confirmed
        assert (
            await client.patch(
                second_url, json={"eipd_screening": controls["eipd_screening"]}
            )
        ).status_code == 200
        readiness = (await client.get(second_url + "/readiness")).json()
        assert readiness["confirmation_blockers"] == []
        approved = await client.post(second_url + "/confirm")
        assert approved.status_code == 200, approved.text
        assert approved.json()["status"] == "confirmado"
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        assert (
            await client.patch(second_url, json={document_field: None})
        ).status_code == 409


@pytest.mark.parametrize(
    "special_version,eipd_version",
    [(1, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)],
)
async def test_api_salud_persistencia_compatibilidad_y_sql_null(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    negative_controls,
    _session_factory,
    complete_payload,
    special_version,
    eipd_version,
):
    from sqlalchemy.exc import IntegrityError

    from app.services import eipd as eipd_service
    from app.services import special_conditions as special_service

    treatment_id, payload = rat_m3
    rights = {
        "sanitary_purpose_analysis": "Aviso de prueba",
        "collection_context_analysis": "2026-10-06",
        "scope": {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]},
        "evidence": [{"evidence_type": "registro", "obtained_on": "2026-10-06"}],
    }
    payload.update(health_assessment=rights, consent_assessment=complete_payload)
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        assert (
            original["health_assessment"]["evidence"][0]["obtained_on"] == "2026-10-06"
        )
        assert original["special_conditions"]["context_binding"]["schema_version"] == 11
        assert original["eipd_screening"]["context_binding"]["schema_version"] == 12
        assert (await client.post(detail + "/confirm")).status_code == 409
        for invalid in (
            {"schema_version": 2},
            {"approved": True},
            {"collection_contexts": ["unknown"]},
            {"sanitary_purpose_covered": {"answer": "no_aplica"}},
            {"scope": {"unknown": True}},
            {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
        ):
            assert (
                await client.patch(detail, json={"health_assessment": invalid})
            ).status_code == 422
        assert (await client.get(detail)).json() == original
        assert (
            await client.patch(
                detail,
                headers={"X-Organization-Id": str(org_b_id)},
                json={"health_assessment": {}},
            )
        ).status_code == 403
        assert (
            await client.patch(detail, json={"justification": "Revisión"})
        ).status_code == 200
        assert (await client.get(detail)).json()["health_assessment"] == original[
            "health_assessment"
        ]
        changed = await client.patch(
            detail,
            json={"health_assessment": {"notes": "Cambio documental"}},
        )
        assert changed.status_code == 200
        assert (
            changed.json()["special_conditions"] == original["special_conditions"]
            and changed.json()["eipd_screening"] == original["eipd_screening"]
        )
        prep = (await client.get(detail + "/readiness")).json()
        assert (
            not prep["special"]["context_current"]
            and not prep["eipd"]["context_current"]
        )
        saved = await client.patch(
            detail,
            json={"health_assessment": rights, **negative_controls},
        )
        assert saved.status_code == 200
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["special"]["context_current"] and prep["eipd"]["context_current"]
        assert "expediente_salud_residual" in {
            i["code"] for i in prep["special"]["issues"]
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        special_args = [
            negative_controls["special_conditions"],
            original["rat_context_snapshot"],
            original["legal_basis"],
            original["consent_assessment"],
            None,
        ]
        special_args += [None] * (special_version - 1)
        old_special = getattr(
            special_service, f"bind_special_conditions_v{special_version}"
        )(*special_args).model_dump(mode="json")
        eipd_args = [
            negative_controls["eipd_screening"],
            original["rat_context_snapshot"],
            None,
        ]
        if eipd_version >= 2:
            eipd_args.append(old_special)
        eipd_args += [None] * max(0, eipd_version - 2)
        old_eipd = getattr(eipd_service, f"bind_eipd_screening_v{eipd_version}")(
            *eipd_args
        ).model_dump(mode="json")
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == uuid.UUID(original["id"]))
                .values(special_conditions=old_special, eipd_screening=old_eipd)
            )
            await db.commit()
        prep = (await client.get(detail + "/readiness")).json()
        for control in ("special", "eipd"):
            assert "asociacion_salud_no_cubierta" in {
                i["code"] for i in prep[control]["issues"]
            }
        assert (await client.get(detail)).json()["eipd_screening"] == old_eipd
        async with _session_factory() as db:
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        update(LegalAssessment)
                        .where(LegalAssessment.id == uuid.UUID(original["id"]))
                        .values(health_assessment=[])
                    )
            await db.rollback()
        deleted = await client.patch(detail, json={"health_assessment": None})
        assert deleted.status_code == 200
        final = (await client.get(detail)).json()
        assert final["health_assessment"] is None
        assert (
            final["special_conditions"] == old_special
            and final["eipd_screening"] == old_eipd
        )
        after = (await client.get(detail + "/readiness")).json()
        assert after["special"]["context_current"]
        assert after["eipd"]["context_current"] == (eipd_version != 1)
        assert all(
            "asociacion_salud_no_cubierta"
            not in {i["code"] for i in after[c]["issues"]}
            for c in ("special", "eipd")
        )
        async with _session_factory() as db:
            assert (
                await db.execute(
                    select(LegalAssessment.id).where(
                        LegalAssessment.id == uuid.UUID(original["id"]),
                        LegalAssessment.health_assessment.is_(None),
                    )
                )
            ).scalar_one()


async def test_api_declared_health_remains_blocked(
    client_a, rat_m3, org_a_id, complete_payload, _session_factory
):
    treatment_id, payload = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in payload["special_conditions"]["declarations"]:
        if declaration["question_id"] in ("datos_sensibles", "salud_perfil_biologico"):
            declaration.update(answer="si", rationale="Alcance documentado", **scope)
    payload["special_conditions"]["conditions"] = [
        {
            "regime_id": "salud_perfil_biologico_art16bis",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "art16bis",
            "documentary_analysis": "Por revisar",
            "evidence": [{"evidence_type": "registro", "reference": "Referencia"}],
            **scope,
        }
    ]
    payload.update(
        consent_assessment=complete_payload,
        health_assessment={
            "route": "consentimiento_expreso",
            "scope": scope,
            "collection_contexts": ["otro"],
            "sanitary_law_references": [
                {"official_source_url": "https://example.test/norma"}
            ],
            "evidence": [{"evidence_type": "registro", "obtained_on": "1900-01-01"}],
        },
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        assert (
            before["health_assessment"]["sanitary_law_references"][0][
                "official_source_url"
            ]
            == "https://example.test/norma"
        )
        assert before["health_assessment"]["evidence"][0]["obtained_on"] == "1900-01-01"
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        assert "salud_perfil_biologico_art16bis" in ready["special"]["detected_regimes"]
        assert ready["health"]["result"] == "incompleto"
        assert "expediente_salud_residual" not in {
            i["code"] for i in ready["special"]["issues"]
        }
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409, rejected.text
        assert (await client.get(detail)).json() == before


@pytest.mark.parametrize("context", ["otro", "laboral"])
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
async def test_api_health_confirmation_six_bases(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    _session_factory,
    context,
    basis,
    complete_lia_context,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
):
    from copy import deepcopy

    treatment_id, payload = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    if basis == "interes_legitimo_art13d":
        from app.db.models import TreatmentDataSource

        async with _session_factory() as db:
            db.add(
                TreatmentDataSource(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    source_type="titular",
                    is_public_source=False,
                )
            )
            await db.commit()
    complete_lia_context[0]["nature_and_scope"][
        "special_rules_description"
    ] = "Régimen sensible y de salud documentado"
    docs = {
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
    payload["legal_basis"] = basis
    if basis in docs:
        field, ordinary = docs[basis]
        payload[field] = ordinary
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in payload["special_conditions"]["declarations"]:
        if declaration["question_id"] in ("datos_sensibles", "salud_perfil_biologico"):
            declaration.update(answer="si", rationale="Datos de salud", **scope)
    common = {
        "authorization_route": "consentimiento",
        "uses_consent_assessment": True,
        "legal_reference": "Referencia documentada",
        "documentary_analysis": "Análisis documentado",
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
        **scope,
    }
    payload["special_conditions"]["conditions"] = [
        {
            **common,
            "regime_id": "sensibles_art16",
            "sensitive_condition_id": "consentimiento_expreso_art16",
        },
        {**common, "regime_id": "salud_perfil_biologico_art16bis"},
    ]
    sensitive = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Datos sensibles",
        "processing_operations": "Operaciones",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Declaración expresa",
        "technology_equivalence_analysis": "Equivalencia",
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
    }
    for field in (
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ):
        sensitive[field] = {"answer": "si", "rationale": "Comprobación"}
    health = {
        "purpose_description": "Gestión de clientes",
        "health_data_description": "Salud",
        "processing_operations": "Operaciones",
        "scope": scope,
        "route": "consentimiento_expreso",
        "sanitary_law_references": [
            {
                "norm_name": "Norma por revisar",
                "provision": "Artículo por identificar",
                "official_source_url": "https://example.test/norma",
                "applicability_analysis": "Aplicabilidad documentada",
            }
        ],
        "sanitary_purpose_analysis": "Finalidad documentada",
        "sanitary_purpose_covered": {"answer": "si", "rationale": "Cobertura"},
        "collection_contexts": [context],
        "collection_context_analysis": "Contexto documentado",
        "includes_data_cession": {"answer": "no", "rationale": "Sin cesión"},
        "includes_identifiable_biological_samples": {
            "answer": "no",
            "rationale": "Sin muestras",
        },
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
    }
    if context == "laboral":
        health.update(
            restricted_context_legal_references=deepcopy(
                health["sanitary_law_references"]
            ),
            restricted_context_analysis="Autorización documentada",
            restricted_context_authorization_documented={
                "answer": "si",
                "rationale": "Referencia",
            },
        )
    payload.update(
        consent_assessment=complete_payload,
        sensitive_consent_assessment=sensitive,
        health_assessment=health,
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["sensitive_consent"]["result"] == "completo"
        assert ready["health"]["result"] == (
            "completo" if context == "otro" else "requiere_revision"
        )
        assert (
            "salud_no_preparada" in {i["code"] for i in ready["confirmation_blockers"]}
        ) == (context == "laboral")
        assert "validador_no_implementado" not in {
            i["code"] for i in ready["special"]["issues"]
        }
        if context == "laboral":
            assert (await client.post(detail + "/confirm")).status_code == 409
        else:
            assert ready["confirmation_blockers"] == [], ready
        assert (await client.get(detail)).json() == before
        health["sanitary_purpose_covered"]["answer"] = "pendiente"
        assert (
            await client.patch(detail, json={"health_assessment": health})
        ).status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["health"]["result"] == "incompleto"
        assert "salud_no_preparada" in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert (
            not ready["special"]["context_current"]
            and not ready["eipd"]["context_current"]
        )
        assert (
            await client.patch(detail, json={"health_assessment": None})
        ).status_code == 200
        assert (await client.get(detail + "/readiness")).json()["health"][
            "result"
        ] == "incompleto"

        restored = await client.patch(
            detail,
            json={
                "health_assessment": before["health_assessment"],
                "special_conditions": payload["special_conditions"],
                "eipd_screening": payload["eipd_screening"],
            },
        )
        assert restored.status_code == 200, restored.text
        if context == "otro":
            positive = deepcopy(payload["eipd_screening"])
            positive["answers"][1]["answer"] = "si"
            assert (
                await client.patch(detail, json={"eipd_screening": positive})
            ).status_code == 200
            assert (await client.post(detail + "/confirm")).status_code == 409
            assert (await client.get(detail)).json()["status"] == "borrador"
            assert (
                await client.patch(
                    detail, json={"eipd_screening": payload["eipd_screening"]}
                )
            ).status_code == 200
            approved = await client.post(detail + "/confirm")
            assert approved.status_code == 200, approved.text
            assert approved.json()["status"] == "confirmado"
            assert (
                await client.patch(detail, json={"health_assessment": None})
            ).status_code == 409
            next_payload = {**payload, "health_assessment": before["health_assessment"]}
            second = await client.post(url, json=next_payload)
            assert second.status_code == 201, second.text
            second_url = url + "/" + second.json()["id"]
            incomplete = {"notes": "Pendiente"}
            assert (
                await client.patch(second_url, json={"health_assessment": incomplete})
            ).status_code == 200
            prep = (await client.get(second_url + "/readiness")).json()
            rejected = await client.post(second_url + "/confirm")
            assert rejected.status_code == 409
            for control in ("special", "eipd"):
                assert rejected.json()["detail"][control] == prep[control]
            assert (await client.get(detail)).json()["status"] == "confirmado"
            assert (
                await client.patch(
                    second_url,
                    json={
                        "health_assessment": before["health_assessment"],
                        "special_conditions": payload["special_conditions"],
                        "eipd_screening": payload["eipd_screening"],
                    },
                )
            ).status_code == 200
            approved = await client.post(second_url + "/confirm")
            assert approved.status_code == 200, approved.text
            assert (await client.get(detail)).json()["status"] == "reemplazado"


@pytest.mark.parametrize(
    "document_field,response_field",
    [
        ("sensitive_consent_assessment", "proof_available"),
        ("geolocation_assessment", "information_clear"),
        ("health_assessment", "sanitary_purpose_covered"),
    ],
)
@pytest.mark.parametrize("answer", ["no", "pendiente"])
async def test_api_health_sensitive_geolocation_joint_confirmation(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    complete_geolocation,
    geolocation_controls,
    _session_factory,
    document_field,
    response_field,
    answer,
):
    from copy import deepcopy

    treatment_id, payload = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    controls = deepcopy(geolocation_controls)
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(answer="si", rationale="Declaración expresa", **scope)
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "legal_reference": "art16",
            "documentary_analysis": "Declaración expresa",
            "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
            **scope,
        }
    )
    sensitive = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Categoría sensible",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Consentimiento expreso documentado",
        "technology_equivalence_analysis": "Equivalencia documentada",
        "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
    }
    for field in [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ]:
        sensitive[field] = {"answer": "si", "rationale": "Comprobación documentada"}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "salud_perfil_biologico":
            declaration.update(answer="si", rationale="Salud documentada", **scope)
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "salud_perfil_biologico_art16bis",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "Referencia sanitaria",
            "documentary_analysis": "Aplicabilidad documentada",
            "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
            **scope,
        }
    )
    health = {
        "purpose_description": "Gestión de clientes",
        "health_data_description": "Datos de salud",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "route": "consentimiento_expreso",
        "sanitary_law_references": [
            {
                "norm_name": "Norma por revisar",
                "provision": "Artículo por identificar",
                "official_source_url": "https://example.test/norma",
                "applicability_analysis": "Aplicabilidad documentada",
            }
        ],
        "sanitary_purpose_analysis": "Finalidad documentada",
        "sanitary_purpose_covered": {
            "answer": "si",
            "rationale": "Cobertura documentada",
        },
        "collection_contexts": ["otro"],
        "collection_context_analysis": "Contexto de recolección documentado",
        "includes_data_cession": {"answer": "no", "rationale": "Sin cesión"},
        "includes_identifiable_biological_samples": {
            "answer": "no",
            "rationale": "Sin muestras",
        },
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
    }
    payload = {
        **payload,
        **controls,
        "consent_assessment": complete_payload,
        "sensitive_consent_assessment": sensitive,
        "health_assessment": health,
        "geolocation_assessment": complete_geolocation,
    }
    expected_regimes = [
        "geolocalizacion_art16sexies",
        "salud_perfil_biologico_art16bis",
        "sensibles_art16",
    ]
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(url, json=payload)
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        readiness = (await client.get(first_url + "/readiness")).json()
        assert readiness["special"]["detected_regimes"] == expected_regimes
        assert readiness["special"]["result"] == "regimenes_preparados"
        assert (
            readiness["sensitive_consent"]["result"]
            == readiness["geolocation"]["result"]
            == "completo"
        )
        assert readiness["health"]["result"] == "completo"
        assert readiness["confirmation_blockers"] == []
        approved = await client.post(first_url + "/confirm")
        assert approved.status_code == 200, approved.text
        confirmed = (await client.get(first_url)).json()
        assert confirmed["status"] == "confirmado"
        second = await client.post(url, json=payload)
        assert second.status_code == 201, second.text
        second_url = url + "/" + second.json()["id"]
        original = second.json()
        changed = deepcopy(payload[document_field])
        changed[response_field]["answer"] = answer
        patched = await client.patch(second_url, json={document_field: changed})
        assert patched.status_code == 200, patched.text
        readiness = (await client.get(second_url + "/readiness")).json()
        assert (
            not readiness["special"]["context_current"]
            and not readiness["eipd"]["context_current"]
        )
        assert patched.json()["special_conditions"] == original["special_conditions"]
        assert patched.json()["eipd_screening"] == original["eipd_screening"]
        # Rebinding removes staleness but must not approve a negative/pending document.
        patched = await client.patch(
            second_url, json={document_field: changed, **controls}
        )
        assert patched.status_code == 200, patched.text
        before = (await client.get(second_url)).json()
        readiness = (await client.get(second_url + "/readiness")).json()
        failed_section = {
            "sensitive_consent_assessment": "sensitive_consent",
            "geolocation_assessment": "geolocation",
            "health_assessment": "health",
        }[document_field]
        other_section = (
            "sensitive_consent"
            if failed_section != "sensitive_consent"
            else "geolocation"
        )
        assert readiness[failed_section]["result"] == (
            "incompleto" if answer == "pendiente" else "requiere_revision"
        )
        assert readiness[other_section]["result"] == "completo"
        assert readiness["special"]["detected_regimes"] == expected_regimes
        assert (
            readiness["special"]["context_current"]
            and readiness["eipd"]["context_current"]
        )
        rejection = await client.post(second_url + "/confirm")
        assert rejection.status_code == 409, rejection.text
        for section in ("special", "eipd"):
            assert rejection.json()["detail"][section] == readiness[section]
        assert (await client.get(second_url)).json() == before
        assert (await client.get(first_url)).json() == confirmed
        restored = await client.patch(
            second_url, json={document_field: payload[document_field], **controls}
        )
        assert restored.status_code == 200, restored.text
        # A positive EIPD answer still blocks even though both special documents are ready.
        positive = deepcopy(controls["eipd_screening"])
        positive["answers"][1]["answer"] = "si"
        assert (
            await client.patch(second_url, json={"eipd_screening": positive})
        ).status_code == 200
        readiness = (await client.get(second_url + "/readiness")).json()
        assert readiness["special"]["result"] == "regimenes_preparados"
        assert (await client.post(second_url + "/confirm")).status_code == 409
        assert (await client.get(first_url)).json() == confirmed
        assert (
            await client.patch(
                second_url, json={"eipd_screening": controls["eipd_screening"]}
            )
        ).status_code == 200
        readiness = (await client.get(second_url + "/readiness")).json()
        assert readiness["confirmation_blockers"] == []
        approved = await client.post(second_url + "/confirm")
        assert approved.status_code == 200, approved.text
        assert approved.json()["status"] == "confirmado"
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        assert (
            await client.patch(second_url, json={document_field: None})
        ).status_code == 409


@pytest.mark.parametrize("giver", ["representante_legal", "mandatario"])
@pytest.mark.parametrize("with_health", [False, True])
async def test_api_sensitive_representation_preserves_confirmed(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    complete_geolocation,
    geolocation_controls,
    _session_factory,
    giver,
    with_health,
):
    from copy import deepcopy

    treatment_id, payload = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    controls = deepcopy(geolocation_controls)
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(answer="si", rationale="Declaración expresa", **scope)
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "legal_reference": "art16",
            "documentary_analysis": "Declaración expresa",
            "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
            **scope,
        }
    )
    sensitive = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Categoría sensible",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Consentimiento expreso documentado",
        "technology_equivalence_analysis": "Equivalencia documentada",
        "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
    }
    for field in [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ]:
        sensitive[field] = {"answer": "si", "rationale": "Comprobación documentada"}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "salud_perfil_biologico":
            declaration.update(answer="si", rationale="Salud documentada", **scope)
    controls["special_conditions"]["conditions"].append(
        {
            "regime_id": "salud_perfil_biologico_art16bis",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "Referencia sanitaria",
            "documentary_analysis": "Aplicabilidad documentada",
            "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
            **scope,
        }
    )
    health = {
        "purpose_description": "Gestión de clientes",
        "health_data_description": "Datos de salud",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "route": "consentimiento_expreso",
        "sanitary_law_references": [
            {
                "norm_name": "Norma por revisar",
                "provision": "Artículo por identificar",
                "official_source_url": "https://example.test/norma",
                "applicability_analysis": "Aplicabilidad documentada",
            }
        ],
        "sanitary_purpose_analysis": "Finalidad documentada",
        "sanitary_purpose_covered": {
            "answer": "si",
            "rationale": "Cobertura documentada",
        },
        "collection_contexts": ["otro"],
        "collection_context_analysis": "Contexto de recolección documentado",
        "includes_data_cession": {"answer": "no", "rationale": "Sin cesión"},
        "includes_identifiable_biological_samples": {
            "answer": "no",
            "rationale": "Sin muestras",
        },
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
    }
    payload = {
        **payload,
        **controls,
        "consent_assessment": complete_payload,
        "sensitive_consent_assessment": sensitive,
        "health_assessment": health,
        "geolocation_assessment": complete_geolocation,
    }
    if not with_health:
        payload.pop("health_assessment")
        controls["special_conditions"]["conditions"] = [
            c
            for c in controls["special_conditions"]["conditions"]
            if c["regime_id"] != "salud_perfil_biologico_art16bis"
        ]
        for declaration in controls["special_conditions"]["declarations"]:
            if declaration["question_id"] == "salud_perfil_biologico":
                declaration.update(answer="no", rationale="Sin salud en este alcance")
                declaration.pop("data_category_codes", None)
                declaration.pop("data_subject_codes", None)
        payload.update(deepcopy(controls))
    document_field = "consent_assessment"
    expected_regimes = [
        "geolocalizacion_art16sexies",
        "salud_perfil_biologico_art16bis",
        "sensibles_art16",
    ]
    if not with_health:
        expected_regimes.remove("salud_perfil_biologico_art16bis")
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(url, json=payload)
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        readiness = (await client.get(first_url + "/readiness")).json()
        assert readiness["special"]["detected_regimes"] == expected_regimes
        assert readiness["special"]["result"] == "regimenes_preparados"
        assert (
            readiness["sensitive_consent"]["result"]
            == readiness["geolocation"]["result"]
            == "completo"
        )
        if with_health:
            assert readiness["health"]["result"] == "completo"
        else:
            assert readiness["health"] is None
        assert readiness["confirmation_blockers"] == []
        approved = await client.post(first_url + "/confirm")
        assert approved.status_code == 200, approved.text
        confirmed = (await client.get(first_url)).json()
        assert confirmed["status"] == "confirmado"
        second = await client.post(url, json=payload)
        assert second.status_code == 201, second.text
        second_url = url + "/" + second.json()["id"]
        original = second.json()
        changed = deepcopy(payload[document_field])
        changed["given_by"] = giver
        if giver == "mandatario":
            changed["answers"].append(
                {"question_id": "mandatario_facultad_expresa", "answer": "si"}
            )
        patched = await client.patch(second_url, json={document_field: changed})
        assert patched.status_code == 200, patched.text
        readiness = (await client.get(second_url + "/readiness")).json()
        assert (
            not readiness["special"]["context_current"]
            and readiness["eipd"]["context_current"]
        )
        assert patched.json()["special_conditions"] == original["special_conditions"]
        assert patched.json()["eipd_screening"] == original["eipd_screening"]
        # Rebinding removes staleness but must not approve a negative/pending document.
        patched = await client.patch(
            second_url, json={document_field: changed, **controls}
        )
        assert patched.status_code == 200, patched.text
        before = (await client.get(second_url)).json()
        readiness = (await client.get(second_url + "/readiness")).json()
        assert readiness["sensitive_consent"]["result"] == "requiere_revision"
        assert "representacion_no_preparada" in {
            issue["code"] for issue in readiness["sensitive_consent"]["issues"]
        }
        assert readiness["geolocation"]["result"] == "completo"
        if with_health:
            assert readiness["health"]["result"] == "requiere_revision"
        else:
            assert readiness["health"] is None
        assert readiness["special"]["detected_regimes"] == expected_regimes
        assert (
            readiness["special"]["context_current"]
            and readiness["eipd"]["context_current"]
        )
        rejection = await client.post(second_url + "/confirm")
        assert rejection.status_code == 409, rejection.text
        for section in ("special", "eipd"):
            assert rejection.json()["detail"][section] == readiness[section]
        assert (await client.get(second_url)).json() == before
        assert (await client.get(first_url)).json() == confirmed
        restored = await client.patch(
            second_url, json={document_field: payload[document_field], **controls}
        )
        assert restored.status_code == 200, restored.text
        # A positive EIPD answer still blocks even though both special documents are ready.
        positive = deepcopy(controls["eipd_screening"])
        positive["answers"][1]["answer"] = "si"
        assert (
            await client.patch(second_url, json={"eipd_screening": positive})
        ).status_code == 200
        readiness = (await client.get(second_url + "/readiness")).json()
        assert readiness["special"]["result"] == "regimenes_preparados"
        assert (await client.post(second_url + "/confirm")).status_code == 409
        assert (await client.get(first_url)).json() == confirmed
        assert (
            await client.patch(
                second_url, json={"eipd_screening": controls["eipd_screening"]}
            )
        ).status_code == 200
        readiness = (await client.get(second_url + "/readiness")).json()
        assert readiness["confirmation_blockers"] == []
        approved = await client.post(second_url + "/confirm")
        assert approved.status_code == 200, approved.text
        assert approved.json()["status"] == "confirmado"
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        assert (
            await client.patch(second_url, json={document_field: None})
        ).status_code == 409


@pytest.mark.parametrize(
    "special_version,eipd_version",
    [(1, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)],
)
async def test_api_biometria_persistencia_compatibilidad_y_sql_null(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    negative_controls,
    _session_factory,
    complete_payload,
    special_version,
    eipd_version,
):
    from sqlalchemy.exc import IntegrityError

    from app.services import eipd as eipd_service
    from app.services import special_conditions as special_service

    treatment_id, payload = rat_m3
    rights = {
        "unique_identification_analysis": "Aviso de prueba",
        "systems_coverage_analysis": "2026-10-06",
        "scope": {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]},
        "evidence": [{"evidence_type": "registro", "obtained_on": "2026-10-06"}],
    }
    payload.update(biometric_assessment=rights, consent_assessment=complete_payload)
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        assert (
            original["biometric_assessment"]["evidence"][0]["obtained_on"]
            == "2026-10-06"
        )
        assert original["special_conditions"]["context_binding"]["schema_version"] == 11
        assert original["eipd_screening"]["context_binding"]["schema_version"] == 12
        assert (await client.post(detail + "/confirm")).status_code == 409
        for invalid in (
            {"schema_version": 2},
            {"approved": True},
            {"systems": [{"approved": True}]},
            {"unique_identification_confirmed": {"answer": "no_aplica"}},
            {"scope": {"unknown": True}},
            {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
        ):
            assert (
                await client.patch(detail, json={"biometric_assessment": invalid})
            ).status_code == 422
        assert (await client.get(detail)).json() == original
        assert (
            await client.patch(
                detail,
                headers={"X-Organization-Id": str(org_b_id)},
                json={"biometric_assessment": {}},
            )
        ).status_code == 403
        assert (
            await client.patch(detail, json={"justification": "Revisión"})
        ).status_code == 200
        assert (await client.get(detail)).json()["biometric_assessment"] == original[
            "biometric_assessment"
        ]
        changed = await client.patch(
            detail,
            json={"biometric_assessment": {"notes": "Cambio documental"}},
        )
        assert changed.status_code == 200
        assert (
            changed.json()["special_conditions"] == original["special_conditions"]
            and changed.json()["eipd_screening"] == original["eipd_screening"]
        )
        prep = (await client.get(detail + "/readiness")).json()
        assert (
            not prep["special"]["context_current"]
            and not prep["eipd"]["context_current"]
        )
        saved = await client.patch(
            detail,
            json={"biometric_assessment": rights, **negative_controls},
        )
        assert saved.status_code == 200
        prep = (await client.get(detail + "/readiness")).json()
        assert prep["special"]["context_current"] and prep["eipd"]["context_current"]
        assert "expediente_biometria_residual" in {
            i["code"] for i in prep["special"]["issues"]
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        special_args = [
            negative_controls["special_conditions"],
            original["rat_context_snapshot"],
            original["legal_basis"],
            original["consent_assessment"],
            None,
        ]
        special_args += [None] * (special_version - 1)
        old_special = getattr(
            special_service, f"bind_special_conditions_v{special_version}"
        )(*special_args).model_dump(mode="json")
        eipd_args = [
            negative_controls["eipd_screening"],
            original["rat_context_snapshot"],
            None,
        ]
        if eipd_version >= 2:
            eipd_args.append(old_special)
        eipd_args += [None] * max(0, eipd_version - 2)
        old_eipd = getattr(eipd_service, f"bind_eipd_screening_v{eipd_version}")(
            *eipd_args
        ).model_dump(mode="json")
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == uuid.UUID(original["id"]))
                .values(special_conditions=old_special, eipd_screening=old_eipd)
            )
            await db.commit()
        prep = (await client.get(detail + "/readiness")).json()
        for control in ("special", "eipd"):
            assert "asociacion_biometria_no_cubierta" in {
                i["code"] for i in prep[control]["issues"]
            }
        assert (await client.get(detail)).json()["eipd_screening"] == old_eipd
        async with _session_factory() as db:
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    await db.execute(
                        update(LegalAssessment)
                        .where(LegalAssessment.id == uuid.UUID(original["id"]))
                        .values(biometric_assessment=[])
                    )
            await db.rollback()
        deleted = await client.patch(detail, json={"biometric_assessment": None})
        assert deleted.status_code == 200
        final = (await client.get(detail)).json()
        assert final["biometric_assessment"] is None
        assert (
            final["special_conditions"] == old_special
            and final["eipd_screening"] == old_eipd
        )
        after = (await client.get(detail + "/readiness")).json()
        assert after["special"]["context_current"]
        assert after["eipd"]["context_current"] == (eipd_version != 1)
        assert all(
            "asociacion_biometria_no_cubierta"
            not in {i["code"] for i in after[c]["issues"]}
            for c in ("special", "eipd")
        )
        async with _session_factory() as db:
            assert (
                await db.execute(
                    select(LegalAssessment.id).where(
                        LegalAssessment.id == uuid.UUID(original["id"]),
                        LegalAssessment.biometric_assessment.is_(None),
                    )
                )
            ).scalar_one()
        # Removing the residual draft document restores the ordinary route.
        rebound = await client.patch(detail, json=negative_controls)
        assert rebound.status_code == 200, rebound.text
        assert (await client.post(detail + "/confirm")).status_code == 200
        confirmed = (await client.get(detail)).json()
        for value in ({}, None):
            protected = await client.patch(detail, json={"biometric_assessment": value})
            assert protected.status_code == 409, protected.text
            assert (await client.get(detail)).json() == confirmed


async def test_api_declared_biometric_remains_blocked(
    client_a, rat_m3, org_a_id, complete_payload, _session_factory
):
    treatment_id, payload = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in payload["special_conditions"]["declarations"]:
        if declaration["question_id"] in (
            "datos_sensibles",
            "biometricos_identificacion_unica",
        ):
            declaration.update(answer="si", rationale="Alcance documentado", **scope)
    payload["special_conditions"]["conditions"] = [
        {
            "regime_id": "biometricos_art16ter",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "art16ter",
            "documentary_analysis": "Por revisar",
            "evidence": [{"evidence_type": "registro", "reference": "Referencia"}],
            **scope,
        }
    ]
    payload.update(
        consent_assessment=complete_payload,
        biometric_assessment={
            "route": "consentimiento_expreso",
            "scope": scope,
            "systems": [{"system_reference": "Sistema A"}],
            "evidence": [{"evidence_type": "registro", "obtained_on": "1900-01-01"}],
        },
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        assert (
            before["biometric_assessment"]["evidence"][0]["obtained_on"] == "1900-01-01"
        )
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        assert "biometricos_art16ter" in ready["special"]["detected_regimes"]
        assert "biometria_no_preparada" in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert "expediente_biometria_residual" not in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409, rejected.text
        assert rejected.json()["detail"]["special"] == ready["special"]
        assert rejected.json()["detail"]["eipd"] == ready["eipd"]
        assert (await client.get(detail)).json() == before


async def test_api_biometric_confirmation_preserves_current(
    client_a, rat_m3, org_a_id, complete_payload, negative_controls, _session_factory
):
    from copy import deepcopy

    treatment_id, payload = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    controls = deepcopy(negative_controls)
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "datos_sensibles":
            declaration.update(answer="si", rationale="Declaración expresa", **scope)
    controls["special_conditions"].setdefault("conditions", []).append(
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "legal_reference": "art16",
            "documentary_analysis": "Declaración expresa",
            "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
            **scope,
        }
    )
    sensitive = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Categoría sensible",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Consentimiento expreso documentado",
        "technology_equivalence_analysis": "Equivalencia documentada",
        "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
    }
    for field in [
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ]:
        sensitive[field] = {"answer": "si", "rationale": "Comprobación documentada"}

    for declaration in controls["special_conditions"]["declarations"]:
        if declaration["question_id"] == "biometricos_identificacion_unica":
            declaration.update(
                answer="si", rationale="Identificación biométrica", **scope
            )
    controls["special_conditions"].setdefault("conditions", []).append(
        {
            "regime_id": "biometricos_art16ter",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "art16ter",
            "documentary_analysis": "Información específica documentada",
            "evidence": [{"evidence_type": "aviso", "reference": "Aviso"}],
            **scope,
        }
    )
    system = {
        field: "Descripción documentada"
        for field in [
            "system_reference",
            "system_name",
            "system_description",
            "specific_purpose",
            "purpose_alignment_analysis",
            "use_period_description",
            "retention_alignment_analysis",
            "rights_exercise_description",
            "rights_contact_channel",
            "information_reference",
        ]
    }
    for field in [
        "system_identification_disclosed",
        "purpose_disclosed",
        "use_period_disclosed",
        "rights_exercise_disclosed",
    ]:
        system[field] = {"answer": "si", "rationale": "Información proporcionada"}
    system["evidence"] = [{"evidence_type": "aviso", "reference": "Aviso"}]
    biometric = {
        "purpose_description": "Gestión de clientes",
        "biometric_data_description": "Categoría biométrica",
        "processing_operations": "Identificación",
        "scope": scope,
        "route": "consentimiento_expreso",
        "unique_identification_analysis": "Identificación única documentada",
        "unique_identification_confirmed": {
            "answer": "si",
            "rationale": "Identificación",
        },
        "systems_coverage_analysis": "Sistema documentado",
        "all_systems_documented": {
            "answer": "si",
            "rationale": "Cobertura documentada",
        },
        "systems": [system],
        "evidence": [{"evidence_type": "aviso", "reference": "Aviso"}],
    }
    payload.update(
        **controls,
        consent_assessment=complete_payload,
        sensitive_consent_assessment=sensitive,
        biometric_assessment=biometric,
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["biometric"]["result"] == "completo"
        assert "biometria_no_preparada" not in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert ready["confirmation_blockers"] == []
        approved = await client.post(detail + "/confirm")
        assert approved.status_code == 200, approved.text
        first_detail = detail
        confirmed = (await client.get(detail)).json()
        second = await client.post(url, json=payload)
        assert second.status_code == 201, second.text
        detail = url + "/" + second.json()["id"]
        changed = deepcopy(biometric)
        changed["systems"][0]["purpose_disclosed"]["answer"] = "pendiente"
        assert (
            await client.patch(detail, json={"biometric_assessment": changed})
        ).status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert (
            not ready["special"]["context_current"]
            and not ready["eipd"]["context_current"]
        )
        assert ready["biometric"]["result"] == "incompleto"
        assert "biometria_no_preparada" in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert (
            await client.patch(
                detail, json={"biometric_assessment": changed, **controls}
            )
        ).status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        before = (await client.get(detail)).json()
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409
        assert (
            rejected.json()["detail"]["confirmation_blockers"]
            == ready["confirmation_blockers"]
        )
        assert (await client.get(detail)).json() == before
        assert (await client.get(first_detail)).json() == confirmed
        assert (
            await client.patch(
                detail, json={"biometric_assessment": biometric, **controls}
            )
        ).status_code == 200
        assert (await client.get(detail + "/readiness")).json()["biometric"][
            "result"
        ] == "completo"
        assert (
            await client.patch(detail, json={"biometric_assessment": None, **controls})
        ).status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["biometric"]["result"] == "incompleto"
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(first_detail)).json() == confirmed
        restored = await client.patch(
            detail, json={"biometric_assessment": biometric, **controls}
        )
        assert restored.status_code == 200
        positive = deepcopy(controls["eipd_screening"])
        positive["answers"][0]["answer"] = "si"
        assert (
            await client.patch(detail, json={"eipd_screening": positive})
        ).status_code == 200
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(first_detail)).json() == confirmed
        assert (
            await client.patch(
                detail, json={"eipd_screening": controls["eipd_screening"]}
            )
        ).status_code == 200
        approved = await client.post(detail + "/confirm")
        assert approved.status_code == 200, approved.text
        assert (await client.get(first_detail)).json()["status"] == "reemplazado"
        assert (
            await client.patch(detail, json={"biometric_assessment": None})
        ).status_code == 409


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
async def test_api_biometric_confirmation_six_bases(
    client_a,
    rat_m3,
    org_a_id,
    complete_payload,
    _session_factory,
    basis,
    complete_lia_context,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
):
    from copy import deepcopy

    treatment_id, payload = rat_m3
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentDataCategory)
            .where(TreatmentDataCategory.treatment_id == treatment_id)
            .values(is_sensitive=True)
        )
        await db.commit()
    if basis == "interes_legitimo_art13d":
        from app.db.models import TreatmentDataSource

        async with _session_factory() as db:
            db.add(
                TreatmentDataSource(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    source_type="titular",
                    is_public_source=False,
                )
            )
            await db.commit()
    complete_lia_context[0]["nature_and_scope"][
        "special_rules_description"
    ] = "Régimen sensible y biométrico documentado"
    docs = {
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
    payload["legal_basis"] = basis
    if basis in docs:
        field, ordinary = docs[basis]
        payload[field] = ordinary
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    for declaration in payload["special_conditions"]["declarations"]:
        if declaration["question_id"] in (
            "datos_sensibles",
            "biometricos_identificacion_unica",
        ):
            declaration.update(
                answer="si", rationale="Identificación biométrica", **scope
            )
    common = {
        "authorization_route": "consentimiento",
        "uses_consent_assessment": True,
        "legal_reference": "Referencia documentada",
        "documentary_analysis": "Análisis documentado",
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
        **scope,
    }
    payload["special_conditions"]["conditions"] = [
        {
            **common,
            "regime_id": "sensibles_art16",
            "sensitive_condition_id": "consentimiento_expreso_art16",
        },
        {**common, "regime_id": "biometricos_art16ter"},
    ]
    sensitive = {
        "purpose_description": "Gestión de clientes",
        "sensitive_data_description": "Datos sensibles",
        "processing_operations": "Operaciones",
        "scope": scope,
        "expression_method": "tecnologico_equivalente",
        "declaration_reference": "Registro",
        "declaration_content_analysis": "Declaración expresa",
        "technology_equivalence_analysis": "Equivalencia",
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
    }
    for field in (
        "express_declaration_documented",
        "sensitive_scope_explicit",
        "purpose_specific",
        "proof_available",
        "consent_current",
    ):
        sensitive[field] = {"answer": "si", "rationale": "Comprobación"}
    system = {
        field: "Descripción documentada"
        for field in [
            "system_reference",
            "system_name",
            "system_description",
            "specific_purpose",
            "purpose_alignment_analysis",
            "use_period_description",
            "retention_alignment_analysis",
            "rights_exercise_description",
            "rights_contact_channel",
            "information_reference",
        ]
    }
    for field in [
        "system_identification_disclosed",
        "purpose_disclosed",
        "use_period_disclosed",
        "rights_exercise_disclosed",
    ]:
        system[field] = {"answer": "si", "rationale": "Información proporcionada"}
    system["evidence"] = [{"evidence_type": "aviso", "reference": "Aviso"}]
    biometric = {
        "purpose_description": "Gestión de clientes",
        "biometric_data_description": "Categoría biométrica",
        "processing_operations": "Identificación",
        "scope": scope,
        "route": "consentimiento_expreso",
        "unique_identification_analysis": "Identificación única documentada",
        "unique_identification_confirmed": {
            "answer": "si",
            "rationale": "Identificación",
        },
        "systems_coverage_analysis": "Sistema documentado",
        "all_systems_documented": {
            "answer": "si",
            "rationale": "Cobertura documentada",
        },
        "systems": [system],
        "evidence": [{"evidence_type": "aviso", "reference": "Aviso"}],
    }
    payload.update(
        consent_assessment=complete_payload,
        sensitive_consent_assessment=sensitive,
        biometric_assessment=biometric,
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["sensitive_consent"]["result"] == "completo"
        assert ready["biometric"]["result"] == "completo"
        assert "biometria_no_preparada" not in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert "validador_no_implementado" not in {
            i["code"] for i in ready["special"]["issues"]
        }
        assert ready["confirmation_blockers"] == [], ready
        assert (await client.get(detail)).json() == before
        biometric["unique_identification_confirmed"]["answer"] = "pendiente"
        assert (
            await client.patch(detail, json={"biometric_assessment": biometric})
        ).status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["biometric"]["result"] == "incompleto"
        assert "biometria_no_preparada" in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert not ready["special"]["context_current"] and (
            not ready["eipd"]["context_current"]
        )
        assert (
            await client.patch(detail, json={"biometric_assessment": None})
        ).status_code == 200
        assert (await client.get(detail + "/readiness")).json()["biometric"][
            "result"
        ] == "incompleto"
        restored = await client.patch(
            detail,
            json={
                "biometric_assessment": before["biometric_assessment"],
                "special_conditions": payload["special_conditions"],
                "eipd_screening": payload["eipd_screening"],
            },
        )
        assert restored.status_code == 200, restored.text
        positive = deepcopy(payload["eipd_screening"])
        positive["answers"][1]["answer"] = "si"
        assert (
            await client.patch(detail, json={"eipd_screening": positive})
        ).status_code == 200
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json()["status"] == "borrador"
        assert (
            await client.patch(
                detail, json={"eipd_screening": payload["eipd_screening"]}
            )
        ).status_code == 200
        approved = await client.post(detail + "/confirm")
        assert approved.status_code == 200, approved.text
        assert approved.json()["status"] == "confirmado"
        confirmed_before = (await client.get(detail)).json()
        assert (
            await client.patch(detail, json={"biometric_assessment": None})
        ).status_code == 409
        next_payload = {
            **payload,
            "biometric_assessment": before["biometric_assessment"],
        }
        second = await client.post(url, json=next_payload)
        assert second.status_code == 201, second.text
        second_url = url + "/" + second.json()["id"]
        incomplete = {"notes": "Pendiente"}
        assert (
            await client.patch(second_url, json={"biometric_assessment": incomplete})
        ).status_code == 200
        prep = (await client.get(second_url + "/readiness")).json()
        draft_before = (await client.get(second_url)).json()
        rejected = await client.post(second_url + "/confirm")
        assert rejected.status_code == 409
        for control in ("special", "eipd"):
            assert rejected.json()["detail"][control] == prep[control]
        assert (await client.get(detail)).json() == confirmed_before
        assert (await client.get(second_url)).json() == draft_before
        assert (
            await client.patch(
                second_url,
                json={
                    "biometric_assessment": before["biometric_assessment"],
                    "special_conditions": payload["special_conditions"],
                    "eipd_screening": payload["eipd_screening"],
                },
            )
        ).status_code == 200
        approved = await client.post(second_url + "/confirm")
        assert approved.status_code == 200, approved.text
        assert (await client.get(detail)).json()["status"] == "reemplazado"


@pytest.mark.parametrize(
    "fields",
    [
        ["sensitive_rights_exception_assessment"],
        ["biometric_rights_exception_assessment"],
        [
            "sensitive_rights_exception_assessment",
            "biometric_rights_exception_assessment",
        ],
    ],
)
async def test_api_rights_exceptions_storage_and_protection(
    client_a, rat_m3, org_a_id, org_b_id, complete_payload, _session_factory, fields
):
    from sqlalchemy.exc import IntegrityError

    treatment_id, payload = rat_m3
    payload["consent_assessment"] = complete_payload
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(url, json=payload)
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        assert (await client.post(first_url + "/confirm")).status_code == 200
        confirmed = (await client.get(first_url)).json()
        for field in fields:
            assert confirmed[field] is None
        documents = {
            field: {
                "exception_basis": (
                    "defensa_derechos_art16d"
                    if field.startswith("sensitive")
                    else "defensa_derechos_art16bis_d"
                ),
                "context": {
                    "context_reference": "Caso documental",
                    "forum_type": "organo_administrativo",
                    "evidence": [
                        {"evidence_type": "caso", "obtained_on": "1900-01-01"}
                    ],
                },
                "evidence": [
                    {"evidence_type": "expediente", "obtained_on": "2026-10-06"}
                ],
            }
            for field in fields
        }
        created = await client.post(url, json={**payload, **documents})
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        original = (await client.get(detail)).json()
        assert original["special_conditions"]["context_binding"]["schema_version"] == 11
        assert original["eipd_screening"]["context_binding"]["schema_version"] == 12
        initial_ready = (await client.get(detail + "/readiness")).json()
        assert initial_ready["special"]["context_current"]
        assert initial_ready["eipd"]["context_current"]
        for field in fields:
            assert original[field]["evidence"][0]["obtained_on"] == "2026-10-06"
            assert (
                original[field]["context"]["evidence"][0]["obtained_on"] == "1900-01-01"
            )
        assert (
            await client.patch(detail, json={"justification": "Revisión"})
        ).status_code == 200
        preserved = (await client.get(detail)).json()
        for field in fields:
            assert preserved[field] == original[field]
            assert (
                await client.patch(
                    detail,
                    headers={"X-Organization-Id": str(org_b_id)},
                    json={field: {}},
                )
            ).status_code == 403
            for invalid in (
                {"approved": True},
                {"schema_version": 2},
                {"context": {"forum_type": "organo_publico"}},
                {"exception_conditions_met": {"answer": "no_aplica"}},
            ):
                assert (
                    await client.patch(detail, json={field: invalid})
                ).status_code == 422
            assert (await client.get(detail)).json() == preserved
        ready = (await client.get(detail + "/readiness")).json()
        association_blockers = [
            b
            for b in ready["confirmation_blockers"]
            if b["code"] == "excepcion_derechos_no_preparada"
        ]
        assert {b["field"] for b in association_blockers} == set(fields)
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409, rejected.text
        assert (
            rejected.json()["detail"]["confirmation_blockers"]
            == ready["confirmation_blockers"]
        )
        assert (await client.get(detail)).json() == preserved
        assert (await client.get(first_url)).json() == confirmed
        for field in fields:
            partial = await client.patch(
                detail, json={field: {"notes": "Objeto nuevo"}}
            )
            assert partial.status_code == 200
            assert partial.json()[field]["context"] is None
            assert partial.json()[field]["evidence"] == []
            async with _session_factory() as db:
                with pytest.raises(IntegrityError):
                    async with db.begin_nested():
                        await db.execute(
                            update(LegalAssessment)
                            .where(LegalAssessment.id == uuid.UUID(original["id"]))
                            .values(**{field: []})
                        )
                await db.rollback()
        deleted = await client.patch(detail, json={field: None for field in fields})
        assert deleted.status_code == 200
        for field in fields:
            assert deleted.json()[field] is None
            async with _session_factory() as db:
                assert (
                    await db.execute(
                        select(LegalAssessment.id).where(
                            LegalAssessment.id == uuid.UUID(original["id"]),
                            getattr(LegalAssessment, field).is_(None),
                        )
                    )
                ).scalar_one()
        stale = (await client.get(detail + "/readiness")).json()
        assert not stale["special"]["context_current"]
        assert not stale["eipd"]["context_current"]
        assert deleted.json()["rat_context_hash"] == original["rat_context_hash"]
        assert deleted.json()["special_conditions"] == original["special_conditions"]
        assert deleted.json()["eipd_screening"] == original["eipd_screening"]
        assert (await client.get(detail)).json() == deleted.json()
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == deleted.json()
        assert (await client.get(first_url)).json() == confirmed
        rebound = await client.patch(
            detail,
            json={
                "special_conditions": payload["special_conditions"],
                "eipd_screening": payload["eipd_screening"],
            },
        )
        assert rebound.status_code == 200, rebound.text
        assert (await client.get(detail + "/readiness")).json()[
            "confirmation_blockers"
        ] == []
        assert (await client.post(detail + "/confirm")).status_code == 200
        assert (await client.get(first_url)).json()["status"] == "reemplazado"
        second_confirmed = (await client.get(detail)).json()
        for field in fields:
            for value in ({}, None):
                assert (
                    await client.patch(detail, json={field: value})
                ).status_code == 409
                assert (await client.get(detail)).json() == second_confirmed


@pytest.mark.parametrize(
    "kind,version",
    [("special", n) for n in range(1, 10)] + [("eipd", n) for n in range(1, 11)],
)
async def test_api_rights_exception_historical_associations(
    client_a, rat_m3, org_a_id, complete_payload, _session_factory, kind, version
):
    from inspect import signature

    from app.services import eipd, special_conditions

    treatment_id, payload = rat_m3
    payload.update(
        consent_assessment=complete_payload,
        sensitive_rights_exception_assessment={},
        biometric_rights_exception_assessment={},
    )
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        created = await client.post(url, json=payload)
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        rat = original["rat_context_snapshot"]
        if kind == "special":
            bind = getattr(special_conditions, f"bind_special_conditions_v{version}")
            args = [rat, original["legal_basis"], original["consent_assessment"]] + [
                None
            ] * 9
            field = "special_conditions"
        else:
            bind = getattr(eipd, f"bind_eipd_screening_v{version}")
            args = [rat, None, original["special_conditions"]] + [None] * 8
            field = "eipd_screening"
        old = bind(
            payload[field], *args[: len(signature(bind).parameters) - 1]
        ).model_dump(mode="json")
        async with _session_factory() as db:
            await db.execute(
                update(LegalAssessment)
                .where(LegalAssessment.id == uuid.UUID(original["id"]))
                .values(**{field: old})
            )
            await db.commit()
        before = (await client.get(detail)).json()
        ready = (await client.get(detail + "/readiness")).json()
        assert not ready[kind]["context_current"]
        assert {
            i["code"]
            for i in ready[kind]["issues"]
            if "asociacion_excepcion" in i["code"]
        } == {
            "asociacion_excepcion_sensible_no_cubierta",
            "asociacion_excepcion_biometrica_no_cubierta",
        }
        assert (await client.get(detail)).json() == before
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409, rejected.text
        assert (
            rejected.json()["detail"]["confirmation_blockers"]
            == ready["confirmation_blockers"]
        )
        assert (await client.get(detail)).json() == before
        rebound = await client.patch(
            detail,
            json={
                "special_conditions": payload["special_conditions"],
                "eipd_screening": payload["eipd_screening"],
            },
        )
        assert rebound.status_code == 200, rebound.text
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        expected_codes = {"excepcion_derechos_no_preparada"}
        if (
            "sensitive_rights_exception_assessment" in rebound.json()
            and rebound.json()["sensitive_rights_exception_assessment"] is not None
        ):
            expected_codes.add("condiciones_especiales_no_preparadas")
            assert "expediente_excepcion_sensible_residual" in {
                i["code"] for i in ready["special"]["issues"]
            }
        if rebound.json()["biometric_rights_exception_assessment"] is not None:
            expected_codes.add("condiciones_especiales_no_preparadas")
            assert "expediente_excepcion_biometrica_residual" in {
                i["code"] for i in ready["special"]["issues"]
            }
        assert {i["code"] for i in ready["confirmation_blockers"]} == expected_codes
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == rebound.json()


@pytest.mark.parametrize(
    "fields",
    [
        ["sensitive_rights_exception_assessment"],
        ["biometric_rights_exception_assessment"],
        [
            "sensitive_rights_exception_assessment",
            "biometric_rights_exception_assessment",
        ],
    ],
)
async def test_api_rights_exception_rebinding_keeps_gate(
    client_a, rat_m3, org_a_id, complete_payload, fields
):
    from copy import deepcopy

    treatment_id, payload = rat_m3
    payload["consent_assessment"] = complete_payload
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(url, json=payload)
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        assert (await client.post(first_url + "/confirm")).status_code == 200
        confirmed = (await client.get(first_url)).json()
        created = await client.post(
            url, json={**payload, **{field: {} for field in fields}}
        )
        assert created.status_code == 201, created.text
        original = created.json()
        detail = url + "/" + original["id"]
        for field in fields:
            updated = await client.patch(
                detail,
                json={
                    field: {
                        "context": {"context_reference": "Caso revisado"},
                        "evidence": [
                            {"evidence_type": "caso", "obtained_on": "2026-10-06"}
                        ],
                    }
                },
            )
            assert updated.status_code == 200, updated.text
        before = (await client.get(detail)).json()
        assert before["rat_context_hash"] == original["rat_context_hash"]
        assert before["special_conditions"] == original["special_conditions"]
        assert before["eipd_screening"] == original["eipd_screening"]
        ready = (await client.get(detail + "/readiness")).json()
        assert (
            not ready["special"]["context_current"]
            and not ready["eipd"]["context_current"]
        )
        assert (await client.get(detail)).json() == before
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == before
        assert (await client.get(first_url)).json() == confirmed
        special_only = await client.patch(
            detail, json={"special_conditions": payload["special_conditions"]}
        )
        assert special_only.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert (
            ready["special"]["context_current"] and not ready["eipd"]["context_current"]
        )
        assert special_only.json()["eipd_screening"] == before["eipd_screening"]
        rebound = await client.patch(
            detail, json={"eipd_screening": payload["eipd_screening"]}
        )
        assert rebound.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["special"]["context_current"] and ready["eipd"]["context_current"]
        expected_fields = set(fields)
        if fields:
            expected_fields.add("special_conditions")
        assert {i["field"] for i in ready["confirmation_blockers"]} == expected_fields
        expected_codes = {"excepcion_derechos_no_preparada"}
        if (
            "sensitive_rights_exception_assessment" in rebound.json()
            and rebound.json()["sensitive_rights_exception_assessment"] is not None
        ):
            expected_codes.add("condiciones_especiales_no_preparadas")
            assert "expediente_excepcion_sensible_residual" in {
                i["code"] for i in ready["special"]["issues"]
            }
        if rebound.json()["biometric_rights_exception_assessment"] is not None:
            expected_codes.add("condiciones_especiales_no_preparadas")
            assert "expediente_excepcion_biometrica_residual" in {
                i["code"] for i in ready["special"]["issues"]
            }
        assert {i["code"] for i in ready["confirmation_blockers"]} == expected_codes
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409
        assert (
            rejected.json()["detail"]["confirmation_blockers"]
            == ready["confirmation_blockers"]
        )
        assert (await client.get(detail)).json() == rebound.json()
        assert (await client.get(first_url)).json() == confirmed
        positive = deepcopy(payload["eipd_screening"])
        next(
            a
            for a in positive["answers"]
            if a["question_id"] == "datos_protegidos_excepcion_consentimiento"
        )["answer"] = "si"
        positive_patch = await client.patch(detail, json={"eipd_screening": positive})
        assert positive_patch.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["eipd"]["context_current"]
        assert ready["eipd"]["result"] == "pendiente_revision"
        assert "excepcion_consentimiento_no_documentada" in {
            i["code"] for i in ready["eipd"]["issues"]
        }
        assert (
            next(
                a
                for a in positive_patch.json()["eipd_screening"]["answers"]
                if a["question_id"] == "datos_protegidos_excepcion_consentimiento"
            )["answer"]
            == "si"
        )
        assert "screening_eipd_no_preparado" in {
            i["code"] for i in ready["confirmation_blockers"]
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == positive_patch.json()
        assert (await client.get(first_url)).json() == confirmed


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
async def test_api_sensitive_rights_exception_six_bases(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    complete_payload,
    complete_lia_context,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
    sensitive_exception_context,
    _session_factory,
    basis,
):
    from copy import deepcopy

    from app.db.models import TreatmentDataSource

    treatment_id, payload = rat_m3
    if basis == "interes_legitimo_art13d":
        async with _session_factory() as db:
            db.add(
                TreatmentDataSource(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    source_type="titular",
                    is_public_source=False,
                )
            )
            await db.commit()
    complete_lia_context[0]["nature_and_scope"][
        "special_rules_description"
    ] = "Excepcion sensible de derechos documentada"
    ordinary_docs = {
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
    payload["legal_basis"] = basis
    if basis in ordinary_docs:
        field, document = ordinary_docs[basis]
        payload[field] = document
    else:
        payload["consent_assessment"] = complete_payload
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(url, json=payload)
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        initial = (await client.get(first_url + "/readiness")).json()
        assert initial["sensitive_rights_exception"] is None
        assert (await client.post(first_url + "/confirm")).status_code == 200
        confirmed = (await client.get(first_url)).json()
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentDataCategory)
                .where(TreatmentDataCategory.treatment_id == treatment_id)
                .values(is_sensitive=True)
            )
            await db.commit()
        exception, _, special = sensitive_exception_context
        special_input = deepcopy(special)
        special_input.pop("context_binding")
        screening = deepcopy(payload["eipd_screening"])
        next(
            a
            for a in screening["answers"]
            if a["question_id"] == "datos_protegidos_excepcion_consentimiento"
        )["answer"] = "si"
        controls = {"special_conditions": special_input, "eipd_screening": screening}
        created = await client.post(
            url,
            json={
                **payload,
                **controls,
                "sensitive_rights_exception_assessment": exception,
            },
        )
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["sensitive_rights_exception"]["result"] == "completo"
        assert ready["sensitive_rights_exception"]["issues"] == []
        assert ready["sensitive_consent"] is None
        assert (
            ready["special"]["result"] == "regimenes_preparados"
            and ready["special"]["context_current"]
        )
        assert (
            ready["eipd"]["context_current"]
            and ready["eipd"]["result"] == "pendiente_revision"
        )
        assert {b["code"] for b in ready["confirmation_blockers"]} == {
            "screening_eipd_no_preparado"
        }
        assert "excepcion_especial_no_validada" in {
            i["code"] for i in ready["eipd"]["issues"]
        }
        assert (await client.get(detail)).json() == before
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409, rejected.text
        assert (
            rejected.json()["detail"]["confirmation_blockers"]
            == ready["confirmation_blockers"]
        )
        assert (await client.get(detail)).json() == before
        assert (await client.get(first_url)).json() == confirmed
        partial = deepcopy(exception)
        partial["context"]["necessary_for_route"]["answer"] = "pendiente"
        patched = await client.patch(
            detail, json={"sensitive_rights_exception_assessment": partial}
        )
        assert patched.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["sensitive_rights_exception"]["result"] == "incompleto"
        assert (
            not ready["special"]["context_current"]
            and not ready["eipd"]["context_current"]
        )
        rebound = await client.patch(detail, json=controls)
        assert rebound.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert (
            ready["special"]["context_current"]
            and ready["special"]["result"] == "incompleto"
        )
        assert any(
            i["field"]
            == "sensitive_rights_exception_assessment.context.necessary_for_route.answer"
            and i["code"] == "respuesta_pendiente"
            for i in ready["special"]["issues"]
        )
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409
        assert rejected.json()["detail"]["special"] == ready["special"]
        assert (
            rejected.json()["detail"]["confirmation_blockers"]
            == ready["confirmation_blockers"]
        )
        assert (await client.get(detail)).json() == rebound.json()
        assert (await client.get(first_url)).json() == confirmed
        deleted = await client.patch(
            detail, json={"sensitive_rights_exception_assessment": None, **controls}
        )
        assert deleted.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["sensitive_rights_exception"]["result"] == "incompleto"
        assert any(
            i["code"] == "expediente_ausente"
            for i in ready["sensitive_rights_exception"]["issues"]
        )
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == deleted.json()
        residual = await client.patch(
            detail,
            json={
                "sensitive_rights_exception_assessment": exception,
                "sensitive_consent_assessment": {},
                **controls,
            },
        )
        assert residual.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["sensitive_rights_exception"]["result"] == "completo"
        assert any(
            i["code"] == "expediente_consentimiento_sensible_residual"
            for i in ready["special"]["issues"]
        )
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == residual.json()
        restored = await client.patch(
            detail, json={"sensitive_consent_assessment": None, **controls}
        )
        assert restored.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert {b["code"] for b in ready["confirmation_blockers"]} == {
            "screening_eipd_no_preparado"
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == restored.json()
        assert (await client.get(first_url)).json() == confirmed
        false_negative = deepcopy(screening)
        next(
            a
            for a in false_negative["answers"]
            if a["question_id"] == "datos_protegidos_excepcion_consentimiento"
        )["answer"] = "no"
        false_patch = await client.patch(
            detail, json={"eipd_screening": false_negative}
        )
        assert false_patch.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["sensitive_rights_exception"]["result"] == "completo"
        assert "excepcion_consentimiento_discordante" in {
            i["code"] for i in ready["eipd"]["issues"]
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == false_patch.json()
        mixed = deepcopy(special_input)
        mixed["conditions"][0].update(
            authorization_route="consentimiento",
            sensitive_condition_id="consentimiento_expreso_art16",
            uses_consent_assessment=True,
        )
        mixed_patch = await client.patch(
            detail, json={"special_conditions": mixed, "eipd_screening": screening}
        )
        assert mixed_patch.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["sensitive_rights_exception"]["result"] == "requiere_revision"
        assert "expediente_excepcion_sensible_residual" in {
            i["code"] for i in ready["special"]["issues"]
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == mixed_patch.json()
        restored = await client.patch(detail, json=controls)
        assert restored.status_code == 200
        assert (await client.get(first_url)).json() == confirmed
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentDataCategory)
                .where(TreatmentDataCategory.treatment_id == treatment_id)
                .values(is_sensitive=False)
            )
            await db.commit()
        changed_ready = (await client.get(detail + "/readiness")).json()
        assert not changed_ready["rat_context_current"]
        assert (
            changed_ready["sensitive_rights_exception"]["result"] == "requiere_revision"
        )
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == restored.json()
        assert (await client.get(first_url)).json() == confirmed


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
async def test_api_biometric_rights_exception_six_bases(
    client_a,
    rat_m3,
    org_a_id,
    org_b_id,
    complete_payload,
    complete_lia_context,
    complete_contract,
    complete_legal_obligation,
    complete_rights_defense,
    complete_economic_obligations,
    biometric_exception_context,
    _session_factory,
    basis,
):
    from copy import deepcopy

    from app.db.models import TreatmentDataSource

    treatment_id, payload = rat_m3
    if basis == "interes_legitimo_art13d":
        async with _session_factory() as db:
            db.add(
                TreatmentDataSource(
                    organization_id=org_a_id,
                    treatment_id=treatment_id,
                    source_type="titular",
                    is_public_source=False,
                )
            )
            await db.commit()
    complete_lia_context[0]["nature_and_scope"][
        "special_rules_description"
    ] = "Excepcion sensible de derechos documentada"
    ordinary_docs = {
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
    payload["legal_basis"] = basis
    if basis in ordinary_docs:
        field, document = ordinary_docs[basis]
        payload[field] = document
    else:
        payload["consent_assessment"] = complete_payload
    url = f"/licitud/treatments/{treatment_id}/assessments"
    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as client:
        first = await client.post(url, json=payload)
        assert first.status_code == 201, first.text
        first_url = url + "/" + first.json()["id"]
        initial = (await client.get(first_url + "/readiness")).json()
        assert initial["biometric_rights_exception"] is None
        assert (await client.post(first_url + "/confirm")).status_code == 200
        confirmed = (await client.get(first_url)).json()
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentDataCategory)
                .where(TreatmentDataCategory.treatment_id == treatment_id)
                .values(is_sensitive=True)
            )
            await db.commit()
        exception, _, special, sensitive_exception = biometric_exception_context
        special_input = deepcopy(special)
        special_input.pop("context_binding")
        screening = deepcopy(payload["eipd_screening"])
        next(
            a
            for a in screening["answers"]
            if a["question_id"] == "datos_protegidos_excepcion_consentimiento"
        )["answer"] = "si"
        controls = {"special_conditions": special_input, "eipd_screening": screening}
        created = await client.post(
            url,
            json={
                **payload,
                **controls,
                "biometric_rights_exception_assessment": exception,
                "sensitive_rights_exception_assessment": sensitive_exception,
            },
        )
        assert created.status_code == 201, created.text
        detail = url + "/" + created.json()["id"]
        before = (await client.get(detail)).json()
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["biometric_rights_exception"]["result"] == "completo"
        assert ready["biometric_rights_exception"]["issues"] == []
        assert ready["sensitive_consent"] is None
        assert ready["biometric"] is None
        assert ready["sensitive_rights_exception"]["result"] == "completo"
        assert (
            ready["special"]["result"] == "regimenes_preparados"
            and ready["special"]["context_current"]
        )
        assert (
            ready["eipd"]["context_current"]
            and ready["eipd"]["result"] == "pendiente_revision"
        )
        assert {b["code"] for b in ready["confirmation_blockers"]} == {
            "screening_eipd_no_preparado"
        }
        assert "excepcion_especial_no_validada" in {
            i["code"] for i in ready["eipd"]["issues"]
        }
        assert (await client.get(detail)).json() == before
        assert (
            await client.get(
                detail + "/readiness", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code == 403
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409, rejected.text
        assert (
            rejected.json()["detail"]["confirmation_blockers"]
            == ready["confirmation_blockers"]
        )
        assert (await client.get(detail)).json() == before
        assert (await client.get(first_url)).json() == confirmed
        partial = deepcopy(exception)
        partial["context"]["necessary_for_route"]["answer"] = "pendiente"
        patched = await client.patch(
            detail, json={"biometric_rights_exception_assessment": partial}
        )
        assert patched.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["biometric_rights_exception"]["result"] == "incompleto"
        assert (
            not ready["special"]["context_current"]
            and not ready["eipd"]["context_current"]
        )
        rebound = await client.patch(detail, json=controls)
        assert rebound.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert (
            ready["special"]["context_current"]
            and ready["special"]["result"] == "incompleto"
        )
        assert any(
            i["field"]
            == "biometric_rights_exception_assessment.context.necessary_for_route.answer"
            and i["code"] == "respuesta_pendiente"
            for i in ready["special"]["issues"]
        )
        rejected = await client.post(detail + "/confirm")
        assert rejected.status_code == 409
        assert rejected.json()["detail"]["special"] == ready["special"]
        assert (
            rejected.json()["detail"]["confirmation_blockers"]
            == ready["confirmation_blockers"]
        )
        assert (await client.get(detail)).json() == rebound.json()
        assert (await client.get(first_url)).json() == confirmed
        deleted = await client.patch(
            detail, json={"biometric_rights_exception_assessment": None, **controls}
        )
        assert deleted.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["biometric_rights_exception"]["result"] == "incompleto"
        assert any(
            i["code"] == "expediente_ausente"
            for i in ready["biometric_rights_exception"]["issues"]
        )
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == deleted.json()
        residual = await client.patch(
            detail,
            json={
                "biometric_rights_exception_assessment": exception,
                "biometric_assessment": {},
                **controls,
            },
        )
        assert residual.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["biometric_rights_exception"]["result"] == "completo"
        assert any(
            i["code"] == "expediente_biometria_residual"
            for i in ready["special"]["issues"]
        )
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == residual.json()
        restored = await client.patch(
            detail, json={"biometric_assessment": None, **controls}
        )
        assert restored.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert {b["code"] for b in ready["confirmation_blockers"]} == {
            "screening_eipd_no_preparado"
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == restored.json()
        assert (await client.get(first_url)).json() == confirmed
        for sensitive_value in (None, {}):
            dependency_patch = await client.patch(
                detail,
                json={
                    "sensitive_rights_exception_assessment": sensitive_value,
                    **controls,
                },
            )
            assert dependency_patch.status_code == 200
            ready = (await client.get(detail + "/readiness")).json()
            assert ready["biometric_rights_exception"]["result"] == "incompleto"
            assert any(
                i["field"].startswith("sensitive_rights_exception_assessment")
                for i in ready["biometric_rights_exception"]["issues"]
            )
            assert (await client.post(detail + "/confirm")).status_code == 409
            assert (await client.get(detail)).json() == dependency_patch.json()
            assert (await client.get(first_url)).json() == confirmed
        restored = await client.patch(
            detail,
            json={
                "sensitive_rights_exception_assessment": sensitive_exception,
                **controls,
            },
        )
        assert restored.status_code == 200
        for mutation in ("context", "system"):
            discordant = deepcopy(exception)
            if mutation == "context":
                discordant["context"]["context_reference"] = "Otro caso"
            else:
                second_system = deepcopy(discordant["systems"][0])
                second_system.update(
                    system_reference="Sistema 2", rights_contact_channel=" "
                )
                discordant["systems"].append(second_system)
            discordant_patch = await client.patch(
                detail,
                json={"biometric_rights_exception_assessment": discordant, **controls},
            )
            assert discordant_patch.status_code == 200
            ready = (await client.get(detail + "/readiness")).json()
            assert ready["biometric_rights_exception"]["result"] == (
                "requiere_revision" if mutation == "context" else "incompleto"
            )
            assert (await client.post(detail + "/confirm")).status_code == 409
            assert (await client.get(detail)).json() == discordant_patch.json()
            assert (await client.get(first_url)).json() == confirmed
        restored = await client.patch(
            detail,
            json={"biometric_rights_exception_assessment": exception, **controls},
        )
        assert restored.status_code == 200
        false_negative = deepcopy(screening)
        next(
            a
            for a in false_negative["answers"]
            if a["question_id"] == "datos_protegidos_excepcion_consentimiento"
        )["answer"] = "no"
        false_patch = await client.patch(
            detail, json={"eipd_screening": false_negative}
        )
        assert false_patch.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["biometric_rights_exception"]["result"] == "completo"
        assert "excepcion_consentimiento_discordante" in {
            i["code"] for i in ready["eipd"]["issues"]
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == false_patch.json()
        mixed = deepcopy(special_input)
        mixed["conditions"][-1].update(
            authorization_route="consentimiento",
            uses_consent_assessment=True,
        )
        mixed_patch = await client.patch(
            detail, json={"special_conditions": mixed, "eipd_screening": screening}
        )
        assert mixed_patch.status_code == 200
        ready = (await client.get(detail + "/readiness")).json()
        assert ready["biometric_rights_exception"]["result"] == "requiere_revision"
        assert "expediente_excepcion_biometrica_residual" in {
            i["code"] for i in ready["special"]["issues"]
        }
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == mixed_patch.json()
        restored = await client.patch(detail, json=controls)
        assert restored.status_code == 200
        assert (await client.get(first_url)).json() == confirmed
        async with _session_factory() as db:
            await db.execute(
                update(TreatmentDataCategory)
                .where(TreatmentDataCategory.treatment_id == treatment_id)
                .values(is_sensitive=False)
            )
            await db.commit()
        changed_ready = (await client.get(detail + "/readiness")).json()
        assert not changed_ready["rat_context_current"]
        assert (
            changed_ready["biometric_rights_exception"]["result"] == "requiere_revision"
        )
        assert (await client.post(detail + "/confirm")).status_code == 409
        assert (await client.get(detail)).json() == restored.json()
        assert (await client.get(first_url)).json() == confirmed
