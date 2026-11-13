"""Asociacion y hash documental de resolucion EIPD; funciones puras sin gates."""

import hashlib
import json

from pydantic import BaseModel, ConfigDict

from app.schemas.licitud import (
    BiometricAssessmentV1,
    BiometricRightsExceptionAssessmentV1,
    ConsentAssessmentV1,
    ContractAssessmentV1,
    EconomicObligationsAssessmentV1,
    EipdResolutionAssessmentStoredV1,
    EipdResolutionAssessmentV1,
    EipdScreeningV1,
    GeolocationAssessmentV1,
    HealthAssessmentV1,
    LegalBasis,
    LegalObligationAssessmentV1,
    LiaAssessmentV1,
    RatContextSnapshotV1,
    RightsDefenseAssessmentV1,
    SensitiveConsentAssessmentV1,
    SensitiveRightsExceptionAssessmentV1,
    SpecialConditionsV1,
)


class EipdResolutionContextV1(BaseModel):
    """Material interno final: cada entrada debe aportarse, incluso si es null.

    No incluye la resolucion ni eventos. No es un contrato de entrada HTTP.
    """

    model_config = ConfigDict(extra="forbid")
    rat_context_snapshot: RatContextSnapshotV1
    legal_basis: LegalBasis | None
    consent_assessment: ConsentAssessmentV1 | None
    lia_assessment: LiaAssessmentV1 | None
    contract_assessment: ContractAssessmentV1 | None
    legal_obligation_assessment: LegalObligationAssessmentV1 | None
    rights_defense_assessment: RightsDefenseAssessmentV1 | None
    economic_obligations_assessment: EconomicObligationsAssessmentV1 | None
    geolocation_assessment: GeolocationAssessmentV1 | None
    sensitive_consent_assessment: SensitiveConsentAssessmentV1 | None
    health_assessment: HealthAssessmentV1 | None
    biometric_assessment: BiometricAssessmentV1 | None
    sensitive_rights_exception_assessment: SensitiveRightsExceptionAssessmentV1 | None
    biometric_rights_exception_assessment: BiometricRightsExceptionAssessmentV1 | None
    special_conditions: SpecialConditionsV1 | None
    eipd_screening: EipdScreeningV1 | None


def _validated_json(model, value):
    # Revalidar tambien instancias modificadas despues de su construccion.
    return model.model_validate(
        value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    ).model_dump(mode="json")


def _hash(material):
    serialized = json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_eipd_resolution_context_hash_v1(
    context: EipdResolutionContextV1 | dict,
) -> str:
    """Hash del snapshot completo y todos los documentos finales validados."""
    return _hash(
        {
            "binding_version": 1,
            "context": _validated_json(EipdResolutionContextV1, context),
        }
    )


def bind_eipd_resolution_v1(
    document: EipdResolutionAssessmentV1 | dict,
    context: EipdResolutionContextV1 | dict,
) -> EipdResolutionAssessmentStoredV1:
    """Asociacion explicita de entrada editable; no conserva decision humana."""
    material = _validated_json(EipdResolutionAssessmentV1, document)
    material["context_binding"] = {
        "binding_version": 1,
        "context_hash": build_eipd_resolution_context_hash_v1(context),
    }
    return EipdResolutionAssessmentStoredV1.model_validate(material)


def build_eipd_resolution_document_hash_v1(
    document: EipdResolutionAssessmentStoredV1 | dict,
) -> str:
    """Incluye contenido y binding; excluye eventos y estado de revision."""
    return _hash(_validated_json(EipdResolutionAssessmentStoredV1, document))


def eipd_resolution_context_is_current_v1(
    document: EipdResolutionAssessmentStoredV1 | dict,
    context: EipdResolutionContextV1 | dict,
) -> bool:
    """Comparacion de lectura sin reasociar ni evaluar aprobacion/completitud."""
    parsed = EipdResolutionAssessmentStoredV1.model_validate(
        _validated_json(EipdResolutionAssessmentStoredV1, document)
    )
    expected = build_eipd_resolution_context_hash_v1(context)
    return (
        parsed.context_binding is not None
        and parsed.context_binding.context_hash == expected
    )
