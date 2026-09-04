"""Constantes y utilidades trusted para el perfil de verificacion rat-default."""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

FIXTURE_SHA256 = "2028a401a0f2c0bd83efcdb2e1e6b6eb991cedd133fea12ed7e17b81fda75ff1"

SUPERADMIN_PROFILE_ID = uuid.UUID("51000000-0000-0000-0000-000000000001")
SUPERADMIN_AUTH_ID = uuid.UUID("51000000-0000-0000-0000-000000000002")
CONFIG_VERSION_ID = uuid.UUID("51000000-0000-0000-0000-000000000003")

TENANT_A_ORG_ID = uuid.UUID("52000000-0000-0000-0000-000000000001")
TENANT_A_PROFILE_ID = uuid.UUID("52000000-0000-0000-0000-000000000002")
TENANT_A_AUTH_ID = uuid.UUID("52000000-0000-0000-0000-000000000003")
TENANT_A_MEMBERSHIP_ID = uuid.UUID("52000000-0000-0000-0000-000000000004")
TENANT_A_DIAGNOSTIC_ID = uuid.UUID("52000000-0000-0000-0000-000000000005")

TENANT_B_ORG_ID = uuid.UUID("53000000-0000-0000-0000-000000000001")
TENANT_B_PROFILE_ID = uuid.UUID("53000000-0000-0000-0000-000000000002")
TENANT_B_AUTH_ID = uuid.UUID("53000000-0000-0000-0000-000000000003")
TENANT_B_MEMBERSHIP_ID = uuid.UUID("53000000-0000-0000-0000-000000000004")
TENANT_B_DIAGNOSTIC_ID = uuid.UUID("53000000-0000-0000-0000-000000000005")

DERIVED_ID_NAMESPACE = uuid.UUID("51000000-0000-0000-0000-000000000099")


def deterministic_id(kind: str, source_id: str) -> uuid.UUID:
    return uuid.uuid5(DERIVED_ID_NAMESPACE, f"{kind}:{source_id}")


def load_fixture(path: Path) -> tuple[dict[str, Any], str]:
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != FIXTURE_SHA256:
        raise ValueError(
            f"fixture SHA-256 mismatch: expected {FIXTURE_SHA256}, got {digest}"
        )
    data = json.loads(payload.decode("utf-8"))
    validate_fixture(data)
    return data, digest


def validate_fixture(data: dict[str, Any]) -> None:
    obligaciones = data.get("obligaciones")
    secciones = data.get("secciones")
    if not isinstance(obligaciones, list) or len(obligaciones) != 8:
        raise ValueError("fixture must contain exactly 8 obligaciones")
    if not isinstance(secciones, list) or len(secciones) != 10:
        raise ValueError("fixture must contain exactly 10 secciones")

    obligacion_ids = {item["id"] for item in obligaciones}
    seccion_ids: set[str] = set()
    pregunta_ids: set[str] = set()
    total_peso = 0
    for expected_order, seccion in enumerate(secciones, start=1):
        if seccion["id"] in seccion_ids:
            raise ValueError(f"duplicate seccion id: {seccion['id']}")
        if seccion["obligacion_id"] not in obligacion_ids:
            raise ValueError(f"unknown obligacion in seccion {seccion['id']}")
        seccion_ids.add(seccion["id"])
        total_peso += seccion["peso_pct"]
        for pregunta in seccion["preguntas"]:
            if pregunta["id"] in pregunta_ids:
                raise ValueError(f"duplicate pregunta id: {pregunta['id']}")
            if pregunta["riesgo"].lower() not in {"alto", "medio", "bajo"}:
                raise ValueError(f"invalid risk for pregunta {pregunta['id']}")
            pregunta_ids.add(pregunta["id"])
        if expected_order > 10:
            raise ValueError("unexpected seccion order")

    if len(pregunta_ids) != 50:
        raise ValueError("fixture must contain exactly 50 preguntas")
    if total_peso != 100:
        raise ValueError(f"section weights must sum 100, got {total_peso}")
