# M3-T1 §140 — Cobertura de investigacion en resolucion y revision EIPD

## Hallazgo verificado

HEAD 03dd73a. EipdResolutionContextV1 cerrado contiene RAT, base y otros documentos,
pero no research_assessment. build_eipd_resolution_context_hash_v1 usa binding_version
1 y contexto normalizado; StoredV1 acepta binding V1 nullable. Revision vigente V1
compara contexto/documento y hashes del evento; no acredita investigacion ni permiso.
API genera especiales V11/screening V12, pero frontera/resolucion V1 no recibe research.
Ese limite sigue protegido por investigacion_confirmacion_bloqueada. Ley fija y
M3-T1 EN PROGRESO; activacion EIPD bloqueada.

## Contratos sucesores propuestos

Crear EipdResolutionContextV2 interno, cerrado, con todos los campos V1 y un campo
research_assessment obligatorio aunque sea null, tipo BoundResearchAssessmentV1.
Agregar context_schema_version Literal[2]=2 para identidad explicita de este contexto.
No ampliar V1 ni aceptar research como extra ignorado. Revalidar dict/modelos antes de
hash; conservar documento y binding research tal como fueron aportados, sin repararlos.

Crear EipdResolutionContextBindingV2 con binding_version Literal[2] y context_hash;
crear EipdResolutionAssessmentStoredV2 separado, manteniendo entrada documental
EipdResolutionAssessmentV1 sin hashes de cliente. La version documental del contenido
no cambia por cambiar su asociacion. No ampliar StoredV1 silenciosamente; salida
persistida admite ambas formas con dispatch explicito por binding_version. Conservar
historicos StoredV1 con binding null para diagnostico actual, sin completar metadatos.

Funciones nuevas: build_eipd_resolution_context_hash_v2, bind_eipd_resolution_v2,
eipd_resolution_context_is_current_v2 y hash documental V2. Hash de contexto usa
SHA-256 JSON UTF-8 ordenado/compacto, allow_nan=False, envelope domain
cumpleia.eipd.resolution.research, binding_version 2 y contexto V2 completo. Hash
nuevo documental usa dominio/version y StoredV2 normalizado completo. No modificar
funciones ni hashes anteriores. Cambios de cuerpo research con binding conservado,
retiro, base, LIA, RAT, especiales o screening cambian identidad V2.

## Compatibilidad y seleccion

Lecturas dispatch por binding persistido; V1 se compara con V1 y V2 con V2. Documento
V1 con investigacion aportada requiere diagnostico de cobertura pendiente aunque su
hash historico siga coincidiendo; nunca convertirlo a V2 o atribuirle investigacion.
V1 sin investigacion conserva calculo/comportamiento anterior.

Primer incremento V2 sera puro, sin escritura API. En integracion posterior, reaporte
explicito de resolucion con investigacion usa V2; borradores ordinarios sin expediente
ni historial V2 conservan V1. Documento ya V2 se compara con contexto V2 aun si
research se retira (null explicito), detectando obsolescencia; no degradar a V1 en
lectura/PATCH parcial. Definir y probar esta seleccion antes de conectarla al servicio.
Resolucion omitida conserva documento/binding; null retira; aporte conjunto respeta
orden RAT/base/LIA, research, especiales, screening y finalmente resolucion. Ningun
reaporte documental crea o reescribe decision humana. Confirmados/reemplazados
permanecen inmutables; locks/tenant/rollback existentes conservados.

## Revision humana y eventos

Evento previo siempre visible, independiente de vigencia. Para investigacion, evento
referido a documento V1 nunca acredita coverage V2: estado obsoleto o diagnostico
especifico de falta de cobertura, sin alterar evento. Revision V2 exige coincidencia
de contexto V2 y hash documental V2, evaluaciones research de completitud y asociacion,
RAT actual y asociaciones especiales/screening que cubran research. Un documento
completo y una revision vigente aun no habilitan gate ni politica excepcional.

La tabla de eventos actual almacena hashes, identidad, decision, autor y fecha. No
asumir una migracion nueva: revisar si la identidad de version puede derivarse sin
ambiguedad del documento hash/binding y los dominios nuevos; si se requiere columna
de version, agregarla nullable append-only sin backfill ni atribucion historica.
Decidir ese detalle antes del primer escritor V2; no reutilizar identidad de politica
como sustituto de la version del documento/contexto. Mantener hashes y eventos antiguos.

## Fronteras pendientes y secuencia

1. Contexto/binding/Stored V2 y funciones puras, fixtures V1 intactas, sin escritura.
2. Dispatch documental/readiness/revision con cobertura explicita; coexistencia de
   motivos y lectura de eventos historicos sin reinterpretacion.
3. Revision de screening V2/frontera/composicion y contratos sucesores necesarios,
   propagando research completo y base final. No pasar V2 a validadores V1 por quitar
   campos: cualquier proyeccion historica debe informar su falta de cobertura.
4. Integracion API bajo locks, seleccion de version documentada, pruebas HTTP/tenant
   y metadatos de eventos definidos; politica y evidencia de confirmacion revisadas.
5. Aceptacion revisada antes de considerar habilitacion. Mantener todos los bloqueos
   actuales hasta entonces; sin publicaciones/selecciones/activacion operacional.

## Validacion requerida

Regresiones fijas V1; contratos cerrados/version desconocida; V2 determinista y sin
mutacion; cambios/retiro research invalidan contexto y revision sin reparar hashes;
V1 con research nunca acredita V2; V1 sin research compatible; V2 null distinto de V1;
evento anterior visible pero sin autoridad sintetica. Posteriormente HTTP omision,
null/reaportes conjuntos, orden final, rollback, inmutabilidad, tenant y concurrencia.
Usar base aislada y runner protegido. Este paso es documental: ultima validacion
329 ampliadas y 162 regresiones §139, sin nueva suite ni migracion. Sin commit/push.

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
