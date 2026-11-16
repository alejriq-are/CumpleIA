"""Composicion V5 con datos ficticios y contexto servidor; sin autoridad positiva."""

from copy import deepcopy

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy import update

from app.db.models import TreatmentPurpose
from app.schemas.eipd_child import EipdChildCompositionV5Out
from tests import test_api_child_adolescent as cases

rat_m3 = cases.rat_m3
saved = cases.saved
pytestmark = pytest.mark.asyncio(loop_scope="session")


def client(state):
    return AsyncClient(
        transport=ASGITransport(app=state[2]),
        base_url="http://test",
        headers={"X-Organization-Id": str(state[3])},
    )


def path(state):
    return f"/licitud/treatments/{state[0]}/assessments/{state[1]['id']}"


async def test_v5_covers_child_without_promoting_old_resolution_or_mutating_row(saved):
    async with client(saved) as http:
        before = (await http.get(path(saved))).json()
        response = await http.get(path(saved) + "/readiness")
        assert response.status_code == 200, response.text
        body = response.json()
        v = body["eipd_controls_v5"]
        assert v["evaluation_version"] == 5 and v["context_schema_version"] == 4
        assert v["child_adolescent_coverage"] == "contexto_v4"
        assert v["resolution_child_coverage"] == "no_cubierta"
        assert not v["can_confirm"] and not v["authorizes_action"]
        for name in ("continuar", "requiere_cambios", "no_continuar"):
            assert v[name]["prerequisites_met"] is False
            assert v[name]["context_metadata"] is None
            assert any(
                i["code"] == "politica_infancia_no_implementada"
                for i in v[name]["issues"]
            )
        assert all(
            body[k] is None
            for k in (
                "eipd_controls",
                "eipd_controls_v2",
                "eipd_controls_v3",
                "eipd_controls_v4",
            )
        )
        assert (await http.get(path(saved))).json() == before


@pytest.mark.parametrize("change", ["child", "consent", "representation", "research"])
async def test_current_composition_identity_tracks_all_new_material(saved, change):
    async with client(saved) as http:
        first = (await http.get(path(saved) + "/readiness")).json()["eipd_controls_v5"]
        payload = {
            "child": {
                "child_adolescent_assessment": {
                    **cases.DOCUMENT,
                    "notes": "PRUEBA: cambio de documento",
                }
            },
            "consent": {
                "consent_assessment": {
                    "given_by": "mandatario",
                    "notes": "PRUEBA: consentimiento",
                }
            },
            "representation": {
                "sensitive_representation_assessment": {
                    "representation_kind": "mandatario",
                    "authority_document_reference": "PRUEBA: referencia",
                }
            },
            "research": {"research_assessment": {}},
        }[change]
        response = await http.patch(path(saved), json=payload)
        assert response.status_code == 200, response.text
        ready = await http.get(path(saved) + "/readiness")
        assert ready.status_code == 200, ready.text
        assert ready.json()["eipd_controls_v5"]["context_hash"] != first["context_hash"]
        assert (await http.post(path(saved) + "/confirm")).status_code == 409


async def test_context_unavailable_never_reuses_stored_hash(saved, _session_factory):
    async with _session_factory() as db:
        await db.execute(
            update(TreatmentPurpose)
            .where(TreatmentPurpose.treatment_id == saved[0])
            .values(purpose="PRUEBA: finalidad nueva")
        )
        await db.commit()
    async with client(saved) as http:
        response = await http.get(path(saved) + "/readiness")
        assert response.status_code == 200, response.text
        v = response.json()["eipd_controls_v5"]
        assert v["child_adolescent_coverage"] == "contexto_actual_no_disponible"
        assert v["context_hash"] is None


@pytest.mark.parametrize(
    "change",
    [
        "authority",
        "positive_decision",
        "metadata",
        "missing_gate",
        "missing_hash",
        "fake_coverage",
        "extra_issue",
    ],
)
async def test_output_rejects_incoherent_identity_and_authority(saved, change):
    async with client(saved) as http:
        raw = deepcopy(
            (await http.get(path(saved) + "/readiness")).json()["eipd_controls_v5"]
        )
    if change == "authority":
        raw["authorizes_action"] = True
    elif change == "positive_decision":
        raw["continuar"]["prerequisites_met"] = True
    elif change == "metadata":
        raw["no_continuar"]["context_metadata"] = {"context_hash": "a" * 64}
    elif change == "missing_gate":
        raw["requiere_cambios"]["issues"] = []
    elif change == "missing_hash":
        raw["context_hash"] = None
    elif change == "extra_issue":
        raw["continuar"]["issues"][0]["authorizes_action"] = True
    else:
        raw["resolution_child_coverage"] = "contexto_v4"
    with pytest.raises(ValidationError):
        EipdChildCompositionV5Out.model_validate(raw)


async def test_legacy_resolution_can_be_read_without_claiming_child_coverage(saved):
    async with client(saved) as http:
        response = await http.patch(
            path(saved), json={"eipd_resolution_assessment": {}}
        )
        assert response.status_code == 200, response.text
        persisted = response.json()
        assert (
            persisted["eipd_resolution_assessment"]["context_binding"][
                "binding_version"
            ]
            == 1
        )
        ready = await http.get(path(saved) + "/readiness")
        assert ready.status_code == 200, ready.text
        assert (
            ready.json()["eipd_controls_v5"]["resolution_child_coverage"]
            == "no_cubierta"
        )
        assert ready.json()["eipd_controls_v3"] is None
        assert (await http.get(path(saved))).json() == persisted
