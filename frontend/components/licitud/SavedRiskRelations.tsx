"use client";
import type { Annex, RiskEvaluation } from "@/lib/api/assessment-support";
import { levelLabels } from "@/lib/api/assessment-support";
import { documentDisclosureClass, documentNavigationButtonClass } from "./document-focus";

type RecordValue = Record<string, unknown>;
function records(value: unknown): RecordValue[] {
  return Array.isArray(value)
    ? value.filter((item): item is RecordValue => !!item && typeof item === "object")
    : [];
}
function content(value: unknown) {
  return typeof value === "string" && value.trim() ? value : "Sin registrar";
}
const states: Record<string, string> = {
  propuesta: "Propuesta",
  en_implementacion: "En implementación",
  verificada: "Verificada",
  no_evaluada: "No evaluada",
  insuficiente: "Insuficiente",
  parcial: "Parcial",
  suficiente: "Suficiente",
  probabilidad: "Probabilidad",
  impacto: "Impacto",
  ambos: "Probabilidad e impacto",
};
export function SavedRiskRelations({
  valuation,
  document,
  annexes,
  annexTarget,
}: {
  valuation: RiskEvaluation;
  document: RecordValue;
  annexes: Annex[];
  annexTarget: (index: number) => string;
}) {
  const risks = records(document.risks),
    measures = records(document.measures);
  function annexLinks(riskId: string, measureId?: string) {
    const matches = annexes
      .map((annex, index) => ({ annex, index }))
      .filter(({ annex }) =>
        measureId ? annex.measure_ids.includes(measureId) : annex.risk_ids.includes(riskId)
      );
    return matches.length ? (
      <ul className="space-y-2">
        {matches.map(({ annex, index }) => (
          <li key={annex.id}>
            <button
              type="button"
              className={documentNavigationButtonClass}
              onClick={() => {
                const target = window.document.getElementById(annexTarget(index));
                target?.focus();
                target?.scrollIntoView({ block: "center" });
              }}
            >
              Consultar anexo {annex.reference} · versión {annex.version}
            </button>
            <p>{annex.description}</p>
          </li>
        ))}
      </ul>
    ) : (
      <p>Sin anexos vinculados explícitamente {measureId ? "a esta medida" : "a este riesgo"}.</p>
    );
  }
  return (
    <section aria-label="Medidas y respaldos del riesgo residual" className="space-y-4">
      <h3 className="text-lg font-semibold">Medidas y respaldos del riesgo residual</h3>
      <p>
        Consulta de la valoración guardada, revisión {valuation.revision}. No incluye ediciones
        pendientes. Un vínculo o un archivo adjunto no demuestra por sí solo la eficacia de una
        medida.
      </p>
      {!valuation.current && (
        <p role="note" className="rounded border border-amber-400 bg-amber-50 p-3">
          Valoración histórica: se muestran sus niveles guardados. No se relacionan con medidas ni
          anexos del documento actual porque su contenido cambió.
        </p>
      )}
      {valuation.analysis.risks.map((rating) => {
        const result = valuation.result.risks.find((item) => item.risk_id === rating.risk_id);
        const risk = risks.find((item) => item.risk_id === rating.risk_id);
        const linked = valuation.current
          ? measures.filter(
              (item) => Array.isArray(item.risk_ids) && item.risk_ids.includes(rating.risk_id)
            )
          : [];
        return (
          <article
            key={rating.risk_id}
            aria-label={`Relaciones guardadas de ${rating.risk_id}`}
            className="min-w-0 space-y-3 rounded border border-slate-300 p-3"
          >
            <h4 className="rounded bg-blue-100 p-2 font-semibold">Riesgo {rating.risk_id}</h4>
            {valuation.current && <p>{content(risk?.description)}</p>}
            <p>
              <strong>Residual previsto:</strong> {levelLabels[result?.projected ?? "sin_resolver"]}
            </p>
            <p>
              <strong>Residual actual verificado:</strong>{" "}
              {levelLabels[result?.residual ?? "sin_resolver"]}
            </p>
            <details>
              <summary
                className={documentDisclosureClass}
                onKeyDown={(event) => {
                  if (event.code !== "Space" && event.key !== " " && event.key !== "Spacebar")
                    return;
                  event.preventDefault();
                  if (!event.repeat) {
                    const details = event.currentTarget.parentElement as HTMLDetailsElement;
                    details.open = !details.open;
                  }
                }}
                onKeyUp={(event) => {
                  if (event.code === "Space" || event.key === " " || event.key === "Spacebar")
                    event.preventDefault();
                }}
              >
                Consultar fundamentos y medidas de {rating.risk_id}
              </summary>
              <div className="space-y-3 pt-3">
                <p className="whitespace-pre-wrap">
                  <strong>Fundamento del residual previsto: </strong>
                  {content(rating.projected.rationale)}
                </p>
                <p className="whitespace-pre-wrap">
                  <strong>Fundamento del residual actual: </strong>
                  {content(rating.residual.rationale)}
                </p>
                {valuation.current && (
                  <>
                    <h5 className="font-semibold">Evidencias declaradas en el riesgo</h5>
                    {records(risk?.evidence).length ? (
                      <ul>
                        {records(risk?.evidence).map((item, i) => (
                          <li key={i}>
                            {content(item.reference)} · {content(item.notes)}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p>Sin evidencias declaradas en este riesgo.</p>
                    )}
                    <h5 className="font-semibold">Anexos vinculados al riesgo {rating.risk_id}</h5>
                    {annexLinks(rating.risk_id)}
                    {!linked.length && (
                      <p>
                        Sin medidas asociadas explícitamente a este riesgo en el documento guardado.
                      </p>
                    )}
                    {linked.map((measure, index) => {
                      const id = content(measure.measure_id);
                      const control = valuation.analysis.controls.find(
                        (item) => item.measure_id === measure.measure_id
                      );
                      return (
                        <section
                          key={index}
                          aria-label={`Medida ${id} de ${rating.risk_id}`}
                          className="space-y-2 rounded border bg-slate-50 p-3"
                        >
                          <h5 className="font-semibold">Medida {id}</h5>
                          <p className="whitespace-pre-wrap">{content(measure.description)}</p>
                          <p>
                            <strong>Dimensión de mitigación: </strong>
                            {states[control?.dimension ?? ""] ?? "Sin declarar"}
                          </p>
                          <p>
                            <strong>Estado de verificación: </strong>
                            {control
                              ? states[control.status]
                              : "Sin valoración guardada para esta medida"}
                          </p>
                          <p>
                            <strong>Eficacia cualitativa: </strong>
                            {control ? states[control.effectiveness] : "No evaluada"}
                          </p>
                          <p className="whitespace-pre-wrap">
                            <strong>Fundamento de mitigación: </strong>
                            {content(control?.rationale)}
                          </p>
                          <p>
                            <strong>Referencias de verificación: </strong>
                            {control?.evidence_references.length
                              ? control.evidence_references.join(" · ")
                              : "Sin referencias registradas"}
                          </p>
                          <h6 className="font-semibold">Evidencias declaradas en la medida</h6>
                          {records(measure.evidence).length ? (
                            <ul>
                              {records(measure.evidence).map((evidence, i) => (
                                <li key={i}>
                                  {content(evidence.reference)} · {content(evidence.notes)}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <p>Sin evidencias declaradas en esta medida.</p>
                          )}
                          <h6 className="font-semibold">Anexos vinculados a la medida {id}</h6>
                          {annexLinks(rating.risk_id, id)}
                        </section>
                      );
                    })}
                  </>
                )}
              </div>
            </details>
          </article>
        );
      })}
      {!valuation.analysis.risks.length && <p>La valoración no contiene riesgos registrados.</p>}
    </section>
  );
}
