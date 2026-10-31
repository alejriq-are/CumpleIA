# Cierre de navegación: aceptación y remanentes

## Paso 2 — aceptación asistida y publicación autorizada

El usuario confirmó los recorridos principales y complementarios del alcance mixto y autorizó commit/push. Quedan aceptados: acceso y retorno a la misma evaluación desde RAT; etiquetas coherentes y orden común en comparación; adopción explícita con motivo; revisión independiente de EIPD/infancia; conservación de borradores, antecedentes y alcance guardado; ventana estrecha, cierre/foco; retirada/restauración de aplicabilidad; cambio del RAT posterior a comparar; error de conexión y recuperación; consulta desde otra pestaña con pendientes independientes. Evidencia asistida reportada por el usuario en este chat; no equivale a auditoría completa ni prueba manual con lector de pantalla.

Rama `feature/alcance-mixto-guiado`, base `8d2cc88`. Publicación del Paso 2 autorizada; sin merge ni despliegue. Confirmación y activación EIPD siguen bloqueadas. Se excluyen los cambios preexistentes de `frontend/next-env.d.ts` y `outputs/`. Contrato y límites: [alcance mixto guiado](alcance-mixto-guiado.md). Las notas inferiores sobre validación o autorización pendiente quedan superadas para el alcance aceptado.

## Paso 2 — alcance mixto guiado: implementación local, 30/10/2026

NAV-UX-005 implementado localmente en `feature/alcance-mixto-guiado`; aceptación asistida pendiente. Permite revisar RAT, regresar a la misma evaluación, comparar y adoptar el alcance con motivo y trazabilidad, conservando borradores y antecedentes. Las determinaciones anteriores requieren revisión para el nuevo alcance; EIPD e infancia siguen independientes.

Evidencia: suite aislada EIPD 1.148 aprobadas; ampliación focalizada alcance/anexos 9 aprobadas (con solapamiento); navegador conectado 135 aprobadas con respuestas controladas. Migración `a84f6e2c9103` aplicada en base aislada y desarrollo local verificado. Sin commit/push de este paso, merge ni despliegue; EIPD bloqueada. Contrato, límites y checklist: [alcance mixto guiado](alcance-mixto-guiado.md).

## Paso 1 — validación asistida y publicación autorizada, 30/10/2026

El usuario confirmó «recorrido OK» tras el ajuste de Espacio en «Vínculos opcionales con riesgos y medidas» y autorizó commit/push. Quedan aceptados el recorrido de archivo inválido → archivo válido con conservación de campos y la apertura/cierre del bloque con teclado. Las notas anteriores de aceptación/autorización pendiente quedan superadas en este alcance.

Verificación técnica: 42 pruebas Chromium aprobadas en assessment-support y licitud-workspace con respuestas controladas y estilos de la aplicación; tipos y ESLint aprobados. LIC-UX-014 queda resuelto en este alcance. LIC-UX-015 conserva pendientes fuera de los dos desplegables del panel. La validación manual con lector de pantalla continúa pendiente; no se atribuye una subida real nueva de anexo a estas pruebas.

Se publica en `feature/anexos-estado-acciones`. Sin merge ni despliegue; confirmación/activación EIPD bloqueadas. Se excluyen los cambios preexistentes de `frontend/next-env.d.ts` y `outputs/`.

Fecha: 29/10/2026. Bloque 13 en `feature/navegacion-13-guia-cierre`.
Base funcional publicada: `41c561b78e7b4d96994d927b86422d7d9efed5d1` (12B).
Estado: **recorridos asistidos ejecutados y aprobados en el alcance registrado**.
El usuario autoriza commit y push del bloque 13 tras aprobar los recorridos asistidos. La lectura completa de las guías no se acredita como prueba ejecutada.
Los casos no repetidos en 13 mantienen su evidencia anterior: sesión real en 12B y negativos controlados en pruebas de sublotes. Lector de pantalla manual sigue No probado. No se declara una nueva ejecución integral de toda la batería.
Este documento es el índice único de cierre; los registros originales siguen en [navegación conectada](navegacion-servidor.md). No sustituye ni reescribe su evidencia.

## Documentos para consultar

