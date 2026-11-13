"""Seleccion de binding desde material del servidor; sin persistencia ni eventos."""

from pydantic import BaseModel

from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
)
from app.services.eipd_resolution_binding_v2 import (
    EipdResolutionContextV2,
    bind_eipd_resolution_v2,
)
from app.services.eipd_resolution_readiness_v2 import _materials


def bind_eipd_resolution_for_context(document, context, *, previous=None):
    """Reaporte explicito: omision/null deben resolverse por el caller de PATCH.

    previous es material persistido de servidor. No acepta una version elegida por
    el cliente. Una resolucion V2 previa conserva cobertura incluso tras retirar
    research; las asociaciones previas no se reparan si no hay reaporte.
    """
    raw = (
        context.model_dump(mode="python") if isinstance(context, BaseModel) else context
    )
    ctx = EipdResolutionContextV2.model_validate(raw)
    previous_version = 1
    if previous is not None:
        _, _, _, previous_version = _materials(previous, ctx)
    special = ctx.special_conditions
    declared = special is not None and (
        any(c.regime_id == "investigacion_art16quinquies" for c in special.conditions)
        or any(
            d.question_id == "fines_historicos_estadisticos_cientificos_investigacion"
            and d.answer == "si"
            for d in special.declarations
        )
    )
    if ctx.research_assessment is not None or declared or previous_version == 2:
        return bind_eipd_resolution_v2(document, ctx)
    legacy = EipdResolutionContextV1.model_validate(
        {
            k: v
            for k, v in ctx.model_dump(mode="python").items()
            if k in EipdResolutionContextV1.model_fields
        }
    )
    return bind_eipd_resolution_v1(document, legacy)
