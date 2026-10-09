# M3-T1 §136 — Asociaciones especiales/EIPD para investigacion

## Estado y alcance

Diseno de implementacion, 2026-10-09. Codigo inspeccionado en HEAD 9bc2d6b:
SpecialContextBindingV10 / bind_special_conditions_v10 y EipdContextBindingV11 /
bind_eipd_screening_v11 no incluyen research_assessment. Research binding V1 y
readiness §135 ya existen; investigacion_confirmacion_bloqueada aplica a documento
presente o regimen detectado. Este paso no agrega versiones al codigo ni abre gates.
Ley base fija; M3-T1 EN PROGRESO y activacion EIPD bloqueada.

## Nuevos contratos y material

Agregar SpecialContextBindingV11 y EipdContextBindingV12 a las uniones de salida,
con discriminacion por schema_version y campos cerrados. Mantener literalmente
contratos V1–V10 especiales y V1–V11 EIPD, hashes y funciones anteriores.
Inputs especiales/screening siguen documentales, sin binding de cliente. Research
mantiene BoundResearchAssessmentV1: no requiere cambiar su version ni migracion.

Funciones nuevas propuestas:
- build_special_context_binding_hash_v11 / bind_special_conditions_v11.
- build_eipd_context_binding_hash_v12 / bind_eipd_screening_v12.

Cada hash nuevo usa SHA-256 sobre JSON UTF-8, claves ordenadas, separadores compactos,
ensure_ascii=False, allow_nan=False; envelope domain/version/material explicitos.
Dominio especial cumpleia.special.research, version 11; dominio screening
cumpleia.eipd.screening.research, version 12. Material incluye previous_context_hash
(calculado por funcion V10 especial o V11 EIPD con todos sus argumentos originales)
y research_assessment: BoundResearchAssessmentV1 completo normalizado o null.
Screening nuevo incluye tambien legal_basis validada explicitamente: su funcion
anterior no recibe base como argumento directo. Asociacion nueva debe reaccionar
al cambio de base incluso sin expediente de investigacion ni documento especial.

Research completo significa assessment mas context_binding existente, no solo sus
hashes. Esto detecta cambios del contenido aunque alguien mantenga metadatos viejos.
Revalidar modelo antes de serializar; aceptar modelos o dict sin modificar originales.
No recalcular/reparar el binding de investigacion al generar asociaciones transversales:
puede estar estructuralmente valido pero obsoleto. Sus dos checks de vigencia siguen
independientes; nueva asociacion transversal no acredita completitud ni correccion.

## Compatibilidad y evaluacion

Dispatch explicito segun version persistida. Para versiones anteriores se conserva
el calculo anterior. Si hay investigacion aportada y binding especial menor a 11 o
screening menor a 12, emitir asociacion_investigacion_no_cubierta y revision; nunca
comparar el hash antiguo con el algoritmo nuevo ni promover su version en lectura.
Ese diagnostico debe coexistir con otros motivos de cobertura: no ocultar fallos
previos de biometria/excepciones mediante una rama excluyente nueva.

Antiguos sin expediente: evaluar como antes, sin actualizar hashes. Research null
es material explicito solo de nuevas versiones; no insertar null en hashes antiguos.
Version desconocida/contrato alterado se rechaza, sin fallback silencioso.
Regimen declarado sin expediente conserva deteccion y bloqueo actuales; una version
nueva con research null no acredita un expediente. La presencia de investigacion
sigue bloqueando confirmacion aun cuando las declaraciones especiales sean negativas.

## Orden de escritura y PATCH

En create o actualizacion final bajo el lock existente:
1. Recomponer RAT y aplicar base/LIA/documentos aportados.
2. Vincular investigacion solo si se aporta explicitamente; null retira; omision conserva.
3. Vincular condiciones especiales solo si se aportan explicitamente, usando nuevo V11.
4. Vincular screening solo si se aporta explicitamente, usando nuevo V12, con condiciones
   especiales finales y expediente de investigacion final.
5. Conservar el tratamiento actual de resolucion/revision EIPD y los bloqueos.

Cambio/retiro/reaporte de investigacion sin reaportar especiales/screening conserva
sus bindings antiguos, detectables como obsoletos o sin cobertura. Cambio conjunto
usa todos los valores finales; nunca la version anterior del expediente. Lecturas
GET/readiness no escriben. Confirmados/reemplazados permanecen inmutables.
Reaportar solo especiales no renueva screening. Reaportar solo screening no renueva
especiales ni investigacion. No backfill, migracion ni reparacion masiva.

## Frontera con resolucion/revision y aceptacion

ResolutionContextV1 materializa otros documentos sin research actualmente. Antes de
habilitar investigacion, revisar explicitamente version nueva de contexto de resolucion,
screening V2, composicion, politica y evidencia de confirmacion para evitar que una
revision historica sea reutilizada como aceptacion de investigacion. No alterar ese
contrato ni extender su semantica silenciosamente en este incremento de binding.
Las nuevas asociaciones por si solas no habilitan excepciones, revision humana ni
activacion EIPD. Mantener validador_no_implementado y el bloqueo transversal §135.

## Pruebas de aceptacion del proximo incremento

- Fixtures fijas de hashes anteriores intactas; viejos sin research compatibles.
- Nuevos hashes deterministas, material null vs objeto, document/body/binding/base/LIA
  y RAT modificados cambian identidad; funciones no mutan entrada.
- Modelos cerrados/version desconocida/hash de cliente rechazados; OpenAPI admite
  sucesores sin ampliar contratos anteriores.
- Binding viejo con research informa no cobertura; nuevo con research obsoleto sigue
  bloqueado; documento completo/asociaciones vigentes tampoco autoriza confirmar.
- HTTP create/PATCH aportes conjuntos/omision/null y orden final; GET/readiness sin
  escritura, inmutabilidad, aislamiento tenant y rollback de cambios invalidos.
- Suite ampliada aislada y Black/Ruff. Sin suite operacional ni cambios a registro EIPD.

## Secuencia acordada

Siguiente paso: contratos nuevos y funciones puras de hash/bind con compatibilidad
historica probada. Luego dispatch evaluador y servicio/API con pruebas HTTP. Solo
posteriormente revisar la frontera de resolucion/EIPD/aceptacion para investigacion.
Ultima validacion de codigo: 303 aprobadas §135; este paso solo documental no ejecuta
nueva suite. Sin commit/push ni cambios de datos/credenciales/politicas.

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
