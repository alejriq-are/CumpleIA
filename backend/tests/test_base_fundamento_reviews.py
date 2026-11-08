"""5D.1 review and resolution rules on the restricted PostgreSQL runtime."""

import asyncio
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import delete, text
from sqlalchemy.exc import DBAPIError

from app.core.deps import get_current_profile
from app.db.models import Membership, UserRole
from app.db.session import get_db
from app.schemas.base_fundamento_versions import (
    BaseFundamentoReviewAuthority,
    BaseFundamentoReviewRegister,
)
from app.services import base_fundamento_reviews as service
from tests import test_base_fundamento_versions as version_cases
from tests import test_eipd_child_successors as cases
from tests import test_eipd_document_versions as versions
from tests import test_eipd_version_reviews as eipd_review
from tests import test_services_consentimiento as consent_cases
from tests.conftest import _make_profile_override_from_db, _make_rls_db_override

rat_m3 = cases.rat_m3
saved = cases.saved
assessment = version_cases.assessment
complete_payload = consent_cases.complete_payload
pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture
async def review_case(
    assessment, profile_b_id, auth_b_id, _session_factory, _app_session_factory
):
    async with _session_factory() as db:
        db.add(
            Membership(
                organization_id=assessment[3],
                profile_id=profile_b_id,
                role=UserRole.admin,
            )
        )
        await db.commit()
    try:
        yield assessment, profile_b_id, auth_b_id, _app_session_factory
    finally:
        async with _session_factory() as db:
            for table in (
                "base_fundamento_reviews",
                "base_fundamento_review_authorities",
                "eipd_review_authority_events",
            ):
                await db.execute(
                    text("DELETE FROM " + table + " WHERE treatment_id=:tid"),
                    {"tid": assessment[0]},
                )
            await db.execute(
                delete(Membership).where(
                    Membership.organization_id == assessment[3],
                    Membership.profile_id == profile_b_id,
                )
            )
            await db.commit()


def scope(case):
    a, *_ = case
    return a[3], a[0], UUID(a[1]["id"])


async def register_version(case, patch):
    a, *_ = case
    url = version_cases.endpoint(a)
    async with cases.client(a) as http:
        response = await http.patch(cases.parent(a), json=patch)
        assert response.status_code == 200, response.text
        preview = await http.get(url + "/preview")
        assert preview.status_code == 200, preview.text
        response = await http.post(url, json=versions.registration(preview.json()))
        assert response.status_code == 201, response.text
        return response.json()


async def grant(case, **kwargs):
    a, actor, *_ = case
    async with cases.client(a) as http:
        response = await http.post(
            version_cases.endpoint(a) + "/review-authorities",
            json=eipd_review.faculty(actor, **kwargs),
        )
        assert response.status_code == 201, response.text
        return UUID(response.json()["id"])


def payload(authority, **kwargs):
    return BaseFundamentoReviewRegister(
        **(
            dict(
                request_id=uuid4(),
                data_kind="ficticios",
                authority_id=authority,
                expected_previous_id=None,
                outcome="requiere_cambios",
                reason="[FICTICIA] Conclusión de revisión",
                reference="SIMULADA-5D1-REVISION",
            )
            | kwargs
        )
    )


async def record(case, version, body):
    _, actor, auth, factory = case
    async with eipd_review.runtime(factory, auth) as db:
        return await service.record(db, *scope(case), UUID(version["id"]), actor, body)


