// Experimental raw ESM entry. INIT installs the bounded guest profile facades.
// No bootstrap, FS, clocks, entropy or Promise workload, bundler or app rewrite.
import {bootstrap} from 'starling:node-startup';
import {createServerHandler,runFreshRequest,runNeutralServer} from 'starling:node-http';
import {Buffer as __nextBuffer} from 'node:buffer';
import {addAbortListener as __nextAbortListener} from 'node:events';
import * as __nextWebStreams from 'node:stream/web';
import {Readable as __nextReadable} from 'node:stream';
import __nextAsyncHooks from 'node:async_hooks';
import Module from 'node:module';
import fs from 'node:fs';
import * as types from 'wasi:http/types@0.2.10';
// Pure profile initialization only. No IO, clocks, entropy, tasks or resources.
// Main Node-compatible realm alias; auxiliary VM realms remain independent.
function installNodeGlobalAlias(target=globalThis) {
  if(target===null||(typeof target!=='object'&&typeof target!=='function'))
    throw new TypeError('Node global alias target must be an object');
  const descriptor=Object.getOwnPropertyDescriptor(target,'global');
  if(descriptor!==undefined) {
    if(!Object.hasOwn(descriptor,'value')||descriptor.value!==target||
       descriptor.writable!==true||descriptor.enumerable!==true||descriptor.configurable!==true)
      throw new TypeError('Existing global property does not match Node22 profile');
    return false;
  }
  Object.defineProperty(target,'global',{value:target,writable:true,enumerable:true,configurable:true});
  return true;
}

installNodeGlobalAlias(globalThis);
// Additional bounded Node BodyInit/context semantics, pure installation only.
{
// Guest profile extension for Node's classic-readable Request BodyInit.
// Installation is pure. Ordinary calls use the existing selected Readable.toWeb.
function installClassicRequestBody(Readable, target = globalThis) {
  const NativeRequest = target.Request;
  if (typeof NativeRequest !== 'function' || typeof Readable !== 'function' ||
      typeof Readable.toWeb !== 'function') throw new TypeError('Native Request and selected Readable.toWeb are required');
  const publicDescriptor = Object.getOwnPropertyDescriptor(target, 'Request');
  const constructorDescriptor = Object.getOwnPropertyDescriptor(NativeRequest.prototype, 'constructor');
  if (!publicDescriptor || !Object.hasOwn(publicDescriptor, 'value') || !publicDescriptor.configurable ||
      !constructorDescriptor || !Object.hasOwn(constructorDescriptor, 'value') || !constructorDescriptor.configurable)
    throw new TypeError('Request must have configurable public data bindings');
  const apply = Reflect.apply, construct = Reflect.construct, get = Reflect.get;
  const hasInstance = Function.prototype[Symbol.hasInstance];
  const toWeb = Readable.toWeb;
  const cancel = target.ReadableStream.prototype.cancel;
  const then = target.Promise.prototype.then;
  const reportCleanup = error => { try { console.error('REQUEST_CLASSIC_BODY_CLEANUP_FAILURE', error); } catch {} };
  function initView(init) {
    if (init === null || (typeof init !== 'object' && typeof init !== 'function')) return {value: init};
    let bodyRead = false, body, converted;
    // An empty forwarding target avoids Proxy invariants for frozen/non-writable
    // input dictionaries. Other getters retain their original receiver and order.
    const value = new Proxy(Object.create(null), {
      get(_unused, key) {
        if (key !== 'body') return get(init, key, init);
        if (!bodyRead) {
          body = get(init, key, init);
          if (body !== null && (typeof body === 'object' || typeof body === 'function') &&
              apply(hasInstance, Readable, [body])) converted = body = apply(toWeb, Readable, [body]);
          bodyRead = true;
        }
        return body;
      },
    });
    return {value, retire(reason) {
      if (converted === undefined) return;
      // A synchronous native constructor refusal must not leave a toWeb lease.
      // Preserve its thrown identity; any secondary async cleanup refusal is
      // retained in stderr rather than replacing that primary exception.
      try { apply(then, apply(cancel, converted, [reason]), [undefined, reportCleanup]); }
      catch (error) { reportCleanup(error); }
    }};
  }
  const Request = new Proxy(NativeRequest, {
    construct(native, args, newTarget) {
      if (args.length < 2) return construct(native, args, newTarget);
      const forwarded = args.slice();
      const init = initView(forwarded[1]);
      forwarded[1] = init.value;
      try { return construct(native, forwarded, newTarget); }
      catch (error) { init.retire?.(error); throw error; }
    },
  });
  // Sharing the genuine native prototype preserves native brand checks, clones,
  // public instanceof and NextRequest subclassing. No method is replaced.
  Object.defineProperty(NativeRequest.prototype, 'constructor', {...constructorDescriptor, value: Request});
  try { Object.defineProperty(target, 'Request', {...publicDescriptor, value: Request}); }
  catch (error) {
    Object.defineProperty(NativeRequest.prototype, 'constructor', constructorDescriptor);
    throw error;
  }
  return Object.freeze({
    restore() {
      if (target.Request === Request) Object.defineProperty(target, 'Request', publicDescriptor);
      const current = Object.getOwnPropertyDescriptor(NativeRequest.prototype, 'constructor');
      if (current && Object.hasOwn(current, 'value') && current.value === Request)
        Object.defineProperty(NativeRequest.prototype, 'constructor', constructorDescriptor);
    },
  });
}

installClassicRequestBody(__nextReadable,globalThis);
}
{
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

installAsyncResourceFacade(__nextAsyncHooks);
}

