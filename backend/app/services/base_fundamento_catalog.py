"""Versioned documentary criteria for the 5D.1 pilot."""

from collections.abc import Callable
from dataclasses import asdict, dataclass

from pydantic import ValidationError

from app.services.consentimiento import evaluate_consent_assessment_v1
from app.services.contract import evaluate_contract_assessment_v1
from app.services.economic_obligations import (
    evaluate_economic_obligations_assessment_v1,
)
from app.services.legal_obligation import evaluate_legal_obligation_assessment_v1
from app.services.lia import evaluate_lia_assessment_v1
from app.services.rights_defense import evaluate_rights_defense_assessment_v1

CATALOG_VERSION = "cumpleia.base_fundamento.v1"
COVERAGE_PENDING = ("FORM-R01", "FORM-R02", "FORM-R03", "FORM-R04", "FORM-R05")


@dataclass(frozen=True)
class Criterion:
    id: str
    label: str
    fields: tuple[str, ...]


COMMON = (
    Criterion("base.definida", "Base de licitud definida", ("legal_basis",)),
    Criterion(
        "base.fundamento", "Fundamento vinculado a la finalidad", ("justification",)
    ),
    Criterion(
        "base.alcance",
        "Finalidad y alcance RAT identificados",
        ("purpose_snapshot", "rat_context_snapshot"),
    ),
)
BACKUP = Criterion("base.respaldo", "Respaldo verificable", ("evidence",))


def consent(document, _snapshot):
    return evaluate_consent_assessment_v1(document)


@dataclass(frozen=True)
class Basis:
    form: str
    evaluate: Callable
    criteria: tuple[Criterion, ...]


