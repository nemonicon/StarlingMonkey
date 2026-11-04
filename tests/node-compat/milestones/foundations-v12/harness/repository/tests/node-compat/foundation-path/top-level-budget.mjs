import { matchesGlob } from 'node:path';
matchesGlob('x', '{1..10000000}');
export function run() { return 'unreachable'; }
