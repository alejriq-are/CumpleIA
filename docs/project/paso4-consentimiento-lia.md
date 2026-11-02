# Paso 4 — LIC-FORM-001: formularios de consentimiento y LIA

## Publicación autorizada y verificación final — 02/11/2026

El usuario autoriza commit y push de esta entrega, su cierre y el diseño LIC-GOV-001 en `feature/consentimiento-lia-formularios`. Se repitieron con resultado aprobado las 172 pruebas de servicios y las 41 pruebas Chromium con respuestas controladas, tipos TypeScript, ESLint/Prettier dirigidos, Ruff/Black dirigidos y comprobación de diferencias. No se acredita una nueva prueba de persistencia real aislada. Se conservan los remanentes FORM-R01 a FORM-R05 y la continuidad 5A–5D. Las notas inferiores de publicación pendiente son antecedentes superados; no hay merge ni despliegue. `frontend/next-env.d.ts` y `outputs/` quedan excluidos.

## Cierre de la entrega del Paso 4 — 02/11/2026

Cierre solicitado por el usuario tras los recorridos aceptados de Consentimiento/LIA, conservación entre bases, consulta y diagnóstico independientes, avisos y resumen de Base y fundamento.

**Entrega v1 aceptada y cerrada; LIC-FORM-001 mantiene remanentes abiertos.** No se declara completado todo el contrato FORM-01 a FORM-05 ni una aprobación jurídica. Las menciones anteriores de aceptación pendiente quedan superadas solo para esta entrega.

Evidencia técnica ya registrada: 41 pruebas Chromium con respuestas controladas, 172 pruebas de servicios, tipos, lint y formato dirigidos. No se repitieron por este cierre documental. Las escrituras reales contra API/PostgreSQL aislado, con distintos roles y organizaciones, siguen pendientes.

### Remanentes que conservan seguimiento

- **FORM-R01:** desglose compatible y versionado de las 19 prácticas de consentimiento y trazabilidad de respuestas históricas/adaptación normativa.
- **FORM-R02:** evidencias por criterio vinculadas a la versión exacta del anexo.
- **FORM-R03:** ayudas y condiciones LIA completas y acceso desde diagnóstico al campo pendiente.
- **FORM-R04:** exportación íntegra, errores 403/422/conflicto/resultado incierto y persistencia real aislada con permisos/aislamiento.
- **FORM-R05:** accesibilidad manual, móvil, adaptación normativa y checklist de cobertura final.

El detalle del contrato y del trabajo restante continúa vigente. Estos requisitos no se eliminan ni se declaran absorbidos por la siguiente tarea.

### Continuidad acordada

Próximo paso: **5A — contrato común del circuito documental**, incorporando LIC-GOV-001: borrador, versión registrada, revisión, decisión, facultades y efecto de cambios posteriores. Después: 5B versiones EIPD general; 5C revisión y decisión EIPD; 5D aplicación del patrón a Base y fundamento.

El cierre es documental. Confirmación y activación EIPD siguen bloqueadas. Cambios locales en `feature/consentimiento-lia-formularios`, base `3d058327`, sin commit/push nuevo, merge ni despliegue. Excluir `frontend/next-env.d.ts` y `outputs/` preexistentes de una futura publicación.

## Entrega inicial sobre el contrato v1 — 31/10/2026

Rama: `feature/consentimiento-lia-formularios`, creada desde `3d058327` (Paso 3 publicado). Implementación local; pendiente aceptación asistida. LIC-FORM-001 permanece abierto. Esta entrega no completa aún los cinco paquetes del [contrato de desarrollo](m3-t1-consentimiento-lia-implementacion.md).

### Implementado

