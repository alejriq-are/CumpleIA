# Paso 5A — contrato común del circuito documental

Identificador: **LIC-DOC-001**. Fecha: 02/11/2026.
Estado: **actuaciones y reglas V1–V3 aprobadas por el usuario el 02/11/2026; implementación pendiente**.
Base inspeccionada: `f0d53ef92e4daacc8d692cad1525c9f1716594ba`.
Rama de preparación: `feature/circuito-documental-5a`.
Publicación: commit y push de la propuesta autorizados el 02/11/2026; no equivalen a validar V1–V3 ni a implementar 5B–5D.

## Aprobación funcional — 02/11/2026

El usuario aprobó expresamente las siguientes actuaciones y las tres reglas V1–V3. Esta aprobación de diseño es posterior a la publicación de la propuesta `a5a51c3`; no acredita implementación ni concede facultades personales.

| Actuación | Quién la realiza |
| --- | --- |
| Preparar la base y su fundamento | Persona encargada de completar la evaluación, con permiso de edición |
| Revisar el fundamento y emitir una conclusión | Delegado u otra persona autorizada para revisar |
| Aceptar la base por la organización | Persona con facultad expresa para esa decisión; puede ser el delegado previa comprobación de sus atribuciones e independencia |

1. Registrar una versión incompleta permite conservarla; aceptarla exige requisitos completos y revisión favorable.
2. Editar, revisar y decidir requieren atribuciones diferenciadas; ser DPD o administrador no concede aceptación automática.
3. Cada aceptación corresponde a una versión exacta y no se hereda a las siguientes.

La aprobación cubre estas reglas funcionales. Los detalles técnicos de API, migraciones, concurrencia e idempotencia deben concretarse y comprobarse en los sublotes. La regla adicional propuesta de impedir la revisión favorable por la propia persona autora no se considera aprobada por inferencia: debe precisarse al diseñar 5C. La posibilidad de que el delegado revise y decida exige las comprobaciones expresamente aprobadas arriba.

5B.1: implementación local del servidor preparada; ver [contrato técnico, evidencia y límites](eipd-versiones-5b1.md). Siguiente tarea: 5B.2, integración de la interfaz y validación conjunta. No cambiar retroactivamente el circuito de infancia. FORM-R01 a FORM-R05 continúan abiertos.

## 1. Objetivo y límites

Definir un patrón común para guardar borradores, registrar versiones, revisar y decidir sobre documentos de una evaluación. Incorpora el diseño aprobado [LIC-GOV-001](revision-aceptacion-base-licitud.md). Los permisos y transiciones nuevos de este contrato son propuestas de producto: no se presentan como obligaciones legales ni como funciones ya disponibles.

5A es documental. No crea tablas, rutas, permisos ni registros de prueba; no cambia la política de infancia. Confirmar una evaluación, aceptar un documento y activar EIPD son acciones distintas. La confirmación y la activación EIPD permanecen bloqueadas.

## 2. Estado comprobado y destino propuesto

| Área | Comportamiento existente | Ampliación prevista |
| --- | --- | --- |
| Evaluación de licitud | Tiene identidad y versión propias; guarda base propuesta, fundamento, formularios y alcance asociado | Conservar esa identidad; no usar su número como versión documental |
| EIPD general | Edita, guarda y consulta un borrador en la evaluación; el nombre de la edición es texto libre | 5B: versiones documentales registradas; 5C: revisión y decisión |
| Infancia | Registra versiones inmutables, revisiones negativas y decisiones de organización con facultad expresa | Mantener contratos e historial. Cualquier convergencia requiere migración y validación separadas |
| Base y fundamento | Guarda una base propuesta, fundamento, consentimiento y LIA como formularios conservados; diagnósticos independientes | 5D: adoptar el circuito según LIC-GOV-001 |
| Aplicabilidad, valoración y anexos | Mantienen sus propias revisiones o versiones | Referenciar la identidad exacta, sin confundir sus contadores |

Infancia admite hoy revisión documental negativa (`requiere_cambios`, `no_continuar`) y una decisión de organización separada (`acepta`, `rechaza`, `requiere_cambios`). No existe una revisión favorable como requisito previo en ese circuito actual. Las reglas futuras siguientes no se le aplican retroactivamente.

## 3. Identidades y estados separados

