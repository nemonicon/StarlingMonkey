// Pure DATA validation, not a Node oracle or component execution attestation.
import assert from 'node:assert/strict';
export function validateGuardResponse(value) {
  assert(value && typeof value === 'object' && !Array.isArray(value));
  assert.equal(value.schemaVersion, 1);
  assert.equal(value.suite, 'REAL_COMPONENT_CJS_FILE_URL_PROBE_V1');
  assert.equal(value.mode, 'guard');
  assert.equal(value.call, 1);
  assert.equal(value.caseCount, 2);
  assert.equal(value.expectedCaseCount, 2);
  assert.equal(value.exactCaseIds, true);
  assert.equal(value.profilePassed, true);
  for (const key of ['guardRefusalIsNodeCompatibilityPass', 'nodeReferenceExecuted', 'applicationImported',
    'fullNextClaim', 'namespaceLimit8192Exercised', 'symlinkReentrancyRealmOrRaceParityProved'])
    assert.equal(value[key], false, key);
  assert(Array.isArray(value.records));
  assert.deepEqual(value.records.map(row => row.id), ['cjs-dynamic-builtin', 'guard-natural-fileurl-refusal']);
  for (const row of value.records) {
    assert.equal(row.passed, true);
    assert.equal(Object.hasOwn(row, 'error'), false);
    assert(row.observation && typeof row.observation === 'object' && !Array.isArray(row.observation));
  }
  assert.deepEqual(value.records[0].observation, {sameJoin: true, joined: '/probe/child'});
  const refusal = value.records[1].observation;
  assert.equal(refusal.rejected, true);
  assert.equal(refusal.isTypeError, true);
  assert.equal(refusal.code, 'ERR_SM_MODULE_IMPORT_REFERRER');
  assert.equal(refusal.operation, 'module_load_hook');
  assert.equal(refusal.moduleMatchesActualSpecifier, true);
  assert.equal(refusal.error.type, 'object');
  assert.equal(refusal.error.isNull, false);
  for (const [key, expected] of [['code', 'ERR_SM_MODULE_IMPORT_REFERRER'],
    ['operation', 'module_load_hook'], ['module', 'file:///probe/target.cjs']])
    assert.deepEqual(refusal.error[key], {type: 'string', value: expected});
  return {guardProfileMatched: true, builtinDynamicImportObserved: true,
    selectedReferrerRefusalObserved: true, nodeCompatibilityAccepted: false};
}
