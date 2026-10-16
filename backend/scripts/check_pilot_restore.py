"""Ensayo local fijo de restauracion. No admite URLs, nombres ni opciones externas."""

import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import get_settings
from scripts.run_eipd_tests import TEST_DATABASE, build_environment, verify_destination

RESTORE_DATABASE = "cumpleia_pilot_restore_check_20261016"
CONTAINER = "cumpleia_db"
HISTORY_TABLES = (
    "eipd_child_resolutions",
    "eipd_child_reviews",
    "organization_acceptance_authorities",
    "organization_document_acceptances",
)


def quote(value):
    return '"' + value.replace('"', '""') + '"'


def snapshot(engine):
    with engine.connect() as db:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        tables = db.execute(
            text(
                "SELECT schemaname,tablename FROM pg_tables WHERE schemaname IN ('public','auth') ORDER BY schemaname,tablename"
            )
        ).all()
        rows = {
            f"{schema}.{table}": tuple(
                db.execute(
                    text(
                        "SELECT count(*),md5(COALESCE(string_agg(row_to_json(t)::text,chr(10) ORDER BY row_to_json(t)::text),'')) FROM "
                        + quote(schema)
                        + "."
                        + quote(table)
                        + " t"
                    )
                ).one()
            )
            for schema, table in tables
        }
        policies = [
            tuple(r)
            for r in db.execute(
                text(
                    "SELECT schemaname,tablename,policyname,roles::text,cmd,qual,with_check FROM pg_policies WHERE schemaname IN ('public','auth') ORDER BY schemaname,tablename,policyname"
                )
            )
        ]
        return {"tables": rows, "policies": policies}


def docker(command, env, stdin=None, stdout=None):
    result = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "-e",
            "PGPASSWORD",
            "-e",
            "PGUSER",
            "-e",
            "PGHOST",
            "-e",
            "PGPORT",
            CONTAINER,
            *command,
        ],
        env=env,
        stdin=stdin,
        stdout=stdout or subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError("Herramienta PostgreSQL no completo el ensayo")


