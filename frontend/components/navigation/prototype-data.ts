export type ModuleId =
  "panel" | "diagnostico" | "rat" | "licitud" | "documentos" | "evidencia" | "organizacion";
export type TaskId = "resumen" | "completar" | "revisar" | "historial";
export type Scenario = "adultos" | "infancia";
export type Values = Record<string, string>;
export type Field = {
  key: string;
  label: string;
  options?: string[];
  hint?: string;
  singleLine?: boolean;
};
export const modules: {
  id: ModuleId;
  title: string;
  short: string;
  description: string;
  upcoming?: boolean;
}[] = [
  {
    id: "panel",
    title: "Panel principal",
    short: "Inicio",
    description: "Tu espacio de trabajo y las próximas tareas.",
  },
  {
    id: "diagnostico",
    title: "Autodiagnóstico",
    short: "Diagnóstico",
    description: "Identifica los antecedentes que necesitas revisar.",
  },
  {
    id: "rat",
    title: "Inventario de tratamientos",
    short: "Inventario RAT",
    description: "Describe para qué y cómo se utilizan los datos.",
  },
  {
    id: "licitud",
    title: "Bases de licitud",
    short: "Bases de licitud",
    description: "Completa el análisis y consulta cada documento en su contexto.",
  },
  {
    id: "documentos",
    title: "Políticas y referencias normativas",
    short: "Políticas y referencias normativas",
    description: "Módulo próximamente disponible.",
    upcoming: true,
  },
  {
    id: "evidencia",
    title: "Carpeta de evidencias",
    short: "Evidencia",
    description: "Módulo próximamente disponible.",
    upcoming: true,
  },
  {
    id: "organizacion",
    title: "Mi organización",
    short: "Organización",
    description: "Nombre, RUT, rubro y tamaño de la organización.",
  },
];
export const tasks: { id: TaskId; label: string }[] = [
  { id: "resumen", label: "Resumen" },
  { id: "completar", label: "Completar datos" },
  { id: "revisar", label: "Documentos y revisiones" },
  { id: "historial", label: "Historial y descargas" },
];
export const scenarioNames = { adultos: "Clientes adultos", infancia: "Programa con menores" };
export const purpose = {
  adultos: "[FICTICIA] Coordinar citas solicitadas por clientes adultos.",
  infancia: "[FICTICIA] Evaluar un programa con participantes sintéticos de 10 a 13 años.",
};
export const labels: Record<string, string> = {
  estado: "Estado y próximas tareas",
  ayuda: "Cómo probar la maqueta",
  alcance: "Alcance del tratamiento",
  fuentes: "Fuentes y sistemas",
  conservacion: "Conservación y eliminación",
  terceros: "Terceros y transferencias",
  base: "Base y fundamento",
  aplicabilidad: "Determinar aplicabilidad",
  infancia: "Infancia y adolescencia",
  eipd: "Tratamiento y alcance de la EIPD",
  riesgos: "Riesgos y valoración",
  medidas: "Medidas de mitigación",
  anexos: "Anexos de respaldo",
  preparar: "Preparar resolución documental",
  proporcionalidad: "Necesidad y proporcionalidad",
  eipd_fuentes: "Fuentes y evidencias de la EIPD",
  documentos: "Documentos guardados",
  resoluciones: "Resoluciones",
  revisiones: "Revisiones del documento",
  decisiones: "Decisiones de la organización",
  facultades: "Facultades",
  versiones: "Versiones registradas",
  eventos: "Actividad del ejemplo",
  descargas: "Descargas",
  respuestas: "Cuestionario",
  resultados: "Resultados del ejemplo",
  informe: "Informe de ejemplo",
  biblioteca: "Biblioteca documental",
  respaldos: "Respaldos vinculados",
  organizacion: "Datos de la organización",
  equipo: "Equipo del ejemplo",
};
export function steps(module: ModuleId, task: TaskId, scenario: Scenario): string[] {
  if (module === "panel") return ["estado", "ayuda"];
  if (module === "organizacion") return ["organizacion"];
  if (task === "resumen") return ["estado"];
  if (task === "historial") return ["versiones", "eventos", "descargas"];
  if (module === "licitud") {
    if (task === "completar")
      return [
        "aplicabilidad",
        "alcance",
        "base",
        ...(scenario === "infancia" ? ["infancia"] : []),
        "eipd",
        "proporcionalidad",
        "riesgos",
        "medidas",
        "eipd_fuentes",
        "anexos",
        ...(scenario === "infancia" ? ["preparar"] : []),
      ];
    return [
      "documentos",
      ...(scenario === "infancia"
        ? ["resoluciones", "revisiones", "decisiones", "facultades"]
        : ["revisiones"]),
    ];
  }
  if (module === "rat")
    return task === "completar"
      ? ["alcance", "fuentes", "conservacion", "terceros"]
      : ["documentos"];
  if (module === "diagnostico")
    return task === "completar"
      ? ["respuestas", ...Array.from({ length: 9 }, (_, i) => `respuesta${i + 2}`)]
      : ["resultados", "informe"];
  if (module === "documentos") return ["biblioteca", "documentos"];
  return ["respaldos", "anexos"];
}
export const fields: Record<string, Field[]> = {
  aplicabilidad: [
    {
      key: "aplicabilidad.eipd",
      label: "¿Corresponde realizar una EIPD?",
      options: [
        "Pendiente de analizar",
        "Corresponde",
        "No corresponde",
        "Información insuficiente",
      ],
    },
    {
      key: "aplicabilidad.eipd_fundamento",
      label: "Fundamento sobre EIPD",
      hint: "Explica el análisis del alcance, contexto y riesgos. La presencia de menores no determina por sí sola una EIPD.",
    },
    {
      key: "aplicabilidad.infancia",
      label: "¿Corresponde documentar infancia y adolescencia?",
      options: [
        "Pendiente de analizar",
        "Corresponde",
        "No corresponde",
        "Información insuficiente",
      ],
    },
    {
      key: "aplicabilidad.infancia_fundamento",
      label: "Fundamento sobre infancia y adolescencia",
      hint: "Indica si los datos conciernen a niños, niñas o adolescentes y contrasta la conclusión con el alcance del RAT.",
    },
  ],
  alcance: [
    { key: "rat.nombre", label: "Nombre del tratamiento" },
    { key: "rat.finalidad", label: "Finalidad" },
    { key: "rat.categorias", label: "Categorías de datos" },
    { key: "rat.titulares", label: "Titulares incluidos" },
  ],
  fuentes: [
    { key: "rat.fuentes", label: "Origen de los datos" },
    { key: "rat.sistemas", label: "Sistemas utilizados" },
  ],
  conservacion: [
    { key: "rat.conservacion", label: "Regla de conservación" },
    { key: "rat.eliminacion", label: "Método de eliminación" },
  ],
  terceros: [
    { key: "rat.terceros", label: "Terceros que reciben los datos" },
    { key: "rat.transferencias", label: "Transferencias internacionales" },
  ],
  base: [
    {
      key: "base.tipo",
      label: "Base de licitud propuesta",
      options: [
        "Pendiente de definir",
        "Consentimiento",
        "Interés legítimo",
        "Contrato",
        "Obligación legal",
      ],
    },
    {
      key: "base.fundamento",
      label: "Fundamento",
      hint: "Explica la propuesta. Seleccionarla no acredita su validez.",
    },
  ],
  infancia: [
    { key: "infancia.edad", label: "Edad y alcance" },
    { key: "infancia.interes", label: "Interés superior" },
    { key: "infancia.autonomia", label: "Autonomía progresiva" },
    {
      key: "infancia.autorizacion",
      label: "Vía de autorización propuesta",
      options: ["Sin declarar", "Pendiente de revisión"],
    },
    { key: "infancia.notas", label: "Notas de infancia" },
  ],
  eipd: [
    { key: "eipd.referencia", label: "Referencia del documento EIPD" },
    { key: "eipd.tratamiento", label: "Tratamiento y alcance de la EIPD" },
    { key: "eipd.seguimiento", label: "Riesgo residual y seguimiento" },
  ],
  proporcionalidad: [{ key: "eipd.analisis", label: "Necesidad y proporcionalidad" }],
  eipd_fuentes: [{ key: "eipd.fuentes", label: "Fuentes y evidencias del análisis" }],
  riesgos: [
    { key: "riesgos.descripcion", label: "R1 · Descripción del riesgo" },
    {
      key: "riesgos.probabilidad",
      label: "Probabilidad residual del ejemplo",
      options: ["Sin evaluar", "Baja", "Media", "Alta"],
    },
    {
      key: "riesgos.impacto",
      label: "Impacto residual del ejemplo",
      options: ["Sin evaluar", "Bajo", "Moderado", "Grave"],
    },
    { key: "riesgos.fundamento", label: "Fundamento de la valoración" },
  ],
  medidas: [
    { key: "medidas.descripcion", label: "M1 · Medida de mitigación" },
    {
      key: "medidas.dimension",
      label: "Dimensión de mitigación",
      options: ["Sin evaluar", "Probabilidad", "Impacto", "Ambas"],
    },
    {
      key: "medidas.eficacia",
      label: "Eficacia declarada",
      options: ["Sin evaluar", "Parcial", "Suficiente"],
    },
    {
      key: "medidas.estado",
      label: "Estado de la medida",
      options: ["Propuesta", "Implementación declarada", "Verificación declarada"],
    },
  ],
  anexos: [
    { key: "anexos.referencia", label: "Referencia del anexo de ejemplo" },
    { key: "anexos.descripcion", label: "Descripción del respaldo" },
    {
      key: "anexos.seccion",
      label: "Sección relacionada",
      options: [
        "Alcance",
        "Base y fundamento",
        "Necesidad y proporcionalidad",
        "Riesgos",
        "Medidas",
        "Fuentes y evidencias",
        "Seguimiento",
      ],
    },
    {
      key: "anexos.riesgos",
      label: "Códigos de riesgos vinculados (opcional)",
      hint: "Un código por línea. Ejemplo: R1.",
    },
    {
      key: "anexos.medidas",
      label: "Códigos de medidas vinculadas (opcional)",
      hint: "Un código por línea. Ejemplo: M1.",
    },
  ],
  preparar: [
    { key: "preparar.referencia", label: "Referencia de la nueva resolución" },
    { key: "preparar.notas", label: "Notas de la resolución en preparación" },
    { key: "preparar.motivo", label: "Motivo del cambio" },
  ],
  respuestas: [
    {
      key: "diagnostico.respuesta",
      label: "¿Se han identificado los tratamientos de datos?",
      options: ["Sin responder", "Sí", "Parcialmente", "No"],
    },
    { key: "diagnostico.notas", label: "Antecedentes de la respuesta" },
  ],
  organizacion: [
    { key: "organizacion.nombre", label: "Nombre de la organización", singleLine: true },
    { key: "organizacion.rut", label: "RUT", singleLine: true },
    { key: "organizacion.rubro", label: "Rubro / industria", singleLine: true },
    {
      key: "organizacion.tamano",
      label: "Tamaño",
      options: [
        "Sin especificar",
        "Micro empresa",
        "Pequeña empresa (PYME)",
        "Mediana empresa (PYME)",
        "Gran Empresa",
      ],
    },
  ],
};
for (let i = 2; i <= 10; i++) {
  labels[`respuesta${i}`] = `Sección ${i} del autodiagnóstico`;
  fields[`respuesta${i}`] = [
    {
      key: `diagnostico.seccion${i}`,
      label: `Observaciones de la sección ${i} de ejemplo`,
      hint: "Campo ilustrativo para probar navegación. No reproduce el cuestionario completo ni calcula resultados.",
    },
  ];
}
labels.respuestas = "Sección 1 · Tratamientos identificados";
export const initial = (s: Scenario): Values => ({
  "rat.nombre":
    s === "adultos"
      ? "[FICTICIA] Gestión de clientes"
      : "[FICTICIA] Programa de fidelización con menores",
  "rat.finalidad": purpose[s],
  "rat.categorias": "Datos de identificación",
  "rat.titulares":
    s === "adultos" ? "Clientes adultos sintéticos" : "Participantes sintéticos de 10 a 13 años",
  "rat.fuentes": "[FICTICIA] Registros sintéticos preparados para la maqueta.",
  "rat.conservacion": "[FICTICIA] Plazo del ensayo pendiente de revisión.",
  "organizacion.nombre": "CumpleIA Demo",
  "organizacion.rut": "1111111-0",
  "organizacion.rubro": "Consultoría",
  "organizacion.tamano": "Pequeña empresa (PYME)",
  "base.tipo": "Pendiente de definir",
  "base.fundamento": "[FICTICIA] Análisis pendiente. No existe autorización para operar.",
  "infancia.edad": "[FICTICIA] Participantes sintéticos de 10 a 13 años.",
  "infancia.interes": "[FICTICIA] Análisis pendiente de beneficios, riesgos y protección.",
  "infancia.autonomia": "[FICTICIA] Comprensión y participación por analizar.",
  "infancia.autorizacion": "Sin declarar",
  "infancia.notas": "[FICTICIA] Documento de ensayo sin valor jurídico.",
  "eipd.referencia": "SIMULADA-MAQUETA-EIPD-001",
  "eipd.analisis": "[FICTICIA] Necesidad y proporcionalidad pendientes de revisión.",
  "riesgos.descripcion": "[FICTICIA] Acceso indebido a datos de identificación.",
  "riesgos.probabilidad": "Baja",
  "riesgos.impacto": "Grave",
  "riesgos.fundamento": "[FICTICIA] Ejemplo sin medición real.",
  "medidas.descripcion": "[FICTICIA] Restringir el acceso según funciones autorizadas.",
  "medidas.dimension": "Probabilidad",
  "medidas.eficacia": "Parcial",
  "medidas.estado": "Propuesta",
  "anexos.seccion": "Base y fundamento",
  "preparar.referencia": "SIMULADA-MAQUETA-RES-003",
  "preparar.notas": "[FICTICIA] Preparación temporal del ejemplo.",
});
export type Resolution = {
  reference: string;
  version: number;
  notes: string;
  origin?: string;
  reason?: string;
};
export const seedResolutions = (): Resolution[] => [
  {
    reference: "SIMULADA-MAQUETA-RES-001",
    version: 1,
    notes: "[FICTICIA] Primer documento del ejemplo. Análisis y evidencias pendientes.",
  },
  {
    reference: "SIMULADA-MAQUETA-RES-002",
    version: 2,
    notes: "[FICTICIA] Segundo documento del ejemplo. Requiere revisión; no autoriza acciones.",
  },
];

