# M3-T1 — Integracion persistente de investigacion

Fecha: 2026-10-09. §132. Estado: DISENO DE INTEGRACION; NO IMPLEMENTADO.
Base: 374b83bf381f273d12f8ddbc1f4fb68b549d67c1.

## Almacenamiento y compatibilidad

Agregar legal_assessments.research_assessment JSONB nullable, almacenando
BoundResearchAssessmentV1 (assessment y context_binding). Migracion append-only
sobre b17d95c0286f: ADD COLUMN y CHECK null u objeto JSON; sin backfill ni cambios
a datos historicos. Historicos devuelven null, no reciben asociacion sintetica.
No crear tabla global ni permisos nuevos; conservar organization_id/RLS de M3.
Revisar efectivamente los grants por columna al aplicar migracion, no asumirlos.

Entrada create/update: research_assessment ResearchAssessmentV1 nullable, sin
context_binding del cliente. Salida: BoundResearchAssessmentV1 nullable, asociacion
generada por servidor. Rechazar hashes/client metadata dentro del expediente por
extra=forbid. No relajar los schemas historicos especiales/EIPD.

research.py importa contratos de licitud.py; importar research.py directamente
de vuelta crearia ciclo. Antes de añadir campos, ubicar las nuevas definiciones
en licitud.py antes de DraftCreate y dejar research.py como exportacion compatible,
sin mover ni modificar contratos historicos. Probar importacion y OpenAPI.

## Semantica de borrador

| Operacion | Resultado previsto |
| --- | --- |
| Create con expediente | Generar binding con RAT construido por servidor, base canonica y LIA del borrador; persistir objeto |
| Create sin expediente | Persistir SQL NULL |
| PATCH omitido | Conservar expediente y binding previos exactamente |
| PATCH null explicito | Retirar expediente, persistir SQL NULL |
| PATCH objeto | Revalidar y generar binding solo para ese aporte explicito |
| PATCH RAT/base/LIA sin reaporte | Conservar binding previo; asociacion debe resultar obsoleta |
| PATCH LIA y expediente juntos | Vincular al contexto final de la misma actualizacion, no a valores anteriores |
| Confirmado/reemplazado | Mantener protecciones existentes; impedir editar o retirar expediente |

Usar model_fields_set para distinguir omision/null. No renovar binding al consultar
readiness/GET ni repararlo por comparar hashes. Aplicar el mismo bloqueo de serie y
control de borrador existentes, rollback atomico y aislamiento tenant.

## Readiness y gates por etapas

Primer incremento de persistencia: guardar/leer/reaportar y mostrar estado documental
y asociacion, sin habilitar investigacion. Mantener validador_no_implementado en
special_conditions hasta integrar la ruta en un cambio posterior revisado.
BoundResearchAssessmentV1 vigente y evaluador completo no bastan para confirmar.

Antes de habilitar: nueva version especial que incluya el material de investigacion
y nueva version EIPD correspondiente, dispatch explicito y pruebas de compatibilidad
para historicos sin documento. No editar hashes/versiones anteriores. Que un contrato
sea viejo no autoriza atribuirle cobertura de un expediente que no contiene.

El primer incremento exige base interes_legitimo_art13d/LIA vigente, RAT no sensible
y titulares adultos. Rutas no soportadas permanecen en revision. No sustituye
screening EIPD, deteccion de condiciones especiales ni autoridad humana.

## Validacion prevista

- Migracion/head/modelos coherentes, NULL historico y CHECK JSONB.
- CRUD PostgreSQL real con app_user, RLS tenant cruzado y alcance RAT.
- HTTP create/GET/PATCH: omision/null/reaportes, ambos cambios atomicos y hashes
  de cliente rechazados dentro del contrato cerrado.
- Contexto/LIA cambiado sin reaporte produce obsolescencia; reaporte explicito
  repara solo la asociacion nueva, sin reinterpretar bindings historicos.
- Estado confirmado/reemplazado conserva expediente y no admite mutacion.
- Readiness/confirmacion mantiene bloqueo de investigacion/EIPD durante esta etapa.
- Ejecutar pruebas en base aislada. Al cambiar head, migrarla y actualizar guarda
  del runner tras revisar identidad; no tocar registro operacional para probar.

## Orden de implementacion

1. Modelos/schema/migracion compatibles y comprobacion de NULL/grants.
2. Servicio/API de borrador con semantica exacta de PATCH y pruebas tenant/HTTP.
3. Readiness documental, obsolescencia y protecciones de inmutabilidad.
4. Versiones nuevas especiales/EIPD y gate integrado con aceptacion revisada.

No migracion aplicada en §132. Ley fija, M3-T1 EN PROGRESO; confirmacion de
investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §133: almacenamiento nullable de investigacion

Migracion append-only c28f1a9d730b sobre b17d95c0286f agrega research_assessment
JSONB nullable a legal_assessments, CHECK SQL NULL u objeto, sin backfill. ORM
agrega campo/constraint; ninguno de los expedientes historicos se reinterpreta.
Contratos nuevos movidos antes de DraftCreate en licitud.py y reexportados por
schemas/research.py para evitar ciclos de importacion; no se agrega input/output
API aun, evitando aceptar datos sin servicio de guardado. Hashes historicos intactos.

Primero upgrade/head y alembic check en base aislada aprobados. Dos pruebas nuevas
verifican columna/nullable/RLS/permisos runtime y borrador HTTP real con SQL NULL,
rechazo arrays/texto/numero/bool/JSON null y almacenamiento objeto. CHECK SQL no
valida todo el contrato; servicio/API posterior lo hara. La primera comprobacion
por nombre de constraint fallo por convencion de nombres; ajustada a tabla/definicion.
Suite final aislada: 121 aprobadas en 10.03 s. Black/Ruff aprobados; runner exige
nuevo head c28f1a9d730b, base aislada y registro EIPD vacio como antes.

