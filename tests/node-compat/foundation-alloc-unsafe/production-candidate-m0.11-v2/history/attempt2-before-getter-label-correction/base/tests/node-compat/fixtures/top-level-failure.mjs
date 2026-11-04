import { spawn } from 'child_process';
spawn('must-never-start');
export function run() { return 'unreachable'; }
