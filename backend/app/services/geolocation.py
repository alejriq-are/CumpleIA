"""Preparación documental de geolocalización, sin certificar el aviso ni su entrega."""

from dataclasses import dataclass
from typing import Literal

from app.schemas.licitud import (
    GeolocationAssessmentV1,
    RatContextSnapshotV1,
    SpecialConditionsV1,
)


@dataclass(frozen=True)
class GeolocationIssueV1:
    field: str
    code: str
    category: Literal["incompleto", "requiere_revision"]
    question_id: str | None = None


@dataclass(frozen=True)
class GeolocationApplicabilityV1:
    field: str
    applicability: Literal["aplicable", "no_aplicable", "sin_resolver"]


@dataclass(frozen=True)
class GeolocationReadinessV1:
    result: Literal["incompleto", "requiere_revision", "completo"]
    issues: tuple[GeolocationIssueV1, ...]
    applicability: tuple[GeolocationApplicabilityV1, ...]

    @property
    def can_confirm(self):
        """Preparación documental únicamente; no habilita gates transversales."""
        return self.result == "completo"


def evaluate_geolocation_assessment_v1(assessment, snapshot, special_conditions):
    from app.services.licitud import canonicalize_text_v1

    geo = (
        GeolocationAssessmentV1.model_validate(assessment)
        if assessment is not None
        else GeolocationAssessmentV1()
    )
    rat = (
        RatContextSnapshotV1.model_validate(snapshot) if snapshot is not None else None
    )
    special = (
        SpecialConditionsV1.model_validate(special_conditions)
        if special_conditions is not None
        else None
    )
    issues = []
    applicability = []

    def issue(field, code, category="incompleto"):
        issues.append(GeolocationIssueV1(field, code, category))

    def present(value):
        return value is not None and bool(value.strip())

    def text(field):
        if not present(getattr(geo, field)):
            issue(field, "campo_obligatorio")

    def response(field):
        value = getattr(geo, field)
        if value is None:
            issue(field, "respuesta_ausente")
            return
        if value.answer == "pendiente":
            issue(field + ".answer", "respuesta_pendiente")
        elif value.answer == "no":
            issue(field + ".answer", "respuesta_revision", "requiere_revision")
        if not present(value.rationale):
            issue(field + ".rationale", "fundamento_ausente")

    if assessment is None:
        issue("geolocation_assessment", "expediente_ausente")
    if rat is None:
        issue("rat_context_snapshot", "snapshot_ausente")
    else:
        if rat.organization_role != "responsable":
            issue(
                "rat_context_snapshot.organization_role",
                "rol_no_admitido",
                "requiere_revision",
            )
        if present(geo.purpose_description) and canonicalize_text_v1(
            geo.purpose_description
        ) != canonicalize_text_v1(rat.purpose):
            issue("purpose_description", "finalidad_distinta", "requiere_revision")
    declaration = None
    condition = None
    if special is None:
        issue("special_conditions", "condiciones_ausentes")
    else:
        declaration = next(
            (d for d in special.declarations if d.question_id == "geolocalizacion"),
            None,
        )
        condition = next(
            (
                c
                for c in special.conditions
                if c.regime_id == "geolocalizacion_art16sexies"
            ),
            None,
        )
        if declaration is None:
            issue(
                "special_conditions.declarations.geolocalizacion", "declaracion_ausente"
            )
        else:
            field = "special_conditions.declarations.geolocalizacion"
            if declaration.answer == "pendiente":
                issue(field + ".answer", "respuesta_pendiente")
            elif declaration.answer == "no":
                issue(field + ".answer", "regimen_no_declarado", "requiere_revision")
            if not present(declaration.rationale):
                issue(field + ".rationale", "fundamento_ausente")
        if condition is None:
            issue(
                "special_conditions.conditions.geolocalizacion_art16sexies",
                "expediente_regimen_ausente",
            )
        else:
            field = "special_conditions.conditions.geolocalizacion_art16sexies"
            if condition.authorization_route is None:
                issue(field + ".authorization_route", "ruta_ausente")
            elif condition.authorization_route != "regla_especifica":
                issue(
                    field + ".authorization_route",
                    "ruta_no_admitida",
                    "requiere_revision",
                )
            if condition.uses_consent_assessment is True:
                issue(
                    field + ".uses_consent_assessment",
                    "referencia_consentimiento_incoherente",
                    "requiere_revision",
                )
            for name in ("legal_reference", "documentary_analysis"):
                if not present(getattr(condition, name)):
                    issue(field + "." + name, "campo_obligatorio")
            if not condition.evidence:
                issue(field + ".evidence", "evidencia_ausente")
            for index, item in enumerate(condition.evidence):
                for name in ("evidence_type", "reference"):
                    if not present(getattr(item, name)):
                        issue(
                            f"{field}.evidence.{index}.{name}", "evidencia_incompleta"
                        )
    # Sensitive IDs on this regime are already rejected by SpecialConditionV1.
    for field in (
        "purpose_description",
        "geolocation_data_description",
        "processing_operations",
        "duration_description",
        "notice_reference",
        "notice_version_reference",
        "notice_delivery_mechanism",
        "notice_content_analysis",
        "third_party_disclosure_description",
    ):
        text(field)
    if geo.scope is None:
        issue("scope", "alcance_ausente")
    for field, available in (
        (
            "data_category_codes",
            (
                {canonicalize_text_v1(i.category_code) for i in rat.data_categories}
                if rat
                else None
            ),
        ),
        (
            "data_subject_codes",
            (
                {canonicalize_text_v1(i.category_code) for i in rat.data_subjects}
                if rat
                else None
            ),
        ),
    ):
        values = (
            [canonicalize_text_v1(v) for v in getattr(geo.scope, field)]
            if geo.scope is not None
            else []
        )
        if geo.scope is not None:
            if not values:
                issue("scope." + field, "alcance_vacio")
            elif len(values) != len(set(values)) or (
                available is not None and not set(values).issubset(available)
            ):
                issue("scope." + field, "alcance_invalido", "requiere_revision")
        for name, item in (
            ("declarations.geolocalizacion", declaration),
            ("conditions.geolocalizacion_art16sexies", condition),
        ):
            if item is None:
                continue
            selected = [canonicalize_text_v1(v) for v in getattr(item, field)]
            if not selected:
                issue("special_conditions." + name + "." + field, "alcance_vacio")
            elif len(selected) != len(set(selected)) or (
                available is not None and not set(selected).issubset(available)
            ):
                issue(
                    "special_conditions." + name + "." + field,
                    "alcance_invalido",
                    "requiere_revision",
                )
            if values and selected and set(values) != set(selected):
                issue("scope." + field, "alcance_discordante", "requiere_revision")
    for field in (
        "information_clear",
        "information_sufficient",
        "information_timely",
        "data_types_disclosed",
        "purpose_disclosed",
        "duration_disclosed",
        "third_party_information_disclosed",
    ):
        response(field)
    factual = geo.value_added_third_party_transfer
    if factual is None:
        issue("value_added_third_party_transfer", "respuesta_ausente")
    else:
        if factual.answer == "pendiente":
            issue("value_added_third_party_transfer.answer", "respuesta_pendiente")
        if not present(factual.rationale):
            issue("value_added_third_party_transfer.rationale", "fundamento_ausente")
    applies = (
        None
        if factual is None or factual.answer == "pendiente"
        else factual.answer == "si"
    )
    for field in (
        "value_added_service_description",
        "third_party_recipient_description",
    ):
        state = (
            "sin_resolver"
            if applies is None
            else "aplicable" if applies else "no_aplicable"
        )
        applicability.append(GeolocationApplicabilityV1(field, state))
        if applies:
            text(field)
        elif applies is False and present(getattr(geo, field)):
            issue(field, "campo_residual", "requiere_revision")
    if not geo.evidence:
        issue("evidence", "evidencia_ausente")
    for index, item in enumerate(geo.evidence):
        for field in ("evidence_type", "reference"):
            if not present(getattr(item, field)):
                issue(f"evidence.{index}.{field}", "evidencia_incompleta")

    def order(item):
        parts = item.field.split(".")
        if parts[0] in (
            "rat_context_snapshot",
            "geolocation_assessment",
            "special_conditions",
        ):
            return (
                (
                    "rat_context_snapshot",
                    "geolocation_assessment",
                    "special_conditions",
                ).index(parts[0]),
                0,
                0,
                0,
            )
        index = list(GeolocationAssessmentV1.model_fields).index(parts[0])
        if parts[0] == "evidence" and len(parts) > 1:
            return (3, index, int(parts[1]), 0 if parts[2] == "evidence_type" else 1)
        if parts[0] == "scope" and len(parts) > 1:
            return (3, index, 0, 0 if parts[1] == "data_category_codes" else 1)
        return (3, index, 0, 0 if len(parts) == 1 or parts[1] == "answer" else 1)

    # Two comparisons may report the same scope discordance, keep one reason.
    issues = list(dict.fromkeys(issues))
    issues.sort(key=order)
    result = (
        "incompleto"
        if any(i.category == "incompleto" for i in issues)
        else "requiere_revision" if issues else "completo"
    )
    return GeolocationReadinessV1(result, tuple(issues), tuple(applicability))
