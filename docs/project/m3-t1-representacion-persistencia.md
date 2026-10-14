# M3-T1 — Integracion persistente de representacion sensible

Estado: plan tecnico de implementacion, 2026-10-14 (§240).
Storage/migracion aplicados (§242), CRUD conectado (§243) y diagnostico
readiness/interfaz integrado (§244); cobertura EIPD de representacion pendiente
y confirmacion bloqueada.
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


## 2026-10-14 — M3-T1 §241: contratos futuros sin ciclo de imports

Tipos de representacion centralizados en schemas/licitud con facade compatible en
sensitive_representation. Preparados subcontratos Create/Update/Out separados para
futura persistencia: entrada documento sin binding, salida envelope servidor, root
cerrado. API activa sigue usando clases anteriores, sin nuevo campo aceptado.
Model_fields_set distingue omitido/null/aporte; validator scope null conservado.

Comparacion antes/despues: JSON schemas de tres modelos API activos y tres modelos
de representacion identicos; hash de documento ficticio identico. No reescritura
de datos/hashes historicos. 19 pruebas nuevas de contratos futuros, mas 88 anteriores:
107 aprobadas en 0.32 s con entorno aislado verificado; Ruff/Black correctos.
No migracion, ORM/CRUD o conexion API nueva. Proximo: implementar conjunto coherente
de persistencia y gates antes de cambiar tipos usados por endpoints.
M3-T1 EN PROGRESO; pruebas ficticias hasta MVP; confirmacion/activacion bloqueadas.


## 2026-10-14 — M3-T1 §242: storage interno de representacion

Migracion nueva e41c5b8a2d90 tras d39e2b0f841c: columna JSONB nullable sin backfill,
constraint de objeto y prohibicion de status confirmado cuando material no sea NULL.
Modelo ORM alineado con SQL NULL real. RLS/privilegios previos conservados; SQL solo
exige objeto y barrera de status, no valida el contrato completo del envelope.
API del nuevo campo todavia no conectada.

Upgrade aplicado primero en base fija aislada tras verificar head anterior/roles;
runner EXPECTED_HEAD actualizado solo despues del exito e incorpora cinco suites
de representacion. 116 pruebas relacionadas aprobadas en 1.00 s: almacenamiento,
roundtrip/null, rechazo de JSON no objeto, barrera real SQL de confirmacion,
lectura/escritura propia y rechazo de tenant ajeno, contratos/binding/evaluador y
guardas runner. Dos aserciones iniciales de nombre fijo corregidas para constraints
generadas por convencion SQLAlchemy; comparacion del constraint_name real.
Alembic check aislado sin drift; Ruff/Black correctos.

Upgrade local de desarrollo aplicado despues de pruebas, con host/base/head
verificados: conteos de expedientes y registros de politica conservados, columna
nueva NULL en todos los expedientes previos. Backend health 200. No datos/documentos
operativos aportados ni politica habilitada. Downgrade definido, no ensayado.
Proximo: CRUD del documento/binding con nuevos contratos y gates, cobertura EIPD
pendiente conservada. M3-T1 EN PROGRESO; pruebas ficticias hasta MVP;
confirmacion/activacion bloqueadas.


## 2026-10-14 — M3-T1 §243: CRUD persistente de representacion y gates

API licitud usa subcontratos versionados Create/Update/Out con documento editable
y envelope solo salida. Crear asigna UUID servidor antes de bind; editar detecta
model_fields_set, extrae el campo antes de setattr y bind tras relectura/bundle/cambios.
Omitido conserva envelope viejo, cambio de consentimiento lo deja obsoleto, reaporte
renueva identidad, null retira solo de borrador. Lectura respeta tenant/tratamiento;
confirmados no admiten edicion, material previo no se reconstruye.

Guardas tras lock/relectura: confirmacion con representacion 409, nueva revision
EIPD con representacion 409 de asociacion pendiente. Readiness con material presente
409 representacion_readiness_integracion_pendiente: no presentar metadata antigua
como cobertura del nuevo documento. Esta entrega CRUD no integra aun diagnostico
readiness; limites explicitos y politica sin cambios. Sin frontend de aporte nuevo.

