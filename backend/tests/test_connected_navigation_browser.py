"""Connected shell against actual API and isolated PostgreSQL; synthetic fixture auth."""

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
saved = cases.saved
pytestmark = [
    pytest.mark.asyncio(loop_scope="session"),
    pytest.mark.skipif(
        os.getenv("CUMPLEIA_UI_INTEGRATION") != "1",
        reason="Integración aislada explícita",
    ),
]


async def test_connected_navigation_real_api(saved, _session_factory):
    tid, row, app, org = saved
    app.add_api_route(
        "/__connected-isolated-test",
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
            CUMPLEIA_UI_ORG=str(org),
            CUMPLEIA_UI_TREATMENT=str(tid),
            CUMPLEIA_UI_ASSESSMENT=str(row["id"]),
        )
        process = await asyncio.create_subprocess_exec(
            "npx",
            "playwright",
            "test",
            "e2e/connected-navigation.integration.spec.ts",
            cwd=Path(__file__).resolve().parents[2] / "frontend",
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        output, _ = await asyncio.wait_for(process.communicate(), 120)
        assert process.returncode == 0, output.decode()[-7500:]
        async with _session_factory() as db:
            assessment = (
                await db.execute(
                    text(
                        "SELECT status::text,justification,confirmed_at FROM legal_assessments WHERE id=:id"
                    ),
                    {"id": row["id"]},
                )
            ).one()
            assert tuple(assessment) == (
                "borrador",
                "[FICTICIA] Navegación conectada persistente",
                None,
            )
            determination = (
                await db.execute(
                    text(
                        "SELECT revision,payload FROM assessment_support_records WHERE assessment_id=:id AND kind='applicability'"
                    ),
                    {"id": row["id"]},
                )
            ).one()
            assert determination[0] == 1
            assert determination[1]["eipd"]["state"] == "corresponde"
            assert determination[1]["infancia"]["state"] == "corresponde"
    finally:
        if process and process.returncode is None:
            process.kill()
            await process.communicate()
        server.should_exit = True
        await asyncio.wait_for(task, 10)
        listener.close()
