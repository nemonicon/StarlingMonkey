// Public API observations only. No AsyncResource facade or host-specific imports.
export const CASE_IDS = Object.freeze([
  'readable-pull', 'readable-cancel', 'writable-write-close', 'writable-abort',
  'transform-write-flush', 'bind-throw-reject', 'snapshot-throw-reject', 'queue-microtask',
]);

export function describeThrown(value) {
  if (value === null) return { type: 'null' };
  if (typeof value !== 'object' && typeof value !== 'function') {
    return { type: typeof value, value: value === undefined ? null : String(value) };
  }
  return { type: typeof value, name: typeof value.name === 'string' ? value.name : null,
    message: typeof value.message === 'string' ? value.message : null };
}

function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  // Observe rejection immediately, including failures before the eventual await.
  promise.then(() => {}, () => {});
  return { promise, resolve, reject };
}

function failure(label) { return new Error(`web-stream-context: ${label}`); }

function context(AsyncLocalStorage, record, runFresh) {
  const first = new AsyncLocalStorage(), second = new AsyncLocalStorage();
  const stores = {
    A: [Object.freeze({ owner: 'A:first' }), Object.freeze({ owner: 'A:second' })],
    B: [Object.freeze({ owner: 'B:first' }), Object.freeze({ owner: 'B:second' })],
  };
  const pending = new Set(), locks = new Set(), timers = new Set(), cleanups = [];
  function label(value, index) {
    return value === undefined ? 'undefined' : value === stores.A[index] ? 'A' :
      value === stores.B[index] ? 'B' : 'unexpected';
  }
  function current() { return { first: label(first.getStore(), 0), second: label(second.getStore(), 1) }; }
  function observe(event, detail = null) {
    if (record.events.length >= 128) throw failure('event-limit');
    record.events.push({ sequence: record.events.length + 1, event, context: current(), detail });
  }
  function check(name, passed) {
    if (record.checks.length >= 128) throw failure('check-limit');
    record.checks.push({ name, passed: passed === true });
    if (passed !== true) throw failure(name);
  }
  function run(owner, callback) {
    return runFresh(() => first.run(stores[owner][0], () => second.run(stores[owner][1], callback)));
  }
  function inOwner(owner) { return first.getStore() === stores[owner][0] && second.getStore() === stores[owner][1]; }
  function track(value) {
    const promise = Promise.resolve(value);
    pending.add(promise);
    promise.then(() => { pending.delete(promise); }, () => { pending.delete(promise); });
    return promise;
  }
  async function deadline(value, milliseconds, name) {
    let handle;
    const expired = new Promise((_, reject) => {
      handle = setTimeout(() => { timers.delete(handle); reject(failure(`${name}-deadline`)); }, milliseconds);
      timers.add(handle);
    });
    try { return await Promise.race([track(value), expired]); }
    finally { clearTimeout(handle); timers.delete(handle); }
  }
  function hold(lock) { locks.add(lock); return lock; }
  function release(lock) { lock.releaseLock(); locks.delete(lock); }
  async function cleanup() {
    const errors = [];
    for (let index = cleanups.length - 1; index >= 0; index--) {
      try { await deadline(cleanups[index](), 250, 'cleanup'); }
      catch (error) { errors.push(describeThrown(error)); }
    }
    // Disabling belongs after stream cancellation and all observed task collection.
    first.disable(); second.disable();
    record.cleanup = { errors, pendingTasks: pending.size, heldLocks: locks.size,
      liveDeadlineTimers: timers.size, knownComplete: errors.length === 0 && pending.size === 0 && locks.size === 0 && timers.size === 0 };
    for (const handle of timers) clearTimeout(handle);
    timers.clear();
  }
  return { AsyncLocalStorage, observe, check, run, inOwner, track, deadline, hold, release,
    addCleanup(callback) { cleanups.push(callback); }, cleanup };
}

