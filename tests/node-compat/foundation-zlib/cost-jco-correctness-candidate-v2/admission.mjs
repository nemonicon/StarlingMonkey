// Dedicated untimed correctness action. No T3 action state is forged/projected.
import {dirname,join} from 'node:path';
import {lstat} from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {descriptor,regular,sha} from './authority.mjs';
import {indexed,deepFreeze,local} from './proofs.mjs';
import {need} from './transport.mjs';
import {PARSER} from './parser-tuple.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export const TOOLING='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8',GUEST='ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8',PUBLICATION='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b';
export const COMPONENT='cf3110b3af503fecd2408781a4dcb53b21670b74cd94e3266c4f0b86f795d794';
export const ARMS=Object.freeze(['native-on','fflate-on','fflate-off']),OUTPUT='/private/tmp/starling-node-compat/zlib-cost-jco-correctness-v2';
export const NODE=Object.freeze({path:'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes:108619024});
const PARENTS=Object.freeze({
 'cost-component-glue-amendment-v1':COMPONENT,
 'cost-component-wit-amendment-v1':'e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa',
 'cost-component-candidate-v1':'a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9',
 'cost-tooling-candidate-v3':TOOLING,'cost-guest-oracle-candidate-v2':GUEST,
 'cost-jco-correctness-candidate-v1':'610295513e79ffa3a926c466f2b07a05d465694e8ee7de706f3966052f8f305a'});
function proof(value){need(value?.index&&value?.result,'Actual indexed proof required');for(const name of['index','result']){const r=descriptor(value[name]);need(Number.isSafeInteger(r.bytes)&&r.bytes>0,'Actual bounded proof bytes');}}
export function authorityModel(v,sourceSha){
 sha(sourceSha);need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_ZLIB_COST_JCO_CORRECTNESS_V2'&&v.action==='untimed-jco-correctness'&&v.actionAllowed===true,'Dedicated actual Root correctness authority; NULL/unreviewed refuses');
 need(v.correctnessSourceIndexSha256===sourceSha&&v.componentSourceIndexSha256===COMPONENT&&v.toolingSourceIndexSha256===TOOLING&&v.guestSourceIndexSha256===GUEST&&v.sourcePublicationIndexSha256===PUBLICATION,'Exact current source/component/native publication ancestry');
 need(v.outputRoot===OUTPUT&&v.workerTimeoutMs===600000&&v.retainedRotations===3&&v.primaryCases===30&&v.primaryEncoderStreams===45&&v.primaryCrossdecodeEdges===135&&v.ffOffEncodings===15&&v.ffOffNodeEdges===15&&v.ffOffGuestEdges===45,'Exact finite untimed scope');
 need(v.nativeInputs===350&&v.metadataProjection===false&&v.operationalAdmission===false&&v.sourcePromotionAllowed===false&&v.pilotOrTimingAllowed===false&&v.stockWasmtimeExecutionAllowed===false&&v.nodeMatrixCodecCallsAllowed===true&&v.ordinaryGuestCallsAllowed===true,'No admission/promotion/WT/timing extension; actual untimed Node/Jco calls need explicit authority');
 proof(v.sourceIndependentReview);descriptor(v.oracle);
 for(const kind of['componentBuildAuthorities','actualComponentReviews']){need(JSON.stringify(Object.keys(v[kind]??{}).sort())===JSON.stringify([...ARMS].sort()),'Exactlythree actual per-arm '+kind);for(const arm of ARMS){if(kind==='actualComponentReviews')proof(v[kind][arm]);else descriptor(v[kind][arm]);}}
 return true;
}
async function sourceIndex(root,expected){const path=join(root,'index.json');const raw=await lstat(path);const ix=descriptor({path,sha256:expected,bytes:raw.size}),value=JSON.parse(await regular(ix));need(value.schemaVersion===1&&Array.isArray(value.files)&&value.files.length<=1024,'Finite immutable source index');const rows=[],seen=new Set();
 for(const item of value.files){local(item.path);need(!seen.has(item.path),'Unique source row');seen.add(item.path);const r=descriptor({path:join(root,item.path),sha256:item.sha256,bytes:item.bytes});await regular(r,{maxBytes:64*1024*1024});rows.push(r);}
 return Object.freeze({rows:Object.freeze(rows),recheck:async()=>{await regular(ix);for(const r of rows)await regular(r,{maxBytes:64*1024*1024});}});
}
export function artifactModel(r,arm){
 need(r?.schemaVersion===1&&r.state==='INDEPENDENT_ZLIB_COST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'&&r.verifiedPassed===true&&r.arm===arm,'Actual independent construction-artifact review, not source review or failed partial');
 need(r.componentSourceIndexSha256===COMPONENT&&r.toolingSourceIndexSha256===TOOLING&&r.guestSourceIndexSha256===GUEST&&r.sourcePublicationIndexSha256===PUBLICATION,'Actual component source identities');
 need(r.externalParentExitCode===0&&r.rawWorkerExitCode===0&&r.ownedGroupGone===true&&r.generatedModuleImported===false&&r.ordinaryGuestExportsInvoked===false&&r.operationalAdmission===false&&r.timingAllowed===false,'Actual clean construction/cleanup only; ordinary calls are new authority');
 need(r.generatedJsGluePolicy==='JCO7_SCALAR_FUNCTIONS_PLUS_EXACT_EMPTY_UTIL_V1'&&Array.isArray(r.emittedImports)&&r.emittedImports.length===0,'Exact scalar/helper/import policy');
 const abi={identity:'() -> string',setup:'(u32) -> string',observe:'(u32) -> string',batch:'(u32,u32) -> string',checkpoint:'() -> string',stage:'(string) -> string',validate:'(string) -> string'};need(r.emittedAbi&&JSON.stringify(Object.keys(r.emittedAbi).sort())===JSON.stringify(Object.keys(abi).sort())&&Object.entries(abi).every(([name,type])=>r.emittedAbi[name]===type),'Exact actual independently reviewed seven scalar ABI');
 for(const name of['component','glue','core','dts','wit','transpileMetadata','packageJson','code','nativeEngine','metadata','actualBuildAuthority','externalParentTerminal','ownedWorkerTerminal','workerIndex','workerCompletion','parentResult','workerResult'])descriptor(r[name]);
 const root='/private/tmp/starling-node-compat/zlib-cost-component-v3-'+arm+'/worker';
 for(const[name,path]of Object.entries({component:'codec-cost.component.wasm',glue:'transpiled/codec_cost.js',core:'transpiled/codec_cost.core.wasm',dts:'transpiled/codec_cost.d.ts',wit:'emitted.wit',transpileMetadata:'transpile-metadata.json',packageJson:'transpiled/package.json',workerIndex:'index.json',workerCompletion:'completion.json',workerResult:'results.json'}))need(r[name].path===join(root,path),'Only actual successful v3 artifact namespace '+name);
 return true;
}
const same=(a,b)=>a.path.replace(/^\/tmp(?=\/|$)/,'/private/tmp')===b.path.replace(/^\/tmp(?=\/|$)/,'/private/tmp')&&a.sha256===b.sha256&&a.bytes===b.bytes;
export async function correctnessPreflight({correctnessSourceIndexSha256,rootAction}={}){
 need(correctnessSourceIndexSha256&&rootAction,'NULL correctness authority refuses before source/artifact/output access');const expectedSourceSha=sha(correctnessSourceIndexSha256),rootRow=descriptor(rootAction),rootBytes=await regular(rootRow),v=deepFreeze(JSON.parse(rootBytes));authorityModel(v,expectedSourceSha);
 const own=await sourceIndex(HERE,expectedSourceSha),parents=[];for(const[name,digest]of Object.entries(PARENTS))parents.push(await sourceIndex(join(HERE,'..',name),digest));
 const peer=await indexed(v.sourceIndependentReview,{state:'INDEPENDENT_ZLIB_COST_JCO_CORRECTNESS_SOURCE_REVIEW_PASSED_V2'});need(peer.data.correctnessSourceIndexSha256===expectedSourceSha&&peer.data.sourceOnly===true&&peer.data.sourceReviewPassed===true&&peer.data.ownerActionsInvoked===false,'Own exact independent source review');
 const {componentPreflight}=await import('../cost-component-glue-amendment-v1/guard.mjs');const {checkOwnedTerminal,parsePublicWit,parsePublicDts,checkTranspileMetadata}=await import('./glue-policy.mjs');
 const frames={},reviews=[];
 for(const arm of ARMS){
  const authorityRow=descriptor(v.componentBuildAuthorities[arm]),buildAuthority=JSON.parse(await regular(authorityRow));
  // Reuse the GENUINE prior component-build authority unchanged for its read-only
  // admission API. Do not change/strip it into a T3 or correctness action state.
  const frame=await componentPreflight({componentSourceIndexSha256:COMPONENT,arm,rootAction:authorityRow});
  const proof=await indexed(v.actualComponentReviews[arm],{state:'INDEPENDENT_ZLIB_COST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'}),r=proof.data;artifactModel(r,arm);need(same(r.actualBuildAuthority,authorityRow),'Actual construction authority crossbinding');
  need(same(r.code,frame.codeRow)&&same(r.nativeEngine,{path:frame.enginePath,sha256:frame.pin.engineSha256,bytes:frame.pin.engineBytes})&&r.metadata.path.replace(/^\/tmp(?=\/|$)/,'/private/tmp')===(frame.enginePath+'.build.json').replace(/^\/tmp(?=\/|$)/,'/private/tmp')&&r.metadata.sha256===frame.pin.metadataSha256&&r.oracleSha256===v.oracle.sha256,'Actual code/native/oracle tuple equals genuine admission');
  need(same(v.oracle,buildAuthority.nodeOracleRenderProof.oracle),'Every arm uses the same real reviewed oracle/render');
  const evidenceRows=Object.freeze(['component','glue','core','dts','wit','transpileMetadata','packageJson','code','nativeEngine','metadata','externalParentTerminal','ownedWorkerTerminal','workerIndex','workerCompletion','parentResult','workerResult'].map(name=>descriptor(r[name])));for(const row of evidenceRows)await regular(row,{maxBytes:64*1024*1024});
  const parent=JSON.parse(await regular(r.externalParentTerminal)),owned=JSON.parse(await regular(r.ownedWorkerTerminal));need(parent.rawExitCode===0,'Actual external parent raw0');checkOwnedTerminal(owned);
  const worker=JSON.parse(await regular(r.workerResult)),parentResult=JSON.parse(await regular(r.parentResult));need(worker.state==='ZLIB_COST_COMPONENT_BUILT_UNREVIEWED_V1'&&parentResult.state==='ZLIB_COST_COMPONENT_BUILD_COMPLETE_UNREVIEWED_V1'&&worker.arm===arm&&parentResult.arm===arm,'Preserved genuine unreviewed construction records; independent review is separate');
  need(parentResult.sourceIndexSha256===COMPONENT&&parentResult.rawWorkerExitCode===0&&parentResult.ownedGroupGone===true&&parentResult.ordinaryGuestExportsInvoked===false,'Actual parent source/terminal/call scope');
  need(same(parentResult.rootAction,authorityRow)&&same(parentResult.workerCompletion,r.workerCompletion)&&same(worker.nativeEngine,r.nativeEngine)&&same(worker.metadata,r.metadata)&&same(worker.source,r.code)&&worker.component.sha256===r.component.sha256&&worker.component.bytes===r.component.bytes&&worker.generatedModuleImported===false&&worker.ordinaryGuestExportsInvoked===false,'Actual raw construction tuples and unexecuted namespace scope match review');
  const windex=JSON.parse(await regular(r.workerIndex)),complete=JSON.parse(await regular(r.workerCompletion));need(complete.state==='COMPONENT_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED'&&complete.index.sha256===r.workerIndex.sha256&&complete.index.bytes===r.workerIndex.bytes&&complete.result.sha256===r.workerResult.sha256&&complete.result.bytes===r.workerResult.bytes&&complete.component.sha256===r.component.sha256&&complete.component.bytes===r.component.bytes,'Actual worker completion/index/result/component binding');const artifacts=[],names=new Set();need(windex.schemaVersion===1&&Array.isArray(windex.files)&&windex.files.length>0&&windex.files.length<=256,'Finite actual worker index');
  for(const row of windex.files){local(row.path);need(!names.has(row.path),'Unique actual worker inventory row');names.add(row.path);const rr=descriptor({path:join(dirname(r.workerIndex.path),row.path),sha256:row.sha256,bytes:row.bytes});await regular(rr,{maxBytes:64*1024*1024});artifacts.push(rr);}
  for(const name of['component','glue','core','dts','wit','transpileMetadata','packageJson','workerResult'])need(artifacts.filter(row=>same(row,r[name])).length===1,'Each actual critical artifact worker-indexed exactly once');
  parsePublicWit(new TextDecoder('utf-8',{fatal:true}).decode(await regular(r.wit)));parsePublicDts(new TextDecoder('utf-8',{fatal:true}).decode(await regular(r.dts)));checkTranspileMetadata(JSON.parse(await regular(r.transpileMetadata)));
  const artifact=deepFreeze({parentAuditedActualComponent:true,...Object.fromEntries(['component','glue','core','dts','wit','transpileMetadata','packageJson'].map(name=>[name,descriptor(r[name])]))});frames[arm]=Object.freeze({frame,artifact,proofResult:r,authority:authorityRow});reviews.push({proof,artifacts,authorityRow,evidenceRows});
 }
 await regular(descriptor(v.oracle));await regular(PARSER);const recheck=async()=>{await regular(rootRow);await own.recheck();for(const p of parents)await p.recheck();await peer.recheck();for(const arm of ARMS)await frames[arm].frame.recheck();for(const r of reviews){await r.proof.recheck();await regular(r.authorityRow);for(const row of r.evidenceRows)await regular(row,{maxBytes:64*1024*1024});for(const row of r.artifacts)await regular(row,{maxBytes:64*1024*1024});}await regular(descriptor(v.oracle));await regular(PARSER);};await recheck();
 return Object.freeze({rootAction:rootRow,sourceSha:expectedSourceSha,frames:Object.freeze(frames),oracle:descriptor(v.oracle),outputRoot:OUTPUT,workerTimeoutMs:600000,criticalSourceFiles:Object.freeze([...own.rows,...parents.flatMap(p=>p.rows)]),recheck});
}
