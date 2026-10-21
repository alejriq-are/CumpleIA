import { apiFetch, ApiError } from "./client";
import {
  documentFields,
  documentMatches,
  validDocument,
  compactDocument,
} from "@/lib/licitud/eipd-document";
import type { Assessment, Scope } from "./licitud";
export type EipdValue = Record<string, unknown>;
export type EipdDraftRow = Assessment & { eipd_resolution_assessment: EipdValue | null };
export type EipdDiagnostic = {
  assessment_id: string;
  rat_context_current: boolean;
  eipd_resolution: {
    result: string;
    issues: { field: string; code: string; category: string }[];
  } | null;
};
const editable = new Set([
  "schema_version",
  "document_reference",
  "document_version",
  "notes",
  ...Object.keys(documentFields),
]);
export function editableEipd(value: EipdValue | null): EipdValue {
  if (!value) return { schema_version: 1 };
  if (Object.keys(value).some((key) => !editable.has(key) && key !== "context_binding"))
    throw new ApiError(502, "Documento EIPD incompatible. No se reemplaza su contenido.");
  const result = Object.fromEntries(Object.entries(value).filter(([key]) => editable.has(key)));
  if (!validDocument(result))
    throw new ApiError(502, "Documento EIPD incompatible. No se habilita el guardado.");
  return structuredClone(result);
}
const path = (scope: Scope, id: string) =>
  `/licitud/treatments/${encodeURIComponent(scope.treatmentId)}/assessments/${encodeURIComponent(id)}`;
export const eipdDraftApi = {
  load: (scope: Scope, id: string) =>
    apiFetch<EipdDraftRow>(path(scope, id), { ...scope, cache: "no-store" }),
  diagnostic: async (scope: Scope, id: string) => {
    const value = await apiFetch<EipdDiagnostic>(path(scope, id) + "/readiness", {
      ...scope,
      cache: "no-store",
    });
    if (
      value.assessment_id !== id ||
      typeof value.rat_context_current !== "boolean" ||
      !(
        value.eipd_resolution === null ||
        (value.eipd_resolution &&
          ["completo", "incompleto", "requiere_revision"].includes(value.eipd_resolution.result) &&
          Array.isArray(value.eipd_resolution.issues) &&
          value.eipd_resolution.issues.every(
            (issue) =>
              issue &&
              typeof issue.field === "string" &&
              typeof issue.code === "string" &&
              typeof issue.category === "string"
          ))
      )
    )
      throw new ApiError(502, "Diagnóstico EIPD incompatible. No acredita preparación.");
    return value;
  },
  save: async (scope: Scope, id: string, document: EipdValue) => {
    document = compactDocument(document);
    if (!validDocument(document))
      throw new ApiError(400, "Revisa los campos, fechas y referencias del documento EIPD.");
    const value = await apiFetch<EipdDraftRow>(path(scope, id), {
      ...scope,
      cache: "no-store",
      method: "PATCH",
      body: { eipd_resolution_assessment: document },
    });
    if (
      value.id !== id ||
      value.organization_id !== scope.organizationId ||
      value.treatment_id !== scope.treatmentId ||
      !value.eipd_resolution_assessment ||
      !documentMatches(editableEipd(value.eipd_resolution_assessment), document)
    )
      throw new ApiError(
        502,
        "No se pudo comprobar el contenido EIPD guardado. Consulta antes de volver a intentar."
      );
    return value;
  },
};
