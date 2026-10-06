from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError

from app.schemas.licitud import LiaAssessmentV1, RatContextSnapshotV1
from app.services.lia import evaluate_lia_assessment_v1


@pytest.fixture
def lia_context():
    rat = {
        "purpose": "Gestión de clientes",
        "organization_role": "responsable",
        "data_categories": [
            {
                "category_code": "id",
                "category_name": "Identidad",
                "is_sensitive": False,
                "notes": None,
            }
        ],
        "data_subjects": [
            {
                "category_code": "clientes",
                "category_name": "Clientes",
                "includes_children": False,
                "includes_adolescents": False,
                "is_vulnerable_group": False,
                "notes": None,
            }
        ],
        "data_sources": [
            {"source_type": "titular", "description": None, "is_public_source": False}
        ],
        "retention": {"retention_rule": "5 años", "deletion_method": None},
        "automated_decisions": {"has_automated_decisions": False, "description": None},
        "systems": [],
        "third_parties": [],
        "international_transfers": [],
        "special_regimes": {
            "has_sensitive_data": False,
            "includes_children": False,
            "includes_adolescents": False,
            "has_vulnerable_groups": False,
        },
    }
    lia = {
        "purpose_and_interest": {
            "purpose_description": " Gestión DE clientes ",
            "legitimate_interest": "Interés documentado",
            "interest_holder": "responsable",
            "controller_benefit": "Beneficio",
            "interest_importance": "Importancia",
            "consequences_without_processing": "Consecuencias",
        },
        "necessity": {
            "contributes_to_purpose": {"answer": "si"},
            "linked_to_interest": {"answer": "si"},
            "achievable_without_personal_data": {"answer": "no"},
            "less_intrusive_alternative": {"answer": "no"},
            "fewer_data_possible": {"answer": "no"},
            "categories_necessary_and_relevant": {"answer": "si"},
            "necessity_analysis": "Necesidad",
            "proportionality_analysis": "Proporcionalidad",
            "alternatives_analysis": "Alternativas",
            "minimization_analysis": "Minimización",
        },
        "nature_and_scope": {"exclusively_professional_context": {"answer": "no"}},
        "reasonable_expectations": {
            "prior_relationship": {"answer": "no"},
            "significant_change_of_use": {"answer": "no"},
            "informed_at_direct_collection": {"answer": "si"},
            "foreseeable_purpose_and_method": {"answer": "si"},
            "innovative_processing": {"answer": "no"},
            "expectations_analysis": "Expectativas",
        },
        "impact": {
            "negative_effects": "Sin efectos adicionales identificados",
            "severity": "baja",
            "likelihood": "baja",
            "loss_of_control": {"answer": "no"},
            "intrusion_analysis": "Intrusión",
            "reasonable_opposition_likelihood": {"answer": "no"},
            "rights_and_freedoms_analysis": "Derechos",
            "transparently_explainable": {"answer": "si"},
            "relevant_unmitigated_impacts": {"answer": "no"},
            "impact_analysis": "Impacto",
        },
        "safeguards": {"safeguards_analysis": "No se proponen medidas adicionales"},
        "transparency_and_opposition": {
            "information_method": "Aviso",
            "interest_communication": "Explicación",
            "opposition_channel": "Portal",
            "opposition_procedure": "Procedimiento",
            "responsible_area": "Área",
        },
        "conclusion": {
            "balancing_summary": "Ponderación",
            "identified_interest": "Interés",
            "necessity_and_proportionality_result": "Resultado",
            "main_impacts": "Impactos",
            "relevant_safeguards": "Salvaguardas",
            "rights_protection_reasoning": "Razonamiento",
            "decision": "puede_basarse",
        },
    }
    return lia, rat


def set_path(data, path, value):
    section, field = path.split(".")
    data[section][field] = value


def application(result, path):
    return next(
        item.applicability for item in result.applicability if item.field == path
    )


