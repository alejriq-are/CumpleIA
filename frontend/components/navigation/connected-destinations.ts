import { modules, type ModuleId } from "./prototype-data";
import { eipdSections, ratSections, type WorkLocation } from "./connected-navigation";

// Visible names belong to destinations; route IDs and server values stay unchanged.
export const connectedDestinations = {
  rat: {
    catalogo: "Inventario de tratamientos",
    resumen: "Inventario de tratamientos",
    nuevo: "Nueva actividad",
  },
  diagnostico: {
    cuestionario: "Cuestionario",
    resultados: "Resultado del autodiagnóstico",
    informe: "Resultado del autodiagnóstico",
  },
  licitud: {
    catalogo: "Evaluaciones y creación de borrador",
    resumen: "Recorrido de esta evaluación",
    aplicabilidad: "Determinar aplicabilidad",
    alcance: "Alcance del RAT",
    base: "Base y fundamento",
    anexos: "Anexos de respaldo",
    infancia: "Completar infancia y adolescencia",
    preparar: "Preparar resolución documental",
    revisar: "Documentos guardados",
    historial: "Historial y descargas",
  },
} as const;

export function connectedDestinationLabel(
  location: WorkLocation,
  diagnosticItems: { id: string; label: string }[] = []
): string {
  if (location.module === "diagnostico") {
    const section = diagnosticItems.find((item) => item.id === location.section);
    if (section) return section.label;
  }
  if (location.module === "rat") {
    const section = ratSections.find(([id]) => id === location.section);
    if (section) return section[1];
  }
  if (location.module === "licitud" && location.section === "eipd")
    return eipdSections[location.step];
  const destinations: Partial<Record<ModuleId, Readonly<Record<string, string>>>> =
    connectedDestinations;
  const label = destinations[location.module]?.[location.section];
  return label ?? modules.find((item) => item.id === location.module)?.title ?? "Panel principal";
}
