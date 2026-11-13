from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    BiometricAssessmentV1,
    ConsentAssessmentV1,
    RatContextSnapshotV1,
    SensitiveConsentAssessmentV1,
    SpecialConditionsV1,
)
from app.services.biometric import evaluate_biometric_assessment_v1 as evaluate
from app.services.special_conditions import bind_special_conditions_v7

TEXTS = [
    "purpose_description",
    "sensitive_data_description",
    "processing_operations",
    "declaration_reference",
    "declaration_content_analysis",
]
RESPONSES = [
    "express_declaration_documented",
    "sensitive_scope_explicit",
    "purpose_specific",
    "proof_available",
    "consent_current",
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
SYSTEM_RESPONSES = [
    "system_identification_disclosed",
    "purpose_disclosed",
    "use_period_disclosed",
    "rights_exercise_disclosed",
]
OWN_TEXTS = [
    "purpose_description",
    "biometric_data_description",
    "processing_operations",
    "unique_identification_analysis",
    "systems_coverage_analysis",
]
OWN_RESPONSES = ["unique_identification_confirmed", "all_systems_documented"]


@pytest.fixture
def complete_payload():
    ids = [
        "consentimiento_libre",
        "consentimiento_informado",
        "consentimiento_especifico_finalidad",
        "consentimiento_previo",
        "voluntad_inequivoca",
        "accion_afirmativa_clara",
        "revocacion_posible",
        "revocacion_medio_equivalente",
        "revocacion_expedita",
        "revocacion_fidedigna",
        "revocacion_gratuita",
        "revocacion_disponible_permanentemente",
        "responsable_puede_acreditar",
    ]
    return {
        "given_by": "titular",
        "grant_method": "electronico",
        "answers": [{"question_id": q, "answer": "si"} for q in ids]
        + [{"question_id": "contexto_contrato_servicio", "answer": "no"}],
    }


@pytest.fixture
def sensitive_context(complete_lia_context, complete_payload, negative_controls):
    rat = deepcopy(complete_lia_context[1])
    rat["data_categories"][0]["is_sensitive"] = True
    rat["special_regimes"]["has_sensitive_data"] = True
    scope = {"data_category_codes": ["id"], "data_subject_codes": ["clientes"]}
    draft = deepcopy(negative_controls["special_conditions"])
    for item in draft["declarations"]:
        if item["question_id"] == "datos_sensibles":
            item.update(answer="si", rationale="Alcance sensible", **scope)
    draft["conditions"] = [
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "sensitive_condition_id": "consentimiento_expreso_art16",
            "uses_consent_assessment": True,
            "legal_reference": "art16",
            "documentary_analysis": "Declaración expresa",
            "evidence": [{"evidence_type": "declaracion", "reference": "Registro"}],
            **scope,
        }
    ]
    document = {field: "Descripción documentada" for field in TEXTS}
    document.update(
        purpose_description=rat["purpose"],
        expression_method="tecnologico_equivalente",
        technology_equivalence_analysis="Equivalencia documentada",
        scope=scope,
        evidence=[{"evidence_type": "declaracion", "reference": "Registro"}],
    )
    document.update(
        {
            field: {"answer": "si", "rationale": "Comprobación documentada"}
            for field in RESPONSES
        }
    )
    special = bind_special_conditions_v7(
        draft,
        rat,
        "consentimiento_art12",
        complete_payload,
        None,
        None,
        None,
        None,
        None,
        None,
        document,
    ).model_dump(mode="json")
    return document, rat, special, deepcopy(complete_payload)


