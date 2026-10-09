"""Asociación y alcance documental especial; no valida autorizaciones jurídicas."""

import hashlib
import json
from dataclasses import dataclass
from typing import get_args

from pydantic import TypeAdapter

from app.schemas.licitud import (
    BiometricAssessmentV1,
    BiometricRightsExceptionAssessmentV1,
    ConsentAssessmentV1,
    ContractAssessmentV1,
    EconomicObligationsAssessmentV1,
    GeolocationAssessmentV1,
    HealthAssessmentV1,
    LegalBasis,
    LegalObligationAssessmentV1,
    LiaAssessmentV1,
    RatContextSnapshotV1,
    RightsDefenseAssessmentV1,
    SensitiveConsentAssessmentV1,
    SensitiveRightsExceptionAssessmentV1,
    SpecialConditionsDraftIn,
    SpecialConditionsV1,
    SpecialQuestionIdV1,
)
from app.services.biometric import evaluate_biometric_assessment_v1
from app.services.biometric_rights_exception import (
    evaluate_biometric_rights_exception_v1,
)
from app.services.geolocation import evaluate_geolocation_assessment_v1
from app.services.health import evaluate_health_assessment_v1
from app.services.research_transversal_binding import build_research_transversal_hash
from app.services.sensitive_consent import evaluate_sensitive_consent_assessment_v1
from app.services.sensitive_rights_exception import (
    evaluate_sensitive_rights_exception_v1,
)


def validate_special_conditions_scope_v1(conditions, snapshot):
    """Todos los selectores son subconjuntos semánticos del alcance RAT."""
    from app.services.licitud import canonicalize_text_v1

    categories = {
        canonicalize_text_v1(item.category_code) for item in snapshot.data_categories
    }
    subjects = {
        canonicalize_text_v1(item.category_code) for item in snapshot.data_subjects
    }
    for item in [*conditions.declarations, *conditions.conditions]:
        for field, available in (
            ("data_category_codes", categories),
            ("data_subject_codes", subjects),
        ):
            codes = [canonicalize_text_v1(code) for code in getattr(item, field)]
            if len(codes) != len(set(codes)):
                raise ValueError(f"{field} no admite códigos semánticos duplicados")
            if not set(codes).issubset(available):
                raise ValueError(f"{field} contiene códigos fuera del alcance RAT")


def build_special_context_binding_hash_v1(snapshot, legal_basis, consent, lia):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    material = {
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_special_context_binding_hash_v2(
    snapshot, legal_basis, consent, lia, contract
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
        else None
    )
    material = {
        "contract_assessment": (
            ContractAssessmentV1.model_validate(contract).model_dump(mode="json")
            if contract is not None
            else None
        ),
        "rat_context_snapshot": rat.model_dump(mode="json"),
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_special_context_binding_hash_v3(
    snapshot, legal_basis, consent, lia, contract, legal_obligation
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
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
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_special_context_binding_hash_v4(
    snapshot, legal_basis, consent, lia, contract, legal_obligation, rights_defense
):
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
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
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def bind_special_conditions_v1(conditions, snapshot, legal_basis, consent, lia):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 1,
                "hash": build_special_context_binding_hash_v1(
                    rat, legal_basis, consent, lia
                ),
            },
        }
    )


def bind_special_conditions_v2(
    conditions, snapshot, legal_basis, consent, lia, contract
):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 2,
                "hash": build_special_context_binding_hash_v2(
                    rat, legal_basis, consent, lia, contract
                ),
            },
        }
    )


def bind_special_conditions_v3(
    conditions, snapshot, legal_basis, consent, lia, contract, legal_obligation
):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 3,
                "hash": build_special_context_binding_hash_v3(
                    rat, legal_basis, consent, lia, contract, legal_obligation
                ),
            },
        }
    )