- Consentimiento: otorgante y método sin valores positivos por defecto; 14 controles generales y 2 condicionales con respuesta y fundamento; referencias de evidencia (tipo, referencia, fecha, mecanismo y notas); notas generales.
- LIA: los 59 campos del contrato existente, distribuidos en ocho grupos. Incluye respuestas estructuradas, fundamentos, escalas propias, medidas con impacto mitigado y conclusión propuesta. La escala LIA no sustituye la matriz EIPD.
- Guardado PATCH del formulario activo. Cambiar de base conserva las ediciones de ambos formularios en esta pestaña. Guardar otra base no presenta las ediciones del formulario inactivo como guardadas; volver a esa base y guardar para persistirlas.
- Consulta legible de consentimiento y de todos los campos LIA guardados; los antecedentes de bases anteriores se identifican aparte. El JSON sigue utilizando el contrato existente.
- Consulta explícita del diagnóstico de cada formulario guardado, separada del guardado y disponible aunque haya ediciones pendientes o la otra base esté activa. Muestra las respuestas guardadas analizadas, identifica antecedentes de otra base y avisa de diferencias con el formulario. No sustituye las ediciones pendientes. Los errores de diagnóstico no anulan una confirmación de guardado.
- No aplica se ofrece según la aplicabilidad del servidor. Una respuesta histórica No aplica se conserva y puede requerir revisión. No se infiere aplicabilidad jurídica en el cliente.
- Se mantienen los controles de solo lectura y estado borrador. No se incorpora ninguna acción de confirmación/activación EIPD.

### Validación ejecutada

- Tipos TypeScript, ESLint dirigido, formato Prettier y comprobación de diferencias.
- 28 pruebas Chromium de `licitud-workspace.spec.ts`, con respuestas controladas: conservación, reapertura, edición de ambos formularios, preservación del inactivo, diagnóstico fallido y No aplica condicionado.
- 13 regresiones Chromium de `mvp-dossier.spec.ts`: consulta, descarga y separación de documentos.
- 172 pruebas de servicios LIA y consentimiento aprobadas, incluidas tres comprobaciones de diagnóstico independiente, correspondencia con las respuestas guardadas y propagación del rechazo de ámbito. Estas pruebas usan evaluadores reales y una lectura de evaluación controlada, sin escritura en PostgreSQL.
- Contraste de los nombres de los 59 campos del catálogo LIA con las ocho clases del esquema Python.

Estas comprobaciones no equivalen a una escritura real contra API/PostgreSQL ni a aceptación visual o jurídica. Se agregó una consulta GET y su esquema de salida para diagnosticar ambos formularios guardados. No cambian los contratos de entrada, los evaluadores puros, las reglas de confirmación, las migraciones ni los datos del expediente manual. `frontend/next-env.d.ts` y `outputs/` preexistentes quedan fuera de esta tarea.

## Recorrido asistido inicial

Usar una evaluación ficticia en borrador y Base y fundamento en el espacio conectado `/dashboard/trabajo`. Si hay pendientes en una pestaña anterior, conservarla abierta. La nueva pestaña no recupera ediciones sin guardar.

1. Seleccionar Consentimiento. Comprobar el editor, otorgante/método Sin responder y los controles con fundamento. Introducir una respuesta Pendiente de analizar y su fundamento ficticio. Guardar borrador y comprobar el aviso junto al botón.
2. Navegar a otra sección y volver: deben conservarse respuesta y fundamento. Reabrir lo guardado en otra pestaña: deben coincidir. No afirmar completitud por este ensayo.
3. Seleccionar Interés legítimo. Comprobar los ocho grupos, completar un fundamento ficticio y una medida con su impacto mitigado. Guardar y reabrir para verificar ambos campos.
4. Antes de guardar una edición LIA nueva, cambiar a Consentimiento y volver: la edición LIA debe conservarse. Guardar Consentimiento no guarda esa edición LIA; debe seguir pendiente hasta guardar en Interés legítimo.
5. Reabrir una evaluación con ambos formularios previamente guardados. Consultar diagnóstico guardado de Consentimiento sin guardar de nuevo. Abrir Respuestas guardadas analizadas y comparar con lo persistido. Cambiar a LIA, escribir un cambio sin guardar y consultar su diagnóstico: debe analizar la LIA guardada aunque Consentimiento sea la base activa, mostrar el aviso de diferencia y conservar el texto pendiente. Repetir en sentido inverso. No aplica solo se ofrece si la consulta lo habilita y el formulario coincide con lo analizado.
6. Simular un fallo de consulta y reintentar al recuperar la conexión: se retira el resultado anterior, se muestra el error y el reintento conserva las ediciones. Consultar nunca guarda ni aprueba la evaluación.

## Trabajo restante para completar LIC-FORM-001

