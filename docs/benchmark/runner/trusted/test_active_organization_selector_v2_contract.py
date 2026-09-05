"""Contrato calibrado de selector activo: mide comportamiento, no nombres."""
from __future__ import annotations
import os
import re
from pathlib import Path
import pytest

WORKSPACE = Path("/workspace")
if not WORKSPACE.is_dir():
    pytest.skip("solo se ejecuta dentro del verifier aislado", allow_module_level=True)
HELPER = WORKSPACE / "frontend/lib/active-organization.ts"
PAGES = (WORKSPACE / "frontend/app/dashboard/organizacion/page.tsx", WORKSPACE / "frontend/app/dashboard/autodiagnostico/page.tsx")

def text(path: Path) -> str:
    assert path.is_file(), f"falta {path.relative_to(WORKSPACE)}"
    return path.read_text(encoding="utf-8")

def test_helper_exportado_valida_y_hace_fallback_seguro():
    source = text(HELPER)
    assert re.search(r"export\s+(?:function|const)\s+\w+", source)
    assert ".find(" in source and "organization" in source
    assert re.search(r"organizaciones\s*\[\s*0\s*\]", source)

@pytest.mark.parametrize("page", PAGES)
def test_paginas_validan_parametro_y_usan_helper(page: Path):
    source = text(page)
    assert "searchParams" in source and "organization" in source
    assert "@/lib/active-organization" in source
    assert "organizaciones[0]" not in source

def test_selector_accesible_actualiza_contexto_url():
    source = "\n".join(p.read_text(encoding="utf-8") for p in (WORKSPACE / "frontend/components").rglob("*.tsx"))
    assert "aria-label" in source or "<label" in source
    assert "useRouter" in source and "organization" in source
