import dotenv from 'dotenv';

dotenv.config();

export const config = {
    host: process.env.MONKDB_HOST || 'localhost',
    port: parseInt(process.env.MONKDB_API_PORT || '4200', 10),
    user: process.env.MONKDB_USER || '',
    password: process.env.MONKDB_PASSWORD || '',
    schema: process.env.MONKDB_SCHEMA || 'monkdb',
};
