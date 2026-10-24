import Link from "next/link";
import { createClient } from "@/lib/supabase/server";

const MODULOS = [
  {
    titulo: "Autodiagnóstico",
    descripcion: "Cuestionario CCS, evaluación de brechas e informe de estado de cumplimiento.",
    href: "/dashboard/autodiagnostico",
  },
  {
    titulo: "Inventario de tratamientos (RAT)",
    descripcion:
      "Registro de Actividades de Tratamiento y gestión del inventario de datos personales.",
    href: "/dashboard/rat",
  },
  {
    titulo: "Bases de licitud",
    descripcion: "Evaluaciones en borrador, fundamentos y documentación LIA de cada tratamiento.",
    href: "/dashboard/licitud",
  },
  {
    titulo: "Documentos",
    descripcion: "Generación de políticas y procedimientos en formato Word / PDF.",
    href: null,
  },
  {
    titulo: "Evidencia",
    descripcion: "Bitácora inmutable con hash encadenado y exportación del expediente.",
    href: null,
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
        <h1 className="text-2xl font-bold text-gray-900">Panel de adecuación</h1>
        <p className="mt-1 break-words text-gray-500">
          Bienvenido/a, <span className="break-all font-medium">{user?.email}</span>. Tu proceso de
          adecuación a la Ley 21.719 comienza aquí.
        </p>
      </div>

      {/* Estado de desarrollo */}
      <div className="mb-8 rounded-xl border border-blue-200 bg-blue-50 px-5 py-4 text-sm text-blue-800">
        <strong>MVP en desarrollo</strong> — Los módulos se habilitarán progresivamente. Las pruebas
        se realizan con datos ficticios.
      </div>

      <aside className="mb-8 rounded-xl border border-blue-200 bg-blue-50 p-5">
        <h2 className="text-lg font-bold text-blue-950">Nueva propuesta de navegación integral</h2>
        <p className="mt-2 text-slate-700">
          Explora el panel, los módulos y los recorridos de adultos e infancia con ejemplos
          ficticios. Tus expedientes no cambian.
        </p>
        <Link
          href="/dashboard/maqueta"
          className="mt-4 inline-block rounded-lg bg-blue-800 px-4 py-3 font-semibold text-white hover:bg-blue-900"
        >
          Abrir maqueta integral de CumpleIA →
        </Link>
      </aside>
      {/* Tarjetas de módulos */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {MODULOS.map((m) => {
          const contenido = (
            <>
              <h2 className="font-semibold text-gray-900">{m.titulo}</h2>
              <p className="mt-1 text-sm text-gray-500">{m.descripcion}</p>
              {!m.href && (
                <span className="mt-4 inline-block rounded-full bg-violet-50 px-2 py-1 text-xs font-medium text-violet-700">
                  Próximamente
                </span>
              )}
            </>
          );

          return m.href ? (
            <Link
              key={m.titulo}
              href={m.href}
              className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
            >
              {contenido}
            </Link>
          ) : (
            <div
              key={m.titulo}
              className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
            >
              {contenido}
            </div>
          );
        })}
      </div>
    </div>
  );
}
