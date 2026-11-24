"""Recorrido ficticio con historia y restauracion local opcional, nunca datos reales."""

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.deps import get_db
from app.schemas.pilot_preparation import SIMULATION_WATERMARK
from scripts import check_pilot_restore as restore
from scripts.run_eipd_tests import build_environment, verify_destination
from tests import test_eipd_child_successors as cases
from tests import test_organization_acceptance as acts
from tests.conftest import _make_rls_db_override

base_rat_m3 = cases.rat_m3
saved = cases.saved
explicit_review_policy = cases.explicit_review_policy
prepared = cases.prepared
pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture
async def rat_m3(base_rat_m3, _session_factory):
    tid, payload = base_rat_m3
    async with _session_factory() as db:
        await db.execute(
            text("UPDATE treatments SET name=:name WHERE id=:id"),
            {"name": "[FICTICIA] Programa de fidelizacion con infancia", "id": tid},
        )
        await db.execute(
            text(
                "UPDATE treatment_purposes SET purpose=:purpose WHERE treatment_id=:id"
            ),
            {"purpose": "[FICTICIA] Programa de fidelizacion de pruebas", "id": tid},
        )
        await db.execute(
            text(
                "UPDATE treatment_data_subjects SET includes_children=true,is_vulnerable_group=true WHERE treatment_id=:id"
            ),
            {"id": tid},
        )
        await db.commit()
    return tid, payload


@pytest.fixture
async def ordinary_scenarios(prepared, negative_controls, _session_factory):
    state, _ = prepared
    created = []
    paths = []
    try:
        async with cases.client(state) as http:
            for group in ("clientes", "trabajadores"):
                response = await http.post(
                    "/rat/treatments",
                    json={
                        "name": f"[FICTICIA] Piloto {group}",
                        "organization_role": "responsable",
                        "retention_rule": "SIMULADA: plazo pendiente",
                    },
                )
                assert response.status_code == 201, response.text
                tid = response.json()["id"]
                created.append(tid)
                root = f"/rat/treatments/{tid}"
                purpose = await http.put(
                    root + "/purposes",
                    json={"items": [{"purpose": f"[FICTICIA] Gestion de {group}"}]},
                )
                assert purpose.status_code == 200, purpose.text
                pid = purpose.json()[0]["id"]
                for path, item in (
                    (
                        "data-categories",
                        {"category_code": "id", "category_name": "Identidad"},
                    ),
                    ("data-subjects", {"category_code": group, "category_name": group}),
                    (
                        "data-sources",
                        {
                            "source_type": "titular",
                            "description": "[FICTICIA] Formulario de pruebas",
                        },
                    ),
                ):
                    response = await http.put(root + "/" + path, json={"items": [item]})
                    assert response.status_code == 200, response.text
                response = await http.post(
                    f"/licitud/treatments/{tid}/assessments",
                    json={
                        **negative_controls,
                        "purpose_id": pid,
                        "scope": {
                            "data_category_codes": ["id"],
                            "data_subject_codes": [group],
                        },
                        "legal_basis": "interes_legitimo_art13d",
                        "justification": "[FICTICIA] Hipotesis para pruebas, no validacion juridica",
                        "lia_assessment": {
                            "purpose_and_interest": {
                                "legitimate_interest": "[FICTICIA] Interes declarado pendiente de revision"
                            }
                        },
                    },
                )
                assert response.status_code == 201, response.text
                parent = (
                    f"/licitud/treatments/{tid}/assessments/{response.json()['id']}"
                )
                dossier = (await http.get(parent + "/mvp-dossier/v1")).json()
                assert not dossier["mvp_ready"] and not dossier["allows_real_data"]
                assert dossier["documents"][2]["status"] != "disponible"
                paths.extend([root, parent])
        yield paths
    finally:
        async with _session_factory() as db:
            for tid in created:
                for table in ("legal_assessments", "legal_assessment_series"):
                    await db.execute(
                        text(
                            "DELETE FROM "
                            + table
                            + " WHERE treatment_id=CAST(:tid AS uuid)"
                        ),
                        {"tid": tid},
                    )
                await db.execute(
                    text("DELETE FROM treatments WHERE id=CAST(:tid AS uuid)"),
                    {"tid": tid},
                )
            await db.commit()


