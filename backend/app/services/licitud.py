"""Servicios del Módulo 3 — Bases de Licitud."""

import hashlib
import json
import unicodedata
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    EipdResolutionReview,
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
    BoundResearchAssessmentV1,
    EipdControlCompositionOut,
    EipdControlCompositionV2Out,
    EipdResolutionReviewIn,
    LegalAssessmentDraftCreate,
    LegalAssessmentDraftUpdate,
    LegalAssessmentReadinessOut,
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
from app.services.biometric import evaluate_biometric_assessment_v1
from app.services.biometric_rights_exception import (
    evaluate_biometric_rights_exception_v1,
)
from app.services.consentimiento import evaluate_consent_assessment_v1
from app.services.contract import evaluate_contract_assessment_v1
from app.services.economic_obligations import (
    evaluate_economic_obligations_assessment_v1,
)
from app.services.eipd import bind_eipd_screening_v11, evaluate_eipd_screening_v1
from app.services.eipd_confirmation import record_eipd_confirmation_evidence_v1
from app.services.eipd_controls import (
    compose_eipd_controls_v1,
    compose_eipd_controls_v2,
)
from app.services.eipd_policy import (
    build_eipd_review_policy_metadata_v1,
    derive_eipd_review_policy_identity_v1,
)
from app.services.eipd_policy_store import (
    lock_eipd_policy_selector_v1,
    read_selected_eipd_policy_v1,
    resolve_eipd_policy_snapshot_for_transaction_v1,
)
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
    build_eipd_resolution_document_hash_v1,
    derive_eipd_resolution_review_state_v1,
    evaluate_eipd_resolution_document_v1,
    evaluate_eipd_resolution_review_prerequisites_v1,
)
from app.services.eipd_review_v2 import evaluate_eipd_resolution_review_prerequisites_v2
from app.services.eipd_screening_v2 import evaluate_eipd_screening_v2
from app.services.geolocation import evaluate_geolocation_assessment_v1
from app.services.health import evaluate_health_assessment_v1
from app.services.legal_obligation import evaluate_legal_obligation_assessment_v1
from app.services.lia import evaluate_lia_assessment_v1
from app.services.research import evaluate_research_assessment_v1
from app.services.research_binding import (
    bind_research_assessment_v1,
    evaluate_research_association_v1,
)
from app.services.rights_defense import evaluate_rights_defense_assessment_v1
from app.services.sensitive_consent import evaluate_sensitive_consent_assessment_v1
from app.services.sensitive_rights_exception import (
    evaluate_sensitive_rights_exception_v1,
)
from app.services.special_conditions import (
    bind_special_conditions_v10,
    evaluate_special_conditions_v1,
)

CONFIRMABLE_ORDINARY_BASES = (
    "consentimiento_art12",
    "interes_legitimo_art13d",
    "contrato_precontractual_art13c",
    "obligacion_legal_art13b",
    "defensa_derechos_art13e",
    "obligaciones_economicas_art13a",
)


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


def _not_found(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def _conflict(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
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


async def _get_or_create_series_for_update_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    purpose: TreatmentPurpose,
    profile_id: uuid.UUID,
) -> LegalAssessmentSeries:
    """Obtiene o crea la serie lógica y la bloquea para la transacción actual."""

    purpose_key = build_purpose_key_v1(purpose.purpose)

    await db.execute(
        pg_insert(LegalAssessmentSeries)
        .values(
            organization_id=organization_id,
            treatment_id=treatment_id,
            purpose_key=purpose_key,
            purpose_text=purpose.purpose,
            created_by=profile_id,
            updated_by=profile_id,
        )
        .on_conflict_do_nothing(
            index_elements=[
                "organization_id",
                "treatment_id",
                "purpose_key",
            ]
        )
    )

    result = await db.execute(
        select(LegalAssessmentSeries)
        .where(
            LegalAssessmentSeries.organization_id == organization_id,
            LegalAssessmentSeries.treatment_id == treatment_id,
            LegalAssessmentSeries.purpose_key == purpose_key,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    return result.scalar_one()


def _reserve_next_version_v1(series: LegalAssessmentSeries) -> int:
    """Reserva la siguiente versión sobre una serie previamente bloqueada."""

    version = series.next_version
    series.next_version = version + 1
    return version


async def resolve_purpose_by_id_from_m2_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    purpose_id: uuid.UUID,
) -> TreatmentPurpose:
    """Resuelve el selector operativo actual de finalidad dentro del tenant."""

    result = await db.execute(
        select(TreatmentPurpose).where(
            TreatmentPurpose.id == purpose_id,
            TreatmentPurpose.organization_id == organization_id,
            TreatmentPurpose.treatment_id == treatment_id,
        )
    )
    purpose = result.scalar_one_or_none()

    if purpose is None:
        raise _bad_request(
            "La finalidad indicada no pertenece a la actividad de tratamiento"
        )

    return purpose


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


async def get_legal_assessment_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
) -> LegalAssessment:
    """Obtiene una versión del expediente acotada al tenant y tratamiento."""

    result = await db.execute(
        select(LegalAssessment).where(
            LegalAssessment.id == assessment_id,
            LegalAssessment.organization_id == organization_id,
            LegalAssessment.treatment_id == treatment_id,
        )
    )
    assessment = result.scalar_one_or_none()

    if assessment is None:
        raise _not_found("Evaluación jurídica no encontrada")

    return assessment


async def get_legal_assessment_draft_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
) -> LegalAssessment:
    """Obtiene una evaluación editable y exige estado borrador."""
    assessment = await get_legal_assessment_v1(
        db, organization_id, treatment_id, assessment_id
    )
    if assessment.status != "borrador":
        raise _conflict("La evaluación jurídica ya no está en estado borrador")
    return assessment


def _scope_from_snapshot_v1(
    snapshot: dict,
) -> LegalAssessmentScopeIn:
    """Recupera el alcance semántico persistido en un snapshot documental v1."""

    parsed = RatContextSnapshotV1.model_validate(snapshot)
    return LegalAssessmentScopeIn(
        data_category_codes=[item.category_code for item in parsed.data_categories],
        data_subject_codes=[item.category_code for item in parsed.data_subjects],
    )


def build_eipd_resolution_context_from_assessment_v1(assessment, snapshot):
    """Contexto final del expediente; no contiene resolucion ni eventos."""
    return EipdResolutionContextV1.model_validate(
        {
            "rat_context_snapshot": snapshot.model_dump(mode="json"),
            "legal_basis": assessment.legal_basis,
            "consent_assessment": assessment.consent_assessment,
            "lia_assessment": assessment.lia_assessment,
            "contract_assessment": assessment.contract_assessment,
            "legal_obligation_assessment": assessment.legal_obligation_assessment,
            "rights_defense_assessment": assessment.rights_defense_assessment,
            "economic_obligations_assessment": assessment.economic_obligations_assessment,
            "geolocation_assessment": assessment.geolocation_assessment,
            "sensitive_consent_assessment": assessment.sensitive_consent_assessment,
            "health_assessment": assessment.health_assessment,
            "biometric_assessment": getattr(assessment, "biometric_assessment", None),
            "sensitive_rights_exception_assessment": getattr(
                assessment, "sensitive_rights_exception_assessment", None
            ),
            "biometric_rights_exception_assessment": getattr(
                assessment, "biometric_rights_exception_assessment", None
            ),
            "special_conditions": assessment.special_conditions,
            "eipd_screening": assessment.eipd_screening,
        }
    )


