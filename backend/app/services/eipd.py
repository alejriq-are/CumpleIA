"""Asociación documental EIPD v1, independiente del hash RAT canónico."""

import hashlib
import json
from dataclasses import dataclass
from typing import Literal, get_args

from pydantic import TypeAdapter

from app.schemas.licitud import (
    BiometricAssessmentV1,
    BiometricRightsExceptionAssessmentV1,
    ContractAssessmentV1,
    EconomicObligationsAssessmentV1,
    EipdQuestionIdV1,
    EipdScreeningDraftIn,
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
from app.services.biometric import evaluate_biometric_assessment_v1
from app.services.geolocation import evaluate_geolocation_assessment_v1
from app.services.health import evaluate_health_assessment_v1
from app.services.research_transversal_binding import build_research_transversal_hash
from app.services.sensitive_consent import evaluate_sensitive_consent_assessment_v1


def build_eipd_context_binding_hash_v1(
    snapshot: RatContextSnapshotV1 | dict,
    lia: LiaAssessmentV1 | dict | None,
) -> str:
    parsed_snapshot = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    parsed_lia = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    material = {
        "rat_context_snapshot": parsed_snapshot.model_dump(mode="json"),
        "lia_assessment": (
            parsed_lia.model_dump(mode="json") if parsed_lia is not None else None
        ),
    }
    serialized = json.dumps(
        material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def bind_eipd_screening_v1(
    screening: EipdScreeningDraftIn | dict,
    snapshot: RatContextSnapshotV1 | dict,
    lia: LiaAssessmentV1 | dict | None,
) -> EipdScreeningV1:
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 1,
                "hash": build_eipd_context_binding_hash_v1(snapshot, lia),
            },
        }
    )


def build_eipd_context_binding_hash_v2(snapshot, lia, special_conditions):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_eipd_context_binding_hash_v3(snapshot, lia, special_conditions, contract):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_eipd_context_binding_hash_v4(
    snapshot, lia, special_conditions, contract, legal_obligation
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "legal_obligation_assessment": (
            LegalObligationAssessmentV1.model_validate(legal_obligation).model_dump(
                mode="json"
            )
            if legal_obligation is not None
            else None
        ),
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_eipd_context_binding_hash_v5(
    snapshot, lia, special_conditions, contract, legal_obligation, rights_defense
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "rights_defense_assessment": (
            RightsDefenseAssessmentV1.model_validate(rights_defense).model_dump(
                mode="json"
            )
            if rights_defense is not None
            else None
        ),
        "legal_obligation_assessment": (
            LegalObligationAssessmentV1.model_validate(legal_obligation).model_dump(
                mode="json"
            )
            if legal_obligation is not None
            else None
        ),
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def bind_eipd_screening_v2(screening, snapshot, lia, special_conditions):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 2,
                "hash": build_eipd_context_binding_hash_v2(
                    snapshot, lia, special_conditions
                ),
            },
        }
    )


def bind_eipd_screening_v3(screening, snapshot, lia, special_conditions, contract):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 3,
                "hash": build_eipd_context_binding_hash_v3(
                    snapshot, lia, special_conditions, contract
                ),
            },
        }
    )


def bind_eipd_screening_v4(
    screening, snapshot, lia, special_conditions, contract, legal_obligation
):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 4,
                "hash": build_eipd_context_binding_hash_v4(
                    snapshot, lia, special_conditions, contract, legal_obligation
                ),
            },
        }
    )


