// Independent Node22.14 public-fetch implementation. Never imported by guest Source.
// Dormant CLI: future Root must authenticate this family, Node, original owner,
// exact origin/output and before/final protection before authorizing execution.
import {mkdir, open, realpath} from 'node:fs/promises';
import {resolve, join, dirname} from 'node:path';
import {pathToFileURL} from 'node:url';

function referenceError(error) {
  const value = {type: typeof error, isNull: error === null, isTypeError: error instanceof TypeError};
  for (const key of ['name', 'message', 'code']) {
    try { value[key] = typeof error?.[key] === 'string' ? error[key].slice(0, 512) : null; }
    catch { value[key] = null; }
  }
  return value;
}
async function settled(operation) {
  try { return {fulfilled: true, valueUndefined: (await operation()) === undefined}; }
  catch (error) { return {fulfilled: false, error: referenceError(error)}; }
}
function metadata(response) {
  return {status: response.status, url: response.url,
    contentType: response.headers.get('content-type'), bodyUsed: response.bodyUsed};
}
function partData(part) {
  return {done: part.done, valueUndefined: part.value === undefined,
    hex: part.value === undefined ? null : Buffer.from(part.value).toString('hex')};
}
async function readToEnd(response, record, cleanup) {
  const reader = response.body.getReader(); let ended = false;
  record.hex = ''; record.receivedBytes = 0; record.parts = [];
  try {
    for (;;) {
      const next = await reader.read();
      if (next.done) { ended = true; record.eof = partData(next); break; }
      const keep = Math.max(4096 - record.receivedBytes, 0);
      record.hex += Buffer.from(next.value.subarray(0, keep)).toString('hex');
      record.receivedBytes += next.value.length; record.parts.push(next.value.length);
      if (record.receivedBytes > 4096) throw new RangeError('4096-byte public body cap; prefix retained');
    }
    record.closed = await settled(() => reader.closed);
  } finally {
    if (!ended) {
      const value = await settled(() => reader.cancel());
      if (!value.fulfilled) cleanup.push({operation: 'cancel-incomplete-read', ...value});
    }
    try { reader.releaseLock(); } catch (error) { cleanup.push({operation: 'releaseLock', error: referenceError(error)}); }
    record.complete = ended;
  }
}

function referenceOrigin(origin) {
  const url = new URL(origin);
  if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || !url.port || url.origin !== origin ||
      url.username || url.password || url.pathname !== '/' || url.search || url.hash)
    throw new TypeError('Root must supply one canonical explicit-port loopback origin');
  return origin;
}

