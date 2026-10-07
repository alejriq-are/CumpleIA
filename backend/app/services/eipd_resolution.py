"""Asociacion y hash documental de resolucion EIPD; funciones puras sin gates."""

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.licitud import (
    BiometricAssessmentV1,
    BiometricRightsExceptionAssessmentV1,
    ConsentAssessmentV1,
    ContractAssessmentV1,
    EconomicObligationsAssessmentV1,
    EipdAgencyConsultationV1,
    EipdOfficialSourcesV1,
    EipdResolutionAssessmentStoredV1,
    EipdResolutionAssessmentV1,
    EipdResolutionReviewIn,
    EipdResolutionReviewOut,
    EipdResolutionReviewStateOut,
    EipdScreeningV1,
    GeolocationAssessmentV1,
    HealthAssessmentV1,
    LegalBasis,
    LegalObligationAssessmentV1,
    LiaAssessmentV1,
    RatContextSnapshotV1,
    RightsDefenseAssessmentV1,
    SensitiveConsentAssessmentV1,
    SensitiveRightsExceptionAssessmentV1,
    SpecialConditionsV1,
)


class EipdResolutionContextV1(BaseModel):
    """Material interno final: cada entrada debe aportarse, incluso si es null.

    No incluye la resolucion ni eventos. No es un contrato de entrada HTTP.
    """

    model_config = ConfigDict(extra="forbid")
    rat_context_snapshot: RatContextSnapshotV1
    legal_basis: LegalBasis | None
    consent_assessment: ConsentAssessmentV1 | None
    lia_assessment: LiaAssessmentV1 | None
    contract_assessment: ContractAssessmentV1 | None
    legal_obligation_assessment: LegalObligationAssessmentV1 | None
    rights_defense_assessment: RightsDefenseAssessmentV1 | None
    economic_obligations_assessment: EconomicObligationsAssessmentV1 | None
    geolocation_assessment: GeolocationAssessmentV1 | None
    sensitive_consent_assessment: SensitiveConsentAssessmentV1 | None
    health_assessment: HealthAssessmentV1 | None
    biometric_assessment: BiometricAssessmentV1 | None
    sensitive_rights_exception_assessment: SensitiveRightsExceptionAssessmentV1 | None
    biometric_rights_exception_assessment: BiometricRightsExceptionAssessmentV1 | None
    special_conditions: SpecialConditionsV1 | None
    eipd_screening: EipdScreeningV1 | None


def _validated_json(model, value):
    # Revalidar tambien instancias modificadas despues de su construccion.
    return model.model_validate(
        value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    ).model_dump(mode="json")


def _hash(material):
    serialized = json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_eipd_resolution_context_hash_v1(
    context: EipdResolutionContextV1 | dict,
) -> str:
    """Hash del snapshot completo y todos los documentos finales validados."""
    return _hash(
        {
            "binding_version": 1,
            "context": _validated_json(EipdResolutionContextV1, context),
        }
    )


def bind_eipd_resolution_v1(
    document: EipdResolutionAssessmentV1 | dict,
    context: EipdResolutionContextV1 | dict,
) -> EipdResolutionAssessmentStoredV1:
    """Asociacion explicita de entrada editable; no conserva decision humana."""
    material = _validated_json(EipdResolutionAssessmentV1, document)
    material["context_binding"] = {
        "binding_version": 1,
        "context_hash": build_eipd_resolution_context_hash_v1(context),
    }
    return EipdResolutionAssessmentStoredV1.model_validate(material)


def build_eipd_resolution_document_hash_v1(
    document: EipdResolutionAssessmentStoredV1 | dict,
) -> str:
    """Incluye contenido y binding; excluye eventos y estado de revision."""
    return _hash(_validated_json(EipdResolutionAssessmentStoredV1, document))


def eipd_resolution_context_is_current_v1(
    document: EipdResolutionAssessmentStoredV1 | dict,
    context: EipdResolutionContextV1 | dict,
) -> bool:
    """Comparacion de lectura sin reasociar ni evaluar aprobacion/completitud."""
    parsed = EipdResolutionAssessmentStoredV1.model_validate(
        _validated_json(EipdResolutionAssessmentStoredV1, document)
    )
    expected = build_eipd_resolution_context_hash_v1(context)
    return (
        parsed.context_binding is not None
        and parsed.context_binding.context_hash == expected
    )


