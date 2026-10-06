from copy import deepcopy
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.services.eipd import bind_eipd_screening_v8
from app.services.licitud import evaluate_transversal_readiness_v1
from app.services.sensitive_consent import (
    evaluate_sensitive_consent_assessment_v1 as evaluate,
)
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


@pytest.mark.parametrize(
    "method,grant",
    [
        ("escrito", "escrito"),
        ("verbal", "verbal"),
        ("tecnologico_equivalente", "electronico"),
    ],
)
def test_sensitive_complete_deterministic_immutable(sensitive_context, method, grant):
    document, rat, special, consent = sensitive_context
    document["expression_method"] = method
    consent["grant_method"] = grant
    if method != "tecnologico_equivalente":
        document.pop("technology_equivalence_analysis")
    before = deepcopy(sensitive_context)
    result = evaluate(*sensitive_context)
    assert result.result == "completo" and result.can_confirm
    assert result == evaluate(*sensitive_context)
    assert sensitive_context == before
    assert next(
        i.applicability
        for i in result.applicability
        if i.field == "technology_equivalence_analysis"
    ) == ("aplicable" if method == "tecnologico_equivalente" else "no_aplicable")


@pytest.mark.parametrize(
    "field",
    TEXTS
    + RESPONSES
    + ["scope", "expression_method", "technology_equivalence_analysis", "evidence"],
)
def test_sensitive_required(sensitive_context, field):
    sensitive_context[0].pop(field)
    result = evaluate(*sensitive_context)
    assert result.result == "incompleto"
    assert field in {i.field for i in result.issues}


@pytest.mark.parametrize("field", RESPONSES)
@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_sensitive_responses(sensitive_context, field, answer, expected):
    sensitive_context[0][field]["answer"] = answer
    assert evaluate(*sensitive_context).result == expected
    sensitive_context[0][field]["rationale"] = " "
    assert evaluate(*sensitive_context).result == "incompleto"


@pytest.mark.parametrize("giver", ["representante_legal", "mandatario"])
def test_sensitive_representation_review(sensitive_context, giver):
    sensitive_context[3]["given_by"] = giver
    assert "representacion_no_preparada" in {
        i.code for i in evaluate(*sensitive_context).issues
    }


@pytest.mark.parametrize(
    "grant", ["verbal", "escrito", "acto_afirmativo", "otro_documentado"]
)
def test_sensitive_method_discordant(sensitive_context, grant):
    sensitive_context[3]["grant_method"] = grant
    assert "medio_discordante" in {i.code for i in evaluate(*sensitive_context).issues}


@pytest.mark.parametrize("index", [0, 1, 2, 3])
def test_sensitive_missing_context(sensitive_context, index):
    args = list(sensitive_context)
    args[index] = None
    assert evaluate(*args).result == "incompleto"


@pytest.mark.parametrize("field", ["data_category_codes", "data_subject_codes"])
@pytest.mark.parametrize("target", ["own", "declaration", "condition"])
@pytest.mark.parametrize("values", [[], ["external"], ["id", " ID "]])
def test_sensitive_scopes_independent(sensitive_context, field, target, values):
    document, rat, special, consent = sensitive_context
    item = (
        document["scope"]
        if target == "own"
        else (
            next(
                d
                for d in special["declarations"]
                if d["question_id"] == "datos_sensibles"
            )
            if target == "declaration"
            else special["conditions"][0]
        )
    )
    item[field] = values
    if target != "own":
        document.pop("scope")
    issues = evaluate(*sensitive_context).issues
    assert any(
        i.code in {"alcance_vacio", "alcance_invalido"} and i.field.endswith(field)
        for i in issues
    )


@pytest.mark.parametrize(
    "kind", ["category", "subject", "ordinary", "flag", "role", "purpose"]
)
def test_sensitive_rat_coverage_and_coherence(sensitive_context, kind):
    document, rat, special, consent = sensitive_context
    if kind == "category":
        rat["data_categories"].append(
            {**rat["data_categories"][0], "category_code": "other"}
        )
    elif kind == "subject":
        rat["data_subjects"].append(
            {**rat["data_subjects"][0], "category_code": "other"}
        )
    elif kind == "ordinary":
        rat["data_categories"][0]["is_sensitive"] = False
    elif kind == "flag":
        rat["special_regimes"]["has_sensitive_data"] = False
    elif kind == "role":
        rat["organization_role"] = "encargado"
    else:
        document["purpose_description"] = "Otra finalidad"
    assert evaluate(*sensitive_context).result == "requiere_revision"


@pytest.mark.parametrize(
    "field,value",
    [
        ("authorization_route", "excepcion_legal"),
        ("authorization_route", None),
        ("sensitive_condition_id", "autorizacion_legal_art16f"),
        ("uses_consent_assessment", False),
        ("legal_reference", " "),
        ("documentary_analysis", " "),
        ("evidence", []),
    ],
)
def test_sensitive_condition(sensitive_context, field, value):
    sensitive_context[2]["conditions"][0][field] = value
    assert not evaluate(*sensitive_context).can_confirm


def test_sensitive_technology_residual_and_factual_dates(sensitive_context):
    document, rat, special, consent = sensitive_context
    document["expression_method"] = "verbal"
    consent["grant_method"] = "verbal"
    assert "campo_residual" in {i.code for i in evaluate(*sensitive_context).issues}
    document.pop("technology_equivalence_analysis")
    document["declaration_obtained_on"] = "1900-01-01"
    document["declaration_version_reference"] = None
    assert evaluate(*sensitive_context).can_confirm


