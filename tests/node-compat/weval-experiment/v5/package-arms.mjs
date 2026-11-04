// Frozen-v5 ordinary Release Weval A/B build/correctness. No throughput measurement here.
// Derived from the hash-pinned corrected-clock A/B builder; both arms select
// one explicit custom Weval engine/cache/tool and real Jco JavaScript adapter.
import assert from 'node:assert/strict';
import { Buffer as NodeBuffer } from 'node:buffer';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { gzipSync } from 'node:zlib';
import { performance } from 'node:perf_hooks';
import {loadWevalContext} from './load-context.mjs';
import { createWorkload, operations, sizes, iterationsFor } from '../../bench-clock-v2/workload.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, '../../../..');
const output = resolve(process.env.NODE_COMPAT_BENCH_OUTPUT ?? '/tmp/starling-node-compat/weval-experiment/v5-components');
assert(process.env.NODE_COMPAT_ENGINE, 'Explicit audited current engine required');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const context=await loadWevalContext();
const toolchainInfo=context.toolchain;
const { directory: toolchain, require, rolldown } = toolchainInfo;
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const engineBytes = await readFile(engine);
const engineMetadata = JSON.parse(await readFile(engine + '.build.json'));
const pins=JSON.parse(await readFile(join(here,'pins.json')));
const historicalPins=JSON.parse(await readFile(join(here,'../pins.json')));
assert.equal(engineMetadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
assert.equal(engineMetadata.observedCMakeOptions.WEVAL,'ON');
assert.equal(engineMetadata.observedCMakeOptions.USE_WASM_OPT,'OFF');
assert.equal(engineMetadata.strictInitialization,true);
assert(engineMetadata.wevalExperiment,'Require a generated cache bound to this custom engine');
const weval=engineMetadata.wevalExperiment;
const sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT??weval.sourceRoot);
assert.equal(weval.cache.generatedFromRawEngineSha256,engineMetadata.engineSha256);
assert.equal(hash(await readFile(weval.cache.path)),weval.cache.sha256);
for(const tool of weval.tools)assert.equal(hash(await readFile(tool.path)),pins.cachedHostTools[tool.name].sha256,tool.name);
const aotOptions=context.provenance.options;
assert.equal(aotOptions.enableAot,true);
for(const path of ['tests/node-compat/bench-clock-v2/workload.mjs','tests/node-compat/bench-clock-v2/benchmark.wit'])assert.equal(hash(await readFile(join(repository,path))),historicalPins.sourceFiles.find(entry=>entry.path===path).sha256,path);
assert.equal(hash(engineBytes), engineMetadata.engineSha256);
assert.equal(engineMetadata.profileEnabled, true);
assert.equal(engineMetadata.gcStress, false, 'Benchmark must use release, never GC stress');
assert.equal(engineMetadata.debuggerEnabled, false);
for (const entry of engineMetadata.sourceManifest) assert.equal(hash(await readFile(join(sourceRoot, entry.path))), entry.sha256, `stale native engine: ${entry.path}`);
const jcoDirectory = join(toolchain, 'node_modules/@bytecodealliance/jco');
const adapterPath = join(jcoDirectory, 'dist/node-builtins/buffer.js');
const { createBufferBuiltin } = await import(pathToFileURL(adapterPath));
const componentize=context.componentize,componentizerProvenance=context.provenance.packaging;
assert.equal(componentizerProvenance.selection, 'patched-import-i32-clock-v2');
assert.equal(engineMetadata.entropyPolicy, 'off');
const preview2Adapter = join(sourceRoot, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
const { componentWit, transpile } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
const unenvPackage = JSON.parse(await readFile(require.resolve('unenv/package.json')));
assert.equal(unenvPackage.version, '2.0.0-rc.24');
const unenvBufferPath = require.resolve('unenv/node/internal/buffer/buffer');
const unenvBufferBytes = await readFile(unenvBufferPath);
const adapter = createBufferBuiltin({ options: {} });
const adapterVirtualId = adapter.resolveId('node:buffer');
const coreVirtualId = '\0jco-node-builtin:unenv-buffer-core';
const adapterVirtualSource = adapter.load(adapterVirtualId);
const coreVirtualSource = adapter.load(coreVirtualId);
assert(coreVirtualSource.includes('globalThis.Buffer = Buffer;'));
await mkdir(output, { recursive: true });
await writeFile(join(output,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),engine})+'\n',{flag:'wx'});
const driverPaths=[fileURLToPath(import.meta.url),join(here,'load-context.mjs'),join(here,'pins.json'),join(repository,'tests/node-compat/bench-clock-v2/workload.mjs'),join(repository,'tests/node-compat/bench-clock-v2/benchmark.wit')];
const driverSources=await Promise.all(driverPaths.map(async path=>({path,sha256:hash(await readFile(path))})));
await mkdir(join(output,'source'),{recursive:true});
for(const entry of driverSources)await writeFile(join(output,'source',entry.path.split('/').pop()),await readFile(entry.path));
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain, 'node_modules'), join(output, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
await writeFile(join(output, 'jco-buffer.generated-adapter.mjs'), adapterVirtualSource);
await writeFile(join(output, 'jco-buffer.generated-core.mjs'), coreVirtualSource);

const scenarios = [];
const oracle = createWorkload(NodeBuffer);
for (const operation of operations) for (const size of sizes) {
  const iterations = iterationsFor(size);
  scenarios.push({ operation, size, iterations, processedBytesPerIteration: size,
    expectedSetupChecksum: oracle.setup(operation, size) >>> 0, expectedRunChecksum: oracle.run(iterations) >>> 0 });
}
const records = [];
for (const arm of ['native', 'jco-js']) {
  const entry = join(here, `${arm}.virtual-entry.mjs`);
  const entrySource = `import { Buffer as SelectedBuffer } from 'benchmark:buffer';
import { Buffer as NativeRegistryBuffer } from 'benchmark:native-registry';
import { createWorkload } from '../../bench-clock-v2/workload.mjs';
const native = SelectedBuffer === NativeRegistryBuffer;
if (native !== ${arm === 'native'}) throw new Error('Buffer implementation contamination');
if (globalThis.Buffer !== SelectedBuffer) throw new Error('global Buffer does not match selected implementation');
if (SelectedBuffer.isEncoding('base64') !== ${arm === 'jco-js'}) throw new Error('wrong encoding implementation');
const workload = createWorkload(SelectedBuffer);
export const setup = workload.setup;
export const run = workload.run;
`;
  const modules = new Set();
  const bundle = await rolldown({ input: entry, platform: 'neutral', treeshake: true,
    transform: { target: 'es2016' }, plugins: [{
    name: 'buffer-ab-benchmark',
    resolveId(id) {
      if (id === entry) return id;
      if (id === 'benchmark:native-registry') return { id: 'node:buffer', external: true };
      if (id === 'benchmark:buffer') return arm === 'native' ? { id: 'node:buffer', external: true } : adapterVirtualId;
      if (arm === 'jco-js') return adapter.resolveId(id);
      return null;
    },
    load(id) { if (id === entry) return entrySource; if (arm === 'jco-js') return adapter.load(id); return null; },
    moduleParsed(info) { modules.add(info.id); },
  }] });
  let chunk;
  try { const generated = await bundle.generate({ format: 'esm', codeSplitting: false }); assert.equal(generated.output.length, 1); chunk = generated.output[0]; }
  finally { await bundle.close(); }
  assert.deepEqual(chunk.imports, ['node:buffer']);
  assert(!chunk.code.includes('reference-kernel'));
  if (arm === 'native') assert(!chunk.code.includes('ERR_JCO_UNSUPPORTED_DEPRECATED_NODE_API'));
  else {
    assert(chunk.code.includes('ERR_JCO_UNSUPPORTED_DEPRECATED_NODE_API'));
    assert([...modules].some(id => id === unenvBufferPath));
  }
  const directory = join(output, arm);
  await mkdir(directory, { recursive: true });
  await writeFile(join(directory, 'application.bundle.mjs'), chunk.code);
  const buildStart = performance.now();
  const { component, interfaceAudit } = await componentize(chunk.code, { ...aotOptions, engine, preview2Adapter, selectedInterfaces: [],
    witWorld: await readFile(join(repository, 'tests/node-compat/bench-clock-v2/benchmark.wit'), 'utf8'), worldName: 'benchmark',
    disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'] });
  const componentizeMs = performance.now() - buildStart;
  const componentPath = join(directory, 'benchmark.component.wasm');
  await writeFile(componentPath, component);
  const wit = await componentWit(component);
  await writeFile(join(directory, 'emitted.wit'), wit);
  assert.deepEqual(wit.split('\n').filter(line => /^\s*import /.test(line)), [], 'A/B components must have zero host imports');
  const { files } = await transpile(component, { name: 'benchmark' });
  for (const [name, value] of Object.entries(files)) { await mkdir(dirname(join(directory, name)), { recursive: true }); await writeFile(join(directory, name), value); }
  const instance = await import(pathToFileURL(join(directory, 'benchmark.js')));
  for (const scenario of scenarios) {
    assert.equal(instance.setup(scenario.operation, scenario.size) >>> 0, scenario.expectedSetupChecksum, `${arm} ${scenario.operation}/${scenario.size} setup checksum`);
    assert.equal(instance.run(scenario.iterations) >>> 0, scenario.expectedRunChecksum, `${arm} ${scenario.operation}/${scenario.size} loop checksum`);
  }
  records.push({ arm, componentPath, componentBytes: component.length, componentGzipBytes: gzipSync(component).length,
    componentSha256: hash(component), componentizeMs, interfaceAudit, wasmImports: [], emittedWit: wit,
    bundleImports: chunk.imports, bundledModules: [...modules].sort(), bundleSha256: hash(chunk.code),
    correctness: { scenarios: scenarios.length, setupFullChecksums: 'Node22.14.0 matched', runChecksums: 'Node22.14.0 matched', nativeContaminationGate: 'passed at snapshot initialization' } });
}
await context.verify();
for(const entry of driverSources)assert.equal(hash(await readFile(entry.path)),entry.sha256,'A/B source changed during packaging');
assert.equal(hash(await readFile(weval.cache.path)),weval.cache.sha256,'Readonly generic IC cache changed during packaging');
for(const tool of weval.tools)assert.equal(hash(await readFile(tool.path)),tool.sha256,tool.name);
const manifest = {
  schemaVersion: 1, node: process.version, createdUtc: new Date().toISOString(), engine, engineSha256: hash(engineBytes),
  engineMetadata, sourceRoot, componentizerProvenance,driverSources,driversCapturedBeforeAndVerifiedAfter:true,
  wevalExperiment: { cache:weval.cache,tools:weval.tools,options:aotOptions,cacheUnchangedAfterBothArms:true,workloadSha256:hash(await readFile(join(repository,'tests/node-compat/bench-clock-v2/workload.mjs'))),builderSha256:hash(await readFile(fileURLToPath(import.meta.url))),scope:'Same frozen-v5 Weval-capable Release engine and generic read-only cache in BOTH arms. App-specific AOT transforms happen separately. This builder reports correctness/packaging/size; it does not measure deployed throughput.' }, preview2Adapter: {path:preview2Adapter, sha256:hash(await readFile(preview2Adapter))}, operations, scenarios, records,
  adapter: { package: '@bytecodealliance/jco', version: '1.40.0', adapterPath, adapterSha256: hash(await readFile(adapterPath)),
    generatedAdapterSha256: hash(adapterVirtualSource), generatedCoreSha256: hash(coreVirtualSource),
    unenvVersion: unenvPackage.version, unenvBufferPath, unenvBufferSha256: hash(unenvBufferBytes),
    sourceReference: 'https://github.com/bytecodealliance/jco/blob/jco-v1.40.0/packages/jco/src/node-builtins/buffer.ts' },
  protocol: { setup: 'Payload creation + one full FNV-1a correctness hash outside throughput timing',
    bundler: { name: 'Rolldown', version: '1.2.16', platform: 'neutral', target: 'es2016', treeshake: true, minify: false },
    run: 'Fixed operation loop; per-result O(1) fingerprint consumed into checksum; host timing only',
    checksumTransport: 's32 preserves all32 checksum bits; host reinterprets as unsigned. Native scalar-export, imported-I32 and signed-BigInt corrections are separately validated; this workload keeps its historical checksum ABI.',
    byteDefinition: 'Input payload bytes; hex string is twice that many ASCII code units',
    allocationPolicy: 'Same Weval-capable Release engine, IC cache and packaging options; profile installed in BOTH arms; JS arm additionally bundles actual Jco adapter',
    scope: 'ASCII UTF-8 and valid lowercase hex; bounded supported domain. No claimed full Buffer or whole-application speedup' },
};
await writeFile(join(output, 'build-results.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify({ output, engineSha256: manifest.engineSha256, records: records.map(({ arm, componentPath, componentBytes, correctness }) => ({ arm, componentPath, componentBytes, correctness })) }, null, 2));
