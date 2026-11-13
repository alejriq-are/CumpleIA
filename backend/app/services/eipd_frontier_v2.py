"""Frontera pura de investigacion; no habilita rutas especiales ni confirmacion."""

from dataclasses import dataclass
from typing import Literal

from app.services.eipd import EipdReadinessV1, evaluate_eipd_screening_v1
from app.services.eipd_resolution import EipdResolutionIssueV1, _validated_json
from app.services.eipd_resolution_binding_v2 import EipdResolutionContextV2
from app.services.research import ResearchReadinessV1, evaluate_research_assessment_v1
from app.services.research_binding import (
    ResearchAssociationV1,
    evaluate_research_association_v1,
)
from app.services.special_conditions import (
    SpecialReadinessV1,
    evaluate_special_conditions_v1,
)


@dataclass(frozen=True)
class EipdFrontierReadinessV2:
    result: Literal["incompleto", "requiere_revision"]
    route: Literal["investigacion_no_sensible_adultos", "sin_resolver"]
    issues: tuple[EipdResolutionIssueV1, ...]
    research: ResearchReadinessV1 | None
    research_association: ResearchAssociationV1 | None
    special: SpecialReadinessV1 | None
    screening: EipdReadinessV1 | None

    @property
    def is_frontier_prepared(self):
        return False

    @property
    def can_confirm(self):
        return False


def evaluate_eipd_frontier_v2(context):
    ctx = (
        EipdResolutionContextV2.model_validate(
            _validated_json(EipdResolutionContextV2, context)
        )
        if context is not None
        else None
    )
    issues = []

    def issue(field, code, category="incompleto"):
        issues.append(EipdResolutionIssueV1(field, code, category))

    if ctx is None:
        issue("context", "contexto_rat_no_disponible")
        return EipdFrontierReadinessV2(
            "incompleto", "sin_resolver", tuple(issues), None, None, None, None
        )
    rat = ctx.rat_context_snapshot
    document = ctx.research_assessment
    research = evaluate_research_assessment_v1(
        document.assessment if document else None,
        rat,
        ctx.legal_basis,
        ctx.lia_assessment,
    )
    association = evaluate_research_association_v1(
        document, rat, ctx.legal_basis, ctx.lia_assessment
    )
    issues.extend(
        EipdResolutionIssueV1("research_assessment." + i.field, i.code, i.category)
        for i in research.issues
    )
    issues.extend(
        EipdResolutionIssueV1(
            "research_assessment.context_binding", c, "requiere_revision"
        )
        for c in association.issues
    )
    if rat.organization_role is None:
        issue("rat_context_snapshot.organization_role", "rol_ausente")
    elif rat.organization_role != "responsable":
        issue(
            "rat_context_snapshot.organization_role",
            "rol_fuera_frontera",
            "requiere_revision",
        )
    names = (
        "contract_assessment",
        "legal_obligation_assessment",
        "rights_defense_assessment",
        "economic_obligations_assessment",
        "geolocation_assessment",
        "sensitive_consent_assessment",
        "health_assessment",
        "biometric_assessment",
        "sensitive_rights_exception_assessment",
        "biometric_rights_exception_assessment",
    )
    extra = [getattr(ctx, n) for n in names]
    special = evaluate_special_conditions_v1(
        ctx.special_conditions,
        rat,
        ctx.legal_basis,
        ctx.consent_assessment,
        ctx.lia_assessment,
        *extra,
        research=document,
    )
    screening = evaluate_eipd_screening_v1(
        ctx.eipd_screening,
        rat,
        ctx.lia_assessment,
        ctx.special_conditions,
        *extra[:6],
        ctx.consent_assessment,
        *extra[6:],
        legal_basis=ctx.legal_basis,
        research=document,
    )
    issues.extend(
        EipdResolutionIssueV1(
            "special_conditions." + i.field,
            i.code,
            "requiere_revision" if i.category == "requiere_revision" else "incompleto",
            i.question_id,
        )
        for i in special.issues
    )
    issues.extend(
        EipdResolutionIssueV1(
            "eipd_screening." + i.field, i.code, "requiere_revision", i.question_id
        )
        for i in screening.issues
    )
    if not special.context_current:
        issue(
            "special_conditions.context_binding",
            "asociacion_obsoleta",
            "requiere_revision",
        )
    if not screening.context_current:
        issue(
            "eipd_screening.context_binding", "asociacion_obsoleta", "requiere_revision"
        )
    declaration = (
        next(
            (
                d
                for d in ctx.special_conditions.declarations
                if d.question_id
                == "fines_historicos_estadisticos_cientificos_investigacion"
            ),
            None,
        )
        if ctx.special_conditions
        else None
    )
    if document is not None and (declaration is None or declaration.answer != "si"):
        issue(
            "special_conditions.declarations",
            "investigacion_declaracion_discordante",
            "requiere_revision",
        )
    condition = (
        next(
            (
                c
                for c in ctx.special_conditions.conditions
                if c.regime_id == "investigacion_art16quinquies"
            ),
            None,
        )
        if ctx.special_conditions
        else None
    )
    if condition is None:
        issue("special_conditions.conditions", "expediente_regimen_ausente")
    elif document is not None and (
        set(condition.data_category_codes)
        != set(document.assessment.data_category_codes)
        or set(condition.data_subject_codes)
        != set(document.assessment.data_subject_codes)
    ):
        issue(
            "special_conditions.conditions",
            "investigacion_alcance_discordante",
            "requiere_revision",
        )
    route = (
        "investigacion_no_sensible_adultos"
        if document is not None
        and ctx.legal_basis == "interes_legitimo_art13d"
        and rat.organization_role == "responsable"
        and not any(
            i.code in ("ruta_sensible_no_preparada", "titulares_no_preparados")
            for i in research.issues
        )
        else "sin_resolver"
    )
    issue(
        "research_assessment",
        "investigacion_confirmacion_bloqueada",
        "requiere_revision",
    )
    ordered = tuple(
        sorted(
            set(issues),
            key=lambda i: (i.field, i.code, i.category, i.question_id or ""),
        )
    )
    return EipdFrontierReadinessV2(
        "requiere_revision", route, ordered, research, association, special, screening
    )
