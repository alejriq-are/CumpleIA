from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.services.geolocation import evaluate_geolocation_assessment_v1 as evaluate

TEXTS = [
    "purpose_description",
    "geolocation_data_description",
    "processing_operations",
    "duration_description",
    "notice_reference",
    "notice_version_reference",
    "notice_delivery_mechanism",
    "notice_content_analysis",
    "third_party_disclosure_description",
]
RESPONSES = [
    "information_clear",
    "information_sufficient",
    "information_timely",
    "data_types_disclosed",
    "purpose_disclosed",
    "duration_disclosed",
    "third_party_information_disclosed",
]
CONDITIONAL = ["value_added_service_description", "third_party_recipient_description"]


@pytest.mark.parametrize("answer", ["si", "no"])
def test_geo_completo_inmutable(geolocation_context, answer):
    geo, rat, special = geolocation_context
    geo["value_added_third_party_transfer"]["answer"] = answer
    if answer == "no":
        for field in CONDITIONAL:
            geo.pop(field)
    before = deepcopy((geo, rat, special))
    result = evaluate(geo, rat, special)
    assert result.result == "completo" and result.can_confirm
    assert result == evaluate(geo, rat, special) and (geo, rat, special) == before
    assert {i.applicability for i in result.applicability} == {
        "aplicable" if answer == "si" else "no_aplicable"
    }


@pytest.mark.parametrize(
    "field",
    TEXTS + RESPONSES + ["scope", "value_added_third_party_transfer", "evidence"],
)
def test_geo_faltantes(geolocation_context, field):
    geo, rat, special = geolocation_context
    geo.pop(field)
    result = evaluate(geo, rat, special)
    assert result.result == "incompleto"
    assert field in {i.field for i in result.issues}


@pytest.mark.parametrize("field", RESPONSES)
@pytest.mark.parametrize(
    "answer,expected", [("no", "requiere_revision"), ("pendiente", "incompleto")]
)
def test_geo_respuestas_precedencia(geolocation_context, field, answer, expected):
    geo, rat, special = geolocation_context
    geo[field]["answer"] = answer
    assert evaluate(geo, rat, special).result == expected
    geo[field]["rationale"] = " "
    assert evaluate(geo, rat, special).result == "incompleto"


@pytest.mark.parametrize("field", CONDITIONAL)
@pytest.mark.parametrize(
    "change,expected", [("missing", "incompleto"), ("residual", "requiere_revision")]
)
def test_geo_condicionales(geolocation_context, field, change, expected):
    geo, rat, special = geolocation_context
    if change == "missing":
        geo.pop(field)
    else:
        geo["value_added_third_party_transfer"]["answer"] = "no"
        for other in CONDITIONAL:
            if other != field:
                geo.pop(other)
    result = evaluate(geo, rat, special)
    assert result.result == expected and field in {i.field for i in result.issues}


@pytest.mark.parametrize("answer", [None, "pendiente"])
def test_geo_factual_sin_resolver(geolocation_context, answer):
    geo, rat, special = geolocation_context
    geo["value_added_third_party_transfer"] = (
        None if answer is None else {"answer": answer}
    )
    for field in CONDITIONAL:
        geo.pop(field)
    result = evaluate(geo, rat, special)
    assert result.result == "incompleto"
    assert {i.applicability for i in result.applicability} == {"sin_resolver"}
    assert all(i.field not in CONDITIONAL for i in result.issues)