@pytest.fixture
def biometric_context(sensitive_context):
    sensitive, rat, special, consent = sensitive_context
    scope = deepcopy(sensitive["scope"])
    for declaration in special["declarations"]:
        if declaration["question_id"] == "biometricos_identificacion_unica":
            declaration.update(
                answer="si", rationale="Identificación biométrica", **scope
            )
    special["conditions"].append(
        {
            "regime_id": "biometricos_art16ter",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "art16ter",
            "documentary_analysis": "Análisis documentado",
            "evidence": [{"evidence_type": "aviso", "reference": "Aviso"}],
            **scope,
        }
    )
    response = {"answer": "si", "rationale": "Información documentada"}
    system = {field: "Descripción documentada" for field in SYSTEM_TEXTS}
    system.update({field: deepcopy(response) for field in SYSTEM_RESPONSES})
    system["evidence"] = [{"evidence_type": "aviso", "reference": "Aviso"}]
    document = {field: "Descripción documentada" for field in OWN_TEXTS}
    document.update({field: deepcopy(response) for field in OWN_RESPONSES})
    document.update(
        purpose_description=rat["purpose"],
        scope=scope,
        route="consentimiento_expreso",
        systems=[system],
        evidence=[{"evidence_type": "aviso", "reference": "Aviso"}],
    )
    return document, rat, special, consent, sensitive


def test_biometric_complete_immutable_and_model_inputs(biometric_context):
    before = deepcopy(biometric_context)
    result = evaluate(*biometric_context)
    assert result.result == "completo" and result.can_confirm
    assert not result.issues
    own = [
        a
        for a in result.applicability
        if not a.field.startswith(
            ("consent_assessment", "sensitive_consent_assessment")
        )
    ]
    assert own and all(a.applicability == "aplicable" for a in own)
    models = [
        BiometricAssessmentV1,
        RatContextSnapshotV1,
        SpecialConditionsV1,
        ConsentAssessmentV1,
        SensitiveConsentAssessmentV1,
    ]
    assert (
        evaluate(
            *(
                m.model_validate(v)
                for m, v in zip(models, biometric_context, strict=False)
            )
        )
        == result
    )
    assert biometric_context == before


@pytest.mark.parametrize(
    "field", OWN_TEXTS + OWN_RESPONSES + ["scope", "route", "systems", "evidence"]
)
def test_biometric_missing_fields(biometric_context, field):
    biometric_context[0].pop(field)
    result = evaluate(*biometric_context)
    assert result.result == "incompleto"
    assert any(
        i.field == field or i.field.startswith(field + ".") for i in result.issues
    )


@pytest.mark.parametrize("field", SYSTEM_TEXTS + SYSTEM_RESPONSES + ["evidence"])
def test_biometric_missing_system_fields(biometric_context, field):
    biometric_context[0]["systems"][0].pop(field)
    result = evaluate(*biometric_context)
    assert result.result == "incompleto"
    assert any(
        i.field == "systems.0." + field
        or i.field.startswith("systems.0." + field + ".")
        for i in result.issues
    )


@pytest.mark.parametrize("field", OWN_RESPONSES + SYSTEM_RESPONSES)
@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_biometric_response_precedence(biometric_context, field, answer, expected):
    owner = (
        biometric_context[0]
        if field in OWN_RESPONSES
        else biometric_context[0]["systems"][0]
    )
    owner[field]["answer"] = answer
    assert evaluate(*biometric_context).result == expected
    owner[field]["rationale"] = " "
    assert evaluate(*biometric_context).result == "incompleto"


@pytest.mark.parametrize("index", range(5))
def test_biometric_missing_dependencies(biometric_context, index):
    values = list(biometric_context)
    values[index] = None
    assert evaluate(*values).result == "incompleto"


