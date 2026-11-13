"""Hashes sucesores; no renuevan la asociacion de investigacion aportada."""

import hashlib
import json

from app.schemas.research import BoundResearchAssessmentV1
from app.services.research_binding import validated


def build_research_transversal_hash(
    domain, version, previous_context_hash, research, **material
):
    document = (
        validated(BoundResearchAssessmentV1, research) if research is not None else None
    )
    envelope = {
        "domain": domain,
        "version": version,
        "material": {
            "previous_context_hash": previous_context_hash,
            "research_assessment": (
                document.model_dump(mode="json") if document else None
            ),
            **material,
        },
    }
    return hashlib.sha256(
        json.dumps(
            envelope,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
