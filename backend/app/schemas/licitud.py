"""Contratos Pydantic del Módulo 3 — Bases de Licitud.

Define los contratos versionados para evaluaciones jurídicas y para el
contexto RAT utilizado por M3. Los identificadores técnicos de M2 no forman
parte de la identidad semántica histórica del contexto.
"""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

LegalBasis = Literal[
    "consentimiento_art12",
    "obligaciones_economicas_art13a",
    "obligacion_legal_art13b",
    "contrato_precontractual_art13c",
    "interes_legitimo_art13d",
    "defensa_derechos_art13e",
]

LegalAssessmentStatus = Literal[
    "borrador",
    "confirmado",
    "reemplazado",
]


class LegalAssessmentScopeIn(BaseModel):
    """Selección M2 aplicable a la finalidad evaluada."""

    data_category_codes: list[str] = Field(default_factory=list)
    data_subject_codes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_codigos_de_alcance(self):
        if any(not code.strip() for code in self.data_category_codes):
            raise ValueError("data_category_codes no admite códigos vacíos")
        if any(not code.strip() for code in self.data_subject_codes):
            raise ValueError("data_subject_codes no admite códigos vacíos")
        if len(self.data_category_codes) != len(set(self.data_category_codes)):
            raise ValueError("data_category_codes no admite códigos duplicados")
        if len(self.data_subject_codes) != len(set(self.data_subject_codes)):
            raise ValueError("data_subject_codes no admite códigos duplicados")
        return self


# ── Checklist de consentimiento v1 ────────────────────────────────────────────

ConsentQuestionIdV1 = Literal[
    "consentimiento_libre",
    "consentimiento_informado",
    "consentimiento_especifico_finalidad",
    "consentimiento_previo",
    "voluntad_inequivoca",
    "accion_afirmativa_clara",
    "revocacion_posible",
    "revocacion_medio_equivalente",
    "revocacion_expedita",
    "revocacion_fidedigna",
    "revocacion_gratuita",
    "revocacion_disponible_permanentemente",
    "responsable_puede_acreditar",
    "contexto_contrato_servicio",
    "mandatario_facultad_expresa",
    "tratamiento_necesario_contrato_servicio",
]

ConsentAnswerValueV1 = Literal["si", "no", "no_aplica", "pendiente"]


class ConsentAnswerV1(BaseModel):
    question_id: ConsentQuestionIdV1
    answer: ConsentAnswerValueV1
    comment: str | None = None


class ConsentEvidenceV1(BaseModel):
    """Metadata documental M3, independiente de la bitácora M5."""

    evidence_type: str
    reference: str | None = None
    obtained_on: date | None = None
    mechanism: str | None = None
    notes: str | None = None


