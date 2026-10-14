"""Dos asociaciones ficticias independientes; completitud nunca autoriza."""

from copy import deepcopy
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app.services.eipd_representation import EipdRepresentationInputV1
from app.services.eipd_representation import compose_eipd_representation_v1 as compose
from app.services.eipd_resolution_binding_v2 import (
    EipdResolutionContextV2,
    bind_eipd_resolution_v2,
)
from app.services.eipd_resolution_binding_v3 import bind_eipd_resolution_v3
from tests import test_eipd_resolution_binding_v3 as cases

complete_resolution = cases.complete_resolution
context = cases.context
materials = cases.materials
represented = cases.represented
DAY = date(2026, 10, 14)


@pytest.fixture
def value(represented):
    document, ctx = represented
    return dict(
        organization_id="a0000000-0000-0000-0000-000000000001",
        treatment_id="a0000000-0000-0000-0000-000000000002",
        assessment_id="a0000000-0000-0000-0000-000000000003",
        context=ctx,
        resolution=bind_eipd_resolution_v3(document, ctx).model_dump(mode="json"),
    )


def test_joint_evaluation_maps_actual_issues_without_authority(value):
    before = deepcopy(value)
    result = compose(value, evaluated_on=DAY)
    assert result == compose(
        EipdRepresentationInputV1.model_validate(value), evaluated_on=DAY
    )
    assert result.context_metadata is not None
    assert not result.authorizes_action and not result.can_confirm
    assert not result.representation.can_confirm and not result.resolution.can_confirm
    assert all(
        any(
            issue.code == item.code
            and issue.field == "sensitive_representation_assessment." + item.field
            for issue in result.resolution.issues
        )
        for item in result.representation.issues
    )
    assert not any(
        i.code == "representacion_evaluacion_integracion_pendiente"
        for i in result.resolution.issues
    )
    assert value == before


@pytest.mark.parametrize(
    "identity", ["organization_id", "treatment_id", "assessment_id"]
)
def test_representation_identity_is_evaluated_independently(value, identity):
    value[identity] = "a0000000-0000-0000-0000-000000000099"
    result = compose(value, evaluated_on=DAY)
    assert result.resolution.context_current
    assert any(
        i.code == "asociacion_contexto_obsoleta" for i in result.representation.issues
    )
    assert result.resolution.result == "requiere_revision" and not result.can_confirm


def test_changed_representation_invalidates_eipd_metadata(value):
    value["context"]["sensitive_representation_assessment"]["assessment"][
        "notes"
    ] += " modificado"
    result = compose(value, evaluated_on=DAY)
    assert not result.resolution.context_current
    assert result.context_metadata is None
    assert any(
        i.code == "asociacion_documento_obsoleta" for i in result.representation.issues
    )


def test_withdrawal_is_explicit_and_does_not_repair_binding(value):
    value["context"]["sensitive_representation_assessment"] = None
    result = compose(value, evaluated_on=DAY)
    assert not result.resolution.context_current and result.context_metadata is None


def test_old_binding_does_not_get_successor_metadata(value, represented):
    document, ctx = represented
    legacy = {k: v for k, v in ctx.items() if k in EipdResolutionContextV2.model_fields}
    legacy["context_schema_version"] = 2
    value["resolution"] = bind_eipd_resolution_v2(document, legacy).model_dump(
        mode="json"
    )
    result = compose(value, evaluated_on=DAY)
    assert result.context_metadata is None and not result.resolution.context_current
    assert any(
        i.code == "asociacion_representacion_no_cubierta"
        for i in result.resolution.issues
    )


@pytest.mark.parametrize("day", ["2026-10-14", datetime(2026, 10, 14)])
def test_date_is_explicit_and_strict(value, day):
    with pytest.raises(ValueError):
        compose(value, evaluated_on=day)


def test_extra_authority_field_is_not_ignored(value):
    value["can_confirm"] = True
    with pytest.raises(ValidationError):
        compose(value, evaluated_on=DAY)


def test_complete_representation_still_has_no_authority(value, represented):
    from app.services.sensitive_representation_binding import (
        bind_sensitive_representation_v1,
    )

    document, ctx = represented
    scope = {
        "data_category_codes": [
            i["category_code"] for i in ctx["rat_context_snapshot"]["data_categories"]
        ],
        "data_subject_codes": [
            i["category_code"] for i in ctx["rat_context_snapshot"]["data_subjects"]
        ],
    }
    ctx.update(
        legal_basis="consentimiento_art12",
        consent_assessment={"given_by": "mandatario"},
        sensitive_consent_assessment={"scope": scope},
    )
    material = {
        field: "PRUEBA: declaracion documental no verificada"
        for field in (
            "representative_reference",
            "represented_subjects_reference",
            "authority_document_reference",
            "authority_document_version",
            "authority_basis_description",
            "express_authority_analysis",
            "scope_match_analysis",
            "validity_analysis",
            "limitations",
            "revocation_information",
        )
    }
    material.update(
        representation_kind="mandatario",
        scope=scope,
        evidence=[{"evidence_type": "PRUEBA", "reference": "PRUEBA"}],
    )
    ctx["sensitive_representation_assessment"] = bind_sensitive_representation_v1(
        material,
        {
            **{
                k: value[k]
                for k in ("organization_id", "treatment_id", "assessment_id")
            },
            **{
                k: ctx[k]
                for k in (
                    "rat_context_snapshot",
                    "legal_basis",
                    "consent_assessment",
                    "sensitive_consent_assessment",
                )
            },
        },
    ).model_dump(mode="json")
    value.update(context=ctx, resolution=bind_eipd_resolution_v3(document, ctx))
    result = compose(value, evaluated_on=DAY)
    assert result.representation.result == "completo"
    assert result.representation.issues == ()
    assert result.context_metadata is not None
    assert not result.can_confirm and not result.authorizes_action
