import type { TreatmentDetailOut } from "@/lib/api/client";

export type TreatmentRequirement = {
  label: string;
  complete: boolean;
};

function declarationResolved(value: string | null) {
  return value === "si" || value === "no";
}

function internationalTransfersResolved(treatment: TreatmentDetailOut) {
  const declaration = treatment.international_transfers_declaration;

  if (declaration === "no") {
    return true;
  }

  if (declaration !== "si") {
    return false;
  }

  return (
    treatment.international_transfers.length > 0 &&
    treatment.international_transfers.every((transfer) => transfer.adequacy_status !== "pendiente")
  );
}

export function treatmentRequirements(treatment: TreatmentDetailOut): TreatmentRequirement[] {
  return [
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
      complete: internationalTransfersResolved(treatment),
    },
  ];
}

export function treatmentReadyForActivation(treatment: TreatmentDetailOut) {
  return treatmentRequirements(treatment).every((requirement) => requirement.complete);
}
