# M3-T1 — Expediente de validacion operativa EIPD

Fecha: 2026-10-09. §111. Estado: DIAGNOSTICO INICIAL; PROVISION NO ACREDITADA.
Base observada limpia/sincronizada: d57b2206b2ae432ae93e6a278e24483d4db1ece9,
rama feature/m3-t1-licitud-persistencia. No equivale a SHA desplegado en un entorno
operativo ni a aceptacion integral. Referencia: m3-t1-eipd-provision-operativa.md.

## Evidencia ejecutada

| Comprobacion | Resultado observado | Limite |
| --- | --- | --- |
| Settings.environment | development | Etiqueta configurada, no certifica destino operativo |
| Hosts configurados de mantenimiento/runtime tenant | Loopback en ambos | No acredita ubicacion fisica ni excluye forwarding |
| EIPD_ADMIN_DATABASE_URL presente | false | No se leyó/imprimio valor de secreto |
| Preflight con configuracion actual | Exit 1, failed | Canal no acreditado; no se inicializa pool dedicado sin configuracion |
| Head via mantenimiento, alembic current | b17d95c0286f (head) | Consulta local, no acredita head de otro entorno |
| Ultima suite completa registrada | 3654 §106 | No se ejecuto nueva suite en §111 |
| Ultimas focalizadas de preflight/canal | 31 §110 | Fixtures sinteticos; no provision operativa |

Salida CLI obtenida, sin secreto/URL/JWT:

```json
{"activation_authorized": false, "channel_verified": false, "status": "failed"}
```

El exit 1 es esperado con la configuracion administrativa ausente observada.
No es evidencia de fallo de una credencial concreta ni de corrupcion del selector.
No se consultaron filas tenant ni se crearon roles/perfiles/publicaciones/selecciones.
No se reescribio .env ni se inyecto una URL por defecto. No se usa conexion owner
como fallback del canal; mantenimiento solo consulto el head de migraciones.

## Campos pendientes para continuar

| Campo | Estado |
| --- | --- |
| Destino elegido (desarrollo local u otro entorno de pruebas) | Desarrollo local, seleccionado por el usuario (§112) |
| Identidad de base y commit desplegado del destino | PENDIENTE |
| Responsable operativo y ventana de validacion | PENDIENTE |
| Login dedicado y referencia de secreto provisionado | PENDIENTE |
| Staff autenticado/perfil superadmin vigente | PENDIENTE |
| Preflight del canal configurado, alcance/permisos/selector | PENDIENTE |
| Humo JWT/HTTP positivo/negativo y auditoria persistida | PENDIENTE |
| Retirada/rotacion y registro revisado | PENDIENTE |

Se solicito el destino al usuario; no interpretar tiempo sin respuesta como
seleccion o aprobacion. No pedir secretos por chat. Una vez indicado el destino,
acreditarlo y completar provision por canal seguro conforme §108–110, manteniendo
politica deshabilitada. Las pruebas sinteticas anteriores no crean una identidad
staff real ni permiten llenar los campos pendientes con actores inventados.
Fuentes complementarias/decision real de aceptacion siguen pendientes por separado.
Ley reformada base fija; activacion bloqueada; M3-T1 EN PROGRESO integral.

## §112 — Destino local seleccionado; provision pendiente (2026-10-09)

Usuario selecciona desarrollo local. Inspeccion readonly confirma etiqueta development,
host de mantenimiento loopback, head b17d95c0286f, canal EIPD ausente y login
propuesto eipd_backend_local inexistente. Hay un perfil superadmin en la base;
solo se consulto su cantidad, no se acredita usuario staff ni se modifica identidad.
Usuario staff solicitado por correo/sub, sin tokens/passwords, pendiente de respuesta.

Accion preparada: crear eipd_backend_local LOGIN NOINHERIT NOSUPERUSER NOCREATEDB
NOCREATEROLE NOREPLICATION NOBYPASSRLS; membresia solo eipd_policy_admin; generar
credencial nueva y guardarla en ~/.config/cumpleia-local-eipd/admin.env con modo 0600,
fuera del repositorio, sin imprimir valor ni modificar .env. No implica creacion o
promocion de perfiles, publicacion/seleccion ni activacion. Preflight posterior de
solo lectura; humo JWT/HTTP requiere identidad staff verificada.

Revision automatica rechazo la accion antes de ejecucion: crear login persistente,
membresia administrativa y credencial no estaba explicitamente autorizado por la
eleccion de entorno. Ningun login/archivo/secret nuevo creado; no se reintenta ni se
usa canal alternativo. Se solicita aprobacion humana concreta para esa provision.
Aceptacion operativa no acreditada. Activacion bloqueada; M3-T1 EN PROGRESO.

