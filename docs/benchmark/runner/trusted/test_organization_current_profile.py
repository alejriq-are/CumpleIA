import subprocess
from pathlib import Path

import run_organization_current_profile


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def test_scope_requires_tests_and_protects_security_assets(tmp_path: Path):
    _git(tmp_path, "init")
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend/app.py").write_text("BASE = True\n")
    _git(tmp_path, "add", ".")
    _git(
        tmp_path,
        "-c",
        "user.name=RAT Test",
        "-c",
        "user.email=rat@example.invalid",
        "commit",
        "-m",
        "baseline",
    )
    baseline = _git(tmp_path, "rev-parse", "HEAD")

    (tmp_path / "backend/app.py").write_text("BASE = False\n")
    assert (
        run_organization_current_profile.validate_candidate_scope(tmp_path, baseline)
        == "candidate did not add or modify backend tests"
    )

    (tmp_path / "backend/tests").mkdir()
    (tmp_path / "backend/tests/test_feature.py").write_text("def test_ok(): pass\n")
    assert (
        run_organization_current_profile.validate_candidate_scope(tmp_path, baseline)
        is None
    )

    protected = tmp_path / "backend/alembic"
    protected.mkdir()
    (protected / "tamper.py").write_text("TAMPER = True\n")
    assert (
        "protected asset"
        in run_organization_current_profile.validate_candidate_scope(tmp_path, baseline)
    )
