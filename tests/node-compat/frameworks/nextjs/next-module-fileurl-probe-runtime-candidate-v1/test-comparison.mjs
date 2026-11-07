// Synthetic JSON DATA only; never imports collector, guest, fixtures or a Node control.
import assert from 'node:assert/strict';
import {validateGuardResponse} from './comparison.mjs';
const code = 'ERR_SM_MODULE_IMPORT_REFERRER';
const valid = {schemaVersion: 1, suite: 'REAL_COMPONENT_CJS_FILE_URL_PROBE_V1', mode: 'guard', call: 1,
  caseCount: 2, expectedCaseCount: 2, exactCaseIds: true, profilePassed: true,
  guardRefusalIsNodeCompatibilityPass: false, nodeReferenceExecuted: false, applicationImported: false,
  fullNextClaim: false, namespaceLimit8192Exercised: false, symlinkReentrancyRealmOrRaceParityProved: false,
  records: [{id: 'cjs-dynamic-builtin', passed: true, observation: {sameJoin: true, joined: '/probe/child'}},
    {id: 'guard-natural-fileurl-refusal', passed: true, observation: {rejected: true, isTypeError: true,
      code, operation: 'module_load_hook', moduleMatchesActualSpecifier: true,
      error: {type: 'object', isNull: false, code: {type: 'string', value: code},
        operation: {type: 'string', value: 'module_load_hook'},
        module: {type: 'string', value: 'file:///probe/target.cjs'}}}}]};
let checks = 0;
assert.deepEqual(validateGuardResponse(valid), {guardProfileMatched: true, builtinDynamicImportObserved: true,
  selectedReferrerRefusalObserved: true, nodeCompatibilityAccepted: false}); checks++;
for (const mutate of [
  x => { x.mode = 'interop'; }, x => { x.call = 2; }, x => { x.schemaVersion = true; },
  x => { x.caseCount = true; }, x => { x.expectedCaseCount = 1; }, x => { x.exactCaseIds = false; },
  x => { x.profilePassed = false; }, x => { x.records.reverse(); }, x => { x.records.pop(); },
  x => { x.records[0].passed = 1; }, x => { x.records[0].error = null; },
  x => { x.records[0].observation.sameJoin = 1; }, x => { x.records[0].observation.joined = '/wrong'; },
  x => { x.records[1].observation.rejected = false; }, x => { x.records[1].observation.isTypeError = 1; },
  x => { x.records[1].observation.code = 'TypeError'; },
  x => { x.records[1].observation.operation = 'module_metadata_hook'; },
  x => { x.records[1].observation.moduleMatchesActualSpecifier = false; },
  x => { x.records[1].observation.error.code.value = 'ERR_SM_MODULE_FILE_URL_UNSUPPORTED'; },
  x => { x.records[1].observation.error.module.value = 'file:///other.cjs'; },
  x => { x.records[1].observation.error.type = 'string'; },
  x => { x.records[1].observation.error.isNull = true; },
  x => { x.nodeReferenceExecuted = true; }, x => { x.guardRefusalIsNodeCompatibilityPass = true; },
  x => { x.fullNextClaim = true; }, x => { x.applicationImported = true; },
  x => { x.namespaceLimit8192Exercised = true; }, x => { x.symlinkReentrancyRealmOrRaceParityProved = true; },
]) {
  const changed = structuredClone(valid); mutate(changed);
  assert.throws(() => validateGuardResponse(changed)); checks++;
}
for (const value of [null, [], false, 1, 'not JSON object']) {
  assert.throws(() => validateGuardResponse(value)); checks++;
}
console.log(JSON.stringify({sourceDataOnly: true, passed: true, checks, syntheticFramesOnly: true,
  collectorOrGuestOrFixtureImported: false, actualProbeExecuted: false, nodeControlExecuted: false}));
