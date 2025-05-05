import os
import unittest
from venv import logger
from dotenv import load_dotenv
from mcp_monkdb import create_monkdb_client, list_tables, run_select_query

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.test"))


class TestMonkDBTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test schema and table in MonkDB."""
        cls.client = create_monkdb_client()
        cls.test_schema = "monkdb"
        cls.test_table = "test_table"

        # Drop table if exists
        cls.client.execute(
            f"DROP TABLE IF EXISTS {cls.test_schema}.{cls.test_table}")

        # Create test table
        cls.client.execute(f"""
            CREATE TABLE {cls.test_schema}.{cls.test_table} (
                id INTEGER,
                name TEXT
            )
        """)

        cls.client.execute(
            f"""REFRESH TABLE {cls.test_schema}.{cls.test_table}""")

        # Insert test data
        cls.client.execute(f"""
            INSERT INTO {cls.test_schema}.{cls.test_table} (id, name)
            VALUES (1, 'Alice'), (2, 'Bob')
        """)
        logger.info("Test table and data set up successfully.")

    @classmethod
    def tearDownClass(cls):
        """Clean up the test table."""
        try:
            cls.client.execute(f"DROP TABLE IF EXISTS monkdb.{cls.test_table}")
            logger.info("Test table dropped.")
        except Exception as e:
            logger.error(f"Teardown failed: {e}")

    def test_list_tables(self):
        """Test that test_table appears in the list of tables."""
        result = list_tables()

        self.assertNotIn("status", result, f"Error in list_tables: {result}")
        self.assertIsInstance(
            result, list, f"Expected list, got: {type(result)}")

        # FIX: handle dicts
        table_names = [
            row["table_name"].lower()
            for row in result
            if isinstance(row, dict) and "table_name" in row
        ]
        print("Returned tables:", table_names)

        self.assertIn(self.test_table.lower(), table_names)

    def test_run_select_query_success(self):
        """Test running a SELECT query successfully."""
        query = f"SELECT * FROM {self.test_schema}.{self.test_table} ORDER BY id"
        result = run_select_query(query)

        self.assertIsInstance(result, list, f"Query failed: {result}")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_run_select_query_failure(self):
        """Test SELECT query on non-existent table returns proper error structure."""
        query = f"SELECT * FROM {self.test_schema}.non_existent_table"
        result = run_select_query(query)

        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "error")
        self.assertIn("Query failed", result.get("message", ""))

    def test_health_check(self):
        try:
            cursor = create_monkdb_client()
            cursor.execute("SELECT 1")
            status = "ok"
        except Exception:
            status = "error"
        self.assertEqual(status, "ok")


if __name__ == "__main__":
    unittest.main()
