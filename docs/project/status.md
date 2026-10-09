## 2026-10-09 — M3-T1 §137: contratos y funciones puras de asociacion

SpecialContextBindingV11 y EipdContextBindingV12 agregados como sucesores cerrados;
versiones anteriores conservadas. Nuevas funciones hash/bind especiales V11 y
screening V12 envuelven el hash anterior intacto con dominio/version explicitos y
BoundResearchAssessmentV1 completo o null. Screening agrega legal_basis validada
explicitamente. Helper research_transversal_binding serializa sin mutacion y no
repara/recalcula los hashes de investigacion recibidos. Binding obsoleto puede ser
serializado estructuralmente: su vigencia sigue siendo un control independiente.

16 casos nuevos: determinismo modelo/dict, null vs documento, cambios de cuerpo,
binding, RAT y LIA, base explicita screening, version research desconocida, contratos
cerrados sucesores y fixtures de hashes historicos. Comparacion estructural de todas
las funciones anteriores contra ed0f669 aprobada como verificacion del cambio; fuera
de pytest para no exigir historial Git en clones superficiales. Fixtures de hashes
quedan como regresion automatica. Suite final aislada: 145 aprobadas en 13.00 s;
Black/Ruff/diff check aprobados. No repetida suite HTTP ampliada de 303 §135, pues
servicios/API siguen generando las versiones anteriores y su dispatch no se modifica.

No dispatch evaluador nuevo ni generacion API de versiones sucesoras aun: funciones
nuevas son primitives aisladas; no afirmar cobertura operacional de investigacion.
No migracion/backfill, cambios de datos/politicas/credenciales, despliegue ni gates.
Proximo: dispatch por version y diagnostico de falta de cobertura; luego escritura
API ordenada research/especiales/screening con pruebas de compatibilidad ampliadas.
Ley fija, M3-T1 EN PROGRESO; confirmacion investigacion y activacion EIPD bloqueadas.
Sin commit/push.

## 2026-10-09 — M3-T1 §136: asociaciones de investigacion delimitadas

Plan concreto en docs/project/m3-t1-investigacion-asociaciones.md. Sucesores previstos:
SpecialContextBindingV11 y EipdContextBindingV12, envelope de dominio/version nuevo
con hash anterior intacto y expediente BoundResearchAssessmentV1 completo o null;
screening incluye base explicita. No regenerar binding research ni hashes historicos.
Dispatch por version; asociaciones antiguas con research requieren revision por falta
de cobertura. PATCH respeta orden RAT/base/LIA, research, especiales, screening y
solo renueva los documentos reaportados. GET sin escrituras e historicos inmutables.

Se delimita tambien la deuda de contexto de resolucion/revision EIPD para no atribuir
aceptacion historica a investigacion antes de ampliar esa frontera explicitamente.
Proximo: contratos y funciones puras nuevos, luego dispatch/API. Sin implementacion,
migracion ni suite nueva; ultima validacion 303 §135. Ley fija, M3-T1 EN PROGRESO,
confirmacion investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §135: readiness de investigacion y bloqueo conservador

Readiness agrega research nullable con result/issues/applicability documentales,
association_result/association_issues independientes y can_confirm fijo false.
Evalua sobre RAT actual recomponible, base y LIA; compara binding persistido sin
renovarlo. Si RAT no disponible informa contexto_rat_no_disponible; si investigacion
es declarada y no hay expediente informa expediente/asociacion ausentes. Historicos
sin expediente ni regimen detectado conservan research null, sin hash sintetico.

Control transversal compartido por readiness y confirmacion agrega bloqueo 409
investigacion_confirmacion_bloqueada si hay expediente o regimen detectado, incluso
si se declararon respuestas negativas o el documento esta completo/vigente.
No se cambia validador especial ni versiones/hashes especiales/EIPD anteriores.
Completitud documental no implica autoridad ni activa una ruta excepcional.

Nuevos casos HTTP verifican completo+vigente+bloqueado, confirmacion 409 sin mutar
expediente, lectura reiterada sin escrituras, LIA cambiada sin reaporte produce
obsolescencia aun con documento completo, reaporte recupera vigencia, falta evidencia
produce incompleto y retiro deja null para ruta no declarada. Otro caso verifica
investigacion declarada sin documento, con bloqueos y sin asociacion sintetica.
Validacion final ampliada en base aislada: 303 pruebas aprobadas en 248.17 s
(incluye 174 HTTP existentes de licitud y 129 focalizadas). Black/Ruff aprobados.
Sin ejecucion de suite contra base operacional ni nueva migracion.

Proximo: delimitar nuevas versiones de asociaciones especiales/EIPD que cubran el
expediente de investigacion sin reinterpretar material historico. Mantener el gate
bloqueado hasta integracion completa y aceptacion revisada. Ley fija, M3-T1 EN
PROGRESO, activacion EIPD bloqueada. Sin migracion/despliegue ni commit/push.

## 2026-10-09 — M3-T1 §134: expediente de investigacion en API de borrador

Create/PATCH aceptan ResearchAssessmentV1 nullable; salida GET/POST/PATCH expone
BoundResearchAssessmentV1 nullable. Servidor genera hashes con RAT/base/LIA finales.
PATCH model_fields_set distingue omision (preserva objeto/binding), null (retira)
y reaporte (revalida/vincula). Base/LIA cambiadas sin reaporte conservan asociacion
anterior, detectable como obsoleta sin renovacion en GET. No cambios a contratos,
hashes ni gates historicos especiales/EIPD. No nueva migracion.

Seis casos HTTP/OpenAPI nuevos contra PostgreSQL aislado: crear/consultar, cambio
simultaneo LIA/base/reaporte, obsolescencia sin reaporte, retiro, rechazo de binding
cliente en create/PATCH, acceso con organizacion ajena rechazado y PATCH bloqueado
en confirmado/reemplazado con expediente conservado. Estados historicos preparados
por fixture con metadatos validos; no equivale a habilitar confirmacion investigacion.
La prueba de acceso usa identidad A con cabecera B (403); no afirma por si sola una
prueba SQL directa de RLS. Las pruebas HTTP existentes verifican compatibilidad.

Primera suite ampliada: 297 aprobadas y tres fallos de preparacion de pruebas nuevas
(dict LIA y overrides de identidad). Corregidos; segundo intento detecto metadatos
obligatorios de ciclo de vida en fixtures, corregidos sin cambiar restricciones.
Resultado final: 127 pruebas focalizadas aprobadas en 11.78 s; los 174 casos HTTP
existentes de licitud ya aprobaron en la ejecucion ampliada. Black/Ruff aprobados.
Runner incluye ambas suites para siguientes ejecuciones. Sin pruebas en base
operacional, cambios de politica/credenciales ni despliegue remoto.

Proximo: integrar readiness documental y estado de asociacion de investigacion,
con bloqueo conservador e inmutabilidad; luego versiones especiales/EIPD nuevas.
Ley fija, M3-T1 EN PROGRESO, confirmacion de investigacion y activacion EIPD
bloqueadas. Sin commit/push en este paso.

## 2026-10-09 — M3-T1 §133: almacenamiento nullable de investigacion

Migracion append-only c28f1a9d730b sobre b17d95c0286f agrega research_assessment
JSONB nullable a legal_assessments, CHECK SQL NULL u objeto, sin backfill. ORM
agrega campo/constraint; ninguno de los expedientes historicos se reinterpreta.
Contratos nuevos movidos antes de DraftCreate en licitud.py y reexportados por
schemas/research.py para evitar ciclos de importacion; no se agrega input/output
API aun, evitando aceptar datos sin servicio de guardado. Hashes historicos intactos.

Primero upgrade/head y alembic check en base aislada aprobados. Dos pruebas nuevas
verifican columna/nullable/RLS/permisos runtime y borrador HTTP real con SQL NULL,
rechazo arrays/texto/numero/bool/JSON null y almacenamiento objeto. CHECK SQL no
valida todo el contrato; servicio/API posterior lo hara. La primera comprobacion
por nombre de constraint fallo por convencion de nombres; ajustada a tabla/definicion.
Suite final aislada: 121 aprobadas en 10.03 s. Black/Ruff aprobados; runner exige
nuevo head c28f1a9d730b, base aislada y registro EIPD vacio como antes.

Luego migracion aplicada al desarrollo local, alembic check aprobado y snapshot
EIPD completo exactamente igual antes/despues: selector revision 1. Sin cambios de
password/perfil/politicas; no suite contra base operacional ni despliegue remoto.
Nuevo head de ambas bases c28f1a9d730b; procedimientos antiguos con head previo son
historicos, requieren ese sucesor para la version actual del codigo.

Proximo: crear/leer/PATCH de expediente con binding de servidor, omision/null/reaporte
y aislamiento tenant, manteniendo investigacion bloqueada hasta integrar readiness.
Ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §132: persistencia/API de investigacion delimitadas

Plan concreto en docs/project/m3-t1-investigacion-integracion.md: columna JSONB
nullable sin backfill, input documental/output con binding de servidor, contratos
sin ciclos de importacion y semantica PATCH omision/null/reaporte. Contexto cambiado
sin reaporte conserva binding y debe marcar obsolescencia. Historicos no reciben
hash nuevo automaticamente; protecciones tenant/inmutabilidad y gates preservados.

Orden: schema/modelo/migracion, luego servicios/API, readiness y finalmente nuevas
versiones especiales/EIPD con aceptacion. Sin cambios de codigo ni migracion aplicada,
no nueva suite; ultima focalizada 119 §131. Siguiente implementar primer incremento
persistente de schema/modelo/migracion en base aislada. Ley fija, M3-T1 EN PROGRESO,
confirmacion de investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §131: asociacion nueva de investigacion

ResearchContextBindingV1 y BoundResearchAssessmentV1 son contratos cerrados nuevos,
independientes de SpecialContextBinding historico. research_binding.py calcula
SHA-256 con dominio/version explicitos: contexto incluye RAT completo/base/LIA;
documento incluye expediente completo. JSON ordenado por claves; orden de listas y
textos conservado deliberadamente (comparacion conservadora, sin prometer equivalencia
semantica). Bind revalida y devuelve copia; chequeo no actualiza hashes automaticamente.

Cambios RAT/finalidad/base/LIA producen asociacion_contexto_obsoleta; cambios de
expediente producen asociacion_documento_obsoleta. Ausencia requiere revision;
contrato historico/version desconocida no se convierte silenciosamente. Asociacion
vigente no acredita completitud/autoridad; can_confirm sigue false. Sin migracion,
API, persistencia ni cambios de bindings/hashes historicos.

La primera ejecucion detecto error previo de catalogo: evaluador research usaba
interes_legitimo abreviado. Corregido a interes_legitimo_art13d, igual que LegalBasis;
pruebas actualizadas y regresion rechaza el alias. Suite final aislada: 119 aprobadas
en 10.04 s (11 asociacion, 45 evaluador investigacion y 63 previas). Black/Ruff
aprobados. Sin escrituras operacionales ni cambio de selector EIPD.

Proximo: diseñar persistencia/API y versiones de asociacion especiales/EIPD para
incorporar investigacion sin reinterpretar historicos. Ley fija, M3-T1 EN PROGRESO,
confirmacion de investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §130: limites y aplicabilidad de investigacion probados

20 casos nuevos en test_services_research.py: difusion ausente/pendiente mantiene
anonimizacion sin resolver, evidencia con referencia/tipo vacios no acredita
preparacion, cada componente de anonimizacion requerido si se publica, RAT parcial
y selectores semanticamente duplicados requieren revision, adolescentes/vulnerables/
sensibilidad declarada no evaden limites iniciales, expediente/snapshot ausentes y
respuestas sin razonamiento impiden completo. No fue necesario cambiar evaluador.

Suite via ejecutor aislado: 107 aprobadas en 13.05 s (44 investigacion, 63 previas).
Black/Ruff aprobados. Sin escritura operacional, cambios legales ni politicas;
can_confirm sigue false, sin persistencia/API/binding ni integracion especial.

Proximo: implementar identidad/binding documental nuevo y probar cambios de
finalidad, RAT, LIA y expediente; conservar schemas y hashes historicos. No inferir
asociacion vigente a partir de completitud. Ley fija, M3-T1 EN PROGRESO y activacion
EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §129: contrato/evaluador puro de investigacion

Se agregan app/schemas/research.py (ResearchAssessmentV1 cerrado, borrador opcional,
revalidacion de instancias) y app/services/research.py. Evaluador puro reutiliza LIA,
canonizacion de finalidad y RAT; exige base interes_legitimo y cobertura completa
conservadora, deriva sensibles/menores/vulnerabilidad a revision. Completa finalidad,
interes publico, exclusividad, medidas/evidencia y conservacion. Difusion si exige
documentacion de anonimizacion; no la hace no aplicable y material residual requiere
revision; pendiente deja aplicabilidad sin resolver. No verifica eficacia material.

Resultado completo solo describe preparacion documental; can_confirm siempre false.
No integra persistencia/API/binding ni levanta validador_no_implementado especial.
Snapshots y hashes historicos intactos; sin migracion ni escrituras operacionales.
Pruebas nuevas: ausencia de campos, si/no/pendiente, difusion/material residual,
alcance, finalidad/base/LIA incompatible, sensibles/menores, schema cerrado,
revalidacion, determinismo y entradas sin cambios. Runner aislado ampliado para
incluir pruebas de investigacion; Black/Ruff aprobados. Suite aislada: 87 pruebas
aprobadas en 13.20 s (24 nuevas de investigacion y 63 previas). No nueva suite completa.

Proximo: ampliar casos de aplicabilidad y limites antes de diseñar binding nuevo e
integracion persistente. Ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §128: siguiente brecha funcional delimitada

Tras cerrar ciclo local del canal, se revisa codigo actual: salud/biometria por
consentimiento ya tienen evaluadores; investigacion_art16quinquies aun deriva a
validador_no_implementado. Se elige preparacion documental inicial para datos no
sensibles/adultos con LIA vigente, decision de producto sin atribuirla como limite
juridico universal. Fuente primaria BCN Ley 21.719/art16quinquies consultada.

Diseno, completitud/aplicabilidad, integracion por pasos y criterios de aceptacion
en docs/project/m3-t1-investigacion-diseno.md. Proximo: schema y evaluador puro,
sin persistir ni levantar bloqueos hasta integrar/aceptar. Sin cambios de codigo,
politicas ni secretos; sin nueva suite. Ley fija, M3-T1 EN PROGRESO y activacion
EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §127: acceso personal recuperado confirmado

El usuario aporta captura con mensaje «Acceso administrativo confirmado. La
activacion EIPD permanece bloqueada» posterior al reinicio de recuperacion.
Se registra como evidencia visual del usuario, sin inspeccion independiente de
JWT/solicitud original ni almacenamiento de imagen, datos personales o tokens.
La captura no muestra el registro; su coherencia y revision 1 fueron comprobadas
tecnicamente antes/despues del ensayo y no se deducen de esta imagen.

Ensayo reversible real y acceso posterior confirmados. Canal activo restaurado;
no retiro definitivo, nuevas credenciales ni cambios de politica. No nueva suite.
Fuentes/aceptacion y alcance integral pendientes; ley fija, M3-T1 EN PROGRESO,
activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §127: retiro reversible del canal real y recuperacion

Proceso propio 8001 detenido y ausencia de sesiones dedicadas comprobada tras
snapshot previo validado. Login local eipd_backend_local cambiado temporalmente
a NOLOGIN: conexion NUEVA con credencial actual rechazada, SQLSTATE 28000.
LOGIN restaurado en finally; nueva conexion y preflight ok. Snapshot completo
posterior exactamente igual al previo, selector revision 1. No cambio de password,
archivo privado, membresias, perfiles, publicaciones, eventos ni selector.

Proceso 8001 reiniciado con credencial privada actual, DEBUG=false y sin access log;
GET /status sin token -> 401. Backend 8000 fuera del ensayo. Comprobacion personal
posterior al reinicio pendiente. No constituye retiro definitivo del canal ni
revocacion instantanea de transacciones ya autorizadas; se dreno antes del cambio.
No nueva suite; ultima 63 §124. Ley fija, fuentes/aceptacion y alcance integral
pendientes; M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §126: comprobacion personal posterior y retirada de copia

El usuario aporta captura posterior al reinicio con mensaje de acceso administrativo
confirmado y activacion EIPD bloqueada; pantalla conserva revision 1, 1 publicacion,
1 seleccion y politica deshabilitada/seleccionada. Evidencia visual del usuario,
sin inspeccion independiente del JWT ni captura de credenciales.

Tras esta confirmacion se retira exclusivamente la copia privada anterior creada
para recuperacion §126, comprobando ruta/tipo/modo 0600 y ausencia posterior.
Archivo actual privado 0600 conservado. No se elimina historial, roles ni perfil;
no nuevas publicaciones/selecciones. La retirada es eliminacion del archivo de
recuperacion, sin afirmar borrado forense del almacenamiento.

Rotacion local y acceso posterior confirmados; recuperacion temporal cerrada.
Retiro definitivo del canal no ejecutado. Fuentes/aceptacion y alcance integral
siguen pendientes; ley fija, M3-T1 EN PROGRESO y activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §126: rotacion real local ejecutada

Se detuvo el proceso propio de validacion 8001 y se comprobo ausencia de conexiones
del login dedicado antes de alterar password. Destino development/loopback, login
esperado, archivo privado 0600 y head b17d95c0286f verificados. Snapshot previo
validado: 1 publicacion deshabilitada, 1 seleccion, revision 1.

Nueva clave aleatoria en memoria, copia privada de recuperacion 0600 externa al
repo y reemplazo privado preparado; cambio password de eipd_backend_local y
sustitucion atomica de admin.env. Conexion NUEVA con credencial anterior rechazada;
nueva credencial: preflight ok. Snapshot completo posterior exactamente igual al
previo; no cambios de perfiles, permisos, publicaciones, eventos ni selector.

Proceso propio 8001 reiniciado con nuevo secreto en memoria, DEBUG=false y sin
access log. GET /admin/eipd/status sin token -> 401. Backend previo 8000 fuera del
cambio. No secretos ni PII en documentos/logs/repositorio. Copia privada de
recuperacion conservada hasta confirmar sesion personal; retirada aun pendiente.
No se afirma validacion personal tras reinicio a partir del diagnostico tecnico.

Proximo: usuario Comprobar acceso y Consultar registro en pantalla con sesion real,
confirmar revision 1/politica deshabilitada y luego retirar copia privada anterior.
No suite nueva (ultima 63 §124). Fuentes/aceptacion y alcance integral pendientes;
ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §125: rotacion real local preparada

Plan concreto en docs/project/m3-t1-eipd-plan-rotacion-local.md. Lectura previa:
archivo externo 0600, destino development/loopback y login dedicado esperado;
preflight ok, revision 1, head b17d95c0286f. Dos conexiones idle durante diagnostico
(incluida la propia); pool del diagnostico dispuesto al terminar. Requerir nueva
comprobacion de drenaje antes de ejecutar. No se cambia clave/archivo/rol/proceso.

Secuencia preparada: snapshot previo, detener solo validacion 8001 y drenar,
reemplazo privado/recuperacion 0600, cambio de clave y sustitucion atomica con
recuperacion ante fallo, conexiones nuevas antigua rechazada/nueva aceptada,
comparacion exacta de auditoria, reinicio y comprobacion personal. Backend 8000 y
perfil permanecen fuera del cambio. Rotacion REAL pendiente, no acreditada por
ensayo aislado §124 ni por este plan. Sin nueva suite; ultima focalizada 63 §124.
Fuentes/aceptacion y alcance integral pendientes; ley fija, M3-T1 EN PROGRESO y
activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §124: ensayo aislado de rotacion/retiro y recuperacion

Se agregan tres pruebas PostgreSQL de ciclo de vida al ejecutor fijo, sobre login
aleatorio temporal de fixture y base aislada. Rotacion: clave antigua rechazada en
conexiones nuevas (28P01), conexion previa sobrevive, pool se dispone y clave nueva
permite recuperar el canal; rol local e identidad se limpian tras rollback. NOLOGIN:
conexion nueva rechazada (28000), conexion previa sigue viva pero _prepare_channel
rechaza con 503; restaurar LOGIN y renovar pool recupera. Retiro de membresia:
conexion caliente rechazada por guarda 503, restauracion recupera el canal.

63 pruebas focalizadas aprobadas en 13.03 s; Black/Ruff aprobados. El snapshot de
pruebas permanece igual antes/despues de cada ensayo (registro inicialmente vacio
por guarda del runner); no se extrapola a prueba de historial no vacio. Fixtures
restauran flags/membresia cuando procede, disponen pools y eliminan solo su rol
aleatorio. No cambian login/secreto/pool operacional ni perfil personal.
Preflight readonly posterior del canal original: ok, auditoria coherente, selector
revision 1 y activation_authorized false. No rotacion/retiro real del canal de usuario
ni actualizacion de su archivo privado en este checkpoint.

Pendiente operacional: ensayo coordinado sobre canal provisionado, renovacion de
procesos/conexiones y referencia de recuperacion segura con historial real. Ensayo
tecnico aislado no acredita ese cambio. Fuentes/aceptacion y alcance integral siguen
pendientes; ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §123: ejecutor focalizado de pruebas aisladas

backend/scripts/run_eipd_tests.py proporciona python -m scripts.run_eipd_tests.
Deriva ambas URLs solo en entorno hijo hacia cumpleia_eipd_tests_20261009, mantiene
roles separados y exige development, hosts loopback iguales, sin parametros URL,
runtime app_user. Antes de pytest consulta readonly current_database/head y registro
EIPD vacio, confirma runtime sin superuser/BYPASSRLS. Rechaza destino/head/roles/estado
incompatibles con salida logica 2 y mensaje sin secretos. No crea/borra DB ni copia
datos; no imprime URLs. Elimina overrides heredados de pytest y credenciales Supabase/
canal administrativo; usa emisor sintetico de pruebas y targets fijos sin argumentos.

Guardas probadas: URLs a base fija y roles intactos, entorno padre sin cambios,
rechazo remoto/query/produccion, runtime owner/destinos distintos, DB/head/registro
no vacio y privilegios runtime incompatibles. Ejecucion por el runner: 60 aprobadas
en 9.45 s (56 API/concurrencia + 4 guardas); Black/Ruff aprobados. Invocacion con
argumento extra bloqueada antes de pytest. Sin nuevas escrituras operacionales ni
cambios de perfil/secretos/backend. No suite completa nueva.

Alcance: protege las invocaciones mediante este ejecutor; pytest directo sigue
resolviendo DATABASE_URL habitual y no queda protegido por este wrapper. Usar este
punto de entrada para la suite EIPD focalizada, sin ejecutar pytest directo contra
la base operacional. Cambios de head requieren revision explicita de la guarda.
Siguiente: preparar ensayo de rotacion/retiro y recuperacion local preservando
historial. Fuentes/aceptacion y alcance integral pendientes; ley fija, M3-T1 EN
PROGRESO y activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §122: cierre delimitado de validacion local

La secuencia acceso personal -> consulta -> publicacion -> seleccion deshabilitada
queda documentada por capturas aportadas por el usuario (§118–121), y snapshot
tecnico posterior readonly coherente. Este cierre solo cubre esa secuencia local;
no marca DONE del modulo ni aceptacion juridica ni puesta en produccion.

Nuevo preflight readonly real: status ok, salida 0, channel_verified y
permissions_verified true, audit_coherent true, selector_present true y revision 1;
activation_authorized false. Las banderas de identidad del entorno/head/autenticacion
personal del CLI permanecen false por alcance limitado de esa herramienta, sin
sustituir la evidencia personal previa. Head comprobado separadamente por lectura
de alembic_version: b17d95c0286f. Sin escrituras ni nueva suite en este checkpoint;
ultima focalizada: 56 aprobadas en base aislada §121, ultima completa: 3654 §106.

Pendientes separados: (1) asegurar ejecucion de futuras suites solo en base aislada,
(2) probar rotacion/retiro del canal y recuperacion local preservando auditoria,
(3) verificar fuentes complementarias y registrar aceptacion real con responsables,
(4) resolver regimenes especiales/representacion y criterios del alcance integral.
No se identifica una fuente nueva ni se cambia una regla legal en esta revision.
Ley 21.719/19.628 reformada fija. M3-T1 EN PROGRESO; activacion EIPD bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §121: seleccion personal y registro confirmados

El usuario aporta dos capturas: revision 1, publicaciones 1, selecciones 1,
referencia m3-t1-eipd-deshabilitada-v1 deshabilitada y seleccionada. La segunda
muestra rechazo preventivo de reseleccion: publicacion ya seleccionada, sin
ofrecer otra seleccion. Se registra como evidencia visual del usuario; no como
inspeccion independiente del JWT o de la solicitud HTTP original.

Comprobacion tecnica readonly posterior mediante canal dedicado: snapshot validado,
1 publicacion, 1 evento y selector revision 1; identidades publicacion/evento/selector
y hash coinciden, actor de publicacion/seleccion consistente, fuentes/aceptacion
pendientes y activacion deshabilitada. Sin nuevas escrituras ni datos personales,
claves, tokens o capturas incorporados al repositorio.

