// Read/hash-only admission. No process, generated code, oracle or guest at import.
import {lstat,realpath} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,regular,need,sha} from '../ownership-component-candidate-v1/authority.mjs';
import {sourceIndex} from '../ownership-gc-component-candidate-v1/guard.mjs';
import {indexed,deepFreeze} from '../ownership-component-candidate-v1/proofs.mjs';
import {streamHash} from '../ownership-component-candidate-v1/packaging.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export const OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-gc-wasmtime-v1';
export const COMPONENT='52d99f4e95860b686d896c88f39b2fa5734eabeb433f48545ba814b2e45ce5f1';
export function authorityModel(v,digest){
 sha(digest);need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_CRYPTO_OWNER355_GC_STOCK_WASMTIME_V1'&&v.action==='stock-wasmtime-validate'&&v.sourceIndexSha256===digest,'New exact GC stock-WT source/action');
 need(v.wasmtimeValidateAllowed===true&&v.publicBufferGcPressureAllowed===true&&v.boundedKeyFixtureAllowed===true&&v.variant==='gc-off'&&v.componentSha256===COMPONENT&&v.outputRoot===OUTPUT,'Actual reviewed GC component fixture only');
 need(v.freshProcesses===3&&v.invocation==='validate()'&&v.workerTimeoutMs===600000&&v.maxPipeBytes===16777216&&v.externalParentDeadlineSeconds===2400,'Three fresh literal zero-argument calls');
 for(const key of ['nodeOracleAllowed','generatedJsAllowed','oomAllowed','resetAllowed','unsafePrototypeProbesAllowed','otherVariantsAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','nativeGcCountObservedClaim','isolatedRootClaim','nativeFreeOrWipeClaim'])need(v[key]===false,'No additional authority '+key);
 need(v.sourceIndependentReview?.index&&v.sourceIndependentReview?.result&&v.jcoGcReview?.index&&v.jcoGcReview?.result&&v.jcoGcContract,'Independent source+actual Jco GC prerequisite required');descriptor(v.externalController);return true;
}
export function environment(env=process.env){
 for(const key of ['NODE_OPTIONS','NODE_PATH','JCO_DEBUG','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','RUST_LOG','RUST_BACKTRACE'])need(!env[key],'No inherited execution override '+key);
 for(const key of Object.keys(env))need(!key.startsWith('WASMTIME_'),'No inherited Wasmtime override '+key);return true;
}
export function jcoModel(proof,refs){
 need(proof.schemaVersion===1&&proof.state==='INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_RESULTS_REVIEW_PASSED_V2'&&proof.verifiedPassed===true,'Actual independent GC Jco-v2 results, not source proposal');
 need(proof.sourceIndexSha256===refs.gcRuntimeSourceIndex.sha256&&proof.componentSha256===COMPONENT&&proof.nativeEngineSha256==='289df4455b56b50a9598c42a7d924aaa2adca7f5461f96782f5758a979e966c8'&&proof.nativeSourceFiles===355,'Exact GC source/component/native tuple');
 need(proof.generatedModuleImported===true&&proof.stockWasmtimeExecuted===false&&proof.publicBufferPressureFixtureExecuted===true&&proof.actualNativeGcCountObserved===false,'Actual Jco fixture boundary; no WT/native-GC count transfer');
 const c=proof.coverage;need(c.rawPublicStrings===23&&c.runRecords===20&&c.guestKeyImports===10&&c.guestSignAttempts===55&&c.guestVerifyAttempts===50&&equal(c.publicGcPressureRequests,{retained:48,fresh:16,wrapper:16,total:80})&&c.fullWrapperPressureRecords===16,'Full fixed Jco-v2 corpus and pressure scope');
 need(proof.operationalAdmission===false&&proof.runtimeAcceptanceClaim===false,'No operational authority');return true;
}
export async function wasmtimePreflight(input){
 const configRow=descriptor(input),config=deepFreeze(JSON.parse(await regular(configRow))),sourceSha=sha(config.sourceIndexSha256),rootRow=descriptor(config.rootAction),root=deepFreeze(JSON.parse(await regular(rootRow)));authorityModel(root,sourceSha);environment();
 const ownRow=descriptor({path:join(HERE,'index.json'),sha256:sourceSha,bytes:(await lstat(join(HERE,'index.json'))).size}),own=await sourceIndex(ownRow);
 const peer=await indexed(root.sourceIndependentReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_WASMTIME_SOURCE_REVIEW_PASSED_V1'});need(peer.data.sourceIndexSha256===sourceSha&&peer.data.sourceOnly===true&&peer.data.sourceReviewPassed===true&&peer.data.ownerActionsInvoked===false,'Source proof only');
 const refs=deepFreeze(JSON.parse(await regular(own.rows.find(r=>r.path===join(HERE,'references.json'))))),freeze=deepFreeze(JSON.parse(await regular(own.rows.find(r=>r.path===join(HERE,'input-freeze.json')))));
 const jco=await indexed(root.jcoGcReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_RESULTS_REVIEW_PASSED_V2'}),artifact=await indexed(refs.artifactReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'});jcoModel(jco.data,refs);
 const jcRow=descriptor(root.jcoGcContract),acRow=descriptor(refs.artifactContract);need(jco.rows.filter(r=>equal(r,jcRow)).length===1&&artifact.rows.filter(r=>equal(r,acRow)).length===1,'Exact indexed contracts once');
 const jc=deepFreeze(JSON.parse(await regular(jcRow))),ac=deepFreeze(JSON.parse(await regular(acRow)));need(jc.schemaVersion===1&&jc.requiredReviewState===jco.data.state&&ac.schemaVersion===1&&ac.requiredReviewState===artifact.data.state,'Exact current contract roles');
 for(const [proof,contract]of [[jco,jc],[artifact,ac]])for(const [key,value]of Object.entries(contract.requiredFixedValues))need(equal(proof.data[key],value),'Whole prerequisite fixed value '+key);
 need(equal(jco.data.coverage,jc.requiredCoverage)&&equal(jc.artifacts,ac.artifacts)&&equal(refs.artifacts,ac.artifacts),'Full coverage and actual12 artifact map unchanged');
 need(artifact.data.verifiedPassed===true&&artifact.data.componentSourceIndexSha256===refs.componentSourceIndex.sha256&&artifact.data.componentSha256===COMPONENT&&artifact.data.generatedModuleImported===false&&artifact.data.keyOperationsInvoked===false&&artifact.data.gcPressureCallsInvoked===false,'Construction proof remains construction-only');
 need(equal(artifact.data.emittedImports,[])&&equal([...artifact.data.publicAbiFunctions].sort(),['clear','inspect','run','validate'])&&refs.artifacts.component.bytes===13118152,'Actual zero-import four-function scalar component');
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===refs.node.path,'Pinned plain parent Node22');
 need(freeze.schemaVersion===1&&Array.isArray(freeze.files)&&freeze.files.length>10000&&freeze.files.length<30000,'Complete finite inherited source/native/tool closure');const all=freeze.files.map(descriptor);need(new Set(all.map(r=>r.path)).size===all.length,'Unique original contexts');
 const controller=descriptor(root.externalController),exact=jc.requiredExactDescriptors,oracleRow=descriptor(exact.nodeOracle),wrapperRow=descriptor(exact.rawWrapper),jcoIx=descriptor(exact.actualIndex),oracle=deepFreeze(JSON.parse(await regular(oracleRow))),wrapper=deepFreeze(JSON.parse(await regular(wrapperRow)));
 need(equal(jco.data.nodeOracle,oracleRow)&&equal(jco.data.actualIndex,jcoIx),'Whole actual Jco index/oracle binding');need(jcoIx.path==='/private/tmp/starling-node-compat/crypto-owner355-gc-runtime-v2/index.json'&&wrapperRow.path===join(dirname(jcoIx.path),'wrapper/raw/001.json'),'Exact actual v2 Jco output context');
 const jcoIndex=JSON.parse(await regular(jcoIx));need(jcoIndex.files.filter(r=>r.path==='wrapper/raw/001.json'&&r.sha256===wrapperRow.sha256&&r.bytes===wrapperRow.bytes).length===1,'Actual complete Jco wrapper indexed once');
 need(wrapper.name==='validate'&&equal(wrapper.args,[])&&wrapper.kind==='return'&&wrapper.returnedType==='string'&&typeof wrapper.value==='string','Actual full zero-argument Jco scalar string');
 const expectedRecord=deepFreeze(JSON.parse(await regular(refs.expectedCompleteRecord)));need(expectedRecord.schemaVersion===2&&expectedRecord.gcObservation.publicGcPressureRequests===16&&expectedRecord.gcObservation.actualNativeGcCountObserved===false,'Whole sealed GC typed expected DATA');
 const recheck=async()=>{await regular(configRow);await regular(rootRow);await regular(controller);await own.recheck();await peer.recheck();await jco.recheck();await artifact.recheck();await regular(jcRow);await regular(acRow);for(const row of all){if(row.bytes>32*1024*1024)await streamHash(row);else await regular(row,{maxBytes:64*1024*1024});}await streamHash(refs.node);await streamHash(refs.wasmtime);for(const row of Object.values(refs.artifacts))await regular(row,{maxBytes:64*1024*1024});await regular(oracleRow);await regular(wrapperRow);await regular(jcoIx);await regular(refs.expectedCompleteRecord);};await recheck();
 return Object.freeze({sourceIndexSha256:sourceSha,rootAction:rootRow,node:descriptor(refs.node),wasmtime:descriptor(refs.wasmtime),component:descriptor(refs.artifacts.component),artifacts:refs.artifacts,oracle,jcoWrapper:wrapper,expectedRecord,outputRoot:OUTPUT,workerTimeoutMs:root.workerTimeoutMs,maxPipeBytes:root.maxPipeBytes,recheck});
}
