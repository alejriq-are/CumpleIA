import { documentMatches } from "@/lib/licitud/eipd-document";
import { apiFetch, ApiError } from "./client";
export type Rank = 1 | 2 | 3 | 4 | null;
export type Rating = { probability: Rank; impact: Rank; rationale: string };
export type RiskRating = {
  risk_id: string;
  harm: string;
  frequency_context: string;
  inherent: Rating;
  projected: Rating;
  residual: Rating;
  action: string;
  owner_reference: string;
  review_on: string | null;
};
export type ControlRating = {
  measure_id: string;
  dimension: "probabilidad" | "impacto" | "ambos" | null;
  effectiveness: "no_evaluada" | "insuficiente" | "parcial" | "suficiente";
  status: "propuesta" | "en_implementacion" | "verificada";
  rationale: string;
  evidence_references: string[];
};
export type Analysis = {
  methodology: "CUMPLEIA-CUALITATIVA-1";
  horizon: string;
  risks: RiskRating[];
  controls: ControlRating[];
};
export type RiskEvaluation = {
  id: string;
  revision: number;
  current: boolean;
  analysis: Analysis;
  result: {
    risks: { risk_id: string; inherent: string; projected: string; residual: string }[];
    worst_residual: string;
    unresolved: boolean;
    can_confirm: false;
    activation: "deshabilitada";
  };
};
export type Annex = {
  id: string;
  reference: string;
  filename: string;
  description: string;
  section: string;
  version: number;
  size: number;
  sha256: string;
  mime: string;
  created_at: string;
  risk_ids: string[];
  measure_ids: string[];
};
export type Support = {
  schema_version: 1;
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  document_hash: string;
  risk_evaluation: RiskEvaluation | null;
  risk_history: { revision: number; created_at: string; document_hash: string }[];
  annexes: Annex[];
  can_confirm: false;
  activation: "deshabilitada";
};
export type SupportScope = {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  token: string;
};
const path = (s: SupportScope) =>
  `/licitud/treatments/${encodeURIComponent(s.treatmentId)}/assessments/${encodeURIComponent(s.assessmentId)}`;
function check(value: Support, scope: SupportScope): Support {
  if (
    !value ||
    value.schema_version !== 1 ||
    value.organization_id !== scope.organizationId ||
    value.treatment_id !== scope.treatmentId ||
    value.assessment_id !== scope.assessmentId ||
    !/^[a-f0-9]{64}$/.test(value.document_hash) ||
    !Array.isArray(value.annexes) ||
    !Array.isArray(value.risk_history) ||
    value.can_confirm !== false ||
    value.activation !== "deshabilitada" ||
    (value.risk_evaluation &&
      (value.risk_evaluation.analysis?.methodology !== "CUMPLEIA-CUALITATIVA-1" ||
        typeof value.risk_evaluation.current !== "boolean" ||
        value.risk_evaluation.result?.can_confirm !== false ||
        value.risk_evaluation.result?.activation !== "deshabilitada"))
  )
    throw new ApiError(502, "Soporte documental incompatible; guardado bloqueado.");
  return value;
}
export function annexFileError(file: File): string {
  if (!/\.(pdf|txt)$/i.test(file.name))
    return "Formato no admitido. Selecciona un archivo PDF o TXT UTF-8.";
  if (file.size === 0) return "El archivo está vacío. Selecciona un PDF o TXT UTF-8 con contenido.";
  if (file.size > 2097152)
    return "El archivo supera el tamaño máximo de 2 MiB. Selecciona un archivo más pequeño.";
  return "";
}
export const supportApi = {
  load: async (s: SupportScope) =>
    check(await apiFetch<Support>(path(s) + "/support", { ...s, cache: "no-store" }), s),
  risks: async (s: SupportScope, analysis: Analysis, snapshot: Support, requestId: string) => {
    const saved = check(
      await apiFetch<Support>(path(s) + "/risk-evaluations", {
        ...s,
        method: "POST",
        body: {
          data_kind: "ficticios",
          request_id: requestId,
          document_hash: snapshot.document_hash,
          expected_revision: snapshot.risk_evaluation?.revision ?? 0,
          analysis,
        },
      }),
      s
    );
    if (
      !saved.risk_evaluation?.current ||
      saved.document_hash !== snapshot.document_hash ||
      saved.risk_evaluation.revision !== (snapshot.risk_evaluation?.revision ?? 0) + 1 ||
      !documentMatches(saved.risk_evaluation.analysis, analysis)
    )
      throw new ApiError(502, "No se pudo comprobar la valoración guardada.");
    return saved;
  },
  annex: async (
    s: SupportScope,
    metadata: Record<string, unknown>,
    file: File,
    requestId: string
  ) => {
    const fileError = annexFileError(file);
    if (fileError) throw new ApiError(422, fileError);
    const encoded = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(",")[1]);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    return check(
      await apiFetch<Support>(path(s) + "/annexes", {
        ...s,
        method: "POST",
        body: {
          ...metadata,
          filename: file.name,
          data_kind: "ficticios",
          request_id: requestId,
          content_base64: encoded,
        },
      }),
      s
    );
  },
  download: async (s: SupportScope, annex: Annex) => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}${path(s)}/annexes/${encodeURIComponent(annex.id)}/content`,
      {
        headers: { Authorization: `Bearer ${s.token}`, "X-Organization-Id": s.organizationId },
        cache: "no-store",
      }
    );
    if (!response.ok) throw new ApiError(response.status, "No se pudo descargar el anexo.");
    const bytes = await response.arrayBuffer();
    const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)))
      .map((v) => v.toString(16).padStart(2, "0"))
      .join("");
    if (bytes.byteLength !== annex.size || hash !== annex.sha256)
      throw new ApiError(502, "No se pudo comprobar la integridad del anexo.");
    const url = URL.createObjectURL(new Blob([bytes], { type: "application/octet-stream" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = annex.filename;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  },
};
export const levelLabels: Record<string, string> = {
  bajo: "Bajo",
  medio: "Medio",
  alto: "Alto",
  muy_alto: "Muy alto",
  sin_resolver: "Sin resolver",
};
export const matrix = [
  ["bajo", "bajo", "medio", "alto"],
  ["bajo", "medio", "alto", "alto"],
  ["medio", "alto", "alto", "muy_alto"],
  ["alto", "alto", "muy_alto", "muy_alto"],
];
export function ratingLevel(value: Rating) {
  return value.probability && value.impact
    ? matrix[value.probability - 1][value.impact - 1]
    : "sin_resolver";
}
export const blankRating = (): Rating => ({ probability: null, impact: null, rationale: "" });
export const blankRisk = (id: string): RiskRating => ({
  risk_id: id,
  harm: "",
  frequency_context: "",
  inherent: blankRating(),
  projected: blankRating(),
  residual: blankRating(),
  action: "",
  owner_reference: "",
  review_on: null,
});
export const blankControl = (id: string): ControlRating => ({
  measure_id: id,
  dimension: null,
  effectiveness: "no_evaluada",
  status: "propuesta",
  rationale: "",
  evidence_references: [],
});
