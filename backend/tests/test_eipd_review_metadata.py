from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.eipd_review_metadata import EipdReviewContextMetadataV1
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
)
from app.services.eipd_resolution_binding_v2 import bind_eipd_resolution_v2
from app.services.eipd_review_metadata import (
    build_eipd_review_context_metadata_v1,
    eipd_review_metadata_is_current_v1,
)
from tests import test_eipd_frontier_v2 as cases
from tests import test_services_eipd_resolution as resolutions
from tests.test_eipd_resolution_readiness import review_payload

context = cases.context
frontier_context = cases.frontier_context
complete_resolution = resolutions.complete_resolution


@pytest.mark.parametrize("version", [1, 2])
def test_server_metadata_is_deterministic_and_not_authority(
    frontier_context, complete_resolution, version
):
    ctx = (
        frontier_context
        if version == 2
        else {
            k: v
            for k, v in frontier_context.items()
            if k in EipdResolutionContextV1.model_fields
        }
    )
    bound = (bind_eipd_resolution_v2 if version == 2 else bind_eipd_resolution_v1)(
        complete_resolution[0], ctx
    )
    before = deepcopy((ctx, bound.model_dump(mode="json")))
    metadata = build_eipd_review_context_metadata_v1(bound, ctx)
    assert (
        metadata.resolution_binding_version
        == metadata.context_schema_version
        == version
    )
    assert metadata.research_coverage == (
        "contexto_v2" if version == 2 else "no_cubierta"
    )
    assert (metadata.research_material_hash is not None) == (version == 2)
    assert metadata == build_eipd_review_context_metadata_v1(bound, ctx)
    # Human event is a synthetic test fixture, never persisted by this helper.
    review = review_payload(
        bind_eipd_resolution_v1(
            complete_resolution[0],
            {k: v for k, v in ctx.items() if k in EipdResolutionContextV1.model_fields},
        )
    )
    review.update(
        document_hash=metadata.document_hash, context_hash=metadata.context_hash
    )
    assert eipd_review_metadata_is_current_v1(metadata, bound, ctx, review)
    assert not eipd_review_metadata_is_current_v1(None, bound, ctx, review)
    assert not hasattr(metadata, "can_confirm")
    assert (ctx, bound.model_dump(mode="json")) == before
    review["document_hash"] = "a" * 64
    assert not eipd_review_metadata_is_current_v1(metadata, bound, ctx, review)


def test_no_projection_or_identity_for_obsolete_context(
    frontier_context, complete_resolution
):
    document = complete_resolution[0]
    legacy = {
        k: v
        for k, v in frontier_context.items()
        if k in EipdResolutionContextV1.model_fields
    }
    with pytest.raises(ValueError):
        build_eipd_review_context_metadata_v1(
            bind_eipd_resolution_v1(document, legacy), frontier_context
        )
    bound = bind_eipd_resolution_v2(document, frontier_context)
    frontier_context["research_assessment"]["assessment"][
        "public_interest_analysis"
    ] += " cambiado"
    with pytest.raises(ValueError):
        build_eipd_review_context_metadata_v1(bound, frontier_context)
    for doc, ctx in [(None, frontier_context), (bound, None)]:
        with pytest.raises(ValueError):
            build_eipd_review_context_metadata_v1(doc, ctx)


def test_v2_null_research_has_context_coverage(frontier_context, complete_resolution):
    frontier_context["research_assessment"] = None
    metadata = build_eipd_review_context_metadata_v1(
        bind_eipd_resolution_v2(complete_resolution[0], frontier_context),
        frontier_context,
    )
    assert (
        metadata.research_coverage == "contexto_v2"
        and metadata.research_material_hash is None
    )


@pytest.mark.parametrize(
    "change",
    ["version", "coverage", "pair", "extra", "partial", "hash", "bool", "string"],
)
def test_closed_metadata_contract(frontier_context, complete_resolution, change):
    value = build_eipd_review_context_metadata_v1(
        bind_eipd_resolution_v2(complete_resolution[0], frontier_context),
        frontier_context,
    ).model_dump(mode="json")
    if change == "version":
        value["metadata_schema_version"] = 99
    elif change == "bool":
        value["metadata_schema_version"] = True
    elif change == "string":
        value["context_schema_version"] = "2"
    elif change == "coverage":
        value["research_coverage"] = "no_cubierta"
    elif change == "pair":
        value["context_schema_version"] = 1
    elif change == "extra":
        value["approved"] = True
    elif change == "partial":
        value.pop("research_material_hash")
    else:
        value["context_hash"] = "fake"
    with pytest.raises(ValidationError):
        EipdReviewContextMetadataV1.model_validate(value)
