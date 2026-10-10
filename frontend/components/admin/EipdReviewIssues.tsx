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
};
function fieldLabel(field: string) {
  return field
    .split(".")
    .map((part) => fields[part] ?? part.replaceAll("_", " "))
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
      {Array.from(groups, ([stage, items]) => (
        <section key={stage} className="space-y-2">
          <h4 className="font-semibold">{stages[stage]}</h4>
          <ul className="list-disc space-y-3 pl-5">
            {Array.from(items, ([key, { issue, count }]) => (
              <li key={key}>
                <p>
                  {messages[issue.code] ??
                    "Hay un motivo pendiente de revisión. Consulta su detalle."}
                </p>
                <p className="break-words text-gray-600">Campo: {fieldLabel(issue.field)}</p>
                {issue.question_id !== null && (
                  <p className="break-words">Pregunta: {issue.question_id.replaceAll("_", " ")}</p>
                )}
                {count > 1 && (
                  <p className="text-gray-600">Informado {count} veces por el diagnóstico.</p>
                )}
                <details className="mt-1 break-words text-gray-600">
                  <summary className="cursor-pointer">Detalle del diagnóstico</summary>
                  <dl>
                    <dt>Código</dt>
                    <dd>{issue.code}</dd>
                    <dt>Campo</dt>
                    <dd>{issue.field}</dd>
                    <dt>Categoría</dt>
                    <dd>{issue.category}</dd>
                    <dt>Etapa</dt>
                    <dd>{issue.stage}</dd>
                    {issue.question_id !== null && (
                      <>
                        <dt>Pregunta</dt>
                        <dd>{issue.question_id}</dd>
                      </>
                    )}
                  </dl>
                </details>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
