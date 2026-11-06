// UNCOMPILED/UNEXECUTED. Observable Promise progress, not a native interest count.
let calls = 0;
function check(value, message) {
  if (!value) throw new Error('COMBINED_SURVIVOR_CHECK:' + message);
}
export async function run() {
  calls++;
  const events = [], ids = [], cancelled = [];
  let cancelledCallbacks = 0;
  function remember(id) {
    check(Number.isInteger(id) && id > 0 && !ids.includes(id), 'unique positive ID');
    ids.push(id); return id;
  }
  for (let i = 0; i < 8; i++) {
    const id = remember(setTimeout(() => { cancelledCallbacks++; }, 0));
    cancelled.push(id); clearTimeout(id); clearTimeout(id);
  }
  const a = new Promise(resolve => remember(setTimeout(() => {
    events.push('timer-a');
    Promise.resolve().then(() => events.push('job-after-a'));
    resolve('a');
  }, 0)));
  const b = new Promise(resolve => remember(setTimeout(() => {
    events.push('timer-b'); resolve('b');
  }, 0)));
  Promise.resolve().then(() => events.push('job-before-timers'));
  const values = await Promise.all([a, b]);
  await new Promise(resolve => remember(setTimeout(() => {
    events.push('fence'); resolve();
  }, 0)));
  const expected = ['job-before-timers', 'timer-a', 'job-after-a', 'timer-b', 'fence'];
  check(JSON.stringify(events) === JSON.stringify(expected), 'oldest survivor and job checkpoints');
  check(cancelledCallbacks === 0, 'cancelled tasks never dispatch');
  return JSON.stringify({schemaVersion: 1, kind: 'combined-surviving-interest-observation-v1',
    calls, values, events, ids, cancelled, cancelledCallbacks,
    pendingPromiseResolved: true, nativeInterestCountObserved: false,
    allInvalidTaskSelectionExercised: false, nativeResourceDropsObserved: false,
    resetCalled: false, entropyRequested: false});
}
