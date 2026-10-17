"""Composicion de identidad y completitud; nunca rebindea ni confirma."""

from app.schemas.child_adolescent import (
    BoundChildAdolescentAssessmentV1,
    ChildAdolescentReadinessOutV1,
)
from app.services.child_adolescent import evaluate_child_adolescent_v1
from app.services.child_adolescent_binding import (
    ChildAdolescentContextV1,
    evaluate_child_adolescent_association_v1,
)
from app.services.child_adolescent_related import evaluate_child_adolescent_related_v1
from app.services.research_binding import validated


def build_child_adolescent_readiness_v1(bound, context):
    ctx = validated(ChildAdolescentContextV1, context)
    document = (
        validated(BoundChildAdolescentAssessmentV1, bound)
        if bound is not None
        else None
    )
    diagnostic = evaluate_child_adolescent_v1(
        document.assessment if document else None, ctx.rat_context_snapshot
    )
    issues = [
        dict(field=i.field, code=i.code, category=i.category) for i in diagnostic.issues
    ]
    if document is not None:
        issues.extend(
            dict(field=i.field, code=i.code, category=i.category)
            for i in evaluate_child_adolescent_related_v1(document.assessment, ctx)
        )
    association_status = "no_aplicable"
    if document is not None or diagnostic.result != "no_aplicable":
        association = evaluate_child_adolescent_association_v1(document, ctx)
        association_status = association.result
        issues.extend(
            dict(
                field="context_binding",
                code=code,
                category=(
                    "incompleto"
                    if code == "asociacion_ausente"
                    else "requiere_revision"
                ),
            )
            for code in association.issues
        )
    issues.sort(key=lambda i: (i["field"], i["code"], i["category"]))
    result = (
        "requiere_revision"
        if any(i["category"] == "requiere_revision" for i in issues)
        else "incompleto" if issues else diagnostic.result
    )
    return ChildAdolescentReadinessOutV1.model_validate(
        dict(
            evaluation_version=1,
            result=result,
            documentary_result=diagnostic.result,
            association_status=association_status,
            issues=issues,
            authorizes_action=False,
            can_confirm=False,
        )
    )
