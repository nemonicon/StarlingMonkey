import assert from 'node:assert/strict';
import {setTimeout as delay} from 'node:timers/promises';
import {createRequestBridge} from './bridge.mjs';
assert.equal(process.version, 'v22.14.0');
let checks = 0;
function check(value, message) { assert(value, message); checks++; }

const post = createRequestBridge(async (req, res) => {
  const parts = [];
  for await (const part of req) parts.push(part);
  check(req.complete && !req.aborted, 'input reaches clean EOF');
  check(req.url === '/path?a=b' && req.headers.host === 'example.test', 'URL and host');
  check(req.headers.hasOwnProperty('host'), 'Node request headers retain Object prototype');
  res.setHeader('set-cookie', ['one=1', 'two=2']);
  res.writeHead(201, {'x-marker': 'BRIDGE'});
  assert.throws(() => res.setHeader('late', 'x'), {code: 'ERR_HTTP_HEADERS_SENT'}); checks++;
  res.end(Buffer.concat(parts));
});
const response = await post(new Request('http://example.test/path?a=b', {method: 'POST', body: 'body✓'}));
check(response.status === 201 && response.headers.get('x-marker') === 'BRIDGE', 'status and headers');
assert.deepEqual(response.headers.getSetCookie(), ['one=1', 'two=2']); checks++;
check(await response.text() === 'body✓', 'body');

let implicitHook = false;
const hooked = await createRequestBridge((_req, res) => {
  const writeHead = res.writeHead;
  res.writeHead = function(...args) { implicitHook = true; this.setHeader('x-hook', 'ran'); return writeHead.apply(this, args); };
  res._implicitHeader();
  check(typeof res._header === 'string' && res._headerSent === true, 'private header hooks have actual header state');
  res.end('hooked');
})(new Request('http://example.test/'));
check(implicitHook && hooked.headers.get('x-hook') === 'ran' && await hooked.text() === 'hooked', 'implicit writeHead interposition');

for (const [method, status] of [['HEAD', 200], ['GET', 304], ['GET', 204]]) {
  const result = await createRequestBridge((_req, res) => { res.statusCode = status; res.end('discard'); })(new Request('http://example.test/', {method}));
  check(await result.text() === '', method + status + ' has no body');
}

let callbackObserved = false, finished = false, closed = 0;
const bytes = Buffer.alloc(128 * 1024, 7);
const streaming = await createRequestBridge((_req, res) => {
  res.on('finish', () => { finished = true; });
  res.on('close', () => { closed++; });
  const accepted = res.write(bytes, () => { callbackObserved = true; bytes.fill(9); });
  check(accepted === false, 'write reports backpressure');
  res.end();
})(new Request('http://example.test/'));
await delay(5);
check(!callbackObserved, 'callback held until consumer makes room');
const body = new Uint8Array(await streaming.arrayBuffer());
check(body.length === 128 * 1024 && body.every(byte => byte === 7), 'owned output bytes');
await delay(0);
check(callbackObserved && finished && closed === 1, 'write/final/close lifetimes');

const abort = new AbortController();
const cancelled = createRequestBridge(async (req, res) => {
  for await (const _part of req) {}
  res.end('unreachable');
})(new Request('http://example.test/', {method: 'POST', body: new ReadableStream({}), duplex: 'half', signal: abort.signal}));
abort.abort();
await assert.rejects(cancelled, {code: 'ECONNRESET'}); checks++;
for (const value of [null, false, 0, undefined]) {
  await assert.rejects(createRequestBridge(() => { throw value; })(new Request('http://example.test/')), {code: 'ERR_SM_HTTP_HANDLER'}); checks++;
}
console.log(JSON.stringify({schemaVersion: 1, state: 'NODE_HOST_HTTP_BRIDGE_CHECKS_PASSED', checks,
  guestExecution: false, nextFrameworkExecuted: false, sourceOnlyCandidate: true}));
