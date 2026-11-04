// Candidate-only checks for explicitly deferred operations and resource limits.
// Keep this separate from the unchanged Node differential corpus.
export function prototypeChecks(events) {
  let deferred = 0;
  function expect(callback, code) {
    let error; try { callback(); } catch (failure) { error = failure; }
    if (error?.code !== code) throw new Error(`Expected ${code}, got ${error?.name}: ${error?.code}`);
  }
  for (const name of ['on', 'once', 'addAbortListener', 'EventEmitterAsyncResource']) {
    expect(() => events[name](), 'ERR_SM_NODE_UNSUPPORTED');
    expect(() => new events[name](), 'ERR_SM_NODE_UNSUPPORTED'); deferred += 2;
  }
  for (const operation of [() => new events.EventEmitter({ captureRejections: true }), () => { events.EventEmitter.captureRejections = true; },
    () => events.getEventListeners(new EventTarget(), 'x'), () => events.getMaxListeners(new EventTarget()), () => events.setMaxListeners(2, new EventTarget())]) {
    expect(operation, 'ERR_SM_NODE_UNSUPPORTED'); deferred++;
  }
  const listener = () => {};
  const e = new events.EventEmitter(); e.setMaxListeners(0);
  for (let i = 0; i < 65536; i++) e.on('x', listener);
  expect(() => e.on('x', listener), 'ERR_SM_NODE_LIMIT');
  if (e.listenerCount('x') !== 65536) throw new Error('Listener limit changed previous state');
  const names = new events.EventEmitter(); for (let i = 0; i < 4096; i++) names.on('x'+i, listener);
  expect(() => names.on('extra', listener), 'ERR_SM_NODE_LIMIT');
  if (names.eventNames().length !== 4096) throw new Error('Name limit changed previous state');
  const recursive = new events.EventEmitter(); recursive.on('x', () => recursive.emit('x'));
  expect(() => recursive.emit('x'), 'ERR_SM_NODE_LIMIT');
  recursive.removeAllListeners(); if (recursive.emit('x') !== false) throw new Error('Depth unwind recovery');
  expect(() => new events.EventEmitter().on(7, listener), 'ERR_SM_NODE_UNSUPPORTED');
  return { deferred, limits: 3, eventNameCoercionDeferred: true };
}
