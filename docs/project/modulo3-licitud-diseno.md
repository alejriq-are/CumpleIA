# Módulo 3 — Bases de licitud
## M3-T0 — Descubrimiento y diseño conceptual

**Fecha:** 2026-09-22  
**Estado:** En diseño  
**Rama:** `feature/m3-t0-licitud-discovery`

## 1. Objetivo

Diseñar el Módulo 3 de CumpleIA para determinar, justificar y confirmar
la base de licitud aplicable a cada finalidad de una actividad de tratamiento
registrada en el RAT, conforme a la Ley N° 21.719.

M3 consume el contexto factual mantenido por M2 y no duplica la lógica del RAT.

## 2. Fuentes consideradas

Fuentes chilenas:

- Ley N° 21.719, especialmente:
  - principios de licitud, finalidad y proporcionalidad;
  - artículo 12: consentimiento;
  - artículo 13: otras fuentes de licitud;
  - artículo 15 ter: evaluación de impacto;
  - artículos 16 y siguientes: datos sensibles y categorías especiales.
- Material CCS incorporado al repositorio.

Referencias comparadas de privacidad europea / RGPD aportadas al proyecto:

- `RAT.md`
- `LIA.xlsx` / `LIA.md`
- `CONSENTIMIENTO.md`

Estas referencias europeas se utilizan como insumo de estructura y UX.
Las reglas jurídicas de CumpleIA deben derivarse de la normativa chilena.

## 3. Punto de partida técnico

Existe scaffolding de Fase 0:

- enum `LegalBasis`;
- tabla/modelo `LegalBase`;
- vínculo actual únicamente con `treatment_id`;
- campos `basis`, `justification`, `confidence`, `approved`, `lia`;
- RLS por `organization_id`;
- FK tenant-safe agregada en M2-T1.

No existen actualmente:

- service M3;
- endpoints M3;
- frontend M3;
- tests funcionales M3;
- dependencia funcional conocida del modelo `LegalBase`.

Por lo tanto, el scaffolding puede rediseñarse en M3-T1.

## 4. Decisión: unidad jurídica de evaluación

La unidad de evaluación de licitud será la **finalidad** (`TreatmentPurpose`),
no únicamente el tratamiento completo.

Motivo:

- un tratamiento puede tener varias finalidades;
- distintas finalidades pueden requerir bases de licitud distintas;
- la Ley exige fines específicos, explícitos y lícitos;
- la necesidad y proporcionalidad del tratamiento se evalúan respecto de la finalidad.

Modelo conceptual:

`Treatment -> TreatmentPurpose -> LegalAssessment`

`Treatment` permanece como contenedor factual del RAT.

## 5. Alcance de datos por finalidad

Actualmente M2 conoce:

- finalidades;
- categorías de datos;
- categorías de titulares;

pero no existe relación entre una finalidad determinada y las categorías
de datos o titulares utilizados específicamente para esa finalidad.

M3 necesita ese alcance para evaluar correctamente:

- necesidad;
- proporcionalidad;
- datos sensibles;
- niños, niñas o adolescentes;
- grupos vulnerables;
- condiciones especiales de tratamiento.

Se incorporará una relación explícita entre finalidad y las categorías
de datos/titulares que participan en ella.

Esta relación es factual y no constituye por sí misma una decisión jurídica.

La incorporación de este detalle **no modifica el actual 10/10 de preparación
del RAT de M2**. Será parte de la preparación requerida para completar M3.

Los nombres físicos de las tablas se decidirán en M3-T1.

## 6. Catálogo chileno de bases generales

El enum inicial:

- consentimiento
- contrato
- obligacion_legal
- interes_legitimo
- otra

es insuficiente como catálogo final.

El diseño M3 debe representar de forma explícita, como mínimo:

1. consentimiento;
2. obligaciones económicas, financieras, bancarias o comerciales
   bajo el régimen legal aplicable;
3. obligación legal o tratamiento dispuesto por ley;
4. celebración o ejecución de contrato y medidas precontractuales;
5. interés legítimo del responsable o de un tercero;
6. formulación, ejercicio o defensa de derechos ante tribunales
   u órganos públicos.

No se copiarán automáticamente las bases del artículo 6 RGPD.

La necesidad de una categoría residual deberá justificarse antes de conservar
un valor genérico equivalente a `otra`.

## 7. Consentimiento

Cuando la base seleccionada sea consentimiento, M3 debe incorporar
una evaluación estructurada inspirada en `CONSENTIMIENTO.md`, adaptada
íntegramente a la Ley N° 21.719.

Debe permitir documentar al menos:

- libertad;
- información;
- especificidad respecto de la finalidad;
- carácter previo;
- manifestación inequívoca / acción afirmativa;
- mecanismo de otorgamiento;
- posibilidad y mecanismo de revocación;
- capacidad del responsable para acreditar el consentimiento.

El resultado no será una certificación jurídica automática.

## 8. Interés legítimo — LIA

Cuando la base seleccionada sea interés legítimo, M3 incorporará
una Evaluación de Interés Legítimo (LIA).

La estructura de la plantilla Seifti se utilizará como referencia de UX:

- finalidad e interés perseguido;
- necesidad;
- proporcionalidad;
- naturaleza y alcance de los datos;
- expectativas razonables del titular;
- impacto probable;
- salvaguardas;
- conclusión.

La LIA de CumpleIA será una herramienta de documentación y responsabilidad
demostrable adaptada al derecho chileno; no se presentará como un formulario
legal obligatorio denominado expresamente por la Ley N° 21.719.

## 9. Datos sensibles y condiciones especiales

La existencia de datos sensibles no se modelará como una nueva base general.

M3 deberá distinguir:

- base general de licitud de la finalidad;
- condición o autorización especial aplicable al tratamiento
  de datos sensibles.

La regla general del artículo 16 exige consentimiento expreso,
sin perjuicio de las excepciones legales específicas.

Las condiciones especiales deberán quedar documentadas
separadamente de la base general.

## 10. Evaluación de impacto

M3 deberá detectar situaciones en que la Ley N° 21.719 indique
la necesidad de una Evaluación de Impacto en Protección de Datos.

En esta etapa:

- M3 puede generar un indicador `requiere_eipd`;
- debe explicar el motivo;
- no implementará todavía el workflow completo de EIPD salvo decisión
  posterior del roadmap.

## 11. Estado y confirmación

El campo legacy `approved: bool` no se considerará suficiente
como modelo objetivo.

El diseño deberá distinguir:

- evaluación incompleta;
- evaluación preparada para revisión;
- decisión confirmada por la organización.

CumpleIA puede asistir o sugerir una base, pero una sugerencia automática
no equivale a una aprobación jurídica.

El campo legacy `confidence` tampoco será fuente de verdad jurídica.
Si se reutiliza, será únicamente metadata de una recomendación automática.

## 12. Frontera M2 / M3 / M5

M2:
- mantiene hechos del tratamiento.

M3:
- determina y documenta bases de licitud;
- consentimiento;
- interés legítimo;
- condiciones especiales;
- alertas jurídicas derivadas.

M5:
- conservará el expediente probatorio, versiones y evidencias inmutables.

## 13. Cierre de M3-T0

### 13.1 Decisiones resueltas

M3-T0 deja resueltas las decisiones de diseño necesarias para iniciar M3-T1:

- modelo de evaluación por finalidad;
- estrategia de serie estable y versiones históricas;
- cardinalidad de borradores y confirmaciones;
- estrategia de revisión cuando cambia el RAT;
- alcance finalidad → datos/titulares mediante snapshot versionado;
- catálogo inicial de bases de licitud chilenas;
- separación entre base general y condiciones especiales;
- tratamiento de datos sensibles y otros regímenes especiales;
- reglas conceptuales para niños, niñas y adolescentes;
- estados persistidos y condiciones derivadas del workflow;
- checklist versionado de consentimiento;
- LIA versionada adaptada al marco chileno;
- integración con M2 sin modificar su actual regla de activación 10/10;
- snapshot y `rat_context_hash`;
- criterios de detección de cambios relevantes;
- relación entre LIA y eventual EIPD;
- modelo físico preliminar y reglas de aislamiento tenant.

### 13.2 Decisiones diferidas explícitamente a M3-T1

Quedan para implementación y detalle técnico en M3-T1:

- nombres físicos definitivos de tablas y columnas;
- enums y constraints concretos;
- schemas Pydantic definitivos;
- algoritmo concreto de canonización y hash;
- composición exacta del snapshot desde los modelos operativos de M2;
- reglas programáticas de validación por base y régimen especial;
- índices físicos definitivos;
- migración Alembic;
- modelos SQLAlchemy;
- servicios y tests de persistencia/RLS.

Estas materias no bloquean el cierre de discovery porque sus decisiones
arquitectónicas ya están documentadas.

### 13.3 Criterios de cierre de M3-T0

M3-T0 se considerará cerrado cuando:

- exista un documento único de diseño con las decisiones anteriores;
- no queden decisiones funcionales o jurídicas esenciales sin resolver
  para comenzar persistencia;
- los puntos diferidos estén identificados explícitamente como trabajo M3-T1;
- no se haya modificado el comportamiento funcional de M2;
- `git diff --check` no reporte errores;
- el documento sea incorporado al repositorio mediante un commit de checkpoint.

Cumplidos estos criterios, el siguiente trabajo será **M3-T1 — Persistencia,
migración, modelos y RLS del módulo de Bases de Licitud**.

## 14. Persistencia histórica y vínculo con el RAT

### 14.1 Identificadores de M2 no son identidad histórica

Las colecciones normalizadas de M2 actualmente utilizan semántica de
reemplazo completo (`replace`):

- finalidades;
- categorías de datos;
- categorías de titulares;
- y otras colecciones normalizadas del RAT.

Al guardar estas colecciones, las filas pueden eliminarse y recrearse aunque
el valor lógico no haya cambiado.

Por lo tanto, los UUID de estas filas son identificadores técnicos del estado
actual y **no deben utilizarse como identidad histórica de una evaluación M3**.

M3 no dependerá de FKs históricas hacia estas filas para conservar decisiones
jurídicas confirmadas.

### 14.2 Snapshot del contexto RAT

Cada versión de una evaluación M3 conservará el contexto factual utilizado
para tomar la decisión.

Conceptualmente:

`Treatment -> LegalAssessment(version) -> RAT context snapshot`

El snapshot deberá contener, como mínimo:

- finalidad evaluada;
- códigos de categorías de datos incluidas;
- códigos de categorías de titulares incluidas;
- indicadores relevantes de sensibilidad;
- presencia de niños, niñas, adolescentes o grupos vulnerables;
- demás hechos del RAT necesarios para la evaluación concreta.

Los nombres físicos y el detalle del schema se definirán en M3-T1.

### 14.3 Fingerprint del contexto

La evaluación almacenará un fingerprint determinístico del contexto RAT
relevante, denominado conceptualmente `rat_context_hash`.

El hash deberá calcularse sobre una representación canónica independiente
de los UUID técnicos recreados por M2.

Por ejemplo, deberá utilizar valores lógicos ordenados como:

- texto normalizado de la finalidad;
- `category_code` de las categorías de datos;
- `category_code` de los titulares;
- flags jurídicamente relevantes.

Un guardado del RAT que recree filas sin cambiar su contenido no debe generar
falsamente una necesidad de revisión.

### 14.4 Cambios posteriores en el RAT

Cuando el contexto actual de una finalidad difiera del snapshot utilizado
para la última evaluación confirmada:

- la evaluación histórica no se elimina;
- la decisión confirmada no se modifica silenciosamente;
- M3 muestra que la finalidad **requiere revisión**;
- se podrá crear una nueva versión en estado `borrador`.

Cuando la nueva versión sea confirmada:

- la versión confirmada anterior pasa a `reemplazado`;
- la nueva versión pasa a `confirmado`.

### 14.5 Estado persistido y condición derivada

Estados persistidos propuestos:

- `borrador`;
- `confirmado`;
- `reemplazado`.

La condición `requiere revisión` no será necesariamente un estado persistido.
Puede derivarse comparando el `rat_context_hash` de la última versión confirmada
con el contexto actual del RAT.

Esto permite distinguir entre:

- la última decisión jurídica efectivamente confirmada por la organización; y
- si esa decisión continúa alineada con el RAT vigente.

### 14.6 Impacto sobre M2

Esta decisión:

- no cambia los 10 requisitos actuales de preparación del RAT;
- no modifica el contador 10/10;
- no requiere reabrir M2-T3.8;
- no obliga a convertir las colecciones M2 en entidades históricas;
- mantiene la frontera M2/M3 ya definida.

M2 representa el estado factual actual.

M3 conserva versiones de las decisiones jurídicas tomadas utilizando snapshots
de ese estado factual.


## 15. Catálogo canónico de bases de licitud

### 15.1 Bases generales

Para tratamientos ordinarios, M3 utilizará un catálogo explícito alineado
con los artículos 12 y 13 de la Ley N° 21.719.

Códigos conceptuales propuestos:

- `consentimiento_art12`
- `obligaciones_economicas_art13a`
- `obligacion_legal_art13b`
- `contrato_precontractual_art13c`
- `interes_legitimo_art13d`
- `defensa_derechos_art13e`

El valor legacy `otra` no formará parte inicialmente del catálogo operativo.

Si aparece un supuesto que no encaje en este catálogo, deberá revisarse
jurídicamente antes de introducir una categoría residual que pueda ocultar
una clasificación incorrecta.

### 15.2 Separación entre base general y condición especial

La existencia de datos sensibles no se resolverá creando nuevas bases
generales dentro del mismo enum.

M3 distinguirá conceptualmente:

- `legal_basis`: fundamento general del tratamiento, cuando corresponda;
- `special_condition`: condición especial aplicable a categorías sensibles
  o especialmente protegidas.

Esta separación es una decisión de diseño de CumpleIA para documentar
correctamente los distintos niveles de autorización previstos en la ley.

No debe interpretarse como que toda excepción especial del artículo 16
requiere necesariamente una segunda base independiente del artículo 13.

### 15.3 Condiciones generales para datos sensibles

Para datos personales sensibles, el catálogo especial deberá poder representar
al menos:

- `consentimiento_expreso_art16`
- `datos_manifiestamente_publicos_art16a`
- `interes_legitimo_entidad_sin_fines_lucro_art16b`
- `vida_salud_integridad_impedimento_art16c`
- `defensa_derechos_art16d`
- `laboral_seguridad_social_art16e`
- `autorizacion_legal_art16f`

Estas condiciones se evaluarán sólo cuando el alcance de la finalidad incluya
datos sensibles.

### 15.4 Regímenes especiales adicionales

M3 deberá detectar además categorías que tienen reglas específicas adicionales,
entre ellas:

- datos de salud y perfil biológico;
- datos biométricos;
- datos de niños, niñas y adolescentes;
- datos sensibles de adolescentes menores de dieciséis años;
- tratamientos históricos, estadísticos, científicos o de investigación;
- geolocalización.

Estas reglas no se incorporarán indiscriminadamente al enum general de bases.

Se modelarán como condiciones, validaciones o alertas adicionales según
corresponda a cada caso.

### 15.5 Consecuencia para el enum legacy

El enum actual:

- consentimiento
- contrato
- obligacion_legal
- interes_legitimo
- otra

se considera scaffolding incompleto.

M3-T1 podrá reemplazarlo por un catálogo explícito sin necesidad de mantener
compatibilidad funcional con endpoints existentes, ya que M3 aún no posee
API ni flujo productivo.


### 15.6 Detección estructurada de condiciones especiales v1

Referencia: [texto oficial BCN de Ley 21.719](https://www.bcn.cl/leychile/navegar?idNorma=1209272),
artículos 16 a 16 sexies del régimen previsto para diciembre de 2026.
La revisión distingue datos sensibles, salud/perfil biológico, identificación
biométrica, infancia/adolescencia, finalidades de investigación y geolocalización.
Estos grupos no se tratarán como autorizaciones intercambiables. Los hechos,
las condiciones seleccionadas y su revisión documental se mantendrán separados.

Las declaraciones se limitarán al alcance de la finalidad evaluada, no a todos
los datos de la organización. Identificadores estables del primer contrato:

- `datos_sensibles`;
- `salud_perfil_biologico`;
- `biometricos_identificacion_unica`;
- `ninos_ninas`;
- `adolescentes`;
- `datos_sensibles_adolescentes_menores_16`;
- `fines_historicos_estadisticos_cientificos_investigacion`;
- `geolocalizacion`;
- `grupos_vulnerables`.

Cada declaración tendrá `question_id`, `answer = si | no | pendiente`,
`rationale` opcional en borrador y listas opcionales `data_category_codes` y
`data_subject_codes` que precisan el subconjunto afectado. Los códigos deben
existir en el alcance del snapshot; no son UUID operacionales ni se infiere su
significado jurídico. No se aceptarán códigos vacíos/duplicados, preguntas
repetidas ni `no_aplica`. Para resolver la detección deben estar las nueve
preguntas con `si`/`no` y fundamento no vacío.

Las declaraciones complementan los hechos RAT; no los sobrescriben. Se
compararán `datos_sensibles`, `ninos_ninas`, `adolescentes` y `grupos_vulnerables`
con sus indicadores estructurados del snapshot. Una discordancia produce
revisión del contexto/declaración y no se resuelve automáticamente.
Salud o biometría afirmativas con `has_sensitive_data = false` también exigen
revisión de la clasificación, sin corregir silenciosamente M2.

Una afirmativa sobre datos sensibles de adolescentes menores de 16 requiere
que el snapshot incluya adolescentes y datos sensibles, además de justificar
la edad y su asociación al subconjunto declarado. La presencia conjunta de los
dos indicadores RAT no demuestra ese cruce: una negativa no se contradice
únicamente por coexistir ambos. No se recopilan fechas de nacimiento de personas
ni se infiere edad desde nombres de categorías.

Una respuesta afirmativa activa revisión del régimen correspondiente. Los
regímenes pueden coexistir; no se elige uno para suprimir los demás. La
vulnerabilidad actúa como factor de revisión y no como una autorización especial
inventada. Las preguntas sobre investigación y geolocalización se responden
explícitamente, sin inferirlas desde finalidad, sistemas, fuentes o prosa libre.

### 15.7 Contrato documental SpecialConditionsV1

Se usará la columna existente `legal_assessments.special_conditions` como
expediente versionado, independiente del screening EIPD. Contrato físico:

- `schema_version`: entero literal `1`;
- `declarations`: lista de declaraciones de §15.6, inicialmente vacía;
- `conditions`: lista de expedientes por régimen, inicialmente vacía;
- `notes`: texto opcional;
- `context_binding`: asociación documental calculada por servidor.

Cada expediente de `conditions` contendrá:

- `regime_id`: `sensibles_art16 | salud_perfil_biologico_art16bis |
  biometricos_art16ter | infancia_adolescencia_art16quater |
  investigacion_art16quinquies | geolocalizacion_art16sexies`;
- `authorization_route`: `consentimiento | excepcion_legal | regla_especifica`
  o `null` en borrador; documenta una ruta propuesta, sin aprobarla;
- `sensitive_condition_id`: uno de los siete identificadores de §15.3 o `null`;
  solo se admite en `sensibles_art16`, no se aplica como permiso genérico a
  salud/biometría u otros regímenes;
- `legal_reference`: referencia jurídica documental opcional;
- `documentary_analysis`: análisis opcional en borrador;
- `uses_consent_assessment`: `true | false | null`, referencia al expediente
  de consentimiento de esta misma evaluación, sin copiarlo ni enlazar UUID externo;
- `data_category_codes` y `data_subject_codes`: listas que precisan alcance;
- `evidence`: metadata documental con `evidence_type`, `reference`,
  `obtained_on` factual, `mechanism` y `notes`, sin integración M5;
- `notes`: observaciones opcionales.

Un `regime_id` no podrá repetirse en v1; subconjuntos con rutas incompatibles
requerirán revisión de la separación de finalidades, no entradas ambiguas.
Los códigos se validarán contra el alcance RAT de la evaluación. Una condición
para un régimen no detectado se conservará pero se marcará para revisión.
Campos, regímenes, condiciones y versiones desconocidos se rechazarán;
no habrá un diccionario libre de respuestas que simule requisitos implementados.

Este contrato permite documentar borradores, pero no declara implementados los
requisitos específicos de ninguna ruta. La matriz de validadores se registrará
por `regime_id` y ruta. Inicialmente todos estarán como **no implementados**;
la salida derivada expondrá esa barrera, sin aceptar un estado aportado por el
cliente. Los cuestionarios concretos y sus requisitos se incorporarán mediante
una decisión explícita de versionado antes de habilitar una ruta.

### 15.8 Preparación, asociación y dependencia con EIPD

La entrada `SpecialConditionsDraftIn` contendrá únicamente versión,
declaraciones, condiciones y notas. El servidor calculará `context_binding`
con versión literal `1` y hash SHA-256 de JSON determinista sobre:
`rat_context_snapshot`, `legal_basis`, `consent_assessment` y `lia_assessment`
con sus valores finales serializados o null cuando corresponda. Se preservarán
valores factuales y orden de listas, con claves ordenadas, separadores compactos,
Unicode sin escape ASCII y UTF-8. Esta asociación no modifica el hash RAT v1.

Omisión en PATCH conserva el expediente y su asociación; objeto reemplaza la
unidad y calcula asociación sobre el resultado final; null elimina el expediente
solo en borrador. Cambios de base, snapshot o cuestionarios sin reaportar el
expediente no lo reasocian: queda desactualizado. La entrada no admite asociación,
resultado ni validadores supuestamente aprobados por el cliente.

El evaluador de detección/preparación devolverá motivos y regímenes afectados:

- `incompleto`: expediente ausente, declaraciones/fundamentos sin resolver,
  códigos fuera de alcance o régimen activado sin expediente correspondiente;
- `requiere_revision`: asociación desactualizada, discordancias con RAT,
  condiciones residuales, referencias incoherentes a consentimiento o cualquier
  ruta cuyo validador específico no esté implementado;
- `sin_regimenes_declarados`: declaraciones completas, negativas, fundadas,
  coherentes con RAT, sin condiciones residuales y asociación vigente.

La precedencia será `incompleto > requiere_revision > sin_regimenes_declarados`,
conservando todos los motivos. Un expediente documental completo de un régimen
positivo continuará bloqueado mientras su validador sea no implementado.
No se introducirá un resultado `aprobado` o un bypass por comentario.

La relación con EIPD requiere evolucionar su asociación documental a
**context_binding.schema_version = 2** cuando se implemente este contrato:
el material será snapshot RAT completo, LIA y `special_conditions` finales.
El orden de guardado será base/cuestionarios, snapshot, condiciones especiales
y después screening EIPD. La asociación de condiciones no incluye EIPD y por
ello no hay un ciclo de hashes.

No se reescribirán asociaciones EIPD v1 existentes. Con condiciones especiales
no nulas, una asociación EIPD v1 no cubre este contexto: se devolverá revisión
y se requerirá reaportar el screening bajo la asociación v2. Los screenings v1
sin condiciones conservarán evaluación histórica conforme a su contrato; al
crear o reaportar screening con la nueva implementación se usará v2. El
cuestionario EIPD seguirá en schema_version 1; evoluciona solo su asociación.

También se comparará la declaración EIPD sobre excepción al consentimiento
con las rutas especiales documentadas. No se deducirá una excepción únicamente
a partir de legal_basis. Si hay una ruta pendiente/no validada, la preparación
mostrará esa incertidumbre y no una autorización resuelta.

### 15.9 Matriz y aceptación del primer bloque especial

| Régimen | Detección/alcance a documentar | Cobertura inicial |
| --- | --- | --- |
| Sensibles | Declaración y flag RAT; condición art16 propuesta | Guardado/detección, validación jurídica bloqueada |
| Salud/perfil biológico | Declaración, subconjunto y contexto de uso | Guardado/detección, reglas específicas pendientes |
| Biometría | Declaración de identificación única y subconjunto | Guardado/detección, información/requisitos específicos pendientes |
| Infancia/adolescencia | Indicadores RAT, edad pertinente y cruce con sensibles | Guardado/detección, autorización/requisitos específicos pendientes |
| Investigación | Declaración de finalidad y análisis documental | Guardado/detección, requisitos específicos pendientes |
| Geolocalización | Declaración y alcance documentado | Guardado/detección, información/requisitos específicos pendientes |
| Vulnerabilidad | Declaración y flag RAT | Factor de revisión, sin ruta de autorización especial |

Antes de implementar se cubrirán con pruebas: borradores parciales; campos,
regímenes y rutas desconocidos; duplicados; códigos ajenos al alcance; flags
RAT discordantes; cruce sensible/adolescente no inferido; varios regímenes;
rutas no implementadas; consentimiento referenciado pero ausente; omisión/null;
asociación especial desactualizada; EIPD v1 con condiciones nuevas; guardado
conjunto con asociación v2; conservación de históricos y consultas HTTP/RLS.

El primer bloque no desbloqueará condiciones positivas ni LIA. La habilitación
posterior exige validadores específicos, cobertura transversal EIPD y pruebas
transaccionales/concurrentes. Esta definición solo modifica documentación;
no añade modelos/código ni nuevas migraciones. Última suite backend:
**558 passed**. M3-T1 sigue en progreso.

## 16. Estrategia de persistencia: núcleo relacional + JSONB versionado

### 16.1 Decisión

M3 utilizará un modelo híbrido:

- columnas relacionales para identidad, estado, base de licitud,
  versionado, confirmación e integridad;
- JSONB versionado para estructuras de evaluación cuyo cuestionario
  pueda evolucionar.

No se crearán inicialmente tablas por cada pregunta o respuesta
de consentimiento o LIA.

Tampoco se almacenará toda la evaluación jurídica en un único JSONB.

### 16.2 Núcleo relacional conceptual

La entidad objetivo `LegalAssessment` deberá representar, como mínimo:

- `id`;
- `organization_id`;
- `treatment_id`;
- `version`;
- `status`;
- `legal_basis`;
- `justification`;
- snapshot identificable de la finalidad evaluada;
- `rat_context_hash`;
- versión del esquema de evaluación;
- fecha y actor de confirmación;
- auditoría de creación y modificación.

Los nombres físicos definitivos se fijarán en M3-T1.

### 16.3 Campos JSONB conceptuales

Se prevén al menos:

- `rat_context_snapshot`;
- `consent_assessment`;
- `lia_assessment`;
- `special_conditions`.

Los campos no aplicables serán `NULL`.

Ejemplos:

- si la base no es consentimiento, `consent_assessment` puede ser `NULL`;
- si la base no es interés legítimo, `lia_assessment` puede ser `NULL`;
- si el alcance no contiene categorías especiales,
  `special_conditions` puede ser `NULL`.

### 16.4 JSONB no significa estructura libre

Cada payload JSONB deberá:

- estar representado por schemas Pydantic explícitos;
- incluir o estar asociado a una versión de schema;
- ser validado antes de persistir;
- conservar la estructura histórica utilizada al confirmar la evaluación.

Cambiar el cuestionario futuro no debe reinterpretar silenciosamente
evaluaciones ya confirmadas.

### 16.5 Versionado de cuestionarios

Los cuestionarios de consentimiento, LIA y condiciones especiales
podrán evolucionar independientemente del schema físico de PostgreSQL.

Conceptualmente:

`consent_assessment.schema_version = 1`

`lia_assessment.schema_version = 1`

`special_conditions.schema_version = 1`

Una nueva versión de cuestionario podrá coexistir con evaluaciones históricas
creadas con una versión anterior.

### 16.6 Qué debe permanecer relacional

No deberán ocultarse dentro del JSONB los atributos operativos principales:

- base general seleccionada;
- estado de la evaluación;
- número de versión;
- tratamiento al que pertenece;
- justificación principal;
- fechas de confirmación;
- actor que confirma;
- fingerprint del contexto RAT.

Esto permitirá consultas, constraints, índices y auditoría sin depender
de consultas internas sobre JSON.

### 16.7 Campo legacy `lia`

El campo `legal_bases.lia` existente confirma que la arquitectura inicial
ya contemplaba una LIA semiestructurada.

M3-T1 podrá reemplazar ese scaffolding por los campos versionados del nuevo
modelo sin necesidad de mantener compatibilidad funcional con la columna
legacy, dado que M3 todavía no posee flujo productivo.


## 17. Checklist de consentimiento — schema v1

### 17.1 Principio de diseño

Cuando la base general seleccionada sea `consentimiento_art12`, M3 requerirá
una evaluación estructurada del consentimiento.

El checklist se basa jurídicamente en la Ley N° 21.719 y utiliza la plantilla
española `CONSENTIMIENTO.md` únicamente como referencia de estructura y UX.

El checklist no emitirá por sí solo una declaración de "cumplimiento legal".
Su función es ayudar a la organización a documentar los elementos necesarios
y detectar materias pendientes antes de confirmar la evaluación.

### 17.2 Estructura conceptual

`consent_assessment` será un JSONB validado por schema Pydantic y contendrá
conceptualmente:

- `schema_version`;
- `given_by`;
- `grant_method`;
- `answers`;
- `evidence`;
- `notes`.

Valores conceptuales de `given_by`:

- `titular`;
- `representante_legal`;
- `mandatario`.

Valores conceptuales de `grant_method`:

- `escrito`;
- `verbal`;
- `electronico`;
- `acto_afirmativo`;
- `otro_documentado`.

Los nombres físicos definitivos se fijarán en M3-T1.

### 17.3 Requisitos del artículo 12

El schema v1 deberá poder documentar explícitamente, al menos:

- consentimiento libre;
- consentimiento informado;
- consentimiento específico respecto de la finalidad evaluada;
- consentimiento previo al tratamiento;
- manifestación inequívoca de voluntad;
- existencia de declaración o acción afirmativa clara;
- mecanismo mediante el cual se obtiene;
- posibilidad real de revocación;
- uso de medios similares o equivalentes para revocar;
- carácter expedito del mecanismo de revocación;
- carácter fidedigno;
- gratuidad;
- disponibilidad permanente;
- capacidad del responsable para acreditar que obtuvo el consentimiento.

Si el consentimiento es otorgado por mandatario, deberá registrarse
si se verificó que cuenta expresamente con facultad para otorgarlo.

### 17.4 Contexto contractual o de prestación de servicios

El checklist deberá preguntar si el consentimiento se solicita dentro de:

- la ejecución de un contrato; o
- la prestación de un servicio.

Cuando corresponda, deberá documentar si la recolección o tratamiento para
el cual se pide consentimiento es realmente necesario para ese contrato
o servicio.

Esto permite detectar el supuesto en que la ley presume que el consentimiento
no fue otorgado libremente.

El sistema no decidirá automáticamente la validez jurídica del consentimiento;
marcará la situación para revisión cuando las respuestas generen dudas.

### 17.5 Preguntas auxiliares de UX

Inspirándose en `CONSENTIMIENTO.md`, CumpleIA podrá formular preguntas
auxiliares para facilitar la evaluación de libertad e información, por ejemplo:

- si existe presión o influencia indebida;
- si negarse produce consecuencias negativas;
- si finalidades diferentes se presentan separadamente;
- si la información entregada es clara y comprensible;
- si el usuario realiza una acción afirmativa real.

Estas preguntas auxiliares son herramientas de evaluación y no deben
presentarse como requisitos textuales adicionales de la Ley N° 21.719
cuando la ley no los formule expresamente.

### 17.6 Datos sensibles

Cuando el alcance incluya datos sensibles y la condición especial seleccionada
sea `consentimiento_expreso_art16`, el mismo expediente de consentimiento podrá
servir como evidencia, pero M3 deberá verificar adicionalmente que la
manifestación sea **expresa** y se haya otorgado mediante una declaración
escrita, verbal o por un medio tecnológico equivalente.

La condición especial se mantiene separada del campo `legal_basis`.

### 17.7 Evidencia

M3 deberá permitir registrar metadata que demuestre cómo se acredita
el consentimiento, sin implementar todavía el repositorio probatorio de M5.

Conceptualmente:

- tipo de evidencia;
- referencia o identificador;
- fecha de obtención, si se conoce;
- sistema o mecanismo utilizado;
- observaciones.

En M3 no se almacenarán necesariamente archivos probatorios definitivos.
M5 será responsable de su conservación y trazabilidad inmutable.

### 17.8 Resultado derivado

El checklist podrá calcular una condición operativa como:

- `completo`;
- `requiere_revision`;
- `incompleto`.

Este resultado será derivado de las respuestas y no equivaldrá a una
determinación jurídica automática.

La evaluación M3 sólo podrá pasar a `confirmado` mediante una acción explícita
del usuario autorizado.

### 17.9 Identificadores estables del checklist de consentimiento v1

El contrato físico v1 utilizará identificadores técnicos estables para las
preguntas cerradas del checklist. Estos identificadores no son texto jurídico
ni etiquetas de interfaz; permiten conservar el significado histórico aunque
la redacción visible cambie en el futuro.

Preguntas generales de consentimiento v1:

- `consentimiento_libre`;
- `consentimiento_informado`;
- `consentimiento_especifico_finalidad`;
- `consentimiento_previo`;
- `voluntad_inequivoca`;
- `accion_afirmativa_clara`;
- `revocacion_posible`;
- `revocacion_medio_equivalente`;
- `revocacion_expedita`;
- `revocacion_fidedigna`;
- `revocacion_gratuita`;
- `revocacion_disponible_permanentemente`;
- `responsable_puede_acreditar`;
- `contexto_contrato_servicio`, indica si el consentimiento se solicita dentro de la ejecución de un
  contrato o de la prestación de un servicio.

Preguntas condicionales v1:

- `mandatario_facultad_expresa`, aplicable cuando `given_by = mandatario`;
- `tratamiento_necesario_contrato_servicio`, aplicable cuando `contexto_contrato_servicio` tenga respuesta `si`.

Cada identificador utilizará la respuesta estructurada común
`si | no | no_aplica | pendiente` y un comentario opcional.

La condición operativa de completitud se derivará del conjunto de respuestas
y de las reglas de aplicabilidad. El identificador estable no implica por sí
solo que una respuesta determinada produzca automáticamente una conclusión
jurídica.

### 17.10 Contrato físico del checklist de consentimiento v1

El JSONB `consent_assessment` utilizará el siguiente contrato físico v1:

- `schema_version`: versión entera del contrato, inicialmente `1`;
- `given_by`: `titular | representante_legal | mandatario`;
- `grant_method`: `escrito | verbal | electronico | acto_afirmativo | otro_documentado`;
- `answers`: lista de respuestas estructuradas;
- `evidence`: lista de metadata documental de evidencia;
- `notes`: texto opcional.

Cada elemento de `answers` contendrá:

- `question_id`: uno de los identificadores estables definidos en §17.9;
- `answer`: `si | no | no_aplica | pendiente`;
- `comment`: texto opcional.

Un mismo `question_id` no podrá aparecer más de una vez dentro de una misma evaluación.
Mientras la evaluación permanezca en `borrador`, `given_by` y `grant_method` podrán permanecer en `null` y el contrato podrá conservar sólo un subconjunto de preguntas. La obligatoriedad de estos campos y la completitud del checklist se evaluarán al confirmar, según las reglas de aplicabilidad.

Cada elemento de `evidence` contendrá:

- `evidence_type`: texto que identifica el tipo de evidencia;
- `reference`: referencia o identificador opcional;
- `obtained_on`: fecha factual opcional de obtención, sin semántica de timestamp de sistema;
- `mechanism`: sistema o mecanismo utilizado, opcional;
- `notes`: observaciones opcionales.

Esta metadata pertenece al expediente documental M3 y no crea todavía una dependencia con `EvidenceEvent` de M5. Una integración futura con la bitácora de evidencia no deberá reinterpretar silenciosamente los JSONB históricos de consentimiento.

### 17.11 Aplicabilidad y completitud operativa del consentimiento v1

Las reglas siguientes fijan un control de preparación del expediente M3.
No constituyen una determinación automática de validez jurídica. Se ejecutarán
sobre el contrato validado `ConsentAssessmentV1`, sin modificar sus respuestas.

Para confirmar una evaluación con `legal_basis = consentimiento_art12`,
`consent_assessment` deberá existir, tener `schema_version = 1` y contener
`given_by` y `grant_method` no nulos.

Las 14 preguntas generales de §17.9 serán siempre aplicables. Cada una deberá
estar presente con respuesta `si` o `no`. Una pregunta general omitida, con
`pendiente` o con `no_aplica` hará que el checklist sea `incompleto`.
`contexto_contrato_servicio = no` será una respuesta resuelta, sin alerta por
sí misma; esa pregunta determina aplicabilidad y no exige respuesta afirmativa.

La aplicabilidad de las dos preguntas condicionales se resolverá así:

| Pregunta | Aplicable | No aplicable | Aplicabilidad sin resolver |
| --- | --- | --- | --- |
| `mandatario_facultad_expresa` | `given_by = mandatario` | `given_by = titular` o `representante_legal` | `given_by = null` |
| `tratamiento_necesario_contrato_servicio` | `contexto_contrato_servicio = si` | `contexto_contrato_servicio = no` | Pregunta general omitida, `pendiente` o `no_aplica` |

Una pregunta condicional aplicable deberá estar presente con respuesta `si`
o `no`; omisión, `pendiente` o `no_aplica` producirán `incompleto`.
Una pregunta condicional no aplicable podrá omitirse o responderse `no_aplica`.
Si conserva `si`, `no` o `pendiente`, se señalará una inconsistencia que requiere
revisión; no se borrará ni convertirá automáticamente la respuesta. Esto permite
detectar respuestas residuales cuando cambien los campos que determinan su
aplicabilidad.

Cuando la aplicabilidad no pueda resolverse, el resultado será `incompleto`,
aunque exista una respuesta para la pregunta condicional. Una respuesta
condicional no sustituye al dato que determina su aplicabilidad.

`comment`, `notes` y los campos opcionales de evidencia no serán obligatorios
para completar este checklist v1. Si se declara un elemento de `evidence`, su
`evidence_type` deberá contener texto no vacío tras ignorar espacios en los
extremos; una fecha aportada deberá ser válida según el contrato Pydantic.
No se impondrá un número mínimo de evidencias ni la presencia de `reference`
en este control. La cantidad de metadata no demuestra por sí sola la capacidad
de acreditar el consentimiento; esa cuestión se documenta mediante la respuesta
`responsable_puede_acreditar` y la revisión humana del expediente.

Las condiciones especiales de §17.6 se validarán separadamente cuando sean
aplicables. Completar este checklist no satisface automáticamente dichas
condiciones.

### 17.12 Resultado derivado y motivos v1

El evaluador devolverá un resultado operativo y motivos identificables,
sin persistirlos como un nuevo estado de la evaluación ni incorporarlos al
JSONB histórico de consentimiento.

Se aplicará esta precedencia:

1. `incompleto`: falta el expediente, `given_by` o `grant_method`; hay preguntas
   aplicables omitidas, pendientes o respondidas `no_aplica`; no puede resolverse
   una condición de aplicabilidad; o una evidencia declarada carece de tipo
   documental no vacío.
2. `requiere_revision`: no existen faltantes anteriores, pero una pregunta
   general distinta de `contexto_contrato_servicio` tiene respuesta `no`, una
   pregunta condicional aplicable tiene respuesta `no`, o una pregunta
   condicional no aplicable conserva una respuesta distinta de `no_aplica`.
3. `completo`: no existen faltantes ni motivos de revisión según estas reglas.

El evaluador conservará todos los motivos detectados, incluidos los de revisión
cuando el resultado agregado sea `incompleto`. La salida deberá identificar el
campo o `question_id` afectado, distinguir faltante de respuesta desfavorable y
exponer la aplicabilidad de ambas preguntas condicionales como
`aplicable | no_aplicable | sin_resolver`. Los motivos se ordenarán por campos
obligatorios, orden de preguntas de §17.9 y posición de evidencia, para obtener
una salida determinista independiente del orden de `answers`.

Un contrato inválido (versión no admitida, identificador desconocido, respuesta
fuera de catálogo, preguntas duplicadas o fecha inválida) se rechazará antes
de evaluar completitud. No se convertirá un error de estructura en un resultado
`completo` ni se descartarán entradas silenciosamente.

### 17.13 Puerta de confirmación y casos de aceptación v1

En el flujo v1, únicamente el resultado `completo` permitirá continuar la
confirmación explícita por un usuario autorizado. `incompleto` y
`requiere_revision` bloquearán esa transición y devolverán sus motivos.
No habrá un bypass mediante comentarios ni una confirmación forzada en v1.

El bloqueo es una política operativa de preparación de CumpleIA: no declara
jurídicamente inválido el consentimiento. El usuario podrá revisar y corregir
el borrador conservando la trazabilidad prevista para M3.

El resultado se recalculará dentro del flujo transaccional de §20.9 con el
payload vigente. Un resultado calculado anteriormente por la interfaz no será
fuente de autorización. También deberán superarse la revalidación del contexto
RAT y las demás validaciones de la evaluación; `completo` no confirma por sí
solo ni reemplaza una evaluación anterior.

Casos mínimos para la futura implementación:

| Caso | Resultado esperado |
| --- | --- |
| Expediente vacío o ausente | `incompleto` |
| Titular, método informado, 13 respuestas generales afirmativas y contexto contractual `no`; condicionales omitidas o `no_aplica` | `completo` |
| Mandatario con `mandatario_facultad_expresa` omitida o `no_aplica` | `incompleto` |
| Mandatario con facultad expresa `no` y resto resuelto favorablemente | `requiere_revision` |
| Contexto contractual `si` y necesidad omitida o `pendiente` | `incompleto` |
| Contexto contractual `si`, necesidad `no` y resto resuelto favorablemente | `requiere_revision` |
| Contexto contractual `no` y necesidad conserva `si` | `requiere_revision` |
| Pregunta general con `no_aplica` | `incompleto` |
| Una pregunta general desfavorable y otra pendiente | `incompleto`, conservando ambos motivos |
| Evidencia declarada con tipo vacío o solo espacios | `incompleto` |
| Mismas respuestas en distinto orden | Mismo resultado, aplicabilidad y orden de motivos |

El evaluador puro `evaluate_consent_assessment_v1` está implementado en
`backend/app/services/consentimiento.py`, con resultados y motivos inmutables,
revalidación estructural de entrada y sin escrituras de persistencia.
`ConsentReadinessV1.can_confirm` expresa únicamente la habilitación de este
control; no ejecuta ni autoriza por sí solo la transición de estado.

La validación específica comprende 40 casos nuevos de consentimiento y
136 pruebas aprobadas junto con los contratos y servicios M3 existentes.
Formato, lint y comprobación de whitespace pasan para este bloque.
No se ejecutó la suite completa backend en este paso.

El service layer incorpora `confirm_legal_assessment_v1` para consentimiento
ordinario v1: bloquea la serie, relee el estado y payload del borrador después
del bloqueo, evalúa el consentimiento vigente, exige justificación y alcance,
recompone el contexto RAT y rechaza un hash distinto. El snapshot documental
persistido se conserva; un cambio semántico exige revisar y actualizar el
borrador antes de confirmar.

La función reemplaza la evaluación anterior y confirma la sucesora con actor
y fecha en la misma transacción. Hace flush del reemplazo antes de confirmar
para respetar el índice parcial de una única evaluación confirmada. No hace
commit ni rollback: el caller debe cerrar la unidad de trabajo y revertirla
completamente ante un error. El caller también debe validar los permisos del
usuario y el acceso al tenant. La API inicial de §17.14 invoca esta función con los controles del caller.

Creación y actualización de borradores admiten `consent_assessment`, validado
con el contrato v1 y serializado en modo JSON para preservar fechas compatibles
con JSONB. En una actualización, omitir el campo conserva su valor y `null`
lo elimina. El checklist se reemplaza como unidad, sin fusionar respuestas.

Hasta implementar las demás reglas de M3, la confirmación rechaza otras bases,
versiones de contrato no admitidas, cualquier indicador de régimen especial
activo y cualquier payload `special_conditions` no nulo. Esta barrera expresa
una limitación de implementación, no una conclusión jurídica sobre esos casos.

Validación inicial de la integración: suite completa backend, **341 passed**; formato,
lint y whitespace pasan. Se verificaron reemplazo y rollback real en PostgreSQL
con `app_user`, además del rechazo cross-tenant con RLS. La prueba de reemplazo
usa un constructor RAT simulado; no sustituye una prueba completa del flujo API.
Las comprobaciones posteriores de concurrencia y API se registran en §17.14.

M3-T1 permanece en progreso. Quedan pendientes los contratos y validaciones
de las demás bases/condiciones especiales y la ampliación del flujo M3 más
allá del consentimiento ordinario.

### 17.14 API inicial y validación concurrente

La API inicial de M3 utiliza el prefijo `/licitud`. Todas las operaciones
requieren autenticación, `X-Organization-Id` validado y suscripción activa o
en grace. Los permisos se comprueban en el servidor mediante el catálogo
existente: `view_content` para lectura y `edit_content` para crear, editar y
confirmar. Un editor puede confirmar según esta política inicial; no se crea
un permiso de aprobación nuevo en este bloque.

| Método | Ruta bajo `/licitud` | Operación |
| --- | --- | --- |
| POST | `/treatments/{treatment_id}/assessments` | Crear borrador, respuesta 201 |
| GET | `/treatments/{treatment_id}/assessments/{assessment_id}` | Leer versión borrador, confirmada o reemplazada |
| PATCH | `/treatments/{treatment_id}/assessments/{assessment_id}` | Actualizar únicamente borrador |
| POST | `/treatments/{treatment_id}/assessments/{assessment_id}/confirm` | Confirmar explícitamente consentimiento ordinario |

La respuesta utiliza `LegalAssessmentOut`. El tenant y el actor provienen del
header validado y del perfil autenticado, respectivamente. El cliente no fija
el estado, número de versión, actor ni fechas de confirmación/reemplazo.
`get_db` hace commit al terminar correctamente y rollback ante un error;
los servicios conservan la responsabilidad de flush y validación sin cerrar
la transacción por sí mismos.

Se verificaron tres escenarios con dos conexiones PostgreSQL como `app_user`:

- dos confirmaciones del mismo borrador: la segunda espera el bloqueo de serie
  y después recibe conflicto, conservando una sola versión confirmada;
- la primera confirmación se revierte: la segunda puede confirmar tras obtener
  el bloqueo, sin reemplazos huérfanos;
- una actualización cambia el checklist mientras otra sesión intenta confirmar:
  la confirmación espera y evalúa el payload actualizado, rechazando el pendiente.

Las pruebas verifican la espera con `pg_blocking_pids`, con tiempos máximos
acotados; no suponen que una demora fija demuestra un bloqueo. Estas pruebas
usan un constructor RAT simulado y prueban locks, filas y transacciones reales.

La suite HTTP verifica el constructor RAT real y las transacciones PostgreSQL:
guardado de fechas JSONB, confirmación y reemplazo, conservación de la versión
anterior ante un checklist incompleto, rechazo de cambio de contexto y revisión
posterior del borrador, inmutabilidad de versiones confirmadas, validación del
contrato, aislamiento de organización y tratamiento, permisos viewer/editor,
y bloqueo por suscripción suspendida con acceso permitido en grace.

Validación de este bloque: **350 pruebas backend aprobadas**, formato, lint
de los archivos Python afectados y whitespace sin errores. No se modificaron
migraciones ni el contrato de hash v1. M3-T1 permanece en progreso: faltan LIA,
condiciones especiales y validaciones de las demás bases, además de la interfaz
M3. La validación concurrente de creación de series/versiones se registra en §20.7.1.

## 18. Evaluación de Interés Legítimo (LIA) — schema v1

### 18.1 Objetivo

Cuando la base general seleccionada sea `interes_legitimo_art13d`,
M3 requerirá una Evaluación de Interés Legítimo estructurada.

La Ley N° 21.719 no establece un formulario denominado expresamente “LIA”.

CumpleIA utilizará la LIA como instrumento de documentación y
responsabilidad demostrable para analizar y justificar:

- el interés legítimo perseguido;
- la necesidad del tratamiento;
- su proporcionalidad;
- el posible efecto sobre derechos y libertades del titular;
- las expectativas razonables;
- las salvaguardas adoptadas.

La estructura toma como referencia de UX la plantilla `LIA.xlsx`
aportada al proyecto, adaptándola al marco jurídico chileno.

### 18.2 Estructura general

`lia_assessment` será JSONB validado por un schema Pydantic explícito.

Schema conceptual v1:

- `schema_version`;
- `purpose_and_interest`;
- `necessity`;
- `nature_and_scope`;
- `reasonable_expectations`;
- `impact`;
- `safeguards`;
- `transparency_and_opposition`;
- `conclusion`.

### 18.3 Respuesta estructurada común

Las preguntas cerradas utilizarán conceptualmente una estructura común:

```json
{
  "answer": "si | no | no_aplica | pendiente",
  "comment": "texto opcional"
}
```

Los identificadores de pregunta deberán ser estables entre frontend,
backend y evaluación histórica.

Una futura modificación de redacción no debe cambiar silenciosamente
el significado de una respuesta histórica.

### 18.4 Finalidad e interés perseguido

La sección `purpose_and_interest` deberá documentar al menos:

- finalidad clara y explícita;
- descripción concreta del interés legítimo perseguido;
- si el interés corresponde al responsable, a un tercero o a ambos;
- beneficio esperado para el responsable;
- beneficio esperado para terceros;
- eventual beneficio público;
- importancia concreta del interés;
- consecuencias de no realizar el tratamiento;
- normativa sectorial, códigos o reglas relevantes;
- otras consideraciones éticas relevantes.

La existencia de un beneficio empresarial no será suficiente por sí sola
para confirmar la evaluación.

El interés debe quedar descrito de forma concreta y relacionado con
la finalidad evaluada.

### 18.5 Necesidad y proporcionalidad

La sección `necessity` deberá analizar:

- si el tratamiento contribuye efectivamente a conseguir la finalidad;
- si existe una relación real entre el tratamiento y el interés perseguido;
- si puede lograrse el mismo objetivo sin tratar datos personales;
- si existe una alternativa razonable menos intrusiva;
- si puede utilizarse una menor cantidad de datos;
- si las categorías utilizadas son necesarias, adecuadas y pertinentes.

La conclusión no deberá considerar superado este bloque cuando exista
una alternativa razonable claramente menos intrusiva que permita lograr
la misma finalidad.

### 18.6 Naturaleza y alcance

La sección `nature_and_scope` consumirá el snapshot RAT de la evaluación
y deberá documentar o derivar al menos:

- categorías de datos utilizadas;
- existencia de datos sensibles;
- datos sujetos a reglas especiales;
- niños, niñas o adolescentes;
- grupos vulnerables;
- si los titulares actúan exclusivamente en un contexto profesional;
- volumen o alcance relevante cuando sea conocido;
- cualquier característica que aumente el impacto potencial.

Los hechos ya existentes en el RAT deberán reutilizarse y no solicitarse
nuevamente al usuario salvo que necesiten precisión adicional.

### 18.7 Expectativas razonables

La sección `reasonable_expectations` deberá evaluar:

- existencia de relación previa con los titulares;
- naturaleza de esa relación;
- si el nuevo tratamiento representa un cambio significativo respecto
  del uso anterior de los datos;
- si el titular fue informado cuando los datos fueron obtenidos directamente;
- si los datos fueron obtenidos de terceros y qué información se entregó;
- cambios de tecnología o contexto desde la recolección;
- grado en que la finalidad y el método pueden resultar previsibles;
- carácter nuevo o innovador del tratamiento;
- evidencia disponible sobre expectativas de los titulares;
- otras circunstancias que hagan razonablemente esperable o inesperado
  el tratamiento.

CumpleIA utilizará estos antecedentes como factores de ponderación,
no como reglas automáticas aisladas.

### 18.8 Impacto sobre los titulares

La sección `impact` deberá analizar:

- posibles efectos negativos;
- gravedad potencial;
- probabilidad de ocurrencia;
- posible pérdida de control sobre los datos;
- grado de intrusión;
- probabilidad razonable de oposición;
- efecto sobre derechos o libertades;
- impacto especial sobre personas vulnerables;
- posibilidad de explicar transparentemente el tratamiento al titular.

Cuando existan impactos relevantes no mitigados, la evaluación deberá
quedar marcada para revisión y no presentarse automáticamente como
apta para confirmación.

### 18.9 Salvaguardas

La sección `safeguards` permitirá documentar medidas que reduzcan
el impacto o mejoren el equilibrio, por ejemplo:

- minimización de datos;
- limitación de acceso;
- reducción del plazo de conservación;
- seudonimización o anonimización cuando corresponda;
- restricciones de uso;
- controles de seguridad;
- transparencia adicional;
- mecanismos sencillos de oposición;
- exclusión de determinadas categorías de titulares;
- revisión humana;
- otras medidas organizativas o técnicas.

Las salvaguardas deberán describirse concretamente.
No bastará una afirmación genérica de que existen medidas de seguridad.

### 18.10 Transparencia y derecho de oposición

La sección `transparency_and_opposition` deberá documentar al menos:

- cómo se informa al titular del tratamiento;
- cómo se identifica el interés legítimo perseguido;
- canal para ejercer el derecho de oposición;
- procedimiento interno para gestionar una oposición;
- responsable o área encargada cuando corresponda.

Cuando la base utilizada sea interés legítimo, M3 deberá recordar
expresamente que el titular puede ejercer su derecho de oposición.

La existencia de una oposición concreta no modificará retrospectivamente
el cuestionario original. Su análisis podrá requerir una revisión de la
evaluación y generar evidencia separada.

### 18.11 Conclusión

La sección `conclusion` deberá contener:

- resumen de la ponderación;
- interés legítimo identificado;
- resultado del análisis de necesidad y proporcionalidad;
- principales impactos identificados;
- salvaguardas relevantes;
- explicación de por qué los derechos y libertades del titular
  se consideran suficientemente protegidos o por qué subsisten dudas;
- decisión propuesta.

Valores conceptuales de `decision`:

- `puede_basarse`;
- `no_puede_basarse`;
- `requiere_revision`.

La decisión generada o asistida por CumpleIA será una recomendación
documental y no una certificación automática de licitud.

La evaluación sólo podrá pasar al estado persistido `confirmado`
mediante una acción explícita de un usuario autorizado.

### 18.12 Completitud

El sistema podrá derivar una condición operativa:

- `completo`;
- `requiere_revision`;
- `incompleto`.

Como mínimo, una LIA no estará completa si faltan:

- descripción concreta del interés;
- análisis de necesidad;
- análisis de proporcionalidad;
- análisis de alternativas menos intrusivas;
- contexto de datos y titulares;
- expectativas razonables;
- evaluación de impacto;
- salvaguardas cuando existan impactos que deban mitigarse;
- conclusión documentada.

`completo` significa que la evaluación contiene la información mínima
esperada para su revisión.

No significa que CumpleIA haya determinado automáticamente que el
tratamiento es lícito.

### 18.13 Relación con EIPD

Una Evaluación de Interés Legítimo no sustituye una Evaluación de Impacto
en Protección de Datos.

Si durante la LIA se detectan indicadores relacionados con los supuestos
de alto riesgo que pueden requerir una EIPD, M3 deberá:

- generar una alerta de posible EIPD;
- indicar los motivos detectados;
- evitar presentar la LIA como sustituto de dicha evaluación;
- mantener ambos procesos conceptualmente separados.

El flujo completo de EIPD queda fuera del alcance inicial de M3,
salvo la detección y derivación documentada.

### 18.14 Contrato físico LIA v1 para borradores

`LiaAssessmentV1` implementa el contrato JSONB con `schema_version = 1` y
las ocho secciones de §18.2. Las secciones omitidas se crean vacías; sus campos
textuales, respuestas y decisión son opcionales para permitir borradores.
Una sección explícitamente `null` se rechaza. La completitud se evaluará
separadamente, sin confundir estructura válida con expediente preparado.

Cada pregunta cerrada se identifica por su ruta estable `seccion.campo`,
no por una etiqueta de interfaz. Su valor es `null` (sin responder) o
`LiaResponseV1` con `answer = si | no | no_aplica | pendiente` y `comment`
opcional. Un objeto de respuesta aportado debe incluir `answer`.

Campos físicos por sección:

- `purpose_and_interest`: `purpose_description`, `legitimate_interest`,
  `interest_holder` (`responsable | tercero | ambos`), `controller_benefit`,
  `third_party_benefit`, `public_benefit`, `interest_importance`,
  `consequences_without_processing`, `relevant_rules`, `ethical_considerations`.
- `necessity`: respuestas `contributes_to_purpose`, `linked_to_interest`,
  `achievable_without_personal_data`, `less_intrusive_alternative`,
  `fewer_data_possible`, `categories_necessary_and_relevant`; textos
  `necessity_analysis`, `proportionality_analysis`, `alternatives_analysis`,
  `minimization_analysis`.
- `nature_and_scope`: respuesta `exclusively_professional_context`; textos
  `volume_and_scope`, `special_rules_description`, `additional_risk_factors`.
  Las categorías y los indicadores estructurados de datos/titulares se consumen
  del `rat_context_snapshot` de la evaluación; no se duplican dentro de LIA.
- `reasonable_expectations`: respuestas `prior_relationship`,
  `significant_change_of_use`, `informed_at_direct_collection`,
  `foreseeable_purpose_and_method`, `innovative_processing`; textos
  `relationship_description`, `third_party_information`,
  `technology_or_context_changes`, `expectations_evidence`,
  `expectations_analysis`.
- `impact`: respuestas `loss_of_control`, `reasonable_opposition_likelihood`,
  `transparently_explainable`, `relevant_unmitigated_impacts`; textos
  `negative_effects`, `intrusion_analysis`, `rights_and_freedoms_analysis`,
  `vulnerable_people_impact`, `impact_analysis`; `severity` y `likelihood`
  con valores `baja | media | alta | pendiente` o `null`. Estos valores
  documentan una valoración del usuario; no generan un scoring automático.
- `safeguards`: lista `measures`, inicialmente vacía, y texto
  `safeguards_analysis`. Cada medida contiene `description` de tipo texto
  obligatorio y `mitigated_impact` opcional. La concreción y ausencia de textos
  vacíos se controlarán al evaluar completitud; se admite contenido pendiente
  en borrador.
- `transparency_and_opposition`: `information_method`, `interest_communication`,
  `opposition_channel`, `opposition_procedure`, `responsible_area`.
- `conclusion`: `balancing_summary`, `identified_interest`,
  `necessity_and_proportionality_result`, `main_impacts`, `relevant_safeguards`,
  `rights_protection_reasoning` y `decision` con el catálogo de §18.11 o `null`.

El contrato rechaza campos desconocidos en raíz, secciones, respuestas y
medidas, así como versiones y valores fuera de catálogo. Los textos factuales
se conservan sin trim ni canonización. Evolucionar estas claves exige una
decisión explícita de versionado, sin reinterpretar expedientes históricos.

Creación y actualización de borradores admiten `lia_assessment`. Se valida
antes de persistir y se serializa como JSON. En PATCH, omitir el campo conserva
el expediente, aportar un objeto lo reemplaza como unidad (sin merge de
secciones) y `null` lo elimina. La lectura API utiliza el mismo contrato.

La confirmación de `interes_legitimo_art13d` permanece bloqueada, incluso si
el cliente aporta `decision = puede_basarse`. Quedan pendientes las reglas de
aplicabilidad/completitud, los motivos derivados y su integración transaccional.

Validación: **377 pruebas backend aprobadas**, incluidas pruebas de estructura,
dominios, preservación documental y flujo HTTP con PostgreSQL/RLS. Formato,
lint de los archivos modificados y whitespace pasan. M3-T1 sigue en progreso.

### 18.15 Aplicabilidad y datos mínimos de LIA v1

Esta definición es una política operativa de preparación documental de CumpleIA,
no una certificación automática de licitud. El evaluador recibirá el expediente
`LiaAssessmentV1` y el `RatContextSnapshotV1` vigente de la evaluación, sin
modificarlos ni inferir hechos desde nombres, comentarios o narrativas.

Un contrato inválido se rechazará antes de calcular el resultado. Un expediente
o snapshot ausente dará resultado `incompleto`. El snapshot debe contener
finalidad no vacía, categorías de datos y titulares no vacíos y rol de la
organización informado. Estos controles no sustituyen la revalidación del
contexto M2 ni la comprobación de hash al confirmar.

Un texto obligatorio se considera aportado cuando no es `null` y contiene
caracteres distintos de espacios tras aplicar `strip()` para comprobarlo.
La comprobación no recorta ni modifica el valor persistido y no determina
si su contenido es jurídicamente suficiente. Esa valoración sigue siendo
humana; no se utilizarán umbrales de longitud ni análisis automático de prosa.

Campos siempre obligatorios:

| Sección | Campos |
| --- | --- |
| `purpose_and_interest` | `purpose_description`, `legitimate_interest`, `interest_holder`, `interest_importance`, `consequences_without_processing` |
| `necessity` | Las seis respuestas cerradas y los cuatro textos de análisis definidos en §18.14 |
| `nature_and_scope` | Respuesta `exclusively_professional_context`; contexto de categorías y titulares del snapshot |
| `reasonable_expectations` | Respuestas `prior_relationship`, `significant_change_of_use`, `foreseeable_purpose_and_method`, `innovative_processing`; texto `expectations_analysis` |
| `impact` | Las cuatro respuestas cerradas de §18.14; `severity`, `likelihood`; textos `negative_effects`, `intrusion_analysis`, `rights_and_freedoms_analysis`, `impact_analysis` |
| `safeguards` | `safeguards_analysis`, incluso cuando explique por qué no se proponen medidas adicionales |
| `transparency_and_opposition` | Los cinco textos definidos en §18.14 |
| `conclusion` | Los seis textos definidos en §18.14 y `decision` |

Las respuestas cerradas aplicables deben estar presentes con `si` o `no`.
Omisión, respuesta `pendiente` o `no_aplica` en una pregunta aplicable producen
`incompleto`. `severity` y `likelihood` requieren `baja`, `media` o `alta`;
`null` o `pendiente` producen `incompleto`.

Los análisis de ausencia de efectos o salvaguardas pueden documentar
expresamente esa ausencia; dejar el texto vacío no sustituye el análisis.
La finalidad declarada en `purpose_description` debe coincidir con la finalidad
del snapshot bajo la canonización textual v1 existente. Una diferencia produce
un motivo de revisión, sin reemplazar ni reinterpretar ninguna finalidad.

### 18.16 Campos condicionales y aplicabilidad LIA v1

| Campo | Condición que exige contenido |
| --- | --- |
| `purpose_and_interest.controller_benefit` | `interest_holder = responsable` o `ambos` |
| `purpose_and_interest.third_party_benefit` | `interest_holder = tercero` o `ambos` |
| `reasonable_expectations.relationship_description` | `prior_relationship = si` |
| `reasonable_expectations.informed_at_direct_collection` | Al menos una fuente del snapshot tiene `source_type = titular` |
| `reasonable_expectations.third_party_information` | Al menos una fuente del snapshot tiene `source_type = tercero` |
| `impact.vulnerable_people_impact` | El snapshot indica niños, adolescentes o grupos vulnerables |
| `nature_and_scope.special_rules_description` | Cualquier indicador de `special_regimes` del snapshot es verdadero |
| `safeguards.measures` | Se activa alguno de los indicadores de documentación de mitigación definidos debajo |

Los campos condicionales textuales pueden quedar vacíos cuando no se cumpla
su condición. Si contienen texto, se conserva; no se considera contradictorio
por sí solo. Los campos opcionales restantes de §18.14 no son obligatorios
para la completitud v1, aunque pueden apoyar la revisión humana.

Para `informed_at_direct_collection`, una lista de fuentes no vacía sin
`source_type = titular` da `no_aplicable`: se permite omitir la respuesta o
usar `no_aplica`. Si conserva `si`, `no` o `pendiente`, se devuelve un motivo
de revisión por respuesta residual. Una lista de fuentes vacía da
`sin_resolver` tanto para la respuesta sobre recolección directa como para
la información de terceros: no permite establecer esas aplicabilidades y
produce `incompleto`. No se interpreta `recogida_automatica`, `fuente_publica` ni
`otro` como recolección directa o de terceros sin una decisión adicional.
Si hay fuentes `titular` y `tercero`, se exigen ambos campos correspondientes.

Una condición dependiente de `interest_holder` o `prior_relationship` no
resuelta se informa como `sin_resolver` y produce `incompleto`. La falta del
dato controlador no vuelve opcional su documentación dependiente.

Los siguientes indicadores exigen al menos una medida documental:
`severity` o `likelihood` en `media`/`alta`, `loss_of_control = si`,
`reasonable_opposition_likelihood = si` o `relevant_unmitigated_impacts = si`.
Son disparadores de documentación de mitigación, no umbrales legales ni
scoring de riesgo. Si todos están resueltos y ninguno se activa, las medidas
pueden omitirse y el análisis de salvaguardas deberá explicar la valoración.
Si no hay un disparador afirmativo y alguno está sin resolver, la aplicabilidad
de medidas es `sin_resolver`, con resultado `incompleto`.

Cada medida aportada debe tener `description` no vacía. Cuando se exigen medidas,
cada una deberá además identificar mediante `mitigated_impact` no vacío qué
impacto pretende mitigar. Una lista no vacía no demuestra eficacia ni elimina
un motivo por impactos no mitigados. Las medidas no se generan ni se validan
jurídicamente de forma automática.

### 18.17 Resultado operativo y motivos de revisión LIA v1

La salida será derivada, con `result`, motivos estructurados y aplicabilidad
de los campos condicionales, sin nuevos estados persistidos ni alteraciones
del JSONB histórico. Se aplicará la precedencia
`incompleto > requiere_revision > completo`, conservando todos los motivos.

`incompleto` se obtiene por cualquier faltante de §§18.15–18.16 o condición
sin resolver. Sin faltantes, `requiere_revision` se obtiene por:

- `contributes_to_purpose = no`, `linked_to_interest = no` o
  `categories_necessary_and_relevant = no`;
- `achievable_without_personal_data = si` o `less_intrusive_alternative = si`;
- `foreseeable_purpose_and_method = no`;
- `informed_at_direct_collection = no` cuando sea aplicable;
- `transparently_explainable = no`;
- `relevant_unmitigated_impacts = si`;
- `decision = no_puede_basarse` o `requiere_revision`;
- finalidad documental diferente de la del snapshot;
- respuesta residual a una pregunta condicional no aplicable.

`fewer_data_possible = si` exige el análisis de minimización ya obligatorio,
pero no produce por sí solo un bloqueo por respuesta desfavorable. La ausencia
de relación previa, un cambio de uso, el carácter innovador, la pérdida de
control, la probabilidad de oposición y las valoraciones de gravedad/probabilidad
son factores documentados de ponderación; no se traducen aisladamente en una
conclusión jurídica. Los disparadores de medidas de §18.16 siguen aplicándose.

`completo` significa únicamente que no existen faltantes ni motivos de revisión
bajo estas reglas y que la decisión propuesta es `puede_basarse`. No prueba
la suficiencia de la ponderación, la eficacia de las medidas ni la licitud.

Cada motivo identificará la ruta afectada y un código estable que distinga
campo faltante, respuesta pendiente, `no_aplica` inválido, aplicabilidad no
resuelta, respuesta que requiere revisión, finalidad distinta, medida incompleta
o decisión que requiere revisión. Se ordenarán primero los motivos del contexto
RAT y luego los del expediente siguiendo el orden de secciones y campos del
contrato físico, con las medidas en su orden original. La aplicabilidad usará
`aplicable | no_aplicable | sin_resolver` y el mismo orden estable.

### 18.18 Confirmación futura y casos de aceptación LIA v1

Cuando se implemente la integración, solo `completo` permitirá superar el
control LIA. `incompleto` y `requiere_revision` bloquearán la confirmación y
expondrán todos los motivos; no habrá bypass mediante comentarios o la decisión
favorable aportada por el cliente. El resultado se recalculará tras bloquear
la serie y releer el borrador, dentro de la transacción de confirmación.

También deberán superarse justificación, alcance, contexto/hash RAT y las
condiciones especiales aplicables. El contrato y evaluador LIA no sustituyen
la detección/derivación de posible EIPD de §18.13; ese control y las condiciones
especiales deberán revisarse antes de habilitar la confirmación de esta base.
La confirmación de interés legítimo permanece bloqueada en la implementación
actual: este paso define reglas y no cambia el lifecycle.

Casos mínimos del futuro evaluador:

| Caso | Resultado esperado |
| --- | --- |
| LIA o snapshot ausente; sección o texto obligatorio sin resolver | `incompleto` |
| Respuesta aplicable `pendiente` o `no_aplica` | `incompleto` |
| Fuentes `titular` y `tercero`, sin información sobre la recolección directa o de terceros | `incompleto` |
| Fuentes vacías aunque exista respuesta sobre información directa | `incompleto`, aplicabilidad sin resolver |
| Solo fuentes no directas y respuesta directa omitida o `no_aplica` | Sin faltante por esa pregunta |
| Solo fuentes no directas y respuesta directa `si` | `requiere_revision` si el resto está completo |
| `interest_holder = ambos` sin uno de los beneficios exigidos | `incompleto` |
| Indicador de mitigación activo y medidas vacías | `incompleto` |
| Medidas exigidas con descripción o impacto mitigado vacío | `incompleto` |
| Alternativa menos intrusiva `si` y resto completo | `requiere_revision` |
| Impactos no mitigados `si` y medidas documentadas | `requiere_revision`, sin eliminar el motivo |
| Decisión favorable con faltantes | `incompleto` |
| Decisión favorable y una respuesta desfavorable | `requiere_revision` |
| Un faltante y un motivo de revisión | `incompleto`, conservando ambos motivos |
| Campos resueltos, finalidad coherente y sin motivos de revisión | `completo`, sin certificación de licitud |
| Mismo input evaluado dos veces | Mismo resultado, motivos y aplicabilidad, sin mutar entrada |

### 18.19 Evaluador puro LIA v1 implementado

`evaluate_lia_assessment_v1` en `backend/app/services/lia.py` implementa
§§18.15–18.17. Recibe expediente y snapshot como modelos o diccionarios,
revalida ambos contratos incluso si una instancia fue modificada y rechaza
una estructura inválida aunque el otro input esté ausente.

Devuelve `LiaReadinessV1` con resultado, tupla de `LiaIssueV1` y tupla de
`LiaFieldApplicabilityV1`, todos inmutables. Los motivos usan rutas de campos
y códigos estables; se ordenan primero los del contexto RAT y después los
campos LIA en su orden contractual, con las medidas en su orden original.
La evaluación no modifica ni persiste entradas o resultados.

`can_confirm` indica que el expediente supera únicamente este control.
No ejecuta una transición ni habilita todavía interés legítimo en el servicio
transaccional. La confirmación permanece bloqueada mientras se revisan la
integración y los controles pendientes de condiciones especiales/EIPD.

Validación: **129 casos nuevos** del evaluador y **506 pruebas backend
aprobadas** en la suite completa. Se verifican campos mínimos, respuestas
aplicables, dependencia de fuentes/beneficiarios/regímenes, disparadores de
mitigación, ausencia de inputs, motivos de revisión, precedencia, canonización
textual de finalidad, orden determinista, inmutabilidad de salida y preservación
de entradas. Formato, lint de los nuevos archivos y whitespace pasan.

Este bloque no modifica API, lifecycle, migraciones ni hash v1. M3-T1 sigue
en progreso. El próximo paso es revisar los controles de EIPD y condiciones
especiales y definir la integración de LIA sin omitirlos.

### 18.20 Revisión de controles pendientes antes de integrar LIA

La completitud LIA implementada no resuelve por sí sola la aplicabilidad de
EIPD ni las autorizaciones de regímenes especiales. No se habilitará
`interes_legitimo_art13d` mediante una simple sustitución del evaluador de
consentimiento por el de LIA dentro de `confirm_legal_assessment_v1`.

Referencia normativa de esta revisión: [Ley 21.719, texto oficial BCN](https://www.bcn.cl/leychile/navegar?idNorma=1209272),
artículo 15 ter incorporado a la Ley 19.628, texto del régimen previsto para
el 1 de diciembre de 2026. El precepto considera alto riesgo y contempla
supuestos de evaluación sistemática con automatización y efectos jurídicos
significativos, procesamiento masivo, monitoreo sistemático de espacios públicos
y datos sensibles/especialmente protegidos bajo excepciones al consentimiento.
Esta referencia no fija umbrales numéricos propios de CumpleIA ni convierte
las valoraciones LIA en una conclusión automática de aplicabilidad.

Brechas de información verificadas contra el contrato y constructor actuales:

| Control | Hechos disponibles | Brecha o límite |
| --- | --- | --- |
| Evaluación sistemática y exhaustiva con automatización y efectos jurídicos significativos | `automated_decisions.has_automated_decisions` y descripción factual | No hay indicadores estructurados de evaluación sistemática/exhaustiva ni de efectos jurídicos significativos |
| Tratamiento masivo o a gran escala | Texto LIA `volume_and_scope` | No hay declaración estructurada ni criterio verificado de escala; no inferir desde texto |
| Observación o monitoreo sistemático de zona de acceso público | Fuentes y descripciones RAT | No hay declaración estructurada del supuesto; fuente pública no equivale a monitoreo |
| Datos sensibles/especialmente protegidos bajo excepción al consentimiento | `special_regimes` y base general | Falta contrato/validación de condición especial; base general y condición no son equivalentes |
| Alto riesgo por naturaleza, alcance, contexto, tecnología o fines | Valoraciones y narrativas LIA | No hay revisión estructurada general de este supuesto; gravedad o probabilidad alta no resuelven solas el examen |
| Salud, biometría, geolocalización, investigación y edad específica | Categorías seleccionadas e indicadores generales RAT | No hay discriminadores estructurados suficientes para todos los regímenes; no inferirlos desde nombres o códigos libres |

Estas brechas también afectan el futuro control transversal de M3. La actual
confirmación de consentimiento ordinario conserva su alcance limitado; pasar
sus barreras actuales no demuestra que se haya evaluado EIPD ni que se hayan
detectado todos los regímenes de §15.4. No se declarará cerrado M3-T1 con esa
cobertura parcial.

### 18.21 Definición del próximo control de detección EIPD v1

El próximo bloque implementará un contrato de screening independiente de la
conclusión LIA. No implementará la realización, aprobación o custodia completa
de una EIPD. El contrato físico y la persistencia se fijan en §18.23 antes de introducir
el screening en los schemas o cambiar tablas.

Preguntas cerradas propuestas, con identificadores estables y respuestas
`si | no | pendiente`, sin `no_aplica`:

- `evaluacion_sistematica_automatizada_efectos_significativos`: declaración
  sobre el supuesto conjunto de evaluación personal sistemática/exhaustiva,
  automatización y efectos jurídicos significativos;
- `tratamiento_masivo_o_gran_escala`;
- `monitoreo_sistematico_zona_publica`;
- `datos_protegidos_excepcion_consentimiento`;
- `probable_alto_riesgo_contextual`: revisión general del riesgo atendiendo
  a naturaleza, alcance, contexto, tecnología y fines.

Cada declaración incluirá fundamento documental, obligatorio y no vacío
cuando se evalúe preparación para confirmar. Las preguntas serán siempre
aplicables al screening. Su ausencia o `pendiente` significan que el supuesto
no está resuelto; no se interpretarán como `no`. La salida conservará todos
los motivos y distinguirá hechos declarados de indicadores del RAT/LIA.

Resultados derivados propuestos:

- `requiere_eipd`: existe al menos una respuesta `si` con fundamento; si hay
  otras pendientes, se conservan también sus motivos de incompletitud;
- `pendiente_revision`: no hay respuesta afirmativa resuelta y falta alguna
  respuesta o fundamento, o hay una inconsistencia entre declaraciones y
  hechos estructurados disponibles;
- `sin_supuestos_declarados`: las cinco respuestas son `no`, están fundadas
  y no hay inconsistencias detectadas. No equivale a una exención ni a una
  certificación de que la EIPD no es exigible.

La revisión deberá detectar contradicciones verificables sin analizar prosa.
Por ejemplo, declarar el supuesto automatizado afirmativo cuando RAT declara
que no hay decisiones automatizadas exige revisión del contexto. Una alerta
LIA de impacto alto se mostrará como antecedente de revisión; no se utilizará
por sí sola para resolver el supuesto legal.

En la primera integración, `requiere_eipd` y `pendiente_revision` bloquearán
la confirmación. No se permitirá eludirlos mediante una decisión LIA favorable
ni una referencia documental genérica. Un mecanismo futuro para continuar
tras una EIPD documentada exige diseño explícito de expediente, revisión y
trazabilidad; queda fuera de este primer screening.

El catálogo se versionará. Antes de desbloquear el flujo se deberá verificar
si hay orientaciones/listas oficiales aplicables y registrar cuáles se han
utilizado. Esta revisión no afirma que esas orientaciones ya existan ni que
el catálogo propuesto cubra futuros cambios regulatorios.

### 18.22 Condiciones especiales y secuencia de integración

La ausencia de `special_conditions` no acredita que un régimen sea inaplicable.
Los indicadores generales verdaderos del snapshot seguirán bloqueando la
confirmación hasta implementar su contrato y validaciones. Los casos que no
pueden clasificarse con datos estructurados permanecerán pendientes; no se
resolverán por nombres de categorías, comentarios o una casilla de bypass.

El próximo diseño deberá separar:

- declaraciones factuales de categorías/regímenes y edad cuando corresponda;
- condición especial seleccionada, su identificador y fundamento;
- respuestas/evidencia que documentan sus requisitos;
- resultado derivado de preparación y motivos;
- screening EIPD y su relación con el contexto/versionado.

No se agregará un catálogo especial operativo incompleto copiando únicamente
los valores de §15.3: también deben definirse aplicabilidad, datos mínimos,
contradicciones, requisitos y casos de aceptación de los regímenes de §15.4.
Un estado `completo` de LIA no subsana la ausencia de ese expediente.

Orden de la integración futura:

1. fijar e implementar el contrato físico del screening EIPD y sus pruebas;
2. definir el contrato de detección/condiciones especiales y su validación;
3. conectar los controles al guardado/lectura de borradores, incluyendo las
   reglas de revalidación cuando cambie el alcance o contexto RAT;
4. después de bloquear la serie y releer el borrador, revalidar contratos,
   justificar/seleccionar alcance y recomponer el contexto/hash RAT;
5. ejecutar evaluador LIA, screening EIPD y condiciones especiales vigentes;
6. solo si todos los controles implementados permiten continuar, reemplazar
   la versión anterior y confirmar la sucesora dentro de la misma transacción.

Casos mínimos antes de habilitar interés legítimo: LIA completa con screening
pendiente; LIA completa con EIPD requerida; declaraciones incompatibles con
RAT; condición especial ausente o no soportada; cambio de alcance/contexto;
error tras reemplazo con rollback; actualización concurrente de screening o
condiciones antes de confirmar. Ninguno debe dejar una confirmación parcial.

Este paso es una revisión y definición documental: no modifica código, API,
lifecycle ni migraciones. La confirmación de interés legítimo continúa
bloqueada. La última suite completa sigue en **506 passed**; no se repitió
por este cambio de documentación. M3-T1 permanece en progreso.

### 18.23 Contrato físico y persistencia del screening EIPD v1

El screening se guardará en una columna dedicada
`legal_assessments.eipd_screening JSONB NULL`. Será independiente de
`lia_assessment` y `special_conditions`, y utilizable con cualquier base general.
No contendrá una EIPD realizada ni reemplazará su expediente probatorio.

La columna se incorporará mediante una migración append-only posterior a la
persistencia M3 existente. No se modificará una migración aplicada ni se
crearán resultados ficticios para evaluaciones anteriores. Las filas existentes
mantendrán `NULL`, que significa screening no documentado, nunca screening
superado. El RLS y las FK tenant-aware de la tabla seguirán aplicándose.

Contrato físico `EipdScreeningV1`:

- `schema_version`: entero literal `1`;
- `answers`: lista, inicialmente vacía, de declaraciones estructuradas;
- `notes`: texto opcional;
- `context_binding`: objeto de asociación calculado por el servidor.

Cada declaración contendrá:

- `question_id`: uno de los cinco identificadores definidos en §18.21;
- `answer`: `si | no | pendiente`;
- `rationale`: texto opcional en borrador, obligatorio y no vacío para
  considerar resuelta la declaración.

Los identificadores no podrán repetirse; se rechazarán preguntas, campos,
respuestas y versiones desconocidas. En borrador se admitirá un subconjunto
de preguntas y fundamentos pendientes. No se admite `no_aplica`, porque todas
las preguntas examinan la presencia de un supuesto en el contexto evaluado.
Los textos se conservarán literalmente.

`context_binding` contendrá:

- `schema_version`: entero literal `1`, versión de la asociación documental;
- `hash`: SHA-256 hexadecimal minúsculo de 64 caracteres, calculado por servidor.

El material de esta asociación v1 será exactamente:

```json
{
  "rat_context_snapshot": "objeto completo del snapshot documental v1",
  "lia_assessment": "objeto LIA v1 serializado o null"
}
```

Los textos entre comillas del ejemplo describen valores: en la serialización
real se usarán los objetos JSON correspondientes, no esas cadenas de ejemplo.
Se aplicará JSON con claves ordenadas, separadores compactos, Unicode sin
escape ASCII, codificación UTF-8 y SHA-256 sobre sus bytes. La asociación
preservará orden de listas y valores factuales; no aplicará canonización de
textos ni deduplicación.

Este hash es independiente de `rat_context_hash` y no modifica el contrato
RAT canónico v1. Usar únicamente ese hash canónico sería insuficiente: por
diseño excluye sistemas y algunos metadatos documentales que pueden ser
relevantes para la revisión del screening. La asociación al snapshot completo
y LIA evita reaplicar silenciosamente declaraciones a hechos documentales
cambiados. Una modificación factual o textual puede exigir revisión aun
cuando el hash semántico RAT se conserve; esa sensibilidad es deliberada.

### 18.24 Entrada API y revalidación de la asociación EIPD

El contrato de entrada `EipdScreeningDraftIn` contendrá únicamente
`schema_version`, `answers` y `notes`. No aceptará `context_binding` ni un
resultado derivado aportado por el cliente. La respuesta expondrá el contrato
persistido `EipdScreeningV1`; la asociación será obligatoria en todo objeto
persistido no nulo.

En creación o PATCH:

- omitir `eipd_screening` conserva su valor en PATCH y guarda `NULL` en creación;
- enviar `null` elimina el screening de un borrador;
- enviar un objeto valida y reemplaza el screening completo; el servidor
  calcula la asociación sobre el snapshot y LIA finales de esa misma operación;
- si un PATCH incluye alcance/LIA y screening, se aplicarán primero los cambios
  y la recomposición RAT y después se asociará el screening al resultado;
- si cambia alcance, snapshot o LIA pero el screening se omite, se conserva su
  contenido y asociación anterior, para poder mostrar que requiere revisión;
  nunca se reasocia automáticamente una declaración previa.

La asociación se recalculará para comparar al evaluar preparación y nuevamente
al confirmar sobre el contexto RAT recompuesto y la LIA vigente, tras bloquear
la serie y releer el borrador. Una diferencia genera `contexto_desactualizado`
y bloquea la confirmación, sin borrar ni reinterpretar respuestas. También se
comprobarán cambios del snapshot actual que no alteran el hash RAT canónico.
La asociación no representa aislamiento de snapshot de PostgreSQL: permanece
la limitación de composición M2 bajo READ COMMITTED ya documentada.

Para un contexto desactualizado se devolverá `pendiente_revision`, conservando
los motivos positivos de posible EIPD encontrados en declaraciones previas.
No se presentarán esas declaraciones históricas como una determinación vigente.
Si el contexto coincide y hay una declaración afirmativa fundada, el resultado
será `requiere_eipd`, aunque también haya preguntas pendientes; se conservarán
los motivos pendientes. Ninguno de ambos resultados permite confirmar.

La confirmación histórica seguirá siendo inmutable. Que una versión anterior
carezca de screening no autoriza completar retroactivamente su JSONB ni
reclasificarla automáticamente; una revisión requiere un nuevo borrador.

### 18.25 Migración y aceptación del bloque EIPD

El contrato exterior `LegalAssessment` conserva su `schema_version = 1`:
la nueva columna es una extensión nullable y el cuestionario/ asociación
se versionan de forma independiente. No se cambia `rat_context_schema_version`
ni se reescriben los JSONB históricos de consentimiento/LIA.

La migración agregará únicamente la columna nullable y una restricción de
forma `eipd_screening IS NULL OR jsonb_typeof(eipd_screening) = 'object'`.
La validación del contrato interno se realizará en Pydantic antes de persistir;
la restricción SQL no sustituye dicha validación. No se agregan índices GIN ni
nuevas tablas porque el primer flujo accede por evaluación, serie y tenant.

La implementación y verificación del próximo bloque comprenderán:

1. migración append-only, modelo ORM y schemas de entrada/salida;
2. asociación documental determinista y persistencia del screening en borradores;
3. evaluador de §18.21 con detección de asociación desactualizada;
4. pruebas de upgrade, downgrade y re-upgrade aisladas del drift histórico;
5. pruebas HTTP/RLS de guardado, omisión, eliminación, revalidación y asociación
   calculada por servidor, además de invariancia del hash RAT v1;
6. pruebas de todos los resultados y de rechazo de preguntas duplicadas,
   `no_aplica`, fundamentos vacíos y asociaciones aportadas por el cliente.

La confirmación de interés legítimo seguirá bloqueada durante este bloque.
Antes de habilitarla deben resolverse condiciones especiales y el alcance de
las orientaciones aplicables al screening. Este diseño no constituye una
verificación de que esas orientaciones existan o hayan sido incorporadas.

Este paso solo fija contrato y persistencia: no añade todavía la columna ni
schemas/código. Última suite backend: **506 passed**. M3-T1 sigue en progreso.

### 18.26 Persistencia EIPD implementada

La migración append-only `7c9e1a3b5d20_eipd_screening.py`, descendiente de
`5997a757f17b`, agrega la columna nullable y la restricción de forma definida
en §18.25. Se aplicó mediante upgrade a la base local de desarrollo. El modelo
ORM utiliza `JSONB(none_as_null=True)` para que eliminar el screening guarde
SQL NULL, no el valor JSON `null` que no satisface la restricción de objeto.

Se implementaron `EipdScreeningDraftIn`, `EipdDeclarationV1`,
`EipdContextBindingV1` y `EipdScreeningV1`, con rechazo de campos desconocidos,
duplicados y dominios inválidos. La asociación es obligatoria al persistir
un objeto no nulo y se rechaza si el cliente intenta aportarla en la entrada.

`build_eipd_context_binding_hash_v1` y `bind_eipd_screening_v1` implementan
la asociación documental de §18.23. Creación, actualización y lectura API
admiten el screening. El guardado calcula la asociación después de recomponer
el snapshot y aplicar LIA. Omitir screening conserva su contenido/asociación;
null lo elimina. No se reasocian automáticamente declaraciones anteriores.

Mientras no exista el evaluador EIPD integrado, cualquier screening no nulo
bloquea la confirmación, incluso para consentimiento ordinario, evitando que
sus declaraciones se ignoren. Los expedientes anteriores sin screening
conservan el alcance limitado de confirmación ya documentado; no representan
una comprobación EIPD completa. Interés legítimo continúa bloqueado.

Validación de este bloque:

- upgrade aplicado en desarrollo y upgrade/downgrade/re-upgrade verificados
  sobre un schema PostgreSQL transaccional aislado, sin retirar la columna
  de datos locales existentes;
- restricción SQL admite objeto/SQL NULL y rechaza array;
- bytes/hash deterministas, preservación de textos, asociación afectada por
  snapshot completo y LIA, e invariancia del hash canónico RAT;
- flujo HTTP/RLS de guardado, omisión, null, reemplazo conjunto con LIA,
  asociación de servidor y rechazo de acceso a otra organización;
- regresión específica: **49 passed**; suite completa backend: **519 passed**;
- formato, lint de los archivos afectados y whitespace sin errores.

El drift global histórico de Alembic no se declara resuelto por esta extensión.
No se modificaron migraciones anteriores ni hash RAT v1. El evaluador EIPD,
la exposición del resultado y su integración transaccional siguen pendientes.
M3-T1 permanece en progreso.

### 18.27 Evaluador EIPD v1 implementado

`evaluate_eipd_screening_v1` en `backend/app/services/eipd.py` recibe el
screening persistido, snapshot vigente y LIA opcional. Revalida todos los
contratos, incluidas instancias modificadas, antes de evaluar; un input
inválido no se oculta porque otro esté ausente.

Devuelve `EipdReadinessV1` inmutable con:

- `result`: los tres valores de §18.21;
- `context_current`: la asociación del screening coincide con snapshot/LIA
  recibidos; es falso si alguno de los dos primeros inputs está ausente;
- `issues`: tupla de motivos con ruta, código, categoría y question_id cuando
  corresponda, en orden de contexto y preguntas del catálogo;
- `observations`: tupla separada de antecedentes LIA de gravedad/probabilidad
  alta, sin convertirlos por sí solos en un supuesto afirmativo;
- `can_continue`: verdadero solo para `sin_supuestos_declarados`; supera
  únicamente este control, sin exención legal ni autorización M3 automática.

La precedencia operativa queda explícita:

1. screening/snapshot ausente, asociación desactualizada o automatización
   declarada afirmativa sin estar documentada en el indicador RAT producen
   `pendiente_revision`, conservando también supuestos afirmativos encontrados;
2. con contexto vigente y sin esa inconsistencia, cualquier declaración `si`
   fundada produce `requiere_eipd`, conservando preguntas/fundamentos pendientes;
3. sin afirmativas fundadas, cualquier faltante produce `pendiente_revision`;
4. cinco declaraciones `no` fundadas, sin inconsistencias y con asociación
   vigente producen `sin_supuestos_declarados`.

Los códigos de motivos son `screening_ausente`, `snapshot_ausente`,
`contexto_desactualizado`, `pregunta_omitida`, `respuesta_pendiente`,
`fundamento_ausente`, `supuesto_declarado`, `automatizacion_no_documentada`.
Una afirmativa sin fundamento no se considera resuelta; mantiene el pendiente.
El indicador RAT aislado no demuestra todos los componentes del supuesto:
una declaración negativa no se marca contradictoria únicamente porque el RAT
registre decisiones automatizadas. La inconsistencia inversa exige revisión
conjunta, sin concluir jurídicamente la verdad de la declaración.

La salida conserva textos y motivos históricos: `context_current = false`
evita presentar afirmativas anteriores como determinación vigente. No se
eliminan alertas porque la decisión LIA sea favorable ni se analizan narrativas
para inferir automatización, escala, monitoreo o eficacia de mitigaciones.

Validación: **36 casos nuevos**, **47 passed** en el archivo específico EIPD
y **555 passed** en la suite backend completa. Se comprobaron los cinco
supuestos, omisiones/pendientes/fundamentos vacíos, precedencia, asociación
actual/desactualizada, ausencia de inputs, revalidación estructural,
observaciones LIA, orden de preguntas independiente de la lista de entrada,
preservación de inputs e inmutabilidad de salida. Formato, lint de los archivos
afectados y whitespace pasan.

Este bloque no modifica migraciones, API ni la puerta de confirmación. La
API aún no expone el resultado derivado. El siguiente paso es exponer la
preparación de la evaluación con resultados LIA/EIPD, manteniendo las barreras
de condiciones especiales y la confirmación de interés legítimo bloqueada.
M3-T1 sigue en progreso.

### 18.28 Consulta de preparación por API

`GET /licitud/treatments/{treatment_id}/assessments/{assessment_id}/readiness`
expone `LegalAssessmentReadinessOut`. Requiere autenticación, tenant validado,
suscripción activa/grace y `view_content`, por lo que viewer puede consultar
los resultados. No confirma, edita, reasocia ni bloquea filas de la evaluación.

La respuesta contiene:

- identidad, estado y base de la evaluación;
- `rat_context_current`: comparación del hash RAT actual con el guardado;
  `null` cuando la finalidad/alcance actuales no permiten recomponer el contexto;
- `consent`: resultado, motivos y aplicabilidad cuando la base sea consentimiento;
- `lia`: resultado, motivos y aplicabilidad cuando la base sea interés legítimo;
- `eipd`: resultado, asociación vigente, motivos y observaciones LIA;
- `confirmation_blockers`: barreras del flujo de confirmación actualmente
  implementado, con campo, código y mensaje;
- `pending_controls`: controles transversales incompletos de detección de
  regímenes, condiciones especiales e integración EIPD.

Los bloques documentales no aplicables a la base seleccionada son `null`.
EIPD se evalúa para cualquier base y su ausencia aparece como pendiente.
Los resultados utilizan el snapshot RAT recompuesto actual; si no está
disponible, los evaluadores reciben snapshot ausente y no se presenta el
histórico como si fuera vigente. Los errores estructurales del expediente se
rechazan, y errores ajenos a finalidad/alcance no se ocultan como preparación.

La lista de bloqueos no es una certificación de preparación completa. El flujo
actual conserva consentimiento ordinario sin screening dentro de su cobertura
limitada, mientras `pending_controls` expone que faltan controles transversales.
No se devuelve un booleano global de aprobación ni se autoriza un usuario
viewer a confirmar. Screening no nulo sigue bloqueando confirmación por
integración pendiente; LIA sigue bloqueada aunque sus resultados sean completos.

Consultar una versión confirmada o reemplazada conserva sus datos históricos
y devuelve el bloqueo de estado no editable. El resultado actual se deriva
en lectura; no se guarda en JSONB ni actualiza timestamps, snapshot o versiones.
Es orientativo bajo READ COMMITTED y no sustituye la revalidación transaccional
que se realizará al intentar confirmar.

Validación: flujo HTTP/RLS de preparación, permisos viewer/editor, aislamiento
por organización y tratamiento, ausencia de escrituras/timestamps modificados,
versión histórica, cambio semántico RAT, cambio documental sin cambio de hash,
contexto no recomponible y declaraciones EIPD positivas. Archivo API:
**11 passed**; suite completa backend: **558 passed**. Formato, lint de los
archivos afectados y whitespace pasan. No se modificaron migraciones ni el
lifecycle de confirmación. M3-T1 permanece en progreso.

Próximo bloque: definir detección y contrato de condiciones especiales antes
de integrar las barreras pendientes y habilitar confirmación LIA.

## 19. Cardinalidad de la base de licitud en M3 v1

### 19.1 Una base general por finalidad

Para M3 v1, cada versión de una evaluación tendrá como máximo una
`legal_basis` general seleccionada como fundamento principal del tratamiento
para la finalidad evaluada.

La selección representa la base en la que la organización declara apoyarse
para esa finalidad.

CumpleIA no utilizará una lista de bases generales intercambiables ni
seleccionará automáticamente una base alternativa cuando falle la elegida.

### 19.2 Condiciones especiales separadas

Una evaluación podrá contener cero o más condiciones o regímenes especiales
adicionales, por ejemplo los aplicables a:

- datos sensibles;
- datos de salud;
- datos biométricos;
- niños, niñas o adolescentes;
- investigación o estadística;
- geolocalización.

Estas condiciones no se mezclarán indiscriminadamente con el catálogo de
bases generales.

### 19.3 Finalidades que requieren bases generales distintas

Si una finalidad declarada en el RAT contiene subconjuntos de tratamiento
que requieren bases generales diferentes según datos, titulares o contexto,
CumpleIA no intentará resolverlos almacenando varias bases generales ambiguas
en una misma evaluación.

M3 deberá:

- recomendar separar la finalidad en finalidades más específicas cuando
  resulte razonable; o
- marcar el caso como `requiere_revision` cuando la separación no sea clara.

Esta es una regla de modelado y trazabilidad de CumpleIA, no una afirmación
de que la Ley N° 21.719 exija formalmente una única base por finalidad.

### 19.4 Base general nullable

`legal_basis` podrá ser conceptualmente nullable cuando un régimen especial
requiera ser analizado sin forzar artificialmente una base general que no
corresponda.

Las reglas concretas de validación según cada régimen se definirán en M3-T1.

## 20. Modelo físico preliminar de M3

### 20.1 Separación entre serie y versión

M3 utilizará conceptualmente dos entidades:

- `legal_assessment_series`: identidad estable de la evaluación de una
  finalidad lógica dentro de un tratamiento;
- `legal_assessments`: versiones históricas de la evaluación.

No se utilizará `treatment_purposes.id` como identidad histórica porque M2
reemplaza las finalidades eliminando y recreando sus filas.

### 20.2 `legal_assessment_series`

Campos preliminares:

- `id UUID PK`;
- `organization_id UUID NOT NULL`;
- `treatment_id UUID NOT NULL`;
- `purpose_key TEXT NOT NULL`;
- `purpose_text TEXT NOT NULL`;
- `next_version INTEGER NOT NULL DEFAULT 1`;
- `created_at`;
- `updated_at`;
- `created_by`;
- `updated_by`.

`purpose_text` conservará el texto factual de la finalidad con el que se creó
la serie. No se actualizará por cambios posteriores que sean canónicamente
equivalentes y, por tanto, mantengan el mismo `purpose_key`.

El texto factual vigente utilizado por cada versión quedará registrado en
`purpose_snapshot`. Un cambio material del texto canonizado generará un
`purpose_key` diferente y, por tanto, una nueva serie según §20.4.

Restricciones preliminares:

- FK tenant-safe `(treatment_id, organization_id)` hacia `treatments`;
- UNIQUE `(organization_id, treatment_id, purpose_key)`;
- RLS por `organization_id`.

### 20.3 `purpose_key`

`purpose_key` será una huella determinista de la finalidad lógica y no
dependerá del UUID de `treatment_purposes`.

La entrada del hash se obtendrá mediante una canonización estable del texto,
por ejemplo:

- normalización Unicode;
- eliminación de espacios iniciales/finales;
- colapso de espacios consecutivos;
- normalización de mayúsculas/minúsculas.

Para M3 v1, la entrada de `purpose_key` será el resultado de la función
canónica textual definida en §23.14 y el digest será **SHA-256** calculado
sobre su codificación UTF-8.

Los tests deberán demostrar que textos canónicamente equivalentes producen
el mismo `purpose_key` y que un cambio material del texto canonizado produce
una clave diferente.

El hash no incorporará categorías de datos, titulares u otros elementos
del RAT. Esos elementos pertenecen a `rat_context_hash`.

### 20.4 Cambio del texto de finalidad

En M3 v1, un cambio material del texto canonizado de la finalidad producirá
un `purpose_key` diferente y, por tanto, una nueva serie lógica.

La serie anterior se conservará como historia.

CumpleIA no intentará inferir automáticamente que dos textos distintos
representan la misma finalidad jurídica.

Una futura funcionalidad podría permitir vincular explícitamente una finalidad
renombrada con una serie anterior, pero queda fuera del alcance inicial.

### 20.5 `legal_assessments`

Campos preliminares:

- `id UUID PK`;
- `organization_id UUID NOT NULL`;
- `series_id UUID NOT NULL`;
- `treatment_id UUID NOT NULL`;
- `version INTEGER NOT NULL`;
- `status TEXT NOT NULL`;
- `legal_basis TEXT NULL`;
- `justification TEXT NULL`;
- `purpose_snapshot TEXT NOT NULL`;
- `rat_context_hash TEXT NOT NULL`;
- `rat_context_snapshot JSONB NOT NULL`;
- `consent_assessment JSONB NULL`;
- `lia_assessment JSONB NULL`;
- `special_conditions JSONB NULL`;
- `eipd_screening JSONB NULL` (extensión implementada, §§18.23–18.26);
- `schema_version INTEGER NOT NULL`;
- `confirmed_at TIMESTAMPTZ NULL`;
- `confirmed_by UUID NULL`;
- `replaced_at TIMESTAMPTZ NULL`;
- `replaced_by_assessment_id UUID NULL`;
- `created_at`;
- `updated_at`;
- `created_by`;
- `updated_by`.

Los nombres físicos definitivos podrán ajustarse en M3-T1.

### 20.6 Estados persistidos

`status` admitirá inicialmente:

- `borrador`;
- `confirmado`;
- `reemplazado`.

`requiere_revision` no será un estado persistido.

Será una condición derivada al comparar la evaluación vigente con el contexto
actual del RAT o al detectar reglas de revisión pendientes.

### 20.7 Versiones

Cada serie tendrá versiones enteras crecientes:

`1, 2, 3, ...`

La versión no se reutilizará aunque una evaluación sea descartada o
reemplazada.

`next_version` en `legal_assessment_series` permitirá asignar versiones
de forma transaccional y proporcionará una fila estable que pueda bloquearse
durante operaciones concurrentes.

La versión se asignará al crear una nueva evaluación en estado `borrador`.
Dentro de la misma transacción se bloqueará la serie, se utilizará el valor
actual de `next_version` como `version` de la nueva evaluación y se incrementará
`next_version` antes de liberar el bloqueo.

Actualizar un borrador existente no consumirá una nueva versión. Una versión
que haya sido asignada y persistida no se reutilizará aunque posteriormente el
borrador sea descartado. Si la transacción de creación falla completamente y
no llega a persistirse, no se considerará que exista una versión histórica
asignada.

### 20.7.1 Validación concurrente de creación y reserva

La lectura bloqueante de `_get_or_create_series_for_update_v1` usa
`populate_existing=True`: obtener `FOR UPDATE` no basta para refrescar una
serie que ya estaba cargada en el identity map de la sesión. La reserva debe
utilizar el `next_version` leído de PostgreSQL después de obtener el bloqueo,
no un valor cargado antes de la transacción concurrente.

Una prueba reprodujo la regresión antes de corregirla: la segunda sesión
conservaba `next_version = 2`; la primera creaba y confirmaba la versión 2,
y al liberar el bloqueo la segunda intentaba reutilizarla. El refresco hace
que la segunda cree la versión 3 y deje `next_version = 4`.

Se verificaron cinco escenarios con contexto RAT real, PostgreSQL y RLS como
`app_user`, usando dos conexiones y comprobación de espera con
`pg_blocking_pids`:

- serie nueva y commit de la primera creación: una serie, un borrador v1;
  la segunda solicitud recibe conflicto sin consumir otra versión;
- serie nueva y rollback de la primera creación: la segunda crea v1;
- serie existente y commit del nuevo borrador: la segunda recibe conflicto;
- serie existente y rollback de la reserva: la segunda reutiliza la versión
  no comprometida, sin salto del contador;
- serie previamente cargada por la segunda sesión y creación/confirmación
  concurrente: el contador se refresca y se asigna la siguiente versión libre.

En todos los casos se comprobaron unicidad de serie, una sola versión borrador,
versiones persistidas esperadas y `next_version` coherente. Los servicios no
hacen commit ni rollback internos. La suite completa posterior a la corrección
arroja **355 passed**; formato, lint y whitespace pasan para este bloque.

### 20.8 Unicidad de borrador y confirmado

Para cada `series_id` deberá existir como máximo:

- un `borrador`;
- un `confirmado`.

Podrán existir múltiples versiones `reemplazado`.

La implementación deberá utilizar restricciones o índices parciales de
PostgreSQL para proteger esta regla también frente a concurrencia.

Conceptualmente:

- UNIQUE parcial sobre `series_id` donde `status = 'borrador'`;
- UNIQUE parcial sobre `series_id` donde `status = 'confirmado'`;
- UNIQUE `(series_id, version)`.

### 20.9 Confirmación transaccional

Al confirmar un borrador:

1. se bloqueará la serie correspondiente;
2. se volverá a validar completitud y contexto RAT;
3. el anterior `confirmado`, si existe, pasará a `reemplazado`;
4. `replaced_at` y `replaced_by_assessment_id` dejarán trazabilidad;
5. el borrador pasará a `confirmado`;
6. se registrarán `confirmed_at` y `confirmed_by`;
7. toda la operación se realizará en una única transacción.

Una confirmación fallida no deberá dejar dos evaluaciones confirmadas ni
una evaluación anterior reemplazada sin sucesora confirmada.

### 20.10 Contexto RAT y condición de revisión

`rat_context_snapshot` contendrá una copia inmutable y estructurada del
contexto factual utilizado para realizar la evaluación.

`rat_context_hash` será calculado sobre una representación canónica que
incluya, como mínimo:

- finalidad;
- categorías de datos aplicables;
- categorías de titulares;
- indicadores de datos sensibles;
- indicadores de niños, niñas o adolescentes;
- grupos vulnerables;
- otros hechos de M2 que afecten las reglas de M3.

Los elementos se ordenarán antes de calcular el hash para evitar cambios
falsos causados únicamente por el orden de las listas.

Si el hash actual difiere del hash de la última evaluación confirmada,
la interfaz mostrará `requiere revisión`.

La evaluación confirmada histórica no se modificará automáticamente.

### 20.11 RLS y aislamiento tenant

Tanto `legal_assessment_series` como `legal_assessments` tendrán
`organization_id` explícito y RLS.

Las relaciones entre ambas tablas y con `treatments` deberán ser tenant-safe,
evitando que un identificador válido de otra organización pueda utilizarse
para crear asociaciones cruzadas.

M3 deberá incluir pruebas reales de aislamiento usando el rol restringido
de aplicación, siguiendo el mismo criterio aplicado en M2.

### 20.12 Índices operativos preliminares

Además de las restricciones de unicidad, se prevén índices para:

- `(organization_id, treatment_id)`;
- `(organization_id, status)`;
- `(organization_id, treatment_id, purpose_key)` en series;
- búsqueda de evaluaciones por `series_id` y versión.

No se crearán inicialmente índices GIN sobre los JSONB salvo que una consulta
real del producto los justifique.

## 21. Contexto RAT que invalida una evaluación

### 21.1 Principio

`rat_context_hash` no representará todo el registro RAT.

Representará únicamente el subconjunto canónico de hechos de M2 que puede
afectar materialmente una evaluación de licitud, consentimiento, interés
legítimo, condiciones especiales o necesidad de revisión.

El objetivo es detectar cambios jurídicamente relevantes evitando
invalidaciones producidas por detalles técnicos o administrativos.

### 21.2 Hechos incluidos en el hash

El contexto canónico incluirá, como mínimo:

- finalidad evaluada, en forma canonizada;
- rol de la organización en el tratamiento;
- categorías de datos aplicables;
- indicadores de datos sensibles y otras categorías especiales;
- categorías de titulares;
- indicadores de niños, niñas o adolescentes;
- indicadores de grupos vulnerables;
- fuentes relevantes de los datos;
- regla de conservación;
- existencia de decisiones automatizadas;
- hechos relevantes sobre terceros o destinatarios;
- hechos relevantes sobre transferencias internacionales cuando puedan
  afectar la evaluación;
- otros indicadores explícitos de M2 que activen reglas especiales de M3.

Los campos exactos se fijarán en M3-T1 después de revisar los modelos
operativos de M2.

### 21.3 Identificadores que no entran en el hash

No deberán participar por sí mismos en `rat_context_hash`:

- UUID de `TreatmentPurpose`;
- UUID de categorías;
- UUID de titulares;
- UUID de fuentes;
- UUID de sistemas;
- UUID de proveedores;
- IDs técnicos de tablas puente.

La recreación de filas técnicamente equivalentes no deberá provocar
`requiere revisión`.

### 21.4 Cambios administrativos u operativos excluidos

Tampoco deberán invalidar por sí solos una evaluación:

- `created_at`;
- `updated_at`;
- `created_by`;
- `updated_by`;
- `sort_order`;
- posición visual de elementos;
- nombre interno del tratamiento;
- responsable interno;
- cambios puramente ortográficos o de formato que no alteren el contenido
  canónico;
- cambios de infraestructura técnica que no alteren los hechos jurídicamente
  relevantes de la evaluación.

Estos elementos podrán permanecer en el snapshot completo cuando sean útiles
para trazabilidad, aunque no formen parte del hash.

### 21.5 Sistemas

Un cambio de sistema técnico no invalidará automáticamente una evaluación.

Por ejemplo, sustituir una aplicación por otra que realiza funcionalmente el
mismo tratamiento no debe cambiar la base de licitud por sí solo.

Sí deberá revisarse cuando el cambio introduzca hechos relevantes para M3,
como por ejemplo:

- nuevas decisiones automatizadas;
- biometría;
- geolocalización;
- nuevas categorías de datos;
- nuevos destinatarios;
- transferencias internacionales;
- cambios relevantes en el alcance o impacto sobre los titulares.

### 21.6 Terceros y transferencias

No se utilizarán UUID o nombres técnicos como única señal de cambio.

El contexto deberá representar las características semánticas relevantes,
por ejemplo, cuando estén disponibles:

- existencia de terceros con acceso;
- rol del tercero;
- país relevante;
- existencia de transferencia internacional;
- condición relevante de la transferencia;
- cambio material de destinatarios o alcance.

Un cambio meramente administrativo de un proveedor no deberá generar
revisión si el contexto jurídico permanece equivalente.

### 21.7 Canonización

Antes de calcular el hash:

- los textos relevantes se normalizarán;
- se eliminarán diferencias irrelevantes de espacios;
- las listas se ordenarán por claves semánticas estables;
- los objetos JSON utilizarán orden determinista de claves;
- no se incluirán valores técnicos volátiles.

M3-T1 definirá y probará una función única de canonización.

El algoritmo de hash será determinista y se utilizará sobre la representación
canónica serializada.

### 21.8 Versionado del algoritmo

El contexto deberá registrar una versión del esquema de canonización/hash,
independiente de la versión del cuestionario LIA o consentimiento.

Conceptualmente:

`rat_context_schema_version = 1`

Una modificación futura del algoritmo no deberá convertir automáticamente
todas las evaluaciones históricas en evaluaciones desactualizadas.

M3 deberá poder interpretar el snapshot usando la versión con la que fue
generado.

### 21.9 Snapshot más amplio que el hash

`rat_context_snapshot` podrá contener más información que la utilizada para
calcular `rat_context_hash`.

Esto permite conservar contexto documental útil sin hacer que cualquier
cambio menor obligue a revisar la evaluación.

El snapshot confirmado será inmutable.

### 21.10 Motivos de revisión

El hash permitirá detectar rápidamente que existe una diferencia, pero la
interfaz no deberá limitarse a mostrar “el contexto cambió”.

Cuando exista diferencia, M3 comparará el snapshot confirmado con el contexto
actual y derivará motivos explicables, por ejemplo:

- `purpose_changed`;
- `organization_role_changed`;
- `data_categories_changed`;
- `sensitive_data_changed`;
- `data_subjects_changed`;
- `vulnerable_group_changed`;
- `data_sources_changed`;
- `retention_changed`;
- `automated_decision_changed`;
- `third_parties_changed`;
- `international_transfer_changed`;
- `special_regime_changed`.

Estos motivos serán derivados y no modificarán la evaluación histórica.

### 21.11 Principio de no invalidación silenciosa

Un cambio relevante en M2:

- no borrará una evaluación confirmada;
- no modificará su snapshot;
- no cambiará automáticamente su base de licitud;
- no reemplazará automáticamente la versión confirmada.

M3 mostrará `requiere revisión` y permitirá preparar una nueva versión.

## 22. Modelo físico del alcance finalidad → datos y titulares

### 22.1 Decisión para M3 v1

M3 v1 no creará una tabla puente histórica entre una finalidad y las filas
actuales de `treatment_data_categories` o `treatment_data_subjects`.

El alcance utilizado por cada versión de `LegalAssessment` quedará persistido
dentro de su `rat_context_snapshot`.

### 22.2 Alcance de datos

El snapshot de la evaluación deberá contener explícitamente las categorías de
datos que el usuario declara aplicables a la finalidad evaluada.

La referencia se hará mediante valores semánticos estables, principalmente:

- `category_code`;
- nombre descriptivo utilizado en el momento de la evaluación;
- indicador de dato sensible;
- indicadores de regímenes especiales relevantes.

No se utilizará el UUID de la fila de M2 como identidad histórica.

### 22.3 Alcance de titulares

El snapshot deberá contener igualmente las categorías de titulares aplicables
a la finalidad evaluada, incluyendo cuando corresponda:

- `category_code`;
- nombre descriptivo;
- `includes_children`;
- `includes_adolescents`;
- `is_vulnerable_group`;
- otros indicadores jurídicamente relevantes disponibles en M2.

### 22.4 Selección del alcance

Cuando un tratamiento tenga varias finalidades, categorías de datos o
categorías de titulares, M3 deberá permitir indicar cuáles corresponden a la
finalidad que se está evaluando.

La selección forma parte del borrador de la evaluación jurídica y no modifica
las colecciones originales del RAT.

M2 continúa describiendo el inventario completo del tratamiento.

M3 documenta qué subconjunto de ese inventario resulta relevante para cada
finalidad evaluada.

### 22.5 Integridad de la selección

M3 no permitirá incorporar al alcance códigos que no existan actualmente en
el tratamiento de la misma organización.

La validación se realizará al guardar y nuevamente al confirmar.

La confirmación conservará el snapshot aunque posteriormente M2 elimine o
modifique esas categorías.

### 22.6 Cambios posteriores

Si una categoría incluida en una evaluación confirmada:

- desaparece del RAT;
- cambia materialmente;
- cambia su condición de sensibilidad;
- cambia un indicador de niños, adolescentes o vulnerabilidad;

la comparación del contexto deberá generar `requiere revisión`.

La evaluación histórica confirmada no se modificará.

### 22.7 Sin duplicación innecesaria

No se creará inicialmente una tabla relacional adicional para este alcance
porque:

- los identificadores actuales de M2 no son históricamente estables;
- el alcance pertenece a una versión concreta de la evaluación;
- necesitamos conservar exactamente el contexto utilizado al confirmar;
- los códigos semánticos y el snapshot son suficientes para el MVP.

Si en el futuro M2 adopta identidades lógicas estables por finalidad,
categoría y titular, esta decisión podrá revisarse mediante una migración
posterior sin alterar los snapshots históricos.

## 23. Contrato canónico del contexto RAT v1

### 23.1 Objetivo

M3-T1 fija `rat_context_schema_version = 1` como el primer contrato
operativo para construir `rat_context_snapshot` y `rat_context_hash`.

El snapshot conservará el contexto factual necesario para explicar y
reconstruir la evaluación jurídica de una finalidad.

El hash se calculará únicamente sobre el subconjunto canónico de hechos
jurídicamente relevantes definido en esta sección.

La existencia de información en el snapshot no implica por sí sola que dicha
información participe en el hash.

### 23.2 Alcance seleccionado por finalidad

Cada evaluación corresponde a una única finalidad de un tratamiento.

El borrador deberá identificar explícitamente:

- la finalidad evaluada;
- los `category_code` de las categorías de datos aplicables;
- los `category_code` de las categorías de titulares aplicables.

Los códigos seleccionados deberán existir actualmente en el tratamiento de la
misma organización al guardar el borrador y nuevamente al confirmarlo.

En una actualización parcial de un borrador, si la solicitud no envía un nuevo
alcance, M3 reutilizará los `category_code` de datos y titulares conservados en
el `rat_context_snapshot` vigente del borrador y volverá a validarlos contra M2
antes de persistir el guardado.

La selección no modificará M2 y quedará materializada en
`rat_context_snapshot`.

No se persistirán UUID de las filas seleccionadas como identidad histórica del
alcance.

Para seleccionar operativamente la finalidad actual, una solicitud podrá
referenciar el `TreatmentPurpose.id` vigente de M2. Ese UUID se utilizará
únicamente para resolver, dentro del mismo tenant y tratamiento, la fila actual
de la finalidad.

Una vez resuelta la fila, M3 derivará `purpose_key` desde `purpose` aplicando
la canonización definida para v1. El UUID de `TreatmentPurpose` no se
persistirá en la serie, en la evaluación ni en el snapshot documental, y no
formará parte de la identidad histórica de la finalidad.

### 23.3 Estructura lógica del snapshot v1

`rat_context_snapshot` utilizará una estructura versionada que represente, al
menos, los siguientes bloques lógicos:

- `purpose`;
- `organization_role`;
- `data_categories`;
- `data_subjects`;
- `data_sources`;
- `retention`;
- `automated_decisions`;
- `systems`;
- `third_parties`;
- `international_transfers`;
- `special_regimes`.

El snapshot podrá contener información documental adicional cuando sea útil
para trazabilidad, siempre que se mantenga explícita la separación entre esa
información y el contexto utilizado para el hash.

### 23.4 Finalidad

La finalidad se representará mediante su texto semántico.

El UUID de `TreatmentPurpose`, `sort_order` e `is_primary` no formarán parte
del hash.

`is_primary` describe la organización del RAT y no modifica por sí solo la
evaluación jurídica de la finalidad seleccionada.

La finalidad utilizada al confirmar deberá coincidir con
`purpose_snapshot`.

### 23.5 Categorías de datos

Para cada categoría de datos seleccionada, el snapshot conservará:

- `category_code`;
- `category_name`;
- `is_sensitive`;
- los indicadores adicionales de regímenes especiales que M2 exponga en el
  futuro y que M3 reconozca explícitamente.

El hash utilizará esos valores semánticos y no el UUID de
`TreatmentDataCategory`.

`notes` podrá conservarse como información documental cuando resulte útil,
pero no formará parte del hash v1.

Las categorías se ordenarán canónicamente por `category_code` normalizado y,
cuando sea necesario para desempate determinista, por su representación
semántica completa.

### 23.6 Categorías de titulares

Para cada categoría de titulares seleccionada, el snapshot conservará:

- `category_code`;
- `category_name`;
- `includes_children`;
- `includes_adolescents`;
- `is_vulnerable_group`;
- otros indicadores jurídicamente relevantes que M2 exponga en el futuro y
  que M3 reconozca explícitamente.

El hash utilizará esos valores semánticos y no el UUID de
`TreatmentDataSubject`.

`notes` podrá conservarse como información documental, pero no formará parte
del hash v1.

Las categorías se ordenarán canónicamente por `category_code` normalizado y,
cuando sea necesario, por su representación semántica completa.

### 23.7 Fuentes de datos

M2 no dispone actualmente de un código lógico estable para
`TreatmentDataSource`.

Por ello, cada fuente se representará canónicamente mediante:

- `source_type`;
- `description` normalizada cuando exista;
- `is_public_source`.

El UUID, fechas de auditoría y orden de creación quedarán excluidos.

Las fuentes se ordenarán por la combinación semántica de esos campos.

### 23.8 Conservación

El contexto canónico incluirá `retention_rule` normalizada.

`deletion_method` podrá conservarse en el snapshot para trazabilidad
operativa, pero no participará inicialmente en el hash v1 salvo que una regla
jurídica de M3 dependa explícitamente de ella.

### 23.9 Decisiones automatizadas

El contexto canónico incluirá:

- `has_automated_decisions`;
- `automated_decision_description` normalizada cuando existan decisiones
  automatizadas.

Cuando `has_automated_decisions` sea falso, la descripción no deberá producir
diferencias en el hash.

### 23.10 Sistemas

Los UUID, nombres, proveedores y sustituciones puramente técnicas de sistemas
no participarán por sí mismos en el hash.

El snapshot podrá conservar información de sistemas para trazabilidad.

M3 incorporará al contexto canónico únicamente hechos jurídicamente
relevantes derivados de sistemas cuando M2 disponga de datos estructurados que
los representen, por ejemplo biometría, geolocalización, decisiones
automatizadas o transferencias.

En v1 no se inferirán esos hechos a partir del nombre del sistema, proveedor,
`hosting_location` o texto libre equivalente.

### 23.11 Terceros y proveedores

Para cada relación con un tercero, el contexto canónico representará los
hechos semánticos disponibles que puedan afectar la evaluación, incluyendo:

- `relationship_type`;
- `has_data_access`;
- país del proveedor cuando esté disponible;
- `has_subprocessors`;
- finalidad de la relación normalizada cuando esté informada.

El UUID y el nombre administrativo del proveedor no participarán por sí solos
en el hash.

`contract_reference`, `engagement_object`, `engagement_duration` y `notes`
podrán conservarse en el snapshot para trazabilidad, pero no participarán en
el hash v1.

`has_contract` podrá conservarse en el snapshot y no formará parte del hash v1
mientras ninguna regla jurídica de M3 dependa explícitamente de ese dato.

### 23.12 Transferencias internacionales

Para cada transferencia, el contexto canónico incluirá:

- `destination_country`;
- `adequacy_status`;
- `mechanism` normalizado cuando exista;
- `guarantees_description` normalizada cuando exista.

Cuando el destinatario esté vinculado a un proveedor, su UUID no participará
en el hash.

`recipient_name` podrá conservarse en el snapshot para trazabilidad y para
explicar el destinatario, pero el nombre por sí solo no será una identidad
técnica estable ni la única señal de cambio.

`evidence_reference` quedará fuera del hash v1.

Las transferencias se ordenarán mediante su representación semántica
canónica.

### 23.13 Regímenes especiales

`special_regimes` será un bloque derivado de hechos explícitos disponibles en
M2 y del alcance seleccionado.

En v1 deberá representar, como mínimo, cuando corresponda:

- existencia de datos sensibles;
- inclusión de niños;
- inclusión de adolescentes;
- existencia de grupos vulnerables.

No se inferirán biometría, salud, perfil biológico, geolocalización u otros
regímenes especiales desde nombres, notas o descripciones libres mientras M2
no disponga de indicadores estructurados suficientes.

La incorporación futura de nuevos indicadores requerirá una decisión explícita
sobre compatibilidad y versionado del contexto.

### 23.14 Canonización de texto

La función canónica v1 aplicará a los textos que participan en el hash, como
mínimo:

- normalización Unicode;
- eliminación de espacios al inicio y al final;
- colapso de secuencias internas de espacios en un único espacio.

La canonización deberá evitar que diferencias puramente de formato produzcan
una revisión.

No se eliminarán ni transformarán palabras con significado jurídico.

Para `rat_context_schema_version = 1`, la canonización textual queda fijada
en este orden:

1. normalización Unicode **NFC**;
2. eliminación de whitespace al inicio y al final;
3. colapso de cualquier secuencia interna de whitespace Unicode en un único
   espacio ASCII;
4. normalización de mayúsculas/minúsculas mediante `casefold()`.

No se eliminarán puntuación, tildes, diacríticos ni otros caracteres con
posible significado semántico o jurídico.

Esta misma función canónica v1 se reutilizará para derivar `purpose_key` y
para los textos incluidos en el objeto canónico de `rat_context_hash`.

Para los campos textuales opcionales del objeto canónico, un valor `null` de
M2 permanecerá como `null`. Si un valor no nulo, después de aplicar la
canonización textual v1, produce la cadena vacía `""`, su representación
canónica será también `null`. De este modo, `null`, `""` y texto compuesto
exclusivamente por whitespace no producirán hashes distintos por una
diferencia meramente técnica de captura.

Esta equivalencia se aplicará únicamente a campos textuales opcionales. No
modifica la identidad de `purpose`, cuyo texto es semánticamente obligatorio.

Las reglas anteriores deberán quedar congeladas mediante tests deterministas
antes de considerar cerrado M3-T1.

### 23.15 Objeto canónico v1

Para `rat_context_schema_version = 1`, `rat_context_hash` se calculará sobre
un objeto canónico con una estructura fija y distinta del snapshot documental.

La estructura canónica contendrá exclusivamente hechos jurídicamente
relevantes definidos en las subsecciones anteriores. No contendrá UUID,
timestamps, campos de auditoría ni información meramente documental.

Los bloques de primer nivel serán:

- `purpose`;
- `organization_role`;
- `data_categories`;
- `data_subjects`;
- `data_sources`;
- `retention`;
- `automated_decisions`;
- `systems`;
- `third_parties`;
- `international_transfers`;
- `special_regimes`.

La representación exacta de los bloques simples será:

```json
{
  "purpose": "gestión de clientes",
  "organization_role": "responsable",
  "retention": {
    "retention_rule": "5 años"
  },
  "automated_decisions": {
    "has_automated_decisions": false,
    "description": null
  }
}
```

`purpose` será el texto de la finalidad después de aplicar la canonización v1.

`organization_role` conservará el valor estructurado de M2 o `null` cuando no
esté informado.

`retention.retention_rule` será la regla de conservación canonizada o
`null`.

En `automated_decisions`, `description` será el texto canonizado únicamente
cuando `has_automated_decisions` sea `true`. Cuando sea `false`,
`description` será canónicamente `null`, aunque M2 conserve accidentalmente
texto en ese campo.

La representación exacta de las categorías seleccionadas será:

```json
{
  "data_categories": [
    {
      "category_code": "identificacion",
      "category_name": "datos de identificación",
      "is_sensitive": false
    }
  ],
  "data_subjects": [
    {
      "category_code": "clientes",
      "category_name": "clientes",
      "includes_children": false,
      "includes_adolescents": false,
      "is_vulnerable_group": false
    }
  ]
}
```

`category_code` y `category_name` se canonizarán mediante la función de
texto v1 definida en §23.14.

Las listas `data_categories` y `data_subjects` contendrán exclusivamente
las categorías seleccionadas para la finalidad evaluada. No contendrán UUID,
`notes` ni campos de auditoría.

Las listas se ordenarán primero por `category_code` canónico y, cuando sea
necesario para un desempate determinista, por la representación semántica
completa del elemento.

La representación exacta de las fuentes de datos será:

```json
{
  "data_sources": [
    {
      "source_type": "titular",
      "description": null,
      "is_public_source": false
    }
  ]
}
```

`source_type` conservará uno de los valores estructurados definidos por M2:
`titular`, `tercero`, `fuente_publica`, `recogida_automatica` u
`otro`.

`description` se canonizará mediante §23.14 y, al ser un campo textual
opcional, se representará como `null` cuando M2 contenga `null`, una cadena
vacía o únicamente whitespace.

`is_public_source` conservará su valor booleano estructurado.

La lista `data_sources` se ordenará determinísticamente por la tupla semántica
(`source_type`, `description`, `is_public_source`). No contendrá UUID,
campos de auditoría ni orden de creación.

La representación exacta de sistemas en el objeto canónico v1 será:

```json
{
  "systems": []
}
```

Para `rat_context_schema_version = 1`, `systems` será siempre una lista
vacía. El modelo M2 actual no expone en `System` hechos jurídicamente relevantes
estructurados que deban participar en el hash.

Los identificadores, `name`, `provider`, `hosting_location`,
`hosting_country` e `is_international` no se incorporarán al objeto
canónico v1. `is_international` es un atributo legacy y las transferencias
internacionales se representarán mediante su bloque estructurado específico.

El snapshot documental podrá conservar los sistemas asociados y sus datos de
trazabilidad sin que ello modifique `rat_context_hash`.

La representación exacta de terceros será:

```json
{
  "third_parties": [
    {
      "relationship_type": "encargado",
      "has_data_access": true,
      "country": "chile",
      "has_subprocessors": false,
      "purpose": "prestación del servicio"
    }
  ]
}
```

`relationship_type` conservará uno de los valores estructurados definidos por
M2: `encargado`, `cesionario` u `otro`.

`has_data_access` y `has_subprocessors` conservarán sus valores booleanos
estructurados.

`country` se obtendrá de `Vendor.country` y `purpose` de
`TreatmentVendor.purpose`. Ambos se canonizarán mediante §23.14 y, al ser
textos opcionales, se representarán como `null` cuando estén ausentes,
vacíos o contengan únicamente whitespace.

La lista `third_parties` se ordenará determinísticamente por la
representación semántica completa de esos cinco campos.

No participarán en el objeto canónico v1 el UUID ni el nombre administrativo
del proveedor, `has_contract`, `contract_reference`,
`engagement_object`, `engagement_duration`, `notes`, ni los
atributos legacy `Vendor.role`, `Vendor.is_international` y
`Vendor.has_dpa`. Esos datos podrán conservarse en el snapshot documental
cuando corresponda.

La representación exacta de transferencias internacionales será:

```json
{
  "international_transfers": [
    {
      "destination_country": "estados unidos",
      "adequacy_status": "pendiente",
      "mechanism": null,
      "guarantees_description": null
    }
  ]
}
```

`destination_country` se canonizará mediante §23.14 y deberá conservar un
valor no vacío, coherente con su carácter obligatorio en M2.

`adequacy_status` conservará uno de los valores estructurados definidos por
M2: `adecuado`, `no_adecuado`, `pendiente` o
`no_determinado`.

`mechanism` y `guarantees_description` se canonizarán mediante §23.14.
Al ser textos opcionales, se representarán como `null` cuando estén
ausentes, vacíos o contengan únicamente whitespace.

La lista `international_transfers` se ordenará determinísticamente por la
representación semántica completa de esos cuatro campos.

No participarán en el objeto canónico v1 `vendor_id`,
`recipient_name`, `evidence_reference`, UUID ni campos de auditoría.
`recipient_name` y `evidence_reference` podrán conservarse en el
snapshot documental para trazabilidad.

La representación exacta de regímenes especiales será:

```json
{
  "special_regimes": {
    "has_sensitive_data": false,
    "includes_children": false,
    "includes_adolescents": false,
    "has_vulnerable_groups": false
  }
}
```

`special_regimes` será un bloque derivado exclusivamente del alcance
seleccionado para la finalidad evaluada.

`has_sensitive_data` será `true` cuando al menos una categoría de datos
seleccionada tenga `is_sensitive = true`.

`includes_children` será `true` cuando al menos una categoría de titulares
seleccionada tenga `includes_children = true`.

`includes_adolescents` será `true` cuando al menos una categoría de
titulares seleccionada tenga `includes_adolescents = true`.

`has_vulnerable_groups` será `true` cuando al menos una categoría de
titulares seleccionada tenga `is_vulnerable_group = true`.

Cuando ninguna fila seleccionada satisfaga una condición, el valor derivado
correspondiente será `false`. No se utilizarán nombres, notas,
descripciones libres ni filas de M2 que estén fuera del alcance seleccionado
para inferir estos indicadores.

### 23.16 Serialización y hash

El hash se calculará sobre un objeto canónico separado conceptualmente del
snapshot documental.

La serialización será JSON determinista:

- claves ordenadas lexicográficamente;
- listas previamente ordenadas por sus representaciones semánticas canónicas;
- separadores compactos `(",", ":")`, sin whitespace añadido por el serializador;
- caracteres Unicode conservados sin escape ASCII (`ensure_ascii=False`);
- representación JSON estándar de booleanos y valores nulos (`true`, `false`, `null`);
- codificación final UTF-8;
- sin BOM ni salto de línea final;
- sin UUID, timestamps ni valores técnicos volátiles.

La referencia de implementación para v1 será equivalente a
`json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`.
El digest SHA-256 se calculará sobre los bytes UTF-8 exactos producidos por
esa serialización, sin transformaciones posteriores.

La misma información semántica deberá producir exactamente el mismo
`rat_context_hash` independientemente del orden de entrada, UUID de las filas
o recreación técnica de registros equivalentes.

La ordenación canónica v1 utilizará claves específicas por bloque:

- `data_categories`: (`category_code`, `category_name`, `is_sensitive`);
- `data_subjects`: (`category_code`, `category_name`, `includes_children`,
  `includes_adolescents`, `is_vulnerable_group`);
- `data_sources`: (`source_type`, clave opcional de `description`,
  `is_public_source`);
- `third_parties`: (`relationship_type`, `has_data_access`, clave opcional de
  `country`, `has_subprocessors`, clave opcional de `purpose`);
- `international_transfers`: (`destination_country`, `adequacy_status`,
  clave opcional de `mechanism`, clave opcional de
  `guarantees_description`).

Para ordenar un texto opcional, `null` tendrá la clave `(0, "")` y un texto
no nulo tendrá la clave `(1, valor_canonico)`. Esta regla existe únicamente
para obtener una comparación total y determinista; no modifica el valor
JSON almacenado, que continuará siendo `null` o el texto canónico según
corresponda.

La ordenación no deduplicará elementos. Si dos elementos tienen una
representación semántica canónica idéntica, ambos permanecerán en la lista y
su multiplicidad formará parte de los bytes utilizados para el hash.


### 23.17 Comparación y motivos de revisión

La comparación entre una evaluación confirmada y el contexto actual utilizará
el contrato correspondiente a `rat_context_schema_version`.

Una diferencia de hash indicará que existe al menos un cambio material en el
contexto canónico.

La comparación estructurada deberá permitir derivar los motivos definidos en
la sección 21.10 sin modificar el snapshot histórico.

### 23.18 Inmutabilidad y evolución

El snapshot de una evaluación confirmada será inmutable.

Una nueva versión del algoritmo de canonización, composición del contexto o
semántica de campos no reescribirá snapshots históricos.

Los cambios incompatibles deberán introducir una nueva
`rat_context_schema_version`.

La implementación de M3-T1 deberá incluir tests que congelen el comportamiento
de la versión 1 antes de utilizarla para confirmar evaluaciones.

### 23.19 Snapshot documental v1

Para `rat_context_schema_version = 1`, `rat_context_snapshot` será una copia
estructurada del contexto factual de M2 utilizado para construir la evaluación
jurídica de una finalidad.

El snapshot documental será distinto del objeto canónico definido en §23.15.
Podrá conservar información adicional de trazabilidad expresamente definida en
esta sección, aunque dicha información no participe en `rat_context_hash`.

El snapshot utilizará los mismos bloques lógicos de primer nivel que el objeto
canónico v1:

- `purpose`;
- `organization_role`;
- `data_categories`;
- `data_subjects`;
- `data_sources`;
- `retention`;
- `automated_decisions`;
- `systems`;
- `third_parties`;
- `international_transfers`;
- `special_regimes`.

No se persistirán UUID de filas operativas de M2, timestamps ni campos de
auditoría dentro del snapshot documental. La identidad histórica del alcance
seleccionado se expresará mediante sus valores semánticos y no mediante
identificadores técnicos.

Los valores documentales conservarán el valor factual capturado en M2. La
canonización definida en §23.14 se aplicará únicamente al objeto canónico
utilizado para `rat_context_hash`, salvo que una regla específica de esta
sección indique lo contrario.

La construcción del snapshot y del objeto canónico deberá realizarse a partir
de la misma lectura lógica de M2 dentro de la operación de guardado o
confirmación, evitando combinar estados de contexto pertenecientes a momentos
distintos.

#### 23.19.1 Finalidad y rol de la organización

`purpose` conservará el texto factual de la finalidad seleccionada en M2.

`organization_role` conservará el valor estructurado de M2 o `null` cuando no
esté informado.

No se conservarán en el snapshot el UUID de `TreatmentPurpose`, `sort_order`
ni `is_primary`.

#### 23.19.2 Categorías de datos

`data_categories` contendrá exclusivamente las categorías seleccionadas para
la finalidad evaluada.

Para cada categoría se conservarán:

- `category_code`;
- `category_name`;
- `is_sensitive`;
- `notes`.

No se conservará el UUID de `TreatmentDataCategory`.

`notes` es información documental y no participa en el objeto canónico ni en
`rat_context_hash` v1.

#### 23.19.3 Categorías de titulares

`data_subjects` contendrá exclusivamente las categorías de titulares
seleccionadas para la finalidad evaluada.

Para cada categoría se conservarán:

- `category_code`;
- `category_name`;
- `includes_children`;
- `includes_adolescents`;
- `is_vulnerable_group`;
- `notes`.

No se conservará el UUID de `TreatmentDataSubject`.

`notes` es información documental y no participa en el objeto canónico ni en
`rat_context_hash` v1.

#### 23.19.4 Fuentes de datos

Para cada elemento de `data_sources` se conservarán:

- `source_type`;
- `description`;
- `is_public_source`.

M2 no dispone actualmente de información documental adicional para este
bloque que deba incorporarse al snapshot v1.

No se conservará el UUID de `TreatmentDataSource`.

#### 23.19.5 Conservación

`retention` conservará:

- `retention_rule`;
- `deletion_method`.

`deletion_method` tendrá finalidad documental y de trazabilidad operativa y no
participará en `rat_context_hash` v1.

#### 23.19.6 Decisiones automatizadas

`automated_decisions` conservará:

- `has_automated_decisions`;
- `description`.

`description` corresponderá al valor factual de
`automated_decision_description` de M2. El snapshot podrá conservarlo aunque
`has_automated_decisions` sea `false`; en ese caso el objeto canónico seguirá
aplicando la regla de §23.15 y utilizará `description = null` para el hash.

#### 23.19.7 Sistemas

`systems` conservará una representación documental de los sistemas asociados
al tratamiento en M2.

Para cada sistema se conservarán:

- `name`;
- `provider`;
- `hosting_location`;
- `hosting_country`;
- `is_international`.

No se conservarán el UUID de `System` ni el UUID de `TreatmentSystem`.

Todos los campos de `systems` tendrán finalidad exclusivamente documental en
v1. Conforme a §23.15, el bloque `systems` del objeto canónico utilizado para
`rat_context_hash` continuará siendo siempre `[]`.

`is_international` se conservará únicamente como dato legacy de trazabilidad
de M2 y no se utilizará para inferir la existencia ni las características de
una transferencia internacional.

#### 23.19.8 Terceros

`third_parties` conservará la relación factual entre el tratamiento y cada
tercero asociado en M2.

Para cada relación se conservarán:

- `vendor_name`;
- `country`;
- `relationship_type`;
- `purpose`;
- `has_data_access`;
- `has_contract`;
- `contract_reference`;
- `engagement_object`;
- `engagement_duration`;
- `has_subprocessors`;
- `notes`.

No se conservarán los UUID de `Vendor` ni de `TreatmentVendor`.

De estos campos, únicamente los definidos en §23.15 formarán parte del objeto
canónico y del hash v1:

- `relationship_type`;
- `has_data_access`;
- `country`;
- `has_subprocessors`;
- `purpose`.

`vendor_name`, `has_contract`, `contract_reference`, `engagement_object`,
`engagement_duration` y `notes` serán exclusivamente documentales.

Los atributos legacy de `Vendor` distintos de `name` y `country` no se
incorporarán al snapshot v1.

#### 23.19.9 Transferencias internacionales

Para cada elemento de `international_transfers` se conservarán:

- `recipient_name`;
- `destination_country`;
- `adequacy_status`;
- `mechanism`;
- `guarantees_description`;
- `evidence_reference`.

No se conservarán los UUID de `InternationalTransfer` ni `vendor_id`.

De estos campos, únicamente los definidos en §23.15 formarán parte del objeto
canónico y del hash v1:

- `destination_country`;
- `adequacy_status`;
- `mechanism`;
- `guarantees_description`.

`recipient_name` y `evidence_reference` serán exclusivamente documentales.

La identidad documental del receptor se expresará mediante `recipient_name`;
no se utilizará un UUID de `Vendor` como identidad histórica.

Para componer `recipient_name` en el snapshot v1 se aplicará la siguiente regla:

- si `InternationalTransfer.recipient_name` tiene valor, se conservará ese valor
  factual;
- si `InternationalTransfer.recipient_name` es `null` y existe `vendor_id`, se
  utilizará como `recipient_name` documental el `Vendor.name` correspondiente
  del mismo tenant.

Esta resolución mediante `Vendor.name` es exclusivamente documental. El
`vendor_id` no se incorporará al snapshot y esta regla no modificará el objeto
canónico ni el hash v1.

#### 23.19.10 Regímenes especiales

`special_regimes` conservará:

- `has_sensitive_data`;
- `includes_children`;
- `includes_adolescents`;
- `has_vulnerable_groups`.

Estos valores se derivarán exclusivamente de las categorías de datos y de
titulares seleccionadas para la finalidad evaluada, aplicando las reglas de
§23.15.

El snapshot no inferirá regímenes especiales a partir de nombres, notas,
descripciones libres, sistemas, terceros, transferencias ni filas de M2 que
estén fuera del alcance seleccionado.

Los valores de este bloque serán los mismos utilizados por el objeto canónico
v1.

#### 23.19.11 Ordenación documental determinista

Las listas del snapshot documental se almacenarán en un orden determinista
para facilitar pruebas, inspección y comparación histórica. Esta ordenación
documental no modificará los valores factuales capturados ni determinará el
`rat_context_hash`.

Se utilizarán las siguientes claves:

- `data_categories`: (`category_code`, `category_name`, `is_sensitive`,
  clave opcional de `notes`);
- `data_subjects`: (`category_code`, `category_name`, `includes_children`,
  `includes_adolescents`, `is_vulnerable_group`, clave opcional de `notes`);
- `data_sources`: (`source_type`, clave opcional de `description`,
  `is_public_source`);
- `systems`: (`name`, clave opcional de `provider`, clave opcional de
  `hosting_location`, clave opcional de `hosting_country`,
  `is_international`);
- `third_parties`: (`relationship_type`, `has_data_access`, clave opcional de
  `country`, `has_subprocessors`, clave opcional de `purpose`,
  `vendor_name`, `has_contract`, clave opcional de `contract_reference`,
  clave opcional de `engagement_object`, clave opcional de
  `engagement_duration`, clave opcional de `notes`);
- `international_transfers`: (`destination_country`, `adequacy_status`,
  clave opcional de `mechanism`, clave opcional de
  `guarantees_description`, clave opcional de `recipient_name`,
  clave opcional de `evidence_reference`).

Para la ordenación documental, un texto opcional `null` tendrá la clave
`(0, "")` y un texto no nulo la clave `(1, valor factual)`. No se aplicará
canonización al valor factual para esta ordenación.

La ordenación no deduplicará filas. La multiplicidad observada en M2 se
conservará en el snapshot.


### 15.10 Implementación del contrato especial y asociación EIPD v2

El borrador admite `special_conditions` con declaraciones factuales,
condiciones propuestas y evidencias. Los identificadores son cerrados; no se
admiten preguntas o regímenes repetidos ni selectores fuera del alcance RAT.
El servidor calcula la asociación sobre el snapshot completo, base jurídica,
consentimiento y LIA finales. El cliente no puede suministrar esa asociación.
La entrada puede ser parcial: persistir un expediente no acredita completitud
ni aplicabilidad ni autorización jurídica.

CREATE y PATCH vinculan los screenings suministrados mediante asociación v2:
snapshot RAT completo, LIA y condiciones especiales finales. El cuestionario
mantiene schema_version 1. Omitir un campo conserva su expediente y asociación;
null elimina las condiciones especiales como SQL NULL. Los screenings v1
históricos siguen intactos. Con condiciones especiales no nulas, su evaluación
informa `asociacion_especial_no_cubierta` y requiere revisión; no se reasocian
silenciosamente. Reenviar el screening genera la asociación v2 explícita.

La confirmación de condiciones especiales permanece bloqueada. El evaluador
de detección/preparación especial y los validadores jurídicos por régimen
siguen pendientes. M3-T1 permanece EN PROGRESO.


### 15.11 Evaluador de detección/preparación especial implementado

`evaluate_special_conditions_v1` es puro y conserva todos los motivos con
precedencia incompleto > requiere_revision > sin_regimenes_declarados.
Exige nueve declaraciones si/no fundadas y asociación vigente; compara los
cuatro indicadores RAT, revisa salud/biometría sin clasificación sensible y
el cruce sensible/adolescente afirmativo con subconjunto documentado. No
infiere ese cruce a partir de la coexistencia de indicadores. Detecta regímenes
coexistentes desde RAT y declaraciones, expedientes ausentes o residuales,
alcance inválido y referencias incoherentes al consentimiento. Vulnerabilidad
es un factor de revisión, sin autorización propia.

Todos los validadores por régimen/ruta permanecen no implementados; los
expedientes positivos nunca producen aprobación. GET readiness expone `special`
con result, context_current, detected_regimes e issues, usando contexto RAT
recompuesto. El evaluador no modifica expedientes ni asociaciones. El bloqueo
de confirmación existente permanece intacto incluso con declaraciones negativas.

La revisión de edades y requisitos jurídicos específicos no se resuelve con
texto libre. Sigue pendiente el contraste transversal entre la pregunta EIPD
sobre excepción al consentimiento y las rutas especiales propuestas; por ello
se mantienen los pending_controls de cobertura transversal, junto a los
validadores jurídicos pendientes. M3-T1 permanece EN PROGRESO.


### 15.12 Contraste documental EIPD/rutas especiales implementado

Con expediente especial explícito, el evaluador EIPD contrasta la pregunta
`datos_protegidos_excepcion_consentimiento` con las rutas propuestas:

- `excepcion_legal` siempre informa `excepcion_especial_no_validada`, pues los
  validadores por régimen todavía no existen; una respuesta EIPD negativa
  añade `excepcion_consentimiento_discordante` sobre las declaraciones;
- ruta null o `regla_especifica` informa `ruta_especial_pendiente`, porque no
  puede determinarse una excepción al consentimiento desde esa selección;
- respuesta EIPD afirmativa sin ruta `excepcion_legal` documentada informa
  `excepcion_consentimiento_no_documentada`; no se crea automáticamente una ruta.

Estos motivos fuerzan pendiente_revision y conservan los supuestos afirmativos,
las omisiones y los motivos de obsolescencia. No validan exigibilidad jurídica
de EIPD ni autorizaciones especiales. Una ruta de consentimiento con respuesta
negativa no añade contradicción EIPD; sigue sometida a preparación especial y
al bloqueo de sus validadores jurídicos. No se usa legal_basis para inferir
excepción. No se analizan nombres, referencias jurídicas ni prosa libre.

Se conserva la evaluación histórica sin expediente especial explícito. Los
screenings v1 con condiciones especiales mantienen además su aviso de asociación
no cubierta. El contraste es puro, ordena motivos por régimen y no modifica
asociaciones ni datos; readiness lo expone mediante los issues EIPD existentes.
Siguen pendientes los validadores específicos, la integración transaccional
EIPD/condiciones con confirmación y el expediente de EIPD exigible. M3-T1 EN PROGRESO.


### 15.13 Contrato de integración transversal en confirmación ordinaria

Decisión del siguiente bloque: la confirmación de un borrador de consentimiento
ordinario exigirá consentimiento preparado, detección especial negativa y
screening EIPD negativo, todos evaluados contra el mismo bundle RAT recompuesto.
Esta sección define comportamiento futuro; la implementación actual conserva
los bloqueos globales descritos en los checkpoints anteriores.

No se admitirá ausencia de los expedientes transversales como vía alternativa.
Los borradores existentes sin special_conditions o eipd_screening deberán
completarlos antes de confirmar bajo el nuevo flujo. Las versiones ya
confirmadas/reemplazadas conservan estado y contenido; no hay migración,
reasociación automática ni reevaluación que cambie su estado histórico.

| Control | Resultado exigido para continuar | Rechazo propuesto |
| --- | --- | --- |
| Estado y versión | Borrador y versiones admitidas | 409 |
| Base | consentimiento_art12 | 409 para otras bases |
| Justificación, alcance y rol RAT | Completos | 400 |
| Consentimiento | can_confirm del evaluador existente | 400 con sus motivos |
| Contexto semántico RAT | Hash coincide con RAT actual | 409 |
| Detección especial | sin_regimenes_declarados y context_current true | 400 si incompleto; 409 si requiere_revision |
| Screening EIPD | sin_supuestos_declarados y context_current true | 400 si ausente o incompleto; 409 si requiere_eipd o revisión de contexto/rutas |

Los motivos de ambos controles se conservarán, aun cuando uno bloquee primero.
Contrato inválido produce 400 y nunca se convierte en una evaluación negativa.
La clasificación EIPD para HTTP se hará desde motivos estructurados: ausencia,
pregunta omitida, respuesta pendiente y fundamento ausente son incompletitud;
asociación obsoleta/no cubierta y discordancias/rutas no validadas son revisión.
Si concurren ambos tipos, revisión tiene prioridad HTTP 409. Los detalles
incluirán resultado, contexto vigente y motivos; no un booleano de aprobación.

El expediente especial completo con nueve negativas fundadas, sin condiciones
residuales y coherente con RAT podrá superar el control especial. Vulnerabilidad
positiva, cualquier régimen detectado o ruta propuesta no validada continuará
bloqueando. Un consentimiento referenciado no desbloquea una ruta especial.
Una EIPD afirmativa no se supera con una referencia documental: la gestión de
EIPD realizada y revisada queda pendiente de un contrato propio.

Confirmación volverá a evaluar dentro de la transacción después de bloquear
la serie y refrescar el borrador. No consumirá resultados enviados por cliente
ni una respuesta GET readiness anterior. Usará un único bundle recompuesto
para hash RAT y evaluadores; no actualizará snapshots/asociaciones al confirmar.
Cambios documentales que no alteren el hash semántico también deben detectarse
mediante las asociaciones de special_conditions y EIPD. La serialización de
serie no equivale a bloquear todos los escritores M2; no se atribuye garantía
adicional de aislamiento RAT al lock M3.

Todas las validaciones ocurrirán antes de reemplazar la confirmada anterior.
Se conserva doble flush, índice parcial y commit/rollback a cargo del caller.
Un fallo deja la anterior confirmada y el borrador intactos. Permisos,
suscripción y RLS mantienen el contrato actual; no se añade permiso nuevo.

GET readiness y POST confirm compartirán la construcción de barreras del
nuevo flujo, evitando diferencias por ausencia de expedientes o resultados
negativos. Readiness seguirá siendo lectura orientativa: no promete éxito
posterior frente a cambios de estado/contexto ni autoriza jurídicamente.
Los pending_controls continuarán señalando validadores positivos y expediente
EIPD pendientes, sin presentar la integración ordinaria como M3-T1 terminado.

Aceptación previa a habilitar: ambos expedientes ausentes y cada uno ausente;
ambos negativos vigentes; parcial/pendiente/fundamento vacío; indicadores RAT
positivos y contradicciones; condiciones residuales; EIPD afirmativa y rutas
pendientes; asociaciones obsoletas aun con hash RAT idéntico; v1 histórico
no cubierto; fracaso sin reemplazo de anterior; relectura tras espera por lock;
confirmación concurrente; consistencia de motivos GET/POST; permisos, tenant y
RLS existentes. Los tests previos que confirmaban sin expedientes deberán usar
inputs negativos completos, conservando sus escenarios de concurrencia.


### 15.14 Integración transversal ordinaria implementada

Confirmación y readiness usan evaluate_transversal_readiness_v1 sobre el mismo
bundle RAT recompuesto por cada operación. La confirmación exige consentimiento
preparado, special.sin_regimenes_declarados y eipd.sin_supuestos_declarados con
ambas asociaciones vigentes. Los bloqueos globales por objeto no nulo fueron
sustituidos por evaluación documental; no se habilitan regímenes positivos.
Borradores sin los expedientes requeridos ya no pueden confirmar. Históricos
confirmados mantienen estado y datos.

POST conserva los motivos de ambos controles en detail.special/detail.eipd y
confirmation_blockers idénticos a readiness para las barreras transversales.
Se rechaza incompletitud con 400, revisión/EIPD afirmativa con 409; si ambos
controles bloquean, se toma el mayor código. Contrato inválido produce 400.
La respuesta de consentimiento y las validaciones anteriores conservan su
orden/contrato; GET puede mostrar además otros bloqueos de estado/contexto.

Todas estas validaciones ocurren tras lock/refresco y antes de reemplazar
la confirmada anterior. No se modifica ninguna asociación al confirmar ni se
hace commit en el servicio. PATCH vacío puede actualizar el snapshot RAT pero
no reasocia los controles omitidos; deberán reaportarse explícitamente.
Readiness conserva pending_controls para validadores especiales y expediente
EIPD/revisión pendientes; deja de señalar detección y screening ordinarios como
integraciones ausentes. M3-T1 sigue EN PROGRESO. LIA permanece bloqueada.


### 18.29 Contrato para habilitar confirmación ordinaria de interés legítimo

Revisión de cobertura: LIA v1 ya evalúa secciones, respuestas, medidas,
aplicabilidad y concordancia de finalidad con RAT; los controles especiales
negativos y EIPD negativos ya se comparten entre readiness y confirmación.
Persistencia, reemplazo, lock/refresco y RLS están implementados para el flujo
ordinario. Falta integrar la selección de base y la preparación LIA en POST,
retirar base_no_implementada para esta base en GET y cubrirlo en pruebas reales.
Este paso es documental; interés legítimo sigue bloqueado en el código actual.

La siguiente implementación admitirá exclusivamente consentimiento_art12 e
interes_legitimo_art13d en la confirmación ordinaria. Las otras bases conservarán
409. La selección de base determina el expediente que debe superar preparación:
consentimiento usa su evaluador actual; interés legítimo exige LIA completo,
recalculado contra el bundle RAT actual. Una decisión puede_basarse aislada
no supera el control. LIA ausente, parcial o incompleto devuelve 400; LIA
requiere_revision devuelve 409, conservando todos sus motivos y aplicabilidad.

Justificación, alcance, rol, hash RAT actual, detección especial negativa
vigente y screening EIPD negativo vigente siguen siendo obligatorios. Una LIA
completa no desbloquea datos sensibles, infancia/adolescencia, biometría,
geolocalización, investigación ni vulnerabilidad positiva. Tampoco desbloquea
EIPD afirmativa o pendiente. No hay habilitación automática de excepciones.
Valoraciones LIA altas permanecen antecedentes EIPD y factores documentales;
no se convierten por sí solas en autorización o prohibición nuevas.

No se exigirá consentimiento preparado cuando la base sea interés legítimo.
Si existe expediente de consentimiento residual, no se eliminará ni confirmará
como autorización adicional: sigue formando parte de la asociación especial.
Un contrato residual inválido se rechaza al validar documentos; las referencias
especiales incoherentes conservan sus motivos. No se modificarán cuestionarios
ni seleccionará una base diferente durante confirmación.

LIA no necesita una nueva asociación física para esta integración: special
ya vincula snapshot/base/consentimiento/LIA completos y EIPD v2 vincula
snapshot/LIA/special. Ambas asociaciones vigentes son obligatorias. Cambiar
LIA o base sin reaportar controles deja asociaciones obsoletas y bloquea, aun
cuando el hash semántico RAT no cambie. No se reasociará al confirmar.

La revalidación ocurre después del lock de serie y refresco del borrador;
se compone un único bundle RAT para hash, LIA y controles transversales. Todas
las validaciones anteceden al reemplazo. Se conserva doble flush, auditoría,
rollback del caller y versiones históricas inmutables. No se cambia esquema,
migración, permisos de edición, suscripción ni políticas RLS.

GET readiness y POST compartirán la construcción de resultado LIA/barrera
lia_no_preparada; se elimina base_no_implementada solo para la base recién
integrada. En el rechazo LIA, detail incluirá code, result, issues y
applicability compatibles con la salida LIA de readiness. El consentimiento
mantiene su respuesta anterior para evitar cambios ajenos a esta integración.
Los controles transversales conservan su contrato de rechazo independiente.
Readiness sigue siendo orientativo y no garantiza confirmación posterior.

Casos de aceptación: LIA completa con controles negativos confirma; decisión
favorable aislada/expediente ausente no confirma; respuestas desfavorables,
medidas condicionales incompletas, finalidad discordante y aplicabilidad sin
resolver bloquean con motivos; cambios factuales RAT o cambios LIA/base sin
reasociar bloquean; EIPD afirmativa y cualquier régimen positivo bloquean;
reemplazo de consentimiento por LIA y viceversa respeta la serie; rechazo o
fallo de flush conserva anterior; cambios de base/LIA tras espera por lock se
releen; creación/confirmación concurrentes preservan una confirmada; permisos,
suscripción, otro tenant y RLS mantienen protección. Actualizar expectativas
anteriores que asumían interés legítimo siempre no implementado.

M3-T1 permanece EN PROGRESO aun tras esta integración: otras bases jurídicas,
validadores por régimen/ruta especial y gestión de EIPD realizada/revisada
siguen pendientes de contratos y cobertura propios.


### 18.30 Confirmación ordinaria LIA implementada

POST confirm admite consentimiento_art12 e interes_legitimo_art13d. Las demás
bases conservan su bloqueo. Para interés legítimo, evaluate_lia_gate_v1 se
comparte con readiness y recalcula LIA contra el bundle RAT actual tras lock y
refresco. LIA incompleto/ausente produce 400, requiere_revision produce 409;
los motivos y aplicabilidad coinciden con GET. Decisión favorable aislada no
basta. GET ya no muestra base_no_implementada para interés legítimo.

LIA no exige un expediente de consentimiento preparado. Los controles
transversales negativos completos y vigentes siguen siendo obligatorios,
incluyendo asociación al documento LIA completo. No se añaden asociaciones
físicas, migraciones ni permisos. No se modifica ningún expediente al confirmar.
Otras bases, regímenes especiales positivos y continuación tras EIPD afirmativa
siguen bloqueados. M3-T1 EN PROGRESO.

Las pruebas reales cubren consentimiento -> LIA -> consentimiento en la misma
serie, rechazo previo sin reemplazar anterior, respuesta LIA compatible con
readiness y bloqueo EIPD afirmativo con LIA completa. Los escenarios PostgreSQL
de rollback/fallo de flush y concurrencia se ejecutan para ambas bases,
incluida modificación LIA incompleta mientras otra sesión espera por el lock.


## 19. Contrato y medidas precontractuales: siguiente base ordinaria

### 19.1 Alcance y decisión de producto

Siguiente bloque: contrato_precontractual_art13c. Referencia normativa:
[BCN, Ley 21.719, artículo 13 letra c](https://www.leychile.cl/leychile/Navegar/imprimir?idNorma=1209272&idParte=).
La disposición vincula la base a la necesidad del tratamiento para celebrar o
ejecutar un contrato entre titular y responsable, o a medidas precontractuales
solicitadas por el titular. El producto separará esas rutas y sus antecedentes.
Estas reglas operativas de documentación no certifican suficiencia jurídica.
Este paso no habilita la base: código actual continúa rechazándola con 409.

El expediente cubrirá la finalidad/alcance evaluados, sin identificar personas
con nombres, documentos o fechas de nacimiento. Casos con rutas incompatibles
por subconjunto deberán separar finalidades; el primer contrato no admite una
lista ambigua de contratos/personas para simular cobertura. Contrato laboral,
datos sensibles u otros indicadores especiales no eluden el control transversal.

### 19.2 ContractAssessmentV1 y persistencia propuesta

Nueva columna nullable contract_assessment JSONB con none_as_null=True y check
SQL NULL u objeto, mediante migración append-only. Conserva tenant y RLS actuales.
No se reutilizarán consent_assessment, lia_assessment, special_conditions ni
justification para ocultar un expediente de base diferente.

Contrato cerrado, extra forbid, schema_version literal 1:

- route: celebracion_contrato | ejecucion_contrato | medidas_precontractuales,
  nullable en borrador;
- purpose_description: texto opcional;
- relationship_description: descripción documental de las partes/relación,
  sin identificación personal;
- contractual_reference: referencia de contrato/proyecto, opcional en borrador;
- contractual_object: objeto documentado;
- processing_operations: operaciones necesarias para esa finalidad;
- necessity_analysis y data_minimization_analysis: análisis documentales;
- holder_is_party: respuesta si/no/pendiente;
- necessary_for_route: respuesta si/no/pendiente;
- purpose_within_route: respuesta si/no/pendiente;
- precontractual_measures: texto condicional;
- requested_by_holder: respuesta si/no/pendiente o null;
- request_reference: referencia documental condicional;
- evidence: lista de metadata documental con evidence_type, reference,
  obtained_on date opcional, mechanism y notes;
- notes: opcional.

Las respuestas serán objetos con answer y rationale opcional; no admitirán
no_aplica. Campos de respuesta generales nullable en borrador. Se rechazan
versiones/campos/rutas desconocidos; la completitud se deriva en evaluador puro.
Entrada CREATE/PATCH opcional: omisión conserva, objeto reemplaza la unidad,
null elimina solo en borrador. La salida conserva también contratos históricos.
No se reciben resultado ni bandera de aprobación del cliente.

### 19.3 Preparación operativa v1

Resultado incompleto > requiere_revision > completo, conservando todos los
motivos en orden físico. Contrato inválido produce error de validación.

Incompleto: expediente/snapshot ausente, route sin resolver, textos comunes
vacíos, respuestas generales ausentes/pendientes o sin fundamento, evidence
sin al menos una entrada con tipo y referencia no vacíos, o requisitos de
ruta sin resolver. Las tres respuestas generales deben ser si/no fundadas.

Celebración/ejecución exige contractual_reference y contractual_object.
Medidas precontractuales exige precontractual_measures, requested_by_holder
si/no fundado y request_reference; no exige un contrato ya firmado. Objeto
contractual se documenta también para contextualizar esas medidas.
requested_by_holder, request_reference y precontractual_measures son no
aplicables a las otras rutas; su contenido residual provoca revisión, no se
borra. Si route falta, aplicabilidad sin_resolver y resultado incompleto.

Requiere_revision sin faltantes: respuesta general no, requested_by_holder no
cuando aplica, finalidad distinta del snapshot tras canonización v1 o contexto
con rol distinto de responsable. El último control es un límite operativo del
primer bloque del producto; no afirma que toda actuación de un encargado sea
ilícita. También requiere revisión cualquier respuesta residual condicional.

Completo: sin faltantes ni motivos de revisión. No demuestra por sí solo la
necesidad jurídica; un contrato/referencia adjuntos no superan respuestas
negativas o análisis faltantes. No se analiza prosa mediante LLM para declarar
licitud ni se confunde necesaria_para_contrato del checklist de consentimiento
con la preparación independiente de esta base.

### 19.4 Asociación documental y compatibilidad

La preparación contractual debe quedar cubierta por las asociaciones, incluso
si cambia un texto sin alterar RAT. Nueva asociación especial v2 incluirá
snapshot, legal_basis, consentimiento, LIA y contract_assessment finales.
Nueva asociación EIPD v3 incluirá snapshot, LIA, contract_assessment y
special_conditions finales. Mantienen algoritmos deterministas existentes y
no cambian hash RAT canónico ni versiones de los cuestionarios.

No se reescribirán asociaciones existentes. Asociaciones especiales v1 y EIPD
v1/v2 con expediente contractual no nulo informarán contexto no cubierto y
revisión. Sin expediente contractual conservarán comparación histórica. Nuevo
guardado/reaporte usará nuevas versiones. Orden: base/cuestionarios/contrato,
snapshot, special_conditions, EIPD. Sin ciclos ni reasociación al confirmar.

### 19.5 Secuencia de implementación y aceptación

1. Schemas y nueva columna/migración, guardado y lectura del borrador; la base
   sigue bloqueada. Asociaciones especiales v2/EIPD v3 y compatibilidad histórica.
2. Evaluador puro con motivos, aplicabilidad y consulta readiness contractual.
3. Integración POST cuando completo y controles transversales negativos
   completos/vigentes. 400 incompleto/contrato inválido, 409 revisión; selección
   de base determina expediente requerido, sin exigir consentimiento o LIA.

Antes de habilitar: parcial/ausente, enums y campos inválidos, null/omisión,
rutas contractuales completas y precontractual completo sin contrato firmado,
solicitud ausente/negativa, fundamento faltante, finalidad distinta, encargado,
campos residuales, evidencia incompleta, contexto factual cambiado, versiones
históricas no cubiertas, controles positivos, GET/POST coherentes, reemplazo
entre bases, rollback, lock/relectura, concurrencia y aislamiento tenant/RLS.

M3-T1 sigue EN PROGRESO: obligaciones económicas, obligación legal, defensa
de derechos, validadores especiales y expediente EIPD permanecen pendientes.


### 19.6 Schemas/persistencia contractual implementados

Implementados ContractAssessmentV1 y columna contract_assessment nullable
JSONB con restricción SQL NULL/objeto; migración 8d2f4a6c9e31 posterior a
7c9e1a3b5d20 aplicada localmente. CREATE/PATCH guardan borradores parciales,
serializan fechas, conservan omisión y eliminan con SQL NULL. Salida GET incluye
el expediente. Validación de campos/enums/versiones cerrada; no hay evaluador
contractual ni habilitación POST para esta base todavía.

Nuevo guardado/reaporte vincula special_conditions mediante asociación v2 y
EIPD mediante v3, incorporando el contrato final. Se conservan comparadores y
constructores históricos. Asociación especial v1 o EIPD v1/v2 con contrato
no nulo informa asociacion_contractual_no_cubierta sin modificar los objetos.
Sin contrato conserva comparación histórica; v1 EIPD con especiales sigue
informando además su limitación previa cuando corresponde. Cambiar contrato
sin reaportar controles vuelve obsoletas las asociaciones y bloquea también
el flujo ordinario si el documento contractual es residual en otra base.

Pruebas cubren contrato parcial, fechas, rechazo de estructura y campos,
lectura/escritura ajenas al tenant, omisión/null, restricción SQL objeto,
asociación conjunta final, cambio contractual sin reasociar y compatibilidad
histórica. No se reescriben documentos ya confirmados. M3-T1 EN PROGRESO.


### 19.7 Evaluador contractual e integración readiness implementados

Evaluador puro evaluate_contract_assessment_v1: incompleto > requiere_revision
> completo, motivos en orden físico, sin mutación y con aplicabilidad estable.
Evalúa ruta, textos, respuestas/fundamentos, evidencia, finalidad RAT y rol.
Celebración y ejecución requieren referencia contractual; medidas previas
requieren medidas, solicitud del titular fundadamente afirmativa y referencia
de solicitud. No exigen contrato firmado. Referencia contractual aportada en
ruta precontractual se conserva como apoyo opcional y no constituye residuo;
no_aplicable indica que no es un requisito obligatorio en esa ruta.

Aclaración operativa de evidencia: se exige al menos una entrada y todas las
entradas aportadas deben tener tipo/referencia no vacíos. Una entrada completa
no oculta otras pendientes. obtained_on factual, mechanism y notes permanecen
opcionales. Respuestas a solicitud/medidas/referencia de solicitud fuera de
ruta aplicable producen revisión, sin borrar datos. Rol distinto de responsable
es revisión bajo el límite operativo definido en §19.3.

GET readiness añade contract (resultado, issues y applicability) para la base
contractual; null en otras bases. Recompone RAT antes de evaluar. Si no puede
recomponer el contexto, snapshot ausente produce incompleto. La barrera
contrato_no_preparado aparece cuando corresponde; base_no_implementada sigue
presente aun con contrato completo, pues POST contractual continúa bloqueado.
No se altera estado, fechas de auditoría ni asociaciones al consultar.

Pruebas cubren las tres rutas, faltantes, respuestas negativas/pendientes,
fundamentos vacíos, residuales, evidencia incompleta, ausencia de contexto,
canonización de finalidad, orden/inmutabilidad y lectura HTTP con tenant y RAT
actual. No se añaden migraciones ni se habilita confirmación. M3-T1 EN PROGRESO.


### 19.8 Confirmación contractual ordinaria implementada

POST confirm admite contrato_precontractual_art13c junto a consentimiento e
interés legítimo. evaluate_contract_gate_v1 comparte resultado y barrera con
readiness; contrato incompleto/ausente produce 400, requiere_revision produce
409. Los motivos/resultados/aplicabilidad del rechazo coinciden con GET.
GET elimina base_no_implementada para esta base. Las otras tres bases mantienen
el bloqueo actual.

Se exige expediente contractual completo y controles especiales/EIPD negativos
completos con asociaciones vigentes. No se exige consentimiento o LIA para
contrato. Las tres rutas superan la preparación bajo sus reglas, incluida
precontractual sin contrato firmado cuando la solicitud está documentada.
Regímenes positivos, EIPD afirmativa, documentos incompletos o asociaciones
obsoletas permanecen bloqueados. La evaluación ocurre tras lock/refresco y usa
el bundle RAT actual antes de reemplazar anterior. No reasocia ni modifica el
expediente; conserva doble flush, auditoría y commit/rollback del caller.

Pruebas incluyen rutas completas, ausencia/parcial, respuestas negativas,
finalidad distinta, cambio documental sin reaporte, indicadores especiales y
EIPD afirmativa. PostgreSQL verifica rollback/fallo de flush y concurrencia
para las tres bases, incluida actualización contractual mientras otra sesión
espera. API cubre consentimiento -> precontractual -> consentimiento, motivos
GET/POST y conservación de anterior ante rechazo. M3-T1 EN PROGRESO.


## 20. Obligación legal o tratamiento dispuesto por ley

### 20.1 Fundamento y alcance del siguiente bloque

Siguiente base: obligacion_legal_art13b. Referencia oficial:
[Diario Oficial, Ley 21.719, artículo 13 letra b, página 8](https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf).
El precepto cubre necesidad para ejecución/cumplimiento de una obligación legal
o tratamiento dispuesto por ley. El producto separará las rutas
cumplimiento_obligacion_legal y tratamiento_dispuesto_por_ley.

Seleccionar esta base o citar el artículo 13(b) no documenta por sí solo la
obligación/disposición concreta del tratamiento. Referencia, versión aplicable,
análisis y declaraciones se conservarán por finalidad/alcance RAT. No se
inventará una excepción desde una obligación contractual, política interna o
recomendación profesional. Las fuentes complementarias no sustituyen el
fundamento legal identificado y analizado por quien prepara el expediente.
Estas son reglas operativas documentales, no un dictamen automatizado.
La base continúa bloqueada en el código actual; este paso define el contrato.

### 20.2 LegalObligationAssessmentV1 propuesto

Nueva columna legal_obligation_assessment JSONB nullable, none_as_null=True,
check SQL NULL/objeto, migración append-only con tenant/RLS existentes.
No se reutilizarán justificación ni expedientes de otras bases.
Contrato cerrado extra forbid y schema_version literal 1:

- route: cumplimiento_obligacion_legal | tratamiento_dispuesto_por_ley,
  nullable en borrador;
- purpose_description: texto;
- normative_requirement_description: obligación o disposición concreta;
- processing_operations: operaciones fundamentadas;
- applicability_analysis: por qué alcanza a la organización y este contexto;
- necessity_analysis y data_minimization_analysis: análisis del alcance/datos;
- normative_references: lista de referencias cerradas con norm_name,
  provision, official_source_url, version_reference y relevance_analysis;
- normative_basis_reviewed: respuesta si/no/pendiente con rationale;
- normative_basis_in_force: respuesta si/no/pendiente con rationale;
- processing_within_legal_scope: respuesta si/no/pendiente con rationale;
- obligation_applies_to_controller: respuesta condicional;
- processing_required_by_law: respuesta condicional;
- evidence: metadata con evidence_type, reference, obtained_on date opcional,
  mechanism y notes;
- notes: opcional.

Textos, respuestas y campos de referencia podrán ser null en borrador; listas
vacías inicialmente. La respuesta condicional aplica solo a su ruta. Respuestas
admiten si/no/pendiente, sin no_aplica. Referencias usan URL http/https validada
sintácticamente cuando está presente; no se descargan fuentes desde esa entrada.
Version_reference documenta la versión/vigencia analizada como texto factual,
sin inferir fechas ni certificar actualización externa. Fechas de evidencia
se conservan; no se recopilan identidades personales para justificar la norma.

Omisión CREATE/PATCH conserva el contrato anterior cuando existe; objeto
reemplaza la unidad, null elimina solo en borrador. Campos/versiones/rutas
extraños se rechazan; resultado derivado o aprobación no vienen del cliente.
GET incluye expediente también en históricos.

### 20.3 Preparación operativa

Evaluador puro con incompleto > requiere_revision > completo, motivos en orden
físico y aplicabilidad estable. Revalida ambos contratos aun con input ausente.

Incompleto: expediente/snapshot ausente, ruta sin resolver, textos comunes
vacíos, respuestas aplicables ausentes/pendientes/sin fundamento, referencias
vacías o con cualquiera de sus cinco campos incompleto, evidencia vacía o
entrada aportada sin tipo/referencia. Cada referencia declarada debe estar
completa; una correcta no oculta otras pendientes.

Cumplimiento exige obligation_applies_to_controller si/no fundado.
Tratamiento dispuesto por ley exige processing_required_by_law si/no fundado.
La otra respuesta condicional es no aplicable; objeto residual provoca revisión
sin borrar contenido. Ruta ausente deja aplicabilidad sin_resolver.

Sin faltantes, respuesta aplicable no, finalidad distinta del snapshot tras
canonización v1 o rol distinto de responsable producen requiere_revision.
La restricción de rol es límite operativo del primer bloque, no afirmación de
ilicitud universal del encargado. Si hay faltantes y alertas, se conservan todos
los motivos pero prevalece incompleto.

Completo únicamente significa documentación resuelta con declaraciones
favorables bajo estas reglas. No confirma autenticidad, jerarquía, vigencia
real de la norma ni corrección del análisis jurídico. URL con dominio oficial,
texto largo, fecha o respuesta normativa positiva no constituyen verificación
automática. No hay búsqueda/RAG/LLM ni acceso de red desde este evaluador.
La evaluación jurídica documentada permanece responsabilidad de la organización.

### 20.4 Asociaciones y compatibilidad propuestas

Nueva asociación especial v3: snapshot, base, consentimiento, LIA, contrato y
legal_obligation_assessment finales. Nueva asociación EIPD v4: snapshot, LIA,
contrato, legal_obligation_assessment y special_conditions finales. Mismo hash
determinista, sin alterar hash RAT ni schema_version de cuestionarios.

No se reescriben asociaciones históricas. Especiales v1/v2 y EIPD v1/v2/v3 con
expediente de obligación legal no nulo informan asociación no cubierta y
revisión; sin él conservan comparación conforme a su versión, incluidas
limitaciones contractuales anteriores. Cambiar expediente sin reaportar
controles los vuelve obsoletos, también cuando el documento sea residual en
otra base. Guardado: base/expedientes, snapshot, especiales y finalmente EIPD.
No hay ciclos ni reasociación al confirmar.

### 20.5 Secuencia y aceptación

1. Schemas/columna/migración, persistencia/lectura y asociaciones especiales v3/
   EIPD v4 con históricos intactos; confirmación sigue bloqueada.
2. Evaluador puro y salida legal_obligation en readiness, conserva
   base_no_implementada hasta integración POST.
3. Gate compartido GET/POST: exige completo y controles transversales negativos
   vigentes, sin exigir consentimiento/LIA/contrato de otras bases. 400 si
   incompleto/contrato inválido, 409 revisión, contexto obsoleto o controles
   positivos. Relectura tras lock y evaluación con un bundle RAT antes de
   reemplazar anterior; mismo lifecycle y rollback del caller.

Aceptación: ambas rutas completas, parcial/ausente, enum/versiones/URLs
inválidos, omisión/null SQL, referencia/evidencia incompleta, fundamentos
faltantes, normativa no revisada/no vigente declarada, solicitud condicional
residual, finalidad distinta, rol no admitido, asociación histórica no cubierta,
fecha factual preservada, cambios sin reasociar, regímenes/EIPD positivos,
GET/POST coherentes, reemplazo entre bases, rollback, concurrencia/lock y RLS.

M3-T1 EN PROGRESO. Obligaciones económicas art13a, defensa de derechos art13e,
validadores especiales y gestión de EIPD siguen pendientes. Este diseño no
introduce una vía para confirmar esos supuestos por comentario libre.


### 20.6 Schemas/persistencia y asociaciones implementados

LegalObligationAssessmentV1 admite borradores cerrados/parciales, referencias
normativas con URL http/https sintácticamente validada y metadata de evidencia.
CREATE/PATCH/GET guardan el expediente en columna propia, preservan omisión y
fechas y eliminan con SQL NULL. Migración 9e3b5d7f1a42 posterior a 8d2f4a6c9e31
aplicada localmente con check SQL NULL/objeto. No hay acceso de red ni validación
automática de la norma al guardar una URL.

Nuevo guardado/reaporte usa asociación especial v3 y EIPD v4 con obligación
legal final, además de los documentos previamente incluidos. Lectura/evaluación
conserva asociaciones históricas y marca asociacion_obligacion_legal_no_cubierta
si un documento no nulo no está cubierto por su versión. Cambio sin reaportar
controles vuelve obsoletas las asociaciones. Sin documento de obligación legal
continúan los comparadores históricos, con sus limitaciones contractuales.

Pruebas cubren guardado parcial/fechas, estructura/URL/respuesta inválidas,
protección de escritura tenant, cambio sin reasociar, guardado conjunto,
check SQL objeto, SQL NULL, compatibilidad especial v1/v2/v3 y EIPD v1/v2/v3/v4.
Los flujos ordinarios existentes se conservan. El evaluador de preparación
normativa y readiness específico siguen pendientes; POST obligación legal sigue
bloqueado. M3-T1 EN PROGRESO.


### 20.7 Evaluador normativo y readiness implementados

Evaluador puro evaluate_legal_obligation_assessment_v1: incompleto >
requiere_revision > completo, motivos en orden físico y aplicabilidad estable.
Ambas rutas exigen textos comunes, tres respuestas normativas fundadas,
referencias completas y evidencia completa. Se exige la respuesta condicional
propia y se marca como revisión la residual de la otra ruta. Referencia/evidencia
completa no oculta otras entradas incompletas; URL solo se valida como http/https,
sin acceso de red, comprobación de dominio o certificación de vigencia jurídica.

GET readiness añade legal_obligation para obligacion_legal_art13b (null en
otras bases), evaluado contra RAT recompuesto. Muestra obligación incompleta,
revisión por finalidad/rol y motivos de referencia/fundamento. Si falta contexto,
el resultado es incompleto. Consulta conserva expedientes y asociaciones.
La barrera obligacion_legal_no_preparada aparece cuando corresponde;
base_no_implementada sigue presente aun con expediente completo: confirmación
continúa bloqueada en este paso. Sin migraciones adicionales.

Pruebas cubren ambas rutas, faltantes, referencias incompletas aun con otra
completa, negativas/pendientes/fundamentos, residuales, evidencia, precedencia,
canonización y orden, estructura/URL inválidas, lectura API/RAT actual,
protección tenant y ausencia de mutaciones. M3-T1 EN PROGRESO.


### 20.8 Confirmación ordinaria de obligación legal implementada

POST confirm admite obligacion_legal_art13b; catálogo de bases habilitadas es
compartido con readiness. evaluate_legal_obligation_gate_v1 usa el evaluador
normativo contra RAT recompuesto tras lock/refresco. Incompleto/ausente produce
400, requiere_revision produce 409; motivos/resultados/aplicabilidad coinciden
con GET. Readiness elimina base_no_implementada para esta base.

Ambas rutas requieren expediente completo y controles especiales/EIPD negativos
completos con asociaciones vigentes. No se exige preparación de consentimiento,
LIA o contrato de otra base. Regímenes positivos, EIPD afirmativa y asociaciones
obsoletas siguen bloqueados. Las referencias normativas continúan siendo
metadata y análisis declarados: confirmar el expediente no verifica externamente
su autenticidad, vigencia real o suficiencia jurídica.

Todas las validaciones anteceden al reemplazo. Se preservan documentos,
asociaciones, doble flush, auditoría y commit/rollback del caller. Pruebas reales
cubren consentimiento -> obligación legal -> consentimiento en ambas rutas,
rechazo sin reemplazo, normativa declarada no vigente, coherencia GET/POST y
rollback/fallo de flush/concurrencia PostgreSQL para cuatro bases. Actualización
normativa mientras otra sesión espera se relee. No hay migraciones ni permisos
nuevos. Art13a y art13e, validadores especiales y gestión EIPD siguen pendientes.
M3-T1 EN PROGRESO.


## 21. Formulación, ejercicio o defensa de derechos

### 21.1 Fundamento y frontera del primer contrato

Siguiente base: defensa_derechos_art13e. Referencia oficial:
[Diario Oficial, Ley 21.719, artículo 13 letra e, página 8](https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf).
El supuesto vincula la necesidad del tratamiento a la formulación, ejercicio o
defensa de un derecho ante tribunales de justicia u órganos públicos.
El producto separará esas tres rutas y el foro documentado. Seleccionar
esta base no identifica por sí solo el derecho ni demuestra necesidad.

Se documentará la finalidad/alcance RAT y las operaciones relacionadas con el
derecho, sin copiar escritos judiciales, datos personales de partes o nombres
de testigos al cuestionario. Referencias de expediente/evidencia serán metadata.
Preparación para formular un derecho no exige que ya exista una causa iniciada.
Fuera del foro previsto por esta base no habrá una categoría otra para eludir
revisión. Esta base general no habilita defensa_derechos_art16d ni otros
regímenes sensibles: sus validadores siguen pendientes y controles positivos
continúan bloqueando. Este paso es documental; POST art13e sigue rechazado.

### 21.2 RightsDefenseAssessmentV1 propuesto

Nueva columna rights_defense_assessment JSONB nullable con none_as_null=True,
check SQL NULL/objeto y migración append-only; mismos tenant, RLS y lifecycle.
Contrato cerrado extra forbid, schema_version literal 1:

- route: formulacion_derecho | ejercicio_derecho | defensa_derecho, nullable;
- purpose_description: finalidad;
- right_description y right_basis_reference: derecho concreto y fundamento
  documentado, sin exigir que toda referencia sea un artículo de ley;
- right_holder: responsable | tercero | ambos, nullable;
- holder_connection_analysis: relación de la organización/tratamiento con el
  derecho y su titular, sin identidad personal;
- forum_type: tribunal_justicia | organo_publico, nullable;
- forum_description: órgano o tribunal/documentación del foro pertinente;
- proceeding_stage: preparacion | en_curso | finalizado, nullable;
- proceeding_reference: referencia cuando existe expediente;
- preparatory_actions: actuaciones previstas al preparar la formulación;
- processing_operations, necessity_analysis, data_minimization_analysis:
  operaciones y análisis documentales;
- related_to_right, necessary_for_route, within_forum_scope:
  respuestas si/no/pendiente con rationale opcional;
- post_proceeding_necessity_analysis: análisis condicional tras finalización;
- evidence: metadata evidence_type, reference, obtained_on date opcional,
  mechanism, notes;
- notes: opcional.

Campos nullable/listas vacías en borrador; no resultado/aprobación del cliente.
Respuestas no admiten no_aplica. Omisión conserva, objeto reemplaza unidad,
null elimina solo borrador; GET conserva históricos y fechas factuales.
Valores/campos/versiones desconocidos se rechazan. No se consultan tribunales,
órganos públicos ni fuentes externas al guardar referencias.

### 21.3 Preparación y aplicabilidad operativa

Evaluador puro: incompleto > requiere_revision > completo, conserva todos los
motivos, orden físico y aplicabilidad estable. Revalida expediente y snapshot.

Incompleto: expediente/snapshot ausente, route/right_holder/forum_type/stage
sin resolver, textos comunes vacíos, respuesta general ausente/pendiente/sin
fundamento, evidencia vacía o entrada con tipo/referencia incompletos, o campo
condicional aplicable sin completar. Cada evidencia aportada debe completarse.
Los textos comunes son finalidad, derecho, fundamento, conexión del titular,
foro, operaciones, necesidad y minimización.

Preparacion aplica preparatory_actions y no exige proceeding_reference.
En_curso/finalizado exige proceeding_reference y no aplica preparatory_actions.
Finalizado aplica post_proceeding_necessity_analysis; otras etapas no lo exigen.
Etapa ausente produce aplicabilidad sin_resolver. Referencia de expediente en
preparación puede conservarse como apoyo opcional, sin sustituir actuaciones.
Contenido residual de actuaciones/análisis posterior en etapa no aplicable
produce revisión sin borrar datos.

Sin faltantes, respuesta general no, finalidad distinta de RAT por canonización
v1, rol distinto de responsable o etapa preparacion para ejercicio/defensa
produce requiere_revision. Este último caso es límite operativo inicial:
requiere revisar la ruta o el contexto, no declara ilícita toda preparación de
una defensa. Formulacion puede estar completa en preparación sin causa iniciada.
Etapa finalizado con análisis completo no obtiene por sí sola una alerta nueva,
pero debe justificar continuidad del tratamiento; no se infieren plazos de
conservación, prescripción o exigibilidad desde una fecha/nombre.

Completo es preparación documental, no certificación de existencia del derecho,
competencia del foro, legitimación procesal, necesidad jurídica ni eficacia de
la defensa. No se analiza prosa con LLM, no se presupone éxito y una referencia
de causa no sustituye respuestas o análisis faltantes.

### 21.4 Asociaciones y compatibilidad

Nueva asociación especial v4 incluye snapshot/base/consentimiento/LIA/contrato/
obligación legal/rights_defense_assessment finales. Nueva EIPD v5 incluye
snapshot/LIA/contrato/obligación legal/rights_defense_assessment/special finales.
Mismo algoritmo determinista, hash RAT y versiones de cuestionarios intactos.

Versiones anteriores no se reescriben: con expediente de derechos no nulo,
especiales v1/v2/v3 y EIPD v1/v2/v3/v4 informan asociación no cubierta; sin él
conservan comparación histórica y limitaciones documentales anteriores.
Cambio sin reaportar controles vuelve asociaciones obsoletas, incluso como
expediente residual en otra base. Orden de guardado conserva expedientes,
snapshot, especiales, EIPD. Sin ciclos o reasociación durante confirmación.

### 21.5 Secuencia y aceptación

1. Schemas/columna/migración y persistencia, asociaciones v4/v5 compatibles;
   confirmación art13e sigue bloqueada.
2. Evaluador y salida rights_defense en readiness; base_no_implementada permanece
   hasta integrar confirmación.
3. Gate GET/POST: completo y controles transversales negativos vigentes; 400
   incompleto/contrato inválido, 409 revisión/contexto/control positivo. No exige
   expedientes de otras bases. Revalida tras lock/refresco, mismo bundle RAT,
   antes del reemplazo y con rollback del caller.

Aceptación: tres rutas y dos foros completos; formulación sin causa iniciada;
parcial/ausente/enums/respuestas inválidos; solicitud de preparación en ruta
incoherente; etapa sin resolver; referencia y análisis posterior condicionales;
residuales; evidencia incompleta; finalidad/rol distintos; omisión/null SQL;
fechas factuales; asociaciones históricas no cubiertas y cambio sin reasociar;
regímenes/EIPD positivos; GET/POST coherentes; reemplazo entre bases; rollback,
relectura tras lock, concurrencia PostgreSQL y protección tenant/RLS.

M3-T1 EN PROGRESO. Obligaciones económicas art13a, regímenes especiales positivos
y gestión EIPD permanecen pendientes. No se añade una base residual genérica.


### 21.6 Schemas/persistencia y asociaciones implementados

RightsDefenseAssessmentV1 admite borradores cerrados/parciales con rutas,
foros, etapas y evidencia factual. CREATE/PATCH/GET preservan omisión y fechas,
reemplazan unidades y eliminan con SQL NULL. Migración ae4c6e8b2f53 posterior a
9e3b5d7f1a42 aplicada localmente con check SQL NULL/objeto y RLS existente.
No se accede a fuentes/tribunales al guardar referencias. El evaluador específico
y readiness de derechos siguen pendientes; confirmación art13e sigue bloqueada.

Nuevo guardado/reaporte usa asociación especial v4 y EIPD v5 con el expediente
final de derechos además de los documentos anteriores. Comparadores históricos
se conservan. Versiones especiales anteriores a v4 y EIPD anteriores a v5 con
derechos no nulos informan asociacion_derechos_no_cubierta, sin reescribir datos.
Con expediente ausente comparan según versión y mantienen limitaciones previas.
Cambios omitidos en controles conservan sus asociaciones y quedan obsoletos.

Pruebas incluyen estructura/enums/respuestas/fechas inválidas, persistencia
parcial, omisión, fecha factual, protección tenant, guardado conjunto final,
cambio sin reaportar, check SQL objeto, SQL NULL y versiones especiales
v1/v2/v3/v4 y EIPD v1/v2/v3/v4/v5. Bases ordinarias anteriores se conservan.
M3-T1 EN PROGRESO.


### 21.7 Evaluador de derechos y readiness implementados

Evaluador puro evaluate_rights_defense_assessment_v1: incompleto >
requiere_revision > completo, motivos ordenados y aplicabilidad por etapa.
Exige ruta/titular/foro/etapa, textos comunes, tres respuestas fundadas y
evidencia completa. Preparación aplica actuaciones previstas, sin exigir causa
iniciada; en_curso/finalizado aplica referencia; finalizado aplica análisis de
necesidad posterior. Referencia aportada en preparación es apoyo opcional.
Actuaciones/análisis posteriores residuales en etapa no aplicable producen
revisión, al igual que preparación en ejercicio/defensa, finalidad distinta o
rol no admitido. No se infieren plazos ni competencia jurídica desde referencias.

GET readiness añade rights_defense para art13e, null en otras bases, contra RAT
actual recompuesto. Barrera defensa_derechos_no_preparada cuando corresponda;
base_no_implementada permanece aun con preparación completa. POST derechos
sigue bloqueado. Lectura no modifica expedientes ni asociaciones.

Pruebas cubren tres rutas/dos foros, etapas y condicionales, ausencia/faltantes,
negativas/pendientes/fundamentos, residuales, evidencia, precedencia, estructura,
canonización, orden/inmutabilidad y API con tenant/contexto actual. No hay nuevas
migraciones ni habilitación de confirmación. M3-T1 EN PROGRESO.


### 21.8 Confirmación ordinaria de derechos implementada

Gate evaluate_rights_defense_gate_v1 compartido con readiness; art13e entra
al catálogo de bases confirmables. Expediente incompleto responde 400 y revisión
409 con resultado, motivos y aplicabilidad compatibles con GET. Completo exige
además justificación, contexto RAT actual y controles especiales/EIPD negativos
vigentes. No exige expedientes de otras bases ni valida competencia del foro.

Confirmación reevalúa el borrador leído después del bloqueo de serie y compone
RAT actual antes de modificar estados. Reemplazo en dos flush y transacción del
caller mantienen atomicidad. Pruebas HTTP cubren tres rutas/dos foros, rechazo,
conservación de vigente, reemplazo y protección del confirmado. Pruebas reales
PostgreSQL/app_user amplían rollback/fallo de flush y concurrencia a cinco bases,
incluido cambio a pendiente mientras otro confirmador espera el bloqueo.
Art13a, regímenes especiales positivos y gestión EIPD permanecen pendientes.
Sin migraciones nuevas ni commit. M3-T1 EN PROGRESO.


## 22. Obligaciones económicas, financieras, bancarias o comerciales

### 22.1 Fundamento y frontera del contrato inicial

Base obligaciones_economicas_art13a. El art13(a) vincula los datos con
obligaciones económicas/financieras/bancarias/comerciales y exige conformidad
con Título III; incluye situación socioeconómica. No basta finalidad comercial.
Referencia: [Diario Oficial, Ley 21.719, art13(a), página 8 y modificaciones
arts17–19, página 14](https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf).
Para revisar Título III usar [BCN, Ley 19.628, versión diferida 2026-12-01](https://www.bcn.cl/leychile/Navegar/imprimir?idNorma=141599&idParte=&idVersion=2026-12-01),
sin confundirla con la versión vigente antes de esa fecha. El régimen contiene
restricciones de comunicación, exclusiones, efectos del pago/extinción y
supresión de obligaciones prescritas. Requiere examinar normas y hechos del caso.

Decisión de producto: expediente documental, sin consultar registros de deuda,
calcular prescripción ni inferir habilitación desde un monto, fecha o nombre.
Distinguir operaciones sin comunicación de las que incluyen comunicación;
ambas documentan régimen aplicable. No se presume que toda deuda puede
comunicarse. Las excepciones de comunicación a tribunales requieren revisión
específica y quedan fuera de la primera ruta ordinaria confirmable; no se
habilitan mediante una respuesta genérica ni se redirigen automáticamente a
art13e. Una finalidad comercial o interés de cobro no reemplaza este expediente.

Situación socioeconómica mantiene el tratamiento factual existente de datos
sensibles. Art13a no fuerza flags RAT a negativos ni desactiva validadores
especiales; el primer gate exige controles especiales/EIPD negativos vigentes.
Un caso con controles positivos seguirá bloqueado hasta implementar su régimen.
Las rutas describen alcance operativo, no nuevos supuestos legales.

### 22.2 EconomicObligationsAssessmentV1 propuesto

Nueva columna economic_obligations_assessment JSONB nullable, none_as_null=True,
check SQL NULL/objeto, migración append-only tras ae4c6e8b2f53. Mismos tenant/RLS,
serie y lifecycle; sin tabla nueva ni cambios al hash canónico RAT.
Contrato cerrado extra forbid, schema_version literal1:

- route: sin_comunicacion | con_comunicacion, nullable;
- obligation_type: economica | financiera | bancaria | comercial, nullable;
- purpose_description, obligation_description, obligation_reference:
  finalidad y obligación/soporte concreto, metadata sin datos personales;
- holder_connection_analysis: relación del titular de datos con la obligación;
- processing_operations, applicability_analysis, data_minimization_analysis:
  operaciones, encaje documentado en régimen y alcance mínimo;
- title_iii_analysis, retention_and_deletion_analysis,
  accuracy_and_update_analysis: revisión del régimen, conservación/supresión y
  mecanismos de actualización; no se convierten en plazos legales automáticos;
- normative_references: lista NormativeReferenceV1, al menos una completa;
- operations_include_communication: ContractResponseV1 factual sobre las
  operaciones; si/no son valores coherentes según route, pendiente sin resolver;
- related_to_obligation, title_iii_reviewed, processing_within_title_iii,
  retention_and_deletion_compatible, accuracy_controls_documented:
  ContractResponseV1 si/no/pendiente con rationale;
- communication_scope, communication_eligibility_analysis,
  communication_restrictions_analysis, payment_and_extinction_controls:
  textos condicionales para con_comunicacion;
- communication_permitted, excluded_data_screened,
  communication_limits_respected: respuestas condicionales ContractResponseV1;
- evidence: lista ContractEvidenceV1 con metadata/fechas factuales;
- notes: opcional.

Todos los enums/textos/respuestas nullable y listas vacías permitidos en borrador.
El tipo identifica el carácter documentado predominante y no decide elegibilidad
ni impide describir otros caracteres concurrentes en obligation_description.
No se incorpora enum de estado de deuda que autorice/rechace por sí solo.
Respuesta no_aplica no admitida; la aplicabilidad la calcula el servidor.
Omisión conserva, objeto reemplaza unidad, null elimina en borrador. GET conserva
históricos; campos/enums/versiones desconocidos y fechas inválidas se rechazan.
No resultado/aprobación aportados por cliente ni búsquedas externas al guardar.

### 22.3 Completitud y aplicabilidad

Evaluador puro evaluate_economic_obligations_assessment_v1: incompleto >
requiere_revision > completo, todos los motivos ordenados por campos y evidencia,
sin mutaciones. Valida contrato y snapshot independientemente. Can_confirm
significa preparación documental, no certificación de legalidad de la deuda.

Incompleto: expediente/snapshot ausente, route/obligation_type sin resolver,
texto común vacío, respuesta común ausente/pendiente/sin rationale, referencias
normativas vacías/incompletas o evidencia vacía/incompleta. Cada referencia
aportada exige nombre, disposición, URL oficial sintáctica, versión y análisis;
cada evidencia aportada exige tipo/referencia. Textos comunes: los enumerados
antes de normative_references, incluida revisión del Título III y mecanismos.
Las referencias deben documentar arts17–19 y otras reglas aplicables en el
análisis; no se inspecciona prosa para inferir cobertura ni se verifica URL.

Con_comunicacion aplica los cuatro textos y tres respuestas condicionales.
Sin_comunicacion no los exige; contenido residual no vacío/respuesta aportada
produce revisión y se conserva. Ruta ausente: aplicabilidad sin_resolver y
sin exigir todavía esos campos. Contenido en notes no reemplaza requisitos.

Respuesta aplicable no con fundamento, finalidad distinta de RAT por
canonización v1, rol distinto de responsable o discordancia de operaciones
produce revisión. operations_include_communication ausente/pendiente/sin
fundamento es incompleto; si exige con_comunicacion y no exige sin_comunicacion.
Discordancia explícita entre esta respuesta y route produce revisión. Snapshot
RAT v1 no contiene un catálogo de operaciones: no se inventan códigos ni se
clasifica processing_operations mediante prosa. Terceros/transferencias RAT se
revisan en applicability_analysis, sin asumir que todo encargado o transferencia
equivale a la comunicación regulada por Título III. No inferir prescripción,
exigibilidad o admisibilidad desde fechas de evidencia. El análisis documental
de conservación no exige como regla propia un plazo fijo para toda operación.

Completo exige respuestas jurídicas aplicables si con fundamento y respuesta
factual operations_include_communication coherente con route, sin faltantes ni motivos
de revisión. El producto no transforma una afirmación del usuario en verificación
externa de exclusiones, pago o vigencia normativa. Primer soporte ordinario
excluye excepciones judiciales: si dependen de ellas, processing_within_title_iii
o communication_permitted se deja pendiente y se documenta revisión requerida.

### 22.4 Asociaciones y compatibilidad

Asociación especial v5 añade economic_obligations_assessment a snapshot/base/
consentimiento/LIA/contrato/obligación legal/derechos finales. Asociación EIPD v6
lo añade a snapshot/LIA/contrato/obligación legal/derechos/especiales finales.
Versiones de cuestionario siguen1; hash y canonización RAT intactos.

Comparadores especiales v1–v4/EIPD v1–v5 se conservan. Con expediente económico
no nulo informan asociacion_economica_no_cubierta; sin él mantienen comparación
y limitaciones históricas. Sin reescribir históricos ni reasociar al confirmar.
Cambio económico sin reaporte de controles vuelve asociaciones obsoletas incluso
si es documento residual en otra base o el hash RAT no cambia. CREATE/PATCH
compone documentos finales, snapshot, especiales y EIPD en ese orden.

### 22.5 Secuencia y aceptación

1. Schemas/columna/migración/persistencia y asociaciones v5/v6 compatibles;
   confirmación art13a bloqueada.
2. Evaluador y economic_obligations nullable en readiness, con motivo
   obligaciones_economicas_no_preparadas; base_no_implementada permanece.
3. Gate compartido GET/POST: completo, justificación, RAT actual y controles
   transversales negativos vigentes. Incompleto/contrato inválido400; revisión,
   contexto obsoleto/control positivo409. No exige expedientes de otras bases.
   Relectura tras lock, revalidación antes de modificar estados, rollback del
   caller y reemplazo entre bases con dos flush existentes.

Aceptación: ambas rutas/cuatro tipos; condicionales sin resolver y residuales;
textos/respuestas/referencias/evidencias incompletos; negativas/pendientes y
precedencia; finalidad/rol/operaciones discordantes; ausencia/snapshot inválido;
inmutabilidad y motivos ordenados; versiones/enums/fechas/campos inválidos;
omisión/null SQL/check objeto; guardado conjunto y cambio sin reaporte;
asociaciones históricas con y sin expediente; controles sensibles/EIPD positivos;
tenant/RLS; HTTP GET/POST coherentes; rechazo sin reemplazo, reemplazo, rollback,
fallo de flush, relectura tras lock y concurrencia real para seis bases.

Este paso modifica documentación únicamente; art13a sigue bloqueado en código.
M3-T1 EN PROGRESO. Regímenes especiales positivos y gestión EIPD pendientes.


### 22.6 Schemas/persistencia y asociaciones implementados

EconomicObligationsAssessmentV1 implementa borradores cerrados/parciales con
rutas, tipo, declaraciones, textos condicionales, referencias normativas y
metadata de evidencia. CREATE/PATCH/GET admiten omisión, reemplazo de unidad y
null SQL; fechas factuales se preservan. Migración bf5d7f9c3a64 posterior a
ae4c6e8b2f53 añade JSONB nullable/check objeto, con RLS/lifecycle existentes.

Nuevas escrituras usan asociación especial v5/EIPD v6 con todos los expedientes
finales, incluido económico. Comparadores anteriores se conservan; económico
no nulo con especiales v1–v4/EIPD v1–v5 informa asociacion_economica_no_cubierta.
Sin expediente conserva comparación histórica y sus limitaciones (EIPD v1 no
cubre especiales). Cambios sin reaporte no reasocian ni reescriben históricos.

Pruebas HTTP PostgreSQL/app_user cubren fechas, estructura/enums/respuestas
inválidos, aislamiento tenant, omisión/null SQL/check objeto, cambio sin reaporte,
guardado conjunto y todas las versiones históricas. Schemas prueban dos rutas
por cuatro tipos y contratos cerrados. Evaluador/readiness específicos pendientes;
confirmación art13a continúa bloqueada. M3-T1 EN PROGRESO. Sin commit.


### 22.7 Evaluador económico y readiness implementados

Evaluador puro evaluate_economic_obligations_assessment_v1 exige campos comunes,
referencias y evidencias completas, declaraciones jurídicas fundadas y factual
de comunicación coherente con ruta. Con_comunicacion aplica cuatro textos y
tres respuestas; sin_comunicacion no los exige y conserva residuales como
revisión; ruta ausente deja aplicabilidad sin_resolver. No se clasifica prosa,
consulta fuentes, calcula prescripción ni declara admisibilidad de una deuda.

Precedencia incompleto > requiere_revision > completo; conserva todos los
motivos ordenados, sin mutar expediente/snapshot. Evalúa finalidad canonizada y
rol contra RAT actual. GET readiness expone economic_obligations solo en art13a;
otras bases null. Barrera obligaciones_economicas_no_preparadas según motivos;
base_no_implementada permanece aun con preparación completa. POST bloqueado.

Pruebas cubren ambas rutas/cuatro tipos, faltantes, respuestas/precedencia,
declaración factual, condicionales/residuales, referencias/evidencias incompletas,
finalidad/rol, canonización, orden/inmutabilidad y HTTP con tenant/contexto actual.
Sin nuevas migraciones ni commit. M3-T1 EN PROGRESO.


### 22.8 Confirmación ordinaria económica implementada

Gate evaluate_economic_obligations_gate_v1 compartido con readiness. Art13a
integra el catálogo de seis bases confirmables ordinarias. Incompleto responde
400 y revisión409 con resultado, motivos y aplicabilidad compatibles con GET.
Completo exige justificación, RAT actual y controles especiales/EIPD negativos
vigentes. No exige expedientes de otras bases ni verifica deuda/fuente externa.

Relectura del borrador después del bloqueo, recomposición RAT y validación antes
de modificar estados mantienen el reemplazo atómico y rollback del caller.
Pruebas HTTP cubren ambas rutas/cuatro tipos, rechazo/conservación/reemplazo,
motivos comunes GET/POST y protección de confirmado. Pruebas reales PostgreSQL
amplían rollback/fallo de flush y concurrencia a seis bases; cambio documental
a pendiente mientras otro confirmador espera el bloqueo vuelve a evaluarse.

Regímenes especiales positivos y gestión EIPD siguen pendientes, así como
excepciones judiciales del régimen económico. No se certifica el cumplimiento
del Título III por completar el cuestionario. Sin nuevas migraciones ni commit.
M3-T1 EN PROGRESO.


## 23. Cobertura ordinaria y primer validador especial: geolocalización

### 23.1 Revisión conjunta de cobertura

Revisión contra código y pruebas actuales, no inferida del catálogo conceptual:

| Base | Gate documental | Flujo HTTP | Rollback/flush/concurrencia PostgreSQL |
| --- | --- | --- | --- |
| consentimiento_art12 | Checklist de consentimiento | Confirmación/reemplazo | Cubierto |
| obligaciones_economicas_art13a | Expediente económico | Ambas rutas/cuatro tipos | Cubierto |
| obligacion_legal_art13b | Expediente normativo | Ambas rutas | Cubierto |
| contrato_precontractual_art13c | Expediente contractual | Tres rutas | Cubierto |
| interes_legitimo_art13d | LIA | Confirmación/rechazo/reemplazo | Cubierto |
| defensa_derechos_art13e | Expediente de derechos | Tres rutas/dos foros | Cubierto |

CONFIRMABLE_ORDINARY_BASES contiene las seis bases. GET/POST usan gates comunes
para cinco expedientes; consentimiento conserva evaluador común y formato de
motivos propio ya probado. Todas requieren justificación, alcance, RAT vigente
y barreras transversales. Tests reales de confirmación cubren seis bases con
app_user/RLS; esos tests simulan composición RAT. HTTP recompone RAT real.
No implica que toda combinación entre bases/regímenes haya sido probada ni
que los validadores especiales estén implementados. Última suite914 passed.

### 23.2 Elección y alcance

Primer régimen especial: geolocalizacion_art16sexies. El art16sexies mantiene
las fuentes de licitud de arts12/13 y exige informar al titular sobre tipo de
datos, finalidad, duración y comunicación/cesión para servicios de valor añadido,
con claridad, suficiencia y oportunidad.
Fuente: [Diario Oficial, Ley 21.719, art16sexies, página14](https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf).

Decisión de producto: validar preparación documental de esa información sin
crear una base nueva o exigir consentimiento para toda geolocalización. La base
general conserva su gate, incluida LIA cuando corresponda. Declaración explícita
de geolocalización activa el régimen; no se infiere desde nombres libres.
El primer soporte admite este régimen como único especial validado, sin excluir
regímenes concurrentes del resultado. Otros especiales positivos/vulnerabilidad
sin resolver siguen bloqueando. Screening EIPD no se fuerza a negativo: vigilancia,
volumen, automatización o riesgo contextual pueden mantener la confirmación
bloqueada aun con expediente de geolocalización preparado.

### 23.3 GeolocationAssessmentV1 propuesto

Columna independiente geolocation_assessment JSONB nullable, none_as_null=True,
check SQL NULL/objeto y migración append-only tras bf5d7f9c3a64. Mantiene series,
RLS y permisos; no cambia SpecialConditionsV1 ni su normalización histórica.
Contrato cerrado schema_version literal1, extra forbid:

- purpose_description, geolocation_data_description, processing_operations:
  finalidad RAT, tipos/precisión de datos y operaciones documentadas;
- duration_description: duración de tratamiento informada;
- scope: SpecialScopeV1 con categorías/titulares seleccionados;
- notice_reference, notice_version_reference, notice_delivery_mechanism:
  metadata del aviso y del medio de entrega, sin personas/coordenadas;
- notice_provided_on: date opcional factual; no prueba oportunidad por sí sola;
- notice_content_analysis: cómo cubre los elementos exigidos;
- information_clear, information_sufficient, information_timely,
  data_types_disclosed, purpose_disclosed, duration_disclosed,
  third_party_information_disclosed: ContractResponseV1 si/no/pendiente+rationale;
- value_added_third_party_transfer: ContractResponseV1 factual si/no/pendiente;
- third_party_disclosure_description: texto común, incluida explicación cuando
  no se prevé comunicación/cesión para servicios de valor añadido;
- value_added_service_description, third_party_recipient_description:
  textos aplicables cuando value_added_third_party_transfer es si;
- evidence: list ContractEvidenceV1, metadata de aviso/entrega/revisión;
- notes: opcional.

Textos/respuestas/scope nullable y listas vacías en borrador. No aprobación del
cliente ni estado legal de comunicación inferido. Omisión conserva, objeto
reemplaza unidad, null elimina en borrador; históricos inmutables. Se rechazan
campos/versiones/valores desconocidos y fechas inválidas; no consultas externas.
Scope no vacío, subconjunto válido de snapshot y coincide con la selección del
expediente geolocalizacion_art16sexies y su declaración afirmativa. Si esos dos
selectores difieren requiere revisión; no se presupone cobertura total de otros
regímenes ni se modifica M2 para hacerlos coincidir. No nombres/coordenadas de
titulares en este contrato, solo descripción y evidencia referenciada.

### 23.4 Evaluador y asociación

Evaluador puro evaluate_geolocation_assessment_v1 con expediente, snapshot y
special_conditions. Precedencia incompleto > requiere_revision > completo;
conserva motivos ordenados y aplicabilidad estable, sin mutar entradas.

Incompleto: expediente/snapshot ausente, campos comunes/scope ausentes o vacíos,
respuestas ausentes/pendientes/sin fundamento, evidencia vacía/entrada incompleta,
campos condicionales aplicables vacíos. Toda evidencia exige tipo y referencia.
Todos los textos de §23.3 salvo notes y los dos condicionales son comunes.
Value_added_third_party_transfer no presume que no sea negativo válido: si/no
resuelve aplicabilidad, pendiente/ausente deja sin_resolver. Condicionales
no aplicables con texto no vacío producen revisión y se conservan.

Revisión: respuesta jurídica no con fundamento, finalidad diferente de RAT por
canonizaciónv1, rol distinto de responsable, alcance inválido/discordante,
ruta especial distinta de regla_especifica, sensitive_condition_id presente o
uses_consent_assessment true en el expediente de geolocalización. Esta condición
no requiere referenciar el checklist; consentimiento como base general mantiene
su requisito propio. No comparar prosa del aviso con LLM ni inferir oportunidad
por fecha. Legal_reference/documentary_analysis y evidencia del expediente
especial genérico continúan exigidos/documentados por su preparación.

Añadir asociación especial v6 y EIPD v7 que incluyen geolocation_assessment
final junto a todos los documentos actuales. Hash RAT/canonización/cuestionarios
intactos. Comparadores anteriores se conservan; documento no nulo con asociación
anterior informa asociacion_geolocalizacion_no_cubierta. Documento ausente
mantiene comparación/limitaciones históricas. Cambios sin reaporte vuelven
asociaciones obsoletas; ningún GET/confirmación reasocia documentos.

### 23.5 Integración transversal sin autorización global

Primero schemas/persistencia/asociaciones, confirmación especial bloqueada.
Después evaluador geolocation nullable en readiness; geolocalización afirmativa
requiere expediente. Documento presente sin régimen detectado es residual y
no habilita confirmación ordinaria silenciosamente.

Integración posterior del detector especial: solo esta ruta puede sustituir
validador_no_implementado por sus motivos reales. Agregar resultado
regimenes_preparados cuando hay régimen(s) soportados completos, sin pendientes,
residuales ni discordancias; conservar sin_regimenes_declarados para negativos.
No interpretar un régimen preparado como ausencia del régimen. Gate acepta
ambos resultados únicamente con asociación vigente y controles EIPD preparados.

EIPD actualmente marca regla_especifica como pendiente. Ajustar exclusivamente
geolocalización preparada, evaluada por servidor contra mismos documentos/RAT;
ninguna otra regla específica obtiene esa excepción. Resultado derivado no se
acepta del cliente ni entra como hash circular. No validar excepciones sensibles
ni cambiar automáticamente respuestas del screening. Mantener respuesta sobre
excepciones al consentimiento coherente con rutas reales: geolocalización no
es excepción sensible y no fuerza esa pregunta a si por base art13. Si EIPD
requiere_eipd/pendiente_revision, confirmación sigue bloqueada.

Confirmación revalida base y régimen tras bloqueo/refresco con mismo bundle RAT,
antes de reemplazo. Incompleto400, revisión/contexto409, rollback del caller.
Pending_controls debe distinguir lo ya implementado de validadores/EIPD aún
pendientes; no anunciar que todas las condiciones especiales están habilitadas.

### 23.6 Aceptación y siguiente paso

Schemas/persistencia: fechas, contratos cerrados, omisión/null SQL/check objeto,
protección tenant/RLS, guardado conjunto y cambios sin reaporte; todas las
asociaciones históricas con/sin documento. Evaluador: ambas declaraciones
factuales, faltantes/negativas/pendientes, condicionales y residuales, referencias,
finalidad/rol/scope, canonización y orden/inmutabilidad. Integración: seis bases
con geolocalización sola preparada, ningún régimen concurrente ignorado,
EIPD positivo continúa bloqueado y regla_especifica de otro régimen bloqueada.
HTTP motivos GET/POST y rechazo sin reemplazo; rollback/fallo de flush y
concurrencia para ruta especial admitida; históricos no se reescriben.

Paso actual documental. Ninguna confirmación especial se habilita. M3-T1
EN PROGRESO. Próximo paso: schemas/persistencia y asociaciones de geolocalización;
luego evaluador y finalmente integración del gate especial/EIPD.


### 23.7 Schemas/persistencia y asociaciones implementados

GeolocationAssessmentV1 guarda borradores cerrados/parciales de aviso, entrega,
respuestas, scope y evidencia; fechas factuales se preservan. CREATE/PATCH/GET
admiten omisión, reemplazo de unidad y SQL NULL. Migración c06e8a1d4b75 posterior
a bf5d7f9c3a64 aplicada localmente: JSONB nullable/check objeto, RLS existente.
No cambia estructura ni normalización de SpecialConditionsV1.

Nuevas escrituras usan asociación especial v6/EIPD v7 con todos los documentos
finales, incluida geolocalización. Comparadores anteriores se conservan;
geolocalización no nula con especiales v1–v5/EIPD v1–v6 produce
asociacion_geolocalizacion_no_cubierta. Ausente conserva comparación/limitaciones
históricas. Cambios sin reaporte conservan asociación anterior y la desactualizan.

Documento sin régimen detectado produce expediente_geolocalizacion_residual;
régimen declarado conserva validador_no_implementado. Ninguno habilita
confirmación en este paso. Evaluador/readiness específicos pendientes.
Pruebas cubren fechas, schemas cerrados, omisión/null SQL/check objeto, tenant,
guardado conjunto/cambios sin reaporte, todas las versiones históricas y
confirmación expresamente bloqueada con régimen declarado. M3-T1 EN PROGRESO.


### 23.8 Evaluador de geolocalización y readiness implementados

Evaluador puro evaluate_geolocation_assessment_v1 exige preparación del aviso,
respuestas jurídicas fundadas, declaración factual de servicios a terceros,
evidencia y alcance coherente con RAT/declaración/condición específica. Compara
selectores por canonización v1, detecta vacíos/duplicados semánticos/subconjuntos
inválidos y discordancias. No certifica entrega ni oportunidad desde fechas.

Declaración factual si aplica servicio/destinatario; no los deja no aplicables y
contenido residual produce revisión; pendiente/ausente deja sin_resolver.
Precedencia incompleto > requiere_revision > completo, motivos estables y sin
mutaciones. Revalida todos los contratos y los selectores externos aunque falte
scope propio. Condición genérica requiere regla_especifica, referencia/análisis
y evidencia; referencia al checklist no sustituye el aviso.

GET readiness expone geolocation si hay expediente o régimen detectado; null
cuando ambos ausentes. Motivo geolocalizacion_no_preparada según resultado.
Preparación completa no elimina validador_no_implementado ni bloqueo EIPD:
confirmación especial continúa bloqueada. Bases ordinarias conservan sus gates.

Pruebas cubren ambas declaraciones factuales, faltantes/negativas/pendientes,
condicionales/residuales, scope propio/externo, finalidad/rol, referencias,
evidencia, contratos inválidos, canonización y orden/inmutabilidad; HTTP protege
tenant y muestra cambios del RAT actual sin reescribir documentos históricos.
Sin nuevas migraciones ni commit. M3-T1 EN PROGRESO.


### 23.9 Gate especial de geolocalización y coherencia EIPD implementados

Detector especial sustituye validador_no_implementado únicamente para
geolocalizacion_art16sexies por motivos del evaluador real. Resultado
regimenes_preparados conserva regímenes detectados y exige ausencia de motivos
incompletos/revisión, incluidos controles concurrentes. Negativos mantienen
sin_regimenes_declarados. Gate compartido GET/POST admite ambos con asociación
vigente; una preparación de geolocalización no suprime otros regímenes.

EIPD deja de marcar ruta_especial_pendiente solo para regla_especifica de
geolocalización preparada, evaluada por servidor contra mismos documentos/RAT.
Otras rutas/reglas específicas/excepciones conservan sus bloqueos. Todas las
preguntas EIPD se evalúan y sus positivos siguen bloqueando confirmación.
No inferir excepción sensible desde una base art13 ni forzar respuestas.

Readiness conserva geolocation y describe validacion_otros_regimenes_especiales
como pendiente, además de gestión EIPD. Incompleto/revisión mantienen motivos
GET/POST compatibles; cambios sin reaporte desactualizan asociaciones aun si el
aviso permanece completo. Confirmación reevalúa tras bloqueo antes de reemplazo.

Pruebas HTTP cubren geolocalización preparada con las seis bases, rechazo con
conservación de vigente, EIPD positivo, reemplazo en ambas direcciones y
protección de confirmado. Pruebas PostgreSQL/app_user amplían rollback/fallo de
flush y concurrencia a geolocalización para las seis bases; cambio del aviso a
pendiente durante espera se relee y rechaza. Pruebas puras cubren cada supuesto
EIPD, regímenes concurrentes/vulnerabilidad, residuales/asociaciones obsoletas y
reglas no implementadas, sin mutaciones. Otros regímenes especiales y gestión
EIPD siguen pendientes. Sin nuevas migraciones ni commit. M3-T1 EN PROGRESO.


## 24. Consentimiento expreso para datos sensibles

### 24.1 Fundamento y frontera inicial

Segundo validador especial: sensibles_art16 con authorization_route
consentimiento y sensitive_condition_id consentimiento_expreso_art16.
Art16 contempla consentimiento expreso mediante declaración escrita, verbal o
medio tecnológico equivalente. Salud/perfil biológico, biometría e infancia
mantienen condiciones específicas en preceptos posteriores.
Fuente: [Diario Oficial, Ley 21.719, art16, página12 y preceptos siguientes](https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf).

Decisión de producto: preparación documental, sin certificar identidad, contenido
ni vigencia de una declaración. El checklist ConsentAssessmentV1 no documenta
por sí solo carácter expreso y alcance sensible: su evidencia puede estar vacía
y grant_method acto_afirmativo no demuestra declaración expresa. Mantener ese
contrato/comportamiento histórico y añadir expediente específico independiente.
No cambiarlo para exigir retroactivamente evidencia a consentimientos ordinarios.

La base general y condición especial siguen separadas. Las seis bases conservan
sus gates; si se selecciona esta condición, el checklist general y expediente
expreso son obligatorios incluso cuando la base general es art13. No se cambia
la base ni se infiere consentimiento desde una finalidad o ausencia de excepción.
Rutas art16(a–f) permanecen no implementadas. Preparación de consentimiento
expreso no autoriza salud, biometría, infancia o investigación concurrentes ni
sustituye gestión EIPD. Geolocalización preparada puede coexistir con este
validador, manteniendo ambos expedientes y sus condiciones.

### 24.2 SensitiveConsentAssessmentV1 propuesto

Nueva columna sensitive_consent_assessment JSONB nullable, none_as_null=True,
check SQL NULL/objeto y migración append-only tras c06e8a1d4b75. Misma serie/RLS,
permisos y lifecycle; no modifica ConsentAssessmentV1 ni SpecialConditionsV1.
Contrato cerrado extra forbid, schema_version literal1:

- purpose_description, sensitive_data_description, processing_operations:
  finalidad RAT, tipos sensibles y operaciones cubiertas;
- scope: SpecialScopeV1 nullable en borrador;
- expression_method: escrito | verbal | tecnologico_equivalente, nullable;
- declaration_reference: metadata de declaración y su registro;
- declaration_version_reference: opcional; no exigir plantilla versionada para
  toda declaración verbal;
- declaration_obtained_on: date opcional factual;
- declaration_content_analysis: cómo documenta una declaración expresa respecto
  del tratamiento/alcance sensible;
- express_declaration_documented, sensitive_scope_explicit, purpose_specific,
  proof_available, consent_current: ContractResponseV1 si/no/pendiente+rationale;
- technology_equivalence_analysis: texto condicional para medio tecnológico;
- evidence: list ContractEvidenceV1, metadata, tipo/referencia requeridos para
  preparación; sin declaraciones completas ni identidades/coordenadas;
- notes: opcional.

Omisión conserva, objeto reemplaza unidad, null elimina en borrador. Fechas
factuales se conservan; campos/versiones/enums/respuestas desconocidos y fechas
inválidas rechazados. No approval del cliente, no consultas a registros ni
verificación automática de documentos al guardar referencias.

### 24.3 Completitud, coherencia y alcance

Evaluador puro evaluate_sensitive_consent_assessment_v1 recibe expediente,
ConsentAssessmentV1, snapshot y SpecialConditionsV1; revalida todos los contratos,
sin mutaciones. Precedencia incompleto > requiere_revision > completo, motivos
ordenados y aplicabilidad estable. Incluir motivos del checklist general con
prefijo consent_assessment y preservar question_id; no modificar su evaluador.

Incompleto: expediente/snapshot/checklist ausentes; checklist incompleto;
expression_method/scope sin resolver; textos comunes vacíos; respuestas
jurídicas ausentes/pendientes/sin fundamento; evidencia vacía o entrada
incompleta; campo tecnológico aplicable vacío. Textos comunes son finalidad,
tipos sensibles, operaciones, declaración/referencia y análisis. Versión y fecha
son apoyos opcionales. Tecnología aplica equivalencia; otros medios no la
requieren y texto residual produce revisión; método ausente deja sin_resolver.

Revisión: checklist requiere_revision; respuesta jurídica no con fundamento;
finalidad distinta por canonizaciónv1; rol distinto de responsable; ruta/ID
sensible distintos; uses_consent_assessment no true; alcance inválido/discordante;
medio contradictorio con checklist. Escrito corresponde a grant_method escrito,
verbal a verbal, tecnológico a electronico. Acto_afirmativo/otro_documentado no
se convierten automáticamente en declaración expresa; requieren revisión del
medio y actualización documental, sin declarar ilícitas esas categorías.

Primer soporte operativo confirma given_by titular. Representante legal o
mandatario mantiene datos pero requiere_revision hasta diseñar acreditación y
vinculación de representación en esta ruta sensible. Este límite de producto no
niega que exista representación jurídicamente válida. No inferir representante,
edad o capacidad desde nombres y no aprobar infancia mediante este límite.

Declaración datos_sensibles afirmativa, condición sensibles_art16 y scope propio
requieren selectores no vacíos, semánticamente únicos y coincidentes. Comparar
por canonizaciónv1; validar cada selector externo incluso si falta scope propio.
Categorías seleccionadas deben ser sensibles en snapshot, sin cambiar M2. Para
el primer gate, cubrir todas las categorías sensibles del alcance RAT de la
evaluación y todos sus grupos de titulares. Si la cobertura es menor, revisar
alcance M3 o esperar soporte granular; no confirmar silenciosamente datos fuera
del consentimiento documentado. Esta es una frontera conservadora del producto:
RAT v1 no contiene una matriz categoría/grupo que permita demostrar cobertura
parcial por pares. No inferirla desde prosa ni exigir consentimiento a categorías
ordinarias ajenas al subconjunto sensible.

Si RAT no tiene categorías sensibles/flag coherente, requiere revisión del
contexto/declaración. Documento sin régimen detectado es residual y bloquea.
La condición genérica conserva requisitos de referencia legal/análisis/evidencia.
Consent_current es declaración fundada de actualidad, no vigilancia externa de
revocaciones; fecha registrada no decide vigencia ni oportunidad por sí sola.

### 24.4 Asociaciones y compatibilidad

Nuevas asociaciones especiales v7 y EIPD v8 incluyen sensitive_consent_assessment
final junto a todos los documentos existentes. No alteran hash/canonización RAT,
cuestionarios ni normalización de contratos anteriores. Comparadores históricos
se conservan; sensible expreso no nulo con especial v1–v6/EIPD v1–v7 informa
asociacion_consentimiento_sensible_no_cubierta. Ausente conserva comparación y
limitaciones anteriores. Cambio del checklist o expediente sin reaporte vuelve
asociaciones obsoletas; no se reasocia durante GET/confirmación. Guardado ordenado:
documentos finales, snapshot, especiales y EIPD. Sin hashes circulares derivados.

### 24.5 Secuencia e integración transversal

1. Schemas/persistencia/asociaciones v7/v8 compatibles; ruta sensible bloqueada.
2. Evaluador y sensitive_consent nullable en readiness cuando hay expediente o
   condición sensibles_art16 de consentimiento propuesta. Motivo
   consentimiento_sensible_no_preparado; preparación no habilita gate aún.
3. Detector admite solo consentimiento_expreso_art16 preparado por evaluador.
   Mantiene regimenes_preparados con todos los regímenes detectados, nunca borra
   concurrentes. Rutas sensibles distintas siguen validador_no_implementado;
   referencias incompletas/representación/alcance bloquean antes de reemplazo.

EIPD no infiere excepción al consentimiento desde una base art13 ni cambia sus
respuestas. Esta ruta es consentimiento y no valida excepción sensible. Detectar
consentimiento especial pendiente/incoherente mediante evaluación del servidor;
ninguna ruta de otro régimen se considera preparada por compartir la palabra
consentimiento. Geolocalización conserva su exención limitada de ruta pendiente.
Cada pregunta EIPD y régimen concurrente mantiene sus propios motivos; positivo/
pendiente sigue bloqueando confirmación incluso con consentimiento expreso listo.

Gate GET/POST compartido: base preparada, todos los regímenes soportados
preparados, asociaciones vigentes y screening negativo. Revalidar tras bloqueo
con mismo bundle RAT antes de modificar estados; rollback del caller y dos flush
existentes. Motivos compatibles GET/POST; incompleto400/revisión409 según barreras
concurrentes. Pending_controls conserva otros validadores/gestión EIPD pendientes.

### 24.6 Aceptación

Tres medios coherentes con checklist, condicional tecnológico y residuales;
checklist ausente/incompleto/desfavorable, evidencia expresa obligatoria;
respuestas negativas/pendientes/fundamentos; ruta/ID/referencia incoherentes;
given_by representante/mandatario conserva revisión; alcance vacío/duplicado/
fuera de RAT/no sensible/parcial/discordante, selectores externos independientes;
finalidad/rol, contratos inválidos, fechas factuales, orden/inmutabilidad.
Persistencia omisión/null SQL/check objeto, tenant/RLS, guardado conjunto y cambio
sin reaporte; todas las asociaciones históricas con/sin expediente.

Integración: seis bases con sensibles simples preparados; coexistencia con
geolocalización; salud/biometría/infancia/investigación/vulnerabilidad pendientes
siguen bloqueados; cada supuesto EIPD positivo bloqueado. HTTP rechazo conserva
vigente, reemplazo en ambas direcciones y protección de confirmado; rollback,
fallo de flush/relectura tras lock y concurrencia PostgreSQL de ruta sensible.

Paso actual documental: ninguna nueva ruta sensible se habilita. Última suite
1044 passed. M3-T1 EN PROGRESO. Próximo paso: schemas/persistencia y asociaciones;
después evaluador y finalmente integración transversal.


## 25. Contrato del expediente sensible — avance incremental

Implementado SensitiveConsentAssessmentV1 de §24 como contrato independiente.
Admite borradores parciales y conserva fechas documentales; cierra campos,
versión y medios, reutilizando alcance, respuestas y evidencia existentes.
No incorpora todavía el expediente a entradas/salidas HTTP ni persistencia:
la siguiente etapa debe incorporarlo junto con asociaciones v7/v8 y bloqueo
residual para evitar que un documento nuevo eluda el gate vigente.

Validación focalizada 58 passed, incluidas 30 pruebas nuevas del contrato.
Última suite completa anterior 1044 passed; no se repitió en esta etapa de
contrato aislado. M3-T1 EN PROGRESO, sin commit ni migración nueva.


## 26. Persistencia y asociaciones del expediente sensible

Completada etapa 24.5.1: entrada CREATE/PATCH y salida GET para expediente
sensible; columna JSONB nullable con none_as_null y check objeto. Migración
aditiva d17f9b2e5c86 después de c06e8a1d4b75, aplicada en desarrollo local.
Omisión conserva, objeto reemplaza y null borra borrador; fechas se conservan.

Guardados actuales especiales v7/EIPD v8 incluyen documento final. Constructores
y comparadores previos siguen disponibles. Especiales v1–v6/EIPD v1–v7 con
expediente sensible no nulo requieren revisión por
asociacion_consentimiento_sensible_no_cubierta; con null conservan comparación
histórica. Cambiar expediente sin reaportar controles vuelve hashes obsoletos.
Lectura y confirmación no actualizan asociaciones.

Expediente sin régimen sensible detectado agrega
expediente_consentimiento_sensible_residual y bloquea. Régimen sensible declarado
mantiene validador_no_implementado: esta etapa no habilita confirmación.

Suite completa 1082 passed; formato/lint/whitespace correctos. M3-T1 EN PROGRESO,
sin commit. Próximo paso: evaluador y preparación sensible nullable en readiness;
posteriormente integración del gate compartido.


## 27. Evaluador y preparación sensible en readiness

Completada etapa 24.5.2: evaluate_sensitive_consent_assessment_v1 recibe
expediente, snapshot, condiciones especiales y checklist; revalida contratos,
no modifica entradas y deriva incompleto > requiere_revision > completo.
Motivos ordenados con índices numéricos, question_id conservado y prefijo
consent_assessment; aplicabilidad incluye checklist y equivalencia tecnológica.

Textos/respuestas/evidencia obligatorios, medio coherente y finalidad/rol según
§24. Alcance propio, declaración y condición se validan independientemente,
incluso sin scope propio. Selección debe cubrir exactamente categorías sensibles
y todos los grupos del alcance RAT; selectores extra/duplicados/fuera del RAT o
cobertura parcial requieren revisión. Representación permanece pendiente;
fechas/versiones no se convierten en requisitos de vigencia automáticos.

Readiness incluye sensitive_consent cuando hay documento o propuesta de condición
sensibles_art16 por consentimiento/consentimiento_expreso_art16; en otro caso null.
Preparación no completa agrega consentimiento_sensible_no_preparado. GET sigue
orientativo: completo no habilita confirmación, pues detector sensible mantiene
validador_no_implementado. EIPD y asociaciones conservan sus barreras.

Suite completa 1159 passed, incluidas 74 pruebas puras y HTTP con tres medios,
confirmación rechazada sin mutación, cambio pendiente/asociaciones obsoletas y
borrado con ruta propuesta. Formato/lint/whitespace correctos. Sin commit ni
migración nueva; M3-T1 EN PROGRESO. Próximo paso: etapa 24.5.3, detector/gate
compartido y coherencia EIPD para ruta sensible preparada.


## 28. Integración transversal del consentimiento expreso sensible

Completada etapa 24.5.3: detector admite únicamente sensibles_art16 con ruta
consentimiento e ID consentimiento_expreso_art16 si su evaluador está preparado.
Usa motivos del evaluador para incompletitud/revisión y conserva los restantes
regímenes. Otras rutas sensibles mantienen validador_no_implementado; no se
habilitan salud/biometría/infancia/investigación por compartir datos sensibles.

EIPD contrasta preparación de propuestas sensibles por consentimiento usando el
checklist actual. Propuesta sin preparación conserva ruta_especial_pendiente;
completa puede mantener screening negativo únicamente con respuestas/coherencia
y asociaciones vigentes. No infiere excepción desde art13. Geolocalización
conserva su exención limitada de ruta pendiente y no borra regímenes concurrentes.

Barrera consentimiento_sensible_no_preparado compartida GET/POST, con 400 para
incompleto y 409 para revisión; otras barreras pueden elevar el rechazo a 409.
GET expone preparación orientativa; POST reevalúa tras lock antes de estados.
Los validadores de las seis bases, asociaciones y EIPD siguen siendo obligatorios.

Suite completa 1217 passed. HTTP cubre seis bases y tres medios, pendientes,
EIPD positivo, protección de confirmado y reemplazo hacia alcance ordinario.
Pruebas transversales cubren sensibilidad/geolocalización simultáneas y regímenes
concurrentes bloqueados. Pruebas con PostgreSQL/app_user/RLS y RAT simulado amplían
rollback/fallo de flush y concurrencia a consentimiento sensible con seis bases,
incluido cambio de prueba a pendiente durante espera del lock. HTTP usa RAT real.

Formato/lint/whitespace correctos. Sin commit ni migración nueva. M3-T1 EN PROGRESO;
próximo paso: revisar brechas de aceptación y priorizar régimen pendiente.


## 29. Evidencia HTTP de coexistencia sensible/geolocalización

Añadida prueba parametrizada test_api_sensitive_geolocation_joint_confirmation:
ambos expedientes preparados, pérdida por no/pendiente en cualquiera, cambios
sin reaporte y asociaciones obsoletas; reaporte no aprueba documento desfavorable.
Rechazo conserva íntegro confirmado y borrador, con coherencia GET/POST de
resultados especiales/EIPD. EIPD positivo conserva bloqueo; reparación conjunta
y screening negativo permiten reemplazo. PATCH de confirmado sigue rechazado.

Cuatro casos aprobados con PostgreSQL/app_user/RLS y RAT real. Verificación
focalizada 4 passed, 85 deselected; última suite completa anterior 1217 passed,
no repetida en esta etapa de cobertura. Black/Ruff/whitespace correctos.
Matriz/backlog actualizados. Sin cambios de implementación/migración ni commit.
M3-T1 EN PROGRESO; siguiente brecha: concurrencia con constructor RAT real.


## 30. Concurrencia con constructor RAT real y regímenes conjuntos

Añadida test_confirmation_concurrent_real_rat_joint: base consentimiento,
expedientes sensible/geolocalización preparados, constructor RAT sin mock,
filas M2 reales y dos conexiones PostgreSQL/app_user/RLS. Segunda sesión precarga
borrador; espera de bloqueo observada mediante pg_blocking_pids.

Commit de primera confirmación rechaza segunda; rollback permite segunda.
Cambio pendiente de cualquier documento rechaza tras espera y conserva vigente.
Cambio is_sensitive en M2 se relee y rechaza por contexto distinto; snapshots
históricos no se reescriben al rechazar. Se conserva un único confirmado.

Ocho casos nuevos aprobados; módulo completo 13 passed. Alcance de esta evidencia:
base consentimiento y ambos regímenes; concurrencia de otras cinco bases sigue
probada con constructor RAT simulado. Última suite completa anterior 1217 passed;
no repetida por extensión focalizada. Formato/lint/whitespace correctos, sin
implementación/migración nueva ni commit. M3-T1 EN PROGRESO. Próximo paso:
priorizar y delimitar régimen especial pendiente.


## 31. Priorización del siguiente régimen: salud y perfil biológico

Decisión de implementación incremental, 2026-10-06: siguiente régimen
salud_perfil_biologico_art16bis. Se reutiliza preparación sensible existente como
prerrequisito, sin asumir que ella prepare las condiciones propias de salud.
Este checkpoint delimita alcance; no crea schema, migración ni habilita gate.

Fuente para el diseño: Ley 21.719 publicada en Diario Oficial,
https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf,
artículo 16 bis. Contraste con BCN:
https://www.bcn.cl/leychile/navegar?idNorma=1209272.
El texto vincula la ruta con consentimiento a fines previstos en legislación
sanitaria especial, distingue supuestos sin consentimiento y contempla
restricciones por contexto de recolección. El contrato siguiente debe reflejar
esas dimensiones separadamente; no basta añadir un campo approved.

### 31.1 Primer alcance de producto

Preparación documental de la ruta con consentimiento expreso del titular,
responsable y alcance de salud/perfil biológico declarado explícitamente.
Mantener los límites actuales de representación y cobertura conservadora.
Requiere checklist general y expediente sensible preparados, referencia concreta
al fundamento sanitario especial y análisis de su aplicación a finalidad,
operaciones y alcance. No elegir una ley sanitaria por defecto ni inferirla
por nombre de actividad. Referencia documental no equivale a verificación externa.

Documentar origen/contexto de recolección, operaciones y eventual cesión/muestras
mediante metadata. Contexto sin resolver o restricciones sin fundamento suficiente
impiden preparación; ningún consentimiento elimina automáticamente restricciones.
No almacenar historias clínicas, resultados genéticos ni muestras en el expediente.

Primer bloque no habilita excepciones sin consentimiento, representación,
infancia/adolescencia, biometría ni investigación concurrentes. Son fronteras
de producto: no equivalen a prohibiciones jurídicas generales.

### 31.2 Diseño físico pendiente, antes de persistencia

Siguiente paso: fijar HealthAssessmentV1 independiente, campos cerrados/versionados,
respuestas fundadas y evidencia; definir respuestas de origen/contexto, selectores,
condicionales, residualidad y matriz de motivos. Distinguir falta de dato,
contradicción y ruta fuera del primer soporte. Referencias normativas deben
identificar norma/artículo y fuente oficial; fechas factuales no deciden vigencia.

Resolver vínculo inequívoco con consentimiento expreso y condiciones especiales,
y preservar contratos existentes. No incorporar campos de cliente que calculen
preparación ni reemplazar la base general. Asociaciones nuevas solo después de
fijar contrato; conservar comparadores previos con documento nuevo no cubierto.

### 31.3 Secuencia y aceptación del bloque

1. Diseño de contrato y matriz completitud/aplicabilidad; revisión del artículo
   completo y fundamento sanitario necesario antes de programar gate.
2. Schema, persistencia nullable y asociaciones compatibles; régimen bloqueado.
3. Evaluador puro/readiness con motivos deterministas e inmutabilidad.
4. Gate compartido y EIPD, habilitando solo la ruta diseñada y preparada.

Aceptar: borradores parciales, contratos inválidos, fundamento/referencias y
prueba ausentes, alcance no sensible/fuera de RAT/parcial/discordante, contexto
sin resolver o restringido, operación/cesión/muestras sin análisis; checklist o
consentimiento sensible no preparados. Fronteras concurrentes siguen bloqueadas.
Persistencia/RLS/fechas/null/históricos/obsolescencia y guardado conjunto.
HTTP: completo, rechazo sin reemplazo, EIPD positivo, protección del confirmado.
Concurrencia/rollback y relectura con RAT real según alcance elegido.

No se declara completo el diseño físico ni habilitada la ruta. Próximo paso:
definir contrato documental y matriz de completitud/aplicabilidad de salud.
M3-T1 EN PROGRESO, sin commit. Checkpoint exclusivamente documental.


## 32. HealthAssessmentV1 y matriz de preparación — diseño

2026-10-06. Desarrollo documental de §31; no se añade código ni habilita salud.
Fuente revisada completa: artículo 16 bis, páginas 12–13 de la publicación oficial
https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf.
El precepto distingue ruta con consentimiento/fines sanitarios, supuestos sin
consentimiento y restricciones según recolección. Las decisiones operativas
siguientes son fronteras del primer soporte, no afirmaciones de prohibición general.

### 32.1 Contrato independiente propuesto

HealthAssessmentV1 cerrado extra forbid; schema_version Literal[1] = 1.
Todos los campos documentales permiten null en borrador; listas con default_factory.
Sin campos approved/result/can_confirm ni normalización nueva del checklist previo.

| Campo | Tipo propuesto | Función |
| --- | --- | --- |
| purpose_description | str nullable | Finalidad RAT |
| health_data_description | str nullable | Metadata de datos de salud/perfil biológico |
| processing_operations | str nullable | Operaciones cubiertas |
| scope | SpecialScopeV1 nullable | Categorías/grupos declarados |
| route | Literal consentimiento_expreso nullable | Primera ruta soportada |
| sanitary_law_references | list HealthLegalReferenceV1 | Fundamento sanitario especial |
| sanitary_purpose_analysis | str nullable | Aplicación de norma/finalidad al alcance |
| sanitary_purpose_covered | ContractResponseV1 nullable | Respuesta fundada de cobertura |
| collection_contexts | list HealthCollectionContextV1 | Contextos declarados expresamente |
| collection_context_analysis | str nullable | Cómo se determinaron los contextos |
| restricted_context_legal_references | list HealthLegalReferenceV1 | Autorización específica documentada, si corresponde |
| restricted_context_analysis | str nullable | Análisis específico de contexto restringido |
| restricted_context_authorization_documented | ContractResponseV1 nullable | Declaración fundada; no aprueba automáticamente |
| includes_data_cession | ContractResponseV1 nullable | Hecho si/no/pendiente |
| cession_description | str nullable | Operaciones/destinatarios por metadata |
| includes_identifiable_biological_samples | ContractResponseV1 nullable | Hecho si/no/pendiente |
| biological_samples_analysis | str nullable | Relación con persona identificada/identificable y operaciones, sin muestras |
| evidence | list ContractEvidenceV1 | Referencias de prueba documental |
| notes | str nullable | Observaciones |

HealthLegalReferenceV1: extra forbid, norm_name/provision/official_source_url/
applicability_analysis str nullable en borrador; completeness requiere texto no
vacío en los cuatro. URL se valida estructuralmente como http/https, sin consulta
a red ni whitelist que confunda acceso con vigencia. Identificar norma/artículo;
no autocompletar una norma sanitaria ni interpretar una URL como autorización.

HealthCollectionContextV1 Literal laboral, educativo, deportivo, social, seguros,
seguridad, identificacion, otro. Lista vacía significa sin resolver; duplicados
exactos rechazados por schema. Otro requiere explicación, no constituye por sí
solo contexto aprobado. Se permiten varios contextos y no se infieren desde M2.

El primer route no admite excepciones. No modificar SpecialConditionV1 para
permitir sensitive_condition_id en salud: ese ID sigue exclusivo de sensibles.
Vínculo salud: regime salud_perfil_biologico_art16bis, authorization_route
consentimiento y uses_consent_assessment true. Debe coexistir condición
sensibles_art16/consentimiento_expreso_art16 y su expediente preparados.

### 32.2 Matriz de completitud y aplicabilidad

| Control | Aplicabilidad | Ausencia/pendiente | Negativo/contradicción |
| --- | --- | --- | --- |
| Finalidad, descripción, operaciones, scope y route | Siempre | incompleto | Finalidad/rol/ruta/alcance incoherente: revisión |
| Referencias sanitarias, análisis y sanitary_purpose_covered | Siempre | incompleto | Respuesta no fundada: revisión |
| Contextos y análisis de recolección | Siempre | Lista vacía/texto vacío: incompleto | Contexto restringido: revisión de primer soporte |
| Autorización/referencias/análisis de contexto restringido | Algún contexto distinto de otro | Campos vacíos/pendientes: incompleto | No o falta de sustento: revisión; sí completo conserva revisión por ruta no soportada |
| Campos anteriores en contexto solo otro | No aplicables | No requeridos | Contenido residual: revisión |
| includes_data_cession | Siempre, como hecho | Ausente/pendiente/fundamento vacío: incompleto | No resuelve no_aplicable; no es desfavorable por sí solo |
| cession_description | Cesión si | Vacío: incompleto | Texto con cesión no: residual/revisión |
| includes_identifiable_biological_samples | Siempre, como hecho | Ausente/pendiente/fundamento vacío: incompleto | No resuelve no_aplicable; no es desfavorable por sí solo |
| biological_samples_analysis | Muestras si | Vacío: incompleto | Texto con muestras no: residual/revisión |
| Evidence y reference/evidence_type por entrada | Siempre | Vacío/incompleto | No verifica contenido externamente |
| Checklist y consentimiento sensible preparados | Siempre en primera ruta | Propagar incompleto | Propagar revisión |

Condicional factual sin resolver deja applicability sin_resolver; no exigir el
texto condicional como si el hecho ya fuera sí. Respuestas ContractResponseV1
excluyen no_aplica; no aplicable se deriva en servidor. Fechas de evidencia son
factuales opcionales. Precedencia incompleto > requiere_revision > completo.
Motivos ordenados por contrato, índices numéricos, sin mutación de entradas.

### 32.3 Coherencia y alcance conservador inicial

Revalidar expediente, snapshot, condiciones, checklist y expediente sensible.
Propagar motivos de consentimiento sensible con prefijo estable; no consultar
registros ni afirmar autorización jurídica externa. Rol responsable; finalidad
por canonización v1. Declaración salud afirmativa con rationale y scope.

Seleccionar categorías sensibles del RAT; validar selectores propios, declaración
y condición aun sin scope propio, duplicados semánticos y pertenencia M2.
Para primer soporte: scope salud, declaración y condición coinciden entre sí y
con scope de consentimiento sensible preparado. Así cubren todas las categorías
sensibles y todos los grupos del alcance RAT. Si salud es un subconjunto menor,
requiere revisión hasta diseñar cobertura granular; no afirmar que todos los
datos sensibles son de salud por su flag ni inferir una matriz categoría/titular.
Sin categorías sensibles/flag coherente o sin régimen declarado: revisión residual.

Condición genérica conserva legal_reference, documentary_analysis y evidencia.
Regímenes concurrentes sin validador, representación, EIPD positivo/pendiente y
asociaciones obsoletas conservan bloqueo. El texto de restricciones no se elude
mediante consentimiento, base art13 ni referencia genérica al artículo 16 bis.

### 32.4 Persistencia, versiones y pasos siguientes

health_assessment JSONB nullable, none_as_null y check objeto; migración aditiva
tras d17f9b2e5c86 cuando se implemente. CREATE/PATCH/GET: omisión conserva, objeto
reemplaza, null borra borrador. Nueva asociación especial v8/EIPD v9 incorpora
health_assessment final; preservar constructores/comparadores previos. Documento
no nulo con especiales v1–v7/EIPD v1–v8 requiere asociación de salud no cubierta;
null mantiene comparación anterior. GET/confirm no reescriben asociaciones.

Aceptación: borradores, campos/enums/versiones inválidos, contextos múltiples/
duplicados/otro/restringido, referencias vacías/URL inválida, condicionales sin
resolver/residuales, evidencia, scope parcial/externo/no sensible/discordante,
checklist y sensible pendientes, rutas/condiciones incoherentes y concurrencias.
Guardar conjuntamente documentos finales antes de controles; cambios sin reaporte
obsoletan hashes. Tenant/RLS/SQL null/check objeto/fechas e históricos. Evaluador
puro, HTTP y rollback/concurrencia antes de habilitar gate.

Próximo paso concreto: schema HealthAssessmentV1 y pruebas de contrato, sin
persistencia ni habilitación hasta etapa posterior. Diseño documental completado;
M3-T1 EN PROGRESO, sin commit ni código/migración nuevos.


## 33. Implementación del contrato HealthAssessmentV1

Implementado §32 como schema independiente, sin persistencia/gate. Incluye
HealthLegalReferenceV1 y HealthCollectionContextV1. Referencia official_source_url
usa HttpUrl nullable: valida esquema http/https y serializa a texto en JSON,
sin consultar red ni decidir legitimidad jurídica. Contextos múltiples conservan
orden y rechazan duplicados exactos; completitud/condicionales se difieren al
evaluador, permitiendo borradores parciales. No altera contratos anteriores.

Verificación focalizada 107 passed: 49 pruebas nuevas y schemas de licitud,
geolocalización y consentimiento sensible. Cubren listas independientes, campos/
versiones/rutas desconocidos, respuestas, contextos, scopes inválidos, evidencia,
URLs y fechas factuales. Formato/lint/whitespace correctos. Última suite completa
anterior 1217 passed; sin repetición para contrato aislado.

Salud continúa bloqueada. Sin nuevas migraciones ni commit. M3-T1 EN PROGRESO.
Siguiente: columna/exposición HTTP y asociaciones especiales v8/EIPD v9, antes
de evaluador/readiness e integración del gate.


## 34. Persistencia de salud y asociaciones compatibles

Implementada etapa de persistencia/exposición de §32.4: health_assessment en
CREATE/PATCH/GET, JSONB none_as_null, check SQL NULL/objeto y migración aditiva
e28a0c3f6d97 tras d17f9b2e5c86, aplicada localmente. Omisión conserva, objeto
reemplaza y null borra borrador; serialización HttpUrl y fechas preservada.

Nuevos guardados especiales v8/EIPD v9 incorporan documento final. Constructores
y comparadores previos conservados: salud no nula con versiones especiales v1–v7
/EIPD v1–v8 informa asociacion_salud_no_cubierta; null conserva comparación.
Cambios sin reaporte obsoletan asociaciones, GET/confirm no las reescriben.
Expediente sin régimen detectado informa expediente_salud_residual y bloquea.
Régimen salud declarado mantiene validador_no_implementado; ninguna habilitación
ni evaluador/readiness específico de salud en esta etapa.

Suite completa 1287 passed, incluidos nueve casos HTTP nuevos. Salud declarada
junto a sensible sin expediente rechaza 400 por incompletitud, conservando
borrador: no cambiar esa precedencia para exigir 409. Formato/lint/whitespace
correctos. M3-T1 EN PROGRESO, sin commit. Próximo paso: evaluador puro de salud
más preparación en readiness, antes de gate.


## 35. Evaluador puro y preparación de salud en readiness

Implementado evaluate_health_assessment_v1 según §32, recibe expediente,
snapshot, condiciones, checklist y consentimiento sensible. Revalida instancias
y diccionarios; propaga motivos/applicabilidad de dependencias con prefijos,
conserva question_id. Precedencia incompleto > requiere_revision > completo,
orden determinista con índices numéricos y sin modificar entradas.

Referencias sanitarias requieren norma/artículo/URL/análisis; finalidad,
operaciones/contexto y prueba completos. Campos restringidos aplican ante contexto
distinto de otro; sin contexto su aplicabilidad queda sin_resolver. Contextos
restringidos completos siguen requiere_revision por límite de primer soporte.
Cesión/muestras son hechos: no no es desfavorable; sí requiere descripción;
pendiente deja sin_resolver, textos residuales ante no producen revisión.

Selectores de expediente, declaración y condición se validan independientemente,
con canonización y pertenencia/cobertura RAT y coincidencia con consentimiento
sensible. Falta de declaración o condición informa motivo específico, incluso
cuando ambas faltan. Rol/finalidad/representación y sensibilidad dependen también
del evaluador sensible. No se infiere clasificación sanitaria desde el RAT.

Readiness health nullable cuando existe expediente o régimen detectado; agrega
salud_no_preparada si no completo. Resultado completo orientativo no habilita
POST: salud mantiene validador_no_implementado, EIPD/asociaciones conservados.

Suite completa 1354 passed; 65 pruebas puras y dos HTTP nuevas (completo y
restringido; rechazo conserva borrador, pendiente/obsolescencia/borrado).
Ajuste final de motivo de condición ausente validado con 65 pruebas puras después
de suite general. Formato/lint/whitespace correctos. Sin migración ni commit.
M3-T1 EN PROGRESO. Próximo: integración de la ruta de salud preparada, manteniendo
contextos restringidos y rutas/regímenes no soportados bloqueados.


## 36. Gate transversal de salud por consentimiento preparado

Integrada ruta salud_perfil_biologico_art16bis por consentimiento con evaluador
completo. Detector conserva salud, sensible y otros regímenes; motivos de salud
se propagan sin borrar dependencias. Otras rutas mantienen validador_no_implementado.
Contextos restringidos conservan revisión aun documentados; consentimiento sensible
preparado sigue obligatorio y no evita las condiciones sanitarias propias.

EIPD contrasta propuesta de salud: preparación no completa mantiene
ruta_especial_pendiente, sin deducir excepción desde art13. Gate compartido agrega
salud_no_preparada con 400 incompleto/409 revisión; otras barreras pueden elevar
rechazo. GET/POST usan el mismo evaluador; relectura tras lock antes de estados.
Asociaciones vigentes y screening negativo siguen necesarios.

Suite completa 1407 passed. HTTP seis bases y contextos otro/laboral, obsolescencia,
EIPD positivo, rechazo conserva vigente, reparación/reemplazo y protección de
confirmado. Transversal puro: salud/sensible/geolocalización simultáneos y otros
regímenes pendientes. Pruebas reales PostgreSQL/app_user/RLS con RAT simulado:
rollback/fallo de flush y concurrencia de salud para seis bases, incluido cambio
pendiente durante espera. Mantener distinción RAT simulado frente a HTTP RAT real.

Formato/lint/whitespace correctos. Sin migraciones nuevas ni commit. M3-T1 EN
PROGRESO. Próxima brecha: evidencia HTTP de tres regímenes preparados juntos y
concurrencia específica de salud con constructor RAT real.


## 37. Evidencia conjunta de salud, sensible y geolocalización

Seis casos HTTP nuevos con los tres regímenes preparados por consentimiento:
respuestas no/pendiente en cada expediente, asociaciones obsoletas, rechazo,
conservación del vigente, reparación, bloqueo EIPD positivo, reemplazo y protección
del confirmado. GET y POST conservan los motivos de preparación y EIPD.

Doce casos concurrentes nuevos con constructor RAT real y PostgreSQL/app_user/RLS:
confirmación con commit/rollback, cambio de cada expediente y cambio del RAT
mientras otra confirmación espera el bloqueo. La segunda sesión precarga el
borrador para comprobar la relectura; se conserva un único confirmado y su historia.
Alcance: base consentimiento_art12, salud en contexto otro. Las otras cinco bases
mantienen la evidencia previa de concurrencia con constructor RAT simulado.

Validación focalizada: módulo de concurrencia 25 passed y HTTP conjunto 10 passed,
18 casos nuevos. Última suite completa anterior: 1407 passed; no se reejecutó en
este paso de pruebas/documentación. Black/Ruff/whitespace correctos. Sin cambios
de implementación, migración nueva ni commit. M3-T1 EN PROGRESO.
Próximo: revisar alcance de representación sensible y criterios de cierre.


## 38. Representación sensible y criterios de cierre revisados

Revisión de alcance de producto, sin ampliar las autorizaciones implementadas.
Se mantiene §24.3: given_by titular puede preparar la ruta sensible;
representante_legal y mandatario conservan el expediente y requieren revisión
con representacion_no_preparada. Salud depende de esa preparación sensible.
No se deduce una prohibición jurídica ni se habilita infancia/adolescencia.
El soporte de representación queda pendiente de diseño de acreditación, vínculo,
alcance, vigencia, completitud y asociaciones; no basta con cambiar given_by.
Cobertura parcial categoría/grupo sigue pendiente de una matriz explícita en RAT.

Evidencia existente: test_sensitive_representation_review cubre ambos valores;
test_sensitive_transversal_blockers cubre representante_legal;
test_health_coherence_dependency comprueba dependencia para representante_legal.
No se encontró prueba HTTP específica de representación en la ruta sensible.
Próximo paso concreto: ambos valores por HTTP, con y sin salud; GET/POST coherentes,
asociaciones reaportadas, rechazo que preserve borrador y confirmado anterior,
y reparación a titular que permita el reemplazo. Es verificar el límite actual,
no implementar ni autorizar la representación.

Criterios de cierre, derivados de §13.2 y de los límites actuales:

| Criterio | Situación y condición pendiente |
| --- | --- |
| Persistencia, constraints, índices, migraciones y RLS | Implementados; revisar diff final y cadena Alembic antes del cierre |
| Snapshot M2, canonización/hash y compatibilidad | Implementados; mantener asociaciones especiales v8/EIPD v9 y lectura histórica |
| Seis bases ordinarias, sensible titular, geolocalización y salud del primer alcance | Implementados; no extrapolar a rutas bloqueadas |
| Confirmación/reemplazo, bloqueo y conservación histórica | Evidencia existente; añadir HTTP específico de representación |
| Regímenes/rutas pendientes y alcance parcial | Mantener revisión explícita; no declarar todos los regímenes implementados |
| Evidencia final de integración | Reejecutar suite completa después del siguiente cambio; 1407 es la última ejecución completa anterior |
| Delimitación de entrega y revisión final | Revisar cambios y pendientes explícitos antes de declarar DONE; no cerrar por conteo de pruebas |

La revisión de criterios no equivale a satisfacerlos. Regímenes especiales
restantes siguen pendientes funcionales; su eventual diferimiento para cierre
requiere una decisión explícita de alcance, no una reclasificación silenciosa.
Workflow completo EIPD sigue diferido; frontend no se agrega como requisito por
esta revisión. Metadata documental no verifica externamente evidencia.
Este paso solo actualiza documentación; no reejecuta pruebas ni crea migración
ni commit. M3-T1 EN PROGRESO.


## 39. Representación sensible verificada por HTTP

Cuatro casos de test_api_sensitive_representation_preserves_confirmed:
representante_legal/mandatario, cada uno con y sin salud, junto a geolocalización.
RAT real y PostgreSQL/app_user/RLS. Mandatario aporta facultad expresa en checklist
para aislar el límite de representación sensible, que sigue requiriendo revisión.
GET informa representacion_no_preparada; POST rechaza con los mismos motivos
especiales/EIPD. Rechazo conserva íntegros borrador y confirmado anterior.

Cambiar given_by vuelve obsoleta la asociación especial; el hash EIPD no incluye
el checklist general y permanece vigente. Reaportar controles no habilita la
representación. Reparar a titular permite reemplazo con screening negativo;
EIPD positivo mantiene bloqueo. El nuevo confirmado rechaza PATCH posterior.
No se amplía soporte de representación ni se modifica implementación.

Validación: cuatro casos focalizados y suite completa 1429 passed en 140.16s.
Black/Ruff/whitespace correctos. Sin migración nueva ni commit.
M3-T1 EN PROGRESO. Próximo: revisar diff final y cadena de migraciones, y dejar
explícita la decisión de alcance de regímenes pendientes antes de declarar DONE.


## 40. Revisión de cambios y cadena de migraciones

Rama feature/m3-t1-licitud-persistencia, HEAD 2fd8881; cambios sin commit.
Revisión de router/API, modelos, confirmación y transacción runtime:
permisos view/edit y suscripción en servidor; sesión runtime app_database_url;
confirmación bloquea serie, relee borrador con populate_existing, valida contexto
M2 y preparación antes de reemplazo, libera índice parcial con flush y deja
commit/rollback al caller. get_db hace rollback ante excepción.
Esta revisión focalizada no constituye auditoría exhaustiva de seguridad.

Alembic heads/current: único head e28a0c3f6d97, aplicado localmente.
Cadena lineal 5997a757f17b -> 7c9e1a3b5d20 -> 8d2f4a6c9e31 ->
9e3b5d7f1a42 -> ae4c6e8b2f53 -> bf5d7f9c3a64 -> c06e8a1d4b75 ->
d17f9b2e5c86 -> e28a0c3f6d97. Migraciones nuevas agregan columnas JSONB
nullable/check objeto y downgrade elimina check/columna. No se ejecutó downgrade
ni upgrade de ensayo; no se alteraron migraciones aplicadas.

Black --check y Ruff: 46 archivos Python nuevos/modificados aprobados.
git diff --check correcto. Última suite integral: 1429 passed (§39), no repetida.
Inventario incluye archivos sin seguimiento: git diff --stat por sí solo no
representa la totalidad de la entrega.

Hallazgo abierto: alembic check global falla por diferencias fuera de las tablas
M3 (índices presentes en DB y ausentes en metadata, y nombre de unique constraint
DiagnosticAnswer). Comparación autogenerate limitada a legal_assessment_series y
legal_assessments devuelve cero diferencias. Esto no verifica políticas RLS ni
compara exhaustivamente check constraints; su evidencia proviene de migraciones
y pruebas existentes. No generar una migración que elimine índices a partir de
este resultado. Procedencia y corrección del drift global quedan por investigar;
no se atribuye automáticamente a este trabajo ni se declara preexistencia probada
para todas las diferencias.

Próximo paso: inventariar y contrastar drift global contra migraciones/metadata
para decidir una corrección concreta sin perder índices. Luego queda la decisión
explícita de alcance de regímenes pendientes. M3-T1 EN PROGRESO; sin commit.


## 41. Drift global de metadata corregido

Inventario: 31 operaciones propuestas por autogenerate; 29 eliminaciones de
índices y remove/add de una unique por diferencia de nombre. Procedencia
contrastada con migraciones 0001_initial_schema (tenant y HNSW),
0002_modulo1_cuestionario_config (activa/unique), 0005_diagnostico_api
(reference_documents) y 0010_modulo2_rat_persistencia (tenant/relaciones).

Modelos declaran ahora los 29 índices históricos en __table_args__: organization_id,
relaciones M2, ux_config_versiones_activa unique con predicado activa, y
knowledge_chunks_embedding_idx con HNSW/vector_cosine_ops. DiagnosticAnswer usa
nombre explícito uq_diagnostic_answers_diagnostic_id_pregunta_id. No cambia
la restricción de unicidad, las columnas ni las reglas funcionales.

Alembic check global aprobado: No new upgrade operations detected.
No se genera migración, no se ejecuta DDL ni se eliminan índices. Se corrige
metadata para reflejar la base creada por migraciones. Esta comparación no
constituye auditoría exhaustiva de checks/RLS ni ensayo de downgrade.

Black/Ruff y git diff --check correctos. Suite integral posterior:
1429 passed en 140.69s. Sin commit. M3-T1 EN PROGRESO.
Próximo: consolidar la propuesta concreta de alcance de entrega y los regímenes
pendientes, para resolver explícitamente los criterios de cierre sin declarar
soportadas las rutas que mantienen revisión.


## 42. Propuesta concreta de alcance de entrega

m3-t1-propuesta-entrega.md consolida alcance backend ya soportado, límites y
pendientes funcionales, evidencia y condiciones de cierre. Recomienda entrega
inicial de seis bases ordinarias, sensible titular, geolocalización y primer
soporte de salud; no marca diferidos los regímenes pendientes automáticamente.
Decisión pendiente: aceptar esa delimitación o continuar alcance integral.
M3-T1 EN PROGRESO; propuesta no equivale a DONE ni autorización de publicación.
Solo documentación; última suite 1429 passed y Alembic check aprobado (§41).
Sin pruebas reejecutadas, cambios de código, migraciones ni commit.


## 43. Decisión de alcance integral y siguiente régimen

Decisión explícita del usuario, 2026-10-06: continuar con el alcance integral.
La propuesta de entrega inicial de §42 no se acepta como recorte para cierre.
Representación, excepciones sensibles/salud, contextos restringidos, biometría,
infancia/adolescencia, investigación y cobertura granular continúan pendientes
funcionales; no se convierten en diferidos por esa propuesta. Workflow completo
EIPD conserva su diferimiento anterior. M3-T1 EN PROGRESO.

Siguiente régimen priorizado: biometricos_art16ter, ya declarado mediante
biometricos_identificacion_unica. Implementación incremental dentro del alcance
integral: empezar por ruta consentimiento expreso, sin dar por resueltas las
excepciones ni los regímenes concurrentes.

Fuente consultada: Ley 21.719, artículo 16 ter, texto oficial BCN:
https://www.bcn.cl/leychile/navegar?idNorma=1209272
El artículo vincula la ruta al inciso primero del art16 y exige informar sistema,
finalidad, período de uso y ejercicio de derechos. Sin consentimiento remite al
inciso segundo del art16bis; no reutilizar automáticamente el expediente sanitario
ni inferir excepción por elegir una base art13.

Decisiones de producto para diseñar el contrato siguiente: expediente biométrico
independiente, metadata del sistema y operaciones, alcance coincidente con RAT,
finalidad y período de uso documentados, canal/procedimiento para derechos,
constancia de información al titular y evidencia referenciada. Reutilizar
checklist/consentimiento sensible preparados en la primera ruta. No almacenar
plantillas biométricas, imágenes, huellas o grabaciones en este expediente.
Declaración específica explícita; el indicador sensible de M2 no identifica por
sí solo biometría. Infancia, salud y otros regímenes conservan sus propias barreras.

Próximo paso: contrato BiometricAssessmentV1 y matriz de completitud/aplicabilidad,
con campos cerrados/versionados, parciales en borrador, respuestas fundadas,
residualidad y asociaciones. Después schema/pruebas, persistencia/asociaciones,
evaluador/readiness, gate y evidencia HTTP/concurrencia. No habilitar gate antes
de esa secuencia. Excepciones biométricas seguirán pendientes dentro del alcance
integral hasta diseñar sus rutas propias; este primer bloque no las difiere.

Solo decisión/diseño preliminar; sin cambios de código, migraciones ni commit.
Última suite 1429 passed, Alembic check aprobado (§41), no reejecutados aquí.


## 44. Contrato y matriz de preparación biométrica

Diseño documental, 2026-10-06; no implementa schema ni habilita confirmación.
Fuente: artículo 16 ter completo en texto oficial BCN,
https://www.bcn.cl/leychile/navegar?idNorma=1209272 . Información específica:
sistema, finalidad, período de utilización y ejercicio de derechos; primera
ruta vinculada a consentimiento expreso. Los mecanismos documentales siguientes
son decisiones de producto para acreditar preparación, no requisitos textuales
adicionales atribuidos a la ley. Excepciones siguen pendientes dentro del alcance
integral y requieren diseño propio; no se importan desde salud automáticamente.

### 44.1 Contratos cerrados y borradores parciales

BiometricAssessmentV1: extra forbid; schema_version Literal[1] = 1.
Textos/respuestas/scope/route nullable; listas default_factory; no campos
approved, result, can_confirm ni no_aplica aportados por cliente.

| Campo | Tipo | Función |
| --- | --- | --- |
| purpose_description | str nullable | Finalidad evaluada en RAT |
| biometric_data_description | str nullable | Descripción de categorías, sin valores biométricos |
| processing_operations | str nullable | Operaciones cubiertas |
| scope | SpecialScopeV1 nullable | Categorías/grupos del alcance |
| route | Literal consentimiento_expreso nullable | Primera ruta implementable |
| unique_identification_analysis | str nullable | Tratamiento técnico y relación con identificación única |
| unique_identification_confirmed | ContractResponseV1 nullable | Declaración fundada de pertenencia al régimen |
| systems | list BiometricSystemV1 | Información específica por sistema utilizado |
| systems_coverage_analysis | str nullable | Cómo se cubren los sistemas de las operaciones declaradas |
| all_systems_documented | ContractResponseV1 nullable | Declaración de cobertura, no inferida por servidor |
| evidence | list ContractEvidenceV1 | Referencias generales documentales |
| notes | str nullable | Observaciones |

BiometricSystemV1: extra forbid; todos los textos/respuestas nullable y listas
vacías permitidas en borrador. Un registro agrupa la información de un sistema;
no duplicar globalmente los cuatro requisitos perdiendo su vínculo por sistema.

| Campo | Tipo | Función |
| --- | --- | --- |
| system_reference | str nullable | Identificador documental estable, no UUID M2 obligatorio |
| system_name | str nullable | Identificación comprensible del sistema |
| system_description | str nullable | Sistema y modalidad de uso, sin imágenes/plantillas |
| specific_purpose | str nullable | Finalidad específica de este sistema |
| purpose_alignment_analysis | str nullable | Relación de finalidad específica con finalidad RAT |
| use_period_description | str nullable | Período de utilización, incluyendo evento/criterio si corresponde |
| retention_alignment_analysis | str nullable | Coherencia documentada con conservación RAT |
| rights_exercise_description | str nullable | Procedimiento para ejercer derechos |
| rights_contact_channel | str nullable | Canal documentado; sin comprobar disponibilidad externa |
| information_reference | str nullable | Referencia al aviso/información proporcionada |
| system_identification_disclosed | ContractResponseV1 nullable | Identificación informada |
| purpose_disclosed | ContractResponseV1 nullable | Finalidad específica informada |
| use_period_disclosed | ContractResponseV1 nullable | Período informado |
| rights_exercise_disclosed | ContractResponseV1 nullable | Forma de ejercicio informada |
| evidence | list ContractEvidenceV1 | Referencias de información por sistema |

No fechas normativas inferidas, límites de duración por defecto, consulta de
registros ni datos biométricos crudos. evidence_date opcional factual se reutiliza
del tipo existente. No resolver coherencia de períodos comparando prosa como si
fuera una regla temporal ejecutable. Finalidad general compara canonización v1;
finalidad específica puede ser más concreta y se vincula mediante análisis,
no se exige igualdad literal con RAT. system_reference no vacío en preparación;
duplicados no vacíos por canonización v1 producen revisión, no deduplicación
silenciosa. M2/snapshot v1 no aporta inventario operativo de sistemas: cobertura
es documental; no afirmar exhaustividad verificada mediante all_systems_documented.

### 44.2 Matriz de completitud y aplicabilidad

| Control | Aplicabilidad | Ausente/pendiente/sin fundamento | Negativo/contradicción |
| --- | --- | --- | --- |
| Textos generales, scope y route | Siempre | incompleto | Finalidad/rol/ruta/alcance incoherente: revisión |
| Análisis y respuesta de identificación única | Siempre | incompleto | No fundada: revisión de declaración/clasificación |
| systems y cobertura | Siempre | Lista vacía, análisis/respuesta ausente: incompleto | all_systems_documented no: revisión |
| Textos de cada sistema | Cada registro aportado | Campo vacío: incompleto con índice numérico | Referencia duplicada: revisión |
| Cuatro respuestas informativas por sistema | Cada sistema | Ausente/pendiente/fundamento vacío: incompleto | No fundada: revisión |
| Evidencia general y por sistema | Siempre/cada sistema | Lista vacía o tipo/referencia vacío: incompleto | Metadata no verifica contenido externamente |
| Checklist general y sensible expreso | Primera ruta | Propagar incompleto | Propagar revisión, incluida representación |
| Rutas o regímenes concurrentes sin soporte | Si detectados | Mantener motivos propios | No quedan preparados por este expediente |

Los cuatro requisitos por sistema siempre aplican. No introducir no_aplicable
por falta de información ni suprimir un requisito por modalidad biométrica.
El primer contrato no contiene condicionales factuales adicionales: cesión,
muestras, restricciones de salud y EIPD conservan expedientes/controles propios.
Motivos estables con field por systems.<índice>.<campo>, question_id conservado
para dependencias; ordenar índices numéricamente. Precedencia incompleto >
requiere_revision > completo. No mutar contratos, snapshots ni documentos.

### 44.3 Coherencia, asociación y persistencia previstas

Evaluador puro evaluate_biometric_assessment_v1(document, snapshot, special,
consent, sensitive_consent), revalidando contratos cerrados. Rol responsable;
declaración biometricos_identificacion_unica si y condición biometricos_art16ter
por consentimiento con uses_consent_assessment true. sensitive_condition_id
permanece exclusivo del régimen sensibles_art16; no extenderlo a biometría.
Condición sensible consentimiento_expreso_art16 y expediente sensible preparados
siguen dependencias propias. No inferir biometría desde flags/nombres de categorías.

Scopes biométrico/declaración/condición no vacíos, semánticamente únicos,
coincidentes y válidos en RAT; categorías seleccionadas sensibles. Primera
cobertura conservadora: todas las categorías sensibles y todos los grupos del
alcance evaluado, coherente con consentimiento sensible. Cobertura parcial por
pares sigue pendiente dentro del alcance integral, sin inferencia desde prosa.
Documento biométrico sin detección produce revisión residual; declaración y
expediente sin clasificación sensible coherente no corrigen M2 automáticamente.

Persistencia prevista: biometric_assessment JSONB nullable/none_as_null, check
objeto, exposición CREATE/PATCH/GET; omisión preserva y null borra solo borrador.
Objeto reemplazado entero. Migración nueva append-only, head actual e28a0c3f6d97.
Asociaciones futuras especiales v9 y EIPD v10 incorporarán documento biométrico
final; mantener versiones históricas y hash RAT. Documento no nulo con asociación
anterior: asociacion_biometria_no_cubierta. GET nunca reasocia automáticamente.

Readiness biometric nullable; gate futuro biometria_no_preparada 400 incompleto/
409 revisión, respetando barreras concurrentes. EIPD debe evaluar preparación de
ruta por consentimiento y conservar positivos/pendientes; nunca deducir excepción
por base art13. Hasta integración completa, detector mantiene
validador_no_implementado en biometría, incluso si existe expediente preparado.

### 44.4 Secuencia y aceptación

1. Schema auxiliar/principal y pruebas de contratos, parciales, extra forbid,
   schema_version, respuestas y alcance; sin persistencia ni gate.
2. Migración/persistencia/API/asociaciones históricas, SQL NULL y objeto; RLS,
   exposición cerrada, rechazo de edición de confirmado, obsolescencia/reaporte.
3. Evaluador puro/readiness: cada campo faltante, respuesta no/pendiente,
   duplicados, scopes, representación, dependencias y ausencia de mutación.
4. Gate/EIPD compartido y HTTP: preparado, reparación, positivos EIPD, asociación
   obsoleta, rechazo que conserva vigente, reemplazo y protección histórica.
5. Concurrencia/rollback con PostgreSQL y constructor RAT real en alcance
   explícito; revalidar tras espera. Luego continuar rutas/regímenes pendientes
   del alcance integral; este bloque no habilita excepciones biométricas.

Solo documentación. Última suite 1429 passed y Alembic check aprobado (§41),
no reejecutados. Sin migración nueva ni commit. M3-T1 EN PROGRESO.
Próximo: implementar schemas BiometricSystemV1/BiometricAssessmentV1 y pruebas.


## 45. Schemas biométricos y pruebas implementados

Añadidos BiometricSystemV1/BiometricAssessmentV1 cerrados extra forbid según §44,
route inicial consentimiento_expreso y schema_version 1. Textos/respuestas/scope
nullable y listas independientes admiten borradores parciales. Se reutilizan
SpecialScopeV1, ContractResponseV1 y ContractEvidenceV1, sin alterar sus contratos.
Sistemas conservan orden y referencias tal como aportadas: duplicados semánticos
quedan para revisión del futuro evaluador, no se eliminan en schema.

53 casos biométricos nuevos: respuestas si/no/pendiente en campos generales y
por sistema, parciales, listas independientes, serialización/roundtrip/fechas,
rechazo de campos extra, aprobación calculada, versiones/rutas no soportadas,
no_aplica, alcance inválido y evidencia inválida. Rechazo de claves template,
embedding/fingerprint; no equivale a inspeccionar datos crudos incluidos en prosa.

Validación seleccionada con contratos licitud/sensible/salud: 150 passed.
Black/Ruff/whitespace correctos. Última suite integral anterior: 1429 passed (§41),
no reejecutada para este cambio aislado de contratos. Sin migración nueva ni commit.
No se incorpora aún biometric_assessment a CREATE/PATCH/GET ni a asociaciones:
biometría sigue bloqueada por validador_no_implementado.

M3-T1 EN PROGRESO, alcance integral. Próximo paso: persistencia/exposición del
expediente biométrico y asociaciones especiales v9/EIPD v10 compatibles;
mantener bloqueo hasta evaluador/gate y conservar pendientes del alcance integral.


## 46. Persistencia biométrica y asociaciones compatibles

biometric_assessment JSONB nullable con none_as_null/check objeto, modelos y
CREATE/PATCH/GET cerrados. Migración append-only f39b1d4e7a08 desde e28a0c3f6d97,
aplicada localmente; Alembic check global aprobado. Omisión conserva expediente,
null borra SQL NULL en borrador, PATCH reemplaza objeto completo.

Escrituras nuevas: especiales v9/EIPD v10 incluyen documento biométrico final.
Constructores/comparadores históricos especiales v1–v8/EIPD v1–v9 conservados.
Documento no nulo con asociación anterior: asociacion_biometria_no_cubierta;
documento ausente permite comparación histórica. GET no reasocia ni reescribe.
Cambio sin reaporte vuelve ambas asociaciones obsoletas; guardar controles usa
el estado final de documentos. Hash RAT sin cambios.

Diez casos HTTP nuevos: nueve pares históricos (1/1, 1/2, 2/3, 3/4, 4/5, 5/6,
6/7, 7/8, 8/9) y régimen biométrico declarado. Serialización/fechas, scopes y
contratos inválidos 422, organización ajena 403, omisión/preservación, sustitución,
obsolescencia/reaporte, residual 409, check DB rechaza array y SQL NULL. GET/POST
coherentes, rechazo conserva borrador. El caso declarado conserva
validador_no_implementado; dependencia sensible ausente mantiene precedencia
incompleta/400. Eliminado residual y reaportados controles, confirma ruta ordinaria;
confirmado rechaza PATCH biométrico tanto objeto como null sin alterar histórico.

Suite integral: 1492 passed en 150.93s. Ampliación final de aserciones de protección
verificada después con diez casos focalizados aprobados (sin cambios posteriores
de implementación). Black/Ruff/whitespace correctos. Sin commit.
M3-T1 EN PROGRESO, alcance integral. Biometría todavía sin evaluador ni gate
habilitado; persistir no autoriza el régimen. Próximo: evaluador puro y readiness
biométrico, manteniendo bloqueo hasta integrar confirmación/EIPD.


## 47. Evaluador puro y preparación biométrica

Implementado evaluate_biometric_assessment_v1 con resultado incompleto /
requiere_revision / completo, motivos inmutables y aplicabilidad. Revalida
contratos, preserva dependencias sensibles/checklist y question_id, verifica
textos/respuestas/evidencia generales y por sistema, declaración y condición,
rol/finalidad, alcances coincidentes y cobertura conservadora. Referencias de
sistema duplicadas por canonización generan revisión; orden numérico de índices.
Finalidad específica se documenta mediante análisis, sin exigir igualdad literal
con RAT ni comparar períodos en prosa como una autorización automática.

Readiness agrega biometric nullable cuando hay expediente o régimen detectado.
Gate compartido agrega biometria_no_preparada si no completo, 400 incompleto/
409 revisión, respetando otras barreras. Preparación completa no habilita POST:
detector biométrico conserva validador_no_implementado y EIPD se mantiene sin
integración biométrica de preparación. No cambia hash ni asociaciones existentes.

73 pruebas puras nuevas: campos generales/por sistema, respuestas no/pendiente,
fundamento ausente, dependencias, rutas/declaración/alcance/representación,
evidencia, sistemas múltiples, duplicados semánticos, orden numérico,
modelos mutados y ausencia de mutación. Un caso HTTP nuevo: completo aún rechaza,
respuesta pendiente/obsolescencia/reaporte, motivos GET/POST, conservación del
borrador, reparación y borrado que vuelve preparación incompleta. Diez casos
HTTP de persistencia anteriores también aprobados en validación integral.

Suite completa posterior: 1566 passed en 154.38s. Black/Ruff/whitespace y Alembic
check correctos. Sin migración nueva ni commit. M3-T1 EN PROGRESO, alcance integral.
Próximo: integrar preparación biométrica en detector/gate y EIPD, conservando
regímenes concurrentes bloqueados, asociaciones y restricciones de primera ruta.
Luego HTTP/concurrencia con RAT real y las excepciones pendientes del alcance.


## 48. Gate biométrico y contraste EIPD integrados

Detector admite biometricos_art16ter por consentimiento cuando el evaluador
biométrico resulta completo. Motivos generales/por sistema y dependencias se
propagan conservando question_id; regímenes detectados no se eliminan. Otras
rutas mantienen validador_no_implementado. Scopes, titular, responsable y
consentimiento sensible preparado conservan límites del primer soporte.

EIPD contrasta preparación de la propuesta biométrica por consentimiento:
no completa agrega ruta_especial_pendiente. Excepciones conservan
excepcion_especial_no_validada; una base art13 no aprueba esa ruta. Positivos/
pendientes EIPD y asociaciones obsoletas siguen bloqueando. Gate compartido
biometria_no_preparada permanece, y confirmación relee después de lock.

Diecinueve pruebas transversales nuevas: preparación conjunta sensible/biométrica
sin mutación, cinco positivos EIPD, expediente ausente/pendiente/obsoleto,
excepción, sensible/checklist ausente y representación; otros seis indicadores
especiales no quedan preparados por el expediente biométrico. Módulos biometría/
salud: 176 passed. Once casos HTTP biométricos aprobados. Caso completo actualizado
ahora confirma, nuevo borrador pendiente/obsoleto rechaza conservando vigente,
borrado impide preparación, EIPD positivo impide reemplazo, reparación/reaporte
con screening negativo permite reemplazo y confirmado rechaza PATCH posterior.

Suite integral posterior: 1585 passed en 155.13s. Black/Ruff/whitespace y Alembic
check aprobados; head f39b1d4e7a08. Sin migración nueva ni commit.
M3-T1 EN PROGRESO, alcance integral. Evidencia HTTP biométrica nueva usa base
consentimiento_art12. Próximo: ampliar HTTP a las seis bases ordinarias y
concurrencia biométrica con constructor RAT real; no extrapolar esta cobertura.
Excepciones biométricas y otros pendientes integrales conservan trabajo propio.


## 49. Biometría en seis bases y concurrencia con RAT real

Seis casos HTTP nuevos, test_api_biometric_confirmation_six_bases: preparación
biométrica/sensible por consentimiento y base general correspondiente; las seis
bases ordinarias conservan su expediente propio. LIA documenta régimen especial
y fuente titular en M2. Comprueba expediente biométrico pendiente/borrado,
asociaciones obsoletas y reaporte, EIPD positivo, confirmación/reemplazo,
protección posterior y rechazo con conservación íntegra de borrador y confirmado.
Una base art13 no sustituye consentimiento de esta ruta biométrica.

Dieciséis casos nuevos, test_biometric_confirmation_concurrent_real_rat_joint:
biometría/sensible/salud/geolocalización preparados, consentimiento_art12 y
constructor RAT real, PostgreSQL/app_user/RLS. Dos conexiones; segunda sesión
precarga borrador y se observa espera mediante pg_blocking_pids. Commit de primera
confirmación rechaza segunda; rollback permite segunda. Cambio pendiente de cada
uno de los cuatro expedientes o cambio de sensibilidad RAT durante espera se
relee y rechaza. Se conserva un único confirmado y documentos históricos,
snapshot/hash/fecha, sin reasociarlos ni reemplazarlos al rechazar.

Validación focalizada: módulo de concurrencia 41 passed y HTTP biométrico
17 passed, 58 verificaciones en total, incluidas 22 nuevas. Black/Ruff/whitespace
correctos. Este paso solo agrega pruebas/documentación; suite integral anterior
1585 passed (§48), no reejecutada; no presentar 1607 como suite ejecutada.
Sin cambios de implementación, migración nueva ni commit.

Límite de evidencia: HTTP con seis bases; concurrencia biométrica con RAT real
solo consentimiento_art12 y coexistencia preparada de cuatro regímenes. No se
extrapola concurrencia biométrica de otras cinco bases ni se habilitan excepciones.
M3-T1 EN PROGRESO, alcance integral. Próximo: priorizar y diseñar la primera ruta
biométrica sin consentimiento, contrastando la remisión de art16ter a art16bis;
no reutilizar autorización sanitaria ni inferir excepción desde base general.
Otros pendientes integrales mantienen trabajo propio.


## 50. Primera excepción biométrica: formulación, ejercicio o defensa de derechos

Delimitación dentro del alcance integral, 2026-10-06. Se prioriza el supuesto de
art16bis inciso segundo letra d, al que remite art16ter para tratamiento biométrico
sin consentimiento. Fuente oficial revisada: Ley 21.719, artículos 16, 16bis y 16ter,
https://www.bcn.cl/leychile/navegar?idNorma=1209272 . El supuesto exige necesidad
para formulación, ejercicio o defensa de un derecho ante tribunal u órgano
administrativo. No basta elegir defensa_derechos_art13e ni reutilizar una
referencia sanitaria o una autorización sensible diferente.

### 50.1 Dependencias y límites concretos

Separar tres niveles: base ordinaria, excepción sensible art16d y excepción
biométrica art16ter por remisión art16bis(d). La excepción sensible de defensa aún
carece de validador; será dependencia a implementar, no una aprobación implícita.
No exigir consentimiento sensible/checklist como prerrequisito de esta ruta sin
consentimiento. Las seis bases mantienen validación propia; primer caso HTTP
priorizado utilizará defensa_derechos_art13e por coherencia, sin hacerla condición
jurídica universal ni habilitar otras combinaciones sin evaluar su expediente.

RightsDefenseAssessmentV1 es de base ordinaria y acepta forum_type organo_publico.
La excepción concreta se delimitará a tribunal_justicia/organo_administrativo;
no equiparar cualquier órgano público a administrativo ni inferirlo desde nombre.
Puede reaprovecharse estructura conceptual de necesidad/derecho, pero no tratar
su resultado completo como validación automática de las excepciones especiales.

Sin consentimiento explícitamente elegido en condición biométrica y sensible:
authorization_route excepcion_legal, uses_consent_assessment false.
sensitive_condition_id defensa_derechos_art16d solo en condición sensibles_art16;
no reutilizar ese campo en biometría. Identificación de la excepción biométrica
se documentará en su contrato propio/versionado, con remisión concreta a art16bis(d).

Expedientes previstos separados: SensitiveRightsExceptionAssessmentV1 y
BiometricRightsExceptionAssessmentV1, sin cambiar semántica de
SensitiveConsentAssessmentV1 ni BiometricAssessmentV1 de consentimiento.
Contrato/campos/JSONB/asociaciones todavía por fijar en siguiente paso; documento
consentimiento residual o rutas mezcladas requerirán revisión, sin borrado automático.

El expediente debe cubrir derecho/fundamento/titular por metadata, vínculo con
datos/operaciones, necesidad, minimización, foro y etapa/referencia, finalidad y
alcance explícito, identificación biométrica/sistemas, evidencia y principios.
Cobertura conservadora inicial coincidente con RAT y las declaraciones; soporte
granular permanece pendiente. Sin plantillas, grabaciones, huellas ni documentos
procesales íntegros en metadata. Representación, menores, investigación, salud y
otros regímenes concurrentes conservan validadores/límites propios.

El aviso de sistema/finalidad/período/derechos está implementado para la ruta
con consentimiento. Antes de diseñar sus condicionales en excepción se delimitará
expresamente la política de información aplicable; no deducir desde la remisión
que todos los campos son dispensables, ni presentar una decisión conservadora
de producto como requisito textual inequívoco de la excepción.

### 50.2 Barrera EIPD y resultado que puede entregarse

El screening existente incluye datos_protegidos_excepcion_consentimiento.
Declarar una excepción real debe conservar la respuesta correspondiente y los
motivos de EIPD; no marcar no artificialmente para confirmar. Positivo exige EIPD
y permanece bloqueado en el flujo actual. Expediente especial documentalmente
preparado no equivale a screening negativo ni a EIPD aprobada.

Primera implementación podrá preparar y exponer esta excepción, pero no prometer
confirmación cuando EIPD la bloquea. Workflow completo EIPD mantiene diferimiento
original; habilitar confirmación tras resolución EIPD necesita diseño de ese
resultado/flujo y decisión explícita de alcance posterior. No eliminar el bloqueo
para declarar completado el régimen ni confundir preparado con confirmado.

### 50.3 Secuencia de siguiente trabajo

1. Fijar ambos contratos independientes y matriz: completitud, condicionales de
   etapa, foro administrativo, principios, información, residualidad, scopes,
   dependencia sensible y resultado EIPD conservado.
2. Schema/pruebas, persistencia/asociaciones históricas y evaluadores puros.
3. Integración de preparación/detección/EIPD; positivos mantienen bloqueo,
   HTTP demuestra motivos coherentes y conservación íntegra del vigente.
4. Diseñar la resolución de la dependencia EIPD antes de habilitar confirmación
   de excepción; no marcar DONE por preparación documental aislada.

Otras excepciones biométricas permanecen pendientes, no diferidas del alcance
integral. Solo documentación/delimitación: última suite integral anterior
1585 passed (§48), 58 verificaciones focalizadas posteriores (§49). No pruebas
reejecutadas, cambios de código, migración ni commit. M3-T1 EN PROGRESO.
Próximo: contrato/matriz de excepción sensible y biométrica de derechos.


## 51. Contratos y matriz de excepciones de derechos

Diseño documental, 2026-10-06. Continúa §50 dentro del alcance integral.
Fuente oficial: https://www.bcn.cl/leychile/navegar?idNorma=1209272 , arts16(d),
16bis inciso segundo(d), 16ter y 14ter. La excepción se documenta separadamente
de base ordinaria y consentimiento. Las estructuras/pruebas y la política
conservadora de información siguientes son decisiones de producto; no constituyen
una interpretación automática ni atribuyen al texto una obligación adicional.

### 51.1 Contexto común, sin aprobar una base ordinaria

RightsExceptionContextV1: extra forbid; textos/enums/respuestas nullable;
evidence list ContractEvidenceV1 con default_factory. No schema propio dentro del
contexto anidado; el documento raíz tiene schema_version Literal[1] = 1.

| Campo | Tipo | Requisito de preparación |
| --- | --- | --- |
| context_reference | str nullable | Referencia documental del caso, sin identificación personal |
| purpose_description | str nullable | Finalidad RAT por canonización v1 |
| route | Literal formulacion_derecho / ejercicio_derecho / defensa_derecho nullable | Actividad relativa al derecho |
| right_description | str nullable | Derecho concreto |
| right_basis_reference | str nullable | Fundamento del derecho; no exigir que todo derecho nazca de una norma con URL |
| right_holder | Literal responsable / tercero / ambos nullable | Vinculación documental |
| holder_connection_analysis | str nullable | Conexión de titulares/datos con derecho |
| forum_type | Literal tribunal_justicia / organo_administrativo nullable | Foro específico de excepción |
| forum_description | str nullable | Identificación del foro por metadata |
| proceeding_stage | Literal preparacion / en_curso / finalizado nullable | Etapa factual |
| proceeding_reference | str nullable | Referencia documental de actuación/caso, también en preparación |
| preparatory_actions | str nullable | Condicional de etapa preparacion |
| processing_operations | str nullable | Operaciones que la excepción cubre |
| necessity_analysis | str nullable | Necesidad específica para el derecho |
| data_minimization_analysis | str nullable | Datos/operaciones limitados |
| safeguards_analysis | str nullable | Medidas/principios aplicados al alcance |
| related_to_right | ContractResponseV1 nullable | Conexión fundada |
| necessary_for_route | ContractResponseV1 nullable | Necesidad fundada |
| within_forum_scope | ContractResponseV1 nullable | Foro fundado, no deducido de su nombre |
| principles_addressed | ContractResponseV1 nullable | Declaración fundada de medidas/principios, no certificación jurídica |
| post_proceeding_necessity_analysis | str nullable | Condicional de etapa finalizado |
| evidence | list ContractEvidenceV1 | Tipo y referencia por entrada |

No convertir organo_publico de RightsDefenseAssessmentV1 a
organo_administrativo automáticamente. Contexto común no hereda ni modifica el
contrato ordinario; no marca necesaria una base art13e para toda excepción.
En preparacion, referencia es documental, no número de expediente judicial
obligatorio; no inventar plazos procesales ni verificaciones de causas.

### 51.2 Documentos separados

SensitiveRightsExceptionAssessmentV1: extra forbid, schema_version 1; campos:

| Campo | Tipo | Función |
| --- | --- | --- |
| exception_basis | Literal defensa_derechos_art16d nullable | Supuesto sensible explícito |
| context | RightsExceptionContextV1 nullable | Antecedentes de derechos |
| sensitive_data_description | str nullable | Metadata de categorías sensibles |
| scope | SpecialScopeV1 nullable | Alcance coincidente declarado |
| exception_application_analysis | str nullable | Aplicación del supuesto a datos/operaciones |
| exception_conditions_met | ContractResponseV1 nullable | Declaración fundada; preparación de producto |
| evidence | list ContractEvidenceV1 | Referencias propias de excepción |
| notes | str nullable | Observaciones opcionales |

BiometricRightsExceptionAssessmentV1: extra forbid, schema_version 1; campos:

| Campo | Tipo | Función |
| --- | --- | --- |
| exception_basis | Literal defensa_derechos_art16bis_d nullable | Remisión biométrica específica |
| context | RightsExceptionContextV1 nullable | Caso biométrico vinculado al sensible |
| biometric_data_description | str nullable | Metadata de identificación biométrica |
| scope | SpecialScopeV1 nullable | Alcance conservador |
| unique_identification_analysis | str nullable | Relación del tratamiento técnico con identificación única |
| unique_identification_confirmed | ContractResponseV1 nullable | Declaración fundada del régimen |
| exception_application_analysis | str nullable | Necesidad biométrica concreta, no solo necesidad genérica de datos |
| exception_conditions_met | ContractResponseV1 nullable | Declaración fundada del supuesto |
| sensitive_context_connection_analysis | str nullable | Relación entre ambos expedientes y operaciones |
| systems | list BiometricSystemV1 | Sistemas e información documental |
| systems_coverage_analysis | str nullable | Cobertura de sistemas; M2 no verifica inventario |
| all_systems_documented | ContractResponseV1 nullable | Declaración fundada de cobertura |
| evidence | list ContractEvidenceV1 | Referencias propias |
| notes | str nullable | Observaciones opcionales |

Todas las listas default_factory; context/scope/enums/respuestas/textos permiten
null en borrador. Claves approved/result/can_confirm y no_aplica rechazadas.
Referencias de evidencia pueden ser parciales en borrador; fechas son opcionales
factuales. No datos biométricos crudos ni documentos íntegros en metadata.

Política inicial de información: reutilizar BiometricSystemV1 y exigir información
de sistema, finalidad, período y derechos, con sus cuatro respuestas y evidencia,
para declarar completo el expediente de excepción. Es frontera conservadora de
producto; no declarar que el art16ter resuelve inequívocamente todos los supuestos
de información en excepciones. Una dispensa o información diferida necesita
contrato/matriz propios posteriores; no se admite no_aplica ni se omiten campos
para forzar preparación. Art14ter se considera en análisis de transparencia,
pero no se afirma que este expediente audite por sí solo todos sus deberes.

### 51.3 Matriz de completitud y aplicabilidad

| Control | Aplicabilidad | Falta/pendiente | Negativo/contradicción |
| --- | --- | --- | --- |
| Contexto, textos comunes, enums, scope y exception_basis | Siempre | incompleto | Finalidad/rol/ruta/alcance incoherente: revisión |
| Respuestas contextuales y propias | Siempre | Ausente/pendiente/fundamento vacío: incompleto | No fundada: revisión |
| preparatory_actions | Etapa preparacion | Vacío: incompleto | Texto en otra etapa: residual/revisión |
| post_proceeding_necessity_analysis | Etapa finalizado | Vacío: incompleto | Texto en otra etapa: residual/revisión |
| Etapa ausente | Condicionales sin_resolver | Etapa incompleta; no exigir condicional como si fuera aplicable | No inferir desde referencia/fechas |
| Evidencia contextual y propia | Siempre | Lista vacía o tipo/referencia vacío: incompleto | No consulta externa |
| Datos/identificación/sistemas biométricos | Documento biométrico | Campos/respuestas/lista vacíos: incompleto | No/duplicados/discordancia: revisión |
| Información de cada sistema | Cada sistema | Campos/respuestas/evidencia incompletos | No fundada: revisión; dispensa aún no soportada |
| Dependencia sensible preparada | Excepción biométrica | Propagar incompleto | Propagar revisión |
| Datos de consentimiento especial en misma ruta sin consentimiento | Si aportados | No se exigen | Residualidad/mix de rutas: revisión, sin borrar |
| Otros regímenes detectados | Cuando concurren | Mantener motivos propios | Preparación de excepción no los elimina |
| EIPD | Siempre transversal | Sin resolver/obsoleto: bloquea | Excepción real/positivo mantiene requiere_eipd y bloqueo |

Precedencia incompleto > requiere_revision > completo. Aplicabilidad derivada,
motivos ordenados por contrato y por índices numéricos, question_id conservado en
dependencias, entradas inmutables. Respuestas afirmativas no sustituyen textos
de necesidad, fundamentos y evidencia; la prosa no se evalúa como sentencia legal.

### 51.4 Vinculación, coherencia y residualidad

Evaluadores futuros: evaluate_sensitive_rights_exception_v1(document, snapshot,
special) y evaluate_biometric_rights_exception_v1(document, snapshot, special,
sensitive_exception). No dependencia del checklist ni consentimiento sensible de
ruta con consentimiento. Validar contratos aunque falte otra dependencia.

Declaraciones datos_sensibles/biometricos_identificacion_unica afirmativas;
condiciones sensibles_art16 y biometricos_art16ter por excepcion_legal,
uses_consent_assessment false explícito. sensitive_condition_id
 defensa_derechos_art16d solo sensible; biometría no agrega ese campo ni lo acepta.
Condiciones: referencia legal, análisis y evidencia completos; la referencia
textual no se interpreta como autorización. Otros exception_basis no soportados
no se aceptan por compartir texto del derecho.

Contextos sensible/biométrico vinculan context_reference, finalidad, route,
right_holder, forum_type, proceeding_stage y proceeding_reference por comparación
semántica v1 de textos y exacta de enums. Descripciones/análisis pueden reflejar
operaciones biométricas más específicas; vínculo exige análisis documentado y no
igualdad literal de toda prosa/evidencia/notas. Diferencias de vínculo: revisión.

Scopes propios/declaraciones/condiciones coincidentes, no vacíos, válidos en RAT,
semánticamente únicos; categorías sensibles y todos los grupos del alcance.
Cobertura parcial por pares sigue pendiente. No inferir biometría desde flag
sensible ni foro/edad/representación desde nombres. Rol responsable inicial.
Excepción documental sin régimen/ruta correspondiente: revisión residual.

SensitiveConsentAssessmentV1/BiometricAssessmentV1 no se convierten a excepciones.
Su presencia cuando se propone la respectiva excepción produce revisión de
expediente residual; el checklist general puede pertenecer a la base ordinaria y
no se borra automáticamente. La base ordinaria mantiene su evaluador propio.
Cuando se propone consentimiento, documentos de excepción residuales también
producen revisión. No combinar subconjuntos de rutas en este primer soporte.

### 51.5 Persistencia/asociaciones y aceptación prevista

Futuras columnas sensitive_rights_exception_assessment y
biometric_rights_exception_assessment, JSONB nullable/none_as_null/check objeto;
CREATE/PATCH/GET, omisión preserva/null borra solo borrador/reemplazo entero.
Migración append-only desde f39b1d4e7a08. Asociaciones especiales v10/EIPD v11
incorporan ambos documentos finales conservando todos los comparadores previos;
documento no cubierto produce motivos específicos por cada expediente.
No circularidad, no cambio del hash RAT ni reasociación automática durante GET.

Readiness future sensitive_rights_exception/biometric_rights_exception nullable;
completo documental no garantiza confirmación. EIPD distingue propuesta preparada
de excepción no validada, conserva respuesta afirmativa y requiere_eipd; no
inventa resultado aprobada ni aceptación externa. Sin resolución EIPD diseñada
no se confirma la excepción, aunque estén completos los dos expedientes.

Aceptar mediante pruebas: contratos parciales/cerrados y etapa/foro, todos los
campos/respuestas/evidencias faltantes, sin_resolver/residualidad de condicionales,
referencias/vínculos/scopes discordantes, sistemas múltiples/duplicados/índices,
rutas mezcladas y consentimiento ausente sin dependencia artificial. Persistencia
SQL NULL/check objeto, exposición/aislamiento, históricos/obsolescencia/reaporte.
HTTP: completo aún bloqueado por EIPD, no falso negativo para confirmar; conservar
vigente y borrador en rechazo, proteger confirmado. Resolución de EIPD y
confirmación de excepción no se declaran entregadas en esta secuencia.

Solo documentación. M3-T1 EN PROGRESO, alcance integral. Última suite integral
1585 passed (§48) y 58 verificaciones posteriores (§49), no reejecutadas aquí.
Sin cambios de código, migración ni commit. Próximo: schemas de los tres tipos y
pruebas de contrato, antes de persistencia o evaluadores.


## 52. Schemas de excepciones de derechos implementados

Añadidos RightsExceptionContextV1, SensitiveRightsExceptionAssessmentV1 y
BiometricRightsExceptionAssessmentV1 según §51. Contratos extra forbid,
contexto/alcance/textos/enums/respuestas nullable, listas independientes y
schema_version 1 en documentos raíz. Foro especial admite tribunal_justicia y
organo_administrativo; no amplía ni convierte RightsDefenseAssessmentV1 ordinario.
Bases especiales diferenciadas: defensa_derechos_art16d y
defensa_derechos_art16bis_d. Biometría reutiliza BiometricSystemV1.

102 casos nuevos: parciales, listas independientes, enums, respuestas si/no/
pendiente, serialización/roundtrip/fechas, contexto anidado, alcance, evidencia,
campos extra/aprobaciones calculadas/no_aplica, sistemas y separación de rutas.
Condicionales de etapa y duplicados semánticos se conservan en borrador para el
futuro evaluador; schema no declara preparación ni aprobación EIPD.

Validación seleccionada de contratos nuevos y licitud/sensible/salud/biometría:
252 passed. Black/Ruff/whitespace correctos. Última suite integral anterior:
1585 passed (§48), no reejecutada para este cambio aislado de contratos.
No persistencia/API/asociaciones, evaluador ni habilitación de excepciones todavía.
Sin migración nueva ni commit. M3-T1 EN PROGRESO, alcance integral.
Próximo: persistencia/exposición de ambos expedientes y asociaciones especiales
v10/EIPD v11 compatibles; mantener positivo EIPD y rutas pendientes bloqueadas.


## 53. Persistencia y API de excepciones de derechos

Implementados los dos expedientes nullable en LegalAssessment y CREATE/PATCH/GET.
JSONB con SQL NULL y constraints de objeto; migracion append-only a40c2e5f8b19
aplicada desde f39b1d4e7a08. Alembic check sin diferencias nuevas.
PATCH conserva por omision, reemplaza el documento entero y permite null solo
sobre borrador; confirmado permanece protegido. Fechas serializadas en JSON.

Tres casos HTTP (sensible, biometrico, ambos) verifican almacenamiento, omision,
reemplazo, borrado/SQL NULL, contratos invalidos y constraint de objeto,
aislamiento entre organizaciones y proteccion de confirmado. GET/POST comparten
asociacion_excepcion_derechos_no_cubierta: cualquier documento presente bloquea
confirmacion con 409 y preserva integramente borrador y vigente. El caso positivo
tras borrar documentos valida la ruta ordinaria, no una excepcion.

Las asociaciones siguen especiales v9/EIPD v10: los nuevos expedientes todavia
no forman parte de sus hashes. La barrera explicita impide confirmar aunque esas
asociaciones anteriores parezcan vigentes. No hay reasociacion automatica ni
cambio del hash RAT. Proximo paso: especiales v10/EIPD v11 con ambos documentos
y comparadores historicos; despues, evaluadores propios de completitud.
Preparacion documental no habilita excepciones sin resolver la dependencia EIPD.

Black/Ruff/whitespace correctos; tres pruebas focalizadas aprobadas. Regresion
integral: 1712 passed en 169.95 segundos. M3-T1 EN PROGRESO, alcance integral; sin commit.


## 54. Asociaciones de excepciones: especiales v10 y EIPD v11

Los constructores nuevos incorporan sensitive_rights_exception_assessment y
biometric_rights_exception_assessment al material final de hash. CREATE y PATCH
con controles aportados usan especiales v10/EIPD v11, despues de aplicar cambios
al documento; EIPD incluye la asociacion especial final, sin circularidad.
Hash RAT canonico v1 y migraciones sin cambios. Head local a40c2e5f8b19.

Comparadores anteriores se conservan: especiales v1-v9 y EIPD v1-v10 siguen
vigentes si ambos documentos estan ausentes y el resto del contexto coincide.
Un documento presente, incluso {}, produce motivo especifico por expediente
si la version historica no lo cubre: asociacion_excepcion_sensible_no_cubierta o
asociacion_excepcion_biometrica_no_cubierta. Ambos motivos aparecen cuando
corresponde. Las versiones nuevas revalidan los contratos de excepcion.

Alta, edicion y borrado de documentos invalidan asociaciones previas sin
reescribirlas; GET/readiness no mutan ni reasocian. Reaportar solo condiciones
especiales no actualiza EIPD: hace falta aportar cada control. Asociacion actual
no implica completitud ni autorizacion; barrera compartida GET/POST
excepcion_derechos_no_preparada mantiene 409 por cada documento presente
mientras faltan evaluadores propios. Se sustituye el motivo provisional §53 de
falta de cobertura por este motivo de preparacion, sin habilitar excepciones.

96 casos nuevos de servicios: 76 historicos (19 versiones x cuatro presencias),
cuatro de versiones actuales, catorce mutaciones y dos equivalencias/revalidacion
Pydantic/JSON. 22 casos HTTP nuevos: 19 historicos y tres de mutacion/reaporte,
con preservacion integra del borrador y vigente ante rechazo. Tres HTTP de
persistencia existentes ampliados para borrado obsoleto y reaporte ordinario.
Respuesta EIPD afirmativa se conserva; sin condicion especial documentada da
pendiente_revision/excepcion_consentimiento_no_documentada y sigue bloqueada.
No se acredita que una excepcion real pueda confirmarse ni se altera el screening.

Formato/lint/whitespace verificados. Regresion integral: 1830 passed en 184.29 s.
Proximo: evaluador de completitud/aplicabilidad de excepcion sensible de derechos,
seguido del biometrico y sus vinculos. Resolucion EIPD sigue pendiente de diseno.
M3-T1 EN PROGRESO, alcance integral; sin migracion nueva ni commit.


## 55. Evaluador puro de excepcion sensible de derechos

Implementado evaluate_sensitive_rights_exception_v1(document, snapshot, special)
en backend/app/services/sensitive_rights_exception.py. Resultado inmutable:
incompleto/requiere_revision/completo, motivos con field/code/category/question_id
y aplicabilidad aplicable/no_aplicable/sin_resolver. can_confirm significa solo
preparacion documental, no autorizacion ni superacion de EIPD. No dependencia
artificial del checklist de consentimiento ni de la base ordinaria art13e.
Referencia oficial reconsultada: https://www.bcn.cl/leychile/navegar?idNorma=1209272,
art16(d); controles de producto segun matriz §51, sin certificacion juridica.

Contexto exige textos de derecho/operaciones/necesidad/minimizacion/salvaguardas,
fundamento del derecho sin URL normativa obligatoria, enums, respuestas fundadas
y evidencia. preparatory_actions solo en preparacion, analisis posterior solo en
finalizado; prosa residual en otra etapa requiere revision. Etapa ausente deja
ambos condicionales sin_resolver, sin inferir desde prosa ni exigirlos como
aplicables. Declaraciones afirmativas no sustituyen analisis ni evidencia.

Rol responsable inicial, finalidad por canonizacion v1, coherencia sensible del
RAT. Declaracion datos_sensibles afirmativa/fundada, condicion sensibles_art16 por
excepcion_legal, ID defensa_derechos_art16d y uses_consent_assessment false
explicito. Campos ausentes incompletos; rutas/negativos incoherentes revision.
Referencia/analisis/evidencia de condicion obligatorios, sin consulta externa.
Scopes propios/declaracion/condicion semanticamente unicos, coincidentes y
cubriendo todas las categorias sensibles y grupos del RAT. No autoriza cobertura
parcial por pares ni convierte organo_publico en organo_administrativo.

172 pruebas nuevas aprobadas: rutas/foros/etapas/titulares, textos/enums/respuestas,
condicionales/residualidad, evidencia, alcance parcial/duplicados/invalido,
canonizacion/Unicode, ausencias/contradicciones, revalidacion de modelos mutados
incluso con otra dependencia ausente, equivalencia JSON/fechas, orden numerico,
prioridad incompleto e inmutabilidad. Dos verificaciones transversales demuestran
que completo puro conserva bloqueo de excepcion y EIPD con respuesta no o si;
positivo se conserva y excepcion_especial_no_validada mantiene pendiente_revision.
Formato/lint/whitespace correctos. Ultima suite integral anterior: 1830 passed
(§54), no reejecutada para este evaluador aislado todavia no conectado a la API.

No modifica asociaciones/migracion ni habilita confirmacion. Falta exponer su
readiness e integrar el evaluador en detector/gates compartidos, incluyendo
residualidad del expediente de consentimiento sensible; despues evaluador
biometrico y vinculos. Resolucion EIPD sigue pendiente de diseno. M3-T1 EN
PROGRESO, alcance integral; sin commit.


## 56. Integracion de excepcion sensible en readiness y barreras

API readiness expone sensitive_rights_exception nullable: se evalua si hay
documento o condicion sensible que propone excepcion_legal/defensa_derechos_art16d.
Una propuesta sin documento produce expediente_ausente; un contexto sensible sin
propuesta de excepcion no crea un expediente por inferencia. Resultado de lectura
orientativo, inmutable; no reasocia ni modifica documentos/estado.

Detector especial integra el evaluador para sensibles_art16/excepcion_legal/
defensa_derechos_art16d y propaga field/code/category/question_id, conservando
rutas restantes como no implementadas. Completo documental puede dar
regimenes_preparados, sin aprobar la excepcion juridica ni habilitar confirmacion.
La barrera compartida GET/POST usa excepcion_derechos_no_preparada para faltas
sensibles: 400 incompleto, 409 revision. Otros controles pueden elevar el rechazo
a 409; EIPD real sigue en pendiente_revision por excepcion_especial_no_validada.
El expediente biometrico conserva la barrera provisional hasta su evaluador.

Consentimiento sensible presente con ruta excepcion_legal produce
expediente_consentimiento_sensible_residual. Expediente de excepcion sensible
sin regimen o ruta correspondiente produce expediente_excepcion_sensible_residual,
incluida propuesta por consentimiento. No se borran ni convierten documentos;
checklist general puede pertenecer a la base ordinaria y conserva evaluador propio.
Asociaciones especiales v10/EIPD v11 y hash RAT sin cambios.

Doce pruebas nuevas: seis de barrera/propagacion en servicios y seis HTTP sobre
las bases ordinarias con RAT real. HTTP verifica complete/incomplete/ausente,
lectura nullable, aislamiento, motivos compartidos, documento obsoleto/reaporte,
residualidad en ambos sentidos, positivo EIPD conservado, falso negativo
excepcion_consentimiento_discordante, revalidacion del RAT y preservacion integra
de borrador/vigente ante rechazo. No confirma una excepcion ni extrapola
concurrencia a esta nueva ruta. 209 verificaciones focalizadas aprobadas, mas
seis HTTP reejecutadas con escenarios de residualidad inversa/EIPD discordante.

Formato/lint/whitespace correctos. Regresion integral: 2014 passed en 199.23 s.
Proximo: evaluador puro biometrico de derechos y vinculos con el sensible,
seguido de integracion propia. Resolucion EIPD permanece pendiente de diseno;
no alterar screening para eludirla. Head local a40c2e5f8b19, sin migracion nueva
ni commit. M3-T1 EN PROGRESO, alcance integral.


## 57. Evaluador puro biometrico de derechos y vinculos sensibles

Implementado evaluate_biometric_rights_exception_v1(document, snapshot, special,
sensitive_exception) en backend/app/services/biometric_rights_exception.py.
Resultado inmutable incompleto/requiere_revision/completo, motivos ordenados por
contrato/indices numericos y aplicabilidad derivada. can_confirm significa solo
preparacion documental; no habilita tratamiento ni supera controles EIPD.
Sin dependencia artificial de consentimiento ni de una base ordinaria art13e.

Propaga preparacion sensible con field/code/category/question_id y aplicabilidad,
con prefijo sensible donde corresponde. Valida contratos aun cuando otra
dependencia falte. Contexto biometrico exige derecho/operaciones/necesidad,
minimizacion/salvaguardas, foro y etapa, evidencia y respuestas fundadas; mismos
condicionales de preparacion/finalizado, etapa ausente sin_resolver y textos
residuales en otra etapa requieren revision. Vincula context_reference,
purpose_description y proceeding_reference por canonizacion v1; route,
right_holder, forum_type y proceeding_stage por igualdad de enums. No compara
toda prosa ni evidencia literalmente: analisis biometrico puede ser especifico.
Analisis de conexion entre ambos expedientes obligatorio.

Declaracion biometricos_identificacion_unica afirmativa/fundada; condicion
biometricos_art16ter por excepcion_legal y uses_consent_assessment false explicito.
Documento exception_basis defensa_derechos_art16bis_d; no agrega ID sensible a
condicion biometrica. Referencia/analisis/evidencia de condicion requeridos.
Scope completo de categorias sensibles y grupos del RAT, coincidente con
expediente/declaracion/condicion y sensible; cobertura parcial por pares pendiente.

Exige identificacion unica documentada, descripcion biometrica, aplicacion de la
excepcion, lista de sistemas, declaracion/analisis de cobertura y evidencia.
Cada sistema requiere diez textos, cuatro respuestas fundadas y evidencia;
referencias de sistema duplicadas semanticamente producen revision. Inventario
M2 no se verifica automaticamente. Politica conservadora de informacion de §51:
no implica afirmar una obligacion universal ni soporta dispensa/no_aplica.

208 pruebas nuevas aprobadas: campos/respuestas/enums/etapas, siete vinculos,
canonizacion/Unicode/prosa especifica, dependencia sensible/motivos/aplicabilidad,
evidencia, scopes completos/invalidos/duplicados/discordantes, condicion/declaracion,
sistemas multiples y numeracion, revalidacion de modelos mutados incluso con
otra dependencia ausente, equivalencia JSON/fechas e inmutabilidad/preferencia
incompleto. Dos verificaciones transversales acreditan que completo puro sigue
bloqueado por detector/gates actuales y EIPD; positivo permanece afirmativo.

Formato/lint/whitespace correctos. Ultima suite integral anterior: 2014 passed
(§56), no reejecutada para este evaluador aislado todavia no conectado a la API.
Sin cambios de contratos/asociaciones/migraciones ni habilitacion de confirmacion.
Proximo: readiness nullable e integracion biometrica en detector/gates con
residualidad de consentimiento/excepcion, manteniendo evaluador de cada ruta y
barrera EIPD. M3-T1 EN PROGRESO, alcance integral; sin commit.


## 58. Integracion biometrica de derechos en readiness y barreras

API readiness expone biometric_rights_exception nullable: evalua documento
presente o propuesta biometricos_art16ter/excepcion_legal, incluso sin documento.
Detector integra el evaluador biometrico y propaga motivos propios y dependencia
sensible con field/code/category/question_id. Campos faltantes producen barrera
compartida excepcion_derechos_no_preparada (400 incompleto, 409 revision).
GET y POST usan las mismas reglas; lectura no escribe, confirma ni reasocia.

Seleccion explicita de rutas: biometric_assessment por consentimiento se evalua
cuando se aporta o cuando el regimen detectado no propone excepcion_legal;
la excepcion sin documento de consentimiento no adquiere dependencia artificial.
Un documento de consentimiento aportado en ruta excepcion genera
expediente_biometria_residual; documento de excepcion en otra ruta/sin regimen
genera expediente_excepcion_biometrica_residual. No se convierten ni borran datos.
Rutas restantes y otros regimenes conservan evaluadores/barreras propios.

Ambas excepciones documentalmente completas pueden dar regimenes_preparados.
EIPD conserva pendiente_revision/excepcion_especial_no_validada: asociaciones
actuales y documentos completos no autorizan la excepcion ni habilitan
confirmacion. Positivo no se cambia, negativo discordante tampoco elimina bloqueo.
Especiales v10/EIPD v11, hash RAT y head local a40c2e5f8b19 sin cambios.

Doce casos nuevos: seis de categorias/propagacion en servicios y seis HTTP sobre
bases ordinarias con RAT real. HTTP verifica readiness nullable, preparacion
completa sin consentimiento especial, documento ausente/pendiente/obsoleto,
reaporte, dependencia sensible null/parcial, discordancia de caso, segundo
sistema incompleto, residualidad en ambos sentidos, EIPD positivo/negativo
discordante, cambio de RAT y aislamiento. Todos los rechazos conservan integro
borrador y vigente; ninguna excepcion confirmada. No extrapolar concurrencia.
251 verificaciones focalizadas aprobadas, incluidos escenarios anteriores de
excepciones/asociaciones. Formato/lint/whitespace correctos.

Regresion integral: 2234 passed en 218.12 s. Proximo: definir diseno/alcance de
resolucion EIPD para estas excepciones, con evidencia y decision trazable antes
de habilitar confirmacion; workflow completo sigue diferido segun diseno previo,
sin bypass ni aprobacion implicita. Mantener los demas pendientes funcionales del
alcance integral. Sin migracion nueva ni commit; M3-T1 EN PROGRESO.


## 59. Resolucion EIPD acotada: evaluacion externa y revision trazable

Paso documental, 2026-10-06. Continua §58 dentro del alcance integral, sin
habilitar confirmaciones. Fuente primaria reconsultada:
https://www.bcn.cl/leychile/navegar?idNorma=1209272, art15ter: EIPD previa al
tratamiento en supuestos obligatorios, incluida excepcion de consentimiento en
datos sensibles/especialmente protegidos. Sus criterios incluyen operaciones,
finalidad, necesidad/proporcionalidad, riesgos y mitigacion. La consulta a la
Agencia para obtener recomendaciones es una posibilidad prevista en ese articulo.
La revision interna de producto descrita aqui no es una aprobacion regulatoria.

### 59.1 Frontera del primer soporte

Registrar metadata de una EIPD realizada y conservada por la organizacion fuera
de CumpleIA, su analisis estructurado y una revision humana autenticada. No basta
una referencia generica ni una casilla approved. Workflow completo de autoria,
custodia de anexos, inventario exhaustivo e intercambio con la Agencia permanece
diferido; esta secuencia implementara solo registro/revision y decision de gate.
No enviar comunicaciones externas ni usar LLM para aprobar contenido juridico.

Primera continuacion soportada: sensible art16(d), sola o junto con biometria por
art16ter/art16bis(d), con ambos evaluadores pertinentes completos, asociaciones
actuales, rol responsable, alcance integral del contexto y sin rutas mezcladas.
El screening exige datos_protegidos_excepcion_consentimiento=si fundada y las
otras cuatro respuestas no fundadas, completas y coherentes con RAT/LIA.
Otro positivo, pendiente, regimen no soportado o contradiccion conserva bloqueo;
ampliar despues con contrato/aceptacion propios, sin recortar pendientes integrales.

### 59.2 Contenido y contrato a concretar antes de codigo

EipdResolutionAssessmentV1: documento cerrado/partial en borrador, schema_version
1; null/textos/enums/respuestas opcionales hasta evaluacion, listas independientes.
Metadata, referencias y analisis solamente; sin datos personales/biometricos crudos.

| Seccion | Preparacion requerida |
| --- | --- |
| Referencia de EIPD | Identificador documental, version, fecha de finalizacion, referencia a informe y responsable de su elaboracion |
| Alcance y operaciones | Finalidad coincidente con RAT, categorias/grupos completos de la evaluacion, operaciones/contexto/tecnologia y analisis de cobertura de ambas excepciones |
| Necesidad/proporcionalidad | Analisis propios de finalidad, minimizacion y medidas; respuestas fundadas y evidencia |
| Evaluacion previa | Declaracion documentada de realizacion antes del tratamiento, con fundamento/evidencia; no inferirla de fecha de subida o confirmacion |
| Riesgos | Lista de riesgos referenciados, descripcion/impacto, valoracion inicial/residual fundada y evidencia; IDs semanticamente unicos |
| Medidas | Referencia de medida y riesgos que cubre, descripcion/eficacia/implantacion y evidencia; referencias coherentes; plan pendiente no equivale a medida implantada |
| Conclusion | Sintesis de riesgo residual, declaracion no_alto/alto/sin_resolver fundada, limites y seguimiento; no calcular umbral legal ni puntaje propio |
| Fuentes oficiales | Revision de listas/orientaciones, fuentes consultadas, fecha, referencias y analisis de aplicabilidad; estado identificado/no_identificado/pendiente documentado |
| Consulta a Agencia | Estado no_solicitada/en_curso/concluida, analisis y referencias condicionales; recomendaciones son antecedentes de revision |
| Evidencia general | Tipo y referencia completos; fechas opcionales factuales aparte de las fechas de revision/finalizacion requeridas |

Fechas/enums/condicionales exactos se fijaran en el siguiente contrato/matriz.
Sin_resolver/faltas son incompleto; negacion/discordancia son revision. Etapas y
condicionales no se deducen desde nombres o prosa. Scope EIPD cubre todas las
categorias/grupos del RAT de esta evaluacion, incluidos los no sensibles; las
excepciones mantienen sus scopes sensibles, contenidos en ese alcance, sin
forzar igualdad entre scopes de diferente funcion.

Riesgo residual alto mantiene bloqueo como frontera conservadora de producto;
no se atribuye al articulo una prohibicion general ni consulta obligatoria.
Consulta en_curso mantiene revision; concluida exige analizar antecedentes y
actualizar evaluacion/medidas cuando corresponda, sin convertir recomendaciones
en autorizacion automatica. No_solicitada no omite evaluacion ni riesgo residual.
No declarar completo solo por aportar informe o marcar todos los controles si.

### 59.3 Revision humana separada del payload

Eventos append-only EipdResolutionReview: tenant y assessment, decision
continuar/requiere_cambios/no_continuar, fundamento/referencia de revision,
hash del documento revisado y hash de contexto, actor y fecha de servidor.
Actor/fecha/tenant/hashes/estado de revision no son campos editables por el cliente.
Permiso edit_content y suscripcion vigente, coherentes con M3; permiso de app no
certifica titulacion ni juicio juridico. La revision expresa una decision humana
interna documentada y no se genera desde una conclusion LIA ni desde el LLM.

Registro de continuar exige documento completo, contexto vigente, riesgo residual
no_alto fundado y todos los controles de esta frontera superados. Requiere_cambios
/no_continuar mantienen bloqueo. Eventos historicos no se sobrescriben: editar
la EIPD o su contexto invalida la revision anterior aunque quede visible en el
historial. Confirmado/reemplazado siguen inmutables; revision nueva solo en borrador.

### 59.4 Asociaciones y transaccion

Sin cambiar hash RAT v1 ni constructores/comparadores especiales v1-v10 y EIPD
v1-v11. Context binding de resolucion v1 incluye snapshot completo, legal_basis,
consentimiento y todos los expedientes ordinarios/especiales finales, condiciones
especiales y screening finales. No incluye el propio documento de resolucion ni
sus eventos. Hash documental separado de la resolucion normalizada incluye su
context_binding y contenido, excluyendo estados/actor/historial de revision.
Revision vincula ambos hashes. No circularidad ni actualizacion automatica en GET.

Orden de escritura: aplicar borrador/documentos; asociar condiciones especiales;
asociar screening; asociar resolucion al contexto final; revision humana sobre
version/hashes concretos. Cambios en cualquiera de esas entradas vuelven obsoleto
el evento previo; reaporte documental no reproduce la decision humana.

Propuesta fisica a concretar: columna JSONB nullable/check objeto para resolucion
y tabla de eventos con organization_id, FK compuesta y RLS desde su migracion
append-only inicial. CREATE/PATCH/GET de metadata; accion separada para registrar
revision con campos de servidor. PATCH omite/preserva, null borra solo borrador,
reemplazo entero; historial permanece. Accion de revision y confirmacion bloquean
la misma serie, releen populate_existing y recomponen RAT/contexto antes de
cualquier cambio. Rechazo/rollback conserva vigente, borrador y eventos previos.

### 59.5 Screening y gate sin borrar el positivo

Mantener cuestionario/contratos/hash actuales. Evaluacion versionada v2 prevista:
solo cuando todas las excepciones declaradas pertenezcan a esta frontera y esten
preparadas, distinguir propuesta documental preparada de ruta no soportada.
La deteccion conserva requiere_eipd y sus motivos; no depende del resultado de
la revision ni se convierte en sin_supuestos_declarados. La version v1 permanece
como comparador/evaluador historico; no borrar sus motivos de snapshots anteriores.

Gate separado combina screening vigente, resolucion completa, revision humana
continuar actual y controles ordinarios/especiales. Permite continuar solo dentro
de esta frontera, con EIPD aun requerida pero documentada y revisada; nunca filtra
arbitrariamente blockers por codigo. Sin documento/revision/contexto vigente,
misma barrera actual. Residualidad: resolucion sin necesidad/propuesta soportada
requiere revision y no aprueba otras rutas. GET ofrece ambos resultados y motivos,
POST revalida iguales reglas despues del lock, antes de reemplazar confirmado.

### 59.6 Fuentes pendientes y aceptacion previa al desbloqueo

Busqueda acotada de listas/orientaciones en fuentes oficiales, 2026-10-06: se
verifico el texto legal; no se verifico una publicacion especifica de orientaciones
aplicables. Esto no acredita inexistencia. Registro de fuentes/estado queda
pendiente; antes de habilitar confirmacion deben verificarse las fuentes vigentes
y registrar su aplicabilidad/version, segun §18.21. No inventar listado ni plazo.
El contrato permite conservar esta tarea pendiente sin forzar un no negativo.

Aceptar mediante pruebas de contratos cerrados/parciales, todos los faltantes,
IDs/medidas/riesgos discordantes, etapas/fuentes/consulta sin_resolver y residualidad,
preparacion y decision separadas, campos de servidor no falsificables, hashes y
revisiones obsoletos por cada documento/RAT, aislamiento/RLS, historial inmutable,
GET sin escritura, seis bases ordinarias, positivo EIPD persistente, unsupported
positivo bloqueado, dos sesiones con RAT real y rollback sin reemplazo parcial.
Solo despues de esa evidencia y revision de fuentes habilitar la frontera concreta.

Este paso solo fija diseno; no codigo/schema/API/migracion ni habilitacion de gates.
Ultima suite integral 2234 passed (§58), no reejecutada para documentacion.
Proximo: contrato fisico/matriz de resolucion y eventos, antes de schemas.
M3-T1 EN PROGRESO, alcance integral; sin commit.


## 60. Contratos y matriz de resolucion EIPD v1

Paso documental, 2026-10-06; concreta §59 sin modificar codigo ni habilitar gates.
Los requisitos siguientes son controles del producto dentro de esa frontera.
No agregan umbrales legales ni sustituyen verificacion de fuentes oficiales.

### 60.1 Convenciones y documento editable

Todos los modelos son cerrados (extra=forbid). schema_version Literal[1]=1.
Campos textuales, fechas, enums, respuestas y objetos anidados nullable/default
None permiten guardar borrador parcial; listas default_factory=list independientes.
Reutilizar ContractResponseV1 (si/no/pendiente, rationale), ContractEvidenceV1
(evidence_type obligatorio al aportar objeto, reference, obtained_on date,
mechanism, notes) y SpecialScopeV1. Sin no_aplica ni campos de aprobacion.
Fechas documentales date; fecha de evento datetime UTC generada por servidor.
Campo obligatorio para completitud no implica obligatorio para guardar borrador.

EipdResolutionAssessmentV1:

| Campo | Tipo |
| --- | --- |
| schema_version | Literal[1] |
| document_reference, document_version, report_reference, prepared_by | str nullable |
| completed_on | date nullable |
| purpose_description, processing_operations, processing_context, technologies_description, exceptions_coverage_analysis | str nullable |
| scope | SpecialScopeV1 nullable |
| necessity_analysis, proportionality_analysis, minimization_analysis | str nullable |
| necessary_for_purpose, proportionate_processing, minimization_addressed, performed_before_processing | ContractResponseV1 nullable |
| prior_assessment_analysis | str nullable |
| risks | list[EipdRiskV1] |
| measures | list[EipdMeasureV1] |
| residual_risk_summary, residual_risk_rationale, limitations_analysis, follow_up_plan | str nullable |
| residual_risk_level | Literal[no_alto, alto, sin_resolver] nullable |
| official_sources | EipdOfficialSourcesV1 nullable |
| agency_consultation | EipdAgencyConsultationV1 nullable |
| evidence | list[ContractEvidenceV1] |
| notes | str nullable |
| context_binding | Asociacion calculada por servidor, separada de contenido de entrada |

context_binding no es un campo libre del contrato editable: el servicio lo produce
al asociar explicitamente el documento al contexto final, como §59.4. La forma
persistida/salida incorpora binding_version=1 y context_hash SHA-256 hexadecimal
(64 caracteres). El hash documental incluye esta asociacion. CREATE/PATCH no
aceptan actor, tenant, hashes, decisiones ni revision_status. Definir una entrada
cerrada y una salida/persistencia cerrada diferenciadas al implementar schemas;
no usar un mismo modelo que permita falsificar metadata del servidor.

EipdRiskV1: risk_id, description, impact_analysis, initial_assessment_analysis,
residual_assessment_analysis str nullable; evidence list[ContractEvidenceV1].
No puntuacion ni escala numerica inferida. EipdMeasureV1: measure_id, description,
effectiveness_analysis, implementation_analysis str nullable; risk_ids list[str];
implemented ContractResponseV1 nullable; evidence list[ContractEvidenceV1].

EipdOfficialSourcesV1: status Literal[identificado,no_identificado,pendiente]
nullable; checked_on date nullable; sources list[EipdOfficialSourceV1];
applicability_analysis str nullable; evidence list[ContractEvidenceV1].
EipdOfficialSourceV1: source_reference, publication_version, review_analysis str
nullable; applicability Literal[aplicable,no_aplicable,pendiente] nullable.
Una fuente consultada puede no tener publicacion/version identificada; su analisis
debe explicar el resultado. no_identificado registra una busqueda documentada,
no acredita inexistencia ni desbloquea por si solo el requisito global de §59.6.

EipdAgencyConsultationV1: status Literal[no_solicitada,en_curso,concluida]
nullable; analysis, consultation_reference, response_reference,
recommendations_analysis, reassessment_analysis str nullable;
recommendations_addressed ContractResponseV1 nullable;
evidence list[ContractEvidenceV1]. Referencias son metadata, no carga de anexos.

### 60.2 Completitud y aplicabilidad deterministas

Todo texto exigido debe contener contenido no blanco; cada respuesta exigida
requiere rationale no blanco. Evidencia exigida significa lista no vacia con tipo
no blanco y referencia no blanca por elemento; obtained_on es opcional factual.
IDs se comparan tras canonizacion coherente con servicios existentes; duplicados
semanticos y referencias desconocidas requieren revision, no se deduplican.
Acumular todos los motivos: requiere_revision prevalece sobre incompleto cuando
coexisten; completo solo sin faltantes ni discordancias. Mostrar aplicabilidad
explicita de condicionales y rutas, sin inferir hechos desde texto libre.

| Bloque | Requisito para preparacion | Incompleto | Requiere revision |
| --- | --- | --- | --- |
| Informe | Cuatro referencias/textos iniciales y completed_on; fecha no futura | Campo ausente/blanco | Fecha futura |
| Alcance | purpose_description coincidente con RAT canonizado; scope cubre exactamente categorias/grupos de la evaluacion; operaciones/contexto/tecnologia y cobertura de excepciones fundadas | Campo o alcance faltante | Diferencia de finalidad/scope; excepcion fuera del alcance |
| Necesidad | Tres analisis y tres respuestas si fundadas | Ausente/pendiente/sin fundamento | Respuesta no |
| Evaluacion previa | performed_before_processing si fundada, prior_assessment_analysis y evidencia general | Ausente/pendiente | No; no inferir si desde completed_on |
| Riesgos | Al menos un riesgo, todos sus textos, ID unico y evidencia propia | Lista vacia/campo/evidencia faltante | IDs repetidos |
| Medidas | Al menos una medida; textos, ID unico, risk_ids no vacios, implemented si fundada y evidencia propia; todos los riesgos cubiertos | Campo/lista/evidencia faltante; riesgo sin cobertura | IDs repetidos/desconocidos; implemented no |
| Conclusion | Sintesis, rationale, limites, seguimiento y residual_risk_level no_alto | Ausente/sin_resolver | alto; bloqueo conservador de producto |
| Fuentes | Estado, fecha no futura, fuentes consultadas no vacias, referencias/analisis y analisis general/evidencia | Ausente/pendiente; fuente con applicability pendiente | Fecha futura; contradiccion con estado declarado |
| Fuentes identificadas | identificado exige al menos una publicacion con version y analisis de aplicabilidad resuelto; no_identificado exige explicar busqueda y resultados en todas las fuentes | Version/analisis requerido faltante | no_identificado junto con publicacion aplicable identificada |
| Consulta | Estado y analisis siempre requeridos | Ausente | en_curso |
| Consulta no_solicitada | Analisis de decision; campos de respuesta/recomendaciones no aplicables | Analisis ausente | Referencias/respuestas residuales de consulta aportadas |
| Consulta en_curso | consultation_reference y evidencia; respuesta/recomendaciones no aplicables hasta conclusion | Referencia/evidencia faltante | Estado en_curso mantiene revision; respuesta concluida residual |
| Consulta concluida | Ambas referencias, recomendaciones/reassessment analizados, recommendations_addressed si fundada y evidencia | Ausente/pendiente | recommendations_addressed no |
| Asociacion | Binding v1 y hash del contexto final vigentes | Asociacion ausente | Contexto obsoleto o version no soportada |
| Frontera | §59.1: excepciones pertinentes preparadas; screening positivo esperado y cuatro no fundados; controles ordinarios/especiales actuales | Documento/control faltante | Otra ruta/positivo, contradiccion o expediente residual |

publication_version solo es exigida para una publicacion identificada; no exigir
version ficticia a un sitio consultado sin resultado. No generar conclusiones de
riesgo mediante aritmetica ni validar la veracidad externa del informe por metadata.
Fuentes documentadas completas no satisfacen automaticamente la verificacion
normativa global pendiente: mantener barrera separada hasta resolver §59.6.

### 60.3 Entrada de revision, salida y evento persistido

EipdResolutionReviewIn cerrado: decision obligatorio Literal[continuar,
requiere_cambios,no_continuar]; rationale y review_reference str obligatorios
no blancos. Sin defaults de decision. El cliente expresa su decision humana;
no puede aportar hashes/actor/fecha/organization_id ni estado de vigencia.

Evento EipdResolutionReviewOut cerrado: id UUID, organization_id UUID,
assessment_id UUID, decision/rationale/review_reference, document_hash,
context_hash (SHA-256 hex), created_by UUID, created_at datetime UTC. Servidor
resuelve estos campos autenticando usuario y releyendo contexto bajo lock.
Persistir mismos datos, FK compuesta assessment/tenant y actor referenciado;
RLS tenant desde migracion inicial. El runtime no modifica/elimina eventos.
Probar esta inmutabilidad tambien por acceso SQL app_user, no solo ausencia de PATCH.

Lectura deriva review_status Literal[sin_revision,vigente,obsoleta] y latest_review
nullable del ultimo evento de ese assessment, con orden estable created_at/id.
No elegir un continuar antiguo cuando el ultimo evento requiere cambios.
Vigente describe igualdad de ambos hashes, no aprobacion: requiere_cambios y
no_continuar siguen bloqueando. Historial preservado aun al borrar documento.
Sin documento con historial: obsoleta; sin eventos: sin_revision.

continuar exige preparacion completa y frontera/fuentes verificadas actuales;
las otras decisiones admiten documento parcial presente con binding vigente para
registrar rechazo concreto, conservando bloqueo. Documento ausente, binding
obsoleto, assessment no borrador o permiso/suscripcion insuficientes rechazan
cualquier evento. Rechazo no escribe ni modifica historial. Revision no confirma.

### 60.4 Plan de implementacion y aceptacion

1. Schemas separados editable/persistido/revision/salida y pruebas de cierre,
   borradores parciales, enums/fechas/listas y metadata no falsificable.
2. Asociacion/hash puros; persistencia JSONB nullable con CHECK objeto y eventos
   append-only/RLS; API documental/revision sin abrir confirmacion.
3. Evaluador puro de matriz y motivos/aplicabilidad; readiness de preparacion y
   vigencia separado de decision y de deteccion EIPD versionada.
4. Fuentes verificadas y gates compartidos GET/POST dentro de §59.1; probar seis
   bases, screening positivo preservado, toda invalidacion, residuos, aislamiento,
   historial, dos sesiones app_user con RAT real y rollback sin reemplazo parcial.

Son criterios pendientes, no evidencia ya ejecutada. En este paso se revisa diff
/whitespace documental; ultima suite integral 2234 passed (§58), no reejecutada.
Proximo paso: schemas y pruebas de contrato. M3-T1 EN PROGRESO integral, sin commit.


## 61. Schemas de resolucion EIPD y revision humana

2026-10-06. Implementados contratos de §60 en schemas/licitud.py: riesgos,
medidas, fuentes oficiales, consulta y EipdResolutionAssessmentV1 editable parcial.
EipdResolutionAssessmentStoredV1 separado agrega context_binding nullable;
binding v1 cerrado/hash SHA-256 hexadecimal. No incorporar esta forma interna
como entrada CREATE/PATCH en la futura integracion.

EipdResolutionReviewIn exige decision explicita, fundamento y referencia no
blancos; rechaza metadata del servidor. ReviewOut agrega UUIDs, hashes y fecha
UTC con zona; ReviewStateOut expone estado/ultimo evento como contrato de lectura.
Schemas no autentican al actor ni producen hashes/fechas: eso corresponde al
servicio futuro bajo lock. Tampoco calculan vigencia/decision ni persistencia.

Borradores aceptan parciales/negativos/pendientes y condicionales residuales;
completitud, IDs semanticos, cobertura y contradicciones pertenecen al evaluador
pendiente, sin rechazar borrador ni asumir aprobacion. Contratos cerrados anidados,
listas independientes, fechas factuales y enums explicitos; no_aplica rechazado.

111 pruebas nuevas: metadata no falsificable, enums/fechas/hash, cierre anidado,
listas/borradores, respuestas parciales, condicionales diferidos y JSON roundtrip.
231 focalizadas aprobadas; todos los schemas: 419 passed. Black/Ruff y diff
whitespace correctos. Ultima suite integral 2234 passed (§58), no reejecutada
para contratos aislados; no sumar parciales como evidencia de suite completa.

Sin integracion API/DB, migracion, evaluador ni habilitacion de gates. Fuentes
oficiales siguen pendientes; EN PROGRESO integral, sin commit. Proximo: asociacion
/hash de resolucion v1, preservando comparadores especiales v1-v10/EIPD v1-v11;
despues persistencia/eventos/RLS/API, matriz y gate segun §60.4.


## 62. Asociacion y hash de resolucion EIPD v1

2026-10-06. Nuevo servicio puro eipd_resolution.py, sin dependencias DB/API.
EipdResolutionContextV1 interno cerrado exige explicitamente snapshot RAT completo,
legal_basis y todos los documentos ordinarios/especiales, consentimiento incluido,
condiciones especiales y screening finales. Entradas nullable deben aportarse
explicitamente; no usar defaults que permitan omitir accidentalmente un expediente.
Contexto excluye resolucion/eventos y rechaza campos extra, evitando circularidad.

build_eipd_resolution_context_hash_v1 revalida material y genera SHA-256 de JSON
normalizado (claves ordenadas, UTF-8, nulls/defaults explicitos, listas preservadas)
con binding_version=1. Incluye tambien campos del snapshot fuera del hash RAT
canonico: ese hash RAT y comparadores especiales v1-v10/EIPD v1-v11 no cambian.

bind_eipd_resolution_v1 acepta solo documento editable y devuelve forma interna
con binding de servidor. Reaporte exige entrada editable explicita; documento
almacenado/binding aportado como entrada se rechaza. No reutiliza decision humana.
build_eipd_resolution_document_hash_v1 incluye documento completo y su binding,
rechaza metadata de revision; eipd_resolution_context_is_current_v1 compara sin
mutar/asociar. Sin binding devuelve false. Schemas invalidos lanzan ValidationError;
la futura integracion debera tratarlos sin convertirlos en aprobacion.

89 pruebas nuevas: alta/baja/modificacion de cada expediente, base ordinaria,
snapshot completo, todos los inputs obligatorios, modelos/JSON/defaults/orden de
claves, contenido propio separado de contexto, lectura sin escritura, metadata
ajena/circular rechazada y revalidacion de instancias/nested modificadas.
296 focalizadas aprobadas, incluyendo 96 asociaciones historicas de excepciones
y 111 schemas EIPD. Black/Ruff y whitespace correctos. Ultima suite integral
2234 passed (§58), no reejecutada para funciones puras aisladas; no sumar este
checkpoint como nueva suite integral ni extrapolar a concurrencia/API.

Pendiente consumir estos hashes desde persistencia/revision bajo lock con RAT
real. Ninguna revision/gate habilitada; fuentes oficiales pendientes.
Proximo: persistencia JSONB y eventos append-only con RLS desde migracion inicial;
despues exposicion documental/API, evaluador y revision segun §60.4.
M3-T1 EN PROGRESO integral, sin migracion nueva ni commit en este paso.


## 63. Persistencia de resolucion EIPD e historial protegido

2026-10-06. Migracion append-only b51d3f6a9c20 posterior a a40c2e5f8b19,
aplicada en PostgreSQL local. Alembic check sin operaciones nuevas.
LegalAssessment.eipd_resolution_assessment JSONB nullable/none_as_null=True,
CHECK objeto: null SQL admitido, null JSON/listas/escalares rechazados.
UQ adicional (id, organization_id) soporta FK compuesta del historial.

EipdResolutionReview persiste UUID, tenant/assessment, decision, fundamento,
referencia, hashes SHA-256, actor FK profiles y fecha timezone con clock_timestamp.
CHECKs para decision, textos no blancos (incluidos tab/newline) y hashes; indices
por tenant y orden historico assessment/created_at/id. No relaciones ORM que
eliminen eventos por cascade. FK a assessment/tenant y organization sin ON DELETE
CASCADE: no borrar el padre para eliminar indirectamente el historial.

RLS desde creacion: SELECT solo organizaciones autenticadas; INSERT ademas exige
actor del auth.uid() y assessment propio borrador con documento presente.
No politicas UPDATE/DELETE. Revocados UPDATE/DELETE/TRUNCATE de app_user y permisos
PUBLIC; solo SELECT/INSERT de runtime. Privilegios administrativos siguen disponibles
para mantenimiento autorizado, sin presentarlos como capacidad de usuario.
Limpieza de fixtures usa propietario exclusivamente para eventos de tenants de test,
antes de borrar organizaciones; sesiones runtime se revierten antes de limpiar.

36 pruebas PostgreSQL/app_user sin BYPASSRLS: aislamiento/lectura sin auth, insercion
valida, identidad suplantada/tenant/parent rechazados, documento/borrador requerido,
permisos reales, UPDATE/DELETE/TRUNCATE denegados, padre protegido, FK cross-tenant
incluso propietario, CHECKs/JSONB y fecha generada. Vaciar documento preserva evento.
No verifica contenido juridico, hashes contra RAT ni permisos/suscripcion de API;
estos controles corresponden a servicios futuros bajo lock, no al CHECK de tabla.

Regresion integral 2470 passed en 221.64 s (3:41), incluidas pruebas anteriores de
schemas/asociaciones. Black/Ruff/Alembic check/whitespace correctos. La suite completa
reemplaza el total anterior como evidencia de regresion, no acredita cierre integral.
No ampliar esta evidencia de persistencia a concurrencia/revision funcional futura.

Sin exposicion API/documental ni accion de revision: sigue pendiente binding final
con RAT actual, evaluador, estados derivados, permisos y relectura transaccional.
Gates/positivo EIPD se conservan; no confirmacion excepcional habilitada. Fuentes
oficiales pendientes. Proximo: CREATE/PATCH/GET documental de resolucion y binding,
con semantica omitir/preservar, null/vaciar, reemplazo entero, inmutabilidad de
confirmados/reemplazados y conservacion del historial; despues revision/evaluador.
M3-T1 EN PROGRESO integral; sin commit.


## 64. API documental de resolucion EIPD y asociacion final

2026-10-06. CREATE/PATCH reciben eipd_resolution_assessment nullable con contrato
editable EipdResolutionAssessmentV1; GET/salida devuelve forma interna con binding.
Hash/actor/decision/estado aportados dentro del documento se rechazan (422).
Sin endpoint de revision humana ni estados derivados de historial en este paso.

Servicio construye contexto con todos los expedientes y snapshot finales. Orden:
aplicar documentos/cambios y RAT; asociar especiales v10; asociar screening v11;
asociar resolucion v1. PATCH mantiene lock de serie y relectura populate_existing;
solo borrador editable. Omitir preserva documento/binding; null vacia JSONB como
NULL SQL; objeto sustituye entero y asocia explicitamente. Cambios en contexto
sin reaporte no actualizan binding. GET/readiness no asocian ni escriben.
No cambiar hashes RAT ni comparadores historicos. No generar/sobrescribir eventos.

Presencia de resolucion agrega barrera provisional compartida
resolucion_eipd_no_validada (409) en readiness/confirmacion, hasta evaluador/revision
funcionales. No altera motivos/positivo de screening ni habilita excepciones.
Retirar documento no elimina historial; ruta ordinaria preparada y sin EIPD requerida
conserva flujo previo. Confirmados/reemplazados rechazan cualquier PATCH.

25 escenarios HTTP nuevos con RAT real/PostgreSQL/app_user: documento parcial,
omision/null/reemplazo, historial previo intacto, lectura sin escritura, invalidacion
por alta/cambio/baja de todos los documentos, orden simultaneo y cambio RAT real,
reaporte explicito, metadata/enums/fechas cerrados, aislamiento por cabecera,
viewer y suscripcion suspendida. Seis bases ordinarias verifican igualdad de barrera
GET/POST y rechazo conservando borrador/vigente; retirar documento restaura ruta
ordinaria y reemplazo/inmutabilidad. No confirmar excepcion ni extrapolar concurrencia.

225 focalizadas aprobadas; regresion integral 2495 passed en 233.70 s (3:53).
Ajuste posterior exclusivamente de redaccion de mensaje al usuario: los 25 HTTP
revalidados (11.07 s). Black/Ruff/whitespace correctos; head local b51d3f6a9c20
sin migracion nueva. Este total no certifica cierre funcional integral.

Proximo: evaluador puro de completitud/aplicabilidad de resolucion segun §60;
despues readiness/vigencia, accion humana autenticada, concurrencia/relectura y
screening versionado/gate separado con fuentes verificadas antes de desbloqueo.
Fuentes y demas pendientes integrales permanecen abiertos. EN PROGRESO; sin commit.


## 65. Evaluador puro de preparacion documental EIPD

2026-10-06. Continua checkpoint local 6d9bb76. Implementado
evaluate_eipd_resolution_document_v1 en eipd_resolution.py para los bloques
documentales de §60.2: referencias/analisis, respuestas fundadas, evaluacion previa,
fechas, scope completo RAT, riesgos/medidas/evidencia, conclusion, fuentes/consulta
condicionales y binding. Fecha evaluated_on date explicita: sin reloj interno, DB,
LLM, comunicacion externa ni escritura. Revalida modelos/dicts y no reasocia.

Resultado inmutable con issues/applicability ordenados y deduplicados, context_current
y is_document_prepared. No can_confirm: completo expresa preparacion documental,
no revision humana ni autorizacion de tratamiento. Requiere_revision prevalece
sobre incompleto segun §60, preservando todos los motivos de ambas categorias.
Esto no cambia precedencia de otros evaluadores historicos ni sus comparadores.

Riesgos/medidas con IDs canonicos unicos, referencias no vacias/conocidas/unicas,
cobertura de todos los riesgos e implemented si fundada/evidencia propia.
Planes pendientes no son implementacion. Sin puntaje ni umbral juridico calculado;
alto conserva revision como frontera conservadora del producto. No inferir EIPD
previa por fecha de informe/evidencia. Fechas requeridas de informe y consulta de
fuentes no futuras; obtained_on sigue metadata factual opcional, sin regla nueva.

Scope coincide con categorias/grupos completos del snapshot, incluso no sensibles;
scopes de excepciones presentes deben estar contenidos, sin exigir igualdad de
alcances de distinta funcion. Completitud juridica propia de excepciones, rol/rutas,
controles ordinarios/especiales y frontera §59.1 son comprobaciones separadas,
aun pendientes de componer antes de gate/revision. No presentarlas como ejecutadas
por este evaluador documental; presencia de documento preparado no las supera.

Fuentes identificado exige publicacion/version documentada y aplicabilidad resuelta;
no_identificado permite busqueda documentada sin version ficticia de publicacion,
pero contradiccion con fuente declarada aplicable requiere revision. Ninguno de
estos estados acredita verificacion oficial global ni inexistencia de orientaciones.
Consulta no_solicitada exige analisis; referencias/respuestas residuales requieren
revision. En_curso mantiene revision y exige referencia/evidencia, con conclusion
residual marcada. Concluida exige referencias, recomendaciones/reassessment,
respuesta fundada y evidencia; no convierte recomendaciones en aprobacion.

159 pruebas nuevas: faltantes individuales, respuestas/evidencia por elemento,
riesgos/medidas/refs/duplicados semanticos, cobertura, prior assessment no inferido,
fechas explicitas, estados/condicionales de fuentes/consulta, scope RAT/subconjunto
de excepciones, binding ausente/obsoleto, todos los motivos/precedencia, orden
numerico, inmutabilidad, JSON/modelos y revalidacion. 455 focalizadas aprobadas,
incluidos contratos y asociaciones previas; Black/Ruff/whitespace correctos.
Ultima suite integral 2495 passed (§64), no reejecutada para evaluador puro aislado;
no sumar focalizadas como evidencia de una suite integral nueva.

Sin conexion API/readiness ni cambio de gates: resolucion_eipd_no_validada sigue
bloqueando, EIPD positivo y resto de controles se conservan. Fuentes pendientes.
Proximo: exposicion de preparacion documental en readiness y vigencia de revision
como resultados separados, usando contexto RAT actual; despues accion humana,
frontera versionada y concurrencia/aceptacion antes de habilitacion.
M3-T1 EN PROGRESO integral; sin migracion ni nuevo commit en este paso.


## 66. Readiness documental y vigencia de revision EIPD

2026-10-06. Readiness expone eipd_resolution (preparacion documental y
context_current) y eipd_resolution_review (sin_revision/vigente/obsoleta y ultimo
evento). Resultados separados de screening, decision humana y confirmacion.
Documento ausente se evalua cuando hay supuesto EIPD positivo; ruta ordinaria
sin documento conserva preparacion null y estado sin_revision.

El contexto se reconstruye desde RAT actual y documentos finales, sin modificar
snapshot, asociaciones ni historial. Contexto no disponible impide acreditar
vigencia. Ultimo evento tenant-aware por created_at descendente e id descendente:
no seleccionar una decision continuar anterior cuando existe otra posterior.
Vigencia requiere binding actual y coincidencia de hashes documental/contextual;
las tres decisiones conservan su contenido sin convertir vigencia en aprobacion.
Cambiar documento/contexto vuelve obsoleta la revision; reaportar al contexto
cambiado actualiza el documento, pero no renueva los hashes del evento anterior.

18 pruebas nuevas: diez puras y ocho HTTP con RAT/PostgreSQL real. Cubren las
tres decisiones, ausencia de documento/contexto/binding, hashes distintos,
cambios de consentimiento/especiales/screening/RAT, contexto no reconstruible,
reaporte, orden determinista con fecha empatada, aislamiento y GET sin escritura.
La confirmacion conserva resolucion_eipd_no_validada y el screening positivo;
no existe accion API para emitir revisiones ni nueva habilitacion de excepciones.

Validacion: suite completa 2672 passed en 237.06 s; Black/Ruff correctos.
Incluye las 159 pruebas del evaluador §65 y las 18 nuevas de este paso.

Proximo: frontera de revision y accion humana autenticada con controles vigentes,
fuentes oficiales y concurrencia, antes de habilitar confirmaciones. La preparacion
documental no acredita verificacion oficial global ni reemplaza controles propios.
M3-T1 EN PROGRESO, alcance integral; sin migracion ni nuevo commit.


## 67. Prerequisitos puros para registrar revision humana EIPD

2026-10-06. Implementado evaluate_eipd_resolution_review_prerequisites_v1,
con entrada ReviewIn cerrada/revalidada, estado, documento, contexto y fecha
explicita. Resultado inmutable conserva decision y todos los motivos; propiedad
prerequisites_met describe solo estos requisitos documentales, sin autorizacion,
confirmacion ni escritura. No sustituye permisos/suscripcion, tenant, bloqueo de
serie, relectura ni actor/fecha/hashes de servidor que debe resolver la accion API.

Cualquier decision exige borrador, documento presente y binding vigente frente
al contexto RAT actual disponible. Requiere_cambios/no_continuar permiten documento
parcial actual, incluso riesgo alto, para registrar una decision negativa concreta.
Esto no habilita tratamiento. Confirmado/reemplazado, documento ausente, binding
ausente/obsoleto o contexto no disponible conservan motivos de rechazo.

Continuar incorpora todos los motivos del evaluador documental y mantiene barreras
explicitas frontera_revision_no_validada y fuentes_oficiales_no_verificadas.
No hay bandera aportable por cliente para superar controles aun no implementados;
ni documento completo ni fuentes declaradas en su payload acreditan la verificacion
global de §59.6. Esta version no permite continuar. Componer/verificar controles
de frontera en una version posterior antes de habilitar esa decision.

38 pruebas nuevas cubren tres decisiones, parcialidad, riesgo alto, inmutabilidad,
ausencia/obsolescencia, estados no editables, metadatos falsificados y banderas de
aprobacion rechazadas, modelos revalidados, fecha explicita y estado desconocido.
215 focalizadas aprobadas, incluyendo evaluador documental y readiness HTTP previos;
Black/Ruff correctos. Ultima suite integral 2672 passed (§66); no reejecutada para
este servicio aislado y no sumar focalizadas como nueva evidencia integral.

Sin nueva ruta API, migracion, gate ni commit. Proximo: accion autenticada de revision
con edit_content/suscripcion, relectura bajo bloqueo de serie, hashes/actor/fecha de
servidor e historial append-only; conservar barreras de continuar de esta version.
Luego frontera verificada, fuentes y concurrencia antes de abrir confirmaciones.
M3-T1 EN PROGRESO, alcance integral.

Validacion de checkpoint §65–§67 previa al commit autorizado: suite completa
2710 passed en 238.18 s; Black/Ruff y diff --check correctos. M3-T1 EN PROGRESO.


## 68. Accion autenticada de revision humana EIPD

2026-10-06. POST /licitud/treatments/{treatment_id}/assessments/{assessment_id}/
eipd-resolution/reviews, respuesta 201 EipdResolutionReviewOut. Usa ReviewIn
cerrado, edit_content, suscripcion vigente y tenant validado en servidor.
Servicio record_eipd_resolution_review_v1 obtiene borrador/serie del tenant,
bloquea la misma serie que PATCH/confirmacion y relee populate_existing antes
de reconstruir RAT/contexto actual y aplicar prerequisitos §67. Versiones de
assessment/snapshot distintas de v1 y estados no borrador rechazan.

Actor/tenant/assessment/hashes resueltos en servidor; UUID y fecha de evento
asignados por PostgreSQL. Flush dentro de transaccion del caller; get_db confirma
al terminar o revierte ante error. Evento append-only sin modificar assessment,
serie, documento/binding ni eventos anteriores. Requiere_cambios/no_continuar
admiten parcial presente vigente; continuar sigue bloqueado por frontera/fuentes.
Revision no confirma ni reemplaza un confirmado. Sin nuevo GET de historial:
readiness existente muestra ultimo evento y vigencia, preservando historia en DB.

15 pruebas nuevas: dos decisiones negativas, hashes/identidad/fecha de servidor,
historial conservado, GET sin cambios, obsolescencia/revision nueva, confirmacion
bloqueada; ausencia/asociacion obsoleta/continuar rechazan sin evento; siete campos
falsificados 422; tenant equivocado 403, lookup 404, viewer 403 y suscripcion
suspendida 402; confirmado/reemplazado inmutables. Dos sesiones app_user con RAT
real prueban espera/relectura: borrar documento bajo lock y commit rechaza sin
escritura; rollback permite revisar documento original con sus hashes.

Validacion: 15 pruebas nuevas aprobadas; suite completa 2725 passed en 242.75 s.
Black/Ruff sobre los tres archivos Python modificados y diff --check correctos.

Proximo: frontera versionada de controles de primera ruta soportada y verificacion
oficial de fuentes, conservando screening positivo y barreras hasta aceptacion.
Concurrencia ampliada/cambios RAT y seis bases para gates siguen pendientes antes
de desbloquear. M3-T1 EN PROGRESO integral; sin migracion, nuevo commit ni push.


## 69. Registro de fuentes EIPD y pendiente temporal

2026-10-06. Creado m3-t1-eipd-fuentes.md con enlaces, versiones consultadas,
metodo/limites y resultados separados. Texto legal comprobado; publicacion concreta
de listas/orientaciones no verificada. Busqueda acotada no demuestra inexistencia.
Apertura de consolidado diferido incompleta se registra como tal, sin exagerar evidencia.
Anuncio ministerial de postergacion se conserva como propuesta: no cambia fecha
legal de producto sin ley publicada/comprobada ni certifica tramitacion exhaustiva.

Fuentes globales siguen pendientes; campos documentales del tenant no sustituyen
su verificacion. Barreras fuentes_oficiales_no_verificadas/frontera_revision_no_validada
y confirmacion conservadas. Proximo: matriz/contrato versionado de primera frontera,
que puede implementarse sin abrir continuar mientras las fuentes siguen pendientes.

Paso documental, diff --check correcto; ultima suite integral 2725 passed (§68),
no reejecutada por esta documentacion. Sin nuevo commit/push ni migracion.
M3-T1 EN PROGRESO integral.


## 70. Base normativa fija y contrato de primera frontera EIPD

### 70.1 Decision del proyecto

2026-10-06. Instruccion explicita del usuario: la ley de privacidad/proteccion de
datos es base normativa irrefutable del proyecto, independientemente de su entrada
en vigor en diciembre o eventual postergacion. Para M3 se mantiene el marco de
Ley 21.719/19.628 reformada ya adoptado. No agregar fecha de activacion, excepcion
transitoria ni desactivar controles por anuncio o postergacion. §69/F3 queda como
antecedente informativo, sin condicionar alcance o implementacion. No equivale a
certificar externamente el estado legislativo; es la decision normativa de producto.

Orientaciones/listas complementarias mantienen su pendiente de verificacion
separado. No cambian la certeza del marco adoptado ni impiden implementar controles
basados en el contrato aprobado; no marcar fuentes verificadas sin evidencia.

### 70.2 Contrato propuesto de preparacion de frontera

Servicio puro versionado separado de documento/revision/gate. Entrada interna:
contexto final EipdResolutionContextV1, revalidado incluyendo modelos modificados.
No aceptar de cliente resultados, flags de preparacion, verificacion o aprobacion.
Salida inmutable: result incompleto/requiere_revision/preparado, motivos por campo,
aplicabilidad y ruta sensible_derechos/sensible_biometrica_derechos/sin_resolver.
Sin can_confirm. Requiere_revision prevalece sobre incompleto, conservando todos
los motivos; orden estable y deduplicacion sin borrar preguntas positivas.

| Control | Exigencia de primera frontera | Si falta | Si contradice/sale del soporte |
| --- | --- | --- | --- |
| Contexto | RAT completo actual, rol responsable y alcance completo de su evaluacion | incompleto | otro rol requiere_revision |
| Deteccion especial | Regimen sensible; biometrico opcional, con sensible obligatorio; solo estos en primera ruta | regimen/condicion faltante incompleto | otros regimenes/coexistencias requieren_revision, sin declararlos ilicitos |
| Condicion sensible | sensibles_art16, excepcion_legal, defensa_derechos_art16d | incompleto | consentimiento/otra excepcion requiere_revision |
| Excepcion sensible | Evaluador propio completo y asociaciones especiales actuales | preservar todos los faltantes | preservar todos sus motivos de revision |
| Biometria presente | Excepcion legal de derechos art16ter/art16bis(d), expediente propio y dependencia sensible completos | incompleto | ruta distinta, inconsistencia o residualidad requiere_revision |
| Asociaciones | Comparadores especiales/EIPD vigentes admitidos segun versiones historicas; sin reasociar al leer | ausente incompleto | obsoleta requiere_revision |
| Screening | Cinco respuestas con fundamento; datos_protegidos_excepcion_consentimiento si, otras cuatro no | ausente/pendiente/fundamento faltante incompleto | otro positivo o contradiccion requiere_revision |
| Residuos | Ningun expediente especial fuera de ruta detectada; conservar comprobaciones transversales actuales | no inferir ausencia desde prosa | residuo requiere_revision |

La primera frontera no restringe por nombre de base ordinaria: las seis conservan
su evaluador independiente. Preparado describe ruta especial/screening solamente;
no reemplaza evaluador ordinario, resolucion preparada/no_alto, fuentes o revision.
Una condicion declarada no sustituye hechos RAT; no detectar ni comparar por prosa.
Sensibilidad/biometria y poblaciones se derivan con detectores existentes.

### 70.3 Deteccion versionada y futura composicion

Mantener evaluate_eipd_screening_v1 y sus motivos historicos. Nueva evaluacion v2
prevista reconoce excepcion preparada dentro de esta frontera sin borrar positivos:
requiere_eipd sigue explicitamente presente con motivos. No convertir en
sin_supuestos_declarados ni eliminar blockers de v1 por lista de codigos.
Compartir validaciones historicas mediante refactor probado o implementacion v2
explicita; revalidar contradicciones y bindings, con pruebas de equivalencia v1.

Orden futuro bajo lock: RAT actual, base ordinaria, especiales/frontera,
screening versionado, resolucion, fuentes verificadas, ultimo evento continuar con
ambos hashes actuales. GET y POST usaran reglas compartidas, sin GET mutador.
Revisiones negativas §68 siguen admitiendo parcial vigente; la frontera no se
convierte en requisito para registrar rechazo. Continuar aun no habilitado.

### 70.4 Aceptacion y siguiente paso

Proximo: implementar evaluador puro de frontera y pruebas propias antes de conexion
API/gates. Cubrir sensible sola y sensible+biometria; cada faltante/respuesta;
otros cuatro positivos; pendientes y fundamentos; rol; rutas mezcladas y residuos;
asociaciones obsoletas; dependencia sensible; precedencia/orden/inmutabilidad y
entradas cerradas. Fechas de vigencia legal no figuran como condicion del evaluador.
Despues screening v2 y composicion, fuentes y aceptacion seis bases/concurrencia
antes de habilitar continuar. Este paso cierra contrato, no implementacion funcional.

Ultima suite integral 2725 passed (§68), no reejecutada para documentacion.
Diff --check correcto. M3-T1 EN PROGRESO integral; sin commit/push ni migracion.


## 71. Evaluador puro de primera frontera EIPD

2026-10-06. Implementado evaluate_eipd_frontier_v1 en eipd_frontier.py sobre
EipdResolutionContextV1 interno cerrado/revalidado. Sin DB/reloj/LLM, fecha de
activacion legal ni flags de aprobacion. Resultado inmutable incompleto/
requiere_revision/preparado, ruta candidata, motivos/aplicabilidad y diagnosticos
especial/screening separados. is_frontier_prepared no implica can_confirm.

Reutiliza deteccion, validacion de expedientes especiales, dependencias sensibles/
biometricas y comparadores historicos. Conserva todos sus motivos, roles responsables,
ruta sensible defensa_derechos_art16d/excepcion_legal y biometria dependiente.
Otro regimen, ruta de consentimiento/otra regla, expediente fuera de frontera o
asociacion no vigente requiere revision. Ambas rutas admitidas segun §70.
Las seis bases ordinarias se asocian independientemente: su preparacion propia
se exige despues en composicion/gate; este evaluador no la certifica.

Exige cinco respuestas fundadas: excepcion protegida si y otras cuatro no.
Omitida/pendiente/fundamento ausente incompleto; otro positivo o negacion de
excepcion requiere revision. Precedencia de revision conserva todos los faltantes;
orden estable, deduplicacion e inmutabilidad. Ninguna reasociacion automatica.

Devuelve el screening v1 entero como diagnostico historico, incluidos positivo,
excepcion_especial_no_validada y pendiente_revision: no filtra blockers por codigo
ni cambia ese resultado. Preparado describe la nueva frontera acotada solamente.
Deteccion v2/composicion aun pendientes, sin sustituir v1 en API o confirmacion.
Fuentes/revision humana/documento EIPD y controles ordinarios son etapas separadas.

106 pruebas nuevas: ambas rutas, respuestas/fundamentos de cada pregunta,
faltantes, rol, dependencias, residuales, rutas mezcladas, seis bases ordinarias,
bindings obsoletos/historicos, precedencia/motivos, igualdad modelo/dict,
revalidacion de modelo mutado y rechazo de campos de aprobacion/fecha.
695 focalizadas aprobadas con excepciones sensible/biometrica, resolucion y
prerequisitos de revision; Black/Ruff/diff --check correctos. Ultima suite integral
2725 passed (§68), no reejecutada para nuevo servicio puro sin integracion;
no sumar focalizadas como evidencia de suite completa.

Proximo: deteccion EIPD v2 explicita para esta frontera, conservando motivos
positivos y compatibilidad historica; luego exposicion/composicion compartida y
fuentes/aceptacion antes de habilitar continuar. Base legal fija segun §70.
M3-T1 EN PROGRESO integral; sin cambio de gates, migracion, commit o push.


## 72. Deteccion EIPD v2 y nucleo historico compartido

2026-10-06. Implementado evaluate_eipd_screening_v2(context) puro en
eipd_screening_v2.py; contexto interno cerrado/revalidado. Calcula frontera §71,
no acepta flag de preparacion/approved/version desde cliente. Salida inmutable
EipdReadinessV2: resultados/motivos/observaciones/context_current de deteccion,
frontier y evaluation_version=2 separado de versiones documentales/bindings.

Refactor de evaluate_eipd_screening_v1 a wrapper con misma firma y nucleo privado
compartido. V1 siempre llama sin excepciones preparadas: comportamiento historico
conservado. Nucleo decide motivo durante evaluacion, sin filtrado posterior de
blockers. Comparadores v1-v11, contrato del cuestionario y hash RAT sin cambios.

Solo si frontera completa vigente: excepciones concretas pasan a motivo
excepcion_especial_preparada, categoria supuesto_declarado; la respuesta protegida
si y su motivo original permanecen, resultado requiere_eipd. No equivale a
sin_supuestos_declarados ni permite can_continue. Diagnostico v1 entero permanece
en frontier.screening, incluidos pendiente_revision/excepcion_especial_no_validada.

Fuera de frontera completa, v2 mantiene integro screening v1 con sus motivos,
observaciones y resultado: faltantes, otros positivos, rol, mezclas, residuos y
asociaciones obsoletas no obtienen preparacion. Ruta ordinaria negativa conserva
sin_supuestos_declarados; can_continue heredado expresa solo deteccion y nunca
confirmacion o aprobacion de la frontera. Preparacion de frontera no sustituye
controles ordinarios, resolucion, fuentes ni revision humana.

56 pruebas nuevas: ambas rutas preparadas, positivos historicos conservados,
modelo/dict e inmutabilidad, cada pregunta pendiente/opuesta/sin fundamento,
contextos invalidos, rol, bindings/residuos/coexistencia, campos falsificados,
contexto ausente y screening ordinario negativo. 161 focalizadas iniciales aprobadas
antes de agregar caso ordinario (55 v2 + 106 frontera); nueva suite integral incluye
ese caso adicional y toda regresion v1. Suite integral: 2887 passed en 243.26 s. Black/Ruff/diff --check correctos.

API/readiness/confirmacion siguen usando v1: en este paso no hay conexion de v2
ni habilitacion de continuar. Proximo: exponer frontera y deteccion v2 separadas
en readiness, con resultados/motivos versionados y positivos persistentes;
luego composicion compartida/fuentes/aceptacion antes de desbloqueo.
Ley como base fija, sin reloj normativo. M3-T1 EN PROGRESO integral;
sin migracion, nuevo commit ni push.


## 73. Readiness de deteccion EIPD v2 y frontera

2026-10-06. LegalAssessmentReadinessOut agrega eipd_v2 con contratos cerrados
EipdReadinessV2Out/EipdFrontierReadinessOut: evaluation_version=2, resultado,
context_current, motivos/observaciones y frontier (ruta/result/issues/applicability,
special y screening v1 como diagnosticos). Evaluacion versionada distinta de
schema/binding documental. Campo nullable con default para compatibilidad de
construccion del modelo; servicio readiness siempre calcula y aporta v2.

Usa el mismo contexto final de resolucion reconstruido desde RAT actual disponible,
no snapshot viejo si la finalidad/alcance no se puede recomponer. Contexto no
disponible mantiene deteccion pendiente, frontera incompleta y motivo explicito.
Preparacion v2 no depende de revision humana ni transforma EIPD positiva en negativa.
Resultado v1 root eipd y confirmation_blockers/pending_controls conservados; lectura
GET sin escritura, reasociacion, nuevo evento ni cambio de estado/confirmacion.

14 pruebas nuevas: diez de contrato (ambas rutas, version/extra/route/approval),
dos HTTP preparados sensible y sensible+biometrico con RAT/PostgreSQL real,
positivo/EIPD requerida, v1 entero visible y bloqueo/GET sin cambios. Actualizacion
incompleta de dependencia sensible invalida preparacion; otro HTTP prueba ruta
ordinaria negativa, tenant equivocado y cambio RAT sin reescribir snapshot.
Caso RAT no reconstruible por finalidad cambiada conserva pendiente/contexto falso
y motivo sin usar contexto almacenado como actual. Suite completa: 2901 passed en 247.30 s; Black/Ruff/diff --check correctos.

Siguiente: contrato/matriz de composicion compartida para decision humana y gate,
con ordinarios, especiales/frontera, deteccion v2, resolucion, fuentes y ultima
revision vigentes; avanzar sin habilitar continuar mientras faltan verificaciones.
Fuente normativa fija segun §70; fuentes complementarias siguen separadas.
M3-T1 EN PROGRESO integral; sin migracion, nuevo commit ni push.


## 74. Contrato de composicion compartida de controles EIPD

2026-10-06. Diseno del siguiente servicio puro, separado de permisos, transaccion,
documento editable y evento humano. Ley adoptada como base fija (§70), sin fecha
de activacion/postergacion en entrada ni logica. Alcance: primera frontera §70;
no ampliar otras rutas ni alterar confirmacion ordinaria sin excepcion EIPD.

### 74.1 Entrada interna cerrada

EipdControlCompositionInputV1 propuesto, revalidar modelos/dicts: organization_id y
assessment_id UUID; assessment_status LegalAssessmentStatus; assessment_schema_version
y rat_context_schema_version int (distintos de 1 generan motivo de revision);
justification str nullable; rat_context_current bool nullable obtenido por comparacion
de hash RAT actual/almacenado; context EipdResolutionContextV1 nullable reconstruido;
resolution EipdResolutionAssessmentStoredV1 nullable; latest_review
EipdResolutionReviewOut nullable seleccionado por fecha/id en el mismo tenant.
Fecha evaluated_on date explicita, separada de la fecha de vigencia legal.
No cliente puede aportar este contrato ni ready/approved/fuentes verificadas.

Contexto no reconstruible no se reemplaza por snapshot viejo. Bool RAT true no
suple contexto ausente ni asociaciones/documentos obsoletos. organization_id/
assessment_id del ultimo evento deben coincidir con entrada; discrepancia requiere
revision y no acredita revision actual aunque hashes coincidan. Autorizacion y
lookup tenant siguen siendo responsabilidad del servicio/DB, no de este contrato.

### 74.2 Matriz comun y composicion por finalidad

| Etapa | Exigencia | Resultado insuficiente |
| --- | --- | --- |
| Estado/version | Borrador; versiones assessment/RAT 1 | Estado inmutable/version no soportada: revision |
| Contexto RAT | Actual disponible, hash vigente, categorias/titulares no vacios; rol responsable para esta frontera | Ausente/desconocido: incompleto; obsoleto/otro rol: revision |
| Base/justificacion | Una de seis bases implementadas y justificacion no blanca | Ausente/faltante: incompleto |
| Preparacion ordinaria | Ejecutar evaluador propio de base con RAT actual: consentimiento, LIA, contrato, obligacion legal, derechos o economica | Preservar todos los motivos/aplicabilidad y precedencia propia; no aprobar base por nombre ni por excepcion especial |
| Especiales/frontera | Evaluador §71 preparado, comparadores y dependencias vigentes | Preservar todos sus motivos; otra ruta/residuo no se declara ilicito |
| Deteccion | §72 requiere_eipd, contexto vigente y primera frontera preparada; positivos visibles | Otros positivos/pendientes/contradicciones no superan frontera |
| Resolucion | Evaluador §65 preparado y binding actual, no_alto fundado, fuentes/consulta documentales completas | Preservar todos los motivos; completo no acredita verificacion global |
| Fuentes complementarias | Verificacion global trazable separada del documento tenant | En esta version: fuentes_oficiales_no_verificadas siempre pendiente |
| Revision para confirmar | Ultimo evento del expediente/tenant, vigente en ambos hashes, decision continuar | Ausente: incompleto; obsoleta/decision negativa/discrepancia: revision |

Preparacion ordinaria usa los evaluadores deterministas vigentes sin redefinir sus
comparadores/conclusiones; LIA mantiene condiciones propias de can_confirm.
No filtrar blockers de evaluate_transversal_readiness_v1 para simular aprobacion:
componer etapas explicitas, conservando v1 como diagnostico historico.

### 74.3 Salida y ausencia de circularidad

Resultado inmutable EipdControlCompositionV1 propuesto: preparation_result
incompleto/requiere_revision/preparado, ordinary (base/evaluador/motivos), frontier,
detection_v2, resolution, review_state y colecciones de motivos por etapa.
Precedencia comun requiere_revision sobre incompleto, sin cambiar resultados
individuales; ordenar por etapa/campo/codigo y conservar question_id.

Separar review_blockers de confirmation_blockers. review_blockers para registrar
continuar incluyen estado/contexto, ordinario, frontera/deteccion, resolucion y
fuentes; no requieren evento continuar previo. confirmation_blockers incluyen
esos mismos controles mas ultimo evento continuar vigente. Esto evita que crear
la primera revision positiva exija tener otra positiva anterior.
preparation_result excluye verificacion global y decision humana: preparado solo
expresa que los controles documentales comunes pasan. Ningun can_confirm ni
bandera de autorizacion; en esta version ambas colecciones mantienen fuente
complementaria pendiente y habilitacion no validada hasta aceptacion de gates.

Revision negativa conserva §67/§68: puede registrar rechazo sobre documento parcial
presente vigente en borrador, sin exigir preparacion ordinaria/composicion completa.
No convertir estos blockers comunes en requisito de rechazo. Inmutabilidad/hash/
actor/fecha de servidor y relectura bajo lock siguen exigidos para cualquier evento.

### 74.4 Integracion y aceptacion

Primer paso: implementar composicion pura y pruebas, sin conectar nuevos gates.
Despues exponer resultado orientativo en readiness, preservando historial y motivos
v1/v2. Accion de revision/confirmacion reconstruye misma entrada bajo lock de serie,
relee populate_existing y evalua antes de flush/reemplazo; caller maneja rollback.
GET sin escritura. Fuentes/aceptacion resueltas con evidencia antes de habilitar.

Pruebas previstas: seis bases y ambos alcances; cada etapa/faltante; estado/version;
RAT ausente/obsoleto; ordinario incompleto/revision; residuos/especiales; deteccion
positiva persistente; resolucion parcial/alto/fuentes/consulta; revision ausente,
negativa/obsoleta/otro tenant-expediente; hashes/ultima decision; no circularidad;
orden/todos los motivos/inmutabilidad/modelos revalidados. Luego HTTP/concurrencia
real, rollback, seis bases y conservacion del confirmado antes de gates habilitados.

Paso documental: ultima suite completa 2901 passed (§73), no reejecutada.
Diff --check correcto. M3-T1 EN PROGRESO integral; sin commit/push ni migracion.


## 75. Composicion pura de controles EIPD implementada

2026-10-06. compose_eipd_controls_v1 en eipd_controls.py implementa §74.
Entrada interna cerrada con tenant/assessment, estado/versiones, justificacion,
vigencia RAT/contexto actual, resolucion y ultimo evento; fecha date explicita.
StrictBool/StrictInt y revalidacion en modo python antes de JSON: evita que una
instancia mutada serialice True como version 1. Campos/fechas de aprobacion y
activacion normativa ajenos rechazados. Sin DB/reloj/LLM ni escrituras.

Composicion por estado/RAT, evaluador ordinario propio de seis bases, frontera,
deteccion v2 y resolucion. Resultados propios conservan motivos/aplicabilidad y
limites: no asumir base preparada por nombre. preparation_result documental
preparado/incompleto/requiere_revision con todos los motivos por etapa y
precedencia comun, sin cambiar precedencia interna de evaluadores existentes.

review_blockers comunes no exigen revision positiva anterior. confirmation_blockers
agregan ultimo evento humano, decision continuar y hashes vigentes. Evento de
otro tenant/assessment conserva motivo revision_otro_expediente y estado obsoleto,
aunque hashes coincidan. Estados/historia se copian a snapshots dataclass congelados
para salida inmutable, sin alterar evento persistido o input. Negativas no habilitan
confirmacion; su registro parcial sigue en servicio §67/§68, sin nuevos requisitos.

Fuentes/aceptacion pendientes permanecen como fuentes_oficiales_no_verificadas y
gate_eipd_no_habilitado en ambas colecciones. Preparado no es permiso ni can_confirm;
no cambia gates actuales ni conecta composicion a API. Frontera/deteccion mantienen
positivo EIPD y diagnostico v1 entero. Ley fija, sin fecha de activacion legal.

80 pruebas nuevas: ambas rutas, preparacion sin revision/no circularidad, tres
decisiones vigentes, hashes distintos/cambio documental, identidad de evento,
estado/version/justificacion/RAT/expediente ausentes, seis evaluadores ordinarios,
fallos de etapas/riesgo residual, entrada cerrada/tipos estrictos/modelo mutado,
fecha explicita, inmutabilidad de salida/revision, orden y todos los motivos.
468 focalizadas aprobadas incluyendo frontera/v2/resolucion/prerequisitos y HTTP
readiness/revision previos; Black/Ruff/diff --check correctos. Ultima suite integral
2901 passed (§73), no reejecutada para nuevo servicio puro sin integracion;
no sumar focalizadas como evidencia de una suite completa nueva.

Proximo: exponer composicion orientativa en readiness con campos de servidor,
ultimo evento del tenant y misma fecha/contexto de evaluacion. Despues integracion
bajo lock/fuentes/aceptacion antes de habilitar revision continuar o confirmacion.
M3-T1 EN PROGRESO integral; sin migracion, nuevo commit ni push.


## 76. Composicion de controles EIPD expuesta en readiness

2026-10-06. eipd_controls publica la composicion §75 con contrato cerrado y
version 1; detection_v2 conserva version 2. Separa preparation_issues,
review_blockers y confirmation_blockers, sin convertir preparado en permiso.
Se muestra ante expediente EIPD, deteccion positiva, excepcion propuesta o
historial existente; el flujo ordinario sin estos antecedentes devuelve null.

Usa identidad del servidor, contexto RAT actual, ultimo evento del mismo tenant
ya consultado y una unica fecha de evaluacion compartida con el diagnostico
documental. No agrega consultas de historial ni escrituras en GET. Documento
retirado conserva evento obsoleto; contexto RAT no reconstruible conserva los
motivos de falta de contexto. Diagnosticos existentes y bloqueos permanecen.

17 pruebas nuevas de contratos/HTTP: versiones y campos cerrados, resultados
consistentes, negativas sucesivas, retiro documental, contexto perdido, aislamiento
entre organizaciones, consultas repetidas sin cambios e historial conservado.
Suite completa: 2998 passed en 248.05 s, incluyendo las 80 pruebas puras de
§75 y las 17 nuevas de este paso. Black/Ruff y diff --check correctos.

Proximo: integrar composicion compartida bajo lock en revision positiva y
confirmacion, conservando barreras de fuentes complementarias/aceptacion.
Ley fija sin dependencia temporal. M3-T1 EN PROGRESO integral; continuar y
confirmacion excepcional bloqueados. Sin migracion, nuevo commit ni push.


## 77. Composicion compartida integrada bajo lock

2026-10-06. Readiness y operaciones mutadoras reutilizan el mismo constructor
interno de composicion y lector del ultimo evento, filtrado por tenant/assessment.
La salida cerrada se valida y serializa en modo JSON para los errores HTTP.
No recibe indicadores de habilitacion del cliente ni modifica hashes/documentos.

Revision continuar reconstruye RAT/contexto despues del lock de serie y relectura
populate_existing; calcula vigencia RAT real y comparte fecha con prerequisitos.
Rechaza antes de insertar cuando faltan prerequisitos o review_blockers, incluyendo
fuentes/aceptacion. Conserva codigo/issues previos y agrega eipd_controls. Negativas
mantienen prerequisitos parciales §67/§68 sin exigir composicion documental completa
ni evento positivo previo. Ultimo evento negativo no habilita confirmacion.

Confirmacion conserva orden de validadores ordinarios, vigencia RAT y motivos
transversales. Ante documento EIPD/deteccion positiva o pendiente/excepcion de
derechos, compone bajo el lock existente antes de consultar/reemplazar confirmado
o hacer flush. confirmation_blockers impiden escritura; error transversal conserva
codigo/diagnosticos previos y agrega eipd_controls. No elimina motivos v1 ni cambia
resultados ordinarios. Los rechazos previos de base/estado/RAT conservan precedencia.

Seis casos nuevos: cuatro HTTP comparan composicion del rechazo con readiness,
con/sin ultimo evento negativo, sin cambios en borrador/historial; dos amplian
concurrencia real app_user de revision positiva con retirada documental confirmada
o revertida. Al esperar se usa documento refrescado y la barrera permanece; no se
inserta evento. Casos negativos previos siguen probando insercion tras rollback.
Doble unitario de confirmacion declara ausencia de historial para la nueva lectura.
227 pruebas focalizadas aprobadas. Suite completa: 3004 passed en 253.18 s. Black/Ruff/diff --check correctos.

Proximo: ampliar concurrencia real de confirmacion y cobertura HTTP de seis bases
para esta composicion antes de resolver fuentes complementarias/aceptacion y
habilitar cualquier frontera. Ley como base fija sin dependencia temporal.
M3-T1 EN PROGRESO integral; continuar/confirmacion excepcional bloqueados.
Sin migracion, nuevo commit ni push.


## 78. HTTP seis bases y concurrencia real de confirmacion

2026-10-06. Ampliada matriz HTTP de resolucion EIPD: seis bases ordinarias con
expediente ordinario completo, con/sin ultimo evento negativo. Revision continuar
y confirmacion rechazan conservando composicion identica a readiness, motivos
previos, borrador, historial y confirmado anterior. review_blockers no exige evento
positivo previo. Tras retirar documento EIPD en flujo ordinario sin supuesto
positivo, se conserva confirmacion ordinaria y proteccion del confirmado.
Esta evidencia no certifica seis bases con excepciones protegidas: el escenario
es ordinario y algunas bases excluyen datos sensibles por sus propios controles.

Dos casos nuevos de concurrencia PostgreSQL/app_user, RAT real y lock de serie:
transaccion titular cambia referencia documental y registra decision no_continuar;
confirmacion en otra conexion tiene borrador precargado y espera lock real,
verificado mediante pg_blocking_pids. Tras commit relee documento/ultimo evento
vigente negativo; tras rollback usa documento original sin evento. Rechazos 409
antes de reemplazar confirmado, sin insertar eventos adicionales ni confirmar
borrador; diagnostico final coincide con GET y confirmado anterior intacto.

Ocho casos adicionales (seis combinaciones con evento previo y dos concurrencias),
mas verificaciones ampliadas en los seis casos existentes. 54 focalizadas aprobadas.
Suite completa: 3012 passed en 295.88 s. Black/Ruff/diff --check correctos.
Sin cambios de logica productiva en este paso, migracion, nuevo commit ni push.
M3-T1 EN PROGRESO integral; continuar/confirmacion excepcional bloqueados.
Ley como base normativa fija, sin condicion por fecha de entrada en vigor.

Proximo: revisar matriz de aceptacion de primera frontera EIPD y verificar fuentes
complementarias oficiales con registro de evidencia. No habilitar gates por el
numero de pruebas ni interpretar una busqueda sin resultados como inexistencia.


## 79. Revision de aceptacion de primera frontera y fuentes

2026-10-06. Revision documental/codigo en HEAD 792c935; no cambia gates.
Base normativa fija §70; fuentes complementarias revalidadas en registro §79/F4.
BCN art15ter y PDF Diario Oficial comprobados, sin instrumento complementario
especifico verificado. Busqueda acotada no demuestra inexistencia ni certifica
inventario de actos de Agencia. Riesgo no_alto y bloqueos globales son limites de
producto, no atribucion de aprobacion obligatoria de Agencia o prohibicion legal
general de riesgo alto. No usar campos editables del tenant como verificacion.

### Matriz de aceptacion acotada

| Criterio | Evidencia comprobada | Conclusion actual |
| --- | --- | --- |
| Sensible de derechos y sensible+biometrica, dependencias/rol/residuos | test_services_eipd_frontier.py, §71; test_api_eipd_v2_readiness.py, §73 | Preparacion especial probada; no autorizacion |
| Deteccion v2 positiva y diagnostico v1 integro | test_services_eipd_screening_v2.py y HTTP v2 | requiere_eipd preservado; gate v1 sigue bloqueando |
| Composicion documental preparada en ambas rutas | test_services_eipd_controls.py, prepared_controls, §75 | Evidencia pura; separacion documental/fuentes/revision |
| Resolucion y ultima decision vigente/obsoleta/negativa | servicios/pruebas §65-68 y composicion §75 | Evaluadores e historial probados; ninguna positiva aceptada actualmente |
| HTTP seis bases ordinarias y confirmado anterior | test_resolution_keeps_confirmation_blocked_six_bases, §78 | No acredita EIPD completa de rutas protegidas; economica conserva exclusion propia |
| Concurrencia revision/confirmacion app_user y RAT real | test_rereads_document_after_series_lock y test_confirmation_rereads_document_and_latest_review_under_real_lock, §77-78 | Documento parcial ordinario; commit/rollback y ultima negativa probados |
| HTTP de ambas rutas protegidas con ordinario/resolucion completos | Aun falta escenario combinado de preparation_result preparado y solo barreras globales | PENDIENTE; ampliar antes de aceptar frontera |
| Concurrencia de expediente protegido preparado/cambio de dependencia | No acreditada por las pruebas ordinarias anteriores | PENDIENTE; no extrapolar cobertura |
| Instrumento complementario de Agencia versionado/aplicable | Registro de fuentes §79: no verificado | PENDIENTE; conservar barrera |
| Habilitacion de revision positiva/confirmacion | §67 agrega frontera_revision_no_validada/fuentes; §75 agrega gate_eipd_no_habilitado; confirmacion conserva v1 | NO HABILITADA; retiro futuro requiere contrato/evidencia, sin filtrar codigos v1 |

Conclusion: primera frontera NO aceptada para habilitacion. Esto no deshace
implementacion/readiness probados; identifica pendientes diferentes del total de
pruebas. M3-T1 EN PROGRESO integral; no cierre DONE ni aprobacion juridica externa.

Proximo paso implementable independiente de publicaciones: HTTP de ambas rutas
protegidas con expediente ordinario/resolucion completos, usando RAT real y
confirmando preparation_result preparado sin habilitar continuar; luego cambio de
dependencia y concurrencia protegida. Conservar positivos, todos los motivos,
borrador/historial/confirmado y controles de base propia. No forzar seis bases
compatibles con sensibles si su evaluador propio lo excluye.

Paso documental: ultima suite integral 3012 passed en 295.88 s (§78), no
reejecutada. Diff --check correcto. Sin codigo, migracion, nuevo commit o push.


## 80. HTTP de ambas rutas protegidas con composicion preparada

2026-10-07. test_api_eipd_prepared_frontier.py agrega cuatro casos HTTP con RAT
real/PostgreSQL: sensible de derechos y sensible+biometrica de derechos, con/sin
ultima revision no_continuar. Base ordinaria contrato con expediente propio completo;
no extrapola a seis bases ni elimina restricciones economicas sobre sensibles.
Resolucion completa usa finalidad y alcance integral del snapshot real de M2,
se aporta por PATCH y recibe binding del servidor. Referencias de fuentes son
sinteticas de test y editables del tenant; no acreditan verificacion global.

Readiness acredita preparation_result preparado, cero preparation_issues,
ordinario/resolucion completos y contexto vigente. Deteccion v2 requiere_eipd;
diagnostico v1 pendiente_revision permanece integro. review_blockers contiene
exclusivamente fuentes_oficiales_no_verificadas y gate_eipd_no_habilitado: no exige
revision positiva previa. confirmation_blockers agrega revision ausente o ultima
decision negativa. POST continuar y confirmar rechazan 409 con la misma composicion,
sin modificar borrador/historial; GET repetido identico y tenant ajeno 403.

Retirar dependencia sensible invalida frontera/composicion, vuelve obsoleta
resolucion y, cuando existe, ultima revision humana; ambas acciones siguen
rechazadas y no crean eventos ni cambian borrador tras rechazo. No reescribe
asociaciones al consultar ni borra los antecedentes historicos.

Cuatro pruebas nuevas aprobadas. 89 pruebas HTTP focalizadas aprobadas en 34.89 s, incluyendo readiness v2,
composicion, documentos y revision previos. Black/Ruff/diff --check correctos.
Paso de pruebas/documentacion; sin cambios de logica productiva o migracion.
Ultima suite completa 3012 passed (§78), no reejecutada; no sumar pruebas focalizadas
como nueva evidencia integral. M3-T1 EN PROGRESO integral, primera frontera aun
no aceptada para habilitacion; fuentes complementarias pendientes §79.
Ley como base fija sin dependencia temporal. Sin nuevo commit ni push.

Proximo: concurrencia real de ambas rutas protegidas preparadas, cambiando
dependencia/documento bajo lock con commit/rollback; conservar relectura actual,
historial y rechazo antes de escritura. Luego completar aceptacion/fuentes.


## 81. Concurrencia real de ambas rutas protegidas preparadas

2026-10-07. Ocho casos nuevos en test_api_eipd_prepared_frontier.py:
sensible/sensible+biometrica x revision continuar/confirmacion x commit/rollback.
Fixture asincrona compartida construye via HTTP expediente ordinario contrato,
frontera y resolucion completos con RAT real; prepara ultima revision negativa
vigente por accion autenticada. No usa mocks del RAT ni del evaluador.

Dos conexiones runtime app_user con identidad autenticada y lock de serie real.
Transaccion titular retira dependencia sensible usando update_legal_assessment_draft_v1,
con contrato normalizado y flush real. Otra conexion precarga borrador y solicita
revision positiva/confirmacion; pg_blocking_pids acredita espera antes de liberar.
Tras commit se relee dependencia incompleta: preparacion/frontera no preparadas,
resolucion y revision obsoletas. Tras rollback se recupera composicion preparada
identica a readiness anterior, incluida ultima decision negativa vigente.

Ambas operaciones rechazan 409 en los ocho escenarios, conservan barreras globales
y mismo evento historico; no insertan nuevos eventos ni confirman borrador. GET
final coincide con diagnostico calculado tras lock. Resolucion almacenada permanece
intacta; rollback conserva borrador original completo y commit solo cambios de la
actualizacion autorizada. Expectativa documental usa normalizacion del schema,
no supone que input vacio persista literalmente como objeto vacio.

97 HTTP focalizadas aprobadas en 36.68 s incluyendo §§80, v2, composicion,
documentos y revision previos. Black/Ruff/diff --check correctos. Ultima suite
completa 3012 passed (§78), no reejecutada para este paso de pruebas; no sumar
focalizadas como nuevo total integral. No cambia logica productiva ni migraciones.

Pendiente tecnico de concurrencia preparada identificado en §79 cubierto para
ambas rutas con contrato ordinario y negativa previa. No extrapola a otras bases,
regimenes o confirmacion excepcional exitosa. No modifica fronteras ni retira
controles v1/§67/globales. M3-T1 EN PROGRESO integral; fuentes complementarias y
aceptacion final de habilitacion pendientes. Ley fija sin dependencia temporal.
Sin nuevo commit ni push.

Proximo: actualizar aceptacion con evidencia §§80-81 y delimitar contrato de
habilitacion del servidor, incluyendo transicion de diagnostico historico v1 sin
filtrado de codigos y verificacion complementaria auditable. Mantener bloqueos
mientras faltan fuentes/aceptacion; el alcance integral restante sigue pendiente.


## 82. Aceptacion actualizada y contrato de habilitacion del servidor

2026-10-07. HEAD revisado 91a71cd26ca3ab9e2960d0c4f1ffb3f28de973fc, limpio.
Paso de diseno/documentacion; no autoriza habilitacion ni afirma verificacion de
fuentes distinta de §79. Ley como base fija §70, sin fecha de activacion normativa.

### 82.1 Aceptacion de evidencia y pendientes

| Criterio §79 | Actualizacion comprobada | Alcance y pendiente |
| --- | --- | --- |
| HTTP protegido completo | §80: cuatro casos, dos rutas con/sin negativa; preparation_result preparado y solo barreras globales en review_blockers | Cubierto con contrato ordinario; no seis bases protegidas ni habilitacion |
| Concurrencia protegida preparada | §81: ocho casos, dos rutas x revision/confirmacion x commit/rollback, dos app_user y RAT real | Cubierto para retiro de dependencia sensible y ultima negativa; no cambio concurrente de politica ni confirmacion exitosa |
| Bases ordinarias y confirmado anterior | §78: seis bases ordinarias, rechazo conserva confirmado | No extrapolar a bases que excluyen sensibles |
| Instrumento complementario aplicable/versionado | §79 no verificado | PENDIENTE; busqueda acotada no acredita inexistencia |
| Decision versionada de habilitacion/compatibilidad | Controles actuales §67/§75 y transversal v1 incondicionales | PENDIENTE implementacion/pruebas; no retirar codigos por lista |
| Revision positiva y confirmacion exitosa | Ninguna autorizada por producto actual | PENDIENTE evidencia tecnica, fuentes y aceptacion explicita de frontera |

Se cierra el pendiente de evidencia HTTP/concurrencia preparada del escenario
acotado, no la aceptacion final de habilitacion. Ultima suite integral 3012 passed
§78; §§80-81: 97 HTTP focalizadas, no nuevo total integral. M3-T1 EN PROGRESO.

### 82.2 Contrato interno propuesto EipdGatePolicyV1

Entrada exclusivamente del servidor, cerrada/revalidada e inmutable tras evaluar.
No forma parte de Create/PATCH/ReviewIn; rechazar campos approved/can_confirm,
policy, flags de fuentes/aceptacion y fechas de activacion enviados por cliente.
Resolver inicialmente devuelve politica deshabilitada; ninguna variable de entorno
booleana, texto del tenant, fecha legal o busqueda sin resultados la habilita.

Campos requeridos (nullable explicitos donde corresponda):

- policy_version: StrictInt literal 1; policy_reference: identificador de revision
  controlada del servidor, no referencia libre de usuario.
- routes: conjunto cerrado de sensible_derechos/sensible_biometrica_derechos,
  sin rutas repetidas; no habilitacion global de excepciones por comodin.
- sources_status: pendiente/verificadas; source_records: instrumentos con emisor,
  referencia/URL primaria, version/fecha y analisis de aplicabilidad a cada ruta,
  junto a evidencia de verificacion y responsable del registro del servidor.
- acceptance_status: pendiente/aceptada; acceptance_reference y validation_commit:
  evidencia de revision tecnica de esta frontera/version, no total de pruebas solo.
- activation: deshabilitada/habilitada; cambios versionados/auditables de politica.

Combinaciones contradictorias o incompletas son errores de contrato, nunca permiso.
Fuentes verificadas exige instrumentos y trazabilidad comprobados del servidor;
aceptada exige referencia/commit/evidencia para las rutas seleccionadas. Habilitada
exige ambas condiciones y al menos una ruta. Pendiente/deshabilitada es valido y
conserva barreras. No inventar instrumento ni declarar verificadas por ausencia
inferida de busqueda. No incorporar en este contrato una obligacion legal general
de aprobacion de Agencia: consulta y limites de riesgo mantienen contrato §59/§65.

Hash canonico policy_hash cubre version/referencia, rutas, fuentes/aplicabilidad,
aceptacion y activation; calcular del objeto validado en servidor. Cualquier cambio
relevante produce otra identidad de politica. La evidencia real se registra/revisa
antes de aceptar fuentes, no se acredita porque un objeto interno diga verificadas.

### 82.3 Composicion y decision versionadas, sin circularidad

Nueva composicion v2 prevista recibe contexto §74 y politica interna explicita;
v1 y todos los bindings documentales/RAT conservan contratos actuales. Diagnostico
v1 entero permanece visible. Version de politica (1), composicion/gate (2), deteccion
(2) y bindings actuales son conceptos distintos; no aceptar version desde cliente.

Motivos documentales/frontier/ordinarios se calculan aun con politica deshabilitada.
Etapa sources depende de evidencia de politica; activation exige ruta incluida y
aceptacion/habilitacion. Resultado documental preparado sigue sin otorgar permiso.
review_blockers nunca exige ultima revision positiva; negativas siguen contrato
parcial §67/§68. confirmation_blockers agrega ultima continuar vigente, misma
organizacion/assessment y hashes documento/contexto/politica actuales.

Prerrequisitos de revision positivos v2 componen controles en vez de sumar barreras
fijas §67 despues de composicion habilitada. V1 conserva su comportamiento entero.
Sin politica resuelta/valida, ruta fuera de alcance, fuentes o aceptacion pendientes:
continuar y confirmacion excepcional siguen rechazados. Faltantes/revision se
reportan por etapa, sin ocultar positivos ni convertir requiere_eipd en negativo.

### 82.4 Transicion de controles transversales

Confirmacion v2 futura debe construir decision semantica propia compartiendo los
validadores actuales: base ordinaria, rol/RAT/vigencia, especiales, dependencias,
residuos, deteccion v2, resolucion, politica y revision. No llamar v1 y sustraer
screening_eipd_no_preparado/resolucion_eipd_no_validada u otros codigos. No reutilizar
un can_continue de deteccion como permiso de confirmacion. Motivos historicos v1
quedan como diagnostico con version explicita, separados de decision activa v2.

Fuera de primera frontera/politica habilitada, conservar el rechazo ordinario y
transversal correspondiente, incluidas rutas mixtas, otros positivos, contextos
incompletos y bases incompatibles. Antes de conectar decision activa: pruebas de
equivalencia del flujo ordinario y de cada rechazo historico, no solo caso feliz.
GET consulta sin escribir/reescribir bindings, mismas entradas que operaciones.

### 82.5 Vigencia humana y atomicidad de politica

Revision positiva futura registra tambien policy_reference/version/hash actuales
como metadatos de servidor. Requiere contrato/persistencia append-only nuevo y
migracion propia antes de conexion: no reescribir eventos ni migraciones antiguas.
Eventos negativos existentes permanecen legibles. Evento positivo sin identidad
de politica no acredita gate v2 aunque documento/contexto coincidan; una nueva
politica requiere nueva revision humana, no promover evento viejo automaticamente.

Bajo lock de serie: releer borrador/RAT/ultimo evento y resolver politica actual
antes de insertar/reemplazar/flush. Politica debe permanecer estable hasta commit:
si es artefacto inmutable del proceso, impedir cambio durante transaccion; si se
persiste, adoptar revision/lock compatible con actualizacion de politica y probar
concurrencia/revocacion. No basta comparar un hash antes de esperar lock. Caller
maneja rollback. No introducir segundo orden de locks sin diseño de no-deadlock.

### 82.6 Implementacion secuenciada y validacion

Siguiente paso: schema/evaluador puro de politica y composicion v2, sin resolver
habilitada en produccion ni migracion/API/gates nuevos. Pruebas: cierres/StrictInt,
modelos mutados, rutas/dependencias, estados contradictorios, trazabilidad ausente,
hash estable/sensible a cambios, fuentes pendientes, habilitacion limitada a ruta,
revision ausente/negativa/politica vieja y cero circularidad. Mantener v1 sin cambios.

Luego persistencia de metadatos de politica en eventos y resolver/auditoria;
prerrequisitos/decision transversal v2 compartidos; HTTP/concurrencia real de cambio
de politica y dependencias, confirmado previo, tenant/roles/suscripcion y hashes.
Resolver real queda deshabilitado mientras fuentes/aceptacion faltan. Cubrir exitos
con politica sintetica de test no autoriza habilitar politica real. Ultima suite
completa y revision tecnica requeridas antes de cualquier habilitacion efectiva.

Paso documental, diff --check correcto; no reejecutar pruebas por diseno sin codigo.
Sin migracion, nuevo commit ni push; frontera no habilitada y M3-T1 EN PROGRESO integral.


## 83. Politica pura y composicion v2 implementadas

2026-10-07. eipd_policy.py implementa EipdGatePolicyV1, SourceRecordV1 y
EipdReviewPolicyIdentityV1 exclusivos del servidor; no se agregan a API/input del
tenant ni se implementa resolver real. Schema cerrado, StrictInt version 1 y
revalidate_instances always en politica/fuentes/identidad; normaliza textos y exige
referencias, URL HTTP(S), fecha/version, cobertura de rutas, responsables y evidencia.
URL valida no acredita emisor/autenticidad: verificacion real pendiente en resolver.

Rechaza rutas/instrumentos duplicados, rutas desconocidas, habilitacion sin rutas,
fuentes verificadas sin instrumentos/cobertura y aceptacion sin referencia, commit
Git completo, evidencia/responsable. Fuentes pendientes/aceptacion pendiente y
activacion deshabilitada siguen estados validos. No introduce fecha de vigencia
legal; fecha explicita date permite detectar publicaciones futuras, sin reloj interno.

build_eipd_policy_hash_v1 SHA256 canonico de todos los datos validados, ordenando
rutas/instrumentos y rutas de aplicabilidad; cambios de evidencia/aceptacion/emisor
responsable/activacion producen otra identidad. evaluate_eipd_policy_v1 devuelve
snapshot congelado y motivos sources/activation ordenados/deduplicados. Politica
None conserva fuentes/gate pendientes y politica_no_disponible; ruta fuera de
politica no queda habilitada. Politicas sinteticas de test no autorizan el producto.

EipdControlCompositionInputV2 agrega assessment v1, politica nullable explicita y
ultima identidad humana nullable; identidad sin evento rechazada. Salida congelada
EipdControlCompositionV2 version 2 agrega politica y review_policy_status, separado
de review_state documental. Mismo nucleo privado compone documentacion y etapas
para v1/v2; v1 mantiene barreras constantes sin cambio de firma/resultados.
V2 calcula etapas de politica durante evaluacion, sin filtrar motivos de v1.

review_blockers no exige evento humano previo. confirmation_blockers agrega
identidad de politica de ultimo evento: id de evento, version, referencia y hash
actuales; sin identidad/otra revision/hash previo bloquean. Vigencia documental
se conserva separada: politica coincidente no elimina obsolescencia del documento,
contexto, otro tenant/assessment ni decision negativa. Deteccion requiere_eipd y
screening v1 entero permanecen. Sin can_confirm ni permiso externo de evaluadores.

104 pruebas nuevas: estados/campos/tipos/cobertura/tipos URL, hashes canonicos y
cambios relevantes, rutas limitadas, politica ausente/deshabilitada/futura, fecha
explicita, entradas/ReviewIn cerrados, ambas rutas preparadas sin circularidad,
tres decisiones, politica anterior/otro evento/documento/tenant, faltantes comunes,
inmutabilidad y modelos anidados modificados revalidados. Se corrigio durante
pruebas la aceptacion por defecto de instancia anidada ya validada pero mutada;
revalidacion always evita confiar en ese estado. No se altera modelo cliente v1.
184 pruebas puras aprobadas (104 nuevas + 80 composicion v1). Suite completa: 3128 passed en 276.34 s, incluyendo §§80-81 y nuevas pruebas
de politica; Black/Ruff/diff --check correctos.

API/readiness/acciones/confirmacion siguen en v1 y barreras actuales. Sin persistir
metadatos ni activar resolver/gate v2. Fuentes complementarias/aceptacion pendientes;
M3-T1 EN PROGRESO integral y ley fija. Sin migracion, nuevo commit ni push.
Proximo: contrato/persistencia append-only de identidad de politica en eventos,
compatibilidad con historicos y RLS antes de resolver/auditoria/accion v2. Politica
real permanece deshabilitada mientras faltan fuentes/aceptacion y evidencia final.


## 84. Identidad de politica persistible en eventos EIPD

2026-10-07. Nueva migracion append-only c62e407bad31 sobre b51d3f6a9c20;
EipdResolutionReview incorpora policy_version Integer, policy_reference Text y
policy_hash Text, todos nullable y sin defaults/backfill. Restriccion CHECK exige
los tres NULL para historia sin identidad, o todos NOT NULL con version 1,
referencia no vacia y hash hexadecimal minusculo de 64 caracteres. NOT NULL
explicitos en rama completa impiden aceptar identidad parcial por logica SQL NULL.
Convencion de nombres del repo se conserva, incluido nombre generado/truncado;
pruebas identifican el constraint real desde catalogo PostgreSQL.

No modifica RLS SELECT/INSERT, FK compuesta tenant/assessment, actor autenticado,
requisito de borrador/documento, ni prohibicion UPDATE/DELETE/TRUNCATE app_user.
Eventos antiguos no se reescriben ni reciben una politica supuesta. Continuar
historico sin identidad sigue legible y no acredita composicion v2. No se exige
identidad a negativas antiguas ni se inventa autorizacion para nuevos positivos.

EipdResolutionReviewWithPolicyOut agrega lectura cerrada/nullable con version
estricta y coherencia de los tres campos, heredando UTC y metadatos de servidor.
No sustituye respuesta API v1 en este paso. ReviewIn sigue rechazando los tres
campos; caller no puede aportar hashes/version/referencia de politica.

build_eipd_review_policy_metadata_v1 calcula campos desde politica interna validada;
no autoriza insercion positiva ni verifica fuente externa. derive_eipd_review_policy_identity_v1
mapea id del evento persistido junto a identidad validada; historicos todos NULL
producen None. Metadatos parciales, version/hash invalidos o identidad sin id se rechazan, sin
promover revisiones viejas a politica actual. No resolver habilitado ni conexion de
acciones v2; POST actual conserva barreras y eventos sin identidad.

35 pruebas nuevas: insercion/lectura runtime con identidad, legacy intacto y mapper,
12 parciales/formatos invalidos rechazados por CHECK real, spoof tenant/actor/parent/
sin auth rechazado por RLS, UPDATE de identidad prohibido, tres decisiones legacy
sin promocion, salida cerrada/tipos estrictos, ReviewIn rechaza metadatos y mapper
rechaza identidad incompleta. 71 pruebas de persistencia/contratos aprobadas,
incluyendo 36 anteriores. Alembic check: No new upgrade operations detected.
Migracion aplicada localmente; comparacion de contenido anterior a/post upgrade
sobre 0 eventos existentes (no constituye prueba de conversion de historial poblado).
Fixtures de eventos sin politica verifican compatibilidad nullable y lectura.
Suite completa: 3163 passed en 277.43 s; Black/Ruff/diff --check correctos.

Proximo: resolver de servidor deshabilitado y lectura de composicion/identidad v2,
antes de auditoria/politica real y acciones v2. Habilitacion efectiva aun requiere
fuentes complementarias/aceptacion, decision transversal v2 sin filtrar v1 y
concurrencia de politica. Ley fija; M3-T1 EN PROGRESO integral; gates bloqueados.
Sin nuevo commit ni push; ninguna migracion historica reescrita o downgrade ejecutado.


## 85. Resolver deshabilitado y lectura de composicion v2

2026-10-07. resolve_eipd_gate_policy_v1 devuelve instancia nueva/revalidada de
artefacto fijo m3-t1-eipd-deshabilitada-v1, version 1, ambas rutas delimitadas,
fuentes/aceptacion pendientes, sin instrumentos/evidencia supuestos y activacion
deshabilitada. Sin parametro de cliente, flags/env, reloj normativo, red o DB;
no acredita auditoria de politicas habilitadas ni permite cambios de politica en
produccion. Una instancia mutada no altera la siguiente resolucion.

LegalAssessmentReadinessOut agrega eipd_controls_v2 nullable junto a v1 conservado.
Salida cerrada/version 2 incluye policy, review_policy_status y latest_review_policy
nullable (id del evento + version/referencia/hash). Policy snapshot valida identidad
completa, estados de activacion coherentes y rutas sin duplicados; tipos/versiones
estrictos, campos extra rechazados. Deteccion anidada version 2 y politica version 1
permanecen conceptos separados. No incluye can_confirm ni permiso de tratamiento.

Readiness construye ambas composiciones con mismo contexto RAT actual, vigencia,
fecha explicita y ultimo evento. Constructor de entrada comun evita drift. Consulta
unica de historial obtiene payload legacy e identidad desde la misma fila filtrada
por tenant/assessment y ordenada created_at/id; acciones v1 reutilizan wrapper legacy.
No busca evento anterior si ultimo carece de politica o es negativo. Ambito de
exposicion igual a §76: EIPD/documento/excepcion/historia; flujo ordinario sin estos
antecedentes mantiene ambas composiciones null.

GET no escribe ni reasocia; retirar documento conserva historial y separa vigencia
documental obsoleta de identidad de politica coincidente/anterior. Politica vigente
no elimina negativa ni bloqueos globales. Metadatos guardados no verifican fuentes
reales; datos editables del tenant tampoco. Root v1/confirmation_blockers permanecen
intactos y POST continuar/confirmar siguen rechazados por reglas v1. No conecta
composicion v2 a autorizacion o accion mutadora, ni activa gates por politica de test.

26 pruebas nuevas: resolver fijo/instancias independientes/env ignorada, contratos
cerrados y versiones/coherencia (ambas rutas), HTTP preparado con una sola consulta
real de historial, GET repetido/parametros ignorados, aislamiento tenant, acciones
bloqueadas y borrador/historial intactos. Historia positiva se crea solo como fixture:
sin identidad/current/anterior; politica actual deshabilitada impide usarla para
confirmar. Retiro documental conserva identidad/evento; ultima negativa legacy
prevalece sobre positiva anterior con identidad. Flujo ordinario null verificado.
26 pruebas aprobadas; 29 HTTP previas aprobadas en validacion inicial.
Suite completa: 3189 passed en 279.29 s; Black/Ruff/diff --check correctos.

Proximo: prerequisitos puros versionados v2 de revision, separando negativos
parciales de positivos con composicion/politica actual; luego accion y decision
transversal v2 sin filtrar codigos v1, auditoria/politica real y concurrencia de
politica antes de habilitar. Fuentes complementarias/aceptacion siguen pendientes.
Ley fija; M3-T1 EN PROGRESO integral. Sin nueva migracion, commit ni push.


## §86 — Prerrequisitos puros de revision EIPD v2

2026-10-07. eipd_review_v2 implementa evaluador puro versionado con entrada
interna cerrada y revalidacion de modelos anidados mutados. Resultado inmutable:
decision, motivos ordenados/deduplicados y composicion opcional. Sin DB, permisos,
accion, resolver activo ni can_confirm.

Nucleo parcial compartido con v1 valida fecha explicita, request cerrado, borrador,
documento/contexto presentes y asociacion vigente. V1 conserva motivos, orden y
bloqueos fijos de positivos. requiere_cambios/no_continuar usan estos requisitos
parciales y no ejecutan composicion completa: faltantes ordinarios/documentales,
alto riesgo o politica deshabilitada no impiden registrar una negativa valida.

continuar compone v2 y conserva todos sus review_blockers, incluida politica,
fuentes, aceptacion, ruta, versiones y preparacion documental. No usa
confirmation_blockers ni exige revision positiva anterior: evita circularidad;
una negativa anterior o identidad de politica obsoleta no sustituye ni impide
por si sola la nueva revision. Confirmacion conserva sus controles propios.

110 pruebas nuevas cubren ambas rutas, negativos parciales, condiciones comunes,
positivos incompletos/deshabilitados, politica sintetica preparada, ausencia de
revision previa, historia negativa/obsoleta, contratos cerrados/modelos mutados,
fecha explicita e inmutabilidad. 148 pruebas focalizadas aprobadas, incluidas 38
v1; suite completa 3299 passed en 281.10 s. Black/Ruff/diff --check correctos.
Politica sintetica preparada solo prueba el evaluador; no activa producto real.

Proximo: integrar revision autenticada v2 con relectura bajo lock y politica
exclusiva de servidor deshabilitada, preservando negativos y metadatos; despues
decision transversal v2, auditoria/politica real y concurrencia de politica.
Fuentes complementarias/aceptacion pendientes; acciones/gates reales siguen v1
bloqueados en este paso. Ley fija; M3-T1 EN PROGRESO integral.
Sin nueva migracion, commit ni push.


## §87 — Revision autenticada con prerrequisitos v2 y politica de servidor

2026-10-07. La accion existente record_eipd_resolution_review_v1 conserva endpoint,
autenticacion/permiso edit_content, suscripcion, tenant y transaccion; usa ahora
prerrequisitos v2 para decidir. Bajo FOR UPDATE de serie relee borrador/versiones,
contexto actual desde M2 y documento antes de resolver politica fija deshabilitada.
Una consulta obtiene ultimo evento e identidad; fecha explicita comun. Los controles
v1 permanecen diagnosticos sin filtrar sus codigos; no determinan la nueva decision.

Negativas conservan requisitos parciales y pueden registrarse aun con documentos
incompletos o politica deshabilitada. Eventos nuevos guardan version/referencia/hash
de politica desde el servidor, junto a actor y hashes documentales existentes.
Identidad vigente no convierte una negativa en aprobacion ni habilita confirmacion.
Eventos historicos sin politica permanecen sin identidad; no backfill ni fallback.
Salida publica de evento conserva contrato previo; readiness expone su identidad v2.

continuar exige review_blockers v2 y sigue rechazado por fuentes/aceptacion pendientes
y activacion deshabilitada. Error 409 conserva issues/eipd_controls legacy y agrega
evaluation_version 2, issues_v2 y eipd_controls_v2. No exige positiva previa y no
escribe evento/documento al rechazar. Confirmacion y decision transversal siguen v1.
Cliente no aporta politica ni activa servidor mediante query o payload.

Diez pruebas HTTP nuevas: negativas parciales con identidad/actor de servidor,
ambas rutas preparadas con/sin negativa previa, composicion identica a readiness,
una consulta de historial, preservacion y cuatro rechazos de politica de cliente.
Prueba historica legacy conserva evento negativo sin identidad mediante fixture;
concurrencia real preparada ampliada con contexto/ultimo evento/identidad v2 tras
commit o rollback. 71 focalizadas aprobadas antes de ampliar aserciones concurrentes.
Suite completa: 3309 passed en 290.08 s, incluidas las aserciones concurrentes
ampliadas. Black/Ruff/diff --check correctos.

Proximo: decision transversal/confirmacion v2 bajo lock sin filtrar reglas v1;
auditoria/politica real, exitos y concurrencia de politica antes de habilitar.
Fuentes complementarias/aceptacion siguen pendientes. Ley fija; M3-T1 EN PROGRESO
integral. Sin nueva migracion, commit ni push.


## §88 — Decision transversal de confirmacion v2 bajo lock

2026-10-07. confirm_legal_assessment_v1 conserva endpoint/permisos/suscripcion,
FOR UPDATE de serie, relectura del borrador/versiones, justificacion, alcance,
vigencia RAT y validadores propios de las seis bases ordinarias. Antes de consultar
o reemplazar confirmado previo obtiene ultimo evento/identidad en una consulta y
construye composiciones v1/v2 con mismo contexto actual y fecha explicita.

Dentro del ambito EIPD (resolucion actual, detector positivo/revision o excepciones
de derechos), confirmation_blockers de v2 determinan la
decision. La composicion valida la frontera delimitada y rechaza las restantes;
no borra ni filtra codigos v1. Fuera de ese ambito las barreras transversales v1
siguen decidiendo. Validadores ordinarios y contexto RAT se ejecutan antes del gate.
Diagnosticos legacy special/eipd/confirmation_blockers/eipd_controls permanecen;
error agrega evaluation_version 2 y eipd_controls_v2. Politica exclusivamente del
resolver fijo deshabilitado; query del cliente no activa gates.

Identidad vigente por si sola no acredita decision positiva ni documentacion actual.
Eventos positivos historicos con identidad actual/anterior o sin identidad no
superan fuentes/aceptacion/activacion pendientes. Negativas conservan decision;
retirar documento mantiene historial y readiness v2 obsoleta/incompleta. El historial
por si solo no amplia el gate ordinario cuando no hay supuestos EIPD actuales.
Rechazo ocurre antes de escrituras/reemplazo del confirmado previo; sin migracion.

Once pruebas HTTP nuevas cubren ambas rutas y cinco historias (ausente, positiva
legacy, positiva con politica actual/anterior y negativa), coincidencia con readiness,
una consulta, query ignorada y preservacion de borrador/historial; caso ordinario
con historial y sin documento confirma sin ampliar el gate. La suite inicial
detecto seis regresiones de ese alcance y se corrigieron conservando el flujo previo. Concurrencia real preparada amplia aserciones v2 tambien
para confirmar tras commit/rollback, manteniendo confirmado previo y negativa.
61 pruebas previas aprobadas; 23 focalizadas posteriores aprobadas, once nuevas.
Tras corregir alcance/fixture: 54 focalizadas aprobadas. Suite completa final:
3320 passed en 287.70 s; Black/Ruff/diff --check correctos.

Proximo: contrato/auditoria de politica real y atomicidad de cambios de politica,
con evidencia de fuentes complementarias y aceptacion antes de habilitar. Resolver
continua deshabilitado; exitos de frontera habilitada y concurrencia de politica
siguen pendientes. Ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §89 — Contrato de auditoria y seleccion transaccional de politica real

2026-10-07. Contrato detallado en m3-t1-eipd-politica-auditoria.md (DISENO).
Publicaciones inmutables con referencia unica/hash de servidor; selector global
revisionado y eventos append-only atomicos. Schema version 1 distinto de revision
del selector; publicar no selecciona. Reseleccion/revocacion requieren nueva
publicacion/referencia, sin promover revisiones historicas ni seleccionar vieja
politica habilitada. Canal administrativo separado del runtime/tenant.

Orden futuro selector FOR SHARE -> serie FOR UPDATE -> relecturas; seleccion usa
FOR UPDATE del selector sin locks de serie. Politica permanece estable hasta
commit/rollback. Requiere modificar uniformemente el orden actual antes de conectar
resolver real; §87/88 todavia usan artefacto fijo y lock de serie solamente.
Readiness orientativo coherente; integridad desconocida falla cerrado en ambito EIPD.
Historia sola no amplia gate ordinario. Negativas parciales admitidas con politica
valida deshabilitada, sin inventar identidad ante corrupcion del resolver.

Evidencia append-only de confirmacion excepcional futura asocia tenant/assessment,
evento humano, publicacion/revision/seleccion y hashes, atomicamente con reemplazo;
requiere contrato/migracion y RLS propios antes de habilitar exitos. Revocacion
conserva evidencia historica y bloquea acciones nuevas, sin mutar confirmados previos.
Matriz incluye privilegios, conflictos de revision, commit/rollback, cambios y
revocacion concurrentes, ambos sentidos de espera, tenants y ambas rutas.

Proximo: contratos/evaluadores puros de publicacion/seleccion/evidencia; despues
persistencia, privilegios/RLS, resolver/orden de locks y concurrencia/exitos antes
de fuentes/aceptacion y habilitacion real. Paso documental; diff --check correcto.
No se reejecuta suite por diseno sin codigo; ultima completa §88: 3320 passed.
Resolver deshabilitado. Ley fija; M3-T1 EN PROGRESO integral.
Sin nueva migracion, commit ni push.


## §90 — Contratos y evaluadores puros de auditoria de politica

2026-10-07. eipd_policy_audit.py implementa contratos internos cerrados/revalidados:
publicacion, evento de seleccion, selector, snapshot de auditoria, solicitud/plan
y evidencia de confirmacion. Modelos frozen, revisiones StrictInt y fechas con zona
normalizadas a UTC; constructores reciben id/actor/fecha explicitos de servidor.
Politica anidada conserva contrato §83; hash canonico calculado/comprobado, referencias
de publicacion unicas. Revalidacion desde python detecta modelos anidados mutados.

Snapshot valida publicaciones/eventos sin duplicados, cadena completa ordenada desde
bootstrap revision 1, hashes/identidad anterior, tiempos y selector igual al ultimo
evento. Sin eventos admite selector null solo como estado previo a bootstrap; no
es politica disponible para confirmar. Constructor de seleccion compara revision
esperada, exige publicacion registrada y no seleccionada previamente, genera evento
con revision consecutiva/identidad previa y selector coherente sin mutar entradas.
Publicar no selecciona; plan no escribe ni acredita permiso administrativo.

Evidencia pura exige selector coherente y recompone controles v2 con politica de la
publicacion actual, assessment/revision humana e identidad revalidados. Sin motivos
de confirmacion y sin tiempos invertidos, construye evidencia con tenant/assessment,
evento humano, publicacion/revision/seleccion, politica, hashes, actor y fecha.
Identidad sola o documento preparado no eluden negativos, obsolescencia, faltantes
ordinarios, politica deshabilitada ni otro tenant/assessment. Exito sintetico prueba
contrato; no confirma assessment real ni persiste evidencia.

65 pruebas nuevas: bootstrap/revocacion puros, contratos cerrados/hash/versiones,
StrictInt, falta de zona, duplicados/modelos mutados, revision esperada obsoleta,
publicacion desconocida/reseleccion, cadenas multiples/corrupcion/tiempos/plan,
evidencia de ambas rutas y rechazo de controles incompletos/historia impropia.
169 focalizadas aprobadas junto a 104 de politica/composicion §83.
Suite completa: 3385 passed en 293.55 s; Black/Ruff/diff --check correctos.

Pendiente persistencia/privilegios/RLS, autenticacion administrativa, historia completa
obtenida de DB, locks/atomicidad y resolver real. Modelos frozen no convierten objetos
anidados en almacenamiento inmutable; revalidacion protege fronteras puras, DB debera
impedir UPDATE/DELETE. Next: migracion append-only de control global y evidencia tenant
con pruebas PostgreSQL/RLS antes de servicios/resolver y cambio de orden de locks.
Fuentes/aceptacion pendientes, resolver fijo deshabilitado. Ley fija;
M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.


## §91 — Persistencia y privilegios de auditoria global EIPD

2026-10-07. Migracion append-only d73f518cbe42 sobre c62e407bad31 aplicada localmente:
eipd_policy_publications, eipd_policy_selections y eipd_policy_selector. Modelos ORM
alineados. Son controles globales, no datos de organizacion: sin tenant ficticio;
eventos humanos conservan sus tablas/RLS. Sin bootstrap ni politica activa insertada.

Publicacion almacena payload JSONB, version/referencia/hash, actor/fecha y evidencia.
Referencia unica; CHECK identidad/version/formato/textos y objeto JSONB con identidad
explicita. DB no recompone hash canonico ni verifica fuentes: futuro canal servidor
debe usar contratos puros §90 para validar payload completo/hash/fechas/autoridad.
FK de seleccion exige publicacion/hash registrados; revision unica/consecutiva,
identidad anterior completa y FK propia a revision/publicacion/hash anteriores.
Publicacion solo puede seleccionarse una vez. Selector singleton exige triple
revision/publicacion/evento coherente. Triggers de constraint diferidos comparan
selector con ultimo evento al finalizar transaccion: evento sin selector actualizado
falla al commit y rollback conserva estado anterior.

Rol eipd_policy_admin NOLOGIN/NOSUPERUSER/NOBYPASSRLS/NOCREATEROLE/NOCREATEDB,
separado y no asumible por app_user; sin concesion de membresia runtime. Migracion
rechaza rol preexistente incompatible o membresia runtime. Admin SELECT/INSERT en
control y UPDATE solo selector; sin UPDATE/DELETE/TRUNCATE de publicaciones/eventos.
RLS explicito de administracion y lectura autenticada global; app_user SELECT solo,
sin escritura/TRUNCATE. PUBLIC sin privilegios. Owner de migracion sigue privilegiado
para mantenimiento; append-only se exige a runtime/canal administrativo, no al owner.
Downgrade de esta migracion elimina tablas/triggers/funcion, conserva rol NOLOGIN
porque puede pertenecer a gestion de despliegue externa. No se reescriben migraciones
historicas ni eventos tenant. Rol no se expone como canal/API administrativa.

44 pruebas nuevas PostgreSQL: privilegios/flags/RLS, lectura sin/con autenticacion
y otro tenant, escrituras runtime y SET ROLE denegados, admin append-only y seleccion
atomica con rollback, trece corrupciones de publicacion/cadena/selector, fallo real
al commit por selector pendiente e inexistencia de publicacion tras rollback.
Fixtures solo datos sinteticos; limpieza owner elimina esos ids, no datos ajenos.
44 aprobadas en 2.98 s; Alembic check sin operaciones nuevas.
Suite completa: 3429 passed en 297.19 s; Black/Ruff/diff --check correctos.

Paso acotado al control global. Evidencia por tenant requiere siguiente migracion,
FK compuestas al assessment/evento humano/publicacion/seleccion y RLS/append-only;
no habilitar confirmacion excepcional antes de esa evidencia atomica. Resolver,
servicio administrativo, relectura/orden de locks y concurrencia de politica quedan
pendientes. Actualmente solo artefacto fijo deshabilitado, sin fuentes/aceptacion
verificadas. Ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §92 — Persistencia append-only de evidencia de confirmacion tenant

2026-10-07. Migracion e84a629dcf53 sobre d73f518cbe42 aplicada localmente, sin editar
migraciones anteriores ni rellenar historicos. EipdConfirmationEvidence almacena
identidades tenant/assessment/review/publication/selection, revision del selector,
politica, hashes documento/contexto, actor y fecha. Una evidencia por assessment.
review_decision interno constante continuar permite FK a decision humana positiva;
no es input publico ni modifica el contrato puro §90.

Nuevas UNIQUE de soporte en publicaciones/eventos humanos y FK compuestas exigen:
assessment del tenant, review del mismo tenant/assessment con politica/hashes exactos
y decision continuar, publicacion con version/referencia/hash coincidentes y triple
revision/publicacion/evento de seleccion auditado. Metadatos legacy null o revision
negativa no pueden acreditar evidencia; claves no reescriben eventos existentes.
CHECK version/revision/referencia/hashes; FK sin cascadas conservan procedencia.

RLS SELECT tenant via auth_org_ids. app_user SELECT/INSERT, sin UPDATE/DELETE/TRUNCATE;
PUBLIC y eipd_policy_admin sin privilegios sobre evidencia. INSERT exige actor JWT,
tenant accesible, assessment borrador con documento, ultima revision humana y
selector actual con publicacion declarada habilitada. Actor de publicacion no recibe
por ello acceso a evidencia tenant. Lectura historica no depende del selector actual:
revocacion conserva evidencia original. Owner de mantenimiento permanece privilegiado.

Estas barreras de DB no recomponen controles documentales/hash ni verifican fuentes,
roles de API o atomicidad de la seleccion durante espera. Servicio futuro debe usar
constructor puro §90, permisos, relecturas y orden de locks §89; no existe endpoint
para insertar evidencia ni conexion de confirmacion real en este paso. Fixtures
siembran politica/positivas sinteticas mediante owner, no mediante accion continuar.
Sin evidencia atomica integrada y fuentes/aceptacion, resolver fijo deshabilitado.

29 PostgreSQL nuevas: lectura/escritura runtime y tenant cruzado, UTC, append-only,
actor suplantado, borrador/documento/revision posterior/anonimo, trece enlaces falsos,
unicidad, rollback conjunto de evidencia/estado y revocacion con historia intacta.
Negativas/legacy fallan FK incluso usando owner sin RLS. Ajuste de limpieza de
fixtures elimina evidencia antes de reviews y controles sinteticos TEST de actores
de prueba antes de perfiles; scope asíncrono y campos lifecycle alineados.
105 focalizadas aprobadas antes de los tres casos finales; 29 nuevas finales
aprobadas en 3.70 s. Alembic check sin operaciones nuevas.
Suite completa: 3458 passed en 302.51 s; Black/Ruff/diff --check correctos.

Proximo: servicio administrativo de publicacion/seleccion y resolver de lectura
validada, aun sin politica real habilitada; despues locks compartidos/orden uniforme
y evidencia atomica en confirmacion, concurrencia/exitos y fuentes/aceptacion.
Ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §93 — Servicios internos de publicacion/seleccion y lectura auditada

2026-10-07. eipd_policy_store.py implementa publish_eipd_policy_v1,
select_eipd_policy_v1, read_eipd_policy_audit_snapshot_v1 y
read_selected_eipd_policy_v1. Sin endpoint administrativo, migracion nueva ni
conexion al resolver de acciones/readiness actuales. Solo canal DB current_user
exacto eipd_policy_admin escribe mediante estos servicios; app_user y owner normal
rechazados en la frontera del servicio. Ese rol acredita canal, no identidad personal:
caller administrativo futuro debe autenticar actor de plataforma y gestionar
commit/rollback. Actor explicito validado por contrato/FK, no tomado del tenant.

Publicar genera UUID/fecha de servidor (clock_timestamp), hash canonico y payload
cerrado via §90; referencia repetida rechazada antes de escritura. No selecciona.
Seleccionar valida solicitud cerrada/revision esperada, adquiere advisory lock
transaccional 719093 y luego FOR UPDATE del selector, relee auditoria, genera plan,
inserta evento y cambia selector en la misma transaccion. No commit interno ni locks
de serie. Advisory serializa tambien bootstrap cuando fila de selector no existe;
siempre precede selector en este canal. Error/rollback no deja evento parcial.

Lectura usa una sola sentencia SQL con aggregates del catalogo completo, cadena
ordenada y selector, bajo snapshot MVCC comun; mapea columnas explicitas a contratos
§90 y comprueba identidad/payload/hash/cadena/tiempos. Datos corruptos, selector
faltante o lectura runtime sin autenticacion no generan fallback habilitado.
Publicacion sin selector es estado de bootstrap, no politica disponible. Leer no
escribe/cachea ni garantiza estabilidad posterior hasta commit. No usar esta lectura
orientativa como resolver transaccional de confirmacion sin locks compatibles.

El canal de publicacion/seleccion admite exclusivamente activacion deshabilitada;
objetos sinteticos habilitados rechazados aun si cumplen schema/evidencia declarada.
No comprueba fuentes reales ni interpreta fechas como activacion. Artefacto fijo
resolve_eipd_gate_policy_v1 permanece intacto/deshabilitado en acciones actuales.

24 PostgreSQL nuevas: publicacion/bootstrap y campos servidor, permisos de canal,
una consulta y autenticacion, extra/StrictInt/target desconocido/revision obsoleta/
reseleccion/referencia repetida/activacion, corrupcion catalogo/hash/payload/tiempos/
selector, rollback y cuatro concurrencias reales con pg_blocking_pids: bootstrap y
seleccion existentes, commit y rollback. Segundo escritor relee revision despues de
espera; commit hace solicitud obsoleta, rollback permite plan sucesor. Fixtures
limpian controles TEST del actor sintetico por prueba, ademas de limpieza de sesion.
24 aprobadas en 2.37 s; Black/Ruff correctos.
Suite completa: 3482 passed en 315.74 s; Black/Ruff/diff --check correctos.

Proximo: resolver transaccional de lectura con bloqueo compartido seguro y orden
selector -> serie en acciones, manteniendo politica deshabilitada; integrar evidencia
atomica despues y validar concurrencia/exitos antes de fuentes/aceptacion/activacion.
Privilegios runtime solo SELECT se conservan: resolver con lock requiere mecanismo
limitado compatible con esos privilegios, no conceder UPDATE global al runtime.
Ley fija; M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.


## §94 — Resolver transaccional con bloqueo compartido limitado

2026-10-07. Migracion append-only f95b73aed064 sobre e84a629dcf53 aplicada localmente.
Funcion public.lock_eipd_policy_selector_v1() sin argumentos, SECURITY DEFINER,
search_path fijo pg_catalog y objetos de dominio calificados. Comprueba JWT auth.uid
con perfil registrado antes de bloquear; advisory xact lock compartido 719093 y
selector singleton FOR SHARE. Devuelve solo existencia; no escribe/publica/selecciona
ni revela datos tenant. EXECUTE solo app_user, retirado de PUBLIC/admin; runtime
conserva SELECT y no recibe UPDATE, INSERT de control ni BYPASSRLS.

Helper lock_eipd_policy_selector_v1 exige READ COMMITTED, invoca funcion y rechaza
selector ausente sin fallback/bootstrap. resolve_eipd_policy_snapshot_for_transaction_v1
lee y revalida auditoria despues de esperar, manteniendo locks hasta commit/rollback
del caller. Sin cache ni commits internos. READINESS orientativo §93 sigue separado.
Advisory compartido serializa tambien frente al bootstrap administrativo exclusivo;
lectores de distintos tenants pueden coexistir. Orden previsto de acciones pasa a
advisory compartido -> selector compartido -> serie exclusiva. Canal administrativo
§93 advisory exclusivo -> selector exclusivo, sin series; PATCH solo serie.

Garantia frente al canal administrativo que respeta ese protocolo y publicaciones
append-only; owner de mantenimiento permanece privilegiado. Actor registrado solo
acredita acceso a bloqueo global, no permisos de accion/tenant ni revision humana.
Resolver transaccional aun no conectado a acciones; estas siguen con artefacto fijo
deshabilitado y lock de serie actual. No introducir lock de selector despues de serie:
conexion siguiente debera cambiar orden uniformemente y releer controles/contexto.

15 PostgreSQL nuevas: atributos/permisos de funcion, anonimo/UUID sin perfil, selector
ausente, aislamiento no admitido, lectores compartidos entre tenants, dos variantes
admin esperando a lector y cuatro lector esperando a admin (bootstrap/seleccion,
commit/rollback), corrupción de hash/payload sin fallback. pg_blocking_pids demuestra
espera real; commit/rollback libera locks y relectura coincide con seleccion nueva/
anterior o ausencia. 39 focalizadas aprobadas con 24 del servicio §93 en 3.66 s.
Alembic check sin operaciones nuevas; Black/Ruff correctos.
Suite completa: 3497 passed en 309.60 s; Black/Ruff/diff --check correctos.

Proximo: integrar orden de locks y snapshot auditado en revision/confirmacion,
con selector deshabilitado explicitamente registrado y errores cerrados si falta;
evidencia atomica, concurrencia de acciones, autoridad administrativa personal y
fuentes/aceptacion antes de habilitar. No bootstrap supuesto ni promocion de historia.
Ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §95 — Revision humana conectada al selector auditado deshabilitado

2026-10-07. POST eipd-resolution/reviews adquiere advisory compartido y selector
FOR SHARE mediante §94 antes del lock FOR UPDATE de serie. Despues de ambos locks
relee borrador, contexto M2 y auditoria completa, y evalua v2 con la publicacion
seleccionada. Historial y diagnostico v1 conservados. Evento negativo guarda version,
referencia y hash de esa publicacion; nunca politica del cliente ni identidad fija
como fallback. Permisos/tenant/suscripcion siguen en dependencias autenticadas.
Locks permanecen hasta commit/rollback del caller; no commits internos.

Selector ausente o auditoria/hash/payload incoherentes devuelve 409 con codigo
politica_eipd_no_disponible, sin evento ni cambio de borrador. Publicacion habilitada
rechazada explicitamente (politica_eipd_habilitada_no_admitida): este paso no habilita
positivas ni excepciones. Runtime no publica/selecciona ni hace bootstrap. Para usar
revision se requiere selector deshabilitado registrado por canal autorizado; ninguna
migracion o accion tenant crea ese selector automaticamente.

Nueve pruebas nuevas con PostgreSQL/app_user: dos decisiones negativas/identidad real,
orden SQL selector antes de serie y lectura posterior, tres fallos cerrados, cuatro
concurrencias reales observadas por pg_blocking_pids: revision espera seleccion
administrativa commit/rollback y registra nueva/anterior identidad; administrador
espera fin de transaccion de revision commit/rollback, con evento persistido/revertido.
Fixtures HTTP existentes registran explicitamente artefacto deshabilitado conocido
por canal interno de test y limpian solo su publicacion/selector; no simulan fallback
ni credenciales administrativas de produccion. 33 HTTP anteriores y nueve nuevas
aprobadas focalmente. Suite completa: 3506 passed en 313.64 s; Black/Ruff/Alembic check/diff correctos.

Alcance de este checkpoint: revision humana exclusivamente. Confirmacion y readiness
v2 aun usan artefacto fijo deshabilitado; cuando selector tiene identidad diferente,
readiness puede mostrar revision obsoleta respecto de su politica fija. Esa consulta
es orientativa y no acredita vigencia contra selector real hasta siguiente integracion.
No cierre del control global ni activacion. Proximo: conectar readiness y confirmacion
al mismo selector con orden compatible, preservando ordinario sin EIPD/historia sola;
luego evidencia atomica, autoridad personal, matriz de exitos y fuentes/aceptacion.
Ley fija; M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.


## §96 — Preparacion y confirmacion con el mismo selector auditado

2026-10-07. Readiness v2 lee publicacion seleccionada mediante snapshot SQL completo
validado y sin locks/escrituras. Ya no compone con artefacto fijo: politica, hash y
estado de identidad humana corresponden al selector real. Es consulta orientativa,
no garantiza estabilidad hasta una accion. Selector ausente/corrupto en su ambito
EIPD devuelve 409 politica_eipd_no_disponible, sin fallback ni bootstrap.

Confirmacion adquiere advisory compartido -> selector FOR SHARE si existe -> serie
FOR UPDATE, antes de releer borrador/contexto M2/controles. Helper exige READ COMMITTED;
require_selector=False solo permite adquirir advisory aun sin fila para conservar
ordinarios sin EIPD. Ambito de gate revalidado bajo serie conserva §88: documento,
deteccion requiere EIPD/revision o expedientes de excepcion; historia sola no amplía
ambito de confirmacion. Si entra al ambito, exige snapshot seleccionado validado
tras ambos locks; ausencia/incoherencia bloquea antes de reemplazar confirmado.
Bootstrap/seleccion administrativos esperan advisory; PATCH solo serie, sin inversion.

Revisiones, readiness y confirmacion usan helper compartido que admite unicamente
activacion deshabilitada. Politica habilitada aun rechazada con codigo
politica_eipd_habilitada_no_admitida, aunque una fixture privilegiada la insertase.
Sin politica client-side, nueva migracion, seed productivo ni commits internos.
Todavia no se conecta escritura de evidencia de confirmacion EIPD: ninguna ruta
excepcional se habilita en este checkpoint. No promociona revisiones historicas.

Trece PostgreSQL/app_user nuevas: ambas rutas coinciden entre revision/consulta/error
de confirmacion; reseleccion cambia hash y vuelve obsoleta revision; seis casos de
selector ausente/hash/extra en preparacion/confirmacion conservan borrador/eventos;
ordinario sin selector confirma y no crea selector/evidencia; cuatro concurrencias
reales observadas con pg_blocking_pids, confirmacion esperando admin commit/rollback
y admin esperando fin de transaccion de confirmacion bloqueada commit/rollback.
13 aprobadas en 5.68 s; 221 focalizadas de confirmacion/preparacion aprobadas en
20.40 s. Dobles unitarios de confirmacion declaran politica/lock simulados, mientras
HTTP y PostgreSQL verifican comportamiento real. API Licitud historica tambien
registra selector explicito; 53 regresiones verificadas en 76.42 s. Suite completa: 3519 passed en 329.62 s; Black/Ruff/Alembic check/diff correctos.

Proximo: conectar evidencia de confirmacion atomica y validar fallos/reemplazo y
exitos sinteticos antes de habilitar; autoridad administrativa personal, fuentes
complementarias y aceptacion tecnica trazable pendientes. Ley fija; EN PROGRESO
integral. Sin commit ni push. §95 tambien sigue pendiente de commit.


## §97 — Evidencia de confirmacion conectada a la transaccion

2026-10-07. Servicio interno eipd_confirmation.record_eipd_confirmation_evidence_v1
relee snapshot auditado, recompone controles con constructor puro §90 y genera UUID
y fecha UTC de servidor (clock_timestamp). Inserta EipdConfirmationEvidence y flush,
sin commit, endpoint ni parametros de evidencia del cliente. Caller conserva locks
selector -> serie y arma contexto actual; DB §92 verifica tenant/JWT/borrador/ultima
revision positiva y FK exactas de politica/documento/contexto/seleccion.

Confirmacion llama servicio solo tras aprobar controles v2 en ambito EIPD y antes
de leer/modificar confirmado anterior. Borrador debe seguir borrador al insertar
por RLS; evidencia, reemplazo y confirmacion quedan en misma transaccion del caller.
ValueError/contrato no preparado devuelve 409 evidencia_eipd_no_preparada; errores
DB/flush propagan para rollback. Si cualquier paso falla, no conserva evidencia ni
reemplazo parcial. Ordinario fuera de EIPD no inserta evidencia. No commits internos.

Guardia §96 se conserva: politica habilitada rechazada en la aplicacion. Exitos
excepcionales solo se ejercitan en pytest con politica/positiva sinteticas insertadas
por owner de fixtures y override local de _selected_disabled_eipd_policy_v1. No flag,
variable de entorno, endpoint o bypass de produccion. Constructor/relectura/gates,
RLS y persistencia real no se simulan; ninguna fuente de fixture acredita verificacion
real ni aceptacion tecnica de politica productiva.

Doce pruebas PostgreSQL/app_user nuevas: dos guardias reales rechazan habilitada sin
evidencia; cuatro exitos sinteticos (ambas rutas, con/sin confirmado previo) conservan
identidad exacta/actor/fecha y evidencia unica, segundo intento no duplica; cuatro
fallos con anterior confirmado revierten evidencia/borrador/anterior (FK real de
insercion, fallo tras evidencia, tras reemplazo y tras flush final); dos controles
fallidos (negativa/identidad obsoleta) prueban que no se intenta insertar evidencia.
12 aprobadas en 4.59 s. Fixtures limpian evidencia antes de revision/politica y RAT.
Suite completa: 3531 passed en 334.47 s; Black/Ruff/Alembic check/diff correctos.

Proximo: concurrencia de confirmaciones exitosas y revocacion tras exito con evidencia
historica preservada, dos series/tenants, y autoridad administrativa personal antes
de fuentes complementarias/aceptacion/activacion. M3-T1 EN PROGRESO integral, ley fija.
Sin migracion, commit ni push; §§95–97 pendientes de commit.


## §98 — Concurrencia exitosa y revocacion con evidencia preservada

2026-10-07. Se amplía matriz PostgreSQL/app_user; sin cambio de comportamiento ni
activacion productiva. Reutiliza politica/positiva owner sinteticas y override local
de guardia de pytest de §97. Servicios de confirmacion, constructor, RLS/FK, locks,
seleccion administrativa deshabilitada y commits/rollbacks son reales.

Doce pruebas nuevas, ambas rutas sensible/sensible-biometrica, con pg_blocking_pids
para demostrar espera efectiva y timeout acotado, no inferir bloqueo por sleep:

- Dos confirmaciones de misma evaluacion/serie con anterior confirmado: primer commit
  deja segunda en 409 al releer status; primer rollback permite exito de segunda.
  En ambos casos queda una evidencia exacta y un reemplazo, sin duplicacion. Evidencia
  no es visible desde otra transaccion antes de commit.
- Administrador intenta seleccionar nueva politica deshabilitada mientras confirmacion
  exitosa conserva locks: espera hasta commit/rollback. Tras commit evidencia original
  se conserva campo por campo y confirmado mantiene status; tras rollback no queda
  evidencia. Seleccion deshabilitada posterior bloquea accion siguiente con identidad
  humana obsoleta y gate_eipd_no_habilitado. Sucesor/positiva historica de test no se
  promocionan ni reemplazan confirmado tras revocacion.
- Confirmacion comienza mientras revocacion tiene lock exclusivo: tras commit revalida
  politica deshabilitada y rechaza sin evidencia/status; tras rollback usa seleccion
  original habilitada sintetica y confirma con evidencia de revision 1.

12 aprobadas en 5.78 s. Fixtures restauran selector previo solo mediante owner para
limpieza tras aserciones, borran publicacion/evento sucesor de test y luego limpian
estado original. Esa restauracion no es canal de rollback/reseleccion productivo:
contrato real sigue exigiendo publicacion nueva. Sin flags/env/endpoints nuevos.
Suite completa: 3543 passed en 343.50 s; Black/Ruff/Alembic check/diff correctos.

Proximo: ampliar exitos concurrentes a series independientes/tenants y PATCH, despues
resolver autoridad personal administrativa; fuentes complementarias y aceptacion
tecnica trazable pendientes antes de habilitar. M3-T1 EN PROGRESO integral; ley fija.
Sin migracion ni cambio de servicios, commit o push; §§95–98 pendientes de commit.


## §99 — Exitos de series/tenants independientes y PATCH concurrente

2026-10-07. Ampliacion de pruebas PostgreSQL/app_user, sin cambios de servicios,
privilegios, migraciones ni activacion. Politica/positivas sinteticas y override
pytest local de guardia §97 conservados. Fixture owner prepara segundo RAT real
(tratamiento/finalidad/categorias/titulares), serie y borrador documental equivalentes
en misma organizacion o en organizacion B; contexto se valida con constructor M2 real,
no sustitucion de builder/gates/RLS. IDs/actores/revisiones diferentes por serie.

Doce nuevas, ambas rutas sensible/sensible-biometrica:

- Cuatro exitos de series independientes (misma org/dos orgs): segunda confirma antes
  de terminar transaccion de primera, ambas conservan locks compartidos de selector.
  Evidencia de cada una invisible antes de commit; despues existe una por evaluacion,
  con actor correspondiente. RLS muestra ambas al mismo tenant o solo propia entre
  tenants, y servicio cruzado devuelve 404 sin acceso.
- Ocho PATCH/confirmacion (misma org/dos orgs, commit/rollback): PATCH parcial toma
  serie A; confirmacion A espera realmente (pg_blocking_pids) manteniendo selector
  compartido. Confirmacion B avanza y hace commit mientras A sigue esperando. Commit
  de PATCH invalida controles revalidados de A y bloquea sin evidencia; rollback
  permite exito de A con evidencia. No se revierte ni sobrescribe evidencia de B.

12 aprobadas en 6.64 s; timeout acotado para detectar espera indebida. Fixtures limpian
primero evidencia/revision y despues borrador/serie/RAT B antes de limpiar politica A.
Clonado owner es preparacion sintetica de pruebas, no via nueva de producto ni
promocion de positivos historicos. Guardia de habilitadas en aplicacion conservada.
Suite completa: 3555 passed en 345.51 s; Black/Ruff/Alembic check/diff correctos.

Proximo: definir/implementar autoridad personal del canal administrativo de politica,
con permisos separados de roles tenant; fuentes complementarias y aceptacion tecnica
trazable antes de habilitar. No cierre integral ni validacion juridica por total de
pruebas. M3-T1 EN PROGRESO integral; ley fija. Sin commit ni push.


## §100 — Contrato de autoridad personal administrativa

2026-10-07. Paso documental previo a implementar autorizacion personal. ADR 0001
establece profiles.is_superadmin como autoridad global, independiente de membresias.
get_current_profile valida JWT mediante extract_auth_identity, establece sub local y
aprovisiona perfil sin promoverlo; require_superadmin comprueba bandera. Canal EIPD
actual _require_admin solo verifica current_user=eipd_policy_admin; actor_id recibido
por servicios internos no acredita por si mismo identidad personal autenticada.

Contrato elegido: exigir simultaneamente identidad JWT verificada por servidor,
perfil global superadmin vigente y conexion administrativa separada. Actor de auditoria
se deriva del perfil autorizado; nunca de actor_id/client payload, accepted_by,
verified_by, X-Organization-Id ni roles owner/admin/editor de organizacion. app_user
no recibe membresia del rol administrativo ni credenciales owner. JIT no promueve;
sin identidad, perfil, permiso o canal adecuado, rechazar antes de publicar/seleccionar.
No crear API administrativa operativa hasta completar barreras y pruebas.

Precondicion descubierta en codigo: migracion 0001 otorga CRUD de todas las tablas
public a app_user y no incluye profiles en lista RLS; 0002 agrega is_superadmin.
Las migraciones revisadas no acreditan proteccion suficiente de columnas de identidad/
autoridad. Esto es hallazgo de codigo, no prueba de explotacion ni comprobacion de
privilegios efectivos en despliegues. Proximo paso debe auditar privilegios reales y
proteger auth_user_id/id/is_superadmin frente a insercion/actualizacion suplantada,
promocion y borrado runtime. Mantener JIT legitimo y cambios de datos de perfil
permitidos; no conceder promocion por rol tenant. Migracion nueva append-only.

Orden administrativo previsto: autoridad personal estabilizada (lectura protegida de
perfil) -> advisory exclusivo -> selector exclusivo; nunca serie. Revocacion personal
concurrente debe tener resultado definido: aplicada antes de autorizar rechaza, o
espera fin de operacion ya autorizada bajo lock. No confiar solo en objeto ORM/cache
anterior a espera. Funcion DB limitada, si se utiliza, exige canal administrativo,
search_path seguro y permisos minimos; no autentica criptograficamente JWT por si sola.
Caller debe propagar sub verificado a conexion administrativa en transaccion local,
sin fuga de identidad entre conexiones de pool. Actor/fecha/hash siempre servidor.

Matriz obligatoria: anonimo/JWT invalido/perfil ausente; tenant owner/admin sin bandera;
actor suplantado; superadmin autenticado por canal incorrecto; canal correcto sin
identidad; JIT sin autopromocion; SQL runtime no altera autoridad/identidad; revocacion
personal commit/rollback antes/durante espera; aislamiento del contexto local del pool;
auditoria exacta del actor; rollback sin publicacion/seleccion parcial. Superadmin
legitimo sin membresia tenant puede administrar solo por canal separado autorizado.

Sin cambio de servicios, permisos, migraciones, pruebas ejecutables ni activacion en
este checkpoint. Ultima suite ejecutada: 3555 passed §99; no se presenta como prueba
del contrato nuevo. Autoridad personal todavia NO implementada. Fuentes/aceptacion
pendientes; ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §101 — Proteccion de identidad y autoridad de perfiles

2026-10-07. Auditoria local efectiva antes del cambio con conexion app_user confirma
INSERT/UPDATE/DELETE de profiles y UPDATE de is_superadmin permitidos. Hallazgo §100
confirmado para base local; no se extrapola a despliegues externos. Migracion nueva
append-only a06c84bf175e sobre f95b73aed064 aplicada localmente.

Revoca INSERT/UPDATE/DELETE/TRUNCATE de tabla profiles para app_user; conserva SELECT
existente y concede INSERT solo auth_user_id/email/full_name, UPDATE solo email/
full_name/updated_at. ID por default DB y is_superadmin=false por default; no INSERT
explicito de ID/autoridad ni UPDATE identidad/autoridad. Sin concesiones al canal EIPD.
Trigger SECURITY INVOKER/search_path pg_catalog exige auth.uid() no nulo y matching
NEW.auth_user_id para runtime; UPDATE ademas acredita identidad OLD y rechaza cambio
de ID/auth_user_id/is_superadmin. Cambios basicos de perfil ajeno rechazados. Funcion
no obtiene privilegios elevados; EXECUTE retirado de PUBLIC/app_user/eipd_policy_admin,
trigger realiza validacion. Owner de mantenimiento conserva atribuciones explicitas.

JIT get_current_profile conserva INSERT de columnas permitidas/ON CONFLICT DO NOTHING,
perfil nuevo sin promocion y RETURNING/SELECT. No cambia API/autenticacion/JWT ni
activa canal administrativo. Proteccion no representa RLS completo de perfiles:
SELECT anterior se conserva y administracion personal EIPD aun pendiente. Downgrade
restaura grants anteriores de CRUD y retira trigger/permisos de columna nuevos;
es reversion de seguridad, no necesaria para operar upgrade.

Doce PostgreSQL/app_user nuevas: privilegios efectivos, JIT idempotente y update basico
propio, cuatro INSERT forjados (anonimo/otra identidad/promocion/ID explicito), seis
mutaciones denegadas (promocion/auth_user_id/ID/borrado/truncate/datos ajenos).
22 focalizadas con autenticacion aprobadas en 0.51 s. No datos reales alterados por
pruebas; insercion/actualizacion propia de test revertida por rollback.
Suite completa: 3567 passed en 431.30 s; Black/Ruff/Alembic check/diff correctos.

Proximo: implementar autorizacion personal transaccional del canal EIPD (JWT verificado,
perfil superadmin vigente, actor derivado y rol separado), locks/revocacion/pool y
pruebas; fuentes/aceptacion antes de activar. Ley fija; EN PROGRESO integral.
Sin commit ni push; §100 documental tambien pendiente de commit.


## §102 — Barrera personal transaccional limitada

2026-10-08. Migracion append-only b17d95c0286f sobre a06c84bf175e aplicada localmente.
public.lock_eipd_personal_authority_v1() sin argumentos retorna UUID de perfil derivado
de auth.uid(); exige perfil existente con is_superadmin=true. SELECT perfil FOR SHARE
antes de evaluar autoridad; retiene lock hasta commit/rollback. Funcion SECURITY
DEFINER con search_path pg_catalog y referencias calificadas, EXECUTE solo rol
administrativo EIPD (owner mantenimiento privilegiado); app_user sin EXECUTE, canal
administrativo sin UPDATE de perfiles ni elevacion nueva. No publica ni selecciona.

Helper authorize_eipd_personal_actor_v1 exige current_user=eipd_policy_admin y
READ COMMITTED; invoca funcion, sin actor del cliente/cache/commit. Sub debe provenir
de JWT verificado por caller y propagarse localmente a conexion separada. Funcion SQL
no verifica criptografia del JWT. Orden previsto perfil -> advisory -> selector,
sin series. No endpoints, configuracion de pool/credenciales ni bootstrap nuevos.

Nueve PostgreSQL nuevas: anonimo/perfil desconocido/owner tenant rechazados; superadmin
por canal runtime rechazado incluso al invocar funcion directamente; atributos,
privilegios y actor exacto derivados; sub local desaparece tras rollback. Cuatro
concurrencias con pg_blocking_pids: revocacion previa commit rechaza tras esperar,
rollback permite autorizacion; revocacion posterior espera fin de transaccion personal
(commit/rollback). Actor global dedicado sintetico sin membresia tenant, limpiado
por owner; no se promueven perfiles de usuarios reales. 45 focalizadas con proteccion
de perfiles/servicios de politica aprobadas en 3.37 s; Black/Ruff/Alembic check correctos.
Ultima suite completa sigue 3567 §101; no se registra total nuevo sin ejecutarla.

Limite: barrera todavia NO conectada a publish/select ni a API/canal autenticado.
Servicios internos conservan contrato confiable anterior actor_id; rol DB solo aun
no acredita persona para escritores. Proximo: integrar barrera antes de locks/global
writes, actor derivado y rechazo de suplantacion, ajustar fixtures y suite completa;
despues transporte autenticado/pool y fuentes/aceptacion antes de habilitar.
Ley fija; EN PROGRESO integral. Sin commit ni push.


## §103 — Escritores con entrada personal y actor derivado

2026-10-08. publish_eipd_policy_v1/select_eipd_policy_v1 ya no aceptan actor_id.
Invocan authorize_eipd_personal_actor_v1 antes de escribir/adquirir locks globales;
actor auditable se deriva de perfil superadmin bloqueado. Seleccion: perfil FOR SHARE
-> advisory exclusivo -> selector FOR UPDATE, sin serie ni commit interno. Solicitud
sin identidad/canal/autoridad falla antes de mutaciones; actor forjado no es argumento
admitido. Politicas habilitadas siguen rechazadas por el canal de publicacion/seleccion.

Primitivas anteriores se renombran _publish_eipd_policy_v1/_select_eipd_policy_v1,
privadas de persistencia para caller confiable. No endpoints ni entrada personal;
DB rol sigue canal privilegiado y no valida criptograficamente sub por si solo.
Fixtures antiguas usan explicitamente primitivas privadas para preparar politica/
metadatos sinteticos, sin promover perfiles tenant ni simular nuevas barreras. Las
pruebas nuevas ejercitan entradas personales reales y actor global dedicado sin
membresia tenant. Transporte futuro debe usar exclusivamente entradas personales y
propagar sub de JWT verificado, con conexion separada y contexto local del pool.

Once PostgreSQL nuevas: publicacion/seleccion exactas con actor derivado, seis rechazos
(anonimo/desconocido/tenant para ambos escritores) conservan catalogo, superadmin por
runtime rechazado, dos argumentos actor_id forjados rechazados sin escritura, rollback
conjunto de publicacion/evento/selector. 44 focalizadas con autoridad personal y
servicios de persistencia aprobadas en 4.41 s.
Suite completa: 3587 passed en 348.04 s; Black/Ruff/Alembic check/diff correctos.

Sin nueva migracion sobre b17d95c0286f. No API administrativa operativa, pool/config/
credenciales nuevas ni activacion real. Proximo: transporte administrativo autenticado
con canal DB separado/contexto transaccional local y pruebas de permiso/revocacion/
pool; despues fuentes complementarias y aceptacion tecnica trazable. Ley fija;
EN PROGRESO integral. Sin commit ni push; §102 tambien pendiente de commit.

## §104 — Pool separado y dependencia autenticada EIPD (2026-10-08)

Se incorpora `EIPD_ADMIN_DATABASE_URL` opcional y secreta, sin valor por defecto ni
fallback a DATABASE_URL/APP_DATABASE_URL. El pool se crea de forma diferida,
READ COMMITTED, sin echo y con parametros ocultos. No se cambia .env ni se
provisionan credenciales reales: el login debe provisionarse por mantenimiento.

`get_eipd_admin_db` valida el bearer con extract_auth_user_id (JWT existente)
antes de obtener el pool. Requiere login dedicado LOGIN/NOINHERIT, sin superuser,
BYPASSRLS, CREATEDB, CREATEROLE, REPLICATION, propiedad de relaciones ni membresias
directas adicionales; miembro de eipd_policy_admin. Rechaza owner y app_user.
SET LOCAL ROLE eipd_policy_admin y sub parametrizado/local preceden la barrera
personal FOR SHARE. No usa JIT, organizacion del header ni actor del payload.
La dependencia gestiona commit/rollback; el lock personal dura la transaccion.

17 pruebas nuevas, con login/password sinteticos efimeros y pool real de una
conexion: JWT ausente/invalido antes de pool, configuracion ausente/invalida,
identidad derivada, reutilizacion del mismo backend tras commit/rollback sin
sub/rol residual, tenant/desconocido/revocado rechazados, owner/app_user rechazados,
y privilegios excesivos bloqueados. Las pruebas de JWT del modulo existente y
las barreras/escritores anteriores se ejecutan juntas: 47 passed en 3.18 s.
Suite completa: 3604 passed en 352.09 s; Black/Ruff/Alembic check/diff correctos.

No nueva migracion, rutas administrativas ni activacion operativa. La validacion
criptografica se reutiliza; los tests de pool inyectan la identidad extraida y
no acreditan una ruta HTTP integrada. Pendiente conectar endpoints publicacion/
seleccion a esta dependencia, validar HTTP/JWT real y concurrencia de revocacion
por transporte; luego fuentes/aceptacion y despliegue/provision controlados.
Ley 21.719/19.628 reformada sigue base fija; M3-T1 EN PROGRESO integral y
activacion excepcional bloqueada. Sin commit/push en este paso.

## §105 — Rutas administrativas EIPD con JWT/pool real (2026-10-08)

Se registran POST /admin/eipd/publications y POST /admin/eipd/selections en la API.
PublicationRequest exige policy/rationale/evidence_reference; SelectionRequest exige
publication_id/expected_revision/rationale/evidence_reference. Esquemas cerrados,
revision StrictInt; actor/UUID/reloj/hash/evento se generan o derivan en servidor.
Se reutilizan entradas personales §103 y dependencia §104, nunca primitivas privadas
ni require_superadmin/JIT/DB tenant. Organizacion del header no concede autoridad.

201 devuelve publicacion o plan evento/selector; cada request tiene su propia
transaccion. Publicar no selecciona automaticamente. 401 token ausente/invalido;
403 identidad verificada sin perfil superadmin vigente; 503 JWKS/pool ausente o
canal inapropiado. 422 cuerpo/campos adicionales; 409 rechazo de dominio/revision
obsoleta/referencia repetida. Unique violation de publicacion tambien se traduce
a 409 para la carrera potencial, sin exponer mensajes SQL. Esa carrera concurrente
queda pendiente de matriz HTTP del siguiente paso; no acreditada por test secuencial.

38 pruebas HTTP nuevas usan app registrada, JWT ES256 real con par de claves y
JWKS sintetico, y pool PostgreSQL/login limitado reales. Cubren publicacion seguida
de seleccion y visibilidad de commit con actor derivado, pool limpio, seis formas
de token invalido por ambas rutas antes de pool, tenant/desconocido/revocado,
campos auditables de cliente rechazados, duplicado/revision obsoleta/desconocido,
publicacion habilitada bloqueada, fallo de commit con rollback sin respuesta exitosa,
JWKS caido, configuracion ausente y owner/app_user rechazados. Sin reemplazar
extract_auth_user_id ni dependencias de autoridad/escritores en pruebas HTTP.
85 focalizadas con pool/autoridad/escritores/autenticacion anteriores: 9.03 s.
Suite completa: 3642 passed en 355.96 s; Black/Ruff/Alembic check/diff correctos.

No migracion nueva ni provision/despliegue con credenciales reales. Ambas operaciones
conservan guardias de habilitadas; sin activacion excepcional. Pendiente concurrencia
HTTP de revocacion/seleccion/publicacion y fallos transaccionales adicionales,
fuentes oficiales/aceptacion y provision operativa controlada. Ley 21.719/19.628
reformada base fija; M3-T1 EN PROGRESO integral. Sin commit/push en este paso.

## §106 — Concurrencia administrativa por HTTP (2026-10-08)

Doce pruebas nuevas, sin cambios en rutas/servicios/migraciones. App registrada,
JWT ES256 firmado con JWKS sintetico, login/pools PostgreSQL restringidos reales.
Las pausas de test controlan flush/commit; no reemplazan SQL, barrera personal,
validacion JWT, escritores ni rollback. Se observan bloqueos efectivos mediante
pg_blocking_pids; pg_stat_clear_snapshot evita cache de pg_stat_activity en el
observador transaccional. Timeouts acotados y limpieza de tasks/pools/roles/perfiles.

Cuatro casos (publicacion/seleccion x commit/rollback de revocacion previa):
peticion HTTP espera UPDATE del perfil; revocacion confirmada -> 403 sin escrituras;
revocacion revertida -> 201. Se relee autoridad despues de esperar.
Seis casos (ambas rutas x commit/rollback/cancelacion de la peticion autorizada):
UPDATE de revocacion espera FOR SHARE hasta cierre. Commit -> 201/cambio persistido;
fallo de commit -> 500/rollback sin cambio; cancelacion -> rollback sin cambio.
Despues de confirmar revocacion, siguiente peticion -> 403; pool sin sub/rol residual.

Seleccion concurrente: dos conexiones esperando advisory, publicaciones diferentes
con expected_revision=0 -> un 201 y un 409; exactamente un evento/selector revision 1.
Publicacion duplicada concurrente: ambas pasan precheck y se encuentran en flush;
se observa espera real por unicidad mientras ganador retiene commit. Un 201 y un
409 (SQLSTATE 23505), una sola publicacion y ningun evento/selector. Esto acredita
la traduccion de conflicto de DB implementada en §105, antes solo secuencial.

Doce nuevas aprobadas en 2.98 s; 97 focalizadas con API/pool/autoridad/escritores/auth
aprobadas en 11.73 s. Suite completa: 3654 passed en 369.30 s; Black/Ruff/Alembic check/diff correctos.
No migracion ni datos/credenciales reales alterados; fixtures usan identidades y
roles temporales propios. Sin habilitacion excepcional ni despliegue operativo.

Proximo: revisar fuentes oficiales y trazabilidad de aceptacion tecnica para el
control EIPD, sin habilitar mientras falten requisitos; registrar/probar provision
operativa por separado. Ley 21.719/19.628 reformada base fija independiente del
calendario; M3-T1 sigue EN PROGRESO integral. Sin commit/push en este paso.

## §107 — Revalidacion de fuentes y trazabilidad tecnica (2026-10-08)

Base Git limpia/sincronizada: 97d4fd29920e98a7b0a94714b04ae43e7cb5d010 (§106).
Registro m3-t1-eipd-fuentes.md actualizado: BCN por portal nuevo, art15ter localizado;
Diario Oficial CVE 2583630 PDF abierto. Busqueda acotada no verifica instrumento
complementario especifico de Agencia; no acredita inexistencia. Ley reformada
base fija independiente del calendario; no reinterpretar consulta facultativa como
aprobacion juridica universal. No version/autoridad/aceptacion inventadas.

| Criterio actual | Evidencia trazable | Estado |
| --- | --- | --- |
| Autoridad y escritores personales | 07bc7dd8ad06a16f5e32efc17ac67efa1036e356, §§102–103 | Implementado/probado |
| Pool separado y JWT/sub local | 01d27b0c44cec33dd2dfa2f160f0e6e3f3dc3257, §104 | Implementado/probado local |
| Rutas HTTP administrativas | 56dba76a0052eccb766f77ac91ba59c62d1f922d, §105 | Implementado/probado local |
| Revocacion/carreras/rollback/cancelacion HTTP | 97d4fd29920e98a7b0a94714b04ae43e7cb5d010, §106 | Doce nuevas; 97 focalizadas, 11.73 s |
| Suite completa del contenido §106 | Checkpoint §106; pruebas antes del commit, contenido luego versionado | 3654 passed, 369.30 s |
| Head local de migraciones | alembic current consultado §107 | b17d95c0286f (head) |
| Fuentes legales base | Registro F1/F4 y revalidacion §107 | Texto consultado, sin certificacion exhaustiva de vigencia |
| Instrumentos complementarios Agencia | Registro §107 | PENDIENTE; sin instrumento/version verificados |
| Decision de aceptacion real con responsable/evidencia | Sin aceptacion trazable registrada | PENDIENTE; pruebas no equivalen a accepted_by |
| Provision/validacion operativa real | Solo roles/credenciales sinteticos de tests | PENDIENTE; sin despliegue acreditado |
| Activacion excepcional real | Guardias productivas conservadas | BLOQUEADA |

La matriz inicial de este documento y checkpoints anteriores son historicos;
para autoridad/pool/transporte/head actual prevalece esta evidencia. No se declara
aceptacion integral ni se genera objeto de politica con fuentes verificadas,
accepted_by, validation_commit o activation habilitada. Este inventario asocia
pruebas a commits; no reemplaza decision de aceptacion ni validacion operativa.

Solo documentacion en §107: diff --check correcto; no nueva suite ni migracion.
Ultima suite completa conserva 3654 §106. Proximo paso independiente: procedimiento
verificable de provision operativa del canal con politica deshabilitada, sin
credenciales reales ni activacion. Completar fuentes/aceptacion antes de habilitar.
M3-T1 EN PROGRESO integral. Sin commit/push en este paso.

## §108 — Procedimiento operativo deshabilitado preparado (2026-10-09)

Base c963e75c2caa0936e04fdeac01ebad4f903ae911. Se agrega
m3-t1-eipd-provision-operativa.md: expediente de entorno/commit/head/login/staff/
secreto por referencia/selector, provision del login separada del grupo NOLOGIN,
comprobaciones de rol local y permisos, pruebas HTTP negativas/positivas con politica
deshabilitada, verificacion de auditoria, revocacion/retirada/rotacion con drenaje.
Reconoce ausencia de GET snapshot; lectura coherente por herramienta de mantenimiento.
Sin retry ciego, borrado de auditoria, downgrade ni aceptacion/fuentes inventadas.

Plantillas no ejecutadas; no se provisionan roles/credenciales/perfiles ni se envia
trafico a un entorno operativo. JSON de publicacion validado contra PublicationRequest;
diff --check correcto. No cambios de codigo ni nueva suite completa: 3654 §106.
Provision real, instrumento complementario y decision de aceptacion permanecen
PENDIENTES. Proximo: preparar preflight verificable de solo lectura del canal,
sin reemplazar JWT/autoridad ni emitir publicacion/seleccion. Activacion bloqueada;
ley reformada base fija; M3-T1 EN PROGRESO integral. Sin commit/push.

## §109 — Preflight administrativo de solo lectura (2026-10-09)

Se agrega backend/scripts/eipd_admin_preflight.py, ejecutable desde backend con
python -m scripts.eipd_admin_preflight. Usa solo EIPD_ADMIN_DATABASE_URL/pool §104;
transaccion READ ONLY, chequeo de login/rol, identidad residual vacia, READ COMMITTED,
EXECUTE de barrera y ausencia de UPDATE de perfiles/is_superadmin. Lee y valida
snapshot completo; rechaza politicas habilitadas incluso no seleccionadas.
Siempre rollback. No setea sub ni llama a barrera FOR SHARE ni publica/selecciona.

Salida JSON limitada: ok (exit 0) si canal y selector deshabilitado coherentes;
pending_selector (exit 2) si canal/auditoria validos sin selector; failed (exit 1)
ante fallo, sin excepcion/URL/secretos. Informe indica expresamente autenticacion
personal no verificada y activacion no autorizada. No acredita provision integral,
JWT HTTP, grupo/permisos completos ni aceptacion real; completar runbook §108.

Seis pruebas nuevas: ausencia de selector sin bootstrap, seleccion deshabilitada
sin cambios y pool limpio, owner/tenant rechazados, escritura accidental bloqueada
por PostgreSQL READ ONLY (25006), error CLI sin divulgar texto sensible. 23 focalizadas
con canal/pool aprobadas en 1.84 s; Black/Ruff/diff correctos. Sin nueva suite completa;
ultima 3654 §106. No migracion/configuracion/roles/credenciales reales modificados.
No preflight ejecutado contra entorno operativo; pruebas usan login/roles sinteticos.
Proximo: ampliar diagnostico de permisos de grupo/dominio y evidencia de entorno
sin secretos; ejecutar provision solo sobre destino/identidad acreditados. Fuentes/
aceptacion real pendientes, activacion bloqueada, ley fija, M3-T1 EN PROGRESO.
Sin commit/push.

## §110 — Permisos efectivos y limites de evidencia del preflight (2026-10-09)

Base f0f5224118886cb21a5c8024ccfd1728bce66391. Preflight readonly amplía catalogo:
grupo NOLOGIN/NOINHERIT sin privilegios amplios, membresias superiores ni propiedad
de relaciones; app_user sin membresia administrativa; login sin ADMIN OPTION;
login/grupo sin CREATE sobre public. Tres tablas globales con RLS y SELECT/INSERT,
UPDATE solo selector; sin DELETE/TRUNCATE/REFERENCES/TRIGGER ni UPDATE por columna
en publicaciones/eventos. Rechaza permisos efectivos de login sobre relaciones
public y del grupo fuera de las tres admitidas, incluidos grants PUBLIC/por columna.
No consulta filas del dominio tenant. No repara permisos ni modifica configuracion.

Informe versionado report_version=1, permissions_verified=true con alcance explicito
public_relations_and_role_flags solo al completar chequeos. environment_identity_verified
/migration_head_verified/personal_authentication_verified/activation_authorized=false:
no acredita destino, head operativo, JWT ni decision de activacion. No cubre todo
privilegio de funciones/secuencias/otros schemas ni equivalencia del cuerpo de RLS;
requiere revisar migraciones/config/entorno y ejecutar matriz HTTP por separado.

Ocho PostgreSQL nuevas: grants efectivos SELECT tabla/columna al grupo/login/PUBLIC
sobre tabla temporal vacia, ADMIN OPTION del login temporal y CREATE public del login.
Rechazos observados y objetos/grants eliminados por cleanup; canal normal vuelve a
superar chequeos. 31 focalizadas con canal y preflight anteriores: 3.26 s; formato/
diff correctos. No nueva suite completa; ultima 3654 §106. Sin migracion/grants
persistentes/credenciales reales ni ejecucion contra entorno operativo acreditado.

Proximo: completar expediente de destino/commit/head/login/staff/responsable y
registrar resultados del preflight/HTTP en entorno acordado. No ampliar privilegios
para hacer pasar el informe; corregir provision conforme contrato. Fuentes oficiales
complementarias/aceptacion real aun pendientes, activacion bloqueada. Ley reformada
base fija; M3-T1 EN PROGRESO integral. Sin commit/push.

## §111 — Expediente inicial y comprobacion de configuracion (2026-10-09)

Base limpia d57b2206b2ae432ae93e6a278e24483d4db1ece9. Se agrega
m3-t1-eipd-expediente-operativo.md con evidencia ejecutada: environment development,
hosts configurados loopback (sin inferir ubicacion fisica), EIPD_ADMIN_DATABASE_URL
ausente, preflight CLI exit 1/failed sin canal inicializado y head local b17d95c0286f
via mantenimiento readonly. No URLs/JWT/passwords impresos ni datos tenant consultados.
No provision de roles/perfiles/secreto/politica; sin fallback owner ni .env modificado.

Destino operativo solicitado al usuario, pendiente. Continuar provision depende
de destino acreditado y del expediente; no crear actor staff ni credenciales ficticias
para simular resultado operativo. No nueva suite; ultima completa 3654 §106,
focalizadas 31 §110. Diff correcto. Fuentes/aceptacion/provision pendientes;
activacion bloqueada, ley fija, M3-T1 EN PROGRESO. Sin commit/push.

## §112 — Seleccion de desarrollo local y accion de provision pendiente

Fecha 2026-10-09. Usuario elige local. Comprobaciones readonly: head b17d95c0286f,
canal EIPD ausente, eipd_backend_local inexistente; un superadmin contado sin identificar
ni modificar. Identidad staff solicitada sin secretos, pendiente. Accion concreta
preparada para login limitado y archivo privado externo al repo; revision automatica
la rechaza antes de ejecucion por falta de autorizacion explicita de persistencia.
No roles/secreto/archivo nuevos ni configuracion/politica modificados. Se pide
aprobacion de provision exacta, sin reintentar por alternativa. Solo documentacion;
ultima suite completa 3654 §106, focalizadas 31 §110. EN PROGRESO; activacion bloqueada.

## §113 — Canal tecnico local provisionado y preflight ejecutado

Fecha 2026-10-09. Autorizacion explicita del usuario tras §112. Login
 eipd_backend_local limitado, miembro solo eipd_policy_admin; credencial nueva
fuera del repo en ~/.config/cumpleia-local-eipd/admin.env 0600, sin valor impreso.
.env habitual/perfiles/politicas intactos. Carga solo en proceso de diagnostico.
Preflight local pending_selector, codigo logico 2 confirmado: canal/permisos/auditoria
coherentes, selector ausente, sin bootstrap. No acredita backend HTTP/JWT personal
ni provision integral. Staff solicitado pendiente; proximo vincular identidad real
y validar proceso HTTP configurado. Sin nueva suite; ultima 3654 §106, focalizadas
31 §110. Ley fija, EN PROGRESO, activacion bloqueada. Sin commit/push.

## §114 — Staff indicado y verificacion pendiente (2026-10-09)

Usuario informa correo de staff (no se reproduce PII en evidencia versionada).
Consulta parametrizada readonly: exactamente un perfil local, auth_user_id presente,
is_superadmin=false. No se modifica ni promueve perfil. Configuracion de autenticacion
presente; GET administrativo readonly del usuario por ID no se completa: ConnectError
en etapa auth_request. No respuesta de Supabase ni identidad externa/JWT acreditados.
Metodo GET consultado en fuente primaria de Supabase auth-js GoTrueAdminApi.
No secretos/URL/JWT/respuestas privadas impresos, ni mensajes enviados al usuario.

Pendientes: identificador de Supabase aportado por usuario para contrastar el vinculo,
autorizacion explicita de superadmin global del perfil local indicado, y humo JWT/HTTP
con proceso configurado. Permiso global permite acceso a organizaciones del entorno
local; elegir staff/correo no se interpreta como promocion autorizada. Canal tecnico
§113 disponible, selector ausente; sin nuevas politicas ni activacion. Sin nueva suite;
ultima 3654 §106/focalizadas 31 §110. EN PROGRESO; sin commit/push.

## §115 — Superadmin local explicitamente autorizado (2026-10-09)

Usuario autoriza superadmin global en base local para el perfil del correo indicado.
Mantenimiento verifica entorno development/host loopback, exactamente un perfil y
vinculo auth_user_id presente, toma FOR UPDATE y cambia solo is_superadmin=true
por id/auth_user_id existentes. Commit realizado y lectura posterior confirma true.
No se crea usuario, cambia email/sub ni modifica Supabase. PII/IDs no se imprimen
ni se incorporan a evidencia versionada. Alcance: organizaciones de base local.

Autoridad local provisionada por autorizacion humana; identidad externa de Supabase
/JWT personal sigue sin verificar (ConnectError previo; User UID aun pendiente).
No declarar humo HTTP aprobado ni sources_status/aceptacion/activacion habilitadas.
Canal tecnico §113 permanece; selector/politica sin cambios. No nueva suite ni
migracion; ultima 3654 §106, focalizadas 31 §110. Proximo contrastar User UID y
completar autenticacion/proceso HTTP configurado. EN PROGRESO; sin commit/push.

## §116 — UID contrastado y rechazo HTTP anonimo (2026-10-09)

Usuario aporta User UID de Supabase; consulta local readonly confirma un perfil
unico por correo, auth_user_id coincide exactamente con UID aportado y superadmin=true.
No se reproduce PII/UID en evidencia versionada. Este contraste usa dato aportado
por usuario y base local; no acredita respuesta externa de Supabase ni JWT firmado.

Backend local 127.0.0.1:8000 responde health 200; OpenAPI 200 registra POST
/admin/eipd/publications y /admin/eipd/selections. Ambas solicitudes sin token
(cuerpo vacio) -> 401. No filas/identidad/canal de DB mutados. Prueba negativa
real acreditada; no acredita SHA del proceso, carga del secreto EIPD o prueba positiva.

Pendiente proceso HTTP configurado con secreto privado del canal y solicitud
personal JWT validada por issuer/JWKS, seguida de publicacion/seleccion deshabilitada
y auditoria/retirada. No solicitar tokens/passwords por chat; usar inicio de sesion
local y canal seguro. ConnectError previo en consulta de autenticacion externa
no se considera resuelto por el contraste UID. Canal tecnico y autoridad local
estan provisionados; selector ausente. Fuentes/aceptacion pendientes, activacion
bloqueada; EN PROGRESO. Sin nueva suite ni commit/push.

## §117 — Proceso local configurado e identidad externa verificada (2026-10-09)

Base limpia 6474873b2cd0eb0a9e941322cbca04bb9e59d365. Archivo privado externo
presente, modo 0600 validado; carga solo en memoria de nuevo proceso local,
DEBUG=false, access_log=false, uvicorn en 127.0.0.1:8001. Proceso de validacion
separado del backend existente 8000; .env habitual sin cambios y secreto no impreso.
Sesión de herramienta que mantiene proceso: 30969 (referencia efimera, no garantiza
persistencia tras cierre/reinicio de herramienta). No despliegue remoto ni servicio
persistente del sistema; verificar salud antes de cada paso.

DNS de proyecto de autenticacion accesible y JWKS publico GET 200. Reintento GET
administrativo readonly de usuario Supabase -> 200; id/correo coinciden con perfil
local y dato humano aportado, email confirmado, superadmin local true. ConnectError
anterior ya no se reproduce en estas consultas. No se exponen PII/claves/respuestas.
Esto acredita identidad externa por consulta administrativa, no JWT de sesion personal.

Proceso nuevo health 200; POST ambas rutas EIPD sin token -> 401. No se publica ni
selecciona politica ni modifica perfil. Credencial privada del canal cargada por
proceso iniciado; pool inicializacion diferida, prueba readonly del canal acreditada
§113. No inferir solicitud autenticada por salud o rechazo anonimo.

Se intento inspeccion de navegador mediante herramienta CUA; inicializacion falla
por helper/setup refresh, sin estado de navegador disponible. Habilidad instalada
leida (computer-use 26.1002.52244); ruta anterior del catalogo ausente, encontrada
mediante busqueda local. No bypass de automatizacion ni extraccion de tokens.
Pendiente sesion autentica del usuario por canal local seguro. No pedir contrasena/
JWT por chat ni generar token sintetico como evidencia operacional.

Proximo: solicitud autenticada con JWT real del staff contra proceso configurado,
politica deshabilitada y auditoria; requiere acceso a sesion del usuario. Fuentes/
aceptacion/provision integral siguen pendientes; activacion bloqueada. Sin nueva
suite, ultima completa 3654 §106 y focalizadas 31 §110. M3-T1 EN PROGRESO.
Sin commit/push.

## 2026-10-09 — M3-T1 §118: comprobacion local de acceso personal preparada

Se incorpora GET /admin/eipd/status, protegido por el canal administrativo y la
autoridad personal existentes. Devuelve solo un resumen de acceso y presencia de
selector; activation_authorized permanece false. No publica, selecciona ni crea
politicas. La pantalla de desarrollo /admin/eipd-validation utiliza la sesion
Supabase del navegador sin mostrar ni persistir el token y consulta el backend
local 127.0.0.1:8001.

Validacion: 40 pruebas focalizadas de API aprobadas; Black/Ruff, type-check y lint
del frontend aprobados. HTTP real sin sesion: pantalla redirige al login (307),
GET de estado rechaza sin token (401). Esto no acredita JWT personal real: queda
pendiente iniciar sesion, abrir la pantalla y pulsar Comprobar acceso. Los procesos
locales son efimeros; backend anterior 8000 permanece. No cambios de credenciales,
perfil ni politicas. Ultima suite completa: 3654 pruebas (§106).

La Ley 21.719 / 19.628 reformada permanece como base fija. Fuentes complementarias,
aceptacion y validacion operacional integral pendientes. M3-T1 EN PROGRESO;
activacion excepcional bloqueada. Sin commit/push en este paso.

## 2026-10-09 — M3-T1 §119: consulta personal del registro operativo

Se incorpora GET /admin/eipd/audit con AdminDb y el contrato cerrado de snapshot
validado. La lectura conserva la comprobacion JWT, autoridad global y canal
restringido; errores de coherencia devuelven 409. No crea ni modifica politicas.
La pantalla local incorpora Consultar registro y muestra revision vigente,
numero de publicaciones/selecciones y referencias/estado de las politicas.
Sin selector la revision mostrada es cero; no se inventa una seleccion inicial.

Pruebas API y concurrencia: 54 aprobadas en 12.91 s. Nuevos casos cubren lectura
sin escrituras antes/despues de publicar y seleccionar, rechazo sin JWT y rechazo
tenant. Black/Ruff y type-check/lint frontend aprobados. Backend de validacion
reiniciado; GET real /audit sin token devuelve 401. No se acredita consulta real
con sesion personal hasta el resultado aportado por el usuario. La comprobacion
de acceso personal §118 ya fue confirmada mediante captura.

Proximo: consultar el registro con la sesion personal; luego preparar publicacion
y seleccion deshabilitadas con revision vigente y evidencia operacional.
No hubo publicaciones/selecciones operacionales en este paso. Ley fija, fuentes
complementarias/aceptacion pendientes; M3-T1 EN PROGRESO y activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §120: publicacion local deshabilitada preparada

GET /admin/eipd/publication-draft protegido por AdminDb devuelve la propuesta fija
resolve_eipd_gate_policy_v1, sin escrituras ni aceptacion: fuentes pendientes,
aceptacion pendiente, sin responsables/evidencia de aceptacion inventados y
activacion deshabilitada. Motivo operacional y referencia documental explicitos.

La pantalla de desarrollo prepara la propuesta tras consultar el snapshot actual,
evita ofrecer publicacion si su referencia ya existe y muestra que el registro
local es permanente. Solo Publicar politica deshabilitada solicita POST existente
con JWT personal. Tras 201 consulta nuevamente la auditoria y contrasta ID/hash y
estado deshabilitado. No selecciona ni activa; no hay reintentos automaticos.
Ante resultado incierto requiere consultar el registro, sin repetir a ciegas.

56 pruebas API/concurrencia aprobadas en 13.27 s; casos nuevos cubren propuesta
readonly, JWT/autoridad, publicacion seguida de auditoria, selector ausente y
rechazo de duplicados sin cambios. Black/Ruff y type-check/lint frontend aprobados.
Proceso local 8001 actualizado; GET propuesta sin token devuelve 401. La publicacion
operacional con sesion personal sigue pendiente: no se ejecuta ni se acredita por
estas pruebas. No se cambian credenciales, perfiles ni el backend previo 8000.

Proximo: usuario prepara/revisa/publica politica deshabilitada en pantalla y aporta
resultado; luego verificar auditoria y preparar seleccion con revision vigente.
Ley 21.719 / 19.628 reformada fija; fuentes complementarias/aceptacion pendientes.
M3-T1 EN PROGRESO; activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §121: seleccion local deshabilitada preparada

La pantalla prepara la seleccion tras consultar GET /audit, toma publication_id,
hash y revision vigentes y muestra referencia/revision antes del boton explicito.
Solo admite la publicacion fija deshabilitada y no ofrece reseleccion de una
publicacion ya presente en eventos. POST /selections existente mantiene autoridad,
control optimista de revision y rechazo de politica habilitada. Tras 201 se consulta
el snapshot y se contrastan evento, hash, revision y selector, conservando estado
deshabilitado. No hay reintentos automaticos ante 409 o respuesta incierta.
La seleccion operacional personal sigue pendiente; no se ejecuta por este paso.

Type-check/lint frontend y formato aprobados. La primera suite en base operacional
produjo 52 aprobadas/4 fallidas porque los casos esperan registro vacio y ya existe
la publicacion personal. Se creo cumpleia_eipd_tests_20261009 vacia, solo esquema
migrado a head, funciones auth y permisos app_user equivalentes; sin copiar datos
personales ni cambiar URLs persistentes. Suite focalizada API/concurrencia en esa
base: 56 aprobadas en 12.15 s. Usar esa base aislada en siguientes suites; no ejecutar
pruebas de escritura contra el registro operacional. La base de pruebas queda local.

Comprobacion readonly posterior del snapshot operacional: 1 publicacion deshabilitada,
0 selecciones y sin selector (revision 0); registro personal preservado. No infiere
solicitud HTTP personal de esta consulta tecnica. Fuentes complementarias y aceptacion
integral pendientes; ley fija, M3-T1 EN PROGRESO y activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §122: cierre delimitado de validacion local

La secuencia acceso personal -> consulta -> publicacion -> seleccion deshabilitada
queda documentada por capturas aportadas por el usuario (§118–121), y snapshot
tecnico posterior readonly coherente. Este cierre solo cubre esa secuencia local;
no marca DONE del modulo ni aceptacion juridica ni puesta en produccion.

Nuevo preflight readonly real: status ok, salida 0, channel_verified y
permissions_verified true, audit_coherent true, selector_present true y revision 1;
activation_authorized false. Las banderas de identidad del entorno/head/autenticacion
personal del CLI permanecen false por alcance limitado de esa herramienta, sin
sustituir la evidencia personal previa. Head comprobado separadamente por lectura
de alembic_version: b17d95c0286f. Sin escrituras ni nueva suite en este checkpoint;
ultima focalizada: 56 aprobadas en base aislada §121, ultima completa: 3654 §106.

Pendientes separados: (1) asegurar ejecucion de futuras suites solo en base aislada,
(2) probar rotacion/retiro del canal y recuperacion local preservando auditoria,
(3) verificar fuentes complementarias y registrar aceptacion real con responsables,
(4) resolver regimenes especiales/representacion y criterios del alcance integral.
No se identifica una fuente nueva ni se cambia una regla legal en esta revision.
Ley 21.719/19.628 reformada fija. M3-T1 EN PROGRESO; activacion EIPD bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §123: ejecutor focalizado de pruebas aisladas

backend/scripts/run_eipd_tests.py proporciona python -m scripts.run_eipd_tests.
Deriva ambas URLs solo en entorno hijo hacia cumpleia_eipd_tests_20261009, mantiene
roles separados y exige development, hosts loopback iguales, sin parametros URL,
runtime app_user. Antes de pytest consulta readonly current_database/head y registro
EIPD vacio, confirma runtime sin superuser/BYPASSRLS. Rechaza destino/head/roles/estado
incompatibles con salida logica 2 y mensaje sin secretos. No crea/borra DB ni copia
datos; no imprime URLs. Elimina overrides heredados de pytest y credenciales Supabase/
canal administrativo; usa emisor sintetico de pruebas y targets fijos sin argumentos.

Guardas probadas: URLs a base fija y roles intactos, entorno padre sin cambios,
rechazo remoto/query/produccion, runtime owner/destinos distintos, DB/head/registro
no vacio y privilegios runtime incompatibles. Ejecucion por el runner: 60 aprobadas
en 9.45 s (56 API/concurrencia + 4 guardas); Black/Ruff aprobados. Invocacion con
argumento extra bloqueada antes de pytest. Sin nuevas escrituras operacionales ni
cambios de perfil/secretos/backend. No suite completa nueva.

Alcance: protege las invocaciones mediante este ejecutor; pytest directo sigue
resolviendo DATABASE_URL habitual y no queda protegido por este wrapper. Usar este
punto de entrada para la suite EIPD focalizada, sin ejecutar pytest directo contra
la base operacional. Cambios de head requieren revision explicita de la guarda.
Siguiente: preparar ensayo de rotacion/retiro y recuperacion local preservando
historial. Fuentes/aceptacion y alcance integral pendientes; ley fija, M3-T1 EN
PROGRESO y activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §124: ensayo aislado de rotacion/retiro y recuperacion

Se agregan tres pruebas PostgreSQL de ciclo de vida al ejecutor fijo, sobre login
aleatorio temporal de fixture y base aislada. Rotacion: clave antigua rechazada en
conexiones nuevas (28P01), conexion previa sobrevive, pool se dispone y clave nueva
permite recuperar el canal; rol local e identidad se limpian tras rollback. NOLOGIN:
conexion nueva rechazada (28000), conexion previa sigue viva pero _prepare_channel
rechaza con 503; restaurar LOGIN y renovar pool recupera. Retiro de membresia:
conexion caliente rechazada por guarda 503, restauracion recupera el canal.

63 pruebas focalizadas aprobadas en 13.03 s; Black/Ruff aprobados. El snapshot de
pruebas permanece igual antes/despues de cada ensayo (registro inicialmente vacio
por guarda del runner); no se extrapola a prueba de historial no vacio. Fixtures
restauran flags/membresia cuando procede, disponen pools y eliminan solo su rol
aleatorio. No cambian login/secreto/pool operacional ni perfil personal.
Preflight readonly posterior del canal original: ok, auditoria coherente, selector
revision 1 y activation_authorized false. No rotacion/retiro real del canal de usuario
ni actualizacion de su archivo privado en este checkpoint.

Pendiente operacional: ensayo coordinado sobre canal provisionado, renovacion de
procesos/conexiones y referencia de recuperacion segura con historial real. Ensayo
tecnico aislado no acredita ese cambio. Fuentes/aceptacion y alcance integral siguen
pendientes; ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §125: rotacion real local preparada

Plan concreto en docs/project/m3-t1-eipd-plan-rotacion-local.md. Lectura previa:
archivo externo 0600, destino development/loopback y login dedicado esperado;
preflight ok, revision 1, head b17d95c0286f. Dos conexiones idle durante diagnostico
(incluida la propia); pool del diagnostico dispuesto al terminar. Requerir nueva
comprobacion de drenaje antes de ejecutar. No se cambia clave/archivo/rol/proceso.

Secuencia preparada: snapshot previo, detener solo validacion 8001 y drenar,
reemplazo privado/recuperacion 0600, cambio de clave y sustitucion atomica con
recuperacion ante fallo, conexiones nuevas antigua rechazada/nueva aceptada,
comparacion exacta de auditoria, reinicio y comprobacion personal. Backend 8000 y
perfil permanecen fuera del cambio. Rotacion REAL pendiente, no acreditada por
ensayo aislado §124 ni por este plan. Sin nueva suite; ultima focalizada 63 §124.
Fuentes/aceptacion y alcance integral pendientes; ley fija, M3-T1 EN PROGRESO y
activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §126: rotacion real local ejecutada

Se detuvo el proceso propio de validacion 8001 y se comprobo ausencia de conexiones
del login dedicado antes de alterar password. Destino development/loopback, login
esperado, archivo privado 0600 y head b17d95c0286f verificados. Snapshot previo
validado: 1 publicacion deshabilitada, 1 seleccion, revision 1.

Nueva clave aleatoria en memoria, copia privada de recuperacion 0600 externa al
repo y reemplazo privado preparado; cambio password de eipd_backend_local y
sustitucion atomica de admin.env. Conexion NUEVA con credencial anterior rechazada;
nueva credencial: preflight ok. Snapshot completo posterior exactamente igual al
previo; no cambios de perfiles, permisos, publicaciones, eventos ni selector.

Proceso propio 8001 reiniciado con nuevo secreto en memoria, DEBUG=false y sin
access log. GET /admin/eipd/status sin token -> 401. Backend previo 8000 fuera del
cambio. No secretos ni PII en documentos/logs/repositorio. Copia privada de
recuperacion conservada hasta confirmar sesion personal; retirada aun pendiente.
No se afirma validacion personal tras reinicio a partir del diagnostico tecnico.

Proximo: usuario Comprobar acceso y Consultar registro en pantalla con sesion real,
confirmar revision 1/politica deshabilitada y luego retirar copia privada anterior.
No suite nueva (ultima 63 §124). Fuentes/aceptacion y alcance integral pendientes;
ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §127: retiro reversible del canal real y recuperacion

Proceso propio 8001 detenido y ausencia de sesiones dedicadas comprobada tras
snapshot previo validado. Login local eipd_backend_local cambiado temporalmente
a NOLOGIN: conexion NUEVA con credencial actual rechazada, SQLSTATE 28000.
LOGIN restaurado en finally; nueva conexion y preflight ok. Snapshot completo
posterior exactamente igual al previo, selector revision 1. No cambio de password,
archivo privado, membresias, perfiles, publicaciones, eventos ni selector.

Proceso 8001 reiniciado con credencial privada actual, DEBUG=false y sin access log;
GET /status sin token -> 401. Backend 8000 fuera del ensayo. Comprobacion personal
posterior al reinicio pendiente. No constituye retiro definitivo del canal ni
revocacion instantanea de transacciones ya autorizadas; se dreno antes del cambio.
No nueva suite; ultima 63 §124. Ley fija, fuentes/aceptacion y alcance integral
pendientes; M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §128: siguiente brecha funcional delimitada

Tras cerrar ciclo local del canal, se revisa codigo actual: salud/biometria por
consentimiento ya tienen evaluadores; investigacion_art16quinquies aun deriva a
validador_no_implementado. Se elige preparacion documental inicial para datos no
sensibles/adultos con LIA vigente, decision de producto sin atribuirla como limite
juridico universal. Fuente primaria BCN Ley 21.719/art16quinquies consultada.

Diseno, completitud/aplicabilidad, integracion por pasos y criterios de aceptacion
en docs/project/m3-t1-investigacion-diseno.md. Proximo: schema y evaluador puro,
sin persistir ni levantar bloqueos hasta integrar/aceptar. Sin cambios de codigo,
politicas ni secretos; sin nueva suite. Ley fija, M3-T1 EN PROGRESO y activacion
EIPD bloqueada. Sin commit/push.

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
