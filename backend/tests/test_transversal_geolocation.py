from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.services.eipd import bind_eipd_screening_v7
from app.services.licitud import evaluate_transversal_readiness_v1
from app.services.special_conditions import bind_special_conditions_v6


def state(geo, rat, controls):
    special = bind_special_conditions_v6(
        controls["special_conditions"],
        rat,
        "consentimiento_art12",
        None,
        None,
        None,
        None,
        None,
        None,
        geo,
    ).model_dump(mode="json")
    eipd = bind_eipd_screening_v7(
        controls["eipd_screening"], rat, None, special, None, None, None, None, geo
    ).model_dump(mode="json")
    return SimpleNamespace(
        health_assessment=None,
        sensitive_consent_assessment=None,
        legal_basis="consentimiento_art12",
        consent_assessment=None,
        lia_assessment=None,
        contract_assessment=None,
        legal_obligation_assessment=None,
        rights_defense_assessment=None,
        economic_obligations_assessment=None,
        geolocation_assessment=geo,
        special_conditions=special,
        eipd_screening=eipd,
    )


def test_geo_transversal_preparado_sin_mutar(
    complete_geolocation, complete_lia_context, geolocation_controls
):
    rat = complete_lia_context[1]
    draft = state(complete_geolocation, rat, geolocation_controls)
    before = deepcopy((vars(draft), rat))
    special, eipd, blockers = evaluate_transversal_readiness_v1(draft, rat)
    assert special.result == "regimenes_preparados" and special.detected_regimes == (
        "geolocalizacion_art16sexies",
    )
    assert eipd.result == "sin_supuestos_declarados" and not blockers
    assert (vars(draft), rat) == before


@pytest.mark.parametrize("index", range(5))
def test_geo_no_omite_eipd_positivo(
    complete_geolocation, complete_lia_context, geolocation_controls, index
):
    rat = complete_lia_context[1]
    geolocation_controls["eipd_screening"]["answers"][index]["answer"] = "si"
    draft = state(complete_geolocation, rat, geolocation_controls)
    special, eipd, blockers = evaluate_transversal_readiness_v1(draft, rat)
    assert special.result == "regimenes_preparados"
    assert eipd.result != "sin_supuestos_declarados"
    assert "screening_eipd_no_preparado" in {b["code"] for b in blockers}


@pytest.mark.parametrize(
    "question",
    [
        "datos_sensibles",
        "salud_perfil_biologico",
        "biometricos_identificacion_unica",
        "ninos_ninas",
        "adolescentes",
        "datos_sensibles_adolescentes_menores_16",
        "fines_historicos_estadisticos_cientificos_investigacion",
        "grupos_vulnerables",
    ],
)
def test_geo_no_omite_regimen_concurrente(
    complete_geolocation, complete_lia_context, geolocation_controls, question
):
    rat = complete_lia_context[1]
    d = next(
        d
        for d in geolocation_controls["special_conditions"]["declarations"]
        if d["question_id"] == question
    )
    d.update(answer="si", data_category_codes=["id"], data_subject_codes=["clientes"])
    draft = state(complete_geolocation, rat, geolocation_controls)
    special, _, blockers = evaluate_transversal_readiness_v1(draft, rat)
    assert special.result != "regimenes_preparados" and special.issues
    assert "condiciones_especiales_no_preparadas" in {b["code"] for b in blockers}


@pytest.mark.parametrize(
    "change", ["stale", "residual", "incomplete", "unimplemented_rule"]
)
def test_geo_barreras_restantes(
    complete_geolocation, complete_lia_context, geolocation_controls, change
):
    rat = complete_lia_context[1]
    draft = state(complete_geolocation, rat, geolocation_controls)
    if change == "stale":
        draft.geolocation_assessment["notes"] = "Cambio sin reaporte"
    elif change == "residual":
        d = next(
            d
            for d in geolocation_controls["special_conditions"]["declarations"]
            if d["question_id"] == "geolocalizacion"
        )
        d["answer"] = "no"
        geolocation_controls["special_conditions"]["conditions"] = []
        draft = state(complete_geolocation, rat, geolocation_controls)
    elif change == "incomplete":
        draft.geolocation_assessment["information_clear"] = {"answer": "pendiente"}
        draft = state(draft.geolocation_assessment, rat, geolocation_controls)
    else:
        geolocation_controls["special_conditions"]["conditions"].append(
            {
                "regime_id": "investigacion_art16quinquies",
                "authorization_route": "regla_especifica",
            }
        )
        draft = state(complete_geolocation, rat, geolocation_controls)
    special, eipd, blockers = evaluate_transversal_readiness_v1(draft, rat)
    assert blockers and special.result != "sin_regimenes_declarados"
    if change == "stale":
        assert not special.context_current and not eipd.context_current
    if change in ("incomplete", "unimplemented_rule"):
        assert "ruta_especial_pendiente" in {i.code for i in eipd.issues}
