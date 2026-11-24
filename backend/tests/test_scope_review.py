"""Real PostgreSQL/API: scope adoption, stale decisions and immutable evidence."""

import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import text, update
from sqlalchemy.exc import DBAPIError

from app.db.models import Membership, UserRole
from tests import test_assessment_support_api as support_cases
from tests import test_eipd_child_successors as cases
from tests.test_navigation_applicability import payload as determination

rat_m3 = cases.rat_m3
saved = cases.saved
prepared = cases.prepared
explicit_review_policy = cases.explicit_review_policy
pytestmark = pytest.mark.asyncio(loop_scope="session")


async def proposal(http, saved):
    base = cases.parent(saved)
    before = (await http.get(base)).json()
    snapshot = before["rat_context_snapshot"]
    scope = dict(
        data_category_codes=[v["category_code"] for v in snapshot["data_categories"]],
        data_subject_codes=[v["category_code"] for v in snapshot["data_subjects"]],
    )
    subjects = [
        dict(
            category_code=v["category_code"],
            category_name=v["category_name"],
            includes_children=v["includes_children"],
            includes_adolescents=v["includes_adolescents"],
            is_vulnerable_group=v["is_vulnerable_group"],
            notes=v.get("notes"),
        )
        for v in snapshot["data_subjects"]
    ]
    subjects.append(
        dict(
            category_code="otro_adultos_hijos",
            category_name="PRUEBA clientes adultos e hijos",
            includes_children=True,
            includes_adolescents=True,
            is_vulnerable_group=True,
            notes="PRUEBA adultos y participantes sintéticos de 10 a 17 años",
        )
    )
    r = await http.put(
        f"/rat/treatments/{saved[0]}/data-subjects", json={"items": subjects}
    )
    assert r.status_code == 200, r.text
    scope["data_subject_codes"].append("otro_adultos_hijos")
    response = await http.post(base + "/scope-review/preview", json={"scope": scope})
    assert response.status_code == 200, response.text
    review = response.json()
    body = dict(
        scope=scope,
        review_hash=review["review_hash"],
        request_id=str(uuid4()),
        data_kind="ficticios",
        reason="PRUEBA incorporar adultos e hijos al alcance",
    )
    return before, review, body


async def test_scope_history_independent_decisions_and_preservation(saved):
    async with cases.client(saved) as http:
        base = cases.parent(saved)
        initial = (await http.get(base + "/applicability")).json()
        d = await http.post(base + "/applicability", json=determination(initial))
        assert d.status_code == 201
        original_decision = d.json()
        before, review, body = await proposal(http, saved)
        assert review["changed"] and review["before"] == before["rat_context_snapshot"]
        assert (await http.get(base)).json() == before  # preview never writes
        result = await http.post(base + "/scope-review", json=body)
        assert result.status_code == 200, result.text
        after = result.json()
        assert after["id"] == before["id"] and after["version"] == before["version"]
        for field in [
            "child_adolescent_assessment",
            "eipd_resolution_assessment",
            "justification",
            "lia_assessment",
        ]:
            assert after[field] == before[field]
        assert after["rat_context_snapshot"] == review["after"]
        changed = (await http.get(base + "/applicability")).json()
        assert (
            not changed["current"]
            and changed["history"] == original_decision["history"]
        )
        assert changed["eipd"] == original_decision["eipd"]
        assert (await http.post(base + "/scope-review", json=body)).json() == after
        history = (
            await http.post(
                base + "/scope-review/preview", json={"scope": body["scope"]}
            )
        ).json()
        assert len(history["history"]) == 1 and not history["changed"]
        event = history["history"][0]
        assert event["before"] == review["before"] and event["after"] == review["after"]
        assert (
            event["created_by"]
            and event["created_at"]
            and event["reason"] == body["reason"]
        )
        r = await http.post(
            base + "/applicability",
            json={
                **determination(changed),
                "infancia": dict(
                    state="corresponde", reason="PRUEBA alcance mixto revisado"
                ),
            },
        )
        assert r.status_code == 201 and r.json()["current"]
        assert (
            r.json()["eipd"]["state"] == r.json()["infancia"]["state"] == "corresponde"
        )
        assert not r.json()["can_confirm"] and r.json()["activation"] == "deshabilitada"


async def test_stale_proposal_and_closed_schema(saved):
    async with cases.client(saved) as http:
        base = cases.parent(saved)
        before, review, body = await proposal(http, saved)
        for patch in [{"data_kind": "reales"}, {"reason": " "}, {"can_confirm": True}]:
            assert (
                await http.post(base + "/scope-review", json={**body, **patch})
            ).status_code == 422
        assert (
            await http.post(
                base + "/scope-review", json={**body, "review_hash": "f" * 64}
            )
        ).status_code == 409
        detail = (await http.get(f"/rat/treatments/{saved[0]}")).json()
        items = [
            {
                k: v[k]
                for k in (
                    "category_code",
                    "category_name",
                    "includes_children",
                    "includes_adolescents",
                    "is_vulnerable_group",
                    "notes",
                )
            }
            for v in detail["data_subjects"]
        ]
        items[-1]["notes"] = "PRUEBA cambio posterior a la comparación"
        r = await http.put(
            f"/rat/treatments/{saved[0]}/data-subjects", json={"items": items}
        )
        assert r.status_code == 200
        assert (await http.post(base + "/scope-review", json=body)).status_code == 409


