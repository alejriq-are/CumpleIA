# Navegación conectada al servidor

## Paso 1 — validación asistida y publicación autorizada, 30/10/2026

El usuario confirmó «recorrido OK» tras el ajuste de Espacio en «Vínculos opcionales con riesgos y medidas» y autorizó commit/push. Quedan aceptados el recorrido de archivo inválido → archivo válido con conservación de campos y la apertura/cierre del bloque con teclado. Las notas anteriores de aceptación/autorización pendiente quedan superadas en este alcance.

Verificación técnica: 42 pruebas Chromium aprobadas en assessment-support y licitud-workspace con respuestas controladas y estilos de la aplicación; tipos y ESLint aprobados. LIC-UX-014 queda resuelto en este alcance. LIC-UX-015 conserva pendientes fuera de los dos desplegables del panel. La validación manual con lector de pantalla continúa pendiente; no se atribuye una subida real nueva de anexo a estas pruebas.

Se publica en `feature/anexos-estado-acciones`. Sin merge ni despliegue; confirmación/activación EIPD bloqueadas. Se excluyen los cambios preexistentes de `frontend/next-env.d.ts` y `outputs/`.

Referencia funcional: [ciclo documental de la EIPD](ciclo-documental-eipd.md). Explica borrador, versión de evaluación, revisiones de aplicabilidad, resoluciones, revisión y decisión; distingue lo implementado del circuito previsto sin habilitar confirmación ni activación.

Fecha: 25/10/2026. Base: 6612076. Rama: feature/navegacion-servidor.

Solicitud: adoptar la navegación de la maqueta aceptada en los módulos conectados.
Reutilizar formularios RAT, Autodiagnóstico (catálogo completo del servidor),
licitud, infancia, riesgos/anexos y organización, sin reemplazarlos por ejemplos.
Contexto explícito autorizado: organización, tratamiento, finalidad y evaluación.
Conservar borradores durante la visita por contexto; recuperar guardados desde API
al recargar. No sincronizar la selección de contexto entre ventanas. No guardar
contenido sensible en localStorage/sessionStorage. Conflictos no sobrescriben historial.

Aplicabilidad documental independiente y persistente por evaluación, con fundamento,
autoría y revisiones append-only; no es un clasificador jurídico ni autorización.
Al cambiar el contexto RAT asociado exigir revisión de la determinación anterior.
Conservar consultas de documentos anteriores y controles de servidor existentes.
No habilitar confirmación/activación EIPD; solo pruebas ficticias, sin merge/despliegue.

Aceptación: navegación escritorio/móvil/teclado, aislamiento entre contextos,
retorno con borradores, carga/errores/permisos, guardado y reapertura, aplicabilidad
condicional conservando antecedentes, 50 preguntas originales, anexos/resoluciones
con contratos actuales. Pruebas asistidas de documentos/historial/descargas diferidas
por usuario hasta integración. Las capacidades faltantes no se simulan como guardadas.


## Resultado implementado — 25/10/2026

- `/dashboard` y `/dashboard/trabajo` presentan el espacio conectado autenticado.
  Las rutas anteriores de Autodiagnóstico, RAT, creación y licitud redirigen al
  contexto correspondiente; la creación de organización sin membresías y el acceso
  administrativo especial anterior se conservan. Sin ampliación de permisos.
- Menú principal, Secciones junto a Menú, paneles laterales con Escape/clic exterior,
  foco confinado y retorno de foco. Opciones de escritorio por tarea; ubicación,
  contexto y nombres visibles. Continuar y Atrás/Adelante recuerdan rutas de visita.
- Contexto seleccionado desde API: membresía autorizada, tratamiento y serie de
  finalidad con sus versiones. El listado expone `series_id` estable; no se deduce
  identidad desde textos ni se crean evaluaciones al cambiar una selección.
- El selector espera validación antes de aplicar. Cancelar o navegar invalida
  respuestas atrasadas. Las respuestas de aplicabilidad se comprueban por tenant,
  tratamiento, evaluación, revisión y bloqueos; no se usan respuestas cacheadas.
- Formularios reales montados por contexto conservan borradores durante la visita.
  Recargar recupera lo guardado en el servidor, no ediciones pendientes. Hay aviso
  de cambios pendientes y confirmación para cerrar sesión o salir hacia la maqueta.
- Autodiagnóstico reutiliza las 50 preguntas/10 secciones del catálogo real y sus
  respuestas API, no los campos ilustrativos. Pertenece a la organización, no a una
  evaluación de licitud. RAT y organización reutilizan sus editores existentes.
- Bases de licitud reutiliza AssessmentFlow: base/LIA, documento EIPD de siete pasos,
  valoración, anexos, infancia, preparación, consulta y revisiones/historial actuales.
  Las brechas de formularios completos de consentimiento/LIA siguen en LIC-FORM-001.
- Determinar aplicabilidad guarda decisiones independientes, fundamento y autoría
  con revisiones append-only en el soporte documental existente. EIPD e infancia
  no se habilitan por seleccionar un valor sin guardar. Negativas y pendientes
  conservan los documentos anteriores consultables; los editores se ocultan.
- GET/POST `.../assessments/{assessment_id}/applicability`: mismos permisos,
  suscripción, tenant y rol runtime que soporte documental. Solo pruebas ficticias.
  Control de revisión esperada, hash del contexto guardado, request_id idempotente
  y bloqueo por serie. Un conflicto conserva el formulario y permite actualizar el
  estado guardado sin descartar el borrador. No modifica la evaluación ni sus hashes.
- La asociación se revisa al cambiar el snapshot RAT de la evaluación. Editar el
  RAT en vivo no sustituye automáticamente ese snapshot ni es una decisión legal.
  La actualización guiada de alcance mixto continúa como NAV-UX-005; no se afirma
  implementado el flujo completo por este cambio de navegación.

## Persistencia y operación local

Migración append-only f6a24c8e9102 sobre e67a4b829c10: extiende los tipos permitidos
por las restricciones de `assessment_support_records` para determinaciones sin
contenido binario. Conserva políticas RLS, FK compuesta, roles y privilegios de solo
SELECT/INSERT; no permite UPDATE/DELETE ni borra historial. Aplicada primero en la
base aislada y después en desarrollo local `cumpleia`, comprobando mismo número de
evaluaciones y registros documentales antes/después. No se insertaron fixtures en
la base de desarrollo. No hay servicios, dependencias o credenciales nuevas.

Backend local health 200 y rutas GET/POST presentes en OpenAPI. Login 200;
/dashboard, /dashboard/trabajo, /dashboard/rat y maqueta sin sesión redirigen a
/login (307). La sesión personal no se inspeccionó ni se utilizó para las pruebas.
Las ventanas conservan selección de contexto independiente; no hay sincronización
en tiempo real de formularios abiertos. Actualizar estado o recargar consulta el
servidor, con control de concurrencia para las determinaciones. Confirmación y
activación EIPD permanecen bloqueadas. Sin merge ni despliegue remoto.

## Evidencia

- 1.145 pruebas del runner EIPD aprobadas en base aislada.
- 194 pruebas de las APIs de licitud/Autodiagnóstico aprobadas, incluido catálogo
  real de 50 preguntas y 10 secciones. No se suman a las anteriores como cobertura
  única; son ejecuciones de conjuntos declarados.
- 55 pruebas de interfaz y regresión aprobadas; una captura opcional omitida en
  esa corrida (maqueta/licitud/primeras seis conectadas).
- Batería conectada ampliada: 10 Chromium, tipos y ESLint aprobados.
- Recorrido Chromium → API real → PostgreSQL aislado aprobado: guardar ambas
  determinaciones y fundamento, recargar, recuperar contexto/datos y abrir infancia.
  Autenticación sintética de fixture; no login personal ni autorización jurídica.
- Compilación de producción en copia temporal con configuración ficticia aprobada.
  Capturas escritorio/móvil revisadas en outputs/navegacion-servidor; sin sobreescribir
  evidencia de la maqueta. Pruebas conectadas incorporadas a CI, ejecución remota pendiente.

## Prueba asistida siguiente

1. Abrir `/dashboard` con la sesión habitual. Verificar aviso Espacio conectado.
2. Cambiar contexto: organización → RAT → finalidad → evaluación existente. Si aún
   no existe evaluación, usar Bases de licitud → Preparar → Evaluaciones y creación
   de borrador; requiere permisos y datos ficticios.
3. Determinar aplicabilidad, guardar y comprobar los accesos correspondientes.
4. Editar/guardar, cambiar módulo y recargar para verificar persistencia real.
5. Probar los recorridos diferidos por usuario: documentos guardados, anexos,
   resoluciones, historial y descargas, en cada contexto y con los roles permitidos.

La aceptación previa corresponde a la maqueta. La aceptación asistida del espacio
conectado y de los recorridos diferidos sigue pendiente. Publicación de esta rama autorizada por el usuario al pausar el 25/10; verificar
HEAD remoto y CI al retomar. 6612076 ya publicó resultados aceptados de la maqueta.

## Checklist para reanudar

Pausa solicitada el 25/10/2026 por unas horas. No hay trabajo funcional programado.
Commit/push autorizado de integración y registro; sin merge ni despliegue remoto.

1. [ ] Comprobar rama `feature/navegacion-servidor`, HEAD/estado local/remoto y CI
   exacta del commit. Si los servicios locales no están disponibles, iniciarlos con
   su configuración existente; no crear credenciales ni cambiar permisos.
2. [ ] Abrir `/dashboard/trabajo` con sesión habitual. Elegir organización → RAT →
   finalidad/serie → evaluación existente y confirmar identidad/versión. No crear
   duplicados ni asumir que dos ventanas deban compartir su selección.
3. [ ] Verificar las 50 preguntas/10 secciones del Autodiagnóstico organizacional,
   retorno con borrador y lectura del guardado. Distinguirlo de licitud por evaluación.
4. [ ] Guardar aplicabilidad EIPD/infancia con fundamentos, comprobar menús condicionales,
   retorno entre módulos y recuperación tras recarga de valores guardados. Antes de
   recargar, guardar o descartar conscientemente los cambios pendientes.
5. [ ] Consultar documentos guardados, base/LIA y EIPD en la evaluación correcta;
   distinguir borrador, guardado y revisión histórica. No sustituir el snapshot RAT
   implícitamente ni dar por resueltos los formularios LIC-FORM-001.
6. [ ] Anexos: PDF/TXT ficticio válido, rechazo CSV/vacío/tamaño, conservación de campos,
   vínculos opcionales R/M, versiones y descarga íntegra de la versión seleccionada.
   Registrar si persiste LIC-UX-014; no declarar corregido por pruebas de maqueta.
7. [ ] Infancia cuando corresponda: preparar resolución, cancelar copia/vista previa
   conservando borrador; registrar solo prueba deliberada, consultar originales y
   sucesor sin heredar revisión/decisión. Comprobar contexto antes de cada registro.
8. [ ] Revisiones, decisiones y facultades: historial consultable y permisos vigentes;
   revocación bloquea nuevas decisiones sin borrar antecedentes. No conceder facultades
   solo para probar navegación ni activar EIPD.
9. [ ] Historial/descargas: identidad, versión, contenido y asociaciones correctas;
   separación entre evaluaciones y organizaciones; bloqueos conservados. Contrastar
   archivos con lo guardado, no con cambios pendientes del formulario.
10. [ ] Escritorio/móvil/teclado: Menú y Secciones accesibles al bajar, Escape/Cerrar
    y clic en fondo sombreado cierran panel y devuelven foco; selección abre área de
    trabajo sin desborde. Atrás/Adelante, cambio de contexto y salida con borrador.
11. [ ] Registrar resultado por paso (OK, fallo o no probado), contexto ficticio y
    evidencia; actualizar checklist y backlog. Cerrar solo criterios efectivamente
    verificados. Resolver hallazgos acotados antes de nueva publicación autorizada.

Referencias: [maqueta aceptada](maqueta-navegacion-integral.md),
[recorrido histórico de licitud](m3-t1-checklist-recorrido-licitud.md),
[backlog](../backlog.md). NAV-UX-005 y LIC-FORM-001 siguen pendientes; no abordar
nuevas funciones por el solo hecho de reanudar estas pruebas.

## Reanudación asistida — 25/10/2026

Usuario confirma frontend/backend iniciados y solicita retomar este checklist.
HEAD local/remoto comprobado: db6f0d38e4e12bdffe5007ecb321787f831e2186,
rama feature/navegacion-servidor. Único cambio local observado al inicio:
frontend/next-env.d.ts regenerado por Next.js; no se revierte ni publica como ajuste funcional.
GitHub Handoff protocol 40194470401 completado success para este HEAD.
No aparece ejecución de CI funcional para este commit en la consulta: no se declara
CI funcional remota aprobada. Se mantienen las validaciones locales documentadas.
Recorrido asistido conectado pendiente de resultados: comenzar por selección y
confirmación de contexto existente (paso 2), sin crear evaluaciones duplicadas.

## Correcciones de revisión externa — lote 1 (C1), 25/10/2026

Usuario autoriza únicamente comenzar el lote 1 del checklist propuesto tras contrastar
el informe de Claude con el repositorio. Claude aporta hipótesis como revisor externo;
no participa en el circuito de ejecución. Rama fix/navegacion-carga-recuperacion,
base db6f0d3. Los lotes posteriores no se implementan en este bloque.

- [x] Fallo reproducido antes del parche: enlace directo a EIPD con consulta retenida
  no muestra estado de carga en el área de trabajo.
- [x] Carga y error de aplicabilidad visibles fuera del formulario oculto en EIPD,
  infancia y preparación. Reintentar consulta o ir a Determinar aplicabilidad.
- [x] Carga del contexto visible fuera del selector al restaurar enlace/historial;
  error de apertura permite reintentar la validación autorizada.
- [x] Formularios conservados montados; reintento solo consulta, sin guardar,
  descartar borradores ni relajar permisos/habilitación por determinación guardada.
- [x] 15 pruebas Chromium conectadas aprobadas (10 previas + 5 nuevas). Tres casos
  de enlaces condicionales repetidos en escritorio/390/320 px, sin desborde.
  Tipos, ESLint y formato aprobados. Capturas de carga/error ficticios revisadas
  en outputs/navegacion-lote1 del espacio de trabajo de esta conversación.
- [ ] Validación asistida con el usuario en su navegador, antes de cerrar el lote.
- [ ] Commit/push de esta corrección: no realizado ni inferido de la autorización
  anterior de publicación de la integración.

Guion asistido: usar evaluación ficticia existente con EIPD habilitada por guardado;
abrir un paso de EIPD, escribir una marca sin guardar, cambiar a Base y volver para
confirmar conservación. Para el error se puede bloquear temporalmente únicamente
la solicitud GET de aplicabilidad mediante las herramientas del navegador y abrir
el mismo enlace en otra pestaña sin borradores; debe aparecer mensaje y ambas acciones.
Retirar el bloqueo y pulsar Reintentar consulta: se abre el destino habilitado.
No cortar ni modificar el backend/base, no guardar revisiones solo para probar UI,
y no recargar la pestaña con el borrador pendiente. La demora y el error ya están
cubiertos automáticamente con respuestas ficticias controladas; el ensayo manual
se guía paso a paso según las herramientas disponibles del usuario.

Límites: solo presentación/recuperación de lecturas del hallazgo C1. Reubicaciones
explicadas (C8), cabecera contextual (C2), permisos explicados (C4), estado guardado
(C9), navegación/teclado y demás lotes siguen pendientes. Sin cambios de API, DB,
migraciones, autorización, confirmación/activación EIPD, merge o despliegue.

### Validación asistida del lote 1 — conservación confirmada

Usuario confirma que escribió texto de prueba sin guardar en EIPD, cambió a Base y
fundamento y volvió al mismo campo: el texto se conserva (OK). La marca corresponde
al texto, no al indicador de estado del menú. No se afirma guardado en servidor.
Pendiente comprobar juntos error visible y reintento; el lote no se cierra todavía.

### Ensayo asistido de desconexión y recuperación — versión conectada

Capturas fdbc984f y f4a2e8d6: /dashboard/trabajo, CumpleIA Demo / Gestión de clientes /
Coordinar citas / versión 1 borrador; determinaciones pendientes, historial vacío.
Offline + Actualizar estado produce error visible; No throttling + nueva consulta
retira el error y GET applicability responde 200. No acredita guardado ni ensayo de
error dentro de EIPD/infancia condicional; esos casos tienen cobertura automática.
La prueba anterior comunicada como conservación OK precedió a la identificación de
/dashboard/maqueta en capturas: no se da por aceptada su equivalente conectado hasta
repetirlo allí. Se mantiene la evidencia histórica y se aclara su alcance.
Hallazgo asistido: mensaje técnico Failed to fetch. Se sustituye en lecturas de
aplicabilidad/apertura por ayuda de conexión en español, preservando mensajes de
permisos/conflictos del servidor. Prueba controlada adicional de desconexión real de
la solicitud verifica traducción, recuperación y borrador sin escrituras.

### Hallazgo asistido adicional — acción de consulta poco visible

Usuario solicita anotar que «Actualizar estado guardado sin descartar el borrador»
no se distingue del contenido y no explica su efecto (captura c70d9387).
Registrado en backlog bajo C9/LIC-UX-015, relacionado con lote 5. Propuesta:
«Consultar última determinación guardada», con ayuda y diferenciación de Guardar.
Solo registro: no se cambia la interfaz ni se da por cerrado ese hallazgo en lote 1.

### Duplicación de pasos confirmada en prueba asistida

Captura 84302033 muestra menú Completar EIPD y los siete botones EipdSteps centrales
con destinos equivalentes. Registrado en backlog para lote 8: conservar navegación
superior/Secciones y ocultar lista central solo cuando exista navegación externa.
No implementado en lote 1; no acredita todavía resultado de error/reintento dentro de EIPD.

### Recuperación condicional con sesión no disponible — pendiente

