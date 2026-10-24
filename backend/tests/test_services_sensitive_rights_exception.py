from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    RatContextSnapshotV1,
    SensitiveRightsExceptionAssessmentV1,
    SpecialConditionsV1,
)
from app.services.sensitive_rights_exception import (
    evaluate_sensitive_rights_exception_v1 as evaluate,
)

CONTEXT_TEXTS = [
    "context_reference",
    "purpose_description",
    "right_description",
    "right_basis_reference",
    "holder_connection_analysis",
    "forum_description",
    "proceeding_reference",
    "processing_operations",
    "necessity_analysis",
    "data_minimization_analysis",
    "safeguards_analysis",
]
OWN_TEXTS = ["sensitive_data_description", "exception_application_analysis"]
RESPONSES = [
    "context.related_to_right",
    "context.necessary_for_route",
    "context.within_forum_scope",
    "context.principles_addressed",
    "exception_conditions_met",
]


def parent(document, path):
    parts = path.split(".")
    for part in parts[:-1]:
        document = document[part]
    return document, parts[-1]


def issue_set(result):
    return {(i.field, i.code, i.category) for i in result.issues}


def test_sensitive_exception_complete_without_consent_or_ordinary_rights(
    sensitive_exception_context,
):
    before = deepcopy(sensitive_exception_context)
    result = evaluate(*sensitive_exception_context)
    assert result.result == "completo" and result.can_confirm
    assert result.issues == ()
    assert {a.field: a.applicability for a in result.applicability}[
        "context.preparatory_actions"
    ] == "no_aplicable"
    assert sensitive_exception_context == before
    assert evaluate(*sensitive_exception_context) == result
    with pytest.raises(FrozenInstanceError):
        result.result = "incompleto"
    with pytest.raises(FrozenInstanceError):
        result.applicability[0].applicability = "sin_resolver"


@pytest.mark.parametrize(
    "route", ["formulacion_derecho", "ejercicio_derecho", "defensa_derecho"]
)
@pytest.mark.parametrize("forum", ["tribunal_justicia", "organo_administrativo"])
@pytest.mark.parametrize("stage", ["preparacion", "en_curso", "finalizado"])
def test_supported_routes_forums_stages(
    sensitive_exception_context, route, forum, stage
):
    document, _, _ = sensitive_exception_context
    document["context"].update(route=route, forum_type=forum, proceeding_stage=stage)
    if stage == "preparacion":
        document["context"]["preparatory_actions"] = "Actuaciones de preparacion"
    elif stage == "finalizado":
        document["context"][
            "post_proceeding_necessity_analysis"
        ] = "Necesidad posterior documentada"
    result = evaluate(*sensitive_exception_context)
    assert result.can_confirm and not result.issues


@pytest.mark.parametrize("holder", ["responsable", "tercero", "ambos"])
def test_supported_holder_with_documented_connection(
    sensitive_exception_context, holder
):
    sensitive_exception_context[0]["context"]["right_holder"] = holder
    assert evaluate(*sensitive_exception_context).can_confirm


@pytest.mark.parametrize("field", ["context." + f for f in CONTEXT_TEXTS] + OWN_TEXTS)
@pytest.mark.parametrize("value", [None, "", " "])
def test_required_texts(sensitive_exception_context, field, value):
    document, _, _ = sensitive_exception_context
    target, name = parent(document, field)
    target[name] = value
    result = evaluate(*sensitive_exception_context)
    assert result.result == "incompleto"
    assert (field, "campo_obligatorio", "incompleto") in issue_set(result)
    assert {a.field: a.applicability for a in result.applicability}[
        field
    ] == "aplicable"


@pytest.mark.parametrize(
    "field",
    [
        "exception_basis",
        "context.route",
        "context.right_holder",
        "context.forum_type",
        "context.proceeding_stage",
    ],
)
def test_required_enums(sensitive_exception_context, field):
    target, name = parent(sensitive_exception_context[0], field)
    target[name] = None
    result = evaluate(*sensitive_exception_context)
    assert (field, "campo_obligatorio", "incompleto") in issue_set(result)


