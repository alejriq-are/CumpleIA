# 5C.1 · Revisión de versiones de la EIPD general

## Contrato para la implementación

La revisión emite una conclusión motivada sobre una versión documental registrada. La identidad de trabajo comprende organización, tratamiento, evaluación y versión documental. El borrador editable, la evaluación de origen y la versión documental tienen identidades distintas. Una nueva versión inicia su propio historial de revisiones.

### Facultad de revisión

- Una persona administradora habilitada en la organización puede otorgar o revocar la facultad de revisar EIPD general para un expediente exacto. El servidor verifica la membresía de quien actúa y de la persona destinataria. El otorgamiento a sí mismo se rechaza.
- Cada actuación conserva identidad, fecha, alcance, motivo y referencia de respaldo. El otorgamiento puede tener vencimiento. La revocación agrega un evento y conserva los anteriores.
- Para registrar una revisión se exige una facultad expresa y vigente en el expediente y que la persona revisora sea distinta de quien registró la versión. La facultad de revisión no habilita decisiones de la organización.

### Registrar y consultar

- Registrar exige versión documental exacta, resultado, fundamento y referencia. Los resultados son «Favorable», «Requiere cambios» y «No continuar». El resultado favorable exige comprobar los requisitos documentales de esa versión con los antecedentes conservados en ella. Una edición posterior del borrador no completa retrospectivamente la versión revisada.
- La primera revisión parte sin revisión previa. Una reconsideración identifica la revisión precedente esperada de esa misma versión y conserva la secuencia. Un cambio concurrente exige consultar el historial antes de reintentar.
- La escritura valida dentro de la misma transacción la facultad, la autoría y la secuencia. El otorgamiento o la revocación concurrente se serializan con el registro. Un reintento de la misma solicitud debe recuperar el resultado registrado sin duplicarlo.
- La consulta permite ver el resultado, el fundamento, la referencia, la autoría y la fecha de cada actuación. Una revocación impide nuevas actuaciones y permite consultar los registros existentes según los permisos de lectura. Se aplican los permisos de consulta del expediente y aislamiento por organización.
- La interfaz abre el formulario desde la versión consultada, identifica su número y referencia y explica por qué una actuación está bloqueada. El servidor decide si admite la operación. En el piloto se usan datos ficticios.

La decisión de la organización corresponde a 5C.2. La confirmación y la activación quedan fuera del bloque.

## Validación requerida

1. Con dos personas del mismo expediente, verificar rechazo de autorrevisión y de una revisión sin facultad, aunque quien la intente sea administrador.
2. Con una facultad vigente, registrar «Requiere cambios» sobre una versión incompleta. Comprobar que «Favorable» se rechaza para esa versión incluso si después se completa el borrador. Probar también «Favorable» sobre una versión que cumpla los requisitos.
3. Reconsiderar con la revisión previa correcta. Comprobar conflicto con una previa desactualizada, idempotencia del reintento y conservación del historial.
4. Revocar o dejar vencer la facultad. Comprobar rechazo de nuevas revisiones, incluso durante una revocación concurrente, y consulta de las anteriores.
5. Consultar una sucesora y comprobar que tiene historial independiente. Probar lecturas y escrituras cruzadas con el rol de ejecución y verificar que se preservan los circuitos de infancia y del borrador EIPD.

## Estado verificado — 05/11/2026

Implementación local de **5C.1** en `feature/eipd-5c1-revision`, HEAD base `baaaa69`. Se revisaron `baaaa69` (reglas/roles del circuito, documentación) y `f9a3b31` (5B.2 cerrado). El árbol ya contenía la migración inicial, consulta inicial de revisiones y ajustes de navegación/pendientes; se preservaron estos cambios. No se ejecutó commit, push, merge ni despliegue de esta entrega.

### Archivos y decisiones implementadas

