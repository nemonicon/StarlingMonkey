import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(process.env.NODE_COMPAT_OPTIMIZATION_OUTPUT ?? '/tmp/starling-node-compat/optimization');
const host = resolve(process.env.NODE_COMPAT_BENCH_HOST ?? '/tmp/starling-node-compat/bench-host-target/release/node-profile-bench-host');
const manifest = JSON.parse(await readFile(join(output, 'probe-build.json')));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
assert.equal(hash(await readFile(manifest.componentPath)), manifest.componentSha256);
assert.equal(manifest.baselineEngineSha256, 'da69618da72315c3b3f20d105708fd625a3b7c0691f49329201036c3c2fd5796');
const selected = process.env.NODE_COMPAT_PROBE_OPERATIONS?.split(',');
const sizes = process.env.NODE_COMPAT_PROBE_SIZES?.split(',').map(Number);
const scenarios = manifest.scenarios.filter(value => (!selected || selected.includes(value.operation)) && (!sizes || sizes.includes(value.size)));
assert(scenarios.length);
function command(args) {
  const result = spawnSync(host, args.map(String), { encoding: 'utf8', timeout: 300000, maxBuffer: 8 * 1024 * 1024 });
  assert.equal(result.status, 0, result.error?.message || result.stderr || result.stdout);
  const report = JSON.parse(result.stdout);
  assert.equal(report.settings.wasmtimeCrate, '42.0.1');
  assert.deepEqual(report.settings.guestHostImports, []);
  return report;
}
const precompiled = join(output, 'probes.local.cwasm');
const compilation = command(['compile', manifest.componentPath, precompiled]);
const records = [];
const median = values => { const sorted = [...values].sort((a, b) => a - b); const middle = (sorted.length - 1) / 2; return (sorted[Math.floor(middle)] + sorted[Math.ceil(middle)]) / 2; };
for (const scenario of scenarios) {
  console.error(`${scenario.operation} ${scenario.size}B x${scenario.iterations}`);
  const report = command(['measure', precompiled, scenario.operation, scenario.size, scenario.iterations, 7, 3, 3, scenario.expectedSetupChecksum, scenario.expectedRunChecksum]);
  for (const instance of report.instances) {
    assert.equal(instance.setupChecksum, scenario.expectedSetupChecksum);
    assert.equal(instance.runChecksum, scenario.expectedRunChecksum);
    assert.equal(instance.linearMemoryGrowFailures, 0);
  }
  const summary = {
    medianBatchNs: median(report.instances.flatMap(instance => instance.batchNs)),
    instanceMedianBatchNs: report.instances.map(instance => median(instance.batchNs)),
    peakProcessRssBytes: Math.max(...report.instances.map(instance => instance.peakProcessRssBytes)),
    largestLinearMemoryRequestBytes: Math.max(...report.instances.map(instance => instance.largestLinearMemoryRequestBytes)),
  };
  records.push({ ...scenario, report, summary });
  await writeFile(join(output, 'probe-results.partial.json'), JSON.stringify({ manifest, compilation, records }, null, 2) + '\n');
}
const result = {
  schema: 1, node: process.version, baselineEngineSha256: manifest.baselineEngineSha256,
  componentSha256: manifest.componentSha256, facts: manifest.facts,
  host, hostSha256: hash(await readFile(host)), compilation, records,
  sourceManifest: await Promise.all(['probes.mjs', 'probes.wit', 'build-probes.mjs', 'run-probes.mjs'].map(async path => ({ path, sha256: hash(await readFile(join(here, path))) }))),
  protocol: { freshInstancesPerCase: 3, warmupBatches: 3, firstBatchUntimed: true, samplesPerInstance: 7,
    sameMaterializedSource: true, sameComponentForAllControls: true, comparison: 'Only selected per-output allocation/validation stages differ',
    measurementUnits: 'Host batch nanoseconds; process peak RSS; largest single linear-memory growth request',
  },
  limitations: ['Diagnostic controls are not compatible alternate Buffer implementations',
    'Own-property brands are reflectable/spoofable and excluded from production recommendations',
    'Class-private stamping is only a control; full realm, species and lifecycle behavior is not established',
    'Native Uint8Array.fromHex controls use valid input only; strict malformed semantics differ from Node',
    'Different native hex implementations cannot by themselves attribute kernel differences to the facade',
    'Within-instance batches are correlated; RSS includes host/runtime and later fresh-instance high-water marks are cumulative',
    'These are controlled performance/allocation observations, not per-allocation GC counters or total guest heap measurements'],
};
await writeFile(join(output, 'probe-results.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ output: join(output, 'probe-results.json'), cases: records.length, facts: result.facts,
  summaries: records.map(value => ({ operation: value.operation, size: value.size, ...value.summary })) }, null, 2));
