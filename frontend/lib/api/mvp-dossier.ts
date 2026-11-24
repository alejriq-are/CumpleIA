import type { Support } from "./assessment-support";
import { apiFetch, ApiError } from "./client";
import type { ChildScope } from "./child-adolescent";
export type Dossier = {
  schema_version: 1;
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  assessment_version: number;
  generated_at: string;
  data_provenance: "no_verificada";
  scope: "expediente_documental_rat_licitud_lia_eipd";
  rat_snapshot_note: string;
  support?: Support | null;
  documents: {
    kind: "rat" | "licitud_lia" | "eipd";
    status: "disponible" | "sin_documento";
    version: number | null;
    coverage: string;
    content: Record<string, unknown> | null;
    content_hash: string | null;
    organization_acceptance: "sin_flujo" | "consultar_eventos" | "sin_eventos";
    acceptance_events: Record<string, unknown>[];
  }[];
  official_sources: {
    reference: string;
    title: string;
    url: string;
    consulted_on: string;
    status: "consultada_sin_aceptacion_juridica";
    scope_note: string;
    artifact_reference?: string | null;
    artifact_sha256?: string | null;
    legal_verifier: null;
  }[];
  release_gates: {
    id: string;
    title: string;
    status: "alcance_definido" | "pendiente" | "bloqueado";
    evidence_needed: string;
  }[];
  packet_hash: string;
  hash_algorithm: "sha256_json_sort_keys_utf8";
  legal_acceptance: "pendiente_organizacion_piloto";
  mvp_ready: false;
  allows_real_data: false;
  authorizes_action: false;
  can_confirm: false;
  activation: "deshabilitada";
};
const hash = /^[0-9a-f]{64}$/;
const uuid = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
function requireValid(value: unknown): asserts value {
  if (!value) throw new ApiError(502, "Expediente incompatible; descarga bloqueada");
}
export async function loadMvpDossier(s: ChildScope): Promise<Dossier> {
  if (![s.organizationId, s.treatmentId, s.assessmentId].every((x) => uuid.test(x)))
    throw new ApiError(400, "Expediente no válido");
  const v = await apiFetch<Dossier>(
    `/licitud/treatments/${s.treatmentId}/assessments/${s.assessmentId}/mvp-dossier/v1`,
    { ...s, cache: "no-store" }
  );
  requireValid(
    v &&
      v.schema_version === 1 &&
      v.organization_id === s.organizationId &&
      v.treatment_id === s.treatmentId &&
      v.assessment_id === s.assessmentId &&
      v.mvp_ready === false &&
      v.allows_real_data === false &&
      v.can_confirm === false &&
      v.authorizes_action === false &&
      v.activation === "deshabilitada" &&
      v.data_provenance === "no_verificada" &&
      v.legal_acceptance === "pendiente_organizacion_piloto" &&
      v.scope === "expediente_documental_rat_licitud_lia_eipd" &&
      v.hash_algorithm === "sha256_json_sort_keys_utf8" &&
      hash.test(v.packet_hash) &&
      Number.isInteger(v.assessment_version) &&
      v.assessment_version > 0 &&
      Number.isFinite(Date.parse(v.generated_at)) &&
      typeof v.rat_snapshot_note === "string"
  );
  requireValid(
    Array.isArray(v.documents) &&
      v.documents.length === 3 &&
      v.documents.map((d) => d.kind).join(",") === "rat,licitud_lia,eipd"
  );
  for (const d of v.documents) {
    requireValid(
      typeof d.coverage === "string" &&
        ["disponible", "sin_documento"].includes(d.status) &&
        Array.isArray(d.acceptance_events)
    );
    requireValid(
      d.status === "sin_documento"
        ? d.content === null && d.content_hash === null
        : d.content !== null &&
            typeof d.content === "object" &&
            !Array.isArray(d.content) &&
            typeof d.content_hash === "string" &&
            hash.test(d.content_hash)
    );
    requireValid(
      d.kind === "eipd"
        ? ["sin_eventos", "consultar_eventos"].includes(d.organization_acceptance)
        : d.organization_acceptance === "sin_flujo" && d.acceptance_events.length === 0
    );
    for (const e of d.acceptance_events)
      requireValid(
        e.organization_id === s.organizationId &&
          e.treatment_id === s.treatmentId &&
          e.assessment_id === s.assessmentId &&
          e.can_confirm === false &&
          e.authorizes_action === false &&
          e.data_kind === "ficticios" &&
          ["acepta", "rechaza", "requiere_cambios"].includes(String(e.decision)) &&
          e.resolution_id === d.content?.id &&
          ["document_hash", "context_hash", "child_material_hash"].every(
            (k) => e[k] === d.content?.[k]
          )
      );
  }
  requireValid(
    Array.isArray(v.release_gates) &&
      v.release_gates.map((g) => g.id).join(",") === "G1,G2,G3,G4,G5,G6,G7"
  );
  v.release_gates.forEach((g, i) =>
    requireValid(
      g.status === (i === 0 ? "alcance_definido" : i >= 5 ? "bloqueado" : "pendiente") &&
        typeof g.title === "string" &&
        typeof g.evidence_needed === "string"
    )
  );
  requireValid(Array.isArray(v.official_sources) && v.official_sources.length === 3);
  const official = [
    "https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf",
    "https://www.bcn.cl/leychile/navegar?i=1209272",
    "https://www.leychile.cl/navegar?idNorma=1227971",
  ];
  v.official_sources.forEach((source, i) =>
    requireValid(
      source.url === official[i] &&
        source.status === "consultada_sin_aceptacion_juridica" &&
        source.legal_verifier === null &&
        typeof source.title === "string" &&
        typeof source.scope_note === "string"
    )
  );
  return v;
}
