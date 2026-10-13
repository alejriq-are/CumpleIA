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

## Trazabilidad de campos de excepciones — §205

Revision estatica 2026-10-13 de tests existentes; no ejecucion nueva ni cobertura
medida por herramienta. Referencias en backend/tests/. No confundir prueba localizada
con prueba aprobada en esta etapa o aceptacion documental.

| Campos/grupo | Prueba localizada | Tipo de asercion revisado |
| --- | --- | --- |
| context_reference, purpose_description, right_description, right_basis_reference, holder_connection_analysis, forum_description, proceeding_reference, processing_operations, necessity_analysis, data_minimization_analysis, safeguards_analysis | Ambos test_services_*rights_exception.py: CONTEXT_TEXTS / test_required_texts | Cada texto mutado a None, vacio y espacios |
| sensitive_data_description, exception_application_analysis | test_services_sensitive_rights_exception.py: OWN_TEXTS / test_required_texts | Texto obligatorio e incompleto |
| biometric_data_description, unique_identification_analysis, exception_application_analysis, sensitive_context_connection_analysis, systems_coverage_analysis | test_services_biometric_rights_exception.py: OWN_TEXTS / test_required_texts | Texto obligatorio e incompleto |
| route, forum_type, proceeding_stage, right_holder, exception_basis | test_required_enums / test_missing_enums; supported routes/forums/stages/holder | Enumeraciones y combinaciones: revisar ramas completas antes de certificar |
| preparatory_actions, post_proceeding_necessity_analysis | test_applicable_stage_text_required, test_stage_residuality; test_stage_conditional_and_residuality | Exigencia segun etapa, residualidad |
| related_to_right, necessary_for_route, within_forum_scope, principles_addressed, exception_conditions_met | RESPONSES / test_required_responses de ambos servicios | Respuestas requeridas y categorias diagnosticas |
| unique_identification_confirmed, all_systems_documented | RESPONSES biometrico / test_required_responses | Respuestas requeridas |
| scope: categorias/titulares | test_scope_empty_invalid_or_duplicate, test_scope_partial_coverage_and_discordance; variantes biometricas | Alcance invalido/duplicado/incompleto y enlace sensible |
| evidence: documento/contexto/condicion/sistema | test_required_evidence de ambos servicios | Lista, tipo y referencia faltantes |
| system_reference/name/description, specific_purpose, purpose_alignment_analysis, use_period_description, retention_alignment_analysis, rights_exercise_description/contact_channel, information_reference | SYSTEM_TEXTS biometrico / test_required_texts | Campos del primer sistema mutados individualmente |
| system_identification_disclosed, purpose_disclosed, use_period_disclosed, rights_exercise_disclosed | RESPONSES biometrico / test_required_responses | Respuestas informativas del primer sistema |
| Sistemas multiples | test_unique_systems_and_information_of_every_system | Duplicado canonico y rights_contact_channel faltante en segundo sistema |

### Brecha delimitada para el proximo ensayo

La prueba localizada de multiples sistemas altera solo el canal de derechos del
segundo sistema. La matriz no acredita todavia omision individual de cada otro
texto/respuesta/evidencia en sistemas posteriores. Revisar el conjunto de tests
antes de agregar casos para evitar duplicacion; si falta cobertura, ampliar ensayo
parametrizado del segundo sistema con aserciones de campo e indice precisos.

Documento EIPD completo, fuentes y politica tienen suites propias: su trazabilidad
por campo no queda cerrada por esta matriz de excepciones. Todos los resultados de
aceptacion documental siguen pendientes; no codigo/datos/politica modificados.

## Segundo sistema: omisiones individuales — §206

Añadido test_second_system_omission_does_not_borrow_complete_first_system en
test_services_biometric_rights_exception.py: segundo sistema con referencia distinta,
primero completo. Quince casos: diez textos en espacios, cuatro respuestas ausentes y
lista de evidencia vacia. Cada caso exige incompleto, can_confirm falso y diagnostico
exacto systems.1; no motivos systems.0 ni mutacion de documento/primer sistema.

Modulo completo: 229 aprobadas en 0.59 s en base aislada verificada. Black y Ruff
aprobados. No cambio de evaluador, schema, politica o expediente operativo.
Queda cubierta esta brecha delimitada de omisiones; respuestas negativas/pendientes,
fundamentos y evidencia parcial en sistemas posteriores no se afirman cubiertos por
los quince casos. Aceptacion documental de todas las filas sigue pendiente.

## Respuestas y evidencia parcial del segundo sistema — §207

14 casos nuevos: cuatro respuestas informativas por no/pendiente/si sin fundamento
(12), tipo o referencia de evidencia en espacios (2). Diagnostico exacto systems.1
con categoria esperada, can_confirm falso, sin motivos del primero ni mutacion.
Modulo completo 243 aprobadas; base aislada verificada. Black/Ruff aprobados.
Brecha delimitada de §206 ampliada; no cobertura universal de combinaciones o indices.
Aceptacion documental sigue pendiente; evaluador y expediente operativo sin cambios.
