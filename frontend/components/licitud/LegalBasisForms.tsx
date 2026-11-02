"use client";
import { liaGroups, type LegalField } from "@/lib/licitud/lia-fields";
export type LegalDocument = Record<string, unknown>;
export function object(value: unknown): LegalDocument {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as LegalDocument)
    : {};
}
const inputClass = "block w-full rounded border border-slate-300 bg-white p-2 text-slate-950";
const answers = [
  ["si", "Sí"],
  ["no", "No"],
  ["pendiente", "Pendiente de analizar"],
];
export const consentQuestions = [
  ["consentimiento_libre", "¿El consentimiento es libre?"],
  ["consentimiento_informado", "¿El consentimiento es informado?"],
  ["consentimiento_especifico_finalidad", "¿Es específico para la finalidad?"],
  ["consentimiento_previo", "¿Es previo al tratamiento?"],
  ["voluntad_inequivoca", "¿La voluntad es inequívoca?"],
  ["accion_afirmativa_clara", "¿Existe una acción afirmativa clara?"],
  ["revocacion_posible", "¿Es posible revocar el consentimiento?"],
  ["revocacion_medio_equivalente", "¿La revocación dispone de un medio equivalente?"],
  ["revocacion_expedita", "¿La revocación es expedita?"],
  ["revocacion_fidedigna", "¿La revocación es fidedigna?"],
  ["revocacion_gratuita", "¿La revocación es gratuita?"],
  ["revocacion_disponible_permanentemente", "¿La revocación está disponible permanentemente?"],
  ["responsable_puede_acreditar", "¿El responsable puede acreditar el consentimiento?"],
  ["contexto_contrato_servicio", "¿Existe un contexto de contrato o servicio?"],
  ["mandatario_facultad_expresa", "¿El mandatario cuenta con facultad expresa?"],
  [
    "tratamiento_necesario_contrato_servicio",
    "¿El tratamiento es necesario para el contrato o servicio?",
  ],
] as const;
function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: unknown;
  options: readonly (readonly string[])[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      {label}
      <select
        aria-label={label}
        className={inputClass}
        value={String(value ?? "")}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">Sin responder</option>
        {options.map(([key, text]) => (
          <option key={key} value={key}>
            {text}
          </option>
        ))}
      </select>
    </label>
  );
}
function Text({
  label,
  value,
  onChange,
  type,
}: {
  label: string;
  value: unknown;
  onChange: (value: string) => void;
  type?: string;
}) {
  return (
    <label className="block">
      {label}
      {type ? (
        <input
          aria-label={label}
          type={type}
          className={inputClass}
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        />
      ) : (
        <textarea
          aria-label={label}
          className={inputClass}
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        />
      )}
    </label>
  );
}
function Response({
  label,
  value,
  onChange,
  allowNA = false,
}: {
  label: string;
  value: unknown;
  onChange: (value: unknown) => void;
  allowNA?: boolean;
}) {
  const current = object(value);
  return (
    <div className="space-y-2 rounded border p-3">
      <Select
        label={label}
        value={current.answer}
        options={
          allowNA || current.answer === "no_aplica"
            ? [...answers, ["no_aplica", "No aplica"]]
            : answers
        }
        onChange={(answer) => onChange(answer ? { ...current, answer } : null)}
      />
      <Text
        label={label + " — Fundamento"}
        value={current.comment}
        onChange={(comment) =>
          onChange({ ...current, answer: current.answer || "pendiente", comment: comment || null })
        }
      />
    </div>
  );
}
export function LiaForm({
  value,
  onChange,
  disabled,
  applicability,
}: {
  value: LegalDocument;
  onChange: (value: LegalDocument) => void;
  disabled: boolean;
  applicability: Record<string, string>;
}) {
  function update(group: string, key: string, item: unknown) {
    onChange({ ...value, schema_version: 1, [group]: { ...object(value[group]), [key]: item } });
  }
  function field(group: string, f: LegalField) {
    const current = object(value[group])[f.key];
    if (f.kind === "response")
      return (
        <Response
          key={f.key}
          label={f.label}
          value={current}
          allowNA={applicability[group + "." + f.key] === "no_aplicable"}
          onChange={(v) => update(group, f.key, v)}
        />
      );
    if (f.kind === "measures") {
      const measures = (Array.isArray(current) ? current : []) as LegalDocument[];
      return (
        <div key={f.key} className="space-y-3">
          <h4 className="font-semibold">{f.label}</h4>
          {measures.map((measure, index) => (
            <div className="space-y-2 rounded border p-3" key={index}>
              <Text
                label={`Medida ${index + 1} — Descripción`}
                value={measure.description}
                onChange={(v) =>
                  update(
                    group,
                    f.key,
                    measures.map((m, i) => (i === index ? { ...m, description: v } : m))
                  )
                }
              />
              <Text
                label={`Medida ${index + 1} — Impacto mitigado`}
                value={measure.mitigated_impact}
                onChange={(v) =>
                  update(
                    group,
                    f.key,
                    measures.map((m, i) =>
                      i === index ? { ...m, mitigated_impact: v || null } : m
                    )
                  )
                }
              />
              <button
                type="button"
                className="rounded border bg-blue-50 p-2"
                onClick={() =>
                  update(
                    group,
                    f.key,
                    measures.filter((_, i) => i !== index)
                  )
                }
              >
                Quitar medida {index + 1}
              </button>
            </div>
          ))}
          <button
            type="button"
            className="rounded border bg-blue-50 p-2"
            onClick={() =>
              update(group, f.key, [...measures, { description: "", mitigated_impact: null }])
            }
          >
            Agregar medida de la LIA
          </button>
        </div>
      );
    }
    return f.kind ? (
      <Select
        key={f.key}
        label={f.label}
        value={current}
        options={f.kind.split("|").map((v) => v.split(":"))}
        onChange={(v) => update(group, f.key, v || null)}
      />
    ) : (
      <Text
        key={f.key}
        label={f.label}
        value={current}
        onChange={(v) => update(group, f.key, v || null)}
      />
    );
  }
  return (
    <fieldset disabled={disabled} className="space-y-4">
      <legend className="text-xl font-semibold">LIA: análisis en borrador</legend>
      <p>
        Completa los ocho grupos. Las respuestas y la conclusión propuesta requieren revisión;
        guardar no aprueba el tratamiento. La escala de impactos LIA es distinta de la matriz EIPD.
      </p>
      {liaGroups.map((group) => (
        <fieldset key={group.key} className="space-y-3 rounded border p-4">
          <legend className="bg-blue-50 px-2 font-semibold">{group.label}</legend>
          {group.fields.map((f) => field(group.key, f))}
        </fieldset>
      ))}
    </fieldset>
  );
}
export function ConsentForm({
  value,
  onChange,
  disabled,
  applicability,
}: {
  value: LegalDocument;
  onChange: (value: LegalDocument) => void;
  disabled: boolean;
  applicability: Record<string, string>;
}) {
  const stored = (Array.isArray(value.answers) ? value.answers : []) as LegalDocument[];
  const evidence = (Array.isArray(value.evidence) ? value.evidence : []) as LegalDocument[];
  function update(key: string, item: unknown) {
    onChange({ ...value, schema_version: 1, [key]: item });
  }
  return (
    <fieldset disabled={disabled} className="space-y-4">
      <legend className="text-xl font-semibold">Consentimiento: expediente en borrador</legend>
      <p>
        Registra únicamente datos ficticios. Esta entrega utiliza los 16 controles del contrato v1;
        no sustituye el desglose de las 19 prácticas originales ni acredita consentimiento válido.
        No aplica solo se ofrece cuando el diagnóstico del servidor lo permite para el formulario
        guardado, o si ya consta en el antecedente.
      </p>
      <Select
        label="Quién otorga el consentimiento"
        value={value.given_by}
        options={[
          ["titular", "Titular"],
          ["representante_legal", "Representante legal"],
          ["mandatario", "Mandatario"],
        ]}
        onChange={(v) => update("given_by", v || null)}
      />
      <Select
        label="Método de otorgamiento"
        value={value.grant_method}
        options={[
          ["escrito", "Escrito"],
          ["verbal", "Verbal"],
          ["electronico", "Electrónico"],
          ["acto_afirmativo", "Acto afirmativo"],
          ["otro_documentado", "Otro documentado"],
        ]}
        onChange={(v) => update("grant_method", v || null)}
      />
      {consentQuestions.map(([key, label]) => (
        <Response
          key={key}
          label={label}
          value={stored.find((a) => a.question_id === key)}
          allowNA={applicability["answers." + key] === "no_aplicable"}
          onChange={(item) =>
            update("answers", [
              ...stored.filter((a) => a.question_id !== key),
              ...(item ? [{ ...object(item), question_id: key }] : []),
            ])
          }
        />
      ))}
      <h4 className="font-semibold">Referencias documentales del consentimiento</h4>
      <p>
        Son metadatos; escribir una referencia no adjunta un archivo ni lo vincula a un criterio.
      </p>
      {evidence.map((item, index) => (
        <fieldset key={index} className="space-y-2 rounded border p-3">
          <legend>Referencia {index + 1}</legend>
          {[
            ["evidence_type", "Tipo de evidencia"],
            ["reference", "Referencia"],
            ["obtained_on", "Fecha de obtención"],
            ["mechanism", "Mecanismo"],
            ["notes", "Notas de la evidencia"],
          ].map(([key, label]) => (
            <Text
              key={key}
              label={`${label} ${index + 1}`}
              type={key === "obtained_on" ? "date" : undefined}
              value={item[key]}
              onChange={(v) =>
                update(
                  "evidence",
                  evidence.map((m, i) =>
                    i === index ? { ...m, [key]: key === "evidence_type" ? v : v || null } : m
                  )
                )
              }
            />
          ))}
          <button
            type="button"
            className="rounded border bg-blue-50 p-2"
            onClick={() =>
              update(
                "evidence",
                evidence.filter((_, i) => i !== index)
              )
            }
          >
            Quitar referencia {index + 1}
          </button>
        </fieldset>
      ))}
      <button
        type="button"
        className="rounded border bg-blue-50 p-2"
        onClick={() =>
          update("evidence", [
            ...evidence,
            { evidence_type: "", reference: null, obtained_on: null, mechanism: null, notes: null },
          ])
        }
      >
        Agregar referencia de evidencia
      </button>
      <Text
        label="Notas del consentimiento"
        value={value.notes}
        onChange={(v) => update("notes", v || null)}
      />
    </fieldset>
  );
}
