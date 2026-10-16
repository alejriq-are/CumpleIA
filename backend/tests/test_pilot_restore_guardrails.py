"""Entradas externas nunca redirigen una restauracion; no requiere conexion DB."""

import unittest
from unittest.mock import patch

from scripts import check_pilot_restore as restore


class RestoreGuards(unittest.TestCase):
    def refuse(self, argument):
        with (
            patch.object(restore.sys, "argv", ["check_pilot_restore", argument]),
            patch.object(restore, "run") as run,
        ):
            self.assertEqual(restore.main(), 2)
            run.assert_not_called()

    def test_force_argument(self):
        self.refuse("--force")

    def test_operational_database_argument(self):
        self.refuse("cumpleia")

    def test_external_url_argument(self):
        self.refuse("postgresql://example.invalid/production")

    def test_missing_docker_refuses_before_settings_or_database(self):
        with (
            patch.object(restore.shutil, "which", return_value=None),
            patch.object(restore, "get_settings") as settings,
        ):
            with self.assertRaisesRegex(RuntimeError, "Docker local no disponible"):
                restore.run()
            settings.assert_not_called()
