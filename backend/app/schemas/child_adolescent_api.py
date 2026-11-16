"""Contratos CRUD de infancia; documento crudo de entrada e identidad de salida."""

from typing import Literal

from pydantic import ConfigDict, model_validator

from app.schemas.child_adolescent import (
    BoundChildAdolescentAssessmentV1,
    ChildAdolescentAssessmentV1,
    ChildAdolescentReadinessOutV1,
)
from app.schemas.eipd_child import EipdChildCompositionV5Out
from app.schemas.licitud import (
    LegalAssessmentRepresentationDraftCreateV1,
    LegalAssessmentRepresentationDraftUpdateV1,
    LegalAssessmentRepresentationOutV2,
    LegalAssessmentRepresentationReadinessOutV2,
)


class LegalAssessmentChildDraftCreateV1(LegalAssessmentRepresentationDraftCreateV1):
    model_config = ConfigDict(extra="forbid")
    child_adolescent_assessment: ChildAdolescentAssessmentV1 | None = None


class LegalAssessmentChildDraftUpdateV1(LegalAssessmentRepresentationDraftUpdateV1):
    model_config = ConfigDict(extra="forbid")
    child_adolescent_assessment: ChildAdolescentAssessmentV1 | None = None


class LegalAssessmentChildOutV1(LegalAssessmentRepresentationOutV2):
    model_config = ConfigDict(extra="forbid")
    child_adolescent_assessment: BoundChildAdolescentAssessmentV1 | None = None


class LegalAssessmentChildReadinessOutV1(LegalAssessmentRepresentationReadinessOutV2):
    eipd_controls_v5: EipdChildCompositionV5Out | None = None
    child_adolescent: ChildAdolescentReadinessOutV1 | None = None
    child_adolescent_context_coverage: Literal["no_aplica", "pendiente"] = "no_aplica"

    @model_validator(mode="after")
    def explicit_child_coverage(self):
        expected = "pendiente" if self.child_adolescent is not None else "no_aplica"
        if self.child_adolescent_context_coverage != expected:
            raise ValueError("Cobertura infancia debe ser explicita")
        if (self.eipd_controls_v5 is not None) != (expected == "pendiente"):
            raise ValueError(
                "Composicion V5 requerida solo con cobertura infancia pendiente"
            )
        if (
            self.eipd_controls_v5 is not None
            and self.eipd_controls_v5.child_adolescent != self.child_adolescent
        ):
            raise ValueError(
                "Diagnostico V5 debe corresponder al documento de infancia"
            )
        if expected == "pendiente" and any(
            getattr(self, field) is not None
            for field in (
                "eipd_controls",
                "eipd_controls_v2",
                "eipd_controls_v3",
                "eipd_controls_v4",
            )
        ):
            raise ValueError("Composicion historica no cubre infancia")
        return self
