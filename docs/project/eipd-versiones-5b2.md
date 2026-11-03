# LIC-DOC-001 — Bloque 5B.2: interfaz de versiones EIPD general

## Estado y alcance

Implementado localmente en `feature/eipd-versiones-5b2`, desde `e83b706d2131ce0bb5fdd01de28abcc5eb93852a` (5B.1 publicado). Aceptación asistida completada y commit/push autorizados por el usuario el 03/11/2026. Esta nota supera las menciones anteriores de interfaz pendiente. No hay merge ni despliegue remoto.

Se integra el contrato de [5B.1](eipd-versiones-5b1.md) y el [circuito documental común](circuito-documental-comun.md). 5C (revisión y decisión), 5D (Base y fundamento) y FORM-R01 a FORM-R05 permanecen abiertos. Confirmación y activación EIPD siguen bloqueadas. No se cambia el circuito de infancia.

## Accesos y comportamiento

- En **Completar EIPD**, después del editor del documento, aparece **Versiones documentales EIPD general**. Los siete pasos siguen siendo un único borrador.
- **Guardar borrador EIPD** conserva el documento editable. **Preparar registro de versión EIPD** consulta una fotografía del contenido guardado en el servidor; no incorpora ediciones pendientes ni registra nada.
- Antes del registro se presentan el documento, referencia, nombre libre, notas y antecedentes conservados. El contexto, determinación, diagnóstico, política e índice de soportes se pueden desplegar. El manifiesto conserva antecedentes consultados; un registro histórico no acredita controles actuales y no incluye archivos binarios.
- Para **Registrar versión documental EIPD**, se exige motivo, declaración de datos ficticios y lectura del contenido guardado. Se permiten antecedentes incompletos; registrarlos no los aprueba. El servidor vuelve a comprobar permisos, aplicabilidad, origen y secuencia.
- **Consultar historial de versiones EIPD** y **Consultar versión EIPD N** recuperan registros históricos de solo lectura. También están disponibles en **Documentos guardados**, sin requerir que actualmente corresponda completar EIPD.
- Desde el editor se puede **Preparar borrador desde esta versión EIPD**. Siempre pide confirmación antes de reemplazar los campos locales; cancelar conserva lo abierto. La copia no modifica el original ni el borrador del servidor, no copia decisiones ni declara vigentes valoraciones históricas. Debe guardarse expresamente antes de registrar otra versión.

El número documental lo asigna el servidor y es distinto de la versión de la evaluación y del nombre libre de edición. La nueva consulta no presenta el borrador EIPD guardado como una versión documental registrada.

## Concurrencia y recuperación

Se genera un identificador de solicitud por registro explícito. Un doble clic no produce otra petición. Ante respuesta incierta se bloquean las ediciones de origen y nuevas solicitudes de registro hasta comprobar el resultado. **Consultar resultado del registro EIPD** recupera la solicitud original. Si aún no se encuentra, **Reintentar el mismo registro EIPD** utiliza exactamente el mismo identificador y contenido.

Un rechazo definitivo por origen o secuencia desactualizados exige una nueva vista previa. No se reintenta automáticamente con otro identificador. Cambiar el origen local invalida la vista previa anterior. La API del cliente comprueba evaluación, tratamiento, organización, identidades y formato de respuestas; no sustituye la autorización del servidor.

Los pendientes de registro participan en el aviso de trabajo sin guardar del editor. La preparación y la solicitud incierta son temporales en esta pestaña; no se promete recuperarlas después de cerrarla o recargarla. Mantenerla abierta hasta resolver un resultado incierto.

## Operación local y evidencia

El 02/11/2026 se verificó la base local `cumpleia` del contenedor `cumpleia_db` en revisión `a84f6e2c9103`. Se ejecutaron las instrucciones `upgrade()` de la migración append-only `b95e7f3d1204`, dentro de una transacción con comprobación de destino y revisión, y se actualizó `alembic_version`. Se comprobó igualdad de conteos de `legal_assessments` y `assessment_support_records` antes/después. Tabla nueva vacía: no se crearon versiones ficticias ni se alteraron documentos para preparar la prueba. No se leyeron credenciales ni se cambió el rol runtime. Las cuatro rutas de versiones están presentes en OpenAPI del backend local (puerto 8000). Esto no acredita un registro autenticado desde la interfaz.

Verificación de frontend:

