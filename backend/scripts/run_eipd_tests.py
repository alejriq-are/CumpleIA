"""Ejecutor local fijo: python -m scripts.run_eipd_tests; nunca crea/borra DB."""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DATABASE = "cumpleia_eipd_tests_20261009"
EXPECTED_HEAD = "d39e2b0f841c"
TARGETS = (
    "tests/test_eipd_test_runner.py",
    "tests/test_services_research.py",
    "tests/test_research_binding.py",
    "tests/test_eipd_resolution_binding_v2.py",
    "tests/test_eipd_frontier_v2.py",
    "tests/test_eipd_screening_v3.py",
    "tests/test_eipd_controls_v3.py",
    "tests/test_eipd_resolution_writer.py",
    "tests/test_eipd_review_metadata.py",
    "tests/test_eipd_review_prerequisites_v3.py",
    "tests/test_eipd_review_metadata_storage.py",
    "tests/test_api_eipd_review_metadata_readiness.py",
    "tests/test_api_eipd_resolution_writer_v2.py",
    "tests/test_api_eipd_controls_v3_readiness.py",
    "tests/test_services_eipd_resolution.py",
    "tests/test_research_transversal_binding.py",
    "tests/test_research_storage.py",
    "tests/test_api_research.py",
    "tests/test_api_licitud.py",
    "tests/test_eipd_channel_lifecycle.py",
    "tests/test_api_eipd_admin.py",
    "tests/test_api_eipd_admin_concurrency.py",
)


def build_environment(settings, inherited):
    if settings.environment != "development":
        raise ValueError("Solo desarrollo local")
    maintenance = make_url(settings.database_url)
    runtime = make_url(settings.app_database_url)
    for url in (maintenance, runtime):
        if (
            url.drivername != "postgresql+asyncpg"
            or url.host not in ("localhost", "127.0.0.1", "::1")
            or url.query
        ):
            raise ValueError("Destino local requerido")
    if (maintenance.host, maintenance.port) != (runtime.host, runtime.port):
        raise ValueError("Destinos diferentes")
    if runtime.username != "app_user" or maintenance.username == runtime.username:
        raise ValueError("Roles separados requeridos")
    env = dict(inherited)
    for key in list(env):
        if key.upper() in (
            "DATABASE_URL",
            "APP_DATABASE_URL",
            "EIPD_ADMIN_DATABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_ANON_KEY",
            "SUPABASE_URL",
            "PYTEST_ADDOPTS",
            "PYTEST_PLUGINS",
        ):
            del env[key]
    env["DATABASE_URL"] = maintenance.set(database=TEST_DATABASE).render_as_string(
        hide_password=False
    )
    env["APP_DATABASE_URL"] = runtime.set(database=TEST_DATABASE).render_as_string(
        hide_password=False
    )
    env["SUPABASE_URL"] = "https://test-project.supabase.co"
    return env


def validate_catalog(
    database,
    head,
    publication_count,
    selection_count,
    selector_count,
    runtime_role,
    bypass,
    superuser,
):
    if database != TEST_DATABASE or head != EXPECTED_HEAD:
        raise ValueError("Base/head no admitidos")
    if any((publication_count, selection_count, selector_count)):
        raise ValueError("Registro de pruebas no vacio")
    if runtime_role != "app_user" or bypass or superuser:
        raise ValueError("Runtime restringido requerido")


async def verify_destination(env):
    maintenance = create_async_engine(
        env["DATABASE_URL"], echo=False, hide_parameters=True
    )
    runtime = create_async_engine(
        env["APP_DATABASE_URL"], echo=False, hide_parameters=True
    )
    try:
        async with maintenance.connect() as db:
            await db.execute(text("SET TRANSACTION READ ONLY"))
            database = await db.scalar(text("SELECT current_database()"))
            head = await db.scalar(text("SELECT version_num FROM alembic_version"))
            counts = [
                await db.scalar(text("SELECT count(*) FROM " + table))
                for table in (
                    "eipd_policy_publications",
                    "eipd_policy_selections",
                    "eipd_policy_selector",
                )
            ]
            await db.rollback()
        async with runtime.connect() as db:
            await db.execute(text("SET TRANSACTION READ ONLY"))
            row = (
                await db.execute(
                    text(
                        "SELECT current_database(), current_user, rolbypassrls, rolsuper FROM pg_roles WHERE rolname=current_user"
                    )
                )
            ).one()
            if row[0] != TEST_DATABASE:
                raise ValueError("Runtime fuera de pruebas")
            validate_catalog(database, head, *counts, *row[1:])
            await db.rollback()
    finally:
        await maintenance.dispose()
        await runtime.dispose()


def main():
    if len(sys.argv) != 1:
        print("Ejecutor fijo: no admite argumentos adicionales.")
        return 2
    try:
        from app.core.config import get_settings

        env = build_environment(get_settings(), os.environ)
        asyncio.run(verify_destination(env))
    except Exception:
        print(
            "Pruebas bloqueadas: comprobar base aislada, head, registro vacio y roles. No se inicio pytest."
        )
        return 2
    print("Destino aislado verificado; iniciando suite EIPD focalizada.", flush=True)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *TARGETS],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
