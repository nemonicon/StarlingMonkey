// Future raw-componentize fixture; never send this through profile admission.
// Actual finite guest builtin must be installed by the explicit test extension.
import diagnostic, { nextTick, scheduleTask, attemptReentry, checkResetGuard }
  from 'starling:test-internal-ticks';
function check(ok, message) { if (!ok) throw new Error(message); }
function scenario(trace) {
  Promise.resolve().then(() => {
    trace.push('promise-first');
    nextTick(() => trace.push('tick-from-promise'));
    Promise.resolve().then(() => trace.push('nested-promise'));
  });
  nextTick(() => {
    trace.push('tick-first');
    nextTick(() => trace.push('nested-tick'));
    Promise.resolve().then(() => trace.push('promise-from-tick'));
  });
  queueMicrotask(() => trace.push('microtask'));
}
// Genuine ESM preinitialization origin. The future harness compares this trace
// after actual snapshot/resumption; it does not flush from inside ModuleEvaluate.
const initialTrace = [];
scenario(initialTrace);
let calls = 0;
export async function run() {
  ++calls;
  check(diagnostic.nextTick === nextTick && diagnostic.scheduleTask === scheduleTask,
        'finite named/default bindings');
  const taskTrace = [];
  await new Promise(resolve => scheduleTask(() => {
    scenario(taskTrace);
    scheduleTask(resolve); // Observe after the preceding full task checkpoint.
  }));
  const value = {}, symbol = Symbol('tick-argument');
  const observations = [];
  await new Promise(resolve => {
    check(nextTick(function(a, b, c) {
      'use strict';
      observations.push(this === undefined, arguments.length === 3, a === value,
                        b === symbol, c === 17);
      for (const operation of [attemptReentry, checkResetGuard]) {
        try { operation(); observations.push(false); }
        catch (error) {
          observations.push(Object.hasOwn(error, 'code') && error.code === 'ERR_SM_NODE_SCHEDULER_REENTRY');
        }
      }
      scheduleTask(resolve);
    }, value, symbol, 17) === undefined, 'nextTick returns undefined');
  });
  check(observations.every(Boolean), 'rooted identity/receiver/reentry/reset guard');
  return JSON.stringify({ calls, initialTrace, taskTrace, observations });
}
