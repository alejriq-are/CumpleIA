import { test, expect, type Page } from "@playwright/test";
import path from "node:path";
import { browserBundle } from "./helpers/browser-bundle";
let script: string;
test.beforeAll(async () => {
  script = await browserBundle(`
 import React from "react";import {createRoot} from "react-dom/client";
 import {OrganizationAcceptancePanel} from ${JSON.stringify(path.resolve("components/licitud/OrganizationAcceptancePanel.tsx"))};
 import {organizationAcceptanceApi as api} from ${JSON.stringify(path.resolve("lib/api/organization-acceptance.ts"))};
 const id="a0000000-0000-0000-0000-000000000001",scope={organizationId:id,treatmentId:id,assessmentId:id,token:"PRUEBA"};
 const resolution={id:"b0000000-0000-0000-0000-000000000001",organization_id:id,treatment_id:id,assessment_id:id,document_hash:"a".repeat(64),context_hash:"b".repeat(64),child_material_hash:"c".repeat(64)};
 const identity={organization_id:id,treatment_id:id,assessment_id:id,actor_id:id,created_by:id,created_at:"2026-10-16T10:00:00Z",data_kind:"ficticios",authorizes_action:false,can_confirm:false};
 const demo=window.demo={mode:"ok",calls:[],authorities:[],events:[],may_designate:true,release:null};
 window.fetch=async(url,options)=>{
 demo.calls.push({url,options});
 if(options.method!=="POST" && demo.mode==="load-wait")await new Promise(resolve=>demo.release=resolve);
 if(options.method!=="POST" && demo.mode==="load-error")return new Response(JSON.stringify({detail:"PRUEBA"}),{status:503});
 if(options.method==="POST"){
  if(demo.mode==="wait")await new Promise(resolve=>demo.release=resolve);
  if(demo.mode==="unknown")throw new Error("PRUEBA: respuesta incierta");
  if(demo.mode==="denied"||demo.mode==="conflict")return new Response(JSON.stringify({detail:"PRUEBA"}),{status:demo.mode==="denied"?403:409});
  const p=JSON.parse(options.body);
  if(url.endsWith("/authority")){const saved={...identity,...p,id:"c0000000-0000-0000-0000-"+String(demo.authorities.length+1).padStart(12,"0"),revision:p.expected_revision+1};delete saved.expected_revision;demo.authorities.push(saved);return new Response(JSON.stringify(saved),{status:201});}
  const saved={...identity,...p,id:"d0000000-0000-0000-0000-"+String(demo.events.length+1).padStart(12,"0"),resolution_id:resolution.id,document_hash:resolution.document_hash,context_hash:resolution.context_hash,child_material_hash:resolution.child_material_hash,material_status:"coincide",faculty_current:true};
  if(demo.mode==="tamper")saved.authorizes_action=true;
  demo.events.push(saved);return new Response(JSON.stringify(saved),{status:201});
 }
 if(url.endsWith("/authority"))return new Response(JSON.stringify({actor_id:id,may_designate:demo.may_designate,authorities:demo.authorities,authorizes_action:false,can_confirm:demo.mode==="invalid-load"}),{status:200});
 return new Response(JSON.stringify(demo.events),{status:200});
 };
 const load=()=>api.load(scope,resolution),designate=(actor,p)=>api.designate(scope,actor,p),record=(actor,p)=>api.record(scope,resolution,actor,p);
 const root=createRoot(document.getElementById("root"));
 window.mount=(options={})=>root.render(React.createElement(OrganizationAcceptancePanel,{load,designate,record,readOnly:options.readOnly??false,guided:options.guided??false,documentIdentity:options.documentIdentity}));
 window.acceptanceApi={api,scope,resolution,id};
 `);
});
test.beforeEach(async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 749 });
  await page.setContent('<div id="root"></div>');
  await page.addScriptTag({ content: script });
});
async function mount(page: Page, options = {}) {
  await page.evaluate((options) => (window as any).mount(options), options);
  await expect(page.getByText("Persona de esta sesión de prueba:", { exact: false })).toBeVisible();
}
async function enable(page: Page) {
  await page.getByRole("checkbox", { name: "Declaro datos ficticios para la aceptación" }).check();
}
async function fillGrant(page: Page) {
  await page.getByLabel("Referencia de la facultad", { exact: true }).fill("PRUEBA: facultad");
  await page.getByLabel("Evidencia de la facultad", { exact: true }).fill("PRUEBA: evidencia");
}
async function grant(page: Page) {
  await fillGrant(page);
  await page.getByRole("button", { name: "Registrar facultad ficticia", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Facultad de prueba registrada");
}
async function fillDecision(page: Page) {
  await page.getByLabel("Fundamento de la decisión", { exact: true }).fill("PRUEBA: fundamento");
  await page.getByLabel("Referencia del acta ficticia", { exact: true }).fill("PRUEBA: acta");
}
async function posts(page: Page) {
  return page.evaluate(() =>
    (window as any).demo.calls.filter((c: any) => c.options.method === "POST")
  );
}
test("owner necesita facultad, registra tres decisiones y revoca", async ({ page }) => {
  await mount(page);
  await enable(page);
  await expect(
    page.getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
  ).toBeDisabled();
  await grant(page);
  for (const d of ["acepta", "rechaza", "requiere_cambios"]) {
    await fillDecision(page);
    await page.getByLabel("Decisión de la organización", { exact: true }).selectOption(d);
    await page
      .getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
      .click();
    await expect(page.getByLabel("Fundamento de la decisión", { exact: true })).toHaveValue("");
  }
  const calls = await posts(page);
  expect(calls).toHaveLength(4);
  for (const c of calls.slice(1)) {
    const body = JSON.parse(c.options.body);
    expect(Object.keys(body).sort()).toEqual([
      "authority_id",
      "data_kind",
      "decision",
      "evidence_reference",
      "rationale",
    ]);
    expect(body.data_kind).toBe("ficticios");
  }
  await page.getByLabel("Acción sobre la facultad", { exact: true }).selectOption("revocar");
  await grant(page);
  await expect(
    page.getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
  ).toBeDisabled();
  expect(JSON.parse((await posts(page))[4].options.body).expected_revision).toBe(1);
  await expect(page.getByText(/no confirma ni activa EIPD/).first()).toBeVisible();
});
test("solo lectura bloquea todos los registros", async ({ page }) => {
  await mount(page, { readOnly: true });
  await expect(page.getByRole("checkbox")).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "Registrar facultad ficticia", exact: true })
  ).toBeDisabled();
  expect(await posts(page)).toHaveLength(0);
});
test("sin permiso de administración no puede designar", async ({ page }) => {
  await page.evaluate(() => ((window as any).demo.may_designate = false));
  await mount(page);
  await enable(page);
  await expect(
    page.getByRole("button", { name: "Registrar facultad ficticia", exact: true })
  ).toBeDisabled();
});
for (const mode of ["denied", "conflict"])
  test(`rechazo ${mode} conserva evidencia sin repetir`, async ({ page }) => {
    await mount(page);
    await enable(page);
    await fillGrant(page);
    await page.evaluate((mode) => ((window as any).demo.mode = mode), mode);
    await page.getByRole("button", { name: "Registrar facultad ficticia", exact: true }).click();
    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByLabel("Referencia de la facultad", { exact: true })).toHaveValue(
      "PRUEBA: facultad"
    );
    expect(await posts(page)).toHaveLength(1);
  });
