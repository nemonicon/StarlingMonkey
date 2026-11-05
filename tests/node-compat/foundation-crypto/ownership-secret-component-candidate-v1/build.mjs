// Dormant genuine355 secret-owner construction caller; builtins only before auth.
import {readFile,lstat,readdir,realpath,statfs} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-component-candidate-v1';
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
export function constructionAuthority(root,own,refs){
 need(root?.schemaVersion===1&&root.state==='ROOT_REVIEWED_SECRET355_COMPONENT_CONSTRUCTION_V1'&&root.phase==='component-build','New genuine component phase');
 need(same(root.sourceIndex,own)&&root.entry.path===join(HERE,'build.mjs')&&root.componentBuildAllowed===true&&root.componentInitializationAllowed===true&&root.retainedReadOnlyApiAllowed===true,'Exact own Source/entry/phase');
 need(same(root.actualRetainedPreflightReview,refs.actualRetainedPreflightReview)&&root.variant==='normal-off'&&root.engineSha256===refs.engine.sha256&&root.nativeSourceFiles===355,'Actual reviewed secret355 normal-OFF only');
 need(root.outputRoot===refs.outputRoot&&root.externalRoot===refs.externalRoot&&root.enclosingNodeDeadlineSeconds===1800&&root.enclosingPhaseDeadlineSeconds===2400&&root.maxComponentBytes===67108864,'Finite owned Root phase');
 for(const k of ['ordinaryGuestExportsAllowed','keyOrCryptoOperationsAllowed','gcPressureAllowed','originalOneShotApiAllowed','originalHelperAllowed','historicalCallableAllowed','normalOrGcBuildAllowed','metadataProjectionAllowed','otherVariantsAllowed','generatedModuleImportAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed'])need(root[k]===false,'No additional phase '+k);
 need(root.actualComponentReview===null&&root.actualRuntimeAuthority===null,'No actual component/runtime adoption');captureDescriptor(root.retainedConfig);return true;
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
export function auditGuestInitialization(ast){
 need(ast?.type==='Program'&&Array.isArray(ast.body),'Actual guest parser Program');const holders=new Set(),exports=[];
 function literal(n){if(n===null)return;need(n&&typeof n==='object','Plain INIT value');if(n.type==='Literal'){need(n.value===null||['string','number','boolean'].includes(typeof n.value),'Plain scalar');return;}if(n.type==='ArrayExpression'){for(const x of n.elements)literal(x);return;}need(n.type==='ObjectExpression','No INIT calls/new/await/identifier resolution');for(const p of n.properties){need(p.type==='Property'&&p.kind==='init'&&!p.computed&&!p.method&&!p.shorthand,'Plain INIT dictionary');literal(p.value);}}
 for(const item of ast.body){const n=item.type==='ExportNamedDeclaration'?item.declaration:item;
  if(item.type==='ExportNamedDeclaration'){need(n?.type==='FunctionDeclaration'&&!item.source,'Only actual function definitions exported');exports.push(n.id.name);}
  if(n?.type==='FunctionDeclaration')continue;
  need(n?.type==='VariableDeclaration','No top-level execution/import/async work');for(const d of n.declarations){need(d.id.type==='Identifier','Plain INIT binding');literal(d.init);if(['rawKey','jwkKey','knownConstructor'].includes(d.id.name)){need(d.init?.type==='Literal'&&d.init.value===null,'No key owners at INIT');holders.add(d.id.name);}}
 }
 need(holders.size===3&&same(exports.sort(),['clear','inspect','run','validate']),'Full guarded fixture and empty key holders');return{topLevelCryptoOrKeyOrAsyncCalls:false,keyHoldersInitiallyNull:true,publicFunctions:exports};
}
async function validateActualPreflight(c,refs){
 const actual=await c.proof(refs.actualRetainedPreflightReview),contract=await c.read(refs.actualRetainedPreflightContract);
 need(actual.schemaVersion===1&&contract.schemaVersion===1&&actual.state===contract.requiredReviewState&&actual.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_RETAINED_PREFLIGHT_RESULTS_REVIEW_PASSED_V1','Real completed d80e DATA review');
 for(const g of ['requiredFixedValues','requiredExactDescriptors','requiredPairs'])for(const[k,v]of Object.entries(contract[g]))need(same(actual[k],v),'Actual read-only contract '+k);
 need(same(actual.coverage,contract.requiredCoverage)&&actual.sourceIndexSha256===refs.retainedSourceIndex.sha256&&same(actual.recordData,refs.actualRetainedRecordData),'Exact retained record DATA binding');
 const data=await c.read(refs.actualRetainedRecordData);need(data.kind==='retained-secret355-bootstrap-v1'&&same(data.sourceIndex,refs.retainedSourceIndex),'Actual full six-property record DATA');return data.historicalBootstrap;
}
async function authenticate(input){
 const configRow=captureDescriptor(input);need(HERE===ORIGINAL&&process.version==='v22.14.0'&&process.execArgv.length===0,'Real own context/plain pinned Node22');
 for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])need(!process.env[k],'No inherited override '+k);
 const c=new Capture(),config=await c.read(configRow),own=captureDescriptor(config.sourceIndex);need(config.schemaVersion===1&&config.state==='SECRET355_COMPONENT_CONFIG_V1'&&own.path===join(HERE,'index.json'),'New exact component config/Source');
 const rows=await c.family(own),refs=await c.read(rows.find(r=>r.path===join(HERE,'references.json'))),inputs=await c.read(rows.find(r=>r.path===join(HERE,'source-inputs.json')));
 need(inputs.schemaVersion===1&&inputs.files.length>=28208&&inputs.files.length<=45000&&new Set(inputs.files.map(r=>r.path)).size===inputs.files.length,'Complete finite dependency/protection ledger');
 for(const r of inputs.files)await c.file(r);for(const ix of inputs.families)await c.family(ix);
 const rootRow=captureDescriptor(config.rootAuthority),root=await c.read(rootRow);constructionAuthority(root,own,refs);await c.file(root.entry);need(same(root.entry,rows.find(r=>r.path===join(HERE,'build.mjs'))),'Exact actual entry');
 const peer=await c.proof(root.sourceIndependentReview);need(peer.schemaVersion===1&&peer.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_SOURCE_REVIEW_PASSED_V1'&&peer.componentSourceIndexSha256===own.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true&&peer.ownerActionsInvoked===false,'New exact Source peer, not self-approval');
 need(await realpath(process.execPath)===refs.node.path,'Actual pinned Node binary');await c.file(refs.node);
 const history=await validateActualPreflight(c,refs),retainedConfig=captureDescriptor(root.retainedConfig),ro=await c.read(retainedConfig);await c.file(ro.rootAuthority);
 need(same(ro.sourceIndex,refs.retainedSourceIndex),'Genuine original retained API config');await c.recheck();return{c,configRow,own,refs,root,rootRow,history,retainedConfig,readonlyRoot:captureDescriptor(ro.rootAuthority)};
}
async function headroom(path,minimum){const s=await statfs(path);need(s.bavail*s.bsize>=minimum,'Operational free disk bound, no space guarantee');}
export async function buildSecretComponent({configDescriptor}={}){
 const f=await authenticate(configDescriptor),{c,refs,root}=f;let record=null,packaging=null,out=null,primary=null,finalErrors=[],componentRow=null,emittedExports=null,sourceAudit=null,componentizationAttempted=false;
 const recheck=async()=>{await c.recheck();if(packaging)await packaging.recheck();};
 await headroom(dirname(refs.outputRoot),2*1024*1024*1024);try{await lstat(refs.outputRoot);throw new Error('Fresh output root required');}catch(e){need(e.code==='ENOENT','Fresh output root required');}
 try{
  // Full Source/protection/phase before ANY custom import; no old bootstrap.
  const api=await import(pathToFileURL(refs.retainedApi.path));need(typeof api.retainedSecretBootstrapPreflight==='function','Actual c47 record API');
  record=await api.retainedSecretBootstrapPreflight({configDescriptor:f.retainedConfig});const h=validateRetainedRecord(record,refs,f.history,f.retainedConfig,f.readonlyRoot);await c.recheck();
  const {loadPackaging,packagingEnvironment}=await import(pathToFileURL(refs.packagingHelper.path));packaging=await loadPackaging(refs.packagingMap);packagingEnvironment(packaging);
  need(packaging.packagingRoot===refs.physicalRoles.packagingRoot&&packaging.toolchainRoot===refs.physicalRoles.toolchainRoot&&packaging.packagerRoot===refs.physicalRoles.packagerRoot&&h.componentizeSourceRoot===refs.physicalRoles.frozenEmbeddingSourceRoot,'Exact separate native/packaging roles');
  const {DurableOutput}=await import(pathToFileURL(refs.durableHelper.path)),abi=await import(pathToFileURL(refs.abiHelper.path));await recheck();out=await DurableOutput.create(refs.outputRoot);
  await out.write('retained-record-data.json',Object.fromEntries(Object.entries(record).filter(([k])=>k!=='recheck')),{json:true});
  await out.write('retained-record-shape.json',Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptors(record)).map(([k,d])=>[k,{type:typeof d.value,writable:d.writable,configurable:d.configurable,enumerable:d.enumerable}])) ,{json:true});
  await recheck();const {loadToolchain}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/toolchain.mjs'))),toolchain=await loadToolchain();need(await realpath(toolchain.directory)===packaging.toolchainRoot,'Genuine authenticated toolchain API');
  const {validateManifest}=await import(pathToFileURL(join(packaging.packagingRoot,'builtins/node-compat/validate-manifest.mjs'))),schema=await c.read(refs.manifestSchema);
  for(const m of h.selectedManifests)validateManifest(m,schema);
  const {builtinMap}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/module-selection.mjs'))),map=builtinMap(h.selectedManifests);need(!Object.hasOwn(map,'node:crypto')&&!Object.hasOwn(map,'crypto'),'Public Nodecrypto stays unadmitted');
  const guest=new TextDecoder('utf-8',{fatal:true}).decode(await readFile(refs.guest.path)),wit=new TextDecoder('utf-8',{fatal:true}).decode(await readFile(refs.wit.path));await c.file(refs.guest);await c.file(refs.wit);
  const init=auditGuestInitialization(toolchain.parseAst(guest,{},refs.guest.path));await out.write('guest-initialization-audit.json',init,{json:true});
  const {bundleProfile}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/profile-bundler.mjs')));
  const bundle=await bundleProfile({rolldown:toolchain.rolldown,parseAst:toolchain.parseAst,input:refs.guest.path,builtinManifests:h.selectedManifests,virtualModules:{}});
  await out.write('bundle-return.json',bundle,{json:true});need(typeof bundle.code==='string','Complete actual bundle text');await out.write('bundle.mjs',Buffer.from(bundle.code));
  need(bundle.imports.length===0&&bundle.moduleIds.length===1&&await realpath(bundle.moduleIds[0])===refs.guest.path,'Single physical complete guest, no shim/provider/import');
  need(same([...new Set(Object.values(map))].sort(),bundle.admittedBuiltins),'Actual full11 manifest map used by bundler');
  await out.write('whole-manifest-selection.json',{manifests:h.selectedManifests,map,publicNodeCryptoAdmitted:false,nativeMetadataUnchanged:true},{json:true});
  const {loadComponentizer}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/componentizer.mjs'))),selected=await loadComponentizer(toolchain);
  need(selected.provenance.selection==='patched-import-i32-clock-v2'&&selected.provenance.legacyEngineDiagnosticEnabled===false&&selected.provenance.debugScalarOOMDiagnostic===null,'Real old reviewed clock-v2 packager only; no diagnostic/native projection');
  const options=abi.componentOptions({engine:h.engine,adapter:packaging.adapter},wit);await out.write('component-options.json',options,{json:true});
  await headroom(refs.outputRoot,800*1024*1024);await recheck();await record.recheck();
  await out.write('before-componentization.json',{engine:h.engine,metadata:h.metadataDescriptor,guest:refs.guest,wit:refs.wit,allManifests:11,keyCallsAllowed:false,ordinaryGuestExportsAllowed:false},{json:true});
  componentizationAttempted=true;const result=await selected.componentize(bundle.code,options);
  await out.write('selected-return-transport.json',{type:typeof result,componentIsUint8Array:result?.component instanceof Uint8Array,componentBytes:result?.component instanceof Uint8Array?result.component.length:null},{json:true});
  need(result?.component instanceof Uint8Array&&result.component.length<=root.maxComponentBytes,'Whole finite component bytes');componentRow=await out.write('crypto-secret-owner.component.wasm',result.component);
  await out.write('interface-audit.json',result.interfaceAudit,{json:true});need(Array.isArray(result.interfaceAudit?.emittedImports)&&result.interfaceAudit.emittedImports.length===0,'Actual final imports[]');
  const {componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco'))),emitted=await componentWit(result.component);await out.write('emitted.wit',Buffer.from(emitted));emittedExports=abi.parsePublicWit(emitted);
  const generated=await transpile(result.component,{name:'crypto_secret_owner',wasiShim:false});await out.write('transpile-return-transport.json',{type:typeof generated,filesType:typeof generated?.files,importsIsArray:Array.isArray(generated?.imports),exportsIsArray:Array.isArray(generated?.exports)},{json:true});
  need(generated?.files&&typeof generated.files==='object','Actual Jco file transport');await out.write('transpile-metadata.json',{imports:generated.imports,exports:generated.exports,fileNames:Object.keys(generated.files)},{json:true});
  for(const[name,bytes]of Object.entries(generated.files))await out.write('transpiled/'+name,bytes);abi.checkTranspileMetadata(generated);
  for(const n of ['crypto_secret_owner.js','crypto_secret_owner.d.ts','crypto_secret_owner.core.wasm'])need(generated.files[n]instanceof Uint8Array,'Whole named Jco artifact '+n);
  const glue=new TextDecoder('utf-8',{fatal:true}).decode(generated.files['crypto_secret_owner.js']),dts=new TextDecoder('utf-8',{fatal:true}).decode(generated.files['crypto_secret_owner.d.ts']);
  sourceAudit={exports:abi.publicJSExports(toolchain.parseAst(glue,{},'crypto_secret_owner.js')),declarations:abi.parsePublicDts(dts),generatedModuleImported:false,loadingProtocolReviewRequired:true,asyncScalarRuntimeProof:false};await out.write('generated-public-source-audit.json',sourceAudit,{json:true});await out.write('transpiled/package.json',Buffer.from('{"type":"module"}\n'));await out.recheck();
 }catch(error){primary={name:error?.name??null,message:error?.message??String(error),stack:error?.stack??null};}
 finally{
  try{if(record)await record.recheck();}catch(error){finalErrors.push({scope:'fresh-own-retained-recheck',name:error?.name??null,message:error?.message??String(error),stack:error?.stack??null});}
  try{await recheck();}catch(error){finalErrors.push({scope:'complete-source-and-packaging-protection',name:error?.name??null,message:error?.message??String(error),stack:error?.stack??null});}
  try{if(out)await out.recheck();}catch(error){finalErrors.push({scope:'owned-output',name:error?.name??null,message:error?.message??String(error),stack:error?.stack??null});}
 }
 if(!out){const error=new Error(primary?.message??'Construction refused before output');error.cause={primary,finalErrors};throw error;}
 const complete=primary===null&&finalErrors.length===0;try{
  const result=await out.write('results.json',{schemaVersion:1,state:complete?'SECRET_OWNER355_COMPONENT_CONSTRUCTED_UNREVIEWED_V1':'SECRET_OWNER355_COMPONENT_CONSTRUCTION_FAILED_V1',componentSourceIndexSha256:f.own.sha256,rootAuthority:f.rootRow,config:f.configRow,actualRetainedPreflightReview:refs.actualRetainedPreflightReview,engine:refs.engine,metadata:refs.metadata,guest:refs.guest,wit:refs.wit,component:componentRow,emittedExports,emittedImports:complete?[]:null,sourceAudit,primaryError:primary,finalProtectionErrors:finalErrors,componentizationAttempted,guestInitializationExecutedByComponentization:componentRow!==null?true:componentizationAttempted?null:false,ordinaryGuestExportsInvoked:false,keyOperationsInvoked:false,generatedModuleImported:false,asyncScalarRuntimeProof:false,operationalAdmission:false,runtimeAcceptanceClaim:false,requiresIndependentActualArtifactReview:true,externalOwnedRawZeroRequired:true},{json:true});
  const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});const completion=await out.write('completion.json',{schemaVersion:1,state:complete?'COMPLETE_UNREVIEWED_EXTERNAL_RAW_ZERO_REQUIRED':'FAILED_UNACCEPTED',index,result,component:componentRow,ordinaryGuestExportsInvoked:false,keyOperationsInvoked:false},{json:true});await out.recheck();return{root:out.root,index,completion,completeUnreviewed:complete};
 }finally{await out.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 need(process.argv.length===3,'One exact config descriptor JSON');const result=await buildSecretComponent({configDescriptor:JSON.parse(process.argv[2])});process.stdout.write(JSON.stringify(result)+'\n');if(!result.completeUnreviewed)process.exitCode=1;
}
