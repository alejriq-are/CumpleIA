from datetime import date
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    EipdAgencyConsultationV1,
    EipdMeasureV1,
    EipdOfficialSourcesV1,
    EipdOfficialSourceV1,
    EipdResolutionAssessmentStoredV1,
    EipdResolutionAssessmentV1,
    EipdResolutionContextBindingV1,
    EipdResolutionReviewIn,
    EipdResolutionReviewOut,
    EipdResolutionReviewStateOut,
    EipdRiskV1,
)

PARTIAL_MODELS = [
    EipdRiskV1,
    EipdMeasureV1,
    EipdOfficialSourceV1,
    EipdOfficialSourcesV1,
    EipdAgencyConsultationV1,
    EipdResolutionAssessmentV1,
    EipdResolutionAssessmentStoredV1,
]
RESPONSE_FIELDS = [
    (EipdResolutionAssessmentV1, f)
    for f in [
        "necessary_for_purpose",
        "proportionate_processing",
        "minimization_addressed",
        "performed_before_processing",
    ]
] + [
    (EipdMeasureV1, "implemented"),
    (EipdAgencyConsultationV1, "recommendations_addressed"),
]


@pytest.mark.parametrize("model", PARTIAL_MODELS)
def test_partial_documents_and_independent_lists(model):
    first, second = model(), model()
    for name in model.model_fields:
        value = getattr(first, name)
        if isinstance(value, list):
            assert value == [] and value is not getattr(second, name)
        elif name != "schema_version":
            assert value is None


@pytest.mark.parametrize("model", PARTIAL_MODELS)
def test_nested_contracts_are_closed(model):
    with pytest.raises(ValidationError):
        model.model_validate({"approved": True})


@pytest.mark.parametrize(
    "field",
    [
        "context_binding",
        "document_hash",
        "context_hash",
        "created_by",
        "created_at",
        "organization_id",
        "assessment_id",
        "decision",
        "review_status",
        "latest_review",
        "can_confirm",
    ],
)
def test_editable_document_rejects_server_metadata(field):
    with pytest.raises(ValidationError):
        EipdResolutionAssessmentV1.model_validate({field: None})


@pytest.mark.parametrize("model,field", RESPONSE_FIELDS)
@pytest.mark.parametrize("answer", ["si", "no", "pendiente"])
def test_responses_allow_partial_rationale(model, field, answer):
    assert model.model_validate({field: {"answer": answer}}).model_dump()[field] == {
        "answer": answer,
        "rationale": None,
    }


@pytest.mark.parametrize("model,field", RESPONSE_FIELDS)
def test_no_aplica_cannot_suppress_controls(model, field):
    with pytest.raises(ValidationError):
        model.model_validate({field: {"answer": "no_aplica"}})


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": 2},
        {"residual_risk_level": "bajo"},
        {"completed_on": "invalid"},
        {"risks": None},
        {"measures": None},
        {"evidence": None},
        {"risks": [{"score": 1}]},
        {"measures": [{"implemented": {"answer": "si", "approved": True}}]},
        {"official_sources": {"status": "verificado"}},
        {"official_sources": {"checked_on": "invalid"}},
        {"official_sources": {"sources": [{"applicability": "otra"}]}},
        {"agency_consultation": {"status": "aprobada"}},
        {"evidence": [{"reference": "informe"}]},
        {"scope": {"data_category_codes": [" "]}},
        {"scope": {"data_subject_codes": ["clientes", "clientes"]}},
        {"scope": {"approved": True}},
    ],
)
def test_invalid_document_structure(payload):
    with pytest.raises(ValidationError):
        EipdResolutionAssessmentV1.model_validate(payload)


@pytest.mark.parametrize("level", ["no_alto", "alto", "sin_resolver"])
@pytest.mark.parametrize("status", ["no_solicitada", "en_curso", "concluida"])
def test_conditionals_remain_partial_until_readiness(level, status):
    doc = EipdResolutionAssessmentV1(
        residual_risk_level=level,
        agency_consultation={"status": status},
        risks=[{"risk_id": "A"}, {"risk_id": " a "}],
        measures=[{"risk_ids": ["unknown"]}],
        official_sources={"status": "no_identificado"},
    )
    assert doc.agency_consultation.status == status
    assert doc.risks[1].risk_id == " a "
    assert doc.measures[0].risk_ids == ["unknown"]


