import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CumpleIA",
  description:
    "Adecuación a la Ley N° 21.719 de Protección de Datos Personales (Chile)",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="bg-gray-50 text-gray-900 antialiased">{children}</body>
    </html>
  );
}
