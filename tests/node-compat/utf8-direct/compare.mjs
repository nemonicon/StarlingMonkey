// PRIVATE host-only measurement stage. Component construction/correctness is a
// separate build-bench.mjs command; compilation is a separate process/phase.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { cpus, platform, arch, release, totalmem } from 'node:os';
import { spawnSync } from 'node:child_process';
import { auditEngines, auditHost, benchmarkSources, digest, settings } from './build-bench.mjs';

const config = settings();
if (process.argv.includes('--plan')) {
  console.log(JSON.stringify({ state: 'plan-only; no compilation or timing', output: config.output,
    host: config.host, modes: ['compile', 'measure'], defaultSamples: 7, defaultFreshInstances: 3,
    defaultWarmups: 3, defaultCounterbalancedRounds: 2 }, null, 2));
  process.exit(0);
}
assert.equal(process.version, 'v22.14.0'); assert.deepEqual(process.execArgv, []); assert(!process.env.NODE_OPTIONS);
const mode = process.argv[2]; assert(['compile', 'measure'].includes(mode), 'Expected compile or measure');
const manifestPath = join(config.output, 'build-results.json'), manifestBytes = await readFile(manifestPath);
const manifest = JSON.parse(manifestBytes);
assert.equal(manifest.state, 'actual-components-correctness-verified');
assert.deepEqual(manifest.sourceManifest, await benchmarkSources(), 'Benchmark sources changed after component build');
assert.deepEqual(manifest.engineAudit, await auditEngines(manifest.config), 'Engine inputs changed after component build');
assert.deepEqual(manifest.host, await auditHost(config.host));
for (const record of manifest.records) {
  assert.equal(digest(await readFile(record.componentPath)), record.componentSha256, 'Component bytes changed');
  assert.deepEqual(record.emittedImports, []);
  for (const entry of record.bundledFiles) assert.equal(digest(await readFile(entry.path)), entry.sha256);
}
function command(args) {
  const result = spawnSync(config.host, args.map(String), { encoding: 'utf8', timeout: 900000, maxBuffer: 32 * 1024 * 1024 });
  assert.equal(result.status, 0, result.error?.message || result.stderr || result.stdout);
  const report = JSON.parse(result.stdout);
  assert.equal(report.settings.wasmtimeCrate, '42.0.1'); assert.deepEqual(report.settings.guestHostImports, []);
  return report;
}
const compiledPath = join(config.output, 'compile-results.json');
if (mode === 'compile') {
  await writeFile(join(config.output, 'compile-started.json'), JSON.stringify({ createdUtc: new Date().toISOString(),
    buildManifestSha256: digest(manifestBytes), host: manifest.host }, null, 2) + '\n', { flag: 'wx' });
  const records = [];
  for (const record of manifest.records) {
    const precompiled = join(dirname(record.componentPath), 'benchmark.local.cwasm');
    const report = command(['compile', record.componentPath, precompiled]);
    records.push({ arm: record.arm, precompiled, precompiledSha256: digest(await readFile(precompiled)),
      componentSha256: record.componentSha256, componentBytes: record.componentBytes,
      componentGzipBytes: record.componentGzipBytes, report });
  }
  await writeFile(compiledPath, JSON.stringify({ schemaVersion: 1, createdUtc: new Date().toISOString(),
    buildManifestSha256: digest(manifestBytes), host: manifest.host, records }, null, 2) + '\n');
  console.log(JSON.stringify({ output: compiledPath, state: 'compiled separately; no throughput timing' }, null, 2));
  process.exit(0);
}
const compiledBytes = await readFile(compiledPath), compiled = JSON.parse(compiledBytes);
assert.equal(compiled.buildManifestSha256, digest(manifestBytes)); assert.deepEqual(compiled.host, manifest.host);
assert.deepEqual(compiled.records.map(record => record.arm), manifest.records.map(record => record.arm));
for (const record of compiled.records) {
  assert.equal(record.precompiledSha256, digest(await readFile(record.precompiled)), 'Only local hash-verified precompiled components are admitted');
  assert.equal(record.componentSha256, manifest.records.find(entry => entry.arm === record.arm).componentSha256);
}
const samples = Number(process.env.NODE_COMPAT_BENCH_SAMPLES ?? 7);
const fresh = Number(process.env.NODE_COMPAT_BENCH_INSTANCES ?? 3);
const warmups = Number(process.env.NODE_COMPAT_BENCH_WARMUPS ?? 3);
const rounds = Number(process.env.NODE_COMPAT_UTF8_BENCH_ROUNDS ?? 2);
for (const value of [samples, fresh, warmups]) assert(Number.isInteger(value) && value > 0 && value < 100);
assert(Number.isInteger(rounds) && rounds > 0 && rounds < 10 && rounds % 2 === 0,
  'Use an even number of rounds so each scenario has both arm orders');
