// Stock Wasmtime host benchmark driver. Every throughput process compiles NO
// guest code and keeps one instance alive across each timed operation batch.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { cpus, platform, arch, release, totalmem } from 'node:os';
import { spawnSync } from 'node:child_process';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(process.env.NODE_COMPAT_BENCH_OUTPUT ?? '/tmp/starling-node-compat/bench-output');
const host = resolve(process.env.NODE_COMPAT_BENCH_HOST ?? '/tmp/starling-node-compat/bench-host-target/release/node-profile-bench-host');
const manifest = JSON.parse(await readFile(join(output, 'build-results.json')));
const samples = Number(process.env.NODE_COMPAT_BENCH_SAMPLES ?? 7);
const fresh = Number(process.env.NODE_COMPAT_BENCH_INSTANCES ?? 3);
const warmups = Number(process.env.NODE_COMPAT_BENCH_WARMUPS ?? 3);
for (const value of [samples, fresh, warmups]) assert(Number.isInteger(value) && value > 0 && value < 100);
const selectedOperations = process.env.NODE_COMPAT_BENCH_OPERATIONS?.split(',');
const selectedSizes = process.env.NODE_COMPAT_BENCH_SIZES?.split(',').map(Number);
const scenarios = manifest.scenarios.filter(s => (!selectedOperations || selectedOperations.includes(s.operation)) && (!selectedSizes || selectedSizes.includes(s.size)));
assert(scenarios.length);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const records = [];
function command(args) {
  const result = spawnSync(host, args.map(String), { encoding: 'utf8', timeout: 900000, maxBuffer: 32 * 1024 * 1024 });
  assert.equal(result.status, 0, result.error?.message || result.stderr || result.stdout);
  const report = JSON.parse(result.stdout);
  assert.equal(report.settings.wasmtimeCrate, '42.0.1');
  assert.deepEqual(report.settings.guestHostImports, []);
  return report;
}
const compilation = [];
for (const arm of manifest.records) {
  assert.equal(hash(await readFile(arm.componentPath)), arm.componentSha256, 'stale component');
  const precompiled = join(dirname(arm.componentPath), 'benchmark.local.cwasm');
  const report = command(['compile', arm.componentPath, precompiled]);
  compilation.push({ arm: arm.arm, componentBytes: arm.componentBytes, componentGzipBytes: arm.componentGzipBytes,
    componentSha256: arm.componentSha256, precompiled, precompiledSha256: hash(await readFile(precompiled)), report });
}
function percentile(values, fraction) {
  const sorted = [...values].sort((a, b) => a - b);
  const index = (sorted.length - 1) * fraction;
  const lower = Math.floor(index), upper = Math.ceil(index);
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (index - lower);
}
for (const [index, scenario] of scenarios.entries()) {
  // Alternate arm order to limit systematic effects from temperature and load.
  const arms = index % 2 ? [...compilation].reverse() : compilation;
  for (const arm of arms) {
    console.error(`${arm.arm} ${scenario.operation} ${scenario.size}B x${scenario.iterations}`);
    const report = command(['measure', arm.precompiled, scenario.operation, scenario.size, scenario.iterations,
      samples, fresh, warmups, scenario.expectedSetupChecksum, scenario.expectedRunChecksum]);
    assert.equal(report.instances.length, fresh);
    for (const instance of report.instances) {
      assert.equal(instance.setupChecksum, scenario.expectedSetupChecksum);
      assert.equal(instance.runChecksum, scenario.expectedRunChecksum);
      assert.equal(instance.batchNs.length, samples);
      assert.equal(instance.linearMemoryGrowFailures, 0);
    }
    const timings = report.instances.flatMap(i => i.batchNs);
    const medianNs = percentile(timings, 0.5);
    const processedBytes = scenario.processedBytesPerIteration * scenario.iterations;
    records.push({ arm: arm.arm, ...scenario, report, summary: {
      batchNs: { min: Math.min(...timings), p25: percentile(timings, 0.25), median: medianNs, p75: percentile(timings, 0.75), max: Math.max(...timings), count: timings.length },
      instanceMedianBatchNs: report.instances.map(i => percentile(i.batchNs, 0.5)),
      nanosecondsPerOperation: medianNs / scenario.iterations,
      inputMiBPerSecond: processedBytes / (medianNs / 1e9) / 1048576,
      instantiateNsMedian: percentile(report.instances.map(i => i.instantiateNs), 0.5),
      setupNsMedian: percentile(report.instances.map(i => i.setupNs), 0.5),
      firstBatchNsMedian: percentile(report.instances.map(i => i.firstBatchNs), 0.5),
      peakProcessRssBytes: Math.max(...report.instances.map(i => i.peakProcessRssBytes ?? 0)),
      largestLinearMemoryRequestBytes: Math.max(...report.instances.map(i => i.largestLinearMemoryRequestBytes)),
    } });
    // Persist completed observations even if later experiments fail.
    await writeFile(join(output, 'wasmtime-records.partial.json'), JSON.stringify({ compilation, records }, null, 2) + '\n');
  }
}
const comparisons = scenarios.map(scenario => {
  const arm = name => records.find(r => r.arm === name && r.operation === scenario.operation && r.size === scenario.size);
  const native = arm('native'), javascript = arm('jco-js');
  return { operation: scenario.operation, size: scenario.size, iterations: scenario.iterations,
    nativeInputMiBPerSecond: native.summary.inputMiBPerSecond, javascriptInputMiBPerSecond: javascript.summary.inputMiBPerSecond,
    javascriptOverNativeMedianTime: javascript.summary.batchNs.median / native.summary.batchNs.median,
    nativePeakProcessRssBytes: native.summary.peakProcessRssBytes, javascriptPeakProcessRssBytes: javascript.summary.peakProcessRssBytes,
    nativeLargestLinearMemoryRequestBytes: native.summary.largestLinearMemoryRequestBytes,
    javascriptLargestLinearMemoryRequestBytes: javascript.summary.largestLinearMemoryRequestBytes,
    nativeInstantiateNsMedian: native.summary.instantiateNsMedian, javascriptInstantiateNsMedian: javascript.summary.instantiateNsMedian,
  };
});
const sourceNames = ['benchmark.wit', 'workload.mjs', 'build.mjs', 'run.mjs', 'host/Cargo.toml', 'host/Cargo.lock', 'host/src/main.rs'];
const results = { schemaVersion: 1, createdUtc: new Date().toISOString(), node: process.version,
  machine: { platform: platform(), arch: arch(), release: release(), cpuModel: cpus()[0]?.model, logicalCpus: cpus().length, totalMemoryBytes: totalmem() },
  host, hostSha256: hash(await readFile(host)), engineSha256: manifest.engineSha256,
  sourceManifest: await Promise.all(sourceNames.map(async path => ({ path, sha256: hash(await readFile(join(here, path))) }))),
  adapter: manifest.adapter, protocol: manifest.protocol, samplesPerInstance: samples, freshInstancesPerScenario: fresh,
  warmupBatches: warmups, armOrder: 'native first for even scenario indexes; javascript first for odd',
  compilation, comparisons, records,
  limitations: ['Microbenchmarks in one local machine run; not whole-application performance claims',
    'Seven batches within an instance are correlated; the default has three fresh instances, not 21 fully independent trials',
    'Both arms use the same profile-enabled engine, so the size delta is incremental JS adapter overhead, not minimal profile-off deployment savings',
    'No guest clock/capability imports. Host Instant times batches of operations plus an O(1) result fingerprint, not an isolated CPU primitive',
    'The fingerprint reads a constant number of result positions; sampled character access may materialize a JavaScript rope string, so string throughput includes that observable work',
    'Setup includes input preparation and one full FNV correctness hash; first batch and warmed throughput are separate',
    'Fresh component instances share a deserialized component within one process; compiler is isolated in a separate compile process',
    'RSS includes Wasmtime code, runtime and allocator retention; later instance peaks are cumulative within each measurement process',
    'Largest linear-memory request is a ResourceLimiter observation, not total guest heap or aggregate resident memory',
    'Checksum transport uses s32 reinterpreted as u32 because high-u32 return lowering failed a separate binding diagnostic'],
};
await writeFile(join(output, 'wasmtime-results.json'), JSON.stringify(results, null, 2) + '\n');
console.log(JSON.stringify({ output: join(output, 'wasmtime-results.json'), comparisons }, null, 2));
