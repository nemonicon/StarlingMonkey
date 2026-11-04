// Pure compact typed-return model. No provider, codec, filesystem or heap access.
import {need,integer,primary,nValue,caseCap} from './planner.mjs';
export const NAMES=Object.freeze(['identity','setup','observe','batch','checkpoint','stage','validate']);
const IDLE=Object.freeze({activeCaseId:null,inputSource:null,stagedValidation:null,prepared:false,retainedUntimedOutput:false});
export const emptyCounts=()=>({publicFunctionEntries:0,perExportEntries:Object.fromEntries(NAMES.map(n=>[n,0])),codecCalls:0,controlOperations:0});
const clone=v=>JSON.parse(JSON.stringify(v));
function equal(a,b,label){need(JSON.stringify(a)===JSON.stringify(b),label);}
function keys(v,names,label){need(v!==null&&typeof v==='object'&&!Array.isArray(v),'ordinary '+label);equal(Object.keys(v).sort(),[...names].sort(),'exact '+label+' keys');}
export function aggregate(fnv,bytes,n){
 integer(fnv,0,0xffffffff,'expected output FNV');integer(bytes,0,16777216,'expected output bytes');integer(n,1,32768,'finite aggregate N');
 let hash=2166136261;for(let i=0;i<n;i++)for(const word of[fnv,bytes,i])hash=Math.imul(hash^(word>>>0),16777619)>>>0;return hash;
}
export function compactCase(v){
 need(v&&v.schemaVersion===1,'compact parent-authenticated expected case');primary(v.caseId);
 need(typeof v.caseName==='string'&&v.caseName.length<=100&&['native-on','fflate-on','fflate-off'].includes(v.arm),'finite case/provider identity');
 need(['encode','decode'].includes(v.direction),'direction');integer(v.logicalBytes,0,524288,'logical bytes');
 integer(v.inputBytes,0,1048576,'input cap');integer(v.inputFNV,0,0xffffffff,'input FNV');
 integer(v.outputBytes,0,v.direction==='encode'?1048576:524288,'actual validated output cap');integer(v.outputFNV,0,0xffffffff,'actual validated output FNV');
 need(/^[a-f0-9]{64}$/.test(v.oracleSha256),'oracle binding');
 need(v.inputSource===(v.direction==='encode'?'raw-fixture':'node-oracle-input'),'exact unstaged input source');
 need(v.parentDeclaredInputSha256===null||/^[a-f0-9]{64}$/.test(v.parentDeclaredInputSha256),'actual decode-input SHA');
 need(v.direction==='decode'?v.parentDeclaredInputSha256!==null:v.parentDeclaredInputSha256===null,'direction-specific parent SHA');
 need(v.timingNMax===caseCap(v.caseId),'original per-case N cap');
 // Payloads and huge host oracle/proof reports never enter an owned measured worker.
 keys(v,['schemaVersion','caseId','caseName','arm','direction','logicalBytes','inputBytes','inputFNV','outputBytes','outputFNV','oracleSha256','inputSource','parentDeclaredInputSha256','timingNMax'],'compact case');
 return Object.freeze(clone(v));
}
export function decodeRetainedString(raw,receipt){
 need(receipt&&receipt.fullPrimitiveCaptured===true&&receipt.fsynced===true,'full primitive retained/fsynced BEFORE type/parse/assert');
 need(typeof receipt.path==='string'&&/^[a-f0-9]{64}$/.test(receipt.sha256)&&Number.isSafeInteger(receipt.bytes),'actual durable file descriptor');
 need(typeof raw==='string'&&raw.length<=2097152,'complete bounded primitive string, never clip');
 const v=JSON.parse(raw);const stack=[v];let nodes=0;
 while(stack.length){const x=stack.pop();need(++nodes<=65536,'compact returned JSON bound');if(x===null||typeof x==='string'||typeof x==='boolean')continue;
  if(typeof x==='number'){need(Number.isFinite(x)&&!Object.is(x,-0),'finite exact JSON number');continue;}
  need(x&&typeof x==='object','ordinary JSON');for(const item of Object.values(x))stack.push(item);
 }
 return v;
}
function window(bytes){return{byteOffset:8,byteLength:bytes,backingBytes:bytes+16,prefix:Array(8).fill(165),suffix:Array(8).fill(90),construction:'new ordinary ArrayBuffer; fixed/attached/unshared by construction'};}
export class CompactCollector{
 #case;#counts=emptyCounts();#active=false;
 constructor(value){this.#case=compactCase(value);}
 get counters(){return clone(this.#counts);}
 state(){const c=this.#case;return this.#active?{activeCaseId:c.caseId,inputSource:c.inputSource,stagedValidation:null,prepared:true,retainedUntimedOutput:false}:{...IDLE};}
 #next(name,n=0,controls=0){const v=clone(this.#counts);v.publicFunctionEntries++;v.perExportEntries[name]++;v.codecCalls+=n;v.controlOperations+=controls;return v;}
 #commit(v,want){keys(v.counters,['publicFunctionEntries','perExportEntries','codecCalls','controlOperations'],'counter');keys(v.counters.perExportEntries,NAMES,'named counter');
  for(const n of[v.counters.publicFunctionEntries,v.counters.codecCalls,v.counters.controlOperations,...Object.values(v.counters.perExportEntries)])integer(n,0,Number.MAX_SAFE_INTEGER,'exact counter');
  equal(v.counters,want,'exact whole counters');equal(v.state,this.state(),'exact whole guest state');this.#counts=want;return v;}
 identity(v){const c=this.#case,want=this.#next('identity');need(v.schemaVersion===1&&v.kind==='codec-cost-identity-v1'&&v.version==='bounded-zlib-cost-guest-v1','identity version');
  need(v.provider===(c.arm==='native-on'?'native':'fflate')&&v.oracleSha256===c.oracleSha256&&v.primaryCases===30,'identity provider/oracle');
  equal(v.exports,NAMES,'same seven ordinary exports');equal(v.snapshotState,{prepared:false,staged:false,retainedOutput:false,codecCalls:0,resources:0},'empty snapshot');
  need(v.codecPrewarmedAtSnapshot===false,'no snapshot codec work');return this.#commit(v,want);}
 setup(v){const c=this.#case,want=this.#next('setup');need(v.schemaVersion===1&&v.kind==='codec-cost-setup-v1'&&v.caseId===c.caseId&&v.caseName===c.caseName,'exact setup');
  need(v.inputSource===c.inputSource&&v.inputFNV1aU32===c.inputFNV&&v.parentDeclaredInputSha256===c.parentDeclaredInputSha256&&v.oracleSha256===c.oracleSha256,'actual expected input fingerprint');
  need(v.stagedValidationCleared===true&&v.priorOutputCleared===true,'setup clears validation state');equal(v.input,window(c.inputBytes),'fixed ordinary input window');this.#active=true;return this.#commit(v,want);}
 batch(v,n){const c=this.#case;nValue(c.caseId,n);need(this.#active,'active exact primary batch');const want=this.#next('batch',n);
  keys(v,['schemaVersion','kind','caseId','caseName','provider','operations','inputBytes','logicalUncompressedBytesPerOperation','totalLogicalUncompressedBytes','totalOutputBytes','lastOutputBytes','lastOutputFNV1aU32','aggregateFNV1aU32','outputArraysRetained','counters','state'],'codec batch');
  need(v.schemaVersion===1&&v.kind==='codec-cost-batch-v1'&&v.caseId===c.caseId&&v.caseName===c.caseName&&v.provider===(c.arm==='native-on'?'native':'fflate')&&v.operations===n,'exact whole codec batch identity');
  need(v.inputBytes===c.inputBytes&&v.logicalUncompressedBytesPerOperation===c.logicalBytes&&v.totalLogicalUncompressedBytes===c.logicalBytes*n,'uncompressed logical denominator');
  need(v.totalOutputBytes===c.outputBytes*n&&v.lastOutputBytes===c.outputBytes&&v.lastOutputFNV1aU32===c.outputFNV&&v.aggregateFNV1aU32===aggregate(c.outputFNV,c.outputBytes,n)&&v.outputArraysRetained===false,'full-output consumption/aggregate matches independently accepted actual signature');
  return this.#commit(v,want);}
 control(v,id){const c=this.#case;integer(id,30,119,'control id');need(id%30===c.caseId&&this.#active,'control for active primary');
  const control=id<60?'consumeInput':id<90?'copyInputAndConsume':'harnessNoCodec',want=this.#next('batch',0,1);
  keys(v,['schemaVersion','kind','caseId','primaryCaseId','control','operations','result','logicalUncompressedBytes','counters','state'],'control');
  need(v.schemaVersion===1&&v.kind==='codec-cost-control-v1'&&v.caseId===id&&v.primaryCaseId===c.caseId&&v.control===control&&v.operations===1&&v.logicalUncompressedBytes===c.logicalBytes,'exact N1 control');
  const expected=control==='harnessNoCodec'?{bytesConsumed:0,declaredInputBytes:c.inputBytes,tag:2166136261,copies:0,codecCalls:0}:
   {bytesConsumed:c.inputBytes,fnv:c.inputFNV,copies:control==='copyInputAndConsume'?1:0,codecCalls:0};equal(v.result,expected,'raw control result; no provider branch or subtraction');return this.#commit(v,want);}
 checkpoint(v){const c=this.#case,want=this.#next('checkpoint');need(v.schemaVersion===1&&v.kind==='codec-cost-checkpoint-v1'&&v.preparedAndStageAndPriorOutputCleared===true&&v.gcOrResetInvoked===false,'checkpoint clears without GC/reset');
  equal(v.before,this.state(),'exact pre-checkpoint state');equal(v.input,{...window(c.inputBytes),fnv1aU32:c.inputFNV,matchesSetupFNV:true,sentinelsUnchanged:true},'reported complete input fingerprint and sentinels');
  this.#active=false;return this.#commit(v,want);}
}
