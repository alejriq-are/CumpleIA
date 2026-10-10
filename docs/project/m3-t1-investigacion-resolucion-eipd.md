# M3-T1 §140 — Cobertura de investigacion en resolucion y revision EIPD

## Hallazgo verificado

HEAD 03dd73a. EipdResolutionContextV1 cerrado contiene RAT, base y otros documentos,
pero no research_assessment. build_eipd_resolution_context_hash_v1 usa binding_version
1 y contexto normalizado; StoredV1 acepta binding V1 nullable. Revision vigente V1
compara contexto/documento y hashes del evento; no acredita investigacion ni permiso.
API genera especiales V11/screening V12, pero frontera/resolucion V1 no recibe research.
Ese limite sigue protegido por investigacion_confirmacion_bloqueada. Ley fija y
M3-T1 EN PROGRESO; activacion EIPD bloqueada.

## Contratos sucesores propuestos

Crear EipdResolutionContextV2 interno, cerrado, con todos los campos V1 y un campo
research_assessment obligatorio aunque sea null, tipo BoundResearchAssessmentV1.
Agregar context_schema_version Literal[2]=2 para identidad explicita de este contexto.
No ampliar V1 ni aceptar research como extra ignorado. Revalidar dict/modelos antes de
hash; conservar documento y binding research tal como fueron aportados, sin repararlos.

Crear EipdResolutionContextBindingV2 con binding_version Literal[2] y context_hash;
crear EipdResolutionAssessmentStoredV2 separado, manteniendo entrada documental
EipdResolutionAssessmentV1 sin hashes de cliente. La version documental del contenido
no cambia por cambiar su asociacion. No ampliar StoredV1 silenciosamente; salida
persistida admite ambas formas con dispatch explicito por binding_version. Conservar
historicos StoredV1 con binding null para diagnostico actual, sin completar metadatos.

Funciones nuevas: build_eipd_resolution_context_hash_v2, bind_eipd_resolution_v2,
eipd_resolution_context_is_current_v2 y hash documental V2. Hash de contexto usa
SHA-256 JSON UTF-8 ordenado/compacto, allow_nan=False, envelope domain
cumpleia.eipd.resolution.research, binding_version 2 y contexto V2 completo. Hash
nuevo documental usa dominio/version y StoredV2 normalizado completo. No modificar
funciones ni hashes anteriores. Cambios de cuerpo research con binding conservado,
retiro, base, LIA, RAT, especiales o screening cambian identidad V2.

## Compatibilidad y seleccion

Lecturas dispatch por binding persistido; V1 se compara con V1 y V2 con V2. Documento
V1 con investigacion aportada requiere diagnostico de cobertura pendiente aunque su
hash historico siga coincidiendo; nunca convertirlo a V2 o atribuirle investigacion.
V1 sin investigacion conserva calculo/comportamiento anterior.

Primer incremento V2 sera puro, sin escritura API. En integracion posterior, reaporte
explicito de resolucion con investigacion usa V2; borradores ordinarios sin expediente
ni historial V2 conservan V1. Documento ya V2 se compara con contexto V2 aun si
research se retira (null explicito), detectando obsolescencia; no degradar a V1 en
lectura/PATCH parcial. Definir y probar esta seleccion antes de conectarla al servicio.
Resolucion omitida conserva documento/binding; null retira; aporte conjunto respeta
orden RAT/base/LIA, research, especiales, screening y finalmente resolucion. Ningun
reaporte documental crea o reescribe decision humana. Confirmados/reemplazados
permanecen inmutables; locks/tenant/rollback existentes conservados.

## Revision humana y eventos

Evento previo siempre visible, independiente de vigencia. Para investigacion, evento
referido a documento V1 nunca acredita coverage V2: estado obsoleto o diagnostico
especifico de falta de cobertura, sin alterar evento. Revision V2 exige coincidencia
de contexto V2 y hash documental V2, evaluaciones research de completitud y asociacion,
RAT actual y asociaciones especiales/screening que cubran research. Un documento
completo y una revision vigente aun no habilitan gate ni politica excepcional.