BASES = {
    "consentimiento_art12": Basis(
        "consent_assessment",
        consent,
        (
            Criterion(
                "consentimiento.otorgamiento",
                "Persona que otorgó y mecanismo",
                ("given_by", "grant_method"),
            ),
            Criterion(
                "consentimiento.alcance",
                "Información, finalidad y manifestación de voluntad",
                (
                    "answers.consentimiento_libre",
                    "answers.consentimiento_informado",
                    "answers.consentimiento_especifico_finalidad",
                    "answers.consentimiento_previo",
                    "answers.voluntad_inequivoca",
                    "answers.accion_afirmativa_clara",
                ),
            ),
            Criterion(
                "consentimiento.retiro",
                "Retiro del consentimiento",
                (
                    "answers.revocacion_posible",
                    "answers.revocacion_medio_equivalente",
                    "answers.revocacion_expedita",
                    "answers.revocacion_fidedigna",
                    "answers.revocacion_gratuita",
                    "answers.revocacion_disponible_permanentemente",
                ),
            ),
            Criterion(
                "consentimiento.acreditacion",
                "Acreditación y representación",
                (
                    "answers.responsable_puede_acreditar",
                    "answers.mandatario_facultad_expresa",
                ),
            ),
            Criterion(
                "consentimiento.contrato",
                "Contexto contractual del consentimiento",
                (
                    "answers.contexto_contrato_servicio",
                    "answers.tratamiento_necesario_contrato_servicio",
                ),
            ),
        ),
    ),
    "obligaciones_economicas_art13a": Basis(
        "economic_obligations_assessment",
        evaluate_economic_obligations_assessment_v1,
        (
            Criterion(
                "economica.obligacion",
                "Obligación y vínculo con el titular",
                (
                    "obligation_type",
                    "obligation_description",
                    "obligation_reference",
                    "holder_connection_analysis",
                    "related_to_obligation",
                ),
            ),
            Criterion(
                "economica.reglas",
                "Reglas aplicables y controles de datos",
                (
                    "normative_references",
                    "applicability_analysis",
                    "title_iii_analysis",
                    "title_iii_reviewed",
                    "processing_within_title_iii",
                    "retention_and_deletion_analysis",
                    "retention_and_deletion_compatible",
                    "accuracy_and_update_analysis",
                    "accuracy_controls_documented",
                    "data_minimization_analysis",
                ),
            ),
            Criterion(
                "economica.comunicacion",
                "Comunicación y sus condiciones",
                (
                    "route",
                    "operations_include_communication",
                    "communication_scope",
                    "communication_eligibility_analysis",
                    "communication_restrictions_analysis",
                    "payment_and_extinction_controls",
                    "communication_permitted",
                    "excluded_data_screened",
                    "communication_limits_respected",
                ),
            ),
        ),
    ),
    "obligacion_legal_art13b": Basis(
        "legal_obligation_assessment",
        evaluate_legal_obligation_assessment_v1,
        (
            Criterion(
                "legal.norma",
                "Norma, vigencia y alcance",
                (
                    "route",
                    "normative_references",
                    "normative_requirement_description",
                    "normative_basis_reviewed",
                    "normative_basis_in_force",
                    "processing_within_legal_scope",
                    "obligation_applies_to_controller",
                    "processing_required_by_law",
                    "applicability_analysis",
                ),
            ),
            Criterion(
                "legal.necesidad",
                "Necesidad y minimización",
                ("necessity_analysis", "data_minimization_analysis"),
            ),
        ),
    ),
    "contrato_precontractual_art13c": Basis(
        "contract_assessment",
        evaluate_contract_assessment_v1,
        (
            Criterion(
                "contrato.relacion",
                "Ruta, relación y vínculo contractual",
                (
                    "route",
                    "relationship_description",
                    "contractual_reference",
                    "contractual_object",
                    "holder_is_party",
                ),
            ),
            Criterion(
                "contrato.necesidad",
                "Necesidad y minimización en la ruta",
                (
                    "necessity_analysis",
                    "data_minimization_analysis",
                    "necessary_for_route",
                    "purpose_within_route",
                ),
            ),
            Criterion(
                "contrato.solicitud",
                "Solicitud y medidas precontractuales",
                (
                    "precontractual_measures",
                    "requested_by_holder",
                    "request_reference",
                ),
            ),
        ),
    ),
    "interes_legitimo_art13d": Basis(
        "lia_assessment",
        evaluate_lia_assessment_v1,
        (
            Criterion(
                "lia.interes",
                "Interés identificado y su titular",
                ("purpose_and_interest",),
            ),
            Criterion("lia.necesidad", "Necesidad y proporcionalidad", ("necessity",)),
            Criterion(
                "lia.expectativas",
                "Contexto y expectativas de los titulares",
                ("nature_and_scope", "reasonable_expectations"),
            ),
            Criterion(
                "lia.impacto", "Impacto y salvaguardas", ("impact", "safeguards")
            ),
            Criterion(
                "lia.transparencia",
                "Información y oposición",
                ("transparency_and_opposition",),
            ),
            Criterion("lia.ponderacion", "Ponderación y conclusión", ("conclusion",)),
        ),
    ),
    "defensa_derechos_art13e": Basis(
        "rights_defense_assessment",
        evaluate_rights_defense_assessment_v1,
        (
            Criterion(
                "derechos.vinculo",
                "Derecho, titular y vínculo",
                (
                    "route",
                    "right_holder",
                    "right_description",
                    "right_basis_reference",
                    "holder_connection_analysis",
                    "related_to_right",
                ),
            ),
            Criterion(
                "derechos.etapa",
                "Foro, etapa y antecedentes",
                (
                    "forum_type",
                    "forum_description",
                    "proceeding_stage",
                    "within_forum_scope",
                    "proceeding_reference",
                    "preparatory_actions",
                    "post_proceeding_necessity_analysis",
                ),
            ),
            Criterion(
                "derechos.necesidad",
                "Necesidad y minimización",
                (
                    "necessity_analysis",
                    "data_minimization_analysis",
                    "necessary_for_route",
                ),
            ),
        ),
    ),
}


def _issue(field: str, code: str) -> dict:
    return {"field": field, "code": code, "category": "incompleto"}


def _criterion_for(field: str, criteria: tuple[Criterion, ...]) -> str | None:
    for criterion in criteria:
        if any(
            field == path or field.startswith(path + ".") for path in criterion.fields
        ):
            return criterion.id
    return None


