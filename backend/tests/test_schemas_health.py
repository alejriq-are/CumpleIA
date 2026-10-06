import pytest
from pydantic import ValidationError

from app.schemas.licitud import HealthAssessmentV1, HealthLegalReferenceV1

RESPONSES = [
    "sanitary_purpose_covered",
    "restricted_context_authorization_documented",
    "includes_data_cession",
    "includes_identifiable_biological_samples",
]


def test_health_empty_partial_and_independent_lists():
    first, second = HealthAssessmentV1(), HealthAssessmentV1()
    assert first.route is None and first.scope is None
    assert HealthLegalReferenceV1().model_dump(mode="json") == {
        "norm_name": None,
        "provision": None,
        "official_source_url": None,
        "applicability_analysis": None,
    }
    for field in [
        "collection_contexts",
        "sanitary_law_references",
        "restricted_context_legal_references",
        "evidence",
    ]:
        assert getattr(first, field) == []
        assert getattr(first, field) is not getattr(second, field)


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
        "otro",
    ],
)
def test_health_context_draft(context):
    document = HealthAssessmentV1(
        collection_contexts=[context], route="consentimiento_expreso"
    )
    assert document.collection_contexts == [context]
    # Completeness and applicability are evaluated later, not during draft validation.
    assert document.collection_context_analysis is None


def test_health_multiple_contexts_keep_order():
    contexts = ["otro", "laboral", "social"]
    assert (
        HealthAssessmentV1(collection_contexts=contexts).model_dump()[
            "collection_contexts"
        ]
        == contexts
    )


@pytest.mark.parametrize("field", RESPONSES)
@pytest.mark.parametrize("answer", ["si", "no", "pendiente"])
def test_health_responses_allow_partial_draft(field, answer):
    document = HealthAssessmentV1.model_validate({field: {"answer": answer}})
    assert document.model_dump()[field] == {"answer": answer, "rationale": None}


@pytest.mark.parametrize("scheme", ["http", "https"])
def test_health_reference_and_factual_date_serialization(scheme):
    document = HealthAssessmentV1.model_validate(
        {
            "sanitary_law_references": [
                {
                    "norm_name": "Norma por documentar",
                    "provision": "Artículo por identificar",
                    "official_source_url": scheme + "://example.test/norma",
                }
            ],
            "restricted_context_legal_references": [{}],
            "evidence": [{"evidence_type": "registro", "obtained_on": "1900-01-01"}],
        }
    )
    serialized = document.model_dump(mode="json")
    assert (
        serialized["sanitary_law_references"][0]["official_source_url"]
        == scheme + "://example.test/norma"
    )
    assert serialized["evidence"][0]["obtained_on"] == "1900-01-01"
    assert serialized["restricted_context_legal_references"][0]["norm_name"] is None


@pytest.mark.parametrize(
    "data",
    [
        {"approved": True},
        {"result": "completo"},
        {"can_confirm": True},
        {"schema_version": 2},
        {"route": "excepcion_legal"},
        {"collection_contexts": ["unknown"]},
        {"collection_contexts": ["laboral", "laboral"]},
        {"collection_contexts": None},
        {"sanitary_law_references": [{"unknown": True}]},
        {"restricted_context_legal_references": [{"unknown": True}]},
        {"scope": {"unknown": True}},
        {"scope": {"data_category_codes": [" "]}},
        {"scope": {"data_subject_codes": ["clientes", "clientes"]}},
        {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
        {"evidence": [{"evidence_type": "registro", "approved": True}]},
    ]
    + [{field: {"answer": "no_aplica"}} for field in RESPONSES],
)
def test_health_closed_contract(data):
    with pytest.raises(ValidationError):
        HealthAssessmentV1.model_validate(data)


@pytest.mark.parametrize(
    "url", ["invalid", "ftp://example.test/norma", "file:///norma"]
)
@pytest.mark.parametrize(
    "field", ["sanitary_law_references", "restricted_context_legal_references"]
)
def test_health_reference_invalid_url(field, url):
    with pytest.raises(ValidationError):
        HealthAssessmentV1.model_validate({field: [{"official_source_url": url}]})
