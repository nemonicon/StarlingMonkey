// Dormant v13 clock-selected construction; only Node builtins before full auth.
import {readFile,lstat,readdir,realpath,open,mkdir} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {createRequire} from 'node:module';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/clock-v13-component-candidate-v1';
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

export function constructionModel(root,own,refs){
 need(root?.schemaVersion===1&&root.state==='ROOT_REVIEWED_CLOCK_V13_COMPONENT_CONSTRUCTION_V1'&&root.phase==='component-build','Fresh Root clock-v13 phase');
 need(same(root.sourceIndex,own)&&root.entry?.path===join(HERE,'build.mjs'),'Exact new Source/entry');
 for(const k of ['componentConstructionAllowed','engineInitializationDuringConstructionAllowed','nativeReadOnlyPreflightAllowed'])need(root[k]===true,'Explicit narrow action '+k);
 need(same(root.nativeEngine,refs.nativeEngine)&&same(root.nativeMetadata,refs.nativeMetadata)&&root.nativeSourceFiles===342&&root.selectedWholeManifests===9,'Genuine complete accepted v13 normalOFF');
 need(root.guestSourceSha256===refs.bundle.sha256&&root.witWorldSha256===refs.wit.sha256&&root.worldName===refs.worldName,'Whole actual bundle/new WIT');
 for(const k of ['selectedInterfaces','disableFeatures','requiredNativeReadOnlyEnvironment'])need(same(root[k],refs[k]),'Exact selected policy '+k);
 for(const k of ['outputRoot','externalRoot','privateTemporaryRoot'])need(root[k]===refs[k],'Fresh phase physical role '+k);
 need(root.enclosingOwnedNodeDeadlineSeconds===1800&&root.externalOwnedPhaseDeadlineSeconds===2400&&root.maxComponentBytes===67108864,'Future owned external watchdog bounds');
 for(const k of ['ordinaryGuestExportsAllowed','generatedModuleImportAllowed','keyOrCryptoWorkloadsAllowed','hostServersAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed'])need(root[k]===false,'No additional authority '+k);
 need(root.actualComponentReview===null&&root.actualRuntimeAuthority===null,'No projected actual authority');
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
async function authenticate(input){
 need(HERE===ORIGINAL,'Original own caller context');environmentModel({...process.env},process.execArgv,process.version);
 const c=new Capture(),configRow=captureDescriptor(input),config=await c.read(configRow),own=captureDescriptor(config.sourceIndex);
 need(config.schemaVersion===1&&config.state==='CLOCK_V13_COMPONENT_CONFIG_V1'&&own.path===join(HERE,'index.json'),'Exact own future config/Source');
 const members=await c.family(own),find=n=>members.find(r=>r.path===join(HERE,n)),refs=await c.read(find('references.json')),inputs=await c.read(find('source-inputs.json'));
 need(inputs.schemaVersion===1&&inputs.files.length>=11000&&inputs.files.length<=20000&&new Set(inputs.files.map(x=>x.path)).size===inputs.files.length,'Finite complete runtime intake');
 for(const r of inputs.files)await c.file(r);for(const ix of inputs.families)await c.family(ix);
 const rootRow=captureDescriptor(config.rootAuthority),root=await c.read(rootRow);constructionModel(root,own,refs);await c.file(root.entry);need(same(root.entry,find('build.mjs')),'Exact actual caller entry');
 const peer=await c.proof(root.sourceIndependentReview);need(peer.schemaVersion===1&&peer.state==='INDEPENDENT_CLOCK_V13_COMPONENT_SOURCE_REVIEW_PASSED_V1'&&peer.componentSourceIndexSha256===own.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true&&peer.ownerActionsInvoked===false,'Independent own Source review, no self-approval');
 const lp=await c.proof(refs.loaderSourcePeer);need(lp.schemaVersion===1&&lp.state==='INDEPENDENT_CLOCK_PACKAGE_LOADER_SOURCE_REVIEW_PASSED_V2'&&lp.sourceIndexSha256===refs.loaderSourceIndex.sha256&&lp.sourceOnly===true&&lp.sourceReviewPassed===true&&lp.ownerActionsInvoked===false,'Actual reviewed loader V2');
 const loaderConfig=captureDescriptor(config.loaderConfig);need(same(root.loaderConfig,loaderConfig),'Root binds exact loader config');const lc=await c.read(loaderConfig),loaderRootRow=captureDescriptor(root.loaderRootAuthority),loaderRoot=await c.read(loaderRootRow);
 need(lc.schemaVersion===1&&lc.state==='CLOCK_PACKAGE_LOADER_CONFIG_V2'&&same(lc.sourceIndex,refs.loaderSourceIndex)&&same(lc.rootAuthority,loaderRootRow),'Genuine loader original config/Root');
 need(loaderRoot.schemaVersion===1&&loaderRoot.state==='ROOT_REVIEWED_EXPERIMENTAL_CLOCK_PACKAGE_CONSTRUCTION_V2'&&loaderRoot.phase==='experimental-component-construction'&&same(loaderRoot.sourceIndex,refs.loaderSourceIndex)&&same(loaderRoot.sourceIndependentReview,refs.loaderSourcePeer),'Genuine loader Root state/Source peer');
 for(const k of ['nativeEngine','nativeMetadata','guestSourceSha256','witWorldSha256','worldName','selectedInterfaces','disableFeatures','privateTemporaryRoot'])need(same(loaderRoot[k],root[k]),'Same actual caller/loader role '+k);
 need(loaderRoot.packageRoot===refs.loaderPackageRoot,'Own experimental package, not old consumed context');
 for(const k of ['packageModuleInitializationAllowed','componentConstructionAllowed','engineInitializationDuringConstructionAllowed','nativeArtifactAdmissionMustBePerformedByCaller','freshOwnedNodeProcessRequired'])need(loaderRoot[k]===true,'Exact loader authority '+k);
 for(const[k,v]of Object.entries(refs.loaderProofs))need(same(loaderRoot[k],v),'Actual loader proof binding '+k);
 for(const k of ['adapterPromotionAllowed','defaultPackagerReplacementAllowed','keyOrCryptoWorkloadsAllowed','ordinaryGuestExportsAllowed','hostServersAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed'])need(loaderRoot[k]===false,'Loader extra action closed '+k);
 for(const[k,v]of Object.entries(refs.requiredNativeReadOnlyEnvironment))need(process.env[k]===v,'Original native read-only consumed-context environment '+k);
 need(process.env.TMPDIR===refs.privateTemporaryRoot,'Exact fresh caller-owned TMPDIR');const tmp=await lstat(refs.privateTemporaryRoot);need(tmp.isDirectory()&&!tmp.isSymbolicLink()&&(tmp.mode&0o777)===0o700&&(await readdir(refs.privateTemporaryRoot)).length===0,'Fresh empty private temporary directory before package');
 need(await realpath(process.execPath)===refs.node.path,'Pinned actual Node');await c.file(refs.node);await c.recheck();return{c,refs,root,rootRow,configRow,own,loaderConfig};
}
class Output{
 constructor(root){this.root=root;this.rows=new Map();this.capture=new Capture();}
 static async create(root){await mkdir(root,{mode:0o700});const out=new Output(root);out.identity=identity(await lstat(root));return out;}
 async write(name,value,json=false){relative(name);need(!this.rows.has(name),'Never overwrite an owned output');const path=join(this.root,name);await mkdir(dirname(path),{recursive:true,mode:0o700});
  const bytes=json?Buffer.from(JSON.stringify(value,null,2)+'\n'):typeof value==='string'?Buffer.from(value):value;need(bytes instanceof Uint8Array,'Complete output byte transport');
  const handle=await open(path,'wx',0o600);try{await handle.writeFile(bytes);await handle.sync();}finally{await handle.close();}
  const r=captureDescriptor({path,sha256:sha(bytes),bytes:bytes.length});await this.capture.file(r);this.rows.set(name,r);return r;
 }
 async recheck(){const s=await lstat(this.root);need(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o777)===0o700&&s.dev===this.identity[0]&&s.ino===this.identity[1],'Owned root identity/mode');await this.capture.recheck();await this.capture.tree(this.root,new Set(this.rows.keys()));}
}
export async function buildClockV13Component({configDescriptor}={}){
 const f=await authenticate(configDescriptor),{c,refs,root}=f;let native=null,selected=null,out=null,component=null,primary=null,componentizationAttempted=false;const finalErrors=[];
 const recheck=async()=>{await c.recheck();if(native)await native.recheck();if(selected)await selected.recheck();};
 try{
  out=await Output.create(refs.outputRoot);await out.write('phase-inputs.json',{sourceIndex:f.own,rootAuthority:f.rootRow,config:f.configRow,loaderConfig:f.loaderConfig,nativeEngine:refs.nativeEngine,nativeMetadata:refs.nativeMetadata,selectedInterfaces:refs.selectedInterfaces},true);
  // First custom import is the unchanged genuine native read/hash API. It imports
  // neither the old packaging module nor Rolldown/Jco package dependencies.
  const {classicPreflight}=await import(pathToFileURL(refs.nativePreflight.path));native=await classicPreflight({variant:'normal-off'});const metadata=await c.read(refs.nativeMetadata);nativeFrameModel(native,refs,metadata);
  await out.write('native-frame-data.json',Object.fromEntries(Object.entries(native).filter(([k])=>k!=='recheck')),true);
  await out.write('native-frame-shape.json',Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptors(native)).map(([k,d])=>[k,{type:typeof d.value,writable:d.writable,configurable:d.configurable,enumerable:d.enumerable}])),true);
  const {selectedManifestsForEngine}=await import(pathToFileURL(refs.nativeSelector.path));const manifests=selectedManifestsForEngine(native.metadata,{sourceRoot:native.sourceRoot});need(manifests.length===9,'Genuine full nine manifests');await out.write('selected-whole-manifests.json',manifests,true);
  await recheck();await out.write('guest.mjs',await readFile(refs.guest.path));const source=new TextDecoder('utf-8',{fatal:true}).decode(await readFile(refs.bundle.path));const wit=new TextDecoder('utf-8',{fatal:true}).decode(await readFile(refs.wit.path));await c.file(refs.bundle);await c.file(refs.wit);await out.write('bundle.mjs',source);await out.write('public-abi.wit',wit);
  const {loadExperimentalClockPackage}=await import(pathToFileURL(refs.loaderEntry.path));selected=await loadExperimentalClockPackage({configDescriptor:f.loaderConfig});await out.write('selected-package-provenance.json',selected.provenance,true);
  const options={engine:refs.nativeEngine.path,preview2Adapter:refs.prunedAdapter.path,witWorld:wit,worldName:refs.worldName,disableFeatures:[...refs.disableFeatures],enableFeatures:[],selectedInterfaces:[...refs.selectedInterfaces],enableAot:false,env:{}};
  await out.write('component-options.json',options,true);await recheck();await out.write('before-componentization.json',{ordinaryGuestExportsAllowed:false,generatedModuleImportAllowed:false,fullOriginalReactDomBundle:true},true);
  componentizationAttempted=true;const result=await selected.componentize(source,options);need(result?.component instanceof Uint8Array&&result.component.length<=root.maxComponentBytes,'Whole bounded actual component');component=await out.write('clock-v13.component.wasm',result.component);await out.write('interface-audit.json',result.interfaceAudit,true);
  need(result.interfaceAudit?.state==='verified-final-component'&&result.interfaceAudit.componentSha256===component.sha256&&result.interfaceAudit.emittedImports.every(x=>refs.selectedInterfaces.includes(x)),'Exact selected standard clock/poll subset, no other capabilities');
  // Package-aware metadata/transpile APIs are imported only AFTER selected loader
  // package initialization/construction, from that exact authenticated package.
  const require=createRequire(join(refs.loaderPackageRoot,'package.json'));const {componentWit,transpile}=await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
  const emitted=await componentWit(result.component);await out.write('emitted.wit',emitted);need([...emitted.matchAll(/\bexport\s+([^;]+);/g)].map(x=>x[1].replace(/\s+/g,' ').trim()).join('|')==='run: func() -> string','Sole actual public run scalar ABI');
  const generated=await transpile(result.component,{name:'clock_v13',wasiShim:false});await out.write('transpile-metadata.json',{imports:generated.imports,exports:generated.exports,files:Object.keys(generated.files)},true);
  for(const[name,bytes]of Object.entries(generated.files))await out.write('transpiled/'+relative(name),bytes);await out.write('transpiled/package.json','{"type":"module"}\n');
 }catch(error){primary={name:error?.name??null,message:error?.message??String(error),stack:error?.stack??null};}
 finally{try{await recheck();}catch(error){finalErrors.push({scope:'whole-source-native-package',message:error?.message??String(error),stack:error?.stack??null});}try{if(out)await out.recheck();}catch(error){finalErrors.push({scope:'owned-output',message:error?.message??String(error),stack:error?.stack??null});}}
 if(!out){const error=new Error(primary?.message??'No owned output created');error.cause={primary,finalErrors};throw error;}
 const complete=primary===null&&finalErrors.length===0;const result=await out.write('results.json',{schemaVersion:1,state:complete?'CLOCK_V13_COMPONENT_CONSTRUCTED_UNREVIEWED_V1':'CLOCK_V13_COMPONENT_FAILED_UNACCEPTED_V1',componentSourceIndexSha256:f.own.sha256,rootAuthority:f.rootRow,config:f.configRow,component,componentizationAttempted,guestInitializationExecutedByComponentization:component!==null?true:componentizationAttempted?null:false,primaryError:primary,finalProtectionErrors:finalErrors,selectedInterfaces:refs.selectedInterfaces,nativeSourceFiles:342,selectedWholeManifests:9,originalReactDomBundle:refs.originalBundle,ordinaryGuestExportsInvoked:false,generatedModuleImported:false,keyOrCryptoWorkloadsInvoked:false,operationalAdmission:false,runtimeAcceptanceClaim:false,actualArtifactReviewRequired:true,externalRawZeroCleanRequired:true},true);
 const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows].map(([path,r])=>({path,sha256:r.sha256,bytes:r.bytes}))},true);const completion=await out.write('completion.json',{schemaVersion:1,state:complete?'COMPLETE_UNREVIEWED_EXTERNAL_RAW_ZERO_REQUIRED':'FAILED_UNACCEPTED',index,result,component},true);await out.recheck();return{root:out.root,index,completion,completeUnreviewed:complete};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 need(process.argv.length===3,'One exact config descriptor');try{const result=await buildClockV13Component({configDescriptor:JSON.parse(process.argv[2])});process.stdout.write(JSON.stringify(result)+'\n');if(!result.completeUnreviewed)process.exitCode=1;}catch(error){process.stderr.write(JSON.stringify({name:error?.name??null,message:error?.message??String(error),stack:error?.stack??null,cause:error?.cause??null})+'\n');process.exitCode=1;}
}