def run():
    if shutil.which("docker") is None:
        raise RuntimeError("Docker local no disponible")
    env = build_environment(get_settings(), os.environ)
    asyncio.run(verify_destination(env))
    source = make_url(env["DATABASE_URL"]).set(drivername="postgresql")
    runtime = make_url(env["APP_DATABASE_URL"]).set(drivername="postgresql")
    if (
        source.database != TEST_DATABASE
        or source.port not in (None, 5432)
        or source.username != "postgres"
    ):
        raise RuntimeError("Destino/rol no admitido para ensayo fijo")
    inspect = subprocess.run(
        ["docker", "inspect", "--format", "{{.Config.Image}}", CONTAINER],
        capture_output=True,
        text=True,
    )
    if inspect.returncode or inspect.stdout.strip() != "pgvector/pgvector:pg16":
        raise RuntimeError("Contenedor fijo no corresponde")
    pg_env = {k: v for k, v in os.environ.items() if not k.upper().startswith("PG")}
    pg_env.update(
        PGPASSWORD=source.password or "",
        PGUSER=source.username,
        PGHOST="127.0.0.1",
        PGPORT="5432",
    )
    src = create_engine(source, echo=False, hide_parameters=True)
    control = create_engine(
        source.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        echo=False,
        hide_parameters=True,
    )
    restored = None
    app = None
    created = False
    marker = "cumpleia-restore-fixture-" + str(uuid4())
    started = time.monotonic()
    try:
        before = snapshot(src)
        with control.connect() as manager:
            if not manager.scalar(text("SELECT pg_try_advisory_lock(20261016,17)")):
                raise RuntimeError("Ensayo ya en ejecucion")
            if manager.scalar(
                text("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=:name)"),
                {"name": RESTORE_DATABASE},
            ):
                raise RuntimeError("Base temporal ya existe; no se sobrescribe")
            try:
                with tempfile.TemporaryDirectory(prefix="cumpleia-restore-") as folder:
                    backup = Path(folder) / "fictitious.dump"
                    with backup.open("wb") as stream:
                        docker(
                            ["pg_dump", "--format=custom", "--dbname", TEST_DATABASE],
                            pg_env,
                            stdout=stream,
                        )
                    backup.chmod(0o600)
                    manager.execute(text("CREATE DATABASE " + quote(RESTORE_DATABASE)))
                    created = True
                    manager.execute(
                        text(
                            "COMMENT ON DATABASE "
                            + quote(RESTORE_DATABASE)
                            + " IS '"
                            + marker
                            + "'"
                        )
                    )
                    with backup.open("rb") as stream:
                        docker(
                            [
                                "pg_restore",
                                "--exit-on-error",
                                "--single-transaction",
                                "--dbname",
                                RESTORE_DATABASE,
                            ],
                            pg_env,
                            stdin=stream,
                        )
                    restored = create_engine(
                        source.set(database=RESTORE_DATABASE),
                        echo=False,
                        hide_parameters=True,
                    )
                    assert snapshot(restored) == before, "Restore distinto del origen"
                    app = create_engine(
                        runtime.set(database=RESTORE_DATABASE),
                        echo=False,
                        hide_parameters=True,
                    )
                    with app.connect() as db:
                        role = db.execute(
                            text(
                                "SELECT current_database(),current_user,rolbypassrls,rolsuper FROM pg_roles WHERE rolname=current_user"
                            )
                        ).one()
                        assert tuple(role) == (
                            RESTORE_DATABASE,
                            "app_user",
                            False,
                            False,
                        )
                        for table in HISTORY_TABLES:
                            assert db.scalar(
                                text(
                                    "SELECT relrowsecurity FROM pg_class WHERE oid=CAST(:t AS regclass)"
                                ),
                                {"t": table},
                            )
                            for operation in ("UPDATE", "DELETE", "TRUNCATE"):
                                assert not db.scalar(
                                    text(
                                        "SELECT has_table_privilege('app_user',:t,:op)"
                                    ),
                                    {"t": table, "op": operation},
                                )
                    assert snapshot(src) == before, "Origen cambio durante ensayo"
                    fingerprint = hashlib.sha256(
                        json.dumps(before, sort_keys=True, default=str).encode()
                    ).hexdigest()
                    report = {
                        "schema_version": 1,
                        "data_kind": "ficticios",
                        "source_database": TEST_DATABASE,
                        "restore_database": RESTORE_DATABASE,
                        "tables_checked": len(before["tables"]),
                        "history_rls_and_immutability_checked": len(HISTORY_TABLES),
                        "history_rows_restored": sum(
                            before["tables"]["public." + table][0]
                            for table in HISTORY_TABLES
                        ),
                        "snapshot_fingerprint": fingerprint,
                        "elapsed_seconds": round(time.monotonic() - started, 2),
                        "result": "restauracion_local_aislada_coincidente",
                        "source_unchanged": True,
                        "proves_production_restore": False,
                        "mvp_ready": False,
                        "allows_real_data": False,
                        "can_confirm": False,
                        "activation": "deshabilitada",
                    }
            finally:
                if app:
                    app.dispose()
                if restored:
                    restored.dispose()
                if created:
                    comment = manager.scalar(
                        text(
                            "SELECT shobj_description(oid,'pg_database') FROM pg_database WHERE datname=:name"
                        ),
                        {"name": RESTORE_DATABASE},
                    )
                    if comment != marker:
                        raise RuntimeError("Base temporal ajena; limpieza bloqueada")
                    manager.execute(text("DROP DATABASE " + quote(RESTORE_DATABASE)))
            report["temporary_database_removed"] = True
            return report
    finally:
        src.dispose()
        control.dispose()


def main():
    if len(sys.argv) != 1:
        print("Ejecutor fijo: no admite argumentos.")
        return 2
    try:
        report = run()
    except Exception:
        print(
            "Ensayo no validado: revisar destino fijo, contenedor, permisos o copia temporal; no se certifica operacion piloto."
        )
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