def test_lia_completa_inmutable_preserva_y_repite(lia_context):
    lia, rat = lia_context
    original = deepcopy(lia_context)
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "completo"
    assert result.can_confirm
    assert result.issues == ()
    assert lia_context == original
    assert evaluate_lia_assessment_v1(lia, rat) == result
    assert (
        evaluate_lia_assessment_v1(
            LiaAssessmentV1.model_validate(lia),
            RatContextSnapshotV1.model_validate(rat),
        )
        == result
    )
    with pytest.raises(FrozenInstanceError):
        result.result = "incompleto"


@pytest.mark.parametrize(
    "path",
    [
        "purpose_and_interest.purpose_description",
        "purpose_and_interest.legitimate_interest",
        "purpose_and_interest.interest_importance",
        "purpose_and_interest.consequences_without_processing",
        "purpose_and_interest.controller_benefit",
        "necessity.necessity_analysis",
        "necessity.proportionality_analysis",
        "necessity.alternatives_analysis",
        "necessity.minimization_analysis",
        "reasonable_expectations.expectations_analysis",
        "impact.negative_effects",
        "impact.intrusion_analysis",
        "impact.rights_and_freedoms_analysis",
        "impact.impact_analysis",
        "safeguards.safeguards_analysis",
        "transparency_and_opposition.information_method",
        "transparency_and_opposition.interest_communication",
        "transparency_and_opposition.opposition_channel",
        "transparency_and_opposition.opposition_procedure",
        "transparency_and_opposition.responsible_area",
        "conclusion.balancing_summary",
        "conclusion.identified_interest",
        "conclusion.necessity_and_proportionality_result",
        "conclusion.main_impacts",
        "conclusion.relevant_safeguards",
        "conclusion.rights_protection_reasoning",
    ],
)
def test_textos_obligatorios_no_admiten_espacios(lia_context, path):
    lia, rat = lia_context
    set_path(lia, path, " \t ")
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "incompleto"
    assert any(
        item.field == path and item.code == "campo_obligatorio"
        for item in result.issues
    )


@pytest.mark.parametrize(
    "path",
    [
        "necessity.contributes_to_purpose",
        "necessity.linked_to_interest",
        "necessity.achievable_without_personal_data",
        "necessity.less_intrusive_alternative",
        "necessity.fewer_data_possible",
        "necessity.categories_necessary_and_relevant",
        "nature_and_scope.exclusively_professional_context",
        "reasonable_expectations.prior_relationship",
        "reasonable_expectations.significant_change_of_use",
        "reasonable_expectations.informed_at_direct_collection",
        "reasonable_expectations.foreseeable_purpose_and_method",
        "reasonable_expectations.innovative_processing",
        "impact.loss_of_control",
        "impact.reasonable_opposition_likelihood",
        "impact.transparently_explainable",
        "impact.relevant_unmitigated_impacts",
    ],
)
@pytest.mark.parametrize(
    "value,code",
    [
        (None, "campo_obligatorio"),
        ({"answer": "pendiente"}, "respuesta_pendiente"),
        ({"answer": "no_aplica"}, "no_aplica_invalido"),
    ],
)
def test_respuestas_aplicables_incompletas(lia_context, path, value, code):
    lia, rat = lia_context
    set_path(lia, path, value)
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "incompleto"
    assert any(item.field == path and item.code == code for item in result.issues)


@pytest.mark.parametrize(
    "path,value",
    [
        ("necessity.contributes_to_purpose", "no"),
        ("necessity.linked_to_interest", "no"),
        ("necessity.categories_necessary_and_relevant", "no"),
        ("necessity.achievable_without_personal_data", "si"),
        ("necessity.less_intrusive_alternative", "si"),
        ("reasonable_expectations.foreseeable_purpose_and_method", "no"),
        ("reasonable_expectations.informed_at_direct_collection", "no"),
        ("impact.transparently_explainable", "no"),
        ("impact.relevant_unmitigated_impacts", "si"),
    ],
)
def test_respuestas_revision_conservadas_con_medidas(lia_context, path, value):
    lia, rat = lia_context
    set_path(lia, path, {"answer": value})
    lia["safeguards"]["measures"] = [
        {"description": "Control", "mitigated_impact": "Impacto"}
    ]
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "requiere_revision"
    assert any(
        item.field == path and item.code == "respuesta_revision"
        for item in result.issues
    )


