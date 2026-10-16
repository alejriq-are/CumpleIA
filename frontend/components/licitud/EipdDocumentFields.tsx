"use client";
import { useEffect, useRef, useState } from "react";
import { documentFields, type Fields } from "@/lib/licitud/eipd-document";
type Value = Record<string, unknown>;
function CodesInput({
  label,
  value,
  onChange,
}: {
  label: string;
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
                type="date"
                className="block w-full rounded border p-2"
                value={typeof v === "string" ? v : ""}
                onChange={(e) => set(e.target.value || null)}
              />
            ) : f.kind === "codes" ? (
              <CodesInput label={label} value={v} onChange={set} />
            ) : (
              <textarea
                aria-label={label}
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
            {f.kind === "codes" && <span>Un código por línea.</span>}
          </label>
        );
      })}
    </div>
  );
}
export function EipdDocumentFields({
  value,
  onChange,
}: {
  value: Value;
  onChange: (v: Value) => void;
}) {
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
export function EipdDocumentView({ value }: { value: Value }) {
  function show(fields: Fields, v: Value, prefix = ""): React.ReactNode {
    return Object.entries(fields).map(([key, f]) => {
      const x = v[key],
        label = prefix ? `${prefix} — ${f.label}` : f.label;
      if (x == null || (Array.isArray(x) && !x.length)) return null;
      if (f.item)
        return (
          <div key={key}>
            <h4>{label}</h4>
            {(x as Value[]).map((row, i) => (
              <div key={i}>{show(f.item!, row, `${label} ${i + 1}`)}</div>
            ))}
          </div>
        );
      if (f.fields) return <div key={key}>{show(f.fields, x as Value, label)}</div>;
      return (
        <dl key={key}>
          <dt>{label}</dt>
          <dd className="whitespace-pre-wrap break-words">
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
    <details>
      <summary>Contenido del documento guardado</summary>
      {show(documentFields, value)}
    </details>
  );
}
