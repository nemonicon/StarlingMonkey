// Read/hash admission only. No bootstrap, generated import or crypto operation at import.
import {lstat,realpath} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,regular,need,sha} from '../ownership-component-candidate-v1/authority.mjs';
import {sourceIndex} from '../ownership-gc-component-candidate-v1/guard.mjs';
import {captureFutureGcArtifact} from '../ownership-gc-component-candidate-v1/artifact-guard.mjs';
import {indexed,deepFreeze} from '../ownership-component-candidate-v1/proofs.mjs';
import {streamHash} from '../ownership-component-candidate-v1/packaging.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export const OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-gc-runtime-v1';
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function authorityModel(v,digest){
 sha(digest);need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_CRYPTO_OWNER355_GC_RUNTIME_V1'&&v.action==='gc-runtime'&&v.sourceIndexSha256===digest,'New exact GC runtime source/action');
 need(v.gcRuntimeAllowed===true&&v.nodeOracleAllowed===true&&v.publicBufferGcPressureAllowed===true&&v.boundedKeyFixtureAllowed===true&&v.variant==='gc-off'&&v.outputRoot===OUTPUT,'Only new GC fixture action');
 sha(v.componentSha256);need(v.engineSha256==='289df4455b56b50a9598c42a7d924aaa2adca7f5461f96782f5758a979e966c8'&&v.guestSourceIndexSha256==='7988586f2aef2d6ee651dfb2978dc34cc756e796181e8c69d77fff085ee888b0','Actual GC native and reviewed fixture identities');
 need(v.workerTimeoutMs===600000&&v.scenarios?.join(',')==='retained,fresh,wrapper','Finite three fresh owned sessions');
 for(const k of ['oomAllowed','resetAllowed','unsafePrototypeProbesAllowed','otherVariantsAllowed','wasmtimeAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','nativeGcCountObservedClaim','isolatedRootClaim','nativeFreeOrWipeClaim'])need(v[k]===false,'No additional authority '+k);
 need(v.sourceIndependentReview?.index&&v.sourceIndependentReview?.result&&v.actualArtifactReview?.index&&v.actualArtifactReview?.result&&v.actualArtifactContract,'Exact new source+GC artifact proofs');return true;
}
export function environment(env=process.env){for(const key of ['NODE_OPTIONS','NODE_PATH','JCO_DEBUG','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE'])need(!env[key],'No inherited loader override '+key);return true;}
export async function runtimePreflight(input){
 const configRow=descriptor(input),config=deepFreeze(JSON.parse(await regular(configRow))),sourceSha=sha(config.sourceIndexSha256),rootRow=descriptor(config.rootAction),root=deepFreeze(JSON.parse(await regular(rootRow)));authorityModel(root,sourceSha);environment();
 const ownRow=descriptor({path:join(HERE,'index.json'),sha256:sourceSha,bytes:(await lstat(join(HERE,'index.json'))).size}),own=await sourceIndex(ownRow);
 const peer=await indexed(root.sourceIndependentReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_SOURCE_REVIEW_PASSED_V1'});need(peer.data.sourceIndexSha256===sourceSha&&peer.data.sourceOnly===true&&peer.data.sourceReviewPassed===true&&peer.data.ownerActionsInvoked===false,'Source peer is not an action grant');
 const refs=deepFreeze(JSON.parse(await regular(own.rows.find(r=>r.path===join(HERE,'references.json'))))),freeze=deepFreeze(JSON.parse(await regular(own.rows.find(r=>r.path===join(HERE,'input-freeze.json')))));
 need(freeze.schemaVersion===1&&Array.isArray(freeze.files)&&freeze.files.length>8000&&freeze.files.length<30000,'Complete finite source/native/tool DATA closure');
 const artifact=await captureFutureGcArtifact({artifactReview:root.actualArtifactReview,componentSourceIndexSha256:refs.componentSourceIndex.sha256});
 need(artifact.proofData.componentSha256===root.componentSha256&&artifact.proofData.engineSha256===refs.engineSha256&&artifact.proofData.generatedModuleImported===false&&artifact.proofData.keyOperationsInvoked===false&&artifact.proofData.gcPressureCallsInvoked===false,'New actual GC component construction proof only');
 const artifactIndex=await indexed(root.actualArtifactReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'}),contractRow=descriptor(root.actualArtifactContract);need(artifactIndex.rows.filter(r=>equal(r,contractRow)).length===1,'Stable actual GC contract indexed once');
 const contract=deepFreeze(JSON.parse(await regular(contractRow)));need(contract.schemaVersion===1&&equal(contract.artifacts,artifact.proofData.artifacts),'Whole actual GC artifact tuple, not normal projected paths');
 const artifacts=deepFreeze(structuredClone(artifact.proofData.artifacts));need(artifacts.component.sha256===root.componentSha256,'Exact actual binary');
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===refs.node.path,'Pinned plain Node22.14 runtime');
 const all=freeze.files.map(descriptor);need(new Set(all.map(r=>r.path)).size===all.length,'Unique original-context inputs');
 const expectedRecord=deepFreeze(JSON.parse(await regular(refs.expectedCompleteRecord)));need(expectedRecord.schemaVersion===2&&expectedRecord.kind==='crypto-owner-within-export-gc-validation-v2'&&expectedRecord.gcObservation.publicGcPressureRequests===16&&expectedRecord.gcObservation.actualNativeGcCountObserved===false,'Whole sealed typed GC expected record');
 const recheck=async()=>{await regular(configRow);await regular(rootRow);await own.recheck();await peer.recheck();await artifact.recheck();await artifactIndex.recheck();await regular(contractRow);for(const row of all){if(row.bytes>32*1024*1024)await streamHash(row);else await regular(row,{maxBytes:64*1024*1024});}await streamHash(refs.node);for(const row of Object.values(artifacts))await regular(row,{maxBytes:64*1024*1024});await regular(refs.expectedCompleteRecord);};await recheck();
 return Object.freeze({parentAuditedActualComponent:true,sourceIndexSha256:sourceSha,configRow,rootAction:rootRow,node:descriptor(refs.node),artifacts,expectedRecord,outputRoot:OUTPUT,workerTimeoutMs:root.workerTimeoutMs,recheck});
}
