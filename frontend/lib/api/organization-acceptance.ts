import { apiFetch, ApiError } from "./client";
import type { ChildScope } from "./child-adolescent";
import type { ChildResolution } from "./child-eipd";
export type Authority = {
  id: string;
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  actor_id: string;
  created_by: string;
  created_at: string;
  revision: number;
  action: "otorgar" | "revocar";
  organization_role: "responsable" | "encargado";
  responsible_party_reference: string | null;
  faculty_reference: string;
  evidence_reference: string;
  data_kind: "ficticios";
  authorizes_action: false;
  can_confirm: false;
};
export type AuthorityState = {
  actor_id: string;
  may_designate: boolean;
  authorities: Authority[];
  authorizes_action: false;
  can_confirm: false;
};
export type Acceptance = {
  id: string;
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  actor_id: string;
  created_by: string;
  created_at: string;
  authority_id: string;
  resolution_id: string;
  decision: "acepta" | "rechaza" | "requiere_cambios";
  rationale: string;
  evidence_reference: string;
  document_hash: string;
  context_hash: string;
  child_material_hash: string;
  data_kind: "ficticios";
  material_status: "coincide" | "obsoleto" | "no_disponible";
  faculty_current: boolean;
  authorizes_action: false;
  can_confirm: false;
};
export type Designation = {
  actor_id: string;
  expected_revision: number;
  action: "otorgar" | "revocar";
  organization_role: "responsable" | "encargado";
  responsible_party_reference: string | null;
  faculty_reference: string;
  evidence_reference: string;
};
const uuid = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
function valid(x: unknown): asserts x {
  if (!x) throw new ApiError(502, "Respuesta de aceptación incompatible; EIPD bloqueada");
}
function path(scope: ChildScope) {
  if (![scope.organizationId, scope.treatmentId, scope.assessmentId].every((x) => uuid.test(x)))
    throw new ApiError(400, "Expediente no válido");
  return `/licitud/treatments/${scope.treatmentId}/assessments/${scope.assessmentId}/organization-acceptance/v1`;
}
function blocked(v: any) {
  valid(v && v.authorizes_action === false && v.can_confirm === false);
}
function identity(v: any, s: ChildScope) {
  blocked(v);
  valid(
    v.data_kind === "ficticios" &&
      [v.id, v.actor_id, v.created_by].every((x) => typeof x === "string" && uuid.test(x)) &&
      typeof v.created_at === "string" &&
      /(?:Z|\+00:00)$/.test(v.created_at) &&
      Number.isFinite(Date.parse(v.created_at))
  );
  for (const [a, b] of [
    [v.organization_id, s.organizationId],
    [v.treatment_id, s.treatmentId],
    [v.assessment_id, s.assessmentId],
  ])
    valid(a === b);
}
function authority(v: Authority, s: ChildScope) {
  identity(v, s);
  valid(
    Number.isSafeInteger(v.revision) &&
      v.revision > 0 &&
      ["otorgar", "revocar"].includes(v.action) &&
      ["responsable", "encargado"].includes(v.organization_role) &&
      typeof v.faculty_reference === "string" &&
      v.faculty_reference.trim() &&
      typeof v.evidence_reference === "string" &&
      v.evidence_reference.trim() &&
      (v.organization_role !== "encargado" ||
        (typeof v.responsible_party_reference === "string" && v.responsible_party_reference.trim()))
  );
  return v;
}
function acceptance(v: Acceptance, s: ChildScope, r: ChildResolution) {
  identity(v, s);
  valid(
    v.created_by === v.actor_id &&
      uuid.test(v.authority_id) &&
      v.resolution_id === r.id &&
      ["acepta", "rechaza", "requiere_cambios"].includes(v.decision) &&
      typeof v.rationale === "string" &&
      v.rationale.trim() &&
      typeof v.evidence_reference === "string" &&
      v.evidence_reference.trim() &&
      ["coincide", "obsoleto", "no_disponible"].includes(v.material_status) &&
      typeof v.faculty_current === "boolean"
  );
  for (const k of ["document_hash", "context_hash", "child_material_hash"] as const)
    valid(v[k] === r[k]);
  return v;
}
export const organizationAcceptanceApi = {
  load: async (s: ChildScope, r: ChildResolution) => {
    const [state, events] = await Promise.all([
      apiFetch<AuthorityState>(path(s) + "/authority", { ...s, cache: "no-store" }),
      apiFetch<Acceptance[]>(path(s) + `/resolutions/${r.id}/events`, { ...s, cache: "no-store" }),
    ]);
    blocked(state);
    valid(
      uuid.test(state.actor_id) &&
        typeof state.may_designate === "boolean" &&
        Array.isArray(state.authorities) &&
        Array.isArray(events)
    );
    state.authorities.forEach((v) => authority(v, s));
    events.forEach((v) => acceptance(v, s, r));
    valid(new Set(events.map((v) => v.id)).size === events.length);
    valid(new Set(state.authorities.map((v) => v.id)).size === state.authorities.length);
    return { state, events };
  },
  designate: async (s: ChildScope, actor: string, p: Designation) => {
    if (
      !uuid.test(p.actor_id) ||
      !Number.isSafeInteger(p.expected_revision) ||
      p.expected_revision < 0 ||
      !["otorgar", "revocar"].includes(p.action) ||
      !["responsable", "encargado"].includes(p.organization_role) ||
      !p.faculty_reference.trim() ||
      !p.evidence_reference.trim() ||
      (p.organization_role === "encargado" && !p.responsible_party_reference?.trim()) ||
      Object.keys(p).some(
        (k) =>
          ![
            "actor_id",
            "expected_revision",
            "action",
            "organization_role",
            "responsible_party_reference",
            "faculty_reference",
            "evidence_reference",
          ].includes(k)
      )
    )
      throw new ApiError(400, "Completa la facultad y sus referencias");
    const v = authority(
      await apiFetch<Authority>(path(s) + "/authority", {
        ...s,
        method: "POST",
        body: { data_kind: "ficticios", ...p },
      }),
      s
    );
    valid(
      v.created_by === actor &&
        v.actor_id === p.actor_id &&
        v.revision === p.expected_revision + 1 &&
        v.action === p.action &&
        v.organization_role === p.organization_role &&
        v.faculty_reference === p.faculty_reference &&
        v.evidence_reference === p.evidence_reference &&
        v.responsible_party_reference === p.responsible_party_reference
    );
    return v;
  },
  record: async (
    s: ChildScope,
    r: ChildResolution,
    actor: string,
    p: {
      authority_id: string;
      decision: Acceptance["decision"];
      rationale: string;
      evidence_reference: string;
    }
  ) => {
    if (
      !uuid.test(p.authority_id) ||
      !["acepta", "rechaza", "requiere_cambios"].includes(p.decision) ||
      !p.rationale.trim() ||
      !p.evidence_reference.trim() ||
      Object.keys(p).some(
        (k) => !["authority_id", "decision", "rationale", "evidence_reference"].includes(k)
      )
    )
      throw new ApiError(400, "Completa decisión, fundamento y evidencia");
    const v = acceptance(
      await apiFetch<Acceptance>(path(s) + `/resolutions/${r.id}/events`, {
        ...s,
        method: "POST",
        body: { data_kind: "ficticios", ...p },
      }),
      s,
      r
    );
    valid(
      v.actor_id === actor &&
        v.authority_id === p.authority_id &&
        v.decision === p.decision &&
        v.rationale === p.rationale &&
        v.evidence_reference === p.evidence_reference
    );
    return v;
  },
};
