import Link from "next/link";

export default async function TratamientoPage({
  params,
}: {
  params: Promise<{ treatmentId: string }>;
}) {
  const { treatmentId } = await params;

  return (
    <div className="space-y-6">
      <Link href="/dashboard/rat" className="text-sm text-blue-700 hover:underline">
        ← Volver al inventario
      </Link>

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-900">Actividad de tratamiento</h1>
        <p className="mt-2 text-sm text-gray-500">
          La ficha de edición se implementará en M2-T3.2.
        </p>
        <p className="mt-4 text-xs text-gray-400">ID: {treatmentId}</p>
      </div>
    </div>
  );
}