Luego migracion aplicada al desarrollo local, alembic check aprobado y snapshot
EIPD completo exactamente igual antes/despues: selector revision 1. Sin cambios de
password/perfil/politicas; no suite contra base operacional ni despliegue remoto.
Nuevo head de ambas bases c28f1a9d730b; procedimientos antiguos con head previo son
historicos, requieren ese sucesor para la version actual del codigo.

Proximo: crear/leer/PATCH de expediente con binding de servidor, omision/null/reaporte
y aislamiento tenant, manteniendo investigacion bloqueada hasta integrar readiness.
Ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §134: expediente de investigacion en API de borrador

Create/PATCH aceptan ResearchAssessmentV1 nullable; salida GET/POST/PATCH expone
BoundResearchAssessmentV1 nullable. Servidor genera hashes con RAT/base/LIA finales.
PATCH model_fields_set distingue omision (preserva objeto/binding), null (retira)
y reaporte (revalida/vincula). Base/LIA cambiadas sin reaporte conservan asociacion
anterior, detectable como obsoleta sin renovacion en GET. No cambios a contratos,
hashes ni gates historicos especiales/EIPD. No nueva migracion.

Seis casos HTTP/OpenAPI nuevos contra PostgreSQL aislado: crear/consultar, cambio
simultaneo LIA/base/reaporte, obsolescencia sin reaporte, retiro, rechazo de binding
cliente en create/PATCH, acceso con organizacion ajena rechazado y PATCH bloqueado
en confirmado/reemplazado con expediente conservado. Estados historicos preparados
por fixture con metadatos validos; no equivale a habilitar confirmacion investigacion.
La prueba de acceso usa identidad A con cabecera B (403); no afirma por si sola una
prueba SQL directa de RLS. Las pruebas HTTP existentes verifican compatibilidad.

Primera suite ampliada: 297 aprobadas y tres fallos de preparacion de pruebas nuevas
(dict LIA y overrides de identidad). Corregidos; segundo intento detecto metadatos
obligatorios de ciclo de vida en fixtures, corregidos sin cambiar restricciones.
Resultado final: 127 pruebas focalizadas aprobadas en 11.78 s; los 174 casos HTTP
existentes de licitud ya aprobaron en la ejecucion ampliada. Black/Ruff aprobados.
Runner incluye ambas suites para siguientes ejecuciones. Sin pruebas en base
operacional, cambios de politica/credenciales ni despliegue remoto.

Proximo: integrar readiness documental y estado de asociacion de investigacion,
con bloqueo conservador e inmutabilidad; luego versiones especiales/EIPD nuevas.
Ley fija, M3-T1 EN PROGRESO, confirmacion de investigacion y activacion EIPD
bloqueadas. Sin commit/push en este paso.

## 2026-10-09 — M3-T1 §135: readiness de investigacion y bloqueo conservador

Readiness agrega research nullable con result/issues/applicability documentales,
association_result/association_issues independientes y can_confirm fijo false.
Evalua sobre RAT actual recomponible, base y LIA; compara binding persistido sin
renovarlo. Si RAT no disponible informa contexto_rat_no_disponible; si investigacion
es declarada y no hay expediente informa expediente/asociacion ausentes. Historicos
sin expediente ni regimen detectado conservan research null, sin hash sintetico.

Control transversal compartido por readiness y confirmacion agrega bloqueo 409
investigacion_confirmacion_bloqueada si hay expediente o regimen detectado, incluso
si se declararon respuestas negativas o el documento esta completo/vigente.
No se cambia validador especial ni versiones/hashes especiales/EIPD anteriores.
Completitud documental no implica autoridad ni activa una ruta excepcional.

Nuevos casos HTTP verifican completo+vigente+bloqueado, confirmacion 409 sin mutar
expediente, lectura reiterada sin escrituras, LIA cambiada sin reaporte produce
obsolescencia aun con documento completo, reaporte recupera vigencia, falta evidencia
produce incompleto y retiro deja null para ruta no declarada. Otro caso verifica
investigacion declarada sin documento, con bloqueos y sin asociacion sintetica.
Validacion final ampliada en base aislada: 303 pruebas aprobadas en 248.17 s
(incluye 174 HTTP existentes de licitud y 129 focalizadas). Black/Ruff aprobados.
Sin ejecucion de suite contra base operacional ni nueva migracion.

Proximo: delimitar nuevas versiones de asociaciones especiales/EIPD que cubran el
expediente de investigacion sin reinterpretar material historico. Mantener el gate
bloqueado hasta integracion completa y aceptacion revisada. Ley fija, M3-T1 EN
PROGRESO, activacion EIPD bloqueada. Sin migracion/despliegue ni commit/push.

## 2026-10-09 — M3-T1 §136: asociaciones de investigacion delimitadas

Plan concreto en docs/project/m3-t1-investigacion-asociaciones.md. Sucesores previstos:
SpecialContextBindingV11 y EipdContextBindingV12, envelope de dominio/version nuevo
con hash anterior intacto y expediente BoundResearchAssessmentV1 completo o null;
screening incluye base explicita. No regenerar binding research ni hashes historicos.
Dispatch por version; asociaciones antiguas con research requieren revision por falta
de cobertura. PATCH respeta orden RAT/base/LIA, research, especiales, screening y
solo renueva los documentos reaportados. GET sin escrituras e historicos inmutables.

Se delimita tambien la deuda de contexto de resolucion/revision EIPD para no atribuir
aceptacion historica a investigacion antes de ampliar esa frontera explicitamente.
Proximo: contratos y funciones puras nuevos, luego dispatch/API. Sin implementacion,
migracion ni suite nueva; ultima validacion 303 §135. Ley fija, M3-T1 EN PROGRESO,
confirmacion investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §137: contratos y funciones puras de asociacion

