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
  const summary = group("resumen", module === "rat" ? "Catálogo" : "Resumen", "resumen", [
    "estado",
  ]);
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
      group("inicio", "Vista general", "resumen", ["estado"]),
      group("ayuda", "Cómo probar la maqueta", "resumen", ["ayuda"]),
    ];
  if (module === "licitud")
    return [
      group("alcance", "Alcance del RAT", "completar", ["alcance"]),
      group("base", "Base y fundamento", "completar", ["base"]),
      ...(scenario === "infancia"
        ? [group("infancia", "Infancia", "completar", ["infancia"])]
        : []),
      group("eipd", "Documentar EIPD", "completar", [
        "eipd",
        "proporcionalidad",
        "riesgos",
        "medidas",
        "eipd_fuentes",
      ]),
      group("anexos", "Anexos de respaldo", "completar", ["anexos"]),
      ...(scenario === "infancia"
        ? [
            group(
              "resoluciones",
              "Resoluciones y revisiones",
              "revisar",
              ["resoluciones", "revisiones", "decisiones", "facultades"],
              true
            ),
          ]
        : []),
      group("consultas", "Documentos guardados", "revisar", [
        "documentos",
        ...(scenario === "adultos" ? ["revisiones"] : []),
      ]),
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
export function groupDestinations(group: NavigationGroup, scenario: Scenario): Destination[] {
  return group.id === "resoluciones" && scenario === "infancia"
    ? [{ module: "licitud", task: "completar", section: "preparar" }, ...group.items]
    : group.items;
}
export function destinationLabel(section: string): string {
  return (
    (
      {
        eipd: "Tratamiento y alcance",
        riesgos: "Valorar riesgos",
        medidas: "Valorar medidas",
        eipd_fuentes: "Fuentes y evidencias",
      } as Record<string, string>
    )[section] ?? labels[section]
  );
}
