import unicodedata
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.db.models import (
    InternationalTransfer,
    LegalAssessment,
    LegalAssessmentSeries,
    System,
    Treatment,
    TreatmentDataCategory,
    TreatmentDataSource,
    TreatmentDataSubject,
    TreatmentPurpose,
    TreatmentVendor,
    Vendor,
)
from app.schemas.licitud import (
    LegalAssessmentDraftCreate,
    LegalAssessmentDraftUpdate,
    LegalAssessmentScopeIn,
)
from app.services import licitud as licitud_service
from app.services.licitud import (
    _load_vendors_by_id,
    build_purpose_key_v1,
    build_third_parties_from_m2_v1,
    canonicalize_text_v1,
    resolve_data_categories_from_m2_v1,
    resolve_data_subjects_from_m2_v1,
    resolve_purpose_from_m2_v1,
)


def test_canonicalize_text_v1_normaliza_unicode_nfc():
    precompuesto = "Gestión de clientes"
    combinado = "Gestio\u0301n de clientes"

    assert precompuesto != combinado
    assert canonicalize_text_v1(precompuesto) == canonicalize_text_v1(combinado)
    assert unicodedata.is_normalized("NFC", canonicalize_text_v1(combinado))


def test_canonicalize_text_v1_colapsa_whitespace_unicode():
    texto = "\t Gestión\u00a0de\n  clientes \r\n"

    assert canonicalize_text_v1(texto) == "gestión de clientes"


def test_canonicalize_text_v1_aplica_casefold():
    assert canonicalize_text_v1("GESTIÓN DE CLIENTES") == "gestión de clientes"
    assert canonicalize_text_v1("Straße") == canonicalize_text_v1("STRASSE")


def test_canonicalize_text_v1_preserva_puntuacion():
    assert canonicalize_text_v1("Clientes, proveedores.") == ("clientes, proveedores.")
    assert canonicalize_text_v1("Clientes proveedores") != (
        canonicalize_text_v1("Clientes, proveedores.")
    )


def test_canonicalize_text_v1_no_elimina_tildes_ni_diacriticos():
    assert canonicalize_text_v1("Gestión") == "gestión"
    assert canonicalize_text_v1("Gestión") != canonicalize_text_v1("Gestion")


def test_build_purpose_key_v1_es_estable_para_textos_equivalentes():
    clave_a = build_purpose_key_v1("  Gestión de CLIENTES ")
    clave_b = build_purpose_key_v1("Gestio\u0301n\tde\nclientes")

    assert clave_a == clave_b
    assert len(clave_a) == 64


def test_build_purpose_key_v1_cambia_ante_cambio_material():
    clave_clientes = build_purpose_key_v1("Gestión de clientes")
    clave_proveedores = build_purpose_key_v1("Gestión de proveedores")

    assert clave_clientes != clave_proveedores


def test_canonicalize_optional_text_v1_normaliza_null_y_vacios():
    from app.services.licitud import canonicalize_optional_text_v1

    assert canonicalize_optional_text_v1(None) is None
    assert canonicalize_optional_text_v1("") is None
    assert canonicalize_optional_text_v1("   \t\n ") is None


def test_canonicalize_optional_text_v1_canoniza_texto_no_vacio():
    from app.services.licitud import canonicalize_optional_text_v1

    assert canonicalize_optional_text_v1("  Cinco AÑOS  ") == "cinco años"


def test_canonicalize_data_categories_v1_canoniza_y_ordena():
    from app.schemas.licitud import RatCanonicalDataCategoryV1
    from app.services.licitud import canonicalize_data_categories_v1

    items = [
        RatCanonicalDataCategoryV1(
            category_code="  SALUD ",
            category_name=" Datos   de Salud ",
            is_sensitive=True,
        ),
        RatCanonicalDataCategoryV1(
            category_code="Identificacion",
            category_name=" Datos de Identificación ",
            is_sensitive=False,
        ),
    ]

    result = canonicalize_data_categories_v1(items)

    assert [item.model_dump() for item in result] == [
        {
            "category_code": "identificacion",
            "category_name": "datos de identificación",
            "is_sensitive": False,
        },
        {
            "category_code": "salud",
            "category_name": "datos de salud",
            "is_sensitive": True,
        },
    ]


def test_canonicalize_data_subjects_v1_canoniza_y_ordena():
    from app.schemas.licitud import RatCanonicalDataSubjectV1
    from app.services.licitud import canonicalize_data_subjects_v1

    items = [
        RatCanonicalDataSubjectV1(
            category_code=" TRABAJADORES ",
            category_name=" Trabajadores ",
            includes_children=False,
            includes_adolescents=False,
            is_vulnerable_group=False,
        ),
        RatCanonicalDataSubjectV1(
            category_code=" Clientes ",
            category_name=" CLIENTES ",
            includes_children=True,
            includes_adolescents=True,
            is_vulnerable_group=True,
        ),
    ]

    result = canonicalize_data_subjects_v1(items)

    assert [item.model_dump() for item in result] == [
        {
            "category_code": "clientes",
            "category_name": "clientes",
            "includes_children": True,
            "includes_adolescents": True,
            "is_vulnerable_group": True,
        },
        {
            "category_code": "trabajadores",
            "category_name": "trabajadores",
            "includes_children": False,
            "includes_adolescents": False,
            "is_vulnerable_group": False,
        },
    ]


def test_canonicalize_data_sources_v1_canoniza_y_ordena():
    from app.schemas.licitud import RatCanonicalDataSourceV1
    from app.services.licitud import canonicalize_data_sources_v1

    items = [
        RatCanonicalDataSourceV1(
            source_type="tercero",
            description="  Proveedor   EXTERNO ",
            is_public_source=False,
        ),
        RatCanonicalDataSourceV1(
            source_type="titular",
            description="   ",
            is_public_source=False,
        ),
        RatCanonicalDataSourceV1(
            source_type="titular",
            description=None,
            is_public_source=True,
        ),
    ]

    result = canonicalize_data_sources_v1(items)

    assert [item.model_dump() for item in result] == [
        {
            "source_type": "tercero",
            "description": "proveedor externo",
            "is_public_source": False,
        },
        {
            "source_type": "titular",
            "description": None,
            "is_public_source": False,
        },
        {
            "source_type": "titular",
            "description": None,
            "is_public_source": True,
        },
    ]


def test_canonicalize_third_parties_v1_canoniza_y_ordena():
    from app.schemas.licitud import RatCanonicalThirdPartyV1
    from app.services.licitud import canonicalize_third_parties_v1

    items = [
        RatCanonicalThirdPartyV1(
            relationship_type="encargado",
            has_data_access=True,
            country=" Estados   Unidos ",
            has_subprocessors=True,
            purpose="  Procesamiento de DATOS ",
        ),
        RatCanonicalThirdPartyV1(
            relationship_type="encargado",
            has_data_access=False,
            country="   ",
            has_subprocessors=False,
            purpose=None,
        ),
        RatCanonicalThirdPartyV1(
            relationship_type="cesionario",
            has_data_access=True,
            country=" Chile ",
            has_subprocessors=False,
            purpose=" Cumplimiento LEGAL ",
        ),
    ]

    result = canonicalize_third_parties_v1(items)

    assert [item.model_dump() for item in result] == [
        {
            "relationship_type": "cesionario",
            "has_data_access": True,
            "country": "chile",
            "has_subprocessors": False,
            "purpose": "cumplimiento legal",
        },
        {
            "relationship_type": "encargado",
            "has_data_access": False,
            "country": None,
            "has_subprocessors": False,
            "purpose": None,
        },
        {
            "relationship_type": "encargado",
            "has_data_access": True,
            "country": "estados unidos",
            "has_subprocessors": True,
            "purpose": "procesamiento de datos",
        },
    ]


def test_canonicalize_international_transfers_v1_canoniza_y_ordena():
    from app.schemas.licitud import RatCanonicalInternationalTransferV1
    from app.services.licitud import canonicalize_international_transfers_v1

    items = [
        RatCanonicalInternationalTransferV1(
            destination_country=" Estados   Unidos ",
            adequacy_status="pendiente",
            mechanism="  Cláusulas CONTRACTUALES ",
            guarantees_description="   ",
        ),
        RatCanonicalInternationalTransferV1(
            destination_country=" Chile ",
            adequacy_status="adecuado",
            mechanism=None,
            guarantees_description=None,
        ),
    ]

    result = canonicalize_international_transfers_v1(items)

    assert [item.model_dump() for item in result] == [
        {
            "destination_country": "chile",
            "adequacy_status": "adecuado",
            "mechanism": None,
            "guarantees_description": None,
        },
        {
            "destination_country": "estados unidos",
            "adequacy_status": "pendiente",
            "mechanism": "cláusulas contractuales",
            "guarantees_description": None,
        },
    ]


