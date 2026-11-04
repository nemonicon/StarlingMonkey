// Host-side assertions for the explicit entropy HTTP fixture.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const oracle = JSON.parse(readFileSync(new URL('./owned-input-node-results.json', import.meta.url))).cases;
export function checkEntropyHTTPReport(body, audit) {
  if (!audit.entropyIntegrationFixture) return;
  const report = body.native.entropyIntegration;
  const policy = audit.entropyPolicy;
  assert.equal(report.policy, policy);
  const expectedCode = policy === 'off' ? 'ERR_SM_ENTROPY_DISABLED' : 'ERR_SM_ENTROPY_INITIALIZATION';
  assert.equal(report.snapshot.length, 4);
  assert(report.snapshot.every(entry => entry.code === expectedCode));
  assert.equal(report.snapshotHash, 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  assert.equal(report.secure.policy, policy);
  assert.deepEqual(report.ownership, oracle);
  if (policy === 'runtime-only') {
    assert.match(report.secure.bytes, /^[a-f0-9]{64}$/);
    assert.equal(report.rsa.type, 'public');
    assert.equal(report.rsa.modulusLength, 2048);
  } else {
    for (const name of ['getRandomValues', 'randomUUID', 'objectURL', 'multipart']) assert.equal(report.secure[name].code, expectedCode);
  }
}
export function checkEntropyHTTPSamples(responses, audit) {
  if (!audit.entropyIntegrationFixture || audit.entropyPolicy !== 'runtime-only') return;
  const samples = responses.map(response => response.body.native.entropyIntegration.secure.bytes);
  assert.equal(new Set(samples).size, samples.length, 'Detect obvious replay across deployed requests/instances');
}
