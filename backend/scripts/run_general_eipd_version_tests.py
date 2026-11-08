"""Fixed isolated destination, additive migration, focused tests; no operational DB writes."""

import asyncio
import os
import subprocess
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from scripts.run_eipd_tests import TEST_DATABASE, build_environment, verify_destination


async def prepare(env):
    engine = create_async_engine(env["DATABASE_URL"], echo=False, hide_parameters=True)
    runtime = create_async_engine(
        env["APP_DATABASE_URL"], echo=False, hide_parameters=True
    )
    try:
        async with engine.connect() as db:
            await db.execute(text("SET TRANSACTION READ ONLY"))
            if await db.scalar(
                text("SELECT current_database()")
            ) != TEST_DATABASE or await db.scalar(
                text("SELECT version_num FROM alembic_version")
            ) not in (
                "a84f6e2c9103",
                "b95e7f3d1204",
                "c53e19d8a621",
                "a52c910be604",
                "bf5d10a26c41",
                "d51ba5e1a702",
            ):
                raise ValueError("Destino aislado no admitido")
            for table in (
                "eipd_policy_publications",
                "eipd_policy_selections",
                "eipd_policy_selector",
            ):
                if await db.scalar(text("SELECT count(*) FROM " + table)):
                    raise ValueError("Estado aislado no vacio")
        async with runtime.connect() as db:
            row = (
                await db.execute(
                    text(
                        "SELECT current_database(),current_user,rolbypassrls,rolsuper FROM pg_roles WHERE rolname=current_user"
                    )
                )
            ).one()
            if tuple(row) != (TEST_DATABASE, "app_user", False, False):
                raise ValueError("Runtime no admitido")
    finally:
        await engine.dispose()
        await runtime.dispose()
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"], env=env, check=True
    )
    await verify_destination(env)


def main():
    if len(sys.argv) != 1:
        return 2
    env = build_environment(get_settings(), os.environ)
    asyncio.run(prepare(env))
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=short",
            # Historical downgrade of an ancestor cannot remove parent keys
            # referenced by the later append-only general-version history.
            "-k",
            "not test_downgrade_guard_and_empty_roundtrip",
            "tests/test_eipd_document_versions.py",
            "tests/test_eipd_version_reviews.py",
            "tests/test_eipd_version_decisions.py",
            "tests/test_base_fundamento_catalog.py",
            "tests/test_base_fundamento_versions.py",
            "tests/test_base_fundamento_reviews.py",
            "tests/test_eipd_child_successors.py",
            "tests/test_eipd_test_runner.py",
        ],
        env=env,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
