import Link from "next/link";
import { NavigationPrototype } from "@/components/navigation/NavigationPrototype";
export const metadata = { title: "Maqueta integral de navegación | CumpleIA" };
export default function Page() {
  return (
    <div className="space-y-5">
      <Link
        href="/dashboard"
        className="inline-block rounded-lg border border-slate-300 bg-white px-4 py-2 font-semibold text-blue-800 hover:bg-blue-50"
      >
        ← Salir de la maqueta y volver al panel actual
      </Link>
      <NavigationPrototype />
    </div>
  );
}
