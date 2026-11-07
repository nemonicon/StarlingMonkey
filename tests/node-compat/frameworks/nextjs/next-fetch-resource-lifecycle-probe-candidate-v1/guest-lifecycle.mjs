// Generated dormant public-fetch lifecycle entry; no HTTP, app or entropy at INIT.
import {bootstrap} from 'starling:node-startup';
import {runFreshRequest, runNeutralServer} from 'starling:node-http';
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


// Dormant guest collector. Every fetch is the guest's installed global fetch.
// No transport, task, resource-count, timing or private Store inference is made.
const lifecycleCaseIds = Object.freeze([
  'read-eof-metadata', 'bodyall-text', 'bodyall-json', 'bodyall-arraybuffer',
  'repeat-read-eof', 'clone-one-cancel-other-drain',
  'direct-reader-cancel-pending', 'direct-reader-cancel-after-read',
]);
const lifecycleBodyCap = 4096;

function lifecycleOrigin(value) {
  if (typeof value !== 'string' || value.length > 128) throw new TypeError('Explicit control origin required');
  const url = new URL(value);
  if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || !url.port ||
      url.username || url.password || url.pathname !== '/' || url.search || url.hash || url.origin !== value)
    throw new TypeError('Control must be a canonical explicit-port http://127.0.0.1 origin');
  return value;
}

function lifecycleError(value) {
  const result = {type: typeof value, isNull: value === null, isTypeError: value instanceof TypeError};
  for (const key of ['name', 'message', 'code']) {
    try { const text = value?.[key]; result[key] = typeof text === 'string' ? text.slice(0, 512) : null; }
    catch { result[key] = null; }
  }
  return result;
}
function lifecycleHex(value) {
  if (!(value instanceof Uint8Array)) throw new TypeError('Byte stream required');
  let out = ''; for (const byte of value) out += byte.toString(16).padStart(2, '0'); return out;
}
function lifecycleMeta(response) {
  return {status: response.status, url: response.url, contentType: response.headers.get('content-type'),
    bodyUsed: response.bodyUsed};
}
async function lifecycleOutcome(action) {
  try { const value = await action(); return {fulfilled: true, valueUndefined: value === undefined}; }
  catch (error) { return {fulfilled: false, error: lifecycleError(error)}; }
}
function lifecyclePart(part) {
  return {done: part.done, valueUndefined: part.value === undefined,
    hex: part.value === undefined ? null : lifecycleHex(part.value)};
}
async function lifecycleDrain(response, observation, cleanupErrors) {
  const reader = response.body.getReader();
  let complete = false, bytes = 0;
  observation.hex = ''; observation.parts = [];
  try {
    for (;;) {
      const part = await reader.read();
      if (part.done) { complete = true; observation.eof = lifecyclePart(part); break; }
      const remaining = lifecycleBodyCap - bytes;
      observation.hex += lifecycleHex(part.value.subarray(0, Math.max(remaining, 0)));
      bytes += part.value.byteLength; observation.receivedBytes = bytes;
      observation.parts.push(part.value.byteLength);
      if (bytes > lifecycleBodyCap) throw new RangeError('Declared 4096-byte response cap exceeded; prefix retained');
    }
    observation.closed = await lifecycleOutcome(() => reader.closed);
  } finally {
    if (!complete) {
      const canceled = await lifecycleOutcome(() => reader.cancel());
      if (!canceled.fulfilled) cleanupErrors.push({operation: 'cancel-incomplete-read', ...canceled});
    }
    try { reader.releaseLock(); } catch (error) { cleanupErrors.push({operation: 'releaseLock', error: lifecycleError(error)}); }
    observation.complete = complete;
  }
}

