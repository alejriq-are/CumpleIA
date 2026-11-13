from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.licitud import (
    EipdResolutionAssessmentStoredV1,
    EipdResolutionAssessmentV1,
)
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
    build_eipd_resolution_context_hash_v1,
    build_eipd_resolution_document_hash_v1,
    eipd_resolution_context_is_current_v1,
)

DOC_FIELDS = [
    f
    for f in EipdResolutionContextV1.model_fields
    if f not in ("rat_context_snapshot", "legal_basis")
]


@pytest.fixture
def resolution_context(complete_lia_context):
    material = {f: None for f in EipdResolutionContextV1.model_fields}
    material["rat_context_snapshot"] = deepcopy(complete_lia_context[1])
    material["legal_basis"] = "consentimiento_art12"
    return material


def partial_document(field):
    if field in ("special_conditions", "eipd_screening"):
        return {"context_binding": {"schema_version": 1, "hash": "a" * 64}}
    return {}


@pytest.mark.parametrize("field", DOC_FIELDS)
@pytest.mark.parametrize("mutation", ["add", "remove", "notes"])
def test_every_document_invalidates_resolution(resolution_context, field, mutation):
    context = deepcopy(resolution_context)
    if mutation != "add":
        context[field] = partial_document(field)
    bound = bind_eipd_resolution_v1({}, context)
    before = deepcopy((bound.model_dump(mode="json"), context))
    changed = deepcopy(context)
    if mutation == "add":
        changed[field] = partial_document(field)
    elif mutation == "remove":
        changed[field] = None
    else:
        if field == "lia_assessment":
            changed[field]["necessity"] = {"necessity_analysis": "Revision documentada"}
        else:
            changed[field]["notes"] = "Revision documentada"
    assert eipd_resolution_context_is_current_v1(bound, context)
    assert not eipd_resolution_context_is_current_v1(bound, changed)
    rebound = bind_eipd_resolution_v1({}, changed)
    assert rebound.context_binding.context_hash != bound.context_binding.context_hash
    assert build_eipd_resolution_document_hash_v1(
        rebound
    ) != build_eipd_resolution_document_hash_v1(bound)
    assert (bound.model_dump(mode="json"), context) == before


@pytest.mark.parametrize(
    "basis",
    [
        None,
        "contrato_precontractual_art13c",
        "obligacion_legal_art13b",
        "interes_legitimo_art13d",
        "defensa_derechos_art13e",
        "obligaciones_economicas_art13a",
    ],
)
def test_basis_directly_changes_context(resolution_context, basis):
    bound = bind_eipd_resolution_v1({}, resolution_context)
    changed = deepcopy(resolution_context)
    changed["legal_basis"] = basis
    assert not eipd_resolution_context_is_current_v1(bound, changed)


@pytest.mark.parametrize(
    "field", ["purpose", "organization_role", "systems", "retention"]
)
def test_full_snapshot_changes_even_noncanonical_rat_fields(resolution_context, field):
    bound = bind_eipd_resolution_v1({}, resolution_context)
    changed = deepcopy(resolution_context)
    values = {
        "purpose": "Otra finalidad",
        "organization_role": "encargado",
        "retention": {"retention_rule": "10 años", "deletion_method": "Borrado seguro"},
        "systems": [
            {
                "name": "Nuevo sistema",
                "provider": "Proveedor",
                "hosting_location": "Local",
                "hosting_country": "CL",
                "is_international": False,
            }
        ],
    }
    changed["rat_context_snapshot"][field] = values[field]
    assert not eipd_resolution_context_is_current_v1(bound, changed)


@pytest.mark.parametrize("field", list(EipdResolutionContextV1.model_fields))
def test_context_requires_explicit_all_inputs(resolution_context, field):
    del resolution_context[field]
    with pytest.raises(ValidationError):
        build_eipd_resolution_context_hash_v1(resolution_context)