Queda confirmada la seleccion operacional deshabilitada y su persistencia coherente.
No constituye aceptacion juridica ni habilitacion. Proximo: revisar el cierre de la
validacion operacional y pendientes de provision/rotacion/retiro y aceptacion,
manteniendo la ley fija. M3-T1 EN PROGRESO; activacion EIPD bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §121: seleccion local deshabilitada preparada

La pantalla prepara la seleccion tras consultar GET /audit, toma publication_id,
hash y revision vigentes y muestra referencia/revision antes del boton explicito.
Solo admite la publicacion fija deshabilitada y no ofrece reseleccion de una
publicacion ya presente en eventos. POST /selections existente mantiene autoridad,
control optimista de revision y rechazo de politica habilitada. Tras 201 se consulta
el snapshot y se contrastan evento, hash, revision y selector, conservando estado
deshabilitado. No hay reintentos automaticos ante 409 o respuesta incierta.
La seleccion operacional personal sigue pendiente; no se ejecuta por este paso.

Type-check/lint frontend y formato aprobados. La primera suite en base operacional
produjo 52 aprobadas/4 fallidas porque los casos esperan registro vacio y ya existe
la publicacion personal. Se creo cumpleia_eipd_tests_20261009 vacia, solo esquema
migrado a head, funciones auth y permisos app_user equivalentes; sin copiar datos
personales ni cambiar URLs persistentes. Suite focalizada API/concurrencia en esa
base: 56 aprobadas en 12.15 s. Usar esa base aislada en siguientes suites; no ejecutar
pruebas de escritura contra el registro operacional. La base de pruebas queda local.

Comprobacion readonly posterior del snapshot operacional: 1 publicacion deshabilitada,
0 selecciones y sin selector (revision 0); registro personal preservado. No infiere
solicitud HTTP personal de esta consulta tecnica. Fuentes complementarias y aceptacion
integral pendientes; ley fija, M3-T1 EN PROGRESO y activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §120: publicacion personal confirmada por captura

El usuario aporta captura posterior a Publicar politica deshabilitada. Muestra
revision actual 0, publicaciones 1, selecciones 0, ninguna politica seleccionada,
referencia m3-t1-eipd-deshabilitada-v1 en estado deshabilitada y mensaje de
publicacion confirmada en el registro; activacion EIPD bloqueada.
Se registra como evidencia visual aportada por el usuario de la publicacion con
su sesion personal y comprobacion posterior de la pantalla, sin afirmar una
inspeccion independiente de la solicitud HTTP o de los campos de auditoria.
No se incorporan imagenes, PII, claves ni tokens al repositorio.

La publicacion operacional queda confirmada por esta evidencia. No acredita
seleccion ni aceptacion juridica. Proximo: preparar seleccion explicita de la
publicacion deshabilitada con revision vigente y comprobar evento/selector en
la auditoria. Fuentes complementarias y aceptacion integral siguen pendientes;
ley fija, M3-T1 EN PROGRESO y activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §120: publicacion local deshabilitada preparada

GET /admin/eipd/publication-draft protegido por AdminDb devuelve la propuesta fija
resolve_eipd_gate_policy_v1, sin escrituras ni aceptacion: fuentes pendientes,
aceptacion pendiente, sin responsables/evidencia de aceptacion inventados y
activacion deshabilitada. Motivo operacional y referencia documental explicitos.

La pantalla de desarrollo prepara la propuesta tras consultar el snapshot actual,
evita ofrecer publicacion si su referencia ya existe y muestra que el registro
local es permanente. Solo Publicar politica deshabilitada solicita POST existente
con JWT personal. Tras 201 consulta nuevamente la auditoria y contrasta ID/hash y
estado deshabilitado. No selecciona ni activa; no hay reintentos automaticos.
Ante resultado incierto requiere consultar el registro, sin repetir a ciegas.

56 pruebas API/concurrencia aprobadas en 13.27 s; casos nuevos cubren propuesta
readonly, JWT/autoridad, publicacion seguida de auditoria, selector ausente y
rechazo de duplicados sin cambios. Black/Ruff y type-check/lint frontend aprobados.
Proceso local 8001 actualizado; GET propuesta sin token devuelve 401. La publicacion
operacional con sesion personal sigue pendiente: no se ejecuta ni se acredita por
estas pruebas. No se cambian credenciales, perfiles ni el backend previo 8000.

Proximo: usuario prepara/revisa/publica politica deshabilitada en pantalla y aporta
resultado; luego verificar auditoria y preparar seleccion con revision vigente.
Ley 21.719 / 19.628 reformada fija; fuentes complementarias/aceptacion pendientes.
M3-T1 EN PROGRESO; activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §119: consulta del registro confirmada por el usuario

El usuario aporta dos capturas de la pantalla local: entrada y resultado de
Consultar registro. La segunda muestra revision actual 0, publicaciones 0,
selecciones 0, ninguna politica seleccionada y activacion EIPD bloqueada.
Se registra como evidencia visual aportada por el usuario de la consulta con su
sesion personal; no como inspeccion independiente de la solicitud HTTP.
No se incorporan imagenes, datos personales, claves ni tokens al repositorio.

La consulta personal del registro queda confirmada. No hubo publicaciones ni
selecciones operacionales en este paso. Proximo: preparar la publicacion de una
politica deshabilitada y verificar su persistencia/auditoria; posteriormente,
seleccionarla con revision vigente. Ley fija, fuentes complementarias y aceptacion
integral pendientes. M3-T1 EN PROGRESO; activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §119: consulta personal del registro operativo

Se incorpora GET /admin/eipd/audit con AdminDb y el contrato cerrado de snapshot
validado. La lectura conserva la comprobacion JWT, autoridad global y canal
restringido; errores de coherencia devuelven 409. No crea ni modifica politicas.
La pantalla local incorpora Consultar registro y muestra revision vigente,
numero de publicaciones/selecciones y referencias/estado de las politicas.
Sin selector la revision mostrada es cero; no se inventa una seleccion inicial.

Pruebas API y concurrencia: 54 aprobadas en 12.91 s. Nuevos casos cubren lectura
sin escrituras antes/despues de publicar y seleccionar, rechazo sin JWT y rechazo
tenant. Black/Ruff y type-check/lint frontend aprobados. Backend de validacion
reiniciado; GET real /audit sin token devuelve 401. No se acredita consulta real
con sesion personal hasta el resultado aportado por el usuario. La comprobacion
de acceso personal §118 ya fue confirmada mediante captura.

Proximo: consultar el registro con la sesion personal; luego preparar publicacion
y seleccion deshabilitadas con revision vigente y evidencia operacional.
No hubo publicaciones/selecciones operacionales en este paso. Ley fija, fuentes
complementarias/aceptacion pendientes; M3-T1 EN PROGRESO y activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §118: comprobacion personal confirmada por el usuario

El usuario aporta captura de /admin/eipd-validation con el resultado:
«Acceso administrativo confirmado. La activacion EIPD permanece bloqueada».
Se registra como evidencia visual aportada por el usuario de la comprobacion con
su sesion real, posterior al cierre y nuevo inicio de sesion. No se capturan ni
persisten tokens, credenciales o datos personales; no se incorpora la imagen al
repositorio. No se afirma una inspeccion independiente de la solicitud HTTP.

La comprobacion de acceso queda satisfecha con esta evidencia. No publica ni
selecciona politicas y no habilita activacion. Proximo paso: preparar la validacion
operacional de publicacion/seleccion de politica deshabilitada y auditoria con
sesion personal. Fuentes complementarias y aceptacion integral siguen pendientes.
M3-T1 EN PROGRESO. Sin commit/push.

## 2026-10-09 — M3-T1 §118: comprobacion local de acceso personal preparada

Se incorpora GET /admin/eipd/status, protegido por el canal administrativo y la
autoridad personal existentes. Devuelve solo un resumen de acceso y presencia de
selector; activation_authorized permanece false. No publica, selecciona ni crea
politicas. La pantalla de desarrollo /admin/eipd-validation utiliza la sesion
Supabase del navegador sin mostrar ni persistir el token y consulta el backend
local 127.0.0.1:8001.

Validacion: 40 pruebas focalizadas de API aprobadas; Black/Ruff, type-check y lint
del frontend aprobados. HTTP real sin sesion: pantalla redirige al login (307),
GET de estado rechaza sin token (401). Esto no acredita JWT personal real: queda
pendiente iniciar sesion, abrir la pantalla y pulsar Comprobar acceso. Los procesos
locales son efimeros; backend anterior 8000 permanece. No cambios de credenciales,
perfil ni politicas. Ultima suite completa: 3654 pruebas (§106).

La Ley 21.719 / 19.628 reformada permanece como base fija. Fuentes complementarias,
aceptacion y validacion operacional integral pendientes. M3-T1 EN PROGRESO;
activacion excepcional bloqueada. Sin commit/push en este paso.

## 2026-10-09 — M3-T1: backend local configurado y Supabase verificado

§117 proceso separado 127.0.0.1:8001, secreto externo en memoria/logs limitados,
health 200 y ambas rutas 401 sin token. DNS/JWKS 200 y consulta admin Supabase 200:
vinculo/correo/confirmacion coinciden con staff local autorizado. No acredita JWT
personal. CUA navegador no inicia (helper/setup refresh); sesion real pendiente.
Sin politicas nuevas ni .env habitual cambiado. EN PROGRESO, activacion bloqueada.
Sin nueva suite ni commit/push.

## 2026-10-09 — M3-T1: UID contrastado y HTTP anonimo probado

§116 UID aportado coincide con perfil local unico/superadmin=true. Backend local
health/OpenAPI 200, ambas rutas EIPD registradas y 401 sin token. No acredita JWT
personal ni carga de secreto/SHA del proceso. Proximo configurar proceso y validar
solicitud autenticada sin compartir tokens por chat; consulta Supabase previa
ConnectError aun no resuelta. Sin nuevas escrituras/politicas/suite. EN PROGRESO,
activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1: autoridad global local autorizada

§115 usuario autoriza; perfil local unico/vinculado, is_superadmin=true confirmado
tras commit de mantenimiento. Sin usuario nuevo ni cambios Supabase/politicas.
Identidad externa/JWT/HTTP siguen pendientes; User UID solicitado. Canal tecnico
§113 permanece, sin selector. Sin nueva suite, EN PROGRESO, activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1: perfil staff local sin autoridad global

§114 correo staff indicado coincide con un perfil local vinculado, superadmin=false.
Consulta externa readonly Supabase falla ConnectError; no verifica identidad externa.
Perfil sin cambios. Pendientes ID Supabase/contraste y autorizacion concreta de
superadmin global local; luego JWT/HTTP configurado. Canal tecnico §113 listo sin
selector. Sin nueva suite; EN PROGRESO, activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1: canal tecnico local provisionado

§113 autorizacion explicita; eipd_backend_local creado limitado y credencial nueva
externa privada 0600. Preflight local: canal/permisos/auditoria validos, pending_selector
codigo 2, sin selector/bootstrap. Solo diagnostico carga secreto; .env/backend HTTP
no cambiados. Identidad staff pendiente; proximo vincular staff y validar HTTP
configurado con politica deshabilitada. Sin nueva suite. Fuentes/aceptacion pendientes,
ley fija, EN PROGRESO; activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1: destino local elegido, provision pendiente

§112 usuario selecciona desarrollo local; canal/login dedicados ausentes, head
b17d95c0286f. Identidad staff solicitada, pendiente. Revision automatica bloquea
creacion persistente de login/membresia/credencial; se solicita aprobacion concreta.
No ejecucion ni secretos/roles/archivos nuevos. Expediente actualizado; ultima suite
3654 §106/focalizadas 31 §110. EN PROGRESO, activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1: expediente inicial de entorno

§111 configuracion observada development/hosts loopback; canal EIPD no configurado.
CLI preflight ejecutado: exit 1/failed, sin conexion dedicada; head local b17d95c0286f
readonly. Expediente con resultados y campos pendientes; destino solicitado al usuario.
Sin provision/secreto/actor/politica real, sin nueva suite. Proximo depende de destino
acreditado para provision deshabilitada y humo JWT/HTTP. Fuentes/aceptacion pendientes;
ley fija, EN PROGRESO integral, activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1: permisos efectivos de preflight

§110 grupo/login/RLS/privilegios de tres tablas y acceso fuera de alcance public,
columnas/PUBLIC incluidos. Informe v1 con limites de identidad/head/JWT/activacion.
Ocho nuevas con objetos/grants temporales; 31 focalizadas aprobadas en 3.26 s.
Sin nueva suite completa, ultima 3654 §106; sin ejecucion operativa acreditada.
Proximo expediente de entorno/destino/identidad/responsable y resultados preflight/
HTTP acordados. Fuentes/aceptacion pendientes, ley fija, EN PROGRESO, activacion
bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1: preflight administrativo readonly

§109 script de diagnostico limitado READ ONLY/rollback, login/rol/perfiles y snapshot
validados, sin sub/JWT/barrera personal ni escrituras. JSON ok/pending_selector/failed
sin secretos; no acredita activacion/provision integral. Seis nuevas y 23 focalizadas
aprobadas en 1.84 s; ultima completa 3654 §106. Sin ejecucion operativa real. Proximo
ampliar diagnostico de permisos/evidencia de entorno. Fuentes/aceptacion pendientes;
ley fija, EN PROGRESO, activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1: procedimiento de provision deshabilitada

§108 runbook operativo preparado con expediente, login/pool/staff separados,
verificacion local de roles, JWT/HTTP/auditoria, retirada/rotacion y revocacion.
Solo documentacion; JSON ejemplo validado, sin ejecucion/provision real ni nueva
suite; ultima 3654 §106. Fuentes/aceptacion/provision real pendientes. Proximo
preflight verificable de solo lectura del canal. Ley fija, EN PROGRESO integral;
activacion bloqueada. Sin commit/push.

## 2026-10-08 — M3-T1: fuentes y trazabilidad de aceptacion

§107 revision documental sobre HEAD 97d4fd29920e98a7b0a94714b04ae43e7cb5d010 limpio.
BCN/Diario Oficial reabiertos; instrumento complementario Agencia no verificado en
busqueda acotada (sin afirmar inexistencia). Matriz actualizada con commits §§103–106,
head local b17d95c0286f y ultima suite 3654 §106; sin nueva suite ni cambio de gates.
Aceptacion real/fuentes complementarias/provision operativa pendientes. Proximo:
procedimiento verificable de provision con politica deshabilitada. Ley fija,
EN PROGRESO integral; activacion bloqueada. Sin commit/push.

## 2026-10-08 — M3-T1: concurrencia administrativa HTTP

§106 doce pruebas reales de revocacion previa/posterior, commit/rollback/cancelacion,
selecciones competidoras y referencia duplicada concurrente. Sin cambios productivos;
locks observados en PostgreSQL, JWT ES256/JWKS sintetico, pools limitados reales.
97 focalizadas aprobadas en 11.73 s. Suite completa: 3654 passed en 369.30 s; Black/Ruff/Alembic check/diff correctos.
Proximo fuentes oficiales/trazabilidad de aceptacion y provision operativa separada;
Ley fija, EN PROGRESO, activacion bloqueada. Sin commit/push.

## 2026-10-08 — M3-T1: API administrativa EIPD autenticada

§105 POST /admin/eipd/publications y /selections conectados a JWT verificado/pool
separado/barrera personal; actor derivado, esquemas cerrados, errores controlados,
solo politicas deshabilitadas. 38 HTTP nuevas con ES256/JWKS sintetico y PostgreSQL
real, 85 focalizadas aprobadas en 9.03 s. Suite completa: 3642 passed en 355.96 s; Black/Ruff/Alembic check/diff correctos.
Proximo matriz concurrente HTTP/revocacion y fallos, luego fuentes/aceptacion y
provision operativa. Ley fija, EN PROGRESO; activacion bloqueada. Sin commit/push.

## 2026-10-08 — M3-T1: pool administrativo y dependencia autenticada

§104 configuracion EIPD separada opcional/secreta, sin fallback owner/runtime;
JWT antes del pool, login dedicado limitado, rol/sub locales y barrera personal
hasta commit/rollback. Sin rutas ni provision de credenciales reales. 17 nuevas,
47 focalizadas aprobadas en 3.18 s. Suite completa: 3604 passed en 352.09 s; Black/Ruff/Alembic check/diff correctos.
Proximo: endpoints administrativos y matriz HTTP/JWT/revocacion; luego fuentes/
aceptacion. Ley fija, EN PROGRESO; activacion bloqueada. Sin commit/push.

## 2026-10-08 — M3-T1: escritores con autoridad personal

§103 entradas personales de publicacion/seleccion derivan actor, rechazan actor_id
cliente y requieren perfil superadmin/canal separado antes de escribir. Orden
perfil -> advisory -> selector, sin serie; guardia de habilitadas conservada.
Primitivas privadas solo setup/caller interno confiable; fixtures existentes explicitas.
11 PostgreSQL nuevas, 44 focalizadas aprobadas. Suite completa: 3587 passed en 348.04 s; Black/Ruff/Alembic check/diff correctos.
Transporte autenticado/pool aun pendiente; proximo conectar canal verificado/local,
fuentes/aceptacion antes de activar. Ley fija; EN PROGRESO. Sin commit/push.

## 2026-10-08 — M3-T1: barrera personal transaccional limitada

§102 funcion de autoridad personal, migracion b17d95c0286f aplicada: UUID derivado
sub/perfil superadmin, FOR SHARE hasta commit/rollback, EXECUTE solo canal admin;
helper exige rol y READ COMMITTED. Nueve PostgreSQL nuevas (cuatro concurrencias),
45 focalizadas aprobadas; formato/esquema correctos. Ultima suite completa 3567 §101.
NO conectada a escritores ni transporte/pool autenticado. Proximo integrar en
publish/select con actor derivado y rechazo de suplantacion; luego canal/pool y
fuentes/aceptacion. Ley fija; EN PROGRESO integral. Sin commit ni push.

## 2026-10-07 — M3-T1: identidad/autoridad de perfiles protegidas

§101 auditoria local confirma permisos amplios; migracion a06c84bf175e aplicada.
app_user INSERT/UPDATE limitados por columnas; identidad/autoridad/DELETE/TRUNCATE
protegidos, trigger exige identidad propia autenticada. SELECT anterior conservado,
JIT idempotente sin promocion y update basico propio funcionando; owner mantenimiento
separado. 12 PostgreSQL nuevas, 22 focalizadas con auth aprobadas.
Suite completa: 3567 passed en 431.30 s; Black/Ruff/Alembic check/diff correctos.
Proximo: autorizacion personal transaccional EIPD/revocacion/pool, luego fuentes y
aceptacion. Canal personal aun pendiente; ley fija, EN PROGRESO. Sin commit/push.

## 2026-10-07 — M3-T1: contrato de autoridad personal administrativa

§100 fija identidad JWT verificada + superadmin global + canal DB separado;
actor auditado derivado de perfil, sin permisos tenant ni identidad de payload.
Hallazgo de codigo: grants amplios de profiles requieren auditoria de privilegios
reales/proteccion de identidad y bandera antes de usarla en canal EIPD. No se afirma
explotacion ni estado efectivo de despliegues. Proximo: endurecimiento append-only,
JIT conservado y pruebas; luego revalidacion/locks personales y canal autenticado.
Solo documentacion; autoridad personal aun no implementada. Ultima suite 3555 §99,
no evidencia del contrato nuevo. Ley fija; EN PROGRESO integral. Sin commit/push.

## 2026-10-07 — M3-T1: series/tenants independientes y PATCH

§99 agrega 12 PostgreSQL reales: series de misma/diferente org confirman sin espera
mutua, evidencia/actor aislados por RLS y lectura cruzada denegada; PATCH de A bloquea
solo serie A, B confirma mientras A espera con selector compartido; commit/rollback
del PATCH invalida/permite confirmacion A despues de releer, ambas rutas.
12 aprobadas en 6.64 s. Suite completa: 3555 passed en 345.51 s; Black/Ruff/Alembic check/diff correctos.
Exitos exclusivamente sinteticos/override pytest; guardia productiva conservada.
Proximo: autoridad personal administrativa separada de tenant; fuentes/aceptacion
antes de activar. Ley fija; EN PROGRESO integral. Sin commit ni push.

## 2026-10-07 — M3-T1: concurrencia exitosa y revocacion con evidencia

§98 agrega 12 PostgreSQL reales (ambas rutas, pg_blocking_pids): confirmaciones de
misma serie commit/rollback dejan una evidencia; revocacion espera fin de transaccion,
conserva evidencia exacta tras commit y bloquea accion futura; confirmacion que espera
revocacion relee nueva politica tras commit o anterior tras rollback.
Exitos solo sinteticos con override pytest §97; guardia productiva conservada.
12 aprobadas en 5.78 s. Suite completa: 3543 passed en 343.50 s; Black/Ruff/Alembic check/diff correctos.
Proximo: series/tenants independientes y PATCH concurrentes; autoridad personal,
fuentes/aceptacion antes de activar. Ley fija; EN PROGRESO integral. Sin commit/push.

## 2026-10-07 — M3-T1: evidencia atomica de confirmacion conectada

§97 inserta evidencia solo tras controles v2 y antes de reemplazar confirmado;
relectura auditada/recomposicion pura, UUID/fecha servidor, FK/RLS y misma transaccion.
Guardia de habilitadas conservada; exitos exclusivamente sinteticos en pytest con
override local de guardia, sin bypass/configuracion/endpoint de produccion.
12 PostgreSQL nuevas aprobadas: ambas rutas, reemplazo, cuatro fallos/rollback,
identidad exacta y ausencia de evidencia ante guardia/controles fallidos.
Suite completa: 3531 passed en 334.47 s; Black/Ruff/Alembic check/diff correctos.
Proximo: concurrencia de exitos/revocacion/tenants; autoridad personal, fuentes y
aceptacion antes de activar. Ley fija; EN PROGRESO integral. Sin commit ni push.

## 2026-10-07 — M3-T1: preparacion/confirmacion con selector auditado

§96 unifica politica de revision, readiness y confirmacion. Consulta orientativa sin
locks; accion advisory compartido -> selector compartido -> serie, relectura M2 y
politica auditada. Ausencia/incoherencia bloquea EIPD sin fallback. Ordinario sin
EIPD no exige selector ni crea bootstrap; historia sola conserva ambito §88.
Solo politicas deshabilitadas admitidas; evidencia atomica aun no conectada.
13 PostgreSQL nuevas aprobadas, cuatro concurrencias reales; 221 focalizadas.
Suite completa: 3519 passed en 329.62 s; Black/Ruff/Alembic check/diff correctos.
Proximo: evidencia atomica/fallos/exitos sinteticos, autoridad personal/fuentes/
aceptacion antes de habilitar. Ley fija; EN PROGRESO integral. Sin commit ni push.

## 2026-10-07 — M3-T1: revision humana con selector auditado

§95 conecta POST revision EIPD: advisory compartido -> selector FOR SHARE -> serie,
relectura de contexto y politica tras locks. Negativas guardan identidad seleccionada;
selector ausente/incoherente falla 409 sin escrituras/fallback/bootstrap. Habilitadas
rechazadas; permisos tenant/suscripcion y diagnostico v1 conservados.
Nueve PostgreSQL nuevas, cuatro concurrencias reales; 33 HTTP previas aprobadas.
Suite completa: 3506 passed en 313.64 s; Black/Ruff/Alembic check/diff correctos.
Confirmacion/readiness aun fijas deshabilitadas: siguiente integrar mismo selector
preservando ordinario sin EIPD; luego evidencia atomica/exitos/autoridad personal.
Fuentes/aceptacion pendientes, ley fija; EN PROGRESO integral. Sin commit ni push.

## 2026-10-07 — M3-T1: resolver transaccional de politica con lock compartido

§94 agrega funcion limitada de bloqueo, migracion f95b73aed064 aplicada localmente.
JWT/perfil, search_path seguro, advisory compartido -> selector FOR SHARE sin
UPDATE/BYPASSRLS runtime. Helper READ COMMITTED y snapshot revalidado tras espera;
locks hasta commit/rollback, sin fallback/bootstrap ni conexion a acciones actuales.
15 PostgreSQL nuevas (seis concurrencias reales), 39 focalizadas aprobadas;
suite completa 3497 passed en 309.60 s; Alembic check/Black/Ruff/diff correctos.
Proximo: integrar orden selector -> serie y snapshot auditado en revision/confirmacion,
con selector deshabilitado explicito; luego evidencia atomica/concurrencia/exitos.
Autoridad personal/fuentes/aceptacion pendientes. Resolver fijo de acciones conservado.
Ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.

## 2026-10-07 — M3-T1: servicios internos de politica auditada

§93 implementa publicacion/seleccion deshabilitada y lectura coherente validada.
Canal DB separado; ids/fecha/hash servidor, advisory -> selector exclusivo,
bootstrap serializado y relectura tras espera. Sin commit interno ni endpoint.
24 PostgreSQL nuevas (cuatro concurrencias reales); suite completa 3482 passed
en 315.74 s; Black/Ruff/diff correctos. Resolver actual fijo conservado.
Proximo: resolver transaccional con bloqueo compartido compatible con runtime
SELECT y orden selector -> serie; luego evidencia atomica/concurrencia/exitos.
Autoridad personal administrativa, fuentes/aceptacion y activacion real pendientes.
Ley fija; M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.

