import hashlib
import importlib.util
import json
import uuid
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from alembic.migration import MigrationContext
from alembic.operations import Operations
from app.schemas.licitud import (
    EipdScreeningDraftIn,
    EipdScreeningV1,
    LiaAssessmentV1,
    RatCanonicalContextV1,
    RatContextSnapshotV1,
)
from app.services.eipd import (
    bind_eipd_screening_v1,
    build_eipd_context_binding_hash_v1,
    evaluate_eipd_screening_v1,
)
from app.services.licitud import build_rat_context_hash_v1


@pytest.fixture
def lia_context():
    rat = {
        "purpose": "Gestión de clientes",
        "organization_role": "responsable",
        "data_categories": [
            {
                "category_code": "id",
                "category_name": "Identidad",
                "is_sensitive": False,
                "notes": None,
            }
        ],
        "data_subjects": [
            {
                "category_code": "clientes",
                "category_name": "Clientes",
                "includes_children": False,
                "includes_adolescents": False,
                "is_vulnerable_group": False,
                "notes": None,
            }
        ],
        "data_sources": [
            {"source_type": "titular", "description": None, "is_public_source": False}
        ],
        "retention": {"retention_rule": "5 años", "deletion_method": None},
        "automated_decisions": {"has_automated_decisions": False, "description": None},
        "systems": [],
        "third_parties": [],
        "international_transfers": [],
        "special_regimes": {
            "has_sensitive_data": False,
            "includes_children": False,
            "includes_adolescents": False,
            "has_vulnerable_groups": False,
        },
    }
    lia = {
        "purpose_and_interest": {
            "purpose_description": " Gestión DE clientes ",
            "legitimate_interest": "Interés documentado",
            "interest_holder": "responsable",
            "controller_benefit": "Beneficio",
            "interest_importance": "Importancia",
            "consequences_without_processing": "Consecuencias",
        },
        "necessity": {
            "contributes_to_purpose": {"answer": "si"},
            "linked_to_interest": {"answer": "si"},
            "achievable_without_personal_data": {"answer": "no"},
            "less_intrusive_alternative": {"answer": "no"},
            "fewer_data_possible": {"answer": "no"},
            "categories_necessary_and_relevant": {"answer": "si"},
            "necessity_analysis": "Necesidad",
            "proportionality_analysis": "Proporcionalidad",
            "alternatives_analysis": "Alternativas",
            "minimization_analysis": "Minimización",
        },
        "nature_and_scope": {"exclusively_professional_context": {"answer": "no"}},
        "reasonable_expectations": {
            "prior_relationship": {"answer": "no"},
            "significant_change_of_use": {"answer": "no"},
            "informed_at_direct_collection": {"answer": "si"},
            "foreseeable_purpose_and_method": {"answer": "si"},
            "innovative_processing": {"answer": "no"},
            "expectations_analysis": "Expectativas",
        },
        "impact": {
            "negative_effects": "Sin efectos adicionales identificados",
            "severity": "baja",
            "likelihood": "baja",
            "loss_of_control": {"answer": "no"},
            "intrusion_analysis": "Intrusión",
            "reasonable_opposition_likelihood": {"answer": "no"},
            "rights_and_freedoms_analysis": "Derechos",
            "transparently_explainable": {"answer": "si"},
            "relevant_unmitigated_impacts": {"answer": "no"},
            "impact_analysis": "Impacto",
        },
        "safeguards": {"safeguards_analysis": "No se proponen medidas adicionales"},
        "transparency_and_opposition": {
            "information_method": "Aviso",
            "interest_communication": "Explicación",
            "opposition_channel": "Portal",
            "opposition_procedure": "Procedimiento",
            "responsible_area": "Área",
        },
        "conclusion": {
            "balancing_summary": "Ponderación",
            "identified_interest": "Interés",
            "necessity_and_proportionality_result": "Resultado",
            "main_impacts": "Impactos",
            "relevant_safeguards": "Salvaguardas",
            "rights_protection_reasoning": "Razonamiento",
            "decision": "puede_basarse",
        },
    }
    return lia, rat


