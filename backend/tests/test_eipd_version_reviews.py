"""5C.1 on isolated PostgreSQL, actual runtime role and fictional records."""

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import delete, text
from sqlalchemy.exc import DBAPIError

from app.db.models import Membership, UserRole
from app.schemas.eipd_document_versions import EipdReviewAuthority, EipdReviewRegister
from app.services import eipd_version_reviews as service
from tests import test_eipd_document_versions as versions
from tests import test_services_eipd_resolution as document_cases
from tests.test_eipd_resolution_readiness import api_document

complete_resolution = document_cases.complete_resolution
rat_m3 = versions.rat_m3
ready = versions.ready
explicit_review_policy = versions.explicit_review_policy
pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture
async def saved(client_a, rat_m3, org_a_id):
    tid, payload = rat_m3
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=client_a),
        base_url="http://test",
        headers={"X-Organization-Id": str(org_a_id)},
    ) as http:
        response = await http.post(
            f"/licitud/treatments/{tid}/assessments", json=payload
        )
        assert response.status_code == 201, response.text
    return tid, response.json(), client_a, org_a_id


@asynccontextmanager
async def runtime(factory, auth):
    async with factory() as db:
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
            {"sub": str(auth)},
        )
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


@pytest.fixture
async def review_case(
    ready, profile_b_id, profile_a_id, auth_b_id, _session_factory, _app_session_factory
):
    async with _session_factory() as db:
        db.add(
            Membership(
                organization_id=ready[3], profile_id=profile_b_id, role=UserRole.admin
            )
        )
        await db.commit()
    async with versions.cases.client(ready) as http:
        url = versions.endpoint(ready)
        v = await http.post(
            url, json=versions.registration((await http.get(url + "/preview")).json())
        )
        assert v.status_code == 201, v.text
    yield ready, v.json(), profile_b_id, auth_b_id, _app_session_factory
    async with _session_factory() as db:
        for table in ("eipd_version_reviews", "eipd_review_authority_events"):
            await db.execute(
                text("DELETE FROM " + table + " WHERE treatment_id=:tid"),
                {"tid": ready[0]},
            )
        await db.execute(
            delete(Membership).where(
                Membership.organization_id == ready[3],
                Membership.profile_id == profile_b_id,
            )
        )
        await db.commit()


def args(case):
    state, v, actor, auth, factory = case
    return state[3], state[0], UUID(state[1]["id"]), UUID(v["id"])


def faculty(subject, sequence=0, action="grant", **kw):
    return dict(
        subject_id=str(subject),
        expected_sequence=sequence,
        action=action,
        reason="[FICTICIA] Facultad motivada",
        reference="SIMULADA-FACULTAD",
        **kw,
    )


def body(authority=None, previous=None, **kw):
    return EipdReviewRegister(
        **dict(
            request_id=uuid4(),
            data_kind="ficticios",
            authority_id=authority or uuid4(),
            expected_previous_id=previous,
            outcome="requiere_cambios",
            reason="[FICTICIA] Revisión motivada",
            reference="SIMULADA-REVISION",
        )
        | kw
    )


async def grant(case, **kw):
    state, _, actor, _, _ = case
    async with versions.cases.client(state) as http:
        response = await http.post(
            versions.endpoint(state) + "/review-authorities", json=faculty(actor, **kw)
        )
        assert response.status_code == 201, response.text
        return response.json()


async def record(case, payload):
    _, _, actor, auth, factory = case
    async with runtime(factory, auth) as db:
        return await service.record(db, *args(case), actor, payload)


async def test_no_implicit_faculty_self_grant_and_self_review(
    review_case, profile_a_id
):
    state, v, actor, auth, factory = review_case
    with pytest.raises(HTTPException) as error:
        await record(review_case, body())
    assert error.value.status_code == 403
    async with versions.cases.client(state) as http:
        url = versions.endpoint(state)
        denied = await http.post(
            url + "/review-authorities", json=faculty(profile_a_id)
        )
        assert denied.status_code == 403
        denied = await http.post(
            url + "/" + v["id"] + "/reviews", json=body().model_dump(mode="json")
        )
        assert denied.status_code == 403
    g = await grant(review_case)
    # B can grant A, but even with that faculty A cannot review A's version.
    async with runtime(factory, auth) as db:
        own = await service.designate(
            db,
            *args(review_case)[:3],
            actor,
            EipdReviewAuthority(**faculty(profile_a_id)),
        )
    async with versions.cases.client(state) as http:
        denied = await http.post(
            versions.endpoint(state) + "/" + v["id"] + "/reviews",
            json=body(UUID(own["id"].hex)).model_dump(mode="json"),
        )
        assert denied.status_code == 403
    assert g["subject_id"] == str(actor)


