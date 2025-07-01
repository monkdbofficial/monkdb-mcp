# Official MonkDB MCP Server

![Python](https://img.shields.io/badge/Python-3.13%2B-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Stable](https://img.shields.io/badge/stability-stable-brightgreen) ![Version](https://img.shields.io/badge/version-0.2.1-blue) ![Last Updated](https://img.shields.io/badge/last%20updated-July%2001%202025-brightgreen)

An **MCP (Modular Command Protocol)** server for interacting with MonkDB, enabling Claude like LLMs to execute database-related tools such as querying, table inspection, and server health checks.

> [!CAUTION]
> Treat your MCP database user as you would any external client connecting to your database, granting only the minimum necessary privileges. Avoid using default or admin users in production environments.

## Features

### Tools

- `run_select_query`
    - Execute SQL queries on your MonkDB cluster.
    - Input: `sql` (string): The SQL query to execute.
    - **Rejects non-select queries** 

- `list_tables`
    - List all tables in `monkdb` schema.

- `health_check`
    - Does a health check ping on MonkDB.
    - Returns either `ok` or an error message.

- `get_server_version`
    - Returns the server version of MonkDB.

- `describe_table`
    - Describe a table's columns in MonkDB.

## Configuration

1. Open the Claude Desktop configuration file located at:
    - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
    - On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add the following:

```json
{
  "mcpServers": {
    "mcp-monkdb": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp-monkdb",
        "--python",
        "3.13",
        "mcp-monkdb"
      ],
      "env": {
        "MONKDB_HOST": "<monkdb-host>",
        "MONKDB_API_PORT": "<monkdb-port>",
        "MONKDB_USER": "<monkdb-user>",
        "MONKDB_PASSWORD": "<monkdb-password>",

        // Optional OTEL Configuration
        "MONKDB_OTEL_ENABLED": "true",
        "MONKDB_OTEL_EXPORTER_OTLP_ENDPOINT": "https://your-otel-endpoint:4318",
        "MONKDB_OTEL_SERVICE_NAME": "mcp-monkdb",
        "MONKDB_OTEL_AUTH_HEADER": "Authorization=Bearer your-token-here"
      }
    }
  }
}
```

Update the environment variables to point to your own MonkDB cluster.

3. Locate the command entry for `uv` and replace it with the absolute path to the `uv` executable. This ensures that the correct version of `uv` is used when starting the server. On a mac, you can find this path using `which uv`.

4. Restart Claude Desktop to apply the changes.

**Note**: you may also use `poetry` instead of `uv`.

```json
{
  "mcpServers": {
    "mcp-monkdb": {
      "command": "poetry",
      "args": [
        "run",
        "python",
        "-m",
        "mcp_monkdb"
      ],
      "env": {
        "MONKDB_HOST": "<monkdb-host>",
        "MONKDB_API_PORT": "<monkdb-port>",
        "MONKDB_USER": "<monkdb-user>",
        "MONKDB_PASSWORD": "<monkdb-password>",

        // Optional OTEL Configuration
        "MONKDB_OTEL_ENABLED": "true",
        "MONKDB_OTEL_EXPORTER_OTLP_ENDPOINT": "https://your-otel-endpoint:4318",
        "MONKDB_OTEL_SERVICE_NAME": "mcp-monkdb",
        "MONKDB_OTEL_AUTH_HEADER": "Authorization=Bearer your-token-here"
      }
    }
  }
}
```


### Environment Variables

The following environment variables are used to configure the MonkDB connection and optional OpenTelemetry (OTEL) tracing.

#### Required Variables

- `MONKDB_HOST`: The hostname or IP address of your MonkDB server.
- `MONKDB_USER`: The username for authentication.
- `MONKDB_PASSWORD`: The password for authentication.
- `MONKDB_API_PORT`: The API port of MonkDB (default is `4200`).

#### Optional Variables

- `MONKDB_SCHEMA`: The schema of MonkDB. Defaults to `monkdb`. Tables under this schema are protected by RBAC policies.

#### Optional OTEL Tracing Variables

To enable distributed tracing using OpenTelemetry:

- `MONKDB_OTEL_ENABLED`: Set to `true` to enable tracing.
- `MONKDB_OTEL_EXPORTER_OTLP_ENDPOINT`: The OTLP HTTP endpoint (e.g. `http://localhost:4318` or `https://your-collector.com:4318`).
- `MONKDB_OTEL_SERVICE_NAME`: Logical name for trace viewers (e.g., `mcp-monkdb`).
- `MONKDB_OTEL_AUTH_HEADER`: (Optional) Auth header if your OTEL collector requires it.  
  Format: `Authorization=Bearer <token>` or `api-key=XYZ123`.

> **Note**  
> If you're using a local OTEL collector with no auth, `MONKDB_OTEL_AUTH_HEADER` can be omitted.

#### Example `.env` Configuration

```env
MONKDB_HOST=xx.xx.xx.xxx
MONKDB_USER=testuser
MONKDB_PASSWORD=testpassword
MONKDB_API_PORT=4200
MONKDB_SCHEMA=monkdb

# OpenTelemetry tracing (optional)
MONKDB_OTEL_ENABLED=true
MONKDB_OTEL_EXPORTER_OTLP_ENDPOINT=https://my-otel-collector:4318
MONKDB_OTEL_SERVICE_NAME=mcp-monkdb
MONKDB_OTEL_AUTH_HEADER=Authorization=Bearer xyz123
```

These can also be configured directly inside your Claude Desktop config:

```json
{
  "mcpServers": {
    "mcp-monkdb": {
      "command": "poetry",
      "args": ["run", "python", "-m", "mcp_monkdb"],
      "env": {
        "MONKDB_HOST": "<monkdb-host>",
        "MONKDB_API_PORT": "<monkdb-port>",
        "MONKDB_USER": "<monkdb-user>",
        "MONKDB_PASSWORD": "<monkdb-password>",
        "MONKDB_OTEL_ENABLED": "true",
        "MONKDB_OTEL_EXPORTER_OTLP_ENDPOINT": "https://your-otel-host:4318",
        "MONKDB_OTEL_SERVICE_NAME": "mcp-monkdb",
        "MONKDB_OTEL_AUTH_HEADER": "Authorization=Bearer your-token"
      }
    }
  }
}
```

#### Traced Operations

| Operation           | ToolTraced? | Captured Attributes                                  |
|---------------------|:-----------:|------------------------------------------------------|
| run_select_query    | ✅          | `monkdb.query`, `monkdb.query.type` (select), `monkdb.query.rows`, `status` |


### Running tests

`cd` in to `mcp_monkdb` folder and then run the below command to execute unit tests.

```bash
python3 -m unittest discover -s tests 
```