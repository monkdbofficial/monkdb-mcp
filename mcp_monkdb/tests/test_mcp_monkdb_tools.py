import os
import unittest
from dotenv import load_dotenv
from mcp_monkdb import create_monkdb_client, list_tables, run_select_query

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.test"))


class TestMonkDBTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = create_monkdb_client()
        cls.test_schema = "monkdb"
        cls.test_table = "test_table"

        # Drop and create test table
        cls.client.execute(
            f"DROP TABLE IF EXISTS {cls.test_schema}.{cls.test_table}")
        cls.client.execute(f"""
            CREATE TABLE {cls.test_schema}.{cls.test_table} (
                id INTEGER,
                name TEXT
            )
        """)
        cls.client.execute(f"""
            INSERT INTO {cls.test_schema}.{cls.test_table} (id, name)
            VALUES (1, 'Alice'), (2, 'Bob')
        """)

    @classmethod
    def tearDownClass(cls):
        cls.client.execute(
            f"DROP TABLE IF EXISTS {cls.test_schema}.{cls.test_table}")

    def test_list_tables(self):
        result = list_tables()
        table_names = [row["table_name"] for row in result]
        self.assertIn(self.test_table, table_names)

    def test_run_select_query_success(self):
        query = f"SELECT * FROM {self.test_schema}.{self.test_table} ORDER BY id"
        result = run_select_query(query)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_run_select_query_failure(self):
        query = f"SELECT * FROM {self.test_schema}.non_existent_table"
        result = run_select_query(query)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "error")
        self.assertIn("Query failed", result["message"])

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