SpecialContextBindingV11 y EipdContextBindingV12 agregados como sucesores cerrados;
versiones anteriores conservadas. Nuevas funciones hash/bind especiales V11 y
screening V12 envuelven el hash anterior intacto con dominio/version explicitos y
BoundResearchAssessmentV1 completo o null. Screening agrega legal_basis validada
explicitamente. Helper research_transversal_binding serializa sin mutacion y no
repara/recalcula los hashes de investigacion recibidos. Binding obsoleto puede ser
serializado estructuralmente: su vigencia sigue siendo un control independiente.

16 casos nuevos: determinismo modelo/dict, null vs documento, cambios de cuerpo,
binding, RAT y LIA, base explicita screening, version research desconocida, contratos
cerrados sucesores y fixtures de hashes historicos. Comparacion estructural de todas
las funciones anteriores contra ed0f669 aprobada como verificacion del cambio; fuera
de pytest para no exigir historial Git en clones superficiales. Fixtures de hashes
quedan como regresion automatica. Suite final aislada: 145 aprobadas en 13.00 s;
Black/Ruff/diff check aprobados. No repetida suite HTTP ampliada de 303 §135, pues
servicios/API siguen generando las versiones anteriores y su dispatch no se modifica.

No dispatch evaluador nuevo ni generacion API de versiones sucesoras aun: funciones
nuevas son primitives aisladas; no afirmar cobertura operacional de investigacion.
No migracion/backfill, cambios de datos/politicas/credenciales, despliegue ni gates.
Proximo: dispatch por version y diagnostico de falta de cobertura; luego escritura
API ordenada research/especiales/screening con pruebas de compatibilidad ampliadas.
Ley fija, M3-T1 EN PROGRESO; confirmacion investigacion y activacion EIPD bloqueadas.
Sin commit/push.

## 2026-10-09 — M3-T1 §138: dispatch y cobertura de investigacion

Evaluadores especiales/screening aceptan research por argumento keyword opcional;
screening recibe tambien legal_basis. Control transversal M3 propaga documentos
persistidos y base final, sin cambiar funciones de escritura create/PATCH ni sus
versiones generadas (especiales V10/screening V11 hasta siguiente incremento).
Version especial 11 y screening 12 comparan contra sus nuevos hashes; las versiones
anteriores conservan algoritmos historicos. Version desconocida sigue rechazada por
contratos cerrados, sin promocion ni fallback a sucesores.

Research presente con version anterior emite asociacion_investigacion_no_cubierta
(requiere_revision especial/pendiente_revision screening) y context_current false.
Chequeo independiente de las ramas de falta de cobertura previa: otros motivos no
se ocultan. Revalida estructura BoundResearchAssessmentV1; no repara sus hashes ni
sustituye su evaluador de completitud/vigencia. Nueva asociacion transversal vigente
no garantiza vigencia research ni autoridad; gate §135 permanece bloqueado.

Ocho casos nuevos: evaluacion antigua/nueva para ambos documentos, cambio de cuerpo
con metadatos conservados produce obsolescencia, antiguos sin research compatibles
y falta de cobertura investigacion coexistiendo con cobertura contractual pendiente.
Suite focalizada 153 aprobadas en 21.35 s. Suite ampliada aislada final: 327 aprobadas en 389.91 s, incluidos 174 casos HTTP
existentes. Black/Ruff/diff check aprobados. Sin ejecucion contra base operacional,
cambios de tablas/datos operacionales ni politicas.

Proximo: generar especiales V11/screening V12 desde API respetando orden final
RAT/base/LIA, research, especiales, screening y omision/null/reaporte. Mantener los
bloqueos hasta revisar frontera de resolucion/revision/aceptacion. Ley fija, M3-T1
EN PROGRESO; confirmacion investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §139: asociaciones sucesoras en escritura API

Create/PATCH generan especiales V11 y screening V12 cuando sus respectivos documentos
se aportan. Orden existente conservado: RAT/base/LIA y documentos finales, research
vinculado explicitamente, especiales con research final, screening con especiales y
research finales/base explicita. Omision conserva el binding previo y null retira,
sin renovacion indirecta ni promocion de historicos. Sin backfill ni migracion.

Consumidores de screening en frontera V1 y screening V2 propagan ctx.legal_basis para
comparar V12, incluyendo casos ordinarios sin research. Contexto de resolucion V1 no
se amplia con investigacion: su cobertura sigue pendiente y el gate §135 permanece
bloqueado. No se atribuye aceptacion de investigacion a revisiones antiguas.

Dos casos HTTP parametrizados aportan/retiran research sin especiales/screening,
verifican conservacion y obsolescencia, luego aporte conjunto recupera asociaciones
vigentes usando valores finales. Reaportar solo especiales no renueva screening;
actualizacion invalida conserva expediente previo. GET no muta y el bloqueo permanece.
Pruebas HTTP existentes actualizan expectativas de versiones/hashes de documentos
nuevos a V11/V12, sin alterar fixtures historicas de funciones puras.

Suite focalizada 155 aprobadas en 17.34 s. Validacion ampliada aislada: 329 aprobadas en 219.37 s. Ademas 162 regresiones
de frontera EIPD/screening V2 aprobadas en 0.75 s. Black/Ruff/diff check aprobados.
Sin suite operacional ni cambio de migracion/registro/politica. Proximo: revisar cobertura versionada del contexto
resolucion/revision EIPD para investigacion, sin ampliar contratos historicos ni
habilitar confirmacion antes de aceptacion revisada. Ley fija, M3-T1 EN PROGRESO,
confirmacion investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §140: contexto y revision EIPD de investigacion delimitados

Revision del codigo confirma que ContextV1 no incluye research; vigencia documental
y evento historico no acreditan investigacion. Plan concreto en
m3-t1-investigacion-resolucion-eipd.md: contexto/binding/Stored V2 separados, hashes
con dominio/version nuevo, dispatch historico y seleccion de version sin reparacion
ni degradacion automatica. Reaportes documentales no crean decisiones humanas.

