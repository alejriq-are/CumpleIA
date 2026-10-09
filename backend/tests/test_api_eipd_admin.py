"""HTTP real + ES256 con JWKS sintetico + pool/login restringidos PostgreSQL."""

from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.db import eipd_admin as channel
from app.db.eipd_admin import get_eipd_admin_session_factory as configured_factory
from app.main import app
from app.services.eipd_policy_store import read_eipd_policy_audit_snapshot_v1
from tests import test_auth as auth
from tests import test_eipd_admin_channel as pools
from tests import test_eipd_personal_writers as writers
from tests import test_services_eipd_policy_store as fixtures

pytestmark = pytest.mark.asyncio(loop_scope="session")
signing_key = auth.signing_key
patch_jwks = auth.patch_jwks
dedicated = pools.dedicated
authority = writers.authority
cleanup = writers.cleanup
policy = fixtures.policy


@pytest_asyncio.fixture
async def api(monkeypatch, dedicated, patch_jwks):
    factory, _ = dedicated
    monkeypatch.setattr(channel, "get_eipd_admin_session_factory", lambda: factory)
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client


def headers(signing_key, user, **kwargs):
    token = auth._sign(signing_key, sub=str(user), **kwargs)
    return {"Authorization": "Bearer " + token}


def publication(policy=None):
    return dict(
        policy=policy or fixtures.disabled(),
        rationale="TEST HTTP",
        evidence_reference="TEST HTTP",
    )


def selection(pub=None, revision=0):
    return dict(
        publication_id=pub or str(uuid4()),
        expected_revision=revision,
        rationale="TEST HTTP",
        evidence_reference="TEST HTTP",
    )


async def state(factory):
    async with factory() as db:
        return await read_eipd_policy_audit_snapshot_v1(db)


async def test_http_publish_select_commits_and_server_actor(
    api, authority, signing_key, _session_factory, dedicated
):
    response = await api.post(
        "/admin/eipd/publications",
        json=publication(),
        headers=headers(signing_key, authority[1]),
    )
    assert response.status_code == 201, response.text
    pub = response.json()
    assert pub["created_by"] == str(authority[0])
    assert pub["created_at"] and pub["policy_hash"] and pub["id"]
    before = await state(_session_factory)
    assert len(before.publications) == 1 and before.selector is None
    response = await api.post(
        "/admin/eipd/selections",
        json=selection(pub["id"]),
        headers=headers(signing_key, authority[1]),
    )
    assert response.status_code == 201, response.text
    result = response.json()
    assert result["event"]["created_by"] == str(authority[0])
    after = await state(_session_factory)
    assert after.selector.publication_id == after.publications[0].id
    assert after.selector.revision == 1 and len(after.selections) == 1
    async with dedicated[0]() as db:
        assert await db.scalar(text("SELECT current_user")) == dedicated[1]
        assert not await db.scalar(
            text("SELECT current_setting('request.jwt.claim.sub',true)")
        )


@pytest.mark.parametrize("operation", ["publications", "selections"])
@pytest.mark.parametrize(
    "invalid", ["missing", "garbage", "expired", "signature", "audience", "issuer"]
)
async def test_invalid_auth_cannot_open_pool(
    monkeypatch, api, authority, signing_key, operation, invalid
):
    def forbidden_pool():
        pytest.fail("JWT invalido abrio pool administrativo")

    monkeypatch.setattr(channel, "get_eipd_admin_session_factory", forbidden_pool)
    credential = headers(signing_key, authority[1])
    if invalid == "missing":
        credential = {}
    elif invalid == "garbage":
        credential = {"Authorization": "Bearer abc.def.ghi"}
    elif invalid == "expired":
        credential = headers(signing_key, authority[1], exp_delta=timedelta(seconds=-1))
    elif invalid == "signature":
        credential = headers(
            auth.ec.generate_private_key(auth.ec.SECP256R1()), authority[1]
        )
    elif invalid == "audience":
        credential = headers(signing_key, authority[1], aud="other")
    elif invalid == "issuer":
        credential = headers(
            signing_key, authority[1], iss="https://other.example/auth/v1"
        )
    response = await api.post(
        "/admin/eipd/" + operation,
        json=publication() if operation == "publications" else selection(),
        headers=credential,
    )
    assert response.status_code == 401


