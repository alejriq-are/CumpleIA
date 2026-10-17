# M3-T1 §143 — Frontera, screening y composicion de investigacion

## Revision de codigo y limite actual

HEAD bb3e941. EipdFrontierReadinessV1 solo admite rutas sensible_derechos,
sensible_biometrica_derechos/sin_resolver y ContextV1. EipdReadinessV2 usa esa frontera.
Composicion InputV1 y InputV2 contienen ContextV1/StoredV1; no cubren research.
Funciones puras de resolucion/revision versionadas §142 ya admiten material V2,
pero no estan conectadas a API. No quitar campos V2 para simular cobertura V1.
Ley fija, M3-T1 EN PROGRESO y confirmacion/activacion EIPD bloqueadas.

## Contratos sucesores previstos

- EipdFrontierReadinessV2 y evaluate_eipd_frontier_v2: ContextV2 cerrado; ruta
  investigacion_no_sensible_adultos o sin_resolver en este incremento. Conservar
  FrontierV1 para sus rutas anteriores, sin atribuirles investigacion. Salida incluye
  readiness research y asociacion, special/screening completos y motivos acumulados.
- EipdReadinessV3 y evaluate_eipd_screening_v3: evaluation_version Literal[3];
  contexto V2 y frontera V2. No confundir evaluation_version 3 con binding_version
  12 del screening documental. Mantener ScreeningV2 intacto para ContextV1.
- EipdControlCompositionInputV3 / CompositionV3: campos de identidad/estado/RAT de
  servidor, ContextV2, resolucion StoredV1 o StoredV2 con dispatch cerrado, ultimo
  evento y politica/identidad reales con contratos existentes. No extender InputV1
  ni InputV2. composition_version Literal[3] en resultado y permiso fijo false.

Entrada V3 de resolucion permite V1 expresamente para diagnosticar falta de cobertura,
no para aprobarla. Ninguna nueva union acepta version desconocida o metadatos libres.
Los schemas HTTP sucesores se agregaran solo cuando se conecte lectura/escritura.

## Frontera pura de investigacion

Primero revalidar ContextV2 completo y calcular resultado research de completitud y
asociacion con RAT/base/LIA finales. Alcance inicial mantiene interes_legitimo_art13d,
LIA preparada, RAT no sensible y titulares adultos no vulnerables; las demas rutas
requieren revision. Revisar rol responsable y alcance/finalidad sin inventar criterios
normativos nuevos. No interpretar un expediente aportado como declaracion especial
negativa o como aceptacion de excepcion legal.

Ejecutar evaluadores especiales y screening con research completo y base explicita.
Verificar especiales V11 y screening V12; versiones anteriores con research requieren
revision, asociaciones obsoletas se conservan. Reconciliar presencia del expediente,
declaracion de fines investigacion y condicion/alcance declarados: discordancias
requieren revision, nunca seleccionar automaticamente una ruta de autorizacion.

Acumular incompletitud, obsolescencia y falta de cobertura, sin filtrar otros motivos
sensibles/infancia/biometria o EIPD. validador_no_implementado y bloqueos historicos
siguen visibles. En el primer incremento frontera V2 no se declara preparada mientras
ese validador no este integrado/revisado; completitud research se muestra separada.
No puede confirmar ni habilitar una politica; no aceptar flags preparados del cliente.

## Screening V3 y composicion V3

Screening V3 transmite ContextV2 sin proyeccion, siempre legal_basis y research.
Conserva deteccion EIPD y motivos completos de screening, con frontera documental
separada. No convertir pendiente_revision/requiere_eipd en exencion por expediente
completo; ninguna preparacion autoriza confirmacion. No extender prepared_exceptions
para investigacion en este primer incremento.

Composicion V3 evalua identidad tenant/assessment y estado, RAT actual, base ordinaria,
frontera/screening, research, resolucion versionada, revision y politica. Orden de
etapas nuevo y fijo que incluya research, sin modificar STAGES de composicion V1/V2.
Reusar evaluadores puros de bases ordinarias, pero no componer V2 sobre material
proyectado sin declarar cobertura pendiente. Diferenciar coincidencia de hashes,
preparacion documental, decision humana e identidad/politica; ninguna sustituye otra.