async def test_scope_tenant_viewer_and_append_only(
    saved,
    org_b_id,
    profile_a_id,
    auth_a_id,
    auth_b_id,
    _session_factory,
    _app_session_factory,
):
    async with cases.client(saved) as http:
        base = cases.parent(saved)
        _, _, body = await proposal(http, saved)
        for suffix, data in [
            ("/scope-review/preview", {"scope": body["scope"]}),
            ("/scope-review", body),
        ]:
            assert (
                await http.post(
                    base + suffix,
                    json=data,
                    headers={"X-Organization-Id": str(org_b_id)},
                )
            ).status_code in (403, 404)
        assert (
            await http.post(
                base.replace(saved[1]["id"], str(uuid4())) + "/scope-review", json=body
            )
        ).status_code == 404
        assert (await http.post(base + "/scope-review", json=body)).status_code == 200
    async with _app_session_factory() as db:
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
            {"sub": str(auth_b_id)},
        )
        assert (
            await db.scalar(
                text(
                    "SELECT count(*) FROM assessment_support_records WHERE assessment_id=:id AND kind='scope'"
                ),
                {"id": saved[1]["id"]},
            )
            == 0
        )
        await db.rollback()
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
            {"sub": str(auth_a_id)},
        )
        with pytest.raises(DBAPIError):
            async with db.begin_nested():
                await db.execute(
                    text(
                        "UPDATE assessment_support_records SET payload='{}' WHERE kind='scope'"
                    )
                )
    async with _session_factory() as db:
        await db.execute(
            update(Membership)
            .where(
                Membership.organization_id == saved[3],
                Membership.profile_id == profile_a_id,
            )
            .values(role=UserRole.viewer)
        )
        await db.commit()
    try:
        async with cases.client(saved) as http:
            assert (
                await http.post(
                    base + "/scope-review/preview", json={"scope": body["scope"]}
                )
            ).status_code == 200
            assert (
                await http.post(base + "/scope-review", json=body)
            ).status_code == 403
    finally:
        async with _session_factory() as db:
            await db.execute(
                update(Membership)
                .where(
                    Membership.organization_id == saved[3],
                    Membership.profile_id == profile_a_id,
                )
                .values(role=UserRole.owner)
            )
            await db.commit()


async def test_same_review_cannot_apply_twice_concurrently(saved):
    async with cases.client(saved) as http:
        _, _, body = await proposal(http, saved)
        results = await asyncio.gather(
            http.post(cases.parent(saved) + "/scope-review", json=body),
            http.post(
                cases.parent(saved) + "/scope-review",
                json={**body, "request_id": str(uuid4())},
            ),
        )
        assert sorted(r.status_code for r in results) == [200, 409]
        history = (
            await http.post(
                cases.parent(saved) + "/scope-review/preview",
                json={"scope": body["scope"]},
            )
        ).json()["history"]
        assert len(history) == 1


async def test_registered_document_and_review_remain_unchanged(prepared):
    state, resolution = prepared
    async with cases.client(state) as http:
        original_path = cases.url(state) + f"/resolutions/{resolution['id']}"
        event = await http.post(original_path + "/reviews", json=cases.review())
        assert event.status_code == 201
        _, _, body = await proposal(http, state)
        assert (
            await http.post(cases.parent(state) + "/scope-review", json=body)
        ).status_code == 200
        assert (await http.get(original_path)).json() == resolution
        assert (await http.get(original_path + "/reviews")).json() == [event.json()]


async def test_adults_become_mixed_without_changing_purpose(saved):
    async with cases.client(saved) as http:
        base = cases.parent(saved)
        snapshot = (await http.get(base)).json()["rat_context_snapshot"]
        items = [
            dict(
                category_code=v["category_code"],
                category_name="PRUEBA clientes adultos",
                includes_children=False,
                includes_adolescents=False,
                is_vulnerable_group=False,
                notes="PRUEBA solo adultos",
            )
            for v in snapshot["data_subjects"]
        ]
        assert (
            await http.put(
                f"/rat/treatments/{saved[0]}/data-subjects", json={"items": items}
            )
        ).status_code == 200
        # Explicit existing API refresh establishes an adults-only stored scope for this test.
        assert (
            await http.patch(
                base,
                json={
                    "scope": {
                        "data_category_codes": [
                            v["category_code"] for v in snapshot["data_categories"]
                        ],
                        "data_subject_codes": [v["category_code"] for v in items],
                    }
                },
            )
        ).status_code == 200
        before, review, body = await proposal(http, saved)
        assert not any(
            v["includes_children"] or v["includes_adolescents"]
            for v in review["before"]["data_subjects"]
        )
        after = (await http.post(base + "/scope-review", json=body)).json()
        assert (
            after["id"] == before["id"]
            and after["purpose_snapshot"] == before["purpose_snapshot"]
        )
        assert any(
            v["includes_children"] and v["includes_adolescents"]
            for v in after["rat_context_snapshot"]["data_subjects"]
        )


async def test_scope_adoption_preserves_annex_metadata_and_bytes(saved):
    async with cases.client(saved) as http:
        base, _ = await support_cases.prepared(http, saved)
        upload = await http.post(base + "/annexes", json=support_cases.annex_payload())
        assert upload.status_code == 201, upload.text
        annexes = upload.json()["annexes"]
        content_path = base + f"/annexes/{annexes[0]['id']}/content"
        content = (await http.get(content_path)).content
        _, _, body = await proposal(http, saved)
        result = await http.post(base + "/scope-review", json=body)
        assert result.status_code == 200, result.text
        assert (await http.get(base + "/support")).json()["annexes"] == annexes
        assert (await http.get(content_path)).content == content