@pytest.mark.parametrize("operation", ["publications", "selections"])
@pytest.mark.parametrize("identity", ["tenant", "unknown", "revoked"])
async def test_valid_jwt_without_authority_is_forbidden(
    api, authority, signing_key, auth_a_id, _session_factory, operation, identity
):
    user = auth_a_id if identity == "tenant" else uuid4()
    if identity == "revoked":
        user = authority[1]
        async with _session_factory() as db:
            await db.execute(
                text("UPDATE profiles SET is_superadmin=false WHERE id=:id"),
                dict(id=authority[0]),
            )
            await db.commit()
    before = await state(_session_factory)
    response = await api.post(
        "/admin/eipd/" + operation,
        json=publication() if operation == "publications" else selection(),
        headers={**headers(signing_key, user), "X-Organization-Id": str(uuid4())},
    )
    assert response.status_code == 403
    assert await state(_session_factory) == before


@pytest.mark.parametrize("operation", ["publications", "selections"])
@pytest.mark.parametrize(
    "field", ["actor_id", "created_by", "created_at", "policy_hash"]
)
async def test_client_audit_fields_rejected(
    api, authority, signing_key, _session_factory, operation, field
):
    body = publication() if operation == "publications" else selection()
    body[field] = str(uuid4())
    before = await state(_session_factory)
    response = await api.post(
        "/admin/eipd/" + operation,
        json=body,
        headers=headers(signing_key, authority[1]),
    )
    assert response.status_code == 422
    assert await state(_session_factory) == before


async def test_duplicate_and_stale_revision_leave_state(
    api, authority, signing_key, _session_factory
):
    credential = headers(signing_key, authority[1])
    body = publication()
    first = await api.post("/admin/eipd/publications", json=body, headers=credential)
    assert first.status_code == 201
    before = await state(_session_factory)
    repeated = await api.post("/admin/eipd/publications", json=body, headers=credential)
    assert repeated.status_code == 409
    assert await state(_session_factory) == before
    chosen = await api.post(
        "/admin/eipd/selections", json=selection(first.json()["id"]), headers=credential
    )
    assert chosen.status_code == 201
    before = await state(_session_factory)
    stale = await api.post(
        "/admin/eipd/selections", json=selection(first.json()["id"]), headers=credential
    )
    assert stale.status_code == 409
    unknown = await api.post(
        "/admin/eipd/selections", json=selection(revision=1), headers=credential
    )
    assert unknown.status_code == 409
    assert await state(_session_factory) == before


async def test_enabled_publication_remains_blocked(
    api, authority, signing_key, _session_factory, policy
):
    before = await state(_session_factory)
    response = await api.post(
        "/admin/eipd/publications",
        json=publication(policy),
        headers=headers(signing_key, authority[1]),
    )
    assert response.status_code == 409
    assert await state(_session_factory) == before


async def test_commit_failure_does_not_report_success(
    monkeypatch, api, authority, signing_key, dedicated, _session_factory
):
    original = AsyncSession.commit

    async def failing_commit(db):
        if db.bind is dedicated[0].kw["bind"]:
            raise RuntimeError("TEST commit failure")
        return await original(db)

    before = await state(_session_factory)
    with monkeypatch.context() as scoped:
        scoped.setattr(AsyncSession, "commit", failing_commit)
        response = await api.post(
            "/admin/eipd/publications",
            json=publication(),
            headers=headers(signing_key, authority[1]),
        )
    assert response.status_code == 500
    assert await state(_session_factory) == before


