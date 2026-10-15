# M3-T1 — Infancia y adolescencia: primer contrato documental

Estado operativo: persistencia, editor de borrador y composicion documental V5
implementados. M3-T1 sigue EN PROGRESO; solo datos ficticios hasta MVP.

- Columna JSONB nullable y migracion `a73d8e0c4b21` aplicada en desarrollo y base
  aislada. Sin backfill ni cambios RLS; expedientes/historia existentes intactos.
- Editor: `/dashboard/licitud/[treatmentId]/[assessmentId]?organizationId=...`,
  enlazado desde la consulta interna. Documento crudo de entrada, identidad de
  salida; omision conserva, null retira y reaporte asocia contexto final.
- Composicion V5 de solo lectura: contexto V4 con UUID servidor, contexto V3 y
  documento infancia; dominio hash propio. Contexto actual ausente produce hash
  null y revision pendiente, sin reutilizar copia antigua. Incluye bloqueos
  generales/documentales e infancia; las tres decisiones tienen requisitos false.
- El contexto V4 es de consulta, no un nuevo binding persistido de resolucion.
  Resoluciones anteriores mantienen `resolution_child_coverage=no_cubierta`;
  no se alteran hashes V1-V3, metadata ni eventos historicos. Las composiciones
  antiguas no se muestran como cobertura nueva. Activacion/confirmacion bloqueadas.
- Guardado y diagnostico se informan por separado. Error/resultado incierto conserva
  cambios y elimina diagnostico viejo; doble envio impedido. Viewer/confirmado
  solo lectura; API sigue imponiendo permisos y aislamiento del servidor.

Pendiente posterior: contrato y persistencia sucesores de resolucion/revision con
identidad infancia, integracion de politica con fuentes y aceptacion explicitamente
verificadas antes de cualquier capacidad positiva. No levantar gates por campos
completos, por hashes vigentes ni por usar datos ficticios.

## Fuente y limite interpretativo