export async function collectNodeReference(origin, saveRecord) {
  origin = referenceOrigin(origin);
  const ids = ['read-eof-metadata', 'bodyall-text', 'bodyall-json', 'bodyall-arraybuffer',
    'repeat-read-eof', 'clone-one-cancel-other-drain', 'direct-reader-cancel-pending', 'direct-reader-cancel-after-read'];
  const capture = {schemaVersion: 1, executor: 'node22-global-fetch', origin, caseIds: ids,
    records: [], allCasesAttempted: false, expectedJsonUrl: origin + '/api/json?q=lifecycle-v1'};
  const request = path => fetch(origin + path, {redirect: 'error', method: 'GET'});
  const perform = async (id, operation) => {
    const row = {id, observations: {}, error: null, cleanupErrors: [], captureLogError: null};
    capture.records.push(row);
    try { await operation(row.observations, row.cleanupErrors); }
    catch (error) { row.error = referenceError(error); }
    // Capture sink failures fail the Node owner; completed raw rows remain on disk.
    await saveRecord(row);
  };
  await perform(ids[0], async (row, cleanup) => {
    const response = await request('/api/json?q=lifecycle-v1'); row.before = metadata(response);
    await readToEnd(response, row, cleanup); row.after = metadata(response);
  });
  await perform(ids[1], async row => {
    const response = await request('/api/json?q=lifecycle-v1'); row.before = metadata(response);
    row.value = await response.text(); row.after = metadata(response);
    row.secondRead = await settled(() => response.text());
  });
  await perform(ids[2], async row => {
    const response = await request('/api/json?q=lifecycle-v1'); row.before = metadata(response);
    row.value = await response.json(); row.after = metadata(response);
    row.secondRead = await settled(() => response.text());
  });
  await perform(ids[3], async row => {
    const response = await request('/api/json?q=lifecycle-v1'); row.before = metadata(response);
    row.hex = Buffer.from(await response.arrayBuffer()).toString('hex'); row.after = metadata(response);
    row.secondRead = await settled(() => response.text());
  });
  await perform(ids[4], async (row, cleanup) => {
    row.responses = [];
    for (const ordinal of [1, 2, 3, 4]) {
      const item = {ordinal}; row.responses.push(item);
      const response = await request('/api/health'); item.before = metadata(response);
      await readToEnd(response, item, cleanup); item.after = metadata(response);
    }
  });
  await perform(ids[5], async (row, cleanup) => {
    const original = await request('/api/json?q=lifecycle-v1'), survivor = original.clone();
    row.before = metadata(original); row.cloneBefore = metadata(survivor);
    const canceledReader = original.body.getReader();
    const cancellation = settled(() => canceledReader.cancel('lifecycle-one-branch'));
    try {
      await readToEnd(survivor, row, cleanup);
      row.cancel = await cancellation; row.canceledClosed = await settled(() => canceledReader.closed);
      row.after = metadata(original); row.cloneAfter = metadata(survivor);
    } finally {
      try { canceledReader.releaseLock(); } catch (error) { cleanup.push({operation: 'clone-releaseLock', error: referenceError(error)}); }
    }
  });
  await perform(ids[6], async (row, cleanup) => {
    const response = await request('/api/json?q=lifecycle-v1'); row.before = metadata(response);
    const reader = response.body.getReader();
    try {
      const first = reader.read().then(part => ({fulfilled: true, part: partData(part)}),
        error => ({fulfilled: false, error: referenceError(error)}));
      const cancellation = settled(() => reader.cancel('lifecycle-direct-reader'));
      row.pendingRead = await first; row.cancel = await cancellation;
      row.readAfterCancel = partData(await reader.read()); row.closed = await settled(() => reader.closed);
      row.after = metadata(response);
    } finally {
      try { reader.releaseLock(); } catch (error) { cleanup.push({operation: 'cancel-releaseLock', error: referenceError(error)}); }
    }
  });
  await perform(ids[7], async (row, cleanup) => {
    const response = await request('/api/json?q=lifecycle-v1'); row.before = metadata(response);
    const reader = response.body.getReader();
    try {
      row.firstRead = partData(await reader.read());
      row.cancel = await settled(() => reader.cancel('lifecycle-direct-reader'));
      row.readAfterCancel = partData(await reader.read()); row.closed = await settled(() => reader.closed);
      row.after = metadata(response);
    } finally {
      try { reader.releaseLock(); } catch (error) { cleanup.push({operation: 'cancel-releaseLock', error: referenceError(error)}); }
    }
  });
  capture.allCasesAttempted = capture.records.length === 8;
  return capture;
}

async function main() {
  if (process.version !== 'v22.14.0' || process.execArgv.length !== 0 || process.env.NODE_OPTIONS !== undefined || process.argv.length !== 4)
    throw new Error('Pinned Node22.14, no flags/options, literal ORIGIN OUTPUT required');
  const origin = referenceOrigin(process.argv[2]), output = process.argv[3];
  if (resolve(output) !== output || await realpath(dirname(output)) !== dirname(output))
    throw new Error('Absolute fresh output under an existing canonical parent required');
  // No recursive creation, fallback, cleanup, listener or server of its own.
  await mkdir(output, {mode: 0o700});
  let ordinal = 0;
  const write = async (name, value) => {
    const fd = await open(join(output, name), 'wx', 0o600);
    try { await fd.writeFile(JSON.stringify(value, null, 2) + '\n'); await fd.sync(); }
    finally { await fd.close(); }
  };
  const capture = await collectNodeReference(origin, row => write(String(++ordinal).padStart(2, '0') + '-' + row.id + '.json', row));
  await write('observations.json', capture); // All raw cases before any semantic check.
  console.log(JSON.stringify({state: 'NODE_FETCH_LIFECYCLE_RAW_CAPTURED_UNREVIEWED_V1', cases: ordinal,
    allCasesAttempted: capture.allCasesAttempted, guestExecuted: false}));
  // Exit0 is capture completion only. The separate DATA validator remains mandatory.
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href)
  main().catch(error => { console.error(error); process.exitCode = 1; });