Se delimita revision de frontera/screening/composicion y metadatos de eventos antes
de escritor V2; no asumir migracion ni cobertura de politica existente. Proximo:
contratos y funciones puras V2 con regresiones V1 intactas. Paso documental, sin
suite nueva; ultima 329 ampliadas y 162 regresiones §139. Ley fija, M3-T1 EN PROGRESO,
confirmacion investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §141: contexto y asociacion puros de resolucion V2

Contratos nuevos EipdResolutionContextBindingV2 y StoredV2 separados de V1; StoredV2
exige binding V2 no nullable. Nuevo modulo eipd_resolution_binding_v2.py define
ContextV2 cerrado con context_schema_version 2 y research_assessment obligatorio,
aunque null. Hash de contexto y documental usan dominios/version explicitos; bind
revalida entrada documental sin hashes de cliente y compara sin reparar asociaciones.
V1 y su modulo historico permanecen intactos; ninguna salida/API admite V2 aun.

Nueve casos nuevos: determinismo modelo/dict y no mutacion; cambios de cuerpo/binding
research, retiro, base, RAT y LIA invalidan contexto; campos extras/version desconocida
rechazados, research omitido rechazado/null admitido, V2 rechazado por contratos V1
cerrados, documento ya asociado no aceptado como entrada editable. Fixtures de hashes
V1 de contexto/documento preservadas; V2 null tiene identidad distinta a V1.
Runner incorpora nuevas pruebas y regresiones documentales V1. Resultado final
focalizado aislado 323 aprobadas en 31.40 s (9 nuevas, 159 documentales V1 y 155 previas).
Black/Ruff/diff check aprobados. No nueva suite HTTP ampliada: API/escritores y
comparadores existentes no se cambian; ultima ampliada 329 y 162 regresiones §139.

Proximo: dispatch documental/readiness y revision con diagnostico explicito de
cobertura research; posterior frontera/composicion, metadatos y escritor API V2.
No migracion/backfill, eventos/revisiones nuevas ni cambios de politica/credenciales.
Ley fija, M3-T1 EN PROGRESO; confirmacion investigacion y activacion EIPD bloqueadas.
Sin commit/push.

## 2026-10-09 — M3-T1 §142: evaluacion y vigencia por version

Nuevo eipd_resolution_readiness_v2.py agrega funciones puras de dispatch documental
y vigencia de revision. Valida Stored/contexto segun binding_version 1/2; version
no admitida rechazada. V2 compara hashes sucesores; V1 conserva comparador/hashes.
Reglas documentales comunes extraidas a helper parametrizado por modelos/comparador;
wrapper V1 conserva comportamiento y regresiones. No cambios en hashes V1.

Research en contexto V2 con resolucion V1 agrega asociacion_investigacion_no_cubierta
y context_current false. Proyeccion de campos V1 solo aplica reglas historicas con
falta de cobertura explicita, sin conversion/reasociacion del documento. V2 conserva
comparacion completa; readiness agrega completitud y vigencia research independientes,
sin reparar metadatos. can_confirm permanece false incluso con hashes coincidentes.
Revision anterior sigue visible; V1 con research resulta obsoleta aunque sus hashes
historicos coincidan. Estado vigente V2 describe coincidencia de hashes, no aprobacion
ni completitud juridica. Cambios research invalidan vigencia sin modificar evento.

Cuatro casos nuevos verifican dispatch V1/V2 y evento conservado/obsoleto, ausencia de
contexto, version desconocida y compatibilidad V1 sin research. Suite focalizada
327 aprobadas en 30.33 s, con 159 regresiones documentales V1. Ademas 272 regresiones
frontera/screening/prerequisitos de revision V2 aprobadas en 2.92 s. Black/Ruff/diff
check aprobados. No repetida suite HTTP ampliada: funciones nuevas no estan conectadas
a API, tipos de salida ni escritores; wrapper historico mantiene resultados verificados.

Proximo: definir/integrar cobertura research en frontera y composicion versionadas,
y luego lectura/escritura API V2 y metadatos de eventos. No migracion/backfill,
revision/evento/politica nueva ni cambios de credenciales. Ley fija, M3-T1 EN PROGRESO;
confirmacion investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §143: frontera/composicion de investigacion delimitadas

Plan en m3-t1-investigacion-frontera-composicion.md tras revisar contratos: sucesores
FrontierV2, ScreeningV3 y CompositionV3 reciben ContextV2/research explicitos, sin
ampliar contratos V1/V2 ni proyectar material para simular cobertura. Diferenciar
version de evaluacion de version de binding. Mantener motivos de deteccion completos,
validador_no_implementado y bloqueo conservador hasta integracion/aceptacion revisadas.

Primer incremento previsto frontera V2 pura no declara preparada la ruta mientras
el validador especial este pendiente. Posterior screening/composicion y luego lectura/
escritura API/metadatos de eventos. Paso documental sin suite nueva: ultima 327
focalizadas y 272 regresiones §142. Ley fija, M3-T1 EN PROGRESO; confirmacion de
investigacion/activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §144: frontera V2 pura de investigacion

Nuevo eipd_frontier_v2.py revalida ContextV2 cerrado y evalua research documental y
asociacion, rol responsable, especiales/screening con research y base finales.
Conserva motivos completos de evaluadores; detecta discordancia de declaracion y
alcance del expediente especial. Ruta investigacion_no_sensible_adultos identifica
candidato de alcance, no permiso ni preparacion; sensible/menores/null/base/rol fuera
de alcance mantienen sin_resolver. Contexto ausente produce incompleto.

Resultado mantiene can_confirm e is_frontier_prepared fijos false, y agrega bloqueo
investigacion_confirmacion_bloqueada aun con documento completo/asociaciones vigentes.
validador_no_implementado historico permanece visible. Ningun cambio al FrontierV1,
screening/composicion anteriores, API, eventos, politica o datos operacionales.