Capturas 8ab64936/ec1912a9/5f207204: usuario observa error visible y ambas acciones en
EIPD, pero Reintentar no recupera el formulario; mensaje «Tu sesión expiró» persiste
también con No throttling. Ir a Determinar aplicabilidad muestra el formulario ya
montado, no acredita consulta exitosa. El lote 1 no se acepta todavía.
Inspección: sessionToken agrupa error de getSession y sesión ausente bajo el mismo
texto; no permite concluir desde la captura si es desconexión del proveedor o sesión
inválida. No se leen cookies/tokens ni se alteran permisos. Próximo paso asistido:
iniciar sesión en otra pestaña del mismo navegador/perfil y reintentar en la pestaña
original sin recargar para conservar borradores; comprobar resultado y texto pendiente.

### Cierre asistido del recorrido C1 — recuperación y borrador confirmados

Usuario confirma finalmente: tras iniciar sesión en otra pestaña del mismo navegador,
volver a la pestaña original /dashboard/trabajo y pulsar Reintentar consulta, reaparece
el formulario EIPD y se conserva el texto pendiente en Notas del borrador EIPD (opcional).
La pestaña nueva no contenía ese borrador: conservación por pestaña, no sincronización.
Quedan comprobados con el usuario error visible y acciones en sección EIPD, retorno
a Determinar aplicabilidad y recuperación de EIPD conservando notas tras restablecer
sesión. El guardado ficticio previo habilitó el menú; recuperar no guardó las notas.
Lote 1 C1: implementación y recorrido asistido completados con este alcance; pruebas
automáticas del último bloque: 16 Chromium, tipos y ESLint aprobados. Sin commit/push.
No equivale a validar manualmente todos los casos de infancia/preparación, cubiertos
en pruebas controladas, ni a dar por implementados los lotes restantes.

Seguimiento separado: sessionToken usa el mismo aviso para error de lectura de sesión
y sesión ausente. La recuperación autenticada funcionó; no se atribuye a una falla del
botón ni se declara resuelta la distinción de causas/mensaje de autenticación.

## Correcciones de revisión externa — lote 2 (C2/C14), 25/10/2026

Usuario autoriza commit/push del lote 1 y continuar con lote 2. Lote 1 publicado
como 465a94c515db4245b5a7b9d89534fc76c6dee0ef en origin/fix/navegacion-carga-recuperacion,
HEAD remoto verificado. Se excluyó frontend/next-env.d.ts generado por Next.js.
Lote 2 en fix/navegacion-contexto-modulo, basado en ese commit; sin commit/push nuevo.

- [x] Cabecera según ámbito: Panel, Autodiagnóstico y Mi organización muestran solo
  organización; RAT añade tratamiento; Bases de licitud añade finalidad/evaluación,
  versión y estado. Etiquetas explícitas; no se borra contexto de navegación recordado.
- [x] Continuar identifica sección y contexto propio del destino recordado. En licitud
  incluye organización, tratamiento, finalidad/evaluación y versión/estado; diagnóstico
  muestra organización sin atribuir respuestas a una evaluación de licitud.
- [x] Sin cambios en rutas, permisos, formularios, persistencia ni memoria de retorno;
  el selector de contexto permanece igual (su simplificación corresponde a otro lote).
- [x] Prueba previa reprodujo Continuar sin contexto. Veinte Chromium conectadas
  aprobadas (16 existentes + 4 nuevas): retorno entre módulos con borrador, encabezado
  por ámbito, dos versiones y Continuar, diagnóstico por organización y ausencia de
  escrituras en los cuatro casos nuevos. Tipos, ESLint y formato aprobados.
- [x] Cuatro casos repetidos con capturas en escritorio/390/320, sin desborde;
  imágenes ficticias revisadas en outputs/navegacion-lote2 del espacio de conversación.
- [ ] Validación asistida del lote 2 pendiente; no cerrar todavía C2/C14 como aceptados.

Guion: desde la evaluación ficticia existente con texto pendiente, ir a Autodiagnóstico
y Mi organización; comprobar que cabecera solo presenta organización. Ir a RAT:
organización/tratamiento, sin finalidad/version de licitud. Volver a Bases de licitud:
contexto completo y mismo borrador. Ir a Panel desde esa sección: Continuar debe nombrar
sección, tratamiento/finalidad y versión; pulsarlo debe recuperar el mismo formulario.
No guardar marcas de prueba ni recargar borradores solo para comprobar estos cambios.
Lotes 3–9, seguimiento de sesión, botón de consulta y duplicación EIPD continúan pendientes.

### Aceptación asistida del lote 2 — 25/10/2026

Usuario confirma «Todo OK» al ejecutar el guion del lote 2. Capturas ff b193e2
(ffb193e2), 32dafffb y 5ac1eed9: Panel muestra solo organización y Continuar identifica
Tratamiento y alcance EIPD, organización/tratamiento/finalidad y versión 1 borrador;
RAT muestra organización/tratamiento sin finalidad/evaluación; regreso a EIPD conserva
[FICTICIA] Texto pendiente de prueba en Notas del borrador EIPD, con aviso sin guardar.
Autodiagnóstico y Mi organización aceptados por confirmación del usuario, sin captura
individual aportada en este mensaje. Aceptación acotada C2/C14 completada; no acredita
guardado de las notas ni cierre global de NAV-UX-002/003. Lote 2 sigue local, sin commit/push.
Siguiente lote propuesto: 3 (C4), explicación de permisos y requisitos de guardado,
pendiente de indicación para iniciar. Mantener abiertos seguimiento de sesión y otros lotes.

## Correcciones de revisión externa — lote 3 (C4), 25/10/2026

Usuario autoriza commit/push del lote 2 y continuar lote 3. Lote 2 publicado como
9c8632f en origin/fix/navegacion-contexto-modulo; rama de implementación lote 3:
fix/navegacion-permisos-requisitos. Solo explicación de estados de bloqueo; no se
modifican permisos, contratos, sesiones, datos guardados ni requisitos jurídicos.

- [x] Aplicabilidad: motivo visible de solo consulta por rol o editable=false del
  servidor; estados de consulta, guardado y ausencia de determinación explicados.
  Ayuda junto a Guardar enumera fundamentos faltantes y declaración ficticia, se
  actualiza al completar y muestra requisitos completos cuando corresponde.
- [x] Descripciones accesibles asociadas a controles y grupos mediante IDs únicos;
  motivo de edición/solo consulta se muestra una vez, sin repetirlo en el pie.
- [x] RAT y Mi organización: aviso externo al fieldset deshabilitado explica solo
  consulta. Se mantienen roles owner/admin/editor para RAT y owner/admin para organización.
- [x] Contexto: dependencias tratamiento/finalidad/evaluación explicadas; Aplicar
  indica carga, error o evaluación faltante. Conserva selección opcional de solo
  organización o tratamiento; no cambia la condición de habilitación anterior.
- [x] Fallo reproducido antes del parche: Guardar no tenía descripción del requisito
  faltante. Veinticinco Chromium conectadas aprobadas (20 previas + 5 nuevas),
  tipos/ESLint/formato aprobados. Cinco dirigidas repetidas con capturas; ayuda de
  Guardar revisada tras estabilizar repintado de scroll; escritorio y solo consulta
  a 320 px sin desborde. No se suman repeticiones como cobertura única.
- [x] Roles viewer/editor y editable=false comprobados con fixtures del navegador,
  sin crear cuentas, cambiar roles reales ni realizar escrituras en los cinco casos
  nuevos. No se atribuye a estas pruebas un ensayo nuevo de autorización/RLS del backend.
- [ ] Validación asistida del lote 3 pendiente. Sin commit/push del lote 3.

Guion asistido sin guardar: abrir Determinar aplicabilidad en evaluación ficticia
existente con fundamento guardado, dejar declaración desmarcada y comprobar que la
ayuda pide completarla; marcarla para ver requisitos completos y volver a desmarcar.
En Cambiar contexto, conservar tratamiento/finalidad y elegir opción vacía de evaluación:
Aplicar queda bloqueado con explicación; seleccionar versión válida habilita y luego
Cancelar conserva contexto/borradores. No recargar notas pendientes ni crear revisiones
solo para probar presentación. Casos de solo consulta disponibles en capturas de
fixtures; no cambiar permisos reales para la prueba asistida.
Lotes 4–9, clasificación de sesión, botón de consulta y duplicación de pasos siguen
pendientes. Sin ampliación de API/DB ni habilitación de confirmación/activación EIPD.

### Validación asistida parcial del lote 3 — ayuda de Guardar

Usuario confirma «cambia correctamente, OK»: al desmarcar/marcar la declaración de
datos ficticios, la ayuda indica el requisito faltante/completo y el botón cambia
su habilitación con fundamentos completos. No se solicita ni se acredita un guardado
nuevo por esta prueba. Pendiente comprobar explicación de evaluación faltante en
Cambiar contexto; lote 3 aún sin cierre asistido completo ni publicación.

### Aceptación asistida del lote 3 — 25/10/2026

Usuario confirma «todo OK» en el selector: al retirar evaluación manteniendo finalidad,
Aplicar contexto se deshabilita y explica el requisito; seleccionar versión válida lo
habilita y Cancelar mantiene el contexto. Sumado al OK previo de ayuda de Guardar,
completa el guion asistido acordado del lote 3 C4. No se guardaron revisiones como
parte de estas instrucciones. Roles viewer/editor y editable=false cuentan con
pruebas controladas automatizadas, no un ensayo manual con cuentas de otros roles.
Lote 3 validado con ese alcance; sin commit/push nuevo. Próximo lote propuesto: 4,
orientación después de guardar aplicabilidad y explicación de reubicación (C3/C8),
pendiente de instrucción para iniciar. Otros pendientes de backlog no se cierran.

## Correcciones de revisión externa — lote 4 (C3/C8), 25/10/2026

Usuario autoriza commit/push del lote 3 y continuar lote 4. Lote 3 publicado como
0340b0a7c33c88e2b5132daad713f03831c0bc64 en origin/fix/navegacion-permisos-requisitos,
HEAD remoto verificado. Rama local lote 4: fix/navegacion-orientacion-aplicabilidad.
La interrupción por cuota ocurrió antes de escribir cambios de este lote; al reanudar
se comprobó estado y se continuó desde el commit publicado.

- [x] Panel Disponibilidad de formularios junto al resultado de guardado: separa EIPD
  e infancia y presenta su estado guardado, no el selector pendiente. Accesos directos
  Completar cuando corresponde y está asociado; Consultar si el rol/estado es de lectura.
- [x] Pendiente, No corresponde e Información insuficiente explican que el formulario
  no está habilitado y la causa. Sin determinación se distingue de determinación que
  requiere revisión por alcance. No se induce una conclusión positiva obligatoria.
- [x] Acceso a Revisar y decidir para antecedentes previos, si existen, sin retirarlos
  al cambiar aplicabilidad. No se reintroducen entradas deshabilitadas en los menús.
- [x] Al reubicar desde EIPD/infancia/preparación aparece aviso con causa, conservación
  de borradores y consulta de documentos. Indica cambios pendientes si existen en la
  evaluación, sin atribuirlos a un formulario concreto no identificado. Aviso cerrable;
  no persiste al consultar una revisión/estado distinto ni al navegar a otro destino.
- [x] No cambios en habilitación, permisos, API, DB, historial ni sincronización entre
  ventanas: solo una consulta explícita o guardado actualiza el estado de la visita.
  Los borradores permanecen montados y la navegación no crea registros.
- [x] Prueba previa reproduce falta de acceso directo. Batería conectada de 34 aprobada;
  tras añadir el caso sin determinación y aclarar textos, 10 casos dirigidos finales
  aprobados (35 escenarios distintos en total; no sumar repeticiones como cobertura).
  Tipos/ESLint/Prettier aprobados; capturas de resultado y reubicación escritorio,
  390/320 revisadas sin desborde en outputs/navegacion-lote4.
- [x] Casos controlados: cuatro estados para ambos temas, independencia EIPD/infancia,
  valor sin guardar no altera accesos, consulta previa accesible, reubicación desde
  tres destinos, borrador EIPD conservado al restaurar aplicabilidad, alcance
  desasociado y ausencia de determinación. Fixtures, sin escrituras en base operativa.
- [ ] Validación asistida del lote 4 pendiente; no se declara aceptado por usuario.
- [ ] Commit/push lote 4 no realizado. Lotes siguientes siguen pendientes.

Guion asistido inicial sin nuevas revisiones: en /dashboard/trabajo, evaluación ficticia
existente con EIPD Corresponde guardada e infancia Pendiente, abrir Determinar
aplicabilidad y localizar Accesos según la determinación guardada. Debe ofrecer
Completar EIPD, explicar infancia no habilitada e indicar conservación/consulta de
antecedentes. Completar EIPD abre el paso correspondiente en el mismo contexto.
Para variantes negativas/reubicación, acordar prueba ficticia deliberada o usar evidencia
controlada; no cambiar conclusiones guardadas solo para imitar un error ni recargar
borradores pendientes. No declarar nuevos guardados por el simple hecho de consultar.

### Validación asistida parcial lote 4 — resumen y acceso directo

Usuario confirma y aporta capturas a5afe215/572a770b: en pestaña nueva del espacio
conectado aparece Accesos según la determinación guardada, EIPD Corresponde con acceso
directo, infancia Pendiente con explicación, consulta de documentos anteriores.
Completar EIPD abre Tratamiento y alcance en el mismo contexto Gestión de clientes /
Coordinar citas / versión 1 borrador. No guardó otra determinación para esta comprobación.
La pestaña anterior mostraba versión previa sin el bloque; se mantuvo abierta para
conservar sus notas pendientes. Esta prueba no acredita sincronización de borradores.
C3 positivo comprobado asistidamente; aviso/reubicación C8 todavía pendiente de ensayo
manual. El lote 4 no queda globalmente aceptado por esta comprobación parcial.

### Ensayo asistido lote 4 — No corresponde y reubicación confirmados

Usuario confirma prueba OK con capturas da0d584a/3e5eebd3: revisión ficticia 2,
EIPD No corresponde, menú Completar EIPD retirado y panel explica no habilitación;
Atrás desde el intento de volver a EIPD muestra aviso «Volviste a Determinar
aplicabilidad… No corresponde», con cambios pendientes/borradores y consulta de
antecedentes preservados. No se declara aún comprobada la recuperación de la nota:
pendiente restaurar Corresponde y abrir EIPD en esta misma pestaña sin recargar.

Usuario solicita anotar confirmación de guardado alejada del botón por el panel de
accesos intermedio. Registrado en backlog para lote 5/C9 y coordinación lote 8;
solo registro, no reubicación implementada en lote 4.

### Aceptación asistida del lote 4 — restauración y nota conservada

Captura 227db7c3: tras restaurar EIPD Corresponde y abrir Tratamiento y alcance en
la misma pestaña, Notas del borrador conserva «[FICTICIA] Conservar durante prueba
de aplicabilidad» y el aviso de cambios sin guardar. Se recupera el formulario sin
persistir esa nota por navegar/restaurar aplicabilidad. Junto con resumen positivo,
No corresponde y reubicación explicada, completa el guion asistido C3/C8 acordado.
Lote 4 validado con ese alcance; infancia/preparación y otros estados cubiertos por
pruebas controladas, no se atribuyen ensayos manuales adicionales. Sin commit/push.
Pendiente lote 5: estado guardado frente a borrador y proximidad del mensaje de éxito
al botón Guardar, según observación registrada. No iniciar siguiente lote sin indicación.

### Publicación autorizada del lote 4

Usuario solicita commit y autoriza push del lote 4 validado. Se publica la rama
fix/navegacion-orientacion-aplicabilidad con código, pruebas y aceptación registrada;
los estados anteriores «sin commit/push» describen el momento previo a esta autorización.
No se inicia lote 5 ni se ejecuta merge/despliegue. Archivo generado next-env.d.ts
excluido. La CI remota debe comprobarse por el commit resultante; no se declara aprobada.


## Lote 5 C9 — estado guardado y borrador

Implementación local sobre 84ad96a en `fix/navegacion-estado-guardado`, autorizada
por usuario el 25/10/2026. Sin commit/push nuevo ni merge/despliegue.

### Cambios y límites

- Última determinación consultada: revisión de aplicabilidad, fecha en español y hora
  de Chile continental (America/Santiago), identificación de quien registró y asociación
  del alcance. Ausencia de registro/metadata se explica; no se inventa fecha ni autor.
- El contrato actual solo entrega `created_by` como identificador. Se presenta como tal,
  sin atribuir el registro al usuario conectado ni inventar un nombre. La resolución de
  nombres legibles requeriría otro alcance y controles; no se amplía la API en este lote.
- Al haber cambios, comparación de estado y fundamento guardados frente al borrador,
  diferenciada por EIPD e infancia. En formulario limpio no se repiten fundamentos.
- «Consultar última determinación guardada» sustituye el rótulo anterior. Botón secundario
  reconocible, foco y ayuda: consulta servidor, actualiza accesos, conserva ediciones,
  no guarda, no recarga RAT y no sincroniza automáticamente otras ventanas.
- Rechazo 409 conserva formulario, abre historial y orienta a consultar antes de guardar.
  Tras consultar se identifica la revisión recuperada y se comparan las diferencias.
  La consulta no repite el POST. Un guardado posterior sigue usando revisión/hash esperados.
- Historial rotulado «Revisión de aplicabilidad», no versión de evaluación; actor y fecha
  disponibles se muestran. No se heredan decisiones ni se modifica historia del servidor.
- «Determinación guardada en el servidor» inmediatamente antes de Guardar, después del
  panel de accesos y la ayuda de requisitos. Solo aparece por respuesta de escritura
  exitosa; nuevas ediciones, otra consulta o un intento posterior retiran ese aviso.

### Evidencia local

46 escenarios Chromium aprobados en la batería `connected-navigation.spec.ts`, 11 nuevos
sobre ausencia/autoría/fecha, lectura limpia y con ediciones, conflicto y posterior guardado
explícito, error/recuperación, fecha no disponible, consulta lenta sin duplicados, teclado,
comparación y proximidad del resultado a 1280/390/320 px. La ejecución dirigida de los 11
nuevos también pasó; no se suma como cobertura distinta. TypeScript, ESLint de los archivos
modificados y Prettier correctos. Capturas ficticias en `outputs/navegacion-lote5/` revisadas.

