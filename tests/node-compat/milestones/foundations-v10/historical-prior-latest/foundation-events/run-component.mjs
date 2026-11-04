// Execute only after the root benchmark window ends. This validates a bundled
// prototype, not native node:events installation, aliases or module factories.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { bundleProfile } from '../profile-bundler.mjs';
assert.equal(process.version, 'v22.14.0');
assert(process.env.NODE_COMPAT_ENGINE && process.env.NODE_COMPAT_WASMTIME);
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../..');
const engine = resolve(process.env.NODE_COMPAT_ENGINE), sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
const metadata = JSON.parse(await readFile(engine + '.build.json'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
assert.equal(hash(await readFile(engine)), metadata.engineSha256); assert.equal(metadata.entropyPolicy, 'off');
assert.equal(metadata.debuggerEnabled, false); assert.equal(metadata.gcStress, false);
for (const input of metadata.sourceManifest) assert.equal(hash(await readFile(join(sourceRoot, input.path))), input.sha256, input.path);
const output = resolve(process.env.NODE_COMPAT_EVENTS_OUTPUT ?? '/tmp/starling-node-compat/foundation-events');
const toolchain = await loadToolchain(), selected = await loadComponentizer(toolchain);
const bundle = await bundleProfile({ ...toolchain, input: join(here, 'component.mjs') }); assert.deepEqual(bundle.imports, []);
const adapter = join(repository, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
assert.equal(hash(await readFile(adapter)), '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const componentOptions = { engine, preview2Adapter: adapter,
  witWorld: 'package test:events-prototype; world test { export run: func() -> string; }', worldName: 'test',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: [] };
const { component, interfaceAudit } = await selected.componentize(bundle.code, componentOptions);
assert.deepEqual(interfaceAudit.emittedImports, []);
await mkdir(output, { recursive: true }); await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain.directory, 'node_modules'), join(output, 'node_modules')); } catch (error) { if (error.code !== 'EEXIST') throw error; }
const { transpile } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const { files } = await transpile(component, { name: 'events_prototype' });
for (const [name, bytes] of Object.entries(files)) { await mkdir(dirname(join(output, name)), { recursive: true }); await writeFile(join(output, name), bytes); }
const path = join(output, 'events-prototype.component.wasm'); await writeFile(path, component); await writeFile(join(output, 'prototype.bundle.mjs'), bundle.code);
const oracle = JSON.parse(await readFile(join(here, 'node-results.json'))).cases;
function check(observed, calls) { assert.equal(observed.failure, undefined, JSON.stringify(observed.failure)); assert.equal(observed.calls, calls); assert.equal(observed.namespaceIdentity, true); assert.deepEqual(observed.cases, oracle); assert.deepEqual(observed.profile, { deferred: 13, limits: 3, eventNameCoercionDeferred: true }); return observed; }
const instance = await import(pathToFileURL(join(output, 'events_prototype.js')));
const calls = [check(JSON.parse(await instance.run()), 1), check(JSON.parse(await instance.run()), 2)];
const host = resolve(process.env.NODE_COMPAT_WASMTIME), version = spawnSync(host, ['--version'], { encoding: 'utf8' }); assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
const execution = spawnSync(host, ['run', '--invoke', 'run()', path], { encoding: 'utf8', timeout: 120000 }); assert.equal(execution.status, 0, execution.stderr);
const fresh = check(JSON.parse(JSON.parse(execution.stdout.trim())), 1);
const initialization = [];
for (const [name, expression] of [['module-once', 'events.once()'], ['async-resource', 'new events.EventEmitterAsyncResource()'], ['capture-rejections', 'new events.EventEmitter({captureRejections:true})'], ['detached-module-once', 'Promise.resolve().then(()=>events.once())']]) {
  const source = `import * as events from ${JSON.stringify(join(here, 'prototype.mjs'))}; ${expression}; export function run(){return '';}`;
  const input = join(output, name+'.mjs'); await writeFile(input, source);
  const lowered = await bundleProfile({ ...toolchain, input }); let failure;
  try { await selected.componentize(lowered.code, componentOptions); } catch (error) { failure = error; }
  assert(failure, name); assert.match(failure.message, /ERR_SM_NODE_UNSUPPORTED/, name);
  initialization.push({name, sourceSha256:hash(source), bundledSourceSha256:hash(lowered.code), error:failure.message});
}
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, installedBuiltin: false,
  engineSha256: metadata.engineSha256, sourceRoot, sourceFilesVerified: metadata.sourceManifest.length, interfaceAudit,
  componentPath: path, componentSha256: hash(component), componentBytes: component.length, bundleSha256: hash(bundle.code), bundleBytes: Buffer.byteLength(bundle.code),
  sourceFiles: await Promise.all(['prototype.mjs', 'checks.mjs', 'prototype-checks.mjs', 'component.mjs', 'run-component.mjs'].map(async name => ({ name, sha256: hash(await readFile(join(here, name))) }))),
  componentizerProvenance: selected.provenance, calls, initialization, wasmtime: { version: version.stdout.trim(), observed: fresh },
  limitations: ['Prototype is bundled guest JS and has no native module registration, aliases or installed CommonJS contract', 'Async helpers/capture/AsyncResource and warning delivery are deferred; no complete events compatibility claim', 'Component size includes the test corpus and limit loops and is not a product comparison'] };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2)+'\n'); await writeFile(join(here, 'component-results.json'), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ output, differentialCases: oracle.length, componentCalls: 3, initializationRejections: initialization.length, imports: [], wasmtimePassed: true }));