## §113 — Provision tecnica local autorizada y ejecutada (2026-10-09)

Usuario autoriza explicitamente login limitado/membresia/credencial externa tras
pregunta concreta §112. Se crea eipd_backend_local LOGIN NOINHERIT NOSUPERUSER
NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS, miembro solo eipd_policy_admin.
Credencial nueva en ~/.config/cumpleia-local-eipd/admin.env, modo 0600. Valor no
impreso ni copiado al repo; .env habitual no modificado. Configuracion cargada solo
en proceso de diagnostico; no se acredita backend HTTP iniciado con este secreto.
No se promueve perfil ni se publica/selecciona politica.

Preflight ejecutado contra canal provisionado; codigo logico confirmado 2:

```json
{"activation_authorized":false,"audit_coherent":true,"channel_verified":true,"environment_identity_verified":false,"migration_head_verified":false,"permission_scope":"public_relations_and_role_flags","permissions_verified":true,"personal_authentication_verified":false,"report_version":1,"selector_present":false,"selector_revision":null,"status":"pending_selector"}
```

Primera invocacion con SystemExit(2) aparece como exit 1 en envoltorio PowerShell;
segunda consulta readonly registra explicitamente codigo de main=2. No confundir
traduccion del envoltorio con status failed: informe es pending_selector.
Auditoria coherente sin selector; no bootstrap automatico. Credencial/rol tecnicos
provisionados localmente, pero validacion operativa integral sigue PENDIENTE.

| Campo actualizado | Resultado |
| --- | --- |
| Login tecnico | eipd_backend_local, atributos/membresia limitados verificados |
| Referencia del secreto | Archivo privado externo, ~/.config/cumpleia-local-eipd/admin.env |
| Preflight local con secreto cargado | pending_selector, codigo logico 2; canal/permisos/auditoria validos |
| Selector actual | Ausente; no se creo ni se selecciono politica |
| Staff autenticado/perfil superadmin | PENDIENTE de correo/sub confirmado por usuario |
| Backend HTTP configurado para canal | PENDIENTE; .env habitual no alterado |
| Humo JWT/HTTP, publicacion/seleccion y retirada | PENDIENTE |

Solicitar identidad staff sin contrasena/token. La presencia de un superadmin no
permite elegirlo ni promover a otra persona a ciegas. Proximo paso identificar
staff y vinculo de perfil, luego configurar proceso local por canal seguro y validar
HTTP con politica deshabilitada. No quitar guardias productivas. Fuentes/aceptacion
real aun pendientes; M3-T1 EN PROGRESO y activacion bloqueada.

## §114 — Staff indicado y verificacion pendiente (2026-10-09)

Usuario informa correo de staff (no se reproduce PII en evidencia versionada).
Consulta parametrizada readonly: exactamente un perfil local, auth_user_id presente,
is_superadmin=false. No se modifica ni promueve perfil. Configuracion de autenticacion
presente; GET administrativo readonly del usuario por ID no se completa: ConnectError
en etapa auth_request. No respuesta de Supabase ni identidad externa/JWT acreditados.
Metodo GET consultado en fuente primaria de Supabase auth-js GoTrueAdminApi.
No secretos/URL/JWT/respuestas privadas impresos, ni mensajes enviados al usuario.

Pendientes: identificador de Supabase aportado por usuario para contrastar el vinculo,
autorizacion explicita de superadmin global del perfil local indicado, y humo JWT/HTTP
con proceso configurado. Permiso global permite acceso a organizaciones del entorno
local; elegir staff/correo no se interpreta como promocion autorizada. Canal tecnico
§113 disponible, selector ausente; sin nuevas politicas ni activacion. Sin nueva suite;
ultima 3654 §106/focalizadas 31 §110. EN PROGRESO; sin commit/push.

## §115 — Superadmin local explicitamente autorizado (2026-10-09)

Usuario autoriza superadmin global en base local para el perfil del correo indicado.
Mantenimiento verifica entorno development/host loopback, exactamente un perfil y
vinculo auth_user_id presente, toma FOR UPDATE y cambia solo is_superadmin=true
por id/auth_user_id existentes. Commit realizado y lectura posterior confirma true.
No se crea usuario, cambia email/sub ni modifica Supabase. PII/IDs no se imprimen
ni se incorporan a evidencia versionada. Alcance: organizaciones de base local.

Autoridad local provisionada por autorizacion humana; identidad externa de Supabase
/JWT personal sigue sin verificar (ConnectError previo; User UID aun pendiente).
No declarar humo HTTP aprobado ni sources_status/aceptacion/activacion habilitadas.
Canal tecnico §113 permanece; selector/politica sin cambios. No nueva suite ni
migracion; ultima 3654 §106, focalizadas 31 §110. Proximo contrastar User UID y
completar autenticacion/proceso HTTP configurado. EN PROGRESO; sin commit/push.