def evaluate_base_document(
    *,
    legal_basis: str | None,
    justification: str | None,
    purpose: str | None,
    snapshot: dict | None,
    document: dict | None,
) -> dict:
    """Build the diagnosis to freeze with the exact saved documentary material."""
    criteria = COMMON
    findings = []
    applicability = []
    evaluator_result = None
    if not justification or not justification.strip():
        findings.append(_issue("justification", "fundamento_ausente"))
    if not purpose or not purpose.strip():
        findings.append(_issue("purpose_snapshot", "finalidad_ausente"))
    for field in ("data_categories", "data_subjects", "organization_role"):
        if not snapshot or not snapshot.get(field):
            findings.append(
                _issue("rat_context_snapshot." + field, "alcance_incompleto")
            )

    basis = BASES.get(legal_basis)
    if basis is None:
        findings.append(
            _issue(
                "legal_basis",
                "base_pendiente" if legal_basis is None else "base_no_reconocida",
            )
        )
    else:
        criteria += (
            Criterion("base.formulario", "Formulario principal", (basis.form,)),
            Criterion(
                "base.operacion",
                "Finalidad y operaciones del formulario",
                ("purpose_description", "processing_operations"),
            ),
            BACKUP,
        ) + basis.criteria
        try:
            diagnostic = basis.evaluate(document, snapshot)
        except ValidationError:
            findings.append(_issue(basis.form, "formulario_o_alcance_incompatible"))
        else:
            evaluator_result = diagnostic.result
            findings.extend(asdict(issue) for issue in diagnostic.issues)
            for item in diagnostic.applicability:
                data = asdict(item)
                field = (
                    data["field"]
                    if "field" in data
                    else "answers." + data["question_id"]
                )
                applicability.append(
                    {
                        "field": field,
                        "criterion_id": _criterion_for(field, criteria),
                        "applicability": data["applicability"],
                    }
                )
        if (
            legal_basis == "consentimiento_art12"
            and document
            and not any(
                isinstance(evidence, dict)
                and isinstance(evidence.get("reference"), str)
                and evidence["reference"].strip()
                for evidence in (document.get("evidence") or [])
            )
        ):
            findings.append(_issue("evidence", "referencia_de_respaldo_ausente"))

    for finding in findings:
        criterion_id = _criterion_for(finding["field"], criteria)
        finding["criterion_id"] = criterion_id
        finding["classification"] = "esencial" if criterion_id else "sin_clasificar"
    return {
        "rule_set": CATALOG_VERSION,
        "legal_basis": legal_basis,
        "primary_form": basis.form if basis else None,
        "evaluator_result": evaluator_result,
        "criteria": [{"id": item.id, "label": item.label} for item in criteria],
        "findings": findings,
        "applicability": applicability,
        "coverage_pending": list(COVERAGE_PENDING),
    }


EQUIVALENT_EVIDENCE_CODES = frozenset(
    {
        "evidencia_ausente",
        "evidencia_incompleta",
        "tipo_evidencia_vacio",
        "referencia_de_respaldo_ausente",
    }
)


def favorable_requirements(bundle):
    """Describe the required resolutions without changing the frozen diagnosis."""
    diagnostic = bundle.get("diagnostic", {})
    if (
        diagnostic.get("rule_set") != CATALOG_VERSION
        or (
            diagnostic.get("legal_basis") is not None
            and diagnostic["legal_basis"] not in BASES
        )
        or not isinstance(diagnostic.get("findings"), list)
        or not isinstance(diagnostic.get("applicability"), list)
    ):
        return [
            {
                "criterion_id": None,
                "field": "diagnostic",
                "code": "diagnostico_no_habilitado",
                "resolution": None,
            }
        ]
    if diagnostic.get("legal_basis") is None and not any(
        finding.get("code") == "base_pendiente" for finding in diagnostic["findings"]
    ):
        return [
            {
                "criterion_id": "base.definida",
                "field": "legal_basis",
                "code": "base_pendiente",
                "resolution": None,
            }
        ]
    requirements = []
    for finding in diagnostic["findings"]:
        equivalent = (
            finding["criterion_id"] == "base.respaldo"
            and finding["code"] in EQUIVALENT_EVIDENCE_CODES
        )
        requirements.append(
            {
                "criterion_id": finding["criterion_id"],
                "field": finding["field"],
                "code": finding["code"],
                "resolution": "respaldo_equivalente" if equivalent else None,
            }
        )
    for item in diagnostic["applicability"]:
        if item["applicability"] == "aplicable" and item["criterion_id"] is not None:
            continue
        requirements.append(
            {
                "criterion_id": item["criterion_id"],
                "field": item["field"],
                "code": "aplicabilidad",
                "resolution": (
                    "no_aplica"
                    if item["criterion_id"] and item["applicability"] == "no_aplicable"
                    else None
                ),
            }
        )
    return requirements
