// Pure WebAPI/injected-response checks. No HTTP, real output store, app or guest.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {collectPortableCache, validatePortableCache} from './collector.mjs';

let checks = 0;
const ok = value => { assert.equal(value, true); checks++; };
const equal = (a, b) => { assert.deepEqual(a, b); checks++; };
const A = '1'.repeat(64), B = 'a'.repeat(64);
const output = '/fake-owned/portable-cache';
const origin = 'http://127.0.0.1:45678';
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const json = value => Buffer.from(JSON.stringify(value));
const value = nonce => ({marker: 'NEXT_PORTABLE_CACHE_VALUE', nonce});
const ack = () => ({marker: 'NEXT_PORTABLE_CACHE_REVALIDATED', tag: 'portable-fetch-v1'});
const bodies = () => [value(A), value(A), ack(), value(B), value(B)];

function memoryStore() {
  const files = new Map(), writes = []; let initializations = 0;
  return {files, writes, get initializations() { return initializations; },
    async init() { assert.equal(initializations++, 0); },
    async write(name, bytes) { assert.equal(files.has(name), false); files.set(name, Buffer.from(bytes)); writes.push(name); }};
}
function response(bytes, {status = 200, chunks, readError, cancelError, releaseError, contentType = 'application/json; charset=utf-8'} = {}) {
  const pieces = chunks ?? [Buffer.from(bytes)]; let offset = 0, canceled = 0, released = 0;
  return {status, headers: new Headers(contentType === null ? {} : {'content-type': contentType}),
    get canceled() { return canceled; }, get released() { return released; },
    body: {getReader() { return {
      async read() {
        if (offset < pieces.length) return {done: false, value: new Uint8Array(pieces[offset++])};
        if (readError !== undefined) throw readError;
        return {done: true};
      },
      async cancel() { canceled++; if (cancelError !== undefined) throw cancelError; },
      releaseLock() { released++; if (releaseError !== undefined) throw releaseError; },
    }; }}};
}
async function run(responses) {
  const store = memoryStore(), calls = [];
  const capture = await collectPortableCache({origin, output, store, fetchImpl: async (url, options) => {
    calls.push({url, method: options.method, redirect: options.redirect, headers: options.headers, signal: options.signal});
    const next = responses[calls.length - 1];
    if (typeof next === 'function') return next();
    return next;
  }});
  return {capture, store, calls};
}
function mutateBody(capture, index, bytes) {
  const copy = structuredClone(capture), row = copy.records[index];
  row.bodyBase64 = bytes.toString('base64'); row.receivedBytes = bytes.length; row.retainedBytes = bytes.length;
  row.body.bytes = bytes.length; row.body.sha256 = hash(bytes);
  return copy;
}

const positive = await run(bodies().map(body => response(json(body))));
ok(validatePortableCache(positive.capture).passed);
equal(positive.calls.map(call => call.method), ['GET', 'GET', 'POST', 'GET', 'GET']);
ok(positive.calls.every(call => call.url === origin + '/api/portable-cache' && call.redirect === 'manual' &&
  call.headers.accept === 'application/json' && call.signal instanceof AbortSignal && !call.signal.aborted));
equal(positive.store.initializations, 1);
equal(positive.store.writes.length, 11);
equal(positive.store.writes.at(-1), 'observations.json');
equal(JSON.parse(positive.store.files.get('observations.json')), positive.capture);
ok(positive.capture.records.every(row => positive.store.files.get(row.id + '.body').toString('base64') === row.bodyBase64 &&
  JSON.stringify(JSON.parse(positive.store.files.get(row.id + '.json'))) === JSON.stringify(row)));
equal([positive.capture.fetchMode, positive.capture.storeMode], ['injected-test-fetch', 'injected-test-store']);
equal(validatePortableCache(positive.capture).actualNextExecutionVerified, false);
equal(validatePortableCache(positive.capture).originalContractAcceptanceUnchanged, true);

for (const malformed of [value('A'.repeat(64)), value(A + '\n'), value(0), {marker: 'wrong', nonce: A},
  {...value(A), extra: true}, {marker: 'NEXT_PORTABLE_CACHE_VALUE'}])
  equal(validatePortableCache(mutateBody(positive.capture, 0, json(malformed))).passed, false);
for (const malformed of [{...ack(), tag: 'other'}, {...ack(), extra: true}, {...ack(), marker: 'wrong'}])
  equal(validatePortableCache(mutateBody(positive.capture, 2, json(malformed))).passed, false);
for (const [index, nonce] of [[1, B], [3, A], [4, A]])
  equal(validatePortableCache(mutateBody(positive.capture, index, json(value(nonce)))).passed, false);
for (const status of [201, 500, true, '200']) {
  const copy = structuredClone(positive.capture); copy.records[0].status = status;
  equal(validatePortableCache(copy).passed, false);
}
for (const headers of [[], [['content-type', 'text/html']], [['content-type']], false]) {
  const copy = structuredClone(positive.capture); copy.records[0].headers = headers;
  equal(validatePortableCache(copy).passed, false);
}
for (const bytes of [Buffer.from('{"nonce":'), Buffer.from([0xff]), json(null), json([])])
  equal(validatePortableCache(mutateBody(positive.capture, 0, bytes)).passed, false);
