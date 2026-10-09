# M3-T1 — Provision operativa del canal EIPD deshabilitado

Fecha: 2026-10-09. Procedimiento base §108; actualizacion §122.
Estado: SECUENCIA LOCAL DESHABILITADA VALIDADA (§118–121); rotacion/retiro y
entornos adicionales pendientes. Ver m3-t1-eipd-cierre-validacion-local.md.
Base de codigo revisada 6a6fd27f878a7612d0ceeb9abdcdf968b9f2bf0e.
Ley 21.719/19.628 reformada es base fija. No autoriza activacion excepcional,
verificacion ficticia de fuentes ni aceptacion integral. Evidencia local disponible:
3654 pruebas §106; trazabilidad y pendientes §107.

## 1. Registro previo del entorno

Completar el expediente siguiente antes de cambiar el entorno. Usar referencias
del gestor de secretos/evidencias; nunca pegar URL con password ni JWT en este
archivo, tickets, logs, historial de terminal o argumentos visibles de procesos.

| Campo | Valor a completar | Evidencia requerida |
| --- | --- | --- |
| Entorno y responsable operativo | PENDIENTE | Entorno aislado y ventana acordada |
| Commit desplegado y version de backend | PENDIENTE | SHA exacto y registro de despliegue |
| Base destino/head aplicado | PENDIENTE | Identidad de DB sin secreto; head b17d95c0286f o sucesor revisado |
| Login tecnico dedicado | PENDIENTE | Catalogo de roles/permisos, distinto de owner/app_user |
| Referencia del secreto EIPD_ADMIN_DATABASE_URL | PENDIENTE | Inyeccion segura, sin copiar su valor |
| Identidad staff y perfil superadmin vigente | PENDIENTE | Vinculo sub/perfil revisado por mantenimiento autorizado |
| Emisor/audiencia y JWKS de autenticacion | PENDIENTE | Configuracion del proyecto correcto; acceso JWKS |
| Selector/revision inicial y politica auditada | PENDIENTE | Lectura coherente previa; no asumir revision cero |
| Referencia unica de publicacion deshabilitada | PENDIENTE | Motivo y referencia de expediente operativos |
| Resultados HTTP/estado posterior/retirada | PENDIENTE | Evidencias sin secretos y responsable de revision |

No se presupone que exista selector o staff superadmin; confirmar ambos. El login
DB no sustituye al usuario autenticado. La API EIPD no crea perfiles JIT ni promueve
usuarios: cualquier alta de staff se realiza por el proceso de mantenimiento
explicitamente autorizado, con identidad Supabase verificada. Un owner de tenant
no basta. El total de tests no rellena esos campos ni acredita entorno operativo.

## 2. Provision tecnica controlada

Mantenimiento aplica las migraciones por su canal habitual; el backend tenant
conserva APP_DATABASE_URL/app_user. EIPD_ADMIN_DATABASE_URL apunta a otra conexion
con login dedicado, en la misma base revisada. DATABASE_URL owner sigue reservado
para migraciones/mantenimiento. No reutilizar service_role de Supabase como JWT
personal de staff ni como sustituto de este canal.

Plantilla de roles para revisar por mantenimiento; nombres ilustrativos, no
credenciales y no instrucciones ejecutadas en §108:

```sql
CREATE ROLE eipd_backend_login NOLOGIN NOINHERIT NOSUPERUSER
  NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT eipd_policy_admin TO eipd_backend_login;
```

El rol de grupo eipd_policy_admin debe seguir NOLOGIN y limitado por migraciones.
El login dedicado no recibe membresias adicionales, ADMIN OPTION, propiedad de
relaciones ni grants directos de dominio. No conceder eipd_policy_admin a app_user.
Provisionar el metodo de autenticacion y secreto mediante el mecanismo seguro del
entorno; solo entonces habilitar LOGIN en el login dedicado. No almacenar password
en esta plantilla ni copiar claves reales al repositorio. Revisar permisos de
conexion/schema y las restricciones efectivas; la plantilla no certifica permisos
heredados de PUBLIC ni configuracion de red/autenticacion del servidor.

