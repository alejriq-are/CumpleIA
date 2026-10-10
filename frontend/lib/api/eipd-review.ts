import { apiFetch } from "./client";

export type EipdReviewDecision = "continuar" | "requiere_cambios" | "no_continuar";
export type EipdNegativeReviewIn = {
  decision: Exclude<EipdReviewDecision, "continuar">;
  rationale: string;
  review_reference: string;
};
export type EipdReviewContextMetadataV1 = {
  metadata_schema_version: 1;
  document_hash: string;
  context_hash: string;
} & (
  | {
      resolution_binding_version: 1;
      context_schema_version: 1;
      research_coverage: "no_cubierta";
      research_material_hash: null;
    }
  | {
      resolution_binding_version: 2;
      context_schema_version: 2;
      research_coverage: "contexto_v2";
      research_material_hash: string | null;
    }
);
export type EipdReviewIssueV3 = {
  stage:
    | "state"
    | "rat"
    | "ordinary"
    | "research"
    | "frontier"
    | "detection"
    | "resolution"
    | "sources"
    | "activation"
    | "review";
  field: string;
  code: string;
  category: "incompleto" | "requiere_revision" | "pendiente_revision" | "supuesto_declarado";
  question_id: string | null;
};
export type EipdReviewDecisionPrerequisitesV3 = {
  prerequisites_met: boolean;
  context_metadata: EipdReviewContextMetadataV1 | null;
  issues: EipdReviewIssueV3[];
};
export type EipdReviewPrerequisitesByDecisionV3 = {
  evaluation_version: 3;
  evaluation_scope: "requisitos_documentales";
  authorizes_action: false;
  can_confirm: false;
  continuar: EipdReviewDecisionPrerequisitesV3;
  requiere_cambios: EipdReviewDecisionPrerequisitesV3;
  no_continuar: EipdReviewDecisionPrerequisitesV3;
};
export type EipdReviewPreparationOut = {
  assessment_id: string;
  status: "borrador" | "confirmado" | "reemplazado";
  review_prerequisites_v3: EipdReviewPrerequisitesByDecisionV3 | null;
};
export type EipdResolutionReviewOutV2 = {
  response_schema_version: 2;
  id: string;
  organization_id: string;
  assessment_id: string;
  decision: EipdReviewDecision;
  rationale: string;
  review_reference: string;
  document_hash: string;
  context_hash: string;
  created_by: string;
  created_at: string;
  review_context_metadata: EipdReviewContextMetadataV1 | null;
} & (
  | { policy_version: null; policy_reference: null; policy_hash: null }
  | { policy_version: 1; policy_reference: string; policy_hash: string }
);
export type EipdReviewScope = {
  token: string;
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
};

const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const hash = /^[0-9a-f]{64}$/;
function requireContract(condition: unknown): asserts condition {
  if (!condition) throw new Error("Respuesta de revisión EIPD incompatible.");
}
function metadataValid(value: EipdReviewContextMetadataV1 | null): boolean {
  if (value === null) return true;
  return Boolean(
    value &&
    value.metadata_schema_version === 1 &&
    hash.test(value.document_hash) &&
    hash.test(value.context_hash) &&
    ((value.resolution_binding_version === 1 &&
      value.context_schema_version === 1 &&
      value.research_coverage === "no_cubierta" &&
      value.research_material_hash === null) ||
      (value.resolution_binding_version === 2 &&
        value.context_schema_version === 2 &&
        value.research_coverage === "contexto_v2" &&
        (value.research_material_hash === null || hash.test(value.research_material_hash))))
  );
}
function assessmentPath(scope: EipdReviewScope): string {
  if (
    !scope.token.trim() ||
    ![scope.organizationId, scope.treatmentId, scope.assessmentId].every((id) => uuid.test(id))
  )
    throw new Error("Sesión y organización/expediente válidos requeridos.");
  return `/licitud/treatments/${scope.treatmentId}/assessments/${scope.assessmentId}`;
}
function eventResponse(
  value: EipdResolutionReviewOutV2,
  scope: EipdReviewScope,
  reviewId?: string
): EipdResolutionReviewOutV2 {
  requireContract(
    value &&
      value.response_schema_version === 2 &&
      uuid.test(value.id) &&
      uuid.test(value.created_by) &&
      typeof value.organization_id === "string" &&
      value.organization_id.toLowerCase() === scope.organizationId.toLowerCase() &&
      typeof value.assessment_id === "string" &&
      value.assessment_id.toLowerCase() === scope.assessmentId.toLowerCase()
  );
  requireContract(!reviewId || value.id.toLowerCase() === reviewId.toLowerCase());
  requireContract(
    ["continuar", "requiere_cambios", "no_continuar"].includes(value.decision) &&
      typeof value.rationale === "string" &&
      value.rationale.trim() &&
      typeof value.review_reference === "string" &&
      value.review_reference.trim()
  );
  requireContract(
    hash.test(value.document_hash) &&
      hash.test(value.context_hash) &&
      typeof value.created_at === "string" &&
      /(?:Z|\+00:00)$/.test(value.created_at) &&
      !Number.isNaN(Date.parse(value.created_at))
  );
  requireContract(metadataValid(value.review_context_metadata));
  if (value.review_context_metadata !== null)
    requireContract(
      value.review_context_metadata.document_hash === value.document_hash &&
        value.review_context_metadata.context_hash === value.context_hash
    );
  requireContract(
    (value.policy_version === null &&
      value.policy_reference === null &&
      value.policy_hash === null) ||
      (value.policy_version === 1 &&
        typeof value.policy_reference === "string" &&
        value.policy_reference.trim() &&
        typeof value.policy_hash === "string" &&
        hash.test(value.policy_hash))
  );
  return value;
}

