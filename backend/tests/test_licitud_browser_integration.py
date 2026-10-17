"""Nuevo recorrido Chromium/API/PostgreSQL aislado, con JWT sintetico de fixture."""

import asyncio
import os
import socket
from pathlib import Path

import pytest
import uvicorn
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from tests import test_eipd_child_successors as cases

rat_m3 = cases.rat_m3
pytestmark = [
    pytest.mark.asyncio(loop_scope="session"),
    pytest.mark.skipif(
        os.getenv("CUMPLEIA_UI_INTEGRATION") != "1",
        reason="Integracion local explicita",
    ),
]


async def test_workspace_real_api(rat_m3, client_a, org_a_id, _session_factory):
    tid, _ = rat_m3
    app = client_a
    app.add_api_route(
        "/__licitud-isolated-test",
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
            CUMPLEIA_UI_ORG=str(org_a_id),
            CUMPLEIA_UI_TREATMENT=str(tid),
        )
        process = await asyncio.create_subprocess_exec(
            "npx",
            "playwright",
            "test",
            "e2e/licitud-workspace.spec.ts",
            cwd=Path(__file__).resolve().parents[2] / "frontend",
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        output, _ = await asyncio.wait_for(process.communicate(), 120)
        assert process.returncode == 0, output.decode()[-6000:]
        async with _session_factory() as db:
            rows = (
                await db.execute(
                    text(
                        "SELECT status::text,lia_assessment->'necessity'->>'necessity_analysis',confirmed_at FROM legal_assessments WHERE treatment_id=:id"
                    ),
                    {"id": tid},
                )
            ).all()
            assert len(rows) == 1
            assert tuple(rows[0]) == (
                "borrador",
                "[FICTICIA] Necesidad de prueba",
                None,
            )
    finally:
        if process and process.returncode is None:
            process.kill()
            await process.communicate()
        server.should_exit = True
        await asyncio.wait_for(task, 10)
        listener.close()
