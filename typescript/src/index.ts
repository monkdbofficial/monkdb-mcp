import { FastMCP } from '@modelcontextprotocol/sdk';
import { listTables } from './tools/listTables';
import { runSelectQuery } from './tools/runSelectQuery';
import { healthCheck } from './tools/healthCheck';
import { getServerVersion } from './tools/getServerVersion';
import { describeTable } from './tools/describeTable';

const mcp = new FastMCP('mcp-monkdb');

mcp.registerTool('list_tables', listTables);
mcp.registerTool('run_select_query', runSelectQuery);
mcp.registerTool('health_check', healthCheck);
mcp.registerTool('get_server_version', getServerVersion);
mcp.registerTool('describe_table', describeTable);

mcp.run();
