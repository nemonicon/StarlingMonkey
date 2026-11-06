// Generated isolated context controls. INIT installs only the pure sealed facade.
import {bootstrap} from 'starling:node-startup';
import {runFreshRequest,runNeutralServer} from 'starling:node-http';
import contextAsyncHooks,{AsyncLocalStorage as ContextAsyncLocalStorage} from 'node:async_hooks';
import {setTimeout as contextTimeout,clearTimeout as contextClearTimeout,setImmediate as contextImmediate,clearImmediate as contextClearImmediate} from 'node:timers';
import {setTimeout as contextPromiseTimeout} from 'node:timers/promises';
import * as types from 'wasi:http/types@0.2.10';
const installContextResource=(()=>{
// Guest JS facade over the actual installed native AsyncLocalStorage snapshot.
// Import/installation captures no context and performs no I/O or task creation.
const installed = new WeakMap();
function installAsyncResourceFacade(asyncHooks) {
  const apply = Reflect.apply, own = Object.getOwnPropertyDescriptor;
  const define = Object.defineProperty, hasOwn = Object.hasOwn;
  const get = Function.call.bind(WeakMap.prototype.get);
  const set = Function.call.bind(WeakMap.prototype.set);
  const prior = get(installed, asyncHooks);
  if (prior) {
    if (asyncHooks.AsyncResource !== prior.constructor)
      throw new TypeError('AsyncResource binding changed after installation');
    return prior.summary;
  }
  if (asyncHooks === null || typeof asyncHooks !== 'object')
    throw new TypeError('Expected mutable node:async_hooks default record');
  const descriptor = own(asyncHooks, 'AsyncResource');
  const ALS = asyncHooks.AsyncLocalStorage;
  if (!descriptor || !hasOwn(descriptor, 'value') || !descriptor.writable || !descriptor.configurable ||
      typeof ALS !== 'function' || typeof ALS.snapshot !== 'function')
    throw new TypeError('Expected original AsyncResource data binding and native ALS snapshot');
  const snapshot = ALS.snapshot;
  const captures = new WeakMap();
  const profile = 'sm-node-22.14.0-async-resource-m0.1';
  function fail(code, operation, message, Ctor = TypeError) {
    const error = new Ctor(message);
    for (const [key, value] of Object.entries({code, module:'node:async_hooks', operation, profile}))
      define(error, key, {value, writable:true, configurable:true, enumerable:true});
    throw error;
  }
  function unsupported(operation) {
    return function () {
      fail('ERR_SM_NODE_UNSUPPORTED', operation, operation + ' is outside this bounded profile', Error);
    };
  }
  class AsyncResource {
    constructor(type, options = undefined) {
      if (typeof type !== 'string') fail('ERR_INVALID_ARG_TYPE', 'AsyncResource', 'type must be a string');
      if (type.length > 4096) fail('ERR_SM_NODE_ASYNC_CONTEXT_LIMIT', 'AsyncResource', 'type exceeds 4096 code units', RangeError);
      if (options !== undefined) fail('ERR_SM_NODE_UNSUPPORTED', 'AsyncResource.options', 'AsyncResource options/trigger IDs are not implemented');
      // The app constructs resources only after deployed bootstrap. This is the
      // real native capture; no JS context stack, Promise patch or fake ID.
      set(captures, this, apply(snapshot, ALS, []));
    }
    runInAsyncScope(fn, thisArg, ...args) {
      const captured = get(captures, this);
      if (!captured) fail('ERR_INVALID_ARG_TYPE', 'AsyncResource.runInAsyncScope', 'Invalid AsyncResource receiver');
      if (typeof fn !== 'function') fail('ERR_INVALID_ARG_TYPE', 'AsyncResource.runInAsyncScope', 'fn must be a function');
      // snapshot's callback is one argument. The same native invoke has a 1024
      // argument cap; reserve that callback slot instead of bypassing the cap.
      if (args.length > 1023) fail('ERR_SM_NODE_ASYNC_CONTEXT_LIMIT', 'AsyncResource.runInAsyncScope', 'Bound argument limit exceeded', RangeError);
      return captured(() => apply(fn, thisArg, args));
    }
  }
  for (const name of ['bind', 'emitDestroy', 'asyncId', 'triggerAsyncId'])
    define(AsyncResource.prototype, name, {value:unsupported('AsyncResource.' + name), writable:true, configurable:true});
  define(AsyncResource, 'bind', {value:unsupported('AsyncResource.bind'), writable:true, configurable:true});
  const summary = Object.freeze({profile, cjsDefaultPatched:true, esmNamedBindingsUpdated:false,
    supported:['new AsyncResource(string)', 'runInAsyncScope'], nativeCapture:'AsyncLocalStorage.snapshot',
    fakeLifecycleIds:false, hooksImplemented:false, nativeCaptureAtInstall:false});
  define(asyncHooks, 'AsyncResource', {...descriptor, value:AsyncResource});
  set(installed, asyncHooks, {constructor:AsyncResource, summary});
  return summary;
}

return installAsyncResourceFacade;})();
installContextResource(contextAsyncHooks);
// Standard WASI HTTP resource ownership -> ordinary Web Request/Response.
// `types` is the actual wasi:http/types@0.2.10 namespace in guest-entry.mjs.
const drop = value => { if (value) value[Symbol.dispose](); };
function text(bytes) {
  let out = '';
  for (const byte of bytes) out += String.fromCharCode(byte);
  return out;
}
function bytes(value) {
  const result = new Uint8Array(value.length);
  for (let i = 0; i < value.length; i++) {
    const code = value.charCodeAt(i);
    if (code > 255) throw new TypeError('HTTP header values must be ByteStrings');
    result[i] = code;
  }
  return result;
}
// js-component-bindgen throws ComponentError with an own DATA payload.
// Only these explicit WIT stream-error records are interpreted. Unknown throws
// (including falsy values) keep their original identity; no message coercion.
function ownData(value,key) {
  if(value===null || (typeof value!=='object' && typeof value!=='function'))return undefined;
  const descriptor=Object.getOwnPropertyDescriptor(value,key);
  return descriptor && Object.prototype.hasOwnProperty.call(descriptor,'value')?descriptor.value:undefined;
}
function streamError(value) {
  const payload=ownData(value,'payload');
  const variant=payload===undefined?value:payload;
  const tag=ownData(variant,'tag');
  if(tag==='closed')return {tag};
  if(tag==='last-operation-failed') {
    const resource=ownData(variant,'val');
    if(resource!==null && (typeof resource==='object' || typeof resource==='function'))return {tag,val:resource};
  }
  return undefined;
}
function diagnosticMethod(resource,name) {
  for(let object=resource,depth=0;object!==null && depth<4;object=Object.getPrototypeOf(object),depth++) {
    const descriptor=Object.getOwnPropertyDescriptor(object,name);
    if(descriptor) {
      if(Object.prototype.hasOwnProperty.call(descriptor,'value') && typeof descriptor.value==='function')return descriptor.value;
      throw new TypeError('WASI diagnostic method must be a DATA function');
    }
  }
  throw new TypeError('WASI diagnostic method missing');
}
function streamFailure(value) {
  const variant=streamError(value);
  if(variant?.tag==='last-operation-failed') {
    const resource=variant.val;
    let message;
    try {
      message=Reflect.apply(diagnosticMethod(resource,'toDebugString'),resource,[]);
      if(typeof message!=='string')throw new TypeError('WASI diagnostic must return a synchronous string');
    } finally {drop(resource);}
    const error=new Error(message);
    Object.defineProperty(error,'cause',{value,configurable:true,writable:true});
    return error;
  }
  return value;
}

