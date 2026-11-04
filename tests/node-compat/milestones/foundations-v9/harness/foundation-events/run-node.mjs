import assert from 'node:assert/strict';
import * as events from 'node:events';
import * as prototype from './prototype.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { eventsChecks } from './checks.mjs';
assert.equal(process.version, 'v22.14.0');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const oracle = eventsChecks(events), observed = eventsChecks(prototype);
assert.deepEqual(observed, oracle);
const deferred = [];
for (const name of ['on', 'once', 'addAbortListener', 'EventEmitterAsyncResource']) for (const construct of [false, true]) {
  let failure; try { if (construct) new prototype[name](); else prototype[name](); } catch (error) { failure = error; }
  assert.equal(failure?.code, 'ERR_SM_NODE_UNSUPPORTED'); deferred.push({ name, construct, code: failure.code });
}
for (const operation of [() => new prototype.EventEmitter({ captureRejections: true }), () => { prototype.EventEmitter.captureRejections = true; },
  () => prototype.getEventListeners(new EventTarget(), 'x'), () => prototype.getMaxListeners(new EventTarget()), () => prototype.setMaxListeners(2, new EventTarget())]) {
  assert.throws(operation, { code: 'ERR_SM_NODE_UNSUPPORTED' });
}
const e = new prototype.EventEmitter(); e.setMaxListeners(0); const listener = () => {};
for (let i = 0; i < 65536; i++) e.on('x', listener);
assert.throws(() => e.on('x', listener), { code: 'ERR_SM_NODE_LIMIT' }); assert.equal(e.listenerCount('x'), 65536);
const names = new prototype.EventEmitter(); for (let i = 0; i < 4096; i++) names.on('x'+i, listener);
assert.throws(() => names.on('extra', listener), { code: 'ERR_SM_NODE_LIMIT' }); assert.equal(names.eventNames().length, 4096);
const recursive = new prototype.EventEmitter(); recursive.on('x', () => recursive.emit('x'));
assert.throws(() => recursive.emit('x'), { code: 'ERR_SM_NODE_LIMIT' }); recursive.removeAllListeners(); assert.equal(recursive.emit('x'), false);
const source = process.binding('natives').events;
const report = { schema: 1, node: process.version, prototypeInstalledAsBuiltin: false,
  prototypeSha256: hash(await readFile(new URL('./prototype.mjs', import.meta.url))), checksSha256: hash(await readFile(new URL('./checks.mjs', import.meta.url))),
  nodeEmbeddedSourceSha256: hash(source), exports: Object.getOwnPropertyNames(events).sort().map(name => ({ name, type: typeof events[name] })),
  cases: oracle, differentialCasesPassed: oracle.length, deferredCallAndConstructCases: deferred,
  additionalDeferredCasesPassed: 5, resourceLimitsPassed: ['65536 listeners/event', '4096 event names', '64 nested emit entries with unwind recovery'],
  scope: 'Pinned Node host oracle versus isolated JS prototype; no native builtin registration or real component execution established by this report' };
await writeFile(new URL('./node-results.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ passed: oracle.length, deferred: deferred.length+5, limits: 3 }));
