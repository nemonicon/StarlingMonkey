// Follow-up to the short two-operation large-buffer batches in compare.mjs.
// Verify longer decoder batches separately; never overwrite the original run.
import assert from 'node:assert/strict';
import { Buffer } from 'node:buffer';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { resolve, join } from 'node:path';
import { createWorkload } from '../bench/workload.mjs';

assert.equal(process.version, 'v22.14.0');
const output = resolve(process.env.NODE_COMPAT_IMPROVEMENT_OUTPUT ?? '/tmp/starling-node-compat/improvement');
const host = resolve(process.env.NODE_COMPAT_BENCH_HOST ?? '/tmp/starling-node-compat/bench-host-target/release/node-profile-bench-host');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const original = JSON.parse(await readFile(join(output, 'improvement-results.json')));
assert.equal(hash(await readFile(host)), original.hostSha256);
const oracle = createWorkload(Buffer);
const records = [];
const median = values => { const a = [...values].sort((x, y) => x - y); return a[(a.length - 1) / 2]; };
for (const size of [65536, 524288]) {
  const iterations = 33554432 / size;
  const expectedSetupChecksum = oracle.setup('utf8-decode', size) >>> 0;
  const expectedRunChecksum = oracle.run(iterations) >>> 0;
  // Two passes with opposite order, same precompiled artifacts, fresh processes.
  for (let pass = 0; pass < 2; pass++) {
    const arms = pass ? original.compilation : [...original.compilation].reverse();
    for (const arm of arms) {
      assert.equal(hash(await readFile(arm.precompiled)), arm.precompiledSha256);
      console.error(`${arm.arm} utf8-decode/${size} x${iterations} pass${pass}`);
      const run = spawnSync(host, ['measure', arm.precompiled, 'utf8-decode', size, iterations, 7, 3, 3, expectedSetupChecksum, expectedRunChecksum].map(String),
        { encoding: 'utf8', timeout: 120000, maxBuffer: 16 * 1024 * 1024 });
      assert.equal(run.status, 0, run.error?.message || run.stderr || run.stdout);
      const report = JSON.parse(run.stdout);
      assert.equal(report.settings.wasmtimeCrate, '42.0.1');
      assert.deepEqual(report.settings.guestHostImports, []);
      assert.equal(report.instances.length, 3);
      for (const instance of report.instances) {
        assert.equal(instance.setupChecksum, expectedSetupChecksum);
        assert.equal(instance.runChecksum, expectedRunChecksum);
        assert.equal(instance.linearMemoryGrowFailures, 0);
        assert.equal(instance.batchNs.length, 7);
      }
      const batchNs = median(report.instances.flatMap(i => i.batchNs));
      records.push({ arm: arm.arm, size, iterations, pass, expectedSetupChecksum, expectedRunChecksum, report,
        medianBatchNs: batchNs, payloadMiBPerSecond: 32 / (batchNs / 1e9),
        instanceMedianBatchNs: report.instances.map(i => median(i.batchNs)) });
    }
  }
}
const comparisons = [65536, 524288].flatMap(size => [0, 1].map(pass => {
  const control = records.find(r => r.arm === 'control' && r.size === size && r.pass === pass);
  const candidate = records.find(r => r.arm === 'candidate' && r.size === size && r.pass === pass);
  return { size, pass, controlPayloadMiBPerSecond: control.payloadMiBPerSecond, candidatePayloadMiBPerSecond: candidate.payloadMiBPerSecond,
    candidateOverControlThroughput: control.medianBatchNs / candidate.medianBatchNs };
}));
const results = { schemaVersion: 1, createdUtc: new Date().toISOString(), node: process.version,
  sourceSha256: hash(await readFile(new URL(import.meta.url))), originalResultsSha256: hash(await readFile(join(output, 'improvement-results.json'))),
  hostSha256: original.hostSha256, machine: original.machine,
  protocol: '32MiB payload per batch; three fresh instances, three warmups and seven correlated timed batches; two passes with opposite arm order; original compiled component hashes',
  comparisons, records,
  limitations: ['Targeted stability check on the same machine, not a replacement for the original experiment',
    'Larger batches change allocation/GC pressure as well as reducing relative timer noise',
    'No formal significance claim; independent session and Weval validation remain future work'] };
await writeFile(join(output, 'stability-results.json'), JSON.stringify(results, null, 2) + '\n');
console.log(JSON.stringify({ comparisons }, null, 2));
