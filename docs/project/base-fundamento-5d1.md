# 5D.1 · Versión documental y revisión de Base y fundamento

Contrato funcional aprobado. Catálogo, registro, revisión e interfaz implementados localmente. Recorrido conectado pendiente. Base Git `7087c47`. Desarrolla [LIC-GOV-001](revision-aceptacion-base-licitud.md) y el [circuito documental común](circuito-documental-comun.md).

## Recorrido

1. En **Base y fundamento**, guardar la base propuesta, el fundamento y los formularios. Desde ese espacio, preparar el registro y consultar la vista previa del contenido guardado en el servidor. Si existen cambios locales, guardarlos antes de registrar.
2. Registrar expresamente una **Versión de Base y fundamento**, con motivo y declaración de datos ficticios. El servidor asigna su propio número dentro de la evaluación.
3. En **Documentos guardados → Evaluación de licitud guardada**, consultar la lista y abrir una versión exacta. Distinguir la propuesta activa, sus antecedentes alternativos y el diagnóstico conservado.
4. Una persona revisora facultada consulta el historial y registra una conclusión motivada. La decisión de la organización se incorpora en 5D.2. Confirmación y activación EIPD quedan fuera de 5D.1.

## Material conservado

El servidor construye el paquete desde los datos guardados. Conserva organización, tratamiento, serie, evaluación y su número, tipo documental, finalidad, alcance RAT adoptado y su huella canónica. Incluye base propuesta, fundamento, formulario pertinente, antecedentes alternativos identificados, referencias a respaldos incorporados por ID, revisión y huella, diagnóstico documental versionado, y los datos de autoría y registro. La selección de base es única.

| Base propuesta | Formulario principal en el modelo actual |
| --- | --- |
| Consentimiento | `consent_assessment` |
| Obligaciones económicas | `economic_obligations_assessment` |
| Obligación legal | `legal_obligation_assessment` |
| Contrato o medidas precontractuales | `contract_assessment` |
| Interés legítimo | `lia_assessment` |
| Defensa de derechos | `rights_defense_assessment` |
| Pendiente de definir | Ninguno. Consentimiento y LIA guardados se presentan como antecedentes. |

Los formularios de consentimiento y LIA que se conserven sin ser la base principal se etiquetan **Antecedente alternativo**. La vista previa identifica los respaldos que se incorporan. Los anexos versionados se consultan por referencia y las referencias libres se conservan como texto. Los controles transversales, la EIPD general y el expediente de infancia quedan fuera del diagnóstico de esta versión.

## Revisión y facultades

| Resultado | Requisitos documentales |
| --- | --- |
| **Favorable** | Base definida y requisitos esenciales aplicables resueltos. Admite respaldo equivalente verificable y observaciones menores documentadas. |
| **Requiere cambios** | Disponible sobre una versión incompleta o con base pendiente. Requiere fundamento y referencia. |
| **Desfavorable** | Disponible sobre una versión incompleta o con base pendiente. Requiere fundamento y referencia. |

Se puede registrar una versión incompleta o con base pendiente, mostrando sus faltantes. El diagnóstico se genera con los evaluadores existentes de la base seleccionada y se conserva con la versión. Se registra su cobertura y se mantienen visibles los pendientes [FORM-R01 a FORM-R05](paso4-consentimiento-lia.md). El resultado Favorable en el piloto expresa una conclusión documental bajo esa cobertura.

### Criterio aprobado para Favorable

El catálogo versionado de cada base identifica los requisitos esenciales y los de seguimiento. La evaluación de cada requisito se vincula a la versión exacta y conserva el motivo y el respaldo consultado cuando corresponda.

| Situación | Tratamiento en el piloto |
| --- | --- |
| Requisito esencial aplicable sin resolver | Bloquea Favorable. Una base indefinida o un fundamento sin vínculo con la finalidad son bloqueos esenciales. |
| Requisito no aplicable | Se registra No aplica con justificación específica del tratamiento. Un campo vacío conserva el pendiente. |
| Respaldo equivalente | Puede satisfacer el requisito si la persona revisora documenta qué acredita y dónde consultarlo. |
| Observación menor | Puede coexistir con Favorable si no altera el fundamento de la conclusión. Se registra el pendiente, la persona responsable y el plazo de seguimiento. |
| Esencialidad o aplicabilidad sin resolver | Bloquea Favorable. El resultado Requiere cambios identifica la información necesaria. |