def build_eipd_context_binding_hash_v6(
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "economic_obligations_assessment": (
            EconomicObligationsAssessmentV1.model_validate(
                economic_obligations
            ).model_dump(mode="json")
            if economic_obligations is not None
            else None
        ),
        "rights_defense_assessment": (
            RightsDefenseAssessmentV1.model_validate(rights_defense).model_dump(
                mode="json"
            )
            if rights_defense is not None
            else None
        ),
        "legal_obligation_assessment": (
            LegalObligationAssessmentV1.model_validate(legal_obligation).model_dump(
                mode="json"
            )
            if legal_obligation is not None
            else None
        ),
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_eipd_context_binding_hash_v7(
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "geolocation_assessment": (
            GeolocationAssessmentV1.model_validate(geolocation).model_dump(mode="json")
            if geolocation is not None
            else None
        ),
        "economic_obligations_assessment": (
            EconomicObligationsAssessmentV1.model_validate(
                economic_obligations
            ).model_dump(mode="json")
            if economic_obligations is not None
            else None
        ),
        "rights_defense_assessment": (
            RightsDefenseAssessmentV1.model_validate(rights_defense).model_dump(
                mode="json"
            )
            if rights_defense is not None
            else None
        ),
        "legal_obligation_assessment": (
            LegalObligationAssessmentV1.model_validate(legal_obligation).model_dump(
                mode="json"
            )
            if legal_obligation is not None
            else None
        ),
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_eipd_context_binding_hash_v8(
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "sensitive_consent_assessment": (
            SensitiveConsentAssessmentV1.model_validate(sensitive_consent).model_dump(
                mode="json"
            )
            if sensitive_consent is not None
            else None
        ),
        "geolocation_assessment": (
            GeolocationAssessmentV1.model_validate(geolocation).model_dump(mode="json")
            if geolocation is not None
            else None
        ),
        "economic_obligations_assessment": (
            EconomicObligationsAssessmentV1.model_validate(
                economic_obligations
            ).model_dump(mode="json")
            if economic_obligations is not None
            else None
        ),
        "rights_defense_assessment": (
            RightsDefenseAssessmentV1.model_validate(rights_defense).model_dump(
                mode="json"
            )
            if rights_defense is not None
            else None
        ),
        "legal_obligation_assessment": (
            LegalObligationAssessmentV1.model_validate(legal_obligation).model_dump(
                mode="json"
            )
            if legal_obligation is not None
            else None
        ),
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_eipd_context_binding_hash_v9(
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "health_assessment": (
            HealthAssessmentV1.model_validate(health).model_dump(mode="json")
            if health is not None
            else None
        ),
        "sensitive_consent_assessment": (
            SensitiveConsentAssessmentV1.model_validate(sensitive_consent).model_dump(
                mode="json"
            )
            if sensitive_consent is not None
            else None
        ),
        "geolocation_assessment": (
            GeolocationAssessmentV1.model_validate(geolocation).model_dump(mode="json")
            if geolocation is not None
            else None
        ),
        "economic_obligations_assessment": (
            EconomicObligationsAssessmentV1.model_validate(
                economic_obligations
            ).model_dump(mode="json")
            if economic_obligations is not None
            else None
        ),
        "rights_defense_assessment": (
            RightsDefenseAssessmentV1.model_validate(rights_defense).model_dump(
                mode="json"
            )
            if rights_defense is not None
            else None
        ),
        "legal_obligation_assessment": (
            LegalObligationAssessmentV1.model_validate(legal_obligation).model_dump(
                mode="json"
            )
            if legal_obligation is not None
            else None
        ),
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def bind_eipd_screening_v9(
    screening,
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 9,
                "hash": build_eipd_context_binding_hash_v9(
                    snapshot,
                    lia,
                    special_conditions,
                    contract,
                    legal_obligation,
                    rights_defense,
                    economic_obligations,
                    geolocation,
                    sensitive_consent,
                    health,
                ),
            },
        }
    )


def bind_eipd_screening_v8(
    screening,
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 8,
                "hash": build_eipd_context_binding_hash_v8(
                    snapshot,
                    lia,
                    special_conditions,
                    contract,
                    legal_obligation,
                    rights_defense,
                    economic_obligations,
                    geolocation,
                    sensitive_consent,
                ),
            },
        }
    )


def bind_eipd_screening_v7(
    screening,
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 7,
                "hash": build_eipd_context_binding_hash_v7(
                    snapshot,
                    lia,
                    special_conditions,
                    contract,
                    legal_obligation,
                    rights_defense,
                    economic_obligations,
                    geolocation,
                ),
            },
        }
    )


def bind_eipd_screening_v6(
    screening,
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 6,
                "hash": build_eipd_context_binding_hash_v6(
                    snapshot,
                    lia,
                    special_conditions,
                    contract,
                    legal_obligation,
                    rights_defense,
                    economic_obligations,
                ),
            },
        }
    )