class ConsentAssessmentV1(BaseModel):
    """Contrato físico v1; admite borradores sin checklist completo."""

    schema_version: Literal[1] = 1
    given_by: Literal["titular", "representante_legal", "mandatario"] | None = None
    grant_method: (
        Literal[
            "escrito", "verbal", "electronico", "acto_afirmativo", "otro_documentado"
        ]
        | None
    ) = None
    answers: list[ConsentAnswerV1] = Field(default_factory=list)
    evidence: list[ConsentEvidenceV1] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def validar_preguntas_unicas(self):
        question_ids = [item.question_id for item in self.answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("answers no admite question_id duplicados")
        return self


# ── Evaluación de interés legítimo v1 ─────────────────────────────────────────


class LiaSectionV1(BaseModel):
    """Campos físicos explícitos: no descartar silenciosamente claves nuevas."""

    model_config = ConfigDict(extra="forbid")


class LiaResponseV1(LiaSectionV1):
    answer: Literal["si", "no", "no_aplica", "pendiente"]
    comment: str | None = None


class LiaPurposeAndInterestV1(LiaSectionV1):
    purpose_description: str | None = None
    legitimate_interest: str | None = None
    interest_holder: Literal["responsable", "tercero", "ambos"] | None = None
    controller_benefit: str | None = None
    third_party_benefit: str | None = None
    public_benefit: str | None = None
    interest_importance: str | None = None
    consequences_without_processing: str | None = None
    relevant_rules: str | None = None
    ethical_considerations: str | None = None


class LiaNecessityV1(LiaSectionV1):
    contributes_to_purpose: LiaResponseV1 | None = None
    linked_to_interest: LiaResponseV1 | None = None
    achievable_without_personal_data: LiaResponseV1 | None = None
    less_intrusive_alternative: LiaResponseV1 | None = None
    fewer_data_possible: LiaResponseV1 | None = None
    categories_necessary_and_relevant: LiaResponseV1 | None = None
    necessity_analysis: str | None = None
    proportionality_analysis: str | None = None
    alternatives_analysis: str | None = None
    minimization_analysis: str | None = None


class LiaNatureAndScopeV1(LiaSectionV1):
    exclusively_professional_context: LiaResponseV1 | None = None
    volume_and_scope: str | None = None
    special_rules_description: str | None = None
    additional_risk_factors: str | None = None


class LiaReasonableExpectationsV1(LiaSectionV1):
    prior_relationship: LiaResponseV1 | None = None
    relationship_description: str | None = None
    significant_change_of_use: LiaResponseV1 | None = None
    informed_at_direct_collection: LiaResponseV1 | None = None
    third_party_information: str | None = None
    technology_or_context_changes: str | None = None
    foreseeable_purpose_and_method: LiaResponseV1 | None = None
    innovative_processing: LiaResponseV1 | None = None
    expectations_evidence: str | None = None
    expectations_analysis: str | None = None


class LiaImpactV1(LiaSectionV1):
    negative_effects: str | None = None
    severity: Literal["baja", "media", "alta", "pendiente"] | None = None
    likelihood: Literal["baja", "media", "alta", "pendiente"] | None = None
    loss_of_control: LiaResponseV1 | None = None
    intrusion_analysis: str | None = None
    reasonable_opposition_likelihood: LiaResponseV1 | None = None
    rights_and_freedoms_analysis: str | None = None
    vulnerable_people_impact: str | None = None
    transparently_explainable: LiaResponseV1 | None = None
    relevant_unmitigated_impacts: LiaResponseV1 | None = None
    impact_analysis: str | None = None


class LiaSafeguardV1(LiaSectionV1):
    description: str
    mitigated_impact: str | None = None


class LiaSafeguardsV1(LiaSectionV1):
    measures: list[LiaSafeguardV1] = Field(default_factory=list)
    safeguards_analysis: str | None = None


class LiaTransparencyAndOppositionV1(LiaSectionV1):
    information_method: str | None = None
    interest_communication: str | None = None
    opposition_channel: str | None = None
    opposition_procedure: str | None = None
    responsible_area: str | None = None


class LiaConclusionV1(LiaSectionV1):
    balancing_summary: str | None = None
    identified_interest: str | None = None
    necessity_and_proportionality_result: str | None = None
    main_impacts: str | None = None
    relevant_safeguards: str | None = None
    rights_protection_reasoning: str | None = None
    decision: (
        Literal["puede_basarse", "no_puede_basarse", "requiere_revision"] | None
    ) = None


class LiaAssessmentV1(LiaSectionV1):
    """Contrato documental LIA v1; admite secciones incompletas en borrador."""

    schema_version: Literal[1] = 1
    purpose_and_interest: LiaPurposeAndInterestV1 = Field(
        default_factory=LiaPurposeAndInterestV1
    )
    necessity: LiaNecessityV1 = Field(default_factory=LiaNecessityV1)
    nature_and_scope: LiaNatureAndScopeV1 = Field(default_factory=LiaNatureAndScopeV1)
    reasonable_expectations: LiaReasonableExpectationsV1 = Field(
        default_factory=LiaReasonableExpectationsV1
    )
    impact: LiaImpactV1 = Field(default_factory=LiaImpactV1)
    safeguards: LiaSafeguardsV1 = Field(default_factory=LiaSafeguardsV1)
    transparency_and_opposition: LiaTransparencyAndOppositionV1 = Field(
        default_factory=LiaTransparencyAndOppositionV1
    )
    conclusion: LiaConclusionV1 = Field(default_factory=LiaConclusionV1)


# ── Expediente contractual v1 ───────────────────────────────────────────────


class ContractResponseV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: Literal["si", "no", "pendiente"]
    rationale: str | None = None


class ContractEvidenceV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_type: str
    reference: str | None = None
    obtained_on: date | None = None
    mechanism: str | None = None
    notes: str | None = None


class ContractAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    route: (
        Literal[
            "celebracion_contrato", "ejecucion_contrato", "medidas_precontractuales"
        ]
        | None
    ) = None
    purpose_description: str | None = None
    relationship_description: str | None = None
    contractual_reference: str | None = None
    contractual_object: str | None = None
    processing_operations: str | None = None
    necessity_analysis: str | None = None
    data_minimization_analysis: str | None = None
    holder_is_party: ContractResponseV1 | None = None
    necessary_for_route: ContractResponseV1 | None = None
    purpose_within_route: ContractResponseV1 | None = None
    precontractual_measures: str | None = None
    requested_by_holder: ContractResponseV1 | None = None
    request_reference: str | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


# ── Expediente de obligación legal v1 ───────────────────────────────────────


class NormativeReferenceV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    norm_name: str | None = None
    provision: str | None = None
    official_source_url: HttpUrl | None = None
    version_reference: str | None = None
    relevance_analysis: str | None = None


class LegalObligationAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    route: (
        Literal["cumplimiento_obligacion_legal", "tratamiento_dispuesto_por_ley"] | None
    ) = None
    purpose_description: str | None = None
    normative_requirement_description: str | None = None
    processing_operations: str | None = None
    applicability_analysis: str | None = None
    necessity_analysis: str | None = None
    data_minimization_analysis: str | None = None
    normative_references: list[NormativeReferenceV1] = Field(default_factory=list)
    normative_basis_reviewed: ContractResponseV1 | None = None
    normative_basis_in_force: ContractResponseV1 | None = None
    processing_within_legal_scope: ContractResponseV1 | None = None
    obligation_applies_to_controller: ContractResponseV1 | None = None
    processing_required_by_law: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


# ── Expediente de defensa de derechos v1 ────────────────────────────────────


class RightsDefenseAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    route: (
        Literal["formulacion_derecho", "ejercicio_derecho", "defensa_derecho"] | None
    ) = None
    purpose_description: str | None = None
    right_description: str | None = None
    right_basis_reference: str | None = None
    right_holder: Literal["responsable", "tercero", "ambos"] | None = None
    holder_connection_analysis: str | None = None
    forum_type: Literal["tribunal_justicia", "organo_publico"] | None = None
    forum_description: str | None = None
    proceeding_stage: Literal["preparacion", "en_curso", "finalizado"] | None = None
    proceeding_reference: str | None = None
    preparatory_actions: str | None = None
    processing_operations: str | None = None
    necessity_analysis: str | None = None
    data_minimization_analysis: str | None = None
    related_to_right: ContractResponseV1 | None = None
    necessary_for_route: ContractResponseV1 | None = None
    within_forum_scope: ContractResponseV1 | None = None
    post_proceeding_necessity_analysis: str | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


class EconomicObligationsAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    route: Literal["sin_comunicacion", "con_comunicacion"] | None = None
    obligation_type: (
        Literal["economica", "financiera", "bancaria", "comercial"] | None
    ) = None
    purpose_description: str | None = None
    obligation_description: str | None = None
    obligation_reference: str | None = None
    holder_connection_analysis: str | None = None
    processing_operations: str | None = None
    applicability_analysis: str | None = None
    data_minimization_analysis: str | None = None
    title_iii_analysis: str | None = None
    retention_and_deletion_analysis: str | None = None
    accuracy_and_update_analysis: str | None = None
    normative_references: list[NormativeReferenceV1] = Field(default_factory=list)
    operations_include_communication: ContractResponseV1 | None = None
    related_to_obligation: ContractResponseV1 | None = None
    title_iii_reviewed: ContractResponseV1 | None = None
    processing_within_title_iii: ContractResponseV1 | None = None
    retention_and_deletion_compatible: ContractResponseV1 | None = None
    accuracy_controls_documented: ContractResponseV1 | None = None
    communication_scope: str | None = None
    communication_eligibility_analysis: str | None = None
    communication_restrictions_analysis: str | None = None
    payment_and_extinction_controls: str | None = None
    communication_permitted: ContractResponseV1 | None = None
    excluded_data_screened: ContractResponseV1 | None = None
    communication_limits_respected: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


# ── Screening EIPD v1 ─────────────────────────────────────────────────────────

EipdQuestionIdV1 = Literal[
    "evaluacion_sistematica_automatizada_efectos_significativos",
    "tratamiento_masivo_o_gran_escala",
    "monitoreo_sistematico_zona_publica",
    "datos_protegidos_excepcion_consentimiento",
    "probable_alto_riesgo_contextual",
]


class EipdDeclarationV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: EipdQuestionIdV1
    answer: Literal["si", "no", "pendiente"]
    rationale: str | None = None


class EipdContextBindingV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class EipdContextBindingV2(EipdContextBindingV1):
    schema_version: Literal[2] = 2


class EipdContextBindingV3(EipdContextBindingV1):
    schema_version: Literal[3] = 3


class EipdContextBindingV4(EipdContextBindingV1):
    schema_version: Literal[4] = 4


class EipdContextBindingV5(EipdContextBindingV1):
    schema_version: Literal[5] = 5


class EipdContextBindingV6(EipdContextBindingV1):
    schema_version: Literal[6] = 6


class EipdContextBindingV7(EipdContextBindingV1):
    schema_version: Literal[7] = 7


class EipdContextBindingV8(EipdContextBindingV1):
    schema_version: Literal[8] = 8


class EipdContextBindingV9(EipdContextBindingV1):
    schema_version: Literal[9] = 9


class EipdContextBindingV10(EipdContextBindingV1):
    schema_version: Literal[10] = 10


class EipdContextBindingV11(EipdContextBindingV1):
    schema_version: Literal[11] = 11


class EipdScreeningDraftIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    answers: list[EipdDeclarationV1] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def validar_declaraciones_unicas(self):
        ids = [item.question_id for item in self.answers]
        if len(ids) != len(set(ids)):
            raise ValueError("answers no admite question_id duplicados")
        return self


class EipdScreeningV1(EipdScreeningDraftIn):
    context_binding: (
        EipdContextBindingV1
        | EipdContextBindingV2
        | EipdContextBindingV3
        | EipdContextBindingV4
        | EipdContextBindingV5
        | EipdContextBindingV6
        | EipdContextBindingV7
        | EipdContextBindingV8
        | EipdContextBindingV9
        | EipdContextBindingV10
        | EipdContextBindingV11
    )


# ── Detección y expediente de condiciones especiales v1 ────────────────────────

SpecialQuestionIdV1 = Literal[
    "datos_sensibles",
    "salud_perfil_biologico",
    "biometricos_identificacion_unica",
    "ninos_ninas",
    "adolescentes",
    "datos_sensibles_adolescentes_menores_16",
    "fines_historicos_estadisticos_cientificos_investigacion",
    "geolocalizacion",
    "grupos_vulnerables",
]
SpecialRegimeIdV1 = Literal[
    "sensibles_art16",
    "salud_perfil_biologico_art16bis",
    "biometricos_art16ter",
    "infancia_adolescencia_art16quater",
    "investigacion_art16quinquies",
    "geolocalizacion_art16sexies",
]
SensitiveConditionIdV1 = Literal[
    "consentimiento_expreso_art16",
    "datos_manifiestamente_publicos_art16a",
    "interes_legitimo_entidad_sin_fines_lucro_art16b",
    "vida_salud_integridad_impedimento_art16c",
    "defensa_derechos_art16d",
    "laboral_seguridad_social_art16e",
    "autorizacion_legal_art16f",
]


class SpecialScopeV1(LegalAssessmentScopeIn):
    model_config = ConfigDict(extra="forbid")


# Resolucion EIPD: contratos documentales; sin persistencia ni habilitacion de gates.


class EipdRiskV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    risk_id: str | None = None
    description: str | None = None
    impact_analysis: str | None = None
    initial_assessment_analysis: str | None = None
    residual_assessment_analysis: str | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)


