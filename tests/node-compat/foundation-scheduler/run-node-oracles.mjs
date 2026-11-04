// Source extraction and small ordinary Node-only oracles. Never componentizes.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
assert.equal(process.version, 'v22.14.0');
const dir = fileURLToPath(new URL('.', import.meta.url));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const run = (filename, args = []) => {
  const child = spawnSync(process.execPath, [dir + filename, ...args], { encoding: 'utf8', timeout: 5000 });
  assert.equal(child.status, 0, child.stderr);
  return JSON.parse(child.stdout);
};
const tickFirst = ['tick-first', 'nested-tick', 'promise-first', 'microtask',
  'promise-from-tick', 'nested-promise', 'tick-from-promise'];
const microtasksFirst = ['promise-first', 'microtask', 'nested-promise',
  'tick-first', 'tick-from-promise', 'nested-tick', 'promise-from-tick'];
const rows = [];
for (const boundary of ['cjs-initial', 'task', 'promise-job']) {
  const actual = run('oracle.cjs', [boundary]);
  const expected = boundary === 'promise-job' ? microtasksFirst : tickFirst;
  assert.deepEqual(actual.trace, expected); rows.push({ ...actual, expected, passed: true });
}
const esm = run('oracle.mjs');
assert.deepEqual(esm.trace, microtasksFirst); rows.push({ ...esm, expected: microtasksFirst, passed: true });
const contracts = run('contracts.cjs');
assert.equal(contracts.returnIsUndefined, true);
assert.deepEqual(contracts.callbacks, [{ receiverUndefined: true, argumentCount: 3,
  objectIdentity: true, symbolIdentity: true, primitive: 17 }]);
assert.equal(contracts.constructedCallbackRan, true);
assert.equal(contracts.publicNodeNextTickConstructible, true);
assert.deepEqual(contracts.invalidCallbacks, Array.from({ length: 6 }, () => ({ name: 'TypeError', code: 'ERR_INVALID_ARG_TYPE' })));
const fatalSource = "process.nextTick(()=>{process.stdout.write('first\\n');throw new Error('SCHEDULER_NODE_FATAL_ORACLE')});process.nextTick(()=>process.stdout.write('second\\n'));";
const fatal = spawnSync(process.execPath, ['-e', fatalSource], { encoding: 'utf8', timeout: 5000 });
assert.equal(fatal.status, 1); assert.equal(fatal.stdout, 'first\n');
assert.match(fatal.stderr, /Error: SCHEDULER_NODE_FATAL_ORACLE/);
await mkdir(new URL('node-source/', import.meta.url), { recursive: true });
// The exact shipped Node binary's source, avoiding a floating branch checkout.
const source = process.binding('natives')['internal/process/task_queues'];
assert.equal(typeof source, 'string');
await writeFile(new URL('node-source/task_queues.node-v22.14.0.js', import.meta.url), source);
const files = ['scenario.cjs', 'oracle.cjs', 'oracle.mjs', 'contracts.cjs',
  'run-node-oracles.mjs', 'node-source/task_queues.node-v22.14.0.js'];
const sources = [];
for (const path of files) { const bytes = await readFile(new URL(path, import.meta.url)); sources.push({ path, sha256: hash(bytes), bytes: bytes.length }); }
const prior = new URL('../foundation-stream/reference-results.json', import.meta.url);
const priorBytes = await readFile(prior);
const report = { schemaVersion: 1, node: process.version,
  nodeBinary: process.execPath, nodeBinarySha256: hash(await readFile(process.execPath)),
  boundaryCases: rows, contracts, fatal: { status: fatal.status, stdout: fatal.stdout,
    expectedMessagePresent: true, stderrSha256: hash(fatal.stderr), source: fatalSource },
  sources, existingSchedulerDriftEvidence: { path: fileURLToPath(prior), sha256: hash(priorBytes),
    scope: 'Prior task/Promise-job Node-versus-Jco traces reused unchanged, not re-executed.' },
  guestExecuted: false, productionSourceChanged: false,
  scope: 'Pinned Node host source/oracles only. No guest queue, embedding ordering, snapshot, or ALS integration pass is claimed.' };
await writeFile(new URL('node-results.json', import.meta.url), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ boundaryCases: rows.length, contracts: true, fatalExit: fatal.status, guestExecuted: false }));
