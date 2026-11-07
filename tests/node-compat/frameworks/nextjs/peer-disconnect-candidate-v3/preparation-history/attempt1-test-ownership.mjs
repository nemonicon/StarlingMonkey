// Actual function-text control-flow seam with inert callbacks and Symbol DATA.
// No Web/WASI resource object, actual allocator/AbortController, I/O or guest runs.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const here=fileURLToPath(new URL('.',import.meta.url));
function extract(path){const source=readFileSync(path,'utf8'),start=source.indexOf('async function handleResources(incoming, outparam) {');
 assert(start>=0);const end=source.indexOf('\n  }\n  return {\n    handle',start);assert(end>start);
 return source.slice(start,end+4);}
async function observe(path){
 const incoming=Symbol('owned-incoming-data'),outparam=Symbol('owned-outparam-data'),marker=Symbol('inert-allocation-throw');
 const drops=[],events=[];
 const drop=(value,kind)=>{if(value!==undefined)drops.push({value,kind});};
 const state={emit(_record,phase){events.push(phase);}};
 function inertAllocation(){throw marker;}
 // Explicit lexical parameters, never module/global rebinding. The exact old/new
 // function executes only until the inert allocation callback and its own finally.
 const instantiate=new Function('drop','state','types','AbortController','streamError','streamFailure','isObservedClosedOutput','mayReturnHandledClosed',
  'return ('+extract(path)+');');
 const fn=instantiate(drop,state,{},inertAllocation,()=>undefined,value=>value,()=>false,()=>false);
 let caught,caughtSet=false;
 try{await fn(incoming,outparam);}catch(error){caughtSet=true;caught=error;}
 assert(caughtSet);assert.equal(caught,marker);
 return{drops:drops.map(x=>x.value===incoming?'incoming':x.value===outparam?'outparam':'unknown'),events};
}
const old=await observe(here+'../peer-disconnect-candidate-v2/adapter-diagnostic.mjs');
const current=await observe(here+'adapter-diagnostic.mjs');
assert.deepEqual(old.drops,[]);assert.deepEqual(old.events,[]);
assert.deepEqual(current.drops,['outparam','incoming']);
assert(current.events.includes('adapter-failed'));assert(current.events.includes('adapter-finally-returned'));
console.log(JSON.stringify({schemaVersion:1,sourceOnly:true,actualFunctionTextUsed:true,
 inertAllocationThrowsPreserved:true,oldCleanupCallbacks:old.drops,newCleanupCallbacks:current.drops,
 guestOrRealAbortControllerOrResourceOrFaultOrNetworkInvoked:false,actualGuestAssertions:0}));
