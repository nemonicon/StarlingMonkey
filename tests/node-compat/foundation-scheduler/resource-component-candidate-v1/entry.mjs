// Primitive-first source bootstrap. Only standard Node modules are static imports.
import {readFile,lstat,readdir,realpath,readlink} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,isAbsolute,relative} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {isDeepStrictEqual} from 'node:util';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/resource-component-candidate-v1';
const OUTPUT_BASE='/private/tmp/starling-node-compat/scheduler-resource-component-v1';
function fixtureModel(name){
 need(['resource','pure','fatal','init-fatal'].includes(name),'Finite exact fixture');
 return Object.freeze({name,clocks:name!=='pure',expectedResidualImports:name==='resource'||name==='pure'?['node:buffer']:[],
  expectedAbi:name==='resource'?{inspect:'() -> string',run:'(u32) -> string',validate:'() -> string'}:{run:'() -> string'},
  expectedInitializationRefusal:name==='init-fatal'});
}
function authorityModel(root,sourceSha){
 need(root?.schemaVersion===1&&root.state==='ROOT_REVIEWED_SCHEDULER_RESOURCE342_COMPONENT_CONSTRUCTION_PHASE_V1'&&root.sourceIndexSha256===sourceSha,'New exact Root construction frame');
 const fixture=fixtureModel(root.fixture);
 need(root.phase==='construct-component'&&root.componentConstructionAllowed===true&&root.initializationOnly===true,'Construction and initialization only');
 need(root.outputRoot===OUTPUT_BASE+'-'+fixture.name&&root.workerTimeoutMs===600000&&root.maxComponentBytes===64*1024*1024&&root.maxBundleBytes===32*1024*1024,'Exact bounded fresh fixture namespace');
 for(const key of ['nativeBuildAllowed','nativeFreezeAllowed','sourcePromotionAllowed','ordinaryExportsAllowed','timerRuntimeAllowed','guestLoadingAllowed','hostRequestsAllowed','gcAllowed','keyOrCryptoAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjectionAllowed'])need(root[key]===false,'No additional authority '+key);
 return fixture;
}
const constructionFrames=new WeakSet(),workerFrames=new WeakSet();
export function requireConstructionFrame(v){need(constructionFrames.has(v),'Genuine new construction preflight capability');}
export function requireWorkerFrame(v){need(workerFrames.has(v),'Genuine private worker capability');}
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export function need(v,m){if(!v)throw new Error(m);}
export function descriptor(value){const r=Object.freeze({path:value?.path,sha256:value?.sha256,bytes:value?.bytes});need(typeof r.path==='string'&&isAbsolute(r.path)&&resolve(r.path)===r.path&&!r.path.includes('\0')&&!r.path.includes('\\'),'Canonical absolute descriptor');need(typeof r.sha256==='string'&&/^[a-f0-9]{64}$/.test(r.sha256)&&Number.isSafeInteger(r.bytes)&&r.bytes>=0,'Exact descriptor primitives');return r;}
function local(n){need(typeof n==='string'&&n&&!isAbsolute(n)&&!n.includes('\\')&&!n.includes('\0')&&n.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Unique local member');return n;}
export async function streamHash(input){const r=descriptor(input);need(r.bytes<=1024*1024*1024,'Bounded whole source bytes');need(await realpath(dirname(r.path))===dirname(r.path).replace(/^\/tmp(?=\/|$)/,'/private/tmp'),'No undeclared ancestor alias');const a=await lstat(r.path);need(a.isFile()&&!a.isSymbolicLink()&&a.size===r.bytes,'Ordinary pinned source');const h=createHash('sha256');let count=0;for await(const b of createReadStream(r.path)){h.update(b);count+=b.length;}const z=await lstat(r.path);need(a.dev===z.dev&&a.ino===z.ino&&a.size===z.size&&a.mtimeMs===z.mtimeMs&&a.ctimeMs===z.ctimeMs&&count===r.bytes&&h.digest('hex')===r.sha256,'Stable complete source hash');}
export async function regular(input){const r=descriptor(input);need(r.bytes<=32*1024*1024,'Finite JSON/source record');await streamHash(r);const raw=await readFile(r.path);need(raw.length===r.bytes&&hash(raw)===r.sha256,'Whole JSON/source bytes');return raw;}
function freeze(v){if(v&&typeof v==='object'){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;}
async function family(input){const ix=descriptor(input),root=dirname(ix.path),index=JSON.parse(await regular(ix)),names=new Set(),rows=[];need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=2048,'Finite indexed family');for(const f of index.files){const n=local(f.path);need(!names.has(n),'No duplicate family member');names.add(n);const r=descriptor({...f,path:join(root,n)});await streamHash(r);rows.push(r);}const actual=[];async function walk(base,prefix=''){for(const name of await readdir(base)){const p=join(base,name),s=await lstat(p),n=prefix+name;need(!s.isSymbolicLink(),'No family links');if(s.isDirectory())await walk(p,n+'/');else{need(s.isFile(),'Ordinary family member');actual.push(n);}}}await walk(root);need(actual.length===names.size+1&&actual.every(n=>n==='index.json'||names.has(n)),'Exact indexed family membership');return{index:ix,rows};}
async function peer(proof,state,sourceSha,key='sourceIndexSha256'){
 const f=await family(proof.index),rr=descriptor(proof.result);need(f.rows.filter(r=>isDeepStrictEqual(r,rr)).length===1,'Exact indexed peer result once');const v=JSON.parse(await regular(rr));need(v.schemaVersion===1&&v.state===state&&v[key]===sourceSha,'Exact independent source identity');return v;
}
async function packagingPhysical(mapRow){
 const map=freeze(JSON.parse(await regular(mapRow))),ix=descriptor(map.publicationIndex),index=JSON.parse(await regular(ix));
 need(map.state==='EXACT_EXISTING_PACKAGING_PHYSICAL_ROLES_NOT_NATIVE_AUTHORITY'&&map.originalZlibNativeFactsConsumed===false&&map.costActionStatesReused===false,'Generic packaging roles, no native authority');
 need(ix.sha256==='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b'&&index.state==='FRESH_ZLIB350_COST_SOURCE_PUBLICATION_V1','Actual immutable packaging publication DATA');
 need(map.files.length===4934&&map.links.length===22&&map.toolFiles===4890&&map.packagingFiles===44,'Whole original package/tool boundary');
 const expected=new Map(),links=new Map();for(const r of map.files){const n=local(r.path);need(!expected.has(n),'Unique packaging file');expected.set(n,r);const found=index.files.filter(f=>f.path===n);need(found.length===1&&found[0].sha256===r.sha256&&found[0].bytes===r.bytes&&found[0].mode===r.mode,'Every role indexed once');}
 for(const l of map.links){const n=local(l.destination);need(!links.has(n),'Unique exact package link');local(l.mappedTarget);links.set(n,l);}
 need(index.files.filter(r=>r.path.startsWith('packaging/')||r.path.startsWith('tools/')).length===expected.size&&isDeepStrictEqual(index.links,map.links),'Complete original physical role inventory');
 const root=map.publicationRoot,s=await lstat(root);need(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o777)===0o700&&s.dev===map.rootIdentity.device&&s.ino===map.rootIdentity.inode,'Exact private publication identity');
 const seen=new Set(),seenLinks=new Set();async function walk(prefix){for(const name of await readdir(join(root,prefix))){const n=prefix+'/'+name,p=join(root,n),st=await lstat(p);if(st.isSymbolicLink()){const l=links.get(n);need(l&&await readlink(p)===l.newLinkText&&await realpath(p)===join(root,l.mappedTarget),'Only exact mapped22 links');seenLinks.add(n);}else if(st.isDirectory()){need((st.mode&0o777)===0o700,'Private tool directories');await walk(n);}else{const r=expected.get(n);need(st.isFile()&&st.nlink===1&&r&&(st.mode&0o7777)===r.mode,'Exact package member/mode');seen.add(n);}}}
 for(const prefix of map.roleRoots){local(prefix);await walk(prefix);}need(seen.size===expected.size&&seenLinks.size===links.size,'No omitted physical source or link');
 for(const r of map.files)await streamHash({path:join(root,r.path),sha256:r.sha256,bytes:r.bytes});return map;
}
function environment(refs){
 need(HERE===ORIGINAL,'Original source execution context only');need(process.version==='v22.14.0'&&process.execArgv.length===0,'Pinned plain Node22');
 for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','NODE_COMPAT_LEGACY_COMPONENTIZER'])need(!process.env[k],'No execution override '+k);
 need(process.env.NODE_COMPAT_TOOLCHAIN===refs.toolchainRoot&&process.env.NODE_COMPAT_COMPONENTIZE_MODULE===join(refs.packagerRoot,'src/componentize.js'),'Exact explicit packaging environment');
}
async function authenticate(sourceSha,configDescriptor){
 need(typeof sourceSha==='string'&&/^[a-f0-9]{64}$/.test(sourceSha),'Caller-pinned source SHA before imports');
 const path=join(HERE,'index.json'),raw=await readFile(path),ownRow=descriptor({path,sha256:sourceSha,bytes:raw.length});need(hash(raw)===sourceSha,'Caller-pinned source index');
 const own=await family(ownRow),member=name=>{const r=own.rows.find(r=>r.path===join(HERE,name));need(r,'Required own member');return r;};
 const refs=freeze(JSON.parse(await regular(member('references.json')))),manifest=freeze(JSON.parse(await regular(member('input-freeze.json'))));environment(refs);need(await realpath(process.execPath)===refs.node.path,'Actual pinned Node path');
 const configRow=descriptor(configDescriptor),cfg=freeze(JSON.parse(await regular(configRow))),rootRow=descriptor(cfg.rootAuthority),root=freeze(JSON.parse(await regular(rootRow)));
 need(cfg.sourceIndexSha256===sourceSha,'Config binds own source');
 for(const r of manifest.files)await streamHash(r);
 for(const r of refs.families)await family(r.index);
 const map=await packagingPhysical(refs.packagingMap);need(map.packagingRoot===refs.packagingRoot&&map.toolchainRoot===refs.toolchainRoot&&map.packagerRoot===refs.packagerRoot,'Explicit immutable packaging context');
 const sp=await peer(root.sourceIndependentReview,'INDEPENDENT_SCHEDULER_RESOURCE342_COMPONENT_SOURCE_REVIEW_PASSED_V1',sourceSha);need(sp.sourceOnly===true&&sp.sourceReviewPassed===true&&sp.ownerActionsInvoked===false,'New source peer only');
 const bp=await peer(refs.actualBootstrapReview,'INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_BOOTSTRAP_REVIEW_PASSED_V1',refs.resourceSourceIndex.sha256,'resourceSourceIndexSha256');
 need(bp.verifiedPassed===true&&bp.toolingSourceIndexSha256===refs.toolingIndex.sha256&&bp.engineSha256===refs.engine.sha256&&bp.metadataSha256===refs.metadata.sha256&&bp.freezeReceiptSha256===refs.freezeReceipt.sha256&&bp.nativeSourceFiles===342&&bp.selectedManifestCount===9&&bp.engineExecuted===false,'Actual resource bootstrap DATA');
 for(const k of ['bootstrapConfig','bootstrapRootObservation','reviewedPins','rootPinReview'])need(isDeepStrictEqual(root[k],refs[k]),'Actual native bootstrap binding '+k);
 const fixture=authorityModel(root,sourceSha);
 async function recheck(){await family(ownRow);await regular(configRow);await regular(rootRow);for(const r of manifest.files)await streamHash(r);for(const r of refs.families)await family(r.index);await family(root.sourceIndependentReview.index);await packagingPhysical(refs.packagingMap);environment(refs);}
 return Object.freeze({sourceSha,ownRow,configRow,rootRow,root,refs,fixture,recheck});
}
export async function resourceComponentPreflight(sourceSha,configDescriptor){
 const source=await authenticate(sourceSha,descriptor(configDescriptor));
 // The genuine original-context API is called unmodified after all custom
 // source/package inputs and current resource pin values are authenticated.
 const {resourceBootstrapPreflight}=await import(pathToFileURL(source.refs.bootstrapEntry.path));
 const native=await resourceBootstrapPreflight({configDescriptor:source.refs.bootstrapConfig});
 const expected=JSON.parse(await regular(source.refs.actualBootstrapWholeFrame)),comparison={...native};delete comparison.recheck;
 need(isDeepStrictEqual(comparison,expected),'Whole actual bootstrap frame; no metadata projection');
 need(native.engine.sha256===source.refs.engine.sha256&&native.metadataDescriptor.sha256===source.refs.metadata.sha256&&native.metadata.sourceManifest.length===342&&native.selectedManifests.length===9,'Genuine complete resource frame');
 need(native.sourceRoot===source.refs.frozenSourceRoot&&native.configuredSourceRoot===source.refs.configuredSourceRoot&&native.originalToolingRoot===dirname(source.refs.bootstrapEntry.path),'Distinct frozen/configured/original contexts');
 const recheck=async()=>{await source.recheck();await native.recheck();};await recheck();
 const frame=Object.freeze({source,native,recheck});constructionFrames.add(frame);return frame;
}
async function main(){
 need(process.argv.length===5,'SourceSHA mode exactDescriptorJSON');const [sourceSha,mode,json]=process.argv.slice(2);need(mode==='construct'||mode==='worker','Two finite construction modes');const input=descriptor(JSON.parse(json));
 if(mode==='construct'){const frame=await resourceComponentPreflight(sourceSha,input);const {buildComponent}=await import('./build.mjs');return buildComponent(frame);}
 const d=freeze(JSON.parse(await regular(input))),source=await authenticate(sourceSha,d.constructionConfig);
 need(d.schemaVersion===1&&d.state==='PARENT_AUDITED_RESOURCE342_COMPONENT_WORKER_V1'&&d.sourceIndexSha256===sourceSha&&isDeepStrictEqual(d.rootAction,source.rootRow)&&d.fixture===source.root.fixture&&d.outputRoot===source.root.outputRoot+'/worker'&&input.path===source.root.outputRoot+'/worker-descriptor.json','Exact owned parent descriptor');
 need(isDeepStrictEqual(d.engine,source.refs.engine)&&isDeepStrictEqual(d.metadata,source.refs.metadata)&&isDeepStrictEqual(d.code,source.refs.fixtures[d.fixture].code)&&isDeepStrictEqual(d.wit,source.refs.fixtures[d.fixture].wit),'Exact engine, original guest and WIT');
 need(d.selectedManifests.path===source.root.outputRoot+'/selected-manifests.json','Own manifest transport');
 const expected=JSON.parse(await regular(source.refs.actualBootstrapWholeFrame));need(isDeepStrictEqual(JSON.parse(await regular(d.selectedManifests)),expected.selectedManifests),'All nine exact manifests');
 const recheck=async()=>{await source.recheck();await regular(input);await regular(d.selectedManifests);};await recheck();const {buildWorker}=await import('./build-worker.mjs');const frame=Object.freeze({source,d,recheck});workerFrames.add(frame);return buildWorker(frame);
}
// No top-level await: body modules can import these standard data functions
// without a circular module-evaluation wait. No body runs at module import.
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))main().then(v=>process.stdout.write(JSON.stringify(v)+'\n'),()=>{process.stderr.write('{"state":"RESOURCE_COMPONENT_SOURCE_OR_CONSTRUCTION_FAILURE","originalFailureRetainedByOwnedCollector":true}\n');process.exitCode=1;});
