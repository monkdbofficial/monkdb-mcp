import { MonkConnection } from '@monkdb/monkdb';
import { config } from './config';

let connection: MonkConnection | null = null;

export function getMonkDBConnection(): MonkConnection {
    if (!connection) {
        connection = new MonkConnection({
            servers: [`http://${config.host}:${config.port}`],
            username: config.user,
            password: config.password,
            schema: config.schema,
        });
    }
    return connection;
}