class EipdMeasureV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    measure_id: str | None = None
    description: str | None = None
    effectiveness_analysis: str | None = None
    implementation_analysis: str | None = None
    risk_ids: list[str] = Field(default_factory=list)
    implemented: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)


class EipdOfficialSourceV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_reference: str | None = None
    publication_version: str | None = None
    review_analysis: str | None = None
    applicability: Literal["aplicable", "no_aplicable", "pendiente"] | None = None


class EipdOfficialSourcesV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["identificado", "no_identificado", "pendiente"] | None = None
    checked_on: date | None = None
    sources: list[EipdOfficialSourceV1] = Field(default_factory=list)
    applicability_analysis: str | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)


class EipdAgencyConsultationV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["no_solicitada", "en_curso", "concluida"] | None = None
    analysis: str | None = None
    consultation_reference: str | None = None
    response_reference: str | None = None
    recommendations_analysis: str | None = None
    reassessment_analysis: str | None = None
    recommendations_addressed: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)


class EipdResolutionAssessmentV1(BaseModel):
    """Entrada editable parcial; metadata del servidor expresamente excluida."""

    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    document_reference: str | None = None
    document_version: str | None = None
    report_reference: str | None = None
    prepared_by: str | None = None
    completed_on: date | None = None
    purpose_description: str | None = None
    processing_operations: str | None = None
    processing_context: str | None = None
    technologies_description: str | None = None
    exceptions_coverage_analysis: str | None = None
    scope: SpecialScopeV1 | None = None
    necessity_analysis: str | None = None
    proportionality_analysis: str | None = None
    minimization_analysis: str | None = None
    necessary_for_purpose: ContractResponseV1 | None = None
    proportionate_processing: ContractResponseV1 | None = None
    minimization_addressed: ContractResponseV1 | None = None
    performed_before_processing: ContractResponseV1 | None = None
    prior_assessment_analysis: str | None = None
    risks: list[EipdRiskV1] = Field(default_factory=list)
    measures: list[EipdMeasureV1] = Field(default_factory=list)
    residual_risk_summary: str | None = None
    residual_risk_rationale: str | None = None
    limitations_analysis: str | None = None
    follow_up_plan: str | None = None
    residual_risk_level: Literal["no_alto", "alto", "sin_resolver"] | None = None
    official_sources: EipdOfficialSourcesV1 | None = None
    agency_consultation: EipdAgencyConsultationV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


