"use client";
import type { Support } from "@/lib/api/assessment-support";
import type { Dossier } from "@/lib/api/mvp-dossier";
import { legalBases } from "@/lib/api/licitud";
import { liaFields } from "@/lib/licitud/lia-fields";
import { EipdDocumentView } from "./EipdDocumentFields";

type Value = Record<string, unknown>;
export function record(value: unknown): Value {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Value) : {};
}
const names: Record<string, string> = {
  category_code: "Código de categoría",
  category_name: "Categoría",
  source_type: "Tipo de fuente",
  description: "Descripción",
  name: "Nombre",
  purpose: "Finalidad",
  source: "Fuente",
  notes: "Notas",
  code: "Código",
  includes_children: "Incluye niños o niñas",
  includes_adolescents: "Incluye adolescentes",
  includes_sensitive_data: "Incluye datos sensibles",
  includes_biometrics: "Incluye datos biométricos",
  organization_role: "Rol de la organización",
  role: "Rol",
  system_name: "Sistema",
  retention_period: "Plazo de conservación",
  retention_criteria: "Criterios de conservación",
  period: "Plazo",
  criteria: "Criterios",
  country: "País",
  recipient: "Destinatario",
  provider: "Proveedor",
  legal_basis: "Base propuesta",
  rationale: "Fundamento",
  answer: "Respuesta",
  reference: "Referencia",
  measures: "Medidas",
  public_benefit: "Beneficio declarado",
};
const choices: Record<string, string> = {
  si: "Sí",
  no: "No",
  pendiente: "Pendiente",
  borrador: "Borrador",
  confirmado: "Confirmado",
  reemplazado: "Reemplazado",
};
function ValueView({ value }: { value: unknown }) {
  if (value == null || value === "" || (Array.isArray(value) && !value.length))
    return <span>Sin información registrada</span>;
  if (typeof value === "boolean") return <span>{value ? "Sí" : "No"}</span>;
  if (Array.isArray(value))
    return (
      <ul className="list-disc space-y-2 pl-5">
        {value.map((item, i) => (
          <li key={i}>
            <ValueView value={item} />
          </li>
        ))}
      </ul>
    );
  if (typeof value === "object")
    return (
      <dl className="space-y-2">
        {Object.entries(record(value))
          .filter(
            ([key]) =>
              ![
                "id",
                "organization_id",
                "treatment_id",
                "schema_version",
                "context_binding",
              ].includes(key)
          )
          .map(([key, item]) => (
            <div key={key}>
              <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
                {names[key] ?? "Otro antecedente registrado"}
              </dt>
              <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
                <ValueView value={item} />
              </dd>
            </div>
          ))}
      </dl>
    );
  return (
    <span className="whitespace-pre-wrap break-words">
      {choices[String(value)] ?? String(value)}
    </span>
  );
}
function Field({ label, value }: { label: string; value: unknown }) {
  return (
    <div>
      <dt className="rounded-t border border-blue-200 bg-blue-100 px-3 py-2 font-semibold text-blue-950">
        {label}
      </dt>
      <dd className="rounded-b border border-t-0 border-blue-200 bg-white px-3 py-3 whitespace-pre-wrap break-words text-slate-950">
        <ValueView value={value} />
      </dd>
    </div>
  );
}
export function DossierDocumentView({
  document: entry,
  support,
}: {
  document: Dossier["documents"][number];
  support?: Support | null;
}) {
  if (entry.status !== "disponible" || !entry.content) return <p>No hay documento guardado.</p>;
  const value = record(entry.content);
  if (entry.kind === "eipd") {
    const document = value.document ? record(value.document) : value;
    return (
      <div className="space-y-3">
        <dl className="space-y-3">
          <Field
            label="Referencia del documento EIPD"
            value={value.document_reference ?? document.document_reference}
          />
          <Field
            label="Etiqueta del documento EIPD"
            value={value.document_version ?? document.document_version}
          />
        </dl>
        <EipdDocumentView
          value={document}
          expanded
          valuation={value.document ? null : support?.risk_evaluation}
        />
        <dl>
          <Field label="Notas del documento" value={document.notes ?? value.notes} />
        </dl>
        {!Array.isArray(document.risks) || !document.risks.length ? (
          <p>Sin riesgos registrados.</p>
        ) : null}
        {!Array.isArray(document.measures) || !document.measures.length ? (
          <p>Sin medidas registradas.</p>
        ) : null}
      </div>
    );
  }
  if (entry.kind === "rat")
    return (
      <dl className="space-y-4">
        {(
          [
            ["purpose", "Finalidad"],
            ["data_subjects", "Titulares"],
            ["data_categories", "Categorías de datos"],
            ["data_sources", "Fuentes"],
            ["systems", "Sistemas"],
            ["retention", "Conservación"],
            ["third_parties", "Terceros"],
            ["international_transfers", "Transferencias internacionales"],
            ["special_regimes", "Condiciones especiales"],
            ["organization_role", "Rol de la organización"],
            ["automated_decisions", "Decisiones automatizadas"],
          ] as const
        ).map(([key, label]) => (
          <Field key={key} label={label} value={value[key]} />
        ))}
      </dl>
    );
  return (
    <div className="space-y-4">
      <dl className="space-y-4">
        <Field label="Finalidad evaluada" value={value.purpose_snapshot} />
        <Field label="Estado de la evaluación" value={value.status} />
        <Field
          label="Base de licitud propuesta"
          value={
            value.legal_basis
              ? (legalBases.find(([code]) => code === value.legal_basis)?.[1] ??
                "Base registrada; consultar antecedentes")
              : "Pendiente de definir"
          }
        />
        <Field label="Fundamento" value={value.justification} />
      </dl>
      {value.lia_assessment != null && (
        <section aria-label="Análisis de interés legítimo">
          <h4 className="font-semibold">Análisis de interés legítimo</h4>
          <dl className="space-y-3">
            {liaFields.map(([group, key, label]) => (
              <Field
                key={key}
                label={label}
                value={record(record(value.lia_assessment)[group])[key]}
              />
            ))}
          </dl>
        </section>
      )}
      <p>
        Esta vista resume la evaluación. La descarga y el detalle técnico conservan todos los
        antecedentes guardados.
      </p>
    </div>
  );
}
