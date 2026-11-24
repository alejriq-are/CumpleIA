"use client";
import { useRef, type ReactNode } from "react";
import type { VersionMaterial } from "@/lib/api/eipd-versions";
import { documentFields, type Fields } from "@/lib/licitud/eipd-document";
import {
  documentDisclosureClass,
  documentNavigationButtonClass,
  focusDocumentSection,
} from "./document-focus";

const object = (v: unknown): Record<string, unknown> =>
  v !== null && typeof v === "object" && !Array.isArray(v) ? (v as Record<string, unknown>) : {};
const list = (v: unknown): unknown[] => (Array.isArray(v) ? v : []);
const names: Record<string, string> = {
  purpose: "Finalidad",
  organization_role: "Rol de la organización",
  data_categories: "Categorías de datos",
  data_subjects: "Personas a quienes conciernen los datos",
  data_sources: "Fuentes de los datos",
  retention: "Conservación y eliminación",
  retention_rule: "Plazo o criterio de conservación",
  deletion_method: "Método de eliminación",
  systems: "Sistemas utilizados",
  third_parties: "Terceros",
  international_transfers: "Transferencias internacionales",
  automated_decisions: "Decisiones automatizadas",
  has_automated_decisions: "Existen decisiones automatizadas",
  special_regimes: "Características especiales del alcance",
  has_sensitive_data: "Incluye datos sensibles",
  is_sensitive: "Es dato sensible",
  includes_children: "Incluye niños y niñas",
  includes_adolescents: "Incluye adolescentes",
  has_vulnerable_groups: "Incluye grupos vulnerables",
  is_vulnerable_group: "Es grupo vulnerable",
  category_code: "Código de categoría",
  category_name: "Categoría",
  source_type: "Tipo de fuente",
  description: "Descripción",
  is_public_source: "Es fuente pública",
  name: "Nombre",
  provider: "Proveedor",
  hosting_location: "Ubicación del alojamiento",
  hosting_country: "País de alojamiento",
  is_international: "Es internacional",
  vendor_name: "Nombre del tercero",
  country: "País",
  relationship_type: "Relación con el tercero",
  has_data_access: "Tiene acceso a datos",
  has_contract: "Existe contrato",
  contract_reference: "Referencia del contrato",
  engagement_object: "Objeto del encargo",
  engagement_duration: "Duración del encargo",
  has_subprocessors: "Tiene subencargados",
  recipient_name: "Destinatario",
  destination_country: "País de destino",
  adequacy_status: "Estado de adecuación",
  mechanism: "Mecanismo",
  guarantees_description: "Garantías",
  evidence_reference: "Referencia del respaldo",
  notes: "Notas",
  eipd: "EIPD",
  infancia: "Infancia y adolescencia",
  state: "Determinación",
  reason: "Fundamento",
  current: "Correspondencia con el alcance al registrar",
  history: "Historial conservado de determinaciones",
  revision: "Revisión",
  created_at: "Fecha de registro (UTC)",
  created_by: "Persona que registró",
  policy: "Reglas conservadas",
  policy_reference: "Referencia de las reglas",
  policy_version: "Versión de las reglas",
  policy_hash: "Huella de las reglas",
  sources_status: "Estado de las fuentes",
  acceptance_status: "Estado de aceptación",
  activation: "Activación",
  allowed_decisions: "Resultados permitidos por estas reglas",
  global_policy_identity: "Reglas generales de referencia",
  authorizes_action: "Autoriza una actuación",
  can_confirm: "Permite confirmar",
  editable: "Era editable al registrar",
  reference: "Referencia",
  rule_set: "Reglas del diagnóstico",
  readiness: "Diagnóstico conservado",
  result: "Resultado",
  context_current: "Correspondencia documental al registrar",
  rat_context_current: "Correspondencia con RAT al registrar",
  eipd_resolution: "Requisitos del documento EIPD",
  issues: "Observaciones",
  field: "Campo observado",
  code: "Código de la observación",
  category: "Clase de observación",
  message: "Descripción",
  confirmation_blockers: "Bloqueos de confirmación",
  pending_controls: "Controles pendientes",
  applicability: "Aplicabilidad de los requisitos",
  status: "Estado",
  legal_basis: "Base jurídica propuesta",
  kind: "Tipo de antecedente",
  payload: "Contenido conservado",
  document_hash: "Huella del documento",
  id: "Identificador",
  organization_id: "Organización",
  treatment_id: "Tratamiento",
  assessment_id: "Evaluación de origen",
  context_hash: "Huella del contexto",
  schema_version: "Versión del formato",
  policy_schema_version: "Versión del formato de reglas",
  version: "Versión",
  support_records: "Valoraciones y anexos",
};
const choices: Record<string, string> = {
  completo: "Completo",
  incompleto: "Incompleto",
  requiere_revision: "Requiere revisión",
  corresponde: "Corresponde",
  no_corresponde: "No corresponde",
  pendiente: "Pendiente",
  informacion_insuficiente: "Información insuficiente",
  deshabilitada: "Deshabilitada",
  requiere_cambios: "Requiere cambios",
  no_continuar: "No continuar",
  favorable: "Favorable",
  responsable: "Responsable",
  encargado: "Encargado",
  titular: "Titular",
  tercero: "Tercero",
  fuente_publica: "Fuente pública",
  recogida_automatica: "Recogida automática",
  otro: "Otro",
  borrador: "Borrador",
  risk_assessment: "Valoración de riesgos",
  attachment: "Anexo",
  applicability: "Determinación de aplicabilidad",
};
function text(v: unknown, empty = "Sin información conservada"): string {
  if (v === null || v === undefined || v === "") return empty;
  if (typeof v === "boolean") return v ? "Sí" : "No";
  return choices[String(v)] ?? String(v);
}
function label(key: string) {
  return (
    names[key] ??
    documentFields[key]?.label ??
    key.replaceAll("_", " ").replace(/^./, (c) => c.toUpperCase())
  );
}
function description(v: unknown): string {
  if (Array.isArray(v)) return v.length ? `${v.length} elementos` : "Sin elementos conservados";
  if (v !== null && typeof v === "object") return "Abrir detalle";
  return text(v);
}
/** Objects and lists expand only on request; leaves are plain text, never form controls. */
function CompactData({ value }: { value: unknown }) {
  if (Array.isArray(value)) {
    if (!value.length) return <p>Sin elementos conservados.</p>;
    return (
      <ol className="list-decimal space-y-2 pl-5">
        {value.map((v, i) => {
          const row = object(v);
          const title =
            row.category_name ??
            row.name ??
            row.vendor_name ??
            row.reference ??
            row.description ??
            row.kind;
          return (
            <li key={i} className="min-w-0 break-words">
              {v !== null && typeof v === "object" ? (
                <details>
                  <summary className={documentDisclosureClass}>
                    {title ? text(title) : `Elemento ${i + 1}`}
                  </summary>
                  <div className="mt-2">
                    <CompactData value={v} />
                  </div>
                </details>
              ) : (
                text(v)
              )}
            </li>
          );
        })}
      </ol>
    );
  }
  if (value !== null && typeof value === "object") {
    const entries = Object.entries(object(value));
    if (!entries.length) return <p>Sin información conservada.</p>;
    return (
      <dl className="space-y-3">
        {entries.map(([key, v]) => {
          const nested = v !== null && typeof v === "object";
          return (
            <div key={key} className="min-w-0 break-words">
              {nested ? (
                <>
                  <dt>
                    <details>
                      <summary className={documentDisclosureClass}>
                        {label(key)} · {description(v)}
                      </summary>
                      <div className="mt-3 border-l-2 border-slate-200 pl-3">
                        <CompactData value={v} />
                      </div>
                    </details>
                  </dt>
                  <dd className="sr-only">Detalle disponible en el desplegable anterior.</dd>
                </>
              ) : (
                <>
                  <dt className="font-semibold">{label(key)}</dt>
                  <dd className="whitespace-pre-wrap break-words">{text(v)}</dd>
                </>
              )}
            </div>
          );
        })}
      </dl>
    );
  }
  return <p className="whitespace-pre-wrap break-words">{text(value)}</p>;
}
function Section({
  title,
  summary,
  children,
}: {
  title: string;
  summary: string;
  children: ReactNode;
}) {
  return (
    <details className="rounded border border-slate-200 bg-white p-2">
      <summary className={documentDisclosureClass}>
        <span className="font-semibold">{title}</span>
        <span className="mt-1 block text-sm font-normal">{summary}</span>
      </summary>
      <div className="space-y-3 px-2 py-3">{children}</div>
    </details>
  );
}
function fieldName(path: string) {
  let fields: Fields = documentFields;
  const labels: string[] = [];
  for (const part of path.split(/[.\[\]]/).filter(Boolean)) {
    const field = fields[part];
    if (field) {
      labels.push(field.label);
      fields = field.fields ?? field.item ?? {};
    } else if (/^\d+$/.test(part)) labels.push(`Elemento ${Number(part) + 1}`);
  }
  return labels.join(" — ") || "Antecedentes del documento";
}
export function EipdVersionContext({ value }: { value: VersionMaterial }) {
  const root = useRef<HTMLDetailsElement>(null);
  const rat = object(value.saved_assessment.rat_context_snapshot);
  const eipd = object(value.applicability.eipd);
  const diagnostic = object(value.diagnostic.readiness);
  const doc = object(diagnostic.eipd_resolution);
  const issues = list(doc.issues);
  const policy = object(value.policy.policy);
  const global = object(policy.global_policy_identity);
  const policyReference =
    global.policy_reference ?? policy.policy_reference ?? value.policy.reference;
  const sources = value.support_records;
  const issueGroups = new Map<string, unknown[]>();
  for (const issue of issues) {
    const rootField = String(object(issue).field ?? "").split(/[.\[\]]/)[0];
    const title = documentFields[rootField]?.label ?? "Contexto y correspondencia del documento";
    issueGroups.set(title, [...(issueGroups.get(title) ?? []), issue]);
  }
  const supportGroups = new Map<string, unknown[]>();
  for (const source of sources) {
    const title = text(source.kind, "Otros antecedentes");
    supportGroups.set(title, [...(supportGroups.get(title) ?? []), source]);
  }
  const knownRat = [
    "purpose",
    "retention",
    "data_categories",
    "data_subjects",
    "data_sources",
    "systems",
    "third_parties",
    "international_transfers",
    "automated_decisions",
    "special_regimes",
    "organization_role",
  ];
  const extraRat = Object.fromEntries(Object.entries(rat).filter(([k]) => !knownRat.includes(k)));
  return (
    <details ref={root} className="space-y-3">
      <summary className={documentDisclosureClass}>
        Contexto y antecedentes conservados con la versión
      </summary>
      <p>
        Consulta de solo lectura. Estos antecedentes corresponden al momento del registro. Abre
        únicamente el apartado que necesites; los cambios posteriores del borrador no se incluyen.
      </p>
      <Section
        title="Alcance RAT guardado"
        summary={
          Array.isArray(rat.data_categories) && Array.isArray(rat.data_subjects)
            ? `${rat.data_categories.length} ${rat.data_categories.length === 1 ? "categoría" : "categorías"} de datos · ${rat.data_subjects.length} ${rat.data_subjects.length === 1 ? "categoría" : "categorías"} de titulares`
            : "Consulta del alcance conservado al registrar"
        }
      >
        <dl className="space-y-3">
          <div>
            <dt className="font-semibold">Finalidad</dt>
            <dd className="whitespace-pre-wrap break-words">{text(rat.purpose)}</dd>
          </div>
          <div>
            <dt className="font-semibold">Plazo o criterio de conservación</dt>
            <dd className="whitespace-pre-wrap break-words">
              {text(object(rat.retention).retention_rule)}
            </dd>
          </div>
          <div>
            <dt className="font-semibold">Método de eliminación</dt>
            <dd className="whitespace-pre-wrap break-words">
              {text(object(rat.retention).deletion_method)}
            </dd>
          </div>
        </dl>
        <CompactData
          value={Object.fromEntries(
            knownRat
              .filter((k) => !["purpose", "retention"].includes(k) && k in rat)
              .map((k) => [k, rat[k]])
          )}
        />
        {!!Object.keys(object(rat.retention)).filter(
          (k) => !["retention_rule", "deletion_method"].includes(k)
        ).length && (
          <Section title="Otros antecedentes de conservación" summary="Detalle conservado">
            <CompactData value={rat.retention} />
          </Section>
        )}
        {!!Object.keys(extraRat).length && (
          <Section title="Otros antecedentes del alcance" summary="Detalle conservado">
            <CompactData value={extraRat} />
          </Section>
        )}
      </Section>
      <Section
        title="Determinación de aplicabilidad"
        summary={`EIPD: ${text(eipd.state ?? (typeof value.applicability.eipd === "string" ? value.applicability.eipd : undefined))}`}
      >
        <p className="whitespace-pre-wrap break-words">
          <strong>Fundamento: </strong>
          {text(eipd.reason)}
        </p>
        <Section
          title="Detalle de la determinación conservada"
          summary="Incluye infancia, correspondencia e historial al registrar"
        >
          <CompactData value={value.applicability} />
        </Section>
      </Section>
      <Section
        title="Diagnóstico al registrar"
        summary={
          Object.keys(doc).length
            ? `Documento EIPD: ${text(doc.result)} · ${issues.length} observaciones`
            : "No hay un resultado documental EIPD conservado"
        }
      >
        <p>
          Es el diagnóstico conservado con esta versión; no es una evaluación del borrador actual.
        </p>
        {Array.from(issueGroups, ([title, group]) => (
          <Section key={title} title={title} summary={`${group.length} observaciones documentales`}>
            <ul className="list-disc space-y-2 pl-5">
              {group.map((v, i) => {
                const issue = object(v);
                const name = fieldName(String(issue.field ?? ""));
                return (
                  <li key={i}>
                    {typeof issue.message === "string"
                      ? issue.message
                      : `${name}: ${issue.category === "incompleto" ? "falta completar o fundamentar este dato." : "requiere revisar sus antecedentes."}`}
                  </li>
                );
              })}
            </ul>
          </Section>
        ))}
        <Section
          title="Otros controles y detalle del diagnóstico"
          summary="Consulta cada control por separado"
        >
          <CompactData value={value.diagnostic} />
        </Section>
      </Section>
      <Section
        title="Política consultada"
        summary={text(policyReference, "Sin referencia de reglas conservada")}
      >
        <p>
          Reglas conservadas al registrar. Su presencia no acredita aceptación ni activación de la
          EIPD.
        </p>
        <CompactData value={value.policy} />
      </Section>
      <Section
        title="Índice de valoraciones y anexos consultados"
        summary={`${sources.length} antecedentes conservados en el índice`}
      >
        <p>
          Este índice conserva las referencias consultadas al registrar; no incorpora archivos
          nuevos ni acredita la eficacia de las medidas.
        </p>
        {!sources.length && <p>Sin elementos conservados.</p>}
        {Array.from(supportGroups, ([title, group]) => (
          <Section key={title} title={title} summary={`${group.length} antecedentes`}>
            <CompactData value={group} />
          </Section>
        ))}
      </Section>
      <button
        type="button"
        className={documentNavigationButtonClass}
        onClick={() => {
          if (!root.current) return;
          root.current.open = false;
          focusDocumentSection(root.current.querySelector("summary"));
        }}
      >
        Cerrar antecedentes y volver a revisiones
      </button>
    </details>
  );
}
