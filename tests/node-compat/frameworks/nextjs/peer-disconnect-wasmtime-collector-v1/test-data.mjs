// Inert DATA counterexamples only. No sockets, timers, streams or guest resources.
import assert from 'node:assert/strict';
import {analyze,parseDiagnosticLog,marker} from './classification.mjs';
let checks=0;
const label='data-only',firstLabel='data-first';
const event=(phase,fields={})=>({schemaVersion:1,marker,origin:'actual-wasi-guest',sequence:1,
 firstLabel,ordinal:3,label,route:'/upload',phase,context:null,...fields});
const record={label,clientCloseObserved:true,forcedClientCleanup:false,status:200};
const normal=[event('adapter-enter'),event('handler-enter',{signalAborted:false,requestSignalLinkedToPeer:false}),
 event('handler-finally'),event('output-write-invocation-attempt',{bytes:1}),event('output-write-returned'),
 event('outgoing-finish-returned'),event('adapter-finally-returned')];
const run=(events,kind='upload-close',r=record)=>analyze(r,events,{firstLabel,ordinal:3,kind});
assert.equal(run(normal).safeToRequestAgain,true);checks++;
for(const phase of ['adapter-enter','handler-enter','handler-finally','output-write-returned','outgoing-finish-returned','adapter-finally-returned']){
 assert.equal(run(normal.filter(e=>e.phase!==phase)).safeToRequestAgain,false);checks++;
}
assert.equal(run([...normal,event('adapter-failed')]).safeToRequestAgain,false);checks++;
assert.equal(run([...normal,event('dispose-failed',{resource:'incoming-request'})]).safeToRequestAgain,false);checks++;
assert.equal(run(normal.map(e=>({...e,firstLabel:'different-factory'}))).safeToRequestAgain,false);checks++;
assert.equal(run(normal.map(e=>({...e,ordinal:1}))).safeToRequestAgain,false);checks++;
assert.equal(run(normal,'upload-close',{...record,clientCloseObserved:false}).safeToRequestAgain,false);checks++;
assert.equal(run(normal,'upload-close',{...record,transportOrCollectionError:{type:'undefined'}}).safeToRequestAgain,false);checks++;
const barrier=event('input-read-invocation-attempt',{inputBytes:1024,hostReadEnteredOrBlockedProved:false});
const closeRecord={...record,synchronizedMilestone:barrier};
const eof=run([...normal,barrier,event('input-read-failed',{error:{payloadTag:'closed'}})],'upload-close',closeRecord);
assert.equal(eof.ioPathObserved,false);assert.equal(eof.coverageStatus,'inconclusive-closed-under-length-no-http-completion-proof');checks+=2;
const inputFailure=run([...normal,barrier,event('input-read-failed',{error:{payloadTag:'last-operation-failed'}}),
 event('handler-read-failed'),event('handler-body-finally'),event('adapter-failed')],'upload-close',closeRecord);
assert.equal(inputFailure.ioPathObserved,true);assert.equal(inputFailure.safeToRequestAgain,false);checks+=2;
assert.equal(run([...normal,event('input-read-failed',{error:{payloadTag:'last-operation-failed'}}),
 event('handler-read-failed'),event('handler-body-finally')]).ioPathObserved,false);checks++;
const outputRecord={...record,firstBodyBeforeClose:true};
assert.equal(run(normal,'output-close',outputRecord).ioPathObserved,false);checks++;
const output=[...normal,event('output-write-failed',{error:{payloadTag:'closed'}}),event('producer-cancel-returned'),
 event('response-reader-cancel-returned'),event('adapter-failed')];
assert.equal(run(output,'output-close',outputRecord).ioPathObserved,true);checks++;
assert.equal(run(output,'output-close',outputRecord).safeToRequestAgain,false);checks++;
assert.equal(run(output.map(e=>e.phase==='output-write-failed'?{...e,error:{type:'undefined'}}:e),'output-close',outputRecord).ioPathObserved,false);checks++;
const allowed=[...new Set(normal.map(e=>e.phase))];
assert.equal(parseDiagnosticLog(normal.map(e=>JSON.stringify(e)).join('\n')+'\n',allowed).events.length,normal.length);checks++;
assert.throws(()=>parseDiagnosticLog(JSON.stringify(event('unknown-phase'))+'\n',allowed));checks++;
assert.throws(()=>parseDiagnosticLog(JSON.stringify({marker,phase:'handler-enter'})+'\n',allowed));checks++;
assert.throws(()=>parseDiagnosticLog(JSON.stringify(event('handler-enter'))+'\n',allowed));checks++;
const validBody=Buffer.from(JSON.stringify({complete:true,received:8192,ordinal:3,readFailure:null,signalAborted:false})).toString('base64');
assert.equal(run(normal,'healthy-upload',{...record,decodedBodyBase64:validBody}).functionChecksPassed,true);checks++;
assert.equal(run(normal,'healthy-upload',{...record,decodedBodyBase64:Buffer.from('{}').toString('base64')}).functionChecksPassed,false);checks++;
console.log(JSON.stringify({sourceOnly:true,pureDataChecks:checks,guestResourceObjectsConstructed:false,
 actualCohortsOrClientsOrServerOrTimersInvoked:false,actualGuestAssertions:0}));
