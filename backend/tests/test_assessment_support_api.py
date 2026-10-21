"""Actual app_user RLS, permissions, stale writes and fictitious support roundtrip."""

import base64
from uuid import uuid4

import pytest
from sqlalchemy import text, update
from sqlalchemy.exc import DBAPIError

from app.db.models import Membership, UserRole
from tests import test_eipd_child_successors as cases

rat_m3 = cases.rat_m3
saved = cases.saved
pytestmark = pytest.mark.asyncio(loop_scope="session")


def document():
    return dict(
        schema_version=1,
        document_reference="SIMULADA-EIPD-001",
        risks=[dict(risk_id="R1", description="PRUEBA discriminacion")],
        measures=[
            dict(
                measure_id="M1",
                description="PRUEBA acceso",
                risk_ids=["R1"],
                implemented=dict(answer="pendiente", rationale="PRUEBA por verificar"),
            )
        ],
    )


def annex_payload():
    return dict(
        data_kind="ficticios",
        request_id=str(uuid4()),
        reference="SIMULADA-ANEXO-001",
        filename="ensayo.txt",
        description="PRUEBA matriz",
        section="riesgos",
        risk_ids=["R1"],
        measure_ids=["M1"],
        content_base64=base64.b64encode(b"[FICTICIA] Matriz simulada").decode(),
    )


async def prepared(http, state):
    path = cases.parent(state)
    response = await http.patch(path, json={"eipd_resolution_assessment": document()})
    assert response.status_code == 200, response.text
    return path, (await http.get(path + "/support")).json()


async def test_roundtrip_versioning_stale_and_export(saved):
    async with cases.client(saved) as http:
        path, support = await prepared(http, saved)
        assert support["annexes"] == [] and support["risk_evaluation"] is None
        upload = annex_payload()
        response = await http.post(path + "/annexes", json=upload)
        assert response.status_code == 201, response.text
        annex = response.json()["annexes"][0]
        assert annex["version"] == 1 and annex["size"] == len(
            b"[FICTICIA] Matriz simulada"
        )
        downloaded = await http.get(path + f"/annexes/{annex['id']}/content")
        assert downloaded.content == b"[FICTICIA] Matriz simulada"
        assert downloaded.headers["x-content-type-options"] == "nosniff"
        assert downloaded.headers["content-type"].startswith("application/octet-stream")
        assert (
            len((await http.post(path + "/annexes", json=upload)).json()["annexes"])
            == 1
        )
        second = {**upload, "request_id": str(uuid4())}
        assert (await http.post(path + "/annexes", json=second)).json()["annexes"][-1][
            "version"
        ] == 2
        payload = dict(
            data_kind="ficticios",
            request_id=str(uuid4()),
            document_hash=support["document_hash"],
            expected_revision=0,
            analysis=dict(
                risks=[
                    dict(
                        risk_id="R1",
                        harm="PRUEBA dano",
                        inherent=dict(
                            probability=2, impact=3, rationale="PRUEBA contexto"
                        ),
                    )
                ]
            ),
        )
        result = await http.post(path + "/risk-evaluations", json=payload)
        assert result.status_code == 201, result.text
        valuation = result.json()["risk_evaluation"]
        assert (
            valuation["current"]
            and valuation["result"]["risks"][0]["inherent"] == "alto"
        )
        assert not valuation["result"]["can_confirm"]
        assert (await http.post(path + "/risk-evaluations", json=payload)).json()[
            "risk_evaluation"
        ]["revision"] == 1
        assert (
            await http.post(
                path + "/risk-evaluations", json={**payload, "request_id": str(uuid4())}
            )
        ).status_code == 409
        dossier = await http.get(path + "/mvp-dossier/v1")
        assert dossier.status_code == 200, dossier.text
        exported = dossier.json()
        assert (
            exported["support"]["risk_evaluation"]["analysis"]["risks"][0]["risk_id"]
            == "R1"
        )
        assert len(exported["support"]["annexes"]) == 2
        assert "content_base64" not in str(exported)
        changed = document()
        changed["risks"][0]["description"] = "PRUEBA contexto cambiado"
        assert (
            await http.patch(path, json={"eipd_resolution_assessment": changed})
        ).status_code == 200
        assert not (await http.get(path + "/support")).json()["risk_evaluation"][
            "current"
        ]
        assert (await http.post(path + "/confirm")).status_code == 409


async def test_cross_tenant_viewer_and_write_constraints(
    saved, org_b_id, profile_a_id, _session_factory, _app_session_factory, auth_b_id
):
    async with cases.client(saved) as http:
        path, support = await prepared(http, saved)
        upload = annex_payload()
        result = await http.post(path + "/annexes", json=upload)
        assert result.status_code == 201, result.text
        annex = result.json()["annexes"][0]
        for route in ["/support", f"/annexes/{annex['id']}/content"]:
            assert (
                await http.get(
                    path + route, headers={"X-Organization-Id": str(org_b_id)}
                )
            ).status_code in (403, 404)
        for patch in [
            {"data_kind": "reales"},
            {"filename": "x.html"},
            {"reference": "REAL-001"},
            {"risk_ids": ["R99"]},
        ]:
            response = await http.post(
                path + "/annexes", json={**upload, "request_id": str(uuid4()), **patch}
            )
            assert response.status_code in (409, 422), response.text
    async with _app_session_factory() as db:
        await db.execute(
            text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
            {"sub": str(auth_b_id)},
        )
        assert (
            await db.scalar(
                text("SELECT count(*) FROM assessment_support_records WHERE id=:id"),
                {"id": annex["id"]},
            )
            == 0
        )
        rights = (
            await db.execute(
                text(
                    "SELECT has_table_privilege(current_user,'assessment_support_records','UPDATE'),has_table_privilege(current_user,'assessment_support_records','DELETE')"
                )
            )
        ).one()
        assert tuple(rights) == (False, False)
        with pytest.raises(DBAPIError):
            async with db.begin_nested():
                await db.execute(
                    text(
                        """INSERT INTO assessment_support_records
                      (id,organization_id,treatment_id,assessment_id,created_by,request_id,kind,revision,data_kind,document_hash,payload)
                      VALUES (:id,:org,:tid,:aid,:actor,:request,'risk',99,'ficticios',:hash,'{}'::jsonb)"""
                    ),
                    dict(
                        id=uuid4(),
                        org=saved[3],
                        tid=saved[0],
                        aid=saved[1]["id"],
                        actor=profile_a_id,
                        request=uuid4(),
                        hash="f" * 64,
                    ),
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
            assert (await http.get(path + "/support")).status_code == 200
            assert (
                await http.post(path + "/annexes", json=annex_payload())
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
