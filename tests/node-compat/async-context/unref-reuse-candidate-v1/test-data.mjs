import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateUnrefCollection} from './validation.mjs';
import {unrefPublicProjection} from './cases.mjs';
const contract=JSON.parse(await readFile(new URL('./future-runtime-contract.json',import.meta.url)));
const frames=(await readFile(new URL('./node-oracle.stdout.jsonl',import.meta.url),'utf8')).trim().split('\n').map(JSON.parse);
const clone=x=>JSON.parse(JSON.stringify(x));let checks=0;
for(const row of frames.filter(x=>x.kind==='whole-call')){
 const v=row.observed;assert.equal(validateUnrefCollection(v,v.phase,v.firstHostCase,v.boundaryMode,contract),true);checks++;
 const guest=clone(v);guest.boundaryMode='actual-native-private-boundaries';guest.firstHostCase=guest.requestedHostCase='synthetic-shape-only';
 assert.equal(validateUnrefCollection(guest,v.phase,'synthetic-shape-only','actual-native-private-boundaries',contract),true);checks++;
 assert.deepEqual(unrefPublicProjection(v),unrefPublicProjection(guest));checks++;
 for(const change of [x=>delete x.boundaryMode,x=>x.firstHostCase='other',x=>x.ordinal=0,x=>x.passed=false,
  x=>x.coverage='inconclusive-callback-before-B-entry',x=>x.physicalStoreOrNativeOwnerIdentityProved=true,
  x=>x.checks=[],x=>x.checks.pop(),x=>x.checks.push({id:'extra',passed:true}),x=>x.checks[0].passed=false,
  x=>x.observations[0].firstIdentity=false,x=>x.observations[0].firstLabel='wrong',x=>x.counts.candidate=1,
  x=>x.plannedHandles.peak=9,x=>x.plannedHandles.clearErrors.push({name:'test'}),x=>x.unknownScope=false]){
  const bad=clone(v);change(bad);assert.throws(()=>validateUnrefCollection(bad,v.phase,v.firstHostCase,v.boundaryMode,contract));checks++;
 }
 assert.throws(()=>validateUnrefCollection(v,v.phase,v.firstHostCase,v.boundaryMode,undefined));checks++;
}
console.log(JSON.stringify({passed:true,pureDataChecks:checks,actualOracleReexecuted:false,nativeOrGuestExecuted:false,
 syntheticNativeShapeOnly:true,sourceAdmissionBeforeReuseRequired:true,nodeProjectionOnlyAfterAllThreeBodies:true}));