- Migración `backend/alembic/versions/c53e19d8a621_eipd_version_reviews.py`: eventos inmutables de facultad y revisión; claves compuestas de expediente/tenant/versión; referencia exacta de la facultad utilizada; RLS y disparador de validación para escrituras con `app_user`.
- `backend/app/schemas/eipd_document_versions.py`, `backend/app/services/eipd_version_reviews.py` y `backend/app/api/eipd_document_versions.py`: otorgar/revocar con secuencia esperada, membresía real, rechazo de autoasignación/autorrevisión, vencimiento, conclusiones motivadas y reconsideración con precedente exacto.
- `frontend/components/licitud/EipdVersionReviews.tsx`, integrado en `EipdVersions.tsx`: consulta explícita desde la versión abierta, referencia/número, historial, motivos de bloqueo y formulario. La administración de facultades está disponible para administradores desde ese expediente exacto. No crea una pantalla global nueva de personas.
- Favorable utiliza exclusivamente el diagnóstico documental conservado: reglas conocidas, resultado completo, contexto documental vigente y ausencia de faltantes. No consulta el borrador actual ni habilita aceptación, confirmación o activación.
- Orden de bloqueo: solicitud de revisión (tenant/persona/clave) → serie del expediente. Otorgar/revocar usa la misma serie. No se adquiere el selector de política porque revisar utiliza el paquete congelado. El disparador vuelve a comprobar membresía, facultad, vencimiento, autoría y secuencia dentro de la escritura.
- Idempotencia de revisión por organización/persona/solicitud: contenido igual recupera el resultado anterior, incluso tras revocación; contenido diferente produce conflicto. Consulta de solicitud por versión exacta para recuperar respuestas inciertas.
- Pendientes temporales por pestaña: se conservan fundamento/referencia ante rechazo, se bloquea cambiar de versión mientras hay campos o una solicitud pendiente, y se permite descartar campos antes del envío. Sin persistencia en almacenamiento del navegador.
- La facultad utilizada permanece referenciada en el historial; revocar impide nuevas revisiones y conserva consultas anteriores. Una sucesora parte sin revisiones.

Rutas añadidas bajo `.../eipd-versions/v1`:

- `GET /review-authorities/history` y `POST /review-authorities`.
- `GET /{version_id}/reviews`, `GET /{version_id}/review-state` y `POST /{version_id}/reviews`.
- `GET /{version_id}/review-requests/{request_id}`.

### Validación ejecutada y límites

- Migración aplicada primero en la base fija aislada `cumpleia_eipd_tests_20261009`; pruebas con el rol real `app_user`, sin BYPASSRLS ni superusuario.
- Ejecutor dirigido, desde `backend`: `PYTHONPATH=. ../.venv/bin/python scripts/run_general_eipd_version_tests.py`. Resultado final: **59 aprobadas, 1 excluida**. Incluye versiones, revisión, guardas del ejecutor y regresión funcional de sucesores de infancia.
- La exclusión es `test_downgrade_guard_and_empty_roundtrip`: intenta quitar la clave padre de una migración antigua de infancia, ya referenciada por versiones generales de 5B y ahora por facultades de 5C. Su fallo observado es de dependencias al revertir el ancestro, no una validación funcional de revisión. No se modificaron las migraciones históricas ni se declara aprobada esa prueba.
- Cobertura nueva: API autenticada de la segunda persona, administración sin facultad implícita, autoasignación/autorrevisión, esquema cerrado, favorable sobre versión completa y rechazo sobre la incompleta tras completar el borrador, reconsideración concurrente, claves idempotentes, revocación concurrente, vencimiento, historial/sucesora independientes, RLS e inmutabilidad.
- Chromium: **17 aprobadas** en `eipd-version-reviews.spec.ts`, `eipd-versions.spec.ts` y `eipd-pending.spec.ts`. Respuestas controladas: registro/reconsideración, bloqueo del autor, historial ajeno rechazado, recuperación sin duplicados, conflicto con campos conservados, facultades, teclado y ancho 320 px. No sustituye recorrido asistido conectado.
- TypeScript, ESLint, Ruff y Black dirigidos aprobados; diferencias verificadas.
- Migración aplicada también a `cumpleia` de desarrollo local tras comprobar destino y rol. Conteos antes/después iguales: **6 evaluaciones, 34 respaldos y 5 versiones documentales**. Tablas nuevas vacías y RLS verificado con `app_user`. No se crearon actuaciones de prueba en desarrollo local.

### Próximo paso

Realizar el recorrido asistido conectado con dos personas habilitadas y datos ficticios: otorgar facultad, consultar una versión registrada, intentar autorrevisión, registrar una conclusión y reconsideración, revocar y consultar historial. Verificar teclado, foco y presentación; lector de pantalla pendiente. Tras la aceptación conjunta de 5C.1, precisar e implementar el contrato de **5C.2**, decisión organizacional y facultades independientes. No declarar cerrado todo 5C ni iniciar 5D por esta entrega.


