# 5D.2 · Decisión de la organización sobre Base y fundamento

Contrato funcional aprobado por el usuario el 08/11/2026. Servidor e interfaz implementados localmente. Validación en PostgreSQL aislado completada. Recorrido principal confirmado en CumpleIA Demo el 12/11/2026. Continúa el [contrato 5D.1](base-fundamento-5d1.md) y desarrolla [LIC-GOV-001](revision-aceptacion-base-licitud.md). Sigue el [precedente de decisión de EIPD](eipd-decision-5c2.md) con reglas de correspondencia propias de Base y fundamento.

## Actuaciones y facultades

Una persona administradora habilitada puede otorgar o revocar a otra persona miembro una facultad expresa de **decisión de Base y fundamento** para la organización, el tratamiento y la evaluación exactos. El historial registra destinatario, actor, motivo, respaldo, secuencia, fecha y vencimiento opcional. La facultad es independiente de las de revisión de Base y fundamento, EIPD general e infancia. El rol organizacional o el cargo de DPD por sí solos carecen de efecto sobre esta autorización.

Quien registró la versión queda excluido de decidir sobre ella para cualquiera de los tres resultados. Si la persona decisora emitió alguna revisión de esa versión, su facultad de decisión debe incluir una constancia expresa y fundamentada de compatibilidad de funciones. Sin esa constancia se requiere otra persona decisora.

| Resultado | Requisitos específicos |
| --- | --- |
| **Acepta** | Base definida, última revisión registrada **Favorable** de esa misma versión, requisitos esenciales resueltos conforme a 5D.1 y correspondencia material vigente. |
| **Requiere cambios** | Identificar qué falta corregir o aclarar. Disponible también para una versión incompleta, histórica o con base pendiente. |
| **Rechaza** | Explicar el motivo del rechazo documental. Disponible también para una versión incompleta, histórica o con base pendiente. |

Toda decisión exige facultad vigente, fundamento, referencia del acta y declaración de datos ficticios. La decisión conserva la identidad de la versión, la revisión consultada si existe, la facultad utilizada, el actor, la fecha UTC y su precedente. Una reconsideración agrega un evento y aplica los requisitos del resultado elegido.

Se conservan las resoluciones verificables de la revisión Favorable, incluidos **No aplica** justificado y respaldo equivalente. Las observaciones menores documentadas pueden coexistir con Acepta. Los pendientes de cobertura del piloto siguen visibles. **Acepta** registra una decisión documental para la versión exacta. La confirmación y la activación EIPD permanecen bloqueadas.

## Correspondencia para Acepta

El servidor compara una proyección canónica del material conservado con la evaluación guardada y el RAT actual. La huella de registro de 5D.1 incluye datos de actualización útiles para detectar vistas previas obsoletas. La comprobación de 5D.2 usa la igualdad del contenido pertinente.

| Componente | Regla propuesta |
| --- | --- |
| Evaluación | Exigir la misma evaluación dentro de su serie y comprobar que sigue siendo la evaluación de trabajo vigente. Un ciclo sucesor exige sus propias actuaciones. |
| Base, fundamento y formulario principal | Comparar la base seleccionada, el fundamento y el contenido canónico completo del formulario principal. Cualquier diferencia bloquea Acepta y exige registrar y revisar una nueva versión para aceptar el contenido cambiado. |
| Finalidad y alcance RAT | Comparar la finalidad y el alcance adoptados con los conservados. Verificar además que el alcance adoptado corresponda al RAT vigente, aunque la evaluación todavía conserve el alcance anterior. |
| Respaldos incorporados | Verificar cada respaldo seleccionado por ID, revisión, versión y huella. La pérdida de disponibilidad o una diferencia en un respaldo incorporado bloquea Acepta. Un nuevo anexo ajeno a la selección no altera por sí solo el paquete. |
| Antecedentes alternativos | Consentimiento o LIA guardados como alternativas siguen visibles en la copia histórica. Sus ediciones por sí solas quedan fuera de la comparación mientras no cambien la base ni el formulario principal. |
| Metadatos | Fecha de guardado, motivo del registro y otros metadatos de presentación quedan fuera de la igualdad material. El diagnóstico se interpreta con la cobertura y las reglas conservadas en 5D.1. |

Una versión anterior del mismo ciclo puede recibir una decisión sobre su contenido exacto. Para Acepta debe cumplir las mismas reglas de correspondencia y revisión, incluso si hay una sucesora registrada. Cada sucesora inicia su propio historial. Una revisión posterior, un cambio material o la revocación de una facultad se muestran junto a la decisión histórica con su efecto actual y preservan el acto registrado.

