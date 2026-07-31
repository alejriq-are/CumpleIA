"""Motor de puntaje del Autodiagnóstico (Fase 1, Módulo 1, Tarea 2).

Funciones puras — sin sesión de base de datos, sin efectos de lado. Reciben
las respuestas y los datos de catálogo (peso por sección, riesgo por
pregunta) que Tarea 3 arma a partir de `ConfigActiva`
(app/services/cuestionario_config.py::obtener_config_activa, o su futura
variante para una versión histórica vía Diagnostic.config_version_id) y
devuelven puntajes/brechas. Persistir el resultado (Diagnostic.global_score/
section_scores, filas de Finding) es responsabilidad de Tarea 3, no de este
módulo.

La fórmula no es una decisión de diseño: viene fijada en
backend/seed_data/modulo1/cuestionario_autodiagnostico_config.json
(`puntaje_por_respuesta`, `formula_puntaje`, `regla_riesgo_brecha`), la misma
fuente de verdad que ya sembró obligaciones/secciones/preguntas/
config_versiones — no se reinterpreta aquí.
"""

from dataclasses import dataclass

_PUNTAJE_POR_RESPUESTA = {"Sí": 1.0, "Parcial": 0.5, "No": 0.0}
_UN_NIVEL_ABAJO = {"Alto": "Medio", "Medio": "Bajo", "Bajo": "Bajo"}


@dataclass(frozen=True)
class RespuestaInput:
    pregunta_id: str
    answer: (
        str  # 'Sí' | 'Parcial' | 'No' | 'N/A' — dominio del CHECK de diagnostic_answers
    )


@dataclass(frozen=True)
class BrechaCandidata:
    pregunta_id: str
    seccion_id: str
    riesgo: (
        str  # 'Alto' | 'Medio' | 'Bajo' — ya degradado si la respuesta fue 'Parcial'
    )


def calcular_puntaje_por_seccion(
    respuestas: list[RespuestaInput],
    seccion_por_pregunta: dict[str, str],
) -> dict[str, float | None]:
    """Puntaje 0-100 por sección: promedio de las preguntas contestadas de esa
    sección (N/A y preguntas sin responder quedan fuera del denominador).

    Itera sobre `seccion_por_pregunta` (el catálogo), no sobre `respuestas`:
    una respuesta con un pregunta_id que ya no existe en el catálogo se
    ignora sola, y toda sección aparece en el resultado aunque no tenga
    ninguna respuesta (con valor None) — necesario para que
    `calcular_puntaje_global` sepa qué excluir de la renormalización.
    """
    respuesta_por_pregunta = {r.pregunta_id: r.answer for r in respuestas}

    valores_por_seccion: dict[str, list[float]] = {
        seccion_id: [] for seccion_id in set(seccion_por_pregunta.values())
    }
    for pregunta_id, seccion_id in seccion_por_pregunta.items():
        answer = respuesta_por_pregunta.get(pregunta_id)
        if answer not in _PUNTAJE_POR_RESPUESTA:
            continue  # N/A, sin responder, o un valor fuera del dominio esperado
        valores_por_seccion[seccion_id].append(_PUNTAJE_POR_RESPUESTA[answer])

    return {
        seccion_id: (sum(valores) / len(valores) * 100) if valores else None
        for seccion_id, valores in valores_por_seccion.items()
    }


def calcular_puntaje_global(
    puntaje_por_seccion: dict[str, float | None],
    peso_por_seccion: dict[str, int],
) -> float | None:
    """Suma ponderada de puntaje_seccion × peso_pct, renormalizando peso_pct
    sobre las secciones con puntaje (no None). None si ninguna sección tiene
    puntaje (diagnóstico sin ninguna respuesta) o si el peso de las secciones
    con puntaje suma 0 (caso extremo pero válido: peso_pct admite 0)."""
    secciones_con_puntaje = [
        (seccion_id, score)
        for seccion_id, score in puntaje_por_seccion.items()
        if score is not None
    ]
    if not secciones_con_puntaje:
        return None

    peso_total = sum(
        peso_por_seccion[seccion_id] for seccion_id, _ in secciones_con_puntaje
    )
    if peso_total == 0:
        return None

    return sum(
        score * (peso_por_seccion[seccion_id] / peso_total)
        for seccion_id, score in secciones_con_puntaje
    )


def detectar_brechas(
    respuestas: list[RespuestaInput],
    seccion_por_pregunta: dict[str, str],
    riesgo_por_pregunta: dict[str, str],
) -> list[BrechaCandidata]:
    """Una respuesta 'No' genera una brecha con el riesgo de la pregunta; una
    'Parcial' genera una brecha un nivel más abajo (Alto->Medio,
    Medio->Bajo, Bajo->Bajo). 'Sí' y 'N/A' no generan brecha."""
    respuesta_por_pregunta = {r.pregunta_id: r.answer for r in respuestas}

    candidatas = []
    for pregunta_id, seccion_id in seccion_por_pregunta.items():
        answer = respuesta_por_pregunta.get(pregunta_id)
        if answer not in ("No", "Parcial"):
            continue

        riesgo_base = riesgo_por_pregunta[pregunta_id]
        riesgo = riesgo_base if answer == "No" else _UN_NIVEL_ABAJO[riesgo_base]
        candidatas.append(
            BrechaCandidata(
                pregunta_id=pregunta_id, seccion_id=seccion_id, riesgo=riesgo
            )
        )
    return candidatas
