import { apiFetch } from "./client";
export const legalBases = [
  ["consentimiento_art12", "Consentimiento"],
  ["obligaciones_economicas_art13a", "Obligaciones económicas"],
  ["obligacion_legal_art13b", "Obligación legal"],
  ["contrato_precontractual_art13c", "Contrato o medidas precontractuales"],
  ["interes_legitimo_art13d", "Interés legítimo (LIA)"],
  ["defensa_derechos_art13e", "Defensa de derechos"],
] as const;
export const legalBasisHelp: Record<string, string> = {
  "": "Pendiente de definir: conserva esta opción si todavía no has identificado una base propuesta. Puedes guardar el borrador sin presentar una conclusión jurídica.",
  consentimiento_art12:
    "Consentimiento: documenta por qué propones esta base y cómo se obtendría y acreditaría para la finalidad. Elegirla no prueba que exista un consentimiento válido.",
  obligaciones_economicas_art13a:
    "Obligaciones económicas: explica la obligación y su relación con la finalidad y los datos incluidos. La selección requiere revisar el supuesto concreto y su fundamento.",
  obligacion_legal_art13b:
    "Obligación legal: identifica la norma y la obligación concreta que sustentarían el tratamiento. No basta señalar que la actividad está regulada.",
  contrato_precontractual_art13c:
    "Contrato o medidas precontractuales: explica el vínculo contractual y por qué los datos serían necesarios para esta finalidad. La selección no valida esa necesidad.",
  interes_legitimo_art13d:
    "Interés legítimo: completa los análisis de interés, necesidad, impactos y salvaguardas en la LIA. Guardar el balance no equivale a aprobarlo.",
  defensa_derechos_art13e:
    "Defensa de derechos: describe el derecho y la actuación que motivan la propuesta, su alcance y los datos necesarios. Requiere revisión del caso concreto.",
};
export type AssessmentSummary = {
  series_id?: string;
  id: string;
  organization_id: string;
  treatment_id: string;
  version: number;
  status: "borrador" | "confirmado" | "reemplazado";
  purpose_snapshot: string;
  legal_basis: string | null;
};
export type Assessment = AssessmentSummary & {
  rat_context_hash?: string;
  rat_context_snapshot?: {
    data_categories?: { category_code: string; category_name: string }[];
    data_subjects?: { category_code: string; category_name: string }[];
    special_regimes?: { includes_children?: boolean; includes_adolescents?: boolean };
    data_sources?: { source_type?: string; description?: string | null }[];
  };
  child_adolescent_assessment?: unknown;
  eipd_resolution_assessment?: Record<string, unknown> | null;
  justification: string | null;
  lia_assessment: Record<string, unknown> | null;
};
export type Draft = {
  purpose_id: string;
  scope: { data_category_codes: string[]; data_subject_codes: string[] };
  legal_basis: string | null;
  justification: string | null;
};
export type Scope = { token: string; organizationId: string; treatmentId: string };
const root = (scope: Scope) =>
  `/licitud/treatments/${encodeURIComponent(scope.treatmentId)}/assessments`;
export const licitudApi = {
  list: (scope: Scope, offset = 0) =>
    apiFetch<AssessmentSummary[]>(`${root(scope)}?offset=${offset}&limit=50`, scope),
  create: (scope: Scope, body: Draft) =>
    apiFetch<Assessment>(root(scope), { ...scope, method: "POST", body }),
  get: (scope: Scope, id: string) =>
    apiFetch<Assessment>(`${root(scope)}/${encodeURIComponent(id)}`, scope),
  save: (
    scope: Scope,
    id: string,
    body: Pick<Assessment, "legal_basis" | "justification"> & {
      lia_assessment?: Record<string, unknown>;
    }
  ) =>
    apiFetch<Assessment>(`${root(scope)}/${encodeURIComponent(id)}`, {
      ...scope,
      method: "PATCH",
      body,
    }),
};

export type AssessmentScope = Draft["scope"];
export type ScopeReview = {
  review_hash: string;
  changed: boolean;
  editable: boolean;
  before: NonNullable<Assessment["rat_context_snapshot"]>;
  after: NonNullable<Assessment["rat_context_snapshot"]>;
  history: {
    revision: number;
    created_by: string;
    created_at: string;
    reason: string;
    before: Record<string, unknown>;
    after: Record<string, unknown>;
  }[];
};
export const scopeReviewApi = {
  preview: (scope: Scope, id: string, selection: AssessmentScope) =>
    apiFetch<ScopeReview>(`${root(scope)}/${encodeURIComponent(id)}/scope-review/preview`, {
      ...scope,
      method: "POST",
      body: { scope: selection },
    }),
  apply: (
    scope: Scope,
    id: string,
    body: {
      scope: AssessmentScope;
      review_hash: string;
      request_id: string;
      data_kind: "ficticios";
      reason: string;
    }
  ) =>
    apiFetch<Assessment>(`${root(scope)}/${encodeURIComponent(id)}/scope-review`, {
      ...scope,
      method: "POST",
      body,
    }),
};
