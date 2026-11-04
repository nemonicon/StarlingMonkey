// Actual optional builtin gate. Requires a v4 Events-enabled OFF engine. The
// native module import remains external; no JS events adapter is bundled.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../../../../toolchain.mjs';
import { loadComponentizer } from '../../../../componentizer.mjs';
import { bundleProfile } from '../../../../profile-bundler.mjs';
import { selectedManifestsForEngine } from '../../../../module-selection.mjs';
assert.equal(process.version, 'v22.14.0');
assert(process.env.NODE_COMPAT_ENGINE && process.env.NODE_COMPAT_WASMTIME);
const here = resolve(dirname(fileURLToPath(import.meta.url)), '../../../../foundation-events'), repository = resolve(here, '../../../..');
const engine = resolve(process.env.NODE_COMPAT_ENGINE), sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
const metadataBytes = await readFile(engine + '.build.json'), metadata = JSON.parse(metadataBytes);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
assert.equal(hash(await readFile(engine)), metadata.engineSha256); assert.equal(metadata.eventsEnabled, true);
assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_EVENTS, 'ON'); assert.equal(metadata.protectedAbortListenerEnabled, true); assert.equal(metadata.strictEventExceptionPolicy?.version, 'sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1'); assert.equal(metadata.entropyPolicy, 'off');
assert.equal(metadata.debuggerEnabled, false); assert.equal(metadata.gcStress, false);
for (const input of metadata.sourceManifest) assert.equal(hash(await readFile(join(sourceRoot, input.path))), input.sha256, input.path);
const builtinManifests = selectedManifestsForEngine(metadata, { sourceRoot });
assert(builtinManifests.some(manifest => Object.hasOwn(manifest.modules, 'node:events')));
const output = resolve(process.env.NODE_COMPAT_EVENTS_OUTPUT ?? '/tmp/starling-node-compat/foundation-events-native');
await mkdir(output, { recursive: true }); await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
const toolchain = await loadToolchain(), selected = await loadComponentizer(toolchain);
try { await symlink(join(toolchain.directory, 'node_modules'), join(output, 'node_modules')); } catch (error) { if (error.code !== 'EEXIST') throw error; }
const bundle = await bundleProfile({ ...toolchain, builtinManifests, input: join(here, 'native-component.mjs') });
assert.deepEqual(bundle.imports, ['node:events']);
assert(bundle.moduleIds.every(id => !id.endsWith('/events.mjs') && !id.endsWith('/prototype.mjs')));
assert.doesNotMatch(bundle.code, /function EventEmitter\(/, 'Semantic facade must reside in the native builtin factory');
const adapter = join(repository, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
assert.equal(hash(await readFile(adapter)), '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const options = { engine, preview2Adapter: adapter, witWorld: 'package test:native-events; world test { export run: func() -> string; }', worldName: 'test',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: [] };
const { transpile } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
async function build(name, source) {
  const { component, interfaceAudit } = await selected.componentize(source, options);
  assert.deepEqual(interfaceAudit.emittedImports, []);
  await writeFile(join(output, name+'.component.wasm'), component); await writeFile(join(output, name+'.source.mjs'), source);
  const { files } = await transpile(component, { name });
  for (const [name, bytes] of Object.entries(files)) { await mkdir(dirname(join(output, name)), { recursive: true }); await writeFile(join(output, name), bytes); }
  return { modulePath: join(output, name+'.js'), componentPath: join(output, name+'.component.wasm'), componentSha256: hash(component), componentBytes: component.length, sourceSha256: hash(source), interfaceAudit };
}
const oracle = JSON.parse(await readFile(join(here, 'native-node-results.json')));
assert.equal(metadata.sourceManifest.find(input=>input.path==='builtins/node-compat/events.mjs')?.sha256, oracle.facadeSha256, 'Oracle facade must match the selected native build');
assert.equal(hash(await readFile(join(here, 'native-checks.mjs'))), oracle.checksSha256);
const fixture = await build('native_events', bundle.code);
function check(observed, count) {
  assert.equal(observed.failure, undefined, JSON.stringify(observed.failure)); assert.equal(observed.calls, count); assert.equal(observed.snapshotTicks, count + 1);
  assert.equal(observed.namespaceIdentity, true); assert.deepEqual(observed.cases, oracle.cases); assert.deepEqual(observed.nativeCases, oracle.nativeCases); assert.deepEqual(observed.profile, oracle.profile);
  assert.deepEqual(observed.commonJS, { same: true, constructorAlias: true, defaultProperty: 'undefined', errorMonitorType: 'symbol', rejectedCall: 'ERR_SM_NODE_UNSUPPORTED', rejectedConstruction: 'ERR_SM_NODE_UNSUPPORTED' });
  return observed;
}
const instance = await import(pathToFileURL(fixture.modulePath)); const calls = [check(JSON.parse(await instance.run()), 1), check(JSON.parse(await instance.run()), 2)];
const rawSource = `import root, * as a from 'node:events'; import bare, * as b from 'events'; import * as again from 'node:events'; export function run(){const saved=root.defaultMaxListeners;root.defaultMaxListeners=19;const shared=bare.defaultMaxListeners;root.defaultMaxListeners=saved;return JSON.stringify({names:Object.getOwnPropertyNames(a).sort(),sameCanonicalNamespace:a===again,sameAliasValues:Object.keys(a).every(name=>a[name]===b[name]),sameConstructors:root===bare&&root===a.EventEmitter,sharedDefault:shared,namedSnapshot:a.defaultMaxListeners,then:typeof a.then,aliasNamespacesSame:a===b});}`;
const raw = await build('native_events_aliases', rawSource); const rawInstance = await import(pathToFileURL(raw.modulePath)); const aliases = JSON.parse(rawInstance.run());
assert.deepEqual(aliases.names, oracle.cases[0].result.names); assert.equal(aliases.sameCanonicalNamespace, true); assert.equal(aliases.sameAliasValues, true); assert.equal(aliases.sameConstructors, true); assert.equal(aliases.sharedDefault, 19); assert.equal(aliases.namedSnapshot, 10); assert.equal(aliases.then, 'undefined');
const initialization = [];
for (const [name, expression, specifier = 'node:events'] of [
  ['module-once', 'events.once()'], ['async-resource', 'new events.EventEmitterAsyncResource()'], ['capture-rejections', 'new events.EventEmitter({captureRejections:true})'],
  ['awaited-once', 'await Promise.resolve().then(()=>events.once())'], ['detached-once', 'Promise.resolve().then(()=>events.once())'], ['bare-once', 'events.once()', 'events'],
]) {
  const source = `import * as events from ${JSON.stringify(specifier)}; ${expression}; export function run(){return '';}`; let failure;
  try { await selected.componentize(source, options); } catch (error) { failure = error; }
  assert(failure, name); assert.match(failure.message, /ERR_SM_NODE_UNSUPPORTED/, name); initialization.push({ name, sourceSha256: hash(source), error: failure.message });
}
const cjsInput = join(output, 'init-require.cjs'); await writeFile(cjsInput, "require('events').once(); module.exports = {};\n");
const entry = join(output, 'init-require-entry.mjs'); await writeFile(entry, `import ${JSON.stringify(cjsInput)}; export function run(){return '';}`);
const lowered = await bundleProfile({ ...toolchain, builtinManifests, input: entry }); let cjsFailure;
try { await selected.componentize(lowered.code, options); } catch (error) { cjsFailure = error; }
assert(cjsFailure); assert.match(cjsFailure.message, /ERR_SM_NODE_UNSUPPORTED/); initialization.push({ name: 'commonjs-once', sourceSha256: hash(lowered.code), error: cjsFailure.message });
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME), version = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' }); assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
const result = spawnSync(wasmtime, ['run', '--invoke', 'run()', fixture.componentPath], { encoding: 'utf8', timeout: 120000 }); assert.equal(result.status, 0, result.stderr); const fresh = check(JSON.parse(JSON.parse(result.stdout.trim())), 1);
let offAdmission = null;
if (process.env.NODE_COMPAT_EVENTS_OFF_ENGINE) {
  const offEngine = resolve(process.env.NODE_COMPAT_EVENTS_OFF_ENGINE), offMetadata = JSON.parse(await readFile(offEngine+'.build.json'));
  assert.equal(hash(await readFile(offEngine)), offMetadata.engineSha256); assert.notEqual(offMetadata.eventsEnabled, true);
  const offSourceRoot = resolve(process.env.NODE_COMPAT_EVENTS_OFF_SOURCE_ROOT ?? sourceRoot);
  for (const input of offMetadata.sourceManifest) assert.equal(hash(await readFile(join(offSourceRoot,input.path))),input.sha256,input.path);
  const offManifests = selectedManifestsForEngine(offMetadata,{sourceRoot:offSourceRoot}); let failure;
  try { await bundleProfile({...toolchain,builtinManifests:offManifests,input:join(here,'native-component.mjs')}); } catch(error) {failure=error;}
  assert(failure); assert.match(failure.message,/not admitted/);
  offAdmission={engineSha256:offMetadata.engineSha256,sourceFilesVerified:offMetadata.sourceManifest.length,error:failure.message,scope:'Actual OFF selection rejects events before packaging; no adapter fallback'};
}
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, installedBuiltin: true, engineSha256: metadata.engineSha256,
  engineReceiptSha256: hash(metadataBytes), engineReceipt: metadata, sourceRoot, sourceFilesVerified: metadata.sourceManifest.length,
  componentizerProvenance: selected.provenance, selectedModuleManifests: metadata.selectedModuleManifests,
  fixture, offAdmission, bundle: { imports: bundle.imports, moduleIds: bundle.moduleIds }, calls, rawAliasFixture: raw, aliases, initialization,
  sourceFiles: await Promise.all(['native-component.mjs', 'native-checks.mjs', 'native-require.cjs', 'checks.mjs', 'prototype-checks.mjs', 'run-native-component.mjs'].map(async name => ({ name, sha256: hash(await readFile(join(here, name))) }))),
  wasmtime: { version: version.stdout.trim(), observed: fresh }, limitations: ['Bounded EventEmitter plus addAbortListener; broader async helpers/capture/AsyncResource/abort ownership and warning delivery remain deferred',
    'Raw alias namespace records can differ by specifier; all export values/constructor state are shared', 'Recursion cap64 does not override the engine stack guard for arbitrary preexisting application stacks', 'No runtime CommonJS loader or builtin export synchronization'] };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2)+'\n'); await writeFile(join(output, 'native-component-results.json'), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ output, differentialCases: oracle.cases.length + oracle.nativeCases.length, profile: oracle.profile, initializationRejections: initialization.length, imports: [], wasmtimePassed: true }));
