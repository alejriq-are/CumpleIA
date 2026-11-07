import { test, expect, type Page } from "@playwright/test";
import { browserBundle } from "./helpers/browser-bundle";
import path from "node:path";
let bundle: string;
const org = "10000000-0000-0000-0000-000000000001",
  tid = "10000000-0000-0000-0000-000000000002",
  aid = "10000000-0000-0000-0000-000000000003";
const actor = "10000000-0000-0000-0000-000000000004",
  vid = "10000000-0000-0000-0000-000000000005";
const material = {
  schema_version: 1,
  document_type: "eipd_general",
  saved_assessment: {
    id: aid,
    organization_id: org,
    treatment_id: tid,
    version: 1,
    purpose_snapshot: "[FICTICIA] Finalidad conservada",
    rat_context_snapshot: { title: "RAT histórico" },
    eipd_resolution_assessment: { schema_version: 1, notes: "[FICTICIA] Contenido guardado" },
  },
  applicability: { eipd: "corresponde" },
  support_records: [],
  policy: { reference: "Ensayo" },
  diagnostic: { readiness: { result: "incompleto" } },
};
const preview = {
  source_hash: "a".repeat(64),
  latest_version: 0,
  bundle: material,
  can_confirm: false,
  activation: "deshabilitada",
};
test.beforeAll(async () => {
  bundle = await browserBundle(
    `import React from "react";import {createRoot} from "react-dom/client";import {EipdVersions} from ${JSON.stringify(path.resolve("components/licitud/EipdVersions.tsx"))};const root=createRoot(document.getElementById("root"));window.renderVersions=(props)=>root.render(React.createElement(EipdVersions,{organizationId:${JSON.stringify(org)},treatmentId:${JSON.stringify(tid)},assessmentId:${JSON.stringify(aid)},token:async()=>"fixture-token",canRegister:true,canCopy:true,onCopy:v=>window.copied=v,...props}));`
  );
});
async function setup(page: Page, mode = "success", props = {}) {
  await page.route("http://localhost:3000/fixture", (r) =>
    r.fulfill({ contentType: "text/html", body: '<div id="root"></div>' })
  );
  await page.goto("http://localhost:3000/fixture");
  await page.evaluate(
    ({ preview, org, tid, aid, actor, vid, mode }) => {
      const w = window as any;
      w.mode = mode;
      w.calls = [];
      w.posts = [];
      w.found = null;
      w.fetch = async (url: string, init: any = {}) => {
        w.calls.push({ url, ...init });
        const method = init.method || "GET";
        const response = (v: any, status = 200) =>
          new Response(JSON.stringify(v), {
            status,
            headers: { "Content-Type": "application/json" },
          });
        if (url.endsWith("/decision-state")) {
          const versionId = url.split("/").at(-2);
          const canDecide = versionId !== vid;
          return response({
            organization_id: org,
            treatment_id: tid,
            assessment_id: aid,
            version_id: versionId,
            decisions: w.decisions ?? [],
            authorities: w.decisionAuthorities ?? [],
            latest_review_id: w.latestDecisionReview ?? null,
            authority_id: canDecide ? actor : null,
            may_manage: canDecide,
            can_decide: canDecide,
            can_accept: canDecide && !!w.latestDecisionReview,
            blocked_reason: canDecide
              ? null
              : "Se requiere una facultad expresa y vigente de decisión",
            acceptance_blocked_reason: w.latestDecisionReview
              ? null
              : "La última revisión de esta versión debe ser Favorable",
          });
        }
        if (url.endsWith("/decision-authorities") && method === "POST") {
          const body = JSON.parse(init.body);
          const value = {
            ...body,
            id: crypto.randomUUID(),
            created_by: actor,
            sequence: body.expected_sequence + 1,
            created_at: "2026-11-07T12:00:00Z",
          };
          w.decisionAuthorities = [...(w.decisionAuthorities ?? []), value];
          return response(value, 201);
        }
        if (url.endsWith("/decisions") && method === "POST") {
          const body = JSON.parse(init.body);
          w.decisionPosts = [...(w.decisionPosts ?? []), body];
          if (w.decisionPosts.length === 1 && mode === "decision-conflict") {
            w.latestDecisionReview = crypto.randomUUID();
            return response({ detail: "La revisión previa cambió." }, 409);
          }
          if (w.decisionPosts.length === 1 && mode === "decision-missing") {
            throw new TypeError("Connection lost");
          }
          const value = {
            id: crypto.randomUUID(),
            organization_id: org,
            treatment_id: tid,
            assessment_id: aid,
            version_id: url.split("/").at(-2),
            request_id: body.request_id,
            sequence: 1,
            review_id: body.expected_review_id,
            authority_id: body.expected_authority_id,
            previous_id: body.expected_decision_id,
            reason: body.reason,
            reference: body.reference,
            outcome: body.outcome,
            created_by: actor,
            created_at: "2026-11-07T12:00:00Z",
          };
          w.decisions = [value];
          if (mode === "decision-conflict") throw new TypeError("Response lost");
          return response(value, 201);
        }
        if (url.includes("/decision-requests/")) {
          const value = w.decisions?.find((d: { request_id: string }) =>
            url.endsWith("/" + d.request_id)
          );
          return value ? response(value) : response({ detail: "Solicitud no encontrada" }, 404);
        }
        if (url.endsWith("/preview"))
          return response(
            w.mode === "foreign"
              ? {
                  ...preview,
                  bundle: {
                    ...preview.bundle,
                    saved_assessment: { ...preview.bundle.saved_assessment, id: vid },
                  },
                }
              : preview
          );
        if (method === "POST") {
          const b = JSON.parse(init.body);
          w.posts.push(b);
          if (w.mode === "stale") return response({ detail: "El origen cambió" }, 409);
          if (w.mode === "missing" && w.posts.length === 1) throw new TypeError("Offline");
          w.found = {
            id: vid,
            organization_id: org,
            treatment_id: tid,
            assessment_id: aid,
            version: 1,
            created_by: actor,
            created_at: "2026-11-02T12:00:00Z",
            request_id: b.request_id,
            reason: b.reason,
            source_hash: b.expected_source_hash,
            bundle_hash: "b".repeat(64),
            bundle: {
              ...preview.bundle,
              version: 1,
              predecessor_id: null,
              reason: b.reason,
              registered_by: actor,
            },
            can_confirm: false,
            activation: "deshabilitada",
          };
          if (w.mode === "lost") throw new TypeError("Response lost");
          return response(w.found, 201);
        }
        if (url.includes("/requests/"))
          return w.found ? response(w.found) : response({ detail: "No encontrado" }, 404);
        if (url.endsWith("/review-state")) {
          const version = w.byId?.[url.split("/").at(-2)!];
          return response({
            version_id: version?.id,
            organization_id: org,
            treatment_id: tid,
            assessment_id: aid,
            can_review: true,
            can_favorable: true,
            may_manage: version?.version === 2,
            reviews: [],
            authorities: [],
          });
        }
        if (w.byId?.[url.split("/").at(-1)!]) return response(w.byId[url.split("/").at(-1)!]);
        if (url.endsWith("/" + vid)) return response(w.found);
        return response(w.versionHistory ?? (w.found ? [w.found] : []));
      };
    },
    { preview, org, tid, aid, actor, vid, mode }
  );
  await page.addScriptTag({ content: bundle });
  await page.evaluate((props) => (window as any).renderVersions(props), props);
}
async function prepare(page: Page) {
  await page
    .getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
    .click();
  await page
    .getByLabel("Motivo del registro de versión EIPD", { exact: true })
    .fill("[FICTICIA] Versión de prueba");
  await page.getByLabel("Declaro datos ficticios para esta versión EIPD", { exact: true }).check();
  await page
    .getByLabel("He leído el contenido guardado y sus pendientes antes de registrar", {
      exact: true,
    })
    .check();
}
test("registro explícito, consulta histórica y copia confirmada sin otra escritura", async ({
  page,
}) => {
  await setup(page);
  await prepare(page);
  await page
    .getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Versión EIPD 1 registrada");
  await page.getByRole("button", { name: "Mostrar historial de versiones EIPD" }).click();
  await page.getByRole("button", { name: "Consultar versión EIPD 1", exact: true }).click();
  await page.getByRole("button", { name: "Ocultar historial de versiones EIPD" }).click();
  await expect(
    page.getByRole("button", { name: "Consultar versión EIPD 1", exact: true })
  ).toBeHidden();
  await expect(page.getByRole("article")).toContainText("Contenido guardado");
  await page.getByRole("button", { name: "Preparar borrador desde esta versión EIPD" }).click();
  await page.getByRole("button", { name: "Conservar mi borrador actual" }).click();
  expect(await page.evaluate(() => (window as any).copied)).toBeUndefined();
  await page.getByRole("button", { name: "Preparar borrador desde esta versión EIPD" }).click();
  await page.getByRole("button", { name: "Reemplazar borrador con esta copia" }).click();
  expect(await page.evaluate(() => (window as any).copied.notes)).toContain("Contenido guardado");
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(1);
  const calls = await page.evaluate(() => (window as any).calls);
  expect(
    calls.every((c: any) => c.cache === "no-store" && c.headers["X-Organization-Id"] === org)
  ).toBeTruthy();
});
test("respuesta perdida recupera solicitud sin duplicar registro", async ({ page }) => {
  await setup(page, "lost");
  await prepare(page);
  await page
    .getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("por comprobar");
  await expect(
    page.getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
  ).toBeDisabled();
  await page.getByRole("button", { name: "Consultar resultado del registro EIPD" }).click();
  await expect(page.getByRole("status")).toContainText("Versión EIPD 1 registrada");
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(1);
});
test("404 permite reintentar exactamente la misma solicitud", async ({ page }) => {
  await setup(page, "missing");
  await prepare(page);
  await page
    .getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
    .click();
  await page.getByRole("button", { name: "Consultar resultado del registro EIPD" }).click();
  await page.getByRole("button", { name: "Reintentar el mismo registro EIPD" }).click();
  await expect(page.getByRole("status")).toContainText("Versión EIPD 1 registrada");
  const posts = await page.evaluate(() => (window as any).posts);
  expect(posts).toHaveLength(2);
  expect(posts[1]).toEqual(posts[0]);
});
test("origen desactualizado exige otra vista previa", async ({ page }) => {
  await setup(page, "stale");
  await prepare(page);
  await page
    .getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("Registro rechazado");
  await expect(
    page.getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
  ).toBeEnabled();
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(1);
});
test("respuesta de otra evaluación no habilita registro", async ({ page }) => {
  await setup(page, "foreign");
  await page
    .getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("incompatible");
  await expect(page.getByLabel("Motivo del registro de versión EIPD", { exact: true })).toHaveCount(
    0
  );
});
test("ediciones pendientes bloquean registro pero conservan consulta", async ({ page }) => {
  await setup(page, "success", {
    canRegister: false,
    draftDirty: true,
    blockedReason: "Guarda los cambios pendientes",
  });
  await expect(
    page.getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
  ).toBeDisabled();
  await page.getByRole("button", { name: "Mostrar historial de versiones EIPD" }).click();
  await expect(
    page.getByText("No hay versiones EIPD registradas en esta evaluación.")
  ).toBeVisible();
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(0);
});

