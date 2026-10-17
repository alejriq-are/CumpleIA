"""Preparacion pura de primera frontera EIPD §70; sin permiso de confirmar."""

from dataclasses import dataclass
from typing import Literal, get_args

from app.schemas.licitud import EipdQuestionIdV1
from app.services.eipd import EipdReadinessV1, evaluate_eipd_screening_v1
from app.services.eipd_resolution import (
    EipdResolutionApplicabilityV1,
    EipdResolutionContextV1,
    EipdResolutionIssueV1,
    _validated_json,
)
from app.services.special_conditions import (
    SpecialReadinessV1,
    evaluate_special_conditions_v1,
)


@dataclass(frozen=True)
class EipdFrontierReadinessV1:
    result: Literal["incompleto", "requiere_revision", "preparado"]
    route: Literal["sensible_derechos", "sensible_biometrica_derechos", "sin_resolver"]
    issues: tuple[EipdResolutionIssueV1, ...]
    applicability: tuple[EipdResolutionApplicabilityV1, ...]
    special: SpecialReadinessV1 | None
    screening: EipdReadinessV1 | None

    @property
    def is_frontier_prepared(self) -> bool:
        return self.result == "preparado"


def evaluate_eipd_frontier_v1(context):
    """No DB, reloj, LLM, flags de aprobacion ni filtrado de blockers historicos.

    Conserva screening v1 completo como diagnostico separado. La excepcion v1
    sigue no validada para confirmacion; esta funcion solo prepara la primera
    frontera y no altera el evaluador ni sus resultados historicos.
    """
    ctx = (
        EipdResolutionContextV1.model_validate(
            _validated_json(EipdResolutionContextV1, context)
        )
        if context is not None
        else None
    )
    issues = []
    applicability = []

    def issue(field, code, category="incompleto", question_id=None):
        issues.append(EipdResolutionIssueV1(field, code, category, question_id))

    def applies(field, value="aplicable"):
        applicability.append(EipdResolutionApplicabilityV1(field, value))

    route = "sin_resolver"
    special = screening = None
    applies("rat_context_snapshot")
    if ctx is None:
        issue("rat_context_snapshot", "contexto_rat_no_disponible")
    else:
        rat = ctx.rat_context_snapshot
        applies("rat_context_snapshot.organization_role")
        if rat.organization_role is None:
            issue("rat_context_snapshot.organization_role", "rol_ausente")
        elif rat.organization_role != "responsable":
            issue(
                "rat_context_snapshot.organization_role",
                "rol_fuera_frontera",
                "requiere_revision",
            )
        special_args = [
            getattr(ctx, f)
            for f in (
                "consent_assessment",
                "lia_assessment",
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
        ]
        special = evaluate_special_conditions_v1(
            ctx.special_conditions, rat, ctx.legal_basis, *special_args
        )
        # Motivos especiales completos, incluidos residuos y asociaciones.
        issues.extend(
            EipdResolutionIssueV1(i.field, i.code, i.category, i.question_id)
            for i in special.issues
        )
        applies("special_conditions")
        applies("special_conditions.context_binding")
        if ctx.special_conditions is not None and not special.context_current:
            issue(
                "special_conditions.context_binding",
                "asociacion_especial_no_vigente",
                "requiere_revision",
            )
        allowed = {"sensibles_art16", "biometricos_art16ter"}
        detected = set(special.detected_regimes)
        for regime in sorted(detected - allowed):
            issue(
                "special_conditions.conditions." + regime,
                "regimen_fuera_frontera",
                "requiere_revision",
            )
        if "sensibles_art16" not in detected:
            issue(
                "special_conditions", "ruta_sensible_no_detectada", "requiere_revision"
            )
        else:
            route = (
                "sensible_biometrica_derechos"
                if "biometricos_art16ter" in detected
                else "sensible_derechos"
            )
        conditions = (
            {c.regime_id: c for c in ctx.special_conditions.conditions}
            if ctx.special_conditions
            else {}
        )
        for regime in sorted(detected & allowed):
            path = "special_conditions.conditions." + regime
            condition = conditions.get(regime)
            applies(path)
            if condition is None:
                issue(path, "condicion_frontera_ausente")
                continue
            if condition.authorization_route is None:
                issue(path + ".authorization_route", "ruta_ausente")
            elif condition.authorization_route != "excepcion_legal":
                issue(
                    path + ".authorization_route",
                    "ruta_fuera_frontera",
                    "requiere_revision",
                )
            if regime == "sensibles_art16":
                if condition.sensitive_condition_id is None:
                    issue(path + ".sensitive_condition_id", "excepcion_ausente")
                elif condition.sensitive_condition_id != "defensa_derechos_art16d":
                    issue(
                        path + ".sensitive_condition_id",
                        "excepcion_fuera_frontera",
                        "requiere_revision",
                    )
        if (
            "biometricos_art16ter" not in detected
            and ctx.biometric_rights_exception_assessment is not None
        ):
            issue(
                "biometric_rights_exception_assessment",
                "expediente_fuera_frontera",
                "requiere_revision",
            )
        for field in (
            "geolocation_assessment",
            "sensitive_consent_assessment",
            "health_assessment",
            "biometric_assessment",
        ):
            applies(field, "no_aplicable")
            if getattr(ctx, field) is not None:
                issue(field, "expediente_fuera_frontera", "requiere_revision")
        screening = evaluate_eipd_screening_v1(
            ctx.eipd_screening,
            rat,
            ctx.lia_assessment,
            ctx.special_conditions,
            ctx.contract_assessment,
            ctx.legal_obligation_assessment,
            ctx.rights_defense_assessment,
            ctx.economic_obligations_assessment,
            ctx.geolocation_assessment,
            ctx.sensitive_consent_assessment,
            ctx.consent_assessment,
            ctx.health_assessment,
            ctx.biometric_assessment,
            ctx.sensitive_rights_exception_assessment,
            ctx.biometric_rights_exception_assessment,
            legal_basis=ctx.legal_basis,
        )
        applies("eipd_screening")
        if ctx.eipd_screening is None:
            issue("eipd_screening", "screening_ausente")
        else:
            applies("eipd_screening.context_binding")
            if not screening.context_current:
                issue(
                    "eipd_screening.context_binding",
                    "asociacion_screening_no_vigente",
                    "requiere_revision",
                )
            answers = {a.question_id: a for a in ctx.eipd_screening.answers}
            for question in get_args(EipdQuestionIdV1):
                path = "eipd_screening.answers." + question
                applies(path)
                answer = answers.get(question)
                if answer is None:
                    issue(path, "pregunta_omitida", question_id=question)
                    continue
                if not answer.rationale or not answer.rationale.strip():
                    issue(
                        path + ".rationale", "fundamento_ausente", question_id=question
                    )
                expected = (
                    "si"
                    if question == "datos_protegidos_excepcion_consentimiento"
                    else "no"
                )
                if answer.answer == "pendiente":
                    issue(path + ".answer", "respuesta_pendiente", question_id=question)
                elif answer.answer != expected:
                    issue(
                        path + ".answer",
                        (
                            "supuesto_fuera_frontera"
                            if expected == "no"
                            else "excepcion_consentimiento_discordante"
                        ),
                        "requiere_revision",
                        question,
                    )
    ordered = tuple(
        sorted(
            set(issues),
            key=lambda i: (i.field, i.code, i.category, i.question_id or ""),
        )
    )
    result = (
        "requiere_revision"
        if any(i.category == "requiere_revision" for i in ordered)
        else "incompleto" if ordered else "preparado"
    )
    return EipdFrontierReadinessV1(
        result,
        route,
        ordered,
        tuple(sorted(set(applicability), key=lambda a: a.field)),
        special,
        screening,
    )
