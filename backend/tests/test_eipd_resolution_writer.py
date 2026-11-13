from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
)
from app.services.eipd_resolution_writer import bind_eipd_resolution_for_context
from tests import test_eipd_frontier_v2 as cases
from tests import test_services_eipd_resolution as resolutions

context = cases.context
frontier_context = cases.frontier_context
complete_resolution = resolutions.complete_resolution


def test_research_binding_uses_final_context_without_mutation(
    frontier_context, complete_resolution
):
    document = complete_resolution[0]
    before = deepcopy((document, frontier_context))
    result = bind_eipd_resolution_for_context(document, frontier_context)
    assert result.context_binding.binding_version == 2
    assert result == bind_eipd_resolution_for_context(document, frontier_context)
    assert (document, frontier_context) == before


def test_declared_research_without_document_still_covered(
    frontier_context, complete_resolution
):
    frontier_context["research_assessment"] = None
    assert (
        bind_eipd_resolution_for_context(
            complete_resolution[0], frontier_context
        ).context_binding.binding_version
        == 2
    )


def test_withdrawal_cannot_downgrade_previous_v2(frontier_context, complete_resolution):
    document = complete_resolution[0]
    previous = bind_eipd_resolution_for_context(document, frontier_context)
    before = previous.model_dump(mode="json")
    frontier_context.update(research_assessment=None, special_conditions=None)
    new = bind_eipd_resolution_for_context(
        document, frontier_context, previous=previous
    )
    assert new.context_binding.binding_version == 2
    assert new.context_binding.context_hash != previous.context_binding.context_hash
    assert previous.model_dump(mode="json") == before


def test_ordinary_v1_binding_is_unchanged(frontier_context, complete_resolution):
    frontier_context.update(research_assessment=None, special_conditions=None)
    document = complete_resolution[0]
    legacy = {
        k: v
        for k, v in frontier_context.items()
        if k in EipdResolutionContextV1.model_fields
    }
    assert bind_eipd_resolution_for_context(
        document, frontier_context
    ) == bind_eipd_resolution_v1(document, legacy)


def test_unknown_previous_or_client_binding_rejected(
    frontier_context, complete_resolution
):
    document = complete_resolution[0]
    bound = bind_eipd_resolution_for_context(document, frontier_context).model_dump(
        mode="json"
    )
    with pytest.raises(ValidationError):
        bind_eipd_resolution_for_context(bound, frontier_context)
    bound["context_binding"]["binding_version"] = 99
    with pytest.raises(ValueError):
        bind_eipd_resolution_for_context(document, frontier_context, previous=bound)