// Pure bounded profile installs; application loading remains deployed-only.
{
// Experimental guest entry corrections, not embedding APIs or host adapters.
// Installation is pure INIT metadata work. Compilation/copying is ordinary only.
function installCrossPrototypeBufferFrom(Buffer, world=globalThis) {
  const U8=world.Uint8Array,AB=world.ArrayBuffer,prototype=Object.getPrototypeOf(U8.prototype);
  const tag=Object.getOwnPropertyDescriptor(prototype,Symbol.toStringTag).get;
  const buffer=Object.getOwnPropertyDescriptor(prototype,'buffer').get;
  const offset=Object.getOwnPropertyDescriptor(prototype,'byteOffset').get;
  const length=Object.getOwnPropertyDescriptor(prototype,'byteLength').get;
  const abLength=Object.getOwnPropertyDescriptor(AB.prototype,'byteLength').get;
  const resizable=Object.getOwnPropertyDescriptor(AB.prototype,'resizable')?.get;
  const detached=Object.getOwnPropertyDescriptor(AB.prototype,'detached')?.get;
  const hasInstance=Function.prototype[Symbol.hasInstance],apply=Reflect.apply;
  const original=Buffer.from;
  function refused(){const e=new TypeError('node:buffer.from requires fixed unshared Uint8Array backing');e.code='ERR_SM_NODE_UNSUPPORTED';e.module='node:buffer';e.operation='Buffer.from';throw e;}
  function from(...args) {
    const value=args[0];let branded=false;
    try{branded=apply(tag,value,[])==='Uint8Array';}catch{}
    if(branded&&!apply(hasInstance,U8,[value])) {
      let backing,start,count;
      try{
        backing=apply(buffer,value,[]);apply(abLength,backing,[]);
        if(resizable&&apply(resizable,backing,[]))refused();
        if(detached&&apply(detached,backing,[]))refused();
        start=apply(offset,value,[]);count=apply(length,value,[]);
        if(!detached)new U8(backing,0,0); // Refuse detached backing, including zero-length views.
      }catch{refused();}
      // A temporary ordinary-prototype view shares only during this call.
      // The genuine old factory performs its existing bounded owned COPY.
      args[0]=new U8(backing,start,count);
    }
    return apply(original,this,args);
  }
  Buffer.from=from;
  return {restore(){if(Buffer.from===from)Buffer.from=original;}};
}

const originalFromLength=Object.getOwnPropertyDescriptor(__nextBuffer.from,'length');
installCrossPrototypeBufferFrom(__nextBuffer);
Object.defineProperty(__nextBuffer.from,'length',originalFromLength);
}
{
// Pure guest JS. Import/installation performs no IO. Calls delegate to the
// original profile ReadStream, including its deployed-phase and ownership guards.
const accepted = ['flags','encoding','fd','fs','mode','autoClose','emitClose','start','end','highWaterMark','signal'];
const sendOnly = ['root','acceptRanges','cacheControl','etag','dotfiles','hidden','extensions','immutable','index','lastModified','maxAge','maxage','from'];

function normalizeReadStreamOptions(value) {
  function fail(code, operation) {
    const e = new TypeError(code === 'ERR_SM_NODE_UNSUPPORTED' ? 'node:fs.' + operation + ' is outside this bounded profile' : operation);
    e.code = code; e.module = 'node:fs'; e.operation = operation; throw e;
  }
  if (value === undefined || value === null) return {};
  if (typeof value === 'string') return {encoding:value};
  if (typeof value !== 'object' || Array.isArray(value)) fail('ERR_INVALID_ARG_TYPE','options');
  // Retain the existing bounded policy for symbols and unknown own keys.
  for (const key of Reflect.ownKeys(value)) {
    if (typeof key !== 'string' || (!accepted.includes(key) && !sendOnly.includes(key))) fail('ERR_SM_NODE_UNSUPPORTED','createReadStream.' + String(key));
  }
  const result = Object.create(null);
  // Node22 copyObject and send both use for-in: inherited enumerable options
  // and getters matter. Read each accepted value once, preserving original
  // thrown values. A null-prototype target avoids any __proto__ setter.
  for (const key in value) {
    if (!accepted.includes(key) && !sendOnly.includes(key)) fail('ERR_SM_NODE_UNSUPPORTED','createReadStream.' + key);
    const entry = value[key];
    if (accepted.includes(key)) result[key] = entry;
  }
  return result;
}

const installed = new WeakMap();
function installReadStreamOptionsFacade(fs) {
  const prior = installed.get(fs);
  if (prior) {
    if (fs.createReadStream !== prior.createReadStream || fs.ReadStream !== prior.ReadStream || fs.FileReadStream !== prior.ReadStream) throw new Error('ReadStream options facade was replaced after installation');
    return prior.summary;
  }
  if (fs === null || typeof fs !== 'object') throw new TypeError('Expected mutable node:fs default record');
  const original = fs.ReadStream;
  if (typeof original !== 'function' || fs.FileReadStream !== original || typeof fs.createReadStream !== 'function') throw new TypeError('Expected original profile ReadStream aliases');
  const names = ['createReadStream','ReadStream','FileReadStream'];
  const descriptors = names.map(name => Object.getOwnPropertyDescriptor(fs,name));
  if (descriptors.some(d => !d || !Object.hasOwn(d,'value') || !d.writable || !d.configurable)) throw new TypeError('Expected writable configurable node:fs data bindings');
  function ReadStream(path, options) {
    if (!new.target) return new ReadStream(path,options);
    const target = new.target;
    const stream = Reflect.construct(original,[path,normalizeReadStreamOptions(options)],target);
    // The current profile's function constructor explicitly returns its real
    // ReadStreamImpl instance. Give that object the genuine derived prototype;
    // its Readable state and native-handle WeakMap remain on the same instance.
    if (Object.getPrototypeOf(stream) !== target.prototype) Object.setPrototypeOf(stream,target.prototype);
    return stream;
  }
  ReadStream.prototype = Object.create(original.prototype,{constructor:{value:ReadStream,writable:true,configurable:true}});
  Object.setPrototypeOf(ReadStream,original);
  function createReadStream(path,options) { return new ReadStream(path,options); }
  const values = [createReadStream,ReadStream,ReadStream];
  for (let i=0;i<names.length;i++) Object.defineProperty(fs,names[i],{...descriptors[i],value:values[i]});
  const summary = Object.freeze({kind:'bounded-readstream-send-options-v1',cjsDefaultPatched:true,esmNamedBindingsUpdated:false,additionalHostInterfaces:false});
  installed.set(fs,{createReadStream,ReadStream,summary});
  return summary;
}

installReadStreamOptionsFacade(fs);
}
{
// Guest-only profile facade. Real stream/AbortSignal objects and protected
// node:events.addAbortListener are required. Installation performs no IO/tasks.
function createSignalPipeTo({
  ReadableStream: RS, WritableStream: WS,
  ReadableStreamDefaultReader: Reader, WritableStreamDefaultWriter: Writer,
  AbortSignal: Signal, Promise: P, addAbortListener,
}) {
  if (typeof addAbortListener !== 'function') throw new TypeError('Protected addAbortListener is required');
  const apply = Reflect.apply;
  const own = Object.getOwnPropertyDescriptor;
  const get = (proto, key) => own(proto, key).get;
  const original = RS.prototype.pipeTo;
  const sourceLocked = get(RS.prototype, 'locked');
  const destLocked = get(WS.prototype, 'locked');
  const getReader = RS.prototype.getReader, getWriter = WS.prototype.getWriter;
  const read = Reader.prototype.read, cancel = Reader.prototype.cancel, releaseReader = Reader.prototype.releaseLock;
  const write = Writer.prototype.write, close = Writer.prototype.close, abort = Writer.prototype.abort, releaseWriter = Writer.prototype.releaseLock;
  const readerClosed = get(Reader.prototype, 'closed'), writerClosed = get(Writer.prototype, 'closed');
  const writerReady = get(Writer.prototype, 'ready'), desiredSize = get(Writer.prototype, 'desiredSize');
  const isAborted = get(Signal.prototype, 'aborted'), reason = get(Signal.prototype, 'reason');
  const then = P.prototype.then;
  const resolve = value => apply(P.resolve, P, [value]);
  const reject = value => apply(P.reject, P, [value]);
  const observe = (promise, fulfilled, rejected) => apply(then, promise, [fulfilled, rejected]);
  const disposeKey = typeof Symbol.dispose === 'symbol' ? Symbol.dispose : Symbol.for('nodejs.dispose');
  return function pipeTo(destination, options = undefined) {
    let reader, writer, signal, preventAbort, preventCancel, preventClose;
    try {
      // Intrinsic getters brand-check without invoking user shadow properties.
      apply(sourceLocked, this, []);
      apply(destLocked, destination, []);
      if (options !== undefined && options !== null && typeof options !== 'object')
        throw new TypeError('pipeTo options must be an object, null or undefined');
      preventAbort = !!options?.preventAbort;
      preventCancel = !!options?.preventCancel;
      preventClose = !!options?.preventClose;
      signal = options?.signal;
      if (signal === undefined) {
        return apply(original, this, [destination, {preventAbort, preventCancel, preventClose}]);
      }
      apply(isAborted, signal, []);
      if (apply(sourceLocked, this, []) || apply(destLocked, destination, [])) throw new TypeError('pipeTo requires unlocked streams');
      reader = apply(getReader, this, []);
      try { writer = apply(getWriter, destination, []); }
      catch (error) { apply(releaseReader, reader, []); throw error; }
    } catch (error) { return reject(error); }
    destination = null; options = undefined;
    let resolveResult, rejectResult;
    const result = new P((yes, no) => { resolveResult = yes; rejectResult = no; });
    let shuttingDown = false, finished = false, sourceClosing = false;
    let sourceState = 'readable', destState = 'writable', disposable;
    let currentWrite = resolve(), currentRead;
    const ignore = () => {};
    function finish(rejected, value) {
      if (finished) return;
      finished = true;
      let cleanupFailed = false, cleanupError;
      for (const action of [
        () => { if (disposable !== undefined) apply(disposable[disposeKey], disposable, []); },
        () => apply(releaseWriter, writer, []),
        () => apply(releaseReader, reader, []),
      ]) {
        try { action(); } catch (error) { if (!cleanupFailed) { cleanupFailed = true; cleanupError = error; } }
      }
      reader = writer = signal = disposable = undefined;
      if (cleanupFailed) rejectResult(cleanupError);
      else if (rejected) rejectResult(value);
      else resolveResult(undefined);
    }
    async function waitWrites() {
      for (;;) {
        const pending = currentWrite;
        await pending;
        if (pending === currentWrite) return;
      }
    }
    function shutdown(action, rejected, value, fromSourceClose = false) {
      if (shuttingDown) return;
      shuttingDown = true; sourceClosing = fromSourceClose;
      // Consume this internal async chain's rejection. The public result is the
      // sole caller-visible completion; release failures are never suppressed.
      observe((async () => {
        try {
          if (fromSourceClose) {
            if (currentRead === undefined) currentRead = apply(read, reader, []); // closed: mark disturbed, no chunk lost
            await currentRead;
          }
          if (destState === 'writable' && apply(desiredSize, writer, []) !== null) await waitWrites();
          if (action !== undefined) await action();
          finish(rejected, value);
        } catch (error) { finish(true, error); }
      })(), ignore, error => finish(true, error));
    }
    const cancelSource = error => sourceState === 'readable' ? apply(cancel, reader, [error]) : resolve();
    const abortDestination = error => destState === 'writable' ? apply(abort, writer, [error]) : resolve();
    function sourceErrored(error) {
      sourceState = 'errored';
      shutdown(preventAbort ? undefined : () => abortDestination(error), true, error);
    }
    function destinationErrored(error) {
      destState = 'errored';
      shutdown(preventCancel ? undefined : () => cancelSource(error), true, error);
    }
    function sourceClosed() {
      sourceState = 'closed';
      shutdown(preventClose ? undefined : () => apply(close, writer, []), false, undefined, true);
    }
    function destinationClosed() {
      destState = 'closed';
      if (shuttingDown) return;
      const error = new TypeError('Destination WritableStream is closed');
      shutdown(preventCancel ? undefined : () => cancelSource(error), true, error);
    }
    function abortPipe() {
      if (shuttingDown) return;
      const error = apply(reason, signal, []);
      shutdown(() => {
        const actions = [];
        if (!preventAbort) actions.push(abortDestination(error));
        if (!preventCancel) actions.push(cancelSource(error));
        return apply(P.all, P, [actions]);
      }, true, error);
    }
    try {
      // Capture both closed promises while locks are still held. Releasing the
      // reader later rejects pending read requests; the pump handles that path.
      observe(apply(readerClosed, reader, []), sourceClosed, sourceErrored);
      observe(apply(writerClosed, writer, []), destinationClosed, destinationErrored);
      if (apply(isAborted, signal, [])) abortPipe();
      else disposable = addAbortListener(signal, abortPipe);
      observe((async () => {
        while (!shuttingDown) {
          await apply(writerReady, writer, []);
          if (shuttingDown) return;
          currentRead = observe(apply(read, reader, []), record => {
            if (record.done) { sourceClosed(); return true; }
            // The public closed promise can settle before read's chunk reaction.
            // A source-close shutdown must forward that already-read final chunk.
            if (shuttingDown && !sourceClosing) return true;
            currentWrite = apply(write, writer, [record.value]);
            observe(currentWrite, ignore, destinationErrored);
            return false;
          }, error => { sourceErrored(error); return true; });
          if (await currentRead) return;
        }
      })(), ignore, destinationErrored);
    } catch (error) {
      shutdown(undefined, true, error);
    }
    return result;
  };
}

function installSignalPipeTo(addAbortListener, target = globalThis, web = target) {
  if (web.ReadableStream !== target.ReadableStream || web.WritableStream !== target.WritableStream)
    throw new TypeError('Profile stream constructors must be the actual global native streams');
  const descriptor = Object.getOwnPropertyDescriptor(target.ReadableStream.prototype, 'pipeTo');
  const pipeTo = createSignalPipeTo({
    ReadableStream: target.ReadableStream, WritableStream: target.WritableStream,
    ReadableStreamDefaultReader: web.ReadableStreamDefaultReader,
    WritableStreamDefaultWriter: web.WritableStreamDefaultWriter,
    AbortSignal: target.AbortSignal, Promise: target.Promise, addAbortListener,
  });
  Object.defineProperty(target.ReadableStream.prototype, 'pipeTo', {...descriptor, value: pipeTo});
  return pipeTo;
}

installSignalPipeTo(__nextAbortListener,globalThis,__nextWebStreams);
}