def bind_eipd_screening_v5(
    screening,
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 5,
                "hash": build_eipd_context_binding_hash_v5(
                    snapshot,
                    lia,
                    special_conditions,
                    contract,
                    legal_obligation,
                    rights_defense,
                ),
            },
        }
    )


EipdResult = Literal["requiere_eipd", "pendiente_revision", "sin_supuestos_declarados"]
EipdIssueCode = Literal[
    "screening_ausente",
    "snapshot_ausente",
    "contexto_desactualizado",
    "asociacion_especial_no_cubierta",
    "asociacion_contractual_no_cubierta",
    "asociacion_obligacion_legal_no_cubierta",
    "asociacion_derechos_no_cubierta",
    "asociacion_economica_no_cubierta",
    "asociacion_geolocalizacion_no_cubierta",
    "asociacion_salud_no_cubierta",
    "asociacion_consentimiento_sensible_no_cubierta",
    "pregunta_omitida",
    "respuesta_pendiente",
    "fundamento_ausente",
    "supuesto_declarado",
    "automatizacion_no_documentada",
    "ruta_especial_pendiente",
    "excepcion_especial_no_validada",
    "excepcion_especial_preparada",
    "excepcion_consentimiento_discordante",
    "excepcion_consentimiento_no_documentada",
]


@dataclass(frozen=True)
class EipdIssueV1:
    field: str
    code: EipdIssueCode
    category: Literal["pendiente_revision", "supuesto_declarado"]
    question_id: EipdQuestionIdV1 | None = None


@dataclass(frozen=True)
class EipdObservationV1:
    field: str
    code: Literal["valoracion_lia_alta"]


@dataclass(frozen=True)
class EipdReadinessV1:
    result: EipdResult
    context_current: bool
    issues: tuple[EipdIssueV1, ...]
    observations: tuple[EipdObservationV1, ...]

    @property
    def can_continue(self) -> bool:
        """Supera solo el screening; no certifica una exención ni confirma M3."""
        return self.result == "sin_supuestos_declarados"


def evaluate_eipd_screening_v1(
    screening: EipdScreeningV1 | dict | None,
    snapshot: RatContextSnapshotV1 | dict | None,
    lia: LiaAssessmentV1 | dict | None,
    special_conditions: SpecialConditionsV1 | dict | None = None,
    contract: ContractAssessmentV1 | dict | None = None,
    legal_obligation: LegalObligationAssessmentV1 | dict | None = None,
    rights_defense: RightsDefenseAssessmentV1 | dict | None = None,
    economic_obligations: EconomicObligationsAssessmentV1 | dict | None = None,
    geolocation: GeolocationAssessmentV1 | dict | None = None,
    sensitive_consent=None,
    consent_assessment=None,
    health=None,
    biometric=None,
    sensitive_rights_exception=None,
    biometric_rights_exception=None,
) -> EipdReadinessV1:
    """Evaluador historico v1: ninguna excepcion habilitada."""
    return _evaluate_eipd_screening(
        screening,
        snapshot,
        lia,
        special_conditions,
        contract,
        legal_obligation,
        rights_defense,
        economic_obligations,
        geolocation,
        sensitive_consent,
        consent_assessment,
        health,
        biometric,
        sensitive_rights_exception,
        biometric_rights_exception,
    )