Revision V1 con research permanece visible pero obsoleta/no cubierta. Revision V2
vigente aun debe cumplir controles de identidad, documento completo, research vigente,
RAT vigente y politica; decision continuar no activa gate por si sola. Politica
actual deshabilitada/fuentes y aceptacion pendientes conserva bloqueo. Nuevos tipos
no crean politica, evento ni actor/fecha. Si contexto ausente, resultados cerrados de
incompletitud/revision, nunca excepciones permisivas.

## Compatibilidad, API y eventos

Primero funciones/contratos puros y tests; luego integrar lectura versionada y decidir
metadatos de eventos y API V2 bajo locks. No introducir columnas ni backfill en este
paso. Conservacion V1/V2 de frontera/screening/composicion probada con fixtures fijas.
Historicos no reciben identidad V3 ni research sintetico. GET/readiness no escribe.
Contexto V2 sin research (null explicito) no se transforma en V1 silenciosamente:
frontera V2 informa ausencia/ruta sin resolver; caller selecciona dispatcher explicito.

## Pruebas y secuencia siguiente

1. Frontera V2 pura: material completo pero bloqueo conservador, ausencia/null,
   obsolescencia research, discordancia de declaraciones, datos sensibles/menores,
   cobertura antigua y coexistencia de motivos. Entradas cerradas y no mutacion.
2. Screening V3 y composicion V3 puros: deteccion conservada, identidad/estado/RAT,
   revision historica visible, politica bloqueada, orden determinista de motivos,
   can_confirm false y ninguna bandera externa preparada.
3. Lectura/API/resolucion V2 y metadatos de eventos con pruebas tenant/rollback/locks;
   reglas de seleccion/reaporte y contrato de salida definidos antes del escritor.
4. Aceptacion revisada y revision del validador especial antes de considerar habilitar.

Este paso documental no ejecuta suite nueva. Ultima validacion §142: 327 focalizadas
y 272 regresiones aprobadas. Sin codigo nuevo, migracion, cambio operacional ni
commit/push. Proximo: implementar frontera V2 pura con bloqueo conservador.

## 2026-10-09 — M3-T1 §144: frontera V2 pura de investigacion

Nuevo eipd_frontier_v2.py revalida ContextV2 cerrado y evalua research documental y
asociacion, rol responsable, especiales/screening con research y base finales.
Conserva motivos completos de evaluadores; detecta discordancia de declaracion y
alcance del expediente especial. Ruta investigacion_no_sensible_adultos identifica
candidato de alcance, no permiso ni preparacion; sensible/menores/null/base/rol fuera
de alcance mantienen sin_resolver. Contexto ausente produce incompleto.

Resultado mantiene can_confirm e is_frontier_prepared fijos false, y agrega bloqueo
investigacion_confirmacion_bloqueada aun con documento completo/asociaciones vigentes.
validador_no_implementado historico permanece visible. Ningun cambio al FrontierV1,
screening/composicion anteriores, API, eventos, politica o datos operacionales.

Diez casos nuevos: completo pero bloqueado/determinista/sin mutacion, cambios de
cuerpo o binding obsoletos, null, sensible, menores, declaracion negativa discordante,
alcance discordante, contexto ausente/version desconocida/extra/campo omitido y
asociaciones historicas especiales/screening con falta de cobertura acumulada.
Suite final focalizada aislada 337 aprobadas en 30.43 s. Black/Ruff/diff check aprobados.
No nueva suite HTTP ampliada porque modulo puro aun no conectado a API; ultimas
regresiones adicionales 272 §142. No migracion ni reparacion de hashes.

Proximo: screening V3 sobre frontera/contexto V2 y composicion V3 conservadora,
antes de integrar lectura/escritura API/metadatos de eventos y aceptacion revisada.
Ley fija, M3-T1 EN PROGRESO; confirmacion investigacion y activacion EIPD bloqueadas.
Sin commit/push.

## 2026-10-09 — M3-T1 §145: screening V3 conservador

Nuevo eipd_screening_v3.py consume frontera V2, que revalida ContextV2 cerrado.
Preserva sin reclasificar resultado, vigencia, issues y observaciones del screening
original. evaluation_version=3 es independiente de schema_version=12 del binding.
can_continue exige frontera preparada y ausencia de supuestos declarados;
can_confirm permanece false. La frontera actual nunca declara preparacion, por lo
que investigacion sigue bloqueada aunque el expediente este completo y vigente.
Contexto ausente conserva screening pendiente; version desconocida, campos extra
y research omitido se rechazan. Screening V2 historico no acepta ContextV2.