@pytest.mark.parametrize("operation", ["publications", "selections"])
async def test_jwks_unavailable_never_opens_pool(
    monkeypatch, api, authority, signing_key, operation
):
    def forbidden_pool():
        pytest.fail("JWKS indisponible abrio pool")

    monkeypatch.setattr(channel, "get_eipd_admin_session_factory", forbidden_pool)
    monkeypatch.setattr(security, "_get_jwks_client", lambda: auth._DownJWKSClient())
    response = await api.post(
        "/admin/eipd/" + operation,
        json=publication() if operation == "publications" else selection(),
        headers=headers(signing_key, authority[1]),
    )
    assert response.status_code == 503


@pytest.mark.parametrize("operation", ["publications", "selections"])
async def test_missing_admin_configuration_is_503(
    monkeypatch, api, authority, signing_key, operation
):
    configured_factory.cache_clear()
    monkeypatch.setattr(channel, "get_eipd_admin_session_factory", configured_factory)
    monkeypatch.setattr(
        channel, "get_settings", lambda: SimpleNamespace(eipd_admin_database_url=None)
    )
    try:
        response = await api.post(
            "/admin/eipd/" + operation,
            json=publication() if operation == "publications" else selection(),
            headers=headers(signing_key, authority[1]),
        )
        assert response.status_code == 503
    finally:
        configured_factory.cache_clear()


@pytest.mark.parametrize("operation", ["publications", "selections"])
@pytest.mark.parametrize("pool", ["owner", "tenant"])
async def test_wrong_runtime_pool_is_503(
    monkeypatch,
    api,
    authority,
    signing_key,
    operation,
    pool,
    _session_factory,
    _app_session_factory,
):
    factory = _session_factory if pool == "owner" else _app_session_factory
    monkeypatch.setattr(channel, "get_eipd_admin_session_factory", lambda: factory)
    before = await state(_session_factory)
    response = await api.post(
        "/admin/eipd/" + operation,
        json=publication() if operation == "publications" else selection(),
        headers=headers(signing_key, authority[1]),
    )
    assert response.status_code == 503
    assert await state(_session_factory) == before


async def test_authenticated_status_is_readonly(
    api, authority, signing_key, _session_factory
):
    before = await state(_session_factory)
    response = await api.get(
        "/admin/eipd/status", headers=headers(signing_key, authority[1])
    )
    assert response.status_code == 200
    assert response.json() == {
        "authenticated_admin": True,
        "selector_present": False,
        "activation_authorized": False,
    }
    assert await state(_session_factory) == before


async def test_status_requires_auth_and_global_authority(api, signing_key, auth_a_id):
    assert (await api.get("/admin/eipd/status")).status_code == 401
    assert (
        await api.get("/admin/eipd/status", headers=headers(signing_key, auth_a_id))
    ).status_code == 403


async def test_personal_audit_tracks_publication_and_selection_readonly(
    api, authority, signing_key, _session_factory
):
    credential = headers(signing_key, authority[1])
    assert (await api.get("/admin/eipd/audit")).status_code == 401
    before = await state(_session_factory)
    response = await api.get("/admin/eipd/audit", headers=credential)
    assert response.status_code == 200
    assert response.json() == before.model_dump(mode="json")
    assert await state(_session_factory) == before
    pub = await api.post(
        "/admin/eipd/publications", json=publication(), headers=credential
    )
    assert pub.status_code == 201
    selected = await api.post(
        "/admin/eipd/selections", json=selection(pub.json()["id"]), headers=credential
    )
    assert selected.status_code == 201
    after = await state(_session_factory)
    response = await api.get("/admin/eipd/audit", headers=credential)
    assert response.status_code == 200
    assert response.json() == after.model_dump(mode="json")
    assert await state(_session_factory) == after


async def test_personal_audit_rejects_tenant(api, signing_key, auth_a_id):
    response = await api.get(
        "/admin/eipd/audit", headers=headers(signing_key, auth_a_id)
    )
    assert response.status_code == 403
