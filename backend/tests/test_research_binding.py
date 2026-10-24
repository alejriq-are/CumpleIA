from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.research import BoundResearchAssessmentV1
from app.services.research_binding import (
    bind_research_assessment_v1 as bind,
)
from app.services.research_binding import (
    evaluate_research_association_v1 as evaluate,
)
from tests import test_services_research as research

context = research.context


def test_binding_is_deterministic_does_not_mutate_and_never_authorizes(context):
    document, rat, lia = context
    before = deepcopy(context)
    bound = bind(document, rat, "interes_legitimo_art13d", lia)
    assert bind(document, rat, "interes_legitimo_art13d", lia) == bound
    assert context == before
    result = evaluate(bound, rat, "interes_legitimo_art13d", lia)
    assert result.result == "vigente" and not result.can_confirm
    assert bound.context_binding.context_hash != bound.context_binding.document_hash
    assert (
        evaluate(bound.model_dump(mode="json"), rat, "interes_legitimo_art13d", lia)
        == result
    )


@pytest.mark.parametrize(
    "change", ["purpose", "rat_scope", "sensitive", "subjects", "lia", "basis"]
)
def test_context_change_invalidates_association(context, change):
    document, rat, lia = context
    bound = bind(document, rat, "interes_legitimo_art13d", lia)
    basis = "interes_legitimo_art13d"
    if change == "purpose":
        rat["purpose"] = "Otra finalidad"
    if change == "rat_scope":
        rat["data_categories"][0]["notes"] = "Cambio documental"
    if change == "sensitive":
        rat["data_categories"][0]["is_sensitive"] = True
    if change == "subjects":
        rat["data_subjects"][0]["includes_children"] = True
    if change == "lia":
        lia["conclusion"]["balancing_summary"] = "Nueva ponderacion"
    if change == "basis":
        basis = "consentimiento_art12"
    result = evaluate(bound, rat, basis, lia)
    assert (
        result.result == "requiere_revision"
        and "asociacion_contexto_obsoleta" in result.issues
    )


def test_document_change_requires_explicit_rebinding(context):
    document, rat, lia = context
    bound = bind(document, rat, "interes_legitimo_art13d", lia)
    bound.assessment.retention_analysis = "Nuevo criterio"
    assert evaluate(bound, rat, "interes_legitimo_art13d", lia).issues == (
        "asociacion_documento_obsoleta",
    )
    fresh = bind(bound.assessment, rat, "interes_legitimo_art13d", lia)
    assert evaluate(fresh, rat, "interes_legitimo_art13d", lia).result == "vigente"
    assert fresh.context_binding.document_hash != bound.context_binding.document_hash


def test_missing_or_historical_binding_is_not_upgraded(context):
    _, rat, lia = context
    assert evaluate(None, rat, "interes_legitimo_art13d", lia).issues == (
        "asociacion_ausente",
    )
    with pytest.raises(ValidationError):
        BoundResearchAssessmentV1.model_validate(
            {"schema_version": 10, "hash": "a" * 64}
        )


def test_invalid_binding_and_mutated_assessment_are_revalidated(context):
    document, rat, lia = context
    bound = bind(document, rat, "interes_legitimo_art13d", lia)
    raw = bound.model_dump()
    raw["context_binding"]["schema_version"] = 2
    with pytest.raises(ValidationError):
        evaluate(raw, rat, "interes_legitimo_art13d", lia)
    bound.assessment.purpose_type = "invalid"
    with pytest.raises(ValidationError):
        evaluate(bound, rat, "interes_legitimo_art13d", lia)


def test_binding_incomplete_document_is_not_readiness_or_authority(context):
    _, rat, lia = context
    bound = bind({}, rat, "interes_legitimo_art13d", lia)
    result = evaluate(bound, rat, "interes_legitimo_art13d", lia)
    assert result.result == "vigente" and not result.can_confirm