- [Guía: dónde está, qué hace y qué conserva](guia-navegacion-trabajo.md).
- [Ciclo documental e identidades](ciclo-documental-eipd.md).
- [Glosario G01–G30](glosario-funcional.md).
- [Plan por lotes](plan-navegacion-formularios.md) y [decisiones sobre propuestas externas](evaluacion-propuestas-claude.md).

## Cómo registrar un resultado

Usar **OK**, **Fallo** o **No probado**. Registrar fecha, commit del frontend/backend utilizado, navegador/ancho/zoom, rol de aplicación, facultad documental, organización/tratamiento/finalidad/evaluación y versión documental si corresponde. Utilizar identificadores ficticios o referencias de prueba, sin tokens ni credenciales. Adjuntar captura o referencia al caso automatizado y anotar su límite.

Las comprobaciones por código no son observaciones de uso. Una prueba automatizada con respuestas controladas no acredita el servicio real. La aceptación de sublotes anteriores no equivale a haber repetido hoy el recorrido integral. Un push no acredita CI, merge ni despliegue.

## Ocho recorridos integrales del bloque 13

Todos parten de `/dashboard/trabajo`, con cuenta autorizada y datos ficticios. Reutilizar evaluaciones existentes para consultas; los guardados indicados deben hacerse únicamente sobre la evaluación ficticia elegida para la prueba. No confirmar ni activar EIPD.

| ID | Recorrido y resultado esperado | Contexto/rol requerido | Evidencia anterior y su límite | Resultado integral 13 |
| --- | --- | --- | --- | --- |
| 13-01 | Aplicar contexto existente → Determinar aplicabilidad → localizar Completar EIPD o explicación de disponibilidad. Distinguir lo guardado de la selección pendiente. | Evaluación ficticia con determinación conocida; permiso de lectura y edición para cambiarla. | 6B, 11B y pruebas de disponibilidad en connected-navigation. La guía aún requiere aceptación de comprensión. | OK: contexto de menores, EIPD Pendiente de analizar e infancia Corresponde; usuario confirma explicación EIPD: disponibilidad y retorno. |
| 13-02 | Escribir nota EIPD sin guardar → cambiar paso/módulo → Ver pendientes → volver. Texto y contexto intactos; siete pasos cuentan como una unidad. | Evaluación con EIPD habilitada y documento editable. | 8B, 9A/9B; usuario confirmó conservación y retorno. No demuestra persistencia tras recargar. | OK: recorrido asistido confirmado por usuario; evidencia en registro 13. |
| 13-03 | Comparar borrador con última determinación consultada → guardar determinación ficticia explícitamente → reconocer aviso junto al botón e historial → consultar. El guardado no guarda notas EIPD. | Evaluación ficticia editable; fundamento y declaración exigidos. | 5, 9A, 12B; consulta conserva pendientes. Cada objeto tiene su propio guardado. | OK en guardado/consulta EIPD y determinación: captura muestra revisión de aplicabilidad 2, formulario coincidente y fundamento de prueba conservado. La posición del aviso de guardado no aparece en estas últimas capturas. |
| 13-04 | Abrir Documentos guardados → leer EIPD general y/o versión de infancia → encontrar revisión y decisión y explicar sus requisitos. | Consulta general; infancia con versión histórica. Decisión requiere facultad vigente y material admitido; probar bloqueo con facultad revocada/controlada. | 10A/10B y casos de organización. EIPD general no tiene circuito formal integrado; no inventar un resultado favorable. | OK en consulta de infancia y acceso a revisión/decisión; captura muestra facultad revocada y bloqueo. No se registraron actuaciones. Consulta EIPD general comprobada en recorrido previo. |
| 13-05 | Desde una versión de infancia preparar copia → conservar o reemplazar preparación según aviso → previsualizar → volver sin registrar. Original e historial intactos. | Versión ficticia de infancia consultable; preparación temporal en la misma pestaña. | 6B, 10B; usuario confirmó copia/previsualización. No se registra otra versión para validar únicamente navegación. | OK: copia temporal, vista previa, retorno sin registro, versiones 1/2 conservadas y cancelación del reemplazo confirmadas por usuario. |
| 13-06 | Menú/Secciones → Tab, Espacio, Escape y fondo atenuado → formulario; repetir aperturas y ancho, zoom 200 %. Foco visible, sin recortes esenciales. | Ventana amplia y estrecha, teclado; formulario con nota pendiente. | 7A/7B, 8A/8B; usuario confirmó recorridos y aclaración de Escape. Lector de pantalla manual sigue No probado. | OK en ventana estrecha, aperturas repetidas, Escape/foco, fondo atenuado y zoom 200 % con teclado. Lector de pantalla manual No probado y preservado como remanente. |
| 13-07 | Fallar consulta, recuperar red y reintentar en la misma pestaña; ante sesión ausente iniciar sesión aparte y volver. Distinguir fallos de red, sesión y permisos. | Cuenta de prueba propia; original abierta, sin recargar. Rol/estado/material negativos en fixtures controlados. | 12B: red/contextos y sesión real aceptados por usuario; casos negativos automatizados. No acredita todos los proveedores o fallos posibles. | Parcial: Offline, error, recuperación y conservación OK. Sesión y negativos rol/estado/material no repetidos en 13; evidencia anterior conserva su alcance. |
| 13-08 | Autodiagnóstico real → RAT → Mi organización; verificar ámbito, ayudas y guardados propios. Encontrar Anexos desde Preparar y explicar bloqueo por documento pendiente. | Organización ficticia con cuestionario, tratamiento y evaluación; permisos según formulario. | 11A/11B/12A, pruebas de soporte. Siguiente exige sección respondida, N/A válido; creación 11B cubierta automáticamente, no ejecutada en recorrido manual. | OK: usuario confirma ámbitos y localización del formulario de anexos; captura adjunta. Sin carga ni guardados en este tramo. |

