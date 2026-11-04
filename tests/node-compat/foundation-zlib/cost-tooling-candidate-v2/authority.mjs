// Future source only. No package/codec/preflight or Root authority is loaded here.
import {readFile,lstat,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {isAbsolute,resolve,dirname,join,sep} from 'node:path';
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export const IMPLEMENTED_ACTIONS=Object.freeze(['source-publication','node-oracle','bundle-source']);
export function need(value,message){if(!value)throw new Error(message);}
export function sha(value){need(typeof value==='string'&&/^[0-9a-f]{64}$/.test(value),'ExactSHA256 required');return value;}
export function canonical(path){need(typeof path==='string'&&isAbsolute(path)&&resolve(path)===path&&!path.includes('\0')&&!path.includes('\\'),'Canonical absolute path required');return path;}
export function descriptor(row){need(row&&typeof row==='object','Explicit descriptor required');return Object.freeze({path:canonical(row.path),sha256:sha(row.sha256),bytes:row.bytes});}
export async function regular(row,{maxBytes=32*1024*1024}={}){
 row=descriptor(row); // capture primitives synchronously before the first await
 canonical(row.path);sha(row.sha256);need(Number.isSafeInteger(row.bytes)&&row.bytes>=0&&row.bytes<=maxBytes,'Bounded exact file bytes required');
 const canonicalParent=await realpath(dirname(row.path));
 // Known /tmp system aliases are permitted only in the declared parent;
 // evidence leaf and every canonical ancestor must be ordinary paths.
 const declaredParent=dirname(row.path).replace(/^\/tmp(?=\/|$)/,'/private/tmp');
 need(canonicalParent===declaredParent,'Only declared canonical paths or the system /tmp alias are permitted');
 const pieces=canonicalParent.split(sep).filter(Boolean);let cursor=sep;
 for(const part of pieces){cursor=join(cursor,part);const info=await lstat(cursor);need(info.isDirectory()&&!info.isSymbolicLink(),'Ordinary canonical source ancestor required');}
 const info=await lstat(row.path);need(info.isFile()&&!info.isSymbolicLink()&&info.size===row.bytes,'Regular expected-size file required');
 const raw=await readFile(row.path),after=await lstat(row.path);
 need(info.dev===after.dev&&info.ino===after.ino&&info.size===after.size&&info.mtimeMs===after.mtimeMs&&info.ctimeMs===after.ctimeMs,'File changed during source read');
 need(raw.length===row.bytes&&hash(raw)===row.sha256,'File digest mismatch');return raw;
}
export function authorityModel(value,{action,arm=null,candidateIndexSha256,publicationIndexSha256=null}={}){
 need(value&&typeof value==='object'&&!Array.isArray(value),'Explicit new Root action authority required');
 need(value.schemaVersion===1&&value.state==='ROOT_REVIEWED_FRESH_ZLIB350_COST_ACTION_V1','New finite Root authority required');
 sha(candidateIndexSha256);need(value.toolingCandidateIndexSha256===candidateIndexSha256,'Exact tooling source index required');
 need(['source-publication','node-oracle','bundle-source','component-build','guest-correctness','pilot','timing'].includes(action),'Unknown action refuses');
 need(IMPLEMENTED_ACTIONS.includes(action),'Unimplemented component/correctness/pilot/timing actions remain CLOSED in this source revision');
 need(value.action===action&&value.actionAllowed===true&&value.operationalAdmission===false,'Permission is action-specific and diagnostic-only');
 need(value.nativeInputs===350&&value.metadataProjection===false&&value.sourcePromotionAllowed===false,'Genuine350 only; no projection/promotion');
 if(action!=='source-publication'){
  sha(publicationIndexSha256);need(value.publicationIndexSha256===publicationIndexSha256,'Exact fresh publication proof required');
  need(Array.isArray(value.permittedArms)&&value.permittedArms.length>0&&new Set(value.permittedArms).size===value.permittedArms.length&&value.permittedArms.every(v=>['native-on','fflate-on','fflate-off'].includes(v))&&value.permittedArms.includes(arm),'Root action binds finite permitted arm(s)');
 }
 need(value.rootReviewedPair&&typeof value.rootReviewedPair==='object','New separately reviewed cost-pair proof required');
 for(const key of['index','result']){const row=value.rootReviewedPair[key];need(row&&typeof row==='object','Pair proof descriptor required');canonical(row.path);sha(row.sha256);need(Number.isSafeInteger(row.bytes)&&row.bytes>0&&row.bytes<=32*1024*1024,'Finite pair proof descriptor');}
 return Object.freeze({action,candidateIndexSha256,publicationIndexSha256});
}
export async function actionAuthority(descriptor,options){
 const captured=Object.freeze({path:canonical(descriptor.path),sha256:sha(descriptor.sha256),bytes:descriptor.bytes});
 const fixedOptions=Object.freeze({...options});
 const raw=await regular(captured),value=JSON.parse(raw);const checked=authorityModel(value,fixedOptions);
 // Descriptor values are captured privately; callers cannot redirect recheck.
 function freezeJSON(item){if(item&&typeof item==='object'){for(const child of Object.values(item))freezeJSON(child);Object.freeze(item);}return item;}
 return Object.freeze({authority:freezeJSON(structuredClone(value)),descriptor:captured,checked,recheck:async()=>{await regular(captured);return true;}});
}
export async function reviewedPair(authority){
 const proof=authority.authority.rootReviewedPair;
 const index=JSON.parse(await regular(proof.index,{maxBytes:1024*1024}));
 need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=256,'Finite Root pair proof index');
 let result=null,found=0;const rows=[],seen=new Set();
 for(const entry of index.files){
  need(typeof entry.path==='string'&&entry.path&&!entry.path.includes('\\')&&!entry.path.includes('\0')&&!isAbsolute(entry.path)&&entry.path.split('/').every(p=>p&&p!=='.'&&p!=='..')&&!seen.has(entry.path),'Finite indexed proof name');seen.add(entry.path);
  const row={path:join(dirname(proof.index.path),entry.path),sha256:entry.sha256,bytes:entry.bytes};
  const raw=await regular(row);need(!raw.includes(0),'Root proof text only');rows.push(Object.freeze({...row}));
  if(row.path===proof.result.path){need(row.sha256===proof.result.sha256&&row.bytes===proof.result.bytes,'Exact indexed pair result');result=JSON.parse(raw);found++;}
 }
 need(found===1,'Root pair result indexed exactly once');
 need(result.schemaVersion===1&&result.state==='ROOT_REVIEWED_GENUINE_ZLIB350_COST_PAIR_V1','New cost pair review, not old validation-bootstrap authority');
 need(result.nativeInputs===350&&result.recipeSha256==='4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2'&&result.operationalAdmission===false&&result.sourcePromotionAllowed===false,'Genuine350 diagnostic pair only');
 need(result.nativeOn?.engine?.sha256==='fb16568958f4948cb78aa53818637535b88a0d87a25eb74923798fdc80cac1e6'&&result.nativeOff?.engine?.sha256==='3d19535f0bbe910066b6c00aea2cdd9bbee933705429d28f3e23714c93bc2a44','Only reviewed finite350 engine facts are eligible');
 // Returned records are independent copies; final recheck captures primitives.
 const capturedIndex=Object.freeze({...proof.index});
 return Object.freeze({data:structuredClone(result),recheck:async()=>{await authority.recheck();await regular(capturedIndex);for(const row of rows)await regular(row);}});
}
export async function publicationProof(authority,indexSha,identity){
 const proof=authority.authority.sourcePublicationProof;need(proof?.index&&proof?.result,'Independent actual source-publication proof required');
 const index=JSON.parse(await regular(proof.index,{maxBytes:1024*1024}));need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length<=256,'Finite source publication proof');
 let found=0,result=null;const captured=[];const names=new Set();
 for(const entry of index.files){
  need(typeof entry.path==='string'&&!isAbsolute(entry.path)&&entry.path.split('/').every(v=>v&&v!=='.'&&v!=='..')&&!entry.path.includes('\\')&&!entry.path.includes('\0')&&!names.has(entry.path),'Finite publication-proof name');names.add(entry.path);
  const row=Object.freeze({path:join(dirname(proof.index.path),entry.path),sha256:entry.sha256,bytes:entry.bytes});const raw=await regular(row,{maxBytes:64*1024*1024});captured.push(row);
  if(row.path===proof.result.path){need(row.sha256===proof.result.sha256&&row.bytes===proof.result.bytes,'Exact indexed publication result');result=JSON.parse(raw);found++;}
 }
 need(found===1&&result.schemaVersion===1&&result.state==='INDEPENDENT_FRESH_ZLIB_COST_SOURCE_PUBLICATION_VERIFIED','Actual publication review state');
 need(result.publicationIndexSha256===indexSha&&result.toolingSourceIndexSha256===authority.checked.candidateIndexSha256&&result.externalPublisherExitCode===0&&result.verifiedPassed===true,'Completed actual source publication bound');
 need(result.rootIdentity?.device===identity.device&&result.rootIdentity?.inode===identity.inode&&result.libraryCodecOrRuntimeActionExecuted===false&&result.operationalAdmission===false,'Source-only actual scope/identity');
 const ix=Object.freeze({...proof.index});return Object.freeze({recheck:async()=>{await authority.recheck();await regular(ix,{maxBytes:1024*1024});for(const row of captured)await regular(row,{maxBytes:64*1024*1024});}});
}
