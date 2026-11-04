import { spawn } from '../templates/child-process.mjs';
spawn('never-executed');
export function run() { return 'unreachable'; }
