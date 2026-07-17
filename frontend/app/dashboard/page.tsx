import { createClient } from "@/lib/supabase/server";

const MODULOS = [
  {
    titulo: "Autodiagnóstico",
    descripcion:
      "Cuestionario CCS, scoring de brechas e informe de estado de cumplimiento.",
  },
  {
    titulo: "Inventario (RAT)",
    descripcion:
      "Registro de Actividades de Tratamiento con detección de datos sensibles.",
  },
  {
    titulo: "Bases de licitud",
    descripcion:
      "Clasificación jurídica de cada tratamiento y generación de LIA.",
  },
  {
    titulo: "Documentos",
    descripcion:
      "Generación de políticas y procedimientos en formato Word / PDF.",
  },
  {
    titulo: "Evidencia",
    descripcion:
      "Bitácora inmutable con hash encadenado y exportación del expediente.",
  },
];

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <div>
      {/* Encabezado */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Panel de adecuación
        </h1>
        <p className="mt-1 text-gray-500">
          Bienvenido/a,{" "}
          <span className="font-medium">{user?.email}</span>. Tu sprint de
          adecuación a la Ley 21.719 comienza aquí.
        </p>
      </div>

      {/* Alerta fase 0 */}
      <div className="mb-8 rounded-xl border border-blue-200 bg-blue-50 px-5 py-4 text-sm text-blue-800">
        <strong>Fase 0 en curso</strong> — Los módulos se habilitarán
        progresivamente. Estamos construyendo los cimientos del sistema.
      </div>

      {/* Tarjetas de módulos */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {MODULOS.map((m) => (
          <div
            key={m.titulo}
            className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
          >
            <h2 className="font-semibold text-gray-900">{m.titulo}</h2>
            <p className="mt-1 text-sm text-gray-500">{m.descripcion}</p>
            <span className="mt-4 inline-block rounded-full bg-violet-50 px-2 py-1 text-xs font-medium text-violet-700">
              Próximamente
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
