// New validation-only normal-owner355 guard. Never projects an old zlib/cost receipt.
import {lstat,realpath} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {descriptor,regular,need,sha} from '../ownership-component-candidate-v1/authority.mjs';
import {local,indexed,deepFreeze} from '../ownership-component-candidate-v1/proofs.mjs';
import {loadPackaging,streamHash,packagingEnvironment} from '../ownership-component-candidate-v1/packaging.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export const OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-component-v2';
export const ENGINE_SHA='36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05';
export async function sourceIndex(input){
 const ix=descriptor(input),value=JSON.parse(await regular(ix));need(value.schemaVersion===1&&Array.isArray(value.files)&&value.files.length>0&&value.files.length<=1024,'Bounded immutable source index');const seen=new Set(),rows=[];
 for(const item of value.files){local(item.path);need(!seen.has(item.path),'Unique source member');seen.add(item.path);const row=descriptor({path:join(dirname(ix.path),item.path),sha256:item.sha256,bytes:item.bytes});await regular(row,{maxBytes:64*1024*1024});rows.push(row);}
 return Object.freeze({rows:Object.freeze(rows),recheck:async()=>{await regular(ix);for(const row of rows)await regular(row,{maxBytes:64*1024*1024});}});
}
export function authorityModel(v,expectedSha){
 sha(expectedSha);need(v&&v.schemaVersion===1&&v.state==='ROOT_REVIEWED_CRYPTO_OWNER355_COMPONENT_BUILD_V2'&&v.action==='component-build','New component-build Root authority only');
 need(v.componentSourceIndexSha256===expectedSha&&v.componentBuildAllowed===true&&v.componentInitializationAllowed===true,'Exact reviewed source/action');
 need(v.variant==='normal-off'&&v.engineSha256===ENGINE_SHA&&v.sourceFiles===355&&v.sourceContractVersion==='sm-webcrypto-key-owner-and-prototype-guard-source-v1','Only actual new guarded normal355 engine');
 need(v.outputRoot===OUTPUT&&v.workerTimeoutMs===600000&&v.maxComponentBytes===67108864,'Finite fresh output/worker/artifact limits');
 for(const n of ['keyExportCallsAllowed','keyOrCryptoOperationsAllowed','metadataProjection','operationalAdmission','runtimeAcceptanceClaim','otherVariantsAllowed'])need(v[n]===false,'No additional authority '+n);
 need(v.sourceIndependentReview?.index&&v.sourceIndependentReview?.result,'Actual independent SOURCE review required');for(const n of ['reviewedNativePins','nativeRootReview'])descriptor(v[n]);return true;
}
export async function componentPreflight(options={}){
 // Capture private primitives synchronously; NULL rejects before artifact/tool/bootstrap reads.
 const configRow=descriptor(options.configDescriptor),config=deepFreeze(JSON.parse(await regular(configRow))),sourceSha=sha(config.componentSourceIndexSha256),rootRow=descriptor(config.rootAction),root=deepFreeze(JSON.parse(await regular(rootRow)));authorityModel(root,sourceSha);
 const ownStat=await lstat(join(HERE,'index.json')),ownIx=descriptor({path:join(HERE,'index.json'),sha256:sourceSha,bytes:ownStat.size}),own=await sourceIndex(ownIx);
 const donor=await sourceIndex({path:join(HERE,'../ownership-component-candidate-v1/index.json'),sha256:'eb648e19274c055968557227221627e2ced5dd35a2c0fb17af941dbc9a8b5c30',bytes:4446});
 const prereqBytes=await regular(donor.rows.find(r=>r.path===join(HERE,'../ownership-component-candidate-v1/prerequisites.json'))),p=deepFreeze(JSON.parse(prereqBytes));
 const sourcePeer=await indexed(root.sourceIndependentReview,{state:'INDEPENDENT_CRYPTO_OWNER355_COMPONENT_SOURCE_REVIEW_PASSED_V2'});need(sourcePeer.data.componentSourceIndexSha256===sourceSha&&sourcePeer.data.sourceOnly===true&&sourcePeer.data.sourceReviewPassed===true&&sourcePeer.data.ownerActionsInvoked===false,'Exact source-only independent peer, not action approval');
 const guest=await sourceIndex(p.guestIndex),nativeSource=await sourceIndex(p.nativeSourceIndex),guestPeer=await indexed(p.guestReview,{state:'INDEPENDENT_CRYPTO_OWNER355_OWNERSHIP_VALIDATION_SOURCE_REVIEW_PASSED_V1'}),nativePeer=await indexed(p.nativeReview,{state:'INDEPENDENT_CRYPTO_OWNER355_V2_NORMAL_OFF_NATIVE_ARTIFACT_REVIEW_PASSED_V1'});
 need(guestPeer.data.sourceIndexSha256===p.guestIndex.sha256&&guestPeer.data.sourceOnly===true&&guestPeer.data.ownerActionsInvoked===false,'Exact unexecuted ownership guest source provenance');need(nativePeer.data.sourceFiles===355&&nativePeer.data.variant==='normal-off'&&nativePeer.data.ownerActionsInvoked===false,'Genuine reviewed normal355 native source');
 for(const n of ['reviewedNativePins','nativeRootReview'])need(JSON.stringify(descriptor(root[n]))===JSON.stringify(descriptor(p[n])),'Actual reviewed native descriptor unchanged '+n);
 const pins=JSON.parse(await regular(p.reviewedNativePins)),review=JSON.parse(await regular(p.nativeRootReview));
 need(pins.state==='ROOT_REVIEWED_CRYPTO_OWNER355_VALIDATION_BOOTSTRAP_V2'&&pins.variants?.['normal-off']?.engineSha256===ENGINE_SHA&&['normal-runtime','gc-off','disabled-off'].every(n=>pins.variants[n]===null),'Normal-only reviewed native data; other variants NULL');
 need(review.reviewedPinsSha256===p.reviewedNativePins.sha256&&review.independentNativeReview.index.sha256===p.nativeReview.index.sha256,'Root native review binds genuine independent proof');
 const publicationPeer=await indexed(p.publicationReview,{state:'INDEPENDENT_FRESH_ZLIB_COST_SOURCE_PUBLICATION_VERIFIED'});need(publicationPeer.data.publicationIndexSha256==='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b'&&publicationPeer.data.verifiedPassed===true&&publicationPeer.data.externalPublisherExitCode===0,'Actual SOURCE publication review, not its native/action authority');
 const mapRow=donor.rows.find(r=>r.path===join(HERE,'../ownership-component-candidate-v1/packaging-context.json')),packaging=await loadPackaging(mapRow);packagingEnvironment(packaging);
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===p.node.path,'Exact pinned plain Node22 process');await streamHash(p.node);
 await regular(p.bootstrapEntry);const {cryptoOwnerBootstrapPreflight}=await import(pathToFileURL(p.bootstrapEntry.path));
 const frame=await cryptoOwnerBootstrapPreflight({variant:'normal-off',reviewedPinsPath:p.reviewedNativePins.path,reviewedPinsSha256:p.reviewedNativePins.sha256,rootReviewPath:p.nativeRootReview.path,rootReviewSha256:p.nativeRootReview.sha256});
 need(frame.validationBootstrapOnly===true&&frame.operationalAdmission===false&&frame.variant==='normal-off'&&frame.pin.engineSha256===ENGINE_SHA&&frame.pin.engineBytes===10002820&&Array.isArray(frame.metadata.sourceManifest)&&frame.metadata.sourceManifest.length===355&&frame.metadata.gcStress===false&&frame.metadata.cryptoKeyOwnershipPolicy?.version==='sm-webcrypto-key-owner-and-prototype-guard-source-v1','Genuine new normal-owner bootstrap; no metadata projection');
 const engine=descriptor({path:frame.enginePath,sha256:frame.pin.engineSha256,bytes:frame.pin.engineBytes}),metaStat=await lstat(frame.enginePath+'.build.json'),metadata=descriptor({path:frame.enginePath+'.build.json',sha256:frame.pin.receiptSha256,bytes:metaStat.size});await streamHash(engine);await regular(metadata);
 const code=descriptor(p.guest),wit=descriptor(p.wit);need(new TextDecoder().decode(await regular(code)).match(/^import\s/m)===null,'Single sealed no-import guest; no bundler/provider/facade');await regular(wit);
 const recheck=async()=>{await regular(configRow);await regular(rootRow);await own.recheck();await donor.recheck();await sourcePeer.recheck();await guest.recheck();await guestPeer.recheck();await nativeSource.recheck();await nativePeer.recheck();await publicationPeer.recheck();await regular(p.reviewedNativePins);await regular(p.nativeRootReview);await frame.recheck();await packaging.recheck();await streamHash(p.node);await regular(code);await regular(wit);await streamHash(engine);await regular(metadata);};await recheck();
 return Object.freeze({...packaging,node:descriptor(p.node),engine,metadata,code,wit,componentSourceIndexSha256:sourceSha,rootAction:rootRow,outputRoot:root.outputRoot,maxComponentBytes:root.maxComponentBytes,workerTimeoutMs:root.workerTimeoutMs,sourceRoot:frame.sourceRoot,configuredSourceRoot:frame.configuredSourceRoot,ownIndex:ownIx,criticalSourceFiles:Object.freeze([...own.rows,...donor.rows]),mapRow,nativeReview:p.nativeReview,nativePins:descriptor(p.reviewedNativePins),nativeRootReview:descriptor(p.nativeRootReview),recheck});
}