La tabla de eventos actual almacena hashes, identidad, decision, autor y fecha. No
asumir una migracion nueva: revisar si la identidad de version puede derivarse sin
ambiguedad del documento hash/binding y los dominios nuevos; si se requiere columna
de version, agregarla nullable append-only sin backfill ni atribucion historica.
Decidir ese detalle antes del primer escritor V2; no reutilizar identidad de politica
como sustituto de la version del documento/contexto. Mantener hashes y eventos antiguos.

## Fronteras pendientes y secuencia

1. Contexto/binding/Stored V2 y funciones puras, fixtures V1 intactas, sin escritura.
2. Dispatch documental/readiness/revision con cobertura explicita; coexistencia de
   motivos y lectura de eventos historicos sin reinterpretacion.
3. Revision de screening V2/frontera/composicion y contratos sucesores necesarios,
   propagando research completo y base final. No pasar V2 a validadores V1 por quitar
   campos: cualquier proyeccion historica debe informar su falta de cobertura.
4. Integracion API bajo locks, seleccion de version documentada, pruebas HTTP/tenant
   y metadatos de eventos definidos; politica y evidencia de confirmacion revisadas.
5. Aceptacion revisada antes de considerar habilitacion. Mantener todos los bloqueos
   actuales hasta entonces; sin publicaciones/selecciones/activacion operacional.

## Validacion requerida

Regresiones fijas V1; contratos cerrados/version desconocida; V2 determinista y sin
mutacion; cambios/retiro research invalidan contexto y revision sin reparar hashes;
V1 con research nunca acredita V2; V1 sin research compatible; V2 null distinto de V1;
evento anterior visible pero sin autoridad sintetica. Posteriormente HTTP omision,
null/reaportes conjuntos, orden final, rollback, inmutabilidad, tenant y concurrencia.
Usar base aislada y runner protegido. Este paso es documental: ultima validacion
329 ampliadas y 162 regresiones §139, sin nueva suite ni migracion. Sin commit/push.

## 2026-10-09 — M3-T1 §141: contexto y asociacion puros de resolucion V2

Contratos nuevos EipdResolutionContextBindingV2 y StoredV2 separados de V1; StoredV2
exige binding V2 no nullable. Nuevo modulo eipd_resolution_binding_v2.py define
ContextV2 cerrado con context_schema_version 2 y research_assessment obligatorio,
aunque null. Hash de contexto y documental usan dominios/version explicitos; bind
revalida entrada documental sin hashes de cliente y compara sin reparar asociaciones.
V1 y su modulo historico permanecen intactos; ninguna salida/API admite V2 aun.

Nueve casos nuevos: determinismo modelo/dict y no mutacion; cambios de cuerpo/binding
research, retiro, base, RAT y LIA invalidan contexto; campos extras/version desconocida
rechazados, research omitido rechazado/null admitido, V2 rechazado por contratos V1
cerrados, documento ya asociado no aceptado como entrada editable. Fixtures de hashes
V1 de contexto/documento preservadas; V2 null tiene identidad distinta a V1.
Runner incorpora nuevas pruebas y regresiones documentales V1. Resultado final
focalizado aislado 323 aprobadas en 31.40 s (9 nuevas, 159 documentales V1 y 155 previas).
Black/Ruff/diff check aprobados. No nueva suite HTTP ampliada: API/escritores y
comparadores existentes no se cambian; ultima ampliada 329 y 162 regresiones §139.

Proximo: dispatch documental/readiness y revision con diagnostico explicito de
cobertura research; posterior frontera/composicion, metadatos y escritor API V2.
No migracion/backfill, eventos/revisiones nuevas ni cambios de politica/credenciales.
Ley fija, M3-T1 EN PROGRESO; confirmacion investigacion y activacion EIPD bloqueadas.
Sin commit/push.

## 2026-10-09 — M3-T1 §142: evaluacion y vigencia por version

Nuevo eipd_resolution_readiness_v2.py agrega funciones puras de dispatch documental
y vigencia de revision. Valida Stored/contexto segun binding_version 1/2; version
no admitida rechazada. V2 compara hashes sucesores; V1 conserva comparador/hashes.
Reglas documentales comunes extraidas a helper parametrizado por modelos/comparador;
wrapper V1 conserva comportamiento y regresiones. No cambios en hashes V1.

