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
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Diagnostic,
    DiagnosticAnswer,
    Finding,
    Membership,
    Organization,
    Profile,
)
from app.services.cuestionario_config import obtener_config_por_id

_RISK_ORDEN = {"alto": 0, "medio": 1, "bajo": 2}

# `informe_generado_en` se guarda en UTC (`datetime.now(UTC)`,
# app/services/diagnostico_ia.py) — sin convertir a la hora de Chile antes de
# formatear, el informe mostraba la hora UTC como si fuera local (hasta 4h de
# diferencia). CumpleIA es un producto solo para Chile (ver CLAUDE.md), así
# que la zona se fija aquí en vez de derivarla de algo configurable.
_TZ_CHILE = ZoneInfo("America/Santiago")

# "Cargo" de quien respondió (mejora al informe, ver
# Claude_22_julio_2026/mejoras-informe-autodiagnostico.md, ítem 1): no existe
# un campo de puesto/cargo real en Profile todavía, así que se usa el rol de
# membresía en la organización como proxy — aproximado, pero es el único dato
# organizacional disponible hoy sin agregar un campo nuevo.
_ROL_DISPLAY = {
    "owner": "Propietario/a",
    "admin": "Administrador/a",
    "editor": "Editor/a",
    "viewer": "Colaborador/a",
}