Diez casos nuevos: completo pero bloqueado/determinista/sin mutacion, cambios de
cuerpo o binding obsoletos, null, sensible, menores, declaracion negativa discordante,
alcance discordante, contexto ausente/version desconocida/extra/campo omitido y
asociaciones historicas especiales/screening con falta de cobertura acumulada.
Suite final focalizada aislada 337 aprobadas en 30.43 s. Black/Ruff/diff check aprobados.
No nueva suite HTTP ampliada porque modulo puro aun no conectado a API; ultimas
regresiones adicionales 272 §142. No migracion ni reparacion de hashes.

Proximo: screening V3 sobre frontera/contexto V2 y composicion V3 conservadora,
antes de integrar lectura/escritura API/metadatos de eventos y aceptacion revisada.
Ley fija, M3-T1 EN PROGRESO; confirmacion investigacion y activacion EIPD bloqueadas.
Sin commit/push.

## 2026-10-09 — M3-T1 §145: screening V3 conservador

Nuevo eipd_screening_v3.py consume frontera V2, que revalida ContextV2 cerrado.
Preserva sin reclasificar resultado, vigencia, issues y observaciones del screening
original. evaluation_version=3 es independiente de schema_version=12 del binding.
can_continue exige frontera preparada y ausencia de supuestos declarados;
can_confirm permanece false. La frontera actual nunca declara preparacion, por lo
que investigacion sigue bloqueada aunque el expediente este completo y vigente.
Contexto ausente conserva screening pendiente; version desconocida, campos extra
y research omitido se rechazan. Screening V2 historico no acepta ContextV2.

Once casos nuevos cubren conservacion/determinismo/sin mutacion, obsolescencia,
retiro, sensible/menores, contexto ausente y contrato cerrado. Modulo puro sin
conexion API, eventos, politica ni migracion. 348 pruebas focalizadas aisladas aprobadas en 27.49 s; Ruff y Black aprobados.
La suite HTTP ampliada no se repitio porque este modulo aun no se conecta a API.
Proximo: composicion V3 con diagnosticos de investigacion y bloqueo conservador;
luego integracion API/metadatos de eventos y aceptacion revisada.
Ley fija; M3-T1 EN PROGRESO. Activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §146: composicion V3 de investigacion

Nuevo eipd_controls_v3.py mantiene contratos separados: entrada cerrada con ContextV2,
resolucion StoredV1/V2 explicita, evento humano y politica/identidad reales de servidor.
Composicion pura sin DB ni escritura. STAGES_V3 incorpora research sin modificar
las etapas ni contratos historicos. Conserva deteccion V3 completa, evaluacion
ordinaria, motivos de frontera, asociacion/documento research y dispatch de resolucion.
Preparacion, revision documental y vigencia de politica se muestran por separado.
Revision de otro tenant/expediente se conserva visible como obsoleta; evento V1 no
acredita cobertura research. Identidad sin evento humano y versiones desconocidas
se rechazan. Fecha de evaluacion explicita; resultado determinista sin mutacion.

Politica V1 solo representa rutas sensibles historicas: se evalúan barreras generales
con sin_resolver y se agrega politica_investigacion_no_implementada sin ampliar V1.
Incluso una identidad coincidente y evento continuar vigente conservan el bloqueo
investigacion_confirmacion_bloqueada. can_confirm fijo false; no promocion automatica
por preparacion documental ni fuentes declaradas. API/eventos/politica operativa y
registro local permanecen sin cambios. Integracion API y metadatos de eventos siguen
pendientes; no se declara terminada la etapa ni habilitada la ruta.

Dieciocho casos nuevos cubren contratos, estado conservador, diagnosticos completos,
resolucion V1/V2, revision positiva/negativa/obsoleta/otro expediente, politica e identidad.
550 pruebas aprobadas en 30.93 s en base aislada protegida: 366 focalizadas
y 184 regresiones historicas de composicion/politica. Black/Ruff aprobados.
Suite HTTP ampliada no repetida: modulo puro aun no conectado a API.
Proximo: delimitar e integrar lectura API versionada de composicion/resolucion antes
de ampliar el escritor y los metadatos auditables de eventos. Aceptacion pendiente.
Ley fija; M3-T1 EN PROGRESO, investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §147: lectura API de composicion V3

Readiness incorpora eipd_controls_v3 opcional cuando hay expediente research o
regimen investigacion detectado. ContextV2 se construye con RAT actual y documentos
persistidos sin rebind/reparacion. Se agrega salida cerrada V3, frontera V2 y
resolucion versionada; banderas can_confirm/can_continue/is_frontier_prepared false
son explicitas. Contratos V1/V2 y sus acciones no se reinterpretan.

La lectura comparte el ultimo evento/identidad obtenidos por consulta unica de
historial; consulta el registro real de politica. Selector ausente produce politica
null y bloqueo politica_no_disponible, sin bootstrap ni fallback sintetico. Registro
invalido conserva rechazo conservador. Politica V1 no acredita ruta investigacion.
No cambia confirmacion/revision, escritor de resolucion, eventos ni base operacional.
La resolucion StoredV2 sigue pendiente de integracion de escritura y metadatos.

Pruebas HTTP nuevas verifican lectura sin INSERT/UPDATE/DELETE, historial consultado
una vez, sin eventos sinteticos, query parameters sin autoridad, limites entre tenants,
asociacion vigente/obsoleta, ordinario sin research con V3 null y OpenAPI cerrado.
Regresion pura adicional corrige propagacion de issues research sin question_id:
el campo es opcional en el agregador, sin perder los motivos de incompletitud.
Suite protegida completa mas readiness V2: 570 pruebas aprobadas en 455.49 s.
Incluye 174 pruebas HTTP de licitud, tres casos HTTP/OpenAPI nuevos y una
regresion pura de expediente research incompleto. Black/Ruff aprobados.
Proximo: integracion versionada del escritor de resolucion y metadatos auditables
sin activar EIPD ni confirmar investigacion; aceptacion revisada pendiente.
Ley fija; M3-T1 EN PROGRESO. Activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §148: escritor puro de resolucion versionada

