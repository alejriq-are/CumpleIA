export type DocumentCapability = {
  action: string;
  state: "available" | "blocked" | "pending";
  reason: string;
};
const states = { available: "Disponible", blocked: "No disponible", pending: "Por comprobar" };
export function DocumentCapabilities({
  object,
  actions,
}: {
  object: string;
  actions: DocumentCapability[];
}) {
  return (
    <aside
      aria-label={`Acciones y requisitos: ${object}`}
      className="space-y-2 rounded border border-slate-300 bg-slate-50 p-3 text-sm break-words"
    >
      <h3 className="font-semibold">Acciones y requisitos</h3>
      <p className="font-medium">{object}</p>
      <ul className="space-y-2">
        {actions.map(({ action, state, reason }) => (
          <li key={action}>
            <strong>
              {action}: {states[state]}.
            </strong>{" "}
            {reason}
          </li>
        ))}
      </ul>
    </aside>
  );
}
