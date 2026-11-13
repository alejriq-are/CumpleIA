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
    | "review"
    | "representation";
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
export type EipdReviewDecisionPrerequisitesV4 = Omit<
  EipdReviewDecisionPrerequisitesV3,
  "prerequisites_met" | "context_metadata"
> & { prerequisites_met: false; context_metadata: null };
export type EipdReviewPrerequisitesByDecisionV4 = Omit<
  EipdReviewPrerequisitesByDecisionV3,
  "evaluation_version" | "continuar" | "requiere_cambios" | "no_continuar"
> & {
  evaluation_version: 4;
  continuar: EipdReviewDecisionPrerequisitesV4;
  requiere_cambios: EipdReviewDecisionPrerequisitesV4;
  no_continuar: EipdReviewDecisionPrerequisitesV4;
};
export type EipdLatestReviewContextStatus =
  "sin_revision" | "sin_metadatos" | "vigente" | "obsoleta";
export type EipdPolicyStatus = {
  sources_status: "pendiente" | "verificadas";
  acceptance_status: "pendiente" | "aceptada";
  activation: "deshabilitada" | "habilitada";
};
export type SensitiveRepresentationReadiness = {
  evaluation_version: 1;
  evaluation_scope: "requisitos_documentales";
  authorizes_action: false;
  can_confirm: false;
  result: "no_aplicable" | "incompleto" | "requiere_revision" | "completo";
  issues: EipdReviewIssueV3[];
};
export type EipdReviewPreparationOut = {
  assessment_id: string;
  status: "borrador" | "confirmado" | "reemplazado";
  review_prerequisites_v3: EipdReviewPrerequisitesByDecisionV3 | null;
  review_prerequisites_v4?: EipdReviewPrerequisitesByDecisionV4 | null;
  current_control_issues_v4?: EipdReviewIssueV3[] | null;
  latest_review_context_status: EipdLatestReviewContextStatus | null;
  policy_status: EipdPolicyStatus | null;
  sensitive_representation: SensitiveRepresentationReadiness | null;
  representation_context_coverage: "no_aplica" | "pendiente";
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
      sensitive_representation?:
        | (Omit<SensitiveRepresentationReadiness, "issues"> & {
            issues: Array<{
              field: string;
              code: string;
              category: "incompleto" | "requiere_revision";
            }>;
          })
        | null;
      representation_context_coverage?: "no_aplica" | "pendiente";
      eipd_controls_v4?: {
        evaluation_version: 4;
        evaluation_scope: "requisitos_documentales";
        authorizes_action: false;
        can_confirm: false;
        policy: EipdPolicyStatus;
        preparation_issues: EipdReviewIssueV3[];
        review_blockers: EipdReviewIssueV3[];
        confirmation_blockers: EipdReviewIssueV3[];
        review_prerequisites_v4: EipdReviewPrerequisitesByDecisionV4;
      } | null;
      eipd_controls_v3: {
        evaluation_version: 3;
        can_confirm: false;
        review_prerequisites_v3: EipdReviewPrerequisitesByDecisionV3;
        review_context_metadata_status: EipdLatestReviewContextStatus;
        policy: EipdPolicyStatus;
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
    const rawRepresentation = value.sensitive_representation ?? null;
    const coverage = value.representation_context_coverage ?? "no_aplica";
    requireContract(["no_aplica", "pendiente"].includes(coverage));
    requireContract((coverage === "pendiente") === (rawRepresentation !== null));
    let representation: SensitiveRepresentationReadiness | null = null;
    if (rawRepresentation !== null) {
      requireContract(
        rawRepresentation.evaluation_version === 1 &&
          rawRepresentation.evaluation_scope === "requisitos_documentales" &&
          rawRepresentation.authorizes_action === false &&
          rawRepresentation.can_confirm === false &&
          ["no_aplicable", "incompleto", "requiere_revision", "completo"].includes(
            rawRepresentation.result
          ) &&
          Array.isArray(rawRepresentation.issues)
      );
      for (const issue of rawRepresentation.issues) {
        requireContract(
          issue &&
            typeof issue.field === "string" &&
            typeof issue.code === "string" &&
            ["incompleto", "requiere_revision"].includes(issue.category)
        );
      }
      const expected = rawRepresentation.issues.some(
        (issue) => issue.category === "requiere_revision"
      )
        ? "requiere_revision"
        : rawRepresentation.issues.length > 0
          ? "incompleto"
          : "completo";
      requireContract(
        rawRepresentation.result === expected ||
          (rawRepresentation.result === "no_aplicable" && rawRepresentation.issues.length === 0)
      );
      representation = {
        evaluation_version: 1,
        evaluation_scope: "requisitos_documentales",
        authorizes_action: false,
        can_confirm: false,
        result: rawRepresentation.result,
        issues: rawRepresentation.issues.map((issue) => ({
          ...issue,
          stage: "representation",
          question_id: null,
        })),
      };
    }
    const successor = value.eipd_controls_v4 ?? null;
    const controls = value.eipd_controls_v3;
    if (successor !== null) {
      requireContract(controls === null);
      requireContract(
        successor.evaluation_version === 4 &&
          successor.evaluation_scope === "requisitos_documentales" &&
          successor.authorizes_action === false &&
          successor.can_confirm === false
      );
      const result = successor.review_prerequisites_v4;
      requireContract(
        result &&
          result.evaluation_version === 4 &&
          result.evaluation_scope === "requisitos_documentales" &&
          result.authorizes_action === false &&
          result.can_confirm === false
      );
      for (const name of ["continuar", "requiere_cambios", "no_continuar"] as const) {
        const decision = result[name];
        requireContract(
          decision &&
            decision.prerequisites_met === false &&
            decision.context_metadata === null &&
            Array.isArray(decision.issues) &&
            decision.issues.length > 0
        );
        const collections =
          name === "continuar"
            ? [
                decision.issues,
                successor.preparation_issues,
                successor.review_blockers,
                successor.confirmation_blockers,
              ]
            : [decision.issues];
        for (const issues of collections) {
          requireContract(Array.isArray(issues));
          for (const issue of issues) {
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
      const policy = successor.policy;
      requireContract(
        policy &&
          ["pendiente", "verificadas"].includes(policy.sources_status) &&
          ["pendiente", "aceptada"].includes(policy.acceptance_status) &&
          policy.activation === "deshabilitada"
      );
    }
    if (controls !== null) {
      requireContract(
        controls &&
          controls.evaluation_version === 3 &&
          controls.can_confirm === false &&
          ["sin_revision", "sin_metadatos", "vigente", "obsoleta"].includes(
            controls.review_context_metadata_status
          )
      );
      const policy = controls.policy;
      requireContract(
        policy &&
          ["pendiente", "verificadas"].includes(policy.sources_status) &&
          ["pendiente", "aceptada"].includes(policy.acceptance_status) &&
          ["deshabilitada", "habilitada"].includes(policy.activation) &&
          (policy.activation !== "habilitada" ||
            (policy.sources_status === "verificadas" && policy.acceptance_status === "aceptada"))
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
      review_prerequisites_v4: successor?.review_prerequisites_v4 ?? null,
      current_control_issues_v4:
        successor === null
          ? null
          : [
              ...successor.preparation_issues,
              ...successor.review_blockers,
              ...successor.confirmation_blockers,
            ],
      review_prerequisites_v3:
        controls === null || coverage === "pendiente" ? null : controls.review_prerequisites_v3,
      sensitive_representation: representation,
      representation_context_coverage: coverage,
      policy_status:
        successor !== null
          ? {
              sources_status: successor.policy.sources_status,
              acceptance_status: successor.policy.acceptance_status,
              activation: successor.policy.activation,
            }
          : controls === null
            ? null
            : {
                sources_status: controls.policy.sources_status,
                acceptance_status: controls.policy.acceptance_status,
                activation: controls.policy.activation,
              },
      latest_review_context_status:
        controls === null || coverage === "pendiente"
          ? null
          : controls.review_context_metadata_status,
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
