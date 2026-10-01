"""Servicios del Módulo 3 — Bases de Licitud."""

import hashlib
import json
import unicodedata
import uuid
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    InternationalTransfer,
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
    LegalAssessmentScopeIn,
    RatCanonicalAutomatedDecisionsV1,
    RatCanonicalContextV1,
    RatCanonicalDataCategoryV1,
    RatCanonicalDataSourceV1,
    RatCanonicalDataSubjectV1,
    RatCanonicalInternationalTransferV1,
    RatCanonicalRetentionV1,
    RatCanonicalSpecialRegimesV1,
    RatCanonicalThirdPartyV1,
    RatContextSnapshotV1,
    RatSnapshotAutomatedDecisionsV1,
    RatSnapshotDataCategoryV1,
    RatSnapshotDataSourceV1,
    RatSnapshotDataSubjectV1,
    RatSnapshotInternationalTransferV1,
    RatSnapshotRetentionV1,
    RatSnapshotSpecialRegimesV1,
    RatSnapshotSystemV1,
    RatSnapshotThirdPartyV1,
)
from app.services import rat as rat_service


@dataclass(frozen=True)
class RatContextBundleV1:
    """Contexto RAT v1 derivado de una misma composición lógica M2."""

    canonical: RatCanonicalContextV1
    snapshot: RatContextSnapshotV1


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def canonicalize_text_v1(value: str) -> str:
    """Canoniza texto jurídicamente relevante según el contrato M3 v1."""

    normalized = unicodedata.normalize("NFC", value)
    return " ".join(normalized.strip().casefold().split())


def build_purpose_key_v1(purpose_text: str) -> str:
    """Deriva la identidad lógica v1 de una finalidad mediante SHA-256."""

    canonical_text = canonicalize_text_v1(purpose_text)
    return hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()


def canonicalize_optional_text_v1(value: str | None) -> str | None:
    """Canoniza texto opcional; vacío o solo whitespace se representa como None."""

    if value is None:
        return None

    canonical_text = canonicalize_text_v1(value)
    return canonical_text or None


def _documentary_optional_text_sort_key_v1(
    value: str | None,
) -> tuple[int, str]:
    """Clave de orden documental: preserva el valor factual sin canonizar."""
    return (0, "") if value is None else (1, value)


def canonicalize_data_categories_v1(
    items: list[RatCanonicalDataCategoryV1],
) -> list[RatCanonicalDataCategoryV1]:
    """Canoniza y ordena categorías de datos según el contrato RAT v1."""

    canonical_items = [
        RatCanonicalDataCategoryV1(
            category_code=canonicalize_text_v1(item.category_code),
            category_name=canonicalize_text_v1(item.category_name),
            is_sensitive=item.is_sensitive,
        )
        for item in items
    ]

    return sorted(
        canonical_items,
        key=lambda item: (
            item.category_code,
            item.category_name,
            item.is_sensitive,
        ),
    )


def canonicalize_data_subjects_v1(
    items: list[RatCanonicalDataSubjectV1],
) -> list[RatCanonicalDataSubjectV1]:
    """Canoniza y ordena titulares de datos según el contrato RAT v1."""

    canonical_items = [
        RatCanonicalDataSubjectV1(
            category_code=canonicalize_text_v1(item.category_code),
            category_name=canonicalize_text_v1(item.category_name),
            includes_children=item.includes_children,
            includes_adolescents=item.includes_adolescents,
            is_vulnerable_group=item.is_vulnerable_group,
        )
        for item in items
    ]

    return sorted(
        canonical_items,
        key=lambda item: (
            item.category_code,
            item.category_name,
            item.includes_children,
            item.includes_adolescents,
            item.is_vulnerable_group,
        ),
    )


def canonicalize_data_sources_v1(
    items: list[RatCanonicalDataSourceV1],
) -> list[RatCanonicalDataSourceV1]:
    """Canoniza y ordena fuentes de datos según el contrato RAT v1."""

    canonical_items = [
        RatCanonicalDataSourceV1(
            source_type=item.source_type,
            description=canonicalize_optional_text_v1(item.description),
            is_public_source=item.is_public_source,
        )
        for item in items
    ]

    return sorted(
        canonical_items,
        key=lambda item: (
            item.source_type,
            (0, "") if item.description is None else (1, item.description),
            item.is_public_source,
        ),
    )


