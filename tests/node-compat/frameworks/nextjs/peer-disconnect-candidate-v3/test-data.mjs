// Inert operation-state counterexamples; no AbortController, streams, resource,
// timers, socket, Node HTTP server or guest is instantiated/invoked by these tests.
import assert from 'node:assert/strict';
import {isObservedClosedOutput,mayReturnHandledClosed} from './policy.mjs';
let checks=0;
const raw={payload:{tag:'closed'}},other={payload:{tag:'closed'}};
const state={observed:true,raw,caught:raw,tag:'closed',responseSet:true};
assert.equal(isObservedClosedOutput(state),true);checks++;
for(const delta of [{observed:false},{raw:other},{caught:other},{tag:undefined},{tag:'last-operation-failed'},
 {tag:'unknown'},{responseSet:false}]){assert.equal(isObservedClosedOutput({...state,...delta}),false);checks++;}
for(const value of [undefined,null,false,0,'',NaN]) {
 assert.equal(isObservedClosedOutput({observed:true,raw:value,caught:value,tag:undefined,responseSet:true}),false);checks++;
}
const valid={classified:true,cancelReturned:true,readerReleased:true,cleanupReturned:true,requestAborted:true,fatalSet:false};
assert.equal(mayReturnHandledClosed(valid),true);checks++;
for(const key of ['classified','cancelReturned','readerReleased','cleanupReturned','requestAborted']) {
 for(const value of [false,undefined,null]){assert.equal(mayReturnHandledClosed({...valid,[key]:value}),false);checks++;}
}
for(const value of [true,undefined,null]){assert.equal(mayReturnHandledClosed({...valid,fatalSet:value}),false);checks++;}
console.log(JSON.stringify({schemaVersion:1,sourceOnly:true,pureDataChecks:checks,
 operationStateDataOnly:true,actualAbortControllerOrRequestOrResourceOrStreamInvoked:false,
 guestOrNodeHttpOrNetworkOrNativeOrCompilerExecuted:false,actualGuestAssertions:0}));
