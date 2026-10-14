# M3-T1 — Infancia y adolescencia: primer contrato documental

Estado: contrato, evaluador documental e identidad propios §§274–276, 2026-10-14. M3-T1 EN PROGRESO.
No campo API, persistencia, evaluador positivo ni cambio del fallback especial.
Solo pruebas ficticias hasta MVP; confirmacion/activacion EIPD bloqueadas.

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

## Secuencia restante

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