## Interfaz y contrato técnico

En **Documentos guardados → Evaluación de licitud guardada → versión de Base y fundamento**, incorporar **Decisión de la organización** junto a la revisión y al acceso único **Consultar evaluación de licitud**. Mostrar versión, revisión vinculada, historial, motivos de bloqueo por resultado y administración de facultades según permiso. Para una versión que ya no corresponde, ofrecer volver al editor y preparar una sucesora cuando proceda. Mantener campos locales ante conflicto y señalar qué se debe consultar de nuevo.

Rutas propuestas bajo el prefijo de versiones de Base y fundamento de 5D.1.

| Operación | Ruta |
| --- | --- |
| Consultar estado y decisiones | `GET /{version_id}/decision-state` |
| Registrar decisión o reconsideración | `POST /{version_id}/decisions` |
| Recuperar un resultado incierto | `GET /{version_id}/decision-requests/{request_id}` |
| Consultar o administrar facultades | `GET /decision-authorities/history`, `POST /decision-authorities` |

Persistir eventos de decisión y facultad en tablas propias de solo adición, con RLS y claves de ámbito. La escritura recibe el identificador de solicitud, la facultad consultada y los precedentes esperados de revisión y decisión. Resolver primero la repetición idempotente con la misma entrada. Una entrada distinta con el mismo identificador produce conflicto. Una escritura nueva verifica en la transacción membresía, autoría, compatibilidad, vigencia, precedentes y, para Acepta, correspondencia actual. Estabilizar las lecturas frente a escritores de la serie, del RAT y de respaldos. Ante una respuesta incierta, consultar el recibo antes de reenviar.

## Validación

- Probar los tres resultados, incluido Acepta tras una revisión Favorable con respaldo equivalente y No aplica justificado. Verificar bloqueos por base pendiente, ausencia de Favorable y revisión posterior incompatible.
- Probar edición de base, fundamento, formulario principal, finalidad y alcance RAT, cambio de ciclo y pérdida de un respaldo incluido. Verificar que un guardado materialmente idéntico, una edición de un antecedente alternativo o un anexo ajeno a la selección no bloqueen por sí solos.
- Probar autoría, separación de facultades, doble función con y sin compatibilidad, vencimiento, revocación, aislamiento por organización e inmutabilidad. Probar concurrencia con edición material, cambio de revisión o revocación, y recuperación sin duplicados.
- En Chromium, comprobar acceso por teclado, foco, ventana estrecha, mensajes y conservación de campos. En CumpleIA Demo, usar la versión 2 Favorable para ensayar una facultad de decisión independiente. Si decide B, documentar compatibilidad aunque su facultad de revisión esté revocada. Confirmar que la versión 1 con base pendiente bloquea Acepta y que una sucesora empieza sin decisiones.

## Estado de implementación

La migración `e7638d2c904a` incorpora el historial de decisiones y sus facultades con aislamiento por organización. La API comprueba la revisión precedente, la facultad y la correspondencia material. El panel **Decisión de la organización** se abre desde la versión consultada y permite recuperar un envío incierto por su identificador.

Pasaron 14 pruebas dirigidas en Chromium con respuestas controladas, TypeScript, ESLint, Prettier, Ruff y Black. Alembic generó el SQL de la migración y pytest detectó la prueba de integración. La migración se aplicó en PostgreSQL aislado y pasó la prueba de integración con `app_user`. La prueba verificó el bloqueo previo a Favorable, el registro de Acepta, el bloqueo tras cambiar el fundamento y la recuperación idempotente de la decisión histórica. La migración también se aplicó en desarrollo local, con RLS habilitado en ambas tablas nuevas y cinco rutas de decisión servidas por la API.

## Recorrido en CumpleIA Demo

- A consultó la versión 2 y comprobó el bloqueo por autoría. Otorgó a B la facultad independiente de decisión con una constancia de compatibilidad.
- B registró la decisión n.º 1 **Acepta** en la versión 2. El historial mostró el acta ficticia, la revisión vinculada y la facultad utilizada.
- La versión 1 conservó su historial de decisiones vacío y mostró **Acepta** deshabilitado porque su última revisión era **Requiere cambios**.
- A revocó la facultad de decisión. B siguió consultando la decisión n.º 1 de la versión 2 y el sistema bloqueó nuevas decisiones por falta de facultad vigente.

Durante el recorrido se añadió el identificador de quien consulta y se corrigieron las claves duplicadas de los paneles de revisión y decisión. Pasaron las tres pruebas de navegador de Base y fundamento después de la corrección. El bloqueo tras cambiar el fundamento se verificó en PostgreSQL aislado.
