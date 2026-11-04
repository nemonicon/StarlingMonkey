'use strict';
// Ordinary pinned-Node boundary oracle. No guest execution or scheduler shim.
exports.scenario = function scenario(boundary) {
  const trace = [];
  function body() {
    Promise.resolve().then(() => {
      trace.push('promise-first');
      process.nextTick(() => trace.push('tick-from-promise'));
      Promise.resolve().then(() => trace.push('nested-promise'));
    });
    process.nextTick(() => {
      trace.push('tick-first');
      process.nextTick(() => trace.push('nested-tick'));
      Promise.resolve().then(() => trace.push('promise-from-tick'));
    });
    queueMicrotask(() => trace.push('microtask'));
    setImmediate(() => process.stdout.write(JSON.stringify({ boundary, trace }) + '\n'));
  }
  if (boundary === 'task') setImmediate(body);
  else if (boundary === 'promise-job') Promise.resolve().then(body);
  else body();
};