Inyectar EIPD_ADMIN_DATABASE_URL en forma postgresql+asyncpg, con login dedicado,
secreto y destino revisados. Backend no usa fallback si falta. Mantener permisos
sin echo de SQL/parametros para este engine. Cambios del secreto/config requieren
renovar procesos y conexiones: Settings/factory estan cacheados. No basta editar
una variable en un worker ya inicializado. No activar LOGIN en el grupo.

## 3. Comprobaciones previas sin escrituras de politicas

Desde la conexion dedicada, verificar la identidad DB y exactamente las condiciones
de app/db/eipd_admin.py::_prepare_channel: LOGIN, NOINHERIT, sin superuser/BYPASSRLS/
CREATEDB/CREATEROLE/REPLICATION; miembro del grupo, sin otras membresias directas
ni propiedad de relaciones. Verificar tambien que el grupo conserve sus privilegios
limitados. Rechazar reutilizacion de owner/app_user. No imprimir la cadena de conexion.

Prueba de rol local sin establecer identidad personal ni escribir dominio:

```sql
BEGIN;
SELECT session_user, current_user, current_database();
SHOW transaction_isolation;
SET LOCAL ROLE eipd_policy_admin;
SELECT current_user;
ROLLBACK;
SELECT current_user, NULLIF(current_setting('request.jwt.claim.sub', true), '');
```

Esperado: login dedicado como session_user, READ COMMITTED, rol de grupo solo dentro
de la transaccion; despues rol dedicado e identidad vacia. No establecer manualmente
sub como sustituto de prueba JWT: la identidad personal se prueba por la API.
Catalogo debe mostrar EXECUTE de lock_eipd_personal_authority_v1 solo para el canal
limitado (y owner de mantenimiento), sin privilegios de UPDATE sobre profiles.
Las publicaciones/eventos son append-only para canal; selector admite UPDATE,
no DELETE/TRUNCATE. Confirmar que el login no accede al dominio tenant por grants
adicionales. Si falla, corregir provision y repetir; no ampliar grants indiscriminadamente.

Mantenimiento lee el snapshot auditado completo con
read_eipd_policy_audit_snapshot_v1 en una transaccion de lectura revisada, o utiliza
una herramienta operativa equivalente que valide hash/cadena/selector. Desde §119 existe GET /admin/eipd/audit protegido por autoridad personal, que
valida el snapshot; en §105 esa ruta aun no existia.
Ausencia de selector validada equivale a expected_revision=0. Si hay selector,
registrar su revision real; si hay corrupcion o politica habilitada inesperada,
interrumpir la puesta en servicio y revisar el incidente. No modificar filas para
hacer coincidir una prueba, ni borrar historial para volver a revision cero.

## 4. Prueba HTTP controlada y politica deshabilitada

Usar cliente que obtenga el token por un canal seguro. Validar firma/expiracion/
audiencia/emisor con el JWKS configurado. No compartir ni registrar el token.
Primero probar respuestas negativas con cuerpos validos: sin token/invalido -> 401;
usuario tenant sin autoridad global -> 403; configuracion ausente o pool inadecuado
-> 503. El estado auditado debe conservarse. No enviar pruebas con fuentes o
aceptaciones inventadas a un entorno compartido.

Ejemplo de cuerpo de publicacion; sustituir referencia/motivo/evidencia por los
valores del expediente antes de enviarlo. Es un ejemplo pendiente, no una
verificacion ni una publicacion operativa ejecutada:

```json
{
  "policy": {
    "policy_version": 1,
    "policy_reference": "provision-deshabilitada-REFERENCIA-UNICA",
    "routes": [],
    "sources_status": "pendiente",
    "source_records": [],
    "acceptance_status": "pendiente",
    "acceptance_reference": null,
    "validation_commit": null,
    "acceptance_evidence_reference": null,
    "accepted_by": null,
    "activation": "deshabilitada"
  },
  "rationale": "SUSTITUIR por motivo operativo revisado",
  "evidence_reference": "SUSTITUIR por referencia de expediente"
}
```

