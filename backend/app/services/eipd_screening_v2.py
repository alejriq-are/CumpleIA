"""Deteccion EIPD v2 sobre frontera calculada; nunca permiso de confirmar."""

from dataclasses import dataclass
from typing import Literal

from app.services.eipd import (
    EipdReadinessV1,
    _evaluate_eipd_screening,
    evaluate_eipd_screening_v1,
)
from app.services.eipd_frontier import (
    EipdFrontierReadinessV1,
    evaluate_eipd_frontier_v1,
)
from app.services.eipd_resolution import EipdResolutionContextV1, _validated_json


@dataclass(frozen=True)
class EipdReadinessV2(EipdReadinessV1):
    frontier: EipdFrontierReadinessV1

    @property
    def evaluation_version(self) -> Literal[2]:
        return 2


def evaluate_eipd_screening_v2(context) -> EipdReadinessV2:
    """Computa preparacion desde contexto actual; no acepta banderas del cliente.

    Conserva comparadores y validaciones compartidas. Solo una frontera completa
    cambia la clasificacion del motivo de excepcion, durante evaluacion, sin
    borrar motivos ni filtrar blockers devueltos por v1. API/gates siguen en v1.
    """
    ctx = (
        EipdResolutionContextV1.model_validate(
            _validated_json(EipdResolutionContextV1, context)
        )
        if context is not None
        else None
    )
    frontier = evaluate_eipd_frontier_v1(ctx)
    if ctx is None:
        screening = evaluate_eipd_screening_v1(None, None, None)
    elif not frontier.is_frontier_prepared:
        screening = frontier.screening
    else:
        prepared = frozenset(
            c.regime_id
            for c in ctx.special_conditions.conditions
            if c.authorization_route == "excepcion_legal"
        )
        screening = _evaluate_eipd_screening(
            ctx.eipd_screening,
            ctx.rat_context_snapshot,
            ctx.lia_assessment,
            ctx.special_conditions,
            ctx.contract_assessment,
            ctx.legal_obligation_assessment,
            ctx.rights_defense_assessment,
            ctx.economic_obligations_assessment,
            ctx.geolocation_assessment,
            ctx.sensitive_consent_assessment,
            ctx.consent_assessment,
            ctx.health_assessment,
            ctx.biometric_assessment,
            ctx.sensitive_rights_exception_assessment,
            ctx.biometric_rights_exception_assessment,
            prepared_exceptions=prepared,
            legal_basis=ctx.legal_basis,
        )
    return EipdReadinessV2(
        screening.result,
        screening.context_current,
        screening.issues,
        screening.observations,
        frontier,
    )
