// Pure extracted checks + parser DATA only. Never imports an owner/generated module.
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const HERE=dirname(fileURLToPath(import.meta.url)),K=dirname(HERE),checks=[];
const check=(name,fn)=>{fn();checks.push({name,passed:true});},reject=(name,fn)=>check(name,()=>assert.throws(fn));
const refs=JSON.parse(await readFile(join(HERE,'references.json'),'utf8')),expected=JSON.parse(await readFile(refs.expectedCompleteRecord.path,'utf8'));
function stripped(s){return s.replace(/^import [^\n]*\n/gm,'').replace(/^export /gm,'');}
function fn(s,name){const start=s.indexOf('export function '+name+'(');assert(start>=0);let end=s.indexOf('\nexport ',start+1);if(end<0)end=s.length;return s.slice(start,end).replace('export function','function');}
const checksText=await readFile(join(HERE,'checks.mjs'),'utf8'),guardText=await readFile(join(HERE,'guard.mjs'),'utf8'),abiText=await readFile(join(K,'ownership-component-candidate-v1/abi.mjs'),'utf8'),loaderText=await readFile(join(HERE,'loading.mjs'),'utf8');
const context=vm.createContext({need:(v,m)=>assert(v,m),structuredClone,sha:v=>{assert.match(v,/^[a-f0-9]{64}$/);return v;},OUTPUT:'/private/tmp/starling-node-compat/crypto-owner355-gc-runtime-v2'});
vm.runInContext(stripped(checksText)+'\n'+fn(guardText,'authorityModel')+'\nthis.api={zeroCounters,nextRun,runRecord,inspectRecord,clearRecord,validateRecord,gcObservation,publicState,canonical,wholeEqual,authorityModel};',context,{timeout:1000});
const a=context.api,copy=x=>JSON.parse(JSON.stringify(x)),oracle={tagHex:'b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7'};
for(const scenario of ['retained','fresh']){
 let c=a.zeroCounters();c.inspectCalls++;const before=copy(expected.before);before.counters=c;check(scenario+' whole initial inspect DATA',()=>a.inspectRecord(before,c,false,false,expected));let requests=0;
 for(let rotation=0;rotation<(scenario==='retained'?3:1);rotation++)for(let id=0;id<4;id++){
  c=a.nextRun(c,id);const r=copy(expected.records[id]);r.counters=c;r.state=a.publicState(true,id!==0||c.keyImportsFulfilled>1);check(scenario+' rotation'+rotation+' case'+id+' complete record DATA',()=>a.runRecord(r,id,c,oracle,expected));requests+=r.gcObservation.publicGcPressureRequests;
 }
 c.clearCalls++;const clear=copy(expected.released);clear.counters=c;check(scenario+' whole clear DATA',()=>a.clearRecord(clear,c,expected));c.inspectCalls++;const after=copy(expected.after);after.counters=c;check(scenario+' whole final inspect DATA',()=>a.inspectRecord(after,c,false,false,expected));check(scenario+' exact scoped request total',()=>assert.equal(requests,scenario==='retained'?48:16));
}
check('whole schema2 wrapper DATA',()=>a.validateRecord(copy(expected),oracle,expected));
for(const [label,mutator]of [
 ['wrong full tag',v=>v.records[0].result.operations.firstSignatureHex='0'.repeat(64)],
 ['wrong retained tag',v=>v.records[2].result.jwk.secondSignatureHex='0'.repeat(64)],
 ['wrong key metadata',v=>v.records[1].result.operations.key.algorithm.length=128],
 ['wrong input sentinel',v=>v.records[0].result.operations.inputAfterHex='00'],
 ['altered refusal message',v=>v.records[3].result.signRefusal.error.message='different'],
 ['run3 pressure truthfulness',v=>v.records[3].gcObservation.publicGcPressureRequested=true],
 ['native count fabricated',v=>v.gcObservation.actualNativeGcCountObserved=true],
 ['wrong pressure bytes',v=>v.pressure.records[0].encodedHex='00'.repeat(64)],
 ['missing pressure record',v=>v.pressure.records.pop()],
 ['wrong phase order',v=>v.pressure.records[0].phase='after-verifies'],
 ['pressure attempt changed',v=>v.records[0].gcObservation.publicGcPressureRequests=3],
 ['unknown complete field',v=>v.unexpected=true],
 ['bool changed to number',v=>v.gcObservation.entropyRequested=0],
 ['partial record cannot be full success',v=>v.records[0].completed=false],
 ['operation observation reordering',v=>v.records[0].observations.reverse()],
 ['fresh wrapper counter mismatch',v=>v.entryCounters.runCalls=1]
]){const v=copy(expected);mutator(v);reject('reject '+label,()=>a.validateRecord(v,oracle,expected));}
const root=JSON.parse(await readFile(join(HERE,'future-root-authority.template.json'),'utf8')),source='a'.repeat(64);root.state='ROOT_REVIEWED_CRYPTO_OWNER355_GC_RUNTIME_V2';root.sourceIndexSha256=source;root.componentSha256='b'.repeat(64);root.gcRuntimeAllowed=root.nodeOracleAllowed=root.publicBufferGcPressureAllowed=root.boundedKeyFixtureAllowed=true;root.sourceIndependentReview={index:{},result:{}};root.actualArtifactReview={index:{},result:{}};root.actualArtifactContract={};check('future GC authority positive DATA',()=>a.authorityModel(root,source));
for(const k of ['oomAllowed','resetAllowed','unsafePrototypeProbesAllowed','otherVariantsAllowed','wasmtimeAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','nativeGcCountObservedClaim','isolatedRootClaim','nativeFreeOrWipeClaim']){const r=copy(root);r[k]=true;reject('authority refuses '+k,()=>a.authorityModel(r,source));}
for(const [k,v]of Object.entries({variant:'normal-off',engineSha256:'36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05',guestSourceIndexSha256:'0'.repeat(64),workerTimeoutMs:1,scenarios:['wrapper'],publicBufferGcPressureAllowed:false,boundedKeyFixtureAllowed:false,state:'ROOT_REVIEWED_CRYPTO_OWNER355_NORMAL_RUNTIME_V1',componentSha256:null})){const r=copy(root);r[k]=v;reject('wrong GC authority '+k,()=>a.authorityModel(r,source));}
// Only the pinned parser library is imported. The captured generated JS is DATA.
const parser={path:'/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain/node_modules/acorn/dist/acorn.mjs',sha256:'1cbcbf252a5800e496dc505c706f309a9dd4e1789392e12963c77ae9497ff6f7',bytes:232769},parserBytes=await readFile(parser.path);assert.equal(parserBytes.length,parser.bytes);assert.equal(createHash('sha256').update(parserBytes).digest('hex'),parser.sha256);const {parse}=await import(pathToFileURL(parser.path));
const lc=vm.createContext({need:(v,m)=>assert(v,m),Buffer});
vm.runInContext(stripped(abiText)+'\n'+stripped(loaderText).replace(/^\{PARSER\};\n/m,'')+'\nthis.audit={validateGlue,validateNamespace,scalarArguments};this.makeNamespace=()=>{const ns=Object.create(null);Object.assign(ns,{inspect:function(){},run:function(id){},clear:function(){},validate:function(){},_util:{}});return ns;};',lc,{timeout:1000});
const construction=JSON.parse(await readFile(join(K,'ownership-gc-component-v1-root-results.json'),'utf8')),glue=construction.artifacts.glue,bytes=await readFile(glue.path);assert.equal(bytes.length,glue.bytes);assert.equal(createHash('sha256').update(bytes).digest('hex'),glue.sha256);const ast=parse(bytes.toString('utf8'),{ecmaVersion:'latest',sourceType:'module'});check('actual new GC glue finite ESM/TLA AST DATA',()=>lc.audit.validateGlue(ast));
check('namespace finite DATA model',()=>lc.audit.validateNamespace(lc.makeNamespace()));const bad=lc.makeNamespace();bad.then=()=>{};reject('then namespace rejected',()=>lc.audit.validateNamespace(bad));
for(const args of [[-0],[-1],[4],['0'],[],[0,1]])reject('bad scalar run args '+JSON.stringify(args),()=>lc.audit.scalarArguments('run',args));
check('literal zero-arg validate model',()=>lc.audit.scalarArguments('validate',[]));reject('validate cannot take array argument',()=>lc.audit.scalarArguments('validate',[[]]));
process.stdout.write(JSON.stringify({schemaVersion:1,state:'EXTRACTED_GC_RUNTIME_DATA_MODELS_AND_STATIC_LOADER_PASSED_V1',checks,count:checks.length,sourceOnly:true,pinnedHostParserInvoked:true,parser,capturedGlue:glue,ownerModulesImported:false,generatedModuleImported:false,nodeOracleCalled:false,bootstrapCalled:false,keyOrPressureOperationsInvoked:false})+'\n');
