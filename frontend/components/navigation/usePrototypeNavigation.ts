"use client";
import { useEffect, useRef, useState } from "react";
import {
  modules,
  evaluationOptions,
  type EvaluationId,
  type ModuleId,
  type TaskId,
} from "./prototype-data";
import { moduleNavigation, groupDestinations, type Destination } from "./prototype-navigation";
type Visit = { location: Destination; evaluationId: EvaluationId };
const start: Destination = { module: "panel", task: "resumen", section: "estado" };
function destinations(module: ModuleId, id: EvaluationId) {
  const scenario = evaluationOptions.find((item) => item.id === id)!.treatment;
  return moduleNavigation(module, scenario).flatMap((group) => groupDestinations(group, scenario));
}
function valid(destination: Destination, id: EvaluationId) {
  return destinations(destination.module, id).some(
    (item) => item.task === destination.task && item.section === destination.section
  );
}
function fragment(visit: Visit) {
  const { module, task, section } = visit.location;
  return `#/${module}/${task}/${section}?evaluacion=${visit.evaluationId}`;
}
function parse(hash: string): Visit {
  const [path, query] = hash.slice(1).split("?");
  const [, mod, task, section] = path.split("/");
  const candidate = new URLSearchParams(query).get("evaluacion");
  const evaluationId = evaluationOptions.find((item) => item.id === candidate)?.id ?? "adultos";
  const moduleId = modules.find((item) => item.id === mod && !item.upcoming)?.id ?? "panel";
  const items = destinations(moduleId, evaluationId);
  const location =
    items.find((item) => item.task === task && item.section === section) ?? items[0] ?? start;
  return { location, evaluationId };
}
export function usePrototypeNavigation() {
  const [visit, setVisit] = useState<Visit>({ location: start, evaluationId: "adultos" });
  const current = useRef(visit);
  const remembered = useRef<Partial<Record<EvaluationId, Partial<Record<ModuleId, Destination>>>>>(
    {}
  );
  const latest = useRef<Partial<Record<EvaluationId, Destination>>>({});
  function apply(next: Visit, push = true) {
    const previous = current.current;
    remembered.current[previous.evaluationId] = {
      ...remembered.current[previous.evaluationId],
      [previous.location.module]: previous.location,
    };
    if (previous.location.module !== "panel")
      latest.current[previous.evaluationId] = previous.location;
    if (next.location.module !== "panel") latest.current[next.evaluationId] = next.location;
    current.current = next;
    setVisit(next);
    if (push && window.location.hash !== fragment(next))
      window.history.pushState(window.history.state, "", fragment(next));
  }
  useEffect(() => {
    const next = parse(window.location.hash);
    current.current = next;
    setVisit(next);
    if (next.location.module !== "panel") latest.current[next.evaluationId] = next.location;
    window.history.replaceState(window.history.state, "", fragment(next));
    const restore = () => {
      const next = parse(window.location.hash);
      if (fragment(next) !== fragment(current.current)) apply(next, false);
    };
    window.addEventListener("popstate", restore);
    window.addEventListener("hashchange", restore);
    return () => {
      window.removeEventListener("popstate", restore);
      window.removeEventListener("hashchange", restore);
    };
    // The listeners read refs so browser navigation never captures an old evaluation.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  function go(module: ModuleId, task?: TaskId, section?: string) {
    if (!modules.some((item) => item.id === module && !item.upcoming)) return;
    const id = current.current.evaluationId;
    const items = destinations(module, id);
    const previous = remembered.current[id]?.[module];
    const target = task
      ? items.find((item) => item.task === task && (!section || item.section === section))
      : previous && valid(previous, id)
        ? previous
        : items[0];
    if (target) apply({ evaluationId: id, location: target });
  }
  function selectEvaluation(id: EvaluationId) {
    if (!evaluationOptions.some((item) => item.id === id)) return;
    const old = current.current.location;
    const previous = remembered.current[id]?.[old.module];
    const location =
      previous && valid(previous, id)
        ? previous
        : valid(old, id)
          ? old
          : (destinations(old.module, id)[0] ?? start);
    apply({ evaluationId: id, location });
  }
  const resume =
    latest.current[visit.evaluationId] ??
    ({ module: "licitud", task: "completar", section: "base" } as Destination);
  function resetNavigation() {
    remembered.current = {};
    latest.current = {};
    apply({ evaluationId: current.current.evaluationId, location: start });
    remembered.current = {};
    latest.current = {};
  }
  return {
    ...visit,
    go,
    selectEvaluation,
    resume,
    hasResume: Boolean(latest.current[visit.evaluationId]),
    resetNavigation,
  };
}
