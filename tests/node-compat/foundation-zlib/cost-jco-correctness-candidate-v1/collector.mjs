// Ordinary JSON/byte collectors only. No guest, provider or codec imports.
import {need,exactKeys,fullBytes,equalBytes,exact,hash} from './transport.mjs';
import {consumeFNV1a} from './fixtures.mjs';
export const NAMES=Object.freeze(['identity','setup','observe','batch','checkpoint','stage','validate']);
const IDLE=Object.freeze({activeCaseId:null,inputSource:null,stagedValidation:null,prepared:false,retainedUntimedOutput:false});
const emptyCounts=()=>({publicFunctionEntries:0,perExportEntries:Object.fromEntries(NAMES.map(name=>[name,0])),codecCalls:0,controlOperations:0});
function copy(value){return JSON.parse(JSON.stringify(value));}
function step(before,name,codec=0){const next=copy(before);next.publicFunctionEntries++;next.perExportEntries[name]++;next.codecCalls+=codec;return next;}
function aggregate(fnv,bytes){let value=2166136261;for(const item of[fnv,bytes,0])value=Math.imul(value^(item>>>0),16777619)>>>0;return value;}
function window(bytes){return{byteOffset:8,byteLength:bytes.length,backingBytes:bytes.length+16,prefix:Array(8).fill(0xa5),suffix:Array(8).fill(0x5a),construction:'new ordinary ArrayBuffer; fixed/attached/unshared by construction'};}
export class Collector{
 #counts=emptyCounts();#active=null;#prior=null;#cases;#nodeInputs;#rawFixtures;#write;
 constructor({arm,oracleSha256,cases,nodeInputs,rawFixtures,write}){
  need(['native-on','fflate-on','fflate-off'].includes(arm),'finite guest arm');need(/^[0-9a-f]{64}$/.test(oracleSha256),'exact oracle digest');
  Object.defineProperties(this,{arm:{value:arm},oracleSha256:{value:oracleSha256}});
  const freeze=value=>{if(value&&typeof value==='object'){for(const item of Object.values(value))freeze(item);Object.freeze(value);}return value;};
  this.#cases=freeze(copy(cases));this.#nodeInputs=freeze(copy(nodeInputs));this.#rawFixtures=new Map([...rawFixtures].map(([name,bytes])=>[name,new Uint8Array(bytes)]));this.#write=write;
 }
 counters(){return copy(this.#counts);}
 state(){return this.#active?{activeCaseId:this.#active.row.index,inputSource:this.#active.source,stagedValidation:copy(this.#active.stage),prepared:true,retainedUntimedOutput:this.#prior!==null}:{...IDLE};}
 async counts(value,wanted,name){exactKeys(value,['publicFunctionEntries','perExportEntries','codecCalls','controlOperations'],'counters');exactKeys(value.perExportEntries,NAMES,'per-export counts');for(const count of[value.publicFunctionEntries,value.codecCalls,value.controlOperations,...Object.values(value.perExportEntries)])need(Number.isSafeInteger(count)&&count>=0&&!Object.is(count,-0),'safe exact counters');await exact(this.#write,name+'-counters',value,wanted);}
 row(index){need(Number.isInteger(index)&&index>=0&&index<30,'primary case0..29');return this.#cases[index];}
 input(index){const row=this.row(index);if(row.direction==='encode')return{bytes:new Uint8Array(this.#rawFixtures.get(row.fixture)),source:'raw-fixture',parentSha:null};const record=this.#nodeInputs.find(value=>value.caseId===index);need(record,'all15 actual Node decoder inputs');const bytes=Buffer.from(record.encodedBase64,'base64');need(hash(bytes)===record.encodedSha256&&bytes.length===record.encodedBytes,'actual authenticated Node input');return{bytes,source:'node-oracle-input',parentSha:record.encodedSha256};}
 async identity(value,name){
  const wanted=step(this.#counts,'identity');need(value.schemaVersion===1&&value.kind==='codec-cost-identity-v1'&&value.version==='bounded-zlib-cost-guest-v1','actual identity version');
  need(value.provider===(this.arm==='native-on'?'native':'fflate')&&value.oracleSha256===this.oracleSha256&&value.primaryCases===30,'provider/oracle identity');
  await exact(this.#write,name+'-exports',value.exports,NAMES);await exact(this.#write,name+'-snapshot',value.snapshotState,{prepared:false,staged:false,retainedOutput:false,codecCalls:0,resources:0});
  need(value.codecPrewarmedAtSnapshot===false,'guest reports no workload prewarm');await exact(this.#write,name+'-state',value.state,this.state());await this.counts(value.counters,wanted,name);this.#counts=wanted;
 }
 async setup(value,index,name,base=null){
  const row=this.row(index),input=this.input(index),wanted=step(base??this.#counts,'setup');
  need(value.schemaVersion===1&&value.kind==='codec-cost-setup-v1'&&value.caseId===index&&value.caseName===row.id,'actual setup case');
  need(value.inputSource===input.source&&value.inputFNV1aU32===consumeFNV1a(input.bytes)&&value.parentDeclaredInputSha256===input.parentSha&&value.oracleSha256===this.oracleSha256,'full setup source/FNV/oracle');
  need(value.stagedValidationCleared===true&&value.priorOutputCleared===true,'setup clears stage/prior');await exact(this.#write,name+'-window',value.input,window(input.bytes));
  this.#active={row,bytes:input.bytes,source:input.source,stage:null};this.#prior=null;await exact(this.#write,name+'-state',value.state,this.state());await this.counts(value.counters,wanted,name);this.#counts=wanted;
 }
 stream(record,index){
  const row=this.row(index);need(row.direction==='decode'&&record.caseId===index&&record.fixture===row.fixture&&record.format===row.format,'staged exact decoder');need(['node-22.14.0','native-on','fflate-on','fflate-off'].includes(record.provider),'finite actual encoder');
  need(record.schemaVersion===1&&record.kind==='codec-cost-stage-v1'&&record.streamId===record.provider+'.'+record.fixture+'.'+record.format,'versioned actual stream ID');
  need(Number.isInteger(record.encodedBytes)&&record.encodedBytes>0&&record.encodedBytes<=1048576,'actual compressed input cap before decoder');
  const bytes=Buffer.from(record.encodedBase64,'base64');need(bytes.toString('base64')===record.encodedBase64&&bytes.length===record.encodedBytes&&consumeFNV1a(bytes)===record.encodedFNV1aU32&&hash(bytes)===record.encodedSha256,'parent full staged bytes/SHA/FNV');return bytes;
 }
 async stage(value,record,name){
  need(this.#active,'setup before stage');const index=this.#active.row.index,bytes=this.stream(record,index),wanted=step(this.#counts,'stage');
  need(value.schemaVersion===1&&value.kind==='codec-cost-stage-ack-v1'&&value.caseId===index&&value.streamId===record.streamId&&value.provider===record.provider&&value.fixture===record.fixture&&value.format===record.format,'actual stage identity');
  need(value.decodedBytes===bytes.length&&value.decodedFNV1aU32===consumeFNV1a(bytes)&&value.parentDeclaredSha256===record.encodedSha256&&value.sha256RecomputedInGuest===false&&value.codecInvoked===false,'base64 staging evidence, not a codec invocation');
  await exact(this.#write,name+'-window',value.input,window(bytes));
  this.#active={row:this.#active.row,bytes,source:'staged-validation',stage:{caseId:index,streamId:record.streamId,provider:record.provider,fixture:record.fixture,format:record.format,parentDeclaredSha256:record.encodedSha256}};this.#prior=null;
  await exact(this.#write,name+'-state',value.state,this.state());await this.counts(value.counters,wanted,name);this.#counts=wanted;
 }
 async observe(value,index,name){
  const row=this.row(index);need(this.#active?.row.index===index,'exact active observe');const wanted=step(this.#counts,'observe',1),expectedInput=this.#active.bytes;
  need(value.schemaVersion===1&&value.kind==='codec-cost-observation-v1'&&value.caseId===index&&value.caseName===row.id&&value.operation===row.operation&&value.format===row.format&&value.direction===row.direction&&value.provider===(this.arm==='native-on'?'native':'fflate'),'actual observation identity');
  need(value.logicalUncompressedBytes===row.logicalUncompressedBytesPerOperation&&value.inputSource===this.#active.source,'exact logical/source domain');await exact(this.#write,name+'-stage',value.stage,this.#active.stage);
  await exact(this.#write,name+'-input',value.input,{...window(expectedInput),fnv1aU32:consumeFNV1a(expectedInput),fullInputUnchanged:true});
  const bytes=fullBytes(value.output,row.direction==='encode'?1048576:524288);need(value.output.isBuffer===true&&value.output.fnv1aU32===consumeFNV1a(bytes),'complete ordinary Buffer output');
  need(Number.isSafeInteger(value.output.byteOffset)&&value.output.byteOffset>=0&&Number.isSafeInteger(value.output.backingBytes)&&value.output.backingBytes>=value.output.byteOffset+bytes.length,'public output window bounds');
  if(row.direction==='decode'&&!equalBytes(bytes,this.#rawFixtures.get(row.fixture))){await this.#write(name+'-full-byte-counterexample.json',{actual:value.output,expectedBase64:Buffer.from(this.#rawFixtures.get(row.fixture)).toString('base64')});throw new Error('ERR_COST_JCO_CORRECTNESS: full decoder bytes mismatch; raw counterexample retained');}
  const own=value.ownership;need(own&&own.nonemptyOutputInputIndependent===(bytes.length?true:null),'nonempty output/input independence, no empty-byte claim');
  if(!bytes.length)need(typeof own.emptyBackingRelationRecorded?.sharesInputBacking==='boolean'&&own.emptyBackingRelationRecorded.isolationClaim===false,'empty backing relation is only recorded');
  if(this.#prior){
   need(own.previousComparable===true&&own.previousFullBytesUnchanged===true,'full prior output stable after next provider call');
   if(!equalBytes(bytes,this.#prior.bytes)){await this.#write(name+'-repeat-counterexample.json',{actual:value.output,expectedBase64:Buffer.from(this.#prior.bytes).toString('base64')});throw new Error('ERR_COST_JCO_CORRECTNESS: provider nondeterminism; full counterexample retained');}
   if(bytes.length&&this.#prior.bytes.length)need(own.successiveIndependentBacking===true&&own.mutationProbe?.performed===true&&own.mutationProbe.currentFullBytesUnchanged===true&&own.mutationProbe.inputFullBytesUnchanged===true&&own.mutationProbe.previousRestored===true,'actual prior mutation/restoration isolation');
  }else need(own.previousComparable===false&&own.previousFullBytesUnchanged===null&&own.mutationProbe?.performed===false,'first observation makes no prior claim');
  await this.counts(value.counters,wanted,name);this.#counts=wanted;this.#prior={bytes:new Uint8Array(bytes)};return bytes;
 }
 async batch(value,index,name,expectedOutput){
  const row=this.row(index);need(this.#active?.row.index===index,'active untimed N1 batch');const wanted=step(this.#counts,'batch',1),fnv=consumeFNV1a(expectedOutput);
  need(value.schemaVersion===1&&value.kind==='codec-cost-batch-v1'&&value.caseId===index&&value.caseName===row.id&&value.provider===(this.arm==='native-on'?'native':'fflate')&&value.operations===1,'untimed primary batchN1 only; never controls');
  need(value.inputBytes===this.#active.bytes.length&&value.logicalUncompressedBytesPerOperation===row.logicalUncompressedBytesPerOperation&&value.totalLogicalUncompressedBytes===row.logicalUncompressedBytesPerOperation&&value.totalOutputBytes===expectedOutput.length&&value.lastOutputBytes===expectedOutput.length&&value.lastOutputFNV1aU32===fnv&&value.aggregateFNV1aU32===aggregate(fnv,expectedOutput.length)&&value.outputArraysRetained===false,'whole compact result equals preceding full output');
  this.#prior=null;await exact(this.#write,name+'-state',value.state,this.state());await this.counts(value.counters,wanted,name);this.#counts=wanted;
 }
 async checkpoint(value,name){
  const wanted=step(this.#counts,'checkpoint');need(value.schemaVersion===1&&value.kind==='codec-cost-checkpoint-v1'&&value.preparedAndStageAndPriorOutputCleared===true&&value.gcOrResetInvoked===false,'public cleanup, no GC/reset');await exact(this.#write,name+'-before',value.before,this.state());
  if(this.#active)await exact(this.#write,name+'-input',value.input,{...window(this.#active.bytes),fnv1aU32:consumeFNV1a(this.#active.bytes),matchesSetupFNV:true,sentinelsUnchanged:true});else need(value.input===null,'idle checkpoint input');
  this.#active=null;this.#prior=null;await exact(this.#write,name+'-state',value.state,this.state());await this.counts(value.counters,wanted,name);this.#counts=wanted;
 }
 async validate(value,request,name){
  need(request.schemaVersion===1&&['primary','crossdecode'].includes(request.kind),'strict untimed validate request');const row=this.row(request.caseId);need(value.schemaVersion===1&&value.kind==='codec-cost-validation-v1'&&value.requestKind===request.kind&&value.caseId===row.index&&value.withinOneOuterExport===true&&value.separateHostCallInterleavingProved===false,'within-one-export wrapper only');
  this.#counts=step(this.#counts,'validate');await this.setup(value.setup,row.index,name+'-setup');
  if(request.kind==='crossdecode')await this.stage(value.stage,request.stageRecord,name+'-stage');else need(value.stage===null,'primary wrapper has no stage');
  need(Array.isArray(value.observations)&&value.observations.length===2,'full adjacent validate pair');const first=await this.observe(value.observations[0],row.index,name+'-first'),second=await this.observe(value.observations[1],row.index,name+'-second');
  await this.counts(value.counters,this.#counts,name);await exact(this.#write,name+'-state',value.state,this.state());return{first,second};
 }
}
