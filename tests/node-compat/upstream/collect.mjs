// Collect existing executions; no componentization, host or timing work.
import assert from 'node:assert/strict';
import { readFile, readdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { context, here, output, hash, regressionImports, verifyUpstreamSource } from './common.mjs';

const ctx = await context();
const skipIntegration = process.env.NODE_COMPAT_UPSTREAM_SKIP_INTEGRATION === '1';
const files = ['componentize-builtins-results.json', 'buffer-ownership-results.json', 'starling-e2e-results.json',
  ...(skipIntegration ? [] : ['starling-integration-results.json']), `initialization-${process.env.NODE_COMPAT_INIT_EXPECT ?? 'strict'}-results.json`];
const sections = {};
for (const name of files) {
  const bytes = await readFile(join(output, name));
  const result = JSON.parse(bytes);
  assert.equal(result.engineSha256, ctx.engineSha256, `Stale result engine: ${name}`);
  if (ctx.componentizerProvenance.selection !== 'stock-legacy-diagnostic') {
    assert.equal(result.componentizerProvenance?.manifestSha256, ctx.componentizerProvenance.manifestSha256, `Stale packaging result: ${name}`);
    assert.deepEqual(result.componentizerProvenance.checkedFiles, ctx.componentizerProvenance.checkedFiles);
  }
  sections[name] = { sha256: hash(bytes), report: result };
}
for (const result of sections['componentize-builtins-results.json'].report.results) {
  assert.equal(hash(await readFile(result.fixturePath)), result.fixtureSha256);
  await verifyUpstreamSource('test/builtins/' + result.name + '.js', ctx.metadata);
  if (result.componentSha256) assert.equal(hash(await readFile(join(result.directory, result.name + '.component.wasm'))), result.componentSha256);
}
await verifyUpstreamSource('test/export-buffers.js', ctx.metadata);
for (const result of sections['buffer-ownership-results.json'].report.components) {
  assert.equal(hash(await readFile(result.componentPath)), result.componentSha256);
}
for (const result of sections['starling-e2e-results.json'].report.results) {
  assert.equal(hash(await readFile(result.sourcePath)), result.sourceSha256);
  if (result.componentSha256) assert.equal(hash(await readFile(join(output, 'starling-e2e', result.name, result.name + '.component.wasm'))), result.componentSha256);
}
for (const result of sections[files.at(-1)].report.results) {
  if (result.componentPath) {
    assert.equal(hash(await readFile(result.componentPath)), result.componentSha256);
    assert.deepEqual(result.emittedImports, []);
  }
}
if (!skipIntegration) {
  const integration = sections['starling-integration-results.json'].report;
  assert.equal(hash(await readFile(integration.componentPath)), integration.componentSha256);
  for (const id of integration.emittedImports) assert(regressionImports.includes(id));
}
const harnessManifest = [];
for (const name of (await readdir(here)).filter(name => name.endsWith('.mjs')).sort()) {
  harnessManifest.push({ path: 'tests/node-compat/upstream/' + name, sha256: hash(await readFile(join(here, name))) });
}
const observedImports = new Set();
for (const section of Object.values(sections)) {
  for (const result of section.report.results ?? []) {
    for (const line of result.emittedImports ?? []) {
      const id = /^import\s+([^;]+);$/.exec(line)?.[1] ?? line;
      assert(regressionImports.includes(id));
      observedImports.add(id);
    }
  }
}
const report = { schema: 1, engine: ctx.engine, engineSha256: ctx.engineSha256, sourceRoot: ctx.sourceRoot,
  engineMetadataPath: ctx.metadataPath, engineMetadataSha256: hash(await readFile(ctx.metadataPath)),
  verifiedSourceManifest: ctx.metadata.sourceManifest,
  nativeBuildPolicy: Object.fromEntries(['hostApi', 'profileEnabled', 'strictInitialization', 'gcStress', 'oomTesting',
    'debuggerEnabled', 'abiFixEnabled', 'bigIntFixEnabled'].map(key => [key, ctx.metadata[key]])),
  sourceFilesVerified: ctx.metadata.sourceManifest.length, componentizerProvenance: ctx.componentizerProvenance,
  allowedRegressionImports: regressionImports, observedRegressionImports: [...observedImports].sort(), harnessManifest, sections,
  notRerun: skipIntegration ? [{ gate: 'Starling integration routes',
    reason: 'Previously recorded crypto entropy failure remains open; selected current rerun excludes these routes',
    priorEvidence: 'tests/node-compat/upstream/phase1-results.json',
    priorEvidenceSha256: hash(await readFile(join(here, 'phase1-results.json'))) }] : [],
  openGates: [
    ...Object.entries(sections).filter(([, section]) => section.report.failed).map(([name, section]) => `${name}: ${section.report.failed} failed`),
    ...(sections[files.at(-1)].report.results.some(result => result.policyGap) ? ['Baseline permits unhandled initializer rejections; rebuilt strict engine required'] : []),
    ...(skipIntegration ? ['Previously recorded crypto integration entropy failure remains unresolved; integration routes not rerun here'] : []),
    'Complete WPT/debugger-ON/AOT/concurrent Vitest and all synthetic-host binding fixtures were not executed',
  ],
};
await writeFile(join(output, 'selected-gate-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ output: join(output, 'selected-gate-results.json'), engineSha256: ctx.engineSha256, openGates: report.openGates }, null, 2));
