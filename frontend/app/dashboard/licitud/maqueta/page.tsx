import Link from "next/link";
import { LicitudFlowPrototype } from "@/components/licitud/LicitudFlowPrototype";

export const metadata = { title: "Maqueta V3 de licitud | CumpleIA" };

export default function Page() {
  return (
    <div className="space-y-5">
      <Link href="/dashboard/licitud" className="text-blue-800 underline">
        Volver a Bases de licitud
      </Link>
      <aside className="rounded-xl border border-blue-200 bg-blue-50 p-4">
        <p className="font-semibold">
          Ya puedes probar la propuesta integral con Panel principal y menú lateral.
        </p>
        <Link
          href="/dashboard/maqueta"
          className="mt-3 inline-block rounded-lg bg-blue-800 px-4 py-2 font-semibold text-white"
        >
          Abrir nueva maqueta integral →
        </Link>
      </aside>
      <LicitudFlowPrototype />
    </div>
  );
}
