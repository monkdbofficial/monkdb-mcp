// src/server.mts

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { createMonkDBClient } from './monkdbClient.mjs';

const server = new McpServer({
    name: 'mcp-monkdb',
    version: '0.1.1',
});

function errorMessage(err: unknown): string {
    return err instanceof Error ? err.message : String(err);
}

// Tool: list_tables
server.tool(
    'list_tables',
    {},
    async () => {
        const cursor = createMonkDBClient();
        try {
            await cursor.execute(`
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = $1
      `, [process.env.MONKDB_SCHEMA || 'monkdb']);

            const rows = cursor.fetchall();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows.map((row: any[]) => row[0]), null, 2),
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error listing tables: ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Tool: run_select_query
server.tool(
    'run_select_query',
    {
        query: z.string(),
    },
    async ({ query }) => {
        if (!query.trim().toLowerCase().startsWith('select')) {
            return {
                content: [
                    {
                        type: 'text',
                        text: 'Only SELECT queries are allowed.',
                    },
                ],
            };
        }

        const cursor = createMonkDBClient();
        try {
            await cursor.execute(query);
            const rows = cursor.fetchall();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows, null, 2),
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Query failed: ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Tool: health_check
server.tool(
    'health_check',
    {},
    async () => {
        const cursor = createMonkDBClient();
        try {
            await cursor.execute('SELECT 1');
            return {
                content: [
                    {
                        type: 'text',
                        text: 'ok',
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Health check failed: ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Tool: get_server_version
server.tool(
    'get_server_version',
    {},
    async () => {
        const cursor = createMonkDBClient();
        try {
            await cursor.execute('SELECT version() AS version');
            const rows = cursor.fetchall();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows, null, 2),
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error retrieving version: ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Tool: describe_table
server.tool(
    'describe_table',
    {
        table_name: z.string(),
    },
    async ({ table_name }) => {
        const cursor = createMonkDBClient();
        try {
            await cursor.execute(`
        SELECT table_schema, table_name, column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = $1 AND table_name = $2
      `, [process.env.MONKDB_SCHEMA || 'monkdb', table_name]);

            const rows = cursor.fetchall();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows, null, 2),
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Failed to describe table "${table_name}": ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Tool: list_schemas
server.tool(
    'list_schemas',
    {},
    async () => {
        const cursor = createMonkDBClient();
        try {
            await cursor.execute('SELECT schema_name FROM information_schema.schemata ORDER BY schema_name');
            const rows = cursor.fetchall();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows.map((row: any[]) => row[0]), null, 2),
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error listing schemas: ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Tool: list_columns
server.tool(
    'list_columns',
    {
        schema_name: z.string().optional().default(process.env.MONKDB_SCHEMA || 'monkdb'),
        table_name: z.string(),
    },
    async ({ schema_name, table_name }) => {
        const cursor = createMonkDBClient();
        try {
            await cursor.execute(`
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = $1 AND table_name = $2
                ORDER BY ordinal_position
            `, [schema_name, table_name]);

            const rows = cursor.fetchall();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows, null, 2),
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Failed to list columns for table "${table_name}" in schema "${schema_name}": ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Tool: list_indexes
server.tool(
    'list_indexes',
    {
        schema_name: z.string().optional().default(process.env.MONKDB_SCHEMA || 'monkdb'),
    },
    async ({ schema_name }) => {
        const cursor = createMonkDBClient();
        try {
            await cursor.execute(`
                SELECT indexname, indexdef
                FROM pg_catalog.pg_indexes
                WHERE schemaname = $1
                ORDER BY indexname
            `, [schema_name]);

            const rows = cursor.fetchall();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows, null, 2),
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Failed to list indexes for schema "${schema_name}": ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Tool: explain_query
server.tool(
    'explain_query',
    {
        query: z.string(),
    },
    async ({ query }) => {
        if (!query.trim().toLowerCase().startsWith('select')) {
            return {
                content: [
                    {
                        type: 'text',
                        text: 'Only SELECT queries are allowed for explain.',
                    },
                ],
            };
        }

        const cursor = createMonkDBClient();
        try {
            await cursor.execute(`EXPLAIN ${query}`);
            const rows = cursor.fetchall();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows, null, 2),
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `EXPLAIN failed: ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Tool: explain_analyze
server.tool(
    'explain_analyze',
    {
        query: z.string(),
    },
    async ({ query }) => {
        if (!query.trim().toLowerCase().startsWith('select')) {
            return {
                content: [
                    {
                        type: 'text',
                        text: 'Only SELECT queries are allowed for explain analyze.',
                    },
                ],
            };
        }

        const cursor = createMonkDBClient();
        try {
            await cursor.execute(`EXPLAIN ANALYZE ${query}`);
            const rows = cursor.fetchall();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows, null, 2),
                    },
                ],
            };
        } catch (err) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `EXPLAIN ANALYZE failed: ${errorMessage(err)}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }
    }
);

// Start the server
export async function startMonkDBMCPServer(): Promise<void> {
    const transport = new StdioServerTransport();
    await server.connect(transport);
}