POST /admin/eipd/publications con staff autorizado -> 201; registrar id/hash/actor/
fecha de respuesta y comprobar persistencia con lectura auditada. Actor debe ser
el perfil del sub verificado, sin actor del body. Publicar no selecciona. Repetir
la misma referencia -> 409 y una sola publicacion; campos extra como actor_id -> 422.
No crear nuevas referencias a ciegas cuando falle una peticion: comprobar primero
si el commit se produjo. El historial persiste; una prueba positiva modifica el
registro global y debe realizarse en el entorno/ventana previstos.

Seleccion es una decision separada. POST /admin/eipd/selections lleva publication_id
obtenido, expected_revision de la lectura previa, rationale y evidence_reference
propios; no actor/fecha/hash del cliente. 201 devuelve evento/selector; verificar
exactamente una revision nueva, cadena/hash coherentes, actor y politica deshabilitada.
409 por revision obsoleta exige releer/revisar y decidir; no reintentar con revision
nueva automaticamente. Publicaciones ya seleccionadas no pueden reseleccionarse.
Mantener la barrera excepcional; un 201 de administracion no habilita confirmaciones.

En entorno de validacion aislado acreditar tambien revocacion concurrente,
rollback/cancelacion, seleccion competidora y referencia duplicada: matriz §106.
No ejecutar estas pruebas de contencion ni cambios de autoridad como humo sobre
usuarios reales de produccion. La suite local es evidencia de implementacion;
la ejecucion operativa debe registrar su propio resultado/entorno/responsable.

## 5. Retirada, revocacion y cambios de secreto

Para retirar el canal, detener admision de nuevas solicitudes administrativas,
controlar las que estan en curso y renovar/cerrar workers y pools del canal. LOGIN
puede deshabilitarse en el login dedicado por mantenimiento; eso bloquea conexiones
nuevas y el chequeo de rol rechaza solicitudes nuevas, pero no cancela operaciones
ya autorizadas. Revocar is_superadmin usa proceso autorizado: UPDATE espera a que
terminen las transacciones con lock personal; las solicitudes posteriores se
rechazan. Registrar el momento efectivo, no prometer cancelacion instantanea.

Rotacion de credencial requiere actualizar el gestor/config y renovar workers/pool,
comprobar que nuevas conexiones usan la credencial nueva y retirar la anterior
segun procedimiento del entorno. Para retirar privilegios, coordinar REVOKE del
login tras drenar sesiones; no retirar grants del grupo compartido como sustituto.
No DROP de rol/perfil referenciado por auditoria, DELETE de publicaciones/eventos,
reseleccion de historia ni downgrade de migraciones para deshacer un humo. Si se
necesita cambiar selector, crear nueva publicacion deshabilitada y evento trazable
por el canal, con revision vigente. Conservar evidencia de operacion y retirada.

## 6. Criterio de cierre del procedimiento

Provision acreditada solo cuando el expediente contiene resultados reales,
responsable, entorno, commit/head, login verificado, identidad staff, pruebas
negativas/positivas, lectura auditada y retirada/rotacion probadas en entorno
apropiado. Si no se ejecuto, conservar PENDIENTE; no firmar accepted_by ni declarar
sources_status verificadas. Fuentes complementarias y aceptacion real de activacion
siguen siendo requisitos separados (§107); este procedimiento no los completa.

§108 prepara este documento y valida el esquema del JSON de ejemplo. No crea roles,
credenciales, perfiles, publicaciones o selecciones reales. Sin migracion/despliegue,
sin nueva suite completa. Ultima suite 3654 (§106); M3-T1 EN PROGRESO integral.

## 7. Preflight disponible (§109)

