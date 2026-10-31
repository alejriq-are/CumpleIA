# Handoff vigente de CumpleIA

## Paso 3 — aceptación asistida y publicación autorizada, 31/10/2026

El usuario confirmó «Recorrido OK» para Consultar anexo desde una valoración asociada al documento actual, tras aceptar la consulta histórica y los ajustes de nombres y títulos. Queda aceptado LIC-UX-013 en este alcance: consulta de relaciones guardadas y navegación a la ficha del anexo correspondiente. La evidencia asistida es el resultado comunicado por el usuario; no equivale a auditoría jurídica ni verificación real de controles.

Verificación técnica previa: 83 pruebas Chromium aprobadas con respuestas controladas; tipos, ESLint, formato y diferencias aprobados. La prueba manual con lector de pantalla sigue pendiente. Se mantienen separadas las valoraciones históricas y las relaciones del documento actual; no cambia el cálculo, API ni permisos. Confirmación y activación EIPD permanecen bloqueadas.

Commit y push autorizados en `feature/riesgos-medidas-evidencias`; sin merge ni despliegue. Se excluyen `frontend/next-env.d.ts` y `outputs/` preexistentes. Las notas inferiores sobre aceptación o autorización pendiente quedan superadas para este alcance.

## Paso 3 — LIC-UX-013: detalle relacionado preparado, 31/10/2026

Ajuste solicitado tras el recorrido de anexos históricos reportado OK: los rótulos identifican el contenido EIPD guardado, la valoración EIPD y sus anexos de respaldo; infancia conserva su denominación específica. En la consulta guardada, títulos principales de 20 px, subtítulos de 18 px y encabezados de riesgo de 16 px, todos seminegrita. Verificación del ajuste: tipos, ESLint y formato aprobados; 83 pruebas Chromium de valoración/anexos, consulta integrada e historial de infancia aprobadas con respuestas controladas. Pendiente revisión visual del usuario; sin cambios en datos o relaciones históricas.

Rama `feature/riesgos-medidas-evidencias`, base `15239c6` (Paso 2 publicado). Implementación local de consulta por riesgo en Documentos guardados → Consultar valoración y anexos: niveles residuales previsto/actual, fundamentos, medidas asociadas, estado/eficacia y referencias de verificación, evidencias declaradas y anexos explícitamente vinculados. Los accesos a anexos llevan a su ficha/versionado y colocan el foco; la descarga mantiene su comprobación existente.

Usa valoración y documento guardados; no incorpora ediciones pendientes. Ante valoración histórica muestra sus niveles/fundamentos sin unir medidas ni anexos del documento actual. Sin valoración guardada conserva el aviso existente. No cambia cálculo, API, permisos, persistencia ni activación EIPD. Un vínculo no acredita eficacia ni aprobación.

Evidencia local: tipos, ESLint y Prettier aprobados; 22 pruebas Chromium del panel aprobadas con respuestas controladas. Los tres casos nuevos comprueban relaciones explícitas, exclusión de anexos ajenos, versión/destino/foco, teclado, ancho 320/1280, lectura de valoración histórica, ausencia de escrituras y conservación/separación del control pendiente. No acredita todavía una prueba asistida con relaciones reales del servidor ni lector de pantalla.

Validación asistida pendiente: en `/dashboard/trabajo`, elegir una evaluación ficticia con valoración guardada y medidas/anexos relacionados; abrir Documentos guardados → Consultar valoración y anexos. Localizar «Medidas y respaldos del riesgo residual», desplegar un riesgo y contrastar sus medidas/referencias con el documento guardado. Pulsar Consultar anexo y comprobar referencia/versión/foco. Comprobar texto pendiente conservado al volver al editor, teclado y ventana estrecha. Si falta valoración o vínculos, registrar ese estado sin inventar relaciones ni crear registros solo para comprobar el diseño.

Sin commit/push nuevo, merge ni despliegue. Excluir `frontend/next-env.d.ts` y `outputs/` preexistentes. LIC-UX-013 queda pendiente de aceptación asistida, no cerrado por la prueba automatizada.

## Paso 2 — aceptación asistida y publicación autorizada

El usuario confirmó los recorridos principales y complementarios del alcance mixto y autorizó commit/push. Quedan aceptados: acceso y retorno a la misma evaluación desde RAT; etiquetas coherentes y orden común en comparación; adopción explícita con motivo; revisión independiente de EIPD/infancia; conservación de borradores, antecedentes y alcance guardado; ventana estrecha, cierre/foco; retirada/restauración de aplicabilidad; cambio del RAT posterior a comparar; error de conexión y recuperación; consulta desde otra pestaña con pendientes independientes. Evidencia asistida reportada por el usuario en este chat; no equivale a auditoría completa ni prueba manual con lector de pantalla.

Rama `feature/alcance-mixto-guiado`, base `8d2cc88`. Publicación del Paso 2 autorizada; sin merge ni despliegue. Confirmación y activación EIPD siguen bloqueadas. Se excluyen los cambios preexistentes de `frontend/next-env.d.ts` y `outputs/`. Contrato y límites: [alcance mixto guiado](project/alcance-mixto-guiado.md). Las notas inferiores sobre validación o autorización pendiente quedan superadas para el alcance aceptado.

## Paso 2 — alcance mixto guiado: implementación local, 30/10/2026

NAV-UX-005 implementado localmente en `feature/alcance-mixto-guiado`; aceptación asistida pendiente. Permite revisar RAT, regresar a la misma evaluación, comparar y adoptar el alcance con motivo y trazabilidad, conservando borradores y antecedentes. Las determinaciones anteriores requieren revisión para el nuevo alcance; EIPD e infancia siguen independientes.

Evidencia: suite aislada EIPD 1.148 aprobadas; ampliación focalizada alcance/anexos 9 aprobadas (con solapamiento); navegador conectado 135 aprobadas con respuestas controladas. Migración `a84f6e2c9103` aplicada en base aislada y desarrollo local verificado. Sin commit/push de este paso, merge ni despliegue; EIPD bloqueada. Contrato, límites y checklist: [alcance mixto guiado](project/alcance-mixto-guiado.md).

## Paso 1 — validación asistida y publicación autorizada, 30/10/2026

El usuario confirmó «recorrido OK» tras el ajuste de Espacio en «Vínculos opcionales con riesgos y medidas» y autorizó commit/push. Quedan aceptados el recorrido de archivo inválido → archivo válido con conservación de campos y la apertura/cierre del bloque con teclado. Las notas anteriores de aceptación/autorización pendiente quedan superadas en este alcance.

Verificación técnica: 42 pruebas Chromium aprobadas en assessment-support y licitud-workspace con respuestas controladas y estilos de la aplicación; tipos y ESLint aprobados. LIC-UX-014 queda resuelto en este alcance. LIC-UX-015 conserva pendientes fuera de los dos desplegables del panel. La validación manual con lector de pantalla continúa pendiente; no se atribuye una subida real nueva de anexo a estas pruebas.

Se publica en `feature/anexos-estado-acciones`. Sin merge ni despliegue; confirmación/activación EIPD bloqueadas. Se excluyen los cambios preexistentes de `frontend/next-env.d.ts` y `outputs/`.

## Paso 1 — anexos y acciones: implementación local, 29/10/2026

Usuario autoriza continuar Paso 1 tras el cierre 13. Rama `feature/anexos-estado-acciones`, base `205f4c9b92ae700bc99efed1447f44d74624ef58`.

LIC-UX-014 implementado localmente: Guardar anexo se deshabilita ante formato no admitido, archivo vacío o mayor de 2 MiB. El motivo queda una sola vez junto al selector, asociado mediante descripción accesible y aviso; junto a Guardar se explica qué corregir sin duplicar el error. Sustituir o quitar el archivo actualiza el estado y conserva los demás campos y la declaración ficticia. La validación del cliente API y del servidor se mantiene; un rechazo de envío conserva foco/aviso y no anuncia éxito.

LIC-UX-015 parcial y acotado al panel de valoración/anexos: metodología y vínculos opcionales usan el patrón compartido de desplegable reconocible con fondo suave, borde y foco. Se corrigió el ancho mínimo del formulario de anexos tras detectar desborde a 320 px. No se declara una auditoría transversal de todos los accesos.

Validación local: 42 pruebas Chromium aprobadas en assessment-support y licitud-workspace, con respuestas controladas; incluye CSV, vacío, sobredimensionado, corrección, conservación de referencia/descripción/sección/vínculos/declaración, retiro de archivo, rechazo de servidor, teclado y anchos 1280/390/320. Inspección visual de captura a 320 px aprobada. No acredita una nueva prueba contra API real ni lector de pantalla manual. Tipos, ESLint, Prettier y diferencias verificados. Una primera ejecución detectó desborde a 320 px; corregido antes de la ejecución final aprobada.

Pendiente: recorrido asistido en `/dashboard/trabajo` → Preparar → Anexos de respaldo: (1) completar metadatos ficticios y elegir CSV, comprobar único error y Guardar bloqueado; (2) reemplazar por TXT válido y confirmar conservación/habilitación según declaración; (3) quitar selección o probar vacío/mayor de 2 MiB, comprobar motivo; (4) abrir/cerrar vínculos con teclado y revisar ventana estrecha. No guardar un anexo nuevo solo para probar presentación. LIC-UX-014 pendiente aceptación asistida; LIC-UX-015 sigue abierto fuera de este panel.

Sin cambios de API, límites, persistencia ni permisos; EIPD bloqueada. No se ejecuta commit/push de este Paso 1 sin autorización específica. Se preservan `frontend/next-env.d.ts` y `outputs/` preexistentes.

## 13 — cierre y publicación autorizados, 29/10/2026

El usuario autoriza commit y push de la documentación del bloque 13 tras los recorridos asistidos aprobados en el alcance del checklist. Se publican guía de tareas, glosario, ciclo documental y resultados con sus límites. La autorización no acredita lectura completa de las guías ni una nueva ejecución de toda la batería.

Se conservan el backlog funcional y la prueba manual con lector de pantalla pendiente. Sesión real conserva evidencia de 12B. Sin cambios de interfaz, merge ni despliegue. Las notas anteriores de autorización pendiente son antecedentes históricos superados por esta autorización.

## 13 — recorridos asistidos consolidados, 29/10/2026

Rama `feature/navegacion-13-guia-cierre`, base funcional publicada `41c561b`.
Guía, glosario G01–G30, ciclo documental e identidades y checklist único preparados.
Usuario aprueba los recorridos realizados: conservación y retorno EIPD, vista
previa/consulta/guardado, aplicabilidad y disponibilidad, consulta de infancia,
revisión frente a decisión con facultad revocada, copia/previsualización sin
registro y cancelación de reemplazo, paneles/teclado/zoom 200 %, recuperación de
red y ámbitos de módulos con localización del formulario de anexos.

Límites: sesión real conserva aceptación anterior de 12B, sin repetirla en 13;
no se registraron nuevas actuaciones de infancia ni se cargaron anexos en este
cierre. Lector manual pendiente; backlog funcional preservado. La lectura final
de las guías y autorización específica de commit/push de 13 quedan pendientes.
No se modifica interfaz ni contratos en 13. Excluir `frontend/next-env.d.ts` y
`outputs/` preexistentes; sin merge ni despliegue. Las entradas anteriores de
13 pendiente de recorridos describen el avance histórico, superado por esta nota.

## 13 — guía y cierre documental preparados, 29/10/2026

Rama `feature/navegacion-13-guia-cierre`, base publicada y verificada
`41c561b78e7b4d96994d927b86422d7d9efed5d1` (12B).
Se incorporan guía de tareas, glosario G01–G30, mapa de identidades y actualización
del ciclo documental, con checklist único de ocho recorridos y remanentes.
El bloque 13 modifica documentación; no cambia formularios ni contratos.

La validación asistida integral de 13 sigue **No probado**; comenzar con 13-01/13-02.
No repetir guardados por localizar un editor que ya está habilitado. La evidencia
anterior conserva sus límites: 185 pruebas aprobadas y una omitida en regresión
12B, más dos comprobaciones dirigidas del ajuste posterior, sin sumarlas como
escenarios únicos. Sesión real y recuperación aceptadas por el usuario en 12B.
Lector de pantalla manual, formularios completos consentimiento/LIA y circuito
formal EIPD general continúan pendientes. Confirmación/activación EIPD bloqueadas.

Guía: [guia-navegacion-trabajo.md](project/guia-navegacion-trabajo.md).
Aceptación/remanentes: [cierre-navegacion-checklist.md](project/cierre-navegacion-checklist.md).
Las notas anteriores de no inicio de 13 o publicación pendiente de 12B son
históricas: 12B ya está publicado en `41c561b`. Este bloque 13 aún no tiene
commit/push autorizado. Excluir `frontend/next-env.d.ts` y `outputs/` preexistentes.
Sin merge, despliegue ni cierre implícito de los pendientes funcionales.

