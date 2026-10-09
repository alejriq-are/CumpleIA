"""Preflight readonly real: ningun bootstrap ni autorizacion personal."""

import pytest
from fastapi import HTTPException
from sqlalchemy import text

from scripts.eipd_admin_preflight import inspect_channel
from tests import test_api_eipd_admin as http
from tests import test_eipd_personal_authority as personal
from tests import test_services_eipd_policy_store as store

pytestmark = pytest.mark.asyncio(loop_scope="session")
dedicated = http.dedicated
authority = http.authority
cleanup = http.cleanup


async def test_missing_selector_is_pending_without_bootstrap(
    dedicated, _session_factory
):
    before = await http.state(_session_factory)
    report = await inspect_channel(dedicated[0])
    assert report["status"] == "pending_selector"
    assert report["audit_coherent"] is True
    assert report["activation_authorized"] is False
    assert report["personal_authentication_verified"] is False
    assert await http.state(_session_factory) == before
    async with dedicated[0]() as db:
        assert await db.scalar(text("SELECT current_user")) == dedicated[1]
        assert not await db.scalar(
            text("SELECT current_setting('request.jwt.claim.sub',true)")
        )


async def test_selected_disabled_policy_report_and_no_changes(
    dedicated, authority, _session_factory
):
    async with _session_factory() as db:
        await personal.admin(db, authority[1])
        pub = await store.publish(db, authority[0])
        await store.choose(db, authority[0], pub, 0)
        await db.commit()
    before = await http.state(_session_factory)
    report = await inspect_channel(dedicated[0])
    assert report["status"] == "ok"
    assert report["selector_revision"] == 1
    assert report["activation_authorized"] is False
    assert await http.state(_session_factory) == before


@pytest.mark.parametrize("pool", ["owner", "tenant"])
async def test_wrong_channel_rejected(pool, _session_factory, _app_session_factory):
    factory = _session_factory if pool == "owner" else _app_session_factory
    with pytest.raises(HTTPException):
        await inspect_channel(factory)


async def test_database_blocks_accidental_write(
    monkeypatch, dedicated, _session_factory
):
    from sqlalchemy.exc import DBAPIError

    from scripts import eipd_admin_preflight as preflight

    before = await http.state(_session_factory)

    async def accidental_write(db):
        await db.execute(text("DELETE FROM public.eipd_policy_selector"))

    monkeypatch.setattr(
        preflight, "read_eipd_policy_audit_snapshot_v1", accidental_write
    )
    with pytest.raises(DBAPIError) as caught:
        await inspect_channel(dedicated[0])
    assert caught.value.orig.sqlstate == "25006"
    assert await http.state(_session_factory) == before


async def test_cli_failure_never_prints_exception_secret(monkeypatch, capsys):
    from scripts import eipd_admin_preflight as preflight

    def unavailable():
        raise ValueError("synthetic-sensitive-url")

    monkeypatch.setattr(preflight, "get_eipd_admin_session_factory", unavailable)
    assert await preflight.main() == 1
    output = capsys.readouterr().out
    assert "synthetic-sensitive-url" not in output
    assert '"status": "failed"' in output
