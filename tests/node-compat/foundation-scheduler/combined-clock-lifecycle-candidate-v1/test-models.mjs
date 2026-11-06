// Synthetic DATA only. Never import/evaluate any fixture, generated module,
// package, preflight, Wasmtime runner or native helper.
import assert from 'node:assert/strict';
import {CASE_CALLBACKS, CASE_IDS, validateResourceRun, validateResourceSequence,
  validateResourceInspect, validateResourceWrapper, validateClockSnapshot,
  validateSurvivingInterest} from './collectors.mjs';
let checks = 0;
const copy = structuredClone;
function test(name, f) { f(); checks++; }
function rejected(name, valid, change, validator) {
  test(name, () => { const v = copy(valid); change(v); assert.throws(() => validator(v)); });
}
function emptyState() {
  return {initial: {timerCallbacks: 0, startedCases: 0, completedCases: 0},
    counters: {inspect: 0, run: 0, validate: 0, timerCallbacks: 0, startedCases: 0, completedCases: 0},
    registeredIds: [], ownPendingNativeHandleCountInstrumented: false,
    hostResourceTableObserved: false, resetCalled: false};
}
function syntheticRun(caseId, previous) {
  const before = copy(previous); before.counters.run++; before.counters.startedCases++;
  const current = before.counters.run, after = copy(before), ids = [];
  for (let i = 0; i < CASE_IDS[caseId]; i++) ids.push(after.registeredIds.length + i + 1);
  after.registeredIds.push(...ids); after.counters.timerCallbacks += CASE_CALLBACKS[caseId];
  after.counters.completedCases++;
  const results = [
    {id: ids[0], pressureChecksum: 3192, events: [{kind: 'one-shot', value: 'queued-' + current, strictReceiverNull: true}]},
    {id: ids[0], fired: 0, doubleClear: true},
    {id: ids[0], ticks: 3, events: [1, 2, 3]},
    {outer: ids[0], victim: ids[1], victimCalls: 0, events: ['outer']},
    {id: ids[0], token: 'active-' + current, pressureChecksum: 3192, combinedOwnersOnly: true, soleTemporaryRootProved: false},
    {same: true, message: 'RESOURCE_HANDLED_CALLBACK'},
    {cleared: ids.slice(0, 32), fired: 0, allocationFailureInjected: false}
  ];
  return {schemaVersion: 1, kind: 'scheduler-resource-run-v1', caseId, current,
    completed: true, result: results[caseId], before, after,
    nativeResourceCountsObserved: false, hostClockValuesUsedAsOracle: false};
}
function syntheticSequence(rotations, start = emptyState()) {
  const rows = []; let next = start;
  for (let i = 0; i < rotations * 7; i++) {
    const row = syntheticRun(i % 7, next); rows.push(row); next = row.after;
  }
  return rows;
}
function inspect(s) {
  return {schemaVersion: 1, kind: 'scheduler-resource-inspect-v1', initDenials:
    ['setTimeout', 'setInterval'].map(name => ({name, installed: true, typeError: true,
      message: name + ' can only be used during request handling'})),
    state: s, snapshotHasLiveTimerRequested: false, initStateGuardSourceCoupled: true};
}
const sequence = syntheticSequence(3);
test('all seven cases and three retained rotations', () => validateResourceSequence(sequence.map(JSON.stringify), 3));
test('one complete rotation', () => validateResourceSequence(sequence.slice(0, 7).map(JSON.stringify)));
for (let id = 0; id < 7; id++) {
  test('case:' + id, () => validateResourceRun(JSON.stringify(sequence[id]), id));
  rejected('callback count:' + id, sequence[id], v => v.after.counters.timerCallbacks++, v => validateResourceRun(JSON.stringify(v), id));
}
rejected('missing case', sequence, v => v.splice(3, 1), v => validateResourceSequence(v.map(JSON.stringify), 3));
rejected('duplicate case', sequence, v => v[3] = copy(v[2]), v => validateResourceSequence(v.map(JSON.stringify), 3));
rejected('retained counter lost', sequence, v => { v[8].before.counters.run++; v[8].after.counters.run++; }, v => validateResourceSequence(v.map(JSON.stringify), 3));
rejected('timer ID reused', sequence[6], v => v.after.registeredIds[1] = v.after.registeredIds[0], v => validateResourceRun(JSON.stringify(v), 6));
rejected('wrong full callback value', sequence[0], v => v.result.events[0].value += '-wrong', v => validateResourceRun(JSON.stringify(v), 0));
rejected('native drops invented', sequence[0], v => v.nativeResourceCountsObserved = true, v => validateResourceRun(JSON.stringify(v), 0));
rejected('sole root invented', sequence[4], v => v.result.soleTemporaryRootProved = true, v => validateResourceRun(JSON.stringify(v), 4));
rejected('unhandled control changed', sequence[5], v => v.result.same = false, v => validateResourceRun(JSON.stringify(v), 5));
rejected('batch dropped a full ID', sequence[6], v => v.result.cleared.pop(), v => validateResourceRun(JSON.stringify(v), 6));
const beforeState = emptyState(); beforeState.counters.inspect = 1; beforeState.counters.validate = 1;
const wrapperRecords = syntheticSequence(1, beforeState), afterState = copy(wrapperRecords.at(-1).after);
afterState.counters.inspect++;
const wrapper = {schemaVersion: 1, kind: 'scheduler-resource-within-export-v1',
  before: inspect(beforeState), records: wrapperRecords, after: inspect(afterState),
  withinOneOuterExport: true, separateHostCallInterleavingProved: false, resetOrReuseProved: false};
