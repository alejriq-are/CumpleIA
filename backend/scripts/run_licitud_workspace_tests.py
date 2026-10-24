"""Destino fijo validado; recorrido nuevo opt-in Chromium sin DB operativa."""

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
    env["CUMPLEIA_UI_INTEGRATION"] = "1"
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=short",
            "tests/test_licitud_listing.py",
            "tests/test_licitud_browser_integration.py",
        ],
        env=env,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
