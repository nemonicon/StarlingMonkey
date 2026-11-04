// Import-only profile. Export inventory: Node.js v22.14.0 lib/child_process.js.
import { unavailable, unsupported } from './unsupported.mjs';

export function ChildProcess() { unsupported('node:child_process', 'ChildProcess'); }
export function _forkChild() { unsupported('node:child_process', '_forkChild'); }
export function exec() { unsupported('node:child_process', 'exec'); }
export function execFile() { unsupported('node:child_process', 'execFile'); }
export function execFileSync() { unsupported('node:child_process', 'execFileSync'); }
export function execSync() { unsupported('node:child_process', 'execSync'); }
export function fork() { unsupported('node:child_process', 'fork'); }
export function spawn() { unsupported('node:child_process', 'spawn'); }
export function spawnSync() { unsupported('node:child_process', 'spawnSync'); }

for (const name of ['spawn', 'kill', 'ref', 'unref']) {
  Object.defineProperty(ChildProcess.prototype, name, {
    value: unavailable('node:child_process', `ChildProcess.prototype.${name}`),
    configurable: true, writable: true,
  });
}
Object.defineProperty(ChildProcess.prototype, Symbol.for('nodejs.dispose'), {
  value: unavailable('node:child_process', 'ChildProcess.prototype[Symbol.dispose]'),
  configurable: true, writable: true,
});

// The default object has actual data properties. Namespace inspection is safe.
// A frozen default is a deliberate profile deviation from Node's mutable CJS object.
export default Object.freeze({
  ChildProcess, _forkChild, exec, execFile, execFileSync, execSync, fork, spawn, spawnSync,
});
