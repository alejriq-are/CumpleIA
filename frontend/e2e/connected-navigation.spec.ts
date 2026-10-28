import { test, expect, type Page } from "@playwright/test";
import { rm, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { buildConnectedHarness } from "./helpers/connected-harness";
let directory: string, script: string, css: string;
let viewerHarness: Awaited<ReturnType<typeof buildConnectedHarness>>;
let editorHarness: Awaited<ReturnType<typeof buildConnectedHarness>>;
const org = "a0000000-0000-0000-0000-000000000001";
const tid = "a0000000-0000-0000-0000-000000000002";
const aid = "a0000000-0000-0000-0000-000000000003";
const aid2 = "a0000000-0000-0000-0000-000000000004";
const series = "a0000000-0000-0000-0000-000000000005";
const organization = {
  id: org,
  name: "[FICTICIA] Organización conectada",
  role: "owner",
  rut: null,
  size: null,
  industry: null,
};
let releaseValidation: (() => void) | undefined;
let releaseApplicability: (() => void) | undefined;
let records: Record<string, any>,
  determinations: Record<string, any>,
  calls: { path: string; method: string; org: string | null; body: any }[],
  errors: string[],
  mode: string;
const detail = {
  id: tid,
  organization_id: org,
  name: "[FICTICIA] Actividad mixta",
  status: "borrador",
  description: "PRUEBA alcance",
  organization_role: "responsable",
  business_area: "PRUEBA",
  data_flow_description: "PRUEBA",
  start_date: null,
  last_reviewed_at: null,
  next_review_at: null,
  retention_rule: "PRUEBA",
  deletion_method: "PRUEBA",
  has_automated_decisions: false,
  automated_decision_description: null,
  systems_declaration: "sin_sistemas",
  vendors_declaration: "sin_proveedores",
  international_transfers_declaration: "sin_transferencias",
  purposes: [
    { id: series, purpose: "[FICTICIA] Finalidad de prueba", is_primary: true, sort_order: 0 },
  ],
  data_categories: [
    {
      category_code: "identificacion",
      category_name: "Identificación",
      is_sensitive: false,
      notes: null,
    },
  ],
  data_subjects: [
    {
      category_code: "clientes",
      category_name: "Clientes",
      includes_children: true,
      includes_adolescents: false,
      notes: null,
    },
  ],
  data_sources: [],
  systems: [],
  vendors: [],
  international_transfers: [],
};
function assessment(id: string, version: number) {
  return {
    id,
    series_id: series,
    organization_id: org,
    treatment_id: tid,
    version,
    status: "borrador",
    purpose_snapshot: "[FICTICIA] Finalidad de prueba",
    rat_context_hash: "a".repeat(64),
    rat_context_snapshot: detail,
    legal_basis: null,
    justification: "[FICTICIA] Fundamento inicial",
    lia_assessment: null,
    child_adolescent_assessment: null,
    eipd_resolution_assessment: null,
  };
}
function applicability(id: string) {
  return (
    determinations[id] ?? {
      organization_id: org,
      treatment_id: tid,
      assessment_id: id,
      context_hash: "a".repeat(64),
      revision: 0,
      current: false,
      editable: true,
      eipd: { state: "pendiente", reason: "" },
      infancia: { state: "pendiente", reason: "" },
      history: [],
      can_confirm: false,
      activation: "deshabilitada",
    }
  );
}
test.setTimeout(30000);
test.beforeAll(async () => {
  ({ directory, script, css } = await buildConnectedHarness([organization], "http://test.invalid"));
  viewerHarness = await buildConnectedHarness(
    [{ ...organization, role: "viewer" }],
    "http://test.invalid"
  );
  editorHarness = await buildConnectedHarness(
    [{ ...organization, role: "editor" }],
    "http://test.invalid"
  );
});
test.afterAll(async () => {
  if (directory) await rm(directory, { recursive: true, force: true });
  for (const harness of [viewerHarness, editorHarness]) {
    if (harness) await rm(harness.directory, { recursive: true, force: true });
  }
});
async function capture(page: Page, name: string) {
  const dir = process.env.CONNECTED_SCREENSHOTS;
  if (dir) {
    await mkdir(dir, { recursive: true });
    await page.screenshot({ path: path.join(dir, name), fullPage: false });
  }
}
async function visit(page: Page, hash = "", bundle = script) {
  await page.goto("http://localhost:3999/" + hash);
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: bundle });
  await expect(page.getByRole("heading", { name: "Panel principal", exact: true })).toBeVisible();
}
test.beforeEach(async ({ page }) => {
  records = { [aid]: assessment(aid, 1), [aid2]: assessment(aid2, 2) };
  determinations = {};
  calls = [];
  errors = [];
  mode = "ok";
  releaseValidation = undefined;
  releaseApplicability = undefined;
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("dialog", async (d) => (d.type() === "beforeunload" ? d.accept() : d.dismiss()));
  await page.route("**/*", async (route) => {
    const req = route.request(),
      url = new URL(req.url());
    if (url.hostname === "localhost")
      return route.fulfill({ contentType: "text/html", body: '<div id="root"></div>' });
    if (url.hostname !== "test.invalid") return route.abort();
    const headers = {
      "access-control-allow-origin": "*",
      "access-control-allow-headers": "*",
      "access-control-allow-methods": "GET,POST,PATCH,OPTIONS",
    };
    if (req.method() === "OPTIONS") return route.fulfill({ status: 204, headers });
    const pathname = url.pathname,
      method = req.method(),
      body = req.postDataJSON();
    calls.push({ path: pathname, method, org: req.headers()["x-organization-id"] ?? null, body });
    const result = (value: any, status = 200) =>
      route.fulfill({
        status,
        headers,
        contentType: "application/json",
        body: JSON.stringify(value),
      });
    if (mode === "deny" && pathname.startsWith("/rat"))
      return result({ detail: "PRUEBA sin acceso" }, 403);
    if (pathname === "/rat/treatments") return result([detail]);
    if (pathname === `/rat/treatments/${tid}`) {
      if (mode === "hold")
        await new Promise<void>((resolve) => {
          releaseValidation = resolve;
        });
      return result(detail);
    }
    if (pathname === "/diagnostico/cuestionario")
      return result({
        secciones: [
          { id: "s1", orden: 1, numero_romano: "I", nombre: "Sección inicial" },
          { id: "s2", orden: 2, numero_romano: "II", nombre: "Sección final" },
        ],
        preguntas: Array.from({ length: 50 }, (_, i) => ({
          id: `q${i + 1}`,
          seccion_id: i < 25 ? "s1" : "s2",
          orden: i + 1,
          texto: `[FICTICIA] Pregunta ${i + 1}`,
        })),
      });
    if (pathname === "/diagnostico/actual") return result({ detail: "No existe" }, 404);
    if (pathname.endsWith("/assessments"))
      return result(url.searchParams.get("offset") === "50" ? [] : Object.values(records));
    const match = pathname.match(/\/assessments\/([^/]+)/);
    const id = match?.[1] ?? aid;
    if (pathname.endsWith("/applicability")) {
      if (method === "GET" && mode === "app-readonly")
        return result({ ...applicability(id), editable: false });
      if (method === "GET" && mode === "app-offline") return route.abort("internetdisconnected");
      if (method === "GET" && ["app-hold-fail", "app-hold"].includes(mode)) {
        const fail = mode === "app-hold-fail";
        await new Promise<void>((resolve) => {
          releaseApplicability = resolve;
        });
        if (fail) return result({ detail: "PRUEBA determinación no disponible" }, 503);
      }
      if (method === "GET" && mode === "app-fail")
        return result({ detail: "PRUEBA determinación no disponible" }, 503);
      if (method === "POST") {
        const prev = applicability(id);
        if (mode === "conflict" || body.expected_revision !== prev.revision)
          return result({ detail: "PRUEBA cambio concurrente" }, 409);
        determinations[id] = {
          ...prev,
          ...body,
          revision: prev.revision + 1,
          current: true,
          history: [
            ...prev.history,
            {
              revision: prev.revision + 1,
              created_at: "2026-10-25T19:45:00+00:00",
              created_by: "a0000000-0000-0000-0000-000000000099",
              eipd: body.eipd,
              infancia: body.infancia,
            },
          ],
        };
      }
      return result(
        mode === "wrong-applicability"
          ? { ...applicability(id), assessment_id: aid2 }
          : applicability(id)
      );
    }
    if (pathname.endsWith("/support"))
      return result({
        schema_version: 1,
        organization_id: org,
        treatment_id: tid,
        assessment_id: id,
        document_hash: "a".repeat(64),
        risk_evaluation: null,
        risk_history: [],
        annexes: [],
        can_confirm: false,
        activation: "deshabilitada",
      });
    if (pathname.endsWith("/readiness"))
      return result({ assessment_id: id, rat_context_current: true, eipd_controls_v5: null });
    if (pathname.endsWith("/eipd-child/v4/resolutions")) return result([]);
    if (pathname.endsWith("/eipd-child/v4/policy"))
      return result({
        policy: {
          policy_schema_version: 1,
          policy_reference: mode === "9a-child" ? "m3-t1-infancia-pruebas-negativas-v1" : "PRUEBA",
          sources_status: "pendiente",
          acceptance_status: "pendiente",
          activation: "deshabilitada",
          allowed_decisions: ["requiere_cambios", "no_continuar"],
          global_policy_identity: {
            policy_version: 1,
            policy_reference: "PRUEBA",
            policy_hash: "d".repeat(64),
          },
        },
        policy_hash: "e".repeat(64),
        authorizes_action: false,
        can_confirm: false,
      });
    if (match && records[id] && pathname.endsWith(id)) {
      if (method === "PATCH") records[id] = { ...records[id], ...body };
      return result(records[id]);
    }
    return result({ detail: "Ruta de prueba no implementada" }, 404);
  });
  await visit(page);
});
const main = (page: Page) => page.locator("main.prototype-work");
async function mod(page: Page, name: string) {
  const mobile = page.getByRole("button", { name: "Abrir menú", exact: true });
  if (await mobile.isVisible()) await mobile.click();
  await page
    .getByRole("navigation", { name: "Módulos del espacio de trabajo" })
    .getByRole("button", { name, exact: true })
    .click();
}
async function section(page: Page, name: string) {
  const trigger = page.locator("header").getByRole("button", { name: "Secciones", exact: true });
  if (await trigger.isVisible()) {
    await trigger.click();
    await page
      .getByRole("dialog", { name: "Secciones del módulo", exact: true })
      .getByRole("button", { name, exact: true })
      .click();
  } else {
    const bar = page.locator(".connected-desktop-sections");
    const direct = bar.getByRole("link", { name, exact: true });
    if (await direct.count()) await direct.click();
    else {
      const group = bar
        .locator("details")
        .filter({ has: page.getByRole("button", { name, exact: true, includeHidden: true }) });
      await group.locator("summary").click();
      await group.getByRole("button", { name, exact: true }).click();
    }
  }
}
// A previously copied URL may still be opened while the menu explains a read failure.
async function openSavedRoute(page: Page, target: string, step = 0) {
  await page.evaluate(
    ({ target, step }) => {
      const params = new URLSearchParams(window.location.hash.split("?")[1]);
      params.delete("step");
      if (step) params.set("step", String(step));
      window.location.hash = `/licitud/${target}?${params}`;
    },
    { target, step }
  );
}
async function choose(page: Page, id = aid) {
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await dialog.getByLabel("Tratamiento del RAT", { exact: true }).selectOption(tid);
  await dialog.getByLabel("Finalidad de la evaluación", { exact: true }).selectOption(series);
  await dialog.getByLabel("Evaluación", { exact: true }).selectOption(id);
  await dialog.getByRole("button", { name: "Aplicar contexto", exact: true }).click();
  await expect(dialog).not.toBeVisible();
}
async function legal(page: Page) {
  await choose(page);
  await mod(page, "Bases de licitud");
  await expect(
    main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
}
async function enable(page: Page) {
  await main(page)
    .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
    .selectOption("corresponde");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Revisión manual");
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(
    main(page).getByText("Determinación guardada en el servidor.", { exact: true })
  ).toBeVisible();
}

test("catálogo de 50 preguntas, borrador entre módulos y contexto cancelado", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mod(page, "Autodiagnóstico");
  await expect(main(page).getByText("0 / 50 preguntas respondidas", { exact: true })).toBeVisible();
  await main(page)
    .getByPlaceholder("Notas u observaciones (opcional)")
    .first()
    .fill("[FICTICIA] Nota conservada");
  await section(page, "II. Sección final");
  await expect(main(page).getByText("[FICTICIA] Pregunta 50", { exact: true })).toBeVisible();
  await section(page, "I. Sección inicial");
  await mod(page, "Panel principal");
  await mod(page, "Autodiagnóstico");
  await expect(main(page).getByPlaceholder("Notas u observaciones (opcional)").first()).toHaveValue(
    "[FICTICIA] Nota conservada"
  );
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Cancelar", exact: true }).click();
  await expect(main(page).getByPlaceholder("Notas u observaciones (opcional)").first()).toHaveValue(
    "[FICTICIA] Nota conservada"
  );
  expect(errors).toEqual([]);
});
test("aplicabilidad guardada, aislamiento, enlaces y reapertura desde servidor", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1100, height: 900 });
  await legal(page);
  await page.locator("header").getByRole("button", { name: "Secciones", exact: true }).click();
  await expect(
    page
      .getByRole("dialog")
      .getByRole("button", { name: "Tratamiento y alcance de la EIPD", exact: true })
  ).toHaveCount(0);
  await page.keyboard.press("Escape");
  await enable(page);
  await capture(page, "conectada-aplicabilidad-escritorio.png");
  await section(page, "Medidas de mitigación");
  await expect(main(page).getByText("Determinar aplicabilidad", { exact: true })).not.toBeVisible();
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Borrador uno");
  await choose(page, aid2);
  await expect(
    main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
  await choose(page, aid);
  await section(page, "Base y fundamento");
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Borrador uno"
  );
  await page.reload();
  await page.addStyleTag({ content: css });
  await page.addScriptTag({ content: script });
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Fundamento inicial"
  );
  await section(page, "Determinar aplicabilidad");
  await expect(main(page).getByLabel("¿Corresponde documentar EIPD?", { exact: true })).toHaveValue(
    "corresponde"
  );
  expect(
    calls
      .filter((v) => v.path.endsWith("/applicability") && v.method === "POST")
      .every((v) => v.org === org)
  ).toBe(true);
  expect(errors).toEqual([]);
});
test("conflicto conserva determinación pendiente y no habilita menú", async ({ page }) => {
  await legal(page);
  mode = "conflict";
  await main(page)
    .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
    .selectOption("corresponde");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] No sobrescribir");
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(main(page).getByRole("alert")).toContainText("cambio concurrente");
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] No sobrescribir"
  );
  expect(Object.keys(determinations)).toHaveLength(0);
  expect(errors).toEqual([]);
});
test("móvil: foco, Escape, clic exterior y límites de pantalla", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await legal(page);
  await enable(page);
  await page.locator("header").getByRole("button", { name: "Secciones", exact: true }).click();
  const drawer = page.getByRole("dialog", { name: "Secciones del módulo", exact: true });
  await drawer.getByRole("button").last().focus();
  await page.keyboard.press("Escape");
  await expect(drawer).not.toBeVisible();
  await page.locator("header").getByRole("button", { name: "Secciones", exact: true }).click();
  await capture(page, "conectada-secciones-movil.png");
  const box = (await drawer.boundingBox())!;
  await page.mouse.click((box.width + 320) / 2, 300);
  await expect(drawer).not.toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});