### Recorrido asistido parcial confirmado — 05/11/2026

El usuario comunica «recorrido OK» y aporta dos capturas de la sesión B. Se observa acceso a CumpleIA Demo, consulta de los datos organizacionales con modificación bloqueada y apertura del formulario de revisión de la versión documental 5, referencia SIMULADA-EIPD-TRABAJADORES-001. No aparece bloqueo de autorrevisión ni de falta de facultad en esa consulta; Favorable permanece bloqueado por requisitos documentales incompletos. La captura anterior de A mostraba el bloqueo de autorrevisión. Se registra aceptación de este tramo, sin atribuir a las imágenes un registro de revisión todavía no mostrado.

Preparación ejecutada: perfil B vinculado localmente a CumpleIA Demo con rol editor; acceso verificado mediante app_user con RLS. La vinculación no otorgó por sí misma facultad de revisión. La captura posterior muestra el formulario habilitado, sin verificar por esta evidencia el detalle del evento de otorgamiento.

Próximo paso inmediato: como B, registrar Requiere cambios con fundamento, referencia y declaración ficticios; comprobar autoría, fecha y resultado en el historial. Luego continuar reconsideración, conflicto entre pestañas, sucesora y revocación/vencimiento conforme al checklist. No se cierra 5C.1 completo con esta confirmación parcial. Sin cambios de código, nuevas pruebas automáticas, commit ni push por este registro.


### Primera revisión conectada confirmada — 05/11/2026

El usuario confirma el registro y aporta captura del historial de la versión documental 5, referencia SIMULADA-EIPD-TRABAJADORES-001. Se observa la actuación 1 con resultado Requiere cambios, fundamento y referencia ficticios, persona revisora B (perfil b73b52fc-127a-4c84-8ecc-f7611852ad9b) y fecha 2026-11-05T22:05:38.418153+00:00. Favorable continúa bloqueado por requisitos incompletos. Evidencia: captura y confirmación del usuario; no se realizó una nueva consulta de base de datos por este registro documental.

El fundamento de prueba contiene «se aprueba», aunque el resultado estructurado es Requiere cambios: no constituye revisión favorable ni aceptación organizacional. El historial se conserva; las actuaciones siguientes deben usar fundamentos coherentes con su resultado.

Próximo paso inmediato: como B, registrar una reconsideración No continuar con fundamento y referencia ficticios coherentes; consultar nuevamente y comprobar dos actuaciones ordenadas, sin reemplazar la primera. Después: conflicto entre pestañas, independencia de sucesora y revocación/vencimiento. No se cierra todavía 5C.1. Sin nuevos cambios de código, pruebas automáticas, commit ni push.


### Consulta comprensible de antecedentes históricos — 05/11/2026

Durante el recorrido manual el usuario observa que Contexto y antecedentes conservados con la versión despliega una consulta interminable y difícil de entender. Se corrige exclusivamente su presentación, sin cambiar paquetes registrados, diagnóstico, permisos ni actuaciones.

Archivos: componente nuevo EipdVersionContext.tsx, integración en EipdVersions.tsx y pruebas eipd-version-context.spec.ts. Al abrir se muestran cinco apartados cerrados con resumen: alcance RAT, determinación, diagnóstico, política e índice de respaldos. Cada detalle se abre por separado. Conservación/eliminación tienen rótulos específicos; se elimina de esta consulta el rótulo genérico Otro antecedente registrado. Las observaciones se agrupan por sección y los respaldos por tipo; el detalle conservado sigue consultable. Botón Cerrar antecedentes y volver a revisiones con retorno de foco; consulta de solo lectura que no altera campos pendientes.

Validación nueva: TypeScript, ESLint y formato dirigidos aprobados; 21 Chromium aprobadas (5 nuevas de contexto y 16 de regresión de versiones/revisiones). Fixture extensa con 120 observaciones y 34 respaldos; apartados cerrados inicialmente, acceso a datos adicionales, ausencia de escrituras, conservación de valores y fundamento pendiente, teclado y anchos 320/1280. Capturas de ambos anchos inspeccionadas. No se repitieron pruebas backend ni se realizaron escrituras de datos por este ajuste visual.

Próximo paso inmediato: comprobar la nueva consulta de antecedentes en la versión 5 durante el recorrido asistido; resolver los campos pendientes antes de recargar la pestaña. Después retomar la reconsideración No continuar y las comprobaciones pendientes de 5C.1. La primera revisión permanece registrada. Sin commit/push, merge ni despliegue de este ajuste.