@pytest.mark.parametrize(
    "change,expected",
    [
        ("purpose", "requiere_revision"),
        ("role", "requiere_revision"),
        ("scope_empty", "incompleto"),
        ("scope_outside", "requiere_revision"),
        ("scope_duplicate", "requiere_revision"),
        ("scope_mismatch", "requiere_revision"),
        ("condition_absent", "incompleto"),
        ("declaration_absent", "incompleto"),
        ("declaration_no", "requiere_revision"),
        ("route", "requiere_revision"),
        ("consent_reference", "requiere_revision"),
        ("reference", "incompleto"),
        ("analysis", "incompleto"),
        ("condition_evidence", "incompleto"),
        ("evidence", "incompleto"),
    ],
)
def test_geo_contexto_y_expediente(geolocation_context, change, expected):
    geo, rat, special = geolocation_context
    condition = special["conditions"][0]
    declaration = next(
        d for d in special["declarations"] if d["question_id"] == "geolocalizacion"
    )
    if change == "purpose":
        geo["purpose_description"] = "Otra finalidad"
    elif change == "role":
        rat["organization_role"] = "encargado"
    elif change == "scope_empty":
        geo["scope"]["data_category_codes"] = []
    elif change == "scope_outside":
        geo["scope"]["data_category_codes"] = ["otro"]
    elif change == "scope_duplicate":
        geo["scope"]["data_category_codes"] = ["id", " ID "]
    elif change == "scope_mismatch":
        rat["data_categories"].append(
            {**rat["data_categories"][0], "category_code": "otro"}
        )
        geo["scope"]["data_category_codes"] = ["otro"]
    elif change == "condition_absent":
        special["conditions"] = []
    elif change == "declaration_absent":
        special["declarations"].remove(declaration)
    elif change == "declaration_no":
        declaration["answer"] = "no"
    elif change == "route":
        condition["authorization_route"] = "excepcion_legal"
    elif change == "consent_reference":
        condition["uses_consent_assessment"] = True
    elif change == "reference":
        condition["legal_reference"] = " "
    elif change == "analysis":
        condition["documentary_analysis"] = None
    elif change == "condition_evidence":
        condition["evidence"].append({"evidence_type": " "})
    elif change == "evidence":
        geo["evidence"].append({"evidence_type": " "})
    assert evaluate(geo, rat, special).result == expected
    geo["duration_description"] = " "
    assert evaluate(geo, rat, special).result == "incompleto"


def test_geo_validacion_ausencia_orden_canonizacion(geolocation_context):
    geo, rat, special = geolocation_context
    assert evaluate(None, None, None).result == "incompleto"
    for args in (({"approved": True}, None, None), (None, {}, None), (None, None, {})):
        with pytest.raises(ValidationError):
            evaluate(*args)
    geo["purpose_description"] = " GESTIÓN de clientes "
    geo["scope"]["data_category_codes"] = [" ID "]
    geo["notice_provided_on"] = "2000-01-01"
    assert evaluate(geo, rat, special).result == "completo"
    geo["information_clear"] = {"answer": "pendiente"}
    assert [i.field for i in evaluate(geo, rat, special).issues] == [
        "information_clear.answer",
        "information_clear.rationale",
    ]


@pytest.mark.parametrize("field", ["data_category_codes", "data_subject_codes"])
def test_geo_scope_externo_aun_sin_scope_propio(geolocation_context, field):
    geo, rat, special = geolocation_context
    geo["scope"] = None
    special["conditions"][0][field] = ["fuera"]
    result = evaluate(geo, rat, special)
    assert result.result == "incompleto"
    assert "alcance_invalido" in {i.code for i in result.issues}


@pytest.mark.parametrize(
    "change",
    [
        "declaration_pending",
        "declaration_scope_empty",
        "condition_route_none",
        "condition_evidence_absent",
    ],
)
def test_geo_faltantes_especiales(geolocation_context, change):
    geo, rat, special = geolocation_context
    d = next(
        d for d in special["declarations"] if d["question_id"] == "geolocalizacion"
    )
    c = special["conditions"][0]
    if change == "declaration_pending":
        d["answer"] = "pendiente"
    elif change == "declaration_scope_empty":
        d["data_subject_codes"] = []
    elif change == "condition_route_none":
        c["authorization_route"] = None
    else:
        c["evidence"] = []
    assert evaluate(geo, rat, special).result == "incompleto"
