"""Screening V3 conserva deteccion y bloquea continuacion con frontera pendiente."""

from dataclasses import dataclass
from typing import Literal

from app.services.eipd import EipdReadinessV1, evaluate_eipd_screening_v1
from app.services.eipd_frontier_v2 import (
    EipdFrontierReadinessV2,
    evaluate_eipd_frontier_v2,
)


@dataclass(frozen=True)
class EipdReadinessV3(EipdReadinessV1):
    frontier: EipdFrontierReadinessV2

    @property
    def evaluation_version(self) -> Literal[3]:
        return 3

    @property
    def can_continue(self) -> bool:
        return (
            self.frontier.is_frontier_prepared
            and self.result == "sin_supuestos_declarados"
        )

    @property
    def can_confirm(self) -> Literal[False]:
        return False


def evaluate_eipd_screening_v3(context) -> EipdReadinessV3:
    """Revalida ContextV2 en frontera; no reclasifica excepciones pendientes."""
    frontier = evaluate_eipd_frontier_v2(context)
    screening = frontier.screening
    if screening is None:
        screening = evaluate_eipd_screening_v1(None, None, None)
    return EipdReadinessV3(
        screening.result,
        screening.context_current,
        screening.issues,
        screening.observations,
        frontier,
    )
