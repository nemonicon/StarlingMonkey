// Targeted host pure DATA only; no native ledger replay or target execution.
import assert from 'node:assert/strict';
import {observeScalarCall} from './worker.mjs';
let cases=0;
for(const thrown of [NaN,Infinity,-Infinity]){
 const records=[];const out={root:'/synthetic',write:async(name,value)=>{const data=JSON.parse(JSON.stringify(value));records.push({name,data});return{path:name,sha256:'0'.repeat(64),bytes:1};}};
 const detail={callAttempts:0,callReturns:0,callThrows:0,ordinaryGuestCalls:0,stringReturns:0,rawStrings:[],rawThrowCaptureFailures:[]};
 let caught=false;try{await observeScalarCall(out,detail,1,()=>{throw thrown;});}catch(e){caught=true;assert(Object.is(e,thrown));}
 assert(caught&&detail.callThrows===1&&detail.rawThrowCaptureFailures.length===0);const raw=records.find(r=>r.name==='raw-throw-1.json');assert(raw.data.nonfinite===true&&raw.data.diagnostic===String(thrown));cases++;
}
console.log(JSON.stringify({schemaVersion:1,pureNonfiniteThrowCases:cases,originalPrimitivePreserved:true,receiptsJsonSafe:true,guestOrCryptoExecuted:false}));
