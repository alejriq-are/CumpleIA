# 5B.1 — Registro de versiones documentales EIPD general

LIC-DOC-001 · 02/11/2026 · rama `feature/eipd-versiones-5b1` · base `a5a51c3e3bc5a6f9ac73195b4c7553979c7ab884`.

## Alcance y estado

Implementación local del servidor y migración aditiva `b95e7f3d1204`, posterior a `a84f6e2c9103`. No incorpora controles nuevos en pantalla. La migración se aplica únicamente a la base aislada de pruebas en esta entrega; no se ha aplicado a la base de desarrollo utilizada por el usuario ni a producción.

El borrador EIPD existente continúa siendo editable. El registro explícito agrega una fotografía inmutable, numerada por evaluación y tipo EIPD general; editar después el borrador no modifica esa fotografía. No se reutiliza el número de evaluación como número documental. Una nueva versión conserva el identificador de la versión documental anterior.

Se permite registrar material incompleto con su diagnóstico. Esto no expresa revisión favorable, aceptación, confirmación ni activación. Las actuaciones y facultades de revisión y decisión se implementarán en 5C. No cambia retroactivamente el circuito de infancia. Las reglas V1–V3 aprobadas están en [el contrato común](circuito-documental-comun.md).

## Contrato de API v1

Prefijo: `/licitud/treatments/{treatment_id}/assessments/{assessment_id}/eipd-versions/v1`.

Todas las rutas requieren sesión, organización autorizada mediante `X-Organization-Id` y suscripción habilitada.

| Método y sufijo | Función |
| --- | --- |
| GET `/preview` | Construye el paquete desde el borrador guardado y devuelve huella de origen y último número registrado; no escribe |
| POST (sin sufijo) | Registra una versión con comprobación del origen y del último número esperado |
| GET (sin sufijo) | Consulta metadatos del historial de esa evaluación |
| GET `/{version_id}` | Consulta el contenido exacto registrado y comprueba su integridad |
| GET `/requests/{request_id}` | Recupera el registro de la solicitud de la persona autenticada en esa evaluación |

El POST admite exclusivamente `request_id` (UUID), `data_kind: ficticios`, `expected_source_hash`, `expected_latest_version` y `reason` no vacío (máximo 4.000 caracteres). Rechaza propiedades adicionales. No acepta del cliente contenido documental, autor, fecha, número asignado ni autorización para activar.

Registrar exige membresía efectiva de edición (`editor`, `admin` u `owner`) y permiso diferenciado `register_document`. El rol lector consulta, pero no registra. Ser administrador de plataforma sin membresía efectiva no concede registro. Este permiso no otorga revisión ni aceptación. El registro y su vista previa se limitan a desarrollo/pruebas.

Antes de registrar deben existir un borrador EIPD guardado y editable, alcance RAT vigente, determinación guardada y vigente «EIPD: Corresponde» y política EIPD seleccionada y verificable. Los faltantes documentales no se convierten en aprobación ni impiden conservar un antecedente incompleto.

## Material conservado y procedencia

El paquete incluye versión de esquema, tipo documental, evaluación guardada con su contenido EIPD, alcance adoptado, determinación e historial consultados, metadatos y contenido estructurado de registros de soporte, política seleccionada y diagnóstico determinista utilizado. El registro agrega autor autenticado, fecha UTC, número, motivo y predecesor. Se conservan huellas SHA-256 calculadas por servidor sobre JSON canónico versionado.

Los soportes son un manifiesto del historial consultado de esa evaluación: identificador, tipo, revisión, huella, autor, fecha y payload. No incluye los archivos binarios. Incluir un soporte histórico no lo declara vigente ni lo convierte en evidencia eficaz. No se deducen vínculos desde referencias libres. En 5B.2 deberá mostrarse este manifiesto antes de registrar y evitar atribuir actualidad a una valoración histórica. La selección manual de un subconjunto de soportes no está implementada en 5B.1.

