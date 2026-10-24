"""Requisitos puros previos a revision: nunca autorizacion ni confirmacion."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app.schemas.licitud import EipdResolutionReviewIn
from app.services.eipd_resolution import (
    bind_eipd_resolution_v1,
    evaluate_eipd_resolution_review_prerequisites_v1,
)
from tests import test_services_eipd_resolution as fixtures

complete_resolution = fixtures.complete_resolution
TODAY = date(2026, 10, 6)
DECISIONS = ["continuar", "requiere_cambios", "no_continuar"]


def request(decision):
    return dict(
        decision=decision, rationale="Revision fundada", review_reference="REV1"
    )


def evaluate(document, context, decision, status="borrador"):
    return evaluate_eipd_resolution_review_prerequisites_v1(
        status, document, context, request(decision), evaluated_on=TODAY
    )


def codes(result):
    return {i.code for i in result.issues}


@pytest.mark.parametrize("decision", DECISIONS)
def test_prepared_document_does_not_accredit_frontier_or_sources(
    complete_resolution, decision
):
    doc, ctx = complete_resolution
    bound = bind_eipd_resolution_v1(doc, ctx)
    before = deepcopy((bound.model_dump(mode="json"), ctx))
    result = evaluate(bound, ctx, decision)
    assert result.decision == decision
    assert result.prerequisites_met == (decision != "continuar")
    assert codes(result) == (
        {"frontera_revision_no_validada", "fuentes_oficiales_no_verificadas"}
        if decision == "continuar"
        else set()
    )
    assert (bound.model_dump(mode="json"), ctx) == before
    assert not hasattr(result, "can_confirm")
    with pytest.raises(FrozenInstanceError):
        result.decision = "continuar"


@pytest.mark.parametrize("decision", DECISIONS)
def test_partial_bound_document_admits_only_negative_review(
    complete_resolution, decision
):
    _, ctx = complete_resolution
    bound = bind_eipd_resolution_v1({}, ctx)
    result = evaluate(bound, ctx, decision)
    assert result.prerequisites_met == (decision != "continuar")
    if decision == "continuar":
        assert "campo_obligatorio" in codes(result)
        assert "frontera_revision_no_validada" in codes(result)


@pytest.mark.parametrize("decision", DECISIONS)
@pytest.mark.parametrize("mode", ["absent", "unbound", "obsolete", "no_context"])
def test_unreviewable_document_rejects_every_decision(
    complete_resolution, decision, mode
):
    doc, ctx = complete_resolution
    bound = bind_eipd_resolution_v1(doc, ctx)
    expected = {
        "absent": "expediente_ausente",
        "unbound": "asociacion_ausente",
        "obsolete": "asociacion_obsoleta",
        "no_context": "contexto_rat_no_disponible",
    }[mode]
    if mode == "absent":
        bound = None
    elif mode == "unbound":
        bound.context_binding = None
    elif mode == "obsolete":
        ctx["consent_assessment"] = {}
    else:
        ctx = None
    result = evaluate(bound, ctx, decision)
    assert not result.prerequisites_met
    assert expected in codes(result)
    assert len(result.issues) == len(set(result.issues))


@pytest.mark.parametrize("decision", DECISIONS)
@pytest.mark.parametrize("status", ["confirmado", "reemplazado"])
def test_immutable_assessment_rejects_review(complete_resolution, decision, status):
    doc, ctx = complete_resolution
    result = evaluate(bind_eipd_resolution_v1(doc, ctx), ctx, decision, status)
    assert not result.prerequisites_met
    assert "evaluacion_no_borrador" in codes(result)


@pytest.mark.parametrize("decision", DECISIONS)
def test_residual_high_remains_blocked_but_can_document_rejection(
    complete_resolution, decision
):
    doc, ctx = complete_resolution
    doc["residual_risk_level"] = "alto"
    bound = bind_eipd_resolution_v1(doc, ctx)
    result = evaluate(bound, ctx, decision)
    assert result.prerequisites_met == (decision != "continuar")
    if decision == "continuar":
        assert any(i.field == "residual_risk_level" for i in result.issues)
        assert "fuentes_oficiales_no_verificadas" in codes(result)


@pytest.mark.parametrize(
    "field",
    [
        "created_by",
        "context_hash",
        "document_hash",
        "organization_id",
        "frontier_verified",
        "sources_verified",
    ],
)
def test_client_cannot_supply_server_metadata_or_override_barriers(
    complete_resolution, field
):
    doc, ctx = complete_resolution
    payload = request("continuar") | {field: "forged"}
    with pytest.raises(ValidationError):
        evaluate_eipd_resolution_review_prerequisites_v1(
            "borrador",
            bind_eipd_resolution_v1(doc, ctx),
            ctx,
            payload,
            evaluated_on=TODAY,
        )


def test_mutated_review_model_revalidated(complete_resolution):
    doc, ctx = complete_resolution
    payload = EipdResolutionReviewIn(**request("no_continuar"))
    payload.decision = "approved"
    with pytest.raises(ValidationError):
        evaluate_eipd_resolution_review_prerequisites_v1(
            "borrador",
            bind_eipd_resolution_v1(doc, ctx),
            ctx,
            payload,
            evaluated_on=TODAY,
        )


@pytest.mark.parametrize("invalid_date", [None, "2026-10-06", datetime(2026, 10, 6)])
def test_date_is_explicit_even_for_negative_review(complete_resolution, invalid_date):
    doc, ctx = complete_resolution
    with pytest.raises(ValueError):
        evaluate_eipd_resolution_review_prerequisites_v1(
            "borrador",
            bind_eipd_resolution_v1(doc, ctx),
            ctx,
            request("no_continuar"),
            evaluated_on=invalid_date,
        )


def test_unknown_status_is_not_accepted(complete_resolution):
    doc, ctx = complete_resolution
    with pytest.raises(ValueError):
        evaluate(bind_eipd_resolution_v1(doc, ctx), ctx, "no_continuar", status="draft")
