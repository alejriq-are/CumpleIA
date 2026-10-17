"""Seleccion de binding desde material del servidor; sin persistencia ni eventos."""

from pydantic import BaseModel

from app.schemas.licitud import EipdResolutionAssessmentStoredV3
from app.services.eipd_resolution import (
    EipdResolutionContextV1,
    bind_eipd_resolution_v1,
)
from app.services.eipd_resolution_binding_v2 import (
    EipdResolutionContextV2,
    bind_eipd_resolution_v2,
)
from app.services.eipd_resolution_binding_v3 import (
    EipdResolutionContextV3,
    bind_eipd_resolution_v3,
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
    represented_context = (
        EipdResolutionContextV3.model_validate(raw)
        if isinstance(raw, dict) and "sensitive_representation_assessment" in raw
        else None
    )
    legacy_raw = (
        {
            **{
                key: value
                for key, value in raw.items()
                if key in EipdResolutionContextV2.model_fields
            },
            "context_schema_version": 2,
        }
        if represented_context is not None
        else raw
    )
    ctx = EipdResolutionContextV2.model_validate(legacy_raw)
    previous_version = 1
    if previous is not None:
        stored = (
            previous.model_dump(mode="python")
            if isinstance(previous, BaseModel)
            else previous
        )
        binding = stored.get("context_binding") if isinstance(stored, dict) else None
        if isinstance(binding, dict) and binding.get("binding_version") == 3:
            EipdResolutionAssessmentStoredV3.model_validate(stored)
            if represented_context is None:
                raise ValueError(
                    "Resolucion V3 exige contexto V3 explicito, incluso tras retirar material"
                )
            previous_version = 3
        else:
            _, _, _, previous_version = _materials(previous, ctx)
    if represented_context is not None and (
        represented_context.sensitive_representation_assessment is not None
        or previous_version == 3
    ):
        return bind_eipd_resolution_v3(document, represented_context)
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
