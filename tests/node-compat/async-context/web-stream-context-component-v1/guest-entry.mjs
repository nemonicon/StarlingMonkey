// Single-source public ALS/stream controls. INIT creates only inert definitions.
import { bootstrap } from 'starling:node-startup';
import { runFreshRequest, runNeutralServer } from 'starling:node-http';
import asyncHooks, { AsyncLocalStorage, AsyncResource } from 'node:async_hooks';
import * as types from 'wasi:http/types@0.2.10';
// Standard WASI HTTP resource ownership -> ordinary Web Request/Response.
// `types` is the actual wasi:http/types@0.2.10 namespace in guest-entry.mjs.
const drop = value => { if (value) value[Symbol.dispose](); };
function text(bytes) {
  let out = '';
  for (const byte of bytes) out += String.fromCharCode(byte);
  return out;
}
function bytes(value) {
  const result = new Uint8Array(value.length);
  for (let i = 0; i < value.length; i++) {
    const code = value.charCodeAt(i);
    if (code > 255) throw new TypeError('HTTP header values must be ByteStrings');
    result[i] = code;
  }
  return result;
}
// js-component-bindgen throws ComponentError with an own DATA payload.
// Only these explicit WIT stream-error records are interpreted. Unknown throws
// (including falsy values) keep their original identity; no message coercion.
function ownData(value,key) {
  if(value===null || (typeof value!=='object' && typeof value!=='function'))return undefined;
  const descriptor=Object.getOwnPropertyDescriptor(value,key);
  return descriptor && Object.prototype.hasOwnProperty.call(descriptor,'value')?descriptor.value:undefined;
}
function streamError(value) {
  const payload=ownData(value,'payload');
  const variant=payload===undefined?value:payload;
  const tag=ownData(variant,'tag');
  if(tag==='closed')return {tag};
  if(tag==='last-operation-failed') {
    const resource=ownData(variant,'val');
    if(resource!==null && (typeof resource==='object' || typeof resource==='function'))return {tag,val:resource};
  }
  return undefined;
}
function diagnosticMethod(resource,name) {
  for(let object=resource,depth=0;object!==null && depth<4;object=Object.getPrototypeOf(object),depth++) {
    const descriptor=Object.getOwnPropertyDescriptor(object,name);
    if(descriptor) {
      if(Object.prototype.hasOwnProperty.call(descriptor,'value') && typeof descriptor.value==='function')return descriptor.value;
      throw new TypeError('WASI diagnostic method must be a DATA function');
    }
  }
  throw new TypeError('WASI diagnostic method missing');
}
function streamFailure(value) {
  const variant=streamError(value);
  if(variant?.tag==='last-operation-failed') {
    const resource=variant.val;
    let message;
    try {
      message=Reflect.apply(diagnosticMethod(resource,'toDebugString'),resource,[]);
      if(typeof message!=='string')throw new TypeError('WASI diagnostic must return a synchronous string');
    } finally {drop(resource);}
    const error=new Error(message);
    Object.defineProperty(error,'cause',{value,configurable:true,writable:true});
    return error;
  }
  return value;
}

