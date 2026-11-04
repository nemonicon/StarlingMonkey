// Dedicated fault-engine gate. No released-engine or fake-throw fallback.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { bundleProfile } from '../profile-bundler.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, '../../..');
const output = resolve(process.env.NODE_COMPAT_OOM_OUTPUT ?? '/tmp/starling-node-compat/oom-gate');
assert(process.env.NODE_COMPAT_ENGINE, 'Explicit DEBUG + NODE_COMPAT_OOM_TESTING engine required');
assert(process.env.NODE_COMPAT_WASMTIME, 'Explicit Wasmtime 42.0.1 path required');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const metadataPath = resolve(process.env.NODE_COMPAT_ENGINE_METADATA ?? engine + '.build.json');
const metadata = JSON.parse(await readFile(metadataPath));
const sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
assert.equal(metadata.engineSha256, hash(await readFile(engine)));
assert.equal(metadata.profileEnabled, true);
assert.equal(metadata.oomTesting, true, 'Silently disabled allocator fault instrumentation is forbidden');
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE, 'Debug');
assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_OOM_TESTING, 'ON');
assert.equal(metadata.componentizeJsRevision, '4d812f5a7b524cea5bcfd565cac55f3fab876a57');
assert.equal(metadata.auditedBaseRevision, '54b3329b3ce818fd1f244e871e9c259b63667cda');
const requiredSources = ['builtins/node-compat/buffer.cpp', 'builtins/node-compat/oom-testing.h',
  'builtins/node-compat/factories.generated.h', 'cmake/builtins.cmake'];
const paths = new Set(metadata.sourceManifest.map(entry => entry.path));
requiredSources.forEach(path => assert(paths.has(path), 'Missing engine source provenance: ' + path));
for (const entry of metadata.sourceManifest) {
  const path = resolve(sourceRoot, entry.path);
  assert(path.startsWith(sourceRoot + '/'));
  assert.equal(hash(await readFile(path)), entry.sha256, 'Stale fault engine source: ' + entry.path);
}
const version = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' });
assert.equal(version.status, 0, version.stderr);
assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
const toolchainContext = await loadToolchain();
const { directory: toolchain, require, rolldown, parseAst } = toolchainContext;
const componentizeDirectory = join(toolchain, 'node_modules/@bytecodealliance/componentize-js');
const { componentize, provenance: componentizer } = await loadComponentizer(toolchainContext,
  { debugScalarOOMDiagnostic: true });
const { transpile, componentWit } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
assert.notEqual(metadata.engineSha256,
  hash(await readFile(join(componentizeDirectory, 'lib/starlingmonkey_embedding.wasm'))));
