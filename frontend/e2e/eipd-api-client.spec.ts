import { test, expect } from "@playwright/test";
import { ApiError } from "../lib/api/client";
import { eipdReviewApi, type EipdNegativeReviewIn } from "../lib/api/eipd-review";

const scope = {
  token: "TEST: token sintetico",
  organizationId: "a0000000-0000-0000-0000-000000000001",
  treatmentId: "a0000000-0000-0000-0000-000000000002",
  assessmentId: "a0000000-0000-0000-0000-000000000003",
};
const rid = "a0000000-0000-0000-0000-000000000004";
const metadata = {
  metadata_schema_version: 1,
  resolution_binding_version: 2,
  context_schema_version: 2,
  research_coverage: "contexto_v2",
  document_hash: "a".repeat(64),
  context_hash: "b".repeat(64),
  research_material_hash: null,
};
function eventBody(version: 2 | 3 = 2) {
  return {
    response_schema_version: version,
    id: rid,
    organization_id: scope.organizationId,
    assessment_id: scope.assessmentId,
    decision: "requiere_cambios",
    rationale: "TEST: revisar expediente",
    review_reference: "TEST: REV159",
    document_hash: metadata.document_hash,
    context_hash: metadata.context_hash,
    created_by: "a0000000-0000-0000-0000-000000000005",
    created_at: "2026-10-09T00:00:00Z",
    policy_version: 1,
    policy_reference: "TEST: politica",
    policy_hash: "c".repeat(64),
    review_context_metadata: metadata,
  };
}
function readiness() {
  const negative = { prerequisites_met: true, context_metadata: metadata, issues: [] };
  return {
    assessment_id: scope.assessmentId,
    status: "borrador",
    eipd_controls_v3: {
      evaluation_version: 3,
      can_confirm: false,
      review_context_metadata_status: "vigente",
      policy: {
        sources_status: "pendiente",
        acceptance_status: "pendiente",
        activation: "deshabilitada",
      },
      review_prerequisites_v3: {
        evaluation_version: 3,
        evaluation_scope: "requisitos_documentales",
        authorizes_action: false,
        can_confirm: false,
        requiere_cambios: negative,
        no_continuar: negative,
        continuar: {
          prerequisites_met: false,
          context_metadata: metadata,
          issues: [
            {
              stage: "research",
              field: "research_assessment",
              code: "investigacion_confirmacion_bloqueada",
              category: "requiere_revision",
              question_id: null,
            },
          ],
        },
      },
    },
  };
}
async function withFetch(
  body: unknown,
  action: (calls: { url: string; options: RequestInit }[]) => Promise<void>,
  status = 200
) {
  const original = globalThis.fetch;
  const calls: { url: string; options: RequestInit }[] = [];
  globalThis.fetch = async (input, init) => {
    calls.push({ url: String(input), options: init ?? {} });
    return new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  };
  try {
    await action(calls);
  } finally {
    globalThis.fetch = original;
  }
}

test("consulta usa sesion/tenant sin cache y no convierte preparacion en permiso", async () => {
  await withFetch(readiness(), async (calls) => {
    const result = await eipdReviewApi.preparation(scope);
    expect(result.review_prerequisites_v3?.requiere_cambios.prerequisites_met).toBe(true);
    expect(result.review_prerequisites_v3?.authorizes_action).toBe(false);
    expect(result.review_prerequisites_v3?.continuar.prerequisites_met).toBe(false);
    expect(calls[0].url).toContain(
      `/treatments/${scope.treatmentId}/assessments/${scope.assessmentId}/readiness`
    );
    expect(calls[0].options.headers).toMatchObject({
      Authorization: `Bearer ${scope.token}`,
      "X-Organization-Id": scope.organizationId,
    });
    expect(calls[0].options.cache).toBe("no-store");
    expect(calls[0].options.method).toBe("GET");
    expect(calls[0].options.body).toBeUndefined();
  });
  await withFetch(
    { assessment_id: scope.assessmentId, status: "borrador", eipd_controls_v3: null },
    async () => {
      expect((await eipdReviewApi.preparation(scope)).review_prerequisites_v3).toBeNull();
    }
  );
});