| Concepto | Qué identifica | Efecto de guardar |
| --- | --- | --- |
| Ediciones pendientes | Campos temporales de esta pestaña | Se conservan al navegar en esta pestaña; solo guardar los envía al servidor. Recargar puede perderlos |
| Borrador guardado | Documento editable del tipo y evaluación seleccionados, con revisión de concurrencia | Actualiza ese borrador; no crea versión documental registrada |
| Versión documental registrada | Fotografía inmutable, con ID y número asignados por servidor dentro de su serie | Solo el registro explícito crea otra versión |
| Revisión documental | Actuación sobre una versión exacta, con resultado y fundamento | Agrega un evento; no edita el documento |
| Decisión de organización | Posición de una persona expresamente facultada sobre una versión exacta | Agrega un evento; no cambia su contenido ni activa EIPD |
| Nombre de la edición | Etiqueta opcional de reconocimiento | No identifica ni numera una versión |

La serie se delimita por organización, tratamiento, evaluación y tipo de documento. Otra evaluación no continúa automáticamente la serie anterior. Cada copia conserva la procedencia cuando existe.

No se utiliza un único estado ambiguo «aprobado». Se muestran por separado:

- **Trabajo:** sin cambios pendientes / cambios sin guardar / guardando / error o resultado incierto.
- **Documento:** borrador guardado / versión registrada N / preparación temporal de sucesora.
- **Revisión:** sin revisión / favorable / requiere cambios / no continuar, con autor, fecha y versión revisada.
- **Decisión:** sin decisión / acepta / requiere cambios / rechaza, con facultad y versión decidida.
- **Correspondencia:** coincide con el material asociado / requiere nueva revisión / no se pudo comprobar.
- **Disponibilidad:** acciones permitidas y requisitos faltantes, calculados por servidor.

«Acepta» significa aceptación documental de la organización en este circuito. No acredita por sí sola licitud, suficiencia jurídica, vigencia de controles ni autorización para operar.

## 4. Contenido exacto que se registra

El servidor construye y conserva un paquete inmutable con:

1. Organización, tratamiento, evaluación, versión de evaluación y tipo de documento.
2. Contenido estructurado, referencia y nombre de edición; versión del esquema.
3. Alcance adoptado en esa evaluación: finalidad, titulares y categorías; identidad y huella de su snapshot.
4. Determinación de aplicabilidad utilizada y su revisión, cuando corresponda.
5. Valoración incorporada y anexos explícitos: ID, versión y huella exactos. Una referencia libre no se transforma automáticamente en evidencia adjunta.
6. Diagnóstico documental y versión de reglas utilizados para registrar; faltantes declarados.
7. Autor autenticado, fecha UTC, procedencia de copia y motivo de nueva versión.
8. Huellas de contenido y contexto, con algoritmo de canonicalización versionado.

Las huellas se calculan en servidor sobre una representación estable; no se confía en hashes, identidad del autor o permisos enviados por el cliente. La consulta traduce fechas e identificadores sin inventar nombres.

Registrar toma el **borrador ya guardado** y las versiones de respaldos seleccionadas, no los campos pendientes del navegador. Si hay pendientes se pide guardarlos primero. El usuario ve antes la versión de origen y las referencias que se incorporarán.

Una versión puede registrarse incompleta, con faltantes visibles; registrarla no equivale a declararla completa. No podrá aceptarse mientras incumpla los requisitos documentales aplicables. Los diagnósticos deterministas no sustituyen la revisión humana.

## 5. Transiciones propuestas para los nuevos circuitos

| Acción | Condiciones | Resultado |
| --- | --- | --- |
| Guardar borrador | Permiso de edición y revisión esperada coincidente | Actualiza borrador y diagnóstico; conserva versiones anteriores |
| Ver vista previa | Campos disponibles en la pestaña | Consulta de lo preparado, incluidos pendientes; sin escritura |
| Registrar versión | Borrador guardado, sin diferencias locales, permiso de registro, origen/contexto/revisiones comprobados | Nueva fotografía inmutable y número del servidor; queda sin revisión y sin decisión |
| Preparar sucesora | Lectura del original y permiso de preparación | Copia temporal identificada; no modifica ni registra el original |
| Registrar revisión | Facultad de revisión, versión exacta consultada y correspondencia comprobada | Evento favorable, requiere cambios o no continuar, siempre motivado |
| Registrar decisión | Facultad expresa vigente, versión exacta y requisitos de la decisión | Evento acepta, requiere cambios o rechaza, con fundamento y referencia del acta |

Para **aceptar**, se propone exigir la última revisión documental favorable sobre esa misma versión y contexto, sin otra revisión posterior que requiera cambios o indique no continuar. La revisión favorable exige requisitos documentales completos y no concede aprobación jurídica. Requerir cambios o rechazar no exige revisión favorable previa.

