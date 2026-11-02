# LIC-GOV-001 — Revisión y aceptación de Base y fundamento

Estado: diseño funcional aprobado por el usuario el 02/11/2026; implementación pendiente.


Ratificación 02/11/2026: el usuario aprobó expresamente la distribución de preparación, revisión y aceptación, junto con V1–V3 del [contrato común 5A](circuito-documental-comun.md#aprobación-funcional--02112026). La implementación se desarrollará en 5B–5D; las facultades del delegado y su independencia deben comprobarse.

## Objetivo y alcance

Distinguir la preparación de una base propuesta, la revisión de su fundamento y la decisión de la organización para una evaluación concreta. Esta aprobación es un acuerdo de producto; no atribuye por sí misma facultades legales a una persona ni certifica la suficiencia jurídica del análisis.

El editor actual guarda una propuesta y sus formularios. No implementa todavía este circuito formal. El circuito existente de aceptación de versiones de infancia tiene su propio ámbito y no se reutilizará como permiso general para decidir bases de licitud.

## Actuaciones e identidades

1. **Preparar y guardar:** una persona con permiso de edición selecciona la base propuesta y documenta su fundamento. Consentimiento y LIA pueden conservarse como análisis alternativos; su existencia no selecciona dos bases ni acepta ninguna. Si la propuesta guardada es «Pendiente de definir», ambos formularios siguen siendo antecedentes.
2. **Revisar el fundamento:** el delegado designado, o la persona expresamente habilitada para esa revisión, registra una conclusión favorable, requiere cambios o desfavorable, con sus motivos. La revisión no sustituye la decisión de la organización.
3. **Decidir por la organización:** una persona con facultad expresa registra aceptación, solicitud de cambios o rechazo del contenido revisado. El cargo de delegado, administrador o propietario no concede automáticamente esta facultad. El delegado podrá decidir únicamente cuando exista la atribución expresa y se haya resuelto la compatibilidad de funciones e independencia que corresponda.
4. **Consultar antecedentes:** las revisiones y decisiones anteriores permanecen consultables, identificando el contenido al que se refieren. Una aceptación documental no confirma ni activa EIPD ni acredita automáticamente cumplimiento legal.

La interfaz debe mostrar quién actuó, en qué calidad, cuándo, sobre qué evaluación y contenido exacto, y con qué fundamento. No inventar nombres cuando el servidor solo entregue un identificador.

## Contenido revisado y cambios posteriores

Cada actuación debe vincularse a una identidad inmutable del contenido: organización, tratamiento, evaluación, alcance asociado, base propuesta, fundamento, formulario pertinente y evidencias versionadas que se hayan incluido. El servidor debe establecer la revisión o huella del conjunto; un nombre libre de edición no reemplaza esa identidad.

Cambiar posteriormente ese conjunto conserva la actuación histórica y la identifica como correspondiente a contenido anterior. No heredar su aceptación al contenido nuevo. La presencia de un formulario alternativo conservado debe distinguirse del formulario que sustenta la propuesta examinada.

No aceptar una base pendiente de definir. Las condiciones de completitud, secuencia entre revisión y decisión, facultades, y resolución de conflictos de funciones deben quedar expresas en el contrato técnico antes de habilitar escrituras. Una conclusión favorable no debe convertirse por sí sola en autorización automática.

## Plan por lotes pequeños

- [ ] **GOV-01 — Contrato y permisos:** contrastar el diseño con los contratos de consentimiento/LIA y el circuito de infancia; definir actores, ámbito de facultades, transiciones, requisitos y política de separación de funciones. Precisar que «formularios conservados» no significa bases aceptadas. Validar conjuntamente los nombres y el recorrido.
- [ ] **GOV-02 — Revisiones del fundamento:** implementar identidad del contenido, registro histórico de revisión y consulta, con autorización en servidor y aislamiento por organización. Añadir migración append-only/RLS si el modelo lo requiere. Validar primero este circuito, sin habilitar decisiones de organización.
- [ ] **GOV-03 — Decisiones de la organización:** implementar facultades expresas y su revocación, aceptación/cambios/rechazo ligados al contenido exacto, y protección frente a cambios concurrentes. Mantener separados los permisos del circuito de infancia.
- [ ] **GOV-04 — Navegación y aceptación asistida:** integrar las acciones diferenciadas en Base y fundamento, consulta histórica y retorno al editor con pendientes conservados. Comprobar teclado, ventana estrecha, errores y recuperación antes del cierre.

Este trabajo complementa LIC-FORM-001; no cierra sus pendientes de cobertura, evidencias por criterio, compatibilidad y pruebas reales aisladas.

## Criterios de comprobación

- [ ] Guardar Consentimiento y LIA con base pendiente conserva antecedentes sin anunciar una base aceptada.
- [ ] Guardar una propuesta no registra revisión ni decisión.
- [ ] Un delegado sin facultad expresa para decidir puede realizar solo las actuaciones para las que esté habilitado; un administrador tampoco obtiene aceptación implícita.
- [ ] El servidor rechaza actores sin permiso, facultades revocadas y accesos entre organizaciones, incluso manipulando la solicitud.
- [ ] Revisiones y decisiones identifican actor, calidad, fecha, fundamento y contenido examinado; no se modifican ni eliminan silenciosamente.
- [ ] Cambios de contenido o revocación concurrente impiden aceptar una revisión desactualizada, con comprobación transaccional en servidor.
- [ ] Un cambio posterior conserva la decisión anterior como antecedente y exige revisar el nuevo contenido.
- [ ] Consultar y reintentar no guardan, descartan ni copian borradores; un envío de resultado incierto no se repite automáticamente.
- [ ] Confirmación y activación EIPD permanecen bloqueadas.

## Referencias y límites

- [Paso 4 — formularios](paso4-consentimiento-lia.md).
- [Contrato de implementación de consentimiento/LIA](m3-t1-consentimiento-lia-implementacion.md).
- [Circuito de aceptación de infancia existente](m3-t1-aceptacion-organizacion.md).
- [Ley 21.719, texto oficial](https://www.bcn.cl/leychile/Navegar?idNorma=1209272&idVersion=2026-12-01): referencia para distinguir funciones del delegado y responsabilidad de la organización. La implementación requiere contrastar las disposiciones y reglamentación aplicables; este diseño no presume que la ley ordene que el delegado apruebe cada base.

No se han implementado endpoints, permisos, migraciones ni controles de este circuito por la aprobación del diseño. Sin nuevas pruebas de ejecución atribuibles a este documento.