## 2026-10-07 — M3-T1: persistencia de evidencia de confirmacion tenant

§92 agrega evidencia append-only tenant, migracion e84a629dcf53 aplicada localmente.
FK compuestas vinculan assessment/revision positiva/politica/seleccion/hashes;
RLS limita lectura tenant e insercion actor JWT/borrador/ultima revision/selector
actual habilitado. Sin endpoint ni integracion de evidencia en confirmacion real.
29 PostgreSQL nuevas; 105 focalizadas previas y suite completa 3458 passed en 302.51 s.
Alembic check sin operaciones nuevas; Black/Ruff/diff correctos. Fixtures ajustadas
al orden FK y ciclo asíncrono, sin reescribir migraciones/eventos historicos.
Proximo: servicio administrativo de publicacion/seleccion y resolver validado;
luego locks/evidencia atomica/concurrencia antes de fuentes/aceptacion y habilitacion.
Resolver fijo deshabilitado. Ley fija; M3-T1 EN PROGRESO integral.
Sin commit ni push.

## 2026-10-07 — M3-T1: persistencia de auditoria global de politica

§91 agrega publicaciones/selecciones/selector globales, migracion d73f518cbe42
aplicada localmente; rol administrativo NOLOGIN separado, runtime lectura autenticada
sin escritura, RLS y constraints de cadena/selector. Consistencia diferida al commit.
44 PostgreSQL nuevas aprobadas; suite completa 3429 passed en 297.19 s.
Alembic check sin operaciones nuevas; Black/Ruff/diff correctos.
Proximo: persistencia append-only de evidencia tenant con FK compuestas/RLS;
luego servicios/resolver y locks. Sin bootstrap/activacion ni API administrativa.
Fuentes/aceptacion pendientes; resolver fijo deshabilitado. Ley fija;
M3-T1 EN PROGRESO integral. Sin commit ni push.

## 2026-10-07 — M3-T1: contratos/evaluadores puros de auditoria

§90 implementa publicacion, cadena/selector revisionados, plan de seleccion y
constructor de evidencia que recompone controles v2. Cerrados/revalidados, hashes,
StrictInt y fechas UTC; no DB, autorizacion, locks ni resolver activo.
65 pruebas nuevas, 169 focalizadas; suite completa 3385 passed en 293.55 s.
Black/Ruff/diff correctos. Proximo: migracion append-only de control global y
evidencia tenant, privilegios/RLS; luego resolver/servicios y orden de locks.
Fuentes/aceptacion y concurrencia/exitos reales pendientes; resolver deshabilitado.
Ley fija; M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.

## 2026-10-07 — M3-T1: contrato de auditoria de politica real

§89 define publicacion inmutable, selector revisionado y auditoria atomica;
orden futuro selector compartido -> serie exclusiva, revocacion y evidencia tenant
de confirmacion. Contrato: m3-t1-eipd-politica-auditoria.md; aun sin implementacion.
Proximo: contratos/evaluadores puros de publicacion/seleccion/evidencia, luego
migraciones/RLS, resolver/locks y concurrencia/exitos antes de habilitar.
Fuentes/aceptacion pendientes; resolver fijo deshabilitado. Solo documentacion,
diff correcto; ultima suite §88: 3320 passed, no reejecutada.
Ley fija; M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.

## 2026-10-07 — M3-T1: decision transversal de confirmacion v2

§88 integra confirmation_blockers v2 bajo lock para el ambito EIPD actual.
Validadores ordinarios/RAT previos y diagnosticos v1 conservados; politica fija
sigue deshabilitada. Una consulta de ultimo evento/identidad y fecha/contexto comunes.
Historia sola no amplia gate ordinario: seis regresiones detectadas/corregidas.
Once HTTP nuevos y concurrencia protegida ampliada; 54 focalizadas aprobadas.
Suite completa final 3320 passed en 287.70 s; Black/Ruff/diff correctos.
Proximo: contrato/auditoria y atomicidad de cambios de politica real; exitos de
frontera habilitada, concurrencia de politica y fuentes/aceptacion pendientes.
Ley fija; M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.

## 2026-10-07 — M3-T1: revision autenticada con prerrequisitos v2

§87 integra decision v2 bajo lock de serie y relectura de contexto M2/documento.
Politica fija de servidor deshabilitada; negativos parciales guardan identidad de
politica sin activar confirmacion. Diagnosticos v1 conservados y error v2 agregado;
una consulta de ultimo evento/identidad, contratos publicos previos preservados.
Diez HTTP nuevos, 71 focalizados aprobados; suite completa 3309 passed en 290.08 s,
incluida concurrencia protegida con aserciones v2 ampliadas. Black/Ruff/diff correctos.
Proximo: decision transversal/confirmacion v2 bajo lock; auditoria/politica real,
exitos/concurrencia de politica y fuentes/aceptacion antes de habilitar.
Ley fija; M3-T1 EN PROGRESO integral. Sin nueva migracion, commit ni push.

## 2026-10-07 — M3-T1: prerrequisitos puros de revision v2

§86 comparte requisitos parciales con v1 y conserva su comportamiento.
Negativas admiten documentacion parcial con asociacion vigente; continuar exige
review_blockers de composicion/politica v2 sin requerir revision positiva previa.
110 pruebas nuevas; 148 focalizadas y suite completa 3299 passed en 281.10 s.
Black/Ruff/diff correctos. Acciones/gates reales siguen v1 bloqueados.
Proximo: revision autenticada v2 bajo lock con politica de servidor deshabilitada;
luego decision transversal, auditoria/politica real, concurrencia y fuentes/aceptacion.
Ley fija; M3-T1 EN PROGRESO integral. Sin nueva migracion, commit ni push.

## 2026-10-07 — M3-T1: readiness de politica/composicion v2

§85 agrega eipd_controls_v2 versionado/cerrado junto a v1. Resolver de servidor fijo
con fuentes/aceptacion pendientes y activacion deshabilitada; sin flags de cliente/env.
Una consulta obtiene ultimo evento/identidad del tenant, sin fallback a positivos
anteriores. GET conserva documentos/historial; vigencia documental/politica separadas.
26 pruebas nuevas; suite completa 3189 passed en 279.29 s, Black/Ruff/diff correctos.
Acciones/gates siguen v1/bloqueados. Proximo: prerequisitos puros de revision v2,
luego acciones/decision/auditoria/politica real y fuentes/aceptacion antes de habilitar.
Ley fija; M3-T1 EN PROGRESO integral. Sin nueva migracion, commit ni push.

## 2026-10-07 — M3-T1: identidad de politica en eventos

§84 agrega policy_version/reference/hash opcionales y CHECK todo NULL o identidad
completa valida; migracion append-only c62e407bad31 aplicada localmente.
Contratos/mapper historicos no promueven eventos sin politica; RLS/permisos intactos.
35 pruebas nuevas, 71 focalizadas y suite completa 3163 passed en 277.43 s.
Alembic check aprobado; Black/Ruff/diff correctos. Comparacion de migracion sobre
0 eventos locales previos, compatibilidad historica cubierta con fixtures.
Proximo: resolver deshabilitado y lectura v2 de composicion/identidad antes de
politica real/auditoria/acciones v2. API/gates siguen v1/bloqueados; fuentes/aceptacion
pendientes. Ley fija; M3-T1 EN PROGRESO integral. Sin nuevo commit ni push.

## 2026-10-07 — M3-T1: politica pura y composicion v2

§83 implementa politica interna cerrada/revalidada, fuentes/aceptacion/rutas,
hash canonico y metadatos de ultimo evento. Composicion v2 comparte nucleo v1,
separa vigencia documental/politica y conserva positivos/faltantes/decisiones.
104 pruebas nuevas; 184 puras aprobadas; suite completa 3128 passed en 276.34 s.
Black/Ruff/diff --check correctos. API/gates reales permanecen v1/bloqueados;
no resolver habilitado ni verificacion real de fuentes en estos evaluadores puros.
Proximo: contrato/persistencia append-only de identidad de politica en eventos,
historicos/RLS antes de resolver/auditoria/acciones v2. Fuentes/aceptacion pendientes.
Ley fija; M3-T1 EN PROGRESO integral. Sin migracion, nuevo commit ni push.

## 2026-10-07 — M3-T1: aceptacion y politica de habilitacion

§82 actualiza evidencia §§80-81: HTTP/concurrencia preparada cubiertos en dos rutas
con contrato ordinario; habilitacion final sigue pendiente. Define politica cerrada
exclusiva de servidor, fuentes/aceptacion trazables, rutas y hash; composicion/gate
v2 futuro sin filtrar codigos v1, identidad de politica en revision y atomicidad.
Proximo: schemas/evaluador puro de politica y composicion v2 sin activar resolver
ni gates. Fuentes complementarias, persistencia/versiones y exitos/concurrencia de
politica siguen pendientes. Ley fija; M3-T1 EN PROGRESO integral.
Paso documental; ultima suite 3012 passed (§78), 97 HTTP focalizadas (§81), no
reejecutadas. Diff correcto; sin codigo, migracion, nuevo commit ni push.

## 2026-10-07 — M3-T1: concurrencia protegida preparada

§81 cubre ambas rutas x revision positiva/confirmacion x commit/rollback: ocho
casos nuevos con dos conexiones app_user, RAT/servicios reales y pg_blocking_pids.
Commit relee dependencia incompleta y obsolescencia documental/humana; rollback
mantiene composicion preparada. Rechazos conservan borrador/resolucion/historial.
97 HTTP focalizadas aprobadas en 36.68 s; Black/Ruff/diff --check correctos.
Ultima suite completa 3012 passed (§78), no reejecutada en este paso de pruebas.
Proximo: actualizar aceptacion §§80-81 y contrato de habilitacion de servidor;
fuentes complementarias/aceptacion y alcance integral restante siguen pendientes.
Ley fija; M3-T1 EN PROGRESO integral. Sin logica nueva, migracion, commit ni push.

## 2026-10-07 — M3-T1: HTTP protegido documentalmente preparado

§80 verifica sensible de derechos y sensible+biometrica con contrato/resolucion
completos y RAT real; cuatro casos con/sin ultima negativa. Preparacion completa
no levanta fuentes/aceptacion ni diagnostico v1; continuar/confirmar 409 sin cambios.
Retirar dependencia invalida frontera/resolucion/revision; tenant ajeno 403.
89 HTTP focalizadas aprobadas en 34.89 s; Black/Ruff/diff --check correctos.
Ultima suite completa 3012 passed (§78), no reejecutada para este paso de pruebas.
Proximo: concurrencia real protegida preparada, commit/rollback y dependencia.
Ley fija; fuentes/aceptacion pendientes. M3-T1 EN PROGRESO integral;
sin logica productiva nueva, migracion, commit ni push.

## 2026-10-06 — M3-T1: aceptacion acotada y fuentes EIPD

§79 contrasta evidencia pura/HTTP/concurrencia y deja primera frontera no aceptada
para habilitacion. Pendientes: HTTP preparado y concurrencia de ambas rutas
protegidas, ademas de instrumento complementario de Agencia no verificado.
BCN art15ter y Diario Oficial Ley21.719 revalidados; busqueda acotada no demuestra
inexistencia de listas/orientaciones. Base normativa fija §70 y bloqueos intactos.
Proximo: HTTP de expediente protegido preparado con RAT real, sin abrir continuar.
Paso documental; ultima suite 3012 passed (§78), no reejecutada, diff correcto.
M3-T1 EN PROGRESO integral; sin codigo, migracion, nuevo commit ni push.

## 2026-10-06 — M3-T1: HTTP seis bases y concurrencia EIPD

§78 amplia seis bases ordinarias con/sin revision negativa y diagnosticos de
revision positiva/confirmacion iguales a readiness; borrador/historial/confirmado
anterior intactos. Dos conexiones app_user con RAT real verifican espera de lock
y relectura de documento/evento tras commit o rollback mediante pg_blocking_pids.
Ocho casos adicionales; 54 focalizadas y suite completa 3012 passed en 295.88 s.
Black/Ruff/diff --check correctos. Sin nueva logica productiva en este paso.
Proximo: matriz de aceptacion de primera frontera y fuentes complementarias
oficiales con evidencia; barreras permanecen. Ley fija sin dependencia temporal.
M3-T1 EN PROGRESO integral; sin migracion, nuevo commit ni push.

## 2026-10-06 — M3-T1: composicion EIPD bajo lock

§77 integra composicion comun en revision continuar y confirmacion antes de
insertar/reemplazar/flush; contexto actual y ultimo evento del tenant releidos.
Errores conservan diagnosticos previos y agregan composicion por etapa.
Negativas mantienen documentacion parcial; fuentes/aceptacion siguen bloqueando.
Seis casos nuevos HTTP/concurrencia real; 227 focalizadas y suite completa
3004 passed en 253.18 s. Black/Ruff/diff --check correctos.
Proximo: ampliar concurrencia de confirmacion y HTTP seis bases para composicion.
Ley fija sin dependencia temporal. M3-T1 EN PROGRESO integral;
sin habilitar frontera, migracion, nuevo commit ni push.

## 2026-10-06 — M3-T1: composicion EIPD en readiness

§76 publica eipd_controls version 1 y deteccion anidada version 2.
Preparacion documental, bloqueos de revision y confirmacion separados.
Contexto/fecha actuales e identidad del servidor; consultas sin escrituras,
historial conservado y aislamiento entre organizaciones verificado.
17 pruebas nuevas; suite completa 2998 passed en 248.05 s, incluyendo §75.
Black/Ruff/diff --check correctos. Proximo: composicion bajo lock en revision
positiva/confirmacion, manteniendo barreras de fuentes complementarias/aceptacion.
Ley fija sin dependencia temporal. M3-T1 EN PROGRESO integral;
continuar/confirmacion excepcional bloqueados, sin migracion, nuevo commit o push.

## 2026-10-06 — M3-T1: composicion pura EIPD implementada

§75 compone estado/RAT, seis bases ordinarias, frontera/v2 y resolucion.
Preparacion documental separada de fuentes/aceptacion y decision humana.
Revision positiva no exige otra previa; confirmacion exige ultimo evento continuar
vigente y del mismo tenant/expediente. Barreras globales conservadas en ambas.
80 pruebas nuevas; 468 focalizadas aprobadas; Black/Ruff/diff correctos.
Ultima suite completa 2901 passed (§73), no reejecutada para servicio aislado.
Proximo: readiness orientativo de composicion; despues lock/fuentes/aceptacion.
Ley fija sin dependencia temporal. M3-T1 EN PROGRESO integral;
sin nueva conexion API/gates, migracion, commit o push.

## 2026-10-06 — M3-T1: contrato de composicion compartida EIPD

§74 cierra entrada interna/matriz/salida de composicion pura. Seis bases ordinarias,
RAT/estado/version, frontera/v2, resolucion y fuentes se componen por etapa;
confirmacion agrega ultimo evento continuar del mismo tenant/expediente y vigente.
Revision positiva no exige evento positivo previo; negativas conservan parcialidad.
preparation_result documental separado de verificacion global/decision humana.
Proximo: implementacion pura y pruebas, sin gates nuevos. Ley como base fija;
fuentes/aceptacion pendientes. M3-T1 EN PROGRESO integral. Paso documental,
ultima suite 2901 passed (§73), diff correcto; sin commit/push ni migracion.

## 2026-10-06 — M3-T1: readiness de frontera y deteccion v2

§73 expone eipd_v2 versionado y cerrado, incluyendo frontera y diagnostico v1.
Contexto final desde RAT actual; no usa snapshot almacenado cuando no puede
reconstruirse finalidad/alcance. V1/bloqueos permanecen; GET no escribe ni reasocia.
14 pruebas nuevas; suite completa 2901 passed en 247.30 s; Black/Ruff/diff correctos.
Dos rutas preparadas conservan requiere_eipd y v1 pendiente; parciales/obsoletos
mantienen bloqueo. Proximo: contrato/matriz de composicion compartida de controles
para revision y gate, sin habilitar continuar mientras fuentes/aceptacion pendientes.
Ley como base fija sin dependencia temporal. M3-T1 EN PROGRESO integral;
sin migracion, nuevo commit ni push.

## 2026-10-06 — M3-T1: deteccion EIPD v2 implementada

§72 agrega deteccion pura v2 y nucleo compartido con v1 historico. Frontera
completa genera motivo de excepcion preparada conservando supuesto positivo y
requiere_eipd; diagnostico v1 entero permanece visible en resultado de frontera.
Fuera de frontera mantiene v1 integro, sin filtrar blockers. API/gates aun en v1.
56 pruebas nuevas; suite completa 2887 passed en 243.26 s; Black/Ruff/diff correctos.
Incluye las 106 pruebas de frontera §71. Proximo: readiness con v2/frontera
separados y versionados; despues composicion/fuentes/aceptacion antes de continuar.
Ley como base fija sin dependencia temporal. M3-T1 EN PROGRESO integral;
sin migracion, nuevo commit ni push.

## 2026-10-06 — M3-T1: evaluador de primera frontera EIPD

§71 implementa servicio puro de preparacion sensible de derechos, sola o con
biometria dependiente. Rol/rutas, especiales, residuos, asociaciones y cinco
respuestas fundadas; screening v1 entero conservado como diagnostico separado.
Preparado no confirma; ordinarios/documento/revision/fuentes siguen separados.
106 pruebas nuevas, 695 focalizadas aprobadas; Black/Ruff/diff correctos.
Ultima suite completa 2725 passed (§68), no reejecutada para servicio aislado.
Proximo: deteccion v2 explicita y despues composicion, manteniendo positivo EIPD.
Ley como base fija sin dependencia temporal. M3-T1 EN PROGRESO integral;
sin gates nuevos, migracion, commit o push.

## 2026-10-06 — M3-T1: base normativa fija y contrato de frontera

Decision explicita: ley adoptada como base fija del proyecto, sin condicionar
controles a fecha de vigencia o eventual postergacion. §70 define matriz/contrato
puro de primera ruta sensible de derechos, sola o con biometria dependiente.
Preparacion de frontera separada de ordinarios/documento/revision/fuentes/gate;
screening positivo preservado, v1 historico intacto y v2 pendiente.
Proximo: evaluador puro y pruebas de frontera. Fuentes complementarias pendientes
se mantienen separadas; continuar aun bloqueado. M3-T1 EN PROGRESO integral.
Paso documental; ultima suite 2725 passed (§68), sin nueva corrida ni commit/push.

## 2026-10-06 — M3-T1: registro de fuentes EIPD

§69 registra busqueda acotada y evidencias en m3-t1-eipd-fuentes.md.
Texto legal comprobado; listas/orientaciones concretas no verificadas, sin inferir
inexistencia. Anuncio ministerial de postergacion registrado como propuesta.
Verificacion global pendiente y barreras actuales conservadas. Proximo: matriz y
contrato versionado de primera frontera, sin habilitar continuar hasta resolver
fuentes/aceptacion. Ultima suite 2725 passed (§68); paso documental, diff correcto.
M3-T1 EN PROGRESO integral; sin commit/push, codigo ni migracion nuevos.

## 2026-10-06 — M3-T1: accion autenticada de revision EIPD

Alcance integral, EN PROGRESO. §68 agrega POST eipd-resolution/reviews con
edit_content/suscripcion, tenant validado, bloqueo de serie y relectura de borrador.
Reconstruye RAT/contexto y aplica prerequisitos; hashes/actor/fecha son de servidor.
Historial append-only; documento y assessment sin cambios. Decisiones negativas
admitidas sobre parcial vigente; continuar sigue bloqueado por frontera/fuentes.
15 pruebas nuevas, incluidas dos sesiones app_user con RAT real y commit/rollback;
suite completa 2725 passed en 242.75 s. Black/Ruff/diff --check correctos.
Proximo: frontera versionada y verificacion oficial de fuentes; gates, seis bases y
concurrencia ampliada antes de habilitar confirmaciones. Sin migracion, commit ni push.
Base actual 4095622, sincronizada con origin antes de este paso.

## 2026-10-06 — M3-T1: checkpoint EIPD autorizado para commit

Se registra avance §65–§67: evaluador documental, readiness y vigencia de ultima
revision, y prerequisitos puros de decision humana. No abre confirmaciones ni
agrega accion API de revision. M3-T1 EN PROGRESO, alcance integral.
Validacion previa al commit: suite completa 2710 passed en 238.18 s;
Black/Ruff sobre seis archivos Python y git diff --check correctos.
Commit local expresamente solicitado por el usuario. Proximo: accion autenticada
de revision, manteniendo continuar bloqueado hasta frontera/fuentes verificadas.

## 2026-10-06 — M3-T1: prerequisitos de revision humana EIPD

Alcance integral, EN PROGRESO. §67 agrega evaluador puro para registrar revision:
borrador, documento y asociacion vigentes exigidos para todas las decisiones.
Rechazos admiten documento parcial; continuar conserva motivos documentales y
barreras de frontera/fuentes no verificadas, sin bandera cliente de aprobacion.
38 pruebas nuevas; 215 focalizadas aprobadas; Black/Ruff correctos.
Ultima suite integral 2672 passed (§66), no reejecutada para servicio aislado.
Sin API/escritura ni cambio de confirmacion. Proximo: accion humana autenticada,
relectura bajo lock, campos de servidor e historial, manteniendo continuar bloqueado.
Checkpoint base 6d9bb76; sin migracion ni nuevo commit.

## 2026-10-06 — M3-T1: readiness documental y vigencia EIPD

Alcance integral, EN PROGRESO. §66 expone preparacion documental y vigencia de
ultima revision como resultados separados del screening y la confirmacion.
Contexto RAT actual; hashes documental/contextual; ultimo evento por fecha/id.
Cambios vuelven obsoleta la revision y reaportar no renueva el evento anterior.
Lecturas sin escritura, aislamiento tenant y barrera provisional conservados.
18 pruebas nuevas; suite completa 2672 passed en 237.06 s; Black/Ruff correctos.
Proximo: frontera de revision y accion humana autenticada, fuentes oficiales y
concurrencia antes de habilitar confirmaciones. Checkpoint base 6d9bb76;
sin migracion ni nuevo commit.

## 2026-10-06 — M3-T1: evaluador documental EIPD implementado

Alcance integral, EN PROGRESO. §65 agrega evaluador puro de completitud/aplicabilidad:
riesgos/medidas, evidencia, scope RAT, fuentes/consulta y binding vigente.
Fecha explicita, resultados inmutables, revision prevalece preservando faltantes.
159 pruebas nuevas; 455 focalizadas aprobadas, Black/Ruff/whitespace correctos.
Ultima suite integral 2495 passed (§64), no reejecutada para evaluador aislado.
Preparacion no aprueba frontera ni revision humana. Sin API/gates nuevos;
fuentes verificadas pendientes. Proximo: readiness documental y vigencia separadas.
Checkpoint base 6d9bb76; sin migracion ni nuevo commit.

## 2026-10-06 — M3-T1: checkpoint local autorizado

Se registra el avance acumulado de M3-T1: seis bases ordinarias, controles
especiales soportados, preparacion de excepciones de derechos y resolucion EIPD
documental con asociaciones, persistencia, historial protegido y API (§64).
68 archivos revisados; formato/lint correctos y sin patrones sensibles detectados.
Validacion: suite integral 2495 passed; 25 HTTP revalidados tras ajuste de mensaje.
El usuario autoriza expresamente este commit local. EN PROGRESO, alcance integral;
evaluador/revision/vigencia EIPD, fuentes y demas rutas pendientes, sin cierre DONE.

## 2026-10-06 — M3-T1: API documental de resolucion EIPD

Alcance integral, EN PROGRESO. §64 integra CREATE/PATCH/GET y binding al contexto
final tras especiales/screening. Omision conserva, null vacia, objeto reemplaza;
historial intacto y GET sin escritura. Metadata de servidor no editable.
Barrera provisional compartida mantiene confirmaciones bloqueadas con resolucion.
25 HTTP nuevos; 225 focalizadas aprobadas. Suite integral 2495 passed en 233.70 s;
25 HTTP revalidados tras ajuste de redaccion. Black/Ruff/whitespace correctos.
Proximo: evaluador puro de completitud/aplicabilidad; luego revision/vigencia/gates.
Fuentes oficiales pendientes; head b51d3f6a9c20, sin migracion nueva ni commit.

## 2026-10-06 — M3-T1: persistencia de resolucion e historial EIPD

Alcance integral, EN PROGRESO. §63 agrega JSONB de resolucion y eventos de revision,
FK tenant-aware sin borrado en cascada, RLS/identidad y permisos append-only runtime.
Migracion local b51d3f6a9c20 aplicada; Alembic check sin diferencias.
36 pruebas PostgreSQL nuevas; regresion integral 2470 passed en 221.64 s.
Black/Ruff/whitespace correctos. Sin API/revision funcional ni apertura de gates;
fuentes oficiales pendientes. Proximo: exposicion CREATE/PATCH/GET y binding final,
conservando historial; despues evaluador/revision. Sin commit.

## 2026-10-06 — M3-T1: asociacion/hash de resolucion EIPD implementados

