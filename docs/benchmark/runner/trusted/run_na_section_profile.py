#!/usr/bin/env python3
"""Perfil trusted para la ronda «Preguntas N/A por sección»."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import run_rat_default

TRUSTED_ROOT = Path(__file__).resolve().parent
PROFILE = "rat-na-section-v1"
VERIFIER_IMAGE = "cumpleia-rat-na-section-verifier:python-3.12.3"
TEST_FILE = TRUSTED_ROOT / "test_na_section_contract.py"
MAX_TEST_OUTPUT = 64 * 1024


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)


def _append_log(path: Path, content: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(content)
    path.chmod(0o600)


def _bounded_output(stdout: str, stderr: str) -> str:
    combined = f"{stdout}\n{stderr}".strip()
    encoded = combined.encode("utf-8", errors="replace")
    if len(encoded) <= MAX_TEST_OUTPUT:
        return combined
    return encoded[:MAX_TEST_OUTPUT].decode("utf-8", errors="replace") + "\n[TRUNCATED]"


def ensure_verifier_image() -> None:
    run_rat_default.command(
        [
            "docker",
            "build",
            "--pull",
            "--tag",
            VERIFIER_IMAGE,
            "--file",
            str(TRUSTED_ROOT / "Dockerfile.na-section-verifier"),
            str(TRUSTED_ROOT),
        ]
    )


def run_contract_tests(workspace: Path):
    return run_rat_default.command(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "--read-only",
            *run_rat_default.CONTAINER_SECURITY_ARGS,
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--mount",
            f"type=bind,src={workspace},dst=/workspace,readonly",
            "--mount",
            f"type=bind,src={TEST_FILE},dst=/opt/rat/test_na_section_contract.py,readonly",
            "--env",
            "HOME=/tmp",
            "--env",
            "SUPABASE_URL=http://invalid.local",
            "--workdir",
            "/workspace/backend",
            VERIFIER_IMAGE,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "/opt/rat/test_na_section_contract.py",
        ],
        check=False,
    )


def validate_candidate_scope(workspace: Path, baseline_commit: str) -> str | None:
    modified = run_rat_default.command(
        ["git", "-C", str(workspace), "diff", "--name-only", baseline_commit, "--"]
    ).stdout.splitlines()
    untracked = run_rat_default.command(
        [
            "git",
            "-C",
            str(workspace),
            "ls-files",
            "--others",
            "--exclude-standard",
        ]
    ).stdout.splitlines()
    paths = {path.strip() for path in modified + untracked if path.strip()}
    if not any(path.startswith("backend/tests/") for path in paths):
        return "candidate did not add or modify backend tests"
    if any(path.startswith("docs/benchmark/runner/") for path in paths):
        return "candidate modified protected benchmark runner assets"
    return None


def run_profile(run_id: str, workspace: Path, evidence: Path) -> int:
    base_code = run_rat_default.run_profile(run_id, workspace, evidence)
    report_path = evidence / "verification.json"
    log_path = evidence / "tests.log"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["profile"] = PROFILE

    if base_code != 0:
        _write_json(report_path, report)
        _append_log(log_path, "SKIP na_section_contract: rat-default did not pass\n")
        return base_code

    try:
        run_config = json.loads((evidence / "run.json").read_text(encoding="utf-8"))
        baseline_commit = run_config["baselineCommit"]
        ensure_verifier_image()
        result = run_contract_tests(workspace)
        output = _bounded_output(result.stdout, result.stderr)
        scope_failure = validate_candidate_scope(workspace, baseline_commit)
        if result.returncode == 0 and scope_failure is None:
            task_status = "PASS"
            report["status"] = "PASS"
            report["trustedChecksPassed"] = True
            report["error"] = None
            exit_code = 0
        elif 1 <= result.returncode <= 5:
            task_status = "FAIL"
            report["status"] = "FAIL"
            report["trustedChecksPassed"] = False
            report["error"] = None
            exit_code = 1
        else:
            task_status = "HARNESS_ERROR"
            report["status"] = "HARNESS_ERROR"
            report["trustedChecksPassed"] = False
            report["error"] = (
                f"task verifier container exited with code {result.returncode}"
            )
            exit_code = 2
        check: dict[str, Any] = {
            "name": "na_section_contract",
            "status": task_status,
        }
        if task_status != "PASS":
            messages = [
                message for message in (scope_failure, output[-4000:]) if message
            ]
            check["message"] = "\n".join(messages)
        report["checks"].append(check)
        _append_log(log_path, f"{task_status} na_section_contract\n{output}\n")
    except Exception as exc:
        exit_code = 2
        message = f"{type(exc).__name__}: {exc}"
        report["status"] = "HARNESS_ERROR"
        report["trustedChecksPassed"] = False
        report["error"] = message
        report["checks"].append(
            {"name": "na_section_contract", "status": "HARNESS_ERROR"}
        )
        _append_log(log_path, f"HARNESS_ERROR na_section_contract: {message}\n")

    report["finishedAt"] = datetime.now(UTC).isoformat()
    _write_json(report_path, report)
    return exit_code
