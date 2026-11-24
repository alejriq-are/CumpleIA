import type { Values, Scenario } from "./prototype-data";
export type DocumentScope = { eipd: boolean; infancia: boolean };
export const pendingScope: DocumentScope = { eipd: false, infancia: false };
export const eipdSections = ["eipd", "proporcionalidad", "riesgos", "medidas", "eipd_fuentes"];
export function scopeFrom(values: Values): DocumentScope {
  return {
    eipd: values["aplicabilidad.eipd"] === "Corresponde",
    infancia: values["aplicabilidad.infancia"] === "Corresponde",
  };
}
export function applicabilityError(values: Values, scenario: Scenario): string {
  for (const key of ["eipd", "infancia"]) {
    const state = values[`aplicabilidad.${key}`];
    if (state !== "Pendiente de analizar" && !values[`aplicabilidad.${key}_fundamento`]?.trim())
      return "Explica el fundamento de cada determinación que no esté pendiente.";
  }
  if (scenario === "infancia" && values["aplicabilidad.infancia"] === "No corresponde")
    return "El alcance del ejemplo declara participantes de 10 a 13 años. No puedes registrar que infancia no corresponde mientras ese alcance se mantenga.";
  if (scenario === "adultos" && values["aplicabilidad.infancia"] === "Corresponde")
    return "El alcance de este ejemplo declara solo clientes adultos. Selecciona el programa con menores para probar su documentación de infancia.";
  return "";
}