async def update_legal_assessment_draft_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: LegalAssessmentDraftUpdate,
) -> LegalAssessment:
    """Actualiza parcialmente un borrador y recompone su contexto RAT v1."""

    assessment = await get_legal_assessment_draft_v1(
        db,
        organization_id,
        treatment_id,
        assessment_id,
    )

    changes = payload.model_dump(mode="json", exclude_unset=True)
    research_was_provided = "research_assessment" in payload.model_fields_set
    research_input = changes.pop("research_assessment", None)
    scope_was_provided = "scope" in changes
    changes.pop("scope", None)
    screening_was_provided = "eipd_screening" in changes
    screening_input = changes.pop("eipd_screening", None)
    special_was_provided = "special_conditions" in changes
    special_input = changes.pop("special_conditions", None)
    resolution_was_provided = "eipd_resolution_assessment" in changes
    resolution_input = changes.pop("eipd_resolution_assessment", None)

    series_result = await db.execute(
        select(LegalAssessmentSeries)
        .where(
            LegalAssessmentSeries.id == assessment.series_id,
            LegalAssessmentSeries.organization_id == organization_id,
            LegalAssessmentSeries.treatment_id == treatment_id,
        )
        .with_for_update()
    )
    series = series_result.scalar_one()

    assessment_result = await db.execute(
        select(LegalAssessment)
        .where(
            LegalAssessment.id == assessment_id,
            LegalAssessment.organization_id == organization_id,
            LegalAssessment.treatment_id == treatment_id,
            LegalAssessment.series_id == series.id,
        )
        .execution_options(populate_existing=True)
    )
    assessment = assessment_result.scalar_one_or_none()

    if assessment is None:
        raise _not_found("Evaluación jurídica no encontrada")

    if assessment.status != "borrador":
        raise _conflict("La evaluación jurídica ya no está en estado borrador")

    scope = (
        payload.scope
        if scope_was_provided
        else _scope_from_snapshot_v1(assessment.rat_context_snapshot)
    )

    bundle = await build_rat_context_bundle_from_m2_v1(
        db,
        organization_id,
        treatment_id,
        purpose_key=series.purpose_key,
        scope=scope,
    )

    for field, value in changes.items():
        setattr(assessment, field, value)

    assessment.purpose_snapshot = bundle.snapshot.purpose
    assessment.rat_context_hash = build_rat_context_hash_v1(bundle.canonical)
    assessment.rat_context_snapshot = bundle.snapshot.model_dump(mode="json")
    if research_was_provided:
        assessment.research_assessment = (
            bind_research_assessment_v1(
                research_input,
                bundle.snapshot,
                assessment.legal_basis,
                assessment.lia_assessment,
            ).model_dump(mode="json")
            if research_input is not None
            else None
        )
    if special_was_provided:
        try:
            assessment.special_conditions = (
                bind_special_conditions_v10(
                    special_input,
                    bundle.snapshot,
                    assessment.legal_basis,
                    assessment.consent_assessment,
                    assessment.lia_assessment,
                    assessment.contract_assessment,
                    assessment.legal_obligation_assessment,
                    assessment.rights_defense_assessment,
                    assessment.economic_obligations_assessment,
                    assessment.geolocation_assessment,
                    assessment.sensitive_consent_assessment,
                    assessment.health_assessment,
                    getattr(assessment, "biometric_assessment", None),
                    getattr(assessment, "sensitive_rights_exception_assessment", None),
                    getattr(assessment, "biometric_rights_exception_assessment", None),
                ).model_dump(mode="json")
                if special_input is not None
                else None
            )
        except ValueError:
            raise _bad_request(
                "Contrato o alcance de condiciones especiales inválido"
            ) from None
    if screening_was_provided:
        assessment.eipd_screening = (
            bind_eipd_screening_v11(
                screening_input,
                bundle.snapshot,
                assessment.lia_assessment,
                assessment.special_conditions,
                assessment.contract_assessment,
                assessment.legal_obligation_assessment,
                assessment.rights_defense_assessment,
                assessment.economic_obligations_assessment,
                assessment.geolocation_assessment,
                assessment.sensitive_consent_assessment,
                assessment.health_assessment,
                getattr(assessment, "biometric_assessment", None),
                getattr(assessment, "sensitive_rights_exception_assessment", None),
                getattr(assessment, "biometric_rights_exception_assessment", None),
            ).model_dump(mode="json")
            if screening_input is not None
            else None
        )
    if resolution_was_provided:
        try:
            assessment.eipd_resolution_assessment = (
                bind_eipd_resolution_v1(
                    resolution_input,
                    build_eipd_resolution_context_from_assessment_v1(
                        assessment, bundle.snapshot
                    ),
                ).model_dump(mode="json")
                if resolution_input is not None
                else None
            )
        except ValidationError:
            raise _bad_request(
                "Contrato de resolucion EIPD o contexto final invalido"
            ) from None
    assessment.updated_at = datetime.now(UTC)
    assessment.updated_by = profile_id

    await db.flush()
    return assessment


