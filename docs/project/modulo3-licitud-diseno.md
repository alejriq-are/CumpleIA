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

El algoritmo concreto y sus tests se fijarán en M3-T1.

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