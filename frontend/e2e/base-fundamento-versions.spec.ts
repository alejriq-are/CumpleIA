import { expect, test, type Page } from "@playwright/test";
import path from "node:path";
import { browserBundle } from "./helpers/browser-bundle";

const org = "10000000-0000-0000-0000-000000000001";
const tid = "10000000-0000-0000-0000-000000000002";
const aid = "10000000-0000-0000-0000-000000000003";
const vid = "10000000-0000-0000-0000-000000000004";
const actor = "10000000-0000-0000-0000-000000000005";
let bundle: string;

test.beforeAll(async () => {
  bundle =
    await browserBundle(`import React from "react"; import { createRoot } from "react-dom/client";
    import { BaseFundamentoRegister, BaseFundamentoHistory } from ${JSON.stringify(path.resolve("components/licitud/BaseFundamentoVersions.tsx"))};
    const scope = async () => ({ organizationId: ${JSON.stringify(org)}, treatmentId: ${JSON.stringify(tid)}, assessmentId: ${JSON.stringify(aid)}, token: "fixture-token" });
    window.render = mode => createRoot(document.getElementById("root")).render(
      mode === "register"
        ? React.createElement(BaseFundamentoRegister, { scope, onPending: v => window.locked = v, blocked: false, savedRevision: 0,
            annexes: [{ id: ${JSON.stringify(actor)}, reference: "SIMULADA-ANEXO-001", version: 1, filename: "respaldo.txt" }] })
        : React.createElement(BaseFundamentoHistory, { scope, onPending: v => window.locked = v })
    );`);
});

async function setup(page: Page, mode: "register" | "review") {
  await page.route("http://localhost:3000/fixture", (route) =>
    route.fulfill({ contentType: "text/html", body: '<div id="root"></div>' })
  );
  await page.goto("http://localhost:3000/fixture");
  await page.evaluate(
    ({ org, tid, aid, vid, actor, mode }) => {
      const w = window as any;
      const material = {
        document_type: "base_fundamento",
        saved_assessment: {
          id: aid,
          organization_id: org,
          treatment_id: tid,
          legal_basis: null,
          purpose_snapshot: "Finalidad ficticia",
        },
        primary_form: null,
        alternatives: {},
        annexes: [],
        diagnostic: {
          criteria: [
            { id: "base.respaldo", label: "Respaldo verificable" },
            { id: "consentimiento.contrato", label: "Contexto contractual" },
          ],
          findings: [
            {
              criterion_id: null,
              field: "legal_basis",
              code: "base_pendiente",
              classification: "esencial",
            },
          ],
          coverage_pending: ["FORM-R01"],
        },
      };
      const version = {
        id: vid,
        organization_id: org,
        treatment_id: tid,
        assessment_id: aid,
        version: 1,
        created_by: actor,
        created_at: "2026-11-07T17:00:00Z",
        reason: "Ensayo ficticio",
        source_hash: "a".repeat(64),
        bundle: material,
      };
      const preview = {
        source_hash: version.source_hash,
        latest_version: 0,
        bundle: material,
        favorable_requirements: [
          {
            criterion_id: "base.definida",
            field: "legal_basis",
            code: "base_pendiente",
            resolution: null,
          },
          {
            criterion_id: "consentimiento.mandato",
            field: "answers.mandatario_facultad_expresa",
            code: "respuesta_no_aplicable",
            resolution: null,
          },
          {
            criterion_id: "consentimiento.mandato",
            field: "answers.mandatario_facultad_expresa",
            code: "aplicabilidad",
            resolution: "no_aplica",
          },
        ],
      };
      const requirements = [
        {
          criterion_id: "base.respaldo",
          field: "evidence",
          code: "evidencia_ausente",
          resolution: "respaldo_equivalente",
        },
        {
          criterion_id: "consentimiento.contrato",
          field: "answers.tratamiento_necesario_contrato_servicio",
          code: "aplicabilidad",
          resolution: "no_aplica",
        },
      ];
      w.posts = [];
      w.fetch = async (url: string, options: RequestInit = {}) => {
        const route = new URL(url).pathname;
        const response = (value: unknown, status = 200) =>
          new Response(JSON.stringify(value), {
            status,
            headers: { "Content-Type": "application/json" },
          });
        if (route.endsWith("/preview")) {
          w.previewAnnexes = new URL(url).searchParams.getAll("annex_ids");
          return response({
            ...preview,
            bundle: {
              ...material,
              annexes: w.previewAnnexes.map((id: string) => ({
                id,
                reference: "SIMULADA-ANEXO-001",
                version: 1,
                revision: 1,
                sha256: "b".repeat(64),
              })),
            },
          });
        }
        if (route.endsWith("/review-state"))
          return response({
            version_id: vid,
            organization_id: org,
            treatment_id: tid,
            assessment_id: aid,
            reviews: w.review ? [w.review] : [],
            authorities: [],
            authority_id: actor,
            blocked_reason: null,
            can_review: true,
            can_favorable: true,
            may_manage: false,
            favorable_requirements: requirements,
          });
        if (options.method === "POST") {
          const body = JSON.parse(String(options.body));
          w.posts.push(body);
          if (mode === "register") {
            w.registered = { ...version, reason: body.reason, request_id: body.request_id };
          } else {
            if (w.posts.length === 1)
              return response({ detail: "La revisión previa cambió." }, 409);
            w.review = {
              ...body,
              id: actor,
              version_id: vid,
              organization_id: org,
              treatment_id: tid,
              assessment_id: aid,
              sequence: 1,
              previous_id: body.expected_previous_id,
              created_by: actor,
              created_at: version.created_at,
            };
          }
          throw new TypeError("Respuesta perdida");
        }
        if (route.includes("/review-requests/")) return response(w.review);
        if (route.includes("/requests/")) return response(w.registered);
        if (route.endsWith("/" + vid))
          return response({ ...version, favorable_requirements: requirements });
        return response([version]);
      };
    },
    { org, tid, aid, vid, actor, mode }
  );
  await page.addScriptTag({ content: bundle });
  await page.evaluate((mode) => (window as any).render(mode), mode);
}