## 12B — cierre y publicación autorizados, 29/10/2026

El usuario autoriza commit y push del bloque 12B validado en
`feature/navegacion-12b-recuperacion`. Se publica la clasificación de errores,
recuperación de consultas/contextos y sesión, corrección del aviso vacío,
pruebas y aceptación asistida. Se conserva la evidencia de comprobaciones ya
aprobadas; no se repite la batería para el cierre documental.
Las menciones anteriores a publicación pendiente son antecedentes históricos.
Excluir `frontend/next-env.d.ts` generado y `outputs/`. Sin inicio de lote 13,
merge ni despliegue. Verificar el commit publicado contra la rama remota.

## 12B — validación asistida completada, 29/10/2026

El usuario confirma recorrido OK de recuperación de aplicabilidad tras desconexión,
del selector de contextos tras restablecer la red y de autenticación real.
La captura de sesión ausente muestra el mensaje específico y el acceso a iniciar
sesión en otra pestaña, conservando `[FICTICIA] Prueba recuperación 12B` en el
formulario original. El usuario confirma que, tras iniciar sesión con la misma
cuenta y reintentar en la pestaña original sin recargar, la consulta se recupera
y el texto pendiente permanece sin guardar. Se completa la aceptación asistida de 12B.

Durante la prueba del selector se corrigió el aviso contradictorio de lista vacía:
no se anuncia ausencia de evaluaciones cuando falla la consulta. Dos pruebas
dirigidas adicionales aprobadas después del ajuste; la regresión previa obtuvo
185 aprobadas y una captura visual opcional omitida. Controles estáticos aprobados.
Las menciones anteriores a autenticación real o validación asistida pendientes
son antecedentes históricos. La prueba manual con lector de pantalla sigue pendiente.

Implementación y validación de 12B completadas; pendiente commit y push, sin
autorización nueva para publicarlos. No se inicia lote 13, merge ni despliegue.
Excluir `frontend/next-env.d.ts` generado y `outputs/` de una eventual publicación.

### 12B — comprobación asistida de conexión y ajuste del selector

El usuario confirma recuperación de la consulta de aplicabilidad al restablecer
la conexión, conservando el texto pendiente. La captura de la pestaña actualizada
confirma error de conexión en español, reintento de contextos y Aplicar bloqueado.
Se detecta y corrige un aviso contradictorio: la lista vacía solo se anuncia cuando
la lectura termina sin errores. Dos pruebas dirigidas verifican que no aparezca
ese aviso ante fallo de sesión o red y que se conserve el borrador al reintentar.
Pendiente confirmación asistida de recuperación del selector y prueba de sesión real.

## 12B — recuperación de consultas y sesión, 29/10/2026

Rama `feature/navegacion-12b-recuperacion`, base publicada `ff85ec7`.
Implementación terminada; validación asistida pendiente. Sin commit ni push de 12B.
Las entradas anteriores «Sin inicio de 12B» describen el cierre histórico de 12A.

Se confirmó que el acceso compartido de licitud confundía cualquier error del
proveedor de sesión con una sesión expirada. Ahora distingue sesión ausente o
respuesta 401, fallo de conexión, servicio de acceso no disponible y otros errores
HTTP, incluidos 403 y 503. Un error no habilita el editor condicionado.
La recuperación se ofrece en las consultas de aplicabilidad, apertura de destinos
y selector de contexto. El reintento de apertura vuelve a consultar aplicabilidad.
El selector conserva su selección y permite reintentar su lectura sin aplicar contexto.

Solo cuando falta una sesión válida se ofrece «Iniciar sesión en otra pestaña».
La ayuda pide conservar la pestaña original y regresar a reintentar: la nueva
pestaña no recupera sus notas sin guardar. Consultar y reintentar no guardan datos,
no cambian permisos ni confirman o activan EIPD. Los borradores siguen siendo
memoria de la pestaña; recargar puede perderlos.

Verificación dirigida: ocho escenarios automatizados aprobados, con ausencia de
sesión, fallo de red, fallo del proveedor y HTTP 401/403/503; incluye recuperación
del selector de contexto. Comprueban conservación de notas, ausencia de escrituras
HTTP y de mensajes falsos de guardado. TypeScript, ESLint y formato aprobados.
Regresión final: 185 pruebas aprobadas y una omitida (captura visual opcional),
en navegación conectada, maqueta y espacio de licitud.
Inspección visual de recuperación en ventana de 390 px sin desbordamiento horizontal.
La restauración de sesión fue simulada: queda pendiente comprobar conjuntamente
el proveedor real tras iniciar sesión. No se ejecutó un inicio de sesión real ni
se almacenaron o imprimieron credenciales. Lector de pantalla manual sigue pendiente.

### Recorrido asistido para reanudar 12B

1. En `/dashboard/trabajo`, abrir Bases de licitud → Determinar aplicabilidad.
2. Añadir `[FICTICIA] Prueba recuperación 12B` al fundamento, sin guardar.
3. En Red del navegador seleccionar Offline; no recargar la página.
4. Pulsar Consultar última determinación guardada. Debe explicar un fallo de conexión,
   conservar el texto y no indicar sesión expirada ni guardado correcto.
5. Restablecer No throttling y repetir la consulta: debe recuperar la lectura y
   conservar el fundamento sin guardarlo.
6. Después validar por separado sesión ausente/401 y recuperación tras autenticación,
   conservando la pestaña original; registrar el resultado real, sin confundirlo
   con las pruebas simuladas. Comprobar también el reintento del selector de contexto.

Excluir `frontend/next-env.d.ts` generado y `outputs/` de una eventual publicación.
No se inicia lote 13, merge ni despliegue.

## 12A — cierre y publicación autorizados, 29/10/2026

El usuario autoriza commit y push del bloque 12A validado, en
`feature/navegacion-12a-recorridos`. Se incluyen las correcciones de progreso,
avisos locales e historial, sus pruebas y la aceptación asistida registrada.
Se conserva la evidencia de pruebas existente; no se repite la batería por este
cierre documental. Excluir `frontend/next-env.d.ts` generado y `outputs/`.
Sin inicio de 12B, merge ni despliegue. Las notas anteriores de publicación
pendiente son antecedentes; el resultado del push se verifica contra la rama remota.

## 12A — validación asistida completada, 29/10/2026

El usuario confirma recorrido OK del avance del autodiagnóstico, los avisos locales
de Próximamente y el retorno mediante Atrás/Adelante entre pasos EIPD, conservando
la nota sin guardar al volver a Describir riesgos. Se completa la validación asistida
del bloque 12A; se conserva la evidencia automatizada registrada en la entrada anterior.

Aclaración comprobada durante el recorrido: N/A es una respuesta válida y aumenta
el avance. Siguiente permanece deshabilitado mientras queden preguntas pendientes
en la sección; para visitar otra sección sin completarla se utiliza Cuestionario.
No se atribuye el bloqueo a N/A ni se cambia esta regla de navegación.

Implementación y validación de 12A completadas, pendiente de commit y push.
Sin inicio de 12B, merge ni despliegue. La comprobación manual con lector de pantalla
continúa pendiente. Excluir `frontend/next-env.d.ts` generado y `outputs/`.
Las menciones anteriores a validación asistida pendiente son antecedentes históricos.

## 12A — implementación y pruebas automáticas, 29/10/2026

Rama `feature/navegacion-12a-recorridos`, base publicada `22f8c74`.
Se corrigieron dos fallos reproducidos: respuestas ajenas al catálogo o con opciones
inválidas podían incrementar el avance; Atrás/Adelante disparaba dos consultas del
mismo tratamiento al recibir popstate y hashchange para un destino.
El avance cuenta solo respuestas válidas del catálogo activo, incluidas N/A;
visitar secciones no aumenta el avance ni demuestra guardado o cumplimiento.
Se conserva el historial por pasos y los borradores. Cambiar pasos EIPD no consulta
ni escribe; restaurar un destino realiza una validación por contexto.
Los avisos de Próximamente se muestran junto al control o tarjeta activados.
En el menú reducido a iconos el aviso dispone de ancho propio para ser legible.
Describir riesgos y Valorar riesgos se conservan: corresponden a tareas y campos distintos.

Evidencia: 152 pruebas de regresión aprobadas y una captura opcional omitida;
siete casos dirigidos 12A aprobados, incluidos los diez apartados y las 50 preguntas
del catálogo JSON de referencia del repositorio, mediante respuestas simuladas.
Esto no acredita el contenido de la base de datos de la sesión del usuario.
TypeScript, ESLint, formato y diff comprobados. Capturas revisadas a 390 y 865 px;
los casos automatizados también cubren 1280 px. Sin cambios de API, puntuación,
permisos ni habilitación de confirmación/activación EIPD.

Pendiente validación asistida: avance sin responder y con N/A; aviso local de
Próximamente en escritorio/ventana estrecha; Atrás/Adelante conservando notas.
No se declara cerrado 12A. Sin commit/push de este bloque ni inicio de 12B.
Excluir `frontend/next-env.d.ts` generado y `outputs/`. La prueba manual con lector
de pantalla sigue pendiente. Las entradas anteriores son antecedentes históricos.

## 11B — cierre y publicación autorizados, 29/10/2026

El usuario autoriza commit y push del bloque 11B y de la corrección RAT pendiente.
RAT quedó separado en `a25d20f91c06b00bb897dd33d60f1257adfa6b07`, rama
`fix/rat-aviso-guardado`. 11B se publica desde
`feature/navegacion-11b-seleccion-creacion`, que incluye ese commit como antecedente.
Recorrido asistido completado en escritorio y ventana estrecha; 141 pruebas automáticas,
TypeScript, ESLint, Prettier y diff aprobados. No se repite la batería por este cierre
documental. Las notas inferiores de publicación pendiente son antecedentes.
Sin inicio de 12A, merge ni despliegue. El lector de pantalla manual continúa pendiente.
Se excluyen `frontend/next-env.d.ts` generado y `outputs/`.

## Corrección RAT — publicación autorizada, 29/10/2026

El usuario autoriza commit y push de la corrección pendiente del aviso RAT. Se publica
por separado de 11B en `fix/rat-aviso-guardado`. Recorrido asistido confirmado OK;
TypeScript, ESLint, formato y diff aprobados. Sin cambios de guardado, API ni permisos.
Las menciones anteriores a autorización pendiente son antecedentes.

## 11B — validación asistida completada, 29/10/2026

El usuario confirma «recorrido OK» también en ventana estrecha: Cancelar creación y
Volver a preparar evaluación se leen y pueden activarse; se conservan el fundamento
y el contexto al cancelar y retomar la preparación, sin recargar ni crear otro borrador.
Con las comprobaciones anteriores, queda completado el recorrido asistido de 11B.
Se mantiene la evidencia automatizada de 141 pruebas aprobadas, TypeScript, ESLint,
Prettier y revisión del diff. No se afirma validación con lector de pantalla ni creación
real de una evaluación en estas pruebas asistidas.

Bloque 11B validado, pendiente de commit/push. Sin inicio de 12A. La corrección del
aviso RAT validada se mantiene como cambio separado pendiente de publicación.
Las entradas anteriores sobre validación pendiente son antecedentes. Excluir
`frontend/next-env.d.ts` generado y `outputs/`.

## 11B — selección y cancelación validadas por el usuario, 29/10/2026

El usuario confirma «recorrido OK» al distinguir el contexto de «Trabajando en…»
del formulario de creación, comprobar el tratamiento propuesto y la elección explícita
de finalidad/categorías/titulares. Confirma que Cancelar creación y Volver a preparar
conservan el fundamento de prueba y el contexto del programa con menores. La captura
del selector muestra «Elegir trabajo existente» y que aplicar contexto no crea una
evaluación; tras cancelar ese panel, el usuario confirma conservación del fundamento
y del contexto. Estas comprobaciones no registraron una evaluación nueva.

Pendiente: recorrido asistido equivalente en ventana estrecha. Se mantiene la evidencia
automatizada de 141 pruebas aprobadas y comprobaciones estáticas anteriores. Sin
commit/push de 11B ni inicio de 12A. La corrección RAT permanece como cambio separado.

## 11B — selección y creación diferenciadas; validación asistida pendiente, 29/10/2026

