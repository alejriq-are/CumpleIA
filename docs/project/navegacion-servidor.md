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