function createWasiHttpHandler(webHandler, types, runFreshRequest) {
  if (typeof runFreshRequest !== "function") throw new TypeError("Native request entry is required");
  const {Fields, IncomingBody, OutgoingBody, OutgoingResponse, ResponseOutparam} = types;
  async function handleResources(incoming, outparam) {
      let inputBody, inputStream, outgoingResponse, outputBody, outputStream, responseReader;
      let incomingEnded = false, responseSet = false, outputFinished = false;
      function releaseInput() {
        const stream = inputStream; inputStream = undefined;
        drop(stream);
        const body = inputBody; inputBody = undefined;
        if (body) {
          if (incomingEnded) drop(IncomingBody.finish(body));
          else drop(body);
        }
      }
      try {
        const fieldResource = incoming.headers();
        const headers = new Headers();
        try { for (const [name, value] of fieldResource.entries()) headers.append(name, text(value)); }
        finally { drop(fieldResource); }
        const scheme = incoming.scheme();
        const protocol = scheme?.tag === 'other' ? scheme.val : scheme?.tag ?? 'http';
        const authority = incoming.authority() ?? headers.get('host') ?? 'localhost';
        const methodValue = incoming.method();
        const method = methodValue.tag === 'other' ? methodValue.val : methodValue.tag.toUpperCase();
        const url = protocol + '://' + authority + (incoming.pathWithQuery() ?? '/');
        inputBody = incoming.consume();
        let body;
        if (!['GET', 'HEAD'].includes(method)) {
          inputStream = inputBody.stream();
          body = new ReadableStream({
            pull(controller) {
              try {
                const chunk = inputStream.blockingRead(64n * 1024n);
                if (chunk.length) controller.enqueue(chunk);
              } catch (error) {
                if (streamError(error)?.tag === 'closed') {
                  incomingEnded = true;
                  releaseInput();
                  controller.close();
                } else {
                  releaseInput();
                  controller.error(streamFailure(error));
                }
              }
            },
            cancel() { releaseInput(); },
          });
        }
        const request = new Request(url, {method, headers, ...(body ? {body, duplex: 'half'} : {})});
        const response = await webHandler(request);
        const fields = [];
        for (const [name, value] of response.headers) if (name !== 'set-cookie') fields.push([name, bytes(value)]);
        const cookies = response.headers.getSetCookie?.() ?? (response.headers.get('set-cookie') ? [response.headers.get('set-cookie')] : []);
        for (const value of cookies) fields.push(['set-cookie', bytes(value)]);
        outgoingResponse = new OutgoingResponse(Fields.fromList(fields));
        outgoingResponse.setStatusCode(response.status);
        outputBody = outgoingResponse.body();
        const outgoing = outgoingResponse; outgoingResponse = undefined;
        responseSet = true;
        ResponseOutparam.set(outparam, {tag: 'ok', val: outgoing});
        outputStream = outputBody.write();
        if (response.body) {
          responseReader = response.body.getReader();
          for (;;) {
            const part = await responseReader.read();
            if (part.done) break;
            for (let offset = 0; offset < part.value.byteLength; offset += 4096) {
              outputStream.blockingWriteAndFlush(part.value.subarray(offset, offset + 4096));
            }
          }
        }
        const stream = outputStream; outputStream = undefined;
        drop(stream);
        outputFinished = true;
        OutgoingBody.finish(outputBody, undefined);
      } catch (error) {
        if (responseReader) try { await responseReader.cancel(error); } catch {}
        throw streamFailure(error);
      } finally {
        releaseInput();
        drop(outputStream);
        if (outputBody && !outputFinished) drop(outputBody);
        drop(outgoingResponse);
        if (!responseSet) drop(outparam);
        drop(incoming);
      }
  }
  return {
    handle(incoming, outparam) {
      let entered=false;
      try {
        return runFreshRequest((...args)=>{
          entered=true;
          return handleResources(...args);
        },undefined,incoming,outparam);
      } catch(error) {
        if(!entered)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  };
}

// The caller still owns incoming/outparam until native callback entry. Always
// attempt both drops, preserving the original pre-entry error even if cleanup
// itself refuses. Cleanup failure is diagnostic and cannot turn into success.
function disposeBeforeEntry(incoming,outparam) {
  let failures=0;
  for(const value of [incoming,outparam])try{drop(value);}catch{failures++;}
  if(failures)try{console.error('NEXT_COMPONENT_PRE_ENTRY_DISPOSAL_FAILURE',failures);}catch{}
}

// Pure orchestration, inlined unchanged into each raw guest entry.
function createNeutralReadyHandler({runNeutralServer,prepareServer,disposeBeforeEntry}) {
  let readiness;
  return Object.freeze({
    handle(incoming,outparam) {
      let enteredNeutral=false;
      try {
        return runNeutralServer(async () => {
          enteredNeutral=true;
          let handler;
          try {
            // Both promise allocation and all preparation happen neutrally.
            // One sticky promise per component instance: concurrent first
            // requests share success or the original rejection, never retry.
            readiness ??= Promise.resolve().then(prepareServer);
            handler=await readiness;
            if(!handler||typeof handler.handle!=='function')
              throw new TypeError('Preparation must return the real WASI handler');
          } catch(error) {
            disposeBeforeEntry(incoming,outparam);
            throw error;
          }
          // The adapter owns both resources from here. It enters native fresh
          // request context BEFORE constructing headers, body or Web Request.
          return handler.handle(incoming,outparam);
        },undefined);
      } catch(error) {
        if(!enteredNeutral)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  });
}


// BEGIN EXACT SHARED V2 CASES, export keywords removed only.
const contextCase = (() => {
// Public API observations only. No AsyncResource facade or host-specific imports.
const CASE_IDS = Object.freeze([
  'readable-pull', 'readable-cancel', 'writable-write-close', 'writable-abort',
  'transform-write-flush', 'bind-throw-reject', 'snapshot-throw-reject', 'queue-microtask',
]);

function describeThrown(value) {
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

async function runWebStreamContextCases({ AsyncLocalStorage, runFresh = callback => callback(),
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

return { CASE_IDS, describeThrown, runWebStreamContextCases };
})();
// END EXACT SHARED V2 CASES.
// BEGIN EXACT CLONE CASE, export keywords removed only.
const cloneCase = (() => {
// Inert at import. Call only inside an explicitly owned ordinary execution.
function describeThrown(value) {
  const type=value===null?'null':typeof value;
  if(['undefined','null'].includes(type))return {type};
  if(['string','boolean','number'].includes(type))return {type,value:type==='string'?value.slice(0,512):value};
  const out={type};
  if(type==='object')try{for(const key of ['name','message','code']){
    const descriptor=Object.getOwnPropertyDescriptor(value,key);
    if(descriptor&&'value'in descriptor&&['string','boolean','number'].includes(typeof descriptor.value))
      out[key]=typeof descriptor.value==='string'?descriptor.value.slice(0,512):descriptor.value;
  }}catch{out.descriptionUnavailable=true;}
  return out;
}

async function runResponseCloneCancelCase({report}) {
  if(!report||typeof report!=='object'||Object.keys(report).length!==0)
    throw new TypeError('Caller-owned empty report required');
  if(typeof globalThis.ReadableStream!=='function'||typeof globalThis.Response!=='function')
    throw new TypeError('Real global ReadableStream and Response required');
  Object.assign(report,{schemaVersion:1,case:'RESPONSE_CLONE_BOTH_CANCEL_OBSERVATION_V1',
    collectionComplete:false,semanticAccepted:null,expectedFromNode:null,
    sourceCancelCalls:0,sourceCancelReasons:[],events:[],snapshots:[],observationOverflow:false,
    microtaskCheckpointRounds:2,sourceGateReleased:false,nativeResourceCountsProved:false});
  const firstReason={marker:'response-clone-first-reason'};
  const secondReason={marker:'response-clone-second-reason'};
  let release,first,second,original,clone;
  const sourceGate=new Promise(resolve=>{release=resolve;});
  const states={first:{state:'not-requested'},second:{state:'not-requested'}};
  function event(kind,detail={}){
    if(report.events.length>=32){report.observationOverflow=true;return;}
    report.events.push({sequence:report.events.length+1,kind,...detail});
  }
  function reasonEvidence(reason){
    return {type:reason===null?'null':typeof reason,isArray:Array.isArray(reason),
      isFirstObject:reason===firstReason,isSecondObject:reason===secondReason,
      arrayLength:Array.isArray(reason)?reason.length:null,
      firstElementIsFirstObject:Array.isArray(reason)&&reason[0]===firstReason,
      secondElementIsSecondObject:Array.isArray(reason)&&reason[1]===secondReason};
  }
  function observe(label,body,reason){
    states[label]={state:'pending'};event('cancel-invocation',{branch:label});
    try{
      const promise=body.cancel(reason);
      states[label].returnedSameRealmPromise=promise instanceof Promise;
      // Both handlers are attached immediately, before the next branch is touched.
      return Promise.resolve(promise).then(value=>{
        states[label]={...states[label],state:'fulfilled',value:describeThrown(value)};
        event('cancel-settled',{branch:label,outcome:'fulfilled'});return states[label];
      },error=>{
        states[label]={...states[label],state:'rejected',error:describeThrown(error)};
        event('cancel-settled',{branch:label,outcome:'rejected'});return states[label];
      });
    }catch(error){
      states[label]={state:'threw',error:describeThrown(error)};
      event('cancel-threw',{branch:label});return Promise.resolve(states[label]);
    }
  }
  function snapshot(phase){
    report.snapshots.push({phase,first:{...states.first},second:{...states.second},
      sourceCancelCalls:report.sourceCancelCalls,sourceGateReleased:report.sourceGateReleased,
      originalBodyUsed:original.bodyUsed,cloneBodyUsed:clone.bodyUsed});
  }
  async function checkpoint(){await Promise.resolve();await Promise.resolve();}
  function releaseSource(){
    if(!report.sourceGateReleased){report.sourceGateReleased=true;event('source-gate-release');release();}
  }
  try{
    const source=new ReadableStream({
      start(controller){event('source-start');controller.enqueue(new Uint8Array([0x43]));},
      cancel(reason){
        report.sourceCancelCalls++;
        if(report.sourceCancelReasons.length<4)report.sourceCancelReasons.push(reasonEvidence(reason));
        else report.observationOverflow=true;
        event('source-cancel-enter');
        return sourceGate.then(()=>{event('source-cancel-return-gate-settled');});
      }
    });
    original=new Response(source,{status:200,headers:{'x-clone-case':'bounded'}});
    clone=original.clone();snapshot('after-clone');
    first=observe('first',original.body,firstReason);snapshot('after-first-cancel-sync');
    await checkpoint();snapshot('before-second-cancel-after-checkpoint');
    second=observe('second',clone.body,secondReason);snapshot('after-second-cancel-sync');
    await checkpoint();snapshot('after-second-checkpoint-before-source-release');
    releaseSource();
    // Never await the first cancellation before requesting cancellation of branch2.
    await Promise.all([first,second]);
    snapshot('after-source-release-and-both-settlements');
    report.cancelOutcomes={first:{...states.first},second:{...states.second}};
    report.responseMetadata={originalStatus:original.status,cloneStatus:clone.status,
      originalHeader:original.headers.get('x-clone-case'),cloneHeader:clone.headers.get('x-clone-case')};
    report.collectionComplete=!report.observationOverflow;
    return report;
  }finally{
    // Also releases a source cancellation held by any earlier exceptional path.
    releaseSource();
    if(first===undefined&&original)first=observe('first',original.body,firstReason);
    if(second===undefined&&clone)second=observe('second',clone.body,secondReason);
    // observe() already handles rejection; do not await an unresolved branch here.
  }
}

return { describeThrown, runResponseCloneCancelCase };
})();
// END EXACT CLONE CASE.

// New dispatch only. The adapter and both case bodies above are derived separately.
function ownErrorData(value, name) {
  if (value === null || (typeof value !== 'object' && typeof value !== 'function')) return null;
  const descriptor = Object.getOwnPropertyDescriptor(value, name);
  return descriptor && Object.hasOwn(descriptor, 'value') && typeof descriptor.value === 'string' ? descriptor.value : null;
}
function publicAsyncResourceRefusal() {
  const records = [];
  for (const [binding, Constructor] of [['named', AsyncResource], ['default', asyncHooks.AsyncResource]]) {
    let threw = false, error;
    try { new Constructor('public-native-refusal-probe'); }
    catch (value) { threw = true; error = value; }
    const row = { binding, constructorType: typeof Constructor, threw,
      errorIsError: threw && error instanceof Error, code: ownErrorData(error, 'code'),
      module: ownErrorData(error, 'module'), operation: ownErrorData(error, 'operation'), profile: ownErrorData(error, 'profile') };
    row.passed = row.constructorType === 'function' && row.threw && row.errorIsError &&
      row.code === 'ERR_SM_NODE_UNSUPPORTED' && row.module === 'node:async_hooks' &&
      row.operation === 'AsyncResource' && row.profile === 'sm-node-22.14.0-m1.0';
    records.push(row);
  }
  const namedAndDefaultConstructorSame = AsyncResource === asyncHooks.AsyncResource;
  return { scope: 'guest-only-public-native-unsupported-contract', facadeInstalled: false,
    namedAndDefaultConstructorSame,
    records, passed: namedAndDefaultConstructorSame && records.every(row => row.passed) };
}
function publishJson(envelope, status, primarySet = false, primary) {
  try {
    const body = new TextEncoder().encode(JSON.stringify(envelope));
    if (body.byteLength > 128 * 1024) throw new Error('control response exceeds 128 KiB');
    return new Response(body, { status,
      headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
  } catch (secondary) { if (primarySet) throw primary; throw secondary; }
}
async function cloneWithDeadline(report) {
  let timer;
  const task = Promise.resolve().then(() => cloneCase.runResponseCloneCancelCase({ report }));
  task.then(() => {}, () => {});
  const expired = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error('clone-cancel five-second observation deadline')), 5000);
  });
  try { await Promise.race([task, expired]); }
  finally { clearTimeout(timer); }
}
async function preparePublicContextServer() {
  const process = bootstrap();
  if (globalThis.process !== process) throw new Error('Actual native process identity mismatch');
  const handler = async request => {
    const url = new URL(request.url);
    if (request.method !== 'GET') return publishJson({ schemaVersion: 1, marker: 'PUBLIC_CONTEXT_CONTROL_METHOD_REFUSED_V1' }, 405);
    if (url.search !== '' || !['/context', '/clone-cancel'].includes(url.pathname)) {
      return publishJson({ schemaVersion: 1, marker: 'PUBLIC_CONTEXT_CONTROL_ROUTE_REFUSED_V1' }, 404);
    }
    let primarySet = false, primary;
    if (url.pathname === '/context') {
      const report = { executionKind: 'component-guest', guestExecuted: true };
      let refusal;
      try {
        refusal = publicAsyncResourceRefusal();
        await contextCase.runWebStreamContextCases({ AsyncLocalStorage,
          runFresh: callback => runFreshRequest(callback, undefined), boundaryMode: 'native-boundaries', report });
      } catch (error) { primarySet = true; primary = error; }
      const passed = !primarySet && report.passed === true && refusal?.passed === true;
      return publishJson({ schemaVersion: 1, marker: 'PUBLIC_ALS_WEB_STREAM_COMPONENT_V1',
        route: '/context', collection: report, publicAsyncResourceRefusal: refusal ?? null,
        primarySet, ...(primarySet ? { primary: contextCase.describeThrown(primary) } : {}),
        passed, fullNextAccepted: false }, passed ? 200 : 500, primarySet, primary);
    }
    const report = {};
    try { await cloneWithDeadline(report); }
    catch (error) { primarySet = true; primary = error; }
    const collectionComplete = !primarySet && report.collectionComplete === true;
    // This route reports observations, not a manufactured Node semantic expectation.
    return publishJson({ schemaVersion: 1, marker: 'RESPONSE_CLONE_CANCEL_COMPONENT_OBSERVATION_V1',
      route: '/clone-cancel', collection: report, primarySet,
      ...(primarySet ? { primary: cloneCase.describeThrown(primary) } : {}),
      collectionComplete, semanticAccepted: null, comparedToNode: false,
      taskCancellationProved: false, fullNextAccepted: false }, collectionComplete ? 200 : 500, primarySet, primary);
  };
  return createWasiHttpHandler(handler, types, runFreshRequest);
}
export const incomingHandler = createNeutralReadyHandler({ runNeutralServer,
  prepareServer: preparePublicContextServer, disposeBeforeEntry });