@pytest.mark.parametrize("field", RESPONSES)
@pytest.mark.parametrize(
    "value,code,category",
    [
        (None, "respuesta_ausente", "incompleto"),
        (
            {"answer": "pendiente", "rationale": "En revision"},
            "respuesta_pendiente",
            "incompleto",
        ),
        (
            {"answer": "no", "rationale": "No se acredita"},
            "respuesta_revision",
            "requiere_revision",
        ),
        ({"answer": "si", "rationale": None}, "fundamento_ausente", "incompleto"),
        ({"answer": "si", "rationale": " "}, "fundamento_ausente", "incompleto"),
    ],
)
def test_required_responses(sensitive_exception_context, field, value, code, category):
    target, name = parent(sensitive_exception_context[0], field)
    target[name] = value
    result = evaluate(*sensitive_exception_context)
    assert result.result == category
    suffix = (
        ""
        if code == "respuesta_ausente"
        else ".rationale" if code == "fundamento_ausente" else ".answer"
    )
    assert (field + suffix, code, category) in issue_set(result)


@pytest.mark.parametrize(
    "field,stage",
    [
        ("preparatory_actions", "preparacion"),
        ("post_proceeding_necessity_analysis", "finalizado"),
    ],
)
@pytest.mark.parametrize("value", [None, "", " "])
def test_applicable_stage_text_required(
    sensitive_exception_context, field, stage, value
):
    context = sensitive_exception_context[0]["context"]
    context.update(proceeding_stage=stage)
    context[field] = value
    result = evaluate(*sensitive_exception_context)
    assert ("context." + field, "campo_obligatorio", "incompleto") in issue_set(result)
    assert {a.field: a.applicability for a in result.applicability}[
        "context." + field
    ] == "aplicable"


@pytest.mark.parametrize(
    "field,stage",
    [
        ("preparatory_actions", "en_curso"),
        ("preparatory_actions", "finalizado"),
        ("post_proceeding_necessity_analysis", "en_curso"),
        ("post_proceeding_necessity_analysis", "preparacion"),
    ],
)
def test_stage_residuality(sensitive_exception_context, field, stage):
    context = sensitive_exception_context[0]["context"]
    context["proceeding_stage"] = stage
    if stage == "preparacion":
        context["preparatory_actions"] = "Preparacion"
    elif stage == "finalizado":
        context["post_proceeding_necessity_analysis"] = "Necesidad posterior"
    context[field] = "Texto residual"
    result = evaluate(*sensitive_exception_context)
    assert result.result == "requiere_revision"
    assert ("context." + field, "campo_residual", "requiere_revision") in issue_set(
        result
    )


@pytest.mark.parametrize("texts", [False, True])
def test_unresolved_stage_does_not_infer_conditional_applicability(
    sensitive_exception_context, texts
):
    context = sensitive_exception_context[0]["context"]
    context["proceeding_stage"] = None
    if texts:
        context.update(
            preparatory_actions="Preparacion",
            post_proceeding_necessity_analysis="Necesidad posterior",
        )
    result = evaluate(*sensitive_exception_context)
    for field in (
        "context.preparatory_actions",
        "context.post_proceeding_necessity_analysis",
    ):
        assert {a.field: a.applicability for a in result.applicability}[
            field
        ] == "sin_resolver"
        assert not any(i.field == field for i in result.issues)
    assert result.result == "incompleto"


@pytest.mark.parametrize("place", ["document", "context", "condition"])
@pytest.mark.parametrize("missing", ["list", "evidence_type", "reference"])
def test_required_evidence(sensitive_exception_context, place, missing):
    document, _, special = sensitive_exception_context
    target = (
        document
        if place == "document"
        else document["context"] if place == "context" else special["conditions"][0]
    )
    if missing == "list":
        target["evidence"] = []
    else:
        target["evidence"][0][missing] = " "
    result = evaluate(*sensitive_exception_context)
    assert result.result == "incompleto"
    assert any(
        i.code == ("evidencia_ausente" if missing == "list" else "evidencia_incompleta")
        for i in result.issues
    )


@pytest.mark.parametrize("place", ["document", "declaration", "condition"])
@pytest.mark.parametrize(
    "field,valid", [("data_category_codes", "id"), ("data_subject_codes", "clientes")]
)
@pytest.mark.parametrize(
    "values,expected",
    [
        ([], "incompleto"),
        (["missing"], "requiere_revision"),
        ([" "], "invalid_contract"),
        (["VALID", " VALID "], "requiere_revision"),
    ],
)
def test_scope_empty_invalid_or_duplicate(
    sensitive_exception_context, place, field, valid, values, expected
):
    document, _, special = sensitive_exception_context
    target = (
        document["scope"]
        if place == "document"
        else (
            next(
                d
                for d in special["declarations"]
                if d["question_id"] == "datos_sensibles"
            )
            if place == "declaration"
            else special["conditions"][0]
        )
    )
    target[field] = [v.replace("VALID", valid.upper()) for v in values]
    if expected == "invalid_contract":
        with pytest.raises(ValidationError):
            evaluate(*sensitive_exception_context)
        return
    result = evaluate(*sensitive_exception_context)
    assert result.result == expected
    assert any(
        i.code == ("alcance_vacio" if not values else "alcance_invalido")
        for i in result.issues
    )


