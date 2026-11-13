from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.services.eipd_screening_v2 import evaluate_eipd_screening_v2
from app.services.eipd_screening_v3 import evaluate_eipd_screening_v3
from tests import test_eipd_frontier_v2 as cases

context = cases.context
frontier_context = cases.frontier_context


def assert_preserved(result):
    raw = result.frontier.screening
    assert (
        result.result,
        result.context_current,
        result.issues,
        result.observations,
    ) == (raw.result, raw.context_current, raw.issues, raw.observations)
    assert not result.can_continue and not result.can_confirm
    assert result.evaluation_version == 3


def test_complete_context_preserves_detection_and_blocks(frontier_context):
    before = deepcopy(frontier_context)
    result = evaluate_eipd_screening_v3(frontier_context)
    assert_preserved(result)
    assert result.frontier.research.result == "completo"
    assert frontier_context["eipd_screening"]["context_binding"]["schema_version"] == 12
    assert result == evaluate_eipd_screening_v3(frontier_context)
    assert frontier_context == before


@pytest.mark.parametrize(
    "change", ["document", "binding", "withdraw", "sensitive", "minor"]
)
def test_changed_context_keeps_diagnostics(frontier_context, change):
    ctx = frontier_context
    if change == "document":
        ctx["research_assessment"]["assessment"][
            "public_interest_analysis"
        ] += " cambiado"
    elif change == "binding":
        ctx["research_assessment"]["context_binding"]["context_hash"] = "a" * 64
    elif change == "withdraw":
        ctx["research_assessment"] = None
    elif change == "sensitive":
        ctx["rat_context_snapshot"]["data_categories"][0]["is_sensitive"] = True
    else:
        ctx["rat_context_snapshot"]["data_subjects"][0]["includes_children"] = True
    before = deepcopy(ctx)
    result = evaluate_eipd_screening_v3(ctx)
    assert_preserved(result)
    assert result.frontier.issues
    assert not result.context_current
    assert ctx == before


def test_missing_context_is_pending():
    result = evaluate_eipd_screening_v3(None)
    assert result.result == "pendiente_revision"
    assert result.issues and not result.context_current
    assert not result.can_continue and not result.can_confirm


@pytest.mark.parametrize("change", ["version", "extra", "missing"])
def test_closed_contract(frontier_context, change):
    if change == "version":
        frontier_context["context_schema_version"] = 99
    elif change == "extra":
        frontier_context["approved"] = True
    else:
        frontier_context.pop("research_assessment")
    with pytest.raises(ValidationError):
        evaluate_eipd_screening_v3(frontier_context)


def test_historical_screening_does_not_accept_research_context(frontier_context):
    with pytest.raises(ValidationError):
        evaluate_eipd_screening_v2(frontier_context)