Fixtures con API interceptada y token sintético; no se inspeccionó sesión personal ni se
modificaron datos de desarrollo. No equivale a una nueva prueba de integración real de API,
concurrencia del servidor o RLS. Validación asistida del usuario aún pendiente.

### Guion de aceptación

1. Abrir `/dashboard/trabajo`, seleccionar el contexto de prueba existente y entrar en
   Bases de licitud → Preparar → Determinar aplicabilidad. Conservar en su pestaña original
   cualquier nota pendiente; una nueva ventana consulta lo guardado, no copia borradores.
2. Comprobar «Última determinación consultada en el servidor», revisión/fecha e identificador
   del autor cuando exista un guardado. Distinguirlo de los valores editables del formulario.
3. Escribir un fundamento ficticio sin guardar. Ver la comparación con el dato guardado.
   Pulsar «Consultar última determinación guardada»: el texto permanece y no se anuncia guardado.
4. Marcar declaración ficticia y guardar de forma explícita. La confirmación debe aparecer
   inmediatamente antes de Guardar; el formulario coincide con lo guardado y el historial
   agrega su revisión. Volver a editar retira la confirmación de escritura anterior.
5. Para concurrencia, usar dos ventanas del mismo contexto: guardar un cambio ficticio en una
   y mantener una edición distinta en la otra. Guardar desde la edición antigua debe rechazar
   el intento y conservarla. Consultar permite comparar con el registro reciente y decidir si
   se realiza un nuevo guardado explícito. No reemplazar ni copiar contextos ajenos.
6. En ventana estrecha, comprobar lectura, consulta por teclado, foco visible y confirmación
   junto a Guardar. La confirmación no significa aprobación ni activa EIPD.

No marcar C9 ni las observaciones de proximidad/consulta como aceptadas manualmente hasta
recibir el resultado del usuario. No iniciar lote 6 en este bloque.


### Validación asistida del lote 5 — consulta y comparación correctas

Capturas ead7a637 y fad26d34 aportadas por el usuario: en el espacio conectado,
Determinar aplicabilidad muestra revisión guardada 3 y, separadamente, el borrador
con la línea «[FICTICIA] Prueba lote 5». Tras Consultar última determinación guardada,
la línea permanece, se mantiene el aviso de cambios sin guardar y aparece el resultado
«Consulta completada. Tus cambios pendientes se conservaron». La comparación identifica
la diferencia; infancia sigue pendiente y sin diferencias. Fecha y autoría por identificador
visibles, sin copiar identificadores personales en esta documentación.

Primera comprobación asistida de lectura/comparación aceptada con ese alcance. Las
capturas no acreditan un nuevo guardado. Pendiente marcar declaración ficticia, guardar
explícitamente y comprobar confirmación inmediatamente antes de Guardar, revisión
incrementada y retirada del aviso de cambios. Concurrencia y móvil siguen cubiertos por
pruebas controladas, sin atribuir nueva aceptación manual. Sin commit/push del lote 5.


### Validación asistida del lote 5 — guardado y coincidencia confirmados

Captura dfa6d431: después de la instrucción de guardado explícito, la pantalla conectada
muestra revisión de aplicabilidad 4 y «El formulario coincide con esta determinación
consultada». La comparación de cambios pendientes ya no aparece en el panel. EIPD
permanece Corresponde e infancia Pendiente de analizar. Confirma el incremento respecto
de la revisión 3 observada antes; no cambia la versión 1 en borrador de la evaluación.

La captura solo cubre la parte superior. La ubicación de «Determinación guardada en el
servidor» respecto de Guardar determinación sigue pendiente de comprobación asistida;
no pedir otro guardado para verla. Bajar en la misma pestaña sin editar, consultar ni
recargar. No se declara aceptado el lote completo ni se ejecuta commit/push nuevo.


### Lote 5 — proximidad aceptada y conceptos en la comparación, 26/10/2026

El usuario confirma expresamente que «Determinación guardada en el servidor» aparece
encima de Guardar determinación: OK. Este criterio de proximidad queda aceptado
asistidamente, además de la consulta/conservación y el guardado observados previamente.

Captura cbc29124: solicita identificar los conceptos de cada valor comparado. Se agregan
«¿Corresponde documentar EIPD?:» y «Fundamento sobre EIPD:» tanto en Guardado en el servidor
como en Tu borrador en el formulario; mismo tratamiento para infancia y adolescencia.
Se conservan contenidos, saltos de línea, contraste guardado/borrador, reglas y estado
pendiente. No se modifica ni guarda el texto de la captura y no se eliminan líneas repetidas.

Validación local del ajuste: 11 escenarios dirigidos del lote 5 aprobados; las pruebas
existentes de comparación verifican ahora las etiquetas de ambos temas en ambas columnas
a 1280/390/320 px. Tipos, ESLint y Prettier correctos; capturas escritorio/320 revisadas.
La batería completa previa de 46 pertenece al estado anterior a este ajuste de etiquetas;
no se afirma una nueva ejecución completa. Pendiente comprobar las etiquetas con usuario;
concurrencia y móvil conservan su evidencia controlada, sin nuevos ensayos manuales.
Sin commit/push nuevo ni inicio de otro lote.


### Aceptación asistida del lote 5 — etiquetas confirmadas, 26/10/2026

El usuario confirma «OK las etiquetas». Junto con las capturas de consulta conservando
el borrador, revisión guardada 4/formulario coincidente y aceptación expresa del aviso
encima de Guardar, completa la validación asistida del recorrido acordado del lote 5.
Conceptos de decisión y fundamento aceptados en la comparación. Se conserva el límite
de autoría por identificador; no se inventan nombres ni se extiende el contrato.

Lote 5 C9 aceptado con este alcance. Concurrencia/conflicto, errores y móvil cuentan con
pruebas controladas; no se atribuyen nuevos ensayos manuales de esos casos. Evidencia:
batería completa previa de 46 escenarios y once dirigidos tras el ajuste de etiquetas,
tipos/lint/formato y capturas revisadas. No sumar ejecuciones como escenarios distintos.
Sin commit/push del lote 5 ni merge/despliegue. Próximo bloque propuesto: lote 6, pendiente
de indicación; no se inicia. NAV-UX-004 conserva sus demás pendientes.


### Publicación autorizada del lote 5

El 26/10/2026, tras confirmar etiquetas y los criterios asistidos anteriores, el usuario
solicita commit y autoriza push del lote 5 en fix/navegacion-estado-guardado. Se incluye
implementación, pruebas y documentación de aceptación. Las menciones anteriores de
«sin commit/push» describen el estado previo a esta autorización. Evidencia: 46 escenarios
completos antes del ajuste final de rótulos y once dirigidos después, tipos/lint/formato
y capturas revisadas. Sin cambios de API/DB/permisos ni habilitación EIPD. Archivos generados
y capturas fuera del commit. La publicación no acredita CI remota, merge ni despliegue.
Siguiente propuesto: lote 6, pendiente de indicación; no se inicia en este cierre.


## Replanificación tras los informes de ciclo documental y glosario — 26/10/2026

Análisis solicitado antes del próximo lote, sobre 2e3f546 (lote 5 publicado).
Se contrastan las propuestas de Claude con el repositorio; no se adopta su vocabulario
ni sus diagramas como reglas del servidor. Ver [evaluación integral](evaluacion-propuestas-claude.md)
y [plan operativo por sublotes](plan-navegacion-formularios.md).

Los lotes 6, 7 y 8 mantienen número y alcance; se subdividen para validar menús/nombres,
accesibilidad y simplificación por separado. Los nuevos bloques 9–13 cubren pendientes
identificables, contexto, capacidades documentales, ayudas y cierre con evidencia.
Las aceptaciones de 1–5 se conservan. No se repiten como ausentes la consulta, comparación,
metadatos disponibles ni guía de accesos ya implementadas.

Checklist inmediato para reanudar:

- [x] Leer ambos Word y contrastar las propuestas con HEAD, contratos y backlog.
- [x] Documentar decisiones P1–P13/G01–G30 y plan con criterios por sublote.
- [ ] Validar con el usuario la propuesta de plan; no atribuir aceptación todavía.
- [ ] Iniciar exclusivamente 6A cuando corresponda: nombres estables y accesos de un destino.
- [ ] Comprobar rutas/contexto, teclado básico y conservación de nota EIPD pendiente.
- [ ] Validar juntos el resultado antes de continuar 6B.

Solo documentación nueva en feature/plan-navegacion-terminologia. No se ejecuta lote 6,
no se cambian datos o permisos y no hay commit/push nuevo, merge ni despliegue en este análisis.
Las autorizaciones de publicación previas correspondieron a los cierres anteriores.


### Publicación autorizada del análisis y plan

El 26/10/2026 el usuario solicita los documentos Markdown para el repositorio y autoriza
commit/push. Se publican evaluación integral y plan 6–13, con referencias en backlog y
HANDOFF. Las menciones inmediatamente anteriores de publicación no autorizada describen
el momento de elaboración. No se inicia 6A, no se modifican funciones ni datos y no hay
merge/despliegue. Archivos generados y outputs locales quedan excluidos del commit.


## Bloque 6A — destinos coherentes y accesos directos

26/10/2026. Usuario solicita continuar 6A del plan publicado en d42b2e9. Rama local
feature/navegacion-6a-destinos. Sin commit/push nuevo ni inicio de 6B.

Cambios acotados:

- Diccionario de destinos conectados para menú, miga y Continuar, con claves de URL intactas.
- Documentos guardados unificado en su título conectado y sus accesos. El grupo de trabajo
  conserva la descripción Revisar y decidir; no es otra pantalla.
- Inventario de tratamientos coincide con su pantalla; el enlace de resultados utiliza
  Resultado del autodiagnóstico, igual que su pantalla existente.
- Los grupos de un solo destino son enlaces directos con su URL y activación por teclado.
  Los de múltiples destinos conservan desplegables y todos sus destinos.
- Destino actual con aria-current y borde/subrayado/negrita; grupo activo indicado sin
  confundirlo con éxito de guardado. Secciones conserva el mismo destino seleccionado.
- AssessmentFlow recibe rótulos conectados opcionales; los títulos de uso independiente
  permanecen sin cambios. Sin API, migraciones, permisos o reglas de aplicabilidad nuevos.

Evidencia controlada:

- 51 pruebas Chromium de connected-navigation: 46 anteriores y 5 nuevas del bloque 6A.
- 20 pruebas del flujo real AssessmentFlow en su harness independiente licitud-workspace.
- 18 pruebas de maqueta de referencia licitud-prototype. Total: 89 escenarios distintos.
- Tras aclarar tipos del diccionario y activar el enlace con Enter en la prueba, tipos,
  las 20 independientes y las cinco dirigidas de 6A pasaron; no sumar estas repeticiones.
- ESLint, Prettier y comprobación de tipos correctos. Capturas locales ficticias de
  escritorio, Secciones 390 y 320 revisadas, sin recorte ni desbordamiento horizontal.
- Enlace previo a revisar conserva IDs; menú, miga y título coherentes; siete destinos
  EIPD disponibles; nota pendiente conservada al consultar, continuar y usar Atrás/Adelante.
  No escrituras de dominio por navegar; el escenario EIPD usa una determinación ficticia
  explícita para habilitar su editor y verifica que navegar no añade escrituras.

Límites: pruebas con servicios simulados, no ensayo integrado nuevo sobre datos reales
ni aceptación asistida. Código generado next-env.d.ts y outputs/ fuera del cambio funcional.
Las cabeceras repetidas y la segunda lista de pasos EIPD siguen en lote 8; no se elimina
contenido ni se rediseña el formulario en 6A. Accesibilidad ampliada permanece en lote 7.

### Validación asistida pendiente de 6A

Usar /dashboard/trabajo, no /dashboard/maqueta. Conservar la pestaña original si contiene
borradores sin guardar; no recargarla para obtener los cambios. Una pestaña nueva permite
ver el código actualizado, pero no recupera las notas sin guardar de la original.

1. En Bases de licitud y la evaluación seleccionada, pulsar Documentos guardados en la
   barra superior: debe abrir directamente, sin desplegar otra opción. Revisar y decidir
   permanece como descripción del grupo. Comprobar Documentos guardados en miga y título.
2. Abrir Historial y descargas con una activación. Usar Atrás/Adelante para volver a
   Documentos guardados; contexto y destino resaltado deben corresponder.
3. Si hay una EIPD habilitada en esa pestaña, abrir Completar EIPD: siguen sus siete destinos.
   Escribir una nota ficticia sin guardar, ir a Documentos guardados y regresar; comprobar
   el mismo texto. No guardar ni volver a determinar aplicabilidad para esta comprobación.
4. En ventana estrecha, abrir Secciones y comprobar los mismos nombres y el destino actual.
5. Inventario de tratamientos: abrir el listado y una ficha; comparar el nombre del acceso,
   la miga y el título. Si se vuelve a Panel, Continuar debe nombrar el destino recordado.

Registrar OK/Fallo/No probado por paso. No cerrar 6A ni iniciar 6B hasta recibir el resultado.


### Validación parcial asistida 6A y ajuste del rótulo de grupo

26/10/2026: captura b4ef3d27 confirma nombre Documentos guardados en acceso, miga y título;
usuario confirma «3 OK» para Historial/Atrás/Adelante y «Todo OK» para conservar nota EIPD.
Después confirma funcionamiento de Continuar y observa falta de legibilidad de Revisar y
decidir en escritorio (94767b1b). El rótulo estaba definido a 12px y peso normal; se ajusta
a 1rem/negrita/color principal y espaciado, conservando la jerarquía y el acceso directo.
No se modifica navegación, formularios, datos ni reglas.

La captura estrecha 5d8db1f4 aún presenta Continuar en Revisar documentos, propio del nombre
anterior; se registra confirmación de funcionamiento, pero no uniformidad de nombres del
código nuevo en esa ventana. Pendiente comprobar el rótulo de escritorio ajustado y usar
la misma pestaña actualizada al reducir ancho. No recargar una pestaña con borrador pendiente.
6A conserva aceptación parcial; 6B no iniciado y sin commit/push nuevo.


### Aceptación asistida del rótulo y cierre acotado 6A

26/10/2026: usuario confirma «esta OK la glosa» tras el ajuste de tamaño/peso/contraste de
Revisar y decidir. Se registra aceptación visual. Las confirmaciones previas acreditan los
recorridos informados: acceso y nombres Documentos guardados, Historial/Atrás/Adelante,
conservación de nota EIPD y funcionamiento de Continuar. No se atribuye verificación de los
nombres nuevos a la captura estrecha antigua ni pruebas manuales adicionales de permisos.

6A aceptado con ese alcance. Evidencia técnica previa: 89 escenarios distintos, tipos,
lint/formato y capturas; tras ajuste visual: cinco dirigidos aprobados y captura de escritorio
revisada, sin sumar ejecuciones como escenarios diferentes. Móvil conserva evidencia
controlada 320/390; no se declara una nueva prueba integrada contra servidor en este cierre.

Cambios locales en feature/navegacion-6a-destinos sobre d42b2e9. Sin commit/push nuevo,
merge/despliegue ni inicio de 6B. Próximo propuesto: 6B conforme al plan, pendiente de
indicación. NAV-UX-006 y demás lotes conservan sus alcances pendientes.


### Publicación autorizada del bloque 6A

26/10/2026: usuario solicita commit y autoriza push tras aceptar la glosa. Se publica
el bloque acotado en feature/navegacion-6a-destinos sobre d42b2e9, con implementación,
pruebas y aceptación documentadas. Evidencia: 89 escenarios distintos anteriores al
ajuste visual; cinco dirigidos y captura después del ajuste. No atribuir nuevos ensayos
manuales ni CI remota sin verificarlos. Generado next-env.d.ts y outputs locales excluidos.
Las menciones previas de sin commit/push son antecedentes. Sin inicio de 6B, merge/despliegue.

## Bloque 6B — operaciones documentales y disponibilidad

Fecha: 26/10/2026. Implementación local en `feature/navegacion-6b-operaciones`,
base publicada `d9f859f9742cd013479e002536f366ad6573ca5a`. Usuario solicita continuar
exclusivamente 6B. Pendiente aceptación asistida; sin commit/push de este bloque.

### Cambios y límites

- Revisión formal: «Resultado de la revisión documental»; actuación independiente:
  «Decisión de la organización». Se conservan valores y restricciones del servidor.
- Infancia: «Versiones registradas del documento de infancia», «Preparar nueva versión
  a partir de esta» y «Registrar nueva versión documental ficticia». Copiar y consultar
  la vista previa preparan contenido temporal; solo el registro explícito crea una versión.
  Las referencias históricas y la correspondencia con resolución documental se conservan.
- `document_version` se presenta como «Nombre de la edición (texto libre)», separado de
  Referencia, con ayuda: no asigna ID ni número de versión. Guardar el documento EIPD de
  la misma evaluación no registra otra versión ni emite una revisión formal.
- Siete pasos compartidos: Tratamiento y alcance de la EIPD; Necesidad y proporcionalidad;
  Describir riesgos; Valorar riesgos; Medidas de mitigación; Fuentes y evidencias;
  Riesgo residual y seguimiento. El tercer paso contiene descripción; la valoración
  permanece en el cuarto. No se fusionan formularios ni se cambia cálculo alguno.
- Navegación condicional: disponibilidad de cada tema informada por separado cuando no
  tiene editor habilitado. Distingue sin registro, pendiente, No corresponde, información
  insuficiente, asociación por revisar, consulta en curso y error. Solo ofrece orientación
  a Determinar aplicabilidad; un borrador no guardado no habilita el editor.
- No cambia backend, API, permisos, confirmación/activación EIPD ni persistencia.
  No se introduce sincronización entre ventanas. Los rótulos validados del lote 5 siguen vigentes.

### Evidencia controlada