El servidor determina los bloqueos a partir del catálogo y de las justificaciones y respaldos registrados. La interfaz muestra por separado los bloqueos, las observaciones de seguimiento y los pendientes de cobertura FORM-R01 a FORM-R05. Las observaciones se asocian a la revisión sin modificar la versión conservada. Favorable sigue siendo una conclusión documental del piloto. La decisión de la organización corresponde a 5D.2.

Se requiere una facultad de **revisión de Base y fundamento** separada de las de EIPD general e infancia. Una persona administradora habilitada puede otorgarla o revocarla para otra persona miembro en el expediente exacto. Se documentan actor, destinatario, alcance, fundamento, respaldo, secuencia y vencimiento cuando se establezca. Quien registró la versión queda excluido de todas sus revisiones. El cargo de DPD o administrador no otorga por sí solo la facultad.

Cada revisión referencia la versión y la facultad utilizada. Una reconsideración conserva la revisión anterior y exige indicar el precedente esperado. Si cambia la base, el fundamento, el formulario o el material incorporado, se prepara una nueva versión con historial propio. La revisión de una versión histórica comprueba su material conservado y muestra el contexto como histórico. En 5D.2 se comprobará la correspondencia actual para una eventual decisión de aceptación.

## Catálogo inicial del piloto

Catálogo de revisión documental aprobado para el piloto, basado en los formularios existentes de CumpleIA. Cada grupo tendrá un identificador estable dentro de un catálogo versionado. Antes de habilitar Favorable, cada hallazgo del evaluador pertinente debe vincularse a un requisito. Los hallazgos sin clasificación quedan pendientes de resolución.

| Base | Requisitos esenciales | Condiciones que se evalúan si aplican |
| --- | --- | --- |
| Todas | Base definida, finalidad y alcance identificados, fundamento que los vincule a la base y formulario principal identificable. Las contradicciones materiales se resuelven antes de Favorable. | La cobertura de formularios y respaldos se registra por separado. |
| Consentimiento | Identificar quién lo otorgó, cómo se obtuvo, qué finalidad cubre y con qué registro se puede verificar. Resolver los hallazgos aplicables sobre información, libertad y retiro del consentimiento. | Si intervino una persona representante, documentar su calidad y respaldo. |
| Obligaciones económicas | Identificar obligación y vínculo con el titular, finalidad, operaciones, alcance y análisis documentado de las reglas pertinentes. Resolver conservación, actualización y minimización cuando afecten la conclusión. | Si hay comunicación, documentar destinatarios y alcance, elegibilidad, exclusiones y restricciones. |
| Obligación legal | Identificar la norma y disposición, su vigencia y cómo se aplica al tratamiento. Explicar qué operación exige o dispone, con qué finalidad y qué datos requiere. | Distinguir la ruta de cumplimiento de una obligación de la ruta de tratamiento dispuesto por ley. |
| Contrato o medidas precontractuales | Identificar relación, ruta y operación, vínculo del titular, necesidad para esa ruta y datos pertinentes. | Si son medidas precontractuales, identificar la solicitud del titular y las medidas concretas. |
| Interés legítimo | Identificar el interés y quién lo persigue. Resolver necesidad, proporcionalidad, expectativas, impacto, salvaguardas relevantes y la ponderación final. Documentar cómo se informa y se atiende la oposición cuando corresponda. | Resolver impactos particulares del contexto, incluidos grupos vulnerables o impactos relevantes sin mitigar, si están presentes. |
| Defensa de derechos | Identificar derecho, titular y vínculo, vía de formulación, ejercicio o defensa, órgano o foro, etapa y necesidad del tratamiento. | Documentar actuaciones preparatorias si todavía no existe expediente formal. Si finalizó, justificar la necesidad de conservar o seguir tratando los datos. |
| Pendiente de definir | La ausencia de base es un bloqueo esencial. Los formularios guardados se conservan como antecedentes. | Pueden registrarse Requiere cambios o Desfavorable conforme a la regla de registro. |

