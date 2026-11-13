import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    EconomicObligationsAssessmentV1,
    LegalAssessmentDraftUpdate,
)


@pytest.mark.parametrize("route", ["sin_comunicacion", "con_comunicacion"])
@pytest.mark.parametrize("kind", ["economica", "financiera", "bancaria", "comercial"])
def test_partial_economic_routes(route, kind):
    parsed = EconomicObligationsAssessmentV1.model_validate(
        {"route": route, "obligation_type": kind}
    )
    assert parsed.evidence == [] and parsed.related_to_obligation is None
    assert parsed.model_dump(mode="json")["route"] == route


@pytest.mark.parametrize(
    "data",
    [
        {"route": "otra"},
        {"obligation_type": "otra"},
        {"schema_version": 2},
        {"approved": True},
        {"related_to_obligation": {"answer": "no_aplica"}},
        {"evidence": [{"evidence_type": "registro", "obtained_on": "invalid"}]},
    ],
)
def test_economic_closed_contract(data):
    with pytest.raises(ValidationError):
        EconomicObligationsAssessmentV1.model_validate(data)


def test_economic_update_omission_null():
    assert (
        LegalAssessmentDraftUpdate.model_validate({}).model_dump(exclude_unset=True)
        == {}
    )
    assert LegalAssessmentDraftUpdate.model_validate(
        {"economic_obligations_assessment": None}
    ).model_dump(exclude_unset=True) == {"economic_obligations_assessment": None}
