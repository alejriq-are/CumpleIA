"use client";
import { useCallback, useEffect, useRef, useState, type MouseEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { SignOutButton } from "@/components/auth/SignOutButton";
import { api, type OrganizationMembershipOut } from "@/lib/api/client";
import { licitudApi } from "@/lib/api/licitud";
import type { Applicability } from "@/lib/api/navigation";
import { AutodiagnosticoWorkspace } from "@/components/autodiagnostico/AutodiagnosticoWorkspace";
import { RatWorkspace } from "@/components/rat/RatWorkspace";
import { TreatmentGeneralForm } from "@/components/rat/TreatmentGeneralForm";
import { LicitudWorkspace, sessionToken } from "@/components/licitud/LicitudWorkspace";
import { OrganizacionForm } from "@/components/organizacion/OrganizacionForm";
import { MainModules } from "./PrototypeMenus";
import { PrototypeDrawer } from "./PrototypeDrawer";
import { ConnectedContextSummary, type SelectedEvaluation } from "./ConnectedContextSummary";
import { ConnectedAssessment } from "./ConnectedAssessment";
import { ConnectedContext, type WorkContext } from "./ConnectedContext";
import {
  encodeWork,
  navigationReadError,
  parseWork,
  paneKey,
  ratSections,
  eipdSections,
  type WorkLocation,
} from "./connected-navigation";
import { modules, type ModuleId } from "./prototype-data";
import { availabilityReason, type AvailabilityReadState } from "./connected-availability";
import { connectedDestinations, connectedDestinationLabel } from "./connected-destinations";
import "./navigation-prototype.css";
import "./connected-navigation.css";

// Closing a disclosure must not move focus away from the user's next control.
function closeDesktopGroups(except?: HTMLDetailsElement) {
  document
    .querySelectorAll<HTMLDetailsElement>(".connected-desktop-sections details[open]")
    .forEach((item) => {
      if (item !== except) item.open = false;
    });
}

type Item = { id: string; label: string; step?: number };
type Group = { label: string; items: Item[]; reason?: string | null; availabilityLabel?: string };
function contextKey(v: WorkContext) {
  return `${v.organizationId}:${v.treatmentId}:${v.assessmentId}`;
}
function ConnectedDiagnostic({
  organization,
  location,
  go,
  onSections,
  onPending,
}: {
  organization: OrganizationMembershipOut;
  location: WorkLocation;
  go: (v: WorkLocation) => void;
  onSections: (org: string, items: Item[]) => void;
  onPending: (key: string, dirty: boolean) => void;
}) {
  const sections = useCallback(
    (items: Item[]) => onSections(organization.id, items),
    [organization.id, onSections]
  );
  const pending = useCallback(
    (v: boolean) => onPending(`diagnostico:${organization.id}`, v),
    [organization.id, onPending]
  );
  return (
    <AutodiagnosticoWorkspace
      organizaciones={[organization]}
      onPending={pending}
      navigation={{
        section: location.section,
        go: (id) => go({ ...location, section: id }),
        onSections: sections,
      }}
    />
  );
}
function memoryKey(v: WorkLocation) {
  return `${v.organizationId}:${v.module}:${v.module === "licitud" ? v.assessmentId : v.module === "rat" ? v.treatmentId : ""}`;
}
export function ConnectedWorkspace({
  organizations,
}: {
  organizations: OrganizationMembershipOut[];
}) {
  const first: WorkLocation = {
    organizationId: organizations[0]?.id ?? "",
    treatmentId: "",
    assessmentId: "",
    module: "panel",
    section: "resumen",
    step: 0,
  };
  const [location, setLocation] = useState(first);
  const [panes, setPanes] = useState<Record<string, WorkLocation>>({});
  const router = useRouter();
  const [exitOpen, setExitOpen] = useState(false);
  const exitTrigger = useRef<HTMLElement | null>(null);
  const exitResolve = useRef<((v: boolean) => void) | null>(null);
  const [menu, setMenu] = useState(false);
  const [sections, setSections] = useState(false);
  const [context, setContext] = useState(false);
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [pending, setPending] = useState<Record<string, boolean>>({});
  const [availability, setAvailability] = useState<Record<string, AvailabilityReadState>>({});
  const [scope, setScope] = useState<Record<string, Applicability>>({});
  const [diagnosticSections, setDiagnosticSections] = useState<Record<string, Item[]>>({});
  const [names, setNames] = useState<Record<string, string>>({});
  const [evaluations, setEvaluations] = useState<Record<string, SelectedEvaluation>>({});
  const [last, setLast] = useState<WorkLocation | null>(null);
  const content = useRef<HTMLElement>(null);
  const current = useRef(location);
  current.current = location;
  const sequence = useRef(0);
  const validationTarget = useRef<WorkLocation | null>(null);
  const rememberedLocations = useRef<Record<string, WorkLocation>>({});

  const updatePending = useCallback(
    (key: string, value: boolean) =>
      setPending((prev) => (prev[key] === value ? prev : { ...prev, [key]: value })),
    []
  );
  const updateScope = useCallback(
    (key: string, value: Applicability) => setScope((prev) => ({ ...prev, [key]: value })),
    []
  );
  const updateAvailability = useCallback((key: string, value: AvailabilityReadState) => {
    setAvailability((prev) =>
      prev[key]?.loading === value.loading && prev[key]?.error === value.error
        ? prev
        : { ...prev, [key]: value }
    );
  }, []);
  const updateDiagnostic = useCallback(
    (orgId: string, items: Item[]) =>
      setDiagnosticSections((prev) => ({ ...prev, [orgId]: items })),
    []
  );
  const go = useCallback(
    (next: WorkLocation, replace = false) => {
      if (!organizations.some((v) => v.id === next.organizationId)) return;
      sequence.current += 1;
      setValidating(false);
      rememberedLocations.current[memoryKey(next)] = next;
      setLocation(next);
      setMenu(false);
      setSections(false);
      setError("");
      validationTarget.current = null;
      setNotice("");
      if (next.module !== "panel") setLast(next);
      setPanes((prev) => ({ ...prev, [paneKey(next)]: next }));
      window.history[
        replace || window.location.hash === encodeWork(next) ? "replaceState" : "pushState"
      ](null, "", encodeWork(next));
      closeDesktopGroups();
      requestAnimationFrame(() => {
        if (!content.current) return;
        const header = content.current.closest(".min-w-0")?.querySelector("header");
        content.current.style.scrollMarginTop = `${(header?.getBoundingClientRect().height ?? 140) + 8}px`;
        content.current.focus({ preventScroll: true });
        content.current.scrollIntoView({ block: "start" });
      });
    },
    [organizations]
  );
  const validate = useCallback(
    async (next: WorkLocation, replace = true) => {
      const version = ++sequence.current;
      validationTarget.current = next;
      setValidating(true);
      setError("");
      if (!organizations.some((v) => v.id === next.organizationId)) {
        setError("No tienes acceso a la organización solicitada.");
        setValidating(false);
        return false;
      }
      try {
        if (next.treatmentId) {
          const token = await sessionToken();
          const t = await api.rat.getTreatment(token, next.organizationId, next.treatmentId);
          if (version !== sequence.current) return;
          setNames((p) => ({ ...p, [next.treatmentId]: t.name }));
          if (next.assessmentId) {
            const a = await licitudApi.get(
              { token, organizationId: next.organizationId, treatmentId: next.treatmentId },
              next.assessmentId
            );
            if (version !== sequence.current) return;
            setEvaluations((p) => ({
              ...p,
              [next.assessmentId]: {
                purpose: a.purpose_snapshot,
                version: a.version,
                status: a.status,
              },
            }));
          }
        }
        if (version === sequence.current) {
          go(next, replace);
          return true;
        }
        return false;
      } catch (e) {
        if (version === sequence.current)
          setError(navigationReadError(e, "No se pudo abrir el contexto autorizado."));
        return false;
      } finally {
        if (version === sequence.current) setValidating(false);
      }
    },
    [go, organizations]
  );
  useEffect(() => {
    const restore = () => {
      const parsed = parseWork(window.location.hash);
      if (parsed) void validate(parsed);
      else if (window.location.hash) setError("El enlace de navegación no es válido.");
    };
    restore();
    window.addEventListener("popstate", restore);
    window.addEventListener("hashchange", restore);
    return () => {
      window.removeEventListener("popstate", restore);
      window.removeEventListener("hashchange", restore);
    };
  }, [validate]);
  useEffect(() => {
    const close = (event: PointerEvent | KeyboardEvent) => {
      const target = event.target as HTMLElement;
      document
        .querySelectorAll<HTMLDetailsElement>(".connected-desktop-sections details[open]")
        .forEach((item) => {
          if (event instanceof KeyboardEvent) {
            if (event.key !== "Escape" || !item.contains(target)) return;
            event.preventDefault();
            item.open = false;
            item.querySelector("summary")?.focus();
          } else if (!item.contains(target)) item.open = false;
        });
    };
    const mobile = window.matchMedia("(max-width: 767px)");
    const resize = () => {
      const focusedGroup = document.activeElement?.closest(".connected-desktop-sections");
      closeDesktopGroups();
      if (mobile.matches && focusedGroup)
        document.getElementById("connected-sections-trigger")?.focus();
    };
    mobile.addEventListener("change", resize);
    document.addEventListener("pointerdown", close);
    document.addEventListener("keydown", close);
    return () => {
      mobile.removeEventListener("change", resize);
      document.removeEventListener("pointerdown", close);
      document.removeEventListener("keydown", close);
    };
  }, []);
  const anyPending = Object.values(pending).some(Boolean);
  function confirmExit() {
    exitTrigger.current = document.activeElement as HTMLElement;
    if (!anyPending) return Promise.resolve(true);
    return new Promise<boolean>((resolve) => {
      exitResolve.current = resolve;
      setExitOpen(true);
    });
  }
  const cancelExit = useCallback(() => {
    setExitOpen(false);
    exitResolve.current?.(false);
    exitResolve.current = null;
    requestAnimationFrame(() => exitTrigger.current?.focus());
  }, []);
  function acceptExit() {
    setExitOpen(false);
    exitResolve.current?.(true);
    exitResolve.current = null;
  }
  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => {
      if (anyPending) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [anyPending]);
  const selected = scope[contextKey(location)];
  const readState = availability[contextKey(location)];
  const eipdReason = availabilityReason(selected, readState, "eipd");
  const infanciaReason = availabilityReason(selected, readState, "infancia");
  const diagnosticItems = diagnosticSections[location.organizationId] ?? [];
  const groups: Group[] =
    location.module === "rat"
      ? [
          {
            label: "Inventario",
            items: [
              { id: "catalogo", label: connectedDestinations.rat.catalogo },
              { id: "nuevo", label: connectedDestinations.rat.nuevo },
            ],
          },
          ...(location.treatmentId
            ? [
                {
                  label: "Actividad de tratamiento",
                  items: ratSections.map(([id, label]) => ({ id, label })),
                },
              ]
            : []),
        ]
      : location.module === "diagnostico"
        ? [
            {
              label: "Cuestionario",
              items: diagnosticItems.length
                ? diagnosticItems
                : [{ id: "cuestionario", label: connectedDestinations.diagnostico.cuestionario }],
            },
            {
              label: "Resultados e informe",
              items: [{ id: "resultados", label: connectedDestinations.diagnostico.resultados }],
            },
          ]
        : location.module === "licitud"
          ? [
              {
                label: "Preparar",
                items: [
                  { id: "catalogo", label: connectedDestinations.licitud.catalogo },
                  ...(location.assessmentId
                    ? [
                        { id: "aplicabilidad", label: connectedDestinations.licitud.aplicabilidad },
                        { id: "alcance", label: connectedDestinations.licitud.alcance },
                        { id: "base", label: connectedDestinations.licitud.base },
                        { id: "anexos", label: connectedDestinations.licitud.anexos },
                      ]
                    : []),
                ],
              },
              ...(location.assessmentId
                ? [
                    {
                      label: "Completar EIPD",
                      availabilityLabel: "EIPD: disponibilidad",
                      reason: eipdReason,
                      items: eipdReason
                        ? []
                        : eipdSections.map((label, step) => ({ id: "eipd", label, step })),
                    },
                    {
                      label: "Infancia y adolescencia",
                      availabilityLabel: "Infancia y adolescencia: disponibilidad",
                      reason: infanciaReason,
                      items: infanciaReason
                        ? []
                        : [
                            { id: "infancia", label: connectedDestinations.licitud.infancia },
                            { id: "preparar", label: connectedDestinations.licitud.preparar },
                          ],
                    },
                  ]
                : []),
              ...(location.assessmentId
                ? [
                    {
                      label: "Revisar y decidir",
                      items: [{ id: "revisar", label: connectedDestinations.licitud.revisar }],
                    },
                    {
                      label: "Historial y descargas",
                      items: [{ id: "historial", label: connectedDestinations.licitud.historial }],
                    },
                  ]
                : []),
            ]
          : [];
  function changeModule(module: ModuleId) {
    const remembered = rememberedLocations.current[memoryKey({ ...location, module })];
    go(
      remembered ?? {
        ...location,
        module,
        section:
          module === "licitud"
            ? location.assessmentId
              ? "aplicabilidad"
              : "catalogo"
            : module === "rat"
              ? "catalogo"
              : module === "diagnostico"
                ? "cuestionario"
                : "resumen",
        step: 0,
      }
    );
  }
  function section(item: Item) {
    go({ ...location, section: item.id, step: item.step ?? 0 });
  }
  async function apply(value: WorkContext) {
    const applied = await validate(
      {
        ...location,
        ...value,
        section:
          location.module === "licitud"
            ? value.assessmentId
              ? "aplicabilidad"
              : "catalogo"
            : location.module === "rat"
              ? "catalogo"
              : location.module === "diagnostico"
                ? "cuestionario"
                : "resumen",
        step: 0,
      },
      false
    );
    if (applied) setContext(false);
  }
  async function intercept(e: MouseEvent) {
    const a = (e.target as HTMLElement).closest("a");
    if (
      !a ||
      e.ctrlKey ||
      e.metaKey ||
      e.shiftKey ||
      e.altKey ||
      a.target === "_blank" ||
      a.hasAttribute("download")
    )
      return;
    const u = new URL(a.href, window.location.href);
    if (u.origin !== window.location.origin) return;
    const match = u.pathname.match(/^\/dashboard\/(rat|licitud)(?:\/([^/]+))?(?:\/([^/]+))?$/);
    if (!match) {
      if (anyPending) {
        e.preventDefault();
        e.stopPropagation();
        if (await confirmExit()) router.push(u.pathname + u.search + u.hash);
      }
      return;
    }
    e.preventDefault();
    const organizationId = u.searchParams.get("organizationId") ?? location.organizationId;
    const targetModule = match[1] as ModuleId;
    const tid = match[2];
    const aid = match[3];
    if (!tid) {
      go({ ...location, module: targetModule, section: "catalogo", step: 0 });
      return;
    }
    if (tid === "nuevo") {
      go({ ...location, module: "rat", section: "nuevo", step: 0 });
      return;
    }
    const next = {
      organizationId,
      treatmentId: tid,
      assessmentId:
        aid ??
        (targetModule === "rat" &&
        tid === location.treatmentId &&
        organizationId === location.organizationId
          ? location.assessmentId
          : ""),
      module: targetModule,
      section: targetModule === "rat" ? "general" : "aplicabilidad",
      step: 0,
    };
    await validate(next, false);
  }
  const activeKey = paneKey(location);
  function locationLabel(v: WorkLocation) {
    return connectedDestinationLabel(v, diagnosticSections[v.organizationId]);
  }
  const displayTitle = locationLabel(location);
  const moduleTitle =
    modules.find((item) => item.id === location.module)?.title ?? "Espacio de trabajo";
  useEffect(() => {
    document.title = `${displayTitle} · ${moduleTitle} | CumpleIA`;
  }, [displayTitle, moduleTitle]);
  const isCurrent = (item: Item) =>
    item.id === location.section && (item.step ?? 0) === location.step;
  function contextLabel(value: WorkLocation) {
    const organization = organizations.find((item) => item.id === value.organizationId);
    const parts = [`Organización: ${organization?.name ?? "Organización seleccionada"}`];
    if (["rat", "licitud"].includes(value.module) && value.treatmentId) {
      parts.push(`Tratamiento: ${names[value.treatmentId] ?? "Tratamiento seleccionado"}`);
    }
    if (value.module === "licitud" && value.assessmentId) {
      parts.push(
        `Finalidad y evaluación: ${evaluations[value.assessmentId] ? `${evaluations[value.assessmentId].purpose} · versión ${evaluations[value.assessmentId].version} · ${evaluations[value.assessmentId].status}` : "Evaluación seleccionada"}`
      );
    }
    return parts.join(" · ");
  }
  const list = (
    <nav aria-label="Secciones del espacio conectado" className="connected-sections">
      {groups.map((group) => (
        <div key={group.label}>
          <h3>{group.reason ? group.availabilityLabel : group.label}</h3>
          {group.reason && (
            <div className="connected-availability-reason">
              <p>{group.reason}</p>
              <button
                onClick={() =>
                  section({
                    id: "aplicabilidad",
                    label: connectedDestinations.licitud.aplicabilidad,
                  })
                }
              >
                Ir a Determinar aplicabilidad
              </button>
            </div>
          )}
          {group.items.map((item) => (
            <button
              key={`${item.id}:${item.step ?? 0}`}
              aria-current={isCurrent(item) ? "page" : undefined}
              onClick={() => section(item)}
            >
              {item.label}
            </button>
          ))}
        </div>
      ))}
    </nav>
  );
  const closeSections = useCallback(() => {
    setSections(false);
    requestAnimationFrame(() => document.getElementById("connected-sections-trigger")?.focus());
  }, []);
  const closeContext = useCallback(() => {
    sequence.current += 1;
    setValidating(false);
    setContext(false);
    requestAnimationFrame(() => document.getElementById("connected-context-trigger")?.focus());
  }, []);
  return (
    <div className="prototype-app connected-app">
      <p className="prototype-demo">
        Espacio conectado al servidor · Pruebas con datos ficticios · Confirmación y activación EIPD
        bloqueadas. <SignOutButton beforeSignOut={confirmExit} />
      </p>
      <div className="prototype-layout">
        <MainModules
          module={location.module}
          navigationLabel="Módulos del espacio de trabajo"
          drawerId="connected-menu-panel"
          go={changeModule}
          expanded={menu}
          setExpanded={setMenu}
          notify={setNotice}
        />
        <div className="min-w-0">
          <header className="prototype-top">
            <div className="connected-toolbar">
              <button
                id="prototype-menu-trigger"
                aria-label="Abrir menú"
                aria-haspopup="dialog"
                aria-expanded={menu}
                aria-controls="connected-menu-panel"
                className="connected-menu-trigger"
                onClick={() => {
                  closeDesktopGroups();
                  setSections(false);
                  setContext(false);
                  setMenu(true);
                }}
              >
                ☰ Menú
              </button>
              {groups.length > 0 && (
                <button
                  id="connected-sections-trigger"
                  aria-haspopup="dialog"
                  aria-expanded={sections}
                  aria-controls="connected-sections-panel"
                  onClick={() => {
                    closeDesktopGroups();
                    setMenu(false);
                    setContext(false);
                    setSections(true);
                  }}
                >
                  Secciones
                </button>
              )}
              <span data-testid="connected-destination" className="min-w-0 flex-1 truncate">
                {modules.find((v) => v.id === location.module)?.title} › {displayTitle}
              </span>
              <button
                id="connected-context-trigger"
                aria-haspopup="dialog"
                aria-expanded={context}
                aria-controls="connected-context-panel"
                onClick={() => {
                  closeDesktopGroups();
                  setMenu(false);
                  setSections(false);
                  setContext(true);
                }}
              >
                Cambiar contexto
              </button>
            </div>
            <div className="px-4 pb-3 text-sm">
              <ConnectedContextSummary
                key={`${location.module}:${contextKey(location)}`}
                organization={
                  organizations.find((item) => item.id === location.organizationId)?.name ??
                  "Organización seleccionada"
                }
                treatment={
                  ["rat", "licitud"].includes(location.module) && location.treatmentId
                    ? (names[location.treatmentId] ?? "Tratamiento seleccionado")
                    : undefined
                }
                assessmentSelected={location.module === "licitud" && !!location.assessmentId}
                evaluation={evaluations[location.assessmentId]}
              />
              {anyPending && (
                <p className="font-semibold text-amber-800">
                  Hay formularios editados durante esta visita. Guarda cada formulario antes de
                  recargar.
                </p>
              )}
            </div>
            <div className="connected-desktop-sections">
              {groups.map((g) =>
                g.items.length === 1 ? (
                  <div key={g.label} className="connected-direct-group">
                    {g.label !== g.items[0].label && (
                      <span className="connected-group-label">{g.label}</span>
                    )}
                    <a
                      href={encodeWork({
                        ...location,
                        section: g.items[0].id,
                        step: g.items[0].step ?? 0,
                      })}
                      aria-current={isCurrent(g.items[0]) ? "page" : undefined}
                      onClick={(event) => {
                        if (
                          event.button !== 0 ||
                          event.metaKey ||
                          event.ctrlKey ||
                          event.shiftKey ||
                          event.altKey
                        )
                          return;
                        event.preventDefault();
                        section(g.items[0]);
                      }}
                    >
                      {g.items[0].label}
                    </a>
                  </div>
                ) : (
                  <details
                    key={g.label}
                    data-current-group={g.items.some(isCurrent) || undefined}
                    onBlur={(event) => {
                      if (!event.currentTarget.contains(event.relatedTarget))
                        event.currentTarget.open = false;
                    }}
                    onToggle={(event) => {
                      if (!event.currentTarget.open) return;
                      closeDesktopGroups(event.currentTarget);
                      const pop = event.currentTarget.querySelector<HTMLElement>(":scope > div");
                      if (pop) {
                        pop.style.left = "0px";
                        const rect = pop.getBoundingClientRect();
                        pop.style.left = `${Math.max(8 - rect.left, Math.min(0, window.innerWidth - 8 - rect.right))}px`;
                      }
                    }}
                  >
                    <summary
                      onKeyDown={(event) => {
                        if (event.code !== "Space" && event.key !== " " && event.key !== "Spacebar")
                          return;
                        // Handle Space explicitly; cancel the native action to avoid a second toggle.
                        event.preventDefault();
                        if (event.repeat) return;
                        const group = event.currentTarget.parentElement as HTMLDetailsElement;
                        if (!group.open) closeDesktopGroups(group);
                        group.open = !group.open;
                      }}
                      onKeyUp={(event) => {
                        if (event.code === "Space" || event.key === " " || event.key === "Spacebar")
                          event.preventDefault();
                      }}
                    >
                      {g.reason ? g.availabilityLabel : g.label}
                    </summary>
                    <div>
                      {g.reason && (
                        <div className="connected-availability-reason">
                          <p>{g.reason}</p>
                          <button
                            onClick={(event) => {
                              event.currentTarget.closest("details")?.removeAttribute("open");
                              section({
                                id: "aplicabilidad",
                                label: connectedDestinations.licitud.aplicabilidad,
                              });
                            }}
                          >
                            Ir a Determinar aplicabilidad
                          </button>
                        </div>
                      )}
                      {g.items.map((item) => (
                        <button
                          key={`${item.id}:${item.step ?? 0}`}
                          aria-current={isCurrent(item) ? "page" : undefined}
                          onClick={(e) => {
                            e.currentTarget.closest("details")?.removeAttribute("open");
                            section(item);
                          }}
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
                  </details>
                )
              )}
            </div>
          </header>
          {validating && !context && (
            <p role="status" className="m-4 rounded bg-blue-50 p-4">
              Consultando evaluación y contexto autorizado…
            </p>
          )}
          {error && !context && (
            <div className="m-4 space-y-3 rounded bg-red-50 p-4 text-red-800">
              <p role="alert">{error}</p>
              {validationTarget.current && (
                <button
                  className="rounded border p-3"
                  disabled={validating}
                  onClick={() => {
                    if (validationTarget.current) void validate(validationTarget.current);
                  }}
                >
                  Reintentar apertura
                </button>
              )}
            </div>
          )}
          {notice && (
            <p role="status" className="m-4 rounded bg-blue-50 p-4">
              {notice}
            </p>
          )}
          {location.module === "diagnostico" && (
            <p className="px-4 py-2 text-sm">
              El Autodiagnóstico se guarda por organización; no pertenece a una evaluación de
              licitud.
            </p>
          )}
          <main
            ref={content}
            tabIndex={-1}
            aria-labelledby="connected-work-title"
            className="prototype-work"
            onClickCapture={intercept}
          >
            {location.module !== "panel" && (
              <h1 id="connected-work-title" className="sr-only">
                Área de trabajo: {displayTitle}
              </h1>
            )}
            {location.module === "panel" && (
              <div className="space-y-6">
                <h1 id="connected-work-title" className="text-2xl font-bold">
                  Panel principal
                </h1>
                <p>
                  Trabaja con la información de tu organización guardada en el servidor. La
                  selección de contexto es independiente en cada ventana.
                </p>
                {last && (
                  <button
                    className="max-w-full rounded bg-blue-800 p-3 text-left text-white"
                    onClick={() => go(last)}
                  >
                    <span className="block font-semibold">Continuar en {locationLabel(last)}</span>
                    <span className="mt-1 block text-sm">{contextLabel(last)}</span>
                  </button>
                )}
                <div className="grid gap-4 sm:grid-cols-2">
                  {modules
                    .filter((v) => v.id !== "panel")
                    .map((v) => (
                      <button
                        key={v.id}
                        aria-disabled={v.upcoming || undefined}
                        className="rounded-xl border bg-white p-5 text-left"
                        onClick={() =>
                          v.upcoming ? setNotice(`${v.title}: próximamente.`) : changeModule(v.id)
                        }
                      >
                        <strong>{v.title}</strong>
                        <p>{v.upcoming ? "Próximamente" : "Abrir módulo →"}</p>
                      </button>
                    ))}
                </div>
                <Link href="/dashboard/maqueta" className="text-blue-800 underline">
                  Consultar maqueta de referencia
                </Link>
              </div>
            )}
            {Object.entries(panes).map(([key, entry]) => {
              const here = key === activeKey;
              const v = here ? location : entry;
              const organization = organizations.find((o) => o.id === v.organizationId);
              if (!organization) return null;
              const readOnly = !["owner", "admin", "editor"].includes(organization.role);
              const permissionHelpId = `connected-permissions-${key.replaceAll(":", "-")}`;
              const organizationReadOnly = !["owner", "admin"].includes(organization.role);
              return (
                <div key={key} hidden={!here} data-work-pane={key}>
                  {v.module === "diagnostico" && (
                    <ConnectedDiagnostic
                      organization={organization}
                      location={v}
                      go={go}
                      onSections={updateDiagnostic}
                      onPending={updatePending}
                    />
                  )}
                  {v.module === "rat" && (
                    <>
                      {readOnly && (
                        <p
                          id={permissionHelpId}
                          className="mb-4 rounded border border-blue-200 bg-blue-50 p-3"
                        >
                          Tu rol permite solo consulta del RAT; no puedes crear ni modificar
                          actividades de tratamiento.
                        </p>
                      )}
                      <fieldset
                        disabled={readOnly}
                        aria-describedby={readOnly ? permissionHelpId : undefined}
                      >
                        <div hidden={!["catalogo", "resumen"].includes(v.section)}>
                          <RatWorkspace organizaciones={[organization]} />
                        </div>
                        {v.section === "nuevo" && (
                          <TreatmentGeneralForm
                            organizaciones={[organization]}
                            initialOrganizationId={organization.id}
                            onPending={(value) =>
                              updatePending(`rat-new:${v.organizationId}`, value)
                            }
                            onCreated={(id) =>
                              void validate({
                                ...v,
                                treatmentId: id,
                                section: "general",
                                assessmentId: "",
                              })
                            }
                          />
                        )}{" "}
                        {v.treatmentId && v.section !== "nuevo" && (
                          <div hidden={["catalogo", "nuevo", "resumen"].includes(v.section)}>
                            <TreatmentGeneralForm
                              organizaciones={[organization]}
                              initialOrganizationId={organization.id}
                              treatmentId={v.treatmentId}
                              activeSection={v.section}
                              onPending={(value) =>
                                updatePending(`rat:${v.organizationId}:${v.treatmentId}`, value)
                              }
                            />
                          </div>
                        )}
                      </fieldset>
                    </>
                  )}
                  {v.module === "licitud" && (
                    <>
                      <div
                        hidden={!!v.assessmentId && !["catalogo", "resumen"].includes(v.section)}
                      >
                        <LicitudWorkspace
                          organizaciones={[organization]}
                          onPending={(value) => updatePending(`create:${key}`, value)}
                        />
                      </div>
                      {v.assessmentId && (
                        <div hidden={["catalogo"].includes(v.section)}>
                          <ConnectedAssessment
                            active={here}
                            location={v}
                            name={organization.name}
                            readOnly={readOnly}
                            go={go}
                            onScope={updateScope}
                            onAvailability={updateAvailability}
                            onPending={updatePending}
                          />
                        </div>
                      )}
                    </>
                  )}
                  {v.module === "organizacion" && (
                    <>
                      {organizationReadOnly && (
                        <p
                          id={permissionHelpId}
                          className="mb-4 rounded border border-blue-200 bg-blue-50 p-3"
                        >
                          Tu rol permite consultar los datos de la organización, pero no
                          modificarlos.
                        </p>
                      )}
                      <fieldset
                        disabled={organizationReadOnly}
                        aria-describedby={organizationReadOnly ? permissionHelpId : undefined}
                      >
                        <legend className="mb-4 text-xl font-bold">Mi organización</legend>
                        <OrganizacionForm
                          organizacion={organization}
                          onPending={(value) => updatePending(`org:${organization.id}`, value)}
                        />
                      </fieldset>
                    </>
                  )}
                </div>
              );
            })}
          </main>
        </div>
      </div>
      <PrototypeDrawer
        open={exitOpen}
        label="Salir del espacio de trabajo"
        className="prototype-sections-drawer"
        close={cancelExit}
      >
        <h2 className="text-xl font-bold">Hay cambios sin guardar</h2>
        <p className="my-4">
          Si sales, se perderán los borradores de esta visita que no hayas guardado en el servidor.
        </p>
        <button className="mr-3 rounded border p-3" onClick={cancelExit}>
          Continuar editando
        </button>
        <button className="rounded bg-blue-800 p-3 text-white" onClick={acceptExit}>
          Salir sin guardar
        </button>
      </PrototypeDrawer>
      <PrototypeDrawer
        open={sections}
        id="connected-sections-panel"
        label="Secciones del módulo"
        className="prototype-sections-drawer"
        close={closeSections}
      >
        <h2 className="text-xl font-bold">Secciones del módulo</h2>
        <button className="prototype-drawer-close" onClick={closeSections}>
          Cerrar secciones
        </button>
        {list}
      </PrototypeDrawer>
      <PrototypeDrawer
        open={context}
        id="connected-context-panel"
        label="Contexto de trabajo"
        className="prototype-sections-drawer"
        close={closeContext}
      >
        <h2 className="mb-4 text-xl font-bold">Contexto de trabajo</h2>
        {context && (
          <ConnectedContext
            organizations={organizations}
            current={location}
            applying={validating}
            applyError={error}
            apply={(value) => void apply(value)}
            cancel={closeContext}
          />
        )}
      </PrototypeDrawer>
    </div>
  );
}