@dataclass(frozen=True)
class EipdResolutionIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class EipdResolutionApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class EipdResolutionDocumentReadinessV1:
    """Preparacion documental solamente; sin decision humana ni permiso de confirmar."""

    result: Literal["incompleto", "requiere_revision", "completo"]
    context_current: bool
    issues: tuple[EipdResolutionIssueV1, ...]
    applicability: tuple[EipdResolutionApplicabilityV1, ...]

    @property
    def is_document_prepared(self):
        return self.result == "completo" and self.context_current


def evaluate_eipd_resolution_document_v1(assessment, context, *, evaluated_on: date):
    """Matriz documental §60: pura, sin DB/clock/LLM ni gate de frontera.

    La fecha de evaluacion es explicita para resultados reproducibles. El servicio
    posterior verificara frontera, fuentes oficiales, controles y revision humana.
    """
    from app.services.licitud import canonicalize_text_v1

    if type(evaluated_on) is not date:
        raise ValueError("evaluated_on exige date explicita")
    document = (
        EipdResolutionAssessmentStoredV1.model_validate(
            _validated_json(EipdResolutionAssessmentStoredV1, assessment)
        )
        if assessment is not None
        else EipdResolutionAssessmentStoredV1()
    )
    ctx = (
        EipdResolutionContextV1.model_validate(
            _validated_json(EipdResolutionContextV1, context)
        )
        if context is not None
        else None
    )
    issues = []
    applicability = []

    def issue(field, code, category="incompleto"):
        issues.append(EipdResolutionIssueV1(field, code, category))

    def applies(field, value="aplicable"):
        applicability.append(EipdResolutionApplicabilityV1(field, value))

    def present(value):
        return value is not None and bool(value.strip())

    def text(field, value):
        applies(field)
        if not present(value):
            issue(field, "campo_obligatorio")

    def factual_date(field, value):
        applies(field)
        if value is None:
            issue(field, "fecha_ausente")
        elif value > evaluated_on:
            issue(field, "fecha_futura", "requiere_revision")

    def response(field, value):
        applies(field)
        if value is None:
            issue(field, "respuesta_ausente")
            return
        if value.answer == "pendiente":
            issue(field + ".answer", "respuesta_pendiente")
        elif value.answer == "no":
            issue(field + ".answer", "respuesta_revision", "requiere_revision")
        if not present(value.rationale):
            issue(field + ".rationale", "fundamento_ausente")

    def evidence(field, values, required=True, applicability_value="aplicable"):
        applies(field, applicability_value)
        if required and not values:
            issue(field, "evidencia_ausente")
        for index, item in enumerate(values):
            for name in ("evidence_type", "reference"):
                if not present(getattr(item, name)):
                    issue(f"{field}.{index}.{name}", "evidencia_incompleta")

    def residual(field, value, applicability_value="no_aplicable"):
        applies(field, applicability_value)
        if applicability_value == "no_aplicable" and (
            present(value) if isinstance(value, str) else value is not None
        ):
            issue(field, "campo_residual", "requiere_revision")

    if assessment is None:
        issue("eipd_resolution_assessment", "expediente_ausente")
    if ctx is None:
        issue("context", "contexto_ausente")
    for name in (
        "document_reference",
        "document_version",
        "report_reference",
        "prepared_by",
        "purpose_description",
        "processing_operations",
        "processing_context",
        "technologies_description",
        "exceptions_coverage_analysis",
        "necessity_analysis",
        "proportionality_analysis",
        "minimization_analysis",
        "prior_assessment_analysis",
        "residual_risk_summary",
        "residual_risk_rationale",
        "limitations_analysis",
        "follow_up_plan",
    ):
        text(name, getattr(document, name))
    factual_date("completed_on", document.completed_on)
    for name in (
        "necessary_for_purpose",
        "proportionate_processing",
        "minimization_addressed",
        "performed_before_processing",
    ):
        response(name, getattr(document, name))
    evidence("evidence", document.evidence)
    applies("residual_risk_level")
    if document.residual_risk_level in (None, "sin_resolver"):
        issue("residual_risk_level", "riesgo_residual_sin_resolver")
    elif document.residual_risk_level == "alto":
        issue("residual_risk_level", "riesgo_residual_alto", "requiere_revision")

    applies("scope")
    if document.scope is None:
        issue("scope", "alcance_ausente")
    selected = {}
    for name, rat_items in (
        (
            "data_category_codes",
            ctx.rat_context_snapshot.data_categories if ctx else [],
        ),
        ("data_subject_codes", ctx.rat_context_snapshot.data_subjects if ctx else []),
    ):
        field = "scope." + name
        applies(field)
        values = (
            [canonicalize_text_v1(v) for v in getattr(document.scope, name)]
            if document.scope
            else []
        )
        selected[name] = set(values)
        if not values:
            issue(field, "alcance_vacio")
        elif len(values) != len(set(values)):
            issue(field, "alcance_duplicado", "requiere_revision")
        if ctx is not None and values:
            required = {canonicalize_text_v1(i.category_code) for i in rat_items}
            if set(values) != required:
                issue(field, "alcance_rat_discordante", "requiere_revision")
    if ctx is not None:
        rat = ctx.rat_context_snapshot
        if present(document.purpose_description) and canonicalize_text_v1(
            document.purpose_description
        ) != canonicalize_text_v1(rat.purpose):
            issue("purpose_description", "finalidad_distinta", "requiere_revision")
        for name in (
            "sensitive_rights_exception_assessment",
            "biometric_rights_exception_assessment",
        ):
            exception = getattr(ctx, name)
            applies(
                name + ".scope",
                "aplicable" if exception is not None else "no_aplicable",
            )
            if exception is None:
                continue
            if exception.scope is None:
                issue(name + ".scope", "dependencia_alcance_ausente")
                continue
            for field in selected:
                codes = {
                    canonicalize_text_v1(v) for v in getattr(exception.scope, field)
                }
                if not codes:
                    issue(name + ".scope." + field, "alcance_vacio")
                elif document.scope is not None and not codes.issubset(selected[field]):
                    issue(
                        name + ".scope." + field,
                        "excepcion_fuera_alcance",
                        "requiere_revision",
                    )

    applies("risks")
    applies("measures")
    if not document.risks:
        issue("risks", "riesgos_ausentes")
    if not document.measures:
        issue("measures", "medidas_ausentes")
    risk_ids = []
    for index, risk in enumerate(document.risks):
        root = f"risks.{index}"
        for name in (
            "risk_id",
            "description",
            "impact_analysis",
            "initial_assessment_analysis",
            "residual_assessment_analysis",
        ):
            text(root + "." + name, getattr(risk, name))
        evidence(root + ".evidence", risk.evidence)
        risk_ids.append(
            canonicalize_text_v1(risk.risk_id) if present(risk.risk_id) else None
        )
    for index, rid in enumerate(risk_ids):
        if rid is not None and risk_ids.count(rid) > 1:
            issue(
                f"risks.{index}.risk_id", "identificador_duplicado", "requiere_revision"
            )
    known = {rid for rid in risk_ids if rid is not None}
    measure_ids = []
    covered = set()
    for index, measure in enumerate(document.measures):
        root = f"measures.{index}"
        for name in (
            "measure_id",
            "description",
            "effectiveness_analysis",
            "implementation_analysis",
        ):
            text(root + "." + name, getattr(measure, name))
        measure_ids.append(
            canonicalize_text_v1(measure.measure_id)
            if present(measure.measure_id)
            else None
        )
        response(root + ".implemented", measure.implemented)
        evidence(root + ".evidence", measure.evidence)
        applies(root + ".risk_ids")
        if not measure.risk_ids:
            issue(root + ".risk_ids", "referencias_riesgo_ausentes")
        refs = [canonicalize_text_v1(v) for v in measure.risk_ids]
        for offset, ref in enumerate(refs):
            path = root + f".risk_ids.{offset}"
            if not ref:
                issue(path, "referencia_riesgo_vacia")
            elif ref not in known:
                issue(path, "referencia_riesgo_desconocida", "requiere_revision")
            if ref and refs.count(ref) > 1:
                issue(path, "referencia_riesgo_duplicada", "requiere_revision")
        covered.update(known.intersection(refs))
    for index, mid in enumerate(measure_ids):
        if mid is not None and measure_ids.count(mid) > 1:
            issue(
                f"measures.{index}.measure_id",
                "identificador_duplicado",
                "requiere_revision",
            )
    for index, rid in enumerate(risk_ids):
        if rid is not None and rid not in covered:
            issue(f"risks.{index}.risk_id", "riesgo_sin_medida")

    sources = document.official_sources or EipdOfficialSourcesV1()
    applies("official_sources")
    if document.official_sources is None:
        issue("official_sources", "fuentes_ausentes")
    applies("official_sources.status")
    if sources.status in (None, "pendiente"):
        issue("official_sources.status", "fuentes_sin_resolver")
    factual_date("official_sources.checked_on", sources.checked_on)
    text("official_sources.applicability_analysis", sources.applicability_analysis)
    evidence("official_sources.evidence", sources.evidence)
    applies("official_sources.sources")
    if not sources.sources:
        issue("official_sources.sources", "fuentes_consultadas_ausentes")
    if sources.status == "identificado" and not any(
        present(source.publication_version) for source in sources.sources
    ):
        issue("official_sources.sources", "publicacion_identificada_ausente")
    for index, source in enumerate(sources.sources):
        root = f"official_sources.sources.{index}"
        text(root + ".source_reference", source.source_reference)
        text(root + ".review_analysis", source.review_analysis)
        applies(root + ".applicability")
        if source.applicability in (None, "pendiente"):
            issue(root + ".applicability", "aplicabilidad_sin_resolver")
        applies(
            root + ".publication_version",
            (
                "aplicable"
                if present(source.publication_version)
                or source.applicability == "aplicable"
                else (
                    "sin_resolver"
                    if source.applicability in (None, "pendiente")
                    else "no_aplicable"
                )
            ),
        )
        if source.applicability == "aplicable" and not present(
            source.publication_version
        ):
            issue(root + ".publication_version", "version_publicacion_ausente")
        if sources.status == "no_identificado" and source.applicability == "aplicable":
            issue(
                "official_sources.status",
                "fuentes_estado_discordante",
                "requiere_revision",
            )

    consultation = document.agency_consultation or EipdAgencyConsultationV1()
    applies("agency_consultation")
    if document.agency_consultation is None:
        issue("agency_consultation", "consulta_ausente")
    applies("agency_consultation.status")
    if consultation.status is None:
        issue("agency_consultation.status", "estado_consulta_ausente")
    elif consultation.status == "en_curso":
        issue("agency_consultation.status", "consulta_en_curso", "requiere_revision")
    text("agency_consultation.analysis", consultation.analysis)
    active = consultation.status in ("en_curso", "concluida")
    for name in (
        "consultation_reference",
        "response_reference",
        "recommendations_analysis",
        "reassessment_analysis",
        "recommendations_addressed",
    ):
        field = "agency_consultation." + name
        is_required = active and (
            name == "consultation_reference" or consultation.status == "concluida"
        )
        if is_required:
            if name == "recommendations_addressed":
                response(field, getattr(consultation, name))
            else:
                text(field, getattr(consultation, name))
        else:
            residual(
                field,
                getattr(consultation, name),
                "sin_resolver" if consultation.status is None else "no_aplicable",
            )
    evidence(
        "agency_consultation.evidence",
        consultation.evidence,
        required=active,
        applicability_value=(
            "sin_resolver" if consultation.status is None else "aplicable"
        ),
    )

    applies("context_binding")
    current = False
    if document.context_binding is None:
        issue("context_binding", "asociacion_ausente")
    elif ctx is not None:
        current = eipd_resolution_context_is_current_v1(document, ctx)
        if not current:
            issue(
                "context_binding.context_hash",
                "asociacion_obsoleta",
                "requiere_revision",
            )
    else:
        applies("context_binding.context_hash", "sin_resolver")

    roots = (
        ["context", "rat_context_snapshot", "eipd_resolution_assessment"]
        + list(EipdResolutionAssessmentStoredV1.model_fields)
        + [
            "sensitive_rights_exception_assessment",
            "biometric_rights_exception_assessment",
        ]
    )

    def order(item):
        parts = item.field.split(".")
        return (
            roots.index(parts[0]),
            tuple((0, int(p)) if p.isdigit() else (1, p) for p in parts[1:]),
            getattr(item, "code", ""),
        )

    ordered = tuple(sorted(set(issues), key=order))
    result = (
        "requiere_revision"
        if any(i.category == "requiere_revision" for i in ordered)
        else "incompleto" if ordered else "completo"
    )
    return EipdResolutionDocumentReadinessV1(
        result, current, ordered, tuple(sorted(set(applicability), key=order))
    )


