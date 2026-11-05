// GC-only construction guard. No keys, pressure, helper or generated code at import.
import {lstat,realpath} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {descriptor,regular,need,sha} from '../ownership-component-candidate-v1/authority.mjs';
import {local,indexed,deepFreeze} from '../ownership-component-candidate-v1/proofs.mjs';
import {loadPackaging,streamHash,packagingEnvironment} from '../ownership-component-candidate-v1/packaging.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export const OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-gc-component-v1';
export const ENGINE_SHA='289df4455b56b50a9598c42a7d924aaa2adca7f5461f96782f5758a979e966c8';
const CONFIGURED='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source',FROZEN='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze';
export async function sourceIndex(input){
 const ix=descriptor(input),value=JSON.parse(await regular(ix));need(value.schemaVersion===1&&Array.isArray(value.files)&&value.files.length>0&&value.files.length<=1024,'Bounded immutable source index');const seen=new Set(),rows=[];
 for(const item of value.files){local(item.path);need(!seen.has(item.path),'Unique source member');seen.add(item.path);const row=descriptor({path:join(dirname(ix.path),item.path),sha256:item.sha256,bytes:item.bytes});await regular(row,{maxBytes:64*1024*1024});rows.push(row);}
 return Object.freeze({rows:Object.freeze(rows),recheck:async()=>{await regular(ix);for(const row of rows)await regular(row,{maxBytes:64*1024*1024});}});
}
export function authorityModel(v,expectedSha){
 sha(expectedSha);need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_CRYPTO_OWNER355_GC_COMPONENT_CONSTRUCTION_V1'&&v.action==='component-build','Separate GC construction authority');
 need(v.componentSourceIndexSha256===expectedSha&&v.componentBuildAllowed===true&&v.componentInitializationAllowed===true,'Exact source/initialization phase');
 need(v.variant==='gc-off'&&v.engineSha256===ENGINE_SHA&&v.sourceFiles===355&&v.sourceContractVersion==='sm-webcrypto-key-owner-and-prototype-guard-source-v1','Actual isolated GC owner355');
 need(v.outputRoot===OUTPUT&&v.workerTimeoutMs===600000&&v.maxComponentBytes===67108864,'Finite fresh construction limits');
 for(const n of ['keyExportCallsAllowed','keyOrCryptoOperationsAllowed','gcPressureCallsAllowed','ordinaryGuestExportsAllowed','metadataProjection','operationalAdmission','runtimeAcceptanceClaim','otherVariantsAllowed','timingAllowed'])need(v[n]===false,'No other permission '+n);
 need(v.sourceIndependentReview?.index&&v.sourceIndependentReview?.result,'Exact independent source peer');
 need(v.actualBootstrapReview?.index&&v.actualBootstrapReview?.result,'Actual independent bootstrap proof required');
 for(const n of ['reviewedGcPins','gcNativeRootReview','gcBootstrapConfig','actualBootstrapObservation'])descriptor(v[n]);return true;
}
export function bootstrapObservationModel(v,root,p){
 need(v?.schemaVersion===1&&v.state==='ROOT_OBSERVED_CRYPTO_OWNER355_GC_PIN_TOOLING_BOOTSTRAP_PASSED_V1'&&v.rootObservedToolRawExitCode===0,'Actual read-only GC bootstrap record');
 need(v.nativeSourceIndexSha256===p.nativeSourceIndex.sha256&&v.toolingSourceIndexSha256===p.toolingIndex.sha256&&v.variant==='gc-off','Actual native/tooling roles');
 need(v.engineSha256===p.engineSha256&&v.metadataSha256===p.metadataSha256&&v.freezeReceiptSha256===p.freezeReceiptSha256,'Exact actual GC artifact tuple');
 need(JSON.stringify(descriptor(v.bootstrapConfig))===JSON.stringify(descriptor(root.gcBootstrapConfig)),'Exact observed bootstrap config');
 for(const n of ['engineExecuted','keyOperationsInvoked','gcWorkloadInvoked','operationalAdmission'])need(v[n]===false,'Read-only proof boundary '+n);
}
export async function componentPreflight(options={}){
 const configRow=descriptor(options.configDescriptor),config=deepFreeze(JSON.parse(await regular(configRow))),sourceSha=sha(config.componentSourceIndexSha256),rootRow=descriptor(config.rootAction),root=deepFreeze(JSON.parse(await regular(rootRow)));authorityModel(root,sourceSha);
 const ownStat=await lstat(join(HERE,'index.json')),ownIx=descriptor({path:join(HERE,'index.json'),sha256:sourceSha,bytes:ownStat.size}),own=await sourceIndex(ownIx);
 const donor=await sourceIndex({path:join(HERE,'../ownership-component-candidate-v1/index.json'),sha256:'eb648e19274c055968557227221627e2ced5dd35a2c0fb17af941dbc9a8b5c30',bytes:4446});
 const p=deepFreeze(JSON.parse(await regular(own.rows.find(r=>r.path===join(HERE,'prerequisites.json')))));
 const sourcePeer=await indexed(root.sourceIndependentReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_COMPONENT_SOURCE_REVIEW_PASSED_V1'});need(sourcePeer.data.componentSourceIndexSha256===sourceSha&&sourcePeer.data.sourceOnly===true&&sourcePeer.data.sourceReviewPassed===true&&sourcePeer.data.ownerActionsInvoked===false,'Source peer is not action authority');
 const guest=await sourceIndex(p.guestIndex),native=await sourceIndex(p.nativeSourceIndex),tooling=await sourceIndex(p.toolingIndex);
 const guestPeer=await indexed(p.guestReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_REVIEW_PASSED_V2'}),nativePeer=await indexed(p.nativeReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_ARTIFACT_REVIEW_PASSED_V1'});
 need(guestPeer.data.sourceIndexSha256===p.guestIndex.sha256&&guestPeer.data.sourceOnly===true&&guestPeer.data.sourceReviewPassed===true&&guestPeer.data.ownerActionsInvoked===false&&guestPeer.data.outerPressureRequests===16&&JSON.stringify(guestPeer.data.perRunPressureDeltas)==='[4,4,8,0]','Exact reviewed GC schema2 source, no runtime transfer');
 need(nativePeer.data.sourceIndexSha256===p.nativeSourceIndex.sha256&&nativePeer.data.verifiedPassed===true&&nativePeer.data.nativeSourceFiles===355&&nativePeer.data.variant==='gc-off'&&nativePeer.data.engineSha256===ENGINE_SHA&&nativePeer.data.freezeReceiptSha256===p.freezeReceiptSha256,'Full exact frozen GC native proof');
 const pub=await indexed(p.publicationReview,{state:'INDEPENDENT_FRESH_ZLIB_COST_SOURCE_PUBLICATION_VERIFIED'});need(pub.data.publicationIndexSha256==='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b'&&pub.data.verifiedPassed===true&&pub.data.externalPublisherExitCode===0,'Packaging source-role authority only');
 const packaging=await loadPackaging(p.packagingMap);packagingEnvironment(packaging);need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===p.node.path,'Pinned plain Node');await streamHash(p.node);
 for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONOPTIMIZE','PYTHONHOME','PYTHONPATH'])need(!process.env[k],'Bootstrap override refuses '+k);
 const pins=JSON.parse(await regular(root.reviewedGcPins)),review=JSON.parse(await regular(root.gcNativeRootReview));
 need(pins.state==='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_V1'&&pins.sourceIndexSha256===p.nativeSourceIndex.sha256&&pins.variants?.['gc-off']?.engineSha256===ENGINE_SHA&&['normal-off','normal-runtime','disabled-off'].every(n=>pins.variants[n]===null),'NEW GC-only pins; never normal/e6b projection');
 need(review.reviewedPinsSha256===root.reviewedGcPins.sha256&&review.sourceIndexSha256===p.nativeSourceIndex.sha256,'New GC Root pin review');
 const bootstrapConfig=deepFreeze(JSON.parse(await regular(root.gcBootstrapConfig)));need(bootstrapConfig.sourceIndex.sha256===p.nativeSourceIndex.sha256&&bootstrapConfig.toolingIndex.sha256===p.toolingIndex.sha256,'Genuine native/tooling contexts');
 need(bootstrapConfig.sourceIndex.path===p.nativeSourceIndex.path&&bootstrapConfig.toolingIndex.path===p.toolingIndex.path,'No index path projection');
 bootstrapObservationModel(JSON.parse(await regular(root.actualBootstrapObservation)),root,p);
 const bootstrapPeer=await indexed(root.actualBootstrapReview,{state:'INDEPENDENT_CRYPTO_OWNER355_GC_BOOTSTRAP_REVIEW_PASSED_V1'}),bp=bootstrapPeer.data;need(bp.verifiedPassed===true&&bp.nativeSourceIndexSha256===p.nativeSourceIndex.sha256&&bp.toolingSourceIndexSha256===p.toolingIndex.sha256&&bp.engineSha256===p.engineSha256&&bp.metadataSha256===p.metadataSha256&&bp.freezeReceiptSha256===p.freezeReceiptSha256&&bp.engineExecuted===false&&bp.operationalAdmission===false,'Exact full independent GC bootstrap tuple');need(JSON.stringify(descriptor(bp.bootstrapRootObservation))===JSON.stringify(descriptor(root.actualBootstrapObservation))&&JSON.stringify(descriptor(bp.bootstrapConfig))===JSON.stringify(descriptor(root.gcBootstrapConfig)),'Exact independently reviewed observation/config roles');
 await regular(p.bootstrapEntry);await tooling.recheck();const {cryptoOwnerGcBootstrapPreflight}=await import(pathToFileURL(p.bootstrapEntry.path));
 const frame=await cryptoOwnerGcBootstrapPreflight({configDescriptor:descriptor(root.gcBootstrapConfig)});
 need(frame.validationBootstrapOnly===true&&frame.operationalAdmission===false&&frame.variant==='gc-off'&&frame.metadata.gcStress===true&&frame.pin.engineSha256===ENGINE_SHA&&frame.pin.engineBytes===10004458&&frame.pin.receiptSha256===p.metadataSha256&&frame.pin.freezeReceiptSha256===p.freezeReceiptSha256&&frame.metadata.sourceManifest.length===355,'Full actual GC bootstrap frame');
 need(frame.sourceIndexSha256===p.nativeSourceIndex.sha256&&frame.configuredSourceRoot===CONFIGURED&&frame.sourceRoot===FROZEN+'/source'&&frame.nativeConfiguredSourceRoot===CONFIGURED&&frame.frozenSourceRoot===FROZEN+'/source','Distinct genuine configured/frozen roots');
 need(frame.reviewedPinsSha256===root.reviewedGcPins.sha256&&frame.rootReviewSha256===root.gcNativeRootReview.sha256&&JSON.stringify(frame.toolingProvenance.toolingIndexed)===JSON.stringify(p.toolingIndex),'Actual GC pin/tooling provenance');
 const engine=descriptor({path:frame.enginePath,sha256:frame.pin.engineSha256,bytes:frame.pin.engineBytes}),metaStat=await lstat(frame.enginePath+'.build.json'),metadata=descriptor({path:frame.enginePath+'.build.json',sha256:frame.pin.receiptSha256,bytes:metaStat.size});await streamHash(engine);await regular(metadata);
 const code=descriptor(p.guest),wit=descriptor(p.wit);await regular(code);await regular(wit);need(Array.isArray(frame.selectedManifests)&&frame.selectedManifests.some(m=>m.modules?.['node:buffer']?.exports?.includes('Buffer')),'Genuine native Buffer facade manifest');
 const recheck=async()=>{await regular(configRow);await regular(rootRow);await own.recheck();await donor.recheck();await sourcePeer.recheck();await guest.recheck();await guestPeer.recheck();await native.recheck();await nativePeer.recheck();await tooling.recheck();await pub.recheck();await bootstrapPeer.recheck();await regular(p.bootstrapEntry);await regular(root.reviewedGcPins);await regular(root.gcNativeRootReview);await regular(root.gcBootstrapConfig);await regular(root.actualBootstrapObservation);await frame.recheck();await packaging.recheck();await streamHash(p.node);await regular(code);await regular(wit);await streamHash(engine);await regular(metadata);};await recheck();
 return Object.freeze({...packaging,node:descriptor(p.node),engine,metadata,code,wit,componentSourceIndexSha256:sourceSha,rootAction:rootRow,outputRoot:root.outputRoot,maxComponentBytes:root.maxComponentBytes,workerTimeoutMs:root.workerTimeoutMs,sourceRoot:frame.sourceRoot,configuredSourceRoot:frame.configuredSourceRoot,ownIndex:ownIx,criticalSourceFiles:Object.freeze([...own.rows,...donor.rows]),mapRow:descriptor(p.packagingMap),nativeReview:p.nativeReview,nativePins:descriptor(root.reviewedGcPins),nativeRootReview:descriptor(root.gcNativeRootReview),bootstrapConfig:descriptor(root.gcBootstrapConfig),actualBootstrapObservation:descriptor(root.actualBootstrapObservation),actualBootstrapReview:root.actualBootstrapReview,selectedManifests:frame.selectedManifests,recheck});
}