test('complete wrapper', () => validateResourceWrapper(JSON.stringify(wrapper)));
test('INIT refusal inspect', () => validateResourceInspect(JSON.stringify(wrapper.before)));
rejected('lost INIT denial', wrapper.before, v => v.initDenials.pop(), v => validateResourceInspect(JSON.stringify(v)));
rejected('wrong INIT phase', wrapper.before, v => v.initDenials[0].typeError = false, v => validateResourceInspect(JSON.stringify(v)));
rejected('wrapper missing seventh', wrapper, v => v.records.pop(), v => validateResourceWrapper(JSON.stringify(v)));
rejected('wrapper broad reuse claim', wrapper, v => v.resetOrReuseProved = true, v => validateResourceWrapper(JSON.stringify(v)));
function clock(calls = 1, first = 0, last = 2, wall = 0) {
  return {schemaVersion: 1, kind: 'combined-clock-snapshot-observation-v1', calls,
    initialization: {dateNow: 0, jobs: 1, moduleEvaluations: 1},
    before: {dateNow: wall, dateObject: 0, iso: '1970-01-01T00:00:00.000Z', performanceNow: first, timeOrigin: 0},
    after: {dateNow: wall, dateObject: 0, iso: '1970-01-01T00:00:00.000Z', performanceNow: last, timeOrigin: 0},
    callbacks: 1, elapsed: last - first, initPerformanceCalled: false, entropyRequested: false,
    resetCalled: false, nativeMonotonicOffsetObserved: false, hostClockValuesAreExactOracle: false};
}
const firstClock = clock(), laterClock = clock(2, 2, 4, -10);
test('zero origin and equal samples permitted', () => validateClockSnapshot(JSON.stringify(clock(1, 0, 0))));
test('retained monotonic; realtime may move backward', () => validateClockSnapshot(JSON.stringify(laterClock), firstClock));
rejected('backward monotonic', laterClock, v => v.before.performanceNow = 1, v => validateClockSnapshot(JSON.stringify(v), firstClock));
rejected('origin changed', laterClock, v => { v.before.timeOrigin++; v.after.timeOrigin++; }, v => validateClockSnapshot(JSON.stringify(v), firstClock));
rejected('ISO dropped bytes', firstClock, v => v.before.iso = 'bad', v => validateClockSnapshot(JSON.stringify(v)));
rejected('INIT clock called unsafely', firstClock, v => v.initPerformanceCalled = true, v => validateClockSnapshot(JSON.stringify(v)));
rejected('native offset invented', firstClock, v => v.nativeMonotonicOffsetObserved = true, v => validateClockSnapshot(JSON.stringify(v)));
const survivor = {schemaVersion: 1, kind: 'combined-surviving-interest-observation-v1', calls: 1,
  values: ['a', 'b'], events: ['job-before-timers', 'timer-a', 'job-after-a', 'timer-b', 'fence'],
  ids: Array.from({length: 11}, (_, i) => i + 1), cancelled: Array.from({length: 8}, (_, i) => i + 1),
  cancelledCallbacks: 0, pendingPromiseResolved: true, nativeInterestCountObserved: false,
  allInvalidTaskSelectionExercised: false, nativeResourceDropsObserved: false,
  resetCalled: false, entropyRequested: false};
test('observable surviving Promise', () => validateSurvivingInterest(JSON.stringify(survivor)));
rejected('surviving order', survivor, v => v.events.reverse(), v => validateSurvivingInterest(JSON.stringify(v)));
rejected('cancelled callback ran', survivor, v => v.cancelledCallbacks++, v => validateSurvivingInterest(JSON.stringify(v)));
rejected('interest count invented', survivor, v => v.nativeInterestCountObserved = true, v => validateSurvivingInterest(JSON.stringify(v)));
rejected('all-invalid invented', survivor, v => v.allInvalidTaskSelectionExercised = true, v => validateSurvivingInterest(JSON.stringify(v)));
console.log(JSON.stringify({schemaVersion: 1, kind: 'synthetic-collector-model-tests', checks,
  passed: true, guestImported: false, guestExecuted: false, clocksRead: false,
  nativeOrHostWorkloadInvoked: false}));
