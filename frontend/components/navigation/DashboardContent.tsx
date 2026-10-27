"use client";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

// The connected workspace supplies its own named main landmark.
// Other dashboard routes keep the existing main wrapper.
export function DashboardContent({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const Tag = pathname === "/dashboard/trabajo" ? "div" : "main";
  return <Tag className="dashboard-content mx-auto max-w-6xl px-6 py-8">{children}</Tag>;
}
