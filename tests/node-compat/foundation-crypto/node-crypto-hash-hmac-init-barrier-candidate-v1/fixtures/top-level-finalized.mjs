import { createHash } from 'node:crypto';
// Conservative policy refuses even a context that would be immediately consumed.
createHash('sha256').update('abc').digest('hex');
export function run() { return 'UNEXPECTED_INITIALIZATION_ACCEPTANCE'; }
