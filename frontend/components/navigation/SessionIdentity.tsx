"use client";
import type { ProfileOut } from "@/lib/api/client";

export type SessionPerson = Pick<ProfileOut, "id" | "email" | "full_name">;
const roleNames: Record<string, string> = {
  owner: "Propietario",
  admin: "Administrador",
  editor: "Editor",
  viewer: "Solo consulta",
};
/** Display only: permissions and review faculty continue to be checked by the server. */
export function SessionIdentity({
  person,
  role,
}: {
  person?: SessionPerson | null;
  role?: string;
}) {
  return (
    <section
      aria-label="Usuario de esta sesión"
      className="min-w-0 space-y-3 rounded border border-blue-200 bg-blue-50 p-4"
    >
      <h2 className="text-lg font-semibold">Usuario de esta sesión</h2>
      {!person ? (
        <p>No se ha podido consultar la identidad de esta sesión.</p>
      ) : (
        <>
          <dl className="space-y-2">
            {person.full_name?.trim() && (
              <div>
                <dt className="font-semibold">Nombre</dt>
                <dd className="break-words">{person.full_name}</dd>
              </div>
            )}
            <div>
              <dt className="font-semibold">Correo de acceso</dt>
              <dd className="break-all">{person.email}</dd>
            </div>
            <div>
              <dt className="font-semibold">Rol en esta organización</dt>
              <dd>{role ? (roleNames[role] ?? "Rol no identificado") : "Sin rol consultado"}</dd>
            </div>
          </dl>
          <details>
            <summary className="cursor-pointer py-2 font-semibold focus-visible:outline focus-visible:outline-2">
              Identificador de la persona
            </summary>
            <p className="break-all">{person.id}</p>
          </details>
        </>
      )}
    </section>
  );
}