Revisado el [texto oficial BCN, Ley21.719, articulo16quater](https://www.bcn.cl/leychile/navegar?i=1209272),
que modifica Ley19.628. Distingue interes superior/autonomia progresiva, reglas de
consentimiento para infancia, autorizaciones de adolescentes y caso sensible de
menores de16; contempla autorizacion o mandato legal expreso. Reconoce ademas una
obligacion especial de proteccion para quienes tratan informacion de menores.

La aplicacion recoge un analisis documental de estas materias. No comprueba por
si misma edad, cuidado personal, facultades o autenticidad. No clasifica personas
por nombre ni resuelve fronteras etarias mediante aritmetica o interpretacion libre.
No se usa una fecha futura como gate para postergar este desarrollo.

## Alcance del primer contrato

ChildAdolescentAssessmentV1 hereda scope cerrado de categorias/grupos RAT. Permite
borradores vacios; separa declaracion, evidencia y analisis. Campos de servidor o
fechas de nacimiento no forman parte de esta entrada.

| Grupo de campos | Proposito tecnico |
| --- | --- |
| declared_groups | Declarar infancia, adolescencia y/o subconjunto adolescente sensible menor16; sin duplicados ni grupos desconocidos |
| age_scope_analysis, sensitive_under16 | Explicar relacion edad/alcance y declarar si/no/pendiente el cruce sensible; una lista no deduce automaticamente el otro campo |
| best_interests_analysis, progressive_autonomy_analysis | Documentar analisis, no respuestas juridicas calculadas desde texto |
| proposed_authorization_route, authorization_reference, authorization_analysis | Propuesta consentimiento o autorizacion legal expresa con material de soporte; no autorizacion validada |
| declared_consent_giver | Padre/madre, representante legal, cuidado personal o titular declarados; sin inferir facultades |
| evidence, notes | Referencias documentales y notas; no verificar documentos reales ni incorporar PII innecesaria |

No adoptar automaticamente el mandato general de representacion sensible como
sustituto de los sujetos previstos para infancia. La coherencia y evidencia de
cada ruta se evaluaran expresamente antes de cualquier integracion positiva.

## Secuencia original de referencia

1. Evaluador puro: contraste con flags RAT/declaraciones especiales y scope; ausencia,
   contradiccion o cruce no documentado producen motivos, nunca autorizacion.
2. Asociacion de documento/contexto con tenant/tratamiento/evaluacion y dominios de
   hash propios. No reescribir envelopes ni hashes historicos especiales/EIPD.
3. Contratos CRUD/almacenamiento como bloque coherente, migracion append-only y RLS;
   omitido conserva identidad, null retira solo borrador, reaporte vuelve a asociar.
4. Composicion transversal y sucesor versionado si cambia material cubierto por EIPD;
   no insertar este documento silenciosamente en contextoV3 existente.
5. Matriz HTTP/SQL/concurrencia y rollback; ninguna ruta positiva habilitada solo
   por completitud de campos. Validacion de fuentes y aceptacion siguen separadas.

## Matriz inicial de aceptacion

Contrato parcial y roundtrip; grupos desconocidos/duplicados; campos extra de
servidor/PII rechazados; no deduccion desde nombres. Evaluador pendiente debe cubrir
flags incompatibles, subconjunto menor16 no inferido por coexistencia sensible y
adolescente, grupos mixtos, ruta ausente, titular/padre/cuidado/representante y
referencias incompletas. Despues persistencia: tenant ajeno, actor, scope invalido,
obsolescencia, historial inmutable, confirmacion bloqueada y commit/rollback real.

Esta delimitacion inicia una ruta residual del alcance integral; no difiere las
otras rutas ni acredita cumplimiento juridico externo.

## 2026-10-14 — M3-T1 §275: evaluador puro de infancia/adolescencia

evaluate_child_adolescent_v1 valida contrato/snapshot sin mutarlos, compara grupos y
categorias del scope, detecta codigos ajenos, material residual y resumen RAT
contradictorio. Exige analisis/referencias/evidencia para completitud documental.
Cruce sensible menor16 separado: adolescencia+sensibilidad no lo deduce; pendiente,
subgrupo incoherente o afirmacion sin contexto producen motivos. Rutas legales
expresas y grupos mixtos conservan revision; titular en infancia/cruce menor16 pide
revision. No acredita edad/facultades ni interpreta prosa como prueba. Resultado
completo solo documental; authorizes_action/can_confirm siemprefalse.

104 pruebas focalizadas infancia/contratos/investigacion/representacion aprobadas
en0.31s;19 nuevas del evaluador. Casos incluyen whitespace, determinismo/inmutabilidad,
RAT ausente/resumen incoherente, ausencia/noaplicable, scope, declaracion residual,
grupo mixto, ruta legal, otorgante y cruce no inferido. Ruff/Black correctos. Sin
API/almacenamiento/binding nuevo, sin cambiar fallback ni gates actuales. Solo
fixtures ficticios. Siguiente asociacion versionada propia antes de persistencia.
M3-T1 EN PROGRESO; confirmacion/activacion EIPD bloqueadas.

## 2026-10-14 — M3-T1 §276: identidad propia de infancia/adolescencia

BoundChildAdolescentAssessmentV1 y contexto interno cerrado con UUID servidor de
org/tratamiento/evaluacion, RAT/base/consentimientos, documento de declaraciones
especiales y representacion asociada. Campos nullable requeridos explicitamente.
Dominios SHA256 propios de documento/contexto; helper valida y canoniza sin mutar.
Especiales usa proyeccion documental explicita sin binding para evitar ciclo; un
envelope accidental se rechaza, no se ignora silenciosamente. No se alteran hashes
historicos ni contexto EIPD V3. Asociacion ausente/documento cambiado/contexto
cambiado requieren revision; vigente no acredita facultades ni permite confirmar.

75 pruebas focalizadas aprobadas en0.31s;17 nuevas de identidad. Cubren parent/tenant,
RAT/base/consentimientos/especiales/representacion, cambio de documento, roundtrip,
reaporte explicito, contratos/version/hash/extra/nullables y contexto invalido sin
documento. Ruff/Black correctos. Sin API/migracion/persistencia nuevas, sin datos
operativos ni cambios a gates. Siguiente componer asociacion con diagnostico antes
de contratos CRUD/almacenamiento. M3-T1 EN PROGRESO; EIPD bloqueada.

## 2026-10-14 — M3-T1 §277: diagnostico de infancia con identidad

build_child_adolescent_readiness_v1 compone evaluador documental y asociacion sin
rebind ni mutacion. Expone resultado documental separado de association_status;
contenido completo con hash/contexto obsoleto requiere revision, identidad vigente
no completa contenido faltante, ausencia y noaplicabilidad quedan diferenciadas.
Salida interna cerrada/versionada exige coherencia de motivos/resultado, asociacion
vigente para completo y flags authorizes_action/can_confirm false. No interpreta
identidad como facultades ni habilita operaciones positivas.

60 pruebas focalizadas de infancia aprobadas en0.30s;14 nuevas: separacion identidad/
completitud, documento/contexto/padre cambiados, ausencia/noaplicable, roundtrip,
inmutabilidad, contexto invalido y salidas incoherentes/autoridad inyectada. Ruff/
Black correctos. Sin API/migracion/CRUD ni datos operativos nuevos. Pendiente contraste
semantico con declaraciones especiales/consentimientos relacionados antes de conectar
persistencia; la identidad cubre esos materiales pero no prueba su coherencia legal.
M3-T1 EN PROGRESO; confirmacion/activacion EIPD bloqueadas.

## 2026-10-14 — M3-T1 §278: coherencia documental relacionada de infancia

Nuevo evaluador puro contrasta documento con consentimiento declarado y proyeccion
especial: ausencia/otorgante pendiente, discrepancia de otorgante, tres declaraciones
edad/cruce y su fundamento, scope comparable, condicion infancia y ruta consentimiento.
Padre/madre o cuidado personal no se equiparan automaticamente a los tres valores
del contrato consentimiento actual; relacion no comparable pide revision. Material
sensible exige presencia del consentimiento sensible relacionado, sin afirmar que
esa presencia satisfaga sus reglas propias. Declaracion especial no crea un cruce
sensible menor16 sin flags/scope correspondientes. Sin inferir edad ni facultades.

Composicion agrega estos motivos aunque documento completo y asociacionvigente;
identidad no encubre incoherencia. 71 pruebas infancia aprobadas en0.31s;11 nuevas.
Fixtures del compositor ahora aportan relaciones coherentes explicitas para aislar
los casos previos. Ruff global y Black271 archivos correctos. Sin API/CRUD/migracion
ni datos operativos nuevos; conserva fallback y gates. Siguiente contratos de
persistencia y matriz transaccional antes de integrar almacenamiento como conjunto.
M3-T1 EN PROGRESO; confirmacion/activacion EIPD bloqueadas.

## Matriz transaccional (propuesta original §279)

Estado historico previo a almacenamiento. Contratos separados child_adolescent_api: Create/Update reciben documento crudo o
null, Out recibe envelope servidor. API activa conserva modelos anteriores;
OpenAPI comprobado sin campo nuevo. PATCH serializa con exclude_unset para no
convertir omisiones en null. No importar estos contratos en rutas antes de storage.

| Operacion | Orden/invariante requerido | Verificacion pendiente de implementacion |
| --- | --- | --- |
| Crear | UUID servidor y contexto RAT final antes de bind; documento y fila en misma transaccion | Roundtrip y rollback total tras error posterior |
| PATCH omitido | Conservar envelope/hash originales | Igualdad JSON antes/despues, sin rebind |
| PATCH null | Retirar solo borrador; reevaluar todos los gates | No habilitar positivo por ausencia de material; confirmado inmutable |
| PATCH reaporte | Releer bajo lock de serie y componer contexto final de todos los campos relacionados | Cambios simultaneos de consentimiento/especiales/representacion capturados por hash |
| Cambio relacionado sin reaporte | Conservar documento; diagnosticar asociacion obsoleta | Contexto/parent/documento viejo no promovido |
| Confirmacion/revision EIPD | Relectura con orden global/selector/serie existente; rechazar cobertura infancia no integrada | Espera real commit/rollback, cero eventos ante rechazo |
| Tenant/permisos | organization_id servidor, FK/RLS existentes, runtime app_user sin BYPASSRLS | Otro tenant/padre,viewer/suscripcion y SQL directo |
| Migracion | Columna JSONB nullable none_as_null, envelope objeto; constraint material no confirmado | Upgrade aislado desde head anterior, sin backfill; ORM/Alembic coherentes |
| Historia | Lectura de confirmado/reemplazado sin mutar; nuevos contextos versionados | Hashes y revisiones anteriores identicos; no presentar V3 como cobertura nueva |

La columna propuesta child_adolescent_assessment no existe aun. Integrar modelo,
migracion/contratos/CRUD/gates como bloque; no aceptar y descartar atributos Python
no persistidos. No nueva tabla ni cambio de privilegios inferido por agregar columna.
El plan no agrega autoridad positiva ni supone verificacion de documentos reales.
