"""Capa de IA del Autodiagnóstico (Fase 1, Módulo 1, Tarea 4).

Genera la narrativa del informe de un diagnóstico completado, anclada a RAG
(Ley 21.719 + guía CCS — nunca Ley 19.628, ver
docs/adr/0002-logica-adaptativa-riesgo-remediacion.md). El LLM solo redacta:
el nivel de riesgo (app/services/diagnostico_puntaje.py, Tarea 2) y el mapeo
a obligaciones (cadena Pregunta→Seccion→Obligacion del catálogo, Tarea 0) ya
vienen resueltos de forma determinista antes de llegar aquí.

Guardarraíl (acordado explícitamente, no solo el schema forzado): cualquier
cita que el modelo devuelva y que no corresponda exactamente a un fragmento
realmente recuperado por RAG se descarta en silencio (se deja constancia en
logs) — nunca se persiste una cita inventada. Lo mismo para un `finding_id`
que no pertenezca al diagnóstico.
"""

import logging
import re
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import (
    Diagnostic,
    DiagnosticAnswer,
    Finding,
    FindingStatus,
    Organization,
)
from app.services.cuestionario_config import obtener_config_por_id
from app.services.providers.llm import get_llm_client
from app.services.rag import search_chunks

logger = logging.getLogger("app.diagnostico_ia")

FUENTES_ANCLAJE = ["ley_21719", "guia_ccs"]

# BUG-01 (revisión manual del informe, Claude_22_julio_2026/
# mejoras-informe-autodiagnostico.md): la regla 5 del system_prompt le pide
# al LLM que no declare una cifra total de brechas/hallazgos, pero es solo
# una instrucción — se verificó en producción que el modelo puede seguir
# haciéndolo (ej. "se detectaron 35 brechas" cuando `len(hallazgos)` real
# era 34). Sin este guardarraíl determinista, el número que el LLM decide
# escribir es una segunda fuente de verdad que puede no coincidir con el
# conteo real que ya se muestra en app/services/diagnostico_exportacion.py.
# No cubre números escritos en palabras ("treinta y cinco") — el LLM
# consistentemente usa dígitos cuando se le da un conteo exacto en el prompt.
_PATRON_CONTEO_BRECHAS = re.compile(r"\b\d+\b\s+(brechas?|hallazgos?)", re.IGNORECASE)


def _quitar_conteo_de_brechas(texto: str) -> str:
    saneado, n = _PATRON_CONTEO_BRECHAS.subn(r"\1", texto)
    if n:
        logger.warning(
            "Se quitó una cifra de brechas/hallazgos declarada por el LLM en "
            "el resumen ejecutivo (%d ocurrencia(s)): el conteo determinista "
            "vive solo en la exportación, no en el texto libre.",
            n,
        )
    return saneado


