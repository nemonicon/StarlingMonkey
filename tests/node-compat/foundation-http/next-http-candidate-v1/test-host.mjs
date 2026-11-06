// Test-only Node stream/Buffer and Node ALS providers, never native evidence.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInThisContext} from 'node:vm';
import {Readable, Writable} from 'node:stream';
import {EventEmitter} from 'node:events';
import {AsyncLocalStorage} from 'node:async_hooks';
import {validateManifest} from '../../../../builtins/node-compat/validate-manifest.mjs';
assert.equal(process.version, 'v22.14.0');
const read = n => readFileSync(new URL(n, import.meta.url), 'utf8');
const header = read('next-http-factory.generated.h');
const source = header.split('R"SM_HTTP(')[1].split(')SM_HTTP"')[0];
const factory = runInThisContext(source);
const als = new AsyncLocalStorage();
let deployed = true, checks = 0, neutralEntries = 0, freshEntries = 0;
const check = (value, message) => { assert(value, message); checks++; };
const checkDeployed = () => { if (!deployed) { const e = new Error('INIT'); e.code = 'ERR_SM_NODE_HTTP_INITIALIZATION'; throw e; } };
const a = {Readable, Writable, EventEmitter, Buffer, checkDeployed,
  runNeutralServer(fn, receiver, ...args) { neutralEntries++; return als.exit(() => Reflect.apply(fn, receiver, args)); },
  runFreshRequest(fn, receiver, ...args) { freshEntries++; return als.exit(() => Reflect.apply(fn, receiver, args)); }};
assert.throws(() => factory({...a, runFreshRequest: undefined}), TypeError); checks++;
const graph = factory(a), inventory = JSON.parse(read('inventory.node-v22.14.0.json'));
const schema = JSON.parse(readFileSync(new URL('../../../../builtins/node-compat/manifest.schema.json', import.meta.url), 'utf8'));
validateManifest(JSON.parse(read('export-manifest.http.node-v22.14.0.json')), schema); checks++;
for (const id of ['http', 'https']) {
  const record = graph[id];
  assert.deepEqual(Object.keys(record).sort(), inventory.modules['node:' + id].exports); checks++;
  check(record.Agent === record.default.Agent && record.globalAgent === record.default.globalAgent, 'named/default identities');
  for (const name of ['createServer','request','get','Server']) {
    for (const mode of ['call','new']) {
      assert.throws(() => mode === 'call' ? record[name]() : new record[name](),
        {code: 'ERR_SM_NODE_UNSUPPORTED', module: 'node:' + id, operation: name}); checks++;
    }
  }
  check(record.then === undefined && record.default.then === undefined, 'not thenable');
  check(Object.entries(record).length === Object.keys(record).length && typeof JSON.stringify(record) === 'string', 'safe namespace inspection');
}
for (const options of [{}, {host: 'example.test', port: 80}, {host: 'x', port: 90, localAddress: 'y', family: 6}, {socketPath: '/guest.sock'}]) {
  const node = await import('node:http');
  assert.equal(new graph.http.Agent().getName(options), new node.Agent().getName(options)); checks++;
}
check(graph.https.globalAgent.protocol === 'https:' && graph.https.globalAgent.defaultPort === 443, 'https configuration');
assert.throws(() => graph.https.globalAgent.createConnection(), {code: 'ERR_SM_NODE_UNSUPPORTED'}); checks++;
for (const [name, value, code] of [['x', undefined, 'ERR_HTTP_INVALID_HEADER_VALUE'], ['x','bad\nvalue','ERR_INVALID_CHAR']]) {
  assert.throws(() => graph.http.validateHeaderValue(name, value), {code}); checks++;
}
deployed = false;
assert.throws(() => graph.hosting.createServerHandler(() => () => {}), {code: 'ERR_SM_NODE_HTTP_INITIALIZATION'}); checks++;
assert.throws(() => new graph.http.IncomingMessage(new Request('http://example.test/')), {code: 'ERR_SM_NODE_HTTP_INITIALIZATION'}); checks++;
deployed = true;
assert.throws(() => new graph.http.IncomingMessage({}), {code: 'ERR_SM_NODE_UNSUPPORTED'}); checks++;
let prepareCount = 0, prepareStore;
const handle = als.run('MUST_NOT_LEAK', () => graph.hosting.createServerHandler(async () => {
  prepareCount++; prepareStore = als.getStore(); await Promise.resolve();
  return async (req, res) => {
    check(req instanceof graph.http.IncomingMessage && res instanceof graph.http.ServerResponse, 'actual message identity');
    check(als.getStore() === undefined, 'neutral app entry');
    res.setHeader('x-path', req.url); res.end('HTTP_PROFILE');
  };
}));
const responses = await Promise.all(Array.from({length: 8}, (_, i) =>
  a.runFreshRequest(() => handle(new Request('http://example.test/' + i)), undefined)));
for (let i = 0; i < responses.length; i++) {
  check(responses[i].headers.get('x-path') === '/' + i && await responses[i].text() === 'HTTP_PROFILE', 'body and path');
}
check(prepareCount === 1 && prepareStore === undefined && neutralEntries === 1 && freshEntries === 8, 'one neutral readiness, fresh entry per request');
console.log(JSON.stringify({passed: true, checks, sourceFactoryExecuted: true, nativeContextExecuted: false, guestExecuted: false}));