Los recorridos asistidos se completaron según las entradas 13 del registro de navegación. No se requiere repetirlos para publicar únicamente la documentación. Para retomar después de cambios funcionales, elegir los recorridos afectados y registrar una nueva base Git; conservar los resultados anteriores como antecedentes. No recargar una pestaña con cambios pendientes.

## Evidencia técnica heredada, sin repetir ejecuciones

12B dejó una ejecución de regresión con **185 pruebas aprobadas y una omitida** (captura opcional de prototipo). Tras el ajuste del aviso de lista vacía se ejecutaron **dos pruebas dirigidas aprobadas**: son una comprobación adicional del ajuste, no dos escenarios nuevos para sumar al total anterior. TypeScript, ESLint, Prettier y comprobación de diferencias aprobaron en ese cierre. No se afirma una ejecución de CI remota.

El bloque 13 cambia documentación: se comprobaron 37 enlaces locales de las cuatro guías, la secuencia única G01–G30, los ocho identificadores 13-01 a 13-08, los nombres/rutas contra las fuentes y la limpieza de diferencias de Git. No se atribuye una nueva ejecución de pruebas de interfaz a estas ediciones.

Fuentes de cobertura para localizar casos (su presencia no declara ejecutada otra batería):

- [Navegación conectada](../../frontend/e2e/connected-navigation.spec.ts): disponibilidad, pendientes, contexto, teclado, ancho y recuperación.
- [Flujo de licitud](../../frontend/e2e/licitud-workspace.spec.ts): ayudas y creación/cancelación de evaluación.
- [Historia documental de infancia](../../frontend/e2e/child-eipd-history.spec.ts): copia, registro e identidad de revisión.
- [Decisión y facultades](../../frontend/e2e/organization-acceptance.spec.ts): identidad, rol, material y revocación.
- [Valoración y anexos](../../frontend/e2e/assessment-support.spec.ts): archivos, metodología y separación de guardados.

## Remanentes que no se cierran por el bloque 13

