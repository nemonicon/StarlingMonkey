// Owned host-only selector checks. No pin files, artifacts or loaders are used.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {selectActualPin as common} from '../production-regression-candidate-v4/admission.mjs';
import {selectActualPin as capability} from '../production-followon-capability-v2/admission.mjs';
assert.equal(process.version,'v22.14.0');
const checks=[];
for(const [name,selector,state,variants,options] of [
 ['common',common,'REVIEWED_REAL_PRODUCTION_FREEZES_V1',{'normal-off':null,'gc-off':null},{gcStress:false}],
 ['capability',capability,'REVIEWED_REAL_PRODUCTION_CAPABILITY_FREEZES_V1',{'normal-off':null,'gc-off':null,'normal-runtime':null},{gcStress:false,entropyPolicy:'runtime-only'}]
]){
 for(const outer of ['UNREVIEWED_PRODUCTION_PIN_CANDIDATES_V1','UNCONFIGURED_ACTUAL_PRODUCTION_FREEZES_REQUIRED']){
  assert.throws(()=>selector({schemaVersion:1,state:outer,variants},options),/unconfigured/);
  checks.push({name:name+' rejects '+outer,passed:true});
 }
 const selected=name==='common'?'normal-off':'normal-runtime';
 assert.throws(()=>selector({schemaVersion:1,state,variants:{...variants,[selected]:{state:'unreviewed-production-freeze-pin-candidate'}}},options));
 checks.push({name:name+' rejects inner unreviewed candidate even with reviewed outer label',passed:true});
}
const report={state:'HOST_ONLY_UNREVIEWED_PIN_STATE_REJECTION_PASSED',tests:checks.length,checks,syntheticRejectionShapesOnly:true,actualArtifactSuccess:false,engineBytesRead:false,guestExecuted:false,pinFilesModified:false};
assert(process.env.NODE_COMPAT_REVIEW_REJECTION_OUTPUT);
await writeFile(process.env.NODE_COMPAT_REVIEW_REJECTION_OUTPUT,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:checks.length}));
