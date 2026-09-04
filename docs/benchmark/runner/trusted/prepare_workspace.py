#!/usr/bin/env python3

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

TRUSTED_ROOT = Path(__file__).resolve().parent
CANONICAL_REPO = TRUSTED_ROOT.parents[3]
WORKSPACE_ROOT = Path("/home/cumplebench/benchmark-workspaces")
RUNTIME_ROOT = Path("/home/cumplebench/benchmark-runtime")
EVIDENCE_ROOT = Path("/home/cumplebench/benchmark-runs")

BASE_SRT_POLICY = Path("/etc/cumpleia-benchmark/srt-prefinal.json")

RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def validate_run_id(run_id: str) -> str:
    if not RUN_ID_RE.fullmatch(run_id):
        raise ValueError("invalid runId")
    return run_id


def validate_baseline_commit(commit: str) -> str:
    if not COMMIT_RE.fullmatch(commit):
        raise ValueError("invalid baselineCommit")
    return commit


def validate_commit_exists(commit: str) -> str:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(CANONICAL_REPO),
            "cat-file",
            "-e",
            f"{commit}^{{commit}}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("baselineCommit does not exist as commit")
    return commit


def validate_preconditions(run_id: str) -> None:
    workspace = WORKSPACE_ROOT / run_id
    runtime = RUNTIME_ROOT / run_id
    evidence = EVIDENCE_ROOT / run_id

    if not CANONICAL_REPO.is_dir():
        raise RuntimeError(f"canonical repository missing: {CANONICAL_REPO}")

    if not BASE_SRT_POLICY.is_file():
        raise RuntimeError(f"base SRT policy missing: {BASE_SRT_POLICY}")

    for label, path in (
        ("workspace", workspace),
        ("runtime", runtime),
        ("evidence", evidence),
    ):
        if path.exists():
            raise RuntimeError(f"{label} already exists: {path}")


def prepare_workspace(run_id: str, baseline_commit: str) -> Path:
    workspace = WORKSPACE_ROOT / run_id

    if workspace.exists():
        raise RuntimeError(f"workspace already exists: {workspace}")

    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "git",
            "clone",
            "--no-hardlinks",
            "--no-checkout",
            str(CANONICAL_REPO),
            str(workspace),
        ],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(workspace),
            "checkout",
            "--detach",
            baseline_commit,
        ],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(workspace),
            "remote",
            "remove",
            "origin",
        ],
        check=True,
    )

    return workspace


def prepare_run_directories(run_id: str) -> tuple[Path, Path]:
    runtime = RUNTIME_ROOT / run_id
    evidence = EVIDENCE_ROOT / run_id

    if runtime.exists():
        raise RuntimeError(f"runtime already exists: {runtime}")

    if evidence.exists():
        raise RuntimeError(f"evidence already exists: {evidence}")

    runtime.mkdir(parents=True, mode=0o700)
    (runtime / "tmp").mkdir(mode=0o700)
    (runtime / "claude").mkdir(mode=0o700)

    evidence.mkdir(parents=True, mode=0o700)

    return runtime, evidence


def generate_srt_policy(
    workspace: Path,
    runtime: Path,
    evidence: Path,
) -> tuple[Path, str]:
    policy = json.loads(BASE_SRT_POLICY.read_text())

    allow_write = [
        str(workspace),
        str(runtime / "tmp"),
        str(runtime / "claude"),
    ]

    policy["filesystem"]["allowWrite"] = allow_write

    deny_read = set(policy["filesystem"].get("denyRead", []))
    deny_read.update((str(CANONICAL_REPO), str(EVIDENCE_ROOT)))
    policy["filesystem"]["denyRead"] = sorted(deny_read)

    deny_write = set(policy["filesystem"].get("denyWrite", []))
    deny_write.update((str(CANONICAL_REPO), str(EVIDENCE_ROOT)))
    policy["filesystem"]["denyWrite"] = sorted(deny_write)

    forbidden = {
        str(CANONICAL_REPO),
        str(evidence),
        str(EVIDENCE_ROOT),
    }

    if forbidden.intersection(allow_write):
        raise RuntimeError("trusted path present in SRT allowWrite")

    policy_path = evidence / "srt-settings.json"
    payload = json.dumps(policy, indent=2, sort_keys=True) + "\n"
    policy_path.write_text(payload)
    policy_path.chmod(0o600)

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return policy_path, digest


def verify_workspace(workspace: Path, baseline_commit: str) -> None:
    head = subprocess.run(
        ["git", "-C", str(workspace), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    if head != baseline_commit:
        raise RuntimeError(
            f"workspace HEAD mismatch: expected {baseline_commit}, got {head}"
        )

    status = subprocess.run(
        ["git", "-C", str(workspace), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    if status:
        raise RuntimeError("workspace is not clean")

    git_dir = workspace / ".git"
    if not git_dir.is_dir():
        raise RuntimeError("workspace .git is not an independent directory")

    remotes = subprocess.run(
        ["git", "-C", str(workspace), "remote"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    if remotes:
        raise RuntimeError(f"workspace has remotes: {remotes}")

    alternates = git_dir / "objects" / "info" / "alternates"
    if alternates.exists():
        raise RuntimeError("workspace uses Git object alternates")

    hardlinked = [
        path
        for path in (git_dir / "objects").rglob("*")
        if path.is_file() and path.stat().st_nlink > 1
    ]

    if hardlinked:
        raise RuntimeError(
            f"workspace contains {len(hardlinked)} hardlinked Git objects"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--baseline-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    run_id = validate_run_id(args.run_id)
    baseline_commit = validate_baseline_commit(args.baseline_commit)
    baseline_commit = validate_commit_exists(baseline_commit)

    validate_preconditions(run_id)

    workspace = prepare_workspace(run_id, baseline_commit)
    verify_workspace(workspace, baseline_commit)

    runtime, evidence = prepare_run_directories(run_id)

    policy_path, policy_sha256 = generate_srt_policy(
        workspace,
        runtime,
        evidence,
    )

    print(f"run_id={run_id}")
    print(f"baseline_commit={baseline_commit}")
    print(f"canonical={CANONICAL_REPO}")
    print(f"workspace={workspace}")
    print(f"runtime={runtime}")
    print(f"evidence={evidence}")
    print(f"base_srt_policy={BASE_SRT_POLICY}")
    print(f"srt_policy={policy_path}")
    print(f"srt_policy_sha256={policy_sha256}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