### Cómo resolver un requisito

- **Cumplido.** Identificar el contenido conservado que acredita el criterio. Una referencia alternativa solo se admite si permite comprobar el mismo hecho. Puede ser un correo fechado, registro interno, bitácora o documento breve. Registrar referencia, hecho acreditado y razón de equivalencia.
- **No aplica.** Solo para criterios condicionales. Registrar qué hecho del tratamiento excluye la condición. Los requisitos esenciales comunes y las contradicciones materiales no admiten esta vía.
- **Observación de seguimiento.** Solo cuando el hecho esencial ya está acreditado. Ejemplos posibles son normalizar el nombre de un respaldo o consolidar referencias dispersas que siguen accesibles. Registrar descripción, responsable y plazo.
- **Bloqueo.** Mantener el hallazgo cuando falta acreditar el hecho, hay contradicción material o la aplicabilidad está por resolver. El tamaño de la organización no cambia la clasificación. Un respaldo equivalente cubre un hecho, sin sustituir el análisis de fondo.

El formulario de revisión propondrá resoluciones por requisito con justificación y referencias. El servidor comprobará el catálogo y las restricciones antes de aceptar Favorable. El diagnóstico original permanece asociado a la versión. Las resoluciones y observaciones quedan asociadas a la revisión. Si el hecho que se quiere acreditar cambia el contenido conservado, se registra una nueva versión.

## Contrato técnico propuesto

Usar entidades append-only diferenciadas para versiones, facultades y revisiones de Base y fundamento. Compartir los mecanismos de canonicalización, coordinación por serie, autorización e idempotencia de 5B y 5C donde corresponda. Claves compuestas de tenant, expediente y versión. RLS desde la primera migración, sin ampliar facultades de otros circuitos.

Rutas propuestas bajo `/licitud/treatments/{treatment_id}/assessments/{assessment_id}/base-fundamento-versions/v1`:

| Operación | Rutas |
| --- | --- |
| Preparar, registrar y consultar versiones | `GET /preview`, `POST /`, `GET /`, `GET /{version_id}`, `GET /requests/{request_id}` |
| Consultar y registrar facultades | `GET /review-authorities/history`, `POST /review-authorities` |
| Consultar, registrar y recuperar revisiones | `GET /{version_id}/review-state`, `POST /{version_id}/reviews`, `GET /{version_id}/review-requests/{request_id}` |

El registro recibe la huella esperada del origen, el número de última versión esperado y un identificador de solicitud. La revisión recibe la versión exacta, el precedente esperado, la facultad consultada y su propio identificador. Los DTO son cerrados. La transacción comprueba membresía, facultad, autoría y secuencia. Una misma solicitud con material idéntico recupera el resultado y con material distinto produce conflicto. Ante conflicto, conservar los campos y pedir una consulta explícita. Ante una respuesta incierta, consultar el recibo antes de reenviar.

## Validación para el cierre

- Registrar y consultar versiones con las seis bases y con base pendiente. Verificar una sola base activa, la separación de alternativas, el diagnóstico congelado y la consulta histórica tras cambiar el borrador.
- Probar Favorable con respaldo equivalente, No aplica justificado y observaciones menores documentadas. Probar bloqueo ante un requisito esencial sin resolver o aplicabilidad incierta. Comprobar separación de autoría, vencimiento y revocación concurrente, y ausencia de permisos implícitos entre circuitos.
- En PostgreSQL aislado con `app_user`, verificar RLS, inmutabilidad, precedencia, concurrencia e idempotencia. En Chromium, verificar consulta, teclado, foco, ventana estrecha y recuperación sin duplicados. Completar un recorrido conectado con datos ficticios.

El usuario aprobó el catálogo, el registro de versiones con base pendiente y la separación de autoría para todos los resultados. El primer paso de implementación es asignar identificadores estables a los criterios y vincular los hallazgos de los evaluadores existentes antes de habilitar Favorable.

## Implementación local del catálogo y del registro

