import { exec } from 'node:child_process';
export function run() {
  try { exec('framework-probe-must-never-spawn'); return JSON.stringify({ unexpectedSuccess: true }); }
  catch (error) { return JSON.stringify({ observedRefusal: true, code: error.code,
    name: error.name, message: error.message, callbackProvided: false, callbackInvocationObserved: false }); }
}
