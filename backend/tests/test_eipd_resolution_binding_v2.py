from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.licitud import EipdResolutionAssessmentStoredV1
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
    build_eipd_resolution_context_hash_v1,
    build_eipd_resolution_document_hash_v1,
)
from app.services.eipd_resolution_binding_v2 import (
    EipdResolutionContextV2,
    bind_eipd_resolution_v2,
    build_eipd_resolution_context_hash_v2,
    build_eipd_resolution_document_hash_v2,
    eipd_resolution_context_is_current_v2,
)
from app.services.research_binding import bind_research_assessment_v1
from tests import test_services_eipd_resolution as resolutions
from tests import test_services_research as research

complete_resolution = resolutions.complete_resolution
context = research.context


@pytest.fixture
def materials(complete_resolution, context):
    document, ctx = deepcopy(complete_resolution)
    research_document, _, lia = context
    ctx.update(
        research_assessment=bind_research_assessment_v1(
            research_document, ctx["rat_context_snapshot"], ctx["legal_basis"], lia
        ).model_dump(mode="json")
    )
    return document, ctx


def test_v2_deterministic_and_nonmutating(materials):
    document, ctx = materials
    before = deepcopy(materials)
    bound = bind_eipd_resolution_v2(document, ctx)
    assert bound.context_binding.binding_version == 2
    assert eipd_resolution_context_is_current_v2(bound, ctx)
    assert build_eipd_resolution_context_hash_v2(
        ctx
    ) == build_eipd_resolution_context_hash_v2(
        EipdResolutionContextV2.model_validate(ctx)
    )
    assert build_eipd_resolution_document_hash_v2(
        bound
    ) == build_eipd_resolution_document_hash_v2(bound.model_dump(mode="json"))
    assert materials == before


@pytest.mark.parametrize(
    "change", ["body", "binding", "withdraw", "basis", "rat", "lia"]
)
def test_changes_invalidate_association_without_repair(materials, change):
    document, ctx = materials
    bound = bind_eipd_resolution_v2(document, ctx)
    previous = bound.model_dump(mode="json")
    if change == "body":
        ctx["research_assessment"]["assessment"][
            "public_interest_analysis"
        ] += " revisado"
    elif change == "binding":
        ctx["research_assessment"]["context_binding"]["document_hash"] = "a" * 64
    elif change == "withdraw":
        ctx["research_assessment"] = None
    elif change == "basis":
        ctx["legal_basis"] = "interes_legitimo_art13d"
    elif change == "rat":
        ctx["rat_context_snapshot"]["purpose"] += " revisada"
    else:
        ctx["lia_assessment"] = {}
    assert not eipd_resolution_context_is_current_v2(bound, ctx)
    assert bound.model_dump(mode="json") == previous


def test_closed_versions_and_required_null(materials):
    document, ctx = materials
    missing = dict(ctx)
    missing.pop("research_assessment")
    with pytest.raises(ValidationError):
        EipdResolutionContextV2.model_validate(missing)
    null = dict(ctx, research_assessment=None)
    EipdResolutionContextV2.model_validate(null)
    for bad in (dict(ctx, context_schema_version=99), dict(ctx, approved=True)):
        with pytest.raises(ValidationError):
            EipdResolutionContextV2.model_validate(bad)
    with pytest.raises(ValidationError):
        EipdResolutionContextV1.model_validate(ctx)
    bound = bind_eipd_resolution_v2(document, ctx)
    with pytest.raises(ValidationError):
        EipdResolutionAssessmentStoredV1.model_validate(bound.model_dump(mode="json"))
    with pytest.raises(ValidationError):
        bind_eipd_resolution_v2(bound, ctx)


def test_historical_hashes_and_null_distinction(complete_resolution):
    document, ctx = complete_resolution
    assert (
        build_eipd_resolution_context_hash_v1(ctx)
        == "a7b447bf23553d5b5d4a938a1325ecac2c4a39a2ee86be889e86ce8c9f7976e3"
    )
    v1 = bind_eipd_resolution_v1(document, ctx)
    assert (
        build_eipd_resolution_document_hash_v1(v1)
        == "982c5841b486043d21aa3d8728272b80b74fc08f92a1aaa7a5c78c16e63d8478"
    )
    new_context = dict(ctx, research_assessment=None)
    assert build_eipd_resolution_context_hash_v2(
        new_context
    ) != build_eipd_resolution_context_hash_v1(ctx)
    assert build_eipd_resolution_document_hash_v2(
        bind_eipd_resolution_v2(document, new_context)
    ) != build_eipd_resolution_document_hash_v1(v1)
