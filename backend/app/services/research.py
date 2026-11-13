"""Preparacion documental pura; sin persistencia, gates ni autorizacion juridica."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import RatContextSnapshotV1
from app.schemas.research import ResearchAssessmentV1
from app.services.lia import evaluate_lia_assessment_v1


@dataclass(frozen=True)
class ResearchIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]


@dataclass(frozen=True)
class ResearchApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class ResearchReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[ResearchIssueV1, ...]
    applicability: tuple[ResearchApplicabilityV1, ...]

    @property
    def can_confirm(self):
        # Aun sin integracion: completo solo describe preparacion documental.
        return False


def evaluate_research_assessment_v1(assessment, snapshot, legal_basis, lia_assessment):
    from app.services.licitud import canonicalize_text_v1

    raw = (
        assessment.model_dump()
        if isinstance(assessment, ResearchAssessmentV1)
        else assessment
    )
    document = (
        ResearchAssessmentV1.model_validate(raw)
        if raw is not None
        else ResearchAssessmentV1()
    )
    rat = (
        RatContextSnapshotV1.model_validate(
            snapshot.model_dump()
            if isinstance(snapshot, RatContextSnapshotV1)
            else snapshot
        )
        if snapshot is not None
        else None
    )
    issues = []
    applicability = []

    def issue(field, code, category="incompleto"):
        issues.append(ResearchIssueV1(field, code, category))

    def present(value):
        return isinstance(value, str) and bool(value.strip())

    def required(field):
        if not present(getattr(document, field)):
            issue(field, "campo_obligatorio")

    def evidence(field):
        items = getattr(document, field)
        if not items:
            issue(field, "evidencia_ausente")
        for index, item in enumerate(items):
            if not present(item.evidence_type) or not present(item.reference):
                issue(f"{field}.{index}", "evidencia_incompleta")

    def response(field, require_yes):
        value = getattr(document, field)
        if value is None:
            issue(field, "campo_obligatorio")
        elif value.answer == "pendiente":
            issue(field, "respuesta_pendiente")
        elif require_yes and value.answer == "no":
            issue(field, "respuesta_revision", "requiere_revision")
        if value is not None and not present(value.rationale):
            issue(field + ".rationale", "campo_obligatorio")

    if assessment is None:
        issue("research_assessment", "expediente_ausente")
    if document.purpose_type is None:
        issue("purpose_type", "campo_obligatorio")
    for field in (
        "purpose_description",
        "public_interest_analysis",
        "exclusivity_controls_analysis",
        "quality_measures_analysis",
        "security_measures_analysis",
        "retention_analysis",
    ):
        required(field)
    response("exclusive_use", True)
    response("measures_implemented", True)
    response("publication_planned", False)
    evidence("evidence")
    planned = document.publication_planned
    applies = (
        "sin_resolver"
        if planned is None or planned.answer == "pendiente"
        else "aplicable" if planned.answer == "si" else "no_aplicable"
    )
    applicability.append(ResearchApplicabilityV1("anonymization", applies))
    if applies == "aplicable":
        required("anonymization_method")
        required("anonymization_analysis")
        evidence("anonymization_evidence")
    elif applies == "no_aplicable" and (
        present(document.anonymization_method)
        or present(document.anonymization_analysis)
        or document.anonymization_evidence
    ):
        issue("anonymization", "documento_residual", "requiere_revision")
    if legal_basis != "interes_legitimo_art13d":
        issue("legal_basis", "base_no_admitida", "requiere_revision")
    dependency = evaluate_lia_assessment_v1(lia_assessment, snapshot)
    issues.extend(
        ResearchIssueV1("lia_assessment." + i.field, i.code, i.category)
        for i in dependency.issues
    )
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    else:
        if present(document.purpose_description) and canonicalize_text_v1(
            document.purpose_description
        ) != canonicalize_text_v1(rat.purpose):
            issue("purpose_description", "finalidad_distinta", "requiere_revision")
        for field, items in (
            ("data_category_codes", rat.data_categories),
            ("data_subject_codes", rat.data_subjects),
        ):
            codes = [canonicalize_text_v1(c) for c in getattr(document, field)]
            expected = {canonicalize_text_v1(i.category_code) for i in items}
            if not codes:
                issue(field, "alcance_ausente")
            elif len(codes) != len(set(codes)) or set(codes) != expected:
                issue(field, "alcance_no_cubierto", "requiere_revision")
        if rat.special_regimes.has_sensitive_data or any(
            c.is_sensitive for c in rat.data_categories
        ):
            issue(
                "rat_context_snapshot",
                "ruta_sensible_no_preparada",
                "requiere_revision",
            )
        if (
            rat.special_regimes.includes_children
            or rat.special_regimes.includes_adolescents
            or rat.special_regimes.has_vulnerable_groups
            or any(
                s.includes_children or s.includes_adolescents or s.is_vulnerable_group
                for s in rat.data_subjects
            )
        ):
            issue(
                "rat_context_snapshot", "titulares_no_preparados", "requiere_revision"
            )
    issues = tuple(sorted(set(issues), key=lambda i: (i.field, i.code, i.category)))
    result = (
        "requiere_revision"
        if any(i.category == "requiere_revision" for i in issues)
        else "incompleto" if issues else "completo"
    )
    return ResearchReadinessV1(result, issues, tuple(applicability))
