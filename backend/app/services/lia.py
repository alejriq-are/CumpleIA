"""Preparación documental LIA v1: evaluación pura, sin persistencia."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import LiaAssessmentV1, RatContextSnapshotV1

LiaReadiness = Literal["completo", "requiere_revision", "incompleto"]
LiaApplicability = Literal["aplicable", "no_aplicable", "sin_resolver"]
LiaIssueCode = Literal[
    "expediente_ausente",
    "snapshot_ausente",
    "campo_obligatorio",
    "respuesta_pendiente",
    "no_aplica_invalido",
    "aplicabilidad_sin_resolver",
    "respuesta_revision",
    "respuesta_no_aplicable",
    "finalidad_distinta",
    "medida_incompleta",
    "decision_revision",
]


@dataclass(frozen=True)
class LiaIssueV1:
    field: str
    code: LiaIssueCode
    category: Literal["incompleto", "requiere_revision"]


@dataclass(frozen=True)
class LiaFieldApplicabilityV1:
    field: str
    applicability: LiaApplicability


@dataclass(frozen=True)
class LiaReadinessV1:
    result: LiaReadiness
    issues: tuple[LiaIssueV1, ...]
    applicability: tuple[LiaFieldApplicabilityV1, ...]

    @property
    def can_confirm(self) -> bool:
        """Supera solo este control; no habilita el lifecycle M3 por sí mismo."""
        return self.result == "completo"


_REQUIRED_TEXTS = {
    "purpose_and_interest": (
        "purpose_description",
        "legitimate_interest",
        "interest_importance",
        "consequences_without_processing",
    ),
    "necessity": (
        "necessity_analysis",
        "proportionality_analysis",
        "alternatives_analysis",
        "minimization_analysis",
    ),
    "reasonable_expectations": ("expectations_analysis",),
    "impact": (
        "negative_effects",
        "intrusion_analysis",
        "rights_and_freedoms_analysis",
        "impact_analysis",
    ),
    "safeguards": ("safeguards_analysis",),
    "transparency_and_opposition": (
        "information_method",
        "interest_communication",
        "opposition_channel",
        "opposition_procedure",
        "responsible_area",
    ),
    "conclusion": (
        "balancing_summary",
        "identified_interest",
        "necessity_and_proportionality_result",
        "main_impacts",
        "relevant_safeguards",
        "rights_protection_reasoning",
    ),
}
_REQUIRED_RESPONSES = {
    "necessity": (
        "contributes_to_purpose",
        "linked_to_interest",
        "achievable_without_personal_data",
        "less_intrusive_alternative",
        "fewer_data_possible",
        "categories_necessary_and_relevant",
    ),
    "nature_and_scope": ("exclusively_professional_context",),
    "reasonable_expectations": (
        "prior_relationship",
        "significant_change_of_use",
        "foreseeable_purpose_and_method",
        "innovative_processing",
    ),
    "impact": (
        "loss_of_control",
        "reasonable_opposition_likelihood",
        "transparently_explainable",
        "relevant_unmitigated_impacts",
    ),
}
_REVIEW_ANSWERS = {
    "necessity.contributes_to_purpose": "no",
    "necessity.linked_to_interest": "no",
    "necessity.categories_necessary_and_relevant": "no",
    "necessity.achievable_without_personal_data": "si",
    "necessity.less_intrusive_alternative": "si",
    "reasonable_expectations.foreseeable_purpose_and_method": "no",
    "reasonable_expectations.informed_at_direct_collection": "no",
    "impact.transparently_explainable": "no",
    "impact.relevant_unmitigated_impacts": "si",
}


def evaluate_lia_assessment_v1(
    assessment: LiaAssessmentV1 | dict | None,
    snapshot: RatContextSnapshotV1 | dict | None,
) -> LiaReadinessV1:
    """Revalida ambos contratos y conserva textos, motivos y aplicabilidad."""
    # Import local para reutilizar canonización v1 sin dependencia circular
    # cuando el lifecycle incorpore este evaluador.
    from app.services.licitud import canonicalize_text_v1

    lia = (
        LiaAssessmentV1.model_validate(
            assessment.model_dump()
            if isinstance(assessment, LiaAssessmentV1)
            else assessment
        )
        if assessment is not None
        else LiaAssessmentV1()
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
    issues: list[LiaIssueV1] = []
    conditional: dict[str, LiaApplicability] = {}

    def issue(field, code, category="incompleto"):
        issues.append(LiaIssueV1(field, code, category))

    def text_present(value):
        return value is not None and bool(value.strip())

    def require_text(path, value, code="campo_obligatorio"):
        if not text_present(value):
            issue(path, code)

    def answer(value):
        return value.answer if value is not None else None

    def response(path, value, applies="aplicable"):
        value_answer = answer(value)
        if applies == "sin_resolver":
            issue(path, "aplicabilidad_sin_resolver")
        elif applies == "no_aplicable":
            if value_answer is not None and value_answer != "no_aplica":
                issue(path, "respuesta_no_aplicable", "requiere_revision")
        elif value_answer is None:
            issue(path, "campo_obligatorio")
        elif value_answer == "pendiente":
            issue(path, "respuesta_pendiente")
        elif value_answer == "no_aplica":
            issue(path, "no_aplica_invalido")
        elif _REVIEW_ANSWERS.get(path) == value_answer:
            issue(path, "respuesta_revision", "requiere_revision")

    if assessment is None:
        issue("lia_assessment", "expediente_ausente")
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    else:
        require_text("rat_context_snapshot.purpose", rat.purpose)
        for field in ("data_categories", "data_subjects", "organization_role"):
            if not getattr(rat, field):
                issue(f"rat_context_snapshot.{field}", "campo_obligatorio")

    for section, fields in _REQUIRED_TEXTS.items():
        for field in fields:
            require_text(f"{section}.{field}", getattr(getattr(lia, section), field))
    for section, fields in _REQUIRED_RESPONSES.items():
        for field in fields:
            response(f"{section}.{field}", getattr(getattr(lia, section), field))

    holder = lia.purpose_and_interest.interest_holder
    if holder is None:
        issue("purpose_and_interest.interest_holder", "campo_obligatorio")
    for field, holders in (
        ("controller_benefit", ("responsable", "ambos")),
        ("third_party_benefit", ("tercero", "ambos")),
    ):
        conditional[f"purpose_and_interest.{field}"] = (
            "sin_resolver"
            if holder is None
            else "aplicable" if holder in holders else "no_aplicable"
        )
    prior = answer(lia.reasonable_expectations.prior_relationship)
    conditional["reasonable_expectations.relationship_description"] = (
        "aplicable"
        if prior == "si"
        else "no_aplicable" if prior == "no" else "sin_resolver"
    )
    sources = {source.source_type for source in rat.data_sources} if rat else set()
    for field, source in (
        ("informed_at_direct_collection", "titular"),
        ("third_party_information", "tercero"),
    ):
        conditional[f"reasonable_expectations.{field}"] = (
            "sin_resolver"
            if not sources
            else "aplicable" if source in sources else "no_aplicable"
        )
    regimes = rat.special_regimes.model_dump() if rat else None
    conditional["nature_and_scope.special_rules_description"] = (
        "sin_resolver"
        if regimes is None
        else "aplicable" if any(regimes.values()) else "no_aplicable"
    )
    conditional["impact.vulnerable_people_impact"] = (
        "sin_resolver"
        if regimes is None
        else (
            "aplicable"
            if any(
                regimes[key]
                for key in (
                    "includes_children",
                    "includes_adolescents",
                    "has_vulnerable_groups",
                )
            )
            else "no_aplicable"
        )
    )

    impact = lia.impact
    ratings = (impact.severity, impact.likelihood)
    triggers = tuple(
        answer(getattr(impact, field))
        for field in (
            "loss_of_control",
            "reasonable_opposition_likelihood",
            "relevant_unmitigated_impacts",
        )
    )
    for field in ("severity", "likelihood"):
        rating = getattr(impact, field)
        if rating is None:
            issue(f"impact.{field}", "campo_obligatorio")
        elif rating == "pendiente":
            issue(f"impact.{field}", "respuesta_pendiente")
    measures_apply: LiaApplicability = "no_aplicable"
    if any(rating in ("media", "alta") for rating in ratings) or "si" in triggers:
        measures_apply = "aplicable"
    elif any(rating in (None, "pendiente") for rating in ratings) or any(
        value not in ("si", "no") for value in triggers
    ):
        measures_apply = "sin_resolver"
    conditional["safeguards.measures"] = measures_apply

    for path, applies in conditional.items():
        section, field = path.split(".")
        value = getattr(getattr(lia, section), field)
        if field == "informed_at_direct_collection":
            response(path, value, applies)
        elif applies == "sin_resolver":
            issue(path, "aplicabilidad_sin_resolver")
        elif applies == "aplicable":
            if field == "measures":
                if not value:
                    issue(path, "campo_obligatorio")
            else:
                require_text(path, value)
    for index, measure in enumerate(lia.safeguards.measures):
        require_text(
            f"safeguards.measures.{index}.description",
            measure.description,
            "medida_incompleta",
        )
        if measures_apply == "aplicable":
            require_text(
                f"safeguards.measures.{index}.mitigated_impact",
                measure.mitigated_impact,
                "medida_incompleta",
            )

    if (
        rat
        and text_present(rat.purpose)
        and text_present(lia.purpose_and_interest.purpose_description)
    ):
        if canonicalize_text_v1(rat.purpose) != canonicalize_text_v1(
            lia.purpose_and_interest.purpose_description
        ):
            issue(
                "purpose_and_interest.purpose_description",
                "finalidad_distinta",
                "requiere_revision",
            )
    decision = lia.conclusion.decision
    if decision is None:
        issue("conclusion.decision", "campo_obligatorio")
    elif decision != "puede_basarse":
        issue("conclusion.decision", "decision_revision", "requiere_revision")

    def sort_key(path):
        if path.startswith("rat_context_snapshot"):
            fields = [
                "purpose",
                "data_categories",
                "data_subjects",
                "organization_role",
            ]
            suffix = path.split(".")
            return (0, fields.index(suffix[1]) + 1 if len(suffix) > 1 else 0, 0, 0, 0)
        if path == "lia_assessment":
            return (1, 0, 0, 0, 0)
        section, field, *rest = path.split(".")
        return (
            2,
            list(LiaAssessmentV1.model_fields).index(section),
            list(type(getattr(lia, section)).model_fields).index(field),
            int(rest[0]) + 1 if rest else 0,
            1 if len(rest) > 1 and rest[1] == "mitigated_impact" else 0,
        )

    issues.sort(key=lambda item: sort_key(item.field))
    applicability = tuple(
        LiaFieldApplicabilityV1(path, conditional[path])
        for path in sorted(conditional, key=sort_key)
    )
    result: LiaReadiness = (
        "incompleto"
        if any(item.category == "incompleto" for item in issues)
        else "requiere_revision" if issues else "completo"
    )
    return LiaReadinessV1(result, tuple(issues), applicability)
