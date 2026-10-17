import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { SignOutButton } from "@/components/auth/SignOutButton";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b border-gray-200 bg-white px-6 py-4">
        <div className="mx-auto flex max-w-6xl flex-col items-start gap-3 sm:flex-row sm:items-center sm:justify-between">
          <span className="text-xl font-bold text-blue-800">CumpleIA</span>
          <div className="flex w-full min-w-0 flex-col items-start gap-2 sm:w-auto sm:flex-row sm:flex-wrap sm:items-center sm:gap-4">
            <Link
              href="/dashboard/organizacion"
              className="shrink-0 text-sm text-gray-500 hover:text-gray-700"
            >
              Mi organización
            </Link>
            <span className="min-w-0 max-w-full break-all text-sm text-gray-500">{user.email}</span>
            <SignOutButton />
          </div>
        </div>
      </nav>
      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  );
}