test("respuestas con autoridad o metadata incoherente se rechazan", async () => {
  const value = readiness();
  value.eipd_controls_v3.review_prerequisites_v3.authorizes_action = true;
  await withFetch(value, async () => {
    await expect(eipdReviewApi.preparation(scope)).rejects.toThrow("incompatible");
  });
  await withFetch(
    { ...eventBody(3), review_context_metadata: { ...metadata, context_hash: "c".repeat(64) } },
    async () => {
      await expect(eipdReviewApi.event(scope, rid)).rejects.toThrow("incompatible");
    }
  );
  await withFetch({ ...eventBody(3), organization_id: scope.treatmentId }, async () => {
    await expect(eipdReviewApi.event(scope, rid)).rejects.toThrow("incompatible");
  });
});

test("motivos malformados se rechazan antes de presentarlos", async () => {
  const value = readiness();
  value.eipd_controls_v3.review_prerequisites_v3.continuar.issues[0].code = {} as unknown as string;
  await withFetch(value, async () => {
    await expect(eipdReviewApi.preparation(scope)).rejects.toThrow("incompatible");
  });
});

test("lectura historica conserva ausencia sin inferir identidad", async () => {
  const value = {
    ...eventBody(3),
    review_context_metadata: null,
    policy_version: null,
    policy_reference: null,
    policy_hash: null,
  };
  await withFetch(value, async (calls) => {
    const result = await eipdReviewApi.event(scope, rid);
    expect(result.review_context_metadata).toBeNull();
    expect(result.policy_hash).toBeNull();
    expect(calls[0].url).toContain(`/eipd-resolution/reviews/${rid}/v3`);
    expect(calls[0].options.cache).toBe("no-store");
  });
});

test("escritura negativa envia solo campos humanos a ruta versionada", async () => {
  const request: EipdNegativeReviewIn = {
    decision: "requiere_cambios",
    rationale: "TEST: revisar expediente",
    review_reference: "TEST: REV159",
  };
  await withFetch(
    eventBody(),
    async (calls) => {
      const result = await eipdReviewApi.recordNegative(scope, request);
      expect(result.review_context_metadata?.context_schema_version).toBe(2);
      expect(calls[0].options.method).toBe("POST");
      expect(JSON.parse(String(calls[0].options.body))).toEqual(request);
      expect(calls[0].url).toContain("/eipd-resolution/reviews/v2");
    },
    201
  );
});

test("continuar, identidad inyectada y rutas invalidas no envian peticion", async () => {
  await withFetch(eventBody(), async (calls) => {
    // Compile-time negative contract and runtime boundary for untyped callers.
    await expect(
      eipdReviewApi.recordNegative(scope, {
        // @ts-expect-error continuar no forma parte de la accion negativa
        decision: "continuar",
        rationale: "TEST",
        review_reference: "TEST",
      })
    ).rejects.toThrow();
    await expect(
      eipdReviewApi.recordNegative(scope, {
        decision: "no_continuar",
        rationale: "TEST",
        review_reference: "TEST",
        review_context_metadata: metadata,
      } as EipdNegativeReviewIn)
    ).rejects.toThrow();
    await expect(eipdReviewApi.event(scope, "../admin")).rejects.toThrow();
    await expect(eipdReviewApi.preparation({ ...scope, token: "" })).rejects.toThrow();
    expect(calls).toHaveLength(0);
  });
});

for (const status of [401, 402, 403, 409]) {
  test(`rechazo ${status} conserva status y motivos estructurados`, async () => {
    const detail = {
      code: "revision_eipd_no_preparada",
      evaluation_version: 3,
      issues_v3: [{ code: "asociacion_obsoleta" }],
    };
    await withFetch(
      { detail },
      async (calls) => {
        let caught: unknown;
        try {
          await eipdReviewApi.preparation(scope);
        } catch (error) {
          caught = error;
        }
        expect(caught).toBeInstanceOf(ApiError);
        expect((caught as ApiError).status).toBe(status);
        expect((caught as ApiError).detail).toEqual(detail);
        expect((caught as ApiError).message).toBe(`Error ${status}`);
        expect(calls).toHaveLength(1);
      },
      status
    );
  });
}

test("errores de texto historicos conservan mensaje", async () => {
  await withFetch(
    { detail: "Acceso denegado" },
    async () => {
      await expect(eipdReviewApi.preparation(scope)).rejects.toThrow("Acceso denegado");
    },
    403
  );
});

