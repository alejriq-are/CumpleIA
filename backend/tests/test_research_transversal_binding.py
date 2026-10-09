"""Contratos sucesores puros; sin dispatch ni habilitacion de gates."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.licitud import EipdScreeningV1, SpecialConditionsV1
from app.services import eipd
from app.services import special_conditions as special
from app.services.research_binding import bind_research_assessment_v1
from tests import test_services_research as research_cases

context = research_cases.context


def arguments(kind, rat, lia):
    if kind == "special":
        return [rat, "interes_legitimo_art13d", None, lia, *([None] * 9)]
    return [rat, lia, *([None] * 10)]


def calculate(kind, rat, lia, bound):
    if kind == "special":
        return special.build_special_context_binding_hash_v11(
            *arguments(kind, rat, lia), research=bound
        )
    return eipd.build_eipd_context_binding_hash_v12(
        *arguments(kind, rat, lia),
        legal_basis="interes_legitimo_art13d",
        research=bound,
    )


@pytest.mark.parametrize("kind", ["special", "eipd"])
def test_successor_deterministic_and_preserves_input(context, negative_controls, kind):
    document, rat, lia = context
    bound = bind_research_assessment_v1(document, rat, "interes_legitimo_art13d", lia)
    before = deepcopy((context, bound))
    identity = calculate(kind, rat, lia, bound)
    assert identity == calculate(kind, rat, lia, bound.model_dump(mode="json"))
    assert identity != calculate(kind, rat, lia, None)
    if kind == "special":
        stored = special.bind_special_conditions_v11(
            negative_controls["special_conditions"],
            *arguments(kind, rat, lia),
            research=bound,
        )
        assert stored.context_binding.schema_version == 11
    else:
        stored = eipd.bind_eipd_screening_v12(
            negative_controls["eipd_screening"],
            *arguments(kind, rat, lia),
            legal_basis="interes_legitimo_art13d",
            research=bound,
        )
        assert stored.context_binding.schema_version == 12
    assert stored.context_binding.hash == identity
    assert (context, bound) == before


@pytest.mark.parametrize("kind", ["special", "eipd"])
@pytest.mark.parametrize("changed", ["body", "binding", "rat", "lia"])
def test_material_changes_identity(context, kind, changed):
    document, rat, lia = context
    bound = bind_research_assessment_v1(
        document, rat, "interes_legitimo_art13d", lia
    ).model_dump(mode="json")
    previous = calculate(kind, rat, lia, bound)
    if changed == "body":
        bound["assessment"]["public_interest_analysis"] += " revisado"
    elif changed == "binding":
        bound["context_binding"]["context_hash"] = "a" * 64
    elif changed == "rat":
        rat["purpose"] += " revisada"
    else:
        lia["conclusion"]["balancing_summary"] += " revisada"
    assert calculate(kind, rat, lia, bound) != previous


def test_screening_basis_is_explicit_even_without_documents(context):
    _, rat, lia = context
    args = arguments("eipd", rat, lia)
    first = eipd.build_eipd_context_binding_hash_v12(
        *args, legal_basis="interes_legitimo_art13d"
    )
    second = eipd.build_eipd_context_binding_hash_v12(
        *args, legal_basis="consentimiento_art12"
    )
    assert first != second
    with pytest.raises(ValidationError):
        eipd.build_eipd_context_binding_hash_v12(*args, legal_basis="interes_legitimo")


@pytest.mark.parametrize("kind", ["special", "eipd"])
def test_unknown_research_version_rejected(context, kind):
    document, rat, lia = context
    bound = bind_research_assessment_v1(
        document, rat, "interes_legitimo_art13d", lia
    ).model_dump(mode="json")
    bound["context_binding"]["schema_version"] = 99
    with pytest.raises(ValidationError):
        calculate(kind, rat, lia, bound)


def test_historical_hashes_unchanged(context):
    _, rat, lia = context
    assert (
        special.build_special_context_binding_hash_v10(*arguments("special", rat, lia))
        == "b7f69091c0b733126a1e63a94c557435ffb2c40a7e8ef1067d65f9359113965c"
    )
    assert (
        eipd.build_eipd_context_binding_hash_v11(*arguments("eipd", rat, lia))
        == "b5502ca1e2b9796b54ac1f8b685731710c201bc69d2b58ae3fc9ceab824d42c8"
    )


@pytest.mark.parametrize(
    "model,version", [(SpecialConditionsV1, 11), (EipdScreeningV1, 12)]
)
def test_closed_successor_contracts(model, version):
    model.model_validate(
        {"context_binding": {"schema_version": version, "hash": "a" * 64}}
    )
    for invalid in (
        {"schema_version": 99, "hash": "a" * 64},
        {"schema_version": version, "hash": "a" * 64, "extra": True},
    ):
        with pytest.raises(ValidationError):
            model.model_validate({"context_binding": invalid})
