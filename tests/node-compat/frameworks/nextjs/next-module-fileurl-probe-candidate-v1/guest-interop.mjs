// Generated Source-only loader probe; no fixtures or ordinary imports at INIT.
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


// Source-only declarations. Import, createRequire and fixture access are ordinary-call only.
const probeModes = Object.freeze(['guard', 'interop']);
const guardCaseIds = Object.freeze(['cjs-dynamic-builtin', 'guard-natural-fileurl-refusal']);
const interopCaseIds = Object.freeze([
  'cjs-dynamic-builtin', 'default-require-cache-identity', 'same-namespace',
  'thenable-default-not-assimilated', 'class-default-construction',
  'undefined-default', 'nan-default', 'negative-zero-default', 'throw-null-preserved',
  'query-refusal', 'fragment-refusal', 'encoded-separator-refusal',
  'uppercase-scheme-refusal', 'extension-refusal', 'url-byte-limit-refusal',
  'decoded-path-limit-refusal',
]);

function probeOwnData(object, key) {
  if (object === null || (typeof object !== 'object' && typeof object !== 'function')) return undefined;
  const descriptor = Object.getOwnPropertyDescriptor(object, key);
  return descriptor && Object.hasOwn(descriptor, 'value') ? descriptor.value : undefined;
}

function failureData(value) {
  const data = {type: typeof value, isNull: value === null};
  if (value === null || typeof value === 'boolean' || typeof value === 'string') data.value = value;
  if (typeof value === 'number') data.value = Number.isFinite(value) ? value : String(value);
  for (const key of ['name', 'message', 'code', 'operation', 'module']) {
    const item = probeOwnData(value, key);
    if (item === undefined) data[key] = {type: 'undefined'};
    else if (item === null || ['boolean', 'string', 'number'].includes(typeof item))
      data[key] = {type: typeof item, value: typeof item === 'string' ? item.slice(0, 512) : item};
    else data[key] = {type: typeof item};
  }
  return data;
}

function check(value, message) {
  if (value !== true) throw new Error('Module file-URL probe assertion: ' + message);
}

async function rejection(action) {
  try { return {rejected: false, value: await action()}; }
  catch (value) { return {rejected: true, value}; }
}

function refusalObservation(result, code, operation, specifier) {
  check(result.rejected === true, 'expected an actual rejected import');
  const error = result.value;
  const observation = {
    rejected: true,
    isTypeError: error instanceof TypeError,
    code: probeOwnData(error, 'code'), operation: probeOwnData(error, 'operation'),
    moduleMatchesActualSpecifier: probeOwnData(error, 'module') === specifier,
    error: failureData(error),
  };
  check(observation.isTypeError && observation.code === code && observation.operation === operation &&
    observation.moduleMatchesActualSpecifier, 'exact native refusal fields');
  return observation;
}

function namespaceObservation(namespace, expected) {
  const names = Object.getOwnPropertyNames(namespace);
  const observation = {
    prototypeNull: Object.getPrototypeOf(namespace) === null,
    ownNames: names,
    noOwnThen: !Object.hasOwn(namespace, 'then'),
    defaultSame: Object.is(namespace.default, expected),
  };
  check(observation.prototypeNull && names.length === 1 && names[0] === 'default' &&
    observation.noOwnThen && observation.defaultSame, 'single-default genuine namespace and exact value');
  return observation;
}

