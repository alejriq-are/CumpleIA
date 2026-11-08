import { consentQuestions } from "./LegalBasisForms";
import { documentDisclosureClass } from "./document-focus";
import type { BaseMaterial, Requirement } from "./BaseFundamentoVersionTypes";

const messages: Record<string, string> = {
  base_pendiente: "La base de licitud está pendiente de definir.",
  fundamento_ausente: "Falta documentar el fundamento.",
  pregunta_omitida: "Falta responder esta pregunta.",
  respuesta_pendiente: "La respuesta está pendiente.",
  campo_obligatorio: "Falta completar este dato.",
  aplicabilidad_sin_resolver: "Falta determinar si este requisito aplica al tratamiento.",
  respuesta_no_aplicable:
    "La pregunta no aplica y conserva una respuesta incompatible. Selecciona No aplica o Sin responder en el borrador y guarda. La justificación se registra durante la revisión.",
  referencia_de_respaldo_ausente: "Falta una referencia que permita comprobar el respaldo.",
  evidencia_ausente: "Falta un respaldo documental.",
  evidencia_incompleta: "El respaldo registrado tiene datos incompletos.",
  tipo_evidencia_vacio: "Falta identificar el tipo de respaldo.",
  diagnostico_no_habilitado:
    "El diagnóstico conservado no se pudo verificar con las reglas del piloto.",
};

export function requirementTitle(item: Requirement, material: BaseMaterial) {
  const question = consentQuestions.find(([key]) => item.field === `answers.${key}`);
  return (
    question?.[1] ??
    material.diagnostic.criteria.find((c) => c.id === item.criterion_id)?.label ??
    "Requisito por aclarar"
  );
}

export function BaseFundamentoRequirements({
  requirements,
  material,
}: {
  requirements: Requirement[];
  material: BaseMaterial;
}) {
  const unresolved = (r: Requirement) =>
    !r.criterion_id || r.code === "aplicabilidad_sin_resolver" || r.code === "aplicabilidad";
  const incompatibleAnswers = new Set(
    requirements.filter((r) => r.code === "respuesta_no_aplicable").map((r) => r.field)
  );
  const groups = [
    {
      title: "Requisitos esenciales que bloquean Favorable",
      help: "Completa o corrige el borrador y registra una nueva versión antes de solicitar una revisión Favorable.",
      items: requirements.filter((r) => !r.resolution && !unresolved(r)),
    },
    {
      title: "Información por aclarar",
      help: "Si falta información sobre el requisito o su aplicabilidad, corresponde Requiere cambios. Indica qué falta aclarar.",
      items: requirements.filter((r) => !r.resolution && unresolved(r)),
    },
    {
      title: "Requisitos que no aplican",
      help: "En la revisión, justifica por qué cada requisito no aplica a este tratamiento. Sin justificación queda pendiente.",
      items: requirements.filter(
        (r) => r.resolution === "no_aplica" && !incompatibleAnswers.has(r.field)
      ),
    },
    {
      title: "Requisitos que admiten respaldo equivalente",
      help: "En la revisión, indica qué hecho acredita el respaldo y dónde puede consultarse, por ejemplo, en un correo fechado o en una bitácora.",
      items: requirements.filter((r) => r.resolution === "respaldo_equivalente"),
    },
  ];
  return (
    <div className="space-y-3">
      {!requirements.length && <p>No hay requisitos pendientes de resolver para Favorable.</p>}
      {groups
        .filter((group) => group.items.length)
        .map((group) => (
          <section
            key={group.title}
            aria-label={group.title}
            className="space-y-1 rounded border bg-white p-3"
          >
            <h5 className="font-semibold">{group.title}</h5>
            <p>{group.help}</p>
            <ul className="list-disc space-y-1 pl-5">
              {group.items.map((r, index) => (
                <li key={index}>
                  <strong>{requirementTitle(r, material)}</strong>
                  {r.resolution !== "no_aplica" &&
                    ` · ${messages[r.code] ?? "Revisa este punto en el contenido conservado."}`}
                </li>
              ))}
            </ul>
          </section>
        ))}
      <p>
        <strong>Observaciones de seguimiento.</strong> Si queda un pendiente menor que no cambia la
        conclusión, puedes registrar una observación con responsable y plazo.
      </p>
      {requirements.length > 0 && (
        <details>
          <summary className={documentDisclosureClass}>
            Ver detalle técnico de los requisitos
          </summary>
          <ul className="list-disc break-words pl-5">
            {requirements.map((r, index) => (
              <li key={index}>
                {r.field} · {r.code}
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