@pytest.mark.parametrize(
    "source_type", ["tercero", "fuente_publica", "recogida_automatica", "otro"]
)
@pytest.mark.parametrize(
    "direct_answer,expected",
    [(None, "completo"), ("no_aplica", "completo"), ("si", "requiere_revision")],
)
def test_fuentes_no_directas(lia_context, source_type, direct_answer, expected):
    lia, rat = lia_context
    rat["data_sources"][0]["source_type"] = source_type
    set_path(
        lia,
        "reasonable_expectations.informed_at_direct_collection",
        None if direct_answer is None else {"answer": direct_answer},
    )
    lia["reasonable_expectations"][
        "third_party_information"
    ] = "Información proporcionada"
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == expected
    assert (
        application(result, "reasonable_expectations.informed_at_direct_collection")
        == "no_aplicable"
    )


def test_fuentes_mixtas_y_vacias(lia_context):
    lia, rat = lia_context
    rat["data_sources"].append(
        {"source_type": "tercero", "description": None, "is_public_source": False}
    )
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "incompleto"
    assert (
        application(result, "reasonable_expectations.third_party_information")
        == "aplicable"
    )
    rat["data_sources"] = []
    result = evaluate_lia_assessment_v1(lia, rat)
    assert (
        application(result, "reasonable_expectations.informed_at_direct_collection")
        == "sin_resolver"
    )
    assert result.result == "incompleto"


@pytest.mark.parametrize("holder", [None, "responsable", "tercero", "ambos"])
def test_beneficios_segun_titular_del_interes(lia_context, holder):
    lia, rat = lia_context
    lia["purpose_and_interest"]["interest_holder"] = holder
    result = evaluate_lia_assessment_v1(lia, rat)
    expected = "completo" if holder == "responsable" else "incompleto"
    assert result.result == expected
    if holder is None:
        assert (
            application(result, "purpose_and_interest.controller_benefit")
            == "sin_resolver"
        )
    else:
        lia["purpose_and_interest"]["third_party_benefit"] = "Beneficio"
        assert evaluate_lia_assessment_v1(lia, rat).result == "completo"


def test_relacion_previa_y_texto_residual(lia_context):
    lia, rat = lia_context
    lia["reasonable_expectations"]["relationship_description"] = "Relación descrita"
    assert evaluate_lia_assessment_v1(lia, rat).result == "completo"
    lia["reasonable_expectations"]["prior_relationship"] = {"answer": "si"}
    lia["reasonable_expectations"]["relationship_description"] = ""
    assert evaluate_lia_assessment_v1(lia, rat).result == "incompleto"


@pytest.mark.parametrize(
    "flag",
    [
        "has_sensitive_data",
        "includes_children",
        "includes_adolescents",
        "has_vulnerable_groups",
    ],
)
def test_regimenes_desde_snapshot(lia_context, flag):
    lia, rat = lia_context
    rat["special_regimes"][flag] = True
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "incompleto"
    assert (
        application(result, "nature_and_scope.special_rules_description") == "aplicable"
    )
    lia["nature_and_scope"]["special_rules_description"] = "Régimen documentado"
    if flag != "has_sensitive_data":
        assert application(result, "impact.vulnerable_people_impact") == "aplicable"
        lia["impact"]["vulnerable_people_impact"] = "Impacto documentado"
    assert evaluate_lia_assessment_v1(lia, rat).result == "completo"


@pytest.mark.parametrize(
    "field,value",
    [
        ("severity", "media"),
        ("likelihood", "alta"),
        ("loss_of_control", {"answer": "si"}),
        ("reasonable_opposition_likelihood", {"answer": "si"}),
        ("relevant_unmitigated_impacts", {"answer": "si"}),
    ],
)
def test_medidas_exigidas_por_indicador(lia_context, field, value):
    lia, rat = lia_context
    lia["impact"][field] = value
    assert evaluate_lia_assessment_v1(lia, rat).result == "incompleto"
    lia["safeguards"]["measures"] = [{"description": "Control"}]
    result = evaluate_lia_assessment_v1(lia, rat)
    assert any(
        i.field == "safeguards.measures.0.mitigated_impact" for i in result.issues
    )
    lia["safeguards"]["measures"][0]["mitigated_impact"] = "Impacto"
    assert evaluate_lia_assessment_v1(lia, rat).result == (
        "requiere_revision" if field == "relevant_unmitigated_impacts" else "completo"
    )


