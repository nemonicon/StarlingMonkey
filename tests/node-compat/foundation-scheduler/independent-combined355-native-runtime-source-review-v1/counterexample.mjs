// Synthetic DATA only. Imports authenticated pure models, never runtime/API/guest.
import assert from 'node:assert/strict';
import {writeFile,readFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const source=new URL('../combined-native-runtime-candidate-v1/',import.meta.url);
const {fatalJcoEvidence}=await import(new URL('models.mjs',source));
const {captureSync,captureDiagnostics,observed}=await import(new URL('capture.mjs',source));
const descriptor=n=>({path:'/synthetic-no-action/'+n,sha256:'a'.repeat(64),bytes:1});
const component=descriptor('component.wasm'),own=descriptor('index.json');
const marker={schemaVersion:1,state:'COMBINED355_FATAL_PUBLIC_CALL_ARMED_V1',sourceIndex:own,component,fixtureId:'fatal',name:'run',args:[],moduleImportCompleted:true,publicExportAboutToBeInvoked:true};
const terminal={closed:true,ownedGroupGone:true,spawnError:null,timedOut:false,externalSignal:null,outputLimitExceeded:false,errors:[],signals:[],signalCount:0,status:1,signal:null,terminalExitZeroObserved:false};
const cases=[];
for(const message of ['RESOURCE_UNHANDLED_TIMER_CALLBACK','UNRELATED_STANDARD_SHIM_OR_BINDING_FAILURE']){
 const sequence={attempted:0,written:0},rows=[];let caught,present=false;
 try{await captureSync({invoke(){throw Error(message);},name:'run',args:[],write:(name,row)=>rows.push({name,row}),sequence,now:()=>0});}catch(error){caught=error;present=true;}
 assert(present&&caught.message===message);
 const typed=rows[0].row,record={original:observed(caught),capture:captureDiagnostics(sequence),expectedFatalClaim:false};
 const accepted=fatalJcoEvidence(terminal,marker,typed,record,component,own);
 cases.push({inventedCause:message,typed,record,accepted});
}
assert.deepEqual(cases[0].typed,cases[1].typed);
assert.deepEqual(cases[0].record,cases[1].record);
assert.equal(cases[1].accepted.typedThrowRetained,true);
for(const value of [null,undefined,0,false]){
 const rows=[],sequence={attempted:0,written:0};let saw=false;
 try{await captureSync({invoke(){throw value;},name:'run',args:[],write:(name,row)=>rows.push(row),sequence,now:()=>0});}catch(error){assert(Object.is(error,value));saw=true;}
 assert(saw);const accepted=fatalJcoEvidence(terminal,marker,rows[0],{capture:captureDiagnostics(sequence)},component,own);cases.push({inventedCause:'unrelated primitive '+String(value),typed:rows[0],accepted});
}
const result={schemaVersion:1,state:'FATAL_JCO_CAUSE_AMBIGUITY_SOURCE_COUNTEREXAMPLE_CONFIRMED',syntheticOnly:true,actualGuestOrShimExecuted:false,actualFailureObserved:false,expectedAndUnrelatedErrorRecordsIndistinguishable:true,unrelatedPostArmThrowsAccepted:5,cases};
await writeFile(new URL('./counterexample-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({state:result.state,unrelatedPostArmThrowsAccepted:5,operationalActionsInvoked:false}));
