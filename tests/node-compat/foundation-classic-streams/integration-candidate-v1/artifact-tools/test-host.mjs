// Pure classifier/pin refusal tests only. Never call admit() or load an engine.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {classify,RECIPE,LABELS} from './metadata-admission.mjs';
import {selectClassicPin} from '../runtime-contract.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const results=[];const test=(name,fn)=>{fn();results.push({name,passed:true});};
const base={buildRecipeSha256:RECIPE,gcStress:false,entropyPolicy:'off',classicStreamsEnabled:true,
 ...Object.fromEntries(['profileEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled'].map(name=>[name,true])),
 oomTesting:false,debuggerEnabled:false,wptSupportEnabled:false};
for(const label of LABELS){const gcStress=label==='gc-off',entropyPolicy=label==='normal-runtime'?'runtime-only':'off',classicStreamsEnabled=label!=='disabled-off';
 test('pure-classify-'+label,()=>assert.deepEqual(classify({...base,gcStress,entropyPolicy,classicStreamsEnabled},label),{gcStress,entropyPolicy,classicStreamsEnabled}));}
for(const[name,change]of [['old306',{buildRecipeSha256:'869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'}],['synthetic',{syntheticMetadataOnly:true}],['diagnostic',{diagnosticOnly:true}],['diagnostic-null',{diagnosticOnly:null}],['diagnostic-policy',{internalTickDiagnosticPolicy:{}}],['wrong-classic',{classicStreamsEnabled:false}],['wrong-gc',{gcStress:true}],['wrong-entropy',{entropyPolicy:'runtime-only'}],['missing-foundation',{utilEnabled:false}],['missing-ticks',{internalTicksEnabled:false}]])
 test('classify-reject-'+name,()=>assert.throws(()=>classify({...base,...change},'normal-off')));
for(const label of LABELS){
 const variants=Object.fromEntries(LABELS.map(name=>[name,null]));
 test('unreviewed-pin-'+label,()=>assert.throws(()=>selectClassicPin({schemaVersion:1,state:'UNREVIEWED_CLASSIC_PRODUCTION_PIN_CANDIDATES_V1',variants},{variant:label,recipeSha256:RECIPE})));
 test('null-reviewed-pin-'+label,()=>assert.throws(()=>selectClassicPin({schemaVersion:1,state:'REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1',variants},{variant:label,recipeSha256:RECIPE})));}
const parent=JSON.parse(await readFile(new URL('./parent-inputs.json',import.meta.url)));test('preserved-five-parent-files',()=>assert.equal(parent.files.length,5));
const output=process.env.NODE_COMPAT_CLASSIC_ARTIFACT_JS_TEST_OUTPUT??new URL('./js-test-results.json',import.meta.url);
await writeFile(output,JSON.stringify({state:'PURE_CLASSIFIER_AND_PIN_REFUSAL_TESTS_PASSED',tests:results.length,passed:results.length,results,
 metadataAdmissionExecuted:false,artifactToolMainExecuted:false,engineOrGuestExecuted:false,actualPins:null},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({tests:results.length,passed:results.length,engineOrGuestExecuted:false}));
