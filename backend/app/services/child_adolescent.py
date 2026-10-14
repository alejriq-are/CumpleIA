"""Completitud/coherencia documental de infancia; no verifica edad ni autoriza."""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from app.schemas.child_adolescent import ChildAdolescentAssessmentV1
from app.schemas.licitud import RatContextSnapshotV1


@dataclass(frozen=True)
class ChildAdolescentIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]


@dataclass(frozen=True)
class ChildAdolescentReadinessV1:
    result: Literal["no_aplicable", "incompleto", "requiere_revision", "completo"]
    issues: tuple[ChildAdolescentIssueV1, ...]

    @property
    def evaluation_version(self) -> Literal[1]:
        return 1

    @property
    def can_confirm(self) -> Literal[False]:
        return False

    @property
    def authorizes_action(self) -> Literal[False]:
        return False


def raw(value):
    return value.model_dump(mode="python") if isinstance(value, BaseModel) else value


def evaluate_child_adolescent_v1(document, rat_snapshot):
    """Referencias y analisis presentes no equivalen a facultades verificadas."""
    doc = (
        ChildAdolescentAssessmentV1.model_validate(raw(document))
        if document is not None
        else None
    )
    rat = (
        RatContextSnapshotV1.model_validate(raw(rat_snapshot))
        if rat_snapshot is not None
        else None
    )
    if (
        doc is None
        and rat is not None
        and not (
            rat.special_regimes.includes_children
            or rat.special_regimes.includes_adolescents
            or any(
                x.includes_children or x.includes_adolescents for x in rat.data_subjects
            )
        )
    ):
        return ChildAdolescentReadinessV1("no_aplicable", ())
    issues = []

    def issue(field, code, category="incompleto"):
        issues.append(ChildAdolescentIssueV1(field, code, category))

    if rat is None:
        issue("rat_context_snapshot", "contexto_rat_no_disponible")
    else:
        expected = {
            "includes_children": any(x.includes_children for x in rat.data_subjects),
            "includes_adolescents": any(
                x.includes_adolescents for x in rat.data_subjects
            ),
            "has_sensitive_data": any(x.is_sensitive for x in rat.data_categories),
        }
        for field, value in expected.items():
            if getattr(rat.special_regimes, field) != value:
                issue(
                    "rat_context_snapshot.special_regimes." + field,
                    "resumen_rat_incoherente",
                    "requiere_revision",
                )
    if doc is None:
        issue("child_adolescent_assessment", "expediente_infancia_ausente")
    else:
        for field in (
            "age_scope_analysis",
            "best_interests_analysis",
            "progressive_autonomy_analysis",
            "authorization_reference",
            "authorization_analysis",
        ):
            if not (getattr(doc, field) or "").strip():
                issue(field, "campo_documental_pendiente")
        if not doc.declared_groups:
            issue("declared_groups", "grupos_edad_pendientes")
        if not doc.evidence or not any(
            (e.reference or "").strip() and e.evidence_type.strip()
            for e in doc.evidence
        ):
            issue("evidence", "evidencia_referenciada_pendiente")
        for field in ("data_category_codes", "data_subject_codes"):
            if not getattr(doc, field):
                issue(field, "alcance_pendiente")
        if doc.proposed_authorization_route is None:
            issue("proposed_authorization_route", "ruta_documental_pendiente")
        elif doc.proposed_authorization_route == "autorizacion_legal_expresa":
            issue(
                "proposed_authorization_route",
                "autorizacion_legal_infancia_revision_pendiente",
                "requiere_revision",
            )
        elif doc.declared_consent_giver is None:
            issue("declared_consent_giver", "otorgante_documental_pendiente")
        if rat is not None:
            categories = {x.category_code: x for x in rat.data_categories}
            subjects = {x.category_code: x for x in rat.data_subjects}
            for field, catalog in (
                ("data_category_codes", categories),
                ("data_subject_codes", subjects),
            ):
                if set(getattr(doc, field)) - catalog.keys():
                    issue(field, "codigo_ajeno_al_alcance", "requiere_revision")
            selected = [subjects[c] for c in doc.data_subject_codes if c in subjects]
            children = any(x.includes_children for x in selected)
            adolescents = any(x.includes_adolescents for x in selected)
            sensitive = any(
                categories[c].is_sensitive
                for c in doc.data_category_codes
                if c in categories
            )
            declared_children = "ninos_ninas" in doc.declared_groups
            declared_adolescents = any(
                g in doc.declared_groups
                for g in ("adolescentes", "adolescentes_sensibles_menores_16")
            )
            if selected and (
                children != declared_children or adolescents != declared_adolescents
            ):
                issue("declared_groups", "grupos_rat_incoherentes", "requiere_revision")
            if selected and not (children or adolescents):
                issue(
                    "data_subject_codes",
                    "expediente_infancia_residual",
                    "requiere_revision",
                )
            if children and adolescents:
                issue(
                    "declared_groups",
                    "grupos_mixtos_revision_pendiente",
                    "requiere_revision",
                )
            if (
                adolescents
                and sensitive
                and doc.sensitive_under16 in (None, "pendiente")
            ):
                issue("sensitive_under16", "cruce_sensible_edad_pendiente")
            if doc.sensitive_under16 == "si" and not (adolescents and sensitive):
                issue(
                    "sensitive_under16",
                    "cruce_sensible_edad_incoherente",
                    "requiere_revision",
                )
            if (
                "adolescentes_sensibles_menores_16" in doc.declared_groups
                and doc.sensitive_under16 != "si"
            ):
                issue(
                    "sensitive_under16",
                    "subgrupo_edad_incoherente",
                    "requiere_revision",
                )
            if (
                doc.proposed_authorization_route == "consentimiento"
                and doc.declared_consent_giver == "titular"
                and (children or doc.sensitive_under16 == "si")
            ):
                issue(
                    "declared_consent_giver",
                    "otorgante_requiere_revision",
                    "requiere_revision",
                )
    ordered = tuple(sorted(set(issues), key=lambda i: (i.field, i.code, i.category)))
    result = (
        "requiere_revision"
        if any(i.category == "requiere_revision" for i in ordered)
        else "incompleto" if ordered else "completo"
    )
    return ChildAdolescentReadinessV1(result, ordered)
