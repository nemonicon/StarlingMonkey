// Matched release experiment: original facade versus trusted fresh-output
// tagging. BOTH engines include the identical boxed-number export ABI fix.
// Run `compare.mjs build`, wait for an idle machine, then `compare.mjs measure`.
import assert from 'node:assert/strict';
import { Buffer as NodeBuffer } from 'node:buffer';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { gzipSync } from 'node:zlib';
import { spawnSync } from 'node:child_process';
import { cpus, platform, arch, release, totalmem } from 'node:os';
import { loadToolchain } from '../toolchain.mjs';
import { createWorkload, operations, sizes, iterationsFor } from '../bench/workload.mjs';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, '../../..');
const output = resolve(process.env.NODE_COMPAT_IMPROVEMENT_OUTPUT ?? '/tmp/starling-node-compat/improvement');
const baselineSource = resolve(process.env.NODE_COMPAT_BASELINE_SOURCE ?? '/tmp/starling-node-compat/optimization-baseline-source');
const controlEngine = resolve(process.env.NODE_COMPAT_CONTROL_ENGINE ?? '/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-control.wasm');
const candidateEngine = resolve(process.env.NODE_COMPAT_CANDIDATE_ENGINE ?? '/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.candidate.release.wasm');
const host = resolve(process.env.NODE_COMPAT_BENCH_HOST ?? '/tmp/starling-node-compat/bench-host-target/release/node-profile-bench-host');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const manifestPath = join(output, 'improvement-build.json');
const changedPaths = ['builtins/node-compat/buffer-facade.mjs', 'builtins/node-compat/factories.generated.h'];