async def create_legal_assessment_draft_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: LegalAssessmentDraftCreate,
) -> LegalAssessment:
    """Crea una nueva versión borrador con contexto RAT v1 persistido."""

    purpose = await resolve_purpose_by_id_from_m2_v1(
        db,
        organization_id,
        treatment_id,
        payload.purpose_id,
    )
    purpose_key = build_purpose_key_v1(purpose.purpose)

    bundle = await build_rat_context_bundle_from_m2_v1(
        db,
        organization_id,
        treatment_id,
        purpose_key=purpose_key,
        scope=payload.scope,
    )

    series = await _get_or_create_series_for_update_v1(
        db,
        organization_id,
        treatment_id,
        purpose,
        profile_id,
    )

    result = await db.execute(
        select(LegalAssessment).where(
            LegalAssessment.organization_id == organization_id,
            LegalAssessment.treatment_id == treatment_id,
            LegalAssessment.series_id == series.id,
            LegalAssessment.status == "borrador",
        )
    )
    if result.scalar_one_or_none() is not None:
        raise _conflict("Ya existe un borrador para esta finalidad")

    version = _reserve_next_version_v1(series)
    now = datetime.now(UTC)
    series.updated_at = now
    series.updated_by = profile_id

    assessment = LegalAssessment(
        organization_id=organization_id,
        series_id=series.id,
        treatment_id=treatment_id,
        version=version,
        status="borrador",
        legal_basis=payload.legal_basis,
        justification=payload.justification,
        purpose_snapshot=bundle.snapshot.purpose,
        rat_context_hash=build_rat_context_hash_v1(bundle.canonical),
        rat_context_snapshot=bundle.snapshot.model_dump(mode="json"),
        consent_assessment=(
            payload.consent_assessment.model_dump(mode="json")
            if payload.consent_assessment is not None
            else None
        ),
        lia_assessment=(
            payload.lia_assessment.model_dump(mode="json")
            if payload.lia_assessment is not None
            else None
        ),
        geolocation_assessment=(
            payload.geolocation_assessment.model_dump(mode="json")
            if payload.geolocation_assessment is not None
            else None
        ),
        sensitive_consent_assessment=(
            payload.sensitive_consent_assessment.model_dump(mode="json")
            if payload.sensitive_consent_assessment is not None
            else None
        ),
        sensitive_rights_exception_assessment=(
            payload.sensitive_rights_exception_assessment.model_dump(mode="json")
            if payload.sensitive_rights_exception_assessment is not None
            else None
        ),
        biometric_rights_exception_assessment=(
            payload.biometric_rights_exception_assessment.model_dump(mode="json")
            if payload.biometric_rights_exception_assessment is not None
            else None
        ),
        biometric_assessment=(
            payload.biometric_assessment.model_dump(mode="json")
            if payload.biometric_assessment is not None
            else None
        ),
        health_assessment=(
            payload.health_assessment.model_dump(mode="json")
            if payload.health_assessment is not None
            else None
        ),
        economic_obligations_assessment=(
            payload.economic_obligations_assessment.model_dump(mode="json")
            if payload.economic_obligations_assessment is not None
            else None
        ),
        rights_defense_assessment=(
            payload.rights_defense_assessment.model_dump(mode="json")
            if payload.rights_defense_assessment is not None
            else None
        ),
        legal_obligation_assessment=(
            payload.legal_obligation_assessment.model_dump(mode="json")
            if payload.legal_obligation_assessment is not None
            else None
        ),
        contract_assessment=(
            payload.contract_assessment.model_dump(mode="json")
            if payload.contract_assessment is not None
            else None
        ),
        research_assessment=(
            bind_research_assessment_v1(
                payload.research_assessment,
                bundle.snapshot,
                payload.legal_basis,
                payload.lia_assessment,
            ).model_dump(mode="json")
            if payload.research_assessment is not None
            else None
        ),
        special_conditions=None,
        schema_version=1,
        rat_context_schema_version=1,
        created_by=profile_id,
        updated_by=profile_id,
    )
    if payload.special_conditions is not None:
        try:
            assessment.special_conditions = bind_special_conditions_v10(
                payload.special_conditions,
                bundle.snapshot,
                assessment.legal_basis,
                assessment.consent_assessment,
                assessment.lia_assessment,
                assessment.contract_assessment,
                assessment.legal_obligation_assessment,
                assessment.rights_defense_assessment,
                assessment.economic_obligations_assessment,
                assessment.geolocation_assessment,
                assessment.sensitive_consent_assessment,
                assessment.health_assessment,
                getattr(assessment, "biometric_assessment", None),
                getattr(assessment, "sensitive_rights_exception_assessment", None),
                getattr(assessment, "biometric_rights_exception_assessment", None),
            ).model_dump(mode="json")
        except ValueError:
            raise _bad_request(
                "Contrato o alcance de condiciones especiales inválido"
            ) from None
    if payload.eipd_screening is not None:
        assessment.eipd_screening = bind_eipd_screening_v11(
            payload.eipd_screening,
            bundle.snapshot,
            assessment.lia_assessment,
            assessment.special_conditions,
            assessment.contract_assessment,
            assessment.legal_obligation_assessment,
            assessment.rights_defense_assessment,
            assessment.economic_obligations_assessment,
            assessment.geolocation_assessment,
            assessment.sensitive_consent_assessment,
            assessment.health_assessment,
            getattr(assessment, "biometric_assessment", None),
            getattr(assessment, "sensitive_rights_exception_assessment", None),
            getattr(assessment, "biometric_rights_exception_assessment", None),
        ).model_dump(mode="json")
    if payload.eipd_resolution_assessment is not None:
        try:
            assessment.eipd_resolution_assessment = bind_eipd_resolution_v1(
                payload.eipd_resolution_assessment,
                build_eipd_resolution_context_from_assessment_v1(
                    assessment, bundle.snapshot
                ),
            ).model_dump(mode="json")
        except ValidationError:
            raise _bad_request(
                "Contrato de resolucion EIPD o contexto final invalido"
            ) from None
    db.add(assessment)
    await db.flush()
    return assessment


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


def evaluate_economic_obligations_gate_v1(assessment, snapshot):
    result = evaluate_economic_obligations_assessment_v1(
        assessment.economic_obligations_assessment, snapshot
    )
    blocker = (
        None
        if result.can_confirm
        else {
            "field": "economic_obligations_assessment",
            "code": "obligaciones_economicas_no_preparadas",
            "message": "Revise los motivos del expediente económico",
            "status_code": 400 if result.result == "incompleto" else 409,
        }
    )
    return result, blocker


def evaluate_rights_defense_gate_v1(assessment, snapshot):
    result = evaluate_rights_defense_assessment_v1(
        assessment.rights_defense_assessment, snapshot
    )
    blocker = (
        None
        if result.can_confirm
        else {
            "field": "rights_defense_assessment",
            "code": "defensa_derechos_no_preparada",
            "message": "Revise los motivos del expediente de derechos",
            "status_code": 400 if result.result == "incompleto" else 409,
        }
    )
    return result, blocker


def evaluate_legal_obligation_gate_v1(assessment, snapshot):
    result = evaluate_legal_obligation_assessment_v1(
        assessment.legal_obligation_assessment, snapshot
    )
    blocker = (
        None
        if result.can_confirm
        else {
            "field": "legal_obligation_assessment",
            "code": "obligacion_legal_no_preparada",
            "message": "Revise los motivos del expediente normativo",
            "status_code": 400 if result.result == "incompleto" else 409,
        }
    )
    return result, blocker


def evaluate_contract_gate_v1(assessment, snapshot):
    result = evaluate_contract_assessment_v1(assessment.contract_assessment, snapshot)
    blocker = (
        None
        if result.can_confirm
        else {
            "field": "contract_assessment",
            "code": "contrato_no_preparado",
            "message": "Revise los motivos del expediente contractual",
            "status_code": 400 if result.result == "incompleto" else 409,
        }
    )
    return result, blocker


def evaluate_lia_gate_v1(assessment, snapshot):
    result = evaluate_lia_assessment_v1(assessment.lia_assessment, snapshot)
    blocker = (
        None
        if result.can_confirm
        else {
            "field": "lia_assessment",
            "code": "lia_no_preparada",
            "message": "Revise los motivos de la evaluación LIA",
            "status_code": 400 if result.result == "incompleto" else 409,
        }
    )
    return result, blocker


def sensitive_consent_is_proposed_v1(assessment):
    return assessment.sensitive_consent_assessment is not None or (
        assessment.special_conditions is not None
        and any(
            item.get("regime_id") == "sensibles_art16"
            and (
                item.get("authorization_route") == "consentimiento"
                or item.get("sensitive_condition_id") == "consentimiento_expreso_art16"
            )
            for item in assessment.special_conditions.get("conditions", [])
        )
    )


def sensitive_rights_exception_is_proposed_v1(assessment):
    return getattr(
        assessment, "sensitive_rights_exception_assessment", None
    ) is not None or (
        assessment.special_conditions is not None
        and any(
            item.get("regime_id") == "sensibles_art16"
            and (
                item.get("authorization_route") == "excepcion_legal"
                or item.get("sensitive_condition_id") == "defensa_derechos_art16d"
            )
            for item in assessment.special_conditions.get("conditions", [])
        )
    )


def biometric_rights_exception_is_proposed_v1(assessment):
    return getattr(
        assessment, "biometric_rights_exception_assessment", None
    ) is not None or (
        assessment.special_conditions is not None
        and any(
            item.get("regime_id") == "biometricos_art16ter"
            and item.get("authorization_route") == "excepcion_legal"
            for item in assessment.special_conditions.get("conditions", [])
        )
    )


