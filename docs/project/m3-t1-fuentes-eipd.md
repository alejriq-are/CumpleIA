# M3-T1 — Inventario inicial de fuentes EIPD

Consulta: 2026-10-13. Estado: EN PROGRESO; matriz revisable, sin habilitacion.
Baseline del proyecto: Ley 21.719/Ley 19.628 reformada, independiente de calendario.

## Fuente oficial localizada

[BCN — Ley 21.719](https://www.bcn.cl/leychile/navegar?idNorma=1209272).
[PDF oficial consultado](https://nuevo.leychile.cl/servicios/Consulta/Exportar?exportar_con_notas_al_pie=False&exportar_con_notas_bcn=False&exportar_con_notas_originales=False&exportar_formato=pdf&hddResultadoExportar=1209272.2026-12-01.0.0%23&nombrearchivo=Ley-21719_13-DIC-2024&radioExportar=Normas).
PDF de 42 paginas, generado 12-Oct-2026; publicacion 13-DIC-2024; ultima modificacion
indicada 05-FEB-2026, Ley 21.806; version diferida 01-DIC-2026. Fecha de generacion
no equivale a fecha de publicacion. Vista HTML no entrego texto; PDF si fue legible.

Articulo 15 ter, paginas 13-14: evaluacion previa cuando sea probable alto riesgo;
incluye supuestos que siempre la requieren. Preve lista orientativa y orientaciones
minimas de la Agencia, y permite consulta para recomendaciones ante alto riesgo.
La consulta no se interpreta aqui como autorizacion automatica ni requisito universal.

## Matriz fuente / contrato / brecha

| Tema | Fuente o evidencia | Relacion con implementacion | Pendiente |
| --- | --- | --- | --- |
| Evaluacion previa | Art. 15 ter localizado | performed_before_processing y prior_assessment_analysis | Analisis juridico por ruta y expediente |
| Operaciones, finalidad, necesidad/proporcionalidad, riesgos/mitigacion | Art. 15 ter localizado | campos y listas del documento EIPD | Trazabilidad de cada criterio; no equivalencia legal de todos los campos |
| Lista y orientaciones de Agencia | Prevision en art. 15 ter | official_sources | Identificar instrumento publicado, version y alcance |
| Consulta a Agencia | Art. 15 ter localizado | agency_consultation | Aplicabilidad concreta y evidencia, sin presumir respuesta |
| Fuentes de politica | SourceRecordV1 interno | Emisor, instrumento, URL, version, fecha, rutas, verificacion y responsable | Registro verificable completo; no inventar verified_by |
| Aceptacion de politica | EipdGatePolicyV1 interno | Referencia, commit, evidencia y responsable | Aceptacion real documentada; los tests no la sustituyen |

Busqueda limitada en BCN, dominios gubernamentales y Diario Oficial: no se identifico
en los resultados revisados una publicacion especifica de lista/orientaciones EIPD.
Esto no demuestra inexistencia. No marcar no_aplicable por ausencia en buscador.
No adoptar guias extranjeras o blogs como instrumentos chilenos vinculantes.

## Resultado y siguiente paso

Fuente legal localizada, no conjunto de fuentes declarado verificado. Requisitos de
contrato son condiciones del producto; distinguirlos de obligaciones legales.
Preparar revision de aplicabilidad de rutas sensible_derechos y
sensible_biometrica_derechos contra articulos especificos y evidencia de Agencia.
Politica y expediente sin cambios: sources/acceptance pendientes; activation
deshabilitada; confirmacion/activacion bloqueadas. No tests por cambio documental.