async function readablePull(c) {
  let reader, pulls = 0;
  const stream = c.run('A', () => new ReadableStream({
    start() { c.observe('source.start'); },
    async pull(controller) {
      pulls++; c.observe('source.pull.before-await');
      await Promise.resolve(); c.observe('source.pull.after-await');
      controller.enqueue('read-value'); controller.close();
    },
    cancel(reason) { c.observe('source.cancel', { cleanup: reason === cleanupReason }); },
  }, { highWaterMark: 0 }));
  const cleanupReason = Object.freeze({ cleanup: 'readable-pull' });
  c.addCleanup(async () => {
    if (reader) { try { await c.track(reader.cancel(cleanupReason)); } finally { c.release(reader); } }
  });
  c.observe('creator.returned');
  await c.run('B', async () => {
    reader = c.hold(stream.getReader()); c.observe('consumer.before-read');
    const first = await c.track(reader.read()); c.observe('consumer.after-first-read');
    const end = await c.track(reader.read()); c.observe('consumer.after-end');
    c.check('one-pull', pulls === 1);
    c.check('read-value', first.value === 'read-value' && first.done === false);
    c.check('read-end', end.value === undefined && end.done === true);
  });
}

async function readableCancel(c) {
  const reason = Object.freeze({ reason: 'readable-cancel' });
  let reader, calls = 0, sameReason = false;
  const stream = c.run('A', () => new ReadableStream({
    start() { c.observe('source.start'); },
    async cancel(value) {
      calls++; sameReason = value === reason; c.observe('source.cancel.before-await');
      await Promise.resolve(); c.observe('source.cancel.after-await');
    },
  }, { highWaterMark: 0 }));
  c.addCleanup(async () => {
    if (reader) { try { await c.track(reader.cancel(reason)); } finally { c.release(reader); } }
  });
  c.observe('creator.returned');
  await c.run('B', async () => {
    reader = c.hold(stream.getReader()); c.observe('consumer.before-cancel');
    await c.track(reader.cancel(reason)); c.observe('consumer.after-cancel');
    c.check('cancel-once', calls === 1); c.check('cancel-reason-identity', sameReason);
  });
}

async function writableWriteClose(c) {
  let writer, writes = 0, closes = 0;
  const stream = c.run('A', () => new WritableStream({
    start() { c.observe('sink.start'); },
    async write(value) {
      writes++; c.observe('sink.write.before-await', { value });
      await Promise.resolve(); c.observe('sink.write.after-await');
    },
    async close() { closes++; c.observe('sink.close.before-await'); await Promise.resolve(); c.observe('sink.close.after-await'); },
  }));
  c.addCleanup(async () => {
    if (writer) { try { await c.track(writer.abort('fixture-cleanup')); } finally { c.release(writer); } }
  });
  c.observe('creator.returned');
  await c.run('B', async () => {
    writer = c.hold(stream.getWriter()); c.observe('consumer.before-write');
    await c.track(writer.write('write-value')); c.observe('consumer.after-write');
    await c.track(writer.close()); c.observe('consumer.after-close');
    c.check('write-once', writes === 1); c.check('close-once', closes === 1);
  });
}

async function writableAbort(c) {
  const reason = Object.freeze({ reason: 'writable-abort' });
  let writer, calls = 0, sameReason = false;
  const stream = c.run('A', () => new WritableStream({
    start() { c.observe('sink.start'); },
    async abort(value) {
      calls++; sameReason = value === reason; c.observe('sink.abort.before-await');
      await Promise.resolve(); c.observe('sink.abort.after-await');
    },
  }));
  c.addCleanup(async () => {
    if (writer) { try { await c.track(writer.abort(reason)); } finally { c.release(writer); } }
  });
  c.observe('creator.returned');
  await c.run('B', async () => {
    writer = c.hold(stream.getWriter()); c.observe('consumer.before-abort');
    await c.track(writer.abort(reason)); c.observe('consumer.after-abort');
    c.check('abort-once', calls === 1); c.check('abort-reason-identity', sameReason);
  });
}

