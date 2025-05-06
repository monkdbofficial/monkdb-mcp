import { getMonkDBConnection } from '../monkdbClient';

export async function healthCheck(): Promise<{ status: string }> {
    const connection = getMonkDBConnection();
    const cursor = connection.cursor();
    try {
        await cursor.execute('SELECT 1');
        return { status: 'ok' };
    } catch (error) {
        return { status: 'error', message: (error as Error).message };
    } finally {
        cursor.close();
    }
}
