"""Chromium -> cliente real -> HTTP/API -> PostgreSQL aislado, solo opt-in local."""

import asyncio
import os
import socket
from pathlib import Path

import pytest
import uvicorn
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from scripts.run_eipd_tests import EXPECTED_HEAD, TEST_DATABASE
from tests import test_api_eipd_negative_review_v3 as cases

explicit_review_policy = cases.explicit_review_policy
rat_m3 = cases.rat_m3
saved = cases.saved
prepared = cases.prepared
pytestmark = [
    pytest.mark.asyncio(loop_scope="session"),
    pytest.mark.skipif(
        os.getenv("CUMPLEIA_UI_INTEGRATION") != "1",
        reason="Integracion Chromium local explicita",
    ),
]


async def test_real_client_form_records_isolated_negative_event(
    prepared, _session_factory, profile_a_id
):
    async with _session_factory() as db:
        assert await db.scalar(text("SELECT current_database()")) == TEST_DATABASE
        assert (
            await db.scalar(text("SELECT version_num FROM alembic_version"))
            == EXPECTED_HEAD
        )
    app = prepared[2]
    app.add_api_route(
        "/__eipd-isolated-test",
        lambda: HTMLResponse('<div id="root"></div>'),
        methods=["GET"],
        include_in_schema=False,
    )
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    port = listener.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(app, log_level="error", lifespan="off", ws="none")
    )
    server.install_signal_handlers = lambda: None
    task = asyncio.create_task(server.serve(sockets=[listener]))
    process = None
    try:
        for _ in range(100):
            if server.started:
                break
            if task.done():
                await task
            await asyncio.sleep(0.05)
        assert server.started
        env = dict(os.environ)
        env.update(
            CUMPLEIA_UI_API=f"http://127.0.0.1:{port}",
            CUMPLEIA_UI_ORG=str(prepared[3]),
            CUMPLEIA_UI_TREATMENT=str(prepared[0]),
            CUMPLEIA_UI_ASSESSMENT=prepared[1]["id"],
        )
        frontend = Path(__file__).resolve().parents[2] / "frontend"
        process = await asyncio.create_subprocess_exec(
            "npx",
            "playwright",
            "test",
            "e2e/eipd-integrated.spec.ts",
            cwd=frontend,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        output, _ = await asyncio.wait_for(process.communicate(), timeout=120)
        assert process.returncode == 0, output.decode()[-6000:]
        async with _session_factory() as db:
            events = (
                await db.execute(
                    text(
                        "SELECT decision::text, review_context_metadata->>'metadata_schema_version', created_by FROM eipd_resolution_reviews WHERE assessment_id=:id"
                    ),
                    {"id": prepared[1]["id"]},
                )
            ).all()
            assert len(events) == 1
            assert events[0][0:2] == ("requiere_cambios", "2")
            assert events[0][2] == profile_a_id
            child_events = (
                await db.execute(
                    text(
                        "SELECT decision,review_context_metadata->>'metadata_schema_version',review_context_metadata->>'child_coverage',created_by FROM eipd_child_reviews WHERE assessment_id=:id"
                    ),
                    {"id": prepared[1]["id"]},
                )
            ).all()
            assert len(child_events) == 1
            assert tuple(child_events[0]) == (
                "requiere_cambios",
                "3",
                "contexto_v4",
                profile_a_id,
            )

            assert (
                await db.scalar(
                    text(
                        "SELECT child_adolescent_assessment->'assessment'->>'notes' FROM legal_assessments WHERE id=:id"
                    ),
                    {"id": prepared[1]["id"]},
                )
                == "PRUEBA: editor Chromium con API real aislada"
            )
            assert (
                await db.scalar(
                    text("SELECT status::text FROM legal_assessments WHERE id=:id"),
                    {"id": prepared[1]["id"]},
                )
                == "borrador"
            )
    finally:
        if process is not None and process.returncode is None:
            process.kill()
            await process.wait()
        server.should_exit = True
        await asyncio.wait_for(task, 10)
        listener.close()
