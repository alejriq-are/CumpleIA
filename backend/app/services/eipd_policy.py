"""Contrato interno §82: evidencia declarada de servidor, sin resolver ni activar gates."""

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StrictInt,
    StringConstraints,
    model_validator,
)

Route = Literal["sensible_derechos", "sensible_biometrica_derechos"]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Hash = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Commit = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]


class SourceRecordV1(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    emitter: Text
    instrument_reference: Text
    primary_url: HttpUrl
    publication_version: Text
    publication_date: date
    applicability_analysis: Text
    applicable_routes: tuple[Route, ...]
    verification_reference: Text
    verified_by: UUID

    @model_validator(mode="after")
    def routes_valid(self):
        if not self.applicable_routes or len(set(self.applicable_routes)) != len(
            self.applicable_routes
        ):
            raise ValueError("Rutas de fuente vacias o duplicadas")
        return self


class EipdGatePolicyV1(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    policy_version: StrictInt = Field(ge=1, le=1)
    policy_reference: Text
    routes: tuple[Route, ...]
    sources_status: Literal["pendiente", "verificadas"]
    source_records: tuple[SourceRecordV1, ...]
    acceptance_status: Literal["pendiente", "aceptada"]
    acceptance_reference: Text | None
    validation_commit: Commit | None
    acceptance_evidence_reference: Text | None
    accepted_by: UUID | None
    activation: Literal["deshabilitada", "habilitada"]

    @model_validator(mode="after")
    def coherent(self):
        if len(set(self.routes)) != len(self.routes):
            raise ValueError("Rutas duplicadas")
        refs = [s.instrument_reference for s in self.source_records]
        if len(set(refs)) != len(refs):
            raise ValueError("Instrumentos duplicados")
        if self.sources_status == "verificadas":
            covered = {r for s in self.source_records for r in s.applicable_routes}
            if not self.source_records or not set(self.routes) <= covered:
                raise ValueError(
                    "Fuentes verificadas exige instrumentos y cobertura de rutas"
                )
        if self.acceptance_status == "aceptada" and any(
            value is None
            for value in (
                self.acceptance_reference,
                self.validation_commit,
                self.acceptance_evidence_reference,
                self.accepted_by,
            )
        ):
            raise ValueError("Aceptacion exige evidencia y responsable")
        if self.activation == "habilitada" and (
            self.sources_status != "verificadas"
            or self.acceptance_status != "aceptada"
            or not self.routes
        ):
            raise ValueError("Habilitacion exige fuentes, aceptacion y rutas")
        return self


class EipdReviewPolicyIdentityV1(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    review_id: UUID
    policy_version: StrictInt = Field(ge=1, le=1)
    policy_reference: Text
    policy_hash: Hash


def validated_policy(value):
    # Revalidar incluso instancias mutadas; mode python conserva bool en StrictInt.
    raw = value.model_dump(mode="python") if isinstance(value, BaseModel) else value
    return EipdGatePolicyV1.model_validate(raw)


def build_eipd_policy_hash_v1(value):
    policy = validated_policy(value)
    data = policy.model_dump(mode="json")
    data["routes"] = sorted(data["routes"])
    for source in data["source_records"]:
        source["applicable_routes"] = sorted(source["applicable_routes"])
    data["source_records"].sort(key=lambda s: s["instrument_reference"])
    canonical = json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EipdPolicyIssueV1:
    stage: Literal["sources", "activation"]
    field: str
    code: str
    category: Literal["requiere_revision"] = "requiere_revision"
    question_id: None = None


@dataclass(frozen=True)
class EipdPolicyReadinessV1:
    policy_version: int | None
    policy_reference: str | None
    policy_hash: str | None
    routes: tuple[str, ...]
    sources_status: str
    acceptance_status: str
    activation: str
    issues: tuple[EipdPolicyIssueV1, ...]


def evaluate_eipd_policy_v1(value, *, route, evaluated_on: date):
    """Evalua el objeto interno; no verifica URL/red ni acredita autoridad real."""
    if type(evaluated_on) is not date:
        raise ValueError("evaluated_on exige date explicita")
    if route not in (
        "sensible_derechos",
        "sensible_biometrica_derechos",
        "sin_resolver",
    ):
        raise ValueError("Ruta no admitida")
    policy = validated_policy(value) if value is not None else None
    issues = []

    def issue(stage, field, code):
        issues.append(EipdPolicyIssueV1(stage, field, code))

    if policy is None or policy.sources_status != "verificadas":
        issue("sources", "official_sources", "fuentes_oficiales_no_verificadas")
    if policy is None:
        issue("activation", "policy", "politica_no_disponible")
    else:
        for source in policy.source_records:
            if source.publication_date > evaluated_on:
                issue(
                    "sources",
                    "source_records." + source.instrument_reference,
                    "publicacion_futura",
                )
        if route not in policy.routes:
            issue("activation", "policy.routes", "ruta_no_habilitada")
        if policy.acceptance_status != "aceptada":
            issue(
                "activation",
                "policy.acceptance_status",
                "frontera_revision_no_validada",
            )
    if policy is None or policy.activation != "habilitada":
        issue("activation", "eipd_gate", "gate_eipd_no_habilitado")
    return EipdPolicyReadinessV1(
        policy.policy_version if policy else None,
        policy.policy_reference if policy else None,
        build_eipd_policy_hash_v1(policy) if policy else None,
        tuple(sorted(policy.routes)) if policy else (),
        policy.sources_status if policy else "pendiente",
        policy.acceptance_status if policy else "pendiente",
        policy.activation if policy else "deshabilitada",
        tuple(
            sorted(
                set(issues),
                key=lambda i: (
                    ("sources", "activation").index(i.stage),
                    i.field,
                    i.code,
                ),
            )
        ),
    )


def build_eipd_review_policy_metadata_v1(value):
    """Metadatos para futura insercion de servidor; no es autorizacion de revision."""
    policy = validated_policy(value)
    return {
        "policy_version": policy.policy_version,
        "policy_reference": policy.policy_reference,
        "policy_hash": build_eipd_policy_hash_v1(policy),
    }


def derive_eipd_review_policy_identity_v1(review):
    """Mapea el evento persistido; historicos sin politica devuelven None."""

    def get(name):
        return (
            review.get(name)
            if isinstance(review, dict)
            else getattr(review, name, None)
        )

    values = {
        name: get(name)
        for name in ("policy_version", "policy_reference", "policy_hash")
    }
    if all(value is None for value in values.values()):
        return None
    return EipdReviewPolicyIdentityV1.model_validate({"review_id": get("id"), **values})


def resolve_eipd_gate_policy_v1():
    """Artefacto de servidor deshabilitado: sin flags/env/cliente ni fuentes supuestas."""
    return EipdGatePolicyV1.model_validate(
        {
            "policy_version": 1,
            "policy_reference": "m3-t1-eipd-deshabilitada-v1",
            "routes": ("sensible_derechos", "sensible_biometrica_derechos"),
            "sources_status": "pendiente",
            "source_records": (),
            "acceptance_status": "pendiente",
            "acceptance_reference": None,
            "validation_commit": None,
            "acceptance_evidence_reference": None,
            "accepted_by": None,
            "activation": "deshabilitada",
        }
    )
