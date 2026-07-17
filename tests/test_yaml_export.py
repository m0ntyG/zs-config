import os
import unittest
import yaml

# Set up database path environment variable before any DB imports
os.environ["ZSCALER_DB_PATH"] = "zs_db/zscaler.db"

from db.database import export_db_to_yaml_string


class TestYAMLExport(unittest.TestCase):
    def test_export_db_to_yaml_string(self):
        # Run export
        yaml_content = export_db_to_yaml_string()
        self.assertTrue(isinstance(yaml_content, str))
        self.assertGreater(len(yaml_content), 0)

        # Parse YAML and validate structure
        data = yaml.safe_load(yaml_content)
        self.assertTrue(isinstance(data, dict))

        # Check all standard tables are present in the export
        expected_tables = [
            "app_settings",
            "users",
            "tenant_configs",
            "certificates",
            "webauthn_credentials",
            "user_tenant_entitlements",
            "scheduled_tasks",
            "task_run_history",
            "zia_resources",
            "zpa_resources",
            "zcc_resources",
            "restore_points",
            "zia_templates",
            "zcc_snapshots",
            "zcc_snapshot_items",
            "sync_logs",
            "audit_logs",
        ]
        for table in expected_tables:
            self.assertIn(table, data, f"Table {table} missing from YAML export")

        # Verify that secrets are redacted
        if "tenant_configs" in data:
            for row in data["tenant_configs"]:
                if "client_secret_enc" in row:
                    self.assertEqual(row["client_secret_enc"], "<REDACTED>")

        if "users" in data:
            for row in data["users"]:
                if "password_hash" in row:
                    self.assertEqual(row["password_hash"], "<REDACTED>")

        if "webauthn_credentials" in data:
            for row in data["webauthn_credentials"]:
                if "public_key" in row:
                    self.assertEqual(row["public_key"], "<REDACTED>")


if __name__ == "__main__":
    unittest.main()