157 escenarios distintos aprobados: 33 infancia, 61 navegación conectada, 18 consulta EIPD,
20 flujo documental, 12 decisión de organización y 13 expediente. Incluyen 11 escenarios
nuevos 6B: razones de disponibilidad, independencia entre temas, borrador frente a guardado,
carga/error, 1280/390/320 px y preparación/nombre libre sin registro ni revisión.
Los selectores que aún esperaban nombres antiguos se actualizaron conservando sus
aserciones de contenido, conservación y ausencia de escrituras prematuras; la pasada
final aprobó 144 escenarios y los 13 de expediente por separado, sin sumar repeticiones.
Tipos, ESLint, formato y revisión visual de capturas correctos. No hay desbordamiento
horizontal en 320/390. Capturas locales: `outputs/navegacion-6b/`, fuera del commit.
Son pruebas Chromium con respuestas ficticias controladas, no una aceptación integrada
nueva sobre el servidor del usuario. `eipd-integrated.spec.ts` adapta los selectores, pero
su recorrido con fixture API aislado no se ejecutó en este bloque.

### Guion de aceptación asistida

1. En `/dashboard/trabajo`, usar una evaluación con EIPD Corresponde guardada e infancia
   Pendiente de analizar. Sin recargar una pestaña con cambios pendientes, comprobar que
   Completar EIPD abre sus pasos y «Infancia y adolescencia: disponibilidad» explica el
   pendiente y ofrece Ir a Determinar aplicabilidad. En estrecho usar Secciones.
2. En Tratamiento y alcance de la EIPD, comprobar el campo «Nombre de la edición (texto
   libre)» y su ayuda. Distinguirlo de Referencia y del número de evaluación. No guardar
   por el solo hecho de probar el rótulo. Confirmar Describir riesgos frente a Valorar riesgos.
3. En un contexto ficticio con infancia habilitada y una versión registrada, leer
   Preparar nueva versión a partir de esta y la explicación de preparación temporal.
   No registrar una versión durante esta comprobación de nombres. Si no hay versión,
   dejar este caso pendiente; no crearla implícitamente para completar la prueba.
4. Comprobar «Resultado de la revisión documental» frente a «Decisión de la organización»
   donde el contexto permita consultar esos controles, sin emitir una decisión de prueba.

Los casos no disponibles en los datos actuales mantienen evidencia controlada y aceptación
asistida pendiente. No cerrar NAV-UX-006 globalmente ni iniciar 7A antes de este cierre.

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

## Bloque 7A — teclado y foco en navegación conectada

27/10/2026. Usuario solicita continuar 7A. Rama `feature/navegacion-7a-teclado`,
base publicada `8fec3dffe641562c9e6ab84b070fcaabb08b1c12`. Implementación local;
pendiente aceptación asistida. Sin commit/push de 7A ni inicio de 7B.

### Hallazgos y cambio acotado

Dos regresiones nuevas reprodujeron el problema antes de corregirlo: con Tab un grupo
abierto permanecía visible al entrar al siguiente y con apertura por teclado podían
coexistir dos desplegables de escritorio. Corregido en ConnectedWorkspace: cerrar al
salir del grupo sin redirigir el foco; al abrir un desplegable cerrar los demás;
Escape solo cierra el desplegable que contiene el foco y vuelve a su summary. Los
controles conservan semántica nativa details/summary, Enter/Espacio y Tab/Shift+Tab.
No se añade role=menu ni se interceptan flechas/Inicio/Fin de campos del formulario.

Abrir Menú, Secciones o Cambiar contexto cierra otros paneles y desplegables conectados.
Al cruzar hacia ventana estrecha, si el foco estaba en la navegación de escritorio
que se oculta, pasa a Secciones visible. No se mueve si estaba en el formulario.
Se conserva el foco/scroll existente al área de trabajo tras seleccionar un destino,
y el cierre por Escape/fondo exterior y retención de Tab de los paneles compartidos:
las pruebas acreditaron esos comportamientos sin cambiar PrototypeDrawer/MainModules.
Escape cierra un panel; no cambia al menú principal ni navega atrás. Un clic dentro de
la superficie del panel no lo cierra salvo selección o cierre explícito.

### Verificación y límites

67 escenarios distintos de navegación conectada aprobados, incluidos seis nuevos 7A.
Los seis dirigidos pasaron primero y luego en la pasada completa; no sumar repeticiones.
Se comprueban entrada/salida Tab/Shift+Tab, apertura Enter/Espacio, un solo desplegable,
Escape/foco de retorno, controles de formulario sin foco robado, ambos paneles con
clic interior y fondo exterior, foco visible, selección sin quedar bajo la cabecera,
retorno entre módulos con nota EIPD pendiente y cero escrituras adicionales después
de preparar el fixture. Cobertura de paneles en 390/320, escritorio y cruce de tamaño.
Tipos, ESLint, Prettier y git diff --check correctos. Capturas locales revisadas en
outputs/navegacion-7a, excluidas de publicación. Las pruebas usan Chromium y respuestas
ficticias controladas; no acreditan un nuevo ensayo integrado sobre el servidor del
usuario, lector de pantalla ni accesibilidad integral. La estructura semántica y nombres
pendientes pertenecen a 7B; cabeceras y listas duplicadas siguen en 8A/8B.
Sin cambios API/backend, permisos, datos, guardado ni habilitación EIPD.

### Guion asistido 7A

1. En /dashboard/trabajo, poner foco en Preparar con Tab (Shift+Tab retrocede). Pulsar
   Enter; Tab entra en sus opciones y Shift+Tab regresa. Escape cierra y deja foco en
   Preparar. El contorno de foco debe verse; no cambia el formulario ni guarda.
2. Abrir Preparar con Espacio y avanzar con Tab hasta el siguiente grupo. El anterior
   debe cerrarse. Abrir Completar EIPD si está habilitado; Tab a un destino y Enter.
   El panel se cierra y el área de trabajo recibe el foco bajo la cabecera. Si EIPD no
   está habilitada, usar otro grupo disponible; no guardar otra determinación solo para probar.
3. En ventana estrecha, Tab hasta Menú y Enter; Escape debe cerrar y devolver foco a
   Menú. Repetir con Secciones. Clic dentro del panel lo mantiene; clic sobre el fondo
   sombreado lo cierra. No confundir cerrar con cambiar de módulo.
4. Con una nota pendiente existente, cambiar de sección/módulo y volver, sin guardar
   ni recargar. Confirmar que permanece. No escribir datos nuevos salvo texto ficticio
   de prueba acordado. Al reducir la ventana con foco en un desplegable de escritorio,
   comprobar que Secciones queda disponible y recibe el foco.

No recargar pestañas con borradores pendientes. Si se necesita cargar la implementación
actualizada, usar una pestaña de prueba independiente y su propio contexto; no esperar
que el contenido sin guardar de otra pestaña se copie automáticamente.

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

## Publicación autorizada de 7A — 27/10/2026

Usuario solicita commit y autoriza push de 7A aceptado, en feature/navegacion-7a-teclado
sobre 8fec3df. Se reúne navegación de teclado, manejo explícito de Espacio, regresiones
y aceptación asistida acotada. Los pendientes de publicación inferiores son antecedentes
anteriores a esta autorización. Mantener los límites de evidencia: pasada completa de 67
antes del último ajuste y siete escenarios dirigidos después, sin atribuir CI remota.
Excluir next-env.d.ts generado y outputs/ locales. Comprobar HEAD remoto tras el push.
No iniciar 7B ni ejecutar merge/despliegue en este cierre.

## Bloque 7B — nombres, regiones y ayudas accesibles

27/10/2026. Usuario solicita continuar 7B. Rama `feature/navegacion-7b-accesibilidad`,
base publicada `39bca0b1d722c18c9f5a10e304847cbe2b631013`. Implementación local;
pendientes validación asistida y lector de pantalla. Sin commit/push ni inicio de 8A.

### Contraste y cambios

- El layout autenticado usaba un main que envolvía al main conectado. DashboardContent
  conserva main para las demás rutas y usa div para /dashboard/trabajo, cuyo espacio
  ya aporta un main. La rama sin organización incluye su propio main con encabezado.
  Autenticación permanece en el layout de servidor, sin cambiar acceso o datos.
- Menú conectado: «Módulos del espacio de trabajo»; MainModules mantiene por defecto
  «Módulos de la maqueta» para la referencia. Sin sustitución global de sus nombres.
- Área de trabajo nombrada por su h1: Panel principal o «Área de trabajo: [destino]».
  El título de la pestaña usa destino, módulo y CumpleIA; no añade identidades personales.
  En destinos con formulario el h1 es accesible sin introducir otra cabecera visible.
- Menú/Secciones/Contexto se relacionan con su diálogo mediante aria-controls; Contexto
  informa también aria-expanded. Cierre, foco y teclado de 7A permanecen.
- AssessmentFlow conectado usa regiones con nombres propios y no tabpanel referidos a
  pestañas locales ocultas. El uso independiente conserva sus pestañas y relación con
  paneles. IDs de pestañas, paneles y regiones de infancia son propios por instancia;
  las referencias de valoración usan su panel correspondiente. El paso sin panel de
  valoración asociado no anuncia un aria-controls a un destino inexistente.
- Ayudas de revisión y decisión tienen identificadores propios por componente. El nombre
  libre de edición, la consulta de determinación y los requisitos de guardado conservan
  su ayuda asociada. EIPD explica deshabilitación por rol, estado, guardado en curso o
  resultado incierto; el estado confirmado no se presenta falsamente como rol de consulta.
- No hay rediseño visual, retiro de listas/cabeceras, nuevas reglas, escritura automática
  ni cambios backend/API. Simplificación de cabecera/listas permanece en 8A/8B.

### Verificación y límites

168 escenarios distintos aprobados: 74 conectados (6 nuevos 7B), 20 flujo documental,
33 historial de infancia, 12 decisiones de organización y 29 maqueta. Una prueba opcional
adicional de capturas de maqueta quedó omitida por su condición; no contarla como aprobada.
Tipos, ESLint, Prettier y git diff --check correctos. Capturas 1280/390 revisadas en
outputs/navegacion-7b, locales y excluidas de publicación. Continúa vigente la cobertura
320 del teclado 7A; las capturas nuevas de ayudas de 7B son 1280/390.

El harness conectado ahora monta el DashboardContent real con pathname simulado de trabajo,
para comprobar el defecto del main anidado y no solo el componente aislado. Comprueba main
único/nombre/título, regiones sin depender de pestañas ocultas, relaciones de paneles,
referencias accesibles con destinos únicos, dos evaluaciones montadas conservando nota,
descripciones de edición/requisitos, bloqueo por estado sin atribución al rol y apertura/
cierre de metodología con teclado y pulsaciones táctiles emuladas sin guardar.
Una primera comprobación de conservación seleccionaba dos textareas por etiqueta, incluida
la evaluación oculta; se acotó al textbox expuesto en el árbol accesible y pasó sin alterar
el aislamiento ni el montaje de borradores. No se ocultó un error funcional.

Son pruebas Chromium con respuestas ficticias controladas, no ensayo integrado nuevo contra
el servidor del usuario ni sesión con lector de pantalla. La consulta con NVDA/Narrador y
las rutas autenticadas fuera de trabajo requieren comprobación manual correspondiente;
no declarar accesibilidad integral certificada. No usar lectura en voz alta del navegador
como sustituto de recorrer regiones y nombres con un lector de pantalla.

### Guion asistido

1. Usar pestaña de prueba actualizada en /dashboard/trabajo y conservar abierta la antigua
   si contiene borradores pendientes. Abrir Determinar aplicabilidad y Documentos guardados;
   el título de la pestaña debe identificar el destino actual y CumpleIA. No guardar.
2. Con Tab llegar a Secciones, abrir con Enter, cerrar con Escape y confirmar retorno del
   foco. Repetir Contexto y cancelar. Confirmar ayuda visible de Consultar última determinación
   guardada y que informa conservación del borrador, sin guardado o sincronización.
3. En EIPD habilitada, consultar Nombre de la edición y su ayuda; en Necesidad y
   proporcionalidad comprobar la explicación de una respuesta (sin registrar otra versión).
   En Valorar riesgos abrir/cerrar metodología con Enter y, si se dispone, toque táctil.
4. Con NVDA o Narrador disponible, recorrer regiones y encabezados: un único contenido
   principal por vista conectada; nombre del área de trabajo y menú conectado; Secciones/
   Contexto anunciados expandido/contraído y foco de retorno. Comprobar descripción de
   consulta/requisitos y nombre de regiones documentales sin pestañas ocultas. Registrar
   lector, navegador y resultado observado. Si no se ejecuta, mantener este criterio pendiente.

No recargar ni cerrar pestañas con preparación temporal que se desee conservar. Cambiar
la pestaña no copia sus borradores. No crear decisiones, determinaciones o versiones solo
para completar esta prueba de estructura.

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

## Publicación autorizada de 7B — 27/10/2026

Usuario solicita commit y autoriza push de 7B en feature/navegacion-7b-accesibilidad,
base 39bca0b. Publicar estructura/nombres/ayudas, pruebas y validación asistida acotada.
La prueba manual con lector de pantalla permanece pendiente por no disponibilidad del
usuario; publicar no cierra ese criterio ni acredita accesibilidad integral certificada.
168 escenarios aprobados y 1 captura opcional omitida según ejecución registrada;
no atribuir CI remota nueva al push. Los pendientes inferiores de autorización describen
estados anteriores. Excluir next-env.d.ts generado y outputs/ locales; verificar HEAD
remoto tras publicar. No iniciar 8A ni ejecutar merge/despliegue en este cierre.

## Bloque 8A — contexto compacto implementado, 27/10/2026

Rama `feature/navegacion-8a-contexto`, base publicada `15aa2736fd9cf190e9e1004b1d3445ed8f75efae`.
Implementación local solicitada por el usuario; validación asistida pendiente. Sin commit/push
ni inicio de 8B. Esta entrada actualiza los estados anteriores de «sin inicio de 8A».

### Cambio acotado

- Cabecera única con organización y tratamiento en espacios propios, versión/estado de la
  evaluación y botón **Ver contexto completo**. Los nombres pueden abreviarse visualmente;
  el panel de lectura muestra sus textos íntegros, finalidad y evaluación con conceptos separados.
- Ámbito conservado: Panel/Mi organización/Autodiagnóstico solo organización; Inventario
  organización/tratamiento; Bases de licitud también finalidad/evaluación. El enlace Continuar
  mantiene el destino y contexto recordados. No se inventan nombres de evaluación.
- El detalle es de consulta: no cambia contexto, no guarda, no recarga RAT ni sincroniza
  ventanas. Enter/toque abre; Cerrar detalle, Escape o fondo exterior cierran y devuelven el foco.
  El borrador y la ruta se conservan. El panel admite desplazamiento para nombres largos.
- AssessmentFlow retira su resumen de contexto y aviso piloto repetidos únicamente cuando
  recibe navegación externa. En uso independiente conserva ambos. El rol de solo consulta
  permanece explícito también en conectado; restricciones de cada acción y aviso global siguen.
- La evaluación activa se distingue del documento histórico consultado, que mantiene número,
  referencia, nombre de edición y antecedentes propios. Prueba: evaluación versión 2 frente a
  versión documental histórica 1, sin escritura.
- No se retira aún la lista central de siete pasos EIPD: corresponde a **8B**. No se modifican
  contratos/API, permisos, criterios de riesgo, guardado ni confirmación/activación.

### Evidencia comparable

Capturas y métricas locales en `outputs/navegacion-8a/` (no versionadas). Chromium, viewport
con altura 900 px, mismo ancho, zoom predeterminado, posición inicial 0, datos ficticios y paso
Tratamiento y alcance de la EIPD. «Primer campo» es Referencia del documento EIPD; Y se mide
respecto del viewport y puede superar su altura. La comparación incluye el espacio retirado
dentro del formulario, no solo la reducción de la cabecera.

| Ancho | Nombres | Altura cabecera antes → después (px) | Y primer campo antes → después (px) |
| --- | --- | --- | --- |
| 1280 | normales | 256,4 → 250,4 | 930,9 → 639,3 |
| 1280 | largos | 296,4 → 250,4 | 996,5 → 639,3 |
| 390 | normales | 177 → 157 | 1387 → 979,1 |
| 390 | largos | 297 → 157 | 1660,6 → 979,1 |
| 320 | normales | 244,5 → 236,5 | 1710,4 → 1186,5 |
| 320 | largos | 404,5 → 236,5 | 2049,6 → 1186,5 |

Capturas de escritorio/móvil y detalle largo revisadas visualmente. No se promete que el primer
campo siempre quede visible: la segunda lista EIPD permanece hasta evaluar 8B.

Pruebas finales: **104 escenarios Chromium** (84 de navegación conectada y 20 de recorrido
independiente), con APIs simuladas y datos ficticios. Incluyen consulta de nombres completos a
1280/390/320, sin desbordamiento horizontal; ámbito por módulo; borrador/foco al cerrar;
consulta táctil emulada; identidad de evaluación frente a documento histórico; errores,
permisos y conservación de teclado/relaciones accesibles. Tipos, ESLint de componentes,
Prettier y `git diff --check` aprobados. No equivale a integración real con el servidor ni a CI remota.
La comprobación manual con lector de pantalla de 7B permanece pendiente.

### Guion asistido 8A

1. Abrir una pestaña de prueba actualizada en `/dashboard/trabajo`. Conservar la antigua si
   contiene preparación temporal o notas sin guardar; una pestaña nueva no copia ese contenido.
2. En Bases de licitud comprobar organización/tratamiento y versión seleccionados. Abrir
   **Ver contexto completo**: leer Organización, Tratamiento, Finalidad y Evaluación separados.
   Cerrar con Escape y comprobar retorno del foco; volver al campo y comprobar su texto.
3. Repetir en ventana estrecha y leer un nombre largo íntegro mediante el detalle; también
   probar Cerrar detalle y clic sobre el fondo gris exterior, sin guardar.
4. Ir a Inventario y luego Panel/Mi organización/Autodiagnóstico; comprobar sus ámbitos.
   En Documentos guardados distinguir la versión histórica de la evaluación de la cabecera.
5. Comparar espacio con igual ventana/zoom/datos, sin exigir primer campo visible en móvil.

Registrar OK/fallo por recorrido antes de solicitar cierre/publicación. No ejecutar 8B ni
registrar nuevos documentos o decisiones como parte de estas comprobaciones de lectura.

## 8A — primera comprobación asistida confirmada, 27/10/2026

