"""Validacion local de un candidato revisado; sin API, shell libre ni publicacion."""

import argparse
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import tarfile

from handoff import check_patch, load_task, state


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_command(command, cwd, env, timeout):
    if os.name != "posix":
        raise ValueError("Ejecutar validacion en WSL/Linux")
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        output, _ = proc.communicate(timeout=timeout)
        code = proc.returncode
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        output, _ = proc.communicate()
        code = 124
    return dict(exit_code=code, output=output[-12000:])


def validation_options(root, task, base):
    config = task.get("validation", {})
    tests = config.get("test_files")
    if not isinstance(tests, list) or not tests:
        raise ValueError("Contrato requiere validation.test_files explicitos")
    for name in tests:
        if (
            not isinstance(name, str)
            or not name.startswith("frontend/e2e/")
            or not name.endswith(".spec.ts")
            or ".." in Path(name).parts
            or "\\" in name
        ):
            raise ValueError("Ruta de prueba no permitida")
        row = subprocess.check_output(
            ["git", "ls-tree", base, "--", name], cwd=root, text=True
        )
        if not row.startswith("100644 "):
            raise ValueError("Prueba debe existir y estar versionada")
    timeout = config.get("timeout_seconds", 60)
    if type(timeout) is not int or not 5 <= timeout <= 120:
        raise ValueError("Timeout debe estar entre 5 y 120 segundos")
    return list(dict.fromkeys(tests)), timeout


def validate_candidate(
    root, task, base, patch, output, reviewed_sha, runner=run_command
):
    root, patch, output = (Path(p).resolve() for p in (root, patch, output))
    if output.is_relative_to(root):
        raise ValueError("Salida debe estar fuera del checkout")
    if not isinstance(reviewed_sha, str) or reviewed_sha != digest(patch):
        raise ValueError("Revision no corresponde al hash exacto del candidato")
    checked = check_patch(root, task, base, patch)
    paths = checked["paths"]
    if any(
        not name.startswith("frontend/")
        or not name.endswith((".ts", ".tsx", ".js", ".jsx"))
        for name in paths
    ):
        raise ValueError("Perfil solo frontend TS/JS existente")
    tests, timeout = validation_options(root, task, base)
    deps = root / "frontend/node_modules"
    if not deps.is_dir():
        raise ValueError("Instalar dependencias existentes antes; ejecutor no instala")
    # Un intento por salida: no mezclar candidatos o resultados anteriores.
    output.mkdir(parents=True, exist_ok=True)
    with (output / "validation-started.json").open("x") as file:
        json.dump(dict(base_head=base, reviewed_candidate_sha256=reviewed_sha), file)
    checkout = output / "checkout"
    checkout.mkdir()
    archive = subprocess.check_output(["git", "archive", base, "frontend"], cwd=root)
    tracked = []
    with tarfile.open(fileobj=io.BytesIO(archive)) as source:
        for member in source.getmembers():
            name = Path(member.name)
            if name.is_absolute() or ".." in name.parts or name.parts[0] != "frontend":
                raise ValueError("Snapshot fuera de alcance")
            if any(part.startswith(".env") for part in name.parts):
                continue
            target = checkout / name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.extractfile(member).read())
                tracked.append(member.name)
            else:
                raise ValueError("Snapshot con enlace no admitido")
    (checkout / "frontend/node_modules").symlink_to(deps, target_is_directory=True)
    subprocess.run(
        ["git", "apply", str(patch)], cwd=checkout, check=True, capture_output=True
    )
    protected = {name: digest(checkout / name) for name in tracked if name not in paths}
    # Ningun secreto/API key del proceso se hereda a los checks.
    env = {
        key: os.environ[key] for key in ("PATH", "HOME", "LANG") if key in os.environ
    }
    env["CI"] = "true"
    cwd = checkout / "frontend"
    results = []
    relative = [str(Path(name).relative_to("frontend")) for name in paths]
    commands = [
        ("format", ["npx", "--no-install", "prettier", "--write", *relative]),
        (
            "ui",
            [
                "npx",
                "--no-install",
                "playwright",
                "test",
                *[str(Path(t).relative_to("frontend")) for t in tests],
                "--timeout",
                str(timeout * 1000),
            ],
        ),
        ("types", ["npm", "run", "type-check"]),
        ("lint", ["npm", "run", "lint"]),
    ]
    after_format = None
    for label, command in commands:
        result = runner(command, cwd, env, timeout)
        results.append(dict(check=label, exit_code=result["exit_code"]))
        (output / (label + ".log")).write_text(result["output"])
        if label == "format":
            after_format = {name: digest(checkout / name) for name in tracked}
        if result["exit_code"]:
            break
    if any(
        not (checkout / name).is_file() or digest(checkout / name) != value
        for name, value in protected.items()
    ):
        raise ValueError("Archivo protegido alterado; no aceptar ni exportar")
    if after_format and any(
        not (checkout / name).is_file() or digest(checkout / name) != value
        for name, value in after_format.items()
    ):
        raise ValueError("Checks modificaron fuentes; no exportar")
    snapshot = state(root)
    if snapshot["head"] != base or snapshot["dirty"]:
        raise ValueError("Base cambio durante validacion; no exportar")
    final = "".join(
        "".join(
            difflib.unified_diff(
                subprocess.check_output(["git", "show", base + ":" + name], cwd=root)
                .decode()
                .splitlines(True),
                (checkout / name).read_text().splitlines(True),
                fromfile="a/" + name,
                tofile="b/" + name,
            )
        )
        for name in paths
    )
    formatted = output / "formatted.patch"
    formatted.write_text(final)
    check_patch(root, task, base, formatted)
    success = len(results) == len(commands) and all(
        row["exit_code"] == 0 for row in results
    )
    summary = dict(
        task_id=task["id"],
        base_head=base,
        checks=results,
        reviewed_candidate_sha256=reviewed_sha,
        formatted_patch_sha256=digest(formatted),
        protected_sha256=protected,
        result="checks_passed_pending_acceptance" if success else "checks_failed",
        automatic_apply=False,
        automatic_publish=False,
    )
    (output / "validation.json").write_text(json.dumps(summary, indent=2))
    feedback = dict(
        task_id=task["id"],
        base_head=base,
        failed_checks=[
            dict(
                check=row["check"],
                exit_code=row["exit_code"],
                log=(output / (row["check"] + ".log")).read_text()[-6000:],
            )
            for row in results
            if row["exit_code"]
        ],
        instruction="Corregir fallo concreto; no editar pruebas protegidas ni debilitar assertions. Formato es automatico.",
    )
    (output / "feedback.json").write_text(
        json.dumps(feedback, ensure_ascii=False, indent=2)
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--task", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--patch", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--reviewed-sha256", required=True)
    args = parser.parse_args()
    try:
        result = validate_candidate(
            args.root,
            load_task(args.task),
            args.base,
            args.patch,
            args.output,
            args.reviewed_sha256,
        )
        print(
            json.dumps(
                {k: v for k, v in result.items() if k != "protected_sha256"}, indent=2
            )
        )
    except (ValueError, FileExistsError, subprocess.CalledProcessError, OSError):
        raise SystemExit(
            "Validacion detenida; revisar artefactos, no aplicar/publicar"
        ) from None


if __name__ == "__main__":
    main()