def test_sensitive_checklist_and_evidence(sensitive_context):
    sensitive_context[3]["answers"][0]["answer"] = "no"
    sensitive_context[0]["evidence"][0]["reference"] = " "
    result = evaluate(*sensitive_context)
    assert result.result == "incompleto"
    assert any(i.field.startswith("consent_assessment.") for i in result.issues)
    assert "evidencia_incompleta" in {i.code for i in result.issues}


@pytest.mark.parametrize(
    "index,data",
    [
        (0, {"approved": True}),
        (1, {"purpose": 7}),
        (2, {"conditions": [{"regime_id": "unknown"}]}),
        (3, {"grant_method": "unknown"}),
    ],
)
def test_sensitive_invalid_contracts(sensitive_context, index, data):
    sensitive_context[index].update(data)
    with pytest.raises(ValidationError):
        evaluate(*sensitive_context)


def transversal_state(context, controls, geo=None):
    document, rat, special, consent = context
    special = bind_special_conditions_v7(
        {k: v for k, v in special.items() if k != "context_binding"},
        rat,
        "consentimiento_art12",
        consent,
        None,
        None,
        None,
        None,
        None,
        geo,
        document,
    ).model_dump(mode="json")
    eipd = bind_eipd_screening_v8(
        controls["eipd_screening"],
        rat,
        None,
        special,
        None,
        None,
        None,
        None,
        geo,
        document,
    ).model_dump(mode="json")
    return SimpleNamespace(
        health_assessment=None,
        legal_basis="consentimiento_art12",
        consent_assessment=consent,
        lia_assessment=None,
        contract_assessment=None,
        legal_obligation_assessment=None,
        rights_defense_assessment=None,
        economic_obligations_assessment=None,
        geolocation_assessment=geo,
        sensitive_consent_assessment=document,
        special_conditions=special,
        eipd_screening=eipd,
    )


@pytest.mark.parametrize("index", range(5))
def test_sensitive_transversal_eipd_positive(
    sensitive_context, negative_controls, index
):
    negative_controls["eipd_screening"]["answers"][index]["answer"] = "si"
    state = transversal_state(sensitive_context, negative_controls)
    special, eipd, blockers = evaluate_transversal_readiness_v1(
        state, sensitive_context[1]
    )
    assert special.result == "regimenes_preparados"
    assert eipd.result != "sin_supuestos_declarados"
    assert "screening_eipd_no_preparado" in {b["code"] for b in blockers}


@pytest.mark.parametrize(
    "question",
    [
        "salud_perfil_biologico",
        "biometricos_identificacion_unica",
        "ninos_ninas",
        "adolescentes",
        "datos_sensibles_adolescentes_menores_16",
        "fines_historicos_estadisticos_cientificos_investigacion",
        "grupos_vulnerables",
    ],
)
def test_sensitive_transversal_concurrent_regimes(
    sensitive_context, negative_controls, question
):
    declaration = next(
        i for i in sensitive_context[2]["declarations"] if i["question_id"] == question
    )
    declaration.update(
        answer="si", data_category_codes=["id"], data_subject_codes=["clientes"]
    )
    state = transversal_state(sensitive_context, negative_controls)
    special, _, blockers = evaluate_transversal_readiness_v1(
        state, sensitive_context[1]
    )
    assert "sensibles_art16" in special.detected_regimes
    assert special.result != "regimenes_preparados" and blockers


def test_sensitive_and_geolocation_transversal(
    sensitive_context, negative_controls, complete_geolocation, geolocation_controls
):
    special = sensitive_context[2]
    declaration = next(
        i for i in special["declarations"] if i["question_id"] == "geolocalizacion"
    )
    declaration.update(
        answer="si", data_category_codes=["id"], data_subject_codes=["clientes"]
    )
    special["conditions"].extend(
        geolocation_controls["special_conditions"]["conditions"]
    )
    state = transversal_state(
        sensitive_context, negative_controls, complete_geolocation
    )
    before = deepcopy((vars(state), sensitive_context[1]))
    special, eipd, blockers = evaluate_transversal_readiness_v1(
        state, sensitive_context[1]
    )
    assert special.detected_regimes == (
        "geolocalizacion_art16sexies",
        "sensibles_art16",
    )
    assert special.result == "regimenes_preparados" and not blockers
    assert (vars(state), sensitive_context[1]) == before


@pytest.mark.parametrize(
    "change",
    ["missing", "pending", "stale", "other_route", "consent_missing", "representation"],
)
def test_sensitive_transversal_blockers(sensitive_context, negative_controls, change):
    if change == "other_route":
        sensitive_context[2]["conditions"][0]["authorization_route"] = "excepcion_legal"
    if change == "representation":
        sensitive_context[3]["given_by"] = "representante_legal"
    state = transversal_state(sensitive_context, negative_controls)
    if change == "missing":
        state.sensitive_consent_assessment = None
    elif change == "pending":
        state.sensitive_consent_assessment["proof_available"]["answer"] = "pendiente"
    elif change == "stale":
        state.sensitive_consent_assessment["notes"] = "Cambio"
    elif change == "consent_missing":
        state.consent_assessment = None
    special, eipd, blockers = evaluate_transversal_readiness_v1(
        state, sensitive_context[1]
    )
    assert blockers
    if change != "stale":
        assert "consentimiento_sensible_no_preparado" in {b["code"] for b in blockers}
    if change == "other_route":
        assert "validador_no_implementado" in {i.code for i in special.issues}