def test_nested_json_roundtrip_and_binding_separation():
    editable = EipdResolutionAssessmentV1(
        completed_on="2026-10-06",
        scope={"data_category_codes": ["id"]},
        risks=[
            {
                "risk_id": "R1",
                "evidence": [{"evidence_type": "informe", "obtained_on": "1900-01-01"}],
            }
        ],
        measures=[{"measure_id": "M1", "risk_ids": ["R1"]}],
        official_sources={
            "status": "identificado",
            "checked_on": "2026-10-06",
            "sources": [{"source_reference": "fuente"}],
        },
        agency_consultation={"status": "concluida", "response_reference": "respuesta"},
    )
    assert editable.completed_on == date(2026, 10, 6)
    stored = EipdResolutionAssessmentStoredV1(
        **editable.model_dump(), context_binding={"context_hash": "a" * 64}
    )
    serialized = stored.model_dump(mode="json")
    assert serialized["risks"][0]["evidence"][0]["obtained_on"] == "1900-01-01"
    assert EipdResolutionAssessmentStoredV1.model_validate(serialized) == stored
    with pytest.raises(ValidationError):
        EipdResolutionAssessmentV1.model_validate(serialized)


@pytest.mark.parametrize(
    "payload",
    [
        {"binding_version": 2, "context_hash": "a" * 64},
        {"context_hash": "A" * 64},
        {"context_hash": "g" * 64},
        {"context_hash": "a" * 63},
        {"context_hash": "a" * 65},
        {"context_hash": "a" * 64, "approved": True},
        {},
    ],
)
def test_binding_version_and_hash(payload):
    with pytest.raises(ValidationError):
        EipdResolutionContextBindingV1.model_validate(payload)


def event_payload():
    return dict(
        id=str(UUID(int=1)),
        organization_id=str(UUID(int=2)),
        assessment_id=str(UUID(int=3)),
        created_by=str(UUID(int=4)),
        decision="continuar",
        rationale="Revision documentada",
        review_reference="REV1",
        document_hash="a" * 64,
        context_hash="b" * 64,
        created_at="2026-10-06T12:00:00Z",
    )


@pytest.mark.parametrize("decision", ["continuar", "requiere_cambios", "no_continuar"])
def test_review_decisions_and_server_event_roundtrip(decision):
    payload = event_payload()
    payload["decision"] = decision
    event = EipdResolutionReviewOut.model_validate(payload)
    assert (
        EipdResolutionReviewOut.model_validate(event.model_dump(mode="json")) == event
    )
    state = EipdResolutionReviewStateOut(review_status="vigente", latest_review=event)
    assert state.latest_review.decision == decision
    with pytest.raises(ValidationError):
        EipdResolutionReviewIn.model_validate(payload)


@pytest.mark.parametrize("field", ["decision", "rationale", "review_reference"])
def test_review_requires_explicit_human_input(field):
    payload = dict(decision="continuar", rationale="fundamento", review_reference="REV")
    del payload[field]
    with pytest.raises(ValidationError):
        EipdResolutionReviewIn.model_validate(payload)


@pytest.mark.parametrize("field", ["rationale", "review_reference"])
@pytest.mark.parametrize("value", ["", " ", "\n\t", None])
def test_review_rejects_empty_foundation(field, value):
    payload = dict(decision="continuar", rationale="fundamento", review_reference="REV")
    payload[field] = value
    with pytest.raises(ValidationError):
        EipdResolutionReviewIn.model_validate(payload)


@pytest.mark.parametrize(
    "field,value",
    [
        ("decision", "approved"),
        ("created_at", "2026-10-06T12:00:00"),
        ("created_at", "2026-10-06T12:00:00-03:00"),
        ("document_hash", "x" * 64),
        ("context_hash", "short"),
        ("created_by", "bad-uuid"),
        ("approved", True),
    ],
)
def test_event_rejects_malformed_metadata(field, value):
    payload = event_payload()
    payload[field] = value
    with pytest.raises(ValidationError):
        EipdResolutionReviewOut.model_validate(payload)


@pytest.mark.parametrize(
    "field",
    [
        "id",
        "organization_id",
        "assessment_id",
        "created_by",
        "created_at",
        "document_hash",
        "context_hash",
        "review_status",
    ],
)
def test_review_input_cannot_spoof_server_fields(field):
    payload = dict(decision="continuar", rationale="fundamento", review_reference="REV")
    payload[field] = None
    with pytest.raises(ValidationError):
        EipdResolutionReviewIn.model_validate(payload)
