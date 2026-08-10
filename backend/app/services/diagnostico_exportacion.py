"""Exportación del informe del Autodiagnóstico (Fase 1, Módulo 1, Tarea 5).

Genera un documento HTML autocontenido (sin JS, con estilos embebidos) a
partir del `informe_ia` ya generado por `app/services/diagnostico_ia.py`
(Tarea 4) más los puntajes deterministas del motor de la Tarea 2. Empieza
simple a propósito (ver `Fase 1/plan-fase1-modulo1-autodiagnostico.md`,
Tarea 5): HTML imprimible a PDF desde el navegador, sin agregar una
dependencia nueva (WeasyPrint u otro motor de PDF) hasta que se necesite de
verdad. El Módulo 4 (generador de documentos Word/PDF pulido) no existe
todavía; conectar con él más adelante en vez de bloquear esta tarea.

Todo texto que no viene del catálogo fijo (nombre de organización, resumen
ejecutivo y narrativas redactadas por el LLM, descripción/acción
correctiva/responsable de un hallazgo, que puede incluir lo que la
organización escribió en `notes`) se escapa con `html.escape` antes de
insertarse: este documento se abre en un navegador, así que es una
superficie de XSS igual que cualquier otra página servida por la app.
"""

from html import escape

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Diagnostic, Finding, Organization
from app.services.cuestionario_config import obtener_config_por_id

_RISK_ORDEN = {"alto": 0, "medio": 1, "bajo": 2}


def _fmt_score(score: float | None) -> str:
    return f"{score:.0f}" if score is not None else "s/i"


