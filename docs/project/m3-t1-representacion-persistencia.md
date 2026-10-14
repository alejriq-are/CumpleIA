# M3-T1 — Integracion persistente de representacion sensible

Estado: plan tecnico de implementacion, 2026-10-14 (§240).
No migracion aplicada, campo API expuesto o ruta de confirmacion habilitada.
Contratos/binding/evaluador puros existentes: §§237–239.

## Almacenamiento y compatibilidad

Nueva columna nullable sensitive_representation_assessment en legal_assessments,
JSONB(none_as_null=True), con envoltorio BoundSensitiveRepresentationV1. Migracion
nueva tras head vigente, nunca editar anteriores. Filas existentes quedan SQL NULL,
sin backfill ni reconstruccion de documentos. Declarar constraint de objeto y
alinearla con metadata ORM para evitar drift. Mantener RLS y privilegios actuales
con pruebas explicitas de la columna bajo app_user.

Primera etapa: expediente con este material no puede pasar a confirmado. Proponer
constraint especifica que impida status confirmado cuando columna no sea NULL;
comprobar transiciones/historicos antes de aplicarla. No sustituye evaluacion de
consentimiento sensible ni permite eludir bloqueos retirando el campo.

## Contratos API y dependencias

Crear/editar reciben SensitiveRepresentationAssessmentV1 sin binding. Salida recibe
BoundSensitiveRepresentationV1 o null. Nunca aceptar envelope/actor/hash del cliente.
Los contratos actualmente importan tipos comunes desde licitud: evitar import circular
moviendo definiciones al modulo central y conservando facade de reexportacion, como
research, o extrayendo comunes sin alterar tipos/hashes. Verificar importaciones y
schemas antes de conectar endpoints.

No exponer el campo en API hasta integrar modelo, migracion y servicio: el bucle
setattr actual no debe aceptar un atributo no persistente que luego desaparezca.

## Creacion y edicion

Creacion: en create_legal_assessment_draft_v1, asignar assessment.id de servidor
antes de construir el contexto; bind tras fijar bundle RAT, base y consentimientos.
Reutilizar el lock de serie y gestion de transaccion existentes.

Edicion: en update_legal_assessment_draft_v1, detectar model_fields_set y extraer
el documento antes del bucle setattr. Tras lock de serie/relectura de borrador,
aplicar cambios y recomponer RAT; solo entonces bind del reaporte explicito.

| Operacion | Tratamiento del material |
| --- | --- |
| Campo omitido | Conservar envelope/hash originales; nunca rebind automatico |
| Campo null explicito | Retirar documento solo de borrador; consentimiento representado conserva bloqueo |
| Documento reaportado | Nuevo binding con contexto actual y UUID de servidor |
| Cambio base/consentimiento/scope/RAT sin reaporte | Conservar documento y diagnosticar obsolescencia |
| Lectura de confirmado/reemplazado | Identidad guardada tal cual; no migracion semantica en lectura |
| Edicion historica | Rechazo existente, sin cambio parcial de otros campos |
| Error posterior al binding | Rollback total, sin documento/serie parcial |

## Diagnostico y barreras concurrentes

Readiness incorpora bloque separado y versionado de representacion; incluir result,
issues y can_confirm=false. No convertir completo documental en aprobacion de
facultades. Identidades/analisis libres no se interpretan como autenticidad ni estado
de revocacion. Toda representacion mantiene gate conservador durante esta entrega,
aunque el documento este completo. Cambios de otros regimenes conservan evaluadores
propios; este bloque no satisface salud, biometria, infancia/investigacion o EIPD.

No modificar los hashes/contextos especiales o de investigacion historicos para
incorporar el nuevo campo. Si ya existe una revision EIPD, sus metadatos antiguos
no incluyen representacion: no presentar su vinculo como cobertura del nuevo material.
Hasta diseñar contexto EIPD sucesor, suprimir diagnostico de vigencia global para
expedientes con representacion e informar cobertura de representacion pendiente;
consulta historica conserva evento sin inferencias. Rechazar nueva escritura de
revision EIPD con representacion presente mediante motivo explicito de asociacion
pendiente, para no crear un evento que parezca cubrir material no incluido en su hash.

## Matriz de pruebas antes de conectar

- API crear/leer parcial y completo ficticios, identidad UUID derivada en servidor.
- Entrada extra/binding/hash rechazados y ningun dato parcial persistido.
- PATCH omitido/null/reaporte con verificaciones de JSON y hashes tras commit.
- Cambios de contexto invalidan asociacion; historicos y eventos previos inmutables.
- Tenant ajeno, tratamiento/evaluacion equivocados, viewer/edit/suscripcion.
- Confirmacion rechazada con documento completo; retiro no desbloquea representante.
- Escritura SQL con app_user: RLS y constraint de no confirmado comprobados.
- Concurrencia edicion/confirmacion/reaporte: relectura de borrador y atomicidad.
- Readiness no infiere vigencia EIPD de un contexto que no cubre representacion.
- Upgrade de base aislada desde head previo y metadata/alembic check coherentes.

## Ejecucion en pasos coherentes

1. Reorganizar tipos e integrar contratos con rechazo de campos de servidor; sin
   activar rutas ni añadir entradas silenciosamente ignoradas.
2. Implementar migracion/modelo/CRUD como conjunto coherente, con base aislada y
   pruebas de aislamiento/historia. Coordinar actualizacion del head fijo del runner
   solo despues de comprobar upgrade; no cambiarlo para aceptar una base desconocida.
3. Integrar diagnostico/gates/limite de cobertura EIPD y pruebas transversales.
4. Validar despliegue local de migracion junto a codigo; sin aplicar cambios al
   expediente ficticio operativo ni sembrar datos reales automaticamente.

Pruebas ficticias hasta MVP. Implementacion de persistencia no acredita fuentes,
facultades reales o aceptacion juridica. M3-T1 sigue EN PROGRESO.