def build_special_context_binding_hash_v5(
    snapshot,
    legal_basis,
    consent,
    lia,
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
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
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
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_special_context_binding_hash_v6(
    snapshot,
    legal_basis,
    consent,
    lia,
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
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
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
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_special_context_binding_hash_v7(
    snapshot,
    legal_basis,
    consent,
    lia,
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
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
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
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def build_special_context_binding_hash_v8(
    snapshot,
    legal_basis,
    consent,
    lia,
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
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
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
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def bind_special_conditions_v8(
    conditions,
    snapshot,
    legal_basis,
    consent,
    lia,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 8,
                "hash": build_special_context_binding_hash_v8(
                    rat,
                    legal_basis,
                    consent,
                    lia,
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


def bind_special_conditions_v7(
    conditions,
    snapshot,
    legal_basis,
    consent,
    lia,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 7,
                "hash": build_special_context_binding_hash_v7(
                    rat,
                    legal_basis,
                    consent,
                    lia,
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


def bind_special_conditions_v6(
    conditions,
    snapshot,
    legal_basis,
    consent,
    lia,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 6,
                "hash": build_special_context_binding_hash_v6(
                    rat,
                    legal_basis,
                    consent,
                    lia,
                    contract,
                    legal_obligation,
                    rights_defense,
                    economic_obligations,
                    geolocation,
                ),
            },
        }
    )


def bind_special_conditions_v5(
    conditions,
    snapshot,
    legal_basis,
    consent,
    lia,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 5,
                "hash": build_special_context_binding_hash_v5(
                    rat,
                    legal_basis,
                    consent,
                    lia,
                    contract,
                    legal_obligation,
                    rights_defense,
                    economic_obligations,
                ),
            },
        }
    )


def bind_special_conditions_v4(
    conditions,
    snapshot,
    legal_basis,
    consent,
    lia,
    contract,
    legal_obligation,
    rights_defense,
):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 4,
                "hash": build_special_context_binding_hash_v4(
                    rat,
                    legal_basis,
                    consent,
                    lia,
                    contract,
                    legal_obligation,
                    rights_defense,
                ),
            },
        }
    )


@dataclass(frozen=True)
class SpecialIssueV1:
    field: str
    code: str
    category: str
    question_id: str | None = None


@dataclass(frozen=True)
class SpecialReadinessV1:
    result: str
    context_current: bool
    detected_regimes: tuple[str, ...]
    issues: tuple[SpecialIssueV1, ...]


def evaluate_special_conditions_v1(
    conditions,
    snapshot,
    legal_basis,
    consent,
    lia,
    contract=None,
    legal_obligation=None,
    rights_defense=None,
    economic_obligations=None,
    geolocation=None,
    sensitive_consent=None,
    health=None,
    biometric=None,
    sensitive_rights_exception=None,
    biometric_rights_exception=None,
):
    """Detecta hechos y preparación documental, sin autorizar rutas especiales."""
    parsed = (
        SpecialConditionsV1.model_validate(conditions)
        if conditions is not None
        else None
    )
    rat = (
        RatContextSnapshotV1.model_validate(snapshot) if snapshot is not None else None
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
    # Validar cuestionarios incluso si falta el expediente o contexto.
    if consent is not None:
        ConsentAssessmentV1.model_validate(consent)
    if lia is not None:
        LiaAssessmentV1.model_validate(lia)
    TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    issues = []
    detected = set()

    def issue(field, code, category="incompleto", question_id=None):
        issues.append(SpecialIssueV1(field, code, category, question_id))

    current = False
    if parsed is None:
        issue("special_conditions", "expediente_ausente")
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    mapping = {
        "datos_sensibles": "sensibles_art16",
        "salud_perfil_biologico": "salud_perfil_biologico_art16bis",
        "biometricos_identificacion_unica": "biometricos_art16ter",
        "ninos_ninas": "infancia_adolescencia_art16quater",
        "adolescentes": "infancia_adolescencia_art16quater",
        "datos_sensibles_adolescentes_menores_16": "infancia_adolescencia_art16quater",
        "fines_historicos_estadisticos_cientificos_investigacion": "investigacion_art16quinquies",
        "geolocalizacion": "geolocalizacion_art16sexies",
    }
    flags = {}
    if rat is not None:
        flags = {
            "datos_sensibles": rat.special_regimes.has_sensitive_data,
            "ninos_ninas": rat.special_regimes.includes_children,
            "adolescentes": rat.special_regimes.includes_adolescents,
            "grupos_vulnerables": rat.special_regimes.has_vulnerable_groups,
        }
        detected.update(
            mapping[q] for q, active in flags.items() if active and q in mapping
        )
    if parsed is not None:
        if rat is not None:
            if parsed.context_binding.schema_version < 10 and (
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
                        issue(field, code, "requiere_revision")
            elif parsed.context_binding.schema_version < 9 and biometric is not None:
                issue(
                    "context_binding.schema_version",
                    "asociacion_biometria_no_cubierta",
                    "requiere_revision",
                )
            elif parsed.context_binding.schema_version < 8 and health is not None:
                issue(
                    "context_binding.schema_version",
                    "asociacion_salud_no_cubierta",
                    "requiere_revision",
                )
            elif (
                parsed.context_binding.schema_version < 7
                and sensitive_consent is not None
            ):
                issue(
                    "context_binding.schema_version",
                    "asociacion_consentimiento_sensible_no_cubierta",
                    "requiere_revision",
                )
            elif parsed.context_binding.schema_version < 6 and geolocation is not None:
                issue(
                    "context_binding.schema_version",
                    "asociacion_geolocalizacion_no_cubierta",
                    "requiere_revision",
                )
            elif (
                parsed.context_binding.schema_version < 5
                and economic_obligations is not None
            ):
                issue(
                    "context_binding.schema_version",
                    "asociacion_economica_no_cubierta",
                    "requiere_revision",
                )
            elif (
                parsed.context_binding.schema_version < 4 and rights_defense is not None
            ):
                issue(
                    "context_binding.schema_version",
                    "asociacion_derechos_no_cubierta",
                    "requiere_revision",
                )
            elif (
                parsed.context_binding.schema_version < 3
                and legal_obligation is not None
            ):
                issue(
                    "context_binding.schema_version",
                    "asociacion_obligacion_legal_no_cubierta",
                    "requiere_revision",
                )
            elif parsed.context_binding.schema_version == 1 and contract is not None:
                issue(
                    "context_binding.schema_version",
                    "asociacion_contractual_no_cubierta",
                    "requiere_revision",
                )
            else:
                expected = (
                    build_special_context_binding_hash_v1(
                        rat, legal_basis, consent, lia
                    )
                    if parsed.context_binding.schema_version == 1
                    else (
                        build_special_context_binding_hash_v2(
                            rat, legal_basis, consent, lia, contract
                        )
                        if parsed.context_binding.schema_version == 2
                        else (
                            build_special_context_binding_hash_v3(
                                rat,
                                legal_basis,
                                consent,
                                lia,
                                contract,
                                legal_obligation,
                            )
                            if parsed.context_binding.schema_version == 3
                            else (
                                build_special_context_binding_hash_v4(
                                    rat,
                                    legal_basis,
                                    consent,
                                    lia,
                                    contract,
                                    legal_obligation,
                                    rights_defense,
                                )
                                if parsed.context_binding.schema_version == 4
                                else (
                                    build_special_context_binding_hash_v5(
                                        rat,
                                        legal_basis,
                                        consent,
                                        lia,
                                        contract,
                                        legal_obligation,
                                        rights_defense,
                                        economic_obligations,
                                    )
                                    if parsed.context_binding.schema_version == 5
                                    else (
                                        build_special_context_binding_hash_v6(
                                            rat,
                                            legal_basis,
                                            consent,
                                            lia,
                                            contract,
                                            legal_obligation,
                                            rights_defense,
                                            economic_obligations,
                                            geolocation,
                                        )
                                        if parsed.context_binding.schema_version == 6
                                        else (
                                            build_special_context_binding_hash_v7(
                                                rat,
                                                legal_basis,
                                                consent,
                                                lia,
                                                contract,
                                                legal_obligation,
                                                rights_defense,
                                                economic_obligations,
                                                geolocation,
                                                sensitive_consent,
                                            )
                                            if parsed.context_binding.schema_version
                                            == 7
                                            else (
                                                build_special_context_binding_hash_v8(
                                                    rat,
                                                    legal_basis,
                                                    consent,
                                                    lia,
                                                    contract,
                                                    legal_obligation,
                                                    rights_defense,
                                                    economic_obligations,
                                                    geolocation,
                                                    sensitive_consent,
                                                    health,
                                                )
                                                if parsed.context_binding.schema_version
                                                == 8
                                                else (
                                                    build_special_context_binding_hash_v9(
                                                        rat,
                                                        legal_basis,
                                                        consent,
                                                        lia,
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
                                                    == 9
                                                    else build_special_context_binding_hash_v10(
                                                        rat,
                                                        legal_basis,
                                                        consent,
                                                        lia,
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
                current = parsed.context_binding.hash == expected
                if not current:
                    issue(
                        "context_binding.hash",
                        "contexto_desactualizado",
                        "requiere_revision",
                    )
        answers = {d.question_id: d for d in parsed.declarations}
        for q in get_args(SpecialQuestionIdV1):
            d = answers.get(q)
            field = "declarations." + q
            if d is None:
                issue(field, "pregunta_omitida", question_id=q)
                continue
            if d.answer == "pendiente":
                issue(field + ".answer", "respuesta_pendiente", question_id=q)
            if not d.rationale or not d.rationale.strip():
                issue(field + ".rationale", "fundamento_ausente", question_id=q)
            if d.answer == "si" and q in mapping:
                detected.add(mapping[q])
            if (
                q in flags
                and d.answer != "pendiente"
                and (d.answer == "si") != flags[q]
            ):
                issue(field, "discordancia_rat", "requiere_revision", q)
            if d.answer == "si":
                if q == "grupos_vulnerables":
                    issue(field, "factor_vulnerabilidad", "requiere_revision", q)
                if (
                    rat is not None
                    and q
                    in ("salud_perfil_biologico", "biometricos_identificacion_unica")
                    and not rat.special_regimes.has_sensitive_data
                ):
                    issue(
                        field,
                        "clasificacion_sensible_incoherente",
                        "requiere_revision",
                        q,
                    )
                if q == "datos_sensibles_adolescentes_menores_16":
                    detected.add("sensibles_art16")
                    if rat is not None and not (
                        rat.special_regimes.includes_adolescents
                        and rat.special_regimes.has_sensitive_data
                    ):
                        issue(
                            field,
                            "cruce_sensible_adolescente_incoherente",
                            "requiere_revision",
                            q,
                        )
                    if not d.data_category_codes or not d.data_subject_codes:
                        issue(field, "subconjunto_edad_no_documentado", question_id=q)
        if rat is not None:
            try:
                validate_special_conditions_scope_v1(parsed, rat)
            except ValueError:
                issue("special_conditions", "alcance_invalido")
        expedients = {c.regime_id: c for c in parsed.conditions}
        for regime in sorted(detected):
            if regime not in expedients:
                issue("conditions." + regime, "expediente_regimen_ausente")
            if regime == "geolocalizacion_art16sexies":
                geo_result = evaluate_geolocation_assessment_v1(
                    geolocation, rat, parsed
                )
                for item in geo_result.issues:
                    field = (
                        item.field
                        if item.field.startswith(
                            (
                                "special_conditions",
                                "rat_context_snapshot",
                                "geolocation_assessment",
                            )
                        )
                        else "geolocation_assessment." + item.field
                    )
                    issue(field, item.code, item.category, item.question_id)
            elif (
                regime == "sensibles_art16"
                and regime in expedients
                and expedients[regime].authorization_route == "consentimiento"
                and expedients[regime].sensitive_condition_id
                == "consentimiento_expreso_art16"
            ):
                sensitive_result = evaluate_sensitive_consent_assessment_v1(
                    sensitive_consent, rat, parsed, consent
                )
                for item in sensitive_result.issues:
                    field = (
                        item.field
                        if item.field.startswith(
                            (
                                "special_conditions",
                                "rat_context_snapshot",
                                "sensitive_consent_assessment",
                                "consent_assessment",
                            )
                        )
                        else "sensitive_consent_assessment." + item.field
                    )
                    issue(field, item.code, item.category, item.question_id)
            elif (
                regime == "sensibles_art16"
                and regime in expedients
                and expedients[regime].authorization_route == "excepcion_legal"
                and expedients[regime].sensitive_condition_id
                == "defensa_derechos_art16d"
            ):
                exception_result = evaluate_sensitive_rights_exception_v1(
                    sensitive_rights_exception, rat, parsed
                )
                for item in exception_result.issues:
                    field = (
                        item.field
                        if item.field.startswith(
                            (
                                "special_conditions",
                                "rat_context_snapshot",
                                "sensitive_rights_exception_assessment",
                            )
                        )
                        else "sensitive_rights_exception_assessment." + item.field
                    )
                    issue(field, item.code, item.category, item.question_id)
            elif (
                regime == "salud_perfil_biologico_art16bis"
                and regime in expedients
                and expedients[regime].authorization_route == "consentimiento"
            ):
                health_result = evaluate_health_assessment_v1(
                    health, rat, parsed, consent, sensitive_consent
                )
                for item in health_result.issues:
                    field = (
                        item.field
                        if item.field.startswith(
                            (
                                "special_conditions",
                                "rat_context_snapshot",
                                "health_assessment",
                                "consent_assessment",
                                "sensitive_consent_assessment",
                            )
                        )
                        else "health_assessment." + item.field
                    )
                    issue(field, item.code, item.category, item.question_id)
            elif (
                regime == "biometricos_art16ter"
                and regime in expedients
                and expedients[regime].authorization_route == "consentimiento"
            ):
                biometric_result = evaluate_biometric_assessment_v1(
                    biometric, rat, parsed, consent, sensitive_consent
                )
                for item in biometric_result.issues:
                    field = (
                        item.field
                        if item.field.startswith(
                            (
                                "special_conditions",
                                "rat_context_snapshot",
                                "biometric_assessment",
                                "consent_assessment",
                                "sensitive_consent_assessment",
                            )
                        )
                        else "biometric_assessment." + item.field
                    )
                    issue(field, item.code, item.category, item.question_id)
            elif (
                regime == "biometricos_art16ter"
                and regime in expedients
                and expedients[regime].authorization_route == "excepcion_legal"
            ):
                exception_result = evaluate_biometric_rights_exception_v1(
                    biometric_rights_exception, rat, parsed, sensitive_rights_exception
                )
                for item in exception_result.issues:
                    field = (
                        item.field
                        if item.field.startswith(
                            (
                                "special_conditions",
                                "rat_context_snapshot",
                                "sensitive_rights_exception_assessment",
                                "biometric_rights_exception_assessment",
                            )
                        )
                        else "biometric_rights_exception_assessment." + item.field
                    )
                    issue(field, item.code, item.category, item.question_id)
            else:
                issue(
                    "conditions." + regime,
                    "validador_no_implementado",
                    "requiere_revision",
                )
        for regime, c in sorted(expedients.items()):
            field = "conditions." + regime
            if regime not in detected:
                issue(field, "condicion_residual", "requiere_revision")
                issue(field, "validador_no_implementado", "requiere_revision")
            if c.uses_consent_assessment is True and consent is None:
                issue(
                    field + ".uses_consent_assessment",
                    "consentimiento_referenciado_ausente",
                    "requiere_revision",
                )
            if (
                c.authorization_route == "consentimiento"
                and c.uses_consent_assessment is not True
            ):
                issue(
                    field + ".uses_consent_assessment",
                    "referencia_consentimiento_incoherente",
                    "requiere_revision",
                )
    if geolocation is not None and "geolocalizacion_art16sexies" not in detected:
        issue(
            "geolocation_assessment",
            "expediente_geolocalizacion_residual",
            "requiere_revision",
        )
    sensitive_condition = (
        next((c for c in parsed.conditions if c.regime_id == "sensibles_art16"), None)
        if parsed is not None
        else None
    )
    exception_route = (
        sensitive_condition is not None
        and sensitive_condition.authorization_route == "excepcion_legal"
        and sensitive_condition.sensitive_condition_id == "defensa_derechos_art16d"
    )
    if sensitive_rights_exception is not None and (
        "sensibles_art16" not in detected or not exception_route
    ):
        issue(
            "sensitive_rights_exception_assessment",
            "expediente_excepcion_sensible_residual",
            "requiere_revision",
        )
    if sensitive_consent is not None and (
        "sensibles_art16" not in detected
        or (
            sensitive_condition is not None
            and sensitive_condition.authorization_route == "excepcion_legal"
        )
    ):
        issue(
            "sensitive_consent_assessment",
            "expediente_consentimiento_sensible_residual",
            "requiere_revision",
        )
    if health is not None and "salud_perfil_biologico_art16bis" not in detected:
        issue("health_assessment", "expediente_salud_residual", "requiere_revision")
    biometric_condition = (
        next(
            (c for c in parsed.conditions if c.regime_id == "biometricos_art16ter"),
            None,
        )
        if parsed is not None
        else None
    )
    biometric_exception_route = (
        biometric_condition is not None
        and biometric_condition.authorization_route == "excepcion_legal"
    )
    if biometric_rights_exception is not None and (
        "biometricos_art16ter" not in detected or not biometric_exception_route
    ):
        issue(
            "biometric_rights_exception_assessment",
            "expediente_excepcion_biometrica_residual",
            "requiere_revision",
        )
    if biometric is not None and (
        "biometricos_art16ter" not in detected or biometric_exception_route
    ):
        issue(
            "biometric_assessment", "expediente_biometria_residual", "requiere_revision"
        )
    result = (
        "incompleto"
        if any(i.category == "incompleto" for i in issues)
        else (
            "requiere_revision"
            if issues
            else "regimenes_preparados" if detected else "sin_regimenes_declarados"
        )
    )
    return SpecialReadinessV1(result, current, tuple(sorted(detected)), tuple(issues))


def build_special_context_binding_hash_v9(
    snapshot,
    legal_basis,
    consent,
    lia,
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
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
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
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def bind_special_conditions_v9(
    conditions,
    snapshot,
    legal_basis,
    consent,
    lia,
    contract,
    legal_obligation,
    rights_defense,
    economic_obligations,
    geolocation,
    sensitive_consent,
    health,
    biometric,
):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 9,
                "hash": build_special_context_binding_hash_v9(
                    rat,
                    legal_basis,
                    consent,
                    lia,
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


def build_special_context_binding_hash_v10(
    snapshot,
    legal_basis,
    consent,
    lia,
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
    basis = TypeAdapter(LegalBasis | None).validate_python(legal_basis)
    consent_model = (
        ConsentAssessmentV1.model_validate(
            consent.model_dump()
            if isinstance(consent, ConsentAssessmentV1)
            else consent
        )
        if consent is not None
        else None
    )
    lia_model = (
        LiaAssessmentV1.model_validate(
            lia.model_dump() if isinstance(lia, LiaAssessmentV1) else lia
        )
        if lia is not None
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
        "legal_basis": basis,
        "consent_assessment": (
            consent_model.model_dump(mode="json") if consent_model is not None else None
        ),
        "lia_assessment": (
            lia_model.model_dump(mode="json") if lia_model is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def bind_special_conditions_v10(
    conditions,
    snapshot,
    legal_basis,
    consent,
    lia,
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
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 10,
                "hash": build_special_context_binding_hash_v10(
                    rat,
                    legal_basis,
                    consent,
                    lia,
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


def build_special_context_binding_hash_v11(
    snapshot,
    legal_basis,
    consent,
    lia,
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
    research=None,
):
    previous = build_special_context_binding_hash_v10(
        snapshot,
        legal_basis,
        consent,
        lia,
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
        "cumpleia.special.research", 11, previous, research
    )


def bind_special_conditions_v11(
    conditions,
    snapshot,
    legal_basis,
    consent,
    lia,
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
    research=None,
):
    parsed = SpecialConditionsDraftIn.model_validate(
        conditions.model_dump()
        if isinstance(conditions, SpecialConditionsDraftIn)
        else conditions
    )
    rat = RatContextSnapshotV1.model_validate(
        snapshot.model_dump()
        if isinstance(snapshot, RatContextSnapshotV1)
        else snapshot
    )
    validate_special_conditions_scope_v1(parsed, rat)
    return SpecialConditionsV1.model_validate(
        {
            **parsed.model_dump(mode="json"),
            "context_binding": {
                "schema_version": 11,
                "hash": build_special_context_binding_hash_v11(
                    rat,
                    legal_basis,
                    consent,
                    lia,
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
                    research=research,
                ),
            },
        }
    )
