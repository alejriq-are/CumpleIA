// Contrato editable EipdResolutionAssessmentV1; nunca incluye identidad del servidor.
export type Field = {
  label: string;
  help?: string;
  kind?: "date" | "codes";
  choices?: [string, string][];
  fields?: Fields;
  item?: Fields;
  required?: boolean;
  response?: boolean;
};
export type Fields = Record<string, Field>;
const answer: [string, string][] = [
  ["si", "Sí"],
  ["no", "No"],
  ["pendiente", "Pendiente"],
];
const responseFields: Fields = {
  answer: { label: "Respuesta", choices: answer, required: true },
  rationale: { label: "Fundamento" },
};
const evidence: Fields = {
  evidence_type: { label: "Tipo de evidencia", required: true },
  reference: { label: "Referencia" },
  obtained_on: { label: "Fecha de obtención", kind: "date" },
  mechanism: { label: "Mecanismo" },
  notes: { label: "Notas" },
};
const evidences: Field = { label: "Evidencias", item: evidence };
export const documentFields: Fields = {
  report_reference: { label: "Referencia del informe" },
  prepared_by: { label: "Preparado por" },
  completed_on: { label: "Fecha del documento", kind: "date" },
  purpose_description: {
    label: "Finalidad del tratamiento",
    help: "Describe para qué se usarán los datos en este alcance. Ejemplo ficticio: coordinar citas solicitadas por clientes. Contrasta con la finalidad de la evaluación seleccionada.",
  },
  processing_operations: {
    label: "Operaciones de tratamiento",
    help: "Describe qué se hace con los datos: recoger, consultar, comunicar o eliminar. Ejemplo ficticio: registrar una solicitud y consultar la agenda.",
  },
  processing_context: {
    label: "Contexto del tratamiento",
    help: "Explica quiénes intervienen, a quiénes conciernen los datos y en qué circunstancias se utilizan. Separa los hechos conocidos de los antecedentes pendientes.",
  },
  technologies_description: {
    label: "Tecnologías utilizadas",
    help: "Identifica los sistemas y herramientas utilizados. Ejemplo ficticio: agenda interna con acceso restringido. Indica lo pendiente de confirmar.",
  },
  exceptions_coverage_analysis: { label: "Análisis de excepciones" },
  scope: {
    label: "Alcance del documento",
    fields: {
      data_category_codes: {
        label: "Códigos de categorías de datos",
        help: "Usa los códigos de categorías del alcance RAT asociado, uno por línea; no escribas descripciones ni inventes códigos. Puedes dejar este campo sin completar mientras reúnes los antecedentes.",
        kind: "codes",
      },
      data_subject_codes: {
        label: "Códigos de titulares",
        help: "Titulares son las personas a quienes conciernen los datos. Usa sus códigos del alcance RAT asociado, uno por línea; no nombres de personas.",
        kind: "codes",
      },
    },
  },
  necessity_analysis: { label: "Análisis de necesidad" },
  proportionality_analysis: { label: "Análisis de proporcionalidad" },
  minimization_analysis: { label: "Análisis de minimización" },
  necessary_for_purpose: {
    label: "Necesario para la finalidad",
    fields: responseFields,
    response: true,
  },
  proportionate_processing: {
    label: "Tratamiento proporcionado",
    fields: responseFields,
    response: true,
  },
  minimization_addressed: {
    label: "Minimización abordada",
    fields: responseFields,
    response: true,
  },
  performed_before_processing: {
    label: "Evaluación previa al tratamiento",
    fields: responseFields,
    response: true,
  },
  prior_assessment_analysis: { label: "Análisis de evaluación previa" },
  risks: {
    label: "Riesgos",
    item: {
      risk_id: {
        label: "Identificador del riesgo",
        help: "Asigna un código que permita vincular este riesgo con su valoración y medidas. Ejemplo ficticio: R1. Conserva el mismo código en los pasos siguientes.",
      },
      description: {
        label: "Descripción",
        help: "Describe el suceso, su causa y las personas afectadas. Ejemplo ficticio: un acceso indebido permite consultar datos de contacto. Valora su nivel en el paso Valorar riesgos.",
      },
      impact_analysis: {
        label: "Análisis de impacto",
        help: "Explica el daño potencial a las personas y sus derechos. Ejemplo ficticio: la divulgación de datos de contacto podría exponer a una persona a contactos no deseados.",
      },
      initial_assessment_analysis: {
        label: "Análisis del riesgo inicial",
        help: "Describe el riesgo antes de considerar controles. La selección de probabilidad e impacto se realiza en Valorar riesgos.",
      },
      residual_assessment_analysis: {
        label: "Análisis del riesgo residual",
        help: "Explica qué riesgo permanece después de las medidas y qué falta comprobar. Distingue una reducción esperada de una reducción verificada.",
      },
      evidence: evidences,
    },
  },
  measures: {
    label: "Medidas",
    item: {
      measure_id: { label: "Identificador de la medida" },
      description: { label: "Descripción" },
      effectiveness_analysis: { label: "Análisis de eficacia" },
      implementation_analysis: { label: "Análisis de implementación" },
      risk_ids: { label: "Riesgos asociados", kind: "codes" },
      implemented: { label: "Medida implementada", fields: responseFields, response: true },
      evidence: evidences,
    },
  },
  residual_risk_summary: { label: "Resumen del riesgo residual" },
  residual_risk_rationale: { label: "Fundamento del riesgo residual" },
  residual_risk_level: {
    label: "Nivel del riesgo residual",
    choices: [
      ["no_alto", "No alto"],
      ["alto", "Alto"],
      ["sin_resolver", "Sin resolver"],
    ],
  },
  limitations_analysis: { label: "Limitaciones del análisis" },
  follow_up_plan: { label: "Plan de seguimiento" },
  official_sources: {
    label: "Fuentes del documento",
    fields: {
      status: {
        label: "Estado de identificación",
        choices: [
          ["identificado", "Identificadas"],
          ["no_identificado", "No identificadas"],
          ["pendiente", "Pendiente"],
        ],
      },
      checked_on: { label: "Fecha de consulta", kind: "date" },
      sources: {
        label: "Fuentes",
        item: {
          source_reference: { label: "Referencia de la fuente" },
          publication_version: { label: "Versión de publicación" },
          review_analysis: { label: "Análisis de revisión" },
          applicability: {
            label: "Aplicabilidad",
            choices: [
              ["aplicable", "Aplicable"],
              ["no_aplicable", "No aplicable"],
              ["pendiente", "Pendiente"],
            ],
          },
        },
      },
      applicability_analysis: { label: "Análisis de aplicabilidad" },
      evidence: evidences,
    },
  },
  agency_consultation: {
    label: "Consulta a la autoridad",
    fields: {
      status: {
        label: "Estado de consulta",
        choices: [
          ["no_solicitada", "No solicitada"],
          ["en_curso", "En curso"],
          ["concluida", "Concluida"],
        ],
      },
      analysis: { label: "Análisis de consulta" },
      consultation_reference: { label: "Referencia de consulta" },
      response_reference: { label: "Referencia de respuesta" },
      recommendations_analysis: { label: "Análisis de recomendaciones" },
      reassessment_analysis: { label: "Análisis de reevaluación" },
      recommendations_addressed: {
        label: "Recomendaciones abordadas",
        fields: responseFields,
        response: true,
      },
      evidence: evidences,
    },
  },
  evidence: evidences,
};
const rootFields: Fields = {
  document_reference: { label: "Referencia" },
  document_version: { label: "Versión" },
  notes: { label: "Notas" },
  ...documentFields,
};
function object(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}
function date(value: string) {
  const d = new Date(value + "T00:00:00Z");
  return (
    /^\d{4}-\d{2}-\d{2}$/.test(value) &&
    Number(value.slice(0, 4)) > 0 &&
    Number.isFinite(d.getTime()) &&
    d.toISOString().slice(0, 10) === value
  );
}
function fieldsValid(value: unknown, fields: Fields): boolean {
  if (
    !object(value) ||
    Object.keys(value).some((k) => !Object.hasOwn(fields, k)) ||
    Object.entries(fields).some(([k, f]) => f.required && !Object.hasOwn(value, k))
  )
    return false;
  return Object.entries(value).every(([key, v]) => {
    const f = fields[key];
    if (v === null) return !f.required && !f.item && f.kind !== "codes";
    if (f.item) return Array.isArray(v) && v.every((row) => fieldsValid(row, f.item!));
    if (f.fields) return fieldsValid(v, f.fields);
    if (f.kind === "codes")
      return (
        Array.isArray(v) &&
        v.every((x) => typeof x === "string" && x.trim()) &&
        (key !== "risk_ids" ? new Set(v).size === v.length : true)
      );
    return (
      typeof v === "string" &&
      (!f.required || Boolean(v.trim())) &&
      (!f.choices || f.choices.some(([code]) => code === v)) &&
      (f.kind !== "date" || date(v))
    );
  });
}
export function validDocument(value: unknown): boolean {
  if (!object(value) || value.schema_version !== 1) return false;
  const { schema_version: _, ...fields } = value;
  return fieldsValid(fields, rootFields);
}
// El servidor completa campos omitidos con null/listas vacías; conserva todos los enviados.
export function documentMatches(actual: unknown, expected: unknown): boolean {
  if (Array.isArray(expected))
    return (
      Array.isArray(actual) &&
      expected.length === actual.length &&
      expected.every((v, i) => documentMatches(actual[i], v))
    );
  if (object(expected))
    return (
      object(actual) && Object.entries(expected).every(([k, v]) => documentMatches(actual[k], v))
    );
  return actual === expected;
}

// Discard only wholly empty optional array rows in a copy at save time.
// A partially completed evidence is retained and must identify its type.
export function compactDocument(value: Record<string, unknown>): Record<string, unknown> {
  const empty = (item: unknown): boolean =>
    item == null ||
    item === "" ||
    (typeof item === "string" && !item.trim()) ||
    (Array.isArray(item) && item.every(empty)) ||
    (object(item) && Object.values(item).every(empty));
  const walk = (item: unknown): unknown =>
    Array.isArray(item)
      ? item.filter((row) => !empty(row)).map(walk)
      : object(item)
        ? Object.fromEntries(Object.entries(item).map(([key, child]) => [key, walk(child)]))
        : item;
  return walk(value) as Record<string, unknown>;
}
