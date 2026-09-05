"""Perfil calibrado v2 para selector de organización activa."""
from pathlib import Path
import run_active_organization_selector_profile as base

PROFILE = "rat-active-organization-selector-v2"
TEST_FILE = Path(__file__).resolve().parent / "test_active_organization_selector_v2_contract.py"

def run_profile(run_id: str, workspace: Path, evidence: Path) -> int:
    original = base.PROFILE, base.TEST_FILE
    try:
        base.PROFILE, base.TEST_FILE = PROFILE, TEST_FILE
        return base.run_profile(run_id, workspace, evidence)
    finally:
        base.PROFILE, base.TEST_FILE = original
