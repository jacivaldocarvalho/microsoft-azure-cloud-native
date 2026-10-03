"""Offline checks for configuration and initialization failure handling."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))
import config

spec = importlib.util.spec_from_file_location("initializer", APP_DIR / "database/init-db.py")
initializer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(initializer)

SETTINGS = {
    "SQL_SERVER": "example.database.windows.net",
    "SQL_DATABASE": "example",
    "SQL_USERNAME": "example",
    "SQL_PASSWORD": "test-only",
}


class ConfigurationTests(unittest.TestCase):
    def test_missing_settings_report_names_without_values(self):
        with patch.dict(os.environ, {"SQL_PASSWORD": "test-only"}, clear=True):
            with self.assertRaises(ValueError) as result:
                config.sql_settings()
            self.assertIn("SQL_SERVER", str(result.exception))
            self.assertNotIn("test-only", str(result.exception))

    def test_canonical_settings_override_legacy_names(self):
        with patch.dict(os.environ, {**SETTINGS, "SQL_USER": "legacy"}, clear=True):
            self.assertEqual(config.sql_settings(), SETTINGS)

    def test_legacy_settings_remain_supported(self):
        legacy = {"SQL_SERVER_NAME": "example", "SQL_DB_NAME": "example",
                  "SQL_USER": "example", "SQL_PASSWORD": "test-only"}
        with patch.dict(os.environ, legacy, clear=True):
            self.assertEqual(config.sql_settings(), SETTINGS)

    def test_initializer_reads_schema_from_another_directory(self):
        connection = MagicMock()
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                with patch.dict(os.environ, SETTINGS, clear=True), patch.object(
                    initializer.pymssql, "connect", return_value=connection
                ):
                    self.assertEqual(initializer.main(), 0)
            finally:
                os.chdir(previous)
        cursor = connection.__enter__.return_value.cursor.return_value.__enter__.return_value
        sql_script = cursor.execute.call_args.args[0]
        self.assertIn("IF OBJECT_ID(N'dbo.Produtos', N'U') IS NULL", sql_script)
        self.assertIn("CREATE TABLE dbo.Produtos", sql_script)
        connection.__enter__.return_value.commit.assert_called_once()

    def test_database_failure_returns_nonzero(self):
        with patch.dict(os.environ, SETTINGS, clear=True), patch.object(
            initializer.pymssql, "connect", side_effect=RuntimeError("connection unavailable")
        ):
            self.assertEqual(initializer.main(), 1)


if __name__ == "__main__":
    unittest.main()
