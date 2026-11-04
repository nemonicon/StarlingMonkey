// Run the shared dependency-free cases against the actual pinned Node APIs.
import assert from 'node:assert/strict';
import { AsyncLocalStorage, AsyncResource, executionAsyncResource, executionAsyncId } from 'node:async_hooks';
import { createHash } from 'node:crypto';
import { readFile as readFileCallback } from 'node:fs';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runResourceCases } from './resource-model-cases.mjs';
import { runResourceEdgeCases } from './resource-model-edge-cases.mjs';

assert.equal(process.version, 'v22.14.0');
assert.deepEqual(process.execArgv, []);
assert(!process.env.NODE_OPTIONS, 'Run without feature flags to preserve the exact Node oracle');
const sourcePath = fileURLToPath(import.meta.url);
const here = dirname(sourcePath);
const result = await runResourceCases({
  AsyncLocalStorage, AsyncResource, executionAsyncResource, executionAsyncId,
  queueMicrotask, setTimeout, clearTimeout, setInterval, clearInterval,
  readFileCallback, readFile, sourcePath,
});
assert.equal(result.caseCount, 19);
assert.equal(result.observationCount, 63);
assert(result.cases.every(item => item.passed));
const original = JSON.parse(await readFile(join(here, 'node-oracle-results.json')));
function stableCases(cases) {
  return cases.map(item => {
    const observations = item.observations.map(({ executionAsyncId, resourceKind, ...entry }) => entry);
    // Independent filesystem requests have no specified cross-request completion
    // order. The shared case asserts each store, not this relative ordering.
    if (item.name === 'native filesystem callback and promise I/O retain registration contexts') {
      observations.sort((a, b) => a.label.localeCompare(b.label));
    }
    return { name: item.name, observations };
  });
}
assert.deepEqual(stableCases(result.cases), stableCases(original.cases),
  'The extracted model must preserve the original labels, stores and assertion counts');
const edge = await runResourceEdgeCases({ AsyncLocalStorage, AsyncResource, queueMicrotask });
assert.equal(edge.caseCount, 9);
assert.equal(edge.observationCount, 44);
assert.equal(edge.assertionPropagationChecked, true);
assert(edge.cases.every(item => item.passed));
const originalEdge = JSON.parse(await readFile(join(here, 'node-promise-edge-oracle-results.json')));
function storeCases(cases) {
  return cases.map(item => ({ name: item.name, observations: item.observations.map(row =>
    Object.fromEntries(Object.entries(row).filter(([key]) => !['executionAsyncId','resourceKind','resultAsyncId'].includes(key)))) }));
}
assert.deepEqual(storeCases(edge.cases), storeCases(originalEdge.cases),
  'The edge suite must retain original store/identity behavior while explicitly excluding ID/lifecycle assertions');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const report = {
  schemaVersion: 1, verifiedAtUtc: new Date().toISOString(),
  node: process.version, executable: process.execPath,
  executableSha256: hash(await readFile(process.execPath)),
  execArgv: process.execArgv, nodeOptionsPresent: Boolean(process.env.NODE_OPTIONS),
  sharedEdgeCasesSha256: hash(await readFile(join(here, 'resource-model-edge-cases.mjs'))),
  originalEdgeSourceSha256: hash(await readFile(join(here, 'node-promise-edge-oracle.mjs'))),
  originalEdgeResultsSha256: hash(await readFile(join(here, 'node-promise-edge-oracle-results.json'))),
  edge: { ...edge, originalLabelsStoresAndCountsIdentical: true },
  sharedCasesSha256: hash(await readFile(join(here, 'resource-model-cases.mjs'))),
  runnerSha256: hash(await readFile(sourcePath)),
  originalOracleSourceSha256: hash(await readFile(join(here, 'node-oracle.mjs'))),
  originalOracleResultsSha256: hash(await readFile(join(here, 'node-oracle-results.json'))),
  originalLabelsStoresAndCountsIdentical: true,
  crossRunNormalization: 'Execution IDs/resource class names and the unspecified relative completion order of the two independent native filesystem requests only; all shared case assertions remain unchanged.',
  ...result,
  injectedImplementations: {
    AsyncLocalStorage: 'node:async_hooks', AsyncResource: 'node:async_hooks',
    queueMicrotask: 'native Node global',
    timers: 'native Node setTimeout/clearTimeout/setInterval/clearInterval',
    filesystem: 'native node:fs and node:fs/promises reading this runner source',
  },
  scope: 'This run uses real Node APIs. The shared cases accept injected APIs for separate guest experiments; guest AsyncTask completion/repeating resources must be labeled as stand-ins and cannot establish real WASI timer/filesystem propagation.',
};
await writeFile(join(here, 'resource-model-node-oracle-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ node: report.node, cases: report.caseCount,
  observations: report.observationCount, edgeCases: report.edge.caseCount, edgeObservations: report.edge.observationCount, originalObservationsIdentical: true, passed: true }, null, 2));
