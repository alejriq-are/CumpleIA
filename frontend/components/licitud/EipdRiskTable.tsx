"use client";
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
const answers: Record<string, string> = { si: "Sí", no: "No", pendiente: "Pendiente" };
export function EipdRiskTable({ value }: { value: Value }) {
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
        La tabla muestra los análisis registrados. El formulario actual no registra niveles
        estructurados por riesgo ni una valoración separada de la mitigación sobre probabilidad e
        impacto. El nivel residual general se presenta aparte y no se atribuye a cada riesgo.
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
                "Riesgo inicial",
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
                  </td>
                  <td className="whitespace-pre-wrap break-words border border-slate-300 p-3 align-top">
                    <p>{text(risk.initial_assessment_analysis)}</p>
                    <p className="mt-2 font-medium text-slate-700">
                      Nivel por riesgo: no registrado.
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
                              Mitigación sobre probabilidad o impacto: no valorada por separado.
                            </p>
                          </div>
                        ))
                      : "Sin mitigación documentada mediante medidas asociadas."}
                  </td>
                  <td className="whitespace-pre-wrap break-words border border-slate-300 p-3 align-top">
                    <p>{text(risk.residual_assessment_analysis)}</p>
                    <p className="mt-2 font-medium text-slate-700">
                      Nivel por riesgo: no registrado.
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