def _evaluate_eipd_screening(
    screening: EipdScreeningV1 | dict | None,
    snapshot: RatContextSnapshotV1 | dict | None,
    lia: LiaAssessmentV1 | dict | None,
    special_conditions: SpecialConditionsV1 | dict | None = None,
    contract: ContractAssessmentV1 | dict | None = None,
    legal_obligation: LegalObligationAssessmentV1 | dict | None = None,
    rights_defense: RightsDefenseAssessmentV1 | dict | None = None,
    economic_obligations: EconomicObligationsAssessmentV1 | dict | None = None,
    geolocation: GeolocationAssessmentV1 | dict | None = None,
    sensitive_consent=None,
    consent_assessment=None,
    health=None,
    biometric=None,
    sensitive_rights_exception=None,
    biometric_rights_exception=None,
    *,
    prepared_exceptions: frozenset[str] = frozenset(),
) -> EipdReadinessV1:
    """Deriva detección EIPD conservando también los motivos históricos."""
    parsed = (
        EipdScreeningV1.model_validate(
            screening.model_dump()
            if isinstance(screening, EipdScreeningV1)
            else screening
        )
        if screening is not None
        else None
    )
    rat = (
        RatContextSnapshotV1.model_validate(
            snapshot.model_dump()
            if isinstance(snapshot, RatContextSnapshotV1)
            else snapshot
        )
        if snapshot is not None
        else None
    )
    parsed_lia = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    for value, model in (
        (sensitive_rights_exception, SensitiveRightsExceptionAssessmentV1),
        (biometric_rights_exception, BiometricRightsExceptionAssessmentV1),
    ):
        if value is not None:
            model.model_validate(
                value.model_dump() if isinstance(value, model) else value
            )
    if biometric is not None:
        BiometricAssessmentV1.model_validate(biometric)
    if health is not None:
        HealthAssessmentV1.model_validate(health)
    if sensitive_consent is not None:
        SensitiveConsentAssessmentV1.model_validate(sensitive_consent)
    if geolocation is not None:
        GeolocationAssessmentV1.model_validate(geolocation)
    if economic_obligations is not None:
        EconomicObligationsAssessmentV1.model_validate(economic_obligations)
    if rights_defense is not None:
        RightsDefenseAssessmentV1.model_validate(rights_defense)
    if legal_obligation is not None:
        LegalObligationAssessmentV1.model_validate(legal_obligation)
    if contract is not None:
        ContractAssessmentV1.model_validate(contract)
    issues: list[EipdIssueV1] = []
    observations: list[EipdObservationV1] = []
    force_review = False
    context_current = False

    if rat is None:
        issues.append(
            EipdIssueV1(
                "rat_context_snapshot", "snapshot_ausente", "pendiente_revision"
            )
        )
        force_review = True
    if parsed is None:
        issues.append(
            EipdIssueV1("eipd_screening", "screening_ausente", "pendiente_revision")
        )
        force_review = True
    elif rat is not None:
        if parsed.context_binding.schema_version < 11 and (
            sensitive_rights_exception is not None
            or biometric_rights_exception is not None
        ):
            for field, value, code in (
                (
                    "sensitive_rights_exception_assessment",
                    sensitive_rights_exception,
                    "asociacion_excepcion_sensible_no_cubierta",
                ),
                (
                    "biometric_rights_exception_assessment",
                    biometric_rights_exception,
                    "asociacion_excepcion_biometrica_no_cubierta",
                ),
            ):
                if value is not None:
                    issues.append(EipdIssueV1(field, code, "pendiente_revision"))
            force_review = True
        elif parsed.context_binding.schema_version < 10 and biometric is not None:
            issues.append(
                EipdIssueV1(
                    "context_binding.schema_version",
                    "asociacion_biometria_no_cubierta",
                    "pendiente_revision",
                )
            )
            force_review = True
        elif parsed.context_binding.schema_version < 9 and health is not None:
            issues.append(
                EipdIssueV1(
                    "context_binding.schema_version",
                    "asociacion_salud_no_cubierta",
                    "pendiente_revision",
                )
            )
            force_review = True
        elif (
            parsed.context_binding.schema_version < 8 and sensitive_consent is not None
        ):
            issues.append(
                EipdIssueV1(
                    "context_binding.schema_version",
                    "asociacion_consentimiento_sensible_no_cubierta",
                    "pendiente_revision",
                )
            )
            force_review = True
        elif parsed.context_binding.schema_version < 7 and geolocation is not None:
            issues.append(
                EipdIssueV1(
                    "context_binding.schema_version",
                    "asociacion_geolocalizacion_no_cubierta",
                    "pendiente_revision",
                )
            )
            force_review = True
        elif (
            parsed.context_binding.schema_version < 6
            and economic_obligations is not None
        ):
            issues.append(
                EipdIssueV1(
                    "context_binding.schema_version",
                    "asociacion_economica_no_cubierta",
                    "pendiente_revision",
                )
            )
            force_review = True
        elif parsed.context_binding.schema_version < 5 and rights_defense is not None:
            issues.append(
                EipdIssueV1(
                    "context_binding.schema_version",
                    "asociacion_derechos_no_cubierta",
                    "pendiente_revision",
                )
            )
            force_review = True
        elif parsed.context_binding.schema_version < 4 and legal_obligation is not None:
            issues.append(
                EipdIssueV1(
                    "context_binding.schema_version",
                    "asociacion_obligacion_legal_no_cubierta",
                    "pendiente_revision",
                )
            )
            force_review = True
        elif parsed.context_binding.schema_version < 3 and contract is not None:
            issues.append(
                EipdIssueV1(
                    "context_binding.schema_version",
                    "asociacion_contractual_no_cubierta",
                    "pendiente_revision",
                )
            )
            force_review = True
        elif parsed.context_binding.schema_version == 1 and special_model is not None:
            issues.append(
                EipdIssueV1(
                    "context_binding.schema_version",
                    "asociacion_especial_no_cubierta",
                    "pendiente_revision",
                )
            )
            force_review = True
        else:
            expected_hash = (
                build_eipd_context_binding_hash_v1(rat, parsed_lia)
                if parsed.context_binding.schema_version == 1
                else (
                    build_eipd_context_binding_hash_v2(rat, parsed_lia, special_model)
                    if parsed.context_binding.schema_version == 2
                    else (
                        build_eipd_context_binding_hash_v3(
                            rat, parsed_lia, special_model, contract
                        )
                        if parsed.context_binding.schema_version == 3
                        else (
                            build_eipd_context_binding_hash_v4(
                                rat,
                                parsed_lia,
                                special_model,
                                contract,
                                legal_obligation,
                            )
                            if parsed.context_binding.schema_version == 4
                            else (
                                build_eipd_context_binding_hash_v5(
                                    rat,
                                    parsed_lia,
                                    special_model,
                                    contract,
                                    legal_obligation,
                                    rights_defense,
                                )
                                if parsed.context_binding.schema_version == 5
                                else (
                                    build_eipd_context_binding_hash_v6(
                                        rat,
                                        parsed_lia,
                                        special_model,
                                        contract,
                                        legal_obligation,
                                        rights_defense,
                                        economic_obligations,
                                    )
                                    if parsed.context_binding.schema_version == 6
                                    else (
                                        build_eipd_context_binding_hash_v7(
                                            rat,
                                            parsed_lia,
                                            special_model,
                                            contract,
                                            legal_obligation,
                                            rights_defense,
                                            economic_obligations,
                                            geolocation,
                                        )
                                        if parsed.context_binding.schema_version == 7
                                        else (
                                            build_eipd_context_binding_hash_v8(
                                                rat,
                                                parsed_lia,
                                                special_model,
                                                contract,
                                                legal_obligation,
                                                rights_defense,
                                                economic_obligations,
                                                geolocation,
                                                sensitive_consent,
                                            )
                                            if parsed.context_binding.schema_version
                                            == 8
                                            else (
                                                build_eipd_context_binding_hash_v9(
                                                    rat,
                                                    parsed_lia,
                                                    special_model,
                                                    contract,
                                                    legal_obligation,
                                                    rights_defense,
                                                    economic_obligations,
                                                    geolocation,
                                                    sensitive_consent,
                                                    health,
                                                )
                                                if parsed.context_binding.schema_version
                                                == 9
                                                else (
                                                    build_eipd_context_binding_hash_v10(
                                                        rat,
                                                        parsed_lia,
                                                        special_model,
                                                        contract,
                                                        legal_obligation,
                                                        rights_defense,
                                                        economic_obligations,
                                                        geolocation,
                                                        sensitive_consent,
                                                        health,
                                                        biometric,
                                                    )
                                                    if parsed.context_binding.schema_version
                                                    == 10
                                                    else build_eipd_context_binding_hash_v11(
                                                        rat,
                                                        parsed_lia,
                                                        special_model,
                                                        contract,
                                                        legal_obligation,
                                                        rights_defense,
                                                        economic_obligations,
                                                        geolocation,
                                                        sensitive_consent,
                                                        health,
                                                        biometric,
                                                        sensitive_rights_exception,
                                                        biometric_rights_exception,
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
            context_current = parsed.context_binding.hash == expected_hash
        if not context_current and not force_review:
            issues.append(
                EipdIssueV1(
                    "context_binding.hash",
                    "contexto_desactualizado",
                    "pendiente_revision",
                )
            )
            force_review = True

    declarations = {item.question_id: item for item in parsed.answers} if parsed else {}
    has_trigger = False
    for question_id in get_args(EipdQuestionIdV1):
        declaration = declarations.get(question_id)
        path = f"answers.{question_id}"
        if declaration is None:
            issues.append(
                EipdIssueV1(path, "pregunta_omitida", "pendiente_revision", question_id)
            )
            continue
        has_rationale = declaration.rationale is not None and bool(
            declaration.rationale.strip()
        )
        if declaration.answer == "pendiente":
            issues.append(
                EipdIssueV1(
                    path + ".answer",
                    "respuesta_pendiente",
                    "pendiente_revision",
                    question_id,
                )
            )
        if not has_rationale:
            issues.append(
                EipdIssueV1(
                    path + ".rationale",
                    "fundamento_ausente",
                    "pendiente_revision",
                    question_id,
                )
            )
        if declaration.answer == "si" and has_rationale:
            has_trigger = True
            issues.append(
                EipdIssueV1(
                    path + ".answer",
                    "supuesto_declarado",
                    "supuesto_declarado",
                    question_id,
                )
            )
        if (
            question_id == "evaluacion_sistematica_automatizada_efectos_significativos"
            and declaration.answer == "si"
            and rat is not None
            and not rat.automated_decisions.has_automated_decisions
        ):
            # La declaración y el indicador RAT requieren revisión conjunta;
            # no se deduce jurídicamente el supuesto desde el indicador aislado.
            issues.append(
                EipdIssueV1(
                    path + ".answer",
                    "automatizacion_no_documentada",
                    "pendiente_revision",
                    question_id,
                )
            )
            force_review = True

    # Solo se contrasta un expediente especial explícito. No se infiere una
    # excepción desde legal_basis ni se convierte la ruta propuesta en permiso.
    if special_model is not None:
        question_id = "datos_protegidos_excepcion_consentimiento"
        declaration = declarations.get(question_id)
        path = f"answers.{question_id}.answer"
        exceptions = [
            c
            for c in special_model.conditions
            if c.authorization_route == "excepcion_legal"
        ]
        unresolved = [
            c
            for c in special_model.conditions
            if c.authorization_route in (None, "regla_especifica")
            and not (
                c.regime_id == "geolocalizacion_art16sexies"
                and c.authorization_route == "regla_especifica"
                and evaluate_geolocation_assessment_v1(
                    geolocation, rat, special_model
                ).can_confirm
            )
        ]
        unresolved += [
            c
            for c in special_model.conditions
            if c.authorization_route == "consentimiento"
            and c.regime_id == "sensibles_art16"
            and not (
                c.sensitive_condition_id == "consentimiento_expreso_art16"
                and evaluate_sensitive_consent_assessment_v1(
                    sensitive_consent, rat, special_model, consent_assessment
                ).can_confirm
            )
        ]
        unresolved += [
            c
            for c in special_model.conditions
            if c.regime_id == "salud_perfil_biologico_art16bis"
            and c.authorization_route == "consentimiento"
            and not evaluate_health_assessment_v1(
                health, rat, special_model, consent_assessment, sensitive_consent
            ).can_confirm
        ]
        unresolved += [
            c
            for c in special_model.conditions
            if c.regime_id == "biometricos_art16ter"
            and c.authorization_route == "consentimiento"
            and not evaluate_biometric_assessment_v1(
                biometric, rat, special_model, consent_assessment, sensitive_consent
            ).can_confirm
        ]
        for condition in sorted(unresolved, key=lambda c: c.regime_id):
            issues.append(
                EipdIssueV1(
                    f"special_conditions.conditions.{condition.regime_id}.authorization_route",
                    "ruta_especial_pendiente",
                    "pendiente_revision",
                    question_id,
                )
            )
            force_review = True
        for condition in sorted(exceptions, key=lambda c: c.regime_id):
            if condition.regime_id in prepared_exceptions:
                issues.append(
                    EipdIssueV1(
                        f"special_conditions.conditions.{condition.regime_id}.authorization_route",
                        "excepcion_especial_preparada",
                        "supuesto_declarado",
                        question_id,
                    )
                )
            else:
                issues.append(
                    EipdIssueV1(
                        f"special_conditions.conditions.{condition.regime_id}.authorization_route",
                        "excepcion_especial_no_validada",
                        "pendiente_revision",
                        question_id,
                    )
                )
                force_review = True
        if declaration is not None and declaration.answer == "no" and exceptions:
            issues.append(
                EipdIssueV1(
                    path,
                    "excepcion_consentimiento_discordante",
                    "pendiente_revision",
                    question_id,
                )
            )
            force_review = True
        if declaration is not None and declaration.answer == "si" and not exceptions:
            issues.append(
                EipdIssueV1(
                    path,
                    "excepcion_consentimiento_no_documentada",
                    "pendiente_revision",
                    question_id,
                )
            )
            force_review = True

    if parsed_lia is not None:
        for field in ("severity", "likelihood"):
            if getattr(parsed_lia.impact, field) == "alta":
                observations.append(
                    EipdObservationV1(
                        f"lia_assessment.impact.{field}", "valoracion_lia_alta"
                    )
                )

    if force_review:
        result: EipdResult = "pendiente_revision"
    elif has_trigger:
        result = "requiere_eipd"
    elif issues:
        result = "pendiente_revision"
    else:
        result = "sin_supuestos_declarados"
    return EipdReadinessV1(result, context_current, tuple(issues), tuple(observations))


def build_eipd_context_binding_hash_v10(
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
    biometric,
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "biometric_assessment": (
            BiometricAssessmentV1.model_validate(biometric).model_dump(mode="json")
            if biometric is not None
            else None
        ),
        "health_assessment": (
            HealthAssessmentV1.model_validate(health).model_dump(mode="json")
            if health is not None
            else None
        ),
        "sensitive_consent_assessment": (
            SensitiveConsentAssessmentV1.model_validate(sensitive_consent).model_dump(
                mode="json"
            )
            if sensitive_consent is not None
            else None
        ),
        "geolocation_assessment": (
            GeolocationAssessmentV1.model_validate(geolocation).model_dump(mode="json")
            if geolocation is not None
            else None
        ),
        "economic_obligations_assessment": (
            EconomicObligationsAssessmentV1.model_validate(
                economic_obligations
            ).model_dump(mode="json")
            if economic_obligations is not None
            else None
        ),
        "rights_defense_assessment": (
            RightsDefenseAssessmentV1.model_validate(rights_defense).model_dump(
                mode="json"
            )
            if rights_defense is not None
            else None
        ),
        "legal_obligation_assessment": (
            LegalObligationAssessmentV1.model_validate(legal_obligation).model_dump(
                mode="json"
            )
            if legal_obligation is not None
            else None
        ),
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def bind_eipd_screening_v10(
    screening,
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
    biometric,
):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 10,
                "hash": build_eipd_context_binding_hash_v10(
                    snapshot,
                    lia,
                    special_conditions,
                    contract,
                    legal_obligation,
                    rights_defense,
                    economic_obligations,
                    geolocation,
                    sensitive_consent,
                    health,
                    biometric,
                ),
            },
        }
    )


def build_eipd_context_binding_hash_v11(
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
    biometric,
    sensitive_rights_exception=None,
    biometric_rights_exception=None,
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    special_model = (
        SpecialConditionsV1.model_validate(
            special_conditions.model_dump()
            if isinstance(special_conditions, SpecialConditionsV1)
            else special_conditions
        )
        if special_conditions is not None
        else None
    )
    material = {
        "sensitive_rights_exception_assessment": (
            SensitiveRightsExceptionAssessmentV1.model_validate(
                sensitive_rights_exception.model_dump()
                if isinstance(
                    sensitive_rights_exception, SensitiveRightsExceptionAssessmentV1
                )
                else sensitive_rights_exception
            ).model_dump(mode="json")
            if sensitive_rights_exception is not None
            else None
        ),
        "biometric_rights_exception_assessment": (
            BiometricRightsExceptionAssessmentV1.model_validate(
                biometric_rights_exception.model_dump()
                if isinstance(
                    biometric_rights_exception, BiometricRightsExceptionAssessmentV1
                )
                else biometric_rights_exception
            ).model_dump(mode="json")
            if biometric_rights_exception is not None
            else None
        ),
        "biometric_assessment": (
            BiometricAssessmentV1.model_validate(biometric).model_dump(mode="json")
            if biometric is not None
            else None
        ),
        "health_assessment": (
            HealthAssessmentV1.model_validate(health).model_dump(mode="json")
            if health is not None
            else None
        ),
        "sensitive_consent_assessment": (
            SensitiveConsentAssessmentV1.model_validate(sensitive_consent).model_dump(
                mode="json"
            )
            if sensitive_consent is not None
            else None
        ),
        "geolocation_assessment": (
            GeolocationAssessmentV1.model_validate(geolocation).model_dump(mode="json")
            if geolocation is not None
            else None
        ),
        "economic_obligations_assessment": (
            EconomicObligationsAssessmentV1.model_validate(
                economic_obligations
            ).model_dump(mode="json")
            if economic_obligations is not None
            else None
        ),
        "rights_defense_assessment": (
            RightsDefenseAssessmentV1.model_validate(rights_defense).model_dump(
                mode="json"
            )
            if rights_defense is not None
            else None
        ),
        "legal_obligation_assessment": (
            LegalObligationAssessmentV1.model_validate(legal_obligation).model_dump(
                mode="json"
            )
            if legal_obligation is not None
            else None
        ),
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
        "special_conditions": (
            special_model.model_dump(mode="json") if special_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def bind_eipd_screening_v11(
    screening,
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
    biometric,
    sensitive_rights_exception=None,
    biometric_rights_exception=None,
):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 11,
                "hash": build_eipd_context_binding_hash_v11(
                    snapshot,
                    lia,
                    special_conditions,
                    contract,
                    legal_obligation,
                    rights_defense,
                    economic_obligations,
                    geolocation,
                    sensitive_consent,
                    health,
                    biometric,
                    sensitive_rights_exception,
                    biometric_rights_exception,
                ),
            },
        }
    )


def build_eipd_context_binding_hash_v12(
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
    biometric,
    sensitive_rights_exception=None,
    biometric_rights_exception=None,
    *,
    legal_basis,
    research=None,
):
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    previous = build_eipd_context_binding_hash_v11(
        snapshot,
        lia,
        special_conditions,
        contract,
        legal_obligation,
        rights_defense,
        economic_obligations,
        geolocation,
        sensitive_consent,
        health,
        biometric,
        sensitive_rights_exception,
        biometric_rights_exception,
    )
    return build_research_transversal_hash(
        "cumpleia.eipd.screening.research", 12, previous, research, legal_basis=basis
    )


def bind_eipd_screening_v12(
    screening,
    snapshot,
    lia,
    special_conditions,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
    biometric,
    sensitive_rights_exception=None,
    biometric_rights_exception=None,
    *,
    legal_basis,
    research=None,
):
    parsed = EipdScreeningDraftIn.model_validate(
        screening.model_dump()
        if isinstance(screening, EipdScreeningDraftIn)
        else screening
    )
    return EipdScreeningV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 12,
                "hash": build_eipd_context_binding_hash_v12(
                    snapshot,
                    lia,
                    special_conditions,
                    contract,
                    legal_obligation,
                    rights_defense,
                    economic_obligations,
                    geolocation,
                    sensitive_consent,
                    health,
                    biometric,
                    sensitive_rights_exception,
                    biometric_rights_exception,
                    legal_basis=legal_basis,
                    research=research,
                ),
            },
        }
    )