async def generar_html_informe(db: AsyncSession, diagnostic: Diagnostic) -> str:
    """Construye el HTML del informe. Asume `diagnostic.informe_ia` ya generado
    (el router es responsable de devolver 409 si es `None` antes de llamar
    esta función — ver `app/services/diagnostico_ia.py::generar_informe`, que
    aplica la misma separación de responsabilidad para el 409 de "no
    completado")."""
    informe_ia = diagnostic.informe_ia or {}
    config = await obtener_config_por_id(db, diagnostic.config_version_id)
    organization = await db.get(Organization, diagnostic.organization_id)
    secciones_por_id = {s.id: s for s in config.secciones}
    preguntas_por_id = {p.id: p for p in config.preguntas}
    section_scores: dict = diagnostic.section_scores or {}

    findings = (
        (
            await db.execute(
                select(Finding).where(Finding.diagnostic_id == diagnostic.id)
            )
        )
        .scalars()
        .all()
    )
    narrativas_por_finding = {
        n["finding_id"]: n for n in informe_ia.get("narrativas", [])
    }

    def _orden_hallazgo(f: Finding) -> tuple[int, int]:
        pregunta = preguntas_por_id.get(f.pregunta_id) if f.pregunta_id else None
        seccion = secciones_por_id.get(pregunta.seccion_id) if pregunta else None
        return (_RISK_ORDEN.get(f.risk.value, 9), seccion.orden if seccion else 99)

    findings_ordenados = sorted(findings, key=_orden_hallazgo)

    filas_puntaje = "\n".join(
        f"<tr><td>{escape(s.numero_romano)}</td><td>{escape(s.nombre)}</td>"
        f"<td class='num'>{_fmt_score(section_scores.get(s.id))}</td></tr>"
        for s in sorted(config.secciones, key=lambda s: s.orden)
    )

    bloques_hallazgos = []
    for f in findings_ordenados:
        pregunta = preguntas_por_id.get(f.pregunta_id) if f.pregunta_id else None
        seccion = secciones_por_id.get(pregunta.seccion_id) if pregunta else None
        narrativa = narrativas_por_finding.get(str(f.id))
        citas_html = ""
        if narrativa and narrativa.get("citas"):
            citas_html = (
                "<ul class='citas'>"
                + "".join(
                    f"<li>{escape(c['source'])} — {escape(c['reference'])}</li>"
                    for c in narrativa["citas"]
                )
                + "</ul>"
            )
        narrativa_html = (
            f"<p class='narrativa'>{escape(narrativa['narrativa'])}</p>{citas_html}"
            if narrativa
            else ""
        )
        bloques_hallazgos.append(
            "<div class='hallazgo risk-{riesgo_clase}'>"
            "<div class='hallazgo-header'>"
            "<span class='riesgo'>Riesgo {riesgo}</span>"
            "<span class='estado'>{estado}</span>"
            "</div>"
            "<p class='seccion'>{seccion}</p>"
            "<p class='descripcion'>{descripcion}</p>"
            "{narrativa_html}"
            "{accion}"
            "{responsable}"
            "</div>".format(
                riesgo_clase=escape(f.risk.value),
                riesgo=escape(f.risk.value.capitalize()),
                estado=escape(f.status.value.capitalize()),
                seccion=escape(seccion.nombre if seccion else "Sección desconocida"),
                descripcion=escape(f.description),
                narrativa_html=narrativa_html,
                accion=(
                    f"<p class='meta'><strong>Acción correctiva:</strong> "
                    f"{escape(f.corrective_action)}</p>"
                    if f.corrective_action
                    else ""
                ),
                responsable=(
                    f"<p class='meta'><strong>Responsable:</strong> "
                    f"{escape(f.responsible)}</p>"
                    if f.responsible
                    else ""
                ),
            )
        )

    generado_en = (
        diagnostic.informe_generado_en.strftime("%d-%m-%Y %H:%M")
        if diagnostic.informe_generado_en
        else "s/i"
    )
    organizacion_nombre = escape(organization.name) if organization else "Organización"
    resumen_ejecutivo_html = "".join(
        f"<p>{escape(parrafo)}</p>"
        for parrafo in informe_ia.get("resumen_ejecutivo", "").split("\n")
        if parrafo.strip()
    )

    return f"""<!DOCTYPE html>
<html lang="es-CL">
<head>
<meta charset="utf-8">
<title>Informe de Autodiagnóstico — {organizacion_nombre}</title>
<style>
  body {{ font-family: Arial, Helvetica, sans-serif; color: #1a1a1a; margin: 2rem; line-height: 1.5; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 0; }}
  h2 {{ font-size: 1.2rem; border-bottom: 2px solid #1a1a1a; padding-bottom: 0.25rem; margin-top: 2rem; }}
  .subtitulo {{ color: #555; margin-top: 0.25rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 0.75rem; }}
  th, td {{ text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #ddd; }}
  td.num, th.num {{ text-align: right; }}
  .hallazgo {{ border-left: 4px solid #999; padding: 0.6rem 1rem; margin: 0.75rem 0; background: #fafafa; }}
  .hallazgo.risk-alto {{ border-left-color: #b91c1c; }}
  .hallazgo.risk-medio {{ border-left-color: #b45309; }}
  .hallazgo.risk-bajo {{ border-left-color: #15803d; }}
  .hallazgo-header {{ display: flex; justify-content: space-between; font-weight: bold; }}
  .seccion {{ color: #555; margin: 0.2rem 0; }}
  .narrativa {{ margin: 0.5rem 0; }}
  .meta {{ margin: 0.2rem 0; }}
  ul.citas {{ margin: 0.3rem 0 0.6rem 1.2rem; color: #444; font-size: 0.9rem; }}
  .global-score {{ font-size: 2rem; font-weight: bold; }}
  footer {{ margin-top: 2rem; padding-top: 0.75rem; border-top: 1px solid #ddd; color: #777; font-size: 0.85rem; }}
  @media print {{ body {{ margin: 0.5in; }} }}
</style>
</head>
<body>
<h1>Informe de Autodiagnóstico — Ley N.° 21.719</h1>
<p class="subtitulo">{organizacion_nombre} · Generado el {escape(generado_en)}</p>

<h2>Puntaje global</h2>
<p class="global-score">{_fmt_score(
        float(diagnostic.global_score) if diagnostic.global_score is not None else None
    )} / 100</p>

<h2>Puntaje por sección</h2>
<table>
<thead><tr><th>N.°</th><th>Sección</th><th class="num">Puntaje</th></tr></thead>
<tbody>
{filas_puntaje}
</tbody>
</table>

<h2>Resumen ejecutivo</h2>
{resumen_ejecutivo_html or "<p>Sin resumen disponible.</p>"}

<h2>Hallazgos</h2>
{"".join(bloques_hallazgos) or "<p>El diagnóstico no registra hallazgos.</p>"}

<footer>
Documento generado automáticamente por CumpleIA a partir del Autodiagnóstico
de cumplimiento de la Ley N.° 21.719. Su contenido debe ser validado por el
responsable correspondiente antes de ser utilizado como evidencia formal de
cumplimiento.
</footer>
</body>
</html>
"""