test("editar el origen invalida la vista previa sin escribir una versión", async ({ page }) => {
  await setup(page);
  await prepare(page);
  await page.evaluate(() =>
    (window as any).renderVersions({
      sourceRevision: "nueva-edicion",
      canRegister: false,
      draftDirty: true,
    })
  );
  await expect(
    page.getByRole("button", { name: "Registrar versión documental EIPD", exact: true })
  ).toHaveCount(0);
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(0);
});
test("consulta de solo lectura no ofrece registro ni reemplazo y admite teclado", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await setup(page, "success", { onCopy: null, canRegister: false });
  await expect(
    page.getByRole("button", { name: "Preparar registro de versión EIPD", exact: true })
  ).toHaveCount(0);
  const history = page.getByRole("button", { name: "Mostrar historial de versiones EIPD" });
  await history.focus();
  await page.keyboard.press("Space");
  await expect(
    page.getByText("No hay versiones EIPD registradas en esta evaluación.")
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Ocultar historial de versiones EIPD" })
  ).toBeFocused();
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(0);
});

async function seedVersions(page: Page) {
  await page.evaluate(
    ({ preview, org, tid, aid, actor, vid }) => {
      const w = window as any;
      const first = {
        id: vid,
        organization_id: org,
        treatment_id: tid,
        assessment_id: aid,
        version: 1,
        created_by: actor,
        created_at: "2026-11-05T12:00:00Z",
        request_id: crypto.randomUUID(),
        reason: "[FICTICIA] Primera",
        source_hash: "a".repeat(64),
        bundle_hash: "b".repeat(64),
        bundle: {
          ...preview.bundle,
          version: 1,
          predecessor_id: null,
          reason: "[FICTICIA] Primera",
          registered_by: actor,
        },
        can_confirm: false,
        activation: "deshabilitada",
      };
      const second = {
        ...first,
        id: crypto.randomUUID(),
        version: 2,
        reason: "[FICTICIA] Segunda",
        bundle: { ...first.bundle, version: 2, predecessor_id: vid, reason: "[FICTICIA] Segunda" },
      };
      w.versionHistory = [first, second];
      w.byId = { [first.id]: first, [second.id]: second };
    },
    { preview, org, tid, aid, actor, vid }
  );
}