Rama `feature/navegacion-11b-seleccion-creacion`, base publicada 11A
`022d15c35e1a4028c9487108dedc860e0f9ee099`. El selector explica que abre trabajo
existente. Evaluaciones y creación de borrador distingue «Trabajando en…» del
tratamiento para crear un registro nuevo. Solo se propone el ID del tratamiento si
figura en el inventario autorizado; no se copian finalidad ni alcance de una evaluación,
pues pueden conservar un alcance anterior al RAT actual. Se comprueba la identidad
del tratamiento consultado. Cancelar creación oculta la preparación conservando sus
campos durante esta visita; volver a preparar los recupera. Cancelar no escribe ni cambia
el contexto. Crear conserva su acción explícita y explica dónde abrir el resultado.

Verificación: TypeScript, ESLint y Prettier aprobados. 141 pruebas aprobadas: 118 de
navegación conectada y 23 del workspace, incluidas dos nuevas sobre precarga por ID
autorizado y cancelación sin escritura con conservación de campos. La batería cubre
permisos, conflictos y pendientes entre contextos. Falta validación asistida del usuario;
no se certifica lector de pantalla. Sin cambios de API, permisos ni metodología;
confirmación y activación EIPD bloqueadas. Sin commit/push de 11B ni inicio de 12A.

La corrección RAT validada permanece en el árbol de trabajo como cambio separado,
pendiente de publicación; las entradas anteriores que indican «Sin inicio de 11B» son
antecedentes. Excluir `frontend/next-env.d.ts` generado y `outputs/`.

## Corrección RAT — recorrido asistido confirmado OK, 29/10/2026

El usuario confirma «recorrido OK» tras probar la reubicación de «Cambios guardados»
encima de «Guardar cambios» en Información general del RAT y el retiro del aviso al
volver a editar. Se conserva la evidencia estática registrada anteriormente (formato,
ESLint, TypeScript y diff). Rama `fix/rat-aviso-guardado`; corrección validada,
pendiente de commit y autorización de push. Sin inicio de 11B. Las notas anteriores
de validación pendiente son antecedentes.

## Corrección RAT — confirmación junto a Guardar cambios, 29/10/2026

Observación del usuario posterior al cierre de 11A: Información general del RAT mostraba
«Cambios guardados» antes del formulario, lejos de su acción. En
`fix/rat-aviso-guardado`, base publicada `022d15c35e1a4028c9487108dedc860e0f9ee099`,
se mueve el aviso inmediatamente encima del botón, dentro del bloque de Información
general. Se añade role=status. Se conserva el retiro del aviso al editar mediante update;
no se cambia guardado, permisos ni API. TypeScript, ESLint y formato aprobados;
diff revisado. Validación visual asistida pendiente: guardar una modificación ficticia,
comprobar proximidad y volver a editar para retirar la confirmación. No se crean pruebas
que reproduzcan este cambio de presentación. Sin commit/push de esta corrección ni
inicio de 11B. Excluir next-env.d.ts generado y outputs/.

## 11A — validación asistida completada y publicación autorizada, 29/10/2026

Usuario confirma diferencias entre referencia, nombre de edición y versión, vista previa
con ediciones pendientes y conservación del texto al navegar. Confirma recorrido final
de valoración, fundamentos y lectura en ventana estrecha. La captura actualizada muestra
las ayudas de horizonte temporal y antecedentes de frecuencia/exposición; la captura
anterior no mostraba esas ayudas y no se atribuye a ella su validación.

11A listo para commit/push expresamente autorizado por el usuario. Rama
`feature/navegacion-11a-ayudas`, base 10B `741f0423bd37db46cec1912e47a1a13ed68ac22b`.
Se conserva la evidencia automatizada anterior: 33 casos de soporte/editor de infancia y
21 del workspace aprobados tras el ajuste de proximidad del aviso; TypeScript, ESLint y
Prettier aprobados. Esta actualización es documental y no requiere repetir la batería.
Sin certificación con lector de pantalla (7B pendiente), cambios de servidor, merge,
despliegue ni inicio de 11B. Excluir `frontend/next-env.d.ts` generado y `outputs/`.
Las menciones inferiores a validación o autorización pendiente son antecedentes.

## 11A — ayudas localizadas implementadas; validación asistida pendiente, 29/10/2026

Rama `feature/navegacion-11a-ayudas`, base publicada 10B
`741f0423bd37db46cec1912e47a1a13ed68ac22b`. Se incorporan ayudas breves junto a
finalidad, operaciones, contexto, tecnologías, códigos del alcance y descripción/análisis
de riesgos; referencia manual y nombre de edición se distinguen de identidad/secuencia
del servidor. Valoración explica horizonte temporal, fundamentos y riesgo previo a
controles; sus ayudas se asocian mediante aria-describedby. Vista previa declara si
incluye ediciones pendientes y que no escribe. Guardar explica su objeto; el aviso
permanece junto a la acción y se retira al editar. Sin cambios a validaciones, contratos,
metodología ni permisos; confirmación/activación EIPD bloqueadas.

Pruebas: 33 escenarios de valoración/anexos y editor de infancia aprobados; tras corregir
la distancia entre ayuda y botón en móvil, los 21 escenarios del workspace aprobados.
Dos casos nuevos comprueban ayudas accesibles, vista previa sin escritura y retiro del
éxito al editar. TypeScript, ESLint y Prettier aprobados. No equivale a prueba con lector
de pantalla ni a validación asistida del usuario; lector manual de 7B pendiente.
Sin commit/push de 11A ni inicio de 11B. Excluir `frontend/next-env.d.ts` generado y `outputs/`.

## Publicación autorizada de 10B — 28/10/2026

Usuario solicita commit y autoriza push de feature/navegacion-10b-historial,
base 10A publicada e3dd155c4a454801efc2c36245afe4cd0b225d43. Incluye accesos internos,
identidad e historial por versión, origen de copia temporal, estilos de consultas y
preparación solicitados por el usuario, pruebas y guion asistido con límites documentados.
174 escenarios Chromium previos y ejecuciones dirigidas posteriores aprobadas según el
registro detallado; checks estáticos y capturas revisados. La última actualización es
documental: no se repite batería ni se atribuye CI remota. Excluir next-env.d.ts generado
y outputs/. Verificar identidad remota tras push. Sin merge, despliegue ni inicio de 11A.
Lector manual de 7B pendiente. Menciones anteriores a autorización pendiente son antecedentes.

## 10B — guion asistido completado, 28/10/2026

Usuario confirma recorrido final con teclado/ventana estrecha, sumado a revisión,
versiones, decisiones y estilos aceptados. Copia manual observada con protección de
preparación existente; origen de copia nueva y escenarios excepcionales mantienen
cobertura automatizada, sin atribuir prueba manual. Ver límites y evidencia en
navegacion-servidor.md. 10B listo para commit/push cuando se autorice; sin publicación
ni inicio de 11A. Lector manual de 7B pendiente. Entradas inferiores son antecedentes.

## 10B — preparar copia destacado, 28/10/2026

Usuario confirma recorrido y muestra confirmación para conservar/reemplazar preparación
existente. No se atribuye copia nueva ni aviso de origen visto en esa captura.
Preparar nueva versión a partir de esta recibe estilo azul suave aprobado; cuatro
pruebas dirigidas y checks estáticos correctos. Pendiente validación visual y recorrido
estrecho/teclado. Sin commit/push de 10B ni inicio de 11A; lector manual de 7B pendiente.
Ver navegacion-servidor.md. Entradas inferiores son antecedentes.

## 10B — decisiones e historial confirmados, 28/10/2026

Usuario confirma recorrido de decisión, historial y retorno. Capturas identifican versión
1 SIMULADA-PILOTO-INFANCIA-RES-001, sin decisiones registradas y facultad otorgada/revocada
en historial. Eventos de facultades no se presentan como decisiones del documento.
Pendiente copia temporal/origen y teclado/ventana estrecha. Sin commit/push de 10B
ni inicio de 11A; lector manual de 7B pendiente. Ver navegacion-servidor.md.
Entradas inferiores son antecedentes.

## 10B — diseño ampliado aceptado, 28/10/2026

Usuario confirma «OK nuevo diseño» de los accesos de consulta y actualización.
Recorrido de revisión y alternancia de versiones ya confirmados. Pendiente decisiones,
origen de preparación y teclado/ventana estrecha. Sin commit/push de 10B ni inicio de 11A.
Lector manual de 7B pendiente. Ver navegacion-servidor.md; entradas inferiores son antecedentes.

## 10B — versiones confirmadas y estilo de consultas ampliado, 28/10/2026

Usuario confirma alternancia de versiones y retorno. Solicita destacar consulta de
versiones, actualización de historial, valoración/anexos y equivalentes. Aplicado estilo
azul suave con borde, foco y estados deshabilitados; desplegables conservan marcador.
Cuatro pruebas dirigidas más 52 de componentes afectados aprobadas en ejecuciones
separadas; checks estáticos y capturas 320/1280 correctos. Pendiente validación visual
ampliada y restantes recorridos de 10B. Sin commit/push ni inicio de 11A.
Lector manual de 7B pendiente. Ver navegacion-servidor.md; entradas inferiores son antecedentes.

## 10B — diseño de accesos aceptado, 28/10/2026

Usuario confirma «Ok el nuevo diseño». Ajuste visual aceptado; primer recorrido de
revisión/historial y retorno ya confirmado. Pendiente alternar versiones y restantes
recorridos asistidos. Sin commit/push de 10B ni inicio de 11A. Lector manual de 7B pendiente.
Ver evidencia en navegacion-servidor.md. Entradas inferiores son antecedentes.

## 10B — primer recorrido OK y mejora visual aplicada, 28/10/2026

Usuario confirma acceso a revisión/historial y retorno; pide distinguir los botones.
Se destacan seis accesos internos con fondo azul suave, texto oscuro, borde y foco.
Cuatro pruebas dirigidas posteriores y checks estáticos aprobados; capturas 320/1280
inspeccionadas. Pendiente confirmación visual y restantes recorridos asistidos.
Sin commit/push de 10B ni inicio de 11A. Ver detalle en navegacion-servidor.md.
Lector manual de 7B pendiente. Entradas inferiores son antecedentes.

## Bloque 10B implementado localmente — 28/10/2026

Rama feature/navegacion-10b-historial, base 10A publicada e3dd155. Accesos internos
con foco bajo cabecera a revisión, decisiones e historial; número/referencia/fecha
y conceptos de cada antecedente. Origen de copia temporal explícito; selección,
formularios y contratos existentes conservados. Sin rutas nuevas ni habilitación EIPD.
174 escenarios Chromium aprobados; ajuste final de identidad validado con 18 dirigidos
y un integrado de tres anchos. Tipos/lint/formato y capturas 320/1280 aprobados.
Guion asistido pendiente en docs/project/navegacion-servidor.md. Sin commit/push
autorizado de 10B ni inicio de 11A. Lector manual de 7B pendiente. Excluir next-env.d.ts
generado y outputs/. Entradas inferiores son antecedentes.

## Publicación autorizada de 10A — 28/10/2026

Usuario solicita commit y autoriza push de feature/navegacion-10a-capacidades,
base 1429f1d. Incluye resumen de acciones y requisitos por documento, sus pruebas
y el guion asistido completado documentado. Evidencia previa: 223 escenarios Chromium,
17 dirigidos tras precisar facultad, dos de capturas y checks estáticos aprobados.
No se repiten pruebas por las últimas entradas documentales ni se atribuye CI remota.
Excluir frontend/next-env.d.ts generado y outputs/. Verificar identidad remota tras push.
Sin merge, despliegue ni inicio de 10B. Lector manual de 7B pendiente.
Las menciones anteriores a autorización pendiente son antecedentes.

## 10A — guion asistido completado, 28/10/2026

Usuario confirma «recorrido OK» al repetir con nota ficticia nueva el retorno desde
Documentos guardados al borrador EIPD tras haber recargado antes. No se recuperaron
los pendientes anteriores: se comprobó conservación durante la nueva navegación.
Consulta de EIPD general guardada también comprobada en otra evaluación.
Guion asistido acordado completado; escenarios excepcionales mantienen evidencia
automatizada y lector manual de 7B pendiente. Listo para commit/push al autorizarse;
sin publicación de 10A ni inicio de 10B. Entradas inferiores son antecedentes.

## 10A — consulta de EIPD general existente comprobada, 28/10/2026

Captura de otra evaluación muestra EIPD PRUEBA-EIPD-LECTURA-20261010, edición PRUEBA-2,
y las capacidades de consulta esperadas. Se cubre el caso antes pendiente por ausencia
de documento. Ver evidencia y límites en navegacion-servidor.md. Falta confirmar el
retorno a la nota pendiente del borrador EIPD original; preparación de infancia ya comprobada.
Sin commit/push de 10A ni inicio de 10B. Lector manual de 7B pendiente.
Entradas inferiores son antecedentes.