def canonicalize_third_parties_v1(
    items: list[RatCanonicalThirdPartyV1],
) -> list[RatCanonicalThirdPartyV1]:
    """Canoniza y ordena terceros según el contrato RAT v1."""

    canonical_items = [
        RatCanonicalThirdPartyV1(
            relationship_type=item.relationship_type,
            has_data_access=item.has_data_access,
            country=canonicalize_optional_text_v1(item.country),
            has_subprocessors=item.has_subprocessors,
            purpose=canonicalize_optional_text_v1(item.purpose),
        )
        for item in items
    ]

    return sorted(
        canonical_items,
        key=lambda item: (
            item.relationship_type,
            item.has_data_access,
            (0, "") if item.country is None else (1, item.country),
            item.has_subprocessors,
            (0, "") if item.purpose is None else (1, item.purpose),
        ),
    )


def canonicalize_international_transfers_v1(
    items: list[RatCanonicalInternationalTransferV1],
) -> list[RatCanonicalInternationalTransferV1]:
    """Canoniza y ordena transferencias internacionales según el contrato RAT v1."""

    canonical_items = [
        RatCanonicalInternationalTransferV1(
            destination_country=canonicalize_text_v1(item.destination_country),
            adequacy_status=item.adequacy_status,
            mechanism=canonicalize_optional_text_v1(item.mechanism),
            guarantees_description=canonicalize_optional_text_v1(
                item.guarantees_description
            ),
        )
        for item in items
    ]

    return sorted(
        canonical_items,
        key=lambda item: (
            item.destination_country,
            item.adequacy_status,
            (0, "") if item.mechanism is None else (1, item.mechanism),
            (
                (0, "")
                if item.guarantees_description is None
                else (1, item.guarantees_description)
            ),
        ),
    )


def derive_special_regimes_v1(
    data_categories: list[RatCanonicalDataCategoryV1],
    data_subjects: list[RatCanonicalDataSubjectV1],
) -> RatCanonicalSpecialRegimesV1:
    """Deriva regímenes especiales exclusivamente desde el alcance RAT seleccionado."""

    return RatCanonicalSpecialRegimesV1(
        has_sensitive_data=any(item.is_sensitive for item in data_categories),
        includes_children=any(item.includes_children for item in data_subjects),
        includes_adolescents=any(item.includes_adolescents for item in data_subjects),
        has_vulnerable_groups=any(item.is_vulnerable_group for item in data_subjects),
    )


def build_rat_canonical_context_v1(
    *,
    purpose: str,
    organization_role: str | None,
    data_categories: list[RatCanonicalDataCategoryV1],
    data_subjects: list[RatCanonicalDataSubjectV1],
    data_sources: list[RatCanonicalDataSourceV1],
    retention_rule: str | None,
    has_automated_decisions: bool,
    automated_decision_description: str | None,
    third_parties: list[RatCanonicalThirdPartyV1],
    international_transfers: list[RatCanonicalInternationalTransferV1],
) -> RatCanonicalContextV1:
    """Construye el objeto canónico RAT v1 a partir de hechos semánticos M2."""

    canonical_categories = canonicalize_data_categories_v1(data_categories)
    canonical_subjects = canonicalize_data_subjects_v1(data_subjects)

    return RatCanonicalContextV1(
        purpose=canonicalize_text_v1(purpose),
        organization_role=organization_role,
        data_categories=canonical_categories,
        data_subjects=canonical_subjects,
        data_sources=canonicalize_data_sources_v1(data_sources),
        retention=RatCanonicalRetentionV1(
            retention_rule=canonicalize_optional_text_v1(retention_rule),
        ),
        automated_decisions=RatCanonicalAutomatedDecisionsV1(
            has_automated_decisions=has_automated_decisions,
            description=(
                canonicalize_optional_text_v1(automated_decision_description)
                if has_automated_decisions
                else None
            ),
        ),
        systems=[],
        third_parties=canonicalize_third_parties_v1(third_parties),
        international_transfers=canonicalize_international_transfers_v1(
            international_transfers
        ),
        special_regimes=derive_special_regimes_v1(
            canonical_categories,
            canonical_subjects,
        ),
    )


