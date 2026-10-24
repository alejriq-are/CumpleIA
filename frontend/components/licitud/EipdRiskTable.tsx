"use client";
import {
  type RiskEvaluation,
  type Rating,
  type Annex,
  levelLabels,
} from "@/lib/api/assessment-support";
type Value = Record<string, unknown>;
function rows(value: unknown): Value[] {
  return Array.isArray(value)
    ? value.filter((item): item is Value =>
        Boolean(item && typeof item === "object" && !Array.isArray(item))
      )
    : [];
}
function text(value: unknown, fallback = "Sin registrar") {
  return typeof value === "string" && value.trim() ? value : fallback;
}
const labels: Record<string, string> = {
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
function Description({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="min-w-0">
      <dt className="rounded-t bg-blue-50 px-3 py-2 font-semibold text-blue-950">{title}</dt>
      <dd className="whitespace-pre-wrap break-words rounded-b border border-blue-100 bg-white px-3 py-3 text-slate-950">
        {children}
      </dd>
    </div>
  );
}
function Level({ level }: { level?: string }) {
  const style: Record<string, string> = {
    bajo: "bg-green-50 text-green-950 border-green-600",
    medio: "bg-amber-50 text-amber-950 border-amber-600",
    alto: "bg-orange-50 text-orange-950 border-orange-600",
    muy_alto: "bg-red-50 text-red-950 border-red-600",
  };
  return (
    <strong
      className={`inline-block rounded border px-3 py-1 ${style[level ?? ""] ?? "border-slate-400 bg-slate-100 text-slate-900"}`}
    >
      {level && level !== "sin_resolver" ? levelLabels[level] : "Pendiente"}
    </strong>
  );
}
function Evidence({ value }: { value: unknown }) {
  const list = rows(value);
  return list.length ? (
    <ul className="list-disc space-y-2 pl-5">
      {list.map((item, i) => (
        <li key={i}>
          {text(item.evidence_type)} · {text(item.reference, "Referencia sin registrar")}
          {item.obtained_on ? ` · Fecha: ${text(item.obtained_on)}` : ""}
          {item.mechanism ? ` · Obtención: ${text(item.mechanism)}` : ""}
          {item.notes ? ` · Notas: ${text(item.notes)}` : ""}
        </li>
      ))}
    </ul>
  ) : (
    <>Sin evidencias registradas.</>
  );
}
function AnnexList({ items }: { items: Annex[] }) {
  return items.length ? (
    <ul className="list-disc space-y-1 pl-5">
      {items.map((item) => (
        <li key={item.id}>
          {item.reference} · versión {item.version} · {item.filename}. {item.description}
        </li>
      ))}
    </ul>
  ) : (
    <>Sin anexos vinculados.</>
  );
}
export function EipdRiskTable({
  value,
  valuation,
  annexes = [],
}: {
  value: Value;
  valuation?: RiskEvaluation | null;
  annexes?: Annex[];
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
  const cell = "whitespace-pre-wrap break-words border border-slate-300 p-3 align-top";
  const scroll =
    "max-w-full overflow-x-auto rounded border border-slate-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700";
  return (
    <section aria-label="Resumen de riesgos y controles" className="my-4 space-y-5">
      <h3 className="rounded bg-blue-100 p-3 font-semibold text-blue-950">
        Relación entre riesgos, controles y riesgo residual
      </h3>
      <p>
        {current
          ? `Valoración CUMPLEIA-CUALITATIVA-1 · revisión ${current.revision}, asociada al documento actual.`
          : valuation
            ? `La valoración revisión ${valuation.revision} es histórica. Sus niveles no se presentan como actuales; revisa y guarda una nueva valoración.`
            : "Sin valoración estructurada vigente. Completa Valorar riesgos; los análisis del documento se conservan."}{" "}
        Los niveles son orientativos y no autorizan el tratamiento.
      </p>
      <p>
        <strong>Horizonte temporal:</strong>{" "}
        {current ? text(current.analysis.horizon) : "Sin valoración vigente"}. El resumen general se
        presenta aparte; no sustituye la evaluación de cada riesgo.
      </p>
      {risks.map((risk, index) => {
        const id = text(risk.risk_id, `Sin identificador ${index + 1}`);
        const controls = linked(risk);
        const rating = current?.analysis.risks.find((item) => item.risk_id === risk.risk_id);
        const result = current?.result.risks.find((item) => item.risk_id === risk.risk_id);
        const stages: {
          key: "inherent" | "projected" | "residual";
          label: string;
          status: string;
        }[] = [
          { key: "inherent", label: "Inherente, antes de controles", status: "Evaluado" },
          {
            key: "projected",
            label: "Residual previsto",
            status: "Estimado; pendiente de comprobar",
          },
          {
            key: "residual",
            label: "Residual actual verificado",
            status: "Verificado; requiere revisión humana",
          },
        ];
        return (
          <section
            key={index}
            aria-label={`Detalle del riesgo ${id}`}
            className="min-w-0 space-y-4 rounded border border-slate-300 p-3 md:p-4"
          >
            <h4 className="rounded bg-blue-900 p-3 text-lg font-semibold text-white">
              Riesgo {id}
            </h4>
            <dl className="grid gap-3 md:grid-cols-2">
              <Description title="Descripción del riesgo">{text(risk.description)}</Description>
              <Description title="Daño potencial a las personas">
                {text(rating?.harm, text(risk.impact_analysis))}
              </Description>
              <Description title="Frecuencia y exposición">
                {text(rating?.frequency_context)}
              </Description>
              <Description title="Análisis de impacto del documento">
                {text(risk.impact_analysis)}
              </Description>
            </dl>
            <div
              role="region"
              tabIndex={0}
              aria-label={`Valoración cualitativa de ${id}; desplazamiento horizontal`}
              className={scroll}
            >
              <table className="w-full min-w-[680px] border-collapse text-left">
                <caption className="bg-blue-50 p-3 text-left font-semibold text-blue-950">
                  Valoración cualitativa de {id}
                </caption>
                <thead className="bg-blue-900 text-white">
                  <tr>
                    {[
                      "Etapa",
                      "Probabilidad",
                      "Impacto en las personas",
                      "Nivel",
                      "Estado de evaluación",
                    ].map((title) => (
                      <th key={title} scope="col" className={cell}>
                        {title}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {stages.map(({ key, label, status }) => {
                    const point: Rating | undefined = rating?.[key];
                    const evaluated = result?.[key] && result[key] !== "sin_resolver";
                    return (
                      <tr key={key} className="bg-white even:bg-slate-50">
                        <th scope="row" className={`${cell} font-semibold`}>
                          {label}
                        </th>
                        <td className={cell}>
                          {point?.probability
                            ? ["Baja", "Media", "Alta", "Muy alta"][point.probability - 1]
                            : "Sin evaluar"}
                        </td>
                        <td className={cell}>
                          {point?.impact
                            ? ["Bajo", "Moderado", "Grave", "Muy grave"][point.impact - 1]
                            : "Sin evaluar"}
                        </td>
                        <td className={cell}>
                          <Level level={result?.[key]} />
                        </td>
                        <td className={cell}>
                          {evaluated ? status : "Pendiente de evaluación o verificación"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <h5 className="font-semibold text-blue-950">Controles asociados a {id}</h5>
            {controls.length ? (
              <div
                role="region"
                tabIndex={0}
                aria-label={`Controles de ${id}; desplazamiento horizontal`}
                className={scroll}
              >
                <table className="w-full min-w-[900px] border-collapse text-left">
                  <caption className="sr-only">Controles asociados a {id}</caption>
                  <thead className="bg-blue-900 text-white">
                    <tr>
                      {[
                        "Control",
                        "Descripción de la medida",
                        "Dimensión de mitigación",
                        "Eficacia cualitativa",
                        "Implementación declarada",
                        "Estado de verificación",
                      ].map((title) => (
                        <th scope="col" key={title} className={cell}>
                          {title}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {controls.map((measure, i) => {
                      const control = current?.analysis.controls.find(
                        (item) => item.measure_id === measure.measure_id
                      );
                      const implemented =
                        measure.implemented && typeof measure.implemented === "object"
                          ? (measure.implemented as Value)
                          : {};
                      return (
                        <tr key={i} className="bg-white even:bg-slate-50">
                          <th scope="row" className={`${cell} font-semibold`}>
                            {text(measure.measure_id)}
                          </th>
                          <td className={cell}>{text(measure.description)}</td>
                          <td className={cell}>
                            {labels[control?.dimension ?? ""] ?? "Sin declarar"}
                          </td>
                          <td className={cell}>
                            {labels[control?.effectiveness ?? ""] ?? "No evaluada"}
                          </td>
                          <td className={cell}>
                            {answers[String(implemented.answer)] ?? "Sin declarar"}
                          </td>
                          <td className={cell}>
                            {labels[control?.status ?? ""] ?? "Sin valoración vigente"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>Sin medidas asociadas a este riesgo.</p>
            )}
            <details className="space-y-3 rounded border p-3">
              <summary>Fundamentos, evidencias y seguimiento de {id}</summary>
              <dl className="space-y-3">
                {stages.map(({ key, label }) => (
                  <Description key={key} title={`${label} — Fundamento de la valoración`}>
                    {text(rating?.[key]?.rationale)}
                  </Description>
                ))}
                <Description title="Análisis inicial del documento">
                  {text(risk.initial_assessment_analysis)}
                </Description>
                <Description title="Análisis residual del documento">
                  {text(risk.residual_assessment_analysis)}
                </Description>
                <Description title="Acción de tratamiento">{text(rating?.action)}</Description>
                <Description title="Responsable">{text(rating?.owner_reference)}</Description>
                <Description title="Fecha de revisión">{text(rating?.review_on)}</Description>
                <Description title="Evidencias del riesgo">
                  <Evidence value={risk.evidence} />
                </Description>
                <Description title="Anexos vinculados al riesgo">
                  <AnnexList items={annexes.filter((a) => a.risk_ids.includes(id))} />
                </Description>
              </dl>
              {controls.map((measure, i) => {
                const control = current?.analysis.controls.find(
                  (item) => item.measure_id === measure.measure_id
                );
                const implemented =
                  measure.implemented && typeof measure.implemented === "object"
                    ? (measure.implemented as Value)
                    : {};
                return (
                  <div key={i} className="space-y-3">
                    <h5 className="rounded bg-blue-100 p-2 font-semibold">
                      Control {text(measure.measure_id)} — fundamentos y evidencias
                    </h5>
                    <dl className="space-y-3">
                      <Description title="Fundamento de mitigación">
                        {text(control?.rationale)}
                      </Description>
                      <Description title="Análisis de eficacia del documento">
                        {text(measure.effectiveness_analysis)}
                      </Description>
                      <Description title="Análisis de implementación del documento">
                        {text(measure.implementation_analysis)}
                      </Description>
                      <Description title="Fundamento de implementación declarada">
                        {text(implemented.rationale)}
                      </Description>
                      <Description title="Referencias de verificación del control">
                        {control?.evidence_references?.length
                          ? control.evidence_references.join("\n")
                          : "Sin referencias registradas; adjuntar un archivo no verifica el control automáticamente."}
                      </Description>
                      <Description title="Evidencias de la medida">
                        <Evidence value={measure.evidence} />
                      </Description>
                      <Description title="Anexos vinculados al control">
                        <AnnexList
                          items={annexes.filter((a) =>
                            a.measure_ids.includes(String(measure.measure_id))
                          )}
                        />
                      </Description>
                    </dl>
                  </div>
                );
              })}
            </details>
          </section>
        );
      })}
      {unlinked.length > 0 && (
        <p role="note" className="rounded border border-amber-400 bg-amber-50 p-3">
          Medidas sin vínculo a un riesgo registrado:{" "}
          {unlinked.map((measure) => text(measure.measure_id, "Sin identificador")).join(", ")}.
          Revisa sus asociaciones.
        </p>
      )}
    </section>
  );
}
