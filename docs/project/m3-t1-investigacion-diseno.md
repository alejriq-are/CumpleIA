# M3-T1 — Preparacion documental de investigacion v1

Fecha: 2026-10-09. §128. Estado: DISENO PREPARADO; NO IMPLEMENTADO.
Base revisada: f9313a887437ed05df9dfced4b8d581838e3eee6.

## Alcance elegido

Siguiente incremento: expediente documental para investigacion_art16quinquies,
datos no sensibles y titulares adultos, asociado al alcance RAT y con la base
ordinaria de interes legitimo/LIA vigente. La restriccion inicial es de producto,
no una limitacion juridica general del articulo. Rutas sensibles, infancia y otros
regimenes pendientes seguiran derivando a revision; no abrir gates excepcionales.

Observacion de codigo: special_conditions.py evalua salud y biometria en ruta de
consentimiento; el regimen investigacion no tiene rama de validador y deriva a
validador_no_implementado. La representacion sensible tambien sigue pendiente.
No interpretar las matrices historicas como ausencia de todos los validadores.

## Fuente primaria y separacion del criterio de producto

Consultado texto de Ley 21.719 publicado por BCN/Ley Chile:
https://nuevo.leychile.cl/navegar?idNorma=1209272, articulo 16 quinquies.
La norma vincula este regimen a finalidades exclusivas de interes publico,
exige acreditar medidas de calidad/seguridad, agrega gestion de riesgos para datos
sensibles y establece anonimizar datos antes de publicar resultados. Permite
conservacion indeterminada bajo sus condiciones; el producto no la presume por
marcar una finalidad. Fuente consultada no equivale a aceptacion juridica del
expediente ni a verificacion de instrucciones complementarias de la Agencia.

Reutilizar LIA como condicion del primer incremento es una decision conservadora
de implementacion; no afirmar que un expediente LIA de este producto sea requisito
formal universal impuesto por el articulo. Ley fija sin condicionarla a fechas.

## Contrato propuesto y aplicabilidad

Nombre previsto ResearchAssessmentV1; schema cerrado extra=forbid, campos opcionales
en borrador. No modificar schemas historicos ni sus hashes. Reutilizar las
respuestas/evidencias documentales existentes para si/no/pendiente.

| Grupo | Datos del expediente | Completitud propuesta |
| --- | --- | --- |
| Finalidad | Tipo historico/estadistico/cientifico/estudio-investigacion, descripcion, analisis de interes publico | Obligatorios para preparar esta ruta |
| Exclusividad | Respuesta y analisis sobre uso exclusivo, controles frente a reutilizacion incompatible | Si requerido; no/pendiente impiden preparacion |
| Calidad y seguridad | Medidas, aplicacion efectiva declarada y evidencia referenciada | Analisis y evidencia presentes; no certificar eficacia real por existencia de campos |
| Difusion | Si/no/pendiente sobre publicacion de datos/resultados | Determina aplicabilidad del grupo de anonimizacion |
| Anonimizacion | Procedimiento, analisis y evidencia de medidas previas a publicar | Obligatorios si difusion=si; pendiente bloquea resolver aplicabilidad |
| Conservacion | Descripcion del criterio y condiciones documentales | No conceder plazo indefinido automaticamente |
| Alcance | Selectores de categorias y titulares vinculados al RAT | Subconjunto valido y cobertura conservadora completa del alcance inicial |

Difusion=no: grupo de anonimizacion no aplicable, conservando razonamiento. No
confundir seudonimizacion con anonimizacion. Documento fuera de regimen/alcance es
residual y requiere revision. Categorias sensibles o menores/vulnerabilidad no se
resuelven con este contrato inicial; mantener evaluaciones existentes de esas rutas.

## Integracion por pasos

1. Agregar schema y evaluador puro de completitud/aplicabilidad; sin persistencia,
   sin levantar validador_no_implementado en el evaluador especial ni confirmar.
2. Probar si/no/pendiente, campos/evidencias, difusion y alcance, datos sensibles,
   asociaciones residuales y coherencia con LIA; usar entorno de pruebas aislado.
3. Disenar version nueva de binding documental con tests de compatibilidad; no
   recalcular ni reinterpretar hashes historicos. Luego persistencia/migracion/API.
4. Integrar readiness especial y gate solo tras revisar coherencia con las seis
   bases, tenant/RLS, RAT vigente, EIPD y confirmacion/reemplazo/concurrencia.
5. Revisar criterios de aceptacion antes de declarar ruta preparada funcionalmente.

## Criterios de aceptacion del primer incremento

- Evaluador puro devuelve issues y aplicabilidad deterministas, sin efectos DB.
- Si/no/pendiente y ausencia documental nunca se interpretan como autorizacion.
- LIA/finalidad/alcance incompatibles requieren revision; no inventar autorizacion.
- Positivo documental no habilita confirmacion mientras integracion este pendiente.
- Pruebas de escritura solo mediante base aislada; no tocar selector EIPD revision 1.

Pendiente implementacion. M3-T1 EN PROGRESO; activacion EIPD bloqueada.