### Documentos guardados: versiones EIPD primero — 05/11/2026

El usuario acepta la simplificación de antecedentes («modificación OK») y solicita reorganizar Documentos guardados, porque el borrador/evaluación de origen ocupa la primera parte de la página antes de las versiones EIPD. Se prioriza la consulta documental registrada:

1. Versiones EIPD guardadas, con historial visible inicialmente y orden descendente (más reciente primero). Al consultar una versión, su contenido completo permanece plegado y quedan accesibles las opciones de revisión.
2. Borrador EIPD guardado, identificado como contenido para seguir trabajando y con consulta cerrada inicialmente.
3. Antecedentes de la evaluación, desplegable que agrupa alcance RAT y base jurídica/fundamento. La consulta de base conserva solo sus antecedentes propios; la EIPD se consulta en su bloque específico.

Se distingue explícitamente la numeración documental EIPD de la versión de evaluación. La preparación/registro de nuevas versiones permanece en el circuito del borrador, sin formulario de registro deshabilitado dentro de esta consulta. Se retiran avisos obsoletos que anunciaban la revisión como no integrada y el bloque extenso de capacidades del borrador de solo lectura. Los campos pendientes de revisión se propagan al estado general de trabajo sin guardar; no se alteran datos registrados ni escrituras del servidor.

Archivos modificados en este ajuste: AssessmentFlow.tsx, EipdVersions.tsx, e2e/licitud-workspace.spec.ts y e2e/eipd-versions.spec.ts. Se mantienen los cambios locales previos.

Validación: TypeScript, ESLint, Prettier y diferencias aprobados. 52 Chromium aprobadas en espacio de trabajo, versiones, revisiones y contexto; 2 recorridos dirigidos de navegación conectada aprobados (54 casos distintos). Las 9 de versiones se repitieron y aprobaron tras el último ajuste de contenido plegado. Nuevos casos comprueban orden, versiones recientes primero, consulta sin formulario de registro, ausencia de contenido EIPD en base jurídica, apartados inicialmente cerrados, pendientes conservados y ausencia de escrituras; capturas de orden a 320/1280 inspeccionadas. Respuestas controladas, sin nuevas pruebas backend ni cambios en base de datos por esta reorganización.

Próximo paso: comprobar visualmente Documentos guardados con el usuario, empezando por la versión 5; resolver campos pendientes antes de recargar. Luego retomar la reconsideración y demás comprobaciones manuales pendientes de 5C.1. Sin commit/push, merge ni despliegue.


### Nomenclatura acordada: evaluación numerada y versión EIPD — 05/11/2026

El usuario propone separar «versión de evaluación», «versión documental EIPD» y «revisión». Se adopta **Evaluación n.º N** para el trabajo de origen, **Versión del documento EIPD** (abreviado **Versión EIPD**) para la copia registrada y **Revisión** para la actuación sobre esa copia. Ejemplo: Evaluación n.º 1 → Versión EIPD 5 → Revisión 1. Se elige la alternativa numerada propuesta, sin añadir reglas de ciclo, apertura ni cierre.

Cambio aplicado en las pantallas conectadas de cabecera/contexto, selector, pendientes, listado/editor de evaluación, borrador EIPD, consulta de versiones y expediente. Se conservan los nombres de las revisiones y las versiones propias de anexos/infancia. Los campos version/assessment_version, rutas, datos e identificadores no se modifican.

La definición vigente está en circuito-documental-comun.md, apartado Terminología de la interfaz; el contrato 5B.1 incorpora una remisión que aclara sus términos históricos. No se interpreta guardar una edición como crear automáticamente otra evaluación numerada.

Validación: 52 Chromium de versiones, espacio de trabajo y expediente aprobadas; 19 casos dirigidos de navegación aprobados, incluidos contexto a 320/390/1280, selección, evaluación activa frente a documento histórico y pendientes de dos evaluaciones (71 casos distintos; los dos selectores históricos restantes se actualizaron y sus casos se repitieron con resultado aprobado). TypeScript, ESLint y formato dirigidos verificados. Sin pruebas backend adicionales ni migraciones por este cambio de rótulos.

