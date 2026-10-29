"use client";
import { documentDisclosureClass } from "./document-focus";
import type { RiskEvaluation, Annex } from "@/lib/api/assessment-support";
import { EipdRiskTable } from "./EipdRiskTable";
import { useEffect, useId, useRef, useState } from "react";
import { eipdStepLabels } from "@/lib/licitud/eipd-steps";
import { documentFields, type Fields } from "@/lib/licitud/eipd-document";
type Value = Record<string, unknown>;
function choiceHelp(value: unknown): string {
  const helps: Record<string, string> = {
    si: "Sí: declara que este punto se aborda en el análisis. Explica el fundamento y las evidencias; la selección no acredita suficiencia.",
    no: "No: declara que este punto no está abordado o no se cumple según tu análisis. Explica la limitación y las acciones pendientes.",
    pendiente:
      "Pendiente: usa esta opción cuando aún no tengas antecedentes suficientes para concluir. No equivale a una respuesta negativa ni a aprobación.",
    no_alto:
      "No alto: registra tu conclusión sobre el riesgo residual tras las medidas, con su fundamento. No autoriza el tratamiento ni activa EIPD.",
    alto: "Alto: registra que el riesgo residual sigue siendo alto. Explica riesgos, medidas y actuaciones que requieren revisión; no se habilita continuar.",
    sin_resolver:
      "Sin resolver: conserva abierta la conclusión cuando falte evaluar riesgos o eficacia de medidas. Explica qué falta resolver.",
    identificado:
      "Identificadas: indica que has localizado fuentes y sus referencias. Debes documentar su revisión y aplicabilidad; identificarlas no las valida.",
    no_identificado:
      "No identificadas: declara que todavía no has localizado fuentes para este análisis. Explica la búsqueda y los pendientes.",
    aplicable:
      "Aplicable: documenta por qué consideras que esta fuente corresponde al caso. La selección requiere revisión humana.",
    no_aplicable:
      "No aplicable: explica por qué la fuente no corresponde al alcance evaluado; conserva la referencia como antecedente.",
    no_solicitada:
      "No solicitada: registra que no se ha realizado una consulta. No determina si corresponde solicitarla.",
    en_curso:
      "En curso: registra una consulta iniciada y pendiente de respuesta. Incluye su referencia y estado.",
    concluida:
      "Concluida: registra la respuesta y el análisis de recomendaciones. La respuesta no se presume favorable ni habilita automáticamente EIPD.",
  };
  return (
    helps[String(value)] ??
    "Sin declarar: deja este punto abierto si no cuentas con antecedentes. Selecciona una opción solo cuando puedas explicar su fundamento."
  );
}

