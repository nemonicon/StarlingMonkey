// Host client only. Importing this file performs no HTTP or filesystem writes.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, realpath, writeFile} from 'node:fs/promises';
import {dirname, isAbsolute, join, resolve} from 'node:path';

const LIMIT = 65536, SECONDS = 20, PATH = '/api/portable-cache';
const CASES = Object.freeze([
  ['portable-first', 'GET'], ['portable-repeat', 'GET'], ['portable-revalidate', 'POST'],
  ['portable-after', 'GET'], ['portable-after-repeat', 'GET'],
].map(row => Object.freeze(row)));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
function originValue(input) {
  const url = new URL(input);
  assert.equal(input, url.origin);
  assert.equal(url.protocol, 'http:'); assert.equal(url.hostname, '127.0.0.1');
  assert(url.port && Number(url.port) >= 1 && Number(url.port) <= 65535);
  return url.origin;
}
function diagnostic(error) {
  const type = typeof error, result = {type, isNull: error === null};
  if (error === null || ['boolean', 'string'].includes(type)) result.value = error;
  if (type === 'number') result.value = Number.isFinite(error) ? error : String(error);
  for (const name of ['name', 'message', 'code', 'stack']) {
    try {
      const value = error?.[name];
      result[name] = value === undefined ? null : value === null || ['boolean', 'string'].includes(typeof value) ? value :
        typeof value === 'number' && Number.isFinite(value) ? value : {type: typeof value};
    } catch (secondary) { result[name] = {propertyReadFailed: true, thrownType: typeof secondary}; }
  }
  return result;
}
function window20() {
  const controller = new AbortController(); let reject;
  const deadline = new Promise((_, no) => { reject = no; });
  const timer = setTimeout(() => {
    const error = new DOMException('Portable cache request exceeded20s', 'TimeoutError');
    controller.abort(error); reject(error);
  }, SECONDS * 1000);
  return {signal: controller.signal, wait: promise => Promise.race([Promise.resolve(promise), deadline]),
    close: () => clearTimeout(timer)};
}
function fileStore(output) {
  return {
    async init() {
      assert.equal(await realpath(dirname(output)), dirname(output));
      await mkdir(output, {mode: 0o700}); // Fresh exclusive namespace; existing paths refuse.
      assert.equal(await realpath(output), output);
    },
    async write(name, bytes) { await writeFile(join(output, name), bytes, {flag: 'wx', mode: 0o600}); },
  };
}

export async function collectPortableCache({origin, output, fetchImpl, store} = {}) {
  origin = originValue(origin);
  assert(typeof output === 'string' && isAbsolute(output) && resolve(output) === output);
  const capture = {schemaVersion: 1, marker: 'NEXT_PORTABLE_CACHE_HTTP_CAPTURE_V1', origin,
    path: PATH, requestSeconds: SECONDS, deliveredBodyCap: LIMIT,
    bodyByteMeaning: 'Fetch-delivered bytes; no compressed-wire or socket-EOF claim.',
    fetchMode: fetchImpl === undefined ? 'default-host-fetch' : 'injected-test-fetch',
    storeMode: store === undefined ? 'host-file-store' : 'injected-test-store', records: [],
    actualNextExecutionRequiresParentProof: true};
  const fetcher = fetchImpl ?? globalThis.fetch, sink = store ?? fileStore(output);
  assert.equal(typeof fetcher, 'function');
  await sink.init();
  try {
    for (const [id, method] of CASES) {
      const record = {id, method, url: origin + PATH, status: null, headers: null,
        complete: false, overflow: false, receivedBytes: 0, retainedBytes: 0,
        body: null, bodyBase64: '', transportError: null, cleanupErrors: []};
      const chunks = [], request = window20(); let reader;
      try {
        const response = await request.wait(fetcher(record.url, {method, redirect: 'manual',
          headers: {accept: 'application/json'}, signal: request.signal}));
        record.status = response.status; record.headers = [...response.headers.entries()];
        if (response.body === null) record.complete = true;
        else {
          reader = response.body.getReader();
          for (;;) {
            const part = await request.wait(reader.read());
            if (part.done) { record.complete = true; break; }
            assert(part.value instanceof Uint8Array, 'Fetch body must deliver Uint8Array');
            record.receivedBytes += part.value.byteLength;
            const keep = Math.min(part.value.byteLength, LIMIT - record.retainedBytes);
            if (keep > 0) { chunks.push(Buffer.from(part.value.subarray(0, keep))); record.retainedBytes += keep; }
            if (record.receivedBytes > LIMIT) {
              record.overflow = true;
              throw new RangeError('Portable cache delivered-body cap exceeded; prefix retained');
            }
          }
        }
      } catch (error) { record.transportError = diagnostic(error); }
      finally {
        if (reader) {
          if (!record.complete) try { await request.wait(reader.cancel()); }
          catch (error) { record.cleanupErrors.push({operation: 'cancel', error: diagnostic(error)}); }
          try { reader.releaseLock(); }
          catch (error) { record.cleanupErrors.push({operation: 'releaseLock', error: diagnostic(error)}); }
        }
        request.close();
      }
      const bytes = Buffer.concat(chunks), name = id + '.body';
      record.bodyBase64 = bytes.toString('base64');
      record.body = {path: join(output, name), sha256: hash(bytes), bytes: bytes.length};
      capture.records.push(record);
      await sink.write(name, bytes);
      await sink.write(id + '.json', Buffer.from(JSON.stringify(record, null, 2) + '\n'));
    }
    // All five raw results, including errors/prefixes, precede nonce semantics.
    await sink.write('observations.json', Buffer.from(JSON.stringify(capture, null, 2) + '\n'));
    return capture;
  } catch (error) {
    // Storage/setup failures are not HTTP semantics. Preserve collected data
    // for the caller's failure record; never admit an incomplete capture.
    if (error !== null && (typeof error === 'object' || typeof error === 'function'))
      try { Object.defineProperty(error, 'portableCacheCapture', {value: capture}); }
      catch { /* Diagnostic attachment is best effort; preserve the original error. */ }
    throw error;
  }
}

