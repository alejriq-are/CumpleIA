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
  rut: string | null;
  industry: string | null;
  size: string | null;
  role: string;
};

export type OrganizationCreate = {
  name: string;
  rut?: string;
  industry?: string;
  size?: string;
};

export type OrganizationUpdate = {
  name: string;
  rut?: string;
  industry?: string;
  size?: string;
};

export type OrganizationDetailOut = {
  id: string;
  name: string;
  rut: string | null;
  industry: string | null;
  size: string | null;
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

// Módulo 1 — Autodiagnóstico (Tareas 3-5). `answer` viaja como el mismo
// literal 'Sí'/'Parcial'/'No'/'N/A' que valida el backend (ver
// app/api/diagnostico.py::RespuestaAnswer).
export type OpcionRespuesta = "Sí" | "Parcial" | "No" | "N/A";

export type ObligacionCuestionarioOut = {
  id: string;
  numero_guia: string;
  nombre: string;
};

export type SeccionCuestionarioOut = {
  id: string;
  numero_romano: string;
  nombre: string;
  obligacion_id: string;
  orden: number;
};

export type PreguntaCuestionarioOut = {
  id: string;
  seccion_id: string;
  texto: string;
  orden: number;
};

export type CuestionarioOut = {
  opciones_respuesta: OpcionRespuesta[];
  obligaciones: ObligacionCuestionarioOut[];
  secciones: SeccionCuestionarioOut[];
  preguntas: PreguntaCuestionarioOut[];
};

export type RespuestaIn = {
  pregunta_id: string;
  answer: OpcionRespuesta;
  notes?: string;
};

export type RespuestaOut = {
  pregunta_id: string;
  answer: string | null;
  notes: string | null;
};

export type PuntajeSeccionOut = {
  seccion_id: string;
  numero_romano: string;
  nombre: string;
  score: number | null;
};

export type HallazgoOut = {
  id: string;
  pregunta_id: string | null;
  seccion_id: string | null;
  description: string;
  // `risk` es el riesgo ajustado (degradado si la respuesta fue 'Parcial');
  // `risk_base` es el riesgo del catálogo antes de esa degradación.
  risk: RiesgoDisplay;
  risk_base: RiesgoDisplay | null;
  answer: OpcionRespuesta | null;
  status: string;
  corrective_action: string | null;
  responsible: string | null;
};

export type CitaOut = {
  source: string;
  reference: string;
};

export type NarrativaHallazgoOut = {
  finding_id: string;
  narrativa: string;
  citas: CitaOut[];
};

export type InformeOut = {
  resumen_ejecutivo: string;
  narrativas: NarrativaHallazgoOut[];
  generado_en: string;
};

export type DiagnosticoActualOut = {
  id: string;
  status: "en_progreso" | "completado";
  global_score: number | null;
  puntaje_por_seccion: PuntajeSeccionOut[];
  respuestas: RespuestaOut[];
  hallazgos: HallazgoOut[];
  informe: InformeOut | null;
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

// Variante de apiFetch para GET /diagnostico/actual: la organización todavía
// sin diagnóstico no es un error de la UI, es el estado inicial esperado —
// se resuelve a `null` en vez de forzar a cada pantalla a parsear el 404.
async function apiFetchOrNull<T>(path: string, opts: FetchOptions): Promise<T | null> {
  const { token, organizationId } = opts;

  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(organizationId ? { "X-Organization-Id": organizationId } : {}),
    },
  });

  if (res.status === 404) return null;

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((detail as { detail?: string })?.detail ?? `Error ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// GET /diagnostico/informe/exportar devuelve HTML descargable, no JSON —
// apiFetch no aplica (asume siempre `res.json()`).
async function fetchBlob(
  path: string,
  { token, organizationId }: { token: string; organizationId: string }
): Promise<Blob> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "X-Organization-Id": organizationId,
    },
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((detail as { detail?: string })?.detail ?? `Error ${res.status}`);
  }

  return res.blob();
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

    // Edita nombre/RUT/rubro/tamaño — requiere Permission.manage_organization.
    update: (
      token: string,
      organizationId: string,
      body: OrganizationUpdate
    ): Promise<OrganizationDetailOut> =>
      apiFetch<OrganizationDetailOut>("/organizations", {
        token,
        organizationId,
        method: "PATCH",
        body,
      }),
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

  // Módulo 1 — Autodiagnóstico (Tareas 3-5). Todos requieren X-Organization-Id.
  diagnostico: {
    cuestionario: (token: string, organizationId: string): Promise<CuestionarioOut> =>
      apiFetch<CuestionarioOut>("/diagnostico/cuestionario", { token, organizationId }),

    guardarRespuestas: (
      token: string,
      organizationId: string,
      respuestas: RespuestaIn[]
    ): Promise<DiagnosticoActualOut> =>
      apiFetch<DiagnosticoActualOut>("/diagnostico/respuestas", {
        token,
        organizationId,
        method: "POST",
        body: { respuestas },
      }),

    // null si la organización todavía no tiene un diagnóstico en curso
    // (404 del backend — ver apiFetchOrNull).
    actual: (token: string, organizationId: string): Promise<DiagnosticoActualOut | null> =>
      apiFetchOrNull<DiagnosticoActualOut>("/diagnostico/actual", { token, organizationId }),

    // 409 si el diagnóstico existe pero no está `completado` — el backend
    // ya valida esto, aquí solo se propaga el mensaje via apiFetch.
    generarInforme: (token: string, organizationId: string): Promise<DiagnosticoActualOut> =>
      apiFetch<DiagnosticoActualOut>("/diagnostico/informe", {
        token,
        organizationId,
        method: "POST",
      }),

    // HTML autocontenido (Tarea 5) — el componente que llama esto arma el
    // Blob URL y dispara la descarga en el navegador.
    exportarInforme: (token: string, organizationId: string): Promise<Blob> =>
      fetchBlob("/diagnostico/informe/exportar", { token, organizationId }),
  },
};
