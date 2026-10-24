import { labels, steps, type ModuleId, type TaskId, type Scenario } from "./prototype-data";
export type Destination = { module: ModuleId; task: TaskId; section: string };
export type NavigationGroup = { id: string; label: string; items: Destination[]; accent?: boolean };
export function moduleNavigation(module: ModuleId, scenario: Scenario): NavigationGroup[] {
  const group = (
    id: string,
    label: string,
    task: TaskId,
    sections: string[],
    accent = false
  ): NavigationGroup => ({
    id,
    label,
    accent,
    items: sections.map((section) => ({ module, task, section })),
  });
  const summary = group(
    "resumen",
    module === "rat" ? "Catálogo de tratamientos" : labels.estado,
    "resumen",
    ["estado"]
  );
  const documents = group(
    "documentos",
    "Documentos y revisiones",
    "revisar",
    steps(module, "revisar", scenario)
  );
  const history = group(
    "historial",
    "Historial y descargas",
    "historial",
    steps(module, "historial", scenario)
  );
  if (module === "documentos" || module === "evidencia") return [];
  if (module === "organizacion")
    return [group("datos", "Datos de la organización", "completar", ["organizacion"])];
  if (module === "panel")
    return [
      group("inicio", "Panel principal", "resumen", ["estado"]),
      group("ayuda", "Cómo probar la maqueta", "resumen", ["ayuda"]),
    ];
  if (module === "licitud")
    return [
      group("alcance", labels.alcance, "completar", ["alcance"]),
      group("preparar", "Preparar", "completar", [
        ...(scenario === "infancia" ? ["preparar"] : []),
        "base",
        ...(scenario === "infancia" ? ["infancia"] : []),
        "eipd",
        "proporcionalidad",
        "riesgos",
        "medidas",
        "eipd_fuentes",
        "anexos",
      ]),
      group("revisar", "Revisar y decidir", "revisar", steps(module, "revisar", scenario)),
      history,
    ];
  if (module === "rat")
    return [
      summary,
      group(
        "actividad",
        "Actividad de tratamiento",
        "completar",
        steps(module, "completar", scenario)
      ),
      documents,
      history,
    ];
  if (module === "diagnostico")
    return [
      summary,
      group(
        "secciones",
        "Secciones del autodiagnóstico",
        "completar",
        steps(module, "completar", scenario)
      ),
      group("resultados", "Resultados e informe", "revisar", ["resultados", "informe"]),
      history,
    ];
  return [
    summary,
    group(
      "editar",
      module === "documentos"
        ? "Biblioteca documental"
        : module === "evidencia"
          ? "Gestionar respaldos"
          : "Datos y equipo",
      "completar",
      steps(module, "completar", scenario)
    ),
    documents,
    history,
  ];
}
export function groupDestinations(group: NavigationGroup, _scenario: Scenario): Destination[] {
  return group.items;
}
export function destinationLabel(section: string, module?: ModuleId): string {
  if (section === "estado" && module === "rat") return "Catálogo de tratamientos";
  if (section === "estado" && module === "panel") return "Panel principal";
  return labels[section] ?? section;
}
export function actionLabel(destination: Destination, scenario?: Scenario): string {
  if (destination.section === "preparar") return "Preparación";
  if (
    destination.module === "licitud" &&
    destination.section === "revisiones" &&
    scenario === "infancia"
  )
    return "Revisión";
  if (destination.module === "licitud" && destination.section === "decisiones") return "Decisión";
  if (
    destination.task === "completar" &&
    !(destination.module === "licitud" && destination.section === "alcance")
  )
    return "Editar";
  return "Consulta";
}
export function destinationHint(destination: Destination, scenario?: Scenario): string {
  if (
    destination.module === "licitud" &&
    destination.section === "revisiones" &&
    scenario !== "infancia"
  )
    return "Acceso previsto a la revisión documental de adultos. Aquí solo se consulta; no registra observaciones.";
  switch (actionLabel(destination, scenario)) {
    case "Preparación":
      return "Borrador temporal. La vista previa permite revisar antes de registrar una nueva resolución simulada.";
    case "Revisión":
      return "Registra observaciones sobre la resolución seleccionada. No es una decisión de la organización.";
    case "Decisión":
      return "Decisión de la organización, separada de la revisión documental y sujeta a facultades vigentes.";
    case "Editar":
      return "Completa los antecedentes del ejemplo y guarda antes de consultar el documento.";
    default:
      return "Consulta del ejemplo. Abrir esta pantalla no modifica los registros.";
  }
}
