"""Contrato aislado de la tarea selector de organización activa."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

WORKSPACE = Path("/workspace")
if not WORKSPACE.is_dir():
    pytest.skip("solo se ejecuta dentro del verifier aislado", allow_module_level=True)

HELPER = WORKSPACE / "frontend/lib/active-organization.ts"
PAGES = (
    WORKSPACE / "frontend/app/dashboard/organizacion/page.tsx",
    WORKSPACE / "frontend/app/dashboard/autodiagnostico/page.tsx",
)


def _text(path: Path) -> str:
    assert path.is_file(), f"falta {path.relative_to(WORKSPACE)}"
    return path.read_text(encoding="utf-8")


def test_helper_valida_la_membresia_y_hace_fallback_seguro():
    text = _text(HELPER)
    assert re.search(r"export\s+(?:function|const)\s+selectActiveOrganization", text)
    assert ".find(" in text
    assert "organization" in text
    assert re.search(r"organizaciones\s*\[\s*0\s*\]", text)


@pytest.mark.parametrize("page", PAGES)
def test_paginas_usan_el_helper_y_el_parametro_de_url(page: Path):
    text = _text(page)
    assert "searchParams" in text
    assert "organization" in text
    assert "selectActiveOrganization" in text


@pytest.mark.parametrize("page", PAGES)
def test_paginas_no_seleccionan_directamente_la_primera_membresia(page: Path):
    text = _text(page)
    assert "organizaciones[0]" not in text


def test_selector_accesible_actualiza_el_parametro_organization():
    components = list((WORKSPACE / "frontend/components").rglob("*.tsx"))
    matching = [path for path in components if "organization" in _text(path).lower()]
    assert matching, "falta componente selector de organización"
    text = "\n".join(_text(path) for path in matching)
    assert "aria-label" in text or "<label" in text
    assert "useRouter" in text
    assert "organization" in text
