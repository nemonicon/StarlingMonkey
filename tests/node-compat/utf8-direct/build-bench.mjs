// PRIVATE build/correctness gate. Packaging is explicit and separate from all
// benchmark timing. This file never changes the production engine or host.
import assert from 'node:assert/strict';
import { Buffer as NodeBuffer } from 'node:buffer';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, realpath, symlink } from 'node:fs/promises';
import { dirname, join, resolve, isAbsolute } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { gzipSync } from 'node:zlib';
import { performance } from 'node:perf_hooks';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { createWorkload, sizes, iterationsFor } from '../bench-clock-v2/workload.mjs';

const here = dirname(fileURLToPath(import.meta.url));
export const repository = resolve(here, '../../..');
export const digest = bytes => createHash('sha256').update(bytes).digest('hex');
export const ENGINE_PINS = Object.freeze({
  control: '0bb5743ba97dbbc8d2c7636fe1ae35ad37e135ea523f9c8939004198fc4c21f8',
  candidate: '3dd0fcae2887a01454720225446a545f4df99ad6a79e9f68efbb5180175a7358',
});
export const selectedOperations = Object.freeze(['utf8-encode', 'utf8-decode', 'byte-copy']);
const codecPath = 'builtins/web/text-codec/text-encoder.cpp';
const headerPath = 'builtins/web/text-codec/text-encoder-direct-testing.h';
const sourceNames = [
  'utf8-direct/build-bench.mjs', 'utf8-direct/compare.mjs', 'utf8-direct/pins.json',
  'utf8-direct/text-encoder-direct-v1.patch', 'utf8-direct/text-encoder-direct-testing.h',
  'bench-clock-v2/workload.mjs', 'bench-clock-v2/benchmark.wit',
  'bench-clock-v2/host/Cargo.toml', 'bench-clock-v2/host/Cargo.lock', 'bench-clock-v2/host/src/main.rs',
  'toolchain.mjs', 'componentizer.mjs', 'capability-policy.mjs', 'wasi-0.2.10-interfaces.json',
  'toolchain/package.json', 'toolchain/package-lock.json',
];
export function settings() {
  const paired = resolve(process.env.NODE_COMPAT_UTF8_PAIRED_ROOT ?? '/tmp/starling-node-compat/utf8-direct/paired');
  return {
    output: resolve(process.env.NODE_COMPAT_UTF8_BENCH_OUTPUT ?? '/tmp/starling-node-compat/utf8-direct/bench-release-v1'),
    controlEngine: resolve(process.env.NODE_COMPAT_UTF8_CONTROL_ENGINE ?? join(paired, 'control-freeze/engine.wasm')),
    candidateEngine: resolve(process.env.NODE_COMPAT_UTF8_CANDIDATE_ENGINE ?? join(paired, 'candidate-freeze/engine.wasm')),
    controlSourceRoot: process.env.NODE_COMPAT_UTF8_CONTROL_SOURCE_ROOT,
    candidateSourceRoot: process.env.NODE_COMPAT_UTF8_CANDIDATE_SOURCE_ROOT,
    host: resolve(process.env.NODE_COMPAT_BENCH_HOST ?? '/tmp/starling-node-compat/bench-host-target/release/node-profile-bench-host'),
    includeJcoDiagnostic: process.env.NODE_COMPAT_UTF8_BENCH_JCO === '1',
  };
}
export async function benchmarkSources() {
  return Promise.all(sourceNames.map(async path => ({ path, sha256: digest(await readFile(join(here, '..', path))) })));
}
function entriesByPath(entries) {
  const result = new Map();
  for (const entry of entries) {
    assert.equal(typeof entry.path, 'string');
    assert(!isAbsolute(entry.path) && !entry.path.split(/[\\/]/).includes('..'));
    assert(!result.has(entry.path), `duplicate source path ${entry.path}`);
    result.set(entry.path, entry.sha256);
  }
  return result;
}
function patchIdentity(patch) {
  return { name: patch.name, sha256: patch.sha256, baseRevision: patch.baseRevision,
    applied: patch.applied, files: patch.files };
}
async function buildInput(metadata, originalPath) {
  const preserved = metadata.sourceRelocation?.preservedBuildInputs?.find(entry => entry.source === originalPath);
  const path = preserved?.path ?? originalPath, bytes = await readFile(path);
  if (preserved) assert.equal(digest(bytes), preserved.sha256, `Changed preserved build input: ${path}`);
  return { path, originalPath, bytes };
}
async function cacheEvidence(metadata) {
  const cache = await buildInput(metadata, metadata.cmakeCachePath), bytes = cache.bytes;
  assert.equal(digest(bytes), metadata.cmakeCacheSha256, 'CMake cache changed since this engine receipt');
  const wanted = ['CMAKE_CXX_FLAGS', 'CMAKE_CXX_FLAGS_RELEASE', 'CMAKE_C_FLAGS', 'CMAKE_C_FLAGS_RELEASE',
    'CMAKE_EXE_LINKER_FLAGS', 'CMAKE_EXE_LINKER_FLAGS_RELEASE'];
  const flags = {};
  for (const key of wanted) {
    const line = bytes.toString().split('\n').find(value => value.startsWith(`${key}:STRING=`));
    assert(line, `Missing actual CMake flag ${key}`);
    flags[key] = line.slice(line.indexOf('=') + 1);
  }
  assert.equal(flags.CMAKE_CXX_FLAGS, '', 'No private GC/OOM compile flag is admitted');
  assert.equal(flags.CMAKE_C_FLAGS, '');
  assert.equal(flags.CMAKE_CXX_FLAGS_RELEASE, '-O3 -DNDEBUG');
  assert.equal(flags.CMAKE_C_FLAGS_RELEASE, '-O3 -DNDEBUG');
  const commandsInput = await buildInput(metadata, metadata.compileCommandsPath), commands = commandsInput.bytes;
  assert.equal(digest(commands), metadata.compileCommandsSha256, 'Compile commands changed since this engine receipt');
  const matches = JSON.parse(commands).filter(entry => entry.file.endsWith('/' + codecPath));
  assert.equal(matches.length, 1, 'Unique actual TextEncoder compile command required');
  const entry = matches[0];
  const command = entry.command ?? entry.arguments.join(' ');
  assert(!command.includes('STARLING_UTF8_DIRECT_GC_STRESS') && !command.includes('STARLING_UTF8_DIRECT_OOM_TESTING'));
  const compiledSource = entry.file.slice(0, -codecPath.length - 1);
  const project = entry.directory;
  let normalized = command;
  // These substitutions remove physical path spelling, never compiler options.
  for (const [path, replacement] of [[compiledSource, '<SOURCE>'], [project, '<BUILD>']]) {
    for (const spelling of new Set([path, path.replace('/private/tmp/', '/tmp/'), path.replace('/tmp/', '/private/tmp/')])) {
      normalized = normalized.split(spelling).join(replacement);
    }
  }
  normalized = normalized.replace(/\/[^\s]*\/spidermonkey-dist-release\/include/g, '<SM_INCLUDE>');
  return { cachePath: cache.path, originalCachePath: cache.originalPath, cacheSha256: digest(bytes), flags,
    compileCommandsPath: commandsInput.path, originalCompileCommandsPath: commandsInput.originalPath, compileCommandsSha256: digest(commands),
    compiledSourceRoot: compiledSource, textEncoderCompileCommand: command, normalizedTextEncoderCompileCommand: normalized };
}
async function opensslEvidence(metadata, engine) {
  const o = metadata.openssl;
  assert.equal(o.completeSourceAudit.state, 'verified-complete-source');
  const library = await buildInput(metadata, o.library.path), configdata = await buildInput(metadata, o.configdata.path);
  assert.equal(digest(library.bytes), o.library.sha256);
  assert.equal(digest(configdata.bytes), o.configdata.sha256);
  assert.equal(digest(await readFile(o.configureRecipe.path)), o.configureRecipe.sha256);
  const preservedMakefile = metadata.sourceRelocation?.preservedBuildInputs?.find(entry =>
    /\/(?:OpenSSL\.)?Makefile$/.test(entry.path) && /openssl/i.test(entry.source));
  let makefileAttestation = null;
  if (metadata.sourceRelocation && !preservedMakefile) {
    const path = join(dirname(engine), 'openssl-makefile-attestation.json');
    const bytes = await readFile(path), receipt = JSON.parse(bytes);
    assert.equal(receipt.schemaVersion, 1);
    assert.equal(receipt.originalEngineMetadataSha256, metadata.sourceRelocation.originalMetadataSha256);
    assert.equal(digest(await readFile(join(dirname(engine), 'engine.wasm.original.build.json'))),
      receipt.originalEngineMetadataSha256, 'Preserved Makefile must attest to the exact original engine receipt');
    const originalConfigdata = metadata.sourceRelocation.preservedBuildInputs.find(entry => entry.source === o.configdata.path);
    assert(originalConfigdata);
    assert.equal(receipt.source, join(dirname(originalConfigdata.source), 'Makefile'));
    assert.equal(resolve(receipt.path), join(dirname(engine), 'build/Makefile'));
    makefileAttestation = { receiptPath: path, receiptSha256: digest(bytes), ...receipt };
  }
  const makefilePath = preservedMakefile?.path ?? makefileAttestation?.path ?? join(dirname(o.configdata.path), 'Makefile');
  const makefile = await readFile(makefilePath, 'utf8');
  if (preservedMakefile) assert.equal(digest(makefile), preservedMakefile.sha256);
  if (makefileAttestation) assert.equal(digest(makefile), makefileAttestation.sha256);
  const names = ['CPPFLAGS', 'CFLAGS', 'CXXFLAGS', 'CNF_CPPFLAGS', 'CNF_CFLAGS', 'LIB_CPPFLAGS', 'LIB_CFLAGS'];
  const flags = {};
  for (const name of names) {
    const line = makefile.split('\n').find(value => value.startsWith(`${name}=`));
    assert(line, `Missing actual OpenSSL ${name}`); flags[name] = line.slice(name.length + 1);
  }
  const sysroot = /--sysroot=([^"\s]+)/.exec(flags.CFLAGS)?.[1];
  assert(sysroot, 'Explicit OpenSSL sysroot required');
  flags.CFLAGS = flags.CFLAGS.replace(sysroot, '<SDK_SYSROOT>');
  return { library: { ...o.library, originalPath: o.library.path, path: library.path },
    configdata: { ...o.configdata, originalPath: o.configdata.path, path: configdata.path }, makefilePath,
    makefileSha256: digest(makefile), makefileAttestation,
    normalizedFlags: flags, actualSysroot: sysroot, realSysroot: await realpath(sysroot),
    sourceManifestSha256: o.completeSourceAudit.sourceManifestSha256,
    scope: 'Actual linked OpenSSL archive bytes are required to match between the two preserved same-project builds.' };
}
export async function auditEngines(config = settings()) {
  assert(/^[0-9a-f]{64}$/.test(ENGINE_PINS.control), 'Same-project immutable control SHA has not yet been published; packaging is disabled');
  const pins = JSON.parse(await readFile(join(here, 'pins.json')));
  const engines = [];
  for (const [arm, engine] of [['control', config.controlEngine], ['candidate', config.candidateEngine]]) {
    const receiptBytes = await readFile(engine + '.build.json');
    const metadata = JSON.parse(receiptBytes);
    assert.equal(digest(await readFile(engine)), ENGINE_PINS[arm], `Wrong immutable ${arm} engine`);
    assert.equal(metadata.engineSha256, ENGINE_PINS[arm]);
    assert.equal(metadata.profileEnabled, true); assert.equal(metadata.strictInitialization, true);
    assert.equal(metadata.gcStress, false); assert.equal(metadata.oomTesting, false);
    assert.equal(metadata.debuggerEnabled, false); assert.equal(metadata.wptSupportEnabled, false);
    assert.equal(metadata.abiFixEnabled, true); assert.equal(metadata.bigIntFixEnabled, true);
    assert.equal(metadata.entropyPolicy, 'off'); assert.equal(metadata.pathEnabled, true);
    const expected = { CMAKE_BUILD_TYPE: 'Release', ENABLE_BUILTIN_NODE_COMPAT: 'ON',
      ENABLE_BUILTIN_WPT_SUPPORT: 'OFF', ENABLE_JS_DEBUGGER: 'OFF', NODE_COMPAT_ENTROPY_MODE: 'OFF',
      NODE_COMPAT_GC_STRESS: 'OFF', NODE_COMPAT_LOCKED_RUST: 'ON', NODE_COMPAT_OOM_TESTING: 'OFF',
      NODE_COMPAT_PATH: 'ON', USE_WASM_OPT: 'ON', WEVAL: 'OFF' };
    assert.deepEqual(metadata.observedCMakeOptions, expected);
    assert(metadata.componentizeJsPatches.every(patch => patch.applied));
    const explicitRoot = arm === 'control' ? config.controlSourceRoot : config.candidateSourceRoot;
    const sourceRoot = resolve(explicitRoot ?? metadata.sourceRelocation?.frozenSourceRoot ?? '');
    assert(explicitRoot || metadata.sourceRelocation?.frozenSourceRoot, 'Explicit frozen source root required');
    entriesByPath(metadata.sourceManifest);
    for (const entry of metadata.sourceManifest) assert.equal(digest(await readFile(join(sourceRoot, entry.path))), entry.sha256, `${arm}: ${entry.path}`);
    const evidence = await cacheEvidence(metadata);
    engines.push({ arm, engine, sourceRoot, engineSha256: metadata.engineSha256,
      receiptPath: engine + '.build.json', receiptSha256: digest(receiptBytes), metadata,
      configurationEvidence: evidence, opensslEvidence: await opensslEvidence(metadata, engine) });
  }
  const [control, candidate] = engines;
  const experiment = candidate.metadata.utf8DirectExperiment;
  assert.equal(experiment.variant, 'release');
  assert.equal(experiment.baseEngineSha256, pins.baseEngineSha256);
  assert.equal(experiment.patchSha256, pins.patchSha256);
  assert.equal(experiment.testingHeaderSha256, pins.testingHeaderSha256);
  assert.equal(experiment.webCodecGCStress, false); assert.equal(experiment.webCodecOOMTesting, false);
  assert.equal(experiment.actualCMakeCxxFlags, '');
  assert.equal(digest(await readFile(join(here, 'text-encoder-direct-v1.patch'))), pins.patchSha256);
  assert.equal(digest(await readFile(join(here, 'text-encoder-direct-testing.h'))), pins.testingHeaderSha256);
  const before = entriesByPath(control.metadata.sourceManifest), after = entriesByPath(candidate.metadata.sourceManifest);
  assert.equal(before.size, pins.baseNativeInputs + 1);
  assert.equal(after.size, pins.baseNativeInputs + 1);
  const changed = [...before].filter(([path, sha]) => after.get(path) !== sha).map(([path]) => path).sort();
  const added = [...after.keys()].filter(path => !before.has(path)).sort();
  assert.deepEqual(changed, [codecPath]); assert.deepEqual(added, []);
  assert.equal(before.get(codecPath), pins.baseTextEncoderSha256);
  assert.equal(after.get(codecPath), pins.patchedTextEncoderSha256);
  assert.equal(before.get(headerPath), pins.testingHeaderSha256);
  assert.equal(after.get(headerPath), pins.testingHeaderSha256);
  assert.equal(before.size, after.size);
  for (const key of ['observedCMakeOptions', 'componentizeSourceManifest', 'archivePins', 'buildTools', 'hostApi', 'selectedModuleManifests', 'buildRecipeSha256']) {
    assert.deepEqual(control.metadata[key], candidate.metadata[key], `Unmatched engine setting: ${key}`);
  }
  assert.deepEqual(control.metadata.componentizeJsPatches.map(patchIdentity), candidate.metadata.componentizeJsPatches.map(patchIdentity));
  assert.deepEqual(control.configurationEvidence.flags, candidate.configurationEvidence.flags);
  assert.equal(control.configurationEvidence.normalizedTextEncoderCompileCommand, candidate.configurationEvidence.normalizedTextEncoderCompileCommand,
    'TextEncoder compile options must match after physical-path substitution');
  for (const key of ['version', 'archive', 'profile', 'entropy', 'randSeed', 'randPatchSha256', 'appliedRandSha256', 'buildFlags']) {
    assert.deepEqual(control.metadata.openssl[key], candidate.metadata.openssl[key], `Unmatched OpenSSL ${key}`);
  }
  assert.deepEqual(control.opensslEvidence.normalizedFlags, candidate.opensslEvidence.normalizedFlags);
  assert.equal(control.opensslEvidence.realSysroot, candidate.opensslEvidence.realSysroot);
  assert.equal(control.opensslEvidence.sourceManifestSha256, candidate.opensslEvidence.sourceManifestSha256);
  assert.equal(control.opensslEvidence.library.sha256, candidate.opensslEvidence.library.sha256,
    'The final private pair must reuse identical OpenSSL archive bytes');
  assert.equal(control.opensslEvidence.library.bytes, candidate.opensslEvidence.library.bytes);
  assert.equal(control.metadata.generatedRustProject.lockSha256, candidate.metadata.generatedRustProject.lockSha256);
  assert.equal(control.metadata.generatedRustProject.manifestSha256, candidate.metadata.generatedRustProject.manifestSha256);
  assert.deepEqual(control.metadata.generatedRustProject.actualCargoBuildCommands, candidate.metadata.generatedRustProject.actualCargoBuildCommands);
  assert.equal(control.metadata.generatedRustProject.cargoBuildLocked, true);
  assert.equal(candidate.metadata.generatedRustProject.cargoBuildLocked, true);
  return { engines, changedSourcePaths: changed, addedSourcePaths: added,
    sameOpenSSLLinkedArchiveBytes: true,
    scope: 'Same-project native pair: sole encoder CPP source delta, same inactive private header, recorded compiler/configuration checks and identical linked OpenSSL archive bytes. This does not prove every other linked instruction is byte-identical.' };
}
export async function auditHost(host) {
  const reference = JSON.parse(await readFile(join(here, '../bench-clock-v2/results.json')));
  const sha256 = digest(await readFile(host));
  assert.equal(sha256, reference.hostSha256, 'Require the exact previously validated stock Wasmtime42 benchmark host');
  for (const path of ['host/Cargo.toml', 'host/Cargo.lock', 'host/src/main.rs']) {
    const row = reference.sourceManifest.find(entry => entry.path === path); assert(row);
    assert.equal(digest(await readFile(join(here, '../bench-clock-v2', path))), row.sha256);
  }
  return { path: host, sha256, referenceReportPath: join(here, '../bench-clock-v2/results.json'),
    referenceReportSha256: digest(await readFile(join(here, '../bench-clock-v2/results.json'))), wasmtime: '42.0.1' };
}
export async function buildBench(config = settings()) {
  assert.equal(process.version, 'v22.14.0'); assert.deepEqual(process.execArgv, []); assert(!process.env.NODE_OPTIONS);
  const engineAudit = await auditEngines(config), host = await auditHost(config.host);
  if (!process.env.NODE_COMPAT_TOOLCHAIN) process.env.NODE_COMPAT_TOOLCHAIN = '/tmp/starling-node-compat/native-toolchain-lock';
  const tc = await loadToolchain(), selected = await loadComponentizer(tc);
  assert.equal(selected.provenance.selection, 'patched-import-i32-clock-v2');
  const { componentWit, transpile } = await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco')));
  await mkdir(config.output, { recursive: true });
  await writeFile(join(config.output, 'build-started.json'), JSON.stringify({ createdUtc: new Date().toISOString(),
    enginePins: ENGINE_PINS, config }, null, 2) + '\n', { flag: 'wx' });
  await writeFile(join(config.output, 'package.json'), '{"type":"module"}\n');
  try { await symlink(join(tc.directory, 'node_modules'), join(config.output, 'node_modules'), 'dir'); }
  catch (error) { if (error.code !== 'EEXIST') throw error; }
  assert.equal(await realpath(join(config.output, 'node_modules')), await realpath(join(tc.directory, 'node_modules')));
  let adapter, adapterVirtualId, adapterInfo;
  if (config.includeJcoDiagnostic) {
    const adapterPath = join(tc.directory, 'node_modules/@bytecodealliance/jco/dist/node-builtins/buffer.js');
    const { createBufferBuiltin } = await import(pathToFileURL(adapterPath));
    adapter = createBufferBuiltin({ options: {} }); adapterVirtualId = adapter.resolveId('node:buffer');
    const unenv = JSON.parse(await readFile(tc.require.resolve('unenv/package.json')));
    assert.equal(unenv.version, '2.0.0-rc.24');
    const unenvPath = tc.require.resolve('unenv/node/internal/buffer/buffer');
    adapterInfo = { version: 'jco1.40.0', path: adapterPath, sha256: digest(await readFile(adapterPath)),
      unenvVersion: unenv.version, unenvPath, unenvSha256: digest(await readFile(unenvPath)),
      generatedAdapterSha256: digest(adapter.load(adapterVirtualId)),
      generatedCoreSha256: digest(adapter.load('\0jco-node-builtin:unenv-buffer-core')) };
  }
  const worldPath = join(here, '../bench-clock-v2/benchmark.wit'), witWorld = await readFile(worldPath, 'utf8');
  const oracle = createWorkload(NodeBuffer), scenarios = [];
  const requestedOperations=process.env.NODE_COMPAT_BENCH_OPERATIONS?.split(',')??selectedOperations;
  const requestedSizes=process.env.NODE_COMPAT_BENCH_SIZES?.split(',').map(Number)??sizes;
  assert(requestedOperations.length&&requestedOperations.every(operation=>selectedOperations.includes(operation)));
  assert(requestedSizes.length&&requestedSizes.every(size=>sizes.includes(size)));
  for (const operation of requestedOperations) for (const size of requestedSizes) {
    const iterations = iterationsFor(size);
    scenarios.push({ operation, size, iterations, processedBytesPerIteration: size,
      purpose: operation === 'utf8-encode' ? 'primary changed codec' : 'unchanged-operation control',
      expectedSetupChecksum: oracle.setup(operation, size) >>> 0, expectedRunChecksum: oracle.run(iterations) >>> 0 });
  }
  const records = [], bundles = new Map();
  for (const implementation of config.includeJcoDiagnostic ? ['native', 'jco-js'] : ['native']) {
    const entry = join(here, `${implementation}.benchmark-virtual-entry.mjs`);
    const entrySource = `import {Buffer as SelectedBuffer} from 'benchmark:buffer';
import {Buffer as NativeBuffer} from 'benchmark:native-registry';
import {createWorkload} from '../bench-clock-v2/workload.mjs';
if((SelectedBuffer===NativeBuffer)!==${implementation === 'native'})throw new Error('Buffer implementation contamination');
if(globalThis.Buffer!==SelectedBuffer)throw new Error('global Buffer contamination');
if(SelectedBuffer.isEncoding('base64')!==${implementation === 'jco-js'})throw new Error('Buffer encoding contamination');
const workload=createWorkload(SelectedBuffer);export const setup=workload.setup;export const run=workload.run;`;
    const modules = new Set();
    const builder = await tc.rolldown({ input: entry, platform: 'neutral', treeshake: true,
      transform: { target: 'es2016' }, plugins: [{ name: 'private-matched-utf8-codec',
        resolveId(id) {
          if (id === entry) return id;
          if (id === 'benchmark:native-registry') return { id: 'node:buffer', external: true };
          if (id === 'benchmark:buffer') return implementation === 'native' ? { id: 'node:buffer', external: true } : adapterVirtualId;
          return implementation === 'jco-js' ? adapter.resolveId(id) : null;
        },
        load(id) { if (id === entry) return entrySource; return implementation === 'jco-js' ? adapter.load(id) : null; },
        moduleParsed(info) { modules.add(info.id); },
      }] });
    let chunk;
    try { const result = await builder.generate({ format: 'esm', codeSplitting: false }); assert.equal(result.output.length, 1); chunk = result.output[0]; }
    finally { await builder.close(); }
    assert.deepEqual(chunk.imports, ['node:buffer']);
    assert(!chunk.code.includes('reference-kernel'));
    assert.equal(chunk.code.includes('ERR_JCO_UNSUPPORTED_DEPRECATED_NODE_API'), implementation === 'jco-js');
    const bundledFiles = [];
    for (const path of [...modules].filter(isAbsolute).sort()) {
      if (path !== entry) bundledFiles.push({ path, sha256: digest(await readFile(path)) });
    }
    if (implementation === 'jco-js') assert(bundledFiles.some(entry => entry.path === adapterInfo.unenvPath));
    bundles.set(implementation, { chunk, bundledFiles, modules: [...modules].sort() });
  }
  for (const engine of engineAudit.engines) for (const [implementation, bundle] of bundles) {
    const arm = `${engine.arm}-${implementation}`, directory = join(config.output, arm);
    await mkdir(directory, { recursive: true });
    await writeFile(join(directory, 'application.bundle.mjs'), bundle.chunk.code);
    const adapterPath = join(engine.sourceRoot, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
    const start = performance.now();
    const { component, interfaceAudit } = await selected.componentize(bundle.chunk.code, {
      engine: engine.engine, sourceName: 'utf8-direct-benchmark.mjs', preview2Adapter: adapterPath,
      selectedInterfaces: [], witWorld, worldName: 'benchmark',
      disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'],
    });
    const componentizeMs = performance.now() - start;
    const componentPath = join(directory, 'benchmark.component.wasm');
    await writeFile(componentPath, component);
    const emittedWit = await componentWit(component);
    assert.deepEqual(emittedWit.split('\n').filter(line => /^\s*import /.test(line)), []);
    await writeFile(join(directory, 'emitted.wit'), emittedWit);
    const { files } = await transpile(component, { name: 'benchmark' });
    for (const [name, data] of Object.entries(files)) {
      await mkdir(dirname(join(directory, name)), { recursive: true }); await writeFile(join(directory, name), data);
    }
    const guest = await import(pathToFileURL(join(directory, 'benchmark.js')));
    for (const scenario of scenarios) {
      assert.equal(guest.setup(scenario.operation, scenario.size) >>> 0, scenario.expectedSetupChecksum, `${arm}: full setup checksum`);
      assert.equal(guest.run(scenario.iterations) >>> 0, scenario.expectedRunChecksum, `${arm}: result fingerprint checksum`);
    }
    records.push({ arm, engineArm: engine.arm, implementation, engineSha256: engine.engineSha256,
      componentPath, componentSha256: digest(component), componentBytes: component.length,
      componentGzipBytes: gzipSync(component).length, componentizeMs, interfaceAudit, emittedImports: [], emittedWit,
      bundleSha256: digest(bundle.chunk.code), bundledFiles: bundle.bundledFiles, bundledModules: bundle.modules,
      preview2Adapter: { path: adapterPath, sha256: digest(await readFile(adapterPath)) },
      correctness: { scenarios: scenarios.length, fullSetupChecksums: 'Node22.14.0 matched',
        loopChecksums: 'Node22.14.0 matched', contaminationGate: 'passed during snapshot initialization' } });
  }
  for (const implementation of bundles.keys()) {
    const pair = records.filter(record => record.implementation === implementation);
    assert.equal(pair[0].bundleSha256, pair[1].bundleSha256);
    assert.deepEqual(pair[0].preview2Adapter.sha256, pair[1].preview2Adapter.sha256);
    assert.equal(pair[0].emittedWit, pair[1].emittedWit);
  }
  const manifest = { schemaVersion: 1, state: 'actual-components-correctness-verified', createdUtc: new Date().toISOString(),
    node: process.version, nodeExecutable: process.execPath, nodeExecutableSha256: digest(await readFile(process.execPath)),
    config, host, engineAudit, sourceManifest: await benchmarkSources(), componentizerProvenance: selected.provenance,
    world: { path: worldPath, sha256: digest(witWorld) }, adapter: adapterInfo ?? null, scenarios, records,
    protocol: { primary: 'control-native versus candidate-native; sole TextEncoder CPP source delta, same inactive testing header retained in both',
      diagnostic: config.includeJcoDiagnostic ? 'Actual Jco Buffer adapter on each engine; additional non-primary controls' : 'not selected',
      sourceMatching: engineAudit.scope,
      bundler: { name: 'Rolldown', version: '1.2.16', target: 'es2016', platform: 'neutral', treeshake: true, minify: false },
      setup: 'Selected payload preparation and one full FNV correctness hash, outside throughput timing',
      run: 'Unchanged bench-clock-v2 workload, O(1) per-result fingerprint; fixed iteration count, host clock only',
      backingObservation: 'Primary UTF8 encode reads visible result bytes/length, not .buffer. Small direct Uint8Array results can defer ArrayBuffer materialization; applications inspecting .buffer can have a different cost.',
      checksumTransport: 'Existing s32 all-bits checksum carrier; direct WIT u32/i64 gates remain separate',
      processedBytes: 'ASCII source payload bytes per operation', selectedInterfaces: [],
      scope: 'Private Release OFF non-Weval codec experiment, not whole-application or full Buffer performance' } };
  const path = join(config.output, 'build-results.json');
  await writeFile(path, JSON.stringify(manifest, null, 2) + '\n');
  console.log(JSON.stringify({ output: path, records: records.map(({ arm, componentBytes, componentSha256 }) => ({ arm, componentBytes, componentSha256 })) }, null, 2));
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.includes('--plan')) console.log(JSON.stringify({ state: 'plan-only; no packaging or timing', ...settings(),
    enginePins: ENGINE_PINS, operations: selectedOperations, sizes, manifest: 'build-results.json' }, null, 2));
  else await buildBench();
}