async function collectFetchLifecycle(origin) {
  origin = lifecycleOrigin(origin);
  const output = {schemaVersion: 1, executor: 'guest-global-fetch', origin,
    caseIds: [...lifecycleCaseIds], records: [], allCasesAttempted: false};
  const run = async (id, body) => {
    const record = {id, observations: {}, error: null, cleanupErrors: [], captureLogError: null};
    output.records.push(record);
    try { await body(record.observations, record.cleanupErrors); }
    catch (error) { record.error = lifecycleError(error); }
    // Ordinary deployed stdout: completed raw case capture precedes semantics.
    try { console.log('NEXT_FETCH_LIFECYCLE_CASE_V1 ' + JSON.stringify(record)); }
    catch (error) { record.captureLogError = lifecycleError(error); }
  };
  const jsonUrl = origin + '/api/json?q=lifecycle-v1';
  const get = path => globalThis.fetch(origin + path, {method: 'GET', redirect: 'error'});
  await run('read-eof-metadata', async (o, cleanup) => {
    const response = await get('/api/json?q=lifecycle-v1'); o.before = lifecycleMeta(response);
    await lifecycleDrain(response, o, cleanup); o.after = lifecycleMeta(response);
  });
  for (const method of ['text', 'json', 'arrayBuffer']) {
    const id = method === 'arrayBuffer' ? 'bodyall-arraybuffer' : 'bodyall-' + method;
    await run(id, async o => {
      const response = await get('/api/json?q=lifecycle-v1'); o.before = lifecycleMeta(response);
      const value = await response[method]();
      if (method === 'arrayBuffer') o.hex = lifecycleHex(new Uint8Array(value)); else o.value = value;
      o.after = lifecycleMeta(response);
      o.secondRead = await lifecycleOutcome(() => response.text());
    });
  }
  await run('repeat-read-eof', async (o, cleanup) => {
    o.responses = [];
    for (let ordinal = 1; ordinal <= 4; ordinal++) {
      const item = {ordinal}; o.responses.push(item);
      const response = await get('/api/health'); item.before = lifecycleMeta(response);
      await lifecycleDrain(response, item, cleanup); item.after = lifecycleMeta(response);
    }
  });
  await run('clone-one-cancel-other-drain', async (o, cleanup) => {
    const response = await get('/api/json?q=lifecycle-v1'), clone = response.clone();
    o.before = lifecycleMeta(response); o.cloneBefore = lifecycleMeta(clone);
    const reader = response.body.getReader();
    // Attach settlement immediately; do not await one tee branch before draining the other.
    const canceled = lifecycleOutcome(() => reader.cancel('lifecycle-one-branch'));
    try {
      await lifecycleDrain(clone, o, cleanup);
      o.cancel = await canceled; o.canceledClosed = await lifecycleOutcome(() => reader.closed);
      o.after = lifecycleMeta(response); o.cloneAfter = lifecycleMeta(clone);
    } finally {
      try { reader.releaseLock(); } catch (error) { cleanup.push({operation: 'clone-releaseLock', error: lifecycleError(error)}); }
    }
  });
  for (const afterRead of [false, true]) {
    await run(afterRead ? 'direct-reader-cancel-after-read' : 'direct-reader-cancel-pending', async (o, cleanup) => {
      const response = await get('/api/json?q=lifecycle-v1'); o.before = lifecycleMeta(response);
      const reader = response.body.getReader();
      try {
        if (afterRead) o.firstRead = lifecyclePart(await reader.read());
        // Both settlements get handlers before either is awaited. A tiny response may
        // already be buffered; these public calls do not attest queued/running tasks.
        const pending = afterRead ? null : reader.read().then(
          part => ({fulfilled: true, part: lifecyclePart(part)}),
          error => ({fulfilled: false, error: lifecycleError(error)}));
        const canceled = lifecycleOutcome(() => reader.cancel('lifecycle-direct-reader'));
        if (pending) o.pendingRead = await pending;
        o.cancel = await canceled; o.readAfterCancel = lifecyclePart(await reader.read());
        o.closed = await lifecycleOutcome(() => reader.closed); o.after = lifecycleMeta(response);
      } finally {
        try { reader.releaseLock(); } catch (error) { cleanup.push({operation: 'cancel-releaseLock', error: lifecycleError(error)}); }
      }
    });
  }
  output.allCasesAttempted = output.records.length === lifecycleCaseIds.length;
  // Preserve target declaration in the observation, independent of response metadata.
  output.expectedJsonUrl = jsonUrl;
  return output;
}

// All routing configuration, bootstrap and fetch occur after deployed entry.
async function prepareFetchLifecycleProbe() {
  const process = bootstrap();
  if (globalThis.process !== process) throw new Error('Native process identity mismatch');
  const origin = lifecycleOrigin(process.env.STARLING_FETCH_CONTROL_ORIGIN);
  let calls = 0;
  return createWasiHttpHandler(async request => {
    const url = new URL(request.url);
    if (request.method !== 'GET' || url.pathname !== '/fetch-lifecycle' || url.search !== '')
      return new Response('one predeclared GET /fetch-lifecycle required', {status: 404});
    if (++calls !== 1) return new Response('probe already called', {status: 409});
    const result = await collectFetchLifecycle(origin);
    return new Response(JSON.stringify({...result, call: calls}), {
      status: 200, headers: {'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store'},
    });
  }, types, runFreshRequest);
}
export const incomingHandler = createNeutralReadyHandler({
  runNeutralServer, prepareServer: prepareFetchLifecycleProbe, disposeBeforeEntry,
});
