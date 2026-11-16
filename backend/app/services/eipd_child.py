"""Contexto sucesor de solo lectura; nunca repara hashes o eventos anteriores."""

from typing import Literal
from uuid import UUID

from app.schemas.child_adolescent import BoundChildAdolescentAssessmentV1
from app.schemas.eipd_child import EipdChildCompositionV5Out
from app.services.eipd_resolution_binding_v3 import EipdResolutionContextV3
from app.services.research_binding import digest


class EipdChildContextV4(EipdResolutionContextV3):
    context_schema_version: Literal[4] = 4
    organization_id: UUID
    treatment_id: UUID
    assessment_id: UUID
    child_adolescent_assessment: BoundChildAdolescentAssessmentV1 | None


def build_eipd_child_composition_v5(*, context, child, blockers):
    parsed = EipdChildContextV4.model_validate(context) if context is not None else None
    issues = [
        dict(field=i["field"], code=i["code"], message=i["message"]) for i in blockers
    ]
    issues.extend(
        dict(
            field=i["field"],
            code=i["code"],
            message="Revise el documento de infancia y su asociacion",
        )
        for i in child["issues"]
    )
    issues.append(
        dict(
            field="child_adolescent_assessment",
            code="politica_infancia_no_implementada",
            message="La cobertura infancia no habilita resolucion, confirmacion ni activacion EIPD",
        )
    )
    issues = list({(i["field"], i["code"], i["message"]): i for i in issues}.values())
    decisions = dict(prerequisites_met=False, context_metadata=None, issues=issues)
    return EipdChildCompositionV5Out.model_validate(
        dict(
            context_hash=(
                digest("cumpleia.eipd.child.context.v4", parsed.model_dump(mode="json"))
                if parsed is not None
                else None
            ),
            child_adolescent_coverage=(
                "contexto_v4" if parsed is not None else "contexto_actual_no_disponible"
            ),
            child_adolescent=child,
            confirmation_blockers=issues,
            continuar=decisions,
            requiere_cambios=decisions,
            no_continuar=decisions,
        )
    )
