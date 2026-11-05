// Distinct retained-bootstrap HARNESS API; import launches nothing.
// Read/hash only: no process launcher, old API import, helper or file writer.
import {readFile,lstat,readdir,realpath} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-retained-bootstrap-candidate-v1';
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
// Appended to exact original d62 read/hash primitives. No action primitive.
function deepFreeze(value){if(value&&typeof value==='object'){for(const x of Object.values(value))deepFreeze(x);Object.freeze(value);}return value;}
export function validateHistorical(frame,pins,metadata,manifests,refs){
  need(frame&&Object.keys(frame).length===41&&frame.schemaVersion===3&&frame.state==='SECRET_OWNER355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V3'&&frame.variant==='normal-off','Exact historical full-frame kind');
  need(pins.schemaVersion===3&&pins.state==='ROOT_REVIEWED_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PINS_V3'&&pins.reviewRequired===false,'Actual reviewed validation pin DATA');
  need(same(Object.keys(pins.variants).sort(),['disabled-off','gc-off','normal-off','normal-runtime'])&&['normal-runtime','gc-off','disabled-off'].every(k=>pins.variants[k]===null),'Normal-OFF only; other three NULL');
  need(same(frame.pin,pins.variants['normal-off'])&&same(frame.metadata,metadata)&&same(frame.selectedManifests,manifests),'Whole original pin/metadata/manifests, no projection');
  need(Object.keys(metadata).length===75&&metadata.sourceManifest.length===355&&metadata.componentizeSourceManifest.length===3&&manifests.length===11&&frame.selectedManifestCount===11,'Actual355+3/75/11');
  need(frame.nativeSourceFiles===355&&frame.externalEmbeddingSources===3&&frame.validationBootstrapOnly===true&&frame.currentCompleteVerifierCalls===1,'Historical one-shot count remains historical');
  need(same(frame.engine,refs.engine)&&same(frame.metadataDescriptor,refs.metadata)&&same(frame.freezeReceipt,refs.freezeReceipt),'Actual frozen descriptors');
  need(same(frame.toolingIndex,refs.toolingIndex)&&same(frame.reviewedPins,refs.reviewedPins)&&same(frame.rootPinReview,refs.rootPinReview),'Historical tooling/pin roles');
  for(const [key,value]of Object.entries(refs.historicalContexts))need(frame[key]===value,'Unchanged historical physical context '+key);
  need(same(frame.verifierFrame.runtimeBackendProof,{verified:false,version:null,vernum:null}),'No new backend runtime proof');
  for(const key of ['engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','grantsRuntimeAuthority'])need(frame[key]===false,'Historical scope '+key);
  need(metadata.gcStress===false&&metadata.entropyPolicy==='off'&&metadata.oomTesting===false,'Normal-OFF only, no GC/entropy/OOM projection');
}
export function makeRetainedRecord({sourceIndex,actualReview,historicalBootstrap,currentVerification,recheck}){
  need(typeof recheck==='function','Fresh own read-only callable');
  return Object.freeze({schemaVersion:1,kind:'retained-secret355-bootstrap-v1',sourceIndex:deepFreeze(sourceIndex),actualReview:deepFreeze(actualReview),historicalBootstrap:deepFreeze(historicalBootstrap),currentVerification:deepFreeze(currentVerification),recheck});
}
async function inspectTree(c,tree){
  const names=new Set(tree.names);need(names.size===tree.names.length,'Unique retained membership');await c.tree(tree.root,names);
  if(tree.private){
    async function walk(path){const s=await lstat(path);need(!s.isSymbolicLink(),'No private links');if(s.isDirectory()){need((s.mode&0o7777)===0o700,'Private directory mode');for(const n of await readdir(path))await walk(join(path,n));}else need(s.isFile()&&s.nlink===1&&(s.mode&0o7777)===0o600,'Private regular independent file');}
    await walk(tree.root);
  }
}
export async function retainedSecretBootstrapPreflight({configDescriptor}={}){
  // Capture exact caller primitives synchronously; no caller-owned descriptor is
  // consulted again after an await. No original bootstrap or helper is imported.
  const cfgRow=captureDescriptor(configDescriptor);
  need(HERE===ORIGINAL&&process.version==='v22.14.0'&&process.execArgv.length===0,'Original new harness context and plain pinned Node22');
  for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])need(!process.env[k],'No inherited loader override '+k);
  const c=new Capture();let primary=null,contextsVerified=false,refs=null;
  async function contextCheck(){
    if(!contextsVerified)return;
    for(const t of refs.retainedTrees)await inspectTree(c,t);
    for(const pair of refs.independentFrozenCopies){const a=await lstat(pair.frozen),b=await lstat(pair.original);need(a.isFile()&&!a.isSymbolicLink()&&b.isFile()&&!b.isSymbolicLink()&&a.nlink===1&&(a.dev!==b.dev||a.ino!==b.ino),'Current independent frozen/original identities');}
  }
  async function verifyCurrent(){await c.recheck();await contextCheck();}
  try{
    const cfg=deepFreeze(await c.read(cfgRow));need(cfg.schemaVersion===1&&cfg.state==='SECRET355_RETAINED_BOOTSTRAP_CONFIG_V1','New retained preflight config');
    const own=captureDescriptor(cfg.sourceIndex);need(own.path===join(HERE,'index.json'),'Actual new Source index');const ownRows=await c.family(own);
    refs=deepFreeze(await c.read(ownRows.find(r=>r.path===join(HERE,'references.json'))));
    const inputs=await c.read(ownRows.find(r=>r.path===join(HERE,'source-inputs.json')));
    need(inputs.schemaVersion===1&&Array.isArray(inputs.files)&&inputs.files.length>=28000&&inputs.files.length<=40000,'Full finite input protection');
    need(new Set(inputs.files.map(r=>r.path)).size===inputs.files.length,'Unique source/protection inputs');
    for(const r of inputs.files)await c.file(r);for(const ix of inputs.families)await c.family(ix);
    need(await realpath(process.execPath)===refs.node.path,'Actual pinned Node executable');await c.file(refs.node);
    const root=deepFreeze(await c.read(cfg.rootAuthority));
    need(root.schemaVersion===1&&root.state==='ROOT_REVIEWED_SECRET355_RETAINED_BOOTSTRAP_PREFLIGHT_V1'&&root.phase==='verify-retained'&&root.readOnlyVerificationAllowed===true&&same(root.sourceIndex,own),'New explicit read-only authority');
    need(same(root.actualBootstrapReview,refs.actualBootstrapReview)&&same(root.historicalBootstrap,refs.historicalBootstrap)&&root.variant==='normal-off','Exact historical proof/variant');
    for(const k of ['helperInvocationAllowed','oneShotApiInvocationAllowed','historicalRecheckInvocationAllowed','exportAllowed','pinDerivationAllowed','nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOrCryptoAllowed','moduleAdmissionAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'])need(root[k]===false,'No additional action '+k);
    need(root.actualComponent===null&&root.runtimeAuthority===null,'No component/runtime adoption');
    const sourcePeer=await c.proof(root.sourceIndependentReview);
    need(sourcePeer.schemaVersion===1&&sourcePeer.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_RETAINED_BOOTSTRAP_SOURCE_REVIEW_PASSED_V1'&&sourcePeer.sourceIndexSha256===own.sha256&&sourcePeer.sourceOnly===true&&sourcePeer.sourceReviewPassed===true,'New genuine Source peer');
    for(const k of ['ownerActionsInvoked','hostActionsInvoked','retainedPreflightActionsInvoked'])need(sourcePeer[k]===false,'Source peer scope '+k);
    const proof=await c.proof(refs.actualBootstrapReview),contract=await c.read(refs.actualBootstrapContract);
    need(contract.schemaVersion===3&&contract.requiredResultSchemaVersion===3&&proof.schemaVersion===3&&proof.state===contract.requiredReviewState&&proof.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_BOOTSTRAP_RESULTS_REVIEW_PASSED_V3','Real completed8298 bootstrap review');
    for(const group of ['requiredFixedValues','requiredExactDescriptors','requiredPairs'])for(const[k,v]of Object.entries(contract[group]))need(same(proof[k],v),'Whole actual review field '+k);
    need(same(proof.coverage,contract.requiredCoverage)&&same(proof.wholePublicData,refs.historicalBootstrap)&&same(proof.retainedPythonFrame,refs.historicalPythonFrame),'Actual full historical tuple');
    const historical=await c.read(refs.historicalBootstrap),pythonFrame=await c.read(refs.historicalPythonFrame);
    need(same(historical,pythonFrame),'Complete historical public/Python DATA unchanged');
    const pins=await c.read(refs.reviewedPins),metadata=await c.read(refs.metadata),manifests=[];
    for(const r of refs.selectedManifests)manifests.push(await c.read(r));
    validateHistorical(historical,pins,metadata,manifests,refs);
    const pinReview=await c.read(refs.rootPinReview);
    need(pinReview.schemaVersion===3&&pinReview.state==='ROOT_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V3'&&same(pinReview.reviewedPins,refs.reviewedPins)&&same(pinReview.actualExportCandidate,refs.exportCandidate)&&same(pinReview.engine,refs.engine)&&same(pinReview.metadata,refs.metadata),'Pinned original Root pin-review DATA');
    contextsVerified=true;await contextCheck();await verifyCurrent();
    // This record intentionally does not spread, relabel or decorate the old
    // bootstrap frame. Its historical call-count field remains inside DATA.
    const currentVerification={schemaVersion:1,kind:'current-read-hash-verification-v1',sourceIndex:own,config:cfgRow,rootAuthority:captureDescriptor(cfg.rootAuthority),protectedFileRows:c.rows.size,retainedTreeScopes:refs.retainedTrees.length,helperScope:'original frozen-verifier/artifact helper',helperInvocations:0,originalApiInvocations:0,historicalRecheckInvocations:0,processesSpawned:0,filesCreated:0,sourceAndProtectionChecked:true,fullMetadataFields:75,selectedWholeManifests:11,engineExecuted:false,componentOrGuestExecuted:false,keyOrApplicationCryptoOperationsInvoked:false,operationalAdmission:false,runtimeAcceptanceClaim:false};
    const recheck=async()=>{await verifyCurrent();need(same(historical,await c.read(refs.historicalBootstrap)),'Historical full DATA unchanged');};
    return makeRetainedRecord({sourceIndex:own,actualReview:refs.actualBootstrapReview,historicalBootstrap:historical,currentVerification,recheck});
  }catch(error){primary=error;throw error;}
  finally{
    try{await verifyCurrent();}
    catch(error){if(primary!==null)throw new AggregateError([primary,error],'Retained preflight and final protection failed');throw error;}
  }
}
