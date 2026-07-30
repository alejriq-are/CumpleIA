import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

// El JWT de Supabase incluye el claim `amr` (Authentication Methods Reference).
// Cuando la sesión se creó a través del link de recuperación de contraseña,
// contiene el método "recovery". Lo usamos para impedir que esa sesión temporal
// navegue por el resto de la app sin antes definir una nueva clave.
function isPasswordRecoverySession(accessToken?: string | null): boolean {
  if (!accessToken) return false;
  try {
    const payload = accessToken.split(".")[1];
    const decoded = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    const amr = decoded.amr as { method: string }[] | undefined;
    return amr?.some((entry) => entry.method === "recovery") ?? false;
  } catch {
    return false;
  }
}

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet: { name: string; value: string; options: CookieOptions }[]) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  // Refresca la sesión (importante para SSR con Supabase)
  const {
    data: { user },
  } = await supabase.auth.getUser();

  let isRecoverySession = false;
  if (user) {
    const {
      data: { session },
    } = await supabase.auth.getSession();
    isRecoverySession = isPasswordRecoverySession(session?.access_token);
  }

  const isProtectedPath =
    request.nextUrl.pathname.startsWith("/dashboard") ||
    request.nextUrl.pathname.startsWith("/admin");
  const isAuthPath = request.nextUrl.pathname.startsWith("/login");
  const isResetPasswordPath = request.nextUrl.pathname.startsWith("/reset-password");

  if (isProtectedPath && !user) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (isAuthPath && user && !isRecoverySession) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Sesión de recuperación activa: no se permite navegar a ninguna otra ruta
  // hasta que el usuario defina su nueva contraseña en /reset-password.
  if (isRecoverySession && !isResetPasswordPath) {
    return NextResponse.redirect(new URL("/reset-password", request.url));
  }

  return supabaseResponse;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
