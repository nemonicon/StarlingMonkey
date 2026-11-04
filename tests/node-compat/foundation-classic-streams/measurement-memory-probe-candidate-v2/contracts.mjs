// Pure finite descriptor validation. No files, proofs, native or guest imports.
import assert from 'node:assert/strict';
export const SHA=/^[0-9a-f]{64}$/;
export const phaseSha='a822a7b02e0b81aae15504dd90d439be789c884336bfab7a7eddcccc0aec6890';
export const timingSha='eded2bdba1703712682fab9a0c8e93dd6a80a5551b3b6c727028729df62f1f65';
export const timingRootSha='fc51ab670f64745453f5a23fb399b9e8ea36a7327ed05460e618505922bd5e55';
export const integritySha='3843d019f0976310f982e1b964bdcd2a09e8c85960e755214a89a03ac8117644';
export const timingSourceSha='78b3e5a0e3389f3d347a9b5700852361aae59cdbdc26813d9ff290f8ddf3e538';
export const instantiateSha='0b9d3cee8d40160a9fa0c56165e60d6a8ef57e10a9c722069f30d5f162c3492b';
export const comparisons=[{id:'same-engine-binding',arms:['native-on','canonical-on']},{id:'whole-profile',arms:['canonical-on','canonical-off']},{id:'different-stock-provider',arms:['canonical-on','stock-on']}];
export const tuples={
 'native-on':['9786b3b98f2a6addedcbd9d63bd94ff103194c6badcf87f927b47a9be24c6cb5',13056344,'8c1c8bdfb64a8b0f60624dbb564490ad8bbe56b39c6a99f000ba0f280fa3ae05',13055500],
 'canonical-on':['a571e13de091953aa5e575425c7b24b126b0004738c807a7377160728673680f',14168969,'0bfdde58a4b28e949f429db8b86150aed18265befee1f545d7f0356d141a6882',14168125],
 'canonical-off':['f658138d215bc84ec8bd85c747e06ce155653e93aa46b25a9b1f653eaa14e206',13449990,'cd6e4c14bdd8bb9f4f57299e209040b01df20be84f1113dbd052c467930d34d8',13449146],
 'stock-on':['da72a27dcf0fd84f8fccd1c23e2bbe327abde03af95e0d7633f40478278dcadb',16487001,'d0f5f35c1acbe37d49f9cda171fc6b5b50282b8ddc151cc6c7eaa59495c08f03',16486157]};