# Etiquetas de tamaño (pedido explícito del usuario, 2026-08-10): "pequeña" y
# "mediana" llevan la sigla "(PYME)" — "micro" y "grande" no, a propósito, no
# es la clasificación MIPYME formal chilena (que sí incluye a la micro).
_TAMANO_DISPLAY = {
    "micro": "Micro empresa",
    "pequeña": "Pequeña empresa (PYME)",
    "mediana": "Mediana empresa (PYME)",
    "grande": "Gran Empresa",
}
_TAMANOS_PYME = {"pequeña", "mediana"}


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
    respuestas_por_pregunta = {a.pregunta_id: a.answer for a in answers}

    # Quién respondió (mejora al informe, ítem 1): el último perfil que
    # guardó respuestas (`updated_by`, ver migración 0008) — no quien inició
    # el diagnóstico si alguien más lo completó después.
    respondedor = (
        await db.get(Profile, diagnostic.updated_by) if diagnostic.updated_by else None
    )
    cargo_respondedor = None
    if respondedor is not None:
        membership = (
            await db.execute(
                select(Membership).where(
                    Membership.organization_id == diagnostic.organization_id,
                    Membership.profile_id == respondedor.id,
                )
            )
        ).scalar_one_or_none()
        if membership is not None:
            cargo_respondedor = _ROL_DISPLAY.get(
                membership.role.value, membership.role.value
            )

    def _orden_hallazgo(f: Finding) -> tuple[int, int]:
        pregunta = preguntas_por_id.get(f.pregunta_id) if f.pregunta_id else None
        seccion = secciones_por_id.get(pregunta.seccion_id) if pregunta else None
        return (_RISK_ORDEN.get(f.risk.value, 9), seccion.orden if seccion else 99)

    findings_ordenados = sorted(findings, key=_orden_hallazgo)

    # Conteo por riesgo (BUG-01 / ítem 2): fuente determinista única del
    # total de brechas abiertas — el resumen ejecutivo del LLM tiene
    # instrucción explícita de NO declarar esta cifra
    # (app/services/diagnostico_ia.py) para no tener dos números que puedan
    # no coincidir.
    abiertos = [f for f in findings if f.status.value != "cerrado"]
    conteo_riesgo = {"alto": 0, "medio": 0, "bajo": 0}
    for f in abiertos:
        conteo_riesgo[f.risk.value] = conteo_riesgo.get(f.risk.value, 0) + 1

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

        # Respuesta + riesgo base/ajustado (mejora al informe, ítem 3): una
        # respuesta 'Parcial' degrada el riesgo un nivel respecto al base del
        # catálogo (ver app/services/diagnostico_puntaje.py::detectar_brechas)
        # — sin esto no se entiende por qué una pregunta de riesgo base Alto
        # puede aparecer como hallazgo Medio.
        answer = respuestas_por_pregunta.get(f.pregunta_id) if f.pregunta_id else None
        riesgo_base = (
            config.riesgo_por_pregunta.get(f.pregunta_id) if f.pregunta_id else None
        )
        riesgo_ajustado = f.risk.value.capitalize()
        if answer == "Parcial" and riesgo_base and riesgo_base != riesgo_ajustado:
            riesgo_texto = (
                f"Riesgo {escape(riesgo_ajustado)} — base {escape(riesgo_base)}, "
                "ajustado por respuesta Parcial"
            )
        else:
            riesgo_texto = f"Riesgo {escape(riesgo_ajustado)}"

        bloques_hallazgos.append(
            "<div class='hallazgo risk-{riesgo_clase}'>"
            "<div class='hallazgo-header'>"
            "<span class='riesgo'>{riesgo_texto}</span>"
            "<span class='estado'>{estado}</span>"
            "</div>"
            "<p class='seccion'>{seccion}</p>"
            "<p class='descripcion'>{descripcion}</p>"
            "{respuesta}"
            "{narrativa_html}"
            "{accion}"
            "{responsable}"
            "</div>".format(
                riesgo_clase=escape(f.risk.value),
                riesgo_texto=riesgo_texto,
                estado=escape(f.status.value.capitalize()),
                seccion=escape(seccion.nombre if seccion else "Sección desconocida"),
                descripcion=escape(f.description),
                respuesta=(
                    f"<p class='meta'><strong>Respuesta:</strong> {escape(answer)}</p>"
                    if answer
                    else ""
                ),
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
        diagnostic.informe_generado_en.astimezone(_TZ_CHILE).strftime("%d-%m-%Y %H:%M")
        if diagnostic.informe_generado_en
        else "s/i"
    )
    organizacion_nombre = escape(organization.name) if organization else "Organización"
    resumen_ejecutivo_html = "".join(
        f"<p>{escape(parrafo)}</p>"
        for parrafo in informe_ia.get("resumen_ejecutivo", "").split("\n")
        if parrafo.strip()
    )

    # Encabezado de identificación (mejora al informe, ítem 1): rubro/tamaño
    # importan porque la Ley 21.719 trata distinto a la PYME; "Tamaño" es el
    # valor libre que la organización declaró al crear su cuenta
    # (`organizations.size`), no una clasificación automática por umbral
    # legal — esa clasificación no existe todavía (ver docs/backlog.md).
    rut_texto = escape(organization.rut) if organization and organization.rut else "s/i"
    industry_texto = (
        escape(organization.industry)
        if organization and organization.industry
        else "s/i"
    )
    size_texto = (
        escape(_TAMANO_DISPLAY.get(organization.size, organization.size))
        if organization and organization.size
        else "s/i"
    )
    respondedor_texto = (
        escape(respondedor.full_name or respondedor.email) if respondedor else "s/i"
    )
    if respondedor is not None and cargo_respondedor:
        respondedor_texto = f"{respondedor_texto} ({escape(cargo_respondedor)})"

    identificacion_html = f"""<table class="identificacion">
<tr><td>Organización</td><td>{organizacion_nombre}</td></tr>
<tr><td>RUT</td><td>{rut_texto}</td></tr>
<tr><td>Rubro</td><td>{industry_texto}</td></tr>
<tr><td>Tamaño</td><td>{size_texto}</td></tr>
<tr><td>Respondido por</td><td>{respondedor_texto}</td></tr>
<tr><td>ID de diagnóstico</td><td>{diagnostic.id}</td></tr>
<tr><td>Fecha de generación</td><td>{escape(generado_en)}</td></tr>
</table>"""

    # Upsell para PYME (pedido explícito del usuario, 2026-08-10): no es parte
    # del contenido probatorio del informe, es una sugerencia comercial — solo
    # se muestra si el tamaño declarado es "pequeña" o "mediana".
    aviso_pyme_html = ""
    if organization and organization.size in _TAMANOS_PYME:
        aviso_pyme_html = """<div class="aviso-pyme">
<strong>¿Sabías que...?</strong> Como empresa PYME, CumpleIA puede asesorarte en la
implementación de tu programa de cumplimiento de la Ley N.° 21.719 — desde la definición
de políticas hasta la designación de un Delegado de Protección de Datos.
</div>"""

    conteo_riesgo_html = f"""<div class="conteo-riesgo">
<div class="conteo-item risk-alto"><span class="conteo-numero">{conteo_riesgo["alto"]}</span><span>Alto</span></div>
<div class="conteo-item risk-medio"><span class="conteo-numero">{conteo_riesgo["medio"]}</span><span>Medio</span></div>
<div class="conteo-item risk-bajo"><span class="conteo-numero">{conteo_riesgo["bajo"]}</span><span>Bajo</span></div>
<div class="conteo-item conteo-total"><span class="conteo-numero">{len(abiertos)}</span><span>Total abiertos</span></div>
</div>"""

    # Estático (no depende de datos del diagnóstico): explica la escala de
    # respuesta y la regla de degradación de riesgo para que un fiscalizador
    # o auditor externo entienda por qué un hallazgo de riesgo base Alto
    # puede aparecer como Medio (mejora al informe, ítem 3).
    metodologia_html = """<p>Cada pregunta se responde con una de estas opciones:
<strong>Sí</strong>, <strong>Parcial</strong>, <strong>No</strong> o <strong>N/A</strong> (no aplica).
El puntaje de cada sección es el promedio de sus preguntas respondidas — <strong>Sí</strong> = 100%,
<strong>Parcial</strong> = 50%, <strong>No</strong> = 0%; las preguntas en <strong>N/A</strong> se
excluyen del promedio. Una respuesta <strong>No</strong> abre un hallazgo con el riesgo base de la
pregunta (Alto, Medio o Bajo, según el catálogo); una respuesta <strong>Parcial</strong> abre un
hallazgo un nivel de riesgo por debajo del base (Alto→Medio, Medio→Bajo, Bajo se mantiene en Bajo).
Las respuestas Sí y N/A no generan hallazgos.</p>
<table>
<thead><tr><th>Respuesta</th><th class="num">Puntaje</th><th>¿Genera hallazgo?</th><th>Riesgo del hallazgo</th></tr></thead>
<tbody>
<tr><td>Sí</td><td class="num">100%</td><td>No</td><td>—</td></tr>
<tr><td>Parcial</td><td class="num">50%</td><td>Sí</td><td>Un nivel bajo el riesgo base</td></tr>
<tr><td>No</td><td class="num">0%</td><td>Sí</td><td>Riesgo base de la pregunta</td></tr>
<tr><td>N/A</td><td class="num">excluida</td><td>No</td><td>—</td></tr>
</tbody>
</table>"""

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
  .identificacion td:first-child {{ color: #555; width: 40%; }}
  .conteo-riesgo {{ display: flex; gap: 1rem; margin-top: 0.75rem; }}
  .conteo-item {{ flex: 1; border: 1px solid #ddd; border-left: 4px solid #999; border-radius: 4px; padding: 0.6rem 1rem; text-align: center; }}
  .conteo-item.risk-alto {{ border-left-color: #b91c1c; }}
  .conteo-item.risk-medio {{ border-left-color: #b45309; }}
  .conteo-item.risk-bajo {{ border-left-color: #15803d; }}
  .conteo-item.conteo-total {{ border-left-color: #1a1a1a; }}
  .conteo-numero {{ display: block; font-size: 1.5rem; font-weight: bold; }}
  .aviso-pyme {{ margin-top: 0.75rem; border: 1px solid #bfdbfe; background: #eff6ff; border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.9rem; color: #1e3a8a; }}
  footer {{ margin-top: 2rem; padding-top: 0.75rem; border-top: 1px solid #ddd; color: #777; font-size: 0.85rem; }}
  @media print {{ body {{ margin: 0.5in; }} }}
</style>
</head>
<body>
<h1>Informe de Autodiagnóstico — Ley N.° 21.719</h1>
<p class="subtitulo">{organizacion_nombre} · Generado el {escape(generado_en)}</p>

{identificacion_html}
{aviso_pyme_html}

<h2>Puntaje global</h2>
<p class="global-score">{_fmt_score(
        float(diagnostic.global_score) if diagnostic.global_score is not None else None
    )} / 100</p>

<h2>Hallazgos abiertos por riesgo</h2>
{conteo_riesgo_html}

<h2>Puntaje por sección</h2>
<table>
<thead><tr><th>N.°</th><th>Sección</th><th class="num">Puntaje</th></tr></thead>
<tbody>
{filas_puntaje}
</tbody>
</table>

<h2>Resumen ejecutivo</h2>
{resumen_ejecutivo_html or "<p>Sin resumen disponible.</p>"}

<h2>Metodología</h2>
{metodologia_html}

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