def derive_eipd_resolution_review_state_v1(document, context, latest_review):
    """El ultimo evento sigue visible; vigencia de hashes no equivale a aprobacion."""
    if latest_review is None:
        return EipdResolutionReviewStateOut(
            review_status="sin_revision", latest_review=None
        )
    review = EipdResolutionReviewOut.model_validate(
        _validated_json(EipdResolutionReviewOut, latest_review)
    )
    current = False
    if document is not None and context is not None:
        parsed = EipdResolutionAssessmentStoredV1.model_validate(
            _validated_json(EipdResolutionAssessmentStoredV1, document)
        )
        current = (
            eipd_resolution_context_is_current_v1(parsed, context)
            and review.document_hash == build_eipd_resolution_document_hash_v1(parsed)
            and review.context_hash == parsed.context_binding.context_hash
        )
    return EipdResolutionReviewStateOut(
        review_status="vigente" if current else "obsoleta", latest_review=review
    )


@dataclass(frozen=True)
class EipdResolutionReviewPrerequisitesV1:
    """Prerequisitos documentales; no autentica ni autoriza ni escribe eventos."""

    decision: Literal["continuar", "requiere_cambios", "no_continuar"]
    issues: tuple[EipdResolutionIssueV1, ...]

    @property
    def prerequisites_met(self) -> bool:
        return not self.issues


