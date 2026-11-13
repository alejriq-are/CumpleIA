from copy import deepcopy
from dataclasses import FrozenInstanceError
from typing import get_args

import pytest
from pydantic import ValidationError

from app.schemas.licitud import EipdQuestionIdV1, LegalBasis
from app.services.eipd import bind_eipd_screening_v11
from app.services.eipd_frontier import evaluate_eipd_frontier_v1
from app.services.eipd_resolution import EipdResolutionContextV1
from app.services.special_conditions import bind_special_conditions_v10

SPECIAL_FIELDS = (
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


def rebind(ctx):
    special = deepcopy(ctx["special_conditions"])
    special.pop("context_binding", None)
    ctx["special_conditions"] = bind_special_conditions_v10(
        special,
        ctx["rat_context_snapshot"],
        ctx["legal_basis"],
        *(ctx[f] for f in SPECIAL_FIELDS),
    ).model_dump(mode="json")
    screening = deepcopy(ctx["eipd_screening"])
    screening.pop("context_binding", None)
    ctx["eipd_screening"] = bind_eipd_screening_v11(
        screening,
        ctx["rat_context_snapshot"],
        ctx["lia_assessment"],
        ctx["special_conditions"],
        *(ctx[f] for f in SPECIAL_FIELDS[2:]),
    ).model_dump(mode="json")
    return ctx


@pytest.fixture(params=["sensitive", "biometric"])
def frontier_context(
    request, sensitive_exception_context, biometric_exception_context, negative_controls
):
    ctx = {f: None for f in EipdResolutionContextV1.model_fields}
    if request.param == "sensitive":
        sensitive, rat, special = deepcopy(sensitive_exception_context)
    else:
        biometric, rat, special, sensitive = deepcopy(biometric_exception_context)
        ctx["biometric_rights_exception_assessment"] = biometric
    ctx.update(
        rat_context_snapshot=rat,
        legal_basis="contrato_precontractual_art13c",
        sensitive_rights_exception_assessment=sensitive,
        special_conditions=special,
        eipd_screening=deepcopy(negative_controls["eipd_screening"]),
    )
    for answer in ctx["eipd_screening"]["answers"]:
        if answer["question_id"] == "datos_protegidos_excepcion_consentimiento":
            answer.update(answer="si", rationale="Excepcion de derechos documentada")
    return rebind(ctx)


def codes(result):
    return {i.code for i in result.issues}


def test_supported_preparation_preserves_v1_positive_without_approval(frontier_context):
    before = deepcopy(frontier_context)
    result = evaluate_eipd_frontier_v1(frontier_context)
    assert result.is_frontier_prepared, result.issues
    expected = (
        "sensible_biometrica_derechos"
        if frontier_context["biometric_rights_exception_assessment"]
        else "sensible_derechos"
    )
    assert result.route == expected
    assert result.screening.result == "pendiente_revision"
    assert any(
        i.category == "supuesto_declarado"
        and i.question_id == "datos_protegidos_excepcion_consentimiento"
        for i in result.screening.issues
    )
    assert any(
        i.code == "excepcion_especial_no_validada" for i in result.screening.issues
    )
    assert not hasattr(result, "can_confirm")
    assert frontier_context == before
    assert (
        evaluate_eipd_frontier_v1(
            EipdResolutionContextV1.model_validate(frontier_context)
        )
        == result
    )
    with pytest.raises(FrozenInstanceError):
        result.result = "preparado"


@pytest.mark.parametrize("question", get_args(EipdQuestionIdV1))
@pytest.mark.parametrize("mode", ["missing", "pending", "blank", "opposite"])
def test_every_screening_answer_and_rationale(frontier_context, question, mode):
    answers = frontier_context["eipd_screening"]["answers"]
    answer = next(a for a in answers if a["question_id"] == question)
    if mode == "missing":
        answers.remove(answer)
    elif mode == "pending":
        answer["answer"] = "pendiente"
    elif mode == "blank":
        answer["rationale"] = " "
    else:
        answer["answer"] = (
            "no" if question == "datos_protegidos_excepcion_consentimiento" else "si"
        )
    result = evaluate_eipd_frontier_v1(rebind(frontier_context))
    assert not result.is_frontier_prepared
    assert result.result == (
        "requiere_revision" if mode == "opposite" else "incompleto"
    )
    assert any(i.question_id == question for i in result.issues)


@pytest.mark.parametrize("role", [None, "encargado"])
def test_role_fixed_without_clock_or_activation_date(frontier_context, role):
    frontier_context["rat_context_snapshot"]["organization_role"] = role
    result = evaluate_eipd_frontier_v1(rebind(frontier_context))
    assert not result.is_frontier_prepared
    assert (
        "rol_ausente" in codes(result)
        if role is None
        else "rol_fuera_frontera" in codes(result)
    )


@pytest.mark.parametrize(
    "field",
    ["special_conditions", "eipd_screening", "sensitive_rights_exception_assessment"],
)
def test_missing_dependencies(frontier_context, field):
    frontier_context[field] = None
    if field == "sensitive_rights_exception_assessment":
        rebind(frontier_context)
    result = evaluate_eipd_frontier_v1(frontier_context)
    assert not result.is_frontier_prepared
    assert result.issues


@pytest.mark.parametrize("field", ["special_conditions", "eipd_screening"])
def test_stale_association_is_not_repaired(frontier_context, field):
    frontier_context[field]["context_binding"]["hash"] = "a" * 64
    before = deepcopy(frontier_context)
    result = evaluate_eipd_frontier_v1(frontier_context)
    assert result.result == "requiere_revision"
    assert not result.is_frontier_prepared
    assert frontier_context == before


def test_missing_biometric_dependency(biometric_exception_context, negative_controls):
    biometric, rat, special, sensitive = deepcopy(biometric_exception_context)
    ctx = {f: None for f in EipdResolutionContextV1.model_fields}
    ctx.update(
        rat_context_snapshot=rat,
        legal_basis="contrato_precontractual_art13c",
        special_conditions=special,
        sensitive_rights_exception_assessment=sensitive,
        eipd_screening=deepcopy(negative_controls["eipd_screening"]),
    )
    result = evaluate_eipd_frontier_v1(rebind(ctx))
    assert not result.is_frontier_prepared
    assert any("biometric" in i.field for i in result.issues)


@pytest.mark.parametrize(
    "field",
    [
        "health_assessment",
        "biometric_assessment",
        "sensitive_consent_assessment",
        "geolocation_assessment",
    ],
)
def test_residual_documents(frontier_context, field):
    frontier_context[field] = {}
    result = evaluate_eipd_frontier_v1(rebind(frontier_context))
    assert result.result == "requiere_revision"
    assert any(
        i.field == field and i.code == "expediente_fuera_frontera"
        for i in result.issues
    )


def test_all_motives_retained_with_revision_precedence(frontier_context):
    frontier_context["rat_context_snapshot"]["organization_role"] = "encargado"
    frontier_context["eipd_screening"]["answers"][0]["rationale"] = None
    result = evaluate_eipd_frontier_v1(rebind(frontier_context))
    assert result.result == "requiere_revision"
    assert {"rol_fuera_frontera", "fundamento_ausente"} <= codes(result)
    assert len(result.issues) == len(set(result.issues))
    assert result == evaluate_eipd_frontier_v1(frontier_context)


def test_missing_context_is_incomplete():
    result = evaluate_eipd_frontier_v1(None)
    assert result.result == "incompleto" and result.route == "sin_resolver"
    assert result.screening is None and result.special is None


@pytest.mark.parametrize(
    "extra", ["approved", "sources_verified", "frontier_prepared", "effective_date"]
)
def test_internal_context_closed(frontier_context, extra):
    frontier_context[extra] = True
    with pytest.raises(ValidationError):
        evaluate_eipd_frontier_v1(frontier_context)


@pytest.mark.parametrize("basis", get_args(LegalBasis))
def test_ordinary_basis_is_independent(frontier_context, basis):
    frontier_context["legal_basis"] = basis
    result = evaluate_eipd_frontier_v1(rebind(frontier_context))
    assert result.is_frontier_prepared, result.issues
    # Preparacion de frontera no evalua expediente ordinario ausente.
    assert not hasattr(result, "can_confirm")


@pytest.mark.parametrize("route", [None, "consentimiento", "regla_especifica"])
def test_other_authorization_routes(frontier_context, route):
    condition = next(
        c
        for c in frontier_context["special_conditions"]["conditions"]
        if c["regime_id"] == "sensibles_art16"
    )
    condition["authorization_route"] = route
    result = evaluate_eipd_frontier_v1(rebind(frontier_context))
    assert not result.is_frontier_prepared
    assert (
        "ruta_ausente" in codes(result)
        if route is None
        else "ruta_fuera_frontera" in codes(result)
    )


@pytest.mark.parametrize(
    "question",
    [
        "geolocalizacion",
        "salud_perfil_biologico",
        "fines_historicos_estadisticos_cientificos_investigacion",
    ],
)
def test_mixed_regimes_outside_first_support(frontier_context, question):
    declaration = next(
        d
        for d in frontier_context["special_conditions"]["declarations"]
        if d["question_id"] == question
    )
    declaration.update(
        answer="si",
        rationale="Otro regimen declarado",
        data_category_codes=["id"],
        data_subject_codes=["clientes"],
    )
    result = evaluate_eipd_frontier_v1(rebind(frontier_context))
    assert result.result == "requiere_revision"
    assert "regimen_fuera_frontera" in codes(result)


@pytest.mark.parametrize(
    "field,old_version", [("special_conditions", 9), ("eipd_screening", 10)]
)
def test_older_bindings_cannot_cover_new_exceptions(
    frontier_context, field, old_version
):
    frontier_context[field]["context_binding"]["schema_version"] = old_version
    result = evaluate_eipd_frontier_v1(frontier_context)
    assert result.result == "requiere_revision"
    assert not result.is_frontier_prepared


def test_mutated_model_revalidated(frontier_context):
    ctx = EipdResolutionContextV1.model_validate(frontier_context)
    ctx.rat_context_snapshot.organization_role = "inventado"
    with pytest.raises(ValidationError):
        evaluate_eipd_frontier_v1(ctx)
