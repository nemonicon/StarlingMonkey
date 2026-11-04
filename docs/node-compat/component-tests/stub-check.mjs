import childProcess, * as childProcessNamespace from '../templates/child-process.mjs';

const names = ['ChildProcess', '_forkChild', 'exec', 'execFile', 'execFileSync', 'execSync', 'fork', 'spawn', 'spawnSync'];
let calls = 0;
const snapshotMarker = 'created-during-initialization';
function assert(value, message) { if (!value) throw new Error(message); }
export async function run() {
  assert(JSON.stringify(Object.keys(childProcessNamespace).sort()) === JSON.stringify([...names, 'default'].sort()), 'namespace inventory');
  assert(childProcessNamespace.default === childProcess, 'default identity');
  assert(childProcess.then === undefined && Reflect.get(childProcessNamespace, 'then') === undefined, 'non-thenable namespace');
  assert(await Promise.resolve(childProcessNamespace) === childProcessNamespace, 'safe Promise resolution');
  let invocationChecks = 0;
  let constructorChecks = 0;
  for (const name of names) {
    assert(childProcessNamespace[name] === childProcess[name], 'named/default identity: ' + name);
    assert(typeof childProcess[name] === 'function', 'callable: ' + name);
    for (const construct of [false, true]) {
      try {
        if (construct) new childProcess[name](); else childProcess[name]();
        throw new Error('operation unexpectedly returned');
      } catch (error) {
        assert(error.code === 'ERR_SM_NODE_UNSUPPORTED', 'error identity: ' + name);
        assert(error.module === 'node:child_process' && error.operation === name, 'error attribution');
        if (construct) constructorChecks++; else invocationChecks++;
      }
    }
  }
  return JSON.stringify({ snapshotMarker, calls: ++calls, invocationChecks, constructorChecks, exports: Object.keys(childProcessNamespace).sort() });
}