La propuesta de separación de funciones es: la persona autora de la versión no emite su revisión favorable. La persona revisora puede decidir además por la organización solo con facultad expresa de decisión y compatibilidad de funciones documentada; ser DPD o administrador no la concede. Este criterio debe validarse conjuntamente antes de programar 5C/5D.

Una nueva actuación no borra la anterior: el estado visible se obtiene de eventos ordenados por secuencia asignada por servidor. Se admite reconsideración motivada sobre la misma versión si su material no cambió, bajo los mismos requisitos, vinculando el evento anterior. Si cambia el contenido, se requiere otra versión y nuevas actuaciones.

## 6. Base y fundamento: regla específica para 5D

La propuesta guardada sigue siendo una sola por evaluación y finalidad. Consentimiento y LIA pueden conservarse como alternativas estudiadas; eso no significa que ambas sean bases seleccionadas.

El paquete para registrar incluye base propuesta, fundamento, alcance y el formulario pertinente. Un consentimiento o LIA conservado como alternativa se identifica como antecedente y no se presenta como fundamento activo. Si se selecciona otra base, se documentan sus antecedentes pertinentes; no se exige completar ambos formularios por defecto.

Con «Pendiente de definir» se permite guardar y documentar faltantes, pero no aceptar la base por la organización. La decisión futura no sobrescribe la propuesta del editor: registra quién acepta o rechaza qué paquete exacto. Cambiar la selección, fundamento o formulario pertinente exige nueva versión para otra decisión.

Este contrato no resuelve FORM-R01 a FORM-R05. En particular, la cobertura normativa y la evidencia por criterio deben completarse antes de afirmar que el diagnóstico habilita aceptación documental en producción.

## 7. Facultades y aislamiento

| Acción | Habilitación propuesta |
| --- | --- |
| Consultar documento e historial | Acceso de lectura a la organización y expediente |
| Editar borrador | Permiso de edición del expediente; no permite decidir |
| Registrar versión | Capacidad expresa de registro para el tipo documental y expediente |
| Revisar | Facultad expresa de revisión para el tipo documental y expediente |
| Decidir | Facultad expresa de decisión para ese tipo documental y expediente |
| Otorgar/revocar facultad | Gestión autorizada de facultades, con referencia y evidencia del otorgamiento |

Estas capacidades son conceptos del contrato, no nombres de permisos ya implementados. El diseño técnico de 5B/5C deberá mapearlas explícitamente a la autorización existente. No reutilizar una facultad de infancia para EIPD general o Base y fundamento.

El otorgamiento identifica persona, organización, tratamiento, evaluación, tipo documental, acción habilitada, referencia, evidencia y período de vigencia cuando se establezca. Se conserva cada otorgamiento/revocación; el servidor comprueba su estado al ejecutar la acción. No se permite autoatribuir facultades mediante el formulario.

Ser DPD permite identificar una función, pero no infiere automáticamente facultad de decidir. Puede ser revisor y/o decisor conforme a la designación y compatibilidad documentadas, según LIC-GOV-001. La independencia y los posibles conflictos se revisan antes de otorgar las facultades.

La revocación bloquea actuaciones nuevas; conserva la decisión histórica y la facultad utilizada entonces. La pantalla distingue «facultad utilizada al registrar» de «facultad actual» y no interpreta una revocación como borrado o nulidad automática del acto pasado.

Cada acceso valida JWT, pertenencia, organización y expediente en servidor. Las tablas nuevas tendrán tenant, claves que impidan relaciones entre organizaciones y RLS desde su primera migración; runtime `app_user` sin BYPASSRLS. Lectura autorizada no implica escritura.

## 8. Efecto de cambios posteriores

| Cambio | Tratamiento del historial y de la siguiente acción |
| --- | --- |
| Editar un borrador después del registro | La versión y sus actuaciones permanecen; se muestra que difiere del borrador. No se trasladan al borrador sus decisiones |
| Registrar una sucesora | La anterior queda histórica; la nueva parte sin revisión ni decisión. Conservar origen y motivo |
| Modificar el RAT | No sustituye automáticamente el alcance de la evaluación. Mostrar diferencia; contrastar y adoptar expresamente antes de aceptar material afectado |
| Adoptar otro alcance o cambiar aplicabilidad | Conservar actuaciones previas; exigir reevaluación de correspondencia y nueva versión cuando cambie el paquete |
| Agregar otra versión de anexo o valoración | No altera respaldos congelados; incorporarla requiere nueva versión documental |
| Cambiar reglas del diagnóstico | Conservar reglas y resultado originales; mostrar si requiere reevaluación bajo las nuevas reglas, sin reescribir el resultado histórico |
| No poder consultar estado o facultad | No anunciar vigencia ni habilitar aceptación; permitir lectura histórica autorizada y reintento seguro |