| Referencia | Pendiente o límite | Cómo retomarlo |
| --- | --- | --- |
| NAV-UX-005 | Actualización guiada del alcance cuando cambia la inclusión de infancia/adultos. | Diseñar asociación explícita sin sustituir silenciosamente el alcance de evaluación. |
| LIC-FORM-001 | Formularios completos de consentimiento y LIA. | Contrastar contratos y completar trabajo funcional separado; las ayudas no equivalen a formulario integrado. |
| LIC-UX-013 | Enlaces de consulta entre residual, medidas y evidencias. | Validación específica con relaciones reales guardadas. |
| LIC-UX-014 | Presentación de errores de anexos, selección inválida y estado del botón de guardar. | Verificar caso inválido y error duplicado; el estilo no sustituye validación. |
| LIC-UX-015 | Visibilidad consistente de acciones en el alcance restante. | Mantener lo aceptado en 6B/10B; comprobar los controles restantes sin declarar cobertura total. |
| LIC-DATA-001 | Errata en referencia histórica. | Rectificación enlazada; no editar ni borrar el registro inmutable. |
| LIC-AUD-001 | Auditoría completa del expediente. | Diseño específico; los historiales actuales son parciales por objeto. |
| LIC-RISK-001 | Metodología configurable y versionada. | La matriz interna fija actual no resuelve este requisito. |
| Accesibilidad 7B | Uso manual con lector de pantalla. | Preparar sesión con herramienta disponible; usuario no dispone de ella en estas pruebas. No certificar por teclado o automatización. |
| Circuito EIPD general | Versiones históricas, revisión y decisión formales completas no integradas; confirmación/activación bloqueadas. | Definir contratos, facultades y requisitos; no extender automáticamente el circuito de infancia. |
| Cierre 13 | Publicación autorizada y verificada en `205f4c9`; lectura completa de guías no acreditada como prueba. | Recorridos asistidos concluidos en el alcance de la tabla; no convertir casos no repetidos en pruebas nuevas. |

## Trazabilidad de las propuestas

| Propuesta | Resultado documental / implementación de referencia |
| --- | --- |
| P1 | Guía de tareas y recorridos 13-01 a 13-08. |
| P2 | Tabla de identidades y efectos del ciclo documental; glosario G05–G12. |
| P3 | Diagramas del ciclo actual y futuro, separados. |
| P4 | Límites de EIPD general y comparación con infancia explícitos. |
| P5 | Tabla de acciones, guardados y registros de la guía. |
| P6 | Capacidades presentes, controles y pendientes; referencia 10A. |
| P7 | Nombres y destinos coherentes de 6A; tabla de ubicación. |
| P8 | Contexto compacto y detalle de 8A; lectura completa sin cambiar selección. |
| P9 | Unidades pendientes y retornos de 9A/9B; recorrido 13-02. |
| P10 | Disponibilidad según determinación guardada de 6B. |
| P11 | Siete pasos de un solo borrador EIPD; 8B. |
| P12 | Barra y Secciones según ancho; teclado 7A/7B y 8B. |
| P13 | Evidencia por tarea, versión, contexto, resultado y límite en este checklist. |

G01–G30 se conservan uno a uno en el glosario, con las sustituciones aceptadas o descartadas. C19 se aplica transversalmente: separar observado, inferido del código y pendiente. Claude es una referencia externa de análisis; no participa en aprobación, ejecución, revisión formal ni decisión del circuito del proyecto.

## Seguimiento posterior: Paso 1, 29/10/2026

LIC-UX-014 implementado localmente en `feature/anexos-estado-acciones`, pendiente aceptación asistida/publicación. LIC-UX-015 abordado solo en desplegables del panel de valoración/anexos; no se cierra transversalmente. Evidencia y recorrido en [registro de navegación](navegacion-servidor.md). Este seguimiento no modifica los resultados históricos de 13.

### Seguimiento de teclado del Paso 1 — 30/10/2026

- El usuario validó el recorrido de archivo inválido y sustitución por un archivo válido, conservando los campos del anexo.
- Informó que la barra espaciadora no abría/cerraba «Vínculos opcionales con riesgos y medidas». La prueba aislada con comportamiento nativo no reproducía el fallo; se añadió activación explícita con Espacio, cancelando la acción nativa para evitar un doble cambio y descartando la repetición al mantener la tecla pulsada.
- Se amplió la prueba para llegar con Tab desde «Sección relacionada», abrir/cerrar tres veces, mantener Espacio, usar Enter y clic, y conservar el código R1. Comprobado en 1280, 390 y 320 píxeles.
- Falta la validación manual del usuario en su navegador con este ajuste. No se considera una comprobación con lector de pantalla. Sin commit ni push de este paso todavía.