Usuario responde «prueba OK» al guion: pestaña actualizada en /dashboard/trabajo,
Bases de licitud → Ver contexto completo, comprobación de datos seleccionados y cierre
con Escape con foco de retorno y texto conservado. Se acepta este recorrido acotado.
No atribuir todavía validación de móvil/nombres largos, cierre exterior, ámbito de otros
módulos o identidad histórica; tampoco lectura por lector de pantalla.

Siguiente prueba: reducir el ancho de esa misma pestaña sin recargar, abrir Ver contexto
completo, leer los datos mediante desplazamiento si hace falta y cerrar pulsando el fondo
gris exterior al panel. Comprobar foco de retorno y contenido conservado, sin guardar.
Después comprobar ámbito por módulo e identidad histórica según guion 8A.
Sin cambios de producto en este registro; sin commit/push autorizado ni inicio de 8B.

## 8A — ventana estrecha confirmada, 27/10/2026

Usuario confirma «recorrido OK» tras reducir el ancho sin recargar, abrir Ver contexto
completo, leer sus datos con desplazamiento si es necesario y cerrar sobre el fondo gris
exterior al panel, con foco de retorno y texto del formulario conservado.
Se acepta este recorrido acotado; siguen pendientes ámbito por módulo e identidad histórica.
No atribuir prueba manual con lector de pantalla ni cierre completo de 8A.
Sin autorización nueva de commit/push; 8B no iniciado.

Siguiente comprobación asistida: navegar sin guardar a Inventario de tratamientos,
abrir Ver contexto completo y comprobar organización/tratamiento. Después ir a Panel
principal y comprobar que el detalle muestra solo organización, sin presentar la evaluación
como contexto propio del panel. Volver a Bases de licitud y comprobar finalidad/evaluación
y conservación del texto pendiente. La identidad del documento histórico se valida después.

## 8A — contexto por módulo confirmado, 27/10/2026

El usuario confirma «recorrido OK» al comprobar Ver contexto completo en Inventario
(organización/tratamiento), Panel principal (solo organización) y retorno a Bases de
licitud (finalidad/evaluación y texto pendiente conservados), sin recargar ni guardar.
Este resultado se suma a las comprobaciones asistidas previas del detalle y ventana estrecha.
Queda por comprobar la distinción entre evaluación activa y documento histórico consultado;
Mi organización/Autodiagnóstico conservan cobertura automatizada, sin atribuirles ahora una
prueba asistida adicional. Lector manual de 7B pendiente. Sin nueva autorización de
commit/push ni inicio de 8B.

Siguiente comprobación de lectura: en Documentos guardados, consultar una versión documental
existente de infancia, si está disponible. Distinguir la evaluación de la cabecera/detalle de
la versión, referencia y nombre de edición del documento histórico. Sus números pueden
coincidir; no tienen que hacerlo. No crear documentos, revisiones o decisiones para probarlo.
Si no existe una versión en el contexto actual, registrar esa limitación y usar un contexto
con historial conocido mediante Cambiar contexto, conservando la pestaña con pendientes.

## 8A — evidencia de identidad histórica, 27/10/2026

La captura aportada por el usuario en Documentos guardados muestra la evaluación activa
«versión 1 · borrador» en la cabecera y, separadamente, referencia documental
SIMULADA-PILOTO-INFANCIA-RES-001, nombre de edición PRUEBA-1, notas y fecha del registro.
El aviso local identifica «resolución 1». La captura anterior del detalle identifica la
organización CumpleIA Demo, tratamiento ficticio con menores, finalidad y evaluación.
Se verifica visualmente separación de evaluación y documento conservado; que ambos números
sean 1 no implica que compartan identidad. No se registra una revisión ni decisión.
Esta evidencia complementa los tres recorridos 8A confirmados por el usuario. No atribuir
validación asistida de Mi organización/Autodiagnóstico, medición comparativa manual o lector
de pantalla; estos límites siguen registrados. Sin nueva autorización de commit/push ni 8B.

## 8A — recorridos asistidos completados, 27/10/2026

Usuario confirma «recorrido OK» al consultar el contexto en Mi organización y
Autodiagnóstico (solo organización), y volver a Bases de licitud recuperando tratamiento,
finalidad y evaluación seleccionados, sin recargar ni guardar.

Con las confirmaciones anteriores quedan aceptados los recorridos asistidos acotados de
8A: detalle completo y Escape/foco/texto conservado; ventana estrecha y cierre exterior;
ámbito por módulo y retorno; separación del documento histórico observada en capturas.
La ganancia de espacio se respalda en las seis mediciones automatizadas y capturas
comparables registradas, no en una medición manual adicional atribuida al usuario.
104 Chromium aprobados (84 conectados y 20 independientes), tipos/lint/formato según la
verificación previa. Este cierre documental no modifica el producto ni requiere repetirlos.
No equivale a certificación de accesibilidad ni a integración real/CI remota; el lector
manual pendiente de 7B sigue abierto. La prueba táctil registrada es emulada.

8A listo para commit/push cuando el usuario lo autorice. No se ejecutaron commit/push,
merge/despliegue ni se inició 8B. Próximo bloque del plan: 8B, navegación principal EIPD
y ubicación del paso. Preservar las pestañas con preparación temporal o notas pendientes.

## Publicación autorizada de 8A — 27/10/2026

Usuario solicita commit y autoriza push en `feature/navegacion-8a-contexto`, base `15aa273`.
Se publica el contexto compacto y su detalle accesible, conservación de la cabecera
independiente, pruebas y resultados asistidos de 8A. 104 Chromium aprobados y checks
estáticos previos aprobados; no atribuir CI remota al push. Lector manual de 7B pendiente.
Las entradas inferiores de autorización pendiente describen estados anteriores.
Excluir `frontend/next-env.d.ts` generado y `outputs/` locales. 8B no iniciado;
sin merge ni despliegue. Verificar identidad del commit remoto tras publicar.

## Bloque 8B — navegación principal y paso actual, 27/10/2026

Rama `feature/navegacion-8b-pasos`, base `e04d8d82f552bf6c82625dcd7db5f6e310736526`
(8A publicado y comprobado contra HEAD remoto). Implementación local solicitada por el
usuario; validación asistida y autorización de publicación pendientes. Sin inicio del lote 9.

### Cambios

- El editor EIPD conectado deja de mostrar su lista central de siete botones. Conserva los
  mismos siete destinos, orden y nombres compartidos mediante la barra o el panel Secciones.
- Encabezado del formulario con nombre del paso y «Paso N de 7 · Completar EIPD». Es ubicación,
  no porcentaje, guardado ni completitud. No se marcan pasos como terminados por visitarlos.
- Anterior/Siguiente identifica el destino y cambia de paso sin guardar. Se ubica después
  del formulario y, en el paso 4, después del panel de valoración, conservando su contenido.
  Los extremos no ofrecen un paso anterior/siguiente inexistente.
- A partir de 1200 px se usa la barra de secciones y se oculta el disparador redundante de
  Secciones; por debajo se usa ese panel y se oculta la barra. Menú principal conserva su
  comportamiento anterior. La barra puede distribuir sus grupos en más de una fila.
- El corte se comprobó en seis anchos (320/390/865/1100/1280/1920), con nombres completos
  de los siete destinos: sin opciones recortadas ni desbordamiento horizontal de página.
  Al estrechar con foco en la barra, pasa a Secciones; al ampliar con el panel abierto,
  se cierra y el foco pasa al grupo/destino visible de la barra.
- El uso independiente conserva EipdSteps y su navegación previa. No se alteran campos,
  requisitos, API, permisos, decisiones, guardado ni los bloqueos de confirmación/activación.

### Verificación

**111 pruebas Chromium aprobadas:** 91 conectadas (incluidas siete nuevas de 8B) y 20 del
recorrido independiente, con API simulada y datos ficticios. Se recorren los siete destinos
por la vía visible a cada ancho; título/posición, Anterior/Siguiente, Atrás/Adelante, borrador,
relaciones accesibles, cierre/foco y disponibilidad condicionada. Las pruebas previas de
teclado, errores, permisos y contexto permanecen aprobadas. En independiente se conservan
los botones de pasos y el recorrido de valoración.

Tipos, ESLint de componentes afectados, Prettier y `git diff --check` aprobados. Capturas
locales `outputs/navegacion-8b/` (no versionadas), revisadas a 320/865/1920 px. No se declara
integración real con servidor ni CI remota nueva. La prueba manual de zoom del navegador
al 200 % y el recorrido asistido de 8B quedan pendientes; las pruebas de anchos no se
presentan como equivalentes a haber probado ese control del navegador. Sigue pendiente
lector manual de 7B; no se declara certificación de accesibilidad.

### Guion asistido de 8B

1. Abrir una pestaña actualizada en /dashboard/trabajo, conservando la antigua si contiene
   notas o preparación temporal. Elegir una evaluación con EIPD «Corresponde» ya guardada.
   En ventana amplia, Completar EIPD → Describir riesgos: debe verse su título y Paso 3 de 7,
   sin la lista central de siete botones.
2. Sin guardar, usar Siguiente al final del formulario → Valorar riesgos (Paso 4 de 7),
   luego Siguiente → Medidas de mitigación (Paso 5 de 7). Volver mediante la navegación y
   comprobar que las notas pendientes continúan. No registrar otra determinación o versión.
3. Reducir el ancho de la misma ventana sin recargar: Secciones sustituye la barra. Abrir
   Completar EIPD y repetir los tres destinos; comprobar nombres completos, cierre con Escape
   y fondo exterior, foco y acceso al bajar por formularios.
4. En escritorio cambiar el zoom del navegador a 200 %, comprobar reflujo, vía de navegación
   visible y acciones legibles sin desplazamiento horizontal de página. Restituir 100 %.
5. Ampliar con el panel Secciones abierto: debe cerrar y dejar el foco en la barra disponible.
   Confirmar que volver con Atrás/Adelante conserva ubicación y contenido, sin guardar.

Registrar resultados por recorrido antes de cerrar el checklist/publicar. No recargar una
pestaña con cambios pendientes ni atribuir sus notas a una pestaña nueva.

## 8B — primera comprobación asistida confirmada, 27/10/2026

El usuario confirma «recorrido OK» al abrir Completar EIPD → Describir riesgos en una
pestaña actualizada y ventana amplia, con evaluación EIPD habilitada: título del paso,
«Paso 3 de 7» y ausencia de la lista central repetida. No se solicitó guardar.
Aceptación acotada a esta primera comprobación. Pendientes: Anterior/Siguiente con
conservación del texto, ventana estrecha/cierres/foco, zoom real 200 % y Atrás/Adelante.
111 pruebas automatizadas y checks previos mantienen su alcance; este registro documental
no modifica producto ni añade ejecuciones. Sin commit/push de 8B ni inicio de lote 9.

## 8B — secuencia y borrador confirmados, 27/10/2026

El usuario confirma «recorrido OK» tras escribir la nota ficticia de navegación 8B en
Describir riesgos, usar Siguiente hacia Valorar riesgos (Paso 4 de 7), continuar a
Medidas de mitigación (Paso 5 de 7) y volver a Describir riesgos mediante Completar EIPD,
con la nota conservada, sin guardar ni recargar. Se acepta este recorrido acotado.
Pendientes: ventana estrecha/cierre/foco, zoom real 200 %, ampliación con Secciones
abierto y Atrás/Adelante. No equivale a guardado en servidor ni sincronización entre
pestañas. Sin commit/push de 8B ni inicio del lote 9.

## 8B — incidencia asistida de Escape repetido, en investigación, 27/10/2026

Usuario informa que Escape cierra Secciones la primera vez, pero no funciona como espera
en aperturas siguientes. No se considera aceptado todavía el recorrido móvil de 8B.
Se añaden cinco escenarios automatizados, a 320/390/865/1100/1199 px: cada uno abre y cierra
Secciones cinco veces con Escape, verifica foco de retorno, vuelve al campo de notas y
comprueba que Escape con panel cerrado mantiene ese foco y su contenido. Los cinco pasan
con el código de producto actual (25 ciclos), sin guardar. Son pruebas con Chromium y API
simulada; no descartan el fallo reportado en la sesión del usuario.

Pendiente precisar si en el fallo el panel lateral permanece visible o ya se eligió una
opción y se regresó al formulario. No se aplica un cambio preventivo sin reproducción ni
se declara corregida la incidencia. Continúan pendientes el guion móvil y zoom real 200 %.

## 8B — aclaración de Escape mediante captura, 27/10/2026

La nueva captura del usuario muestra Describir riesgos con el formulario visible y sin
panel lateral Secciones abierto. En ese estado, Escape no debe mover el foco al disparador:
no es un atajo global de retorno. Elegir un destino cierra Secciones y lleva al área de
trabajo; solo Escape mientras el panel permanece abierto lo cierra con foco de retorno.
La afirmación conversacional de posible fallo de reapertura fue prematura. La evidencia
aportada no reproduce un panel abierto que rechace Escape; no se aplica corrección de
producto por este caso. Se mantienen las cinco pruebas de repetición aprobadas como regresión.

Siguiente comprobación asistida precisa: pulsar Secciones y, sin seleccionar destino,
verificar que aparece el panel lateral con Cerrar secciones; pulsar Escape y comprobar
cierre/foco. Repetir la misma apertura y Escape sin elegir una opción. No se da todavía
por aceptado este recorrido hasta confirmación del usuario. Zoom real 200 % pendiente.

## 8B — cierre repetido de Secciones confirmado, 27/10/2026

El usuario confirma «recorrido OK» al abrir Secciones, mantener visible el panel lateral
sin seleccionar destino, pulsar Escape y comprobar cierre/foco en el disparador, repitiendo
la secuencia. La incidencia reportada queda aclarada en este alcance: Escape con el panel
cerrado no es un atajo global de retorno desde el formulario. No fue necesaria una
corrección adicional de producto por este caso; permanecen las cinco pruebas de repetición
aprobadas. No atribuir a esta confirmación otros recorridos no ejecutados.

Pendientes del guion 8B: zoom real del navegador al 200 %, ampliar con Secciones abierto
y comprobar foco en la barra; Atrás/Adelante con contenido conservado. La secuencia móvil
entre los tres pasos y el cierre sobre fondo exterior no se dan por aceptados únicamente
por este OK de Escape. Sin commit/push de 8B ni inicio del lote 9.

## 8B — zoom real 200 % confirmado, 27/10/2026

Usuario confirma «recorrido OK» al ampliar la ventana, ajustar el zoom real del navegador
al 200 %, abrir Secciones, leer y seleccionar pasos EIPD sin contenido cortado ni
desplazamiento horizontal de toda la página, y restituir 100 %, sin recargar ni guardar.
Esta confirmación cubre el control real del navegador, que antes permanecía pendiente;
no equivale a certificación de accesibilidad ni a prueba manual con lector de pantalla.

Pendientes: ampliación con Secciones abierto y foco en la barra visible; Atrás/Adelante
con nota conservada. No atribuir todavía cierre exterior o secuencia móvil de tres pasos
por este OK de zoom. Sin commit/push de 8B ni inicio del lote 9.

## 8B — ampliación y foco en barra confirmados, 27/10/2026

Tras precisar usar la pestaña actualizada donde aparece Paso 3 de 7, abrir Secciones y
maximizar la ventana hasta mostrar la barra superior, el usuario confirma «recorrido OK»:
el panel se cierra y el foco pasa a una opción de la barra. Las capturas anteriores de
ventanas todavía estrechas no se interpretan como fallo de ese cambio de ancho.
Se suma al zoom real 200 % y Escape repetido ya confirmados. No implica validación de
contenido pendiente de una pestaña antigua ni sincronización entre pestañas.

Siguiente comprobación: en la misma pestaña actualizada, Describir riesgos → Valorar riesgos
→ Medidas de mitigación; Atrás del navegador debe volver al Paso 4, Adelante al Paso 5.
Volver a Describir riesgos y comprobar la nota ficticia pendiente sin guardar ni recargar.
El recorrido móvil de esos tres destinos y cierre exterior conserva cobertura automatizada;
no atribuir aceptación manual adicional sin confirmación específica. Sin publicación de 8B.

## 8B — Atrás/Adelante y conservación confirmados, 27/10/2026

Usuario confirma «recorrido OK» tras Describir riesgos → Valorar riesgos → Medidas de
mitigación; Atrás del navegador vuelve al Paso 4 y Adelante al Paso 5. Al volver a
Describir riesgos se conserva la nota ficticia de navegación 8B, sin guardar ni recargar.
Este resultado completa la comprobación asistida de navegación histórica del guion.

Queda para completar la aceptación acotada de 8B: repetir los tres destinos desde
Secciones en ventana estrecha, comprobar la nota y cerrar el panel mediante clic en el
fondo gris exterior. No confundir con Escape repetido y zoom 200 %, ya confirmados.
La parte pendiente dispone de cobertura automatizada, pero aún no se atribuye al usuario.
Sin commit/push de 8B ni inicio del lote 9. Lector manual de 7B sigue pendiente.

## 8B — recorridos asistidos completados, 27/10/2026

Usuario confirma «recorrido OK» al reducir la ventana, recorrer desde Secciones Describir
riesgos → Valorar riesgos → Medidas de mitigación, volver a Describir riesgos y comprobar
la nota conservada; abrir Secciones y cerrar mediante clic en el fondo gris exterior con
foco de retorno al disparador, sin guardar ni recargar.

Con esta confirmación se completan los recorridos asistidos acordados de 8B: título/Paso N
de 7 y lista central retirada; secuencia Anterior/Siguiente con conservación; panel móvil,
Escape repetido y cierre exterior; zoom real del navegador 200 %; ampliación y foco en barra;
Atrás/Adelante y nota conservada. El caso de Escape con panel cerrado quedó aclarado como
expectativa de un atajo global inexistente, sin corrección adicional de producto.

Evidencia automatizada: 111 escenarios aprobados en la ejecución de regresión (91 conectados
+ 20 independientes), más cinco escenarios nuevos de aperturas repetidas ejecutados y
aprobados separadamente (25 ciclos). Total: 116 escenarios distintos aprobados en esas dos
ejecuciones; no presentar una única ejecución conjunta de 116 ni sumar reejecuciones como
escenarios nuevos. Tipos/lint/formato y capturas previas conservan su alcance.