Research en contexto V2 con resolucion V1 agrega asociacion_investigacion_no_cubierta
y context_current false. Proyeccion de campos V1 solo aplica reglas historicas con
falta de cobertura explicita, sin conversion/reasociacion del documento. V2 conserva
comparacion completa; readiness agrega completitud y vigencia research independientes,
sin reparar metadatos. can_confirm permanece false incluso con hashes coincidentes.
Revision anterior sigue visible; V1 con research resulta obsoleta aunque sus hashes
historicos coincidan. Estado vigente V2 describe coincidencia de hashes, no aprobacion
ni completitud juridica. Cambios research invalidan vigencia sin modificar evento.

Cuatro casos nuevos verifican dispatch V1/V2 y evento conservado/obsoleto, ausencia de
contexto, version desconocida y compatibilidad V1 sin research. Suite focalizada
327 aprobadas en 30.33 s, con 159 regresiones documentales V1. Ademas 272 regresiones
frontera/screening/prerequisitos de revision V2 aprobadas en 2.92 s. Black/Ruff/diff
check aprobados. No repetida suite HTTP ampliada: funciones nuevas no estan conectadas
a API, tipos de salida ni escritores; wrapper historico mantiene resultados verificados.

Proximo: definir/integrar cobertura research en frontera y composicion versionadas,
y luego lectura/escritura API V2 y metadatos de eventos. No migracion/backfill,
revision/evento/politica nueva ni cambios de credenciales. Ley fija, M3-T1 EN PROGRESO;
confirmacion investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §143: frontera/composicion de investigacion delimitadas

Plan en m3-t1-investigacion-frontera-composicion.md tras revisar contratos: sucesores
FrontierV2, ScreeningV3 y CompositionV3 reciben ContextV2/research explicitos, sin
ampliar contratos V1/V2 ni proyectar material para simular cobertura. Diferenciar
version de evaluacion de version de binding. Mantener motivos de deteccion completos,
validador_no_implementado y bloqueo conservador hasta integracion/aceptacion revisadas.

Primer incremento previsto frontera V2 pura no declara preparada la ruta mientras
el validador especial este pendiente. Posterior screening/composicion y luego lectura/
escritura API/metadatos de eventos. Paso documental sin suite nueva: ultima 327
focalizadas y 272 regresiones §142. Ley fija, M3-T1 EN PROGRESO; confirmacion de
investigacion/activacion EIPD bloqueadas. Sin commit/push.

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

## 2026-10-09 — M3-T1 §148: escritor puro de resolucion versionada

Nuevo eipd_resolution_writer.py selecciona binding con material de servidor:
ContextV2 cerrado y resolucion previa persistida opcional. Research presente o
investigacion declarada exige V2 aun sin documento research; una resolucion V2
previa conserva V2 despues de retirar documento/declaracion. Ordinario sin research
ni antecedente V2 mantiene binding V1 exacto. Reaporte explicito genera asociacion
sobre contexto final; no muta ni repara documentos anteriores. Version desconocida
y binding aportado dentro del documento de cliente se rechazan.

Funcion pura aun no conectada a POST/PATCH. Omision conserva y null retira deben
seguir resueltos por el caller, bajo locks existentes. Revision/confirmacion y lector
historico esperan V1: integrar esos consumidores antes de habilitar persistencia V2,
sin convertir eventos antiguos ni permitir decisiones positivas. Metadatos auditables
requieren documentar version de binding y cobertura del contexto de cada evento.

Cinco pruebas nuevas: research vigente sin mutacion/determinista, research declarado
sin documento, retirada sin downgrade, ordinario identico V1, contratos rechazados.
375 pruebas focalizadas aisladas aprobadas en 28.97 s; Black/Ruff aprobados.
Suite HTTP ampliada no repetida: helper puro sin conexion API. Ultima suite
completa mas readiness V2: 570 aprobadas en §147.
Proximo: conectar escritor/lectores mediante dispatch y bloqueo explicito de revision
V2 hasta incorporar metadatos auditables. No migracion ni cambio operacional.
Ley fija; M3-T1 EN PROGRESO. Activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §149: escritor V2 conectado a API

POST/PATCH de resolucion usan bind_eipd_resolution_for_context sobre ContextV2
con material final research/especiales/screening/base/LIA/RAT. PATCH aporta antecedente
persistido para impedir downgrade V2. Omision conserva JSON anterior; null elimina;
reaporte explicito asocia nuevamente. Out admite StoredV1 y StoredV2 sin ampliar
el documento de entrada: binding del cliente sigue rechazado. Ordinario mantiene V1.

