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
