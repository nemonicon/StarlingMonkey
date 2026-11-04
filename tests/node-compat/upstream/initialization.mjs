// Profile policy diagnostics: the baseline intentionally demonstrates the gap;
// strict mode is the acceptance gate for a rebuilt profile engine.
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { context, output, hash } from './common.mjs';

const ctx = await context();
const expectedPolicy = process.env.NODE_COMPAT_INIT_EXPECT ?? 'strict';
assert(['legacy', 'strict'].includes(expectedPolicy));
if (expectedPolicy === 'strict') assert.equal(ctx.metadata.strictInitialization, true, 'Strict acceptance requires explicit native build metadata');
const prefix = "import { spawn } from 'node:child_process';\n";
const suffix = "\nexport function run() { return 'initialized'; }\n";
const vectors = [
  { name: 'direct-unsupported-call', source: 'spawn();', rejected: true },
  { name: 'awaited-callback-unsupported-call', source: 'await Promise.resolve().then(() => spawn());', rejected: true },
  { name: 'detached-callback-unsupported-call', source: 'Promise.resolve().then(() => spawn());', rejected: true, legacyAccepted: true },
  { name: 'detached-async-unsupported-call', source: '(async () => spawn())();', rejected: true, legacyAccepted: true },
  { name: 'explicit-unhandled-rejection', source: "Promise.reject(new Error('initialization-gate-rejection'));", rejected: true, legacyAccepted: true },
  { name: 'late-microtask-handler', source: 'const p = Promise.resolve().then(() => spawn()); queueMicrotask(() => p.catch(() => {}));', rejected: false },
  { name: 'awaited-handled-rejection', source: 'await Promise.resolve().then(() => spawn()).catch(() => {});', rejected: false },
  { name: 'finalizer-unhandled-rejection', source: 'const r = new FinalizationRegistry(() => { Promise.resolve().then(() => spawn()); }); function register() { r.register({}, 0); } register();', rejected: true, legacyAccepted: true },
  { name: 'finalizer-late-handler', source: 'const r = new FinalizationRegistry(() => { const p = Promise.resolve().then(() => spawn()); queueMicrotask(() => p.catch(() => {})); }); function register() { r.register({}, 0); } register();', rejected: false },
];
const results = [];
for (const vector of vectors) {
  const source = prefix + vector.source + suffix;
  let error, component;
  try {
    ({ component } = await ctx.componentize(source, { engine: ctx.engine, sourceName: vector.name + '.js',
      preview2Adapter: ctx.preview2Adapter,
      witWorld: 'package test:initialization-policy; world test { export run: func() -> string; }',
      selectedInterfaces: [], disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'] }));
  } catch (failure) { error = failure.message; }
  const shouldReject = vector.rejected && !(expectedPolicy === 'legacy' && vector.legacyAccepted);
  const record = { name: vector.name, source, sourceSha256: hash(source), shouldReject, rejected: !!error,
    policyGap: vector.rejected && !error, error,
    componentSha256: component && hash(component) };
  if (component) {
    const wit = await ctx.componentWit(component);
    record.emittedImports = wit.split('\n').filter(line => /^\s*import /.test(line)).map(line => line.trim());
    assert.deepEqual(record.emittedImports, [], 'Accepted initialization fixtures must have zero host imports');
    record.componentPath = join(output, vector.name + '.component.wasm');
    record.componentBytes = component.length;
    await writeFile(record.componentPath, component);
  }
  if (error && !vector.name.includes('explicit-')) assert.match(error, /child_process\.spawn|ERR_SM_NODE_INITIALIZATION_REJECTION/);
  record.pass = record.rejected === shouldReject;
  results.push(record);
  console.log(JSON.stringify({ name: vector.name, pass: record.pass, rejected: record.rejected, policyGap: record.policyGap }));
}
const report = { schema: 1, engine: ctx.engine, engineSha256: ctx.engineSha256, expectedPolicy,
  componentizerProvenance: ctx.componentizerProvenance,
  checkpoint: 'After queued initialization jobs and pre-snapshot finalization cleanup; handled rejections must pass',
  sourceRoot: ctx.sourceRoot, passed: results.filter(result => result.pass).length,
  failed: results.filter(result => !result.pass).length, results };
await writeFile(join(output, `initialization-${expectedPolicy}-results.json`), JSON.stringify(report, null, 2) + '\n');
assert.equal(report.failed, 0, 'Initialization policy gate failed; inspect result records');
