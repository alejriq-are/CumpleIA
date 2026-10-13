# M3-T1 — Evidencias revisables por ruta EIPD

Fecha: 2026-10-13. EN PROGRESO. Lista de revision del contrato del producto, no lista
universal de obligaciones legales ni aprobacion. Fundamento normativo se conserva
en [inventario de fuentes](m3-t1-fuentes-eipd.md). Politica deshabilitada.

## Forma de registrar la revision

Por cada punto: referencia documental/version, alcance, analisis, resultado
(pendiente / evidencia aportada / revisada con observaciones / aceptacion documentada),
responsable y fecha. Todos los puntos comienzan pendientes. Ejemplos de evidencia
son orientativos: su mera existencia no acredita condiciones ni autenticidad.
No inventar nombres, UUID de revisores, firmas, procedimientos o documentos reales.

| Punto | Campos del contrato | Evidencia candidata para revisar | Resultado inicial |
| --- | --- | --- | --- |
| Identidad y alcance | context_reference, purpose_description, scope | Referencia de expediente y correspondencia con finalidad/categorias/titulares RAT | Pendiente |
| Derecho y relacion | route, right_description, right_basis_reference, right_holder, holder_connection_analysis | Antecedente que describa derecho y relacion con titular/responsable | Pendiente |
| Foro y etapa | forum_type, forum_description, proceeding_stage, proceeding_reference, preparatory_actions | Referencia de actuacion y explicacion de etapa, incluida preparacion | Pendiente |
| Operaciones y necesidad | processing_operations, necessity_analysis, related_to_right, necessary_for_route, within_forum_scope | Analisis concreto de operaciones, necesidad y alcance | Pendiente |
| Minimizacion y resguardos | data_minimization_analysis, safeguards_analysis, principles_addressed | Analisis y evidencias de controles aplicados al caso | Pendiente |
| Continuidad posterior | post_proceeding_necessity_analysis | Justificacion cuando corresponda a etapa finalizada, segun evaluador | Pendiente |
| Ruta sensible | sensitive_data_description, exception_basis, exception_application_analysis, exception_conditions_met, evidence | Descripcion y analisis de excepcion sobre categorias cubiertas | Pendiente |
| Ruta biometrica | biometric_data_description, unique_identification_analysis, unique_identification_confirmed, sensitive_context_connection_analysis | Analisis de identificacion unica y conexion con contexto sensible | Pendiente |
| Sistemas biometricos | systems, systems_coverage_analysis, all_systems_documented | Inventario de sistemas y evidencia de cobertura | Pendiente |
| Informacion por sistema | system_reference/name/description, specific_purpose, use_period_description, rights_exercise_description/contact_channel, information_reference, evidence | Descripcion y material informativo con analisis de alineacion | Pendiente |
| Documento EIPD | EipdResolutionAssessmentV1 | Operaciones, riesgos, medidas, riesgo residual, fuentes y seguimiento del mismo alcance | Pendiente |
| Fuente y aceptacion de politica | SourceRecordV1 / EipdGatePolicyV1 | Referencias verificables, cobertura de rutas, responsable, commit y evidencia de aceptacion | Pendiente |

Fuente tecnica: backend/app/schemas/licitud.py (RightsExceptionContextV1,
SensitiveRightsExceptionAssessmentV1, BiometricRightsExceptionAssessmentV1,
BiometricSystemV1) y evaluadores correspondientes. Esta tabla agrupa campos;
no reemplaza los validadores ni enumera todas sus ramas condicionales.

## Condicion para el siguiente ensayo

Usar fixture sintetico dedicado de alcance admitido en base aislada, separado del
expediente de investigacion existente. Recorrer lista contra diagnósticos reales y
registrar campos/ramas no cubiertos. No rellenar fixture operativo con hechos ficticios
presentados como evidencia real. Aceptacion de fuentes y politica siguen pendientes;
ninguna fila se marca aceptada por pasar tests. Sin modificaciones de codigo/datos.

## Ensayo sintetico de frontera y requisitos — §204

2026-10-13: 60 pruebas existentes aprobadas en 9.23 s, base aislada verificada.

| Grupo de lista | Ensayo tecnico observado | Limite de evidencia |
| --- | --- | --- |
| Ruta sensible y biometrica | Prepared frontier HTTP parametrizado con biometric False/True y revision negativa previa/ausente | No verifica documentos reales ni aceptacion por responsable |
| Dependencias/vinculos | Cambios con commit/rollback durante bloqueo, revision/confirmacion releen dependencias | No ensayo humano simultaneo |
| Documento parcial o sin identidad vigente | Requisitos distinguen negativas y rechazan material ausente/no vinculado/obsoleto | Completitud documental no acredita fuente o frontera |
| Fuentes y politica | Documento preparado conserva barreras globales | No habilita politica operativa |
| Riesgo residual y estado | Riesgo alto e inmutabilidad mantienen rechazos segun caso | No evaluacion externa de riesgo |
| Investigacion | Contexto completo conserva bloqueo; discordancia/obsolescencia visibles | No ampliar frontera para fixture operativo de investigacion |

Suites: test_api_eipd_prepared_frontier.py, test_eipd_frontier_v2.py y
test_eipd_resolution_review_prerequisites.py. Fixtures reutilizados de pruebas,
separados del expediente operativo; sin nuevos schemas o datos operativos.
No cobertura individual de cada campo de la lista por esta corrida. Todas las filas
de aceptacion documental anteriores siguen pendientes. Proximo: detectar campos
sin trazabilidad de prueba especifica y preparar matriz de cobertura, sin repetir
estos casos salvo cambio o fallo.
