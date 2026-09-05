#!/usr/bin/env python3
"""Perfil trusted para la tarea selector de organización activa."""

from __future__ import annotations

import os
from pathlib import Path

import run_organization_current_profile as base
import run_rat_default

PROFILE = "rat-active-organization-selector-v1"
TRUSTED_ROOT = Path(__file__).resolve().parent
TEST_FILE = TRUSTED_ROOT / "test_active_organization_selector_contract.py"
PROTECTED_PREFIXES = ("docs/benchmark/runner/", "backend/alembic/", "backend/seed_data/")


def run_contract_tests(workspace: Path):
    return run_rat_default.command(
        [
            "docker", "run", "--rm", "--network", "none",
            "--user", f"{os.getuid()}:{os.getgid()}", "--read-only",
            *run_rat_default.CONTAINER_SECURITY_ARGS,
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
            "--mount", f"type=bind,src={workspace},dst=/workspace,readonly",
            "--mount", f"type=bind,src={TEST_FILE},dst=/opt/rat/test_active_organization_selector_contract.py,readonly",
            "--env", "HOME=/tmp", "--workdir", "/workspace",
            base.VERIFIER_IMAGE, "-m", "pytest", "-q", "-p", "no:cacheprovider",
            "/opt/rat/test_active_organization_selector_contract.py",
        ],
        check=False,
    )


def validate_candidate_scope(workspace: Path, baseline_commit: str) -> str | None:
    modified = run_rat_default.command(
        ["git", "-C", str(workspace), "diff", "--name-only", baseline_commit, "--"]
    ).stdout.splitlines()
    untracked = run_rat_default.command(
        ["git", "-C", str(workspace), "ls-files", "--others", "--exclude-standard"]
    ).stdout.splitlines()
    paths = {path.strip() for path in modified + untracked if path.strip()}
    if not any(path.startswith("frontend/") and ("test" in path or "spec" in path) for path in paths):
        return "candidate did not add or modify frontend tests"
    protected = next((path for path in paths if path.startswith(PROTECTED_PREFIXES)), None)
    return f"candidate modified protected asset: {protected}" if protected else None


def run_profile(run_id: str, workspace: Path, evidence: Path) -> int:
    original = (base.PROFILE, base.run_contract_tests, base.validate_candidate_scope)
    try:
        base.PROFILE = PROFILE
        base.run_contract_tests = run_contract_tests
        base.validate_candidate_scope = validate_candidate_scope
        return base.run_profile(run_id, workspace, evidence)
    finally:
        base.PROFILE, base.run_contract_tests, base.validate_candidate_scope = original