async def test_reconsideration_idempotency_history_and_successor(review_case):
    state, v, actor, auth, factory = review_case
    g = await grant(review_case)
    first_body = body(UUID(g["id"]))
    first, retry = await asyncio.gather(
        record(review_case, first_body), record(review_case, first_body)
    )
    assert first == retry
    second = await record(review_case, body(UUID(g["id"]), first["id"]))
    assert second["sequence"] == 2 and second["previous_id"] == first["id"]
    with pytest.raises(HTTPException) as error:
        await record(review_case, body(UUID(g["id"])))
    assert error.value.status_code == 409
    with pytest.raises(HTTPException) as error:
        await record(
            review_case, first_body.model_copy(update={"reason": "Otro contenido"})
        )
    assert error.value.status_code == 409
    async with runtime(factory, auth) as db:
        assert (
            await service.lookup(db, *args(review_case), actor, first_body.request_id)
            == first
        )
        assert len(await service.history(db, *args(review_case))) == 2
    async with versions.cases.client(state) as http:
        url = versions.endpoint(state)
        successor = await http.post(
            url, json=versions.registration((await http.get(url + "/preview")).json())
        )
        assert successor.status_code == 201, successor.text
        assert (
            await http.get(url + "/" + successor.json()["id"] + "/reviews")
        ).json() == []
        assert (
            await http.post(versions.cases.parent(state) + "/confirm")
        ).status_code in (400, 409)


async def test_favorable_uses_only_frozen_complete_document(
    review_case, complete_resolution
):
    state, v, actor, auth, factory = review_case
    g = await grant(review_case)
    authority = UUID(g["id"])
    await record(review_case, body(authority))
    with pytest.raises(HTTPException) as error:
        await record(review_case, body(authority, outcome="favorable"))
    assert error.value.status_code == 409  # Sequence is checked first.
    async with versions.cases.client(state) as http:
        url = versions.endpoint(state)
        first = (await http.get(url + "/" + v["id"] + "/reviews")).json()[0]
        current = (await http.get(versions.cases.parent(state))).json()
        document = api_document(complete_resolution[0], current)
        response = await http.patch(
            versions.cases.parent(state), json={"eipd_resolution_assessment": document}
        )
        assert response.status_code == 200, response.text
        preview = (await http.get(url + "/preview")).json()
        assert (
            preview["bundle"]["diagnostic"]["readiness"]["eipd_resolution"]["result"]
            == "completo"
        )
        successor = await http.post(url, json=versions.registration(preview))
        assert successor.status_code == 201, successor.text
    with pytest.raises(HTTPException) as error:
        await record(
            review_case, body(authority, UUID(first["id"]), outcome="favorable")
        )
    assert error.value.status_code == 422
    successor_case = (state, successor.json(), actor, auth, factory)
    favorable = await record(successor_case, body(authority, outcome="favorable"))
    assert favorable["outcome"] == "favorable"
    async with runtime(factory, auth) as db:
        assert len(await service.history(db, *args(review_case))) == 1


async def test_revoke_blocks_new_reviews_but_preserves_retry_and_history(review_case):
    state, v, actor, auth, factory = review_case
    g = await grant(review_case)
    request = body(UUID(g["id"]))
    first = await record(review_case, request)
    await grant(review_case, sequence=1, action="revoke")
    assert await record(review_case, request) == first
    with pytest.raises(HTTPException) as error:
        await record(review_case, body(UUID(g["id"]), first["id"]))
    assert error.value.status_code == 403
    async with runtime(factory, auth) as db:
        result = await service.state(db, *args(review_case), actor)
        assert not result["can_review"] and len(result["reviews"]) == 1


async def test_expiration_after_wait_and_concurrent_revoke(review_case):
    state, v, actor, auth, factory = review_case
    # Expired grants cannot be written.
    async with versions.cases.client(state) as http:
        response = await http.post(
            versions.endpoint(state) + "/review-authorities",
            json=faculty(
                actor, expires_at=(datetime.now(UTC) - timedelta(seconds=1)).isoformat()
            ),
        )
        assert response.status_code == 422
    g = await grant(
        review_case, expires_at=(datetime.now(UTC) + timedelta(seconds=1)).isoformat()
    )
    await asyncio.sleep(1.1)
    with pytest.raises(HTTPException) as error:
        await record(review_case, body(UUID(g["id"])))
    assert error.value.status_code == 403
    g = await grant(review_case, sequence=1)
    # Hold the same series lock while revoking, then start a waiting reviewer.
    from app.services.organization_acceptance import series_lock
    from tests.conftest import _AUTH_A_ID, _PROFILE_A_ID

    async with runtime(factory, _AUTH_A_ID) as db:
        await series_lock(db, *args(review_case)[:3])
        await service.designate(
            db,
            *args(review_case)[:3],
            _PROFILE_A_ID,
            EipdReviewAuthority(**faculty(actor, sequence=2, action="revoke")),
        )
        waiter = asyncio.create_task(record(review_case, body(UUID(g["id"]))))
        await asyncio.sleep(0.05)
        assert not waiter.done()
    with pytest.raises(HTTPException) as error:
        await waiter
    assert error.value.status_code == 403