def serialize_rat_canonical_context_v1(
    context: RatCanonicalContextV1,
) -> bytes:
    """Serializa el contexto RAT v1 a su representación JSON canónica UTF-8."""

    serialized = json.dumps(
        context.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return serialized.encode("utf-8")


def build_rat_context_hash_v1(
    context: RatCanonicalContextV1,
) -> str:
    """Calcula SHA-256 sobre los bytes exactos del contexto RAT canónico v1."""

    canonical_bytes = serialize_rat_canonical_context_v1(context)
    return hashlib.sha256(canonical_bytes).hexdigest()


async def _load_vendors_by_id(
    db: AsyncSession,
    organization_id: uuid.UUID,
    vendor_ids: set[uuid.UUID],
) -> dict[uuid.UUID, Vendor]:
    """Carga vendors del tenant en una sola consulta, indexados por UUID."""
    if not vendor_ids:
        return {}

    result = await db.execute(
        select(Vendor).where(
            Vendor.organization_id == organization_id,
            Vendor.id.in_(vendor_ids),
        )
    )
    vendors = list(result.scalars().all())
    return {vendor.id: vendor for vendor in vendors}


def _build_third_parties_from_vendor_map_v1(
    relationships: list[TreatmentVendor],
    vendors_by_id: dict[uuid.UUID, Vendor],
) -> list[RatCanonicalThirdPartyV1]:
    """Proyecta relaciones M2 usando vendors ya cargados del mismo tenant."""
    vendor_ids = {relationship.vendor_id for relationship in relationships}
    missing_vendor_ids = vendor_ids - set(vendors_by_id)
    if missing_vendor_ids:
        raise _bad_request(
            "Uno o más proveedores asociados no pertenecen a la organización"
        )

    items = [
        RatCanonicalThirdPartyV1(
            relationship_type=relationship.relationship_type,
            has_data_access=relationship.has_data_access,
            country=vendors_by_id[relationship.vendor_id].country,
            has_subprocessors=relationship.has_subprocessors,
            purpose=relationship.purpose,
        )
        for relationship in relationships
    ]

    return canonicalize_third_parties_v1(items)


async def build_third_parties_from_m2_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    relationships: list[TreatmentVendor],
) -> list[RatCanonicalThirdPartyV1]:
    """Proyecta relaciones M2 de terceros al contrato canónico RAT v1."""
    vendor_ids = {relationship.vendor_id for relationship in relationships}
    vendors_by_id = await _load_vendors_by_id(
        db,
        organization_id,
        vendor_ids,
    )
    return _build_third_parties_from_vendor_map_v1(
        relationships,
        vendors_by_id,
    )


def resolve_purpose_from_m2_v1(
    purposes: list,
    purpose_key: str,
):
    """Resuelve una finalidad M2 por su identidad lógica canónica v1."""
    matches = [
        purpose
        for purpose in purposes
        if build_purpose_key_v1(purpose.purpose) == purpose_key
    ]

    if not matches:
        raise _bad_request(
            "La finalidad indicada no pertenece a la actividad de tratamiento"
        )

    if len(matches) > 1:
        raise _bad_request("El RAT contiene finalidades canónicamente ambiguas")

    return matches[0]


def resolve_data_categories_from_m2_v1(
    categories: list[TreatmentDataCategory],
    selected_codes: list[str],
) -> list[TreatmentDataCategory]:
    """Resuelve categorías M2 seleccionadas mediante category_code canónico v1."""
    requested_codes = [canonicalize_text_v1(code) for code in selected_codes]

    if len(requested_codes) != len(set(requested_codes)):
        raise _bad_request(
            "data_category_codes contiene códigos canónicamente duplicados"
        )

    categories_by_code: dict[str, list[TreatmentDataCategory]] = {}
    for category in categories:
        canonical_code = canonicalize_text_v1(category.category_code)
        categories_by_code.setdefault(canonical_code, []).append(category)

    ambiguous_codes = {
        code for code, matches in categories_by_code.items() if len(matches) > 1
    }
    if ambiguous_codes:
        raise _bad_request("El RAT contiene categorías de datos canónicamente ambiguas")

    missing_codes = {code for code in requested_codes if code not in categories_by_code}
    if missing_codes:
        raise _bad_request(
            "Una o más categorías de datos seleccionadas no pertenecen "
            "a la actividad de tratamiento"
        )

    return [categories_by_code[code][0] for code in requested_codes]


