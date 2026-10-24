from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.services import eipd
from app.services import special_conditions as special
from app.services.eipd_frontier_v2 import evaluate_eipd_frontier_v2
from app.services.eipd_resolution import EipdResolutionContextV1
from app.services.research_binding import bind_research_assessment_v1
from tests import test_services_research as research_cases

context = research_cases.context


@pytest.fixture
def frontier_context(context, negative_controls):
    document, rat, lia = context
    basis = "interes_legitimo_art13d"
    bound = bind_research_assessment_v1(document, rat, basis, lia)
    declarations = deepcopy(negative_controls["special_conditions"])
    for d in declarations["declarations"]:
        if (
            d["question_id"]
            == "fines_historicos_estadisticos_cientificos_investigacion"
        ):
            d["answer"] = "si"
    declarations["conditions"] = [
        dict(
            regime_id="investigacion_art16quinquies",
            authorization_route="regla_especifica",
            data_category_codes=["id"],
            data_subject_codes=["clientes"],
        )
    ]
    conditions = special.bind_special_conditions_v11(
        declarations, rat, basis, None, lia, *([None] * 9), research=bound
    )
    screening = eipd.bind_eipd_screening_v12(
        negative_controls["eipd_screening"],
        rat,
        lia,
        conditions,
        *([None] * 9),
        legal_basis=basis,
        research=bound,
    )
    value = {k: None for k in EipdResolutionContextV1.model_fields}
    value.update(
        rat_context_snapshot=rat,
        legal_basis=basis,
        lia_assessment=lia,
        special_conditions=conditions.model_dump(mode="json"),
        eipd_screening=screening.model_dump(mode="json"),
        research_assessment=bound.model_dump(mode="json"),
    )
    return value


def test_complete_research_stays_blocked(frontier_context):
    before = deepcopy(frontier_context)
    result = evaluate_eipd_frontier_v2(frontier_context)
    assert result.research.result == "completo"
    assert result.research_association.result == "vigente"
    assert result.special.context_current and result.screening.context_current
    assert result.route == "investigacion_no_sensible_adultos"
    assert not result.can_confirm and not result.is_frontier_prepared
    assert {
        "validador_no_implementado",
        "investigacion_confirmacion_bloqueada",
    }.issubset({i.code for i in result.issues})
    assert frontier_context == before
    assert result == evaluate_eipd_frontier_v2(frontier_context)


@pytest.mark.parametrize(
    "change",
    ["document", "binding", "null", "sensitive", "minor", "declaration", "scope"],
)
def test_discordance_and_obsolescence_remain_visible(frontier_context, change):
    ctx = frontier_context
    if change == "document":
        ctx["research_assessment"]["assessment"][
            "public_interest_analysis"
        ] += " cambiado"
    elif change == "binding":
        ctx["research_assessment"]["context_binding"]["context_hash"] = "a" * 64
    elif change == "null":
        ctx["research_assessment"] = None
    elif change == "sensitive":
        ctx["rat_context_snapshot"]["data_categories"][0]["is_sensitive"] = True
    elif change == "minor":
        ctx["rat_context_snapshot"]["data_subjects"][0]["includes_children"] = True
    elif change == "declaration":
        for d in ctx["special_conditions"]["declarations"]:
            if (
                d["question_id"]
                == "fines_historicos_estadisticos_cientificos_investigacion"
            ):
                d["answer"] = "no"
    else:
        ctx["special_conditions"]["conditions"][0]["data_category_codes"] = []
    before = deepcopy(ctx)
    result = evaluate_eipd_frontier_v2(ctx)
    assert not result.can_confirm and not result.is_frontier_prepared
    assert result.result == "requiere_revision"
    expected = {
        "document": "asociacion_documento_obsoleta",
        "binding": "asociacion_contexto_obsoleta",
        "null": "expediente_ausente",
        "sensitive": "ruta_sensible_no_preparada",
        "minor": "titulares_no_preparados",
        "declaration": "investigacion_declaracion_discordante",
        "scope": "investigacion_alcance_discordante",
    }
    assert expected[change] in {i.code for i in result.issues}
    if change in ("sensitive", "minor", "null"):
        assert result.route == "sin_resolver"
    assert ctx == before


def test_absent_and_unknown_context(frontier_context):
    result = evaluate_eipd_frontier_v2(None)
    assert (
        result.result == "incompleto"
        and result.route == "sin_resolver"
        and not result.can_confirm
    )
    for change in (
        dict(frontier_context, context_schema_version=99),
        dict(frontier_context, approved=True),
    ):
        with pytest.raises(ValidationError):
            evaluate_eipd_frontier_v2(change)
    missing = dict(frontier_context)
    missing.pop("research_assessment")
    with pytest.raises(ValidationError):
        evaluate_eipd_frontier_v2(missing)


def test_historical_associations_report_missing_research_coverage(frontier_context):
    ctx = frontier_context
    rat, lia, basis = (
        ctx["rat_context_snapshot"],
        ctx["lia_assessment"],
        ctx["legal_basis"],
    )
    original = ctx["special_conditions"]
    input_special = {k: v for k, v in original.items() if k != "context_binding"}
    old_special = special.bind_special_conditions_v10(
        input_special, rat, basis, None, lia, *([None] * 9)
    )
    input_screening = {
        k: v for k, v in ctx["eipd_screening"].items() if k != "context_binding"
    }
    old_screening = eipd.bind_eipd_screening_v11(
        input_screening, rat, lia, old_special, *([None] * 9)
    )
    ctx["special_conditions"] = old_special.model_dump(mode="json")
    ctx["eipd_screening"] = old_screening.model_dump(mode="json")
    result = evaluate_eipd_frontier_v2(ctx)
    assert not result.special.context_current and not result.screening.context_current
    coverage = [
        i for i in result.issues if i.code == "asociacion_investigacion_no_cubierta"
    ]
    assert any(i.field.startswith("special_conditions") for i in coverage)
    assert any(i.field.startswith("eipd_screening") for i in coverage)
    assert not result.can_confirm
