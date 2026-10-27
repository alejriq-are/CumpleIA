import type { Applicability } from "@/lib/api/navigation";

export type AvailabilityReadState = { loading: boolean; error: string };

export function availabilityReason(
  saved: Applicability | undefined,
  read: AvailabilityReadState | undefined,
  topic: "eipd" | "infancia"
): string | null {
  if (!read || read.loading)
    return "Consultando la determinación guardada. La disponibilidad aún no está confirmada.";
  if (read.error)
    return "No se pudo consultar la disponibilidad. Reintenta la consulta en Determinar aplicabilidad; este error no significa que no corresponda.";
  if (!saved)
    return "No se dispone de una determinación consultada. Abre Determinar aplicabilidad para consultar.";
  if (saved.revision === 0)
    return "Todavía no hay una determinación guardada para esta evaluación.";
  if (!saved.current)
    return "La determinación guardada requiere revisar su asociación al alcance actual.";
  switch (saved[topic].state) {
    case "corresponde":
      return null;
    case "no_corresponde":
      return "La determinación guardada indica «No corresponde». El formulario no está habilitado.";
    case "informacion_insuficiente":
      return "La determinación guardada indica «Información insuficiente». Revisa los antecedentes antes de determinar si corresponde.";
    default:
      return "La determinación guardada está «Pendiente de analizar». Guarda «Corresponde» con su fundamento para habilitar este formulario.";
  }
}
