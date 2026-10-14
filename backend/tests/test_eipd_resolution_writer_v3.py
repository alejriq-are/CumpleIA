"""Seleccion ficticia de binding sucesor, sin exposicion nueva en API."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.services.eipd_resolution_binding_v2 import EipdResolutionContextV2
from app.services.eipd_resolution_binding_v3 import (
    EipdResolutionContextV3,
    bind_eipd_resolution_v3,
)
from app.services.eipd_resolution_writer import bind_eipd_resolution_for_context as bind
from tests import test_eipd_resolution_binding_v3 as cases

complete_resolution = cases.complete_resolution
context = cases.context
materials = cases.materials
represented = cases.represented


def test_material_selects_v3_and_keeps_input_unchanged(represented):
    document, ctx = represented
    before = deepcopy(represented)
    assert bind(document, ctx) == bind_eipd_resolution_v3(document, ctx)
    assert bind(document, EipdResolutionContextV3.model_validate(ctx)) == bind(
        document, ctx
    )
    assert represented == before


def test_explicit_reaporte_after_withdrawal_keeps_v3(represented):
    document, ctx = represented
    previous = bind(document, ctx)
    before = previous.model_dump(mode="json")
    ctx.update(
        sensitive_representation_assessment=None,
        research_assessment=None,
        special_conditions=None,
    )
    current = bind(document, ctx, previous=previous)
    assert current.context_binding.binding_version == 3
    assert current.context_binding.context_hash != previous.context_binding.context_hash
    assert previous.model_dump(mode="json") == before
    assert bind(document, ctx, previous=before) == current


def test_old_context_cannot_downgrade_v3(represented):
    document, ctx = represented
    previous = bind(document, ctx)
    legacy = {
        key: value
        for key, value in ctx.items()
        if key in EipdResolutionContextV2.model_fields
    }
    legacy["context_schema_version"] = 2
    with pytest.raises(ValueError, match="V3"):
        bind(document, legacy, previous=previous)


@pytest.mark.parametrize("declared_research", [True, False])
def test_no_representation_keeps_previous_selection(represented, declared_research):
    document, ctx = represented
    ctx["sensitive_representation_assessment"] = None
    if not declared_research:
        ctx.update(research_assessment=None, special_conditions=None)
    result = bind(document, ctx)
    assert result.context_binding.binding_version == (2 if declared_research else 1)


@pytest.mark.parametrize(
    "field,value", [("context_schema_version", 2), ("can_confirm", True)]
)
def test_context_injection_cannot_be_projected_away(represented, field, value):
    document, ctx = represented
    ctx[field] = value
    with pytest.raises(ValidationError):
        bind(document, ctx)


def test_client_binding_and_malformed_previous_rejected(represented):
    document, ctx = represented
    stored = bind(document, ctx).model_dump(mode="json")
    with pytest.raises(ValidationError):
        bind(stored, ctx)
    stored["context_binding"]["context_hash"] = "invalid"
    with pytest.raises(ValidationError):
        bind(document, ctx, previous=stored)
