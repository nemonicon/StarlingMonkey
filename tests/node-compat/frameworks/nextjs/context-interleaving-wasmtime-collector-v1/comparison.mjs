// Pure DATA only. The genuine producer projection imports no platform services
// and runs no collection/timer/ALS work at import; only its projection is used.
import assert from 'node:assert/strict';
import {isDeepStrictEqual} from 'node:util';
import {CONTEXT_CONTROL_IDS,contextPublicProjection} from '../../../async-context/context-interleaving-candidate-v1/cases.mjs';
const exact=(x,names)=>{assert(x&&typeof x==='object'&&!Array.isArray(x));assert.deepEqual(Object.keys(x).sort(),[...names].sort());};
const sorted=x=>[...x].sort();
const edgeKey=e=>JSON.stringify(e);
const fail=(control,reason)=>{throw new Error(control+': '+reason);};
export function validateCollection(value,call,contract,boundaryMode){
 exact(value,['schemaVersion','suite','call','boundaryMode','records','passed','logicalBranchesOnly','actualHttpResourceConcurrencyProved','nativeOwnerIdentityOrTeardownProved','resetOrGcWorkload','peakPlannedWaits']);
 assert.equal(value.schemaVersion,1);assert.equal(value.suite,'CONTEXT_INTERLEAVING_FIVE_CONTROLS_V1');assert.equal(value.call,call);assert.equal(value.boundaryMode,boundaryMode);assert.equal(value.passed,true);
 assert.equal(value.logicalBranchesOnly,true);for(const k of ['actualHttpResourceConcurrencyProved','nativeOwnerIdentityOrTeardownProved','resetOrGcWorkload'])assert.equal(value[k],false);
 assert(Number.isInteger(value.peakPlannedWaits)&&value.peakPlannedWaits>=0&&value.peakPlannedWaits<=8);
 assert(Array.isArray(value.records));assert.deepEqual(value.records.map(r=>r.id),CONTEXT_CONTROL_IDS);assert.deepEqual(contract.map(r=>r.id),CONTEXT_CONTROL_IDS);
 let assertions=0,edges=0;
 for(let i=0;i<5;i++){
  const r=value.records[i],c=contract[i];exact(r,['id','passed','assertions','events','requiredEdges']);assert.equal(r.passed,true,r.id+': passed');
  assert(Array.isArray(r.assertions)&&Array.isArray(r.events)&&Array.isArray(r.requiredEdges));
  for(const a of r.assertions){exact(a,['id','passed']);assert.equal(typeof a.id,'string');if(a.passed!==true)fail(r.id,a.id+' is not literal true');}
  assert.equal(new Set(r.assertions.map(a=>a.id)).size,r.assertions.length,r.id+': duplicate assertions');
  assert.deepEqual(sorted(r.assertions.map(a=>a.id)),c.assertionIds,r.id+': assertion inventory');
  assert(r.events.every(x=>typeof x==='string'));assert.equal(new Set(r.events).size,r.events.length,r.id+': duplicate events');assert.deepEqual(sorted(r.events),c.eventIds,r.id+': event inventory');
  for(const e of r.requiredEdges){assert(Array.isArray(e)&&e.length===2&&e.every(x=>typeof x==='string'));if(r.events.indexOf(e[0])<0||r.events.indexOf(e[1])<0||r.events.indexOf(e[0])>=r.events.indexOf(e[1]))fail(r.id,'partial-order '+e[0]+' < '+e[1]);}
  const actualEdges=r.requiredEdges.map(edgeKey);assert.equal(new Set(actualEdges).size,actualEdges.length);assert.deepEqual(sorted(actualEdges),sorted(c.requiredEdges.map(edgeKey)),r.id+': required-edge inventory');
  assertions+=r.assertions.length;edges+=r.requiredEdges.length;
 }
 assert.equal(assertions,153);return{assertions,edges};
}
// This is explicit failed/unknown-state DISPOSAL, not oracle comparison. It may
// run only after the complete response file is saved. Never project or resume a
// self-reported failed collection, inconsistent boolean, or transport error.
export function assessSafety(bytes,status,call){
 try{
  const value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
  if(status!==200)return{envelope:value,safeToReuse:false,reason:'http-status-'+status,reportedPassed:value?.collection?.passed};
  if(value?.schemaVersion!==1||value.marker!=='NEXT_NATIVE_CONTEXT_INTERLEAVING_V1'||value.call!==call||value.method!=='GET')return{envelope:value,safeToReuse:false,reason:'unknown-response-envelope'};
  const c=value.collection;
  if(c?.passed!==true||Object.hasOwn(c,'error'))return{envelope:value,safeToReuse:false,reason:'collection-failed-or-unknown',reportedPassed:c?.passed,reportedError:c?.error};
  if(!Array.isArray(c.records)||c.records.length!==5||c.records.some(r=>r?.passed!==true||Object.hasOwn(r,'error')||!Array.isArray(r.assertions)||r.assertions.some(a=>a?.passed!==true)))return{envelope:value,safeToReuse:false,reason:'collection-self-report-inconsistent'};
  return{envelope:value,safeToReuse:true,reason:'explicit-positive-self-report'};
 }catch(error){return{safeToReuse:false,reason:'malformed-or-undecodable-response',error:String(error)};}
}
export function validate(value,call,contract){
 exact(value,['schemaVersion','marker','call','method','collection']);assert.equal(value.schemaVersion,1);assert.equal(value.marker,'NEXT_NATIVE_CONTEXT_INTERLEAVING_V1');assert.equal(value.call,call);assert.equal(value.method,'GET');
 return validateCollection(value.collection,call,contract,'actual-native-private-boundaries');
}
export function compare(actual,node,call,contract){
 validate(actual,call,contract);validateCollection(node,call,contract,'node-public-empty-store-projection');
 const ap=contextPublicProjection(actual.collection),np=contextPublicProjection(node);
 return ap.records.map((r,i)=>({call,id:r.id,classification:isDeepStrictEqual(r,np.records[i])?'matches-node-public-projection':'difference-requires-review',actualProjection:r,nodeProjection:np.records[i],actualFullRecord:actual.collection.records[i],nodeOriginalFullRecord:node.records[i]}));
}
export function parseOracle(text,contract){
 assert.equal(typeof text,'string');const frames=text.trim().split('\n').map(x=>JSON.parse(x));assert.equal(frames.length,7);const original=[],facade=[];
 for(let i=0;i<6;i++){const f=frames[i],call=i%3+1,variant=i<3?'node-original':'node-sealed-facade';exact(f,['kind','variant','call','observed']);assert.equal(f.kind,'whole-collection');assert.equal(f.variant,variant);assert.equal(f.call,call);validateCollection(f.observed,call,contract,'node-public-empty-store-projection');(i<3?original:facade).push(f.observed);}
 const summary=frames[6];assert.equal(summary.schemaVersion,1);assert.equal(summary.state,'CONTEXT_INTERLEAVING_NODE22_REFERENCE_AND_SEALED_FACADE_HOST_PASSED_V1');assert.equal(summary.passed,true);assert.equal(summary.collections,6);assert.equal(summary.controlsPerCollection,5);assert.deepEqual(summary.variants,['node-original','node-sealed-facade']);assert.deepEqual(summary.calls,[1,2,3]);
 assert.deepEqual(summary.selectedAssertionCounts,contract.map(r=>({id:r.id,assertions:r.assertionIds.length})));assert.equal(summary.nativeBoundaryParityClaimed,false);assert.equal(summary.guestOrEngineExecuted,false);assert.equal(summary.publicProjectionMatched,true);
 assert.equal(summary.maxPlannedWaits,Math.max(...frames.slice(0,6).map(f=>f.observed.peakPlannedWaits)));
 for(let i=0;i<3;i++)assert.deepEqual(contextPublicProjection(original[i]),contextPublicProjection(facade[i]));
 return{frames,values:original,facade,summary,hostAssertionsVerified:918};
}