async def test_populated_pilot_history_restore(
    prepared,
    ordinary_scenarios,
    explicit_review_policy,
    profile_a_id,
    auth_a_id,
    auth_b_id,
    org_b_id,
    _session_factory,
):
    state, first = prepared
    async with _session_factory() as db:
        original_name = await db.scalar(
            text("SELECT name FROM organizations WHERE id=:id"), {"id": state[3]}
        )
        await db.execute(
            text("UPDATE organizations SET name=:name WHERE id=:id"),
            {"name": "[FICTICIA] Comercial Piloto Andes SpA", "id": state[3]},
        )
        await db.commit()
    try:
        async with cases.client(state) as http:
            gbody = acts.designation(profile_a_id)
            gbody.update(
                faculty_reference="SIMULADA-PILOTO-DES-001",
                evidence_reference="SIMULADA-PILOTO-FAC-001",
            )
            response = await http.post(acts.base(state) + "/authority", json=gbody)
            assert response.status_code == 201, response.text
            authority = response.json()
            rows = []
            for version in (1, 2):
                if version == 2:
                    response = await http.patch(
                        cases.parent(state),
                        json={
                            "child_adolescent_assessment": {
                                "declared_groups": ["ninos_ninas"],
                                "notes": "[FICTICIA] Programa de fidelizacion, material sucesor",
                            }
                        },
                    )
                    assert response.status_code == 200, response.text
                    response = await http.post(
                        cases.url(state) + "/resolutions",
                        json={
                            "data_kind": "ficticios",
                            "document": {
                                "notes": "[FICTICIA] Resolucion sucesora, sin valor juridico"
                            },
                        },
                    )
                    assert response.status_code == 201, response.text
                    row = response.json()
                    assert (await http.get(acts.events(state, row))).json() == []
                    assert (
                        await http.post(
                            acts.events(state, first),
                            json=acts.decision(authority["id"]),
                        )
                    ).status_code == 409
                else:
                    row = first
                rows.append(row)
                review = cases.review(
                    "requiere_cambios" if version == 1 else "no_continuar"
                )
                review["review_reference"] = f"SIMULADA-PILOTO-REV-00{version}"
                response = await http.post(
                    cases.url(state) + f"/resolutions/{row['id']}/reviews", json=review
                )
                assert response.status_code == 201, response.text
                acceptance = acts.decision(authority["id"], "requiere_cambios")
                acceptance["evidence_reference"] = f"SIMULADA-PILOTO-ACTA-00{version}"
                response = await http.post(acts.events(state, row), json=acceptance)
                assert response.status_code == 201, response.text
            dossier = (await http.get(cases.parent(state) + "/mvp-dossier/v1")).json()
            act_body = dict(
                data_kind="ficticios",
                authority_id=authority["id"],
                document_hashes={
                    d["kind"]: d["content_hash"] for d in dossier["documents"]
                },
                review_decision="pendiente",
            )
            response = await http.post(
                cases.parent(state) + "/pilot-preparation/v2", json=act_body
            )
            assert response.status_code == 200, response.text
            act = response.json()
            assert act["watermark"] == SIMULATION_WATERMARK
            assert act["legal_review_status"] == "pendiente_no_realizada"
            assert (
                not act["mvp_ready"]
                and not act["allows_real_data"]
                and not act["can_confirm"]
            )
            gbody.update(expected_revision=1, action="revocar")
            assert (
                await http.post(acts.base(state) + "/authority", json=gbody)
            ).status_code == 201
            assert (
                await http.post(
                    acts.events(state, rows[-1]), json=acts.decision(authority["id"])
                )
            ).status_code == 403
            paths = [
                cases.parent(state),
                f"/rat/treatments/{state[0]}",
                cases.url(state) + "/policy",
                cases.url(state) + "/resolutions",
                acts.base(state) + "/authority",
            ]
            for row in rows:
                paths.extend(
                    [
                        cases.url(state) + f"/resolutions/{row['id']}",
                        cases.url(state) + f"/resolutions/{row['id']}/reviews",
                        acts.events(state, row),
                    ]
                )
            dossier = (await http.get(cases.parent(state) + "/mvp-dossier/v1")).json()
            paths.extend(ordinary_scenarios)
            expected = {}
            for path in paths:
                r = await http.get(path)
                assert r.status_code == 200, r.text
                expected[path] = r.json()
            assert (
                expected[acts.events(state, first)][0]["material_status"] == "obsoleto"
            )
            assert all(
                not expected[acts.events(state, row)][0]["faculty_current"]
                for row in rows
            )
            assert (
                await http.post(cases.parent(state) + "/confirm")
            ).status_code == 409
            assert (
                await http.get(
                    acts.events(state, first),
                    headers={"X-Organization-Id": str(org_b_id)},
                )
            ).status_code in (403, 404)
        async with _session_factory() as db:
            assert [
                await db.scalar(text("SELECT count(*) FROM " + t))
                for t in restore.HISTORY_TABLES
            ] == [2, 2, 2, 2]
        if os.environ.get("CUMPLEIA_POPULATED_PILOT_RESTORE") != "1":
            return  # CI cubre API; el ensayo Docker fijo se ejecuta solo localmente.
        env = build_environment(get_settings(), os.environ)
        with pytest.raises(ValueError, match="Registro de pruebas no vacio"):
            await verify_destination(
                env
            )  # modo normal sigue rechazando registro poblado.
        fixture = {
            "organization_id": str(state[3]),
            "publication_id": str(explicit_review_policy.id),
        }
        with pytest.raises(RuntimeError):
            await restore.verify_populated_fixture(
                env, {**fixture, "publication_id": str(uuid4())}
            )
        from app.services.eipd_policy import resolve_eipd_gate_policy_v1

        foreign_policy = resolve_eipd_gate_policy_v1().model_copy(
            update={"policy_reference": "AJENA"}
        )
        with patch(
            "app.services.eipd_policy.resolve_eipd_gate_policy_v1",
            return_value=foreign_policy,
        ):
            with pytest.raises(RuntimeError):
                await restore.verify_populated_fixture(env, fixture)
        loop = asyncio.get_running_loop()

        async def verify_api(url):
            engine = create_async_engine(
                url, echo=False, hide_parameters=True, poolclass=NullPool
            )
            factory = async_sessionmaker(engine, expire_on_commit=False)
            app = state[2]
            previous = app.dependency_overrides[get_db]
            app.dependency_overrides[get_db] = _make_rls_db_override(auth_a_id, factory)
            try:
                async with cases.client(state) as http:
                    for path, value in expected.items():
                        r = await http.get(path)
                        assert r.status_code == 200, r.text
                        assert r.json() == value, path
                    restored_dossier = (
                        await http.get(cases.parent(state) + "/mvp-dossier/v1")
                    ).json()
                    assert restored_dossier["documents"] == dossier["documents"]
                    assert (
                        await http.post(cases.parent(state) + "/confirm")
                    ).status_code == 409
                    assert (
                        await http.post(
                            acts.events(state, rows[-1]),
                            json=acts.decision(authority["id"]),
                        )
                    ).status_code == 403
                    assert (
                        await http.get(
                            acts.events(state, first),
                            headers={"X-Organization-Id": str(org_b_id)},
                        )
                    ).status_code in (403, 404)
                async with factory() as db:
                    await db.execute(
                        text("SELECT set_config('request.jwt.claim.sub',:sub,true)"),
                        {"sub": str(auth_b_id)},
                    )
                    for table in restore.HISTORY_TABLES:
                        assert (
                            await db.scalar(text("SELECT count(*) FROM " + table)) == 0
                        )
            finally:
                app.dependency_overrides[get_db] = previous
                await engine.dispose()

        def callback(url):
            asyncio.run_coroutine_threadsafe(verify_api(url), loop).result(timeout=60)

        report = await asyncio.to_thread(
            restore.run,
            populated_fixture={
                "organization_id": str(state[3]),
                "publication_id": str(explicit_review_policy.id),
            },
            verify_restored=callback,
        )
        assert report["history_rows_restored"] == 8
        assert report["restored_api_verified"] and report["temporary_database_removed"]
        report["scenarios_checked"] = [
            "clientes_lia_borrador",
            "trabajadores_lia_borrador",
            "infancia_sucesores_negativos",
        ]
        target = Path(
            "../docs/project/pilot-evidence/populated-history-restore-20261016.json"
        )
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print("Piloto poblado: 8 eventos historicos, restauracion y API verificadas.")
    finally:
        async with _session_factory() as db:
            await db.execute(
                text("UPDATE organizations SET name=:name WHERE id=:id"),
                {"name": original_name, "id": state[3]},
            )
            await db.commit()
