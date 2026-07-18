const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Tipos espejo de los schemas del backend
export type ProfileOut = {
  id: string;
  email: string;
  full_name: string | null;
};

export type MembershipOut = {
  organization_id: string;
  role: string;
};

export type HealthOut = {
  status: string;
  database: string;
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
  },
};
