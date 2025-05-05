import atexit
from dataclasses import asdict, dataclass, field, is_dataclass
import json
import logging
from typing import Any, List, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from monkdb import client

import concurrent

from mcp_monkdb.env_vals import get_config


@dataclass
class Column:
    database: str
    table: str
    name: str
    column_type: str
    default_kind: Optional[str]
    default_expression: Optional[str]
    comment: Optional[str]


@dataclass
class Table:
    database: str
    name: str
    engine: str
    create_table_query: str
    dependencies_database: str
    dependencies_table: str
    engine_full: str
    sorting_key: str
    primary_key: str
    total_rows: int
    total_bytes: int
    total_bytes_uncompressed: int
    parts: int
    active_parts: int
    total_marks: int
    comment: Optional[str] = None
    columns: List[Column] = field(default_factory=list)


MCP_SERVER_NAME = "mcp-monkdb"

# Configure logging for mcp server operations
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

QUERY_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=10)
atexit.register(lambda: QUERY_EXECUTOR.shutdown(wait=True))
SELECT_QUERY_TIMEOUT_SECS = 30


load_dotenv()

deps = [
    "monkdb",
    "python-dotenv",
    "uvicorn",
    "pip-system-certs",
]

mcp = FastMCP(MCP_SERVER_NAME, dependencies=deps)


def result_to_table(query_columns, result) -> List[Table]:
    return [Table(**dict(zip(query_columns, row))) for row in result]


def result_to_column(query_columns, result) -> List[Column]:
    return [Column(**dict(zip(query_columns, row))) for row in result]


def to_json(obj: Any) -> str:
    if is_dataclass(obj):
        return json.dumps(asdict(obj), default=to_json)
    elif isinstance(obj, list):
        return [to_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: to_json(value) for key, value in obj.items()}
    return obj


@mcp.tool()
def list_tables():
    """List available MonkDB tables under monkdb schema"""
    logger.info("Listing all tables")
    cursor = create_monkdb_client()
    result = cursor.execute(f"""
        SELECT table_name FROM information_schema.tables where table_schema = 'monkdb';""")
    logger.info(
        f"Found {len(result) if isinstance(result, list) else 1} tables")
    return result


def execute_query(query: str):
    cursor = create_monkdb_client()
    try:
        res = cursor.execute(query)
        column_names = res.column_names
        rows = []
        for row in res.result_rows:
            row_dict = {}
            for i, col_name in enumerate(column_names):
                row_dict[col_name] = row[i]
            rows.append(row_dict)
        logger.info(f"Query returned {len(rows)} rows")
        return rows
    except Exception as err:
        logger.error(f"Error executing query: {err}")
        # Return a structured dictionary rather than a string to ensure proper serialization
        # by the MCP protocol. String responses for errors can cause BrokenResourceError.
        return {"error": str(err)}


@mcp.tool()
def run_select_query(query: str):
    """Run a SELECT query in a MonkDB database"""
    logger.info(f"Executing SELECT query: {query}")

    # Enforce SELECT-only query for safety
    if not query.strip().lower().startswith("select"):
        logger.warning("Rejected non-SELECT query")
        return {
            "status": "error",
            "message": "Only SELECT queries are allowed in this endpoint.",
        }

    try:
        future = QUERY_EXECUTOR.submit(execute_query, query)
        try:
            result = future.result(timeout=SELECT_QUERY_TIMEOUT_SECS)

            if isinstance(result, dict) and "error" in result:
                logger.warning(f"Query failed: {result['error']}")
                return {
                    "status": "error",
                    "message": f"Query failed: {result['error']}",
                }

            return result
        except concurrent.futures.TimeoutError:
            logger.warning(
                f"Query timed out after {SELECT_QUERY_TIMEOUT_SECS} seconds: {query}"
            )
            future.cancel()
            return {
                "status": "error",
                "message": f"Query timed out after {SELECT_QUERY_TIMEOUT_SECS} seconds",
            }
    except Exception as e:
        logger.error(f"Unexpected error in run_select_query: {str(e)}")
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}


@mcp.tool()
def health_check():
    """Simple health check on MonkDB"""
    try:
        cursor = create_monkdb_client()
        cursor.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_server_version():
    """Returns the version of MonkDB server"""
    cursor = create_monkdb_client()
    result = cursor.execute("select version() AS version")
    return result


def create_monkdb_client():
    config = get_config().get_client_config()
    try:
        connection = client.connect(config["url"], username=config["username"])
        logger.info("MonkDB connection established successfully!")
        return connection.cursor()
    except Exception as e:
        logger.error(f"Failed to connect to MonkDB: {str(e)}")
        raise