async def test_favorable_equivalence_justified_nonapplicability_and_followup(
    review_case,
    complete_payload,
    monkeypatch,
):
    a, actor, auth, factory = review_case
    version = await register_version(
        review_case,
        {
            "legal_basis": "consentimiento_art12",
            "justification": "[FICTICIA] Fundamento asociado a la finalidad",
            "consent_assessment": complete_payload,
        },
    )
    authority = await grant(review_case)
    required = service.favorable_requirements(version["bundle"])
    assert [r["resolution"] for r in required].count(
        "respaldo_equivalente"
    ) == 1, required
    assert [r["resolution"] for r in required].count("no_aplica") == 2, required
    assert all(r["resolution"] for r in required), required
    with pytest.raises(HTTPException) as absent:
        await record(review_case, version, payload(authority, outcome="favorable"))
    assert absent.value.status_code == 422
    resolutions = [
        dict(
            r,
            justification="[FICTICIA] Se revisó este requisito en su contexto",
            reference=(
                "SIMULADA-BITACORA-001"
                if r["resolution"] == "respaldo_equivalente"
                else None
            ),
        )
        for r in required
    ]
    with pytest.raises(HTTPException) as duplicate:
        await record(
            review_case,
            version,
            payload(authority, resolutions=resolutions + resolutions),
        )
    assert duplicate.value.status_code == 422
    body = payload(
        authority,
        outcome="favorable",
        resolutions=resolutions,
        observations=[
            dict(
                description="[FICTICIA] Normalizar nombre de respaldo",
                responsible="Equipo ficticio",
                due_on="2026-12-01",
            )
        ],
    ).model_dump(mode="json")
    with monkeypatch.context() as patch:
        patch.setitem(
            a[2].dependency_overrides,
            get_current_profile,
            _make_profile_override_from_db(auth),
        )
        patch.setitem(
            a[2].dependency_overrides, get_db, _make_rls_db_override(auth, factory)
        )
        async with cases.client(a) as http:
            url = version_cases.endpoint(a) + "/" + version["id"]
            state = (await http.get(url + "/review-state")).json()
            assert state["favorable_requirements"] == required
            response = await http.post(url + "/reviews", json=body)
            assert response.status_code == 201, response.text
            accepted = response.json()
            assert accepted["outcome"] == "favorable"
            assert accepted["resolutions"] == resolutions
            assert accepted["observations"] == body["observations"]
            assert (
                await http.get(url + "/review-requests/" + body["request_id"])
            ).json() == accepted
            assert (await http.post(url + "/reviews", json=body)).json() == accepted
            assert (await http.get(url)).json() == version


async def test_pending_cannot_be_favorable_and_faculty_is_independent(review_case):
    a, actor, *_ = review_case
    version = await register_version(review_case, {"legal_basis": None})
    async with cases.client(a) as http:
        response = await http.post(
            versions.endpoint(a) + "/review-authorities",
            json=eipd_review.faculty(actor),
        )
        assert response.status_code == 201, response.text
    with pytest.raises(HTTPException) as independent:
        await record(review_case, version, payload(uuid4()))
    assert independent.value.status_code == 403
    authority = await grant(review_case)
    with pytest.raises(HTTPException) as favorable:
        await record(review_case, version, payload(authority, outcome="favorable"))
    assert favorable.value.status_code == 422
    first = await record(
        review_case, version, payload(authority, outcome="desfavorable")
    )
    with pytest.raises(HTTPException) as stale:
        await record(review_case, version, payload(authority))
    assert stale.value.status_code == 409
    second = await record(
        review_case, version, payload(authority, expected_previous_id=first["id"])
    )
    assert second["previous_id"] == first["id"]


async def test_author_concurrent_revocation_and_read_isolation(
    review_case,
    profile_a_id,
    auth_a_id,
    org_b_id,
):
    a, actor, auth, factory = review_case
    version = await register_version(review_case, {"legal_basis": None})
    version_id = UUID(version["id"])
    async with eipd_review.runtime(factory, auth) as db:
        granted_to_author = await service.designate(
            db,
            *scope(review_case),
            actor,
            BaseFundamentoReviewAuthority(**eipd_review.faculty(profile_a_id)),
        )
    async with cases.client(a) as http:
        url = version_cases.endpoint(a) + "/" + version["id"]
        denied = await http.post(
            url + "/reviews",
            json=payload(granted_to_author["id"]).model_dump(mode="json"),
        )
        assert denied.status_code == 403
        foreign = await http.get(
            url + "/review-state", headers={"X-Organization-Id": str(org_b_id)}
        )
        assert foreign.status_code in (403, 404)
    authority = await grant(review_case)
    first_body = payload(authority)
    first = await record(review_case, version, first_body)
    async with eipd_review.runtime(factory, auth_a_id) as db:
        await service.designate(
            db,
            *scope(review_case),
            profile_a_id,
            BaseFundamentoReviewAuthority(
                **eipd_review.faculty(actor, sequence=1, action="revoke")
            ),
        )
        task = asyncio.create_task(
            record(
                review_case,
                version,
                payload(authority, expected_previous_id=first["id"]),
            )
        )
        await asyncio.sleep(0.05)
        assert not task.done()
    with pytest.raises(HTTPException) as revoked:
        await task
    assert revoked.value.status_code == 403
    assert (await record(review_case, version, first_body))["id"] == first["id"]
    async with eipd_review.runtime(factory, auth) as db:
        assert len(await service.history(db, *scope(review_case), version_id)) == 1
    with pytest.raises(DBAPIError):
        async with eipd_review.runtime(factory, auth) as db:
            await db.execute(
                text("DELETE FROM base_fundamento_reviews WHERE id=:id"),
                {"id": first["id"]},
            )