- TypeScript y ESLint dirigidos aprobados.
- 32 pruebas Chromium aprobadas en una ejecución final: ocho de versiones, seis de vista previa y dieciocho de consulta existente. Una integración opcional omitida por requerir entorno aislado. Se corrigió y comprobó la devolución del foco al botón de consulta después de la espera, sin trasladarlo si el usuario ya enfocó otro control.
- Casos nuevos: registro explícito, consulta y copia confirmada/cancelada, respuesta perdida, recuperación por solicitud, reintento idéntico después de 404, conflicto de origen, rechazo de respuesta ajena, bloqueo por ediciones pendientes, invalidación de vista previa y consulta de lectura mediante teclado a 390 px. Este último comprueba interacción, no sustituye revisión visual de estilos o lector de pantalla.
- La evidencia PostgreSQL/RLS de 5B.1 (191 pruebas aisladas) se conserva por referencia, no se repitió para esta interfaz.

Archivos principales: `EipdVersions.tsx`, cliente `eipd-versions.ts`, integración con `EipdDraftEditor.tsx` y `AssessmentFlow.tsx`, rótulo específico de `EipdDocumentView`, pruebas `eipd-versions.spec.ts`.

## Checklist de aceptación asistida

Usar `/dashboard/trabajo`, datos ficticios y una evaluación con borrador editable, alcance vigente y determinación guardada «EIPD: Corresponde». La política debe estar seleccionada y verificable por el servidor. No cambiar política ni facultades solo para superar una prueba.

- [x] Abrir Completar EIPD → Tratamiento y alcance. Localizar Versiones documentales EIPD general al final del editor. Comprobar que un cambio pendiente impide preparar el registro y que navegar conserva el texto.
- [x] Guardar el borrador y preparar el registro. Comparar referencia, nombre, notas y contenido con lo guardado. Revisar el diagnóstico y los antecedentes, incluidos soportes históricos.
- [x] Escribir un motivo ficticio, declarar datos ficticios y confirmar lectura. Registrar una vez. Comprobar número propio, motivo, autor, fecha, copia de solo lectura y activación bloqueada.
- [x] Editar/guardar después el borrador. Consultar la versión anterior y comprobar que conserva su contenido; registrar otra versión y comprobar la secuencia sin sobrescribir la anterior.
- [x] En Documentos guardados, consultar historial y detalle; comprobar que no ofrece edición del original ni aceptación del documento.
- [x] Preparar una copia desde el editor: cancelar primero y comprobar conservación; confirmar después y comprobar que solo cambia el borrador local hasta guardarlo.
- [x] Probar rechazo de origen cambiado desde otra pestaña, sin crear un segundo registro automáticamente.
- [x] Probar consulta sin conexión y recuperación; para resultado de POST incierto, consultar solicitud/reintentar la misma, sin cerrar la pestaña ni generar otra solicitud.
- [x] Revisar teclado, foco y presentación en ventana estrecha. Validación manual con lector de pantalla pendiente.

Ante bloqueo, conservar el mensaje exacto y el contexto; no sustituirlo por datos de la maqueta. La aprobación del recorrido se registra separadamente de las comprobaciones automatizadas.

## Cierre asistido — 03/11/2026

El usuario confirmó los recorridos del checklist: registro y secuencia de versiones, consulta histórica independiente del borrador, copia cancelada/confirmada, rechazo por origen cambiado desde otra pestaña, recuperación de conexión sin duplicados, teclado y ventana estrecha. La primera captura con botón deshabilitado correspondía a motivo vacío; repetido el orden de vista previa, cambio guardado en otra pestaña y registro, el usuario confirmó el rechazo esperado.

Se aceptó presentar los antecedentes conservados con etiquetas legibles en lugar de JSON. Evidencia manual: confirmaciones del usuario en este chat; no equivale a prueba con lector de pantalla ni demuestra por sí sola un POST confirmado con respuesta perdida (cubierto por pruebas controladas). Lector de pantalla pendiente. No se borran las versiones ficticias creadas durante las pruebas.

Bloque 5B.2 aceptado dentro de este alcance. Siguiente trabajo: 5C, revisión y decisión de versiones EIPD general y atribuciones diferenciadas; 5D y FORM-R01–R05 siguen abiertos. Sin merge, despliegue ni habilitación de confirmación/activación EIPD.

Verificación de cierre repetida el 03/11/2026: TypeScript y ESLint dirigidos aprobados; ocho pruebas Chromium de versiones aprobadas. Las 32 pruebas previas se conservan como evidencia histórica y no se declaran repetidas en este cierre.
