// Pure validation of durably captured whole strings. No private module, fixture,
// native API, clock, helper or process is imported/invoked here.
import assert from 'node:assert/strict';
import {validateSnapshot} from '../combined-clock-diagnostics-candidate-v1/validate-snapshot.mjs';
const keys = (v, names) => assert.deepEqual(Object.keys(v).sort(), [...names].sort());
const u64 = value => { assert.equal(typeof value, 'string'); assert(/^(0|[1-9][0-9]*)$/.test(value)); const n=BigInt(value); assert(n<=18446744073709551615n); return n; };
const i64 = value => { assert.equal(typeof value, 'string'); assert(/^(0|-?[1-9][0-9]*)$/.test(value)); const n=BigInt(value); assert(n>=-9223372036854775808n&&n<=9223372036854775807n); return n; };
const parse = raw => { assert.equal(typeof raw, 'string'); return JSON.parse(raw); };
function stats(v) { keys(v,['constructed','invalidated','destroyed','unexpectedRun','unexpectedCancel']); for(const n of Object.values(v))u64(n); return v; }
export function collectSelectorProbe(raw, expectedCount) {
  assert(Number.isInteger(expectedCount)&&expectedCount>=1&&expectedCount<=8);
  const v=parse(raw); keys(v,['schemaVersion','requestedCount','diagnosticOnly','selectedNone','actualEngineQueueUsed','selectorOnly','naturalEventLoopSettlementObserved','hostPollableResourcesCreated','timerResourceDropsObserved','before','queued','after','probeBefore','probeAfter']);
  assert.equal(v.schemaVersion,2);assert.equal(v.requestedCount,expectedCount);
  for(const k of ['diagnosticOnly','selectedNone','actualEngineQueueUsed','selectorOnly'])assert.equal(v[k],true);
  for(const k of ['naturalEventLoopSettlementObserved','hostPollableResourcesCreated','timerResourceDropsObserved'])assert.equal(v[k],false);
  const a=validateSnapshot(JSON.stringify(v.before)),q=validateSnapshot(JSON.stringify(v.queued)),b=validateSnapshot(JSON.stringify(v.after));
  for(const s of [q,b]) {
    assert.equal(s.currentCallSerial,a.currentCallSerial); assert.deepEqual(s.afterLoop,a.afterLoop);assert.deepEqual(s.afterPostCall,a.afterPostCall);
    assert.deepEqual(s.timerLeases,a.timerLeases);assert.equal(s.eventSerial,a.eventSerial);
  }
  assert.equal(a.current.queued,'0');assert.equal(q.current.queued,String(expectedCount));assert.equal(b.current.queued,'0');
  for(const s of [a,q,b]) { assert.equal(s.current.interest,1);assert.equal(s.current.loopRunning,false);assert.equal(s.current.timerRegistry,'0');assert.equal(s.current.immediateCacheOwned,a.current.immediateCacheOwned); }
  const n=BigInt(expectedCount);
  for(const name of Object.keys(a.counters)) {
    const aq=u64(q.counters[name])-u64(a.counters[name]),qb=u64(b.counters[name])-u64(q.counters[name]);
    assert.equal(aq,name==='queueEnqueue'?n:0n,'enqueue/invalidation prefix:'+name);
    assert.equal(qb,name==='prunedInvalid'?n:['selectorCall','selectorEmpty'].includes(name)?1n:0n,'one selector-only call:'+name);
  }
  stats(v.probeBefore);stats(v.probeAfter);
  for(const name of Object.keys(v.probeBefore))assert.equal(u64(v.probeAfter[name])-u64(v.probeBefore[name]),['constructed','invalidated','destroyed'].includes(name)?n:0n,'native sentinel lifetime:'+name);
  return {record:v,selectorBranchObserved:true,naturalEventLoopSettlementObserved:false,timerResourceDropObserved:false,hostStoreDeathObserved:false,fullLifecycleGateAccepted:false};
}
export function collectClockState(raw, previous=null) {
  const v=parse(raw);keys(v,['schemaVersion','diagnosticOnly','currentCallSerial','recordingComplete','hostStoreDeathObserved','resumeEpochObserved','clock','performance','embedding']);
  assert.equal(v.schemaVersion,2);assert.equal(v.diagnosticOnly,true);assert.equal(v.recordingComplete,true);
  assert.equal(v.hostStoreDeathObserved,false);assert.equal(v.resumeEpochObserved,false);u64(v.currentCallSerial);
  const c=v.clock;keys(c,['overflow','monotonicSamplePresent','adjustmentOverflow','wizenSamplePresent','offsetNs','monotonicCalls','lastMonotonicRawNs','lastOffsetAppliedNs','lastMonotonicAdjustedNs','wizenTransitions','lastWizenRawNs','lastWizenOffsetBeforeNs','lastWizenOffsetAfterNs']);
  assert.equal(c.overflow,false);assert.equal(c.adjustmentOverflow,false);
  for(const k of ['monotonicSamplePresent','wizenSamplePresent'])assert.equal(typeof c[k],'boolean');
  const numericNames=Object.keys(c).filter(k=>!['overflow','monotonicSamplePresent','adjustmentOverflow','wizenSamplePresent'].includes(k));
  const nc=Object.fromEntries(numericNames.map(k=>[k,u64(c[k])]));
  assert.equal(c.monotonicSamplePresent,nc.monotonicCalls>0n);assert.equal(c.wizenSamplePresent,nc.wizenTransitions>0n);
  if(c.monotonicSamplePresent) { assert(nc.lastMonotonicRawNs+nc.lastOffsetAppliedNs<=18446744073709551615n);assert.equal(nc.lastMonotonicAdjustedNs,nc.lastMonotonicRawNs+nc.lastOffsetAppliedNs);assert(nc.lastOffsetAppliedNs<=nc.offsetNs); }
  else for(const k of ['lastMonotonicRawNs','lastOffsetAppliedNs','lastMonotonicAdjustedNs'])assert.equal(nc[k],0n);
  if(c.wizenSamplePresent) { assert.equal(nc.lastWizenOffsetAfterNs,nc.lastWizenOffsetBeforeNs>nc.lastWizenRawNs?nc.lastWizenOffsetBeforeNs:nc.lastWizenRawNs);assert.equal(nc.offsetNs,nc.lastWizenOffsetAfterNs); }
  else for(const k of ['offsetNs','lastWizenRawNs','lastWizenOffsetBeforeNs','lastWizenOffsetAfterNs'])assert.equal(nc[k],0n);
  const p=v.performance;keys(p,['originPresent','originCount','periodNumerator','periodDenominator']);assert.equal(typeof p.originPresent,'boolean');i64(p.originCount);assert(u64(p.periodNumerator)>0n&&u64(p.periodDenominator)>0n);if(!p.originPresent)assert.equal(p.originCount,'0');
  const e=v.embedding;keys(e,['callEntries','firstCallClears','originEmplacements','entryObserved','lastEntryHadFirstCall','lastEntryHadClocks']);
  for(const k of ['entryObserved','lastEntryHadFirstCall','lastEntryHadClocks'])assert.equal(typeof e[k],'boolean');
  const calls=u64(e.callEntries),clears=u64(e.firstCallClears),origins=u64(e.originEmplacements);
  assert.equal(calls,u64(v.currentCallSerial));assert.equal(e.entryObserved,calls>0n);assert(origins<=clears&&clears<=calls);
  assert.equal(p.originPresent,origins>0n); // checks future actual shared state/link identity
  if(!e.entryObserved) {assert.equal(e.lastEntryHadFirstCall,false);assert.equal(e.lastEntryHadClocks,false);}
  if(e.lastEntryHadFirstCall)assert(clears>0n);
  if(previous) { // SAME retained instance only; never compare unrelated fresh epochs.
    assert(calls>=u64(previous.embedding.callEntries));assert(nc.monotonicCalls>=u64(previous.clock.monotonicCalls));assert(nc.wizenTransitions>=u64(previous.clock.wizenTransitions));assert(nc.offsetNs>=u64(previous.clock.offsetNs));
    if(c.wizenTransitions===previous.clock.wizenTransitions)assert.equal(c.offsetNs,previous.clock.offsetNs);
  }
  return {record:v,nativeOffsetValueObserved:true,wizenTransitionRecorded:c.wizenSamplePresent,explicitResumeEpochObserved:false,exactHostEpochClaim:false,hostStoreDeathObserved:false,fullLifecycleGateAccepted:false};
}
