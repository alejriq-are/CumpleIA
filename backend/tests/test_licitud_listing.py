"""Listado paginado real con control de tenant y rol; no confirma expedientes."""

from uuid import uuid4

import pytest

from tests import test_eipd_child_successors as cases

rat_m3 = cases.rat_m3
saved = cases.saved
pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_index_and_pagination(saved):
    async with cases.client(saved) as http:
        path = f"/licitud/treatments/{saved[0]}/assessments"
        r = await http.get(path)
        assert r.status_code == 200, r.text
        row = r.json()[0]
        assert row["id"] == saved[1]["id"] and row["organization_id"] == str(saved[3])
        assert "rat_context_snapshot" not in row and "lia_assessment" not in row
        assert (await http.get(path + "?offset=1&limit=1")).json() == []
        for query in ("?offset=-1", "?limit=0", "?limit=101"):
            assert (await http.get(path + query)).status_code == 422


async def test_foreign_tenant_and_treatment_denied(saved, org_b_id):
    async with cases.client(saved) as http:
        path = f"/licitud/treatments/{saved[0]}/assessments"
        assert (
            await http.get(path, headers={"X-Organization-Id": str(org_b_id)})
        ).status_code in (403, 404)
        assert (
            await http.get(f"/licitud/treatments/{uuid4()}/assessments")
        ).status_code == 404


async def test_viewer_can_list_but_cannot_create(
    saved, rat_m3, profile_a_id, _session_factory
):
    from sqlalchemy import update

    from app.db.models import Membership, UserRole

    async with _session_factory() as db:
        await db.execute(
            update(Membership)
            .where(
                Membership.profile_id == profile_a_id,
                Membership.organization_id == saved[3],
            )
            .values(role=UserRole.viewer)
        )
        await db.commit()
    try:
        async with cases.client(saved) as http:
            path = f"/licitud/treatments/{saved[0]}/assessments"
            assert (await http.get(path)).status_code == 200
            assert (await http.post(path, json=rat_m3[1])).status_code == 403
    finally:
        async with _session_factory() as db:
            await db.execute(
                update(Membership)
                .where(
                    Membership.profile_id == profile_a_id,
                    Membership.organization_id == saved[3],
                )
                .values(role=UserRole.owner)
            )
            await db.commit()
