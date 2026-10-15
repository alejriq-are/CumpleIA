"""Contratos CRUD futuros; no estan conectados a endpoints ni almacenamiento."""

from pydantic import ConfigDict

from app.schemas.child_adolescent import (
    BoundChildAdolescentAssessmentV1,
    ChildAdolescentAssessmentV1,
)
from app.schemas.licitud import (
    LegalAssessmentRepresentationDraftCreateV1,
    LegalAssessmentRepresentationDraftUpdateV1,
    LegalAssessmentRepresentationOutV2,
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