test("contexto rechazado no se aplica ni produce escrituras", async ({ page }) => {
  mode = "deny";
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await expect(dialog.getByRole("alert")).toContainText("sin acceso");
  await expect(
    dialog.getByRole("button", { name: "Aplicar contexto", exact: true })
  ).toBeDisabled();
  await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("RAT conserva campos entre secciones y nueva actividad al volver del catálogo", async ({
  page,
}) => {
  await choose(page);
  await mod(page, "Inventario de tratamientos");
  await section(page, "Información general");
  const name = main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true });
  await name.fill("[FICTICIA] Nombre pendiente");
  await section(page, "Finalidades");
  await section(page, "Información general");
  await expect(name).toHaveValue("[FICTICIA] Nombre pendiente");
  await section(page, "Nueva actividad");
  const fresh = main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true });
  await fresh.fill("[FICTICIA] Nueva actividad pendiente");
  await section(page, "Inventario de tratamientos");
  await section(page, "Nueva actividad");
  await expect(
    main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true })
  ).toHaveValue("[FICTICIA] Nueva actividad pendiente");
  expect(errors).toEqual([]);
});

test("cancelar validación lenta impide que una respuesta tardía cambie el contexto", async ({
  page,
}) => {
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await dialog.getByLabel("Tratamiento del RAT", { exact: true }).selectOption(tid);
  await dialog.getByLabel("Finalidad de la evaluación", { exact: true }).selectOption(series);
  await dialog.getByLabel("Evaluación", { exact: true }).selectOption(aid);
  mode = "hold";
  await dialog.getByRole("button", { name: "Aplicar contexto", exact: true }).click();
  await expect.poll(() => !!releaseValidation).toBe(true);
  await expect(
    dialog.getByRole("button", { name: "Aplicar contexto", exact: true })
  ).toBeDisabled();
  await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
  const response = page.waitForResponse((v) => v.url().endsWith(`/rat/treatments/${tid}`));
  releaseValidation!();
  await response;
  await expect(page.locator("header")).not.toContainText("Actividad mixta");
  await expect(
    main(page).getByRole("heading", { name: "Panel principal", exact: true })
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test("Atrás y Adelante restauran evaluación sin mezclar borradores", async ({ page }) => {
  await legal(page);
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Contexto uno pendiente");
  await choose(page, aid2);
  await expect(
    main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
  await page.goBack();
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Contexto uno pendiente"
  );
  await page.goForward();
  await expect(
    main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test("cancelar cierre de sesión conserva el borrador del cuestionario", async ({ page }) => {
  await mod(page, "Autodiagnóstico");
  const note = main(page).getByPlaceholder("Notas u observaciones (opcional)").first();
  await note.fill("[FICTICIA] No descartar al cancelar salida");
  await page.getByRole("button", { name: "Cerrar sesión", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Salir del espacio de trabajo", exact: true });
  await expect(dialog).toBeVisible();
  await dialog.getByRole("button", { name: "Continuar editando", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(note).toHaveValue("[FICTICIA] No descartar al cancelar salida");
  expect(errors).toEqual([]);
});

test("respuesta de otra evaluación no habilita formularios ni permite guardar", async ({
  page,
}) => {
  mode = "wrong-applicability";
  await legal(page);
  await expect(main(page).getByRole("alert")).toContainText("no corresponde al contexto");
  await expect(
    main(page).getByRole("button", { name: "Guardar determinación", exact: true })
  ).toBeDisabled();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

for (const target of ["eipd", "infancia", "preparar"]) {
  test(`enlace directo a ${target}: carga, error visible y reintento`, async ({ page }) => {
    if (target !== "eipd")
      await page.setViewportSize({ width: target === "infancia" ? 390 : 320, height: 844 });
    determinations[aid] = {
      ...applicability(aid),
      current: true,
      revision: 1,
      eipd: { state: "corresponde", reason: "[FICTICIA] EIPD" },
      infancia: { state: "corresponde", reason: "[FICTICIA] Infancia" },
    };
    mode = "app-hold-fail";
    await page.evaluate((hash) => {
      window.location.hash = hash;
    }, `#/licitud/${target}?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid}`);
    await expect(main(page).getByRole("status")).toContainText(
      "Cargando evaluación y aplicabilidad"
    );
    await expect.poll(() => !!releaseApplicability).toBe(true);
    await capture(page, `lote1-${target}-cargando.png`);
    releaseApplicability!();
    await expect(main(page).getByRole("alert")).toContainText("PRUEBA determinación no disponible");
    await expect(
      main(page).getByRole("button", { name: "Ir a Determinar aplicabilidad", exact: true })
    ).toBeVisible();
    await capture(page, `lote1-${target}-error.png`);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    mode = "ok";
    await main(page).getByRole("button", { name: "Reintentar consulta", exact: true }).click();
    await expect(
      main(page).getByRole("alert").filter({ hasText: "No se pudo consultar la aplicabilidad" })
    ).not.toBeVisible();
    await expect(page.locator(".prototype-demo")).toBeVisible();
    await expect(page).toHaveURL(new RegExp(`/licitud/${target}\\?`));
    expect(calls.some((v) => v.method !== "GET")).toBe(false);
    expect(errors).toEqual([]);
  });
}

test("recuperar aplicabilidad conserva borradores de determinación y base", async ({ page }) => {
  await legal(page);
  await enable(page);
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Base pendiente conservada");
  await section(page, "Determinar aplicabilidad");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Determinación pendiente conservada");
  mode = "app-fail";
  await main(page)
    .getByRole("button", {
      name: "Consultar última determinación guardada",
      exact: true,
    })
    .click();
  await expect(main(page).getByRole("alert")).toContainText("PRUEBA determinación no disponible");
  await openSavedRoute(page, "eipd");
  await expect(main(page).getByRole("alert")).toContainText("PRUEBA determinación no disponible");
  await main(page)
    .getByRole("button", { name: "Ir a Determinar aplicabilidad", exact: true })
    .click();
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Determinación pendiente conservada"
  );
  mode = "ok";
  await main(page)
    .getByRole("button", {
      name: "Consultar última determinación guardada",
      exact: true,
    })
    .click();
  await expect(main(page).getByRole("alert")).not.toBeVisible();
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Determinación pendiente conservada"
  );
  await section(page, "Base y fundamento");
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Base pendiente conservada"
  );
  expect(calls.filter((v) => v.method === "POST")).toHaveLength(1);
  expect(errors).toEqual([]);
});

test("validación de enlace muestra carga fuera del diálogo y permite reintentar", async ({
  page,
}) => {
  mode = "hold";
  await page.evaluate((hash) => {
    window.location.hash = hash;
  }, `#/licitud/base?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid}`);
  await expect(page.getByRole("status")).toContainText(
    "Consultando evaluación y contexto autorizado"
  );
  await expect.poll(() => !!releaseValidation).toBe(true);
  mode = "deny";
  releaseValidation!();
  // The held treatment response is accepted; retry is exercised after a fresh denied link.
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toBeVisible();
  await page.evaluate((hash) => {
    window.location.hash = hash;
  }, `#/licitud/base?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid2}`);
  await expect(page.getByRole("alert")).toContainText("PRUEBA sin acceso");
  mode = "ok";
  await page.getByRole("button", { name: "Reintentar apertura", exact: true }).click();
  await expect(page.getByRole("alert")).not.toBeVisible();
  await expect(page).toHaveURL(new RegExp(`assessmentId=${aid2}`));
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("desconexión muestra ayuda en español y se recupera sin descartar el borrador", async ({
  page,
}) => {
  await legal(page);
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Texto pendiente durante desconexión");
  mode = "app-offline";
  await main(page)
    .getByRole("button", {
      name: "Consultar última determinación guardada",
      exact: true,
    })
    .click();
  await expect(main(page).getByRole("alert")).toContainText(
    "No se pudo conectar con el servidor. Revisa la conexión y vuelve a intentar."
  );
  await expect(main(page).getByRole("alert")).not.toContainText("Failed to fetch");
  mode = "ok";
  await main(page)
    .getByRole("button", {
      name: "Consultar última determinación guardada",
      exact: true,
    })
    .click();
  await expect(main(page).getByRole("alert")).not.toBeVisible();
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Texto pendiente durante desconexión"
  );
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

for (const width of [1280, 390]) {
  test(`contexto visible según módulo y retorno con borrador a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 844 });
    await legal(page);
    await section(page, "Base y fundamento");
    await main(page)
      .getByRole("textbox", { name: "Fundamento", exact: true })
      .fill("[FICTICIA] Lote 2 conservar");
    const context = page.getByTestId("connected-context-summary");
    await expect(context).toContainText("Organización: [FICTICIA] Organización conectada");
    await expect(context).toContainText("Tratamiento: [FICTICIA] Actividad mixta");
    await expect(context).toContainText("versión 1 · borrador");
    await page.getByRole("button", { name: "Ver contexto completo", exact: true }).click();
    const detailPanel = page.getByRole("dialog", { name: "Contexto seleccionado", exact: true });
    await expect(
      detailPanel.getByText("[FICTICIA] Finalidad de prueba", { exact: true })
    ).toBeVisible();
    await expect(detailPanel.getByText("versión 1 · borrador", { exact: true })).toBeVisible();
    await page.keyboard.press("Escape");
    for (const moduleName of ["Autodiagnóstico", "Mi organización", "Panel principal"]) {
      await mod(page, moduleName);
      await expect(context).toHaveText("Organización: [FICTICIA] Organización conectada");
    }
    await mod(page, "Inventario de tratamientos");
    await expect(context).toContainText("Tratamiento: [FICTICIA] Actividad mixta");
    await expect(context).not.toContainText("Finalidad");
    await expect(context).not.toContainText("versión");
    await mod(page, "Bases de licitud");
    await expect(context).toContainText("versión 1 · borrador");
    await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
      "[FICTICIA] Lote 2 conservar"
    );
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await capture(page, `lote2-contexto-licitud-${width}.png`);
    expect(calls.some((v) => v.method !== "GET")).toBe(false);
    expect(errors).toEqual([]);
  });
}

test("Continuar identifica evaluación y versión recordadas sin cambiar el destino", async ({
  page,
}) => {
  await legal(page);
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Continuar versión uno");
  await choose(page, aid2);
  await section(page, "Base y fundamento");
  await main(page)
    .getByRole("textbox", { name: "Fundamento", exact: true })
    .fill("[FICTICIA] Continuar versión dos");
  await mod(page, "Panel principal");
  const resume = main(page).getByRole("button", { name: /^Continuar en Base y fundamento/ });
  await expect(resume).toContainText("Organización: [FICTICIA] Organización conectada");
  await expect(resume).toContainText("Tratamiento: [FICTICIA] Actividad mixta");
  await expect(resume).toContainText(
    "Finalidad y evaluación: [FICTICIA] Finalidad de prueba · versión 2 · borrador"
  );
  await expect(page.getByTestId("connected-context-summary")).not.toContainText("versión");
  await page.setViewportSize({ width: 320, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await capture(page, "lote2-continuar-320.png");
  await resume.click();
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Continuar versión dos"
  );
  await choose(page, aid);
  await section(page, "Base y fundamento");
  await expect(main(page).getByRole("textbox", { name: "Fundamento", exact: true })).toHaveValue(
    "[FICTICIA] Continuar versión uno"
  );
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("Continuar al Autodiagnóstico identifica organización y conserva su ámbito", async ({
  page,
}) => {
  await legal(page);
  await mod(page, "Autodiagnóstico");
  await main(page)
    .getByPlaceholder("Notas u observaciones (opcional)")
    .first()
    .fill("[FICTICIA] Diagnóstico organizacional");
  await mod(page, "Panel principal");
  const resume = main(page).getByRole("button", { name: /^Continuar en/ });
  await expect(resume).toContainText("Organización: [FICTICIA] Organización conectada");
  await expect(resume).not.toContainText("Actividad mixta");
  await expect(resume).not.toContainText("versión");
  await resume.click();
  await expect(main(page).getByPlaceholder("Notas u observaciones (opcional)").first()).toHaveValue(
    "[FICTICIA] Diagnóstico organizacional"
  );
  await expect(page.getByTestId("connected-context-summary")).toHaveText(
    "Organización: [FICTICIA] Organización conectada"
  );
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("Guardar determinación explica requisitos faltantes y los actualiza sin escribir", async ({
  page,
}) => {
  await legal(page);
  const save = main(page).getByRole("button", { name: "Guardar determinación", exact: true });
  await expect(save).toBeDisabled();
  await expect(save).toHaveAccessibleDescription(/declaración de datos ficticios/);
  await main(page)
    .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
    .selectOption("corresponde");
  await expect(save).toHaveAccessibleDescription(/fundamento sobre EIPD/);
  await save.scrollIntoViewIfNeeded();
  await expect(save).toHaveText("Guardar determinación");
  await page.evaluate(
    () =>
      new Promise<void>((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
      )
  );
  await capture(page, "lote3-requisitos-faltantes.png");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Análisis de prueba");
  await expect(save).not.toHaveAccessibleDescription(/fundamento sobre EIPD/);
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await expect(save).toBeEnabled();
  await expect(save).toHaveAccessibleDescription(/Requisitos completos/);
  await main(page)
    .getByLabel("¿Corresponde documentar infancia y adolescencia?", { exact: true })
    .selectOption("informacion_insuficiente");
  await expect(save).toBeDisabled();
  await expect(save).toHaveAccessibleDescription(/fundamento sobre infancia y adolescencia/);
  await main(page)
    .getByLabel("Fundamento sobre infancia y adolescencia", { exact: true })
    .fill("[FICTICIA] Información pendiente de contraste");
  await expect(save).toBeEnabled();
  await capture(page, "lote3-requisitos-completos.png");
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("evaluación de solo consulta explica el bloqueo indicado por servidor", async ({ page }) => {
  mode = "app-readonly";
  await legal(page);
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toBeDisabled();
  await expect(
    main(page).getByRole("button", { name: "Guardar determinación", exact: true })
  ).toHaveAccessibleDescription(/evaluación.*solo consulta/);
  await expect(
    main(page).getByText(/El servidor indica que esta evaluación es de solo consulta/)
  ).toBeVisible();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("rol de consulta ve motivos en aplicabilidad, RAT y organización sin escrituras", async ({
  page,
}) => {
  await visit(page, "", viewerHarness.script);
  await legal(page);
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toBeDisabled();
  await expect(
    main(page).getByRole("button", { name: "Guardar determinación", exact: true })
  ).toHaveAccessibleDescription(/Tu rol permite solo consulta/);
  await mod(page, "Inventario de tratamientos");
  await section(page, "Información general");
  await expect(
    main(page).getByText(
      "Tu rol permite solo consulta del RAT; no puedes crear ni modificar actividades de tratamiento.",
      { exact: true }
    )
  ).toBeVisible();
  await expect(
    main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true })
  ).toBeDisabled();
  await mod(page, "Mi organización");
  await expect(
    main(page).getByText(
      "Tu rol permite consultar los datos de la organización, pero no modificarlos.",
      { exact: true }
    )
  ).toBeVisible();
  await expect(main(page).getByLabel("Nombre de la organización", { exact: true })).toBeDisabled();
  await page.setViewportSize({ width: 320, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await capture(page, "lote3-organizacion-consulta-320.png");
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("editor puede editar RAT pero recibe explicación de solo consulta en organización", async ({
  page,
}) => {
  await visit(page, "", editorHarness.script);
  await choose(page);
  await mod(page, "Inventario de tratamientos");
  await section(page, "Información general");
  await expect(
    main(page).getByRole("textbox", { name: "Nombre de la actividad *", exact: true })
  ).toBeEnabled();
  await mod(page, "Mi organización");
  await expect(main(page).getByLabel("Nombre de la organización", { exact: true })).toBeDisabled();
  await expect(
    main(page).getByText(
      "Tu rol permite consultar los datos de la organización, pero no modificarlos.",
      { exact: true }
    )
  ).toBeVisible();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("contexto explica dependencia y evaluación faltante conservando selección opcional", async ({
  page,
}) => {
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await expect(
    dialog.getByLabel("Finalidad de la evaluación", { exact: true })
  ).toHaveAccessibleDescription(/Selecciona primero un tratamiento/);
  await expect(dialog.getByLabel("Evaluación", { exact: true })).toHaveAccessibleDescription(
    /después una finalidad/
  );
  const apply = dialog.getByRole("button", { name: "Aplicar contexto", exact: true });
  await expect(apply).toBeEnabled();
  await expect(apply).toHaveAccessibleDescription(/Puedes aplicar solo la organización/);
  await dialog.getByLabel("Tratamiento del RAT", { exact: true }).selectOption(tid);
  await expect(dialog.getByLabel("Finalidad de la evaluación", { exact: true })).toBeEnabled();
  await expect(apply).toHaveAccessibleDescription(/Puedes aplicar organización y tratamiento/);
  await dialog.getByLabel("Finalidad de la evaluación", { exact: true }).selectOption(series);
  await expect(apply).toBeDisabled();
  await expect(apply).toHaveAccessibleDescription(
    /Selecciona una evaluación para la finalidad elegida/
  );
  await capture(page, "lote3-evaluacion-faltante.png");
  await dialog.getByLabel("Evaluación", { exact: true }).selectOption(aid);
  await expect(apply).toBeEnabled();
  await expect(apply).toHaveAccessibleDescription(/El contexto está listo/);
  await capture(page, "lote3-contexto-requisitos.png");
  await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

const availability = (page: Page) =>
  main(page).getByRole("region", { name: "Disponibilidad de formularios", exact: true });
const relocation = (page: Page) =>
  main(page).getByRole("region", { name: "Cambio de sección", exact: true });
for (const state of ["pendiente", "corresponde", "no_corresponde", "informacion_insuficiente"]) {
  test(`resultado guardado explica accesos para ambos temas: ${state}`, async ({ page }) => {
    await legal(page);
    await expect(availability(page)).toContainText("Sin determinación guardada");
    for (const topic of ["EIPD", "infancia y adolescencia"]) {
      await main(page)
        .getByLabel(`¿Corresponde documentar ${topic}?`, { exact: true })
        .selectOption(state);
      if (state !== "pendiente")
        await main(page)
          .getByLabel(`Fundamento sobre ${topic}`, { exact: true })
          .fill(`[FICTICIA] Análisis ${topic}`);
    }
    await expect(
      availability(page).getByRole("button", { name: "Completar EIPD", exact: true })
    ).not.toBeVisible();
    await main(page)
      .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
      .check();
    await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
    await expect(
      main(page).getByText("Determinación guardada en el servidor.", { exact: true })
    ).toBeVisible();
    await expect(availability(page)).toContainText("Accesos según la determinación guardada");
    for (const topic of ["EIPD", "infancia y adolescencia"]) {
      const button = availability(page).getByRole("button", {
        name: `Completar ${topic}`,
        exact: true,
      });
      if (state === "corresponde") await expect(button).toBeVisible();
      else await expect(button).not.toBeVisible();
    }
    if (state === "corresponde") {
      await main(page)
        .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
        .selectOption("no_corresponde");
      await availability(page).getByRole("button", { name: "Completar EIPD", exact: true }).click();
      await expect(page).toHaveURL(/\/licitud\/eipd\?/);
    } else {
      await expect(availability(page)).toContainText("El formulario no está habilitado");
      await availability(page)
        .getByRole("button", { name: "Ir a Documentos guardados", exact: true })
        .click();
      await expect(page).toHaveURL(/\/licitud\/revisar\?/);
    }
    expect(calls.filter((v) => v.method === "POST")).toHaveLength(1);
    expect(errors).toEqual([]);
  });
}

test("resultado positivo de EIPD no habilita infancia y ofrece acceso directo", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await expect(
    availability(page).getByRole("button", { name: "Completar EIPD", exact: true })
  ).toBeVisible();
  await expect(
    availability(page).getByRole("button", {
      name: "Completar infancia y adolescencia",
      exact: true,
    })
  ).not.toBeVisible();
  await availability(page).scrollIntoViewIfNeeded();
  await capture(page, "lote4-resultado-eipd.png");
  await availability(page).getByRole("button", { name: "Completar EIPD", exact: true }).click();
  await expect(page).toHaveURL(/\/licitud\/eipd\?/);
  expect(calls.filter((v) => v.method === "POST")).toHaveLength(1);
  expect(errors).toEqual([]);
});
for (const target of ["eipd", "infancia", "preparar"]) {
  test(`reubicación desde ${target} explica causa y conserva borradores`, async ({ page }) => {
    if (target !== "eipd")
      await page.setViewportSize({ width: target === "infancia" ? 390 : 320, height: 844 });
    determinations[aid] = {
      ...applicability(aid),
      current: true,
      revision: 1,
      eipd: { state: "corresponde", reason: "[FICTICIA] EIPD guardada" },
      infancia: { state: "corresponde", reason: "[FICTICIA] Infancia guardada" },
    };
    await legal(page);
    if (target === "eipd") {
      await section(page, "Tratamiento y alcance de la EIPD");
      await main(page)
        .getByRole("textbox", { name: "Notas del borrador EIPD (opcional)", exact: true })
        .fill("[FICTICIA] Conservar al reubicar");
      await section(page, "Determinar aplicabilidad");
    }
    mode = "app-hold";
    await main(page)
      .getByRole("button", {
        name: "Consultar última determinación guardada",
        exact: true,
      })
      .click();
    await expect.poll(() => !!releaseApplicability).toBe(true);
    await openSavedRoute(page, target);
    const topic = target === "eipd" ? "eipd" : "infancia";
    determinations[aid] = {
      ...determinations[aid],
      revision: 2,
      [topic]: { state: "no_corresponde", reason: "[FICTICIA] Cambio guardado" },
    };
    mode = "ok";
    releaseApplicability!();
    await expect(relocation(page)).toContainText("No corresponde");
    await expect(relocation(page)).toContainText("se conservan durante esta visita");
    await expect(
      relocation(page).getByRole("button", { name: "Ir a Documentos guardados", exact: true })
    ).toBeVisible();
    await expect(page).toHaveURL(/\/licitud\/aplicabilidad\?/);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await capture(page, `lote4-reubicacion-${target}.png`);
    if (target === "eipd") {
      await expect(relocation(page)).toContainText("Hay cambios sin guardar en esta evaluación");
      determinations[aid] = {
        ...determinations[aid],
        revision: 3,
        eipd: { state: "corresponde", reason: "[FICTICIA] Aplicabilidad restaurada" },
      };
      await main(page)
        .getByRole("button", {
          name: "Consultar última determinación guardada",
          exact: true,
        })
        .click();
      await expect(relocation(page)).not.toBeVisible();
      await availability(page).getByRole("button", { name: "Completar EIPD", exact: true }).click();
      await expect(
        main(page).getByRole("textbox", { name: "Notas del borrador EIPD (opcional)", exact: true })
      ).toHaveValue("[FICTICIA] Conservar al reubicar");
    }
    expect(calls.some((v) => v.method !== "GET")).toBe(false);
    expect(errors).toEqual([]);
  });
}

test("determinación desasociada explica revisión y conserva acceso a consulta", async ({
  page,
}) => {
  determinations[aid] = {
    ...applicability(aid),
    revision: 1,
    current: false,
    eipd: { state: "corresponde", reason: "[FICTICIA] Alcance anterior" },
  };
  await page.evaluate((hash) => {
    window.location.hash = hash;
  }, `#/licitud/eipd?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid}`);
  await expect(relocation(page)).toContainText("requiere revisión");
  await expect(availability(page)).toContainText("requiere revisión");
  await expect(
    availability(page).getByRole("button", { name: "Completar EIPD", exact: true })
  ).not.toBeVisible();
  await expect(
    availability(page).getByRole("button", { name: "Ir a Documentos guardados", exact: true })
  ).toBeVisible();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("enlace sin determinación explica ausencia de guardado y permite cerrar el aviso", async ({
  page,
}) => {
  await page.evaluate((hash) => {
    window.location.hash = hash;
  }, `#/licitud/eipd?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid}`);
  await expect(relocation(page)).toContainText("todavía no hay una determinación guardada");
  await expect(relocation(page)).not.toContainText("requiere revisión");
  await expect(availability(page)).toContainText("Sin determinación guardada");
  await relocation(page).getByRole("button", { name: "Cerrar aviso", exact: true }).click();
  await expect(relocation(page)).not.toBeVisible();
  await expect(availability(page)).toBeVisible();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

const storedDraft = (page: Page) =>
  main(page).getByRole("region", {
    name: "Estado guardado y borrador de aplicabilidad",
    exact: true,
  });
const querySaved = (page: Page) =>
  main(page).getByRole("button", { name: "Consultar última determinación guardada", exact: true });
function serverDetermination(revision: number, reason = "[FICTICIA] Fundamento del servidor") {
  const value = {
    ...applicability(aid),
    current: true,
    revision,
    eipd: { state: "corresponde", reason },
    infancia: { state: "pendiente", reason: "" },
  };
  return {
    ...value,
    history: [
      ...value.history.filter((v: any) => v.revision !== revision),
      {
        revision,
        created_at: "2026-10-25T19:45:00+00:00",
        created_by: "a0000000-0000-0000-0000-000000000099",
        eipd: value.eipd,
        infancia: value.infancia,
      },
    ],
  };
}
test("lote 5: distingue ausencia de registro y consulta sin escrituras", async ({ page }) => {
  await legal(page);
  await expect(storedDraft(page)).toContainText("Todavía no hay una determinación guardada");
  await expect(storedDraft(page)).not.toContainText("Registrada por");
  await expect(querySaved(page)).toHaveAccessibleDescription(
    /Conserva tus cambios pendientes y no guarda el formulario/
  );
  await querySaved(page).focus();
  await page.keyboard.press("Enter");
  await expect(main(page).getByRole("status")).toContainText("Consulta completada");
  await expect(
    main(page).getByText("Determinación guardada en el servidor.", { exact: true })
  ).not.toBeVisible();
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});
test("lote 5: presenta revisión fecha y autor real disponible sin inventar nombre", async ({
  page,
}) => {
  determinations[aid] = serverDetermination(1);
  await legal(page);
  await expect(storedDraft(page)).toContainText("Revisión de aplicabilidad 1");
  await expect(storedDraft(page)).toContainText("a0000000-0000-0000-0000-000000000099");
  await expect(storedDraft(page)).toContainText(/25.*oct.*2026/);
  await expect(storedDraft(page)).toContainText("16:45");
  await expect(storedDraft(page)).toContainText("no entrega su nombre");
  await expect(storedDraft(page)).toContainText("El formulario coincide");
  await main(page).getByText("Historial de determinaciones (1)", { exact: true }).click();
  const history = main(page)
    .locator("details")
    .filter({ has: page.locator("summary", { hasText: "Historial de determinaciones" }) });
  await expect(history).toContainText("Revisión de aplicabilidad 1");
  await expect(history).toContainText("Registrada por (identificador)");
  await expect(history).not.toContainText("Versión 1");
  expect(errors).toEqual([]);
});
test("lote 5: consulta limpia carga lo guardado y retira éxito de escritura anterior", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  determinations[aid] = serverDetermination(2, "[FICTICIA] Nueva determinación externa");
  const posts = calls.filter((v) => v.method === "POST").length;
  await querySaved(page).click();
  await expect(storedDraft(page)).toContainText("Revisión de aplicabilidad 2");
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Nueva determinación externa"
  );
  await expect(
    main(page).getByText("Determinación guardada en el servidor.", { exact: true })
  ).not.toBeVisible();
  await expect(main(page).getByRole("status")).toContainText(
    "El formulario muestra la determinación consultada"
  );
  expect(calls.filter((v) => v.method === "POST")).toHaveLength(posts);
  expect(errors).toEqual([]);
});
test("lote 5: conflicto abre historial y consulta compara sin reemplazar borrador", async ({
  page,
}) => {
  determinations[aid] = serverDetermination(1);
  await legal(page);
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Mi borrador local");
  determinations[aid] = serverDetermination(2, "[FICTICIA] Guardado por otra ventana");
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(main(page).getByRole("alert")).toContainText("cambio concurrente");
  const history = main(page)
    .locator("details")
    .filter({ has: page.locator("summary", { hasText: "Historial de determinaciones" }) });
  await expect(history).toHaveAttribute("open", "");
  await expect(storedDraft(page)).toContainText("Revisión de aplicabilidad 1");
  await querySaved(page).click();
  await expect(storedDraft(page)).toContainText("Revisión de aplicabilidad 2");
  await expect(storedDraft(page)).toContainText("[FICTICIA] Guardado por otra ventana");
  await expect(storedDraft(page)).toContainText("[FICTICIA] Mi borrador local");
  await expect(storedDraft(page)).toContainText("Difiere de lo consultado");
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Mi borrador local"
  );
  await expect(main(page).getByRole("alert")).not.toBeVisible();
  expect(calls.filter((v) => v.method === "POST")).toHaveLength(1);
  expect(determinations[aid].eipd.reason).toBe("[FICTICIA] Guardado por otra ventana");
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(storedDraft(page)).toContainText("Revisión de aplicabilidad 3");
  const writes = calls.filter((v) => v.method === "POST");
  expect(writes[1].body.expected_revision).toBe(2);
  expect(writes[1].body.eipd.reason).toBe("[FICTICIA] Mi borrador local");
  expect(errors).toEqual([]);
});
test("lote 5: confirmación adyacente a Guardar se retira al editar y ante error de consulta", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  const savedNotice = main(page).getByText("Determinación guardada en el servidor.", {
    exact: true,
  });
  expect(await savedNotice.evaluate((e) => e.nextElementSibling?.textContent)).toBe(
    "Guardar determinación"
  );
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Edición posterior");
  await expect(savedNotice).not.toBeVisible();
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(savedNotice).toBeVisible();
  mode = "app-fail";
  await querySaved(page).click();
  await expect(main(page).getByRole("alert")).toContainText("determinación no disponible");
  await expect(savedNotice).not.toBeVisible();
  mode = "ok";
  await querySaved(page).click();
  await expect(main(page).getByRole("alert")).not.toBeVisible();
  await expect(savedNotice).not.toBeVisible();
  expect(calls.filter((v) => v.method === "POST")).toHaveLength(2);
  expect(errors).toEqual([]);
});
test("lote 5: fallo de guardado conserva ambos temas sin confirmación falsa", async ({ page }) => {
  await legal(page);
  await enable(page);
  for (const topic of ["EIPD", "infancia y adolescencia"]) {
    await main(page)
      .getByLabel(`¿Corresponde documentar ${topic}?`, { exact: true })
      .selectOption("informacion_insuficiente");
    await main(page)
      .getByLabel(`Fundamento sobre ${topic}`, { exact: true })
      .fill(`[FICTICIA] Pendiente ${topic}`);
  }
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  mode = "conflict";
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(main(page).getByRole("alert")).toBeVisible();
  await expect(
    main(page).getByText("Determinación guardada en el servidor.", { exact: true })
  ).not.toBeVisible();
  for (const topic of ["EIPD", "infancia y adolescencia"]) {
    await expect(main(page).getByLabel(`Fundamento sobre ${topic}`, { exact: true })).toHaveValue(
      `[FICTICIA] Pendiente ${topic}`
    );
  }
  await expect(availability(page)).toContainText("EIPD: Corresponde");
  expect(determinations[aid].revision).toBe(1);
  expect(errors).toEqual([]);
});
test("lote 5: metadatos ausentes o fecha inválida no inventan fecha ni autor", async ({ page }) => {
  determinations[aid] = { ...serverDetermination(1), history: [] };
  await legal(page);
  await expect(storedDraft(page)).toContainText("Fecha no disponible");
  await expect(storedDraft(page)).toContainText("Registrada por (identificador): No disponible");
  determinations[aid] = serverDetermination(2);
  determinations[aid].history[0].created_at = "fecha inválida";
  await querySaved(page).click();
  await expect(storedDraft(page)).toContainText("Fecha no disponible");
  await expect(storedDraft(page)).not.toContainText("Invalid Date");
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});
for (const width of [1280, 390, 320]) {
  test(`lote 5: comparación consulta y guardado legibles a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    determinations[aid] = serverDetermination(1);
    await legal(page);
    await main(page)
      .getByLabel("Fundamento sobre EIPD", { exact: true })
      .fill("[FICTICIA] Conservar mi análisis antes de guardar");
    await querySaved(page).focus();
    await expect(querySaved(page)).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(storedDraft(page)).toContainText("Tu borrador tiene cambios sin guardar");
    for (const topic of ["EIPD", "infancia y adolescencia"]) {
      await expect(
        storedDraft(page).getByText(`¿Corresponde documentar ${topic}?:`, { exact: true })
      ).toHaveCount(2);
      await expect(
        storedDraft(page).getByText(`Fundamento sobre ${topic}:`, { exact: true })
      ).toHaveCount(2);
    }
    await storedDraft(page).scrollIntoViewIfNeeded();
    await capture(page, `lote5-comparacion-${width}.png`);
    await querySaved(page).scrollIntoViewIfNeeded();
    await capture(page, `lote5-consulta-${width}.png`);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    await main(page)
      .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
      .check();
    await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
    const notice = main(page).getByText("Determinación guardada en el servidor.", { exact: true });
    await expect(notice).toBeVisible();
    expect(await notice.evaluate((e) => e.nextElementSibling?.textContent)).toBe(
      "Guardar determinación"
    );
    await capture(page, `lote5-guardado-${width}.png`);
    expect(errors).toEqual([]);
  });
}

test("lote 5: consulta lenta bloquea duplicados y conserva el borrador tras terminar", async ({
  page,
}) => {
  determinations[aid] = serverDetermination(1);
  await legal(page);
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Análisis durante consulta");
  const before = calls.filter(
    (v) => v.path.endsWith("/applicability") && v.method === "GET"
  ).length;
  mode = "app-hold";
  await querySaved(page).click();
  await expect.poll(() => !!releaseApplicability).toBe(true);
  await expect(
    main(page).getByRole("button", { name: "Consultando determinación…", exact: true })
  ).toBeDisabled();
  await expect(
    main(page).getByRole("button", { name: "Guardar determinación", exact: true })
  ).toBeDisabled();
  mode = "ok";
  releaseApplicability!();
  await expect(querySaved(page)).toBeEnabled();
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Análisis durante consulta"
  );
  await expect(main(page).getByRole("status")).toContainText(
    "Tus cambios pendientes se conservaron"
  );
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Nuevo cambio después de consultar");
  await expect(main(page).getByText(/Consulta completada/)).not.toBeVisible();
  expect(calls.filter((v) => v.path.endsWith("/applicability") && v.method === "GET")).toHaveLength(
    before + 1
  );
  expect(calls.some((v) => v.method !== "GET")).toBe(false);
  expect(errors).toEqual([]);
});

test("6A destinos únicos directos con nombre común y sin escrituras", async ({ page }) => {
  await legal(page);
  const header = page.locator("header");
  const documents = header.getByRole("link", { name: "Documentos guardados", exact: true });
  await expect(documents).toHaveAttribute("href", new RegExp(`assessmentId=${aid}`));
  await expect(header.locator("summary").filter({ hasText: "Revisar y decidir" })).toHaveCount(0);
  await documents.focus();
  await documents.press("Enter");
  await expect(page).toHaveURL(/#\/licitud\/revisar\?/);
  await expect(
    main(page).getByRole("heading", { name: "Documentos guardados", exact: true })
  ).toBeVisible();
  await expect(page.getByTestId("connected-destination")).toHaveText(
    "Bases de licitud › Documentos guardados"
  );
  await expect(documents).toHaveAttribute("aria-current", "page");
  await capture(page, "6a-documentos-escritorio.png");
  const history = header.getByRole("link", { name: "Historial y descargas", exact: true });
  await history.click();
  await expect(
    main(page).getByRole("heading", { name: "Historial y descargas", exact: true })
  ).toBeVisible();
  await expect(history).toHaveAttribute("aria-current", "page");
  await expect(documents).not.toHaveAttribute("aria-current");
  await page.goBack();
  await expect(documents).toHaveAttribute("aria-current", "page");
  await page.goForward();
  await expect(history).toHaveAttribute("aria-current", "page");
  expect(calls.filter((call) => call.method !== "GET")).toEqual([]);
  expect(errors).toEqual([]);
});

test("6A grupos múltiples y nota EIPD conservada al consultar y continuar", async ({ page }) => {
  await legal(page);
  await enable(page);
  const writes = calls.filter((call) => call.method !== "GET").length;
  const header = page.locator("header");
  const group = header
    .locator("details")
    .filter({ has: page.locator("summary", { hasText: "Completar EIPD" }) });
  await group.locator("summary").click();
  await expect(group.getByRole("button")).toHaveCount(7);
  await group
    .getByRole("button", { name: "Tratamiento y alcance de la EIPD", exact: true })
    .click();
  const note = main(page).getByRole("textbox", {
    name: "Notas del borrador EIPD (opcional)",
    exact: true,
  });
  await note.fill("[FICTICIA] Nota del bloque 6A sin guardar");
  await expect(group).toHaveAttribute("data-current-group", "true");
  await group.locator("summary").click();
  await expect(
    group.getByRole("button", { name: "Tratamiento y alcance de la EIPD", exact: true })
  ).toHaveAttribute("aria-current", "page");
  await group.getByRole("button", { name: "Describir riesgos", exact: true }).click();
  await expect(page).toHaveURL(/step=2/);
  await group.locator("summary").click();
  await expect(
    group.getByRole("button", { name: "Describir riesgos", exact: true })
  ).toHaveAttribute("aria-current", "page");
  await group
    .getByRole("button", { name: "Tratamiento y alcance de la EIPD", exact: true })
    .click();
  await header.getByRole("link", { name: "Documentos guardados", exact: true }).click();
  await mod(page, "Panel principal");
  await main(page)
    .getByRole("button", { name: /^Continuar en Documentos guardados/ })
    .click();
  await expect(
    main(page).getByRole("heading", { name: "Documentos guardados", exact: true })
  ).toBeVisible();
  await page.goBack();
  await expect(
    main(page).getByRole("heading", { name: "Panel principal", exact: true })
  ).toBeVisible();
  await page.goBack();
  await expect(
    main(page).getByRole("heading", { name: "Documentos guardados", exact: true })
  ).toBeVisible();
  await page.goBack();
  await expect(note).toHaveValue("[FICTICIA] Nota del bloque 6A sin guardar");
  await expect(page).toHaveURL(new RegExp(`assessmentId=${aid}`));
  expect(calls.filter((call) => call.method !== "GET")).toHaveLength(writes);
  expect(errors).toEqual([]);
});

for (const width of [390, 320]) {
  test(`6A Secciones conserva destino activo y nombre en ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 844 });
    await legal(page);
    await section(page, "Documentos guardados");
    await expect(
      main(page).getByRole("heading", { name: "Documentos guardados", exact: true })
    ).toBeVisible();
    await expect(page.getByTestId("connected-destination")).toContainText("Documentos guardados");
    await page.getByRole("button", { name: "Secciones", exact: true }).click();
    const drawer = page.getByRole("dialog", { name: "Secciones del módulo", exact: true });
    await expect(
      drawer.getByRole("button", { name: "Documentos guardados", exact: true })
    ).toHaveAttribute("aria-current", "page");
    await capture(page, `6a-secciones-${width}.png`);
    await page.keyboard.press("Escape");
    await expect(drawer).not.toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    expect(calls.filter((call) => call.method !== "GET")).toEqual([]);
    expect(errors).toEqual([]);
  });
}

test("6A enlace anterior conserva IDs y nombre único del inventario", async ({ page }) => {
  const hash = `#/licitud/revisar?organizationId=${org}&treatmentId=${tid}&assessmentId=${aid}`;
  await visit(page, hash);
  await expect(
    main(page).getByRole("heading", { name: "Documentos guardados", exact: true })
  ).toBeVisible();
  await expect(page).toHaveURL(new RegExp(`assessmentId=${aid}$`));
  await mod(page, "Inventario de tratamientos");
  await section(page, "Inventario de tratamientos");
  await expect(
    main(page).getByRole("heading", { name: "Inventario de tratamientos", exact: true })
  ).toBeVisible();
  await expect(page.getByTestId("connected-destination")).toHaveText(
    "Inventario de tratamientos › Inventario de tratamientos"
  );
  await section(page, "Información general");
  await expect(
    main(page).getByRole("heading", { name: "Información general", exact: true })
  ).toBeVisible();
  expect(calls.filter((call) => call.method !== "GET")).toEqual([]);
  expect(errors).toEqual([]);
});

for (const scenario of [
  {
    name: "sin registro",
    revision: 0,
    current: false,
    state: "pendiente",
    reason: "Todavía no hay una determinación guardada",
  },
  {
    name: "pendiente",
    revision: 1,
    current: true,
    state: "pendiente",
    reason: "Pendiente de analizar",
  },
  {
    name: "no corresponde",
    revision: 1,
    current: true,
    state: "no_corresponde",
    reason: "No corresponde",
  },
  {
    name: "información insuficiente",
    revision: 1,
    current: true,
    state: "informacion_insuficiente",
    reason: "Información insuficiente",
  },
  {
    name: "asociación por revisar",
    revision: 1,
    current: false,
    state: "corresponde",
    reason: "revisar su asociación",
  },
]) {
  test(`6B disponibilidad explica ${scenario.name} sin ofrecer editor`, async ({ page }) => {
    determinations[aid] = {
      ...applicability(aid),
      revision: scenario.revision,
      current: scenario.current,
      eipd: { state: scenario.state, reason: "[FICTICIA]" },
      infancia: { state: scenario.state, reason: "[FICTICIA]" },
    };
    await legal(page);
    const group = page
      .locator("header details")
      .filter({ has: page.locator("summary", { hasText: "EIPD: disponibilidad" }) });
    await group.locator("summary").click();
    await expect(group).toContainText(scenario.reason);
    await expect(
      group.getByRole("button", { name: "Tratamiento y alcance de la EIPD", exact: true })
    ).toHaveCount(0);
    await group.getByRole("button", { name: "Ir a Determinar aplicabilidad", exact: true }).click();
    await expect(
      main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
    ).toBeVisible();
    await expect(
      main(page).getByRole("button", {
        name: "Consultar última determinación guardada",
        exact: true,
      })
    ).toBeVisible();
    expect(calls.filter((call) => call.method !== "GET")).toEqual([]);
    expect(errors).toEqual([]);
  });
}

test("6B disponibilidad de cada tema depende de lo guardado y no del borrador", async ({
  page,
}) => {
  determinations[aid] = serverDetermination(1);
  await legal(page);
  const header = page.locator("header");
  const eipdGroup = header
    .locator("details")
    .filter({ has: page.locator("summary", { hasText: "Completar EIPD" }) });
  await main(page)
    .getByLabel("¿Corresponde documentar infancia y adolescencia?", { exact: true })
    .selectOption("corresponde");
  await main(page)
    .getByLabel("Fundamento sobre infancia y adolescencia", { exact: true })
    .fill("[FICTICIA] Sin guardar");
  const childGroup = header.locator("details").filter({
    has: page.locator("summary", { hasText: "Infancia y adolescencia: disponibilidad" }),
  });
  await childGroup.locator("summary").click();
  await expect(childGroup).toContainText("Pendiente de analizar");
  await expect(
    childGroup.getByRole("button", { name: "Completar infancia y adolescencia", exact: true })
  ).toHaveCount(0);
  await eipdGroup.locator("summary").click();
  await expect(eipdGroup.getByRole("button")).toHaveCount(7);
  await eipdGroup.getByRole("button", { name: "Describir riesgos", exact: true }).click();
  await expect(page).toHaveURL(/step=2/);
  await expect(
    main(page).getByRole("heading", { name: "Describir riesgos", exact: true })
  ).toBeVisible();
  await section(page, "Tratamiento y alcance de la EIPD");
  await main(page)
    .getByRole("textbox", { name: "Nombre de la edición (texto libre)", exact: true })
    .fill("[FICTICIA] Edición libre");
  await expect(main(page)).toContainText("no registra otra versión ni una revisión documental");
  await section(page, "Determinar aplicabilidad");
  await expect(
    main(page).getByLabel("Fundamento sobre infancia y adolescencia", { exact: true })
  ).toHaveValue("[FICTICIA] Sin guardar");
  expect(determinations[aid].revision).toBe(1);
  expect(calls.filter((call) => call.method !== "GET")).toEqual([]);
});

test("6B cargar y fallar la consulta no se presentan como No corresponde", async ({ page }) => {
  determinations[aid] = serverDetermination(1);
  await legal(page);
  mode = "app-hold-fail";
  await querySaved(page).click();
  await expect.poll(() => !!releaseApplicability).toBe(true);
  const group = page
    .locator("header details")
    .filter({ has: page.locator("summary", { hasText: "EIPD: disponibilidad" }) });
  await group.locator("summary").click();
  await expect(group).toContainText("Consultando la determinación guardada");
  await expect(
    group.getByRole("button", { name: "Tratamiento y alcance de la EIPD", exact: true })
  ).toHaveCount(0);
  releaseApplicability!();
  await expect(group).toContainText("No se pudo consultar la disponibilidad");
  await expect(group).not.toContainText("indica «No corresponde»");
  mode = "ok";
  await group.getByRole("button", { name: "Ir a Determinar aplicabilidad", exact: true }).click();
  await querySaved(page).click();
  await expect(page.locator("header summary").filter({ hasText: "Completar EIPD" })).toBeVisible();
  expect(calls.filter((call) => call.method !== "GET")).toEqual([]);
});

for (const width of [1280, 390, 320]) {
  test(`6B disponibilidad visible y legible en ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    determinations[aid] = serverDetermination(1);
    await legal(page);
    if (width < 768) {
      await page.getByRole("button", { name: "Secciones", exact: true }).click();
      const drawer = page.getByRole("dialog", { name: "Secciones del módulo", exact: true });
      await expect(drawer).toContainText("Infancia y adolescencia: disponibilidad");
      await expect(drawer).toContainText("Pendiente de analizar");
      await drawer.getByText(/La determinación guardada está/).scrollIntoViewIfNeeded();
      await expect(
        drawer.getByRole("button", { name: "Completar infancia y adolescencia", exact: true })
      ).toHaveCount(0);
    } else {
      const group = page.locator("header details").filter({
        has: page.locator("summary", { hasText: "Infancia y adolescencia: disponibilidad" }),
      });
      await group.locator("summary").click();
      await expect(group).toContainText("Pendiente de analizar");
    }
    await capture(page, `6b-disponibilidad-${width}.png`);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
    expect(calls.filter((call) => call.method !== "GET")).toEqual([]);
  });
}

test("7A escritorio cierra el grupo al salir con Tab y abre solo el siguiente", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  const writes = calls.filter((v) => v.method !== "GET").length;
  const nav = page.locator(".connected-desktop-sections");
  const prepare = nav.locator("summary").filter({ hasText: /^Preparar$/ });
  const eipd = nav.locator("summary").filter({ hasText: /^Completar EIPD$/ });
  await prepare.focus();
  await page.keyboard.press("Enter");
  await expect(prepare.locator("..")).toHaveAttribute("open", "");
  await page.keyboard.press("Tab");
  await expect(
    nav.getByRole("button", { name: "Evaluaciones y creación de borrador", exact: true })
  ).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(prepare).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(prepare.locator("..")).not.toHaveAttribute("open", "");
  await expect(prepare).toBeFocused();
  await page.keyboard.press("Space");
  for (let i = 0; i < 6; i++) await page.keyboard.press("Tab");
  await expect(eipd).toBeFocused();
  await expect(prepare.locator("..")).not.toHaveAttribute("open", "");
  await page.keyboard.press("Enter");
  await expect(nav.locator("details[open]")).toHaveCount(1);
  await page.keyboard.press("Tab");
  await expect(
    nav.getByRole("button", { name: "Tratamiento y alcance de la EIPD", exact: true })
  ).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(eipd).toBeFocused();
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
});

test("7A abrir otro desplegable no deja dos abiertos y salir de navegación conserva foco", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  const nav = page.locator(".connected-desktop-sections");
  const prepare = nav.locator("summary").filter({ hasText: /^Preparar$/ });
  const eipd = nav.locator("summary").filter({ hasText: /^Completar EIPD$/ });
  await prepare.focus();
  await page.keyboard.press("Enter");
  await eipd.focus();
  await page.keyboard.press("Space");
  await expect(nav.locator("details[open]")).toHaveCount(1);
  const help = main(page).getByLabel("Fundamento sobre EIPD", { exact: true });
  await help.focus();
  await expect(nav.locator("details[open]")).toHaveCount(0);
  await expect(help).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(help).toBeFocused();
});

async function tabTo(page: Page, target: import("@playwright/test").Locator) {
  for (let i = 0; i < 50; i++) {
    if (await target.evaluate((element) => element === document.activeElement)) return;
    await page.keyboard.press("Tab");
  }
  await expect(target).toBeFocused();
}
for (const width of [390, 320]) {
  test(`7A paneles con teclado, fondo, foco y borrador conservado a ${width}px`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 844 });
    await legal(page);
    await enable(page);
    await section(page, "Tratamiento y alcance de la EIPD");
    const note = main(page).getByLabel("Notas del borrador EIPD (opcional)", { exact: true });
    await note.fill("[FICTICIA] Conservar en recorrido 7A");
    const writes = calls.filter((v) => v.method !== "GET").length;
    const menu = page.getByRole("button", { name: "Abrir menú", exact: true });
    const sections = page.locator("header").getByRole("button", { name: "Secciones", exact: true });
    for (const [trigger, name, closeName] of [
      [menu, "Menú principal", "Cerrar menú"],
      [sections, "Secciones del módulo", "Cerrar secciones"],
    ] as const) {
      await trigger.focus();
      await page.keyboard.press("Enter");
      const drawer = page.getByRole("dialog", { name, exact: true });
      const close = drawer.getByRole("button", { name: closeName, exact: true });
      await expect(close).toBeFocused();
      await expect(close).toHaveCSS("outline-style", "solid");
      await page.keyboard.press("Shift+Tab");
      await expect(drawer.getByRole("button").last()).toBeFocused();
      await page.keyboard.press("Tab");
      await expect(close).toBeFocused();
      await drawer
        .getByText(name === "Menú principal" ? "CumpleIA" : name, { exact: true })
        .click();
      await expect(drawer).toBeVisible();
      await page.keyboard.press("Escape");
      await expect(drawer).toBeHidden();
      await expect(trigger).toBeFocused();
      await page.keyboard.press("Space");
      await expect(drawer).toBeVisible();
      const box = (await drawer.boundingBox())!;
      await page.mouse.click((box.x + box.width + width) / 2, 400);
      await expect(drawer).toBeHidden();
      await expect(trigger).toBeFocused();
    }
    await sections.press("Enter");
    const drawer = page.getByRole("dialog", { name: "Secciones del módulo", exact: true });
    const target = drawer.getByRole("button", {
      name: "Necesidad y proporcionalidad",
      exact: true,
    });
    await tabTo(page, target);
    await page.keyboard.press("Enter");
    await expect(drawer).toBeHidden();
    await expect(main(page)).toBeFocused();
    const header = (await page.locator("header").boundingBox())!;
    const work = (await main(page).boundingBox())!;
    expect(work.y).toBeGreaterThanOrEqual(header.y + header.height - 1);
    await menu.press("Enter");
    await tabTo(
      page,
      page
        .getByRole("dialog", { name: "Menú principal", exact: true })
        .getByRole("button", { name: "Panel principal", exact: true })
    );
    await page.keyboard.press("Space");
    await expect(main(page)).toBeFocused();
    await menu.press("Enter");
    await tabTo(
      page,
      page
        .getByRole("dialog", { name: "Menú principal", exact: true })
        .getByRole("button", { name: "Bases de licitud", exact: true })
    );
    await page.keyboard.press("Enter");
    await sections.press("Enter");
    await tabTo(
      page,
      drawer.getByRole("button", { name: "Tratamiento y alcance de la EIPD", exact: true })
    );
    await page.keyboard.press("Enter");
    await expect(note).toHaveValue("[FICTICIA] Conservar en recorrido 7A");
    expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
    expect(errors).toEqual([]);
    await capture(page, `7a-retorno-${width}.png`);
  });
}

test("7A selección de escritorio coloca el foco bajo la cabecera y Escape no roba foco al formulario", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  const nav = page.locator(".connected-desktop-sections");
  const summary = nav.locator("summary").filter({ hasText: /^Completar EIPD$/ });
  await summary.focus();
  await page.keyboard.press("Enter");
  await page.keyboard.press("Tab");
  await page.keyboard.press("Space");
  await expect(main(page)).toBeFocused();
  await expect(nav.locator("details[open]")).toHaveCount(0);
  const header = (await page.locator("header").boundingBox())!;
  expect((await main(page).boundingBox())!.y).toBeGreaterThanOrEqual(header.y + header.height - 1);
  const note = main(page).getByLabel("Notas del borrador EIPD (opcional)", { exact: true });
  await note.fill("[FICTICIA] Foco de edición 7A");
  const writes = calls.filter((v) => v.method !== "GET").length;
  await page.keyboard.press("Escape");
  await expect(note).toBeFocused();
  await page.keyboard.press("End");
  await page.keyboard.press("ArrowLeft");
  await expect(note).toHaveValue("[FICTICIA] Foco de edición 7A");
  const context = page.getByRole("button", { name: "Cambiar contexto", exact: true });
  await summary.focus();
  await page.keyboard.press("Enter");
  await context.focus();
  await page.keyboard.press("Enter");
  await expect(nav.locator("details[open]")).toHaveCount(0);
  await page.keyboard.press("Escape");
  await expect(context).toBeFocused();
  await expect(note).toHaveValue("[FICTICIA] Foco de edición 7A");
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
  await capture(page, "7a-escritorio.png");
});

test("7A al pasar a estrecho el foco de un desplegable vuelve a Secciones visible", async ({
  page,
}) => {
  await legal(page);
  const summary = page
    .locator(".connected-desktop-sections summary")
    .filter({ hasText: /^Preparar$/ });
  await summary.focus();
  await page.keyboard.press("Enter");
  await page.keyboard.press("Tab");
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(
    page.locator("header").getByRole("button", { name: "Secciones", exact: true })
  ).toBeFocused();
  await expect(page.locator(".connected-desktop-sections details[open]")).toHaveCount(0);
});

test("7A Espacio explícito abre y cierra una vez sin depender de la activación nativa", async ({
  page,
}) => {
  await legal(page);
  const summary = page
    .locator(".connected-desktop-sections summary")
    .filter({ hasText: /^Preparar$/ });
  const group = summary.locator("..");
  const beforeUrl = page.url();
  const writes = calls.filter((v) => v.method !== "GET").length;
  await summary.focus();
  // Synthetic events have no native activation: the control must handle Space itself.
  await summary.dispatchEvent("keydown", { key: " ", code: "Space", repeat: false });
  await expect(group).toHaveAttribute("open", "");
  await summary.dispatchEvent("keydown", { key: " ", code: "Space", repeat: true });
  await expect(group).toHaveAttribute("open", "");
  await summary.dispatchEvent("keyup", { key: " ", code: "Space" });
  await expect(group).toHaveAttribute("open", "");
  await expect(summary).toBeFocused();
  await summary.dispatchEvent("keydown", { key: " ", code: "Space", repeat: false });
  await summary.dispatchEvent("keyup", { key: " ", code: "Space" });
  await expect(group).not.toHaveAttribute("open", "");
  // Real key down/up must not trigger both our handler and the native toggle.
  await page.keyboard.press("Space");
  await expect(group).toHaveAttribute("open", "");
  await page.keyboard.press("Space");
  await expect(group).not.toHaveAttribute("open", "");
  await expect(summary).toBeFocused();
  expect(page.url()).toBe(beforeUrl);
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
  expect(errors).toEqual([]);
});

async function expectAccessibleReferences(page: Page) {
  const invalid = await page.evaluate(() => {
    const attributes = ["aria-labelledby", "aria-describedby", "aria-controls", "aria-owns"];
    return Array.from(
      document.querySelectorAll<HTMLElement>(attributes.map((a) => `[${a}]`).join(","))
    )
      .filter((element) => element.getClientRects().length > 0)
      .flatMap((element) =>
        attributes.flatMap((attribute) =>
          (element.getAttribute(attribute) ?? "")
            .split(/\s+/)
            .filter(Boolean)
            .flatMap((id) => {
              const targets = Array.from(document.querySelectorAll<HTMLElement>("[id]")).filter(
                (node) => node.id === id
              );
              return targets.length !== 1 ||
                (attribute === "aria-labelledby" && targets[0].getClientRects().length === 0)
                ? [`${attribute}: ${id} (${targets.length} destinos)`]
                : [];
            })
        )
      );
  });
  expect(invalid).toEqual([]);
}

test("7B un main real con nombre y título por destino dentro de la envoltura del dashboard", async ({
  page,
}) => {
  await expect(page.locator("main")).toHaveCount(1);
  await expect(page.getByRole("main", { name: "Panel principal", exact: true })).toBeVisible();
  await expect(
    page.getByRole("navigation", { name: "Módulos del espacio de trabajo", exact: true })
  ).toBeVisible();
  await expect(
    page.getByRole("navigation", { name: "Módulos de la maqueta", exact: true })
  ).toHaveCount(0);
  await legal(page);
  await expect(page.locator("main")).toHaveCount(1);
  await expect(
    page.getByRole("main", { name: "Área de trabajo: Determinar aplicabilidad", exact: true })
  ).toBeVisible();
  await expect(
    page.getByRole("heading", {
      level: 1,
      name: "Área de trabajo: Determinar aplicabilidad",
      exact: true,
    })
  ).toHaveCount(1);
  await expect(page).toHaveTitle("Determinar aplicabilidad · Bases de licitud | CumpleIA");
  await expectAccessibleReferences(page);
  await section(page, "Documentos guardados");
  await expect(main(page).getByRole("tabpanel")).toHaveCount(0);
  await expect(
    main(page).getByRole("region", { name: "Documentos guardados de la evaluación", exact: true })
  ).toBeVisible();
  await expectAccessibleReferences(page);
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(0);
});

for (const width of [1100, 390]) {
  test(`7B paneles relacionados, título, foco y ayuda consultable a ${width}px`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 844 });
    await legal(page);
    const trigger = page.locator("header").getByRole("button", { name: "Secciones", exact: true });
    await trigger.focus();
    await page.keyboard.press("Enter");
    await expect(trigger).toHaveAttribute("aria-expanded", "true");
    const id = await trigger.getAttribute("aria-controls");
    await expect(
      page.getByRole("dialog", { name: "Secciones del módulo", exact: true })
    ).toHaveAttribute("id", id!);
    await expectAccessibleReferences(page);
    await page.keyboard.press("Escape");
    await expect(trigger).toBeFocused();
    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    const query = main(page).getByRole("button", {
      name: "Consultar última determinación guardada",
      exact: true,
    });
    await query.focus();
    await expect(query).toHaveAccessibleDescription(
      /Conserva tus cambios pendientes y no guarda el formulario/
    );
    await expect(
      main(page).getByRole("button", { name: "Guardar determinación", exact: true })
    ).toHaveAccessibleDescription(/declaración de datos ficticios/);
    await capture(page, `7b-ayuda-${width}.png`);
    expect(calls.filter((v) => v.method !== "GET")).toHaveLength(0);
  });
}

test("7B evaluaciones montadas mantienen identificadores únicos y ayudas en su contexto", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  const note = main(page).getByRole("textbox", {
    name: "Notas del borrador EIPD (opcional)",
    exact: true,
  });
  await note.fill("[FICTICIA] Conservar contexto accesible 7B");
  await expect(
    main(page).getByLabel("Nombre de la edición (texto libre)", { exact: true })
  ).toHaveAccessibleDescription(/No es el identificador ni el número de versión/);
  const writes = calls.filter((v) => v.method !== "GET").length;
  await choose(page, aid2);
  await expect(
    main(page).getByRole("heading", { name: "Determinar aplicabilidad", exact: true })
  ).toBeVisible();
  await section(page, "Documentos guardados");
  await expectAccessibleReferences(page);
  await choose(page, aid);
  await section(page, "Necesidad y proporcionalidad");
  const response = main(page).getByLabel("Necesario para la finalidad", { exact: true });
  await expect(response).toHaveAccessibleDescription(/Sin declarar/);
  await response.selectOption("pendiente");
  await expect(response).toHaveAccessibleDescription(/Pendiente: usa esta opción/);
  await expectAccessibleReferences(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  await expect(note).toHaveValue("[FICTICIA] Conservar contexto accesible 7B");
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
  expect(errors).toEqual([]);
});

test("7B estado confirmado explica consulta sin atribuirla falsamente al rol", async ({ page }) => {
  records[aid].status = "confirmado";
  determinations[aid] = {
    ...applicability(aid),
    revision: 1,
    current: true,
    editable: false,
    eipd: { state: "corresponde", reason: "[FICTICIA] Prueba de consulta" },
  };
  await legal(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  const field = main(page).getByLabel("Referencia del documento EIPD", { exact: true });
  await expect(field).toBeDisabled();
  await expect(
    main(page).getByRole("group", {
      name: "Documento de consulta · evaluación versión 1",
      exact: true,
    })
  ).toHaveAccessibleDescription(/solo puede editarse mientras la evaluación está en borrador/);
  await expect(
    main(page).getByText(
      "Tu rol permite consultar este documento, pero no editarlo ni guardarlo.",
      { exact: true }
    )
  ).toHaveCount(0);
  await expectAccessibleReferences(page);
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(0);
});

test.describe("7B interacción táctil", () => {
  test.use({ hasTouch: true, viewport: { width: 390, height: 844 } });
  test("metodología se puede abrir y cerrar tocando su encabezado sin guardar", async ({
    page,
  }) => {
    await legal(page);
    await enable(page);
    await section(page, "Valorar riesgos");
    const writes = calls.filter((v) => v.method !== "GET").length;
    const summary = main(page).getByText("Metodología CUMPLEIA-CUALITATIVA-1 y criterios", {
      exact: true,
    });
    await summary.tap();
    await expect(summary.locator("..")).toHaveAttribute("open", "");
    await expect(main(page).getByRole("table")).toBeVisible();
    await summary.tap();
    await expect(summary.locator("..")).not.toHaveAttribute("open", "");
    await summary.focus();
    await page.keyboard.press("Enter");
    await expect(main(page).getByRole("table")).toBeVisible();
    await page.keyboard.press("Enter");
    await expect(summary.locator("..")).not.toHaveAttribute("open", "");
    await expect(summary).toBeFocused();
    expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
  });
});

for (const width of [1280, 390, 320]) {
  for (const longNames of [false, true]) {
    test(`8A cabecera y primer campo a ${width}px nombres ${longNames ? "largos" : "normales"}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      const original = detail.name;
      try {
        if (longNames) {
          detail.name =
            "[FICTICIA] Actividad de atención y seguimiento de solicitudes de participantes con un nombre extendido para comprobar el contexto seleccionado";
          records[aid].purpose_snapshot =
            "[FICTICIA] Finalidad extensa para comprobar la lectura completa del contexto y la identificación de la evaluación elegida sin perder acceso al formulario ni a las acciones de navegación durante esta prueba controlada.";
        }
        await legal(page);
        await enable(page);
        await section(page, "Tratamiento y alcance de la EIPD");
        await page.evaluate(() => window.scrollTo(0, 0));
        const field = main(page).getByRole("textbox", {
          name: "Referencia del documento EIPD",
          exact: true,
        });
        const metrics = {
          header: (await page.locator("header").boundingBox())!.height,
          fieldY: (await field.boundingBox())!.y,
        };
        const key = `${width}-${longNames ? "largos" : "normales"}`;
        const dir = process.env.CONTEXT_EVIDENCE;
        if (dir) {
          await mkdir(dir, { recursive: true });
          if (process.env.CONTEXT_BEFORE === "1") {
            await writeFile(path.join(dir, `antes-${key}.json`), JSON.stringify(metrics));
            await page.screenshot({ path: path.join(dir, `antes-${key}.png`) });
            return;
          }
          const before = JSON.parse(await readFile(path.join(dir, `antes-${key}.json`), "utf8"));
          expect(metrics.header).toBeLessThanOrEqual(before.header);
          expect(metrics.fieldY).toBeLessThan(before.fieldY);
          await writeFile(
            path.join(dir, `despues-${key}.json`),
            JSON.stringify({ before, after: metrics })
          );
          await page.screenshot({ path: path.join(dir, `despues-${key}.png`) });
        }
        await expect(
          main(page).getByRole("complementary", { name: "Alcance de la evaluación", exact: true })
        ).toHaveCount(0);
        await expect(field).toBeVisible();
        await page.getByRole("button", { name: "Ver contexto completo", exact: true }).click();
        const contextDetail = page.getByRole("dialog", {
          name: "Contexto seleccionado",
          exact: true,
        });
        await expect(contextDetail.getByText(detail.name, { exact: true })).toBeVisible();
        await expect(
          contextDetail.getByText(records[aid].purpose_snapshot, { exact: true })
        ).toBeVisible();
        await expect(
          contextDetail.getByText("versión 1 · borrador", { exact: true })
        ).toBeVisible();
        await expectAccessibleReferences(page);
        if (dir && longNames) await page.screenshot({ path: path.join(dir, `detalle-${key}.png`) });
        await page.keyboard.press("Escape");

        expect(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)
        ).toBeTruthy();
      } finally {
        detail.name = original;
      }
    });
  }
}

for (const width of [1280, 390]) {
  test(`8A detalle de contexto conserva borrador y foco a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await legal(page);
    await enable(page);
    await section(page, "Tratamiento y alcance de la EIPD");
    const note = main(page).getByRole("textbox", {
      name: "Notas del borrador EIPD (opcional)",
      exact: true,
    });
    await note.fill("[FICTICIA] Conservar al consultar contexto 8A");
    const writes = calls.filter((v) => v.method !== "GET").length;
    const url = page.url();
    const trigger = page.getByRole("button", { name: "Ver contexto completo", exact: true });
    await trigger.focus();
    await page.keyboard.press("Enter");
    const panel = page.getByRole("dialog", { name: "Contexto seleccionado", exact: true });
    await expect(panel).toBeVisible();
    const close = panel.getByRole("button", { name: "Cerrar detalle", exact: true });
    await expect(close).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(close).toBeFocused();
    await expectAccessibleReferences(page);
    await page.keyboard.press("Escape");
    await expect(panel).toBeHidden();
    await expect(trigger).toBeFocused();
    await expect(note).toHaveValue("[FICTICIA] Conservar al consultar contexto 8A");
    await trigger.click();
    await page
      .locator(".prototype-drawer-backdrop:visible")
      .click({ position: { x: width - 4, y: 450 } });
    await expect(panel).toBeHidden();
    await expect(trigger).toBeFocused();
    expect(page.url()).toBe(url);
    expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
  });
}

test("8A distingue evaluación activa de versión documental histórica", async ({ page }) => {
  const historic = {
    id: "b0000000-0000-0000-0000-000000000001",
    organization_id: org,
    treatment_id: tid,
    assessment_id: aid2,
    version: 1,
    resolution_binding_version: 4,
    stored_coverage: "contexto_v4",
    data_kind: "ficticios",
    document: {
      schema_version: 1,
      document_reference: "SIMULADA-8A-HISTORICA-001",
      document_version: "[FICTICIA] Edición histórica",
      notes: "[FICTICIA] Documento conservado",
    },
    context_snapshot: {
      context_schema_version: 4,
      organization_id: org,
      treatment_id: tid,
      assessment_id: aid2,
      child_adolescent_assessment: { assessment: { schema_version: 1 } },
    },
    document_hash: "a".repeat(64),
    context_hash: "b".repeat(64),
    child_material_hash: "c".repeat(64),
    created_by: org,
    created_at: "2026-10-16T10:00:00Z",
    authorizes_action: false,
    can_confirm: false,
  };
  await page.route("**/eipd-child/v4/resolutions", async (route) => {
    if (route.request().method() === "OPTIONS") return route.fallback();
    return route.fulfill({
      contentType: "application/json",
      headers: { "access-control-allow-origin": "*" },
      body: JSON.stringify([historic]),
    });
  });
  await page.route("**/eipd-child/v4/resolutions/*/reviews", async (route) => {
    if (route.request().method() === "OPTIONS") return route.fallback();
    return route.fulfill({
      contentType: "application/json",
      headers: { "access-control-allow-origin": "*" },
      body: "[]",
    });
  });
  await page.route("**/eipd-child/v4/policy", async (route) => {
    if (route.request().method() === "OPTIONS") return route.fallback();
    return route.fulfill({
      contentType: "application/json",
      headers: { "access-control-allow-origin": "*" },
      body: JSON.stringify({
        policy: {
          policy_schema_version: 1,
          policy_reference: "m3-t1-infancia-pruebas-negativas-v1",
          sources_status: "pendiente",
          acceptance_status: "pendiente",
          activation: "deshabilitada",
          allowed_decisions: ["requiere_cambios", "no_continuar"],
          global_policy_identity: {
            policy_version: 1,
            policy_reference: "PRUEBA",
            policy_hash: "d".repeat(64),
          },
        },
        policy_hash: "e".repeat(64),
        authorizes_action: false,
        can_confirm: false,
      }),
    });
  });
  await choose(page, aid2);
  await mod(page, "Bases de licitud");
  await section(page, "Documentos guardados");

  await main(page)
    .getByRole("button", { name: "Consultar versión documental 1", exact: true })
    .click();
  await expect(
    main(page).getByRole("heading", {
      name: "Versión documental de infancia 1 consultada",
      exact: true,
    })
  ).toBeVisible();
  await expect(main(page).getByText("SIMULADA-8A-HISTORICA-001", { exact: true })).toBeVisible();
  await expect(page.getByTestId("connected-context-summary")).toContainText("versión 2 · borrador");
  await page.getByRole("button", { name: "Ver contexto completo", exact: true }).click();
  await expect(
    page
      .getByRole("dialog", { name: "Contexto seleccionado", exact: true })
      .getByText("versión 2 · borrador", { exact: true })
  ).toBeVisible();
  await page.keyboard.press("Escape");
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(0);
  expect(errors).toEqual([]);
});

test.describe("8A consulta táctil", () => {
  test.use({ hasTouch: true, viewport: { width: 390, height: 844 } });
  test("detalle completo se consulta y cierra mediante toque sin cambiar selección", async ({
    page,
  }) => {
    await legal(page);
    const url = page.url();
    await page.getByRole("button", { name: "Ver contexto completo", exact: true }).tap();
    const panel = page.getByRole("dialog", { name: "Contexto seleccionado", exact: true });
    await expect(panel.getByText("[FICTICIA] Finalidad de prueba", { exact: true })).toBeVisible();
    await panel.getByRole("button", { name: "Cerrar detalle", exact: true }).tap();
    await expect(panel).toBeHidden();
    expect(page.url()).toBe(url);
    expect(calls.filter((v) => v.method !== "GET")).toHaveLength(0);
  });
});

for (const width of [320, 390, 865, 1100, 1280, 1920]) {
  test(`8B siete pasos con una vía principal a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await legal(page);
    await enable(page);
    const writes = calls.filter((v) => v.method !== "GET").length;
    const labels = [
      "Tratamiento y alcance de la EIPD",
      "Necesidad y proporcionalidad",
      "Describir riesgos",
      "Valorar riesgos",
      "Medidas de mitigación",
      "Fuentes y evidencias",
      "Riesgo residual y seguimiento",
    ];
    await expect(
      page.locator("header").getByRole("button", { name: "Secciones", exact: true })
    ).toBeVisible({ visible: width < 1200 });
    for (const [index, label] of labels.entries()) {
      await section(page, label);
      await expect(main(page).getByRole("heading", { name: label, exact: true })).toBeVisible();
      await expect(
        main(page).getByText(`Paso ${index + 1} de 7 · Completar EIPD`, { exact: true })
      ).toBeVisible();
      await expect(
        main(page).getByRole("navigation", { name: "Pasos documentales EIPD" })
      ).toHaveCount(0);
      expect(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)
      ).toBeTruthy();
    }
    await section(page, labels[2]);
    const note = main(page).getByRole("textbox", {
      name: "Notas del borrador EIPD (opcional)",
      exact: true,
    });
    await note.fill("[FICTICIA] Conservar recorrido 8B");
    await main(page)
      .getByRole("button", { name: "Siguiente: Valorar riesgos →", exact: true })
      .click();
    await expect(
      main(page).getByText("Paso 4 de 7 · Completar EIPD", { exact: true })
    ).toBeVisible();
    await main(page)
      .getByRole("button", { name: "Siguiente: Medidas de mitigación →", exact: true })
      .click();
    await expect(
      main(page).getByText("Paso 5 de 7 · Completar EIPD", { exact: true })
    ).toBeVisible();
    await page.goBack();
    await expect(
      main(page).getByText("Paso 4 de 7 · Completar EIPD", { exact: true })
    ).toBeVisible();
    await page.goForward();
    await expect(
      main(page).getByText("Paso 5 de 7 · Completar EIPD", { exact: true })
    ).toBeVisible();
    await section(page, labels[2]);
    await expect(note).toHaveValue("[FICTICIA] Conservar recorrido 8B");
    await expectAccessibleReferences(page);
    await capture(page, `8b-${width}.png`);
    expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
  });
}

test("8B al ampliar ventana el panel cierra y devuelve foco a la barra visible", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1100, height: 900 });
  await legal(page);
  await enable(page);
  await section(page, "Describir riesgos");
  await page.getByRole("button", { name: "Secciones", exact: true }).click();
  await expect(
    page.getByRole("dialog", { name: "Secciones del módulo", exact: true })
  ).toBeVisible();
  await page.setViewportSize({ width: 1600, height: 900 });
  await expect(
    page.getByRole("dialog", { name: "Secciones del módulo", exact: true })
  ).toBeHidden();
  await expect(
    page.locator(".connected-desktop-sections details[data-current-group] > summary")
  ).toBeFocused();
  await expect(main(page).getByText("Paso 3 de 7 · Completar EIPD", { exact: true })).toBeVisible();
});

for (const width of [320, 390, 865, 1100, 1199]) {
  test(`8B Escape cierra Secciones en aperturas repetidas a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await legal(page);
    await enable(page);
    await section(page, "Describir riesgos");
    const note = main(page).getByRole("textbox", {
      name: "Notas del borrador EIPD (opcional)",
      exact: true,
    });
    await note.fill("[FICTICIA] Repetir Escape 8B");
    const writes = calls.filter((v) => v.method !== "GET").length;
    const trigger = page.getByRole("button", { name: "Secciones", exact: true });
    const panel = page.getByRole("dialog", { name: "Secciones del módulo", exact: true });
    for (let cycle = 0; cycle < 5; cycle++) {
      await trigger.click();
      await expect(panel).toBeVisible();
      await expect(
        panel.getByRole("button", { name: "Cerrar secciones", exact: true })
      ).toBeFocused();
      await page.keyboard.press("Escape");
      await expect(panel).toBeHidden();
      await expect(trigger).toBeFocused();
      await note.click();
      await page.keyboard.press("Escape");
      await expect(note).toBeFocused();
      await expect(note).toHaveValue("[FICTICIA] Repetir Escape 8B");
    }
    expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
    expect(errors).toEqual([]);
  });
}

const pendingButton = (page: Page, count: number) =>
  page.getByRole("button", { name: `Ver pendientes (${count})`, exact: true });
const pendingDialog = (page: Page) =>
  page.getByRole("dialog", { name: "Unidades de trabajo pendientes", exact: true });

test("9A consulta inicial no implica guardado ni crea pendientes", async ({ page }) => {
  await legal(page);
  await expect(pendingButton(page, 0)).toBeVisible();
  await pendingButton(page, 0).click();
  await expect(
    pendingDialog(page).getByText("No hay cambios pendientes informados.", { exact: false })
  ).toBeVisible();
  await expect(pendingDialog(page).getByText("Guardado confirmado", { exact: true })).toHaveCount(
    0
  );
  await expect(pendingDialog(page).locator("li")).toHaveCount(0);
  await page.keyboard.press("Escape");
  await expect(pendingButton(page, 0)).toBeFocused();
  expect(calls.filter((v) => v.method !== "GET")).toEqual([]);
  expect(errors).toEqual([]);
});

test("9A determinación y siete pasos EIPD cuentan dos unidades; guardar limpia solo una", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  await main(page)
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] Pendiente EIPD 9A");
  await expect(pendingButton(page, 1)).toBeVisible();
  await section(page, "Necesidad y proporcionalidad");
  await expect(pendingButton(page, 1)).toBeVisible();
  await section(page, "Describir riesgos");
  await expect(pendingButton(page, 1)).toBeVisible();
  await section(page, "Determinar aplicabilidad");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Determinación pendiente 9A");
  await expect(pendingButton(page, 2)).toBeVisible();
  await pendingButton(page, 2).click();
  await expect(pendingDialog(page).locator("li")).toHaveCount(2);
  await expect(
    pendingDialog(page).getByRole("heading", { name: "Borrador EIPD · siete pasos" })
  ).toBeVisible();
  await expect(
    pendingDialog(page).getByRole("heading", { name: "Determinación de aplicabilidad" })
  ).toBeVisible();
  await expect(pendingDialog(page).locator("li").first()).toContainText(
    "[FICTICIA] Finalidad de prueba"
  );
  await expect(
    pendingDialog(page).getByText("[FICTICIA] Pendiente EIPD 9A", { exact: true })
  ).toHaveCount(0);
  await page.keyboard.press("Escape");
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(pendingButton(page, 1)).toBeVisible();
  await section(page, "Tratamiento y alcance de la EIPD");
  await expect(
    main(page).getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] Pendiente EIPD 9A");
  expect(errors).toEqual([]);
});

test("9A error y reintento de consulta conservan pendiente y no anuncian guardado", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Mantener 9A");
  mode = "app-offline";
  await main(page)
    .getByRole("button", { name: "Consultar última determinación guardada", exact: true })
    .click();
  await expect(main(page).getByRole("alert")).toBeVisible();
  await expect(pendingButton(page, 1)).toBeVisible();
  await pendingButton(page, 1).click();
  await expect(pendingDialog(page)).toContainText("Error; revisa el formulario");
  await page.keyboard.press("Escape");
  mode = "ok";
  await main(page)
    .getByRole("button", { name: "Consultar última determinación guardada", exact: true })
    .click();
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Mantener 9A"
  );
  await expect(pendingButton(page, 1)).toBeVisible();
  await pendingButton(page, 1).click();
  await expect(pendingDialog(page)).toContainText("Cambios sin guardar");
  await expect(pendingDialog(page).getByText("Guardado confirmado", { exact: true })).toHaveCount(
    0
  );
  expect(calls.filter((v) => v.method === "POST")).toHaveLength(1);
  expect(errors).toEqual([]);
});

test("9A dos evaluaciones mantienen dos borradores EIPD con identidad separada", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  await main(page)
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] Primera evaluación");
  await choose(page, aid2);
  await section(page, "Determinar aplicabilidad");
  const active = page.locator("[data-work-pane]:visible");
  await active
    .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
    .selectOption("corresponde");
  await active
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Segunda determinación");
  await active.getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.").check();
  await active.getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(
    active.getByText("Determinación guardada en el servidor.", { exact: true })
  ).toBeVisible();
  await section(page, "Tratamiento y alcance de la EIPD");
  await active
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] Segunda evaluación");
  await pendingButton(page, 2).click();
  await expect(pendingDialog(page).locator("li")).toHaveCount(2);
  await expect(pendingDialog(page)).toContainText("Evaluación: versión 1");
  await expect(pendingDialog(page)).toContainText("Evaluación: versión 2");
  expect(errors).toEqual([]);
});

for (const width of [320, 1280]) {
  test(`9A pendientes legibles, cierre y foco a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 844 });
    await legal(page);
    await enable(page);
    await main(page)
      .getByLabel("Fundamento sobre EIPD", { exact: true })
      .fill("[FICTICIA] Pendiente visible");
    const writes = calls.filter((v) => v.method !== "GET").length;
    await pendingButton(page, 1).click();
    await expect(
      pendingDialog(page).getByRole("button", { name: "Cerrar pendientes" })
    ).toBeFocused();
    expect(await pendingDialog(page).evaluate((el) => el.scrollWidth <= el.clientWidth + 1)).toBe(
      true
    );
    await capture(page, `9a-pendientes-${width}.png`);
    await page.keyboard.press("Escape");
    await expect(pendingButton(page, 1)).toBeFocused();
    await pendingButton(page, 1).click();
    const panel = await pendingDialog(page).boundingBox();
    await page.mouse.click(panel!.x + panel!.width + 5, panel!.y + 30);
    await expect(pendingDialog(page)).not.toBeVisible();
    await expect(pendingButton(page, 1)).toBeFocused();
    expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
    expect(errors).toEqual([]);
  });
}

