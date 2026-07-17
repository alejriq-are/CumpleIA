import { redirect } from "next/navigation";

// La raíz redirige al dashboard; el middleware maneja usuarios no autenticados.
export default function RootPage() {
  redirect("/dashboard");
}