for (const field of ['sha256', 'bytes']) {
  const copy = structuredClone(positive.capture); copy.records[0].body[field] = field === 'bytes' ? 999 : '0'.repeat(64);
  equal(validatePortableCache(copy).passed, false);
}
const noncanonical = structuredClone(positive.capture); noncanonical.records[0].bodyBase64 += '\n';
equal(validatePortableCache(noncanonical).passed, false);
const missing = structuredClone(positive.capture); missing.records.pop();
equal(validatePortableCache(missing).passed, false);
equal(validatePortableCache(null).passed, false);

const tooLarge = Buffer.alloc(65537, 0x78), overflowResponse = response(tooLarge);
const overflow = await run([overflowResponse, ...bodies().slice(1).map(body => response(json(body)))]);
equal(overflow.calls.length, 5); equal(overflow.store.files.size, 11);
equal(overflow.capture.records[0].receivedBytes, 65537);
equal(overflow.capture.records[0].retainedBytes, 65536);
equal(overflow.store.files.get('portable-first.body'), tooLarge.subarray(0, 65536));
ok(overflow.capture.records[0].overflow && !overflow.capture.records[0].complete);
equal(overflow.capture.records[0].transportError.name, 'RangeError');
equal([overflowResponse.canceled, overflowResponse.released], [1, 1]);
equal(validatePortableCache(overflow.capture).passed, false);

const readError = Object.assign(new Error('original reader failure'), {code: 'ERR_TEST_PARTIAL'});
const prefix = Buffer.from('{"marker":"NEXT_PORTABLE_');
const partialResponse = response(prefix, {readError});
const partial = await run([partialResponse, ...bodies().slice(1).map(body => response(json(body)))]);
equal(partial.calls.length, 5); equal(partial.store.files.size, 11);
equal(partial.store.files.get('portable-first.body'), prefix);
equal(partial.capture.records[0].bodyBase64, prefix.toString('base64'));
equal(partial.capture.records[0].complete, false);
equal(partial.capture.records[0].transportError.code, 'ERR_TEST_PARTIAL');
equal(partial.capture.records[0].transportError.message, 'original reader failure');
equal([partialResponse.canceled, partialResponse.released], [1, 1]);
equal(validatePortableCache(partial.capture).passed, false);

const cleanupResponse = response(prefix, {readError: 0, cancelError: null, releaseError: false});
const cleanup = await run([cleanupResponse, ...bodies().slice(1).map(body => response(json(body)))]);
equal(cleanup.capture.records[0].transportError.value, 0);
equal(cleanup.capture.records[0].cleanupErrors.map(row => [row.operation, row.error.type, row.error.isNull]),
  [['cancel', 'object', true], ['releaseLock', 'boolean', false]]);
equal(cleanup.calls.length, 5); equal(validatePortableCache(cleanup.capture).passed, false);
const timeout = await run([() => { throw new DOMException('constructed timeout DATA', 'TimeoutError'); },
  ...bodies().slice(1).map(body => response(json(body)))]);
equal(timeout.capture.records[0].transportError.code, 23);
equal(timeout.capture.records[0].retainedBytes, 0);
equal(timeout.calls.length, 5); equal(timeout.store.files.size, 11);
equal(validatePortableCache(timeout.capture).passed, false);

for (const badOrigin of ['http://localhost:45678', 'https://127.0.0.1:45678', origin + '/', origin + '/api/portable-cache',
  'http://user@127.0.0.1:45678', 'http://127.0.0.1:0']) {
  let touched = false;
  await assert.rejects(collectPortableCache({origin: badOrigin, output, fetchImpl() { touched = true; },
    store: {init() { touched = true; }}})); checks++; equal(touched, false);
}
for (const badOutput of ['relative', '/fake-owned/../cache', '/fake-owned//cache']) {
  let touched = false;
  await assert.rejects(collectPortableCache({origin, output: badOutput, fetchImpl() { touched = true; },
    store: {init() { touched = true; }}})); checks++; equal(touched, false);
}
const storageError = new Error('storage failed'), brokenStore = memoryStore();
brokenStore.write = async () => { throw storageError; };
await assert.rejects(collectPortableCache({origin, output, store: brokenStore,
  fetchImpl: async () => response(json(value(A)))}), error => error === storageError); checks++;
equal(storageError.portableCacheCapture.records.length, 1);
equal(storageError.portableCacheCapture.records[0].bodyBase64, json(value(A)).toString('base64'));
for (const error of [Object.freeze(new Error('frozen primary')),
  Object.defineProperty(new Error('preexisting primary'), 'portableCacheCapture', {value: 'preexisting'})]) {
  const store = memoryStore(); store.write = async () => { throw error; };
  await assert.rejects(collectPortableCache({origin, output, store,
    fetchImpl: async () => response(json(value(A)))}), observed => observed === error); checks++;
  equal(error.portableCacheCapture, error.message === 'frozen primary' ? undefined : 'preexisting');
}

console.log(JSON.stringify({schemaVersion: 1, passed: true, checks,
  scope: 'Pure injected WebAPI/response/store DATA; no HTTP, app, cache filesystem or guest.',
  realHttpExecuted: false, realOutputStoreUsed: false, actualNextExecutionVerified: false}));