@pytest.mark.parametrize("field", ["data_category_codes", "data_subject_codes"])
def test_scope_partial_coverage_and_discordance(sensitive_exception_context, field):
    document, rat, special = sensitive_exception_context
    if field == "data_category_codes":
        extra = deepcopy(rat["data_categories"][0])
        extra["category_code"] = "otra"
        rat["data_categories"].append(extra)
    else:
        extra = deepcopy(rat["data_subjects"][0])
        extra["category_code"] = "otros"
        rat["data_subjects"].append(extra)
    result = evaluate(*sensitive_exception_context)
    assert result.result == "requiere_revision"
    assert sum(i.code == "cobertura_sensible_incompleta" for i in result.issues) == 3
    document["scope"][field].append(extra["category_code"])
    assert any(
        i.code == "alcance_discordante"
        for i in evaluate(*sensitive_exception_context).issues
    )
    next(d for d in special["declarations"] if d["question_id"] == "datos_sensibles")[
        field
    ].append(extra["category_code"])
    special["conditions"][0][field].append(extra["category_code"])
    assert evaluate(*sensitive_exception_context).can_confirm


def test_scope_canonization_and_nonsensitive_exclusion(sensitive_exception_context):
    document, rat, special = sensitive_exception_context
    extra = deepcopy(rat["data_categories"][0])
    extra.update(category_code="publica", is_sensitive=False)
    rat["data_categories"].append(extra)
    document["context"]["purpose_description"] = "  GESTIÓN  DE CLIENTES  "
    document["scope"].update(
        data_category_codes=[" ID "], data_subject_codes=[" CLIENTES "]
    )
    assert evaluate(*sensitive_exception_context).can_confirm
    document["scope"]["data_category_codes"].append("publica")
    assert evaluate(*sensitive_exception_context).result == "requiere_revision"


@pytest.mark.parametrize(
    "field,missing,mismatch",
    [
        ("authorization_route", None, "consentimiento"),
        ("sensitive_condition_id", None, "consentimiento_expreso_art16"),
        ("uses_consent_assessment", None, True),
    ],
)
@pytest.mark.parametrize("mode", ["missing", "mismatch"])
def test_exception_condition_coherence(
    sensitive_exception_context, field, missing, mismatch, mode
):
    sensitive_exception_context[2]["conditions"][0][field] = (
        missing if mode == "missing" else mismatch
    )
    result = evaluate(*sensitive_exception_context)
    assert result.result == ("incompleto" if mode == "missing" else "requiere_revision")
    assert any(
        i.field.endswith("." + field) and i.question_id == "datos_sensibles"
        for i in result.issues
    )


@pytest.mark.parametrize(
    "change,expected",
    [
        ("absent", "incompleto"),
        ("pending", "incompleto"),
        ("no", "requiere_revision"),
        ("rationale", "incompleto"),
        ("condition", "incompleto"),
        ("legal_reference", "incompleto"),
        ("documentary_analysis", "incompleto"),
    ],
)
def test_special_dependency_failures(sensitive_exception_context, change, expected):
    special = sensitive_exception_context[2]
    declaration = next(
        d for d in special["declarations"] if d["question_id"] == "datos_sensibles"
    )
    if change == "absent":
        special["declarations"].remove(declaration)
    elif change == "condition":
        special["conditions"] = []
    elif change in ("legal_reference", "documentary_analysis"):
        special["conditions"][0][change] = " "
    elif change == "rationale":
        declaration["rationale"] = " "
    else:
        declaration["answer"] = "pendiente" if change == "pending" else "no"
    result = evaluate(*sensitive_exception_context)
    assert result.result == expected
    assert all(
        i.question_id == "datos_sensibles"
        for i in result.issues
        if i.field.startswith("special_conditions")
    )


@pytest.mark.parametrize("index", [0, 1, 2])
def test_missing_dependencies(sensitive_exception_context, index):
    values = list(sensitive_exception_context)
    values[index] = None
    result = evaluate(*values)
    assert result.result == "incompleto" and not result.can_confirm
    assert any(
        i.code
        == ["expediente_ausente", "snapshot_ausente", "condiciones_ausentes"][index]
        for i in result.issues
    )


