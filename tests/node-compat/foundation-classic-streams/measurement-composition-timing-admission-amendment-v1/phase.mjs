// Pure finite timing admission. No artifact, host or action imports.
import assert from 'node:assert/strict';
import {arms,protocol} from '../measurement-execution-activated-v2/protocol.mjs';
const SHA=/^[0-9a-f]{64}$/;
export function selectTimingPhase(value){
 assert(value&&typeof value==='object');assert.equal(value.schemaVersion,1);
 assert.equal(value.state,'ROOT_REVIEWED_COMPOSED_COMMON_BYTE_MEASUREMENT_INPUTS_V2');assert.equal(value.timingAllowed,true);
 assert.equal(value.sourceFamilyIndexSha256,'1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612');assert.equal(value.pairPinsSha256,'f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e');assert(SHA.test(value.timingAdmissionSourceIndexSha256));assert.equal(value.collectorSourceIndexSha256,'257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da');
 assert.equal(value.coordinatedWindow,'ROOT_EXPLICIT_SINGLE_MEASUREMENT_WINDOW');
 assert.deepEqual(Object.keys(value.components).sort(),[...arms].sort());
 for(const arm of arms){const r=value.components[arm];assert.equal(r.arm,arm);assert(SHA.test(r.componentSha256)&&SHA.test(r.engineSha256)&&SHA.test(r.bundleSha256));assert.deepEqual(r.emittedImports,[]);assert.equal(r.correctnessPassed,true);assert.equal(r.identityPassed,true);assert.equal(r.checkpointProbePassed,true);assert(Array.isArray(r.transpiledFiles)&&r.transpiledFiles.length>0);assert.equal(typeof r.modulePath,'string');}
 assert.equal(value.components['native-on'].engineSha256,value.components['canonical-on'].engineSha256);
 assert.equal(value.components['canonical-on'].engineSha256,value.components['stock-on'].engineSha256);
 assert.notEqual(value.components['canonical-on'].engineSha256,value.components['canonical-off'].engineSha256);
 assert.equal(value.components['canonical-on'].bundleSha256,value.components['canonical-off'].bundleSha256);
 for(const name of ['actualCorrectness','freshFull20And14','freshReplay','freshHttpBothHosts']){
  const r=value[name];assert(r&&typeof r==='object'&&r.reviewedPassed===true,name);assert(SHA.test(r.reportSha256)&&SHA.test(r.rootReviewSha256));assert.equal(typeof r.reportPath,'string');assert.equal(typeof r.rootReviewPath,'string');
 }
 assert.equal(value.freshFull20And14.workloadCases,20);assert.equal(value.freshFull20And14.boundaryCases,14);
 assert.equal(value.freshHttpBothHosts.sameBytes,true);assert.deepEqual(value.freshHttpBothHosts.requestsPerHost,[3,3]);assert.deepEqual(value.freshHttpBothHosts.stopCodes,[0,0]);assert.equal(value.freshHttpBothHosts.standardInterfaces,'6@0.2.10; clock duration type only');
 assert.deepEqual(value.protocol,protocol);return structuredClone(value);
}
