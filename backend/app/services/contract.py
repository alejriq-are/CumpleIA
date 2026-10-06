"""Preparación documental contractual; no certifica necesidad jurídica."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import ContractAssessmentV1, RatContextSnapshotV1


@dataclass(frozen=True)
class ContractIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class ContractApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class ContractReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[ContractIssueV1, ...]
    applicability: tuple[ContractApplicabilityV1, ...]

    @property
    def can_confirm(self):
        """Supera solamente preparación contractual, no controles transversales."""
        return self.result == "completo"


def evaluate_contract_assessment_v1(assessment, snapshot):
    from app.services.licitud import canonicalize_text_v1

    contract = (
        ContractAssessmentV1.model_validate(assessment)
        if assessment is not None
        else ContractAssessmentV1()
    )
    rat = (
        RatContextSnapshotV1.model_validate(snapshot) if snapshot is not None else None
    )
    issues = []
    applicability = []

    def issue(field, code, category="incompleto"):
        issues.append(ContractIssueV1(field, code, category))

    def present(value):
        return value is not None and bool(value.strip())

    def text(field):
        if not present(getattr(contract, field)):
            issue(field, "campo_obligatorio")

    def response(field):
        value = getattr(contract, field)
        if value is None:
            issue(field, "respuesta_ausente")
            return
        if value.answer == "pendiente":
            issue(field + ".answer", "respuesta_pendiente")
        elif value.answer == "no":
            issue(field + ".answer", "respuesta_revision", "requiere_revision")
        if not present(value.rationale):
            issue(field + ".rationale", "fundamento_ausente")

    if assessment is None:
        issue("contract_assessment", "expediente_ausente")
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    else:
        if rat.organization_role != "responsable":
            issue(
                "rat_context_snapshot.organization_role",
                "rol_no_admitido",
                "requiere_revision",
            )
        if present(contract.purpose_description) and canonicalize_text_v1(
            contract.purpose_description
        ) != canonicalize_text_v1(rat.purpose):
            issue("purpose_description", "finalidad_distinta", "requiere_revision")
    if contract.route is None:
        issue("route", "ruta_ausente")
    for field in (
        "purpose_description",
        "relationship_description",
        "contractual_object",
        "processing_operations",
        "necessity_analysis",
        "data_minimization_analysis",
    ):
        text(field)
    for field in ("holder_is_party", "necessary_for_route", "purpose_within_route"):
        response(field)
    for field in (
        "contractual_reference",
        "precontractual_measures",
        "requested_by_holder",
        "request_reference",
    ):
        applies = (
            None
            if contract.route is None
            else (
                contract.route != "medidas_precontractuales"
                if field == "contractual_reference"
                else contract.route == "medidas_precontractuales"
            )
        )
        state = (
            "sin_resolver"
            if applies is None
            else "aplicable" if applies else "no_aplicable"
        )
        applicability.append(ContractApplicabilityV1(field, state))
        value = getattr(contract, field)
        if applies:
            response(field) if field == "requested_by_holder" else text(field)
        elif applies is False and (
            value is not None if field == "requested_by_holder" else present(value)
        ):
            # Una referencia de contrato/proyecto puede apoyar también medidas
            # previas; no se exige, pero no es una respuesta residual incoherente.
            if field != "contractual_reference":
                issue(field, "campo_residual", "requiere_revision")
    if not contract.evidence:
        issue("evidence", "evidencia_ausente")
    for index, item in enumerate(contract.evidence):
        for field in ("evidence_type", "reference"):
            if not present(getattr(item, field)):
                issue(f"evidence.{index}.{field}", "evidencia_incompleta")

    def order(item):
        parts = item.field.split(".")
        if parts[0] == "rat_context_snapshot":
            return (0, 0, 0, 0)
        if parts[0] == "contract_assessment":
            return (1, 0, 0, 0)
        field_index = list(ContractAssessmentV1.model_fields).index(parts[0])
        if parts[0] == "evidence" and len(parts) > 1:
            return (
                2,
                field_index,
                int(parts[1]),
                0 if parts[2] == "evidence_type" else 1,
            )
        return (2, field_index, 0, 0 if len(parts) == 1 or parts[1] == "answer" else 1)

    issues.sort(key=order)
    result = (
        "incompleto"
        if any(i.category == "incompleto" for i in issues)
        else "requiere_revision" if issues else "completo"
    )
    return ContractReadinessV1(result, tuple(issues), tuple(applicability))
