import type { EipdReviewIssueV3 } from "@/lib/api/eipd-review";

const stages: Record<EipdReviewIssueV3["stage"], string> = {
  state: "Estado de la evaluación",
  rat: "Inventario de tratamiento",
  ordinary: "Base de licitud",
  research: "Investigación",
  frontier: "Alcance admitido",
  detection: "Detección EIPD",
  resolution: "Documento EIPD",
  sources: "Fuentes oficiales",
  activation: "Habilitación EIPD",
  review: "Revisión",
};
const messages: Record<string, string> = {
  campo_obligatorio: "Falta completar este campo.",
  pregunta_omitida: "Falta responder esta pregunta.",
  expediente_ausente: "Falta el documento de evaluación.",
  evidencia_ausente: "Falta aportar evidencia documental.",
  justificacion_ausente: "Falta justificar la base de licitud.",
  base_ausente: "Falta seleccionar una base de licitud.",
  contexto_rat_desactualizado: "El inventario cambió. Revisa y actualiza el contexto del borrador.",
  investigacion_confirmacion_bloqueada:
    "La confirmación del expediente de investigación permanece bloqueada.",
  metadatos_revision_no_disponibles:
    "No está disponible la identidad auditable del material que se revisaría.",
  asociacion_contexto_obsoleta:
    "El documento está vinculado a un contexto anterior. Revisa su vinculación.",
  gate_eipd_no_habilitado: "La habilitación EIPD está pendiente.",
  fuentes_oficiales_no_verificadas: "La verificación de fuentes oficiales está pendiente.",
  politica_investigacion_no_implementada:
    "La política para investigación sigue pendiente de implementación.",
};
const fields: Record<string, string> = {
  justification: "Justificación",
  legal_basis: "Base de licitud",
  scope: "Alcance",
  research_assessment: "Evaluación de investigación",
  eipd_resolution_assessment: "Documento EIPD",
  eipd_screening: "Detección EIPD",
  special_conditions: "Condiciones especiales",
  document_reference: "Referencia del documento",
  document_version: "Versión del documento",
  prepared_by: "Responsable de preparación",
  completed_on: "Fecha de elaboración",
  purpose_description: "Descripción de la finalidad",
  processing_operations: "Operaciones de tratamiento",
  public_interest_analysis: "Análisis de interés público",
  security_measures_analysis: "Medidas de seguridad",
  retention_analysis: "Conservación",
  official_sources: "Fuentes oficiales",
  evidence: "Evidencia",
  agency_consultation: "Consulta a la agencia",
  exclusive_use: "Uso exclusivo para la finalidad de investigación",
  exclusivity_controls_analysis: "Controles de uso exclusivo",
  quality_measures_analysis: "Medidas de calidad de los datos",
  measures_implemented: "Implementación de medidas",
  purpose_type: "Tipo de finalidad",
  publication_planned: "Publicación prevista",
  anonymization_method: "Método de anonimización",
  anonymization_analysis: "Análisis de anonimización",
  anonymization_evidence: "Evidencia de anonimización",
  data_category_codes: "Categorías de datos",
  data_subject_codes: "Categorías de titulares",
  processing_context: "Contexto del tratamiento",
  technologies_description: "Tecnologías utilizadas",
  exceptions_coverage_analysis: "Análisis de excepciones",
  necessity_analysis: "Análisis de necesidad",
  proportionality_analysis: "Análisis de proporcionalidad",
  minimization_analysis: "Análisis de minimización",
  necessary_for_purpose: "Necesidad para la finalidad",
  proportionate_processing: "Proporcionalidad del tratamiento",
  minimization_addressed: "Minimización de datos",
  performed_before_processing: "Evaluación previa al tratamiento",
  prior_assessment_analysis: "Análisis de la evaluación previa",
  risks: "Riesgos",
  measures: "Medidas",
  residual_risk_summary: "Resumen del riesgo residual",
  residual_risk_rationale: "Fundamento del riesgo residual",
  residual_risk_level: "Nivel de riesgo residual",
  limitations_analysis: "Limitaciones",
  follow_up_plan: "Plan de seguimiento",
  report_reference: "Referencia del informe",
  notes: "Notas",
  assessment: "Evaluación",
  context_binding: "Vinculación al contexto",
  context_hash: "Identidad del contexto",
  document_hash: "Identidad del documento",
  research_material_hash: "Identidad del material de investigación",
  status: "Estado",
  rat_context_hash: "Identidad del inventario",
  rat_context_snapshot: "Contexto del inventario",
  organization_role: "Rol de la organización",
  lia_assessment: "Evaluación de interés legítimo",
  consent_assessment: "Evaluación de consentimiento",
  contract_assessment: "Evaluación contractual",
  legal_obligation_assessment: "Evaluación de obligación legal",
  sensitive_consent_assessment: "Consentimiento para datos sensibles",
  sensitive_rights_exception_assessment: "Excepción para datos sensibles",
  biometric_rights_exception_assessment: "Excepción para datos biométricos",
  health_assessment: "Evaluación de datos de salud",
  biometric_assessment: "Evaluación de datos biométricos",
  geolocation_assessment: "Evaluación de geolocalización",
  economic_obligations_assessment: "Evaluación de obligaciones económicas",
  rights_defense_assessment: "Evaluación de defensa de derechos",
  conclusion: "Conclusión",
  balancing_summary: "Resumen de ponderación",
  decision: "Decisión",
  identified_interest: "Interés identificado",
  necessity_and_proportionality_result: "Resultado de necesidad y proporcionalidad",
  main_impacts: "Impactos principales",
  relevant_safeguards: "Salvaguardas relevantes",
  rights_protection_reasoning: "Fundamento de protección de derechos",
  purpose_and_interest: "Finalidad e interés",
  legitimate_interest: "Interés legítimo",
  interest_holder: "Titular del interés",
  controller_benefit: "Beneficio del responsable",
  third_party_benefit: "Beneficio de terceros",
  public_benefit: "Beneficio público",
  interest_importance: "Importancia del interés",
  consequences_without_processing: "Consecuencias de no realizar el tratamiento",
  relevant_rules: "Normas relevantes",
  ethical_considerations: "Consideraciones éticas",
  necessity: "Necesidad",
  contributes_to_purpose: "Contribución a la finalidad",
  linked_to_interest: "Relación con el interés",
  achievable_without_personal_data: "Posibilidad de cumplir la finalidad sin datos personales",
  less_intrusive_alternative: "Alternativa menos intrusiva",
  fewer_data_possible: "Posibilidad de utilizar menos datos",
  categories_necessary_and_relevant: "Necesidad y pertinencia de las categorías",
  alternatives_analysis: "Análisis de alternativas",
  nature_and_scope: "Naturaleza y alcance",
  exclusively_professional_context: "Contexto exclusivamente profesional",
  volume_and_scope: "Volumen y alcance",
  special_rules_description: "Descripción de reglas especiales",
  additional_risk_factors: "Factores de riesgo adicionales",
  reasonable_expectations: "Expectativas razonables",
  prior_relationship: "Relación previa",
  relationship_description: "Descripción de la relación",
  significant_change_of_use: "Cambio significativo de uso",
  informed_at_direct_collection: "Información al recopilar los datos directamente",
  third_party_information: "Información procedente de terceros",
  technology_or_context_changes: "Cambios de tecnología o contexto",
  foreseeable_purpose_and_method: "Previsibilidad de la finalidad y el método",
  innovative_processing: "Tratamiento innovador",
  expectations_evidence: "Evidencia de expectativas",
  expectations_analysis: "Análisis de expectativas",
  impact: "Impacto",
  negative_effects: "Efectos negativos",
  severity: "Gravedad",
  likelihood: "Probabilidad",
  loss_of_control: "Pérdida de control",
  intrusion_analysis: "Análisis de intrusión",
  reasonable_opposition_likelihood: "Probabilidad de oposición razonable",
  rights_and_freedoms_analysis: "Análisis de derechos y libertades",
  vulnerable_people_impact: "Impacto en personas vulnerables",
  transparently_explainable: "Posibilidad de explicar el tratamiento con transparencia",
  relevant_unmitigated_impacts: "Impactos relevantes sin mitigar",
  impact_analysis: "Análisis de impacto",
  safeguards: "Salvaguardas",
  description: "Descripción",
  mitigated_impact: "Impacto mitigado",
  safeguards_analysis: "Análisis de salvaguardas",
  transparency_and_opposition: "Transparencia y oposición",
  information_method: "Medio de información",
  interest_communication: "Comunicación del interés",
  opposition_channel: "Canal de oposición",
  opposition_procedure: "Procedimiento de oposición",
  responsible_area: "Área responsable",
  answer: "Respuesta",
  comment: "Comentario",
  acceptance_status: "Estado de aceptación",
  analysis: "Análisis",
  answers: "Respuestas",
  applicability_analysis: "Análisis de aplicabilidad",
  checked_on: "Fecha de verificación",
  conditions: "Condiciones",
  declarations: "Declaraciones",
  eipd_gate: "Habilitación EIPD",
  policy: "Política",
  routes: "Rutas de evaluación",
  sources: "Fuentes",
  datos_protegidos_excepcion_consentimiento: "Datos protegidos por una excepción al consentimiento",
  evaluacion_sistematica_automatizada_efectos_significativos:
    "Evaluación sistemática automatizada con efectos significativos",
  monitoreo_sistematico_zona_publica: "Monitoreo sistemático de zonas públicas",
  probable_alto_riesgo_contextual: "Probable alto riesgo según el contexto",
  tratamiento_masivo_o_gran_escala: "Tratamiento masivo o a gran escala",
  latest_review: "Última revisión",
  latest_review_context_metadata: "Identidad del material de la última revisión",
};
const categories: Record<EipdReviewIssueV3["category"], string> = {
  incompleto: "Incompleto",
  requiere_revision: "Requiere revisión",
  pendiente_revision: "Revisión pendiente",
  supuesto_declarado: "Supuesto declarado",
};
function fieldLabel(field: string) {
  return field
    .split(".")
    .map(
      (part) =>
        fields[part] ??
        (/^\d+$/.test(part) ? `Elemento ${Number(part) + 1}` : "Campo pendiente de identificar")
    )
    .join(" › ");
}
export function EipdReviewIssues({ issues }: { issues: EipdReviewIssueV3[] }) {
  const groups = new Map<
    EipdReviewIssueV3["stage"],
    Map<string, { issue: EipdReviewIssueV3; count: number }>
  >();
  for (const issue of issues) {
    const group = groups.get(issue.stage) ?? new Map();
    groups.set(issue.stage, group);
    const key = JSON.stringify([issue.field, issue.code, issue.category, issue.question_id]);
    const item = group.get(key);
    if (item) item.count += 1;
    else group.set(key, { issue, count: 1 });
  }
  return (
    <div className="mt-3 space-y-3 text-sm">
      <p>{issues.length} motivos informados.</p>
      <p className="text-gray-600">
        Despliega un tema para revisar sus motivos. Las repeticiones idénticas se agrupan.
      </p>
      {Array.from(groups, ([stage, items]) => (
        <details key={stage} className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <summary className="cursor-pointer font-semibold text-gray-900">
            {stages[stage]} — {items.size}{" "}
            {items.size === 1 ? "motivo distinto" : "motivos distintos"}
          </summary>
          <ul className="mt-4 list-none space-y-3">
            {Array.from(items, ([key, { issue, count }]) => (
              <li
                key={key}
                className="min-w-0 space-y-2 rounded-lg border border-gray-200 bg-white p-4"
              >
                <p>
                  {messages[issue.code] ??
                    "Hay un motivo pendiente de revisión. Consulta su detalle."}
                </p>
                <p className="break-words text-gray-600">Campo: {fieldLabel(issue.field)}</p>
                {issue.question_id !== null && (
                  <p className="break-words">
                    Pregunta: {fields[issue.question_id] ?? "Pregunta pendiente de identificar"}
                  </p>
                )}
                {count > 1 && (
                  <p className="text-gray-600">Informado {count} veces por el diagnóstico.</p>
                )}
                <details className="mt-2 break-words rounded-md bg-gray-50 p-3 text-gray-700">
                  <summary className="cursor-pointer font-medium text-blue-800">
                    Detalle del diagnóstico
                  </summary>
                  <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-3 sm:grid-cols-[9rem_minmax(0,1fr)]">
                    <dt className="font-semibold text-gray-900">Motivo</dt>
                    <dd className="min-w-0 break-words">
                      {messages[issue.code] ?? "Motivo pendiente de revisión."}
                    </dd>
                    <dt className="font-semibold text-gray-900">Campo</dt>
                    <dd className="min-w-0 break-words">{fieldLabel(issue.field)}</dd>
                    <dt className="font-semibold text-gray-900">Categoría</dt>
                    <dd className="min-w-0 break-words">{categories[issue.category]}</dd>
                    <dt className="font-semibold text-gray-900">Etapa</dt>
                    <dd className="min-w-0 break-words">{stages[issue.stage]}</dd>
                    {issue.question_id !== null && (
                      <>
                        <dt className="font-semibold text-gray-900">Pregunta</dt>
                        <dd className="min-w-0 break-words">
                          {fields[issue.question_id] ?? "Pregunta pendiente de identificar"}
                        </dd>
                      </>
                    )}
                  </dl>
                </details>
              </li>
            ))}
          </ul>
        </details>
      ))}
    </div>
  );
}