Nuevo eipd_resolution_writer.py selecciona binding con material de servidor:
ContextV2 cerrado y resolucion previa persistida opcional. Research presente o
investigacion declarada exige V2 aun sin documento research; una resolucion V2
previa conserva V2 despues de retirar documento/declaracion. Ordinario sin research
ni antecedente V2 mantiene binding V1 exacto. Reaporte explicito genera asociacion
sobre contexto final; no muta ni repara documentos anteriores. Version desconocida
y binding aportado dentro del documento de cliente se rechazan.

Funcion pura aun no conectada a POST/PATCH. Omision conserva y null retira deben
seguir resueltos por el caller, bajo locks existentes. Revision/confirmacion y lector
historico esperan V1: integrar esos consumidores antes de habilitar persistencia V2,
sin convertir eventos antiguos ni permitir decisiones positivas. Metadatos auditables
requieren documentar version de binding y cobertura del contexto de cada evento.

Cinco pruebas nuevas: research vigente sin mutacion/determinista, research declarado
sin documento, retirada sin downgrade, ordinario identico V1, contratos rechazados.
375 pruebas focalizadas aisladas aprobadas en 28.97 s; Black/Ruff aprobados.
Suite HTTP ampliada no repetida: helper puro sin conexion API. Ultima suite
completa mas readiness V2: 570 aprobadas en §147.
Proximo: conectar escritor/lectores mediante dispatch y bloqueo explicito de revision
V2 hasta incorporar metadatos auditables. No migracion ni cambio operacional.
Ley fija; M3-T1 EN PROGRESO. Activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §149: escritor V2 conectado a API

POST/PATCH de resolucion usan bind_eipd_resolution_for_context sobre ContextV2
con material final research/especiales/screening/base/LIA/RAT. PATCH aporta antecedente
persistido para impedir downgrade V2. Omision conserva JSON anterior; null elimina;
reaporte explicito asocia nuevamente. Out admite StoredV1 y StoredV2 sin ampliar
el documento de entrada: binding del cliente sigue rechazado. Ordinario mantiene V1.

Readiness despacha documento y vigencia de revision por version cuando hay research
presente/declarado o resolucion V2. Conserva forma documental superior y expone
binding_version en composicion V3. Composiciones V1/V2 quedan null en este ambito;
no se proyecta una resolucion V2 sobre lectores historicos. V3 sigue disponible al
retirar research si persiste resolucion V2. Registro real de politica o ausencia
explicita; sin bootstrap, rebind de lectura ni eventos sinteticos.

Confirmacion y registro de cualquier decision de revision V2 rechazan 409
resolucion_eipd_v2_revision_pendiente tras relectura/locks existentes. Metadatos
versionados de eventos aun pendientes; no se escribe historia V2 sin cobertura
auditable. Acciones historicas V1 conservan comportamiento. No migracion ni cambio
operacional; ley fija y activacion EIPD bloqueada.

Seis casos HTTP nuevos cubren create/PATCH y contexto final, omision/obsolescencia/
reaporte/null, retirada sin downgrade, V1 preservada hasta reaporte, aislamiento,
binding cliente rechazado, declaracion sin documento, lectura sin mutacion, revision
positiva/negativa bloqueada sin eventos e inmutabilidad de expediente confirmado.
485 pruebas aisladas aprobadas en 68.19 s: suite focalizada mas regresiones
HTTP de resolucion, revision, readiness V2 y confirmacion V2/seleccionada.
Incluye seis casos nuevos. Black/Ruff aprobados. No se repitieron las 174
pruebas generales HTTP de licitud; ultima suite completa §147: 570 aprobadas.
Proximo: contrato/metadatos auditables por version para eventos, conservando historia
V1 y bloqueo hasta integrar prerequisitos y aceptacion. M3-T1 EN PROGRESO.
Sin commit/push.

## 2026-10-09 — M3-T1 §150: contrato puro de metadatos de revision

Nuevo schemas/eipd_review_metadata.py define EipdReviewContextMetadataV1 cerrado:
metadata_schema_version 1, versiones enteras estrictas de binding/contexto 1/2,
cobertura no_cubierta/contexto_v2 coherente, hashes de documento/contexto y hash
opcional del material research completo (incluido su binding). V2 cubre research
null explicitamente; null en hash de research no declara documento presente.

Nuevo services/eipd_review_metadata.py genera identidad desde material de servidor
validado y asociado vigente. No proyecta ContextV2 sobre binding V1 ni genera identidad
vigente para contexto obsoleto/ausente/resolucion no asociada. Usa hashes historicos
V1 o sucesores V2 y dominio separado del hash research. Comparador verifica identidad
contra hashes de evento y material actual; metadatos ausentes permanecen ausentes.
Vigencia no acredita autoridad, tenant, completitud, politica ni decision positiva:
esas validaciones corresponden a los prerequisitos/locks/actor autentico del caller.

Doce casos prueban V1/V2 sin mutacion/determinismo, correspondencia con evento,
historia sin metadata, hashes distintos, proyeccion rechazada, contexto obsoleto o
material ausente, V2 con research null y contratos/versiones estrictos incoherentes.
393 pruebas focalizadas aisladas aprobadas en 18.58 s, con doce casos nuevos;
Black/Ruff aprobados. No se repitio suite HTTP ampliada: helpers puros sin conexion
API. Ultimas regresiones API ampliadas §149: 485 aprobadas.

Sin conexion API/eventos ni migracion en este paso. Proxima persistencia: nueva columna
JSONB nullable sin backfill/default sintetico, preservando RLS/tenant/append-only y
FK historicas. Validar contrato/pares/hash del evento al insertar; salida de lectura
versionada debe mantener null historico y no reinterpretar evidencias V1. Prerequisitos
V2 y aceptacion siguen pendientes; todas las revisiones V2 siguen rechazadas.
Ley fija, M3-T1 EN PROGRESO; activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §151: almacenamiento de metadatos de revision