Próximo paso: comprobar con el usuario la terminología en cabecera, selector y versión EIPD 5, y continuar las pruebas manuales pendientes de reconsideración de 5C.1. Sin commit/push, merge ni despliegue.


### Identificación de la persona de la sesión — 06/11/2026

A petición del usuario, Mi organización y Ver contexto completo muestran Usuario de esta sesión: nombre cuando está disponible, correo de acceso y rol en la organización seleccionada. El identificador de perfil se consulta en Identificador de la persona, útil para otorgar facultades sin confundirlo con un número de evaluación o versión documental.

La página de trabajo obtiene el perfil autenticado mediante el endpoint existente /me en el servidor, junto a las organizaciones autorizadas; solo pasa id/email/full_name al componente cliente. El rol procede de la membresía de la organización seleccionada. SessionIdentity.tsx se comparte entre ConnectedWorkspace.tsx y ConnectedContextSummary.tsx. El bloque queda fuera del formulario organizacional deshabilitado, por lo que también puede consultarlo quien tiene rol editor o solo consulta. Si falta identidad se informa sin inventar una persona. No se modifican facultades, autorización, registros ni almacenamiento del navegador.

Archivos: frontend/app/dashboard/trabajo/page.tsx; componentes de navegación SessionIdentity, ConnectedWorkspace y ConnectedContextSummary; fixture conectada y pruebas dirigidas. 12 Chromium aprobadas: perfiles A/B y cambio de rol por propiedades, ausencia explícita de identidad, organización/contexto a 320/1280, rol editor, cierre/foco, pendientes intactos y ausencia de escrituras. TypeScript, ESLint, Prettier y diferencias verificados; capturas de móvil/contexto y escritorio/organización inspeccionadas. Pruebas con identidades ficticias controladas; pendiente confirmación manual en las sesiones reales A y B.

Próximo paso: abrir Mi organización y Ver contexto completo en ambos navegadores y comprobar correo, rol e identificador de cada sesión; después retomar la reconsideración y el resto del recorrido manual de 5C.1. Sin nuevas escrituras de datos, migraciones, commit/push, merge ni despliegue por este ajuste.


### Publicación autorizada — 06/11/2026

El usuario solicita ejecutar commit y autoriza push del trabajo de este recorrido. Se prepara la entrega en feature/eipd-5c1-revision: revisión de versiones y facultades 5C.1, consulta EIPD ordenada, pendientes del documento general, nomenclatura Evaluación n.º / Versión EIPD / Revisión e identidad de sesión. Se excluyen outputs/, frontend/next-env.d.ts y los ajustes previos independientes de infancia y comparación de aplicabilidad, incluidos sus enlaces/expectativas asociados. Los cambios excluidos se conservan localmente.

La publicación no declara terminado el checklist manual: se confirmó autorrevisión bloqueada, acceso de B y primera revisión Requiere cambios de la versión EIPD 5; se aceptó la consulta resumida. Continúan pendientes la reconsideración y el resto de pruebas asistidas, así como 5C.2. Confirmación y activación permanecen bloqueadas. No hay autorización de merge ni despliegue.


Validación final de publicación: copia temporal creada desde el árbol exacto preparado en Git, sin los cambios locales excluidos. TypeScript, ESLint y Prettier aprobados; 55 Chromium de versiones/contexto/revisiones/pendientes/espacio de trabajo/identidad y 5 dirigidas de navegación aprobadas (60 en total). Ruff y Black dirigidos del servidor aprobados. Las 59 pruebas PostgreSQL y su exclusión histórica documentadas arriba conservan su evidencia previa; no se declaran repetidas por esta publicación. Siguiente paso funcional: continuar el checklist asistido de reconsideración/revocación antes de cerrar 5C.1.


### Recorrido asistido: reconsideración confirmada y concurrencia no concluyente — 06/11/2026

El usuario confirma Paso 1 OK (consulta de la revisión existente como B) y Paso 2 OK (reconsideración). En las capturas siguientes se observa la reconsideración No continuar con referencia SIMULADA-5C1-RECONSIDERACION-02 como actuación 8; existen actuaciones de prueba anteriores.

Para Paso 3, la primera captura muestra CONCURRENCIA-A registrada como actuación 9 y la segunda muestra CONCURRENCIA-B registrada como actuación 10, ambas de la versión del documento EIPD 5. No se valida todavía el rechazo de una pestaña desactualizada. La instrucción anterior de esperar exactamente tres actuaciones no era aplicable al historial ya existente.

