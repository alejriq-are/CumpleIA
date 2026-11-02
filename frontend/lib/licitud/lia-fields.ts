export type LegalField = { key: string; label: string; kind?: string };
export const liaGroups: { key: string; label: string; fields: LegalField[] }[] = [
  {
    key: "purpose_and_interest",
    label: "Finalidad e interés",
    fields: [
      { key: "purpose_description", label: "Descripción de la finalidad" },
      { key: "legitimate_interest", label: "Interés legítimo declarado" },
      {
        key: "interest_holder",
        label: "Titular del interés",
        kind: "responsable:Responsable|tercero:Tercero|ambos:Ambos",
      },
      { key: "controller_benefit", label: "Beneficio para el responsable" },
      { key: "third_party_benefit", label: "Beneficio para terceros" },
      { key: "public_benefit", label: "Beneficio público" },
      { key: "interest_importance", label: "Importancia del interés" },
      {
        key: "consequences_without_processing",
        label: "Consecuencias de no realizar el tratamiento",
      },
      { key: "relevant_rules", label: "Normas pertinentes" },
      { key: "ethical_considerations", label: "Consideraciones éticas" },
    ],
  },
  {
    key: "necessity",
    label: "Necesidad y proporcionalidad",
    fields: [
      { key: "contributes_to_purpose", label: "¿Contribuye a la finalidad?", kind: "response" },
      { key: "linked_to_interest", label: "¿Está vinculado al interés?", kind: "response" },
      {
        key: "achievable_without_personal_data",
        label: "¿Puede lograrse sin datos personales?",
        kind: "response",
      },
      {
        key: "less_intrusive_alternative",
        label: "¿Existe una alternativa menos intrusiva?",
        kind: "response",
      },
      { key: "fewer_data_possible", label: "¿Pueden usarse menos datos?", kind: "response" },
      {
        key: "categories_necessary_and_relevant",
        label: "¿Las categorías son necesarias y pertinentes?",
        kind: "response",
      },
      { key: "necessity_analysis", label: "Análisis de necesidad" },
      { key: "proportionality_analysis", label: "Análisis de proporcionalidad" },
      { key: "alternatives_analysis", label: "Alternativas consideradas" },
      { key: "minimization_analysis", label: "Análisis de minimización" },
    ],
  },
  {
    key: "nature_and_scope",
    label: "Naturaleza y alcance",
    fields: [
      {
        key: "exclusively_professional_context",
        label: "¿El contexto es exclusivamente profesional?",
        kind: "response",
      },
      { key: "volume_and_scope", label: "Naturaleza y alcance" },
      { key: "special_rules_description", label: "Reglas especiales aplicables" },
      { key: "additional_risk_factors", label: "Factores adicionales de riesgo" },
    ],
  },
  {
    key: "reasonable_expectations",
    label: "Expectativas razonables",
    fields: [
      { key: "prior_relationship", label: "¿Existe una relación previa?", kind: "response" },
      { key: "relationship_description", label: "Descripción de la relación" },
      {
        key: "significant_change_of_use",
        label: "¿Existe un cambio significativo de uso?",
        kind: "response",
      },
      {
        key: "informed_at_direct_collection",
        label: "¿Se informó al recoger directamente los datos?",
        kind: "response",
      },
      {
        key: "third_party_information",
        label: "Información cuando los datos proceden de terceros",
      },
      { key: "technology_or_context_changes", label: "Cambios tecnológicos o de contexto" },
      {
        key: "foreseeable_purpose_and_method",
        label: "¿Son previsibles la finalidad y el método?",
        kind: "response",
      },
      { key: "innovative_processing", label: "¿El tratamiento es innovador?", kind: "response" },
      { key: "expectations_evidence", label: "Antecedentes de las expectativas" },
      { key: "expectations_analysis", label: "Expectativas de los titulares" },
    ],
  },
  {
    key: "impact",
    label: "Impactos en las personas",
    fields: [
      { key: "negative_effects", label: "Efectos negativos" },
      {
        key: "severity",
        label: "Gravedad del impacto",
        kind: "baja:Baja|media:Media|alta:Alta|pendiente:Pendiente",
      },
      {
        key: "likelihood",
        label: "Probabilidad del impacto",
        kind: "baja:Baja|media:Media|alta:Alta|pendiente:Pendiente",
      },
      { key: "loss_of_control", label: "¿Existe pérdida de control?", kind: "response" },
      { key: "intrusion_analysis", label: "Análisis de intrusión" },
      {
        key: "reasonable_opposition_likelihood",
        label: "¿Es razonable esperar oposición?",
        kind: "response",
      },
      { key: "rights_and_freedoms_analysis", label: "Análisis de derechos y libertades" },
      { key: "vulnerable_people_impact", label: "Impacto en personas vulnerables" },
      {
        key: "transparently_explainable",
        label: "¿Puede explicarse de forma transparente?",
        kind: "response",
      },
      {
        key: "relevant_unmitigated_impacts",
        label: "¿Hay impactos relevantes sin mitigar?",
        kind: "response",
      },
      { key: "impact_analysis", label: "Impactos en los titulares" },
    ],
  },
  {
    key: "safeguards",
    label: "Salvaguardas",
    fields: [
      { key: "measures", label: "Medidas y los impactos que mitigan", kind: "measures" },
      { key: "safeguards_analysis", label: "Medidas de protección" },
    ],
  },
  {
    key: "transparency_and_opposition",
    label: "Transparencia y oposición",
    fields: [
      { key: "information_method", label: "Medio para informar" },
      { key: "interest_communication", label: "Comunicación del interés" },
      { key: "opposition_channel", label: "Canal de oposición" },
      { key: "opposition_procedure", label: "Procedimiento de oposición" },
      { key: "responsible_area", label: "Área responsable" },
    ],
  },
  {
    key: "conclusion",
    label: "Conclusión del balance",
    fields: [
      { key: "balancing_summary", label: "Balance y fundamentos pendientes de revisión" },
      { key: "identified_interest", label: "Interés identificado" },
      {
        key: "necessity_and_proportionality_result",
        label: "Resultado de necesidad y proporcionalidad",
      },
      { key: "main_impacts", label: "Impactos principales" },
      { key: "relevant_safeguards", label: "Salvaguardas relevantes" },
      { key: "rights_protection_reasoning", label: "Fundamento de protección de derechos" },
      {
        key: "decision",
        label: "Conclusión propuesta",
        kind: "puede_basarse:Puede basarse|no_puede_basarse:No puede basarse|requiere_revision:Requiere revisión",
      },
    ],
  },
];
export const liaFields = liaGroups.flatMap((group) =>
  group.fields.map((field) => [group.key, field.key, field.label] as const)
);