La vista previa de registro del servidor es distinta de la vista previa existente de ediciones pendientes del navegador. El servidor solo conoce lo guardado. 5B.2 debe exigir guardar primero los cambios locales y presentar el origen exacto; abrir la vista previa no registra nada.

## Concurrencia y recuperación

La huella de origen incluye la fecha de actualización de la evaluación: modificar y restaurar el texto tampoco permite reutilizar una vista previa anterior. El registro compara esa huella y el último número documental esperado; si cambiaron responde 409 y exige consultar de nuevo.

Orden de bloqueos retenidos hasta finalizar la transacción: selector global de política, solicitud por organización/persona/UUID y serie de evaluación. El bloqueo de solicitud también cubre solicitudes simultáneas entre evaluaciones distintas.

Repetir la misma solicitud con el mismo contenido devuelve el registro original, incluso si después se editó el borrador. Reutilizar su UUID con otro contenido o evaluación responde 409. Dos solicitudes distintas sobre el mismo origen y número esperado producen un registro y un conflicto. Después de una respuesta incierta se consulta la solicitud original o se reintenta con el mismo UUID; no se genera otro automáticamente.

## Persistencia y seguridad

La tabla `eipd_document_versions` tiene relación compuesta con organización/tratamiento/evaluación, unicidad de número por evaluación y unicidad de solicitud por organización/persona. RLS filtra la lectura y comprueba organización, actor real, membresía, suscripción y estado del padre al insertar. El runtime `app_user` no puede actualizar, borrar ni truncar el historial. Un trigger bloquea actualizaciones también administrativas. El borrado administrativo queda reservado a limpieza explícita de fixtures aisladas; no existe endpoint de eliminación ni se afirma resistencia frente al dueño de la base.

La migración no elimina antecedentes y su downgrade destructivo está bloqueado. No modifica contratos de infancia. La API conserva `can_confirm: false` y activación deshabilitada.

## Verificación y continuidad

Ejecución dirigida en PostgreSQL aislado, con runtime real `app_user` sin bypass de RLS. **191 pruebas aprobadas** en la ejecución final (registro, aplicabilidad, API de licitud, seguridad del runner y concurrencia entre series), en 206,55 segundos. Ruff, Black y `git diff --check` aprobados para los cambios del bloque.

Comando desde `backend`: `PYTHONPATH=. ../.venv/bin/python scripts/run_general_eipd_version_tests.py`. El runner valida el destino fijo aislado, rol, separación de conexiones y estado antes de migrar. No acepta argumentos para apuntar a otra base. No usar pytest directamente con la configuración operacional.

Comprobaciones: registro incompleto, edición posterior con fotografía conservada, nueva versión/predecesor, solicitudes repetidas y concurrentes, rechazo de contenido adicional, determinación no aplicable, lectura entre organizaciones y denegación de modificaciones del historial. No acredita pruebas manuales de una interfaz aún inexistente.

Siguientes pasos:

1. Commit y push de 5B.1 autorizados por el usuario el 02/11/2026 en `feature/eipd-versiones-5b1`; esta publicación no aplica la migración operacional ni acredita validación de interfaz.
2. 5B.2: integrar vista previa de registro, motivo, historial, detalle, recuperación de solicitud y preparación de sucesora; mantener separados los pendientes de cada pestaña y los soportes históricos.
3. Aplicar la migración al entorno de desarrollo verificado antes del recorrido conectado de 5B.2; no se aplica por esta documentación.
4. Validar conjuntamente el recorrido completo. Mantener 5C, 5D y FORM-R01 a FORM-R05 abiertos.

Sin merge ni despliegue. Cambios preexistentes de `frontend/next-env.d.ts` y `outputs/` excluidos.


## Nombres visibles actualizados — 05/11/2026

En la interfaz, la anterior «versión de evaluación» se presenta como **Evaluación n.º N**. Las copias inmutables se denominan **Versión del documento EIPD** o **Versión EIPD**, y sus actuaciones siguen llamándose **Revisión**. No cambia este contrato de persistencia ni la numeración. Véase [Terminología de la interfaz](circuito-documental-comun.md#terminología-de-la-interfaz--05112026).
