// Extract pure guard/record functions only; do not import or call the real API.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import vm from 'node:vm';
const HERE=dirname(fileURLToPath(import.meta.url)),checks=[];
assert.equal(process.version,'v22.14.0');
const code=await readFile(join(HERE,'retained-bootstrap.mjs'),'utf8');
const begin=code.indexOf('function deepFreeze'),end=code.indexOf('async function inspectTree');
assert(begin>0&&end>begin);
const pure=code.slice(begin,end).replaceAll('export function ','function ');
const {validateHistorical,makeRetainedRecord}=vm.runInNewContext(pure+'\n({validateHistorical,makeRetainedRecord});',{same:isDeepStrictEqual,need:(v,m)=>assert(v,m)});
const test=(v,n)=>{assert(v,n);checks.push(n);};
const refuses=(fn,n)=>{assert.throws(fn);checks.push(n);};
const d=n=>({path:'/PURE/'+n,sha256:'a'.repeat(64),bytes:1});
const contexts=Object.fromEntries(['originalToolingRoot','configuredSourceRoot','sourceRoot','frozenRoot','componentizeSourceRoot','workRoot','enginePath'].map(k=>[k,'/PURE/'+k]));
const refs={engine:d('engine'),metadata:d('metadata'),freezeReceipt:d('receipt'),toolingIndex:d('historical-tooling'),reviewedPins:d('pins'),rootPinReview:d('pin-review'),historicalContexts:contexts};
const metadata={sourceManifest:Array.from({length:355},()=>({})),componentizeSourceManifest:[{},{},{}],gcStress:false,entropyPolicy:'off',oomTesting:false};
for(let i=0;Object.keys(metadata).length<75;i++)metadata['pure'+i]=i;
const manifests=Array.from({length:11},(_,i)=>({modules:{['pure'+i]:{}}}));
const pin={state:'reviewed-secret-owner355-normal-off-pin-v3',reviewRequired:false};
const pins={schemaVersion:3,state:'ROOT_REVIEWED_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PINS_V3',reviewRequired:false,variants:{'normal-off':pin,'normal-runtime':null,'gc-off':null,'disabled-off':null}};
const frame={schemaVersion:3,state:'SECRET_OWNER355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V3',variant:'normal-off',pin,metadata,selectedManifests:manifests,selectedManifestCount:11,nativeSourceFiles:355,externalEmbeddingSources:3,validationBootstrapOnly:true,currentCompleteVerifierCalls:1,engine:refs.engine,metadataDescriptor:refs.metadata,freezeReceipt:refs.freezeReceipt,toolingIndex:refs.toolingIndex,reviewedPins:refs.reviewedPins,rootPinReview:refs.rootPinReview,...contexts,verifierFrame:{runtimeBackendProof:{verified:false,version:null,vernum:null}},engineExecuted:false,guestExecuted:false,operationalAdmission:false,runtimeAcceptanceClaim:false,grantsRuntimeAuthority:false};
for(let i=0;Object.keys(frame).length<41;i++)frame['pure'+i]=i;
validateHistorical(frame,pins,metadata,manifests,refs);checks.push('synthetic whole historical guard accepts');
for(const [name,mutate]of[
 ['field-count',f=>f.extra=true],['state',f=>f.state='projected'],['variant',f=>f.variant='gc-off'],['native-count',f=>f.nativeSourceFiles=342],['embedding-count',f=>f.externalEmbeddingSources=0],['manifest-count',f=>f.selectedManifestCount=9],['frame-metadata',f=>f.metadata.pure0='changed'],['historical-count',f=>f.currentCompleteVerifierCalls=0],['engine',f=>f.engine.path='/PURE/wrong'],['context',f=>f.sourceRoot='/PURE/wrong'],['backend-proof',f=>f.verifierFrame.runtimeBackendProof.verified=true],['runtime-flag',f=>f.operationalAdmission=true]]){
 const f=structuredClone(frame);mutate(f);refuses(()=>validateHistorical(f,pins,metadata,manifests,refs),'refuses '+name);
}
for(const name of ['normal-runtime','gc-off','disabled-off']){const p=structuredClone(pins);p.variants[name]={};refuses(()=>validateHistorical(frame,p,metadata,manifests,refs),'other variant refuses '+name);}
let calls=0;const freshOwn=async()=>{calls++;};
const current={helperInvocations:0,originalApiInvocations:0,historicalRecheckInvocations:0,processesSpawned:0,filesCreated:0};
const record=makeRetainedRecord({sourceIndex:d('new-source'),actualReview:{index:d('review-index'),result:d('review-result')},historicalBootstrap:frame,currentVerification:current,recheck:freshOwn});
test(record.kind==='retained-secret355-bootstrap-v1'&&record.schemaVersion===1,'new finite record kind');
test(record.historicalBootstrap===frame&&record.historicalBootstrap.currentCompleteVerifierCalls===1,'historical object retained unchanged');
test(!Object.hasOwn(record,'state')&&!Object.hasOwn(record,'currentCompleteVerifierCalls')&&!Object.hasOwn(record,'metadata'),'no historical spread or admission decoration');
test(Object.values(record.currentVerification).every(v=>v===0),'current helper/API/process/write counts zero');
test(record.recheck===freshOwn&&calls===0,'own callable retained but not invoked');
test(Object.isFrozen(record)&&Object.isFrozen(record.historicalBootstrap.metadata)&&Object.isFrozen(record.currentVerification),'new and full historical DATA deeply frozen');
refuses(()=>makeRetainedRecord({sourceIndex:{},actualReview:{},historicalBootstrap:{},currentVerification:{},recheck:null}),'noncallable fresh recheck refuses');
test(!/from ['"]node:child_process/.test(code)&&!code.includes('execFile(')&&!code.includes('spawn(')&&!code.includes('await import('),'no process or operational import seam');
test(!code.includes('async function write(')&&!code.includes('mkdir(')&&!code.includes('open('),'no file writer/output creator');
test(code.includes('finally{')&&code.includes('await verifyCurrent();')&&code.includes('new AggregateError([primary,error]'),'primary and final protection failures retained');
test(code.includes("inputs.files.length>=28000")&&code.includes('for(const r of inputs.files)await c.file(r)')&&code.includes('for(const ix of inputs.families)await c.family(ix)'),'full own input/family intake');
test(code.includes('root.readOnlyVerificationAllowed===true')&&code.includes("root.phase==='verify-retained'")&&code.includes('sourcePeer.sourceIndexSha256===own.sha256'),'new explicit Root/Source gate');
test(code.includes('const recheck=async()=>{await verifyCurrent();need(same(historical,await c.read(refs.historicalBootstrap))'),'fresh closure only reads/hashes full context');
const result={schemaVersion:1,state:'SOURCE_ONLY_RETAINED_BOOTSTRAP_PURE_MODELS_PASSED_V1',checks:checks.length,checkNames:checks,syntheticDataOnly:true,actualPreflightImportedOrInvoked:false,historicalApiOrHelperOrRecheckInvoked:false,ownRealRecheckInvoked:false,processesSpawned:0};
await writeFile(join(HERE,'pure-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({checks:checks.length,sourceOnly:true,actualApiCalls:0}));
