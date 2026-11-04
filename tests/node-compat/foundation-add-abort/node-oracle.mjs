// Exact Node22 public addAbortListener oracle. No private binding, native fault,
// guest memory access or host modification is involved.
import assert from 'node:assert/strict';
import { addAbortListener } from 'node:events';
import { AsyncLocalStorage } from 'node:async_hooks';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const sourcePath = fileURLToPath(import.meta.url), here = dirname(sourcePath);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const nodePin = Object.freeze({ release: 'v22.14.0', tagObject: 'ddf66aca0766567c70bf16a92610f03ce0cd2bcd',
  revision: '5d2feb257bcee090e57900eb51720171a6aa92f3' });
assert.equal(process.version, nodePin.release); assert.deepEqual(process.execArgv, []);
assert(!process.env.NODE_OPTIONS, 'Use unmodified pinned Node default behavior');
const immediate = () => new Promise(done => setImmediate(done));
const caught = fn => { try { fn(); } catch (error) { return error; } throw new Error('Expected throw'); };
const errorShape = error => ({ name: error?.name ?? null, code: error?.code ?? null, message: error?.message ?? null });

async function throwChild(mode) {
  const order = [], exceptions = [], warnings = [], marker = new Error('ADD_ABORT_LISTENER_SENTINEL');
  process.on('warning', warning => warnings.push(errorShape(warning)));
  process.on('uncaughtException', (error, origin) => {
    exceptions.push({ ...errorShape(error), sameMarker: error === marker, origin });
    order.push('uncaughtException');
  });
  const controller = new AbortController();
  let callerCaught = false;
  if (mode === 'fresh') {
    addAbortListener(controller.signal, () => { order.push('throwing listener'); throw marker; });
    addAbortListener(controller.signal, () => { order.push('second listener'); });
    order.push('before abort');
    try { controller.abort(); } catch { callerCaught = true; }
    order.push('after abort');
  } else {
    controller.abort(); order.push('before registration');
    try { addAbortListener(controller.signal, () => { order.push('throwing listener'); throw marker; }); }
    catch { callerCaught = true; }
    order.push('after registration');
  }
  await immediate(); order.push('after immediate');
  assert.equal(callerCaught, false); assert.equal(exceptions.length, 1);
  assert.equal(exceptions[0].sameMarker, true); assert.equal(exceptions[0].origin, 'uncaughtException');
  assert.deepEqual(order, mode === 'fresh'
    ? ['before abort', 'throwing listener', 'second listener', 'after abort', 'uncaughtException', 'after immediate']
    : ['before registration', 'after registration', 'throwing listener', 'uncaughtException', 'after immediate']);
  return { mode, order, callerCaught, exceptions, warnings, publicUncaughtExceptionHandlerInstalled: true,
    scope: 'Synchronous listener throw observed through a public uncaughtException handler in an isolated fresh process; no crash or emitter replacement.' };
}