11 pruebas HTTP nuevas; bloque completo representacion/storage/runner 127 aprobadas
en 3.79 s, entorno aislado verificado. Casos: guardar/leer SQL, UUID derivado,
omision/obsolescencia/reaporte/null, inyeccion y cambios parciales no aplicados,
tenant ajeno/padre incorrecto, gates y confirmado historico intacto. Regresion
API licitud previa: 174 casos aprobaron en primera corrida; tres casos nuevos
fallaron por fixtures (selector/consentimiento ausentes y app compartida), corregidos
sin relajar guardas. No se afirma suite completa del producto en esta etapa.
Runner incorpora CRUD. Ruff/Black correctos; sin migracion adicional.
Proximo: diagnostico versionado readiness de representacion y cobertura EIPD
conservadora, manteniendo can_confirm=false. M3-T1 EN PROGRESO, pruebas ficticias
hasta MVP; confirmacion/activacion bloqueadas.


## 2026-10-14 — M3-T1 §244: diagnostico de representacion en readiness/interfaz

Contrato de salida versionado con result/motivos, flags false y cobertura pendiente
cuando hay diagnostico. Backend evalua contra RAT actual; motivos de obsolescencia,
material/alcance/fechas y contexto no disponible. Exige representacion ausente para
consentimiento representado sensible; documento completo solo comprueba datos.
Gate de confirmacion conservado. Readiness vuelve a 200 con bloque propio en vez
de 409 temporal. Sin documento/representacion sensible, salida null/no_aplica.

Con diagnostico pendiente, proyeccion V3 marca las tres decisiones no preparadas,
metadata de accion null y motivo de asociacion pendiente. No toca eventos, hashes
historicos ni habilita nuevas revisiones. Estado de metadata interno anterior
sigue referido al contexto de su version; campo cobertura explicito lo delimita.
Cliente valida diagnostico/coherencia/flags y suprime vigencia global/prerrequisitos
que no cubren representacion. Pantalla muestra bloque, motivos españoles y aviso
sin facultad/autenticidad; consulta historica retira el bloque actual. Sin botones
nuevos de escritura o confirmacion. Compatible con respuesta legacy sin bloque.

132 pruebas backend focalizadas aprobadas (5.45 s), entorno aislado verificado;
20 cliente y 11 interacciones Chromium frontend aprobadas (31, 4.5 s), tipos/lint
correctos. Incluye actualizacion test OpenAPI al contrato sucesor sin retirar V3,
rechazo de flags/resultados incoherentes, contexto obsoleto/retiro, tres decisiones
pendientes y UI/historia. Ruff/Black/Prettier correctos. No suite integral nueva,
prueba visual con sesion real del bloque nuevo ni cambio de fixture operativo.
M3-T1 EN PROGRESO; pruebas ficticias hasta MVP; confirmacion/activacion bloqueadas.


## 2026-10-14 — M3-T1 §245: representacion ausente y RAT actual en API

Cuatro casos HTTP ficticios adicionales: representante legal/mandatario, con RAT
sensible antes de crear o cambiado despues. Readiness detecta documento ausente,
conserva flags false y cobertura pendiente; el cambio posterior informa tambien
contexto RAT desactualizado. Consulta no modifica snapshot/envelope persistidos y
confirmacion no resulta exitosa. 17 pruebas API de representacion aprobadas en
5.29 s con base fija aislada verificada; Ruff/Black correctos. Sin cambio de reglas,
fixture operativo ni politica. M3-T1 EN PROGRESO; pruebas ficticias hasta MVP.

## 2026-10-14 — M3-T1 §246: contexto RAT ausente no descarta representacion

Corregido readiness: con consentimiento de representante legal/mandatario y RAT
actual no disponible, el bloque indica requiere_revision/cobertura pendiente aunque
no exista documento. No inferir no_aplica de un contexto que no puede recomponerse.
Cuatro regresiones HTTP ficticias con/sin material y ambos otorgantes; dos casos
sin documento reprodujeron el fallo antes del cambio. Consulta conserva expediente
persistido, flags false y confirmacion bloqueada.

198 pruebas de API representacion, licitud previa y controles V3 aprobadas en
205.51 s con base fija aislada verificada. Ruff/Black y diff-check correctos.
Sin migracion, cambio de politica o datos operativos. M3-T1 EN PROGRESO; pruebas
ficticias hasta MVP; cobertura EIPD de representacion sigue pendiente.