function CodesInput({
  label,
  value,
  onChange,
  describedBy,
}: {
  label: string;
  describedBy?: string;
  value: unknown;
  onChange: (v: string[]) => void;
}) {
  const [raw, setRaw] = useState(Array.isArray(value) ? value.join("\n") : "");
  const sent = useRef(value);
  useEffect(() => {
    if (value !== sent.current) {
      setRaw(Array.isArray(value) ? value.join("\n") : "");
      sent.current = value;
    }
  }, [value]);
  return (
    <textarea
      aria-label={label}
      aria-describedby={describedBy}
      className="block w-full rounded border p-2"
      value={raw}
      onChange={(e) => {
        setRaw(e.target.value);
        const next = e.target.value
          .split("\n")
          .map((x) => x.trim())
          .filter(Boolean);
        sent.current = next;
        onChange(next);
      }}
    />
  );
}
function Controls({
  fields,
  value,
  onChange,
  prefix = "",
}: {
  fields: Fields;
  value: Value;
  onChange: (v: Value) => void;
  prefix?: string;
}) {
  const controlId = useId();
  return (
    <div className="space-y-3">
      {Object.entries(fields).map(([key, f]) => {
        const v = value[key],
          label = prefix ? `${prefix} — ${f.label}` : f.label;
        const set = (next: unknown) => onChange({ ...value, [key]: next });
        if (f.item) {
          const rows = Array.isArray(v) ? (v as Value[]) : [];
          return (
            <fieldset key={key} className="space-y-3 rounded border p-3">
              <legend>{label}</legend>
              {rows.map((row, i) => (
                <div key={i} className="space-y-2 rounded border p-3">
                  <Controls
                    fields={f.item!}
                    value={row}
                    prefix={`${label} ${i + 1}`}
                    onChange={(next) => set(rows.map((r, j) => (j === i ? next : r)))}
                  />
                  <button type="button" onClick={() => set(rows.filter((_, j) => j !== i))}>
                    Quitar {label.toLowerCase()} {i + 1}
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={() => set([...rows, f.item!.evidence_type ? { evidence_type: "" } : {}])}
              >
                Añadir {label.toLowerCase()}
              </button>
            </fieldset>
          );
        }
        if (f.response) {
          const current = (v as Value) || {};
          return (
            <div key={key} className="space-y-2">
              <label className="block">
                {label}
                <select
                  aria-label={label}
                  aria-describedby={`${controlId}-${key}-help`}
                  className="block w-full rounded border p-2"
                  value={typeof current.answer === "string" ? current.answer : ""}
                  onChange={(e) =>
                    set(e.target.value ? { ...current, answer: e.target.value } : null)
                  }
                >
                  <option value="">Sin declarar</option>
                  {f.fields!.answer.choices!.map(([code, text]) => (
                    <option key={code} value={code}>
                      {text}
                    </option>
                  ))}
                </select>
              </label>
              <p id={`${controlId}-${key}-help`} aria-live="polite" className="text-sm">
                {choiceHelp(current.answer)}
              </p>
              <label className="block">
                {label} — Fundamento
                <textarea
                  aria-label={`${label} — Fundamento`}
                  disabled={!current.answer}
                  className="block w-full rounded border p-2"
                  value={typeof current.rationale === "string" ? current.rationale : ""}
                  onChange={(e) => set({ ...current, rationale: e.target.value || null })}
                />
              </label>
            </div>
          );
        }
        if (key === "agency_consultation" && f.fields) {
          const current = (v as Value) || {};
          const detailsValue = Object.fromEntries(
            Object.entries(current).filter(([field]) => field !== "status")
          );
          const hasDetails = Object.values(detailsValue).some((item) =>
            Array.isArray(item)
              ? item.length > 0
              : item && typeof item === "object"
                ? Object.values(item).some(Boolean)
                : Boolean(item)
          );
          const showDetails =
            current.status === "en_curso" || current.status === "concluida" || hasDetails;
          return (
            <fieldset key={key} className="space-y-3 rounded border p-3">
              <legend>{label}</legend>
              <Controls
                fields={{ status: f.fields.status }}
                value={current}
                prefix={label}
                onChange={set}
              />
              <details
                open={showDetails || undefined}
                key={showDetails ? "con-antecedentes" : "sin-antecedentes"}
                className="space-y-3"
              >
                <summary>Antecedentes y evidencias de consulta a la autoridad</summary>
                <p>
                  Completa estos antecedentes cuando exista una consulta. Los datos guardados
                  permanecen visibles aunque cambies su estado.
                </p>
                <Controls
                  fields={Object.fromEntries(
                    Object.entries(f.fields).filter(([field]) => field !== "status")
                  )}
                  value={current}
                  prefix={label}
                  onChange={set}
                />
              </details>
            </fieldset>
          );
        }
        if (f.fields)
          return (
            <fieldset key={key} className="space-y-3 rounded border p-3">
              <legend>{label}</legend>
              <Controls
                fields={f.fields}
                value={(v as Value) || {}}
                prefix={label}
                onChange={set}
              />
              <button type="button" onClick={() => set(null)}>
                Limpiar {label.toLowerCase()}
              </button>
            </fieldset>
          );
        return (
          <label key={key} className="block">
            {label}
            {f.required ? " *" : ""}
            {f.choices ? (
              <select
                aria-label={label}
                aria-describedby={`${controlId}-${key}-help`}
                className="block w-full rounded border p-2"
                value={typeof v === "string" ? v : ""}
                onChange={(e) => set(e.target.value || null)}
              >
                <option value="">Sin declarar</option>
                {f.choices.map(([code, text]) => (
                  <option key={code} value={code}>
                    {text}
                  </option>
                ))}
              </select>
            ) : f.kind === "date" ? (
              <input
                aria-label={label}
                aria-describedby={f.help ? `${controlId}-${key}-field-help` : undefined}
                type="date"
                className="block w-full rounded border p-2"
                value={typeof v === "string" ? v : ""}
                onChange={(e) => set(e.target.value || null)}
              />
            ) : f.kind === "codes" ? (
              <CodesInput
                label={label}
                value={v}
                onChange={set}
                describedBy={f.help ? `${controlId}-${key}-field-help` : undefined}
              />
            ) : (
              <textarea
                aria-label={label}
                aria-describedby={f.help ? `${controlId}-${key}-field-help` : undefined}
                required={f.required}
                className="block w-full rounded border p-2"
                value={
                  f.kind === "codes"
                    ? Array.isArray(v)
                      ? v.join("\n")
                      : ""
                    : typeof v === "string"
                      ? v
                      : ""
                }
                onChange={(e) =>
                  set(
                    f.kind === "codes"
                      ? e.target.value
                          .split("\n")
                          .map((x) => x.trim())
                          .filter(Boolean)
                      : e.target.value || (f.required ? "" : null)
                  )
                }
              />
            )}
            {f.choices && (
              <span
                id={`${controlId}-${key}-help`}
                aria-live="polite"
                className="block text-sm font-normal"
              >
                {choiceHelp(v)}
              </span>
            )}
            {f.help && (
              <span
                id={`${controlId}-${key}-field-help`}
                className="mt-1 block text-sm font-normal text-slate-700"
              >
                {f.help}
              </span>
            )}
            {f.kind === "codes" && !f.help && <span>Un código por línea.</span>}
          </label>
        );
      })}
    </div>
  );
}
export const eipdGroups: { title: string; description: string; keys: string[] }[] = [
  {
    title: `1. ${eipdStepLabels[0]}`,
    description:
      "Describe la finalidad, operaciones, tecnologías y datos incluidos. Usa el alcance de la evaluación guardada como referencia.",
    keys: [
      "report_reference",
      "prepared_by",
      "completed_on",
      "purpose_description",
      "processing_operations",
      "processing_context",
      "technologies_description",
      "exceptions_coverage_analysis",
      "scope",
    ],
  },
  {
    title: `2. ${eipdStepLabels[1]}`,
    description:
      "Explica por qué se necesitan los datos, las alternativas y los límites. Las respuestas requieren fundamento; no completan automáticamente la evaluación.",
    keys: [
      "necessity_analysis",
      "proportionality_analysis",
      "minimization_analysis",
      "necessary_for_purpose",
      "proportionate_processing",
      "minimization_addressed",
      "performed_before_processing",
      "prior_assessment_analysis",
    ],
  },
  {
    title: `3. ${eipdStepLabels[2]}`,
    description:
      "Añade cada riesgo con un identificador, su impacto y el análisis inicial y residual. El sistema conserva tu análisis; no calcula una puntuación de riesgo.",
    keys: ["risks"],
  },
  {
    title: `4. ${eipdStepLabels[3]}`,
    description:
      "Valora el riesgo para las personas y compara el riesgo inherente con el residual previsto y actual verificado.",
    keys: [],
  },
  {
    title: `5. ${eipdStepLabels[4]}`,
    description:
      "Asocia cada medida a los identificadores de riesgos que aborda. Documenta implementación, eficacia y evidencias; una medida declarada no se considera implementada automáticamente.",
    keys: ["measures"],
  },
  {
    title: `6. ${eipdStepLabels[5]}`,
    description:
      "Conserva referencias, revisión de aplicabilidad y evidencias. Documenta una consulta a la autoridad solo si corresponde a los antecedentes del caso.",
    keys: ["official_sources", "agency_consultation", "evidence"],
  },
  {
    title: `7. ${eipdStepLabels[6]}`,
    description:
      "Explica qué riesgo permanece después de las medidas, las limitaciones y el plan de seguimiento. Esta conclusión no aprueba ni activa EIPD.",
    keys: [
      "residual_risk_summary",
      "residual_risk_rationale",
      "residual_risk_level",
      "limitations_analysis",
      "follow_up_plan",
    ],
  },
];

export function EipdSteps({
  step,
  onChange,
  supportPanelId,
}: {
  step: number;
  onChange: (step: number) => void;
  supportPanelId?: string;
}) {
  return (
    <nav aria-label="Pasos documentales EIPD" className="flex flex-wrap gap-2">
      {eipdGroups.map((group, index) => (
        <button
          key={group.title}
          type="button"
          className={
            step === index
              ? "rounded bg-blue-800 p-2 font-semibold text-white"
              : "rounded border bg-white p-2"
          }
          aria-current={step === index ? "step" : undefined}
          aria-controls={index === 3 ? supportPanelId : undefined}
          onClick={() => onChange(index)}
        >
          {group.title}
        </button>
      ))}
    </nav>
  );
}
export function EipdDocumentFields({
  value,
  onChange,
  guided = false,
  activeStep,
}: {
  value: Value;
  onChange: (v: Value) => void;
  guided?: boolean;
  activeStep?: number;
}) {
  const [localStep, setStep] = useState(0);
  const step = activeStep ?? localStep;
  const groups = eipdGroups;
  if (guided)
    return (
      <section className="space-y-4" aria-label="Secciones del análisis EIPD">
        {activeStep === undefined && <EipdSteps step={step} onChange={setStep} />}
        <p>{groups[step].description}</p>
        <Controls
          fields={Object.fromEntries(groups[step].keys.map((key) => [key, documentFields[key]]))}
          value={value}
          onChange={onChange}
        />
      </section>
    );
  return (
    <details>
      <summary>Análisis, riesgos, medidas, fuentes y evidencias</summary>
      <p>
        Son declaraciones documentales de prueba. Identificar fuentes no las verifica ni acepta la
        política; completar campos no habilita EIPD.
      </p>
      <Controls fields={documentFields} value={value} onChange={onChange} />
    </details>
  );
}
export function EipdDocumentView({
  value,
  expanded = false,
  valuation,
  annexes,
}: {
  value: Value;
  expanded?: boolean;
  valuation?: RiskEvaluation | null;
  annexes?: Annex[];
}) {
  function show(fields: Fields, v: Value, prefix = ""): React.ReactNode {
    return Object.entries(fields).map(([key, f]) => {
      const x = v[key],
        label = prefix ? `${prefix} — ${f.label}` : f.label;
      if (x == null || (Array.isArray(x) && !x.length)) return null;
      if (f.item)
        return (
          <div key={key}>
            <h4 className="mt-4 rounded bg-slate-100 p-2 font-semibold text-blue-950">{label}</h4>
            {(x as Value[]).map((row, i) => (
              <div key={i}>{show(f.item!, row, `${label} ${i + 1}`)}</div>
            ))}
          </div>
        );
      if (f.fields) return <div key={key}>{show(f.fields, x as Value, label)}</div>;
      return (
        <dl key={key}>
          <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
            {label}
          </dt>
          <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
            {f.choices
              ? f.choices.find(([c]) => c === x)?.[1]
              : Array.isArray(x)
                ? x.join(", ")
                : String(x)}
          </dd>
        </dl>
      );
    });
  }
  return (
    <details open={expanded || undefined}>
      <summary className={documentDisclosureClass}>
        {expanded ? "Contenido preparado" : "Contenido del documento guardado"}
      </summary>
      <EipdRiskTable value={value} valuation={valuation} annexes={annexes} />
      <div className="mt-4 space-y-4">
        {show(
          Object.fromEntries(
            Object.entries(documentFields).filter(([key]) => key !== "risks" && key !== "measures")
          ),
          value
        )}
      </div>
      {((Array.isArray(value.risks) && value.risks.length > 0) ||
        (Array.isArray(value.measures) && value.measures.length > 0)) && (
        <details className="mt-4 space-y-3 rounded border p-3">
          <summary className="font-semibold text-blue-950">
            Análisis y evidencias por riesgo y medida
          </summary>
          {show({ risks: documentFields.risks, measures: documentFields.measures }, value)}
        </details>
      )}
    </details>
  );
}
