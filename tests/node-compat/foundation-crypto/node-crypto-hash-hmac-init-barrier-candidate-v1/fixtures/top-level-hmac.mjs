import { createHmac } from 'node:crypto';
createHmac('sha256', Uint8Array.of(1, 2, 3));
export function run() { return 'UNEXPECTED_INITIALIZATION_ACCEPTANCE'; }
