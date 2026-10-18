# Bases de licitud: entrada y borradores desde el frontend

Bloque 17/10/2026, datos ficticios, EIPD bloqueada. No publica el MVP para datos
reales ni convierte completitud documental en aceptacion juridica.

## Recorrido

`/dashboard` enlaza `/dashboard/licitud`. Sesion obligatoria, organizaciones de
la cuenta, selector de tratamiento RAT. Si no hay organizacion, enlaza a su
creacion. El inventario sigue gestionando finalidades/categorias/titulares.
Elegir finalidad y alcance y declarar uso ficticio permite crear un borrador.
Base y fundamento pueden quedar pendientes. Historial de versiones por tratamiento
con paginas de 50 y enlaces que conservan organizationId.

El expediente existente agrega fundamento/base propuesta y nueve analisis
principales de LIA. Conserva secciones y campos anteriores no representados;
cambiar base no elimina documentacion guardada. No implementa el cuestionario
completo de cada base ni certifica completitud de LIA. Infancia, resoluciones,
revisiones, facultades y dossier siguen en sus paneles existentes. Confirmados,
reemplazados y viewers en solo lectura. Sin boton de confirmar/activar EIPD.

API nueva GET `/licitud/treatments/{id}/assessments`: indice de metadatos,
no documentos completos; offset no negativo y limit 1..100, orden estable.
Exige suscripcion/permiso de lectura, comprueba tratamiento del tenant y filtra
ambos IDs con app_user/RLS. Sin migraciones ni cambios de politica.

## Validacion

Cinco pruebas Chromium de componentes con API simulada: crear/guardar/reabrir,
viewer, rechazo conserva formulario, preservacion de campos LIA e historial
confirmado de solo lectura. Tipos y lint frontend aprobados antes de cierre.
Guion local fijo: desde backend `python -m scripts.run_licitud_workspace_tests`.
Valida destino de pruebas existente antes de iniciar API/Chromium/PostgreSQL.
La integrada usa perfil/claim sintetico; no acredita login externo real.
Comprueba en DB que el registro queda borrador, LIA persiste y confirmed_at null.
Listado API con aislamiento, validacion de paginado y permisos de viewer.
Integrada nueva incorporada al ejecutor CI existente; cinco casos UI al comando
frontend existente. El recorrido con cuenta real de pruebas lo ejecuta el usuario.

Estado de cierre: cinco UI, tres API y dos integradas Chromium/API/PostgreSQL
aprobadas. Docker/WSL restablecido por el usuario tras interrupcion; tipos,
lint/formato aprobados. CI previa bea0006 success; verificar candidato por HEAD.
Sin migraciones, merge ni despliegue. No certifica MVP ni datos reales.

Prueba manual: entrar al panel -> Bases de licitud, seleccionar organizacion
ficticia y tratamiento RAT con finalidades/categorias/titulares completos. Crear
borrador, abrir enlace, guardar fundamento/LIA y volver al listado para reabrir.
Tras editar fundamentos recargar el expediente antes de consultar diagnósticos y
vinculos de los paneles inferiores. Repetir con clientes, trabajadores e infancia;
para esta ultima usar los paneles existentes cuando corresponda. Registrar errores
sin copiar credenciales ni datos personales. La cuenta/sesion y flujo de paginas
Next completos quedan para esta prueba asistida del usuario.

## Cierre de prueba manual asistida — 18/10/2026

Base funcional verificada: `33039d37d79ebce9c332473025b0eabf8236d641`.
CI GitHub Actions 39040075836 success y Handoff 39040075894/39040072718
success, consultadas por HEAD exacto el 18/10. Este cierre solo modifica documentos;
no atribuye al futuro commit documental una CI que corresponde a la base funcional.

El usuario ejecuto el recorrido en Next con su sesion de pruebas; Codex reviso
capturas y los JSON descargados. Clientes: borrador y edicion/reapertura LIA.
Trabajadores: fundamento pendiente, segunda edicion persistida y dossier.
Infancia: RAT corregido a incluye ninos, sin adolescentes ni sensibles; fuente
sintetica descrita; documento guardado/reabierto y segunda edicion limitada a cinco
participantes sinteticos. Dos resoluciones conservadas, revisiones negativas
requiere_cambios y no_continuar asociadas a sus respectivas versiones.

En resolucion 2 se registro una decision documental requiere_cambios, conservada
tras recarga; facultad ficticia otorgada (revision 1) y revocada (revision 2).
La decision anterior sigue visible; facultad actual no disponible y selector de
nueva decision bloqueado incluso tras recargar. Esto acredita el bloqueo UI;
no se envio una peticion HTTP manual forzada. El rechazo servidor tras revocacion
esta cubierto por la prueba automatizada test_revision_cas_concurrency_and_revoke
(y concurrencia de aceptacion/revocacion), incluida en la CI funcional aprobada.

JSON final generado 2026-10-18T20:33:17.260919Z, SHA de paquete declarado
`ede07544652b88163bc76e545c30d3ff3eb59545974e163ce0afcec99f4cfd79`:
resolucion 2 / PRUEBA-2, exactamente un evento documental requiere_cambios,
material coincide, faculty_current=false. Borrador, confirmed_at=null,
activation=deshabilitada; can_confirm, authorizes_action, allows_real_data y
mvp_ready=false. Revisado contenido; no recalculo independiente del hash.
El dossier exporta la ultima resolucion y sus decisiones; no el historial completo
de facultades ni las revisiones negativas. Esos historiales se observaron en UI.
No se copian a Git cuentas, identificadores personales ni el expediente completo.

Tras la prueba se restauro backend local con Compose base, sin override temporal:
verificado environment=development y eipd_child_test_writes_enabled=False.
Override privado retirado. No cambio .env, migraciones, politica global ni datos
historicos. La exportacion final confirma bloqueo EIPD y datos reales.

Sin pruebas pendientes para este recorrido ficticio acotado. Hallazgos pendientes
en backlog: estado de guardado, controles poco visibles, coherencia RAT/infancia
y criterio de completitud de fuentes. No son corregidos por este cierre.
No acredita MVP para produccion: siguen pendientes organizacion/evidencia
juridica autenticas, revision de aplicabilidad, controles operativos externos y
una decision independiente para datos reales o activacion EIPD. Sin merge/despliegue.
