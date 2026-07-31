"""Tests del motor de puntaje (Fase 1, Módulo 1, Tarea 2).

Casos hechos a mano con secciones sintéticas (sin DB) para las tres
funciones puras, más un test de integración liviano contra el catálogo real
sembrado (obtener_config_activa) al final.
"""

import pytest

from app.services.cuestionario_config import obtener_config_activa
from app.services.diagnostico_puntaje import (
    BrechaCandidata,
    RespuestaInput,
    calcular_puntaje_global,
    calcular_puntaje_por_seccion,
    detectar_brechas,
)

# ── Catálogo sintético compartido ─────────────────────────────────────────────
# SX: 2 preguntas, SY: 3 preguntas, SZ: 1 pregunta (nunca se responde en los
# tests de puntaje, para probar el caso "sección sin ninguna respuesta").

_SECCION_POR_PREGUNTA = {
    "SXQ1": "SX",
    "SXQ2": "SX",
    "SYQ1": "SY",
    "SYQ2": "SY",
    "SYQ3": "SY",
    "SZQ1": "SZ",
}
_RIESGO_POR_PREGUNTA = {
    "SXQ1": "Alto",
    "SXQ2": "Medio",
    "SYQ1": "Bajo",
    "SYQ2": "Alto",
    "SYQ3": "Medio",
    "SZQ1": "Bajo",
}
_PESO_POR_SECCION = {"SX": 60, "SY": 30, "SZ": 10}


# ── calcular_puntaje_por_seccion ──────────────────────────────────────────────


def test_puntaje_por_seccion_todas_las_preguntas_contestadas():
    respuestas = [
        RespuestaInput("SXQ1", "Sí"),  # 1.0
        RespuestaInput("SXQ2", "Parcial"),  # 0.5
    ]
    resultado = calcular_puntaje_por_seccion(respuestas, _SECCION_POR_PREGUNTA)
    assert resultado["SX"] == pytest.approx(75.0)  # (1.0+0.5)/2 * 100


def test_puntaje_por_seccion_excluye_na_y_sin_responder_del_denominador():
    respuestas = [
        RespuestaInput("SYQ1", "Sí"),  # 1.0
        RespuestaInput("SYQ2", "N/A"),  # excluida
        RespuestaInput("SYQ3", "No"),  # 0.0
        # SYQ2 respondida N/A y sin ninguna respuesta serían equivalentes;
        # aquí se cubre N/A explícito.
    ]
    resultado = calcular_puntaje_por_seccion(respuestas, _SECCION_POR_PREGUNTA)
    assert resultado["SY"] == pytest.approx(50.0)  # (1.0+0.0)/2 * 100, no /3


def test_puntaje_por_seccion_sin_ninguna_respuesta_es_none():
    resultado = calcular_puntaje_por_seccion([], _SECCION_POR_PREGUNTA)
    assert resultado["SZ"] is None


def test_puntaje_por_seccion_ignora_respuesta_de_pregunta_desconocida():
    respuestas = [RespuestaInput("PREGUNTA_QUE_NO_EXISTE", "Sí")]
    resultado = calcular_puntaje_por_seccion(respuestas, _SECCION_POR_PREGUNTA)
    assert all(v is None for v in resultado.values())


# ── calcular_puntaje_global ───────────────────────────────────────────────────


def test_puntaje_global_renormaliza_pesos_excluyendo_secciones_sin_puntaje():
    puntaje_por_seccion = {"SX": 75.0, "SY": 50.0, "SZ": None}
    resultado = calcular_puntaje_global(puntaje_por_seccion, _PESO_POR_SECCION)
    # peso_total = 60+30 = 90 (SZ excluida); 75*60/90 + 50*30/90
    assert resultado == pytest.approx(66.6667, rel=1e-4)


def test_puntaje_global_sin_ninguna_seccion_con_puntaje_es_none():
    puntaje_por_seccion = {"SX": None, "SY": None, "SZ": None}
    assert calcular_puntaje_global(puntaje_por_seccion, _PESO_POR_SECCION) is None


def test_puntaje_global_peso_total_cero_es_none():
    puntaje_por_seccion = {"SX": 75.0}
    assert calcular_puntaje_global(puntaje_por_seccion, {"SX": 0}) is None


# ── detectar_brechas ───────────────────────────────────────────────────────────


def test_detectar_brechas_regla_completa():
    respuestas = [
        RespuestaInput("SXQ1", "Parcial"),  # Alto -> Medio
        RespuestaInput("SXQ2", "Parcial"),  # Medio -> Bajo
        RespuestaInput("SYQ1", "Parcial"),  # Bajo -> Bajo
        RespuestaInput("SYQ2", "No"),  # Alto se mantiene
        RespuestaInput("SYQ3", "Sí"),  # no genera brecha
        RespuestaInput("SZQ1", "N/A"),  # no genera brecha
    ]
    brechas = detectar_brechas(respuestas, _SECCION_POR_PREGUNTA, _RIESGO_POR_PREGUNTA)

    por_pregunta = {b.pregunta_id: b for b in brechas}
    assert len(brechas) == 4
    assert por_pregunta["SXQ1"] == BrechaCandidata("SXQ1", "SX", "Medio")
    assert por_pregunta["SXQ2"] == BrechaCandidata("SXQ2", "SX", "Bajo")
    assert por_pregunta["SYQ1"] == BrechaCandidata("SYQ1", "SY", "Bajo")
    assert por_pregunta["SYQ2"] == BrechaCandidata("SYQ2", "SY", "Alto")
    assert "SYQ3" not in por_pregunta
    assert "SZQ1" not in por_pregunta


def test_detectar_brechas_sin_respuesta_no_genera_brecha():
    assert detectar_brechas([], _SECCION_POR_PREGUNTA, _RIESGO_POR_PREGUNTA) == []


# ── Integración liviana contra el catálogo real sembrado ─────────────────────


@pytest.mark.asyncio
async def test_motor_contra_catalogo_real_pregunta_conocida(_session_factory):
    """S1Q1 ('¿La organización ha designado...?') tiene riesgo 'Alto' en el
    catálogo real (ver backend/seed_data/modulo1/cuestionario_autodiagnostico_config.json).
    Chequeo de integración liviano: no reemplaza los casos unitarios de arriba."""
    async with _session_factory() as session:
        config = await obtener_config_activa(session)

    seccion_por_pregunta = {p.id: p.seccion_id for p in config.preguntas}
    assert config.riesgo_por_pregunta["S1Q1"] == "Alto"

    brechas = detectar_brechas(
        [RespuestaInput("S1Q1", "No")], seccion_por_pregunta, config.riesgo_por_pregunta
    )
    assert brechas == [BrechaCandidata("S1Q1", "S1", "Alto")]

    puntaje = calcular_puntaje_por_seccion(
        [RespuestaInput("S1Q1", "Sí")], seccion_por_pregunta
    )
    assert puntaje["S1"] == pytest.approx(100.0)  # única pregunta contestada de S1
