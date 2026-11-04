// Declaration gate only; source models are never positive artifact evidence.
import assert from 'node:assert/strict';
import {isAbsolute,resolve} from 'node:path';
export const PRODUCER_INDEX='46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc';
export const RECIPE='d98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6';
export function selectActivation(document){
 assert(document&&typeof document==='object');assert.equal(document.schemaVersion,1);
 assert.equal(document.state,'ROOT_REVIEWED_CLASSIC_DIAGNOSTIC_CORRECTNESS_ACTIVATION_V1','Actual diagnostic-v3 Root authority remains unconfigured');
 assert.equal(document.variant,'benchmark-classic-on');assert.equal(document.producerIndexSha256,PRODUCER_INDEX);assert.equal(document.recipeSha256,RECIPE);
 assert.equal(document.timingAllowed,false);assert.equal(document.runtimeAcceptanceClaim,false);
 for(const key of ['producerRoot','sourceRoot','reviewedPinsPath'])assert(typeof document[key]==='string'&&isAbsolute(document[key])&&!document[key].includes('\0')&&resolve(document[key])===document[key],key);
 assert(/^[a-f0-9]{64}$/.test(document.reviewedPinsSha256));assert(document.reviewedActualEngine&&typeof document.reviewedActualEngine==='object');
 assert.equal(document.reviewedActualEngine.diagnosticOnly,true);assert.equal(document.reviewedActualEngine.sourceFiles,342);assert.equal(document.reviewedActualEngine.addonFiles,2);
 return structuredClone(document);
}