## 10A — recorridos asistidos disponibles comprobados, 28/10/2026

Capturas muestran capacidades de EIPD general, versión histórica de infancia,
facultad revocada, requisitos de preparación y conservación del nombre de edición
al volver en ventana estrecha. Ver registro detallado en navegacion-servidor.md.
Pendiente consulta asistida de EIPD general guardada: no existe en el contexto probado;
no crear un documento solo para comprobar el rótulo. Cobertura automatizada previa
conservada. Sin declaración de aceptación integral, commit/push de 10A ni inicio de 10B.
Lector manual de 7B pendiente. Entradas inferiores son antecedentes.

## Bloque 10A — acciones y requisitos por documento, 28/10/2026

Implementado localmente en `feature/navegacion-10a-capacidades`, base 9B publicada
`1429f1d4bc311a707cf48a5b3a6601b4b2842748`. Resume capacidades del borrador EIPD
general, consulta guardada, versión histórica de infancia, preparación temporal y
decisión organizacional. Los requisitos reflejan los controles y contratos existentes;
facultad explícita separada del rol administrador. Datos sin consultar/error no se
presentan como permisos comprobados. Material histórico cambiado conserva consulta
y no implica invalidez general. Sin ampliar revisión favorable, confirmación o activación.
223 escenarios Chromium con fixtures aprobados; ajuste final de facultad validado
con 17 escenarios dirigidos, tipos/lint/formato y capturas 320/1280 inspeccionadas.
Pendiente validación asistida de 10A; sin commit/push autorizado ni inicio de 10B.
Lector manual de 7B pendiente. Entradas inferiores son antecedentes.
Ver el checklist y evidencia de 10A en `docs/project/navegacion-servidor.md`.
Excluir `frontend/next-env.d.ts` generado y `outputs/`.

## Publicación autorizada de 9B — 28/10/2026

Usuario solicita commit y autoriza push de `feature/navegacion-9b-destinos`, base
`650c766`. Incluye destinos validados desde Pendientes, confirmación del cambio de
contexto, consulta de disponibilidad y conservación de borradores, pruebas y aceptación
asistida acordada. 200 escenarios Chromium con fixtures y checks estáticos aprobados;
los últimos cambios documentan los recorridos y esta autorización. No atribuir nueva
CI remota ni integración backend real. Sin merge/despliegue, lote 10 no iniciado y lector
manual de 7B pendiente. Excluir `frontend/next-env.d.ts` generado y `outputs/`.
Las menciones anteriores de autorización pendiente son antecedentes. Verificar identidad
remota después del push.

## 9B — recorridos asistidos acordados completados, 28/10/2026

Usuario confirma «recorrido OK» al solicitar recarga con cambios pendientes y cancelarla:
se conservan las dos unidades y la nota EIPD. Se completa el guion asistido acordado,
sumado al retorno a formularios, cambio de contexto con cancelación/confirmación y
panel estrecho con cierre y foco ya confirmados. Los casos adicionales de acceso
condicionado, preparación temporal y errores mantienen cobertura automatizada;
no se atribuyen como ejecución asistida del usuario. 200 escenarios Chromium con
fixtures y comprobaciones estáticas previamente aprobados. Sin nueva ejecución de
pruebas por este registro documental, CI remota ni certificación de accesibilidad.
9B listo para commit/push cuando el usuario lo autorice; todavía sin publicación.
Lote 10 no iniciado; lector manual de 7B pendiente. Las entradas anteriores de
validación pendiente son antecedentes.

## 9B — tres recorridos asistidos confirmados, 28/10/2026

Usuario confirma retorno desde Pendientes a cada formulario con texto conservado,
cancelación/confirmación entre trabajadores y clientes, y lectura/cierre/foco del panel
estrecho mediante Escape y fondo exterior. Ver el registro en navegacion-servidor.md.
Pendiente comprobar advertencia de salida/recarga y cancelarla conservando borradores.
200 escenarios automatizados previamente aprobados. Sin commit/push nuevo autorizado
ni inicio de lote 10. Lector manual de 7B pendiente. Entradas inferiores son antecedentes.

## Bloque 9B — destinos de pendientes, 28/10/2026