test("9A valoración y anexo son unidades separadas del borrador EIPD", async ({ page }) => {
  await legal(page);
  await enable(page);
  await section(page, "Valorar riesgos");
  await main(page)
    .getByLabel("Horizonte temporal de la valoración", { exact: true })
    .fill("[FICTICIA] 24 meses");
  await expect(pendingButton(page, 1)).toBeVisible();
  await section(page, "Anexos de respaldo");
  await main(page)
    .getByLabel("Descripción del anexo", { exact: true })
    .fill("[FICTICIA] Anexo pendiente");
  await expect(pendingButton(page, 2)).toBeVisible();
  await section(page, "Tratamiento y alcance de la EIPD");
  await main(page)
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] EIPD sin guardar");
  await expect(pendingButton(page, 3)).toBeVisible();
  await pendingButton(page, 3).click();
  await expect(
    pendingDialog(page).getByRole("heading", { name: "Valoración de riesgos", exact: true })
  ).toBeVisible();
  await expect(
    pendingDialog(page).getByRole("heading", {
      name: "Anexo de respaldo en preparación",
      exact: true,
    })
  ).toBeVisible();
  await expect(
    pendingDialog(page).getByRole("heading", { name: "Borrador EIPD · siete pasos", exact: true })
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test("9A preparación temporal e infancia se cuentan separadas sin registrar versiones", async ({
  page,
}) => {
  mode = "9a-child";
  await legal(page);
  await main(page)
    .getByLabel("¿Corresponde documentar infancia y adolescencia?", { exact: true })
    .selectOption("corresponde");
  await main(page)
    .getByLabel("Fundamento sobre infancia y adolescencia", { exact: true })
    .fill("[FICTICIA] Alcance mixto de prueba");
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(pendingButton(page, 0)).toBeVisible();
  await section(page, "Preparar nueva versión documental de infancia");
  await main(page)
    .getByLabel("Declaro que este registro usa datos ficticios", { exact: true })
    .check();
  await main(page)
    .getByLabel("Nombre de la edición (texto libre)", { exact: true })
    .filter({ visible: true })
    .fill("[FICTICIA] Preparación 9A");
  await section(page, "Completar infancia y adolescencia");
  await main(page)
    .getByLabel("Análisis de edad y alcance", { exact: true })
    .fill("[FICTICIA] Edad por revisar");
  await expect(pendingButton(page, 2)).toBeVisible();
  await pendingButton(page, 2).click();
  await expect(pendingDialog(page)).toContainText(
    "Preparación temporal: se registra mediante una nueva versión documental."
  );
  await expect(
    pendingDialog(page).getByRole("heading", {
      name: "Antecedentes de infancia y adolescencia",
      exact: true,
    })
  ).toBeVisible();
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(1);
  expect(errors).toEqual([]);
});

test("9A RAT y autodiagnóstico mantienen unidades y ámbito al cambiar de módulo", async ({
  page,
}) => {
  await choose(page);
  await mod(page, "Inventario de tratamientos");
  await section(page, "Información general");
  await main(page)
    .getByRole("textbox", { name: "Nombre de la actividad *", exact: true })
    .fill("[FICTICIA] RAT pendiente");
  await expect(pendingButton(page, 1)).toBeVisible();
  await mod(page, "Autodiagnóstico");
  await main(page)
    .getByPlaceholder("Notas u observaciones (opcional)")
    .first()
    .fill("[FICTICIA] Diagnóstico pendiente");
  await expect(pendingButton(page, 2)).toBeVisible();
  await mod(page, "Panel principal");
  await pendingButton(page, 2).click();
  const rat = pendingDialog(page)
    .locator("li")
    .filter({ has: page.getByRole("heading", { name: "RAT · Información general", exact: true }) });
  const diagnostic = pendingDialog(page)
    .locator("li")
    .filter({
      has: page.getByRole("heading", { name: "Cuestionario de autodiagnóstico", exact: true }),
    });
  await expect(rat).toContainText("Tratamiento:");
  await expect(diagnostic).toContainText("Organización:");
  await expect(diagnostic).not.toContainText("Tratamiento:");
  await expect(diagnostic).not.toContainText("Evaluación:");
  expect(calls.filter((v) => v.method !== "GET")).toEqual([]);
  expect(errors).toEqual([]);
});

const pendingTrigger = (page: Page) => page.getByRole("button", { name: /^Ver pendientes \(/ });
async function pendingLink(page: Page, label: string) {
  await pendingTrigger(page).click();
  await pendingDialog(page)
    .getByRole("button", { name: `Ir a ${label}`, exact: true })
    .click();
}

test("9B Panel vuelve al formulario EIPD y a determinación con sus notas intactas", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  await main(page)
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] EIPD destino 9B");
  await section(page, "Determinar aplicabilidad");
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Determinación destino 9B");
  const writes = calls.filter((v) => v.method !== "GET").length;
  await mod(page, "Panel principal");
  await pendingLink(page, "Borrador EIPD · siete pasos");
  await expect(pendingDialog(page)).not.toBeVisible();
  await expect(
    main(page).getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] EIPD destino 9B");
  await expect(main(page)).toBeFocused();
  await pendingLink(page, "Determinación de aplicabilidad");
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Determinación destino 9B"
  );
  await expect(pendingButton(page, 2)).toBeVisible();
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
  expect(errors).toEqual([]);
});

