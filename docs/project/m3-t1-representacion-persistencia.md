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

## 2026-10-14 — M3-T1 §247: documento completo y alcances en API

Tres casos HTTP ficticios comprueban documento completo compatible, alcance RAT
incompatible y alcance de consentimiento sensible incompatible. Completo conserva
can_confirm/authorizes_action false y cobertura pendiente; los alcances incompatibles
informan requiere_revision y motivo especifico. En los tres casos confirmacion y
nueva revision EIPD devuelven 409 con codigo explicito, sin modificar expediente.
24 pruebas API de representacion aprobadas en 7.47 s, base fija aislada verificada;
Ruff/Black correctos. No reglas nuevas, migracion, cambios operativos ni habilitacion.
M3-T1 EN PROGRESO; pruebas ficticias hasta MVP.

## 2026-10-14 — M3-T1 §248: concurrencia representacion/confirmacion

Cuatro casos con PostgreSQL real y app_user prueban ambos ordenes: aporte de
representacion primero o confirmacion ordinaria primero, con commit/rollback del
holder. Espera comprobada por pg_blocking_pids, no por retraso supuesto. Tras commit
el waiter relee y rechaza 409; tras rollback prosigue la otra operacion. Estado
final exclusivo: borrador con material o confirmado sin material. No se permite
confirmado con representacion. Confirmacion ordinaria ficticia no activa EIPD.

28 pruebas API/representacion aprobadas en 8.65 s en base fija aislada verificada;
Ruff/Black correctos. Primera corrida detecto fixture transversal obsoleto al
cambiar consentimiento; reaporte de controles ficticios corrigio preparacion sin
relajar gates. Sin cambios de servicio, migraciones, politica ni datos operativos.
M3-T1 EN PROGRESO; pruebas ficticias hasta MVP; confirmacion EIPD bloqueada.

## 2026-10-14 — M3-T1 §249: regresion OpenAPI detectada por CI

CI de d5a1986 (run 38611120420) fallo en test_openapi_research_contracts por
KeyError LegalAssessmentDraftCreate: el endpoint ya publica el contrato sucesor de
representacion. Prueba corregida para resolver el ref real de requestBody POST/PATCH,
sin depender del nombre interno de clase. Conserva checks de ResearchAssessmentV1,
extras rechazados y binding solo de salida; no cambia contrato ni servicio.

33 pruebas API investigacion/contratos representacion aprobadas en 4.05 s en base
fija aislada verificada; Ruff/Black correctos. Validacion integral remota del nuevo
commit pendiente, no se declara CI completa aprobada. M3-T1 EN PROGRESO; datos
ficticios hasta MVP; confirmacion/activacion EIPD bloqueadas.

## 2026-10-14 — M3-T1 §250: binding EIPD V3 de representacion

Contexto V3 extiende V2 con envelope representacion requerido incluso si null;
contrato interno cerrado, binding/documento StoredV3 separados, dominios de hash
nuevos. Cambios de cuerpo, hashes de asociacion, retiro, investigacion, RAT o
consentimiento invalidan identidad sin repararla. V1/V2 no aceptan documentos V3;
null explicito no comparte hash V2. Funciones puras, sin dispatch/API/metadata/eventos
nuevos ni cambio de gates; cobertura operativa de representacion sigue pendiente.

10 casos nuevos y regresiones de bindings/evaluador historicos: 206 aprobadas en
0.61 s con entorno aislado verificado; Ruff/Black correctos. Sin migracion o datos
operativos. Proximo: contrato sucesor de metadata y composicion compatible antes
de conectar writer/API. M3-T1 EN PROGRESO; datos ficticios hasta MVP; EIPD bloqueada.

## 2026-10-14 — M3-T1 §251: metadata V2 para contexto EIPD V3

Nuevo contrato interno cerrado exige versiones metadata2/binding3/context3,
cobertura research/representacion contexto_v3 y hashes de material nullable
explicitos. Builder puro solo acepta resolucion V3 asociada al contexto vigente;
rechaza contexto obsoleto, no convierte historia ni atribuye facultades. Metadatos
V1 y lectores/eventos actuales intactos. Integracion writer/lectores/UI aun pendiente;
representacion operativa sigue con cobertura pendiente y gates bloqueados.

12 pruebas nuevas; 47 de metadata/bindings nuevos e historicos aprobadas en 0.36 s;
cuatro guardas de runner aprobadas en 0.02 s. Runner aislado incluye suites nuevas.
Ruff/Black correctos. Sin migracion, nuevas rutas o datos operativos. M3-T1 EN
PROGRESO; pruebas ficticias hasta MVP. Autorizacion permanente de usuario para
implementar/validar/commit/push en rama actual; sin merge/despliegue/activar EIPD.

