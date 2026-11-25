"use client";
export function SessionRecovery({ required }: { required?: boolean }) {
  if (!required) return null;
  return (
    <div className="space-y-2 rounded border border-blue-300 bg-blue-50 p-3 text-slate-900">
      <a
        href="/login"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block rounded border border-blue-400 bg-white px-3 py-2 font-semibold text-blue-900 underline"
      >
        Iniciar sesión en otra pestaña
      </a>
      <p className="text-sm">
        Mantén abierta esta pestaña para conservar los cambios sin guardar. Después de iniciar
        sesión, vuelve aquí y reintenta la consulta. La pestaña nueva no recupera tus borradores
        pendientes.
      </p>
    </div>
  );
}
