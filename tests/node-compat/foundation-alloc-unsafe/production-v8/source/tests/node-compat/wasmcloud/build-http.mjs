import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { cp, mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { createProfilePlugin } from '../profile-bundler.mjs';
import { selectedManifestsForEngine } from '../module-selection.mjs';
import { selectCoreExpectations } from '../core-expectations.mjs';
import { RANDOM } from '../entropy/selection-policy.mjs';
import { makeOracleCorpus } from '../oracle.mjs';
import { componentizeSelectedHTTP } from './http-stubbing.mjs';
import { auditClockDependency } from './type-audit.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, '../../..');
const engineSourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
assert(process.env.NODE_COMPAT_ENGINE, 'Set NODE_COMPAT_ENGINE to the native profile embedding engine');
assert(process.env.NODE_COMPAT_WASM_TOOLS, 'Set NODE_COMPAT_WASM_TOOLS to the repository-pinned wasm-tools 1.235.0 executable');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const output = resolve(process.env.NODE_COMPAT_HTTP_OUTPUT ?? '/tmp/starling-node-compat/wasmcloud-http');
const toolchainInfo = await loadToolchain();
const { directory: toolchain, require, rolldown, parseAst } = toolchainInfo;
const hash = value => createHash('sha256').update(value).digest('hex');
const engineBytes = await readFile(engine);
const metadataPath = resolve(process.env.NODE_COMPAT_ENGINE_METADATA ?? engine + '.build.json');
const engineMetadata = JSON.parse(await readFile(metadataPath));
assert.equal(engineMetadata.engineSha256, hash(engineBytes));
assert.equal(engineMetadata.profileEnabled, true);
const entropyPolicy = engineMetadata.entropyPolicy ?? 'off';
assert(['off', 'runtime-only'].includes(entropyPolicy));
const runtimeEntropy = entropyPolicy === 'runtime-only';
const selectedInterfaces = ['wasi:http/types@0.2.10', 'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:clocks/monotonic-clock@0.2.10', ...(runtimeEntropy ? [RANDOM] : [])].sort();
const builtinManifests = selectedManifestsForEngine(engineMetadata, { sourceRoot: engineSourceRoot });
assert.equal(engineMetadata.debuggerEnabled, false);
assert.equal(engineMetadata.gcStress, false, 'Use the normal native engine for HTTP host validation');
assert.equal(engineMetadata.auditedBaseRevision ?? engineMetadata.starlingMonkeyRevision, '54b3329b3ce818fd1f244e871e9c259b63667cda');
assert.equal(engineMetadata.componentizeJsRevision, '4d812f5a7b524cea5bcfd565cac55f3fab876a57');
const sourcePaths = new Set(engineMetadata.sourceManifest.map(entry => entry.path));
for (const required of ['buffer.cpp', 'register.cpp', 'factories.generated.h', 'buffer-facade.mjs', 'child-process.mjs', 'unsupported.mjs', 'export-manifest.node-v22.14.0.json']) {
  assert(sourcePaths.has('builtins/node-compat/' + required), `Build manifest omits ${required}`);
}
assert(sourcePaths.has('cmake/builtins.cmake'));
for (const entry of engineMetadata.sourceManifest) {
  const path = resolve(engineSourceRoot, entry.path);
  assert(path.startsWith(engineSourceRoot + '/'));
  assert.equal(hash(await readFile(path)), entry.sha256, `Stale native engine: ${entry.path}`);
}
const generation = spawnSync(process.execPath, [join(engineSourceRoot, 'builtins/node-compat/generate-factories.mjs'), '--check'], { encoding: 'utf8' });
assert.equal(generation.status, 0, generation.stderr || generation.stdout);
const releasedDirectory = join(toolchain, 'node_modules/@bytecodealliance/componentize-js');
assert.notEqual(hash(engineBytes), hash(await readFile(join(releasedDirectory, 'lib/starlingmonkey_embedding.wasm'))), 'Released engine fallback forbidden');
const { componentize, directory: componentizeDirectory, provenance: componentizerProvenance } = await loadComponentizer(toolchainInfo);
const { componentWit, componentNew, metadataAdd } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
const { _setPreopens, _clearPreopens } = await import(pathToFileURL(require.resolve('@bytecodealliance/preview2-shim/filesystem')));
await mkdir(output, { recursive: true });
const witDirectory = join(output, 'wit');
await mkdir(witDirectory, { recursive: true });
await cp(join(repository, 'host-apis/wasi-0.2.10/wit/deps'), join(witDirectory, 'deps'), { recursive: true });
const worldFilename = runtimeEntropy ? 'profile-runtime-entropy.wit' : 'profile.wit';
const worldSource = await readFile(join(here, worldFilename), 'utf8');
await writeFile(join(witDirectory, 'profile.wit'), worldSource);
const coreExpectations = selectCoreExpectations(engineMetadata, { sourceRoot: engineSourceRoot });
const corpus = makeOracleCorpus();
const httpEntry = resolve(process.env.NODE_COMPAT_HTTP_ENTRY ?? join(here, 'http.mjs'));
const utilFoundationsFixture = httpEntry === resolve(here, '../foundations/http-v7.mjs');
const expandedFoundationsFixture = utilFoundationsFixture || httpEntry === resolve(here, '../foundations/http-v6.mjs');
const foundationsIntegrationFixture = expandedFoundationsFixture || httpEntry === resolve(here, '../foundations/http.mjs');
let foundationOracles = null;
const virtualModules = { 'node-compat:core-expectations': `export default ${JSON.stringify(coreExpectations)};`, 'node-compat:oracle-vectors': `export default ${JSON.stringify(corpus)};`, 'node-compat:entropy-policy': `export default ${JSON.stringify(entropyPolicy)};` };
if (foundationsIntegrationFixture) {
  assert.equal(engineMetadata.pathEnabled, true); assert.equal(engineMetadata.eventsEnabled, true);
  const pathDirectory = resolve(here, '../foundation-path');
  const lexical = JSON.parse(await readFile(join(pathDirectory, 'lexical-vectors.json')));
  const globs = JSON.parse(await readFile(join(pathDirectory, 'glob-vectors.json')));
  const globReport = JSON.parse(await readFile(join(pathDirectory, 'glob-results.json')));
  const pathManifest = builtinManifests.find(manifest => Object.hasOwn(manifest.modules, 'node:path'));
  const pathCorpus = { lexical, globs, denied: globReport.denied, acceptedAdversarial: globReport.acceptedAdversarial,
    exportNames: [...pathManifest.modules['node:path'].exports].sort() };
  const eventsOracle = JSON.parse(await readFile(resolve(here, '../foundation-events/native-node-results.json')));
  assert.equal(engineMetadata.sourceManifest.find(input => input.path === 'builtins/node-compat/events.mjs')?.sha256, eventsOracle.facadeSha256);
  virtualModules['node-compat:path-oracles'] = `export default ${JSON.stringify(pathCorpus)};`;
  foundationOracles = { path: { lexical: lexical.length, globs: globs.length, budgets: pathCorpus.denied.length,
    acceptedAdversarial: pathCorpus.acceptedAdversarial.length, corpusSha256: hash(JSON.stringify(pathCorpus)) },
    events: { cases: eventsOracle.cases.length, nativeCases: eventsOracle.nativeCases.length, profile: eventsOracle.profile, facadeSha256: eventsOracle.facadeSha256 },
    dynamicBareAliases: ['buffer', 'child_process', 'path', 'path/posix', 'path/win32', 'events'],
    fixtureSha256: hash(await readFile(httpEntry)) };
  if (expandedFoundationsFixture) {
    for (const field of ['stringDecoderEnabled', 'assertEnabled', 'querystringEnabled']) assert.equal(engineMetadata[field], true);
    assert.equal(engineMetadata.sourceManifest.find(input => input.path === 'builtins/web/text-codec/text-decoder.cpp')?.sha256,
      '4697d8951a724d92e7550d48bd10cd2652d4d789797dc90ad8401216e9a4512c');
    const decoderCorpus = JSON.parse(await readFile(resolve(here, '../foundation-string-decoder/component-corpus.json')));
    virtualModules['node-compat:string-decoder-oracles'] = `export default ${JSON.stringify(decoderCorpus)};`;
    const readOracle = async name => JSON.parse(await readFile(resolve(here, '../foundation-'+name+'/native-node-results.json')));
    const assertOracle = await readOracle('assert'), querystringOracle = await readOracle('querystring');
    for (const oracle of [assertOracle, querystringOracle]) for (const [name, sha256] of Object.entries(oracle.sources)) {
      if (sourcePaths.has('builtins/node-compat/'+name)) assert.equal(engineMetadata.sourceManifest.find(input => input.path === 'builtins/node-compat/'+name)?.sha256, sha256);
    }
    foundationOracles.stringDecoder = { sequences: decoderCorpus.sequences.length,
      writes: decoderCorpus.sequences.reduce((sum, value) => sum+value.chunks.length, 0), genericCases: decoderCorpus.decoderCases.length,
      preservedOrderingDeviations: decoderCorpus.deviations.length, corpusSha256: hash(JSON.stringify(decoderCorpus)) };
    foundationOracles.assert = { cases: assertOracle.cases, profile: assertOracle.sourceProfile };
    foundationOracles.querystring = { cases: querystringOracle.cases, profile: querystringOracle.sourceProfile };
    foundationOracles.dynamicBareAliases.push('string_decoder', 'assert', 'assert/strict', 'querystring');
    if (utilFoundationsFixture) {
      assert.equal(engineMetadata.utilEnabled, true);
      const utilOracle = await readOracle('util');
      for (const [name, sha256] of Object.entries(utilOracle.sources)) {
        if (sourcePaths.has('builtins/node-compat/'+name)) assert.equal(engineMetadata.sourceManifest.find(input => input.path === 'builtins/node-compat/'+name)?.sha256, sha256);
      }
      foundationOracles.util = { variants: utilOracle.variants, expectedExports: utilOracle.expectedExports };
      foundationOracles.dynamicBareAliases.push('util', 'util/types', 'sys');
    }
  }
}

const preview1AdapterPath = join(repository, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
const preview1Adapter = await readFile(preview1AdapterPath);
assert.equal(hash(preview1Adapter), '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const adapterImportModules = [...new Set(WebAssembly.Module.imports(new WebAssembly.Module(preview1Adapter)).map(entry => entry.module))].sort();
const standardImports = ['wasi:http/types@0.2.10', ...(runtimeEntropy ? [RANDOM] : [])];
const build = await rolldown({
  input: httpEntry, platform: 'neutral', treeshake: false,
  plugins: [
    { name: 'selected-standard-http-interface', resolveId(id) {
      if (standardImports.includes(id)) return { id, external: true };
      if (id.startsWith('wasi:')) throw new Error(`Unselected WASI interface: ${id}`);
    } },
    createProfilePlugin(parseAst, { builtinManifests, virtualModules }),
  ],
});
let bundle;
try {
  const generated = await build.generate({ format: 'esm', codeSplitting: false });
  assert.equal(generated.output.length, 1);
  bundle = generated.output[0];
} finally { await build.close(); }
const expectedBundleImports = ['node:buffer', 'node:child_process', 'wasi:http/types@0.2.10', ...(foundationsIntegrationFixture ? ['node:path', 'node:path/posix', 'node:path/win32', 'node:events'] : []),
  ...(expandedFoundationsFixture ? ['node:string_decoder', 'node:assert', 'node:assert/strict', 'node:querystring'] : []),
  ...(utilFoundationsFixture ? ['node:util', 'node:util/types', 'node:sys'] : [])];
assert.deepEqual([...bundle.imports].sort(), expectedBundleImports.sort());
if (foundationsIntegrationFixture) {
  assert(Object.keys(bundle.modules).every(id => !/builtins\/node-compat\/|foundation-[^/]+\/prototype\.mjs|path-vendor/.test(id)), 'Joint app must import actual native modules');
  assert.match(bundle.code, /import\(id\)/, 'Computed bare imports must survive bundling');
}
assert.doesNotMatch(bundle.code, /reference-kernel|buffer-facade|createBufferModule|hexEncode|hexDecode|__require/);
assert(Object.keys(bundle.modules).every(id => !/node_modules\/(?:buffer|unenv)|node-builtins/.test(id)));
await writeFile(join(output, 'http.bundle.mjs'), bundle.code);
// The host-side WIT parser uses the npm toolchain's filesystem shim. Grant only
// this generated WIT directory to that build tool; it is not a deployed import.
_setPreopens({ [witDirectory]: witDirectory });
let component;
let packagingAudit;
let finalCore;
let interfaceAudit;
try {
  ({ component, finalCore, packagingAudit, interfaceAudit } = await componentizeSelectedHTTP(componentize, componentizeDirectory, bundle.code, {
    engine, witPath: witDirectory, worldName: 'profile', preview2Adapter: preview1AdapterPath,
    disableFeatures: ['stdio', 'clocks', 'fetch-event', ...(runtimeEntropy ? [] : ['random'])], selectedInterfaces,
  }, componentizerProvenance, async core => {
    // Finalize before the shared wrapper audits selected interfaces. Auditing
    // an intermediate adapter composition would describe a different artifact.
    assert(!WebAssembly.Module.imports(new WebAssembly.Module(core)).some(entry => entry.module === 'wasi_snapshot_preview1'));
    return metadataAdd(await componentNew(core, [], false), Object.entries({
      language: [['JavaScript', '']], 'processed-by': [['ComponentizeJS', '0.23.0'], ['StarlingMonkey selected HTTP packaging', '0.1.0']],
    }));
  }));
} finally { _clearPreopens(); }
// No core Preview1 imports remain, so no adapter is needed. Reuse the same
// public Jco wrapping/producers APIs with an empty adapter set. The remaining
// nominal duration type dependency is checked separately from clock functions.
assert(packagingAudit.coreImportModules.every(id => id !== 'wasi_snapshot_preview1'));
packagingAudit.finalWrapping = { api: 'Jco componentNew(finalCore, [], false) + metadataAdd',
  adapters: [], reason: 'Final core imports contain no wasi_snapshot_preview1 interface', coreSha256: hash(finalCore) };
await writeFile(join(output, 'native-profile-http.core.wasm'), finalCore);
await writeFile(join(output, 'packaging-audit.json'), JSON.stringify(packagingAudit, null, 2) + '\n');
const componentPath = join(output, 'native-profile-http.component.wasm');
await writeFile(componentPath, component);
const emittedWit = await componentWit(component);
await writeFile(join(output, 'emitted.wit'), emittedWit);
const emittedImports = [...emittedWit.matchAll(/^\s*import\s+([^;\s]+);/gm)].map(match => match[1]).sort();
const emittedExports = [...emittedWit.matchAll(/^\s*export\s+([^;\s]+);/gm)].map(match => match[1]).sort();
// These exact resource interfaces are the only admitted host capabilities.
// No package-wide wildcard, version remapping, custom provider or TLS adapter.
const allowedImports = selectedInterfaces;
assert.deepEqual(emittedImports.filter(id => id.startsWith('wasi:random/')), runtimeEntropy ? [RANDOM] : []);
for (const imported of emittedImports) assert(allowedImports.includes(imported), `Unexpected emitted host capability: ${imported}`);
assert(emittedImports.includes('wasi:http/types@0.2.10'));
assert.deepEqual(emittedExports, ['wasi:http/incoming-handler@0.2.10']);
const clockDependency = await auditClockDependency(resolve(process.env.NODE_COMPAT_WASM_TOOLS), componentPath, packagingAudit.coreImports, output);
const audit = {
  schema: 1, node: process.version, engine, engineSha256: hash(engineBytes), engineMetadataPath: metadataPath,
  auditedBaseRevision: engineMetadata.auditedBaseRevision ?? engineMetadata.starlingMonkeyRevision,
  componentizeJsRevision: engineMetadata.componentizeJsRevision,
  packagingAudit, componentizerProvenance, interfaceAudit, engineSourceRoot,
  preview1Adapter: { path: preview1AdapterPath, sha256: hash(preview1Adapter), bytes: preview1Adapter.length,
    sourceRevision: engineMetadata.auditedBaseRevision ?? engineMetadata.starlingMonkeyRevision, sourceImportModules: adapterImportModules,
    versionPolicy: 'Repository standard 0.2.0 adapter selected during ComponentizeJS; final no-Preview1 core is wrapped without an adapter and must emit exact 0.2.10',
    usedInFinalWrapping: false },
  componentPath, componentBytes: component.length, componentSha256: hash(component),
  coreExpectations,
  world: 'starling:node-compat-http-test/profile@0.1.0', worldSource, worldFilename, entropyPolicy, selectedInterfaces, builtinManifests: engineMetadata.selectedModuleManifests ?? null,
  bundleImports: bundle.imports, bundledModules: Object.keys(bundle.modules),
  httpEntry, entropyIntegrationFixture: foundationsIntegrationFixture || httpEntry === resolve(here, '../entropy/http.mjs'), foundationsIntegrationFixture, expandedFoundationsFixture, utilFoundationsFixture, foundationOracles,
  applicationBundleSha256: hash(bundle.code), applicationBundleExports: bundle.exports,
  allowedImports, emittedImports, emittedExports, emittedWit,
  executableCoreInterfaces: packagingAudit.coreImportModules, clockDependency,
  corpus: { seed: corpus.seed, strings: corpus.strings.length, bytes: corpus.bytes.length },
  requestStatePolicy: 'Explicit HTTP resource handler; counters report observed JS state retention, not a claim of host instance reuse or request isolation',
  limitations: [`No outgoing HTTP, DNS, socket, filesystem, CLI, environment or clock functions selected; monotonic duration is a type-only dependency; secure entropy ${runtimeEntropy ? 'explicitly selected as wasi:random/random@0.2.10' : 'OFF'}`, 'Component contains oracle corpus; size is not a product/performance comparison', 'HTTP handler success does not establish general Node HTTP or process compatibility'],
};
await writeFile(join(output, 'component-audit.json'), JSON.stringify(audit, null, 2) + '\n');
console.log(JSON.stringify(audit, null, 2));
