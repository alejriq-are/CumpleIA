import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "handoff", Path(__file__).parents[1] / "handoff.py"
)
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for cmd in (
            ("git", "init", "-q"),
            ("git", "config", "user.name", "TEST"),
            ("git", "config", "user.email", "test@example.invalid"),
        ):
            h.run(self.root, *cmd)
        (self.root / "test.txt").write_text("  PRUEBA\n\n")
        h.run(self.root, "git", "add", "test.txt")
        h.run(self.root, "git", "commit", "-qm", "test")
        self.task = dict(
            id="TEST",
            objective="Prueba",
            acceptance=["Una linea"],
            allowed_files=["test.txt"],
            context_files=["test.txt"],
            checks=["no ejecutado"],
        )
        self.base = h.state(self.root)["head"]
        self.diff = Path(self.temp.name).parent / (self.root.name + ".patch")
        self.diff.write_text(
            "diff --git a/test.txt b/test.txt\n--- a/test.txt\n+++ b/test.txt\n@@ -1,2 +1,2 @@\n-  PRUEBA\n+  PRUEBA CAMBIO\n \n"
        )

    def tearDown(self):
        self.diff.unlink(missing_ok=True)
        self.temp.cleanup()

    def test_exact_content_and_no_invented_ci(self):
        s = h.state(self.root)
        data = json.loads(h.packet(self.root, self.task, s))
        self.assertIsNone(s["ci"])
        self.assertFalse(s["remote_checked"])
        self.assertEqual(data["files"]["test.txt"]["content"], "  PRUEBA\n\n")

    def test_dirty_blocks_packet(self):
        (self.root / "extra").write_text("PRUEBA")
        with self.assertRaises(ValueError):
            h.packet(self.root, self.task, h.state(self.root))

    def test_budget_blocks_packet(self):
        with self.assertRaises(ValueError):
            h.packet(self.root, self.task, h.state(self.root), max_chars=10)

    def test_check_does_not_apply_or_validate_tests(self):
        result = h.check_patch(self.root, self.task, self.base, self.diff)
        self.assertEqual(result["tests"], "no_ejecutados")
        self.assertEqual((self.root / "test.txt").read_text(), "  PRUEBA\n\n")

    def test_stale_blocks_patch(self):
        with self.assertRaises(ValueError):
            h.check_patch(self.root, self.task, "0" * 40, self.diff)

    def test_scope_blocks_patch(self):
        self.task["allowed_files"] = ["other.txt"]
        with self.assertRaises(ValueError):
            h.check_patch(self.root, self.task, self.base, self.diff)

    def test_mode_blocks_patch(self):
        self.diff.write_text(
            self.diff.read_text().replace(
                "--- a/", "old mode 100644\nnew mode 120000\n--- a/"
            )
        )
        with self.assertRaises(ValueError):
            h.check_patch(self.root, self.task, self.base, self.diff)

    def test_remote_failure_not_verified(self):
        with patch.object(
            h,
            "run",
            side_effect=lambda root, *a: (
                (_ for _ in ()).throw(subprocess.CalledProcessError(1, a))
                if a[:2] == ("git", "fetch")
                else subprocess.check_output(a, cwd=root, text=True).strip()
            ),
        ):
            s = h.state(self.root, True)
        self.assertFalse(s["remote_checked"])
        self.assertIsNone(s["ci"])
        self.assertIn("fetch_no_verificado", s["errors"])

    def test_ci_from_other_sha_not_verified(self):
        original = h.run

        def fake(root, *args):
            if args[:2] == ("git", "fetch"):
                return ""
            if args[:2] == ("gh", "run"):
                return json.dumps([{"headSha": "0" * 40, "conclusion": "success"}])
            if args[:2] == ("gh", "pr"):
                return "[]"
            return original(root, *args)

        with patch.object(h, "run", side_effect=fake):
            snapshot = h.state(self.root, True)
        self.assertIsNone(snapshot["ci"])
        self.assertIn("ci_no_verificado", snapshot["errors"])

    def test_reserved_paths_rejected(self):
        for name in ("../x", "/tmp/x", ".env", "sources/x"):
            file = self.root / "manifest.json"
            file.write_text(
                json.dumps(
                    {**self.task, "context_files": [name], "allowed_files": [name]}
                )
            )
            with self.assertRaises(ValueError):
                h.load_task(file)


if __name__ == "__main__":
    unittest.main()