def test_derive_special_regimes_v1_deriva_solo_desde_alcance_seleccionado():
    from app.schemas.licitud import (
        RatCanonicalDataCategoryV1,
        RatCanonicalDataSubjectV1,
    )
    from app.services.licitud import derive_special_regimes_v1

    categories = [
        RatCanonicalDataCategoryV1(
            category_code="salud",
            category_name="datos de salud",
            is_sensitive=True,
        )
    ]
    subjects = [
        RatCanonicalDataSubjectV1(
            category_code="menores",
            category_name="menores",
            includes_children=True,
            includes_adolescents=True,
            is_vulnerable_group=True,
        )
    ]

    result = derive_special_regimes_v1(categories, subjects)

    assert result.model_dump() == {
        "has_sensitive_data": True,
        "includes_children": True,
        "includes_adolescents": True,
        "has_vulnerable_groups": True,
    }


def test_derive_special_regimes_v1_alcance_vacio_es_false():
    from app.services.licitud import derive_special_regimes_v1

    result = derive_special_regimes_v1([], [])

    assert result.model_dump() == {
        "has_sensitive_data": False,
        "includes_children": False,
        "includes_adolescents": False,
        "has_vulnerable_groups": False,
    }


def test_build_rat_canonical_context_v1_ensambla_contexto_completo():
    from app.schemas.licitud import (
        RatCanonicalDataCategoryV1,
        RatCanonicalDataSourceV1,
        RatCanonicalDataSubjectV1,
        RatCanonicalInternationalTransferV1,
        RatCanonicalThirdPartyV1,
    )
    from app.services.licitud import build_rat_canonical_context_v1

    result = build_rat_canonical_context_v1(
        purpose="  Gestión   de CLIENTES ",
        organization_role="responsable",
        data_categories=[
            RatCanonicalDataCategoryV1(
                category_code=" SALUD ",
                category_name=" Datos de Salud ",
                is_sensitive=True,
            )
        ],
        data_subjects=[
            RatCanonicalDataSubjectV1(
                category_code=" CLIENTES ",
                category_name=" Clientes ",
                includes_children=True,
                includes_adolescents=False,
                is_vulnerable_group=False,
            )
        ],
        data_sources=[
            RatCanonicalDataSourceV1(
                source_type="titular",
                description="  Formulario WEB ",
                is_public_source=False,
            )
        ],
        retention_rule="  Cinco AÑOS ",
        has_automated_decisions=False,
        automated_decision_description="Este texto no debe participar",
        third_parties=[
            RatCanonicalThirdPartyV1(
                relationship_type="encargado",
                has_data_access=True,
                country=" Chile ",
                has_subprocessors=False,
                purpose=" Prestación del SERVICIO ",
            )
        ],
        international_transfers=[
            RatCanonicalInternationalTransferV1(
                destination_country=" Estados Unidos ",
                adequacy_status="pendiente",
                mechanism=None,
                guarantees_description="   ",
            )
        ],
    )

    assert result.purpose == "gestión de clientes"
    assert result.organization_role == "responsable"
    assert result.retention.retention_rule == "cinco años"
    assert result.automated_decisions.has_automated_decisions is False
    assert result.automated_decisions.description is None
    assert result.systems == []
    assert result.data_sources[0].description == "formulario web"
    assert result.third_parties[0].country == "chile"
    assert result.international_transfers[0].destination_country == "estados unidos"
    assert result.special_regimes.model_dump() == {
        "has_sensitive_data": True,
        "includes_children": True,
        "includes_adolescents": False,
        "has_vulnerable_groups": False,
    }


def test_build_rat_canonical_context_v1_conserva_descripcion_si_hay_decision_automatizada():
    from app.services.licitud import build_rat_canonical_context_v1

    result = build_rat_canonical_context_v1(
        purpose="Gestión de clientes",
        organization_role=None,
        data_categories=[],
        data_subjects=[],
        data_sources=[],
        retention_rule=None,
        has_automated_decisions=True,
        automated_decision_description="  PERFILAMIENTO   automático ",
        third_parties=[],
        international_transfers=[],
    )

    assert result.automated_decisions.has_automated_decisions is True
    assert result.automated_decisions.description == "perfilamiento automático"


def test_serialize_rat_canonical_context_v1_produce_json_canonico_utf8():
    from app.services.licitud import (
        build_rat_canonical_context_v1,
        serialize_rat_canonical_context_v1,
    )

    context = build_rat_canonical_context_v1(
        purpose="Gestión de clientes",
        organization_role="responsable",
        data_categories=[],
        data_subjects=[],
        data_sources=[],
        retention_rule=None,
        has_automated_decisions=False,
        automated_decision_description=None,
        third_parties=[],
        international_transfers=[],
    )

    serialized = serialize_rat_canonical_context_v1(context)

    assert isinstance(serialized, bytes)
    assert b"\n" not in serialized
    assert b'": ' not in serialized
    assert b'", ' not in serialized
    assert b"}, " not in serialized
    assert b"], " not in serialized
    assert b"\\u00f3" not in serialized
    assert "gestión de clientes".encode() in serialized

    decoded = serialized.decode("utf-8")
    assert decoded.startswith('{"automated_decisions":')
    assert decoded.endswith("}")


def test_build_rat_context_hash_v1_es_estable_para_contextos_equivalentes():
    from app.schemas.licitud import RatCanonicalDataCategoryV1
    from app.services.licitud import (
        build_rat_canonical_context_v1,
        build_rat_context_hash_v1,
    )

    context_a = build_rat_canonical_context_v1(
        purpose="  Gestión de CLIENTES ",
        organization_role="responsable",
        data_categories=[
            RatCanonicalDataCategoryV1(
                category_code=" SALUD ",
                category_name=" Datos de Salud ",
                is_sensitive=True,
            ),
            RatCanonicalDataCategoryV1(
                category_code=" IDENTIFICACION ",
                category_name=" Datos de Identificación ",
                is_sensitive=False,
            ),
        ],
        data_subjects=[],
        data_sources=[],
        retention_rule=" 5 AÑOS ",
        has_automated_decisions=False,
        automated_decision_description=None,
        third_parties=[],
        international_transfers=[],
    )

    context_b = build_rat_canonical_context_v1(
        purpose="gestión   de clientes",
        organization_role="responsable",
        data_categories=[
            RatCanonicalDataCategoryV1(
                category_code="identificacion",
                category_name="datos de identificación",
                is_sensitive=False,
            ),
            RatCanonicalDataCategoryV1(
                category_code="salud",
                category_name="datos de salud",
                is_sensitive=True,
            ),
        ],
        data_subjects=[],
        data_sources=[],
        retention_rule="5 años",
        has_automated_decisions=False,
        automated_decision_description=None,
        third_parties=[],
        international_transfers=[],
    )

    hash_a = build_rat_context_hash_v1(context_a)
    hash_b = build_rat_context_hash_v1(context_b)

    assert hash_a == hash_b
    assert len(hash_a) == 64


def test_build_rat_context_hash_v1_cambia_ante_cambio_semantico():
    from app.services.licitud import (
        build_rat_canonical_context_v1,
        build_rat_context_hash_v1,
    )

    base = dict(
        purpose="gestión de clientes",
        organization_role="responsable",
        data_categories=[],
        data_subjects=[],
        data_sources=[],
        has_automated_decisions=False,
        automated_decision_description=None,
        third_parties=[],
        international_transfers=[],
    )

    context_a = build_rat_canonical_context_v1(
        **base,
        retention_rule="5 años",
    )
    context_b = build_rat_canonical_context_v1(
        **base,
        retention_rule="10 años",
    )

    assert build_rat_context_hash_v1(context_a) != build_rat_context_hash_v1(context_b)


