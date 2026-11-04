// New action model only. T3's action enum and ordinary350 admission stay CLOSED.
import {readFile,lstat} from 'node:fs/promises';
import {join,dirname,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,regular,sha} from './authority.mjs';
import {need} from './transport.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export const TOOLING='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8';
export const GUEST='ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8';
export const PUBLICATION='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b';
export const ARMS=Object.freeze(['native-on','fflate-on','fflate-off']);
export const OUTPUT='/private/tmp/starling-node-compat/zlib-cost-jco-correctness-v1';
function proof(value,label){need(value&&typeof value==='object',label+' actual indexed proof required');for(const key of['index','result']){const row=descriptor(value[key]);need(Number.isSafeInteger(row.bytes)&&row.bytes>0&&row.bytes<=32*1024*1024,label+' bounded proof');}}
export function authorityModel(value,sourceSha){
 sha(sourceSha);need(value?.schemaVersion===1&&value.state==='ROOT_REVIEWED_ZLIB_COST_JCO_CORRECTNESS_V1'&&value.action==='untimed-jco-correctness'&&value.actionAllowed===true,'Separate exact Root correctness authority; NULL/unreviewed refuses');
 need(value.correctnessSourceIndexSha256===sourceSha&&value.toolingSourceIndexSha256===TOOLING&&value.guestSourceIndexSha256===GUEST&&value.sourcePublicationIndexSha256===PUBLICATION,'Exact source/guest/publication ancestry');need(value.componentSourceIndexSha256==='e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa','Only corrected WIT source ancestry; actual artifact/ABI proof remains required');
 need(value.outputRoot===OUTPUT&&value.workerTimeoutMs===600000&&value.retainedRotations===3&&value.primaryCases===30&&value.primaryEncoderStreams===45&&value.primaryCrossdecodeEdges===135,'Finite fresh correctness domain');
 need(value.ffOffEncodings===15&&value.ffOffNodeEdges===15&&value.ffOffGuestEdges===45,'Separate actual FF-OFF domain');
 need(value.metadataProjection===false&&value.operationalAdmission===false&&value.nativeInputs===350&&value.sourcePromotionAllowed===false&&value.pilotOrTimingAllowed===false&&value.stockWasmtimeExecutionAllowed===false,'No projection/ordinary admission/timing/Wasmtime authority');
 for(const name of['sourceIndependentReview','sourcePublicationReview','rootReviewedNativePair','rootReviewedNodeOracleRender','actualGeneratedLoadingProtocolReview','freshNodeMatrixDecoderReview'])proof(value[name],name);
 for(const kind of['actualComponentReviews','actualBundleReviews']){need(JSON.stringify(Object.keys(value[kind]??{}).sort())===JSON.stringify([...ARMS].sort()),'Exactly three real per-arm '+kind);for(const arm of ARMS)proof(value[kind][arm],arm+' '+kind);}
 return true;
}
export function implementationReady(slots){
 // Do not fill these from a caller's config. They are reviewed SOURCE slots.
 need(slots?.runtimeActionsEnabled===true&&slots.actualGeneratedLoadingProtocol!==null&&slots.reviewedComponentSourceIndexSha256!==null&&slots.freshNodeMatrixDecoderImplementation!==null,'SOURCE gate closed: real generated loader, ABI and Node matrix decoder are not implemented/reviewed');
 throw new Error('ERR_COST_JCO_CORRECTNESS: this revision has no activated implementation; a new immutable source cut is required');
}
function member(value){need(typeof value==='string'&&!isAbsolute(value)&&!value.includes('\\')&&!value.includes('\0')&&value.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Finite indexed source member');return value;}
async function ownIndex(expected){
 const path=join(HERE,'index.json'),size=(await lstat(path)).size,ix=descriptor({path,sha256:sha(expected),bytes:size});
 const raw=await regular(ix),value=JSON.parse(raw);need(value.schemaVersion===1&&Array.isArray(value.files)&&value.files.length<=128,'Finite own source index');
 const seen=new Set(),rows=[];for(const item of value.files){const name=member(item.path);need(!seen.has(name),'Unique source member');seen.add(name);const row=descriptor({path:join(HERE,name),sha256:item.sha256,bytes:item.bytes});await regular(row,{maxBytes:64*1024*1024});rows.push(row);}
 return{rows,recheck:async()=>{await regular(ix);for(const row of rows)await regular(row,{maxBytes:64*1024*1024});}};
}
export async function correctnessPreflight({correctnessSourceIndexSha256,rootAction}={}){
 need(correctnessSourceIndexSha256&&rootAction,'NULL authority refuses before artifact/tool/output access');
 const captured=descriptor(rootAction),raw=await regular(captured),value=JSON.parse(raw);authorityModel(value,correctnessSourceIndexSha256);
 const source=await ownIndex(correctnessSourceIndexSha256),slotRow=source.rows.find(row=>row.path===join(HERE,'implementation-slots.json'));need(slotRow,'Implementation slots indexed once');
 const slots=JSON.parse(await regular(slotRow));
 implementationReady(slots); // Always refuses in this sealed source revision.
 // No configured helper, generated JS, provider, codec, worker, output or timing
 // can be reached. A successor must replace this gate using real observed glue,
 // authenticate ALL proofs before loaders and capture their primitive rechecks.
 await source.recheck();await regular(captured);throw new Error('Unreachable closed correctness source');
}