Migracion aditiva d39e2b0f841c sobre c28f1a9d730b agrega review_context_metadata JSONB
nullable a eipd_resolution_reviews, sin default/backfill. CHECK cerrado exige campos,
versiones/cobertura coherentes y hashes identicos a los del evento; research hash es
null o hash valido solo en V2. JSON null/arrays, contratos parciales/extras y versiones
o hashes discordantes se rechazan. ORM mapea SQL NULL mediante none_as_null=True.

Lector puro read_eipd_review_context_metadata_v1 revalida metadata y correspondencia
con hashes del evento; historicos null retornan None sin inferir identidad. No cambia
salidas ni escritor de eventos HTTP: visibilidad API y prerequisitos siguen pendientes.
Mantiene RLS, FK de tenant y permisos runtime INSERT/SELECT; UPDATE/DELETE rechazados.
Ninguna revision V2 ni confirmacion/activacion habilitada.

Diecisiete casos PostgreSQL nuevos cubren nullabilidad/grants/RLS, roundtrip y
historia intacta, rechazo de modificaciones/borrado, once contratos invalidos y
cuatro intentos de saltar aislamiento (tenant/actor/padre/sin autenticacion).
445 pruebas aisladas aprobadas en 25.03 s, incluyendo regresiones de politica de
revision; Black/Ruff aprobados. Ejecutor protegido fija nuevo head d39e2b0f841c.
Suite HTTP general de licitud no repetida; ultima completa §147: 570 aprobadas.

Migracion validada/aplicada en base aislada y luego en base local cumpleia; destinos
local/development comprobados. Comparacion de registros antes/despues confirma
politica/publicaciones/selecciones/selector/eventos existentes identicos, sin metadata
sintetica. No se ejecuta downgrade ni se modifica migracion historica.
Proximo: exponer lectura API versionada de metadata y evaluar prerequisitos V2,
antes de permitir eventos. Ley fija; M3-T1 EN PROGRESO. Activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §152: lectura API de metadata de revision

Composicion V3 expone latest_review_context_metadata y estado separado sin_revision,
sin_metadatos, vigente u obsoleta. La consulta del ultimo evento retorna metadata
validada junto a evento/identidad de politica; wrapper historico conserva contrato
de dos valores. Una sola SELECT de historial; no busca identidad de eventos anteriores.
Metadata solo de salida, no agregada a entradas HTTP de decision humana.

Vigencia compara hashes del evento, documento y ContextV2 actuales, incluido research.
Historia sin metadata conserva null; evento reciente sin identidad no hereda metadata
anterior. Revision documental, politica y metadata son estados independientes. Ausencia
u obsolescencia agrega bloqueo explicito de confirmacion en V3; metadata vigente
no elimina bloques documentales, de fuentes, politica ni investigacion.

Seis casos HTTP/OpenAPI nuevos: sin evento, historico sin metadata, identidad vigente,
material cambiado con metadata obsoleta, ultima negativa sin fallback y contrato de
salida cerrado. Verifican una consulta de historial, ausencia de escrituras, expediente
y conteo de eventos intactos, frontera de tenant y revision V2 aun rechazada.
465 pruebas aisladas aprobadas en 39.62 s: focalizadas mas readiness V2/revisiones
historicas; Black/Ruff aprobados. Suite HTTP general de licitud no repetida; ultima
completa §147: 570 aprobadas. Sin migracion ni cambio operacional en este paso.

Proximo: prerequisitos puros de revision V2 con metadatos/cobertura explicitos antes
de conectar registro de decisiones; confirmacion y activacion permanecen bloqueadas.
Ley fija; M3-T1 EN PROGRESO. Sin commit/push.


## 2026-10-09 — M3-T1 §153: prerequisitos puros de revision V3

Nuevo eipd_review_v3 evalua decisiones sobre resolucion con binding V2 y ContextV2.
Negativas requiere_cambios/no_continuar exigen borrador, versiones admitidas,
RAT vigente y asociacion actual; no exigen completitud documental ni un evento
anterior. Metadata se genera desde material de servidor con cobertura contexto_v2,
research presente o null explicito; nunca se acepta en la solicitud humana.
Ausencia, binding historico y obsolescencia producen motivos separados y no identidad.

Continuar agrega review_blockers de composicion V3 sin exigir revision anterior.
Conserva barreras de investigacion, fuentes, politica y activacion. prerequisites_met
solo describe requisitos puros; can_confirm siempre false y no reemplaza permisos,
validacion de tenant/actor, politica real ni relectura bajo lock. No conecta acciones
HTTP ni inserta eventos; guardia V2 existente permanece bloqueada.

Doce casos nuevos: negativas parciales sin mutacion, positivo bloqueado sin circularidad,
seis cambios de estado/identidad, research null cubierto y entradas humanas cerradas.
560 pruebas aisladas aprobadas en 34.80 s, incluyendo prerequisitos V2 y revisiones
HTTP historicas; Black/Ruff aprobados. Suite HTTP general licitud no repetida;
ultima completa §147: 570 aprobadas. Sin migracion ni cambios de datos operacionales.

Proximo: integrar prerequisitos/metadata de servidor en registro controlado de
negativas V2, con locks, aislamiento y persistencia atomica; positivos, confirmacion
y activacion siguen bloqueados. Ley fija; M3-T1 EN PROGRESO. Sin commit/push.


## 2026-10-09 — M3-T1 §154: registro HTTP de negativas V2

Accion autenticada de revision permite requiere_cambios/no_continuar para resolucion
binding V2. Tras locks globales de politica/selector y serie, relee borrador/versiones,
reconstruye RAT/ContextV2 actuales y aplica prerequisitos V3. No repara asociaciones.
Evento persiste hashes, review_context_metadata generada por servidor, actor autenticado
e identidad de politica seleccionada deshabilitada en la misma transaccion.
Decision continuar V2 conserva 409 resolucion_eipd_v2_revision_pendiente; confirmacion
y activacion permanecen bloqueadas. Escritor V1 y contratos HTTP historicos intactos.