class EipdResolutionContextBindingV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    binding_version: Literal[1] = 1
    context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class EipdResolutionAssessmentStoredV1(EipdResolutionAssessmentV1):
    """Forma documental interna/salida; nunca usar como entrada editable."""

    context_binding: EipdResolutionContextBindingV1 | None = None


EipdResolutionReviewDecision = Literal["continuar", "requiere_cambios", "no_continuar"]


class EipdResolutionReviewIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: EipdResolutionReviewDecision
    rationale: str
    review_reference: str

    @model_validator(mode="after")
    def validar_revision_fundada(self):
        if not self.rationale.strip() or not self.review_reference.strip():
            raise ValueError("La revision exige fundamento y referencia no vacios")
        return self


class EipdResolutionReviewOut(EipdResolutionReviewIn):
    id: uuid.UUID
    organization_id: uuid.UUID
    assessment_id: uuid.UUID
    document_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    created_by: uuid.UUID
    created_at: datetime

    @model_validator(mode="after")
    def validar_fecha_servidor_utc(self):
        if (
            self.created_at.utcoffset() is None
            or self.created_at.utcoffset().total_seconds() != 0
        ):
            raise ValueError("created_at exige fecha UTC con zona horaria")
        return self


class EipdResolutionReviewWithPolicyOut(EipdResolutionReviewOut):
    """Lectura futura de servidor; historicos mantienen identidad nullable."""

    policy_version: int | None = Field(default=None, strict=True, ge=1, le=1)
    policy_reference: str | None = None
    policy_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validar_identidad_politica(self):
        values = (self.policy_version, self.policy_reference, self.policy_hash)
        if any(value is not None for value in values):
            if (
                any(value is None for value in values)
                or not self.policy_reference.strip()
            ):
                raise ValueError(
                    "Identidad de politica exige version, referencia y hash"
                )
        return self


class EipdResolutionReviewStateOut(BaseModel):
    """Estado derivado de lectura; no evalua ni autoriza confirmacion."""

    model_config = ConfigDict(extra="forbid")
    review_status: Literal["sin_revision", "vigente", "obsoleta"]
    latest_review: EipdResolutionReviewOut | None


HealthCollectionContextV1 = Literal[
    "laboral",
    "educativo",
    "deportivo",
    "social",
    "seguros",
    "seguridad",
    "identificacion",
    "otro",
]


class HealthLegalReferenceV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    norm_name: str | None = None
    provision: str | None = None
    official_source_url: HttpUrl | None = None
    applicability_analysis: str | None = None


class BiometricSystemV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system_reference: str | None = None
    system_name: str | None = None
    system_description: str | None = None
    specific_purpose: str | None = None
    purpose_alignment_analysis: str | None = None
    use_period_description: str | None = None
    retention_alignment_analysis: str | None = None
    rights_exercise_description: str | None = None
    rights_contact_channel: str | None = None
    information_reference: str | None = None
    system_identification_disclosed: ContractResponseV1 | None = None
    purpose_disclosed: ContractResponseV1 | None = None
    use_period_disclosed: ContractResponseV1 | None = None
    rights_exercise_disclosed: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)


class BiometricAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    purpose_description: str | None = None
    biometric_data_description: str | None = None
    processing_operations: str | None = None
    scope: SpecialScopeV1 | None = None
    route: Literal["consentimiento_expreso"] | None = None
    unique_identification_analysis: str | None = None
    unique_identification_confirmed: ContractResponseV1 | None = None
    systems: list[BiometricSystemV1] = Field(default_factory=list)
    systems_coverage_analysis: str | None = None
    all_systems_documented: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


class RightsExceptionContextV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    context_reference: str | None = None
    purpose_description: str | None = None
    route: (
        Literal["formulacion_derecho", "ejercicio_derecho", "defensa_derecho"] | None
    ) = None
    right_description: str | None = None
    right_basis_reference: str | None = None
    right_holder: Literal["responsable", "tercero", "ambos"] | None = None
    holder_connection_analysis: str | None = None
    forum_type: Literal["tribunal_justicia", "organo_administrativo"] | None = None
    forum_description: str | None = None
    proceeding_stage: Literal["preparacion", "en_curso", "finalizado"] | None = None
    proceeding_reference: str | None = None
    preparatory_actions: str | None = None
    processing_operations: str | None = None
    necessity_analysis: str | None = None
    data_minimization_analysis: str | None = None
    safeguards_analysis: str | None = None
    related_to_right: ContractResponseV1 | None = None
    necessary_for_route: ContractResponseV1 | None = None
    within_forum_scope: ContractResponseV1 | None = None
    principles_addressed: ContractResponseV1 | None = None
    post_proceeding_necessity_analysis: str | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)


class SensitiveRightsExceptionAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    exception_basis: Literal["defensa_derechos_art16d"] | None = None
    context: RightsExceptionContextV1 | None = None
    sensitive_data_description: str | None = None
    scope: SpecialScopeV1 | None = None
    exception_application_analysis: str | None = None
    exception_conditions_met: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


class BiometricRightsExceptionAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    exception_basis: Literal["defensa_derechos_art16bis_d"] | None = None
    context: RightsExceptionContextV1 | None = None
    biometric_data_description: str | None = None
    scope: SpecialScopeV1 | None = None
    unique_identification_analysis: str | None = None
    unique_identification_confirmed: ContractResponseV1 | None = None
    exception_application_analysis: str | None = None
    exception_conditions_met: ContractResponseV1 | None = None
    sensitive_context_connection_analysis: str | None = None
    systems: list[BiometricSystemV1] = Field(default_factory=list)
    systems_coverage_analysis: str | None = None
    all_systems_documented: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


class HealthAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    purpose_description: str | None = None
    health_data_description: str | None = None
    processing_operations: str | None = None
    scope: SpecialScopeV1 | None = None
    route: Literal["consentimiento_expreso"] | None = None
    sanitary_law_references: list[HealthLegalReferenceV1] = Field(default_factory=list)
    sanitary_purpose_analysis: str | None = None
    sanitary_purpose_covered: ContractResponseV1 | None = None
    collection_contexts: list[HealthCollectionContextV1] = Field(default_factory=list)
    collection_context_analysis: str | None = None
    restricted_context_legal_references: list[HealthLegalReferenceV1] = Field(
        default_factory=list
    )
    restricted_context_analysis: str | None = None
    restricted_context_authorization_documented: ContractResponseV1 | None = None
    includes_data_cession: ContractResponseV1 | None = None
    cession_description: str | None = None
    includes_identifiable_biological_samples: ContractResponseV1 | None = None
    biological_samples_analysis: str | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def validar_contextos_unicos(self):
        if len(self.collection_contexts) != len(set(self.collection_contexts)):
            raise ValueError("collection_contexts no admite contextos duplicados")
        return self


class SensitiveConsentAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    purpose_description: str | None = None
    sensitive_data_description: str | None = None
    processing_operations: str | None = None
    scope: SpecialScopeV1 | None = None
    expression_method: (
        Literal["escrito", "verbal", "tecnologico_equivalente"] | None
    ) = None
    declaration_reference: str | None = None
    declaration_version_reference: str | None = None
    declaration_obtained_on: date | None = None
    declaration_content_analysis: str | None = None
    express_declaration_documented: ContractResponseV1 | None = None
    sensitive_scope_explicit: ContractResponseV1 | None = None
    purpose_specific: ContractResponseV1 | None = None
    proof_available: ContractResponseV1 | None = None
    consent_current: ContractResponseV1 | None = None
    technology_equivalence_analysis: str | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


class GeolocationAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    purpose_description: str | None = None
    geolocation_data_description: str | None = None
    processing_operations: str | None = None
    duration_description: str | None = None
    scope: SpecialScopeV1 | None = None
    notice_reference: str | None = None
    notice_version_reference: str | None = None
    notice_delivery_mechanism: str | None = None
    notice_provided_on: date | None = None
    notice_content_analysis: str | None = None
    information_clear: ContractResponseV1 | None = None
    information_sufficient: ContractResponseV1 | None = None
    information_timely: ContractResponseV1 | None = None
    data_types_disclosed: ContractResponseV1 | None = None
    purpose_disclosed: ContractResponseV1 | None = None
    duration_disclosed: ContractResponseV1 | None = None
    third_party_information_disclosed: ContractResponseV1 | None = None
    value_added_third_party_transfer: ContractResponseV1 | None = None
    third_party_disclosure_description: str | None = None
    value_added_service_description: str | None = None
    third_party_recipient_description: str | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    notes: str | None = None


class SpecialDeclarationV1(SpecialScopeV1):
    question_id: SpecialQuestionIdV1
    answer: Literal["si", "no", "pendiente"]
    rationale: str | None = None


class SpecialEvidenceV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_type: str
    reference: str | None = None
    obtained_on: date | None = None
    mechanism: str | None = None
    notes: str | None = None


class SpecialConditionV1(SpecialScopeV1):
    regime_id: SpecialRegimeIdV1
    authorization_route: (
        Literal["consentimiento", "excepcion_legal", "regla_especifica"] | None
    ) = None
    sensitive_condition_id: SensitiveConditionIdV1 | None = None
    legal_reference: str | None = None
    documentary_analysis: str | None = None
    uses_consent_assessment: bool | None = None
    evidence: list[SpecialEvidenceV1] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def validar_catalogo_sensible(self):
        if (
            self.sensitive_condition_id is not None
            and self.regime_id != "sensibles_art16"
        ):
            raise ValueError("sensitive_condition_id solo se admite en sensibles_art16")
        return self


class SpecialContextBindingV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class SpecialContextBindingV2(SpecialContextBindingV1):
    schema_version: Literal[2] = 2


class SpecialContextBindingV3(SpecialContextBindingV1):
    schema_version: Literal[3] = 3


class SpecialContextBindingV4(SpecialContextBindingV1):
    schema_version: Literal[4] = 4


class SpecialContextBindingV5(SpecialContextBindingV1):
    schema_version: Literal[5] = 5


class SpecialContextBindingV6(SpecialContextBindingV1):
    schema_version: Literal[6] = 6


class SpecialContextBindingV7(SpecialContextBindingV1):
    schema_version: Literal[7] = 7


class SpecialContextBindingV8(SpecialContextBindingV1):
    schema_version: Literal[8] = 8


class SpecialContextBindingV9(SpecialContextBindingV1):
    schema_version: Literal[9] = 9


class SpecialContextBindingV10(SpecialContextBindingV1):
    schema_version: Literal[10] = 10


class SpecialConditionsDraftIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    declarations: list[SpecialDeclarationV1] = Field(default_factory=list)
    conditions: list[SpecialConditionV1] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def validar_identificadores_unicos(self):
        questions = [item.question_id for item in self.declarations]
        regimes = [item.regime_id for item in self.conditions]
        if len(questions) != len(set(questions)):
            raise ValueError("declarations no admite question_id duplicados")
        if len(regimes) != len(set(regimes)):
            raise ValueError("conditions no admite regime_id duplicados")
        return self


