import { createClient } from "@/lib/supabase/client";
import { ApiError } from "@/lib/api/client";

export const sessionRequiredMessage =
  "No hay una sesión válida disponible. Vuelve a iniciar sesión.";

export function requiresSignIn(error: unknown) {
  return error instanceof ApiError && error.status === 401;
}

export async function sessionToken() {
  const { data, error } = await createClient().auth.getSession();
  if (error) {
    if (error.status === 401 || error.name === "AuthSessionMissingError")
      throw new ApiError(401, sessionRequiredMessage);
    if (error.name === "AuthRetryableFetchError" && !error.status)
      throw new TypeError("Failed to fetch");
    throw new Error(
      "No se pudo comprobar la sesión. El servicio de acceso no está disponible; vuelve a intentar."
    );
  }
  if (!data.session) throw new ApiError(401, sessionRequiredMessage);
  return data.session.access_token;
}
