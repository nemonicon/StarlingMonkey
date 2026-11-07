// Pure Source admission for a future collector, after durable body capture.
// This does no oracle comparison/projection and creates no timers or stores.
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function need(ok,message){if(ok!==true)throw new Error('UNREF_REUSE_INVALID_COLLECTION:'+message);}
export function validateUnrefCollection(value,phase,hostCase,boundaryMode,contract){
 need(contract?.schemaVersion===1&&contract.suite==='UNREF_ACROSS_ORDINARY_CALLS_V1','contract');
 const control=contract.controls[phase];need(!!control,'phase');
 need(typeof hostCase==='string'&&/^[A-Za-z0-9._-]{1,96}$/.test(hostCase),'Root case');
 need(['node-public-empty-store-projection','actual-native-private-boundaries'].includes(boundaryMode),'boundary policy');
 const keys=[...contract.requiredKeys,...(phase==='C'?['finalCleanup']:[])].sort();
 need(value!==null&&typeof value==='object'&&equal(Object.keys(value).sort(),keys),'exact fields');
 for(const [k,v] of Object.entries(contract.requiredConstants))need(equal(value[k],v),'constant '+k);
 need(value.phase===phase&&value.ordinal===control.ordinal,'phase/ordinal');
 need(value.firstHostCase===hostCase&&value.requestedHostCase===hostCase,'same first host case');
 need(value.boundaryMode===boundaryMode,'actual boundary');
 for(const field of ['checks','callbackChecks']){
  const rows=value[field];need(Array.isArray(rows),'array '+field);
  need(equal(rows.map(r=>r.id),control[field+'Ids']),'exact '+field+' inventory');
  need(rows.every(r=>equal(Object.keys(r).sort(),['id','passed'])&&r.passed===true),'true DATA '+field);
 }
 need(equal(value.counts,control.counts),'callback counts');
 need(equal(value.plannedHandles,control.plannedHandles),'local planned handle accounting');
 need(Array.isArray(value.observations)&&value.observations.length===control.observations.length,'observation inventory');
 for(let i=0;i<control.observations.length;i++){
  const actual=value.observations[i],expected=control.observations[i];
  need(equal(Object.keys(actual).sort(),['firstIdentity','firstLabel','id','ordinal','phase','secondIdentity','secondLabel','sequence']),'observation fields');
  need(actual.firstIdentity===true&&actual.secondIdentity===true,'actual marker identities');
  for(const k of ['sequence','id','phase','ordinal','firstLabel','secondLabel'])need(actual[k]===expected[k],'Source observation '+k);
 }
 if(phase==='C')need(equal(value.finalCleanup,contract.finalCleanup),'final explicit cleanup');
 return true;
}
