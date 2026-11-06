// Unsealed runtime Source proposal. Node builtins only before full authentication.
import {readFile,lstat,readdir,realpath,readlink} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/combined-native-runtime-candidate-v1';
const same=isDeepStrictEqual,sha=b=>createHash('sha256').update(b).digest('hex');
function need(v,m){if(!v)throw new Error(m);}
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

// Descend only finite declared descriptor roles. Historical metadata digests are DATA.
async function exactRoles(c,v){if(!v||typeof v!=='object')return;if(same(Object.keys(v).sort(),['bytes','path','sha256'])){await c.file(v);return;}if(v.index&&v.result&&Object.keys(v).length===2){await c.proof(v);return;}for(const x of Object.values(v))await exactRoles(c,x);}
async function contractProof(c,pair,row,state){
 need(pair&&row,'Actual result is pending');const members=await c.family(pair.index);for(const x of [pair.result,row])need(members.filter(y=>same(x,y)).length===1,'Actual result and contract indexed once');const p=await c.read(pair.result),k=await c.read(row);need(p.schemaVersion===1&&p.state===state&&p.verifiedPassed===true&&k.requiredReviewState===state,'Genuine actual bounded DATA proof');for(const group of ['requiredFixedValues','requiredExactDescriptors'])for(const [key,v]of Object.entries(k[group]??{}))need(same(p[key],v),'Actual contract '+key);if(k.requiredCoverage)need(same(p.coverage,k.requiredCoverage),'Full actual coverage');await exactRoles(c,k.requiredExactDescriptors);return{proof:p,contract:k};
}
function environment(){need(process.env.PREVIEW2_SHIM_DEBUG==='0','Selected nondebug standard shim environment');need(process.env.RAYON_NUM_THREADS==='1','Exact selected one-thread stockWT environment');need(process.version==='v22.14.0'&&same(process.execArgv,[]),'Fresh plain pinned Node22');for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','NODE_COMPAT_LEGACY_COMPONENTIZER','NODE_COMPAT_COMPONENTIZE_MODULE'])need(!process.env[k],'No startup/package override '+k);}
async function intake(c,inputs){
 need(inputs.schemaVersion===1&&Array.isArray(inputs.files)&&Array.isArray(inputs.families),'Finite own source intake');for(const r of inputs.files)await c.file(r);for(const ix of inputs.families)await c.family(ix);for(const bound of inputs.boundaries??[]){const b=await c.read(bound.manifest);need(Array.isArray(b[bound.field])&&b[bound.field].length===bound.expectedRows,'Exact declared boundary');for(const r of b[bound.field])await c.file(r);for(const ix of b[bound.familyField]??[])await c.family(ix);}
}
export async function authenticate(configDescriptor){
 need(HERE===ORIGINAL,'Actual own runtime module context');environment();const c=new Capture();let errorPresent=false,primary;
 try{
  const configRow=captureDescriptor(configDescriptor),cfg=await c.read(configRow),own=captureDescriptor(cfg.sourceIndex);need(cfg.schemaVersion===1&&cfg.state==='COMBINED355_RUNTIME_CONFIG_V1'&&own.path===join(HERE,'index.json'),'Own exact Source config');
  const members=await c.family(own),byName=n=>{const r=members.find(x=>x.path===join(HERE,n));need(r,'Indexed own member '+n);return r;},refs=await c.read(byName('references.json'));need(refs.originalRoot===HERE,'Own references context');await intake(c,await c.read(byName('source-inputs.json')));await c.packageTree((await c.read(refs.packageInventory)).package,refs.loaderPackageRoot);
  const rootRow=captureDescriptor(cfg.rootAuthority),root=await c.read(rootRow);need(same(root.entry,byName('entry.mjs'))&&same(root.externalController,byName('external.py'))&&!Object.hasOwn(root,'config'),'Root authenticates actual own entry/controller; config binds Root without descriptor cycle');
  const catalogue=await c.read(refs.fixtureCatalogue),fixture=catalogue.fixtures.find(x=>x.id===cfg.fixtureId);need(fixture&&catalogue.nativeGeneration==='new-combined355-normal-off'&&root.fixtureId===cfg.fixtureId&&root.phase===cfg.phase,'Actual one held fixture/phase');
  const peer=await c.proof(root.sourceIndependentReview);need(peer.state==='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V1'&&peer.sourceIndexSha256===own.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true&&peer.ownerActionsInvoked===false,'Separate genuine own Source review');
  const fp=await c.proof(refs.fixtureSourcePeer);need(fp.state===refs.fixtureReviewRequiredState&&fp.fixtureSourceIndexSha256===refs.fixtureSourceIndex.sha256&&fp.sourceReviewPassed===true&&fp.ownerActionsInvoked===false,'Actual held six fixture Source peer');
  const np=await c.proof(refs.nativeApiSourcePeer);need(np.state==='INDEPENDENT_COMBINED355_NATIVE_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V1'&&np.toolingSourceIndexSha256===refs.nativeApiSourceIndex.sha256&&np.sourceReviewPassed===true&&np.ownerActionsInvoked===false,'Genuine full80 retained API Source peer');
  const bp=await contractProof(c,refs.actualBootstrapReview,refs.actualBootstrapContract,'INDEPENDENT_COMBINED355_NORMAL_OFF_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1'),rp=await contractProof(c,refs.actualReadOnlyReview,refs.actualReadOnlyContract,refs.actualReadOnlyRequiredState);need(same(rp.proof.retainedData,refs.actualReadOnlyData)&&same(rp.proof.config,refs.readOnlyConfig)&&same(rp.proof.actualBootstrapReview,refs.actualBootstrapReview),'Actual retained read-only roles');
  const metadata=await c.read(refs.nativeMetadata),expectedBootstrap=await c.read(bp.proof.bootstrapFrame),expectedRecordData=await c.read(refs.actualReadOnlyData);need(await realpath(process.execPath)===refs.node.path,'Pinned executable realpath');await c.file(refs.node);await c.recheck();
  // First custom imports occur only after complete own/external/family/package auth.
  const models=await import(pathToFileURL(join(HERE,'models.mjs')));models.phaseModel(root,own,refs,fixture,cfg.phase);
  let artifact=null,artifactContract=null;
  if(cfg.phase!=='init-fatal-evidence'){
   const slot=refs.artifactSlots[fixture.id];if(slot.actualReview)need(same(root.actualArtifactReview,slot.actualReview)&&same(root.actualArtifactContract,slot.contract),'Existing actual perfixture proof fixed by Source');
   const state='INDEPENDENT_COMBINED355_'+fixture.id.replaceAll('-','_').toUpperCase()+'_COMPONENT_ARTIFACT_REVIEW_PASSED_V1';const {proof:p,contract:k}=await contractProof(c,root.actualArtifactReview,root.actualArtifactContract,state);models.artifactModel(p,k,refs,fixture,root);await exactRoles(c,k.artifacts);await exactRoles(c,p.generatedFiles);await c.file(p.binaryGraph);if(slot.knownComponent)need(same(p.artifacts.component,slot.knownComponent),'Exact known component');artifact=p;artifactContract=k;
  }
  await c.recheck();return{c,configRow,own,refs,rootRow,root,fixture,artifact,artifactContract,metadata,expectedBootstrap,expectedRecordData,models};
 }catch(error){errorPresent=true;primary=error;throw error;}finally{try{await c.recheck();}catch(error){if(errorPresent)throw new AggregateError([primary,error],'Runtime auth and final protection failed');throw error;}}
}
// Children are Source/artifact authenticated only. They NEVER call the native
// retained API, fabricate its frame, or repeat parent whole-native admission.
export async function authenticateChild(configDescriptor){
 need(HERE===ORIGINAL,'Actual own child context');environment();const c=new Capture();let primary,present=false;
 try{
  const configRow=captureDescriptor(configDescriptor),cfg=await c.read(configRow),own=captureDescriptor(cfg.sourceIndex);need(cfg.schemaVersion===1&&cfg.state==='COMBINED355_RUNTIME_CONFIG_V1'&&own.path===join(HERE,'index.json'),'Own child Source config');const members=await c.family(own),at=n=>{const r=members.find(x=>x.path===join(HERE,n));need(r,'Own child member');return r;},refs=await c.read(at('references.json')),inputs=await c.read(at('child-inputs.json'));
  need(refs.originalRoot===HERE&&inputs.schemaVersion===1,'Child own exact context');for(const r of inputs.files)await c.file(r);const rootRow=captureDescriptor(cfg.rootAuthority),root=await c.read(rootRow);need(same(root.entry,at('entry.mjs'))&&same(root.externalController,at('external.py'))&&!Object.hasOwn(root,'config'),'Own child Root paths');
  const p=await c.proof(root.sourceIndependentReview);need(p.state==='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V1'&&p.sourceIndexSha256===own.sha256&&p.sourceOnly===true&&p.sourceReviewPassed===true&&p.ownerActionsInvoked===false,'Actual separate Source peer');
  const catalogue=await c.read(refs.fixtureCatalogue),fixture=catalogue.fixtures.find(x=>x.id===cfg.fixtureId);need(fixture&&cfg.phase===root.phase,'Child held fixture');await c.file(fixture.source);await c.file(fixture.wit);const fp=await c.proof(refs.fixtureSourcePeer);need(fp.state===refs.fixtureReviewRequiredState&&fp.fixtureSourceIndexSha256===refs.fixtureSourceIndex.sha256&&fp.sourceReviewPassed===true,'Held fixture Source peer');await c.recheck();
  const models=await import(pathToFileURL(join(HERE,'models.mjs')));models.phaseModel(root,own,refs,fixture,cfg.phase);need(['run','fatal'].includes(cfg.phase),'No compiler in child');const slot=refs.artifactSlots[fixture.id];if(slot.actualReview)need(same(root.actualArtifactReview,slot.actualReview)&&same(root.actualArtifactContract,slot.contract),'Child exact fixed artifact proof');const state='INDEPENDENT_COMBINED355_'+fixture.id.replaceAll('-','_').toUpperCase()+'_COMPONENT_ARTIFACT_REVIEW_PASSED_V1',{proof:artifact,contract:artifactContract}=await contractProof(c,root.actualArtifactReview,root.actualArtifactContract,state);models.artifactModel(artifact,artifactContract,refs,fixture,root);await exactRoles(c,artifactContract.artifacts);await exactRoles(c,artifact.generatedFiles);if(slot.knownComponent)need(same(artifact.artifacts.component,slot.knownComponent),'Child actual known component');need(await realpath(process.execPath)===refs.node.path,'Child exact pinned Node');await c.file(refs.node);await c.recheck();
  return{c,configRow,own,refs,rootRow,root,fixture,artifact,artifactContract,models,recheck:()=>c.recheck(),childSourceAndArtifactAuthenticationOnly:true,nativeApiInvocations:0,nativeFrameReturned:false};
 }catch(error){present=true;primary=error;throw error;}finally{try{await c.recheck();}catch(error){if(present)throw new AggregateError([primary,error],'Child auth and final protection failed');throw error;}}
}
export async function run({configDescriptor,operation='parent',scenario=null}={}){
 need(['parent','worker','fatal-worker'].includes(operation),'Only implemented explicit operation; no action for unknown operation');
 if(operation==='worker'||operation==='fatal-worker'){const f=await authenticateChild(configDescriptor);try{const body=await import(pathToFileURL(join(HERE,'runtime.mjs')));return await body.run(f,{operation,scenario});}finally{await f.recheck();}}
 const f=await authenticate(configDescriptor);let record=null,primary,primaryPresent=false;
 f.recheck=async()=>{if(record)await record.recheck();await f.c.recheck();};
 try{
  const api=await import(pathToFileURL(f.refs.nativeApi.path)),predicate=await import(pathToFileURL(f.refs.callerNativeModel.path));need(typeof api.combinedNativeBootstrapPreflight==='function'&&typeof predicate.nativeRecordModel==='function','Genuine original full80 API/pure record model');record=await api.combinedNativeBootstrapPreflight({configDescriptor:f.refs.readOnlyConfig});predicate.nativeRecordModel(record,f.refs,f.metadata,f.expectedBootstrap,f.expectedRecordData);f.record=record;await f.recheck();
  const body=await import(pathToFileURL(join(HERE,f.root.phase==='map'?'mapping.mjs':'runtime.mjs')));return await body.run(f,{operation,scenario});
 }catch(error){primaryPresent=true;primary=error;throw error;}finally{try{await f.recheck();}catch(error){if(primaryPresent)throw new AggregateError([primary,error],'Runtime phase and final protection failed');throw error;}}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===4||process.argv.length===5,'Exact operation/config/scenario');const value=await run({operation:process.argv[2],configDescriptor:JSON.parse(process.argv[3]),scenario:process.argv[4]??null});process.stdout.write(JSON.stringify(value)+'\n');if(value.completeUnreviewed!==true)process.exitCode=1;}