class SpecialConditionsV1(SpecialConditionsDraftIn):
    context_binding: (
        SpecialContextBindingV1
        | SpecialContextBindingV2
        | SpecialContextBindingV3
        | SpecialContextBindingV4
        | SpecialContextBindingV5
        | SpecialContextBindingV6
        | SpecialContextBindingV7
        | SpecialContextBindingV8
        | SpecialContextBindingV9
        | SpecialContextBindingV10
    )


class ResearchAssessmentV1(LegalAssessmentScopeIn):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    schema_version: Literal[1] = 1
    purpose_type: (
        Literal["historico", "estadistico", "cientifico", "estudio_investigacion"]
        | None
    ) = None
    purpose_description: str | None = None
    public_interest_analysis: str | None = None
    exclusive_use: ContractResponseV1 | None = None
    exclusivity_controls_analysis: str | None = None
    quality_measures_analysis: str | None = None
    security_measures_analysis: str | None = None
    measures_implemented: ContractResponseV1 | None = None
    evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    publication_planned: ContractResponseV1 | None = None
    anonymization_method: str | None = None
    anonymization_analysis: str | None = None
    anonymization_evidence: list[ContractEvidenceV1] = Field(default_factory=list)
    retention_analysis: str | None = None


class ResearchContextBindingV1(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, revalidate_instances="always"
    )
    schema_version: Literal[1] = 1
    context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    document_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class BoundResearchAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    assessment: ResearchAssessmentV1
    context_binding: ResearchContextBindingV1


class LegalAssessmentDraftCreate(BaseModel):
    """Entrada para crear una nueva versión en estado borrador."""

    purpose_id: uuid.UUID
    scope: LegalAssessmentScopeIn
    legal_basis: LegalBasis | None = None
    justification: str | None = None
    consent_assessment: ConsentAssessmentV1 | None = None
    lia_assessment: LiaAssessmentV1 | None = None
    research_assessment: ResearchAssessmentV1 | None = None
    geolocation_assessment: GeolocationAssessmentV1 | None = None
    sensitive_consent_assessment: SensitiveConsentAssessmentV1 | None = None
    health_assessment: HealthAssessmentV1 | None = None
    sensitive_rights_exception_assessment: (
        SensitiveRightsExceptionAssessmentV1 | None
    ) = None
    biometric_rights_exception_assessment: (
        BiometricRightsExceptionAssessmentV1 | None
    ) = None
    biometric_assessment: BiometricAssessmentV1 | None = None
    economic_obligations_assessment: EconomicObligationsAssessmentV1 | None = None
    rights_defense_assessment: RightsDefenseAssessmentV1 | None = None
    legal_obligation_assessment: LegalObligationAssessmentV1 | None = None
    contract_assessment: ContractAssessmentV1 | None = None
    eipd_resolution_assessment: EipdResolutionAssessmentV1 | None = None
    eipd_screening: EipdScreeningDraftIn | None = None
    special_conditions: SpecialConditionsDraftIn | None = None


class LegalAssessmentDraftUpdate(BaseModel):
    """Actualización parcial de un borrador existente."""

    scope: LegalAssessmentScopeIn | None = None
    legal_basis: LegalBasis | None = None
    justification: str | None = None
    consent_assessment: ConsentAssessmentV1 | None = None
    lia_assessment: LiaAssessmentV1 | None = None
    research_assessment: ResearchAssessmentV1 | None = None
    geolocation_assessment: GeolocationAssessmentV1 | None = None
    sensitive_consent_assessment: SensitiveConsentAssessmentV1 | None = None
    health_assessment: HealthAssessmentV1 | None = None
    sensitive_rights_exception_assessment: (
        SensitiveRightsExceptionAssessmentV1 | None
    ) = None
    biometric_rights_exception_assessment: (
        BiometricRightsExceptionAssessmentV1 | None
    ) = None
    biometric_assessment: BiometricAssessmentV1 | None = None
    economic_obligations_assessment: EconomicObligationsAssessmentV1 | None = None
    rights_defense_assessment: RightsDefenseAssessmentV1 | None = None
    legal_obligation_assessment: LegalObligationAssessmentV1 | None = None
    contract_assessment: ContractAssessmentV1 | None = None
    eipd_resolution_assessment: EipdResolutionAssessmentV1 | None = None
    eipd_screening: EipdScreeningDraftIn | None = None
    special_conditions: SpecialConditionsDraftIn | None = None

    @model_validator(mode="after")
    def validar_scope_null_explicito(self):
        if "scope" in self.model_fields_set and self.scope is None:
            raise ValueError("scope no puede ser null")
        return self


# ── Contexto RAT canónico v1 ─────────────────────────────────────────────────


class RatCanonicalDataCategoryV1(BaseModel):
    category_code: str
    category_name: str
    is_sensitive: bool


class RatCanonicalDataSubjectV1(BaseModel):
    category_code: str
    category_name: str
    includes_children: bool
    includes_adolescents: bool
    is_vulnerable_group: bool


class RatCanonicalDataSourceV1(BaseModel):
    source_type: Literal[
        "titular",
        "tercero",
        "fuente_publica",
        "recogida_automatica",
        "otro",
    ]
    description: str | None
    is_public_source: bool


class RatCanonicalRetentionV1(BaseModel):
    retention_rule: str | None


class RatCanonicalAutomatedDecisionsV1(BaseModel):
    has_automated_decisions: bool
    description: str | None


class RatCanonicalThirdPartyV1(BaseModel):
    relationship_type: Literal[
        "encargado",
        "cesionario",
        "otro",
    ]
    has_data_access: bool
    country: str | None
    has_subprocessors: bool
    purpose: str | None


class RatCanonicalInternationalTransferV1(BaseModel):
    destination_country: str
    adequacy_status: Literal[
        "adecuado",
        "no_adecuado",
        "pendiente",
        "no_determinado",
    ]
    mechanism: str | None
    guarantees_description: str | None


class RatCanonicalSpecialRegimesV1(BaseModel):
    has_sensitive_data: bool
    includes_children: bool
    includes_adolescents: bool
    has_vulnerable_groups: bool


