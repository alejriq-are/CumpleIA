"""Recorrido Chromium local fijo; mismas barreras de destino que suite EIPD."""

import asyncio
import os
import shutil
import subprocess
import sys

from app.core.config import get_settings
from scripts.run_eipd_tests import build_environment, verify_destination


def main():
    if len(sys.argv) != 1:
        print("Ejecutor fijo: no admite argumentos adicionales.")
        return 2
    if shutil.which("npx") is None:
        print("Prueba no iniciada: Node/npm deben estar disponibles en PATH.")
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
            "tests/test_eipd_browser_integration.py",
        ],
        env=env,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