for (const mode of ["unknown", "tamper"])
  test(`respuesta incierta ${mode} bloquea decisión`, async ({ page }) => {
    await mount(page);
    await enable(page);
    await grant(page);
    await fillDecision(page);
    await page.evaluate((mode) => ((window as any).demo.mode = mode), mode);
    await page
      .getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
      .click();
    await expect(page.getByRole("alert")).toContainText("Resultado incierto");
    await expect(
      page.getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
    ).toBeDisabled();
    await expect(page.getByLabel("Fundamento de la decisión", { exact: true })).toHaveValue(
      "PRUEBA: fundamento"
    );
    expect(await posts(page)).toHaveLength(2);
  });
test("encargado identifica al responsable mandante", async ({ page }) => {
  await mount(page);
  await enable(page);
  await page.getByLabel("Rol de la organización", { exact: true }).selectOption("encargado");
  await fillGrant(page);
  await page.getByRole("button", { name: "Registrar facultad ficticia", exact: true }).click();
  expect(await posts(page)).toHaveLength(0);
  await page
    .getByLabel("Responsable por cuya cuenta actúa", { exact: true })
    .fill("PRUEBA: mandante");
  await page.getByRole("button", { name: "Registrar facultad ficticia", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("registrada");
  expect(JSON.parse((await posts(page))[0].options.body).responsible_party_reference).toBe(
    "PRUEBA: mandante"
  );
});
test("doble envío no duplica facultad", async ({ page }) => {
  await mount(page);
  await enable(page);
  await fillGrant(page);
  await page.evaluate(() => ((window as any).demo.mode = "wait"));
  await page.getByRole("button", { name: "Registrar facultad ficticia", exact: true }).dblclick();
  await expect.poll(async () => (await posts(page)).length).toBe(1);
  await page.evaluate(() => (window as any).demo.release());
  await expect(page.getByRole("status")).toContainText("registrada");
});
test("carga incompatible no expone formulario", async ({ page }) => {
  await page.evaluate(() => {
    (window as any).demo.mode = "invalid-load";
    (window as any).mount();
  });
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("checkbox")).toHaveCount(0);
});
test("cliente rechaza identidad inyectada y continuar", async ({ page }) => {
  const result = await page.evaluate(async () => {
    const { api, scope, resolution, id } = (window as any).acceptanceApi;
    const check = async (p: any) => {
      try {
        await api.record(scope, resolution, id, p);
        return null;
      } catch (e) {
        return (e as any).status;
      }
    };
    const p = {
      authority_id: id,
      decision: "acepta",
      rationale: "PRUEBA",
      evidence_reference: "PRUEBA",
    };
    return [await check({ ...p, decision: "continuar" }), await check({ ...p, created_by: id })];
  });
  expect(result).toEqual([400, 400]);
  expect(await posts(page)).toHaveLength(0);
});

test("vista guiada separa facultades y exige seleccionar una decision", async ({ page }) => {
  await mount(page, { guided: true });
  await enable(page);
  await expect(page.getByLabel("Referencia de la facultad", { exact: true })).toBeHidden();
  await expect(page.getByLabel("Decisión de la organización", { exact: true })).toHaveValue("");
  await page
    .getByRole("button", { name: "Gestionar facultades de la organización", exact: true })
    .click();
  await grant(page);
  await fillDecision(page);
  await page
    .getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
    .click();
  expect(await posts(page)).toHaveLength(1);
  await page
    .getByLabel("Decisión de la organización", { exact: true })
    .selectOption("requiere_cambios");
  await expect(
    page.getByText("Requiere cambios: la organización solicita ajustes", { exact: false })
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
    .click();
  await expect(
    page.getByText("Decisión documental de prueba registrada.", { exact: false })
  ).toBeVisible();
  expect(await posts(page)).toHaveLength(2);
});

const capabilities = (page: Page) =>
  page.getByRole("complementary", {
    name: "Acciones y requisitos: Decisión sobre la versión de infancia consultada",
    exact: true,
  });
test("10A facultad ausente, otorgada y revocada explican la decisión sin perder historia", async ({
  page,
}) => {
  await mount(page);
  await expect(capabilities(page)).toContainText("No hay una facultad otorgada");
  await enable(page);
  await grant(page);
  await fillDecision(page);
  await expect(capabilities(page)).toContainText(
    "Registrar decisión de la organización: Disponible."
  );
  await page
    .getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Decisión documental de prueba registrada");
  await expect(capabilities(page)).toContainText("no habilita confirmación ni activación");
  await page.getByLabel("Acción sobre la facultad", { exact: true }).selectOption("revocar");
  await grant(page);
  await expect(capabilities(page)).toContainText("La facultad de esta persona está revocada");
  await expect(
    page.getByText("Decisión de la organización: Acepta el documento", { exact: true })
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
  ).toBeDisabled();
  expect(await posts(page)).toHaveLength(3);
});
for (const state of ["obsoleto", "no_disponible"]) {
  test(`10A material ${state} conserva la decisión histórica sin atribuir vigencia`, async ({
    page,
  }) => {
    await mount(page);
    await enable(page);
    await grant(page);
    await fillDecision(page);
    await page
      .getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
      .click();
    await expect(page.getByRole("status")).toContainText(
      "Decisión documental de prueba registrada"
    );
    await page.evaluate((state) => {
      (window as any).demo.events[0].material_status = state;
    }, state);
    await page
      .getByRole("button", { name: "Actualizar aceptación de organización", exact: true })
      .click();
    await expect(
      page.getByText("Esta decisión histórica se conserva", { exact: false })
    ).toContainText("ni declara inválidas las demás versiones");
    expect(await posts(page)).toHaveLength(2);
  });
}
test("10A consulta fallida no afirma una facultad disponible", async ({ page }) => {
  await page.evaluate(() => {
    (window as any).demo.mode = "load-error";
    (window as any).mount();
  });
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(capabilities(page)).toContainText(
    "Registrar decisión de la organización: Por comprobar."
  );
  await expect(capabilities(page)).toContainText("No se pudo consultar la facultad");
  await expect(
    page.getByRole("button", { name: "Registrar decisión documental ficticia", exact: true })
  ).toHaveCount(0);
  expect(await posts(page)).toHaveLength(0);
});
test("10A consulta en curso no deduce permiso de administración", async ({ page }) => {
  await page.evaluate(() => {
    (window as any).demo.mode = "load-wait";
    (window as any).mount();
  });
  await expect(capabilities(page)).toContainText("Registrar facultad: Por comprobar.");
  await expect(capabilities(page)).not.toContainText("Registrar facultad: Disponible.");
  expect(await posts(page)).toHaveLength(0);
});

test("10B permite localizar decisiones y volver sin registros", async ({ page }) => {
  await mount(page, {
    guided: true,
    documentIdentity: "Versión documental de infancia 2 · PRUEBA-002",
  });
  const historyButton = page.getByRole("button", {
    name: "Ver decisiones registradas de esta versión",
    exact: true,
  });
  await historyButton.focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("heading", { name: "Historial documental de esta versión", exact: true })
  ).toBeFocused();
  await expect(page.getByText("No hay decisiones de organización registradas.")).toBeVisible();
  await page
    .getByRole("button", { name: "Volver a Decisión de la organización", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Aceptación documental por organización", exact: true })
  ).toBeFocused();
  await expect(
    page.getByText("Documento de estas decisiones: Versión documental de infancia 2 · PRUEBA-002", {
      exact: true,
    })
  ).toBeVisible();
  expect(await posts(page)).toHaveLength(0);
});