La comprobación compara material semántico del alcance y respaldos, no fechas de actualización aisladas. Una diferencia material pendiente no se interpreta como «coincide». Los cambios puramente de presentación no alteran las huellas. La definición exhaustiva de campos materiales deberá quedar codificada y probada por tipo documental antes de su aceptación formal.

## 9. Concurrencia y resultado incierto

Cada escritura incluye revisión esperada del recurso; registrar incluye revisión del borrador, contexto y serie; revisar/decidir incluye versión, revisión del historial y facultad esperadas. El servidor vuelve a comprobarlas dentro de la transacción.

El registro asigna el número y guarda paquete/evento de forma atómica. Decidir y revocar comparten la coordinación necesaria para impedir una aceptación posterior a una revocación ya confirmada. Respetar el orden de bloqueo existente selector global → serie; documentar cualquier extensión antes de implementarla.

Se propone una clave de idempotencia por organización, actor y acción. Misma clave y mismo contenido devuelve el resultado original autorizado; reutilizarla con contenido distinto produce conflicto. Tras un corte de conexión, consultar el resultado de esa operación antes de reenviar; no mostrar «guardado» ni repetir a ciegas.

| Situación | Respuesta funcional propuesta |
| --- | --- |
| Sin sesión válida | Recuperar sesión en otra pestaña; conservar pendientes en la original |
| Sin permiso o recurso ajeno | Denegar sin revelar datos del otro tenant; distinguir 403/404 según política del API |
| Revisión/contexto/facultad cambiados | 409; conservar campos y ofrecer consulta/comparación, sin sobrescribir |
| Datos o requisitos insuficientes | 422 con campos y motivos; conservar campos |
| Sin conexión o respuesta incierta | Explicar conservación temporal y consulta del resultado; no confundir con lista vacía |

Los borradores pendientes siguen siendo temporales por pestaña. No introducir persistencia de contenido sensible en localStorage/sessionStorage. Consultar o reintentar una lectura no guarda, registra, decide ni sincroniza las demás pestañas.

## 10. Contrato técnico mínimo para 5B–5D

Entidades conceptuales futuras: serie documental, versión registrada, evento de revisión, evento de decisión, facultad y recibo de operación idempotente. Separar el borrador mutable de estas entidades inmutables. Versión y actuaciones deben tener claves de tenant/expediente/tipo y referencias exactas; evitar eliminaciones en cascada del historial.

Antes de escribir la primera migración se deben cerrar nombres, DTO versionados y rutas en el contrato del sublote. No se declaran endpoints nuevos disponibles por este documento. La respuesta de consulta entregará contenido, identidad, correspondencia, revisión, decisión y acciones/requisitos calculados; la interfaz no deduce autorización a partir de un rótulo o resultado diagnóstico.

Las migraciones serán nuevas y append-only; no convertir el `document_version` libre histórico en un número de versión. Los borradores existentes siguen siendo borradores. No registrar automáticamente el historial anterior ni atribuirle revisores o decisiones inexistentes.

## 11. Plan de implementación y puertas de validación

| Lote | Entrega acotada | Evidencia necesaria antes del cierre |
| --- | --- | --- |
| **5A** | Este contrato y continuidad documental | V1–V3 aprobadas; revisar enlaces y consistencia contra código |
| **5B.1** | Contrato API/migración, registro inmutable EIPD general e idempotencia | PostgreSQL aislado con RLS/runtime real, tenant ajeno, permisos, concurrencia y resultado incierto |
| **5B.2** | Vista previa, registro explícito, consulta histórica y preparación de sucesora | Navegador y recorrido conjunto; pendientes conservados, teclado, foco y ventana estrecha |
| **5C.1** | Revisión EIPD general y facultades de revisión | Resultado motivado sobre versión exacta; separación de autoría; historial inmutable y aislamiento |
| **5C.2** | Decisión de organización y facultades de decisión | Revisión requerida, revocación concurrente, conflicto, actos anteriores consultables y EIPD bloqueada |
| **5D.1** | Paquete de Base y fundamento y revisión | Base única, alternativas identificadas, diagnóstico guardado exacto; cobertura FORM pendiente visible |
| **5D.2** | Decisión de Base y fundamento y navegación | Facultades independientes, pendiente de definir bloqueado, cambio de base/contexto sin herencia |

