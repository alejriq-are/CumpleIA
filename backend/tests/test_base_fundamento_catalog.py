from dataclasses import replace

import pytest

from app.services import base_fundamento_catalog as catalog
from app.services.consentimiento import ConsentIssueV1, ConsentReadinessV1


def diagnose(basis, document=None, **overrides):
    return catalog.evaluate_base_document(
        **(
            dict(
                legal_basis=basis,
                justification="[FICTICIA] Fundamento",
                purpose="[FICTICIA] Finalidad",
                snapshot=None,
                document=document,
            )
            | overrides
        )
    )


@pytest.mark.parametrize(
    "basis,criterion",
    [
        ("consentimiento_art12", "consentimiento.otorgamiento"),
        ("obligaciones_economicas_art13a", "economica.obligacion"),
        ("obligacion_legal_art13b", "legal.norma"),
        ("contrato_precontractual_art13c", "contrato.relacion"),
        ("interes_legitimo_art13d", "lia.ponderacion"),
        ("defensa_derechos_art13e", "derechos.vinculo"),
    ],
)
def test_existing_evaluator_findings_link_to_catalog(basis, criterion):
    result = diagnose(basis, {})
    assert result["rule_set"] == "cumpleia.base_fundamento.v1"
    assert result["primary_form"] == catalog.BASES[basis].form
    assert criterion in {f["criterion_id"] for f in result["findings"]}
    assert all(f["criterion_id"] for f in result["findings"])
    assert all(a["criterion_id"] for a in result["applicability"])
    assert result["coverage_pending"] == list(catalog.COVERAGE_PENDING)


def test_pending_basis_does_not_evaluate_a_saved_alternative():
    result = diagnose(None, {"given_by": "titular"})
    assert result["primary_form"] is None
    assert result["evaluator_result"] is None
    assert any(f["code"] == "base_pendiente" for f in result["findings"])


def test_no_evidence_reference_remains_a_mapped_finding():
    result = diagnose("consentimiento_art12", {"given_by": "titular"})
    assert any(
        f["criterion_id"] == "base.respaldo"
        and f["code"] == "referencia_de_respaldo_ausente"
        for f in result["findings"]
    )


def test_unknown_evaluator_finding_stays_unclassified(monkeypatch):
    basis = "consentimiento_art12"
    result = ConsentReadinessV1(
        "incompleto",
        (ConsentIssueV1("answers.nuevo_criterio", "campo_obligatorio", "incompleto"),),
        (),
    )
    monkeypatch.setitem(
        catalog.BASES,
        basis,
        replace(
            catalog.BASES[basis],
            evaluate=lambda *_: result,
        ),
    )
    finding = next(
        f for f in diagnose(basis)["findings"] if f["field"] == "answers.nuevo_criterio"
    )
    assert finding["classification"] == "sin_clasificar"
    assert finding["criterion_id"] is None


def test_conditional_precontractual_request_tracks_route():
    result = diagnose("contrato_precontractual_art13c", {"route": "ejecucion_contrato"})
    request = next(
        a for a in result["applicability"] if a["field"] == "requested_by_holder"
    )
    assert request["criterion_id"] == "contrato.solicitud"
    assert request["applicability"] == "no_aplicable"
    result = diagnose(
        "contrato_precontractual_art13c", {"route": "medidas_precontractuales"}
    )
    request = next(
        a for a in result["applicability"] if a["field"] == "requested_by_holder"
    )
    assert request["applicability"] == "aplicable"
