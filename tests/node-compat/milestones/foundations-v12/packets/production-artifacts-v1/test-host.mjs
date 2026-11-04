// Pure classifier/selector rejection checks. No metadata admission main or loader.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {classify,RECIPE} from './metadata-admission.mjs';
import {selectActualPin as selectOff} from '../production-regression-candidate-v4/admission.mjs';
import {selectActualPin as selectCapability} from '../production-followon-capability-v2/admission.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const results=[];
function test(name,fn){fn();results.push({name,passed:true});}
const base={buildRecipeSha256:RECIPE,gcStress:false,entropyPolicy:'off'};
for(const [label,gcStress,entropyPolicy]of[['normal-off',false,'off'],['normal-runtime',false,'runtime-only'],['gc-off',true,'off']])
 test('pure-label-coherence-'+label,()=>assert.deepEqual(classify({...base,gcStress,entropyPolicy},label),{gcStress,entropyPolicy}));
for(const [name,change]of[['diagnostic',{diagnosticOnly:true}],['diagnostic-null',{diagnosticOnly:null}],['diagnostic-policy',{internalTickDiagnosticPolicy:{}}],['old-recipe',{buildRecipeSha256:'0'.repeat(64)}],['wrong-gc',{gcStress:true}],['wrong-entropy',{entropyPolicy:'runtime-only'}]])
 test(name+'-rejected-before-engine',()=>assert.throws(()=>classify({...base,...change},'normal-off')));
test('no-runtime-gc-label',()=>assert.throws(()=>classify(base,'gc-runtime')));
for(const path of['/tmp/starling-node-compat/foundations-v11/native-freeze/off-foundations.engine.wasm.build.json','/tmp/starling-node-compat/foundation-scheduler-link1-v1/native-freeze/diagnostic-release.engine.wasm.build.json']){
 const metadata=JSON.parse(await readFile(path));test('actual-old-metadata-'+path,()=>assert.throws(()=>classify(metadata,'normal-off')));
}
const candidate={schemaVersion:1,state:'UNREVIEWED_PRODUCTION_PIN_CANDIDATES_V1',variants:{'normal-off':null,'normal-runtime':null,'gc-off':null}};
test('unreviewed-export-not-off-admitted',()=>assert.throws(()=>selectOff(candidate,{gcStress:false})));
test('unreviewed-export-not-gc-admitted',()=>assert.throws(()=>selectOff(candidate,{gcStress:true})));
test('unreviewed-export-not-runtime-admitted',()=>assert.throws(()=>selectCapability(candidate,{gcStress:false,entropyPolicy:'runtime-only'})));
for(const [selector,document]of[[selectOff,{...candidate,state:'REVIEWED_REAL_PRODUCTION_FREEZES_V1'}],[selectCapability,{...candidate,state:'REVIEWED_REAL_PRODUCTION_CAPABILITY_FREEZES_V1'}]])
 test('null-actual-pins-still-rejected-'+document.state,()=>assert.throws(()=>selector(document,{gcStress:false})));
const output=process.env.NODE_COMPAT_ARTIFACT_JS_TEST_OUTPUT??fileURLToPath(new URL('./js-test-results.json',import.meta.url));
await writeFile(output,JSON.stringify({state:'PURE_CLASSIFIER_AND_UNREVIEWED_SELECTOR_NEGATIVES_PASSED',tests:results.length,passed:results.length,failures:0,results,
 actualProductionFreezeValidated:false,engineBytesRead:false,nativeOrGuestExecuted:false,pinCandidateCreated:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({tests:results.length,passed:results.length,output,nativeOrGuestExecuted:false}));