test("prepara una base pendiente, incluye el anexo elegido y recupera el registro", async ({
  page,
}) => {
  await setup(page, "register");
  await page.getByRole("checkbox", { name: /SIMULADA-ANEXO-001/ }).check();
  await page.getByRole("button", { name: "Preparar registro de Base y fundamento" }).click();
  await expect(page.getByText("Pendiente de definir", { exact: true })).toBeVisible();
  await expect(page.getByText(/La base de licitud está pendiente de definir/)).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Requisitos esenciales que bloquean Favorable" })
  ).toBeVisible();
  await expect(page.getByText(/conserva una respuesta incompatible/)).toBeVisible();
  await expect(page.getByRole("region", { name: "Requisitos que no aplican" })).toHaveCount(0);
  await expect(page.getByText(/Cobertura pendiente del piloto/)).toBeVisible();
  await page.getByLabel("Motivo del registro").fill("[FICTICIA] Registrar antecedentes");
  await page.getByLabel("Declaro datos ficticios para esta versión").check();
  await page.getByLabel("Revisé el contenido guardado y sus pendientes").check();
  await page
    .getByRole("button", { name: "Registrar versión documental de Base y fundamento" })
    .click();
  await page.getByRole("button", { name: "Consultar resultado de la solicitud" }).click();
  await expect(
    page.getByText("Versión de Base y fundamento 1 registrada en el servidor.")
  ).toBeVisible();
  expect(
    await page.evaluate(() =>
      (window as any).posts.map((p: { annex_ids: string[] }) => p.annex_ids)
    )
  ).toEqual([[actor]]);
});

test("revisión favorable conserva requisitos y observación ante conflicto y recupera el recibo", async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 800 });
  await setup(page, "review");
  await page.getByRole("button", { name: "Consultar versiones de Base y fundamento" }).click();
  await page.getByRole("button", { name: "Consultar versión de Base y fundamento 1" }).click();
  const read = page.getByRole("button", {
    name: "Consultar revisiones y facultades de Base y fundamento",
  });
  await read.click();
  await expect(page.getByRole("region", { name: "Requisitos que no aplican" })).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Requisitos que admiten respaldo equivalente" })
  ).toBeVisible();
  await page.getByLabel("Resultado de la revisión").selectOption("favorable");
  await page.getByLabel("Fundamento de la revisión").fill("[FICTICIA] Revisión de ensayo");
  await page.getByLabel("Referencia de respaldo de la revisión").fill("REVISION-001");
  await page
    .getByLabel("Justificación de respaldo equivalente")
    .fill("Acredita el hecho en la bitácora");
  await page.getByLabel("Dónde consultar el respaldo equivalente").fill("BITACORA-001");
  await page
    .getByLabel("Justificación de no aplica")
    .fill("El tratamiento carece de contexto contractual");
  await page.getByRole("button", { name: "Añadir observación" }).click();
  await page.getByLabel("Observación 1").fill("Normalizar la referencia");
  await page.getByLabel("Responsable").fill("Equipo de ensayo");
  await page.getByLabel("Plazo").fill("2026-12-01");
  await page.getByLabel("Declaro datos ficticios para esta revisión").check();
  const submit = page.getByRole("button", { name: "Registrar revisión de Base y fundamento" });
  await submit.click();
  await expect(page.getByRole("alert")).toBeFocused();
  await expect(submit).toBeDisabled();
  await expect(page.getByLabel("Justificación de no aplica")).toHaveValue(
    "El tratamiento carece de contexto contractual"
  );
  await expect(
    page.getByRole("button", { name: "Volver a versiones de Base y fundamento" })
  ).toBeDisabled();
  await read.click();
  await submit.click();
  await page.getByRole("button", { name: "Consultar resultado de la solicitud" }).click();
  await expect(page.getByText("1. Favorable")).toBeVisible();
  await expect(
    page.getByText(/Normalizar la referencia · Responsable: Equipo de ensayo/)
  ).toBeVisible();
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(2);
});