export const artifactRoot=arm=>'/tmp/starling-node-compat/'+(arm==='stock-on'?'production-common-byte-stock-only-v1':'production-common-byte-correctness-v2')+'/'+arm;
export const packageFile=arm=>({path:artifactRoot(arm).slice(0,-arm.length)+'package.json',sha256:'1239d4d885dcad42201a27ed9324f8f0f760b78700d8db9ced39a511cffe7eae',bytes:18});
export const orderFor=(repetition,pair)=>repetition===1?[...pair].reverse():[...pair];
export const schedule=()=>comparisons.flatMap(comparison=>[0,1,2].flatMap(repetition=>orderFor(repetition,comparison.arms).map((arm,position)=>({comparison:comparison.id,repetition,runOrder:orderFor(repetition,comparison.arms),position,arm}))));
const keys=(value,names)=>{assert(value&&typeof value==='object'&&!Array.isArray(value));assert.deepEqual(Object.keys(value).sort(),[...names].sort());};
function rawJson(value,max){assert.equal(typeof value,'string');assert(Buffer.byteLength(value)<=max);const parsed=JSON.parse(value);assert.equal(JSON.stringify(parsed),value,'Canonical expected JSON only');return parsed;}
export function validateDescriptor(d){
 keys(d,['schemaVersion','state','sourceIndexSha256','parentPhaseSha256','arm','comparison','repetition','runOrder','position','component','modulePath','coreFiles','criticalFiles','expected','nativeEvidence']);
 assert.equal(d.schemaVersion,1);assert.equal(d.state,'PARENT_AUTHENTICATED_SMALL_MEMORY_WORKER_INPUT_V2');assert(SHA.test(d.sourceIndexSha256));assert.equal(d.parentPhaseSha256,phaseSha);
 const scheduled=schedule().filter(row=>row.arm===d.arm&&row.comparison===d.comparison&&row.repetition===d.repetition&&row.position===d.position);assert.equal(scheduled.length,1);assert.deepEqual(d.runOrder,scheduled[0].runOrder);
 const tuple=tuples[d.arm],root=artifactRoot(d.arm);assert(tuple);assert.equal(d.modulePath,root+'/common_byte.js');assert.deepEqual(d.coreFiles,['common_byte.core.wasm']);
 keys(d.component,['path','sha256','bytes']);assert.deepEqual(d.component,{path:root+'/common-byte.component.wasm',sha256:tuple[0],bytes:tuple[1]});
 assert.deepEqual(d.criticalFiles,[d.component,{path:root+'/common_byte.core.wasm',sha256:tuple[2],bytes:tuple[3]},
  {path:root+'/common_byte.js',sha256:'747296bc080f83a7a97657224a6aff71cfeaff124a47d4266c5c65124d99a53c',bytes:133860},
  {path:root+'/common_byte.d.ts',sha256:'e6e5d4c3d021092d6a6b662c6235f34987eca59672915aa18ab0e1618f3defe8',bytes:2209},packageFile(d.arm)]);
 keys(d.expected,['identityRaw','probeRaw','cases']);rawJson(d.expected.identityRaw,4096);rawJson(d.expected.probeRaw,1024);assert.equal(d.expected.cases.length,2);
 for(const [i,index] of [1,5].entries()){
  const row=d.expected.cases[i];keys(row,['index','iterations','setupReturn','batchRaw','units']);assert.equal(row.index,index);assert.equal(row.iterations,1);requireS32(row.setupReturn);assert.equal(row.setupReturn,index===1?151852933:-1502831163,'Pinned Node setup result');
  const expected=rawJson(row.batchRaw,2048);assert.equal(expected.result.iterations,1);assert.equal(expected.result.totalUnits,index===1?8192:4194304);assert.equal(row.units,expected.result.totalUnits);assert.deepEqual(expected.result.records,[]);
 }
 keys(d.nativeEvidence,['engineSha256','metadataSha256','notLoadedByWorker']);assert.equal(d.nativeEvidence.notLoadedByWorker,true);
 assert.equal(d.nativeEvidence.engineSha256,d.arm==='canonical-off'?'4e1f62ea9ee192e1f288e4f5f6bc1e8ea5f3b259e8ae56527930cf90c1a72d94':'12a8f7dc79e12e8bc3519b3fe72e898b226bbabde6930e63d3a6c30706b88274');assert.equal(d.nativeEvidence.metadataSha256,d.arm==='canonical-off'?'eed24cdf9e35f4ee194342d25e64197c6278829ce533a01b7ddc3506799a4af3':'f2f67947631136647259b7ba40422d6fb89fe943b1b74d2db4c5754bbfcc2c31');
 assert(Buffer.byteLength(JSON.stringify(d))<=16384);return structuredClone(d);
}
export function validateAuthority(value,ownSha){
 keys(value,['schemaVersion','state','sourceIndexSha256','memorySupplementAllowed','throughputReplacement','runtimeAcceptanceClaim','phase','timingReport','timingRootReceipt','integrityIndex']);
 assert.equal(value.schemaVersion,1);assert.equal(value.state,'ROOT_REVIEWED_COMMON_BYTE_PROCESS_RSS_SUPPLEMENT_V2');assert.equal(value.sourceIndexSha256,ownSha);assert(SHA.test(ownSha));assert.equal(value.memorySupplementAllowed,true);
 assert.equal(value.throughputReplacement,false);assert.equal(value.runtimeAcceptanceClaim,false);
 for(const [name,sha256] of Object.entries({phase:phaseSha,timingReport:timingSha,timingRootReceipt:timingRootSha,integrityIndex:integritySha})){
  keys(value[name],['path','sha256']);assert.equal(value[name].sha256,sha256);assert.equal(typeof value[name].path,'string');assert(value[name].path.startsWith('/')&&!value[name].path.includes('\0')&&value[name].path.length<=1024);
 }
 return structuredClone(value);
}
export function requireS32(value){assert.equal(typeof value,'number','setup public ABI is signed32 number');assert(Number.isInteger(value)&&value>=-2147483648&&value<=2147483647,'setup must be finite signed32');return value;}
export function requirePublicReturn(name,actual,expected){
 if(name==='setup'){requireS32(actual);requireS32(expected);assert.equal(actual,expected,'Exact signed32 setup result');return;}
 assert(['identity','checkpointProbe','batch'].includes(name),'Unknown public scalar');assert.equal(typeof actual,'string');assert.equal(typeof expected,'string');
 if(JSON.stringify(JSON.parse(actual))!==expected)throw new Error('Public string JSON mismatch: '+name+' (whole raw return retained)');
}
export function buildExpectedCases(oracle,compactExpected){
 return[1,5].map(index=>{const compact=compactExpected(oracle,index,1);return{index,iterations:1,setupReturn:requireS32(oracle[index].setup),batchRaw:JSON.stringify(compact),units:compact.result.totalUnits};});
}
export function buildDescriptor({sourceIndexSha256,row,record,expectedCases,native}){
 const component={path:record.componentPath,sha256:record.componentSha256,bytes:record.componentBytes};
 return validateDescriptor({schemaVersion:1,state:'PARENT_AUTHENTICATED_SMALL_MEMORY_WORKER_INPUT_V2',sourceIndexSha256,parentPhaseSha256:phaseSha,...row,component,modulePath:record.modulePath,coreFiles:record.coreFiles,
  criticalFiles:[component,...['common_byte.core.wasm','common_byte.js','common_byte.d.ts'].map(name=>{const f=record.transpiledFiles.find(f=>f.name===name);assert(f);return{path:artifactRoot(row.arm)+'/'+name,sha256:f.sha256,bytes:f.bytes};}),packageFile(row.arm)],
  expected:{identityRaw:JSON.stringify(record.identity),probeRaw:JSON.stringify(record.checkpointProbe),cases:expectedCases},nativeEvidence:{...native,notLoadedByWorker:true}});
}
