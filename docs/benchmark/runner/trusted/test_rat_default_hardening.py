from pathlib import Path

import run_rat_default


def test_runtime_images_are_pinned_by_digest():
    dockerfile = Path(run_rat_default.__file__).with_name("Dockerfile.rat-default")
    first_line = dockerfile.read_text(encoding="utf-8").splitlines()[0]

    assert first_line.startswith("FROM python@sha256:")
    assert run_rat_default.POSTGRES_IMAGE.startswith("pgvector/pgvector@sha256:")


def test_runner_container_security_limits_are_fail_closed():
    args = run_rat_default.CONTAINER_SECURITY_ARGS

    assert args == [
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "128",
        "--memory",
        "256m",
    ]
