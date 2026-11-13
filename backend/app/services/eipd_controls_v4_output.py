"""Proyeccion estricta del diagnostico V4, sin contexto de accion habilitado."""

from dataclasses import asdict

from app.schemas.licitud import EipdControlCompositionV4Out
from app.services.eipd_controls_v4 import compose_eipd_controls_v4


def build_eipd_controls_v4_output(value, *, evaluated_on):
    result = compose_eipd_controls_v4(value, evaluated_on=evaluated_on)
    data = asdict(result)
    data.update(
        evaluation_version=4,
        evaluation_scope="requisitos_documentales",
        authorizes_action=False,
        can_confirm=False,
    )
    detection = data["detection"]
    detection["evaluation_version"] = result.detection.evaluation_version
    if result.detection.evaluation_version == 3:
        detection.update(can_continue=False, can_confirm=False)
        detection["frontier"].update(is_frontier_prepared=False, can_confirm=False)
    data["resolution"]["can_confirm"] = False
    decisions = dict(
        evaluation_version=4,
        evaluation_scope="requisitos_documentales",
        authorizes_action=False,
        can_confirm=False,
    )
    for name in ("continuar", "requiere_cambios", "no_continuar"):
        decisions[name] = dict(
            prerequisites_met=False,
            context_metadata=None,
            issues=[asdict(i) for i in result.review_blockers],
        )
    data["review_prerequisites_v4"] = decisions
    return EipdControlCompositionV4Out.model_validate(data)
