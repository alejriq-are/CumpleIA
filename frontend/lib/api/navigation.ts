import { apiFetch, ApiError } from "./client";
import type { Scope } from "./licitud";
export type Determination = {
  state: "pendiente" | "corresponde" | "no_corresponde" | "informacion_insuficiente";
  reason: string;
};
export type Applicability = {
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  context_hash: string;
  revision: number;
  current: boolean;
  editable: boolean;
  eipd: Determination;
  infancia: Determination;
  history: {
    revision: number;
    created_by: string;
    created_at: string;
    eipd: Determination;
    infancia: Determination;
  }[];
  can_confirm: false;
  activation: "deshabilitada";
};
const path = (s: Scope, id: string) =>
  `/licitud/treatments/${encodeURIComponent(s.treatmentId)}/assessments/${encodeURIComponent(id)}/applicability`;
function validate(value: Applicability, s: Scope, id: string): Applicability {
  const states = ["pendiente", "corresponde", "no_corresponde", "informacion_insuficiente"];
  if (
    !value ||
    value.organization_id !== s.organizationId ||
    value.treatment_id !== s.treatmentId ||
    value.assessment_id !== id ||
    !Number.isInteger(value.revision) ||
    value.revision < 0 ||
    !/^[0-9a-f]{64}$/.test(value.context_hash) ||
    typeof value.current !== "boolean" ||
    typeof value.editable !== "boolean" ||
    !Array.isArray(value.history) ||
    value.can_confirm !== false ||
    value.activation !== "deshabilitada" ||
    [value.eipd, value.infancia].some(
      (v) => !v || !states.includes(v.state) || typeof v.reason !== "string"
    )
  )
    throw new ApiError(
      502,
      "La respuesta no corresponde al contexto solicitado. No se habilitaron formularios."
    );
  return value;
}
export const navigationApi = {
  get: async (s: Scope, id: string) =>
    validate(await apiFetch<Applicability>(path(s, id), { ...s, cache: "no-store" }), s, id),
  save: async (
    s: Scope,
    id: string,
    body: {
      data_kind: "ficticios";
      request_id: string;
      expected_revision: number;
      context_hash: string;
      eipd: Determination;
      infancia: Determination;
    }
  ) =>
    validate(
      await apiFetch<Applicability>(path(s, id), { ...s, method: "POST", body, cache: "no-store" }),
      s,
      id
    ),
};
