"use client";
import { documentFields, type Fields } from "@/lib/licitud/eipd-document";
import { eipdGroups } from "./EipdDocumentFields";
type Issue = { field: string; code: string; category: string };
export function EipdPendingContent({
  issues,
  saved,
  onComplete,
}: {
  issues: Issue[];
  saved: Record<string, unknown>;
  onComplete: (root: string) => void;
}) {
  return (
    <div className="space-y-3">
      <p>
        Estos pendientes corresponden al contenido guardado en el servidor. Completa los campos y
        guarda el borrador para actualizar esta lista; las ediciones pendientes aún no se incluyen.
      </p>
      {issues.length === 0 ? (
        <p>No hay pendientes documentales informados.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left">
            <caption className="text-left font-semibold">
              Pendientes documentales ({issues.length})
            </caption>
            <thead>
              <tr>
                {["Sección", "Pendiente", "Acción"].map((label) => (
                  <th key={label} className="border bg-blue-50 p-3">
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {issues.map((issue, index) => {
                const parts = issue.field.split(/[.\[\]]/).filter(Boolean);
                const root = parts[0];
                const group = eipdGroups.find((group) => group.keys.includes(root));
                let fields: Fields = documentFields;
                const labels: string[] = [];
                for (const part of parts) {
                  const field = fields[part];
                  if (field) {
                    labels.push(field.label);
                    fields = field.fields ?? field.item ?? {};
                  }
                }
                const rows = saved[root];
                const item =
                  Array.isArray(rows) && /^\d+$/.test(parts[1] ?? "")
                    ? rows[Number(parts[1])]
                    : null;
                const identifier =
                  item && typeof item === "object"
                    ? String(item.risk_id ?? item.measure_id ?? "")
                    : "";
                const name = labels.join(" — ") || "Antecedentes de la evaluación";
                const specific: Record<string, string> = {
                  "scope.data_category_codes": "Falta indicar las categorías de datos incluidas.",
                  "scope.data_subject_codes":
                    "Falta indicar las categorías de titulares incluidas.",
                };
                const missing = issue.category === "incompleto";
                const riskDamage = root === "risks" && parts.at(-1) === "impact_analysis";
                const description =
                  (identifier ? identifier + ": " : "") +
                  (missing && specific[issue.field]
                    ? specific[issue.field]
                    : riskDamage && missing
                      ? "Falta describir el daño potencial a las personas."
                      : issue.code === "finalidad_distinta"
                        ? "La finalidad del documento difiere del alcance guardado; revisa su correspondencia."
                        : issue.code === "alcance_rat_discordante"
                          ? name + ": revisa su correspondencia con el alcance guardado."
                          : issue.code === "fundamento_ausente"
                            ? name + ": falta explicar el fundamento."
                            : issue.code === "respuesta_pendiente"
                              ? name + ": falta resolver la respuesta pendiente."
                              : missing
                                ? name + ": falta completar este dato."
                                : name + ": requiere revisar los antecedentes y su fundamento.");
                const action =
                  root === "scope"
                    ? "Completar alcance"
                    : root === "risks"
                      ? "Completar riesgo" + (identifier ? " " + identifier : "s")
                      : "Completar sección";
                return (
                  <tr key={index}>
                    <td className="border p-3 align-top">
                      {group?.title ?? "Antecedentes de la evaluación"}
                    </td>
                    <td className="border p-3 align-top">{description}</td>
                    <td className="border p-3 align-top">
                      {group ? (
                        <button
                          type="button"
                          className="rounded border border-blue-300 bg-blue-50 px-3 py-2 font-semibold text-blue-800 focus-visible:outline focus-visible:outline-2"
                          onClick={() => onComplete(root)}
                        >
                          {action}
                        </button>
                      ) : (
                        "Revisar el contexto y los antecedentes de la evaluación."
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