1. Resolver y versionar el desglose de las 19 prácticas de consentimiento del original: no convertir un Sí histórico agrupado en respuestas afirmativas a preguntas nuevas. Mantener trazabilidad y adaptación chilena según la [auditoría de cobertura](m3-t1-consentimiento-lia-cobertura.md).
2. Vincular evidencias por criterio a una versión exacta del anexo. Las referencias de este editor son metadatos; no son una carga de archivo ni un vínculo versionado. El anexo de Base y fundamento debe seguir admitiendo ausencia de vínculos a riesgos/medidas.
3. Completar ayudas y visualización contextual de todos los campos condicionales LIA (fuentes, relación previa, vulnerabilidad y salvaguardas), sin duplicar el evaluador del servidor. El diagnóstico ya informa los pendientes; falta su recorrido completo y enlace directo al campo.
4. Ampliar prueba de consulta/exportación para todos los datos nuevos, fallos 403/422/conflicto y guardado incierto. Ejecutar escrituras contra API/PostgreSQL aislado con roles/organizaciones distintas.
5. Validar accesibilidad, móvil y adaptación normativa; actualizar contrato, cobertura y checklist antes de cerrar FORM-01 a FORM-05.

Próximo punto: aceptación del recorrido inicial y definición del esquema compatible de desgloses/evidencias. No requiere reanalizar los Excel originales: la cobertura ya está documentada. No hay commit, push, merge ni despliegue de esta entrega todavía.

## Corrección durante la aceptación — 31/10/2026

Observación del usuario: diagnóstico aparentemente discordante y necesidad de volver a guardar para consultarlo. Se verificaron dos causas: la consulta estaba deshabilitada ante cualquier edición y la ruta de readiness solo evaluaba la base activa guardada. La nueva ruta `basis-diagnostics` evalúa por separado los dos formularios conservados de la misma evaluación y devuelve el contenido exacto analizado en la misma lectura. LIA usa el alcance RAT guardado en la evaluación; el diagnóstico no reemplaza la comprobación de readiness para confirmar ni interpreta cambios posteriores del RAT como incorporados. No se ha demostrado un fallo de persistencia con escrituras reales: queda pendiente comprobar los ejemplos del usuario contra el servidor en ejecución. La prueba de navegador nueva verifica ausencia de PATCH al consultar, consulta de antecedentes de la otra base, respuesta fallida/reintento y conservación de texto pendiente.

### Claridad de avisos — 02/11/2026

Se reemplaza «base activa guardada» por el nombre de la base propuesta seleccionada en el último guardado, aclarando que consultar el otro formulario no cambia esa selección ni aprueba la evaluación. La explicación sobre finalidad/datos asociados y actualización expresa del alcance RAT aparece solo en LIA. La finalidad se presenta en un párrafo propio, sin agregar otro punto al texto guardado. Aceptación del usuario: recorrido OK. No cambia el diagnóstico ni los datos.

### Resumen de Base y fundamento — 02/11/2026

Se incorpora antes del editor un resumen de la base propuesta, fundamento y existencia de formularios Consentimiento/LIA guardados. Usa la respuesta GET de apertura y PATCH exitoso; no confunde las ediciones pendientes con contenido persistido. Identifica la versión/estado de la evaluación y aclara que otras pestañas no se sincronizan automáticamente. No se inventa fecha ni autor, ausentes en esta respuesta. Aceptación del usuario de los avisos anteriores: recorrido OK. Aceptación visual del resumen comunicada por el usuario: recorrido OK.

Verificación del resumen: las 28 pruebas de navegación del espacio de trabajo pasan, incluida conservación del resumen guardado durante la edición y actualización tras guardar. Tipos, lint, formato y diferencias aprobados. Sumadas las 13 pruebas de consulta documental ya ejecutadas, son 41 pruebas Chromium en este alcance.

## Extensión aprobada — revisión y decisión, 02/11/2026

El usuario aprobó separar revisión del fundamento por el delegado y aceptación por una persona expresamente facultada por la organización. Se registra como LIC-GOV-001, implementación pendiente, con contrato y lotes propios en [revisión y aceptación de Base y fundamento](revision-aceptacion-base-licitud.md). La designación como delegado no concede automáticamente la facultad de decisión; los formularios conservados no equivalen a bases aceptadas. No cambia el comportamiento actual ni cierra LIC-FORM-001.