def evaluate_eipd_resolution_review_prerequisites_v1(
    assessment_status, document, context, review, *, evaluated_on: date
):
    """§60.3: rechazos parciales actuales; continuar sigue cerrado en v1.

    La accion posterior debe autenticar permisos/suscripcion, bloquear la serie,
    releer borrador/RAT y resolver hashes/actor/fecha en servidor. Esta funcion
    no sustituye esos controles. No acepta banderas de aprobacion de frontera o
    fuentes: aun no existe verificacion implementada que pueda acreditarlas.
    """
    partial, parsed, ctx = _evaluate_eipd_review_partial_prerequisites(
        assessment_status, document, context, review, evaluated_on=evaluated_on
    )
    issues = list(partial.issues)
    if partial.decision == "continuar":
        readiness = evaluate_eipd_resolution_document_v1(
            parsed, ctx, evaluated_on=evaluated_on
        )
        issues.extend(readiness.issues)
        issues.append(
            EipdResolutionIssueV1(
                "review.decision", "frontera_revision_no_validada", "requiere_revision"
            )
        )
        issues.append(
            EipdResolutionIssueV1(
                "official_sources",
                "fuentes_oficiales_no_verificadas",
                "requiere_revision",
            )
        )
    return EipdResolutionReviewPrerequisitesV1(
        partial.decision, tuple(dict.fromkeys(issues))
    )


