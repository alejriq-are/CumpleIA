from copy import deepcopy
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.services.eipd import bind_eipd_screening_v9
from app.services.health import evaluate_health_assessment_v1 as evaluate
from app.services.licitud import evaluate_transversal_readiness_v1
from app.services.special_conditions import (
    bind_special_conditions_v7,
    bind_special_conditions_v8,
)

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


@pytest.fixture
def health_context(sensitive_context):
    sensitive, rat, special, consent = sensitive_context
    scope = deepcopy(sensitive["scope"])
    for declaration in special["declarations"]:
        if declaration["question_id"] == "salud_perfil_biologico":
            declaration.update(answer="si", rationale="Datos de salud", **scope)
    special["conditions"].append(
        {
            "regime_id": "salud_perfil_biologico_art16bis",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
            "legal_reference": "art16bis",
            "documentary_analysis": "Revisión documentada",
            "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
            **scope,
        }
    )
    health = {
        "purpose_description": rat["purpose"],
        "health_data_description": "Datos de salud",
        "processing_operations": "Operaciones documentadas",
        "scope": scope,
        "route": "consentimiento_expreso",
        "sanitary_law_references": [
            {
                "norm_name": "Norma por revisar",
                "provision": "Artículo por identificar",
                "official_source_url": "https://example.test/norma",
                "applicability_analysis": "Aplicabilidad documentada",
            }
        ],
        "sanitary_purpose_analysis": "Finalidad documentada",
        "sanitary_purpose_covered": {
            "answer": "si",
            "rationale": "Cobertura documentada",
        },
        "collection_contexts": ["otro"],
        "collection_context_analysis": "Contexto de recolección documentado",
        "includes_data_cession": {"answer": "no", "rationale": "Sin cesión"},
        "includes_identifiable_biological_samples": {
            "answer": "no",
            "rationale": "Sin muestras",
        },
        "evidence": [{"evidence_type": "registro", "reference": "Registro"}],
    }
    return health, rat, special, consent, sensitive


def test_health_complete_immutable_deterministic(health_context):
    before = deepcopy(health_context)
    result = evaluate(*health_context)
    assert result.result == "completo" and result.can_confirm
    assert result == evaluate(*health_context)
    assert health_context == before
    own = [
        i
        for i in result.applicability
        if not i.field.startswith(
            ("consent_assessment", "sensitive_consent_assessment")
        )
    ]
    assert all(i.applicability == "no_aplicable" for i in own)


@pytest.mark.parametrize(
    "field",
    [
        "purpose_description",
        "health_data_description",
        "processing_operations",
        "scope",
        "route",
        "sanitary_law_references",
        "sanitary_purpose_analysis",
        "sanitary_purpose_covered",
        "collection_contexts",
        "collection_context_analysis",
        "includes_data_cession",
        "includes_identifiable_biological_samples",
        "evidence",
    ],
)
def test_health_required(health_context, field):
    health_context[0].pop(field)
    result = evaluate(*health_context)
    assert result.result == "incompleto"
    assert any(
        i.field == field or i.field.startswith(field + ".") for i in result.issues
    )


@pytest.mark.parametrize(
    "factual,conditional",
    [
        ("includes_data_cession", "cession_description"),
        ("includes_identifiable_biological_samples", "biological_samples_analysis"),
    ],
)
@pytest.mark.parametrize("answer", ["si", "no", "pendiente"])
def test_health_conditionals(health_context, factual, conditional, answer):
    health = health_context[0]
    health[factual]["answer"] = answer
    result = evaluate(*health_context)
    assert (
        next(i.applicability for i in result.applicability if i.field == conditional)
        == {"si": "aplicable", "no": "no_aplicable", "pendiente": "sin_resolver"}[
            answer
        ]
    )
    assert result.result == ("completo" if answer == "no" else "incompleto")
    health[conditional] = "Descripción documentada"
    assert (
        evaluate(*health_context).result
        == {"si": "completo", "no": "requiere_revision", "pendiente": "incompleto"}[
            answer
        ]
    )