Cada lote requiere sus comprobaciones y validación conjunta antes de pasar al siguiente. Una prueba con respuestas controladas no sustituye persistencia/aislamiento real. Infancia mantiene pruebas de regresión y contratos actuales. No hay merge ni despliegue por completar estos lotes.

### Roles y separación de actuaciones en 5C

| Actuación | Facultad requerida |
| --- | --- |
| Preparar el borrador y registrar la versión | Autor con permiso de edición y registro para el expediente. |
| Emitir una conclusión sobre la versión registrada | Revisor autorizado, que puede ser el DPD u otra persona facultada. |
| Aceptar la versión por la organización | Persona con facultad expresa de decisión para el expediente. |

La regla general contempla tres personas distintas. En un esquema de dos personas, la persona revisora puede también decidir si ambas facultades son expresas y se documenta la excepción y la comprobación de independencia. La persona autora queda separada de ambas actuaciones. Ser DPD o administrador no concede por sí solo la facultad de aceptar.

La gestión de estas facultades se propone en **Mi organización → Personas y facultades**. Debe poder consultarse quién tiene cada facultad, su alcance, su vigencia y su historial. El servidor comprueba la facultad y su vigencia al registrar cada actuación.

### Reglas de registro, revisión y aceptación

- **V1.** Se puede registrar una versión incompleta y conservar sus faltantes. Para aceptarla, deben estar completos los requisitos y existir una revisión favorable de esa misma versión.
- **V2.** Editar, revisar y decidir son actuaciones separadas. Cada una requiere su propia facultad y queda registrada con la identidad de quien la realiza.
- **V3.** La aceptación identifica la versión exacta. Una sucesora requiere su propia revisión y decisión. Las versiones anteriores conservan su historial.

### Activación de EIPD fuera de 5C

Aceptar una versión registra la decisión documental de la organización. En un futuro flujo de activación, una acción separada designaría la versión aceptada como referencia operativa para las medidas, responsables, plazos y seguimiento del riesgo residual. Por ejemplo, activar la versión 4 dejaría trazabilidad de quién la activó y cuándo. Registrar o aceptar la versión 5 no reemplazaría automáticamente esa referencia. La confirmación y la activación siguen bloqueadas en el piloto.

### Recorrido explicativo de validación de 5A

1. Guardar un borrador de EIPD: queda editable y todavía sin versión documental registrada.
2. Registrar versión 1: se conserva una fotografía; revisar esa versión no modifica el original.
3. Registrar revisión favorable y decisión de una persona facultada: ambas quedan separadas; EIPD sigue sin activarse.
4. Cambiar el borrador y registrar versión 2: versión 1 conserva sus antecedentes; versión 2 requiere su propia revisión/decisión.
5. En Base y fundamento, conservar consentimiento y LIA con base pendiente: son antecedentes; no hay una base aceptada. Seleccionar una base y registrar su paquete permite iniciar su circuito específico.

Este recorrido explica las reglas aprobadas; todavía no es una prueba disponible en la aplicación.

## 12. Fuentes y verificación de esta entrega

- [Ciclo documental y diferencias actuales](ciclo-documental-eipd.md).
- [Paso 4: cierre y remanentes](paso4-consentimiento-lia.md).
- [Revisión y aceptación de Base y fundamento](revision-aceptacion-base-licitud.md).
- [Aceptación actual de infancia](m3-t1-aceptacion-organizacion.md).
- [Esquemas generales](../../backend/app/schemas/licitud.py), [servicio de licitud](../../backend/app/services/licitud.py).
- [Esquemas de versiones de infancia](../../backend/app/schemas/eipd_child_persistence.py), [persistencia de infancia](../../backend/app/services/eipd_child_persistence.py).
- [Esquemas de facultades/decisiones de infancia](../../backend/app/schemas/organization_acceptance.py), [servicio de aceptación](../../backend/app/services/organization_acceptance.py).

Entrega solo documental: se inspeccionaron contratos/código de referencia y diferencias. No se ejecutaron pruebas funcionales nuevas ni escrituras de datos; las pruebas de Paso 4 siguen siendo evidencia de aquella entrega. La aprobación funcional de V1–V3 está registrada arriba; no acredita implementación de 5B–5D.

## Continuidad 5B.2

La interfaz de versiones EIPD general está implementada localmente; ver [5B.2](eipd-versiones-5b2.md) para alcance, evidencia y checklist de aceptación asistida pendiente. La migración de 5B.1 ya está aplicada en desarrollo local. No se implementan por ello revisión, decisión ni aceptación del documento general (5C), ni el circuito de Base y fundamento (5D). Las versiones incompletas se pueden conservar; registrarlas no constituye aceptación.