test("estado de ultima revision conserva las cuatro variantes, ausencia V3 y rechaza estados desconocidos", async () => {
  for (const state of ["sin_revision", "sin_metadatos", "vigente", "obsoleta"] as const) {
    const body = readiness();
    body.eipd_controls_v3.review_context_metadata_status = state;
    await withFetch(body, async () => {
      expect((await eipdReviewApi.preparation(scope)).latest_review_context_status).toBe(state);
    });
  }
  const invalid = readiness();
  invalid.eipd_controls_v3.review_context_metadata_status = "aprobada";
  await withFetch(invalid, async () => {
    await expect(eipdReviewApi.preparation(scope)).rejects.toThrow("incompatible");
  });
  await withFetch(
    { assessment_id: scope.assessmentId, status: "borrador", eipd_controls_v3: null },
    async () => {
      expect((await eipdReviewApi.preparation(scope)).latest_review_context_status).toBeNull();
    }
  );
});

test("politica proyecta estados sin autoridad y rechaza enum o habilitacion incoherentes", async () => {
  const body = readiness();
  await withFetch(body, async () => {
    expect((await eipdReviewApi.preparation(scope)).policy_status).toEqual(
      body.eipd_controls_v3.policy
    );
  });
  for (const patch of [
    { sources_status: "aprobadas" },
    { acceptance_status: "automatica" },
    { activation: "activada" },
    { activation: "habilitada" },
  ]) {
    const invalid = readiness();
    Object.assign(invalid.eipd_controls_v3.policy, patch);
    await withFetch(invalid, async () => {
      await expect(eipdReviewApi.preparation(scope)).rejects.toThrow("incompatible");
    });
  }
  const enabled = readiness();
  enabled.eipd_controls_v3.policy = {
    sources_status: "verificadas",
    acceptance_status: "aceptada",
    activation: "habilitada",
  };
  await withFetch(enabled, async () => {
    expect((await eipdReviewApi.preparation(scope)).policy_status).toEqual(
      enabled.eipd_controls_v3.policy
    );
  });
  await withFetch(
    { assessment_id: scope.assessmentId, status: "borrador", eipd_controls_v3: null },
    async () => {
      expect((await eipdReviewApi.preparation(scope)).policy_status).toBeNull();
    }
  );
});

test("representacion proyecta diagnostico sin autoridad y oculta vigencia EIPD incompleta", async () => {
  const raw = {
    ...readiness(),
    sensitive_representation: {
      evaluation_version: 1,
      evaluation_scope: "requisitos_documentales",
      authorizes_action: false,
      can_confirm: false,
      result: "incompleto",
      issues: [
        {
          field: "authority_document_reference",
          code: "representacion_material_pendiente",
          category: "incompleto",
        },
      ],
    },
    representation_context_coverage: "pendiente",
  };
  await withFetch(raw, async () => {
    const result = await eipdReviewApi.preparation(scope);
    expect(result.sensitive_representation?.can_confirm).toBe(false);
    expect(result.sensitive_representation?.issues[0].stage).toBe("representation");
    expect(result.representation_context_coverage).toBe("pendiente");
    expect(result.latest_review_context_status).toBeNull();
    expect(result.review_prerequisites_v3).toBeNull();
  });
  await withFetch(
    {
      ...raw,
      sensitive_representation: { ...raw.sensitive_representation, result: "completo", issues: [] },
    },
    async () => {
      expect((await eipdReviewApi.preparation(scope)).sensitive_representation?.can_confirm).toBe(
        false
      );
    }
  );
});

for (const change of [
  { authorizes_action: true },
  { can_confirm: true },
  { evaluation_version: 2 },
  { result: "completo" },
  { issues: [{ field: "PRUEBA", code: "PRUEBA", category: "aprobado" }] },
]) {
  test(`diagnostico representacion incompatible rechazado ${JSON.stringify(change)}`, async () => {
    const raw = {
      ...readiness(),
      representation_context_coverage: "pendiente",
      sensitive_representation: {
        evaluation_version: 1,
        evaluation_scope: "requisitos_documentales",
        authorizes_action: false,
        can_confirm: false,
        result: "incompleto",
        issues: [{ field: "PRUEBA", code: "PRUEBA", category: "incompleto" }],
        ...change,
      },
    };
    await withFetch(raw, async () => {
      await expect(eipdReviewApi.preparation(scope)).rejects.toThrow("incompatible");
    });
  });
}

test("cobertura pendiente sin diagnostico no se acepta", async () => {
  await withFetch(
    {
      ...readiness(),
      representation_context_coverage: "pendiente",
      sensitive_representation: null,
    },
    async () => {
      await expect(eipdReviewApi.preparation(scope)).rejects.toThrow("incompatible");
    }
  );
});

