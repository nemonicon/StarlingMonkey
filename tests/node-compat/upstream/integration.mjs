import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { cp, mkdir, open, readFile, readdir, realpath, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { context, output, repository, hash, auditRegressionImports, regressionImports } from './common.mjs';

assert(process.env.NODE_COMPAT_WASMTIME, 'Explicit Wasmtime42 required');
const ctx = await context();
const directory = join(output, 'starling-integration');
await mkdir(join(directory, 'wit'), { recursive: true });
await cp(join(repository, 'host-apis/wasi-0.2.10/wit/deps'), join(directory, 'wit/deps'), { recursive: true });
await writeFile(join(directory, 'wit/test.wit'), 'package test:starling-upstream; world test { export wasi:http/incoming-handler@0.2.10; }');
const { _setPreopens, _clearPreopens } = await import(pathToFileURL(ctx.require.resolve('@bytecodealliance/preview2-shim/filesystem')));
let testsRoot = join(repository, 'tests');
let traceAdaptation;
if (process.env.NODE_COMPAT_UPSTREAM_TRACE_CRYPTO === '1') {
  testsRoot = join(directory, 'diagnostic-tests');
  await cp(join(repository, 'tests/integration'), join(testsRoot, 'integration'), { recursive: true });
  await cp(join(repository, 'tests/assert.js'), join(testsRoot, 'assert.js'));
  const serverPath = join(testsRoot, 'integration/test-server.js');
  const original = await readFile(serverPath, 'utf8');
  const changed = original.replace('const maybePromise = subtest();', "console.log('UPSTREAM SUBTEST ' + name); const maybePromise = subtest();");
  assert.notEqual(changed, original);
  await writeFile(serverPath, changed);
  traceAdaptation = { purpose: 'Name the currently executing original crypto subtest before a native trap', originalSha256: hash(original), tracedSha256: hash(changed) };
}
testsRoot = await realpath(testsRoot);
const sourcePath = join(testsRoot, 'integration/test-server.js');
process.chdir(testsRoot);
let component;
try {
  _setPreopens({ [join(directory, 'wit')]: join(directory, 'wit') });
  ({ component } = await ctx.componentize({ sourcePath, engine: ctx.engine, preview2Adapter: ctx.preview2Adapter,
    witPath: join(directory, 'wit'), worldName: 'test' }));
} finally { _clearPreopens(); }
const componentPath = join(directory, 'test-server.component.wasm');
await writeFile(componentPath, component);
const wit = await ctx.componentWit(component);
await writeFile(join(directory, 'emitted.wit'), wit);
const emittedImports = [...wit.matchAll(/^\s*import ([^;]+);/gm)].map(match => match[1]);
auditRegressionImports(wit);
const logPath = join(directory, 'wasmtime.log');
const log = await open(logPath, 'w');
const command = [resolve(process.env.NODE_COMPAT_WASMTIME), 'serve', '-S', 'common', '--addr', '127.0.0.1:0', componentPath];
const host = spawn(command[0], command.slice(1), { stdio: ['ignore', log.fd, log.fd] });
let exited = false, exitStatus;
const exit = new Promise(resolve => host.once('exit', (code, signal) => { exited = true; exitStatus = { code, signal }; resolve(); }));
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const allNames = ['blob', 'btoa', 'crypto', 'event', 'fetch', 'formdata', 'performance', 'textdecoder', 'timers', 'urlsearchparams'];
const names = process.env.NODE_COMPAT_UPSTREAM_ROUTES?.split(',') ?? allNames;
assert(names.every(name => allNames.includes(name)));
const results = [];
let address;
try {
  const deadline = Date.now() + 60000;
  while (!address && Date.now() < deadline) {
    const text = await readFile(logPath, 'utf8');
    assert(!exited, `Wasmtime exited: ${text}`);
    address = /Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text)?.[1];
    if (!address) await pause(100);
  }
  assert(address, 'Wasmtime listener timeout');
  for (const name of names) {
    try {
      const response = await fetch(address + '/' + name, { signal: AbortSignal.timeout(45000),
        headers: { 'User-Agent': 'test-agent', 'eXample-hEader': 'Header Value' } });
      const body = await response.text();
      results.push({ name, pass: response.status === 200 && body.startsWith('OK ' + name), status: response.status, body });
    } catch (error) { results.push({ name, pass: false, error: error.message }); }
    console.log(JSON.stringify(results.at(-1)));
  }
} finally {
  if (!exited) host.kill('SIGINT');
  await Promise.race([exit, pause(5000)]);
  if (!exited) { host.kill('SIGKILL'); await exit; }
  await log.close();
}
const sourceManifest = [];
for (const entry of await readdir(join(repository, 'tests/integration'), { recursive: true, withFileTypes: true })) {
  if (entry.isFile() && entry.name.endsWith('.js')) {
    const path = join(entry.parentPath, entry.name);
    sourceManifest.push({ path, sha256: hash(await readFile(path)) });
  }
}
const report = { schema: 1, engineSha256: ctx.engineSha256, engine: ctx.engine,
  componentizerProvenance: ctx.componentizerProvenance,
  componentSha256: hash(component), componentBytes: component.length, componentPath, emittedImports,
  allowedImports: regressionImports, selectedFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'],
  world: 'test:starling-upstream/test', worldSource: await readFile(join(directory, 'wit/test.wit'), 'utf8'),
  command, sourceManifest, results, passed: results.filter(result => result.pass).length,
  failed: results.filter(result => !result.pass).length, logPath, stopped: exited, exitStatus,
  adaptation: 'Original integration server and all ten registered handlers/assertions, custom engine, external output, loopback serve; additionally require OK response body',
  traceAdaptation, upstreamSkips: (await readFile(logPath, 'utf8')).split('\n').filter(line => line.includes('SKIPPING TEST')),
};
await writeFile(join(output, 'starling-integration-results.json'), JSON.stringify(report, null, 2) + '\n');
assert.equal(report.failed, 0, 'Inspect exact route failures; no failure is silently skipped');