Alcance integral, EN PROGRESO. §62 agrega servicio puro con contexto final completo,
base/consentimiento y todos los expedientes; hash documental separado incluye binding.
Comparacion sin escritura, revalidacion de modelos, entradas internas cerradas.
89 pruebas nuevas; 296 focalizadas aprobadas. Black/Ruff y whitespace correctos.
Ultima suite integral 2234 passed (§58), no reejecutada para funciones aisladas.
Sin API/DB/gates nuevos; fuentes pendientes. Proximo: persistencia JSONB y eventos
append-only/RLS; luego exposicion documental y revision. Sin migracion ni commit.

## 2026-10-06 — M3-T1: schemas de resolucion/revision EIPD implementados

Alcance integral, EN PROGRESO. §61 implementa documento editable parcial cerrado,
forma interna con binding y revision humana separada de campos de servidor.
111 pruebas nuevas aprobadas; 231 focalizadas y 419 de schemas. Black/Ruff y
whitespace correctos. Ultima suite integral 2234 passed (§58), no reejecutada.
Sin persistencia/API/evaluador ni apertura de gates; fuentes oficiales pendientes.
Proximo: asociacion/hash de resolucion v1; luego persistencia/eventos/RLS/API.
Sin migracion nueva ni commit.

## 2026-10-06 — M3-T1: contratos/matriz de resolucion EIPD definidos

Alcance integral, EN PROGRESO. §60 concreta documento parcial cerrado, riesgos,
medidas, fuentes/consulta condicionales y revision humana con metadata de servidor.
Matriz separa incompleto/revision y preparacion/decision/vigencia; hashes y eventos
no editables por cliente. Confirmaciones siguen bloqueadas; fuentes pendientes.
Proximo: schemas separados y pruebas de contrato. Solo documentacion; ultima
suite 2234 passed (§58), no reejecutada. Sin migracion nueva ni commit.

## 2026-10-06 — M3-T1: resolucion EIPD acotada disenada

Alcance integral, EN PROGRESO. §59 delimita registro de EIPD externa, analisis,
revision humana/eventos trazables y gate separado; positivo EIPD se conserva.
Primer soporte previsto: excepciones sensibles de derechos solas/con biometria,
sin otros positivos/rutas pendientes ni riesgo residual alto. Frontera de producto,
sin aprobacion regulatoria automatica; workflow completo sigue diferido.
Fuentes legales verificadas; orientaciones especificas no verificadas, tarea pendiente
antes de habilitar confirmaciones. Proximo: contratos/matriz de resolucion y eventos.
Solo documentacion, gates actuales bloqueados; ultima suite 2234 passed (§58),
no reejecutada aqui. Sin migracion nueva ni commit.

## 2026-10-06 — M3-T1: integracion biometrica de derechos

Alcance integral, EN PROGRESO. Readiness nullable, detector y barreras biometricas
integrados con dependencia sensible y residualidad en ambos sentidos (§58).
Ruta de excepcion no exige expediente de consentimiento; mezcla mantiene revision.
Doce casos nuevos, seis HTTP con RAT real; 251 verificaciones focalizadas aprobadas.
Regresion integral: 2234 passed en 218.12 s; formato/lint/whitespace correctos.
Completo documental no confirma excepcion: EIPD conserva bloqueo/positivo.
Proximo: definir resolucion EIPD antes de habilitar estas confirmaciones.
Sin migracion nueva ni commit.

## 2026-10-06 — M3-T1: evaluador puro biometrico de derechos

Alcance integral, EN PROGRESO. Preparacion biometrica, dependencia sensible,
vinculos de contexto/alcance e informacion por sistema implementados (§57).
208 pruebas nuevas aprobadas; formato/lint/whitespace correctos.
Evaluador aislado: todavia no expuesto ni integrado en detector/gates API.
Proximo: readiness e integracion biometrica con residualidad y EIPD conservado.
Ultima suite integral anterior 2014 passed (§56), no reejecutada en este paso.
Sin cambios de asociaciones/migracion ni commit.

## 2026-10-06 — M3-T1: readiness e integracion sensible de derechos

Alcance integral, EN PROGRESO. Evaluador sensible conectado a detector, readiness
nullable y barreras compartidas; residualidad explicita en ambos sentidos (§56).
Completo documental no confirma excepcion: EIPD conserva bloqueo/positivo y
rechaza falso negativo. Doce casos nuevos, incluidos seis HTTP con RAT real.
209 verificaciones focalizadas y seis HTTP ampliadas aprobadas; regresion
integral: 2014 passed en 199.23 s. Formato/lint/whitespace correctos.
Proximo: evaluador biometrico de derechos y vinculos; despues integracion.
Sin migracion nueva ni commit.

## 2026-10-06 — M3-T1: evaluador puro de excepcion sensible

Alcance integral, EN PROGRESO. Preparacion/aplicabilidad de derechos sensible
implementada segun §51/§55: contexto, etapa, foro, necesidad, evidencia y alcance.
172 pruebas nuevas aprobadas; formato/lint/whitespace correctos.
Evaluador aislado: todavia no expuesto ni integrado en detector/gates API.
Controles transversales y EIPD siguen bloqueando, incluso completo documental.
Proximo: integracion/readiness sensible con residualidad; despues biometrico.
Ultima suite integral anterior 1830 passed (§54), no reejecutada en este paso.
Sin migracion nueva ni commit.

## 2026-10-06 — M3-T1: asociaciones de excepciones implementadas

Alcance integral, EN PROGRESO. Especiales v10/EIPD v11 incluyen ambos expedientes;
comparadores historicos conservados. Presencia no cubierta tiene motivos propios;
mutaciones invalidan asociaciones y el reaporte es explicito (§54).
118 casos nuevos: 96 servicios y 22 HTTP. Regresion integral: 1830 passed en 184.29 s.
Confirmacion sigue bloqueada por excepcion_derechos_no_preparada y barreras EIPD.
Proximo: evaluador de excepcion sensible de derechos; despues biometrico/vinculos.
Sin migracion nueva ni commit.

## 2026-10-06 — M3-T1: persistencia/API de excepciones

Alcance integral, EN PROGRESO. Ambos expedientes almacenados y expuestos;
migracion local a40c2e5f8b19 aplicada, Alembic check sin diferencias.
Tres casos HTTP aprobados; regresion integral 1712 passed en 169.95 s (§53).
Presencia de expediente bloquea confirmacion y preserva borrador/vigente.
Proximo: asociaciones especiales v10/EIPD v11; despues evaluadores propios.
EIPD conserva bloqueo; sin commit.

## 2026-10-06 — M3-T1: schemas de excepciones implementados

Alcance integral, EN PROGRESO. RightsExceptionContextV1 y documentos sensible/
biométrico de derechos cerrados, parciales y separados de consentimiento.
102 casos nuevos; 252 pruebas seleccionadas de contratos aprobadas. Diseño §52.

Sin persistencia/API/asociaciones ni evaluador/gate; EIPD conserva bloqueo.
Próximo: persistencia/exposición de ambos expedientes y asociaciones compatibles.
Última suite integral anterior 1585 passed, no reejecutada aquí.
Formato/lint/whitespace correctos; sin migración nueva ni commit.

## 2026-10-06 — M3-T1: contratos de excepción de derechos diseñados

Alcance integral, EN PROGRESO. §51 fija RightsExceptionContextV1 y expedientes
sensible/biométrico independientes; foro administrativo, etapa/condicionales,
necesidad y evidencia, vínculos/scopes, información conservadora y residualidad.
Sin dependencia artificial de consentimiento. EIPD conserva positivo y bloqueo.

Próximo: implementar schemas y pruebas de contrato. Solo documentación;
última suite 1585 passed y 58 verificaciones posteriores, no reejecutadas aquí.
Sin migración ni commit; resolución EIPD/confirmación de excepción pendientes.

## 2026-10-06 — M3-T1: primera excepción biométrica delimitada

Alcance integral, EN PROGRESO. Se prioriza formulación/ejercicio/defensa de derechos
por remisión art16ter a art16bis(d); dependencia sensible art16d necesita validador
propio. Base ordinaria no aprueba excepción automáticamente. Diseño §50.

EIPD positivo conserva bloqueo: preparación documental no habilita confirmación
sin resolver esa dependencia. No alterar screening para eludirla. Próximo:
contratos/matriz de excepción sensible y biométrica, con scopes y foro específicos.

Solo documentación; última suite 1585 passed y 58 verificaciones posteriores.
Sin pruebas reejecutadas, migraciones ni commit.

## 2026-10-06 — M3-T1: evidencia biométrica ampliada

Alcance integral, EN PROGRESO. Seis casos HTTP de bases ordinarias y dieciséis
concurrentes nuevos con RAT real y cuatro regímenes preparados. Conservación
íntegra del vigente/documentos históricos ante rechazo. Diseño §49.

58 verificaciones focalizadas aprobadas: concurrencia 41, HTTP biométrico 17.
Concurrencia real biométrica cubre consentimiento_art12; no extrapolar otras bases.
Última suite integral anterior 1585 passed (§48), no reejecutada en este paso de
pruebas/documentación. Formato/lint/whitespace correctos; sin migración ni commit.
Próximo: delimitar primera excepción biométrica sin consentimiento dentro del
alcance integral, con contrato propio y remisión normativa revisada.

## 2026-10-06 — M3-T1: confirmación biométrica integrada

Alcance integral, EN PROGRESO. Primera ruta biométrica por consentimiento
preparado integrada con detector/gate y EIPD. Régimen conserva dependencias,
restricciones y asociaciones; excepciones siguen bloqueadas. Diseño §48.

Suite integral **1585 passed en 155.13s**; 19 casos transversales nuevos, 176
pruebas seleccionadas biometría/salud y once HTTP biométricos aprobados.
Black/Ruff/whitespace y Alembic check correctos. Sin migración nueva ni commit.
Próximo: HTTP biométrico de seis bases y concurrencia con constructor RAT real.

## 2026-10-06 — M3-T1: preparación biométrica implementada

Alcance integral, EN PROGRESO. Evaluador puro y biometric nullable en readiness;
motivos compartidos de preparación GET/POST. Completo sigue bloqueado por régimen
sin validador integrado. Diseño §47. Próximo: integración detector/gate y EIPD.

Suite integral **1566 passed en 154.38s**, incluidas 73 pruebas puras y un caso
HTTP nuevos. Black/Ruff/whitespace y Alembic check correctos.
Sin migración nueva ni commit; excepciones y regímenes restantes siguen pendientes.

## 2026-10-06 — M3-T1: persistencia biométrica implementada

Alcance integral, EN PROGRESO. Expediente biométrico en CREATE/PATCH/GET y JSONB
nullable; asociaciones especiales v9/EIPD v10 compatibles. Head f39b1d4e7a08
aplicado; Alembic check aprobado. Diseño §46. Régimen sigue bloqueado.

Suite integral 1492 passed en 150.93s; diez casos HTTP focalizados aprobados tras
ampliación final de protección del confirmado. Formato/lint/whitespace correctos.
Sin commit. Próximo: evaluador puro y readiness, antes de habilitar gate/EIPD.

## 2026-10-06 — M3-T1: schemas biométricos implementados

Alcance integral, EN PROGRESO. BiometricSystemV1/BiometricAssessmentV1 y 53 casos
nuevos; 150 pruebas seleccionadas de contratos aprobadas. Formato/lint correctos.
Sin persistencia/API/asociaciones ni evaluador/gate; biometría sigue bloqueada.
Diseño §45. Próximo: persistencia/exposición y asociaciones compatibles.

Última suite integral anterior: 1429 passed (§41), no reejecutada aquí.
Sin migración nueva ni commit.

## 2026-10-06 — M3-T1: contrato biométrico diseñado

Alcance integral, EN PROGRESO. §44 define BiometricAssessmentV1/BiometricSystemV1,
matriz por sistema, dependencias sensibles, scopes, asociaciones futuras y
aceptación. No habilita biometría ni sus excepciones. Próximo: schemas y pruebas.

Solo documentación; última suite 1429 passed y Alembic check aprobado (§41),
no reejecutados. Sin migración nueva ni commit.

## 2026-10-06 — M3-T1: alcance integral confirmado

El usuario decide continuar alcance integral; no se adopta entrega inicial para
cierre. M3-T1 EN PROGRESO. Siguiente régimen: biometría, diseño §43.
Próximo paso: contrato y matriz de completitud/aplicabilidad para primera ruta
por consentimiento expreso. Excepciones y otros regímenes siguen pendientes
funcionales dentro del alcance integral, sin habilitación automática.

Solo documentación. Última suite 1429 passed; Alembic check aprobado (§41).
Sin pruebas reejecutadas, migraciones ni commit.

## 2026-10-06 — M3-T1: propuesta de entrega preparada

M3-T1 EN PROGRESO. Propuesta revisable en m3-t1-propuesta-entrega.md:
backend de seis bases ordinarias, sensible titular, geolocalización y primer
alcance de salud. Pendientes funcionales explicitados; no diferidos automáticamente.
Decisión pendiente: entrega inicial o continuar alcance integral. Diseño §42.

Solo documentación. Última suite 1429 passed; Alembic check aprobado (§41).
Sin pruebas reejecutadas, migraciones ni commit; no se declara DONE.

## 2026-10-06 — M3-T1: drift global corregido

M3-T1 EN PROGRESO. Modelos alineados con índices históricos y nombre de unique:
29 índices declarados, sin eliminar índices ni modificar la base de datos.
Alembic check global aprobado, sin operaciones nuevas. Diseño §41.

Suite integral posterior: **1429 passed en 140.69s**. Black/Ruff/whitespace
correctos. Sin migración nueva ni commit. Próximo: propuesta explícita de alcance
de entrega y tratamiento de regímenes pendientes antes del cierre.

## 2026-10-06 — M3-T1: cadena de migraciones revisada

M3-T1 EN PROGRESO. Head único e28a0c3f6d97 aplicado localmente; cadena lineal.
Formato/lint aprobados para 46 archivos Python nuevos/modificados. Comparación
Alembic limitada a tablas M3 sin diferencias; última suite integral 1429 passed.

Hallazgo pendiente: alembic check global falla por índices/nombres de restricciones
fuera de M3. No se modificó la base ni se generó migración correctiva. Próximo:
inventariar procedencia del drift y definir corrección que conserve los índices.
Regímenes especiales restantes siguen pendientes de decisión explícita de alcance.
Diseño §40; revisión focalizada, sin commit.

## 2026-10-06 — M3-T1: representación HTTP verificada

M3-T1 EN PROGRESO. Cuatro casos HTTP aprobados para representante legal y
mandatario, con y sin salud: asociaciones, rechazo sin alterar el vigente,
reparación a titular, reemplazo y protección posterior. Representación sensible
sigue requiriendo revisión; mandato completo no evita ese límite de producto.

Suite completa: **1429 passed en 140.16s**. Black/Ruff/whitespace correctos.
Solo pruebas y documentación; sin migración nueva ni commit. Diseño §39.
Próximo: revisión final de diff/cadena Alembic y decisión explícita del alcance
de regímenes pendientes antes de declarar DONE.

## 2026-10-06 — M3-T1: representación y criterios de cierre revisados

M3-T1 EN PROGRESO. Diseño §38 consolida el límite actual de representación
sensible y los criterios de cierre. Representante legal/mandatario conservan
revisión; soporte específico y alcance granular siguen pendientes.

Próximo paso: comprobar por HTTP ambos valores, con y sin salud, conservación
del vigente ante rechazo y reparación a titular. Después: validación integral,
revisión final de cambios y delimitación explícita de regímenes pendientes.

Solo documentación; sin pruebas reejecutadas, migraciones ni commit.
Última suite completa: 1407 passed; después, 35 verificaciones focalizadas.

## 2026-10-06 — M3-T1: evidencia conjunta con RAT real

M3-T1 EN PROGRESO. Salud, consentimiento sensible y geolocalización preparados
juntos: seis casos HTTP nuevos y doce concurrentes con constructor RAT real,
PostgreSQL/app_user/RLS. Cambios durante bloqueo se revalidan; rechazo conserva
el vigente y reparación permite reemplazo. Se mantienen asociaciones y EIPD.

Validación focalizada: 25 pruebas de concurrencia y 10 HTTP conjuntas aprobadas.
Alcance nuevo: consentimiento_art12, salud en contexto otro. Otras cinco bases
conservan concurrencia de salud con RAT simulado. Última suite completa anterior:
1407 passed; no reejecutada en este paso de pruebas/documentación.

Sin cambios de implementación, migración nueva ni commit. Diseño §37.
Próximo: revisar representación sensible y criterios de cierre M3-T1.

## 2026-10-06 — M3-T1: integración de confirmación de salud preparada

M3-T1 EN PROGRESO. Detector admite salud_perfil_biologico_art16bis por
consentimiento preparado, junto al consentimiento sensible preparado. Contextos
restringidos siguen revisión; excepciones/rutas no soportadas y representación
no se habilitan. EIPD evalúa preparación de la propuesta de salud; pendiente
mantiene ruta_especial_pendiente. No interpreta la base art13 como excepción.

Gate GET/POST comparte salud_no_preparada; POST revalida tras bloqueo. Se conservan
regímenes detectados, asociaciones, bases ordinarias y screening EIPD negativo.
Preparación documental no verifica externamente normas o evidencia.

Validación: **1407 passed**. HTTP seis bases con contexto otro/laboral, preparación
pendiente, EIPD positivo, conservación del vigente, reemplazo y protección de
confirmado. Transversal: salud/sensible/geolocalización simultáneos, cada supuesto
EIPD y regímenes concurrentes bloqueados. PostgreSQL/app_user/RLS con RAT simulado:
rollback/fallo de flush y concurrencia de salud con seis bases, incluida relectura
del expediente cambiado a pendiente durante bloqueo. No afirmar RAT real en estos
nuevos casos transaccionales. Black/Ruff/whitespace correctos.

Sin migración nueva ni commit. Próximo paso: cubrir HTTP conjunto salud/sensible/
geolocalización y ampliar concurrencia de salud con constructor RAT real.

## 2026-10-06 — M3-T1: evaluador y readiness de salud

M3-T1 EN PROGRESO. Evaluador puro de salud revalida contratos y propaga motivos
checklist/sensible. Completitud de referencias sanitarias, evidencia, contexto,
finalidad/rol/alcance y condicionales de cesión/muestras. Contextos restringidos
mantienen revisión incluso con referencias y respuestas completas. No verifica
jurídicamente las normas ni consulta URLs. Orden determinista e inmutabilidad.

Readiness añade health nullable cuando hay documento o régimen detectado;
preparación pendiente agrega salud_no_preparada. Completo no habilita confirmación:
detector mantiene validador_no_implementado de salud. GET no cambia asociaciones.

Validación: suite completa **1354 passed**, incluidas 65 pruebas puras y dos HTTP
nuevas. Ajuste final del motivo de condición ausente verificado con las **65
pruebas puras** tras la ejecución general. Black/Ruff/whitespace correctos.
Sin migración ni commit; head local e28a0c3f6d97. Próximo paso: integrar gate de
salud exclusivamente para la ruta preparada del primer soporte, conservando
restricciones, regímenes concurrentes y EIPD.

## 2026-10-06 — M3-T1: persistencia y asociaciones de salud

M3-T1 EN PROGRESO. Health_assessment disponible en CREATE/PATCH/GET; JSONB
nullable con SQL NULL/check objeto. Migración aditiva e28a0c3f6d97 aplicada local
tras d17f9b2e5c86. Omisión conserva, objeto reemplaza y null borra borrador.

Guardados actuales usan especiales v8/EIPD v9 incluyendo documento final de
salud. Comparadores anteriores se conservan; documento no nulo con especiales
v1–v7/EIPD v1–v8 requiere asociacion_salud_no_cubierta. Cambio sin reaporte deja
asociaciones obsoletas. Residual de salud bloquea; régimen declarado sigue con
validador_no_implementado. No se añade evaluador/readiness específico ni gate.

Validación: **1287 passed** en suite completa. Nueve casos HTTP nuevos de salud:
versiones históricas con/sin documento, tenant, fechas/URL, omisión/borrado SQL,
check objeto, guardado conjunto, obsolescencia y rechazo sin mutación. Caso de
salud con sensible sin expediente rechaza 400 por precedencia de incompletitud.
Black/Ruff/whitespace correctos. Sin commit. Próximo paso: evaluador puro de salud
y preparación nullable en readiness, conservando bloqueo de confirmación.

## 2026-10-06 — M3-T1: schema del expediente de salud

M3-T1 EN PROGRESO. Implementados HealthAssessmentV1, HealthLegalReferenceV1 y
HealthCollectionContextV1 según §32. Contratos cerrados, borradores parciales,
route consentimiento_expreso, listas independientes y contextos duplicados
rechazados. Referencias usan HttpUrl (http/https) con serialización JSON textual;
no verifican fuente/contenido/vigencia externamente. Fechas factuales conservadas.

Validación focalizada **107 passed**, incluidas 49 pruebas nuevas y compatibilidad
con schemas previos. Black/Ruff/whitespace correctos. Última suite completa
anterior 1217 passed, no repetida para contrato aislado. Salud sigue bloqueada;
no exposición HTTP, persistencia ni evaluador añadidos. Sin migración ni commit.
Próximo paso: persistencia/exposición y asociaciones especiales v8/EIPD v9.

## 2026-10-06 — M3-T1: contrato y matriz documental de salud

M3-T1 EN PROGRESO. Definido diseño §32 HealthAssessmentV1, referencias sanitarias,
contextos de recolección, cesión/muestras, evidencia y condicionales. Ruta inicial
con consentimiento preparado; contextos restringidos conservan revisión incluso
con documentación, hasta validador propio. Alcance conservador coincide con
consentimiento sensible; no se infiere clasificación sanitaria desde flags M2.

Fuente oficial artículo 16 bis revisada completa. Solo documentación: salud sigue
bloqueada, sin schema/persistencia/gate nuevos ni commit. Próximo paso: schema y
pruebas de contrato. Última suite completa anterior 1217 passed; última ampliación
concurrencia 13 passed. No se repiten pruebas por diseño documental.

## 2026-10-06 — M3-T1: priorización de salud/perfil biológico

M3-T1 EN PROGRESO. Diseño §31 prioriza salud_perfil_biologico_art16bis con primer
alcance documental por consentimiento expreso. Prerrequisito sensible no sustituye
fundamento sanitario/contexto propios. Excepciones y regímenes concurrentes no se
habilitan. Fuente oficial referenciada; contrato físico/matriz quedan como próximo
paso. No se confunde delimitación con implementación.

Cambio exclusivamente documental, sin repetir pruebas. Última suite completa
anterior 1217 passed; última ampliación de concurrencia 13 passed (8 nuevos).
Sin código/migración ni commit. Régimen de salud continúa bloqueado.

## 2026-10-06 — M3-T1: concurrencia con constructor RAT real

M3-T1 EN PROGRESO. Ampliada evidencia con base consentimiento y coexistencia
sensible/geolocalización: dos conexiones PostgreSQL/app_user/RLS, filas M2 y
constructor reales, espera observada por pg_blocking_pids y borrador precargado
en segunda sesión. Commit/rollback de primera confirmación, cambios pendientes
de ambos documentos y cambio de sensibilidad M2 durante espera; rechazo conserva
confirmado y snapshots. No se extrapola RAT real a las otras cinco bases.

Validación: 8 casos nuevos aprobados; módulo test_concurrent_creation_licitud.py
completo **13 passed**. Black/Ruff/whitespace correctos. Última suite completa
anterior **1217 passed**, no repetida por ampliación focalizada de pruebas.
Matriz/backlog actualizados. Sin implementación/migración nueva ni commit.
Siguiente paso: priorizar y delimitar próximo régimen especial pendiente.

## 2026-10-06 — M3-T1: coexistencia HTTP sensible/geolocalización

M3-T1 EN PROGRESO. Cerrada brecha HTTP conjunta de la matriz de aceptación;
backlog actualizado. Cuatro casos contra PostgreSQL/app_user/RLS con RAT real:
confirmación preparada, no/pendiente de cualquiera, obsolescencia/reaporte,
coherencia GET/POST especial/EIPD, rechazo sin modificar confirmado ni borrador,
EIPD positivo, reparación/reemplazo y protección de confirmado.

Validación focalizada: **4 passed, 85 deselected**; Black/Ruff/whitespace correctos.
Última suite completa anterior: **1217 passed**, no repetida porque esta etapa
solo añade cobertura y documentación. Sin cambios de implementación, migración
ni commit. Próximo paso: revisar concurrencia con constructor RAT real.

## 2026-10-06 — M3-T1: revisión de aceptación, paso 1

M3-T1 EN PROGRESO. Contrastados diseño, código y pruebas; matriz en
m3-t1-revision-aceptacion.md y referencia añadida a docs/backlog.md, que carecía
de entrada M3-T1. Distingue implementación probada, funcionalidad pendiente,
límites de evidencia y diferidos explícitos. EIPD completo no es brecha de esta
etapa; frontend requiere delimitación de roadmap.

Siguiente recomendado: evidencia HTTP conjunta sensible/geolocalización, después
revisión del límite RAT simulado en concurrencia y priorización de régimen.
Última suite completa anterior 1217 passed; revisión solo documental, sin repetir
suite. Sin cambios de código/migración ni commit.

## 2026-10-06 — M3-T1: confirmación por consentimiento expreso sensible