async function twoEipdDrafts(page: Page) {
  await legal(page);
  await enable(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  await main(page)
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] Evaluación uno 9B");
  await choose(page, aid2);
  await section(page, "Determinar aplicabilidad");
  const active = page.locator("[data-work-pane]:visible");
  await active
    .getByLabel("¿Corresponde documentar EIPD?", { exact: true })
    .selectOption("corresponde");
  await active
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Segunda determinación");
  await active.getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.").check();
  await active.getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await expect(
    active.getByText("Determinación guardada en el servidor.", { exact: true })
  ).toBeVisible();
  await section(page, "Tratamiento y alcance de la EIPD");
  await active
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] Evaluación dos 9B");
}

test("9B pendiente de otra evaluación anticipa destino, cancela y confirma sin mezclar notas", async ({
  page,
}) => {
  await twoEipdDrafts(page);
  const before = page.url(),
    writes = calls.filter((v) => v.method !== "GET").length;
  await pendingButton(page, 2).click();
  const first = pendingDialog(page).locator("li").filter({ hasText: "Evaluación: versión 1" });
  await first
    .getByRole("button", { name: "Ir a Borrador EIPD · siete pasos", exact: true })
    .click();
  const confirmation = pendingDialog(page).getByRole("region", {
    name: "Confirmar destino pendiente",
  });
  await expect(confirmation).toContainText("Antes de cambiar de contexto");
  await expect(confirmation).toContainText("Destino: Tratamiento y alcance de la EIPD");
  await expect(confirmation).toContainText("versión 1");
  await expect(confirmation).toContainText("versión 2");
  await confirmation.getByRole("button", { name: "Cancelar cambio", exact: true }).click();
  expect(page.url()).toBe(before);
  await expect(
    first.getByRole("button", { name: "Ir a Borrador EIPD · siete pasos", exact: true })
  ).toBeFocused();
  await first
    .getByRole("button", { name: "Ir a Borrador EIPD · siete pasos", exact: true })
    .click();
  await capture(page, "9b-confirmar-pendiente.png");
  await confirmation
    .getByRole("button", { name: "Abrir pendiente en este contexto", exact: true })
    .click();
  await expect(page).toHaveURL(new RegExp(`assessmentId=${aid}(?:&|$)`));
  await expect(
    page
      .locator("[data-work-pane]:visible")
      .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] Evaluación uno 9B");
  await expect(pendingButton(page, 2)).toBeVisible();
  await pendingButton(page, 2).click();
  await pendingDialog(page)
    .locator("li")
    .filter({ hasText: "Evaluación: versión 2" })
    .getByRole("button", { name: "Ir a Borrador EIPD · siete pasos", exact: true })
    .click();
  await confirmation
    .getByRole("button", { name: "Abrir pendiente en este contexto", exact: true })
    .click();
  await expect(
    page
      .locator("[data-work-pane]:visible")
      .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] Evaluación dos 9B");
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
  expect(errors).toEqual([]);
});

