"""Diagnostico V3 ficticio con cobertura historica conservadora."""

from copy import deepcopy
from datetime import date

import pytest
from pydantic import ValidationError

from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
)
from app.services.eipd_resolution_binding_v2 import (
    EipdResolutionContextV2,
    bind_eipd_resolution_v2,
    build_eipd_resolution_document_hash_v2,
)
from app.services.eipd_resolution_binding_v3 import (
    bind_eipd_resolution_v3,
    build_eipd_resolution_document_hash_v3,
)
from app.services.eipd_resolution_readiness_v2 import (
    derive_eipd_resolution_review_state_versioned as state,
)
from app.services.eipd_resolution_readiness_v2 import (
    evaluate_eipd_resolution_document_versioned as evaluate,
)
from tests import test_eipd_resolution_binding_v3 as cases
from tests.test_eipd_resolution_readiness import review_payload

complete_resolution = cases.complete_resolution
context = cases.context
materials = cases.materials
represented = cases.represented
DAY = date(2026, 10, 14)


def test_v3_identity_is_current_but_evaluation_never_authorizes(represented):
    document, ctx = represented
    bound = bind_eipd_resolution_v3(document, ctx)
    before = deepcopy((ctx, bound.model_dump(mode="json")))
    result = evaluate(bound, ctx, evaluated_on=DAY)
    assert result.binding_version == 3 and result.context_current
    assert result.result == "requiere_revision" and not result.can_confirm
    assert any(
        i.code == "representacion_evaluacion_integracion_pendiente"
        for i in result.issues
    )
    assert before == (ctx, bound.model_dump(mode="json"))


@pytest.mark.parametrize("version", [1, 2])
def test_old_binding_does_not_cover_representation(represented, version):
    document, ctx = represented
    model = EipdResolutionContextV1 if version == 1 else EipdResolutionContextV2
    old_ctx = {key: value for key, value in ctx.items() if key in model.model_fields}
    if version == 2:
        old_ctx["context_schema_version"] = 2
    bound = (bind_eipd_resolution_v1 if version == 1 else bind_eipd_resolution_v2)(
        document, old_ctx
    )
    result = evaluate(bound, ctx, evaluated_on=DAY)
    assert not result.context_current and not result.can_confirm
    assert any(i.code == "asociacion_representacion_no_cubierta" for i in result.issues)
    review = review_payload(
        bind_eipd_resolution_v1(
            document,
            {
                key: value
                for key, value in ctx.items()
                if key in EipdResolutionContextV1.model_fields
            },
        )
    )
    if version == 2:
        review.update(
            document_hash=build_eipd_resolution_document_hash_v2(bound),
            context_hash=bound.context_binding.context_hash,
        )
    assert state(bound, old_ctx, review).review_status == "vigente"
    assert state(bound, ctx, review).review_status == "obsoleta"


def test_changed_representation_invalidates_v3(represented):
    document, ctx = represented
    bound = bind_eipd_resolution_v3(document, ctx)
    ctx["sensitive_representation_assessment"]["assessment"]["notes"] += " cambiado"
    assert not evaluate(bound, ctx, evaluated_on=DAY).context_current


def test_review_v3_tracks_document_and_context_without_repair(represented):
    document, ctx = represented
    bound = bind_eipd_resolution_v3(document, ctx)
    legacy = {
        key: value
        for key, value in ctx.items()
        if key in EipdResolutionContextV1.model_fields
    }
    review = review_payload(bind_eipd_resolution_v1(document, legacy))
    review.update(
        document_hash=build_eipd_resolution_document_hash_v3(bound),
        context_hash=bound.context_binding.context_hash,
    )
    assert state(bound, ctx, review).review_status == "vigente"
    ctx["sensitive_representation_assessment"] = None
    assert state(bound, ctx, review).review_status == "obsoleta"


def test_v3_binding_requires_v3_context(represented):
    document, ctx = represented
    bound = bind_eipd_resolution_v3(document, ctx)
    legacy = {
        key: value
        for key, value in ctx.items()
        if key in EipdResolutionContextV2.model_fields
    }
    legacy["context_schema_version"] = 2
    with pytest.raises(ValidationError):
        evaluate(bound, legacy, evaluated_on=DAY)