export type EvaluationId = "adultos" | "adultos-citas-v2" | "adultos-comercial" | "infancia";
export const treatmentOptions: { id: Scenario; label: string }[] = [
  { id: "adultos", label: "[FICTICIA] Gestión de clientes" },
  { id: "infancia", label: "[FICTICIA] Programa de fidelización con menores" },
];
export const purposeOptions = [
  { id: "citas", treatment: "adultos", label: purpose.adultos },
  {
    id: "comercial",
    treatment: "adultos",
    label: "[FICTICIA] Atender consultas y realizar seguimiento comercial de clientes adultos.",
  },
  { id: "programa", treatment: "infancia", label: purpose.infancia },
];
export type ExampleEvaluation = {
  id: EvaluationId;
  treatment: Scenario;
  purposeId: string;
  version: number;
  label: string;
};
export const evaluationOptions: ExampleEvaluation[] = [
  {
    id: "adultos",
    treatment: "adultos",
    purposeId: "citas",
    version: 1,
    label: "Evaluación de citas · versión 1 · Borrador",
  },
  {
    id: "adultos-citas-v2",
    treatment: "adultos",
    purposeId: "citas",
    version: 2,
    label: "Evaluación de citas · versión 2 · Borrador",
  },
  {
    id: "adultos-comercial",
    treatment: "adultos",
    purposeId: "comercial",
    version: 1,
    label: "Evaluación de seguimiento comercial · versión 1 · Borrador",
  },
  {
    id: "infancia",
    treatment: "infancia",
    purposeId: "programa",
    version: 1,
    label: "Evaluación del programa con menores · versión 1 · Borrador",
  },
];
export function evaluationRecords<T>(
  factory: (evaluation: ExampleEvaluation) => T
): Record<EvaluationId, T> {
  return Object.fromEntries(
    evaluationOptions.map((evaluation) => [evaluation.id, factory(evaluation)])
  ) as Record<EvaluationId, T>;
}
export function initialEvaluations(): Record<EvaluationId, Values> {
  return evaluationRecords((evaluation) => ({
    ...initial(evaluation.treatment),
    "aplicabilidad.eipd": "Pendiente de analizar",
    "aplicabilidad.eipd_fundamento": "",
    "aplicabilidad.infancia": "Pendiente de analizar",
    "aplicabilidad.infancia_fundamento": "",
    "rat.finalidad": purposeOptions.find((item) => item.id === evaluation.purposeId)!.label,
    "eipd.referencia": `SIMULADA-MAQUETA-EIPD-${evaluation.id.toUpperCase()}`,
  }));
}