test("9B Cambiar contexto explica destino antes de Aplicar y cancelar preserva pantalla y texto", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  await main(page)
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] Cancelar contexto 9B");
  const before = page.url(),
    writes = calls.filter((v) => v.method !== "GET").length;
  await page.getByRole("button", { name: "Cambiar contexto", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Contexto de trabajo", exact: true });
  await dialog.getByLabel("Evaluación", { exact: true }).selectOption(aid2);
  const preview = dialog.getByRole("region", { name: "Antes de aplicar contexto" });
  await expect(preview).toContainText("Destino al aplicar: Determinar aplicabilidad");
  await expect(preview).toContainText("versión 2");
  await expect(preview).toContainText("Aplicar no los guarda ni copia sus datos");
  await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
  expect(page.url()).toBe(before);
  await expect(
    main(page).getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] Cancelar contexto 9B");
  await choose(page, aid2);
  await expect(page).toHaveURL(new RegExp(`aplicabilidad.*assessmentId=${aid2}`));
  await expect(pendingButton(page, 1)).toBeVisible();
  await pendingLink(page, "Borrador EIPD · siete pasos");
  await pendingDialog(page)
    .getByRole("button", { name: "Abrir pendiente en este contexto", exact: true })
    .click();
  await expect(
    page
      .locator("[data-work-pane]:visible")
      .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] Cancelar contexto 9B");
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(writes);
  expect(errors).toEqual([]);
});

