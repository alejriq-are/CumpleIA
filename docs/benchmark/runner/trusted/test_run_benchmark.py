from pathlib import Path

import pytest

import run_benchmark


@pytest.mark.parametrize(
    ("agent_exit", "timed_out", "verifier_exit", "expected"),
    [
        (0, False, 0, ("PASS", True)),
        (1, False, 0, ("FAIL", True)),
        (0, False, 1, ("FAIL", False)),
        (None, True, 0, ("TIMEOUT", True)),
        (0, False, 2, ("HARNESS_ERROR", None)),
    ],
)
def test_derive_status(agent_exit, timed_out, verifier_exit, expected):
    assert run_benchmark.derive_status(agent_exit, timed_out, verifier_exit) == expected


def test_redact_and_write_removes_exact_credential(tmp_path: Path):
    output = tmp_path / "agent.log"
    run_benchmark.redact_and_write(output, b"before secret-value after", "secret-value")
    assert output.read_text() == "before [REDACTED] after"
    assert output.stat().st_mode & 0o777 == 0o600


def test_manifest_is_sorted_and_excludes_itself(tmp_path: Path):
    (tmp_path / "b.log").write_text("b")
    (tmp_path / "a.json").write_text("a")
    run_benchmark.write_manifest(tmp_path)
    lines = (tmp_path / "manifest.sha256").read_text().splitlines()
    assert [line.split("  ", 1)[1] for line in lines] == ["a.json", "b.log"]


def test_cloud_transport_requires_credential():
    transport = {
        "candidateName": "candidate",
        "backendClass": "cloud",
        "provider": "provider",
        "endpoint": "https://example.invalid",
        "modelId": "model",
        "credentialEnv": None,
        "timeoutSeconds": 30,
    }
    with pytest.raises(run_benchmark.HarnessError):
        run_benchmark.validate_transport(transport, "candidate")


def test_task_specific_profile_is_supported(monkeypatch, tmp_path: Path):
    task = tmp_path / "task.md"
    transport = tmp_path / "transport.json"
    task.write_text("task")
    transport.write_text("{}")
    monkeypatch.setattr(run_benchmark, "resolve_repo_file", lambda path, label: task)
    monkeypatch.setattr(
        run_benchmark.prepare_workspace, "validate_commit_exists", lambda commit: None
    )

    config = {
        "schemaVersion": "1.0",
        "runId": "round-1-candidate",
        "candidateName": "candidate",
        "baselineCommit": "a" * 40,
        "taskFile": "task.md",
        "transportConfig": "transport.json",
        "timeoutSeconds": 1800,
        "verificationProfile": "rat-na-section-v1",
    }

    assert run_benchmark.validate_run_config(config) == config


def test_organization_current_profile_is_supported(monkeypatch, tmp_path: Path):
    task = tmp_path / "task.md"
    transport = tmp_path / "transport.json"
    task.write_text("task")
    transport.write_text("{}")
    monkeypatch.setattr(run_benchmark, "resolve_repo_file", lambda path, label: task)
    monkeypatch.setattr(
        run_benchmark.prepare_workspace, "validate_commit_exists", lambda commit: None
    )
    config = {
        "schemaVersion": "1.0",
        "runId": "round-2-candidate",
        "candidateName": "candidate",
        "baselineCommit": "a" * 40,
        "taskFile": "task.md",
        "transportConfig": "transport.json",
        "timeoutSeconds": 1800,
        "verificationProfile": "rat-organization-current-v1",
    }
    assert run_benchmark.validate_run_config(config) == config


def test_local_transport_preflight_passes_with_expected_host_and_no_wildcards(
    monkeypatch,
):
    monkeypatch.setattr(
        run_benchmark.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (2, 1, 6, "", ("127.77.18.1", 0)),
        ],
    )

    class Result:
        stdout = "LISTEN 0 128 127.77.18.1:18080 0.0.0.0:*\n"

    monkeypatch.setattr(
        run_benchmark.subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    run_benchmark.validate_local_transport_preflight(
        {"endpoint": "http://llm-local.cumpleia:18080"}
    )


def test_local_transport_preflight_rejects_wrong_host_mapping(monkeypatch):
    monkeypatch.setattr(
        run_benchmark.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (2, 1, 6, "", ("127.0.0.1", 0)),
        ],
    )

    with pytest.raises(run_benchmark.HarnessError, match="local transport hostname"):
        run_benchmark.validate_local_transport_preflight(
            {"endpoint": "http://llm-local.cumpleia:18080"}
        )


def test_local_transport_preflight_rejects_wildcard_listener(monkeypatch):
    monkeypatch.setattr(
        run_benchmark.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (2, 1, 6, "", ("127.77.18.1", 0)),
        ],
    )

    class Result:
        stdout = "LISTEN 0 128 0.0.0.0:9000 0.0.0.0:*\n"

    monkeypatch.setattr(
        run_benchmark.subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    with pytest.raises(run_benchmark.HarnessError, match="wildcard listener"):
        run_benchmark.validate_local_transport_preflight(
            {"endpoint": "http://llm-local.cumpleia:18080"}
        )


def test_cloud_transport_preflight_skips_local_checks(monkeypatch):
    def unexpected_local_preflight(_transport):
        raise AssertionError("local preflight must not run for cloud transport")

    monkeypatch.setattr(
        run_benchmark,
        "validate_local_transport_preflight",
        unexpected_local_preflight,
    )

    run_benchmark.validate_transport_preflight(
        {
            "backendClass": "cloud",
            "endpoint": "https://api.anthropic.com",
        }
    )