def test_binding_bytes_exactos_y_orden_de_claves(lia_context):
    lia, rat = lia_context
    material = {
        "rat_context_snapshot": RatContextSnapshotV1.model_validate(rat).model_dump(
            mode="json"
        ),
        "lia_assessment": LiaAssessmentV1.model_validate(lia).model_dump(mode="json"),
    }
    expected = hashlib.sha256(
        json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()
    original = deepcopy(lia_context)
    assert build_eipd_context_binding_hash_v1(rat, lia) == expected
    assert (
        build_eipd_context_binding_hash_v1(dict(reversed(list(rat.items()))), lia)
        == expected
    )
    assert lia_context == original
    assert bind_eipd_screening_v1({}, rat, lia).context_binding.hash == expected


def test_binding_detecta_hechos_excluidos_del_hash_canonico(lia_context):
    lia, rat = lia_context
    before = build_eipd_context_binding_hash_v1(rat, lia)
    canonical_before = build_rat_context_hash_v1(
        RatCanonicalContextV1.model_validate(rat)
    )
    rat["retention"]["deletion_method"] = "Borrado revisado"
    assert build_eipd_context_binding_hash_v1(rat, lia) != before
    assert (
        build_rat_context_hash_v1(RatCanonicalContextV1.model_validate(rat))
        == canonical_before
    )
    before = build_eipd_context_binding_hash_v1(rat, lia)
    lia["conclusion"]["balancing_summary"] = "Otra ponderación"
    assert build_eipd_context_binding_hash_v1(rat, lia) != before
    assert build_eipd_context_binding_hash_v1(
        rat, None
    ) != build_eipd_context_binding_hash_v1(rat, {})


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": 2},
        {"context_binding": {"hash": "a" * 64}},
        {"result": "sin_supuestos_declarados"},
        {"answers": [{"question_id": "desconocida", "answer": "no"}]},
        {
            "answers": [
                {
                    "question_id": "tratamiento_masivo_o_gran_escala",
                    "answer": "no_aplica",
                }
            ]
        },
        {
            "answers": [
                {
                    "question_id": "tratamiento_masivo_o_gran_escala",
                    "answer": "no",
                    "extra": 1,
                }
            ]
        },
        {
            "answers": [
                {"question_id": "tratamiento_masivo_o_gran_escala", "answer": "si"},
                {"question_id": "tratamiento_masivo_o_gran_escala", "answer": "no"},
            ]
        },
    ],
)
def test_entrada_screening_rechaza_valores_desconocidos(payload):
    with pytest.raises(ValidationError):
        EipdScreeningDraftIn.model_validate(payload)


def test_borradores_parciales_y_binding_persistido_obligatorio(lia_context):
    lia, rat = lia_context
    partial = {
        "answers": [
            {"question_id": "tratamiento_masivo_o_gran_escala", "answer": "pendiente"}
        ],
        "notes": " Texto factual ",
    }
    result = bind_eipd_screening_v1(partial, rat, lia)
    assert result.answers[0].rationale is None
    assert result.notes == " Texto factual "
    assert EipdScreeningV1.model_validate_json(result.model_dump_json()) == result
    with pytest.raises(ValidationError):
        EipdScreeningV1.model_validate(partial)
    with pytest.raises(ValidationError):
        EipdScreeningV1.model_validate(
            {**partial, "context_binding": {"hash": "A" * 64}}
        )


