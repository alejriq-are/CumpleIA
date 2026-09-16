import Link from "next/link";

export default function NuevoTratamientoPage() {
  return (
    <div className="space-y-6">
      <Link href="/dashboard/rat" className="text-sm text-blue-700 hover:underline">
        ← Volver al inventario
      </Link>

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-900">Nueva actividad</h1>
        <p className="mt-2 text-sm text-gray-500">
          El formulario de creación se implementará en M2-T3.2.
        </p>
      </div>
    </div>
  );
}
