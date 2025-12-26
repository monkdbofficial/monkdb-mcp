import pytest
import concurrent.futures

from mcp_monkdb.mcp_server import run_select_query


# ---------- Helpers / Mocks ----------

def mock_execute_query_returning_rows(row_count):
    return [{"id": i} for i in range(row_count)]


# ---------- Tests ----------

def test_rejects_non_select_query():
    result = run_select_query("DELETE FROM users")
    assert result["status"] == "error"
    assert "Only SELECT queries" in result["message"]


def test_select_within_row_limit(monkeypatch):
    monkeypatch.setattr(
        "mcp_monkdb.mcp_server.execute_query",
        lambda q: mock_execute_query_returning_rows(5),
    )

    result = run_select_query("SELECT * FROM users LIMIT 5")
    assert isinstance(result, list)
    assert len(result) == 5


def test_select_exceeds_hard_row_limit(monkeypatch):
    monkeypatch.setattr(
        "mcp_monkdb.mcp_server.execute_query",
        lambda q: mock_execute_query_returning_rows(1000),
    )

    result = run_select_query("SELECT * FROM users LIMIT 1000")
    assert isinstance(result, list)
    assert len(result) <= 100  # hard cap enforced


def test_select_without_limit_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "mcp_monkdb.mcp_server.execute_query",
        lambda q: mock_execute_query_returning_rows(10),
    )

    result = run_select_query("SELECT * FROM users")
    assert result["status"] == "error"
    assert "LIMIT is required" in result["message"]


def test_query_timeout(monkeypatch):
    def slow_query(_):
        raise concurrent.futures.TimeoutError()

    monkeypatch.setattr(
        "mcp_monkdb.mcp_server.execute_query",
        slow_query,
    )

    result = run_select_query("SELECT * FROM users LIMIT 10")
    assert result["status"] == "error"
    assert "timed out" in result["message"].lower()