Once casos nuevos cubren conservacion/determinismo/sin mutacion, obsolescencia,
retiro, sensible/menores, contexto ausente y contrato cerrado. Modulo puro sin
conexion API, eventos, politica ni migracion. 348 pruebas focalizadas aisladas aprobadas en 27.49 s; Ruff y Black aprobados.
La suite HTTP ampliada no se repitio porque este modulo aun no se conecta a API.
Proximo: composicion V3 con diagnosticos de investigacion y bloqueo conservador;
luego integracion API/metadatos de eventos y aceptacion revisada.
Ley fija; M3-T1 EN PROGRESO. Activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §146: composicion V3 de investigacion

Nuevo eipd_controls_v3.py mantiene contratos separados: entrada cerrada con ContextV2,
resolucion StoredV1/V2 explicita, evento humano y politica/identidad reales de servidor.
Composicion pura sin DB ni escritura. STAGES_V3 incorpora research sin modificar
las etapas ni contratos historicos. Conserva deteccion V3 completa, evaluacion
ordinaria, motivos de frontera, asociacion/documento research y dispatch de resolucion.
Preparacion, revision documental y vigencia de politica se muestran por separado.
Revision de otro tenant/expediente se conserva visible como obsoleta; evento V1 no
acredita cobertura research. Identidad sin evento humano y versiones desconocidas
se rechazan. Fecha de evaluacion explicita; resultado determinista sin mutacion.

Politica V1 solo representa rutas sensibles historicas: se evalúan barreras generales
con sin_resolver y se agrega politica_investigacion_no_implementada sin ampliar V1.
Incluso una identidad coincidente y evento continuar vigente conservan el bloqueo
investigacion_confirmacion_bloqueada. can_confirm fijo false; no promocion automatica
por preparacion documental ni fuentes declaradas. API/eventos/politica operativa y
registro local permanecen sin cambios. Integracion API y metadatos de eventos siguen
pendientes; no se declara terminada la etapa ni habilitada la ruta.

Dieciocho casos nuevos cubren contratos, estado conservador, diagnosticos completos,
resolucion V1/V2, revision positiva/negativa/obsoleta/otro expediente, politica e identidad.
550 pruebas aprobadas en 30.93 s en base aislada protegida: 366 focalizadas
y 184 regresiones historicas de composicion/politica. Black/Ruff aprobados.
Suite HTTP ampliada no repetida: modulo puro aun no conectado a API.
Proximo: delimitar e integrar lectura API versionada de composicion/resolucion antes
de ampliar el escritor y los metadatos auditables de eventos. Aceptacion pendiente.
Ley fija; M3-T1 EN PROGRESO, investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §147: lectura API de composicion V3

Readiness incorpora eipd_controls_v3 opcional cuando hay expediente research o
regimen investigacion detectado. ContextV2 se construye con RAT actual y documentos
persistidos sin rebind/reparacion. Se agrega salida cerrada V3, frontera V2 y
resolucion versionada; banderas can_confirm/can_continue/is_frontier_prepared false
son explicitas. Contratos V1/V2 y sus acciones no se reinterpretan.

La lectura comparte el ultimo evento/identidad obtenidos por consulta unica de
historial; consulta el registro real de politica. Selector ausente produce politica
null y bloqueo politica_no_disponible, sin bootstrap ni fallback sintetico. Registro
invalido conserva rechazo conservador. Politica V1 no acredita ruta investigacion.
No cambia confirmacion/revision, escritor de resolucion, eventos ni base operacional.
La resolucion StoredV2 sigue pendiente de integracion de escritura y metadatos.

Pruebas HTTP nuevas verifican lectura sin INSERT/UPDATE/DELETE, historial consultado
una vez, sin eventos sinteticos, query parameters sin autoridad, limites entre tenants,
asociacion vigente/obsoleta, ordinario sin research con V3 null y OpenAPI cerrado.
Regresion pura adicional corrige propagacion de issues research sin question_id:
el campo es opcional en el agregador, sin perder los motivos de incompletitud.
Suite protegida completa mas readiness V2: 570 pruebas aprobadas en 455.49 s.
Incluye 174 pruebas HTTP de licitud, tres casos HTTP/OpenAPI nuevos y una
regresion pura de expediente research incompleto. Black/Ruff aprobados.
Proximo: integracion versionada del escritor de resolucion y metadatos auditables
sin activar EIPD ni confirmar investigacion; aceptacion revisada pendiente.
Ley fija; M3-T1 EN PROGRESO. Activacion EIPD bloqueada. Sin commit/push.
