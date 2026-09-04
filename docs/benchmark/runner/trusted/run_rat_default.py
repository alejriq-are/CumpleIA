#!/usr/bin/env python3
"""Reset efimero, migraciones y verificacion trusted del perfil rat-default."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from rat_default_common import FIXTURE_SHA256

TRUSTED_ROOT = Path(__file__).resolve().parent
CANONICAL_REPO = TRUSTED_ROOT.parents[3]
WORKSPACE_ROOT = Path("/home/cumplebench/benchmark-workspaces")
EVIDENCE_ROOT = Path("/home/cumplebench/benchmark-runs")
FIXTURE = (
    CANONICAL_REPO
    / "backend/seed_data/modulo1/cuestionario_autodiagnostico_config.json"
)
NETWORK = "cumpleia-benchmark-net"
RUNNER_IMAGE = "cumpleia-rat-runner:python-3.12.3"
POSTGRES_IMAGE = (
    "pgvector/pgvector@sha256:"
    "ccc6e83d6e35e931dc7c5def2022729d5a6c370318d099181995567ff1fb4d6b"
)
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
CONTAINER_SECURITY_ARGS = [
    "--cap-drop",
    "ALL",
    "--security-opt",
    "no-new-privileges",
    "--pids-limit",
    "128",
    "--memory",
    "256m",
]


class HarnessError(RuntimeError):
    pass


def command(
    args: list[str], *, check: bool = True, capture: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        text=True,
        capture_output=capture,
        check=False,
        timeout=300,
    )
    if check and result.returncode != 0:
        raise HarnessError(
            f"command failed with exit code {result.returncode}: {args[0]} {args[1]}"
        )
    return result


def validate_path(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    expected_root = root.resolve(strict=True)
    if resolved == expected_root or expected_root not in resolved.parents:
        raise HarnessError(f"{label} is outside its trusted root")
    return resolved


def ensure_network() -> None:
    inspect = command(["docker", "network", "inspect", NETWORK], check=False)
    if inspect.returncode != 0:
        command(["docker", "network", "create", "--internal", NETWORK])
        inspect = command(["docker", "network", "inspect", NETWORK])
    data = json.loads(inspect.stdout)
    if len(data) != 1 or data[0].get("Internal") is not True:
        raise HarnessError(f"Docker network {NETWORK} is not internal")


def ensure_runner_image() -> None:
    command(
        [
            "docker",
            "build",
            "--pull",
            "--tag",
            RUNNER_IMAGE,
            "--file",
            str(TRUSTED_ROOT / "Dockerfile.rat-default"),
            str(TRUSTED_ROOT),
        ]
    )
    version = command(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            *CONTAINER_SECURITY_ARGS,
            RUNNER_IMAGE,
            "--version",
        ]
    )
    if version.stdout.strip() != "Python 3.12.3":
        raise HarnessError("runner Python version is not 3.12.3")


def write_failure(evidence: Path, started: datetime, message: str) -> None:
    finished = datetime.now(UTC)
    report = {
        "schemaVersion": "1.0",
        "profile": "rat-default",
        "status": "HARNESS_ERROR",
        "trustedChecksPassed": False,
        "startedAt": started.isoformat(),
        "finishedAt": finished.isoformat(),
        "fixtureSha256": FIXTURE_SHA256,
        "checks": [],
        "error": message,
    }
    (evidence / "verification.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (evidence / "tests.log").write_text(f"HARNESS_ERROR {message}\n", encoding="utf-8")


def container_name(run_id: str) -> str:
    safe = re.sub(r"[^a-z0-9_.-]", "-", run_id.lower())
    return f"cumpleia-rat-pg-{safe}"[:63]


def run_profile(run_id: str, workspace: Path, evidence: Path) -> int:
    started = datetime.now(UTC)
    password = secrets.token_urlsafe(32)
    pg_name = container_name(run_id)
    dsn = f"postgresql://postgres:{password}@{pg_name}:5432/cumpleia_benchmark"
    database_url = dsn.replace("postgresql://", "postgresql+asyncpg://", 1)

    try:
        ensure_network()
        ensure_runner_image()
        command(
            [
                "docker",
                "run",
                "--detach",
                "--rm",
                "--name",
                pg_name,
                "--network",
                NETWORK,
                "--env",
                f"POSTGRES_PASSWORD={password}",
                "--env",
                "POSTGRES_DB=cumpleia_benchmark",
                "--health-cmd",
                "pg_isready -U postgres -d cumpleia_benchmark",
                "--health-interval",
                "1s",
                "--health-timeout",
                "3s",
                "--health-retries",
                "30",
                POSTGRES_IMAGE,
            ]
        )
        for _ in range(40):
            health = command(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", pg_name],
                check=False,
            )
            if health.stdout.strip() == "healthy":
                break
            time.sleep(1)
        else:
            raise HarnessError("ephemeral PostgreSQL did not become healthy")

        common = [
            "docker",
            "run",
            "--rm",
            "--network",
            NETWORK,
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "--read-only",
            *CONTAINER_SECURITY_ARGS,
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
        ]
        migration = common + [
            "--mount",
            f"type=bind,src={workspace / 'backend'},dst=/workspace/backend,readonly",
            "--env",
            f"DATABASE_URL={database_url}",
            "--env",
            "SUPABASE_URL=http://invalid.local",
            RUNNER_IMAGE,
            "-m",
            "alembic",
            "upgrade",
            "head",
        ]
        command(migration)

        trusted_mounts = [
            "--mount",
            f"type=bind,src={TRUSTED_ROOT},dst=/opt/rat/trusted,readonly",
            "--mount",
            f"type=bind,src={FIXTURE},dst=/opt/rat/fixture.json,readonly",
            "--env",
            f"RAT_TRUSTED_DATABASE_URL={dsn}",
        ]
        command(
            common
            + trusted_mounts
            + [
                RUNNER_IMAGE,
                "/opt/rat/trusted/load_rat_default_fixture.py",
                "--fixture",
                "/opt/rat/fixture.json",
            ]
        )

        verification = command(
            common
            + trusted_mounts
            + [
                "--mount",
                f"type=bind,src={evidence},dst=/evidence",
                RUNNER_IMAGE,
                "/opt/rat/trusted/verify_rat_default.py",
                "--fixture",
                "/opt/rat/fixture.json",
                "--output",
                "/evidence/verification.json",
                "--log",
                "/evidence/tests.log",
            ],
            check=False,
        )
        if verification.returncode not in {0, 1, 2}:
            raise HarnessError("trusted verifier terminated unexpectedly")
        return verification.returncode
    except Exception as exc:
        write_failure(evidence, started, f"{type(exc).__name__}: {exc}")
        return 2
    finally:
        password = ""
        command(["docker", "rm", "--force", pg_name], check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    if not RUN_ID_RE.fullmatch(args.run_id):
        raise SystemExit("invalid runId")
    try:
        workspace = validate_path(args.workspace, WORKSPACE_ROOT, "workspace")
        evidence = validate_path(args.evidence, EVIDENCE_ROOT, "evidence")
        if evidence.name != args.run_id or workspace.name != args.run_id:
            raise HarnessError("runId does not match workspace/evidence")
        if not (workspace / "backend/alembic.ini").is_file():
            raise HarnessError("candidate workspace has no backend/alembic.ini")
        return run_profile(args.run_id, workspace, evidence)
    except Exception as exc:
        print(f"HARNESS_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
