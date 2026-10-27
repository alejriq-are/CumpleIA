# Navegación conectada al servidor

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