_INFORME_SCHEMA = {
    "type": "object",
    "properties": {
        "resumen_ejecutivo": {
            "type": "string",
            "description": "Resumen general del estado de cumplimiento, 2-4 párrafos.",
        },
        "narrativas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "finding_id": {"type": "string"},
                    "narrativa": {"type": "string"},
                    "citas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source": {"type": "string"},
                                "reference": {"type": "string"},
                            },
                            "required": ["source", "reference"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["finding_id", "narrativa", "citas"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["resumen_ejecutivo", "narrativas"],
    "additionalProperties": False,
}


async def generar_informe(db: AsyncSession, diagnostic: Diagnostic) -> dict:
    """Genera, sanea y persiste `diagnostic.informe_ia`. Devuelve el informe."""
    if diagnostic.status != "completado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El informe solo puede generarse con el diagnóstico completado.",
        )

    config = await obtener_config_por_id(db, diagnostic.config_version_id)
    preguntas_por_id = {p.id: p for p in config.preguntas}
    secciones_por_id = {s.id: s for s in config.secciones}
    obligaciones_por_id = {o.id: o for o in config.obligaciones}

    organization = await db.get(Organization, diagnostic.organization_id)

    findings = (
        (
            await db.execute(
                select(Finding).where(
                    Finding.diagnostic_id == diagnostic.id,
                    Finding.status != FindingStatus.cerrado,
                )
            )
        )
        .scalars()
        .all()
    )
    answers = (
        (
            await db.execute(
                select(DiagnosticAnswer).where(
                    DiagnosticAnswer.diagnostic_id == diagnostic.id
                )
            )
        )
        .scalars()
        .all()
    )

    contexto_libre = "\n".join(
        f"{preguntas_por_id[a.pregunta_id].texto}: {a.notes}"
        for a in answers
        if a.notes and a.pregunta_id in preguntas_por_id
    )

    hallazgos_contexto = []
    for f in findings:
        pregunta = preguntas_por_id.get(f.pregunta_id) if f.pregunta_id else None
        seccion = secciones_por_id.get(pregunta.seccion_id) if pregunta else None
        obligacion = obligaciones_por_id.get(seccion.obligacion_id) if seccion else None
        hallazgos_contexto.append(
            {
                "finding_id": str(f.id),
                "descripcion": f.description,
                "riesgo": f.risk.value.capitalize(),
                "seccion": seccion.nombre if seccion else None,
                "obligacion": obligacion.nombre if obligacion else None,
            }
        )

    query_rag = (
        "; ".join(
            f"{h['obligacion']} - {h['seccion']} - {h['descripcion']}"
            for h in hallazgos_contexto
            if h["obligacion"]
        )
        or "Ley 21.719 protección de datos personales cumplimiento"
    )
    fragmentos = await search_chunks(query_rag, db, top_k=12, sources=FUENTES_ANCLAJE)
    fragmentos_prompt = [
        {
            "source": frag["source"],
            "reference": frag["reference"],
            "content": frag["content"],
        }
        for frag in fragmentos
    ]

    system_prompt = (
        "Eres un asistente que redacta la narrativa de un informe de "
        "cumplimiento de la Ley N° 21.719 de Protección de Datos Personales "
        "de Chile, para una PYME. Reglas estrictas:\n"
        "1. No inventes fragmentos legales ni cites nada que no esté en los "
        "fragmentos entregados. Cada cita debe usar exactamente el 'source' "
        "y 'reference' de un fragmento entregado.\n"
        "2. El nivel de riesgo y la obligación de cada hallazgo YA vienen "
        "calculados — no los recalcules ni los contradigas, solo redacta "
        "sobre ellos.\n"
        "3. Si no hay un fragmento relevante para un hallazgo, escribe la "
        "narrativa igual mencionándolo, pero sin inventar una cita.\n"
        "4. Escribe en español de Chile, en un tono profesional y directo.\n"
        "5. NUNCA menciones en el resumen ejecutivo una cifra total de "
        "brechas/hallazgos (ej. 'se detectaron 12 brechas'): ese conteo ya "
        "se muestra de forma exacta en otra sección del informe, calculado "
        "por el sistema, no por ti. Si necesitas referirte a la cantidad, "
        "usa términos generales ('varias brechas de riesgo alto', 'la "
        "mayoría de los hallazgos'), nunca un número."
    )

    perfil = (
        f"Rubro: {organization.industry or 'no informado'}; "
        f"tamaño: {organization.size or 'no informado'}."
    )
    puntaje_texto = (
        "Puntaje global: "
        f"{diagnostic.global_score if diagnostic.global_score is not None else 'sin calcular'}."
    )
    hallazgos_texto = (
        "\n".join(
            f"- [{h['finding_id']}] Riesgo {h['riesgo']} — Obligación: {h['obligacion']} "
            f"— Sección: {h['seccion']} — {h['descripcion']}"
            for h in hallazgos_contexto
        )
        or "Sin brechas abiertas: el diagnóstico no detectó hallazgos pendientes."
    )
    fragmentos_texto = (
        "\n".join(
            f"[{f['source']} | {f['reference']}] {f['content']}"
            for f in fragmentos_prompt
        )
        or "No se recuperaron fragmentos relevantes."
    )
    contexto_libre_texto = (
        contexto_libre or "La organización no agregó contexto adicional."
    )

    user_prompt = (
        f"Perfil de la organización: {perfil}\n{puntaje_texto}\n\n"
        f"Hallazgos (brechas abiertas):\n{hallazgos_texto}\n\n"
        "Contexto adicional que agregó la organización:\n"
        f"{contexto_libre_texto}\n\n"
        "Fragmentos legales recuperados (cita SOLO con estos, usando su "
        f"source y reference exactos):\n{fragmentos_texto}\n\n"
        "Redacta el resumen ejecutivo y, para cada hallazgo listado arriba "
        "(usa su finding_id exacto), una narrativa breve citando los "
        "fragmentos relevantes si existen."
    )

    llm = get_llm_client(get_settings())
    resultado = await llm.generate_structured(
        system=system_prompt,
        prompt=user_prompt,
        schema=_INFORME_SCHEMA,
        tool_name="informe_diagnostico",
    )

    fragmentos_validos = {(f["source"], f["reference"]) for f in fragmentos_prompt}
    finding_ids_validos = {h["finding_id"] for h in hallazgos_contexto}

    narrativas_saneadas = []
    for item in resultado.get("narrativas", []):
        finding_id = item.get("finding_id")
        if finding_id not in finding_ids_validos:
            logger.warning(
                "Descartando narrativa con finding_id desconocido: %s", finding_id
            )
            continue
        citas_originales = item.get("citas", [])
        citas_validas = [
            c
            for c in citas_originales
            if (c.get("source"), c.get("reference")) in fragmentos_validos
        ]
        if len(citas_validas) != len(citas_originales):
            logger.warning(
                "Descartando %d cita(s) sin fragmento recuperado real para el "
                "hallazgo %s",
                len(citas_originales) - len(citas_validas),
                finding_id,
            )
        narrativas_saneadas.append(
            {
                "finding_id": finding_id,
                "narrativa": item.get("narrativa", ""),
                "citas": citas_validas,
            }
        )

    informe = {
        "resumen_ejecutivo": _quitar_conteo_de_brechas(
            resultado.get("resumen_ejecutivo", "")
        ),
        "narrativas": narrativas_saneadas,
    }

    diagnostic.informe_ia = informe
    diagnostic.informe_generado_en = datetime.now(UTC)

    return informe