M3-T1 permanece **EN PROGRESO**. Integrada exclusivamente la condición
sensibles_art16/consentimiento_expreso_art16 por consentimiento preparado.
Detector conserva todos los regímenes detectados; otras rutas sensibles y
regímenes sin validador siguen bloqueados. Coexistencia con geolocalización
preparada conserva las barreras concurrentes y el screening EIPD negativo.

Gate compartido GET/POST incluye consentimiento_sensible_no_preparado y vuelve
a evaluar checklist, alcance, evidencia, medio y representación. EIPD requiere
revisión de consentimiento sensible propuesto sin preparación; no lo convierte
en excepción ni omite respuestas. Bases art13 conservan sus propios requisitos.

Validación: **1217 passed** en suite completa. HTTP con seis bases/tres medios,
EIPD positivo, preparación pendiente, protegido confirmado, conservación del
vigente ante rechazo y reemplazo sensible/ordinario. PostgreSQL con app_user/RLS:
rollback, fallo de flush y concurrencia sensible con seis bases; relectura tras
bloqueo ante cambio de prueba a pendiente. RAT simulado en pruebas transaccionales,
RAT real en HTTP. Regímenes concurrentes y coexistencia sensible/geolocalización
cubiertos en evaluador transversal. Black/Ruff/whitespace correctos.

Sin commit ni migración nueva; head local d17f9b2e5c86. Siguiente paso: revisar
brechas de aceptación restantes de M3-T1 y priorizar el próximo régimen pendiente.

## 2026-10-06 — M3-T1: preparación del consentimiento expreso sensible

M3-T1 permanece **EN PROGRESO**. Implementado evaluador puro del expediente
sensible según §24: checklist general reutilizado, medios coherentes, evidencia,
finalidad/rol, representación pendiente y selectores independientes. Requiere
cobertura de categorías sensibles y todos los grupos del alcance RAT; no infiere
una matriz de pares. Tecnología tiene aplicabilidad condicional y residuales.
Fechas/versiones son apoyos opcionales; no deciden vigencia automáticamente.

Readiness añade sensitive_consent nullable al existir expediente o propuesta de
ruta sensible por consentimiento. Preparación pendiente agrega
consentimiento_sensible_no_preparado; contrato inválido conserva rechazo.
No se habilita el gate sensible: incluso preparado mantiene el validador especial
pendiente y POST confirm rechaza sin alterar el borrador.

Validación: **1159 passed** en suite completa, incluidas 74 pruebas del evaluador
más HTTP con tres medios, preparación completa, obsolescencia y borrado.
Black/Ruff/whitespace correctos. Sin commit ni migración nueva; head local sigue
d17f9b2e5c86. Siguiente paso: integración transversal de la ruta sensible preparada,
con controles concurrentes, EIPD y compatibilidad GET/POST.

## 2026-10-06 — M3-T1: persistencia y asociaciones del consentimiento sensible

M3-T1 permanece **EN PROGRESO**. Sensitive_consent_assessment disponible en
CREATE/PATCH/GET con JSONB nullable, SQL NULL y restricción de objeto.
Omisión conserva; objeto reemplaza; null borra únicamente borrador.
Migración aditiva d17f9b2e5c86 aplicada localmente después de c06e8a1d4b75.

Nuevos guardados usan asociaciones especiales v7/EIPD v8 incluyendo expediente
sensible final. Comparadores históricos se conservan: documento no nulo con
especiales v1–v6/EIPD v1–v7 requiere revisión por asociación no cubierta.
Cambios sin reaporte dejan asociaciones obsoletas; GET no las reescribe.
Expediente residual bloquea y sensibles declarados siguen con validador pendiente.

Validación: **1082 passed** en suite completa, Black/Ruff/whitespace correctos.
Cobertura HTTP: tenant, fechas, contratos inválidos, omisión/borrado SQL NULL,
check objeto, guardado conjunto, obsolescencia, versiones históricas con/sin
expediente y rechazo de confirmación sensible preservando borrador.
Sin commit. Siguiente paso: evaluador puro y preparación sensible en readiness;
la habilitación transversal permanece pendiente.

## 2026-10-06 — M3-T1: contrato del expediente de consentimiento sensible

M3-T1 permanece **EN PROGRESO**. Añadido SensitiveConsentAssessmentV1 según
§24: borradores parciales, tres medios expresos, fechas factuales, alcance,
respuestas y evidencia. Contrato cerrado; no admite aprobación del cliente.
Los contratos anteriores se conservan. Esta etapa todavía no expone el nuevo
expediente en CREATE/PATCH/GET ni añade persistencia o asociaciones.

Validación focalizada: **58 passed** (30 pruebas nuevas y esquemas existentes);
Black y Ruff correctos. Última suite completa anterior: **1044 passed**.
Sin commit ni nueva migración; ruta sensible continúa bloqueada.

Siguiente paso: persistencia y exposición del expediente junto con asociaciones
especiales v7/EIPD v8 y protección de expedientes residuales.

## 2026-10-06 — M3-T1: diseño de consentimiento expreso sensible

M3-T1 permanece **EN PROGRESO**. Definido §24 para sensibles_art16 por
consentimiento_expreso_art16: declaración/medios expresos, prueba y cobertura
sensible coherente con checklist/RAT. Expediente independiente y asociaciones
especiales v7/EIPD v8 propuestas preservan históricos. Primer soporte titular;
representación y otros regímenes requieren validadores propios. EIPD no se omite.

Paso documental; ruta sensible sigue bloqueada. Última suite **1044 passed**;
no se repite por cambios solo documentales. Whitespace correcto. Sin commit ni
migraciones nuevas. Fuente oficial citada en diseño.

Siguiente paso: schemas/persistencia/asociaciones de consentimiento sensible,
manteniendo bloqueo; después evaluador y gate transversal.

## 2026-10-06 — M3-T1: confirmación especial de geolocalización

M3-T1 permanece **EN PROGRESO**. Geolocalización preparada integra el detector
especial y la coherencia EIPD. Resultado regimenes_preparados conserva regímenes;
gate compartido admite geolocalización completa con asociación vigente, base
preparada y screening EIPD negativo. Otros regímenes/vulnerabilidad/EIPD positivos
siguen bloqueando. Pending_controls distingue validadores especiales restantes.

Validación: **1044 passed**. HTTP con seis bases, motivos GET/POST, rechazo con
conservación de vigente, EIPD positivo y reemplazo en ambas direcciones;
rollback/fallo de flush y concurrencia PostgreSQL con/sin geolocalización para
las seis bases, incluido cambio del aviso a pendiente tras espera de bloqueo.
Cada supuesto EIPD y régimen concurrente, residuales/contexto obsoleto y reglas
no implementadas siguen bloqueados. Formato/lint/whitespace correctos.
Sin commit ni nuevas migraciones.

Siguiente paso: definir documentalmente el validador de consentimiento expreso
para datos sensibles art16, preservando regímenes concurrentes y controles EIPD.
No cerrar M3-T1: otros validadores especiales y gestión EIPD pendientes.

## 2026-10-06 — M3-T1: preparación de geolocalización

M3-T1 permanece **EN PROGRESO**. Evaluador puro de geolocalización implementado:
aviso/entrega, respuestas fundadas, terceros condicionales, evidencia y scope
coherente con RAT/declaración/condición. Readiness expone geolocation cuando hay
expediente o régimen; null si ambos ausentes. Preparación completa no elimina
bloqueos especiales/EIPD; confirmación especial sigue pendiente.

Validación: **996 passed**. Faltantes/negativas/pendientes, ambas declaraciones
factuales, condicionales/residuales, alcance propio/externo, finalidad/rol,
referencias/evidencia, contratos inválidos, canonización, orden/inmutabilidad y
HTTP con tenant/contexto actual. Formato/lint/whitespace correctos.
Sin commit ni nuevas migraciones. No se certifica aviso/entrega desde fechas.

Siguiente paso: integrar resultado en detector especial y coherencia EIPD,
admitiendo solo geolocalización preparada y manteniendo bloqueos concurrentes;
probar gates compartidos, rollback/relectura/concurrencia y seis bases.

## 2026-10-06 — M3-T1: persistencia de geolocalización

M3-T1 permanece **EN PROGRESO**. GeolocationAssessmentV1 admite borradores
cerrados/parciales de aviso, entrega, scope, respuestas y evidencia factual.
Migración c06e8a1d4b75 aplicada localmente, check SQL NULL/objeto. Nuevas
asociaciones especiales v6/EIPD v7 incluyen expediente final; comparadores
históricos preservados, documento no nulo exige revisión en versiones anteriores.
Documento residual y régimen declarado siguen bloqueando confirmación.

Validación: **931 passed**. Fechas, campos/respuestas/versiones inválidos,
omisión/null SQL/check objeto, protección tenant, cambio sin reaporte, guardado
conjunto y todas las asociaciones históricas; prueba explícita de régimen
persistido sin habilitar confirmación. Bases anteriores/concurrencia preservadas.
Formato/lint/whitespace correctos. Sin commit.

Siguiente paso: evaluador de preparación de geolocalización y salida específica
en readiness; después integrar gate especial y coherencia EIPD.

## 2026-10-06 — M3-T1: cobertura ordinaria y diseño de geolocalización

M3-T1 permanece **EN PROGRESO**. Revisados gates y cobertura real de las seis
bases ordinarias. Definido §23: primer validador especial de geolocalización
art16sexies, información específica, scope, condicionales y contrato documental.
Columna independiente/asociaciones especiales v6/EIPD v7 propuestas preservan
históricos. Integración futura debe mantener bloqueos EIPD y otros regímenes.

Paso documental, ninguna confirmación especial habilitada. Última suite
**914 passed**; sin repetirla por cambios solo documentales. Whitespace correcto.
Sin commit ni migraciones nuevas. Fuente oficial citada en diseño.

Siguiente paso: schemas/persistencia/asociaciones de geolocalización, manteniendo
bloqueo especial; después evaluador y gate transversal.

## 2026-10-06 — M3-T1: confirmación ordinaria de obligaciones económicas

M3-T1 permanece **EN PROGRESO**. Art13a confirma con expediente económico
completo, RAT actual y controles especiales/EIPD negativos vigentes. Gate
compartido con readiness: incompleto400/revisión409 y mismos motivos.
Ambas rutas/cuatro tipos, sin exigir expedientes de otras bases. No certifica
admisibilidad de una deuda ni verifica fuentes externas.

Validación: **914 passed**. HTTP rechazo/conservación/reemplazo y protección del
confirmado; rollback/fallo de flush y concurrencia PostgreSQL para seis bases,
incluido cambio pendiente mientras otro confirmador espera el bloqueo.
Formato/lint/whitespace correctos. Sin nuevas migraciones ni commit.

Las seis bases ordinarias tienen gate; regímenes especiales positivos, gestión
EIPD y excepciones judiciales económicas siguen pendientes. No cerrar M3-T1.
Siguiente paso: revisar cobertura conjunta de las seis bases y definir el primer
validador especial pendiente con su alcance documental antes de habilitarlo.

## 2026-10-06 — M3-T1: preparación de obligaciones económicas

M3-T1 permanece **EN PROGRESO**. Evaluador económico puro implementado con
completitud/aplicabilidad, declaración factual coherente con ruta, referencias,
evidencia y motivos ordenados. Readiness expone economic_obligations contra RAT
actual; confirmación art13a permanece bloqueada aun con preparación completa.
No verifica fuentes externas ni calcula prescripción/exigibilidad.

Validación: **885 passed**. Ambas rutas/cuatro tipos, faltantes, respuestas y
precedencia, declaración factual, condicionales/residuales, referencias/evidencia,
finalidad/rol, canonización, orden/inmutabilidad y HTTP con tenant/contexto actual.
Formato/lint/whitespace correctos. Sin commit ni nuevas migraciones.

Siguiente paso: gate económico compartido en confirmación, con controles
transversales negativos vigentes; probar rechazo/reemplazo, rollback,
relectura tras lock y concurrencia PostgreSQL para seis bases.

## 2026-10-06 — M3-T1: persistencia de obligaciones económicas

M3-T1 permanece **EN PROGRESO**. EconomicObligationsAssessmentV1 permite
borradores cerrados/parciales, con rutas/tipos, referencias y evidencia factual.
Migración bf5d7f9c3a64 aplicada localmente, check SQL NULL/objeto. Nuevas
asociaciones especiales v5/EIPD v6 incluyen expediente final; históricos no se
reescriben y versiones anteriores requieren revisión con económico no nulo.
Evaluador/readiness específicos pendientes; confirmación art13a bloqueada.

Validación: **813 passed**. Dos rutas/cuatro tipos, campos/enums/respuestas
inválidos, fechas, omisión/null SQL/check objeto, protección tenant, cambios sin
reaporte, guardado conjunto y todas las versiones históricas. Formato/lint/
whitespace correctos. Bases anteriores y concurrencia conservadas. Sin commit.

Siguiente paso: evaluador económico de completitud/aplicabilidad y motivos en
readiness; después gate transaccional compartido.

## 2026-10-06 — M3-T1: contrato documental de obligaciones económicas

M3-T1 permanece **EN PROGRESO**. Definido §22 para art13a: obligación concreta,
revisión de Título III, rutas con/sin comunicación y requisitos condicionales.
Diseño de EconomicObligationsAssessmentV1, persistencia, asociaciones especiales
v5/EIPD v6, evaluador/readiness y gate posterior. Situación socioeconómica no
elimina controles sensibles; excepciones judiciales requieren revisión específica.
Fuente oficial art13a y versión diferida BCN referenciadas en diseño.

Paso documental: art13a sigue bloqueado en código. Última suite **793 passed**;
no se repite por cambios únicamente documentales. Whitespace verificado.
Sin commit ni nuevas migraciones.

Siguiente paso: implementar schemas/persistencia y asociaciones v5/v6
compatibles; luego evaluador y confirmación transaccional.

## 2026-10-06 — M3-T1: confirmación ordinaria de defensa de derechos

M3-T1 permanece **EN PROGRESO**. Art13e confirma con expediente de derechos
completo, contexto RAT actual y controles especiales/EIPD negativos vigentes.
Gate compartido con readiness: incompleto 400, revisión 409 y mismos motivos.
Tres rutas y dos tipos de foro; no valida competencia jurídica ni exige
expedientes de otras bases. Art13a y controles especiales positivos siguen
bloqueados; gestión EIPD pendiente.

Validación: **793 passed**. Flujo HTTP real con rechazo/conservación/reemplazo,
protección de confirmados; rollback, fallo de flush y concurrencia PostgreSQL
para cinco bases, con relectura de cambios después del bloqueo. Formato/lint/
whitespace correctos. Migración vigente ae4c6e8b2f53; sin nuevas migraciones ni
commit.

Siguiente paso: definir documentalmente el expediente de obligaciones económicas
art13a y su aplicabilidad antes de schemas, persistencia y confirmación.

## 2026-10-06 — M3-T1: preparación de defensa de derechos

M3-T1 permanece **EN PROGRESO**. Implementado evaluador puro de derechos con
completitud, aplicabilidad por etapa y motivos ordenados. Readiness expone
rights_defense contra RAT actual; preparación completa no habilita todavía
confirmación art13e. No se infieren competencia jurídica ni plazos.

Validación: **769 passed**. Tres rutas/dos foros, etapas y condicionales,
faltantes, negativas/pendientes/fundamentos, residuales, evidencia, precedencia,
canonización, orden/inmutabilidad y API con tenant/contexto actual. Formato,
lint y whitespace correctos. Sin commit ni migraciones nuevas.

Siguiente paso: integrar gate de derechos compartido en confirmación, con
controles transversales negativos vigentes; probar rechazo/reemplazo,
rollback, relectura tras lock y concurrencia PostgreSQL.

## 2026-10-06 — M3-T1: persistencia de defensa de derechos

M3-T1 permanece **EN PROGRESO**. RightsDefenseAssessmentV1 guarda borradores
cerrados/parciales con rutas, foros, etapas y metadata de evidencia.
Migración ae4c6e8b2f53 aplicada localmente, check SQL NULL/objeto.
Asociación especial v4/EIPD v5 incluye expediente final; históricos no se
reescriben y versiones anteriores requieren revisión con derechos no nulos.
Evaluador y readiness específicos pendientes; confirmación art13e bloqueada.

Validación: **727 passed**. Persistencia/fechas, campos/enums/respuestas inválidos,
omisión/null SQL, check objeto, protección tenant, cambios sin reaporte,
guardado conjunto y compatibilidad histórica. Formato/lint/whitespace correctos.
Sin commit. Bases ordinarias habilitadas y concurrencia siguen pasando.

Siguiente paso: evaluador de preparación de derechos con completitud,
aplicabilidad por etapa y motivos en readiness; después gate transaccional.

## 2026-10-06 — M3-T1: contrato documental de defensa de derechos

M3-T1 permanece **EN PROGRESO**. Definido §21 para defensa_derechos_art13e:
formulación/ejercicio/defensa ante tribunal u órgano público, derecho concreto,
conexión, necesidad, etapas y documentación condicional. Texto oficial art13(e)
verificado en Diario Oficial. Preparación para formular no exige causa iniciada.
Se fijan schemas, persistencia, asociaciones especiales v4/EIPD v5 compatibles,
evaluador/readiness y gate posterior; régimen sensible art16d sigue separado.

Paso documental: la base continúa bloqueada en código. Última suite **721 passed**;
no se repite por cambios solo de diseño. Whitespace correcto. Sin commit.

Siguiente paso: implementar schemas/persistencia y asociaciones nuevas,
manteniendo confirmación bloqueada; después evaluador y gate transaccional.

## 2026-10-06 — M3-T1: confirmación ordinaria de obligación legal

M3-T1 permanece **EN PROGRESO**. Obligación legal confirma con expediente
normativo completo y controles especiales/EIPD negativos vigentes. Gate
compartido con readiness, catálogo de bases habilitadas común y motivos
GET/POST compatibles. Incompleto 400, revisión 409. No exige expedientes de
otras bases ni verifica contenido/vigencia externa de fuentes normativas.

Validación: **721 passed**. Ambas rutas, rechazo/reemplazo HTTP, conservación
de anterior, cambio sin reaporte, controles positivos y rollback/fallo de flush/
concurrencia PostgreSQL para cuatro bases. Formato/lint/whitespace correctos.
Sin commit ni migraciones nuevas. Art13a/art13e y regímenes positivos siguen
bloqueados; gestión EIPD pendiente.

Siguiente paso: definir el expediente de defensa de derechos art13e, con
alcance/documentación y controles antes de habilitarlo.

## 2026-10-06 — M3-T1: preparación normativa en readiness

M3-T1 permanece **EN PROGRESO**. Implementado evaluador puro de obligación
legal con completitud/aplicabilidad, referencias, respuestas fundadas y motivos
ordenados; readiness expone legal_obligation contra RAT actual. No verifica
contenido, autenticidad o vigencia externa de fuentes. Confirmación sigue
bloqueada incluso con expediente preparado.

Validación: **705 passed**. Ambas rutas, faltantes, negativas/pendientes,
referencias/evidencias incompletas, residuales, precedencia, canonización,
orden/inmutabilidad y API con tenant/contexto actual. Formato/lint/whitespace
correctos. Sin commit ni nuevas migraciones.

Siguiente paso: integrar gate normativo compartido en confirmación, exigiendo
completo y controles transversales negativos vigentes; probar reemplazo,
rechazo, rollback, relectura tras lock y concurrencia PostgreSQL.

## 2026-10-05 — M3-T1: persistencia de obligación legal

M3-T1 permanece **EN PROGRESO**. LegalObligationAssessmentV1 guarda borradores
cerrados/parciales con referencias normativas, URLs sintácticas y fechas.
Migración 9e3b5d7f1a42 aplicada localmente con check SQL NULL/objeto.
Nuevo guardado vincula asociación especial v3/EIPD v4 al expediente final;
históricos no se reescriben y las versiones no cubiertas requieren revisión.
Obligación legal sigue bloqueada en confirmación; evaluador específico pendiente.

Validación: **670 passed**. Persistencia, campos/URL/respuestas inválidas,
SQL NULL/check objeto, protección tenant, cambio sin reaporte, asociaciones
finales y compatibilidad de versiones. Formato/lint/whitespace correctos.
Sin commit. No se accede a red desde las URLs del expediente.

Siguiente paso: evaluador puro de preparación normativa y salida específica
en readiness, manteniendo confirmación bloqueada hasta integrar su gate.

## 2026-10-05 — M3-T1: contrato documental de obligación legal

M3-T1 permanece **EN PROGRESO**. Definido §20 para obligacion_legal_art13b,
rutas obligación legal/tratamiento dispuesto por ley y referencias normativas
con versión, disposición, fuente y análisis. Verificado artículo 13(b) en
Diario Oficial. Se definen schemas cerrados, preparación/aplicabilidad,
asociaciones especiales v3/EIPD v4 y compatibilidad sin reescribir históricos.
No se afirma validación automática de autenticidad/vigencia de fuentes.

Paso documental; la base sigue bloqueada en el código. Última suite ejecutada:
**665 passed**; no se repite por cambios solo de diseño. Whitespace correcto.
Sin commit.

Siguiente paso: schemas/persistencia y nuevas asociaciones, manteniendo
confirmación bloqueada; después evaluador/readiness y gate transaccional.

## 2026-10-05 — M3-T1: confirmación contractual ordinaria

M3-T1 permanece **EN PROGRESO**. Contrato/precontractual confirma con expediente
completo y controles especiales/EIPD negativos vigentes. Gate compartido con
readiness, motivos GET/POST coherentes; incompleto 400 y revisión 409.
No exige consentimiento o LIA. Evalúa después de lock/refresco y antes de
reemplazar, sin modificar documentos/asociaciones. Otras bases/regímenes
positivos y continuación tras EIPD afirmativa siguen bloqueados.

Validación: **665 passed**. Tres rutas completas; rechazo/obsolescencia,
reemplazo API consentimiento -> precontractual -> consentimiento, conservación
de anterior, rollback/fallo de flush y concurrencia PostgreSQL para tres bases.
Formato/lint/whitespace correctos. Sin commit ni migraciones adicionales.

Siguiente paso: definir el expediente de obligación legal art13b y su referencia
normativa verificable, antes de implementar o habilitar esa base.

## 2026-10-05 — M3-T1: preparación contractual en readiness

M3-T1 permanece **EN PROGRESO**. Implementado evaluador contractual puro con
completitud, aplicabilidad y motivos ordenados/inmutables. Readiness expone
contract para la base contractual contra RAT actual. Distingue celebración,
ejecución y medidas solicitadas; precontractual no exige contrato firmado.
Referencias opcionales de apoyo se conservan; evidencia aportada incompleta y
respuestas residuales se señalan. Confirmación contractual sigue bloqueada.

Validación: **650 passed**; rutas completas, faltantes, negativas/pendientes,
fundamentos, residuales, evidencia, contexto, rol, canonización, orden y lectura
HTTP sin mutaciones/otro tenant. Formato/lint/whitespace correctos. Sin commit.
No se añaden migraciones en este paso.

Siguiente paso: integrar gate contractual compartido en confirmación ordinaria
cuando completo y con controles transversales negativos vigentes; verificar
reemplazo, rechazo, rollback, relectura tras lock y concurrencia.

## 2026-10-05 — M3-T1: persistencia contractual y asociaciones nuevas

M3-T1 permanece **EN PROGRESO**. ContractAssessmentV1 guarda borradores cerrados
y parciales en contract_assessment; CREATE/PATCH/GET admiten fechas, omisión y
null SQL. Migración 8d2f4a6c9e31 aplicada localmente con check NULL/objeto.
Nuevo guardado usa asociación especial v2/EIPD v3 con contrato final; conserva
históricos y señala asociaciones anteriores no cubiertas cuando hay contrato.
La confirmación contractual continúa bloqueada; evaluador sigue pendiente.

Validación: **616 passed**. Incluye persistencia, fechas, invalidaciones,
SQL NULL/check objeto, protección tenant, cambio sin reasociar, guardado conjunto
y versiones históricas. Flujos consentimiento/LIA y concurrencia siguen pasando.
Formato/lint/whitespace correctos. Sin commit.

Siguiente paso: evaluador contractual puro con completitud, aplicabilidad y
motivos según §19.3; integrarlo en readiness antes de habilitar confirmación.

## 2026-10-05 — M3-T1: contrato de la siguiente base ordinaria

M3-T1 permanece **EN PROGRESO**. Definido §19 para contrato_precontractual_art13c:
rutas celebración/ejecución/medidas solicitadas por titular, expediente cerrado,
completitud/aplicabilidad y matriz de aceptación. Referencia oficial BCN revisada.
Se propone columna contractual propia y evolución de asociaciones especiales
v2/EIPD v3, sin reescribir históricos. Implementación dividida en persistencia,
evaluador y confirmación.

Paso documental: la nueva base sigue bloqueada en el código. Última suite:
**612 passed**; no se repite por cambios solo documentales. Whitespace correcto.
Sin commit.

Siguiente paso: schemas/persistencia contractual y asociaciones nuevas con
compatibilidad histórica, manteniendo confirmación contractual bloqueada.

## 2026-10-05 — M3-T1: confirmación ordinaria de interés legítimo

