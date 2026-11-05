// Dormant selected-clock ReactDOM runtime/transpile; only Node builtins before full auth.
import {readFile,lstat,readdir,realpath,open,mkdir,statfs,readlink} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import Module,{createRequire} from 'node:module';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/clock-v13-runtime-candidate-v2';
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


export const INTERFACES=Object.freeze(['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10']);
export function artifactModel(p,contract,refs){
 need(p?.schemaVersion===1&&p.state==='INDEPENDENT_CLOCK_V13_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'&&p.verifiedPassed===true,'Actual clock-selected artifact proof');
 need(p.componentSourceIndexSha256===refs.componentSourceIndex.sha256&&p.componentSha256===refs.component.sha256&&p.engineSha256===refs.nativeEngine.sha256,'Actual original component/native/source identities');
 need(p.nativeSourceFiles===342&&p.externalEmbeddingSources===3&&p.fullMetadataFields===64&&p.selectedManifestCount===9,'Whole accepted native342+3/64/9 only');
 need(same([...p.emittedImports].sort(),[...INTERFACES].sort())&&same(p.publicAbiFunctions,['run']),'Exactly three standard callable0.2.10 interfaces and sole run');
 for(const k of ['ordinaryGuestExportsInvoked','generatedModuleImported','runtimeAcceptanceClaim','operationalAdmission'])need(p[k]===false,'Construction scope only '+k);
 need(contract?.schemaVersion===1&&same(contract.artifacts,p.artifacts)&&same(p.artifacts,refs.artifacts),'Whole exact actual artifact contract/map');return true;
}
export function phaseModel(root,own,refs,phase){
 need(root?.schemaVersion===1&&root.state==='ROOT_REVIEWED_CLOCK_V13_REACTDOM_DIFFERENTIAL_V2'&&root.phase===phase&&same(root.sourceIndex,own),'New own Root phase/source');
 need(['mapped-transpile','runtime-differential'].includes(phase)&&root.variant==='normal-off'&&same(root.actualArtifactReview,refs.actualArtifactReview)&&same(root.actualArtifactContract,refs.actualArtifactContract),'Exact actual proof, distinct finite phases');
 need(root.componentSha256===refs.component.sha256&&root.outputRoot===(phase==='mapped-transpile'?refs.mappedOutputRoot:refs.runtimeOutputRoot),'Same reviewed component and fixed fresh output');
 need(same(root.selectedInterfaces,INTERFACES)&&same(root.mappingOptions,refs.mappingOptions),'Unchanged actual selected interfaces/standard mapping');
 need(root.mappedTranspileAllowed===(phase==='mapped-transpile')&&root.jcoCompilerWasmHelpersAllowed===(phase==='mapped-transpile'),'No implicit compilation action');
 need(root.generatedApplicationImportAllowed===(phase==='runtime-differential')&&root.ordinaryRunAllowed===(phase==='runtime-differential')&&root.stockWasmtimeAllowed===(phase==='runtime-differential'),'No application work during mapping');
 need(root.nativeReadOnlyPreflightAllowed===true,'Genuine original native read-only API explicitly allowed');
 need(root.externalOutputRoot===root.outputRoot+'-external-root'&&same(root.monitorIndex,refs.monitorIndex)&&same(root.monitorEntry,refs.monitorEntry),'Genuine owned external monitor/context');
 need(root.standardShimWorkerThreadsAllowed===true&&root.ownedWorkerDeadlineMs===180000&&root.requiredExternalParentDeadlineSeconds===1200,'Real standard worker shim and external deadlines');
 for(const k of ['customHostServicesAllowed','componentConstructionAllowed','nativeBuildAllowed','engineReplacementAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','otherGuestAllowed','resourceSevenCaseProfileAccepted','clockProfilePromotionAllowed','dateTimerSnapshotTeardownAccepted','resetOrReuseAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed'])need(root[k]===false,'Slice does not grant '+k);
 if(phase==='runtime-differential')need(root.actualMappedOutputReview&&root.actualMappedOutputReview.path,'Separate actual mapped-output proof required');
 else need(root.actualMappedOutputReview===null,'No mapped proof invented in advance');return true;
}