@pytest.mark.parametrize(
    "change", ["role", "flag", "categories", "purpose", "context", "scope"]
)
def test_factual_incoherence_or_missing_context(sensitive_exception_context, change):
    document, rat, _ = sensitive_exception_context
    expected = "requiere_revision"
    if change == "role":
        rat["organization_role"] = "encargado"
    elif change == "flag":
        rat["special_regimes"]["has_sensitive_data"] = False
    elif change == "categories":
        rat["data_categories"][0]["is_sensitive"] = False
    elif change == "purpose":
        document["context"]["purpose_description"] = "Otra finalidad"
    elif change == "context":
        document["context"] = None
        expected = "incompleto"
    else:
        document["scope"] = None
        expected = "incompleto"
    assert evaluate(*sensitive_exception_context).result == expected


@pytest.mark.parametrize("index", [0, 1, 2])
@pytest.mark.parametrize("missing", [False, True])
def test_revalidate_mutated_models_even_with_missing_dependency(
    sensitive_exception_context, index, missing
):
    models = [
        SensitiveRightsExceptionAssessmentV1,
        RatContextSnapshotV1,
        SpecialConditionsV1,
    ]
    values = [
        m.model_validate(v)
        for m, v in zip(models, sensitive_exception_context, strict=True)
    ]
    if index == 0:
        values[index].context.forum_type = "organo_publico"
    elif index == 1:
        values[index].organization_role = "invalid"
    else:
        values[index].conditions[0].authorization_route = "invalid"
    if missing:
        values[(index + 1) % 3] = None
    with pytest.raises(ValidationError):
        evaluate(*values)


def test_model_roundtrip_optional_metadata_and_immutable_inputs(
    sensitive_exception_context,
):
    document, _, _ = sensitive_exception_context
    document.update(notes="Notas opcionales")
    document["evidence"][0].update(obtained_on="1900-01-01")
    models = [
        m.model_validate(v)
        for m, v in zip(
            [
                SensitiveRightsExceptionAssessmentV1,
                RatContextSnapshotV1,
                SpecialConditionsV1,
            ],
            sensitive_exception_context,
            strict=True,
        )
    ]
    before = [m.model_dump(mode="json") for m in models]
    result = evaluate(*models)
    assert result.can_confirm and result == evaluate(*before)
    assert [m.model_dump(mode="json") for m in models] == before


def test_issue_order_numeric_indices_and_precedence(sensitive_exception_context):
    document, _, _ = sensitive_exception_context
    document["evidence"] = [{"evidence_type": "", "reference": ""} for _ in range(12)]
    document["exception_conditions_met"]["answer"] = "no"
    result = evaluate(*sensitive_exception_context)
    assert result.result == "incompleto"
    indices = [
        int(i.field.split(".")[1])
        for i in result.issues
        if i.field.startswith("evidence.")
    ]
    assert indices == sorted(indices)
    assert any(i.category == "requiere_revision" for i in result.issues)
    assert len(result.issues) == len(set(result.issues))
    assert len(result.applicability) == len({i.field for i in result.applicability})
    with pytest.raises(FrozenInstanceError):
        result.issues[0].code = "other"


def test_affirmative_answers_do_not_replace_necessity_or_evidence(
    sensitive_exception_context,
):
    document, _, _ = sensitive_exception_context
    document["context"]["necessity_analysis"] = " "
    document["context"]["evidence"] = []
    result = evaluate(*sensitive_exception_context)
    assert not result.can_confirm
    assert (
        "context.necessity_analysis",
        "campo_obligatorio",
        "incompleto",
    ) in issue_set(result)
    assert ("context.evidence", "evidencia_ausente", "incompleto") in issue_set(result)


