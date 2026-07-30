const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Tipos espejo de los schemas del backend
export type ProfileOut = {
  id: string;
  email: string;
  full_name: string | null;
  is_superadmin: boolean;
};

export type MembershipOut = {
  organization_id: string;
  role: string;
};

export type OrganizationOut = {
  id: string;
  name: string;
  role: string;
};

export type OrganizationMembershipOut = {
  id: string;
  name: string;
  role: string;
};

export type OrganizationCreate = {
  name: string;
  rut?: string;
  industry?: string;
  size?: string;
};

export type HealthOut = {
  status: string;
  database: string;
};

// Módulo 1 — configuración versionada del cuestionario de autodiagnóstico.
// El riesgo viaja como 'Alto'/'Medio'/'Bajo': el backend hace la conversión
// de/hacia el enum interno en minúscula (ver app/services/cuestionario_config.py).
export type RiesgoDisplay = "Alto" | "Medio" | "Bajo";

export type ObligacionOut = {
  id: string;
  numero_guia: string;
  nombre: string;
};

export type SeccionOut = {
  id: string;
  numero_romano: string;
  nombre: string;
  obligacion_id: string;
  orden: number;
  peso_pct: number;
};

export type PreguntaOut = {
  id: string;
  seccion_id: string;
  texto: string;
  orden: number;
  riesgo: RiesgoDisplay;
};

export type CreadoPorOut = {
  id: string;
  email: string;
  full_name: string | null;
};

export type ConfigVersionOut = {
  numero_version: number;
  activa: boolean;
  nota: string | null;
  creado_en: string;
  creado_por: CreadoPorOut;
};

export type ConfigCuestionarioOut = {
  version: ConfigVersionOut;
  obligaciones: ObligacionOut[];
  secciones: SeccionOut[];
  preguntas: PreguntaOut[];
};

export type GuardarConfigRequest = {
  nota?: string;
  pesos: { seccion_id: string; peso_pct: number }[];
  riesgos: { pregunta_id: string; riesgo: RiesgoDisplay }[];
};

type FetchOptions = {
  token: string;
  organizationId?: string;
  method?: string;
  body?: unknown;
};

async function apiFetch<T>(path: string, opts: FetchOptions): Promise<T> {
  const { token, organizationId, method = "GET", body } = opts;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  if (organizationId) {
    headers["X-Organization-Id"] = organizationId;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((detail as { detail?: string })?.detail ?? `Error ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  health: (): Promise<HealthOut> => fetch(`${API_URL}/health`).then((r) => r.json()),

  me: {
    get: (token: string): Promise<ProfileOut> => apiFetch<ProfileOut>("/me", { token }),

    membership: (token: string, organizationId: string): Promise<MembershipOut> =>
      apiFetch<MembershipOut>("/me/membership", { token, organizationId }),

    // Organizaciones del usuario con su rol; no requiere X-Organization-Id.
    // Lista vacía si aún no pertenece a ninguna. Útil para el onboarding.
    organizations: (token: string): Promise<OrganizationMembershipOut[]> =>
      apiFetch<OrganizationMembershipOut[]>("/me/organizations", { token }),
  },

  organizations: {
    // Onboarding: crea la organización y deja al usuario actual como owner.
    create: (token: string, body: OrganizationCreate): Promise<OrganizationOut> =>
      apiFetch<OrganizationOut>("/organizations", { token, method: "POST", body }),
  },

  // Config global (no tenant-scoped): no requiere X-Organization-Id.
  cuestionarioConfig: {
    get: (token: string): Promise<ConfigCuestionarioOut> =>
      apiFetch<ConfigCuestionarioOut>("/cuestionario-config", { token }),

    // Solo superadmin; el backend responde 403 para cualquier otro rol.
    save: (token: string, body: GuardarConfigRequest): Promise<ConfigCuestionarioOut> =>
      apiFetch<ConfigCuestionarioOut>("/cuestionario-config", {
        token,
        method: "POST",
        body,
      }),
  },
};
