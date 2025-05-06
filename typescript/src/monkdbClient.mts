// src/monkdbClient.mts

import { MonkConnection } from '@monkdb/monkdb';
import { config } from './config.mjs';

export function createMonkDBClient() {
    try {
        const connection = new MonkConnection({
            servers: [`http://${config.host}:${config.port}`],
            username: config.user,
            password: config.password,
            schema: config.schema,
        });

        return connection.cursor();
    } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        console.error(`[createMonkDBClient] Failed to connect to MonkDB: ${message}`);
        throw new Error(`MonkDB connection error: ${message}`);
    }
}

