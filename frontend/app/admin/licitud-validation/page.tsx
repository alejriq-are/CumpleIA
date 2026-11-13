"use client";

import { EipdReviewConsultation } from "@/components/admin/EipdReviewConsultation";
import { eipdReviewApi } from "@/lib/api/eipd-review";
import { ApiError } from "@/lib/api/client";
import { createClient } from "@/lib/supabase/client";

async function sessionToken() {
  const { data, error } = await createClient().auth.getSession();
  if (error || !data.session) throw new ApiError(401, "Sesión no disponible");
  return data.session.access_token;
}

export default function LicitudValidationPage() {
  return (
    <EipdReviewConsultation
      loadPreparation={async (scope) =>
        eipdReviewApi.preparation({ ...scope, token: await sessionToken() })
      }
      loadEvent={async (scope, reviewId) =>
        eipdReviewApi.event({ ...scope, token: await sessionToken() }, reviewId)
      }
    />
  );
}
