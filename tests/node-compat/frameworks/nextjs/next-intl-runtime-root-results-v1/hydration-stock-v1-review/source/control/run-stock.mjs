// Actual full Next custom-server control through the candidate message bridge.
// This is host Node evidence, never a claim of guest execution.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {Readable} from 'node:stream';
import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import {constants} from 'node:fs';
import {cp, mkdir, readFile, writeFile, rm, lstat, readdir, realpath} from 'node:fs/promises';
import {dirname, join, resolve, relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequestBridge} from '../http-bridge-candidate-v1/bridge.mjs';
import {createHostModuleRequire} from '../http-bridge-candidate-v1/module-host-provider.mjs';
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.argv[2]);
const source = resolve(process.argv[3]);
const browserTools = process.argv[4];
assert.equal(process.version, 'v22.14.0');
assert.equal(process.argv.length,5);assert(browserTools,'Both browser checks mandatory');
assert.equal(root,'/private/tmp/starling-node-compat/next-browser-hydration-stock-v1');
assert(source.endsWith('/application/.next/standalone'));
await mkdir(root, {mode: 0o700});
await mkdir(join(root, 'responses'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const descriptor = async path => { const b = await readFile(path); return {path, sha256: hash(b), bytes: b.length}; };
const plan = JSON.parse(await readFile(join(here, 'plans.json')));
assert.deepEqual(await descriptor(plan.applicationInputs.path),plan.applicationInputs);
const input = JSON.parse(await readFile(plan.applicationInputs.path));assert.equal(input.root,source);
async function walk(root){const out={files:[],dirs:['.'],links:[]};async function visit(dir){for(const name of(await readdir(dir)).sort()){const path=join(dir,name),s=await lstat(path),r=relative(root,path);if(s.isSymbolicLink())out.links.push(r);else if(s.isDirectory()){out.dirs.push(r);await visit(path);}else{assert(s.isFile(),'Only regular files/directories');out.files.push(r);}}}await visit(root);return out;}
async function sourceBookend(){assert.equal(await realpath(input.root),input.root);const tree=await walk(input.root);assert.equal(tree.links.length,0);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),input.directories.map(x=>x.path).sort());for(const r of input.files){const path=join(input.root,r.path),s=await lstat(path);assert.deepEqual(await descriptor(path),{path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);assert.equal(s.nlink,r.nlink);}for(const r of input.directories){const s=await lstat(join(input.root,r.path));assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);}}
async function copiedApplicationBookend(application){
  const tree=await walk(application);assert.equal(tree.links.length,0);
  assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),input.directories.map(x=>x.path).sort());
  for(const r of input.files){const path=join(application,r.path),s=await lstat(path);assert.deepEqual(await descriptor(path),{path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert.equal(s.nlink,1);assert(s.dev!==r.dev||s.ino!==r.ino);}
  for(const r of input.directories)assert.equal((await lstat(join(application,r.path))).mode&0o777,r.mode);
}
const result = {schemaVersion: 1, suite: 'FULL_NEXT_STOCK_ORIGINAL_MODULE_BRIDGE_HYDRATION_BROWSER_CONTROL_V1',
  node: process.version, guestExecuted: false, applicationModified: false,
  standaloneSource: source, sourceServer: await descriptor(join(source, 'server.js')),
  bridge: await descriptor(join(here, '../http-bridge-candidate-v1/bridge.mjs')), harness: await descriptor(fileURLToPath(import.meta.url)),
  http: [], errors: [], transportErrors: [], prepared: false};
const save = () => { if (result.moduleObservations?.snapshot) result.moduleSnapshot = result.moduleObservations.snapshot(); return writeFile(join(root, 'result.json'), JSON.stringify(result, null, 2) + '\n'); };
await save();
let server, app;
try {
  const application = join(root, 'application');
  await sourceBookend();
  await cp(source, application, {recursive: true, force: false, errorOnExist: true, verbatimSymlinks: true,mode:constants.COPYFILE_FICLONE});
  await copiedApplicationBookend(application);
  result.applicationCopy={files:input.regularFiles,bytes:input.bytes,byteIdentical:true,independentInodes:true,modesEqual:true,copyFlag:'COPYFILE_FICLONE',reflinkActuallyUsed:null,fallback:'Node ordinary byte copy if reflink unsupported'};
  assert.equal((await descriptor(join(application, 'server.js'))).sha256, result.sourceServer.sha256);
  // A fresh logical server starts with an empty cache. Only its owned copy is reset.
  await rm(join(application, '.next/cache'), {recursive: true, force: true});
  result.freshOwnedCacheReset = true;
  const moduleObservations = {};
  const require = createHostModuleRequire(join(application, 'server.js'), moduleObservations);
  result.moduleSource = await descriptor(join(here, '../../../foundation-module/node-module-candidate-v1/module-core.mjs'));
  result.hostModuleProvider = await descriptor(join(here, '../http-bridge-candidate-v1/module-host-provider.mjs'));
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
  server = createServer(async (request, response) => {
    if (!handler) { response.writeHead(503); response.end('Preparing'); return; }
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
      result.transportErrors.push({url: request.url, name: error.name, message: error.message, stack: error.stack});
      if (!response.headersSent) { response.writeHead(500); response.end('BRIDGE_FAILURE'); }
      else response.destroy(error);
    }
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const port = server.address().port;
  result.origin = 'http://127.0.0.1:' + port;
  const next = require('next');
  app = next({dir: application, dev: false, webpack: true, hostname: '127.0.0.1', port});
  await app.prepare();
  handler = createRequestBridge(app.getRequestHandler());
  result.prepared = true;
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
    const args = [join(here, 'browser-check.mjs'), '--origin', result.origin,
      '--tools', browserTools, '--output', join(root, 'browser')];
    result.browserArgv = [process.execPath, ...args];
    const child = spawn(process.execPath, args, {stdio: ['ignore', 'inherit', 'inherit']});
    const [code, signal] = await once(child, 'exit');
    result.browserExit = {code, signal};
    result.browser = JSON.parse(await readFile(join(root, 'browser/result.json')));
  }
} catch (error) {
  result.errors.push({name: error.name, message: error.message, stack: error.stack});
} finally {
  if (server) { server.closeAllConnections(); await new Promise(resolve => server.close(resolve)); }
  if (app) await app.close();
  try{await sourceBookend();result.originalApplicationInputsPreserved=true;}catch(error){result.originalApplicationInputsPreserved=false;result.errors.push({stage:'original-app-final-protection',name:error.name,message:error.message,stack:error.stack});}
  result.passed = result.prepared && result.http.length === 24 && result.http.every(x => x.passed)
    && result.cacheInvalidation?.passed === true && result.streaming?.complete === true && result.streaming?.incrementalDeliveryObserved === true
    && result.browserExit?.code === 0 && result.browser?.passed === true
    && result.originalApplicationInputsPreserved === true && result.errors.length === 0 && result.transportErrors.length === 0;
  await save();
}
console.log(JSON.stringify({state: result.passed ? 'FULL_NEXT_HOST_MESSAGE_BRIDGE_PASSED' : 'FULL_NEXT_HOST_MESSAGE_BRIDGE_FAILED',
  http: result.http.length, passedHttp: result.http.filter(x => x.passed).length,
  errors: result.errors, transportErrors: result.transportErrors, guestExecuted: false}));
process.exitCode = result.passed ? 0 : 1;