export function validatePortableCache(capture) {
  const failures = []; let checks = 0;
  const check = (ok, message) => { checks++; if (ok !== true) failures.push(message); };
  check(capture?.schemaVersion === 1 && capture?.marker === 'NEXT_PORTABLE_CACHE_HTTP_CAPTURE_V1', 'capture schema');
  try { check(originValue(capture.origin) === capture.origin, 'loopback origin'); }
  catch { check(false, 'loopback origin'); }
  check(capture?.path === PATH && capture?.requestSeconds === SECONDS && capture?.deliveredBodyCap === LIMIT, 'fixed protocol');
  const records = Array.isArray(capture?.records) ? capture.records : [];
  check(records.length === CASES.length, 'exact five outcomes');
  const nonces = [];
  for (let i = 0; i < CASES.length; i++) {
    const row = records[i], [id, method] = CASES[i];
    if (!row || typeof row !== 'object') { check(false, id + ' missing'); continue; }
    check(row.id === id && row.method === method && row.url === capture.origin + PATH, id + ' identity');
    check(row.status === 200 && Number.isInteger(row.status), id + ' status');
    check(row.complete === true && row.overflow === false && row.transportError === null &&
      Array.isArray(row.cleanupErrors) && row.cleanupErrors.length === 0, id + ' transport/cleanup');
    check(Number.isSafeInteger(row.receivedBytes) && row.receivedBytes >= 0 && row.receivedBytes <= LIMIT &&
      row.retainedBytes === row.receivedBytes, id + ' complete byte counts');
    const headers = row.headers;
    const validHeaders = Array.isArray(headers) && headers.every(pair => Array.isArray(pair) && pair.length === 2 && pair.every(x => typeof x === 'string'));
    check(validHeaders === true, id + ' fetch-exposed headers');
    check(validHeaders && headers.find(([key]) => key.toLowerCase() === 'content-type')?.[1].split(';', 1)[0].trim().toLowerCase() === 'application/json', id + ' JSON media type');
    let value;
    try {
      assert.equal(typeof row.bodyBase64, 'string');
      const bytes = Buffer.from(row.bodyBase64, 'base64');
      check(bytes.toString('base64') === row.bodyBase64 && bytes.length === row.retainedBytes && bytes.length <= LIMIT &&
        row.body?.bytes === bytes.length && row.body?.sha256 === hash(bytes), id + ' raw body integrity');
      value = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(bytes));
      check(value !== null && typeof value === 'object' && !Array.isArray(value), id + ' JSON object');
      if (method === 'POST') {
        check(JSON.stringify(Object.keys(value).sort()) === JSON.stringify(['marker', 'tag']) &&
          value.marker === 'NEXT_PORTABLE_CACHE_REVALIDATED' && value.tag === 'portable-fetch-v1', id + ' acknowledgement');
      } else {
        const valid = JSON.stringify(Object.keys(value).sort()) === JSON.stringify(['marker', 'nonce']) &&
          value.marker === 'NEXT_PORTABLE_CACHE_VALUE' && typeof value.nonce === 'string' && value.nonce.length === 64 && /^[0-9a-f]{64}$/.test(value.nonce);
        check(valid, id + ' exact marker/nonce'); nonces[i] = valid ? value.nonce : null;
      }
    } catch { check(false, id + ' complete UTF8/JSON body'); }
  }
  check(typeof nonces[0] === 'string' && nonces[0] === nonces[1], 'first equals repeat');
  check(typeof nonces[3] === 'string' && nonces[3] !== nonces[0], 'after differs from first');
  check(typeof nonces[3] === 'string' && nonces[3] === nonces[4], 'after equals after-repeat');
  return {schemaVersion: 1, passed: failures.length === 0, checks, failures, cases: records.length,
    subsetOnly: true, originalContractAcceptanceUnchanged: true, actualNextExecutionVerified: false};
}
