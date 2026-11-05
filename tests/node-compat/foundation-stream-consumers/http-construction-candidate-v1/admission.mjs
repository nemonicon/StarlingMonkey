// New action-specific admission. No owner/packager imports occur at initialization.
import {lstat,realpath} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {descriptor,regular,need,sha,hash} from './authority.mjs';
import {indexed,deepFreeze} from './proofs.mjs';
import {indexFiles,verifyClosure,verifyLiveInputs,streamHash} from './physical.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export const OUTPUTS=Object.freeze({'bundle-source':'/private/tmp/starling-node-compat/consumers355-http-bundle-v1','component-build':'/private/tmp/starling-node-compat/consumers355-http-component-v1'});
export function assertNoOverrides(env=process.env){
 for(const k of ['NODE_OPTIONS','NODE_PATH','NODE_COMPAT_LEGACY_COMPONENTIZER','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE'])need(!env[k],'Inherited loader override refuses '+k);
 for(const k of Object.keys(env))need(!k.startsWith('NAPI_RS_'),'No native binding override');
 need(env.NODE_COMPAT_HTTP_REQUIRE_INTRINSICS!=='1','Private optional intrinsic HTTP profile remains unimplemented/closed');
 return true;
}
export function actionModel(v,{sourceSha,action}={}){
 sha(sourceSha);need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_CONSUMERS355_HTTP_CONSTRUCTION_V1'&&v.sourceIndexSha256===sourceSha&&v.action===action&&Object.hasOwn(OUTPUTS,action)&&v.actionAllowed===true,'New explicit finite construction action');
 need(v.bundleRoot===OUTPUTS['bundle-source']&&v.componentRoot===OUTPUTS['component-build']&&v.variant==='normal-runtime'&&v.engineSha256==='b227a8d2e6fb6b83da556d3520dceec82d5e1978801ba3c607bc9a31aa28ad60'&&v.sourceFiles===355,'Exact normal-Runtime355/fresh namespaces');
 for(const k of ['ordinaryGuestExportsAllowed','hostRequestsAllowed','wireBodyAdapterAllowed','metadataProjection','operationalAdmission','runtimeAcceptanceClaim'])need(v[k]===false,'Unselected action remains closed '+k);
 need(v.workerTimeoutMs===600000&&v.publicationIndex&&v.publicationCompletion&&v.publicationIndependentReview&&v.sourceIndependentReview,'Exact reviewed source publication and operational bound required');if(action==='component-build')need(v.actualBundleReview,'Separate actual reviewed whole-entry bundle required before component construction');return true;
}
export async function httpPreflight({configDescriptor}={}){
 // Input/config/Root primitives are captured privately before awaits/parsing.
 const configRow=descriptor(configDescriptor),config=deepFreeze(JSON.parse(await regular(configRow))),rootRow=descriptor(config.rootAction),root=deepFreeze(JSON.parse(await regular(rootRow))),sourceSha=sha(config.sourceIndexSha256),action=config.action;actionModel(root,{sourceSha,action});
 const publicationIndex=descriptor(root.publicationIndex);need(publicationIndex.path===join(HERE,'index.json'),'Only this actually published source family executes');const pub=await indexFiles(publicationIndex);const get=name=>{const r=pub.rows.find(v=>v.path===join(HERE,name));need(r,'Published source member '+name);return r;};
 const publication=deepFreeze(JSON.parse(await regular(get('publication.json'))));need(publication.state==='CONSUMERS355_HTTP_SOURCE_PUBLISHED_PENDING_REVIEW_V1'&&publication.sourceIndexSha256===sourceSha&&publication.outputRoot===HERE,'Actual publication source/context');const proposalIndex=descriptor(publication.proposalIndex),proposal=await indexFiles(proposalIndex,{maximumFiles:512});
 const completed=JSON.parse(await regular(root.publicationCompletion));need(root.publicationCompletion.path===join(HERE,'completion.json')&&completed.state==='SOURCE_PUBLICATION_COMPLETE_EXTERNAL_ZERO_AND_REVIEW_REQUIRED_V1'&&completed.index.sha256===publicationIndex.sha256&&completed.sourceIndexSha256===sourceSha,'Actual source completion, not runtime acceptance');
 const sourcePeer=await indexed(root.sourceIndependentReview,{state:'INDEPENDENT_CONSUMERS355_HTTP_CONSTRUCTION_SOURCE_REVIEW_PASSED_V1'});need(sourcePeer.data.httpSourceIndexSha256===sourceSha&&sourcePeer.data.sourceOnly===true&&sourcePeer.data.sourceReviewPassed===true&&sourcePeer.data.ownerActionsInvoked===false,'Exact independent source review');
 const publishedPeer=await indexed(root.publicationIndependentReview,{state:'INDEPENDENT_CONSUMERS355_HTTP_SOURCE_PUBLICATION_PASSED_V1'});need(publishedPeer.data.sourceIndexSha256===sourceSha&&publishedPeer.data.publicationIndexSha256===publicationIndex.sha256&&publishedPeer.data.publisherRawExitCode===0&&publishedPeer.data.verifiedPassed===true&&publishedPeer.data.runtimeActionsInvoked===false,'Actual reviewed source copy/external0 only');
 const p=deepFreeze(JSON.parse(await regular(get('prerequisites.json')))),closure=await verifyClosure(get('closure.json'));need(p.familySha256==='a986e9b2fbdad5922f0ef9b9adba202912fa373ddb4a26b648495a1651e64916','Exact genuine355 context family');
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===p.node.path,'Pinned plain Node22');await streamHash(p.node);
 assertNoOverrides();
 need(process.env.NODE_COMPAT_TOOLCHAIN===p.invocation.toolchainRoot&&process.env.NODE_COMPAT_COMPONENTIZE_MODULE===p.invocation.componentizeModule&&await realpath(process.env.NODE_COMPAT_WASMTIME??'')===p.invocation.wasmtimeRealPath,'Actual original tool invocation roots');
 need(process.env.NODE_COMPAT_RELEASE_FAMILY_INDEX_SHA256===p.familySha256,'Explicit a986 family binding');for(const k of ['NODE_COMPAT_RELEASE_SCOPE','NODE_COMPAT_RELEASE_SCOPE_OUTPUT','NODE_COMPAT_RELEASE_ACTION_AUTHORITY','NODE_COMPAT_RELEASE_ACTION_AUTHORITY_SHA256'])need(!process.env[k],'Old release scope cannot authorize new HTTP action');
 const family=await indexFiles(p.familyIndex,{maximumFiles:2048});await family.recheck();
 // Call actual full355 read-only bridge at ORIGINAL location. Never relocate it,
 // outer-wrap a rejecting342 gate, or fabricate an old release action scope.
 const bridge=join(p.paths.familyRoot,'native-preflight.mjs'),bridgeRow=closure.rows.find(r=>r.path===bridge);need(bridgeRow,'Exact original bridge covered');await streamHash(bridgeRow);const {validationPreflight}=await import(pathToFileURL(bridge));
 const native=await validationPreflight({variant:'normal-runtime'});need(native.validationBootstrapOnly===true&&native.operationalAdmission===false&&native.pin.engineSha256===p.normalRuntimeEngineSha256&&native.pin.receiptSha256===p.normalRuntimeMetadataSha256&&native.metadata.sourceManifest.length===355&&native.metadata.entropyPolicy==='runtime-only'&&native.metadata.gcStress===false&&native.metadata.streamConsumersEnabled===true,'Genuine complete355 RuntimeOnly frame');
 need(native.admissionSourceRoot===p.nativeConfiguredSourceRoot&&native.runtimeSourceRoot===p.nativeFrozenSourceRoot&&native.sourceRoot===p.nativeFrozenSourceRoot&&native.componentToolRoot===p.paths.packagingRoot,'Actual configured/frozen/packaging roots unchanged');const manifests=deepFreeze(structuredClone(native.selectedManifests)),core=deepFreeze(structuredClone(native.coreExpectations)),metadata=deepFreeze(structuredClone(native.metadata)),pin=deepFreeze(structuredClone(native.pin));need(manifests.some(m=>m.modules?.['node:stream/consumers']&&m.profileVersion==='sm-node-22.14.0-m0.14')&&core.coreVersion==='sm-node-22.14.0-m0.11','Actual consumer manifest and unchanged core contract');
 let actualBundle=null,bundlePeer=null;if(action==='component-build'){
  bundlePeer=await indexed(root.actualBundleReview,{state:'INDEPENDENT_CONSUMERS355_HTTP_BUNDLE_REVIEW_PASSED_V1'});const b=bundlePeer.data;need(b.sourceIndexSha256===sourceSha&&b.publicationIndexSha256===publicationIndex.sha256&&b.engineSha256===pin.engineSha256&&b.bundleRawExitCode===0&&b.componentizerInvoked===false&&b.wholeEntryAndFixtureClosureVerified===true,'Separate actual full-entry bundle review, no proof transfer');
  for(const k of ['bundle','graph']){const r=descriptor(b[k]);need(bundlePeer.rows.filter(v=>v.path===r.path&&v.sha256===r.sha256&&v.bytes===r.bytes).length===1,'Actual bundle data indexed once');await streamHash(r);}actualBundle=deepFreeze({bundle:descriptor(b.bundle),graph:descriptor(b.graph)});
 }
 const live=await verifyLiveInputs(closure),recheck=async()=>{await regular(configRow);await regular(rootRow);await pub.recheck();await proposal.recheck();await sourcePeer.recheck();await publishedPeer.recheck();await regular(root.publicationCompletion);await closure.recheck();await family.recheck();await native.recheck();need(JSON.stringify(native.metadata)===JSON.stringify(metadata)&&JSON.stringify(native.pin)===JSON.stringify(pin),'Private actual frame unchanged');if(bundlePeer)await bundlePeer.recheck();await verifyLiveInputs(closure);await streamHash(p.node);};await recheck();
 return Object.freeze({action,sourceSha,rootAction:rootRow,configRow,publicationIndex,ownRows:pub.rows,proposalIndex,prerequisites:p,closure,live,enginePath:native.enginePath,sourceRoot:native.sourceRoot,admissionSourceRoot:native.admissionSourceRoot,runtimeSourceRoot:native.runtimeSourceRoot,metadata,pin,selectedManifests:manifests,coreExpectations:core,actualBundle,outputRoot:OUTPUTS[action],workerTimeoutMs:root.workerTimeoutMs,recheck});
}