@pytest.mark.parametrize("field", ["severity", "likelihood"])
@pytest.mark.parametrize("value", [None, "pendiente"])
def test_valoracion_sin_resolver_y_disparador_positivo(lia_context, field, value):
    lia, rat = lia_context
    lia["impact"][field] = value
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "incompleto"
    assert application(result, "safeguards.measures") == "sin_resolver"
    lia["impact"]["loss_of_control"] = {"answer": "si"}
    assert (
        application(evaluate_lia_assessment_v1(lia, rat), "safeguards.measures")
        == "aplicable"
    )


def test_descripcion_medida_opcional_no_puede_ser_vacia(lia_context):
    lia, rat = lia_context
    lia["safeguards"]["measures"] = [{"description": " ", "mitigated_impact": None}]
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "incompleto"
    assert result.issues[0].code == "medida_incompleta"


@pytest.mark.parametrize("decision", [None, "no_puede_basarse", "requiere_revision"])
def test_decision_no_bypassea(lia_context, decision):
    lia, rat = lia_context
    lia["conclusion"]["decision"] = decision
    assert evaluate_lia_assessment_v1(lia, rat).result == (
        "incompleto" if decision is None else "requiere_revision"
    )


def test_finalidad_distinta_precedencia_y_orden(lia_context):
    lia, rat = lia_context
    lia["purpose_and_interest"]["purpose_description"] = "Otra finalidad"
    lia["conclusion"]["balancing_summary"] = None
    rat["data_categories"] = []
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "incompleto"
    assert [i.field for i in result.issues] == [
        "rat_context_snapshot.data_categories",
        "purpose_and_interest.purpose_description",
        "conclusion.balancing_summary",
    ]
    assert result.issues[1].category == "requiere_revision"
    reordered = {
        key: dict(reversed(list(value.items())))
        for key, value in reversed(list(lia.items()))
    }
    assert evaluate_lia_assessment_v1(reordered, rat) == result


@pytest.mark.parametrize(
    "field,value",
    [
        ("purpose", " "),
        ("data_categories", []),
        ("data_subjects", []),
        ("organization_role", None),
    ],
)
def test_contexto_minimo(lia_context, field, value):
    lia, rat = lia_context
    rat[field] = value
    result = evaluate_lia_assessment_v1(lia, rat)
    assert result.result == "incompleto"
    assert result.issues[0].field == f"rat_context_snapshot.{field}"


@pytest.mark.parametrize("missing", ["lia", "rat", "both"])
def test_ausencia_de_expediente_o_snapshot(lia_context, missing):
    lia, rat = lia_context
    result = evaluate_lia_assessment_v1(
        None if missing != "rat" else lia, None if missing != "lia" else rat
    )
    assert result.result == "incompleto"
    assert not result.can_confirm


def test_rechaza_contrato_invalido_aunque_otro_input_ausente(lia_context):
    _, rat = lia_context
    with pytest.raises(ValidationError):
        evaluate_lia_assessment_v1({"schema_version": 2}, None)
    with pytest.raises(ValidationError):
        evaluate_lia_assessment_v1(None, {})
    model = LiaAssessmentV1()
    model.conclusion.decision = "aprobado"
    with pytest.raises(ValidationError):
        evaluate_lia_assessment_v1(model, rat)


def test_factores_no_producen_conclusion_aislada(lia_context):
    lia, rat = lia_context
    for field in ("significant_change_of_use", "innovative_processing"):
        lia["reasonable_expectations"][field] = {"answer": "si"}
    lia["necessity"]["fewer_data_possible"] = {"answer": "si"}
    assert evaluate_lia_assessment_v1(lia, rat).result == "completo"
