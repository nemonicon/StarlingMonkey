// Pure models for the exact existing sealed result-contract layouts.
import {need,integer} from './planner.mjs';
export function stable(value){
 if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
 if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stable(value[k])).join(',')+'}';
 return JSON.stringify(value);
}
export const same=(a,b)=>stable(a)===stable(b);
export function providerComparisons(rows){
 const native=rows['native-on'],on=rows['fflate-on'],off=rows['fflate-off'];
 need(native&&on&&off&&same(native.nativeEngine,on.nativeEngine)&&same(native.metadata,on.metadata),'same actual ON engine/metadata for provider comparison');
 need(off.nativeEngine.sha256!==on.nativeEngine.sha256,'separate OFF engine');
 need(off.code.sha256===on.code.sha256&&off.code.bytes===on.code.bytes,'identical FF bundle BYTES across distinct per-arm paths');return true;
}
export function descriptorsIn(value){const rows=[],seen=new Set();let nodes=0;
 function walk(v){if(!v||typeof v!=='object')return;need(++nodes<=1048576,'finite descriptor traversal');
  if(typeof v.path==='string'&&typeof v.sha256==='string'&&Number.isSafeInteger(v.bytes)){
   const r={path:v.path,sha256:v.sha256,bytes:v.bytes},key=stable(r);if(!seen.has(key)){seen.add(key);rows.push(r);}}
  for(const child of Object.values(v))walk(child);
 }walk(value);return rows;
}
export function contractModel(data,contract,indexRows){
 need(data?.schemaVersion===1&&data.verifiedPassed===true&&contract.requiredReviewState===data.state,'actual result/contract state');
 for(const[key,wanted]of Object.entries(contract.requiredFixedValues??{}))need(same(data[key],wanted),'immutable fixed field '+key);
 for(const[key,wanted]of Object.entries(contract.requiredCoverage??{}))need(same(data.coverage?.[key],wanted),'finite coverage '+key);
 const bound=[...descriptorsIn(data),...indexRows];
 for(const[key,wanted]of Object.entries(contract.requiredExactDescriptors??{}))need(bound.some(row=>same(row,wanted)),'exact descriptor bound in result or its index '+key);
 const components=data.components??data.requiredComponents,artifacts=data.actualComponentReviews??data.requiredActualComponentReviews;
 if(contract.requiredComponents)need(same(components,contract.requiredComponents),'actual three components');
 if(contract.requiredActualComponentReviews)need(same(artifacts,contract.requiredActualComponentReviews),'actual artifact reviews');
 return{components,artifacts};
}
export function quietWindowModel(value,{runId,sourceSha,phase,nowUtcMs,globalBudgetMs}){
 need(value?.schemaVersion===1&&value.state==='ROOT_COORDINATED_CODEC_MEASUREMENT_QUIET_WINDOW_V1'&&value.exclusiveMeasurementApproved===true,'new Root coordinated quiet-window DATA');
 need(value.runId===runId&&value.sourceIndexSha256===sourceSha&&value.phase===phase,'exact quiet window/source/phase');
 const parse=s=>{need(typeof s==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(s),'canonical UTC window');const ms=Date.parse(s);need(Number.isFinite(ms)&&new Date(ms).toISOString()===s,'valid UTC window');return ms;};
 const start=parse(value.startsAtUtc),end=parse(value.expiresAtUtc);integer(globalBudgetMs,1,86400000,'preselected global phase bound');
 need(end>start&&end-start<=86400000&&nowUtcMs>=start&&nowUtcMs<end,'active finite declared quiet window');
 need(end-nowUtcMs>=globalBudgetMs,'quiet window must fit full preselected global budget');return{start,end};
}
