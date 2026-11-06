// Synthetic synchronous resource API double ONLY. No native/async proof.
import assert from 'node:assert/strict';
import {createAsyncLocalStorage} from './after/builtins/node-compat/async-local-storage-factory.mjs';
let current={bindings:new Map()};
const kernel={
 createState:()=>({enabled:false}),
 enabled:s=>s.enabled,setEnabled:(s,v)=>{s.enabled=v;},
 get:(s,raw)=>raw||s.enabled?current.bindings.get(s):undefined,
 set:(s,v)=>{current.bindings.set(s,v);},
 capture:()=>({bindings:new Map([...current.bindings].filter(([s])=>s.enabled))}),
 invoke:(resource,callback,receiver,args)=>{const old=current;current=resource;try{return Reflect.apply(callback,receiver,args);}finally{current=old;}},
};
const ALS=createAsyncLocalStorage(kernel),a=new ALS(),b=new ALS();
let checks=0;const equal=(x,y)=>{assert.equal(x,y);checks++;};
equal(a.getStore(),undefined);
const marker={value:1};equal(a.run(marker,()=>a.getStore()),marker);equal(a.getStore(),undefined);
equal(a.run('A',()=>a.run('B',()=>a.getStore())),'B');equal(a.getStore(),undefined);
const frozen=Object.freeze({error:true});
for(const thrown of [frozen,null,undefined,0,false]){
 let seen=false;try{a.run('THROW',()=>{throw thrown;});}catch(e){seen=true;equal(e,thrown);}equal(seen,true);equal(a.getStore(),undefined);
}
a.run('A',()=>b.enterWith('B'));equal(a.getStore(),undefined);equal(b.getStore(),'B');
let child;
a.run('PARENT',()=>{child=kernel.capture();a.enterWith('LATER');equal(a.getStore(),'LATER');});
equal(kernel.invoke(child,()=>a.getStore(),undefined,[]),'PARENT');
a.disable();equal(a.getStore(),undefined);
const disabledChild=kernel.capture();a.enterWith('NEW');
equal(kernel.invoke(disabledChild,()=>a.getStore(),undefined,[]),undefined);
equal(kernel.invoke(child,()=>a.getStore(),undefined,[]),'PARENT');
let exitChild;
equal(a.exit(()=>{equal(a.getStore(),undefined);exitChild=kernel.capture();return 7;}),7);
equal(a.getStore(),'NEW');equal(kernel.invoke(exitChild,()=>a.getStore(),undefined,[]),undefined);
const receiver={receiver:true};
const bound=a.run('BOUND',()=>ALS.bind(function(x,y){equal(this,receiver);equal(x,2);equal(y,3);equal(a.getStore(),'BOUND');b.enterWith('BOUND-B');return 9;}));
equal(bound.length,2);equal(bound.call(receiver,2,3),9);equal(a.getStore(),'NEW');equal(b.getStore(),'B');
equal(bound.call(receiver,2,3),9);
const snap=a.run('SNAPSHOT',()=>ALS.snapshot());
equal(snap(()=>a.getStore()),'SNAPSHOT');equal(a.getStore(),'NEW');
let seen=false;try{snap(()=>{throw frozen;});}catch(e){equal(e,frozen);seen=true;}equal(seen,true);equal(a.getStore(),'NEW');
a.disable();const stateCount=current.bindings.size;
equal(a.run(undefined,()=>a.getStore()),undefined);equal(current.bindings.size,stateCount);
assert.throws(()=>ALS.bind(7),e=>e.code==='ERR_INVALID_ARG_TYPE');checks++;
assert.throws(()=>ALS.prototype.getStore.call({}),e=>e.code==='ERR_INVALID_ARG_TYPE');checks++;
console.log(JSON.stringify({schemaVersion:1,state:'SYNTHETIC_SYNCHRONOUS_FACADE_MODEL_CHECKS_PASSED',checks,
 nativeKernelInvoked:false,PromiseOrTaskPropagationProved:false,asyncProof:false}));