## §116 — UID contrastado y rechazo HTTP anonimo (2026-10-09)

Usuario aporta User UID de Supabase; consulta local readonly confirma un perfil
unico por correo, auth_user_id coincide exactamente con UID aportado y superadmin=true.
No se reproduce PII/UID en evidencia versionada. Este contraste usa dato aportado
por usuario y base local; no acredita respuesta externa de Supabase ni JWT firmado.

Backend local 127.0.0.1:8000 responde health 200; OpenAPI 200 registra POST
/admin/eipd/publications y /admin/eipd/selections. Ambas solicitudes sin token
(cuerpo vacio) -> 401. No filas/identidad/canal de DB mutados. Prueba negativa
real acreditada; no acredita SHA del proceso, carga del secreto EIPD o prueba positiva.

Pendiente proceso HTTP configurado con secreto privado del canal y solicitud
personal JWT validada por issuer/JWKS, seguida de publicacion/seleccion deshabilitada
y auditoria/retirada. No solicitar tokens/passwords por chat; usar inicio de sesion
local y canal seguro. ConnectError previo en consulta de autenticacion externa
no se considera resuelto por el contraste UID. Canal tecnico y autoridad local
estan provisionados; selector ausente. Fuentes/aceptacion pendientes, activacion
bloqueada; EN PROGRESO. Sin nueva suite ni commit/push.

## §117 — Proceso local configurado e identidad externa verificada (2026-10-09)

Base limpia 6474873b2cd0eb0a9e941322cbca04bb9e59d365. Archivo privado externo
presente, modo 0600 validado; carga solo en memoria de nuevo proceso local,
DEBUG=false, access_log=false, uvicorn en 127.0.0.1:8001. Proceso de validacion
separado del backend existente 8000; .env habitual sin cambios y secreto no impreso.
Sesión de herramienta que mantiene proceso: 30969 (referencia efimera, no garantiza
persistencia tras cierre/reinicio de herramienta). No despliegue remoto ni servicio
persistente del sistema; verificar salud antes de cada paso.

DNS de proyecto de autenticacion accesible y JWKS publico GET 200. Reintento GET
administrativo readonly de usuario Supabase -> 200; id/correo coinciden con perfil
local y dato humano aportado, email confirmado, superadmin local true. ConnectError
anterior ya no se reproduce en estas consultas. No se exponen PII/claves/respuestas.
Esto acredita identidad externa por consulta administrativa, no JWT de sesion personal.

Proceso nuevo health 200; POST ambas rutas EIPD sin token -> 401. No se publica ni
selecciona politica ni modifica perfil. Credencial privada del canal cargada por
proceso iniciado; pool inicializacion diferida, prueba readonly del canal acreditada
§113. No inferir solicitud autenticada por salud o rechazo anonimo.

Se intento inspeccion de navegador mediante herramienta CUA; inicializacion falla
por helper/setup refresh, sin estado de navegador disponible. Habilidad instalada
leida (computer-use 26.1002.52244); ruta anterior del catalogo ausente, encontrada
mediante busqueda local. No bypass de automatizacion ni extraccion de tokens.
Pendiente sesion autentica del usuario por canal local seguro. No pedir contrasena/
JWT por chat ni generar token sintetico como evidencia operacional.

Proximo: solicitud autenticada con JWT real del staff contra proceso configurado,
politica deshabilitada y auditoria; requiere acceso a sesion del usuario. Fuentes/
aceptacion/provision integral siguen pendientes; activacion bloqueada. Sin nueva
suite, ultima completa 3654 §106 y focalizadas 31 §110. M3-T1 EN PROGRESO.
Sin commit/push.

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

### §118 — correccion del arranque local

El primer arranque del frontend sobreescribia en memoria la clave publica de
.env.local con un valor de ejemplo del backend y causaba Invalid API key.
Se detuvo ese proceso y se reinicio Next usando su .env.local existente, sin
editar credenciales. La clave publica del frontend responde 200 en auth/v1/settings;
/login responde 200. Sesion personal y comprobacion administrativa aun pendientes.
No se registran claves ni tokens. Sin commit/push.

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

## Validacion local publicacion

La referencia de la propuesta identifica este procedimiento operacional; no acredita
por si sola una publicacion ejecutada ni aceptacion juridica. Resultado personal
pendiente hasta la comprobacion real aportada por el usuario.

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

## Validacion local seleccion

La seleccion personal esta preparada y pendiente de ejecucion real. La referencia
identifica el procedimiento, sin acreditar por si sola resultado ni aceptacion.

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
