// Pure host-side validation only. The caller MUST persist the entire typed raw
// return/throw and streams before calling these functions. No module is loaded,
// guest called, clock read, process started or evidence written by this module.
import assert from 'node:assert/strict';

export const CASE_CALLBACKS = Object.freeze([2, 1, 4, 2, 2, 2, 1]);
export const CASE_IDS = Object.freeze([2, 2, 2, 3, 2, 2, 33]);
function need(value, message) { assert(value, message); }
function integer(value, message) { need(Number.isSafeInteger(value) && value >= 0, message); }
function keys(value, names) { assert.deepEqual(Object.keys(value).sort(), [...names].sort(), 'complete record fields'); }
function parse(raw) {
  need(typeof raw === 'string', 'whole scalar string required');
  return JSON.parse(raw);
}
function state(value) {
  keys(value, ['initial', 'counters', 'registeredIds', 'ownPendingNativeHandleCountInstrumented', 'hostResourceTableObserved', 'resetCalled']);
  assert.deepEqual(value.initial, {timerCallbacks: 0, startedCases: 0, completedCases: 0});
  keys(value.counters, ['inspect', 'run', 'validate', 'timerCallbacks', 'startedCases', 'completedCases']);
  for (const name of ['inspect', 'run', 'validate', 'timerCallbacks', 'startedCases', 'completedCases'])
    integer(value.counters[name], 'counter:' + name);
  need(Array.isArray(value.registeredIds), 'all IDs retained');
  need(value.registeredIds.every(id => Number.isInteger(id) && id > 0), 'positive timer IDs');
  need(new Set(value.registeredIds).size === value.registeredIds.length, 'unique timer IDs');
  need(value.ownPendingNativeHandleCountInstrumented === false, 'no invented native handle count');
  need(value.hostResourceTableObserved === false && value.resetCalled === false, 'honest resource scope');
}
export function validateResourceInspect(raw) {
  const value = parse(raw);
  keys(value, ['schemaVersion', 'kind', 'initDenials', 'state', 'snapshotHasLiveTimerRequested', 'initStateGuardSourceCoupled']);
  need(value.schemaVersion === 1 && value.kind === 'scheduler-resource-inspect-v1', 'resource inspect schema');
  assert.deepEqual(value.initDenials.map(r => r.name), ['setTimeout', 'setInterval']);
  for (const row of value.initDenials) {
    keys(row, ['name', 'installed', 'typeError', 'message']);
    need(row.installed === true && row.typeError === true && typeof row.message === 'string', 'INIT timer refusal');
    need(row.message.includes(row.name + ' can only be used during request handling'), 'actual INIT convention');
  }
  state(value.state);
  need(value.snapshotHasLiveTimerRequested === false && value.initStateGuardSourceCoupled === true, 'snapshot limit');
  return value;
}
export function validateResourceRun(raw, expectedCase) {
  const value = parse(raw);
  keys(value, ['schemaVersion', 'kind', 'caseId', 'current', 'completed', 'result', 'before', 'after', 'nativeResourceCountsObserved', 'hostClockValuesUsedAsOracle']);
  need(Number.isInteger(expectedCase) && expectedCase >= 0 && expectedCase < 7, 'finite case ID');
  need(value.schemaVersion === 1 && value.kind === 'scheduler-resource-run-v1' &&
    value.caseId === expectedCase && value.completed === true, 'resource run schema');
  integer(value.current, 'sequence'); need(value.current > 0, 'positive sequence');
  state(value.before); state(value.after);
  const before = value.before.counters, after = value.after.counters;
  need(after.run === before.run && after.startedCases === before.startedCases, 'entry counters already incremented before before-snapshot');
  need(after.completedCases === before.completedCases + 1, 'one completion');
  need(after.inspect === before.inspect && after.validate === before.validate, 'no hidden export counters');
  need(after.timerCallbacks - before.timerCallbacks === CASE_CALLBACKS[expectedCase], 'all callbacks');
  const newIds = value.after.registeredIds.slice(value.before.registeredIds.length);
  assert.deepEqual(value.after.registeredIds.slice(0, value.before.registeredIds.length), value.before.registeredIds);
  need(newIds.length === CASE_IDS[expectedCase], 'all registered IDs');
  need(value.nativeResourceCountsObserved === false && value.hostClockValuesUsedAsOracle === false, 'honest observation scope');
  const r = value.result;
  keys(r, [
    ['id', 'pressureChecksum', 'events'], ['id', 'fired', 'doubleClear'], ['id', 'ticks', 'events'],
    ['outer', 'victim', 'victimCalls', 'events'], ['id', 'token', 'pressureChecksum', 'combinedOwnersOnly', 'soleTemporaryRootProved'],
    ['same', 'message'], ['cleared', 'fired', 'allocationFailureInjected']
  ][expectedCase]);
  if (expectedCase === 0) {
    assert.deepEqual(r.events, [{kind: 'one-shot', value: 'queued-' + value.current, strictReceiverNull: true}]);
    need(r.pressureChecksum === 3192 && r.id === newIds[0], 'queued argv/Buffer checksum');
  } else if (expectedCase === 1) {
    need(r.id === newIds[0] && r.fired === 0 && r.doubleClear === true, 'double queued cancellation');
  } else if (expectedCase === 2) {
    need(r.id === newIds[0] && r.ticks === 3, 'interval self-clear'); assert.deepEqual(r.events, [1, 2, 3]);
  } else if (expectedCase === 3) {
    need(r.outer === newIds[0] && r.victim === newIds[1] && r.victimCalls === 0, 'nested cancellation');
    assert.deepEqual(r.events, ['outer']);
  } else if (expectedCase === 4) {
    need(r.id === newIds[0] && r.token === 'active-' + value.current && r.pressureChecksum === 3192, 'active argv');
    need(r.combinedOwnersOnly === true && r.soleTemporaryRootProved === false, 'root proof limitation');
  } else if (expectedCase === 5) {
    assert.deepEqual(r, {same: true, message: 'RESOURCE_HANDLED_CALLBACK'});
  } else {
    assert.deepEqual(r.cleared, newIds.slice(0, 32));
    need(r.fired === 0 && r.allocationFailureInjected === false, 'bounded retirement batch');
  }
  return value;
}
export function validateResourceSequence(raws, rotations = 1) {
  need(Number.isInteger(rotations) && rotations >= 1 && rotations <= 3, 'finite rotations');
  need(Array.isArray(raws) && raws.length === 7 * rotations, 'complete seven-case coverage');
  const values = raws.map((raw, i) => validateResourceRun(raw, i % 7));
  for (let i = 1; i < values.length; i++) {
    const a = values[i - 1], b = values[i];
    need(b.current === a.current + 1, 'retained sequence');
    assert.deepEqual(b.before.registeredIds, a.after.registeredIds);
    for (const key of ['timerCallbacks', 'completedCases', 'inspect', 'validate'])
      need(b.before.counters[key] === a.after.counters[key], 'retained counter:' + key);
    need(b.before.counters.run === a.after.counters.run + 1 &&
      b.before.counters.startedCases === a.after.counters.startedCases + 1, 'one next entry');
  }
  return values;
}
export function validateResourceWrapper(raw) {
  const value = parse(raw);
  keys(value, ['schemaVersion', 'kind', 'before', 'records', 'after', 'withinOneOuterExport', 'separateHostCallInterleavingProved', 'resetOrReuseProved']);
  need(value.schemaVersion === 1 && value.kind === 'scheduler-resource-within-export-v1', 'wrapper schema');
  validateResourceInspect(JSON.stringify(value.before)); validateResourceInspect(JSON.stringify(value.after));
  const records = validateResourceSequence(value.records.map(r => JSON.stringify(r)));
  assert.deepEqual(records[0].before.registeredIds, value.before.state.registeredIds);
  assert.deepEqual(records.at(-1).after.registeredIds, value.after.state.registeredIds);
  for (const key of ['timerCallbacks', 'completedCases', 'inspect', 'validate'])
    need(records[0].before.counters[key] === value.before.state.counters[key], 'wrapper first boundary:' + key);
  need(records[0].before.counters.run === value.before.state.counters.run + 1 &&
    records[0].before.counters.startedCases === value.before.state.counters.startedCases + 1, 'wrapper first entry');
  for (const key of ['run', 'startedCases', 'completedCases', 'timerCallbacks', 'validate'])
    need(records.at(-1).after.counters[key] === value.after.state.counters[key], 'wrapper last boundary:' + key);
  for (const key of ['run', 'startedCases', 'completedCases'])
    need(value.after.state.counters[key] - value.before.state.counters[key] === 7, 'wrapper seven entries:' + key);
  need(value.after.state.counters.timerCallbacks - value.before.state.counters.timerCallbacks === 14, 'wrapper all callbacks');
  need(value.after.state.counters.inspect === value.before.state.counters.inspect + 1, 'wrapper final inspect');
  need(value.after.state.counters.validate === value.before.state.counters.validate, 'one wrapper already entered');
  need(value.withinOneOuterExport === true && value.separateHostCallInterleavingProved === false &&
    value.resetOrReuseProved === false, 'wrapper proof boundary');
  return value;
}
export function validateClockSnapshot(raw, previous = null) {
  const v = parse(raw);
  keys(v, ['schemaVersion', 'kind', 'calls', 'initialization', 'before', 'after', 'callbacks', 'elapsed', 'initPerformanceCalled', 'entropyRequested', 'resetCalled', 'nativeMonotonicOffsetObserved', 'hostClockValuesAreExactOracle']);
  need(v.schemaVersion === 1 && v.kind === 'combined-clock-snapshot-observation-v1', 'clock schema');
  integer(v.calls, 'clock calls'); need(v.calls > 0, 'clock called');
  keys(v.initialization, ['dateNow', 'jobs', 'moduleEvaluations']);
  need(Number.isSafeInteger(v.initialization.dateNow) && v.initialization.jobs === 1 && v.initialization.moduleEvaluations === 1, 'captured INIT observations');
  for (const sample of [v.before, v.after]) {
    keys(sample, ['dateNow', 'dateObject', 'iso', 'performanceNow', 'timeOrigin']);
    need(Number.isSafeInteger(sample.dateNow) && Number.isSafeInteger(sample.dateObject), 'whole Date observations');
    need(typeof sample.iso === 'string' && Date.parse(sample.iso) === sample.dateObject, 'Date object full ISO equality');
    need(Number.isFinite(sample.performanceNow) && sample.performanceNow >= 0 && Number.isFinite(sample.timeOrigin), 'finite monotonic observations');
  }
  need(v.after.performanceNow >= v.before.performanceNow && v.after.timeOrigin === v.before.timeOrigin, 'within-export monotonic/order');
  need(v.elapsed === v.after.performanceNow - v.before.performanceNow && v.callbacks === 1, 'whole elapsed/callback observation');
  if (previous) {
    need(v.calls === previous.calls + 1, 'retained clock sequence');
    assert.deepEqual(v.initialization, previous.initialization);
    need(v.before.timeOrigin === previous.after.timeOrigin && v.before.performanceNow >= previous.after.performanceNow, 'retained monotonic/origin');
  }
  for (const key of ['initPerformanceCalled', 'entropyRequested', 'resetCalled', 'nativeMonotonicOffsetObserved', 'hostClockValuesAreExactOracle'])
    need(v[key] === false, 'clock proof limitation:' + key);
  return v;
}
export function validateSurvivingInterest(raw) {
  const v = parse(raw);
  keys(v, ['schemaVersion', 'kind', 'calls', 'values', 'events', 'ids', 'cancelled', 'cancelledCallbacks', 'pendingPromiseResolved', 'nativeInterestCountObserved', 'allInvalidTaskSelectionExercised', 'nativeResourceDropsObserved', 'resetCalled', 'entropyRequested']);
  need(v.schemaVersion === 1 && v.kind === 'combined-surviving-interest-observation-v1', 'survivor schema');
  integer(v.calls, 'survivor calls'); need(v.calls > 0, 'survivor called');
  assert.deepEqual(v.values, ['a', 'b']);
  assert.deepEqual(v.events, ['job-before-timers', 'timer-a', 'job-after-a', 'timer-b', 'fence']);
  need(v.ids.length === 11 && new Set(v.ids).size === 11 && v.ids.every(id => Number.isInteger(id) && id > 0), 'all eleven IDs');
  assert.deepEqual(v.cancelled, v.ids.slice(0, 8));
  need(v.cancelledCallbacks === 0 && v.pendingPromiseResolved === true, 'surviving Promise progress');
  for (const key of ['nativeInterestCountObserved', 'allInvalidTaskSelectionExercised', 'nativeResourceDropsObserved', 'resetCalled', 'entropyRequested'])
    need(v[key] === false, 'survivor proof limitation:' + key);
  return v;
}
