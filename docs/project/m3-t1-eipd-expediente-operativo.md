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
