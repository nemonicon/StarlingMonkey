// PREPARED ONLY. Run only after Root supplies original terminal/report and the
// independent Python intake has authenticated the exact full Source/DATA.
// Imports pure collectors/session/WAVE only; no application/helper/API action.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {plannedCalls,validateSession,validateWasmtime} from '../combined-native-runtime-candidate-v3/session-model.mjs';
import * as collectors from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';
import {terminalModel} from '../combined-native-runtime-candidate-v3/models.mjs';
import {parseScalarStringOutput} from '../clock-v13-runtime-candidate-v2/wave.mjs';
const P=dirname(fileURLToPath(import.meta.url)),json=async p=>JSON.parse(await readFile(p));
const input=await json(join(P,'intake-summary.json'));
assert.equal(input.originalRootTerminalSupplied,true,'No live/partial output inspection');
const sha=b=>createHash('sha256').update(b).digest('hex');let checks=0;
async function exact(row){const b=await readFile(row.path);assert.equal(b.length,row.bytes);assert.equal(sha(b),row.sha256);checks++;return b;}
const refs=await json(join(P,'../combined-native-runtime-candidate-v3/references.json')),fixture=(await json(refs.fixtureCatalogue.path)).fixtures.find(x=>x.id==='resource'),result=JSON.parse((await exact(input.result)).toString());
assert.equal(result.state,'COMBINED355_RUNTIME_COMPLETE_UNREVIEWED_V3');assert.equal(result.fixtureId,'resource');assert.deepEqual(result.sourceIndex,input.sourceIndex);assert.equal(result.sessions.length,5);checks+=4;
const actual={rawPublicStrings:0,runRecords:0,callbackObservations:0,newIds:0,retainedJcoRotations:0,freshJcoRotations:0,freshWasmtimeWithinExportRotations:0};
const childPids=new Set(),sessionRows=[],allRuns=[],callbackVector=[],registrationVector=[];
const mainRoot=input.actualOutputRoot;
for(let n=0;n<2;n++){
 const scenario=n===0?'retained':'fresh',session=result.sessions[n];assert.equal(session.host,'jco-standard-shim');assert.equal(session.scenario,scenario);
 const terminal=JSON.parse((await exact(session.terminal)).toString());terminalModel(terminal);assert(!childPids.has(terminal.pid));childPids.add(terminal.pid);
 assert.equal(terminal.executable,refs.node.path);assert.deepEqual(terminal.args,[join(P,'../combined-native-runtime-candidate-v3/entry.mjs').replace('/independent-combined355-resource-runtime-v3-results-review-v1/..',''), 'worker',JSON.stringify(input.runtimeConfig),scenario]);
 const child=JSON.parse((await exact(session.result)).toString());assert.equal(child.state,'COMBINED355_JCO_SESSION_COMPLETE_UNREVIEWED_V3');assert.equal(child.scenario,scenario);assert.equal(child.fixtureId,'resource');assert.deepEqual(child.sourceIndex,input.sourceIndex);assert.equal(child.rawAttempts,child.rawWritten);assert.equal(child.captureFailures,0);assert.deepEqual(child.finalProtectionErrors,[]);
 const count=scenario==='retained'?23:9;assert.equal(child.rawWritten,count);const rows=[];
 for(let i=0;i<count;i++)rows.push(await json(join(mainRoot,scenario,'raw',String(i+1).padStart(3,'0')+'.json')));
 const validated=validateSession(fixture,scenario,rows,collectors);assert.deepEqual(validated,child.validation);assert.deepEqual(validated,session.validation);
 const plan=plannedCalls('resource',scenario);assert.equal(plan.length,count);for(let i=0;i<count;i++){assert.deepEqual(rows[i].args,plan[i].args);assert.equal(rows[i].name,plan[i].name);assert.equal(rows[i].kind,'return');assert.equal(rows[i].observed.type,'string');assert.equal(typeof rows[i].observed.value,'string');}
 const before=collectors.validateResourceInspect(rows[0].observed.value),after=collectors.validateResourceInspect(rows.at(-1).observed.value),runs=collectors.validateResourceSequence(rows.slice(1,-1).map(x=>x.observed.value),scenario==='retained'?3:1);
 assert.deepEqual(before.state.counters,{inspect:1,run:0,validate:0,timerCallbacks:0,startedCases:0,completedCases:0});assert.deepEqual(before.state.registeredIds,[]);
 assert.equal(after.state.counters.inspect,2);assert.equal(after.state.counters.validate,0);assert.equal(after.state.counters.run,scenario==='retained'?21:7);assert.equal(after.state.counters.timerCallbacks,scenario==='retained'?42:14);assert.equal(after.state.registeredIds.length,scenario==='retained'?138:46);
 actual.rawPublicStrings+=count;actual.runRecords+=runs.length;actual.callbackObservations+=validated.callbackObservations;actual.newIds+=validated.newIds;actual[scenario==='retained'?'retainedJcoRotations':'freshJcoRotations']+=scenario==='retained'?3:1;
 for(const v of runs){allRuns.push(v);callbackVector.push(v.after.counters.timerCallbacks-v.before.counters.timerCallbacks);registrationVector.push(v.after.registeredIds.length-v.before.registeredIds.length);}
 const stdout=JSON.parse((await exact(terminal.stdout)).toString());assert.equal(stdout.root,join(mainRoot,scenario));assert.equal(stdout.completeUnreviewed,true);assert.deepEqual(stdout.index,{...session.index,path:'index.json'});assert.deepEqual(stdout.completion,{...session.completion,path:'completion.json'});
 sessionRows.push({host:'jco',scenario,pid:terminal.pid,publicStrings:count,runRecords:runs.length,validation:validated,initialCounters:before.state.counters,finalCounters:after.state.counters,finalRegisteredIdObservations:after.state.registeredIds.length});checks+=17+count*5;
}
for(let n=0;n<3;n++){
 const session=result.sessions[n+2];assert.equal(session.host,'stock-wasmtime42');assert.equal(session.fresh,true);assert.equal(session.literalInvoke,'validate()');
 const terminal=JSON.parse((await exact(session.terminal)).toString());terminalModel(terminal);assert(!childPids.has(terminal.pid));childPids.add(terminal.pid);assert.equal(terminal.executable,refs.wasmtime.path);assert.deepEqual(terminal.args,['run','--invoke','validate()',input.component.path]);
 const bytes=await exact(terminal.stdout),raw=parseScalarStringOutput({stdoutBytes:bytes,rawDurablyRetained:true}),decoded=await json(join(mainRoot,'wasmtime-'+n+'.decoded.json'));
 assert.equal(decoded.returnedType,'string');assert.equal(decoded.value,raw);assert.deepEqual(decoded.rawStdout,terminal.stdout);
 const v=collectors.validateResourceWrapper(raw),validation=validateWasmtime(fixture,raw,decoded.hostWallBeforeMs,decoded.hostWallAfterMs,collectors);assert.deepEqual(validation,session.validation);assert.deepEqual(validation.wholeWrapper,v);
 assert.deepEqual(v.before.state.counters,{inspect:1,run:0,validate:1,timerCallbacks:0,startedCases:0,completedCases:0});assert.deepEqual(v.before.state.registeredIds,[]);assert.deepEqual(v.after.state.counters,{inspect:2,run:7,validate:1,timerCallbacks:14,startedCases:7,completedCases:7});assert.equal(v.after.state.registeredIds.length,46);assert.deepEqual(v.records.map(r=>r.current),[1,2,3,4,5,6,7]);
 const runs=collectors.validateResourceSequence(v.records.map(r=>JSON.stringify(r)));for(const r of runs){allRuns.push(r);callbackVector.push(r.after.counters.timerCallbacks-r.before.counters.timerCallbacks);registrationVector.push(r.after.registeredIds.length-r.before.registeredIds.length);}
 actual.rawPublicStrings++;actual.runRecords+=runs.length;actual.callbackObservations+=14;actual.newIds+=46;actual.freshWasmtimeWithinExportRotations++;
 sessionRows.push({host:'stock-wasmtime42',fresh:true,pid:terminal.pid,publicStrings:1,runRecords:7,initialCounters:v.before.state.counters,finalCounters:v.after.state.counters,finalRegisteredIdObservations:46,withinOneExport:true,separateHostCallInterleavingProved:false});checks+=18;
}
assert.equal(childPids.size,5);assert.deepEqual(actual,{rawPublicStrings:35,runRecords:49,callbackObservations:98,newIds:322,retainedJcoRotations:3,freshJcoRotations:1,freshWasmtimeWithinExportRotations:3});assert.deepEqual(result.coverage,actual);checks+=3;
assert.deepEqual(callbackVector,Array.from({length:7},()=>collectors.CASE_CALLBACKS).flat());assert.deepEqual(registrationVector,Array.from({length:7},()=>collectors.CASE_IDS).flat());assert.deepEqual(allRuns.map(v=>v.caseId),Array.from({length:49},(_,i)=>i%7));checks+=3;
const cases=Array.from({length:7},(_,caseId)=>({caseId,runObservations:allRuns.filter(v=>v.caseId===caseId).length,callbackCounterIncrements:allRuns.filter(v=>v.caseId===caseId).reduce((n,v)=>n+v.after.counters.timerCallbacks-v.before.counters.timerCallbacks,0),newIdObservations:allRuns.filter(v=>v.caseId===caseId).reduce((n,v)=>n+v.after.registeredIds.length-v.before.registeredIds.length,0)}));assert(cases.every(x=>x.runObservations===7));checks++;
for(const field of ['expectedCallbackFailureProved','fatalCallbackGateSatisfied','fullSixFixturesAccepted','all17GatesSatisfied','nativeOffsetInterestDropOrTeardownProved','fullProfileAcceptance','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']){assert.equal(result[field],false);checks++;}
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_RETAINED_RESOURCE_RAW_DATA_SEMANTICS_PASSED',checks,coverage:actual,sessionRows,cases,typedNodeStrings:32,fullWaveStringsDecoded:3,distinctFreshOwnedChildren:5,allWholeValuesParsedWithoutClipping:true,allRunVectorsAndCountersValidated:true,timerIdUniquenessScope:'per component instance;322registration observations, no globalnumericIDuniqueness claim',nativeDropHandleGcOrBackendCountsObserved:false,crossHostExactWholeWrapperByteEqualityClaim:false,apiHelperOrGuestReruns:false}));
