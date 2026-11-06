// Isolated ordinary native signal-pipe probe; no application or filesystem bootstrap.
// Guest profile initialization; standard native modules, no host shim.
import {addAbortListener as __nextProtectedAbortListener} from 'node:events';
import * as __nextNativeWebStreams from 'node:stream/web';
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

installSignalPipeTo(__nextProtectedAbortListener,globalThis,__nextNativeWebStreams);

import {runFreshRequest} from 'starling:node-http';
import * as types from 'wasi:http/types@0.2.10';
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
function streamFailure(value) {
  if (value?.tag === 'last-operation-failed') {
    let message = 'WASI HTTP stream operation failed';
    try { message = value.val.toDebugString(); } finally { drop(value.val); }
    return new Error(message);
  }
  return value instanceof Error ? value : new Error('WASI HTTP stream failure: ' + value?.tag);
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
                if (error?.tag === 'closed') {
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



// INIT declares functions only. No streams, signals, timers or promises until collection.
const pipeCaseIds=Object.freeze(["finite final chunk is not lost", "preventClose preserves open destination", "source error preventAbort=false", "write rejection cancels source", "preaborted executes both actions", "cancel failure overrides abort reason", "abort failure overrides abort reason", "stopImmediatePropagation cannot suppress cancellation", "wait for in-flight write before cancellation", "ready backpressure bounds reads", "locked source refuses without stealing locks", "locked destination refuses without source lock"]);
const tick=()=>new Promise(resolve=>setTimeout(resolve,0));
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const settle=async(p,marker)=>{try{await p;return {rejected:false};}catch(error){return {rejected:true,same:error===marker,type:error===null?'null':typeof error,name:error instanceof Error?error.name:undefined};}};
function failureData(error){const out={type:typeof error,isNull:error===null};if(error===null||['string','number','boolean'].includes(typeof error))out.value=error;else if(error!==undefined)for(const key of ['name','message','code'])try{const value=error[key];out[key]={type:typeof value,...(['string','number','boolean'].includes(typeof value)?{value:typeof value==='string'?value.slice(0,2048):value}:{})};}catch{out[key]={type:'read-threw'};}return out;}
async function collectPipeProbe(call,pipe=ReadableStream.prototype.pipeTo){
 const scenarios=[];
 function scenario(name,run){scenarios.push({name,run});}
scenario('finite final chunk is not lost',async pipe=>{const log=[];const r=new ReadableStream({start(c){c.enqueue('a');c.enqueue('b');c.close();}});const w=new WritableStream({write(v){log.push(v);},close(){log.push('close');}});await pipe.call(r,w,{signal:new AbortController().signal});return {log,readLocked:r.locked,writeLocked:w.locked};});
scenario('preventClose preserves open destination',async pipe=>{let closed=0;const log=[];const r=new ReadableStream({start(c){c.enqueue('x');c.close();}});const w=new WritableStream({write(x){log.push(x);},close(){closed++;}});await pipe.call(r,w,{signal:new AbortController().signal,preventClose:true});const writer=w.getWriter();await writer.write('tail');writer.releaseLock();return {log,closed,locks:[r.locked,w.locked]};});
scenario('source error preventAbort=false',async pipe=>{const preventAbort=false;const marker={source:true};const aborts=[];const r=new ReadableStream({start(c){c.error(marker);}});const w=new WritableStream({abort(e){aborts.push(e===marker);}});const result=await settle(pipe.call(r,w,{signal:new AbortController().signal,preventAbort}),marker);return {result,aborts,locks:[r.locked,w.locked]};});
scenario('write rejection cancels source',async pipe=>{const marker={write:true};const cancels=[];const r=new ReadableStream({pull(c){c.enqueue('x');},cancel(e){cancels.push(e===marker);}});const w=new WritableStream({write(){throw marker;}});const result=await settle(pipe.call(r,w,{signal:new AbortController().signal}),marker);return {result,cancels,locks:[r.locked,w.locked]};});
scenario('preaborted executes both actions',async pipe=>{const ctrl=new AbortController();const marker={pre:true};ctrl.abort(marker);const log=[];const r=new ReadableStream({cancel(e){log.push(['cancel',e===marker]);}});const w=new WritableStream({abort(e){log.push(['abort',e===marker]);}});return {result:await settle(pipe.call(r,w,{signal:ctrl.signal}),marker),log,locks:[r.locked,w.locked]};});
scenario('cancel failure overrides abort reason',async pipe=>{const ctrl=new AbortController();const marker={};const r=new ReadableStream({cancel(){throw false;}});const w=new WritableStream({});const p=pipe.call(r,w,{signal:ctrl.signal});await tick();ctrl.abort(marker);return {result:await settle(p,false),locks:[r.locked,w.locked]};});
scenario('abort failure overrides abort reason',async pipe=>{const ctrl=new AbortController();const marker={};const r=new ReadableStream({});const w=new WritableStream({abort(){throw null;}});const p=pipe.call(r,w,{signal:ctrl.signal});await tick();ctrl.abort(marker);return {result:await settle(p,null),locks:[r.locked,w.locked]};});
scenario('stopImmediatePropagation cannot suppress cancellation',async pipe=>{const ctrl=new AbortController();ctrl.signal.addEventListener('abort',event=>event.stopImmediatePropagation());const marker={};let cancelled=0,aborted=0;const r=new ReadableStream({cancel(){cancelled++;}});const w=new WritableStream({abort(){aborted++;}});const p=pipe.call(r,w,{signal:ctrl.signal});await tick();ctrl.abort(marker);return {result:await settle(p,marker),cancelled,aborted,locks:[r.locked,w.locked]};});
scenario('wait for in-flight write before cancellation',async pipe=>{const gate=deferred(),entered=deferred();const ctrl=new AbortController();const log=[];const marker={};const r=new ReadableStream({pull(c){c.enqueue('x');},cancel(){log.push('cancel');}},{highWaterMark:0});const w=new WritableStream({write(){log.push('write');entered.resolve();return gate.promise;},abort(){log.push('abort');}});const p=pipe.call(r,w,{signal:ctrl.signal});await entered.promise;ctrl.abort(marker);await tick();const before=[...log];gate.resolve();const result=await settle(p,marker);return {before,log,result,locks:[r.locked,w.locked]};});
scenario('ready backpressure bounds reads',async pipe=>{const gate=deferred(),entered=deferred();let reads=0,writes=0;const r=new ReadableStream({pull(c){if(reads===3)c.close();else c.enqueue(++reads);}},{highWaterMark:0});const w=new WritableStream({write(){writes++;if(writes===1){entered.resolve();return gate.promise;}}},{highWaterMark:1});const p=pipe.call(r,w,{signal:new AbortController().signal});await entered.promise;await tick();const before={reads,writes};gate.resolve();await p;return {before,reads,writes,locks:[r.locked,w.locked]};});
scenario('locked source refuses without stealing locks',async pipe=>{const r=new ReadableStream({}),reader=r.getReader(),w=new WritableStream({});const result=await settle(pipe.call(r,w,{signal:new AbortController().signal}));const locks=[r.locked,w.locked];reader.releaseLock();return {rejected:result.rejected,name:result.name,locks};});
scenario('locked destination refuses without source lock',async pipe=>{const r=new ReadableStream({}),w=new WritableStream({}),writer=w.getWriter();const result=await settle(pipe.call(r,w,{signal:new AbortController().signal}));const locks=[r.locked,w.locked];writer.releaseLock();return {rejected:result.rejected,name:result.name,locks};});
 const records=[];
 for(const {name,run}of scenarios){try{const value=await run(pipe);records.push({id:name,completed:true,value});}catch(error){records.push({id:name,completed:false,error:failureData(error)});}}
 return {schemaVersion:1,suite:'NATIVE_SIGNAL_PIPE_REGRESSION_V1',call,caseCount:scenarios.length,records,applicationImported:false,fullNextClaim:false};
}

let calls=0;
const handler=async()=>new Response(JSON.stringify(await collectPipeProbe(++calls)),{status:200,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
export const incomingHandler=createWasiHttpHandler(handler,types,runFreshRequest);
