// Read-only HARNESS API. Only Node built-ins are imported; import launches nothing.
import {readFile,lstat,readdir,realpath,mkdir,open} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFile} from 'node:child_process';
import {promisify,isDeepStrictEqual} from 'node:util';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-artifact-tooling-candidate-v3';
const JS_OUT='/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v3-bootstrap-js-normal-off';
const run=promisify(execFile),sha=b=>createHash('sha256').update(b).digest('hex');
const same=isDeepStrictEqual;
function need(v,m){if(!v)throw new Error(m);}
function freeze(v){if(v&&typeof v==='object'){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;}
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

export async function secretArtifactBootstrapPreflight({configDescriptor}={}){
  const cfgRow=captureDescriptor(configDescriptor); // Capture primitives before the first await.
  need(HERE===ORIGINAL,'Only original successor tooling context');
  for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])need(!process.env[k],'No loader override '+k);
  const c=new Capture(),cfg=freeze(await c.read(cfgRow));need(cfg.schemaVersion===3&&cfg.state==='SECRET_OWNER355_ARTIFACT_TOOLING_CONFIG_V3'&&cfg.phase==='bootstrap','Explicit bootstrap config');
  const own=captureDescriptor(cfg.toolingIndex);need(own.path===join(HERE,'index.json'),'Original own index');const rows=await c.family(own);
  const refs=freeze(await c.read(rows.find(r=>r.path===join(HERE,'references.json'))));
  const ownInputs=await c.read(rows.find(r=>r.path===join(HERE,'source-inputs.json')));
  need(ownInputs.schemaVersion===1&&Array.isArray(ownInputs.files)&&ownInputs.files.length>0&&ownInputs.files.length<=4096&&same(ownInputs.protectedInputLedger,refs.protectedInputLedger),'Own complete declared input manifest');
  need(new Set(ownInputs.files.map(r=>r.path)).size===ownInputs.files.length,'Unique declared input rows');
  for(const input of ownInputs.files)await c.file(input);
  need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===refs.node.path,'Pinned plain Node22');await c.file(refs.node);await c.file(refs.python);
  const root=freeze(await c.read(cfg.rootAuthority));need(root.schemaVersion===3&&root.state==='ROOT_REVIEWED_SECRET_OWNER355_ARTIFACT_TOOLING_PHASE_V3'&&root.phase==='bootstrap'&&root.bootstrapAllowed===true&&root.exportAllowed===false&&same(root.toolingIndex,own)&&root.jsOutputRoot===JS_OUT,'New separate bootstrap authority');
  for(const k of ['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'])need(root[k]===false,'No other action '+k);
  for(const ix of refs.families)await c.family(ix);
  const sp=await c.proof(root.sourceIndependentReview);need(sp.schemaVersion===1&&sp.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V3'&&sp.toolingSourceIndexSha256===own.sha256&&sp.sourceOnly===true&&sp.sourceReviewPassed===true&&sp.ownerActionsInvoked===false&&sp.hostActionsInvoked===false&&sp.exportOrBootstrapActionsInvoked===false,'Real successor source review');
  const vp=await c.proof(refs.actualVerifierReview);need(vp.state==='INDEPENDENT_CRYPTO_OWNER355_SECRET_FROZEN_VERIFIER_RESULTS_REVIEW_PASSED_V1'&&vp.verifiedPassed===true&&same(vp.actualWholeFrame,refs.actualVerifierWholeFrame)&&same(vp.inputClosure,refs.protectedInputLedger),'Actual complete verifier proof');
  const ledger=await c.read(refs.protectedInputLedger);need(ledger.files.length===refs.protectedInputRows&&ledger.files.length===27729,'Full original protection ledger');for(const r of ledger.files)await c.file(r);
  for(const key of ['actualExportCandidate','reviewedPins','rootPinReview'])await c.read(root[key]);await c.proof(root.independentExportReview);
  await c.recheck();
  await mkdir(JS_OUT,{mode:0o700});const outIdentity=identity(await lstat(JS_OUT));let result=null,error=null,stdout=Buffer.alloc(0),stderr=Buffer.alloc(0),auditPassed=false;
  try {
    try {
      result=await run(refs.python.path,['-B','-I',join(HERE,'artifact_tooling.py'),'parent','bootstrap','--config-descriptor',JSON.stringify(cfgRow)],{cwd:'/Users/dan/dev/StarlingMonkey',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'},timeout:1200000,maxBuffer:16*1024*1024,encoding:'buffer',killSignal:'SIGTERM'});
      stdout=result.stdout;stderr=result.stderr;
    }catch(e){error=e;stdout=Buffer.isBuffer(e.stdout)?e.stdout:Buffer.alloc(0);stderr=Buffer.isBuffer(e.stderr)?e.stderr:Buffer.alloc(0);}
    // Raw parent JSONL (monitor PID notice plus final observation) is saved before assertions.
    await write(join(JS_OUT,'stdout.log'),stdout);await write(join(JS_OUT,'stderr.log'),stderr);
    const terminal={schemaVersion:3,rawExitCode:error===null?0:(Number.isInteger(error.code)?error.code:null),signal:error?.signal??null,childKillReported:error===null?false:(typeof error.killed==='boolean'?error.killed:null),timedOut:error===null?false:null,timeoutCauseEstablished:false,rawStreamsComplete:error===null,exceptionCode:error===null?null:(typeof error.code==='string'?error.code:null),enclosingRootControllerRequiredForIndependentCleanupReview:true};
    await write(join(JS_OUT,'terminal.json'),Buffer.from(JSON.stringify(terminal,null,2)+'\n'));
    need(error===null&&stderr.length===0,'Raw-zero Python parent required; failed captures remain unaccepted');
    const lines=stdout.toString('utf8').split('\n').filter(Boolean).map(x=>JSON.parse(x));need(lines.length===2&&Number.isSafeInteger(lines[0].pid)&&lines[0].timeoutSeconds===600&&lines[1].completeUnreviewed===true,'Exact original monitor notice plus observation; never relabel prefixes');
    const observation=await c.read(lines[1].observation);need(observation.state==='SECRET_OWNER355_ARTIFACT_PHASE_COMPLETE_UNREVIEWED_V3'&&observation.phase==='bootstrap'&&observation.sourceAndOriginalProtectionRechecked===true&&observation.errors.length===0&&same(observation.toolingIndex,own),'Actual parent collection');
    const rawTerminal=await c.read(observation.rawTerminal);need(rawTerminal.rawExitCode===0&&rawTerminal.timeout===false&&rawTerminal.forcedCleanup===false&&rawTerminal.allObservedOwnedGroupsGone===true&&rawTerminal.parentOwnedGroupGone===true&&rawTerminal.errors.length===0&&rawTerminal.signals.length===0&&rawTerminal.interruptedSignals.length===0&&rawTerminal.remainingObservedPids.length===0&&same(rawTerminal.authority,cfg.rootAuthority)&&rawTerminal.finalGroups.length>0&&rawTerminal.finalGroups.every(g=>g.alive===false),'Owned worker clean-zero');
    await c.file(rawTerminal.stderr);need(rawTerminal.stderr.bytes===0&&rawTerminal.stdout.bytes<=16*1024*1024,'Full bounded worker streams');
    const value=freeze(await c.read(observation.completePhaseReturn)),raw=await c.read(rawTerminal.stdout);need(same(value,raw),'Whole actual worker stdout and saved bootstrap JSON');
    need(value.schemaVersion===3&&value.state==='SECRET_OWNER355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V3'&&value.variant==='normal-off'&&value.nativeSourceFiles===355&&value.externalEmbeddingSources===3&&value.selectedManifestCount===11&&same(value.toolingIndex,own)&&same(value.rootAuthority,cfg.rootAuthority)&&same(value.config,cfgRow),'Genuine new bootstrap frame');
    need(value.engineExecuted===false&&value.guestExecuted===false&&value.operationalAdmission===false&&value.runtimeAcceptanceClaim===false&&value.validationBootstrapOnly===true,'No engine/runtime authority');
    need(same(value.verifierFrame,await c.read(refs.actualVerifierWholeFrame))&&same(value.pin.verifierFrame,value.verifierFrame),'Whole original verifier metadata and all manifests unchanged');
    await c.recheck();auditPassed=true;
    const recheck=async()=>{await c.recheck();need(same(value,await c.read(observation.completePhaseReturn)),'Actual retained frame unchanged');};
    return Object.freeze({...value,recheck});
  } finally {
    let failure=null;try{await c.recheck();auditPassed=true;}catch(e){failure=e;auditPassed=false;}
    const s=await lstat(JS_OUT);need(s.isDirectory()&&!s.isSymbolicLink()&&same(identity(s).slice(0,2),outIdentity.slice(0,2)),'Fresh JS output directory identity');
    await write(join(JS_OUT,'post-audit.json'),Buffer.from(JSON.stringify({schemaVersion:3,sourceAndProofProtectionRechecked:auditPassed,engineExecuted:false,operationalAdmission:false})+'\n'));
    if(failure!==null)throw failure;
  }
}