@pytest.mark.parametrize(
    "change",
    [
        "purpose",
        "role",
        "partial",
        "ordinary",
        "representation",
        "sensitive_pending",
        "consent_no",
        "declaration_no",
        "declaration_missing",
        "condition_missing",
        "condition_route",
        "condition_link",
        "scope_discordant",
        "duplicate",
        "period",
        "specific_purpose",
    ],
)
def test_biometric_coherence(biometric_context, change):
    document, rat, special, consent, sensitive = biometric_context
    if change == "purpose":
        document["purpose_description"] = "Otra finalidad"
    elif change == "role":
        rat["organization_role"] = "encargado"
    elif change == "partial":
        rat["data_categories"].append(
            {**rat["data_categories"][0], "category_code": "other"}
        )
    elif change == "ordinary":
        rat["data_categories"][0]["is_sensitive"] = False
    elif change == "representation":
        consent["given_by"] = "representante_legal"
    elif change == "sensitive_pending":
        sensitive["proof_available"]["answer"] = "pendiente"
    elif change == "consent_no":
        consent["answers"][0]["answer"] = "no"
    elif change == "declaration_no":
        next(
            d
            for d in special["declarations"]
            if d["question_id"] == "biometricos_identificacion_unica"
        )["answer"] = "no"
    elif change == "declaration_missing":
        special["declarations"] = [
            d
            for d in special["declarations"]
            if d["question_id"] != "biometricos_identificacion_unica"
        ]
    elif change == "condition_missing":
        special["conditions"].pop()
    elif change == "condition_route":
        special["conditions"][-1]["authorization_route"] = "excepcion_legal"
    elif change == "condition_link":
        special["conditions"][-1]["uses_consent_assessment"] = False
    elif change == "scope_discordant":
        special["conditions"][-1]["data_category_codes"] = ["outside"]
    elif change == "duplicate":
        document["systems"].append(deepcopy(document["systems"][0]))
    elif change == "period":
        document["systems"][0]["retention_alignment_analysis"] = " "
    else:
        document["systems"][0]["purpose_alignment_analysis"] = " "
    assert not evaluate(*biometric_context).can_confirm


def test_biometric_more_specific_purpose_and_multiple_systems(biometric_context):
    document = biometric_context[0]
    document["systems"][0]["specific_purpose"] = "Acceso a un recinto"
    other = deepcopy(document["systems"][0])
    other["system_reference"] = "Segundo"
    document["systems"].append(other)
    assert evaluate(*biometric_context).result == "completo"


def test_biometric_numeric_order_and_semantic_duplicates(biometric_context):
    document = biometric_context[0]
    document["systems"] = [deepcopy(document["systems"][0]) for _ in range(12)]
    for i, system in enumerate(document["systems"]):
        system["system_reference"] = str(i)
        system["system_name"] = " "
    issues = [
        i.field
        for i in evaluate(*biometric_context).issues
        if i.field.endswith("system_name")
    ]
    assert issues == [f"systems.{i}.system_name" for i in range(12)]
    document["systems"][1]["system_reference"] = " 0 "
    assert "sistema_duplicado" in {i.code for i in evaluate(*biometric_context).issues}


@pytest.mark.parametrize("place", ["general", "system", "condition"])
@pytest.mark.parametrize("field", ["evidence_type", "reference"])
def test_biometric_evidence_required(biometric_context, place, field):
    document, _, special, _, _ = biometric_context
    evidence = (
        document["evidence"]
        if place == "general"
        else (
            document["systems"][0]["evidence"]
            if place == "system"
            else special["conditions"][-1]["evidence"]
        )
    )
    evidence[0][field] = " "
    assert evaluate(*biometric_context).result == "incompleto"


@pytest.mark.parametrize("index", range(5))
def test_biometric_revalidates_mutated_models(biometric_context, index):
    models = [
        BiometricAssessmentV1,
        RatContextSnapshotV1,
        SpecialConditionsV1,
        ConsentAssessmentV1,
        SensitiveConsentAssessmentV1,
    ]
    values = list(biometric_context)
    values[index] = models[index].model_validate(values[index])
    if index == 0:
        values[index].route = "invalid"
    elif index == 1:
        values[index].organization_role = "invalid"
    elif index == 2:
        values[index].declarations[0].answer = "invalid"
    elif index == 3:
        values[index].given_by = "invalid"
    else:
        values[index].expression_method = "invalid"
    with pytest.raises(ValidationError):
        evaluate(*values)


def biometric_state(context, controls):
    from types import SimpleNamespace

    from app.services.eipd import bind_eipd_screening_v10
    from app.services.special_conditions import bind_special_conditions_v9

    document, rat, special, consent, sensitive = context
    special_input = deepcopy(special)
    special_input.pop("context_binding")
    special = bind_special_conditions_v9(
        special_input,
        rat,
        "consentimiento_art12",
        consent,
        None,
        None,
        None,
        None,
        None,
        None,
        sensitive,
        None,
        document,
    ).model_dump(mode="json")
    eipd = bind_eipd_screening_v10(
        controls["eipd_screening"],
        rat,
        None,
        special,
        None,
        None,
        None,
        None,
        None,
        sensitive,
        None,
        document,
    ).model_dump(mode="json")
    return SimpleNamespace(
        legal_basis="consentimiento_art12",
        consent_assessment=consent,
        lia_assessment=None,
        contract_assessment=None,
        legal_obligation_assessment=None,
        rights_defense_assessment=None,
        economic_obligations_assessment=None,
        geolocation_assessment=None,
        sensitive_consent_assessment=sensitive,
        health_assessment=None,
        biometric_assessment=document,
        special_conditions=special,
        eipd_screening=eipd,
    )