async def test_rls_immutable_direct_writes_and_cross_tenant(
    review_case, auth_a_id, org_b_id, _session_factory
):
    state, v, actor, auth, factory = review_case
    g = await grant(review_case)
    first = await record(review_case, body(UUID(g["id"])))
    async with runtime(factory, auth_a_id) as db:
        for table in ("eipd_version_reviews", "eipd_review_authority_events"):
            for operation in (
                "UPDATE " + table + " SET reason='changed'",
                "DELETE FROM " + table,
                "TRUNCATE " + table,
            ):
                with pytest.raises(DBAPIError):
                    async with db.begin_nested():
                        await db.execute(text(operation))
        # A cannot forge B's review identity using direct runtime SQL.
        with pytest.raises(DBAPIError):
            async with db.begin_nested():
                await db.execute(
                    text(
                        """INSERT INTO eipd_version_reviews
                    (id,organization_id,treatment_id,assessment_id,version_id,created_by,
                     sequence,previous_id,request_id,outcome,reason,reference,authority_id,input_hash)
                    VALUES (:id,:org,:tid,:aid,:vid,:actor,2,:previous,:request,
                    'requiere_cambios','SIMULADA','SIMULADA',:authority,:hash)"""
                    ),
                    dict(
                        id=uuid4(),
                        org=state[3],
                        tid=state[0],
                        aid=UUID(state[1]["id"]),
                        vid=UUID(v["id"]),
                        actor=actor,
                        previous=first["id"],
                        request=uuid4(),
                        authority=UUID(g["id"]),
                        hash="a" * 64,
                    ),
                )
    async with _session_factory() as db:
        await db.execute(
            delete(Membership).where(
                Membership.organization_id == state[3], Membership.profile_id == actor
            )
        )
        await db.commit()
    async with runtime(factory, auth) as db:
        for table in ("eipd_version_reviews", "eipd_review_authority_events"):
            assert (
                await db.scalar(
                    text(
                        "SELECT count(*) FROM " + table + " WHERE organization_id=:org"
                    ),
                    {"org": state[3]},
                )
                == 0
            )
        with pytest.raises(HTTPException):
            await service.history(db, *args(review_case))
    async with versions.cases.client(state) as http:
        assert (
            await http.get(
                versions.endpoint(state) + "/" + v["id"] + "/reviews",
                headers={"X-Organization-Id": str(org_b_id)},
            )
        ).status_code in (403, 404)


async def test_reviewer_api_and_schema_permissions(review_case, org_b_id, profile_a_id):
    state, v, actor, auth, factory = review_case
    async with versions.cases.client(state) as http:
        url = versions.endpoint(state)
        denied = await http.post(url + "/review-authorities", json=faculty(uuid4()))
        assert denied.status_code == 403
        for patch in (
            {"reason": " "},
            {"reference": " "},
            {"data_kind": "reales"},
            {"outcome": "acepta"},
            {"created_by": str(actor)},
        ):
            response = await http.post(
                url + "/" + v["id"] + "/reviews",
                json=body().model_dump(mode="json") | patch,
            )
            assert response.status_code == 422
    g = await grant(review_case)
    # Exercise the full authenticated reviewer API using the same runtime fixtures.
    from app.core.deps import get_current_profile
    from app.db.session import get_db
    from tests.conftest import _make_profile_override_from_db, _make_rls_db_override

    old_profile = state[2].dependency_overrides[get_current_profile]
    old_db = state[2].dependency_overrides[get_db]
    state[2].dependency_overrides[get_current_profile] = _make_profile_override_from_db(
        auth
    )
    state[2].dependency_overrides[get_db] = _make_rls_db_override(auth, factory)
    try:
        async with versions.cases.client(state) as http:
            url = versions.endpoint(state) + "/" + v["id"]
            request = body(UUID(g["id"])).model_dump(mode="json")
            response = await http.post(url + "/reviews", json=request)
            assert response.status_code == 201, response.text
            first = response.json()
            assert (
                await http.get(url + "/review-requests/" + request["request_id"])
            ).json() == first
            assert (await http.get(url + "/reviews")).json() == [first]
            assert (await http.get(url + "/review-state")).json()["can_review"]
            assert (await http.post(url + "/reviews", json=request)).json() == first
    finally:
        state[2].dependency_overrides[get_current_profile] = old_profile
        state[2].dependency_overrides[get_db] = old_db


async def test_concurrent_reconsiderations_only_one_is_appended(review_case):
    g = await grant(review_case)
    first = await record(review_case, body(UUID(g["id"])))
    results = await asyncio.gather(
        record(review_case, body(UUID(g["id"]), first["id"])),
        record(review_case, body(UUID(g["id"]), first["id"])),
        return_exceptions=True,
    )
    assert len([r for r in results if isinstance(r, dict)]) == 1
    errors = [r for r in results if isinstance(r, HTTPException)]
    assert len(errors) == 1 and errors[0].status_code == 409