## 2026-10-09 — M3-T1 §129: contrato/evaluador puro de investigacion

Se agregan app/schemas/research.py (ResearchAssessmentV1 cerrado, borrador opcional,
revalidacion de instancias) y app/services/research.py. Evaluador puro reutiliza LIA,
canonizacion de finalidad y RAT; exige base interes_legitimo y cobertura completa
conservadora, deriva sensibles/menores/vulnerabilidad a revision. Completa finalidad,
interes publico, exclusividad, medidas/evidencia y conservacion. Difusion si exige
documentacion de anonimizacion; no la hace no aplicable y material residual requiere
revision; pendiente deja aplicabilidad sin resolver. No verifica eficacia material.

Resultado completo solo describe preparacion documental; can_confirm siempre false.
No integra persistencia/API/binding ni levanta validador_no_implementado especial.
Snapshots y hashes historicos intactos; sin migracion ni escrituras operacionales.
Pruebas nuevas: ausencia de campos, si/no/pendiente, difusion/material residual,
alcance, finalidad/base/LIA incompatible, sensibles/menores, schema cerrado,
revalidacion, determinismo y entradas sin cambios. Runner aislado ampliado para
incluir pruebas de investigacion; Black/Ruff aprobados. Suite aislada: 87 pruebas
aprobadas en 13.20 s (24 nuevas de investigacion y 63 previas). No nueva suite completa.

Proximo: ampliar casos de aplicabilidad y limites antes de diseñar binding nuevo e
integracion persistente. Ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §130: limites y aplicabilidad de investigacion probados

20 casos nuevos en test_services_research.py: difusion ausente/pendiente mantiene
anonimizacion sin resolver, evidencia con referencia/tipo vacios no acredita
preparacion, cada componente de anonimizacion requerido si se publica, RAT parcial
y selectores semanticamente duplicados requieren revision, adolescentes/vulnerables/
sensibilidad declarada no evaden limites iniciales, expediente/snapshot ausentes y
respuestas sin razonamiento impiden completo. No fue necesario cambiar evaluador.

Suite via ejecutor aislado: 107 aprobadas en 13.05 s (44 investigacion, 63 previas).
Black/Ruff aprobados. Sin escritura operacional, cambios legales ni politicas;
can_confirm sigue false, sin persistencia/API/binding ni integracion especial.

Proximo: implementar identidad/binding documental nuevo y probar cambios de
finalidad, RAT, LIA y expediente; conservar schemas y hashes historicos. No inferir
asociacion vigente a partir de completitud. Ley fija, M3-T1 EN PROGRESO y activacion
EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §131: asociacion nueva de investigacion

ResearchContextBindingV1 y BoundResearchAssessmentV1 son contratos cerrados nuevos,
independientes de SpecialContextBinding historico. research_binding.py calcula
SHA-256 con dominio/version explicitos: contexto incluye RAT completo/base/LIA;
documento incluye expediente completo. JSON ordenado por claves; orden de listas y
textos conservado deliberadamente (comparacion conservadora, sin prometer equivalencia
semantica). Bind revalida y devuelve copia; chequeo no actualiza hashes automaticamente.

Cambios RAT/finalidad/base/LIA producen asociacion_contexto_obsoleta; cambios de
expediente producen asociacion_documento_obsoleta. Ausencia requiere revision;
contrato historico/version desconocida no se convierte silenciosamente. Asociacion
vigente no acredita completitud/autoridad; can_confirm sigue false. Sin migracion,
API, persistencia ni cambios de bindings/hashes historicos.

La primera ejecucion detecto error previo de catalogo: evaluador research usaba
interes_legitimo abreviado. Corregido a interes_legitimo_art13d, igual que LegalBasis;
pruebas actualizadas y regresion rechaza el alias. Suite final aislada: 119 aprobadas
en 10.04 s (11 asociacion, 45 evaluador investigacion y 63 previas). Black/Ruff
aprobados. Sin escrituras operacionales ni cambio de selector EIPD.

Proximo: diseñar persistencia/API y versiones de asociacion especiales/EIPD para
incorporar investigacion sin reinterpretar historicos. Ley fija, M3-T1 EN PROGRESO,
confirmacion de investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §132: persistencia/API de investigacion delimitadas

Plan concreto en docs/project/m3-t1-investigacion-integracion.md: columna JSONB
nullable sin backfill, input documental/output con binding de servidor, contratos
sin ciclos de importacion y semantica PATCH omision/null/reaporte. Contexto cambiado
sin reaporte conserva binding y debe marcar obsolescencia. Historicos no reciben
hash nuevo automaticamente; protecciones tenant/inmutabilidad y gates preservados.

Orden: schema/modelo/migracion, luego servicios/API, readiness y finalmente nuevas
versiones especiales/EIPD con aceptacion. Sin cambios de codigo ni migracion aplicada,
no nueva suite; ultima focalizada 119 §131. Siguiente implementar primer incremento
persistente de schema/modelo/migracion en base aislada. Ley fija, M3-T1 EN PROGRESO,
confirmacion de investigacion y activacion EIPD bloqueadas. Sin commit/push.

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
