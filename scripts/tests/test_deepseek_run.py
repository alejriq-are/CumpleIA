import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
import handoff as h

SPEC = importlib.util.spec_from_file_location(
    "deepseek_run", Path(__file__).parents[1] / "deepseek_run.py"
)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.output = Path(self.tmp.name) / "out"
        for cmd in (
            ("git", "init", "-q"),
            ("git", "config", "user.name", "TEST"),
            ("git", "config", "user.email", "test@example.invalid"),
        ):
            h.run(self.root, *cmd)
        (self.root / "a.txt").write_text("PRUEBA\n")
        h.run(self.root, "git", "add", "a.txt")
        h.run(self.root, "git", "commit", "-qm", "test")
        self.base = h.state(self.root)["head"]
        self.bundle = dict(
            task=dict(id="TEST", allowed_files=["a.txt"]),
            state=dict(head=self.base),
            files={},
        )
        self.result = dict(
            task_id="TEST",
            base_head=self.base,
            patch="--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-PRUEBA\n+PRUEBA NUEVA\n",
            checks=[],
        )

    def tearDown(self):
        self.tmp.cleanup()

    def balance(self, key):
        return dict(
            is_available=True,
            balance_infos=[dict(currency="USD", total_balance="4.70")],
        )

    def transport(self, body, key):
        self.assertEqual(key, "PRUEBA-CLAVE-FICTICIA")
        self.assertEqual(body["max_tokens"], 4096)
        self.assertEqual(body["thinking"]["type"], "disabled")
        return dict(
            choices=[
                dict(
                    finish_reason="stop", message=dict(content=json.dumps(self.result))
                )
            ],
            usage=dict(prompt_tokens=10, completion_tokens=10),
        )

    def test_default_never_reads_key_or_calls_network(self):
        original = m.os.environ.get

        def checked_get(name, *args):
            if name == "CUMPLEIA_DEEPSEEK_HANDOFF_KEY":
                raise AssertionError("No leer clave")
            return original(name, *args)

        with patch.object(m.os.environ, "get", side_effect=checked_get):
            result = m.run_task(
                self.root,
                self.bundle,
                self.output,
                transport=lambda *a: self.fail("No llamar API"),
            )
        self.assertEqual(result["requests_sent"], 0)

    def test_mock_send_scoped_no_apply_no_secret_log(self):
        with patch.dict(
            m.os.environ, {"CUMPLEIA_DEEPSEEK_HANDOFF_KEY": "PRUEBA-CLAVE-FICTICIA"}
        ):
            result = m.run_task(
                self.root, self.bundle, self.output, True, self.transport, self.balance
            )
        self.assertEqual(result["requests_sent"], 1)
        self.assertEqual((self.root / "a.txt").read_text(), "PRUEBA\n")
        self.assertNotIn(
            "PRUEBA-CLAVE-FICTICIA",
            "".join(p.read_text() for p in self.output.iterdir()),
        )

    def test_no_second_request_in_same_run_directory(self):
        with patch.dict(
            m.os.environ, {"CUMPLEIA_DEEPSEEK_HANDOFF_KEY": "PRUEBA-CLAVE-FICTICIA"}
        ):
            m.run_task(
                self.root, self.bundle, self.output, True, self.transport, self.balance
            )
            with self.assertRaises(FileExistsError):
                m.run_task(
                    self.root,
                    self.bundle,
                    self.output,
                    True,
                    lambda *a: self.fail("Segunda API"),
                )

    def test_fabricated_execution_rejected(self):
        self.result["checks"] = [dict(status="passed")]
        with patch.dict(
            m.os.environ, {"CUMPLEIA_DEEPSEEK_HANDOFF_KEY": "PRUEBA-CLAVE-FICTICIA"}
        ):
            with self.assertRaises(ValueError):
                m.run_task(
                    self.root,
                    self.bundle,
                    self.output,
                    True,
                    self.transport,
                    self.balance,
                )

    def test_stale_never_sends(self):
        self.bundle["state"]["head"] = "0" * 40
        with self.assertRaises(ValueError):
            m.run_task(
                self.root,
                self.bundle,
                self.output,
                True,
                lambda *a: self.fail("No enviar"),
            )

    def test_currency_delta_not_combined(self):
        before = dict(
            balance_infos=[
                dict(currency="USD", total_balance="4.70"),
                dict(currency="CNY", total_balance="5.39"),
            ]
        )
        after = dict(
            balance_infos=[
                dict(currency="USD", total_balance="4.69"),
                dict(currency="CNY", total_balance="5.38"),
            ]
        )
        self.assertEqual(m.balance_delta(before, after), dict(USD="0.01", CNY="0.01"))

    def test_insufficient_balance_never_sends(self):
        with patch.dict(
            m.os.environ, {"CUMPLEIA_DEEPSEEK_HANDOFF_KEY": "PRUEBA-CLAVE-FICTICIA"}
        ):
            with self.assertRaises(ValueError):
                m.run_task(
                    self.root,
                    self.bundle,
                    self.output,
                    True,
                    lambda *a: self.fail("No llamar API"),
                    lambda key: dict(is_available=False),
                )

    def test_usage_estimate_separate_from_invoice(self):
        costs = m.estimated_cost(
            dict(
                prompt_tokens=1000000,
                completion_tokens=1000000,
                prompt_cache_hit_tokens=0,
            )
        )
        from decimal import Decimal

        self.assertEqual(Decimal(costs["peak_usd"]), Decimal("1.5"))
        self.assertEqual(Decimal(costs["off_peak_usd"]), Decimal("0.75"))
        self.assertIsNone(m.estimated_cost(dict(prompt_tokens=-1, completion_tokens=1)))

    def test_output_cannot_dirty_repo(self):
        with self.assertRaises(ValueError):
            m.run_task(self.root, self.bundle, self.root / "out")


if __name__ == "__main__":
    unittest.main()