def resolve_data_subjects_from_m2_v1(
    subjects: list[TreatmentDataSubject],
    selected_codes: list[str],
) -> list[TreatmentDataSubject]:
    """Resuelve titulares M2 seleccionados mediante category_code canónico v1."""
    requested_codes = [canonicalize_text_v1(code) for code in selected_codes]

    if len(requested_codes) != len(set(requested_codes)):
        raise _bad_request(
            "data_subject_codes contiene códigos canónicamente duplicados"
        )

    subjects_by_code: dict[str, list[TreatmentDataSubject]] = {}
    for subject in subjects:
        canonical_code = canonicalize_text_v1(subject.category_code)
        subjects_by_code.setdefault(canonical_code, []).append(subject)

    ambiguous_codes = {
        code for code, matches in subjects_by_code.items() if len(matches) > 1
    }
    if ambiguous_codes:
        raise _bad_request("El RAT contiene titulares de datos canónicamente ambiguos")

    missing_codes = {code for code in requested_codes if code not in subjects_by_code}
    if missing_codes:
        raise _bad_request(
            "Uno o más titulares de datos seleccionados no pertenecen "
            "a la actividad de tratamiento"
        )

    return [subjects_by_code[code][0] for code in requested_codes]


def build_data_sources_from_m2_v1(
    sources: list[TreatmentDataSource],
) -> list[RatCanonicalDataSourceV1]:
    """Proyecta fuentes M2 sin identidad técnica y conserva multiplicidad."""
    return canonicalize_data_sources_v1(
        [
            RatCanonicalDataSourceV1(
                source_type=source.source_type,
                description=source.description,
                is_public_source=source.is_public_source,
            )
            for source in sources
        ]
    )


def build_international_transfers_from_m2_v1(
    transfers: list[InternationalTransfer],
) -> list[RatCanonicalInternationalTransferV1]:
    """Proyecta hechos estructurados M2, sin inferirlos desde el proveedor."""
    items = []
    for transfer in transfers:
        if not canonicalize_text_v1(transfer.destination_country):
            raise _bad_request("El RAT contiene una transferencia sin país de destino")
        items.append(
            RatCanonicalInternationalTransferV1(
                destination_country=transfer.destination_country,
                adequacy_status=transfer.adequacy_status,
                mechanism=transfer.mechanism,
                guarantees_description=transfer.guarantees_description,
            )
        )
    return canonicalize_international_transfers_v1(items)


