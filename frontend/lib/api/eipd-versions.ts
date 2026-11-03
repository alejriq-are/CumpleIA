import { apiFetch, ApiError } from "./client";
import { editableEipd, type EipdValue } from "./eipd-draft";
import type { Scope } from "./licitud";

export type VersionScope = Scope & { assessmentId: string };
export type VersionMaterial = {
  schema_version: 1;
  document_type: "eipd_general";
  saved_assessment: Record<string, unknown> & { eipd_resolution_assessment: EipdValue };
  applicability: Record<string, unknown>;
  support_records: Record<string, unknown>[];
  policy: Record<string, unknown>;
  diagnostic: Record<string, unknown>;
};
export type VersionPreview = {
  source_hash: string;
  latest_version: number;
  bundle: VersionMaterial;
  can_confirm: false;
  activation: "deshabilitada";
};
export type VersionRequest = {
  request_id: string;
  data_kind: "ficticios";
  expected_source_hash: string;
  expected_latest_version: number;
  reason: string;
};
export type VersionMetadata = {
  id: string;
  version: number;
  created_at: string;
  reason: string;
  bundle_hash: string;
};
export type RegisteredVersion = VersionMetadata & {
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  created_by: string;
  request_id: string;
  source_hash: string;
  bundle: VersionMaterial & {
    version: number;
    predecessor_id: string | null;
    reason: string;
    registered_by: string;
  };
  can_confirm: false;
  activation: "deshabilitada";
};
const record = (v: unknown): v is Record<string, unknown> =>
  !!v && typeof v === "object" && !Array.isArray(v);
const uuid = (v: unknown): v is string =>
  typeof v === "string" && /^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(v);
const hash = (v: unknown): v is string => typeof v === "string" && /^[0-9a-f]{64}$/.test(v);
const integer = (v: unknown): v is number => Number.isSafeInteger(v) && Number(v) >= 0;
const incompatible = (): never => {
  throw new ApiError(502, "Respuesta de versiones EIPD incompatible. No se confirma el registro.");
};
function material(v: unknown, s: VersionScope): v is VersionMaterial & Record<string, unknown> {
  if (!record(v) || !record(v.saved_assessment)) return false;
  const a = v.saved_assessment;
  if (
    v.schema_version !== 1 ||
    v.document_type !== "eipd_general" ||
    a.id !== s.assessmentId ||
    a.organization_id !== s.organizationId ||
    a.treatment_id !== s.treatmentId ||
    !record(a.eipd_resolution_assessment) ||
    !record(v.applicability) ||
    !Array.isArray(v.support_records) ||
    !v.support_records.every(record) ||
    !record(v.policy) ||
    !record(v.diagnostic)
  )
    return false;
  editableEipd(a.eipd_resolution_assessment);
  return true;
}
function metadata(v: unknown): v is VersionMetadata & Record<string, unknown> {
  return (
    record(v) &&
    uuid(v.id) &&
    integer(v.version) &&
    v.version > 0 &&
    typeof v.created_at === "string" &&
    Number.isFinite(Date.parse(v.created_at)) &&
    typeof v.reason === "string" &&
    hash(v.bundle_hash)
  );
}
function registered(v: unknown, s: VersionScope): RegisteredVersion {
  if (
    !metadata(v) ||
    !record(v) ||
    v.organization_id !== s.organizationId ||
    v.treatment_id !== s.treatmentId ||
    v.assessment_id !== s.assessmentId ||
    !uuid(v.created_by) ||
    !uuid(v.request_id) ||
    !hash(v.source_hash) ||
    !material(v.bundle, s) ||
    v.can_confirm !== false ||
    v.activation !== "deshabilitada" ||
    v.bundle.version !== v.version ||
    v.bundle.reason !== v.reason ||
    v.bundle.registered_by !== v.created_by ||
    !(v.bundle.predecessor_id === null || uuid(v.bundle.predecessor_id))
  )
    return incompatible();
  return v as RegisteredVersion;
}
const path = (s: VersionScope) =>
  `/licitud/treatments/${encodeURIComponent(s.treatmentId)}/assessments/${encodeURIComponent(s.assessmentId)}/eipd-versions/v1`;
export const eipdVersionsApi = {
  preview: async (s: VersionScope): Promise<VersionPreview> => {
    const v = await apiFetch<VersionPreview>(path(s) + "/preview", { ...s, cache: "no-store" });
    if (
      !record(v) ||
      !hash(v.source_hash) ||
      !integer(v.latest_version) ||
      !material(v.bundle, s) ||
      v.can_confirm !== false ||
      v.activation !== "deshabilitada"
    )
      return incompatible();
    return v;
  },
  history: async (s: VersionScope): Promise<VersionMetadata[]> => {
    const v = await apiFetch<VersionMetadata[]>(path(s), { ...s, cache: "no-store" });
    if (
      !Array.isArray(v) ||
      !v.every(metadata) ||
      new Set(v.map((r) => r.id)).size !== v.length ||
      new Set(v.map((r) => r.version)).size !== v.length
    )
      return incompatible();
    return v;
  },
  detail: async (s: VersionScope, id: string) => {
    const v = registered(
      await apiFetch<unknown>(path(s) + "/" + encodeURIComponent(id), { ...s, cache: "no-store" }),
      s
    );
    if (v.id !== id) return incompatible();
    return v;
  },
  register: async (s: VersionScope, body: VersionRequest) => {
    const v = registered(
      await apiFetch<unknown>(path(s), { ...s, method: "POST", body, cache: "no-store" }),
      s
    );
    if (
      v.request_id !== body.request_id ||
      v.source_hash !== body.expected_source_hash ||
      v.reason !== body.reason ||
      v.version !== body.expected_latest_version + 1
    )
      return incompatible();
    return v;
  },
  lookup: async (s: VersionScope, requestId: string) => {
    const v = registered(
      await apiFetch<unknown>(path(s) + "/requests/" + encodeURIComponent(requestId), {
        ...s,
        cache: "no-store",
      }),
      s
    );
    if (v.request_id !== requestId) return incompatible();
    return v;
  },
};