// Production-shaped guest adapter. No diagnostic app, event log or host service.
// `types` is the genuine selected wasi:http/types@0.2.10 namespace.
const drop=value=>{if(value)value[Symbol.dispose]();};
function text(value){let out='';for(const byte of value)out+=String.fromCharCode(byte);return out;}
function bytes(value){
  const out=new Uint8Array(value.length);
  for(let i=0;i<value.length;i++){const code=value.charCodeAt(i);if(code>255)throw new TypeError('HTTP header values must be ByteStrings');out[i]=code;}
  return out;
}
function ownData(value,key){
  if(value===null||(typeof value!=='object'&&typeof value!=='function'))return undefined;
  const descriptor=Object.getOwnPropertyDescriptor(value,key);
  return descriptor&&Object.prototype.hasOwnProperty.call(descriptor,'value')?descriptor.value:undefined;
}
function streamError(value){
  const payload=ownData(value,'payload'),variant=payload===undefined?value:payload,tag=ownData(variant,'tag');
  if(tag==='closed')return{tag};
  if(tag==='last-operation-failed'){
    const resource=ownData(variant,'val');
    if(resource!==null&&(typeof resource==='object'||typeof resource==='function'))return{tag,val:resource};
  }
  return undefined;
}
function diagnosticMethod(resource,name){
  for(let object=resource,depth=0;object!==null&&depth<4;object=Object.getPrototypeOf(object),depth++){
    const descriptor=Object.getOwnPropertyDescriptor(object,name);
    if(descriptor){
      if(Object.prototype.hasOwnProperty.call(descriptor,'value')&&typeof descriptor.value==='function')return descriptor.value;
      throw new TypeError('WASI diagnostic method must be a DATA function');
    }
  }
  throw new TypeError('WASI diagnostic method missing');
}
function streamFailure(value){
  const variant=streamError(value);
  if(variant?.tag==='last-operation-failed'){
    const resource=variant.val;let message;
    try{message=Reflect.apply(diagnosticMethod(resource,'toDebugString'),resource,[]);
      if(typeof message!=='string')throw new TypeError('WASI diagnostic must return a synchronous string');}
    finally{drop(resource);}
    const error=new Error(message);Object.defineProperty(error,'cause',{value,configurable:true,writable:true});return error;
  }
  return value;
}
function isObservedClosedOutput({observed,raw,caught,tag,responseSet}){
  return observed===true&&raw===caught&&tag==='closed'&&responseSet===true;
}
function mayReturnHandledClosed({classified,cancelReturned,readerReleased,cleanupReturned,requestAborted,fatalSet}){
  return classified===true&&cancelReturned===true&&readerReleased===true&&cleanupReturned===true&&requestAborted===true&&fatalSet===false;
}
function createWasiHttpHandler(webHandler,types,runFreshRequest){
  if(typeof runFreshRequest!=='function')throw new TypeError('Native request entry is required');
  const{Fields,IncomingBody,OutgoingBody,OutgoingResponse,ResponseOutparam}=types;
  async function handleResources(incoming,outparam){
    let inputBody,inputStream,outgoingResponse,outputBody,outputStream,responseReader,ioAbort,request;
    let incomingEnded=false,responseTransferred=false,responseSet=false,outputFinished=false;
    let headerChildUncertain=false,inputChildUncertain=false,inputBodyUncertain=false,outputChildUncertain=false,outputBodyUncertain=false;
    let primarySet=false,primaryValue,observedIo=false,firstIoReason;
    let outputFailureObserved=false,outputFailureRaw,outputFailureTag;
    let handledClosed=false,cancelReturned=false,readerReleased=false,cleanupReturned=false;
    function rememberFailure(error){if(!primarySet){primarySet=true;primaryValue=error;}}
    function abortObservedIo(reason){
      if(!observedIo){observedIo=true;firstIoReason=reason;}
      try{
        ioAbort.abort(reason);
        const signal=request===undefined?ioAbort.signal:request.signal;
        if(!signal.aborted||signal.reason!==firstIoReason)throw new Error('Observed I/O abort did not propagate');
      }catch(error){rememberFailure(error);}
    }
    function releaseInput(){
      const stream=inputStream;inputStream=undefined;
      if(stream)try{drop(stream);}catch(error){inputChildUncertain=true;rememberFailure(error);}
      // A failed child disposal leaves ownership uncertain; do not then dispose
      // its parent. The export must fail, never claim completed cleanup.
      if(inputChildUncertain)return;
      const body=inputBody;inputBody=undefined;
      if(body)try{
        if(incomingEnded)drop(IncomingBody.finish(body)); // Future intentionally uninspected.
        else drop(body);
      }catch(error){inputBodyUncertain=true;rememberFailure(error);}
    }
    try{
      // Allocation is inside the guard after incoming/outparam ownership entry.
      ioAbort=new AbortController();
      const headers=new Headers(),fieldResource=incoming.headers();
      try{for(const[name,value]of fieldResource.entries())headers.append(name,text(value));}
      catch(error){rememberFailure(error);}
      try{drop(fieldResource);}catch(error){headerChildUncertain=true;rememberFailure(error);}
      if(primarySet)throw primaryValue;
      const scheme=incoming.scheme(),protocol=scheme?.tag==='other'?scheme.val:scheme?.tag??'http';
      const authority=incoming.authority()??headers.get('host')??'localhost';
      const methodValue=incoming.method(),method=methodValue.tag==='other'?methodValue.val:methodValue.tag.toUpperCase();
      const url=protocol+'://'+authority+(incoming.pathWithQuery()??'/');
      inputBody=incoming.consume();let body;
      if(!['GET','HEAD'].includes(method)){
        inputStream=inputBody.stream();
        body=new ReadableStream({
          pull(controller){
            let chunk;
            try{chunk=inputStream.blockingRead(64n*1024n);}
            catch(error){
              const variant=streamError(error);
              if(variant?.tag==='closed'){
                incomingEnded=true;releaseInput();
                if(primarySet)controller.error(primaryValue);else controller.close();
              }else{
                let primary;
                try{primary=streamFailure(error);}catch(conversionError){rememberFailure(conversionError);primary=conversionError;}
                releaseInput();
                controller.error(primary);
                if(variant?.tag==='last-operation-failed')abortObservedIo(primary);
              }
              return;
            }
            if(chunk.length)controller.enqueue(chunk);
          },
          cancel(){releaseInput();if(primarySet)throw primaryValue;},
        });
      }
      request=new Request(url,{method,headers,signal:ioAbort.signal,...(body?{body,duplex:'half'}:{})});
      const response=await webHandler(request);
      if(primarySet)throw primaryValue;
      const fields=[];
      for(const[name,value]of response.headers)if(name!=='set-cookie')fields.push([name,bytes(value)]);
      const cookies=response.headers.getSetCookie?.()??(response.headers.get('set-cookie')?[response.headers.get('set-cookie')]:[]);
      for(const value of cookies)fields.push(['set-cookie',bytes(value)]);
      outgoingResponse=new OutgoingResponse(Fields.fromList(fields));outgoingResponse.setStatusCode(response.status);
      outputBody=outgoingResponse.body();
      const outgoing=outgoingResponse;outgoingResponse=undefined;responseTransferred=true;
      ResponseOutparam.set(outparam,{tag:'ok',val:outgoing});responseSet=true;
      outputStream=outputBody.write();
      if(response.body){
        responseReader=response.body.getReader();
        for(;;){
          const part=await responseReader.read();if(part.done)break;
          for(let offset=0;offset<part.value.byteLength;offset+=4096){
            try{outputStream.blockingWriteAndFlush(part.value.subarray(offset,offset+4096));}
            catch(error){outputFailureObserved=true;outputFailureRaw=error;outputFailureTag=streamError(error)?.tag;throw error;}
          }
        }
      }
      const stream=outputStream;outputStream=undefined;
      try{drop(stream);}catch(error){outputChildUncertain=true;throw error;}
      const finishedBody=outputBody;outputBody=undefined;outputFinished=true;
      OutgoingBody.finish(finishedBody,undefined);
    }catch(error){
      const observedOutput=outputFailureObserved&&outputFailureRaw===error;
      const variant=observedOutput?streamError(error):undefined;
      let primary=error;
      if(observedOutput)try{primary=streamFailure(error);}catch(conversionError){primary=conversionError;}
      if(observedOutput&&responseSet&&['closed','last-operation-failed'].includes(variant?.tag))abortObservedIo(primary);
      if(isObservedClosedOutput({observed:outputFailureObserved,raw:outputFailureRaw,caught:error,tag:outputFailureTag,responseSet})&&!primarySet){
        if(!responseReader)rememberFailure(new Error('Closed output has no response reader'));
        else{
          try{await responseReader.cancel(primary);cancelReturned=true;}catch(cancelError){rememberFailure(cancelError);}
          try{responseReader.releaseLock();responseReader=undefined;readerReleased=true;}catch(lockError){rememberFailure(lockError);}
          if(!primarySet)handledClosed=true;
        }
      }else{
        // Preserve the exact first unknown/falsy primary through later cleanup.
        rememberFailure(primary);
        if(responseReader)try{await responseReader.cancel(primary);}catch(cancelError){rememberFailure(cancelError);}
      }
    }finally{
      if(responseReader)try{responseReader.releaseLock();responseReader=undefined;}catch(error){rememberFailure(error);}
      releaseInput();
      const stream=outputStream;outputStream=undefined;
      if(stream)try{drop(stream);}catch(error){outputChildUncertain=true;rememberFailure(error);}
      const body=outputBody;outputBody=undefined;
      if(body&&!outputFinished&&!outputChildUncertain)try{drop(body);}catch(error){outputBodyUncertain=true;rememberFailure(error);}
      if(outgoingResponse&&!outputChildUncertain&&!outputBodyUncertain)try{drop(outgoingResponse);}catch(error){rememberFailure(error);}
      if(!responseTransferred)try{drop(outparam);}catch(error){rememberFailure(error);}
      if(!headerChildUncertain&&!inputChildUncertain&&!inputBodyUncertain)try{drop(incoming);}catch(error){rememberFailure(error);}
      cleanupReturned=!primarySet&&!headerChildUncertain&&!inputChildUncertain&&!inputBodyUncertain&&!outputChildUncertain&&!outputBodyUncertain;
    }
    if(primarySet)throw primaryValue;
    if(handledClosed&&!mayReturnHandledClosed({classified:handledClosed,cancelReturned,readerReleased,cleanupReturned,
      requestAborted:request?.signal.aborted===true,fatalSet:primarySet}))throw new Error('Known output close cleanup incomplete');
  }
  return{handle(incoming,outparam){
    let entered=false;
    try{return runFreshRequest((...args)=>{entered=true;return handleResources(...args);},undefined,incoming,outparam);}
    catch(error){if(!entered)disposeBeforeEntry(incoming,outparam);throw error;}
  }};
}