def build_rat_context_snapshot_v1(
    *,
    treatment: Treatment,
    purpose: TreatmentPurpose,
    data_categories: list[TreatmentDataCategory],
    data_subjects: list[TreatmentDataSubject],
    data_sources: list[TreatmentDataSource],
    systems: list[System],
    relationships: list[TreatmentVendor],
    vendors_by_id: dict[uuid.UUID, Vendor],
    international_transfers: list[InternationalTransfer],
) -> RatContextSnapshotV1:
    """Construye el snapshot documental RAT v1 desde hechos M2 ya cargados."""
    relationship_vendor_ids = {item.vendor_id for item in relationships}
    missing_vendor_ids = relationship_vendor_ids - set(vendors_by_id)
    if missing_vendor_ids:
        raise _bad_request(
            "Uno o más proveedores asociados no pertenecen a la organización"
        )

    canonical_categories = canonicalize_data_categories_v1(
        [
            RatCanonicalDataCategoryV1(
                category_code=item.category_code,
                category_name=item.category_name,
                is_sensitive=item.is_sensitive,
            )
            for item in data_categories
        ]
    )
    canonical_subjects = canonicalize_data_subjects_v1(
        [
            RatCanonicalDataSubjectV1(
                category_code=item.category_code,
                category_name=item.category_name,
                includes_children=item.includes_children,
                includes_adolescents=item.includes_adolescents,
                is_vulnerable_group=item.is_vulnerable_group,
            )
            for item in data_subjects
        ]
    )
    special_regimes = derive_special_regimes_v1(
        canonical_categories,
        canonical_subjects,
    )

    snapshot_categories = [
        RatSnapshotDataCategoryV1(
            category_code=item.category_code,
            category_name=item.category_name,
            is_sensitive=item.is_sensitive,
            notes=item.notes,
        )
        for item in data_categories
    ]
    snapshot_categories.sort(
        key=lambda item: (
            item.category_code,
            item.category_name,
            item.is_sensitive,
            _documentary_optional_text_sort_key_v1(item.notes),
        )
    )

    snapshot_subjects = [
        RatSnapshotDataSubjectV1(
            category_code=item.category_code,
            category_name=item.category_name,
            includes_children=item.includes_children,
            includes_adolescents=item.includes_adolescents,
            is_vulnerable_group=item.is_vulnerable_group,
            notes=item.notes,
        )
        for item in data_subjects
    ]
    snapshot_subjects.sort(
        key=lambda item: (
            item.category_code,
            item.category_name,
            item.includes_children,
            item.includes_adolescents,
            item.is_vulnerable_group,
            _documentary_optional_text_sort_key_v1(item.notes),
        )
    )

    snapshot_sources = [
        RatSnapshotDataSourceV1(
            source_type=item.source_type,
            description=item.description,
            is_public_source=item.is_public_source,
        )
        for item in data_sources
    ]
    snapshot_sources.sort(
        key=lambda item: (
            item.source_type,
            _documentary_optional_text_sort_key_v1(item.description),
            item.is_public_source,
        )
    )

    snapshot_systems = [
        RatSnapshotSystemV1(
            name=item.name,
            provider=item.provider,
            hosting_location=item.hosting_location,
            hosting_country=item.hosting_country,
            is_international=item.is_international,
        )
        for item in systems
    ]
    snapshot_systems.sort(
        key=lambda item: (
            item.name,
            _documentary_optional_text_sort_key_v1(item.provider),
            _documentary_optional_text_sort_key_v1(item.hosting_location),
            _documentary_optional_text_sort_key_v1(item.hosting_country),
            item.is_international,
        )
    )

    snapshot_third_parties = []
    for relationship in relationships:
        vendor = vendors_by_id[relationship.vendor_id]
        snapshot_third_parties.append(
            RatSnapshotThirdPartyV1(
                vendor_name=vendor.name,
                country=vendor.country,
                relationship_type=relationship.relationship_type,
                purpose=relationship.purpose,
                has_data_access=relationship.has_data_access,
                has_contract=relationship.has_contract,
                contract_reference=relationship.contract_reference,
                engagement_object=relationship.engagement_object,
                engagement_duration=relationship.engagement_duration,
                has_subprocessors=relationship.has_subprocessors,
                notes=relationship.notes,
            )
        )
    snapshot_third_parties.sort(
        key=lambda item: (
            item.relationship_type,
            item.has_data_access,
            _documentary_optional_text_sort_key_v1(item.country),
            item.has_subprocessors,
            _documentary_optional_text_sort_key_v1(item.purpose),
            item.vendor_name,
            item.has_contract,
            _documentary_optional_text_sort_key_v1(item.contract_reference),
            _documentary_optional_text_sort_key_v1(item.engagement_object),
            _documentary_optional_text_sort_key_v1(item.engagement_duration),
            _documentary_optional_text_sort_key_v1(item.notes),
        )
    )

    snapshot_transfers = []
    for transfer in international_transfers:
        recipient_name = transfer.recipient_name
        if recipient_name is None and transfer.vendor_id is not None:
            vendor = vendors_by_id.get(transfer.vendor_id)
            if vendor is None:
                raise _bad_request(
                    "Uno o más destinatarios asociados no pertenecen "
                    "a la organización"
                )
            recipient_name = vendor.name

        snapshot_transfers.append(
            RatSnapshotInternationalTransferV1(
                recipient_name=recipient_name,
                destination_country=transfer.destination_country,
                adequacy_status=transfer.adequacy_status,
                mechanism=transfer.mechanism,
                guarantees_description=transfer.guarantees_description,
                evidence_reference=transfer.evidence_reference,
            )
        )
    snapshot_transfers.sort(
        key=lambda item: (
            item.destination_country,
            item.adequacy_status,
            _documentary_optional_text_sort_key_v1(item.mechanism),
            _documentary_optional_text_sort_key_v1(item.guarantees_description),
            _documentary_optional_text_sort_key_v1(item.recipient_name),
            _documentary_optional_text_sort_key_v1(item.evidence_reference),
        )
    )

    return RatContextSnapshotV1(
        purpose=purpose.purpose,
        organization_role=treatment.organization_role,
        data_categories=snapshot_categories,
        data_subjects=snapshot_subjects,
        data_sources=snapshot_sources,
        retention=RatSnapshotRetentionV1(
            retention_rule=treatment.retention_rule,
            deletion_method=treatment.deletion_method,
        ),
        automated_decisions=RatSnapshotAutomatedDecisionsV1(
            has_automated_decisions=treatment.has_automated_decisions,
            description=treatment.automated_decision_description,
        ),
        systems=snapshot_systems,
        third_parties=snapshot_third_parties,
        international_transfers=snapshot_transfers,
        special_regimes=RatSnapshotSpecialRegimesV1(
            has_sensitive_data=special_regimes.has_sensitive_data,
            includes_children=special_regimes.includes_children,
            includes_adolescents=special_regimes.includes_adolescents,
            has_vulnerable_groups=special_regimes.has_vulnerable_groups,
        ),
    )


