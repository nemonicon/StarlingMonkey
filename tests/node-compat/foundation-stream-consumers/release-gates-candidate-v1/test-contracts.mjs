// Pure contract/data checks only. No owner helper, package, Wasm or guest imports.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {assertFourPins,assertRuntimeAuthority,variantForScope,assertFrame,assertSourceTransition,assertConsumerPrerequisite} from './contracts.mjs';
const json=async url=>JSON.parse(await readFile(new URL(url,import.meta.url)));
let passed=0;const checks=[];
function check(name,fn){fn();passed++;checks.push(name);}
function refuses(name,fn){check(name,()=>assert.throws(fn));}
const pinsRaw=await readFile(new URL('../reviewed-native-v2-validation-bootstrap-pins-v2.json',import.meta.url)),pins=JSON.parse(pinsRaw),review=await json('../native-v2-validation-bootstrap-root-review-v2.json'),pinsSha=createHash('sha256').update(pinsRaw).digest('hex');
check('actual four native pin data match external review',()=>assertFourPins(pins,review,pinsSha));
const prerequisite=await json('./reviewed-consumer-validation.json');check('actual consumer prerequisite shape and qualified nested scope',()=>assertConsumerPrerequisite(prerequisite));
refuses('operational consumer prerequisite refuses',()=>{const value=structuredClone(prerequisite);value.scope.operationalAdmission=true;assertConsumerPrerequisite(value);});
for(const label of ['normal-off','normal-runtime','gc-off','disabled-off']){
 refuses(label+' NULL refuses',()=>{const value=structuredClone(pins);value.variants[label]=null;assertFourPins(value,review,pinsSha);});
 refuses(label+' wrong engine refuses',()=>{const value=structuredClone(pins);value.variants[label].engineSha256='0'.repeat(64);assertFourPins(value,review,pinsSha);});
 refuses(label+' unreviewed refuses',()=>{const value=structuredClone(pins);value.variants[label].reviewRequired=true;assertFourPins(value,review,pinsSha);});
}
refuses('wrong native review digest refuses',()=>assertFourPins(pins,review,'0'.repeat(64)));
const template=await json('./runtime-authority.template.json'),familyIndexSha256='a'.repeat(64),output='/tmp/starling-node-compat/production-consumers355-release-gates-v1/synthetic-not-created';
for(const scope of ['release-off','allocator-gc','focused-off','focused-runtime','focused-gc','getter'])refuses(scope+' NULL runtime authority refuses',()=>assertRuntimeAuthority(template,{familyIndexSha256,scope,output}));
const authority={...template,familyIndexSha256,consumerValidationSha256:'36964b2dff52497ed43ce89ec34dbec1610d03d180a477510189150907ded65b',scopes:{'release-off':{approved:true,variant:'normal-off',output,deadlineMs:7200000}}};
check('synthetic explicit bounded runtime authority shape',()=>assertRuntimeAuthority(authority,{familyIndexSha256,scope:'release-off',output}));
for(const [name,mutate]of [['unknown scope',a=>delete a.scopes['release-off']],['wrong variant',a=>a.scopes['release-off'].variant='normal-runtime'],['wrong output',a=>a.scopes['release-off'].output+='/other'],['over-budget',a=>a.scopes['release-off'].deadlineMs=7200001],['timing',a=>a.allowTiming=true],['build',a=>a.allowNativeBuild=true],['prior pass reuse',a=>a.noPriorPassReuse=false],['resume',a=>a.noResume=false],['operational',a=>a.operationalAdmission=true]])refuses(name+' authority refuses',()=>{const a=structuredClone(authority);mutate(a);assertRuntimeAuthority(a,{familyIndexSha256,scope:'release-off',output});});
refuses('wrong generated family index refuses',()=>assertRuntimeAuthority(authority,{familyIndexSha256:'b'.repeat(64),scope:'release-off',output}));
check('strict-runtime OFF is not runtime-only entropy',()=>assert.equal(variantForScope('release-off'),'normal-off'));
check('focused runtime uses separate actual runtime-only tuple',()=>assert.equal(variantForScope('focused-runtime'),'normal-runtime'));
refuses('unknown scope refuses',()=>variantForScope('http'));
const lineage=await json('./lineage.json');
for(const label of ['normal-off','normal-runtime','gc-off','disabled-off']){
 const raw=await readFile(pins.variants[label].enginePath+'.build.json'),metadata=JSON.parse(raw);
 check(label+' actual frozen metadata hash',()=>assert.equal(createHash('sha256').update(raw).digest('hex'),pins.variants[label].receiptSha256));
 check(label+' actual full355 ordered source rows',()=>assert.deepEqual(metadata.sourceManifest.map(({path,sha256})=>({path,sha256})),lineage.native355));
}
for(const [before,after]of [[306,342],[342,350],[350,355]]){
 check('actual complete source transition '+before+' -> '+after,()=>assertSourceTransition(lineage['native'+before],lineage['native'+after],lineage['delta'+after],lineage['added'+after]));
 refuses('changed undeclared source '+after,()=>{const rows=structuredClone(lineage['native'+after]);rows.find(row=>row.path==='builtins/node-compat/buffer.cpp').sha256='0'.repeat(64);assertSourceTransition(lineage['native'+before],rows,lineage['delta'+after],lineage['added'+after]);});
 refuses('missing source '+after,()=>assertSourceTransition(lineage['native'+before],lineage['native'+after].slice(1),lineage['delta'+after],lineage['added'+after]));
 refuses('duplicate source '+after,()=>assertSourceTransition(lineage['native'+before],[...lineage['native'+after],lineage['native'+after][0]],lineage['delta'+after],lineage['added'+after]));
}
const sourceRoot='/synthetic-frame-only',metadata={engineSha256:'0'.repeat(64),sourceManifest:lineage.native355},frame={metadata:structuredClone(metadata),sourceRoot,validationBootstrapOnly:true,operationalAdmission:false};
check('pure exact full355 frame comparison shape only',()=>assertFrame(metadata,sourceRoot,frame));
refuses('no captured genuine frame refuses',()=>assertFrame(metadata,sourceRoot,undefined));
refuses('projected342 subset refuses',()=>assertFrame({...metadata,sourceManifest:lineage.native342},sourceRoot,frame));
refuses('caller changed metadata refuses',()=>assertFrame({...metadata,diagnosticOnly:true},sourceRoot,frame));
refuses('wrong frozen source root refuses',()=>assertFrame(metadata,'/other',frame));
console.log(JSON.stringify({schemaVersion:1,state:'passed',checks:passed,names:checks,syntheticContractFixturesOnly:true,actualNativePinsReadAsData:true,ownerHelperImported:false,guestExecuted:false,sourcePublisherExecuted:false}));