await mkdir(output, { recursive: true });
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain, 'node_modules'), join(output, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const bundle = await bundleProfile({ rolldown, parseAst, input: join(here, 'component.mjs') });
assert.deepEqual([...bundle.imports].sort(), ['node:buffer', 'node:child_process']);
assert(bundle.moduleIds.every(id => !/node_modules\/(?:buffer|unenv)|node-builtins|reference-kernel|buffer-facade/.test(id)));
await writeFile(join(output, 'application.bundle.mjs'), bundle.code);
const world = await readFile(join(here, 'profile.wit'), 'utf8');
const { component, debugDiagnosticAudit } = await componentize(bundle.code, { engine, witWorld: world, worldName: 'profile', selectedInterfaces: [],
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'] });
assert(debugDiagnosticAudit, 'The scalar-only DEBUG loader audit must be returned');
const componentPath = join(output, 'native-buffer-oom.component.wasm');
await writeFile(componentPath, component);
const wit = await componentWit(component);
await writeFile(join(output, 'emitted.wit'), wit);
const imports = wit.split('\n').filter(line => /^\s*import /.test(line));
assert.deepEqual(imports, [], 'Allocator tests must not add host services');
const { files } = await transpile(component, { name: 'native-buffer-oom' });
for (const [name, bytes] of Object.entries(files)) {
  const path = join(output, name); await mkdir(dirname(path), { recursive: true }); await writeFile(path, bytes);
}
const expectedFaults = ['decode-utf8-staging', 'decode-uint8array', 'encode-malloc-staging', 'encode-js-string'];
const failureStages = { 1: 'initial integrity', 2: 'decode UTF8 staging OOM',
  3: 'decode Uint8Array OOM', 4: 'decode recovery', 5: 'encode malloc staging OOM',
  6: 'encode JS string OOM', 7: '32 recovery pairs', 8: 'unsupported Error distinction',
  9: 'bounded RangeError distinction', 10: 'final integrity' };
function check(status, call) {
  assert(Number.isInteger(status), 'Expected scalar s32 test status');
  assert(status > 0, 'Guest check failed at stage: ' + (failureStages[-status] ?? status));
  assert.equal(status, (call << 16) | 0x7ff, 'All checks and resumed call count must pass');
  return { status, calls: status >>> 16, passedMask: status & 0xffff,
    faults: call === 1 ? expectedFaults : [], snapshotInitialization: 'both kernels succeeded',
    liveBuffersIntact: true, privateBrandsIntact: true, recoveryPairs: 32,
    unsupportedDistinct: true, profileLimitDistinct: true };
}
const guest = await import(pathToFileURL(join(output, 'native-buffer-oom.js')));
const calls = [];
for (let i = 1; i <= 3; i++) {
  calls.push(check(await guest.run(), i));
}
const host = spawnSync(wasmtime, ['run', '--invoke', 'run()', componentPath],
  { encoding: 'utf8', timeout: 180000 });
assert.equal(host.status, 0, host.error?.message || host.stderr || host.stdout);
const wasmtimeReport = check(Number(host.stdout.trim()), 1);
const report = { schema: 1, verifiedAtUtc: new Date().toISOString(), node: process.version,
  engine, engineSha256: metadata.engineSha256, metadataPath, metadata, engineSourceRoot: sourceRoot, componentizer,
  debugDiagnosticAudit,
  componentPath, componentBytes: component.length, componentSha256: hash(component),
  bundleImports: bundle.imports, bundleModuleIds: bundle.moduleIds, emittedImports: imports, emittedWit: wit,
  wasmtime: version.stdout.trim(), calls, wasmtimeReport,
  resultCarrier: { wit: 'run: func() -> s32', passedMask: '0x7ff', callCountBits: 'bits16..30',
    failure: 'negative stage number', failureStages,
    reason: 'DEBUG indirect canonical-memory bindings are unavailable. The scoped scalar path never accesses the shifted DEBUG memory view; every Buffer/string/Error operation is checked inside the guest.' },
  sourceManifest: await Promise.all(['component.mjs', 'profile.wit', 'run.mjs'].map(async path =>
    ({ path, sha256: hash(await readFile(join(here, path))) }))),
  faultMechanism: 'Pinned DEBUG SpiderMonkey FailureSimulator: first allocator checkpoint in each selected API; native assertions verify actual simulator trip, null result and pending OOM. No manual JS/native Error substitutes.',
  ownershipMechanism: 'Tracked JS::FreePolicy delegate counts native temporary acquisitions/releases; every kernel exit asserts live count zero and totals equal, including early returns.',
  limitations: ['Four selected native kernel allocation API scopes; not exhaustive failure at every internal allocator check or engine-wide OOM.',
    'Facade, TextEncoder/TextDecoder, module installation, ArrayBuffer materialization and component/bootstrap OOM are outside these four checkpoints.',
    'This separate debug fault engine is not a deployment artifact or a performance baseline.',
    'Only the explicitly guarded scalar s32 diagnostic world is admitted for DEBUG; indirect string/list Component Model interoperability remains unavailable in these debug engines.',
    'Jco invokes one resumed instance three times; Wasmtime invokes a fresh instance once. Both execute 32 successful kernel pairs after the four failures.',
    'The simulator and counters assume this current single-threaded guest; this is not a concurrency failure test.'] };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
await writeFile(join(here, 'results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ output, engineSha256: report.engineSha256,
  componentSha256: report.componentSha256, points: expectedFaults, calls: calls.length,
  wasmtimePassed: true, emittedImports: imports }, null, 2));
