import { apiFetch, ApiError } from "./client";
export type ChildDocument = {
  schema_version?: 1;
  data_category_codes?: string[];
  data_subject_codes?: string[];
  declared_groups?: ("ninos_ninas" | "adolescentes" | "adolescentes_sensibles_menores_16")[];
  age_scope_analysis?: string | null;
  best_interests_analysis?: string | null;
  progressive_autonomy_analysis?: string | null;
  authorization_reference?: string | null;
  authorization_analysis?: string | null;
  notes?: string | null;
  sensitive_under16?: "si" | "no" | "pendiente" | null;
  proposed_authorization_route?: "consentimiento" | "autorizacion_legal_expresa" | null;
  declared_consent_giver?:
    "padre_madre" | "representante_legal" | "cuidado_personal" | "titular" | null;
  evidence?: {
    evidence_type: string;
    reference?: string | null;
    obtained_on?: string | null;
    mechanism?: string | null;
    notes?: string | null;
  }[];
};
export type ChildScope = {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  token: string;
};
export type ChildAssessment = {
  id: string;
  status: "borrador" | "confirmado" | "reemplazado";
  child_adolescent_assessment: {
    assessment: ChildDocument;
    context_binding: { context_hash: string; document_hash: string; binding_version: 1 };
  } | null;
  rat_context_snapshot: {
    data_categories: { category_code: string; category_name: string }[];
    data_subjects: { category_code: string; category_name: string }[];
  };
};
export type ChildReadiness = {
  eipd_controls_v5: null | {
    evaluation_version: 5;
    context_schema_version: 4;
    can_confirm: false;
    authorizes_action: false;
    context_hash: string | null;
    child_adolescent_coverage: "contexto_v4" | "contexto_actual_no_disponible";
    resolution_child_coverage: "no_cubierta";
    child_adolescent: {
      result: string;
      association_status: string;
      can_confirm: false;
      authorizes_action: false;
    };
    confirmation_blockers: { code: string; message: string }[];
    continuar: Decision;
    requiere_cambios: Decision;
    no_continuar: Decision;
  };
};
type Decision = {
  prerequisites_met: false;
  context_metadata: null;
  issues: { code: string; message: string }[];
};
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
function path(scope: ChildScope) {
  if (![scope.organizationId, scope.treatmentId, scope.assessmentId].every((x) => uuid.test(x)))
    throw new ApiError(400, "Expediente no válido");
  return `/licitud/treatments/${scope.treatmentId}/assessments/${scope.assessmentId}`;
}
export function validateChildReadiness(value: ChildReadiness): ChildReadiness {
  if (!value || !Object.prototype.hasOwnProperty.call(value, "eipd_controls_v5"))
    throw new ApiError(502, "Diagnóstico incompatible; no se habilitan acciones");
  const v = value.eipd_controls_v5;
  if (
    v &&
    (v.evaluation_version !== 5 ||
      v.context_schema_version !== 4 ||
      v.can_confirm !== false ||
      v.authorizes_action !== false ||
      v.resolution_child_coverage !== "no_cubierta" ||
      v.child_adolescent.can_confirm !== false ||
      v.child_adolescent.authorizes_action !== false ||
      !v.confirmation_blockers.some((i) => i.code === "politica_infancia_no_implementada") ||
      !["contexto_v4", "contexto_actual_no_disponible"].includes(v.child_adolescent_coverage) ||
      (v.child_adolescent_coverage === "contexto_v4"
        ? !v.context_hash || !/^[0-9a-f]{64}$/.test(v.context_hash)
        : v.context_hash !== null) ||
      [v.continuar, v.requiere_cambios, v.no_continuar].some(
        (d) =>
          d.prerequisites_met !== false ||
          d.context_metadata !== null ||
          !d.issues.some((i) => i.code === "politica_infancia_no_implementada")
      ))
  )
    throw new ApiError(502, "Diagnóstico incompatible; no se habilitan acciones");
  return value;
}
export const childApi = {
  load: (scope: ChildScope) =>
    apiFetch<ChildAssessment & Partial<import("./licitud").Assessment>>(path(scope), {
      ...scope,
      cache: "no-store",
    }),
  save: (scope: ChildScope, document: ChildDocument | null) =>
    apiFetch<ChildAssessment & Partial<import("./licitud").Assessment>>(path(scope), {
      ...scope,
      cache: "no-store",
      method: "PATCH",
      body: { child_adolescent_assessment: document },
    }),
  readiness: async (scope: ChildScope) =>
    validateChildReadiness(
      await apiFetch<ChildReadiness>(path(scope) + "/readiness", { ...scope, cache: "no-store" })
    ),
};
