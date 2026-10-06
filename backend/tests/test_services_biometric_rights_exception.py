from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    BiometricRightsExceptionAssessmentV1,
    RatContextSnapshotV1,
    SensitiveRightsExceptionAssessmentV1,
    SpecialConditionsV1,
)
from app.services.biometric_rights_exception import (
    evaluate_biometric_rights_exception_v1 as evaluate,
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
OWN_TEXTS = [
    "biometric_data_description",
    "unique_identification_analysis",
    "exception_application_analysis",
    "sensitive_context_connection_analysis",
    "systems_coverage_analysis",
]
SYSTEM_TEXTS = [
    "system_reference",
    "system_name",
    "system_description",
    "specific_purpose",
    "purpose_alignment_analysis",
    "use_period_description",
    "retention_alignment_analysis",
    "rights_exercise_description",
    "rights_contact_channel",
    "information_reference",
]
RESPONSES = [
    "exception_conditions_met",
    "unique_identification_confirmed",
    "all_systems_documented",
    "context.related_to_right",
    "context.necessary_for_route",
    "context.within_forum_scope",
    "context.principles_addressed",
    "systems.0.system_identification_disclosed",
    "systems.0.purpose_disclosed",
    "systems.0.use_period_disclosed",
    "systems.0.rights_exercise_disclosed",
]


def parent(value, path):
    parts = path.split(".")
    for part in parts[:-1]:
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value, parts[-1]


def issue_set(result):
    return {(i.field, i.code, i.category) for i in result.issues}


def test_complete_biometric_exception_without_consent(biometric_exception_context):
    before = deepcopy(biometric_exception_context)
    result = evaluate(*biometric_exception_context)
    assert result.result == "completo" and result.can_confirm and not result.issues
    assert evaluate(*biometric_exception_context) == result
    assert biometric_exception_context == before
    with pytest.raises(FrozenInstanceError):
        result.result = "incompleto"
    with pytest.raises(FrozenInstanceError):
        result.applicability[0].applicability = "sin_resolver"
    assert len(result.applicability) == len({i.field for i in result.applicability})


@pytest.mark.parametrize(
    "field",
    ["context." + f for f in CONTEXT_TEXTS]
    + OWN_TEXTS
    + ["systems.0." + f for f in SYSTEM_TEXTS],
)
@pytest.mark.parametrize("value", [None, "", " "])
def test_required_texts(biometric_exception_context, field, value):
    target, name = parent(biometric_exception_context[0], field)
    target[name] = value
    result = evaluate(*biometric_exception_context)
    assert result.result == "incompleto"
    assert (field, "campo_obligatorio", "incompleto") in issue_set(result)
    assert {i.field: i.applicability for i in result.applicability}[
        field
    ] == "aplicable"


@pytest.mark.parametrize("field", RESPONSES)
@pytest.mark.parametrize(
    "value,code,category,suffix",
    [
        (None, "respuesta_ausente", "incompleto", ""),
        (
            {"answer": "pendiente", "rationale": "Revision"},
            "respuesta_pendiente",
            "incompleto",
            ".answer",
        ),
        (
            {"answer": "no", "rationale": "No se acredita"},
            "respuesta_revision",
            "requiere_revision",
            ".answer",
        ),
        (
            {"answer": "si", "rationale": " "},
            "fundamento_ausente",
            "incompleto",
            ".rationale",
        ),
    ],
)
def test_required_responses(
    biometric_exception_context, field, value, code, category, suffix
):
    target, name = parent(biometric_exception_context[0], field)
    target[name] = value
    result = evaluate(*biometric_exception_context)
    assert result.result == category
    assert (field + suffix, code, category) in issue_set(result)


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
def test_missing_enums(biometric_exception_context, field):
    target, name = parent(biometric_exception_context[0], field)
    target[name] = None
    result = evaluate(*biometric_exception_context)
    assert (field, "campo_obligatorio", "incompleto") in issue_set(result)


@pytest.mark.parametrize(
    "field,stage",
    [
        ("preparatory_actions", "preparacion"),
        ("post_proceeding_necessity_analysis", "finalizado"),
    ],
)
def test_stage_conditional_and_residuality(biometric_exception_context, field, stage):
    document, _, _, sensitive = biometric_exception_context
    for doc in (document, sensitive):
        doc["context"]["proceeding_stage"] = stage
        doc["context"][field] = "Analisis de etapa"
    assert evaluate(*biometric_exception_context).can_confirm
    document["context"][field] = " "
    result = evaluate(*biometric_exception_context)
    assert ("context." + field, "campo_obligatorio", "incompleto") in issue_set(result)
    document["context"].update(proceeding_stage="en_curso")
    document["context"][field] = "Residual"
    result = evaluate(*biometric_exception_context)
    assert ("context." + field, "campo_residual", "requiere_revision") in issue_set(
        result
    )
    document["context"]["proceeding_stage"] = None
    result = evaluate(*biometric_exception_context)
    assert {i.field: i.applicability for i in result.applicability}[
        "context." + field
    ] == "sin_resolver"
    assert not any(i.field == "context." + field for i in result.issues)


@pytest.mark.parametrize(
    "field,value",
    [
        ("context_reference", "Otro caso"),
        ("purpose_description", "Otra finalidad"),
        ("route", "ejercicio_derecho"),
        ("right_holder", "tercero"),
        ("forum_type", "tribunal_justicia"),
        ("proceeding_stage", "preparacion"),
        ("proceeding_reference", "Otra actuacion"),
    ],
)
def test_discordant_sensitive_context_link(biometric_exception_context, field, value):
    document, _, _, _ = biometric_exception_context
    document["context"][field] = value
    if field == "proceeding_stage":
        document["context"]["preparatory_actions"] = "Preparacion documentada"
    result = evaluate(*biometric_exception_context)
    assert result.result == "requiere_revision"
    assert (
        "context." + field,
        "vinculo_contexto_sensible_discordante",
        "requiere_revision",
    ) in issue_set(result)


def test_link_canonization_and_specific_prose_not_literal_equality(
    biometric_exception_context,
):
    document, _, _, _ = biometric_exception_context
    for field in ("context_reference", "purpose_description", "proceeding_reference"):
        document["context"][field] = (
            "  " + document["context"][field].upper().replace(" ", "  ") + " "
        )
    document["context"]["purpose_description"] = " GESTIÓN DE CLIENTES "
    for field in (
        "right_description",
        "holder_connection_analysis",
        "forum_description",
        "necessity_analysis",
        "data_minimization_analysis",
        "safeguards_analysis",
    ):
        document["context"][field] = "Analisis especifico biometrico"
    document["context"]["evidence"] = [
        {"evidence_type": "caso", "reference": "Referencia biometrica especifica"}
    ]
    document["notes"] = "Observacion distinta"
    assert evaluate(*biometric_exception_context).can_confirm


@pytest.mark.parametrize(
    "change,category",
    [
        ("missing", "incompleto"),
        ("pending", "incompleto"),
        ("negative", "requiere_revision"),
        ("stage", "incompleto"),
        ("scope", "requiere_revision"),
        ("rationale", "incompleto"),
    ],
)
def test_sensitive_dependency_propagated(biometric_exception_context, change, category):
    from app.services.sensitive_rights_exception import (
        evaluate_sensitive_rights_exception_v1,
    )

    document, rat, special, sensitive = biometric_exception_context
    if change == "missing":
        sensitive = None
    elif change == "pending":
        sensitive["exception_conditions_met"]["answer"] = "pendiente"
    elif change == "negative":
        sensitive["exception_conditions_met"]["answer"] = "no"
    elif change == "stage":
        sensitive["context"]["proceeding_stage"] = None
    elif change == "scope":
        sensitive["scope"]["data_category_codes"] = ["otra"]
    else:
        sensitive["exception_conditions_met"]["rationale"] = " "
    dependency = evaluate_sensitive_rights_exception_v1(sensitive, rat, special)
    result = evaluate(document, rat, special, sensitive)
    assert result.result == category
    for i in dependency.issues:
        path = (
            i.field
            if i.field.startswith(
                (
                    "rat_context_snapshot",
                    "special_conditions",
                    "sensitive_rights_exception_assessment",
                )
            )
            else "sensitive_rights_exception_assessment." + i.field
        )
        assert any(
            r.field == path
            and r.code == i.code
            and r.category == i.category
            and r.question_id == i.question_id
            for r in result.issues
        )
    for a in dependency.applicability:
        path = (
            a.field
            if a.field.startswith(
                (
                    "rat_context_snapshot",
                    "special_conditions",
                    "sensitive_rights_exception_assessment",
                )
            )
            else "sensitive_rights_exception_assessment." + a.field
        )
        assert any(
            r.field == path and r.applicability == a.applicability
            for r in result.applicability
        )


@pytest.mark.parametrize("place", ["document", "context", "system", "condition"])
@pytest.mark.parametrize("missing", ["list", "evidence_type", "reference"])
def test_required_evidence(biometric_exception_context, place, missing):
    document, _, special, _ = biometric_exception_context
    target = (
        document
        if place == "document"
        else (
            document["context"]
            if place == "context"
            else (
                document["systems"][0]
                if place == "system"
                else special["conditions"][-1]
            )
        )
    )
    if missing == "list":
        target["evidence"] = []
    else:
        target["evidence"][0][missing] = " "
    result = evaluate(*biometric_exception_context)
    assert result.result == "incompleto"
    assert any(
        i.code == ("evidencia_ausente" if missing == "list" else "evidencia_incompleta")
        for i in result.issues
    )


@pytest.mark.parametrize("place", ["document", "declaration", "condition"])
@pytest.mark.parametrize("field", ["data_category_codes", "data_subject_codes"])
@pytest.mark.parametrize(
    "mode,category",
    [
        ("empty", "incompleto"),
        ("unknown", "requiere_revision"),
        ("duplicate", "requiere_revision"),
    ],
)
def test_scope_empty_unknown_or_semantic_duplicate(
    biometric_exception_context, place, field, mode, category
):
    document, _, special, _ = biometric_exception_context
    target = (
        document["scope"]
        if place == "document"
        else (
            next(
                d
                for d in special["declarations"]
                if d["question_id"] == "biometricos_identificacion_unica"
            )
            if place == "declaration"
            else special["conditions"][-1]
        )
    )
    valid = target[field][0]
    target[field] = (
        []
        if mode == "empty"
        else ["otra"] if mode == "unknown" else [valid, " " + valid.upper() + " "]
    )
    result = evaluate(*biometric_exception_context)
    assert result.result == category
    assert any(
        i.code == ("alcance_vacio" if mode == "empty" else "alcance_invalido")
        for i in result.issues
    )


@pytest.mark.parametrize("field", ["data_category_codes", "data_subject_codes"])
def test_scope_complete_coverage_and_sensitive_link(biometric_exception_context, field):
    document, rat, special, sensitive = biometric_exception_context
    source = (
        rat["data_categories"]
        if field == "data_category_codes"
        else rat["data_subjects"]
    )
    extra = deepcopy(source[0])
    extra["category_code"] = "otro"
    source.append(extra)
    result = evaluate(*biometric_exception_context)
    assert not result.can_confirm
    assert any(i.code == "cobertura_biometria_no_preparada" for i in result.issues)
    for scope in (document["scope"], sensitive["scope"]):
        scope[field].append("otro")
    for declaration in special["declarations"]:
        if declaration["question_id"] in (
            "datos_sensibles",
            "biometricos_identificacion_unica",
        ):
            declaration[field].append("otro")
    for condition in special["conditions"]:
        condition[field].append("otro")
    assert evaluate(*biometric_exception_context).can_confirm
    document["scope"][field].remove("otro")
    assert any(
        i.code == "alcance_excepcion_sensible_discordante"
        for i in evaluate(*biometric_exception_context).issues
    )


@pytest.mark.parametrize(
    "field,value,category",
    [
        ("authorization_route", None, "incompleto"),
        ("authorization_route", "consentimiento", "requiere_revision"),
        ("uses_consent_assessment", None, "incompleto"),
        ("uses_consent_assessment", True, "requiere_revision"),
        ("legal_reference", " ", "incompleto"),
        ("documentary_analysis", " ", "incompleto"),
    ],
)
def test_biometric_condition_coherence(
    biometric_exception_context, field, value, category
):
    biometric_exception_context[2]["conditions"][-1][field] = value
    result = evaluate(*biometric_exception_context)
    assert result.result == category
    assert any(
        i.field.endswith("." + field)
        and i.question_id == "biometricos_identificacion_unica"
        for i in result.issues
    )


@pytest.mark.parametrize(
    "change,category",
    [
        ("absent", "incompleto"),
        ("pending", "incompleto"),
        ("no", "requiere_revision"),
        ("rationale", "incompleto"),
        ("condition", "incompleto"),
    ],
)
def test_biometric_declaration_or_condition_missing(
    biometric_exception_context, change, category
):
    special = biometric_exception_context[2]
    declaration = next(
        d
        for d in special["declarations"]
        if d["question_id"] == "biometricos_identificacion_unica"
    )
    if change == "absent":
        special["declarations"].remove(declaration)
    elif change == "condition":
        special["conditions"].pop()
    elif change == "rationale":
        declaration["rationale"] = " "
    else:
        declaration["answer"] = "pendiente" if change == "pending" else "no"
    result = evaluate(*biometric_exception_context)
    assert result.result == category
    assert any(
        i.question_id == "biometricos_identificacion_unica" for i in result.issues
    )


def test_unique_systems_and_information_of_every_system(biometric_exception_context):
    document, _, _, _ = biometric_exception_context
    system = deepcopy(document["systems"][0])
    system["system_reference"] = "SISTÉMA"
    document["systems"].append(system)
    assert evaluate(*biometric_exception_context).can_confirm
    duplicate = deepcopy(system)
    # Canonical duplicate with decomposed Unicode, case and whitespace changes.
    duplicate["system_reference"] = " sistéma "
    document["systems"].append(duplicate)
    assert any(
        i.code == "sistema_duplicado"
        for i in evaluate(*biometric_exception_context).issues
    )
    document["systems"].pop()
    document["systems"][1]["rights_contact_channel"] = " "
    assert (
        "systems.1.rights_contact_channel",
        "campo_obligatorio",
        "incompleto",
    ) in issue_set(evaluate(*biometric_exception_context))


def test_empty_systems_and_numeric_order(biometric_exception_context):
    document, _, _, _ = biometric_exception_context
    original = deepcopy(document["systems"][0])
    document["systems"] = []
    assert ("systems", "sistemas_ausentes", "incompleto") in issue_set(
        evaluate(*biometric_exception_context)
    )
    document["systems"] = [deepcopy(original) for _ in range(12)]
    for index, system in enumerate(document["systems"]):
        system["system_reference"] = f"Sistema {index}"
        system["purpose_disclosed"] = None
    result = evaluate(*biometric_exception_context)
    indices = [
        int(i.field.split(".")[1])
        for i in result.issues
        if i.field.startswith("systems.")
    ]
    assert indices == sorted(indices) and 10 in indices
    assert len(result.issues) == len(set(result.issues))
    with pytest.raises(FrozenInstanceError):
        result.issues[0].code = "other"


@pytest.mark.parametrize("index", range(4))
@pytest.mark.parametrize("missing", [False, True])
def test_revalidate_mutated_models_with_other_missing_dependency(
    biometric_exception_context, index, missing
):
    models = [
        BiometricRightsExceptionAssessmentV1,
        RatContextSnapshotV1,
        SpecialConditionsV1,
        SensitiveRightsExceptionAssessmentV1,
    ]
    values = [
        m.model_validate(v)
        for m, v in zip(models, biometric_exception_context, strict=True)
    ]
    if index == 0:
        values[index].systems[0].purpose_disclosed.answer = "no_aplica"
    elif index == 1:
        values[index].organization_role = "invalid"
    elif index == 2:
        values[index].conditions[-1].authorization_route = "invalid"
    else:
        values[index].context.forum_type = "organo_publico"
    if missing:
        values[(index + 1) % 4] = None
    with pytest.raises(ValidationError):
        evaluate(*values)


@pytest.mark.parametrize("index", range(4))
def test_missing_dependencies(biometric_exception_context, index):
    values = list(biometric_exception_context)
    values[index] = None
    assert evaluate(*values).result == "incompleto"


def test_models_json_dates_and_immutable_inputs(biometric_exception_context):
    document, _, _, _ = biometric_exception_context
    document["evidence"][0]["obtained_on"] = "1900-01-01"
    models = [
        m.model_validate(v)
        for m, v in zip(
            [
                BiometricRightsExceptionAssessmentV1,
                RatContextSnapshotV1,
                SpecialConditionsV1,
                SensitiveRightsExceptionAssessmentV1,
            ],
            biometric_exception_context,
            strict=True,
        )
    ]
    before = [m.model_dump(mode="json") for m in models]
    result = evaluate(*models)
    assert result.can_confirm and result == evaluate(*before)
    assert [m.model_dump(mode="json") for m in models] == before


def test_incomplete_precedence_and_affirmative_not_sufficient(
    biometric_exception_context,
):
    document, _, _, _ = biometric_exception_context
    document["context"]["necessity_analysis"] = " "
    document["context"]["evidence"] = []
    document["exception_conditions_met"]["answer"] = "no"
    result = evaluate(*biometric_exception_context)
    assert result.result == "incompleto"
    assert any(i.category == "requiere_revision" for i in result.issues)
    assert not result.can_confirm


@pytest.mark.parametrize(
    "route,forum,holder",
    [
        ("formulacion_derecho", "tribunal_justicia", "tercero"),
        ("ejercicio_derecho", "organo_administrativo", "ambos"),
        ("defensa_derecho", "tribunal_justicia", "responsable"),
    ],
)
def test_supported_context_variants_linked(
    biometric_exception_context, route, forum, holder
):
    document, _, _, sensitive = biometric_exception_context
    for item in (document, sensitive):
        item["context"].update(route=route, forum_type=forum, right_holder=holder)
    assert evaluate(*biometric_exception_context).can_confirm


@pytest.mark.parametrize("positive", [False, True])
def test_pure_biometric_complete_keeps_current_confirmation_barriers(
    biometric_exception_context, negative_controls, positive
):
    from types import SimpleNamespace

    from app.services.eipd import bind_eipd_screening_v11
    from app.services.licitud import evaluate_transversal_readiness_v1

    document, rat, special, sensitive = biometric_exception_context
    assert evaluate(*biometric_exception_context).can_confirm
    screening = deepcopy(negative_controls["eipd_screening"])
    if positive:
        next(
            a
            for a in screening["answers"]
            if a["question_id"] == "datos_protegidos_excepcion_consentimiento"
        )["answer"] = "si"
    screening = bind_eipd_screening_v11(
        screening, rat, None, special, *([None] * 8), sensitive, document
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
        sensitive_rights_exception_assessment=sensitive,
        biometric_rights_exception_assessment=document,
        special_conditions=special,
        eipd_screening=screening,
    )
    before = deepcopy(vars(state))
    special_result, eipd_result, blockers = evaluate_transversal_readiness_v1(
        state, rat
    )
    assert special_result.context_current and eipd_result.context_current
    assert "validador_no_implementado" not in {i.code for i in special_result.issues}
    assert special_result.result == "regimenes_preparados"
    assert eipd_result.result == "pendiente_revision"
    assert "excepcion_especial_no_validada" in {i.code for i in eipd_result.issues}
    assert not any(b["code"] == "excepcion_derechos_no_preparada" for b in blockers)
    assert not any(b["field"] == "biometric_assessment" for b in blockers)
    assert "screening_eipd_no_preparado" in {b["code"] for b in blockers}
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
    "change,category,status",
    [
        ("absent", "incompleto", 400),
        ("pending", "incompleto", 400),
        ("negative", "requiere_revision", 409),
        ("dependency", "incompleto", 400),
        ("context", "requiere_revision", 409),
        ("system", "incompleto", 400),
    ],
)
def test_shared_biometric_exception_gate_reasons(
    biometric_exception_context, negative_controls, change, category, status
):
    from types import SimpleNamespace

    from app.services.eipd import bind_eipd_screening_v11
    from app.services.licitud import evaluate_transversal_readiness_v1
    from app.services.special_conditions import bind_special_conditions_v10

    document, rat, special, sensitive = biometric_exception_context
    if change == "absent":
        document = None
    elif change == "pending":
        document["unique_identification_confirmed"]["answer"] = "pendiente"
    elif change == "negative":
        document["exception_conditions_met"]["answer"] = "no"
    elif change == "dependency":
        sensitive = None
    elif change == "context":
        document["context"]["context_reference"] = "Otro caso"
    else:
        document["systems"][0]["purpose_disclosed"] = None
    draft = deepcopy(special)
    draft.pop("context_binding")
    special = bind_special_conditions_v10(
        draft,
        rat,
        "contrato_precontractual_art13c",
        *([None] * 10),
        sensitive,
        document,
    ).model_dump(mode="json")
    screening = bind_eipd_screening_v11(
        negative_controls["eipd_screening"],
        rat,
        None,
        special,
        *([None] * 8),
        sensitive,
        document,
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
        sensitive_rights_exception_assessment=sensitive,
        biometric_rights_exception_assessment=document,
        special_conditions=special,
        eipd_screening=screening,
    )
    before = deepcopy(vars(state))
    special_result, _, blockers = evaluate_transversal_readiness_v1(state, rat)
    own = evaluate(document, rat, special, sensitive)
    assert own.result == category
    block = next(
        b for b in blockers if b["field"] == "biometric_rights_exception_assessment"
    )
    assert (
        block["code"] == "excepcion_derechos_no_preparada"
        and block["status_code"] == status
    )
    assert not any(b["field"] == "biometric_assessment" for b in blockers)
    assert "validador_no_implementado" not in {i.code for i in special_result.issues}
    for i in own.issues:
        path = (
            i.field
            if i.field.startswith(
                (
                    "special_conditions",
                    "rat_context_snapshot",
                    "sensitive_rights_exception_assessment",
                    "biometric_rights_exception_assessment",
                )
            )
            else "biometric_rights_exception_assessment." + i.field
        )
        assert any(
            s.field == path
            and s.code == i.code
            and s.category == i.category
            and s.question_id == i.question_id
            for s in special_result.issues
        )
    assert vars(state) == before
