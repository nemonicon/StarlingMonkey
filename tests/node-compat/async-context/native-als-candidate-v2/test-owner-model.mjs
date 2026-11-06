// Explicit synchronous DATA model. No native kernel, async workload or host ALS.
import assert from 'node:assert/strict';
import {createAsyncLocalStorage} from './after/builtins/node-compat/async-local-storage-factory.mjs';

const fresh = () => {const resource={bindings:new Map(),owner:null};resource.owner=resource;return resource;};
const server=fresh();let current=server,owner=server;
const kernel={
  createState:()=>({enabled:false}), enabled:s=>s.enabled,
  setEnabled:(s,value)=>{s.enabled=value;},
  get:(s,raw)=>raw||s.enabled?current.bindings.get(s):undefined,
  set:(s,value)=>{current.bindings.set(s,value);},
  capture:()=>({bindings:new Map([...current.bindings].filter(([s])=>s.enabled)),owner}),
  invoke:(resource,callback,receiver,args)=>{
    const previous=current,previousOwner=owner;current=resource;owner=resource.owner;
    try{return Reflect.apply(callback,receiver,args);}finally{current=previous;owner=previousOwner;}
  },
  runFresh:callback=>kernel.invoke(fresh(),callback,undefined,[]),
  runNeutral:callback=>kernel.invoke(server,callback,undefined,[]),
};
const ALS=createAsyncLocalStorage(kernel),a=new ALS(),b=new ALS();
let checks=0;
const eq=(actual,expected)=>{assert.equal(actual,expected);checks++;};
const task=callback=>({resource:kernel.capture(),callback,cancelled:false});
const dispatch=value=>{assert(!value.cancelled);return kernel.invoke(value.resource,value.callback,undefined,[]);};

// Prepare once under a neutral owner, even if accidentally requested from a request.
let ready,request1,request2,prepareCalls=0;
function ensureReady(){
  return kernel.runNeutral(()=>{
    if(!ready){prepareCalls++;a.enterWith('SERVER');ready=task(()=>[a.getStore(),owner]);}
    return ready;
  });
}
kernel.runFresh(()=>{
  request1=owner;a.enterWith('REQUEST1');
  eq(ensureReady(),ready);eq(a.getStore(),'REQUEST1');eq(owner,request1);
});
eq(owner,server);eq(dispatch(ready)[0],'SERVER');eq(dispatch(ready)[1],server);
kernel.runFresh(()=>{request2=owner;eq(a.getStore(),undefined);eq(ensureReady(),ready);eq(owner,request2);});
eq(prepareCalls,1);assert.notEqual(request1,request2);checks++;

// Request body/response resources are created INSIDE the real entry boundary.
let body,continuation,tick,timer,io,requestOwner;
kernel.runFresh(()=>{
  requestOwner=owner;a.enterWith('A');
  body=task(()=>[a.getStore(),owner]);
  continuation=task(()=>[a.getStore(),owner]);
  tick=task(()=>[a.getStore(),owner]);timer=task(()=>[a.getStore(),owner]);io=task(()=>[a.getStore(),owner]);
  a.enterWith('LATER');eq(a.getStore(),'LATER');
});
for(const item of [body,continuation,tick,timer,io]){eq(dispatch(item)[0],'A');eq(dispatch(item)[1],requestOwner);eq(owner,server);}
eq(a.getStore(),'SERVER');

// Repeating native tasks reuse their cell; newly created children snapshot it.
let repeat,child;
kernel.runFresh(()=>a.run('FIRST',()=>{repeat=task(()=>{const old=a.getStore();a.enterWith('SECOND');child=task(()=>a.getStore());return old;});}));
eq(dispatch(repeat),'FIRST');eq(dispatch(repeat),'SECOND');eq(dispatch(child),'SECOND');eq(owner,server);

// Cancellation runs in registered context, does not invalidate unrelated resources.
let cancelled;
kernel.runFresh(()=>a.run('CANCEL',()=>{cancelled=task(()=>{eq(a.getStore(),'CANCEL');eq(owner,cancelled.resource.owner);});}));
kernel.invoke(cancelled.resource,()=>{cancelled.callback();cancelled.cancelled=true;},undefined,[]);
eq(cancelled.cancelled,true);eq(owner,server);eq(dispatch(body)[0],'A');

// Disabled capture is empty while old resources can see old stores after enable.
let old,disabled;
kernel.runFresh(()=>a.run('OLD',()=>{old=task(()=>a.getStore());}));
a.disable();disabled=task(()=>a.getStore());
eq(dispatch(old),undefined);a.enterWith('REENABLED');eq(dispatch(old),'OLD');eq(dispatch(disabled),undefined);
eq(a.getStore(),'REENABLED');

// Fresh entry, nested entry and static capture restore BOTH current and owner.
let bound,snapshot;
kernel.runFresh(()=>{
  const outer=owner;a.enterWith('OUTER');bound=ALS.bind(()=>[a.getStore(),owner]);snapshot=ALS.snapshot();
  kernel.runFresh(()=>{eq(a.getStore(),undefined);assert.notEqual(owner,outer);checks++;a.enterWith('INNER');});
  eq(owner,outer);eq(a.getStore(),'OUTER');
});
eq(bound()[0],'OUTER');eq(snapshot(()=>a.getStore()),'OUTER');eq(owner,server);
for(const thrown of [Object.freeze({failure:true}),null,undefined,0,false]){
  let caught=false;
  try{kernel.runFresh(()=>a.run('THROW',()=>{throw thrown;}));}catch(error){eq(error,thrown);caught=true;}
  eq(caught,true);eq(owner,server);eq(a.getStore(),'REENABLED');
}

// Instance-local restoration leaves the other instance's same-resource change.
kernel.runFresh(()=>{a.run('A',()=>b.enterWith('B'));eq(a.getStore(),undefined);eq(b.getStore(),'B');});
eq(owner,server);eq(b.getStore(),undefined);

console.log(JSON.stringify({schemaVersion:1,state:'SYNTHETIC_NATIVE_OWNER_MODEL_PASSED',checks,
  nativeKernelInvoked:false,asyncPropagationProved:false,requestLifecycleProved:false}));
