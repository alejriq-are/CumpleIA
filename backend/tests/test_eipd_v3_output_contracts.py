"""Contratos sucesores de salida, sin ampliar entradas ni activar endpoints."""

import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    EipdResolutionDocumentVersionedOut,
    EipdResolutionDocumentVersionedOutV2,
    LegalAssessmentRepresentationDraftCreateV1,
    LegalAssessmentRepresentationDraftUpdateV1,
    LegalAssessmentRepresentationOutV1,
    LegalAssessmentRepresentationOutV2,
)
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
)
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


@pytest.mark.parametrize("version", [1, 2, 3])
def test_successor_field_accepts_identity_without_conversion(represented, version):
    document, ctx = represented
    if version == 3:
        bound = bind_eipd_resolution_v3(document, ctx)
    else:
        model = EipdResolutionContextV1 if version == 1 else EipdResolutionContextV2
        legacy = {key: value for key, value in ctx.items() if key in model.model_fields}
        if version == 2:
            legacy["context_schema_version"] = 2
        bound = (bind_eipd_resolution_v1 if version == 1 else bind_eipd_resolution_v2)(
            document, legacy
        )
    # Validar el campo exacto de salida sin fabricar un expediente completo.
    from pydantic import TypeAdapter

    field = LegalAssessmentRepresentationOutV2.model_fields[
        "eipd_resolution_assessment"
    ]
    parsed = TypeAdapter(field.annotation).validate_python(
        bound.model_dump(mode="json")
    )
    assert parsed.model_dump(mode="json") == bound.model_dump(mode="json")
    if version == 3:
        old_field = LegalAssessmentRepresentationOutV1.model_fields[
            "eipd_resolution_assessment"
        ]
        with pytest.raises(ValidationError):
            TypeAdapter(old_field.annotation).validate_python(
                bound.model_dump(mode="json")
            )


@pytest.mark.parametrize(
    "model",
    [
        LegalAssessmentRepresentationDraftCreateV1,
        LegalAssessmentRepresentationDraftUpdateV1,
    ],
)
def test_new_binding_remains_server_only(represented, model):
    document, ctx = represented
    base = (
        {
            "purpose_id": "a0000000-0000-0000-0000-000000000001",
            "scope": {
                "data_category_codes": ["PRUEBA"],
                "data_subject_codes": ["PRUEBA"],
            },
        }
        if model is LegalAssessmentRepresentationDraftCreateV1
        else {}
    )
    with pytest.raises(ValidationError):
        model.model_validate(
            {
                **base,
                "eipd_resolution_assessment": bind_eipd_resolution_v3(
                    document, ctx
                ).model_dump(mode="json"),
            }
        )


@pytest.mark.parametrize("version", [None, 1, 2, 3])
def test_readiness_version_never_authorizes(version):
    data = dict(
        result="requiere_revision",
        context_current=False,
        issues=[],
        applicability=[],
        binding_version=version,
        can_confirm=False,
    )
    parsed = EipdResolutionDocumentVersionedOutV2.model_validate(data)
    assert parsed.binding_version == version and parsed.can_confirm is False
    if version == 3:
        with pytest.raises(ValidationError):
            EipdResolutionDocumentVersionedOut.model_validate(data)
    with pytest.raises(ValidationError):
        EipdResolutionDocumentVersionedOutV2.model_validate(
            dict(data, can_confirm=True)
        )


@pytest.mark.parametrize("version", [True, "3", 3.0, 0, 4])
def test_readiness_rejects_loose_or_unknown_binding(version):
    with pytest.raises(ValidationError):
        EipdResolutionDocumentVersionedOutV2.model_validate(
            dict(
                result="requiere_revision",
                context_current=False,
                issues=[],
                applicability=[],
                binding_version=version,
                can_confirm=False,
            )
        )
