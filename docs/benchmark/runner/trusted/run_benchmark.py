#!/usr/bin/env python3
"""Ciclo completo y autoritativo de una corrida del benchmark RAT."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import prepare_workspace
import run_active_organization_selector_profile
import run_na_section_profile
import run_organization_current_profile
import run_rat_default
import verify_evidence

TRUSTED_ROOT = Path(__file__).resolve().parent
CANONICAL_REPO = TRUSTED_ROOT.parents[3]
MANAGED_SETTINGS = CANONICAL_REPO / "docs/benchmark/runner/managed-settings.json"
SYSTEM_MANAGED_SETTINGS = Path("/etc/claude-code/managed-settings.json")
SRT_BIN = Path("/home/cumplebench/.nvm/versions/node/v20.20.2/bin/srt")
CLAUDE_BIN = Path("/home/cumplebench/.local/bin/claude")
MAX_LOG_BYTES = 16 * 1024 * 1024
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
TRANSPORT_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
ENV_NAME_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")


class HarnessError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


def validate_local_transport_preflight(transport: dict[str, Any]) -> None:
    endpoint = urlsplit(transport["endpoint"])
    host = endpoint.hostname
    expected_address = "127.77.18.1"

    if not host:
        raise HarnessError("local transport endpoint has no hostname")

    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(
                host,
                None,
                type=socket.SOCK_STREAM,
            )
        }
    except socket.gaierror as exc:
        raise HarnessError("local transport hostname resolution failed") from exc

    if addresses != {expected_address}:
        raise HarnessError(
            "local transport hostname does not resolve exclusively "
            f"to {expected_address}"
        )

    try:
        result = subprocess.run(
            ["ss", "-ltnH"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise HarnessError("unable to inspect local TCP listeners") from exc

    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 4:
            continue

        local_address = fields[3]
        if local_address.startswith("0.0.0.0:") or local_address.startswith("[::]:"):
            raise HarnessError(f"wildcard listener detected: {local_address}")


def validate_transport_preflight(transport: dict[str, Any]) -> None:
    if transport["backendClass"] == "local":
        validate_local_transport_preflight(transport)


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(0o600)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write(path, (json.dumps(data, indent=2, sort_keys=True) + "\n").encode())


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HarnessError(f"invalid {label}") from exc
    if not isinstance(data, dict):
        raise HarnessError(f"{label} must be a JSON object")
    return data


def require_exact_keys(data: dict[str, Any], required: set[str], label: str) -> None:
    if set(data) != required:
        raise HarnessError(f"{label} fields do not match its schema")


def resolve_repo_file(relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise HarnessError(f"invalid {label}")
    path = (CANONICAL_REPO / relative).resolve(strict=True)
    root = CANONICAL_REPO.resolve(strict=True)
    if root not in path.parents or not path.is_file():
        raise HarnessError(f"{label} is outside the canonical repository")
    return path


def validate_run_config(data: dict[str, Any]) -> dict[str, Any]:
    require_exact_keys(
        data,
        {
            "schemaVersion",
            "runId",
            "candidateName",
            "baselineCommit",
            "taskFile",
            "transportConfig",
            "timeoutSeconds",
            "verificationProfile",
        },
        "run config",
    )
    if data["schemaVersion"] != "1.0":
        raise HarnessError("unsupported run config schemaVersion")
    if not isinstance(data["runId"], str) or not NAME_RE.fullmatch(data["runId"]):
        raise HarnessError("invalid runId")
    if not isinstance(data["candidateName"], str) or not NAME_RE.fullmatch(
        data["candidateName"]
    ):
        raise HarnessError("invalid candidateName")
    try:
        prepare_workspace.validate_baseline_commit(data["baselineCommit"])
        prepare_workspace.validate_commit_exists(data["baselineCommit"])
    except (TypeError, ValueError) as exc:
        raise HarnessError("invalid baselineCommit") from exc
    if (
        not isinstance(data["timeoutSeconds"], int)
        or not 1 <= data["timeoutSeconds"] <= 86400
    ):
        raise HarnessError("invalid timeoutSeconds")
    if data["verificationProfile"] not in {
        "rat-default",
        run_na_section_profile.PROFILE,
        run_organization_current_profile.PROFILE,
        run_active_organization_selector_profile.PROFILE,
    }:
        raise HarnessError("unsupported verificationProfile")
    resolve_repo_file(data["taskFile"], "taskFile")
    resolve_repo_file(data["transportConfig"], "transportConfig")
    return data


def validate_transport(data: dict[str, Any], candidate_name: str) -> dict[str, Any]:
    require_exact_keys(
        data,
        {
            "candidateName",
            "backendClass",
            "provider",
            "endpoint",
            "modelId",
            "credentialEnv",
            "timeoutSeconds",
        },
        "transport config",
    )
    for field in ("candidateName", "provider"):
        if not isinstance(data[field], str) or not TRANSPORT_NAME_RE.fullmatch(
            data[field]
        ):
            raise HarnessError(f"invalid transport {field}")
    if data["candidateName"] != candidate_name:
        raise HarnessError("candidateName mismatch between run and transport")
    if data["backendClass"] not in {"cloud", "local"}:
        raise HarnessError("invalid backendClass")
    if not isinstance(data["endpoint"], str):
        raise HarnessError("invalid transport endpoint")
    endpoint = urlsplit(data["endpoint"])
    if (
        endpoint.scheme not in {"http", "https"}
        or not endpoint.hostname
        or endpoint.username is not None
        or endpoint.password is not None
        or endpoint.query
        or endpoint.fragment
    ):
        raise HarnessError("invalid transport endpoint")
    if data["backendClass"] == "cloud" and endpoint.scheme != "https":
        raise HarnessError("cloud transport endpoint must use HTTPS")
    if not isinstance(data["modelId"], str) or not data["modelId"]:
        raise HarnessError("invalid modelId")
    credential_env = data["credentialEnv"]
    if credential_env is not None and (
        not isinstance(credential_env, str) or not ENV_NAME_RE.fullmatch(credential_env)
    ):
        raise HarnessError("invalid credentialEnv")
    if data["backendClass"] == "cloud" and credential_env is None:
        raise HarnessError("cloud transport requires credentialEnv")
    if (
        not isinstance(data["timeoutSeconds"], int)
        or not 1 <= data["timeoutSeconds"] <= 3600
    ):
        raise HarnessError("invalid transport timeoutSeconds")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_environment(
    transport: dict[str, Any], runtime: Path
) -> tuple[dict[str, str], str]:
    credential_name = transport["credentialEnv"]
    if credential_name is None:
        credential = "local-transport-no-secret"
    else:
        credential = os.environ.get(credential_name, "")
        if not credential:
            raise HarnessError(
                f"required credential environment is not set: {credential_name}"
            )

    runtime_tmp = prepare_workspace.runtime_tmp_path(runtime.name)
    environment = {
        "PATH": (
            "/home/cumplebench/.nvm/versions/node/v20.20.2/bin:"
            "/home/cumplebench/.local/bin:/usr/local/bin:/usr/bin:/bin"
        ),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "HOME": str(runtime / "claude"),
        "TMPDIR": str(runtime_tmp),
        "CLAUDE_CONFIG_DIR": str(runtime / "claude"),
        "CLAUDE_CODE_TMPDIR": str(runtime_tmp),
        "DISABLE_UPDATES": "1",
        "CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS": "1",
        "ANTHROPIC_BASE_URL": transport["endpoint"],
        "ANTHROPIC_AUTH_TOKEN": credential,
        "ANTHROPIC_MODEL": transport["modelId"],
        "ANTHROPIC_DEFAULT_SONNET_MODEL": transport["modelId"],
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": transport["modelId"],
    }
    if transport["backendClass"] == "local":
        environment["CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT"] = "1"
    return environment, credential


def redact_and_write(
    path: Path, content: bytes, credential: str, truncated: bool = False
) -> None:
    if truncated:
        content += b"\n[TRUNCATED BY TRUSTED HARNESS]\n"
    text = content.decode("utf-8", errors="replace")
    if credential:
        text = text.replace(credential, "[REDACTED]")
    atomic_write(path, text.encode("utf-8"))


def run_candidate(
    prompt: str,
    workspace: Path,
    runtime: Path,
    evidence: Path,
    policy_path: Path,
    transport: dict[str, Any],
    timeout_seconds: int,
    claude_bin: Path,
) -> tuple[int | None, bool]:
    if not SRT_BIN.is_file() or not os.access(SRT_BIN, os.X_OK):
        raise HarnessError("SRT executable is unavailable")
    if not claude_bin.is_file() or not os.access(claude_bin, os.X_OK):
        raise HarnessError("candidate executable is unavailable")
    environment, credential = candidate_environment(transport, runtime)
    command = [
        str(SRT_BIN),
        f"--settings={policy_path}",
        "--",
        str(claude_bin),
        "--print",
        prompt,
        "--permission-mode",
        "dontAsk",
        "--no-session-persistence",
        "--no-chrome",
        "--disable-slash-commands",
    ]
    timed_out = False
    exit_code: int | None = None
    stdout_buffer = bytearray()
    stderr_buffer = bytearray()
    stdout_truncated = False
    stderr_truncated = False

    def drain(stream: Any, buffer: bytearray, stream_name: str) -> None:
        nonlocal stdout_truncated, stderr_truncated
        while chunk := stream.read(65536):
            remaining = MAX_LOG_BYTES - len(buffer)
            if remaining > 0:
                buffer.extend(chunk[:remaining])
            if len(chunk) > remaining:
                if stream_name == "stdout":
                    stdout_truncated = True
                else:
                    stderr_truncated = True

    try:
        process = subprocess.Popen(
            command,
            cwd=workspace,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        stdout_thread = threading.Thread(
            target=drain,
            args=(process.stdout, stdout_buffer, "stdout"),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=drain,
            args=(process.stderr, stderr_buffer, "stderr"),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()
        try:
            process.wait(timeout=min(timeout_seconds, transport["timeoutSeconds"]))
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        stdout_thread.join(timeout=5)
        stderr_thread.join(timeout=5)
        if stdout_thread.is_alive() or stderr_thread.is_alive():
            raise HarnessError("candidate log pipes did not close")
    finally:
        redact_and_write(
            evidence / "agent.stdout.log",
            bytes(stdout_buffer),
            credential,
            stdout_truncated,
        )
        redact_and_write(
            evidence / "agent.stderr.log",
            bytes(stderr_buffer),
            credential,
            stderr_truncated,
        )
        credential = ""
    return exit_code, timed_out


def derive_status(
    agent_exit_code: int | None, timed_out: bool, verifier_code: int
) -> tuple[str, bool | None]:
    if verifier_code == 2:
        return "HARNESS_ERROR", None
    checks_passed = verifier_code == 0
    if timed_out:
        return "TIMEOUT", checks_passed
    if agent_exit_code != 0 or not checks_passed:
        return "FAIL", checks_passed
    return "PASS", True


def write_manifest(evidence: Path) -> None:
    entries: list[str] = []
    for path in sorted(evidence.iterdir(), key=lambda item: item.name):
        if path.name == "manifest.sha256" or not path.is_file():
            continue
        entries.append(f"{sha256_file(path)}  {path.name}")
    atomic_write(evidence / "manifest.sha256", ("\n".join(entries) + "\n").encode())


def write_result(
    evidence: Path,
    config: dict[str, Any],
    status: str,
    agent_exit_code: int | None,
    timed_out: bool,
    trusted_checks_passed: bool | None,
    started: datetime,
) -> None:
    finished = utc_now()
    write_json(
        evidence / "result.json",
        {
            "schemaVersion": "1.0",
            "runId": config["runId"],
            "candidateName": config["candidateName"],
            "baselineCommit": config["baselineCommit"],
            "status": status,
            "agentExitCode": agent_exit_code,
            "timedOut": timed_out,
            "trustedChecksPassed": trusted_checks_passed,
            "startedAt": started.isoformat(),
            "finishedAt": finished.isoformat(),
            "durationSeconds": round((finished - started).total_seconds(), 6),
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    started = utc_now()
    config: dict[str, Any] | None = None
    transport: dict[str, Any] | None = None
    evidence: Path | None = None
    agent_exit_code: int | None = None
    timed_out = False
    trusted_checks_passed: bool | None = None
    status = "HARNESS_ERROR"

    try:
        config = validate_run_config(
            load_object(args.config.resolve(strict=True), "run config")
        )
        transport_path = resolve_repo_file(config["transportConfig"], "transportConfig")
        transport = validate_transport(
            load_object(transport_path, "transport config"), config["candidateName"]
        )
        task_path = resolve_repo_file(config["taskFile"], "taskFile")
        prompt = task_path.read_text(encoding="utf-8")
        if not prompt.strip():
            raise HarnessError("taskFile is empty")

        prepare_workspace.validate_preconditions(config["runId"])
        workspace = prepare_workspace.prepare_workspace(
            config["runId"], config["baselineCommit"]
        )
        prepare_workspace.verify_workspace(workspace, config["baselineCommit"])
        runtime, evidence = prepare_workspace.prepare_run_directories(config["runId"])
        policy_path, policy_sha256 = prepare_workspace.generate_srt_policy(
            workspace, runtime, evidence
        )

        write_json(evidence / "run.json", config)
        write_json(evidence / "transport.json", transport)
        atomic_write(evidence / "task.md", prompt.encode("utf-8"))
        write_json(
            evidence / "baseline.json",
            {
                "baselineCommit": config["baselineCommit"],
                "taskFile": config["taskFile"],
                "taskSha256": sha256_file(task_path),
                "srtPolicySha256": policy_sha256,
                "managedSettingsSha256": sha256_file(MANAGED_SETTINGS),
            },
        )
        atomic_write(evidence / "managed-settings.json", MANAGED_SETTINGS.read_bytes())

        if not SYSTEM_MANAGED_SETTINGS.is_file() or sha256_file(
            SYSTEM_MANAGED_SETTINGS
        ) != sha256_file(MANAGED_SETTINGS):
            raise HarnessError(
                "effective managed settings do not match the trusted copy"
            )

        agent_exit_code, timed_out = run_candidate(
            prompt,
            workspace,
            runtime,
            evidence,
            policy_path,
            transport,
            config["timeoutSeconds"],
            CLAUDE_BIN,
        )
        if config["verificationProfile"] == run_na_section_profile.PROFILE:
            verifier_code = run_na_section_profile.run_profile(
                config["runId"], workspace, evidence
            )
        elif config["verificationProfile"] == run_organization_current_profile.PROFILE:
            verifier_code = run_organization_current_profile.run_profile(
                config["runId"], workspace, evidence
            )
        elif config["verificationProfile"] == run_active_organization_selector_profile.PROFILE:
            verifier_code = run_active_organization_selector_profile.run_profile(
                config["runId"], workspace, evidence
            )
        else:
            verifier_code = run_rat_default.run_profile(
                config["runId"], workspace, evidence
            )
        status, trusted_checks_passed = derive_status(
            agent_exit_code, timed_out, verifier_code
        )
    except Exception as exc:
        if evidence is not None:
            for log_name in ("agent.stdout.log", "agent.stderr.log"):
                log_path = evidence / log_name
                if not log_path.exists():
                    atomic_write(log_path, b"")
            verification_path = evidence / "verification.json"
            if not verification_path.exists():
                now = utc_now().isoformat()
                write_json(
                    verification_path,
                    {
                        "schemaVersion": "1.0",
                        "profile": config["verificationProfile"],
                        "status": "HARNESS_ERROR",
                        "trustedChecksPassed": False,
                        "startedAt": started.isoformat(),
                        "finishedAt": now,
                        "checks": [],
                        "error": f"{type(exc).__name__}: {exc}",
                    },
                )
            atomic_write(
                evidence / "tests.log",
                f"HARNESS_ERROR {type(exc).__name__}: {exc}\n".encode(),
            )
        print(f"HARNESS_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
    finally:
        if config is not None and evidence is not None:
            write_result(
                evidence,
                config,
                status,
                agent_exit_code,
                timed_out,
                trusted_checks_passed,
                started,
            )
            write_manifest(evidence)
            try:
                verify_evidence.validate_evidence(evidence)
            except Exception as exc:
                status = "HARNESS_ERROR"
                trusted_checks_passed = None
                current_log = (evidence / "tests.log").read_bytes()
                atomic_write(
                    evidence / "tests.log",
                    current_log
                    + f"HARNESS_ERROR evidence validation: {type(exc).__name__}: {exc}\n".encode(),
                )
                write_result(
                    evidence,
                    config,
                    status,
                    agent_exit_code,
                    timed_out,
                    trusted_checks_passed,
                    started,
                )
                write_manifest(evidence)
                try:
                    verify_evidence.validate_evidence(evidence)
                except Exception as final_exc:
                    print(
                        "HARNESS_ERROR: evidence could not be closed: "
                        f"{type(final_exc).__name__}: {final_exc}",
                        file=sys.stderr,
                    )
                else:
                    verify_evidence.lock_evidence(evidence)
            else:
                verify_evidence.lock_evidence(evidence)

    return {"PASS": 0, "FAIL": 1, "TIMEOUT": 124, "HARNESS_ERROR": 2}[status]


if __name__ == "__main__":
    raise SystemExit(main())