async function build() {
  await mkdir(output, { recursive: true });
  await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
  const { directory: toolchain, require, rolldown } = await loadToolchain();
  const { componentize } = await import(pathToFileURL(join(toolchain, 'node_modules/@bytecodealliance/componentize-js/src/componentize.js')));
  const { componentWit, transpile } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
  try { await symlink(join(toolchain, 'node_modules'), join(output, 'node_modules'), 'dir'); }
  catch (error) { if (error.code !== 'EEXIST') throw error; }
  const engines = [];
  for (const [arm, engine] of [['control', controlEngine], ['candidate', candidateEngine]]) {
    const metadata = JSON.parse(await readFile(engine + '.build.json'));
    assert.equal(hash(await readFile(engine)), metadata.engineSha256);
    assert.equal(metadata.abiFixEnabled, true);
    assert.equal(metadata.profileEnabled, true);
    assert.equal(metadata.gcStress, false);
    assert.equal(metadata.debuggerEnabled, false);
    assert(metadata.componentizeJsPatches.every(p => p.applied));
    for (const entry of metadata.sourceManifest) {
      const source = arm === 'control' && changedPaths.includes(entry.path)
        ? join(baselineSource, 'node-compat', entry.path.split('/').at(-1))
        : join(repository, entry.path);
      assert.equal(hash(await readFile(source)), entry.sha256, `stale ${arm} engine: ${entry.path}`);
    }
    engines.push({ arm, engine, metadata });
  }
  assert.equal(engines[0].metadata.engineSha256, '6daf1f03438aad3a14124b2dc09f95f09b91eac285233c2345cbd1a24b302748', 'immutable ABI-fixed control');
  assert.deepEqual(engines[0].metadata.componentizeSourceManifest, engines[1].metadata.componentizeSourceManifest);
  for (const key of ['componentizeJsRevision', 'hostApi', 'archivePins', 'buildTools', 'wptSupportEnabled']) {
    assert.deepEqual(engines[0].metadata[key], engines[1].metadata[key], `unmatched build setting: ${key}`);
  }
  const patchKey = p => ({ name: p.name, sha256: p.sha256, baseRevision: p.baseRevision, applied: p.applied });
  assert.deepEqual(engines[0].metadata.componentizeJsPatches.map(patchKey), engines[1].metadata.componentizeJsPatches.map(patchKey));
  const before = new Map(engines[0].metadata.sourceManifest.map(e => [e.path, e.sha256]));
  assert.deepEqual(engines[1].metadata.sourceManifest.filter(e => before.get(e.path) !== e.sha256).map(e => e.path).sort(), [...changedPaths].sort());

  const entry = join(here, 'comparison.virtual-entry.mjs');
  const entrySource = `import {Buffer} from 'node:buffer';
import {createWorkload} from '../bench/workload.mjs';
if(globalThis.Buffer!==Buffer || Buffer.isEncoding('base64')) throw new Error('wrong native Buffer');
const workload=createWorkload(Buffer);export const setup=workload.setup;export const run=workload.run;`;
  const builder = await rolldown({ input: entry, platform: 'neutral', treeshake: true, transform: { target: 'es2016' }, plugins: [{
    name: 'matched-native-buffer-comparison',
    resolveId(id) { if (id === entry) return id; if (id === 'node:buffer') return { id, external: true }; },
    load(id) { if (id === entry) return entrySource; },
  }] });
  let bundle;
  try { const generated = await builder.generate({ format: 'esm', codeSplitting: false }); assert.equal(generated.output.length, 1); bundle = generated.output[0]; }
  finally { await builder.close(); }
  assert.deepEqual(bundle.imports, ['node:buffer']);
  const scenarios = [];
  const oracle = createWorkload(NodeBuffer);
  for (const operation of operations) for (const size of sizes) {
    const iterations = iterationsFor(size);
    scenarios.push({ operation, size, iterations, processedBytesPerIteration: size,
      expectedSetupChecksum: oracle.setup(operation, size) >>> 0, expectedRunChecksum: oracle.run(iterations) >>> 0 });
  }
  const records = [];
  const witWorld = await readFile(join(here, '../bench/benchmark.wit'), 'utf8');
  for (const { arm, engine, metadata } of engines) {
    const directory = join(output, arm);
    await mkdir(directory, { recursive: true });
    await writeFile(join(directory, 'application.bundle.mjs'), bundle.code);
    const { component } = await componentize(bundle.code, { engine, witWorld, worldName: 'benchmark',
      disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'] });
    const componentPath = join(directory, 'benchmark.component.wasm');
    await writeFile(componentPath, component);
    const emittedWit = await componentWit(component);
    assert.deepEqual(emittedWit.split('\n').filter(line => /^\s*import /.test(line)), []);
    await writeFile(join(directory, 'emitted.wit'), emittedWit);
    const { files } = await transpile(component, { name: 'benchmark' });
    for (const [name, value] of Object.entries(files)) { await mkdir(dirname(join(directory, name)), { recursive: true }); await writeFile(join(directory, name), value); }
    const instance = await import(pathToFileURL(join(directory, 'benchmark.js')));
    for (const scenario of scenarios) {
      assert.equal(instance.setup(scenario.operation, scenario.size) >>> 0, scenario.expectedSetupChecksum, `${arm} setup`);
      assert.equal(instance.run(scenario.iterations) >>> 0, scenario.expectedRunChecksum, `${arm} run`);
    }
    records.push({ arm, engine, engineMetadata: metadata, componentPath, componentSha256: hash(component),
      componentBytes: component.length, componentGzipBytes: gzipSync(component).length, emittedWit, wasmImports: [],
      bundleSha256: hash(bundle.code), correctness: 'All 20 setup/full-byte and run/fingerprint checksums match Node22.14.0 via Jco' });
  }
  const manifest = { schemaVersion: 1, createdUtc: new Date().toISOString(), node: process.version,
    records, scenarios, changedPaths, sourceManifest: await sourceManifest(),
    protocol: { engines: 'Identical ComponentizeJS guest ABI patch, C++ kernels, build options and toolchain. Only facade and its generated header differ.',
      bundler: { name: 'Rolldown', version: '1.2.16', target: 'es2016', treeshake: true, platform: 'neutral' },
      checksumTransport: 'Original benchmark s32 bit carrier retained in both arms; direct u32 regression is independently tested.',
      scope: 'Native facade before/after, ASCII UTF-8 and valid lowercase hex. Not a rerun of the Jco JavaScript comparison.',
      byteDefinition: 'Logical payload bytes, not ASCII source characters for hex decode',
      baselineSource, capabilityImports: [] } };
  await writeFile(manifestPath, JSON.stringify(manifest, null, 2) + '\n');
  console.log(JSON.stringify({ manifestPath, records: records.map(({ arm, componentSha256, componentBytes, correctness }) => ({ arm, componentSha256, componentBytes, correctness })) }, null, 2));
}

async function sourceManifest() {
  const paths = ['optimization/compare.mjs', 'bench/workload.mjs', 'bench/benchmark.wit', 'bench/host/Cargo.toml', 'bench/host/Cargo.lock', 'bench/host/src/main.rs'];
  return Promise.all(paths.map(async path => ({ path, sha256: hash(await readFile(join(here, '..', path))) })));
}
function percentile(values, fraction) {
  const sorted = [...values].sort((a, b) => a - b), index = (sorted.length - 1) * fraction;
  return sorted[Math.floor(index)] + (sorted[Math.ceil(index)] - sorted[Math.floor(index)]) * (index - Math.floor(index));
}
async function measure() {
  const manifest = JSON.parse(await readFile(manifestPath));
  assert.deepEqual(manifest.sourceManifest, await sourceManifest(), 'measurement sources changed after component build');
  const samples = 7, fresh = 3, warmups = 3;
  function command(args) {
    const result = spawnSync(host, args.map(String), { encoding: 'utf8', timeout: 600000, maxBuffer: 32 * 1024 * 1024 });
    assert.equal(result.status, 0, result.error?.message || result.stderr || result.stdout);
    const report = JSON.parse(result.stdout);
    assert.equal(report.settings.wasmtimeCrate, '42.0.1');
    assert.deepEqual(report.settings.guestHostImports, []);
    return report;
  }
  const compilation = [];
  for (const arm of manifest.records) {
    assert.equal(hash(await readFile(arm.componentPath)), arm.componentSha256);
    const precompiled = join(dirname(arm.componentPath), 'benchmark.local.cwasm');
    const report = command(['compile', arm.componentPath, precompiled]);
    compilation.push({ arm: arm.arm, componentBytes: arm.componentBytes, componentGzipBytes: arm.componentGzipBytes,
      componentSha256: arm.componentSha256, precompiled, precompiledSha256: hash(await readFile(precompiled)), report });
  }
  const records = [];
  for (const [index, scenario] of manifest.scenarios.entries()) {
    for (const arm of index % 2 ? [...compilation].reverse() : compilation) {
      console.error(`${arm.arm} ${scenario.operation}/${scenario.size}`);
      const report = command(['measure', arm.precompiled, scenario.operation, scenario.size, scenario.iterations,
        samples, fresh, warmups, scenario.expectedSetupChecksum, scenario.expectedRunChecksum]);
      assert.equal(report.instances.length, fresh);
      for (const instance of report.instances) {
        assert.equal(instance.setupChecksum, scenario.expectedSetupChecksum);
        assert.equal(instance.runChecksum, scenario.expectedRunChecksum);
        assert.equal(instance.batchNs.length, samples);
        assert.equal(instance.linearMemoryGrowFailures, 0);
      }
      const timings = report.instances.flatMap(i => i.batchNs), median = percentile(timings, 0.5);
      records.push({ arm: arm.arm, ...scenario, report, summary: {
        batchNs: { min: Math.min(...timings), p25: percentile(timings, .25), median, p75: percentile(timings, .75), max: Math.max(...timings), count: timings.length },
        instanceMedianBatchNs: report.instances.map(i => percentile(i.batchNs, .5)),
        payloadMiBPerSecond: scenario.processedBytesPerIteration * scenario.iterations / (median / 1e9) / 1048576,
        peakProcessRssBytes: Math.max(...report.instances.map(i => i.peakProcessRssBytes ?? 0)),
        largestLinearMemoryRequestBytes: Math.max(...report.instances.map(i => i.largestLinearMemoryRequestBytes)),
      } });
      await writeFile(join(output, 'improvement-records.partial.json'), JSON.stringify({ compilation, records }, null, 2) + '\n');
    }
  }
  const comparisons = manifest.scenarios.map(scenario => {
    const find = arm => records.find(r => r.arm === arm && r.operation === scenario.operation && r.size === scenario.size).summary;
    const control = find('control'), candidate = find('candidate');
    return { operation: scenario.operation, size: scenario.size, iterations: scenario.iterations,
      controlPayloadMiBPerSecond: control.payloadMiBPerSecond, candidatePayloadMiBPerSecond: candidate.payloadMiBPerSecond,
      candidateOverControlThroughput: control.batchNs.median / candidate.batchNs.median,
      controlPeakProcessRssBytes: control.peakProcessRssBytes, candidatePeakProcessRssBytes: candidate.peakProcessRssBytes,
      controlLargestLinearMemoryRequestBytes: control.largestLinearMemoryRequestBytes,
      candidateLargestLinearMemoryRequestBytes: candidate.largestLinearMemoryRequestBytes };
  });
  const results = { schemaVersion: 1, createdUtc: new Date().toISOString(), node: process.version,
    machine: { platform: platform(), arch: arch(), release: release(), cpuModel: cpus()[0]?.model, logicalCpus: cpus().length, totalMemoryBytes: totalmem() },
    host, hostSha256: hash(await readFile(host)), sourceManifest: manifest.sourceManifest, protocol: manifest.protocol,
    engines: manifest.records.map(({ arm, engineMetadata }) => ({ arm, engineSha256: engineMetadata.engineSha256, componentizeJsPatches: engineMetadata.componentizeJsPatches })),
    buildManifestSha256: hash(await readFile(manifestPath)), samplesPerInstance: samples, freshInstancesPerScenario: fresh, warmupBatches: warmups,
    armOrder: 'control first on even scenario index, candidate first on odd', compilation, comparisons, records,
    limitations: ['One Apple M2 machine run, no whole-application or Weval-enabled claim',
      'Seven measured batches within each instance are correlated; three fresh instances per arm/scenario',
      'Host timings include result fingerprint access; string access can materialize ropes',
      'RSS is process high-water including Wasmtime/runtime/allocator retention; later instance peaks are cumulative',
      'Largest linear-memory growth request is not total heap, resident memory, allocation count or evidence of a leak',
      'Both arms are native; do not combine ratios with historical JavaScript-adapter measurements from a separate run'] };
  await writeFile(join(output, 'improvement-results.json'), JSON.stringify(results, null, 2) + '\n');
  console.log(JSON.stringify({ output: join(output, 'improvement-results.json'), comparisons }, null, 2));
}
if (process.argv[2] === 'build') await build();
else if (process.argv[2] === 'measure') await measure();
else throw new Error('Expected build or measure');