M3-T1 permanece **EN PROGRESO**. Interés legítimo ya confirma con LIA completo
recalculado contra RAT actual y controles especiales/EIPD negativos completos
y vigentes. Barrera LIA compartida con readiness; incompleto 400, revisión 409.
Consentimiento preparado no se exige para esta base. Otras bases y regímenes
positivos siguen bloqueados; EIPD afirmativa no permite continuar.

Validación: **612 passed**. Flujo API real consentimiento -> LIA -> consentimiento,
motivos GET/POST, rechazo sin reemplazo y bloqueo EIPD con LIA completa.
Rollback/fallo de flush y concurrencia PostgreSQL parametrizados para ambas
bases, incluida relectura tras actualización LIA. Formato/lint/whitespace
correctos. Sin commit, sin nuevas migraciones ni permisos.

Siguiente paso: revisar cobertura residual de M3-T1 y definir el contrato de
la siguiente base jurídica ordinaria antes de habilitarla; validadores
especiales y expediente EIPD siguen pendientes.

## 2026-10-05 — M3-T1: contrato de habilitación LIA ordinaria

M3-T1 permanece **EN PROGRESO**. Revisada cobertura real y definido §18.29:
interés legítimo requerirá LIA completo con RAT actual, detección especial
negativa y EIPD negativo, ambos vigentes. Decisión favorable aislada no basta.
Se fijan rechazos, asociaciones, expediente residual de consentimiento,
coherencia readiness/POST y aceptación de reemplazo/concurrencia/rollback.

Paso documental: LIA sigue bloqueada en el código actual. No se habilitan otras
bases ni regímenes especiales. Última suite ejecutada: **600 passed**; no se
repite por cambios solo documentales. Whitespace correcto. Sin commit.

Siguiente paso: implementar selección de base y barrera LIA compartida, adaptar
readiness y verificar los casos de §18.29 con PostgreSQL/app_user.

## 2026-10-05 — M3-T1: confirmación ordinaria con controles transversales

M3-T1 permanece **EN PROGRESO**. Implementado gate compartido para readiness
y confirmación: exige detección especial y screening EIPD negativos completos
con asociaciones vigentes, además del consentimiento. Ausencia bloquea; rutas
especiales positivas, LIA y continuación tras EIPD afirmativa siguen pendientes.
Los controles se evalúan después del lock/refresco y antes de reemplazar la
confirmada anterior. Los motivos transversales GET/POST coinciden.

Validación: **600 passed**. Incluye rechazo por ausencia, asociación obsoleta
con hash RAT igual, EIPD afirmativa, v1 no cubierto, relectura tras lock,
rollback HTTP con anterior conservada, reemplazo y concurrencia PostgreSQL.
Fixtures ordinarias actualizadas con declaraciones negativas explícitas;
PATCH que cambia contexto debe reaportar controles para actualizar asociaciones.
Formato, lint y whitespace correctos. Sin commit.

Siguiente paso: revisar cobertura residual y definir el contrato para habilitar
interés legítimo; no se habilitará únicamente por una conclusión LIA favorable.

## 2026-10-05 — M3-T1: contrato de confirmación transversal ordinaria

M3-T1 permanece **EN PROGRESO**. §15.13 fija la próxima integración:
consentimiento preparado, detección especial y EIPD negativos completos y
vigentes. Ausencia no será una alternativa para confirmar borradores; históricos
confirmados no cambian. Se definen rechazos 400/409, evaluación compartida con
readiness, relectura tras lock, un bundle RAT y validación antes de reemplazo.

Paso documental: la confirmación actual mantiene sus bloqueos globales.
No se habilitan rutas especiales, LIA ni continuación tras EIPD afirmativa.
Última suite ejecutada: **590 passed**; no se repite por cambios solo de diseño.
Sin commit.

Siguiente paso: implementar el gate transversal compartido y adaptar pruebas
ordinarias/de concurrencia con expedientes negativos completos, además de los
casos de rechazo y rollback definidos en §15.13.

## 2026-10-05 — M3-T1: contraste EIPD/condiciones especiales

M3-T1 permanece **EN PROGRESO**. El evaluador EIPD contrasta la respuesta sobre
excepción al consentimiento con rutas especiales explícitas: excepciones no
validadas, rutas sin resolver y declaraciones discordantes/no documentadas.
Los motivos fuerzan pendiente_revision y conservan los supuestos afirmativos.
No se deducen excepciones desde legal_basis ni se habilitan autorizaciones.
Readiness expone los motivos; no hay cambios de persistencia o confirmación.

Validación: **590 passed**, incluidas matriz de rutas/respuestas, coexistencia,
contexto obsoleto, orden determinista y consulta API sin mutaciones. Formato,
lint y revisión de whitespace correctos. Sin commit.

Siguiente paso: definir la integración de preparación transversal en la
confirmación ordinaria, antes de sustituir los bloqueos globales existentes.
Validadores especiales positivos, LIA y expediente EIPD siguen pendientes.

## 2026-10-05 — M3-T1: evaluación de preparación especial

M3-T1 permanece **EN PROGRESO**. Implementado evaluador puro especial y salida
special en GET readiness: motivos, asociación vigente y regímenes coexistentes.
Compara declaraciones con RAT, exige nueve respuestas fundadas, revisa alcance,
expedientes faltantes/residuales y referencias a consentimiento. No infiere el
cruce sensible/adolescente ni habilita rutas positivas; todos sus validadores
jurídicos continúan pendientes. La confirmación conserva sus bloqueos.

Validación: **581 passed**; formato y lint correctos. Pruebas de precedencia,
coherencia RAT, contexto desactualizado, pluralidad de regímenes, ausencia,
alcance, referencias y exposición API. Sin commit.

Siguiente paso: contraste transversal EIPD/condiciones especiales, con motivos
sobre excepción al consentimiento, sin inferir autorización desde legal_basis.

## 2026-10-05 — M3-T1: persistencia especial y asociación EIPD v2

M3-T1 permanece **EN PROGRESO**. Implementados schemas cerrados de
special_conditions, guardado parcial, alcance validado contra RAT y asociación
calculada por servidor sobre snapshot/base/consentimiento/LIA finales.
CREATE/PATCH generan asociación EIPD v2 al recibir screening; omitir conserva
la asociación anterior y null elimina condiciones especiales como SQL NULL.

Los screenings v1 históricos se conservan; con condiciones especiales su
evaluación requiere revisión por asociacion_especial_no_cubierta. Las rutas
especiales siguen bloqueadas y no se acredita autorización al guardar.

Validación: **566 passed**, incluidas pruebas API de guardado, rechazo de
alcance, rollback, obsolescencia EIPD y borrado; contrato especial y
compatibilidad v1/v2. Sin commit.

Siguiente paso: evaluador de detección y preparación especial, con motivos de
completitud, aplicabilidad y contexto; después integración en readiness.

## 2026-10-05 — M3-T1: contrato de detección y condiciones especiales

M3-T1 permanece **EN PROGRESO**. §§15.6–15.9 definen declaraciones factuales,
regímenes, expedientes propuestos, motivos y asociación calculada por servidor
en special_conditions existente. Ninguna ruta jurídica positiva se habilita:
los validadores específicos permanecen no implementados.

Se fija la dependencia con EIPD: asociación v2 incluirá las condiciones
especiales finales, sin reescribir screenings v1 históricos. Un screening v1
con condiciones nuevas deberá revisarse, no reasociarse silenciosamente.

Revisión normativa contra texto oficial BCN, enlazado en el diseño. Paso solo
documental; whitespace pasa y no se repiten tests. Última suite: **558 passed**.
Sin commit. Interés legítimo y condiciones especiales continúan bloqueados.

Siguiente paso: implementar schemas y persistencia del contrato especial,
con asociación EIPD v2 y pruebas; después, evaluador de detección/preparación.

## 2026-10-05 — M3-T1: consulta API de preparación

M3-T1 permanece **EN PROGRESO**. GET /licitud/.../readiness expone resultados
consentimiento/LIA/EIPD, motivos, contexto actual, bloqueos del flujo existente
y controles transversales pendientes. Es de solo lectura con view_content,
suscripción y tenant validados. No confirma ni altera el expediente.

Los resultados se calculan con contexto RAT recompuesto. Se detecta screening
desactualizado incluso cuando el hash semántico RAT no cambia. No se presenta
la ausencia de bloqueos actuales como aprobación o cobertura completa.
Interés legítimo y screening no nulo mantienen sus barreras de confirmación.

Archivo API: **11 passed**; suite completa backend: **558 passed**. Pruebas
HTTP usan PostgreSQL/RLS y comprueban permisos, contexto, historial y ausencia
de modificaciones. Formato, lint y whitespace pasan. Sin migraciones nuevas,
sin cambios al lifecycle y sin commit.

Siguiente paso: definir detección y contrato de condiciones especiales antes
de integrar las barreras pendientes y habilitar confirmación LIA.

## 2026-10-05 — M3-T1: evaluador puro EIPD v1

M3-T1 permanece **EN PROGRESO**. evaluate_eipd_screening_v1 implementa los
tres resultados derivados, fundamentos, contexto desactualizado y revisión
de automatización declarada frente al indicador RAT. La salida es inmutable,
con motivos y observaciones LIA separados, sin persistir ni modificar entradas.

Validación: **36 casos nuevos**, archivo EIPD **47 passed**, suite completa
backend **555 passed**. Formato, lint y whitespace pasan. Sin cambios de
migraciones, API o confirmación en este bloque. Trabajo sin commit.

La API todavía no expone preparación; interés legítimo sigue bloqueado.
Siguiente paso: exponer resultados LIA/EIPD y motivos para preparar la evaluación,
manteniendo barreras de condiciones especiales antes de habilitar confirmación.

## 2026-10-05 — M3-T1: migración y persistencia screening EIPD

M3-T1 permanece **EN PROGRESO**. Migración append-only 7c9e1a3b5d20 aplicada
en desarrollo: columna nullable eipd_screening y restricción de objeto. Se
implementaron schemas, asociación documental calculada por servidor y
creación/edición/lectura API. Null elimina mediante SQL NULL; omisión conserva
la asociación anterior y permite identificar cambios de contexto posteriores.

El screening no nulo bloquea confirmación mientras falte el evaluador integrado,
para no ignorar declaraciones. Interés legítimo permanece bloqueado. No se
alteraron migraciones históricas ni el hash canónico RAT v1.

Upgrade/downgrade/re-upgrade probados en schema PostgreSQL transaccional
isolado; pruebas HTTP usan app_user con RLS. Suite específica: **49 passed**;
suite completa: **519 passed**. Formato, lint y whitespace pasan. Sin commit.
El drift global histórico de Alembic sigue fuera del alcance de este bloque.

Siguiente paso: implementar el evaluador EIPD y sus resultados/motivos,
incluyendo contexto desactualizado y contradicciones estructuradas.

## 2026-10-05 — M3-T1: contrato físico del screening EIPD

M3-T1 permanece **EN PROGRESO**. Se fija eipd_screening como JSONB nullable
independiente en legal_assessments, mediante futura migración append-only.
El contrato v1 admite declaraciones parciales en borrador y una asociación
documental calculada por servidor sobre snapshot RAT completo y LIA vigente.
No modifica el hash canónico RAT v1 ni reinterpreta versiones históricas.

Se definieron entrada/salida, reemplazo/omisión/null y detección de screening
desactualizado. La asociación no se actualiza silenciosamente al cambiar hechos.
La confirmación LIA sigue bloqueada. Columna, modelos y evaluador aún pendientes.

Paso solo documental; diff sin errores de whitespace. Última suite completa:
**506 passed**; no se repitió. Sin commit.

Siguiente paso: implementar migración, modelos y guardado del screening EIPD,
con pruebas de asociación y persistencia antes del evaluador/integración.

## 2026-10-05 — M3-T1: revisión EIPD y condiciones especiales

M3-T1 permanece **EN PROGRESO**. Se revisaron diseño, campos RAT/LIA y barreras
de confirmación. Los hechos actuales no resuelven todos los supuestos EIPD ni
los regímenes especiales; no se desbloquea interés legítimo.

Se documentaron las brechas, un screening EIPD propuesto con declaraciones
fundadas y resultados derivados, y la secuencia de integración con condiciones
especiales. La ubicación física del screening sigue pendiente de diseño.
La confirmación ordinaria de consentimiento conserva cobertura parcial y no
se presenta como verificación completa de EIPD/regímenes especiales.

Referencia normativa: texto oficial BCN de Ley 21.719, art. 15 ter del régimen
previsto para diciembre de 2026, enlazado en el diseño. No se afirma existencia
ni cobertura de orientaciones regulatorias futuras.

Paso únicamente documental, diff sin errores de whitespace; no se repitieron
pruebas de código. Última suite completa: **506 passed**. Sin commit.

Siguiente paso: fijar el contrato físico/persistencia del screening EIPD antes
de implementar sus modelos y evaluador.

## 2026-10-05 — M3-T1: evaluador puro LIA v1

M3-T1 permanece **EN PROGRESO**. evaluate_lia_assessment_v1 implementa
aplicabilidad, faltantes y motivos de revisión de LIA sobre el snapshot RAT,
con salida inmutable, orden determinista y sin persistir ni alterar entradas.
Revalida contratos, incluyendo instancias modificadas, antes de evaluar.

Validación: **129 casos nuevos** y **506 passed** en la suite completa backend;
formato, lint y whitespace pasan. No se modificaron API, lifecycle, migraciones
ni hash v1. La confirmación de interés legítimo permanece bloqueada. Sin commit.

Siguiente paso: revisar EIPD y condiciones especiales y definir la integración
transaccional de LIA manteniendo los controles aún no implementados.

## 2026-10-05 — M3-T1: reglas operativas de completitud LIA v1

M3-T1 permanece **EN PROGRESO**. Se definieron en §§18.15–18.18 del diseño
los campos mínimos, condiciones derivadas del snapshot RAT, disparadores de
documentación de mitigación, motivos de revisión y precedencia de resultados.
Las reglas no infieren suficiencia jurídica desde textos ni producen scoring.

La aplicabilidad de información directa/de terceros utiliza source_type; los
hechos de categorías y titulares provienen del snapshot. Una decisión favorable
no sustituye faltantes ni elimina motivos de revisión. Solo completo podrá
superar el control LIA cuando se implemente su integración.

Este paso modifica únicamente documentación; no se ejecutaron pruebas de código.
La última suite backend permanece en **377 passed**. La confirmación de interés
legítimo sigue bloqueada y el trabajo está sin commit.

Siguiente paso: implementar el evaluador puro LIA y sus casos de aceptación;
revisar controles EIPD/condiciones especiales antes de habilitar confirmación.

## 2026-10-05 — M3-T1: contrato documental LIA v1

M3-T1 permanece **EN PROGRESO**. Se implementaron las ocho secciones de
LiaAssessmentV1 con respuestas estructuradas, claves estables, textos
preservados y rechazo de campos/versiones/valores desconocidos. Las categorías
y los indicadores de datos/titulares se reutilizan desde el snapshot RAT.

La API admite LIA en creación/edición/lectura de borradores: omisión conserva,
objeto reemplaza íntegramente y null elimina. Interés legítimo sigue bloqueado
al confirmar; una decisión propuesta favorable no habilita la transición.

Suite completa backend: **377 passed**; formato, lint y whitespace pasan.
Pruebas HTTP usan PostgreSQL, RLS y contexto RAT real. Sin migraciones ni
cambios al hash v1. El trabajo permanece sin commit.

Siguiente paso: definir aplicabilidad, completitud y motivos derivados de LIA
antes de implementar el evaluador y conectarlo a la confirmación.

## 2026-10-05 — M3-T1: creación concurrente de series y versiones

M3-T1 permanece **EN PROGRESO**. Cinco pruebas con dos sesiones PostgreSQL,
RLS como app_user y contexto RAT real validan creación sobre serie nueva o
existente, commit/rollback de la primera solicitud y asignación de versiones.

Se reprodujo y corrigió una regresión del identity map: una sesión con la
serie previamente cargada podía reservar una versión ya usada por la sesión
concurrente. La lectura bajo FOR UPDATE ahora refresca la serie con
populate_existing=True antes de usar next_version.

Se comprueban una única serie, un único borrador, conflicto sin consumo de
versiones, reserva revertida sin salto y contador actualizado después del
bloqueo. Suite completa backend: **355 passed**; formato, lint y whitespace
pasan. No se modificaron migraciones ni hash v1. Sin commit.

Siguiente bloque: contratos y validaciones LIA/condiciones especiales,
manteniendo bloqueada su confirmación hasta completar esos controles.

## 2026-10-05 — M3-T1: API inicial y concurrencia de confirmación

M3-T1 permanece **EN PROGRESO**. La API `/licitud` expone creación, lectura,
edición de borradores y confirmación de consentimiento ordinario. Exige
suscripción activa/grace, tenant validado y permisos existentes de lectura o
edición; la confirmación utiliza `edit_content`. Las versiones históricas
pueden leerse y no pueden editarse.

Se verificaron con dos sesiones PostgreSQL la confirmación simultánea,
la confirmación tras rollback de la primera sesión y la revalidación de un
checklist modificado durante la espera del bloqueo. Se usa `app_user` con RLS;
la espera se comprueba mediante `pg_blocking_pids`.

Las pruebas HTTP usan contexto RAT real y cubren guardado, confirmación,
reemplazo, contexto desactualizado, permisos viewer/editor, suscripción y
acceso entre organizaciones. Suite completa: **350 passed**; formato, lint
y whitespace pasan. No se modificaron migraciones ni hash v1. Sin commit.

Pendiente: contratos LIA/condiciones especiales, validaciones de las demás
bases, concurrencia en creación de series/versiones e interfaz M3. Las bases
y regímenes especiales todavía no soportados siguen bloqueados al confirmar.

## 2026-10-05 — M3-T1: consentimiento v1 y confirmación inicial

M3-T1 permanece **EN PROGRESO**. Se incorporaron los contratos del checklist
de consentimiento v1, el evaluador puro de aplicabilidad/completitud y el
guardado del expediente en borradores. La confirmación inicial del service
layer bloquea la serie, relee el borrador, revalida consentimiento y contexto
RAT y reemplaza la versión anterior sin commits internos.

Alcance actual: consentimiento ordinario. Las demás bases y los regímenes
especiales permanecen bloqueados hasta implementar sus validaciones.
Todavía no hay endpoint M3 de confirmación; el caller debe validar permisos
y cerrar o revertir la transacción. No se modificaron migraciones ni hash v1.

Validación: **341 pruebas backend aprobadas**, formato y lint de los archivos
Python modificados, y revisión de whitespace sin errores. Incluye reemplazo
y rollback en PostgreSQL con app_user y rechazo cross-tenant con RLS.
El constructor RAT se simula en la prueba transaccional de reemplazo;
concurrencia entre sesiones y flujo API completo siguen pendientes.

El trabajo está sin commit. Continuar por concurrencia del lifecycle y por
las validaciones/contratos faltantes antes de exponer la confirmación por API.

## 2026-10-01 — M3-T1 Bases de Licitud: contexto RAT v1 canónico + snapshot documental

M3-T1 permanece **EN PROGRESO**. No debe considerarse cerrado.

Sobre la persistencia base previamente comprometida en `fde0b4f`, quedó
implementado y validado el siguiente bloque de aplicación:

- schemas Pydantic v1 para el contexto RAT canónico y el snapshot documental;
- canonización textual v1 y construcción determinista de `purpose_key`;
- serialización determinista y cálculo SHA-256 de `rat_context_hash`;
- composición tenant-aware del contexto M2→M3 para finalidad, categorías,
  titulares, fuentes, sistemas, terceros y transferencias internacionales;
- selección explícita de categorías y titulares para la finalidad evaluada;
- derivación estructurada de regímenes especiales, sin inferencias desde texto
  libre, nombres u otros campos fuera del alcance definido;
- objeto canónico de 11 bloques, manteniendo `systems = []` en hash v1;
- snapshot documental v1 con valores factuales de M2 y sin UUIDs operacionales,
  timestamps ni campos de auditoría;
- conservación documental de sistemas y de metadatos de trazabilidad de
  terceros y transferencias que no participan en el hash;
- resolución documental de `recipient_name` desde `Vendor.name` cuando la
  transferencia no contiene nombre directo y sí referencia a un Vendor del
  mismo tenant;
- ordenación documental determinista sin canonizar los valores factuales y sin
  deduplicar filas;
- composición conjunta mediante `RatContextBundleV1`, de modo que objeto
  canónico y snapshot se construyen desde los mismos objetos M2 cargados en una
  misma composición lógica. Esto no implica aislamiento de snapshot de base de
  datos bajo PostgreSQL `READ COMMITTED`.

El contrato y las decisiones anteriores quedaron documentados en
`modulo3-licitud-diseno.md`, incluida la definición del objeto canónico,
serialización/hash y snapshot documental v1.

Validación del checkpoint:

- `test_schemas_licitud.py` + `test_services_licitud.py`: **70 passed**;
- suite completa backend: **247 passed**;
- Black: **PASS**;
- Ruff: **PASS**;
- `git diff --check`: sin errores de whitespace.

La persistencia estructural, migración, modelos ORM, integridad tenant-aware y
RLS continúan respaldados por el checkpoint `fde0b4f`. El `alembic check`
global mantiene drift histórico preexistente ajeno a M3; no debe declararse
como limpio.

Pendiente para continuar M3-T1:

1. integrar contexto canónico, hash y snapshot documental con el guardado
   transaccional de evaluaciones;
2. implementar asignación segura de `next_version` bajo concurrencia y resolver
   la creación/obtención concurrente de series sin hacer `commit` o `rollback`
   dentro del service layer;
3. implementar ciclo de borrador, confirmación, reemplazo y revalidación del
   contexto RAT cuando corresponda;
4. completar validaciones programáticas específicas por base jurídica;
5. definir e implementar los contratos de consentimiento, LIA y condiciones
   especiales;
6. ampliar pruebas de persistencia, concurrencia, lifecycle y reglas jurídicas
   antes de cerrar M3-T1.

**Punto de reanudación:** contexto RAT v1 canónico y snapshot documental
implementados y validados; continuar por integración transaccional con la
persistencia ya existente, sin modificar el contrato de hash v1 salvo decisión
de diseño explícita.

No actualizar todavía `modules-roadmap.md` ni declarar M3-T1 como DONE.

## 2026-09-23 — M3-T1 Bases de Licitud: checkpoint de diseño canónico RAT v1

M3-T1 permanece **EN PROGRESO**. No debe considerarse cerrado.

La persistencia base del módulo quedó previamente implementada y comprometida
en `fde0b4f` (`feat(m3): add legal basis assessment persistence and RLS`),
incluyendo migración, modelos ORM, integridad tenant-aware, RLS y tests.

En la jornada actual se avanzó en el contrato de aplicación y quedó definido
en `modulo3-licitud-diseno.md` el contexto RAT canónico v1 utilizado por M3:

- `purpose_key` derivado mediante canonización textual v1 y SHA-256;
- canonización textual NFC, trim, colapso de whitespace Unicode y `casefold()`;
- tratamiento determinista de textos opcionales vacíos como `null`;
- separación explícita entre `rat_context_snapshot` documental y el objeto
  canónico utilizado para `rat_context_hash`;
- estructura canónica de 11 bloques: finalidad, rol de la organización,
  categorías de datos, titulares, fuentes, conservación, decisiones
  automatizadas, sistemas, terceros, transferencias internacionales y
  regímenes especiales;
- `systems` vacío en el objeto canónico v1, sin inferencias desde nombres,
  proveedores o texto libre;
- `special_regimes` derivado exclusivamente de indicadores estructurados del
  alcance seleccionado;
- serialización JSON determinista con claves ordenadas, separadores compactos,
  Unicode sin escape ASCII, UTF-8 y SHA-256 sobre los bytes exactos;
- claves de ordenación deterministas por bloque y tratamiento explícito de
  textos opcionales nulos;
- preservación de multiplicidad: la canonización no deduplica elementos.

`git diff --check -- ../docs/project/modulo3-licitud-diseno.md` finalizó sin
salida.

El trabajo de aplicación todavía no comprometido incluye schemas del contexto
RAT v1, canonización y hash, carga batch tenant-aware de Vendor y proyección
de terceros, resolución de finalidad por `purpose_key`, y selección canónica
de categorías y titulares con rechazo de duplicidad, inexistencia y ambigüedad.
La línea base de schemas y servicios se reprodujo: **39 passed in 0.17s**.

Continuación de integración M2→M3:

- proyección de `TreatmentDataSource` y `InternationalTransfer` al contrato
  canónico existente, preservando multiplicidad y excluyendo UUID/auditoría
  y metadatos administrativos;
- rechazo HTTP 400 de transferencias con país de destino vacío;
- `build_rat_context_from_m2_v1` compone los 11 bloques mediante las lecturas
  tenant-aware de M2 y los resolutores ya validados;
- categorías y titulares se limitan al alcance elegido; fuentes, terceros y
  transferencias provienen de la actividad completa porque M2 no dispone de
  selección por finalidad para esos bloques;
- no hay escritura de M2, persistencia del snapshot ni confirmación en este
  constructor; los errores de lectura se propagan;
