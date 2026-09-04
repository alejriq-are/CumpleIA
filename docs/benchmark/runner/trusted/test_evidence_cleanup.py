import json
from pathlib import Path

import pytest

import cleanup_run
import run_benchmark
import verify_evidence


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value) + "\n")
    path.chmod(0o600)


@pytest.fixture
def closed_run(tmp_path: Path, monkeypatch):
    evidence_root = tmp_path / "evidence"
    workspace_root = tmp_path / "workspaces"
    runtime_root = tmp_path / "runtime"
    runtime_tmp_root = tmp_path / "runtime-tmp"
    for root in (evidence_root, workspace_root, runtime_root, runtime_tmp_root):
        root.mkdir(mode=0o700)
    run_id = "test-run"
    evidence = evidence_root / run_id
    workspace = workspace_root / run_id
    runtime = runtime_root / run_id
    runtime_tmp = runtime_tmp_root / cleanup_run.runtime_tmp_name(run_id)
    evidence.mkdir(mode=0o700)
    workspace.mkdir(mode=0o700)
    runtime.mkdir(mode=0o700)
    runtime_tmp.mkdir(mode=0o700)

    monkeypatch.setattr(verify_evidence, "EVIDENCE_ROOT", evidence_root)
    monkeypatch.setattr(cleanup_run, "EVIDENCE_ROOT", evidence_root)
    monkeypatch.setattr(cleanup_run, "WORKSPACE_ROOT", workspace_root)
    monkeypatch.setattr(cleanup_run, "RUNTIME_ROOT", runtime_root)
    monkeypatch.setattr(cleanup_run, "RUNTIME_TMP_ROOT", runtime_tmp_root)

    canonical = str(Path(verify_evidence.__file__).resolve().parent.parents[3])
    task = evidence / "task.md"
    policy = evidence / "srt-settings.json"
    managed = evidence / "managed-settings.json"
    task.write_text("test task\n")
    policy.write_text(
        json.dumps(
            {
                "filesystem": {
                    "allowWrite": [str(workspace)],
                    "denyRead": [canonical, str(evidence_root)],
                    "denyWrite": [canonical, str(evidence_root)],
                }
            }
        )
    )
    managed.write_text("{}\n")
    for path in (task, policy, managed):
        path.chmod(0o600)

    run = {
        "schemaVersion": "1.0",
        "runId": run_id,
        "candidateName": "candidate",
        "baselineCommit": "a" * 40,
        "taskFile": "tasks/test.md",
        "transportConfig": "transport/test.json",
        "timeoutSeconds": 30,
        "verificationProfile": "rat-default",
    }
    write_json(evidence / "run.json", run)
    write_json(
        evidence / "transport.json",
        {
            "candidateName": "candidate",
            "backendClass": "local",
            "provider": "provider",
            "endpoint": "http://example.invalid",
            "modelId": "model",
            "credentialEnv": None,
            "timeoutSeconds": 30,
        },
    )
    write_json(
        evidence / "baseline.json",
        {
            "baselineCommit": "a" * 40,
            "taskFile": "tasks/test.md",
            "taskSha256": verify_evidence.sha256_file(task),
            "srtPolicySha256": verify_evidence.sha256_file(policy),
            "managedSettingsSha256": verify_evidence.sha256_file(managed),
        },
    )
    write_json(
        evidence / "verification.json",
        {
            "schemaVersion": "1.0",
            "profile": "rat-default",
            "status": "PASS",
            "trustedChecksPassed": True,
            "checks": [],
        },
    )
    write_json(
        evidence / "result.json",
        {
            "schemaVersion": "1.0",
            "runId": run_id,
            "candidateName": "candidate",
            "baselineCommit": "a" * 40,
            "status": "PASS",
            "agentExitCode": 0,
            "timedOut": False,
            "trustedChecksPassed": True,
            "startedAt": "2026-09-04T12:00:00+00:00",
            "finishedAt": "2026-09-04T12:00:01+00:00",
            "durationSeconds": 1.0,
        },
    )
    for name in ("agent.stdout.log", "agent.stderr.log", "tests.log"):
        (evidence / name).write_text("")
        (evidence / name).chmod(0o600)
    run_benchmark.write_manifest(evidence)
    return run_id, evidence, workspace, runtime, runtime_tmp


def test_validate_and_lock_evidence(closed_run):
    _, evidence, _, _, _ = closed_run
    assert verify_evidence.validate_evidence(evidence) == evidence
    verify_evidence.lock_evidence(evidence)
    assert evidence.stat().st_mode & 0o777 == 0o500
    assert all(path.stat().st_mode & 0o777 == 0o400 for path in evidence.iterdir())


def test_cleanup_deletes_only_ephemeral_roots(closed_run):
    run_id, evidence, workspace, runtime, runtime_tmp = closed_run
    assert cleanup_run.cleanup(run_id, execute=False) == [
        ("workspace", "WOULD_DELETE"),
        ("runtime", "WOULD_DELETE"),
        ("runtime_tmp", "WOULD_DELETE"),
    ]
    assert cleanup_run.cleanup(run_id, execute=True) == [
        ("workspace", "DELETED"),
        ("runtime", "DELETED"),
        ("runtime_tmp", "DELETED"),
    ]
    assert evidence.exists()
    assert not workspace.exists()
    assert not runtime.exists()
    assert not runtime_tmp.exists()


def test_manifest_tamper_is_rejected(closed_run):
    _, evidence, _, _, _ = closed_run
    (evidence / "task.md").write_text("tampered\n")
    with pytest.raises(verify_evidence.EvidenceError, match="SHA-256 mismatch"):
        verify_evidence.validate_evidence(evidence)
