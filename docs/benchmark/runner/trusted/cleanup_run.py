#!/usr/bin/env python3
"""Limpieza segura de workspace/runtime después del cierre de evidencia."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import verify_evidence

WORKSPACE_ROOT = Path("/home/cumplebench/benchmark-workspaces")
RUNTIME_ROOT = Path("/home/cumplebench/benchmark-runtime")
EVIDENCE_ROOT = Path("/home/cumplebench/benchmark-runs")


class CleanupError(RuntimeError):
    pass


def resolve_target(root: Path, run_id: str) -> Path:
    resolved_root = root.resolve(strict=True)
    target = root / run_id
    if not target.exists():
        return target
    if target.is_symlink():
        raise CleanupError(f"refusing symlink target: {target}")
    resolved = target.resolve(strict=True)
    if resolved.parent != resolved_root or resolved.name != run_id:
        raise CleanupError(f"target escaped expected root: {target}")
    return resolved


def cleanup(run_id: str, execute: bool) -> list[tuple[str, str]]:
    if not verify_evidence.NAME_RE.fullmatch(run_id):
        raise CleanupError("invalid runId")
    evidence = EVIDENCE_ROOT / run_id
    verify_evidence.validate_evidence(evidence)
    if execute:
        verify_evidence.lock_evidence(evidence)

    targets = [
        ("workspace", resolve_target(WORKSPACE_ROOT, run_id)),
        ("runtime", resolve_target(RUNTIME_ROOT, run_id)),
    ]
    result: list[tuple[str, str]] = []
    for label, target in targets:
        if not target.exists():
            result.append((label, "ABSENT"))
        elif not execute:
            result.append((label, "WOULD_DELETE"))
        else:
            shutil.rmtree(target)
            if target.exists():
                raise CleanupError(f"failed to remove {label}")
            result.append((label, "DELETED"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="delete workspace/runtime; omission performs a dry run",
    )
    args = parser.parse_args()
    try:
        for label, status in cleanup(args.run_id, args.execute):
            print(f"{label}={status}")
        evidence_status = "RETAINED_AND_LOCKED" if args.execute else "VALIDATED"
        print(f"evidence={evidence_status}")
        return 0
    except Exception as exc:
        print(f"cleanup=REFUSED error={type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