async function mainCases() {
  const cases = [], warnings = [];
  const onWarning = warning => warnings.push(errorShape(warning));
  process.on('warning', onWarning);
  async function test(name, run) { cases.push({ name, passed: true, observations: await run() }); }
  const disposeSymbol = Symbol.dispose;
  assert.equal(typeof disposeSymbol, 'symbol');
  assert.equal(disposeSymbol, Symbol.for('nodejs.dispose'));

  await test('Symbol.dispose and returned resource descriptors', () => {
    const controller = new AbortController(), resource = addAbortListener(controller.signal, () => {});
    const descriptor = Object.getOwnPropertyDescriptor(resource, disposeSymbol);
    assert.equal(Object.getPrototypeOf(resource), null);
    assert.deepEqual(Reflect.ownKeys(resource), [disposeSymbol]);
    assert.deepEqual([descriptor.enumerable, descriptor.writable, descriptor.configurable], [true, true, true]);
    assert.equal(typeof descriptor.value, 'function'); assert.equal(descriptor.value.length, 0);
    assert.equal(Object.hasOwn(descriptor.value, 'prototype'), false);
    assert.equal(resource.then, undefined); resource[disposeSymbol]();
    const globalDescriptor = Object.getOwnPropertyDescriptor(Symbol, 'dispose');
    return { globalSymbol: { description: disposeSymbol.description, registryKey: Symbol.keyFor(disposeSymbol),
      sameAsNodeRegistrySymbol: true, descriptor: { enumerable: globalDescriptor.enumerable,
        writable: globalDescriptor.writable, configurable: globalDescriptor.configurable } },
      resource: { nullPrototype: true, onlyOwnKeyIsDispose: true, enumerable: descriptor.enumerable,
        writable: descriptor.writable, configurable: descriptor.configurable, functionName: descriptor.value.name,
        functionLength: descriptor.value.length, ownsFunctionPrototype: false, then: '<undefined>' } };
  });

  await test('signal validation precedes listener validation', () => {
    const rows = [];
    for (const [label, signal] of [['undefined', undefined], ['null', null], ['boolean', true],
      ['number', 1], ['string', 'signal'], ['symbol', Symbol('signal')], ['bigint', 1n],
      ['plain object', {}], ['array', []], ['function with aborted property', Object.assign(function signal(){}, { aborted: true })]]) {
      const error = caught(() => addAbortListener(signal, null));
      assert.equal(error.name, 'TypeError'); assert.equal(error.code, 'ERR_INVALID_ARG_TYPE');
      assert(error.message.includes('signal')); rows.push({ label, ...errorShape(error) });
    }
    const controller = new AbortController();
    for (const [label, listener] of [['undefined', undefined], ['null', null], ['number', 1], ['object', {}]]) {
      const error = caught(() => addAbortListener(controller.signal, listener));
      assert.equal(error.code, 'ERR_INVALID_ARG_TYPE'); assert(error.message.includes('listener'));
      rows.push({ label: `listener ${label}`, ...errorShape(error) });
    }
    let handleEventReads = 0;
    const listenerObject = { get handleEvent() { handleEventReads++; throw new Error('unexpected handleEvent read'); } };
    assert.equal(caught(() => addAbortListener(controller.signal, listenerObject)).code, 'ERR_INVALID_ARG_TYPE');
    assert.equal(handleEventReads, 0);
    return { rows, handleEventReads };
  });

  await test('aborted getter read follows listener validation and preserves thrown value', () => {
    const marker = {}, reads = [];
    const fake = { get aborted() { reads.push('get aborted'); throw marker; } };
    const invalid = caught(() => addAbortListener(fake, null));
    assert.equal(invalid.code, 'ERR_INVALID_ARG_TYPE'); assert(invalid.message.includes('listener'));
    assert.deepEqual(reads, []);
    assert.equal(caught(() => addAbortListener(fake, () => {})), marker);
    assert.deepEqual(reads, ['get aborted']);
    let hasCalls = 0;
    const hasMarker = {}, proxy = new Proxy({}, { has(target, key) { hasCalls++; assert.equal(key, 'aborted'); throw hasMarker; } });
    assert.equal(caught(() => addAbortListener(proxy, null)), hasMarker); assert.equal(hasCalls, 1);
    return { invalidListenerCheckedBeforeAbortedRead: true, getterExceptionIdentity: true, getterReads: reads,
      hasExceptionIdentity: true, hasCalls };
  });

  await test('structural fake signal calls and disposer method lookup', () => {
    const calls = [];
    let listener;
    const target = {
      get aborted() { calls.push('get aborted'); return false; },
      get addEventListener() {
        calls.push('get addEventListener');
        return function(type, callback, options) {
          assert.equal(this, fake); assert.equal(type, 'abort'); listener = callback;
          assert.equal(Object.getPrototypeOf(options), null); assert.equal(options.once, true);
          calls.push('call addEventListener:abort:once');
        };
      },
      get removeEventListener() { calls.push('get original removeEventListener'); return () => { calls.push('original removal'); }; },
    };
    const fake = new Proxy(target, { has(object, key) { calls.push(`has:${String(key)}`); return Reflect.has(object, key); } });
    const callback = () => {}; const resource = addAbortListener(fake, callback);
    assert.equal(listener, callback);
    Object.defineProperty(target, 'removeEventListener', { configurable: true, value: function(type, callback) {
      assert.equal(this, fake); assert.equal(type, 'abort'); assert.equal(callback, listener); calls.push('replacement removal');
    } });
    assert.equal(resource[disposeSymbol](), undefined); assert.equal(resource[disposeSymbol](), undefined);
    assert.deepEqual(calls, ['has:aborted', 'get aborted', 'get addEventListener', 'call addEventListener:abort:once',
      'replacement removal', 'replacement removal']);
    const missingAdd = caught(() => addAbortListener({ aborted: false }, () => {}));
    assert.equal(missingAdd.name, 'TypeError'); assert.equal(missingAdd.code, undefined);
    return { calls, deferredRemovalReadsCurrentMethod: true, repeatedFakeDisposalRepeatsRemoval: true,
      missingAddEventListener: errorShape(missingAdd),
      scope: 'Public structural acceptance; no private option symbol or listener storage is inspected.' };
  });

  await test('already-aborted structural object schedules without event methods', async () => {
    const order = [], receiver = [];
    const fake = { get aborted() { order.push('get aborted'); return {}; },
      get addEventListener() { throw new Error('unexpected addEventListener read'); },
      get removeEventListener() { throw new Error('unexpected removeEventListener read'); } };
    order.push('before registration');
    const resource = addAbortListener(fake, function(...args) {
      order.push('listener'); receiver.push({ undefinedThis: this === undefined, argumentCount: args.length });
    });
    resource[disposeSymbol](); resource[disposeSymbol](); order.push('after dispose');
    await Promise.resolve(); order.push('after microtask checkpoint');
    assert.deepEqual(order, ['before registration', 'get aborted', 'after dispose', 'listener', 'after microtask checkpoint']);
    assert.deepEqual(receiver, [{ undefinedThis: true, argumentCount: 0 }]);
    return { order, receiver, queuedCallbackUnaffectedByDisposal: true };
  });

  await test('fresh signal callback is synchronous with signal receiver and Event', () => {
    const controller = new AbortController(), order = [], details = [];
    addAbortListener(controller.signal, function(...args) {
      const event = args[0]; order.push('listener');
      details.push({ signalThis: this === controller.signal, argumentCount: args.length, eventInstance: event instanceof Event,
        type: event.type, targetIsSignal: event.target === controller.signal,
        currentTargetIsSignal: event.currentTarget === controller.signal, abortedDuringCallback: controller.signal.aborted,
        reasonDuringCallback: controller.signal.reason, isTrusted: event.isTrusted, cancelable: event.cancelable });
    });
    order.push('before abort'); controller.abort('first reason'); order.push('after abort');
    controller.abort('second reason'); controller.signal.dispatchEvent(new Event('abort'));
    assert.deepEqual(order, ['before abort', 'listener', 'after abort']);
    assert.equal(details.length, 1); assert.equal(details[0].signalThis, true);
    assert.equal(details[0].argumentCount, 1); assert.equal(details[0].eventInstance, true);
    assert.equal(details[0].targetIsSignal, true); assert.equal(details[0].currentTargetIsSignal, true);
    assert.equal(details[0].abortedDuringCallback, true); assert.equal(details[0].reasonDuringCallback, 'first reason');
    return { order, details, onceAcrossRepeatedAbortAndManualEvent: true };
  });

  await test('already-aborted signal callback is a zero-argument microtask despite disposal', async () => {
    const controller = new AbortController(), order = [], details = [];
    controller.abort('already'); queueMicrotask(() => order.push('earlier queued microtask'));
    order.push('before registration');
    const resource = addAbortListener(controller.signal, function(...args) {
      order.push('listener'); details.push({ undefinedThis: this === undefined, argumentCount: args.length });
    });
    resource[disposeSymbol](); queueMicrotask(() => order.push('later queued microtask')); order.push('after registration/dispose');
    await Promise.resolve(); order.push('await continuation');
    assert.deepEqual(order, ['before registration', 'after registration/dispose', 'earlier queued microtask', 'listener',
      'later queued microtask', 'await continuation']);
    assert.deepEqual(details, [{ undefinedThis: true, argumentCount: 0 }]);
    return { order, details, queuedCallbackUnaffectedByDisposal: true };
  });

  await test('stopImmediatePropagation skips ordinary listeners but not protected registrations', () => {
    const controller = new AbortController(), order = [];
    controller.signal.addEventListener('abort', event => { order.push('ordinary stopper'); event.stopImmediatePropagation(); });
    addAbortListener(controller.signal, event => { order.push('protected one'); event.stopImmediatePropagation(); });
    controller.signal.addEventListener('abort', () => order.push('ordinary later'));
    addAbortListener(controller.signal, () => order.push('protected two'));
    controller.abort(); assert.deepEqual(order, ['ordinary stopper', 'protected one', 'protected two']);
    return { order };
  });

  await test('fresh disposal is effect-idempotent and can remove a later listener during dispatch', () => {
    const disposed = new AbortController(); let disposedCalls = 0;
    const resource = addAbortListener(disposed.signal, () => disposedCalls++);
    assert.equal(resource[disposeSymbol](), undefined); assert.equal(resource[disposeSymbol](), undefined);
    disposed.signal.dispatchEvent(new Event('abort')); disposed.abort(); assert.equal(disposedCalls, 0);
    const controller = new AbortController(), order = []; let later;
    addAbortListener(controller.signal, () => { order.push('first listener'); later[disposeSymbol](); });
    later = addAbortListener(controller.signal, () => order.push('disposed later listener'));
    controller.abort(); later[disposeSymbol]();
    assert.deepEqual(order, ['first listener']);
    return { disposedCalls, order, realSignalRemovalEffectIdempotent: true };
  });

  await test('manual abort event consumes once registration without changing signal state', () => {
    const controller = new AbortController(), callbacks = [];
    addAbortListener(controller.signal, function(event) { callbacks.push({ signalThis: this === controller.signal,
      type: event.type, aborted: controller.signal.aborted, isTrusted: event.isTrusted }); });
    const first = controller.signal.dispatchEvent(new Event('abort'));
    const beforeRealAbort = controller.signal.aborted;
    const second = controller.signal.dispatchEvent(new Event('abort'));
    controller.abort('real reason');
    assert.deepEqual(callbacks, [{ signalThis: true, type: 'abort', aborted: false, isTrusted: false }]);
    assert.equal(beforeRealAbort, false); assert.equal(controller.signal.aborted, true);
    return { callbacks, beforeRealAbort, realAbortState: controller.signal.aborted, dispatchReturnValues: [first, second] };
  });

  await test('manual event after already-aborted registration does not replace queued callback', async () => {
    const controller = new AbortController(), order = []; controller.abort();
    addAbortListener(controller.signal, (...args) => { order.push(`queued listener:${args.length}`); });
    controller.signal.dispatchEvent(new Event('abort')); order.push('after manual dispatch');
    await Promise.resolve(); assert.deepEqual(order, ['after manual dispatch', 'queued listener:0']);
    return { order };
  });

  await test('registration inside real abort callback observes already-aborted microtask path', async () => {
    const controller = new AbortController(), order = [];
    addAbortListener(controller.signal, () => {
      order.push('first listener'); addAbortListener(controller.signal, (...args) => order.push(`late listener:${args.length}`));
    });
    controller.abort(); order.push('after abort'); await Promise.resolve(); order.push('after checkpoint');
    assert.deepEqual(order, ['first listener', 'after abort', 'late listener:0', 'after checkpoint']);
    return { order };
  });

  await test('duplicate protected registrations share one listener tuple and either disposer removes it', () => {
    const controller = new AbortController(); let calls = 0;
    const callback = () => calls++;
    const first = addAbortListener(controller.signal, callback), second = addAbortListener(controller.signal, callback);
    assert.notEqual(first, second);
    second[disposeSymbol](); controller.abort(); controller.signal.dispatchEvent(new Event('abort'));
    first[disposeSymbol](); second[disposeSymbol](); assert.equal(calls, 0);
    const other = new AbortController(); let undisposedCalls = 0;
    const same = () => undisposedCalls++;
    addAbortListener(other.signal, same); addAbortListener(other.signal, same);
    other.abort(); other.signal.dispatchEvent(new Event('abort')); assert.equal(undisposedCalls, 1);
    return { disposableObjectsDistinct: true, callsAfterOneDisposer: calls, undisposedDuplicateCalls: undisposedCalls };
  });

  await test('ordinary callback registered first is not upgraded to protected or once', () => {
    const stopped = new AbortController(), stoppedOrder = [];
    const callback = () => stoppedOrder.push('ordinary duplicate');
    stopped.signal.addEventListener('abort', event => { stoppedOrder.push('stopper'); event.stopImmediatePropagation(); });
    stopped.signal.addEventListener('abort', callback);
    addAbortListener(stopped.signal, callback);
    addAbortListener(stopped.signal, () => stoppedOrder.push('different protected callback'));
    stopped.abort(); assert.deepEqual(stoppedOrder, ['stopper', 'different protected callback']);
    const repeated = new AbortController(); let calls = 0;
    const ordinary = () => calls++;
    repeated.signal.addEventListener('abort', ordinary);
    const resource = addAbortListener(repeated.signal, ordinary);
    repeated.signal.dispatchEvent(new Event('abort')); repeated.signal.dispatchEvent(new Event('abort')); repeated.abort();
    assert.equal(calls, 3);
    resource[disposeSymbol](); repeated.signal.dispatchEvent(new Event('abort')); assert.equal(calls, 3);
    return { stoppedOrder, ordinaryFirstRemainsNonOnceCalls: calls,
      protectedDuplicateDoesNotReplaceExistingTupleFlags: true };
  });

  await test('protected callback registered first keeps its flags after an ordinary duplicate', () => {
    const controller = new AbortController(), order = [];
    controller.signal.addEventListener('abort', event => { order.push('stopper'); event.stopImmediatePropagation(); });
    const callback = () => order.push('protected callback');
    addAbortListener(controller.signal, callback);
    controller.signal.addEventListener('abort', callback);
    controller.abort(); controller.signal.dispatchEvent(new Event('abort'));
    assert.deepEqual(order, ['stopper', 'protected callback', 'stopper']);
    return { order, laterOrdinaryDuplicateDidNotRemoveProtectionOrOnce: true };
  });

  await test('fresh and synthetic dispatch use dispatch ALS context; queued path uses registration ALS context', async () => {
    const storage = new AsyncLocalStorage(), observed = [];
    try {
      const fresh = new AbortController();
      storage.run('FRESH_REGISTER', () => addAbortListener(fresh.signal, () => observed.push({
        label: 'fresh listener', store: storage.getStore() })));
      storage.run('FRESH_DISPATCH', () => fresh.abort());
      const manual = new AbortController();
      storage.run('MANUAL_REGISTER', () => addAbortListener(manual.signal, () => observed.push({
        label: 'manual listener', store: storage.getStore() })));
      storage.run('MANUAL_DISPATCH', () => manual.signal.dispatchEvent(new Event('abort')));
      const already = new AbortController(); already.abort();
      storage.run('QUEUED_REGISTER', () => addAbortListener(already.signal, () => observed.push({
        label: 'already-aborted listener', store: storage.getStore() })));
      await Promise.resolve();
      assert.deepEqual(observed, [
        { label: 'fresh listener', store: 'FRESH_DISPATCH' },
        { label: 'manual listener', store: 'MANUAL_DISPATCH' },
        { label: 'already-aborted listener', store: 'QUEUED_REGISTER' },
      ]);
      assert.equal(storage.getStore(), undefined);
      return { observed, rootStoreRestored: true, implementation: 'actual node:async_hooks AsyncLocalStorage' };
    } finally { storage.disable(); }
  });
  await immediate(); process.off('warning', onWarning);
  return { cases, warnings };
}