const operations = process.env.NODE_COMPAT_BENCH_OPERATIONS?.split(',');
const sizes = process.env.NODE_COMPAT_BENCH_SIZES?.split(',').map(Number);
if (operations) for (const operation of operations) assert(manifest.scenarios.some(s => s.operation === operation), `Unknown operation ${operation}`);
if (sizes) for (const size of sizes) assert(manifest.scenarios.some(s => s.size === size), `Unknown size ${size}`);
const scenarios = manifest.scenarios.filter(s => (!operations || operations.includes(s.operation)) && (!sizes || sizes.includes(s.size)));
assert(scenarios.length > 0);
await writeFile(join(config.output, 'measurement-started.json'), JSON.stringify({ createdUtc: new Date().toISOString(),
  buildManifestSha256: digest(manifestBytes), compileManifestSha256: digest(compiledBytes),
  samples, fresh, warmups, rounds, scenarios }, null, 2) + '\n', { flag: 'wx' });
function percentile(values, fraction) {
  assert(values.length && values.every(Number.isFinite));
  const sorted = [...values].sort((a, b) => a - b), index = (sorted.length - 1) * fraction;
  return sorted[Math.floor(index)] + (sorted[Math.ceil(index)] - sorted[Math.floor(index)]) * (index - Math.floor(index));
}
function summary(reports, scenario) {
  const instances = reports.flatMap(report => report.instances), timings = instances.flatMap(instance => instance.batchNs);
  const median = percentile(timings, .5);
  const rss = instances.map(instance => instance.peakProcessRssBytes).filter(Number.isFinite);
  return { batchNs: { min: Math.min(...timings), p25: percentile(timings, .25), median,
    p75: percentile(timings, .75), max: Math.max(...timings), count: timings.length },
    instanceMedianBatchNs: instances.map(instance => percentile(instance.batchNs, .5)),
    nanosecondsPerOperation: median / scenario.iterations,
    inputMiBPerSecond: scenario.processedBytesPerIteration * scenario.iterations / (median / 1e9) / 1048576,
    instantiateNsMedian: percentile(instances.map(instance => instance.instantiateNs), .5),
    setupNsMedian: percentile(instances.map(instance => instance.setupNs), .5),
    firstBatchNsMedian: percentile(instances.map(instance => instance.firstBatchNs), .5),
    peakProcessRssBytes: rss.length ? Math.max(...rss) : null,
    largestLinearMemoryRequestBytes: Math.max(...instances.map(instance => instance.largestLinearMemoryRequestBytes)),
    freshInstances: instances.length, measurementProcesses: reports.length };
}
const records = [], order = [];
for (let round = 0; round < rounds; ++round) for (const [index, scenario] of scenarios.entries()) {
  // Pair native arms directly. The second round reverses each scenario's
  // order; optional Jco pairs are separate diagnostics, never primary arms.
  const kinds = manifest.adapter ? ['native', 'jco-js'] : ['native'];
  if (round % 2) kinds.reverse();
  for (const implementation of kinds) {
    const pair = ['control', 'candidate'].map(engine => `${engine}-${implementation}`);
    if ((round + index) % 2) pair.reverse();
    for (const arm of pair) {
      const compiledArm = compiled.records.find(entry => entry.arm === arm); assert(compiledArm);
      console.error(`round ${round + 1}: ${arm} ${scenario.operation}/${scenario.size} x${scenario.iterations}`);
      order.push({ round: round + 1, operation: scenario.operation, size: scenario.size, arm });
      const report = command(['measure', compiledArm.precompiled, scenario.operation, scenario.size, scenario.iterations,
        samples, fresh, warmups, scenario.expectedSetupChecksum, scenario.expectedRunChecksum]);
      assert.equal(report.instances.length, fresh);
      for (const instance of report.instances) {
        assert.equal(instance.setupChecksum, scenario.expectedSetupChecksum);
        assert.equal(instance.runChecksum, scenario.expectedRunChecksum);
        assert.equal(instance.batchNs.length, samples); assert.equal(instance.linearMemoryGrowFailures, 0);
        assert(instance.batchNs.every(value => Number.isFinite(value) && value > 0));
      }
      records.push({ arm, implementation, round: round + 1, ...scenario, report, summary: summary([report], scenario) });
      await writeFile(join(config.output, 'records.partial.json'), JSON.stringify({ order, records }, null, 2) + '\n');
    }
  }
}
const aggregate = [];
for (const scenario of scenarios) for (const arm of manifest.records.map(record => record.arm)) {
  const selected = records.filter(record => record.arm === arm && record.operation === scenario.operation && record.size === scenario.size);
  assert.equal(selected.length, rounds);
  aggregate.push({ arm, ...scenario, summary: summary(selected.map(record => record.report), scenario) });
}
const comparisons = [];
for (const scenario of scenarios) for (const implementation of manifest.adapter ? ['native', 'jco-js'] : ['native']) {
  const find = engine => aggregate.find(record => record.arm === `${engine}-${implementation}` && record.operation === scenario.operation && record.size === scenario.size).summary;
  const control = find('control'), candidate = find('candidate');
  comparisons.push({ operation: scenario.operation, size: scenario.size, iterations: scenario.iterations, implementation,
    comparisonRole: implementation === 'native' ? 'primary native codec before/after' : 'Jco adapter diagnostic on each engine',
    candidateOverControlThroughput: control.batchNs.median / candidate.batchNs.median,
    controlInputMiBPerSecond: control.inputMiBPerSecond, candidateInputMiBPerSecond: candidate.inputMiBPerSecond,
    controlPeakProcessRssBytes: control.peakProcessRssBytes, candidatePeakProcessRssBytes: candidate.peakProcessRssBytes,
    controlLargestLinearMemoryRequestBytes: control.largestLinearMemoryRequestBytes,
    candidateLargestLinearMemoryRequestBytes: candidate.largestLinearMemoryRequestBytes,
    roundRatios: Array.from({ length: rounds }, (_, round) => {
      const arm = engine => records.find(record => record.round === round + 1 && record.arm === `${engine}-${implementation}` && record.operation === scenario.operation && record.size === scenario.size).summary;
      return { round: round + 1, candidateOverControlThroughput: arm('control').batchNs.median / arm('candidate').batchNs.median };
    }) });
}
const adapterComparisons = [];
if (manifest.adapter) for (const scenario of scenarios) for (const engine of ['control', 'candidate']) {
  const find = implementation => aggregate.find(record => record.arm === `${engine}-${implementation}` && record.operation === scenario.operation && record.size === scenario.size).summary;
  const native = find('native'), javascript = find('jco-js');
  adapterComparisons.push({ engine, operation: scenario.operation, size: scenario.size,
    comparisonRole: 'Contextual implementation diagnostic within one exact engine; not the native codec before/after result',
    nativeOverJavascriptThroughput: javascript.batchNs.median / native.batchNs.median,
    nativeInputMiBPerSecond: native.inputMiBPerSecond, javascriptInputMiBPerSecond: javascript.inputMiBPerSecond,
    nativePeakProcessRssBytes: native.peakProcessRssBytes, javascriptPeakProcessRssBytes: javascript.peakProcessRssBytes,
    nativeLargestLinearMemoryRequestBytes: native.largestLinearMemoryRequestBytes,
    javascriptLargestLinearMemoryRequestBytes: javascript.largestLinearMemoryRequestBytes });
}
const result = { schemaVersion: 1, state: 'completed-private-local-measurement', createdUtc: new Date().toISOString(),
  node: process.version, machine: { platform: platform(), arch: arch(), release: release(), cpuModel: cpus()[0]?.model,
    logicalCpus: cpus().length, totalMemoryBytes: totalmem() }, host: manifest.host,
  sourceManifest: manifest.sourceManifest, engineAudit: manifest.engineAudit, componentizerProvenance: manifest.componentizerProvenance,
  buildManifestPath: manifestPath, buildManifestSha256: digest(manifestBytes),
  compileManifestPath: compiledPath, compileManifestSha256: digest(compiledBytes),
  compilation: compiled.records, protocol: manifest.protocol, scenarios,
  samplesPerInstance: samples, freshInstancesPerScenarioPerRound: fresh, warmupBatches: warmups, rounds,
  armOrder: 'Each scenario counterbalanced across an even number of rounds; exact order retained below',
  order, records, aggregate, comparisons, adapterComparisons,
  limitations: [
    'Private microbenchmark on one local machine; no full-application, full-Buffer, uniform or statistically significant performance claim.',
    'The same-project engines differ only in encoder CPP in their source manifests; the same inactive private header exists in both. Linked OpenSSL archive bytes match exactly, but this is not a proof that every other linked instruction is byte-identical.',
    'Seven batches within an instance are correlated. Fresh instances share one deserialized component inside each measurement process; rounds use separate processes.',
    'Packaging and native host compilation run separately; operation timing includes the unchanged O(1) observable fingerprint and guest calls.',
    'RSS is whole-process high-water including Wasmtime/runtime/code/allocator retention; later instance peaks are cumulative within a process, not isolated guest live heaps.',
    'Largest linear-memory request is the ResourceLimiter maximum desired bytes for one memory, not summed memory, committed pages, allocation count, heap size or a leak proof.',
    'UTF-8 inputs are ASCII at four fixed sizes. General Unicode correctness has separate shared codec tests.',
    'Primary UTF8 encode reads visible result bytes/length, not .buffer; small direct Uint8Array results can defer ArrayBuffer materialization. Applications inspecting .buffer can have a different cost.',
    'Optional Jco arms bundle the actual JavaScript adapter in an already profile-enabled engine; their size delta is adapter overhead, not minimal profile-disabled deployment savings.',
    'No guest clocks or host capabilities are imported. Host Instant reports elapsed time and remains subject to local system load and scheduling.',
  ] };
const path = join(config.output, 'results.json');
await writeFile(path, JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ output: path, comparisons }, null, 2));