test("consulta abre versiones recientes primero sin formulario de registro", async ({ page }) => {
  await setup(page, "success", { consultationOnly: true });
  const guide = page.locator("details").filter({
    has: page.getByText("Cómo revisar y decidir una EIPD", { exact: true }),
  });
  await expect(guide).toHaveAttribute("open", "");
  await expect(guide.getByRole("listitem")).toHaveText([
    /^Registra la versión/,
    /^Consulta la versión exacta/,
    /^Registra la revisión/,
    /^Registra la decisión/,
  ]);
  await seedVersions(page);
  await page.getByRole("button", { name: "Actualizar lista de versiones" }).click();
  await expect(page.getByRole("button", { name: /^Consultar versión EIPD/ })).toHaveText([
    "Consultar versión EIPD 2",
    "Consultar versión EIPD 1",
  ]);
  await expect(
    page.getByRole("region", { name: "Registrar versión EIPD", exact: true })
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Consultar versión EIPD 2", exact: true }).click();
  await expect(
    page.getByRole("article", { name: "Versión EIPD 2 consultada", exact: true })
  ).toBeVisible();
  await expect(page.getByText("Orden para aceptar esta versión.", { exact: true })).toBeVisible();
  const content = page.getByText("Contenido EIPD conservado para esta versión", { exact: true });
  await expect(content.locator("..")).not.toHaveAttribute("open", "");
  const reviewMenu = page.locator("summary").getByText("Revisiones y facultades", { exact: true });
  await reviewMenu.focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("button", { name: "Consultar revisiones y facultades", exact: true })
  ).toBeVisible();
  const admin = page.getByRole("button", {
    name: "Administrar facultades del expediente",
    exact: true,
  });
  await expect(admin).toHaveCount(0);
  await page
    .getByRole("button", { name: "Ver historial de facultades del expediente", exact: true })
    .click();
  await expect(
    page.getByText("Historial de facultades del expediente", { exact: true })
  ).toBeFocused();
  await admin.click();
  await expect(
    page.getByText("Administrar facultad de revisión del expediente", { exact: true })
  ).toBeFocused();
  await page.getByRole("button", { name: "Contenido conservado", exact: true }).click();
  await expect(content).toBeFocused();
  await expect(content.locator("..")).toHaveAttribute("open", "");
  await page.getByRole("button", { name: "Contexto y antecedentes", exact: true }).click();
  await expect(
    page.getByText("Contexto y antecedentes conservados con la versión", { exact: true })
  ).toBeFocused();
  await page
    .getByRole("button", { name: "Consultar revisiones y facultades", exact: true })
    .click();
  await page.getByLabel("Fundamento de la revisión").fill("[FICTICIA] Nota pendiente");
  await expect(page.getByRole("button", { name: "Actualizar lista de versiones" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Volver a versiones EIPD" })).toBeDisabled();
  await page.getByRole("button", { name: "Ir a Revisiones y facultades" }).click();
  await expect(reviewMenu).toBeFocused();
  await expect(page.getByLabel("Fundamento de la revisión")).toHaveValue(
    "[FICTICIA] Nota pendiente"
  );
  await page
    .getByRole("button", { name: "Descartar campos de revisión y facultad sin registrar" })
    .click();
  await page.getByRole("button", { name: "Volver a versiones EIPD" }).click();
  await expect(
    page.getByRole("button", { name: "Consultar versión EIPD 2", exact: true })
  ).toBeVisible();
  await page.getByRole("button", { name: "Consultar versión EIPD 1", exact: true }).click();
  await reviewMenu.click();
  await page
    .getByRole("button", { name: "Consultar revisiones y facultades", exact: true })
    .click();
  await expect(page.getByLabel("Fundamento de la revisión")).toBeVisible();
  await expect(admin).toHaveCount(0);
  expect(await page.evaluate(() => (window as any).posts.length)).toBe(0);
});

for (const mode of ["decision-conflict", "decision-missing"]) {
  test(`decisión sobre versión exacta conserva el formulario y recupera la solicitud (${mode})`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: 320, height: 800 });
    await setup(page, mode, { consultationOnly: true });
    await seedVersions(page);
    await page.getByRole("button", { name: "Actualizar lista de versiones" }).click();
    await page.getByRole("button", { name: "Consultar versión EIPD 1", exact: true }).click();
    await page.getByRole("button", { name: "Decisión de la organización", exact: true }).click();
    const read = page.getByRole("button", {
      name: "Consultar decisiones y facultades",
      exact: true,
    });
    await read.click();
    await expect(
      page.getByText("Se requiere una facultad expresa y vigente de decisión")
    ).toBeVisible();
    await expect(page.getByLabel("Resultado de la decisión")).toHaveCount(0);
    await page.getByRole("button", { name: "Volver a versiones EIPD" }).click();
    await page.getByRole("button", { name: "Consultar versión EIPD 2", exact: true }).click();
    await page.getByRole("button", { name: "Decisión de la organización", exact: true }).click();
    await expect(
      page.locator("summary").filter({ hasText: /^Decisión de la organización$/ })
    ).toBeFocused();
    await read.click();
    await expect(page.getByRole("option", { name: "Acepta", exact: true })).toHaveAttribute(
      "disabled",
      ""
    );
    if (mode === "decision-conflict") {
      await page.getByText("Administrar facultades de decisión", { exact: true }).click();
      await page.getByLabel("Identificador de la persona destinataria").fill(actor);
      await page.getByLabel("Motivo de la facultad de decisión").fill("[FICTICIA] Designación");
      await page.getByLabel("Referencia de respaldo de la facultad de decisión").fill("MEMO-001");
      await page
        .getByLabel("Fundamento de compatibilidad de funciones")
        .fill("[FICTICIA] Compatibilidad");
      await page
        .getByRole("button", { name: "Registrar actuación de facultad de decisión" })
        .click();
      await expect(page.getByText("Actuación de facultad de decisión registrada.")).toBeVisible();
      await page.getByText("Historial de facultades de decisión", { exact: true }).click();
      await expect(
        page.getByText("Compatibilidad documentada: [FICTICIA] Compatibilidad")
      ).toBeVisible();
    }
    const reason = page.getByLabel("Fundamento de la decisión");
    await reason.fill("[FICTICIA] Decisión de ensayo");
    await page.getByLabel("Referencia del acta").fill("ACTA-001");
    await page.getByLabel("Declaro datos ficticios para esta decisión").check();
    await expect(page.getByRole("button", { name: "Volver a versiones EIPD" })).toBeDisabled();
    const register = page.getByRole("button", { name: "Registrar decisión", exact: true });
    await register.click();
    if (mode === "decision-conflict") {
      const error = page.getByRole("alert").filter({ hasText: "Tus campos se conservan" });
      await expect(error).toBeFocused();
      await expect(reason).toHaveValue("[FICTICIA] Decisión de ensayo");
      await expect(register).toBeDisabled();
      await read.click();
      await page.getByLabel("Resultado de la decisión").selectOption("acepta");
      await register.click();
    }
    await page
      .getByRole("button", { name: "Consultar resultado de la solicitud de decisión" })
      .click();
    if (mode === "decision-missing") {
      await page.getByRole("button", { name: "Reintentar la misma decisión" }).click();
      expect(
        await page.evaluate(() => {
          const posts = (window as any).decisionPosts;
          return posts[0].request_id === posts[1].request_id;
        })
      ).toBe(true);
    }
    await expect(page.getByText("Decisión documental registrada.")).toBeVisible();
    await expect(page.getByText("Referencia del acta: ACTA-001")).toBeVisible();
    await expect(page.getByRole("button", { name: "Volver a versiones EIPD" })).toBeEnabled();
  });
}
