// Actual full Next custom-server control through the candidate message bridge.
// This is host Node evidence, never a claim of guest execution.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {Readable} from 'node:stream';
import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import {cp, mkdir, readFile, writeFile, rm} from 'node:fs/promises';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHostProfile} from './module-host-provider.mjs';
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.argv[2]);
const source = resolve(process.argv[3]);
const browserTools = process.argv[4];
assert.equal(process.version, 'v22.14.0');
assert.equal(process.argv.length,5,'Fresh output, actual standalone source and browser tools are required');
assert(browserTools,'Both browser checks are mandatory');
assert(root.startsWith('/private/tmp/starling-node-compat/next-native-profile-host-'));
assert(source.endsWith('/application/.next/standalone'));
await mkdir(root, {mode: 0o700});
await mkdir(join(root, 'responses'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const errorData = error => {
  const record={valueType:typeof error,isNull:error===null};
  if(error===null||!['object','function'].includes(typeof error)){record.primitive=error===undefined?'undefined':String(error);return record;}
  for(const key of ['name','message','stack','code','module','operation'])try{const value=error[key];if(typeof value==='string'||typeof value==='number'||typeof value==='boolean')record[key]=value;}catch{record[key+'ReadFailed']=true;}
  return record;
};
const descriptor = async path => { const b = await readFile(path); return {path, sha256: hash(b), bytes: b.length}; };
const result = {schemaVersion: 1, suite: 'FULL_NEXT_SELECTED_HTTP_CLASSIC_TOWEB_IMPORTS_PRIVATE_VM_HOST_V2',
  node: process.version, guestExecuted: false, applicationModified: false,
  standaloneSource: source, sourceServer: await descriptor(join(source, 'server.js')),
  httpFactory: await descriptor(join(here, '../../../foundation-http/next-http-candidate-v1/next-http-factory.generated.h')), harness: await descriptor(fileURLToPath(import.meta.url)),
  hostOnlyQualifications: {nativeGuestExecuted:false,nativeALSExecuted:false,FS:'stock Node (including stream IO)',crypto:'stock Node',zlib:'stock Node',processOsUrlGlobals:'stock Node',HTTPTransport:'stock Node localhost + Web Request/Response',ByteKernel:'R TEST-ONLY Node byte adapter',abortResistKey:'TEST-only symbol; not native protected AbortTarget proof'},
  toWebSource: await descriptor(join(here, '../../../foundation-classic-streams/readable-toweb-candidate-v1/readable-toweb.mjs')),
  selectedFacades:['http','https','events','stream','stream/promises','string_decoder','buffer','tty','inspector','v8','dns/promises'],
  http: [], errors: [], transportErrors: [], prepared: false};
const save = () => { if (result.moduleObservations?.snapshot) result.moduleSnapshot = result.moduleObservations.snapshot(); return writeFile(join(root, 'result.json'), JSON.stringify(result, null, 2) + '\n'); };
await save();
let server, app;
try {
  const application = join(root, 'application');
  await cp(source, application, {recursive: true, force: false, errorOnExist: true, verbatimSymlinks: true});
  assert.equal((await descriptor(join(application, 'server.js'))).sha256, result.sourceServer.sha256);
  // A fresh logical server starts with an empty cache. Only its owned copy is reset.
  await rm(join(application, '.next/cache'), {recursive: true, force: true});
  result.freshOwnedCacheReset = true;
  const moduleObservations = {};
  const profile = createHostProfile(join(application, 'server.js'), moduleObservations);
  const require = profile.require;
  result.moduleSource = await descriptor(join(here, '../../../foundation-module/node-module-candidate-v1/module-core.mjs'));
  result.hostModuleProvider = await descriptor(join(here, 'module-host-provider.mjs'));
  result.moduleObservations = moduleObservations;
  const installed = Object.fromEntries(['next', 'react', 'react-dom'].map(name => [name, require(name + '/package.json').version]));
  assert.deepEqual(installed, {next: '16.4.5', react: '19.3.1', 'react-dom': '19.3.1'});
  result.installed = installed;
  const config = JSON.parse(await readFile(join(application, '.next/required-server-files.json'))).config;
  process.env.NODE_ENV = 'production';
  process.env.NEXT_TELEMETRY_DISABLED = '1';
  process.env.__NEXT_PRIVATE_STANDALONE_CONFIG = JSON.stringify(config);
  process.chdir(application);
  let handler;
  server = createServer((request, response) => profile.hosting.runFreshRequest(async () => {
    if (!handler) { response.writeHead(503); response.end('Preparing'); return; }
    profile.noteConversion();
    const abort = new AbortController();
    request.once('aborted', () => abort.abort());
    response.once('close', () => { if (!response.writableFinished) abort.abort(); });
    try {
      const headers = new Headers();
      for (let i = 0; i < request.rawHeaders.length; i += 2) headers.append(request.rawHeaders[i], request.rawHeaders[i + 1]);
      const body = ['GET', 'HEAD'].includes(request.method) ? undefined : Readable.toWeb(request);
      const web = new Request(result.origin + request.url, {method: request.method, headers, body,
        ...(body ? {duplex: 'half'} : {}), signal: abort.signal});
      const returned = await handler(web);
      for (const [name, value] of returned.headers) if (name !== 'set-cookie') response.setHeader(name, value);
      const cookies = returned.headers.getSetCookie();
      if (cookies.length) response.setHeader('set-cookie', cookies);
      response.writeHead(returned.status, returned.statusText);
      if (returned.body) for await (const chunk of returned.body) if (!response.write(chunk)) await once(response, 'drain');
      response.end();
    } catch (error) {
      result.transportErrors.push({url: request.url, ...errorData(error)});
      if (!response.headersSent) { response.writeHead(500); response.end('BRIDGE_FAILURE'); }
      else response.destroy(error);
    }
  }, undefined));
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const port = server.address().port;
  result.origin = 'http://127.0.0.1:' + port;
  // Start readiness under the same selected private hosting factory before
  // any incoming request owner. This gate only observes that real preparation;
  // no synthetic request or alternate bridge class is used to wait for it.
  let resolveReady,rejectReady;
  const readinessObserved=new Promise((resolve,reject)=>{resolveReady=resolve;rejectReady=reject;});
  handler = profile.hosting.createServerHandler(async () => {
    profile.notePrepare();
    try {
      const next = require('next');
      app = next({dir: application, dev: false, webpack: true, hostname: '127.0.0.1', port});
      await app.prepare();
      const readyHandler=profile.wrapHandler(app.getRequestHandler());
      result.prepared=true;resolveReady();return readyHandler;
    } catch(error) {rejectReady(error);throw error;}
  });
  await readinessObserved;
  await save();
  const contract = JSON.parse(await readFile(join(here, '../fixture-contract.json')));
  const bodies = new Map();
  for (const item of contract.requests) {
    const response = await fetch(result.origin + item.path, {method: item.method ?? 'GET',
      headers: item.headers, body: item.body, redirect: 'manual', signal: AbortSignal.timeout(20000)});
    const body = await response.text();
    const failures = [];
    if (response.status !== item.status) failures.push('status ' + response.status + ' != ' + item.status);
    for (const text of item.includes ?? []) if (!body.includes(text)) failures.push('missing ' + JSON.stringify(text));
    if (item.location && response.headers.get('location') !== item.location) failures.push('location mismatch');
    if (item.json) try {
      const actual = JSON.parse(body);
      for (const [key, value] of Object.entries(item.json)) if (JSON.stringify(actual[key]) !== JSON.stringify(value)) failures.push('JSON ' + key + ' mismatch');
    } catch (error) { failures.push(error.message); }
    for (const [key, value] of Object.entries(item.responseHeaders ?? {})) if (response.headers.get(key) !== value) failures.push('header ' + key + ' mismatch');
    for (const [key, values] of Object.entries(item.responseHeaderIncludes ?? {})) for (const value of values) if (!response.headers.get(key)?.includes(value)) failures.push('header ' + key + ' missing ' + value);
    if (item.equalJsonTo && body !== bodies.get(item.equalJsonTo)) failures.push('body differs from ' + item.equalJsonTo);
    bodies.set(item.id, body);
    await writeFile(join(root, 'responses', item.id + '.txt'), body);
    result.http.push({id: item.id, status: response.status, headers: Object.fromEntries(response.headers),
      bodyBytes: Buffer.byteLength(body), bodySha256: hash(body), passed: !failures.length, failures});
    await save();
  }
  const names = [...bodies.get('server-action-form-ssr').matchAll(/name="(\$ACTION_ID_[^"]+)"/g)].map(m => m[1]);
  assert.equal(names.length, 1);
  const form = new FormData();
  form.set(names[0], ''); form.set('value', 'fixture-action');
  const action = await fetch(result.origin + '/actions', {method: 'POST', body: form,
    headers: {origin: result.origin}, redirect: 'manual', signal: AbortSignal.timeout(20000)});
  const actionBody = await action.text();
  await writeFile(join(root, 'responses/server-action-submit.txt'), actionBody);
  result.http.push({id: 'server-action-submit', status: action.status, headers: Object.fromEntries(action.headers),
    bodyBytes: Buffer.byteLength(actionBody), bodySha256: hash(actionBody),
    passed: action.status === 303 && action.headers.get('location') === '/action-result?value=fixture-action'});
  const before = JSON.parse(bodies.get('cache-first')), after = JSON.parse(bodies.get('cache-after-revalidate'));
  result.cacheInvalidation = {before, after, passed: after.generation > before.generation};
  const streamed = await fetch(result.origin + '/stream', {signal: AbortSignal.timeout(20000)});
  const chunks = []; let text = '', shell = -1, ready = -1;
  const decoder = new TextDecoder();
  for await (const chunk of streamed.body) {
    text += decoder.decode(chunk, {stream: true});
    if (shell < 0 && text.includes('NEXT_STREAM_SHELL')) shell = chunks.length;
    if (ready < 0 && text.includes('NEXT_STREAM_READY')) ready = chunks.length;
    chunks.push({base64: Buffer.from(chunk).toString('base64'), bytes: chunk.length});
  }
  text += decoder.decode();
  await writeFile(join(root, 'stream-chunks.json'), JSON.stringify(chunks, null, 2) + '\n');
  result.streaming = {chunks: chunks.length, shellChunk: shell, readyChunk: ready,
    complete: text.includes('NEXT_STREAM_SHELL') && text.includes('NEXT_STREAM_READY'),
    incrementalDeliveryObserved: ready > shell && shell >= 0};
  if (browserTools) {
    const args = [join(here, '../browser-check.mjs'), '--origin', result.origin,
      '--tools', browserTools, '--output', join(root, 'browser')];
    result.browserArgv = [process.execPath, ...args];
    const child = spawn(process.execPath, args, {stdio: ['ignore', 'inherit', 'inherit']});
    const [code, signal] = await once(child, 'exit');
    result.browserExit = {code, signal};
    result.browser = JSON.parse(await readFile(join(root, 'browser/result.json')));
  }
} catch (error) {
  result.errors.push(errorData(error));
} finally {
  if (server) try { server.closeAllConnections(); await new Promise(resolve => server.close(resolve)); } catch(error) { result.errors.push({stage:'server-close',...errorData(error)}); }
  if (app) try { await app.close(); } catch(error) { result.errors.push({stage:'app-close',...errorData(error)}); }
  result.hostBufferUnchanged = result.moduleObservations?.hostBufferUnchanged() === true;
  if (result.moduleObservations?.snapshot) result.moduleSnapshot=result.moduleObservations.snapshot();
  result.passed = result.hostBufferUnchanged && result.prepared && result.http.length === 24 && result.http.every(x => x.passed)
    && result.cacheInvalidation?.passed === true && result.streaming?.complete === true && result.streaming?.incrementalDeliveryObserved === true
    && result.moduleSnapshot?.contextMetrics?.neutralEntries === 1
    && result.moduleSnapshot?.contextMetrics?.freshEntries >= 24
    && result.moduleSnapshot?.contextMetrics?.prepareOwners?.every(x=>x===null) === true
    && result.moduleSnapshot?.contextMetrics?.pairedClassChecks >= 24
    && (!browserTools || (result.browserExit?.code === 0 && result.browser?.passed === true))
    && result.errors.length === 0 && result.transportErrors.length === 0;
  await save();
}
console.log(JSON.stringify({state: result.passed ? 'FULL_NEXT_SELECTED_PROFILE_HOST_PASSED' : 'FULL_NEXT_SELECTED_PROFILE_HOST_FAILED',
  http: result.http.length, passedHttp: result.http.filter(x => x.passed).length,
  errors: result.errors, transportErrors: result.transportErrors, guestExecuted: false}));
process.exitCode = result.passed ? 0 : 1;
