import type { ModuleId } from "./prototype-data";
import type { WorkContext } from "./ConnectedContext";
export type WorkLocation = WorkContext & { module: ModuleId; section: string; step: number };
const modules = ["panel", "diagnostico", "rat", "licitud", "organizacion"];
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export function encodeWork(v: WorkLocation) {
  const q = new URLSearchParams({ organizationId: v.organizationId });
  if (v.treatmentId) q.set("treatmentId", v.treatmentId);
  if (v.assessmentId) q.set("assessmentId", v.assessmentId);
  if (v.step) q.set("step", String(v.step));
  return `#/${v.module}/${encodeURIComponent(v.section)}?${q}`;
}
export function parseWork(hash: string): WorkLocation | null {
  try {
    const [path, query] = hash.replace(/^#/, "").split("?");
    const [, module, section, ...rest] = path.split("/");
    if (rest.length || !modules.includes(module) || !section || !/^[-a-zA-Z0-9_]+$/.test(section))
      return null;
    const allowed: Record<string, string[]> = {
      panel: ["resumen"],
      rat: [
        "catalogo",
        "nuevo",
        "resumen",
        "general",
        "finalidades",
        "categorias",
        "titulares",
        "fuentes",
        "sistemas",
        "proveedores",
        "transferencias",
        "revision",
      ],
      licitud: [
        "catalogo",
        "resumen",
        "aplicabilidad",
        "alcance",
        "base",
        "anexos",
        "eipd",
        "infancia",
        "preparar",
        "revisar",
        "historial",
      ],
      organizacion: ["resumen"],
    };
    if (allowed[module] && !allowed[module].includes(section)) return null;
    const q = new URLSearchParams(query);
    const organizationId = q.get("organizationId") ?? "",
      treatmentId = q.get("treatmentId") ?? "",
      assessmentId = q.get("assessmentId") ?? "";
    if (
      !uuid.test(organizationId) ||
      (treatmentId && !uuid.test(treatmentId)) ||
      (assessmentId && (!treatmentId || !uuid.test(assessmentId)))
    )
      return null;
    const step = Number(q.get("step") ?? 0);
    if (!Number.isInteger(step) || step < 0 || step > 6) return null;
    return { module: module as ModuleId, section, organizationId, treatmentId, assessmentId, step };
  } catch {
    return null;
  }
}
export function paneKey(v: WorkLocation) {
  return `${v.module}:${v.organizationId}:${v.module === "rat" ? (v.section === "nuevo" ? "nuevo" : v.treatmentId) : v.module === "licitud" ? `${v.treatmentId}:${v.assessmentId}` : ""}`;
}
export const ratSections = [
  ["general", "Información general"],
  ["finalidades", "Finalidades"],
  ["categorias", "Categorías de datos"],
  ["titulares", "Titulares"],
  ["fuentes", "Fuentes"],
  ["sistemas", "Sistemas"],
  ["proveedores", "Proveedores"],
  ["transferencias", "Transferencias internacionales"],
  ["revision", "Revisión del tratamiento"],
];
export const eipdSections = [
  "Tratamiento y alcance de la EIPD",
  "Necesidad y proporcionalidad",
  "Riesgos",
  "Valorar riesgos",
  "Medidas de mitigación",
  "Fuentes y evidencias",
  "Riesgo residual y seguimiento",
];
