// No guest/bootstrap/native action at import or in the read-only admission.
import {lstat,realpath} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,regular,need,sha} from '../ownership-component-candidate-v1/authority.mjs';
import {sourceIndex} from '../ownership-component-candidate-v3/guard.mjs';
import {indexed,deepFreeze} from '../ownership-component-candidate-v1/proofs.mjs';
import {streamHash} from '../ownership-component-candidate-v1/packaging.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export const OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-runtime-v1';
export const COMPONENT='842f82e8ae330580bee2d160880b5a3a35aac7c9baf357938814ecf2237a149d';
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function authorityModel(v,digest){
 sha(digest);need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_CRYPTO_OWNER355_NORMAL_RUNTIME_V1'&&v.action==='normal-runtime'&&v.sourceIndexSha256===digest,'New exact runtime source/action');
 need(v.normalRuntimeAllowed===true&&v.nodeOracleAllowed===true&&v.variant==='normal-off'&&v.outputRoot===OUTPUT&&v.componentSha256===COMPONENT,'Only actual guarded normal component');
 need(v.workerTimeoutMs===600000&&v.scenarios?.join(',')==='retained,fresh,wrapper','Finite three-worker ordinary schedule');
 for(const key of ['gcAllowed','oomAllowed','resetAllowed','otherVariantsAllowed','wasmtimeAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim'])need(v[key]===false,'No extra authority '+key);
 need(v.sourceIndependentReview?.index&&v.sourceIndependentReview?.result&&v.actualArtifactReview?.index&&v.actualArtifactReview?.result&&v.actualArtifactContract,'Separate actual artifact/source proofs');return true;
}
export function environment(env=process.env){for(const key of ['NODE_OPTIONS','NODE_PATH','JCO_DEBUG','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE'])need(!env[key],'No inherited loader override '+key);return true;}
export async function runtimePreflight(input){
 const configRow=descriptor(input),config=deepFreeze(JSON.parse(await regular(configRow))),sourceSha=sha(config.sourceIndexSha256),rootRow=descriptor(config.rootAction),root=deepFreeze(JSON.parse(await regular(rootRow)));authorityModel(root,sourceSha);environment();
 const ownRow=descriptor({path:join(HERE,'index.json'),sha256:sourceSha,bytes:(await lstat(join(HERE,'index.json'))).size}),own=await sourceIndex(ownRow);
 const peer=await indexed(root.sourceIndependentReview,{state:'INDEPENDENT_CRYPTO_OWNER355_RUNTIME_SOURCE_REVIEW_PASSED_V1'});need(peer.data.sourceIndexSha256===sourceSha&&peer.data.sourceOnly===true&&peer.data.sourceReviewPassed===true&&peer.data.ownerActionsInvoked===false,'Independent runtime source review only');
 const refsRow=own.rows.find(r=>r.path===join(HERE,'references.json')),refs=deepFreeze(JSON.parse(await regular(refsRow))),freezeRow=own.rows.find(r=>r.path===join(HERE,'input-freeze.json')),freeze=deepFreeze(JSON.parse(await regular(freezeRow)));
 need(freeze.schemaVersion===1&&Array.isArray(freeze.files)&&freeze.files.length>12000&&freeze.files.length<20000,'Complete finite source/native/tool/artifact closure');
 const artifact=await indexed(root.actualArtifactReview,{state:'INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_ARTIFACT_REVIEW_PASSED_V1'});need(artifact.data.verifiedPassed===true&&artifact.data.componentSourceIndexSha256===refs.componentSourceIndex.sha256&&artifact.data.componentSha256===COMPONENT&&artifact.data.generatedModuleImported===false&&artifact.data.keyOperationsInvoked===false,'Actual completed component proof, not source/borrowed codec approval');
 const contractRow=descriptor(root.actualArtifactContract);need(artifact.rows.filter(r=>equal(r,contractRow)).length===1,'Exact stable artifact contract indexed once');const contract=deepFreeze(JSON.parse(await regular(contractRow)));need(equal(contract.artifacts,refs.artifacts),'Whole actual named artifact tuple unchanged');
 need(refs.artifacts.component.sha256===COMPONENT&&refs.engine.sha256==='36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05'&&refs.engine.bytes===10002820,'Only new source-guarded engine/component relation');
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===refs.node.path,'Pinned plain Node22.14 process');
 const all=freeze.files.map(descriptor);need(new Set(all.map(r=>r.path)).size===all.length,'Unique full input paths');
 const recheck=async()=>{await regular(configRow);await regular(rootRow);await own.recheck();await peer.recheck();await artifact.recheck();await regular(contractRow);for(const row of all){if(row.bytes>32*1024*1024)await streamHash(row);else await regular(row,{maxBytes:64*1024*1024});}await streamHash(refs.node);for(const row of Object.values(refs.artifacts))await regular(row,{maxBytes:64*1024*1024});};await recheck();
 return Object.freeze({parentAuditedActualComponent:true,sourceIndexSha256:sourceSha,configRow,rootAction:rootRow,node:descriptor(refs.node),artifacts:deepFreeze(structuredClone(refs.artifacts)),outputRoot:OUTPUT,workerTimeoutMs:root.workerTimeoutMs,recheck});
}