test("9B consulta fresca reubica EIPD bloqueada y recupera el pendiente al habilitarse", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  await main(page)
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] Conservar al bloquear 9B");
  await mod(page, "Panel principal");
  determinations[aid] = {
    ...determinations[aid],
    revision: 2,
    eipd: { state: "no_corresponde", reason: "[FICTICIA] Cambio externo" },
  };
  await pendingLink(page, "Borrador EIPD · siete pasos");
  await expect(main(page).getByRole("region", { name: "Cambio de sección" })).toContainText(
    "No corresponde"
  );
  await expect(
    main(page).getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).not.toBeVisible();
  await expect(pendingButton(page, 1)).toBeVisible();
  determinations[aid] = {
    ...determinations[aid],
    revision: 3,
    eipd: { state: "corresponde", reason: "[FICTICIA] Rehabilitada" },
  };
  await pendingLink(page, "Borrador EIPD · siete pasos");
  await expect(
    main(page).getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] Conservar al bloquear 9B");
  await expect(
    main(page).getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).toBeVisible();
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(1);
  expect(errors).toEqual([]);
});

test("9B error y cancelación de validación lenta no cambian destino ni eliminan el borrador", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await main(page)
    .getByLabel("Fundamento sobre EIPD", { exact: true })
    .fill("[FICTICIA] Validación pendiente 9B");
  await mod(page, "Panel principal");
  const before = page.url();
  mode = "deny";
  await pendingLink(page, "Determinación de aplicabilidad");
  await expect(pendingDialog(page).getByRole("alert")).toContainText("Los borradores se conservan");
  expect(page.url()).toBe(before);
  mode = "hold";
  await pendingDialog(page)
    .getByRole("button", { name: "Ir a Determinación de aplicabilidad", exact: true })
    .click();
  await expect.poll(() => !!releaseValidation).toBe(true);
  await pendingDialog(page).getByRole("button", { name: "Cerrar pendientes", exact: true }).click();
  mode = "ok";
  releaseValidation?.();
  await expect(pendingDialog(page)).not.toBeVisible();
  expect(page.url()).toBe(before);
  await pendingLink(page, "Determinación de aplicabilidad");
  await expect(main(page).getByLabel("Fundamento sobre EIPD", { exact: true })).toHaveValue(
    "[FICTICIA] Validación pendiente 9B"
  );
  expect(errors).toEqual([]);
});