Desde backend ejecutar `python -m scripts.eipd_admin_preflight` con configuracion
segura ya provisionada. Script no acepta URL/JWT por argumentos ni imprime secretos.
Exit 0/JSON ok: canal y selector deshabilitado coherentes; exit 2/pending_selector:
canal/auditoria validos sin selector, sin bootstrap; exit 1/failed: revisar por canal
operativo seguro, no volcar secretos a logs para diagnosticar. Transaccion READ ONLY,
rollback siempre. Salida no acredita autenticacion personal, aceptacion o activacion.
No verifica exhaustivamente grupo/grants de dominio/red/entorno; las comprobaciones
del resto del procedimiento siguen pendientes. No sustituir smoke JWT/HTTP por
preflight ni usar su ok como permiso de habilitar. §109 probado con fixtures locales,
no ejecutado contra un entorno operativo real.

## 8. Alcance ampliado del informe (§110)

Se mantiene el comando y codigos de §109. Ahora verifica atributos/membresias/
propiedad del grupo, ADMIN OPTION del login, CREATE public, RLS y permisos de tres
tablas globales, accesos efectivos fuera de alcance sobre relaciones public, incluidos
PUBLIC/grants por columna. No verifica exhaustivamente funciones/secuencias/otros
schemas ni contenido de politicas RLS, ni sustituye head/migraciones revisados.

JSON incluye report_version=1 y permissions_verified=true solo tras completar esas
comprobaciones; permission_scope=public_relations_and_role_flags. Campos
migration_head_verified/environment_identity_verified/personal_authentication_verified/
activation_authorized=false distinguen el diagnostico de la validacion operativa.
Registrar informe/exit junto con referencia del entorno, commit/head comprobados por
mantenimiento, fecha/responsable y resultados HTTP. No conceder SELECT sobre
alembic_version al canal solo para completar evidencia: comprobar head por mantenimiento.
Un ok no acredita el destino correcto ni acepta una politica. Si faltan expediente,
identidad o resultados reales, conservar PENDIENTE. §110 no ejecuta provision real.

## 9. Primera evidencia del entorno (§111)

Resultados reales iniciales en m3-t1-eipd-expediente-operativo.md. Configuracion
administrativa ausente; preflight exit 1/failed esperado, sin pool dedicado.
Head local consultado por mantenimiento b17d95c0286f. Provisión no acreditada;
destino solicitado al usuario y pendiente, sin credenciales/actor real disponibles.
No confundir etiqueta development/loopback con identificacion operativa completa.

## 10. Canal local provisionado (§113)

Autorizacion concreta recibida; login limitado creado y credencial privada externa
0600. Evidencia en expediente §113: preflight pending_selector/codigo 2, canal/
permisos/auditoria verificados sin selector. .env habitual no alterado; solo proceso
de diagnostico carga secreto. Backend HTTP, identidad staff, humo/seleccion y retirada
pendientes. No trasladar valor del archivo privado a evidencia ni commitearlo.

## 11. Proceso de validacion local (§117)

Proceso efimero separado 127.0.0.1:8001 carga archivo privado mediante dotenv en
memoria, DEBUG=false/access_log=false; backend previo 8000 no reiniciado ni .env
modificado. Health 200 y rutas 401 sin token. DNS/JWKS accesibles; identidad staff
contrastada por lectura administrativa Supabase 200. Prueba JWT de sesion personal
pendiente: no sustituirla por consulta admin, token sintetico o flags locales.
Tras reinicio/cierre comprobar proceso/config antes de continuar; referencia de
sesion efimera en expediente. No pegar secretos/tokens en evidencia ni chat.

## §118 — comprobacion mediante sesion personal local

Con los procesos locales disponibles, iniciar sesion normalmente en
http://localhost:3000 y abrir /admin/eipd-validation; pulsar Comprobar acceso.
La pantalla solo funciona en desarrollo y consulta GET /admin/eipd/status en
127.0.0.1:8001 con la sesion del navegador. No compartir contrasenas ni tokens por
chat. El resumen de acceso no sustituye el snapshot completo de auditoria ni
habilita activacion. Registrar el resultado real antes de avanzar a escrituras
con politica deshabilitada. Si los procesos terminaron, reiniciarlos con el canal
privado existente sin copiar secretos al repositorio.

