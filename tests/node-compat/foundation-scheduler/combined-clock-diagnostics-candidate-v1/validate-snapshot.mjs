// Pure validation of an ALREADY DURABLY RETAINED full scalar string. No guest,
// process, helper, native API, module loader, clock or host provider is invoked.
import assert from 'node:assert/strict';
const NAMES = ['queueEnqueue', 'queueDetachRun', 'queueDetachCancel', 'interestIncr', 'interestDecr',
  'selectorCall', 'prunedInvalid', 'selectorEmpty', 'pollCall', 'emptyPollAttempt',
  'timerConstruct', 'timerRetire', 'timerDestroy', 'timerAcquire', 'timerDropAttempt',
  'timerDropReturned', 'hostMonotonicDropAttempt', 'hostMonotonicDropReturned',
  'immediateCacheAcquire', 'immediateCacheUse', 'callEntered', 'loopBoundary', 'postCallBoundary'];
function keys(v, names) { assert.deepEqual(Object.keys(v).sort(), [...names].sort()); }
function u64(v) {
  assert.equal(typeof v, 'string'); assert(/^(0|[1-9][0-9]*)$/.test(v));
  const n = BigInt(v); assert(n <= 18446744073709551615n); return n;
}
function runtime(v) {
  keys(v, ['queued', 'interest', 'loopRunning', 'timerRegistry', 'immediateCacheOwned']);
  u64(v.queued); u64(v.timerRegistry);
  assert(Number.isInteger(v.interest) && v.interest >= 0 && v.interest <= 2147483647);
  assert.equal(typeof v.loopRunning, 'boolean'); assert.equal(typeof v.immediateCacheOwned, 'boolean');
}
function boundary(v, currentSerial, loop) {
  keys(v, ['present', 'callSerial', 'functionIndex', 'runtime', 'loopResultObserved', 'loopReturnedSuccess', 'currentFunction', 'freeListSize']);
  assert.equal(typeof v.present, 'boolean');
  const serial = u64(v.callSerial); assert(u64(v.functionIndex) <= 4294967295n);
  u64(v.freeListSize); runtime(v.runtime);
  assert(Number.isInteger(v.currentFunction));
  assert.equal(typeof v.loopReturnedSuccess, 'boolean');
  // Absent is the genuine zero-initialized POD, not a successful boundary.
  assert.equal(v.loopResultObserved, v.present && loop);
  if (v.present) assert(serial > 0n && serial < currentSerial);
  else { assert.equal(serial, 0n); assert.equal(v.loopReturnedSuccess, false); }
  if (!loop) assert.equal(v.loopReturnedSuccess, false); // explicitly unobserved
}
export function validateSnapshot(raw) {
  assert.equal(typeof raw, 'string'); const v = JSON.parse(raw);
  keys(v, ['schemaVersion', 'diagnosticOnly', 'overflow', 'invariantViolation', 'recordingComplete',
    'hostResourceTableObserved', 'destructionAtHostStoreExitObserved', 'eventSerial',
    'currentCallSerial', 'current', 'afterLoop', 'afterPostCall', 'counters', 'timerLeases']);
  assert.equal(v.schemaVersion, 1); assert.equal(v.diagnosticOnly, true);
  assert.equal(v.overflow, false); assert.equal(v.invariantViolation, false);
  assert.equal(v.recordingComplete, true); // no silent512-row clipping/reuse
  assert.equal(v.hostResourceTableObserved, false); assert.equal(v.destructionAtHostStoreExitObserved, false);
  const event = u64(v.eventSerial), call = u64(v.currentCallSerial);
  runtime(v.current); boundary(v.afterLoop, call, true); boundary(v.afterPostCall, call, false);
  keys(v.counters, NAMES); const c = Object.fromEntries(NAMES.map(n => [n, u64(v.counters[n])]));
  assert.equal(c.callEntered, call);
  assert(c.postCallBoundary <= c.loopBoundary && c.loopBoundary <= call);
  assert.equal(v.afterLoop.present, c.loopBoundary > 0n);
  assert.equal(v.afterPostCall.present, c.postCallBoundary > 0n);
  assert.equal(c.queueEnqueue - c.queueDetachRun - c.queueDetachCancel - c.prunedInvalid, u64(v.current.queued));
  assert.equal(c.interestIncr - c.interestDecr, BigInt(v.current.interest));
  assert.equal(c.emptyPollAttempt, 0n);
  assert(c.immediateCacheAcquire <= 1n);
  assert(c.immediateCacheUse >= c.immediateCacheAcquire);
  assert.equal(v.current.immediateCacheOwned, c.immediateCacheAcquire === 1n);
  assert(Array.isArray(v.timerLeases) && v.timerLeases.length <= 512);
  assert.equal(BigInt(v.timerLeases.length), c.timerAcquire);
  let owned = 0n, attempted = 0n, returned = 0n, previousAcquisition = 0n;
  const recordedEvents = new Set();
  for (let i = 0; i < v.timerLeases.length; i++) {
    const r = v.timerLeases[i];
    keys(r, ['serial', 'timerId', 'acquiredAt', 'invalidatedAt', 'dropAttemptAt', 'dropReturnedAt', 'owned']);
    assert.equal(u64(r.serial), BigInt(i + 1));
    assert(Number.isInteger(r.timerId) && r.timerId > 0 && r.timerId <= 2147483647);
    const acquired = u64(r.acquiredAt), invalidated = u64(r.invalidatedAt),
      attempt = u64(r.dropAttemptAt), ret = u64(r.dropReturnedAt);
    assert(acquired > 0n && acquired <= event); assert.equal(typeof r.owned, 'boolean');
    assert(acquired > previousAcquisition); previousAcquisition = acquired;
    for (const e of [acquired, invalidated, attempt, ret]) if (e) {
      assert(!recordedEvents.has(e)); recordedEvents.add(e);
    }
    if (attempt) { assert(acquired < invalidated && invalidated < attempt && attempt <= event); attempted++; }
    else assert.equal(invalidated, 0n);
    if (ret) { assert(attempt > 0n && attempt < ret && ret <= event); assert.equal(r.owned, false); returned++; }
    else { assert.equal(r.owned, true); owned++; }
  }
  assert.equal(c.timerDropAttempt, attempted); assert.equal(c.timerDropReturned, returned);
  assert.equal(c.timerAcquire - c.timerDropReturned, owned);
  assert(c.timerRetire <= c.timerConstruct && c.timerDestroy <= c.timerConstruct);
  // These are standard drop CALL returns; never host Store destruction counts.
  assert(c.hostMonotonicDropAttempt >= c.timerDropAttempt);
  assert(c.hostMonotonicDropReturned >= c.timerDropReturned);
  assert(c.hostMonotonicDropReturned <= c.hostMonotonicDropAttempt);
  return v;
}
export function requirePreviousTimerBoundary(raw) {
  const v = validateSnapshot(raw), a = v.afterLoop, b = v.afterPostCall;
  assert(a.present && b.present && a.loopReturnedSuccess);
  assert.equal(a.callSerial, b.callSerial); assert.equal(a.functionIndex, b.functionIndex);
  for (const r of [a.runtime, b.runtime]) {
    assert.equal(r.queued, '0'); assert.equal(r.interest, 0);
    assert.equal(r.timerRegistry, '0'); assert.equal(r.loopRunning, false);
  }
  assert.equal(b.currentFunction, -1); assert.equal(b.freeListSize, '0');
  // Cached pollable may remain owned. This check is intentionally timer-only,
  // prior-call quiescence, not full disposal/reset/adoption or host-table proof.
  return v;
}