@pytest.mark.parametrize("positive", [False, True])
def test_pure_complete_exception_keeps_transversal_and_eipd_blocked(
    sensitive_exception_context, negative_controls, positive
):
    from types import SimpleNamespace

    from app.services.eipd import bind_eipd_screening_v11
    from app.services.licitud import evaluate_transversal_readiness_v1

    document, rat, special = sensitive_exception_context
    assert evaluate(document, rat, special).can_confirm
    screening = deepcopy(negative_controls["eipd_screening"])
    if positive:
        next(
            a
            for a in screening["answers"]
            if a["question_id"] == "datos_protegidos_excepcion_consentimiento"
        )["answer"] = "si"
    screening = bind_eipd_screening_v11(
        screening, rat, None, special, *([None] * 8), document, None
    ).model_dump(mode="json")
    state = SimpleNamespace(
        legal_basis="contrato_precontractual_art13c",
        consent_assessment=None,
        lia_assessment=None,
        contract_assessment=None,
        legal_obligation_assessment=None,
        rights_defense_assessment=None,
        economic_obligations_assessment=None,
        geolocation_assessment=None,
        sensitive_consent_assessment=None,
        health_assessment=None,
        biometric_assessment=None,
        sensitive_rights_exception_assessment=document,
        biometric_rights_exception_assessment=None,
        special_conditions=special,
        eipd_screening=screening,
    )
    before = deepcopy(vars(state))
    special_result, eipd_result, blockers = evaluate_transversal_readiness_v1(
        state, rat
    )
    assert special_result.context_current and eipd_result.context_current
    assert eipd_result.result == "pendiente_revision"
    assert "excepcion_especial_no_validada" in {i.code for i in eipd_result.issues}
    codes = {b["code"] for b in blockers}
    assert "excepcion_derechos_no_preparada" not in codes
    assert "condiciones_especiales_no_preparadas" not in codes
    assert special_result.result == "regimenes_preparados"
    assert "screening_eipd_no_preparado" in codes
    assert vars(state) == before
    if positive:
        assert (
            next(
                a
                for a in state.eipd_screening["answers"]
                if a["question_id"] == "datos_protegidos_excepcion_consentimiento"
            )["answer"]
            == "si"
        )


@pytest.mark.parametrize(
    "change,expected,status",
    [
        ("absent", "incompleto", 400),
        ("pending", "incompleto", 400),
        ("negative", "requiere_revision", 409),
        ("stage", "incompleto", 400),
        ("scope", "requiere_revision", 409),
        ("rationale", "incompleto", 400),
    ],
)
def test_shared_sensitive_exception_gate_reasons(
    sensitive_exception_context, negative_controls, change, expected, status
):
    from types import SimpleNamespace

    from app.services.eipd import bind_eipd_screening_v11
    from app.services.licitud import evaluate_transversal_readiness_v1
    from app.services.special_conditions import bind_special_conditions_v10

    document, rat, special = sensitive_exception_context
    if change == "absent":
        document = None
    elif change == "pending":
        document["context"]["necessary_for_route"]["answer"] = "pendiente"
    elif change == "negative":
        document["exception_conditions_met"]["answer"] = "no"
    elif change == "stage":
        document["context"]["proceeding_stage"] = None
    elif change == "scope":
        document["scope"]["data_category_codes"] = ["otra"]
    else:
        document["exception_conditions_met"]["rationale"] = " "
    draft = deepcopy(special)
    draft.pop("context_binding")
    special = bind_special_conditions_v10(
        draft, rat, "contrato_precontractual_art13c", *([None] * 10), document, None
    ).model_dump(mode="json")
    screening = bind_eipd_screening_v11(
        negative_controls["eipd_screening"],
        rat,
        None,
        special,
        *([None] * 8),
        document,
        None,
    ).model_dump(mode="json")
    state = SimpleNamespace(
        legal_basis="contrato_precontractual_art13c",
        consent_assessment=None,
        lia_assessment=None,
        contract_assessment=None,
        legal_obligation_assessment=None,
        rights_defense_assessment=None,
        economic_obligations_assessment=None,
        geolocation_assessment=None,
        sensitive_consent_assessment=None,
        health_assessment=None,
        biometric_assessment=None,
        sensitive_rights_exception_assessment=document,
        biometric_rights_exception_assessment=None,
        special_conditions=special,
        eipd_screening=screening,
    )
    before = deepcopy(vars(state))
    special_result, _, blockers = evaluate_transversal_readiness_v1(state, rat)
    own = evaluate(document, rat, special)
    assert own.result == expected
    block = next(
        b for b in blockers if b["field"] == "sensitive_rights_exception_assessment"
    )
    assert (
        block["code"] == "excepcion_derechos_no_preparada"
        and block["status_code"] == status
    )
    assert "validador_no_implementado" not in {i.code for i in special_result.issues}
    for i in own.issues:
        field = (
            i.field
            if i.field.startswith(
                (
                    "special_conditions",
                    "rat_context_snapshot",
                    "sensitive_rights_exception_assessment",
                )
            )
            else "sensitive_rights_exception_assessment." + i.field
        )
        assert any(
            s.field == field
            and s.code == i.code
            and s.category == i.category
            and s.question_id == i.question_id
            for s in special_result.issues
        )
    assert vars(state) == before