async def test_migracion_upgrade_downgrade_reupgrade_aislados(_session_factory):
    """Ejecuta DDL real en un schema transaccional, sin downgrade de datos locales."""
    path = Path(__file__).parents[1] / "alembic/versions/7c9e1a3b5d20_eipd_screening.py"
    spec = importlib.util.spec_from_file_location("eipd_migration_test", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    schema = "eipd_test_" + uuid.uuid4().hex
    async with _session_factory() as db:
        await db.execute(text(f'CREATE SCHEMA "{schema}"'))
        await db.execute(text(f'SET LOCAL search_path TO "{schema}", public'))
        await db.execute(
            text("CREATE TABLE legal_assessments (id integer primary key)")
        )
        await db.execute(text("INSERT INTO legal_assessments VALUES (1)"))
        connection = await db.connection()

        def run(connection, action):
            with Operations.context(MigrationContext.configure(connection)):
                action()

        await connection.run_sync(run, migration.upgrade)
        assert (
            await db.execute(
                text("SELECT eipd_screening IS NULL FROM legal_assessments")
            )
        ).scalar_one()
        with pytest.raises(IntegrityError):
            async with db.begin_nested():
                await db.execute(
                    text("UPDATE legal_assessments SET eipd_screening = '[]'::jsonb")
                )
        await db.execute(
            text("UPDATE legal_assessments SET eipd_screening = '{}'::jsonb")
        )
        await connection.run_sync(run, migration.downgrade)
        assert (
            await db.execute(
                text(
                    "SELECT count(*) FROM information_schema.columns WHERE table_schema = :schema AND table_name = 'legal_assessments' AND column_name = 'eipd_screening'"
                ),
                {"schema": schema},
            )
        ).scalar_one() == 0
        await connection.run_sync(run, migration.upgrade)
        assert (
            await db.execute(
                text("SELECT eipd_screening IS NULL FROM legal_assessments")
            )
        ).scalar_one()
        await db.rollback()


_EIPD_IDS = [
    "evaluacion_sistematica_automatizada_efectos_significativos",
    "tratamiento_masivo_o_gran_escala",
    "monitoreo_sistematico_zona_publica",
    "datos_protegidos_excepcion_consentimiento",
    "probable_alto_riesgo_contextual",
]


@pytest.fixture
def negative_screening(lia_context):
    lia, rat = lia_context
    screening = bind_eipd_screening_v1(
        {
            "answers": [
                {
                    "question_id": q,
                    "answer": "no",
                    "rationale": " Fundamento documentado ",
                }
                for q in _EIPD_IDS
            ]
        },
        rat,
        lia,
    )
    return screening, rat, lia


def test_screening_resuelto_puro_e_inmutable(negative_screening):
    screening, rat, lia = negative_screening
    original = deepcopy(negative_screening)
    result = evaluate_eipd_screening_v1(screening, rat, lia)
    assert result.result == "sin_supuestos_declarados"
    assert result.context_current
    assert result.can_continue
    assert result.issues == result.observations == ()
    assert negative_screening == original
    assert evaluate_eipd_screening_v1(screening.model_dump(), rat, lia) == result
    screening.answers.reverse()
    assert evaluate_eipd_screening_v1(screening, rat, lia) == result
    with pytest.raises(FrozenInstanceError):
        result.result = "requiere_eipd"


@pytest.mark.parametrize("question", _EIPD_IDS)
def test_cada_supuesto_afirmativo_fundado(negative_screening, question):
    screening, rat, lia = negative_screening
    rat["automated_decisions"]["has_automated_decisions"] = True
    draft = screening.model_dump(exclude={"context_binding"})
    next(item for item in draft["answers"] if item["question_id"] == question)[
        "answer"
    ] = "si"
    screening = bind_eipd_screening_v1(draft, rat, lia)
    result = evaluate_eipd_screening_v1(screening, rat, lia)
    assert result.result == "requiere_eipd"
    assert not result.can_continue
    assert result.issues[0].question_id == question
    assert result.issues[0].code == "supuesto_declarado"


@pytest.mark.parametrize("index", range(5))
@pytest.mark.parametrize(
    "change,code",
    [
        ("omit", "pregunta_omitida"),
        ("pending", "respuesta_pendiente"),
        ("empty", "fundamento_ausente"),
        ("positive_without_rationale", "fundamento_ausente"),
    ],
)
def test_cada_pregunta_y_fundamento_no_se_omiten(
    negative_screening, index, change, code
):
    screening, rat, lia = negative_screening
    rat["automated_decisions"]["has_automated_decisions"] = True
    data = screening.model_dump(exclude={"context_binding"})
    question = data["answers"][index]["question_id"]
    if change == "omit":
        data["answers"].pop(index)
    elif change == "pending":
        data["answers"][index]["answer"] = "pendiente"
    else:
        data["answers"][index]["rationale"] = " \t "
        if change == "positive_without_rationale":
            data["answers"][index]["answer"] = "si"
    result = evaluate_eipd_screening_v1(
        bind_eipd_screening_v1(data, rat, lia), rat, lia
    )
    assert result.result == "pendiente_revision"
    assert not result.can_continue
    assert any(
        item.code == code and item.question_id == question for item in result.issues
    )


def test_afirmativo_prevalece_sobre_faltantes_con_contexto_vigente(negative_screening):
    screening, rat, lia = negative_screening
    screening.answers[1].answer = "si"
    screening.answers[2].answer = "pendiente"
    screening.answers[2].rationale = None
    result = evaluate_eipd_screening_v1(screening, rat, lia)
    assert result.result == "requiere_eipd"
    assert [item.code for item in result.issues] == [
        "supuesto_declarado",
        "respuesta_pendiente",
        "fundamento_ausente",
    ]


@pytest.mark.parametrize("changed", ["rat", "lia"])
def test_contexto_desactualizado_conserva_disparadores_historicos(
    negative_screening, changed
):
    screening, rat, lia = negative_screening
    screening.answers[1].answer = "si"
    if changed == "rat":
        rat["retention"]["deletion_method"] = "Nueva regla"
    else:
        lia["conclusion"]["balancing_summary"] = "Nueva valoración"
    result = evaluate_eipd_screening_v1(screening, rat, lia)
    assert result.result == "pendiente_revision"
    assert not result.context_current
    assert result.issues[0].code == "contexto_desactualizado"
    assert result.issues[1].code == "supuesto_declarado"


def test_automatizacion_no_documentada_requiere_revision(negative_screening):
    screening, rat, lia = negative_screening
    screening.answers[0].answer = "si"
    result = evaluate_eipd_screening_v1(screening, rat, lia)
    assert result.result == "pendiente_revision"
    assert result.context_current
    assert [item.code for item in result.issues] == [
        "supuesto_declarado",
        "automatizacion_no_documentada",
    ]
    # Una declaración negativa no contradice por sí sola automatización RAT:
    # el supuesto contiene también otros hechos no determinados por ese flag.
    rat["automated_decisions"]["has_automated_decisions"] = True
    data = screening.model_dump(exclude={"context_binding"})
    data["answers"][0]["answer"] = "no"
    result = evaluate_eipd_screening_v1(
        bind_eipd_screening_v1(data, rat, lia), rat, lia
    )
    assert result.result == "sin_supuestos_declarados"


def test_valoraciones_lia_altas_son_observaciones_separadas(negative_screening):
    screening, rat, lia = negative_screening
    lia["impact"]["severity"] = lia["impact"]["likelihood"] = "alta"
    rebound = bind_eipd_screening_v1(
        screening.model_dump(exclude={"context_binding"}), rat, lia
    )
    result = evaluate_eipd_screening_v1(rebound, rat, lia)
    assert result.result == "sin_supuestos_declarados"
    assert result.issues == ()
    assert [item.field for item in result.observations] == [
        "lia_assessment.impact.severity",
        "lia_assessment.impact.likelihood",
    ]


@pytest.mark.parametrize("missing", ["screening", "snapshot", "both"])
def test_screening_o_snapshot_ausente(negative_screening, missing):
    screening, rat, lia = negative_screening
    screening.answers[1].answer = "si"
    result = evaluate_eipd_screening_v1(
        None if missing != "snapshot" else screening,
        None if missing != "screening" else rat,
        lia,
    )
    assert result.result == "pendiente_revision"
    assert not result.context_current
    assert not result.can_continue


def test_lia_no_es_obligatoria_para_screening(negative_screening):
    screening, rat, _ = negative_screening
    screening = bind_eipd_screening_v1(
        screening.model_dump(exclude={"context_binding"}), rat, None
    )
    assert (
        evaluate_eipd_screening_v1(screening, rat, None).result
        == "sin_supuestos_declarados"
    )


def test_inputs_invalidos_no_se_ocultan_por_ausencias(negative_screening):
    screening, rat, _ = negative_screening
    with pytest.raises(ValidationError):
        evaluate_eipd_screening_v1(None, {}, None)
    with pytest.raises(ValidationError):
        evaluate_eipd_screening_v1(None, None, {"schema_version": 2})
    with pytest.raises(ValidationError):
        evaluate_eipd_screening_v1({"schema_version": 2}, None, None)
    screening.answers[0].answer = "no_aplica"
    with pytest.raises(ValidationError):
        evaluate_eipd_screening_v1(screening, rat, None)


@pytest.mark.parametrize(
    "invalid",
    [
        {"declarations": [{"question_id": "datos_sensibles", "answer": "no_aplica"}]},
        {"declarations": [{"question_id": "desconocida", "answer": "no"}]},
        {"context_binding": {"schema_version": 1, "hash": "a" * 64}},
        {
            "conditions": [
                {
                    "regime_id": "biometricos_art16ter",
                    "sensitive_condition_id": "consentimiento_expreso_art16",
                }
            ]
        },
        {"declarations": [{"question_id": "datos_sensibles", "answer": "no"}] * 2},
    ],
)
def test_contrato_especial_rechaza_declaraciones_invalidas(invalid):
    from app.schemas.licitud import SpecialConditionsDraftIn

    with pytest.raises(ValidationError):
        SpecialConditionsDraftIn.model_validate(invalid)


def test_asociacion_especial_y_compatibilidad_eipd(negative_screening):
    from app.services.eipd import bind_eipd_screening_v2
    from app.services.special_conditions import bind_special_conditions_v1

    screening, rat, lia = negative_screening
    special = bind_special_conditions_v1({}, rat, None, None, lia)
    assert special == bind_special_conditions_v1({}, rat, None, None, lia)
    assert (
        special.context_binding.hash
        != bind_special_conditions_v1(
            {}, rat, "consentimiento_art12", None, lia
        ).context_binding.hash
    )
    old_binding = screening.context_binding.model_dump()
    result = evaluate_eipd_screening_v1(screening, rat, lia, special)
    assert result.result == "pendiente_revision"
    assert result.issues[0].code == "asociacion_especial_no_cubierta"
    assert screening.context_binding.model_dump() == old_binding
    current = bind_eipd_screening_v2(
        screening.model_dump(exclude={"context_binding"}), rat, lia, special
    )
    assert current.context_binding.schema_version == 2
    assert evaluate_eipd_screening_v1(current, rat, lia, special).context_current
    special.notes = "Cambio documental"
    assert not evaluate_eipd_screening_v1(current, rat, lia, special).context_current


def test_alcance_especial_fuera_del_rat(negative_screening):
    from app.services.special_conditions import bind_special_conditions_v1

    _, rat, lia = negative_screening
    with pytest.raises(ValueError):
        bind_special_conditions_v1(
            {
                "declarations": [
                    {
                        "question_id": "datos_sensibles",
                        "answer": "pendiente",
                        "data_category_codes": ["fuera_del_rat"],
                    }
                ]
            },
            rat,
            None,
            None,
            lia,
        )


@pytest.fixture
def negative_special(negative_screening):
    from typing import get_args

    from app.schemas.licitud import SpecialQuestionIdV1
    from app.services.special_conditions import bind_special_conditions_v1

    _, rat, _ = negative_screening
    rat["special_regimes"] = dict.fromkeys(rat["special_regimes"], False)
    data = {
        "declarations": [
            {"question_id": q, "answer": "no", "rationale": "Revisado"}
            for q in get_args(SpecialQuestionIdV1)
        ]
    }
    return (
        bind_special_conditions_v1(data, rat, None, None, None).model_dump(mode="json"),
        rat,
    )


def test_preparacion_especial_negativa_determinista(negative_special):
    from copy import deepcopy

    from app.services.special_conditions import evaluate_special_conditions_v1

    special, rat = negative_special
    before = deepcopy(special)
    a = evaluate_special_conditions_v1(special, rat, None, None, None)
    special["declarations"].reverse()
    b = evaluate_special_conditions_v1(special, rat, None, None, None)
    assert a == b
    assert a.result == "sin_regimenes_declarados"
    assert a.context_current and not a.detected_regimes
    special["declarations"].reverse()
    assert special == before


@pytest.mark.parametrize(
    "change,code,result",
    [
        ("omitida", "pregunta_omitida", "incompleto"),
        ("pendiente", "respuesta_pendiente", "incompleto"),
        ("fundamento", "fundamento_ausente", "incompleto"),
        ("rat", "discordancia_rat", "requiere_revision"),
        ("binding", "contexto_desactualizado", "requiere_revision"),
        ("residual", "condicion_residual", "requiere_revision"),
    ],
)
def test_preparacion_especial_motivos(negative_special, change, code, result):
    from app.services.special_conditions import evaluate_special_conditions_v1

    special, rat = negative_special
    if change == "omitida":
        special["declarations"].pop()
    elif change == "pendiente":
        special["declarations"][0]["answer"] = "pendiente"
    elif change == "fundamento":
        special["declarations"][0]["rationale"] = " "
    elif change == "rat":
        rat["special_regimes"]["has_vulnerable_groups"] = True
    elif change == "binding":
        special["context_binding"]["hash"] = "0" * 64
    elif change == "residual":
        special["conditions"] = [{"regime_id": "sensibles_art16"}]
    evaluated = evaluate_special_conditions_v1(special, rat, None, None, None)
    assert evaluated.result == result
    assert code in [i.code for i in evaluated.issues]


def test_preparacion_especial_varios_regimenes_y_precedencia(negative_special):
    from app.services.special_conditions import evaluate_special_conditions_v1

    special, rat = negative_special
    for d in special["declarations"]:
        if d["question_id"] in ("datos_sensibles", "geolocalizacion"):
            d["answer"] = "si"
    result = evaluate_special_conditions_v1(special, rat, None, None, None)
    assert result.result == "incompleto"
    assert result.detected_regimes == ("geolocalizacion_art16sexies", "sensibles_art16")
    assert "validador_no_implementado" in [i.code for i in result.issues]
    special["conditions"] = [
        {
            "regime_id": regime,
            "authorization_route": "consentimiento",
            "uses_consent_assessment": True,
        }
        for regime in result.detected_regimes
    ]
    result = evaluate_special_conditions_v1(special, rat, None, None, None)
    assert result.result == "incompleto"
    assert any(i.category == "requiere_revision" for i in result.issues)
    assert "consentimiento_referenciado_ausente" in [i.code for i in result.issues]


def test_cruce_adolescente_no_se_infiere(negative_special):
    from app.services.special_conditions import evaluate_special_conditions_v1

    special, rat = negative_special
    rat["special_regimes"].update(has_sensitive_data=True, includes_adolescents=True)
    result = evaluate_special_conditions_v1(special, rat, None, None, None)
    assert not any(
        i.question_id == "datos_sensibles_adolescentes_menores_16"
        for i in result.issues
    )
    for d in special["declarations"]:
        if d["question_id"] == "datos_sensibles_adolescentes_menores_16":
            d["answer"] = "si"
    result = evaluate_special_conditions_v1(special, rat, None, None, None)
    assert "subconjunto_edad_no_documentado" in [i.code for i in result.issues]


def test_preparacion_especial_ausencia_y_contrato(negative_special):
    from app.services.special_conditions import evaluate_special_conditions_v1

    special, rat = negative_special
    assert (
        evaluate_special_conditions_v1(None, rat, None, None, None).result
        == "incompleto"
    )
    assert (
        evaluate_special_conditions_v1(special, None, None, None, None).result
        == "incompleto"
    )
    with pytest.raises(ValidationError):
        evaluate_special_conditions_v1(None, None, None, {"schema_version": 2}, None)


@pytest.mark.parametrize(
    "question,code",
    [
        ("salud_perfil_biologico", "clasificacion_sensible_incoherente"),
        ("biometricos_identificacion_unica", "clasificacion_sensible_incoherente"),
        (
            "datos_sensibles_adolescentes_menores_16",
            "cruce_sensible_adolescente_incoherente",
        ),
        ("grupos_vulnerables", "factor_vulnerabilidad"),
    ],
)
def test_preparacion_especial_positivas_incoherentes(negative_special, question, code):
    from app.services.special_conditions import evaluate_special_conditions_v1

    special, rat = negative_special
    for d in special["declarations"]:
        if d["question_id"] == question:
            d["answer"] = "si"
    result = evaluate_special_conditions_v1(special, rat, None, None, None)
    assert code in [i.code for i in result.issues]


def test_preparacion_especial_alcance_y_referencia_incoherentes(negative_special):
    from app.services.special_conditions import evaluate_special_conditions_v1

    special, rat = negative_special
    special["declarations"][0]["data_category_codes"] = ["fuera"]
    special["conditions"] = [
        {
            "regime_id": "sensibles_art16",
            "authorization_route": "consentimiento",
            "uses_consent_assessment": False,
        }
    ]
    result = evaluate_special_conditions_v1(special, rat, None, None, None)
    assert result.result == "incompleto"
    assert {"alcance_invalido", "referencia_consentimiento_incoherente"}.issubset(
        {i.code for i in result.issues}
    )


@pytest.mark.parametrize(
    "route,answer,codes",
    [
        (
            "excepcion_legal",
            "no",
            {"excepcion_especial_no_validada", "excepcion_consentimiento_discordante"},
        ),
        ("excepcion_legal", "si", {"excepcion_especial_no_validada"}),
        (
            "excepcion_legal",
            "pendiente",
            {"excepcion_especial_no_validada", "respuesta_pendiente"},
        ),
        (None, "no", {"ruta_especial_pendiente"}),
        ("regla_especifica", "no", {"ruta_especial_pendiente"}),
        ("consentimiento", "si", {"excepcion_consentimiento_no_documentada"}),
        ("consentimiento", "no", {"ruta_especial_pendiente"}),
    ],
)
def test_contraste_eipd_rutas_propuestas(negative_screening, route, answer, codes):
    from copy import deepcopy

    from app.services.eipd import bind_eipd_screening_v2
    from app.services.special_conditions import bind_special_conditions_v1

    screening, rat, lia = negative_screening
    data = screening.model_dump(exclude={"context_binding"})
    for item in data["answers"]:
        if item["question_id"] == "datos_protegidos_excepcion_consentimiento":
            item["answer"] = answer
    special = bind_special_conditions_v1(
        {
            "conditions": [
                {"regime_id": "sensibles_art16", "authorization_route": route}
            ]
        },
        rat,
        None,
        None,
        lia,
    )
    screening = bind_eipd_screening_v2(data, rat, lia, special)
    before = deepcopy(screening.model_dump())
    result = evaluate_eipd_screening_v1(screening, rat, lia, special)
    assert result.context_current
    assert codes.issubset({i.code for i in result.issues})
    assert result.result == (
        "pendiente_revision" if codes else "sin_supuestos_declarados"
    )
    assert screening.model_dump() == before
    if answer == "si":
        assert "supuesto_declarado" in {i.code for i in result.issues}


def test_contraste_eipd_varias_rutas_y_contexto_obsoleto(negative_screening):
    from app.services.eipd import bind_eipd_screening_v2
    from app.services.special_conditions import bind_special_conditions_v1

    screening, rat, lia = negative_screening
    special = bind_special_conditions_v1(
        {
            "conditions": [
                {
                    "regime_id": "sensibles_art16",
                    "authorization_route": "excepcion_legal",
                },
                {"regime_id": "biometricos_art16ter", "authorization_route": None},
            ]
        },
        rat,
        None,
        None,
        lia,
    )
    screening = bind_eipd_screening_v2(
        screening.model_dump(exclude={"context_binding"}), rat, lia, special
    )
    rat["purpose"] += " modificado"
    result = evaluate_eipd_screening_v1(screening, rat, lia, special)
    assert result.result == "pendiente_revision"
    assert {
        "contexto_desactualizado",
        "ruta_especial_pendiente",
        "excepcion_especial_no_validada",
        "excepcion_consentimiento_discordante",
    }.issubset({i.code for i in result.issues})
    special.conditions.reverse()
    assert (
        evaluate_eipd_screening_v1(screening, rat, lia, special).issues == result.issues
    )


@pytest.mark.parametrize("special_version,eipd_version", [(1, 1), (1, 2), (2, 3)])
def test_asociaciones_contractuales_versionadas(
    negative_screening, negative_controls, special_version, eipd_version
):
    from app.services.eipd import (
        bind_eipd_screening_v1,
        bind_eipd_screening_v2,
        bind_eipd_screening_v3,
    )
    from app.services.special_conditions import (
        bind_special_conditions_v1,
        bind_special_conditions_v2,
        evaluate_special_conditions_v1,
    )

    screening, rat, lia = negative_screening
    rat["special_regimes"] = dict.fromkeys(rat["special_regimes"], False)
    contract = {"route": "ejecucion_contrato", "notes": "Documento factual"}
    special = (
        bind_special_conditions_v1(
            negative_controls["special_conditions"], rat, None, None, lia
        )
        if special_version == 1
        else bind_special_conditions_v2(
            negative_controls["special_conditions"], rat, None, None, lia, contract
        )
    )
    data = screening.model_dump(exclude={"context_binding"})
    eipd = (
        bind_eipd_screening_v1(data, rat, lia)
        if eipd_version == 1
        else (
            bind_eipd_screening_v2(data, rat, lia, special)
            if eipd_version == 2
            else bind_eipd_screening_v3(data, rat, lia, special, contract)
        )
    )
    a = evaluate_special_conditions_v1(special, rat, None, None, lia, contract)
    b = evaluate_eipd_screening_v1(eipd, rat, lia, special, contract)
    assert a.context_current == (special_version == 2)
    assert b.context_current == (eipd_version == 3)
    if eipd_version < 3:
        assert "asociacion_contractual_no_cubierta" in {i.code for i in b.issues}
    contract["notes"] = "Cambió"
    assert not evaluate_special_conditions_v1(
        special, rat, None, None, lia, contract
    ).context_current
    assert not evaluate_eipd_screening_v1(
        eipd, rat, lia, special, contract
    ).context_current


@pytest.mark.parametrize(
    "special_version,eipd_version", [(1, 1), (1, 2), (2, 3), (3, 4)]
)
def test_asociaciones_obligacion_legal_versionadas(
    negative_screening, negative_controls, special_version, eipd_version
):
    from app.services.eipd import (
        bind_eipd_screening_v1,
        bind_eipd_screening_v2,
        bind_eipd_screening_v3,
        bind_eipd_screening_v4,
    )
    from app.services.special_conditions import (
        bind_special_conditions_v1,
        bind_special_conditions_v2,
        bind_special_conditions_v3,
        evaluate_special_conditions_v1,
    )

    screening, rat, lia = negative_screening
    rat["special_regimes"] = dict.fromkeys(rat["special_regimes"], False)
    legal = {"route": "tratamiento_dispuesto_por_ley", "notes": "Referencia factual"}
    bind_special = {
        1: lambda: bind_special_conditions_v1(
            negative_controls["special_conditions"], rat, None, None, lia
        ),
        2: lambda: bind_special_conditions_v2(
            negative_controls["special_conditions"], rat, None, None, lia, None
        ),
        3: lambda: bind_special_conditions_v3(
            negative_controls["special_conditions"], rat, None, None, lia, None, legal
        ),
    }
    special = bind_special[special_version]()
    data = screening.model_dump(exclude={"context_binding"})
    bind_eipd = {
        1: lambda: bind_eipd_screening_v1(data, rat, lia),
        2: lambda: bind_eipd_screening_v2(data, rat, lia, special),
        3: lambda: bind_eipd_screening_v3(data, rat, lia, special, None),
        4: lambda: bind_eipd_screening_v4(data, rat, lia, special, None, legal),
    }
    screening = bind_eipd[eipd_version]()
    a = evaluate_special_conditions_v1(special, rat, None, None, lia, None, legal)
    b = evaluate_eipd_screening_v1(screening, rat, lia, special, None, legal)
    assert a.context_current == (special_version == 3)
    assert b.context_current == (eipd_version == 4)
    if special_version < 3:
        assert "asociacion_obligacion_legal_no_cubierta" in {i.code for i in a.issues}
    if eipd_version < 4:
        assert "asociacion_obligacion_legal_no_cubierta" in {i.code for i in b.issues}
    legal["notes"] = "Otra revisión"
    assert not evaluate_special_conditions_v1(
        special, rat, None, None, lia, None, legal
    ).context_current
    assert not evaluate_eipd_screening_v1(
        screening, rat, lia, special, None, legal
    ).context_current


@pytest.mark.parametrize(
    "special_version,eipd_version", [(1, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
)
def test_asociaciones_derechos_versionadas(
    negative_screening, negative_controls, special_version, eipd_version
):
    from app.services import eipd as e
    from app.services import special_conditions as s

    screening, rat, lia = negative_screening
    rat["special_regimes"] = dict.fromkeys(rat["special_regimes"], False)
    rights = {"route": "defensa_derecho", "notes": "Documento factual"}
    args = [negative_controls["special_conditions"], rat, None, None, lia]
    if special_version >= 2:
        args.append(None)
    if special_version >= 3:
        args.append(None)
    if special_version >= 4:
        args.append(rights)
    special = getattr(s, f"bind_special_conditions_v{special_version}")(*args)
    args = [screening.model_dump(exclude={"context_binding"}), rat, lia]
    if eipd_version >= 2:
        args.append(special)
    if eipd_version >= 3:
        args.append(None)
    if eipd_version >= 4:
        args.append(None)
    if eipd_version >= 5:
        args.append(rights)
    screening = getattr(e, f"bind_eipd_screening_v{eipd_version}")(*args)
    a = s.evaluate_special_conditions_v1(
        special, rat, None, None, lia, None, None, rights
    )
    b = e.evaluate_eipd_screening_v1(screening, rat, lia, special, None, None, rights)
    assert a.context_current == (special_version == 4)
    assert b.context_current == (eipd_version == 5)
    if special_version < 4:
        assert "asociacion_derechos_no_cubierta" in {i.code for i in a.issues}
    if eipd_version < 5:
        assert "asociacion_derechos_no_cubierta" in {i.code for i in b.issues}
    rights["notes"] = "Cambio factual"
    assert not s.evaluate_special_conditions_v1(
        special, rat, None, None, lia, None, None, rights
    ).context_current
    assert not e.evaluate_eipd_screening_v1(
        screening, rat, lia, special, None, None, rights
    ).context_current