Comprobación ejecutada en desarrollo local, transacción de solo lectura y consultas limitadas a ambas referencias dentro de CumpleIA Demo: A referencia la actuación previa 8; B referencia la previa 9. Se reconstruyeron los datos de cada solicitud y su huella almacenada: ambas coinciden con esos precedentes. La solicitud B no coincide con una previa 8. Esto acredita que B llegó al servidor con previa 9; no demuestra aceptación de una solicitud desactualizada ni permite atribuir por sí solo la causa de actualización de la segunda pestaña. Se solicitó al usuario aclarar si consultó o recargó entre ambos envíos.

Próximo paso: repetir Paso 3 de forma controlada con el historial actual (10 actuaciones): ambas pestañas consultan primero la 10; primera registra A y la segunda envía sin consultar ni recargar. Comprobar rechazo, conservación de campos y ausencia de nueva actuación B. No eliminar ni reescribir las actuaciones de prueba existentes. Sin cambios de código, escrituras de datos, pruebas automáticas nuevas, commit ni push por este diagnóstico.


### Segundo intento de conflicto: B2 no registrado — 06/11/2026

Las capturas preparatorias muestran ambas pestañas con última actuación 10 y B2 preparado. El usuario confirma A2 como actuación 11 y luego reporta «prueba fallida». La captura posterior conserva fundamento/referencia/declaración de B2, muestra la actuación 11 y no incluye un aviso de resultado dentro del encuadre.

Verificación adicional ejecutada en transacción de solo lectura y limitada al mismo tenant/documento: SIMULADA-CONFLICTO-A2 existe como actuación 11, previa 10; SIMULADA-CONFLICTO-B2 no existe y la última actuación sigue siendo 11. No se acredita un registro indebido de B2; tampoco se declara aprobado el rechazo por conflicto sin conocer la respuesta mostrada o recibida. La captura posterior ya muestra el historial actualizado a 11, por lo que no debe reenviarse B2 con ese estado para intentar demostrar una previa 10.

Próximo paso: comprobar el mensaje de resultado debajo del formulario y aclarar qué ocurrió al enviar B2. Mantener el historial intacto y no avanzar a revocación hasta resolver el resultado del Paso 3. Sin cambios de código ni nuevas escrituras de datos, pruebas automáticas, commit o push.


### Conflicto observado en navegador y aviso corregido — 06/11/2026

El usuario informa que Registrar reconsideración no agrega actuación ni muestra aviso y solicita continuar. Inspección de la pestaña Comet mediante la habilidad computer-use: la consola conserva una respuesta 409 Conflict para POST a la ruta de revisiones de la versión EIPD 5; la página no muestra alerta y conserva los campos B2. No se pulsó Registrar, no se reenviaron solicitudes y no se cambió el historial durante la inspección. Se cerró el panel de diagnóstico al finalizar.

El componente anterior quitaba el formulario ante 409, dejaba el aviso al final sin foco y borraba el error al iniciar cualquier consulta. Se corrige EipdVersionReviews.tsx: aviso destacado y enfocado/desplazado a la vista; formulario conservado tras conflicto, con reenvío bloqueado hasta consulta explícita; aviso de intento no registrado que permanece al actualizar historial; revisión previa consultada visible. La preparación de la solicitud queda dentro del manejo de errores. No cambia el control transaccional del servidor.

Validación: tipos y ESLint aprobados; 19 Chromium aprobadas en revisiones y versiones. Incluye dos pestañas reales controladas por una ruta simulada común: ambas consultan 10, A registra 11, B envía previa 10 y recibe 409; se comprueban ausencia de actuación 12, campos/declaración conservados, aviso enfocado y dentro del viewport a 1280/320, bloqueo del reenvío, ausencia de consulta automática y actualización explícita a previa 11 sin nuevo POST. Se inspeccionaron capturas; sin repetir pruebas backend porque no se modifica su código. El servidor local compila el ajuste; la pestaña que estaba abierta aún no muestra el nuevo rótulo, por lo que necesita una carga nueva para verificar la corrección visual.

Paso 3: se observó rechazo 409 y ausencia de B2; la presentación del resultado requería corrección. Pendiente aceptación manual del aviso actualizado antes de continuar a las pruebas de facultad revocada/vencida. Conservar B2 sin reenviar; se puede abrir una pareja de pestañas nuevas para cargar el ajuste y comprobar que ambas indican Revisión previa consultada: 11. Sin commit/push, merge ni despliegue de este ajuste.


