// Isolated API-semantics prototype. This is not a registered Node builtin.
import {runResourceCases} from './resource-model-cases.mjs';
import {runResourceEdgeCases} from './resource-model-edge-cases.mjs';
const p=globalThis.__asyncContextProbe;
if(!p?.createState)throw new Error('Select the isolated resource-model-v3 native engine');
const apply=Reflect.apply,objectIs=Object.is;
// Created before application stores. Only native capture runs on this template;
// application callbacks receive a fresh child, never the mutable template.
const emptyEntryTemplate=p.capture();
const freshEntry=(callback,...args)=>p.runResource(p.runResource(emptyEntryTemplate,p.capture,undefined),callback,undefined,...args);
const states=new WeakMap(),resources=new WeakMap();
const weakGet=Function.call.bind(WeakMap.prototype.get),weakSet=Function.call.bind(WeakMap.prototype.set);
function invalid(message){const error=new TypeError(message);error.code='ERR_INVALID_ARG_TYPE';return error;}
function state(self){const value=weakGet(states,self);if(!value)throw invalid('Invalid AsyncLocalStorage receiver');return value;}
function resource(self){const value=weakGet(resources,self);if(!value)throw invalid('Invalid AsyncResource receiver');return value;}
function callable(fn){if(typeof fn!=='function')throw invalid('callback must be a function');return fn;}
export class AsyncLocalStorage {
  constructor(){weakSet(states,this,p.createState());}
  getStore(){return p.get(state(this));}
  enterWith(store){const token=state(this);p.enabled(token,true);p.set(token,store);}
  disable(){p.enabled(state(this),false);}
  run(store,callback,...args){
    const token=state(this);
    if(objectIs(store,p.get(token)))return apply(callable(callback),null,args);
    p.enabled(token,true);const previous=p.get(token,true);p.set(token,store);
    try{return apply(callable(callback),null,args);}finally{p.set(token,previous);}
  }
  exit(callback,...args){
    const token=state(this);
    if(!p.enabled(token))return apply(callable(callback),null,args);
    p.enabled(token,false);
    try{return apply(callable(callback),null,args);}finally{p.enabled(token,true);}
  }
  static bind(fn){return AsyncResource.bind(fn);}
  static snapshot(){return AsyncLocalStorage.bind((callback,...args)=>apply(callable(callback),undefined,args));}
}
export class AsyncResource {
  constructor(type,options){
    if(typeof type!=='string')throw invalid('type must be a string');
    // Trigger IDs/destroy hooks are deliberately outside this store prototype.
    weakSet(resources,this,p.capture());
  }
  runInAsyncScope(callback,thisArg,...args){return p.runResource(resource(this),callable(callback),thisArg,...args);}
  bind(callback,thisArg){
    callable(callback);const self=this,hasThis=arguments.length>1;
    const bound=function(...args){return self.runInAsyncScope(callback,hasThis?thisArg:this,...args);};
    Object.defineProperty(bound,'asyncResource',{value:self,writable:true,enumerable:true,configurable:true});
    return bound;
  }
  emitDestroy(){resource(this);return this;}
  static bind(callback,type='bound-anonymous-fn',thisArg){
    const self=new AsyncResource(type);
    return arguments.length>2?self.bind(callback,thisArg):self.bind(callback);
  }
}
const immediate=(callback,...args)=>p.schedule(()=>apply(callback,undefined,args));
const intervals=new Map();let nextInterval=1;
function interval(callback,_delay,...args){
  const id=nextInterval++,cell=new AsyncResource('diagnostic-repeated-task');
  const entry={active:true,handle:0};intervals.set(id,entry);
  const dispatch=()=>{if(!entry.active)return;cell.runInAsyncScope(callback,undefined,...args);if(entry.active)entry.handle=p.schedule(dispatch);};
  entry.handle=p.schedule(dispatch);return id;
}
function stopInterval(id){const entry=intervals.get(id);if(!entry)return;entry.active=false;p.cancel(entry.handle);intervals.delete(id);}
function complete(_path,callback){p.schedule(()=>callback(null,new Uint8Array([1])));}
function completePromise(path){return new Promise((resolve,reject)=>complete(path,(error,bytes)=>error?reject(error):resolve(bytes)));}
let calls=0;
async function targeted(){
  let checks=0;const equal=(a,b,label)=>{checks++;if(!objectIs(a,b))throw new Error(label);};
  const als=new AsyncLocalStorage(),second=new AsyncLocalStorage();
  const gate=()=>{let resolve;const promise=new Promise(done=>resolve=done);return{promise,resolve};};
  try{
    const pending=gate(),done=gate();let rootRan=false,scopedRan=false;
    p.nativeThen(pending.promise,()=>{equal(als.getStore(),undefined,'native empty registration');rootRan=true;});
    const marker={retained:true};
    als.run(marker,()=>p.nativeThen(pending.promise,()=>{equal(als.getStore(),marker,'native moving-GC registration');scopedRan=true;done.resolve();}));
    p.gc();als.run('RESOLVER',()=>pending.resolve());await done.promise;
    equal(rootRan,true,'native root ran');equal(scopedRan,true,'native scoped ran');
    let exitChild;
    als.run('A',()=>{
      const result=als.exit(()=>{equal(als.getStore(),undefined,'exit hides store');exitChild=new Promise(resolve=>queueMicrotask(()=>{equal(als.getStore(),undefined,'exit child excludes disabled store');resolve();}));return 31;});
      equal(result,31,'exit return');equal(als.getStore(),'A','exit restores enablement');
    });await exitChild;
    const receiver={tag:7};
    const bound=als.run('BOUND',()=>AsyncLocalStorage.bind(function(a,b){equal(this,receiver,'bound receiver');equal(a,1,'bound first argument');equal(b,2,'bound second argument');equal(als.getStore(),'BOUND','bound store');return 17;}));
    equal(bound.call(receiver,1,2),17,'bound return');equal(als.getStore(),undefined,'bound restoration');
    const failure={},cell=als.run('RESOURCE',()=>new AsyncResource('diagnostic-throw'));
    try{cell.runInAsyncScope(()=>{second.enterWith('SECOND');throw failure;});}catch(error){equal(error,failure,'resource throw identity');}
    equal(als.getStore(),undefined,'resource throw scope restoration');
    cell.runInAsyncScope(()=>equal(second.getStore(),'SECOND','resource mutation persists after throw'));
    let deliberateReuse;
    await freshEntry(async()=>{equal(als.getStore(),undefined,'first fresh entry');als.enterWith('ENTRY-ONE');deliberateReuse=new AsyncResource('deliberately-shared');await 0;equal(als.getStore(),'ENTRY-ONE','first entry await');});
    await freshEntry(async()=>{equal(als.getStore(),undefined,'second fresh entry');deliberateReuse.runInAsyncScope(()=>equal(als.getStore(),'ENTRY-ONE','intentional cross-entry resource reuse'));equal(als.getStore(),undefined,'fresh entry restored after reused resource');await 0;equal(als.getStore(),undefined,'second entry await');});
    return{checks,movingGC:true,nativeReactions:2,freshEntries:2,scope:'Additional store/receiver/arguments/exit/error-restoration and explicit fresh-entry checks; no request handle ownership, lifecycle IDs or destroy hooks.'};
  }finally{als.disable();second.disable();}
}
export async function run(){
  calls++;
  try{
    const report=await runResourceCases({AsyncLocalStorage,AsyncResource,queueMicrotask,setTimeout:immediate,clearTimeout:p.cancel,setInterval:interval,clearInterval:stopInterval,readFileCallback:complete,readFile:completePromise,sourcePath:'pure-guest-completion',executionAsyncResource:()=>({constructor:{name:'DiagnosticResource'}}),executionAsyncId:()=>-1});
    const edges=await runResourceEdgeCases({AsyncLocalStorage,AsyncResource,queueMicrotask});
    const extras=await targeted();
    return JSON.stringify({calls,...report,edges,extras,stats:p.stats(),scope:'Isolated mutable resource/store prototype. Timers/repeated resources and I/O completions use actual pure guest AsyncTask dispatch with synthetic bytes; this does not test real host timers or filesystem. IDs/destroy hooks and public executionAsyncResource identity are not implemented.'});
  }catch(error){return JSON.stringify({calls,failure:String(error),stack:error.stack,stats:p.stats()});}
}
