import { getMonkDBConnection } from '../monkdbClient';

export async function getServerVersion(): Promise<string> {
    const connection = getMonkDBConnection();
    const cursor = connection.cursor();
    try {
        await cursor.execute('SELECT version() AS version');
        const rows = cursor.fetchall();
        return rows[0][0];
    } finally {
        cursor.close();
    }
}
