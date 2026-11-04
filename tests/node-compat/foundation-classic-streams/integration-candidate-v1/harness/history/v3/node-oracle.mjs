// The only executed gate in this future-component template directory.
// Pinned public Node built-ins only; no candidate factory or componentizer.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import * as stream from 'node:stream';
import * as promises from 'node:stream/promises';
import { Buffer } from 'node:buffer';
import { checks as originalChecks } from '../../implementation-candidate-v1/checks.mjs';
import { checks as portableChecks } from './checks.mjs';

assert.equal(process.version, 'v22.14.0');
assert.deepEqual(process.execArgv, []);
assert(!process.env.NODE_OPTIONS);
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const originalURL = new URL('../../implementation-candidate-v1/checks.mjs', import.meta.url);
const expectedURL = new URL('../../implementation-candidate-v1/node-final-acceptance-results.json', import.meta.url);
const sourceReceiptURL = new URL('../../implementation-candidate-v1/source-receipt.json', import.meta.url);
const manifestURL = new URL('../../implementation-candidate-v1/export-manifest.classic-streams.node-v22.14.0.json', import.meta.url);
const original = await readFile(originalURL);
const transformed = await readFile(new URL('./checks.mjs', import.meta.url));
const expectedBytes = await readFile(expectedURL);
const sourceReceipt = await readFile(sourceReceiptURL);
const manifest = await readFile(manifestURL);
const from = 'await new Promise(resolve=>process.nextTick(resolve));';
const to = 'await promises.finished(source).catch(()=>{});';
assert.equal(sha256(original), 'fd7905c7ee795c2240e72efa79ed7f13776e50fc4c475cea8ab06092df9df8f1');
assert.equal(sha256(expectedBytes), '88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce');
assert.equal(sha256(sourceReceipt), 'a62bec02a53ca7cbe82bfe1408bc39c3693635771d2fffd622f9d1d1d7b40e46');
assert.equal(sha256(manifest), '2e980ee70e8aaf9b960c76716f352329ef6cadc2fe3f96b3b70a405a7c3fd163');
assert.equal(original.toString().split(from).length - 1, 1);
assert.equal(transformed.toString(), original.toString().replace(from, to));
assert(!transformed.toString().includes('process.nextTick'));
assert(!transformed.toString().includes('builtinFactory'));
const sealed = JSON.parse(expectedBytes);
assert.equal(sealed.groups, 19);
const originalObserved = await originalChecks(stream, promises, Buffer);
const transformedObserved = await portableChecks(stream, promises, Buffer);
assert.equal(originalObserved.length, 19);
assert.deepEqual(originalObserved, sealed.expected);
assert.deepEqual(transformedObserved, originalObserved);
const inputs = [
  ['../../implementation-candidate-v1/checks.mjs', original],
  ['./checks.mjs', transformed],
  ['../../implementation-candidate-v1/node-final-acceptance-results.json', expectedBytes],
  ['../../implementation-candidate-v1/source-receipt.json', sourceReceipt],
  ['../../implementation-candidate-v1/export-manifest.classic-streams.node-v22.14.0.json', manifest],
  ['./node-oracle.mjs', await readFile(new URL('./node-oracle.mjs', import.meta.url))],
];
const result = {
  schemaVersion: 1,
  status: 'NODE22_ONLY_EXACT_SINGLE_WAIT_TRANSFORM_PASSED',
  node: process.version,
  versions: process.versions,
  nodeExecutable: process.execPath,
  nodeExecutableSha256: sha256(await readFile(process.execPath)),
  transform: { occurrenceCount: 1, from, to, byteExactReplacementVerified: true,
    scope: 'Wait for public stream completion after early iterator return; swallow its expected destruction rejection. No scheduler substitute.' },
  sourceInputs: inputs.map(([path, bytes]) => ({ path, sha256: sha256(bytes), bytes: bytes.length })),
  groupCount: originalObserved.length,
  originalObserved,
  transformedObserved,
  originalMatchesSealedNodeExpected: true,
  transformedMatchesOriginal: true,
  candidateImplementationExecuted: false,
  guestSchedulerExecuted: false,
  nativeEngineExecuted: false,
  componentizerLoaded: false,
  componentOrTargetHostExecuted: false,
  futureComponentTemplatesExecuted: false,
  actualFutureEnginePins: null,
};
await writeFile(new URL('./node-oracle-results.json', import.meta.url), JSON.stringify(result, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify({ status: result.status, groupCount: result.groupCount, transformedSha256: sha256(transformed) }));
