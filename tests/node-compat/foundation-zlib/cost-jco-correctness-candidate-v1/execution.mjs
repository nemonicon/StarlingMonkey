// Internal scenario engine over an ALREADY reviewed synchronous invoke wrapper.
// No generated-module loader is inferred here. This is not an action entry.
import {primaryCase,crossdecode,call,makeStream,assertSameStream} from './scenarios.mjs';
import {Collector} from './collector.mjs';
import {need} from './transport.mjs';
export async function executePrimary({session,write,arm,caseIds,rotations,oracleSha256,cases,nodeInputs,rawFixtures,prefix}){
 need(typeof session?.invoke==='function'&&[1,3].includes(rotations),'Future actual synchronous wrapper and finite rotations');
 need(Array.isArray(caseIds)&&caseIds.length>0&&new Set(caseIds).size===caseIds.length&&caseIds.every(id=>Number.isInteger(id)&&id>=0&&id<30),'Exact primary IDs');
 const collector=new Collector({arm,oracleSha256,cases,nodeInputs,rawFixtures,write}),records=[],streams=new Map();
 await call(session,collector,write,prefix+'-identity','identity',[]);
 for(let rotation=0;rotation<rotations;rotation++)for(const caseId of caseIds){
  const name=prefix+'-rotation'+rotation+'-case'+String(caseId).padStart(2,'0');
  await write(name+'-started.json',{schemaVersion:1,kind:'primary',arm,caseId,rotation,partial:true});
  const result=await primaryCase({session,collector,write,caseId,prefix:name}),row=cases[caseId];
  if(row.direction==='encode'){
   const stream=makeStream({provider:arm,row,bytes:result.first}),old=streams.get(stream.streamId);
   if(old)await assertSameStream(write,name,stream,old);else streams.set(stream.streamId,stream);
  }
  const record={schemaVersion:1,arm,caseId,rotation,rawRows:result.rawRows,fullDecodeFixtureEqualityChecked:row.direction==='decode',withinProviderEncodedDeterminismChecked:row.direction==='encode',priorOutputStabilityReportedAndChecked:true,publicCounters:collector.counters(),checkpointState:collector.state(),untimedBatchN1:true,withinExportPairCompared:true};
  await write(name+'-complete.json',record);records.push(record);
 }
 return{schemaVersion:1,arm,records,streams:[...streams.values()],retainedInstance:rotations===3,retainedRotations:rotations,actualFreshProcessProvedHere:false,resetOrReuseProof:false,timing:false};
}
export async function executeGuestEdge({session,write,arm,stream,oracleSha256,cases,nodeInputs,rawFixtures,prefix}){
 need(typeof session?.invoke==='function','Future reviewed actual synchronous wrapper');
 const collector=new Collector({arm,oracleSha256,cases,nodeInputs,rawFixtures,write});await call(session,collector,write,prefix+'-identity','identity',[]);
 await write(prefix+'-started.json',{schemaVersion:1,arm,stream,partial:true});
 const record=await crossdecode({session,collector,write,record:stream,prefix});
 const result={schemaVersion:1,decoder:arm,streamId:stream.streamId,provider:stream.provider,caseId:stream.caseId,rawRows:record.rawRows,fullRawFixtureEqual:true,adjacentFullPairChecked:true,priorOutputStabilityReportedAndChecked:true,publicCounters:collector.counters(),checkpointState:collector.state(),actualFreshProcessProvedHere:false,resetOrReuseProof:false,timing:false};
 await write(prefix+'-complete.json',result);return result;
}