function createWasiHttpHandler(webHandler, types, runFreshRequest) {
  if (typeof runFreshRequest !== "function") throw new TypeError("Native request entry is required");
  const {Fields, IncomingBody, OutgoingBody, OutgoingResponse, ResponseOutparam} = types;
  async function handleResources(incoming, outparam) {
      let inputBody, inputStream, outgoingResponse, outputBody, outputStream, responseReader;
      let incomingEnded = false, responseSet = false, outputFinished = false;
      function releaseInput() {
        const stream = inputStream; inputStream = undefined;
        drop(stream);
        const body = inputBody; inputBody = undefined;
        if (body) {
          if (incomingEnded) drop(IncomingBody.finish(body));
          else drop(body);
        }
      }
      try {
        const fieldResource = incoming.headers();
        const headers = new Headers();
        try { for (const [name, value] of fieldResource.entries()) headers.append(name, text(value)); }
        finally { drop(fieldResource); }
        const scheme = incoming.scheme();
        const protocol = scheme?.tag === 'other' ? scheme.val : scheme?.tag ?? 'http';
        const authority = incoming.authority() ?? headers.get('host') ?? 'localhost';
        const methodValue = incoming.method();
        const method = methodValue.tag === 'other' ? methodValue.val : methodValue.tag.toUpperCase();
        const url = protocol + '://' + authority + (incoming.pathWithQuery() ?? '/');
        inputBody = incoming.consume();
        let body;
        if (!['GET', 'HEAD'].includes(method)) {
          inputStream = inputBody.stream();
          body = new ReadableStream({
            pull(controller) {
              try {
                const chunk = inputStream.blockingRead(64n * 1024n);
                if (chunk.length) controller.enqueue(chunk);
              } catch (error) {
                if (streamError(error)?.tag === 'closed') {
                  incomingEnded = true;
                  releaseInput();
                  controller.close();
                } else {
                  releaseInput();
                  controller.error(streamFailure(error));
                }
              }
            },
            cancel() { releaseInput(); },
          });
        }
        const request = new Request(url, {method, headers, ...(body ? {body, duplex: 'half'} : {})});
        const response = await webHandler(request);
        const fields = [];
        for (const [name, value] of response.headers) if (name !== 'set-cookie') fields.push([name, bytes(value)]);
        const cookies = response.headers.getSetCookie?.() ?? (response.headers.get('set-cookie') ? [response.headers.get('set-cookie')] : []);
        for (const value of cookies) fields.push(['set-cookie', bytes(value)]);
        outgoingResponse = new OutgoingResponse(Fields.fromList(fields));
        outgoingResponse.setStatusCode(response.status);
        outputBody = outgoingResponse.body();
        const outgoing = outgoingResponse; outgoingResponse = undefined;
        responseSet = true;
        ResponseOutparam.set(outparam, {tag: 'ok', val: outgoing});
        outputStream = outputBody.write();
        if (response.body) {
          responseReader = response.body.getReader();
          for (;;) {
            const part = await responseReader.read();
            if (part.done) break;
            for (let offset = 0; offset < part.value.byteLength; offset += 4096) {
              outputStream.blockingWriteAndFlush(part.value.subarray(offset, offset + 4096));
            }
          }
        }
        const stream = outputStream; outputStream = undefined;
        drop(stream);
        outputFinished = true;
        OutgoingBody.finish(outputBody, undefined);
      } catch (error) {
        if (responseReader) try { await responseReader.cancel(error); } catch {}
        throw streamFailure(error);
      } finally {
        releaseInput();
        drop(outputStream);
        if (outputBody && !outputFinished) drop(outputBody);
        drop(outgoingResponse);
        if (!responseSet) drop(outparam);
        drop(incoming);
      }
  }
  return {
    handle(incoming, outparam) {
      let entered=false;
      try {
        return runFreshRequest((...args)=>{
          entered=true;
          return handleResources(...args);
        },undefined,incoming,outparam);
      } catch(error) {
        if(!entered)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  };
}

// The caller still owns incoming/outparam until native callback entry. Always
// attempt both drops, preserving the original pre-entry error even if cleanup
// itself refuses. Cleanup failure is diagnostic and cannot turn into success.
function disposeBeforeEntry(incoming,outparam) {
  let failures=0;
  for(const value of [incoming,outparam])try{drop(value);}catch{failures++;}
  if(failures)try{console.error('NEXT_COMPONENT_PRE_ENTRY_DISPOSAL_FAILURE',failures);}catch{}
}

// Pure orchestration, inlined unchanged into each raw guest entry.
function createNeutralReadyHandler({runNeutralServer,prepareServer,disposeBeforeEntry}) {
  let readiness;
  return Object.freeze({
    handle(incoming,outparam) {
      let enteredNeutral=false;
      try {
        return runNeutralServer(async () => {
          enteredNeutral=true;
          let handler;
          try {
            // Both promise allocation and all preparation happen neutrally.
            // One sticky promise per component instance: concurrent first
            // requests share success or the original rejection, never retry.
            readiness ??= Promise.resolve().then(prepareServer);
            handler=await readiness;
            if(!handler||typeof handler.handle!=='function')
              throw new TypeError('Preparation must return the real WASI handler');
          } catch(error) {
            disposeBeforeEntry(incoming,outparam);
            throw error;
          }
          // The adapter owns both resources from here. It enters native fresh
          // request context BEFORE constructing headers, body or Web Request.
          return handler.handle(incoming,outparam);
        },undefined);
      } catch(error) {
        if(!enteredNeutral)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  });
}


// Shared ordinary workload. No instances, timers, I/O or async work at import.
const CONTEXT_CONTROL_IDS = ['fresh-branches','cross-owner-promises','shared-readiness','disable-captures','normal-timer-abort'];
function contextFailure(control,id) {
  const e=new Error(control+': '+id);e.code='ERR_CONTEXT_CONTROL_ASSERTION';e.control=control;e.check=id;return e;
}
function contextError(value) {
  if(value===null)return{type:'null'};
  if(typeof value==='object'||typeof value==='function'){
    const out={type:typeof value};
    for(const key of ['name','message','code','control','check']){
      const d=Object.getOwnPropertyDescriptor(value,key);
      if(d&&Object.hasOwn(d,'value')&&typeof d.value==='string')out[key]=d.value;
    }
    return out;
  }
  return{type:typeof value,value:typeof value==='number'&&!Number.isFinite(value)?String(value):typeof value==='bigint'?String(value):value};
}
function deferred() {let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return{promise,resolve,reject};}
function marker(label){return Object.freeze({label});}
function recordFor(id) {
  const record={id,passed:false,assertions:[],events:[],requiredEdges:[]};
  return{record,
    check(name,value){record.assertions.push({id:name,passed:value===true});if(value!==true)throw contextFailure(id,name);},
    event(name){if(record.events.length>=256)throw contextFailure(id,'event-bound');record.events.push(name);},
    before(a,b){record.requiredEdges.push([a,b]);this.check('order:'+a+'<'+b,record.events.indexOf(a)>=0&&record.events.indexOf(a)<record.events.indexOf(b));},
  };
}
function setup(backend,record) {
  const stores=[];
  function store(label){
    const value=new backend.AsyncLocalStorage();
    // Force genuine enabled state with a non-undefined seed, then restore empty.
    // Node empty-store projection is used only for this managed enabled set.
    value.run(marker('enable:'+label),()=>{});record.check('initial-empty:'+label,value.getStore()===undefined);
    stores.push(value);return value;
  }
  const a=store('a'),b=store('b'),boundaries=backend.boundaries(stores);
  return{a,b,
    fresh(fn){return boundaries.runFreshRequest(fn,undefined);},
    neutral(fn){return boundaries.runNeutralServer(fn,undefined);},
    empty(id){record.check(id+':a-empty',a.getStore()===undefined);record.check(id+':b-empty',b.getStore()===undefined);},
    cleanup(){for(const state of stores)state.disable();},
  };
}
function scheduling(backend) {
  const timeouts=new Set(),immediates=new Set();let pendingPromises=0,peak=0;
  function note(){peak=Math.max(peak,timeouts.size+immediates.size+pendingPromises);if(peak>8)throw contextFailure('scheduler','eight-live-waits-limit');}
  function callback(kind,fn,delay=1){
    return new Promise((resolve,reject)=>{
      if(kind==='tick'){backend.nextTick(()=>{try{resolve(fn());}catch(e){reject(e);}});return;}
      const list=kind==='immediate'?immediates:timeouts;
      let handle;const invoke=()=>{list.delete(handle);try{resolve(fn());}catch(e){reject(e);}};
      handle=kind==='immediate'?backend.setImmediate(invoke):backend.setTimeout(invoke,delay);list.add(handle);note();
    });
  }
  function promiseTimeout(delay,value,options){
    pendingPromises++;note();let result;
    try{result=backend.promiseTimeout(delay,value,options);}catch(e){pendingPromises--;throw e;}
    // Observe immediately; never create an unhandled intermediate rejection.
    return result.then(value=>{pendingPromises--;return value;},reason=>{pendingPromises--;throw reason;});
  }
  function deadline(promise){
    let handle;const expired=new Promise((_,reject)=>{handle=backend.setTimeout(()=>{timeouts.delete(handle);reject(contextFailure('scheduler','five-second-collection-deadline'));},5000);timeouts.add(handle);note();});
    return Promise.race([promise,expired]).finally(()=>{backend.clearTimeout(handle);timeouts.delete(handle);});
  }
  return{callback,promiseTimeout,deadline,peak:()=>peak,
    clear(){for(const h of timeouts)backend.clearTimeout(h);for(const h of immediates)backend.clearImmediate(h);timeouts.clear();immediates.clear();},
    pending:()=>timeouts.size+immediates.size+pendingPromises};
}
async function freshBranches(backend,r,schedule) {
  const c=setup(backend,r),started=deferred();let entries=0,active=0,peak=0;
  const run=label=>c.fresh(()=>{
    c.empty('fresh-'+label);
    const m=marker(label),other=marker('other-'+label);
    return c.a.run(m,()=>c.b.run(other,async()=>{
      active++;peak=Math.max(peak,active);r.event(label+':entered');if(++entries===2)started.resolve();
      await started.promise;r.check(label+':both-entered',entries===2);
      for(const kind of ['tick','promise','immediate','timer']){
        const body=()=>{r.event(label+':'+kind+':callback');r.check(label+':'+kind+':callback-store',c.a.getStore()===m&&c.b.getStore()===other);};
        if(kind==='promise')await Promise.resolve().then(body);else await schedule.callback(kind,body);
        r.event(label+':'+kind+':after');r.check(label+':'+kind+':continuation-store',c.a.getStore()===m&&c.b.getStore()===other);
        r.before(label+':'+kind+':callback',label+':'+kind+':after');
      }
      active--;r.event(label+':done');return label;
    }));
  });
  try{
    const first=run('A'),second=run('B');c.empty('outer-after-entries');
    r.check('two-logical-branches-active',peak===2);r.check('results',JSON.stringify(await Promise.all([first,second]))==='["A","B"]');
    c.empty('outer-after-completion');r.check('logical-branches-done',active===0);
    for(const label of ['A','B'])r.before(label+':entered',label+':done');
  }finally{c.cleanup();}
}
async function crossOwnerPromises(backend,r) {
  const c=setup(backend,r),pending={A:c.neutral(deferred),B:c.neutral(deferred)},both=deferred();let registered=0;
  const settled=c.neutral(()=>Promise.resolve(marker('settled'))),sent={A:marker('from-A'),B:marker('from-B')};
  function branch(label,other){return c.fresh(()=>{
    c.empty('fresh-'+label);const m=marker(label),second=marker('other-'+label);
    return c.a.run(m,()=>c.b.run(second,async()=>{
      const own=pending[label].promise;
      const then=own.then(function(value){r.event(label+':then');r.check(label+':then-context',c.a.getStore()===m&&c.b.getStore()===second);r.check(label+':then-value-receiver',value===sent[other]&&this===undefined);return value;});
      const awaited=(async()=>{const value=await own;r.event(label+':await');r.check(label+':pending-await-context',c.a.getStore()===m&&c.b.getStore()===second);r.check(label+':pending-await-value',value===sent[other]);})();
      const all=Promise.all([own,settled]).then(values=>{r.event(label+':all');r.check(label+':all-context-values',c.a.getStore()===m&&values[0]===sent[other]&&values[1].label==='settled');});
      r.event(label+':registered');if(++registered===2)both.resolve();await both.promise;
      r.check(label+':registration-barrier',registered===2);r.event(label+':resolve-other');pending[other].resolve(sent[label]);
      await Promise.all([then,awaited,all]);r.check(label+':after-all-context',c.a.getStore()===m&&c.b.getStore()===second);
      await settled;r.check(label+':settled-await-context',c.a.getStore()===m);
      const thenable={then(resolve){r.event(label+':thenable');r.check(label+':thenable-context-receiver',c.a.getStore()===m&&this===thenable);resolve(sent[label]);}};
      r.check(label+':thenable-value',await Promise.resolve(thenable)===sent[label]);r.check(label+':after-thenable-context',c.a.getStore()===m);
      r.event(label+':done');return label;
    }));
  });}
  try{
    const a=branch('A','B'),b=branch('B','A');c.empty('outer-after-entries');await Promise.all([a,b]);c.empty('outer-after-completion');
    for(const label of ['A','B'])for(const event of ['then','await','all']){r.before(label+':registered',label+':'+event);r.before((label==='A'?'B':'A')+':resolve-other',label+':'+event);}
  }finally{c.cleanup();}
}
async function sharedReadiness(backend,r,schedule) {
  const c=setup(backend,r);let readiness,attempts=0;
  const prepared=marker('prepared'),seen=[];
  async function prepare(){attempts++;r.event('prepare:start');c.empty('prepare-before-await');await schedule.callback('immediate',()=>{c.empty('prepare-callback');r.event('prepare:immediate');});c.empty('prepare-after-await');r.event('prepare:done');return prepared;}
  function ensure(){return c.neutral(()=>readiness??=Promise.resolve().then(prepare));}
  function caller(label){return c.fresh(()=>{
    c.empty('fresh-'+label);const m=marker(label);
    return c.a.run(m,async()=>{
      r.event(label+':call');const value=ensure();seen.push(value);r.check(label+':caller-after-ensure',c.a.getStore()===m);
      r.check(label+':not-prepared-synchronously',attempts===0);const result=await value;
      r.check(label+':prepared-result-context',result===prepared&&c.a.getStore()===m);r.event(label+':done');return result;
    });
  });}
  try{
    const a=caller('A'),b=caller('B');r.check('same-readiness-promise',seen[0]===seen[1]);await Promise.all([a,b]);r.check('one-prepare-attempt',attempts===1);c.empty('outer-after-first-pair');
    await c.fresh(()=>c.a.run(marker('later'),async()=>{const value=ensure();r.check('later-same-readiness',value===seen[0]);r.check('later-result',await value===prepared);}));
    r.check('still-one-attempt',attempts===1);c.empty('outer-after-later');
    for(const label of ['A','B']){r.before(label+':call','prepare:start');r.before('prepare:done',label+':done');}
  }finally{c.cleanup();}
}
async function disableCaptures(backend,r) {
  const c=setup(backend,r),pending=c.neutral(deferred),registered=c.neutral(deferred),observed=c.neutral(deferred);
  const aMarker=marker('A'),aOther=marker('A-other'),bMarker=marker('B'),bOther=marker('B-other'),receiver={label:'receiver'};let captured;
  // Both fresh entries and all neutral allocations precede disable. The Node
  // reference never projects an empty boundary while an ALS is disabled.
  const first=c.fresh(()=>c.a.run(aMarker,()=>c.b.run(aOther,()=>{
    const callback=function(value){return{store:c.a.getStore(),other:c.b.getStore(),receiver:this,value};};
    captured={snapshot:backend.AsyncLocalStorage.snapshot(),bound:backend.AsyncLocalStorage.bind(callback),resource:new backend.AsyncResource('context-capture'),callback};
    const reaction=pending.promise.then(()=>{r.event('A:disabled-reaction');r.check('A:disabled-store-hidden',c.a.getStore()===undefined);r.check('A:other-store-retained',c.b.getStore()===aOther);observed.resolve();});registered.resolve();return reaction;
  })));
  const second=c.fresh(()=>c.a.run(bMarker,()=>c.b.run(bOther,async()=>{
    await registered.promise;c.a.disable();r.event('B:disabled');
    const seeDisabled=()=>c.a.getStore();
    r.check('disabled-snapshot',captured.snapshot(seeDisabled)===undefined);
    r.check('disabled-bound',captured.bound.call(receiver,'x').store===undefined);
    r.check('disabled-resource',captured.resource.runInAsyncScope(seeDisabled)===undefined);
    r.check('B:unrelated-not-disabled',c.b.getStore()===bOther);pending.resolve();await observed.promise;
    r.check('B:await-registered-disabled-has-no-a',c.a.getStore()===undefined);r.check('B:await-keeps-other',c.b.getStore()===bOther);
    c.a.enterWith(bMarker);r.event('B:reenabled');
    for(const [name,invoke] of [['snapshot',()=>captured.snapshot(()=>captured.callback.call(receiver,'x'))],['bound',()=>captured.bound.call(receiver,'x')],['resource',()=>captured.resource.runInAsyncScope(captured.callback,receiver,'x')]]){
      const value=invoke();r.check(name+':old-capture-restored',value.store===aMarker&&value.other===aOther&&value.receiver===receiver&&value.value==='x');
      r.check(name+':B-restored',c.a.getStore()===bMarker&&c.b.getStore()===bOther);
    }
    r.check('exit-still-disables-captured-store',c.a.exit(()=>captured.bound()).store===undefined);r.check('after-exit-B-restored',c.a.getStore()===bMarker);
  })));
  try{await Promise.all([first,second]);c.empty('outer-after-completion');r.before('B:disabled','A:disabled-reaction');r.before('A:disabled-reaction','B:reenabled');}finally{c.cleanup();}
}
async function normalTimerAbort(backend,r,schedule) {
  const c=setup(backend,r),registered=c.neutral(deferred),done=c.neutral(deferred),controller=new AbortController(),reason=marker('normal-abort');
  let settlements=0;const aMarker=marker('A'),bMarker=marker('B');
  const first=c.fresh(()=>c.a.run(aMarker,()=>{
    const observed=schedule.promiseTimeout(60000,'not-delivered',{signal:controller.signal}).then(
      ()=>{throw contextFailure(r.record.id,'aborted-timer-fulfilled');},
      error=>{settlements++;r.event('A:abort-reaction');r.check('abort-error-shape',error.name==='AbortError'&&error.code==='ABORT_ERR'&&error.cause===reason);r.check('abort-reaction-A-context',c.a.getStore()===aMarker);done.resolve();return'cancelled';});
    registered.resolve();return observed;
  }));
  const second=c.fresh(()=>c.a.run(bMarker,async()=>{
    await registered.promise;r.event('B:abort');controller.abort(reason);r.check('abort-reason-identity',controller.signal.reason===reason);r.check('B:after-abort-context',c.a.getStore()===bMarker);await done.promise;r.check('B:after-cancel-context',c.a.getStore()===bMarker);
  }));
  try{
    const result=await Promise.all([first,second]);r.check('abort-result-and-once',result[0]==='cancelled'&&settlements===1);c.empty('outer-after-abort');r.before('B:abort','A:abort-reaction');
    const finishController=new AbortController(),value=marker('normal-finish'),finishMarker=marker('finish');let finished=0;
    await c.fresh(()=>c.a.run(finishMarker,()=>schedule.promiseTimeout(1,value,{signal:finishController.signal}).then(result=>{finished++;r.event('finish:reaction');r.check('normal-finish-value-context',result===value&&c.a.getStore()===finishMarker);})));
    finishController.abort(marker('after-finish'));await Promise.resolve();r.check('normal-finish-exactly-once',finished===1);c.empty('outer-after-normal-finish');
  }finally{if(!controller.signal.aborted)controller.abort(reason);c.cleanup();}
}
async function collectContextInterleaving(backend,call=1) {
  const result={schemaVersion:1,suite:'CONTEXT_INTERLEAVING_FIVE_CONTROLS_V1',call,boundaryMode:backend.boundaryMode,records:[],passed:false,
    logicalBranchesOnly:true,actualHttpResourceConcurrencyProved:false,nativeOwnerIdentityOrTeardownProved:false,resetOrGcWorkload:false};
  const schedule=scheduling(backend),controls=[freshBranches,crossOwnerPromises,sharedReadiness,disableCaptures,normalTimerAbort];
  try{
    await schedule.deadline((async()=>{
      for(let i=0;i<controls.length;i++){
        const r=recordFor(CONTEXT_CONTROL_IDS[i]);result.records.push(r.record);
        try{await controls[i](backend,r,schedule);r.record.passed=true;}catch(error){r.record.error=contextError(error);throw error;}
      }
    })());
    if(schedule.pending()!==0)throw contextFailure('scheduler','workload-handles-not-settled');
    result.passed=result.records.length===5&&result.records.every(r=>r.passed&&r.assertions.every(a=>a.passed));
  }catch(error){result.error=contextError(error);}finally{schedule.clear();result.peakPlannedWaits=schedule.peak();}
  return result;
}
function contextPublicProjection(result) {
  if(result.schemaVersion!==1||result.suite!=='CONTEXT_INTERLEAVING_FIVE_CONTROLS_V1'||result.passed!==true||result.records.length!==5)throw contextFailure('projection','refuse-incomplete-result');
  if(JSON.stringify(result.records.map(r=>r.id))!==JSON.stringify(CONTEXT_CONTROL_IDS))throw contextFailure('projection','control-inventory');
  return{schemaVersion:1,kind:'CONTEXT_INTERLEAVING_PUBLIC_EXPECTATIONS_V1',call:result.call,records:result.records.map(r=>{
    if(r.passed!==true||r.assertions.some(a=>a.passed!==true)||new Set(r.assertions.map(a=>a.id)).size!==r.assertions.length||new Set(r.events).size!==r.events.length)throw contextFailure(r.id,'invalid-observations');
    for(const [a,b] of r.requiredEdges)if(r.events.indexOf(a)<0||r.events.indexOf(a)>=r.events.indexOf(b))throw contextFailure(r.id,'event-partial-order');
    const order=(a,b)=>a<b?-1:a>b?1:0;
    return{id:r.id,assertions:[...r.assertions].sort((a,b)=>order(a.id,b.id)),eventIds:[...r.events].sort(),requiredEdges:[...r.requiredEdges].sort((a,b)=>order(JSON.stringify(a),JSON.stringify(b)))};
  })};
}

// Source fragment only; no body executes during INIT.
function createNativeContextBackend(process) {
  return{AsyncLocalStorage:ContextAsyncLocalStorage,AsyncResource:contextAsyncHooks.AsyncResource,
    boundaryMode:'actual-native-private-boundaries',
    boundaries(){return{runFreshRequest,runNeutralServer};},
    nextTick:callback=>process.nextTick(callback),setTimeout:contextTimeout,clearTimeout:contextClearTimeout,
    setImmediate:contextImmediate,clearImmediate:contextClearImmediate,promiseTimeout:contextPromiseTimeout};
}
let contextCalls=0;
async function prepareContextServer() {
  const process=bootstrap();
  if(globalThis.process!==process)throw new Error('Actual native process identity mismatch');
  const backend=createNativeContextBackend(process);
  const handler=async request=>{
    const call=++contextCalls;
    const collected=await collectContextInterleaving(backend,call);
    return new Response(JSON.stringify({schemaVersion:1,marker:'NEXT_NATIVE_CONTEXT_INTERLEAVING_V1',call,
      method:request.method,collection:collected}),{status:collected.passed?200:500,
      headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
  };
  return createWasiHttpHandler(handler,types,runFreshRequest);
}
export const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer:prepareContextServer,disposeBeforeEntry});
