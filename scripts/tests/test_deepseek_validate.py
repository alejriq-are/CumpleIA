import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))
import deepseek_validate as v
import handoff as h


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        for args in [
            ("git", "init", "-q"),
            ("git", "config", "user.name", "TEST"),
            ("git", "config", "user.email", "test@example.invalid"),
        ]:
            h.run(self.root, *args)
        (self.root / "frontend/e2e").mkdir(parents=True)
        (self.root / ".gitignore").write_text("node_modules/\n")
        (self.root / "frontend/a.ts").write_text("const a = 1;\n")
        (self.root / "frontend/e2e/protected.spec.ts").write_text(
            "// PRUEBA INDEPENDIENTE\n"
        )
        (self.root / "frontend/.env.example").write_text("PRUEBA=solo_ficticia\n")
        h.run(self.root, "git", "add", ".")
        h.run(self.root, "git", "commit", "-qm", "fixture")
        self.base = h.state(self.root)["head"]
        (self.root / "frontend/node_modules").mkdir()
        self.task = dict(
            id="TEST",
            allowed_files=["frontend/a.ts"],
            validation=dict(
                test_files=["frontend/e2e/protected.spec.ts"], timeout_seconds=5
            ),
        )
        self.patch = Path(self.tmp.name) / "candidate.patch"
        self.patch.write_text(
            "--- a/frontend/a.ts\n+++ b/frontend/a.ts\n@@ -1 +1 @@\n-const a = 1;\n+const a = 2;\n"
        )
        self.hash = v.digest(self.patch)
        self.output = Path(self.tmp.name) / "validation"

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self, runner):
        return v.validate_candidate(
            self.root, self.task, self.base, self.patch, self.output, self.hash, runner
        )

    def test_format_before_checks_no_secrets_no_source_apply(self):
        seen = []

        def runner(command, cwd, env, timeout):
            seen.append(command)
            self.assertNotIn("CUMPLEIA_DEEPSEEK_HANDOFF_KEY", env)
            self.assertNotIn("DATABASE_URL", env)
            self.assertFalse((cwd / ".env.example").exists())
            if "prettier" in command:
                (cwd / "a.ts").write_text("const a = 2; // formatted\n")
            return dict(exit_code=0, output="PRUEBA")

        result = self.validate(runner)
        self.assertEqual(result["result"], "checks_passed_pending_acceptance")
        self.assertIn("prettier", seen[0])
        self.assertEqual((self.root / "frontend/a.ts").read_text(), "const a = 1;\n")
        self.assertIn("formatted", (self.output / "formatted.patch").read_text())
        self.assertTrue((self.output / "feedback.json").exists())
        self.assertFalse(result["automatic_publish"])
        self.assertEqual(h.state(self.root)["head"], self.base)

    def test_failed_check_stops_and_produces_specific_feedback(self):
        def runner(command, *args):
            return dict(
                exit_code=1 if "playwright" in command else 0,
                output="PRUEBA: Expected 1 Received 2",
            )

        result = self.validate(runner)
        self.assertEqual(result["result"], "checks_failed")
        self.assertEqual(len(result["checks"]), 2)
        feedback = json.loads((self.output / "feedback.json").read_text())
        self.assertEqual(feedback["failed_checks"][0]["check"], "ui")
        self.assertIn("Received 2", feedback["failed_checks"][0]["log"])

    def test_review_hash_and_reused_output_blocked(self):
        with self.assertRaises(ValueError):
            v.validate_candidate(
                self.root,
                self.task,
                self.base,
                self.patch,
                self.output,
                "wrong",
                lambda *a: self.fail(),
            )
        self.validate(lambda *a: dict(exit_code=0, output=""))
        with self.assertRaises(FileExistsError):
            self.validate(lambda *a: self.fail("No ejecutar de nuevo"))

    def test_protected_test_or_source_mutation_rejected(self):
        def runner(command, cwd, *args):
            if "playwright" in command:
                (cwd / "e2e/protected.spec.ts").write_text("// debilitado\n")
            return dict(exit_code=0, output="")

        with self.assertRaises(ValueError):
            self.validate(runner)
        self.assertFalse((self.output / "formatted.patch").exists())

    def test_test_path_injection_and_timeout_policy_rejected(self):
        for name in [
            "frontend/e2e/../evil.spec.ts",
            "frontend/e2e/-flag",
            "other.spec.ts",
        ]:
            self.task["validation"]["test_files"] = [name]
            with self.assertRaises(ValueError):
                self.validate(lambda *a: self.fail())
        self.task["validation"]["test_files"] = ["frontend/e2e/protected.spec.ts"]
        self.task["validation"]["timeout_seconds"] = 0
        with self.assertRaises(ValueError):
            self.validate(lambda *a: self.fail())

    def test_checks_cannot_rewrite_even_allowed_source(self):
        def runner(command, cwd, *args):
            if "playwright" in command:
                (cwd / "a.ts").write_text("const a = 99;\n")
            return dict(exit_code=0, output="")

        with self.assertRaises(ValueError):
            self.validate(runner)
        self.assertFalse((self.output / "formatted.patch").exists())

    def test_dirty_base_during_validation_blocks_export(self):
        def runner(*args):
            (self.root / "frontend/a.ts").write_text("const a = 3;\n")
            return dict(exit_code=0, output="")

        with self.assertRaises(ValueError):
            self.validate(runner)
        self.assertFalse((self.output / "formatted.patch").exists())

    @unittest.skipUnless(os.name == "posix", "process groups require WSL/Linux")
    def test_timeout_kills_child_process_group(self):
        result = v.run_command(
            [
                sys.executable,
                "-c",
                "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)']); time.sleep(10)",
            ],
            Path(self.tmp.name),
            {"PATH": os.environ["PATH"]},
            0.1,
        )
        self.assertEqual(result["exit_code"], 124)


if __name__ == "__main__":
    unittest.main()
