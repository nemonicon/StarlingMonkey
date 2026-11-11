// Differential check of bounded, already captured observations. No hosts are started.
import assert from 'node:assert/strict';
import { readFile, open } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { isDeepStrictEqual } from 'node:util';
import { compareWebStreamContextReports } from '../web-stream-context-component-v1/compare.mjs';

assert.equal(process.version, 'v22.14.0');
assert.equal(process.argv.length, 10,
  'node compare-results.mjs NODE_CONTEXT NODE_CLONE NODE_FOLLOWUPS GUEST_CONTEXT_1 GUEST_CLONE GUEST_FOLLOWUPS GUEST_CONTEXT_2 OUTPUT');
const refs = [];
async function read(path) {
  const bytes = await readFile(path);
  assert(bytes.length <= 128 * 1024, 'Bounded observation file');
  refs.push({ path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') });
  return JSON.parse(bytes);
}
const [nodeContext, nodeClone, nodeFollowups, first, clone, followups, last] = await Promise.all(process.argv.slice(2, 9).map(read));
assert.equal(nodeClone.nodeVersion, 'v22.14.0');
assert.equal(nodeClone.captureCompleted, true); assert.equal(nodeClone.timedOut, false);
assert.equal(nodeClone.observation.collectionComplete, true);
assert.equal(nodeClone.observation.sourceCancelCalls, 1);
assert.equal(nodeClone.observation.sourceCancelReasons[0].firstElementIsFirstObject, true);
assert.equal(nodeClone.observation.sourceCancelReasons[0].secondElementIsSecondObject, true);

function contextComparison(envelope) {
  const shape = envelope?.schemaVersion === 1 && envelope.marker === 'PUBLIC_ALS_WEB_STREAM_COMPONENT_V1' &&
    envelope.route === '/context' && envelope.primarySet === false && envelope.fullNextAccepted === false;
  const refusal = envelope?.publicAsyncResourceRefusal;
  const typedRefusal = refusal?.facadeInstalled === false && refusal.namedAndDefaultConstructorSame === true &&
    refusal.passed === true && Array.isArray(refusal.records) && refusal.records.length === 2 &&
    isDeepStrictEqual(refusal.records.map(row => row.binding), ['named', 'default']) &&
    refusal.records.every(row => row.passed === true && row.constructorType === 'function' && row.threw === true &&
      row.errorIsError === true && row.code === 'ERR_SM_NODE_UNSUPPORTED' && row.module === 'node:async_hooks' &&
      row.operation === 'AsyncResource' && row.profile === 'sm-node-22.14.0-m1.0');
  const comparison = compareWebStreamContextReports(nodeContext, envelope?.collection ?? null);
  return { shape, typedRefusal, comparison, passed: shape && typedRefusal && comparison.passed };
}
const contexts = [contextComparison(first), contextComparison(last)];
const cloneCollected = clone?.schemaVersion === 1 && clone.marker === 'RESPONSE_CLONE_CANCEL_COMPONENT_OBSERVATION_V1' &&
  clone.route === '/clone-cancel' && clone.collectionComplete === true && clone.primarySet === false &&
  clone.collection?.collectionComplete === true && clone.fullNextAccepted === false;
const cloneMatches = cloneCollected && isDeepStrictEqual(nodeClone.observation, clone.collection);
assert.equal(nodeFollowups.nodeVersion, 'v22.14.0');
assert.equal(nodeFollowups.suite, 'NODE_RESPONSE_CLONE_CANCEL_FOLLOWUP_OBSERVATION_V1');
assert.equal(nodeFollowups.captureCompleted, true); assert.equal(nodeFollowups.timedOut, false);
assert.equal(nodeFollowups.observation.collectionComplete, true);
const followupsCollected = followups?.schemaVersion === 1 &&
  followups.marker === 'RESPONSE_CLONE_CANCEL_FOLLOWUP_COMPONENT_OBSERVATION_V1' &&
  followups.route === '/clone-cancel-followups' && followups.collectionComplete === true &&
  followups.primarySet === false && followups.collection?.collectionComplete === true &&
  followups.fullNextAccepted === false;
const followupsMatch = followupsCollected && isDeepStrictEqual(nodeFollowups.observation, followups.collection);
const result = { schemaVersion: 1, state: 'CLONE_CANCEL_COMPONENT_NODE_DIFFERENTIAL_V2',
  nodeVersion: process.version, inputFiles: refs.sort((a, b) => a.path.localeCompare(b.path)),
  contexts, clone: { collected: cloneCollected, allSharedObservationFieldsMatch: cloneMatches,
    nodeSourceCancelCalls: nodeClone.observation.sourceCancelCalls,
    guestSourceCancelCalls: clone.collection?.sourceCancelCalls ?? null,
    nodeSnapshots: nodeClone.observation.snapshots,
    guestSnapshots: clone.collection?.snapshots ?? null,
    nodeReasons: nodeClone.observation.sourceCancelReasons,
    guestReasons: clone.collection?.sourceCancelReasons ?? null,
    passed: cloneMatches },
  followups: { collected: followupsCollected, allSharedObservationFieldsMatch: followupsMatch,
    nodeObservation: nodeFollowups.observation, guestObservation: followups.collection ?? null,
    passed: followupsMatch },
  passed: contexts.every(row => row.passed) && cloneMatches && followupsMatch,
  actualNativeResourceRetirementProved: false, hostInstanceIdentityProved: false,
  fullNextAccepted: false, productionProfilePromoted: false };
const data = Buffer.from(JSON.stringify(result, null, 2) + '\n');
const file = await open(process.argv[9], 'wx', 0o600);
try { await file.writeFile(data); await file.sync(); }
finally { await file.close(); }
console.log(JSON.stringify({ passed: result.passed, contexts: contexts.map(row => row.passed),
  clone: cloneMatches, followups: followupsMatch, nodeSourceCancelCalls: result.clone.nodeSourceCancelCalls,
  guestSourceCancelCalls: result.clone.guestSourceCancelCalls }));
process.exitCode = result.passed ? 0 : 1;