async function transformWriteFlush(c) {
  let reader, writer, transforms = 0, flushes = 0;
  const stream = c.run('A', () => new TransformStream({
    start() { c.observe('transformer.start'); },
    async transform(value, controller) {
      transforms++; c.observe('transformer.transform.before-await');
      await Promise.resolve(); c.observe('transformer.transform.after-await');
      controller.enqueue(`${value}-transformed`);
    },
    async flush() { flushes++; c.observe('transformer.flush.before-await'); await Promise.resolve(); c.observe('transformer.flush.after-await'); },
  }));
  c.addCleanup(async () => {
    const jobs = []; let primarySet = false, primary;
    const remember = error => { if (!primarySet) { primarySet = true; primary = error; } };
    // Request both operations even if one throws synchronously; observe both promises.
    if (reader) try { jobs.push(c.track(reader.cancel('fixture-cleanup'))); } catch (error) { remember(error); }
    if (writer) try { jobs.push(c.track(writer.abort('fixture-cleanup'))); } catch (error) { remember(error); }
    try {
      for (const row of await Promise.allSettled(jobs)) if (row.status === 'rejected') remember(row.reason);
    } catch (error) { remember(error); }
    finally {
      // Attempt both lock releases, retaining an earlier rejection including falsy values.
      if (reader) try { c.release(reader); } catch (error) { remember(error); }
      if (writer) try { c.release(writer); } catch (error) { remember(error); }
    }
    if (primarySet) throw primary;
  });
  c.observe('creator.returned');
  await c.run('B', async () => {
    reader = c.hold(stream.readable.getReader()); writer = c.hold(stream.writable.getWriter());
    c.observe('consumer.before-paired-read-write');
    // Start both sides before awaiting either; default TransformStream backpressure is real.
    const read = c.track(reader.read()), write = c.track(writer.write('input'));
    const [value] = await Promise.all([read, write]); c.observe('consumer.after-paired-read-write');
    const end = c.track(reader.read()), close = c.track(writer.close());
    const [closed] = await Promise.all([end, close]); c.observe('consumer.after-close');
    c.check('transform-once', transforms === 1); c.check('flush-once', flushes === 1);
    c.check('transformed-value', value.value === 'input-transformed' && value.done === false);
    c.check('transform-end', closed.value === undefined && closed.done === true);
  });
}

async function capturedCallbacks(c, kind) {
  const receiver = Object.freeze({ receiver: kind });
  const thrownValues = [Object.freeze({ sentinel: kind }), null, undefined, 0, false];
  let invoke;
  c.run('A', () => {
    if (kind === 'bind') {
      const bound = c.AsyncLocalStorage.bind(function (callback, value) { return Reflect.apply(callback, this, [value]); });
      invoke = (callback, value) => Reflect.apply(bound, receiver, [callback, value]);
    } else {
      const snapshot = c.AsyncLocalStorage.snapshot();
      invoke = (callback, value) => snapshot(callback, value);
    }
  });
  c.observe('capture.returned');
  await c.run('B', async () => {
    for (let index = 0; index < thrownValues.length; index++) {
      const sentinel = thrownValues[index]; let caught = false, value;
      try {
        invoke(function (argument) {
          c.observe('captured.sync', { index, argumentIdentity: argument === sentinel,
            receiverIdentity: kind === 'bind' ? this === receiver : null });
          c.check(`sync-${index}-capture-A`, c.inOwner('A'));
          c.check(`sync-${index}-argument`, argument === sentinel);
          if (kind === 'bind') c.check(`sync-${index}-receiver`, this === receiver);
          throw sentinel;
        }, sentinel);
      } catch (error) { caught = true; value = error; }
      c.observe('caller.after-sync-throw', { index, caught, identity: caught && value === sentinel });
      c.check(`sync-${index}-throw-identity`, caught && value === sentinel);
      c.check(`sync-${index}-caller-B`, c.inOwner('B'));
    }
    for (const [index, sentinel] of [thrownValues[0], false].entries()) {
      const rejection = c.track(invoke(async function (argument) {
        c.observe('captured.async.before-await', { index });
        c.check(`async-${index}-capture-before-A`, c.inOwner('A'));
        c.check(`async-${index}-argument`, argument === sentinel);
        await Promise.resolve(); c.observe('captured.async.after-await', { index });
        c.check(`async-${index}-capture-after-A`, c.inOwner('A'));
        throw sentinel;
      }, sentinel));
      c.observe('caller.after-async-call', { index });
      c.check(`async-${index}-immediate-caller-B`, c.inOwner('B'));
      let caught = false, value;
      try { await rejection; } catch (error) { caught = true; value = error; }
      c.observe('caller.after-rejection', { index, caught, identity: caught && value === sentinel });
      c.check(`async-${index}-rejection-identity`, caught && value === sentinel);
      c.check(`async-${index}-resumed-caller-B`, c.inOwner('B'));
    }
  });
}

