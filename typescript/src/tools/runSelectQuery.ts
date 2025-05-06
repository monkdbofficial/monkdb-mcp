import { getMonkDBConnection } from '../monkdbClient';

export async function runSelectQuery(query: string): Promise<any[]> {
    if (!query.trim().toLowerCase().startsWith('select')) {
        throw new Error('Only SELECT queries are allowed.');
    }

    const connection = getMonkDBConnection();
    const cursor = connection.cursor();
    try {
        await cursor.execute(query);
        return cursor.fetchall();
    } finally {
        cursor.close();
    }
}