@pytest.mark.asyncio
async def test_load_vendors_by_id_carga_en_batch_e_indexa_por_uuid():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    vendor_a = Vendor(
        id=uuid.UUID("d0000000-0000-0000-0000-000000000011"),
        organization_id=organization_id,
        name="Proveedor A",
        country="Chile",
    )
    vendor_b = Vendor(
        id=uuid.UUID("d0000000-0000-0000-0000-000000000012"),
        organization_id=organization_id,
        name="Proveedor B",
        country="Estados Unidos",
    )

    result = MagicMock()
    result.scalars.return_value.all.return_value = [vendor_a, vendor_b]

    db = AsyncMock()
    db.execute.return_value = result

    vendors = await _load_vendors_by_id(
        db,
        organization_id,
        {vendor_a.id, vendor_b.id},
    )

    assert vendors == {
        vendor_a.id: vendor_a,
        vendor_b.id: vendor_b,
    }
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_load_vendors_by_id_no_consulta_si_lista_vacia():
    db = AsyncMock()

    vendors = await _load_vendors_by_id(
        db,
        uuid.UUID("d0000000-0000-0000-0000-000000000001"),
        set(),
    )

    assert vendors == {}
    db.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_build_third_parties_from_m2_v1_combina_vendor_y_canoniza():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")
    vendor_id = uuid.UUID("d0000000-0000-0000-0000-000000000011")

    relationship = TreatmentVendor(
        organization_id=organization_id,
        treatment_id=treatment_id,
        vendor_id=vendor_id,
        relationship_type="encargado",
        purpose="  Prestación   del SERVICIO ",
        has_data_access=True,
        has_subprocessors=False,
    )
    vendor = Vendor(
        id=vendor_id,
        organization_id=organization_id,
        name="Proveedor A",
        country="  CHILE ",
    )

    result = MagicMock()
    result.scalars.return_value.all.return_value = [vendor]

    db = AsyncMock()
    db.execute.return_value = result

    items = await build_third_parties_from_m2_v1(
        db,
        organization_id,
        [relationship],
    )

    assert len(items) == 1
    assert items[0].relationship_type == "encargado"
    assert items[0].has_data_access is True
    assert items[0].country == "chile"
    assert items[0].has_subprocessors is False
    assert items[0].purpose == "prestación del servicio"
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_build_third_parties_from_m2_v1_rechaza_vendor_faltante():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")
    vendor_id = uuid.UUID("d0000000-0000-0000-0000-000000000099")

    relationship = TreatmentVendor(
        organization_id=organization_id,
        treatment_id=treatment_id,
        vendor_id=vendor_id,
        relationship_type="encargado",
        purpose="Prestación del servicio",
        has_data_access=True,
        has_subprocessors=False,
    )

    result = MagicMock()
    result.scalars.return_value.all.return_value = []

    db = AsyncMock()
    db.execute.return_value = result

    with pytest.raises(HTTPException) as exc:
        await build_third_parties_from_m2_v1(
            db,
            organization_id,
            [relationship],
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "Uno o más proveedores asociados no pertenecen a la organización"
    )
    db.execute.assert_awaited_once()


def test_reserve_next_version_v1_incrementa_y_devuelve_version_asignada():
    series = LegalAssessmentSeries(
        organization_id=uuid.uuid4(),
        treatment_id=uuid.uuid4(),
        purpose_key="purpose-key",
        purpose_text="Gestión de clientes",
        next_version=3,
    )

    version = licitud_service._reserve_next_version_v1(series)

    assert version == 3
    assert series.next_version == 4


async def test_get_or_create_series_for_update_v1_inserta_idempotente_y_bloquea():
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    purpose = TreatmentPurpose(
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose=" Gestión de clientes ",
    )
    series = LegalAssessmentSeries(
        id=uuid.uuid4(),
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose_key=build_purpose_key_v1(purpose.purpose),
        purpose_text=purpose.purpose,
        next_version=1,
    )

    insert_result = MagicMock()
    select_result = MagicMock()
    select_result.scalar_one.return_value = series

    db = AsyncMock()
    db.execute.side_effect = [insert_result, select_result]

    result = await licitud_service._get_or_create_series_for_update_v1(
        db,
        organization_id,
        treatment_id,
        purpose,
        profile_id,
    )

    assert result is series
    assert db.execute.await_count == 2

    insert_stmt = db.execute.await_args_list[0].args[0]
    compiled_insert = insert_stmt.compile()
    assert organization_id in compiled_insert.params.values()
    assert treatment_id in compiled_insert.params.values()
    assert profile_id in compiled_insert.params.values()
    assert build_purpose_key_v1(purpose.purpose) in compiled_insert.params.values()

    select_stmt = db.execute.await_args_list[1].args[0]
    compiled_select = select_stmt.compile()
    assert organization_id in compiled_select.params.values()
    assert treatment_id in compiled_select.params.values()
    assert build_purpose_key_v1(purpose.purpose) in compiled_select.params.values()
    assert select_stmt._for_update_arg is not None


