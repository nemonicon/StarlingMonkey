// Execute after the root benchmark window. Validates bundled guest semantics;
// native builtin registration/aliases remain a separate integration gate.
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
const output = resolve(process.env.NODE_COMPAT_ASSERT_OUTPUT ?? '/tmp/starling-node-compat/foundation-assert-prototype');
const toolchain = await loadToolchain(), selected = await loadComponentizer(toolchain);
const bundle = await bundleProfile({ ...toolchain, input: join(here, 'component.mjs') }); assert.deepEqual(bundle.imports, []);
const adapter = join(repository, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
assert.equal(hash(await readFile(adapter)), '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const options = { engine, preview2Adapter: adapter,
  witWorld: 'package test:assert-prototype; world test { export run: func() -> string; }', worldName: 'test',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: [] };
const { component, interfaceAudit } = await selected.componentize(bundle.code, options);
assert.deepEqual(interfaceAudit.emittedImports, []);
await mkdir(output, { recursive: true }); await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain.directory, 'node_modules'), join(output, 'node_modules')); } catch (error) { if (error.code !== 'EEXIST') throw error; }
const { transpile, componentWit } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const emittedWit = await componentWit(component);
assert.equal(emittedWit.replace(/\s+/g, ' ').trim(), 'package root:component; world root { export run: func() -> string; }');
const { files } = await transpile(component, { name: 'assert_prototype' });
for (const [name, bytes] of Object.entries(files)) { await mkdir(dirname(join(output, name)), { recursive: true }); await writeFile(join(output, name), bytes); }
const path = join(output, 'assert-prototype.component.wasm'); await writeFile(path, component); await writeFile(join(output, 'prototype.bundle.mjs'), bundle.code);
const oracle = JSON.parse(await readFile(join(here, 'node-results.json')));
for (const [name, digest] of Object.entries(oracle.sources)) assert.equal(hash(await readFile(join(here, name))), digest, name);
function check(observed, calls) {
  assert.equal(observed.failure, undefined, JSON.stringify(observed.failure));
  assert.equal(observed.calls, calls); assert.equal(observed.namespaceIdentity, true);
  assert.deepEqual(observed.cases, oracle.cases); assert.deepEqual(observed.profile, oracle.deferredAndMutationCases); return observed;
}
const instance = await import(pathToFileURL(join(output, 'assert_prototype.js')));
const calls = [check(JSON.parse(await instance.run()), 1), check(JSON.parse(await instance.run()), 2)];
const host = resolve(process.env.NODE_COMPAT_WASMTIME), version = spawnSync(host, ['--version'], { encoding: 'utf8' }); assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
const execution = spawnSync(host, ['run', '--invoke', 'run()', path], { encoding: 'utf8', timeout: 120000 }); assert.equal(execution.status, 0, execution.stderr);
const fresh = check(JSON.parse(JSON.parse(execution.stdout.trim())), 1);
const initialization = [];
for (const [name, expression] of [
  ['deep-equality-call', 'root.deepStrictEqual({}, {})'],
  ['call-tracker-new', 'new root.CallTracker()'],
  ['async-helper-call', 'root.rejects(Promise.resolve())'],
  ['async-helper-new', 'new root.doesNotReject()'],
  ['deferred-microtask', 'Promise.resolve().then(()=>root.deepEqual({}, {}))'],
]) {
  const source = `import * as root from ${JSON.stringify(join(here, 'prototype.mjs'))}; ${expression}; export function run(){return '';}`;
  const input = join(output, name+'.mjs'); await writeFile(input, source);
  const lowered = await bundleProfile({ ...toolchain, input }); let failure;
  try { await selected.componentize(lowered.code, options); } catch (error) { failure = error; }
  assert(failure, name); assert.match(failure.message, /ERR_SM_NODE_UNSUPPORTED/, name);
  initialization.push({ name, sourceSha256: hash(source), bundledSourceSha256: hash(lowered.code), error: failure.message });
}
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, installedBuiltin: false,
  engineSha256: metadata.engineSha256, sourceRoot, sourceFilesVerified: metadata.sourceManifest.length,
  engineBuildMetadata: metadata,
  adapter: { path: adapter, sha256: hash(await readFile(adapter)) },
  interfaceAudit, emittedWit, emittedExports: [{ name: 'run', parameters: [], result: 'string' }],
  componentPath: path, componentSha256: hash(component), componentBytes: component.length,
  bundleSha256: hash(bundle.code), bundleBytes: Buffer.byteLength(bundle.code), sources: oracle.sources,
  componentHarnessSources: await Promise.all(['component.mjs', 'run-component.mjs'].map(async name => ({ name, sha256: hash(await readFile(join(here, name))) }))),
  componentizerProvenance: selected.provenance, calls, initialization,
  wasmtime: { version: version.stdout.trim(), sha256: hash(await readFile(host)), observed: fresh },
  limitations: ['Bundled isolated guest JS; no native module installation, alias/cache or CommonJS proof',
    'Deep equality, async helpers, complex matchers and CallTracker are deferred; diagnostics/stack differ',
    'Size includes test vectors; no product performance comparison'] };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2)+'\n');
await writeFile(join(here, 'component-results.json'), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ output, differentialCases: oracle.cases.length, prototypeOnlyCases: oracle.deferredAndMutationCases.length,
  componentCalls: 3, initializationRejections: initialization.length, imports: [], wasmtimePassed: true }));