Listo para commit/push de 8B cuando el usuario lo autorice. Sin publicación, merge o
despliegue; lote 9 no iniciado. No declara certificación de accesibilidad, integración real
por estas pruebas automatizadas o CI remota nueva; lector manual de 7B pendiente.

## Publicación autorizada de 8B — 27/10/2026

Usuario solicita commit y autoriza push de `feature/navegacion-8b-pasos`, base `e04d8d8`.
Incluye navegación principal EIPD, título/Paso N de 7, Anterior/Siguiente, foco al cambiar
ancho, pruebas y aceptación asistida. Evidencia: 111 escenarios de regresión más cinco de
repetición aprobados en ejecuciones separadas; tipos/lint/formato y capturas aprobados.
Lector manual de 7B pendiente. No atribuir CI remota nueva al push.
Las menciones inferiores de autorización pendiente son antecedentes. Excluir next-env.d.ts
generado y outputs/ locales. Lote 9 no iniciado; sin merge/despliegue. Verificar HEAD remoto.

## Bloque 9A — pendientes identificables, 28/10/2026

Implementación local en `feature/navegacion-9a-pendientes`, base publicada
`a1c93c173045035c27c4ff8b3bbf4ce7d0e62868` (8B). Usuario solicita continuar 9A;
no hay autorización nueva de commit/push. Pendiente aceptación asistida.

### Unidad guardable y alcance implementado

Una unidad representa una acción independiente de guardado o registro, no cada pantalla:

| Unidad | Identidad y efecto |
| --- | --- |
| Determinación | EIPD e infancia forman un único formulario por evaluación. |
| Base de licitud y fundamento | Un formulario por evaluación. |
| Borrador EIPD | Los siete pasos comparten una unidad por evaluación. |
| Antecedentes de infancia | Guardado separado por evaluación. |
| Preparación de nueva versión de infancia | Temporal en la pestaña; requiere registrar explícitamente una versión. |
| Valoración de riesgos | Independiente del documento EIPD y del anexo. |
| Anexo en preparación | Formulario independiente, incluido archivo seleccionado; sin copiar contenido a la lista. |
| RAT | Información general y cada sección con guardado separado se informan por separado. Nueva actividad es otra unidad. |
| Autodiagnóstico | Un cuestionario por organización; sus secciones no multiplican el conteo. |
| Mi organización | Un formulario por organización. |
| Creación de evaluación | Preparación distinta de la evaluación existente; informa el tratamiento elegido en ese formulario. |

La cabecera ofrece **Ver pendientes (N)**. Su panel muestra nombre, contexto disponible,
estado y origen de cada unidad pendiente, con cierre explícito, Escape, fondo exterior y
retorno de foco. El resumen vacío dice que no hay pendientes *informados*; no afirma que
los formularios estén completos o guardados. No lista contenido de campos, archivos ni
credenciales. Los enlaces de retorno y confirmación al cambiar contexto siguen en 9B.

Se amplía el contrato mediante descriptores con identidad estable, contexto, destino
canónico y origen formulario/temporal. En los editores de evaluación se reportan sin consulta,
consultando, consultado sin cambios, editado, guardando, guardado confirmado y error según
la operación real. Una lectura exitosa nunca se transforma en confirmación de escritura.
Los callbacks antiguos de otros formularios aportan solo edición pendiente; su `false`
no se convierte en «guardado». El conteo no utiliza el booleano agregado por evaluación.
No altera estados de dominio, contratos API, autorizaciones ni contenido de documentos.

Los avisos locales junto al guardado permanecen. Consultar/reintentar no retira unidades
editadas ni guarda el formulario. Guardar una unidad no limpia las demás. La lista y los
borradores siguen en memoria de la pestaña: sin autosave ni almacenamiento nuevo en
localStorage/sessionStorage. No sincroniza otras pestañas. Confirmación/activación EIPD
permanecen bloqueadas; no implica aprobación jurídica ni auditoría de eventos históricos.

### Evidencia ejecutada localmente

- **190 escenarios Chromium aprobados en una ejecución final** de navegación conectada,
  espacio de licitud, editor de infancia, historial de infancia y valoración/anexos.
  Incluye nueve escenarios nuevos 9A: vacío sin guardado falso, dos unidades frente a
  varios pasos EIPD, guardado parcial, error/reintento, aislamiento por evaluación,
  panel a 320/1280 px, valoración/anexo separados, preparación temporal/infancia separados
  y ámbito de RAT/autodiagnóstico al cambiar de módulo.
- TypeScript, ESLint dirigido, Prettier y `git diff --check` aprobados.
- Capturas de panel a 320/1280 px inspeccionadas visualmente. Registro local:
  `outputs/9a/regression.log`; capturas `outputs/9a/9a-pendientes-*.png`, no versionadas.
- Los primeros intentos de pruebas se ajustaron a rótulos/selección visible reales y a
  los requisitos existentes: no se desbloqueó valoración con borrador EIPD sucio ni
  preparación con infancia sin guardar. La fixture válida de política de infancia
  respeta el contrato y solo se usa en su escenario 9A.
- Son pruebas con API simulada, no integración real del servidor, CI remota, prueba
  manual de lector de pantalla ni certificación de accesibilidad. Se conserva el
  pendiente de lector manual de 7B.

### Checklist de aceptación asistida 9A

Usar `/dashboard/trabajo`, una pestaña actualizada y datos ficticios. Si la pestaña antigua
no muestra Ver pendientes, abrir su dirección en una pestaña nueva y dejar la original
abierta; los cambios no guardados de la original no se trasladan automáticamente.

- [ ] Inicio: Ver pendientes (0) abre un panel vacío que no anuncia «todo guardado».
- [ ] En una evaluación con EIPD habilitada, escribir una nota ficticia en el borrador:
  aparece una unidad; cambiar por varios pasos no la multiplica.
- [ ] Volver a Determinar aplicabilidad y añadir una línea al fundamento sin cambiar la
  determinación guardada: aparecen dos unidades con nombres y contexto correctos.
- [ ] Guardar solo la determinación mediante su declaración ficticia: queda pendiente
  únicamente EIPD; volver a su formulario conserva la nota.
- [ ] En ventana estrecha, abrir/cerrar Ver pendientes con Escape y fondo gris exterior;
  el foco vuelve al botón y el texto es legible.
- [ ] Error de consulta y reintento conservan la unidad y el contenido sin anunciar
  guardado; si se usa simulación de desconexión, restaurar conexión antes de continuar.

No iniciar 9B ni publicar hasta la siguiente instrucción/autorización correspondiente.
Excluir `frontend/next-env.d.ts` generado y `outputs/` al preparar una publicación.

## 9A — conteo e identificación confirmados, 28/10/2026

Usuario confirma «recorrido OK» en el primer recorrido asistido. La captura muestra
Unidades de trabajo pendientes (2): Determinación de aplicabilidad y Borrador EIPD ·
siete pasos, ambos para CumpleIA Demo / Gestión de clientes / finalidad de citas /
evaluación versión 1, borrador. El recorrido comunicado incluye cambiar de paso EIPD
sin multiplicar su unidad. Se valida este alcance; no se atribuye aún aceptación de
guardado parcial, recuperación de errores o cierres en ventana estrecha.

Siguiente comprobación: cerrar el panel, guardar solo la determinación con su declaración
ficticia, comprobar Ver pendientes (1) con únicamente el borrador EIPD y volver a sus
notas para verificar conservación. Sin guardar EIPD ni recargar durante esta prueba.
Sin commit/push de 9A; 9B no iniciado. Lector manual de 7B pendiente.

## 9A — guardado parcial y nota conservada confirmados, 28/10/2026

Usuario confirma «recorrido OK» tras cerrar Pendientes, guardar únicamente la
determinación con la declaración ficticia, comprobar Ver pendientes (1) con solo
Borrador EIPD y volver a la EIPD con la nota conservada, sin guardar EIPD ni recargar.
Se valida el retiro individual del pendiente guardado y la conservación del otro.
No implica aceptación todavía del cierre en ventana estrecha ni recuperación de errores.

Siguiente comprobación: reducir la misma ventana, abrir Ver pendientes (1), revisar
lectura/contexto y cerrar mediante Escape con foco de retorno al botón. Reabrir y cerrar
mediante clic en el fondo gris exterior al panel, comprobando el mismo retorno de foco.
No guardar ni recargar. Sin commit/push de 9A ni inicio de 9B; lector manual de 7B pendiente.

## 9A — panel estrecho y cierre confirmados, 28/10/2026

Usuario confirma «recorrido OK» al reducir la misma ventana, abrir Ver pendientes (1),
leer el contenido completo, cerrar mediante Escape con retorno de foco al disparador,
reabrir y cerrar mediante clic en el fondo gris exterior al panel con el mismo retorno.
La secuencia se realizó sin guardar ni recargar. Se valida este alcance del panel;
no implica prueba con lector de pantalla ni aceptación de recuperación de errores.

Siguiente comprobación: mantener el borrador EIPD pendiente, editar el fundamento de
la determinación sin guardar, simular desconexión y consultar la última determinación.
El error debe conservar las dos unidades y sus datos. Restaurar conexión y repetir
la consulta en la misma pestaña: el borrador de determinación y el EIPD siguen pendientes,
sin confirmación falsa de guardado. No recargar ni guardar para esta comprobación.
Sin commit/push de 9A ni inicio de 9B; lector manual de 7B pendiente.

## 9A — recuperación confirmada y recorridos acordados completados, 28/10/2026

Usuario confirma «recorrido OK» al mantener el borrador EIPD, añadir la línea ficticia
de recuperación al fundamento de determinación sin guardar, simular Offline y consultar.
La primera captura muestra error de conexión en español y Ver pendientes (2). Tras
restaurar No throttling y repetir en la misma pestaña, la segunda muestra Consulta
completada, aviso de conservación de cambios y Ver pendientes (2), sin éxito de guardado.
La confirmación del recorrido cubre la conservación de la línea añadida y de ambos
pendientes, sin guardar ni recargar. Las capturas por sí solas no muestran todo el texto
de los borradores; esa conservación se registra como confirmación del usuario.

Quedan completados los recorridos asistidos acordados de 9A: identificación/contexto y
conteo sin multiplicar pasos EIPD; guardado de una sola unidad y conservación de la otra;
lectura/cierre/foco en ventana estrecha; desconexión y consulta recuperada conservando
pendientes y sin simular escritura. Los escenarios adicionales de formularios, contextos
y preparación temporal mantienen la cobertura automatizada documentada: 190 escenarios
Chromium aprobados en la ejecución final, incluidos nueve específicos 9A. No se atribuye
al usuario ejecución asistida adicional de todos esos escenarios.

9A listo para commit/push cuando el usuario lo autorice. No se publica, no se inicia 9B,
no hay merge/despliegue ni habilitación EIPD. Lector manual de 7B pendiente; sin nueva
prueba manual de lector, certificación de accesibilidad ni CI remota atribuida.
La casilla de inicio vacío del guion detallado tiene cobertura automatizada; no se marca
como ejecución asistida explícita si no fue confirmada separadamente.

## Publicación autorizada de 9A — 28/10/2026

Usuario solicita commit y autoriza push de `feature/navegacion-9a-pendientes`, base
`a1c93c1`. Incluye unidades pendientes, estados UI, panel consultable, pruebas y
validación asistida acordada. 190 escenarios Chromium y checks estáticos previamente
aprobados; los últimos cambios solo registran los resultados asistidos y esta autorización.
No atribuir CI remota ni integración real a las pruebas con fixtures. Sin merge/despliegue,
9B no iniciado y lector manual de 7B pendiente. Excluir next-env.d.ts generado y outputs/.
Las entradas inferiores de autorización pendiente son antecedentes. Verificar identidad
remota después del push.

## Bloque 9B — destinos de pendientes, 28/10/2026

Rama `feature/navegacion-9b-destinos`; base 9A publicada `650c766a28912f37120a22d7c2c47913e21cdd58`.
Se consultó origin antes de iniciar. Los registros anteriores de «9B no iniciado» describen antecedentes.

### Implementación

- Cada unidad muestra su destino y la acción «Ir a …». Se validan ruta, pertenencia
  organizacional y respuesta del tratamiento/evaluación antes de navegar; cancelar
  invalida una consulta en curso para impedir un cambio tardío.
- Si cambia organización, tratamiento o evaluación, Pendientes muestra contexto actual,
  contexto de destino y pantalla antes de confirmar. Cancelar mantiene ruta y datos,
  y devuelve el foco al acceso del pendiente. Abrir no guarda ni copia borradores.
- Cambiar contexto muestra selección propuesta, pantalla de destino y efecto sobre los
  pendientes antes de Aplicar. El destino mostrado usa la misma función que la navegación.
- Retorno de autodiagnóstico desde resultados lleva al cuestionario. La creación de una
  evaluación vuelve al formulario ya iniciado en su panel propietario; no crea otra evaluación.
- Antes de abrir desde Pendientes se renueva la consulta de aplicabilidad. Mientras se
  consulta no se expone el editor condicionado con permisos almacenados. Si ya no está
  disponible, se explica el retorno a Determinar aplicabilidad. Los editores permanecen
  montados y conservan sus campos; se puede recuperar el pendiente al habilitarse nuevamente.
- El aviso junto al contador permanece en la cabecera también con cero pendientes, con
  ancho mínimo del contador y texto adaptable. No se impone una altura que recorte contenido.

Conservar en memoria no equivale a guardar en servidor: borradores solo durante esta
visita y pestaña. Sin autosave, nuevo almacenamiento, cambios API/backend/migraciones,
permisos o reglas de riesgo. Confirmación y activación EIPD permanecen bloqueadas.

### Checklist asistido 9B — pendiente

Usar `/dashboard/trabajo` y datos ficticios. No recargar una pestaña con cambios.
Si la pestaña antigua no muestra «Ir a …», abrir la misma dirección en otra pestaña
actualizada y realizar allí un escenario nuevo; los cambios de la original no se trasladan.

- [ ] En evaluación con EIPD habilitada, escribir una nota ficticia sin guardar; añadir
  una línea ficticia al fundamento de determinación sin modificar el estado guardado.
  Ir a Panel, abrir Ver pendientes (2), usar «Ir a Borrador EIPD · siete pasos» y comprobar
  la nota. Repetir desde Panel con Determinación y comprobar la línea.
- [ ] Cambiar contexto con esos pendientes: leer pantalla de destino antes de Aplicar.
  Cancelar conserva selección, pantalla y texto. Aplicar conserva las unidades previas.
- [ ] Desde otra evaluación, ir al pendiente anterior: leer «Antes de cambiar de contexto»,
  cancelar y comprobar permanencia; volver a abrir y confirmar el destino correcto.
  Notas ficticias distintas por evaluación no deben mezclarse.
- [ ] Con un acceso condicionado ya no disponible, el retorno explica la causa y mantiene
  el pendiente. Al restaurar la determinación mediante el flujo explícito, se recupera el
  texto anterior. No registrar versiones para comprobar únicamente navegación.
- [ ] En ventana estrecha abrir/cerrar panel con teclado, Escape y fondo exterior; comprobar
  foco y lectura completa. Al quitar/agregar un pendiente la cabecera no salta por el aviso.
- [ ] Advertencia de salida/recarga sigue disponible con cambios. No aceptar una recarga
  para conservarlos; consultar o navegar no debe anunciar guardado.

### Evidencia automatizada

200 escenarios Chromium aprobados en la ejecución final de cinco archivos:
`connected-navigation`, `licitud-workspace`, `child-adolescent-editor`, `child-eipd-history`
y `assessment-support`. Incluye diez casos nuevos 9B: retorno EIPD/determinación,
cancelación y confirmación entre evaluaciones con notas distintas, anticipación en Cambiar
contexto, consulta fresca y reubicación, error y cancelación de consulta lenta,
cuestionario desde resultados, creación en panel original, cabecera/teclado a 320 y
1280 px y preparación temporal bloqueada/recuperada. Se comprueba ausencia de escrituras
adicionales por abrir o cancelar. Regresiones previas cubren aviso de salida, cierres,
foco y nombres largos. Tipos, ESLint y formato de archivos afectados aprobados.
Captura local de confirmación de contexto inspeccionada: texto y acciones legibles,
panel desplazable sin recorte horizontal. Evidencias locales en `outputs/9b/`, excluidas
del repositorio. No se modifica `frontend/next-env.d.ts` generado por la ejecución.

No atribuir aceptación asistida, prueba de lector de pantalla, integración backend real
ni CI remota a las pruebas con fixtures. Sin commit/push de 9B ni inicio del lote 10.

## 9B — retorno, cambio de contexto y panel estrecho confirmados, 28/10/2026

Usuario confirma «recorrido OK» en tres secuencias asistidas:

- Desde Panel, localizar las unidades de determinación y EIPD y volver a cada formulario
  con sus textos conservados.
- Cambiar contexto y conservar los dos pendientes de clientes al seleccionar trabajadores.
  La captura muestra trabajadores como contexto actual y ambas unidades de clientes con
  sus destinos. Usuario confirma después cancelar la apertura del pendiente sin cambiar
  contexto y confirmar el retorno a clientes con la nota EIPD conservada.
- Reducir la misma ventana, leer nombres y botones completos, cerrar con Escape y con
  fondo gris exterior al panel, con retorno de foco a Ver pendientes, sin guardar ni recargar.

Esta aceptación no atribuye comprobación asistida adicional de acceso condicionado,
preparación temporal o advertencia de recarga. Esos casos conservan la cobertura automatizada
previamente documentada. Siguiente recorrido: comprobar la advertencia de salida/recarga
con dos pendientes y cancelar la salida, verificando contexto y nota conservados.
No aceptar la recarga ni abandonar la pestaña durante la comprobación. Sin commit/push
nuevo autorizado de 9B; lote 10 y lector manual de 7B siguen pendientes.

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

## Bloque 10A — acciones y requisitos por documento, 28/10/2026

Rama `feature/navegacion-10a-capacidades`, base 9B publicada
`1429f1d4bc311a707cf48a5b3a6601b4b2842748`. Se consultó origin y las reglas
vigentes antes de iniciar. El repositorio confirma que EIPD general y versiones de
infancia tienen capacidades distintas; el resumen se deriva de esos contratos.

### Implementación y límites

