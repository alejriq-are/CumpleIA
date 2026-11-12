"""Decisions on Base y fundamento through the restricted API runtime."""

from uuid import uuid4

import pytest

from app.core.deps import get_current_profile
from app.db.session import get_db
from app.services.base_fundamento_catalog import favorable_requirements
from tests import test_base_fundamento_reviews as reviews
from tests import test_eipd_version_reviews as eipd
from tests.conftest import _make_profile_override_from_db, _make_rls_db_override

rat_m3 = reviews.rat_m3
saved = reviews.saved
assessment = reviews.assessment
review_case = reviews.review_case
complete_payload = reviews.complete_payload
pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_acceptance_checks_current_content_and_keeps_the_historical_receipt(
    review_case, complete_payload, monkeypatch
):
    assessment_data, actor, auth, factory = review_case
    version = await reviews.register_version(
        review_case,
        {
            "legal_basis": "consentimiento_art12",
            "justification": "[FICTICIA] Fundamento asociado a la finalidad",
            "consent_assessment": complete_payload,
        },
    )
    root = reviews.version_cases.endpoint(assessment_data)
    url = f"{root}/{version['id']}"
    authority = await reviews.grant(review_case)
    resolutions = [
        dict(
            item,
            justification="[FICTICIA] Criterio verificado en el ensayo",
            reference=(
                "SIMULADA-5D2" if item["resolution"] == "respaldo_equivalente" else None
            ),
        )
        for item in favorable_requirements(version["bundle"])
    ]
    async with reviews.cases.client(assessment_data) as http:
        grant = await http.post(
            root + "/decision-authorities",
            json=dict(
                eipd.faculty(actor),
                compatibility_reason="[FICTICIA] Compatibilidad documentada",
            ),
        )
        assert grant.status_code == 201, grant.text

    with monkeypatch.context() as patch:
        app = assessment_data[2]
        patch.setitem(
            app.dependency_overrides,
            get_current_profile,
            _make_profile_override_from_db(auth),
        )
        patch.setitem(
            app.dependency_overrides, get_db, _make_rls_db_override(auth, factory)
        )
        async with reviews.cases.client(assessment_data) as http:
            state = await http.get(url + "/decision-state")
            assert state.status_code == 200, state.text
            assert not state.json()["can_accept"]
            review = await http.post(
                url + "/reviews",
                json=reviews.payload(
                    authority, outcome="favorable", resolutions=resolutions
                ).model_dump(mode="json"),
            )
            assert review.status_code == 201, review.text
            body = {
                "request_id": str(uuid4()),
                "data_kind": "ficticios",
                "expected_authority_id": grant.json()["id"],
                "expected_review_id": review.json()["id"],
                "expected_decision_id": None,
                "outcome": "acepta",
                "reason": "[FICTICIA] Aceptación documental",
                "reference": "SIMULADA-5D2-ACTA",
            }
            accepted = await http.post(url + "/decisions", json=body)
            assert accepted.status_code == 201, accepted.text

    async with reviews.cases.client(assessment_data) as http:
        changed = await http.patch(
            reviews.cases.parent(assessment_data),
            json={"justification": "[FICTICIA] Fundamento cambiado"},
        )
        assert changed.status_code == 200, changed.text

    with monkeypatch.context() as patch:
        patch.setitem(
            app.dependency_overrides,
            get_current_profile,
            _make_profile_override_from_db(auth),
        )
        patch.setitem(
            app.dependency_overrides, get_db, _make_rls_db_override(auth, factory)
        )
        async with reviews.cases.client(assessment_data) as http:
            replay = await http.post(url + "/decisions", json=body)
            assert replay.status_code == 201, replay.text
            assert replay.json()["id"] == accepted.json()["id"]
            state = await http.get(url + "/decision-state")
            assert not state.json()["can_accept"]
            assert "fundamento" in state.json()["acceptance_blocked_reason"]
            blocked = await http.post(
                url + "/decisions",
                json=dict(
                    body,
                    request_id=str(uuid4()),
                    expected_decision_id=accepted.json()["id"],
                ),
            )
            assert blocked.status_code == 422, blocked.text