## 2026-10-14 — M3-T1 §252: lectura compatible de metadata sucesora

Lector interno V2 conserva null historico y distingue estrictamente metadata1/2;
rechaza versiones desconocidas/bool/texto y hashes discordantes con evento. Contrato
OutV3 preparado admite identidad V1/V2 sin convertirla, mantiene campos originales
y valida hashes. Ningun endpoint cambia aun; schema SQL actual solo admite metadata1.
Proximo bloque necesario: migracion append-only/constraint para metadata2, pruebas
RLS/append-only y actualizacion de entorno aislado antes de conectar escritura.

Siete casos nuevos; 64 pruebas lector nuevo/historico, contratos representacion y
API investigacion aprobadas en 4.54 s con base fija aislada verificada. Ruff/Black
correctos. Sin migracion, alteracion de historia, politica ni datos operativos.
Objetivo autonomo activo por solicitud explicita del usuario, con commit/push de
bloques validados; sin merge/despliegue ni activar EIPD. M3-T1 EN PROGRESO.

## 2026-10-14 — M3-T1 §253: almacenamiento compatible de metadata V2

Migracion append-only f52d6c9b3e10 tras e41c5b8a2d90 amplía constraint existente:
conserva contrato metadata1 completo y admite metadata2 cerrado con binding/context3,
cobertura research/representacion contexto_v3, hashes de evento concordantes y
hashes de material explicitos nullable. ORM alineado. Sin backfill ni cambios de
filas, privilegios/RLS o canales operativos. Downgrade rechaza si hay eventos V2;
no los borra/convierte para restaurar contrato viejo. Downgrade no ensayado.

Upgrade aplicado solo en base fija aislada despues de verificar head/destino previo;
runner EXPECTED_HEAD actualizado tras exito e incluye suite almacenamiento sucesora.
17 casos nuevos: roundtrip, append-only, identidad null historica, forma/version/
cobertura/hash incompatibles, campo faltante, tenant/actor/padre/no_auth. 38 pruebas
nuevas/historicas/guardas aprobadas en 4.32 s; alembic check sin drift, Ruff/Black
correctos. Base operativa local sigue en e41 hasta integrar lectores/writer coherentes.
M3-T1 EN PROGRESO; ficticios hasta MVP; activacion EIPD bloqueada.

## 2026-10-14 — M3-T1 §254: seleccion de binding V3 desde servidor

Writer compartido valida contexto V3 cerrado antes de cualquier proyeccion y elige
binding3 cuando hay material de representacion. Reaporte tras retiro conserva V3
previo; contexto V2 no puede degradar esa cobertura. Sin representacion ni V3 previo,
seleccion V1/V2 historica conservada. Previous es documento validado de servidor,
no version propuesta por cliente. Omision/null siguen responsabilidad del caller.

Ocho casos nuevos; 29 pruebas writer/binding y HTTP V2 historico aprobadas en 3.51 s,
base fija aislada verificada. Runner incorpora suite. Ruff/Black correctos. Builder
operativo sigue proporcionando V2: falta dispatch/readiness compatible V3, metadata
proyectada y contratos API antes de conectar su uso. Sin nuevos eventos, cambio de
politica o datos operativos. M3-T1 EN PROGRESO; EIPD bloqueada; datos ficticios.

## 2026-10-14 — M3-T1 §255: dispatch/readiness documental V3

Adaptador versionado admite binding/context3, selecciona hash/documento/modelo
correspondiente y conserva proyeccion V1/V2 para reglas historicas. Contexto V3
cerrado se valida antes de proyectar. Material representacion con binding1/2 añade
asociacion_representacion_no_cubierta, invalida contexto y revision previa; V3
reconoce identidad pero conserva motivo representacion_evaluacion_integracion_pendiente
hasta conectar evaluacion conjunta. Nunca can_confirm=true. Contexto V2 no acepta
binding3; cambios/retiro invalidan asociacion sin reparar documentos.

Seis casos nuevos; 47 pruebas adaptador/historicas/metadata/writer/HTTP V3 anteriores
aprobaron en 6.47 s, con base fija aislada verificada. Caso historico reforzado despues:
revision realmente vigente con hashes de su version pasa obsoleta al añadir material;
seis casos nuevos revalidados en 0.20 s. Ruff/Black correctos; runner incorpora suite.
No builder operativo/contexto API cambiado aun, nuevos eventos o politica. Proximo:
composicion y contratos de salida antes de activar writer V3 en endpoints.
M3-T1 EN PROGRESO; datos ficticios hasta MVP; EIPD bloqueada.
