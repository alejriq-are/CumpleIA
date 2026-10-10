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
function eventBody() {
  return {
    response_schema_version: 2,
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
    { ...eventBody(), review_context_metadata: { ...metadata, context_hash: "c".repeat(64) } },
    async () => {
      await expect(eipdReviewApi.event(scope, rid)).rejects.toThrow("incompatible");
    }
  );
  await withFetch({ ...eventBody(), organization_id: scope.treatmentId }, async () => {
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
    ...eventBody(),
    review_context_metadata: null,
    policy_version: null,
    policy_reference: null,
    policy_hash: null,
  };
  await withFetch(value, async (calls) => {
    const result = await eipdReviewApi.event(scope, rid);
    expect(result.review_context_metadata).toBeNull();
    expect(result.policy_hash).toBeNull();
    expect(calls[0].url).toContain(`/eipd-resolution/reviews/${rid}/v2`);
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
