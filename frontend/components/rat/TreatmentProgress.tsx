import type { TreatmentDetailOut } from "@/lib/api/client";

type Props = {
  treatment: TreatmentDetailOut;
};

type Requirement = {
  label: string;
  complete: boolean;
};

function declarationResolved(value: string | null) {
  return value === "si" || value === "no";
}

function statusLabel(status: TreatmentDetailOut["status"]) {
  switch (status) {
    case "borrador":
      return "Registro en preparación";
    case "activo":
      return "Activo";
    case "archivado":
      return "Archivado";
  }
}

export function TreatmentProgress({ treatment }: Props) {
  const requirements: Requirement[] = [
    {
      label: "Nombre de la actividad",
      complete: Boolean(treatment.name.trim()),
    },
    {
      label: "Rol de la organización",
      complete: Boolean(treatment.organization_role),
    },
    {
      label: "Finalidad registrada",
      complete: treatment.purposes.length > 0,
    },
    {
      label: "Categoría de datos registrada",
      complete: treatment.data_categories.length > 0,
    },
    {
      label: "Titular de datos registrado",
      complete: treatment.data_subjects.length > 0,
    },
    {
      label: "Fuente de datos registrada",
      complete: treatment.data_sources.length > 0,
    },
    {
      label: "Regla de conservación",
      complete: Boolean(treatment.retention_rule?.trim()),
    },
    {
      label: "Sistemas declarados",
      complete: declarationResolved(treatment.systems_declaration),
    },
    {
      label: "Proveedores declarados",
      complete: declarationResolved(treatment.vendors_declaration),
    },
    {
      label: "Transferencias internacionales declaradas",
      complete: declarationResolved(treatment.international_transfers_declaration),
    },
  ];

  const completed = requirements.filter((item) => item.complete).length;
  const percent = completed * 10;

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Preparación del registro</h2>
          <p className="mt-1 text-sm text-gray-500">
            Avance de los requisitos mínimos necesarios para poder activar esta actividad.
          </p>
        </div>

        <div className="self-start rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-700">
          {statusLabel(treatment.status)}
        </div>
      </div>

      <div className="mt-5">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="font-medium text-gray-700">{completed} de 10 requisitos</span>
          <span className="text-gray-500">{percent}%</span>
        </div>

        <div
          className="h-2.5 w-full overflow-hidden rounded-full bg-gray-200"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={10}
          aria-valuenow={completed}
          aria-label="Avance de preparación del registro"
        >
          <div
            className="h-full rounded-full bg-blue-700 transition-all"
            style={{ width: `${percent}%` }}
          />
        </div>
      </div>

      <div className="mt-5 grid gap-2 sm:grid-cols-2">
        {requirements.map((requirement) => (
          <div key={requirement.label} className="flex items-center gap-2 text-sm">
            <span
              aria-hidden="true"
              className={requirement.complete ? "font-semibold text-green-700" : "text-gray-400"}
            >
              {requirement.complete ? "✓" : "○"}
            </span>
            <span className={requirement.complete ? "text-gray-700" : "text-gray-500"}>
              {requirement.label}
            </span>
          </div>
        ))}
      </div>

      {treatment.status === "borrador" && completed < 10 && (
        <p className="mt-5 border-t border-gray-100 pt-4 text-sm text-gray-500">
          Aún faltan datos antes de poder activar esta actividad.
        </p>
      )}

      <p className="mt-2 text-xs text-gray-400">
        Este avance indica la preparación del registro para su activación; no representa un
        porcentaje de cumplimiento legal.
      </p>
    </section>
  );
}
