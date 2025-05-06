// monkdbClient.mts

import { MonkConnection } from '@monkdb/monkdb';
import { config } from './config.mjs';

export function createMonkDBClient() {
    const connection = new MonkConnection({
        servers: [`http://${config.host}:${config.port}`],
        username: config.user,
        password: config.password,
        schema: config.schema,
    });

    return connection.cursor();
}
