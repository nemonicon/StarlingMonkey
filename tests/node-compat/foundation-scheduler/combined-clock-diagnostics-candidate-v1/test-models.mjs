// Synthetic plain DATA, not native execution or a compiler check.
import assert from 'node:assert/strict';
import {validateSnapshot, requirePreviousTimerBoundary} from './validate-snapshot.mjs';
const names = ['queueEnqueue', 'queueDetachRun', 'queueDetachCancel', 'interestIncr', 'interestDecr',
  'selectorCall', 'prunedInvalid', 'selectorEmpty', 'pollCall', 'emptyPollAttempt',
  'timerConstruct', 'timerRetire', 'timerDestroy', 'timerAcquire', 'timerDropAttempt',
  'timerDropReturned', 'hostMonotonicDropAttempt', 'hostMonotonicDropReturned',
  'immediateCacheAcquire', 'immediateCacheUse', 'callEntered', 'loopBoundary', 'postCallBoundary'];
const runtime = {queued: '0', interest: 0, loopRunning: false, timerRegistry: '0', immediateCacheOwned: false};
const boundary = {present: true, callSerial: '1', functionIndex: '0', runtime: structuredClone(runtime),
  loopResultObserved: true, loopReturnedSuccess: true, currentFunction: 0, freeListSize: '1'};
const valid = {schemaVersion: 1, diagnosticOnly: true, overflow: false, invariantViolation: false,
  recordingComplete: true, hostResourceTableObserved: false, destructionAtHostStoreExitObserved: false,
  eventSerial: '4', currentCallSerial: '2', current: {...runtime, interest: 1},
  afterLoop: boundary, afterPostCall: {...structuredClone(boundary), loopResultObserved: false,
    loopReturnedSuccess: false, currentFunction: -1, freeListSize: '0'},
  counters: Object.fromEntries(names.map(n => [n, '0'])),
  timerLeases: [{serial: '1', timerId: 1, acquiredAt: '1', invalidatedAt: '2',
    dropAttemptAt: '3', dropReturnedAt: '4', owned: false}]};
Object.assign(valid.counters, {queueEnqueue: '1', queueDetachRun: '1', interestIncr: '2', interestDecr: '1',
  timerConstruct: '1', timerRetire: '1', timerDestroy: '1', timerAcquire: '1', timerDropAttempt: '1',
  timerDropReturned: '1', hostMonotonicDropAttempt: '1', hostMonotonicDropReturned: '1',
  callEntered: '2', loopBoundary: '1', postCallBoundary: '1'});
let checks = 0;
function pass(f) { f(); checks++; }
function bad(change, fn = validateSnapshot) {
  pass(() => {const v = structuredClone(valid); change(v); assert.throws(() => fn(JSON.stringify(v)));});
}
pass(() => validateSnapshot(JSON.stringify(valid)));
pass(() => requirePreviousTimerBoundary(JSON.stringify(valid)));
// Current getter/export interest is1; the previous completed boundary is0.
pass(() => assert.equal(requirePreviousTimerBoundary(JSON.stringify(valid)).current.interest, 1));
bad(v => v.overflow = true);
bad(v => v.invariantViolation = true);
bad(v => v.recordingComplete = false);
bad(v => v.timerLeases.pop());
bad(v => v.timerLeases.push(structuredClone(v.timerLeases[0])));
bad(v => v.timerLeases[0].serial = '2');
bad(v => v.timerLeases[0].privateHandle = 4);
bad(v => v.timerLeases[0].dropAttemptAt = '1');
bad(v => v.timerLeases[0].invalidatedAt = '3');
bad(v => v.timerLeases[0].dropReturnedAt = '3');
bad(v => v.timerLeases[0].owned = true);
bad(v => v.counters.timerAcquire = '2');
bad(v => v.counters.timerDropReturned = '0');
bad(v => v.counters.queueEnqueue = '2');
bad(v => v.current.interest = 0);
bad(v => v.counters.emptyPollAttempt = '1');
bad(v => v.counters.immediateCacheAcquire = '2');
bad(v => v.hostResourceTableObserved = true);
bad(v => v.destructionAtHostStoreExitObserved = true);
bad(v => v.afterLoop.callSerial = '2');
bad(v => v.afterLoop.loopResultObserved = false);
bad(v => v.afterPostCall.loopResultObserved = true);
bad(v => v.afterPostCall.currentFunction = 0, requirePreviousTimerBoundary);
bad(v => v.afterPostCall.freeListSize = '1', requirePreviousTimerBoundary);
bad(v => v.afterLoop.runtime.interest = 1, requirePreviousTimerBoundary);
bad(v => v.afterLoop.runtime.queued = '1', requirePreviousTimerBoundary);
bad(v => v.afterLoop.runtime.timerRegistry = '1', requirePreviousTimerBoundary);
bad(v => v.afterLoop.loopReturnedSuccess = false, requirePreviousTimerBoundary);
bad(v => v.eventSerial = '18446744073709551616');
bad(v => v.counters.pollCall = '01');
pass(() => {
  const v = structuredClone(valid);
  v.counters.immediateCacheAcquire = '1'; v.counters.immediateCacheUse = '2';
  v.current.immediateCacheOwned = v.afterLoop.runtime.immediateCacheOwned = v.afterPostCall.runtime.immediateCacheOwned = true;
  // This must remain accepted as TIMER boundary evidence, without pretending
  // that the still-owned immediate cache was dropped at host Store destruction.
  assert.equal(requirePreviousTimerBoundary(JSON.stringify(v)).current.immediateCacheOwned, true);
});
pass(() => {
  const v = structuredClone(valid); v.eventSerial = '18446744073709551615';
  assert.equal(validateSnapshot(JSON.stringify(v)).eventSerial, '18446744073709551615');
});
console.log(JSON.stringify({schemaVersion: 1, checks, passed: true,
  nativeCppExecuted: false, guestImported: false, helperOrHostWorkloadInvoked: false}));
