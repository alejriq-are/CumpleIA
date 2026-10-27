"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { PrototypeDrawer } from "./PrototypeDrawer";
import { modules, type ModuleId, type Scenario } from "./prototype-data";
import {
  moduleNavigation,
  groupDestinations,
  destinationLabel,
  actionLabel,
  type Destination,
} from "./prototype-navigation";
function Icon({ index }: { index: number }) {
  const paths = [
    "M3 10 12 3l9 7v11h-6v-7H9v7H3Z",
    "M5 3h14v18H5ZM8 8h8M8 12h8M8 16h5",
    "M3 5h18v14H3ZM3 10h18M9 10v9",
    "M12 3 3 7v6c0 5 9 8 9 8s9-3 9-8V7ZM8 12l3 3 5-6",
    "M5 3h10l4 4v14H5ZM14 3v5h5M8 12h8M8 16h8",
    "M4 7h6l2-3h8v17H4ZM8 12h8M8 16h5",
    "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4 21v-3c0-5 16-5 16 0v3",
  ];
  return (
    <svg
      aria-hidden="true"
      className="mt-0.5 h-5 w-5 shrink-0"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
    >
      <path d={paths[index]} />
    </svg>
  );
}

export function MainModules({
  module,
  go,
  expanded,
  setExpanded,
  notify,
  navigationLabel = "Módulos de la maqueta",
  drawerId,
}: {
  navigationLabel?: string;
  drawerId?: string;
  module: ModuleId;
  go: (module: ModuleId) => void;
  expanded: boolean;
  setExpanded: (open: boolean) => void;
  notify: (text: string) => void;
}) {
  const [mobile, setMobile] = useState(false);
  const [unavailable, setUnavailable] = useState("");
  useEffect(() => {
    const media = window.matchMedia("(max-width: 767px)");
    const update = () => {
      setMobile(media.matches);
      setExpanded(false);
    };
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, [setExpanded]);
  const close = useCallback(() => {
    setExpanded(false);
    requestAnimationFrame(() => document.getElementById("prototype-menu-trigger")?.focus());
  }, [setExpanded]);
  const nav = (
    <>
      <div className="prototype-brand">
        <strong>CumpleIA</strong>
        <small>Cumplimiento de datos personales</small>
        {mobile && (
          <button className="prototype-drawer-close" onClick={close}>
            Cerrar menú
          </button>
        )}
      </div>
      <nav id="prototype-global-menu" aria-label={navigationLabel}>
        {[
          { title: "Trabajo", ids: ["panel", "diagnostico", "rat", "licitud"] },
          { title: "Próximas funciones", ids: ["documentos", "evidencia"] },
          { title: "Cuenta", ids: ["organizacion"] },
        ].map((group) => (
          <div key={group.title}>
            <h2>{group.title}</h2>
            {modules
              .filter((item) => group.ids.includes(item.id))
              .map((item) => (
                <button
                  key={item.id}
                  title={item.title}
                  aria-label={item.title + (item.upcoming ? " · Próximamente" : "")}
                  aria-disabled={item.upcoming || undefined}
                  aria-current={item.id === module ? "page" : undefined}
                  onClick={() => {
                    if (item.upcoming) {
                      const message = `${item.title}: próximamente. Aún no está disponible.`;
                      notify(message);
                      setUnavailable(message);
                      return;
                    }
                    setExpanded(false);
                    go(item.id);
                  }}
                >
                  <Icon index={modules.indexOf(item)} />
                  <span className="prototype-rail-label">
                    {item.title}
                    {item.upcoming && <small>Próximamente</small>}
                  </span>
                </button>
              ))}
          </div>
        ))}
      </nav>
      {mobile && unavailable && (
        <p role="status" className="p-3 text-sm text-white">
          {unavailable}
        </p>
      )}
    </>
  );
  return mobile ? (
    <PrototypeDrawer
      open={expanded}
      id={drawerId}
      label="Menú principal"
      className="prototype-rail"
      close={close}
    >
      {nav}
    </PrototypeDrawer>
  ) : (
    <aside className="prototype-rail">{nav}</aside>
  );
}
export function ModuleOptions({
  scope,
  location,
  scenario,
  go,
  status,
  mobileExpanded,
  setMobileExpanded,
}: {
  location: Destination;
  scope: import("./prototype-applicability").DocumentScope;
  scenario: Scenario;
  go: (module: ModuleId, task: Destination["task"], section: string) => void;
  status: (section: string) => string;
  mobileExpanded: boolean;
  setMobileExpanded: (expanded: boolean) => void;
}) {
  const [open, setOpen] = useState<string | null>(null);
  const root = useRef<HTMLElement>(null);
  const wrapper = useRef<HTMLDivElement>(null);
  const [mobile, setMobile] = useState(false);
  useEffect(() => {
    const media = window.matchMedia("(max-width: 767px)");
    const update = () => {
      setMobile(media.matches);
      setMobileExpanded(false);
    };
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, [setMobileExpanded]);
  const closeSections = useCallback(() => {
    setOpen(null);
    setMobileExpanded(false);
    requestAnimationFrame(() => document.getElementById("prototype-sections-trigger")?.focus());
  }, [setMobileExpanded]);

  const triggers = useRef<Record<string, HTMLButtonElement | null>>({});
  const groups = moduleNavigation(location.module, scenario, scope);
  useEffect(() => {
    setOpen(null);
    setMobileExpanded(false);
  }, [location, scenario, setMobileExpanded]);
  useEffect(() => {
    if (mobile || !open) return;
    const outside = (event: PointerEvent) => {
      if (
        !wrapper.current?.contains(event.target as Node) &&
        !(event.target as HTMLElement).closest("#prototype-sections-trigger")
      ) {
        setOpen(null);
        setMobileExpanded(false);
      }
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.preventDefault();
      if (mobileExpanded) {
        closeSections();
      } else if (open) {
        triggers.current[open]?.focus();
        setOpen(null);
      } else {
        setMobileExpanded(false);
        document.getElementById("prototype-sections-trigger")?.focus();
      }
    };
    let width = window.innerWidth;
    const resize = () => {
      if (window.innerWidth !== width) {
        width = window.innerWidth;
        setOpen(null);
        setMobileExpanded(false);
      }
    };
    document.addEventListener("pointerdown", outside);
    document.addEventListener("keydown", escape);
    window.addEventListener("resize", resize);
    return () => {
      document.removeEventListener("pointerdown", outside);
      document.removeEventListener("keydown", escape);
      window.removeEventListener("resize", resize);
    };
  }, [open, mobileExpanded, setMobileExpanded, closeSections, mobile]);
  function focusItem(id: string, last = false) {
    requestAnimationFrame(() => {
      const items = root.current?.querySelectorAll<HTMLButtonElement>(
        `[data-group="${id}"] button`
      );
      items?.[last ? items.length - 1 : 0]?.focus();
    });
  }
  const nav = (
    <nav ref={root} id="prototype-module-options" aria-label="Opciones del módulo">
      {groups.map((group) => {
        const items = groupDestinations(group, scenario);
        const direct = items.length === 1;
        const active = items.some(
          (item) => item.task === location.task && item.section === location.section
        );
        const dirtyCount = items.filter(
          (item) => status(item.section) === "Cambios sin guardar"
        ).length;
        const temporary = items.some((item) => status(item.section) === "Borrador temporal");
        const hasSaved = items.some((item) => status(item.section) === "Guardado en maqueta");
        const state = dirtyCount
          ? `${dirtyCount} con cambios sin guardar`
          : temporary
            ? "Borrador temporal"
            : hasSaved
              ? "Guardado en maqueta"
              : "";
        return (
          <div className="prototype-tab" key={group.id}>
            {mobile && !direct ? (
              <h3 className="prototype-section-group-title">{group.label}</h3>
            ) : (
              <button
                ref={(node) => {
                  triggers.current[group.id] = node;
                }}
                data-nav-group={group.id}
                type="button"
                aria-expanded={direct ? undefined : open === group.id}
                aria-controls={direct ? undefined : `prototype-options-${group.id}`}
                aria-current={active ? "page" : undefined}
                onClick={() => {
                  if (direct) {
                    setOpen(null);
                    setMobileExpanded(false);
                    go(items[0].module, items[0].task, items[0].section);
                  } else setOpen(open === group.id ? null : group.id);
                }}
                onKeyDown={(event) => {
                  if (!direct && ["ArrowDown", "ArrowUp"].includes(event.key)) {
                    event.preventDefault();
                    setOpen(group.id);
                    focusItem(group.id, event.key === "ArrowUp");
                  }
                }}
              >
                {direct && group.id !== "infancia"
                  ? destinationLabel(items[0].section, items[0].module)
                  : group.label}
                {state && (
                  <>
                    <span
                      aria-hidden="true"
                      className={`prototype-dot ${!dirtyCount && !temporary ? "saved" : ""}`}
                    />
                    <span className="sr-only">{state}</span>
                  </>
                )}
                {!direct && <span aria-hidden="true">{open === group.id ? "▴" : "▾"}</span>}
              </button>
            )}
            {!direct && (mobile || open === group.id) && (
              <div
                id={`prototype-options-${group.id}`}
                data-group={group.id}
                className="prototype-pop"
                ref={(node) => {
                  if (!node || window.innerWidth < 768) return;
                  node.style.left = "0px";
                  const rect = node.getBoundingClientRect();
                  node.style.left = `${Math.max(12 - rect.left, Math.min(0, window.innerWidth - 12 - rect.right))}px`;
                }}
                onBlur={(event) => {
                  if (
                    event.relatedTarget &&
                    !event.currentTarget.parentElement?.contains(event.relatedTarget as Node)
                  )
                    setOpen(null);
                }}
                onKeyDown={(event) => {
                  if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
                  event.preventDefault();
                  const buttons = Array.from(
                    event.currentTarget.querySelectorAll<HTMLButtonElement>("button")
                  );
                  const i = buttons.indexOf(document.activeElement as HTMLButtonElement);
                  buttons[
                    event.key === "Home"
                      ? 0
                      : event.key === "End"
                        ? buttons.length - 1
                        : (i + (event.key === "ArrowUp" ? -1 : 1) + buttons.length) % buttons.length
                  ]?.focus();
                }}
              >
                <p className="prototype-pop-title">{group.label}</p>
                {items.map((item) => (
                  <button
                    key={item.section}
                    aria-current={
                      item.section === location.section && item.task === location.task
                        ? "page"
                        : undefined
                    }
                    onClick={() => {
                      setOpen(null);
                      setMobileExpanded(false);
                      go(item.module, item.task, item.section);
                    }}
                  >
                    <span>
                      {destinationLabel(item.section, item.module)}
                      {status(item.section) && (
                        <small className="block text-xs text-slate-500">
                          {status(item.section)}
                        </small>
                      )}
                    </span>
                    <span
                      className={`prototype-verb ${actionLabel(item, scenario) === "Decisión" ? "decision" : ""}`}
                    >
                      {actionLabel(item, scenario)}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </nav>
  );
  return (
    <div ref={wrapper} className="prototype-section-options">
      {mobile ? (
        <PrototypeDrawer
          open={mobileExpanded}
          label="Secciones del módulo"
          className="prototype-sections-drawer"
          close={closeSections}
        >
          <div className="prototype-sections-heading">
            <h2 id="prototype-sections-title">Secciones del módulo</h2>
            <button className="prototype-drawer-close" onClick={closeSections}>
              Cerrar secciones
            </button>
          </div>
          <p className="px-2 pb-2 text-xs text-slate-600">Escape o clic en el fondo para cerrar.</p>
          {nav}
        </PrototypeDrawer>
      ) : (
        nav
      )}
    </div>
  );
}