## §119 — revision antes de escrituras

En /admin/eipd-validation, pulsar Consultar registro con la sesion personal.
GET /admin/eipd/audit valida el snapshot completo y permite obtener la revision
actual antes de una seleccion. La UI muestra revision y resumen; consultar no
publica ni selecciona. Ante error, no inferir revision cero ni reintentar escrituras
a ciegas. Registrar el resultado real; la activacion permanece bloqueada.

## §120 — publicacion explicita deshabilitada

En /admin/eipd-validation, pulsar Preparar publicacion, revisar referencia, estado,
motivo y evidencia. Publicar politica deshabilitada guarda una publicacion permanente
local con actor/fecha/hash del servidor, sin seleccion ni activacion. La pantalla
contrasta el resultado mediante GET /audit. Ante referencia ya registrada o error,
consultar el registro antes de continuar; no repetir POST a ciegas. Registrar el
resultado personal real; este procedimiento no constituye aceptacion juridica.

## §121 — seleccion personal y pruebas aisladas

En /admin/eipd-validation, pulsar Preparar seleccion, revisar referencia y revision,
y pulsar Seleccionar politica deshabilitada. Se guardan evento y selector local;
la politica permanece deshabilitada. Ante 409 o resultado incierto consultar el
registro, sin repetir POST a ciegas. Registrar la comprobacion posterior real.

Las suites de escritura deben usar cumpleia_eipd_tests_20261009 con DATABASE_URL y
APP_DATABASE_URL apuntando a esa base solo en el proceso de pruebas, conservando
respectivamente roles mantenimiento/app_user. No copiar credenciales a documentos
ni cambiar el entorno del backend operacional. Base vacia creada/migrada en §121;
las pruebas no deben ejecutarse contra el registro personal de desarrollo.

## §123 — entrada de pruebas focalizadas

Desde backend, usar `../.venv/bin/python -m scripts.run_eipd_tests` sin argumentos.
El ejecutor exige la base local aislada cumpleia_eipd_tests_20261009 existente,
head b17d95c0286f, registro EIPD vacio y runtime app_user restringido; redirige URLs
solo en el proceso hijo. No cambia .env ni crea o vacia bases. Ante bloqueo revisar
el diagnostico y preservar datos; no borrar historial para hacer pasar las guardas.

Targets fijos: tests/test_eipd_test_runner.py, tests/test_api_eipd_admin.py y
tests/test_api_eipd_admin_concurrency.py. `pytest` directo no recibe la proteccion
del wrapper: no usarlo contra la base operacional. Para otra suite/head, revisar
primero alcance y guardas. Resultado §123: 60 aprobadas.

## §124 — resultados del ensayo aislado

El ejecutor incluye tests/test_eipd_channel_lifecycle.py; resultado total 63 aprobadas.
ALTER PASSWORD rechaza la credencial antigua solo en nuevas conexiones; NOLOGIN
impide nuevas conexiones sin terminar las existentes. La guarda de cada solicitud
rechaza rol NOLOGIN o membresia retirada. Restaurar flags/membresia o sustituir la
credencial y renovar el pool recupera el canal de pruebas; no habilita activacion.

Para una rotacion real: preparar la credencial y recuperacion fuera del repositorio,
drenar solicitudes y cerrar conexiones, aplicar el cambio, inyectarlo en nuevos
procesos, verificar rechazo de clave anterior con conexion nueva y ejecutar preflight
mas comprobacion personal. No asumir revocacion instantanea de una solicitud ya
autorizada. Mantener publicaciones/eventos y verificar snapshot antes/despues.
Ese cambio real no se ejecuto en §124; el canal actual sigue intacto en revision 1.

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
