"use client";
import { useCallback } from "react";
import { ChildAdolescentEditor } from "./ChildAdolescentEditor";
import { childApi, type ChildDocument } from "@/lib/api/child-adolescent";
import { createClient } from "@/lib/supabase/client";
import { ApiError } from "@/lib/api/client";
export function ChildAdolescentPage({
  organizationId,
  treatmentId,
  assessmentId,
  readOnly,
}: {
  organizationId: string;
  treatmentId: string;
  assessmentId: string;
  readOnly: boolean;
}) {
  const scope = useCallback(async () => {
    const { data, error } = await createClient().auth.getSession();
    if (error || !data.session) throw new ApiError(401, "Sesión no disponible");
    return { organizationId, treatmentId, assessmentId, token: data.session.access_token };
  }, [organizationId, treatmentId, assessmentId]);
  const load = useCallback(async () => childApi.load(await scope()), [scope]);
  const save = useCallback(
    async (doc: ChildDocument | null) => childApi.save(await scope(), doc),
    [scope]
  );
  const readiness = useCallback(async () => childApi.readiness(await scope()), [scope]);
  return (
    <ChildAdolescentEditor
      key={`${organizationId}:${treatmentId}:${assessmentId}`}
      load={load}
      save={save}
      readiness={readiness}
      readOnly={readOnly}
    />
  );
}