- pruebas de equivalencia semántica, cambios por cada campo, multiplicidad,
  ausencia de bloques opcionales y filtros por tenant/tratamiento en las
  consultas reales del servicio M2 con sesión simulada. Estas últimas no
  sustituyen las pruebas RLS contra PostgreSQL.

Validación de esta continuación: **79 passed in 0.58s** en schemas y
servicios M2/M3 (`test_schemas_licitud.py`, `test_services_licitud.py`,
`test_schemas_rat.py`, `test_services_rat.py`), incluidos los 39 tests M3
previos y 25 casos nuevos. Ruff y Black pasan en los dos archivos Python
modificados. No se ejecutó la suite completa ni las pruebas RLS en esta
continuación; no se modificaron migraciones ni contratos Pydantic.

Pendiente para continuar M3-T1:

1. definir e implementar la composición exacta del snapshot documental;
2. integrar contexto/hash y snapshot en el guardado de borradores y la
   confirmación transaccional con revalidación del RAT;
3. continuar con validaciones por base jurídica, consentimiento, LIA,
   condiciones especiales y service layer;
4. ejecutar suite completa y pruebas RLS antes de cualquier cierre.

**Punto de reanudación:** constructor de contexto M2→M3 implementado;
continuar por snapshot documental y persistencia sin modificar el hash v1.

No actualizar todavía `modules-roadmap.md` ni declarar M3-T1 como DONE.

## M2-T3.8 — infraestructura E2E autenticada del RAT

Playwright/Chromium incorporado al frontend con login real de Supabase, fixture
E2E existente y limpieza de las actividades creadas por cada prueba. Se verifica
acceso sin sesión, preparación completa, rechazo server-side de activación
incompleta, activación, invalidación por requisito pendiente, retorno a
preparación, archivo, reactivación y persistencia en detalle/listado.

Validación en `feature/m2-t3-8-rat-finalization`:

- ejecución inicial corregida: **2 passed**;
- dos repeticiones consecutivas: **4 passed**, incluida limpieza API (204/404);
- type-check, lint, Prettier y `git diff --check`: **PASS**;
- backend `/health`: base de datos disponible.

Sesión solo en memoria, sin archivos de autenticación; capturas, trazas y vídeo
desactivados. Los escenarios afirmativos de relaciones y otros roles no forman
parte de esta suite mínima. No se modifican backend, migraciones ni comportamiento
de la aplicación. El seed existente se conserva sin cambios.

Preparación y límites: [E2E del frontend](frontend-e2e.md).

## 2026-09-16 — M2-T3.2: creación/edición de información general RAT

Se completó M2-T3.2 del Módulo 2 — creación y edición de la información general
de una actividad de tratamiento.

Implementado:

- formulario reutilizable de información general;
- creación de actividades mediante `POST /rat/treatments`;
- carga de detalle mediante `GET /rat/treatments/{treatment_id}`;
- edición mediante `PATCH /rat/treatments/{treatment_id}`;
- campos de nombre, descripción, área de negocio, rol de la organización,
  descripción del flujo de datos, fechas, regla de conservación, método de
  eliminación y decisiones automatizadas;
- navegación desde `/dashboard/rat/nuevo` hacia la ficha creada;
- reutilización de `/dashboard/rat/[treatmentId]` para edición;
- manejo de errores de API y estados HTTP 402/403;
- barra general de preparación basada en los 10 requisitos reales de activación;
- estado visual `borrador` presentado al usuario como `Registro en preparación`,
  sin modificar el estado interno del backend;
- leyenda explícita indicando que el avance mide preparación del registro para
  activación y no porcentaje de cumplimiento legal.

Validación funcional:

- creación de actividad: PASS;
- carga del detalle creado: PASS;
- edición y guardado de cambios: PASS;
- reflejo de cambios en el listado RAT: PASS;
- estado `Registro en preparación`: PASS;
- barra de avance calculada correctamente: 3 de 10 requisitos en la actividad
  de prueba;
- `npm run type-check`: PASS;
- `npm run build`: PASS.

La actividad permanece en estado interno `borrador` mientras no cumpla los
requisitos mínimos de activación. Las declaraciones de sistemas, proveedores y
transferencias internacionales deben estar resueltas en `si` o `no`; el valor
`pendiente` no satisface la validación de activación.

**Siguiente paso: M2-T3.3 — finalidades, categorías de datos, titulares y fuentes.**

## 2026-09-16 — M2-T3.1: listado RAT y navegación frontend

Se completó M2-T3.1 del Módulo 2 — frontend del Inventario / RAT.

Implementado:

- nueva ruta `/dashboard/rat`;
- listado de actividades de tratamiento consumiendo `GET /rat/treatments`;
- selector de organización reutilizando el patrón del autodiagnóstico;
- estados loading, empty y error;
- UX específica para HTTP 402 (suscripción) y 403 (sin acceso);
- CTA `Nueva actividad`;
- navegación hacia `/dashboard/rat/nuevo`;
- navegación hacia `/dashboard/rat/[treatmentId]`;
- tarjeta Inventario (RAT) habilitada en el dashboard;
- cliente API extendido con tipos RAT y `ApiError` con status HTTP.

Validación frontend:

- `npm run type-check`: PASS;
- `npm run build`: PASS;
- rutas `/dashboard/rat`, `/dashboard/rat/nuevo` y
  `/dashboard/rat/[treatmentId]` incluidas en el build;
- warning no bloqueante: Node.js 20 está deprecado por la versión actual de
  `@supabase/supabase-js`; actualizar a Node 22+ queda como mantenimiento técnico.

M2-T3.1 y M2-T3.2 dejan operativo el flujo de listado, creación, consulta y
edición de la información general de las actividades de tratamiento.

**Siguiente paso: M2-T3.3 — finalidades, categorías de datos, titulares y fuentes.**

## 2026-09-16 — M2-T3.0: declaraciones y activación del RAT

Se implementó el ajuste mínimo de backend previo a la interfaz M2-T3.1.
`Treatment` guarda ahora tres declaraciones explícitas: uso de sistemas,
participación de terceros/proveedores y transferencias internacionales. Cada una
acepta `si`, `no` o `pendiente`; `null` significa que todavía no fue declarada.
La migración append-only `0011_treatment_declarations_activation.py` agrega las
columnas y restricciones de dominio sin inferir valores desde relaciones o desde
los campos legacy.

La transición a `activo`, tanto desde `borrador` como desde `archivado`, exige
nombre y rol de la organización, al menos una finalidad, categoría de datos,
categoría de titulares y fuente de datos, regla de conservación y las tres
declaraciones. Una declaración `pendiente` registra que la organización revisó el punto pero aún
no lo ha resuelto, y por lo tanto no satisface la activación. Solo `si` o `no`
cumplen ese requisito. Las otras transiciones permitidas son
`activo → borrador`, `activo → archivado` y `borrador → archivado`. El service
rechaza las demás con HTTP 400; los valores fuera de dominio se rechazan en el
contrato HTTP y mediante restricciones de base de datos.

Validación local: tests específicos RAT, 166 tests backend, Ruff y Black PASS;
Alembic upgrade, downgrade y re-upgrade PASS. Módulo 1 freemium y benchmark no
se modificaron. M2-T3.1 y M2-T3.2 quedaron completados; siguiente paso: M2-T3.3, finalidades, categorías de datos, titulares y fuentes.

## 2026-09-15 — M2-T2 cerrado: servicio/API del RAT

Se completó M2-T2 del Módulo 2 — Inventario / RAT.

El backend del RAT dispone ahora de contratos Pydantic normalizados, service
layer, API REST, permisos y gate server-side de suscripción para módulos M2+.

Implementado:

- `require_active_subscription`: `active` y `grace` permiten acceso;
  `suspended` y `cancelled` bloquean con HTTP 402;
- validación previa de acceso al tenant para evitar consultar suscripciones de
  organizaciones ajenas;
- schemas RAT separados en `app/schemas/rat.py`;
- service layer tenant-aware en `app/services/rat.py`;
- router `/rat` con 22 operaciones HTTP;
- lectura con `view_content` y escritura con `edit_content`;
- CRUD de Treatment, System y Vendor;
- finalidades, categorías de datos, titulares y fuentes normalizadas;
- relaciones Treatment-System y Treatment-Vendor;
- transferencias internacionales;
- detalle agregado del tratamiento;
- tests HTTP ejecutados contra `app_user` con RLS activo.

Validación:

- gate de suscripción: **6 passed**;
- schemas RAT: **9 passed**;
- services RAT: **5 passed**;
- API RAT end-to-end: **6 passed**;
- M2-T2 específico: **26 passed**;
- suite backend completa: **162 passed**;
- Ruff: **PASS**;
- Black: **PASS**.

**M2-T0: DONE. M2-T1: DONE. M2-T2: DONE.**

M2 dispone de backend funcional, pero aún no de interfaz para el usuario.
**Siguiente paso: M2-T3 — frontend del RAT e integración funcional end-to-end.**

## 2026-09-15 — M2-T1 cerrado: persistencia normalizada del RAT

Se completó M2-T1 del Módulo 2 — Inventario / RAT.

Resultado: **PASS / DONE**.

Implementación:

- migración `0010_modulo2_rat_persistencia.py`;
- ampliación de `Treatment`, `System` y `Vendor` manteniendo compatibilidad
  transitoria con el scaffolding;
- nuevas entidades `treatment_purposes`, `treatment_data_categories`,
  `treatment_data_subjects`, `treatment_data_sources`, `treatment_systems`,
  `treatment_vendors` e `international_transfers`;
- FK compuestas con `organization_id` para impedir relaciones cross-tenant;
- RLS en todas las tablas nuevas con el patrón `auth_org_ids()`;
- coherencia tenant-aware agregada al vínculo `LegalBase → Treatment`;
- tests específicos en `tests/test_rls_isolation_rat.py`.

Validación:

- Alembic upgrade: PASS;
- downgrade a `d2e3f4a5b6c7`: PASS;
- re-upgrade a `e3f4a5b6c7d8`: PASS;
- tests específicos RAT: **7 passed**;
- suite backend completa: **136 passed**;
- Ruff, Black y `git diff --check`: PASS.

M2 sigue sin ser funcional de extremo a extremo: M2-T1 cubre persistencia.
M2-T2 quedó cerrado con service layer, API RAT, contratos Pydantic,
permisos y gate server-side de suscripción para M2+.
El siguiente paso es **M2-T3 — frontend del RAT e integración funcional end-to-end**.

# Estado actual del proyecto

## Checkpoint — cierre conceptual M2-T0 (2026-09-15)

**M2-T0 — Descubrimiento y diseño conceptual del Inventario / RAT: DONE.**

El [diseño del RAT](modulo2-rat-diseno.md) registra el cierre aprobado, alcance,
matriz canónica resumida, decisiones, frontera M2/M3/M5 y modelo conceptual.
`Treatment` representa una actividad; el objetivo incorpora catálogos, relaciones
N:M con sistemas/terceros, encargos y transferencias internacionales explícitas.
M3 determina, justifica y aprueba la base de legitimidad; M5 concentra el expediente
probatorio. El documento identifica el alcance del extracto de conversación disponible.

Se verificaron `CLAUDE.md` y `docs/backlog.md`: ambos reconocen el MVP del Módulo 1
completado. Los riesgos documentales 1 y 2 quedan resueltos en
[riesgos y asuntos abiertos](risks-open-items.md); los demás se conservan.

**Siguiente paso vigente: M2-T3 — frontend del RAT e integración funcional end-to-end.**
migraciones**, conforme al [roadmap](modules-roadmap.md). Sustituye la selección
genérica de próxima tarea del checkpoint anterior. Módulo 2 sigue sin implementar
funcionalmente; este cierre no modifica código, API, UI ni migraciones.

Base documental de trabajo: `origin/main` actualizado mediante fetch, commit
`146428e`; rama `feature/m2-t0-cierre-conceptual`. Los checkpoints siguientes
conservan su contexto histórico.

## Checkpoint operativo — cierre de jornada 2026-09-14

### Estado Git

- Rama vigente: `main`.
- `main` sincronizado con `origin/main`.
- Working tree limpio al cierre de la jornada.
- Checkpoint Git previo a este registro: `b665035` — `benchmark: conserva configuraciones Ornith F1.29A`.
- Commit previo de documentación operativa: `a52c853` — `docs: agrega runbook operativo de Qwen3.6 local`.

### Benchmark y modelo local

La exploración de modelos locales queda cerrada por ahora:

- F1.29A — Ornith-1.5-9B Q5_K_M: **NO PROMOTE**.
- F1.29B — Qwen3.5-9B Q5_K_M: **Gate 1 PASS / Gate 2 FAIL / STOP**.
- Qwen3.6-35B-A3B IQ4_XS queda ratificado como **modelo local principal de CumpleIA**.

No reabrir selección de modelos salvo que aparezca un candidato claramente superior, cambie el hardware/runtime o exista una limitación funcional concreta de Qwen3.6.

### Qwen3.6 — operación local

Se automatizó la operación diaria mediante:

`cumpleia-qwen`

Comandos principales:

- `cumpleia-qwen status` — revisar estado del servidor, bridge y GPU.
- `cumpleia-qwen start` — iniciar Qwen3.6 y el bridge local.
- `cumpleia-qwen stop` — detener el entorno y liberar recursos.
- `cumpleia-qwen restart` — reinicio completo.
- `cumpleia-qwen log` — seguir el log de `llama-server`.

Configuración operativa:

- modelo: Qwen3.6-35B-A3B IQ4_XS;
- contexto: 65536;
- `-ngl 99`;
- `-ncmoe 32`;
- llama-server: `127.0.0.1:8080`;
- endpoint operativo: `http://llm-local.cumpleia:18080`;
- bridge: `socat`;
- template Claude Code compatible: `qwen36-claude-code.jinja`.

El arranque observado del modelo en el OMEN fue aproximadamente 3 min 49 s.

La guía completa está en:

[`qwen36-operacion-local.md`](qwen36-operacion-local.md)

### Validación end-to-end

Se validó exitosamente el flujo real:

`Claude Code → llm-local.cumpleia:18080 → socat → llama-server → Qwen3.6 → Read tool → resultado`

La prueba utilizó un archivo con UUID aleatorio no incluido en el prompt y produjo:

- tool-use real;
- dos turnos;
- lectura correcta;
- respuesta final exacta.

Por tanto, el entorno local está operativo para desarrollo cotidiano con Claude Code.

### Próxima sesión

El benchmark deja de ser el foco principal. La próxima sesión debe volver al **desarrollo funcional de CumpleIA**.

Antes de comenzar:

1. Entrar a `~/projects/CumpleIA`.
2. Ejecutar `git status -sb`.
3. Ejecutar `cumpleia-qwen status`.
4. Si Qwen está detenido, ejecutar `cumpleia-qwen start`.
5. Confirmar:
   - `llama-server : OK`;
   - `SRT bridge : OK`.
6. Revisar conjuntamente:
   - `docs/project/status.md`;
   - `docs/project/modules-roadmap.md`;
   - `docs/project/risks-open-items.md`.
7. Seleccionar la siguiente fase/tarea funcional concreta de CumpleIA.
8. Usar Qwen3.6 para desarrollo cotidiano y Claude/DeepSeek cloud como segunda revisión en tareas críticas.

**Próximo foco vigente:** retomar el roadmap funcional del producto, no continuar exploración de modelos.

---


## Benchmark — cierre F1.29A y F1.29B (2026-09-14)

[F1.29A](../benchmark/F1.29A_Cierre_Ornith_1.5_9B_2026-09-14.md) cierra
Ornith-1.5-9B Q5_K_M como **NO PROMOTE**: r1 INVALID por contexto/Docker,
r2 FAIL funcional con overflow 64K (562.85 s) y siete errores TypeScript,
r3 TIMEOUT 128K (1810.79 s), incompleta y con errores persistentes.
[F1.29B](../benchmark/F1.29B_Cierre_Qwen3.5_9B_Q5_K_M_2026-09-14.md) cierra
Qwen3.5-9B Q5_K_M con **Gate 1 PASS / Gate 2 FAIL / STOP**, sin mini-agentic,
performance ni RAT: corregir HTTP 500 del template no logró un Read real.

Se ratifica **Qwen3.6-35B-A3B IQ4_XS**, seleccionado en
[F1.28](../benchmark/F1.28_Cierre_seleccion_modelos_locales_2026-09-11.md),
como principal local, preservando F1.25-B FAIL y la evidencia histórica.
El [estado del benchmark](../benchmark/status.md) consolida la decisión vigente.
Este cierre es documental; no modifica capacidad del producto.

## Benchmark — cierre F1.27 (2026-09-11)

El [cierre F1.27](../benchmark/F1.27_Cierre_DeepSeek_Coder_V2_Lite_2026-09-11.md)
registra DeepSeek-Coder-V2-Lite-Instruct Q4_K_M con `-ngl 20` canónico tras
calibrar el cliff de VRAM. **Performance PASS**: pp16384 936.06 ± 70.01 y
tg256 56.87 ± 10.13 tok/s; transporte directo, SRT y Claude Code básico PASS.
**Agentic tool compatibility FAIL con el stack actual**: mini-agentic sin
ediciones, 2 FAIL + 1 ERROR; intento textual de tool call sin ejecución real
y contenido inventado. Aunque hay tokens de herramientas, llama.cpp
`5202104b5 (322)` reporta `tool_mode: NONE` y `supports_tools: false`.

**RAT completa: no procede; no ejecutar. DeepSeek no seleccionado. Se mantiene
Qwen3.6-35B-A3B IQ4_XS como candidato local principal**, con las reservas de F1.25.
F1.27 queda cerrada sin ejecuciones pendientes. La reevaluación futura requiere
build/template/parser compatible con tool-calling de DeepSeek y evidencia nueva.
El [estado del benchmark](../benchmark/status.md) concentra el estado vigente;
este cierre es exclusivamente documental.

## Benchmark — cierre F1.26 (2026-09-11)

El [cierre F1.26](../benchmark/F1.26_Cierre_Qwen3_Coder_recalibrado_RAT_2026-09-11.md)
registra Qwen3-Coder-30B-A3B-Instruct Q4_K_M con `-ncmoe 32`, pruebas
sintéticas y transporte funcional, y mini-agentic PASS fuerte (~5m43s).
La RAT conserva TIMEOUT (1814.351633 s; límite 1800 s) y FAIL funcional real:
dos errores de type-check, fallback ausente incorrecto, selector reutilizable
y tests frontend incompletos, además del falso negativo nominal del verifier.

**Operational viability FAIL; no seleccionado. Qwen3.6-35B-A3B IQ4_XS sigue
como candidato local principal**, con las reservas documentadas en F1.25.
F1.26 está cerrada sin nuevas ejecuciones pendientes; el estado vigente se
consolida en [benchmark/status.md](../benchmark/status.md). Este cierre sólo
actualiza documentación y conserva los resultados históricos.

## Benchmark — cierre F1.25 (2026-09-10)

El estado vigente del benchmark está en [benchmark/status.md](../benchmark/status.md).
El [cierre F1.25](../benchmark/F1.25_Cierre_LLM_local_Claude_Code_RAT_2026-09-10.md)
confirma viabilidad de Qwen3.6-35B-A3B IQ4_XS en el OMEN con Claude Code,
con revisión de integración. Conserva A como calibración (16K insuficiente y
Docker apagado) y B como FAIL formal pese a exit 0 y checks generales PASS.
Incluye los defectos reales, la validación posterior y la trazabilidad trusted.
F1.24H conserva su hallazgo válido: 5.23 tok/s se obtuvo con MoE subóptimo
y no representa el límite del hardware/modelo.

No quedan ejecuciones pendientes para cerrar F1.25. Una futura calibración del
verifier debe tener evidencia separada. Este avance documental no modifica
capacidad del producto; los apartados anteriores del benchmark conservados
más abajo describen su secuencia histórica, no el próximo paso vigente.

## Snapshot Git observado

| Elemento | Valor observado |
|---|---|
| Repositorio de trabajo | `P_CumpleIA` |
| Rama checkout | `fix/modulo1-tarea6-backlog-y-tests-onupdate` |
| HEAD | `fcf5315` |
| `main` local | `4cedff1` |
| `origin/main` en el snapshot | `4cedff1` |
| Archivos trackeados | 142 |
| Migraciones Alembic | 9 |
| Archivos de tests backend | 16 |
| Python trackeado | 64 archivos |
| TSX trackeado | 20 archivos |
| TS trackeado | 7 archivos |

La rama actual contiene tres archivos modificados respecto de `main`: dos archivos de tests y `docs/backlog.md`.

## Inconsistencia a verificar en GitHub

El documento fechado **10-08-2026** afirma que el PR #20 quedó mergeado a `main`. Sin embargo, los refs Git incluidos en el ZIP muestran:

- `main` / `origin/main`: `4cedff1` - PR #19.
- rama `fix/modulo1-tarea6-backlog-y-tests-onupdate`: `fcf5315`.

Esto puede significar que el PR #20 fue mergeado después del último `fetch`, o que el documento anticipó el merge. No debe resolverse por memoria: al retomar, hacer `git fetch` y verificar el estado real remoto.

## Estado funcional por fases

### Fase 0 - Cimientos

**Completada según código y notas históricas.** Incluye:

- monorepo frontend/backend;
- autenticación con Supabase;
- aprovisionamiento JIT de perfiles;
- organizaciones y membresías;
- aislamiento multi-tenant con PostgreSQL RLS;
- rol runtime `app_user` sin `BYPASSRLS`;
- CI backend/frontend;
- RAG con pgvector;
- ingesta de fuentes legales;
- abstracción de proveedor LLM y embeddings.

### Fase 1 - Módulo 1 Autodiagnóstico

**Construido en el código del snapshot.** Incluye:

- catálogo versionado del cuestionario;
- 10 secciones y 50 preguntas según el seed vigente;
- panel superadmin para pesos y riesgo por pregunta;
- scoring determinista;
- hallazgos por riesgo;
- API de diagnóstico;
- narrativa de informe con IA y guardarraíles;
- RAG limitado a Ley 21.719 + guía CCS para el informe;
- exportación HTML;
- wizard frontend;
- dashboard de puntajes y hallazgos;
- generación/regeneración del informe;
- descarga del informe HTML;
- edición de datos de organización.

## Verificación de tests

No se ejecutó la suite completa durante esta revisión porque el entorno de análisis no tenía instalada la dependencia `pgvector`; `compileall` sí pasó para `app`, `scripts` y `tests`.

La nota del 10-08-2026 reporta **129/129 tests** como criterio esperado. El árbol fuente contiene 123 funciones de test directas; la diferencia puede corresponder a parametrizaciones. Antes de desarrollar, debe ejecutarse la suite real en el entorno del proyecto.

## Estado de la base de conocimiento RAG

La nota del 30-07-2026 reporta 198 chunks con embedding:

- `guia_ccs`: 76
- `ley_19628`: 31
- `ley_21719`: 91

Ese dato es **histórico**, no una consulta al Postgres actual. Debe verificarse en la base al retomar si es importante para la siguiente tarea.

## Checkpoint de entorno local - 31-08-2026

Se reconstruyó y validó el entorno local de desarrollo de CumpleIA en el nuevo equipo HP OMEN, utilizando WSL2 con Ubuntu 24.04 y Docker Desktop con integración WSL.

Estado verificado:

- repositorio en rama `main`, sincronizado con `origin/main` y working tree limpio antes de registrar este checkpoint;
- PostgreSQL 16 + pgvector operativo mediante Docker;
- migraciones Alembic aplicadas correctamente hasta `d2e3f4a5b6c7`;
- rol runtime `app_user` operativo, sin privilegios `SUPERUSER` ni `BYPASSRLS`;
- autenticación de `app_user` contra PostgreSQL validada desde el entorno Python local;
- políticas RLS verificadas en las tablas multi-tenant;
- seed del Módulo 1 ejecutado correctamente:
  - 8 obligaciones;
  - 10 secciones;
  - 50 preguntas;
  - configuración versión 1 activa;
- backend levantado correctamente y endpoint `/health` con estado `ok`;
- suite completa de backend ejecutada en el entorno local:
  - **129 tests collected**;
  - **129 passed**;
  - **0 failed**;
  - tiempo observado: **10.75 s**.

Este checkpoint reemplaza, para efectos del entorno local actual, la observación anterior de este documento que indicaba que la suite completa no había podido ejecutarse.

**Estado:** baseline local estable y validado para continuar el desarrollo y las pruebas.

**F1.16 — Sandbox Runtime:** completada y validada con resultado **PASS**.

La política SRT pre-final quedó documentada en:

`docs/benchmark/F1.16_SRT_validacion_2026-08-31.md`

La validación confirmó, entre otros controles, aislamiento de red, bloqueo de localhost y sockets Unix, protección de rutas sensibles y de `.git/config`, ejecución de Claude Code dentro de SRT y aislamiento de su configuración runtime.

**Próximo paso:** continuar con la etapa siguiente del Benchmark RAT posterior a F1.16.

**F1.17 — Managed Settings de Claude Code:** completada y validada con resultado **PASS**.

La política administrada quedó documentada en:

`docs/benchmark/F1.17_Managed_Settings_validacion_2026-08-31.md`

La configuración versionada utilizada por el benchmark se encuentra en:

