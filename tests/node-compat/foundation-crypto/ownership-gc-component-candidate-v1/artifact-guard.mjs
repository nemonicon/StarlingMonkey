// Future artifact proof DATA only. No generated module, key or GC API is loaded.
import {descriptor,regular,need} from '../ownership-component-candidate-v1/authority.mjs';
import {indexed} from '../ownership-component-candidate-v1/proofs.mjs';
export function artifactModel(value,sourceSha){
 need(value?.schemaVersion===1&&value.state==='INDEPENDENT_CRYPTO_OWNER355_GC_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'&&value.verifiedPassed===true,'Actual new GC component artifact proof');
 need(value.componentSourceIndexSha256===sourceSha&&value.engineSha256==='289df4455b56b50a9598c42a7d924aaa2adca7f5461f96782f5758a979e966c8'&&value.sourceFiles===355,'No normal/other-source artifact transfer');
 need(JSON.stringify(value.emittedImports)==='[]'&&JSON.stringify([...value.publicAbiFunctions].sort())==='["clear","inspect","run","validate"]','Actual emitted zero imports/four functions');
 for(const k of ['generatedModuleImported','keyOperationsInvoked','gcPressureCallsInvoked','operationalAdmission'])need(value[k]===false,'Construction-only artifact boundary '+k);
 const out={};for(const k of ['component','glue','core','dts','wit','transpileMetadata','packageJson','publicSourceAudit','interfaceAudit','bundle','bundleGraph','selectedManifests'])out[k]=descriptor(value.artifacts[k]);return Object.freeze(out);
}
export async function captureFutureGcArtifact({artifactReview,componentSourceIndexSha256}={}){
 const proof=await indexed(artifactReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'}),artifacts=artifactModel(proof.data,componentSourceIndexSha256);
 const recheck=async()=>{await proof.recheck();for(const row of Object.values(artifacts))await regular(row,{maxBytes:64*1024*1024});};await recheck();return Object.freeze({artifacts,proofData:proof.data,recheck,ordinaryExportsAuthorized:false});
}
export function refuseRuntime(){throw new Error('NEW_GC_RUNTIME_SOURCE_REVIEW_AND_ROOT_ACTION_REQUIRED');}
