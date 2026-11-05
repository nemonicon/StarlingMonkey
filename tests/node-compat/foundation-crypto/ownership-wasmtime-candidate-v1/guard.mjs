// Validation-only source. Imports no generated code and invokes no helper/guest.
import {lstat,realpath} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,regular,need,sha} from '../ownership-component-candidate-v1/authority.mjs';
import {sourceIndex} from '../ownership-component-candidate-v3/guard.mjs';
import {indexed,deepFreeze} from '../ownership-component-candidate-v1/proofs.mjs';
import {streamHash} from '../ownership-component-candidate-v1/packaging.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export const OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-wasmtime-v1';
export const COMPONENT='842f82e8ae330580bee2d160880b5a3a35aac7c9baf357938814ecf2237a149d';
export function authorityModel(v,digest){
 sha(digest);need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_CRYPTO_OWNER355_STOCK_WASMTIME_V1'&&v.action==='stock-wasmtime-validate'&&v.sourceIndexSha256===digest,'New exact stock-WT source/action');
 need(v.wasmtimeValidateAllowed===true&&v.variant==='normal-off'&&v.componentSha256===COMPONENT&&v.outputRoot===OUTPUT,'Only actual normal guarded component');
 need(v.freshProcesses===3&&v.invocation==='validate()'&&v.workerTimeoutMs===600000&&v.maxPipeBytes===16777216&&v.externalParentDeadlineSeconds===2400,'Three finite fresh zero-argument invocations');
 for(const key of ['nodeOracleAllowed','generatedJsAllowed','gcAllowed','oomAllowed','resetAllowed','otherVariantsAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim'])need(v[key]===false,'No additional authority '+key);
 need(v.sourceIndependentReview?.index&&v.sourceIndependentReview?.result,'Independent WT source review required');descriptor(v.externalController);return true;
}
export function environment(env=process.env){
 for(const key of ['NODE_OPTIONS','NODE_PATH','JCO_DEBUG','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','RUST_LOG','RUST_BACKTRACE'])need(!env[key],'No inherited execution override '+key);
 for(const key of Object.keys(env))need(!key.startsWith('WASMTIME_'),'No inherited Wasmtime override '+key);return true;
}
export async function wasmtimePreflight(input){
 const configRow=descriptor(input),config=deepFreeze(JSON.parse(await regular(configRow))),sourceSha=sha(config.sourceIndexSha256),rootRow=descriptor(config.rootAction),root=deepFreeze(JSON.parse(await regular(rootRow)));authorityModel(root,sourceSha);environment();
 const ownRow=descriptor({path:join(HERE,'index.json'),sha256:sourceSha,bytes:(await lstat(join(HERE,'index.json'))).size}),own=await sourceIndex(ownRow);
 const peer=await indexed(root.sourceIndependentReview,{state:'INDEPENDENT_CRYPTO_OWNER355_WASMTIME_SOURCE_REVIEW_PASSED_V1'});need(peer.data.sourceIndexSha256===sourceSha&&peer.data.sourceOnly===true&&peer.data.sourceReviewPassed===true&&peer.data.ownerActionsInvoked===false,'Exact source peer is not action authority');
 const refsRow=own.rows.find(r=>r.path===join(HERE,'references.json')),refs=deepFreeze(JSON.parse(await regular(refsRow))),freezeRow=own.rows.find(r=>r.path===join(HERE,'input-freeze.json')),freeze=deepFreeze(JSON.parse(await regular(freezeRow)));
 const normal=await indexed(refs.normalReview,{state:'INDEPENDENT_CRYPTO_OWNER355_NORMAL_RUNTIME_RESULTS_REVIEW_PASSED_V1'}),artifact=await indexed(refs.artifactReview,{state:'INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_ARTIFACT_REVIEW_PASSED_V1'});
 for(const [key,expected]of [['normalReview',refs.normalReview],['normalContract',refs.normalContract],['artifactReview',refs.artifactReview],['artifactContract',refs.artifactContract]])need(equal(root[key],expected),'Exact historical prerequisite '+key);
 const normalContractRow=descriptor(refs.normalContract),artifactContractRow=descriptor(refs.artifactContract);
 need(normal.rows.filter(r=>equal(r,normalContractRow)).length===1&&artifact.rows.filter(r=>equal(r,artifactContractRow)).length===1,'Both immutable contracts indexed exactly once');
 const nc=deepFreeze(JSON.parse(await regular(normalContractRow))),ac=deepFreeze(JSON.parse(await regular(artifactContractRow)));
 need(nc.requiredReviewState===normal.data.state&&ac.requiredReviewState===artifact.data.state,'Exact contract states');
 for(const [proof,contract]of [[normal,nc],[artifact,ac]])for(const [key,value]of Object.entries(contract.requiredFixedValues))need(equal(proof.data[key],value),'Whole prerequisite fixed value '+key);
 need(equal(normal.data.coverage,nc.requiredCoverage)&&equal(nc.artifacts,ac.artifacts)&&equal(refs.artifacts,ac.artifacts),'Whole actual coverage and artifact tuple unchanged');
 need(ac.requiredFixedValues.publicAbiFunctions.validate==='() -> string'&&equal(ac.requiredFixedValues.emittedImports,[]),'Actual zero-argument string validate ABI and unchanged imports[]');
 need(normal.data.verifiedPassed===true&&normal.data.generatedModuleImported===true&&normal.data.asyncGuestScalarObservedAsOrdinaryStrings===true&&normal.data.stockWasmtimeExecuted===false&&normal.data.gcExecuted===false,'Completed normal fixture; no WT/GC proof relabel');
 need(artifact.data.verifiedPassed===true&&artifact.data.componentSha256===COMPONENT&&artifact.data.generatedModuleImported===false&&artifact.data.keyOperationsInvoked===false,'Separate prior construction proof retains its scope');
 need(refs.artifacts.component.sha256===COMPONENT&&refs.artifacts.engine.sha256==='36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05'&&refs.artifacts.engine.bytes===10002820,'Exact guarded normal355 engine/component');
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===refs.node.path,'Pinned plain parent Node22');
 need(freeze.schemaVersion===1&&Array.isArray(freeze.files)&&freeze.files.length>13000&&freeze.files.length<20000,'Finite complete inherited input closure');const all=freeze.files.map(descriptor);need(new Set(all.map(r=>r.path)).size===all.length,'Unique inherited contexts');
 const controller=descriptor(root.externalController),oracleRow=descriptor(refs.nodeOracle),wrapperRow=descriptor(refs.normalWrapper),oracle=deepFreeze(JSON.parse(await regular(oracleRow))),wrapper=deepFreeze(JSON.parse(await regular(wrapperRow)));
 need(equal(oracleRow,nc.requiredExactDescriptors.nodeOracle)&&nc.requiredExactDescriptors.actualIndex.sha256===refs.normalOutputIndex.sha256,'Actual normal oracle/output index binding');
 const normalIndex=JSON.parse(await regular(refs.normalOutputIndex));need(normalIndex.files.filter(r=>r.path==='wrapper/raw/001.json'&&r.sha256===wrapperRow.sha256&&r.bytes===wrapperRow.bytes).length===1,'Whole normal fresh-wrapper raw record indexed once');
 need(wrapper.name==='validate'&&equal(wrapper.args,[])&&wrapper.kind==='return'&&wrapper.returnedType==='string'&&typeof wrapper.value==='string','Actual normal wrapper is a complete zero-argument string');
 const recheck=async()=>{await regular(configRow);await regular(rootRow);await regular(controller);await own.recheck();await peer.recheck();await normal.recheck();await artifact.recheck();await regular(normalContractRow);await regular(artifactContractRow);for(const row of all){if(row.bytes>32*1024*1024)await streamHash(row);else await regular(row,{maxBytes:64*1024*1024});}await streamHash(refs.node);await streamHash(refs.wasmtime);for(const row of Object.values(refs.artifacts))await regular(row,{maxBytes:64*1024*1024});await regular(oracleRow);await regular(wrapperRow);};await recheck();
 return Object.freeze({sourceIndexSha256:sourceSha,rootAction:rootRow,node:descriptor(refs.node),wasmtime:descriptor(refs.wasmtime),component:descriptor(refs.artifacts.component),artifacts:refs.artifacts,oracle,normalWrapper:wrapper,outputRoot:OUTPUT,workerTimeoutMs:root.workerTimeoutMs,maxPipeBytes:root.maxPipeBytes,recheck});
}
