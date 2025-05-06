import { getMonkDBConnection } from '../monkdbClient';

export async function listTables(): Promise<string[]> {
    const connection = getMonkDBConnection();
    const cursor = connection.cursor();
    try {
        await cursor.execute(
            `SELECT table_name FROM information_schema.tables WHERE table_schema = ?`,
            [connection.options.schema]
        );
        const rows = cursor.fetchall();
        return rows.map((row) => row[0]);
    } finally {
        cursor.close();
    }
}
