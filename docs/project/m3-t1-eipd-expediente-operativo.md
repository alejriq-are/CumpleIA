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