def biometric_consent_is_proposed_v1(assessment, detected_regimes):
    if getattr(assessment, "biometric_assessment", None) is not None:
        return True
    condition = next(
        (
            item
            for item in (assessment.special_conditions or {}).get("conditions", [])
            if item.get("regime_id") == "biometricos_art16ter"
        ),
        None,
    )
    return "biometricos_art16ter" in detected_regimes and (
        condition is None or condition.get("authorization_route") != "excepcion_legal"
    )


def evaluate_transversal_readiness_v1(assessment, snapshot):
    """Mismas barreras documentales para lectura y confirmación transaccional."""
    special = evaluate_special_conditions_v1(
        assessment.special_conditions,
        snapshot,
        assessment.legal_basis,
        assessment.consent_assessment,
        assessment.lia_assessment,
        assessment.contract_assessment,
        assessment.legal_obligation_assessment,
        assessment.rights_defense_assessment,
        assessment.economic_obligations_assessment,
        assessment.geolocation_assessment,
        assessment.sensitive_consent_assessment,
        assessment.health_assessment,
        getattr(assessment, "biometric_assessment", None),
        getattr(assessment, "sensitive_rights_exception_assessment", None),
        getattr(assessment, "biometric_rights_exception_assessment", None),
        research=getattr(assessment, "research_assessment", None),
    )
    eipd = evaluate_eipd_screening_v1(
        assessment.eipd_screening,
        snapshot,
        assessment.lia_assessment,
        assessment.special_conditions,
        assessment.contract_assessment,
        assessment.legal_obligation_assessment,
        assessment.rights_defense_assessment,
        assessment.economic_obligations_assessment,
        assessment.geolocation_assessment,
        assessment.sensitive_consent_assessment,
        assessment.consent_assessment,
        assessment.health_assessment,
        getattr(assessment, "biometric_assessment", None),
        getattr(assessment, "sensitive_rights_exception_assessment", None),
        getattr(assessment, "biometric_rights_exception_assessment", None),
        legal_basis=assessment.legal_basis,
        research=getattr(assessment, "research_assessment", None),
    )
    blockers = []
    if (
        getattr(assessment, "research_assessment", None) is not None
        or "investigacion_art16quinquies" in special.detected_regimes
    ):
        blockers.append(
            {
                "field": "research_assessment",
                "code": "investigacion_confirmacion_bloqueada",
                "message": "La preparación documental de investigación no habilita su confirmación",
                "status_code": 409,
            }
        )
    if getattr(assessment, "eipd_resolution_assessment", None) is not None:
        blockers.append(
            {
                "field": "eipd_resolution_assessment",
                "code": "resolucion_eipd_no_validada",
                "message": "La resolución EIPD está pendiente de evaluación y revisión",
                "status_code": 409,
            }
        )
    if (
        special.result not in ("sin_regimenes_declarados", "regimenes_preparados")
        or not special.context_current
    ):
        blockers.append(
            {
                "field": "special_conditions",
                "code": "condiciones_especiales_no_preparadas",
                "message": "Revise los motivos de detección especial",
                "status_code": 400 if special.result == "incompleto" else 409,
            }
        )
    if eipd.result != "sin_supuestos_declarados" or not eipd.context_current:
        incomplete_codes = {
            "screening_ausente",
            "pregunta_omitida",
            "respuesta_pendiente",
            "fundamento_ausente",
        }
        review = any(i.code not in incomplete_codes for i in eipd.issues)
        blockers.append(
            {
                "field": "eipd_screening",
                "code": "screening_eipd_no_preparado",
                "message": "Revise los motivos del screening EIPD",
                "status_code": 409 if review or eipd.result == "requiere_eipd" else 400,
            }
        )
    if sensitive_consent_is_proposed_v1(assessment):
        sensitive_result = evaluate_sensitive_consent_assessment_v1(
            assessment.sensitive_consent_assessment,
            snapshot,
            assessment.special_conditions,
            assessment.consent_assessment,
        )
        if not sensitive_result.can_confirm:
            blockers.append(
                {
                    "field": "sensitive_consent_assessment",
                    "code": "consentimiento_sensible_no_preparado",
                    "message": "Revise los motivos del consentimiento expreso sensible",
                    "status_code": (
                        400 if sensitive_result.result == "incompleto" else 409
                    ),
                }
            )
    if (
        assessment.health_assessment is not None
        or "salud_perfil_biologico_art16bis" in special.detected_regimes
    ):
        health_result = evaluate_health_assessment_v1(
            assessment.health_assessment,
            snapshot,
            assessment.special_conditions,
            assessment.consent_assessment,
            assessment.sensitive_consent_assessment,
        )
        if not health_result.can_confirm:
            blockers.append(
                {
                    "field": "health_assessment",
                    "code": "salud_no_preparada",
                    "message": "Revise los motivos del expediente de salud",
                    "status_code": 400 if health_result.result == "incompleto" else 409,
                }
            )
    biometric_document = getattr(assessment, "biometric_assessment", None)
    if biometric_consent_is_proposed_v1(assessment, special.detected_regimes):
        biometric_result = evaluate_biometric_assessment_v1(
            biometric_document,
            snapshot,
            assessment.special_conditions,
            assessment.consent_assessment,
            assessment.sensitive_consent_assessment,
        )
        if not biometric_result.can_confirm:
            blockers.append(
                {
                    "field": "biometric_assessment",
                    "code": "biometria_no_preparada",
                    "message": "Revise los motivos del expediente biométrico",
                    "status_code": (
                        400 if biometric_result.result == "incompleto" else 409
                    ),
                }
            )
    if sensitive_rights_exception_is_proposed_v1(assessment):
        exception_result = evaluate_sensitive_rights_exception_v1(
            getattr(assessment, "sensitive_rights_exception_assessment", None),
            snapshot,
            assessment.special_conditions,
        )
        if not exception_result.can_confirm:
            blockers.append(
                {
                    "field": "sensitive_rights_exception_assessment",
                    "code": "excepcion_derechos_no_preparada",
                    "message": "Revise los motivos de la excepción sensible de derechos",
                    "status_code": (
                        400 if exception_result.result == "incompleto" else 409
                    ),
                }
            )
    if biometric_rights_exception_is_proposed_v1(assessment):
        exception_result = evaluate_biometric_rights_exception_v1(
            getattr(assessment, "biometric_rights_exception_assessment", None),
            snapshot,
            assessment.special_conditions,
            getattr(assessment, "sensitive_rights_exception_assessment", None),
        )
        if not exception_result.can_confirm:
            blockers.append(
                {
                    "field": "biometric_rights_exception_assessment",
                    "code": "excepcion_derechos_no_preparada",
                    "message": "Revise los motivos de la excepción biométrica de derechos",
                    "status_code": (
                        400 if exception_result.result == "incompleto" else 409
                    ),
                }
            )
    return special, eipd, blockers


