"""Diagnostico documental conservador; nunca acredita facultad ni confirma."""

from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import TypeAdapter

from app.schemas.sensitive_representation import BoundSensitiveRepresentationV1
from app.services.research_binding import validated
from app.services.sensitive_representation_binding import (
    SensitiveRepresentationContextV1,
    evaluate_sensitive_representation_association_v1,
)


@dataclass(frozen=True)
class SensitiveRepresentationIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]


@dataclass(frozen=True)
class SensitiveRepresentationReadinessV1:
    result: Literal["no_aplicable", "incompleto", "requiere_revision", "completo"]
    issues: tuple[SensitiveRepresentationIssueV1, ...]

    @property
    def can_confirm(self):
        return False


def evaluate_sensitive_representation_v1(bound, context, *, evaluated_on):
    ctx = validated(SensitiveRepresentationContextV1, context)
    day = TypeAdapter(date).validate_python(evaluated_on)
    document = (
        validated(BoundSensitiveRepresentationV1, bound) if bound is not None else None
    )
    given_by = ctx.consent_assessment.given_by if ctx.consent_assessment else None
    if given_by == "titular" and document is None:
        return SensitiveRepresentationReadinessV1("no_aplicable", ())
    issues = []

    def add(field, code, category="incompleto"):
        issues.append(SensitiveRepresentationIssueV1(field, code, category))

    if ctx.legal_basis != "consentimiento_art12":
        add("legal_basis", "representacion_ruta_no_admitida", "requiere_revision")
    if given_by is None:
        add("consent_assessment.given_by", "representacion_otorgante_pendiente")
    elif given_by == "titular":
        add(
            "consent_assessment.given_by",
            "representacion_documento_incompatible",
            "requiere_revision",
        )
    if document is None:
        add("representation_assessment", "representacion_documento_ausente")
    else:
        for code in evaluate_sensitive_representation_association_v1(
            document, ctx
        ).issues:
            add("context_binding", code, "requiere_revision")
        material = document.assessment
        if material.representation_kind is None:
            add("representation_kind", "representacion_clase_pendiente")
        elif given_by is not None and material.representation_kind != given_by:
            add(
                "representation_kind",
                "representacion_clase_incompatible",
                "requiere_revision",
            )
        for field in (
            "representative_reference",
            "represented_subjects_reference",
            "authority_document_reference",
            "authority_document_version",
            "authority_basis_description",
            "express_authority_analysis",
            "scope_match_analysis",
            "validity_analysis",
            "limitations",
            "revocation_information",
        ):
            if getattr(material, field) is None:
                add(field, "representacion_material_pendiente")
        if material.scope is None:
            add("scope", "representacion_alcance_pendiente")
        else:
            rat = ctx.rat_context_snapshot
            if set(material.scope.data_category_codes) != {
                item.category_code for item in rat.data_categories
            } or set(material.scope.data_subject_codes) != {
                item.category_code for item in rat.data_subjects
            }:
                add(
                    "scope",
                    "representacion_alcance_rat_incompatible",
                    "requiere_revision",
                )
            sensitive_scope = (
                ctx.sensitive_consent_assessment.scope
                if ctx.sensitive_consent_assessment
                else None
            )
            if sensitive_scope is None:
                add(
                    "sensitive_consent_assessment.scope",
                    "representacion_alcance_sensible_pendiente",
                )
            elif set(material.scope.data_category_codes) != set(
                sensitive_scope.data_category_codes
            ) or set(material.scope.data_subject_codes) != set(
                sensitive_scope.data_subject_codes
            ):
                add(
                    "scope",
                    "representacion_alcance_sensible_incompatible",
                    "requiere_revision",
                )
        if not any(
            item.reference and item.reference.strip() and item.evidence_type.strip()
            for item in material.evidence
        ):
            add("evidence", "representacion_evidencia_pendiente")
        for field in ("issued_on", "valid_from"):
            if getattr(material, field) is not None and getattr(material, field) > day:
                add(field, "representacion_fecha_futura", "requiere_revision")
        if material.valid_until is not None and material.valid_until < day:
            add(
                "valid_until",
                "representacion_intervalo_finalizado",
                "requiere_revision",
            )
    rat = ctx.rat_context_snapshot
    for field in ("includes_children", "includes_adolescents", "has_vulnerable_groups"):
        subject_field = (
            "is_vulnerable_group" if field == "has_vulnerable_groups" else field
        )
        if getattr(rat.special_regimes, field) or any(
            getattr(item, subject_field) for item in rat.data_subjects
        ):
            add(
                f"rat.{field}",
                "representacion_regimen_concurrente_pendiente",
                "requiere_revision",
            )
    result = "completo"
    if any(issue.category == "requiere_revision" for issue in issues):
        result = "requiere_revision"
    elif issues:
        result = "incompleto"
    return SensitiveRepresentationReadinessV1(result, tuple(issues))
