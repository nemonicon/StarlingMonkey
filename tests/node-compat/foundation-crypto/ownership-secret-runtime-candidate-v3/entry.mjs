// Dormant genuine secret355 ordinary runtime caller; builtins only before authentication.
import {readFile,lstat,readdir,realpath,statfs} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-runtime-candidate-v3';
const same=isDeepStrictEqual,sha=b=>createHash('sha256').update(b).digest('hex');
function need(v,m){if(!v)throw new Error(m);}
export function captureDescriptor(value){
  const r=Object.freeze({path:value?.path,sha256:value?.sha256,bytes:value?.bytes});
  need(typeof r.path==='string'&&isAbsolute(r.path)&&resolve(r.path)===r.path&&!r.path.includes('\\')&&!r.path.includes('\0'),'Canonical absolute descriptor; no normalization');
  need(typeof r.sha256==='string'&&/^[a-f0-9]{64}$/.test(r.sha256)&&Number.isSafeInteger(r.bytes)&&r.bytes>=0&&r.bytes<=2**40,'Exact descriptor primitives');return r;
}
function relative(n){need(typeof n==='string'&&n&&!isAbsolute(n)&&!n.includes('\\')&&!n.includes('\0')&&n.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Confined local name');return n;}
function identity(s){return [s.dev,s.ino,s.size,s.mtimeMs,s.ctimeMs];}
class Capture {
  rows=new Map();families=[];
  async file(input){
    const r=captureDescriptor(input),a=await lstat(r.path),physical=await realpath(r.path);need(a.isFile()&&!a.isSymbolicLink()&&a.size===r.bytes,'Ordinary pinned DATA');
    const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(r.path)){h.update(b);bytes+=b.length;}
    const z=await lstat(r.path);need(same(identity(a),identity(z))&&physical===await realpath(r.path)&&bytes===r.bytes&&h.digest('hex')===r.sha256,'Stable exact DATA');
    const captured={r,identity:identity(z),physical};if(this.rows.has(r.path))need(same(captured,this.rows.get(r.path)),'Captured identity changed');this.rows.set(r.path,captured);return r;
  }
  async read(input){const r=await this.file(input);need(r.bytes<=32*1024*1024,'Bounded JSON DATA');const b=await readFile(r.path);need(b.length===r.bytes&&sha(b)===r.sha256,'Exact JSON bytes');return JSON.parse(b);}
  async tree(root,names){
    const actual=[];need((await lstat(root)).isDirectory()&&!(await lstat(root)).isSymbolicLink(),'Ordinary family root');
    async function walk(base,prefix=''){for(const name of await readdir(base)){const p=join(base,name),s=await lstat(p),n=prefix+name;need(!s.isSymbolicLink(),'No family links');if(s.isDirectory())await walk(p,n+'/');else{need(s.isFile(),'Regular family member');actual.push(n);}}}
    await walk(root);need(actual.length===names.size&&actual.every(n=>names.has(n)),'Exact family membership');
  }
  async family(input){
    const ix=captureDescriptor(input),v=await this.read(ix),base=dirname(ix.path),names=new Set(['index.json']),rows=[ix];
    need(v.schemaVersion===1&&Array.isArray(v.files)&&v.files.length>0&&v.files.length<=2048,'Finite source/proof family');
    for(const m of v.files){const n=relative(m.path);need(!names.has(n),'Unique member');names.add(n);const r=captureDescriptor({path:join(base,n),sha256:m.sha256,bytes:m.bytes});await this.file(r);rows.push(r);}
    await this.tree(base,names);this.families.push({base,names});return rows;
  }
  async proof(pair){const rows=await this.family(pair.index);need(rows.filter(r=>same(r,captureDescriptor(pair.result))).length===1,'Result indexed exactly once');return this.read(pair.result);}
  async recheck(){for(const {r}of [...this.rows.values()])await this.file(r);for(const {base,names}of this.families)await this.tree(base,names);}
}
export function validateRetainedRecord(record,refs,expectedHistory,retainedConfig,readonlyRoot){
 need(record&&Object.isFrozen(record)&&same(Reflect.ownKeys(record),['schemaVersion','kind','sourceIndex','actualReview','historicalBootstrap','currentVerification','recheck']),'Exact genuine frozen retained record');
 need(record.schemaVersion===1&&record.kind==='retained-secret355-bootstrap-v1'&&same(record.sourceIndex,refs.retainedSourceIndex)&&same(record.actualReview,refs.actualHistoricalBootstrapReview),'New record versus historical review roles');
 const d=Object.getOwnPropertyDescriptor(record,'recheck');need(d&&typeof d.value==='function'&&d.enumerable&&!d.writable&&!d.configurable,'Fresh own callable, never serialized DATA');
 const h=record.historicalBootstrap,v=record.currentVerification;
 need(same(Object.keys(v).sort(),refs.currentVerificationFields),'Full current verification record shape');
 need(same(h,expectedHistory)&&Object.keys(h).length===41&&h.variant==='normal-off'&&h.nativeSourceFiles===355&&h.externalEmbeddingSources===3&&h.selectedManifestCount===11&&h.currentCompleteVerifierCalls===1,'Full historical355+3/11 unchanged');
 need(h.metadataDescriptor.path===h.engine.path+'.build.json'&&same(h.engine,refs.engine)&&same(h.metadataDescriptor,refs.metadata)&&same(h.freezeReceipt,refs.freezeReceipt),'Actual frozen engine/whole raw sidecar/receipt');
 need(Object.keys(h.metadata).length===75&&h.metadata.sourceManifest.length===355&&h.metadata.componentizeSourceManifest.length===3&&h.selectedManifests.length===11,'All native metadata/manifests, no projection');
 need(h.metadata.cryptoKeyOwnershipPolicy?.version==='sm-webcrypto-key-owner-and-prototype-guard-source-v1'&&h.metadata.cryptoSecretFailureSourcePolicy?.version==='sm-webcrypto-secret-failure-owner-source-v2','Guarded owner ancestry plus real secret-failure layer');
 need(h.metadata.cryptoSecretFailureSourcePolicy.sourceFiles===355&&h.metadata.cryptoSecretFailureSourcePolicy.unchangedParentFiles===352&&h.metadata.cryptoSecretFailureSourcePolicy.changedSourceFiles===3,'Actual352+3 source layer');
 need(h.metadata.entropyPolicy==='off'&&h.metadata.gcStress===false&&h.metadata.oomTesting===false&&h.metadata.observedCMakeOptions.CMAKE_BUILD_TYPE==='Release','Release/OFF/noGC/OOM');
 need(same(h.verifierFrame.runtimeBackendProof,{verified:false,version:null,vernum:null}),'No backend runtime proof');
 for(const k of ['engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','grantsRuntimeAuthority'])need(h[k]===false,'Historical no action '+k);
 need(v.schemaVersion===1&&v.kind==='current-read-hash-verification-v1'&&same(v.sourceIndex,refs.retainedSourceIndex)&&same(v.config,retainedConfig)&&same(v.rootAuthority,readonlyRoot),'Actual fresh current read-only config/context');
 for(const k of ['helperInvocations','originalApiInvocations','historicalRecheckInvocations','processesSpawned','filesCreated'])need(v[k]===0,'Current API zero action '+k);
 need(v.protectedFileRows===28256&&v.retainedTreeScopes===8&&v.fullMetadataFields===75&&v.selectedWholeManifests===11&&v.sourceAndProtectionChecked===true,'Full current protection counts');
 for(const k of ['engineExecuted','componentOrGuestExecuted','keyOrApplicationCryptoOperationsInvoked','operationalAdmission','runtimeAcceptanceClaim'])need(v[k]===false,'Read-only current scope '+k);
 return h;
}
async function validateActualPreflight(c,refs){
 const actual=await c.proof(refs.actualRetainedPreflightReview),contract=await c.read(refs.actualRetainedPreflightContract);
 need(actual.schemaVersion===1&&contract.schemaVersion===1&&actual.state===contract.requiredReviewState&&actual.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_RETAINED_PREFLIGHT_RESULTS_REVIEW_PASSED_V1','Real completed d80e DATA review');
 for(const g of ['requiredFixedValues','requiredExactDescriptors','requiredPairs'])for(const[k,v]of Object.entries(contract[g]))need(same(actual[k],v),'Actual read-only contract '+k);
 need(same(actual.coverage,contract.requiredCoverage)&&actual.sourceIndexSha256===refs.retainedSourceIndex.sha256&&same(actual.recordData,refs.actualRetainedRecordData),'Exact retained record DATA binding');
 const data=await c.read(refs.actualRetainedRecordData);need(data.kind==='retained-secret355-bootstrap-v1'&&same(data.sourceIndex,refs.retainedSourceIndex),'Actual full six-property record DATA');return data.historicalBootstrap;
}
export function runtimeAuthority(root,own,refs){
 need(root?.schemaVersion===1&&root.state==='ROOT_REVIEWED_SECRET355_NORMAL_RUNTIME_V3'&&root.phase==='guarded-normal-runtime'&&same(root.sourceIndex,own),'New exact guarded-runtime phase/source');
 need(root.variant==='normal-off'&&root.runtimeWorkloadAllowed===true&&root.nodeOracleAllowed===true&&root.retainedReadOnlyApiAllowed===true&&root.guardedPrototypeCase3Allowed===true,'Only four guarded normal cases plus host oracle');
 need(root.nativeSourceFiles===355&&root.externalEmbeddingSources===3&&root.selectedManifestCount===11&&root.fullMetadataFields===75&&root.engineSha256===refs.engine.sha256&&root.componentSha256===refs.artifacts.component.sha256,'Actual secret355 artifact/native relation');
 need(same(root.actualArtifactReview,refs.actualArtifactReview)&&same(root.actualArtifactContract,refs.actualArtifactContract)&&same(root.componentSourceIndex,refs.componentSourceIndex),'Exact independently reviewed c067 component facts');
 need(root.outputRoot===refs.outputRoot&&root.externalOutputRoot===refs.externalOutputRoot&&root.externalParentDeadlineSeconds===2400&&root.workerTimeoutMs===600000&&same(root.scenarios,['retained','fresh','wrapper']),'Finite fixed fresh three-process schedule');
 need(same(root.monitorIndex,refs.monitorIndex)&&same(root.monitorEntry,refs.monitorEntry),'Genuine original external owned monitor');
 for(const k of ['originalOneShotApiAllowed','originalHelperAllowed','historicalCallableAllowed','nativeBuildAllowed','nativeFreezeAllowed','componentBuildAllowed','gcAllowed','gcPressureAllowed','oomAllowed','faultInjectionAllowed','unsafeResetAllowed','wasmtimeAllowed','otherVariantsAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed'])need(root[k]===false,'No extra authority '+k);
 captureDescriptor(root.retainedConfig);need(root.actualRuntimeReview===null,'No runtime acceptance in advance');return true;
}
export function artifactModel(proof,contract,refs){
 need(proof?.schemaVersion===1&&proof.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_V2_ARTIFACT_REVIEW_PASSED_V1'&&proof.verifiedPassed===true,'Actual secret355 component proof');
 need(proof.componentSourceIndexSha256===refs.componentSourceIndex.sha256&&proof.componentSha256===refs.artifacts.component.sha256&&proof.engineSha256===refs.engine.sha256,'Exact source/component/engine roles');
 need(proof.nativeSourceFiles===355&&proof.externalEmbeddingSources===3&&proof.selectedManifestCount===11&&proof.fullMetadataFields===75,'Complete355+3/75/11 proof');
 need(same(proof.emittedImports,[])&&same([...proof.publicAbiFunctions].sort(),['clear','inspect','run','validate']),'Only four actual scalar functions/imports[]');
 for(const k of ['generatedModuleImported','ordinaryGuestExportsInvoked','keyOperationsInvoked','asyncScalarRuntimeProof'])need(proof[k]===false,'Construction scope only '+k);
 need(contract?.schemaVersion===1&&same(contract.artifacts,proof.artifacts)&&same(proof.artifacts,refs.artifacts),'Whole indexed actual artifact contract/map, never a borrowed frame');return true;
}
export function plainNodeEnvironment(env){
 for(const k of ['NODE_OPTIONS','NODE_PATH','JCO_DEBUG','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK'])need(!env[k],'No inherited loader override '+k);return true;
}
async function authenticate(input){
 const configRow=captureDescriptor(input);need(HERE===ORIGINAL&&process.version==='v22.14.0'&&process.execArgv.length===0,'Original own runtime context/plain pinned Node22');plainNodeEnvironment(process.env);
 const c=new Capture();let primary=null;
 try{
  const config=await c.read(configRow),own=captureDescriptor(config.sourceIndex);need(config.schemaVersion===1&&config.state==='SECRET355_NORMAL_RUNTIME_CONFIG_V3'&&own.path===join(HERE,'index.json'),'New actual runtime Source/config');
  const ownRows=await c.family(own),refs=await c.read(ownRows.find(r=>r.path===join(HERE,'references.json'))),inputs=await c.read(ownRows.find(r=>r.path===join(HERE,'source-inputs.json')));
  need(inputs.schemaVersion===1&&inputs.files.length>=33364&&inputs.files.length<=45000&&new Set(inputs.files.map(r=>r.path)).size===inputs.files.length,'Complete distinct physical-role protection intake');
  for(const r of inputs.files)await c.file(r);need(inputs.modeRows.length===inputs.files.length,'Complete captured input modes');for(const m of inputs.modeRows)need(((await lstat(m.file.path)).mode&0o7777)===m.mode,'Actual protected input mode');for(const r of inputs.families)await c.family(r);for(const t of inputs.historicalDonorTrees){const names=new Set(t.names);need(names.size===t.names.length,'Exact historical donor tree');await c.tree(t.root,names);c.families.push({base:t.root,names});}
  need(refs.actualArtifactReview&&refs.actualArtifactContract&&refs.artifacts,'Sealed actual artifact proof required; no wildcard slot');
  const rootRow=captureDescriptor(config.rootAuthority),root=await c.read(rootRow);runtimeAuthority(root,own,refs);need(same(root.entry,ownRows.find(r=>r.path===join(HERE,'entry.mjs')))&&same(root.externalController,ownRows.find(r=>r.path===join(HERE,'external.py'))),'Exact own real entry/caller bytes');
  const peer=await c.proof(root.sourceIndependentReview);need(peer.schemaVersion===1&&peer.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_RUNTIME_SOURCE_REVIEW_PASSED_V3'&&peer.sourceIndexSha256===own.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true,'Separate runtime Source peer');
  for(const k of ['ownerActionsInvoked','hostActionsInvoked','runtimeActionsInvoked'])need(peer[k]===false,'Source approval only '+k);
  const artifact=await c.proof(refs.actualArtifactReview),artifactRows=await c.family(refs.actualArtifactReview.index);need(artifactRows.filter(r=>same(r,refs.actualArtifactContract)).length===1,'Exact actual artifact contract indexed once');const contract=await c.read(refs.actualArtifactContract);artifactModel(artifact,contract,refs);
  const contextHold=await c.proof(refs.contextCorrectionReview);need(contextHold.state==='ROOT_CRYPTO_OWNER355_SECRET_RUNTIME_V2_CONTEXT_REVIEW_HELD_V1'&&contextHold.sourceReviewPassed===false&&same(contextHold.sourceIndex,refs.previousRuntimeV2SourceIndex)&&contextHold.actualRuntimeAttempted===false,'Preserve exact unexecuted v2 context HOLD');
  const held=await c.proof(refs.heldRuntimeSourceReview),correction=await c.read(refs.requiredCorrectionContract);need(held.schemaVersion===1&&held.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_RUNTIME_SOURCE_REVIEW_HELD_V1'&&held.sourceIndexSha256===refs.parentRuntimeSourceIndex.sha256&&held.sourceReviewPassed===false&&same(correction.heldSourceIndex,refs.parentRuntimeSourceIndex),'Exact immutable M1 Source HOLD history,not runtime authority');
  for(const r of Object.values(refs.artifacts))await c.file(r);
  need(await realpath(process.execPath)===refs.node.path,'Actual pinned Node executable');await c.file(refs.node);
  const history=await validateActualPreflight(c,refs),retainedConfig=captureDescriptor(root.retainedConfig),ro=await c.read(retainedConfig);await c.file(ro.rootAuthority);need(same(ro.sourceIndex,refs.retainedSourceIndex),'Genuine original retained read-only config');
  await c.recheck();return{c,configRow,own,refs,root,rootRow,history,retainedConfig,readonlyRoot:captureDescriptor(ro.rootAuthority)};
 }catch(error){primary=error;throw error;}
 finally{try{await c.recheck();}catch(error){if(primary!==null)throw new AggregateError([primary,error],'Runtime authentication and final source protection failed');throw error;}}
}
async function prepareRuntime(input){
 const f=await authenticate(input);let record=null,packaging=null,primary=null;
 const recheck=async()=>{if(record)await record.recheck();if(packaging)await packaging.recheck();await f.c.recheck();};
 try{
  // Complete source/dependency/Root/artifact authentication precedes custom code.
  const api=await import(pathToFileURL(f.refs.retainedApi.path));need(typeof api.retainedSecretBootstrapPreflight==='function','Genuine c47 distinct read-only API');
  record=await api.retainedSecretBootstrapPreflight({configDescriptor:f.retainedConfig});validateRetainedRecord(record,f.refs,f.history,f.retainedConfig,f.readonlyRoot);
  const helper=await import(pathToFileURL(f.refs.packagingHelper.path));packaging=await helper.loadPackaging(f.refs.packagingMap);
  need(packaging.packagingRoot===f.refs.physicalRoles.packagingRoot&&packaging.toolchainRoot===f.refs.physicalRoles.toolchainRoot&&packaging.packagerRoot===f.refs.physicalRoles.packagerRoot,'Actual original package roles, not native admission');
  await recheck();
  return Object.freeze({kind:'secret355-normal-runtime-admission-v3',sourceIndexSha256:f.own.sha256,configRow:f.configRow,rootAction:f.rootRow,node:captureDescriptor(f.refs.node),artifacts:deepFreeze(f.refs.artifacts),outputRoot:f.refs.outputRoot,workerTimeoutMs:f.root.workerTimeoutMs,historicalBootstrap:record.historicalBootstrap,currentVerification:record.currentVerification,retainedRecordData:deepFreeze(Object.fromEntries(Object.entries(record).filter(([k])=>k!=='recheck'))),retainedRecordShape:deepFreeze(Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptors(record)).map(([k,d])=>[k,{type:typeof d.value,writable:d.writable,configurable:d.configurable,enumerable:d.enumerable}]))),parentAuditedActualComponent:true,recheck});
 }catch(error){primary=error;throw error;}
 finally{try{await recheck();}catch(error){if(primary!==null)throw new AggregateError([primary,error],'Runtime preparation and final protection failed');throw error;}}
}
function deepFreeze(v){if(v&&typeof v==='object'){for(const x of Object.values(v))deepFreeze(x);Object.freeze(v);}return v;}
export async function runSecretRuntime({configDescriptor}={}){
 const frame=await prepareRuntime(configDescriptor);try{const body=await import(pathToFileURL(join(HERE,'runtime-body.mjs')));return await body.runParent(frame);}finally{await frame.recheck();}
}
export async function runSecretWorker({configDescriptor,scenario}={}){
 need(['retained','fresh','wrapper'].includes(scenario),'Exact finite worker scenario');const frame=await prepareRuntime(configDescriptor);try{const body=await import(pathToFileURL(join(HERE,'runtime-body.mjs')));return await body.runWorker(frame,scenario);}finally{await frame.recheck();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 need(process.argv.length===(process.argv[2]==='parent'?4:5)&&['parent','worker'].includes(process.argv[2]),'Exact new own runtime CLI');
 const configDescriptor=JSON.parse(process.argv[3]),result=process.argv[2]==='parent'?await runSecretRuntime({configDescriptor}):await runSecretWorker({configDescriptor,scenario:process.argv[4]});process.stdout.write(JSON.stringify(result)+'\n');
}
