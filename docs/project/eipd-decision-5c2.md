# 5C.2 · Decisión de la organización sobre una versión EIPD

Reglas de facultades y separación de funciones aprobadas por el usuario. Persistencia, API e interfaz implementadas localmente. Recorrido conectado verificado en CumpleIA Demo. Base de trabajo `c711141`. Este contrato desarrolla el [circuito común 5A](circuito-documental-comun.md) y utiliza las revisiones registradas en [5C.1](eipd-revision-5c1.md).

## Alcance y recorrido

Desde **Documentos guardados → Versiones EIPD → Consultar versión EIPD**, incorporar **Decisión de la organización** junto a **Revisiones y facultades**. La consulta identifica el número, la referencia de la versión y su última revisión. Permite consultar decisiones y facultades, ver por qué se bloquea una acción y, con autorización, registrar una decisión o administrar facultades de decisión.

La decisión es documental. Su registro no confirma ni activa la EIPD. La adopción de Base y fundamento corresponde a 5D. El borrador, el circuito de infancia y la revisión 5C.1 conservan sus reglas.

## Facultades

- Una persona administradora habilitada puede otorgar o revocar a otra persona miembro una facultad expresa de decisión sobre EIPD general en la organización, tratamiento y evaluación exactos. El cargo de administrador, propietario o DPD y la facultad de revisión no habilitan una decisión.
- Cada evento conserva destinatario, actor, fecha UTC, motivo, respaldo y secuencia. El otorgamiento admite vencimiento. La revocación impide actos nuevos y conserva tanto la actuación anterior como la facultad utilizada.
- Quien registró la versión no decide sobre ella. Una persona que también revisó esa versión solo puede decidir cuando su facultad independiente documenta expresamente la compatibilidad de funciones y su fundamento. Si falta esa constancia, se requiere otra persona decisora.

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

Rutas bajo `.../eipd-versions/v1`:

| Método y ruta | Contrato |
| --- | --- |
| `GET /{version_id}/decision-state` | Identidad de versión, última revisión y decisión, historial, facultad vigente y acciones habilitadas con motivos por resultado. |
| `POST /{version_id}/decisions` | `request_id`, `expected_review_id`, `expected_decision_id`, `expected_authority_id`, resultado, fundamento, referencia del acta y declaración del piloto. Los dos primeros precedentes pueden ser nulos cuando no hay antecedente. |
| `GET /{version_id}/decision-requests/{request_id}` | Recuperar el resultado de una solicitud propia tras una respuesta incierta. |
| `GET /decision-authorities/history` | Consultar las actuaciones del expediente y su vigencia. |
| `POST /decision-authorities` | Destinatario, actuación, secuencia esperada, motivo, respaldo, vencimiento opcional y constancia de compatibilidad cuando corresponda. |

DTO cerrados y versionados. El servidor asigna secuencia, fecha y actor. La idempotencia se delimita por organización, actor y solicitud de decisión. La misma solicitud con material idéntico recupera el acto original tras verificar el permiso de lectura. Reutilizarla con otro material produce conflicto.

La transacción vuelve a comprobar la revisión, la decisión y la facultad esperadas, además de la correspondencia cuando el resultado sea **Acepta**. Reusar la serie que coordina 5B y 5C.1 para serializar revisión, decisión y revocación. Si se requiere el selector global de política, se toma antes de la serie. Documentar el orden completo con el bloqueo de solicitud antes de introducir escrituras. Ante cambios concurrentes, responder 409 y requerir consulta explícita antes de reenviar. Ante requisitos insuficientes, responder 422 con motivo. Los campos se conservan temporalmente en la pestaña.

## Correspondencia y concurrencia antes de habilitar Acepta

La huella de registro de 5B protege una operación contra cambios del borrador e incluye `updated_at`. La comprobación de 5C.2 usa la siguiente proyección semántica. La identidad, la huella de integridad y el diagnóstico de la versión se validan primero con los servicios de 5B y 5C.1.

| Material | Comparación propuesta |
| --- | --- |
| Alcance | Comparar la finalidad y la huella canónica `rat_context_hash` conservadas con las de la evaluación. Reutilizar `rat_context_current` del diagnóstico de Licitud para detectar diferencias materiales del inventario pendientes de adoptar. La instantánea de presentación puede contener campos ajenos a la huella semántica. |
| Aplicabilidad | Exigir una determinación vigente de EIPD general en estado Corresponde y comparar su alcance asociado, estado y fundamento con los conservados. El historial de determinaciones y los campos de infancia quedan fuera de esta comparación. |
| Política | Comparar la identidad y huella de la política EIPD activa con la conservada. Política ausente, incompatible o cambiada bloquea Acepta. |
| Respaldos | Validar los respaldos efectivamente incorporados por identidad, revisión y huella. Un respaldo nuevo que la versión no incorporó queda fuera de esta comprobación. |
| Borrador | Usar el contenido documental y los requisitos conservados. Los campos editados después del registro, el nombre de presentación y las fechas de guardado quedan fuera de esta comprobación. |

La comparación de aplicabilidad admite volver a guardar una determinación materialmente idéntica. Una versión anterior sigue siendo consultable. Su posibilidad de recibir una nueva aceptación depende de la misma verificación de correspondencia y de la última revisión de esa versión. Para los tres resultados se comprueban los precedentes y la facultad bajo bloqueo.

