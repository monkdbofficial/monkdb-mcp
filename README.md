# MonkDB MCP Server

An **MCP (Modular Command Protocol)** server for interacting with MonkDB, enabling Claude to execute database-related tools such as querying, table inspection, and server health checks.

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
      }
    }
  }
}
```

Update the environment variables to point to your own MonkDB cluster.

3. Locate the command entry for `uv` and replace it with the absolute path to the `uv` executable. This ensures that the correct version of `uv` is used when starting the server. On a mac, you can find this path using `which uv`.

4. Restart Claude Desktop to apply the changes.


### Environment Variables

The following environment variables are used to configure the MonkDB connection:

#### Required Variables

* `MONKDB_HOST`: The hostname of your MonkDB server
* `MONKDB_USER`: The username for authentication
* `MONKDB_PASSWORD`: The password for authentication
* `MONKDB_API_PORT`: The API port of MonkDB which is `4200`.

> [!CAUTION]
> It is important to treat your MCP database user as you would any external client connecting to your database, granting only the minimum necessary privileges required for its operation. The use of default or administrative users should be strictly avoided at all times.

#### Optional Variables

* `MONKDB_SCHEMA`: The schema of MonkDB. By default, MonkDB provides a universal schema `monkdb` under which tables are created. Access to these tables are restricted by RBAC policies provided by MonkDB. 

#### Example Configurations

```env
MONKDB_HOST=xx.xx.xx.xxx #update the hostname or ip address of monkdb
MONKDB_USER=testuser
MONKDB_PASSWORD=testpassword
MONKDB_API_PORT=4200

# Not needed as by default it is monkdb.
MONKDB_SCHEMA=monkdb
```

You can set these variables in your environment, in a `.env` file, or in the Claude Desktop configuration:

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
      }
    }
  }
}
```

### Running tests

`cd` in to `mcp_monkdb` folder and then run the below command to execute unit tests.

```bash
python3 -m unittest discover -s tests 
```