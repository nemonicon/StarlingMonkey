// Prepared retained-DATA validator. Never imports generated/application modules.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {plannedCalls,validateSession,validateWasmtime} from '../combined-native-runtime-candidate-v3/session-model.mjs';
import {terminalModel,realtimeBracket} from '../combined-native-runtime-candidate-v3/models.mjs';
import * as collectors from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';
import {parseScalarStringOutput} from '../clock-v13-runtime-candidate-v2/wave.mjs';
const P=dirname(fileURLToPath(import.meta.url)),json=async p=>JSON.parse(await readFile(p));
const intake=await json(join(P,'intake-summary.json'));
assert.equal(intake.originalRootTerminalSupplied,true,'Do not inspect live or partial output');
assert.equal(intake.state,'INDEPENDENT_CLOCK_SNAPSHOT_RUNTIME_V3_ACTUAL_READ_ONLY_INTAKE_PASSED');
const sha=b=>createHash('sha256').update(b).digest('hex');let checks=0;
async function exact(row){const b=await readFile(row.path);assert.equal(b.length,row.bytes);assert.equal(sha(b),row.sha256);checks++;return b;}
const refs=await json(join(P,'../combined-native-runtime-candidate-v3/references.json')),fixture=(await json(refs.fixtureCatalogue.path)).fixtures.find(x=>x.id==='clock-snapshot'),result=JSON.parse((await exact(intake.result)).toString()),root=intake.actualOutputRoot;
assert.equal(result.state,'COMBINED355_RUNTIME_COMPLETE_UNREVIEWED_V3');assert.equal(result.fixtureId,'clock-snapshot');assert.deepEqual(result.sourceIndex,intake.sourceIndex);assert.equal(result.sessions.length,5);checks+=4;
const values=[],sessions=[],pids=new Set();
for(let n=0;n<2;n++){
 const scenario=n===0?'retained':'fresh',session=result.sessions[n],count=n===0?3:1;assert.equal(session.host,'jco-standard-shim');assert.equal(session.scenario,scenario);
 const t=JSON.parse((await exact(session.terminal)).toString());terminalModel(t);assert(!pids.has(t.pid));pids.add(t.pid);assert.equal(t.executable,refs.node.path);assert.deepEqual(t.args,[join(P,'../combined-native-runtime-candidate-v3/entry.mjs'),'worker',JSON.stringify(intake.runtimeConfig),scenario]);
 const child=JSON.parse((await exact(session.result)).toString());assert.equal(child.state,'COMBINED355_JCO_SESSION_COMPLETE_UNREVIEWED_V3');assert.equal(child.fixtureId,'clock-snapshot');assert.equal(child.scenario,scenario);assert.deepEqual(child.sourceIndex,intake.sourceIndex);assert.equal(child.rawAttempts,count);assert.equal(child.rawWritten,count);assert.equal(child.captureFailures,0);assert.deepEqual(child.finalProtectionErrors,[]);
 const raw=[];for(let i=1;i<=count;i++)raw.push(await json(join(root,scenario,'raw',String(i).padStart(3,'0')+'.json')));
 const v=validateSession(fixture,scenario,raw,collectors);assert.deepEqual(v,child.validation);assert.deepEqual(v,session.validation);assert.equal(plannedCalls('clock-snapshot',scenario).length,count);
 const parentBracket=await json(join(root,'brackets',scenario+'.json'));assert.equal(parentBracket.coarseAllowanceMs,1);assert.equal(parentBracket.decreasingClockInconclusive,false);assert.equal(parentBracket.performanceTimeOriginEpochAssumed,false);
 let previous=null;const observed=[];
 for(let i=0;i<count;i++){
  const row=raw[i],value=collectors.validateClockSnapshot(row.observed.value,previous),wall=realtimeBracket(value,row.hostWallBeforeMs,row.hostWallAfterMs);
  assert.equal(value.calls,i+1);assert(row.hostWallBeforeMs>=parentBracket.before&&row.hostWallAfterMs<=parentBracket.after);assert.equal(value.initialization.jobs,1);assert.equal(value.initialization.moduleEvaluations,1);assert.equal(value.callbacks,1);assert.equal(value.initPerformanceCalled,false);
  values.push(value);observed.push({calls:value.calls,initialization:value.initialization,before:value.before,after:value.after,elapsed:value.elapsed,wallBracket:wall});previous=value;checks+=8;
 }
 const out=JSON.parse((await exact(t.stdout)).toString());assert.equal(out.root,join(root,scenario));assert.equal(out.completeUnreviewed,true);assert.deepEqual(out.index,{...session.index,path:'index.json'});assert.deepEqual(out.completion,{...session.completion,path:'completion.json'});
 sessions.push({host:'jco-standard-shim',scenario,pid:t.pid,publicStrings:count,callCounters:observed.map(x=>x.calls),values:observed});checks+=19;
}
for(let n=0;n<3;n++){
 const session=result.sessions[n+2];assert.equal(session.host,'stock-wasmtime42');assert.equal(session.fresh,true);assert.equal(session.literalInvoke,'run()');const t=JSON.parse((await exact(session.terminal)).toString());terminalModel(t);assert(!pids.has(t.pid));pids.add(t.pid);assert.equal(t.executable,refs.wasmtime.path);assert.deepEqual(t.args,['run','--invoke','run()',intake.component.path]);
 const raw=parseScalarStringOutput({stdoutBytes:await exact(t.stdout),rawDurablyRetained:true}),saved=await json(join(root,'wasmtime-'+n+'.decoded.json'));assert.equal(saved.returnedType,'string');assert.equal(saved.value,raw);assert.deepEqual(saved.rawStdout,t.stdout);
 const validation=validateWasmtime(fixture,raw,saved.hostWallBeforeMs,saved.hostWallAfterMs,collectors);assert.deepEqual(validation,session.validation);const value=collectors.validateClockSnapshot(raw);assert.deepEqual(validation.fullValue,value);assert.equal(value.calls,1);assert.equal(value.initialization.jobs,1);assert.equal(value.initialization.moduleEvaluations,1);assert.equal(value.callbacks,1);
 const bracket=await json(join(root,'brackets','wasmtime-'+n+'.json'));assert.equal(saved.hostWallBeforeMs,bracket.before);assert.equal(saved.hostWallAfterMs,bracket.after);assert.equal(bracket.coarseAllowanceMs,1);assert.equal(bracket.decreasingClockInconclusive,false);const wall=realtimeBracket(value,bracket.before,bracket.after);
 values.push(value);sessions.push({host:'stock-wasmtime42',fresh:true,pid:t.pid,publicStrings:1,callCounters:[1],values:[{calls:value.calls,initialization:value.initialization,before:value.before,after:value.after,elapsed:value.elapsed,wallBracket:wall}]});checks+=21;
}
assert.equal(pids.size,5);assert.equal(values.length,7);const coverage={jcoRetainedStrings:3,jcoFreshStrings:1,freshWasmtimeStrings:3};assert.deepEqual(result.coverage,coverage);checks+=3;
for(const key of ['expectedCallbackFailureProved','fatalCallbackGateSatisfied','nativeOffsetInterestDropOrTeardownProved','fullSixFixturesAccepted','all17GatesSatisfied','fullProfileAcceptance','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']){assert.equal(result[key],false);checks++;}
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_RETAINED_CLOCK_SNAPSHOT_RAW_DATA_SEMANTICS_PASSED',checks,coverage,sessions,wholeStrings:7,typedNodeStrings:4,fullWaveStringsDecoded:3,distinctFreshOwnedChildren:5,initializationPayloadsEqualAcrossAllObservedInstances:values.every(v=>JSON.stringify(v.initialization)===JSON.stringify(values[0].initialization)),allInitializationPayloads:values.map(v=>v.initialization),allWholeValuesParsedWithoutClipping:true,allDateSamplesWithinHostWholeCallBracketPlus1ms:true,retainedMonotonicAndTimeOriginContinuity:true,performanceTimeOriginEpochEquivalenceProved:false,nativeMonotonicOffsetOrResumptionProved:false,nativeDropHandleGcCountsObserved:false,crossHostClockValueEqualityClaim:false,apiHelperOrGuestReruns:false}));
