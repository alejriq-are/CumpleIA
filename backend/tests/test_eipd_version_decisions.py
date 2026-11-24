"""Decision API and concurrent guards on the isolated PostgreSQL runtime."""

import asyncio
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.core.deps import get_current_profile
from app.db.session import get_db
from app.schemas.eipd_document_versions import (
    EipdDecisionAuthority,
    EipdDecisionRegister,
)
from app.services import eipd_version_decisions as decisions
from tests import test_eipd_document_versions as versions
from tests import test_eipd_version_reviews as review
from tests.conftest import _make_profile_override_from_db, _make_rls_db_override
from tests.test_eipd_resolution_readiness import api_document
from tests.test_eipd_version_reviews import (  # noqa: F401
    complete_resolution,  # noqa: F811
    explicit_review_policy,
    rat_m3,
    ready,
    review_case,
    saved,
)

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture
async def decision_case(review_case, _session_factory):  # noqa: F811
    yield review_case
    async with _session_factory() as db:
        for table in ("eipd_version_decisions", "eipd_decision_authority_events"):
            await db.execute(
                text("DELETE FROM " + table + " WHERE treatment_id=:tid"),
                {"tid": review_case[0][0]},
            )
        await db.commit()


async def grant(case, **kwargs):
    state, _, actor, _, _ = case
    async with versions.cases.client(state) as http:
        response = await http.post(
            versions.endpoint(state) + "/decision-authorities",
            json=review.faculty(actor, **kwargs),
        )
        assert response.status_code == 201, response.text
        return UUID(response.json()["id"])


def payload(authority, **kwargs):
    return EipdDecisionRegister(
        **(
            dict(
                request_id=uuid4(),
                data_kind="ficticios",
                expected_authority_id=authority,
                expected_decision_id=None,
                expected_review_id=None,
                outcome="requiere_cambios",
                reason="[FICTICIA] Decisión motivada",
                reference="ACTA-SIMULADA-001",
            )
            | kwargs
        )
    )


async def record(case, body):
    _, _, actor, auth, factory = case
    async with review.runtime(factory, auth) as db:
        return await decisions.record(db, *review.args(case), actor, body)


async def test_decision_api_independent_authority_and_history(decision_case):
    case = decision_case
    state, version, actor, auth, factory = case
    await review.grant(case)
    with pytest.raises(HTTPException) as denied:
        await record(case, payload(uuid4()))
    assert denied.value.status_code == 403
    authority = await grant(case)
    with pytest.raises(HTTPException) as incomplete:
        await record(case, payload(authority, outcome="acepta"))
    assert incomplete.value.status_code == 422
    first_body = payload(authority)
    first = await record(case, first_body)
    assert (await record(case, first_body))["id"] == first["id"]
    with pytest.raises(HTTPException) as stale:
        await record(case, payload(authority, outcome="rechaza"))
    assert stale.value.status_code == 409
    second = await record(
        case, payload(authority, outcome="rechaza", expected_decision_id=first["id"])
    )
    await grant(case, sequence=1, action="revoke")
    assert (await record(case, first_body))["id"] == first["id"]
    async with versions.cases.client(state) as http:
        url = versions.endpoint(state) + "/" + version["id"]
        response = await http.get(url + "/decision-state")
        assert response.status_code == 200, response.text
        assert [d["id"] for d in response.json()["decisions"]] == [
            str(first["id"]),
            str(second["id"]),
        ]
    with pytest.raises(DBAPIError):
        async with review.runtime(factory, auth) as db:
            await db.execute(
                text("DELETE FROM eipd_version_decisions WHERE id=:id"),
                {"id": first["id"]},
            )


