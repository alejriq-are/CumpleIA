# 5C.2 · Decisión de la organización sobre una versión EIPD

Estado propuesto para validación funcional. Base de trabajo `c711141`. Este contrato desarrolla el [circuito común 5A](circuito-documental-comun.md) y utiliza las revisiones registradas en [5C.1](eipd-revision-5c1.md).

## Alcance y recorrido

Desde **Documentos guardados → Versiones EIPD → Consultar versión EIPD**, incorporar **Decisión de la organización** junto a **Revisiones y facultades**. La consulta identifica el número, la referencia de la versión y su última revisión. Permite consultar decisiones y facultades, ver por qué se bloquea una acción y, con autorización, registrar una decisión o administrar facultades de decisión.

La decisión es documental. Su registro no confirma ni activa la EIPD. La adopción de Base y fundamento corresponde a 5D. El borrador, el circuito de infancia y la revisión 5C.1 conservan sus reglas.

## Facultades

- Propuesta para el piloto. Una persona administradora habilitada puede otorgar o revocar a otra persona miembro una facultad expresa de decisión sobre EIPD general en la organización, tratamiento y evaluación exactos. El cargo de administrador, propietario o DPD y la facultad de revisión no habilitan una decisión.
- Cada evento conserva destinatario, actor, fecha UTC, motivo, respaldo y secuencia. El otorgamiento admite vencimiento. La revocación impide actos nuevos y conserva tanto la actuación anterior como la facultad utilizada.
- Propuesta de separación. Quien registró la versión no decide sobre ella. Una persona que también revisó esa versión solo puede decidir cuando su facultad independiente documenta expresamente la compatibilidad de funciones y su fundamento. Si falta esa constancia, se requiere otra persona decisora.

## Resultados y reconsideración

| Resultado | Requisitos particulares |
| --- | --- |
| **Acepta** | Última revisión **Favorable** sobre esa misma versión, requisitos documentales conservados completos y correspondencia material vigente. Una revisión posterior **Requiere cambios** o **No continuar** bloquea una nueva aceptación. |
| **Requiere cambios** | Puede registrarse sobre una versión incompleta o sin revisión favorable. El evento registra la última revisión consultada, o su ausencia. |
| **Rechaza** | Puede registrarse sobre una versión incompleta o sin revisión favorable. El evento registra la última revisión consultada, o su ausencia. |

Toda decisión exige facultad vigente, versión exacta, fundamento, referencia del acta y declaración de datos ficticios en el piloto. Una reconsideración motivada enlaza la última decisión esperada de la misma versión y aplica los requisitos del resultado solicitado. La versión sucesora inicia su propio historial. Una revisión posterior, un cambio material o una revocación se muestran junto a la decisión histórica y no la reescriben.

Para **Acepta**, el servidor comprueba el diagnóstico conservado y compara el alcance adoptado, la determinación, la política y las identidades de los respaldos incorporados con su contexto aplicable. Una edición del borrador, una fecha de actualización o la mera existencia de otro respaldo no sustituyen los antecedentes incorporados. Si el RAT presenta una diferencia material pendiente de adoptar, o la correspondencia es incierta, se bloquea la aceptación con un motivo explícito. La implementación debe fijar y probar la proyección de campos materiales antes de habilitar la escritura.

## Contrato técnico propuesto

Usar una migración nueva con eventos de decisión y de facultad de decisión separados. Claves compuestas por tenant y expediente, con referencias a versión, revisión, decisión previa y facultad utilizadas, según corresponda. Historial inmutable, RLS y guardas de escritura verificadas con `app_user`. Validar JWT, membresía, expediente y capacidades en servidor para toda lectura o escritura.

Rutas propuestas bajo `.../eipd-versions/v1`:

| Método y ruta | Contrato |
| --- | --- |
| `GET /{version_id}/decision-state` | Identidad de versión, última revisión y decisión, historial, facultad vigente y acciones habilitadas con motivos por resultado. |
| `POST /{version_id}/decisions` | `request_id`, `expected_revision_id`, `expected_decision_id`, `expected_authority_id`, resultado, fundamento, referencia del acta y declaración del piloto. Los dos primeros precedentes pueden ser nulos cuando no hay antecedente. |
| `GET /{version_id}/decision-requests/{request_id}` | Recuperar el resultado de una solicitud propia tras una respuesta incierta. |
| `GET /decision-authorities/history` | Consultar las actuaciones del expediente y su vigencia. |
| `POST /decision-authorities` | Destinatario, actuación, secuencia esperada, motivo, respaldo, vencimiento opcional y constancia de compatibilidad cuando corresponda. |

DTO cerrados y versionados. El servidor asigna secuencia, fecha y actor. La idempotencia se delimita por organización, actor y solicitud de decisión. La misma solicitud con material idéntico recupera el acto original tras verificar el permiso de lectura. Reutilizarla con otro material produce conflicto.

La transacción vuelve a comprobar la revisión, la decisión y la facultad esperadas, además de la correspondencia cuando el resultado sea **Acepta**. Reusar la serie que coordina 5B y 5C.1 para serializar revisión, decisión y revocación. Si se requiere el selector global de política, se toma antes de la serie. Documentar el orden completo con el bloqueo de solicitud antes de introducir escrituras. Ante cambios concurrentes, responder 409 y requerir consulta explícita antes de reenviar. Ante requisitos insuficientes, responder 422 con motivo. Los campos se conservan temporalmente en la pestaña.

## Validación para el cierre

- Con PostgreSQL aislado y `app_user`, comprobar pertenencia, RLS, inmutabilidad, separación de autoría, doble función con y sin constancia, y revocación o vencimiento de la facultad.
- Probar una aceptación persistida con revisión favorable vigente. Probar rechazo de aceptación cuando falta esa revisión, la última revisión cambia, hay faltantes o el contexto difiere. Probar las dos decisiones restantes sin revisión favorable.
- Probar carrera entre decisión y revocación, revisión y decisión, reconsideraciones concurrentes y recuperación idempotente. Comprobar que las decisiones anteriores se consultan y que la sucesora parte sin actuaciones.
- En Chromium, comprobar navegación con teclado, foco, ventana estrecha, conservación de campos ante conflicto y recuperación de una respuesta incierta. Completar un recorrido conectado con datos ficticios y verificar que confirmación y activación siguen bloqueadas.

Antes de implementar, validar las propuestas sobre quién administra facultades, separación de autoría y compatibilidad de la doble función. El recorrido 5C.1 sobre la versión 8 comprobó la disponibilidad de **Favorable**. Para ensayar **Acepta** se necesita además una revisión Favorable efectivamente registrada.
