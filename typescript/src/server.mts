// server.mts

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { createMonkDBClient } from './monkdbClient.mjs';

const server = new McpServer({
    name: 'mcp-monkdb',
    version: '0.1.0',
});

// Tool: list_tables
server.tool(
    'list_tables',
    {},
    async () => {
        const cursor = createMonkDBClient();
        try {
            await cursor.execute(
                `SELECT table_name FROM information_schema.tables WHERE table_schema = $1`,
                [process.env.MONKDB_SCHEMA || 'monkdb']
            );

            const rows = cursor.fetchall();
            cursor.close();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows.map((row: any) => row.table_name)),
                    },
                ],
            };
        } catch (error) {
            console.error('[list_tables] Error:', error);
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error listing tables: ${(error as Error).message}`,
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
            cursor.close();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows),
                    },
                ],
            };
        } catch (error) {
            console.error('[run_select_query] Error:', error);
            return {
                content: [
                    {
                        type: 'text',
                        text: `Query failed: ${(error as Error).message}`,
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
            cursor.close();
            return {
                content: [
                    {
                        type: 'text',
                        text: 'ok',
                    },
                ],
            };
        } catch (error) {
            let message = 'Unknown error';
            if (error instanceof Error) {
                message = error.message;
            }
            return {
                content: [
                    {
                        type: 'text',
                        text: `error: ${message}`,
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
            cursor.close();
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows),
                    },
                ],
            };
        } catch (error) {
            console.error('[get_server_version] Error:', error);
            return {
                content: [
                    {
                        type: 'text',
                        text: `error: ${(error as Error).message}`,
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
            await cursor.execute(
                `SELECT table_schema, table_name, column_name, data_type, is_nullable, column_default
           FROM information_schema.columns
           WHERE table_schema = $1 AND table_name = $2`,
                [process.env.MONKDB_SCHEMA || 'monkdb', table_name]
            );
            const rows = cursor.fetchall();

            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(rows),
                    },
                ],
            };
        } catch (error) {
            console.error(`[describe_table] Error for table ${table_name}:`, error);
            return {
                content: [
                    {
                        type: 'text',
                        text: `Failed to describe table "${table_name}": ${(error as Error).message}`,
                    },
                ],
            };
        } finally {
            cursor.close();
        }

    }
);

// Start the server
const transport = new StdioServerTransport();
await server.connect(transport);
