# M3-T1 — Infancia y adolescencia: primer contrato documental

Estado: diseño y contrato interno §274, 2026-10-14. M3-T1 EN PROGRESO.
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