async def _latest_eipd_review_snapshot_v1(db, organization_id, assessment_id):
    """Lee ultimo evento del tenant; operaciones mutadoras llaman bajo lock."""
    latest_review = await db.scalar(
        select(EipdResolutionReview)
        .where(
            EipdResolutionReview.assessment_id == assessment_id,
            EipdResolutionReview.organization_id == organization_id,
        )
        .order_by(
            EipdResolutionReview.created_at.desc(), EipdResolutionReview.id.desc()
        )
        .limit(1)
    )
    review_payload = (
        {
            name: getattr(latest_review, name)
            for name in (
                "id",
                "organization_id",
                "assessment_id",
                "decision",
                "rationale",
                "review_reference",
                "document_hash",
                "context_hash",
                "created_by",
                "created_at",
            )
        }
        if latest_review is not None
        else None
    )
    identity = (
        derive_eipd_review_policy_identity_v1(latest_review) if latest_review else None
    )
    return review_payload, identity


async def _latest_eipd_review_payload_v1(db, organization_id, assessment_id):
    payload, _ = await _latest_eipd_review_snapshot_v1(
        db, organization_id, assessment_id
    )
    return payload


def _assessment_eipd_composition_input_v1(
    assessment, organization_id, context, rat_current, latest_review
):
    return {
        "organization_id": organization_id,
        "assessment_id": assessment.id,
        "assessment_status": assessment.status,
        "assessment_schema_version": assessment.schema_version,
        "rat_context_schema_version": assessment.rat_context_schema_version,
        "justification": assessment.justification,
        "rat_context_current": rat_current,
        "context": context,
        "resolution": assessment.eipd_resolution_assessment,
        "latest_review": latest_review,
    }


def _compose_assessment_eipd_controls_v1(
    assessment, organization_id, context, rat_current, latest_review, evaluated_on
):
    composition = compose_eipd_controls_v1(
        _assessment_eipd_composition_input_v1(
            assessment, organization_id, context, rat_current, latest_review
        ),
        evaluated_on=evaluated_on,
    )
    return EipdControlCompositionOut.model_validate(
        {
            **asdict(composition),
            "evaluation_version": 1,
            "detection_v2": {
                **asdict(composition.detection_v2),
                "evaluation_version": composition.detection_v2.evaluation_version,
            },
        }
    ).model_dump(mode="json")


async def _selected_disabled_eipd_policy_v1(db):
    try:
        publication = await read_selected_eipd_policy_v1(db)
    except ValueError:
        raise HTTPException(
            status_code=409, detail={"code": "politica_eipd_no_disponible"}
        ) from None
    if publication.policy.activation != "deshabilitada":
        raise HTTPException(
            status_code=409, detail={"code": "politica_eipd_habilitada_no_admitida"}
        )
    return publication.policy


def _compose_assessment_eipd_controls_v2(
    assessment,
    organization_id,
    context,
    rat_current,
    latest_review,
    identity,
    evaluated_on,
    policy,
):
    result = compose_eipd_controls_v2(
        {
            "assessment": _assessment_eipd_composition_input_v1(
                assessment, organization_id, context, rat_current, latest_review
            ),
            "policy": policy,
            "latest_review_policy": identity,
        },
        evaluated_on=evaluated_on,
    )
    return EipdControlCompositionV2Out.model_validate(
        {
            **asdict(result),
            "evaluation_version": result.evaluation_version,
            "detection_v2": {
                **asdict(result.detection_v2),
                "evaluation_version": result.detection_v2.evaluation_version,
            },
            "latest_review_policy": (
                identity.model_dump(mode="json") if identity else None
            ),
        }
    ).model_dump(mode="json")