async def test_resolve_purpose_by_id_from_m2_v1_resuelve_selector_operativo():
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    purpose_id = uuid.uuid4()
    purpose = TreatmentPurpose(
        id=purpose_id,
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose="Gestión de clientes",
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = purpose
    db = AsyncMock()
    db.execute.return_value = result

    resolved = await licitud_service.resolve_purpose_by_id_from_m2_v1(
        db,
        organization_id,
        treatment_id,
        purpose_id,
    )

    assert resolved is purpose
    db.execute.assert_awaited_once()
    params = db.execute.call_args.args[0].compile().params
    assert organization_id in params.values()
    assert treatment_id in params.values()
    assert purpose_id in params.values()


async def test_resolve_purpose_by_id_from_m2_v1_rechaza_selector_ajeno():
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    purpose_id = uuid.uuid4()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db = AsyncMock()
    db.execute.return_value = result

    with pytest.raises(HTTPException) as exc:
        await licitud_service.resolve_purpose_by_id_from_m2_v1(
            db,
            organization_id,
            treatment_id,
            purpose_id,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "La finalidad indicada no pertenece a la actividad de tratamiento"
    )


def test_resolve_purpose_from_m2_v1_resuelve_por_identidad_canonica():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    purpose = TreatmentPurpose(
        id=uuid.UUID("d0000000-0000-0000-0000-000000000021"),
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose="  Gestión   de CLIENTES ",
        is_primary=True,
        sort_order=0,
    )

    purpose_key = build_purpose_key_v1("gestión de clientes")

    resolved = resolve_purpose_from_m2_v1(
        [purpose],
        purpose_key,
    )

    assert resolved is purpose


def test_resolve_purpose_from_m2_v1_rechaza_finalidad_inexistente():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    purpose = TreatmentPurpose(
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose="Gestión de clientes",
        is_primary=True,
        sort_order=0,
    )

    unknown_key = build_purpose_key_v1("Selección de personal")

    with pytest.raises(HTTPException) as exc:
        resolve_purpose_from_m2_v1(
            [purpose],
            unknown_key,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "La finalidad indicada no pertenece a la actividad de tratamiento"
    )


def test_resolve_purpose_from_m2_v1_rechaza_ambiguedad_canonica():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    purposes = [
        TreatmentPurpose(
            organization_id=organization_id,
            treatment_id=treatment_id,
            purpose="Gestión de clientes",
            is_primary=True,
            sort_order=0,
        ),
        TreatmentPurpose(
            organization_id=organization_id,
            treatment_id=treatment_id,
            purpose=" GESTIÓN   DE CLIENTES ",
            is_primary=False,
            sort_order=1,
        ),
    ]

    purpose_key = build_purpose_key_v1("gestión de clientes")

    with pytest.raises(HTTPException) as exc:
        resolve_purpose_from_m2_v1(
            purposes,
            purpose_key,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "El RAT contiene finalidades canónicamente ambiguas"


def test_resolve_data_categories_from_m2_v1_resuelve_codigos_canonicos():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    category_a = TreatmentDataCategory(
        organization_id=organization_id,
        treatment_id=treatment_id,
        category_code=" IDENTIFICACION ",
        category_name="Datos de identificación",
        is_sensitive=False,
    )
    category_b = TreatmentDataCategory(
        organization_id=organization_id,
        treatment_id=treatment_id,
        category_code="SALUD",
        category_name="Datos de salud",
        is_sensitive=True,
    )

    resolved = resolve_data_categories_from_m2_v1(
        [category_a, category_b],
        ["salud", " identificacion "],
    )

    assert resolved == [category_b, category_a]


def test_resolve_data_categories_from_m2_v1_rechaza_scope_canonico_duplicado():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    category = TreatmentDataCategory(
        organization_id=organization_id,
        treatment_id=treatment_id,
        category_code="SALUD",
        category_name="Datos de salud",
        is_sensitive=True,
    )

    with pytest.raises(HTTPException) as exc:
        resolve_data_categories_from_m2_v1(
            [category],
            ["SALUD", " salud "],
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "data_category_codes contiene códigos canónicamente duplicados"
    )


def test_resolve_data_categories_from_m2_v1_rechaza_codigo_inexistente():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    category = TreatmentDataCategory(
        organization_id=organization_id,
        treatment_id=treatment_id,
        category_code="IDENTIFICACION",
        category_name="Datos de identificación",
        is_sensitive=False,
    )

    with pytest.raises(HTTPException) as exc:
        resolve_data_categories_from_m2_v1(
            [category],
            ["salud"],
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "Una o más categorías de datos seleccionadas no pertenecen "
        "a la actividad de tratamiento"
    )


def test_resolve_data_categories_from_m2_v1_rechaza_ambiguedad_canonica_rat():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    categories = [
        TreatmentDataCategory(
            organization_id=organization_id,
            treatment_id=treatment_id,
            category_code="SALUD",
            category_name="Datos de salud",
            is_sensitive=True,
        ),
        TreatmentDataCategory(
            organization_id=organization_id,
            treatment_id=treatment_id,
            category_code=" salud ",
            category_name="Información de salud",
            is_sensitive=True,
        ),
    ]

    with pytest.raises(HTTPException) as exc:
        resolve_data_categories_from_m2_v1(
            categories,
            ["salud"],
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "El RAT contiene categorías de datos canónicamente ambiguas"
    )


def test_resolve_data_subjects_from_m2_v1_resuelve_codigos_canonicos():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    subject_a = TreatmentDataSubject(
        organization_id=organization_id,
        treatment_id=treatment_id,
        category_code=" MENORES ",
        category_name="Niños y adolescentes",
        includes_children=True,
        includes_adolescents=True,
        is_vulnerable_group=False,
    )
    subject_b = TreatmentDataSubject(
        organization_id=organization_id,
        treatment_id=treatment_id,
        category_code="CLIENTES",
        category_name="Clientes",
        includes_children=False,
        includes_adolescents=False,
        is_vulnerable_group=False,
    )

    resolved = resolve_data_subjects_from_m2_v1(
        [subject_a, subject_b],
        [" clientes ", "MENORES"],
    )

    assert resolved == [subject_b, subject_a]


def test_resolve_data_subjects_from_m2_v1_rechaza_scope_canonico_duplicado():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    subject = TreatmentDataSubject(
        organization_id=organization_id,
        treatment_id=treatment_id,
        category_code="CLIENTES",
        category_name="Clientes",
        includes_children=False,
        includes_adolescents=False,
        is_vulnerable_group=False,
    )

    with pytest.raises(HTTPException) as exc:
        resolve_data_subjects_from_m2_v1(
            [subject],
            ["CLIENTES", " clientes "],
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "data_subject_codes contiene códigos canónicamente duplicados"
    )


def test_resolve_data_subjects_from_m2_v1_rechaza_codigo_inexistente():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    subject = TreatmentDataSubject(
        organization_id=organization_id,
        treatment_id=treatment_id,
        category_code="CLIENTES",
        category_name="Clientes",
        includes_children=False,
        includes_adolescents=False,
        is_vulnerable_group=False,
    )

    with pytest.raises(HTTPException) as exc:
        resolve_data_subjects_from_m2_v1(
            [subject],
            ["trabajadores"],
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "Uno o más titulares de datos seleccionados no pertenecen "
        "a la actividad de tratamiento"
    )


def test_resolve_data_subjects_from_m2_v1_rechaza_ambiguedad_canonica_rat():
    organization_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    treatment_id = uuid.UUID("d0000000-0000-0000-0000-000000000002")

    subjects = [
        TreatmentDataSubject(
            organization_id=organization_id,
            treatment_id=treatment_id,
            category_code="CLIENTES",
            category_name="Clientes",
            includes_children=False,
            includes_adolescents=False,
            is_vulnerable_group=False,
        ),
        TreatmentDataSubject(
            organization_id=organization_id,
            treatment_id=treatment_id,
            category_code=" clientes ",
            category_name="Personas clientes",
            includes_children=False,
            includes_adolescents=False,
            is_vulnerable_group=False,
        ),
    ]

    with pytest.raises(HTTPException) as exc:
        resolve_data_subjects_from_m2_v1(
            subjects,
            ["clientes"],
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "El RAT contiene titulares de datos canónicamente ambiguos"
    )


def test_build_rat_context_snapshot_v1_conserva_hechos_documentales():
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    vendor_id = uuid.uuid4()

    treatment = Treatment(
        id=treatment_id,
        organization_id=organization_id,
        name="Actividad",
        organization_role="responsable",
        retention_rule=" Cinco años ",
        deletion_method=" Borrado seguro ",
        has_automated_decisions=False,
        automated_decision_description=" Descripción conservada ",
    )
    purpose = TreatmentPurpose(
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose=" Gestión de clientes ",
    )
    categories = [
        TreatmentDataCategory(
            organization_id=organization_id,
            treatment_id=treatment_id,
            category_code="ID",
            category_name="Identidad",
            is_sensitive=False,
            notes=" Nota categoría ",
        )
    ]
    subjects = [
        TreatmentDataSubject(
            organization_id=organization_id,
            treatment_id=treatment_id,
            category_code="CLIENTES",
            category_name="Clientes",
            includes_children=False,
            includes_adolescents=False,
            is_vulnerable_group=False,
            notes=" Nota titular ",
        )
    ]
    sources = [
        TreatmentDataSource(
            organization_id=organization_id,
            treatment_id=treatment_id,
            source_type="titular",
            description=" Formulario WEB ",
            is_public_source=False,
        )
    ]
    systems = [
        System(
            organization_id=organization_id,
            name="CRM",
            provider=" Proveedor sistema ",
            hosting_location=" Cloud ",
            hosting_country=" Chile ",
            is_international=True,
        )
    ]
    relationships = [
        TreatmentVendor(
            organization_id=organization_id,
            treatment_id=treatment_id,
            vendor_id=vendor_id,
            relationship_type="encargado",
            purpose=" Hosting ",
            has_data_access=True,
            has_contract=True,
            contract_reference=" C-123 ",
            engagement_object=" Servicio cloud ",
            engagement_duration=" 12 meses ",
            has_subprocessors=False,
            notes=" Nota proveedor ",
        )
    ]
    vendors_by_id = {
        vendor_id: Vendor(
            id=vendor_id,
            organization_id=organization_id,
            name="Proveedor A",
            country=" Chile ",
        )
    }
    transfers = [
        InternationalTransfer(
            organization_id=organization_id,
            treatment_id=treatment_id,
            vendor_id=vendor_id,
            recipient_name=None,
            destination_country=" España ",
            adequacy_status="pendiente",
            mechanism=" Cláusulas contractuales ",
            guarantees_description=" Garantías ",
            evidence_reference=" EV-001 ",
        )
    ]

    snapshot = licitud_service.build_rat_context_snapshot_v1(
        treatment=treatment,
        purpose=purpose,
        data_categories=categories,
        data_subjects=subjects,
        data_sources=sources,
        systems=systems,
        relationships=relationships,
        vendors_by_id=vendors_by_id,
        international_transfers=transfers,
    )

    assert snapshot.purpose == " Gestión de clientes "
    assert snapshot.data_categories[0].notes == " Nota categoría "
    assert snapshot.data_subjects[0].notes == " Nota titular "
    assert snapshot.data_sources[0].description == " Formulario WEB "
    assert snapshot.retention.retention_rule == " Cinco años "
    assert snapshot.retention.deletion_method == " Borrado seguro "
    assert snapshot.automated_decisions.description == " Descripción conservada "
    assert snapshot.systems[0].hosting_country == " Chile "
    assert snapshot.systems[0].is_international is True
    assert snapshot.third_parties[0].vendor_name == "Proveedor A"
    assert snapshot.third_parties[0].contract_reference == " C-123 "
    assert snapshot.international_transfers[0].recipient_name == "Proveedor A"
    assert snapshot.international_transfers[0].evidence_reference == " EV-001 "
    assert not any(snapshot.special_regimes.model_dump().values())


def test_build_rat_context_snapshot_v1_prefiere_recipient_name_factual():
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    vendor_id = uuid.uuid4()

    treatment = Treatment(
        id=treatment_id,
        organization_id=organization_id,
        name="Actividad",
        has_automated_decisions=False,
    )
    purpose = TreatmentPurpose(
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose="Finalidad",
    )
    vendors_by_id = {
        vendor_id: Vendor(
            id=vendor_id,
            organization_id=organization_id,
            name="Nombre del proveedor",
        )
    }
    transfers = [
        InternationalTransfer(
            organization_id=organization_id,
            treatment_id=treatment_id,
            vendor_id=vendor_id,
            recipient_name="Destinatario factual",
            destination_country="España",
            adequacy_status="pendiente",
        )
    ]

    snapshot = licitud_service.build_rat_context_snapshot_v1(
        treatment=treatment,
        purpose=purpose,
        data_categories=[],
        data_subjects=[],
        data_sources=[],
        systems=[],
        relationships=[],
        vendors_by_id=vendors_by_id,
        international_transfers=transfers,
    )

    assert snapshot.international_transfers[0].recipient_name == "Destinatario factual"


def test_build_rat_context_snapshot_v1_rechaza_vendor_fallback_no_resuelto():
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    vendor_id = uuid.uuid4()

    treatment = Treatment(
        id=treatment_id,
        organization_id=organization_id,
        name="Actividad",
        has_automated_decisions=False,
    )
    purpose = TreatmentPurpose(
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose="Finalidad",
    )
    transfers = [
        InternationalTransfer(
            organization_id=organization_id,
            treatment_id=treatment_id,
            vendor_id=vendor_id,
            recipient_name=None,
            destination_country="España",
            adequacy_status="pendiente",
        )
    ]

    with pytest.raises(HTTPException) as exc:
        licitud_service.build_rat_context_snapshot_v1(
            treatment=treatment,
            purpose=purpose,
            data_categories=[],
            data_subjects=[],
            data_sources=[],
            systems=[],
            relationships=[],
            vendors_by_id={},
            international_transfers=transfers,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "Uno o más destinatarios asociados no pertenecen a la organización"
    )


def test_build_rat_context_snapshot_v1_ordena_documental_sin_deduplicar():
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()

    treatment = Treatment(
        id=treatment_id,
        organization_id=organization_id,
        name="Actividad",
        has_automated_decisions=False,
    )
    purpose = TreatmentPurpose(
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose="Finalidad",
    )
    sources = [
        TreatmentDataSource(
            organization_id=organization_id,
            treatment_id=treatment_id,
            source_type="titular",
            description="beta",
            is_public_source=False,
        ),
        TreatmentDataSource(
            organization_id=organization_id,
            treatment_id=treatment_id,
            source_type="titular",
            description=None,
            is_public_source=False,
        ),
        TreatmentDataSource(
            organization_id=organization_id,
            treatment_id=treatment_id,
            source_type="titular",
            description="Alpha",
            is_public_source=False,
        ),
        TreatmentDataSource(
            organization_id=organization_id,
            treatment_id=treatment_id,
            source_type="titular",
            description="beta",
            is_public_source=False,
        ),
    ]

    snapshot = licitud_service.build_rat_context_snapshot_v1(
        treatment=treatment,
        purpose=purpose,
        data_categories=[],
        data_subjects=[],
        data_sources=sources,
        systems=[],
        relationships=[],
        vendors_by_id={},
        international_transfers=[],
    )

    assert [item.description for item in snapshot.data_sources] == [
        None,
        "Alpha",
        "beta",
        "beta",
    ]


def _source_m3(**overrides):
    values = dict(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        treatment_id=uuid.uuid4(),
        source_type="titular",
        description="  Formulario WEB ",
        is_public_source=False,
    )
    values.update(overrides)
    return TreatmentDataSource(**values)


def _transfer_m3(**overrides):
    values = dict(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        treatment_id=uuid.uuid4(),
        destination_country="  ESPAÑA ",
        adequacy_status="pendiente",
        mechanism="  Cláusulas CONTRACTUALES ",
        guarantees_description="  ",
        recipient_name="Destinatario original",
    )
    values.update(overrides)
    return InternationalTransfer(**values)


def _context_m3(sources, transfers):
    return licitud_service.build_rat_canonical_context_v1(
        purpose="Clientes",
        organization_role="responsable",
        data_categories=[],
        data_subjects=[],
        data_sources=licitud_service.build_data_sources_from_m2_v1(sources),
        retention_rule=None,
        has_automated_decisions=False,
        automated_decision_description=None,
        third_parties=[],
        international_transfers=(
            licitud_service.build_international_transfers_from_m2_v1(transfers)
        ),
    )


def test_m2_fuentes_y_transferencias_proyectan_solo_campos_semanticos():
    source, transfer = _source_m3(), _transfer_m3()
    result = _context_m3([source], [transfer])
    assert result.data_sources[0].model_dump() == {
        "source_type": "titular",
        "description": "formulario web",
        "is_public_source": False,
    }
    assert result.international_transfers[0].model_dump() == {
        "destination_country": "españa",
        "adequacy_status": "pendiente",
        "mechanism": "cláusulas contractuales",
        "guarantees_description": None,
    }
    assert source.description == "  Formulario WEB "
    assert transfer.destination_country == "  ESPAÑA "


@pytest.mark.parametrize("empty", [None, "", " \t\n\u00a0"])
def test_m2_proyecciones_normalizan_opcionales_vacios(empty):
    context = _context_m3(
        [_source_m3(description=empty)],
        [_transfer_m3(mechanism=empty, guarantees_description=empty)],
    )
    assert context.data_sources[0].description is None
    assert context.international_transfers[0].mechanism is None
    assert context.international_transfers[0].guarantees_description is None


@pytest.mark.parametrize("country", ["", " \t\n\u00a0"])
def test_m2_transferencia_rechaza_pais_vacio(country):
    with pytest.raises(HTTPException) as exc:
        _context_m3([], [_transfer_m3(destination_country=country)])
    assert exc.value.status_code == 400
    assert exc.value.detail == "El RAT contiene una transferencia sin país de destino"


def test_m2_hash_ignora_recreacion_orden_y_metadatos():
    sources = [_source_m3(), _source_m3(description=None)]
    transfers = [_transfer_m3(), _transfer_m3(destination_country="Chile")]
    original = _context_m3(sources, transfers)
    for row in sources + transfers:
        row.id = uuid.uuid4()
        row.created_at = datetime(2026, 9, 23, tzinfo=UTC)
        row.updated_at = datetime(2026, 9, 24, tzinfo=UTC)
    transfers[0].vendor_id = uuid.uuid4()
    transfers[0].recipient_name = "Nombre administrativo nuevo"
    transfers[0].evidence_reference = "Referencia actualizada"
    transfers[0].destination_country = "espan\u0303a"
    transfers[0].mechanism = "cláusulas\tcontractuales"
    sources[0].description = "formulario\nweb"
    equivalent = _context_m3(list(reversed(sources)), list(reversed(transfers)))
    assert licitud_service.build_rat_context_hash_v1(original) == (
        licitud_service.build_rat_context_hash_v1(equivalent)
    )


@pytest.mark.parametrize(
    "block,field,value",
    [
        ("source", "source_type", "tercero"),
        ("source", "description", "Recogida presencial"),
        ("source", "is_public_source", True),
        ("transfer", "destination_country", "Chile"),
        ("transfer", "adequacy_status", "no_determinado"),
        ("transfer", "mechanism", "Otro mecanismo"),
        ("transfer", "guarantees_description", "Garantías adicionales"),
    ],
)
def test_m2_hash_cambia_por_cada_hecho_semantico(block, field, value):
    source, transfer = _source_m3(), _transfer_m3()
    before = licitud_service.build_rat_context_hash_v1(
        _context_m3([source], [transfer])
    )
    setattr(source if block == "source" else transfer, field, value)
    after = licitud_service.build_rat_context_hash_v1(_context_m3([source], [transfer]))
    assert before != after


@pytest.mark.parametrize("block", ["source", "transfer"])
def test_m2_hash_conserva_multiplicidad_y_detecta_eliminacion(block):
    source, transfer = _source_m3(), _transfer_m3()
    single = _context_m3([source], [transfer])
    duplicate = _context_m3(
        [source, _source_m3()] if block == "source" else [source],
        [transfer, _transfer_m3()] if block == "transfer" else [transfer],
    )
    assert (
        len(
            duplicate.data_sources
            if block == "source"
            else duplicate.international_transfers
        )
        == 2
    )
    assert licitud_service.build_rat_context_hash_v1(single) != (
        licitud_service.build_rat_context_hash_v1(duplicate)
    )
    assert _context_m3([], []).data_sources == []
    assert _context_m3([], []).international_transfers == []


@pytest.fixture
def m2_context_reader(monkeypatch):
    org_id, treatment_id = uuid.uuid4(), uuid.uuid4()
    common = dict(organization_id=org_id, treatment_id=treatment_id)
    results = {
        "obtener_tratamiento": Treatment(
            id=treatment_id,
            organization_id=org_id,
            organization_role="responsable",
            retention_rule=" Cinco AÑOS ",
            has_automated_decisions=False,
            automated_decision_description="No participa",
        ),
        "listar_finalidades": [
            TreatmentPurpose(**common, purpose=" Gestión de clientes ")
        ],
        "listar_categorias_datos": [
            TreatmentDataCategory(
                **common,
                category_code="ID",
                category_name="Identidad",
                is_sensitive=False,
            ),
            TreatmentDataCategory(
                **common,
                category_code="SALUD",
                category_name="Salud",
                is_sensitive=True,
            ),
        ],
        "listar_titulares_datos": [
            TreatmentDataSubject(
                **common,
                category_code="CLIENTES",
                category_name="Clientes",
                includes_children=False,
                includes_adolescents=False,
                is_vulnerable_group=False,
            ),
            TreatmentDataSubject(
                **common,
                category_code="MENORES",
                category_name="Menores",
                includes_children=True,
                includes_adolescents=True,
                is_vulnerable_group=True,
            ),
        ],
        "listar_fuentes_datos": [_source_m3(**common)],
        "listar_sistemas_tratamiento": [],
        "listar_vendors_tratamiento": [],
        "listar_transferencias": [_transfer_m3(**common)],
    }
    readers = {}
    for name, value in results.items():
        readers[name] = AsyncMock(return_value=value)
        monkeypatch.setattr(licitud_service.rat_service, name, readers[name])
    return org_id, treatment_id, readers


async def test_update_legal_assessment_draft_v1_reutiliza_scope_y_no_consume_version(
    monkeypatch,
):
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    assessment_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    series_id = uuid.uuid4()

    snapshot = {
        "purpose": "Gestión de clientes",
        "organization_role": "responsable",
        "data_categories": [
            {
                "category_code": "ID",
                "category_name": "Identidad",
                "is_sensitive": False,
                "notes": None,
            }
        ],
        "data_subjects": [
            {
                "category_code": "CLIENTES",
                "category_name": "Clientes",
                "includes_children": False,
                "includes_adolescents": False,
                "is_vulnerable_group": False,
                "notes": None,
            }
        ],
        "data_sources": [],
        "retention": {
            "retention_rule": None,
            "deletion_method": None,
        },
        "automated_decisions": {
            "has_automated_decisions": False,
            "description": None,
        },
        "systems": [],
        "third_parties": [],
        "international_transfers": [],
        "special_regimes": {
            "has_sensitive_data": False,
            "includes_children": False,
            "includes_adolescents": False,
            "has_vulnerable_groups": False,
        },
    }
    assessment = LegalAssessment(
        id=assessment_id,
        organization_id=organization_id,
        series_id=series_id,
        treatment_id=treatment_id,
        version=2,
        status="borrador",
        legal_basis=None,
        justification=None,
        purpose_snapshot="Gestión de clientes",
        rat_context_hash="hash-anterior",
        rat_context_snapshot=snapshot,
    )
    series = LegalAssessmentSeries(
        id=series_id,
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose_key=build_purpose_key_v1("Gestión de clientes"),
        purpose_text="Gestión de clientes",
        next_version=3,
    )

    get_draft = AsyncMock(return_value=assessment)
    monkeypatch.setattr(
        licitud_service,
        "get_legal_assessment_draft_v1",
        get_draft,
    )

    updated_snapshot = licitud_service.RatContextSnapshotV1.model_validate(snapshot)
    bundle = licitud_service.RatContextBundleV1(
        canonical=_context_m3([], []),
        snapshot=updated_snapshot,
    )
    build_bundle = AsyncMock(return_value=bundle)
    monkeypatch.setattr(
        licitud_service,
        "build_rat_context_bundle_from_m2_v1",
        build_bundle,
    )

    series_result = MagicMock()
    series_result.scalar_one.return_value = series
    assessment_result = MagicMock()
    assessment_result.scalar_one_or_none.return_value = assessment

    fresh_snapshot = {
        **snapshot,
        "data_categories": [
            {
                "category_code": "EMAIL",
                "category_name": "Correo electrónico",
                "is_sensitive": False,
                "notes": None,
            }
        ],
        "data_subjects": [
            {
                "category_code": "PROVEEDORES",
                "category_name": "Proveedores",
                "includes_children": False,
                "includes_adolescents": False,
                "is_vulnerable_group": False,
                "notes": None,
            }
        ],
    }

    execute_results = iter([series_result, assessment_result])

    async def execute_side_effect(*args, **kwargs):
        result = next(execute_results)
        if result is assessment_result:
            assessment.rat_context_snapshot = fresh_snapshot
        return result

    db = AsyncMock()
    db.execute.side_effect = execute_side_effect

    payload = LegalAssessmentDraftUpdate(
        justification="Justificación actualizada",
    )

    result = await licitud_service.update_legal_assessment_draft_v1(
        db,
        organization_id,
        treatment_id,
        assessment_id,
        profile_id,
        payload,
    )

    assert result is assessment
    assert assessment.version == 2
    assert series.next_version == 3
    assert assessment.justification == "Justificación actualizada"
    assert assessment.updated_by == profile_id
    assert assessment.rat_context_hash == (
        licitud_service.build_rat_context_hash_v1(bundle.canonical)
    )
    assert assessment.rat_context_snapshot == updated_snapshot.model_dump(mode="json")

    build_bundle.assert_awaited_once_with(
        db,
        organization_id,
        treatment_id,
        purpose_key=series.purpose_key,
        scope=LegalAssessmentScopeIn(
            data_category_codes=["EMAIL"],
            data_subject_codes=["PROVEEDORES"],
        ),
    )
    db.flush.assert_awaited_once()
    db.commit.assert_not_awaited()
    db.rollback.assert_not_awaited()


async def test_update_legal_assessment_draft_v1_revalida_estado_despues_del_lock(
    monkeypatch,
):
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    assessment_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    series_id = uuid.uuid4()

    snapshot = {
        "purpose": "Gestión de clientes",
        "organization_role": "responsable",
        "data_categories": [],
        "data_subjects": [],
        "data_sources": [],
        "retention": {
            "retention_rule": None,
            "deletion_method": None,
        },
        "automated_decisions": {
            "has_automated_decisions": False,
            "description": None,
        },
        "systems": [],
        "third_parties": [],
        "international_transfers": [],
        "special_regimes": {
            "has_sensitive_data": False,
            "includes_children": False,
            "includes_adolescents": False,
            "has_vulnerable_groups": False,
        },
    }

    assessment = LegalAssessment(
        id=assessment_id,
        organization_id=organization_id,
        series_id=series_id,
        treatment_id=treatment_id,
        version=1,
        status="borrador",
        purpose_snapshot="Gestión de clientes",
        rat_context_hash="hash",
        rat_context_snapshot=snapshot,
    )
    refreshed_assessment = LegalAssessment(
        id=assessment_id,
        organization_id=organization_id,
        series_id=series_id,
        treatment_id=treatment_id,
        version=1,
        status="confirmado",
        purpose_snapshot="Gestión de clientes",
        rat_context_hash="hash",
        rat_context_snapshot=snapshot,
    )
    series = LegalAssessmentSeries(
        id=series_id,
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose_key=build_purpose_key_v1("Gestión de clientes"),
        purpose_text="Gestión de clientes",
        next_version=2,
    )

    monkeypatch.setattr(
        licitud_service,
        "get_legal_assessment_draft_v1",
        AsyncMock(return_value=assessment),
    )
    build_bundle = AsyncMock()
    monkeypatch.setattr(
        licitud_service,
        "build_rat_context_bundle_from_m2_v1",
        build_bundle,
    )

    series_result = MagicMock()
    series_result.scalar_one.return_value = series
    assessment_result = MagicMock()
    assessment_result.scalar_one_or_none.return_value = refreshed_assessment

    db = AsyncMock()
    db.execute.side_effect = [series_result, assessment_result]

    with pytest.raises(HTTPException) as exc:
        await licitud_service.update_legal_assessment_draft_v1(
            db,
            organization_id,
            treatment_id,
            assessment_id,
            profile_id,
            LegalAssessmentDraftUpdate(justification="No debe persistir"),
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "La evaluación jurídica ya no está en estado borrador"
    build_bundle.assert_not_awaited()
    db.flush.assert_not_awaited()


async def test_update_legal_assessment_draft_v1_usa_scope_nuevo(
    monkeypatch,
):
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    assessment_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    series_id = uuid.uuid4()

    old_snapshot = {
        "purpose": "Gestión de clientes",
        "organization_role": "responsable",
        "data_categories": [],
        "data_subjects": [],
        "data_sources": [],
        "retention": {
            "retention_rule": None,
            "deletion_method": None,
        },
        "automated_decisions": {
            "has_automated_decisions": False,
            "description": None,
        },
        "systems": [],
        "third_parties": [],
        "international_transfers": [],
        "special_regimes": {
            "has_sensitive_data": False,
            "includes_children": False,
            "includes_adolescents": False,
            "has_vulnerable_groups": False,
        },
    }
    assessment = LegalAssessment(
        id=assessment_id,
        organization_id=organization_id,
        series_id=series_id,
        treatment_id=treatment_id,
        version=1,
        status="borrador",
        purpose_snapshot="Gestión de clientes",
        rat_context_hash="hash",
        rat_context_snapshot=old_snapshot,
    )
    series = LegalAssessmentSeries(
        id=series_id,
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose_key=build_purpose_key_v1("Gestión de clientes"),
        purpose_text="Gestión de clientes",
        next_version=2,
    )

    monkeypatch.setattr(
        licitud_service,
        "get_legal_assessment_draft_v1",
        AsyncMock(return_value=assessment),
    )

    bundle = licitud_service.RatContextBundleV1(
        canonical=_context_m3([], []),
        snapshot=licitud_service.RatContextSnapshotV1.model_validate(old_snapshot),
    )
    build_bundle = AsyncMock(return_value=bundle)
    monkeypatch.setattr(
        licitud_service,
        "build_rat_context_bundle_from_m2_v1",
        build_bundle,
    )

    series_result = MagicMock()
    series_result.scalar_one.return_value = series
    assessment_result = MagicMock()
    assessment_result.scalar_one_or_none.return_value = assessment
    db = AsyncMock()
    db.execute.side_effect = [series_result, assessment_result]

    new_scope = LegalAssessmentScopeIn(
        data_category_codes=["salud"],
        data_subject_codes=["clientes"],
    )
    payload = LegalAssessmentDraftUpdate(scope=new_scope)

    await licitud_service.update_legal_assessment_draft_v1(
        db,
        organization_id,
        treatment_id,
        assessment_id,
        profile_id,
        payload,
    )

    build_bundle.assert_awaited_once_with(
        db,
        organization_id,
        treatment_id,
        purpose_key=series.purpose_key,
        scope=new_scope,
    )
    assert series.next_version == 2


async def test_get_legal_assessment_draft_v1_devuelve_borrador_tenant_aware():
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    assessment_id = uuid.uuid4()

    assessment = LegalAssessment(
        id=assessment_id,
        organization_id=organization_id,
        series_id=uuid.uuid4(),
        treatment_id=treatment_id,
        version=1,
        status="borrador",
        purpose_snapshot="Gestión de clientes",
        rat_context_hash="hash",
        rat_context_snapshot={},
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = assessment
    db = AsyncMock()
    db.execute.return_value = result

    resolved = await licitud_service.get_legal_assessment_draft_v1(
        db,
        organization_id,
        treatment_id,
        assessment_id,
    )

    assert resolved is assessment
    db.execute.assert_awaited_once()
    params = db.execute.call_args.args[0].compile().params
    assert organization_id in params.values()
    assert treatment_id in params.values()
    assert assessment_id in params.values()


async def test_get_legal_assessment_draft_v1_rechaza_inexistente():
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(HTTPException) as exc:
        await licitud_service.get_legal_assessment_draft_v1(
            db,
            uuid.uuid4(),
            uuid.uuid4(),
            uuid.uuid4(),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Evaluación jurídica no encontrada"


async def test_get_legal_assessment_draft_v1_rechaza_no_borrador():
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()

    assessment = LegalAssessment(
        id=uuid.uuid4(),
        organization_id=organization_id,
        series_id=uuid.uuid4(),
        treatment_id=treatment_id,
        version=1,
        status="confirmado",
        purpose_snapshot="Gestión de clientes",
        rat_context_hash="hash",
        rat_context_snapshot={},
        confirmed_at=datetime.now(UTC),
        confirmed_by=uuid.uuid4(),
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = assessment
    db = AsyncMock()
    db.execute.return_value = result

    with pytest.raises(HTTPException) as exc:
        await licitud_service.get_legal_assessment_draft_v1(
            db,
            organization_id,
            treatment_id,
            assessment.id,
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == ("La evaluación jurídica ya no está en estado borrador")


async def test_create_legal_assessment_draft_v1_rechaza_segundo_borrador(
    monkeypatch,
):
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    purpose_id = uuid.uuid4()

    purpose = TreatmentPurpose(
        id=purpose_id,
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose="Gestión de clientes",
    )
    treatment = Treatment(
        id=treatment_id,
        organization_id=organization_id,
        organization_role="responsable",
        retention_rule=None,
        deletion_method=None,
        has_automated_decisions=False,
        automated_decision_description=None,
    )
    snapshot = licitud_service.build_rat_context_snapshot_v1(
        treatment=treatment,
        purpose=purpose,
        data_categories=[],
        data_subjects=[],
        data_sources=[],
        systems=[],
        relationships=[],
        vendors_by_id={},
        international_transfers=[],
    )
    bundle = licitud_service.RatContextBundleV1(
        canonical=_context_m3([], []),
        snapshot=snapshot,
    )
    series = LegalAssessmentSeries(
        id=uuid.uuid4(),
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose_key=build_purpose_key_v1(purpose.purpose),
        purpose_text=purpose.purpose,
        next_version=4,
    )
    existing_draft = LegalAssessment(
        id=uuid.uuid4(),
        organization_id=organization_id,
        series_id=series.id,
        treatment_id=treatment_id,
        version=3,
        status="borrador",
        purpose_snapshot=purpose.purpose,
        rat_context_hash="hash-existente",
        rat_context_snapshot={},
    )

    monkeypatch.setattr(
        licitud_service,
        "resolve_purpose_by_id_from_m2_v1",
        AsyncMock(return_value=purpose),
    )
    monkeypatch.setattr(
        licitud_service,
        "build_rat_context_bundle_from_m2_v1",
        AsyncMock(return_value=bundle),
    )
    monkeypatch.setattr(
        licitud_service,
        "_get_or_create_series_for_update_v1",
        AsyncMock(return_value=series),
    )

    draft_result = MagicMock()
    draft_result.scalar_one_or_none.return_value = existing_draft

    db = AsyncMock()
    db.execute.return_value = draft_result
    db.add = MagicMock()

    payload = LegalAssessmentDraftCreate(
        purpose_id=purpose_id,
        scope=LegalAssessmentScopeIn(),
    )

    with pytest.raises(HTTPException) as exc:
        await licitud_service.create_legal_assessment_draft_v1(
            db,
            organization_id,
            treatment_id,
            profile_id,
            payload,
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "Ya existe un borrador para esta finalidad"
    assert series.next_version == 4
    db.add.assert_not_called()
    db.flush.assert_not_awaited()
    db.commit.assert_not_awaited()
    db.rollback.assert_not_awaited()


async def test_create_legal_assessment_draft_v1_persiste_contexto_y_reserva_version(
    monkeypatch,
):
    organization_id = uuid.uuid4()
    treatment_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    purpose_id = uuid.uuid4()
    series_id = uuid.uuid4()

    purpose = TreatmentPurpose(
        id=purpose_id,
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose=" Gestión de clientes ",
    )
    treatment = Treatment(
        id=treatment_id,
        organization_id=organization_id,
        organization_role="responsable",
        retention_rule=None,
        deletion_method=None,
        has_automated_decisions=False,
        automated_decision_description=None,
    )
    snapshot = licitud_service.build_rat_context_snapshot_v1(
        treatment=treatment,
        purpose=purpose,
        data_categories=[],
        data_subjects=[],
        data_sources=[],
        systems=[],
        relationships=[],
        vendors_by_id={},
        international_transfers=[],
    )
    bundle = licitud_service.RatContextBundleV1(
        canonical=_context_m3([], []),
        snapshot=snapshot,
    )
    series = LegalAssessmentSeries(
        id=series_id,
        organization_id=organization_id,
        treatment_id=treatment_id,
        purpose_key=build_purpose_key_v1(purpose.purpose),
        purpose_text=purpose.purpose,
        next_version=2,
    )

    resolve_purpose = AsyncMock(return_value=purpose)
    build_bundle = AsyncMock(return_value=bundle)
    get_series = AsyncMock(return_value=series)
    monkeypatch.setattr(
        licitud_service,
        "resolve_purpose_by_id_from_m2_v1",
        resolve_purpose,
    )
    monkeypatch.setattr(
        licitud_service,
        "build_rat_context_bundle_from_m2_v1",
        build_bundle,
    )
    monkeypatch.setattr(
        licitud_service,
        "_get_or_create_series_for_update_v1",
        get_series,
    )

    no_draft_result = MagicMock()
    no_draft_result.scalar_one_or_none.return_value = None

    db = AsyncMock()
    db.execute.return_value = no_draft_result
    db.add = MagicMock()

    payload = LegalAssessmentDraftCreate(
        purpose_id=purpose_id,
        scope=LegalAssessmentScopeIn(),
        legal_basis="contrato_precontractual_art13c",
        justification="Necesario para la relación contractual.",
    )

    assessment = await licitud_service.create_legal_assessment_draft_v1(
        db,
        organization_id,
        treatment_id,
        profile_id,
        payload,
    )

    assert isinstance(assessment, LegalAssessment)
    assert assessment.organization_id == organization_id
    assert assessment.treatment_id == treatment_id
    assert assessment.series_id == series_id
    assert assessment.version == 2
    assert assessment.status == "borrador"
    assert assessment.legal_basis == "contrato_precontractual_art13c"
    assert assessment.justification == "Necesario para la relación contractual."
    assert assessment.purpose_snapshot == " Gestión de clientes "
    assert assessment.rat_context_hash == (
        licitud_service.build_rat_context_hash_v1(bundle.canonical)
    )
    assert assessment.rat_context_snapshot == snapshot.model_dump(mode="json")
    assert assessment.schema_version == 1
    assert assessment.rat_context_schema_version == 1
    assert assessment.created_by == profile_id
    assert assessment.updated_by == profile_id

    assert series.next_version == 3
    assert series.updated_by == profile_id
    assert series.updated_at is not None

    resolve_purpose.assert_awaited_once_with(
        db,
        organization_id,
        treatment_id,
        purpose_id,
    )
    build_bundle.assert_awaited_once_with(
        db,
        organization_id,
        treatment_id,
        purpose_key=build_purpose_key_v1(purpose.purpose),
        scope=payload.scope,
    )
    get_series.assert_awaited_once_with(
        db,
        organization_id,
        treatment_id,
        purpose,
        profile_id,
    )
    db.add.assert_called_once_with(assessment)
    db.flush.assert_awaited_once()
    db.commit.assert_not_awaited()
    db.rollback.assert_not_awaited()


async def test_m2_composicion_propaga_tenant_y_seleccion(m2_context_reader):
    org_id, treatment_id, readers = m2_context_reader
    db = AsyncMock()
    vendor_id = uuid.uuid4()
    transfer_vendor_id = uuid.uuid4()
    readers["listar_vendors_tratamiento"].return_value = [
        TreatmentVendor(
            organization_id=org_id,
            treatment_id=treatment_id,
            vendor_id=vendor_id,
            relationship_type="encargado",
            has_data_access=True,
            has_contract=False,
            has_subprocessors=False,
            purpose=" Hosting ",
        )
    ]
    vendor_result = MagicMock()
    readers["listar_transferencias"].return_value = [
        InternationalTransfer(
            organization_id=org_id,
            treatment_id=treatment_id,
            vendor_id=transfer_vendor_id,
            recipient_name=None,
            destination_country=" España ",
            adequacy_status="pendiente",
        )
    ]
    vendor_result.scalars.return_value.all.return_value = [
        Vendor(
            id=vendor_id,
            organization_id=org_id,
            country=" Chile ",
            name="Proveedor",
        ),
        Vendor(
            id=transfer_vendor_id,
            organization_id=org_id,
            country=" España ",
            name="Destinatario por vendor",
        ),
    ]
    db.execute.return_value = vendor_result
    result = await licitud_service.build_rat_context_from_m2_v1(
        db,
        org_id,
        treatment_id,
        purpose_key=build_purpose_key_v1("gestión de clientes"),
        scope=LegalAssessmentScopeIn(
            data_category_codes=[" id "], data_subject_codes=["clientes"]
        ),
    )
    for reader in readers.values():
        reader.assert_awaited_once_with(db, org_id, treatment_id)
    vendor_query = db.execute.call_args.args[0].compile().params
    assert org_id in vendor_query.values()
    loaded_vendor_ids = next(
        value for value in vendor_query.values() if isinstance(value, list)
    )
    assert set(loaded_vendor_ids) == {vendor_id, transfer_vendor_id}
    assert result.purpose == "gestión de clientes"
    assert [item.category_code for item in result.data_categories] == ["id"]
    assert [item.category_code for item in result.data_subjects] == ["clientes"]
    assert not any(result.special_regimes.model_dump().values())
    assert result.retention.retention_rule == "cinco años"
    assert result.automated_decisions.description is None
    assert result.systems == []
    assert result.data_sources[0].description == "formulario web"
    assert result.third_parties[0].country == "chile"
    assert result.international_transfers[0].destination_country == "españa"
    db.commit.assert_not_awaited()
    db.flush.assert_not_awaited()


async def test_m2_composicion_bundle_reutiliza_misma_lectura_para_canonico_y_snapshot(
    m2_context_reader,
):
    org_id, treatment_id, readers = m2_context_reader
    db = AsyncMock()
    vendor_id = uuid.uuid4()

    readers["listar_sistemas_tratamiento"].return_value = [
        System(
            organization_id=org_id,
            name=" CRM Principal ",
            provider=" Proveedor Sistema ",
            hosting_location=" Santiago ",
            hosting_country=" Chile ",
            is_international=False,
        )
    ]
    readers["listar_transferencias"].return_value = [
        InternationalTransfer(
            organization_id=org_id,
            treatment_id=treatment_id,
            vendor_id=vendor_id,
            recipient_name=None,
            destination_country=" España ",
            adequacy_status="pendiente",
        )
    ]

    vendor_result = MagicMock()
    vendor_result.scalars.return_value.all.return_value = [
        Vendor(
            id=vendor_id,
            organization_id=org_id,
            country=" España ",
            name="Destinatario documental",
        )
    ]
    db.execute.return_value = vendor_result

    bundle = await licitud_service.build_rat_context_bundle_from_m2_v1(
        db,
        org_id,
        treatment_id,
        purpose_key=build_purpose_key_v1("gestión de clientes"),
        scope=LegalAssessmentScopeIn(
            data_category_codes=[" id "],
            data_subject_codes=["clientes"],
        ),
    )

    for reader in readers.values():
        reader.assert_awaited_once_with(db, org_id, treatment_id)

    assert bundle.canonical.purpose == "gestión de clientes"
    assert bundle.canonical.systems == []
    assert bundle.canonical.international_transfers[0].destination_country == "españa"

    assert bundle.snapshot.purpose == " Gestión de clientes "
    assert bundle.snapshot.systems[0].name == " CRM Principal "
    assert bundle.snapshot.systems[0].provider == " Proveedor Sistema "
    assert bundle.snapshot.international_transfers[0].destination_country == " España "
    assert (
        bundle.snapshot.international_transfers[0].recipient_name
        == "Destinatario documental"
    )

    db.commit.assert_not_awaited()
    db.flush.assert_not_awaited()


async def test_m2_composicion_no_lee_hijos_de_tratamiento_ajeno(m2_context_reader):
    org_id, treatment_id, readers = m2_context_reader
    readers["obtener_tratamiento"].side_effect = HTTPException(
        404, "Actividad de tratamiento no encontrada"
    )
    db = AsyncMock()
    with pytest.raises(HTTPException) as exc:
        await licitud_service.build_rat_context_from_m2_v1(
            db,
            org_id,
            treatment_id,
            purpose_key=build_purpose_key_v1("Clientes"),
            scope=LegalAssessmentScopeIn(),
        )
    assert exc.value.status_code == 404
    for name, reader in readers.items():
        if name != "obtener_tratamiento":
            reader.assert_not_awaited()
    db.execute.assert_not_awaited()


@pytest.mark.parametrize(
    "scope",
    [
        LegalAssessmentScopeIn(data_category_codes=["inexistente"]),
        LegalAssessmentScopeIn(data_subject_codes=["inexistente"]),
        LegalAssessmentScopeIn(data_category_codes=["ID", " id "]),
    ],
)
async def test_m2_composicion_rechaza_alcance_invalido(m2_context_reader, scope):
    org_id, treatment_id, readers = m2_context_reader
    with pytest.raises(HTTPException) as exc:
        await licitud_service.build_rat_context_from_m2_v1(
            AsyncMock(),
            org_id,
            treatment_id,
            purpose_key=build_purpose_key_v1("Gestión de clientes"),
            scope=scope,
        )
    assert exc.value.status_code == 400
    readers["listar_fuentes_datos"].assert_not_awaited()


@pytest.mark.parametrize("name", ["listar_fuentes_datos", "listar_transferencias"])
async def test_m2_composicion_no_oculta_error_de_lectura(m2_context_reader, name):
    org_id, treatment_id, readers = m2_context_reader
    readers[name].side_effect = HTTPException(
        404, "Actividad de tratamiento no encontrada"
    )
    with pytest.raises(HTTPException) as exc:
        await licitud_service.build_rat_context_from_m2_v1(
            AsyncMock(),
            org_id,
            treatment_id,
            purpose_key=build_purpose_key_v1("Gestión de clientes"),
            scope=LegalAssessmentScopeIn(),
        )
    assert exc.value.status_code == 404


async def test_m2_composicion_consultas_reales_acotan_tenant_y_tratamiento():
    org_id, treatment_id = uuid.uuid4(), uuid.uuid4()
    treatment = Treatment(
        id=treatment_id,
        organization_id=org_id,
        organization_role=None,
        retention_rule=None,
        has_automated_decisions=False,
    )
    purpose = TreatmentPurpose(
        organization_id=org_id,
        treatment_id=treatment_id,
        purpose="Clientes",
    )
    seen = []

    async def execute(statement):
        model = statement.column_descriptions[0]["entity"]
        params = statement.compile().params
        assert params["organization_id_1"] == org_id
        if model is Treatment:
            assert params["id_1"] == treatment_id
        else:
            assert params["treatment_id_1"] == treatment_id
        seen.append(model)
        result = MagicMock()
        result.scalar_one_or_none.return_value = treatment
        result.scalars.return_value.all.return_value = (
            [purpose] if model is TreatmentPurpose else []
        )
        return result

    db = AsyncMock()
    db.execute.side_effect = execute
    context = await licitud_service.build_rat_context_from_m2_v1(
        db,
        org_id,
        treatment_id,
        purpose_key=build_purpose_key_v1("Clientes"),
        scope=LegalAssessmentScopeIn(),
    )
    assert TreatmentDataSource in seen
    assert InternationalTransfer in seen
    assert TreatmentVendor in seen
    assert context.data_sources == []
    assert context.international_transfers == []
    assert context.third_parties == []
    assert context.data_categories == []
    assert context.data_subjects == []
    assert not any(context.special_regimes.model_dump().values())


async def test_m2_composicion_consulta_real_rechaza_tratamiento_ajeno():
    org_id, treatment_id = uuid.uuid4(), uuid.uuid4()
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    with pytest.raises(HTTPException) as exc:
        await licitud_service.build_rat_context_from_m2_v1(
            db,
            org_id,
            treatment_id,
            purpose_key=build_purpose_key_v1("Clientes"),
            scope=LegalAssessmentScopeIn(),
        )
    assert exc.value.status_code == 404
    db.execute.assert_awaited_once()
    params = db.execute.call_args.args[0].compile().params
    assert params["organization_id_1"] == org_id
    assert params["id_1"] == treatment_id
