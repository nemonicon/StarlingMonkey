// Pure full-return validation; never invokes guest, clock or filesystem.
import {isDeepStrictEqual as same} from 'node:util';
import {need,pureResult,realtimeBracket} from './models.mjs';
export function plannedCalls(id,scenario){
 need(['retained','fresh','node-oracle'].includes(scenario),'Finite worker scenario');
 if(id==='resource'){need(scenario!=='node-oracle','No fake Node scheduler oracle');return[{name:'inspect',args:[]},...Array.from({length:scenario==='retained'?21:7},(_,i)=>({name:'run',args:[i%7]})),{name:'inspect',args:[]}];}
 need(['pure','clock-snapshot','surviving-interest'].includes(id),'Positive finite session fixture');need(id==='pure'||scenario!=='node-oracle','Only deterministic pure Node oracle');const count=id==='pure'?(scenario==='fresh'?1:2):(scenario==='retained'?3:1);return Array.from({length:count},()=>({name:'run',args:[]}));
}
export function retainedRows(rows,plan){
 need(Array.isArray(rows)&&rows.length===plan.length,'No omitted typed calls');return rows.map((v,i)=>{need(v.schemaVersion===1&&v.sequence===i+1&&v.name===plan[i].name&&same(v.args,plan[i].args)&&v.kind==='return'&&v.observed?.type==='string'&&typeof v.observed.value==='string','Complete ordered typed synchronous returns');need(Number.isSafeInteger(v.hostWallBeforeMs)&&Number.isSafeInteger(v.hostWallAfterMs),'Actual host wall brackets');return v.observed.value;});
}
export function validateSession(fixture,scenario,rows,collectors){
 const raw=retainedRows(rows,plannedCalls(fixture.id,scenario));
 if(fixture.id==='pure'){raw.forEach((x,i)=>pureResult(x,i+1));return{publicStrings:raw.length,pureValues:raw,nodeOracleExactnessRequired:true};}
 if(fixture.id==='resource'){
  const before=collectors.validateResourceInspect(raw[0]),after=collectors.validateResourceInspect(raw.at(-1)),values=collectors.validateResourceSequence(raw.slice(1,-1),scenario==='retained'?3:1),first=values[0],last=values.at(-1);
  need(before.state.counters.inspect===1&&before.state.counters.run===0&&before.state.counters.startedCases===0&&before.state.counters.completedCases===0&&before.state.counters.timerCallbacks===0&&before.state.registeredIds.length===0,'Fresh initial snapshot counters/IDs');
  need(first.before.counters.inspect===1&&first.before.counters.validate===0&&first.before.counters.run===1&&first.before.counters.startedCases===1&&first.before.counters.completedCases===0&&first.before.registeredIds.length===0,'First run follows actual inspect');
  for(const key of ['run','validate','timerCallbacks','startedCases','completedCases'])need(after.state.counters[key]===last.after.counters[key],'Whole final inspect counter '+key);need(after.state.counters.inspect===2&&same(after.state.registeredIds,last.after.registeredIds),'Final inspection preserves every ID');
  return{publicStrings:raw.length,runRecords:values.length,callbackObservations:values.reduce((n,v)=>n+v.after.counters.timerCallbacks-v.before.counters.timerCallbacks,0),newIds:values.reduce((n,v)=>n+v.after.registeredIds.length-v.before.registeredIds.length,0),withinRetainedModuleOnly:true,nativeResourceCountsObserved:false};
 }
 let previous=null;const ids=new Set(),values=[];for(let i=0;i<raw.length;i++){
  const v=fixture.id==='clock-snapshot'?collectors.validateClockSnapshot(raw[i],previous):collectors.validateSurvivingInterest(raw[i]);need(v.calls===i+1,'Complete scalar retained call counter');if(fixture.id==='clock-snapshot')realtimeBracket(v,rows[i].hostWallBeforeMs,rows[i].hostWallAfterMs);else for(const id of v.ids){need(!ids.has(id),'No timer ID reuse across retained calls');ids.add(id);}values.push(v);previous=v;
 }
 return{publicStrings:raw.length,callCounters:values.map(x=>x.calls),fullInitializations:fixture.id==='clock-snapshot'?values.map(x=>x.initialization):[],perSessionTimeOrigins:fixture.id==='clock-snapshot'?values.map(x=>x.before.timeOrigin):[],hostWallTimeBracketed:fixture.id==='clock-snapshot',performanceTimeOriginEpochAssumed:false,nativeInterestOrDropObserved:false};
}
export function validateWasmtime(fixture,raw,before,after,collectors){
 if(fixture.id==='pure'){pureResult(raw,1);return{publicStrings:1,pureValue:raw};}
 if(fixture.id==='resource'){const v=collectors.validateResourceWrapper(raw);return{publicStrings:1,runRecords:7,callbackObservations:14,newIds:46,withinOneOuterExport:true,separateHostCallInterleavingProved:false,wholeWrapper:v};}
 const v=fixture.id==='clock-snapshot'?collectors.validateClockSnapshot(raw):collectors.validateSurvivingInterest(raw);need(v.calls===1,'Fresh WT scalar counter');if(fixture.id==='clock-snapshot')realtimeBracket(v,before,after);return{publicStrings:1,fullValue:v,nativeOffsetInterestDropOrTeardownProved:false};
}
