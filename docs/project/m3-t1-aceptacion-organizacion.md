# Aceptacion documental por organizacion — contrato operativo

Implementado el 16/10/2026, sobre el modelo juridico V2 conservado sin cambios.
Alcance: documentos sucesores EIPD con infancia, por organizacion/tratamiento/
evaluacion/version. No equivale a adopcion de todas las politicas de M3-T1.

## Permisos y registros

- Owner/admin puede otorgar o revocar facultad a un miembro owner/admin/editor
  del expediente. No tiene facultad implicita para aceptar, ni bypass global.
- Designacion exige referencia y evidencia; rol responsable/encargado por actividad.
  Encargado identifica al responsable por cuya cuenta actua. Es una declaracion
  de pruebas, no una verificacion de representacion real.
- Actor autenticado y facultado registra acepta/rechaza/requiere_cambios, fundamento
  y referencia del acta. Actor, organizacion, fecha UTC y hashes los fija el servidor.
- Solo ultima resolucion con contexto/material vigente. Un sucesor no hereda
  decisiones; cambios marcan historial obsoleto. Revocar conserva eventos anteriores.
- Historial append-only, FK RESTRICT, RLS por tenant, UPDATE/DELETE/TRUNCATE
  denegados a app_user. Revision de facultad usa CAS y lock de serie; aceptar y
  revocar comparten serie. Aceptar respeta orden selector global -> serie.

API bajo `/licitud/treatments/{tid}/assessments/{aid}/organization-acceptance/v1`:
GET/POST `authority`; GET/POST `resolutions/{rid}/events`. Designar requiere
manage_members; decidir edit_content; leer view. Ambas escrituras solo en
entorno development/test con opt-in EIPD_CHILD_TEST_WRITES_ENABLED y data_kind
ficticios. Respuestas siempre authorizes_action=false y can_confirm=false.
La aceptacion no publica/selecciona politica global ni confirma/activa EIPD.

## Prueba manual opcional con datos ficticios

En un proceso exclusivo de pruebas, abrir editor infancia del expediente,
seleccionar una resolucion guardada y su panel de aceptacion. Declarar datos
ficticios; registrar facultad y evidencia de prueba para miembro autorizado;
registrar decision y consultar historial. Revocar facultad: nuevos registros se
rechazan y el historial se conserva. Crear sucesor: no hereda la decision anterior.
No cambiar el opt-in del entorno operativo para repetir pruebas automaticas.

## Evidencia local

65 pruebas backend enfocadas: API, actor/tenant, CAS, orden concurrente aceptar/
revocar, perdida de rol, contexto obsoleto, FK e inmutabilidad, downgrade protegido.
41 Chromium UI/cliente: historial/editor y aceptacion; formularios conservados
ante rechazo, resultado incierto sin reintentos, doble envio, lectura sola y
contratos adulterados. Una integrada real valida grant/decision/historial contra
API/PostgreSQL app_user y conserva bloqueada EIPD. Tipos/lint/formato aprobados.
Ejecutores desde backend, con Node disponible para integrada:
`python -m scripts.run_organization_acceptance_tests` y
`python -m scripts.run_eipd_browser_test`; verifican destino aislado fijo.

Migracion append-only d16a3b7c8e52 aplicada a base aislada y desarrollo local.
Nueve tablas previas conservan conteos/checksums; tablas nuevas vacias en desarrollo.
Opt-in operativo false, politica infancia V1 intacta. CI/publicacion se verifica
contra HEAD, no por conteos historicos.

## Pendientes para MVP

Verificacion humana de fuentes y suficiencia juridica, facultades y evidencias
reales de organizacion piloto; extender adopcion a otras politicas/documentos si
se acuerda. Datos reales requieren migracion y controles propios. Gates MVP y
levantamiento EIPD son decisiones separadas; ninguno se cierra con actas ficticias.
