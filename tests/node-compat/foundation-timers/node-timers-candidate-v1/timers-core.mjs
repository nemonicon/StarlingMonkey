// UNCOMPILED guest timer factory. All scheduling/liveness is native `kernel`;
// the host test adapter is separate. No Promise/setTimeout immediate alias.
export function createTimersFacade(a) {
 const {kernel:k,promisifyCustom,disposeSymbol,AbortSignal:Signal,EventTarget:Target,inventory}=a;
 const PROFILE='sm-node-22.14.0-m0.21',records=new WeakMap(),token=Symbol('private-native-node-timer');
 const get=Function.call.bind(WeakMap.prototype.get),set=Function.call.bind(WeakMap.prototype.set),apply=Reflect.apply;
 const aborted=Object.getOwnPropertyDescriptor(Signal.prototype,'aborted').get;
 const reason=Object.getOwnPropertyDescriptor(Signal.prototype,'reason').get;
 const add=Function.call.bind(Target.prototype.addEventListener),remove=Function.call.bind(Target.prototype.removeEventListener);
 function failure(code,op,text,Type=Error){return Object.assign(new Type(text),{code,module:'node:timers',operation:op,profile:PROFILE});}
 function unsupported(op){throw failure('ERR_SM_NODE_UNSUPPORTED',op,'Deferred timer operation: '+op);}
 function record(value){const r=get(records,value);if(!r)throw failure('ERR_INVALID_THIS','handle','Receiver must be a native-owned Timeout/Immediate',TypeError);return r;}
 function delay(value){value=value===undefined?1:value*1;if(!Number.isFinite(value)||value<1||value>2147483647)return 1;return Math.trunc(value);}
 function referenced(handle,value){const r=record(handle);k.setRef(r.id,value);const state=k.state(r.id);r.referenced=r.kind===2&&state<0?false:value;return handle;}
 function hasRef(handle){const r=record(handle),state=k.state(r.id);return state<0?(r.kind===2?false:r.referenced):state===1;}
 function cancel(handle){const r=record(handle);k.clear(r.id);if(r.kind===2)r.referenced=false;}
 class Timeout {
  constructor(key){if(key!==token)throw failure('ERR_ILLEGAL_CONSTRUCTOR','Timeout','Illegal constructor',TypeError);}
  ref(){return referenced(this,true);}
  unref(){return referenced(this,false);}
  hasRef(){return hasRef(this);}
  refresh(){const r=record(this);k.refresh(r.id);return this;}
  close(){cancel(this);return this;}
  [disposeSymbol](){cancel(this);}
  [Symbol.toPrimitive](){return record(this).id;}
 }
 class Immediate {
  constructor(key){if(key!==token)throw failure('ERR_ILLEGAL_CONSTRUCTOR','Immediate','Illegal constructor',TypeError);}
  ref(){return referenced(this,true);}
  unref(){return referenced(this,false);}
  hasRef(){return hasRef(this);}
  [disposeSymbol](){cancel(this);}
 }
 function schedule(kind,callback,time,args){
  if(typeof callback!=='function')throw failure('ERR_INVALID_ARG_TYPE','callback','callback must be a function',TypeError);
  if(args.length>1024)throw failure('ERR_SM_NODE_SCHEDULER_LIMIT','arguments','Too many callback arguments',RangeError);
  const h=kind===2?new Immediate(token):new Timeout(token),r={id:0,kind,referenced:true};set(records,h,r);
  // Native callback holds this closure/handle/args via actual TimerTask roots.
  // Context is captured by native AsyncTask before the real queue commit.
  const callbackWrapper=function(...values){return apply(callback,h,values);};
  r.id=k.create(kind,callbackWrapper,kind===2?0:delay(time),args);return h;
 }
 function setTimeout(callback,time,...args){return schedule(0,callback,time,args);}
 function setInterval(callback,time,...args){return schedule(1,callback,time,args);}
 function setImmediate(callback,...args){return schedule(2,callback,0,args);}
 function clearTimeout(value){const r=value&&(typeof value==='object'||typeof value==='function')?get(records,value):undefined;if(r){if(r.kind!==2)cancel(value);return;}if(typeof value==='string'&&/^\d+$/.test(value))value=Number(value);if(typeof value==='number'&&Number.isInteger(value)&&value>0&&value<=2147483647)k.clear(value);}
 const clearInterval=clearTimeout;
 function clearImmediate(value){const r=value&&(typeof value==='object'||typeof value==='function')?get(records,value):undefined;if(r?.kind===2)cancel(value);}
 function abortError(signal){const e=failure('ABORT_ERR','promises','The operation was aborted');e.name='AbortError';e.cause=apply(reason,signal,[]);return e;}
 function options(value){if(value===undefined)return{ref:true};if(!value||typeof value!=='object')throw failure('ERR_INVALID_ARG_TYPE','options','options must be object',TypeError);const ref=value.ref;if(ref!==undefined&&typeof ref!=='boolean')throw failure('ERR_INVALID_ARG_TYPE','options.ref','ref must be boolean',TypeError);const signal=value.signal;if(signal!==undefined){try{apply(aborted,signal,[]);}catch{throw failure('ERR_INVALID_ARG_TYPE','options.signal','signal must be native AbortSignal',TypeError);}}return{ref:ref!==false,signal};}
 function wait(kind,time,value,opts){
  // Return an actual guest Promise, not a scheduling backend. All native task
  // allocation comes from schedule() and real ref/unref ownership above.
  return new Promise((resolve,reject)=>{
   let opt;try{opt=options(opts);}catch(e){reject(e);return;}
   const signal=opt.signal;if(signal&&apply(aborted,signal,[])){reject(abortError(signal));return;}
   let handle,settled=false,listener;
   const clean=()=>{if(signal&&listener)remove(signal,'abort',listener);};
   const finish=()=>{if(settled)return;settled=true;clean();resolve(value);};
   listener=()=>{if(settled)return;settled=true;if(handle)cancel(handle);clean();reject(abortError(signal));};
   try{handle=kind===2?setImmediate(finish):setTimeout(finish,time);if(!opt.ref)handle.unref();if(signal){add(signal,'abort',listener,{once:true});if(apply(aborted,signal,[]))listener();}}
   catch(e){if(handle)cancel(handle);clean();if(!settled){settled=true;reject(e);}}
  });
 }
 function setTimeoutPromise(time,value,opts){if(new.target)unsupported('new promises.setTimeout');return wait(0,time,value,opts);}
 function setImmediatePromise(value,opts){if(new.target)unsupported('new promises.setImmediate');return wait(2,0,value,opts);}
 function setIntervalPromise(){unsupported('promises.setInterval');}
 const scheduler={yield(){return setImmediatePromise();},wait(time,opts){return setTimeoutPromise(time,undefined,opts);}};
 const promisesDefault={setTimeout:setTimeoutPromise,setImmediate:setImmediatePromise,setInterval:setIntervalPromise,scheduler};
 const promises=Object.create(null);for(const key of inventory.promises)promises[key]=key==='default'?promisesDefault:promisesDefault[key];
 const deferred=op=>function(){unsupported(op);};
 const rootDefault={setTimeout,setInterval,setImmediate,clearTimeout,clearInterval,clearImmediate,promises:promisesDefault,
  _unrefActive:deferred('_unrefActive'),active:deferred('active'),enroll:deferred('enroll'),unenroll:deferred('unenroll')};
 Object.defineProperty(setTimeout,promisifyCustom,{value:setTimeoutPromise,configurable:true});
 Object.defineProperty(setImmediate,promisifyCustom,{value:setImmediatePromise,configurable:true});
 const root=Object.create(null);for(const key of inventory.timers)root[key]=key==='default'?rootDefault:rootDefault[key];
 return{root,promises,globals:{setTimeout,setInterval,setImmediate,clearTimeout,clearInterval,clearImmediate}};
}
