// Pure host DATA only, after complete typed strings/terminals have been durable.
// No guest/private builtin, clock, process, native helper or fixture imported.
import assert from 'node:assert/strict';
import {validateSnapshot, requirePreviousTimerBoundary} from '../combined-clock-diagnostics-candidate-v1/validate-snapshot.mjs';
import {validateResourceInspect, validateResourceRun, validateResourceWrapper,
  validateClockSnapshot, validateSurvivingInterest} from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';
export const CASE_NATIVE = Object.freeze([
  {construct: 2, acquire: 2, run: 2, cancel: 0},
  {construct: 2, acquire: 2, run: 1, cancel: 1},
  {construct: 2, acquire: 4, run: 4, cancel: 0},
  {construct: 3, acquire: 3, run: 2, cancel: 1},
  {construct: 2, acquire: 2, run: 2, cancel: 0},
  {construct: 2, acquire: 2, run: 2, cancel: 0},
  {construct: 33, acquire: 33, run: 1, cancel: 32},
]);
const keys = (v, names) => assert.deepEqual(Object.keys(v).sort(), [...names].sort());
const parse = raw => { assert.equal(typeof raw, 'string'); return JSON.parse(raw); };
const decimal = s => { assert.equal(typeof s, 'string'); assert(/^(0|[1-9][0-9]*)$/.test(s)); return BigInt(s); };
export function requireNativeDelta(beforeRaw, afterRaw, expected) {
  const before = validateSnapshot(beforeRaw), after = validateSnapshot(afterRaw);
  // Same outer export: prior completed boundary is unchanged. No host call slipped in.
  assert.equal(before.currentCallSerial, after.currentCallSerial);
  assert.deepEqual(before.afterLoop, after.afterLoop); assert.deepEqual(before.afterPostCall, after.afterPostCall);
  for (const v of [before, after]) {
    assert.equal(v.current.queued, '0'); assert.equal(v.current.timerRegistry, '0');
    assert.equal(v.current.interest, 1); // genuine embedding's current export promise
    assert(v.timerLeases.every(r => r.owned === false));
  }
  assert.equal(after.current.loopRunning, true); // after awaited callback/Promise checkpoint
  const delta = Object.fromEntries(Object.keys(before.counters).map(name => {
    const d = decimal(after.counters[name]) - decimal(before.counters[name]); assert(d >= 0n); return [name, d];
  }));
  const e = expected; keys(e, ['construct', 'acquire', 'run', 'cancel']);
  for (const n of Object.values(e)) assert(Number.isSafeInteger(n) && n >= 0 && n <= 512);
  assert.equal(e.acquire, e.run + e.cancel);
  const wanted = {queueEnqueue: e.acquire, queueDetachRun: e.run, queueDetachCancel: e.cancel,
    interestIncr: 0, interestDecr: 0, selectorCall: e.run, prunedInvalid: 0, selectorEmpty: 0,
    pollCall: e.run, emptyPollAttempt: 0, timerConstruct: e.construct, timerRetire: e.construct,
    timerDestroy: e.construct, timerAcquire: e.acquire, timerDropAttempt: e.acquire,
    timerDropReturned: e.acquire, hostMonotonicDropAttempt: e.acquire,
    hostMonotonicDropReturned: e.acquire, immediateCacheAcquire: 0, immediateCacheUse: 0,
    callEntered: 0, loopBoundary: 0, postCallBoundary: 0};
  keys(delta, Object.keys(wanted));
  for (const [name, n] of Object.entries(wanted)) assert.equal(delta[name], BigInt(n), 'native delta:' + name);
  assert.equal(decimal(after.eventSerial) - decimal(before.eventSerial), 4n * BigInt(e.acquire));
  assert.equal(after.timerLeases.length - before.timerLeases.length, e.acquire);
  assert.deepEqual(after.timerLeases.slice(0, before.timerLeases.length), before.timerLeases);
  assert.equal(after.current.immediateCacheOwned, before.current.immediateCacheOwned);
  return {before, after, delta};
}
export function collectResourceInspect(raw) {
  const v = parse(raw); keys(v, ['schemaVersion', 'kind', 'resourceRaw', 'nativeRaw']);
  assert.equal(v.schemaVersion, 1); assert.equal(v.kind, 'private-resource-inspect-v1');
  return {record: v, resource: validateResourceInspect(v.resourceRaw), native: validateSnapshot(v.nativeRaw)};
}
function bindTimerIds(native, ids) {
  assert.deepEqual(native.after.timerLeases.slice(native.before.timerLeases.length).map(r => r.timerId), ids);
}
function acquisitionIds(resource) {
  const ids = resource.after.registeredIds.slice(resource.before.registeredIds.length);
  return resource.caseId === 2 ? [ids[0], ids[0], ids[0], ids[1]] : ids;
}
export function collectResourceRun(raw, caseId) {
  assert(Number.isInteger(caseId) && caseId >= 0 && caseId < 7);
  const v = parse(raw); keys(v, ['schemaVersion', 'kind', 'caseId', 'resourceRaw', 'beforeNativeRaw', 'afterNativeRaw']);
  assert.equal(v.schemaVersion, 1); assert.equal(v.kind, 'private-resource-run-v1'); assert.equal(v.caseId, caseId);
  const resource = validateResourceRun(v.resourceRaw, caseId);
  const native = requireNativeDelta(v.beforeNativeRaw, v.afterNativeRaw, CASE_NATIVE[caseId]);
  bindTimerIds(native, acquisitionIds(resource)); return {record: v, resource, native};
}
export function collectResourceWrapper(raw) {
  const v = parse(raw); keys(v, ['schemaVersion', 'kind', 'resourceRaw', 'beforeNativeRaw', 'afterNativeRaw']);
  assert.equal(v.schemaVersion, 1); assert.equal(v.kind, 'private-resource-wrapper-v1');
  const e = CASE_NATIVE.reduce((a, r) => Object.fromEntries(Object.keys(a).map(k => [k, a[k] + r[k]])), {construct: 0, acquire: 0, run: 0, cancel: 0});
  const resource = validateResourceWrapper(v.resourceRaw); const native = requireNativeDelta(v.beforeNativeRaw, v.afterNativeRaw, e);
  bindTimerIds(native, resource.records.flatMap(acquisitionIds)); return {record: v, resource, native};
}
export function collectClock(raw, previousClock = null) {
  const v = parse(raw); keys(v, ['schemaVersion', 'kind', 'clockRaw', 'beforeNativeRaw', 'afterNativeRaw']);
  assert.equal(v.schemaVersion, 1); assert.equal(v.kind, 'private-clock-observation-v1');
  return {record: v, clock: validateClockSnapshot(v.clockRaw, previousClock),
    native: requireNativeDelta(v.beforeNativeRaw, v.afterNativeRaw, {construct: 1, acquire: 1, run: 1, cancel: 0}), nativeOffsetObserved: false};
}
export function collectSurvivor(raw) {
  const v = parse(raw); keys(v, ['schemaVersion', 'kind', 'survivorRaw', 'beforeNativeRaw', 'afterNativeRaw']);
  assert.equal(v.schemaVersion, 1); assert.equal(v.kind, 'private-survivor-observation-v1');
  const survivor = validateSurvivingInterest(v.survivorRaw); const native = requireNativeDelta(v.beforeNativeRaw, v.afterNativeRaw, {construct: 11, acquire: 11, run: 3, cancel: 8});
  bindTimerIds(native, survivor.ids); return {record: v, survivor, native, allInvalidSelectorExercised: false};
}
export function requireNextExportBoundary(previousAfterRaw, nextSnapshotRaw, actualPreviousFunctionIndex) {
  assert(Number.isInteger(actualPreviousFunctionIndex) && actualPreviousFunctionIndex >= 0 && actualPreviousFunctionIndex <= 4294967295);
  const previous = validateSnapshot(previousAfterRaw), next = requirePreviousTimerBoundary(nextSnapshotRaw);
  assert.equal(decimal(next.currentCallSerial), decimal(previous.currentCallSerial) + 1n);
  for (const b of [next.afterLoop, next.afterPostCall]) {
    assert.equal(b.callSerial, previous.currentCallSerial);
    assert.equal(b.functionIndex, String(actualPreviousFunctionIndex));
  }
  for (const [name, n] of Object.entries({callEntered: 1n, loopBoundary: 1n, postCallBoundary: 1n, interestIncr: 1n, interestDecr: 1n}))
    assert.equal(decimal(next.counters[name]) - decimal(previous.counters[name]), n);
  // This new observer export has its own interest; prior completed call has zero.
  assert.equal(next.current.interest, 1); assert.equal(next.current.queued, '0'); assert.equal(next.current.timerRegistry, '0');
  assert.deepEqual(next.timerLeases, previous.timerLeases);
  return {next, timerBoundaryObserved: true, hostStoreDeathObserved: false, cachedImmediateDisposalObserved: false};
}
// A requirement, not an executable all-invalid fixture or a passing approximation.
export function requireAllInvalidEvidence(beforeRaw, afterRaw) {
  const a = validateSnapshot(beforeRaw), b = validateSnapshot(afterRaw);
  assert(decimal(b.counters.prunedInvalid) > decimal(a.counters.prunedInvalid), 'No native invalid queued task was observed');
  assert(decimal(b.counters.selectorEmpty) > decimal(a.counters.selectorEmpty), 'No native all-pruned selection observed');
  assert.equal(b.counters.emptyPollAttempt, a.counters.emptyPollAttempt);
  return {observedPruningOnly: true, constructibleWithSnapshotOnlyApi: false, fullGateAccepted: false};
}