if (process.argv[2] === '--throw-child') {
  const mode = process.argv[3]; assert(['fresh', 'already-aborted'].includes(mode));
  console.log(JSON.stringify(await throwChild(mode)));
} else {
  const runtime = await mainCases(), children = [];
  for (const mode of ['fresh', 'already-aborted']) {
    const child = spawnSync(process.execPath, [sourcePath, '--throw-child', mode], {
      encoding: 'utf8', env: process.env, timeout: 30000, maxBuffer: 1024 * 1024,
    });
    assert.equal(child.status, 0, child.error?.message ?? child.stderr);
    children.push({ ...JSON.parse(child.stdout), exitStatus: child.status,
      stderr: child.stderr.replace(/\(node:\d+\)/g, '(node:<PID>)') });
  }
  const report = { schemaVersion: 1, state: 'verified-public-node22-addAbortListener-oracle',
    recordedAtUtc: new Date().toISOString(), nodePin, node: process.version, executable: process.execPath,
    executableSha256: hash(await readFile(process.execPath)), runnerSha256: hash(await readFile(sourcePath)),
    execArgv: process.execArgv, nodeOptionsPresent: Boolean(process.env.NODE_OPTIONS),
    caseCount: runtime.cases.length, ...runtime, isolatedListenerThrowCases: children,
    scope: 'Valid public Node event/AbortSignal operations, structural input validation observations and isolated public uncaughtException reporting. No Node private binding or guest/native instrumentation is used.',
    limitations: ['This is a Node reference oracle, not a StarlingMonkey implementation/component proof.',
      'Structural fake acceptance and repeated fake remover side effects are recorded Node behavior; a bounded guest profile may deliberately reject fakes with an explicit deviation.',
      'No GC/finalizer/resource-retention claim follows from ordinary disposal and callback counts.',
      'Only synchronous listener throws are covered; async listener rejection/reporting semantics are not inferred.'] };
  await writeFile(join(here, 'node-results.json'), JSON.stringify(report, null, 2) + '\n');
  const sourceRoot = resolve(process.env.NODE_COMPAT_ADD_ABORT_NODE_SOURCE ?? '/tmp/starling-node-compat/foundation-add-abort/node-v22.14.0-source');
  const paths = ['lib/events.js', 'lib/internal/events/abort_listener.js', 'lib/internal/event_target.js',
    'lib/internal/abort_controller.js', 'lib/internal/validators.js', 'lib/internal/util.js',
    'lib/internal/process/task_queues.js', 'test/parallel/test-events-add-abort-listener.mjs',
    'test/parallel/test-event-target.js', 'test/parallel/test-eventtarget.js', 'doc/api/events.md'];
  const files = [];
  for (let i = 0; i < paths.length; i += 4) {
    const group = await Promise.all(paths.slice(i, i + 4).map(async path => {
      const url = `https://raw.githubusercontent.com/nodejs/node/${nodePin.revision}/${path}`;
      const response = await fetch(url); assert(response.ok, `${response.status}: ${url}`);
      const bytes = new Uint8Array(await response.arrayBuffer()), localPath = join(sourceRoot, path);
      await mkdir(dirname(localPath), { recursive: true }); await writeFile(localPath, bytes);
      return { path, url, localPath, bytes: bytes.length, sha256: hash(bytes) };
    }));
    files.push(...group);
  }
  const ledger = { schemaVersion: 1, state: 'official-pinned-addAbortListener-source-ledger',
    recordedAtUtc: new Date().toISOString(), nodePin, runnerSha256: hash(await readFile(sourcePath)), files,
    sourceSymbols: [
      { path: 'lib/events.js', symbol: 'addAbortListener export', line: 223 },
      { path: 'lib/internal/events/abort_listener.js', symbol: 'addAbortListener', line: 23 },
      { path: 'lib/internal/validators.js', symbol: 'validateAbortSignal', line: 442 },
      { path: 'lib/internal/event_target.js', symbol: 'kResistStopPropagation', line: 65 },
      { path: 'lib/internal/event_target.js', symbol: 'Listener.same', line: 522 },
      { path: 'lib/internal/event_target.js', symbol: 'EventTarget.addEventListener duplicate check', line: 673 },
      { path: 'lib/internal/event_target.js', symbol: 'EventTarget dispatch iteration', line: 791 },
      { path: 'lib/internal/event_target.js', symbol: 'emitUncaughtException', line: 1100 },
      { path: 'lib/internal/util.js', symbol: 'SymbolDispose', line: 922 },
    ],
    scope: 'Official source/tests downloaded by immutable Node commit and hashed. Source describes Node internal dispatch hooks; none is invoked or inspected through a private runtime API. Official test files are not executed.',
    referenceOracle: { path: join(here, 'node-results.json'), sha256: hash(await readFile(join(here, 'node-results.json'))) } };
  await writeFile(join(here, 'node-source-ledger.json'), JSON.stringify(ledger, null, 2) + '\n');
  console.log(JSON.stringify({ node: process.version, passed: true, caseCount: report.caseCount,
    isolatedListenerThrowCases: children.length, warnings: report.warnings.length, sourceFiles: files.length }, null, 2));
}