class RatCanonicalContextV1(BaseModel):
    purpose: str
    organization_role: Literal["responsable", "encargado"] | None
    data_categories: list[RatCanonicalDataCategoryV1]
    data_subjects: list[RatCanonicalDataSubjectV1]
    data_sources: list[RatCanonicalDataSourceV1]
    retention: RatCanonicalRetentionV1
    automated_decisions: RatCanonicalAutomatedDecisionsV1
    systems: list[dict] = Field(default_factory=list, max_length=0)
    third_parties: list[RatCanonicalThirdPartyV1]
    international_transfers: list[RatCanonicalInternationalTransferV1]
    special_regimes: RatCanonicalSpecialRegimesV1


# ── Snapshot documental RAT v1 ────────────────────────────────────────────────


class RatSnapshotDataCategoryV1(BaseModel):
    category_code: str
    category_name: str
    is_sensitive: bool
    notes: str | None


class RatSnapshotDataSubjectV1(BaseModel):
    category_code: str
    category_name: str
    includes_children: bool
    includes_adolescents: bool
    is_vulnerable_group: bool
    notes: str | None


class RatSnapshotDataSourceV1(BaseModel):
    source_type: Literal[
        "titular",
        "tercero",
        "fuente_publica",
        "recogida_automatica",
        "otro",
    ]
    description: str | None
    is_public_source: bool


class RatSnapshotRetentionV1(BaseModel):
    retention_rule: str | None
    deletion_method: str | None


class RatSnapshotAutomatedDecisionsV1(BaseModel):
    has_automated_decisions: bool
    description: str | None


class RatSnapshotSystemV1(BaseModel):
    name: str
    provider: str | None
    hosting_location: str | None
    hosting_country: str | None
    is_international: bool


class RatSnapshotThirdPartyV1(BaseModel):
    vendor_name: str
    country: str | None
    relationship_type: Literal[
        "encargado",
        "cesionario",
        "otro",
    ]
    purpose: str | None
    has_data_access: bool
    has_contract: bool
    contract_reference: str | None
    engagement_object: str | None
    engagement_duration: str | None
    has_subprocessors: bool
    notes: str | None


class RatSnapshotInternationalTransferV1(BaseModel):
    recipient_name: str | None
    destination_country: str
    adequacy_status: Literal[
        "adecuado",
        "no_adecuado",
        "pendiente",
        "no_determinado",
    ]
    mechanism: str | None
    guarantees_description: str | None
    evidence_reference: str | None


class RatSnapshotSpecialRegimesV1(BaseModel):
    has_sensitive_data: bool
    includes_children: bool
    includes_adolescents: bool
    has_vulnerable_groups: bool


class RatContextSnapshotV1(BaseModel):
    purpose: str
    organization_role: Literal["responsable", "encargado"] | None
    data_categories: list[RatSnapshotDataCategoryV1]
    data_subjects: list[RatSnapshotDataSubjectV1]
    data_sources: list[RatSnapshotDataSourceV1]
    retention: RatSnapshotRetentionV1
    automated_decisions: RatSnapshotAutomatedDecisionsV1
    systems: list[RatSnapshotSystemV1]
    third_parties: list[RatSnapshotThirdPartyV1]
    international_transfers: list[RatSnapshotInternationalTransferV1]
    special_regimes: RatSnapshotSpecialRegimesV1


