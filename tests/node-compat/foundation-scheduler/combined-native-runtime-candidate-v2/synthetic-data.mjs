// Extracted synthetic DATA only, never guest source.
import {CASE_IDS,CASE_CALLBACKS} from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';
const copy=structuredClone;
export function emptyState() {
  return {initial: {timerCallbacks: 0, startedCases: 0, completedCases: 0},
    counters: {inspect: 0, run: 0, validate: 0, timerCallbacks: 0, startedCases: 0, completedCases: 0},
    registeredIds: [], ownPendingNativeHandleCountInstrumented: false,
    hostResourceTableObserved: false, resetCalled: false};
}
export function syntheticRun(caseId, previous) {
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
export function syntheticSequence(rotations, start = emptyState()) {
  const rows = []; let next = start;
  for (let i = 0; i < rotations * 7; i++) {
    const row = syntheticRun(i % 7, next); rows.push(row); next = row.after;
  }
  return rows;
}
export function inspect(s) {
  return {schemaVersion: 1, kind: 'scheduler-resource-inspect-v1', initDenials:
    ['setTimeout', 'setInterval'].map(name => ({name, installed: true, typeError: true,
      message: name + ' can only be used during request handling'})),
    state: s, snapshotHasLiveTimerRequested: false, initStateGuardSourceCoupled: true};
}
export function clock(calls = 1, first = 0, last = 2, wall = 0) {
  return {schemaVersion: 1, kind: 'combined-clock-snapshot-observation-v1', calls,
    initialization: {dateNow: 0, jobs: 1, moduleEvaluations: 1},
    before: {dateNow: wall, dateObject: 0, iso: '1970-01-01T00:00:00.000Z', performanceNow: first, timeOrigin: 0},
    after: {dateNow: wall, dateObject: 0, iso: '1970-01-01T00:00:00.000Z', performanceNow: last, timeOrigin: 0},
    callbacks: 1, elapsed: last - first, initPerformanceCalled: false, entropyRequested: false,
    resetCalled: false, nativeMonotonicOffsetObserved: false, hostClockValuesAreExactOracle: false};
}
export const survivor = {schemaVersion: 1, kind: 'combined-surviving-interest-observation-v1', calls: 1,
  values: ['a', 'b'], events: ['job-before-timers', 'timer-a', 'job-after-a', 'timer-b', 'fence'],
  ids: Array.from({length: 11}, (_, i) => i + 1), cancelled: Array.from({length: 8}, (_, i) => i + 1),
  cancelledCallbacks: 0, pendingPromiseResolved: true, nativeInterestCountObserved: false,
  allInvalidTaskSelectionExercised: false, nativeResourceDropsObserved: false,
  resetCalled: false, entropyRequested: false};
