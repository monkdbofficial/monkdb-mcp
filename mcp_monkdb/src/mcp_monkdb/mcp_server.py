import atexit
from dataclasses import asdict, dataclass, field, is_dataclass
import json
import logging
from typing import Any, List
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from monkdb import client

import concurrent

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from mcp_monkdb.env_vals import get_config
from mcp_monkdb.models import Column, Table

tracer = trace.get_tracer(__name__)

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


def result_to_column(query_columns, result) -> List[Column]:
    return [Column(**dict(zip(query_columns, row))) for row in result]


def result_to_table(query_columns, result) -> List[Table]:
    return [Table(**dict(zip(query_columns, row))) for row in result]


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
    with tracer.start_as_current_span("list_tables"):
        logger.info("Listing all tables")
        try:
            cursor = create_monkdb_client()
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'monkdb';
            """)
            rows = cursor.fetchall()
            if not rows:
                raise ValueError("No tables found in schema 'monkdb'")

            return [{"table_name": row[0]} for row in rows]
        except Exception as e:
            trace.get_current_span().record_exception(e)
            trace.get_current_span().set_status(Status(StatusCode.ERROR, str(e)))
            logger.error(f"Failed to list tables: {str(e)}")
            return {"status": "error", "message": str(e)}


def execute_query(query: str):
    cursor = create_monkdb_client()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        result = []
        for row in rows:
            result.append(
                {column_names[i]: value for i, value in enumerate(row)})

        logger.info(f"Query returned {len(result)} rows")
        return result

    except Exception as err:
        logger.error(f"Error executing query: {err}")
        return {"status": "error", "message": f"Query failed: {str(err)}"}


@mcp.tool()
def run_select_query(query: str):
    """Run a SELECT query in a MonkDB database"""
    with tracer.start_as_current_span("run_select_query") as span:
        span.set_attribute("monkdb.query", query.strip())
        span.set_attribute("monkdb.query.type", "select")
        logger.info(f"Executing SELECT query: {query}")

        if not query.strip().lower().startswith("select"):
            msg = "Only SELECT queries are allowed in this endpoint."
            span.set_status(Status(StatusCode.ERROR, msg))
            return {"status": "error", "message": msg}

        try:
            future = QUERY_EXECUTOR.submit(execute_query, query)
            result = future.result(timeout=SELECT_QUERY_TIMEOUT_SECS)

            if isinstance(result, dict) and "error" in result:
                span.set_status(Status(StatusCode.ERROR, result["error"]))
                return {"status": "error", "message": result["error"]}

            span.set_status(Status(StatusCode.OK))
            span.set_attribute("monkdb.query.rows", len(result))
            return result

        except concurrent.futures.TimeoutError:
            msg = f"Query timed out after {SELECT_QUERY_TIMEOUT_SECS} seconds"
            span.set_status(Status(StatusCode.ERROR, msg))
            return {"status": "error", "message": msg}

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
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
    """Returns the version of MonkDB server using version() scalar function"""
    cursor = create_monkdb_client()
    result = cursor.execute("SELECT version() AS version")
    return result


@mcp.tool()
def describe_table(table_name: str):
    """Describe a table's columns in MonkDB"""
    cursor = create_monkdb_client()
    try:
        query = """
            SELECT table_schema, table_name, column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'monkdb' AND table_name = %s;
        """
        cursor.execute(query, (table_name,))
        rows = cursor.fetchall()
        if not rows:
            raise ValueError(f"No columns found for table: {table_name}")

        query_columns = [desc[0] for desc in cursor.description]
        return result_to_column(query_columns, rows)

    except Exception as e:
        logger.error(f"Failed to describe table '{table_name}': {str(e)}")
        return {"status": "error", "message": str(e)}


def create_monkdb_client():
    config = get_config().get_client_config()
    try:
        connection = client.connect(config["url"], username=config["username"])
        logger.info("MonkDB connection established successfully!")
        return connection.cursor()
    except Exception as e:
        logger.error(f"Failed to connect to MonkDB: {str(e)}")
        raise
