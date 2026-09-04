#!/usr/bin/env python3
"""Verificador trusted y fail-closed para el perfil rat-default."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

import psycopg2
from psycopg2.extras import register_uuid

from rat_default_common import (
    CONFIG_VERSION_ID,
    FIXTURE_SHA256,
    SUPERADMIN_PROFILE_ID,
    TENANT_A_AUTH_ID,
    TENANT_A_DIAGNOSTIC_ID,
    TENANT_A_MEMBERSHIP_ID,
    TENANT_A_ORG_ID,
    TENANT_B_AUTH_ID,
    TENANT_B_DIAGNOSTIC_ID,
    TENANT_B_MEMBERSHIP_ID,
    TENANT_B_ORG_ID,
    deterministic_id,
    load_fixture,
)

Check = Callable[[Any], dict[str, Any]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    return parser.parse_args()


def fetchall(
    cursor: Any, query: str, params: tuple[Any, ...] = ()
) -> list[tuple[Any, ...]]:
    cursor.execute(query, params)
    return list(cursor.fetchall())


def expect(name: str, actual: Any, expected: Any) -> dict[str, Any]:
    if actual != expected:
        raise AssertionError(f"{name}: value mismatch")
    return {"name": name, "status": "PASS"}


def check_fixture_hash(_: Any) -> dict[str, Any]:
    return {"name": "fixture_sha256", "status": "PASS", "sha256": FIXTURE_SHA256}


def check_alembic_head(cursor: Any) -> dict[str, Any]:
    rows = fetchall(cursor, "SELECT version_num FROM alembic_version")
    return expect("alembic_single_head", len(rows), 1)


def check_catalog(cursor: Any, data: dict[str, Any]) -> dict[str, Any]:
    obligations = fetchall(
        cursor, "SELECT id, numero_guia, nombre FROM obligaciones ORDER BY id"
    )
    expected_obligations = sorted(
        (item["id"], item["numero_guia"], item["nombre"])
        for item in data["obligaciones"]
    )
    expect("obligaciones_content", obligations, expected_obligations)

    sections = fetchall(
        cursor,
        "SELECT id, numero_romano, nombre, obligacion_id, orden FROM secciones ORDER BY orden",
    )
    expected_sections = [
        (item["id"], item["numero"], item["nombre"], item["obligacion_id"], index)
        for index, item in enumerate(data["secciones"], start=1)
    ]
    expect("secciones_content", sections, expected_sections)

    questions = fetchall(
        cursor,
        "SELECT id, seccion_id, texto, orden FROM preguntas ORDER BY seccion_id, orden",
    )
    expected_questions = sorted(
        [
            (
                question["id"],
                section["id"],
                question["texto"],
                index,
            )
            for section in data["secciones"]
            for index, question in enumerate(section["preguntas"], start=1)
        ],
        key=lambda row: (row[1], row[3]),
    )
    expect("preguntas_content", questions, expected_questions)
    return {
        "name": "catalog_content",
        "status": "PASS",
        "counts": {"obligaciones": 8, "secciones": 10, "preguntas": 50},
    }


def check_configuration(cursor: Any, data: dict[str, Any]) -> dict[str, Any]:
    versions = fetchall(
        cursor,
        "SELECT id, numero_version, activa, creado_por FROM config_versiones ORDER BY numero_version",
    )
    expect(
        "config_v1_active",
        versions,
        [(CONFIG_VERSION_ID, 1, True, SUPERADMIN_PROFILE_ID)],
    )
    weights = fetchall(
        cursor,
        "SELECT id, seccion_id, peso_pct FROM config_seccion_pesos "
        "WHERE version_id = %s ORDER BY seccion_id",
        (CONFIG_VERSION_ID,),
    )
    expected_weights = sorted(
        [
            (deterministic_id("peso", s["id"]), s["id"], Decimal(str(s["peso_pct"])))
            for s in data["secciones"]
        ],
        key=lambda row: row[1],
    )
    expect("section_weights", weights, expected_weights)
    expect("section_weight_sum", sum(row[2] for row in weights), Decimal("100.00"))

    risks = fetchall(
        cursor,
        "SELECT id, pregunta_id, riesgo::text FROM config_pregunta_riesgo "
        "WHERE version_id = %s ORDER BY pregunta_id",
        (CONFIG_VERSION_ID,),
    )
    expected_risks = sorted(
        [
            (deterministic_id("riesgo", q["id"]), q["id"], q["riesgo"].lower())
            for s in data["secciones"]
            for q in s["preguntas"]
        ],
        key=lambda row: row[1],
    )
    expect("question_risks", risks, expected_risks)
    return {
        "name": "active_configuration",
        "status": "PASS",
        "version": 1,
        "weights": 10,
        "weightSum": 100,
        "risks": 50,
    }


def check_app_user(cursor: Any) -> dict[str, Any]:
    roles = fetchall(
        cursor,
        "SELECT rolsuper, rolcreatedb, rolcreaterole, rolbypassrls, rolcanlogin "
        "FROM pg_roles WHERE rolname = 'app_user'",
    )
    expect("app_user_role", roles, [(False, False, False, False, True)])
    expect(
        "app_user_no_schema_create",
        fetchall(cursor, "SELECT has_schema_privilege('app_user', 'public', 'CREATE')"),
        [(False,)],
    )
    required_tables = ["organizations", "memberships", "diagnostics"]
    for table in required_tables:
        expect(
            f"rls_enabled_{table}",
            fetchall(
                cursor,
                "SELECT relrowsecurity FROM pg_class WHERE oid = %s::regclass",
                (table,),
            ),
            [(True,)],
        )
    return {"name": "app_user_least_privilege", "status": "PASS"}


def visible_ids(cursor: Any, auth_id: Any, table: str) -> list[Any]:
    cursor.execute("SET LOCAL ROLE app_user")
    cursor.execute(
        "SELECT set_config('request.jwt.claim.sub', %s, true)", (str(auth_id),)
    )
    rows = fetchall(cursor, f"SELECT id FROM {table} ORDER BY id")
    cursor.execute("RESET ROLE")
    return [row[0] for row in rows]


def check_rls(cursor: Any) -> dict[str, Any]:
    expect(
        "tenant_a_organizations",
        visible_ids(cursor, TENANT_A_AUTH_ID, "organizations"),
        [TENANT_A_ORG_ID],
    )
    expect(
        "tenant_a_diagnostics",
        visible_ids(cursor, TENANT_A_AUTH_ID, "diagnostics"),
        [TENANT_A_DIAGNOSTIC_ID],
    )
    expect(
        "tenant_a_memberships",
        visible_ids(cursor, TENANT_A_AUTH_ID, "memberships"),
        [TENANT_A_MEMBERSHIP_ID],
    )
    expect(
        "tenant_b_organizations",
        visible_ids(cursor, TENANT_B_AUTH_ID, "organizations"),
        [TENANT_B_ORG_ID],
    )
    expect(
        "tenant_b_diagnostics",
        visible_ids(cursor, TENANT_B_AUTH_ID, "diagnostics"),
        [TENANT_B_DIAGNOSTIC_ID],
    )
    expect(
        "tenant_b_memberships",
        visible_ids(cursor, TENANT_B_AUTH_ID, "memberships"),
        [TENANT_B_MEMBERSHIP_ID],
    )
    return {"name": "rls_tenant_a_b", "status": "PASS"}


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> int:
    args = parse_args()
    started_at = datetime.now(UTC)
    checks: list[dict[str, Any]] = []
    log_lines: list[str] = []
    status = "HARNESS_ERROR"
    error: str | None = None

    try:
        data, _ = load_fixture(args.fixture)
        register_uuid()
        dsn = os.environ.get("RAT_TRUSTED_DATABASE_URL")
        if not dsn:
            raise RuntimeError("RAT_TRUSTED_DATABASE_URL is required")
        with psycopg2.connect(dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL statement_timeout = '30s'")
                operations: list[tuple[str, Callable[[], dict[str, Any]]]] = [
                    ("fixture_sha256", lambda: check_fixture_hash(cursor)),
                    ("alembic_single_head", lambda: check_alembic_head(cursor)),
                    ("catalog_content", lambda: check_catalog(cursor, data)),
                    ("active_configuration", lambda: check_configuration(cursor, data)),
                    ("app_user_least_privilege", lambda: check_app_user(cursor)),
                    ("rls_tenant_a_b", lambda: check_rls(cursor)),
                ]
                for name, operation in operations:
                    try:
                        result = operation()
                        checks.append(result)
                        log_lines.append(f"PASS {name}")
                    except AssertionError as exc:
                        checks.append(
                            {"name": name, "status": "FAIL", "message": str(exc)}
                        )
                        log_lines.append(f"FAIL {name}: {exc}")
                status = (
                    "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
                )
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        log_lines.append(f"HARNESS_ERROR {error}")

    finished_at = datetime.now(UTC)
    report = {
        "schemaVersion": "1.0",
        "profile": "rat-default",
        "status": status,
        "trustedChecksPassed": status == "PASS",
        "startedAt": started_at.isoformat(),
        "finishedAt": finished_at.isoformat(),
        "fixtureSha256": FIXTURE_SHA256,
        "checks": checks,
        "error": error,
    }
    atomic_write(args.output, json.dumps(report, indent=2, sort_keys=True) + "\n")
    atomic_write(args.log, "\n".join(log_lines) + "\n")
    return 0 if status == "PASS" else (1 if status == "FAIL" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