test("9B autodiagnóstico pendiente desde resultados vuelve al cuestionario", async ({ page }) => {
  await choose(page);
  await mod(page, "Autodiagnóstico");
  await main(page)
    .getByPlaceholder("Notas u observaciones (opcional)")
    .first()
    .fill("[FICTICIA] Cuestionario 9B");
  await section(page, "Resultado del autodiagnóstico");
  await mod(page, "Panel principal");
  await pendingLink(page, "Cuestionario de autodiagnóstico");
  await expect(main(page).getByPlaceholder("Notas u observaciones (opcional)").first()).toHaveValue(
    "[FICTICIA] Cuestionario 9B"
  );
  expect(calls.filter((v) => v.method !== "GET")).toEqual([]);
  expect(errors).toEqual([]);
});

test("9B recupera la creación de evaluación en su panel original sin crear otra", async ({
  page,
}) => {
  await legal(page);
  await section(page, "Evaluaciones y creación de borrador");
  await page
    .locator("[data-work-pane]:visible")
    .getByLabel("Tratamiento del RAT", { exact: true })
    .selectOption(tid);
  await page
    .locator('[data-work-pane]:visible textarea[aria-label="Fundamento"]:visible')
    .fill("[FICTICIA] Creación temporal 9B");
  await choose(page, aid2);
  await pendingLink(page, "Creación de evaluación (sin registrar)");
  await pendingDialog(page)
    .getByRole("button", { name: "Abrir pendiente en este contexto", exact: true })
    .click();
  await expect(
    page.locator('[data-work-pane]:visible textarea[aria-label="Fundamento"]:visible')
  ).toHaveValue("[FICTICIA] Creación temporal 9B");
  await expect(page).toHaveURL(new RegExp(`catalogo.*assessmentId=${aid}`));
  expect(calls.filter((v) => v.method !== "GET")).toEqual([]);
  expect(errors).toEqual([]);
});