export const eipdReviewApi = {
  async preparation(scope: EipdReviewScope): Promise<EipdReviewPreparationOut> {
    const path = assessmentPath(scope);
    const value = await apiFetch<{
      assessment_id: string;
      status: EipdReviewPreparationOut["status"];
      eipd_controls_v3: {
        evaluation_version: 3;
        can_confirm: false;
        review_prerequisites_v3: EipdReviewPrerequisitesByDecisionV3;
      } | null;
    }>(path + "/readiness", {
      token: scope.token,
      organizationId: scope.organizationId,
      cache: "no-store",
    });
    requireContract(
      value &&
        typeof value.assessment_id === "string" &&
        value.assessment_id.toLowerCase() === scope.assessmentId.toLowerCase() &&
        ["borrador", "confirmado", "reemplazado"].includes(value.status)
    );
    const controls = value.eipd_controls_v3;
    if (controls !== null) {
      requireContract(
        controls && controls.evaluation_version === 3 && controls.can_confirm === false
      );
      const result = controls.review_prerequisites_v3;
      requireContract(
        result &&
          result.evaluation_version === 3 &&
          result.evaluation_scope === "requisitos_documentales" &&
          result.authorizes_action === false &&
          result.can_confirm === false
      );
      for (const decision of ["continuar", "requiere_cambios", "no_continuar"] as const) {
        const item = result[decision];
        requireContract(
          item &&
            typeof item.prerequisites_met === "boolean" &&
            Array.isArray(item.issues) &&
            metadataValid(item.context_metadata)
        );
        requireContract(item.prerequisites_met === (item.issues.length === 0));
        for (const issue of item.issues) {
          requireContract(
            issue &&
              [
                "state",
                "rat",
                "ordinary",
                "research",
                "frontier",
                "detection",
                "resolution",
                "sources",
                "activation",
                "review",
              ].includes(issue.stage) &&
              typeof issue.field === "string" &&
              typeof issue.code === "string" &&
              [
                "incompleto",
                "requiere_revision",
                "pendiente_revision",
                "supuesto_declarado",
              ].includes(issue.category) &&
              (issue.question_id === null || typeof issue.question_id === "string")
          );
        }
      }
    }
    return {
      assessment_id: value.assessment_id,
      status: value.status,
      review_prerequisites_v3: controls === null ? null : controls.review_prerequisites_v3,
    };
  },
  async event(scope: EipdReviewScope, reviewId: string): Promise<EipdResolutionReviewOutV2> {
    const path = assessmentPath(scope);
    if (!uuid.test(reviewId)) throw new Error("Identificador de revisión inválido.");
    const value = await apiFetch<EipdResolutionReviewOutV2>(
      `${path}/eipd-resolution/reviews/${reviewId}/v2`,
      { token: scope.token, organizationId: scope.organizationId, cache: "no-store" }
    );
    return eventResponse(value, scope, reviewId);
  },
  async recordNegative(
    scope: EipdReviewScope,
    request: EipdNegativeReviewIn
  ): Promise<EipdResolutionReviewOutV2> {
    const path = assessmentPath(scope);
    if (
      !["requiere_cambios", "no_continuar"].includes(request.decision) ||
      Object.keys(request).some(
        (key) => !["decision", "rationale", "review_reference"].includes(key)
      ) ||
      typeof request.rationale !== "string" ||
      !request.rationale.trim() ||
      typeof request.review_reference !== "string" ||
      !request.review_reference.trim()
    )
      throw new Error("La revisión negativa exige decisión, fundamento y referencia.");
    const body = {
      decision: request.decision,
      rationale: request.rationale,
      review_reference: request.review_reference,
    };
    const value = await apiFetch<EipdResolutionReviewOutV2>(path + "/eipd-resolution/reviews/v2", {
      token: scope.token,
      organizationId: scope.organizationId,
      method: "POST",
      body,
      cache: "no-store",
    });
    requireContract(value && value.decision === request.decision);
    return eventResponse(value, scope);
  },
};