`docs/benchmark/runner/managed-settings.json`

SHA-256 de referencia:

`f51e229df07d539fc1367654110ba028c64261f577e7477dae115049b66f2a0f`

La validación confirmó carga efectiva como `Enterprise managed settings (file)`, modo `dontAsk`, bloqueo de WebFetch y WebSearch, neutralización de bypass de permisos y bloqueo de sideload de MCP, custom agents y plugins.

**Próximo paso:** continuar con **F1.18 — transporte y backend de modelo**, revisando el diseño original del benchmark para incorporar de forma controlada tanto modelos remotos como una eventual LLM local en el HP OMEN.

**F1.18A — Contrato común de transporte:** implementada documentalmente; la validación de backends permanece pendiente.

El contrato neutral para candidatos cloud y local quedó documentado en:

`docs/benchmark/F1.18A_Contrato_comun_transporte_2026-09-01.md`

Sus archivos de configuración de referencia son:

- `docs/benchmark/runner/transport-contract.schema.json`;
- `docs/benchmark/runner/candidate-transport.example.json`.

El contrato fija nombre lógico, clase de backend, proveedor, endpoint, model ID, referencia de credencial y timeout. Las credenciales no se versionan: solo se declara el nombre de su variable de entorno, o `null` cuando el backend no requiere autenticación.

Python **3.12.3** permanece como baseline común. F1.18A no instala Ollama/Qwen, no selecciona modelos definitivos y no modifica la política SRT, la allowlist de red ni los managed settings de F1.17.

**Próximo paso:** continuar con **F1.18B — validación de transporte cloud** y posteriormente F1.18C para el transporte local controlado.

**F1.18B — Transporte cloud Anthropic:** completada y validada con resultado **PASS**.

La validación quedó documentada en:

`docs/benchmark/F1.18B_Transporte_cloud_Anthropic_validacion_2026-09-01.md`

Se confirmó una inferencia real de Claude Code hacia Anthropic dentro de SRT, manteniendo accesibles únicamente los dominios Anthropic previamente autorizados. El acceso a Internet general permaneció bloqueado mediante allowlist.

No fue necesario modificar la política SRT ni Managed Settings y no se incorporaron componentes de transporte local.

**Próximo paso:** validar el siguiente backend cloud del Benchmark RAT, verificando previamente endpoint, model ID, autenticación y allowlist mínima. La arquitectura de transporte local se abordará posteriormente como una etapa separada.
**F1.18C — Transporte cloud DeepSeek:** completada y validada con resultado **PASS**.

La validación quedó documentada en:

`docs/benchmark/F1.18C_Transporte_cloud_DeepSeek_validacion_2026-09-01.md`

Se validó DeepSeek como segundo backend cloud mediante tres niveles independientes: API nativa, interfaz Anthropic-compatible mediante SDK y ejecución real de Claude Code dentro de SRT utilizando DeepSeek como backend.

La política SRT fue ampliada exclusivamente con `api.deepseek.com`. Internet general permaneció bloqueado y no se habilitaron Unix sockets ni local binding.
Durante la ejecución con Claude Code 2.1.252 se observaron advertencias `unrecognized_model` asociadas a los identificadores DeepSeek utilizados por llamadas internas de Claude Code. Estas advertencias quedaron documentadas como una limitación de compatibilidad a vigilar, pero no impidieron completar correctamente la inferencia solicitada.

Las credenciales permanecen fuera del repositorio y al finalizar las pruebas no quedaron variables de autenticación persistentes en el entorno.

**Próximo paso:** definir y validar la arquitectura de transporte para un backend LLM local antes de instalar Ollama u otro runtime o descargar un modelo. El diseño deberá permitir la comunicación controlada desde SRT sin habilitar localhost, local binding o Unix sockets de forma general.
### F1.18D-A — Arquitectura de transporte local seguro

- Estado: PASS arquitectónico.
- Se descartó el diseño basado en Unix Domain Socket selectivo bajo SRT/Linux.
- No se habilitó `allowAllUnixSockets`.
- Se validó transporte local mediante hostname dedicado y proxy/allowlist SRT.
- `llm-local.cumpleia` autorizado alcanza un servicio loopback local.
- Acceso directo a `127.0.0.1` desde SRT continúa bloqueado.
- Un hostname alternativo no autorizado hacia el mismo servicio devuelve HTTP 403.
- `allowUnixSockets` permanece vacío.
- `allowLocalBinding` permanece en false.
- No se instalaron todavía llama.cpp, Ollama ni modelos locales.
- Próximo paso: validar el transporte con un runtime LLM real y posteriormente F1.18D-B para Claude Code.
### F1.18D-A2 — Validación del transporte con runtime LLM real

- Estado: **PASS**.
- Se instaló CUDA Toolkit 13.1 dentro de WSL, sin instalar drivers NVIDIA Linux.
- Se compiló `llama.cpp` tag `b10516`, commit `b95502b`, con `GGML_CUDA=ON` y arquitectura CUDA `120`.
- Se validó `llama-server` utilizando la NVIDIA GeForce RTX 5060 Laptop GPU.
- Modelo de validación: `Qwen3.5-0.8B-Q4_0.gguf`.
- El modelo se almacena físicamente en `D:\CumpleIA-LLM\models` y se accede desde el runtime mediante `~/runtime/local-llm/models`.
- Se endureció el transporte asignando `llm-local.cumpleia` al loopback dedicado `127.77.18.1`.
- `llama-server` escucha exclusivamente en `127.77.18.1:18080`.
- Se confirmó inferencia real fuera de SRT con resultado `F1.18D-A2-LOCAL-OK`.
- Se confirmó inferencia real dentro de SRT con resultado `F1.18D-A2-SRT-OK`.
- El acceso directo desde SRT a `127.0.0.1:18080` permanece bloqueado (`HTTP=000`).
- `nvidia-smi` confirmó `/llama-server` como proceso CUDA y aproximadamente 829 MiB de VRAM asignada durante la validación.
- No se detectaron listeners locales wildcard en `0.0.0.0` ni `[::]`.
- Se comprobó que `allowedDomains` de SRT controla hostname pero no puerto; por ello la ausencia de listeners wildcard pasa a ser un invariante de seguridad del benchmark.
- La evidencia completa quedó registrada en `docs/benchmark/F1.18D-A2_Validacion_runtime_LLM_local_2026-09-02.md`.

### F1.18D-B — Integración Claude Code con LLM local — PASS

- Se confirmó que `llama-server` expone un endpoint Anthropic-compatible `/v1/messages`.
- La primera integración con Claude Code falló por incompatibilidad del chat template original de Qwen3.5 (`System message must be at the beginning`).
- Se resolvió utilizando `--chat-template chatml`, sin introducir proxy o adaptador adicional.
- La ventana inicial de 4096 tokens fue insuficiente para Claude Code; se amplió a `16384`.
- Claude Code ejecutado fuera de SRT devolvió correctamente `F1.18D-B-CLAUDE-LOCAL-OK`.
- Dentro de SRT fue necesario redirigir `TMPDIR` a `/home/cumplebench/runtime/tmp`, evitando habilitar escritura general en `/tmp`.
- Claude Code ejecutado dentro de SRT devolvió correctamente `F1.18D-B-SRT-LOCAL-OK`.
- Se confirmó nuevamente que el acceso directo desde SRT a `127.0.0.1:18080` permanece bloqueado (`HTTP=000`).
- El identificador lógico `local` continúa generando el aviso no fatal `unrecognized_model`; para esta validación se utilizó temporalmente `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1`.
- El modelo `Qwen3.5-0.8B-Q4_0.gguf` se mantiene como modelo de validación de transporte, no como candidato definitivo para generación de código.
- La evidencia completa quedó registrada en `docs/benchmark/F1.18D-B_Integracion_Claude_Code_LLM_local_2026-09-02.md`.

**Próximo paso:** iniciar **F1.19 — harness reproducible y confiable**, encargado de preparar/resetear el workspace y ejecutar fuera del sandbox del agente las verificaciones de confianza del benchmark.

### F1.19B — Workspace reproducible y aislamiento — PASS

- El workspace se materializa como clon Git independiente, sin hardlinks,
  alternates ni remotes, en detached HEAD del baseline exacto.
- La política SRT por corrida permite escritura solo en el workspace y runtime
  correspondientes; repositorio canónico y evidencia trusted quedan fuera.
- El preflight rechaza colisiones de workspace/runtime/evidencia y opera
  fail-closed.
- F1.19C reutilizó el mecanismo en una corrida integral y la regresión pasó.

### F1.19C — Reset de estado y verifier trusted `rat-default` — PASS

- PostgreSQL `pgvector/pg16` efímero sobre la red Docker internal
  `cumpleia-benchmark-net`.
- Runner mínimo con Python 3.12.3, filesystem read-only, sin Docker socket y
  workspace candidato montado read-only durante Alembic.
- Loader trusted del fixture Módulo 1 protegido por SHA-256, con IDs
  deterministas, 8 obligaciones, 10 secciones, 50 preguntas, v1 activa, 10
  pesos que suman 100 y 50 riesgos válidos.
- Tenants A/B, memberships y diagnósticos centinela deterministas.
- Verifier trusted de contenido, configuración, privilegios y aislamiento RLS.
- Generación fail-closed de `verification.json` y `tests.log` fuera del
  workspace, modo `0600`.
- Corrida integral `f119c-validation2-20260904`: PASS en los seis grupos de
  checks; PostgreSQL efímero eliminado al finalizar.

Documentación: `docs/benchmark/F1.19C_Reset_estado_verificacion_trusted_2026-09-04.md`.

**Próximo paso:** integrar la ejecución candidata y el perfil `rat-default` en
el ciclo completo que genera `result.json` y `manifest.sha256`.

### F1.19D — Ciclo completo, resultado y manifest — PASS

- `run-config` incorpora `taskFile`; tarea efectiva y hashes quedan preservados
  en evidencia.
- Preflight estricto de run, transport, baseline, tarea, perfil, timeout,
  credencial declarada y managed settings efectivos.
- Claude Code 2.1.252 se ejecuta dentro de SRT con entorno mínimo, runtime por
  corrida, timeout de grupo de procesos y sin acceso de lectura/escritura al
  repositorio canónico ni a evidencia trusted.
- Logs concurrentes limitados a 16 MiB, con redacción de la credencial efectiva
  antes de persistir y permisos `0600`.
- Estado final derivado únicamente por el harness: `PASS`, `FAIL`, `TIMEOUT` o
  `HARNESS_ERROR`.
- `result.json` autoritativo y `manifest.sha256` ordenado sobre toda la evidencia.
- Validaciones: ciclo controlado PASS, ejecutable externo bloqueado/FAIL,
  timeout real/TIMEOUT, manifest íntegro y 8 tests unitarios PASS.

Documentación:
`docs/benchmark/F1.19D_Ciclo_completo_resultado_manifest_2026-09-04.md`.

**Próximo paso:** F1.19E — retención/limpieza segura, validación de evidencia
cerrada y procedimiento operativo para rondas comparables entre candidatos.

### F1.19E — Retención, limpieza y cierre de evidencia — PASS

- Política versionada: workspace/runtime se eliminan solo después del cierre;
  evidencia se conserva y su borrado no está soportado.
- Validador independiente de cobertura y hashes del manifest, estructura JSON,
  coherencia cruzada, estados, tiempos, baseline, tarea y política SRT.
- Snapshot de managed settings incorporado a la evidencia.
- Cierre automático `0500` para el directorio y `0400` para sus archivos.
- Cualquier inconsistencia de cierre degrada el resultado a `HARNESS_ERROR`.
- Limpieza con dry-run por defecto y `--execute` explícito; objetivos derivados
  únicamente del runId bajo las raíces efímeras conocidas.
- Validación real: TIMEOUT coherente, evidencia PASS antes y después de limpiar,
  workspace/runtime eliminados y evidencia retenida.
- Suite trusted: 11 passed.

Documentación:
`docs/benchmark/F1.19E_Retencion_limpieza_evidencia_2026-09-04.md`.

**Próximo paso:** definir y ejecutar la primera ronda benchmark real con tarea,
candidatos, baseline y presupuesto comparables.

### F1.20A — Preflight de la primera ronda — PASS técnico

- Las imágenes Python 3.12.3 y pgvector/pg16 quedaron fijadas por digest.
- Los contenedores del runner eliminan todas las capacidades y aplican
  `no-new-privileges`, límite de 128 procesos y 256 MiB de memoria.
- La integración directa `f119f-hardening-20260904` repitió los seis grupos
  trusted con PASS y sin PostgreSQL residual.
- El ciclo completo `f119f-full-hardening-20260904` produjo TIMEOUT controlado,
  checks trusted PASS, evidencia cerrada/validada y limpieza efectiva.
- Dos pruebas de regresión cubren el pinning de imágenes y los argumentos de
  seguridad; la suite trusted completa terminó con 13 passed.
- Se estableció un gate funcional: `rat-default` valida infraestructura y
  baseline, pero no puede puntuar por sí solo una tarea nueva porque una
  solución vacía también puede superarlo.

Documentación:
`docs/benchmark/F1.20A_Preflight_primera_ronda_2026-09-04.md`.

**Próximo paso:** confirmar tarea y candidatos definitivos; después construir
el task file y verifier trusted específicos antes de consumir presupuesto de
modelos.

### F1.20B — Tarea y verifier N/A por sección — PASS

- La primera tarea funcional quedó fijada en
  `docs/benchmark/runner/tasks/na-section-v1.md`.
- El contrato exige conteos API `respondidas`/`no_aplica`, representación en
  dashboard y HTML, fórmula intacta, tests y alcance acotado.
- El perfil `rat-na-section-v1` encadena los seis checks de `rat-default` con
  cuatro pruebas funcionales aisladas y una validación trusted del diff.
- El código candidato se prueba sin red, secretos ni DB, en workspace
  read-only y con los límites de seguridad del runner.
- Validación negativa: el baseline intacto fue rechazado mientras los seis
  checks de infraestructura permanecieron en PASS.
- Validación positiva: una solución dorada temporal obtuvo 4 passed y superó
  el control de alcance; luego fue eliminada.
- Suite trusted: Ruff PASS, Black PASS, 15 passed y 1 skipped contextual.

Documentación:
`docs/benchmark/F1.20B_Tarea_y_verifier_NA_por_seccion_2026-09-04.md`.

**Próximo paso:** fijar este checkpoint como baseline y decidir candidatos,
timeout y presupuesto de la primera ronda.

### F1.20D — Cierre de la primera ronda RAT — CERRADA

- Tarea: `rat-na-section-v1` sobre el baseline común
  `f7d8eb223b8adbb97d7a042a24f7c9297447e99c`.
- Claude Sonnet 5: **FAIL**, 3/4 tests, 308.498130 s; faltó la
  representación explícita requerida de ambos conteos en dashboard.
- DeepSeek V4 Pro: **PASS**, 4/4 tests, 532.326318 s.
- Qwen3-4B local: **FAIL**, 1/4 tests, 60.880742 s; implementación incompleta
  en API, exportación HTML y contrato TypeScript/dashboard.
- Las tres evidencias y sus manifests pasaron el validador independiente
  trusted sin repetir corridas ni modificar evidencia o workspaces.
- Baseline, tarea, configuración y verifier de la ronda permanecen preservados.
- Una sola tarea no permite inferir un ranking general entre modelos.

Documentación:
`docs/benchmark/F1.20D_Cierre_primera_ronda_RAT_2026-09-04.md`.

**Próximo paso:** diseñar una segunda tarea representativa y fijar su verifier
trusted antes de ejecutar nuevos candidatos.

### F1.21A — Diseño de segunda tarea funcional — PASS

- Se fijó la tarea `organization-current-v1`: implementar
  `GET /organizations/current` con selección por `X-Organization-Id`, permiso
  `view_content`, lectura permitida a `viewer` miembro y rechazo de cruce
  entre tenants.
- El baseline actual no expone esa ruta, por lo que la validación negativa no
  dependerá de introducir una vulnerabilidad artificial.
- Aún no se ejecutaron candidatos ni se eligió/descargó un modelo local nuevo.
- F1.21B completó el perfil trusted y validó baseline negativo y solución
  dorada temporal.

Documentación:
`docs/benchmark/F1.21A_Diseno_segunda_tarea_organizacion_actual_2026-09-04.md`.

### F1.21B — Verifier trusted de organización actual — PASS

- Perfil `rat-organization-current-v1` encadenado a `rat-default`.
- Contenedor sin red, credenciales ni acceso de escritura al workspace.
- Contrato: 4/4 PASS con solución dorada temporal; 4/4 FAIL con baseline
  intacto, resultado esperado.
- Suite del harness: 17 passed, 2 skipped.
- La solución dorada y sus copias temporales fueron eliminadas tras validar.
- No se ejecutaron candidatos ni se modificaron evidencias existentes.

Documentación:
`docs/benchmark/F1.21B_Verifier_organizacion_actual_2026-09-04.md`.

**Próximo paso:** F1.21C — fijar commit baseline, hashes, candidatos, timeout
y presupuesto antes de ejecutar la segunda ronda.

### F1.21C — Configuración de segunda ronda RAT — PASS técnico

- Baseline: `4b3b4b74d71a312096b9329c6e80f5a31c40f03d`.
- Perfil: `rat-organization-current-v1`; tarea y hashes del verifier fijados.
- Candidatos comparables: Claude Sonnet 5, DeepSeek V4 Pro y Qwen3-4B local.
- Una ejecución por candidato, timeout común de 1.800 segundos y sin reintentos.
- No se incorpora aún un modelo local mayor: la RTX 5060 Laptop tiene 8 GiB
  de VRAM y Qwen3-8B ya resultó operacionalmente inviable en este transporte.
- Seis configuraciones validadas, preflight local PASS y suite trusted:
  21 passed, 2 skipped.

Documentación:
`docs/benchmark/F1.21C_Configuracion_segunda_ronda_RAT_2026-09-04.md`.

**Próximo paso:** autorizar explícitamente una ejecución autoritativa por cada
candidato de la segunda ronda.

### F1.21D — Reparación de sockets puente SRT — PASS

- Las corridas Qwen/Claude de segunda ronda no alcanzaron a ejecutar agentes:
  ambas reportaron fallo de creación de bridge sockets.
- Causa identificada: el `TMPDIR` por `runId` dejaba insuficiente margen bajo
  el límite Unix de 108 bytes para `cc-socks`.
- El harness ahora deriva un TMPDIR corto con hash, lo limita en SRT y lo
  elimina mediante limpieza trusted.
- Suite tras el cambio: 22 passed, 2 skipped; Ruff y Black PASS.
- Sonda aislada con TMPDIR corto y transporte local: PASS (`OK`), sin bridge
  socket error; sus directorios temporales fueron eliminados.

Documentación:
`docs/benchmark/F1.21D_Reparacion_sockets_SRT_2026-09-04.md`.

### F1.21E — Cierre de la segunda ronda RAT — CERRADA

- Tarea: `organization-current-v1` sobre baseline
  `4b3b4b74d71a312096b9329c6e80f5a31c40f03d`.
- Claude Sonnet 5: **PASS**, 4/4 tests, 261.639231 s.
- Qwen3-4B local: **FAIL**, 0/4 tests, 106.626028 s; no expuso la ruta y
  modificó un activo protegido de migración.
- DeepSeek V4 Pro: **FAIL**, 0/4 tests, 201.262959 s; no expuso la ruta ni
  agregó o modificó pruebas backend.
- Las tres evidencias efectivas y sus manifests pasaron el validador trusted.
- Los intentos previos cerrados por infraestructura o credencial permanecen
  preservados y no se usan como resultados comparables.
- Dos tareas aún no permiten inferir un ranking general entre modelos.

Documentación:
`docs/benchmark/F1.21E_Cierre_segunda_ronda_RAT_2026-09-04.md`.

**Próximo paso:** diseñar y validar una tercera tarea funcional independiente
antes de concluir rankings o reemplazar candidatos.

### F1.22A — Diseño de tercera tarea funcional: selector de organización activa — PASS

- Tarea `active-organization-selector-v1`: resolver la selección explícita de
  tenant en las pantallas de organización y autodiagnóstico para usuarios con
  múltiples membresías.
- El contexto activo viaja en el parámetro URL `organization`, se valida contra
  la lista obtenida por el servidor y nunca se reenvía un UUID ajeno al backend.
- Alcance independiente de F1.20/F1.21: Next.js, TypeScript, UI accesible y
  propagación de contexto existente; no cambia backend, RLS ni migraciones.
- F1.22B deberá probar baseline negativo, selector accesible, propagación del
  UUID válido y fallback seguro ante UUID ajeno.

Documentación:
`docs/benchmark/F1.22A_Diseno_tercera_tarea_selector_organizacion_2026-09-04.md`.

**Próximo paso:** F1.22B — implementar y validar el verifier trusted de la
tercera tarea antes de fijar candidatos.

### F1.22B — Verifier trusted de selector de organización activa — PASS

- Perfil `rat-active-organization-selector-v1` aislado y encadenado a
  `rat-default`.
- Baseline: 4 fallos esperados; solución dorada temporal: 6/6 PASS.
- Suite trusted: `23 passed, 3 skipped`; worktree dorado eliminado.

Documentación:
`docs/benchmark/F1.22B_Verifier_selector_organizacion_2026-09-04.md`.

**Próximo paso:** F1.22C — fijar baseline, hashes y candidatos.

### F1.22D — Cierre de tercera ronda RAT — CERRADA

- Qwen3-4B local: FAIL, 2/6, 112.377609 s.
- Claude Sonnet 5 r2: FAIL, 3/6, 350.831602 s.
- DeepSeek V4 Pro: FAIL, 2/6, 206.228365 s.
- Las tres evidencias efectivas pasaron validación trusted; la primera corrida
  de Claude se preserva como incidencia de etiqueta incorrecta.

Documentación:
`docs/benchmark/F1.22D_Cierre_tercera_ronda_RAT_2026-09-04.md`.

### F1.23A — Calibración del verifier de selector — PASS

- La solución retenida de Claude r2 cumplía el comportamiento de seguridad,
  pero F1.22 exigía un nombre literal de helper.
- F1.23B sustituirá esas convenciones por controles observables de validación,
  fallback, propagación de contexto y selector accesible.

Documentación:
`docs/benchmark/F1.23A_Calibracion_verifier_selector_2026-09-04.md`.

### F1.23B — Verifier calibrado de selector — PASS

- Perfil v2 conserva F1.22 histórico y elimina exigencias de nombres internos.
- Baseline FAIL; workspace retenido de Claude r2 PASS 4/4 en sólo lectura.

Documentación:
`docs/benchmark/F1.23B_Verifier_calibrado_selector_2026-09-04.md`.

### F1.23D — Cierre de ronda comparativa calibrada — CERRADA

- Claude Sonnet 5: **PASS**, 4/4, 523.724770 s.
- Qwen3-4B local: **FAIL**, 1/4, 176.574400 s.
- DeepSeek V4 Pro: **FAIL**, 1/4, 203.544294 s.
- Tres evidencias y manifests trusted verificados; la calibración eliminó el
  falso negativo de F1.22 por convención de nombre.

Documentación:
`docs/benchmark/F1.23D_Cierre_ronda_calibrada_RAT_2026-09-07.md`.

## 2026-09-02 — F1.19A cerrado: contrato y estructura del harness reproducible

Se completó F1.19A del benchmark.

Resultado: PASS.

Artefactos incorporados:

- `docs/benchmark/F1.19A_Contrato_harness_2026-09-02.md`
- `docs/benchmark/runner/run-config.schema.json`
- `docs/benchmark/runner/run-result.schema.json`
- `docs/benchmark/runner/run-config.example.json`

El diseño establece:

- separación explícita entre harness trusted y candidato untrusted;
- workspace efímero controlado por el harness;
- baseline identificado por commit Git completo;
- reutilización independiente del contrato de transporte F1.18A;
- estados autoritativos `PASS`, `FAIL`, `TIMEOUT` y `HARNESS_ERROR`;
- resultado estructurado `result.json`;
- evidencia por corrida con manifest SHA-256;
- prohibición de persistir secretos en configuración, logs o resultados;
- regla fail-closed ante fallas del entorno trusted;
- invariantes de reproducibilidad para comparación entre candidatos.

Los schemas fueron validados con JSON Schema Draft 2020-12.

Pruebas realizadas:

- configuración válida aceptada;
- resultado válido aceptado;
- commit corto rechazado;
- campo adicional rechazado;
- estado inválido rechazado;
- campo obligatorio faltante rechazado;
- ejemplo de configuración validado contra el schema.

La ubicación del workspace no es controlable por la configuración de corrida; será determinada exclusivamente por el harness trusted.

Siguiente etapa: F1.19B — workspace reproducible y aislamiento del repositorio canónico.

### §118 — correccion del arranque local

El primer arranque del frontend sobreescribia en memoria la clave publica de
.env.local con un valor de ejemplo del backend y causaba Invalid API key.
Se detuvo ese proceso y se reinicio Next usando su .env.local existente, sin
editar credenciales. La clave publica del frontend responde 200 en auth/v1/settings;
/login responde 200. Sesion personal y comprobacion administrativa aun pendientes.
No se registran claves ni tokens. Sin commit/push.
