import { getMonkDBConnection } from '../monkdbClient';

export async function describeTable(tableName: string): Promise<any[]> {
    const connection = getMonkDBConnection();
    const cursor = connection.cursor();
    try {
        await cursor.execute(
            `SELECT table_schema, table_name, column_name, data_type, is_nullable, column_default
       FROM information_schema.columns
       WHERE table_schema = ? AND table_name = ?`,
            [connection.options.schema, tableName]
        );
        return cursor.fetchall();
    } finally {
        cursor.close();
    }
}
