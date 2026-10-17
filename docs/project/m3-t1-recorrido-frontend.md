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