async function microtasks(c) {
  const doneA = deferred(), doneB = deferred(); let callsA = 0, callsB = 0;
  c.run('A', () => {
    queueMicrotask(() => {
      try {
        callsA++; c.observe('microtask.A'); c.check('microtask-A-context', c.inOwner('A'));
        c.track(Promise.resolve().then(() => {
          c.observe('microtask.A.then'); c.check('microtask-A-then-context', c.inOwner('A')); doneA.resolve();
        })).catch(doneA.reject);
      } catch (error) { doneA.reject(error); }
    });
  });
  c.observe('scheduler.returned');
  await c.run('B', async () => {
    queueMicrotask(() => {
      try { callsB++; c.observe('microtask.B'); c.check('microtask-B-context', c.inOwner('B')); doneB.resolve(); }
      catch (error) { doneB.reject(error); }
    });
    c.observe('caller.before-microtask-await');
    await Promise.all([c.track(doneA.promise), c.track(doneB.promise)]);
    c.observe('caller.after-microtask-await');
    c.check('microtasks-once', callsA === 1 && callsB === 1);
    c.check('microtasks-caller-B', c.inOwner('B'));
  });
}

export async function runWebStreamContextCases({ AsyncLocalStorage, runFresh = callback => callback(),
  boundaryMode = 'public-only', report = {} }) {
  Object.assign(report, { schemaVersion: 1, suite: 'PUBLIC_ALS_WEB_STREAM_CONTEXT_OBSERVATIONS_V1',
    expectationsFrozen: false, webStreamContextComparisonPerformed: false,
    nativeAsyncResourceTested: false, fullNextAccepted: false, boundaryMode,
    nativeBoundaryClaimRequiresExternalProof: boundaryMode !== 'public-only', records: [], passed: false });
  const required = { AsyncLocalStorage, ReadableStream: globalThis.ReadableStream,
    WritableStream: globalThis.WritableStream, TransformStream: globalThis.TransformStream,
    queueMicrotask: globalThis.queueMicrotask, setTimeout: globalThis.setTimeout, clearTimeout: globalThis.clearTimeout };
  report.surface = Object.fromEntries(Object.entries(required).map(([name, value]) => [name, typeof value]));
  if (typeof runFresh !== 'function' || typeof boundaryMode !== 'string' ||
      Object.values(required).some(value => typeof value !== 'function') ||
      typeof AsyncLocalStorage.bind !== 'function' || typeof AsyncLocalStorage.snapshot !== 'function') {
    report.setupError = { type: 'missing-public-api' }; return report;
  }
  const controls = [readablePull, readableCancel, writableWriteClose, writableAbort, transformWriteFlush,
    c => capturedCallbacks(c, 'bind'), c => capturedCallbacks(c, 'snapshot'), microtasks];
  for (let index = 0; index < controls.length; index++) {
    const record = { id: CASE_IDS[index], events: [], checks: [], fulfilled: false, primarySet: false, passed: false };
    report.records.push(record);
    const c = context(AsyncLocalStorage, record, runFresh);
    try {
      await c.deadline(controls[index](c), 1000, record.id);
      c.observe('case.outer-after-completion');
      // Stream callback contexts remain observations, but caller restoration is a public ALS invariant.
      const last = record.events[record.events.length - 1].context;
      c.check('outer-restored', last.first === 'undefined' && last.second === 'undefined');
      record.fulfilled = true;
    } catch (error) { record.primarySet = true; record.primary = describeThrown(error); }
    finally { await c.cleanup(); }
    record.passed = record.fulfilled && !record.primarySet && record.cleanup.knownComplete && record.checks.every(check => check.passed);
    // An uncollected task/lock is uncertainty; do not start another control after it.
    if (!record.cleanup.knownComplete) break;
  }
  report.completedAllCases = report.records.length === CASE_IDS.length && report.records.every(record => record.fulfilled);
  report.passed = report.completedAllCases && report.records.every(record => record.passed);
  report.contextOracleStatus = 'OBSERVATIONS_ONLY_WEB_STREAM_BASELINE_NOT_FROZEN';
  return report;
}