Readiness despacha documento y vigencia de revision por version cuando hay research
presente/declarado o resolucion V2. Conserva forma documental superior y expone
binding_version en composicion V3. Composiciones V1/V2 quedan null en este ambito;
no se proyecta una resolucion V2 sobre lectores historicos. V3 sigue disponible al
retirar research si persiste resolucion V2. Registro real de politica o ausencia
explicita; sin bootstrap, rebind de lectura ni eventos sinteticos.

Confirmacion y registro de cualquier decision de revision V2 rechazan 409
resolucion_eipd_v2_revision_pendiente tras relectura/locks existentes. Metadatos
versionados de eventos aun pendientes; no se escribe historia V2 sin cobertura
auditable. Acciones historicas V1 conservan comportamiento. No migracion ni cambio
operacional; ley fija y activacion EIPD bloqueada.

Seis casos HTTP nuevos cubren create/PATCH y contexto final, omision/obsolescencia/
reaporte/null, retirada sin downgrade, V1 preservada hasta reaporte, aislamiento,
binding cliente rechazado, declaracion sin documento, lectura sin mutacion, revision
positiva/negativa bloqueada sin eventos e inmutabilidad de expediente confirmado.
485 pruebas aisladas aprobadas en 68.19 s: suite focalizada mas regresiones
HTTP de resolucion, revision, readiness V2 y confirmacion V2/seleccionada.
Incluye seis casos nuevos. Black/Ruff aprobados. No se repitieron las 174
pruebas generales HTTP de licitud; ultima suite completa §147: 570 aprobadas.
Proximo: contrato/metadatos auditables por version para eventos, conservando historia
V1 y bloqueo hasta integrar prerequisitos y aceptacion. M3-T1 EN PROGRESO.
Sin commit/push.

## 2026-10-09 — M3-T1 §150: contrato puro de metadatos de revision

Nuevo schemas/eipd_review_metadata.py define EipdReviewContextMetadataV1 cerrado:
metadata_schema_version 1, versiones enteras estrictas de binding/contexto 1/2,
cobertura no_cubierta/contexto_v2 coherente, hashes de documento/contexto y hash
opcional del material research completo (incluido su binding). V2 cubre research
null explicitamente; null en hash de research no declara documento presente.

Nuevo services/eipd_review_metadata.py genera identidad desde material de servidor
validado y asociado vigente. No proyecta ContextV2 sobre binding V1 ni genera identidad
vigente para contexto obsoleto/ausente/resolucion no asociada. Usa hashes historicos
V1 o sucesores V2 y dominio separado del hash research. Comparador verifica identidad
contra hashes de evento y material actual; metadatos ausentes permanecen ausentes.
Vigencia no acredita autoridad, tenant, completitud, politica ni decision positiva:
esas validaciones corresponden a los prerequisitos/locks/actor autentico del caller.

Doce casos prueban V1/V2 sin mutacion/determinismo, correspondencia con evento,
historia sin metadata, hashes distintos, proyeccion rechazada, contexto obsoleto o
material ausente, V2 con research null y contratos/versiones estrictos incoherentes.
393 pruebas focalizadas aisladas aprobadas en 18.58 s, con doce casos nuevos;
Black/Ruff aprobados. No se repitio suite HTTP ampliada: helpers puros sin conexion
API. Ultimas regresiones API ampliadas §149: 485 aprobadas.

Sin conexion API/eventos ni migracion en este paso. Proxima persistencia: nueva columna
JSONB nullable sin backfill/default sintetico, preservando RLS/tenant/append-only y
FK historicas. Validar contrato/pares/hash del evento al insertar; salida de lectura
versionada debe mantener null historico y no reinterpretar evidencias V1. Prerequisitos
V2 y aceptacion siguen pendientes; todas las revisiones V2 siguen rechazadas.
Ley fija, M3-T1 EN PROGRESO; activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §151: almacenamiento de metadatos de revision

