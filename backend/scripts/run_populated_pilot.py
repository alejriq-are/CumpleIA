"""Piloto fijo en DB aislada validada antes de poblar fixtures y restaurar."""

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
    env["CUMPLEIA_POPULATED_PILOT_RESTORE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-s", "tests/test_populated_pilot.py"],
        env=env,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
