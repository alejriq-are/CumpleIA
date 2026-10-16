"use client";
import { useCallback } from "react";
import { ChildEipdHistory } from "./ChildEipdHistory";
import {
  childEipdApi,
  type ChildResolution,
  type ResolutionDraft,
  type NegativeDecision,
} from "@/lib/api/child-eipd";
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
  const history = useCallback(async () => {
    const current = await scope();
    const [assessment, policy, resolutions] = await Promise.all([
      childApi.load(current),
      childEipdApi.policy(current),
      childEipdApi.list(current),
    ]);
    return { status: assessment.status, policy, resolutions };
  }, [scope]);
  const createResolution = useCallback(
    async (draft: ResolutionDraft) => childEipdApi.create(await scope(), draft),
    [scope]
  );
  const loadReviews = useCallback(
    async (resolution: ChildResolution) => childEipdApi.reviews(await scope(), resolution),
    [scope]
  );
  const createReview = useCallback(
    async (
      resolution: ChildResolution,
      decision: NegativeDecision,
      rationale: string,
      reference: string
    ) => childEipdApi.review(await scope(), resolution, decision, rationale, reference),
    [scope]
  );
  return (
    <div key={`${organizationId}:${treatmentId}:${assessmentId}`} className="space-y-6">
      <ChildAdolescentEditor
        key={`${organizationId}:${treatmentId}:${assessmentId}`}
        load={load}
        save={save}
        readiness={readiness}
        readOnly={readOnly}
      />
      <ChildEipdHistory
        load={history}
        create={createResolution}
        reviews={loadReviews}
        review={createReview}
        readOnly={readOnly}
      />
    </div>
  );
}
