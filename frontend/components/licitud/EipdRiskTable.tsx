"use client";
import { type RiskEvaluation, levelLabels } from "@/lib/api/assessment-support";
type Value = Record<string, unknown>;
function rows(value: unknown): Value[] {
  return Array.isArray(value)
    ? value.filter((item): item is Value =>
        Boolean(item && typeof item === "object" && !Array.isArray(item))
      )
    : [];
}
function text(value: unknown, fallback = "Sin información registrada") {
  return typeof value === "string" && value.trim() ? value : fallback;
}
const controlLabels: Record<string, string> = {
  probabilidad: "Probabilidad",
  impacto: "Impacto",
  ambos: "Probabilidad e impacto",
  no_evaluada: "No evaluada",
  insuficiente: "Insuficiente",
  parcial: "Parcial",
  suficiente: "Suficiente",
  propuesta: "Propuesta",
  en_implementacion: "En implementación",
  verificada: "Verificada",
};
const answers: Record<string, string> = { si: "Sí", no: "No", pendiente: "Pendiente" };
export function EipdRiskTable({
  value,
  valuation,
}: {
  value: Value;
  valuation?: RiskEvaluation | null;
}) {
  const current = valuation?.current ? valuation : null;
  const risks = rows(value.risks),
    measures = rows(value.measures);
  if (!risks.length) return null;
  const linked = (risk: Value) =>
    measures.filter(
      (measure) =>
        typeof risk.risk_id === "string" &&
        risk.risk_id.trim() &&
        Array.isArray(measure.risk_ids) &&
        measure.risk_ids.includes(risk.risk_id)
    );
  const unlinked = measures.filter(
    (measure) => !risks.some((risk) => linked(risk).includes(measure))
  );
  return (
    <section aria-label="Resumen de riesgos y controles" className="my-4 space-y-3">
      <h3 className="rounded bg-blue-100 p-3 font-semibold text-blue-950">
        Relación entre riesgos, controles y riesgo residual
      </h3>
      <p className="text-sm">
        {current
          ? `Valoración CUMPLEIA-CUALITATIVA-1 · revisión ${current.revision}. Los niveles son orientativos y no autorizan el tratamiento.`
          : "Sin valoración estructurada vigente. Completa Valorar riesgos; los análisis del documento se conservan."}{" "}
        El nivel residual general se presenta aparte y no se atribuye a cada riesgo.
      </p>
      <div
        role="region"
        aria-label="Tabla de riesgos y controles; desplazamiento horizontal"
        tabIndex={0}
        className="max-w-full overflow-x-auto rounded border border-slate-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
      >
        <table className="w-full min-w-[960px] table-fixed border-collapse text-left text-sm">
          <caption className="sr-only">
            Riesgos con sus medidas asociadas y análisis residual
          </caption>
          <thead className="bg-blue-900 text-white">
            <tr>
              {[
                "Riesgo",
                "Impacto en las personas",
                "Riesgo inherente",
                "Medidas de control",
                "Eficacia y mitigación",
                "Riesgo residual",
              ].map((label) => (
                <th key={label} scope="col" className="border border-blue-800 p-3 align-top">
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {risks.map((risk, index) => {
              const controls = linked(risk);
              const result = current?.result.risks.find((item) => item.risk_id === risk.risk_id);
              const rating = current?.analysis.risks.find((item) => item.risk_id === risk.risk_id);
              const ranks = (
                point: { probability: number | null; impact: number | null } | undefined
              ) =>
                point
                  ? `Probabilidad: ${point.probability ? ["Baja", "Media", "Alta", "Muy alta"][point.probability - 1] : "Sin evaluar"}. Impacto: ${point.impact ? ["Bajo", "Moderado", "Grave", "Muy grave"][point.impact - 1] : "Sin evaluar"}.`
                  : "";
              return (
                <tr key={index} className="bg-white even:bg-slate-50">
                  <th
                    scope="row"
                    className="whitespace-pre-wrap break-words border border-slate-300 p-3 align-top font-normal"
                  >
                    <strong className="text-blue-900">
                      {text(risk.risk_id, "Sin identificador")}
                    </strong>
                    <p className="mt-2">{text(risk.description)}</p>
                  </th>
                  <td className="whitespace-pre-wrap break-words border border-slate-300 p-3 align-top">
                    {text(risk.impact_analysis)}
                    {rating?.harm && <p className="mt-2">Daño valorado: {rating.harm}</p>}
                  </td>
                  <td className="whitespace-pre-wrap break-words border border-slate-300 p-3 align-top">
                    <p>{text(risk.initial_assessment_analysis)}</p>
                    <p className="mt-2 font-medium text-slate-700">
                      Nivel por riesgo: {levelLabels[result?.inherent ?? "sin_resolver"]}.
                      {rating && <span className="block">{ranks(rating.inherent)}</span>}
                    </p>
                  </td>
                  <td className="border border-slate-300 p-3 align-top">
                    {controls.length
                      ? controls.map((measure, i) => {
                          const implemented =
                            measure.implemented && typeof measure.implemented === "object"
                              ? (measure.implemented as Value)
                              : {};
                          return (
                            <div key={i} className="mb-4 space-y-2 whitespace-pre-wrap break-words">
                              <strong className="text-blue-900">
                                {text(measure.measure_id, "Sin identificador de medida")}
                              </strong>
                              <p>{text(measure.description)}</p>
                              <p>
                                Implementada:{" "}
                                {answers[String(implemented.answer)] ?? "Sin declarar"}
                              </p>
                              <p>
                                {text(
                                  implemented.rationale,
                                  "Fundamento de implementación sin registrar"
                                )}
                              </p>
                            </div>
                          );
                        })
                      : "Sin medidas asociadas a este riesgo."}
                  </td>
                  <td className="border border-slate-300 p-3 align-top">
                    {controls.length
                      ? controls.map((measure, i) => (
                          <div key={i} className="mb-4 space-y-2 whitespace-pre-wrap break-words">
                            <strong className="text-blue-900">
                              {text(measure.measure_id, "Medida sin identificador")}
                            </strong>
                            <p>
                              {text(
                                measure.effectiveness_analysis,
                                "Eficacia pendiente de evaluar"
                              )}
                            </p>
                            <p>
                              {text(
                                measure.implementation_analysis,
                                "Análisis de implementación pendiente"
                              )}
                            </p>
                            <p className="font-medium text-slate-700">
                              {(() => {
                                const rating = current?.analysis.controls.find(
                                  (item) => item.measure_id === measure.measure_id
                                );
                                return rating
                                  ? `Dimensión: ${controlLabels[rating.dimension ?? ""] ?? "Sin declarar"}. Eficacia: ${controlLabels[rating.effectiveness]}. Estado: ${controlLabels[rating.status]}. ${rating.rationale}`
                                  : "Mitigación: pendiente de valoración estructurada.";
                              })()}
                            </p>
                          </div>
                        ))
                      : "Sin mitigación documentada mediante medidas asociadas."}
                  </td>
                  <td className="whitespace-pre-wrap break-words border border-slate-300 p-3 align-top">
                    <p>{text(risk.residual_assessment_analysis)}</p>
                    <p className="mt-2 font-medium text-slate-700">
                      Residual actual: {levelLabels[result?.residual ?? "sin_resolver"]}. Previsto:{" "}
                      {levelLabels[result?.projected ?? "sin_resolver"]}.
                      {rating && (
                        <>
                          <span className="block">Actual: {ranks(rating.residual)}</span>
                          <span className="block">Previsto: {ranks(rating.projected)}</span>
                        </>
                      )}
                    </p>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {unlinked.length > 0 && (
        <p role="note">
          Medidas sin vínculo a un riesgo registrado:{" "}
          {unlinked.map((measure) => text(measure.measure_id, "Sin identificador")).join(", ")}.
          Revisa sus asociaciones.
        </p>
      )}
    </section>
  );
}