function representationV4Readiness() {
  const issue = {
    stage: "activation",
    field: "policy.routes",
    code: "politica_representacion_no_implementada",
    category: "requiere_revision",
    question_id: null,
  };
  const decision = { prerequisites_met: false, context_metadata: null, issues: [issue] };
  return {
    ...readiness(),
    eipd_controls_v3: null,
    eipd_controls_v4: {
      evaluation_version: 4,
      evaluation_scope: "requisitos_documentales",
      authorizes_action: false,
      can_confirm: false,
      policy: readiness().eipd_controls_v3.policy,
      preparation_issues: [issue],
      review_blockers: [issue],
      confirmation_blockers: [issue],
      review_prerequisites_v4: {
        evaluation_version: 4,
        evaluation_scope: "requisitos_documentales",
        authorizes_action: false,
        can_confirm: false,
        continuar: decision,
        requiere_cambios: decision,
        no_continuar: decision,
      },
    },
  };
}

test("V4 conserva politica sin convertir requisitos o identidad en version historica", async () => {
  await withFetch(representationV4Readiness(), async () => {
    const result = await eipdReviewApi.preparation(scope);
    expect(result.policy_status?.activation).toBe("deshabilitada");
    expect(result.review_prerequisites_v3).toBeNull();
    expect(result.latest_review_context_status).toBeNull();
    expect(result.review_prerequisites_v4?.can_confirm).toBe(false);
    expect(result.current_control_issues_v4?.length).toBe(3);
  });
});

for (const change of [
  "authority",
  "action_context",
  "prerequisites",
  "enabled",
  "both_versions",
] as const) {
  test(`V4 rechaza salida incompatible ${change}`, async () => {
    const raw = JSON.parse(JSON.stringify(representationV4Readiness()));
    if (change === "authority") raw.eipd_controls_v4.authorizes_action = true;
    if (change === "action_context")
      raw.eipd_controls_v4.review_prerequisites_v4.continuar.context_metadata = metadata;
    if (change === "prerequisites")
      raw.eipd_controls_v4.review_prerequisites_v4.continuar.prerequisites_met = true;
    if (change === "enabled") raw.eipd_controls_v4.policy.activation = "habilitada";
    if (change === "both_versions") raw.eipd_controls_v3 = readiness().eipd_controls_v3;
    await withFetch(raw, async () => {
      await expect(eipdReviewApi.preparation(scope)).rejects.toThrow();
    });
  });
}

test("V4 rechaza motivos actuales malformados antes de mostrarlos", async () => {
  const raw = JSON.parse(JSON.stringify(representationV4Readiness()));
  raw.eipd_controls_v4.confirmation_blockers[0].category = "aprobado";
  await withFetch(raw, async () => {
    await expect(eipdReviewApi.preparation(scope)).rejects.toThrow();
  });
});

const successorMetadata = {
  metadata_schema_version: 2,
  resolution_binding_version: 3,
  context_schema_version: 3,
  research_coverage: "contexto_v3",
  representation_coverage: "contexto_v3",
  document_hash: "a".repeat(64),
  context_hash: "b".repeat(64),
  research_material_hash: null,
  representation_material_hash: "d".repeat(64),
};

test("lectura V3 conserva metadata2 sin inferir vigencia y usa ruta sucesora", async () => {
  const raw = { ...eventBody(3), review_context_metadata: successorMetadata };
  await withFetch(raw, async (calls) => {
    const result = await eipdReviewApi.event(scope, rid);
    expect(result.response_schema_version).toBe(3);
    expect(result.review_context_metadata).toEqual(successorMetadata);
    expect(calls[0].url).toContain(`/reviews/${rid}/v3`);
    expect(calls[0].options.method ?? "GET").toBe("GET");
  });
});

for (const change of ["coverage", "hash", "authority", "extra_metadata", "old_response"] as const) {
  test(`lectura V3 rechaza metadata o version incompatible ${change}`, async () => {
    const raw = JSON.parse(
      JSON.stringify({ ...eventBody(3), review_context_metadata: successorMetadata })
    );
    if (change === "coverage") raw.review_context_metadata.representation_coverage = "no_cubierta";
    if (change === "hash") raw.review_context_metadata.document_hash = "f".repeat(64);
    if (change === "authority") raw.can_confirm = true;
    if (change === "extra_metadata") raw.review_context_metadata.approved = true;
    if (change === "old_response") raw.response_schema_version = 2;
    await withFetch(raw, async () => {
      await expect(eipdReviewApi.event(scope, rid)).rejects.toThrow("incompatible");
    });
  });
}
