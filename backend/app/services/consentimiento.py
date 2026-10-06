"""Evaluación operativa del checklist de consentimiento v1, sin persistencia."""

from dataclasses import dataclass
from typing import Literal, get_args

from app.schemas.licitud import ConsentAssessmentV1, ConsentQuestionIdV1

ConsentReadiness = Literal["completo", "requiere_revision", "incompleto"]
ConsentApplicability = Literal["aplicable", "no_aplicable", "sin_resolver"]
ConsentIssueCode = Literal[
    "expediente_ausente",
    "campo_obligatorio",
    "pregunta_omitida",
    "respuesta_pendiente",
    "no_aplica_invalido",
    "respuesta_desfavorable",
    "respuesta_no_aplicable",
    "aplicabilidad_sin_resolver",
    "tipo_evidencia_vacio",
]

# El orden del Literal es el orden documental de §17.9.
_QUESTION_IDS = get_args(ConsentQuestionIdV1)
_CONDITIONAL_IDS = _QUESTION_IDS[-2:]


@dataclass(frozen=True)
class ConsentIssueV1:
    field: str
    code: ConsentIssueCode
    category: Literal["incompleto", "requiere_revision"]
    question_id: ConsentQuestionIdV1 | None = None


@dataclass(frozen=True)
class ConsentQuestionApplicabilityV1:
    question_id: ConsentQuestionIdV1
    applicability: ConsentApplicability


@dataclass(frozen=True)
class ConsentReadinessV1:
    result: ConsentReadiness
    issues: tuple[ConsentIssueV1, ...]
    applicability: tuple[ConsentQuestionApplicabilityV1, ...]

    @property
    def can_confirm(self) -> bool:
        """Solo habilita este control; no sustituye el resto del lifecycle M3."""
        return self.result == "completo"


def evaluate_consent_assessment_v1(
    assessment: ConsentAssessmentV1 | dict | None,
) -> ConsentReadinessV1:
    """Valida estructura y deriva preparación sin alterar el expediente."""
    if assessment is None:
        return ConsentReadinessV1(
            result="incompleto",
            issues=(
                ConsentIssueV1(
                    "consent_assessment", "expediente_ausente", "incompleto"
                ),
            ),
            applicability=tuple(
                ConsentQuestionApplicabilityV1(question_id, "sin_resolver")
                for question_id in _CONDITIONAL_IDS
            ),
        )

    # Revalidar también instancias mutadas o construidas sin validación.
    payload = (
        assessment.model_dump()
        if isinstance(assessment, ConsentAssessmentV1)
        else assessment
    )
    validated = ConsentAssessmentV1.model_validate(payload)
    answers = {item.question_id: item.answer for item in validated.answers}
    issues: list[ConsentIssueV1] = []

    for field in ("given_by", "grant_method"):
        if getattr(validated, field) is None:
            issues.append(ConsentIssueV1(field, "campo_obligatorio", "incompleto"))

    given_by = validated.given_by
    contract = answers.get("contexto_contrato_servicio")
    applicability = (
        ConsentQuestionApplicabilityV1(
            "mandatario_facultad_expresa",
            (
                "sin_resolver"
                if given_by is None
                else "aplicable" if given_by == "mandatario" else "no_aplicable"
            ),
        ),
        ConsentQuestionApplicabilityV1(
            "tratamiento_necesario_contrato_servicio",
            (
                "aplicable"
                if contract == "si"
                else "no_aplicable" if contract == "no" else "sin_resolver"
            ),
        ),
    )
    conditional = {item.question_id: item.applicability for item in applicability}

    for question_id in _QUESTION_IDS:
        answer = answers.get(question_id)
        applies = conditional.get(question_id, "aplicable")
        code: ConsentIssueCode | None = None
        category: Literal["incompleto", "requiere_revision"] = "incompleto"
        if applies == "sin_resolver":
            code = "aplicabilidad_sin_resolver"
        elif applies == "no_aplicable":
            if answer is not None and answer != "no_aplica":
                code, category = "respuesta_no_aplicable", "requiere_revision"
        elif answer is None:
            code = "pregunta_omitida"
        elif answer == "pendiente":
            code = "respuesta_pendiente"
        elif answer == "no_aplica":
            code = "no_aplica_invalido"
        elif answer == "no" and question_id != "contexto_contrato_servicio":
            code, category = "respuesta_desfavorable", "requiere_revision"
        if code is not None:
            issues.append(
                ConsentIssueV1(f"answers.{question_id}", code, category, question_id)
            )

    for index, evidence in enumerate(validated.evidence):
        if not evidence.evidence_type.strip():
            issues.append(
                ConsentIssueV1(
                    f"evidence.{index}.evidence_type",
                    "tipo_evidencia_vacio",
                    "incompleto",
                )
            )

    result: ConsentReadiness = "completo"
    if any(issue.category == "incompleto" for issue in issues):
        result = "incompleto"
    elif issues:
        result = "requiere_revision"
    return ConsentReadinessV1(result, tuple(issues), applicability)
