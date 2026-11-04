// Ordinary guest JS only. No clocks, hosts, process, streams or native exports.
import {fixtureSpecs,fixtureBytes,consumeFNV1a} from './fixtures.mjs';
import {createControls} from './controls.mjs';
import {cases,VERSION,EXPORTS,MAX_INPUT,MAX_OUTPUT,MAX_RAW,requireValue,primaryCase,operationCount,jsonRecord,wire,bytesEqual,base64,stageRecord,nodeInputs,exactKeys,aggregateStep} from './contract.mjs';
import {ownedWindow,windowMetadata,unchangedWindow} from './owned-window.mjs';
import {captureUntimedOutput,requirePriorOutputUnchanged} from './output-stability.mjs';
export function createRuntime({provider,oracleInputs}){
 requireValue(provider&&['native','fflate'].includes(provider.id),'finite source provider');
 const Buffer=provider.Buffer,inputs=nodeInputs(oracleInputs),controls=createControls({Buffer});
 for(const row of cases)requireValue(typeof provider.methods[row.operation]==='function','six captured methods');
 const perExportEntries=Object.fromEntries(EXPORTS.map(name=>[name,0]));
 let publicFunctionEntries=0,codecCalls=0,controlOperations=0,active=null,priorOutput=null;
 const snapshotState=Object.freeze({prepared:false,staged:false,retainedOutput:false,codecCalls:0,resources:0});
 const enter=name=>{publicFunctionEntries++;perExportEntries[name]++;};
 const counters=()=>({publicFunctionEntries,perExportEntries:{...perExportEntries},codecCalls,controlOperations});
 const state=()=>({activeCaseId:active?.row.index??null,inputSource:active?.source??null,stagedValidation:active?.stage??null,prepared:!!active?.window,retainedUntimedOutput:priorOutput!==null});
 function needActive(caseId){const row=primaryCase(caseId);requireValue(active&&active.row.index===caseId&&active.window,'setup required for exact active primary');return row;}
 function prepare(caseId){
  active=null;priorOutput=null;const row=primaryCase(caseId);let bytes,source,parentSha256=null;
  if(row.direction==='encode'){bytes=fixtureBytes(fixtureSpecs.find(value=>value.id===row.fixture));source='raw-fixture';}
  else{const found=inputs.records.find(value=>value.caseId===caseId),checked=stageRecord(found);bytes=checked.bytes;source='node-oracle-input';parentSha256=checked.record.encodedSha256;}
  const window=ownedWindow(Buffer,bytes);active={row,window,source,stage:null,setupInputFNV:consumeFNV1a(window.input)};
  return{row,source,parentSha256};
 }
 function setup(caseId){
  enter('setup');const prepared=prepare(caseId);
  return wire({schemaVersion:1,kind:'codec-cost-setup-v1',caseId,caseName:prepared.row.id,inputSource:prepared.source,input:windowMetadata(active.window),inputFNV1aU32:active.setupInputFNV,parentDeclaredInputSha256:prepared.parentSha256,oracleSha256:inputs.oracleSha256,stagedValidationCleared:true,priorOutputCleared:true,counters:counters(),state:state()});
 }
 function stage(record){
  enter('stage');requireValue(active,'setup before stage');const original=active.row;
  // A failed stage cannot leave an old staged stream available as a fallback.
  priorOutput=null;active={row:original,window:null,source:null,stage:null};
  const checked=stageRecord(jsonRecord(record));requireValue(checked.row.index===original.index,'stage exact active decoder ID');
  const window=ownedWindow(Buffer,checked.bytes),value=checked.record;
  active={row:original,window,source:'staged-validation',setupInputFNV:consumeFNV1a(window.input),stage:{caseId:value.caseId,streamId:value.streamId,provider:value.provider,fixture:value.fixture,format:value.format,parentDeclaredSha256:value.encodedSha256}};
  return wire({schemaVersion:1,kind:'codec-cost-stage-ack-v1',caseId:original.index,streamId:value.streamId,provider:value.provider,fixture:value.fixture,format:value.format,decodedBytes:window.input.length,decodedFNV1aU32:active.setupInputFNV,parentDeclaredSha256:value.encodedSha256,sha256RecomputedInGuest:false,input:windowMetadata(window),codecInvoked:false,counters:counters(),state:state()});
 }
 function invoke(row){
  requireValue(active.window.input.length<=MAX_INPUT&&unchangedWindow(active.window),'fixed bounded input/sentinels before provider');
  codecCalls++;const output=provider.methods[row.operation](active.window.input);
  requireValue(Buffer.isBuffer(output)&&output.length<=MAX_OUTPUT,'bounded ordinary Buffer output');return output;
 }
 function observe(caseId){
  enter('observe');const row=needActive(caseId),inputBefore=new Uint8Array(active.window.input),output=invoke(row);
  requireValue(output.length<=(row.direction==='encode'?MAX_INPUT:MAX_RAW),'trusted full-output transport domain');
  requireValue(unchangedWindow(active.window,inputBefore),'full input immutability');
  const nonempty=output.length>0;requireValue(!nonempty||output.buffer!==active.window.input.buffer,'nonempty output/input independence');
  const previousComparable=priorOutput!==null&&priorOutput.caseId===caseId;
  let independentBacking=null,previousFullBytesUnchanged=null,mutationProbe={performed:false,reason:previousComparable?'empty output has no addressable mutation':'no previous comparable output',currentFullBytesUnchanged:null,inputFullBytesUnchanged:null,previousRestored:null};
  if(previousComparable){
   requirePriorOutputUnchanged(priorOutput);previousFullBytesUnchanged=true;
   independentBacking=nonempty&&priorOutput.output.length>0?output.buffer!==priorOutput.output.buffer:null;
   if(nonempty&&priorOutput.output.length>0){
    requireValue(independentBacking,'successive nonempty output backing independence');const currentBefore=new Uint8Array(output),saved=priorOutput.output[0];
    try{priorOutput.output[0]=saved^255;requireValue(bytesEqual(output,currentBefore)&&unchangedWindow(active.window,inputBefore),'previous mutation must not affect current/input');}
    finally{priorOutput.output[0]=saved;requirePriorOutputUnchanged(priorOutput);}
    mutationProbe={performed:true,reason:null,currentFullBytesUnchanged:true,inputFullBytesUnchanged:true,previousRestored:priorOutput.output[0]===saved};
   }
  }
  const result={schemaVersion:1,kind:'codec-cost-observation-v1',caseId,caseName:row.id,provider:provider.id,operation:row.operation,format:row.format,direction:row.direction,logicalUncompressedBytes:row.logicalUncompressedBytesPerOperation,inputSource:active.source,stage:active.stage,input:{...windowMetadata(active.window),fnv1aU32:consumeFNV1a(active.window.input),fullInputUnchanged:true},output:{bytes:output.length,fnv1aU32:consumeFNV1a(output),base64:base64(output),byteOffset:output.byteOffset,backingBytes:output.buffer.byteLength,isBuffer:true},ownership:{nonemptyOutputInputIndependent:nonempty?true:null,emptyBackingRelationRecorded:nonempty?null:{sharesInputBacking:output.buffer===active.window.input.buffer,isolationClaim:false},previousComparable,previousFullBytesUnchanged,successiveIndependentBacking:independentBacking,mutationProbe},counters:counters()};
  priorOutput=captureUntimedOutput(caseId,output,result.output.base64);return wire(result);
 }
 function batch(caseId,operations){
  enter('batch');priorOutput=null;const selected=operationCount(caseId,operations),row=needActive(selected.primary.index);
  if(selected.kind!=='codec'){
   controlOperations++;const result=controls[selected.kind](active.window.input);
   return wire({schemaVersion:1,kind:'codec-cost-control-v1',caseId,primaryCaseId:row.index,control:selected.kind,operations:1,result,logicalUncompressedBytes:row.logicalUncompressedBytesPerOperation,counters:counters(),state:state()});
  }
  let aggregateFNV1aU32=2166136261,totalOutputBytes=0,lastOutputBytes=0,lastOutputFNV1aU32=null;
  for(let index=0;index<operations;index++){
   const output=invoke(row),fnv=consumeFNV1a(output);lastOutputBytes=output.length;lastOutputFNV1aU32=fnv;totalOutputBytes+=output.length;
   requireValue(Number.isSafeInteger(totalOutputBytes),'safe aggregate byte count');aggregateFNV1aU32=aggregateStep(aggregateFNV1aU32,fnv,output.length,index);
  }
  return wire({schemaVersion:1,kind:'codec-cost-batch-v1',caseId,caseName:row.id,provider:provider.id,operations,inputBytes:active.window.input.length,logicalUncompressedBytesPerOperation:row.logicalUncompressedBytesPerOperation,totalLogicalUncompressedBytes:row.logicalUncompressedBytesPerOperation*operations,totalOutputBytes,lastOutputBytes,lastOutputFNV1aU32,aggregateFNV1aU32,outputArraysRetained:false,counters:counters(),state:state()});
 }
 function checkpoint(){
  enter('checkpoint');const before=state(),input=active?.window?{...windowMetadata(active.window),fnv1aU32:consumeFNV1a(active.window.input),matchesSetupFNV:consumeFNV1a(active.window.input)===active.setupInputFNV,sentinelsUnchanged:unchangedWindow(active.window)}:null;
  active=null;priorOutput=null;return wire({schemaVersion:1,kind:'codec-cost-checkpoint-v1',before,input,preparedAndStageAndPriorOutputCleared:true,counters:counters(),state:state(),gcOrResetInvoked:false});
 }
 function identity(){enter('identity');return wire({schemaVersion:1,kind:'codec-cost-identity-v1',version:VERSION,provider:provider.id,providerSourceVersion:provider.sourceVersion,oracleSha256:inputs.oracleSha256,primaryCases:30,controlCaseRanges:{consumeInput:[30,59],copyInputAndConsume:[60,89],harnessNoCodec:[90,119]},exports:[...EXPORTS],snapshotState,counterMeaning:'named-function entries including internal validate calls; outer host calls are parent raw records',counters:counters(),state:state(),codecPrewarmedAtSnapshot:false});}
 function validate(record){
  enter('validate');const request=jsonRecord(record);requireValue(request&&typeof request==='object','validation request');
  requireValue(request.schemaVersion===1&&['primary','crossdecode'].includes(request.kind),'finite validation kind/version');
  exactKeys(request,request.kind==='primary'?['schemaVersion','kind','caseId']:['schemaVersion','kind','caseId','stageRecord'],'validation request');
  const row=primaryCase(request.caseId);if(request.kind==='crossdecode')requireValue(row.direction==='decode','crossdecode request requires decoder');
  const setupResponse=JSON.parse(setup(request.caseId)),stageResponse=request.kind==='crossdecode'?JSON.parse(stage(wire(request.stageRecord))):null;
  const first=JSON.parse(observe(request.caseId)),second=JSON.parse(observe(request.caseId));
  return wire({schemaVersion:1,kind:'codec-cost-validation-v1',requestKind:request.kind,caseId:request.caseId,setup:setupResponse,stage:stageResponse,observations:[first,second],withinOneOuterExport:true,separateHostCallInterleavingProved:false,counters:counters(),state:state()});
 }
 return Object.freeze({identity,setup,stage,observe,batch,checkpoint,validate});
}
