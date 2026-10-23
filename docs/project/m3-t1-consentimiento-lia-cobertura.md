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

Las plantillas originales no se encontraron en los archivos disponibles de esta
sesión: sources/ está vacío y docs/fuentes contiene las leyes y material CCS.
Esta revisión confirma el acuerdo registrado, pero no certifica traslado íntegro
campo por campo desde esos adjuntos originales.

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
   versión aplicable, identificando aparte las recomendaciones metodológicas. Cotejar
   con las plantillas originales cuando estén disponibles. Coordinar la bitácora
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
