// Dormant observer: Node built-ins only before full authentication. The only
// operational dynamic import is the original d62 bootstrap API after all gates.
import { readFile,lstat,readdir,realpath,open } from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import { createHash } from 'node:crypto';
import { isDeepStrictEqual } from 'node:util';
import { dirname,join,resolve,isAbsolute } from 'node:path';
import { fileURLToPath,pathToFileURL } from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-artifact-bootstrap-v3-root-controller-candidate-v1';
const REPO='/Users/dan/dev/StarlingMonkey';
const same=isDeepStrictEqual,sha=b=>createHash('sha256').update(b).digest('hex');
function need(value,message){if(!value)throw new Error(message);}
const FORBIDDEN=['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed','moduleAdmissionAllowed'];
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
async function write(path,bytes){const f=await open(path,'wx',0o600);try{await f.writeFile(bytes);await f.sync();}finally{await f.close();}}


async function currentDescriptor(path){
  need(isAbsolute(path)&&resolve(path)===path,'Canonical input path');
  const before=await lstat(path);need(before.isFile()&&!before.isSymbolicLink(),'Regular current DATA');
  const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(path)){h.update(b);bytes+=b.length;}
  const after=await lstat(path);need(same(identity(before),identity(after))&&bytes===after.size,'Stable current DATA');
  return captureDescriptor({path,sha256:h.digest('hex'),bytes});
}
async function save(path,value){await write(path,Buffer.from(JSON.stringify(value,null,2)+'\n'));return currentDescriptor(path);}
function onlyFourPinEdits(before,after){
  const edits=new Map([
    [JSON.stringify(['state']),['UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3','ROOT_REVIEWED_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PINS_V3']],
    [JSON.stringify(['reviewRequired']),[true,false]],
    [JSON.stringify(['variants','normal-off','state']),['unreviewed-secret-owner355-normal-off-pin-v3','reviewed-secret-owner355-normal-off-pin-v3']],
    [JSON.stringify(['variants','normal-off','reviewRequired']),[true,false]],
  ]),seen=new Set();
  function walk(a,b,path){
    if(same(a,b))return;
    if(a!==null&&b!==null&&typeof a==='object'&&typeof b==='object'&&Array.isArray(a)===Array.isArray(b)){
      need(same(Object.keys(a).sort(),Object.keys(b).sort()),'Complete unchanged pin field set');
      if(Array.isArray(a))need(a.length===b.length,'Complete unchanged pin list');
      for(const key of Object.keys(a))walk(a[key],b[key],path.concat(key));return;
    }
    const key=JSON.stringify(path),allowed=edits.get(key);
    need(allowed&&same(a,allowed[0])&&same(b,allowed[1]),'Exactly four permitted state/flag edits');seen.add(key);
  }
  walk(before,after,[]);need(seen.size===4,'All four actual state/flag changes required');
  need(same(Object.keys(after.variants).sort(),['disabled-off','gc-off','normal-off','normal-runtime'])&&['normal-runtime','gc-off','disabled-off'].every(k=>after.variants[k]===null),'Only normal-OFF is present');
}
async function privateTree(c,root,names){
  await c.tree(root,names);
  async function visit(path){const s=await lstat(path);need(!s.isSymbolicLink(),'No private tree links');if(s.isDirectory()){need((s.mode&0o7777)===0o700,'Private frozen directory');for(const n of await readdir(path))await visit(join(path,n));}else need(s.isFile()&&s.nlink===1&&(s.mode&0o7777)===0o600,'Private frozen regular file');}
  await visit(root);
}
async function authorize(configDescriptor){
  need(HERE===ORIGINAL&&process.version==='v22.14.0'&&process.execArgv.length===0,'Original observer and plain pinned Node22');
  for(const key of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])need(!process.env[key],'No loader override '+key);
  const c=new Capture(),configRow=captureDescriptor(configDescriptor),cfg=await c.read(configRow);
  need(cfg.schemaVersion===1&&cfg.state==='SECRET355_BOOTSTRAP_ROOT_CONTROLLER_CONFIG_V1'&&cfg.phase==='bootstrap-js','New explicit JS observation config');
  const own=captureDescriptor(cfg.controllerIndex);need(own.path===join(HERE,'index.json'),'Original observer Source family');await c.family(own);
  const refs=await c.read(await currentDescriptor(join(HERE,'references.json'))),inputs=await c.read(await currentDescriptor(join(HERE,'source-inputs.json')));
  need(refs.schemaVersion===1&&refs.originalControllerRoot===HERE&&inputs.schemaVersion===1&&Array.isArray(inputs.files)&&inputs.files.length>=27800&&inputs.files.length<=40000,'Full finite Source/protection closure');
  need(new Set(inputs.files.map(r=>r.path)).size===inputs.files.length,'Unique declared rows');
  for(const r of inputs.files)await c.file(r);
  for(const ix of inputs.families)await c.family(ix);
  await c.file(refs.node);await c.file(refs.python);need(await realpath(process.execPath)===refs.node.path,'Pinned actual Node executable');
  const root=await c.read(cfg.rootAuthority);
  need(root.schemaVersion===1&&root.state==='ROOT_REVIEWED_SECRET355_BOOTSTRAP_CONTROLLER_PHASE_V1'&&root.phase==='bootstrap-js'&&same(root.controllerIndex,own),'New Root JS authority');
  need(same(root.controllerEntry,await currentDescriptor(join(HERE,'ownership-secret-artifact-bootstrap-v3-root-controller.py')))&&same(root.runnerEntry,await currentDescriptor(fileURLToPath(import.meta.url))),'Actual new parent/observer bytes');
  need(root.pinDerivationAllowed===false&&root.bootstrapJsAllowed===true&&same(root.toolingIndex,refs.toolingIndex)&&same(root.independentExportReview,refs.exportReview)&&same(root.actualExportCandidate,refs.exportCandidate),'Explicit narrow one-shot action');
  for(const key of FORBIDDEN)need(root[key]===false,'No other authority '+key);
  need(root.actualBootstrap===null&&root.runtimeAuthority===null,'No projected result/runtime authority');
  for(const key of ['pinOutputRoot','observerOutputRoot','observerExternalRoot','outerDeadlineSeconds'])need(root[key]===refs[key],'Fixed role '+key);
  const peer=await c.proof(root.sourceIndependentReview);
  need(peer.schemaVersion===1&&peer.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_BOOTSTRAP_ROOT_CONTROLLER_SOURCE_REVIEW_PASSED_V1'&&peer.controllerSourceIndexSha256===own.sha256&&peer.toolingSourceIndexSha256===refs.toolingIndex.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true&&peer.ownerActionsInvoked===false,'New independent own Source review');
  for(const key of ['ownerActionsInvoked','hostActionsInvoked','bootstrapActionsInvoked'])need(peer[key]===false,'Own independent Source scope '+key);
  await c.family(refs.toolingIndex);const sourcePeer=await c.proof(refs.toolingSourceReview);
  need(sourcePeer.schemaVersion===1&&sourcePeer.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V3'&&sourcePeer.toolingSourceIndexSha256===refs.toolingIndex.sha256&&sourcePeer.sourceOnly===true&&sourcePeer.sourceReviewPassed===true,'Actual d62/522e Source pair');
  for(const key of ['ownerActionsInvoked','hostActionsInvoked','exportOrBootstrapActionsInvoked'])need(sourcePeer[key]===false,'Source scope '+key);
  const proof=await c.proof(refs.exportReview),contract=await c.read(refs.exportContract);
  need(contract.schemaVersion===3&&contract.requiredResultSchemaVersion===3&&proof.schemaVersion===3&&proof.state===contract.requiredReviewState&&proof.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_OFF_PIN_EXPORT_REVIEW_PASSED_V3','Exact actual export review state');
  for(const group of ['requiredFixedValues','requiredExactDescriptors','requiredPairs'])for(const [key,value]of Object.entries(contract[group]))need(same(proof[key],value),'Complete export contract '+key);
  need(same(proof.coverage,contract.requiredCoverage)&&same(proof.candidate,refs.exportCandidate)&&same(proof.rootObservation,refs.exportRootObservation)&&same(proof.inputClosure,refs.exportInputLedger),'Actual candidate/Root/closure bindings');
  const tr=await c.read(refs.toolingReferences);
  for(const source of [refs.toolingInputs,tr.protectedInputLedger,refs.exportInputLedger])for(const r of(await c.read(source)).files)await c.file(r);
  const receipt=await c.read(tr.freezeReceipt);need(receipt.copies.length===1902,'Actual frozen1902 rows');
  const names=new Set(['normal-off-freeze-receipt.json']);for(const r of receipt.copies){need(r.path.startsWith(tr.frozenRoot+'/'),'Actual frozen namespace');names.add(relative(r.path.slice(tr.frozenRoot.length+1)));}
  for(const r of receipt.copies)if(r.original!==null){const a=await lstat(r.path),b=await lstat(r.original);need(a.nlink===1&&(a.dev!==b.dev||a.ino!==b.ino),'Independent actual frozen copy inode');}
  need(names.size===1903,'Actual complete frozen membership');await privateTree(c,tr.frozenRoot,names);c.families.push({base:tr.frozenRoot,names});
  const normal=await c.read(tr.normalProtection);need(normal.originalReferenceEntries===1387&&normal.requiredNormalFreezeMembership.length===1391,'Untouched old normal scope');
  await c.tree(dirname(normal.freezeReceipt.path),new Set(normal.requiredNormalFreezeMembership));c.families.push({base:dirname(normal.freezeReceipt.path),names:new Set(normal.requiredNormalFreezeMembership)});
  const toolingCfg=await c.read(root.toolingBootstrapConfig),toolingRoot=await c.read(root.toolingBootstrapAuthority);
  need(same(toolingCfg,{schemaVersion:3,state:'SECRET_OWNER355_ARTIFACT_TOOLING_CONFIG_V3',phase:'bootstrap',toolingIndex:refs.toolingIndex,rootAuthority:root.toolingBootstrapAuthority}),'Original d62 config binding');
  need(toolingRoot.schemaVersion===3&&toolingRoot.state==='ROOT_REVIEWED_SECRET_OWNER355_ARTIFACT_TOOLING_PHASE_V3'&&toolingRoot.phase==='bootstrap'&&toolingRoot.variant==='normal-off'&&same(toolingRoot.toolingIndex,refs.toolingIndex)&&same(toolingRoot.sourceIndependentReview,refs.toolingSourceReview),'Separate actual d62 bootstrap authority');
  need(toolingRoot.bootstrapAllowed===true&&toolingRoot.exportAllowed===false&&toolingRoot.runtimeAuthority===null&&toolingRoot.actualBootstrap===null,'Only read-only bootstrap is permitted');
  for(const key of FORBIDDEN.filter(k=>k!=='moduleAdmissionAllowed'))need(toolingRoot[key]===false,'No original action '+key);
  for(const key of ['nativeSourceIndex','verifierSourceIndex','actualVerifierReview','actualArtifactReview','engine','metadata','freezeReceipt','configuredSourceRoot','frozenSourceRoot','frozenRoot'])need(same(toolingRoot[key],tr[key]),'Original source/frozen role '+key);
  for(const [key,value]of Object.entries({nativeSourceFiles:355,externalEmbeddingSources:3,selectedManifestCount:11,outputRoot:refs.bootstrapOutputRoot,externalOutputRoot:refs.bootstrapExternalRoot,jsOutputRoot:refs.bootstrapJsRoot,externalParentDeadlineSeconds:600,expectedCompleteVerifierCalls:1,actualExportCandidate:refs.exportCandidate,independentExportReview:refs.exportReview,reviewedPins:root.reviewedPins,rootPinReview:root.rootPinReview}))need(same(toolingRoot[key],value),'Complete original bootstrap field '+key);
  const candidate=await c.read(refs.exportCandidate),reviewed=await c.read(root.reviewedPins),review=await c.read(root.rootPinReview);onlyFourPinEdits(candidate,reviewed);
  const expectedReview=await c.read(refs.pinReviewTemplate);Object.assign(expectedReview,{state:'ROOT_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V3',toolingIndex:refs.toolingIndex,reviewedPins:root.reviewedPins,actualExportCandidate:refs.exportCandidate,independentExportReview:refs.exportReview});need(same(review,expectedReview),'Exact schema3 Root pin review');
  const recheck=async()=>{await c.recheck();await privateTree(c,tr.frozenRoot,names);};
  await recheck();return{c,cfg,configRow,own,root,refs,tr,recheck};
}

export function capturePublicReturn(value){
  need(value!==null&&typeof value==='object','Public bootstrap object');
  const descriptors=Object.getOwnPropertyDescriptors(value),keys=Reflect.ownKeys(descriptors);
  const shape=keys.map(key=>{const d=descriptors[key];return{key:typeof key==='string'?key:String(key),keyType:typeof key,valueType:Object.hasOwn(d,'value')?typeof d.value:null,enumerable:d.enumerable,configurable:d.configurable,writable:d.writable??null,getter:typeof d.get,setter:typeof d.set};});
  return{descriptors,keys,shape};
}
export function publicDataAndCallable(snapshot,frozen){
  need(frozen&&snapshot.keys.every(k=>typeof k==='string')&&snapshot.keys.includes('recheck'),'Frozen own string fields plus actual recheck');
  const data={};let callable=null;
  for(const key of snapshot.keys){const d=snapshot.descriptors[key];need(Object.hasOwn(d,'value')&&d.enumerable===true&&d.configurable===false&&d.writable===false,'Every own field is frozen enumerable DATA');if(key==='recheck'){need(typeof d.value==='function','Actual callable recheck');callable=d.value;}else{need(typeof d.value!=='function'&&typeof d.value!=='undefined'&&typeof d.value!=='symbol','No omitted non-DATA field');Object.defineProperty(data,key,{value:d.value,enumerable:true,writable:false,configurable:false});}}
  const meta=Object.getOwnPropertyDescriptors(callable);
  return{data,callable,callableDescriptor:{property:'recheck',valueType:'function',enumerable:true,configurable:false,writable:false,ownName:meta.name?.value??null,ownLength:meta.length?.value??null,returnObjectFrozen:frozen}};
}
async function absent(path){try{await lstat(path);throw new Error('Future output already exists: '+path);}catch(error){if(error.code!=='ENOENT')throw error;}}

async function main(configDescriptor,ownerDescriptor){
  const f=await authorize(configDescriptor),{c,refs,root}=f;
  const owner=await c.read(ownerDescriptor);need(owner.schemaVersion===1&&same(owner.controllerIndex,f.own)&&same(owner.rootAuthority,f.cfg.rootAuthority)&&same(owner.config,f.configRow)&&owner.outputRoot===refs.observerOutputRoot,'Actual enclosing owned parent');
  const out=refs.observerOutputRoot,s=await lstat(out);need(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o7777)===0o700&&same([s.dev,s.ino],owner.outputIdentity),'Owned private output identity');
  for(const path of [refs.bootstrapOutputRoot,refs.bootstrapExternalRoot,refs.bootstrapJsRoot])await absent(path);
  let apiCalls=0,recheckCalls=0,stage='preimport',dataRow=null,pythonFrameRow=null,shapeRow=null,callableRow=null,primaryError=null,protectionError=null,wholeEqual=false;
  try{
    await f.recheck();
    // Complete own/source/export/original protection precedes this only custom import.
    const api=await import(pathToFileURL(refs.bootstrapEntry.path));need(typeof api.secretArtifactBootstrapPreflight==='function','Genuine original public API');
    await save(join(out,'api-call-start.json'),{schemaVersion:1,api:refs.bootstrapEntry,config:root.toolingBootstrapConfig,callNumber:1});
    stage='api-call';apiCalls++;const value=await api.secretArtifactBootstrapPreflight({configDescriptor:root.toolingBootstrapConfig});
    stage='public-return';const snapshot=capturePublicReturn(value);shapeRow=await save(join(out,'public-return-shape.json'),{schemaVersion:1,ownFields:snapshot.shape,returnObjectFrozen:Object.isFrozen(value)});
    const captured=publicDataAndCallable(snapshot,Object.isFrozen(value));
    // Every own DATA field is retained before equality/semantic assertions.
    dataRow=await save(join(out,'whole-public-data.json'),captured.data);callableRow=await save(join(out,'callable-property.json'),captured.callableDescriptor);
    pythonFrameRow=await currentDescriptor(join(refs.bootstrapOutputRoot,'bootstrap-frame.json'));const pythonFrame=await c.read(pythonFrameRow);
    need(same(captured.data,pythonFrame),'Whole public DATA equals actual retained Python frame');wholeEqual=true;
    need(captured.data.schemaVersion===3&&captured.data.state==='SECRET_OWNER355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V3'&&same(captured.data.toolingIndex,refs.toolingIndex)&&same(captured.data.rootAuthority,root.toolingBootstrapAuthority)&&same(captured.data.config,root.toolingBootstrapConfig),'Actual whole frame identity');
    need(captured.data.nativeSourceFiles===355&&captured.data.externalEmbeddingSources===3&&captured.data.selectedManifestCount===11&&captured.data.currentCompleteVerifierCalls===1&&captured.data.validationBootstrapOnly===true,'Complete source-supported validation scope');
    for(const key of ['engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','grantsRuntimeAuthority'])need(captured.data[key]===false,'No runtime authority '+key);
    await save(join(out,'returned-recheck-start.json'),{schemaVersion:1,callNumber:1});stage='returned-recheck';recheckCalls++;const returned=await captured.callable();
    await save(join(out,'returned-recheck-result.json'),{schemaVersion:1,fulfilled:true,valueType:typeof returned});need(returned===undefined,'Genuine read-only recheck returns undefined');
    stage='complete';
  }catch(error){primaryError={stage,type:error.name,message:error.message};}
  finally{try{await f.recheck();}catch(error){protectionError={type:error.name,message:error.message};}}
  const observation={schemaVersion:1,state:primaryError===null&&protectionError===null&&wholeEqual&&apiCalls===1&&recheckCalls===1?'SECRET355_JS_BOOTSTRAP_OBSERVED_UNREVIEWED_V1':'SECRET355_JS_BOOTSTRAP_FAILED_UNACCEPTED_V1',controllerIndex:f.own,rootAuthority:f.cfg.rootAuthority,config:f.configRow,toolingBootstrapConfig:root.toolingBootstrapConfig,apiEntry:refs.bootstrapEntry,apiCalls,returnedRecheckCalls:recheckCalls,wholePublicData:dataRow,retainedPythonFrame:pythonFrameRow,publicReturnShape:shapeRow,callableDescriptor:callableRow,wholeDataEqualsPythonFrame:wholeEqual,sourceAndOriginalProtectionRechecked:protectionError===null,error:primaryError,protectionError,requiresIndependentActualReview:true,engineExecuted:false,guestExecuted:false,keyOperationsInvoked:false,moduleAdmissionGranted:false,operationalAdmission:false,runtimeAcceptanceClaim:false};
  const result=await save(join(out,'js-observation.json'),observation);process.stdout.write(JSON.stringify({observation:result})+'\n');
  if(observation.state!=='SECRET355_JS_BOOTSTRAP_OBSERVED_UNREVIEWED_V1')process.exitCode=1;
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){
  need(process.argv.length===4,'Own config and actual parent owner descriptors');
  await main(JSON.parse(process.argv[2]),JSON.parse(process.argv[3]));
}