export function nativeFrameModel(frame,refs,metadata){
 need(frame&&Object.isFrozen(frame)&&same(Reflect.ownKeys(frame),['enginePath','sourceRoot','metadata','pin','variant','recheck']),'Whole genuine classicPreflight frame');
 need(frame.variant==='normal-off'&&frame.enginePath===refs.nativeEngine.path&&frame.sourceRoot===refs.nativeSourceRoot&&same(frame.metadata,metadata),'Exact original native context/whole sidecar');
 need(metadata.engineSha256===refs.nativeEngine.sha256&&metadata.engineBytes===refs.nativeEngine.bytes&&metadata.sourceManifest.length===342&&metadata.componentizeSourceManifest.length===3&&metadata.selectedModuleManifests.length===9,'Actual342+3/9 metadata');
 need(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE==='Release'&&metadata.entropyPolicy==='off'&&metadata.gcStress===false&&metadata.oomTesting===false,'Real normalOFF Release');
 need(frame.pin.sourceFiles===342&&frame.pin.engineSha256===refs.nativeEngine.sha256&&frame.pin.receiptSha256===refs.nativeMetadata.sha256&&frame.pin.componentizeSourceRoot===refs.nativeEmbeddingSourceRoot,'Genuine original frozen pin, no metadata projection');
 const d=Object.getOwnPropertyDescriptor(frame,'recheck');need(d&&typeof d.value==='function'&&d.enumerable&&!d.writable&&!d.configurable,'Fresh actual native recheck');return true;
}
export function environmentModel(env,execArgv,version){
 need(version==='v22.14.0'&&same(execArgv,[]),'Plain pinned fresh Node22');
 for(const k of ['NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','NODE_COMPAT_LEGACY_COMPONENTIZER'])need(!env[k],'No startup/package override '+k);
 return true;
}
async function noExternalSearchRoots(packageRoot){
 const physical=p=>p.replace(/^\/tmp(?=\/|$)/,'/private/tmp'),roots=new Set(Module.globalPaths.map(physical));for(let p=dirname(packageRoot);;p=dirname(p)){roots.add(join(p,'node_modules'));if(dirname(p)===p)break;}
 for(const path of roots){if(path.startsWith(packageRoot+'/'))continue;let s;try{s=await lstat(path);}catch(error){need(error.code==='ENOENT','Observe actual external dependency-search absence');}need(s===undefined,'No external Node dependency-search root '+path);}
}
async function packageContext(c,refs,prior){
 const inventory=await c.read(refs.packageInventory),v=inventory.package;need(v.root===refs.loaderPackageRoot&&v.files.length===4889&&v.links.length===21,'Whole actual private package inventory');
 const root=await lstat(v.root);need(root.isDirectory()&&!root.isSymbolicLink()&&(root.mode&0o777)===0o700,'Private package root');const id=[root.dev,root.ino];if(prior)need(same(prior,id),'Package root identity unchanged');
 const names=new Set(),links=new Map();for(const r of v.files){relative(r.relativePath);need(!names.has(r.relativePath)&&r.path===join(v.root,r.relativePath),'Exact package row');names.add(r.relativePath);await c.file(r);const s=await lstat(r.path);need(s.nlink===1&&(s.mode&0o777)===r.mode,'Independent package file/mode');}
 for(const r of v.links){relative(r.path);need(!names.has(r.path)&&!links.has(r.path),'Unique declared alias');links.set(r.path,r);}
 const actual=new Set();async function walk(path,prefix=''){for(const n of await readdir(path)){const p=join(path,n),name=prefix+n,s=await lstat(p);if(s.isSymbolicLink()){const link=links.get(name);need(link&&await readlink(p)===link.target&&await realpath(p)===link.resolvedPath&&names.has(relativePath(v.root,link.resolvedPath)),'Exact package alias text/target');actual.add(name);}else if(s.isDirectory()){need((s.mode&0o777)===0o700,'Private package dirs');await walk(p,name+'/');}else{need(s.isFile(),'Regular package members');actual.add(name);}}}
 function relativePath(root,path){need(path.startsWith(root+'/'),'Alias target inside exact package');return path.slice(root.length+1);}
 await walk(v.root);need(actual.size===names.size+links.size&&[...names,...links.keys()].every(n=>actual.has(n)),'Complete package file/alias membership');return id;
}
async function authenticate(input,phase){
 const configRow=captureDescriptor(input);need(HERE===ORIGINAL,'Own real clock runtime Source context');environmentModel({...process.env},process.execArgv,process.version);const c=new Capture();let primary=null,primaryPresent=false;
 try{
  const cfg=await c.read(configRow),own=captureDescriptor(cfg.sourceIndex);need(cfg.schemaVersion===1&&cfg.state==='CLOCK_V13_REACTDOM_CONFIG_V2'&&own.path===join(HERE,'index.json'),'Exact new own config/Source');const rows=await c.family(own),refs=await c.read(rows.find(r=>r.path===join(HERE,'references.json'))),inputs=await c.read(rows.find(r=>r.path===join(HERE,'source-inputs.json')));
  need(inputs.schemaVersion===1&&inputs.files.length>=11581&&inputs.files.length<=25000&&new Set(inputs.files.map(r=>r.path)).size===inputs.files.length,'Complete finite current native/tool/old-proof intake');for(const r of inputs.files)await c.file(r);for(const ix of inputs.families)await c.family(ix);const packageIdentity=await packageContext(c,refs,null);await noExternalSearchRoots(refs.loaderPackageRoot);
  const rootRow=captureDescriptor(cfg.rootAuthority),root=await c.read(rootRow);phaseModel(root,own,refs,phase);need(same(root.entry,rows.find(r=>r.path===join(HERE,'entry.mjs'))),'Exact actual own entry');
  const peer=await c.proof(root.sourceIndependentReview);need(peer.schemaVersion===1&&peer.state==='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_PASSED_V2'&&peer.sourceIndexSha256===own.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true,'Independent own Source peer');for(const k of ['ownerActionsInvoked','hostActionsInvoked','runtimeActionsInvoked'])need(peer[k]===false,'Source peer no phase '+k);
  const held=await c.proof(refs.previousSourceHold),correction=await c.read(refs.requiredCorrectionContract);need(held.state==='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_HELD_V1'&&held.sourceReviewPassed===false&&held.sourceIndexSha256===refs.previousSourceIndex.sha256&&same(correction.heldSourceIndex,refs.previousSourceIndex),'Exact prior null-presence Source HOLD, never action authority');
  need(refs.actualArtifactReview&&refs.actualArtifactContract,'Real completed artifact proof, never NULL readiness');const proof=await c.proof(refs.actualArtifactReview),contract=await c.read(refs.actualArtifactContract);artifactModel(proof,contract,refs);const proofRows=await c.family(refs.actualArtifactReview.index);need(proofRows.filter(r=>same(r,refs.actualArtifactContract)).length===1,'Whole actual artifact contract indexed once');
  for(const r of Object.values(refs.artifacts))await c.file(r);for(const[k,v]of Object.entries(refs.requiredNativeReadOnlyEnvironment))need(process.env[k]===v,'Genuine native consumed-context environment '+k);
  need(await realpath(process.execPath)===refs.node.path,'Pinned actual plain Node22');await c.file(refs.node);await c.recheck();return{c,refs,root,rootRow,configRow,own,packageIdentity};
 }catch(error){primaryPresent=true;primary=error;throw error;}finally{try{await c.recheck();}catch(error){if(primaryPresent)throw new AggregateError([primary,error],'Clock admission and final protection failed');throw error;}}
}
async function prepare(input,phase){
 const f=await authenticate(input,phase);let native=null,primary=null,primaryPresent=false;
 const recheck=async()=>{if(native)await native.recheck();await packageContext(f.c,f.refs,f.packageIdentity);await noExternalSearchRoots(f.refs.loaderPackageRoot);await f.c.recheck();};
 try{
  const {classicPreflight}=await import(pathToFileURL(f.refs.nativePreflight.path));native=await classicPreflight({variant:'normal-off'});nativeFrameModel(native,f.refs,await f.c.read(f.refs.nativeMetadata));need(Object.keys(native.metadata).length===64,'Full original64-field native sidecar');await recheck();return Object.freeze({...f,native,recheck});
 }catch(error){primaryPresent=true;primary=error;throw error;}finally{try{await recheck();}catch(error){if(primaryPresent)throw new AggregateError([primary,error],'Clock native preparation/final protection failed');throw error;}}
}
export async function prepareMappedClock({configDescriptor}={}){
 const f=await prepare(configDescriptor,'mapped-transpile');try{const body=await import(pathToFileURL(join(HERE,'body.mjs')));return await body.prepareMapped(f);}finally{await f.recheck();}
}
export async function runClockDifferential({configDescriptor}={}){
 const f=await prepare(configDescriptor,'runtime-differential');try{const body=await import(pathToFileURL(join(HERE,'body.mjs')));return await body.runDifferential(f);}finally{await f.recheck();}
}
export async function runClockJcoWorker({configDescriptor,scenario}={}){
 need(['retained','fresh'].includes(scenario),'Finite Jco scenario');const f=await prepare(configDescriptor,'runtime-differential');try{const body=await import(pathToFileURL(join(HERE,'body.mjs')));return await body.runJcoWorker(f,scenario);}finally{await f.recheck();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 need(['map','runtime','jco-worker'].includes(process.argv[2])&&process.argv.length===(process.argv[2]==='jco-worker'?5:4),'Exact finite clock CLI');const configDescriptor=JSON.parse(process.argv[3]);let result;
 if(process.argv[2]==='map')result=await prepareMappedClock({configDescriptor});else if(process.argv[2]==='runtime')result=await runClockDifferential({configDescriptor});else result=await runClockJcoWorker({configDescriptor,scenario:process.argv[4]});process.stdout.write(JSON.stringify(result)+'\n');
}