def test_biometric_transversal_prepared_immutable(biometric_context, negative_controls):
    from app.services.licitud import evaluate_transversal_readiness_v1

    state = biometric_state(biometric_context, negative_controls)
    before = deepcopy(vars(state))
    special, eipd, blockers = evaluate_transversal_readiness_v1(
        state, biometric_context[1]
    )
    assert special.result == "regimenes_preparados" and special.context_current
    assert special.detected_regimes == ("biometricos_art16ter", "sensibles_art16")
    assert eipd.result == "sin_supuestos_declarados" and eipd.context_current
    assert not blockers
    assert vars(state) == before


@pytest.mark.parametrize("index", range(5))
def test_biometric_eipd_positive(biometric_context, negative_controls, index):
    from app.services.licitud import evaluate_transversal_readiness_v1

    controls = deepcopy(negative_controls)
    controls["eipd_screening"]["answers"][index]["answer"] = "si"
    special, _, blockers = evaluate_transversal_readiness_v1(
        biometric_state(biometric_context, controls), biometric_context[1]
    )
    assert special.result == "regimenes_preparados"
    assert "screening_eipd_no_preparado" in {i["code"] for i in blockers}


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "pending",
        "stale",
        "route",
        "sensitive_missing",
        "consent_missing",
        "representation",
    ],
)
def test_biometric_transversal_blockers(biometric_context, negative_controls, change):
    from app.services.licitud import evaluate_transversal_readiness_v1

    if change == "route":
        biometric_context[2]["conditions"][-1][
            "authorization_route"
        ] = "excepcion_legal"
    if change == "representation":
        biometric_context[3]["given_by"] = "representante_legal"
    state = biometric_state(biometric_context, negative_controls)
    if change == "missing":
        state.biometric_assessment = None
    elif change == "pending":
        state.biometric_assessment["systems"][0]["purpose_disclosed"][
            "answer"
        ] = "pendiente"
    elif change == "stale":
        state.biometric_assessment["notes"] = "Cambio"
    elif change == "sensitive_missing":
        state.sensitive_consent_assessment = None
    elif change == "consent_missing":
        state.consent_assessment = None
    special, eipd, blockers = evaluate_transversal_readiness_v1(
        state, biometric_context[1]
    )
    assert blockers
    if change == "stale":
        assert not special.context_current and not eipd.context_current
    else:
        assert "biometria_no_preparada" in {i["code"] for i in blockers}
        if change != "route":
            assert "ruta_especial_pendiente" in {i.code for i in eipd.issues}
        else:
            assert "excepcion_especial_no_validada" in {i.code for i in eipd.issues}


@pytest.mark.parametrize(
    "question",
    [
        "salud_perfil_biologico",
        "ninos_ninas",
        "adolescentes",
        "datos_sensibles_adolescentes_menores_16",
        "fines_historicos_estadisticos_cientificos_investigacion",
        "grupos_vulnerables",
    ],
)
def test_biometric_other_regimes_stay_blocked(
    biometric_context, negative_controls, question
):
    from app.services.licitud import evaluate_transversal_readiness_v1

    declaration = next(
        d for d in biometric_context[2]["declarations"] if d["question_id"] == question
    )
    declaration.update(
        answer="si",
        rationale="Alcance por revisar",
        data_category_codes=["id"],
        data_subject_codes=["clientes"],
    )
    special, _, blockers = evaluate_transversal_readiness_v1(
        biometric_state(biometric_context, negative_controls), biometric_context[1]
    )
    assert blockers and special.result != "regimenes_preparados"
    assert "biometricos_art16ter" in special.detected_regimes