// Same pre-entry ownership contract as V4; preserve the original entry error.
function disposeBeforeEntry(incoming,outparam){
  let failures=0;
  for(const value of[incoming,outparam])try{drop(value);}catch{failures++;}
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
          return await handler.handle(incoming,outparam);
        },undefined);
      } catch(error) {
        if(!enteredNeutral)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  });
}

function readRoutingOrigin(value) {
  if(typeof value!=='string'||value.length>2048)
    throw new TypeError('Set canonical STARLING_NEXT_ORIGIN before deployment');
  const url=new URL(value);
  if(!['http:','https:'].includes(url.protocol)||!url.hostname||url.username||url.password||
     url.pathname!=='/'||url.search||url.hash||url.origin!==value)
    throw new TypeError('STARLING_NEXT_ORIGIN must be a canonical HTTP(S) origin');
  const port=url.port?Number(url.port):(url.protocol==='https:'?443:80);
  if(!Number.isInteger(port)||port<1||port>65535)throw new TypeError('Invalid routing port');
  return Object.freeze({origin:url.origin,hostname:url.hostname,port});
}

// Deployed control helper, inlined in raw entries. Never called during INIT.
// Capture under marker, invoke under a distinct enabled caller, restore caller.
// Default Node22 exit disables the instance; it is tested separately.
function evaluateCapturedStoreRestoration(state,AsyncLocalStorage,marker) {
  const outerBefore=state.getStore()===marker;
  const snapshot=AsyncLocalStorage.snapshot(),bound=AsyncLocalStorage.bind(()=>state.getStore());
  const otherStore={request:'enabled-caller'};
  const observed=state.run(otherStore,()=>{
    const otherBefore=state.getStore()===otherStore;
    const snapshotMarker=snapshot(()=>state.getStore())===marker;
    const otherAfterSnapshot=state.getStore()===otherStore;
    const boundMarker=bound()===marker;
    const otherAfterBound=state.getStore()===otherStore;
    return {otherBefore,snapshotMarker,otherAfterSnapshot,boundMarker,otherAfterBound};
  });
  return {outerBefore,...observed,outerAfter:state.getStore()===marker};
}

