// Combined candidate acceptance. Preserve every earlier baseline report and
// write only to a new optimization output tree. --collect-only verifies runs
// already completed with these exact entry points.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { closeSync, openSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const tests = resolve(here, '..');
const output = resolve(process.env.NODE_COMPAT_OPTIMIZATION_OUTPUT ?? '/tmp/starling-node-compat/optimization');
const release = resolve(process.env.NODE_COMPAT_CANDIDATE_ENGINE ?? '/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.candidate.release.wasm');
const stress = resolve(process.env.NODE_COMPAT_CANDIDATE_STRESS_ENGINE ?? '/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.candidate.gc-stress.wasm');
const releaseDirectory = join(output, 'candidate-release-semantic');
const stressDirectory = join(output, 'candidate-stress-semantic');
const httpDirectory = join(output, 'candidate-http');
const cloudDirectory = join(output, 'candidate-wasmcloud');
const cloudResults = join(cloudDirectory, 'candidate-host-results.json');
await mkdir(output, { recursive: true });
await mkdir(cloudDirectory, { recursive: true });
function run(script, name, environment) {
  const log = openSync(join(output, name + '.log'), 'w');
  try {
    const result = spawnSync(process.execPath, [script], { env: { ...process.env, ...environment },
      stdio: ['ignore', log, log], timeout: 300000 });
    assert.equal(result.status, 0, result.error?.message || `Validation failed; see ${join(output, name + '.log')}`);
  } finally { closeSync(log); }
}
if (!process.argv.includes('--collect-only')) {
  assert(process.env.NODE_COMPAT_WASMTIME && process.env.NODE_COMPAT_WASM_TOOLS, 'Set exact Wasmtime 42.0.1 and wasm-tools 1.235.0 paths');
  for (const [engine, directory, name] of [[release, releaseDirectory, 'candidate-release-semantic'], [stress, stressDirectory, 'candidate-stress-semantic']]) {
    run(join(tests, 'run.mjs'), name, { NODE_COMPAT_ENGINE: engine, NODE_COMPAT_OUTPUT: directory,
      NODE_COMPAT_ENGINE_METADATA: engine + '.build.json',
      NODE_COMPAT_SEMANTIC_ENTRY: join(here, 'candidate-component.mjs') });
  }
  run(join(tests, 'wasmcloud/build-http.mjs'), 'candidate-http-build', { NODE_COMPAT_ENGINE: release,
    NODE_COMPAT_ENGINE_METADATA: release + '.build.json',
    NODE_COMPAT_HTTP_OUTPUT: httpDirectory, NODE_COMPAT_HTTP_ENTRY: join(here, 'candidate-http.mjs') });
  run(join(tests, 'wasmcloud/test-wasmtime-http.mjs'), 'candidate-wasmtime-http', { NODE_COMPAT_HTTP_OUTPUT: httpDirectory,
    NODE_COMPAT_HTTP_AUDIT: join(httpDirectory, 'component-audit.json'),
    NODE_COMPAT_HTTP_REQUIRE_INTRINSICS: '1' });
  run(join(tests, 'wasmcloud/run-host.mjs'), 'candidate-wasmcloud', {
    NODE_COMPAT_HTTP_COMPONENT: join(httpDirectory, 'native-profile-http.component.wasm'),
    NODE_COMPAT_HTTP_AUDIT: join(httpDirectory, 'component-audit.json'),
    NODE_COMPAT_WASMCLOUD_OUTPUT: cloudDirectory, NODE_COMPAT_WASMCLOUD_RESULTS: cloudResults,
  });
}
const readJSON = async path => JSON.parse(await readFile(path));
const releaseReport = await readJSON(join(releaseDirectory, 'results.json'));
const stressReport = await readJSON(join(stressDirectory, 'results.json'));
const httpAudit = await readJSON(join(httpDirectory, 'component-audit.json'));
const wasmtimeHTTP = await readJSON(join(httpDirectory, 'wasmtime-results.json'));
const wasmCloud = await readJSON(cloudResults);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
function check(report) {
  assert(!report.failure, JSON.stringify(report.failure));
  assert.equal(report.strings, 381);
  assert.equal(report.bytes, 250);
  assert.equal(report.stubCalls, 9);
  assert.equal(report.stubConstructors, 9);
  assert.equal(report.intrinsics.nativeModule, true);
  assert.equal(report.intrinsics.sizesChecked, 8);
  assert.equal(report.intrinsics.inputSpoofsRejected, 3);
  assert.equal(report.intrinsics.publicInputShadowsChecked, 4);
  assert.equal(report.intrinsics.publicReplacementCalls, 0);
  assert.equal(report.intrinsics.capturedProducerAndBrandChecksPassed, true);
}
for (const [report, engine, gcStress, directory] of [[releaseReport, release, false, releaseDirectory], [stressReport, stress, true, stressDirectory]]) {
  assert.equal(report.engineSha256, hash(await readFile(engine)));
  assert.equal(report.componentSha256, hash(await readFile(join(directory, 'native-profile.component.wasm'))));
  assert.equal(report.semanticEntry, join(here, 'candidate-component.mjs'));
  assert.equal(report.engineMetadata.gcStress, gcStress);
  assert.deepEqual(report.emittedImports, []);
  assert.equal(report.calls.length, 2);
  report.calls.forEach(check);
  check(report.wasmtimeReport);
  assert.equal(report.initializationFailures.length, 4);
}
assert.equal(httpAudit.componentSha256, hash(await readFile(httpAudit.componentPath)));
assert.equal(httpAudit.engineSha256, releaseReport.engineSha256);
assert.equal(httpAudit.httpEntry, join(here, 'candidate-http.mjs'));
assert.equal(wasmtimeHTTP.componentSha256, httpAudit.componentSha256);
assert.equal(wasmCloud.component.sha256, httpAudit.componentSha256);
assert.deepEqual(httpAudit.clockDependency.callableImports, []);
assert.deepEqual(httpAudit.clockDependency.coreClockImports, []);
for (const transport of [wasmtimeHTTP, wasmCloud]) {
  assert.equal(transport.responses.length, 3);
  for (const response of transport.responses) {
    assert.equal(response.status, 200);
    check(response.body.native);
    assert.equal(response.body.native.calls, response.body.componentInstanceRequestCount);
  }
}
const summary = {
  schema: 1, verifiedAtUtc: new Date().toISOString(),
  release: { path: join(releaseDirectory, 'results.json'), engineSha256: releaseReport.engineSha256,
    componentSha256: releaseReport.componentSha256, emittedImports: [], calls: releaseReport.calls,
    initializationFailures: releaseReport.initializationFailures, wasmtimeReport: releaseReport.wasmtimeReport },
  gcStress: { path: join(stressDirectory, 'results.json'), engineSha256: stressReport.engineSha256,
    componentSha256: stressReport.componentSha256, emittedImports: [], calls: stressReport.calls,
    initializationFailures: stressReport.initializationFailures, wasmtimeReport: stressReport.wasmtimeReport },
  http: { audit: httpAudit, wasmtime: wasmtimeHTTP, wasmCloud },
  sourceManifest: await Promise.all(['intrinsics-checks.mjs', 'candidate-component.mjs', 'candidate-http.mjs', 'validate-candidate.mjs']
    .map(async path => ({ path, sha256: hash(await readFile(join(here, path))) }))),
  limitations: ['SharedArrayBuffer is not exposed in these component engines; host Node tests cover rejection separately',
    'Cross-realm creation is not exposed by the production component API, so cross-realm overload parity remains unverified',
    'HTTP counters report observed state retention, not general request reuse/isolation guarantees',
    'Forced rooted-boundary collections are not full GC zeal or exhaustive OOM injection'],
};
const resultPath = join(output, 'candidate-validation-results.json');
await writeFile(resultPath, JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify({ resultPath, releaseEngine: summary.release.engineSha256, stressEngine: summary.gcStress.engineSha256,
  releaseAndStressPassed: true, httpComponent: httpAudit.componentSha256, wasmtimeRequests: wasmtimeHTTP.responses.length,
  wasmCloudRequests: wasmCloud.responses.length, capturedPublicReplacementCalls: 0 }, null, 2));