Ocho casos nuevos aislados: ambas negativas con research presente/null explicito,
dos eventos append-only independientes, metadata/hashes/cobertura/actor/politica,
readiness vigente con negativa bloqueante, tenant ajeno y metadata inyectada rechazados;
material research obsoleto, RAT desactualizado y estado confirmado sin evento;
fallo despues de flush revierte evento y metadata. Expediente permanece inalterado.
Fixture ordinaria incompleta rechaza confirmacion por 400 antes del guard EIPD;
regresiones documentales conservan comprobacion 409 para expedientes aplicables.

578 pruebas aisladas aprobadas en 41.89 s, incluyendo prerequisitos y registro HTTP
historicos V2; Black/Ruff aprobados. Suite HTTP general licitud no repetida;
ultima completa §147: 570 aprobadas. Sin migracion ni inserciones operacionales.

Proximo: comprobar concurrencia/relectura de negativas V2 frente a cambios del
expediente y de politica antes de ampliar consumidores. Positivos/confirmacion
siguen bloqueados; fuentes/aceptacion pendientes. Ley fija; M3-T1 EN PROGRESO.
Sin commit/push.


## 2026-10-09 — M3-T1 §155: concurrencia de negativas V2

Diez casos PostgreSQL reales con sesiones app_user independientes prueban espera
observable mediante pg_blocking_pids, sin temporizadores como evidencia de bloqueo.
PATCH de research sin reaporte, reaporte con documento nuevo y retirada se prueban
con commit/rollback: revision espera serie, relee material y genera identidad actual,
o rechaza obsolescencia/ausencia sin evento. Rollback conserva material anterior.

Cambio de selector previo bloquea revision hasta terminar y usa identidad real nueva
si commit o anterior si rollback. Cambio administrativo posterior espera hasta commit/
rollback de revision: evento solo visible tras commit; rollback no publica nada.
Historia conserva hashes/metadatos y politica original aunque selector cambie.
No se habilitan positivos ni confirmacion/activacion; no fue necesario cambiar escritor.
Limpieza de fixtures solo sobre datos sinteticos de la base aislada.

603 pruebas aisladas aprobadas en 46.31 s, incluidos locks compartidos y regresiones
HTTP/prerequisitos historicos. Black/Ruff y diff check aprobados. Suite HTTP general
licitud no repetida; ultima completa §147: 570 aprobadas. Sin migracion, cambio de
permisos ni datos operacionales. M3-T1 EN PROGRESO, Ley fija, fuentes/aceptacion pendientes.

Proximo: verificar negativas simultaneas sobre la misma serie y cancelacion durante
espera antes de ampliar consumidores. Sin commit/push.


## 2026-10-09 — M3-T1 §156: negativas simultaneas y cancelacion

Cuatro casos nuevos de PostgreSQL real amplian concurrencia V2. Dos negativas sobre
la misma serie esperan bloqueo observable y conservan eventos independientes con
igual identidad vigente: commit de primera conserva ambas; rollback conserva solo
segunda. Lectura del ultimo evento retorna segunda negativa y su metadata exacta.

Cancelacion de tarea durante espera de serie o politica usa cierre de sesion/transaccion
real. No persiste evento parcial. En espera de serie se prueba que administrador puede
adquirir bloqueo global exclusivo antes de liberar serie: shared lock de tarea cancelada
ya fue liberado. Reintento en sesion nueva usa documento/politica actuales y publica
exactamente un evento con metadata V2. No se cambian escritor, permisos ni contratos.

14 pruebas de concurrencia V2 aprobadas en 4.89 s; regresion ampliada: 607 pruebas
aisladas aprobadas en 51.50 s, incluidos registro HTTP historico y locks compartidos.
Black/Ruff y diff check aprobados. Suite HTTP general licitud no repetida;
ultima completa §147: 570 aprobadas. Sin migracion ni datos operacionales modificados.

Proximo: lectura de prerequisitos V3 de revision en readiness para explicar preparacion
por decision sin atribuir permiso ni habilitar positivos. M3-T1 EN PROGRESO; Ley fija,
fuentes/aceptacion pendientes, confirmacion/activacion bloqueadas. Sin commit/push.


## 2026-10-09 — M3-T1 §157: prerequisitos por decision en readiness

Salida cerrada V3 agrega review_prerequisites_v3 con claves continuar/requiere_cambios/
no_continuar, evaluation_version 3 y evaluation_scope requisitos_documentales.
Cada decision muestra prerequisites_met, identidad de material actual y motivos.
authorizes_action/can_confirm constantes false: diagnostico no valida permisos,
locks ni disponibilidad de accion. Metadata prospectiva se distingue de metadata
del ultimo evento historico; no crea ni simula una revision humana.

Evaluador puro extrae kernel de decision validada sin rationale/referencia ficticios;
escritor mantiene validacion humana EipdResolutionReviewIn y delega al mismo kernel.
Negativas pueden cumplir requisitos documentales aun sin politica seleccionada;
registro real conserva rechazo de politica ausente y controles transaccionales.
Continuar mantiene motivos comunes sin exigir evento anterior. Contratos V1/V2 intactos.

Cinco casos HTTP/OpenAPI nuevos: material vigente/obsoleto/ausente/historico, salida
cerrada y exclusiva de lectura; una SELECT de historial, sin escrituras ni eventos,
expediente intacto, tenant ajeno rechazado y parametros de autoridad ignorados.
Tres casos puros comprueban equivalencia diagnostico/solicitud humana por decision.
615 pruebas aisladas aprobadas en 53.47 s, Black/Ruff/diff check aprobados.
Suite HTTP general licitud no repetida; ultima completa §147: 570 aprobadas.
Sin migracion ni datos operacionales modificados. Capacidad expuesta por API,
interfaz de usuario no ampliada en este incremento.

Proximo: contrato de salida versionada de eventos V2 con metadata auditable, conservando
historia sin identidad inferida. M3-T1 EN PROGRESO; Ley fija, fuentes/aceptacion pendientes,
positivos/confirmacion/activacion bloqueados. Sin commit/push.
