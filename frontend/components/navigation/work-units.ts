import type { WorkLocation } from "./connected-navigation";
import type { WorkState } from "./work-unit-state";
export type WorkUnit = {
  id: string;
  label: string;
  location: WorkLocation;
  destination?: WorkLocation;
  origin: "form" | "temporary";
  state: WorkState;
};
export const workStatusLabels: Record<WorkState["status"], string> = {
  not_loaded: "Sin consultar",
  loading: "Consultando",
  ready: "Consultado sin cambios",
  edited: "Cambios sin guardar",
  saving: "Guardando",
  saved: "Guardado confirmado",
  error: "Error; revisa el formulario",
};
export const assessmentUnits: Record<
  string,
  { label: string; section: string; step?: number; temporary?: boolean }
> = {
  alcance: { label: "Revisión de alcance RAT asociado", section: "alcance", temporary: true },
  aplicabilidad: { label: "Determinación de aplicabilidad", section: "aplicabilidad" },
  base: { label: "Base de licitud y fundamento", section: "base" },
  eipd: { label: "Borrador EIPD · siete pasos", section: "eipd" },
  infancia: { label: "Antecedentes de infancia y adolescencia", section: "infancia" },
  preparar: {
    label: "Preparación de nueva versión de infancia",
    section: "preparar",
    temporary: true,
  },
  valoracion: { label: "Valoración de riesgos", section: "eipd", step: 3 },
  anexos: { label: "Anexo de respaldo en preparación", section: "anexos" },
};
