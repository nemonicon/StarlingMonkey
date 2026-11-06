// Whole retained failure DATA only; actual exported pure classifier, no runtime.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {fatalJcoObservation,terminalModel} from '../combined-native-runtime-candidate-v3/models.mjs';
const P=dirname(fileURLToPath(import.meta.url)),json=async p=>JSON.parse(await readFile(p));
const intake=await json(join(P,'intake-summary.json'));assert.equal(intake.originalRootTerminalSupplied,true);assert.equal(intake.state,'INDEPENDENT_FATAL_V3_ACTUAL_FAILURE_READ_ONLY_INTAKE_PASSED');
const sha=b=>createHash('sha256').update(b).digest('hex');let checks=0;
async function exact(d){const b=await readFile(d.path);assert.equal(b.length,d.bytes);assert.equal(sha(b),d.sha256);checks++;return b;}
const rows=intake.actualPartialFiles,j=JSON.parse((await exact(intake.childTerminals['jco-fatal'])).toString()),w=JSON.parse((await exact(intake.childTerminals['wasmtime-fatal'])).toString()),marker=JSON.parse((await exact(rows['fatal-jco/fatal-armed.json'])).toString()),typed=JSON.parse((await exact(rows['fatal-jco/raw/001.json'])).toString()),caught=JSON.parse((await exact(rows['fatal-jco/caught-failure.json'])).toString());
const actual=fatalJcoObservation(j,marker,typed,caught,intake.component,intake.sourceIndex);
assert.deepEqual(actual,{reachedBeforeCallMarker:true,typedThrowRetained:true,nativeAbortObserved:false,workerFinallyExecutionProved:false,observedInvocationFailure:true,callbackCause:'inconclusive',expectedCallbackFailureProved:false,fatalCallbackGateSatisfied:false,nativeCallbackReachedObserved:false,uniqueOriginalJsErrorIdentityProved:false});checks++;
assert.equal(j.status,1);assert.equal(j.signal,null);assert.equal(w.status,134);assert.equal(w.signal,null);terminalModel(w,{failureObservation:true});checks+=5;
assert.deepEqual(typed.observed,{type:'object',opaque:true,fullOpaqueValueClaim:false});assert.deepEqual(caught.original,typed.observed);assert.deepEqual(caught.capture,{attempted:1,written:1,captureFailures:[]});checks+=3;
const stderr=(await exact(w.stderr)).toString(),parent=(await exact((await json(intake.externalParentTerminal.path)).stderr)).toString();
const expression="stderr.includes('RESOURCE_UNHANDLED_TIMER_CALLBACK')&&!/unknown import|failed to instantiate|no export/i.test(stderr)";
const source=await readFile(join(P,'../combined-native-runtime-candidate-v3/runtime.mjs'),'utf8');assert(source.includes(expression));
const predicate=text=>text.includes('RESOURCE_UNHANDLED_TIMER_CALLBACK')&&!/unknown import|failed to instantiate|no export/i.test(text);
assert.equal(predicate(stderr),false);assert(stderr.includes('unreachable'));assert(!stderr.includes('RESOURCE_UNHANDLED_TIMER_CALLBACK'));assert(parent.includes('WT fatal identity/reach evidence pending if diagnostic absent; nonzero alone never enough'));checks+=5;
const failures=[],clone=x=>JSON.parse(JSON.stringify(x));
function reject(name,change){const v=[clone(j),clone(marker),clone(typed),clone(caught),clone(intake.component),clone(intake.sourceIndex)];change(v);assert.throws(()=>fatalJcoObservation(...v));failures.push(name);}
reject('missing armed marker',v=>v[1]=null);
reject('wrong component identity',v=>v[1].component.sha256='0'.repeat(64));
reject('wrong source identity',v=>v[1].sourceIndex.sha256='0'.repeat(64));
reject('module import not completed',v=>v[1].moduleImportCompleted=false);
reject('not armed before public call',v=>v[1].publicExportAboutToBeInvoked=false);
reject('ordinary return is not fatal evidence',v=>v[2].kind='return');
reject('missing typed throw on raw1',v=>v[2]=null);
reject('typed capture not written',v=>v[3].capture.written=0);
reject('capture write failure',v=>v[3].capture.captureFailures=[{type:'object'}]);
reject('timeout is not expected failure',v=>v[0].timedOut=true);
reject('signalled child is not expected failure',v=>v[0].signals=['SIGTERM']);
reject('raw0 is not expected failure',v=>{v[0].status=0;v[0].terminalExitZeroObserved=true;});
for(const observed of [{type:'string',value:'generic failure'},{type:'undefined'},typed.observed]){const v=clone(typed);v.observed=observed;const a=fatalJcoObservation(j,marker,v,caught,intake.component,intake.sourceIndex);assert.equal(a.callbackCause,'inconclusive');assert.equal(a.expectedCallbackFailureProved,false);assert.equal(a.fatalCallbackGateSatisfied,false);failures.push('generic thrown '+observed.type+' never proves callback cause');}
const abort={...j,status:null,signal:'SIGABRT'};const a=fatalJcoObservation(abort,marker,null,null,intake.component,intake.sourceIndex);assert.equal(a.nativeAbortObserved,true);assert.equal(a.callbackCause,'inconclusive');assert.equal(a.expectedCallbackFailureProved,false);failures.push('synthetic native SIGABRT remains inconclusive');
for(const text of ['wasm trap: unreachable','RESOURCE_UNHANDLED_TIMER_CALLBACK unknown import','RESOURCE_UNHANDLED_TIMER_CALLBACK failed to instantiate','RESOURCE_UNHANDLED_TIMER_CALLBACK no export']){assert.equal(predicate(text),false);failures.push('WT absence/startup diagnostic not fatal identity');}
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_FATAL_FAILURE_DATA_AND_PURE_CLASSIFIER_VALIDATED',checks,actualJcoClassification:actual,wasmtime:{rawExitCode:w.status,signal:w.signal,sourceSpecificDiagnosticObserved:false,genericUnreachableObserved:true,callbackCause:'inconclusive',nativeCallbackReachedObserved:false,uniqueOriginalJsErrorIdentityProved:false},parentPredicateAccepted:false,parentRefusalMessage:'WT fatal identity/reach evidence pending if diagnostic absent; nonzero alone never enough',counterexamples:failures.length,cases:failures,actualOpaqueThrowRetained:true,fullOpaqueObjectOrErrorIdentityClaim:false,apiHelperOrGuestReruns:false}));