def _evaluate_eipd_review_partial_prerequisites(
    assessment_status, document, context, review, *, evaluated_on: date
):
    """Nucleo parcial compartido; no decide habilitacion de positivos."""
    if type(evaluated_on) is not date:
        raise ValueError("evaluated_on exige date explicita")
    if assessment_status not in ("borrador", "confirmado", "reemplazado"):
        raise ValueError("Estado de evaluacion desconocido")
    request = EipdResolutionReviewIn.model_validate(
        _validated_json(EipdResolutionReviewIn, review)
    )
    parsed = (
        EipdResolutionAssessmentStoredV1.model_validate(
            _validated_json(EipdResolutionAssessmentStoredV1, document)
        )
        if document is not None
        else None
    )
    ctx = (
        EipdResolutionContextV1.model_validate(
            _validated_json(EipdResolutionContextV1, context)
        )
        if context is not None
        else None
    )
    issues = []

    def block(field, code, category="requiere_revision"):
        issues.append(EipdResolutionIssueV1(field, code, category))

    if assessment_status != "borrador":
        block("status", "evaluacion_no_borrador")
    if parsed is None:
        block("eipd_resolution_assessment", "expediente_ausente", "incompleto")
    if ctx is None:
        block("rat_context_snapshot", "contexto_rat_no_disponible", "incompleto")
    if parsed is not None:
        if parsed.context_binding is None:
            block("context_binding", "asociacion_ausente", "incompleto")
        elif ctx is not None and not eipd_resolution_context_is_current_v1(parsed, ctx):
            block("context_binding.context_hash", "asociacion_obsoleta")
    return (
        EipdResolutionReviewPrerequisitesV1(
            request.decision, tuple(dict.fromkeys(issues))
        ),
        parsed,
        ctx,
    )
