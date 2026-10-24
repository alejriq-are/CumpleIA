"""Selector explicito solo en pruebas HTTP; nunca bootstrap de produccion."""

import pytest_asyncio
from sqlalchemy import text

from app.services.eipd_policy import resolve_eipd_gate_policy_v1
from app.services.eipd_policy_store import (
    _publish_eipd_policy_v1 as publish_eipd_policy_v1,
)
from app.services.eipd_policy_store import (
    _select_eipd_policy_v1 as select_eipd_policy_v1,
)


@pytest_asyncio.fixture(autouse=True)
async def explicit_review_policy(_session_factory, _seed_test_data, profile_a_id):
    async with _session_factory() as db:
        await db.execute(text("SET LOCAL ROLE eipd_policy_admin"))
        publication = await publish_eipd_policy_v1(
            db,
            resolve_eipd_gate_policy_v1(),
            actor_id=profile_a_id,
            rationale="TEST: selector explicito HTTP",
            evidence_reference="TEST: politica deshabilitada",
        )
        await select_eipd_policy_v1(
            db,
            dict(publication_id=publication.id, expected_revision=0),
            actor_id=profile_a_id,
            rationale="TEST: seleccion HTTP",
            evidence_reference="TEST",
        )
        await db.commit()
    yield publication
    async with _session_factory() as db:
        await db.execute(
            text("DELETE FROM eipd_policy_selector WHERE publication_id=:id"),
            dict(id=publication.id),
        )
        await db.execute(
            text("DELETE FROM eipd_policy_selections WHERE publication_id=:id"),
            dict(id=publication.id),
        )
        await db.execute(
            text("DELETE FROM eipd_policy_publications WHERE id=:id"),
            dict(id=publication.id),
        )
        await db.commit()
