// Dormant genuine secret355 stock-Wasmtime host caller; builtins only before authentication.
import {readFile,lstat,readdir,realpath,readlink} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-host-candidate-v1';
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
export function plainHostEnvironment(env){
 for(const k of ['NODE_OPTIONS','NODE_PATH','JCO_DEBUG','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','RUST_LOG','RUST_BACKTRACE'])need(!env[k],'No inherited execution override '+k);
 for(const k of Object.keys(env))need(!k.startsWith('WASMTIME_'),'No inherited Wasmtime override '+k);return true;
}
export function hostAuthority(v,own,refs){
 need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_SECRET355_STOCK_WASMTIME_HOST_V1'&&v.phase==='stock-wasmtime-guarded-validate'&&same(v.sourceIndex,own),'New exact secret355 host Source/phase');
 need(v.variant==='normal-off'&&v.wasmtimeValidateAllowed===true&&v.boundedKeyFixtureAllowed===true&&v.guardedPrototypeCase3Allowed===true,'Only genuine four-case guarded normal fixture');
 need(v.nativeSourceFiles===355&&v.externalEmbeddingSources===3&&v.fullMetadataFields===75&&v.selectedManifestCount===11&&v.componentSha256===refs.artifacts.component.sha256&&v.engineSha256===refs.engine.sha256,'Actual c067/901 secret355 native roles');
 need(refs.actualRuntimeReview!==null&&refs.actualRuntimeContract!==null&&same(v.actualRuntimeReview,refs.actualRuntimeReview)&&same(v.actualRuntimeContract,refs.actualRuntimeContract),'Actual completed independent Jco DATA prerequisite required; pending Source refuses');
 need(same(v.actualArtifactReview,refs.actualArtifactReview)&&same(v.actualArtifactContract,refs.actualArtifactContract),'Exact component DATA review');
 need(v.outputRoot===refs.outputRoot&&v.externalOutputRoot===refs.externalOutputRoot&&v.externalParentDeadlineSeconds===2400&&v.freshProcesses===3&&v.invocation==='validate()'&&v.workerTimeoutMs===600000&&v.maxPipeBytes===16777216,'Finite three fresh zero-argument owned calls');
 need(same(v.monitorIndex,refs.monitorIndex)&&same(v.monitorEntry,refs.monitorEntry),'Genuine original monitor context');
 for(const k of ['nodeOracleAllowed','retainedApiAllowed','originalOneShotApiAllowed','originalHelperAllowed','historicalCallableAllowed','generatedJsAllowed','nativeBuildAllowed','nativeFreezeAllowed','componentBuildAllowed','gcAllowed','gcPressureAllowed','oomAllowed','faultInjectionAllowed','unsafeResetAllowed','otherVariantsAllowed','metadataProjectionAllowed','sourcePromotionAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','nativeFreeOrWipeClaim','isolatedRootClaim'])need(v[k]===false,'No extra authority '+k);
 need(v.actualHostReview===null,'No host outcome/adoption in advance');return true;
}
export function actualRuntimeModel(v,contract,refs){
 need(v?.schemaVersion===1&&v.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_RUNTIME_RESULTS_REVIEW_PASSED_V1'&&v.verifiedPassed===true&&v.sourceIndexSha256===refs.runtimeSourceIndex.sha256,'Actual independent new secret Jco runtime result');
 for(const[k,w]of Object.entries({componentSha256:refs.artifacts.component.sha256,engineSha256:refs.engine.sha256,nativeSourceFiles:355,externalEmbeddingSources:3,fullMetadataFields:75,selectedManifestCount:11,rawPublicStrings:23,caseRecords:20,guestKeyImports:10,guestSignAttempts:55,guestVerifyAttempts:50,successfulFullGuestTagsCompared:45,threeFreshOwnedNodeProcesses:true,allFourCasesReviewed:true,allRawTypedBeforeAssertionsReviewed:true,allSourceNativeApiPackageProtectionReviewed:true,operationalAdmission:false,runtimeAcceptanceClaim:false}))need(same(v[k],w),'Full actual Jco proof field '+k);
 need(contract?.schemaVersion===1&&contract.requiredReviewState===v.state,'Exact indexed runtime contract role');
 for(const k of ['requiredFixedValues','requiredExactDescriptors']){need(contract[k]&&typeof contract[k]==='object','Complete actual runtime contract '+k);for(const[n,w]of Object.entries(contract[k]))need(same(v[n],w),'Whole runtime contract '+n);}
 if(contract.requiredCoverage!==undefined)need(same(v.coverage,contract.requiredCoverage),'Complete exact runtime coverage');
 need(same(contract.artifacts,refs.artifacts),'Whole unchanged actual artifact map');return true;
}
export function artifactModel(v,contract,refs){
 need(v?.schemaVersion===1&&v.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_V2_ARTIFACT_REVIEW_PASSED_V1'&&v.verifiedPassed===true&&v.componentSourceIndexSha256===refs.componentSourceIndex.sha256,'Actual secret355 component review');
 need(v.componentSha256===refs.artifacts.component.sha256&&v.engineSha256===refs.engine.sha256&&v.nativeSourceFiles===355&&v.externalEmbeddingSources===3&&v.fullMetadataFields===75&&v.selectedManifestCount===11,'Actual355/3/75/11 context');
 need(same(v.emittedImports,[])&&same([...v.publicAbiFunctions].sort(),['clear','inspect','run','validate']),'Four scalar functions and no imports');
 for(const k of ['generatedModuleImported','ordinaryGuestExportsInvoked','keyOperationsInvoked','asyncScalarRuntimeProof'])need(v[k]===false,'Construction history remains construction '+k);
 need(same(contract.artifacts,v.artifacts)&&same(v.artifacts,refs.artifacts),'Exact component artifact contract');return true;
}
async function packageContext(c,refs){
 const m=await c.read(refs.packagingMap),root=m.publicationRoot,s=await lstat(root);
 need(m.state==='EXACT_EXISTING_PACKAGING_PHYSICAL_ROLES_NOT_NATIVE_AUTHORITY'&&m.originalZlibNativeFactsConsumed===false&&m.costActionStatesReused===false,'Original package DATA only');
 need(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o7777)===0o700&&s.dev===m.rootIdentity.device&&s.ino===m.rootIdentity.inode,'Actual package root identity/mode');
 const files=new Map(m.files.map(r=>[r.path,r])),links=new Map(m.links.map(r=>[r.destination,r])),seenFiles=new Set(),seenLinks=new Set();need(files.size===4934&&links.size===22,'Whole actual package4934+22');
 async function walk(base){for(const name of await readdir(base)){const p=join(base,name),n=p.slice(root.length+1),st=await lstat(p);if(st.isSymbolicLink()){const r=links.get(n);need(r&&await readlink(p)===r.newLinkText&&await realpath(p)===join(root,r.mappedTarget),'Exact selected original package alias');seenLinks.add(n);}else if(st.isDirectory()){need((st.mode&0o7777)===0o700,'Whole package directory modes');await walk(p);}else{const r=files.get(n);need(st.isFile()&&r&&st.nlink===1&&(st.mode&0o7777)===r.mode,'Exact package ordinary file mode/inode');await c.file({path:p,sha256:r.sha256,bytes:r.bytes});seenFiles.add(n);}}}
 for(const n of m.roleRoots)await walk(join(root,n));need(seenFiles.size===files.size&&seenLinks.size===links.size,'Whole package file/link membership');
}
async function authenticate(input){
 const configRow=captureDescriptor(input);need(HERE===ORIGINAL&&process.version==='v22.14.0'&&process.execArgv.length===0,'Original own host context/plain pinned Node22');plainHostEnvironment(process.env);
 const c=new Capture();let refs=null,inputs=null,primary=null;
 const recheck=async()=>{await c.recheck();if(inputs){for(const m of inputs.modeRows)need(((await lstat(m.file.path)).mode&0o7777)===m.mode,'Every protected input mode');for(const t of inputs.historicalDonorTrees){const names=new Set(t.names);need(names.size===t.names.length,'Unique historical donor inventory');await c.tree(t.root,names);}}if(refs)await packageContext(c,refs);};
 try{
  const cfg=await c.read(configRow),own=captureDescriptor(cfg.sourceIndex);need(cfg.schemaVersion===1&&cfg.state==='SECRET355_STOCK_WASMTIME_HOST_CONFIG_V1'&&own.path===join(HERE,'index.json'),'Exact own Source/config');
  const rows=await c.family(own);refs=await c.read(rows.find(r=>r.path===join(HERE,'references.json')));inputs=await c.read(rows.find(r=>r.path===join(HERE,'source-inputs.json')));
  need(inputs.schemaVersion===1&&inputs.files.length>=34000&&inputs.files.length<=50000&&new Set(inputs.files.map(r=>r.path)).size===inputs.files.length&&inputs.modeRows.length===inputs.files.length,'Complete unique actual finite Source/native/proof/tool protection');
  for(const r of inputs.files)await c.file(r);for(const x of inputs.families)await c.family(x);
  const rootRow=captureDescriptor(cfg.rootAuthority),root=await c.read(rootRow);hostAuthority(root,own,refs);need(same(root.entry,rows.find(r=>r.path===join(HERE,'entry.mjs')))&&same(root.externalController,rows.find(r=>r.path===join(HERE,'external.py'))),'Actual own caller bytes');
  const peer=await c.proof(root.sourceIndependentReview);need(peer.schemaVersion===1&&peer.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_HOST_SOURCE_REVIEW_PASSED_V1'&&peer.sourceIndexSha256===own.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true,'Separate host Source peer');for(const k of ['ownerActionsInvoked','hostActionsInvoked','runtimeActionsInvoked'])need(peer[k]===false,'Source proof only '+k);
  const ar=await c.proof(refs.actualArtifactReview),arRows=await c.family(refs.actualArtifactReview.index);need(arRows.filter(r=>same(r,refs.actualArtifactContract)).length===1,'Artifact contract indexed once');artifactModel(ar,await c.read(refs.actualArtifactContract),refs);
  const runtime=await c.proof(refs.actualRuntimeReview),runtimeRows=await c.family(refs.actualRuntimeReview.index);need(runtimeRows.filter(r=>same(r,refs.actualRuntimeContract)).length===1,'Runtime DATA contract indexed once');const contract=await c.read(refs.actualRuntimeContract);actualRuntimeModel(runtime,contract,refs);
  const exact=contract.requiredExactDescriptors,ixRow=captureDescriptor(exact.actualIndex),oracleRow=captureDescriptor(exact.nodeOracle),wrapperRow=captureDescriptor(exact.rawWrapper);need(same(runtime.actualIndex,ixRow)&&same(runtime.nodeOracle,oracleRow)&&same(runtime.rawWrapper,wrapperRow),'Whole audited actual runtime/index/oracle/wrapper roles');
  const jcoRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v3';need(ixRow.path===join(jcoRoot,'index.json')&&wrapperRow.path===join(jcoRoot,'wrapper/raw/001.json')&&oracleRow.path===join(jcoRoot,'node-oracle.json'),'Actual runtime V3 output context; no old paths');
  const ix=await c.read(ixRow),names=new Set(['index.json','completion.json']);need(ix.schemaVersion===1&&ix.files.length>30&&ix.files.length<100,'Finite actual complete runtime inventory');
  for(const x of ix.files){const n=relative(x.path);need(!names.has(n),'Unique actual runtime indexed row');names.add(n);await c.file({path:join(jcoRoot,n),sha256:x.sha256,bytes:x.bytes});}await c.file(exact.actualCompletion);await c.tree(jcoRoot,names);c.families.push({base:jcoRoot,names});
  const oracle=await c.read(oracleRow),wrapper=await c.read(wrapperRow);need(same(Object.keys(wrapper),['schemaVersion','name','args','kind','observed'])&&wrapper.schemaVersion===1&&wrapper.name==='validate'&&same(wrapper.args,[])&&wrapper.kind==='return'&&same(Object.keys(wrapper.observed),['type','value'])&&wrapper.observed.type==='string'&&typeof wrapper.observed.value==='string','Whole actual V3 typed wrapper, no legacy top-level value');
  need(await realpath(process.execPath)===refs.node.path,'Actual pinned Node executable');await c.file(refs.node);await c.file(refs.wasmtime);for(const r of Object.values(refs.artifacts))await c.file(r);
  await recheck();return Object.freeze({kind:'secret355-stock-wasmtime-host-admission-v1',sourceIndexSha256:own.sha256,rootAction:rootRow,artifacts:refs.artifacts,component:refs.artifacts.component,wasmtime:refs.wasmtime,oracle,jcoWrapper:wrapper,outputRoot:refs.outputRoot,workerTimeoutMs:root.workerTimeoutMs,maxPipeBytes:root.maxPipeBytes,recheck});
 }catch(error){primary=error;throw error;}
 finally{try{await recheck();}catch(error){if(primary!==null)throw new AggregateError([primary,error],'Host authentication and final protection failed');throw error;}}
}
export async function runSecretHost({configDescriptor}={}){
 const frame=await authenticate(configDescriptor);let primary=null;try{const body=await import(pathToFileURL(join(HERE,'run.mjs')));return await body.runWasmtime(frame);}catch(error){primary=error;throw error;}finally{try{await frame.recheck();}catch(error){if(primary!==null)throw new AggregateError([primary,error],'Host phase and final protection failed');throw error;}}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===3,'One exact new host config descriptor');process.stdout.write(JSON.stringify(await runSecretHost({configDescriptor:JSON.parse(process.argv[2])}))+'\n');}