for (const width of [320, 1280]) {
  test(`9B cabecera estable al alternar aviso y abrir pendiente con teclado a ${width}px`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 844 });
    await legal(page);
    await enable(page);
    const header = page.locator("header.prototype-top");
    const height = await header.evaluate((el) => el.getBoundingClientRect().height);
    const reason = main(page).getByLabel("Fundamento sobre EIPD", { exact: true });
    const original = await reason.inputValue();
    await reason.fill("[FICTICIA] Cabecera 9B");
    expect(await header.evaluate((el) => el.getBoundingClientRect().height)).toBe(height);
    await pendingTrigger(page).focus();
    await page.keyboard.press("Enter");
    await pendingDialog(page)
      .getByRole("button", { name: "Ir a Determinación de aplicabilidad", exact: true })
      .focus();
    await page.keyboard.press("Enter");
    await expect(pendingDialog(page)).not.toBeVisible();
    await expect(main(page)).toBeFocused();
    await reason.fill(original);
    await expect(pendingButton(page, 0)).toBeVisible();
    expect(await header.evaluate((el) => el.getBoundingClientRect().height)).toBe(height);
    expect(errors).toEqual([]);
  });
}

test("9B preparación temporal bloqueada se conserva y se recupera al habilitar infancia", async ({
  page,
}) => {
  mode = "9a-child";
  await legal(page);
  await main(page)
    .getByLabel("¿Corresponde documentar infancia y adolescencia?", { exact: true })
    .selectOption("corresponde");
  await main(page)
    .getByLabel("Fundamento sobre infancia y adolescencia", { exact: true })
    .fill("[FICTICIA] Infancia 9B");
  await main(page)
    .getByLabel("Declaro que esta prueba utiliza únicamente datos ficticios.")
    .check();
  await main(page).getByRole("button", { name: "Guardar determinación", exact: true }).click();
  await section(page, "Preparar nueva versión documental de infancia");
  await main(page)
    .getByLabel("Declaro que este registro usa datos ficticios", { exact: true })
    .check();
  await main(page)
    .getByLabel("Nombre de la edición (texto libre)", { exact: true })
    .filter({ visible: true })
    .fill("[FICTICIA] Temporal 9B");
  await mod(page, "Panel principal");
  const enabled = structuredClone(determinations[aid]);
  determinations[aid] = {
    ...enabled,
    revision: 2,
    infancia: { state: "no_corresponde", reason: "[FICTICIA] Cambio externo" },
  };
  await pendingLink(page, "Preparación de nueva versión de infancia");
  await expect(main(page).getByRole("region", { name: "Cambio de sección" })).toContainText(
    "No corresponde"
  );
  await expect(pendingButton(page, 1)).toBeVisible();
  determinations[aid] = { ...enabled, revision: 3 };
  await pendingLink(page, "Preparación de nueva versión de infancia");
  await expect(
    main(page)
      .getByLabel("Nombre de la edición (texto libre)", { exact: true })
      .filter({ visible: true })
  ).toHaveValue("[FICTICIA] Temporal 9B");
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(1);
  expect(errors).toEqual([]);
});

test("10A EIPD general explica guardado sin ofrecer actuaciones formales de infancia", async ({
  page,
}) => {
  await legal(page);
  await enable(page);
  await section(page, "Tratamiento y alcance de la EIPD");
  const panel = main(page).getByRole("complementary", {
    name: "Acciones y requisitos: Borrador EIPD general · evaluación versión 1",
    exact: true,
  });
  await expect(panel).toContainText("Editar y guardar borrador: Disponible.");
  await expect(panel).toContainText("Registrar revisión o decisión documental: No disponible.");
  await expect(panel).toContainText("Confirmar o activar EIPD: No disponible.");
  await expect(
    main(page).getByRole("button", { name: "Registrar revisión ficticia", exact: true })
  ).toHaveCount(0);
  const before = calls.filter((v) => v.method !== "GET").length;
  await main(page)
    .getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
    .fill("[FICTICIA] Capacidad 10A");
  await section(page, "Documentos guardados");
  await section(page, "Tratamiento y alcance de la EIPD");
  await expect(
    main(page).getByLabel("Notas del borrador EIPD (opcional)", { exact: true })
  ).toHaveValue("[FICTICIA] Capacidad 10A");
  expect(calls.filter((v) => v.method !== "GET")).toHaveLength(before);
  expect(errors).toEqual([]);
});

for (const width of [320, 1280]) {
  test(`10A acciones de EIPD legibles sin desbordamiento a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 844 });
    await legal(page);
    await enable(page);
    await section(page, "Tratamiento y alcance de la EIPD");
    const panel = main(page).getByRole("complementary", {
      name: "Acciones y requisitos: Borrador EIPD general · evaluación versión 1",
      exact: true,
    });
    await panel.scrollIntoViewIfNeeded();
    await expect(panel).toBeVisible();
    const box = await panel.boundingBox();
    expect(box!.x).toBeGreaterThanOrEqual(0);
    expect(box!.x + box!.width).toBeLessThanOrEqual(width);
    expect(await panel.evaluate((el) => el.scrollWidth <= el.clientWidth + 1)).toBe(true);
    await capture(page, `10a-capacidades-${width}.png`);
    const stickyHeight = await page
      .locator("header.prototype-top")
      .evaluate((el) => el.getBoundingClientRect().height);
    await panel.evaluate(
      (el, height) => window.scrollBy(0, el.getBoundingClientRect().top - height - 8),
      stickyHeight
    );
    await capture(page, `10a-capacidades-inicio-${width}.png`);
    expect(errors).toEqual([]);
  });
}
