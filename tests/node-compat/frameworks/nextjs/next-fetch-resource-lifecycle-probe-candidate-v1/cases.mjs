// Dormant guest collector. Every fetch is the guest's installed global fetch.
// No transport, task, resource-count, timing or private Store inference is made.
export const lifecycleCaseIds = Object.freeze([
  'read-eof-metadata', 'bodyall-text', 'bodyall-json', 'bodyall-arraybuffer',
  'repeat-read-eof', 'clone-one-cancel-other-drain',
  'direct-reader-cancel-pending', 'direct-reader-cancel-after-read',
]);
const lifecycleBodyCap = 4096;

export function lifecycleOrigin(value) {
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

export async function collectFetchLifecycle(origin) {
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
