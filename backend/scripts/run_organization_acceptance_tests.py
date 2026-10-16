"""Suite fija de aceptacion: solo DB aislada validada, sin argumentos arbitrarios."""

import asyncio
import os
import subprocess
import sys

from app.core.config import get_settings
from scripts.run_eipd_tests import build_environment, verify_destination


def main():
    if len(sys.argv) != 1:
        return 2
    env = build_environment(get_settings(), os.environ)
    asyncio.run(verify_destination(env))
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_organization_acceptance.py",
            "tests/test_mvp_dossier.py",
            "tests/test_pilot_preparation.py",
            "tests/test_pilot_restore_guardrails.py",
            "tests/test_child_adolescent_storage.py",
            "tests/test_eipd_child_successors.py",
            "tests/test_eipd_test_runner.py",
        ],
        env=env,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
