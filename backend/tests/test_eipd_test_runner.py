"""Guardas del ejecutor: sin abrir conexiones ni modificar el entorno padre."""

import unittest
from types import SimpleNamespace

from sqlalchemy.engine import make_url

from scripts.run_eipd_tests import (
    EXPECTED_HEAD,
    TEST_DATABASE,
    build_environment,
    validate_catalog,
)


class RunnerGuards(unittest.TestCase):
    def settings(self, **changes):
        values = dict(
            environment="development",
            database_url="postgresql+asyncpg://owner:fake@localhost:5432/cumpleia",
            app_database_url="postgresql+asyncpg://app_user:fake@localhost:5432/cumpleia",
        )
        return SimpleNamespace(**(values | changes))

    def test_routes_both_roles_to_fixed_database_without_mutating_parent(self):
        parent = {
            "DATABASE_URL": "operational",
            "eipd_admin_database_url": "private",
            "PYTEST_ADDOPTS": "other",
            "SUPABASE_SERVICE_ROLE_KEY": "private",
        }
        before = parent.copy()
        env = build_environment(self.settings(), parent)
        self.assertEqual(parent, before)
        for key, user in (("DATABASE_URL", "owner"), ("APP_DATABASE_URL", "app_user")):
            url = make_url(env[key])
            self.assertEqual(url.database, TEST_DATABASE)
            self.assertEqual(url.username, user)
        self.assertNotIn("eipd_admin_database_url", env)
        self.assertNotIn("PYTEST_ADDOPTS", env)
        self.assertNotIn("SUPABASE_SERVICE_ROLE_KEY", env)

    def test_rejects_nonlocal_query_and_production(self):
        for changes in (
            dict(environment="production"),
            dict(database_url="postgresql+asyncpg://owner:fake@remote/cumpleia"),
            dict(
                database_url="postgresql+asyncpg://owner:fake@localhost/cumpleia?host=remote"
            ),
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                build_environment(self.settings(**changes), {})

    def test_rejects_runtime_owner_and_mismatched_destinations(self):
        for url in (
            "postgresql+asyncpg://owner:fake@localhost:5432/cumpleia",
            "postgresql+asyncpg://app_user:fake@localhost:5433/cumpleia",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                build_environment(self.settings(app_database_url=url), {})

    def test_catalog_rejects_operational_database_wrong_head_and_nonempty_state(self):
        valid = [TEST_DATABASE, EXPECTED_HEAD, 0, 0, 0, "app_user", False, False]
        validate_catalog(*valid)
        for index, value in (
            (0, "cumpleia"),
            (1, "old"),
            (2, 1),
            (3, 1),
            (4, 1),
            (5, "owner"),
            (6, True),
            (7, True),
        ):
            args = valid.copy()
            args[index] = value
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate_catalog(*args)