// Source fragment inlined in the raw ESM. No call occurs during INIT.
async function prepareServer() {
  const process=bootstrap();
  if(globalThis.process!==process)throw new Error('Native process identity mismatch');
  process.chdir('/app');
  const routing=readRoutingOrigin(process.env.STARLING_NEXT_ORIGIN);
  const required=JSON.parse(fs.readFileSync('/app/.next/required-server-files.json','utf8'));
  if(!required||typeof required.config!=='object'||!required.config||Array.isArray(required.config))
    throw new TypeError('Actual standalone Next config is required');
  process.env.NODE_ENV='production';
  process.env.NEXT_TELEMETRY_DISABLED='1';
  process.env.__NEXT_PRIVATE_STANDALONE_CONFIG=JSON.stringify(required.config);
  const require=Module.createRequire('/app/server.js');
  const versions={next:require('next/package.json').version,react:require('react/package.json').version,
    reactDom:require('react-dom/package.json').version};
  if(versions.next!=='16.4.5'||versions.react!=='19.3.1'||versions.reactDom!=='19.3.1')
    throw new Error('Pinned standalone dependency versions changed');
  // This configures real routing metadata. There is no socket/listener here;
  // the host owning this origin supplies standard incoming WASI HTTP resources.
  const next=require('next');
  const app=next({dir:'/app',dev:false,webpack:true,hostname:routing.hostname,port:routing.port});
  await app.prepare();
  const requestHandler=app.getRequestHandler();
  if(typeof requestHandler!=='function')throw new TypeError('Next request handler missing');
  const webHandler=createServerHandler(()=>requestHandler);
  return createWasiHttpHandler(webHandler,types,runFreshRequest);
}

export const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer,disposeBeforeEntry});
