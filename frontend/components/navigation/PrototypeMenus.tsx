"use client";
import { useEffect, useRef, useState } from "react";
import { modules, type ModuleId, type Scenario } from "./prototype-data";
import {
  moduleNavigation,
  groupDestinations,
  destinationLabel,
  type Destination,
} from "./prototype-navigation";
const focus =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800";
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
export function MainModules({ module, go }: { module: ModuleId; go: (module: ModuleId) => void }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <aside className="min-w-0 self-start rounded-xl border border-slate-200 bg-white shadow-sm md:sticky md:top-4 md:max-h-[calc(100dvh-2rem)] md:overflow-y-auto">
      <div className="flex items-center justify-between gap-2 border-b border-slate-100 p-4">
        <div>
          <p className="text-lg font-bold text-blue-900">CumpleIA</p>
          <p className="text-xs text-slate-500">Menú principal</p>
        </div>
        <button
          type="button"
          className={`rounded-lg border border-slate-300 p-2 text-sm font-semibold md:hidden ${focus}`}
          aria-expanded={expanded}
          aria-controls="prototype-global-menu"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Cerrar menú" : "Abrir menú"}
        </button>
      </div>
      <nav
        id="prototype-global-menu"
        aria-label="Módulos de la maqueta"
        className={`${expanded ? "flex" : "hidden"} flex-col gap-1 p-2 md:flex`}
      >
        {modules.map((item, i) => (
          <button
            key={item.id}
            aria-current={item.id === module ? "page" : undefined}
            className={`flex items-start gap-3 rounded-lg border-l-4 px-3 py-3 text-left font-semibold ${focus} ${item.id === module ? "border-orange-600 bg-orange-100 text-orange-950" : "border-transparent text-slate-700 hover:bg-slate-100"}`}
            onClick={() => {
              setExpanded(false);
              go(item.id);
            }}
          >
            <Icon index={i} />
            <span>{item.id === "panel" ? "Inicio / Panel principal" : item.title}</span>
          </button>
        ))}
      </nav>
      <p className="hidden border-t border-slate-100 p-4 text-xs text-slate-500 md:block">
        Maqueta navegable
        <br />
        Datos ficticios durante esta visita
      </p>
    </aside>
  );
}
export function ModuleOptions({
  location,
  scenario,
  go,
  status,
}: {
  location: Destination;
  scenario: Scenario;
  go: (module: ModuleId, task: Destination["task"], section: string) => void;
  status: (section: string) => string;
}) {
  const [open, setOpen] = useState<string | null>(null);
  const [mobileExpanded, setMobileExpanded] = useState(false);
  const root = useRef<HTMLElement>(null);
  const triggers = useRef<Record<string, HTMLButtonElement | null>>({});
  const groups = moduleNavigation(location.module, scenario);
  useEffect(() => {
    setOpen(null);
    setMobileExpanded(false);
  }, [location, scenario]);
  useEffect(() => {
    if (!open) return;
    const outside = (event: PointerEvent) => {
      if (!root.current?.contains(event.target as Node)) setOpen(null);
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setOpen(null);
        triggers.current[open]?.focus();
      }
    };
    const resize = () => setOpen(null);
    window.addEventListener("resize", resize);
    document.addEventListener("pointerdown", outside);
    document.addEventListener("keydown", escape);
    return () => {
      window.removeEventListener("resize", resize);
      document.removeEventListener("pointerdown", outside);
      document.removeEventListener("keydown", escape);
    };
  }, [open]);
  function focusItem(id: string, last = false) {
    requestAnimationFrame(() => {
      const items = root.current?.querySelectorAll<HTMLButtonElement>(
        `[data-group="${id}"] button`
      );
      items?.[last ? items.length - 1 : 0]?.focus();
    });
  }
  return (
    <div>
      <button
        className={`mb-2 flex w-full items-center justify-between rounded-lg border border-orange-500 bg-orange-50 p-3 text-left text-sm font-bold text-orange-950 sm:hidden ${focus}`}
        aria-expanded={mobileExpanded}
        aria-controls="prototype-module-options"
        onClick={() => setMobileExpanded(!mobileExpanded)}
      >
        Opciones del módulo <span aria-hidden="true">{mobileExpanded ? "▴" : "▾"}</span>
      </button>
      <nav
        ref={root}
        id="prototype-module-options"
        aria-label="Opciones del módulo"
        className={`${mobileExpanded ? "grid" : "hidden"} max-h-[55dvh] grid-cols-1 gap-2 overflow-y-auto sm:flex sm:max-h-none sm:flex-wrap sm:overflow-visible`}
      >
        {groups.map((group) => {
          const items = groupDestinations(group, scenario);
          const direct = items.length === 1;
          const active = items.some(
            (item) => item.task === location.task && item.section === location.section
          );
          const expanded = open === group.id;
          return (
            <div className="relative min-w-0" key={group.id}>
              <button
                ref={(node) => {
                  triggers.current[group.id] = node;
                }}
                data-nav-group={group.id}
                type="button"
                aria-expanded={direct ? undefined : expanded}
                aria-controls={direct ? undefined : `prototype-options-${group.id}`}
                aria-current={active ? "step" : undefined}
                className={`flex min-h-12 w-full items-center justify-between gap-3 rounded-lg border px-3 py-3 text-left text-sm font-semibold ${focus} ${active ? "border-orange-600 bg-orange-100 text-orange-950" : group.accent ? "border-blue-700 bg-blue-50 text-blue-900 hover:bg-blue-100" : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"}`}
                onClick={() => {
                  if (direct) {
                    setOpen(null);
                    setMobileExpanded(false);
                    go(items[0].module, items[0].task, items[0].section);
                  } else setOpen(expanded ? null : group.id);
                }}
                onKeyDown={(event) => {
                  if (!direct && ["ArrowDown", "ArrowUp"].includes(event.key)) {
                    event.preventDefault();
                    setOpen(group.id);
                    focusItem(group.id, event.key === "ArrowUp");
                  }
                }}
              >
                <span>
                  {group.label}
                  {direct && status(items[0].section) && (
                    <span className="mt-1 block text-xs font-normal">
                      {status(items[0].section)}
                    </span>
                  )}
                </span>
                {!direct && (
                  <span aria-hidden="true" className="text-base">
                    {expanded ? "▴" : "▾"}
                  </span>
                )}
              </button>
              {!direct && expanded && (
                <div
                  id={`prototype-options-${group.id}`}
                  data-group={group.id}
                  ref={(node) => {
                    if (!node || window.innerWidth < 640) return;
                    node.style.left = "0px";
                    node.style.right = "auto";
                    const bounds = node.getBoundingClientRect();
                    node.style.left = `${Math.max(16 - bounds.left, Math.min(0, window.innerWidth - 16 - bounds.right))}px`;
                  }}
                  className={`relative z-30 mt-2 sm:absolute sm:top-full max-h-[55dvh] w-full overflow-y-auto rounded-xl border border-slate-300 bg-white p-2 shadow-xl sm:w-80 left-0`}
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
                    const next =
                      event.key === "Home"
                        ? 0
                        : event.key === "End"
                          ? buttons.length - 1
                          : (i + (event.key === "ArrowUp" ? -1 : 1) + buttons.length) %
                            buttons.length;
                    buttons[next]?.focus();
                  }}
                >
                  <p className="px-3 py-2 text-xs font-bold uppercase tracking-wide text-slate-500">
                    {group.label}
                  </p>
                  {items.map((item) => (
                    <button
                      key={item.section}
                      aria-current={
                        item.section === location.section && item.task === location.task
                          ? "step"
                          : undefined
                      }
                      className={`mb-1 flex w-full items-start justify-between gap-3 rounded-lg px-3 py-3 text-left text-sm ${focus} ${item.section === location.section && item.task === location.task ? "bg-orange-100 font-bold text-orange-950" : "text-slate-800 hover:bg-blue-50"}`}
                      onClick={() => {
                        setOpen(null);
                        setMobileExpanded(false);
                        go(item.module, item.task, item.section);
                      }}
                    >
                      <span>
                        {destinationLabel(item.section)}
                        {status(item.section) && (
                          <span className="mt-1 block text-xs font-normal text-slate-600">
                            {status(item.section)}
                          </span>
                        )}
                      </span>
                      <span aria-hidden="true">→</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </div>
  );
}
