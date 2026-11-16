"""Matrix boundaries, immutable-contract compatibility and conservative residuals."""

import base64
from copy import deepcopy
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.assessment_support import AnnexSave, RiskMethodology
from app.services.assessment_support import MATRIX, decode_annex, evaluate

DOC = {
    "risks": [{"risk_id": "R1"}, {"risk_id": "R2"}],
    "measures": [
        {
            "measure_id": "M1",
            "risk_ids": ["R1"],
            "implemented": {"answer": "si"},
            "evidence": [{"reference": "SIMULADA-M1"}],
        }
    ],
}


def analysis():
    return dict(
        horizon="12 meses",
        risks=[
            dict(
                risk_id="R1",
                harm="PRUEBA discriminacion",
                inherent=dict(probability=1, impact=4, rationale="PRUEBA grave"),
                projected=dict(probability=1, impact=2, rationale="PRUEBA estimacion"),
            )
        ],
    )


def test_matrix_covers_all_pairs_and_critical_impact_is_not_low():
    assert len(MATRIX) == 4 and all(len(row) == 4 for row in MATRIX)
    for probability in range(1, 5):
        for impact in range(1, 5):
            data = analysis()
            data["risks"][0]["inherent"].update(probability=probability, impact=impact)
            out = evaluate(RiskMethodology.model_validate(data), DOC)
            assert out["risks"][0]["inherent"] == MATRIX[probability - 1][impact - 1]
            assert out["unresolved"] and not out["can_confirm"]
    assert MATRIX[0][3] == "alto"


@pytest.mark.parametrize("rank", [True, 0, 5, 1.5, "2"])
def test_rank_rejects_bool_and_out_of_scale(rank):
    data = analysis()
    data["risks"][0]["inherent"]["probability"] = rank
    with pytest.raises(ValidationError):
        RiskMethodology.model_validate(data)


def test_actual_residual_requires_verified_implemented_evidenced_controls():
    data = analysis()
    data["risks"][0]["residual"] = dict(
        probability=1, impact=2, rationale="PRUEBA verificacion"
    )
    with pytest.raises(HTTPException):
        evaluate(RiskMethodology.model_validate(data), DOC)
    data["controls"] = [
        dict(
            measure_id="M1",
            status="verificada",
            dimension="impacto",
            effectiveness="parcial",
            rationale="PRUEBA eficacia",
            evidence_references=["SIMULADA-M1"],
        )
    ]
    assert (
        evaluate(RiskMethodology.model_validate(data), DOC)["risks"][0]["residual"]
        == "bajo"
    )
    for change in [
        {"status": "propuesta"},
        {"dimension": "probabilidad"},
        {"effectiveness": "insuficiente"},
        {"evidence_references": ["AJENA"]},
        {"rationale": " "},
    ]:
        invalid = deepcopy(data)
        invalid["controls"][0].update(change)
        with pytest.raises(HTTPException):
            evaluate(RiskMethodology.model_validate(invalid), DOC)
    doc = deepcopy(DOC)
    doc["measures"][0]["implemented"]["answer"] = "pendiente"
    with pytest.raises(HTTPException):
        evaluate(RiskMethodology.model_validate(data), doc)


@pytest.mark.parametrize(
    "change",
    [
        {"harm": ""},
        {"inherent": {"probability": 2, "impact": 3, "rationale": " "}},
        {"review_on": "2026-02-30"},
        {"risk_id": "R99"},
    ],
)
def test_rejects_unfounded_or_foreign_risk(change):
    data = analysis()
    data["risks"][0].update(change)
    with pytest.raises(HTTPException):
        evaluate(RiskMethodology.model_validate(data), DOC)


def test_annex_bytes_and_closed_fields():
    values = dict(
        data_kind="ficticios",
        request_id=str(uuid4()),
        reference="SIMULADA-A",
        filename="ensayo.txt",
        description="PRUEBA",
        section="riesgos",
        content_base64=base64.b64encode(b"PRUEBA").decode(),
    )
    assert decode_annex(AnnexSave.model_validate(values)) == (b"PRUEBA", "text/plain")
    for patch in [
        {"filename": "../ensayo.txt"},
        {"filename": "ensayo.pdf"},
        {"filename": "ensayo.html"},
        {"content_base64": "!!!!"},
    ]:
        with pytest.raises(HTTPException):
            decode_annex(AnnexSave.model_validate(values | patch))
    for patch in [{"data_kind": "reales"}, {"can_confirm": True}]:
        with pytest.raises(ValidationError):
            AnnexSave.model_validate(values | patch)