### Paso 3 aceptado y revocación registrada por el usuario — 06/11/2026

El usuario confirma A3 como actuación 12 (SIMULADA-CONFLICTO-A3) y aporta captura del aviso visible de conflicto al enviar B3 desde previa 11. Posteriormente confirma Paso 3 OK: campos conservados, registro bloqueado hasta consulta explícita, historial actualizado a previa 12 y ausencia de actuación SIMULADA-CONFLICTO-B3. Queda aceptado el recorrido asistido de conflicto con el aviso corregido; la corrección de interfaz continúa local, sin nueva publicación.

A continuación se indica descartar únicamente los campos del intento B3 y, como A, registrar la revocación de la facultad de B con referencia SIMULADA-5C1-REVOCACION-B. El usuario responde «recorrido OK» a ese paso: se registra confirmación del otorgante sobre la revocación, sin atribuir todavía una comprobación posterior de bloqueo desde B ni una verificación nueva de base de datos.

Próximo paso inmediato: como B, consultar revisiones y facultades de la versión EIPD 5 y comprobar facultad no vigente, imposibilidad de nuevas actuaciones y consulta intacta de las 12 anteriores. Después quedan por completar vencimiento, sucesora independiente y recorrido favorable sobre una versión completa según el contrato. No se cierra globalmente 5C.1 ni se inicia 5C.2 por estas confirmaciones.


### Paso 5 aceptado: revocación bloquea actuaciones y conserva historial — 06/11/2026

El usuario confirma Paso 5 OK y aporta captura de B con Revisión previa consultada: 12, registro de reconsideración deshabilitado e historial de facultades que conserva otorgamiento (1) y revocación (2), esta última con referencia SIMULADA-5C1-REVOCACION-B. Se incorpora la confirmación del usuario sobre consulta de las 12 revisiones anteriores y bloqueo por falta de facultad vigente. No se ejecutó una consulta nueva de base de datos ni se modificaron actuaciones.

Próximo paso inmediato: A otorga una nueva facultad a B con vencimiento futuro cercano (cinco minutos, hora local); comprobar desde B que se habilita la revisión antes del vencimiento y, después, que se bloquea sin borrar los registros anteriores. No registrar revisiones adicionales solo para verificar la habilitación. Después continúan sucesora independiente y favorable sobre versión completa. Sin cierre global de 5C.1 ni nueva publicación.


### Pasos 6/7 aceptados: facultad temporal y vencimiento — 06/11/2026

El usuario confirma la habilitación temporal (Paso 6) y Paso 7 OK tras vencer. La captura de administración conserva otorgamiento 1, revocación 2, un otorgamiento 3 sin vencimiento seguido de revocación 4, y otorgamiento 5 con referencia SIMULADA-5C1-VENCIMIENTO-B, registrado 2026-11-06T17:51:39.980994+00:00 y vencimiento 2026-11-06T17:56:00+00:00 (14:56 hora local). El reloj de la captura muestra 15:00. No aparece una revocación posterior al otorgamiento 5.

Se registra la confirmación del usuario de que B pudo consultar las 12 revisiones y quedó bloqueado después del vencimiento. La captura aportada corresponde a la administración de facultades por A; no se la presenta como imagen del bloqueo de B. No se ejecutaron nuevas escrituras ni consultas de base de datos para esta anotación.

Próximo paso inmediato: registrar expresamente, como A, una versión sucesora EIPD de prueba y comprobar que comienza sin revisiones mientras la versión 5 conserva las 12 anteriores. Después completar la comprobación de Favorable sobre una versión documental que cumpla requisitos, contrastando que completar el borrador no habilita retrospectivamente Favorable para la versión 5. La facultad de B está vencida y requerirá un nuevo otorgamiento explícito antes de una actuación futura.


## Punto de reanudación histórico: pausa antes del Paso 8 — 06/11/2026

El usuario solicita detener el recorrido para retomarlo en unas horas, registrar avance, ejecutar commit y autoriza push. Queda pausado el recorrido manual exactamente antes de iniciar el Paso 8. No se ha ejecutado el registro de la sucesora por este paso; no se programa recordatorio ni se continúan pruebas manuales durante la pausa.

### Avance aceptado en este recorrido