@pytest.mark.parametrize(
    "context",
    [
        "laboral",
        "educativo",
        "deportivo",
        "social",
        "seguros",
        "seguridad",
        "identificacion",
    ],
)
def test_health_restricted_stays_review_with_complete_authorization(
    health_context, context
):
    health = health_context[0]
    health["collection_contexts"] = ["otro", context]
    assert evaluate(*health_context).result == "incompleto"
    health["restricted_context_legal_references"] = deepcopy(
        health["sanitary_law_references"]
    )
    health["restricted_context_analysis"] = "Aplicabilidad documentada"
    health["restricted_context_authorization_documented"] = {
        "answer": "si",
        "rationale": "Referencia aportada",
    }
    result = evaluate(*health_context)
    assert result.result == "requiere_revision"
    assert "contexto_restringido_no_preparado" in {i.code for i in result.issues}


@pytest.mark.parametrize(
    "field,value",
    [
        ("restricted_context_legal_references", [{}]),
        ("restricted_context_analysis", "Análisis"),
        ("restricted_context_authorization_documented", {"answer": "si"}),
    ],
)
def test_health_restricted_residual(health_context, field, value):
    health_context[0][field] = value
    assert evaluate(*health_context).result == "requiere_revision"


@pytest.mark.parametrize(
    "field", ["norm_name", "provision", "official_source_url", "applicability_analysis"]
)
def test_health_references_required(health_context, field):
    health_context[0]["sanitary_law_references"][0].pop(field)
    assert "referencia_incompleta" in {i.code for i in evaluate(*health_context).issues}


@pytest.mark.parametrize("index", range(5))
def test_health_missing_dependency(health_context, index):
    args = list(health_context)
    args[index] = None
    result = evaluate(*args)
    assert result.result == "incompleto"
    if index == 2:
        assert any(
            i.field == "special_conditions.conditions.salud_perfil_biologico_art16bis"
            and i.code == "expediente_regimen_ausente"
            for i in result.issues
        )


@pytest.mark.parametrize(
    "field",
    [
        "sanitary_purpose_covered",
        "includes_data_cession",
        "includes_identifiable_biological_samples",
    ],
)
def test_health_response_rationale(health_context, field):
    health_context[0][field]["rationale"] = " "
    assert evaluate(*health_context).result == "incompleto"


@pytest.mark.parametrize("target", ["own", "declaration", "condition"])
@pytest.mark.parametrize("codes", [[], ["external"], ["id", " ID "]])
def test_health_scope_independent(health_context, target, codes):
    health, rat, special, consent, sensitive = health_context
    item = (
        health["scope"]
        if target == "own"
        else (
            next(
                i
                for i in special["declarations"]
                if i["question_id"] == "salud_perfil_biologico"
            )
            if target == "declaration"
            else special["conditions"][-1]
        )
    )
    item["data_category_codes"] = codes
    if target != "own":
        health.pop("scope")
    assert any(
        i.code in ("alcance_vacio", "alcance_invalido")
        and "data_category_codes" in i.field
        for i in evaluate(*health_context).issues
    )


@pytest.mark.parametrize(
    "change",
    [
        "purpose",
        "role",
        "partial",
        "ordinary",
        "condition_route",
        "reference",
        "representation",
        "sensitive_pending",
        "consent_no",
    ],
)
def test_health_coherence_dependency(health_context, change):
    health, rat, special, consent, sensitive = health_context
    if change == "purpose":
        health["purpose_description"] = "Otra finalidad"
    elif change == "role":
        rat["organization_role"] = "encargado"
    elif change == "partial":
        rat["data_categories"].append(
            {**rat["data_categories"][0], "category_code": "other"}
        )
    elif change == "ordinary":
        rat["data_categories"][0]["is_sensitive"] = False
    elif change == "condition_route":
        special["conditions"][-1]["authorization_route"] = "excepcion_legal"
    elif change == "reference":
        special["conditions"][-1]["uses_consent_assessment"] = False
    elif change == "representation":
        consent["given_by"] = "representante_legal"
    elif change == "sensitive_pending":
        sensitive["proof_available"]["answer"] = "pendiente"
    else:
        consent["answers"][0]["answer"] = "no"
    assert not evaluate(*health_context).can_confirm


@pytest.mark.parametrize(
    "data",
    [
        {"approved": True},
        {"collection_contexts": ["unknown"]},
        {"route": "excepcion_legal"},
        {"sanitary_law_references": [{"official_source_url": "ftp://example.test"}]},
    ],
)
def test_health_invalid_contract(health_context, data):
    health_context[0].update(data)
    with pytest.raises(ValidationError):
        evaluate(*health_context)


