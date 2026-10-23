# Cobertura de consentimiento y LIA en el recorrido de licitud

Revisión: 23/10/2026. Base inspeccionada: 7325bff, rama
feature/m3-t1-licitud-persistencia. Auditoría de código y diseño; sin modificar
el expediente del usuario ni implementar nuevos formularios en esta revisión.

## Resultado

Cobertura parcial. El servidor dispone de contratos, persistencia y evaluadores
para consentimiento y LIA; el recorrido visible no permite completarlos íntegramente.
La presencia de nueve textos LIA no equivale a un formulario completo ni a una
validación jurídica. Consentimiento solo ofrece selección de base y fundamento.

## Acuerdo y fuentes

[Diseño del módulo](modulo3-licitud-diseno.md), secciones 2, 17 y 18:
CONSENTIMIENTO.md y LIA.xlsx/LIA.md son referencias comparadas de estructura y UX;
las reglas se adaptan a Chile. Se acordó checklist estructurado para consentimiento
y evaluación estructurada para interés legítimo.

El usuario aportó los originales ES - DESCARGABLE CONSENTIMIENTO.xlsx y
ES - DESCARGABLE LIA.xlsx el 23/10/2026. Se leyeron todas sus hojas y celdas
con contenido, sin modificar los archivos. Ambos incluyen Introducción y una hoja
operativa con columnas Preguntas, Respuestas y Comentarios. El cotejo siguiente
cubre las 19 preguntas operativas de consentimiento y las 31 de LIA, más sus
estados/conclusiones. Reemplaza la limitación anterior de originales no disponibles.
Las celdas comerciales de introducción/contacto no forman parte de los controles.

Identidad de fuentes originales:
- ES - DESCARGABLE CONSENTIMIENTO.xlsx: SHA-256 `f751ad4b0a0661038d93872f0683f09547dd3f83d3844150ea88f3f063eff3ad`.
- ES - DESCARGABLE LIA.xlsx: SHA-256 `60ae2ad591af5e8d3e0d901b2e2346227ab3fa5ab58da96d43d9a086579afb85`.

Las referencias a hojas/celdas siguientes identifican el criterio original. No
atribuyen al derecho chileno el texto europeo ni declaran validez jurídica automática.