def test_determinism_defaults_models_and_key_order(resolution_context):
    context = EipdResolutionContextV1.model_validate(resolution_context)
    first = build_eipd_resolution_context_hash_v1(context)
    assert first == build_eipd_resolution_context_hash_v1(
        context.model_dump(mode="json")
    )
    assert first == build_eipd_resolution_context_hash_v1(
        dict(reversed(list(resolution_context.items())))
    )
    bound = bind_eipd_resolution_v1({}, context)
    assert bound == bind_eipd_resolution_v1(EipdResolutionAssessmentV1(), context)
    assert build_eipd_resolution_document_hash_v1(
        bound
    ) == build_eipd_resolution_document_hash_v1(bound.model_dump(mode="json"))
    assert eipd_resolution_context_is_current_v1(
        bound.model_dump(mode="json"), resolution_context
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"notes": "Revisión ñ"},
        {"completed_on": "2026-10-06"},
        {"risks": [{"risk_id": "R1"}]},
        {"measures": [{"risk_ids": ["R1"]}]},
        {"agency_consultation": {"status": "en_curso"}},
        {"official_sources": {"status": "pendiente"}},
        {"performed_before_processing": {"answer": "no"}},
        {"scope": {"data_subject_codes": ["clientes"]}},
    ],
)
def test_document_content_changes_only_document_hash(resolution_context, payload):
    original = bind_eipd_resolution_v1({}, resolution_context)
    changed = bind_eipd_resolution_v1(payload, resolution_context)
    assert original.context_binding == changed.context_binding
    assert build_eipd_resolution_document_hash_v1(
        original
    ) != build_eipd_resolution_document_hash_v1(changed)
    assert eipd_resolution_context_is_current_v1(changed, resolution_context)


@pytest.mark.parametrize(
    "field", ["review_status", "latest_review", "decision", "created_by", "created_at"]
)
def test_review_metadata_is_not_hash_material(resolution_context, field):
    document = bind_eipd_resolution_v1({}, resolution_context).model_dump(mode="json")
    document[field] = None
    with pytest.raises(ValidationError):
        build_eipd_resolution_document_hash_v1(document)


@pytest.mark.parametrize("field", ["resolution", "review_events", "context_binding"])
def test_no_circular_context_inputs(resolution_context, field):
    resolution_context[field] = {}
    with pytest.raises(ValidationError):
        build_eipd_resolution_context_hash_v1(resolution_context)


def test_unbound_document_is_not_current_and_reading_does_not_bind(resolution_context):
    document = EipdResolutionAssessmentStoredV1()
    before = document.model_dump(mode="json")
    assert not eipd_resolution_context_is_current_v1(document, resolution_context)
    assert document.model_dump(mode="json") == before


def test_binding_requires_editable_input_and_rejects_spoofed_binding(
    resolution_context,
):
    bound = bind_eipd_resolution_v1({}, resolution_context)
    with pytest.raises(ValidationError):
        bind_eipd_resolution_v1(bound, resolution_context)
    with pytest.raises(ValidationError):
        bind_eipd_resolution_v1({"context_binding": None}, resolution_context)


def test_mutated_model_instances_revalidated(resolution_context):
    context = EipdResolutionContextV1.model_validate(resolution_context)
    context.legal_basis = "invalid"
    with pytest.raises(ValidationError):
        build_eipd_resolution_context_hash_v1(context)
    document = EipdResolutionAssessmentV1()
    document.residual_risk_level = "invalid"
    with pytest.raises(ValidationError):
        bind_eipd_resolution_v1(document, resolution_context)
    bound = bind_eipd_resolution_v1({}, resolution_context)
    bound.context_binding.context_hash = "invalid"
    with pytest.raises(ValidationError):
        build_eipd_resolution_document_hash_v1(bound)


def test_nested_context_model_mutation_revalidated(resolution_context):
    resolution_context["sensitive_rights_exception_assessment"] = {}
    context = EipdResolutionContextV1.model_validate(resolution_context)
    context.sensitive_rights_exception_assessment.exception_basis = "invalid"
    with pytest.raises(ValidationError):
        build_eipd_resolution_context_hash_v1(context)