Implementado localmente en `feature/navegacion-9b-destinos`, sobre 9A publicado
`650c766a28912f37120a22d7c2c47913e21cdd58`. Ver pendientes permite ir al formulario
con su contexto validado; anticipa y permite cancelar el cambio de contexto.
La disponibilidad condicionada se vuelve a consultar antes de mostrar el editor;
una reubicación conserva el borrador y la preparación temporal. Cambiar contexto
explica el destino y conserva pendientes de la visita, sin guardar ni sincronizar pestañas.
[Alcance y checklist asistido](project/navegacion-servidor.md#bloque-9b--destinos-de-pendientes-28102026).
200 escenarios Chromium con fixtures y tipos/lint aprobados; confirmación visual inspeccionada.
Pendiente validación conjunta de 9B; sin commit/push autorizado, merge ni despliegue.
Lote 10 no iniciado. Lector manual de 7B pendiente. Las entradas inferiores son antecedentes.
Excluir `frontend/next-env.d.ts` generado y `outputs/`.

## Publicación autorizada de 9A — 28/10/2026

Usuario solicita commit y autoriza push de `feature/navegacion-9a-pendientes`, base
`a1c93c1`. Incluye unidades pendientes, estados UI, panel consultable, pruebas y
validación asistida acordada. 190 escenarios Chromium y checks estáticos previamente
aprobados; los últimos cambios solo registran los resultados asistidos y esta autorización.
No atribuir CI remota ni integración real a las pruebas con fixtures. Sin merge/despliegue,
9B no iniciado y lector manual de 7B pendiente. Excluir next-env.d.ts generado y outputs/.
Las entradas inferiores de autorización pendiente son antecedentes. Verificar identidad
remota después del push.

## 9A — recorridos asistidos acordados completados, 28/10/2026

Usuario confirma recuperación tras Offline con dos pendientes conservados y sin falso
guardado; capturas distinguen error de conexión de consulta completada. Se suma al
conteo/contexto, guardado parcial y panel estrecho ya confirmados.
[Resultado y límites](project/navegacion-servidor.md#9a--recuperación-confirmada-y-recorridos-acordados-completados-28102026).
190 escenarios automatizados aprobados en el alcance documentado. Listo para commit/push
cuando se autorice; sin publicación de 9A ni inicio de 9B. Lector manual de 7B pendiente.
Las entradas inferiores de aceptación pendiente son antecedentes.

## 9A — panel estrecho confirmado OK, 28/10/2026

Usuario confirma lectura completa, Escape y cierre exterior con retorno del foco a
Ver pendientes (1), sin guardar ni recargar.
[Registro y siguiente comprobación](project/navegacion-servidor.md#9a--panel-estrecho-y-cierre-confirmados-28102026).
Pendiente recuperación de consulta con ambos borradores conservados. Sin commit/push
de 9A ni inicio de 9B; lector manual de 7B pendiente.

## 9A — guardado parcial confirmado OK, 28/10/2026

Usuario confirma que guardar solo la determinación deja un pendiente EIPD y conserva
su nota, sin guardar ese borrador ni recargar.
[Registro y siguiente comprobación](project/navegacion-servidor.md#9a--guardado-parcial-y-nota-conservada-confirmados-28102026).
Pendientes cierre/foco en ventana estrecha y recuperación de consulta. Sin commit/push
de 9A ni inicio de 9B; lector manual de 7B pendiente.

## 9A — primer recorrido asistido OK, 28/10/2026

Usuario confirma conteo de dos unidades identificadas: determinación y un solo borrador
EIPD para sus siete pasos, con contexto correcto en la captura.
[Registro y siguiente comprobación](project/navegacion-servidor.md#9a--conteo-e-identificación-confirmados-28102026).
Pendiente guardar solo la determinación y comprobar conservación de EIPD; restantes
recorridos de 9A siguen abiertos. Sin publicación de 9A ni inicio de 9B.

## 9A implementado localmente — 28/10/2026

Rama `feature/navegacion-9a-pendientes`, base 8B `a1c93c1`. Ver pendientes (N)
identifica formularios y preparación temporal con contexto; siete pasos EIPD cuentan
una sola unidad. Estados UI distinguen lectura y escritura; guardado parcial y error
conservan los demás pendientes. Sin autosave/almacenamiento nuevo, navegación de 9B,
cambios API ni habilitación EIPD. 190 Chromium con fixtures y checks estáticos aprobados.
[Alcance, evidencia y checklist asistido](project/navegacion-servidor.md#bloque-9a--pendientes-identificables-28102026).
Pendiente aceptación asistida; sin commit/push autorizado de 9A, merge o despliegue.
Lector manual de 7B pendiente. Excluir next-env.d.ts generado y outputs/.
Las entradas inferiores describen antecedentes; lote 9 ahora sí está iniciado.

## Publicación autorizada de 8B — 27/10/2026

Usuario solicita commit y autoriza push de `feature/navegacion-8b-pasos`, base `e04d8d8`.
Incluye navegación principal EIPD, título/Paso N de 7, Anterior/Siguiente, foco al cambiar
ancho, pruebas y aceptación asistida. Evidencia: 111 escenarios de regresión más cinco de
repetición aprobados en ejecuciones separadas; tipos/lint/formato y capturas aprobados.
Lector manual de 7B pendiente. No atribuir CI remota nueva al push.
Las menciones inferiores de autorización pendiente son antecedentes. Excluir next-env.d.ts
generado y outputs/ locales. Lote 9 no iniciado; sin merge/despliegue. Verificar HEAD remoto.

## 8B — recorridos asistidos completados, 27/10/2026

Usuario confirma el último recorrido móvil, nota conservada y cierre exterior/foco.
8B aceptado en el alcance acordado, incluidos zoom 200 %, Escape repetido, ampliación y
Atrás/Adelante. [Evidencia y límites](project/navegacion-servidor.md#8b--recorridos-asistidos-completados-27102026).
111 escenarios de regresión + cinco nuevos de repetición aprobados en ejecuciones separadas.
Listo para commit/push cuando se autorice; lote 9 no iniciado. Lector manual de 7B pendiente.
Las entradas inferiores de validación pendiente son antecedentes del proceso.

## 8B — Atrás/Adelante y nota conservada OK, 27/10/2026

Usuario confirma regreso al Paso 4 con Atrás, retorno al Paso 5 con Adelante y nota
conservada en Describir riesgos, sin guardar ni recargar.
[Resultado y remanente asistido](project/navegacion-servidor.md#8b--atrásadelante-y-conservación-confirmados-27102026).
Pendiente secuencia móvil de tres destinos y cierre exterior; sin publicación de 8B.

## 8B — ampliación y foco confirmados OK, 27/10/2026

Usuario confirma cierre de Secciones al maximizar la pestaña actualizada y foco en la
barra visible. Zoom 200 % y Escape repetido previamente confirmados.
[Registro y siguiente prueba](project/navegacion-servidor.md#8b--ampliación-y-foco-en-barra-confirmados-27102026).
Pendiente Atrás/Adelante con conservación de nota; sin commit/push de 8B ni lote 9.

## 8B — zoom del navegador 200 % OK, 27/10/2026

Usuario confirma lectura/selección de pasos mediante Secciones con zoom real 200 %, sin
recortes ni desplazamiento horizontal de página, y retorno a 100 %.
[Registro y límites](project/navegacion-servidor.md#8b--zoom-real-200--confirmado-27102026).
Pendientes ampliación/foco y Atrás/Adelante; sin commit/push de 8B ni inicio de lote 9.

## 8B — Escape repetido confirmado OK, 27/10/2026

Usuario confirma apertura/cierre repetidos de Secciones sin elegir destino, con Escape
y foco de retorno. Caso anterior aclarado: el panel cerrado no consume Escape como
atajo global. [Registro y pendientes](project/navegacion-servidor.md#8b--cierre-repetido-de-secciones-confirmado-27102026).
Continúan pendientes zoom real 200 %, ampliación/foco y navegación histórica; sin publicación de 8B.

## 8B — Escape con panel cerrado aclarado, 27/10/2026

Captura muestra el formulario sin Secciones abierto: Escape no es un atajo global al
botón. No se reproduce fallo de cierre de un panel abierto. Pendiente repetir apertura
→ Escape sin elegir destino y confirmar; zoom real 200 % también pendiente.
[Detalle](project/navegacion-servidor.md#8b--aclaración-de-escape-mediante-captura-27102026).
Sin cambios adicionales de producto ni publicación de 8B.

## 8B — secuencia y conservación de nota OK, 27/10/2026

Usuario confirma Describir riesgos → Valorar riesgos → Medidas de mitigación,
Pasos 3/4/5 y nota conservada al volver sin guardar ni recargar.
[Registro y pendientes](project/navegacion-servidor.md#8b--secuencia-y-borrador-confirmados-27102026).
Continúan pendientes las comprobaciones de ventana estrecha, zoom y navegación histórica.
Sin commit/push de 8B ni inicio de lote 9.

## 8B — primer recorrido asistido OK, 27/10/2026

Usuario confirma Describir riesgos, Paso 3 de 7 y ausencia de lista central repetida
en ventana amplia. Continúan pendientes los siguientes recorridos del guion 8B;
[registro y límites](project/navegacion-servidor.md#8b--primera-comprobación-asistida-confirmada-27102026).
Sin commit/push de 8B ni inicio de lote 9.

## Bloque 8B implementado localmente — 27/10/2026

Rama `feature/navegacion-8b-pasos` sobre 8A publicado `e04d8d8`. Navegación EIPD conectada
sin lista central repetida; título/Paso N de 7 y Anterior/Siguiente después del formulario.
Barra desde 1200 px, panel Secciones por debajo; foco conservado al cambiar de ancho.
Editor independiente conserva su navegación. 111 Chromium (91 conectados + 20 independientes),
tipos/lint/formato y capturas aprobados. [Alcance y guion](project/navegacion-servidor.md#bloque-8b--navegación-principal-y-paso-actual-27102026).
Pendiente validación asistida, incluido zoom real 200 %. Lector manual de 7B pendiente.
Sin commit/push de 8B ni inicio de lote 9. Excluir next-env.d.ts generado y outputs/ locales.
Esta entrada actualiza las menciones anteriores de 8B no iniciado.

## Publicación autorizada de 8A — 27/10/2026

Usuario solicita commit y autoriza push en `feature/navegacion-8a-contexto`, base `15aa273`.
Se publica el contexto compacto y su detalle accesible, conservación de la cabecera
independiente, pruebas y resultados asistidos de 8A. 104 Chromium aprobados y checks
estáticos previos aprobados; no atribuir CI remota al push. Lector manual de 7B pendiente.
Las entradas inferiores de autorización pendiente describen estados anteriores.
Excluir `frontend/next-env.d.ts` generado y `outputs/` locales. 8B no iniciado;
sin merge ni despliegue. Verificar identidad del commit remoto tras publicar.

## 8A — recorridos asistidos completados, 27/10/2026

Usuario confirma ámbito organizacional en Mi organización/Autodiagnóstico y retorno a
Bases de licitud con su selección recuperada. Sumado a los recorridos anteriores y captura
histórica, 8A queda aceptado en ese alcance. Ganancia de espacio respaldada por mediciones
locales; 104 Chromium y comprobaciones estáticas previas aprobados.
[Resultado y límites](project/navegacion-servidor.md#8a--recorridos-asistidos-completados-27102026).
Listo para cierre Git cuando sea autorizado; sin commit/push de 8A ni inicio de 8B.
Lector manual de 7B pendiente. Las entradas inferiores describen estados anteriores.

## 8A — identidad histórica comprobada en captura, 27/10/2026

Cabecera de evaluación versión 1/borrador separada de resolución 1, referencia
SIMULADA-PILOTO-INFANCIA-RES-001 y edición PRUEBA-1 en Documentos guardados.
Evidencia visual añadida al [registro de 8A](project/navegacion-servidor.md#8a--evidencia-de-identidad-histórica-27102026).
No se registraron actuaciones. Conserva los límites de validación documentados;
sin nueva autorización de commit/push ni inicio de 8B.

## 8A — contexto por módulo confirmado, 27/10/2026

El usuario confirma «recorrido OK» al comprobar Ver contexto completo en Inventario
(organización/tratamiento), Panel principal (solo organización) y retorno a Bases de
licitud (finalidad/evaluación y texto pendiente conservados), sin recargar ni guardar.
Este resultado se suma a las comprobaciones asistidas previas del detalle y ventana estrecha.
Queda por comprobar la distinción entre evaluación activa y documento histórico consultado;
Mi organización/Autodiagnóstico conservan cobertura automatizada, sin atribuirles ahora una
prueba asistida adicional. Lector manual de 7B pendiente. Sin nueva autorización de
commit/push ni inicio de 8B.

## 8A — ventana estrecha confirmada, 27/10/2026

Usuario confirma «recorrido OK» tras reducir el ancho sin recargar, abrir Ver contexto
completo, leer sus datos con desplazamiento si es necesario y cerrar sobre el fondo gris
exterior al panel, con foco de retorno y texto del formulario conservado.
Se acepta este recorrido acotado; siguen pendientes ámbito por módulo e identidad histórica.
No atribuir prueba manual con lector de pantalla ni cierre completo de 8A.
Sin autorización nueva de commit/push; 8B no iniciado.

## 8A — primera comprobación asistida OK, 27/10/2026

El usuario confirma «prueba OK» tras el guion de abrir Ver contexto completo en Bases de
licitud, comprobar la selección y cerrar con Escape con retorno del foco y conservación del
formulario. Se registra aceptación de este recorrido, no del conjunto completo de 8A.
Pendientes: detalle en ventana estrecha/nombres largos y cierre exterior, ámbitos por módulo
y distinción frente al documento histórico. [Guion y evidencia](project/navegacion-servidor.md#bloque-8a--contexto-compacto-implementado-27102026).
Sin nueva autorización de commit/push; 8B no iniciado. Lector manual de 7B sigue pendiente.

## Bloque 8A implementado localmente — 27/10/2026

Rama `feature/navegacion-8a-contexto` sobre 7B publicado `15aa273`.
Cabecera compacta con detalle completo accesible; contexto por módulo; retirada del resumen
repetido solo en recorrido conectado. Formularios independientes y documento histórico conservados.
104 Chromium aprobados (84 conectados + 20 independientes), tipos/lint/formato y capturas
comparables; evidencia y [guion asistido 8A](project/navegacion-servidor.md#bloque-8a--contexto-compacto-implementado-27102026).
Pendiente validación del usuario; sin commit/push ni inicio de 8B. Lector de pantalla de 7B
sigue pendiente. Excluir `frontend/next-env.d.ts` generado y `outputs/` locales.
Las entradas inferiores de «sin inicio de 8A» describen estados anteriores.

## Publicación autorizada de 7B — 27/10/2026

Usuario solicita commit y autoriza push de 7B en feature/navegacion-7b-accesibilidad,
base 39bca0b. Publicar estructura/nombres/ayudas, pruebas y validación asistida acotada.
La prueba manual con lector de pantalla permanece pendiente por no disponibilidad del
usuario; publicar no cierra ese criterio ni acredita accesibilidad integral certificada.
168 escenarios aprobados y 1 captura opcional omitida según ejecución registrada;
no atribuir CI remota nueva al push. Los pendientes inferiores de autorización describen
estados anteriores. Excluir next-env.d.ts generado y outputs/ locales; verificar HEAD
remoto tras publicar. No iniciar 8A ni ejecutar merge/despliegue en este cierre.

## 7B — recorridos visuales y de teclado confirmados, 27/10/2026

Usuario aporta secuencia de Determinar aplicabilidad a Documentos guardados con título
de pestaña actualizado; confirma «recorrido OK» al abrir/cerrar Secciones y Contexto
con retorno del foco; confirma contorno de foco en Consultar última determinación guardada.
Capturas muestran ayuda de consulta y explicación de Nombre de la edición en preparación
de infancia. Confirma «recorrido OK» al abrir y cerrar Análisis, riesgos, medidas, fuentes
y evidencias con Enter, manteniendo foco. Es aceptación de esos recorridos, sin registrar
nuevos documentos ni actuaciones durante el guion.

Usuario informa que no dispone de Narrador/NVDA. La prueba manual con lector de pantalla
no se ejecutó y permanece pendiente, junto con cualquier comprobación asistida no cubierta.
La verificación estructural de main único, nombres, relaciones e IDs sigue respaldada por
fixtures automatizados; una captura visual no acredita su anuncio por lector. Tampoco se
atribuye al usuario prueba táctil real, comprobada solo mediante emulación.

168 pruebas aprobadas y 1 captura opcional omitida, según evidencia previa. 7B validado
parcialmente con este alcance; no dar por completado su criterio de lector ni declarar
accesibilidad certificada. Sin commit/push de 7B ni inicio de 8A. Rama
feature/navegacion-7b-accesibilidad sobre 39bca0b. Excluir generados y capturas locales.
Las menciones inferiores de aceptación asistida totalmente pendiente son antecedentes;
queda pendiente específicamente la parte no comprobada indicada aquí.

## Bloque 7B implementado localmente — 27/10/2026

Usuario solicita continuar 7B; rama feature/navegacion-7b-accesibilidad sobre 39bca0b.
Main conectado único/nominado, menú conectado con nombre correcto, título por destino,
relaciones de diálogos, regiones documentales sin pestañas ocultas e IDs por evaluación.
Ayudas asociadas y bloqueo EIPD por causa real, preservando usos independientes y 7A.
168 pruebas aprobadas (6 nuevas 7B); 1 captura opcional omitida, tipos/lint/formato correctos.
Capturas 1280/390 revisadas. Pruebas controladas; no certificación ni prueba con lector.
[Guion y límites](project/navegacion-servidor.md#bloque-7b--nombres-regiones-y-ayudas-accesibles).
Pendientes validación asistida y lector de pantalla; sin commit/push ni inicio de 8A.
Excluir next-env.d.ts generado y outputs/ locales. Entradas inferiores son antecedentes.

## Publicación autorizada de 7A — 27/10/2026

Usuario solicita commit y autoriza push de 7A aceptado, en feature/navegacion-7a-teclado
sobre 8fec3df. Se reúne navegación de teclado, manejo explícito de Espacio, regresiones
y aceptación asistida acotada. Los pendientes de publicación inferiores son antecedentes
anteriores a esta autorización. Mantener los límites de evidencia: pasada completa de 67
antes del último ajuste y siete escenarios dirigidos después, sin atribuir CI remota.
Excluir next-env.d.ts generado y outputs/ locales. Comprobar HEAD remoto tras el push.
No iniciar 7B ni ejecutar merge/despliegue en este cierre.

## Aceptación asistida acotada de 7A — 27/10/2026

Usuario confirma «Todo funciona OPK» tras comprender que el clic exterior se hace sobre
el fondo gris y no dentro del panel azul. Aceptados los recorridos informados: primera
secuencia Enter/Tab/Escape; apertura/cierre con Espacio en pestaña nueva con código
actualizado; avance al siguiente grupo y selección de destino («Todo el recorrido OK»);
y prueba estrecha de Menú/Secciones, Escape y clic interior/exterior tras aclaración.
El usuario también comprobó que la pestaña antigua conserva su preparación de infancia;
la nueva empieza vacía por ser temporal por pestaña, sin registro ni sincronización.
Esto no acredita copia de borradores entre ventanas ni guardado de una nueva versión.

7A aceptado con este alcance asistido. Retención completa de Tab/Shift+Tab, cambio de
tamaño con foco y ausencia de escrituras siguen respaldados por escenarios controlados,
sin atribuir pruebas manuales adicionales. No equivale a certificación de accesibilidad
ni cierra 7B o NAV-UX-006 globalmente. Evidencia automatizada: pasada completa inicial
de 67; tras ajuste explícito de Espacio pasaron 7 escenarios dirigidos, tipos y lint.
No se declara una pasada completa posterior de 68 escenarios.

Rama feature/navegacion-7a-teclado sobre 8fec3df. Sin commit/push de 7A; requiere
indicación del usuario para publicar. Próximo propuesto: 7B, estructura y ayudas
accesibles, sin iniciar. Excluir next-env.d.ts generado y outputs/ locales.
Esta aceptación sustituye los pendientes asistidos anteriores solo con el alcance indicado.

## 7A — observación asistida de Espacio y corrección explícita, 27/10/2026

Usuario confirma la primera secuencia Enter/Tab/Escape («toda la secuencia OK»),
pero informa que presionar y soltar Espacio no abre/cierra Preparar. La prueba
Chromium controlada anterior sí activaba el summary nativo; no se atribuye una
reproducción exacta del navegador del usuario. Se reemplaza solo para Espacio la
activación implícita por manejo explícito en el summary conectado: cancelar acción
nativa, alternar una vez por pulsación e ignorar repetición al mantener la tecla.
Enter mantiene su acción nativa; Tab, Escape y foco conservan sus comportamientos.

Siete escenarios dirigidos 7A aprobados tras el ajuste: los seis existentes y uno
nuevo que despacha eventos sin activación nativa y comprueba pulsación mantenida,
liberación, apertura/cierre real sin doble activación, mismo foco/URL y cero escrituras.
Tipos/lint/formato y diff --check correctos. La pasada completa de 67 escenarios
corresponde a antes de este ajuste; no se declara una nueva pasada completa de 68.
Pendiente repetir Espacio con el usuario y continuar aceptación de 7A. Sin commit/push.
No recargar su pestaña con borradores pendientes; para cargar código actualizado si
fuera necesario usar pestaña independiente con contexto propio.

## Bloque 7A implementado localmente — 27/10/2026

Usuario autoriza continuar 7A; rama feature/navegacion-7a-teclado sobre 8fec3df.
Corregidos dos problemas reproducidos de teclado en desplegables de escritorio:
coexistencia y permanencia al salir con Tab. Cierre sin robar foco, Escape localizado,
exclusión al abrir paneles y foco a Secciones al ocultarse navegación de escritorio.
Paneles compartidos, foco/scroll a trabajo y borradores conservados, sin cambios API/backend.
67 escenarios conectados (6 nuevos) aprobados; tipos/lint/formato y capturas revisados.
Pruebas controladas, no aceptación del usuario ni certificación de accesibilidad.
[Guion y evidencia](project/navegacion-servidor.md#bloque-7a--teclado-y-foco-en-navegación-conectada).
Pendiente validación asistida; sin commit/push ni inicio de 7B. Excluir generados/capturas.
Las entradas siguientes describen antecedentes anteriores.

## Cierre asistido y publicación autorizada de 6B — 27/10/2026

Usuario solicita commit y autoriza push al terminar las comprobaciones asistidas.
Rama `feature/navegacion-6b-operaciones`, base d9f859f. Se acepta con el alcance
observado y confirmado: nombres de edición y pasos EIPD, disponibilidad independiente
por tema, matriz alineada/coloreada, aviso ante reemplazo de preparación, cambio entre
revisión documental y decisión de organización («resultado OK»), conservación al volver
a preparación y regreso desde vista previa con referencia, PRUEBA-1 y notas intactas.
El usuario guardó expresamente una determinación ficticia de infancia Corresponde en
el programa con menores, manteniendo EIPD pendiente; capturas confirman su acceso.
Se encontraron dos versiones históricas; durante el guion no se solicitó registrar
otra ni emitir revisión/decisión. La vista previa mostró registro deshabilitado sin
revisión de contenido; volver mantuvo los campos. La preparación conservada no acredita
una copia nueva ni persistencia después de recargar. No atribuir esos ensayos al usuario.

171 escenarios automatizados distintos aprobados: 157 del bloque y 14 del formulario de
valoración (3 nuevos de matriz). Tipos/lint/formato correctos; capturas controladas de
1280/390/320 revisadas. Ausencia de registro, negativas, información insuficiente,
asociación por revisar y errores/carga conservan evidencia controlada, no nueva aceptación
manual. La prueba integrada API aislada no se ejecutó. Sin cambios backend ni reglas de
activación EIPD. NAV-UX-006 permanece abierto para los demás sublotes.

Este cierre sustituye los pendientes de aceptación asistida anteriores solo con ese
alcance. Commit/push autorizado para estos cambios y documentación; excluir next-env.d.ts
generado y outputs/ locales. No hacer merge/despliegue ni iniciar 7A en este cierre.
Siguiente bloque propuesto: 7A, teclado y foco, pendiente de indicación del usuario.

## Ajuste visual solicitado durante 6B — matriz Probabilidad / Impacto

26/10/2026. Usuario solicita alinear cabeceras y distinguir niveles por color.
Implementado en AssessmentSupportPanel: tabla de columnas fijas, títulos y valores
centrados, bordes visibles y cabeceras con scope de fila/columna. Bajo verde suave
(#dcfce7), Medio amarillo suave (#fef9c3), Alto naranja suave (#fed7aa), Muy alto rojo
suave (#fecaca), con texto oscuro (#0f172a), nombres explícitos y cabeceras neutras.
Contraste calculado texto/fondo: 16,26; 16,62; 13,19 y 12,34 a 1 respectivamente.
No se modifican valores de la matriz, metodología ni cálculo; el color es apoyo visual.
En ventana estrecha se conserva desplazamiento horizontal local con acceso por teclado.

14 escenarios del formulario aprobados, incluidos 3 de alineación/colores y dimensiones
1280/390/320; tipos y ESLint correctos. Capturas revisadas en outputs/matriz-6b (locales,
no publicar). Respuestas ficticias controladas; pendiente revisión visual por usuario en
Valorar riesgos → Metodología CUMPLEIA-CUALITATIVA-1 y criterios. Sin commit/push nuevo.

## Bloque 6B implementado localmente — 26/10/2026

Usuario solicita continuar 6B. Rama `feature/navegacion-6b-operaciones`, base publicada
`d9f859f9742cd013479e002536f366ad6573ca5a`. Operaciones documentales diferenciadas,
nombre libre de edición con ayuda, siete pasos EIPD alineados y razones de disponibilidad
por tema, sin acceso al editor bloqueado. Conservados contratos, históricos y borradores;
sin cambios backend ni activación EIPD. 157 escenarios distintos aprobados con fixtures,
tipos/lint/formato correctos y capturas escritorio/390/320 revisadas. No atribuir ensayo
integrado contra el servidor del usuario. Pendiente aceptación asistida según
[guion y evidencia](project/navegacion-servidor.md#bloque-6b--operaciones-documentales-y-disponibilidad).
Sin commit/push nuevo ni inicio de 7A. Excluir `frontend/next-env.d.ts` generado y `outputs/`.
Las entradas inferiores conservan antecedentes del cierre anterior.

## Publicación autorizada del bloque 6A — 26/10/2026

Usuario solicita commit y autoriza push del bloque 6A aceptado, en
feature/navegacion-6a-destinos sobre d42b2e9. Se reúnen implementación, regresiones,
legibilidad ajustada y aceptación asistida acotada. Las menciones inferiores de
publicación pendiente son antecedentes anteriores a esta autorización.
Excluir next-env.d.ts generado y outputs/ locales. Verificar HEAD remoto tras publicar;
no atribuir CI remota por el push. No iniciar 6B ni ejecutar merge/despliegue.

## Cierre asistido acotado 6A — 26/10/2026

Usuario confirma «esta OK la glosa» tras aumentar legibilidad de Revisar y decidir.
Aceptados los recorridos informados de acceso Documentos guardados/nombres, Historial con
Atrás/Adelante, conservación de nota EIPD y funcionamiento de Continuar, más este ajuste
visual. No atribuir a la captura estrecha antigua la comprobación de nombres nuevos;
320/390 conservan evidencia controlada, no nuevo ensayo asistido documentado.
6A aceptado con este alcance; no cierra NAV-UX-006 globalmente. [Detalle](project/navegacion-servidor.md#aceptación-asistida-del-rótulo-y-cierre-acotado-6a).
Cambios locales sobre d42b2e9, sin commit/push nuevo ni inicio de 6B. Próximo bloque
propuesto: 6B, pendiente de indicación. Los estados inferiores son antecedentes anteriores.

## Validación parcial 6A y legibilidad del grupo — 26/10/2026

Usuario confirma acceso/nombres Documentos guardados, Atrás/Adelante (3 OK), conservación
de nota EIPD y funcionamiento de Continuar. Observa que Revisar y decidir se lee demasiado
pequeño en escritorio. Ajuste acotado del rótulo: tamaño 1rem, negrita, color de texto
principal y espaciado; Documentos guardados conserva acceso directo y misma URL.
Captura estrecha aportada de Continuar aún muestra el nombre anterior Revisar documentos;
no acredita por sí sola nomenclatura nueva en móvil. Pendiente aceptación visual del
rótulo ajustado y comprobar móvil en la pestaña actualizada. Sin inicio de 6B ni commit/push.

## Bloque 6A implementado localmente — 26/10/2026

Usuario autoriza continuar exclusivamente 6A del plan. Rama feature/navegacion-6a-destinos,
base d42b2e9. Nombres de destino compartidos en navegación conectada; pantalla Documentos
guardados unificada en menú/miga/título/Continuar y enlaces de orientación. Grupos de un
solo destino son enlaces directos; grupos múltiples conservan desplegable. Activo señalado
por subrayado/borde/negrita y aria-current en el destino; no implica guardado o completitud.
Rutas, IDs, contexto, persistencia y reglas no cambian; componente documental independiente
conserva sus títulos anteriores. Sin cambios backend ni habilitación EIPD.

Validación: 51 escenarios conectados (5 nuevos), 20 del flujo documental independiente y
18 de maqueta de referencia aprobados; 89 distintos, sin sumar repeticiones. Tipos, ESLint,
formato y capturas escritorio/390/320 revisados. Pruebas con fixtures ficticios, no una
nueva prueba integrada contra el servidor del usuario. [Evidencia y guion](project/navegacion-servidor.md#bloque-6a--destinos-coherentes-y-accesos-directos).
Pendiente aceptación asistida del usuario. No iniciar 6B ni otros lotes. Sin commit/push
nuevo ni merge/despliegue; autorización previa cerró solamente la documentación del plan.
next-env.d.ts generado y outputs/ locales ajenos al bloque funcional.

## Plan integral de navegación y terminología — 26/10/2026

Usuario solicita analizar dos informes Word de Claude antes del siguiente lote y
replanificar incorporando los lotes pendientes 6, 7 y 8. Contraste de texto/tablas/diagramas,
código y contratos sobre `2e3f5460190185413f6e85243ad59958ba148463`.
La revisión de Claude es fuente externa, no instrucciones ni circuito de ejecución.
Se agregan [evaluación P1–P13 y glosario G01–G30](project/evaluacion-propuestas-claude.md)
y [plan por sublotes 6–13](project/plan-navegacion-formularios.md).
Decisiones de diseño propuestas para implementación, no cambios funcionales aceptados en uso.
Conservar lotes 1–5 y sus aceptaciones; Git acredita lote 5 publicado en 2e3f546.
Las notas históricas siguientes de publicación pendiente describen estados anteriores.

Rama documental: feature/plan-navegacion-terminologia. Sin cambios nuevos de código,
API, datos, permisos ni activación EIPD. No se inicia lote 6. Próximo propuesto: 6A,
nombres de destinos y accesos de un solo destino, con validación conjunta antes de avanzar.
NAV-UX-005, LIC-FORM-001 y demás trabajos funcionales conservan sus propios contratos.
El usuario solicita incorporar los Markdown al repositorio y autoriza commit/push el 26/10/2026.
Este cierre publica solo documentación; no inicia 6A ni acredita implementación o CI remota.
Sin merge/despliegue.
Excluir next-env.d.ts generado y outputs/ locales de cualquier publicación posterior.

## Cierre autorizado del lote 5 — 26/10/2026

Usuario solicita commit y autoriza push del lote 5 aceptado en fix/navegacion-estado-guardado.
Este cierre reúne implementación, pruebas y aceptación asistida C9, incluidos rótulos y
proximidad del resultado de guardado. Las menciones anteriores de publicación pendiente
son antecedentes previos a esta autorización. Excluir frontend/next-env.d.ts y outputs/.
No iniciar lote 6 ni ejecutar merge/despliegue. Comprobar HEAD remoto exacto tras publicar;
no inferir aprobación de CI remota del push. Otros pendientes del backlog conservan su alcance.

## Último resultado — lote 5 aceptado, 26/10/2026

Usuario confirma «OK las etiquetas». Lote 5 C9 aceptado con alcance de consulta que
conserva borrador, comparación rotulada, guardado/revisión coincidente y aviso próximo
a Guardar. Concurrencia, errores y móvil verificados con fixtures, no nuevos ensayos
manuales. Evidencia y límites en [continuidad](project/navegacion-servidor.md#aceptación-asistida-del-lote-5--etiquetas-confirmadas-26102026).
Cambios locales en fix/navegacion-estado-guardado sobre 84ad96a, sin commit/push nuevo.
Archivo generado frontend/next-env.d.ts y capturas de outputs/ ajenos al commit funcional.
Siguiente propuesto: lote 6, pendiente de indicación. No se inicia otro lote.

## Último resultado — lote 5, 26/10/2026

Usuario acepta proximidad del aviso de guardado (OK). Solicita conceptos en cada valor
comparado: etiquetas de decisión y fundamento agregadas en ambas columnas, para EIPD e
infancia. Once pruebas dirigidas, tipos/lint/formato y capturas correctos tras el ajuste;
46 pruebas completas anteriores no repetidas. Pendiente revisión asistida de etiquetas.
Conservar la pestaña original con sus cambios pendientes; no guardar ni recargar para
probar los rótulos. Sin commit/push nuevo. Lote 6 y demás pendientes no iniciados.

## Último resultado asistido — guardado del lote 5

Captura dfa6d431 confirma revisión de aplicabilidad 4 y formulario coincidente,
sin comparación pendiente en el panel. Falta comprobar visualmente el aviso de éxito
inmediatamente antes de Guardar: bajar en la misma pestaña, sin repetir guardado,
editar, consultar o recargar. Sin commit/push del lote 5; aceptación parcial.

## Último resultado asistido — lote 5, 25/10/2026

Capturas ead7a637/fad26d34 confirman consulta y comparación: revisión guardada 3,
línea de prueba conservada en borrador, resultado de consulta y cambios sin guardar.
Aceptación parcial de C9; pendiente guardar explícitamente y validar proximidad del
aviso de éxito/revisión incrementada. No recargar el borrador para esta prueba.
[Detalle y próximo paso](project/navegacion-servidor.md#validación-asistida-del-lote-5--consulta-y-comparación-correctas).
Sin commit/push nuevo ni inicio de otro lote.

## Bloque activo — lote 5 C9, 25/10/2026

Usuario autoriza continuar lote 5 tras documentación publicada en 84ad96a. Implementado
localmente en fix/navegacion-estado-guardado: última determinación consultada con revisión,
fecha/hora Chile y autoría por identificador del contrato; comparación con borrador pendiente;
consulta explícita sin escrituras; historial abierto tras rechazo 409; confirmación de guardado
inmediatamente antes de Guardar. No se inventan nombres de personas ni se modifican permisos,
API, DB o activación EIPD. 46 pruebas Chromium aprobadas (11 nuevas), tipos/lint/formato
correctos; capturas escritorio/390/320 revisadas. Validación asistida pendiente, sin commit/push
del lote 5. Archivo generado frontend/next-env.d.ts ajeno al bloque; capturas ficticias
en outputs/navegacion-lote5/ son evidencia local no destinada al commit. Próximo paso: seguir el
[guion de aceptación del lote 5](project/navegacion-servidor.md#lote-5-c9--estado-guardado-y-borrador).
Los lotes siguientes y demás pendientes del backlog no se inician ni se cierran por este cambio.

## Guía del ciclo documental — 25/10/2026

Se agrega la [guía de borradores, versiones, revisión y decisión EIPD](project/ciclo-documental-eipd.md), contrastada con e587da6, en la rama feature/documentacion-ciclo-documental. Incluye funcionamiento actual, límites de revisión del EIPD general, sucesores de infancia y circuito conceptual pendiente. Cambio exclusivamente documental; no modifica estados, permisos, datos ni la interfaz. El usuario autoriza commit y push de esta guía. Lote 5 y los demás pendientes del backlog conservan su estado.

## Cierre autorizado del lote 4 — 25/10/2026

Usuario autoriza commit y push del lote 4 validado en
fix/navegacion-orientacion-aplicabilidad. El presente bloque reúne implementación,
pruebas y aceptación asistida C3/C8. Lote 5 y mejora de ubicación del aviso de guardado
siguen pendientes, sin iniciar. Verificar HEAD/CI remoto exactos al retomar; no se
infiere CI funcional aprobada de una publicación. Sin merge ni despliegue.
El archivo frontend/next-env.d.ts regenerado por Next.js queda fuera de este commit.

## Último resultado — lote 4 validado, 25/10/2026

Captura 227db7c3 confirma retorno a EIPD tras restaurar Corresponde, con nota pendiente
conservada. Resumen/acceso directo, No corresponde y reubicación explicada ya comprobados
asistidamente. Lote 4 C3/C8 aceptado con ese alcance, local en
fix/navegacion-orientacion-aplicabilidad sobre 0340b0a, sin commit/push nuevo.
Siguiente propuesto: lote 5 C9, incluido acercar la confirmación de guardado al botón.
Pruebas de infancia y demás estados automatizadas; no atribuir ensayos manuales no realizados.

## Bloque activo — lote 4 C3/C8, 25/10/2026

Lote 3 publicado en 0340b0a (remoto verificado). Lote 4 implementado localmente en
fix/navegacion-orientacion-aplicabilidad: resultado de accesos según determinación
guardada, guía para estados no habilitados/consulta previa y aviso de reubicación
con conservación de borradores. Sin cambios de reglas/API/DB/permisos. 34 pruebas
conectadas y 10 dirigidas finales aprobadas (35 escenarios únicos), tipos/lint/formato
y capturas escritorio/390/320 correctos. Aceptación asistida y publicación lote 4
pendientes. [Guion vigente](project/navegacion-servidor.md). No iniciar otros lotes.

## Último resultado — lote 3 validado, 25/10/2026

Usuario confirma OK ayuda dinámica de Guardar y selector de contexto (motivo de
bloqueo, habilitación al seleccionar evaluación y Cancelar). Lote 3 C4 aceptado con
ese alcance; roles/solo consulta verificados automáticamente con fixtures, no otras
cuentas personales. Cambios locales en fix/navegacion-permisos-requisitos sobre
9c8632f; sin commit/push nuevo. Próximo propuesto: lote 4 C3/C8, aún no iniciado.

## Bloque activo — lote 3 C4, 25/10/2026

Lote 2 validado y publicado en 9c8632f, rama fix/navegacion-contexto-modulo.
Usuario autoriza continuar lote 3: implementado localmente en
fix/navegacion-permisos-requisitos, explicaciones de permisos/solo consulta y
requisitos para Guardar/Aplicar contexto, con descripciones accesibles. Veinticinco
Chromium, tipos/lint/formato y capturas aprobados; aceptación asistida pendiente.
Sin commit/push del lote 3 ni cambios de permisos/cuentas/datos/API/DB.
[Guion y límites](project/navegacion-servidor.md). Otros lotes permanecen pendientes.

## Último resultado — lote 2 aceptado, 25/10/2026

Usuario confirma Todo OK; capturas verifican Continuar contextual, cabecera RAT y
retorno a EIPD con notas sin guardar conservadas. Lote 2 C2/C14 validado, local en
fix/navegacion-contexto-modulo sobre lote 1 publicado 465a94c; sin commit/push nuevo.
Siguiente bloque propuesto: lote 3 C4 (permisos/requisitos), aún no iniciado.
No descartar notas pendientes ni cerrar otros criterios de backlog por esta aceptación.

## Bloque activo — lote 2 C2/C14, 25/10/2026

Lote 1 validado y publicado como 465a94c en fix/navegacion-carga-recuperacion,
confirmado contra remoto. Usuario autoriza continuar lote 2: implementación local
en fix/navegacion-contexto-modulo, cabecera por ámbito y Continuar con contexto del
destino; rutas/memoria/borradores intactos. Veinte Chromium, tipos/lint/formato y
capturas escritorio/390/320 aprobados. Aceptación asistida pendiente; sin publicación
nueva del lote 2. Ver [guion vigente](project/navegacion-servidor.md).

## Último resultado asistido — C1, 25/10/2026

Usuario confirma recuperación con Reintentar consulta y notas EIPD pendientes
conservadas en pestaña original tras reautenticar en otra. Lote 1 acotado completado
localmente; 16 Chromium/tipos/lint aprobados, sin commit/push nuevo. Seguimiento de
clasificación de error/sesión y mejoras de botón/duplicación registrados en backlog.
No iniciar lotes siguientes sin indicación; NAV-UX-003/004 no cerrados globalmente.
Los estados anteriores «recuperación pendiente» son antecedentes de este ensayo.

## Bloque activo — lote 1 C1, 25/10/2026

Retomado por usuario. Corrección local en fix/navegacion-carga-recuperacion sobre
db6f0d3: carga/error de aplicabilidad visibles en secciones condicionales, reintento
y retorno al formulario sin desmontar borradores; indicador/reintento de validación
de enlace fuera del selector. 15 Chromium, tipos/ESLint/formato y tres casos visuales
a 390/320/escritorio aprobados. Validación asistida pendiente, sin commit/push nuevo.
[Alcance y guion](project/navegacion-servidor.md#correcciones-de-revisión-externa--lote-1-c1-25102026).
Claude solo revisor externo; restantes lotes pendientes, EIPD bloqueada.

## Pausa solicitada y reanudación — 25/10/2026

Usuario solicita detener el trabajo por unas horas, registrar avance y próximos pasos,
y autoriza commit/push de la integración y este registro. Rama de continuidad:
`feature/navegacion-servidor`, base publicada de maqueta `6612076`.
Publicación del presente bloque autorizada; comprobar HEAD remoto y CI al retomar.
No confundir push con merge o despliegue: ninguno está autorizado en este cierre.

Leer primero [estado y guion conectado](project/navegacion-servidor.md), después
[checklist de maqueta](project/maqueta-navegacion-integral.md),
[checklist de licitud](project/m3-t1-checklist-recorrido-licitud.md) y
[backlog](backlog.md). Los bloques fechados anteriores conservan evidencia histórica;
este punto de continuidad prevalece sobre sus menciones de aceptación/publicación pendientes.

Retomar con sesión habitual en `/dashboard/trabajo`, comprobar servicios locales y
seleccionar organización/RAT/finalidad/evaluación existentes. No asumir el contexto
de otra ventana, no crear duplicados y no recargar ediciones pendientes para probar.
Seguir el checklist conectado: persistencia/aplicabilidad y luego documentos, anexos,
resoluciones, revisiones/decisiones/facultades, historial y descargas. Registrar cada
resultado asistido y hallazgo antes de cerrar NAV-UX-002/003/004. NAV-UX-005,
LIC-FORM-001 y demás pendientes no quedan resueltos por la integración.
Trabajo funcional detenido tras publicación; sin tareas programadas ni cambios adicionales.

## Entrada y limites

Participan usuario, ChatGPT/Codex y Deepseek. El usuario incorporó a Claude como
revisor puntual de navegación: aportó informe de solo lectura y propuesta HTML.
Codex valida e implementa; esto no delega operación, permisos ni publicación a Claude.
Leer AGENTS.md y docs/ai/handoff-contract.md. Para una tarea acotada, leer solo
su paquete y los ADR relevantes, no toda la historia de status.md.
EIPD bloqueada; datos ficticios; sin merge/despliegue. Credenciales nunca via chat.

## Estado operativo

Base verificada para preparar este contrato: 39dfad5, rama
feature/m3-t1-licitud-persistencia. CI 38819932076 success, comprobada por Codex
via GitHub Actions 2026-10-15: 4454 backend aprobadas, 1 omitida; frontend e
integrada aprobados. Esta observacion es un snapshot, no el HEAD perpetuo.
Antes de transferir, generar scripts/handoff.py state --remote: ese resultado
identifica el HEAD exacto de la tarea. Una CI anterior no prueba un commit nuevo.

## Bloque funcional vigente — producto

25/10, integración local de navegación en rama feature/navegacion-servidor, base
6612076 (ya publicado con aceptación de maqueta). /dashboard y /dashboard/trabajo
usan módulos/API reales y contexto autorizado por organización/RAT/serie/evaluación;
50 preguntas, borradores por contexto, paneles móviles, historial y salida protegida.
Aplicabilidad independiente persistida append-only; migración f6a24c8e9102 aplicada
primero aislada y después en desarrollo local, sin pérdida/inserción de expedientes.
1.145 runner EIPD + 194 API aprobadas; 55 UI con una captura opcional omitida,
batería conectada ampliada de 10, recorrido Chromium/API/PostgreSQL real y build
aprobados; tipos/ESLint correctos. [Contrato, límites y prueba](project/navegacion-servidor.md).
Aceptación asistida conectada y CI remota pendientes. Publicación de la integración
autorizada por el usuario en el cierre de pausa del 25/10. No hay sincronización automática entre ventanas ni cambio de snapshot
RAT implícito; NAV-UX-005 y LIC-FORM-001 siguen abiertos. EIPD/datos reales bloqueados.

24/10, aceptación asistida: usuario confirma OK navegación de la maqueta y cierres
móviles; aclara que Escape vuelve al formulario y clic exterior es fondo sombreado.
Aprueba commit/push de resultados y solicita integrar navegación al servidor.
Documentos/anexos/resoluciones/historial/descargas se probarán tras conexión.
Las menciones siguientes a aceptación pendiente son antecedentes superados por
este recorrido; no se declara aceptado el producto conectado ni habilitada EIPD.

Incidencia móvil de cierre persistente comunicada por usuario en ambos paneles:
solución local actual reemplaza diálogos nativos por PrototypeDrawer con portal,
fondo explícito, Escape/clic exterior, foco confinado y fondo inert. 30 Chromium
incluidas capturas y tipos/ESLint aprobados. Falta validar en Edge del usuario;
los ajustes previos de eventos no resolvieron su reporte. Sin commit/push nuevo.

24/10, prueba asistida: usuario confirma borradores/guardados de riesgos y medidas,
retirada/restauración EIPD sin pérdida, independencia infancia/EIPD y separación
entre evaluaciones. Solicita Secciones junto a Menú con panel lateral móvil:
implementado localmente, selección abre formulario y cierra panel, Escape/Cerrar
restauran foco; 29 Chromium incluidas capturas, tipos/ESLint aprobados. Validación
asistida del panel y publicación pendientes. NAV-UX-005 registra alcance mixto
adultos/hijos para desarrollo posterior, sin modificar la restricción del ejemplo.

24/10, ajuste posterior: aplicabilidad independiente de EIPD e infancia. Bases de
licitud abre Determinar aplicabilidad; estado Corresponde guardado con fundamento
habilita su menú de completar. Pendiente/No corresponde/Información insuficiente
no habilitan edición. Datos previos conservados, filtros también en historial,
Continuar y enlaces. No clasificador jurídico ni cambios de servidor. 29 Chromium,
tipos/ESLint aprobados; [contrato y prueba](project/maqueta-aplicabilidad.md).
Validación asistida y publicación de este ajuste pendientes.

24/10: usuario aprueba propuesta de Claude; rediseño de maqueta sobre base a9d3ab4,
rama feature/maqueta-navegacion-review. Menú oscuro, contexto Cambiar con confirmación,
agrupación por intención, historial Atrás/Adelante, recuerdo por módulo/evaluación,
Continuar real, salida protegida y cajón/ubicación móvil. Formularios y bloqueos
conservados. [Respuesta hallazgo por hallazgo y oportunidades](project/maqueta-revision-claude.md).
25 Chromium (incluidas capturas), tipos/ESLint aprobados localmente; revisión
asistida y CI remota pendientes. Lo siguiente describe el antecedente de la maqueta.

Maqueta integral NAV-UX-001 en `/dashboard/maqueta`: Panel principal y seis módulos,
menú principal izquierdo y opciones superiores por módulo según bosquejo del usuario,
submenús por clic/teclado y formularios centrales. Selección explícita de tratamiento,
finalidad y evaluación: dos tratamientos, tres finalidades y cuatro evaluaciones
ficticias con borradores/guardados/anexos separados; adopción conectada NAV-UX-002 pendiente,
Mi organización con nombre/RUT/rubro/tamaño, Documentos y Carpeta de evidencias
marcados Próximamente. Guardado en memoria y consultas/ventanas de detalle. Accesos desde dashboard y
licitud. [Contrato y guion de prueba](project/maqueta-navegacion-integral.md).
Ajuste asistido: menú principal persistente también en ventana estrecha al bajar
por formularios; 17 pruebas locales aprobadas, captura opcional omitida, tipos/lint
aprobados. Cuestionario completo de 50 preguntas requerido para integración;
campos actuales del diagnóstico son ilustrativos. CI del ajuste no verificada.
No sustituye producto ni implementa consentimientos/LIA completos; validación
asistida del diseño y adopción pendientes. Recargar reinicia la demostración.

Pendiente LIC-UX-013: consulta del residual por riesgo junto con medidas, dimensión,
eficacia, verificación y respaldos. Alcance y criterios detallados en [backlog](backlog.md);
registrado para desarrollo posterior, sin cambios de producto. Preservar procedencia
y revisión histórica; no atribuir reducciones individuales no evaluadas.

Pendiente LIC-FORM-001: formularios completos de consentimiento/LIA. Originales Excel
aportados y 50 preguntas cotejadas; servidor existente no equivale a UI completa.
Para retomar leer [contrato de implementación](project/m3-t1-consentimiento-lia-implementacion.md)
y [auditoría de cobertura](project/m3-t1-consentimiento-lia-cobertura.md). Desarrollo
no iniciado en este bloque documental; preservación/versionado/evidencias requieren
las decisiones indicadas. Usuario pidió registro detallado para implementación posterior.

Bloque de riesgos/anexos implementado: metodología interna de cuatro niveles,
inherente/residual previsto/actual, controles fundamentados y respaldo PDF/TXT
versionado. Revisar documentos reúne RAT, licitud/LIA y EIPD. Preparación infancia
oculta en adultos; consulta de autoridad condicional y filas vacías corregidas.
Migración e67a4b829c10 en pruebas y desarrollo local; 38 tablas previas intactas.
Pruebas dirigidas, tipos/lint/formato y recorrido real aislado aprobados; detalle en
[contrato vigente](project/m3-t1-riesgos-anexos.md). Pendiente validación asistida
ampliada y revisión/adopción formal EIPD general/RAT-LIA; EIPD/datos reales bloqueados.
CI base 6bf7870 aprobada: 4518 backend (2 omitidas), 211 frontend y 2 integradas.
Bloque UX del 22/10 implementado: LIC-UX-005 a 012, siete pasos EIPD con valoración
como paso 4, tablas completas por riesgo, tipografía y avisos cercanos al guardado.
34 Chromium y 4 aisladas de recorrido/listado aprobadas; tipos/lint/formato y
capturas escritorio/móvil revisados. Checklist consolida el recorrido asistido:
[estado vigente](project/m3-t1-checklist-recorrido-licitud.md).
Pendiente revisión visual del usuario y CI del nuevo bloque; metodología configurable
y auditoría completa requieren diseño separado. EIPD bloqueada; sin merge/despliegue.

19/10: recorrido Bases de Licitud integrado al servidor: cuatro pestanas,
secciones cortas, borradores conservados al navegar y diagnosticos/descargas
invalidados tras guardar. Preparacion de resolucion infancia con vista previa,
lectura ficticia y proteccion de reemplazo; revision/decision/facultades separadas.
EIPD general: borrador con seis secciones, riesgos/medidas/evidencias/seguimiento,
guardado y reapertura; copia guardada consultable sin confundirla con resolucion.
71 Chromium afectados, 4 API/integracion con PostgreSQL aislado, tipos/lint/formato;
SQL confirma EIPD/LIA persistidos y confirmed_at=null; vista movil/escritorio revisada.
No nuevos endpoints, migraciones, permisos ni opt-in local. EIPD/datos reales
bloqueados, sin merge/despliegue. CI exacta del nuevo commit por consultar.
Pendientes: validacion asistida conectada; revision EIPD general/adopcion RAT-LIA
y trazabilidad estructurada requieren sus contratos; cierre juridico/operativo
no declarado. LIC-UX-004 abierto. Contrato: project/m3-t1-licitud-experiencia.md.

18/10: recorrido manual ficticio de Bases de licitud cerrado: clientes,
trabajadores e infancia; guardado/reapertura, dos resoluciones, revisiones negativas,
decision documental y grant/revocacion. Decision conservada, nuevas decisiones
bloqueadas en UI tras recarga; JSON con faculty_current=false y EIPD/datos reales
bloqueados. Escritura temporal local restituida a false y override retirado.
CI funcional de 33039d3 success (39040075836), Handoff tambien success.
No hay pruebas pendientes del recorrido acotado; pendientes de producto/operacion
no equivalen a aprobacion para datos reales. Evidencia y limites en
project/m3-t1-recorrido-frontend.md; hallazgos en backlog.md. Sin merge/despliegue.

16/10: piloto sigue ficticio. Usuario define escenario [FICTICIA] Comercial Piloto
Andes SpA / [FICTICIA] Persona Facultada Piloto, contactos example.invalid y RUT
simulados. V2 genera actas descargables HTML/JSON con marca ACTA DE PRUEBA,
DATOS FICTICIOS, SIN VALOR JURIDICO; referencias SIMULADA- exigidas en servidor.
Revision pendiente/no realizada por defecto; cualquier otra decision es simulada.
Escenario no sustituye identidad tecnica de sesion, no registra aceptacion real
ni cierra gates. V1 e historiales conservados, datos reales y EIPD bloqueados.
20 backend/guardas, 13 UI/cliente y una integrada real aprobadas; tipos/lint/formato.
Docker/WSL restablecido; CI previa b229fb3 aprobada. Verificar nuevo HEAD/CI.
[Contrato y evidencia](project/m3-t1-piloto-preparacion.md).
Pendientes reales: empresa/actas/facultades, revision humana y controles de piloto.
Piloto poblado local validado: clientes/trabajadores con LIA borrador e infancia
con dos resoluciones, dos revisiones negativas, dos eventos documentales y
otorgamiento/revocacion de facultades (ocho registros historicos). Restauracion
de 39 tablas conserva conteos/checksums/politicas y lecturas API como app_user;
aislamiento, facultad revocada y EIPD bloqueada comprobados en la copia.
Ejecutor fijo: backend `python -m scripts.run_populated_pilot`; limpia solo fixtures
y copia propias. Evidencia: project/pilot-evidence/populated-history-restore-20261016.json.
41 pruebas dirigidas y recorrido local poblado aprobados; CI del previo 8a8903f
aprobada. Comprobar candidato por HEAD. No certifica produccion ni backup externo.
Sin migraciones, provision de identidades, merge o despliegue.

## Proxima transferencia

Estado: DS-001 a DS-005 terminados. DS-005 agrega reordenacion de evidencia;
25 UI aprobadas (7 independientes), tipos/lint/formato aprobados tras Prettier
final de Codex. El bucle Deepseek se detuvo tras tres fallos de formato;
no acredita autonomia completa. Ver docs/ai/pilot-results.md y results/DS-005.json.
Permisos acotados, no agente general; no reenviar pilotos terminados.
BENCH-001: tres pares pequenos, 5 puntos cuota local vs 22 delegados; no ahorro
observado, cuota compartida y par 2 contaminado. No extrapolar. Informe:
docs/ai/benchmarks/BENCH-001.md. 18 regresiones nuevas, comando CI 91 aprobadas.

Desde raiz y checkout limpio:

    python3 scripts/handoff.py state --remote
    python3 scripts/handoff.py packet --task docs/ai/tasks/DS-001.json --remote > /tmp/CumpleIA-DS-001.json

No hay bloque Deepseek activo. Decision: seleccionar bloques coherentes caso a
caso; microtareas directas en Codex. Ejecutor consolidado y validado localmente
sin API: 36 unitarias + 25 Chromium. Guia: docs/ai/deepseek-automation.md.

Modalidad recomendada por preferencia del usuario: lanzador local + API,
`python3 scripts/deepseek_run.py ID`. Por defecto prepara sin gasto. Clave dedicada
y servicio verificados; trece generaciones pagadas entre pilotos y BENCH-001. Nuevas tareas requieren
contrato y autorizacion de gasto; no hay lote mensual autorizado. Ver
docs/ai/deepseek-automation.md.

Fallback manual: copiar el JSON completo a Deepseek y pedir diff unificado + reporte, sin aplicar.
Al volver, guardar el diff fuera del checkout y comprobarlo usando el HEAD del
paquete (nunca sustituirlo por el HEAD actual para eludir una base obsoleta):

    python3 scripts/handoff.py check --task docs/ai/tasks/DS-001.json --base HEAD_DEL_PAQUETE --patch /tmp/DS-001.patch

El check no aplica el parche ni aprueba pruebas. Codex revisa, aplica y ejecuta
los checks del contrato. Solo tras aceptar el bloque se hace commit/push bajo
la autorizacion del usuario. Mantener un unico responsable por tarea.

## Evidencia y continuidad

Tabla de verificacion, resultados del ensayo local y criterios del piloto:
docs/ai/pilot-results.md. Accesos: docs/ai/access-matrix.md.
Los handoffs fechados previos permanecen como antecedentes para preservar enlaces.
Nuevos cierres historicos, solo cuando aporten una decision o evidencia necesaria,
van a docs/archive/. No duplicar el historial en este archivo.

### Seguimiento de teclado del Paso 1 — 30/10/2026

- El usuario validó el recorrido de archivo inválido y sustitución por un archivo válido, conservando los campos del anexo.
- Informó que la barra espaciadora no abría/cerraba «Vínculos opcionales con riesgos y medidas». La prueba aislada con comportamiento nativo no reproducía el fallo; se añadió activación explícita con Espacio, cancelando la acción nativa para evitar un doble cambio y descartando la repetición al mantener la tecla pulsada.
- Se amplió la prueba para llegar con Tab desde «Sección relacionada», abrir/cerrar tres veces, mantener Espacio, usar Enter y clic, y conservar el código R1. Comprobado en 1280, 390 y 320 píxeles.
- Falta la validación manual del usuario en su navegador con este ajuste. No se considera una comprobación con lector de pantalla. Sin commit ni push de este paso todavía.