async function collectFileUrlProbe(mode) {
  if (!probeModes.includes(mode)) throw new TypeError('Unknown predeclared probe mode');
  const expectedIds = mode === 'guard' ? guardCaseIds : interopCaseIds;
  const records = [];
  const run = async (id, body) => {
    try { records.push({id, passed: true, observation: await body()}); }
    catch (error) { records.push({id, passed: false, error: failureData(error)}); }
  };
  // This function is invoked by the deployed GET handler, never during INIT.
  // The driver is loaded by the installed CJS loader. Its unmodified function
  // contains the natural import() expression; no eval or private metadata API.
  const {createRequire} = await import('node:module');
  const require = createRequire('/probe/driver.cjs');
  const driver = require('/probe/driver.cjs');
  check(typeof driver.load === 'function', 'real CJS driver');
  const targetUrl = 'file:///probe/target.cjs';
  await run('cjs-dynamic-builtin', async () => {
    const namespace = await driver.load('node:path');
    const builtin = require('node:path');
    const sameJoin = namespace.join === builtin.join;
    const joined = namespace.join('/probe', 'child');
    check(sameJoin && joined === '/probe/child', 'CJS import(node:path) remains usable');
    return {sameJoin, joined};
  });
  if (mode === 'guard') {
    await run('guard-natural-fileurl-refusal', async () => refusalObservation(
      await rejection(() => driver.load(targetUrl)),
      'ERR_SM_MODULE_IMPORT_REFERRER', 'module_load_hook', targetUrl));
  } else {
    let firstNamespace;
    await run('default-require-cache-identity', async () => {
      const value = require('/probe/target.cjs');
      firstNamespace = await driver.load(targetUrl);
      const observed = namespaceObservation(firstNamespace, value);
      const filename = require.resolve('/probe/target.cjs');
      const cache = probeOwnData(require.cache, filename);
      const loaded = probeOwnData(cache, 'loaded') === true;
      const cacheSame = probeOwnData(cache, 'exports') === value;
      check(filename === '/probe/target.cjs' && loaded && cacheSame && value.marker === 'target-value',
        'completed real require cache and value identity');
      return {...observed, filename, loaded, cacheSame, marker: value.marker};
    });
    await run('same-namespace', async () => {
      const again = await driver.load(targetUrl);
      const same = firstNamespace !== undefined && again === firstNamespace;
      check(same, 'successful repeated canonical import namespace identity');
      return {same};
    });
    await run('thenable-default-not-assimilated', async () => {
      const value = require('/probe/thenable.cjs');
      const namespace = await driver.load('file:///probe/thenable.cjs');
      const observed = namespaceObservation(namespace, value);
      const thenReads = value.inspectThenReads();
      check(thenReads === 0, 'default export then getter was not read');
      return {...observed, thenReads};
    });
    await run('class-default-construction', async () => {
      const Constructor = require('/probe/class.cjs');
      const namespace = await driver.load('file:///probe/class.cjs');
      const observed = namespaceObservation(namespace, Constructor);
      const instance = new namespace.default(7);
      const prototypeSame = Object.getPrototypeOf(instance) === Constructor.prototype;
      const result = instance.describe();
      check(prototypeSame && result === 'class:7', 'genuine class default can construct');
      return {...observed, prototypeSame, result};
    });
    for (const [id, name, predicate] of [
      ['undefined-default', 'undefined', value => value === undefined],
      ['nan-default', 'nan', value => Number.isNaN(value)],
      ['negative-zero-default', 'negative-zero', value => Object.is(value, -0)],
    ]) {
      await run(id, async () => {
        const path = '/probe/' + name + '.cjs';
        const value = require(path), namespace = await driver.load('file://' + path);
        const observed = namespaceObservation(namespace, value);
        const expectedPrimitive = predicate(namespace.default);
        check(expectedPrimitive, 'selected primitive default survives');
        return {...observed, expectedPrimitive};
      });
    }
    await run('throw-null-preserved', async () => {
      const path = '/probe/throw-null.cjs';
      const result = await rejection(() => driver.load('file://' + path));
      const rejectedNull = result.rejected && result.value === null;
      const noCompletedCacheEntry = !Object.hasOwn(require.cache, path);
      check(rejectedNull && noCompletedCacheEntry, 'original falsy throw and original CJS failed-load cleanup');
      return {rejectedNull, noCompletedCacheEntry, error: failureData(result.value)};
    });
    for (const [id, url] of [
      ['query-refusal', targetUrl + '?probe=1'],
      ['fragment-refusal', targetUrl + '#probe'],
      ['encoded-separator-refusal', 'file:///probe%2ftarget.cjs'],
      ['uppercase-scheme-refusal', 'FILE:///probe/target.cjs'],
      ['extension-refusal', 'file:///probe/target.js'],
      ['url-byte-limit-refusal', 'file:///probe/' + 'x'.repeat(12297) + '.cjs'],
      ['decoded-path-limit-refusal', 'file:///probe/' + 'x'.repeat(4096) + '.cjs'],
    ]) {
      await run(id, async () => refusalObservation(await rejection(() => driver.load(url)),
        'ERR_SM_MODULE_FILE_URL_UNSUPPORTED', 'module_file_url', url));
    }
  }
  const exactCaseIds = records.length === expectedIds.length &&
    records.every((record, index) => record.id === expectedIds[index]);
  return {
    schemaVersion: 1, suite: 'REAL_COMPONENT_CJS_FILE_URL_PROBE_V1', mode,
    caseCount: records.length, expectedCaseCount: expectedIds.length, records,
    exactCaseIds, profilePassed: exactCaseIds && records.every(record => record.passed === true),
    guardRefusalIsNodeCompatibilityPass: false,
    nodeReferenceExecuted: false, applicationImported: false,
    fullNextClaim: false, namespaceLimit8192Exercised: false,
    symlinkReentrancyRealmOrRaceParityProved: false,
  };
}

// Literal mode is selected by Source assembly, not a request parameter or environment.
const fileUrlProbeMode = 'interop';
async function prepareFileUrlProbe() {
  bootstrap();
  let calls = 0;
  return createWasiHttpHandler(async request => {
    const url = new URL(request.url);
    if (request.method !== 'GET' || url.pathname !== '/probe' || url.search !== '')
      return new Response('one predeclared GET /probe required', {status: 404});
    if (++calls !== 1) return new Response('probe already called', {status: 409});
    const result = await collectFileUrlProbe(fileUrlProbeMode);
    return new Response(JSON.stringify({...result, call: calls}), {
      status: 200, headers: {'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store'},
    });
  }, types, runFreshRequest);
}
export const incomingHandler = createNeutralReadyHandler({
  runNeutralServer, prepareServer: prepareFileUrlProbe, disposeBeforeEntry,
});
