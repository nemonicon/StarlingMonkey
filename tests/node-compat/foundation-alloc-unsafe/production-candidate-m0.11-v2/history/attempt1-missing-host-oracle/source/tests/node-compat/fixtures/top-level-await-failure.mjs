import { exec } from 'node:child_process';
await Promise.resolve().then(() => exec('must-never-start'));
export function run() { return 'unreachable'; }
