import { apiFetch, ApiError } from "./client";
import type { ChildScope } from "./child-adolescent";
import type { Dossier } from "./mvp-dossier";
import type { AuthorityState } from "./organization-acceptance";
export const pilotReferences = {
  review_reference: "Referencia de revisión jurídica ficticia",
  environment_reference: "Referencia de entorno",
  access_reference: "Referencia de control de accesos",
  restore_reference: "Referencia de restauración",
  retention_reference: "Referencia de retención",
  support_reference: "Referencia de soporte",
  incident_reference: "Referencia de incidentes",
};
export type PilotForm = {
  review_decision: "acepta" | "rechaza" | "requiere_cambios" | "pendiente";
} & Record<keyof typeof pilotReferences, string | null>;
export type PilotResult = {
  schema_version: 1;
  data_kind: "ficticios";
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  actor_id: string;
  authority_id: string;
  authority_evidence_reference: string;
  document_hashes: Record<string, string | null>;
  declared_references: Record<string, string | null>;
  review_decision: string;
  missing: string[];
  preparation_complete: boolean;
  evidence_status: "declarada_no_verificada";
  persistence: "simulacion_no_registrada";
  legal_acceptance: "pendiente_organizacion_piloto";
  mvp_ready: false;
  allows_real_data: false;
  can_confirm: false;
  authorizes_action: false;
  activation: "deshabilitada";
};
function valid(v: unknown): asserts v {
  if (!v) throw new ApiError(502, "Preparación incompatible; no hay aprobación real");
}
const uuid = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
export async function preparePilot(
  s: ChildScope,
  packet: Dossier,
  form: PilotForm
): Promise<PilotResult> {
  if (
    ![s.organizationId, s.treatmentId, s.assessmentId].every((x) => uuid.test(x)) ||
    packet.organization_id !== s.organizationId ||
    packet.treatment_id !== s.treatmentId ||
    packet.assessment_id !== s.assessmentId
  )
    throw new ApiError(400, "Expediente no válido");
  const prefix = `/licitud/treatments/${s.treatmentId}/assessments/${s.assessmentId}`;
  const state = await apiFetch<AuthorityState>(prefix + "/organization-acceptance/v1/authority", {
    ...s,
    cache: "no-store",
  });
  valid(
    state &&
      uuid.test(state.actor_id) &&
      state.can_confirm === false &&
      state.authorizes_action === false &&
      Array.isArray(state.authorities)
  );
  state.authorities.forEach((g) =>
    valid(
      g.organization_id === s.organizationId &&
        g.treatment_id === s.treatmentId &&
        g.assessment_id === s.assessmentId &&
        uuid.test(g.id) &&
        uuid.test(g.actor_id) &&
        Number.isSafeInteger(g.revision) &&
        g.revision > 0 &&
        ["otorgar", "revocar"].includes(g.action) &&
        g.can_confirm === false &&
        g.authorizes_action === false &&
        g.data_kind === "ficticios"
    )
  );
  const grant = state.authorities
    .filter((g) => g.actor_id === state.actor_id)
    .sort((a, b) => b.revision - a.revision)[0];
  if (!grant || grant.action !== "otorgar")
    throw new ApiError(403, "Registra primero una facultad ficticia vigente para tu usuario");
  const hashes = Object.fromEntries(packet.documents.map((d) => [d.kind, d.content_hash]));
  const refs = Object.fromEntries(
    Object.keys(pilotReferences).map((k) => [
      k,
      form[k as keyof typeof pilotReferences]?.trim() || null,
    ])
  );
  const v = await apiFetch<PilotResult>(prefix + "/pilot-preparation/v1", {
    ...s,
    method: "POST",
    body: {
      data_kind: "ficticios",
      authority_id: grant.id,
      document_hashes: hashes,
      review_decision: form.review_decision,
      ...refs,
    },
  });
  valid(
    v &&
      v.schema_version === 1 &&
      v.data_kind === "ficticios" &&
      v.organization_id === s.organizationId &&
      v.treatment_id === s.treatmentId &&
      v.assessment_id === s.assessmentId &&
      v.actor_id === state.actor_id &&
      v.authority_id === grant.id &&
      v.can_confirm === false &&
      v.authorizes_action === false &&
      v.mvp_ready === false &&
      v.allows_real_data === false &&
      v.activation === "deshabilitada" &&
      v.evidence_status === "declarada_no_verificada" &&
      v.persistence === "simulacion_no_registrada" &&
      v.legal_acceptance === "pendiente_organizacion_piloto" &&
      v.review_decision === form.review_decision &&
      typeof v.preparation_complete === "boolean" &&
      Array.isArray(v.missing) &&
      v.missing.every((x) => typeof x === "string") &&
      v.preparation_complete === (v.missing.length === 0)
  );
  const expectedMissing = [
    ...Object.keys(refs).filter((k) => !refs[k]),
    ...Object.keys(hashes).filter((k) => hashes[k] === null),
    ...(form.review_decision === "acepta" ? [] : ["revision_juridica_ficticia_no_aceptada"]),
  ];
  valid(JSON.stringify(v.missing) === JSON.stringify(expectedMissing));
  for (const k of Object.keys(hashes)) valid(v.document_hashes?.[k] === hashes[k]);
  for (const k of Object.keys(refs)) valid(v.declared_references?.[k] === refs[k]);
  return v;
}
