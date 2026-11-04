// Authenticated DATA/configured-code boundary only. No bootstrap imported or run here.
import {lstat} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {descriptor,regular,need} from '../ownership-component-candidate-v1/authority.mjs';
import {indexed,deepFreeze,local} from '../ownership-component-candidate-v1/proofs.mjs';
const ROOT='/private/tmp/starling-node-compat/crypto-owner-source-v2',REL='tests/node-compat/foundation-crypto/native-integration-candidate-v2';
const NATIVE_SHA='68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575';
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function bootstrapEnvironment(env=process.env){
 // The actual reviewed bootstrap launch excludes these overrides. Do not let
 // a future loader obtain unsealed Python modules or disabled assertions.
 for(const key of ['PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE'])need(!env[key],'Inherited Python bootstrap override refuses '+key);
 return true;
}
export function executableContextModel(c,contract,prerequisites){
 need(c?.schemaVersion===1&&c.state==='ACTUAL_CONFIGURED_CRYPTO_OWNER355_BOOTSTRAP_CONTEXT_DATA_V1'&&c.sourcePreparationEntryIsProvenanceOnly===true,'Explicit original/configured role split');
 need(c.configuredSourceRoot===ROOT&&c.sourceRoot==='/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze/source'&&c.normalOnly===true,'Exact actual configured/frozen roots; no relocation/projection');
 need(c.configuredSourceIndex.path===join(ROOT,REL,'index.json')&&c.configuredSourceIndex.sha256===NATIVE_SHA&&c.configuredBootstrapEntry.path===join(ROOT,REL,'artifact-tools/bootstrap-preflight.mjs'),'Only configured staged entry/index executes');
 need(c.configuredToolPins.path===join(ROOT,REL,'artifact-tools/tool-pins.json')&&c.configuredPolicy.path===join(ROOT,REL,'policy.json')&&c.nativeConfiguredSourceFiles===355&&c.configuredToolDependencies===922,'Explicit configured355/tool922 roles');
 need(contract.schemaVersion===1&&contract.state==='INDEPENDENT_CRYPTO_OWNER355_NORMAL_OFF_PIN_AND_JS_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1'&&contract.verifiedPassed===true&&contract.readOnlyBootstrapOnly===true&&contract.variant==='normal-off'&&contract.otherVariantsNull===true&&contract.positiveKeyOperationsInvoked===false,'Actual genuine normal-only pin/JS bootstrap review; not key approval');
 need(contract.configuredSourceRoot===c.configuredSourceRoot&&contract.sourceRoot===c.sourceRoot&&contract.contextsAreDistinct===true&&contract.sourceFiles===355&&contract.configuredToolDependencies===922&&equal(contract.configuredSourceIndex,c.configuredSourceIndex),'Actual two-context contract binds executable root');
 for(const[key,value]of [['sourceIndex',prerequisites.nativeSourceIndex],['reviewedPins',prerequisites.reviewedNativePins],['rootNativeReview',prerequisites.nativeRootReview],['independentNativeReview',prerequisites.nativeReview],['actualJsBootstrapFrame',c.actualFrame]])need(equal(contract[key],value),'Actual contract exact provenance '+key);
 need(c.configuredBootstrapEntry.sha256===prerequisites.bootstrapEntry.sha256&&c.configuredBootstrapEntry.bytes===prerequisites.bootstrapEntry.bytes&&c.configuredBootstrapEntry.path!==prerequisites.bootstrapEntry.path,'Same source digest is insufficient: original entry DATA only');return true;
}
export function assertReturnedContexts(frame,contract,expectedFrame){
 need(frame?.variant==='normal-off'&&frame.validationBootstrapOnly===true&&frame.operationalAdmission===false,'Genuine returned validation-only frame');
 need(frame.configuredSourceRoot===contract.configuredSourceRoot&&frame.sourceRoot===contract.sourceRoot&&frame.enginePath===contract.engine.path,'Genuine returned context spellings unchanged, no rewritten metadata/roots');
 for(const key of ['metadata','pin','selectedManifests'])need(equal(frame[key],expectedFrame[key]),'Whole genuine returned frame equals actual reviewed frame '+key);return true;
}
export async function captureConfiguredBootstrap(contextRow,prerequisites,rootAuthority){
 const row=descriptor(contextRow),p=deepFreeze(structuredClone(prerequisites)),root=deepFreeze(structuredClone(rootAuthority));
 const c=deepFreeze(JSON.parse(await regular(row)));
 need(equal(root.actualBootstrapReview,c.actualBootstrapReview)&&root.actualBootstrapReviewGrantsComponentAuthority===false,'Root explicitly pins real read-only bootstrap DATA without promoting its scope');
 const proof=await indexed(c.actualBootstrapReview,{state:'INDEPENDENT_CRYPTO_OWNER355_NORMAL_OFF_PIN_AND_JS_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1'}),contractRow=descriptor(c.actualContract);
 need(proof.rows.filter(v=>equal(v,contractRow)).length===1,'Actual stable contract is indexed exactly once');const contract=deepFreeze(JSON.parse(await regular(contractRow)));executableContextModel(c,contract,p);
 need(proof.data.verifiedPassed===true&&proof.data.sourceIndexSha256===NATIVE_SHA&&proof.data.configuredToolDependencyRowsRehashed===922&&proof.data.otherVariantsNull===true&&proof.data.positiveKeyOperationsInvoked===false,'Actual independent completed read-only review');
 const ix=descriptor(c.configuredSourceIndex),index=JSON.parse(await regular(ix));need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=1024,'Finite configured native-producer source index');const sourceRows=[],seen=new Set();
 for(const item of index.files){local(item.path);need(!seen.has(item.path),'Unique configured source row');seen.add(item.path);const r=descriptor({path:join(dirname(ix.path),item.path),sha256:item.sha256,bytes:item.bytes});await regular(r,{maxBytes:64*1024*1024});sourceRows.push(r);}
 for(const item of [c.configuredBootstrapEntry,c.configuredToolPins,c.configuredPolicy])need(sourceRows.filter(r=>equal(r,descriptor(item))).length===1,'Configured entry/tool/policy authenticated by full68b6 index');
 const policy=deepFreeze(JSON.parse(await regular(c.configuredPolicy))),tools=deepFreeze(JSON.parse(await regular(c.configuredToolPins))),expectedFrameRow=descriptor(c.actualFrame),expectedFrame=deepFreeze(JSON.parse(await regular(expectedFrameRow)));
 need(Array.isArray(policy.expectedNativeSourceManifest)&&policy.expectedNativeSourceManifest.length===355&&Array.isArray(tools.toolDependencies)&&tools.toolDependencies.length===922&&tools.nativeSources===355,'Exact actual configured355+tool922, no subset/projection');
 need(equal(expectedFrame.metadata.sourceManifest.map(({path,sha256})=>({path,sha256})),policy.expectedNativeSourceManifest),'Retained actual metadata binds complete355 source policy');assertReturnedContexts(expectedFrame,contract,expectedFrame);
 const toolRows=[],nativeRows=[],toolNames=new Set(),nativeNames=new Set();
 for(const item of tools.toolDependencies){local(item.path);need(!toolNames.has(item.path),'Unique configured tool row');toolNames.add(item.path);const r=descriptor({path:join(ROOT,item.path),sha256:item.sha256,bytes:item.bytes});await regular(r,{maxBytes:64*1024*1024});toolRows.push(r);}
 for(const item of policy.expectedNativeSourceManifest){local(item.path);need(!nativeNames.has(item.path),'Unique native row');nativeNames.add(item.path);for(const root of [c.configuredSourceRoot,c.sourceRoot]){const path=join(root,item.path),size=(await lstat(path)).size,r=descriptor({path,sha256:item.sha256,bytes:size});await regular(r,{maxBytes:64*1024*1024});nativeRows.push(r);}}
 const entry=descriptor(c.configuredBootstrapEntry),recheck=async()=>{await regular(row);await proof.recheck();await regular(contractRow);await regular(expectedFrameRow);await regular(ix);for(const r of sourceRows)await regular(r,{maxBytes:64*1024*1024});for(const r of toolRows)await regular(r,{maxBytes:64*1024*1024});for(const r of nativeRows)await regular(r,{maxBytes:64*1024*1024});await regular(entry);};await recheck();
 return Object.freeze({entry,contract,expectedFrame,configuredSourceIndex:ix,configuredSourceRoot:c.configuredSourceRoot,sourceRoot:c.sourceRoot,assertReturned(frame){return assertReturnedContexts(frame,contract,expectedFrame);},recheck});
}