class LegalAssessmentOut(BaseModel):
    """Expediente de una versión M3, incluidas las versiones históricas."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    treatment_id: uuid.UUID
    series_id: uuid.UUID
    version: int
    status: LegalAssessmentStatus
    legal_basis: LegalBasis | None
    justification: str | None
    purpose_snapshot: str
    rat_context_hash: str
    rat_context_snapshot: dict
    consent_assessment: ConsentAssessmentV1 | None
    lia_assessment: LiaAssessmentV1 | None
    research_assessment: BoundResearchAssessmentV1 | None = None
    special_conditions: SpecialConditionsV1 | None
    contract_assessment: ContractAssessmentV1 | None
    legal_obligation_assessment: LegalObligationAssessmentV1 | None
    geolocation_assessment: GeolocationAssessmentV1 | None
    sensitive_consent_assessment: SensitiveConsentAssessmentV1 | None
    health_assessment: HealthAssessmentV1 | None
    sensitive_rights_exception_assessment: SensitiveRightsExceptionAssessmentV1 | None
    biometric_rights_exception_assessment: BiometricRightsExceptionAssessmentV1 | None
    biometric_assessment: BiometricAssessmentV1 | None
    economic_obligations_assessment: EconomicObligationsAssessmentV1 | None
    rights_defense_assessment: RightsDefenseAssessmentV1 | None
    eipd_resolution_assessment: EipdResolutionAssessmentStoredV1 | None = None
    eipd_screening: EipdScreeningV1 | None
    schema_version: int
    rat_context_schema_version: int
    confirmed_at: datetime | None
    confirmed_by: uuid.UUID | None
    replaced_at: datetime | None
    replaced_by_assessment_id: uuid.UUID | None


class ReadinessIssueOut(BaseModel):
    field: str
    code: str
    category: Literal[
        "incompleto", "requiere_revision", "pendiente_revision", "supuesto_declarado"
    ]
    question_id: str | None = None


class ReadinessApplicabilityOut(BaseModel):
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


class DocumentaryReadinessOut(BaseModel):
    result: Literal["completo", "requiere_revision", "incompleto"]
    issues: list[ReadinessIssueOut]
    applicability: list[ReadinessApplicabilityOut]


class EipdResolutionDocumentReadinessOut(DocumentaryReadinessOut):
    """Preparacion documental aislada de revision y frontera de confirmacion."""

    model_config = ConfigDict(extra="forbid")
    context_current: bool


class EipdObservationOut(BaseModel):
    field: str
    code: Literal["valoracion_lia_alta"]


class EipdReadinessOut(BaseModel):
    result: Literal["requiere_eipd", "pendiente_revision", "sin_supuestos_declarados"]
    context_current: bool
    issues: list[ReadinessIssueOut]
    observations: list[EipdObservationOut]


class SpecialReadinessOut(BaseModel):
    result: Literal[
        "incompleto",
        "requiere_revision",
        "sin_regimenes_declarados",
        "regimenes_preparados",
    ]
    context_current: bool
    detected_regimes: list[SpecialRegimeIdV1]
    issues: list[ReadinessIssueOut]


class EipdFrontierReadinessOut(BaseModel):
    """Preparacion acotada, separada de permiso de confirmar."""

    model_config = ConfigDict(extra="forbid")
    result: Literal["incompleto", "requiere_revision", "preparado"]
    route: Literal["sensible_derechos", "sensible_biometrica_derechos", "sin_resolver"]
    issues: list[ReadinessIssueOut]
    applicability: list[ReadinessApplicabilityOut]
    special: SpecialReadinessOut | None
    screening: EipdReadinessOut | None


class EipdReadinessV2Out(EipdReadinessOut):
    """Deteccion versionada; exige EIPD aunque la frontera este preparada."""

    model_config = ConfigDict(extra="forbid")
    evaluation_version: Literal[2]
    frontier: EipdFrontierReadinessOut


class EipdCompositionIssueOut(ReadinessIssueOut):
    model_config = ConfigDict(extra="forbid")
    stage: Literal[
        "state",
        "rat",
        "ordinary",
        "frontier",
        "detection",
        "resolution",
        "sources",
        "activation",
        "review",
    ]


class EipdOrdinaryControlOut(DocumentaryReadinessOut):
    model_config = ConfigDict(extra="forbid")
    legal_basis: LegalBasis


class EipdControlCompositionOut(BaseModel):
    """Diagnostico por etapas; no habilita revision ni confirmacion."""

    model_config = ConfigDict(extra="forbid")
    evaluation_version: Literal[1]
    preparation_result: Literal["preparado", "incompleto", "requiere_revision"]
    ordinary: EipdOrdinaryControlOut | None
    detection_v2: EipdReadinessV2Out
    resolution: EipdResolutionDocumentReadinessOut
    review_state: EipdResolutionReviewStateOut
    preparation_issues: list[EipdCompositionIssueOut]
    review_blockers: list[EipdCompositionIssueOut]
    confirmation_blockers: list[EipdCompositionIssueOut]


class EipdPolicyIssueOut(ReadinessIssueOut):
    model_config = ConfigDict(extra="forbid")
    stage: Literal["sources", "activation"]


class EipdPolicyReadinessOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_version: int | None = Field(strict=True, ge=1, le=1)
    policy_reference: str | None
    policy_hash: str | None = Field(pattern=r"^[0-9a-f]{64}$")
    routes: list[Literal["sensible_derechos", "sensible_biometrica_derechos"]]
    sources_status: Literal["pendiente", "verificadas"]
    acceptance_status: Literal["pendiente", "aceptada"]
    activation: Literal["deshabilitada", "habilitada"]
    issues: list[EipdPolicyIssueOut]

    @model_validator(mode="after")
    def validar_snapshot_politica(self):
        identity = (self.policy_version, self.policy_reference, self.policy_hash)
        if any(value is not None for value in identity):
            if (
                any(value is None for value in identity)
                or not self.policy_reference.strip()
            ):
                raise ValueError("Snapshot exige identidad de politica completa")
        elif (
            self.routes
            or self.sources_status != "pendiente"
            or self.acceptance_status != "pendiente"
            or self.activation != "deshabilitada"
        ):
            raise ValueError("Politica ausente no acredita fuentes ni activacion")
        if len(set(self.routes)) != len(self.routes):
            raise ValueError("Rutas duplicadas")
        if self.activation == "habilitada" and (
            self.sources_status != "verificadas"
            or self.acceptance_status != "aceptada"
            or not self.routes
        ):
            raise ValueError("Activacion incoherente")
        return self


class EipdReviewPolicyIdentityOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    review_id: uuid.UUID
    policy_version: int = Field(strict=True, ge=1, le=1)
    policy_reference: str = Field(min_length=1)
    policy_hash: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validar_referencia_politica(self):
        if not self.policy_reference.strip():
            raise ValueError("Referencia de politica vacia")
        return self


class EipdControlCompositionV2Out(EipdControlCompositionOut):
    evaluation_version: Literal[2]
    policy: EipdPolicyReadinessOut
    review_policy_status: Literal[
        "sin_revision", "sin_identidad", "vigente", "obsoleta"
    ]
    latest_review_policy: EipdReviewPolicyIdentityOut | None


class ConfirmationBlockerOut(BaseModel):
    field: str
    code: str
    message: str


class LegalAssessmentReadinessOut(BaseModel):
    """Lectura orientativa: no autoriza ni modifica la evaluación."""

    assessment_id: uuid.UUID
    status: LegalAssessmentStatus
    legal_basis: LegalBasis | None
    rat_context_current: bool | None
    consent: DocumentaryReadinessOut | None
    lia: DocumentaryReadinessOut | None
    contract: DocumentaryReadinessOut | None
    legal_obligation: DocumentaryReadinessOut | None
    health: DocumentaryReadinessOut | None
    biometric: DocumentaryReadinessOut | None
    biometric_rights_exception: DocumentaryReadinessOut | None
    sensitive_consent: DocumentaryReadinessOut | None
    sensitive_rights_exception: DocumentaryReadinessOut | None
    geolocation: DocumentaryReadinessOut | None
    economic_obligations: DocumentaryReadinessOut | None
    rights_defense: DocumentaryReadinessOut | None
    eipd_resolution: EipdResolutionDocumentReadinessOut | None = None
    eipd_resolution_review: EipdResolutionReviewStateOut = Field(
        default_factory=lambda: EipdResolutionReviewStateOut(
            review_status="sin_revision", latest_review=None
        )
    )
    eipd: EipdReadinessOut
    eipd_v2: EipdReadinessV2Out | None = None
    eipd_controls: EipdControlCompositionOut | None = None
    eipd_controls_v2: EipdControlCompositionV2Out | None = None
    special: SpecialReadinessOut
    confirmation_blockers: list[ConfirmationBlockerOut]
    pending_controls: list[str]