async def confirm_legal_assessment_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    profile_id: uuid.UUID,
) -> LegalAssessment:
    """Confirma las bases ordinarias implementadas dentro de la transacción.

    El caller debe validar permisos y tenant, y hacer commit o rollback de la
    unidad de trabajo. Los regímenes sin validador implementado siguen bloqueados.
    """
    draft = await get_legal_assessment_draft_v1(
        db, organization_id, treatment_id, assessment_id
    )
    # Incluso sin selector, el advisory compartido serializa bootstrap antes de
    # serie. Su ausencia solo bloquea si el contexto revalidado exige EIPD.
    await lock_eipd_policy_selector_v1(db, require_selector=False)
    series_result = await db.execute(
        select(LegalAssessmentSeries)
        .where(
            LegalAssessmentSeries.id == draft.series_id,
            LegalAssessmentSeries.organization_id == organization_id,
            LegalAssessmentSeries.treatment_id == treatment_id,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    series = series_result.scalar_one_or_none()
    if series is None:
        raise _not_found("Serie de evaluación jurídica no encontrada")

    # La lectura anterior al lock no es fuente de verdad del estado/payload.
    draft_result = await db.execute(
        select(LegalAssessment)
        .where(
            LegalAssessment.id == assessment_id,
            LegalAssessment.series_id == series.id,
            LegalAssessment.organization_id == organization_id,
            LegalAssessment.treatment_id == treatment_id,
        )
        .execution_options(populate_existing=True)
    )
    draft = draft_result.scalar_one_or_none()
    if draft is None:
        raise _not_found("Evaluación jurídica no encontrada")
    if draft.status != "borrador":
        raise _conflict("La evaluación jurídica ya no está en estado borrador")
    if draft.schema_version != 1 or draft.rat_context_schema_version != 1:
        raise _conflict("Versión de evaluación o contexto RAT no admitida")
    if draft.legal_basis not in CONFIRMABLE_ORDINARY_BASES:
        raise _conflict(
            "La confirmación de esta base jurídica aún no está implementada"
        )
    if not draft.justification or not draft.justification.strip():
        raise _bad_request("Se requiere una justificación para confirmar")

    try:
        scope = _scope_from_snapshot_v1(draft.rat_context_snapshot)
        readiness = (
            evaluate_consent_assessment_v1(draft.consent_assessment)
            if draft.legal_basis == "consentimiento_art12"
            else None
        )
    except ValidationError:
        raise _bad_request(
            "Contrato de consentimiento o snapshot RAT inválido"
        ) from None
    if readiness is not None and not readiness.can_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "consentimiento_no_preparado",
                "result": readiness.result,
                "issues": [asdict(issue) for issue in readiness.issues],
                "applicability": [asdict(item) for item in readiness.applicability],
            },
        )
    if not scope.data_category_codes or not scope.data_subject_codes:
        raise _bad_request("El alcance requiere categorías de datos y titulares")

    bundle = await build_rat_context_bundle_from_m2_v1(
        db,
        organization_id,
        treatment_id,
        purpose_key=series.purpose_key,
        scope=scope,
    )
    if build_rat_context_hash_v1(bundle.canonical) != draft.rat_context_hash:
        raise _conflict("El contexto RAT cambió; revise y actualice el borrador")
    if bundle.canonical.organization_role is None:
        raise _bad_request("El contexto RAT requiere el rol de la organización")
    try:
        if draft.legal_basis == "interes_legitimo_art13d":
            lia_result, lia_blocker = evaluate_lia_gate_v1(draft, bundle.snapshot)
            if lia_blocker is not None:
                raise HTTPException(
                    status_code=lia_blocker["status_code"],
                    detail={
                        "code": lia_blocker["code"],
                        **asdict(lia_result),
                        "issues": [
                            {**asdict(i), "question_id": None}
                            for i in lia_result.issues
                        ],
                    },
                )
        elif draft.legal_basis == "contrato_precontractual_art13c":
            contract_result, contract_blocker = evaluate_contract_gate_v1(
                draft, bundle.snapshot
            )
            if contract_blocker is not None:
                raise HTTPException(
                    status_code=contract_blocker["status_code"],
                    detail={
                        "code": contract_blocker["code"],
                        **asdict(contract_result),
                    },
                )
        elif draft.legal_basis == "obligacion_legal_art13b":
            legal_result, legal_blocker = evaluate_legal_obligation_gate_v1(
                draft, bundle.snapshot
            )
            if legal_blocker is not None:
                raise HTTPException(
                    status_code=legal_blocker["status_code"],
                    detail={"code": legal_blocker["code"], **asdict(legal_result)},
                )
        elif draft.legal_basis == "defensa_derechos_art13e":
            rights_result, rights_blocker = evaluate_rights_defense_gate_v1(
                draft, bundle.snapshot
            )
            if rights_blocker is not None:
                raise HTTPException(
                    status_code=rights_blocker["status_code"],
                    detail={"code": rights_blocker["code"], **asdict(rights_result)},
                )
        elif draft.legal_basis == "obligaciones_economicas_art13a":
            economic_result, economic_blocker = evaluate_economic_obligations_gate_v1(
                draft, bundle.snapshot
            )
            if economic_blocker is not None:
                raise HTTPException(
                    status_code=economic_blocker["status_code"],
                    detail={
                        "code": economic_blocker["code"],
                        **asdict(economic_result),
                    },
                )
        special, eipd, blockers = evaluate_transversal_readiness_v1(
            draft, bundle.snapshot
        )
    except ValidationError:
        raise _bad_request("Contrato documental transversal inválido") from None
    eipd_controls = None
    eipd_controls_v2 = None
    evaluated_on = datetime.now(UTC).date()
    latest_review, identity = await _latest_eipd_review_snapshot_v1(
        db, organization_id, draft.id
    )
    if (
        draft.eipd_resolution_assessment is not None
        or eipd.result in ("requiere_eipd", "requiere_revision")
        or draft.sensitive_rights_exception_assessment is not None
        or draft.biometric_rights_exception_assessment is not None
    ):
        context = build_eipd_resolution_context_from_assessment_v1(
            draft, bundle.snapshot
        )
        eipd_controls = _compose_assessment_eipd_controls_v1(
            draft,
            organization_id,
            context,
            True,
            latest_review,
            evaluated_on,
        )
        eipd_controls_v2 = _compose_assessment_eipd_controls_v2(
            draft,
            organization_id,
            context,
            True,
            latest_review,
            identity,
            evaluated_on,
            await _selected_disabled_eipd_policy_v1(db),
        )
    # La composicion v2 evalua la frontera delimitada y rechaza las restantes.
    # Fuera del ambito EIPD se conservan las barreras transversales existentes.
    decision_blocked = (
        bool(eipd_controls_v2["confirmation_blockers"])
        if eipd_controls_v2 is not None
        else bool(blockers)
    )
    if decision_blocked:
        raise HTTPException(
            status_code=max((item["status_code"] for item in blockers), default=409),
            detail={
                "code": "controles_transversales_no_preparados",
                **(
                    {
                        "eipd_controls": eipd_controls,
                        "eipd_controls_v2": eipd_controls_v2,
                        "evaluation_version": 2,
                    }
                    if eipd_controls_v2 is not None
                    else {}
                ),
                "special": asdict(special),
                "eipd": asdict(eipd),
                "confirmation_blockers": [
                    {k: v for k, v in item.items() if k != "status_code"}
                    for item in blockers
                ],
            },
        )

    if eipd_controls_v2 is not None:
        try:
            await record_eipd_confirmation_evidence_v1(
                db,
                _assessment_eipd_composition_input_v1(
                    draft, organization_id, context, True, latest_review
                ),
                identity,
                actor_id=profile_id,
            )
        except ValueError:
            raise HTTPException(
                status_code=409, detail={"code": "evidencia_eipd_no_preparada"}
            ) from None

    previous_result = await db.execute(
        select(LegalAssessment)
        .where(
            LegalAssessment.series_id == series.id,
            LegalAssessment.organization_id == organization_id,
            LegalAssessment.treatment_id == treatment_id,
            LegalAssessment.status == "confirmado",
        )
        .execution_options(populate_existing=True)
    )
    previous = previous_result.scalar_one_or_none()
    now = datetime.now(UTC)
    if previous is not None:
        previous.status = "reemplazado"
        previous.replaced_at = now
        previous.replaced_by_assessment_id = draft.id
        previous.updated_at = now
        previous.updated_by = profile_id
        # Liberar el índice parcial antes de confirmar la sucesora.
        await db.flush()

    draft.status = "confirmado"
    draft.confirmed_at = now
    draft.confirmed_by = profile_id
    draft.updated_at = now
    draft.updated_by = profile_id
    series.updated_at = now
    series.updated_by = profile_id
    await db.flush()
    return draft


