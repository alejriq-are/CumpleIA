import Link from "next/link";
import { LicitudFlowPrototype } from "@/components/licitud/LicitudFlowPrototype";

export const metadata = { title: "Maqueta de licitud | CumpleIA" };

export default function Page() {
  return (
    <div className="space-y-5">
      <Link href="/dashboard/licitud" className="text-blue-800 underline">
        Volver a Bases de licitud
      </Link>
      <LicitudFlowPrototype />
    </div>
  );
}