Orden implementado para Acepta. Selector global de política, solicitud de decisión, bloqueo exclusivo de la serie de 5C.1 y bloqueos SHARE de las tablas RAT que alimentan la huella canónica. Para Requiere cambios y Rechaza se omite el selector global. Se comprueba el recibo idempotente antes de exigir facultad vigente para una escritura nueva.

La serie coordina aplicabilidad, respaldos, registro de versión y revisiones, pero la edición de Licitud también utiliza bloqueos de fila y el RAT tiene escritores propios. La serie serializa las escrituras de Licitud, revisiones y facultades del expediente. Para estabilizar el RAT durante la aceptación, el piloto toma bloqueos SHARE de sus tablas con NOWAIT y responde 409 si un escritor está activo. El bloqueo de tablas puede entrar en conflicto con una escritura RAT de otra organización durante esa transacción.

La revisión del código confirmó que los reemplazos de finalidades, categorías y titulares en `services/rat.py` modifican tablas de detalle y marcan el tratamiento actualizado dentro de la misma transacción. La verificación de Acepta debe probar ambos órdenes de commit, incluida una edición RAT ya iniciada al leer la correspondencia. Un cambio RAT confirmado antes de la decisión debe bloquearla si altera la proyección. Si la decisión queda confirmada primero, el cambio posterior se presenta como una diferencia de contexto de un acto histórico.

## Validación para el cierre

- Con PostgreSQL aislado y `app_user`, comprobar pertenencia, RLS, inmutabilidad, separación de autoría, doble función con y sin constancia, y revocación o vencimiento de la facultad.
- Probar una aceptación persistida con revisión favorable vigente. Probar rechazo de aceptación cuando falta esa revisión, la última revisión cambia, hay faltantes o el contexto difiere. Probar las dos decisiones restantes sin revisión favorable.
- Probar carrera entre decisión y revocación, revisión y decisión, reconsideraciones concurrentes y recuperación idempotente. Comprobar que las decisiones anteriores se consultan y que la sucesora parte sin actuaciones.
- En Chromium, comprobar navegación con teclado, foco, ventana estrecha, conservación de campos ante conflicto y recuperación de una respuesta incierta. Completar un recorrido conectado con datos ficticios y verificar que confirmación y activación siguen bloqueadas.

El usuario confirmó quién administra facultades, la separación de autoría y la condición para la doble función. El recorrido 5C.1 sobre la versión 8 comprobó la disponibilidad de **Favorable**. Para ensayar **Acepta** se necesita además una revisión Favorable efectivamente registrada.


## Implementación de servidor

La migración `a52c910be604` agrega eventos de decisión y facultad, claves de ámbito y precedencia, RLS y guardas de escritura. El disparador comprueba autoría, membresía, facultad y compatibilidad, última revisión y decisión, y los requisitos congelados para Acepta. La comparación semántica con el RAT, la determinación, la política y los respaldos vigentes se realiza en el servicio API dentro de la transacción.

La migración se aplicó en PostgreSQL aislado para las pruebas. La migración también se aplicó en la base local de desarrollo. Se conservaron 6 evaluaciones, 37 respaldos, 8 versiones y 12 revisiones. Las tablas nuevas quedaron vacías con RLS y se verificaron las cinco rutas locales. El resultado del recorrido se registra abajo.


## Interfaz y recorrido conectado

En Documentos guardados, al consultar una versión, **Decisión de la organización** abre el historial y la administración de facultades según los permisos consultados. El formulario explica el bloqueo de Acepta, conserva los campos ante un conflicto y exige volver a consultar. Ante un resultado incierto, consulta la solicitud por su identificador y ofrece reintentar con el mismo identificador si aún no figura. Los cambios pendientes bloquean volver a la lista y cambiar de versión, con acceso al formulario desde el aviso.

Recorrido en desarrollo con datos ficticios:

1. Como A, consulta la versión 8 y otorga una facultad independiente de decisión a B. Documenta la compatibilidad si B también registra la revisión.
2. Como B, comprueba que **Acepta** está bloqueado antes de tener una revisión Favorable persistida. Con facultad de revisión vigente, registra esa revisión en la versión exacta.
3. Vuelve a consultar decisiones y facultades. Si el contexto material coincide, registra **Acepta** con fundamento y referencia de acta ficticios. Vuelve a abrir la versión y verifica que figure la decisión n.º 1, vinculada a la revisión y facultad utilizadas.
4. Revoca la facultad de decisión y verifica que B conserva la consulta histórica. Comprueba que la versión 5 incompleta conserva su propio historial y que confirmación y activación siguen bloqueadas.

### Resultado observado — 07/11/2026

- A otorgó a B la facultad independiente de decisión con compatibilidad documentada. Como autor de la versión 8, A quedó bloqueado para decidir sobre ella.
- B comprobó que Acepta estaba bloqueado mientras faltaba la revisión Favorable. Registró la revisión n.º 1, referencia `SIMULADA-5C2-REVISION-001`.
- B registró Acepta n.º 1 sobre la versión 8, con referencia de acta `SIMULADA-5C2-ACTA-001`, vinculada a la revisión y a la facultad utilizadas.
- A registró la revocación n.º 3 con respaldo `SIMULADA-5C2-REVOCACION-001`. Después, B pudo consultar la decisión histórica y la interfaz exigió una facultad vigente para nuevas actuaciones.
- La versión 5 conservó sus 12 revisiones y mostró un historial de decisiones vacío. La confirmación y la activación siguieron bloqueadas en el recorrido.
