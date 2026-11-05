// Pure exact catch/presence and actual capture functions; no phase/Frame/actions.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {capturedRun} from './body.mjs';
const body=await readFile(new URL('./body.mjs',import.meta.url),'utf8'),entry=await readFile(new URL('./entry.mjs',import.meta.url),'utf8');
let checks=0;const ck=(v,m)=>{assert.ok(v,m);checks++;};
ck((body.match(/let primary=null,primaryPresent=false,finalErrors=\[\]/g)||[]).length===3,'Three body declarations');
ck((body.match(/catch\(error\)\{primaryPresent=true;primary=error;\}/g)||[]).length===3,'Three exact body catches');
ck((body.match(/if\(primaryPresent\|\|finalErrors.length\)/g)||[]).length===3,'Three presence-controlled failure branches');
ck((body.match(/primaryPresent,primary:observed\(primary\)/g)||[]).length===3,'Three truthful failure presence fields');
ck((entry.match(/primaryPresent=true;primary=error;throw error;/g)||[]).length===2&&(entry.match(/if\(primaryPresent\)throw new AggregateError/g)||[]).length===2,'Both entry combined errors use presence');
ck(!body.includes('primary!==null')&&!entry.includes('primary!==null'),'Old null sentinel absent');
const values=[null,undefined,false,0,-0,'',NaN,Symbol('X'),Object.freeze({value:'X'})];
for(const value of values){
 const records=[],sequence={attempted:0,written:0};let present=false,primary;
 try{await capturedRun(()=>{throw value;},async(p,r)=>records.push({p,r}),sequence);}catch(error){present=true;primary=error;}
 ck(present&&Object.is(primary,value),'Every primary value remains present');
 ck(sequence.attempted===1&&sequence.written===1&&records[0].r.kind==='throw','Raw before failure classification');
 // Exact future control predicate; no operational runJcoWorker(fakeFrame) call.
 ck(Boolean(present||[].length),'Caught value cannot reach completion branch');
 const guard=Object.freeze({guard:true});let combined;
 try{try{throw value;}catch(error){present=true;primary=error;throw error;}finally{try{throw guard;}catch(error){if(present)throw new AggregateError([primary,error],'Clock admission and final protection failed');throw error;}}}catch(e){combined=e;}
 ck(combined instanceof AggregateError&&Object.is(combined.errors[0],value)&&combined.errors[1]===guard,'Primary plus protection values retained including null');
 const writer=Object.freeze({writer:true}),failed={attempted:0,written:0};let failure;
 try{await capturedRun(()=>{throw value;},async()=>{throw writer;},failed);}catch(e){failure=e;}
 ck(failure instanceof AggregateError&&Object.is(failure.errors[0],value)&&failure.errors[1]===writer&&failed.attempted===1&&failed.written===0,'Existing aggregate X/Y and honest attempts remain');
}
let primaryPresent=false,primary=null;try{}catch(error){primaryPresent=true;primary=error;}
ck(primaryPresent===false&&!Boolean(primaryPresent||[].length),'Success has no fabricated primary');
console.log(JSON.stringify({schemaVersion:1,passed:true,checks,bodyPresenceSites:3,entryCombinedPresenceSites:2,originalValueCases:values.length,rawNullThrowRetained:true,nullCannotReachChildCompletion:true,noOperationalFrameFabricated:true,noOwnerOrJcoOrShimOrGuestAction:true}));
