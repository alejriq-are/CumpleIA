import { apiFetch } from "./client";
export const legalBases = [
  ["consentimiento_art12", "Consentimiento"],
  ["obligaciones_economicas_art13a", "Obligaciones económicas"],
  ["obligacion_legal_art13b", "Obligación legal"],
  ["contrato_precontractual_art13c", "Contrato o medidas precontractuales"],
  ["interes_legitimo_art13d", "Interés legítimo (LIA)"],
  ["defensa_derechos_art13e", "Defensa de derechos"],
] as const;
export type AssessmentSummary = {
  id: string;
  organization_id: string;
  treatment_id: string;
  version: number;
  status: "borrador" | "confirmado" | "reemplazado";
  purpose_snapshot: string;
  legal_basis: string | null;
};
export type Assessment = AssessmentSummary & {
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
