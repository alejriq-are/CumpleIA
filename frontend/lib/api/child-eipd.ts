import { apiFetch, ApiError } from "./client";
import type { ChildScope } from "./child-adolescent";
export type ResolutionDraft = {
  schema_version: 1;
  document_reference: string | null;
  document_version: string | null;
  notes: string | null;
};
export type NegativeDecision = "requiere_cambios" | "no_continuar";
type Identity = {
  id: string;
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  data_kind: "ficticios";
  document_hash: string;
  context_hash: string;
  child_material_hash: string;
  created_by: string;
  created_at: string;
  authorizes_action: false;
  can_confirm: false;
};
export type ChildPolicy = {
  policy: {
    policy_schema_version: 1;
    policy_reference: "m3-t1-infancia-pruebas-negativas-v1";
    sources_status: "pendiente";
    acceptance_status: "pendiente";
    activation: "deshabilitada";
    allowed_decisions: ["requiere_cambios", "no_continuar"];
    global_policy_identity: { policy_version: 1; policy_reference: string; policy_hash: string };
  };
  policy_hash: string;
  authorizes_action: false;
  can_confirm: false;
};
export type ChildResolution = Identity & {
  version: number;
  resolution_binding_version: 4;
  stored_coverage: "contexto_v4";
  document: Record<string, unknown>;
  context_snapshot: {
    context_schema_version: 4;
    organization_id: string;
    treatment_id: string;
    assessment_id: string;
    child_adolescent_assessment: unknown;
  };
};
export type ChildReview = Identity & {
  response_schema_version: 4;
  resolution_id: string;
  decision: NegativeDecision;
  rationale: string;
  review_reference: string;
  policy_snapshot: ChildPolicy["policy"];
  policy_hash: string;
  review_context_metadata: {
    metadata_schema_version: 3;
    resolution_binding_version: 4;
    context_schema_version: 4;
    child_coverage: "contexto_v4";
    document_hash: string;
    context_hash: string;
    child_material_hash: string;
    policy_hash: string;
  };
};
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const hash = /^[0-9a-f]{64}$/;
function valid(condition: unknown): asserts condition {
  if (!condition)
    throw new ApiError(502, "Respuesta de historial incompatible; EIPD permanece bloqueada");
}
function id(value: string) {
  if (typeof value !== "string" || !uuid.test(value))
    throw new ApiError(400, "Identificador no válido");
  return value;
}
function path(scope: ChildScope) {
  id(scope.organizationId);
  if (typeof scope.token !== "string" || !scope.token.trim())
    throw new ApiError(401, "Sesión no disponible");
  return `/licitud/treatments/${id(scope.treatmentId)}/assessments/${id(scope.assessmentId)}/eipd-child/v4`;
}
function identity(value: Identity, scope: ChildScope) {
  valid(
    value &&
      uuid.test(value.id) &&
      uuid.test(value.created_by) &&
      value.data_kind === "ficticios" &&
      value.authorizes_action === false &&
      value.can_confirm === false
  );
  for (const [actual, expected] of [
    [value.organization_id, scope.organizationId],
    [value.treatment_id, scope.treatmentId],
    [value.assessment_id, scope.assessmentId],
  ])
    valid(typeof actual === "string" && actual.toLowerCase() === expected.toLowerCase());
  valid(
    [value.document_hash, value.context_hash, value.child_material_hash].every(
      (h) => typeof h === "string" && hash.test(h)
    )
  );
  valid(
    typeof value.created_at === "string" &&
      /(?:Z|\+00:00)$/.test(value.created_at) &&
      Number.isFinite(Date.parse(value.created_at))
  );
}
export function validatePolicy(value: ChildPolicy): ChildPolicy {
  const p = value?.policy;
  valid(
    value &&
      value.authorizes_action === false &&
      value.can_confirm === false &&
      hash.test(value.policy_hash) &&
      p &&
      p.policy_schema_version === 1 &&
      p.policy_reference === "m3-t1-infancia-pruebas-negativas-v1" &&
      p.sources_status === "pendiente" &&
      p.acceptance_status === "pendiente" &&
      p.activation === "deshabilitada" &&
      Array.isArray(p.allowed_decisions) &&
      p.allowed_decisions.length === 2 &&
      p.allowed_decisions[0] === "requiere_cambios" &&
      p.allowed_decisions[1] === "no_continuar" &&
      p.global_policy_identity?.policy_version === 1 &&
      typeof p.global_policy_identity.policy_reference === "string" &&
      p.global_policy_identity.policy_reference.trim() &&
      hash.test(p.global_policy_identity.policy_hash)
  );
  return value;
}
export function validateResolution(
  value: ChildResolution,
  scope: ChildScope,
  expectedId?: string
): ChildResolution {
  identity(value, scope);
  const c = value.context_snapshot;
  valid(
    value.resolution_binding_version === 4 &&
      value.stored_coverage === "contexto_v4" &&
      Number.isSafeInteger(value.version) &&
      value.version > 0 &&
      value.document &&
      typeof value.document === "object" &&
      !Array.isArray(value.document) &&
      value.document.schema_version === 1 &&
      c &&
      c.context_schema_version === 4 &&
      c.child_adolescent_assessment &&
      typeof c.child_adolescent_assessment === "object" &&
      !Array.isArray(c.child_adolescent_assessment)
  );
  for (const key of ["organization_id", "treatment_id", "assessment_id"] as const)
    valid(typeof c[key] === "string" && c[key].toLowerCase() === value[key].toLowerCase());
  valid(!expectedId || value.id.toLowerCase() === expectedId.toLowerCase());
  return value;
}
export function validateReview(
  value: ChildReview,
  scope: ChildScope,
  resolution: ChildResolution
): ChildReview {
  identity(value, scope);
  valid(
    value.response_schema_version === 4 &&
      value.resolution_id === resolution.id &&
      ["requiere_cambios", "no_continuar"].includes(value.decision) &&
      typeof value.rationale === "string" &&
      value.rationale.trim() &&
      typeof value.review_reference === "string" &&
      value.review_reference.trim()
  );
  validatePolicy({
    policy: value.policy_snapshot,
    policy_hash: value.policy_hash,
    authorizes_action: value.authorizes_action,
    can_confirm: value.can_confirm,
  });
  const m = value.review_context_metadata;
  valid(
    m &&
      m.metadata_schema_version === 3 &&
      m.resolution_binding_version === 4 &&
      m.context_schema_version === 4 &&
      m.child_coverage === "contexto_v4"
  );
  for (const key of ["document_hash", "context_hash", "child_material_hash"] as const)
    valid(value[key] === resolution[key] && m[key] === value[key]);
  valid(m.policy_hash === value.policy_hash);
  return value;
}
export const childEipdApi = {
  policy: async (scope: ChildScope) =>
    validatePolicy(
      await apiFetch<ChildPolicy>(path(scope) + "/policy", { ...scope, cache: "no-store" })
    ),
  list: async (scope: ChildScope) => {
    const values = await apiFetch<ChildResolution[]>(path(scope) + "/resolutions", {
      ...scope,
      cache: "no-store",
    });
    valid(Array.isArray(values));
    const ids = new Set<string>(),
      versions = new Set<number>();
    return values.map((v) => {
      validateResolution(v, scope);
      valid(!ids.has(v.id.toLowerCase()) && !versions.has(v.version));
      ids.add(v.id.toLowerCase());
      versions.add(v.version);
      return v;
    });
  },
  create: async (scope: ChildScope, draft: ResolutionDraft) => {
    if (
      !draft ||
      draft.schema_version !== 1 ||
      Object.keys(draft).some(
        (k) => !["schema_version", "document_reference", "document_version", "notes"].includes(k)
      ) ||
      typeof draft.document_reference !== "string" ||
      !draft.document_reference.trim() ||
      [draft.document_version, draft.notes].some((v) => v != null && typeof v !== "string")
    )
      throw new ApiError(400, "Referencia documental requerida");
    const saved = validateResolution(
      await apiFetch<ChildResolution>(path(scope) + "/resolutions", {
        ...scope,
        cache: "no-store",
        method: "POST",
        body: { data_kind: "ficticios", document: draft },
      }),
      scope
    );
    valid(
      saved.document.document_reference === draft.document_reference &&
        (saved.document.document_version ?? null) === (draft.document_version ?? null) &&
        (saved.document.notes ?? null) === (draft.notes ?? null)
    );
    return saved;
  },
  reviews: async (scope: ChildScope, resolution: ChildResolution) => {
    validateResolution(resolution, scope);
    const values = await apiFetch<ChildReview[]>(
      path(scope) + `/resolutions/${id(resolution.id)}/reviews`,
      { ...scope, cache: "no-store" }
    );
    valid(Array.isArray(values));
    const ids = new Set<string>();
    return values.map((v) => {
      validateReview(v, scope, resolution);
      valid(!ids.has(v.id.toLowerCase()));
      ids.add(v.id.toLowerCase());
      return v;
    });
  },
  review: async (
    scope: ChildScope,
    resolution: ChildResolution,
    decision: NegativeDecision,
    rationale: string,
    reference: string
  ) => {
    validateResolution(resolution, scope);
    if (
      !["requiere_cambios", "no_continuar"].includes(decision) ||
      typeof rationale !== "string" ||
      !rationale.trim() ||
      typeof reference !== "string" ||
      !reference.trim()
    )
      throw new ApiError(400, "Decisión negativa, fundamento y referencia requeridos");
    const saved = validateReview(
      await apiFetch<ChildReview>(path(scope) + `/resolutions/${id(resolution.id)}/reviews`, {
        ...scope,
        cache: "no-store",
        method: "POST",
        body: { data_kind: "ficticios", decision, rationale, review_reference: reference },
      }),
      scope,
      resolution
    );
    valid(
      saved.decision === decision &&
        saved.rationale === rationale &&
        saved.review_reference === reference
    );
    return saved;
  },
};
