import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { createMonkDBClient } from '../src/monkdbClient.mjs';

const testSchema = process.env.MONKDB_SCHEMA || 'monkdb';
const testTable = 'test_table_mcp_ts';

let cursor: any;

beforeAll(async () => {
    cursor = createMonkDBClient();

    // Drop and Create table
    await cursor.execute(`DROP TABLE IF EXISTS ${testSchema}.${testTable}`);
    await cursor.execute(`
    CREATE TABLE ${testSchema}.${testTable} (
      id INTEGER,
      name TEXT
    )
  `);
    await cursor.execute(`REFRESH TABLE ${testSchema}.${testTable}`);
    await cursor.execute(`
    INSERT INTO ${testSchema}.${testTable} (id, name) 
    VALUES (1, 'Alice'), (2, 'Bob')
  `);
});

afterAll(async () => {
    try {
        await cursor.execute(`DROP TABLE IF EXISTS ${testSchema}.${testTable}`);
        cursor.close();
    } catch (err) {
        console.error('[Teardown] Failed to drop test table:', err);
    }
});

describe('MonkDB MCP Server Tools (TS)', () => {
    it('should list tables and include the test table', async () => {
        await cursor.execute(`
      SELECT table_name FROM information_schema.tables 
      WHERE table_schema = $1
    `, [testSchema]);
        const rows = cursor.fetchall();
        const tableNames = rows.map((row: any[]) => row[0].toLowerCase());
        expect(tableNames).toContain(testTable.toLowerCase());
    });

    it('should run SELECT query successfully', async () => {
        const query = `SELECT * FROM ${testSchema}.${testTable} ORDER BY id`;
        await cursor.execute(query);
        const rows = cursor.fetchall();
        expect(rows.length).toBe(2);
        expect(rows[0][0]).toBe(1);
        expect(rows[0][1]).toBe('Alice');
    });

    it('should return error for invalid table in SELECT query', async () => {
        let errorMsg = '';
        try {
            await cursor.execute(`SELECT * FROM ${testSchema}.non_existent_table`);
        } catch (err: any) {
            errorMsg = err.message || '';
        }
        expect(errorMsg).toContain('All servers failed. Last error: MonkDB responded with status 404');
    });

    it('should pass health check with SELECT 1', async () => {
        await cursor.execute('SELECT 1');
        const result = cursor.fetchall();
        expect(result[0][0]).toBe(1);
    });

    it('should fetch MonkDB version', async () => {
        await cursor.execute('SELECT version() AS version');
        const version = cursor.fetchall();
        expect(typeof version[0][0]).toBe('string');
    });

    it('should describe the test table', async () => {
        await cursor.execute(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_schema = $1 AND table_name = $2
    `, [testSchema, testTable]);
        const cols = cursor.fetchall();
        expect(cols.some((c: any[]) => c[0] === 'id')).toBe(true);
        expect(cols.some((c: any[]) => c[0] === 'name')).toBe(true);
    });

    it('should list schemas', async () => {
        await cursor.execute('SELECT schema_name FROM information_schema.schemata ORDER BY schema_name');
        const schemas = cursor.fetchall();
        expect(schemas.length).toBeGreaterThan(0);
        expect(schemas.some((s: any[]) => s[0] === testSchema)).toBe(true);
    });

    it('should list columns for test table', async () => {
        await cursor.execute(`
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
        `, [testSchema, testTable]);
        const cols = cursor.fetchall();
        expect(cols.length).toBe(3);
        expect(cols[0][0]).toBe('id');
        expect(cols[1][0]).toBe('name');
        expect(cols[2][0]).toBe('email');
    });

    it('should list indexes for schema (may be empty for new schema)', async () => {
        await cursor.execute(`
            SELECT indexname, indexdef
            FROM pg_catalog.pg_indexes
            WHERE schemaname = $1
            ORDER BY indexname
        `, [testSchema]);
        const indexes = cursor.fetchall();
        // MonkDB uses automatic Lucene indexing, so this may return empty or system indexes
        expect(Array.isArray(indexes)).toBe(true);
    });

    it('should explain query plan', async () => {
        const explainQuery = `EXPLAIN SELECT * FROM ${testSchema}.${testTable} WHERE id = 1`;
        await cursor.execute(explainQuery);
        const plan = cursor.fetchall();
        expect(Array.isArray(plan)).toBe(true);
        expect(plan.length).toBeGreaterThan(0);
    });

    it('should explain analyze query with actual execution', async () => {
        const explainQuery = `EXPLAIN ANALYZE SELECT * FROM ${testSchema}.${testTable} WHERE id = 1`;
        await cursor.execute(explainQuery);
        const analyzePlan = cursor.fetchall();
        expect(Array.isArray(analyzePlan)).toBe(true);
        expect(analyzePlan.length).toBeGreaterThan(0);
    });
});