Resumen «Acciones y requisitos» con estados «Disponible», «No disponible» y «Por comprobar»:

- Borrador EIPD general: editar/guardar según carga, rol, estado, operación en curso y
  resultado incierto. Guardar actualiza el documento y no crea una versión registrada.
  Revisión o decisión formal del circuito de infancia no disponible para este objeto.
- Consulta de EIPD guardada: lectura del contenido del servidor; no incluye ediciones
  pendientes ni admite edición en esa consulta. Explica que editar requiere el flujo
  Completar EIPD con su determinación y controles efectivos.
- Versión histórica de infancia: identidad por número y referencia; original no editable.
  Preparar desde ella produce una copia temporal. Revisión documenta únicamente
  Requiere cambios o No continuar sobre esa versión; no se introduce revisión favorable.
- Preparación temporal: distingue completar/vista previa de registrar. Explica declaración,
  referencia, cambios del material por guardar y lectura de vista previa cuando corresponde.
  Registro explícito crea una versión nueva; copiar o previsualizar no registra.
- Decisión organizacional: capacidad y razones consultadas para la sesión; facultad ausente,
  revocada, rol/estado de solo lectura, declaración y campos requeridos. Owner/admin no
  equivale a facultad. Gestionar facultades distingue permiso administrativo y designación.
- Sin consulta o ante error no se informa facultad ni edición como comprobada. Una nueva
  carga de aceptación retira su snapshot anterior durante la consulta. No se vacían campos.
- Ante material obsoleto/no disponible informado en eventos se explica que la decisión
  histórica se conserva y no acredita decisión sobre material actual. No se infiere la
  invalidez de otras versiones ni se calcula asociación de hashes en la interfaz. El servidor
  sigue validando material/facultad al registrar; el resumen no otorga autorización.
- Confirmación y activación permanecen bloqueadas, incluso tras Acepta el documento.

Resumen informativo: no duplica botones ni introduce nuevos registros, rutas, permisos,
endpoints, dependencias o reglas jurídicas. Se conservan controles, referencias, versiones,
preparaciones y borradores. Sin cambios backend/API/migraciones ni sincronización entre
pestañas. Solo datos ficticios. 10B no iniciado.

### Checklist asistido 10A — completado con alcance documentado

Usar `/dashboard/trabajo`. Conservar la pestaña original si tiene cambios; para cargar
los nuevos controles usar otra pestaña y un escenario ficticio independiente.

- [x] En una evaluación con EIPD habilitada, ir a Completar EIPD → Tratamiento y alcance.
  Al final del formulario, junto a las acciones de guardado y antes de Diagnóstico del
  servidor, leer Acciones y requisitos. Debe distinguir editar/guardar de revisión o
  decisión formal no disponible y de confirmación/activación bloqueadas.
- [x] En Documentos guardados, si existe EIPD general guardada, comprobar resumen de consulta
  y diferencia respecto de versiones registradas de infancia. No guardar solo para probar
  el rótulo; si no existe documento, registrar el caso como no disponible para esta sesión.
- [x] En contexto de infancia con versiones existentes, consultar una versión. Ver su número
  y referencia en el resumen; editar original no disponible, preparación de copia temporal,
  revisión negativa y decisión organizacional separadas. Consultar no envía registros.
- [x] Seleccionar Decisión de la organización. Leer el motivo de bloqueo correspondiente
  a facultad ausente/revocada o los requisitos pendientes si está otorgada. No designar ni
  revocar facultades para comprobar un texto. Las decisiones históricas siguen consultables.
- [x] En Preparar nueva versión documental de infancia, distinguir completar, vista previa
  y registrar, con requisito faltante explicado. No registrar otra versión para probar el panel.
- [x] Volver a un borrador con nota ficticia pendiente y comprobar su conservación. Reducir
  ventana y verificar texto legible, estados expresados con palabras y sin recorte horizontal.

### Evidencia automatizada y visual

223 escenarios Chromium aprobados en una ejecución de seis archivos: navegación conectada,
workspace de licitud, editor de infancia, historial de infancia, valoración/anexos y
aceptación de organización. Incluye 11 casos nuevos 10A: EIPD general y conservación de
nota, referencia de versión histórica, requisitos de preparación/vista previa, facultad
ausente/otorgada/revocada, material obsoleto/no disponible, error/carga pendiente y
lectura sin desbordamiento a 320/1280 px. No se registran actuaciones al consultar los
resúmenes. Casos anteriores mantienen validación de consulta/solo lectura, expediente
confirmado, respuesta incompatible, conflicto y resultado incierto.

Después de precisar el rótulo «Registrar facultad» y sus requisitos (distinto de abrir
Gestionar facultades), se repitieron los 17 escenarios de aceptación: aprobados.
Tras ajustar únicamente la toma de capturas, se repitieron dos casos de anchos: aprobados.
Tipos, lint y formato de archivos afectados aprobados. Capturas 320/1280 inspeccionadas:
estados expresados con texto, ancho adaptable, inicio visible bajo la cabecera y lectura
por desplazamiento en móvil. Evidencias locales `outputs/10a/` excluidas de publicación.

La cobertura con fixtures no equivale a integración backend real, CI remota o aceptación
asistida; lector manual de 7B pendiente. No se realiza commit/push hasta autorización.

## 10A — recorridos asistidos disponibles comprobados, 28/10/2026

Las capturas aportadas por el usuario muestran:

- EIPD general: resumen con editar/guardar disponible y revisión/decisión formal y
  confirmación/activación no disponibles.
- Documentos guardados de clientes: no hay documento EIPD guardado en este contexto.
  La consulta del resumen de una EIPD general existente queda pendiente en validación
  asistida; no se creó ni guardó un documento únicamente para comprobar el rótulo.
- Infancia: versión documental 1 con referencia SIMULADA-PILOTO-INFANCIA-RES-001;
  original no editable, copia temporal diferenciada de revisión y decisión.
- Decisión de organización: facultad revocada como causa explícita de bloqueo;
  decisiones históricas consultables y confirmación/activación bloqueadas.
- Preparación temporal: antes de la declaración ficticia explica ese requisito;
  al marcarla permite completar y explica referencia faltante para registrar.
- Tras el recorrido solicitado de consulta y retorno, la última captura en ventana
  estrecha conserva «[Ficticia] Prueba de Infancia Bloque 10A», muestra Ver pendientes (2)
  y texto legible sin recorte horizontal del resumen. No se atribuye guardado o registro
  de nueva versión a estas consultas.

Queda comprobado el alcance asistido disponible en esta sesión. La consulta de EIPD
general guardada sigue pendiente por falta de un caso existente; conserva la cobertura
automatizada previamente documentada. Los escenarios de material obsoleto/no disponible,
carga/error y otras facultades tienen cobertura automatizada, sin atribuir su ejecución
manual al usuario. No se declara validación asistida integral ni prueba con lector.

223 escenarios Chromium con fixtures previamente aprobados, ajuste final de facultad
validado con 17 escenarios dirigidos y dos de capturas. Este registro solo documental
no requiere repetir pruebas de producto. Sin commit/push autorizado de 10A ni inicio
de 10B; lector manual de 7B pendiente. Entradas anteriores son antecedentes.

## 10A — consulta de EIPD general existente comprobada, 28/10/2026

El usuario encontró otra evaluación de Gestión de Clientes con documento EIPD guardado.
La captura muestra referencia PRUEBA-EIPD-LECTURA-20261010 y nombre de edición PRUEBA-2.
El resumen distingue consulta disponible, edición fuera de esa vista, circuito formal
no disponible para EIPD general y confirmación/activación bloqueadas. Queda cubierta
la comprobación del resumen de consulta que antes faltaba por ausencia de documento
en el contexto anterior. El contenido expandible no se muestra abierto en la captura;
no se atribuye inspección de todos sus campos ni escrituras. Se conserva Ver pendientes (2).
Pendiente la confirmación solicitada de retorno a la nota del borrador EIPD original
tras visitar Documentos guardados; la conservación de preparación temporal de infancia
ya tiene evidencia. Sin repetir pruebas automáticas por este registro documental,
sin commit/push autorizado de 10A ni inicio de 10B. Lector manual de 7B pendiente.
Las menciones anteriores a ausencia de un caso de consulta son antecedentes.

## 10A — guion asistido completado, 28/10/2026

Tras informar que había recargado y perdido los pendientes de la pestaña, el usuario
repitió el recorrido con una nota ficticia nueva en el borrador EIPD, fue a Documentos
guardados y volvió al editor. Confirma «recorrido OK»: nota conservada y pendiente
identificable, sin guardar ni recargar durante la repetición. Esta evidencia no implica
recuperación de los borradores anteriores perdidos con la recarga.
Se completa el guion asistido acordado, incluida la consulta de EIPD general guardada
en otra evaluación documentada en la entrada anterior. Casos de carga/error, material
no asociado y facultades adicionales conservan su evidencia automatizada; no se
atribuyen como pruebas manuales. Lector manual de 7B pendiente.
10A listo para commit/push cuando se autorice. Sin publicación de 10A ni inicio de 10B.
Este cierre documental no modifica producto ni requiere repetir la batería previa.

## Publicación autorizada de 10A — 28/10/2026

Usuario solicita commit y autoriza push de feature/navegacion-10a-capacidades,
base 1429f1d. Incluye resumen de acciones y requisitos por documento, sus pruebas
y el guion asistido completado documentado. Evidencia previa: 223 escenarios Chromium,
17 dirigidos tras precisar facultad, dos de capturas y checks estáticos aprobados.
No se repiten pruebas por las últimas entradas documentales ni se atribuye CI remota.
Excluir frontend/next-env.d.ts generado y outputs/. Verificar identidad remota tras push.
Sin merge, despliegue ni inicio de 10B. Lector manual de 7B pendiente.
Las menciones anteriores a autorización pendiente son antecedentes.

## Bloque 10B — revisión e historial del documento seleccionado, 28/10/2026

Implementado localmente en feature/navegacion-10b-historial sobre 10A publicada
e3dd155c4a454801efc2c36245afe4cd0b225d43. Se verificó origin y contrato antes de
editar. Se opta por accesos internos y encabezados en los componentes existentes;
no se crean rutas ni se separa el circuito en nuevas pantallas.

### Alcance implementado

- Versión de infancia consultada identificada por número, referencia y fecha UTC.
  Accesos Ir a Revisión del documento, Ver revisiones registradas e Ir a Decisión de
  la organización sitúan foco en su encabezado. Cambiar de actuación conserva los
  formularios montados y su contenido. Volver al documento consultado conserva selección.
- El desplazamiento interno calcula la altura real de la cabecera conectada para
  evitar ocultar destinos al cambiar de ancho; no modifica hash, contexto ni rutas.
- Las revisiones indican versión y referencia revisadas, resultado, fundamento,
  referencia de revisión, fecha UTC y persona registrada por identificador disponible.
  El servidor no aporta un nombre para inventarlo. Se conservan validaciones de
  identidad/asociación y aislamiento por versión existentes.
- Las decisiones tienen acceso a su historial y retorno al panel. Junto al historial
  aparece la identidad de la versión seleccionada; fundamento y acta llevan concepto.
  Revisiones y decisiones siguen siendo operaciones distintas. Los eventos consultados
  no se presentan como auditoría completa del expediente.
- Copiar desde una versión identifica número y referencia de origen de la preparación
  temporal. El original se conserva y se pide nueva lectura de la vista previa antes
  de registrar. El origen temporal se retira tras registrar; no se añade metadata a API.
- No se amplía el circuito formal de la EIPD general, no se introducen revisión favorable,
  permisos, nuevas escrituras, API, migraciones, dependencias ni activación/confirmación.

### Evidencia ejecutada

174 escenarios Chromium aprobados: navegación conectada, historial de infancia y
aceptación organizacional. Incluye tres pruebas nuevas 10B y ampliación del caso
integrado de identidad histórica: accesos con foco visible bajo cabecera a 320/390/1280,
retorno, revisiones separadas al cambiar versión, metadatos y origen de copia.
Los accesos y consultas no generan POST; las escrituras de fixtures solo se usan en
pruebas explícitas de registro. Tras añadir referencia junto al historial de decisiones,
se repitieron los 18 escenarios de aceptación y el integrado de tres anchos: aprobados.
Tipos, ESLint y formato de siete archivos afectados aprobados. Capturas 320/1280
inspeccionadas: lectura por desplazamiento y texto sin recorte horizontal.
Evidencias locales outputs/10b/ excluidas de publicación. No atribuir CI remota,
pruebas de backend real o certificación de accesibilidad a fixtures.

### Checklist asistido — recorrido acordado completado

Conservar pestaña con pendientes; para cargar código reciente usar otra pestaña del
espacio conectado, con datos ficticios. No recargar la pestaña que tenga borradores.

- [x] En Bases de licitud → Documentos guardados, contexto de infancia con versiones,
  consultar una versión y reconocer su número, referencia y fecha.
- [x] Ir a Revisión del documento y Ver revisiones registradas; reconocer resultado,
  fundamento, referencia, fecha y persona por identificador si existen eventos. Volver
  al documento consultado mantiene identidad. No registrar revisión para probar el acceso.
- [x] Consultar otra versión y volver a la primera. Revisiones y decisiones pertenecen
  a la versión seleccionada; ausencia de eventos no reutiliza antecedentes de otra.
- [x] Ir a Decisión de la organización, Ver decisiones registradas de esta versión y
  volver. Distinguir decisión de revisión; facultad revocada conserva consulta histórica.
- [x] Preparar copia con preparación existente muestra confirmación de reemplazo y opción
  Conservar documento en preparación, como en la captura del usuario. El origen de una
  copia nueva conserva prueba automatizada; no se atribuye su inspección manual. No
  registrar otra versión para probar textos.
- [x] Repetir accesos internos en ventana estrecha y con teclado; destino con foco visible,
  texto sin recorte bajo cabecera y borradores conservados.

Pendiente validación conjunta; sin commit/push autorizado de 10B ni inicio de 11A.
Lector manual de 7B permanece pendiente. Las entradas anteriores son antecedentes.

## 10B — primer recorrido OK y accesos destacados, 28/10/2026

Usuario confirma «recorrido OK» para ir a revisión, ver revisiones y volver al documento
seleccionado. Observa que estos accesos se confunden con el contenido y solicita fondo suave.
Se aplica a los seis accesos internos de revisión, decisión, historiales y retorno un
estilo común: fondo azul suave, texto azul oscuro seminegrita, borde, hover y foco de
teclado visibles; altura mínima 44 px y texto adaptable. Las acciones de registro no
adoptan este estilo. Sin cambios de navegación ni permisos.
Tras el ajuste visual: cuatro escenarios dirigidos aprobados (tres 10B e integrado de
identidad/foco a 320/390/1280); tipos, ESLint, formato y diff-check aprobados. Capturas
320/1280 inspeccionadas, botones legibles y sin recorte horizontal. La batería previa
de 174 escenarios se conserva como evidencia anterior, no se atribuye otra ejecución.
Pendiente confirmación visual del usuario y restantes recorridos asistidos de 10B.
Sin commit/push autorizado de 10B ni inicio de 11A. Lector manual de 7B pendiente.

## 10B — diseño de accesos aceptado, 28/10/2026

Usuario confirma «Ok el nuevo diseño» tras destacar los seis accesos internos con
fondo azul suave, texto oscuro, borde y foco visible. Queda aceptado ese ajuste visual,
sumado al primer recorrido de revisión/historial y retorno ya confirmado.
Siguiente comprobación asistida: alternar dos versiones de infancia y volver a la
primera, verificando identidad y antecedentes propios. No registrar actuaciones.
Restantes recorridos de 10B pendientes; sin commit/push autorizado ni inicio de 11A.
Este registro documental no modifica producto ni requiere repetir las pruebas previas.
Lector manual de 7B pendiente. Entradas anteriores son antecedentes.

## 10B — alternancia de versiones OK y consultas destacadas, 28/10/2026

Usuario confirma «recorrido OK» al alternar versiones de infancia y volver a la primera.
Solicita destacar también Consultar versión documental, Actualizar historial de infancia,
Consultar valoración y anexos y accesos equivalentes porque se confunden con texto.
Se extiende el estilo azul suave aprobado a esos controles y a actualización de aceptación,
descarga de anexos, gestionar/consultar historial de facultades, consulta de alcance RAT,
evaluación de licitud/LIA, contenido documental guardado, identidad del registro y
Anterior/Siguiente del paso EIPD. Los desplegables conservan marcador nativo y teclado.
Los botones deshabilitados se atenúan; altura mínima 44 px, texto adaptable y foco visible.
La lista de versiones separa los botones con espacio. No se modifica la operación de los
controles: algunos actualizan consultas o abren contenido en esta misma pantalla, no otra página.
Guardar/registrar y los formularios conservan sus operaciones y restricciones.

Tras este ajuste: cuatro pruebas dirigidas 10B/integración aprobadas y 52 escenarios de
valoración/anexos, workspace de licitud y editor de infancia aprobados en otra ejecución.
Tipos, ESLint y formato aprobados. Capturas de consulta de versión a 320/1280 inspeccionadas:
accesos destacados y textos sin recorte horizontal. La batería de 174 anterior es antecedente,
no se atribuye como repetida tras este cambio visual. Evidencias locales outputs/10b/.
Pendiente aprobación visual de este ajuste y restantes recorridos asistidos (decisiones,
origen de preparación y teclado/ventana estrecha). Sin commit/push de 10B ni inicio de 11A.
Lector manual de 7B pendiente.

## 10B — diseño ampliado de consultas aceptado, 28/10/2026

Usuario confirma «OK nuevo diseño» después de destacar consultas de versiones,
actualización de historiales, valoración/anexos y accesos equivalentes. Se acepta ese
ajuste visual; primer recorrido y alternancia de versiones ya confirmados.
Siguiente recorrido: acceder a Decisión de la organización de una versión de infancia,
consultar su historial y volver conservando identidad; no registrar decisión ni facultad.
Preparación/origen y repetición con teclado/ventana estrecha siguen pendientes del guion.
Sin commit/push autorizado de 10B ni inicio de 11A; lector manual de 7B pendiente.
Registro documental, sin repetir pruebas de producto. Entradas anteriores son antecedentes.