- Paso 1: consulta de la revisión existente como B, identidad de la sesión y bloqueo de Favorable en la versión incompleta.
- Paso 2: reconsideración con conservación de las actuaciones anteriores.
- Paso 3: conflicto entre pestañas, rechazo visible y enfocado, campos conservados, consulta explícita requerida, ausencia de B3 y actualización del historial sin reenvío.
- Paso 4: revocación registrada por A.
- Paso 5: B bloqueado tras revocación; lectura de las 12 actuaciones e historial de facultades conservados.
- Paso 6: facultad temporal habilitada antes del vencimiento.
- Paso 7: B bloqueado tras el vencimiento; historial conservado sin nueva revocación por el mero transcurso del tiempo.

La evidencia manual es la confirmación del usuario y las capturas descritas en los apartados anteriores; no se amplía a una aceptación de todo 5C.1 ni a pruebas todavía pendientes.

### Estado que debe reconocerse al volver

- Rama: feature/eipd-5c1-revision.
- Organización: CumpleIA Demo; evaluación n.º 1, tratamiento ficticio Gestión de trabajadores.
- Versión del documento EIPD utilizada: 5, referencia SIMULADA-EIPD-TRABAJADORES-001.
- Última revisión aceptada en el recorrido: 12, referencia SIMULADA-CONFLICTO-A3. Los intentos B2/B3 no deben reenviarse.
- B: perfil b73b52fc-127a-4c84-8ecc-f7611852ad9b. La facultad del otorgamiento 5 ya venció; no habilita nuevas revisiones. Requerirá un nuevo otorgamiento expreso antes de revisar en etapas posteriores.
- No se ejecutó el Paso 8; la versión sucesora para esa prueba sigue pendiente.

### Próxima acción exacta

Retomar como A: abrir la misma evaluación, consultar el estado actual y preparar el registro de una versión sucesora desde el borrador guardado. Si la última versión sigue siendo 5, la sucesora será la 6. Motivo de prueba: [FICTICIA] Versión sucesora para comprobar que su historial de revisiones es independiente. Revisar el paquete y sus pendientes, marcar declaraciones ficticia/lectura y registrar expresamente. Después comprobar historial vacío de la sucesora y conservación de las 12 revisiones de la versión 5.

Quedan pendientes la sucesora independiente y la revisión Favorable sobre una versión completa, incluyendo el rechazo de Favorable sobre la versión 5 incompleta aunque se complete después el borrador. No iniciar 5C.2 ni habilitar confirmación/activación.

### Alcance del commit autorizado en esta pausa

Solo EipdVersionReviews.tsx, su prueba e2e/eipd-version-reviews.spec.ts y esta documentación/HANDOFF. Corrección del aviso de conflicto ya validada: 19 Chromium aprobadas, incluidos dos escenarios de dos pestañas a 1280/320; tipos, lint y formato aprobados. Se conserva esa evidencia sin atribuir una nueva ejecución durante la pausa. Los ajustes previos ajenos de infancia/aplicabilidad, next-env.d.ts y outputs/ quedan locales. Sin merge ni despliegue.

## Cierre del recorrido manual — 07/11/2026

El usuario aceptó el recorrido de 5C.1 y solicitó su cierre. Las comprobaciones se realizaron con datos ficticios en CumpleIA Demo, tratamiento Gestión de trabajadores, Evaluación n.º 1.

| Paso | Resultado observado |
| --- | --- |
| 8 | A revisó la asociación de la determinación con el alcance actual, guardó la determinación y registró la versión EIPD 6. |
| 9 | La versión 6 empezó con cero revisiones. La versión 5 conservó sus 12 revisiones, con `SIMULADA-CONFLICTO-A3` como última. |
| 10 | Favorable estuvo bloqueado en las versiones 5 y 7 por requisitos de su contenido conservado. Tras resolver los pendientes documentales y registrar la versión 8, la consulta como B mostró Favorable habilitado. La versión 8 tenía cero revisiones. |

La comprobación de Favorable se aceptó en la interfaz. Quedan pendientes como verificaciones separadas el registro y la consulta posterior de una conclusión Favorable, y la prueba con lector de pantalla. Este cierre documental usa la evidencia manual compartida y las verificaciones automáticas ya registradas.

El siguiente paso es precisar el contrato de 5C.2 para la decisión de la organización sobre una versión EIPD y las facultades independientes para emitirla. Confirmación y activación quedan fuera de ese contrato.