Fuente oficial contrastada: [Ley 21.719, BCN](https://www.bcn.cl/leychile/navegar?i=1209272),
artículos 12 y 13 d), definición de consentimiento y deberes relacionados.
El régimen reformado tiene vigencia diferida al 01/12/2026; no presentarlo como
vigente al día de esta revisión. [Fecha de vigencia, BCN](https://www.bcn.cl/balance-legislativo/detalle/ficha_LEY_21719_2024-12-13).
Distinguir normativa vigente y preparación para la reforma en ayudas y revisión.
La ley no impone un formulario llamado LIA: su estructura es una herramienta de
documentación de CumpleIA y debe distinguir exigencias legales de metodología interna.

## Cobertura verificada

| Componente | Servidor | Pantalla actual | Brecha |
| --- | --- | --- | --- |
| Consentimiento | ConsentAssessmentV1: otorgante, mecanismo, 14 preguntas generales y 2 condicionales, comentarios, evidencias y notas; evaluador de aplicabilidad/preparación | Base propuesta y fundamento; sin editor consent_assessment | Conectar formulario completo, consulta y diagnóstico |
| LIA | LiaAssessmentV1: ocho grupos, respuestas y condiciones, análisis, salvaguardas y conclusión; contraste con contexto RAT | Nueve textos repartidos por los grupos; preserva campos previos no representados | Exponer respuestas y demás campos que exige el evaluador; no se puede completar desde los nueve textos solos |
| Evidencias | Consentimiento admite metadatos; anexos generales guardados por sección base, con versiones/hashes | Anexos disponibles, pero sin editor de evidencia de consentimiento ni enlace preciso por pregunta/control de ambas evaluaciones | Asociar referencia/versión de respaldo al punto evaluado y distinguir existencia de archivo de comprobación de contenido |
| Diagnóstico | Readiness evalúa consentimiento o LIA según base | El editor no ofrece un diagnóstico específico junto a sus preguntas | Mostrar pendientes y motivos en español con acceso al campo correspondiente |
| Consulta | Contratos y exportación conservan material | DossierDocumentView resume base/fundamento y solo nueve textos de LIA; no presenta checklist consentimiento | Vista legible completa y descarga que conserve todo el material |

Evidencia de código:
- backend/app/schemas/licitud.py: ConsentAssessmentV1 y LiaAssessmentV1, campos CREATE/PATCH/GET.
- backend/app/services/consentimiento.py y lia.py: controles de preparación.
- backend/app/services/licitud.py: integración de contratos y diagnóstico por base.
- frontend/components/licitud/LegalAssessmentEditor.tsx: selección/fundamento y nueve textos LIA.
- frontend/lib/licitud/lia-fields.ts: inventario de nueve campos editables.
- frontend/lib/api/licitud.ts: contrato del cliente sin consent_assessment.
- frontend/components/licitud/DossierDocumentView.tsx: consulta parcial.

## Incorporaciones necesarias

1. **Consentimiento condicional.** Al elegir Consentimiento, mostrar quién lo otorga,
   cómo se obtiene y las preguntas existentes, con Sí/No/Pendiente/No aplica solo
   donde corresponda. Cubrir libertad, información, finalidad específica, carácter
   previo, manifestación inequívoca/acción afirmativa, acreditación y revocación.
   Incluir condiciones de mandato y contexto contractual; no dar respuestas positivas
   por defecto. Conectar al contrato existente antes de crear un esquema alternativo.
2. **LIA completa.** Organizar interés/finalidad, necesidad y alternativas,
   naturaleza/alcance, expectativas, impactos, salvaguardas, transparencia/oposición
   y conclusión. Incluir titulares del interés, respuestas estructuradas, condiciones
   derivadas del RAT y fundamentos que hoy no se editan. No copiar escalas europeas
   como si fueran exigencias chilenas ni confundir la LIA con la valoración EIPD.
3. **Evidencia trazable.** Permitir aportar referencias, fecha, mecanismo y notas;
   enlazar anexos guardados con referencia y versión al control pertinente. Precisar
   qué se declara y qué fue comprobado. La mera carga de un PDF no valida su contenido.
4. **Diagnóstico y revisión.** Mostrar incompleto/requiere revisión/completo documental,
   motivos y campos pendientes con los evaluadores existentes. Separar guardado,
   preparación documental y revisión jurídica humana; completar no significa aprobación.
5. **Conservación y consulta.** Guardar/reabrir todos los campos, preservar información
   al cambiar de base, distinguir antecedentes previos y evitar pérdidas de campos
   fuera del editor. Mostrar checklist y LIA completos en Revisar documentos.
6. **Trazabilidad de criterios.** Mapear cada pregunta a fuente chilena/artículo y
   versión aplicable, identificando aparte las recomendaciones metodológicas. Usar
   el cotejo de originales incluido en este informe al implementar cada criterio. Coordinar la bitácora
   completa con LIC-AUD-001 sin darla por implementada en este formulario.

## Aceptación propuesta para implementación

- Consentimiento muestra su checklist y LIA muestra su evaluación; selección de
  otra base no crea ni elimina silenciosamente estas evaluaciones.
- Borradores incompletos se guardan sin declarar validez jurídica; pendientes y
  condiciones se explican sin forzar respuestas favorables.
- Guardar, recargar, cambiar de base y consultar/exportar conserva respuestas,
  fundamentos, referencias y versiones de anexos; permisos/RLS se mantienen.
- Pruebas negativas cubren respuestas omitidas/pendientes/desfavorables,
  No aplica improcedente, condiciones de mandato/contrato, cambios RAT y errores.
- Verificar recorrido con API/PostgreSQL aislado y roles de lectura/escritura;
  no modificar el expediente manual para completar artificialmente los controles.
- Revisión jurídica humana de redacción y mapeo normativo antes de presentar
  criterios como legalmente suficientes. EIPD y operación con datos reales bloqueadas.

## Verificación ejecutada

190 pruebas aprobadas: test_services_consentimiento.py, test_services_lia.py y
test_schemas_lia.py. Comprueban servicios/esquemas existentes; no prueban los
formularios ausentes, ni constituyen certificación de cumplimiento legal.

La captura del usuario confirma LIA oculta al elegir Consentimiento y fundamento
conservado. Ese cambio es temporal, sin guardar: falta recargar para recuperar
la base persistida Pendiente de definir. No guardar Consentimiento para esta prueba.

## Cotejo de los originales aportados

Cobertura significa correspondencia temática con el contrato existente, no un
control independiente ya disponible en la pantalla. Consentimiento no tiene editor;
sus respuestas generales agrupan varias buenas prácticas del original. Ninguna de
las 19 se considera resuelta en UX por existir un campo genérico en el servidor.
LIA tiene campos para la mayoría de los temas, pero su interfaz solo expone nueve
textos. No copiar automáticamente decisiones, recomendaciones o escalas del Excel.

### Consentimiento: hoja Checklist

| Celda original | Criterio resumido | Contrato actual relacionado | Adaptación/incorporación |
| --- | --- | --- | --- |
| A4 | Ausencia de obligación | `consentimiento_libre` | Desglosar voluntariedad y su fundamento. |
| A5 | Consecuencias de rechazar | `consentimiento_libre` | Documentar consecuencias reales de no consentir. |
| A6 | Separación de condiciones generales | `consentimiento_libre` | Control explícito de presentación separada. |
| A7 | Condicionamiento de contrato/servicio | `contexto_contrato_servicio; tratamiento_necesario_contrato_servicio` | Aplicar según contexto y necesidad; revisión del caso. |
| A8 | Presiones o influencias | `consentimiento_libre` | Control explícito y comentario/evidencia. |
| A9 | Desequilibrio de poder | `consentimiento_libre` | Analizar libertad real, especialmente en trabajadores; no convertir presencia de desequilibrio en conclusión automática. |
| A11 | Granularidad por finalidad | `consentimiento_especifico_finalidad; evaluación por finalidad RAT` | Separar finalidades y registrar evidencia de la elección. |
| A13 | Lenguaje comprensible | `consentimiento_informado` | Desglosar claridad y accesibilidad de la información. |
| A14 | Información de uso, responsable, finalidad y datos | `consentimiento_informado; evidence` | Identificar aviso y versión; adaptar contenido informativo chileno. |
| A15 | Información sobre revocación | `consentimiento_informado; revocacion_posible` | Documentar canal y cómo se comunica. |
| A17 | Acto afirmativo distinguible | `accion_afirmativa_clara; grant_method` | Registrar mecanismo y soporte verificable. |
| A18 | Ausencia de casillas premarcadas | `accion_afirmativa_clara` | Desglosar control del mecanismo. |
| A19 | Ausencia de aceptación por inacción | `voluntad_inequivoca; accion_afirmativa_clara` | No inferir consentimiento del silencio o de no desmarcar. |
| A20 | Consentimiento explícito frente a implícito | `voluntad_inequivoca; grant_method` | Adaptar al art. 12; no confundir inequívoco ordinario con requisitos de consentimiento expreso de regímenes especiales. |
| A22 | Facilidad y disponibilidad de revocación | `seis controles de revocación existentes` | Conservar condiciones chilenas; no exigir motivo para revocar. |
| A23 | Revocación en comunicaciones publicitarias | `revocacion_posible; evidence` | Condicional a marketing; revisar además normativa chilena de consumo aplicable antes de fijar reglas específicas. |
| A24 | Tratamiento tras revocación | `Sin control dedicado de efectos posteriores` | Adaptar: revisar cese, supresión y conservación según otras bases y obligaciones; no programar borrado automático universal. |
| A26 | Evidencia del consentimiento | `responsable_puede_acreditar; evidence` | Vincular referencia/versión, mecanismo y fecha al criterio evaluado. |
| A27 | Revisión periódica del consentimiento | `Sin control dedicado de seguimiento` | Recomendación, no caducidad periódica universal; revisar cambios de finalidad/contexto y plan de revisión. |

Checklist A29 es estado y A30 es conclusión. Derivar estado documental de respuestas,
pendientes y aplicabilidad. La conclusión requiere fundamento y revisión humana;
no sustituirla por una suma de casillas. Hay que decidir y versionar expresamente
cómo conservar el desglose adicional (presión, perjuicio, casillas, revocación y
seguimiento) sin introducir claves que el contrato no guarda o alterar históricos.
El diseño chileno agrega controles como carácter previo, representación y medios
específicos de revocación que no deben eliminarse por no ser una copia del Excel.

### LIA: hoja LIA

| Celda original | Criterio resumido | Contrato actual relacionado | Adaptación/incorporación |
| --- | --- | --- | --- |
| A4 | Finalidad explícita | `purpose_and_interest.purpose_description` | Contrastar con finalidad RAT. |
| A5 | Beneficio del responsable | `purpose_and_interest.controller_benefit` | Condicional al titular del interés. |
| A6 | Beneficio de terceros | `purpose_and_interest.third_party_benefit` | Condicional al titular del interés. |
| A7 | Beneficio público | `purpose_and_interest.public_benefit` | No confundir beneficio declarado con habilitación legal. |
| A8 | Importancia del interés | `purpose_and_interest.interest_importance` | Exponer análisis y fundamento. |
| A9 | Consecuencias de no tratar | `purpose_and_interest.consequences_without_processing` | Exponer análisis y alternativas. |
| A10 | Reglas aplicables | `purpose_and_interest.relevant_rules` | Sustituir referencias europeas por régimen chileno pertinente; fuente y versión. |
| A11 | Consideraciones éticas | `purpose_and_interest.ethical_considerations` | Identificar criterio metodológico y fundamento. |
| A13 | Contribución a la finalidad | `necessity.contributes_to_purpose; linked_to_interest` | Exponer respuesta estructurada. |
| A14 | Proporcionalidad | `necessity.proportionality_analysis` | Exponer análisis y fundamento. |
| A15 | Alternativa sin datos personales | `necessity.achievable_without_personal_data; alternatives_analysis` | Exponer respuesta y alternativa. |
| A16 | Menos datos o menor intrusión | `necessity.less_intrusive_alternative; fewer_data_possible; minimization_analysis` | Exponer respuestas y análisis. |
| A18 | Categorías especiales e infracciones | `RAT special_regimes; nature_and_scope.special_rules_description` | Clasificar según Chile; una LIA general no sustituye condiciones especiales de licitud. |
| A19 | Datos especialmente privados | `nature_and_scope.additional_risk_factors; impact.intrusion_analysis` | Distinguir percepción de privacidad de categoría sensible legal. |
| A20 | Infancia y vulnerabilidad | `RAT special_regimes; impact.vulnerable_people_impact` | Aplicar controles específicos, no extrapolar umbrales europeos. |
| A21 | Contexto profesional exclusivo | `nature_and_scope.exclusively_professional_context` | No inferir bajo riesgo solo por contexto laboral. |
| A23 | Relación previa | `reasonable_expectations.prior_relationship; relationship_description` | Exponer respuesta y condicional. |
| A24 | Cambio significativo de uso | `reasonable_expectations.significant_change_of_use` | Exponer respuesta y contexto. |
| A25 | Información en recogida directa | `reasonable_expectations.informed_at_direct_collection` | Aplicabilidad según origen RAT. |
| A26 | Información cuando el origen es tercero | `reasonable_expectations.third_party_information` | Revisar origen, deber informativo y compatibilidad jurídica; no presumir autorización por provenir de tercero. |
| A27 | Cambios tecnológicos o de contexto | `reasonable_expectations.technology_or_context_changes` | Registrar cambio y temporalidad en el análisis. |
| A28 | Previsibilidad de finalidad/método | `reasonable_expectations.foreseeable_purpose_and_method` | Exponer respuesta estructurada. |
| A29 | Tratamiento innovador | `reasonable_expectations.innovative_processing` | Exponer respuesta; innovación no equivale automáticamente a prohibición. |
| A30 | Evidencia de expectativas | `reasonable_expectations.expectations_evidence` | Referenciar soporte y versión. |
| A31 | Otros factores de expectativas | `reasonable_expectations.expectations_analysis` | Texto ya editable, completar contexto. |
| A33 | Efectos negativos | `impact.negative_effects; impact_analysis` | Exponer análisis completo. |
| A34 | Pérdida de control | `impact.loss_of_control` | Exponer respuesta estructurada. |
| A35 | Probabilidad y gravedad | `impact.likelihood; severity` | Exponer campos existentes; no equiparar automáticamente con matriz EIPD de cuatro niveles. |
| A36 | Oposición e intrusión | `impact.reasonable_opposition_likelihood; intrusion_analysis` | Exponer respuesta y análisis. |
| A37 | Explicación transparente | `impact.transparently_explainable` | Reformular como capacidad de explicar y justificar, no preferencia del responsable. |
| A38 | Salvaguardas | `safeguards.measures; safeguards_analysis` | Relacionar cada medida con el impacto que mitiga. |

LIA A40 es estado y A41 conclusión: corresponde a conclusion.decision y a su
fundamentación. Exponer los campos de conclusión del contrato, separando decisión
aportada, preparación documental y revisión jurídica. Transparencia/oposición es
un grupo propio del contrato chileno y debe conservarse aunque no figure con ese
título en el original. Los datos RAT existentes deben reutilizarse, mostrando origen
y pendientes sin rellenar respuestas favorables automáticamente.

### Ajustes normativos que requieren especial cuidado

- Checklist A24: la supresión posterior a revocación depende de las condiciones y
  excepciones aplicables; el art. 7 reformado contempla otra base legal y excepciones.
  [Fuente oficial chilena](https://www.bcn.cl/leychile/navegar?i=1209272).
- Checklist A20: redacción ordinaria debe documentar voluntad inequívoca y acto
  afirmativo; los supuestos de consentimiento expreso tienen controles propios.
- Checklist A27: revisión periódica es recomendación del original, no un plazo de
  caducidad general impuesto por Chile.
- LIA A18/A20: categorías y personas sujetas a protección especial requieren su
  régimen chileno; interés legítimo general no basta por sí solo.
- LIA A37: evaluar posibilidad de informar y explicar, no si al responsable le
  gustaría hacerlo. Mantener las garantías de información/oposición chilenas.

El alcance de LIC-FORM-001 incluye este cotejo. Implementación aún pendiente;
la entrega de los archivos resuelve la disponibilidad de referencias, no la brecha
funcional ni la revisión jurídica humana de la redacción final.