## 10B — decisiones e historial confirmados OK, 28/10/2026

Usuario confirma «recorrido OK» del acceso a Decisión de la organización, consulta
histórica y retorno. Capturas muestran versión documental de infancia 1, referencia
SIMULADA-PILOTO-INFANCIA-RES-001, nombre de edición PRUEBA-1 y ausencia de decisiones
organizacionales registradas. Historial de facultades visible: otorgamiento seguido
de revocación. No se atribuye nueva decisión, facultad o registro a este recorrido.
Se confirma el recorrido disponible sin decisiones existentes; no se infiere historial
de decisiones poblado a partir de los eventos de facultades, que son distintos.
Pendientes: origen de copia temporal y repetición con teclado/ventana estrecha.
Sin commit/push autorizado de 10B ni inicio de 11A. Lector manual de 7B pendiente.
Registro documental: no requiere repetir pruebas automáticas ya ejecutadas.

## 10B — confirmación de copia observada y botón destacado, 28/10/2026

Usuario informa «recorrido OK» y solicita destacar Preparar nueva versión a partir de
esta como los accesos anteriores. Captura muestra la confirmación de reemplazo por
una preparación ya existente (Ver pendientes 1), con opciones Reemplazar preparación
y Conservar documento en preparación. Esta imagen no acredita ejecución de reemplazo,
copia nueva ni visualización del aviso de origen; no se atribuyen esos efectos.
Se aplica únicamente al botón de preparar copia la clase común azul suave, borde,
texto oscuro y foco. La lógica y protección de reemplazo permanecen sin cambios.
Cuatro pruebas dirigidas de copia, solo lectura, confirmación/conservación y origen
aprobadas; tipos, ESLint y formato aprobados. Sin nueva batería completa por este ajuste.
Pendiente confirmación visual; la protección de una preparación existente es el caso
asistido disponible, origen nuevo conserva evidencia automatizada. Resta teclado y
ventana estrecha. Sin commit/push de 10B ni inicio de 11A; lector manual de 7B pendiente.

## 10B — recorrido asistido acordado completado, 28/10/2026

Usuario confirma «recorrido OK» tras el recorrido final en ventana estrecha con Tab/Enter:
Ver revisiones registradas y Volver al documento consultado, destino visible bajo
cabecera, texto legible y selección/preparación pendiente conservadas según el guion.
Se suma a revisión e historial, alternancia de versiones, decisiones y retorno ya
confirmados, y a la aceptación de los estilos visuales solicitados.
En copia temporal, la captura disponible muestra protección de una preparación
existente mediante confirmación de reemplazo; origen de copia nueva conserva evidencia
automatizada, sin afirmar visualización manual de ese aviso. Decisiones sin registros
es el caso manual disponible; eventos poblados y escenarios excepcionales mantienen
cobertura automatizada. No se registraron actuaciones nuevas para verificar navegación.
Guion asistido acordado completado con estos límites; no certifica accesibilidad integral.
Lector manual de 7B pendiente. 10B listo para commit/push al autorizarse; sin publicación
ni inicio de 11A. La última actualización es documental, sin repetir pruebas de producto.
Evidencia previa: 174 Chromium, posteriores ajustes dirigidos (18 y un integrado,
cuatro dirigidos, 52 de componentes afectados y cuatro de copia en ejecuciones separadas),
checks estáticos y capturas documentados. No se suman ejecuciones repetidas como casos únicos.

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

### Recorrido asistido 11A — pendiente

1. Completar EIPD → Tratamiento y alcance de la EIPD: revisar ayudas de referencia,
   nombre de edición, finalidad y códigos. Confirmar que aclaran qué ingresar.
2. Escribir una nota ficticia sin guardar, abrir vista previa y comprobar que advierte
   ediciones pendientes y conserva el texto. Cerrar vista previa y cambiar de paso.
3. Describir riesgos: revisar identificador, descripción, impacto y análisis inicial/residual.
4. Valorar riesgos: revisar horizonte y fundamentos, además de distinción entre inherente,
   residual previsto y actual verificado. Si no hay riesgos guardados, verificar instrucción
   para añadirlos y guardarlos antes de valorar. Probar ventana estrecha sin recargar.

No se pide registrar revisiones, decidir, aprobar ni activar. Pruebas automatizadas usan
fixtures; no se atribuyen escrituras al servidor del usuario ni capturas manuales.

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

## Corrección RAT — recorrido asistido confirmado OK, 29/10/2026

El usuario confirma «recorrido OK» tras probar la reubicación de «Cambios guardados»
encima de «Guardar cambios» en Información general del RAT y el retiro del aviso al
volver a editar. Se conserva la evidencia estática registrada anteriormente (formato,
ESLint, TypeScript y diff). Rama `fix/rat-aviso-guardado`; corrección validada,
pendiente de commit y autorización de push. Sin inicio de 11B. Las notas anteriores
de validación pendiente son antecedentes.


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

## Corrección RAT — publicación autorizada, 29/10/2026

El usuario autoriza commit y push del aviso RAT, separado del bloque 11B.
Recorrido asistido, TypeScript, ESLint, formato y diff aprobados.

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

## 12A — cierre y publicación autorizados, 29/10/2026

El usuario autoriza commit y push del bloque 12A validado, en
`feature/navegacion-12a-recorridos`. Se incluyen las correcciones de progreso,
avisos locales e historial, sus pruebas y la aceptación asistida registrada.
Se conserva la evidencia de pruebas existente; no se repite la batería por este
cierre documental. Excluir `frontend/next-env.d.ts` generado y `outputs/`.
Sin inicio de 12B, merge ni despliegue. Las notas anteriores de publicación
pendiente son antecedentes; el resultado del push se verifica contra la rama remota.


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

### 12B — comprobación asistida de conexión y ajuste del selector

El usuario confirma recuperación de la consulta de aplicabilidad al restablecer
la conexión, conservando el texto pendiente. La captura de la pestaña actualizada
confirma error de conexión en español, reintento de contextos y Aplicar bloqueado.
Se detecta y corrige un aviso contradictorio: la lista vacía solo se anuncia cuando
la lectura termina sin errores. Dos pruebas dirigidas verifican que no aparezca
ese aviso ante fallo de sesión o red y que se conserve el borrador al reintentar.
Pendiente confirmación asistida de recuperación del selector y prueba de sesión real.

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

Guía: [guia-navegacion-trabajo.md](guia-navegacion-trabajo.md).
Aceptación/remanentes: [cierre-navegacion-checklist.md](cierre-navegacion-checklist.md).
Las notas anteriores de no inicio de 13 o publicación pendiente de 12B son
históricas: 12B ya está publicado en `41c561b`. Este bloque 13 aún no tiene
commit/push autorizado. Excluir `frontend/next-env.d.ts` y `outputs/` preexistentes.
Sin merge, despliegue ni cierre implícito de los pendientes funcionales.

## 13 — aceptación asistida: conservación, vista previa y guardado EIPD

El usuario confirma recorrido OK en la evaluación ficticia seleccionada:

- Nota `[FICTICIA] Prueba de cierre 13` conservada al cambiar de módulo y volver por Ver pendientes, con su contexto (13-02 OK).
- Vista previa del borrador con edición pendiente en Finalidad del tratamiento; no guarda ni registra versión.
- Documentos guardados no incorpora esa edición pendiente; al volver al editor siguen finalidad y nota (usuario confirma OK).
- Guardar borrador EIPD explícitamente muestra confirmación; Documentos guardados incorpora la finalidad de prueba y la unidad EIPD deja de figurar en pendientes (usuario confirma OK).

Aclaración de prueba: inicialmente se pidió buscar Notas del borrador EIPD en
la vista previa. La vista EipdDocumentView recorre documentFields y no presenta
esa nota general del editor. Se corrigió la instrucción usando Finalidad del
tratamiento; no se atribuye esa omisión a pérdida del borrador. Contenido preparado
es desplegable y el código lo abre inicialmente; no se reprodujo un fallo de apertura.

Evidencia: confirmaciones textuales del usuario en esta conversación. No hay
captura nueva, identificación completa de la evaluación ni commit del proceso
servido confirmado por captura; referencia de código documental `41c561b`.
No se registró otra determinación en estas pruebas: esa parte de 13-03 sigue No probado.
13-04 a 13-08 pendientes de aceptación integral. Próximo: consultar versión de
infancia y distinguir revisión, decisión y copia temporal sin registrar actuaciones.
Sin nuevo commit/push, merge ni despliegue.

## 13 — consulta de infancia, copia temporal, paneles y conexión aceptados

Contexto observado en capturas: CumpleIA Demo, [FICTICIA] Programa de
fidelización con menores, evaluación versión 1 en borrador. Documento consultado:
versión de infancia 1, SIMULADA-PILOTO-INFANCIA-RES-001.

- Capturas `codex-clipboard-b6ede47e-87c0-48e6-9ced-39814ac7b472.png` y
  `codex-clipboard-5a558875-1e00-44d6-8a22-2e0de27a7e15.png`: accesos de revisión
  y decisión conservan versión 1; la decisión muestra facultad revocada y acciones
  bloqueadas. No se registraron revisiones, facultades ni decisiones.
- Captura `codex-clipboard-9ac64010-cd52-48a6-8382-03a17b0662b3.png`: origen de copia
  temporal desde versión 1, referencia y PRUEBA-1 conservados. Usuario confirma
  vista previa, volver sin registrar, versiones 1 y 2 sin agregar otra y retorno
  por pendientes con la preparación intacta. No acredita por sí sola la prueba
  de cancelar un reemplazo previo.
- Usuario confirma ventana estrecha, Secciones, Escape/foco con aperturas repetidas,
  cierre de Menú por fondo atenuado y conservación de preparación. No se repitió
  zoom 200 % ni lectura manual con tecnología de asistencia en este tramo.
- Usuario confirma fundamento pendiente [FICTICIA] Prueba recuperación 13,
  Offline, consulta con error de conexión, restablecimiento No throttling y nueva
  consulta correcta sin perder el texto ni recargar. Sesión real se conserva como
  evidencia anterior de 12B, no como prueba nueva de 13.

La tabla de aceptación integral mantiene resultados por comprobación, sin ampliar
estos OK a operaciones no ejecutadas. Próximo: ámbitos de Autodiagnóstico, RAT,
Mi organización y localización de anexos; después completar pendientes aplicables.
Sin publicación autorizada de 13 ni cambios en contratos o interfaz.

## 13-08 — ámbitos y formulario de anexos: recorrido asistido OK

El usuario confirma el recorrido de Autodiagnóstico de la organización,
Inventario del programa con menores y Mi organización, sin presentar la
evaluación EIPD como ámbito propio de esos módulos. Confirma retorno a
Preparar → Anexos de respaldo.

La captura `codex-clipboard-9cf65419-e96f-47ba-88e4-6153a4ea2a59.png` muestra
CumpleIA Demo / [FICTICIA] Programa de fidelización con menores, evaluación
versión 1 en borrador; no hay anexos registrados y está visible Agregar anexo
ficticio con referencia, descripción, sección relacionada, vínculos opcionales,
selector PDF/TXT y declaración ficticia. Se ven dos unidades pendientes en
la visita; no se infiere de ese contador que el formulario de carga esté bloqueado.

Resultado 13-08 OK en consulta y localización; no se subieron archivos ni se
modificaron registros para este recorrido. Próximo: zoom 200 % y navegación
con teclado en el cierre 13; lector de pantalla manual permanece pendiente.

## 13-06 — zoom y teclado: recorrido asistido OK

El usuario confirma zoom del navegador al 200 %, acceso con Tab a Menú/Secciones,
apertura con Enter o Espacio, lectura/desplazamiento del panel, cierre con Escape
y retorno del foco; restauración al 100 % sin recargar. Complementa el recorrido
anterior de ventana estrecha y aperturas repetidas. Resultado OK en ese alcance.
No hubo prueba manual con lector de pantalla ni se declara certificación.
Próximo: guardado explícito de determinación ficticia (parte pendiente de 13-03).

## 13-01 y 13-03 — determinación guardada y disponibilidad EIPD

Capturas `codex-clipboard-634b971b-83cf-48a5-a20e-3a61ed34b3d4.png` y
`codex-clipboard-d335d152-bac4-4e2e-8457-50b4f8471743.png`: contexto ficticio
Programa de fidelización con menores; revisión de aplicabilidad 2 asociada al
alcance actual; formulario coincidente con lo consultado en servidor. EIPD queda
Pendiente de analizar e infancia Corresponde; fundamento de infancia conserva
[FICTICIA] Prueba recuperación 13. Consulta completada sin ediciones pendientes
en esa determinación. Una unidad pendiente puede seguir siendo la preparación
temporal de infancia: no se atribuye su identidad al contador sin abrir la lista.

Usuario confirma explícitamente comprobación EIPD resultado OK: explicación
EIPD: disponibilidad y retorno a Determinar aplicabilidad, sin cambiar valores.
13-01 OK; 13-03 guardado y consulta de ambos objetos comprobados, sin confundir
revisión de aplicabilidad con versión de evaluación o de infancia. Estas dos
capturas no muestran la posición del aviso de éxito; se conserva como límite
de evidencia, sin afirmar una captura inexistente.

Próximo: repetir Preparar nueva versión a partir de esta y elegir Conservar
para verificar cancelación del reemplazo de la preparación existente. No registrar
otra versión ni descartar la preparación. Publicación del bloque 13 pendiente.

## 13-05 — cancelación de reemplazo confirmada y consolidación

Usuario confirma recorrido OK: Documentos guardados → versión de infancia 1 →
Preparar nueva versión a partir de esta → Conservar documento en preparación →
retorno por pendientes con referencia, nombre y notas intactos. No se registró
otra versión ni se recargó la pestaña. Completa la comprobación de cancelación
pendiente de 13-05.

Los recorridos asistidos efectuados de 13 quedan aprobados en el alcance del
checklist. Sesión real de 12B y negativos controlados de sublotes anteriores se
reutilizan como antecedentes, no como nuevas ejecuciones en 13. La captura de
facultad revocada de 13 demuestra el bloqueo presentado, no una prueba de alta o
revocación nueva. Lector de pantalla manual no probado. No hay certificación,
CI remota nueva, merge ni despliegue. Las guías requieren lectura final del usuario;
commit/push de 13 todavía sin autorización nueva.

## 13 — cierre y publicación autorizados, 29/10/2026

El usuario autoriza commit y push de la documentación del bloque 13 tras los recorridos asistidos aprobados en el alcance del checklist. Se publican guía de tareas, glosario, ciclo documental y resultados con sus límites. La autorización no acredita lectura completa de las guías ni una nueva ejecución de toda la batería.

Se conservan el backlog funcional y la prueba manual con lector de pantalla pendiente. Sesión real conserva evidencia de 12B. Sin cambios de interfaz, merge ni despliegue. Las notas anteriores de autorización pendiente son antecedentes históricos superados por esta autorización.

## Paso 1 — anexos y acciones: implementación local, 29/10/2026

Usuario autoriza continuar Paso 1 tras el cierre 13. Rama `feature/anexos-estado-acciones`, base `205f4c9b92ae700bc99efed1447f44d74624ef58`.

LIC-UX-014 implementado localmente: Guardar anexo se deshabilita ante formato no admitido, archivo vacío o mayor de 2 MiB. El motivo queda una sola vez junto al selector, asociado mediante descripción accesible y aviso; junto a Guardar se explica qué corregir sin duplicar el error. Sustituir o quitar el archivo actualiza el estado y conserva los demás campos y la declaración ficticia. La validación del cliente API y del servidor se mantiene; un rechazo de envío conserva foco/aviso y no anuncia éxito.

LIC-UX-015 parcial y acotado al panel de valoración/anexos: metodología y vínculos opcionales usan el patrón compartido de desplegable reconocible con fondo suave, borde y foco. Se corrigió el ancho mínimo del formulario de anexos tras detectar desborde a 320 px. No se declara una auditoría transversal de todos los accesos.

Validación local: 42 pruebas Chromium aprobadas en assessment-support y licitud-workspace, con respuestas controladas; incluye CSV, vacío, sobredimensionado, corrección, conservación de referencia/descripción/sección/vínculos/declaración, retiro de archivo, rechazo de servidor, teclado y anchos 1280/390/320. Inspección visual de captura a 320 px aprobada. No acredita una nueva prueba contra API real ni lector de pantalla manual. Tipos, ESLint, Prettier y diferencias verificados. Una primera ejecución detectó desborde a 320 px; corregido antes de la ejecución final aprobada.

Pendiente: recorrido asistido en `/dashboard/trabajo` → Preparar → Anexos de respaldo: (1) completar metadatos ficticios y elegir CSV, comprobar único error y Guardar bloqueado; (2) reemplazar por TXT válido y confirmar conservación/habilitación según declaración; (3) quitar selección o probar vacío/mayor de 2 MiB, comprobar motivo; (4) abrir/cerrar vínculos con teclado y revisar ventana estrecha. No guardar un anexo nuevo solo para probar presentación. LIC-UX-014 pendiente aceptación asistida; LIC-UX-015 sigue abierto fuera de este panel.

Sin cambios de API, límites, persistencia ni permisos; EIPD bloqueada. No se ejecuta commit/push de este Paso 1 sin autorización específica. Se preservan `frontend/next-env.d.ts` y `outputs/` preexistentes.

### Seguimiento de teclado del Paso 1 — 30/10/2026

- El usuario validó el recorrido de archivo inválido y sustitución por un archivo válido, conservando los campos del anexo.
- Informó que la barra espaciadora no abría/cerraba «Vínculos opcionales con riesgos y medidas». La prueba aislada con comportamiento nativo no reproducía el fallo; se añadió activación explícita con Espacio, cancelando la acción nativa para evitar un doble cambio y descartando la repetición al mantener la tecla pulsada.
- Se amplió la prueba para llegar con Tab desde «Sección relacionada», abrir/cerrar tres veces, mantener Espacio, usar Enter y clic, y conservar el código R1. Comprobado en 1280, 390 y 320 píxeles.
- Falta la validación manual del usuario en su navegador con este ajuste. No se considera una comprobación con lector de pantalla. Sin commit ni push de este paso todavía.
