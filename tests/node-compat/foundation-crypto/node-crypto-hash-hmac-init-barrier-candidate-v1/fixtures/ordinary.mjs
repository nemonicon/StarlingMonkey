import { createHash, createHmac } from 'node:crypto';
let calls = 0;
export function run() {
  calls++;
  return JSON.stringify({ calls,
    hash: createHash('sha256').update('abc').digest('hex'),
    hmac: createHmac('sha256', 'Jefe').update('what do ya want for nothing?').digest('hex') });
}