async def get_legal_assessment_readiness_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
) -> LegalAssessmentReadinessOut:
    """Consulta orientativa del contexto actual, sin locks ni escrituras."""
    assessment = await get_legal_assessment_v1(
        db, organization_id, treatment_id, assessment_id
    )
    blockers: list[dict] = []

    def block(field, code, message):
        blockers.append({"field": field, "code": code, "message": message})

    if assessment.status != "borrador":
        block("status", "evaluacion_no_editable", "Esta versión no es un borrador")
    if assessment.schema_version != 1 or assessment.rat_context_schema_version != 1:
        block(
            "schema_version",
            "version_no_admitida",
            "Versión de evaluación o contexto no admitida",
        )
    if assessment.legal_basis not in CONFIRMABLE_ORDINARY_BASES:
        block(
            "legal_basis",
            "base_no_implementada",
            "La confirmación de esta base aún no está implementada",
        )
    if not assessment.justification or not assessment.justification.strip():
        block(
            "justification",
            "justificacion_ausente",
            "Falta justificar la base seleccionada",
        )

    series = (
        await db.execute(
            select(LegalAssessmentSeries).where(
                LegalAssessmentSeries.id == assessment.series_id,
                LegalAssessmentSeries.organization_id == organization_id,
                LegalAssessmentSeries.treatment_id == treatment_id,
            )
        )
    ).scalar_one_or_none()
    if series is None:
        raise _not_found("Serie de evaluación jurídica no encontrada")

    try:
        scope = _scope_from_snapshot_v1(assessment.rat_context_snapshot)
    except ValidationError:
        raise _bad_request("Snapshot RAT inválido") from None
    if not scope.data_category_codes or not scope.data_subject_codes:
        block(
            "scope",
            "alcance_incompleto",
            "Faltan categorías de datos o titulares en el alcance",
        )
    current_snapshot = None
    rat_current = None
    try:
        bundle = await build_rat_context_bundle_from_m2_v1(
            db,
            organization_id,
            treatment_id,
            purpose_key=series.purpose_key,
            scope=scope,
        )
        current_snapshot = bundle.snapshot
        rat_current = (
            build_rat_context_hash_v1(bundle.canonical) == assessment.rat_context_hash
        )
        if not rat_current:
            block(
                "rat_context_hash",
                "contexto_rat_desactualizado",
                "El contexto RAT cambió; revise el borrador",
            )
        if bundle.canonical.organization_role is None:
            block(
                "rat_context_snapshot.organization_role",
                "rol_ausente",
                "Falta el rol de la organización",
            )
    except HTTPException as exc:
        if exc.status_code not in (400, 404):
            raise
        block(
            "rat_context_snapshot",
            "contexto_rat_no_disponible",
            "No se pudo recomponer el contexto actual; revise finalidad y alcance",
        )
    research = None
    consent = None
    lia = None
    contract = None
    legal_obligation = None
    health = None
    biometric = None
    sensitive_consent = None
    sensitive_rights_exception = None
    biometric_rights_exception = None
    geolocation = None
    economic_obligations = None
    rights_defense = None
    eipd_resolution = None
    eipd_controls = None
    eipd_controls_v2 = None
    evaluated_on = datetime.now(UTC).date()
    try:
        if assessment.legal_basis == "consentimiento_art12":
            result = evaluate_consent_assessment_v1(assessment.consent_assessment)
            consent = {
                "result": result.result,
                "issues": [asdict(item) for item in result.issues],
                "applicability": [
                    {
                        "field": f"answers.{item.question_id}",
                        "applicability": item.applicability,
                    }
                    for item in result.applicability
                ],
            }
            if not result.can_confirm:
                block(
                    "consent_assessment",
                    "consentimiento_no_preparado",
                    "Revise los motivos del checklist de consentimiento",
                )
        elif assessment.legal_basis == "interes_legitimo_art13d":
            result, lia_blocker = evaluate_lia_gate_v1(assessment, current_snapshot)
            lia = asdict(result)
            if lia_blocker is not None:
                blockers.append(
                    {k: v for k, v in lia_blocker.items() if k != "status_code"}
                )
        elif assessment.legal_basis == "contrato_precontractual_art13c":
            result, contract_blocker = evaluate_contract_gate_v1(
                assessment, current_snapshot
            )
            contract = asdict(result)
            if contract_blocker is not None:
                blockers.append(
                    {k: v for k, v in contract_blocker.items() if k != "status_code"}
                )
        elif assessment.legal_basis == "obligacion_legal_art13b":
            result, legal_blocker = evaluate_legal_obligation_gate_v1(
                assessment, current_snapshot
            )
            legal_obligation = asdict(result)
            if legal_blocker is not None:
                blockers.append(
                    {k: v for k, v in legal_blocker.items() if k != "status_code"}
                )
        elif assessment.legal_basis == "defensa_derechos_art13e":
            result, rights_blocker = evaluate_rights_defense_gate_v1(
                assessment, current_snapshot
            )
            rights_defense = asdict(result)
            if rights_blocker is not None:
                blockers.append(
                    {k: v for k, v in rights_blocker.items() if k != "status_code"}
                )
        elif assessment.legal_basis == "obligaciones_economicas_art13a":
            result, economic_blocker = evaluate_economic_obligations_gate_v1(
                assessment, current_snapshot
            )
            economic_obligations = asdict(result)
            if economic_blocker is not None:
                blockers.append(
                    {k: v for k, v in economic_blocker.items() if k != "status_code"}
                )
        special, eipd, transversal_blockers = evaluate_transversal_readiness_v1(
            assessment, current_snapshot
        )
        research_document = getattr(assessment, "research_assessment", None)
        if (
            research_document is not None
            or "investigacion_art16quinquies" in special.detected_regimes
        ):
            bound = (
                BoundResearchAssessmentV1.model_validate(research_document)
                if research_document is not None
                else None
            )
            research_result = evaluate_research_assessment_v1(
                bound.assessment if bound else None,
                current_snapshot,
                assessment.legal_basis,
                assessment.lia_assessment,
            )
            association = (
                evaluate_research_association_v1(
                    bound,
                    current_snapshot,
                    assessment.legal_basis,
                    assessment.lia_assessment,
                )
                if current_snapshot is not None
                else None
            )
            research = {
                **asdict(research_result),
                "association_result": (
                    association.result if association else "requiere_revision"
                ),
                "association_issues": (
                    list(association.issues)
                    if association
                    else ["contexto_rat_no_disponible"]
                ),
                "can_confirm": False,
            }
        if (
            assessment.geolocation_assessment is not None
            or "geolocalizacion_art16sexies" in special.detected_regimes
        ):
            geo_result = evaluate_geolocation_assessment_v1(
                assessment.geolocation_assessment,
                current_snapshot,
                assessment.special_conditions,
            )
            geolocation = asdict(geo_result)
            if not geo_result.can_confirm:
                block(
                    "geolocation_assessment",
                    "geolocalizacion_no_preparada",
                    "Revise los motivos del aviso de geolocalización",
                )
        if sensitive_consent_is_proposed_v1(assessment):
            sensitive_result = evaluate_sensitive_consent_assessment_v1(
                assessment.sensitive_consent_assessment,
                current_snapshot,
                assessment.special_conditions,
                assessment.consent_assessment,
            )
            sensitive_consent = asdict(sensitive_result)
        if (
            assessment.health_assessment is not None
            or "salud_perfil_biologico_art16bis" in special.detected_regimes
        ):
            health_result = evaluate_health_assessment_v1(
                assessment.health_assessment,
                current_snapshot,
                assessment.special_conditions,
                assessment.consent_assessment,
                assessment.sensitive_consent_assessment,
            )
            health = asdict(health_result)
        biometric_document = getattr(assessment, "biometric_assessment", None)
        if biometric_consent_is_proposed_v1(assessment, special.detected_regimes):
            biometric = asdict(
                evaluate_biometric_assessment_v1(
                    biometric_document,
                    current_snapshot,
                    assessment.special_conditions,
                    assessment.consent_assessment,
                    assessment.sensitive_consent_assessment,
                )
            )
        if sensitive_rights_exception_is_proposed_v1(assessment):
            sensitive_rights_exception = asdict(
                evaluate_sensitive_rights_exception_v1(
                    getattr(assessment, "sensitive_rights_exception_assessment", None),
                    current_snapshot,
                    assessment.special_conditions,
                )
            )
        if biometric_rights_exception_is_proposed_v1(assessment):
            biometric_rights_exception = asdict(
                evaluate_biometric_rights_exception_v1(
                    getattr(assessment, "biometric_rights_exception_assessment", None),
                    current_snapshot,
                    assessment.special_conditions,
                    getattr(assessment, "sensitive_rights_exception_assessment", None),
                )
            )
        resolution_document = getattr(assessment, "eipd_resolution_assessment", None)
        resolution_context = (
            build_eipd_resolution_context_from_assessment_v1(
                assessment, current_snapshot
            )
            if current_snapshot is not None
            else None
        )
        detection_v2 = evaluate_eipd_screening_v2(resolution_context)
        eipd_v2 = {
            **asdict(detection_v2),
            "evaluation_version": detection_v2.evaluation_version,
        }
        if (
            resolution_document is not None
            or eipd.result == "requiere_eipd"
            or any(i.category == "supuesto_declarado" for i in eipd.issues)
        ):
            eipd_resolution = asdict(
                evaluate_eipd_resolution_document_v1(
                    resolution_document,
                    resolution_context,
                    evaluated_on=evaluated_on,
                )
            )
        review_payload, review_identity = await _latest_eipd_review_snapshot_v1(
            db, organization_id, assessment.id
        )
        eipd_resolution_review = derive_eipd_resolution_review_state_v1(
            resolution_document, resolution_context, review_payload
        )
        proposed_exception = any(
            c.get("authorization_route") == "excepcion_legal"
            for c in (assessment.special_conditions or {}).get("conditions", [])
        )
        if (
            eipd_resolution is not None
            or review_payload is not None
            or proposed_exception
            or getattr(assessment, "sensitive_rights_exception_assessment", None)
            is not None
            or getattr(assessment, "biometric_rights_exception_assessment", None)
            is not None
        ):
            eipd_controls = _compose_assessment_eipd_controls_v1(
                assessment,
                organization_id,
                resolution_context,
                rat_current,
                review_payload,
                evaluated_on,
            )
            eipd_controls_v2 = _compose_assessment_eipd_controls_v2(
                assessment,
                organization_id,
                resolution_context,
                rat_current,
                review_payload,
                review_identity,
                evaluated_on,
                await _selected_disabled_eipd_policy_v1(db),
            )
        blockers.extend(
            {k: v for k, v in item.items() if k != "status_code"}
            for item in transversal_blockers
        )
    except ValidationError:
        raise _bad_request("Contrato documental de la evaluación inválido") from None
    return LegalAssessmentReadinessOut.model_validate(
        {
            "assessment_id": assessment.id,
            "status": assessment.status,
            "legal_basis": assessment.legal_basis,
            "rat_context_current": rat_current,
            "research": research,
            "consent": consent,
            "lia": lia,
            "contract": contract,
            "legal_obligation": legal_obligation,
            "geolocation": geolocation,
            "sensitive_consent": sensitive_consent,
            "sensitive_rights_exception": sensitive_rights_exception,
            "health": health,
            "biometric": biometric,
            "biometric_rights_exception": biometric_rights_exception,
            "economic_obligations": economic_obligations,
            "rights_defense": rights_defense,
            "eipd_resolution": eipd_resolution,
            "eipd_resolution_review": eipd_resolution_review,
            "eipd": asdict(eipd),
            "eipd_v2": eipd_v2,
            "eipd_controls": eipd_controls,
            "eipd_controls_v2": eipd_controls_v2,
            "special": asdict(special),
            "confirmation_blockers": blockers,
            "pending_controls": [
                "validacion_otros_regimenes_especiales",
                "expediente_eipd_y_revision",
            ],
        }
    )


