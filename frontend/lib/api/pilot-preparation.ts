import { apiFetch, ApiError } from "./client";
import type { ChildScope } from "./child-adolescent";
import type { Dossier } from "./mvp-dossier";
import type { AuthorityState } from "./organization-acceptance";
export const pilotReferences = {
  review_reference: "Referencia de revisión jurídica ficticia",
  environment_reference: "Referencia de entorno",
  access_reference: "Referencia de control de accesos",
  restore_reference: "Referencia de restauración",
  retention_reference: "Referencia de retención",
  support_reference: "Referencia de soporte",
  incident_reference: "Referencia de incidentes",
};
export const SIMULATION_WATERMARK = "ACTA DE PRUEBA, DATOS FICTICIOS, SIN VALOR JURÍDICO";
export const pilotScenario = {
  company: {
    name: "[FICTICIA] Comercial Piloto Andes SpA",
    test_rut: "00.000.000-0",
    activity:
      "Comercio minorista en línea; clientes, trabajadores y programa de fidelización con menores (escenario de prueba).",
    address: "Calle Ficticia 123, Santiago",
    contact: "contacto@piloto.example.invalid",
  },
  person: {
    name: "[FICTICIA] Persona Facultada Piloto",
    test_rut: "00.000.001-0",
    position: "Gerencia General (representante legal simulado)",
    contact: "facultada@piloto.example.invalid",
  },
  designation: {
    type: "designación simulada para pruebas",
    test_date: "2000-01-01",
    date_status: "simulada",
    real_legal_document: null,
  },
} as const;
export type PilotForm = {
  act_reference?: string;
  designation_reference?: string;
  review_decision: "acepta" | "rechaza" | "requiere_cambios" | "pendiente";
} & Record<keyof typeof pilotReferences, string | null>;
export type PilotResult = {
  schema_version: 2;
  watermark: typeof SIMULATION_WATERMARK;
  scenario: typeof pilotScenario;
  act_reference: string;
  designation_reference: string;
  scenario_notice: string;
  legal_review_status: "pendiente_no_realizada" | "simulada_sin_valor_juridico";
  data_kind: "ficticios";
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  actor_id: string;
  authority_id: string;
  authority_evidence_reference: string;
  document_hashes: Record<string, string | null>;
  declared_references: Record<string, string | null>;
  review_decision: string;
  missing: string[];
  preparation_complete: boolean;
  evidence_status: "declarada_no_verificada";
  persistence: "simulacion_no_registrada";
  legal_acceptance: "pendiente_organizacion_piloto";
  mvp_ready: false;
  allows_real_data: false;
  can_confirm: false;
  authorizes_action: false;
  activation: "deshabilitada";
};
function valid(v: unknown): asserts v {
  if (!v) throw new ApiError(502, "Preparación incompatible; no hay aprobación real");
}
const uuid = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
export async function preparePilot(
  s: ChildScope,
  packet: Dossier,
  form: PilotForm
): Promise<PilotResult> {
  if (
    ![s.organizationId, s.treatmentId, s.assessmentId].every((x) => uuid.test(x)) ||
    packet.organization_id !== s.organizationId ||
    packet.treatment_id !== s.treatmentId ||
    packet.assessment_id !== s.assessmentId
  )
    throw new ApiError(400, "Expediente no válido");
  const prefix = `/licitud/treatments/${s.treatmentId}/assessments/${s.assessmentId}`;
  const state = await apiFetch<AuthorityState>(prefix + "/organization-acceptance/v1/authority", {
    ...s,
    cache: "no-store",
  });
  valid(
    state &&
      uuid.test(state.actor_id) &&
      state.can_confirm === false &&
      state.authorizes_action === false &&
      Array.isArray(state.authorities)
  );
  state.authorities.forEach((g) =>
    valid(
      g.organization_id === s.organizationId &&
        g.treatment_id === s.treatmentId &&
        g.assessment_id === s.assessmentId &&
        uuid.test(g.id) &&
        uuid.test(g.actor_id) &&
        Number.isSafeInteger(g.revision) &&
        g.revision > 0 &&
        ["otorgar", "revocar"].includes(g.action) &&
        g.can_confirm === false &&
        g.authorizes_action === false &&
        g.data_kind === "ficticios"
    )
  );
  const grant = state.authorities
    .filter((g) => g.actor_id === state.actor_id)
    .sort((a, b) => b.revision - a.revision)[0];
  if (!grant || grant.action !== "otorgar")
    throw new ApiError(403, "Registra primero una facultad ficticia vigente para tu usuario");
  const hashes = Object.fromEntries(packet.documents.map((d) => [d.kind, d.content_hash]));
  const refs = Object.fromEntries(
    Object.keys(pilotReferences).map((k) => [
      k,
      form[k as keyof typeof pilotReferences]?.trim() || null,
    ])
  );
  const actReference = form.act_reference?.trim() || "SIMULADA-PILOTO-ACTA-001";
  const designationReference = form.designation_reference?.trim() || "SIMULADA-PILOTO-DES-001";
  const simulationReference = /^SIMULADA-[A-Z0-9][A-Z0-9-]*$/;
  if (
    ![
      actReference,
      designationReference,
      ...Object.values(refs).filter((v): v is string => v !== null),
    ].every((v) => simulationReference.test(v) && v.length <= 128)
  )
    throw new ApiError(
      400,
      "Usa referencias con prefijo SIMULADA- y letras mayúsculas, números o guiones"
    );
  const v = await apiFetch<PilotResult>(prefix + "/pilot-preparation/v2", {
    ...s,
    method: "POST",
    body: {
      data_kind: "ficticios",
      act_reference: actReference,
      designation_reference: designationReference,
      authority_id: grant.id,
      document_hashes: hashes,
      review_decision: form.review_decision,
      ...refs,
    },
  });
  valid(
    v &&
      v.schema_version === 2 &&
      v.data_kind === "ficticios" &&
      v.organization_id === s.organizationId &&
      v.treatment_id === s.treatmentId &&
      v.assessment_id === s.assessmentId &&
      v.actor_id === state.actor_id &&
      v.authority_id === grant.id &&
      v.can_confirm === false &&
      v.authorizes_action === false &&
      v.mvp_ready === false &&
      v.allows_real_data === false &&
      v.activation === "deshabilitada" &&
      v.evidence_status === "declarada_no_verificada" &&
      v.persistence === "simulacion_no_registrada" &&
      v.legal_acceptance === "pendiente_organizacion_piloto" &&
      v.review_decision === form.review_decision &&
      typeof v.preparation_complete === "boolean" &&
      Array.isArray(v.missing) &&
      v.missing.every((x) => typeof x === "string") &&
      v.preparation_complete === (v.missing.length === 0)
  );
  valid(
    v.watermark === SIMULATION_WATERMARK &&
      v.act_reference === actReference &&
      v.designation_reference === designationReference &&
      simulationReference.test(v.authority_evidence_reference) &&
      v.scenario_notice ===
        "Escenario ficticio; no identifica ni acredita a la organización o persona real de la sesión." &&
      v.legal_review_status ===
        (form.review_decision === "pendiente"
          ? "pendiente_no_realizada"
          : "simulada_sin_valor_juridico")
  );
  valid(
    v.scenario &&
      Object.keys(v.scenario).sort().join(",") === Object.keys(pilotScenario).sort().join(",")
  );
  for (const section of Object.keys(pilotScenario) as (keyof typeof pilotScenario)[]) {
    valid(
      v.scenario[section] &&
        Object.keys(v.scenario[section]).sort().join(",") ===
          Object.keys(pilotScenario[section]).sort().join(",")
    );
    for (const [key, value] of Object.entries(pilotScenario[section]))
      valid((v.scenario?.[section] as Record<string, unknown>)?.[key] === value);
  }
  const expectedMissing = [
    ...Object.keys(refs).filter((k) => !refs[k]),
    ...Object.keys(hashes).filter((k) => hashes[k] === null),
    ...(form.review_decision === "acepta" ? [] : ["revision_juridica_ficticia_no_aceptada"]),
  ];
  valid(JSON.stringify(v.missing) === JSON.stringify(expectedMissing));
  for (const k of Object.keys(hashes)) valid(v.document_hashes?.[k] === hashes[k]);
  for (const k of Object.keys(refs)) valid(v.declared_references?.[k] === refs[k]);
  return v;
}
