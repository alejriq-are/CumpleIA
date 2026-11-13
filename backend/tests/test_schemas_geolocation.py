import pytest
from pydantic import ValidationError

from app.schemas.licitud import GeolocationAssessmentV1, LegalAssessmentDraftUpdate


@pytest.mark.parametrize("answer", ["si", "no", "pendiente"])
def test_geolocation_partial_factual(answer):
    data = GeolocationAssessmentV1.model_validate(
        {
            "value_added_third_party_transfer": {"answer": answer},
            "notice_provided_on": "2026-10-06",
        }
    )
    assert data.scope is None and data.evidence == []
    assert data.model_dump(mode="json")["notice_provided_on"] == "2026-10-06"


@pytest.mark.parametrize(
    "data",
    [
        {"approved": True},
        {"schema_version": 2},
        {"information_clear": {"answer": "no_aplica"}},
        {"notice_provided_on": "invalid"},
        {"scope": {"unknown": True}},
        {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
    ],
)
def test_geolocation_closed_schema(data):
    with pytest.raises(ValidationError):
        GeolocationAssessmentV1.model_validate(data)


def test_geolocation_omission_null():
    assert (
        LegalAssessmentDraftUpdate.model_validate({}).model_dump(exclude_unset=True)
        == {}
    )
    assert LegalAssessmentDraftUpdate.model_validate(
        {"geolocation_assessment": None}
    ).model_dump(exclude_unset=True) == {"geolocation_assessment": None}