async def record_eipd_resolution_review_v1(
    db: AsyncSession,
    organization_id: uuid.UUID,
    treatment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: EipdResolutionReviewIn,
) -> EipdResolutionReview:
    """Registra decision humana bajo lock; caller autentica y maneja transaccion."""
    draft = await get_legal_assessment_draft_v1(
        db, organization_id, treatment_id, assessment_id
    )
    # Orden global: advisory compartido -> selector FOR SHARE -> serie.
    # No existe fallback a la politica fija ni bootstrap desde una accion tenant.
    try:
        await resolve_eipd_policy_snapshot_for_transaction_v1(db)
    except ValueError:
        raise HTTPException(
            status_code=409, detail={"code": "politica_eipd_no_disponible"}
        ) from None
    series = await db.scalar(
        select(LegalAssessmentSeries)
        .where(
            LegalAssessmentSeries.id == draft.series_id,
            LegalAssessmentSeries.organization_id == organization_id,
            LegalAssessmentSeries.treatment_id == treatment_id,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if series is None:
        raise _not_found("Serie de evaluacion juridica no encontrada")
    draft = await db.scalar(
        select(LegalAssessment)
        .where(
            LegalAssessment.id == assessment_id,
            LegalAssessment.series_id == series.id,
            LegalAssessment.organization_id == organization_id,
            LegalAssessment.treatment_id == treatment_id,
        )
        .execution_options(populate_existing=True)
    )
    if draft is None:
        raise _not_found("Evaluacion juridica no encontrada")
    if draft.status != "borrador":
        raise _conflict("La evaluacion juridica ya no esta en estado borrador")
    if draft.schema_version != 1 or draft.rat_context_schema_version != 1:
        raise _conflict("Version de evaluacion o contexto RAT no admitida")
    try:
        scope = _scope_from_snapshot_v1(draft.rat_context_snapshot)
        bundle = await build_rat_context_bundle_from_m2_v1(
            db,
            organization_id,
            treatment_id,
            purpose_key=series.purpose_key,
            scope=scope,
        )
        context = build_eipd_resolution_context_from_assessment_v1(
            draft, bundle.snapshot
        )
        evaluated_on = datetime.now(UTC).date()
        result = evaluate_eipd_resolution_review_prerequisites_v1(
            draft.status,
            draft.eipd_resolution_assessment,
            context,
            payload,
            evaluated_on=evaluated_on,
        )
    except ValidationError:
        raise _bad_request("Contrato documental de revision EIPD invalido") from None
    # Identidad auditada revalidada tras adquirir ambos locks, hasta commit.
    # v1 se conserva como diagnostico; v2 decide los prerrequisitos de esta accion.
    policy = await _selected_disabled_eipd_policy_v1(db)
    latest_review, identity = await _latest_eipd_review_snapshot_v1(
        db, organization_id, draft.id
    )
    try:
        result_v2 = evaluate_eipd_resolution_review_prerequisites_v2(
            {
                "assessment": _assessment_eipd_composition_input_v1(
                    draft,
                    organization_id,
                    context,
                    build_rat_context_hash_v1(bundle.canonical)
                    == draft.rat_context_hash,
                    latest_review,
                ),
                "policy": policy,
                "latest_review_policy": identity,
            },
            payload,
            evaluated_on=evaluated_on,
        )
    except ValidationError:
        raise _bad_request("Contrato documental de revision EIPD invalido") from None
    eipd_controls = None
    eipd_controls_v2 = None
    if result_v2.decision == "continuar":
        eipd_controls = _compose_assessment_eipd_controls_v1(
            draft,
            organization_id,
            context,
            build_rat_context_hash_v1(bundle.canonical) == draft.rat_context_hash,
            latest_review,
            evaluated_on,
        )
        composition = result_v2.composition
        eipd_controls_v2 = EipdControlCompositionV2Out.model_validate(
            {
                **asdict(composition),
                "evaluation_version": 2,
                "detection_v2": {
                    **asdict(composition.detection_v2),
                    "evaluation_version": 2,
                },
                "latest_review_policy": (
                    identity.model_dump(mode="json") if identity else None
                ),
            }
        ).model_dump(mode="json")
    if not result_v2.prerequisites_met:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "revision_eipd_no_preparada",
                **(
                    {
                        "eipd_controls": eipd_controls,
                        "eipd_controls_v2": eipd_controls_v2,
                    }
                    if eipd_controls
                    else {}
                ),
                "issues": [asdict(i) for i in result.issues],
                "evaluation_version": 2,
                "issues_v2": [asdict(i) for i in result_v2.issues],
            },
        )
    request = EipdResolutionReviewIn.model_validate(
        payload.model_dump(mode="json")
        if isinstance(payload, EipdResolutionReviewIn)
        else payload
    )
    event = EipdResolutionReview(
        organization_id=organization_id,
        assessment_id=assessment_id,
        decision=request.decision,
        rationale=request.rationale,
        review_reference=request.review_reference,
        document_hash=build_eipd_resolution_document_hash_v1(
            draft.eipd_resolution_assessment
        ),
        context_hash=draft.eipd_resolution_assessment["context_binding"][
            "context_hash"
        ],
        created_by=profile_id,
        **build_eipd_review_policy_metadata_v1(policy),
    )
    db.add(event)
    await db.flush()
    return event
