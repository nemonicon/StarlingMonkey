// Unexecuted combined355 Source proposal; no operational action authorized; only Node builtins before full auth.
import {readFile,lstat,readdir,realpath,readlink} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/combined-native-component-caller-candidate-v1';
const same=isDeepStrictEqual,sha=b=>createHash('sha256').update(b).digest('hex');
function need(v,m){if(!v)throw new Error(m);}
export function prerequisiteModel(refs){
 need(refs.fixtureSourceIndex&&refs.fixtureSourcePeer&&refs.fixtureReviewRequiredState&&refs.fixtureReviewSourceField&&refs.readOnlyConfig&&refs.actualReadOnlyReview&&refs.actualReadOnlyContract&&refs.actualReadOnlyRequiredState&&refs.actualReadOnlyData&&refs.actualBootstrapReview&&refs.actualBootstrapContract,'Pending actual prerequisites/fixture peer; draft cannot authorize action');return true;
}
export function captureDescriptor(value){
  const r=Object.freeze({path:value?.path,sha256:value?.sha256,bytes:value?.bytes});
  need(typeof r.path==='string'&&isAbsolute(r.path)&&resolve(r.path)===r.path&&!r.path.includes('\\')&&!r.path.includes('\0'),'Canonical absolute descriptor; no normalization');
  need(typeof r.sha256==='string'&&/^[a-f0-9]{64}$/.test(r.sha256)&&Number.isSafeInteger(r.bytes)&&r.bytes>=0&&r.bytes<=2**40,'Exact descriptor primitives');return r;
}
function relative(n){need(typeof n==='string'&&n&&!isAbsolute(n)&&!n.includes('\\')&&!n.includes('\0')&&n.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Confined local name');return n;}
function identity(s){return [s.dev,s.ino,s.size,s.mtimeMs,s.ctimeMs,s.mode,s.nlink];}
class Capture {
  rows=new Map();families=[];packageTrees=[];
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
  async packageTree(inventory,root){
    need(inventory.root===root&&inventory.files.length===4889&&inventory.links.length===21,'Exact reviewed private4889+21 package');const dir=await lstat(root);need(dir.isDirectory()&&!dir.isSymbolicLink()&&(dir.mode&0o777)===0o700,'Private package root');
    const names=new Set(),links=new Map();for(const r of inventory.files){const n=relative(r.relativePath);need(!names.has(n)&&r.path===join(root,n),'Exact unique package role');names.add(n);await this.file({path:r.path,sha256:r.sha256,bytes:r.bytes});const s=await lstat(r.path);need((s.mode&0o777)===r.mode&&s.nlink===1,'Package actual mode/independent file');}for(const r of inventory.links){relative(r.path);need(!names.has(r.path)&&!links.has(r.path),'Unique package alias');links.set(r.path,r);}
    const t={root,rootIdentity:[dir.dev,dir.ino],names,links};await this.checkPackage(t);this.packageTrees.push(t);
  }
  async checkPackage(t){const s=await lstat(t.root);need(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o777)===0o700&&same([s.dev,s.ino],t.rootIdentity),'Package root identity');const actual=new Set();async function walk(base,prefix=''){for(const n of await readdir(base)){const p=join(base,n),name=prefix+n,x=await lstat(p);if(x.isDirectory())await walk(p,name+'/');else if(x.isSymbolicLink()){const d=t.links.get(name);need(d&&await readlink(p)===d.target&&await realpath(p)===d.resolvedPath&&d.resolvedPath.startsWith(t.root+'/')&&t.names.has(d.resolvedPath.slice(t.root.length+1)),'Exact confined package alias');actual.add(name);}else{need(x.isFile()&&t.names.has(name),'Declared package file');actual.add(name);}}}await walk(t.root);need(actual.size===t.names.size+t.links.size&&[...t.names,...t.links.keys()].every(n=>actual.has(n)),'Exact private package membership');}
  async recheck(){for(const {r}of [...this.rows.values()])await this.file(r);for(const {base,names}of this.families)await this.tree(base,names);for(const t of this.packageTrees)await this.checkPackage(t);}
}

export function nativeRecordModel(record,refs,metadata,expectedBootstrap,expectedRecordData=null){
 need(record&&Object.isFrozen(record)&&same(Reflect.ownKeys(record),['schemaVersion','kind','sourceIndex','actualReview','bootstrap','currentVerification','recheck']),'Whole genuine combined retained record');
 need(record.schemaVersion===1&&record.kind==='retained-combined355-bootstrap-v1'&&same(record.sourceIndex,refs.nativeApiSourceIndex)&&same(record.actualReview,refs.actualBootstrapReview),'Actual new combined API/proof roles');
 if(expectedRecordData!==null)need(same(Object.fromEntries(Object.entries(record).filter(([k])=>k!=='recheck')),expectedRecordData),'Whole current six DATA properties equal the independently reviewed actual retained record; fresh own callable separate');
 const b=record.bootstrap,v=record.currentVerification,n=b.nativeFrame;need(same(b,expectedBootstrap),'Entire actual operational bootstrap DATA retained unchanged');
 need(b.nativeSourceFiles===355&&b.externalEmbeddingSources===3&&b.fullMetadataFields===80&&b.selectedManifestCount===11&&same(b.engine,refs.nativeEngine)&&same(b.metadataDescriptor,refs.nativeMetadata)&&same(b.freezeReceipt,refs.freezeReceipt),'Genuine combined355+3/80/11 frozen tuples');
 need(same(b.metadata,metadata)&&Object.keys(metadata).length===80&&metadata.sourceManifest.length===355&&metadata.componentizeSourceManifest.length===3&&metadata.selectedModuleManifests.length===11&&b.selectedManifests.length===11,'Full metadata and eleven whole manifests, never 342/64 or355/75');
 need(n.state==='COMBINED355_FROZEN_FULL80_NATIVE_DATA_VERIFIED_NO_ACTION_AUTHORITY_V1'&&same(n.metadata,metadata)&&same(n.selectedManifests,b.selectedManifests)&&same(b.pin.nativeFrame,n),'Whole native frame/pin/manifests');
 need(n.verificationCapsule.state==='COMBINED355_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1'&&same(n.verificationCapsule.engine,refs.nativeEngine)&&same(n.verificationCapsule.metadata,refs.nativeMetadata),'Exact unchanged historical verifier capsule, no state relabel');
 need(n.rawMetadataPathsPreserved===true&&metadata.enginePath!==b.enginePath&&b.enginePath===refs.nativeEngine.path&&metadata.gcStress===false&&metadata.oomTesting===false&&metadata.entropyPolicy==='off'&&metadata.observedCMakeOptions.CMAKE_BUILD_TYPE==='Release','Original configured metadata versus actual frozen engine');
 need(same(n.runtimeBackendProof,{verified:false,version:null,vernum:null})&&n.remaining15DeviationsApproved===false&&b.currentFrozenVerifierCalls===1&&b.validationBootstrapOnly===true,'Pending native/runtime/deviation gates remain literal historical DATA');
 for(const k of ['engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','grantsRuntimeAuthority'])need(b[k]===false,'Bootstrap history does not authorize construction '+k);
 need(v.kind==='current-read-hash-verification-v1'&&same(v.config,refs.readOnlyConfig)&&same(v.sourceIndex,refs.nativeApiSourceIndex)&&v.fullMetadataFields===80&&v.selectedWholeManifests===11,'Distinct fresh read-only record context');
 for(const k of ['helperInvocations','processesSpawned','filesCreated'])need(v[k]===0,'No helper/action in current readonly API '+k);
 for(const k of ['engineExecuted','guestExecuted','operationalAdmission'])need(v[k]===false,'Read-only current scope '+k);
 const d=Object.getOwnPropertyDescriptor(record,'recheck');need(d&&typeof d.value==='function'&&d.enumerable&&!d.writable&&!d.configurable,'Fresh genuine own readonly recheck');return b;
}
export function phaseModel(root,own,refs,fixture,phase){
 need(root?.schemaVersion===1&&root.state==='ROOT_REVIEWED_COMBINED355_COMPONENT_CALLER_V1'&&root.phase===phase&&same(root.sourceIndex,own),'New exact combined caller phase/Source');
 need(['bundle','construct'].includes(phase)&&root.fixtureId===fixture.id&&same(root.fixtureSource,fixture.source)&&same(root.fixtureWit,fixture.wit)&&root.worldName===fixture.worldName,'Exact selected whole fixture/WIT');
 need(root.bundlePreparationAllowed===(phase==='bundle')&&root.componentConstructionAllowed===(phase==='construct')&&root.engineInitializationAllowed===(phase==='construct')&&root.nativeReadOnlyApiAllowed===true,'Separate genuine bundle and construction permissions');
 need(root.nativeSourceFiles===355&&root.externalEmbeddingSources===3&&root.fullMetadataFields===80&&root.selectedWholeManifests===11&&same(root.nativeEngine,refs.nativeEngine)&&same(root.nativeMetadata,refs.nativeMetadata),'Current full80/native355 context');
 need(same(root.readOnlyConfig,refs.readOnlyConfig)&&same(root.actualBootstrapReview,refs.actualBootstrapReview)&&same(root.actualReadOnlyReview,refs.actualReadOnlyReview),'Actual new readonly prerequisites only');
 need(same(root.selectedInterfaces,fixture.selectedInterfaces)&&same(root.disableFeatures,fixture.disableFeatures)&&root.selectedInterfaces.every(x=>['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10'].includes(x)),'Explicit opt-in standard clock/poll only');
 if(fixture.id==='pure')need(root.selectedInterfaces.length===0,'Pure component requires imports[]');
 for(const k of ['ordinaryGuestExportsAllowed','generatedModuleImportAllowed','keyOrCryptoAllowed','hostServersAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','unsafeResetAllowed','metadataProjectionAllowed','sourcePromotionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed'])need(root[k]===false,'No extra phase '+k);
 need(root.outputRoot===refs.outputBase+'-'+phase+'-'+fixture.id&&root.externalRoot===root.outputRoot+'-external-root'&&root.privateTemporaryRoot===root.outputRoot+'-tmp','Fixed fresh phase/fixture roots');
 need(root.ownedNodeDeadlineSeconds===(phase==='bundle'?1200:2400)&&root.maxComponentBytes===67108864&&root.maxBundleBytes===33554432,'Genuine finite external watchdog/capture policy');
 need(root.actualComponentReview===null&&root.actualRuntimeAuthority===null,'No result/runtime authority in advance');
 if(phase==='construct')need(root.bundleReport&&root.bundle&&root.bundleExternalTerminal&&root.loaderConfig&&root.loaderRootAuthority&&root.guestSourceSha256===root.bundle.sha256&&root.witWorldSha256===fixture.wit.sha256,'Root binds actual separate bundle and genuine paired loader/exact WIT; no Root minting');
 return true;
}
export function environmentModel(env,execArgv,version){
 need(version==='v22.14.0'&&same(execArgv,[]),'Plain fresh pinned Node22');
 for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','NODE_COMPAT_LEGACY_COMPONENTIZER','NODE_COMPAT_COMPONENTIZE_MODULE'])need(!env[k],'No startup/package override '+k);return true;
}
async function contractProof(c,pair,contractRow,expectedState){
 need(pair!==null&&contractRow!==null&&typeof expectedState==='string','Required actual DATA proof is pending; no action');
 const rows=await c.family(pair.index);need(rows.filter(r=>same(r,pair.result)).length===1&&rows.filter(r=>same(r,contractRow)).length===1,'Exact indexed proof/contract once');const proof=await c.read(pair.result),contract=await c.read(contractRow);need(proof.schemaVersion===1&&proof.state===expectedState&&proof.verifiedPassed===true&&contract.requiredReviewState===expectedState,'Real prerequisite, not Source proposal');
 for(const group of ['requiredFixedValues','requiredExactDescriptors'])for(const[k,v]of Object.entries(contract[group]??{}))need(same(proof[k],v),'Whole actual prerequisite '+k);if(contract.requiredCoverage)need(same(proof.coverage,contract.requiredCoverage),'Whole actual coverage');
 // Follow only the finite current exact-role contract, never arbitrary nested
 // historical metadata descriptors (including the unretained57-byte digest).
 const exact=async v=>{if(!v||typeof v!=='object')return;if(same(Object.keys(v).sort(),['bytes','path','sha256'])){await c.file(v);return;}if(v.index&&v.result&&Object.keys(v).length===2){await c.proof(v);return;}for(const x of Object.values(v))await exact(x);};await exact(contract.requiredExactDescriptors);return{proof,contract};
}
async function authenticate(input,phase){
 need(HERE===ORIGINAL,'Original new combined caller context');environmentModel({...process.env},process.execArgv,process.version);const c=new Capture();let primary=null,primaryPresent=false;
 try{
  const configRow=captureDescriptor(input),cfg=await c.read(configRow),own=captureDescriptor(cfg.sourceIndex);need(cfg.schemaVersion===1&&cfg.state==='COMBINED355_COMPONENT_CALLER_CONFIG_V1'&&cfg.phase===phase&&own.path===join(HERE,'index.json'),'Exact own phase/config');
  const rows=await c.family(own),refs=await c.read(rows.find(r=>r.path===join(HERE,'references.json'))),inputs=await c.read(rows.find(r=>r.path===join(HERE,'source-inputs.json')));
  for(const r of inputs.files)await c.file(r);for(const ix of inputs.families)await c.family(ix);for(const bound of inputs.boundaries){const b=await c.read(bound.manifest);need(Array.isArray(b[bound.field])&&b[bound.field].length===bound.expectedRows,'Exact compact boundary rows');for(const r of b[bound.field])await c.file(r);for(const ix of b[bound.familyField]??[])await c.family(ix);}await c.packageTree((await c.read(refs.packageInventory)).package,refs.loaderPackageRoot);
  prerequisiteModel(refs);
  const catalogue=await c.read(refs.fixtureCatalogue),fixture=catalogue.fixtures.find(x=>x.id===cfg.fixtureId);need(fixture&&catalogue.nativeGeneration==='new-combined355-normal-off','One exact genuine fixture');await c.file(fixture.source);await c.file(fixture.wit);
  const rootRow=captureDescriptor(cfg.rootAuthority),root=await c.read(rootRow);phaseModel(root,own,refs,fixture,phase);need(same(root.entry,rows.find(r=>r.path===join(HERE,'entry.mjs')))&&same(root.externalController,rows.find(r=>r.path===join(HERE,'external.py'))),'Actual own entry/controller');
  const peer=await c.proof(root.sourceIndependentReview);need(peer.state==='INDEPENDENT_COMBINED355_COMPONENT_CALLER_SOURCE_REVIEW_PASSED_V1'&&peer.componentSourceIndexSha256===own.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true&&peer.ownerActionsInvoked===false,'Separate new caller Source peer');
  const fp=await c.proof(refs.fixtureSourcePeer);need(fp.sourceOnly===true&&fp.sourceReviewPassed===true&&fp.ownerActionsInvoked===false&&typeof refs.fixtureReviewRequiredState==='string'&&fp.state===refs.fixtureReviewRequiredState&&typeof refs.fixtureReviewSourceField==='string'&&fp[refs.fixtureReviewSourceField]===refs.fixtureSourceIndex.sha256,'Real fixture Source peer, no self-approval');
  const np=await c.proof(refs.nativeApiSourcePeer);need(np.state==='INDEPENDENT_COMBINED355_NATIVE_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V1'&&np.toolingSourceIndexSha256===refs.nativeApiSourceIndex.sha256&&np.sourceReviewPassed===true&&np.ownerActionsInvoked===false,'Actual c365 API Source peer');
  const lp=await c.proof(refs.loaderSourcePeer);need(lp.state==='INDEPENDENT_CLOCK_PACKAGE_LOADER_SOURCE_REVIEW_PASSED_V2'&&lp.sourceIndexSha256===refs.loaderSourceIndex.sha256&&lp.sourceReviewPassed===true&&lp.ownerActionsInvoked===false,'Actual loader V2 Source peer');
  const bp=await contractProof(c,refs.actualBootstrapReview,refs.actualBootstrapContract,'INDEPENDENT_COMBINED355_NORMAL_OFF_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1'),rp=await contractProof(c,refs.actualReadOnlyReview,refs.actualReadOnlyContract,refs.actualReadOnlyRequiredState);need(same(rp.proof.actualBootstrapReview,refs.actualBootstrapReview)&&same(rp.proof.config,refs.readOnlyConfig)&&same(rp.proof.retainedData,refs.actualReadOnlyData)&&rp.proof.toolingSourceIndexSha256===refs.nativeApiSourceIndex.sha256,'Actual combined retained record proof/direct roles');const expectedRecordData=await c.read(refs.actualReadOnlyData);
  need(bp.proof.toolingSourceIndexSha256===refs.nativeApiSourceIndex.sha256&&bp.proof.nativeSourceFiles===355&&bp.proof.fullMetadataFields===80&&bp.proof.selectedManifestCount===11,'Actual combined bootstrap proof');const expectedBootstrap=await c.read(bp.proof.bootstrapFrame),metadata=await c.read(refs.nativeMetadata);
  const readOnlyConfig=await c.read(refs.readOnlyConfig);need(readOnlyConfig.state==='COMBINED355_NATIVE_READ_ONLY_BOOTSTRAP_CONFIG_V1'&&same(readOnlyConfig.toolingIndex,refs.nativeApiSourceIndex),'Genuine retained API config context');await c.read(readOnlyConfig.rootAuthority);
  if(phase==='construct'){
   const br=await c.read(root.bundleReport);need(br.state==='COMBINED355_BUNDLE_COMPLETE_UNREVIEWED_V1'&&same(br.fixtureSource,fixture.source)&&same(br.fixtureWit,fixture.wit)&&same(br.bundle,root.bundle)&&br.nativeSourceFiles===355&&br.selectedWholeManifests===11,'Exact separately produced bundle roles');await c.file(root.bundle);need(same(br.sourceIndex,own)&&br.fixtureId===fixture.id&&br.primaryPresent===false&&br.finalProtectionErrors.length===0&&br.fixtureEvaluated===false&&br.packagerLoaded===false&&br.allElevenManifestsUsed===true,'Complete genuine bundle phase data');const bt=await c.read(root.bundleExternalTerminal);need(bt.rawExitCode===0&&bt.parentOwnedGroupGone===true&&bt.allObservedOwnedGroupsGone===true&&bt.timeout===false&&bt.forcedCleanup===false&&bt.errors.length===0&&bt.signals.length===0&&bt.interruptedSignals.length===0&&bt.remainingObservedPids.length===0,'Actual separately owned bundle raw0/cleanup');
   const lc=await c.read(root.loaderConfig),lr=await c.read(root.loaderRootAuthority);need(lc.state==='CLOCK_PACKAGE_LOADER_CONFIG_V2'&&same(lc.sourceIndex,refs.loaderSourceIndex)&&same(lc.rootAuthority,root.loaderRootAuthority)&&lr.state==='ROOT_REVIEWED_EXPERIMENTAL_CLOCK_PACKAGE_CONSTRUCTION_V2'&&same(lr.sourceIndependentReview,refs.loaderSourcePeer),'Genuine original loader config/Root');need(lr.packageRoot===refs.loaderPackageRoot&&same(lr.sourceIndex,refs.loaderSourceIndex)&&lr.phase==='experimental-component-construction'&&lr.packageModuleInitializationAllowed===true&&lr.componentConstructionAllowed===true&&lr.engineInitializationDuringConstructionAllowed===true&&lr.nativeArtifactAdmissionMustBePerformedByCaller===true&&lr.freshOwnedNodeProcessRequired===true,'Actual narrow loader role');for(const k of ['nativeEngine','nativeMetadata','guestSourceSha256','witWorldSha256','worldName','selectedInterfaces','disableFeatures','privateTemporaryRoot'])need(same(lr[k],root[k]),'Paired actual construction/loader role '+k);
  }
  need(await realpath(process.execPath)===refs.node.path,'Actual pinned Node executable');await c.file(refs.node);await c.recheck();return{c,configRow,own,refs,rootRow,root,fixture,expectedBootstrap,expectedRecordData,metadata};
 }catch(error){primary=error;primaryPresent=true;throw error;}finally{try{await c.recheck();}catch(error){if(primaryPresent)throw new AggregateError([primary,error],'Caller authentication and final protection failed');throw error;}}
}
export async function runCombinedCaller({configDescriptor,phase}={}){
 const f=await authenticate(configDescriptor,phase);let record=null,primary=null,primaryPresent=false;const recheck=async()=>{if(record)await record.recheck();await f.c.recheck();};
 try{
  const api=await import(pathToFileURL(f.refs.nativeApi.path));need(typeof api.combinedNativeBootstrapPreflight==='function','Genuine full80 combined API');record=await api.combinedNativeBootstrapPreflight({configDescriptor:f.refs.readOnlyConfig});nativeRecordModel(record,f.refs,f.metadata,f.expectedBootstrap,f.expectedRecordData);await recheck();
  const body=await import(pathToFileURL(join(HERE,phase==='bundle'?'bundle.mjs':'construct.mjs')));return await body.run({...f,record,recheck});
 }catch(error){primary=error;primaryPresent=true;throw error;}finally{try{await recheck();}catch(error){if(primaryPresent)throw new AggregateError([primary,error],'Caller phase and final protection failed');throw error;}}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===4&&['bundle','construct'].includes(process.argv[2]),'Exact separate caller phase/config');const value=await runCombinedCaller({phase:process.argv[2],configDescriptor:JSON.parse(process.argv[3])});process.stdout.write(JSON.stringify(value)+'\n');if(value.completeUnreviewed!==true)process.exitCode=1;}
