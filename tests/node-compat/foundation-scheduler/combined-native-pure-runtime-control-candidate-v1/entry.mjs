// Unexecuted combined355 Source proposal; no operational action authorized; only Node builtins before full auth.
import {readFile,lstat,readdir,realpath,readlink} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/combined-native-pure-runtime-control-candidate-v1';
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

export function artifactModel(p,contract,refs){
 need(p?.schemaVersion===1&&p.state==='INDEPENDENT_COMBINED355_PURE_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'&&p.verifiedPassed===true&&same(p.acceptedFixtureIds,['pure']),'Actual per-pure artifact proof, no overall fixture projection');
 need(contract?.schemaVersion===1&&contract.requiredReviewState===p.state,'Exact executable artifact contract state');
 for(const[k,v]of Object.entries(contract.requiredFixedValues??{}))need(same(p[k],v),'Every versioned artifact fixed value '+k);
 need(p.componentSourceIndexSha256===refs.callerSourceIndex.sha256&&p.componentSha256===refs.component.sha256&&p.engineSha256===refs.nativeEngine.sha256&&p.metadataSha256===refs.nativeMetadata.sha256,'Same actual combined component/native/metadata');
 need(p.nativeSourceFiles===355&&p.externalEmbeddingSources===3&&p.fullMetadataFields===80&&p.selectedWholeManifests===11&&same(p.emittedImports,[])&&same(p.publicAbiFunctions,['run']),'Full80/355+3/11, pure imports[] and sole run');
 need(same(p.publicAbiSignatures,[{name:'run',params:[],result:'string'}]),'Exact actual zero-argument string scalar ABI');
 need(same(p.generatedFiles,refs.generated)&&same(contract.generatedFiles,p.generatedFiles)&&same(contract.artifacts,p.artifacts),'Whole actual artifact contract/generated maps');
 for(const k of ['ordinaryGuestExportsInvoked','generatedApplicationModuleImported','keyOrCryptoWorkloadsInvoked','operationalAdmission','runtimeAcceptanceClaim','allSixFixtureArtifactContractSatisfied'])need(p[k]===false,'Artifact-only existing scope '+k);return true;
}
export function rootModel(root,own,refs){
 need(root?.schemaVersion===1&&root.state==='ROOT_REVIEWED_COMBINED355_PRELIMINARY_PURE_CONTROL_V1'&&same(root.sourceIndex,own),'New explicit pure-control Root');
 need(root.nativeSourceFiles===355&&root.externalEmbeddingSources===3&&root.fullMetadataFields===80&&root.selectedWholeManifests===11,'Exact current native context');
 for(const k of ['actualPureReview','actualPureContract','component','fixtureSource','readOnlyConfig'])need(same(root[k],refs[k]),'Exact actual pure/native role '+k);
 for(const k of ['parentNativeReadOnlyApiAllowed','nodeFixtureOracleAllowed','pureGeneratedImportAllowed','pureRunAllowed','stockWasmtimeAllowed'])need(root[k]===true,'Distinct issued action '+k);
 need(root.outputRoot===refs.outputRoot&&root.externalRoot===refs.outputRoot+'-external-root'&&root.parentDeadlineSeconds===1200&&root.childDeadlineMs===60000,'Fresh bounded roots and real deadlines');
 need(root.parentNativeApiCalls===1&&root.childNativeApiCalls===0&&root.nodeOracleCalls===3&&root.retainedJcoCalls===3&&root.freshJcoCalls===1&&root.freshWasmtimeCalls===3&&root.componentValues===7&&root.totalValues===10,'Exact preliminary schedule');
 for(const k of ['resourceRuntimeAllowed','otherGuestAllowed','componentConstructionAllowed','transpileOrMappingAllowed','nativeBuildAllowed','nativeFreezeAllowed','keyOrCryptoAllowed','gcOrOomOrFaultAllowed','unsafeResetOrReuseAllowed','allSixFixtureGateComplete','fullSeventeenGateComplete','fullNextCompatibility','deploymentAccepted','adoptionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed'])need(root[k]===false,'No wider gate '+k);return true;
}
export function environmentModel(env,execArgv,version){
 need(version==='v22.14.0'&&same(execArgv,[]),'Fresh plain pinned Node22');
 for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','NODE_COMPAT_LEGACY_COMPONENTIZER','NODE_COMPAT_COMPONENTIZE_MODULE'])need(!env[k],'No startup override '+k);return true;
}
async function boundary(c,row){
 const inputs=await c.read(row);
 for(const r of inputs.files)await c.file(r);for(const ix of inputs.families)await c.family(ix);
 for(const b of inputs.boundaries){const v=await c.read(b.manifest);need(v[b.field].length===b.expectedRows,'Full parent native/tool boundary');for(const r of v[b.field])await c.file(r);for(const ix of v[b.familyField]??[])await c.family(ix);}
}
async function publication(c,ix,completion,expectedResult,roots){
 const v=await c.read(ix),base=dirname(ix.path),names=new Set(['index.json','completion.json']);
 need(v.schemaVersion===1&&v.files.length===18,'Exact actual per-pure construction publication');
 const dirs=new Set([base]);for(const r of v.files){const n=relative(r.path);need(!names.has(n),'Unique actual artifact member');names.add(n);const p=join(base,n);await c.file({path:p,sha256:r.sha256,bytes:r.bytes});const s=await lstat(p);need(s.nlink===1&&(s.mode&0o777)===0o600,'Actual independent private artifact');dirs.add(dirname(p));}
 const done=await c.read(completion);need(done.state==='COMPLETE_UNREVIEWED_EXTERNAL_RAW_ZERO_REQUIRED'&&same(done.index,{...ix,path:'index.json'})&&same(done.result,{...expectedResult,path:'result.json'}),'Exact actual construction completion');
 await c.tree(base,names);c.families.push({base,names});for(const path of dirs){const s=await lstat(path);need(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o777)===0o700,'Private actual artifact directory');roots.push({path,dev:s.dev,ino:s.ino});}
}
async function authenticate(input,role){
 need(HERE===ORIGINAL&&['parent','oracle','retained','fresh'].includes(role),'Actual own runtime Source and finite role');environmentModel({...process.env},process.execArgv,process.version);
 const c=new Capture(),artifactRoots=[];let primaryPresent=false,primary;
 const complete=async()=>{const errors=[];try{await c.recheck();}catch(e){errors.push(e);}for(const root of artifactRoots)try{const s=await lstat(root.path);need(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o777)===0o700&&s.dev===root.dev&&s.ino===root.ino,'Artifact directory identity/mode unchanged');}catch(e){errors.push(e);}if(errors.length)throw new AggregateError(errors,'Complete source/artifact protections attempted');};
 try{
  const configRow=captureDescriptor(input),cfg=await c.read(configRow),own=captureDescriptor(cfg.sourceIndex);
  need(cfg.schemaVersion===1&&cfg.state==='COMBINED355_PURE_CONTROL_CONFIG_V1'&&own.path===join(HERE,'index.json'),'New actual config/Source');
  const rows=await c.family(own),refs=await c.read(rows.find(r=>r.path===join(HERE,'references.json'))),inputs=await c.read(rows.find(r=>r.path===join(HERE,'source-inputs.json')));
  for(const r of inputs.files)await c.file(r);for(const ix of inputs.families)await c.family(ix);
  if(role==='parent'){await boundary(c,inputs.parentOnlyBoundary);await c.family(refs.callerSourceIndex);await c.packageTree((await c.read(refs.packageInventory)).package,refs.loaderPackageRoot);}
  const rootRow=captureDescriptor(cfg.rootAuthority),root=await c.read(rootRow);rootModel(root,own,refs);
  need(same(root.entry,rows.find(r=>r.path===join(HERE,'entry.mjs')))&&same(root.externalController,rows.find(r=>r.path===join(HERE,'external.py'))),'Actual own entry and controller');
  const peer=await c.proof(root.sourceIndependentReview);need(peer.schemaVersion===1&&peer.state==='INDEPENDENT_COMBINED355_PURE_RUNTIME_CONTROL_SOURCE_REVIEW_PASSED_V1'&&peer.sourceIndexSha256===own.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true,'New independent Source peer');for(const k of ['ownerActionsInvoked','hostActionsInvoked','runtimeActionsInvoked'])need(peer[k]===false,'Source no action '+k);
  const p=await c.proof(refs.actualPureReview),contract=await c.read(refs.actualPureContract);artifactModel(p,contract,refs);const proofRows=await c.family(refs.actualPureReview.index);need(proofRows.filter(r=>same(r,refs.actualPureContract)).length===1,'Actual contract indexed once');
  await publication(c,p.artifacts.constructionIndex,p.artifacts.constructionCompletion,p.artifacts.constructionResult,artifactRoots);
  await c.file(refs.component);for(const r of Object.values(refs.generated))await c.file(r);
  need(await readFile(refs.generated.packageJson.path,'utf8')==='{\"type\":\"module\"}\n','Exact original ESM package');
  need(refs.generated.glue.path===join(dirname(refs.generated.core.path),'combined_pure.js')&&refs.generated.core.path.endsWith('/combined_pure.core.wasm'),'Exact actual no-import core loading tuple');
  need(await realpath(process.execPath)===refs.node.path,'Actual pinned Node');await complete();
  return{c,refs,root,rootRow,own,configRow,role,recheck:complete,native:null};
 }catch(error){primaryPresent=true;primary=error;throw error;}finally{try{await complete();}catch(error){if(primaryPresent)throw new AggregateError([primary,error],'Authentication plus protection failure');throw error;}}
}
export async function runPureControl({configDescriptor}={}){
 const f=await authenticate(configDescriptor,'parent');let record=null,primaryPresent=false,primary;
 const recheck=async()=>{const failures=[];if(record)try{await record.recheck();}catch(e){failures.push(e);}try{await f.recheck();}catch(e){failures.push(e);}if(failures.length)throw new AggregateError(failures,'All parent native/source checks attempted');};
 try{
  const api=await import(pathToFileURL(f.refs.nativeApi.path)),model=await import(pathToFileURL(f.refs.callerEntry.path));
  need(typeof api.combinedNativeBootstrapPreflight==='function'&&typeof model.nativeRecordModel==='function','Genuine existing APIs in actual original contexts');
  record=await api.combinedNativeBootstrapPreflight({configDescriptor:f.refs.readOnlyConfig});
  const data=await f.c.read(f.refs.actualReadOnlyData),metadata=await f.c.read(f.refs.nativeMetadata);model.nativeRecordModel(record,f.refs,metadata,data.bootstrap,data);await recheck();
  const nativeShape=Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptors(record)).map(([k,d])=>[k,{type:typeof d.value,writable:d.writable,configurable:d.configurable,enumerable:d.enumerable}]));
  const body=await import(pathToFileURL(join(HERE,'body.mjs')));return await body.parent({...f,native:record,nativeData:data,nativeShape,recheck});
 }catch(error){primaryPresent=true;primary=error;throw error;}finally{try{await recheck();}catch(error){if(primaryPresent)throw new AggregateError([primary,error],'Parent runtime plus final protection');throw error;}}
}
export async function runPureChild({configDescriptor,role}={}){
 need(['oracle','retained','fresh'].includes(role),'Child cannot invoke parent admission');const f=await authenticate(configDescriptor,role);
 try{const body=await import(pathToFileURL(join(HERE,'worker.mjs')));return await body.worker(f,role);}finally{await f.recheck();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 need(process.argv.length===4,'Exact finite own CLI');const role=process.argv[2],configDescriptor=JSON.parse(process.argv[3]);
 const value=role==='parent'?await runPureControl({configDescriptor}):await runPureChild({configDescriptor,role});process.stdout.write(JSON.stringify(value)+'\n');
}