El catálogo `cumpleia.base_fundamento.v1` reutiliza los seis evaluadores documentales sobre el alcance guardado. Conserva código y campo de cada hallazgo, el identificador del criterio cuando existe y la aplicabilidad informada. Los hallazgos sin correspondencia se conservan como sin clasificar. Los pendientes FORM-R01 a FORM-R05 se informan por separado. El servicio no decide todavía si una resolución aportada durante la revisión permite emitir Favorable.

La migración `bf5d10a26c41` crea la serie de versiones de Base y fundamento por evaluación, con RLS, claves de ámbito e inmutabilidad. La API implementa vista previa, registro, historial, detalle y recuperación de solicitudes. `annex_ids` indica la selección explícita en vista previa y registro. Cada respaldo seleccionado conserva ID, revisión, número de versión y SHA-256 del archivo. La huella del origen incorpora el sello de actualización del borrador para rechazar vistas previas obsoletas. Los bloqueos se toman en orden solicitud → serie para registrar y solo serie para la vista previa.

La migración se aplicó en PostgreSQL aislado. Próximo paso. Incorporar las facultades de revisión, la persistencia de conclusiones y la validación de resoluciones por requisito sobre una versión exacta.


## Implementación local de las revisiones

La migración `d51ba5e1a702` crea facultades y revisiones específicas de Base y fundamento, con RLS, historial inmutable y validación transaccional de la facultad, la autoría y la secuencia. La API permite consultar el estado, otorgar y revocar, registrar conclusiones y recuperar el recibo de una solicitud. La secuencia de una revisión es propia de la versión consultada.

`favorable_requirements` indica los bloqueos y las resoluciones admitidas para la versión exacta. `can_favorable` indica que la versión carece de bloqueos que exijan modificar el contenido, pero el registro exige aportar todas las resoluciones indicadas. El respaldo equivalente solo resuelve hallazgos de acreditación documental. No aplica exige una condición que el evaluador ya identifica como no aplicable y su justificación. Las observaciones con responsable y fecha se conservan por separado y no levantan bloqueos. El formulario de revisión deberá mostrar esas diferencias.

Validación dirigida con `app_user` en PostgreSQL aislado. 79 pruebas aprobadas y una exclusión histórica de reversión de infancia. Se probó la aceptación de un Favorable con respaldo equivalente, dos condiciones no aplicables justificadas y una observación, además de facultad independiente, bloqueo de autorrevisión, revocación concurrente, aislamiento e idempotencia. Migración aplicada solo a la base de pruebas. La interfaz se describe en la sección siguiente.


## Interfaz y recorrido conectado

En Base y fundamento se prepara el registro con los anexos seleccionados y se consulta una vista previa del contenido guardado. Documentos guardados → Evaluación de licitud guardada ofrece la lista de versiones y, para cada versión, el contenido conservado, el diagnóstico, el historial de revisiones y la administración de facultades según permiso. Los formularios mantienen los campos ante conflicto y permiten consultar el recibo de una solicitud incierta.

Las migraciones `bf5d10a26c41` y `d51ba5e1a702` se aplicaron en desarrollo local. Se verificaron RLS y la conservación de los registros anteriores. Recorrido en CumpleIA Demo con datos ficticios:

1. Como A, guarda una propuesta con base pendiente en una evaluación de ensayo. Prepara y registra su versión. Comprueba que Consentimiento y LIA, si están guardados, aparecen como antecedentes.
2. Abre la versión desde Evaluación de licitud guardada. Verifica el bloqueo de autorrevisión y otorga a B la facultad de revisión de Base y fundamento. Como B, comprueba el bloqueo de Favorable en la versión pendiente y registra Requiere cambios.
3. Como A, guarda una base definida y registra una versión nueva. Como B, revisa el diagnóstico conservado. Para ensayar Favorable, resuelve los requisitos aplicables con respaldo equivalente o No aplica justificado donde se ofrezcan esas vías. Registra una observación menor con responsable y plazo.
4. Comprueba que cada versión conserva su historial. Como A, revoca la facultad y verifica como B que la consulta histórica sigue disponible y el registro queda bloqueado.