Migracion aditiva d39e2b0f841c sobre c28f1a9d730b agrega review_context_metadata JSONB
nullable a eipd_resolution_reviews, sin default/backfill. CHECK cerrado exige campos,
versiones/cobertura coherentes y hashes identicos a los del evento; research hash es
null o hash valido solo en V2. JSON null/arrays, contratos parciales/extras y versiones
o hashes discordantes se rechazan. ORM mapea SQL NULL mediante none_as_null=True.

Lector puro read_eipd_review_context_metadata_v1 revalida metadata y correspondencia
con hashes del evento; historicos null retornan None sin inferir identidad. No cambia
salidas ni escritor de eventos HTTP: visibilidad API y prerequisitos siguen pendientes.
Mantiene RLS, FK de tenant y permisos runtime INSERT/SELECT; UPDATE/DELETE rechazados.
Ninguna revision V2 ni confirmacion/activacion habilitada.

Diecisiete casos PostgreSQL nuevos cubren nullabilidad/grants/RLS, roundtrip y
historia intacta, rechazo de modificaciones/borrado, once contratos invalidos y
cuatro intentos de saltar aislamiento (tenant/actor/padre/sin autenticacion).
445 pruebas aisladas aprobadas en 25.03 s, incluyendo regresiones de politica de
revision; Black/Ruff aprobados. Ejecutor protegido fija nuevo head d39e2b0f841c.
Suite HTTP general de licitud no repetida; ultima completa §147: 570 aprobadas.

Migracion validada/aplicada en base aislada y luego en base local cumpleia; destinos
local/development comprobados. Comparacion de registros antes/despues confirma
politica/publicaciones/selecciones/selector/eventos existentes identicos, sin metadata
sintetica. No se ejecuta downgrade ni se modifica migracion historica.
Proximo: exponer lectura API versionada de metadata y evaluar prerequisitos V2,
antes de permitir eventos. Ley fija; M3-T1 EN PROGRESO. Activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §152: lectura API de metadata de revision

Composicion V3 expone latest_review_context_metadata y estado separado sin_revision,
sin_metadatos, vigente u obsoleta. La consulta del ultimo evento retorna metadata
validada junto a evento/identidad de politica; wrapper historico conserva contrato
de dos valores. Una sola SELECT de historial; no busca identidad de eventos anteriores.
Metadata solo de salida, no agregada a entradas HTTP de decision humana.

Vigencia compara hashes del evento, documento y ContextV2 actuales, incluido research.
Historia sin metadata conserva null; evento reciente sin identidad no hereda metadata
anterior. Revision documental, politica y metadata son estados independientes. Ausencia
u obsolescencia agrega bloqueo explicito de confirmacion en V3; metadata vigente
no elimina bloques documentales, de fuentes, politica ni investigacion.

Seis casos HTTP/OpenAPI nuevos: sin evento, historico sin metadata, identidad vigente,
material cambiado con metadata obsoleta, ultima negativa sin fallback y contrato de
salida cerrado. Verifican una consulta de historial, ausencia de escrituras, expediente
y conteo de eventos intactos, frontera de tenant y revision V2 aun rechazada.
465 pruebas aisladas aprobadas en 39.62 s: focalizadas mas readiness V2/revisiones
historicas; Black/Ruff aprobados. Suite HTTP general de licitud no repetida; ultima
completa §147: 570 aprobadas. Sin migracion ni cambio operacional en este paso.

Proximo: prerequisitos puros de revision V2 con metadatos/cobertura explicitos antes
de conectar registro de decisiones; confirmacion y activacion permanecen bloqueadas.
Ley fija; M3-T1 EN PROGRESO. Sin commit/push.


## 2026-10-09 — M3-T1 §153: prerequisitos puros de revision V3

Nuevo eipd_review_v3 evalua decisiones sobre resolucion con binding V2 y ContextV2.
Negativas requiere_cambios/no_continuar exigen borrador, versiones admitidas,
RAT vigente y asociacion actual; no exigen completitud documental ni un evento
anterior. Metadata se genera desde material de servidor con cobertura contexto_v2,
research presente o null explicito; nunca se acepta en la solicitud humana.
Ausencia, binding historico y obsolescencia producen motivos separados y no identidad.

Continuar agrega review_blockers de composicion V3 sin exigir revision anterior.
Conserva barreras de investigacion, fuentes, politica y activacion. prerequisites_met
solo describe requisitos puros; can_confirm siempre false y no reemplaza permisos,
validacion de tenant/actor, politica real ni relectura bajo lock. No conecta acciones
HTTP ni inserta eventos; guardia V2 existente permanece bloqueada.