def test_health_date_optional_and_numeric_issue_order(health_context):
    health_context[0]["evidence"] = [
        {"evidence_type": "registro", "reference": " ", "obtained_on": "1900-01-01"}
        for _ in range(12)
    ]
    result = evaluate(*health_context)
    assert [i.field for i in result.issues if i.field.startswith("evidence.")] == [
        f"evidence.{i}.reference" for i in range(12)
    ]


def health_state(context, controls, geo=None):
    health, rat, special, consent, sensitive = context
    special = bind_special_conditions_v8(
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
        sensitive,
        health,
    ).model_dump(mode="json")
    eipd = bind_eipd_screening_v9(
        controls["eipd_screening"],
        rat,
        None,
        special,
        None,
        None,
        None,
        None,
        geo,
        sensitive,
        health,
    ).model_dump(mode="json")
    return SimpleNamespace(
        legal_basis="consentimiento_art12",
        consent_assessment=consent,
        lia_assessment=None,
        contract_assessment=None,
        legal_obligation_assessment=None,
        rights_defense_assessment=None,
        economic_obligations_assessment=None,
        geolocation_assessment=geo,
        sensitive_consent_assessment=sensitive,
        health_assessment=health,
        special_conditions=special,
        eipd_screening=eipd,
    )


@pytest.mark.parametrize("index", range(5))
def test_health_eipd_positive(health_context, negative_controls, index):
    negative_controls["eipd_screening"]["answers"][index]["answer"] = "si"
    state = health_state(health_context, negative_controls)
    special, eipd, blockers = evaluate_transversal_readiness_v1(
        state, health_context[1]
    )
    assert special.result == "regimenes_preparados"
    assert "screening_eipd_no_preparado" in {i["code"] for i in blockers}


@pytest.mark.parametrize(
    "question",
    [
        "biometricos_identificacion_unica",
        "ninos_ninas",
        "adolescentes",
        "datos_sensibles_adolescentes_menores_16",
        "fines_historicos_estadisticos_cientificos_investigacion",
        "grupos_vulnerables",
    ],
)
def test_health_concurrent_regimes(health_context, negative_controls, question):
    declaration = next(
        i for i in health_context[2]["declarations"] if i["question_id"] == question
    )
    declaration.update(
        answer="si", data_category_codes=["id"], data_subject_codes=["clientes"]
    )
    state = health_state(health_context, negative_controls)
    special, _, blockers = evaluate_transversal_readiness_v1(state, health_context[1])
    assert special.result != "regimenes_preparados" and blockers
    assert "salud_perfil_biologico_art16bis" in special.detected_regimes


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "stale",
        "pending",
        "route",
        "sensitive_missing",
        "checklist_missing",
        "restricted",
    ],
)
def test_health_transversal_blockers(health_context, negative_controls, change):
    if change == "restricted":
        health_context[0]["collection_contexts"] = ["laboral"]
    elif change == "route":
        health_context[2]["conditions"][-1]["authorization_route"] = "excepcion_legal"
    state = health_state(health_context, negative_controls)
    if change == "missing":
        state.health_assessment = None
    elif change == "stale":
        state.health_assessment["notes"] = "Cambio"
    elif change == "pending":
        state.health_assessment["sanitary_purpose_covered"]["answer"] = "pendiente"
    elif change == "sensitive_missing":
        state.sensitive_consent_assessment = None
    elif change == "checklist_missing":
        state.consent_assessment = None
    special, eipd, blockers = evaluate_transversal_readiness_v1(
        state, health_context[1]
    )
    assert blockers
    if change == "stale":
        assert not special.context_current and not eipd.context_current
    else:
        assert "salud_no_preparada" in {i["code"] for i in blockers}


def test_health_sensitive_geolocation_all_prepared(
    health_context, negative_controls, complete_geolocation, geolocation_controls
):
    special = health_context[2]
    declaration = next(
        i for i in special["declarations"] if i["question_id"] == "geolocalizacion"
    )
    declaration.update(
        answer="si", data_category_codes=["id"], data_subject_codes=["clientes"]
    )
    special["conditions"].extend(
        geolocation_controls["special_conditions"]["conditions"]
    )
    state = health_state(health_context, negative_controls, complete_geolocation)
    before = deepcopy((vars(state), health_context[1]))
    special, eipd, blockers = evaluate_transversal_readiness_v1(
        state, health_context[1]
    )
    assert special.detected_regimes == (
        "geolocalizacion_art16sexies",
        "salud_perfil_biologico_art16bis",
        "sensibles_art16",
    )
    assert special.result == "regimenes_preparados" and not blockers
    assert (vars(state), health_context[1]) == before
