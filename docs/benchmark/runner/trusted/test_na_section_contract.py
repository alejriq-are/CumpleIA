"""Pruebas autoritativas de la tarea N/A por sección.

Este archivo se monta desde el checkout canónico. El código candidato se monta
en solo lectura y se ejecuta sin red, base de datos ni secretos.
"""

from __future__ import annotations

import os
import re
import uuid
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("SUPABASE_URL", "http://invalid.local")
WORKSPACE = Path("/workspace")
if not WORKSPACE.is_dir():
    pytest.skip("solo se ejecuta dentro del verifier aislado", allow_module_level=True)

from app.api import diagnostico as api  # noqa: E402
from app.services import diagnostico_exportacion as exportacion  # noqa: E402
from app.services.diagnostico_puntaje import (  # noqa: E402
    RespuestaInput,
    calcular_puntaje_por_seccion,
)


class _RowsResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return self._rows

    def scalar_one_or_none(self):
        return self._rows[0] if self._rows else None


class _FakeDb:
    def __init__(self, result_rows, organization=None):
        self._result_rows = iter(result_rows)
        self._organization = organization

    async def execute(self, _statement):
        return _RowsResult(next(self._result_rows))

    async def get(self, model, _identifier):
        if model.__name__ == "Organization":
            return self._organization
        return None


def _catalogo():
    secciones = [
        SimpleNamespace(id="S1", numero_romano="I", nombre="Gobernanza", orden=1),
        SimpleNamespace(id="S2", numero_romano="II", nombre="Licitud", orden=2),
        SimpleNamespace(id="S3", numero_romano="III", nombre="Seguridad", orden=3),
    ]
    preguntas = [
        SimpleNamespace(id="S1Q1", seccion_id="S1"),
        SimpleNamespace(id="S1Q2", seccion_id="S1"),
        SimpleNamespace(id="S1Q3", seccion_id="S1"),
        SimpleNamespace(id="S2Q1", seccion_id="S2"),
        SimpleNamespace(id="S2Q2", seccion_id="S2"),
        SimpleNamespace(id="S3Q1", seccion_id="S3"),
    ]
    return SimpleNamespace(
        secciones=secciones,
        preguntas=preguntas,
        riesgo_por_pregunta={p.id: "Bajo" for p in preguntas},
    )


def _respuestas():
    return [
        SimpleNamespace(pregunta_id="S1Q1", answer="Sí", notes=None),
        SimpleNamespace(pregunta_id="S1Q2", answer="N/A", notes=None),
        SimpleNamespace(pregunta_id="S1Q3", answer="Parcial", notes=None),
        SimpleNamespace(pregunta_id="S2Q1", answer="No", notes=None),
    ]


def _diagnostico():
    return SimpleNamespace(
        id=uuid.UUID("10000000-0000-0000-0000-000000000001"),
        organization_id=uuid.UUID("10000000-0000-0000-0000-000000000002"),
        config_version_id=uuid.UUID("10000000-0000-0000-0000-000000000003"),
        status="en_proceso",
        global_score=50.0,
        section_scores={"S1": 75.0, "S2": 0.0, "S3": None},
        informe_ia={"resumen_ejecutivo": "Resumen", "narrativas": []},
        informe_generado_en=datetime(2026, 9, 4, 12, 0, tzinfo=UTC),
        updated_by=None,
    )


@pytest.mark.asyncio
async def test_api_expone_conteos_por_seccion(monkeypatch):
    config = _catalogo()

    async def _config(_db, _version_id):
        return config

    monkeypatch.setattr(api, "obtener_config_por_id", _config)
    salida = await api._construir_actual_out(
        _FakeDb([_respuestas(), []]), _diagnostico()
    )
    por_seccion = {
        fila["seccion_id"]: fila for fila in salida.model_dump()["puntaje_por_seccion"]
    }

    assert por_seccion["S1"]["respondidas"] == 2
    assert por_seccion["S1"]["no_aplica"] == 1
    assert por_seccion["S2"]["respondidas"] == 1
    assert por_seccion["S2"]["no_aplica"] == 0
    assert por_seccion["S3"]["respondidas"] == 0
    assert por_seccion["S3"]["no_aplica"] == 0


def test_conteos_no_cambian_la_formula_de_puntaje():
    resultado = calcular_puntaje_por_seccion(
        [
            RespuestaInput("S1Q1", "Sí"),
            RespuestaInput("S1Q2", "N/A"),
            RespuestaInput("S1Q3", "Parcial"),
        ],
        {"S1Q1": "S1", "S1Q2": "S1", "S1Q3": "S1", "S2Q1": "S2"},
    )
    assert resultado == {"S1": 75.0, "S2": None}


def _texto(celda: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", celda)).strip()


@pytest.mark.asyncio
async def test_html_exportado_muestra_respondidas_y_na(monkeypatch):
    config = _catalogo()

    async def _config(_db, _version_id):
        return config

    monkeypatch.setattr(exportacion, "obtener_config_por_id", _config)
    organization = SimpleNamespace(
        name="Organización", rut=None, industry=None, size=None
    )
    html = await exportacion.generar_html_informe(
        _FakeDb([[], _respuestas()], organization), _diagnostico()
    )

    bloque = re.search(
        r"<h2>Puntaje por sección</h2>\s*<table>(.*?)</table>",
        html,
        flags=re.DOTALL,
    )
    assert bloque, "no se encontró la tabla de puntaje por sección"
    headers = [
        _texto(c)
        for c in re.findall(r"<th[^>]*>(.*?)</th>", bloque.group(1), re.DOTALL)
    ]
    assert "Respondidas" in headers
    assert "N/A" in headers

    filas = re.findall(r"<tr[^>]*>(.*?)</tr>", bloque.group(1), re.DOTALL)
    gobernanza = next(f for f in filas if "Gobernanza" in f)
    celdas = [
        _texto(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", gobernanza, re.DOTALL)
    ]
    valores = dict(zip(headers, celdas, strict=True))
    assert valores["Respondidas"] == "2"
    assert valores["N/A"] == "1"


def _sin_comentarios(texto: str) -> str:
    texto = re.sub(r"/\*.*?\*/", "", texto, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", texto)


def test_contrato_typescript_y_dashboard_muestran_ambos_conteos():
    contrato = _sin_comentarios(
        (WORKSPACE / "frontend/lib/api/client.ts").read_text(encoding="utf-8")
    )
    tipo = re.search(
        r"export\s+type\s+PuntajeSeccionOut\s*=\s*\{(.*?)\};",
        contrato,
        flags=re.DOTALL,
    )
    assert tipo, "falta PuntajeSeccionOut"
    assert re.search(r"\brespondidas\s*:\s*number\s*;", tipo.group(1))
    assert re.search(r"\bno_aplica\s*:\s*number\s*;", tipo.group(1))

    dashboard = _sin_comentarios(
        (
            WORKSPACE / "frontend/components/autodiagnostico/ResultadosDashboard.tsx"
        ).read_text(encoding="utf-8")
    )
    assert ".respondidas" in dashboard
    assert ".no_aplica" in dashboard
    assert re.search(r">\s*Respondidas\s*<", dashboard)
    assert re.search(r">\s*N/A\s*<", dashboard)