Doce casos nuevos: negativas parciales sin mutacion, positivo bloqueado sin circularidad,
seis cambios de estado/identidad, research null cubierto y entradas humanas cerradas.
560 pruebas aisladas aprobadas en 34.80 s, incluyendo prerequisitos V2 y revisiones
HTTP historicas; Black/Ruff aprobados. Suite HTTP general licitud no repetida;
ultima completa §147: 570 aprobadas. Sin migracion ni cambios de datos operacionales.

Proximo: integrar prerequisitos/metadata de servidor en registro controlado de
negativas V2, con locks, aislamiento y persistencia atomica; positivos, confirmacion
y activacion siguen bloqueados. Ley fija; M3-T1 EN PROGRESO. Sin commit/push.


## 2026-10-09 — M3-T1 §154: registro HTTP de negativas V2

Accion autenticada de revision permite requiere_cambios/no_continuar para resolucion
binding V2. Tras locks globales de politica/selector y serie, relee borrador/versiones,
reconstruye RAT/ContextV2 actuales y aplica prerequisitos V3. No repara asociaciones.
Evento persiste hashes, review_context_metadata generada por servidor, actor autenticado
e identidad de politica seleccionada deshabilitada en la misma transaccion.
Decision continuar V2 conserva 409 resolucion_eipd_v2_revision_pendiente; confirmacion
y activacion permanecen bloqueadas. Escritor V1 y contratos HTTP historicos intactos.

Ocho casos nuevos aislados: ambas negativas con research presente/null explicito,
dos eventos append-only independientes, metadata/hashes/cobertura/actor/politica,
readiness vigente con negativa bloqueante, tenant ajeno y metadata inyectada rechazados;
material research obsoleto, RAT desactualizado y estado confirmado sin evento;
fallo despues de flush revierte evento y metadata. Expediente permanece inalterado.
Fixture ordinaria incompleta rechaza confirmacion por 400 antes del guard EIPD;
regresiones documentales conservan comprobacion 409 para expedientes aplicables.

578 pruebas aisladas aprobadas en 41.89 s, incluyendo prerequisitos y registro HTTP
historicos V2; Black/Ruff aprobados. Suite HTTP general licitud no repetida;
ultima completa §147: 570 aprobadas. Sin migracion ni inserciones operacionales.

Proximo: comprobar concurrencia/relectura de negativas V2 frente a cambios del
expediente y de politica antes de ampliar consumidores. Positivos/confirmacion
siguen bloqueados; fuentes/aceptacion pendientes. Ley fija; M3-T1 EN PROGRESO.
Sin commit/push.


## 2026-10-09 — M3-T1 §155: concurrencia de negativas V2

Diez casos PostgreSQL reales con sesiones app_user independientes prueban espera
observable mediante pg_blocking_pids, sin temporizadores como evidencia de bloqueo.
PATCH de research sin reaporte, reaporte con documento nuevo y retirada se prueban
con commit/rollback: revision espera serie, relee material y genera identidad actual,
o rechaza obsolescencia/ausencia sin evento. Rollback conserva material anterior.

Cambio de selector previo bloquea revision hasta terminar y usa identidad real nueva
si commit o anterior si rollback. Cambio administrativo posterior espera hasta commit/
rollback de revision: evento solo visible tras commit; rollback no publica nada.
Historia conserva hashes/metadatos y politica original aunque selector cambie.
No se habilitan positivos ni confirmacion/activacion; no fue necesario cambiar escritor.
Limpieza de fixtures solo sobre datos sinteticos de la base aislada.

603 pruebas aisladas aprobadas en 46.31 s, incluidos locks compartidos y regresiones
HTTP/prerequisitos historicos. Black/Ruff y diff check aprobados. Suite HTTP general
licitud no repetida; ultima completa §147: 570 aprobadas. Sin migracion, cambio de
permisos ni datos operacionales. M3-T1 EN PROGRESO, Ley fija, fuentes/aceptacion pendientes.

Proximo: verificar negativas simultaneas sobre la misma serie y cancelacion durante
espera antes de ampliar consumidores. Sin commit/push.
