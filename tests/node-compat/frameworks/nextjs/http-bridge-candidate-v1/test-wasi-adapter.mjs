// Host ownership/translation tests. These do not execute a WASI component.
import assert from 'node:assert/strict';
import {createWasiHttpHandler} from './wasi-adapter.mjs';

const encode = value => new TextEncoder().encode(value);
const decode = value => new TextDecoder().decode(value);
let checks = 0;

function resources(options = {}) {
  const live = new Set(), events = [], written = [];
  let serial = 0, receivedFields, receivedStatus, responseCalls = 0;
  class Resource {
    constructor(kind, parent) {
      this.id = kind + ':' + ++serial;
      this.parent = parent;
      live.add(this);
      events.push('new ' + this.id);
    }
    use() { assert(live.has(this), 'using consumed resource ' + this.id); }
    take() {
      this.use();
      assert(![...live].some(value => value.parent === this), 'child outlives drop: ' + this.id);
      live.delete(this);
      events.push('consume ' + this.id);
    }
    [Symbol.dispose]() { this.take(); }
  }
  const ioFailure = () => {
    const error = new Resource('io-error');
    error.toDebugString = () => { error.use(); return 'fixture io failure'; };
    return {tag: 'last-operation-failed', val: error};
  };
  class Fields extends Resource {
    constructor(entries, parent) { super('fields', parent); this.values = entries; }
    entries() { this.use(); return this.values; }
    static fromList(entries) { return new Fields(entries); }
  }
  const incoming = new Resource('incoming-request');
  const outparam = new Resource('response-outparam');
  incoming.headers = () => { incoming.use(); return new Fields([
    ['host', encode('fixture.test')], ['x-byte', Uint8Array.of(0xe9)],
  ], incoming); };
  incoming.scheme = () => { incoming.use(); return {tag: 'https'}; };
  incoming.authority = () => { incoming.use(); return 'fixture.test'; };
  incoming.method = () => { incoming.use(); return {tag: options.method ?? 'get'}; };
  incoming.pathWithQuery = () => { incoming.use(); return '/route?q=1'; };
  incoming.consume = () => {
    incoming.use();
    const body = new Resource('incoming-body', incoming);
    body.stream = () => {
      body.use();
      const stream = new Resource('input-stream', body);
      const chunks = (options.input ?? ['a', 'bc']).map(encode);
      stream.blockingRead = count => {
        stream.use(); assert.equal(count, 65536n);
        if (options.inputError) throw ioFailure();
        if (!chunks.length) throw {tag: 'closed'};
        return chunks.shift();
      };
      return stream;
    };
    return body;
  };
  class OutgoingResponse extends Resource {
    constructor(fields) {
      super('outgoing-response');
      receivedFields = fields.values;
      fields.take();
    }
    setStatusCode(status) {
      this.use(); receivedStatus = status;
      if (options.statusError) throw new Error('status refused');
    }
    body() {
      this.use();
      if (options.bodyError) throw new Error('body refused');
      // The WIT response body is independently owned; set(outparam,response)
      // transfers the parent response before streaming the owned body.
      const body = new Resource('outgoing-body');
      body.write = () => {
        body.use();
        const stream = new Resource('output-stream', body);
        stream.blockingWriteAndFlush = bytes => {
          stream.use(); assert(bytes.length <= 4096);
          if (options.outputError) throw ioFailure();
          written.push(new Uint8Array(bytes));
        };
        return stream;
      };
      return body;
    }
  }
  const types = {
    Fields, OutgoingResponse,
    IncomingBody: {finish(body) { body.take(); return new Resource('future-trailers'); }},
    OutgoingBody: {finish(body, trailers) {
      assert.equal(trailers, undefined); body.take();
      if (options.finishError) throw new Error('finish refused');
    }},
    ResponseOutparam: {set(param, result) {
      ++responseCalls;
      assert.equal(result.tag, 'ok');
      param.take(); result.val.take();
      if (options.setError) throw new Error('set refused after ownership transfer');
    }},
  };
  return {incoming, outparam, types, live, events, written,
    fields: () => receivedFields, status: () => receivedStatus, calls: () => responseCalls};
}

async function run(name, options, handler, expectedError) {
  const state = resources(options);
  let called = false;
  const wrapped = async request => { called = true; return handler(request); };
  try {
    const promise = createWasiHttpHandler(wrapped, state.types).handle(state.incoming, state.outparam);
    if (expectedError) await assert.rejects(promise, expectedError);
    else await promise;
    assert.equal(state.live.size, 0, name + ': leaked ' + [...state.live].map(value => value.id));
    assert(called);
    ++checks;
    return state;
  } catch (error) {
    error.message = name + ': ' + error.message;
    throw error;
  }
}

const normal = await run('GET and duplicate response cookies', {}, request => {
  assert.equal(request.url, 'https://fixture.test/route?q=1');
  assert.equal(request.method, 'GET');
  assert.equal(request.headers.get('x-byte'), '\u00e9');
  const headers = new Headers([['content-type', 'text/plain'], ['set-cookie', 'a=1'], ['set-cookie', 'b=2']]);
  return new Response('reply', {status: 201, headers});
});
assert.equal(normal.status(), 201);
assert.equal(normal.calls(), 1);
assert.deepEqual(normal.fields().filter(([name]) => name === 'set-cookie').map(([, value]) => decode(value)), ['a=1', 'b=2']);
assert.equal(normal.written.map(decode).join(''), 'reply');

await run('POST body EOF and incoming trailers ownership', {method: 'post'}, async request => {
  assert.equal(await request.text(), 'abc');
  return new Response('accepted');
});
await run('unread POST body cancellation', {method: 'post'}, () => new Response('ignored'));
await run('empty response body', {}, () => new Response(null, {status: 204}));

const large = await run('large response chunk splits at standard write limit', {}, () => new Response(encode('x'.repeat(9000))));
assert.deepEqual(large.written.map(value => value.length), [4096, 4096, 808]);

await run('application throws before outparam', {}, () => { throw new Error('application failed'); }, /application failed/);
await run('status validation throws with owned response', {statusError: true}, () => new Response('reply'), /status refused/);
await run('body acquisition throws with owned response', {bodyError: true}, () => new Response('reply'), /body refused/);
await run('set consumes both owned arguments even when it throws', {setError: true}, () => new Response('reply'), /set refused/);
await run('finish consumes owned body even when it throws', {finishError: true}, () => new Response('reply'), /finish refused/);
await run('outgoing stream error owns diagnostic resource', {outputError: true}, () => new Response('reply'), /fixture io failure/);
await run('incoming stream error owns diagnostic resource', {method: 'post', inputError: true}, async request => {
  await request.text();
  return new Response('unreachable');
}, /fixture io failure/);

let cancelled = false;
await run('output error cancels Web response reader', {outputError: true}, () => new Response(new ReadableStream({
  start(controller) { controller.enqueue(encode('first')); },
  cancel() { cancelled = true; },
})), /fixture io failure/);
assert(cancelled);

console.log(JSON.stringify({suite: 'WASI_HTTP_ADAPTER_HOST_OWNERSHIP_V1', checks, passed: true,
  wasiComponentExecuted: false, nativeGuestExecuted: false}));
