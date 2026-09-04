#!/usr/bin/env python3
"""Carga trusted, determinista y transaccional del fixture rat-default."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values, register_uuid

from rat_default_common import (
    CONFIG_VERSION_ID,
    SUPERADMIN_AUTH_ID,
    SUPERADMIN_PROFILE_ID,
    TENANT_A_AUTH_ID,
    TENANT_A_DIAGNOSTIC_ID,
    TENANT_A_MEMBERSHIP_ID,
    TENANT_A_ORG_ID,
    TENANT_A_PROFILE_ID,
    TENANT_B_AUTH_ID,
    TENANT_B_DIAGNOSTIC_ID,
    TENANT_B_MEMBERSHIP_ID,
    TENANT_B_ORG_ID,
    TENANT_B_PROFILE_ID,
    deterministic_id,
    load_fixture,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dsn = os.environ.get("RAT_TRUSTED_DATABASE_URL")
    if not dsn:
        raise SystemExit("RAT_TRUSTED_DATABASE_URL is required")
    data, digest = load_fixture(args.fixture)
    register_uuid()

    with psycopg2.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout = '30s'")
            cursor.execute(
                "INSERT INTO profiles (id, auth_user_id, email, full_name, is_superadmin) "
                "VALUES (%s, %s, %s, %s, true)",
                (
                    SUPERADMIN_PROFILE_ID,
                    SUPERADMIN_AUTH_ID,
                    "rat-superadmin@example.invalid",
                    "RAT Superadmin",
                ),
            )
            execute_values(
                cursor,
                "INSERT INTO obligaciones (id, numero_guia, nombre) VALUES %s",
                [
                    (o["id"], o["numero_guia"], o["nombre"])
                    for o in data["obligaciones"]
                ],
            )
            execute_values(
                cursor,
                "INSERT INTO secciones (id, numero_romano, nombre, obligacion_id, orden) VALUES %s",
                [
                    (s["id"], s["numero"], s["nombre"], s["obligacion_id"], order)
                    for order, s in enumerate(data["secciones"], start=1)
                ],
            )
            execute_values(
                cursor,
                "INSERT INTO preguntas (id, seccion_id, texto, orden) VALUES %s",
                [
                    (q["id"], s["id"], q["texto"], order)
                    for s in data["secciones"]
                    for order, q in enumerate(s["preguntas"], start=1)
                ],
            )
            cursor.execute(
                "INSERT INTO config_versiones "
                "(id, numero_version, activa, nota, creado_por) VALUES (%s, 1, true, %s, %s)",
                (
                    CONFIG_VERSION_ID,
                    "RAT rat-default trusted fixture",
                    SUPERADMIN_PROFILE_ID,
                ),
            )
            execute_values(
                cursor,
                "INSERT INTO config_seccion_pesos (id, version_id, seccion_id, peso_pct) VALUES %s",
                [
                    (
                        deterministic_id("peso", s["id"]),
                        CONFIG_VERSION_ID,
                        s["id"],
                        s["peso_pct"],
                    )
                    for s in data["secciones"]
                ],
            )
            execute_values(
                cursor,
                "INSERT INTO config_pregunta_riesgo (id, version_id, pregunta_id, riesgo) VALUES %s",
                [
                    (
                        deterministic_id("riesgo", q["id"]),
                        CONFIG_VERSION_ID,
                        q["id"],
                        q["riesgo"].lower(),
                    )
                    for s in data["secciones"]
                    for q in s["preguntas"]
                ],
            )
            execute_values(
                cursor,
                "INSERT INTO profiles (id, auth_user_id, email, full_name, is_superadmin) VALUES %s",
                [
                    (
                        TENANT_A_PROFILE_ID,
                        TENANT_A_AUTH_ID,
                        "rat-a@example.invalid",
                        "RAT Tenant A",
                        False,
                    ),
                    (
                        TENANT_B_PROFILE_ID,
                        TENANT_B_AUTH_ID,
                        "rat-b@example.invalid",
                        "RAT Tenant B",
                        False,
                    ),
                ],
            )
            execute_values(
                cursor,
                "INSERT INTO organizations (id, name, rut, industry, size, plan) VALUES %s",
                [
                    (
                        TENANT_A_ORG_ID,
                        "RAT Tenant A",
                        "11.111.111-1",
                        "benchmark",
                        "small",
                        "free",
                    ),
                    (
                        TENANT_B_ORG_ID,
                        "RAT Tenant B",
                        "22.222.222-2",
                        "benchmark",
                        "small",
                        "free",
                    ),
                ],
            )
            execute_values(
                cursor,
                "INSERT INTO memberships (id, organization_id, profile_id, role) VALUES %s",
                [
                    (
                        TENANT_A_MEMBERSHIP_ID,
                        TENANT_A_ORG_ID,
                        TENANT_A_PROFILE_ID,
                        "owner",
                    ),
                    (
                        TENANT_B_MEMBERSHIP_ID,
                        TENANT_B_ORG_ID,
                        TENANT_B_PROFILE_ID,
                        "owner",
                    ),
                ],
            )
            execute_values(
                cursor,
                "INSERT INTO diagnostics "
                "(id, organization_id, config_version_id, status, created_by, updated_by) VALUES %s",
                [
                    (
                        TENANT_A_DIAGNOSTIC_ID,
                        TENANT_A_ORG_ID,
                        CONFIG_VERSION_ID,
                        "en_progreso",
                        TENANT_A_PROFILE_ID,
                        TENANT_A_PROFILE_ID,
                    ),
                    (
                        TENANT_B_DIAGNOSTIC_ID,
                        TENANT_B_ORG_ID,
                        CONFIG_VERSION_ID,
                        "en_progreso",
                        TENANT_B_PROFILE_ID,
                        TENANT_B_PROFILE_ID,
                    ),
                ],
            )

    print(f"rat-default fixture loaded; sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