async def build_rat_context_bundle_from_m2_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    *,
    purpose_key: str,
    scope: LegalAssessmentScopeIn,
) -> RatContextBundleV1:
    """Compone contexto canónico y snapshot desde la misma lectura lógica M2.

    Categorías y titulares corresponden al alcance seleccionado. Fuentes,
    sistemas, terceros y transferencias corresponden a la actividad completa:
    M2 no dispone de relaciones por finalidad para esos bloques.

    No implica aislamiento de snapshot de base de datos; garantiza que ambos
    objetos se construyen a partir de los mismos objetos M2 cargados durante
    esta composición.
    """
    treatment = await rat_service.obtener_tratamiento(db, organization_id, treatment_id)
    purpose = resolve_purpose_from_m2_v1(
        await rat_service.listar_finalidades(db, organization_id, treatment_id),
        purpose_key,
    )
    categories = resolve_data_categories_from_m2_v1(
        await rat_service.listar_categorias_datos(db, organization_id, treatment_id),
        scope.data_category_codes,
    )
    subjects = resolve_data_subjects_from_m2_v1(
        await rat_service.listar_titulares_datos(db, organization_id, treatment_id),
        scope.data_subject_codes,
    )
    sources = await rat_service.listar_fuentes_datos(db, organization_id, treatment_id)
    systems = await rat_service.listar_sistemas_tratamiento(
        db, organization_id, treatment_id
    )
    relationships = await rat_service.listar_vendors_tratamiento(
        db, organization_id, treatment_id
    )
    transfers = await rat_service.listar_transferencias(
        db, organization_id, treatment_id
    )

    vendor_ids = {relationship.vendor_id for relationship in relationships}
    vendor_ids.update(
        transfer.vendor_id
        for transfer in transfers
        if transfer.recipient_name is None and transfer.vendor_id is not None
    )
    vendors_by_id = await _load_vendors_by_id(
        db,
        organization_id,
        vendor_ids,
    )
    third_parties = _build_third_parties_from_vendor_map_v1(
        relationships,
        vendors_by_id,
    )

    canonical = build_rat_canonical_context_v1(
        purpose=purpose.purpose,
        organization_role=treatment.organization_role,
        data_categories=[
            RatCanonicalDataCategoryV1(
                category_code=item.category_code,
                category_name=item.category_name,
                is_sensitive=item.is_sensitive,
            )
            for item in categories
        ],
        data_subjects=[
            RatCanonicalDataSubjectV1(
                category_code=item.category_code,
                category_name=item.category_name,
                includes_children=item.includes_children,
                includes_adolescents=item.includes_adolescents,
                is_vulnerable_group=item.is_vulnerable_group,
            )
            for item in subjects
        ],
        data_sources=build_data_sources_from_m2_v1(sources),
        retention_rule=treatment.retention_rule,
        has_automated_decisions=treatment.has_automated_decisions,
        automated_decision_description=treatment.automated_decision_description,
        third_parties=third_parties,
        international_transfers=build_international_transfers_from_m2_v1(transfers),
    )

    snapshot = build_rat_context_snapshot_v1(
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

    return RatContextBundleV1(
        canonical=canonical,
        snapshot=snapshot,
    )


async def build_rat_context_from_m2_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    *,
    purpose_key: str,
    scope: LegalAssessmentScopeIn,
) -> RatCanonicalContextV1:
    """Compone el contexto canónico v1 manteniendo el contrato existente."""
    bundle = await build_rat_context_bundle_from_m2_v1(
        db,
        organization_id,
        treatment_id,
        purpose_key=purpose_key,
        scope=scope,
    )
    return bundle.canonical
