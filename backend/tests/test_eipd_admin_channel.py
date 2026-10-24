"""Canal autenticado sobre login dedicado y pool PostgreSQL de una conexion."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db import eipd_admin as channel
from tests import test_eipd_personal_authority as personal

authority = personal.authority
pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def dedicated(_session_factory):
    role = "test_eipd_" + uuid4().hex
    password = uuid4().hex
    async with _session_factory() as db:
        await db.execute(
            text(f"CREATE ROLE {role} LOGIN NOINHERIT PASSWORD '{password}'")
        )
        await db.execute(text(f"GRANT eipd_policy_admin TO {role}"))
        await db.commit()
    url = make_url(get_settings().database_url).set(username=role, password=password)
    engine = create_async_engine(
        url,
        pool_size=1,
        max_overflow=0,
        isolation_level="READ COMMITTED",
        echo=False,
        hide_parameters=True,
    )
    try:
        yield async_sessionmaker(engine, expire_on_commit=False), role
    finally:
        await engine.dispose()
        async with _session_factory() as db:
            await db.execute(text(f"DROP ROLE {role}"))
            await db.commit()


@pytest.fixture
def credentials():
    return HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="synthetic-test-token"
    )


@pytest.mark.parametrize("missing", [True, False])
async def test_authentication_precedes_pool(monkeypatch, credentials, missing):
    def no_pool():
        pytest.fail("No debe abrir pool sin JWT valido")

    def invalid(token):
        raise HTTPException(401, "Token invalido")

    monkeypatch.setattr(channel, "get_eipd_admin_session_factory", no_pool)
    monkeypatch.setattr(channel, "extract_auth_user_id", invalid)
    stream = channel.get_eipd_admin_db(None if missing else credentials)
    with pytest.raises(HTTPException) as caught:
        await anext(stream)
    assert caught.value.status_code == 401


@pytest.mark.parametrize(
    "value", [None, "", "sqlite:///private-secret", "bad-url-secret"]
)
async def test_absent_or_bad_configuration_is_closed(monkeypatch, value):
    channel.get_eipd_admin_session_factory.cache_clear()
    monkeypatch.setattr(
        channel,
        "get_settings",
        lambda: SimpleNamespace(
            eipd_admin_database_url=SecretStr(value) if value is not None else None
        ),
    )
    with pytest.raises(HTTPException) as caught:
        channel.get_eipd_admin_session_factory()
    assert caught.value.status_code == 503
    assert "secret" not in caught.value.detail
    channel.get_eipd_admin_session_factory.cache_clear()


@pytest.mark.parametrize("finish", ["commit", "rollback"])
async def test_derived_identity_and_pool_cleanup(
    monkeypatch, dedicated, authority, credentials, finish
):
    factory, role = dedicated
    monkeypatch.setattr(channel, "get_eipd_admin_session_factory", lambda: factory)
    monkeypatch.setattr(channel, "extract_auth_user_id", lambda token: authority[1])
    stream = channel.get_eipd_admin_db(credentials)
    db = await anext(stream)
    pid = await db.scalar(text("SELECT pg_backend_pid()"))
    assert await db.scalar(text("SELECT current_user")) == "eipd_policy_admin"
    assert await db.scalar(text("SELECT session_user")) == role
    assert await db.scalar(
        text("SELECT NULLIF(current_setting('request.jwt.claim.sub',true),'')")
    ) == str(authority[1])
    assert await channel.authorize_eipd_personal_actor_v1(db) == authority[0]
    if finish == "commit":
        with pytest.raises(StopAsyncIteration):
            await anext(stream)
    else:
        with pytest.raises(RuntimeError, match="endpoint failure"):
            await stream.athrow(RuntimeError("endpoint failure"))
    async with factory() as reused:
        assert await reused.scalar(text("SELECT pg_backend_pid()")) == pid
        assert await reused.scalar(text("SELECT current_user")) == role
        assert (
            await reused.scalar(
                text("SELECT NULLIF(current_setting('request.jwt.claim.sub',true),'')")
            )
            is None
        )
        await channel._prepare_channel(reused)
        with pytest.raises(DBAPIError):
            await channel.authorize_eipd_personal_actor_v1(reused)
        await reused.rollback()


@pytest.mark.parametrize("kind", ["tenant", "unknown", "revoked"])
async def test_verified_identity_without_authority_denied(
    monkeypatch, dedicated, authority, auth_a_id, credentials, _session_factory, kind
):
    factory, _ = dedicated
    auth = auth_a_id if kind == "tenant" else uuid4()
    if kind == "revoked":
        auth = authority[1]
        async with _session_factory() as db:
            await db.execute(
                text("UPDATE profiles SET is_superadmin=false WHERE id=:id"),
                {"id": authority[0]},
            )
            await db.commit()
    monkeypatch.setattr(channel, "get_eipd_admin_session_factory", lambda: factory)
    monkeypatch.setattr(channel, "extract_auth_user_id", lambda token: auth)
    with pytest.raises(HTTPException) as caught:
        await anext(channel.get_eipd_admin_db(credentials))
    assert caught.value.status_code == 403
    async with factory() as db:
        assert (
            await db.scalar(
                text("SELECT NULLIF(current_setting('request.jwt.claim.sub',true),'')")
            )
            is None
        )


async def test_owner_connection_is_never_admin_runtime(_session_factory):
    async with _session_factory() as db:
        with pytest.raises(HTTPException) as caught:
            await channel._prepare_channel(db)
        assert caught.value.status_code == 503


async def test_tenant_connection_is_never_admin_runtime(_app_session_factory):
    async with _app_session_factory() as db:
        with pytest.raises(HTTPException) as caught:
            await channel._prepare_channel(db)
        assert caught.value.status_code == 503


async def test_configured_factory_has_separate_safe_pool(monkeypatch):
    channel.get_eipd_admin_session_factory.cache_clear()
    monkeypatch.setattr(
        channel,
        "get_settings",
        lambda: SimpleNamespace(
            eipd_admin_database_url=SecretStr(
                "postgresql+asyncpg://dedicated:synthetic@localhost/test"
            )
        ),
    )
    factory = channel.get_eipd_admin_session_factory()
    try:
        assert factory.kw["bind"].url.username == "dedicated"
        assert factory.kw["bind"].echo is False
        assert factory.kw["bind"].sync_engine.hide_parameters is True
        assert factory.kw["bind"].get_execution_options().get("isolation_level") is None
        assert (
            factory.kw["bind"].sync_engine.dialect._on_connect_isolation_level
            == "READ COMMITTED"
        )
        assert factory is channel.get_eipd_admin_session_factory()
    finally:
        await factory.kw["bind"].dispose()
        channel.get_eipd_admin_session_factory.cache_clear()


@pytest.mark.parametrize("privilege", ["CREATEDB", "BYPASSRLS", "INHERIT"])
async def test_excessive_login_privilege_is_rejected(
    dedicated, _session_factory, privilege
):
    factory, role = dedicated
    async with _session_factory() as owner:
        await owner.execute(text(f"ALTER ROLE {role} {privilege}"))
        await owner.commit()
    async with factory() as db:
        with pytest.raises(HTTPException) as caught:
            await channel._prepare_channel(db)
        assert caught.value.status_code == 503
