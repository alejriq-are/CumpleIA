from copy import deepcopy
from inspect import signature

import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    BiometricRightsExceptionAssessmentV1,
    SensitiveRightsExceptionAssessmentV1,
)
from app.services import eipd, special_conditions


@pytest.fixture
def binding_context(complete_lia_context, negative_controls):
    return complete_lia_context[1], negative_controls


def special_args(rat):
    return [rat, "consentimiento_art12"] + [None] * 10


def eipd_args(rat, special=None):
    return [rat, None, special] + [None] * 8


def documents(mode):
    return (
        {} if mode in ("sensitive", "both") else None,
        {} if mode in ("biometric", "both") else None,
    )


def evaluate(kind, control, rat, docs):
    if kind == "special":
        return special_conditions.evaluate_special_conditions_v1(
            control, *special_args(rat), *docs
        )
    return eipd.evaluate_eipd_screening_v1(
        control,
        rat,
        lia=None,
        sensitive_rights_exception=docs[0],
        biometric_rights_exception=docs[1],
    )


@pytest.mark.parametrize(
    "kind,version",
    [("special", n) for n in range(1, 10)] + [("eipd", n) for n in range(1, 11)],
)
@pytest.mark.parametrize("mode", ["none", "sensitive", "biometric", "both"])
def test_historical_binding_exception_coverage(binding_context, kind, version, mode):
    rat, controls = binding_context
    module = special_conditions if kind == "special" else eipd
    name = (
        f"bind_special_conditions_v{version}"
        if kind == "special"
        else f"bind_eipd_screening_v{version}"
    )
    bind = getattr(module, name)
    args = special_args(rat) if kind == "special" else eipd_args(rat)
    control = bind(
        controls["special_conditions" if kind == "special" else "eipd_screening"],
        *args[: len(signature(bind).parameters) - 1],
    )
    before = control.model_dump(mode="json")
    docs = documents(mode)
    result = evaluate(kind, control, rat, docs)
    assert result.context_current == (mode == "none")
    codes = {item.code for item in result.issues}
    expected = set()
    if docs[0] is not None:
        expected.add("asociacion_excepcion_sensible_no_cubierta")
    if docs[1] is not None:
        expected.add("asociacion_excepcion_biometrica_no_cubierta")
    assert {code for code in codes if "asociacion_excepcion" in code} == expected
    assert control.model_dump(mode="json") == before
    assert documents(mode) == docs


@pytest.mark.parametrize("mode", ["none", "sensitive", "biometric", "both"])
def test_latest_bindings_cover_exceptions(binding_context, mode):
    rat, controls = binding_context
    docs = documents(mode)
    before = deepcopy((rat, controls, docs))
    special = special_conditions.bind_special_conditions_v10(
        controls["special_conditions"], *special_args(rat), *docs
    )
    screening = eipd.bind_eipd_screening_v11(
        controls["eipd_screening"], *eipd_args(rat, special), *docs
    )
    assert special.context_binding.schema_version == 10
    assert screening.context_binding.schema_version == 11
    assert evaluate("special", special, rat, docs).context_current
    result = eipd.evaluate_eipd_screening_v1(
        screening,
        rat,
        lia=None,
        special_conditions=special,
        sensitive_rights_exception=docs[0],
        biometric_rights_exception=docs[1],
    )
    assert result.context_current
    assert not any("asociacion_excepcion" in i.code for i in result.issues)
    assert (
        special_conditions.bind_special_conditions_v10(
            controls["special_conditions"], *special_args(rat), *docs
        )
        == special
    )
    assert (rat, controls, docs) == before


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize(
    "mutation", ["add", "remove", "notes", "context", "evidence", "scope", "response"]
)
def test_new_document_mutation_invalidates_both_bindings(
    binding_context, index, mutation
):
    rat, controls = binding_context
    docs = list(documents("both"))
    if mutation == "add":
        docs[index] = None
    special = special_conditions.bind_special_conditions_v10(
        controls["special_conditions"], *special_args(rat), *docs
    )
    screening = eipd.bind_eipd_screening_v11(
        controls["eipd_screening"], *eipd_args(rat, special), *docs
    )
    before = deepcopy(
        (special.model_dump(mode="json"), screening.model_dump(mode="json"), rat)
    )
    changed = deepcopy(docs)
    if mutation == "remove":
        changed[index] = None
    elif mutation == "add":
        changed[index] = {}
    else:
        values = {
            "notes": "Revision",
            "context": {"forum_type": "organo_administrativo"},
            "evidence": [{"evidence_type": "caso", "obtained_on": "2026-10-06"}],
            "scope": {"data_category_codes": ["id"]},
            "response": {"answer": "pendiente"},
        }
        changed[index][
            "exception_conditions_met" if mutation == "response" else mutation
        ] = values[mutation]
    assert not evaluate("special", special, rat, changed).context_current
    assert not eipd.evaluate_eipd_screening_v1(
        screening,
        rat,
        lia=None,
        special_conditions=special,
        sensitive_rights_exception=changed[0],
        biometric_rights_exception=changed[1],
    ).context_current
    new_special = special_conditions.bind_special_conditions_v10(
        controls["special_conditions"], *special_args(rat), *changed
    )
    assert new_special.context_binding.hash != special.context_binding.hash
    # Rebinding special conditions alone does not update EIPD.
    assert not eipd.evaluate_eipd_screening_v1(
        screening,
        rat,
        lia=None,
        special_conditions=new_special,
        sensitive_rights_exception=changed[0],
        biometric_rights_exception=changed[1],
    ).context_current
    new_screening = eipd.bind_eipd_screening_v11(
        controls["eipd_screening"], *eipd_args(rat, new_special), *changed
    )
    assert new_screening.context_binding.hash != screening.context_binding.hash
    assert eipd.evaluate_eipd_screening_v1(
        new_screening,
        rat,
        lia=None,
        special_conditions=new_special,
        sensitive_rights_exception=changed[0],
        biometric_rights_exception=changed[1],
    ).context_current
    assert (
        special.model_dump(mode="json"),
        screening.model_dump(mode="json"),
        rat,
    ) == before


@pytest.mark.parametrize("index", [0, 1])
def test_new_binding_models_match_json_and_revalidate(binding_context, index):
    rat, controls = binding_context
    models = [
        SensitiveRightsExceptionAssessmentV1,
        BiometricRightsExceptionAssessmentV1,
    ]
    docs = [models[0](), models[1]()]
    special = special_conditions.bind_special_conditions_v10(
        controls["special_conditions"], *special_args(rat), *docs
    )
    json_docs = [v.model_dump(mode="json") for v in docs]
    assert special == special_conditions.bind_special_conditions_v10(
        controls["special_conditions"], *special_args(rat), *json_docs
    )
    assert eipd.bind_eipd_screening_v11(
        controls["eipd_screening"], *eipd_args(rat, special), *docs
    ) == eipd.bind_eipd_screening_v11(
        controls["eipd_screening"], *eipd_args(rat, special), *json_docs
    )
    docs[index].exception_basis = "invalid"
    with pytest.raises(ValidationError):
        special_conditions.bind_special_conditions_v10(
            controls["special_conditions"], *special_args(rat), *docs
        )
    with pytest.raises(ValidationError):
        eipd.bind_eipd_screening_v11(
            controls["eipd_screening"], *eipd_args(rat, special), *docs
        )