async def test_acceptance_requires_compatible_review_and_stable_rat(
    decision_case,
    complete_resolution,  # noqa: F811
    _session_factory,
):
    state, _, actor, auth, factory = decision_case
    async with versions.cases.client(state) as http:
        url = versions.endpoint(state)
        current = (await http.get(versions.cases.parent(state))).json()
        response = await http.patch(
            versions.cases.parent(state),
            json={
                "eipd_resolution_assessment": api_document(
                    complete_resolution[0], current
                ),
            },
        )
        assert response.status_code == 200, response.text
        preview = (await http.get(url + "/preview")).json()
        successor = await http.post(url, json=versions.registration(preview))
        assert successor.status_code == 201, successor.text
    case = (state, successor.json(), actor, auth, factory)
    reviewer = await review.grant(case)
    conclusion = await review.record(
        case, review.body(UUID(reviewer["id"]), outcome="favorable")
    )
    faculty = await grant(case)
    with pytest.raises(HTTPException) as denied:
        await record(
            case,
            payload(faculty, outcome="acepta", expected_review_id=conclusion["id"]),
        )
    assert denied.value.status_code == 403
    faculty = await grant(
        case, sequence=1, compatibility_reason="[FICTICIA] Compatibilidad documentada"
    )
    body = payload(faculty, outcome="acepta", expected_review_id=conclusion["id"])
    async with _session_factory() as writer:
        await writer.execute(
            text("UPDATE treatments SET retention_rule=:rule WHERE id=:id"),
            {"rule": "[FICTICIA] Regla material nueva", "id": state[0]},
        )
        with pytest.raises(HTTPException) as changing:
            await record(case, body)
        assert changing.value.status_code == 409
        await writer.rollback()
    accepted = await record(case, body)
    assert accepted["review_id"] == conclusion["id"]
    assert accepted["outcome"] == "acepta"
    async with _session_factory() as writer:
        await writer.execute(
            text("UPDATE treatments SET retention_rule=:rule WHERE id=:id"),
            {"rule": "[FICTICIA] Regla material posterior", "id": state[0]},
        )
        await writer.commit()
    assert (await record(case, body))["id"] == accepted["id"]
    with pytest.raises(HTTPException) as obsolete:
        await record(
            case,
            payload(
                faculty,
                outcome="acepta",
                expected_review_id=conclusion["id"],
                expected_decision_id=accepted["id"],
            ),
        )
    assert obsolete.value.status_code == 422


async def test_decision_post_receipt_and_concurrent_revocation(
    decision_case,
    auth_a_id,
    profile_a_id,
    org_b_id,
    monkeypatch,
):
    state, version, actor, auth, factory = decision_case
    authority = await grant(decision_case)
    decision = payload(authority)
    request = decision.model_dump(mode="json")
    url = versions.endpoint(state) + "/" + version["id"]
    async with versions.cases.client(state) as http:
        denied = await http.post(url + "/decisions", json=request)
        assert denied.status_code == 403
        assert (
            await http.get(
                url + "/decision-state", headers={"X-Organization-Id": str(org_b_id)}
            )
        ).status_code in (403, 404)
        with monkeypatch.context() as patch:
            patch.setitem(
                state[2].dependency_overrides,
                get_current_profile,
                _make_profile_override_from_db(auth),
            )
            patch.setitem(
                state[2].dependency_overrides,
                get_db,
                _make_rls_db_override(auth, factory),
            )
            response = await http.post(url + "/decisions", json=request)
            assert response.status_code == 201, response.text
            first = response.json()
            receipt = await http.get(
                url + "/decision-requests/" + request["request_id"]
            )
            assert receipt.json() == first
    async with review.runtime(factory, auth_a_id) as db:
        await decisions.designate(
            db,
            *review.args(decision_case)[:3],
            profile_a_id,
            EipdDecisionAuthority(**review.faculty(actor, sequence=1, action="revoke")),
        )
        task = asyncio.create_task(
            record(
                decision_case,
                payload(
                    authority,
                    expected_decision_id=UUID(first["id"]),
                    outcome="rechaza",
                ),
            )
        )
        await asyncio.sleep(0.05)
        assert not task.done()
    with pytest.raises(HTTPException) as revoked:
        await task
    assert revoked.value.status_code == 409
