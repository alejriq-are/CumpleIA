#!/usr/bin/env python3
"""Valida integridad, coherencia y cierre de una evidencia de benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

EVIDENCE_ROOT = Path("/home/cumplebench/benchmark-runs")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
REQUIRED_FILES = {
    "agent.stderr.log",
    "agent.stdout.log",
    "baseline.json",
    "managed-settings.json",
    "manifest.sha256",
    "result.json",
    "run.json",
    "srt-settings.json",
    "task.md",
    "tests.log",
    "transport.json",
    "verification.json",
}
RUN_KEYS = {
    "schemaVersion",
    "runId",
    "candidateName",
    "baselineCommit",
    "taskFile",
    "transportConfig",
    "timeoutSeconds",
    "verificationProfile",
}
TRANSPORT_KEYS = {
    "candidateName",
    "backendClass",
    "provider",
    "endpoint",
    "modelId",
    "credentialEnv",
    "timeoutSeconds",
}
BASELINE_KEYS = {
    "baselineCommit",
    "taskFile",
    "taskSha256",
    "srtPolicySha256",
    "managedSettingsSha256",
}


class EvidenceError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"invalid JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise EvidenceError(f"JSON root is not an object: {path.name}")
    return value


def exact_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        raise EvidenceError(f"unexpected fields in {label}")


def parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise EvidenceError(f"invalid timestamp: {label}")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise EvidenceError(f"invalid timestamp: {label}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EvidenceError(f"timestamp lacks timezone: {label}")
    return parsed


def validate_root(evidence: Path) -> Path:
    if evidence.is_symlink():
        raise EvidenceError("evidence directory must not be a symlink")
    resolved = evidence.resolve(strict=True)
    root = EVIDENCE_ROOT.resolve(strict=True)
    if resolved == root or root not in resolved.parents:
        raise EvidenceError("evidence is outside the trusted root")
    if not NAME_RE.fullmatch(resolved.name):
        raise EvidenceError("invalid evidence runId")
    if resolved.stat().st_mode & 0o077:
        raise EvidenceError("evidence directory is accessible by group or others")
    return resolved


def validate_files(evidence: Path) -> dict[str, str]:
    entries = list(evidence.iterdir())
    if any(path.is_symlink() for path in entries):
        raise EvidenceError("evidence contains a symlink")
    if any(not path.is_file() for path in entries):
        raise EvidenceError("evidence contains a non-file entry")
    names = {path.name for path in entries}
    missing = REQUIRED_FILES - names
    if missing:
        raise EvidenceError(
            f"required evidence files missing: {', '.join(sorted(missing))}"
        )
    for path in entries:
        if path.stat().st_mode & 0o077:
            raise EvidenceError(
                f"evidence file is accessible by group or others: {path.name}"
            )

    lines = (evidence / "manifest.sha256").read_text(encoding="utf-8").splitlines()
    manifest: dict[str, str] = {}
    ordered_names: list[str] = []
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or not SHA256_RE.fullmatch(parts[0]):
            raise EvidenceError("malformed manifest entry")
        name = parts[1]
        if Path(name).name != name or name == "manifest.sha256" or name in manifest:
            raise EvidenceError("invalid or duplicate manifest filename")
        manifest[name] = parts[0]
        ordered_names.append(name)
    if ordered_names != sorted(ordered_names):
        raise EvidenceError("manifest entries are not sorted")
    actual_names = names - {"manifest.sha256"}
    if set(manifest) != actual_names:
        raise EvidenceError("manifest does not cover exactly all evidence files")
    for name, expected in manifest.items():
        if sha256_file(evidence / name) != expected:
            raise EvidenceError(f"SHA-256 mismatch: {name}")
    return manifest


def validate_result(result: dict[str, Any]) -> None:
    exact_keys(
        result,
        {
            "schemaVersion",
            "runId",
            "candidateName",
            "baselineCommit",
            "status",
            "agentExitCode",
            "timedOut",
            "trustedChecksPassed",
            "startedAt",
            "finishedAt",
            "durationSeconds",
        },
        "result.json",
    )
    if result["schemaVersion"] != "1.0":
        raise EvidenceError("unsupported result schemaVersion")
    if not isinstance(result["runId"], str) or not NAME_RE.fullmatch(result["runId"]):
        raise EvidenceError("invalid result runId")
    if not isinstance(result["candidateName"], str) or not NAME_RE.fullmatch(
        result["candidateName"]
    ):
        raise EvidenceError("invalid result candidateName")
    if not isinstance(result["baselineCommit"], str) or not COMMIT_RE.fullmatch(
        result["baselineCommit"]
    ):
        raise EvidenceError("invalid result baselineCommit")
    if result["status"] not in {"PASS", "FAIL", "TIMEOUT", "HARNESS_ERROR"}:
        raise EvidenceError("invalid result status")
    if result["agentExitCode"] is not None and (
        not isinstance(result["agentExitCode"], int)
        or isinstance(result["agentExitCode"], bool)
    ):
        raise EvidenceError("invalid agentExitCode")
    if not isinstance(result["timedOut"], bool):
        raise EvidenceError("invalid timedOut")
    if result["trustedChecksPassed"] is not None and not isinstance(
        result["trustedChecksPassed"], bool
    ):
        raise EvidenceError("invalid trustedChecksPassed")
    started = parse_timestamp(result["startedAt"], "startedAt")
    finished = parse_timestamp(result["finishedAt"], "finishedAt")
    duration = result["durationSeconds"]
    if (
        not isinstance(duration, (int, float))
        or isinstance(duration, bool)
        or duration < 0
    ):
        raise EvidenceError("invalid durationSeconds")
    if (
        finished < started
        or abs((finished - started).total_seconds() - duration) > 0.01
    ):
        raise EvidenceError("inconsistent result duration")

    status = result["status"]
    if status == "PASS" and not (
        result["agentExitCode"] == 0
        and result["timedOut"] is False
        and result["trustedChecksPassed"] is True
    ):
        raise EvidenceError("inconsistent PASS result")
    if status == "TIMEOUT" and result["timedOut"] is not True:
        raise EvidenceError("inconsistent TIMEOUT result")
    if status == "HARNESS_ERROR" and result["trustedChecksPassed"] is not None:
        raise EvidenceError("inconsistent HARNESS_ERROR result")
    if status == "FAIL" and (
        result["timedOut"] is not False
        or (result["agentExitCode"] == 0 and result["trustedChecksPassed"] is True)
    ):
        raise EvidenceError("inconsistent FAIL result")


def validate_semantics(evidence: Path) -> None:
    run = load_object(evidence / "run.json")
    transport = load_object(evidence / "transport.json")
    baseline = load_object(evidence / "baseline.json")
    result = load_object(evidence / "result.json")
    verification = load_object(evidence / "verification.json")
    srt_policy = load_object(evidence / "srt-settings.json")
    exact_keys(run, RUN_KEYS, "run.json")
    exact_keys(transport, TRANSPORT_KEYS, "transport.json")
    exact_keys(baseline, BASELINE_KEYS, "baseline.json")
    validate_result(result)

    if result["runId"] != evidence.name:
        raise EvidenceError("directory name does not match result runId")
    for key in ("runId", "candidateName", "baselineCommit"):
        if run.get(key) != result[key]:
            raise EvidenceError(f"run/result mismatch: {key}")
    if transport.get("candidateName") != result["candidateName"]:
        raise EvidenceError("transport/result candidateName mismatch")
    if baseline.get("baselineCommit") != result["baselineCommit"]:
        raise EvidenceError("baseline/result commit mismatch")
    if baseline.get("taskFile") != run.get("taskFile"):
        raise EvidenceError("baseline/run taskFile mismatch")
    if not (evidence / "task.md").read_text(encoding="utf-8").strip():
        raise EvidenceError("task.md is empty")

    hashes = {
        "taskSha256": "task.md",
        "srtPolicySha256": "srt-settings.json",
        "managedSettingsSha256": "managed-settings.json",
    }
    for field, filename in hashes.items():
        expected = baseline.get(field)
        if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
            raise EvidenceError(f"invalid baseline hash: {field}")
        if sha256_file(evidence / filename) != expected:
            raise EvidenceError(f"baseline hash mismatch: {filename}")

    if verification.get("profile") != run.get("verificationProfile"):
        raise EvidenceError("verification profile mismatch")
    verification_passed = (
        verification.get("status") == "PASS"
        and verification.get("trustedChecksPassed") is True
    )
    if result["status"] != "HARNESS_ERROR" and (
        result["trustedChecksPassed"] is not verification_passed
    ):
        raise EvidenceError("result/verification status mismatch")

    filesystem = srt_policy.get("filesystem")
    if not isinstance(filesystem, dict):
        raise EvidenceError("SRT policy has no filesystem object")
    deny_read = filesystem.get("denyRead")
    deny_write = filesystem.get("denyWrite")
    allow_write = filesystem.get("allowWrite")
    canonical = str(Path(__file__).resolve().parent.parents[3])
    evidence_root = str(EVIDENCE_ROOT)
    if not isinstance(deny_read, list) or not {canonical, evidence_root}.issubset(
        set(deny_read)
    ):
        raise EvidenceError("SRT denyRead lacks trusted roots")
    if not isinstance(deny_write, list) or not {canonical, evidence_root}.issubset(
        set(deny_write)
    ):
        raise EvidenceError("SRT denyWrite lacks trusted roots")
    if not isinstance(allow_write, list) or {canonical, evidence_root}.intersection(
        allow_write
    ):
        raise EvidenceError("SRT allowWrite contains a trusted root")


def validate_evidence(evidence: Path) -> Path:
    resolved = validate_root(evidence)
    validate_files(resolved)
    validate_semantics(resolved)
    return resolved


def lock_evidence(evidence: Path) -> None:
    resolved = validate_evidence(evidence)
    for path in resolved.iterdir():
        path.chmod(0o400)
    resolved.chmod(0o500)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--lock", action="store_true")
    args = parser.parse_args()
    try:
        resolved = validate_evidence(args.evidence)
        if args.lock:
            lock_evidence(resolved)
        print(f"evidence={resolved}")
        print("status=PASS")
        return 0
    except Exception as exc:
        print(f"status=FAIL error={type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
